#![cfg(all(feature="desktop",debug_assertions))]
#[allow(dead_code)]
#[path="support/native_player.rs"] mod native_player;
#[test]
#[ignore="Requires an interactive desktop"]
fn shortcuts_show_actual_failure_and_preserve_it_after_explanation() {
    let session=molip_quest::pilot_session::PilotSession::new().unwrap();
    let mut command=std::process::Command::new(env!("CARGO_BIN_EXE_molip-quest"));
    native_player::configure(&session,&mut command,"shortcuts-feedback");
    command.env("MOLIP_PILOT_SELF_TEST","shortcuts-feedback");
    let status=native_player::wait(&mut command.spawn().unwrap(),150,"shortcuts-feedback");
    let raw=std::fs::read_to_string("target/pilot-native-result.json").unwrap();
    std::fs::write("target/mq-shortcuts-native-result.json",&raw).unwrap();
    let result:serde_json::Value=serde_json::from_str(&raw).unwrap();
    assert!(status.success()&&result["passed"]==true,"{result}");
    assert_eq!(result["checked"].as_array().unwrap().len(),4);
}
