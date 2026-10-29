mod common;

#[tokio::test]
async fn array_positions_repetition_and_empty_data_match_the_actual_teacher_runs() {
    let lesson=common::replay("java-arrays").await;
    assert_eq!(lesson.tasks.len(),9); // 8 teaching steps + the appended final challenge (92b37e2a)
    assert!(lesson.tasks.iter().all(|task|task.interaction.is_none()));
    let challenge=&lesson.tasks[7];
    let fixed=challenge.solution.replace("System.out.println(total)","System.out.println(6000)");
    assert!(!molip_quest::lesson_runner::check(challenge,&fixed).await.unwrap().passed,"A memorized total must fail");
}
