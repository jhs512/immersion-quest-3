use molip_quest::repository_course::{CourseManifest, Lesson};

#[tokio::test]
async fn reviewed_candidate_uses_real_admission_and_keeps_the_problem_identity() {
    let baseline_course = CourseManifest::parse(include_str!("fixtures/player-pilot/a/course.json")).unwrap();
    let baseline = Lesson::parse(include_str!("fixtures/player-pilot/a/lesson.json"), &baseline_course.lessons[0]).unwrap();
    let candidate_course = CourseManifest::parse(include_str!("fixtures/player-pilot/i/course.json")).unwrap();
    let raw = include_str!("fixtures/player-pilot/i/lesson.json");
    let candidate = Lesson::parse(raw, &candidate_course.lessons[0]).unwrap();
    assert_eq!(candidate.tasks[0].goal, "숫자 3을 출력한 뒤 제출하세요.");
    assert_eq!(candidate.tasks[1], baseline.tasks[1]);
    assert_eq!(candidate.chapters, baseline.chapters);
    let mut normalized = candidate.clone();
    normalized.revision = baseline.revision.clone();
    normalized.tasks[0].goal = baseline.tasks[0].goal.clone();
    assert_eq!(normalized, baseline);
    assert!(Lesson::parse(raw, &baseline_course.lessons[0]).is_err());
    assert!(molip_quest::lesson_runner::check(&candidate.tasks[0], &candidate.tasks[0].solution).await.unwrap().passed);
    assert!(!molip_quest::lesson_runner::check(&candidate.tasks[0], &candidate.tasks[0].starter_code).await.unwrap().passed);
    assert!(!raw.contains("core_flow"));
    assert!(!raw.contains("synthetic-fixture-only"));
}
