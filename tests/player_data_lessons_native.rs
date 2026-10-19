#![cfg(all(feature="desktop",debug_assertions))]
#[allow(dead_code)]
#[path="support/native_player.rs"] mod native_player;

fn verify(mode:&str,count:usize) {
    let session=molip_quest::pilot_session::PilotSession::new().unwrap();
    let mut command=std::process::Command::new(env!("CARGO_BIN_EXE_molip-quest"));
    native_player::configure(&session,&mut command,mode);
    command.env("MOLIP_PILOT_SELF_TEST",mode);
    let status=native_player::wait(&mut command.spawn().unwrap(),480,mode);
    let raw=std::fs::read_to_string("target/pilot-native-result.json").unwrap();
    std::fs::write(format!("target/pilot-{mode}-result.json"),&raw).unwrap();
    let result:serde_json::Value=serde_json::from_str(&raw).unwrap();
    assert!(status.success()&&result["passed"]==true,"{result}");
    assert_eq!(result["checked"].as_array().unwrap().len(),count+3);
    let store:serde_json::Value=serde_json::from_slice(&std::fs::read(session.directory().join("pilot-remote.json")).unwrap()).unwrap();
    let events:Vec<_>=store["comments"].as_array().unwrap().iter().filter_map(|comment|molip_quest::issue_progress::parse_event(comment["body"].as_str().unwrap())).collect();
    use molip_quest::issue_progress::EventKind;
    let passed:std::collections::HashSet<_>=events.iter().filter(|event|event.kind==EventKind::Attempt&&event.passed).filter_map(|event|event.task_id.as_ref()).collect();
    assert_eq!(passed.len(),count);
    assert_eq!(events.iter().filter(|event|event.kind==EventKind::Completed).count(),1);
    assert!(!events.iter().any(|event|event.kind==EventKind::ExampleRun));
}

#[test]
#[ignore="Requires an interactive desktop, pandas and the built player"]
fn pandas_selection_and_summaries_restore_student_state() {verify("aice-selection",10)}

#[test]
#[ignore="Requires an interactive desktop, JDK25 and the built player"]
fn java_array_loops_restore_student_state() {verify("java-arrays",8)}
