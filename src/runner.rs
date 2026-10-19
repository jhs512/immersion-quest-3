use crate::Unit;
use serde::{Deserialize, Serialize};
use std::{process::Stdio, time::Duration};
use tokio::{
    io::{AsyncRead, AsyncReadExt, AsyncWriteExt},
    process::Command,
};

const OUTPUT_LIMIT: u64 = 65536;

pub fn assemble(
    unit: &Unit,
    answers: &std::collections::HashMap<String, String>,
) -> Result<String, String> {
    if answers.len() != unit.blanks.len() {
        return Err("지정된 빈칸에만 답을 입력해 주세요.".into());
    }
    let mut code = unit.starter_code.clone();
    for blank in &unit.blanks {
        let answer = answers.get(blank).ok_or("빈칸 답이 없습니다.")?;
        if answer.contains("{{") || answer.len() > 65536 {
            return Err("빈칸 답을 확인해 주세요.".into());
        }
        code = code.replace(&format!("{{{{{blank}}}}}"), answer);
    }
    Ok(code)
}
#[derive(Clone, Serialize, Deserialize)]
pub struct Execution {
    pub stdout: String,
    pub stderr: String,
    pub success: bool,
    pub state: String,
    #[serde(default)]
    pub artifacts: Vec<Artifact>,
}
#[derive(Clone, Serialize, Deserialize, PartialEq)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum Artifact {
    Html { title: String, srcdoc: String },
    Table {
        title: String,
        columns: Vec<String>,
        rows: Vec<Vec<String>>,
        total_rows: usize,
        total_columns: usize,
    },
    Image {
        title: String,
        data_url: String,
    },
}

/// The Python that runs student code, in this order: `MOLIP_PYTHON`, the repo's own
/// `target/ml-env` in debug builds, the managed environment the installer scripts create under
/// the app's data folder (`ml-env`), then the first `python3` a login shell or a well-known
/// install location knows about. The last step matters on macOS: an app opened from Finder gets
/// only `/usr/bin:/bin:/usr/sbin:/sbin`, so Homebrew's or uv's python3 is invisible without it.
pub fn python_executable() -> String {
    if let Ok(path) = std::env::var("MOLIP_PYTHON") {
        return path;
    }
    let local = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join(if cfg!(windows) {
        "target/ml-env/Scripts/python.exe"
    } else {
        "target/ml-env/bin/python"
    });
    if cfg!(debug_assertions) && local.is_file() {
        return local.to_string_lossy().into_owned();
    }
    if let Some(managed) = managed_python() {
        return managed;
    }
    if cfg!(windows) {
        "python".into()
    } else {
        static FOUND: std::sync::OnceLock<String> = std::sync::OnceLock::new();
        FOUND.get_or_init(unix_python3).clone()
    }
}

/// `<data dir>/ml-env`, created by packaging/macos/install.sh with the course packages.
fn managed_python() -> Option<String> {
    let environment = crate::data_dir().ok()?.join("ml-env");
    managed_python_in(&environment)
}

fn managed_python_in(environment: &std::path::Path) -> Option<String> {
    if cfg!(windows) {
        let standalone = environment.join("python.exe");
        if standalone.is_file() {
            return Some(standalone.to_string_lossy().into_owned());
        }
    }
    let python = environment.join(if cfg!(windows) {
        "Scripts/python.exe"
    } else {
        "bin/python"
    });
    python
        .is_file()
        .then(|| python.to_string_lossy().into_owned())
}

#[cfg(all(test, windows))]
mod python_resolution_tests {
    #[test]
    fn copied_runtime_wins_and_old_venvs_remain_supported() {
        let directory = tempfile::tempdir().unwrap();
        let root = directory.path();
        std::fs::create_dir(root.join("Scripts")).unwrap();
        let legacy = root.join("Scripts/python.exe");
        std::fs::write(&legacy, b"legacy launcher").unwrap();
        assert_eq!(
            super::managed_python_in(root),
            Some(legacy.to_string_lossy().into_owned())
        );
        let copied = root.join("python.exe");
        std::fs::write(&copied, b"copied runtime").unwrap();
        assert_eq!(
            super::managed_python_in(root),
            Some(copied.to_string_lossy().into_owned())
        );
    }
}

