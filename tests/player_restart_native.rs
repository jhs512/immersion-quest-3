#![cfg(all(feature = "desktop", debug_assertions))]
use molip_quest::pilot_session::PilotSession;
#[test]
#[ignore = "Requires an interactive desktop and the built player binary"]
fn actual_player_reopens_saved_answer_and_progress_after_process_restart() {
    let session = PilotSession::new().unwrap();
    for phase in ["seed", "reopen"] {
        let mut command = std::process::Command::new(env!("CARGO_BIN_EXE_molip-quest"));
        session.configure(&mut command);
        command
            .env("MOLIP_PILOT_SELF_TEST", format!("restart-{phase}"))
            .env_remove("DIOXUS_DEVSERVER_IP")
            .env_remove("DIOXUS_DEVSERVER_PORT");
        #[cfg(windows)]
        {
            use std::os::windows::process::CommandExt;
            command.creation_flags(0x08000000);
        }
        command
            .stdout(std::process::Stdio::null())
            .stderr(std::process::Stdio::null());
        let mut child = command.spawn().unwrap();
        let deadline = std::time::Instant::now() + std::time::Duration::from_secs(60);
        let status = loop {
            if let Some(status) = child.try_wait().unwrap() {
                break status;
            }
            if std::time::Instant::now() > deadline {
                let _ = child.kill();
                let _ = child.wait();
                panic!("Native restart {phase} timed out");
            }
            std::thread::sleep(std::time::Duration::from_millis(100));
        };
        let raw =
            std::fs::read_to_string(session.directory().join(format!("restart-{phase}.json")))
                .unwrap();
        let result: serde_json::Value = serde_json::from_str(&raw).unwrap();
        std::fs::create_dir_all("target").unwrap();
        std::fs::write(format!("target/pilot-restart-{phase}.json"), &raw).unwrap();
        assert!(
            status.success() && result["passed"] == true,
            "{phase}: {result}"
        );
    }
}
