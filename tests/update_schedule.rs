use molip_quest::updater::UpdateSchedule;

#[test]
fn startup_five_minutes_and_manual_checks_do_not_overlap() {
    let mut schedule=UpdateSchedule::default();
    assert!(schedule.begin(0,false));
    assert!(!schedule.begin(1,true));
    schedule.finish();
    assert!(!schedule.begin(299,false));
    assert!(schedule.begin(300,false));
    schedule.finish();
    assert!(schedule.begin(301,true));
    schedule.finish();
    assert!(!schedule.begin(600,false));
    assert!(schedule.begin(601,false));
}

#[test]
fn a_notified_build_is_not_announced_again_after_process_state_is_reopened() {
    use molip_quest::updater::UpdateNotices;
    let root=tempfile::tempdir().unwrap();let path=root.path().join("notices.json");
    let mut first=UpdateNotices::open(&path).unwrap();
    assert!(first.record(42).unwrap());
    assert!(!first.record(42).unwrap());
    let mut reopened=UpdateNotices::open(&path).unwrap();
    assert!(!reopened.record(42).unwrap());
    assert!(reopened.record(43).unwrap());
}

#[test]
fn repository_answer_scope_survives_reopening_and_separates_accounts_courses_modes() {
    use molip_quest::{drafts::repository_scope,issue_progress::{ProgressKey,StudyMode}};
    let key=ProgressKey{user_id:1,course_id:"course".into(),lesson_id:"lesson".into()};
    let scope=repository_scope(&key,StudyMode::Full,"step");
    assert_eq!(scope,r#"repo-v2:[1,"course","lesson","full","step"]"#);
    assert_ne!(scope,repository_scope(&key,StudyMode::Review,"step"));
    assert_ne!(scope,repository_scope(&ProgressKey{user_id:2,..key.clone()},StudyMode::Full,"step"));
    assert_ne!(scope,repository_scope(&ProgressKey{course_id:"other".into(),..key.clone()},StudyMode::Full,"step"));
}
