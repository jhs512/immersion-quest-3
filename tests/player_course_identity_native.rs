#![cfg(all(feature="desktop",debug_assertions))]
#[allow(dead_code)]
#[path="support/native_player.rs"] mod native_player;
#[test]
#[ignore="Requires an interactive native desktop"]
fn first_entry_requires_a_course_name_and_rename_updates_the_same_registration(){
    let session=molip_quest::pilot_session::PilotSession::new().unwrap();
    rusqlite::Connection::open(session.directory().join("course-names.sqlite3")).unwrap().execute("DELETE FROM names",[]).unwrap();
    let mut command=std::process::Command::new(env!("CARGO_BIN_EXE_molip-quest"));native_player::configure(&session,&mut command,"course-identity");command.env("MOLIP_PILOT_SELF_TEST","course-identity");
    let status=native_player::wait(&mut command.spawn().unwrap(),100,"course identity");
    let raw=std::fs::read_to_string("target/pilot-native-result.json").unwrap();let result:serde_json::Value=serde_json::from_str(&raw).unwrap();
    std::fs::write("target/pilot-course-identity-native-result.json",&raw).unwrap();assert!(status.success()&&result["passed"]==true,"{result}");
    let remote:serde_json::Value=serde_json::from_slice(&std::fs::read(session.directory().join("pilot-remote.json")).unwrap()).unwrap();
    assert_eq!(remote["enrollments"].as_array().unwrap().len(),1,"renaming must not create another issue");
    assert!(remote["enrollments"][0]["body"].as_str().unwrap().contains("[BE16]바꾼이름"));
    assert!(remote["comments"].as_array().unwrap().is_empty(),"name changes must not create progress comments");
}
