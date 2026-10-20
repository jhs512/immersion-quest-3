#![cfg(all(feature="desktop",debug_assertions))]
#[allow(dead_code)]
#[path="support/native_player.rs"] mod native_player;
#[test]
#[ignore="Requires an interactive desktop"]
fn native_bash_narration_runs_ls_and_overview() {
    let session=molip_quest::pilot_session::PilotSession::new().unwrap();
    // Select this isolated fixture before launch. Switching versions in the
    // WebView remounts RepositoryPlayer and can discard an in-flight lesson open.
    let version=molip_quest::lesson_registry::find("bash-basics").unwrap().pilot;
    let initial=serde_json::json!({"corrupted":false,"version":version.to_string(),"issue":null,"comments":[]});
    std::fs::write(session.directory().join("pilot-remote.json"),serde_json::to_vec(&initial).unwrap()).unwrap();
    let mut command=std::process::Command::new(env!("CARGO_BIN_EXE_molip-quest"));
    native_player::configure(&session,&mut command,"bash-basics");command.env("MOLIP_PILOT_SELF_TEST","bash-basics");
    let status=native_player::wait(&mut command.spawn().unwrap(),200,"bash-basics");
    let _=std::fs::copy(session.directory().join("bash-basics.log"),"target/mq3-bash-native-process.log");
    let result:serde_json::Value=serde_json::from_str(&std::fs::read_to_string("target/pilot-native-result.json").unwrap()).unwrap();
    std::fs::copy("target/pilot-native-result.json","target/pilot-bash-native-result.json").unwrap();
    assert!(status.success()&&result["passed"]==true,"{result}");
    assert_eq!(result["checked"].as_array().unwrap().len(),3);
}
