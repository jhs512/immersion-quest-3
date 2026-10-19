use crate::{lesson_runner,repository_course::Task};

fn task(setup:&str)->Task {
    serde_json::from_value(serde_json::json!({
        "id":"sql-isolation","title":"독립된 SQL 실습","goal":"같은 표를 독립 실행해요.",
        "language":"sql","starter_code":"","solution":"SELECT count(*) AS n FROM stock;",
        "files":{"setup.sql":setup},"tests":[{"input":"","expected":"n\n2"}]
    })).unwrap()
}

#[tokio::test]
async fn database_files_cannot_escape_the_in_memory_practice() {
    let owned=tempfile::tempdir().unwrap();let file=owned.path().join("outside.db");
    let path=file.to_string_lossy().replace('\'',"''");
    let result=lesson_runner::run(&task(""),&format!("ATTACH DATABASE '{path}' AS outside; CREATE TABLE outside.t(value);"),"").await.unwrap();
    assert!(!file.exists(),"SQL practice wrote a database outside its isolated state");
    assert!(!result.success,"ATTACH must be rejected before touching disk");
}

#[tokio::test]
async fn each_run_restores_tables_and_bounds_large_results() {
    let task=task("CREATE TABLE stock(value INTEGER); INSERT INTO stock VALUES(2),(3);");
    let changed=lesson_runner::run(&task,"DELETE FROM stock; SELECT count(*) AS n FROM stock;","").await.unwrap();
    assert!(changed.success);assert_eq!(changed.stdout,"n\n0\n");
    let restored=lesson_runner::run(&task,"SELECT count(*) AS n FROM stock;","").await.unwrap();
    assert!(restored.success);assert_eq!(restored.stdout,"n\n2\n");
    let many=lesson_runner::run(&task,"WITH RECURSIVE nums(n) AS (VALUES(1) UNION ALL SELECT n+1 FROM nums WHERE n<100000) SELECT n FROM nums;","").await.unwrap();
    assert!(!many.success,"unbounded result collection must be rejected");
    assert!(many.stdout.len()<=65536);
}

#[tokio::test]
async fn actual_queries_handle_literals_transactions_and_new_data() {
    let mut task=task("CREATE TABLE stock(value INTEGER, label TEXT); INSERT INTO stock VALUES(2,'pen;blue'),(3,NULL);");
    let result=lesson_runner::run(&task,"BEGIN; UPDATE stock SET value=value+1; ROLLBACK; SELECT value, label FROM stock ORDER BY value;", "").await.unwrap();
    assert!(result.success,"{}",result.stderr);assert_eq!(result.stdout,"value | label\n2 | pen;blue\n3 | NULL\n");
    task.tests[0].expected="n\n5".into();
    task.variations=serde_json::from_value(serde_json::json!([{"files":{"setup.sql":"CREATE TABLE stock(value INTEGER); INSERT INTO stock VALUES(7),(9);"},"expected":"n\n16"}])).unwrap();
    assert!(lesson_runner::check(&task,"SELECT SUM(value) AS n FROM stock;").await.unwrap().passed);
    assert!(!lesson_runner::check(&task,"SELECT 5 AS n;").await.unwrap().passed);
}
