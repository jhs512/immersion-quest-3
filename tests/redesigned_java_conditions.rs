mod common;

#[tokio::test]
async fn delivery_boundaries_and_each_teacher_edit_match_real_java_execution() {
    let lesson=common::replay("java-conditions").await;
    assert_eq!(lesson.tasks.len(),9); // 8 teaching steps + the appended final challenge (92b37e2a)
    assert!(lesson.tasks.iter().all(|task|task.interaction.is_none()));
    let challenge=&lesson.tasks[7];
    let constant=challenge.solution.replace("System.out.println(fee);","System.out.println(0);");
    assert!(!molip_quest::lesson_runner::check(challenge,&constant).await.unwrap().passed,"A memorized result must fail");
    let fixed_threshold=challenge.solution.replace("amount >= limit","amount >= 20000");
    assert!(!molip_quest::lesson_runner::check(challenge,&fixed_threshold).await.unwrap().passed,"Changed free-delivery limits must still work");
}
