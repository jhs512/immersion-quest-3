#![cfg(all(feature = "desktop", debug_assertions))]
#[path = "support/native_player.rs"]
mod native_player;
use molip_quest::pilot_session::PilotSession;
#[test]
#[ignore = "Requires an interactive desktop and the built player binary"]
fn actual_player_reopens_saved_answer_and_progress_after_process_restart() {
    let session = PilotSession::new().unwrap();
    for phase in ["seed", "reopen"] {
        native_player::run(
            std::path::Path::new(env!("CARGO_BIN_EXE_molip-quest")),
            &session,
            phase,
        );
    }
}
