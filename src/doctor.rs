use crate::runner::python_executable;
use serde::{Deserialize, Serialize};
use std::process::Stdio;
use tokio::process::Command;

#[derive(Clone, PartialEq, Serialize, Deserialize)]
pub struct Check {
    pub name: String,
    pub ready: bool,
    pub detail: String,
}

async fn probe(executable: &str, args: &[&str]) -> Option<Vec<u8>> {
    probe_with_timeout(executable, args, std::time::Duration::from_secs(20))
        .await
        .ok()
}

pub(crate) async fn probe_with_timeout(
    executable: &str,
    args: &[&str],
    timeout: std::time::Duration,
) -> Result<Vec<u8>, String> {
    let mut command = Command::new(executable);
    command
        .args(args)
        .env_remove("JDK_JAVA_OPTIONS").env_remove("JAVA_TOOL_OPTIONS").env_remove("_JAVA_OPTIONS")
        .stdin(Stdio::null())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .kill_on_drop(true);
    #[cfg(windows)]
    command.creation_flags(0x08000000);
    if let Some(path)=crate::runtime_setup::library_path(){command.env("DYLD_LIBRARY_PATH",path);}
    let child = command.spawn().map_err(|e| e.to_string())?;
    let output = tokio::time::timeout(timeout, child.wait_with_output())
        .await
        .map_err(|_| {
            "검사 시간 초과 · 설치 여부를 확인하지 못했습니다. 잠시 후 다시 검사하세요.".to_string()
        })?
        .map_err(|e| e.to_string())?;
    if !output.status.success() {
        return Err(format!(
            "검사 실행 실패: {}",
            String::from_utf8_lossy(&output.stderr)
                .chars()
                .take(2000)
                .collect::<String>()
        ));
    }
    if output.stdout.len() > 65536 {
        return Err("검사 결과가 너무 큽니다.".into());
    }
    Ok(output.stdout)
}

pub async fn inspect() -> Vec<Check> {
    let python = python_executable();
    let mut checks = inspect_python(&python, std::time::Duration::from_secs(120)).await;
    for (name,result) in [("Java · JDK 25",crate::runtime_setup::inspect_java().await),("C · 컴파일·실행",crate::runtime_setup::inspect_c().await)] {
        checks.push(Check{name:name.into(),ready:result.is_ok(),detail:result.unwrap_or_else(|error|error)});
    }
    checks.push(inspect_voice().await);
    checks
}

/// The narration's neural voice (Edge Read Aloud over the network): one short clip, so a
/// classroom without that network learns here, not mid-lesson, that the device voice will read.
async fn inspect_voice() -> Check {
    let result = tokio::time::timeout(
        std::time::Duration::from_secs(25),
        tokio::task::spawn_blocking(|| crate::tts::synthesize(&crate::tts::default_voice(), "안녕하세요")),
    )
    .await;
    let (ready, detail) = match result {
        Ok(Ok(Ok((bytes, engine)))) => (true, format!("인터넷 음성 연결됨 ({engine}, {} KB)", bytes.len() / 1024)),
        Ok(Ok(Err(error))) => (false, format!("인터넷 음성에 연결하지 못했습니다. 해설은 이 컴퓨터의 한국어 음성으로 읽고, 그것도 없으면 자막만 보입니다. ({error})")),
        Ok(Err(error)) => (false, format!("음성 검사가 실패했습니다: {error}")),
        Err(_) => (false, "인터넷 음성 서버가 25초 안에 답하지 않았습니다. 해설은 이 컴퓨터의 음성으로 읽습니다.".into()),
    };
    Check { name: "해설 음성 · 인터넷(Edge)".into(), ready, detail }
}

async fn inspect_python(python: &str, package_timeout: std::time::Duration) -> Vec<Check> {
    inspect_python_with_prefix(python, package_timeout, "").await
}