#[cfg(not(windows))]
fn unix_python3() -> String {
    // A login shell sees the PATH the user's .zprofile/.profile set up (Homebrew, uv, pyenv).
    let shell = std::env::var("SHELL").unwrap_or_else(|_| "/bin/sh".into());
    let from_shell = std::process::Command::new(&shell)
        .args(["-lc", "command -v python3"])
        .stdin(std::process::Stdio::null())
        .stderr(std::process::Stdio::null())
        .output()
        .ok()
        .filter(|out| out.status.success())
        .and_then(|out| String::from_utf8(out.stdout).ok())
        .map(|out| out.trim().to_string())
        .filter(|path| path.starts_with('/') && std::path::Path::new(path).is_file());
    // Apple's /usr/bin/python3 is only a stub that offers to install the developer tools,
    // so a real installation anywhere else wins over it.
    let home = std::env::var("HOME").unwrap_or_default();
    let known = [
        "/opt/homebrew/bin/python3".to_string(),
        "/usr/local/bin/python3".to_string(),
        format!("{home}/.local/bin/python3"),
        "/Library/Frameworks/Python.framework/Versions/Current/bin/python3".to_string(),
    ];
    from_shell
        .filter(|path| path != "/usr/bin/python3")
        .or_else(|| {
            known
                .into_iter()
                .find(|path| std::path::Path::new(path).is_file())
        })
        .unwrap_or_else(|| "python3".into())
}

#[cfg(windows)]
fn unix_python3() -> String {
    "python".into()
}

fn read_artifacts(directory: &std::path::Path) -> Vec<Artifact> {
    let path = directory.join("rich_results.json");
    if !path.metadata().is_ok_and(|m| m.len() <= 8_000_000) {
        return vec![];
    }
    let Some(items) = std::fs::read(path)
        .ok()
        .and_then(|bytes| serde_json::from_slice::<Vec<Artifact>>(&bytes).ok())
    else {
        return vec![];
    };
    items
        .into_iter()
        .take(14)
        .filter(|item| match item {
            Artifact::Html { .. } => false,
            Artifact::Table { columns, rows, .. } => {
                columns.len() <= 31
                    && rows.len() <= 100
                    && rows
                        .iter()
                        .all(|row| row.len() <= 31 && row.iter().all(|s| s.len() <= 3000))
            }
            Artifact::Image { data_url, .. } => {
                data_url.starts_with("data:image/png;base64,") && data_url.len() <= 2_700_000
            }
        })
        .collect()
}
#[derive(Clone, Serialize, Deserialize)]
pub struct TestCaseResult {
    pub input: String,
    pub expected: String,
    pub stdout: String,
    pub stderr: String,
    pub passed: bool,
    pub state: String,
}
#[derive(Clone, Serialize, Deserialize)]
pub struct TestReport {
    pub passed: bool,
    pub cases: Vec<TestCaseResult>,
}

async fn read_output<R: AsyncRead + Unpin>(pipe: R) -> std::io::Result<Vec<u8>> {
    let mut bytes = Vec::new();
    pipe.take(OUTPUT_LIMIT + 1).read_to_end(&mut bytes).await?;
    Ok(bytes)
}

pub async fn run_python(code: &str, input: &str) -> Result<Execution, String> {
    execute_python(code, input, None).await
}

pub async fn run_code(
    language: crate::Language,
    code: &str,
    input: &str,
) -> Result<Execution, String> {
    match language {
        crate::Language::Python => run_python(code, input).await,
        crate::Language::Java => crate::java::run(code, input).await,
    }
}

async fn execute_python(
    code: &str,
    input: &str,
    checker: Option<&str>,
) -> Result<Execution, String> {
    execute_python_files(code,input,checker,&std::collections::BTreeMap::new()).await
}

