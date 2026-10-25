use molip_quest::{lesson_runner, repository_course::{CourseManifest, Lesson}};
use serde_json::json;

fn root() -> std::path::PathBuf { env!("CARGO_MANIFEST_DIR").into() }
fn course() -> CourseManifest {
    CourseManifest::parse(&std::fs::read_to_string(root().join("courses/redesigned-courses/java-backend.json")).unwrap()).unwrap()
}

#[test]
fn previews_are_ungraded_metadata_and_old_courses_still_open() {
    let course = course();
    assert_eq!(course.lessons.len(), 34);
    assert_eq!(course.lesson_previews.len(), 34);
    assert_eq!(course.lessons.iter().filter(|l| l.required).count(), 26);
    assert!(course.lessons[..26].iter().all(|l| l.track == "basic"));
    assert!(course.lessons.iter().all(|l| !l.category.is_empty()));
    let mut old = serde_json::to_value(&course).unwrap();
    old.as_object_mut().unwrap().remove("lesson_previews");
    assert!(CourseManifest::parse(&old.to_string()).unwrap().lesson_previews.is_empty());
    let mut invalid = old.clone();
    invalid["lesson_previews"] = json!({"unknown": serde_json::to_value(course.lesson_previews.values().next().unwrap()).unwrap()});
    assert!(CourseManifest::parse(&invalid.to_string()).is_err());
    let mut invalid = serde_json::to_value(&course).unwrap();
    invalid["lesson_previews"][&course.lessons[0].id]["scenario"] = json!([]);
    assert!(CourseManifest::parse(&invalid.to_string()).is_err());
}

#[test]
fn adding_bridges_preserves_old_final_achievement_without_granting_new_answers() {
    use molip_quest::issue_progress::{self, EventKind, LearningEvent, ProgressKey, StudyMode};
    let course = course();
    for reference in &course.lessons[26..] {
        let key = reference.repository.strip_prefix("jhs512/mq3-lesson-redesigned-").unwrap();
        let lesson:Lesson=serde_json::from_str(&std::fs::read_to_string(root().join(format!("courses/redesigned/{key}.json"))).unwrap()).unwrap();
        let final_id=lesson.tasks.last().unwrap().id.clone();
        let progress_key=ProgressKey{user_id:1,course_id:course.id.clone(),lesson_id:lesson.id.clone()};
        let mut passed=LearningEvent::new(progress_key.clone(),&format!("{key}-1"),StudyMode::Full,"old",EventKind::Attempt);
        passed.task_id=Some(final_id.clone());passed.passed=true;
        let mut completed=LearningEvent::new(progress_key,&format!("{key}-1"),StudyMode::Full,"old",EventKind::Completed);
        completed.required=vec![final_id.clone()];
        let events=vec![passed,completed];
        assert_eq!(issue_progress::learned_tasks(&events,&lesson.revision),[final_id].into_iter().collect());
        let status=issue_progress::status(&events,&lesson.revision,&lesson.required_tasks());
        assert!(status.completed && !status.current, "old completion remains; new bridges await real solves");
        assert_eq!(status.full_completions,1);
    }
}

#[tokio::test]
async fn every_new_bridge_and_existing_final_is_graded_by_the_app_runner() {
    let course = course();
    for reference in &course.lessons[26..] {
        let key = reference.repository.strip_prefix("jhs512/mq3-lesson-redesigned-").unwrap();
        let raw = std::fs::read_to_string(root().join(format!("courses/redesigned/{key}.json"))).unwrap();
        let lesson = Lesson::parse(&raw, reference).unwrap();
        assert_eq!(lesson.tasks.len(), if key == "socket-partial-frames" || key == "node-cpu-offload" {5} else {4}, "{key}");
        for task in &lesson.tasks {
            let result = lesson_runner::check(task, &task.solution).await.unwrap();
            assert!(result.passed, "{key} / {} solution: {}", task.title, serde_json::to_string(&result).unwrap());
            let wrong = lesson_runner::check(task, &task.starter_code).await.unwrap();
            assert!(!wrong.passed, "{key} / {} starter accepted", task.title);
        }
        eprintln!("{key}: all {} steps pass; starters rejected",lesson.tasks.len());
    }
}
