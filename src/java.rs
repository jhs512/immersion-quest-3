//! JDK 25 source-file execution. Each attempt has a fresh Main.java and working folder.
use crate::runner::Execution;
use std::{path::PathBuf, process::Stdio, time::Duration};
use tokio::{
    io::{AsyncRead, AsyncReadExt, AsyncWriteExt},
    process::Command,
};

const LIMIT: usize = 65536;

pub fn executable() -> String {
    if let Ok(path) = std::env::var("MOLIP_JAVA") {
        return path;
    }
    if let Some(home) = std::env::var_os("JAVA_HOME") {
        let path =
            PathBuf::from(home)
                .join("bin")
                .join(if cfg!(windows) { "java.exe" } else { "java" });
        if path.is_file() {
            return path.to_string_lossy().into_owned();
        }
    }
    #[cfg(target_os = "macos")]
    if let Ok(output) = std::process::Command::new("/usr/libexec/java_home").args(["-v", "25"]).output() {
        if output.status.success() {
            let path = PathBuf::from(String::from_utf8_lossy(&output.stdout).trim()).join("bin/java");
            if path.is_file() { return path.to_string_lossy().into_owned(); }
        }
    }
    "java".into()
}

fn command() -> Command {
    let mut cmd = Command::new(executable());
    cmd.env_remove("JDK_JAVA_OPTIONS")
        .env_remove("JAVA_TOOL_OPTIONS")
        .env_remove("_JAVA_OPTIONS")
        .kill_on_drop(true);
    #[cfg(windows)]
    cmd.creation_flags(0x08000000);
    cmd
}

pub fn is_jdk25(version: &str) -> bool {
    let mut tokens = version.split_whitespace();
    matches!(tokens.next(), Some("openjdk" | "java"))
        && tokens
            .next()
            .is_some_and(|v| v.trim_matches('"').split(['.', '-']).next() == Some("25"))
}

pub async fn version() -> Result<String, String> {
    let mut cmd = command();
    cmd.arg("--version")
        .stdin(Stdio::null())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());
    let output = tokio::time::timeout(Duration::from_secs(10), cmd.output()).await
        .map_err(|_| "JDK 버전 확인 시간이 초과됐어요.".to_string())?
        .map_err(|e| format!("JDK 25를 찾지 못했어요. 설치 후 앱을 다시 여세요. JAVA_HOME 또는 MOLIP_JAVA 경로를 확인하세요: {e}"))?;
    let text = String::from_utf8_lossy(&output.stdout).trim().to_string();
    if !output.status.success() || !is_jdk25(&text) {
        return Err(format!(
            "이 과정은 JDK 25가 필요해요. 확인한 버전: {}",
            if text.is_empty() {
                "확인 실패"
            } else {
                &text
            }
        ));
    }
    Ok(text)
}

async fn read<R: AsyncRead + Unpin>(pipe: R) -> std::io::Result<Vec<u8>> {
    let mut bytes = Vec::new();
    pipe.take((LIMIT + 1) as u64)
        .read_to_end(&mut bytes)
        .await?;
    Ok(bytes)
}

pub async fn run(code: &str, input: &str) -> Result<Execution, String> {
    run_files(code, input, &std::collections::BTreeMap::new()).await
}

/// Restore authored files into a fresh directory for every execution.
pub async fn run_files(code: &str, input: &str, files: &std::collections::BTreeMap<String,String>) -> Result<Execution, String> {
    execute(code, input, None, files).await
}

/// A grading wrapper checks disk state after main returns, before the fresh directory disappears.
pub async fn run_files_checked(code: &str, input: &str, files: &std::collections::BTreeMap<String,String>, expected: &std::collections::BTreeMap<String,String>) -> Result<Execution, String> {
    use sha2::{Digest,Sha256};
    if expected.is_empty() { return run_files(code,input,files).await; }
    let witness=format!("MQ3_FILE_CHECK_{}",crate::issue_progress::new_id());
    let mut checks=String::from("class QuestContract { public static void main(String[] args) throws Exception { Main.main(args);\n");
    for (name,content) in expected {
        if !crate::repository_course::safe_file(name) {return Err("검사할 파일 경로를 확인하세요.".into());}
        let name=serde_json::to_string(name).map_err(|e|e.to_string())?;
        // A fixed-size digest avoids Java's 65,535-byte string constant limit.
        let digest=format!("{:x}",Sha256::digest(content.as_bytes()));
        checks.push_str(&format!("if (!java.util.HexFormat.of().formatHex(java.security.MessageDigest.getInstance(\"SHA-256\").digest(java.nio.file.Files.readAllBytes(java.nio.file.Path.of({name})))).equals(\"{digest}\")) throw new AssertionError(\"저장한 파일 내용을 확인하세요.\");\n"));
    }
    checks.push_str(&format!("System.err.println({}); }} }}",serde_json::to_string(&witness).map_err(|e|e.to_string())?));
    let mut result=execute(code,input,Some(&checks),files).await?;
    if let Some(prefix)=result.stderr.strip_suffix(&format!("{witness}\n")) {
        result.stderr=prefix.to_string();
    } else if result.success {
        result.success=false;
        result.state="concept_error".into();
        result.stderr="저장한 파일 검사까지 실행을 마쳐야 해요.".into();
    }
    Ok(result)
}

