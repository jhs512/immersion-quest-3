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
    execute(code, input, None).await
}

/// Execute an authored contract against the student's separately compiled source.
pub async fn contract(code: &str, checker: &str) -> Result<Execution, String> {
    execute(code, "", Some(checker)).await
}

async fn execute(code: &str, input: &str, checker: Option<&str>) -> Result<Execution, String> {
    if code.len() > LIMIT || input.len() > LIMIT {
        return Err("코드와 입력은 각각 64KB 이하여야 해요.".into());
    }
    version().await?;
    let directory = tempfile::tempdir().map_err(|e| e.to_string())?;
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
