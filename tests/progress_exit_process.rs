#![cfg(all(feature="desktop",debug_assertions))]
use molip_quest::{github_player::GithubUser,issue_progress::{LearningEvent,ProgressKey,StudyMode,EventKind},progress_sync::ProgressStore};
#[test]
fn exit_helper_runs_without_a_window_and_persists_the_ten_exit_budget(){
    let session=molip_quest::pilot_session::PilotSession::new().unwrap();
    let store=ProgressStore::new(&session.directory().join("progress-events.sqlite3"));
    let user=GithubUser{id:987654321,login:"mq3-validation".into()};
    let key=ProgressKey{user_id:user.id,course_id:"crs_3f59e7bd-70c1-4e81-9cb0-000000000001".into(),lesson_id:"lesson".into()};
    for attempt in 0..11 {
        let mut event=LearningEvent::new(key.clone(),"v1",StudyMode::Full,"round",EventKind::Attempt);event.passed=true;event.task_id=Some(format!("task-{attempt}"));
        store.record("mq3-validation/course",&user,"Lesson",&event,&[]).unwrap();
        let mut cmd=std::process::Command::new(env!("CARGO_BIN_EXE_molip-quest"));session.configure(&mut cmd);cmd.arg("--flush-progress-on-exit");
        assert!(cmd.status().unwrap().success());
        assert_eq!(store.pending_count(user.id).unwrap(),if attempt<10{0}else{1});
    }
    let remote:serde_json::Value=serde_json::from_slice(&std::fs::read(session.directory().join("pilot-remote.json")).unwrap()).unwrap();
    assert_eq!(remote["comments"].as_array().unwrap().len(),10);
}
