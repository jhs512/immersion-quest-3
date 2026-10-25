#![cfg(all(feature="desktop",debug_assertions))]
//! The first Vim step's narration in the real app: per caption, the highlighted text, the spotlight and
//! the caption box (tools/player-pilot-vim-narration.js). Old text highlights must not stay on terminal
//! sentences, the caption must not cover the header or step tabs, the last sentence lights the live panel.
#[allow(dead_code)]
#[path="support/native_player.rs"] mod native_player;
#[test]
#[ignore="Requires an interactive desktop"]
fn vim_first_step_narration_moves_highlight_and_caption_with_its_targets(){
    let session=molip_quest::pilot_session::PilotSession::new().unwrap();
    let _=std::fs::remove_file("target/pilot-native-result.json");
    let mut command=std::process::Command::new(env!("CARGO_BIN_EXE_molip-quest"));
    native_player::configure(&session,&mut command,"vim-narration");command.env("MOLIP_PILOT_SELF_TEST","vim-narration");
    let status=native_player::wait(&mut command.spawn().unwrap(),300,"vim-narration");
    let _=std::fs::copy(session.directory().join("vim-narration.log"),"target/pilot-vim-narration.log");
    let raw=std::fs::read_to_string("target/pilot-native-result.json").unwrap_or_else(|error|panic!("no result ({error}); exit {status:?}; log: {}",std::fs::read_to_string(session.directory().join("vim-narration.log")).unwrap_or_default()));
    std::fs::write("target/pilot-vim-narration.json",&raw).unwrap();
    let result:serde_json::Value=serde_json::from_str(&raw).unwrap();
    assert!(status.success()&&result["passed"]==true,"{}",serde_json::to_string_pretty(&serde_json::json!({"problems":result["problems"],"error":result["error"]})).unwrap());
}
