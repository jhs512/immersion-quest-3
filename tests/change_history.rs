use molip_quest::{change_history::ChangeEntry, content_updates::SnapshotStore};
use sha2::{Digest, Sha256};
fn snapshot() -> molip_quest::content_updates::Snapshot {
    let mut course: serde_json::Value =
        serde_json::from_str(include_str!("fixtures/player-pilot/a/course.json")).unwrap();
    let mut lesson: serde_json::Value =
        serde_json::from_str(include_str!("fixtures/player-pilot/a/lesson.json")).unwrap();
    course["change_history"] = serde_json::json!([{"at":"2026-10-18T09:00:00Z","summary":"코스 순서를 정리했어요.","reason":"선수 지식을 먼저 익히도록 바꿨어요.","details":["수업 내용과 고유 코드는 유지해요."]}]);
    lesson["change_history"] = serde_json::json!([{"at":"2026-10-19T02:00:00Z","summary":"문제의 오탈자를 고쳤어요.","reason":"설명을 읽기 쉽게 다듬었어요.","details":["출력이라는 단어의 오탈자를 고쳤어요."]}]);
    let raw = lesson.to_string();
    course["lessons"][0]["sha256"] = format!("{:x}", Sha256::digest(raw.as_bytes())).into();
    let root = tempfile::tempdir().unwrap();
    SnapshotStore::new(root.path())
        .prepare("mq3-validation/course", &course.to_string(), |_| {
            Ok(raw.clone())
        })
        .unwrap()
}
#[test]
fn author_changes_are_newest_first_and_contain_reason_time_and_expandable_details() {
    let snapshot = snapshot();
    let history = snapshot.history();
    assert_eq!(history.len(), 2);
    assert_eq!(history[0].entry.at, "2026-10-19T02:00:00Z");
    assert_eq!(history[0].entry.summary, "문제의 오탈자를 고쳤어요.");
    assert_eq!(history[0].entry.reason, "설명을 읽기 쉽게 다듬었어요.");
    assert_eq!(
        history[0].entry.details,
        vec!["출력이라는 단어의 오탈자를 고쳤어요."]
    );
    assert_eq!(history[1].entry.at, "2026-10-18T09:00:00Z");
    assert_ne!(history[0].origin, history[1].origin);
}
#[test]
fn invalid_author_history_is_rejected_instead_of_becoming_a_valid_candidate() {
    let mut change = ChangeEntry {
        at: "2026-02-29T10:00:00Z".into(),
        summary: "요약".into(),
        reason: "이유".into(),
        details: vec![],
    };
    assert!(change.validate().is_err());
    change.at = "2024-02-29T10:00:00Z".into();
    assert!(change.validate().is_ok());
    change.reason = " ".into();
    assert!(change.validate().is_err());
}

#[test]
fn applying_content_does_not_append_learner_clicks_to_author_history() {
    let candidate = snapshot();
    let root = tempfile::tempdir().unwrap();
    let store = SnapshotStore::new(root.path());
    store.apply(&candidate).unwrap();
    store.apply(&candidate).unwrap();
    assert_eq!(
        store
            .active("mq3-validation/course")
            .unwrap()
            .unwrap()
            .history(),
        candidate.history()
    );
}

#[test]
fn invalid_history_rejects_candidate_and_keeps_previous_installed_content() {
    let candidate = snapshot();
    let root = tempfile::tempdir().unwrap();
    let store = SnapshotStore::new(root.path());
    store.apply(&candidate).unwrap();
    let mut raw: serde_json::Value =
        serde_json::from_str(include_str!("fixtures/player-pilot/a/course.json")).unwrap();
    raw["change_history"] = serde_json::json!([{"at":"2026-13-01T00:00:00Z","summary":"수정","reason":"오류 수정","details":[]}]);
    assert!(store
        .prepare("mq3-validation/course", &raw.to_string(), |_| Ok(
            include_str!("fixtures/player-pilot/a/lesson.json").into()
        ))
        .is_err());
    assert_eq!(
        store
            .active("mq3-validation/course")
            .unwrap()
            .unwrap()
            .history(),
        candidate.history()
    );
}
