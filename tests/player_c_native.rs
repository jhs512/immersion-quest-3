#![cfg(all(feature="desktop",debug_assertions))]
#[allow(dead_code)]
#[path="support/native_player.rs"] mod native_player;

#[test]
#[ignore="Requires an interactive desktop, a C compiler and the built player binary"]
fn approved_c_lesson_replays_from_canonical_state_and_preserves_edits() {
    let session=molip_quest::pilot_session::PilotSession::new().unwrap();
    let mut command=std::process::Command::new(env!("CARGO_BIN_EXE_molip-quest"));
    native_player::configure(&session,&mut command,"c");
    command.env("MOLIP_PILOT_SELF_TEST","engineer-c-start");
    let status=native_player::wait(&mut command.spawn().unwrap(),480,"approved C lesson");
    let raw=std::fs::read_to_string("target/pilot-native-result.json").unwrap();
    std::fs::write("target/pilot-c-result.json",&raw).unwrap();
    let result:serde_json::Value=serde_json::from_str(&raw).unwrap();
    assert!(status.success()&&result["passed"]==true,"{result}");
    assert_eq!(result["checked"].as_array().unwrap().len(),8,"Six steps and two modified-answer replays");
    let store:serde_json::Value=serde_json::from_slice(&std::fs::read(session.directory().join("pilot-remote.json")).unwrap()).unwrap();
    let events:Vec<_>=store["comments"].as_array().unwrap().iter().flat_map(|comment|molip_quest::issue_progress::parse_events(comment["body"].as_str().unwrap())).collect();
    use molip_quest::issue_progress::EventKind;
    let passed:std::collections::HashSet<_>=events.iter().filter(|event|event.kind==EventKind::Attempt&&event.passed).filter_map(|event|event.task_id.as_ref()).collect();
    assert_eq!(passed.len(),6);
    assert_eq!(events.iter().filter(|event|event.kind==EventKind::Completed).count(),1);
    assert!(!events.iter().any(|event|event.kind==EventKind::ExampleRun),"Teacher runs must not become student runs");
}