pub(crate) async fn execute_python_files(
    code: &str,
    input: &str,
    checker: Option<&str>,
    files: &std::collections::BTreeMap<String,String>,
) -> Result<Execution, String> {
    if code.len() > 65536 || input.len() > 65536 || checker.is_some_and(|c| c.len() > 65536) {
        return Err("코드와 입력은 각각 64KB 이하여야 합니다.".into());
    }
    let directory = tempfile::tempdir().map_err(|e| e.to_string())?;
    let data = directory.path().join("data");
    std::fs::create_dir(&data).map_err(|e| e.to_string())?;
    for (name, bytes) in [
        (
            "cafe-sales.xlsx",
            include_bytes!("../site/data/cafe-sales.xlsx").as_slice(),
        ),
        (
            "titanic.csv",
            include_bytes!("../courses/data/titanic.csv").as_slice(),
        ),
        (
            "credit.csv",
            include_bytes!("../courses/data/credit.csv").as_slice(),
        ),
        (
            "stock.csv",
            include_bytes!("../courses/data/stock.csv").as_slice(),
        ),
        (
            "prices.html",
            include_bytes!("../courses/data/prices.html").as_slice(),
        ),
        (
            "croissant.csv",
            include_bytes!("../courses/data/croissant.csv").as_slice(),
        ),
    ] {
        std::fs::write(data.join(name), bytes).map_err(|e| e.to_string())?;
    }
    for (name,content) in files {
        if !crate::repository_course::safe_file(name) {return Err("실습 파일 경로를 확인하세요.".into())}
        let path=directory.path().join(name);
        std::fs::create_dir_all(path.parent().ok_or("파일 경로 오류")?).map_err(|e|e.to_string())?;
        std::fs::write(path,content).map_err(|e|e.to_string())?;
    }
    std::fs::write(directory.path().join("main.py"), code).map_err(|e| e.to_string())?;
    let executable = python_executable();
    let mut command = Command::new(executable);
    command
        .arg("-I")
        // Pipes must use the same encoding as the UTF-8 input/output below.
        // -I ignores PYTHON* environment variables, so set this via -X.
        .arg("-X")
        .arg("utf8")
        .arg("-u")
        .current_dir(directory.path())
        // TensorFlow's C++ start-up logs are not the learner's output; -I does not drop TF_* variables.
        .env("TF_CPP_MIN_LOG_LEVEL", "3")
        .env("TF_ENABLE_ONEDNN_OPTS", "0")
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .kill_on_drop(true);
    if let Some(checker) = checker {
        std::fs::write(directory.path().join("checker.py"), checker).map_err(|e| e.to_string())?;
        std::fs::write(directory.path().join("check_runner.py"),
            "import runpy,sys,traceback\ntry:\n    runpy.run_path('checker.py',run_name='__main__')\nexcept AssertionError:\n    traceback.print_exc()\n    sys.exit(1)\nexcept SystemExit as e:\n    sys.exit(0 if e.code is None else e.code)\nexcept BaseException:\n    traceback.print_exc()\n    sys.exit(2)\n"
        ).map_err(|e| e.to_string())?;
        command
            .arg("check_runner.py")
            .arg(directory.path().join("main.py"));
    } else {
        std::fs::write(
            directory.path().join("rich_runner.py"),
            include_str!("../assets/python/rich_runner.py"),
        )
        .map_err(|e| e.to_string())?;
        command.arg("rich_runner.py");
    }
    #[cfg(windows)]
    command.creation_flags(0x08000000);
    let mut child = command.spawn().map_err(|e| {
        format!("Python을 실행할 수 없습니다. 설치와 실행 경로를 확인해 주세요: {e}")
    })?;
    let mut stdin = child.stdin.take().ok_or("입력 연결에 실패했습니다.")?;
    let stdout = child.stdout.take().ok_or("출력 연결에 실패했습니다.")?;
    let stderr = child
        .stderr
        .take()
        .ok_or("오류 출력 연결에 실패했습니다.")?;
    let input = input.as_bytes().to_vec();
    let collected = async {
        let write = async {
            let _ = stdin.write_all(&input).await;
            drop(stdin);
            Ok::<(), std::io::Error>(())
        };
        let (stdout, stderr, status, ()) = tokio::try_join!(
            read_output(stdout),
            read_output(stderr),
            child.wait(),
            write
        )?;
        Ok::<_, std::io::Error>((stdout, stderr, status))
    };
    // A checker reruns the reference and the learner on several data sets; TensorFlow imports and
    // trains in that one process, so grading gets more time than a plain run.
    let limit = if checker.is_some() { 180 } else { 60 };
    match tokio::time::timeout(Duration::from_secs(limit), collected).await {
        Ok(Ok((stdout, stderr, status))) => {
            let limited = stdout.len() as u64 > OUTPUT_LIMIT || stderr.len() as u64 > OUTPUT_LIMIT;
            Ok(Execution {
                artifacts: read_artifacts(directory.path()),
                stdout: String::from_utf8_lossy(&stdout[..stdout.len().min(OUTPUT_LIMIT as usize)])
                    .replace("\r\n", "\n"),
                stderr: String::from_utf8_lossy(&stderr[..stderr.len().min(OUTPUT_LIMIT as usize)])
                    .into(),
                success: status.success() && !limited,
                state: if limited {
                    "output_limit"
                } else if status.success() {
                    "finished"
                } else if checker.is_some() && status.code() == Some(1) {
                    "wrong_answer"
                } else if checker.is_some() {
                    "checker_error"
                } else {
                    "runtime_error"
                }
                .into(),
            })
        }
        Ok(Err(error)) => {
            let _ = child.kill().await;
            Err(error.to_string())
        }
        Err(_) => {
            let _ = child.kill().await;
            Ok(Execution {
                artifacts: vec![],
                stdout: String::new(),
                stderr: format!("실행 시간 제한 {limit}초를 초과했습니다."),
                success: false,
                state: "timeout".into(),
            })
        }
    }
}

