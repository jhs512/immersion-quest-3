#![cfg(all(feature = "desktop", debug_assertions))]
#[allow(dead_code)]
#[path = "support/native_player.rs"]
mod native_player;

#[test]
#[ignore = "Requires Docker Desktop and the native player"]
fn sql_tables_are_visible_before_the_first_query() {
    let session = molip_quest::pilot_session::PilotSession::new().unwrap();
    let mut command = std::process::Command::new(env!("CARGO_BIN_EXE_molip-quest"));
    native_player::configure(&session, &mut command, "sql-browser");
    command.env("MOLIP_PILOT_SELF_TEST", "sql-browser");
    let status = native_player::wait(&mut command.spawn().unwrap(), 180, "SQL table browser");
    let raw = std::fs::read_to_string("target/pilot-native-result.json").unwrap();
    std::fs::write("target/pilot-sql-browser-result.json", &raw).unwrap();
    let result: serde_json::Value = serde_json::from_str(&raw).unwrap();
    assert!(status.success() && result["passed"] == true, "{result}");
}
