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
    for id in lesson.required_tasks() {
        let mut passed=LearningEvent::new(key.clone(),&lesson.revision,StudyMode::Full,"completion",EventKind::Attempt);
        passed.task_id=Some(id);passed.passed=true;
        github.append(&course.repository,&user,&lesson.title,&passed).unwrap();
    }
    let mut done=LearningEvent::new(key.clone(),&lesson.revision,StudyMode::Full,"completion",EventKind::Completed);
    done.required=lesson.required_tasks();github.append(&course.repository,&user,&lesson.title,&done).unwrap();
    let catalog=github.course_progress(&changed,&user).unwrap();
    assert_eq!(catalog.required[&lesson.id],replacement.required_tasks());
    assert!(!molip_quest::issue_progress::status(&catalog.events[&lesson.id],&replacement.revision,&catalog.required[&lesson.id]).current);
    pilot_source::set_version('e').unwrap();
    let wording=github.course(pilot_source::REPOSITORY).unwrap();
    let catalog=github.course_progress(&wording,&user).unwrap();
    assert!(molip_quest::issue_progress::status(&catalog.events[&lesson.id],&wording.lessons[0].revision,&catalog.required[&lesson.id]).current);
    pilot_source::set_version('j').unwrap();
    let visual_course = github.course(pilot_source::REPOSITORY).unwrap();
    let visual_lesson = github.lesson(&visual_course.lessons[0]).unwrap();
    assert_eq!(visual_lesson.tasks[0].supporting_materials.len(), 4);
    assert_eq!(visual_lesson.required_tasks(), lesson.required_tasks());
    // Long lessons must cross a real 100-comment page without duplicating page one.
    let before = github.events(&course.repository, &issue, &key).unwrap().len();
    for _ in 0..105 {
        let event = LearningEvent::new(key.clone(), &lesson.revision, StudyMode::Full,
                                      "long-lesson", EventKind::Viewed);
        github.append(&course.repository, &user, &lesson.title, &event).unwrap();
    }
    let after = github.events(&course.repository, &issue, &key).unwrap();
    assert_eq!(after.len(), before + 105);

    let batch=(0..3).map(|_|LearningEvent::new(key.clone(),&lesson.revision,StudyMode::Full,"hourly",EventKind::Viewed)).collect::<Vec<_>>();
    let raw=std::fs::read(pilot_source::data_dir().unwrap().join("pilot-remote.json")).unwrap();
    let before_comments=serde_json::from_slice::<serde_json::Value>(&raw).unwrap()["comments"].as_array().unwrap().len();
    let (_,remote)=github.append_batch(&course.repository,&user,&lesson.title,&batch).unwrap();
    assert!(batch.iter().all(|event|remote.contains(event)));
    github.append_batch(&course.repository,&user,&lesson.title,&batch).unwrap();
    let raw=std::fs::read(pilot_source::data_dir().unwrap().join("pilot-remote.json")).unwrap();
    let comments=serde_json::from_slice::<serde_json::Value>(&raw).unwrap();
    assert_eq!(comments["comments"].as_array().unwrap().len(),before_comments+1,"whole batch posts once; lost-response retry must not duplicate it");

}
