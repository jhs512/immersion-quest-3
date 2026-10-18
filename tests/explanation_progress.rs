use molip_quest::issue_progress::*;

#[test]
fn explanation_is_not_success_and_success_before_or_after_view_remains_normal_success() {
    let key=ProgressKey{user_id:1,course_id:"course".into(),lesson_id:"lesson".into()};
    let task="stp_3f59e7bd-70c1-4e81-9cb0-000000000005";
    let mut view=LearningEvent::new(key.clone(),"v1",StudyMode::Full,"one",EventKind::ExplanationViewed);
    view.task_id=Some(task.into());
    let mut events=vec![view.clone()];
    assert!(passed_for_study(&events,"v1",StudyMode::Full,"one").is_empty());
    assert!(explanation_info(&events,task).before_success);
    let mut attempt=LearningEvent::new(key,"v1",StudyMode::Full,"one",EventKind::Attempt);
    attempt.task_id=Some(task.into());attempt.passed=true;events.push(attempt);
    view.id=new_id();view.success_before_view=true;events.push(view);
    assert!(passed_for_study(&events,"v1",StudyMode::Full,"one").contains(task));
    let info=explanation_info(&events,task);
    assert!(info.before_success && info.after_success);
}
