use molip_quest::issue_progress::*;
fn key()->ProgressKey { ProgressKey{user_id:42,course_id:"java".into(),lesson_id:"git".into()} }
fn event(mode:StudyMode,revision:&str,kind:EventKind)->LearningEvent {LearningEvent::new(key(),revision,mode,"round-a",kind)}
#[test]
fn completion_requires_every_required_task_in_the_same_mode_and_revision() {
    let mut attempt=event(StudyMode::Review,"v1",EventKind::Attempt);attempt.task_id=Some("one".into());attempt.passed=true;
    let mut done=event(StudyMode::Review,"v1",EventKind::Completed);done.required=vec!["one".into()];
    assert!(!status(&[done.clone()],"v1",&done.required).completed);
    assert!(!status(&[attempt.clone(),done.clone()],"v2",&done.required).current);
    let state=status(&[attempt.clone(),done.clone(),done.clone()],"v1",&done.required);
    assert!(state.completed&&state.current);assert_eq!(state.review_completions,1);assert_eq!(state.full_completions,0);
    attempt.mode=StudyMode::Full;
    assert!(!status(&[attempt,done.clone()],"v1",&done.required).completed);
}
#[test]
fn completion_survives_new_required_tasks_and_old_versions() {
    let mut attempt=event(StudyMode::Full,"v1",EventKind::Attempt);attempt.task_id=Some("one".into());attempt.passed=true;
    let mut done=event(StudyMode::Full,"v1",EventKind::Completed);done.required=vec!["one".into()];
    let state=status(&[attempt,done],"v2",&["one".into(),"new".into()]);
    assert!(state.completed);assert!(!state.current);assert_eq!(state.full_completions,1);
}
#[test]
fn merging_is_idempotent_and_account_scoped() {
    let a=event(StudyMode::Full,"v1",EventKind::Viewed);
    let mut other=a.clone();other.id=new_id();other.key.user_id=99;
    let parsed=parse_event(&a.comment()).unwrap();assert_eq!(parsed,a);
    assert_eq!(merge([a.clone(),a.clone(),other],&key()),vec![a]);
}

#[test]
fn learning_progress_combines_old_modes_and_rounds_without_double_counting() {
    let first="stp_3f59e7bd-70c1-4e81-9cb0-000000000005".to_string();
    let second="stp_3f59e7bd-70c1-4e81-9cb0-000000000006".to_string();
    let mut a=event(StudyMode::Full,"v1",EventKind::Attempt);a.task_id=Some(first.clone());a.passed=true;
    let mut b=event(StudyMode::Review,"v1",EventKind::Attempt);b.task_id=Some(second.clone());b.passed=true;b.round="other-round".into();
    let required=vec![first,second,"stp_3f59e7bd-70c1-4e81-9cb0-000000000007".into()];
    let progress=learning_progress(&[a.clone(),a,b],"v2",&required);
    assert_eq!((progress.solved,progress.total,progress.percent),(2,3,66));
    assert_eq!(learning_progress(&[],"v2",&[]).percent,0);
}
