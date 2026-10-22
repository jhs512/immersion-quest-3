#![cfg(all(feature="desktop",debug_assertions))]
#[allow(dead_code)]
#[path="support/native_player.rs"] mod native_player;
#[test]
#[ignore="Requires an interactive desktop"]
fn actual_course_guide_reads_goals_narrates_and_refreshes_without_learning_events() {
    let session=molip_quest::pilot_session::PilotSession::new().unwrap();
    let mut command=std::process::Command::new(env!("CARGO_BIN_EXE_molip-quest"));
    native_player::configure(&session,&mut command,"course-guide");command.env("MOLIP_PILOT_SELF_TEST","course-guide");
    let status=native_player::wait(&mut command.spawn().unwrap(),120,"course-guide");
    let raw=std::fs::read_to_string("target/pilot-native-result.json").unwrap();std::fs::write("target/pilot-course-guide-result.json",&raw).unwrap();
    let result:serde_json::Value=serde_json::from_str(&raw).unwrap();assert!(status.success()&&result["passed"]==true,"{result}");
    assert_eq!(result["checked"].as_array().unwrap().len(),5);
    let remote:serde_json::Value=serde_json::from_slice(&std::fs::read(session.directory().join("pilot-remote.json")).unwrap()).unwrap();
    assert!(remote["comments"].as_array().unwrap().is_empty(),"reading or narrating the guide must not create progress");
}
