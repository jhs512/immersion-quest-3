use molip_quest::telemetry;
use opentelemetry::{trace::FutureExt, KeyValue};
#[tokio::test]
async fn local_pipeline_keeps_async_context_failures_navigation_and_web_errors() {
    let root = tempfile::tempdir().unwrap();
    std::env::set_var("MOLIP_DATA_DIR", root.path());
    let guard = telemetry::initialize().unwrap();
    let mut root_span = telemetry::operation(
        "test.action",
        vec![
            KeyValue::new("task.id", "task_1"),
            KeyValue::new("authorization", "SECRET"),
        ],
    );
    async {
        let first = telemetry::observe("test.first", vec![], async {
            tokio::task::yield_now().await;
            Ok::<_, String>(())
        });
        let second = telemetry::observe("test.second", vec![], async {
            Err::<(), _>("private/path/SECRET (os error 183)".into())
        });
        let (a, b) = tokio::join!(first, second);
        assert!(a.is_ok() && b.is_err());
    }
    .with_context(root_span.context())
    .await;
    root_span.finish("ok");
    telemetry::record_web_error(telemetry::WebError {
        kind: "error".into(),
        name: "TypeError".into(),
        file: "/private/SECRET.js".into(),
        line: 3,
        column: 2,
        course: "course_1".into(),
        lesson: "lesson_1".into(),
        task: "task_1".into(),
    });
    let mut navigation =
        telemetry::operation("task.open", vec![KeyValue::new("task.id", "task_1")]);
    navigation.finish("ok");
    let value: serde_json::Value =
        serde_json::from_str(&telemetry::export_recent().unwrap()).unwrap();
    let spans = value["spans"].as_array().unwrap();
    let parent = spans.iter().find(|r| r["name"] == "test.action").unwrap();
    for name in ["test.first", "test.second"] {
        let child = spans.iter().find(|r| r["name"] == name).unwrap();
        assert_eq!(child["parent_span_id"], parent["span_id"]);
        assert_eq!(child["trace_id"], parent["trace_id"]);
    }
    let failed = spans.iter().find(|r| r["name"] == "test.second").unwrap();
    assert_eq!(failed["error"], true);
    assert_eq!(failed["attributes"]["error.code"], 183);
    assert!(spans
        .iter()
        .any(|r| r["name"] == "javascript.error" && r["attributes"]["task.id"] == "task_1"));
    assert!(spans.iter().any(|r| r["name"] == "operation.started"));
    assert!(!value.to_string().contains("SECRET"));
    assert_eq!(value["retention_seconds"], 3600);
    assert_eq!(value["navigation_retention_days"], 180);
    drop(guard);
    let connection = rusqlite::Connection::open(root.path().join("telemetry.sqlite3")).unwrap();
    assert_eq!(
        connection
            .query_row("SELECT count(*) FROM spans WHERE navigation=1", [], |r| {
                r.get::<_, usize>(0)
            })
            .unwrap(),
        1
    );
    std::env::remove_var("MOLIP_DATA_DIR");
}