async fn inspect_python_with_prefix(python: &str, package_timeout: std::time::Duration, prefix: &str) -> Vec<Check> {
    let mut checks = Vec::new();
    let version = probe_with_timeout(
        python,
        &[
            "-I",
            "-X",
            "utf8",
            "-c",
            "import sys; print(sys.version.split()[0])",
        ],
        std::time::Duration::from_secs(20),
    )
    .await;
    checks.push(Check {
        name: "Python 실행".into(),
        ready: version.is_ok(),
        detail: version
            .as_ref()
            .map(|v| format!("버전 {} · {python}", String::from_utf8_lossy(v).trim()))
            .unwrap_or_else(|error| {
                format!("Python 실행을 확인하지 못했습니다. {error} (시도한 경로: {python})")
            }),
    });
    // Import packages in separate children: a slow or crashed native extension must
    // not erase completed checks or prevent later packages from being checked.
    let mut results = std::collections::HashMap::new();
    if version.is_ok() {
        let limit = std::sync::Arc::new(tokio::sync::Semaphore::new(3));
        let mut workers = tokio::task::JoinSet::new();
        for key in ["pandas", "matplotlib", "seaborn", "sklearn", "tensorflow", "xgboost", "openpyxl", "bs4", "requests", "FinanceDataReader", "yfinance"] {
            let python = python.to_owned();
            let prefix = prefix.to_owned();
            let limit = limit.clone();
            workers.spawn(async move {
                let _permit = limit.acquire_owned().await.unwrap();
                let script = format!("{prefix}import json,importlib,sys\nname=sys.argv[1]\ntry:\n module=importlib.import_module(name); result={{'version':str(getattr(module,'__version__','설치됨'))}}\nexcept ModuleNotFoundError as e:\n result={{'error':str(e),'missing':e.name==name}}\nexcept Exception as e:\n result={{'error':str(e),'missing':False}}\nprint(json.dumps(result))");
                let result = probe_with_timeout(&python, &["-I", "-X", "utf8", "-c", &script, key], package_timeout)
                    .await.and_then(|out| serde_json::from_slice::<serde_json::Value>(&out)
                        .map_err(|e| format!("검사 결과를 읽지 못했습니다: {e}")));
                (key, result)
            });
        }
        while let Some(worker) = workers.join_next().await {
            if let Ok((key, result)) = worker { results.insert(key, result); }
        }
    }
    for (key, name) in [
        ("pandas", "pandas · 표 분석"),
        ("matplotlib", "matplotlib · 그래프"),
        ("seaborn", "seaborn · 시각화"),
        ("sklearn", "scikit-learn · 모델 학습"),
        ("tensorflow", "TensorFlow · 딥러닝"),
        ("xgboost", "XGBoost · 부스팅 모델"),
        ("openpyxl", "openpyxl · Excel 읽기"),
        ("bs4", "BeautifulSoup · HTML 분석"),
        ("requests", "requests · 웹 페이지 받기"),
        ("FinanceDataReader", "FinanceDataReader · 주가 받기"),
        ("yfinance", "yfinance · 주가 받기 (야후)"),
    ] {
        let result = results.remove(key).unwrap_or_else(|| Err(
            if version.is_ok() { "패키지 검사를 완료하지 못했어요.".into() }
            else { "Python 실행을 확인한 뒤 패키지를 다시 검사하세요.".into() }
        ));
        let package_version = result.as_ref().ok().and_then(|v| v["version"].as_str());
        checks.push(Check {
            name: name.into(),
            ready: package_version.is_some(),
            detail: package_version.map(|v| format!("버전 {v}"))
                .unwrap_or_else(|| match &result {
                    Err(error) => error.clone(),
                    Ok(value) if value["missing"] == true => "선택한 Python 환경에 패키지를 설치하세요.".into(),
                    Ok(value) => format!("패키지를 불러오지 못했습니다: {}",
                        value["error"].as_str().unwrap_or("검사 결과 없음")),
                }),
        });
    }
    checks
}

// ---- 환경 설치: a fresh learning Python in the app data folder, for this OS. ----