fn normalized(value: &str) -> String {
    value
        .replace("\r\n", "\n")
        .trim_end_matches('\n')
        .to_string()
}

pub async fn check_unit(unit: &Unit, code: &str) -> Result<TestReport, String> {
    check_unit_files(unit, code, &std::collections::BTreeMap::new()).await
}

/// Grade a repository Java task with the same fresh authored files as execution.
pub async fn check_unit_files(unit: &Unit, code: &str, files: &std::collections::BTreeMap<String,String>) -> Result<TestReport, String> {
    check_unit_prepared(unit,code,files,&std::collections::BTreeMap::new()).await
}

pub async fn check_unit_prepared(unit: &Unit, code: &str, files: &std::collections::BTreeMap<String,String>, expected_files: &std::collections::BTreeMap<String,String>) -> Result<TestReport, String> {
    let mut cases = Vec::new();
    // Java contracts return a compiler-tree mutation of the submitted source.
    // The changed method must affect a real execution, as well as pass direct API tests.
    if unit.language == crate::Language::Java {
        if let Some(checker) = unit.checker.as_deref().filter(|c| !c.trim().is_empty()) {
            let contracts = if checker.trim_start().starts_with('[') {
                serde_json::from_str::<Vec<String>>(checker).map_err(|e| e.to_string())?
            } else {
                vec![checker.to_string()]
            };
            if contracts.is_empty() || contracts.len() > 8 {
                return Err("개념 검사 수를 확인하세요.".into());
            }
            for checker in contracts {
                let contract = crate::java::contract_files(code, &checker, files).await?;
                let mut used = false;
                if contract.success {
                    for test in unit.tests.iter().take(3) {
                        let mutation = crate::java::run_files(&contract.stdout, &test.input, files).await?;
                        if mutation.success
                            && normalized(&mutation.stdout) != normalized(&test.expected)
                        {
                            used = true;
                            break;
                        }
                    }
                }
                cases.push(TestCaseResult {
                input: "개념 사용 검사".into(), expected: "메서드 계약과 실제 호출".into(),
                stdout: String::new(), stderr: if !contract.success { contract.stderr } else if !used {
                    "메서드의 계산을 바꿔도 출력이 같아요. main에서 해당 객체나 메서드의 결과를 사용하세요.".into()
                } else { String::new() }, passed: contract.success && used,
                state: if contract.success && used { "finished" } else { "concept_error" }.into(),
            });
                if !cases.last().unwrap().passed {
                    return Ok(TestReport {
                        passed: false,
                        cases,
                    });
                }
            }
        }
    }
    if let Some(checker) = unit
        .checker
        .as_deref()
        .filter(|c| unit.language != crate::Language::Java && !c.trim().is_empty())
    {
        let result = execute_python(code, "", Some(checker)).await?;
        cases.push(TestCaseResult {
            input: String::new(),
            expected: "검사 코드 종료 상태 0".into(),
            stdout: result.stdout,
            stderr: result.stderr,
            passed: result.success,
            state: result.state,
        });
    } else {
        if unit.tests.is_empty() || unit.tests.len() > 30 {
            return Err("입출력 테스트는 1개 이상 30개 이하로 등록해야 합니다.".into());
        }
        for test in &unit.tests {
            let result = if unit.language == crate::Language::Java {
                crate::java::run_files_checked(code, &test.input, files, expected_files).await?
            } else { run_code(unit.language, code, &test.input).await? };
            let passed = result.success && normalized(&result.stdout) == normalized(&test.expected);
            cases.push(TestCaseResult {
                input: test.input.clone(),
                expected: test.expected.clone(),
                stdout: result.stdout,
                stderr: result.stderr,
                passed,
                state: result.state,
            });
        }
    }
    Ok(TestReport {
        passed: cases.iter().all(|c| c.passed),
        cases,
    })
}
