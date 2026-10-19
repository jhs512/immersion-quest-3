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

#[tokio::test]
async fn arrays_are_graded_with_empty_single_and_reordered_prepared_values() {
    let source="void main() {\n    int[] prices = {2, 4};\n    int total = 0;\n    for (int price : prices) total = total + price;\n    System.out.println(total);\n}\n";
    let task:Task=serde_json::from_value(serde_json::json!({"id":"array-total","title":"Array total","goal":"Read every prepared price","language":"java","starter_code":source,"solution":source,
        "tests":[{"input":"","expected":"6"}],"variations":[{"values":{"prices":"{}"},"expected":"0"},{"values":{"prices":"{7}"},"expected":"7"},{"values":{"prices":"{4, 2, 1}"},"expected":"7"}]})).unwrap();
    let report=lesson_runner::check(&task,source).await.unwrap();
    assert!(report.passed,"Prepared Java arrays must be replaceable: {}",serde_json::to_string(&report).unwrap());
    assert_eq!(report.cases.len(),4);
    let fixed=source.replace("System.out.println(total)","System.out.println(6)");
    let report=lesson_runner::check(&task,&fixed).await.unwrap();
    assert!(!report.passed);
    assert!(report.cases[0].passed);
}