/// The learning packages, pinned (the same file the setup scripts read).
const REQUIREMENTS: &str = include_str!("../requirements-learning.txt");

// Match the macOS installer: TensorFlow has no current Intel Mac wheel.
// Keep reinstalling from inside the app on the same supported environment.
fn learning_python_version() -> &'static str {
    if cfg!(all(target_os = "macos", target_arch = "x86_64")) { "3.12" } else { "3.13" }
}

fn learning_requirements() -> String { REQUIREMENTS.to_owned() }

/// Where `uv` usually lands after its installer, besides PATH.
fn uv_candidates() -> Vec<std::path::PathBuf> {
    let mut out = vec![std::path::PathBuf::from("uv")];
    if let Some(home) = std::env::var_os("USERPROFILE").or_else(|| std::env::var_os("HOME")) {
        let home = std::path::PathBuf::from(home);
        out.push(
            home.join(".local")
                .join("bin")
                .join(if cfg!(windows) { "uv.exe" } else { "uv" }),
        );
        out.push(
            home.join(".cargo")
                .join("bin")
                .join(if cfg!(windows) { "uv.exe" } else { "uv" }),
        );
    }
    if !cfg!(windows) {
        out.push("/opt/homebrew/bin/uv".into());
        out.push("/usr/local/bin/uv".into());
    }
    out
}

async fn find_uv() -> Option<String> {
    for candidate in uv_candidates() {
        let path = candidate.to_string_lossy().into_owned();
        if probe(&path, &["--version"]).await.is_some() {
            return Some(path);
        }
    }
    None
}

/// Select a real patch-version directory without following uv's minor-version
/// junction. Merely querying python.exe through that junction can fail with 448.
#[cfg(windows)]
fn direct_windows_python(store: &std::path::Path) -> Option<std::path::PathBuf> {
    use std::os::windows::fs::MetadataExt;
    std::fs::read_dir(store)
        .ok()?
        .filter_map(Result::ok)
        .filter_map(|entry| {
            let name = entry.file_name();
            let patch = name
                .to_str()?
                .strip_prefix("cpython-3.13.")?
                .strip_suffix("-windows-x86_64-none")?
                .parse::<u32>()
                .ok()?;
            let metadata = std::fs::symlink_metadata(entry.path()).ok()?;
            if !metadata.is_dir() || metadata.file_attributes() & 0x400 != 0 {
                return None;
            }
            let python = entry.path().join("python.exe");
            python.is_file().then_some((patch, python))
        })
        .max_by_key(|(patch, _)| *patch)
        .map(|(_, path)| path)
}

#[cfg(windows)]
fn copy_python_runtime(source: &std::path::Path, target: &std::path::Path) -> Result<(), String> {
    use std::os::windows::fs::MetadataExt;
    let metadata = std::fs::symlink_metadata(source).map_err(|e| e.to_string())?;
    if metadata.file_attributes() & 0x400 != 0 {
        return Err(format!(
            "Python 원본에 연결 파일이 있습니다: {}",
            source.display()
        ));
    }
    if metadata.is_dir() {
        std::fs::create_dir_all(target).map_err(|e| e.to_string())?;
        for entry in std::fs::read_dir(source).map_err(|e| e.to_string())? {
            let entry = entry.map_err(|e| e.to_string())?;
            // This new copy belongs to the app, not to uv's managed installation.
            if entry.file_name() == "EXTERNALLY-MANAGED" {
                continue;
            }
            copy_python_runtime(&entry.path(), &target.join(entry.file_name()))?;
        }
    } else {
        std::fs::copy(source, target).map_err(|e| e.to_string())?;
    }
    Ok(())
}