/// Execute an authored contract against the student's separately compiled source.
pub async fn contract(code: &str, checker: &str) -> Result<Execution, String> {
    contract_files(code, checker, &std::collections::BTreeMap::new()).await
}

pub async fn contract_files(code: &str, checker: &str, files: &std::collections::BTreeMap<String,String>) -> Result<Execution, String> {
    execute(code, "", Some(checker), files).await
}

async fn execute(code: &str, input: &str, checker: Option<&str>, files: &std::collections::BTreeMap<String,String>) -> Result<Execution, String> {
    if code.len() > LIMIT || input.len() > LIMIT {
        return Err("코드와 입력은 각각 64KB 이하여야 해요.".into());
    }
    version().await?;
    let directory = tempfile::tempdir().map_err(|e| e.to_string())?;
    for (name, content) in files {
        if !crate::repository_course::safe_file(name) {
            return Err("실습 파일 경로를 확인하세요.".into());
        }
        let path=directory.path().join(name);
        std::fs::create_dir_all(path.parent().ok_or("파일 경로 오류")?).map_err(|e|e.to_string())?;
        std::fs::write(path,content).map_err(|e|e.to_string())?;
    }
    std::fs::write(directory.path().join("Main.java"), code).map_err(|e| e.to_string())?;
    let entry = if let Some(checker) = checker {
        std::fs::write(directory.path().join("QuestContract.java"), checker)
            .map_err(|e| e.to_string())?;
        "QuestContract.java"
    } else {
        "Main.java"
    };
    let mut cmd = command();
    cmd.args([
        "-Xmx128m",
        "-Dfile.encoding=UTF-8",
        "-Dstdout.encoding=UTF-8",
        "-Dstderr.encoding=UTF-8",
        "--source",
        "25",
        entry,
    ])
    .current_dir(directory.path())
    .stdin(Stdio::piped())
    .stdout(Stdio::piped())
    .stderr(Stdio::piped());
    let mut child = cmd
        .spawn()
        .map_err(|e| format!("JDK 25 실행에 실패했어요: {e}"))?;
    let mut stdin = child.stdin.take().ok_or("입력을 연결하지 못했어요.")?;
    let stdout = child.stdout.take().ok_or("출력을 연결하지 못했어요.")?;
    let stderr = child
        .stderr
        .take()
        .ok_or("오류 출력을 연결하지 못했어요.")?;
    let collected = async {
        let write = async {
            let _ = stdin.write_all(input.as_bytes()).await;
            drop(stdin);
            Ok::<(), std::io::Error>(())
        };
        tokio::try_join!(read(stdout), read(stderr), child.wait(), write)
    };
    match tokio::time::timeout(Duration::from_secs(20), collected).await {
        Ok(Ok((out, err, status, ()))) => {
            let limited = out.len() > LIMIT || err.len() > LIMIT;
            let stderr =
                String::from_utf8_lossy(&err[..err.len().min(LIMIT)]).replace("\r\n", "\n");
            let state = if limited {
                "output_limit"
            } else if status.success() {
                "finished"
            } else if stderr.contains("error:") {
                "compile_error"
            } else {
                "runtime_error"
            };
            Ok(Execution {
                stdout: String::from_utf8_lossy(&out[..out.len().min(LIMIT)]).replace("\r\n", "\n"),
                stderr: if limited {
                    format!("{stderr}\n출력 제한 64KB를 초과했어요.")
                } else {
                    stderr
                },
                success: status.success() && !limited,
                state: state.into(),
                artifacts: vec![],
            })
        }
        Ok(Err(e)) => {
            let _ = child.kill().await;
            Err(e.to_string())
        }
        Err(_) => {
            let _ = child.kill().await;
            Ok(Execution {
                stdout: String::new(),
                stderr: "실행 시간 제한 20초를 초과했어요. 반복문의 종료 조건을 확인하세요.".into(),
                success: false,
                state: "timeout".into(),
                artifacts: vec![],
            })
        }
    }
}

