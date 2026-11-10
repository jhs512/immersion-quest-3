#![cfg(all(feature="desktop",debug_assertions))]
#[allow(dead_code)]
#[path="support/native_player.rs"] mod native_player;

/// The first cloud lesson in the real debug player: editor tabs, learner edits and commands graded by
/// the owned local cloud API, the teacher in its own runtime, and 초기화, for every step.
#[test]
#[ignore="Requires an interactive desktop, Docker Desktop Linux engine and the built player; runs privileged Docker-in-Docker guests"]
fn cloud_lesson_steps_grade_teach_and_reset_in_the_player() {
    let mode="cloud-vpc-subnet-ec2";
    let session=molip_quest::pilot_session::PilotSession::new().unwrap();
    let mut command=std::process::Command::new(env!("CARGO_BIN_EXE_molip-quest"));
    native_player::configure(&session,&mut command,mode);
    command.env("MOLIP_PILOT_SELF_TEST",mode);
    let status=native_player::wait(&mut command.spawn().unwrap(),5700,mode);
    let raw=std::fs::read_to_string("target/pilot-native-result.json").unwrap();
    std::fs::write(format!("target/pilot-{mode}-result.json"),&raw).unwrap();
    let result:serde_json::Value=serde_json::from_str(&raw).unwrap();
    assert!(status.success()&&result["passed"]==true,"{result}");
    assert_eq!(result["checked"].as_array().unwrap().len(),7,"{result}");
    let store:serde_json::Value=serde_json::from_slice(&std::fs::read(session.directory().join("pilot-remote.json")).unwrap()).unwrap();
    let events:Vec<_>=store["comments"].as_array().unwrap().iter().flat_map(|comment|molip_quest::issue_progress::parse_events(comment["body"].as_str().unwrap())).collect();
    use molip_quest::issue_progress::EventKind;
    let passed:std::collections::HashSet<_>=events.iter().filter(|event|event.kind==EventKind::Attempt&&event.passed).filter_map(|event|event.task_id.as_ref()).collect();
    assert_eq!(passed.len(),7);
    assert_eq!(events.iter().filter(|event|event.kind==EventKind::Completed).count(),1);
}