async fn create_learning_environment(
    report: &tokio::sync::mpsc::UnboundedSender<String>,
    uv: &str,
    env_dir: &std::path::Path,
    store: &std::path::Path,
) -> Result<(), String> {
    #[cfg(windows)]
    {
        if direct_windows_python(store).is_none() {
            let result = run_logged(
                report,
                uv,
                &[
                    "python",
                    "install",
                    "3.13",
                    "--no-bin",
                    "--no-registry",
                    "--no-config",
                ],
                Some(store),
            )
            .await;
            // uv can finish extracting Python and then fail to create the minor
            // junction. The extracted interpreter is still usable directly.
            if let Err(error) = result {
                if direct_windows_python(store).is_none() {
                    return Err(error);
                }
                let _ = report
                    .send("연결 경로 생성은 실패했지만 실제 Python 파일로 계속합니다.".into());
            }
        }
        let python =
            direct_windows_python(store).ok_or("실제 Python 3.13 설치 폴더를 찾지 못했습니다.")?;
        let python_str = python.to_string_lossy().into_owned();
        let _ = report.send(format!("연결 경로 없이 실행: {python_str}"));
        let _ = report.send("Python 본체와 라이브러리를 독립된 학습 환경으로 복사합니다 (가상환경 중계 파일 없이 실행).".into());
        return copy_python_runtime(python.parent().ok_or("Python 폴더가 없습니다.")?, env_dir);
    }
    #[cfg(not(windows))]
    let env_str = env_dir.to_string_lossy().into_owned();
    #[cfg(not(windows))]
    run_logged(
        report,
        uv,
        &["venv", &env_str, "--python", learning_python_version(), "--managed-python"],
        Some(store),
    )
    .await
}

/// Run a command, streaming every output line to `report`; Err on a non-zero exit.
pub(crate) async fn run_logged(
    report: &tokio::sync::mpsc::UnboundedSender<String>,
    program: &str,
    args: &[&str],
    python_store: Option<&std::path::Path>,
) -> Result<(), String> {
    use tokio::io::{AsyncBufReadExt, BufReader};
    let mut command = Command::new(program);
    if let Some(store) = python_store {
        // Keep uv away from the shared Roaming installation: Windows cloud/reparse
        // filters can reject its interpreter junction with OS error 448.
        command.env("UV_PYTHON_INSTALL_DIR", store);
    }
    command
        .args(args)
        .stdin(Stdio::null())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .kill_on_drop(true);
    #[cfg(windows)]
    command.creation_flags(0x08000000);
    command.env("UV_NO_MODIFY_PATH","1");
    let mut child = command
        .spawn()
        .map_err(|e| format!("{program} 실행 실패: {e}"))?;
    let stdout = child.stdout.take().map(|o| BufReader::new(o).lines());
    let stderr = child.stderr.take().map(|o| BufReader::new(o).lines());
    let out_report = report.clone();
    let err_report = report.clone();
    let out_task = tokio::spawn(async move {
        if let Some(mut lines) = stdout {
            while let Ok(Some(line)) = lines.next_line().await {
                let _ = out_report.send(line);
            }
        }
    });
    let err_task = tokio::spawn(async move {
        if let Some(mut lines) = stderr {
            while let Ok(Some(line)) = lines.next_line().await {
                let _ = err_report.send(line);
            }
        }
    });
    let status = tokio::time::timeout(std::time::Duration::from_secs(1800), child.wait())
        .await
        .map_err(|_| "30분 안에 끝나지 않았습니다.".to_string())?
        .map_err(|e| e.to_string())?;
    let _ = out_task.await;
    let _ = err_task.await;
    if status.success() {
        Ok(())
    } else {
        Err(format!(
            "{program} {} 실패 ({status})",
            args.first().copied().unwrap_or("")
        ))
    }
}

