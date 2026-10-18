use molip_quest::{github_player::Github, issue_progress::{EventKind, LearningEvent, ProgressKey, StudyMode}, pilot_source};

#[test]
fn production_github_loading_and_progress_use_only_the_isolated_pilot_store() {
    std::env::set_var("MOLIP_PILOT", "1");
    let github = Github::new();
    let user = github.user().unwrap();
    assert_eq!(user.login, "mq3-validation");
    let course = github.course(pilot_source::REPOSITORY).unwrap();
    let lesson = github.lesson(&course.lessons[0]).unwrap();
    assert_eq!(lesson.schema_version, 2);
    assert!(github.course("jhs512/mq3-course-java-backend").is_err());
    let key = ProgressKey { user_id: user.id, course_id: course.id.clone(), lesson_id: lesson.id.clone() };
    let event = LearningEvent::new(key.clone(), &lesson.revision, StudyMode::Full, "pilot-round", EventKind::Started);
    let (issue, events) = github.append(&course.repository, &user, &lesson.title, &event).unwrap();
    assert_eq!(events.len(), 1);
    let (_, again) = github.append(&course.repository, &user, &lesson.title, &event).unwrap();
    assert_eq!(again.len(), 1);
    assert_eq!(github.events(&course.repository, &issue, &key).unwrap().len(), 1);
    assert!(molip_quest::data_dir().unwrap().to_string_lossy().contains("mq3-player-pilot"));
    pilot_source::set_version('c').unwrap();
    let changed = github.course(pilot_source::REPOSITORY).unwrap();
    assert_eq!(changed.id, course.id);
    let replacement = github.lesson(&changed.lessons[0]).unwrap();
    assert_ne!(replacement.tasks[1].id, lesson.tasks[1].id);
    assert!(github.events(&course.repository, &issue, &key).unwrap().iter().any(|old| old.revision == "pilot-a"));
}
