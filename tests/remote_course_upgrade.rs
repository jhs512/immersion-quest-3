use molip_quest::{bundled_courses, content_lifecycle, content_updates, drafts,
    github_player::Github, issue_progress::{ProgressKey, StudyMode}};

#[test]
fn remote_course_without_rust_survives_app_upgrade_then_refreshes_without_losing_answers() {
    let profile = tempfile::tempdir().unwrap();
    std::env::set_var("MOLIP_DATA_DIR", profile.path());
    std::env::remove_var("MOLIP_PILOT");
    let repository = bundled_courses::REPOSITORIES[0];
    let store = content_updates::installed_store().unwrap();
    let current = bundled_courses::prepare(&store, repository).unwrap().unwrap();
    let mut old: serde_json::Value = serde_json::from_str(bundled_courses::course_source(repository).unwrap()).unwrap();
    let rust: std::collections::HashSet<String> = current.course().lessons.iter()
        .filter(|reference| reference.revision.starts_with("rust-"))
        .map(|reference| reference.id.clone()).collect();
    assert_eq!(rust.len(), 4);
    old["lessons"].as_array_mut().unwrap().retain(|reference| !rust.contains(reference["id"].as_str().unwrap()));
    old["lesson_previews"].as_object_mut().unwrap().retain(|id, _| !rust.contains(id));
    let stale = store.prepare(repository, &old.to_string(), |reference|
        Ok(bundled_courses::lesson_source(reference).unwrap().into())).unwrap();
    assert!(stale.is_remote());
    store.apply(&stale).unwrap();
    let reference = &stale.course().lessons[4];
    let key = ProgressKey {user_id: 987654321, course_id: stale.course().id.clone(), lesson_id: reference.id.clone()};
    let scope = drafts::repository_scope(&key, StudyMode::Full, "unfinished-task");
    drafts::save(&scope, "learner answer", &Default::default()).unwrap();
    let github = Github::new();
    assert_eq!(github.installed_course(repository).unwrap(), *stale.course());
    assert!(content_lifecycle::refresh_course(&store, repository, || Err("offline".into()),
        |_| panic!("failed download must not back up or replace content")).is_err());
    assert_eq!(store.active(repository).unwrap().unwrap(), stale);
    assert!(content_lifecycle::refresh_course(&store, repository, || Ok(current.clone()),
        |next| drafts::backup_repository(key.user_id, &key.course_id, &next.fingerprint())).unwrap());
    let reopened = github.installed_course(repository).unwrap();
    assert_eq!(reopened.lessons.len(), stale.course().lessons.len() + 4);
    let launch = reopened.lessons.iter().position(|r| r.revision.starts_with("java-launch-")).unwrap();
    assert!(reopened.lessons[launch + 1..launch + 5].iter().all(|r| r.revision.starts_with("rust-")));
    assert_eq!(reopened.lessons.iter().find(|r| r.id == key.lesson_id).unwrap().revision, reference.revision);
    assert_eq!(drafts::load(&scope).unwrap().unwrap().code, "learner answer");
    assert_eq!(drafts::repository_backups(key.user_id, &key.course_id).unwrap().len(), 1);
}