async fn prepare_python_environment(
    report: &tokio::sync::mpsc::UnboundedSender<String>, uv: &str,
    env_dir: &std::path::Path, python_store: &std::path::Path,
) -> Result<std::path::PathBuf, String> {
    let python = env_dir.join(if cfg!(windows) { "python.exe" } else { "bin/python" });
    let existing_python = if python.is_file() { Some(python.clone()) }
        else if cfg!(windows) && env_dir.join("Scripts/python.exe").is_file() { Some(env_dir.join("Scripts/python.exe")) }
        else { None };
    let usable = if let Some(path) = &existing_python {
        probe_with_timeout(&path.to_string_lossy(), &["-I", "-c", "import sys; print(sys.version_info[:2])"], std::time::Duration::from_secs(20)).await.is_ok_and(|out| String::from_utf8_lossy(&out).trim() == if learning_python_version() == "3.12" { "(3, 12)" } else { "(3, 13)" })
    } else { false };
    let python = if usable {
        let _ = report.send("기존 Python을 유지하고 필요한 패키지를 준비해요.".into());
        existing_python.unwrap()
    } else {
        let backup = if env_dir.exists() {
            let backup = env_dir.parent().ok_or("Python 설치 경로 오류")?.join(format!("ml-env-backup-{}", crate::issue_progress::new_id()));
            std::fs::rename(&env_dir, &backup).map_err(|e| format!("Python 환경 보관 실패 · {} → {}: {e}", env_dir.display(), backup.display()))?;
            Some(backup)
        } else { None };
        if let Err(error) = create_learning_environment(report, uv, env_dir, python_store).await {
            // Keep any partial installation for diagnosis and restore the previous one.
            if let Some(backup) = backup {
                if env_dir.exists() {
                    let partial = env_dir.parent().ok_or("Python 설치 경로 오류")?.join(format!("ml-env-incomplete-{}", crate::issue_progress::new_id()));
                    std::fs::rename(&env_dir, &partial).map_err(|e| format!("{error} / 불완전한 Python 환경 보관 실패: {e}"))?;
                }
                std::fs::rename(&backup, &env_dir).map_err(|e| format!("{error} / 기존 Python 환경 복구 실패: {e}"))?;
            }
            return Err(format!("Python 환경 생성 · {}: {error}", env_dir.display()));
        }
        python
    };
    Ok(python)
}

/// Install (or reinstall) the learning Python environment in the app data folder: get `uv`
/// if it is missing, create the platform's supported Python environment and install its pins. Progress
/// lines go to `report`; the result names the interpreter.
pub async fn install(report: tokio::sync::mpsc::UnboundedSender<String>) -> Result<String, String> {
    let data_dir = crate::data_dir()?;
    let env_dir = data_dir.join("ml-env");
    let python_store = data_dir.join("python");
    let say = |line: &str| {
        let _ = report.send(line.to_string());
    };
    say("[1/3] uv (Python 패키지 설치 도구)를 확인합니다.");
    let uv = match find_uv().await {
        Some(uv) => uv,
        None => {
            say("uv가 없어 받습니다 (astral.sh).");
            if cfg!(windows) {
                run_logged(
                    &report,
                    "powershell",
                    &[
                        "-NoProfile",
                        "-ExecutionPolicy",
                        "ByPass",
                        "-Command",
                        "irm https://astral.sh/uv/install.ps1 | iex",
                    ],
                    None,
                )
                .await?;
            } else {
                run_logged(
                    &report,
                    "sh",
                    &["-c", "curl -LsSf https://astral.sh/uv/install.sh | sh"],
                    None,
                )
                .await?;
            }
            find_uv()
                .await
                .ok_or("uv를 설치했지만 찾지 못했습니다. 앱을 다시 열고 시도하세요.")?
        }
    };
    say(&format!("uv: {uv}"));
    say(&format!(
        "앱 전용 Python 저장 위치: {}",
        python_store.display()
    ));
    say(&format!(
        "[2/3] Python {} 실행 환경을 확인해요: {}",
        learning_python_version(),
        env_dir.display()
    ));
    let python = prepare_python_environment(&report, &uv, &env_dir, &python_store).await?;
    say("[3/3] 수업 패키지를 설치합니다 (pandas, scikit-learn, TensorFlow, XGBoost, matplotlib, seaborn, openpyxl, BeautifulSoup, requests, FinanceDataReader, yfinance). 몇 분 걸립니다.");
    let requirements =
        std::env::temp_dir().join(format!("molip-requirements-{}.txt", std::process::id()));
    std::fs::write(&requirements, learning_requirements()).map_err(|e| e.to_string())?;
    let python_str = python.to_string_lossy().into_owned();
    let req_str = requirements.to_string_lossy().into_owned();
    let mut package_args = vec!["pip", "install", "--python", &python_str, "-r", &req_str];
    if cfg!(windows) {
        package_args.extend([
            "--system",
            "--link-mode",
            "copy",
            "--no-config",
            "--no-managed-python",
            "--no-python-downloads",
        ]);
    }
    let result = run_logged(&report, &uv, &package_args, Some(&python_store)).await;
    let _ = std::fs::remove_file(&requirements);
    result?;
    Ok(format!("설치 완료 · {python_str}"))
}

