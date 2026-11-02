//! Compares MQ's report capture from a helper process with capture inside the window's own process.
use serde_json::{json, Value};
use std::{path::PathBuf, time::Duration};

#[link(name = "CoreGraphics", kind = "framework")]
extern "C" {
    fn CGPreflightScreenCaptureAccess() -> bool;
}

fn preflight() -> bool {
    unsafe { CGPreflightScreenCaptureAccess() }
}

/// Same filter and capture as `bug_report::capture` at build 165.
fn attempt(pid: u32, require_title: bool) -> Value {
    let windows = match xcap::Window::all() {
        Ok(windows) => windows,
        Err(error) => return json!({"listed": false, "error": error.to_string()}),
    };
    let total = windows.len();
    let owned: Vec<_> = windows
        .into_iter()
        .filter(|w| w.pid().ok() == Some(pid))
        .collect();
    let titles: Vec<String> = owned
        .iter()
        .map(|w| w.title().unwrap_or_else(|e| format!("<{e}>")))
        .collect();
    let chosen = owned
        .into_iter()
        .filter(|w| !require_title || w.title().is_ok_and(|t| t == "MQ"))
        .filter(|w| !w.is_minimized().unwrap_or(true))
        .max_by_key(|w| w.width().unwrap_or(0) as u64 * w.height().unwrap_or(0) as u64);
    let Some(window) = chosen else {
        return json!({"listed": true, "total_windows": total, "owned_titles": titles, "error": "MQ window unavailable"});
    };
    match window.capture_image() {
        Ok(image) => {
            let pixel = image.get_pixel(image.width() / 2, image.height() / 2).0;
            json!({"listed": true, "total_windows": total, "owned_titles": titles,
                "width": image.width(), "height": image.height(), "center_rgba": pixel,
                "webview_content_visible": pixel[0] > 200 && pixel[1] < 80 && pixel[2] < 80})
        }
        Err(error) => json!({"listed": true, "total_windows": total, "owned_titles": titles, "error": error.to_string()}),
    }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.get(1).map(String::as_str) == Some("--helper") {
        let pid = args[2].parse().unwrap();
        let report = json!({"helper_pid": std::process::id(), "preflight": preflight(), "capture": attempt(pid, true)});
        std::fs::write(&args[3], report.to_string()).unwrap();
        return;
    }
    let out = PathBuf::from(args.get(1).expect("output json path"));
    use tao::{event::Event, event_loop::{ControlFlow, EventLoop}, window::WindowBuilder};
    let event_loop = EventLoop::new();
    let window = WindowBuilder::new()
        .with_title("MQ")
        .with_inner_size(tao::dpi::LogicalSize::new(800.0, 600.0))
        .build(&event_loop)
        .unwrap();
    let _webview = wry::WebViewBuilder::new()
        .with_html("<html><body style='margin:0;background:#ff0000;height:100vh'></body></html>")
        .build(&window)
        .unwrap();
    let start = std::time::Instant::now();
    event_loop.run(move |event, _, flow| {
        *flow = ControlFlow::WaitUntil(std::time::Instant::now() + Duration::from_millis(200));
        if !matches!(event, Event::NewEvents(_)) || start.elapsed() < Duration::from_secs(4) {
            return;
        }
        let me = std::process::id();
        let helper_out = out.with_extension("helper.json");
        let status = std::process::Command::new(std::env::current_exe().unwrap())
            .args(["--helper", &me.to_string()])
            .arg(&helper_out)
            .status();
        let helper: Value = std::fs::read(&helper_out)
            .ok()
            .and_then(|b| serde_json::from_slice(&b).ok())
            .unwrap_or_else(|| json!({"status": format!("{status:?}")}));
        let report = json!({
            "app_pid": me,
            "macos": std::process::Command::new("sw_vers").arg("-productVersion").output().map(|o| String::from_utf8_lossy(&o.stdout).trim().to_string()).unwrap_or_default(),
            "preflight_in_app": preflight(),
            "in_process_with_title": attempt(me, true),
            "in_process_pid_only": attempt(me, false),
            "helper_process": helper,
        });
        std::fs::write(&out, serde_json::to_string_pretty(&report).unwrap()).unwrap();
        *flow = ControlFlow::Exit;
    });
}
