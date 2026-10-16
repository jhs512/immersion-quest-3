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
