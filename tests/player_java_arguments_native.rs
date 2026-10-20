#![cfg(all(feature="desktop",debug_assertions))]
#[allow(dead_code)]
#[path="support/native_player.rs"] mod native_player;
#[test]
#[ignore="Requires an interactive desktop and JDK 25"]
fn argument_lesson_preserves_editor_terminal_demonstrations_and_progress(){
    let session=molip_quest::pilot_session::PilotSession::new().unwrap();
    let mut command=std::process::Command::new(env!("CARGO_BIN_EXE_molip-quest"));
    native_player::configure(&session,&mut command,"java-arguments");command.env("MOLIP_PILOT_SELF_TEST","java-arguments");
    let status=native_player::wait(&mut command.spawn().unwrap(),220,"java-arguments");
    let result:serde_json::Value=serde_json::from_str(&std::fs::read_to_string("target/pilot-native-result.json").unwrap()).unwrap();
    std::fs::copy("target/pilot-native-result.json","target/pilot-java-arguments-native-result.json").unwrap();
    assert!(status.success()&&result["passed"]==true,"{result}");assert_eq!(result["checked"].as_array().unwrap().len(),12);
}
