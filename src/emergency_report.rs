//! A process independent of the Dioxus renderer and main event loop.
use std::{
    io::{BufRead, Write},
    path::Path,
    process::{Child, ChildStdin, Command, Stdio},
    sync::{Mutex, OnceLock},
};
static PIPE: OnceLock<Mutex<ChildStdin>> = OnceLock::new();
struct CaptureTask {
    stop: std::sync::mpsc::Sender<()>,
    worker: Option<std::thread::JoinHandle<()>>,
}
impl Drop for CaptureTask {
    fn drop(&mut self) {
        let _ = self.stop.send(());
        if let Some(worker) = self.worker.take() {
            let _ = worker.join();
        }
    }
}
fn command() -> Result<Command, String> {
    let mut command = Command::new(std::env::current_exe().map_err(|e| e.to_string())?);
    #[cfg(windows)]
    {
        use std::os::windows::process::CommandExt;
        command.creation_flags(0x08000000);
    }
    Ok(command)
}
pub struct AgentGuard(Child);
impl Drop for AgentGuard {
    fn drop(&mut self) {
        let _ = self.0.kill();
        let _ = self.0.wait();
    }
}
pub fn start() -> Option<AgentGuard> {
    if molip_quest::pilot_source::enabled()
        && std::env::var_os("MOLIP_FORCE_REPORT_AGENT").is_none()
    {
        return None;
    }
    #[cfg(any(target_os = "windows", target_os = "macos"))]
    {
        let mut child = command()
            .ok()?
            .args(["--diagnostics-agent", &std::process::id().to_string()])
            .stdin(Stdio::piped())
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .spawn()
            .ok()?;
        let pipe = child.stdin.take()?;
        let _ = PIPE.set(Mutex::new(pipe));
        Some(AgentGuard(child))
    }
    #[cfg(not(any(target_os = "windows", target_os = "macos")))]
    {
        None
    }
}
pub fn request(kind: &str) -> Result<(), String> {
    let kind = if kind == "content" { "content" } else { "bug" };
    std::thread::Builder::new()
        .name("report-request".into())
        .spawn(move || {
            molip_quest::telemetry::flush();
            if let Err(error) = request_inner(kind) {
                notify(&error);
            }
        })
        .map_err(|e| e.to_string())?;
    Ok(())
}
fn request_inner(kind: &str) -> Result<(), String> {
    let kind = if kind == "content" { "content" } else { "bug" };
    if let Some(pipe) = PIPE.get() {
        if let Ok(mut pipe) = pipe.try_lock() {
            if writeln!(pipe, "{kind}").is_ok() {
                return Ok(());
            }
        }
    }
    command()?
        .args(["--report-dialog", &std::process::id().to_string(), kind])
        .stdin(Stdio::null())
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn()
        .map_err(|e| e.to_string())?;
    Ok(())
}
pub fn cli(args: &[String]) -> bool {
    let flag = args.get(1).map(String::as_str).unwrap_or("");
    if !matches!(
        flag,
        "--diagnostics-agent" | "--report-dialog" | "--capture-report"
    ) {
        return false;
    }
    let Some(parent) = args
        .get(2)
        .and_then(|s| s.parse::<u32>().ok())
        .filter(|id| *id > 0)
    else {
        return true;
    };
    match flag {
        "--diagnostics-agent" => {
            #[cfg(any(target_os = "windows", target_os = "macos"))]
            agent(parent);
        }
        "--report-dialog" => {
            if let Err(error) = dialog(parent, args.get(3).map(String::as_str).unwrap_or("bug")) {
                notify(&error);
            }
        }
        "--capture-report" =>
        {
            #[cfg(any(target_os = "windows", target_os = "macos"))]
            if let Some(path) = args.get(3) {
                let _ = molip_quest::bug_report::capture(parent, Path::new(path));
            }
        }
        _ => {}
    }
    true
}