#[cfg(test)]
mod install_tests {
    /// Confirm the old path used the minor junction, then make that alias unusable
    /// and verify the new environment uses and runs the real patch interpreter.
    #[cfg(windows)]
    #[tokio::test]
    #[ignore = "requires uv and Python download"]
    async fn environment_bypasses_unusable_minor_alias() {
        let uv = super::find_uv().await.expect("uv must be installed");
        let root = std::env::temp_dir().join(format!(
            "molip-python-alias-test-{}-{}",
            std::process::id(),
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        let store = root.join("python");
        let (tx, _rx) = tokio::sync::mpsc::unbounded_channel();
        super::run_logged(
            &tx,
            &uv,
            &[
                "python",
                "install",
                "3.13",
                "--no-bin",
                "--no-registry",
                "--no-config",
            ],
            Some(&store),
        )
        .await
        .unwrap();
        let old_env = root.join("old-env");
        let old_str = old_env.to_string_lossy();
        super::run_logged(
            &tx,
            &uv,
            &[
                "venv",
                &old_str,
                "--python",
                "3.13",
                "--managed-python",
                "--no-python-downloads",
                "--no-config",
            ],
            Some(&store),
        )
        .await
        .unwrap();
        let old_config = std::fs::read_to_string(old_env.join("pyvenv.cfg")).unwrap();
        assert!(old_config.contains("cpython-3.13-windows-x86_64-none"));
        let minor = store.join("cpython-3.13-windows-x86_64-none");
        // remove_dir removes only this test-created junction, never its contents.
        std::fs::remove_dir(&minor).unwrap();
        std::fs::create_dir(&minor).unwrap();
        std::fs::write(minor.join("python.exe"), "unusable minor alias").unwrap();
        let env = root.join("new-env");
        super::create_learning_environment(&tx, &uv, &env, &store)
            .await
            .unwrap();
        // The copied runtime must not depend on the original store or a venv launcher.
        let canonical_root = std::fs::canonicalize(&root).unwrap();
        assert!(std::fs::canonicalize(&store)
            .unwrap()
            .starts_with(&canonical_root));
        std::fs::rename(&store, root.join("source-unavailable")).unwrap();
        let python = env.join("python.exe");
        let output = super::probe(
            &python.to_string_lossy(),
            &["-c", "import sys,ssl,sqlite3; print(sys.version_info[:2])"],
        )
        .await
        .unwrap();
        assert_eq!(String::from_utf8_lossy(&output).trim(), "(3, 13)");
        assert!(!env.join("pyvenv.cfg").exists());
        assert!(!env.join("Scripts/python.exe").exists());
        assert!(!env.join("Lib/EXTERNALLY-MANAGED").exists());
        // root is a unique temporary fixture containing no remaining junctions.
        assert!(std::fs::canonicalize(&root)
            .unwrap()
            .starts_with(std::fs::canonicalize(std::env::temp_dir()).unwrap()));
        std::fs::remove_dir_all(&root).unwrap();
    }

    /// Exercises the real uv subprocess without downloading Python or packages.
    #[tokio::test]
    #[ignore = "requires uv"]
    async fn uv_uses_app_python_store() {
        let uv = super::find_uv().await.expect("uv must be installed");
        let store = crate::data_dir().unwrap().join("python");
        let (tx, mut rx) = tokio::sync::mpsc::unbounded_channel();
        super::run_logged(&tx, &uv, &["python", "dir"], Some(&store))
            .await
            .unwrap();
        drop(tx);
        let actual = rx.recv().await.expect("uv must report its Python store");
        assert_eq!(std::path::PathBuf::from(actual.trim()), store);
    }

    /// Needs the network and a few minutes: `cargo test -- --ignored environment_installs`.
    /// Uses a disposable app data folder, never the learner's environment.
    #[tokio::test]
    #[ignore]
    async fn environment_installs_and_passes_the_checks() {
        let directory = tempfile::tempdir().unwrap();
        let previous = std::env::var_os("MOLIP_DATA_DIR");
        std::env::set_var("MOLIP_DATA_DIR", directory.path());
        let (tx, mut rx) = tokio::sync::mpsc::unbounded_channel::<String>();
        #[cfg(target_os="macos")]
        crate::runtime_setup::prepare_openmp(&tx).await.unwrap();
        let worker = tokio::spawn(super::install(tx));
        while let Some(line) = rx.recv().await {
            eprintln!("{line}");
        }
        let done = worker.await.unwrap().unwrap();
        eprintln!("{done}");
        assert!(done.contains("ml-env"));
        let python = done.trim_start_matches("설치 완료 · ").to_string();
        verify_diagnostic(&python).await;
        // A cold package import can take longer than the interactive diagnostic
        // probe's 20 seconds (antivirus scanning and first-use caches on Windows).
        let mut command = tokio::process::Command::new(&python);
        if let Some(path)=crate::runtime_setup::library_path(){command.env("DYLD_LIBRARY_PATH",path);}
        command.args([
                "-I",
                "-c",
                "import pandas, sklearn, tensorflow, xgboost, matplotlib, seaborn, openpyxl, bs4, requests, FinanceDataReader, yfinance; print('ok')",
            ]).kill_on_drop(true);
        #[cfg(windows)]
        command.creation_flags(0x08000000);
        let output = tokio::time::timeout(std::time::Duration::from_secs(120), command.output())
            .await
            .expect("freshly installed packages must import within two minutes")
            .unwrap();
        assert!(
            output.status.success(),
            "{}",
            String::from_utf8_lossy(&output.stderr)
        );
        assert_eq!(String::from_utf8_lossy(&output.stdout).trim(), "ok");
        if let Some(value) = previous { std::env::set_var("MOLIP_DATA_DIR", value); }
        else { std::env::remove_var("MOLIP_DATA_DIR"); }
    }

    pub(super) async fn verify_diagnostic(python: &str) {
        let timed_out = super::inspect_python(python, std::time::Duration::from_nanos(1)).await;
        assert!(
            timed_out[0].ready,
            "An import timeout must not mark Python missing"
        );
        assert!(timed_out[1..].iter().all(|check| !check.ready
            && check.detail.contains("검사 시간 초과")
            && !check.detail.contains("패키지를 설치하세요")));
        let checks = super::inspect_python(python, std::time::Duration::from_secs(120)).await;
        assert!(checks.iter().any(|check| check.name == "TensorFlow · 딥러닝"));
        assert!(checks.iter().any(|check| check.name == "XGBoost · 부스팅 모델"));
        for check in checks {
            assert!(check.ready, "{}: {}", check.name, check.detail);
        }
    }
}

#[cfg(test)]
mod diagnostic_tests {
    #[tokio::test]
    #[ignore = "requires uv and an existing Python 3.13/3.12 installation"]
    async fn package_repair_preserves_working_environment() {
        let uv = super::find_uv().await.expect("uv");
        let root = tempfile::tempdir().unwrap();
        let env = root.path().join("ml-env");
        let (tx, _rx) = tokio::sync::mpsc::unbounded_channel();
        super::run_logged(&tx, &uv, &["venv", &env.to_string_lossy(), "--python", &super::python_executable(), "--no-python-downloads", "--no-config"], None).await.unwrap();
        let sentinel = env.join("existing-package-marker.txt");
        std::fs::write(&sentinel, "keep existing packages").unwrap();
        // No installer is available: a working environment must bypass creation.
        let python = super::prepare_python_environment(&tx, "missing-uv", &env, &root.path().join("python")).await.unwrap();
        assert!(python.is_file());
        assert_eq!(std::fs::read_to_string(&sentinel).unwrap(), "keep existing packages");
        assert!(!root.path().read_dir().unwrap().any(|entry| entry.unwrap().file_name().to_string_lossy().contains("backup")));
    }

    #[tokio::test]
    async fn slow_package_does_not_erase_other_package_results() {
        let python = super::python_executable();
        // Simulate a slow first TensorFlow import through the real child-process path.
        let prefix = "import importlib,time,types\ndef fixture_import(name):\n if name == 'tensorflow': time.sleep(2)\n return types.SimpleNamespace(__version__='fixture')\nimportlib.import_module=fixture_import\n";
        let checks = super::inspect_python_with_prefix(&python, std::time::Duration::from_millis(500), prefix).await;
        for name in ["pandas · 표 분석", "yfinance · 주가 받기 (야후)"] {
            let check = checks.iter().find(|c| c.name == name).unwrap();
            assert!(check.ready, "{}: {}", check.name, check.detail);
        }
        let slow = checks.iter().find(|c| c.name == "TensorFlow · 딥러닝").unwrap();
        assert!(!slow.ready && slow.detail.contains("검사 시간 초과"));
    }

    /// Recheck the existing app-owned environment without reinstalling it.
    #[tokio::test]
    #[ignore]
    async fn diagnostic_keeps_python_ready_after_import_timeout() {
        let environment = crate::data_dir().unwrap().join("ml-env");
        let python = environment.join(if cfg!(windows) {
            "python.exe"
        } else {
            "bin/python"
        });
        super::install_tests::verify_diagnostic(&python.to_string_lossy()).await;
    }
}

/// Repair only missing/broken tools. A successful installation is verified by real execution.
pub async fn prepare(report:tokio::sync::mpsc::UnboundedSender<String>)->Result<String,String> {
    static PREPARING:tokio::sync::Mutex<()>=tokio::sync::Mutex::const_new(());
    let _guard=PREPARING.try_lock().map_err(|_|"다른 환경 설치가 진행 중이에요.".to_string())?;
    let mut problems=vec![];
    for (name,result) in [("Java",crate::runtime_setup::prepare_java(&report).await),("C",crate::runtime_setup::prepare_c(&report).await)] {
        match result {Ok(line)=>{let _=report.send(line);},Err(error)=>{let _=report.send(format!("{name} · {error}"));problems.push(format!("{name} · {error}"));}}
    }
    #[cfg(target_os="macos")]
    if let Err(error)=crate::runtime_setup::prepare_openmp(&report).await{problems.push(error);}
    let checks=inspect_python(&python_executable(),std::time::Duration::from_secs(120)).await;
    if checks.iter().all(|check|check.ready) {
        let _=report.send("Python · 실행과 수업 패키지가 준비되어 있어요. 기존 환경을 유지해요.".into());
    }else{
        let needs_install = checks.iter().any(|check| !check.ready && !check.detail.contains("검사 시간 초과"));
        let checks = if needs_install {
        if let Err(error)=install(report.clone()).await{problems.push(format!("Python 패키지 설치 · {error}"));}
        inspect_python(&python_executable(),std::time::Duration::from_secs(120)).await
        } else { checks };
        for check in checks.into_iter().filter(|check|!check.ready){problems.push(format!("{} · {}",check.name,check.detail));}
    }
    if problems.is_empty(){Ok("Java·C·Python 실행 환경을 확인했어요. 앱을 다시 열 필요 없이 바로 사용할 수 있어요.".into())}
    else{Err(format!("준비된 도구는 바로 사용할 수 있어요. 추가 확인: {}",problems.join(" / ")))}
}
