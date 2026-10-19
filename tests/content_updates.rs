use molip_quest::content_updates::SnapshotStore;
use std::path::Path;
fn fixture(version:&str,file:&str)->String { std::fs::read_to_string(Path::new(env!("CARGO_MANIFEST_DIR")).join("tests/fixtures/player-pilot").join(version).join(file)).unwrap() }
#[test]
fn duplicate_child_codes_across_lessons_cannot_replace_installed_content() {
    use sha2::{Digest,Sha256};
    let root=tempfile::tempdir().unwrap(); let store=SnapshotStore::new(root.path());
    let repo="mq3-validation/course";
    let original=store.prepare(repo,&fixture("a","course.json"),|_|Ok(fixture("a","lesson.json"))).unwrap();
    store.apply(&original).unwrap();
    // Each lesson is valid on its own. Only the complete candidate reveals the collision.
    for duplicate_kind in ["chapter","unit","step"] {
        let mut course:serde_json::Value=serde_json::from_str(&fixture("a","course.json")).unwrap();
        let mut copy:serde_json::Value=serde_json::from_str(&fixture("a","lesson.json")).unwrap();
        let new_id="lsn_3f59e7bd-70c1-4e81-9cb0-000000000099";
        copy["id"]=new_id.into();
        if duplicate_kind!="chapter" { copy["chapters"][0]["id"]="chp_3f59e7bd-70c1-4e81-9cb0-000000000097".into(); }
        if duplicate_kind=="step" { copy["chapters"][0]["units"][0]["id"]="unt_3f59e7bd-70c1-4e81-9cb0-000000000096".into(); }
        let document=copy.to_string();
        let mut reference=course["lessons"][0].clone(); reference["id"]=new_id.into();
        reference["sha256"]=format!("{:x}",Sha256::digest(document.as_bytes())).into();
        let parsed_reference=serde_json::from_value(reference.clone()).unwrap();
        molip_quest::repository_course::Lesson::parse(&document,&parsed_reference).unwrap();
        course["lessons"].as_array_mut().unwrap().push(reference);
        let result=store.prepare(repo,&course.to_string(),|r|Ok(if r.id==new_id {document.clone()} else {fixture("a","lesson.json")}));
        assert!(result.is_err(),"duplicate {duplicate_kind} accepted across lessons");
        assert_eq!(store.active(repo).unwrap().unwrap().fingerprint(),original.fingerprint());
    }
}
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
    // A failed application can be retried after editing the live draft.
    drafts::backup_repository(10,"course-one","snapshot-a").unwrap();
    let retried=drafts::repository_backups(10,"course-one").unwrap();
    assert_eq!(retried[0].draft.code,"new work");
    assert_eq!(retried.len(),2);
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

#[test]
fn installed_catalog_requirements_survive_a_corrupt_remote_candidate() {
    std::env::set_var("MOLIP_PILOT","1");
    use molip_quest::{github_player::Github,pilot_source,issue_progress::{ProgressKey,StudyMode,LearningEvent,EventKind}};
    pilot_source::set_version('a').unwrap();
    let gh=Github::new();let user=gh.user().unwrap();
    let course=gh.installed_course(pilot_source::REPOSITORY).unwrap();
    let key=ProgressKey{user_id:user.id,course_id:course.id.clone(),lesson_id:course.lessons[0].id.clone()};
    let completed=LearningEvent::new(key,"pilot-a",StudyMode::Full,"catalog-test",EventKind::Completed);
    gh.append(&course.repository,&user,"test",&completed).unwrap();
    pilot_source::corrupt_update().unwrap();
    assert!(gh.prepare_course(&course.repository).is_err());
    let progress=gh.course_progress(&course,&user).unwrap();
    assert_eq!(progress.required[&course.lessons[0].id].len(),2);
}

#[test]
fn legacy_resource_ids_with_colons_keep_distinct_lesson_and_step_identity() {
    use sha2::{Digest,Sha256};
    let root=tempfile::tempdir().unwrap();let store=SnapshotStore::new(root.path());let repo="mq3-validation/course";
    let mut course:serde_json::Value=serde_json::from_str(&fixture("a","course.json")).unwrap();
    course["schema_version"]=1.into();let template=course["lessons"][0].clone();course["lessons"]=serde_json::json!([]);
    let mut documents=std::collections::BTreeMap::new();
    for (lesson_id,step_id) in [("a:b","c"),("a","b:c")] {
        let mut lesson:serde_json::Value=serde_json::from_str(&fixture("a","lesson.json")).unwrap();
        lesson["schema_version"]=1.into();lesson["id"]=lesson_id.into();lesson["revision"]="v1".into();
        lesson["tasks"].as_array_mut().unwrap().truncate(1);lesson["tasks"][0]["id"]=step_id.into();
        let raw=lesson.to_string();let mut reference=template.clone();reference["id"]=lesson_id.into();reference["revision"]="v1".into();reference["sha256"]=format!("{:x}",Sha256::digest(raw.as_bytes())).into();
        course["lessons"].as_array_mut().unwrap().push(reference);documents.insert(lesson_id.to_string(),raw);
    }
    let before=store.prepare(repo,&course.to_string(),|reference|Ok(documents[&reference.id].clone())).unwrap();
    course["lessons"].as_array_mut().unwrap().remove(0);
    let after=store.prepare(repo,&course.to_string(),|reference|Ok(documents[&reference.id].clone())).unwrap();
    let changes=after.changes_from(&before);
    assert_eq!(changes.removed,vec!["c"]);assert!(changes.modified.is_empty());assert!(changes.added.is_empty());
}
