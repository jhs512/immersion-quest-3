#![cfg(all(feature="desktop",debug_assertions))]
#[allow(dead_code)]
#[path="support/native_player.rs"] mod native_player;

#[test]
#[ignore="Requires an interactive desktop"]
fn git_terminal_survives_explanation_completion_and_cancellation() {
    let session=molip_quest::pilot_session::PilotSession::new().unwrap();
    let mut command=std::process::Command::new(env!("CARGO_BIN_EXE_molip-quest"));
    native_player::configure(&session,&mut command,"terminal-restore");
    command.env("MOLIP_PILOT_SELF_TEST","terminal-restore");
    let status=native_player::wait(&mut command.spawn().unwrap(),160,"terminal-restore");
    let raw=std::fs::read_to_string("target/pilot-native-result.json").unwrap();
    let result:serde_json::Value=serde_json::from_str(&raw).unwrap();
    assert!(status.success()&&result["passed"]==true,"{result}");
    assert_eq!(result["checked"].as_array().unwrap().len(),2);
}
