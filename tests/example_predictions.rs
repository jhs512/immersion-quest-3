use molip_quest::issue_progress::{LearningEvent,ProgressKey,StudyMode,EventKind,passed_for_study,parse_event};

#[test]
fn prediction_is_an_observation_and_cannot_grant_or_revoke_success() {
    let key=ProgressKey{user_id:1,course_id:"course".into(),lesson_id:"lesson".into()};
    let mut predicted=LearningEvent::new(key.clone(),"v1",StudyMode::Full,"round",EventKind::ExampleRun);
    predicted.task_id=Some("task".into());predicted.prediction=Some("wrong-first-guess".into());
    assert!(passed_for_study(&[predicted.clone()],"v1",StudyMode::Full,"round").is_empty());
    assert_eq!(parse_event(&predicted.comment()).unwrap().prediction.as_deref(),Some("wrong-first-guess"));
    let mut attempt=LearningEvent::new(key,"v1",StudyMode::Full,"round",EventKind::Attempt);
    attempt.task_id=Some("task".into());attempt.passed=true;
    assert!(passed_for_study(&[predicted,attempt],"v1",StudyMode::Full,"round").contains("task"));
}

#[test]
fn old_events_have_no_prediction_and_keep_their_serialized_shape() {
    let event=LearningEvent::new(ProgressKey{user_id:1,course_id:"course".into(),lesson_id:"lesson".into()},"v1",StudyMode::Full,"round",EventKind::Attempt);
    let mut value=serde_json::to_value(event).unwrap();
    value.as_object_mut().unwrap().remove("prediction");
    let restored:LearningEvent=serde_json::from_value(value).unwrap();
    assert!(restored.prediction.is_none());
    assert!(serde_json::to_value(restored).unwrap().get("prediction").is_none());
}
