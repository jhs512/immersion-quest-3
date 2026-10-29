mod common;

#[tokio::test]
async fn ten_java_steps_and_every_teacher_run_agree_with_actual_jdk_output() {
    let lesson=common::replay("java-values").await;
    assert_eq!(lesson.tasks.len(),10);
    // Every step is a coding task now (2026-10-26); a typed result fails the prepared-value variation.
    assert!(lesson.tasks.iter().all(|task|task.interaction.is_none()));
    let last=&lesson.tasks[8];
    let hardcoded=last.solution.replace("(quantity + 1)","8");
    assert!(!molip_quest::lesson_runner::check(last,&hardcoded).await.unwrap().passed,"Memorized quantity must fail");
    // The final challenge (2026-10-29): a typed total fails the changed quantities.
    let challenge=&lesson.tasks[9];
    assert!(molip_quest::lesson_runner::check(challenge,&challenge.solution).await.unwrap().passed);
    let typed=challenge.solution.replace("(quantity + added)","5");
    assert!(!molip_quest::lesson_runner::check(challenge,&typed).await.unwrap().passed,"Memorized total must fail");
}
