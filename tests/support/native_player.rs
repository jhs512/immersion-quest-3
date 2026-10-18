use molip_quest::pilot_session::PilotSession;
use std::{
    path::Path,
    process::{Child, Command, ExitStatus},
    time::{Duration, Instant},
};

pub fn configure(session: &PilotSession, command: &mut Command, phase: &str) {
    session.configure(command);
    command
        .env("MOLIP_PILOT_SELF_TEST", format!("restart-{phase}"))
        .env_remove("DIOXUS_DEVSERVER_IP")
        .env_remove("DIOXUS_DEVSERVER_PORT")
        .env_remove("MOLIP_DEV_LIVE")
        .env_remove("MOLIP_GH_SETUP_PREVIEW")
        .env_remove("MOLIP_LEGACY");
    #[cfg(windows)]
    {
        use std::os::windows::process::CommandExt;
        command.creation_flags(0x08000000);
    }
    let log = std::fs::File::create(session.directory().join(format!("{phase}.log"))).unwrap();
    command.stdout(log.try_clone().unwrap()).stderr(log);
}
pub fn wait(child: &mut Child, seconds: u64, label: &str) -> ExitStatus {
    let deadline = Instant::now() + Duration::from_secs(seconds);
    loop {
        if let Some(status) = child.try_wait().unwrap() {
            return status;
        }
        if Instant::now() > deadline {
            let _ = child.kill();
            let _ = child.wait();
            panic!("{label} timed out");
        }
        std::thread::sleep(Duration::from_millis(100));
    }
}
pub fn result(session: &PilotSession, phase: &str) -> serde_json::Value {
    let path = session.directory().join(format!("restart-{phase}.json"));
    let raw = std::fs::read_to_string(&path).unwrap_or_else(|error| {
        panic!(
            "Missing {phase} result: {error}: {}",
            std::fs::read_to_string(session.directory().join(format!("{phase}.log")))
                .unwrap_or_default()
        )
    });
    std::fs::create_dir_all("target").unwrap();
    std::fs::write(format!("target/pilot-restart-{phase}.json"), &raw).unwrap();
    let value: serde_json::Value = serde_json::from_str(&raw).unwrap();
    assert_eq!(value["passed"], true, "{value}");
    value
}
pub fn run(executable: &Path, session: &PilotSession, phase: &str) {
    let mut command = Command::new(executable);
    configure(session, &mut command, phase);
    let mut child = command.spawn().unwrap();
    let status = wait(&mut child, 60, phase);
    let value = result(session, phase);
    assert!(status.success(), "{phase}: {value}");
}
