use molip_quest::{lesson_runner,repository_course::Task};

#[tokio::test]
async fn running_prepared_code_does_not_compile_or_grade_the_selected_answer() {
    let task:Task=serde_json::from_value(serde_json::json!({
        "id":"example-choice","title":"Output","goal":"Choose output","language":"javascript","starter_code":"","solution":"two",
        "example_code":"console.log(2);",
        "interaction":{"kind":"choice","options":[{"id":"two","text":"2"},{"id":"three","text":"3"}],"answer":"two"}
    })).unwrap();
    let executed=lesson_runner::run_example(&task,task.example_code.as_deref().unwrap(),"").await.unwrap();
    assert!(executed.success);assert_eq!(executed.stdout,"2\n");
    assert!(!lesson_runner::check(&task,"three").await.unwrap().passed);
    assert!(lesson_runner::check(&task,"two").await.unwrap().passed);
    assert!(lesson_runner::run(&task,"three","").await.is_err(),"Answer submission is still not a program execution path");
}

#[test]
fn published_interaction_examples_require_nonempty_bounded_source() {
    let mut value:serde_json::Value=serde_json::from_str(include_str!("fixtures/player-pilot/f/lesson.json")).unwrap();
    value["tasks"][0]["example_code"]=serde_json::json!("console.log(2);");
    let lesson:molip_quest::repository_course::Lesson=serde_json::from_value(value.clone()).unwrap();
    lesson.validate().unwrap();
    for source in ["".to_owned()," \n".to_owned(),"x".repeat(65537)] {
        value["tasks"][0]["example_code"]=serde_json::json!(source);
        let lesson:molip_quest::repository_course::Lesson=serde_json::from_value(value.clone()).unwrap();
        assert!(lesson.validate().is_err(),"An unusable example must not be published as runnable");
    }
}

#[tokio::test]
async fn reordered_statements_produce_real_different_outputs_without_granting_success() {
    let value=serde_json::json!({"id":"order-example","title":"Order","goal":"Set before print","language":"javascript","starter_code":"[\"print\",\"assign\"]","solution":"[\"assign\",\"print\"]",
      "example_code":"let quantity=2;\n// @order\n","example_order_marker":"// @order",
      "interaction":{"kind":"order","options":[{"id":"assign","text":"quantity=3;"},{"id":"print","text":"console.log(quantity);"}],"accepted":[["assign","print"]]}});
    let task:Task=serde_json::from_value(value).unwrap();
    let before=task.example_for_answer(&task.starter_code).unwrap();
    let after=task.example_for_answer(&task.solution).unwrap();
    assert_ne!(before,after);
    assert_eq!(lesson_runner::run_example(&task,&before,"").await.unwrap().stdout,"2\n");
    assert_eq!(lesson_runner::run_example(&task,&after,"").await.unwrap().stdout,"3\n");
    for answer in [r#"["print","unknown"]"#,r#"["print","print"]"#,"not JSON"] {
        assert!(task.example_for_answer(answer).is_err());
    }
    assert!(!lesson_runner::check(&task,&task.starter_code).await.unwrap().passed);
}
