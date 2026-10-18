use molip_quest::content_updates::SnapshotStore;
use std::path::Path;
fn fixture(version:&str,file:&str)->String { std::fs::read_to_string(Path::new(env!("CARGO_MANIFEST_DIR")).join("tests/fixtures/player-pilot").join(version).join(file)).unwrap() }
#[test]
fn candidate_is_validated_in_full_before_replacing_active_content() {
    let root=tempfile::tempdir().unwrap();
    let store=SnapshotStore::new(root.path());
    let repo="mq3-validation/course";
    let a=store.prepare(repo,&fixture("a","course.json"),|_|Ok(fixture("a","lesson.json"))).unwrap();
    store.apply(&a).unwrap();
    assert_eq!(store.active(repo).unwrap().unwrap().course().lessons[0].revision,"pilot-a");
    assert!(store.prepare(repo,&fixture("b","course.json"),|_|Err("download failed".into())).is_err());
    assert!(store.prepare(repo,&fixture("b","course.json"),|_|Ok(fixture("a","lesson.json"))).is_err());
    assert_eq!(store.active(repo).unwrap().unwrap().course().lessons[0].revision,"pilot-a");
    let b=store.prepare(repo,&fixture("b","course.json"),|_|Ok(fixture("b","lesson.json"))).unwrap();
    assert_eq!(store.active(repo).unwrap().unwrap().course().lessons[0].revision,"pilot-a");
    store.apply(&b).unwrap();
    let reopened=SnapshotStore::new(root.path());
    let active=reopened.active(repo).unwrap().unwrap();
    assert_eq!(active.course().lessons[0].revision,"pilot-b");
    assert_eq!(active.lesson(&active.course().lessons[0]).unwrap().tasks.len(),3);
}

#[test]
fn additions_are_distinct_from_title_revision_and_order_changes() {
    let root=tempfile::tempdir().unwrap(); let store=SnapshotStore::new(root.path()); let repo="mq3-validation/course";
    let a=store.prepare(repo,&fixture("a","course.json"),|_|Ok(fixture("a","lesson.json"))).unwrap();
    let e=store.prepare(repo,&fixture("e","course.json"),|_|Ok(fixture("e","lesson.json"))).unwrap();
    let b=store.prepare(repo,&fixture("b","course.json"),|_|Ok(fixture("b","lesson.json"))).unwrap();
    let renamed=e.changes_from(&a);
    assert!(renamed.added.is_empty()); assert!(renamed.removed.is_empty());
    assert!(renamed.modified.is_empty());
    let added=b.changes_from(&a);
    assert_eq!(added.added,vec!["stp_3f59e7bd-70c1-4e81-9cb0-000000000007"]);
    assert!(added.removed.is_empty());
    assert!(added.modified.is_empty());
}

#[test]
fn update_backup_keeps_retired_answers_and_isolates_accounts_and_courses() {
    std::env::set_var("MOLIP_PILOT","1");
    use molip_quest::{drafts,issue_progress::{ProgressKey,StudyMode}};
    let key=ProgressKey{user_id:10,course_id:"course-one".into(),lesson_id:"lesson-one".into()};
    let scope=drafts::repository_scope(&key,StudyMode::Full,"old-step");
    drafts::save(&scope,"student original",&Default::default()).unwrap();
    drafts::backup_repository(10,"course-one","snapshot-a").unwrap();
    drafts::save(&scope,"new work",&Default::default()).unwrap();
    let backup=drafts::repository_backups(10,"course-one").unwrap();
    assert_eq!(backup.len(),1);assert_eq!(backup[0].draft.code,"student original");
    assert_eq!(backup[0].step_id,"old-step");
    assert_eq!(drafts::load(&scope).unwrap().unwrap().code,"new work");
    assert!(drafts::repository_backups(11,"course-one").unwrap().is_empty());
    assert!(drafts::repository_backups(10,"course-two").unwrap().is_empty());
}

#[test]
fn bad_later_reference_or_changed_course_identity_cannot_replace_a_valid_course() {
    let root=tempfile::tempdir().unwrap();let store=SnapshotStore::new(root.path());let repo="mq3-validation/course";
    let a=store.prepare(repo,&fixture("a","course.json"),|_|Ok(fixture("a","lesson.json"))).unwrap();store.apply(&a).unwrap();
    let mut course:serde_json::Value=serde_json::from_str(&fixture("b","course.json")).unwrap();
    let mut second=course["lessons"][0].clone();second["id"]="lsn_3f59e7bd-70c1-4e81-9cb0-000000000099".into();
    course["lessons"].as_array_mut().unwrap().push(second);
    let failed=store.prepare(repo,&course.to_string(),|reference|if reference.id.ends_with("99"){Err("reference missing".into())}else{Ok(fixture("b","lesson.json"))});
    assert!(failed.is_err()); assert_eq!(store.active(repo).unwrap().unwrap().fingerprint(),a.fingerprint());
    course["lessons"].as_array_mut().unwrap().pop();course["id"]="crs_3f59e7bd-70c1-4e81-9cb0-000000000098".into();
    let foreign=store.prepare(repo,&course.to_string(),|_|Ok(fixture("b","lesson.json"))).unwrap();
    assert!(store.apply(&foreign).is_err());assert_eq!(store.active(repo).unwrap().unwrap().fingerprint(),a.fingerprint());
    assert!(store.prepare("different/course",&fixture("a","course.json"),|_|Ok(fixture("a","lesson.json"))).is_err());
}
