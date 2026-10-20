#![cfg(all(feature="desktop",debug_assertions))]
#[allow(dead_code)]
#[path="support/native_player.rs"] mod native_player;
#[test]
#[ignore="Requires an interactive desktop and JDK 25"]
fn java_source_and_terminal_share_the_native_workspace(){
    let session=molip_quest::pilot_session::PilotSession::new().unwrap();
    let mut command=std::process::Command::new(env!("CARGO_BIN_EXE_molip-quest"));
    native_player::configure(&session,&mut command,"java-launch");command.env("MOLIP_PILOT_SELF_TEST","java-launch");
    let status=native_player::wait(&mut command.spawn().unwrap(),220,"java-launch");
    let result:serde_json::Value=serde_json::from_str(&std::fs::read_to_string("target/pilot-native-result.json").unwrap()).unwrap();
    std::fs::copy("target/pilot-native-result.json","target/pilot-java-launch-native-result.json").unwrap();
    assert!(status.success()&&result["passed"]==true,"{result}");assert_eq!(result["checked"].as_array().unwrap().len(),12);
}
