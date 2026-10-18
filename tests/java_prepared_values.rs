use molip_quest::{repository_course::Task,lesson_runner};

#[tokio::test]
async fn a_memorized_java_output_does_not_pass_when_prepared_quantity_changes() {
    let source="void main() {\n    int quantity = 7;\n    System.out.println(\"수량: \" + (quantity + 1));\n}\n";
    let task:Task=serde_json::from_value(serde_json::json!({"id":"quantity","title":"Quantity","goal":"Use the value","language":"java","starter_code":source,"solution":source,
        "tests":[{"input":"","expected":"수량: 8"}],"variations":[{"values":{"quantity":"4"},"expected":"수량: 5"}]})).unwrap();
    let report=lesson_runner::check(&task,source).await.unwrap();
    assert!(report.passed);assert_eq!(report.cases.len(),2);
    let hardcoded=source.replace("(quantity + 1)","8");
    let report=lesson_runner::check(&task,&hardcoded).await.unwrap();
    assert!(!report.passed);assert!(report.cases[0].passed);assert!(!report.cases[1].passed);
}
