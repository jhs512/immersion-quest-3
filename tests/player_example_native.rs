#![cfg(all(feature="desktop",debug_assertions))]
#[allow(dead_code)]
#[path="support/native_player.rs"] mod native_player;

#[test]
#[ignore="Requires an interactive desktop and the built player binary"]
fn actual_player_keeps_predictions_separate_from_attempts_and_teacher_runs() {
    let session=molip_quest::pilot_session::PilotSession::new().unwrap();
    let mut command=std::process::Command::new(env!("CARGO_BIN_EXE_molip-quest"));
    native_player::configure(&session,&mut command,"examples");
    command.env("MOLIP_PILOT_SELF_TEST","interaction-example");
    let status=native_player::wait(&mut command.spawn().unwrap(),120,"prepared examples");
    let raw=std::fs::read_to_string("target/pilot-native-result.json").unwrap();
    std::fs::write("target/pilot-example-result.json",&raw).unwrap();
    let result:serde_json::Value=serde_json::from_str(&raw).unwrap();
    assert!(status.success()&&result["passed"]==true,"{result}");
    let store:serde_json::Value=serde_json::from_slice(&std::fs::read(session.directory().join("pilot-remote.json")).unwrap()).unwrap();
    let events:Vec<_>=store["comments"].as_array().unwrap().iter().filter_map(|comment|molip_quest::issue_progress::parse_event(comment["body"].as_str().unwrap())).collect();
    let predicted:Vec<_>=events.iter().filter(|event|event.prediction.is_some()).collect();
    assert_eq!(predicted.len(),1,"Teacher runs must not write learner predictions");
    assert_eq!(predicted[0].prediction.as_deref(),Some("five"));
    assert_eq!(predicted[0].kind,molip_quest::issue_progress::EventKind::ExampleRun);
    assert!(!predicted[0].passed);
    assert!(events.iter().any(|event|event.kind==molip_quest::issue_progress::EventKind::Attempt&&event.passed&&event.task_id==predicted[0].task_id));
}
