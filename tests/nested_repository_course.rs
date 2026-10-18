use molip_quest::repository_course::{CourseManifest, Lesson};
use serde_json::{json, Value};
use sha2::{Digest, Sha256};

fn changed_lesson(change: impl FnOnce(&mut Value)) -> Result<Lesson, String> {
    let mut course = CourseManifest::parse(include_str!("fixtures/player-pilot/a/course.json")).unwrap();
    let mut value: Value = serde_json::from_str(include_str!("fixtures/player-pilot/a/lesson.json")).unwrap();
    change(&mut value);
    let raw = serde_json::to_string(&value).unwrap();
    course.lessons[0].sha256 = format!("{:x}", Sha256::digest(raw.as_bytes()));
    Lesson::parse(&raw, &course.lessons[0])
}

#[tokio::test]
async fn fixed_pilot_course_opens_and_grades_through_the_real_player_contract() {
    let course = CourseManifest::parse(include_str!("fixtures/player-pilot/a/course.json")).unwrap();
    let lesson = Lesson::parse(include_str!("fixtures/player-pilot/a/lesson.json"), &course.lessons[0]).unwrap();
    assert_eq!(lesson.tasks.len(), 2);
    let task = &lesson.tasks[0];
    assert!(molip_quest::lesson_runner::check(task, &task.solution).await.unwrap().passed);
    assert!(!molip_quest::lesson_runner::check(task, &task.starter_code).await.unwrap().passed);
}

#[test]
fn every_level_has_its_own_goals_and_steps_resolve_to_their_context() {
    let lesson = changed_lesson(|_| {}).unwrap();
    assert_eq!(lesson.objectives.len(), 2);
    let (chapter, unit, step) = lesson.context_for(&lesson.tasks[1].id).unwrap();
    assert_eq!(chapter.title, "값과 출력");
    assert_eq!(unit.title, "값을 조금씩 바꿔요");
    assert_eq!(step.objectives, ["출력 결과를 확인해요: 5"]);
    assert!(lesson.context_for("missing").is_none());
    for pointer in ["/objectives", "/chapters/0/objectives", "/chapters/0/units/0/objectives", "/chapters/0/units/0/steps/0/objectives"] {
        assert!(changed_lesson(|value| *value.pointer_mut(pointer).unwrap() = json!([])).is_err(), "{pointer}");
        assert!(changed_lesson(|value| *value.pointer_mut(pointer).unwrap() = json!(["  "])).is_err(), "{pointer}");
    }
}

#[test]
fn invalid_codes_duplicate_steps_and_unconnected_payloads_are_rejected() {
    for code in ["stp_not-a-uuid", "stp_3f59e7bd-70c1-1e81-9cb0-000000000005", "unt_3f59e7bd-70c1-4e81-9cb0-000000000005"] {
        assert!(changed_lesson(|value| value["chapters"][0]["units"][0]["steps"][0]["id"] = json!(code)).is_err());
    }
    assert!(changed_lesson(|value| {
        value["chapters"][0]["units"][0]["steps"][1] = value["chapters"][0]["units"][0]["steps"][0].clone();
    }).is_err());
    assert!(changed_lesson(|value| { value["tasks"].as_array_mut().unwrap().swap(0, 1); }).is_err());
    assert!(changed_lesson(|value| { value["chapters"][0]["units"][0]["steps"].as_array_mut().unwrap().pop(); }).is_err());
}

#[test]
fn pilot_versions_keep_identity_and_a_corrupted_candidate_cannot_replace_the_pinned_lesson() {
    let a = CourseManifest::parse(include_str!("fixtures/player-pilot/a/course.json")).unwrap();
    let b = CourseManifest::parse(include_str!("fixtures/player-pilot/b/course.json")).unwrap();
    let first = Lesson::parse(include_str!("fixtures/player-pilot/a/lesson.json"), &a.lessons[0]).unwrap();
    let second = Lesson::parse(include_str!("fixtures/player-pilot/b/lesson.json"), &b.lessons[0]).unwrap();
    assert_eq!(a.id, b.id);
    assert_eq!(first.id, second.id);
    assert_eq!(first.tasks[0].id, second.tasks[0].id);
    assert_eq!(second.required_tasks().len(), 3);
    assert!(Lesson::parse(include_str!("fixtures/player-pilot/b/lesson.json"), &a.lessons[0]).is_err());
    let damaged = include_str!("fixtures/player-pilot/a/lesson.json").replace("값과 출력", "손상 후보");
    assert!(Lesson::parse(&damaged, &a.lessons[0]).is_err());
    assert!(Lesson::parse(include_str!("fixtures/player-pilot/a/lesson.json"), &a.lessons[0]).is_ok());
}