#[cfg(any(target_os = "windows", target_os = "macos"))]
fn agent(parent: u32) {
    use dioxus::desktop::tao::{
        event::Event,
        event_loop::{ControlFlow, EventLoopBuilder},
    };
    use global_hotkey::{
        hotkey::{Code, HotKey, Modifiers},
        GlobalHotKeyEvent, GlobalHotKeyManager, HotKeyState,
    };
    #[derive(Clone)]
    enum Signal {
        Report(&'static str, bool),
        Quit,
    }
    let event_loop = EventLoopBuilder::<Signal>::with_user_event().build();
    #[cfg(target_os = "macos")]
    let event_loop = {
        use dioxus::desktop::tao::platform::macos::{ActivationPolicy, EventLoopExtMacOS};
        let mut event_loop = event_loop;
        event_loop.set_activation_policy(ActivationPolicy::Accessory);
        event_loop
    };
    let Ok(manager) = GlobalHotKeyManager::new() else {
        return;
    };
    let modifiers = Some(Modifiers::CONTROL | Modifiers::ALT | Modifiers::SHIFT);
    let bug = HotKey::new(modifiers, Code::KeyB);
    let content = HotKey::new(modifiers, Code::KeyP);
    // Normal buttons still work when the OS chord is already occupied.
    let bug_ready = manager.register(bug).is_ok();
    let content_ready = manager.register(content).is_ok();
    if let Ok(root) = molip_quest::data_dir() {
        let _=std::fs::write(root.join(format!("report-agent-{parent}.json")),serde_json::json!({"pid":std::process::id(),"bug_hotkey":bug_ready,"content_hotkey":content_ready}).to_string());
    }
    let proxy = event_loop.create_proxy();
    let hotkeys = proxy.clone();
    GlobalHotKeyEvent::set_event_handler(Some(move |event: GlobalHotKeyEvent| {
        if event.state == HotKeyState::Pressed {
            let kind = if event.id == bug.id() {
                "bug"
            } else if event.id == content.id() {
                "content"
            } else {
                return;
            };
            let _ = hotkeys.send_event(Signal::Report(kind, false));
        }
    }));
    std::thread::spawn(move || {
        for line in std::io::stdin().lock().lines() {
            match line.as_deref() {
                Ok("bug") => {
                    let _ = proxy.send_event(Signal::Report("bug", true));
                }
                Ok("content") => {
                    let _ = proxy.send_event(Signal::Report("content", true));
                }
                _ => {}
            }
        }
        let _ = proxy.send_event(Signal::Quit);
    });
    let mut report: Option<Child> = None;
    let mut active_kind = "";
    let mut pending = None;
    let deferred = event_loop.create_proxy();
    event_loop.run(move |event, _, flow| {
        let _keep = &manager;
        *flow = ControlFlow::Wait;
        match event {
            Event::UserEvent(Signal::Quit) => *flow = ControlFlow::Exit,
            Event::UserEvent(Signal::Report(kind, forced)) => {
                if report
                    .as_mut()
                    .is_some_and(|c| c.try_wait().ok().flatten().is_none())
                {
                    if kind != active_kind {
                        pending = Some((kind, forced));
                        *flow = ControlFlow::WaitUntil(
                            std::time::Instant::now() + std::time::Duration::from_millis(100),
                        );
                    }
                    return;
                }
                active_kind = kind;
                let focused = forced
                    || xcap::Window::all().is_ok_and(|windows| {
                        windows.into_iter().any(|w| {
                            w.pid().ok() == Some(parent) && w.is_focused().unwrap_or(false)
                        })
                    });
                if focused {
                    report = command().ok().and_then(|mut command| {
                        command
                            .args(["--report-dialog", &parent.to_string(), kind])
                            .stdin(Stdio::null())
                            .stdout(Stdio::null())
                            .stderr(Stdio::null())
                            .spawn()
                            .ok()
                    });
                }
            }
            Event::MainEventsCleared => {
                if pending.is_some() {
                    if report
                        .as_mut()
                        .is_none_or(|c| c.try_wait().ok().flatten().is_some())
                    {
                        if let Some((kind, forced)) = pending.take() {
                            let _ = deferred.send_event(Signal::Report(kind, forced));
                        }
                    } else {
                        *flow = ControlFlow::WaitUntil(
                            std::time::Instant::now() + std::time::Duration::from_millis(100),
                        );
                    }
                }
            }
            _ => {}
        }
    });
}
fn script(path: &Path, content: &str) -> Result<(), String> {
    let mut bytes = Vec::new();
    if cfg!(windows) {
        bytes.extend_from_slice(b"\xef\xbb\xbf");
    }
    bytes.extend_from_slice(content.as_bytes());
    std::fs::write(path, bytes).map_err(|e| e.to_string())
}
fn notify(message: &str) {
    let Ok(folder) = tempfile::tempdir() else {
        return;
    };
    let file = folder.path().join("message.txt");
    let _ = std::fs::write(&file, message);
    #[cfg(windows)]
    {
        let path = folder.path().join("notify.ps1");
        let _=script(&path,"param([string]$Path)\nAdd-Type -AssemblyName System.Windows.Forms\n[System.Windows.Forms.MessageBox]::Show([System.IO.File]::ReadAllText($Path),'MQ · 신고') | Out-Null\n");
        let mut command = Command::new("powershell.exe");
        use std::os::windows::process::CommandExt;
        command.creation_flags(0x08000000);
        let _ = command
            .args(["-NoProfile", "-ExecutionPolicy", "Bypass", "-File"])
            .arg(path)
            .arg(file)
            .status();
    }
    #[cfg(target_os = "macos")]
    {
        let path = folder.path().join("notify.js");
        let _=script(&path,"ObjC.import('Foundation');function run(args){const app=Application.currentApplication();app.includeStandardAdditions=true;const text=ObjC.unwrap($.NSString.stringWithContentsOfFileEncodingError(args[0],$.NSUTF8StringEncoding,null));app.displayDialog(text,{withTitle:'MQ · 신고',buttons:['확인'],defaultButton:'확인'});}");
        let _ = Command::new("/usr/bin/osascript")
            .args(["-l", "JavaScript"])
            .arg(path)
            .arg(file)
            .status();
    }
}
fn dialog(parent: u32, kind: &str) -> Result<(), String> {
    let path = molip_quest::bug_report::prepare(parent, kind)?;
    let folder = path.parent().ok_or("report path")?;
    let mut capture = command()?
        .args(["--capture-report", &parent.to_string()])
        .arg(folder.join("screen.png"))
        .stdin(Stdio::null())
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn()
        .ok();
    // Capture has a separate lifetime: PrintWindow on a hung app can itself hang.
    let (stop_capture, capture_stopped) = std::sync::mpsc::channel();
    let _capture_task = CaptureTask {
        stop: stop_capture,
        worker: Some(std::thread::spawn(move || {
            if let Some(child) = capture.as_mut() {
                for _ in 0..30 {
                    if child.try_wait().ok().flatten().is_some() {
                        return;
                    }
                    if capture_stopped
                        .recv_timeout(std::time::Duration::from_millis(100))
                        .is_ok()
                    {
                        break;
                    }
                }
                let _ = child.kill();
                let _ = child.wait();
            }
        })),
    };
    let native = folder.join(if cfg!(windows) {
        "report.ps1"
    } else {
        "report.js"
    });
    script(
        &native,
        if cfg!(windows) {
            include_str!("../assets/diagnostics/report.ps1")
        } else {
            include_str!("../assets/diagnostics/report.js")
        },
    )?;
    #[cfg(windows)]
    return windows_dialog(&native, &path);
    #[cfg(not(windows))]
    loop {
        #[cfg(windows)]
        let result = {
            use std::os::windows::process::CommandExt;
            let mut command = Command::new("powershell.exe");
            command.creation_flags(0x08000000);
            command
                .args(["-NoProfile", "-ExecutionPolicy", "Bypass", "-File"])
                .arg(&native)
                .arg(&path)
                .status()
        };
        #[cfg(target_os = "macos")]
        let result = Command::new("/usr/bin/osascript")
            .args(["-l", "JavaScript"])
            .arg(&native)
            .arg(&path)
            .status();
        #[cfg(not(any(target_os = "windows", target_os = "macos")))]
        return Err("Native reports are supported on Windows and macOS.".into());
        #[cfg(any(target_os = "windows", target_os = "macos"))]
        {
            if !result.map_err(|e| e.to_string())?.success() {
                return Ok(());
            }
            let response =
                std::fs::read_to_string(folder.join("response.json")).map_err(|e| e.to_string())?;
            let response: serde_json::Value =
                serde_json::from_str(response.trim_start_matches('\u{feff}'))
                    .map_err(|e| e.to_string())?;
            let mut draft = molip_quest::bug_report::load(&path)?;
            draft.description = response["description"].as_str().unwrap_or("").into();
            draft.include_screen = response["include_screen"] == true;
            molip_quest::bug_report::save(&path, &draft)?;
            match molip_quest::bug_report::submit(&path) {
                Ok(url) => {
                    notify("신고를 보냈어요. GitHub 이슈를 열어요.");
                    open_issue(&url);
                    return Ok(());
                }
                Err(error) => {
                    notify(&format!("신고를 보내지 못했어요. 기록은 이 컴퓨터에 보관했어요. 다시 보내거나 취소할 수 있어요.\n\n{error}"));
                }
            }
        }
    }
}
#[cfg(not(windows))]
fn open_issue(url: &str) {
    if !url.starts_with("https://github.com/") {
        return;
    }
    #[cfg(windows)]
    {
        use std::os::windows::process::CommandExt;
        let _ = Command::new("rundll32.exe")
            .creation_flags(0x08000000)
            .args(["url.dll,FileProtocolHandler", url])
            .spawn();
    }
    #[cfg(target_os = "macos")]
    let _ = Command::new("/usr/bin/open").arg(url).spawn();
}

#[cfg(windows)]
fn windows_dialog(native: &Path, path: &Path) -> Result<(), String> {
    use std::os::windows::process::CommandExt;
    let mut command = Command::new("powershell.exe");
    command.creation_flags(0x08000000);
    let mut child = command
        .args(["-NoProfile", "-ExecutionPolicy", "Bypass", "-File"])
        .arg(native)
        .arg(path)
        .spawn()
        .map_err(|e| e.to_string())?;
    let folder = path.parent().ok_or("report folder")?;
    let mut seen = String::new();
    let mut upload: Option<std::sync::mpsc::Receiver<(String, Result<String, String>)>> = None;
    loop {
        let open = child.try_wait().map_err(|e| e.to_string())?.is_none();
        if !open && upload.is_none() {
            return Ok(());
        }
        if upload.is_none() && open {
            if let Ok(text) = std::fs::read_to_string(folder.join("response.json")) {
                if let Ok(response) =
                    serde_json::from_str::<serde_json::Value>(text.trim_start_matches('\u{feff}'))
                {
                    if let Some(attempt) = response["attempt"].as_str().filter(|a| *a != seen) {
                        seen = attempt.into();
                        let mut draft = molip_quest::bug_report::load(path)?;
                        draft.description = response["description"].as_str().unwrap_or("").into();
                        draft.include_screen = response["include_screen"] == true;
                        molip_quest::bug_report::save(path, &draft)?;
                        let (tx, rx) = std::sync::mpsc::channel();
                        let path = path.to_owned();
                        let attempt = seen.clone();
                        std::thread::spawn(move || {
                            let result = molip_quest::bug_report::submit(&path);
                            let _ = tx.send((attempt, result));
                        });
                        upload = Some(rx);
                    }
                }
            }
        }
        if let Some(result) = upload.as_ref().and_then(|rx| rx.try_recv().ok()) {
            let (attempt, result) = result;
            let outcome = match result {
                Ok(url) => {
                    serde_json::json!({"attempt":attempt,"ok":true,"url":url,"message":"신고를 보냈어요. 이슈 열기 버튼에서 확인할 수 있어요."})
                }
                Err(error) => {
                    serde_json::json!({"attempt":attempt,"ok":false,"message":format!("신고 전송 실패. 기록은 보관했어요. 다시 시도할 수 있어요. {error}")})
                }
            };
            std::fs::write(
                folder.join("outcome.json"),
                serde_json::to_vec(&outcome).map_err(|e| e.to_string())?,
            )
            .map_err(|e| e.to_string())?;
            upload = None;
        }
        std::thread::sleep(std::time::Duration::from_millis(100));
    }
}
