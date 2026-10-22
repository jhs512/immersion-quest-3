#![cfg(all(feature="desktop",debug_assertions))]
#[allow(dead_code)]
#[path="support/native_player.rs"] mod native_player;
#[test]
#[ignore="Requires an interactive native desktop; does not create hosted repositories"]
fn restructured_git_lessons_render_and_pr_explanation_preserves_the_student_workspace(){
    let session=molip_quest::pilot_session::PilotSession::new().unwrap();
    let mut command=std::process::Command::new(env!("CARGO_BIN_EXE_molip-quest"));
    native_player::configure(&session,&mut command,"git-course");command.env("MOLIP_PILOT_SELF_TEST","git-course");
    let status=native_player::wait(&mut command.spawn().unwrap(),180,"git-course");
    let result:serde_json::Value=serde_json::from_str(&std::fs::read_to_string("target/pilot-native-result.json").unwrap()).unwrap();
    std::fs::copy("target/pilot-native-result.json","target/pilot-git-course-native-result.json").unwrap();
    assert!(status.success()&&result["passed"]==true,"{result}");assert_eq!(result["checked"].as_array().unwrap().len(),7);
}
