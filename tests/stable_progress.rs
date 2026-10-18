use molip_quest::{issue_progress::*, repository_course::{CourseManifest, Lesson}};

fn pilot(version: &str) -> Lesson {
    let root = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("tests/fixtures/player-pilot").join(version);
    let course = CourseManifest::parse(&std::fs::read_to_string(root.join("course.json")).unwrap()).unwrap();
    Lesson::parse(&std::fs::read_to_string(root.join("lesson.json")).unwrap(), &course.lessons[0]).unwrap()
}
fn completed(lesson: &Lesson) -> Vec<LearningEvent> {
    let key=ProgressKey{user_id:42,course_id:"course-one".into(),lesson_id:lesson.id.clone()};
    let mut events=vec![];
    for id in lesson.required_tasks() {
        let mut event=LearningEvent::new(key.clone(),&lesson.revision,StudyMode::Full,"first",EventKind::Attempt);
        event.task_id=Some(id);event.passed=true;events.push(event);
    }
    let mut event=LearningEvent::new(key,&lesson.revision,StudyMode::Full,"first",EventKind::Completed);
    event.required=lesson.required_tasks();events.push(event);events
}

#[test]
fn stable_codes_preserve_success_after_rename_reorder_and_nonessential_revision() {
    let mut lesson=pilot("a");let events=completed(&lesson);
    lesson.revision="wording-fix".into();lesson.title="renamed".into();lesson.tasks.reverse();
    assert!(status(&events,&lesson.revision,&lesson.required_tasks()).current);
    assert_eq!(passed_for_study(&events,&lesson.revision,StudyMode::Full,"new").len(),2);
    assert!(passed_for_study(&events,&lesson.revision,StudyMode::Review,"new").is_empty());
}

#[test]
fn replacement_and_addition_preserve_old_completion_without_transferring_success() {
    let a=pilot("a");let b=pilot("b");let c=pilot("c");let mut events=completed(&a);
    for newer in [&b,&c] {
        let state=status(&events,&newer.revision,&newer.required_tasks());
        assert!(state.completed);assert!(!state.current);
    }
    let known=passed_for_study(&events,&c.revision,StudyMode::Full,"next");
    assert!(!known.contains(&c.tasks[1].id));
    let mut attempt=LearningEvent::new(events[0].key.clone(),&c.revision,StudyMode::Full,"next",EventKind::Attempt);
    attempt.task_id=Some(c.tasks[1].id.clone());attempt.passed=true;events.push(attempt);
    let mut done=LearningEvent::new(events[0].key.clone(),&c.revision,StudyMode::Full,"next",EventKind::Completed);
    done.required=c.required_tasks();events.push(done);
    let state=status(&events,&c.revision,&c.required_tasks());
    assert!(state.current);assert_eq!(state.full_completions,2);
}

#[test]
fn histories_are_idempotent_and_scoped_to_user_course_and_lesson() {
    let lesson=pilot("a");let events=completed(&lesson);let key=events[0].key.clone();
    for alternate in [ProgressKey{user_id:99,..key.clone()},ProgressKey{course_id:"other".into(),..key.clone()},ProgressKey{lesson_id:"other".into(),..key.clone()}] {
        let mut foreign=events.clone();for event in &mut foreign{event.key=alternate.clone();}
        assert_eq!(merge(events.clone().into_iter().chain(events.clone()).chain(foreign),&key).len(),events.len());
    }
}
