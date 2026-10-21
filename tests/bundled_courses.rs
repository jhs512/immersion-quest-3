use molip_quest::{github_player::Github,content_updates::SnapshotStore,repository_course::CourseManifest};
use sha2::{Digest,Sha256};

#[test]
fn installation_and_upgrade_use_current_three_courses_without_content_downloads_or_lost_work(){
    // This integration binary owns its environment. Debug's mock transport rejects
    // every default-course download, so accidentally calling GitHub goes red.
    let directory=tempfile::tempdir().unwrap();
    if cfg!(debug_assertions){std::env::set_var("MOLIP_PILOT","1");}
    else{std::env::set_var("MOLIP_DATA_DIR",directory.path());}
    let github=Github::new();
    for (repository,count) in [
        ("jhs512/mq3-course-redesigned-java-backend",24),
        ("jhs512/mq3-course-redesigned-aice-associate",24),
        ("jhs512/mq3-course-redesigned-engineer-practical",30),
    ]{
        let course=github.installed_course(repository).expect("fresh installation must use the app's current course content");
        assert_eq!(course.lessons.len(),count);
        assert_eq!(github.course(repository).unwrap(),course);
        for reference in &course.lessons {
            assert_eq!(github.installed_lesson(&course,reference).unwrap(),github.lesson(reference).unwrap());
        }
        #[cfg(debug_assertions)]
        assert!(github.prepare_course(repository).is_err(),"update checks must try the remote even for bundled courses; this mock denies default-course downloads");
        let name=repository.strip_prefix("jhs512/mq3-course-redesigned-").unwrap();
        let legacy=std::fs::read_to_string(format!("tests/fixtures/published-course-baselines/{name}.json")).unwrap();
        let store=molip_quest::content_updates::installed_store().unwrap();
        for raw in [legacy.clone(),serde_json::to_string_pretty(&serde_json::from_str::<serde_json::Value>(&legacy).unwrap()).unwrap()] {
            let candidate=molip_quest::bundled_courses::prepare_update(&store,repository,&raw,|_|panic!("known old manifest must not download old lessons")).unwrap();
            assert_eq!(candidate.course(),&course,"known stale server snapshot cannot roll back bundled content");
        }
    }
    // Reproduce an already installed 18-lesson Java snapshot with changed content.
    let current=github.course("jhs512/mq3-course-redesigned-java-backend").unwrap();
    let mut old:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned-courses/java-backend.json")).unwrap();
    let removed=["bash-basics","vim-basics","java-launch","java-arguments","git-branch-advanced","github-pr"];
    old["lessons"].as_array_mut().unwrap().retain(|r|!removed.iter().any(|key|r["repository"].as_str().unwrap().ends_with(&format!("-{key}"))));
    let existing=current.lessons.iter().find(|r|r.revision=="java-values-1").unwrap();
    let mut outdated:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/java-values.json")).unwrap();
    outdated["tasks"][0]["starter_code"]="// old installed source".into();
    let outdated_raw=outdated.to_string();
    let reference=old["lessons"].as_array_mut().unwrap().iter_mut().find(|r|r["id"]==existing.id).unwrap();
    reference["sha256"]=format!("{:x}",Sha256::digest(outdated_raw.as_bytes())).into();
    let old_course=CourseManifest::parse(&old.to_string()).unwrap();assert_eq!(old_course.lessons.len(),18);
    let store=molip_quest::content_updates::installed_store().unwrap();
    let stale=store.prepare(&current.repository,&old.to_string(),|r|{
        if r.id==existing.id{return Ok(outdated_raw.clone())}
        Ok(molip_quest::lesson_registry::by_revision(&r.revision).unwrap().lesson.to_owned())
    }).unwrap();
    store.apply(&stale).unwrap();
    // Old app caches have no source marker. They must still migrate to the current bundle.
    let cache=molip_quest::data_dir().unwrap().join("content-snapshots").join(format!("{:x}.json",Sha256::digest(current.repository.as_bytes())));
    let mut legacy_cache:serde_json::Value=serde_json::from_slice(&std::fs::read(&cache).unwrap()).unwrap();
    legacy_cache.as_object_mut().unwrap().remove("remote");
    std::fs::write(&cache,serde_json::to_vec(&legacy_cache).unwrap()).unwrap();
    let key=molip_quest::issue_progress::ProgressKey{user_id:987654321,course_id:current.id.clone(),lesson_id:existing.id.clone()};
    let task_id=stale.lesson(&old_course.lessons.iter().find(|r|r.id==existing.id).unwrap()).unwrap().tasks[0].id.clone();
    let scope=molip_quest::drafts::repository_scope(&key,molip_quest::issue_progress::StudyMode::Full,&task_id);
    molip_quest::drafts::save(&scope,"learner's own code",&Default::default()).unwrap();
    let repaired=github.installed_course(&current.repository).unwrap();
    assert_eq!(repaired,current);assert_eq!(repaired.id,old_course.id);
    let active=store.active(&current.repository).unwrap().unwrap();
    assert_ne!(active.fingerprint(),stale.fingerprint());
    assert_ne!(active.lesson(existing).unwrap().tasks[0].starter_code,"// old installed source");
    assert_eq!(active.lesson(existing).unwrap().tasks[0].id,task_id,"progress resource codes must remain stable");
    assert_eq!(molip_quest::drafts::load(&scope).unwrap().unwrap().code,"learner's own code");
    assert_eq!(github.installed_course(&current.repository).unwrap(),repaired,"reopening must remain current");
    // A newly published remote manifest is authoritative and survives reopening/app upgrade.
    let mut updated:serde_json::Value=serde_json::from_str(molip_quest::bundled_courses::course_source(&current.repository).unwrap()).unwrap();
    updated["title"]="Remote updated course".into();
    let next=molip_quest::bundled_courses::prepare_update(&store,&current.repository,&updated.to_string(),|r|Ok(molip_quest::bundled_courses::lesson_source(r).unwrap().into())).unwrap();
    assert!(next.is_remote());store.apply(&next).unwrap();
    assert_eq!(github.installed_course(&current.repository).unwrap().title,"Remote updated course");
    assert_eq!(github.course(&current.repository).unwrap(),*next.course());
    let legacy=include_str!("fixtures/published-course-baselines/java-backend.json");
    assert_eq!(molip_quest::bundled_courses::prepare_update(&store,&current.repository,legacy,|_|panic!("old download")).unwrap().fingerprint(),next.fingerprint());
    updated["lessons"][0]["sha256"]="0".repeat(64).into();
    assert!(molip_quest::bundled_courses::prepare_update(&store,&current.repository,&updated.to_string(),|r|Ok(molip_quest::lesson_registry::by_revision(&r.revision).unwrap().lesson.into())).is_err());
    assert_eq!(store.active(&current.repository).unwrap().unwrap().fingerprint(),next.fingerprint());
    // The existing snapshot API and non-default courses remain separate.
    let other=SnapshotStore::new(directory.path().join("other"));
    assert!(other.active("teacher/extra-course").unwrap().is_none());
}
