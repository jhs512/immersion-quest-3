#![cfg(all(feature="desktop",debug_assertions))]
#[allow(dead_code)]
#[path="support/native_player.rs"] mod native_player;

#[test]
#[ignore="Requires an interactive desktop"]
fn toolbar_and_menus_fit_the_actual_webview() {
    let session=molip_quest::pilot_session::PilotSession::new().unwrap();
    let mut command=std::process::Command::new(env!("CARGO_BIN_EXE_molip-quest"));
    native_player::configure(&session,&mut command,"toolbar-audit");
    command.env("MOLIP_PILOT_SELF_TEST","toolbar-audit");
    let status=native_player::wait(&mut command.spawn().unwrap(),150,"toolbar-audit");
    let raw=std::fs::read_to_string("target/pilot-native-result.json").unwrap();
    let result:serde_json::Value=serde_json::from_str(&raw).unwrap();
    std::fs::write("target/pilot-toolbar-result.json",result.to_string()).unwrap();
    assert!(status.success()&&result["passed"]==true,"{result}");
}