#[cfg(test)]
mod tests {
    #[test]
    fn accepts_only_25() {
        for text in ["openjdk 25.0.3 2026-04-21", "java 25 2025-09-16"] {
            assert!(super::is_jdk25(text));
        }
        for text in [
            "openjdk 21.0.9",
            "openjdk 26",
            "openjdk 250",
            "",
            "error 25",
        ] {
            assert!(!super::is_jdk25(text));
        }
    }
}

#[cfg(test)]
mod prepared_file_tests {
    #[tokio::test]
    async fn disk_checks_support_the_allowed_file_size_without_java_constants() {
        let expected=std::collections::BTreeMap::from([("result.txt".to_string(),"a".repeat(200_000))]);
        let files=std::collections::BTreeMap::from([("seed.txt".to_string(),"a".repeat(200_000))]);
        let source="import java.nio.file.*; class Main { public static void main(String[] args) throws Exception { Files.copy(Path.of(\"seed.txt\"),Path.of(\"result.txt\")); } }";
        let result=super::run_files_checked(source,"",&files,&expected).await.unwrap();
        assert!(result.success,"{}",result.stderr);
    }

    #[tokio::test]
    async fn grading_uses_changed_files_and_rejects_overwriting_old_text() {
        let task:crate::repository_course::Task=serde_json::from_value(serde_json::json!({
            "id":"file-probe","title":"저장","goal":"이전 글을 남겨요.","language":"java",
            "starter_code":"", "solution":"", "files":{"quotes.txt":"시작\n"},
            "tests":[{"input":"","expected":"시작\n다음"}],
            "expected_files":{"quotes.txt":"시작\n다음\n"},
            "variations":[{"files":{"quotes.txt":""},"expected":"다음","expected_files":{"quotes.txt":"다음\n"}},
                {"files":{"quotes.txt":"이전\n"},"expected":"이전\n다음","expected_files":{"quotes.txt":"이전\n다음\n"}}]
        })).unwrap();
        let source=r#"import java.nio.file.*;
class Main { public static void main(String[] args) throws Exception {
    Path file=Path.of("quotes.txt");
    Files.writeString(file,"다음\n",StandardOpenOption.CREATE,StandardOpenOption.APPEND);
    System.out.print(Files.readString(file));
} }"#;
        let result=crate::lesson_runner::check(&task,source).await.unwrap();
        assert!(result.passed);
        assert_eq!(result.cases.len(),3);
        let wrong=source.replace(",StandardOpenOption.CREATE,StandardOpenOption.APPEND","");
        assert!(!crate::lesson_runner::check(&task,&wrong).await.unwrap().passed);
        let memory_only=source.replace("Files.writeString(file,\"다음\\n\",StandardOpenOption.CREATE,StandardOpenOption.APPEND);","String previous=Files.readString(file);")
            .replace("System.out.print(Files.readString(file));","System.out.print(previous+\"다음\\n\");");
        assert!(!crate::lesson_runner::check(&task,&memory_only).await.unwrap().passed);
        let exit_early=source.replace("System.out.print(Files.readString(file));","System.out.print(Files.readString(file)); System.exit(0);");
        assert!(!crate::lesson_runner::check(&task,&exit_early).await.unwrap().passed);
    }

    #[tokio::test]
    async fn each_java_run_restores_utf8_files_and_nested_paths() {
        let files=std::collections::BTreeMap::from([("data/quotes.txt".to_string(), "시작".to_string())]);
        let source=r#"import java.nio.file.*;
class Main { public static void main(String[] args) throws Exception {
    Path file=Path.of("data", "quotes.txt");
    System.out.println(Files.readString(file));
    Files.writeString(file,"수정");
} }"#;
        for _ in 0..2 {
            let result=super::run_files(source,"",&files).await.unwrap();
            assert!(result.success,"{}",result.stderr);
            assert_eq!(result.stdout,"시작\n");
        }
        let unsafe_files=std::collections::BTreeMap::from([("../escape.txt".to_string(), "x".to_string())]);
        assert!(super::run_files(source,"",&unsafe_files).await.is_err());
    }
}
