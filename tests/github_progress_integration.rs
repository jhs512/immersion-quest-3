use molip_quest::{github_player::Github,issue_progress::*,repository_course};

#[test]
#[ignore = "Creates clearly marked verification progress in the public course repository"]
fn gh_identity_pinned_content_and_public_issue_round_trip() {
    let github=Github::new();let user=github.user().unwrap();
    assert_eq!(user.login,"jhs512");
    assert!(github.ensure_user(user.id+1).is_err());
    let course=github.course(repository_course::COURSE_REPOSITORY).unwrap();
    let installed = tempfile::tempdir().unwrap();
    let store = molip_quest::content_updates::SnapshotStore::new(installed.path());
    let mut unique_steps = std::collections::HashSet::new();
    for raw in [
        include_str!("../courses/redesigned-courses/java-backend.json"),
        include_str!("../courses/redesigned-courses/aice-associate.json"),
        include_str!("../courses/redesigned-courses/engineer-practical.json"),
    ] {
        let expected = repository_course::CourseManifest::parse(raw).unwrap();
        let remote = github.course(&expected.repository).unwrap();
        assert_eq!(remote.id, expected.id);
        assert_eq!(remote.lessons.len(), expected.lessons.len());
        let mut documents = std::collections::HashMap::new();
        for (reference, approved) in remote.lessons.iter().zip(&expected.lessons) {
            assert_eq!(reference.id, approved.id);
            assert_eq!(reference.repository, approved.repository);
            assert_eq!(reference.revision, approved.revision);
            assert_eq!(reference.sha256, approved.sha256);
            // This verifies the actual immutable GitHub content through the app loader.
            let document = github.content(&reference.repository, &reference.revision, "lesson.json").unwrap();
            let lesson = repository_course::Lesson::parse(&document, reference).unwrap();
            for step in &lesson.tasks {assert!(unique_steps.insert(step.id.clone()));}
            documents.insert(reference.id.clone(), document);
        }
        let prepared = store.prepare(&expected.repository, raw,
            |reference| Ok(documents[&reference.id].clone())).unwrap();
        store.apply(&prepared).unwrap();
        assert!(store.active(&expected.repository).unwrap().is_some());
    }
    assert_eq!(unique_steps.len(), 689);
    // A distinct course/lesson key keeps this smoke test out of real learner progress.
    let key=ProgressKey{user_id:user.id,course_id:"mq3-verification".into(),lesson_id:"progress-protocol".into()};
    let round=new_id();
    let started=LearningEvent::new(key.clone(),"v1.0.0",StudyMode::Review,&round,EventKind::Started);
    let (issue,_)=github.append(&course.repository,&user,"[시스템 검증] 진도 프로토콜",&started).unwrap();
    let mut attempt=LearningEvent::new(key.clone(),"v1.0.0",StudyMode::Review,&round,EventKind::Attempt);
    attempt.task_id=Some("contract-check".into());attempt.passed=true;
    github.append(&course.repository,&user,"[시스템 검증] 진도 프로토콜",&attempt).unwrap();
    let (_,events)=github.append(&course.repository,&user,"[시스템 검증] 진도 프로토콜",&attempt).unwrap();
    assert_eq!(events.iter().filter(|e|e.id==attempt.id).count(),1);
    let mut done=LearningEvent::new(key,"v1.0.0",StudyMode::Review,&round,EventKind::Completed);done.required=vec!["contract-check".into()];
    let (_,events)=github.append(&course.repository,&user,"[시스템 검증] 진도 프로토콜",&done).unwrap();
    assert!(status(&events,"v1.0.0",&done.required).current);
    assert!(!status(&events,"v2.0.0",&done.required).current);
    assert!(status(&events,"v2.0.0",&done.required).completed);
    eprintln!("verified issue {}",issue.html_url);
    let mut cmd=std::process::Command::new("gh");
    cmd.args(["issue","close",&issue.number.to_string(),"--repo",&course.repository,"--reason","completed"]);
    assert!(cmd.output().unwrap().status.success());
}
