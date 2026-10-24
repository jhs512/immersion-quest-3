#![cfg(all(feature="desktop",debug_assertions))]
#[allow(dead_code)]
#[path="support/native_player.rs"] mod native_player;
#[test]
#[ignore="Requires an interactive desktop"]
fn clearing_does_not_wait_for_github_and_next_clear_retries_retained_history(){
    let session=molip_quest::pilot_session::PilotSession::new().unwrap();
    std::fs::write(session.directory().join("pilot-progress-blocked"),"").unwrap();
    let mut command=std::process::Command::new(env!("CARGO_BIN_EXE_molip-quest"));
    native_player::configure(&session,&mut command,"async-progress");command.env("MOLIP_PILOT_SELF_TEST","async-progress");
    let status=native_player::wait(&mut command.spawn().unwrap(),100,"async-progress");
    let raw=std::fs::read_to_string("target/pilot-native-result.json").unwrap();std::fs::write("target/pilot-async-progress-result.json",&raw).unwrap();
    let result:serde_json::Value=serde_json::from_str(&raw).unwrap();assert!(status.success()&&result["passed"]==true,"{result}");assert_eq!(result["checked"].as_array().unwrap().len(),6);
    let remote:serde_json::Value=serde_json::from_slice(&std::fs::read(session.directory().join("pilot-remote.json")).unwrap()).unwrap();
    let events=remote["comments"].as_array().unwrap().iter().flat_map(|c|molip_quest::issue_progress::parse_events(c["body"].as_str().unwrap())).collect::<Vec<_>>();
    assert_eq!(events.iter().filter(|e|e.kind==molip_quest::issue_progress::EventKind::Attempt&&e.passed).count(),2);
    assert_eq!(events.iter().filter(|e|e.kind==molip_quest::issue_progress::EventKind::Completed).count(),1);
    for passed in events.iter().filter(|e|e.kind==molip_quest::issue_progress::EventKind::Attempt&&e.passed) {
        assert!(events.iter().any(|start|start.kind==molip_quest::issue_progress::EventKind::Started&&start.task_id==passed.task_id&&start.key==passed.key&&start.at<=passed.at),"problem start must reach the durable outbox before its success");
    }
}
