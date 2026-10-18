use molip_quest::{lesson_runner, repository_course::Task};
use serde_json::json;

#[tokio::test]
async fn choice_grading_follows_option_identity_after_reordering() {
    let mut value = json!({"id":"choice","title":"판단","goal":"맞는 설명을 골라요.","language":"javascript","starter_code":"","solution":"staged","tests":[],"interaction":{"kind":"choice","options":[{"id":"committed","text":"이미 기록했어요."},{"id":"staged","text":"기록할 준비를 했어요."}],"answer":"staged"}});
    let task: Task = serde_json::from_value(value.clone()).unwrap();
    assert!(lesson_runner::check(&task, "staged").await.unwrap().passed);
    assert!(!lesson_runner::check(&task, "committed").await.unwrap().passed);
    value["interaction"]["options"].as_array_mut().unwrap().reverse();
    let shuffled: Task = serde_json::from_value(value).unwrap();
    assert!(lesson_runner::check(&shuffled, "staged").await.unwrap().passed);
}

fn interaction_task(interaction: serde_json::Value) -> Task {
    serde_json::from_value(json!({"id":"interaction","title":"판단","goal":"조건을 확인해요.","language":"javascript","starter_code":"","solution":"","interaction":interaction})).unwrap()
}

#[tokio::test]
async fn ordering_accepts_declared_alternatives_but_not_missing_or_repeated_pieces() {
    let task = interaction_task(json!({"kind":"order","options":[{"id":"a","text":"A"},{"id":"b","text":"B"},{"id":"noise","text":"사용하지 않아요"}],"accepted":[["a","b"],["b","a"]]}));
    for answer in [r#"["a","b"]"#, r#"["b","a"]"#] {
        assert!(lesson_runner::check(&task, answer).await.unwrap().passed);
    }
    for answer in [r#"["a","a"]"#, r#"["a"]"#, r#"["noise","b"]"#, "not JSON"] {
        assert!(!lesson_runner::check(&task, answer).await.unwrap().passed);
    }
}

#[tokio::test]
async fn fill_accepts_only_owner_declared_answers_and_does_not_execute() {
    let task = interaction_task(json!({"kind":"fill","accepted":["git add", "git stage"]}));
    assert!(lesson_runner::check(&task, " git add\n").await.unwrap().passed);
    assert!(lesson_runner::check(&task, "git stage").await.unwrap().passed);
    assert!(!lesson_runner::check(&task, "git commit").await.unwrap().passed);
    assert!(lesson_runner::run(&task, "git add", "").await.is_err());
}

#[test]
fn lesson_validation_accepts_interactions_without_code_tests_and_rejects_broken_answers() {
    let mut lesson: molip_quest::repository_course::Lesson = serde_json::from_str(include_str!("fixtures/player-pilot/a/lesson.json")).unwrap();
    let original = lesson.tasks[0].clone();
    let mut task = interaction_task(json!({"kind":"choice","options":[{"id":"a","text":"A"},{"id":"b","text":"B"}],"answer":"a"}));
    task.id = original.id;
    lesson.tasks[0] = task;
    assert!(lesson.validate().is_ok());
    lesson.tasks[0].interaction = Some(serde_json::from_value(json!({"kind":"choice","options":[{"id":"a","text":"A"},{"id":"a","text":"B"}],"answer":"a"})).unwrap());
    assert!(lesson.validate().is_err());
}
