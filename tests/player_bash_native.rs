#![cfg(all(feature="desktop",debug_assertions))]
#[allow(dead_code)]
#[path="support/native_player.rs"] mod native_player;
#[test]
#[ignore="Requires an interactive desktop"]
fn native_bash_narration_runs_ls_and_overview() {
    let session=molip_quest::pilot_session::PilotSession::new().unwrap();
    let mut command=std::process::Command::new(env!("CARGO_BIN_EXE_molip-quest"));
    native_player::configure(&session,&mut command,"bash-basics");command.env("MOLIP_PILOT_SELF_TEST","bash-basics");
    let status=native_player::wait(&mut command.spawn().unwrap(),200,"bash-basics");
    let _=std::fs::copy(session.directory().join("bash-basics.log"),"target/mq3-bash-native-process.log");
    let result:serde_json::Value=serde_json::from_str(&std::fs::read_to_string("target/pilot-native-result.json").unwrap()).unwrap();
    assert!(status.success()&&result["passed"]==true,"{result}");
    assert_eq!(result["checked"].as_array().unwrap().len(),2);
}
