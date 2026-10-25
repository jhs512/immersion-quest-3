#![cfg(all(feature="desktop",debug_assertions))]
//! The narration speed chosen in the select survives step and lesson changes (up to 3x), and
//! 관리자 자동 풀이 initializes a practice workspace once per run and keeps the real cumulative
//! state; every pass is a real, recorded pass. Measured in the real app (tools/player-pilot-auto-state.js).
#[allow(dead_code)]
#[path="support/native_player.rs"] mod native_player;
use molip_quest::issue_progress::{self,EventKind};

#[test]
#[ignore="Requires an interactive desktop, Bash and JDK 25"]
fn speed_choice_persists_and_auto_run_initializes_each_workspace_once(){
    let session=molip_quest::pilot_session::PilotSession::new().unwrap();
    let initial=serde_json::json!({"corrupted":false,"version":molip_quest::pilot_source::AUTO_CHAIN_VERSION.to_string(),"issue":null,"comments":[]});
    std::fs::write(session.directory().join("pilot-remote.json"),serde_json::to_vec(&initial).unwrap()).unwrap();
    std::fs::write(session.directory().join("pilot-course-reviewer"),"").unwrap();
    let _=std::fs::remove_file("target/pilot-native-result.json");
    let mut command=std::process::Command::new(env!("CARGO_BIN_EXE_molip-quest"));
    native_player::configure(&session,&mut command,"auto-state");
    command.env("MOLIP_PILOT_SELF_TEST","auto-state");
    // MOLIP_AUTO_STATE_PART=rate|runs runs one half (quick red/green loop); unset runs both.
    let part=std::env::var("MOLIP_AUTO_STATE_PART").ok();
    if let Some(part)=&part {command.env("MOLIP_AUTO_STATE_PART",part);}
    let status=native_player::wait(&mut command.spawn().unwrap(),if part.is_some(){700}else{1300},"auto-state");
    let _=std::fs::copy(session.directory().join("auto-state.log"),"target/pilot-auto-state.log");
    let raw=std::fs::read_to_string("target/pilot-native-result.json").unwrap_or_else(|error|panic!("no result ({error}); exit {status:?}; log: {}",std::fs::read_to_string(session.directory().join("auto-state.log")).unwrap_or_default()));
    std::fs::write("target/pilot-auto-state.json",&raw).unwrap();
    let result:serde_json::Value=serde_json::from_str(&raw).unwrap();
    // Uploaded history: every pass the runs report is a real pass event; nothing was deleted.
    println!("{}",serde_json::to_string_pretty(&result).unwrap());
    let remote:serde_json::Value=serde_json::from_slice(&std::fs::read(session.directory().join("pilot-remote.json")).unwrap()).unwrap();
    let events:Vec<_>=remote["comments"].as_array().into_iter().flatten().flat_map(|c|issue_progress::parse_events(c["body"].as_str().unwrap())).collect();
    let passes=events.iter().filter(|e|e.passed&&matches!(e.kind,EventKind::Attempt)).count();
    std::fs::write("target/pilot-auto-state-remote-events.txt",events.iter().map(|e|format!("{:?} {} passed={} {}",e.kind,e.task_id.as_deref().unwrap_or("-"),e.passed,e.at)).collect::<Vec<_>>().join("\n")).unwrap();
    assert!(status.success()&&result["passed"]==true,"{result}");
    let reported:usize=result["report"]["runs"].as_array().into_iter().flatten().map(|r|r["passed"].as_array().map_or(0,Vec::len)).sum();
    assert!(passes>=reported,"uploaded passes {passes} < passes the runs reported {reported}");
}
