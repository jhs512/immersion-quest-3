mod common;

#[tokio::test]
async fn nine_java_steps_and_every_teacher_run_agree_with_actual_jdk_output() {
    let lesson=common::replay("java-values").await;
    assert_eq!(lesson.tasks.len(),9);
    // Every step is a coding task now (2026-10-26); a typed result fails the prepared-value variation.
    assert!(lesson.tasks.iter().all(|task|task.interaction.is_none()));
    let last=&lesson.tasks[8];
    let hardcoded=last.solution.replace("(quantity + 1)","8");
    assert!(!molip_quest::lesson_runner::check(last,&hardcoded).await.unwrap().passed,"Memorized quantity must fail");
}
