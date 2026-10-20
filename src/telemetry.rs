//! Local-only OpenTelemetry traces. No network exporter or application data payloads.
use opentelemetry::{
    trace::{FutureExt, Span, TraceContextExt, Tracer, TracerProvider},
    Context, KeyValue,
};
use opentelemetry_sdk::{
    error::{OTelSdkError, OTelSdkResult},
    trace::{BatchConfigBuilder, BatchSpanProcessor, SdkTracerProvider, SpanData, SpanExporter},
    Resource,
};
use rusqlite::{params, Connection};
use serde::{Deserialize, Serialize};
use std::{
    path::Path,
    sync::{mpsc, Arc, Mutex, OnceLock},
    time::{Duration, SystemTime, UNIX_EPOCH},
};

const RETENTION_MS: i64 = 60 * 60 * 1000;
const NAVIGATION_MS: i64 = 180 * 24 * 60 * 60 * 1000;
const MAX_RECORDS: usize = 10_000;
const MAX_NAVIGATION: usize = 50_000;
static RECORDER: OnceLock<Recorder> = OnceLock::new();

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Record {
    pub trace_id: String,
    pub span_id: String,
    pub parent_span_id: String,
    pub name: String,
    pub started_ms: i64,
    pub ended_ms: i64,
    pub duration_ms: u64,
    pub error: bool,
    pub attributes: std::collections::BTreeMap<String, serde_json::Value>,
}

fn millis(time: SystemTime) -> i64 {
    time.duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis()
        .min(i64::MAX as u128) as i64
}
fn now() -> i64 {
    millis(SystemTime::now())
}

// An allowlist, rather than redacting arbitrary logs after collection. In particular,
// source code, terminal commands/output, URLs, tokens and exception messages stay out.
fn allowed(key: &str) -> bool {
    matches!(
        key,
        "operation.name"
            | "course.id"
            | "lesson.id"
            | "task.id"
            | "task.language"
            | "result.state"
            | "error.code"
            | "error.kind"
            | "tool.kind"
            | "package.name"
            | "process.exit_code"
            | "exception.type"
            | "code.file"
            | "code.line"
            | "code.column"
            | "checks.total"
            | "checks.failed"
            | "app.build"
            | "app.version"
            | "os.type"
            | "host.arch"
    )
}

#[derive(Debug)]
struct Store {
    connection: Mutex<Connection>,
}
impl Store {
    fn open(path: &Path) -> Result<Self, String> {
        let connection = Connection::open(path).map_err(|e| e.to_string())?;
        connection
            .busy_timeout(Duration::from_millis(250))
            .map_err(|e| e.to_string())?;
        // Reuse free pages, with a hard 64 MiB database ceiling. No growing WAL file.
        connection.execute_batch("PRAGMA journal_mode=DELETE; PRAGMA secure_delete=ON; PRAGMA max_page_count=16384;
            CREATE TABLE IF NOT EXISTS spans(id INTEGER PRIMARY KEY, ended_ms INTEGER NOT NULL, payload TEXT NOT NULL, navigation INTEGER NOT NULL DEFAULT 0);
            CREATE INDEX IF NOT EXISTS spans_ended ON spans(ended_ms);").map_err(|e|e.to_string())?;
        let store = Self {
            connection: Mutex::new(connection),
        };
        store.prune(now()).map_err(|e| e.to_string())?;
        Ok(store)
    }
    fn prune_connection(connection: &Connection, at: i64) -> rusqlite::Result<()> {
        connection.execute("DELETE FROM spans WHERE ended_ms < CASE WHEN navigation=1 THEN ?1 ELSE ?2 END OR ended_ms > ?3", params![at-NAVIGATION_MS,at-RETENTION_MS,at+60_000])?;
        for (navigation, limit) in [(0, MAX_RECORDS), (1, MAX_NAVIGATION)] {
            connection.execute("DELETE FROM spans WHERE navigation=?1 AND id NOT IN (SELECT id FROM spans WHERE navigation=?1 ORDER BY id DESC LIMIT ?2)", params![navigation,limit as i64])?;
        }
        Ok(())
    }
    fn prune(&self, at: i64) -> rusqlite::Result<()> {
        Self::prune_connection(
            &self.connection.lock().unwrap_or_else(|e| e.into_inner()),
            at,
        )
    }
    fn write(&self, records: &[Record]) -> Result<(), String> {
        let mut connection = self.connection.lock().unwrap_or_else(|e| e.into_inner());
        let transaction = connection.transaction().map_err(|e| e.to_string())?;
        Self::prune_connection(&transaction, now()).map_err(|e| e.to_string())?;
        for record in records {
            let payload = serde_json::to_string(record).map_err(|e| e.to_string())?;
            transaction
                .execute(
                    "INSERT INTO spans(ended_ms,payload,navigation) VALUES(?1,?2,?3)",
                    params![
                        record.ended_ms,
                        payload,
                        if matches!(
                            record.name.as_str(),
                            "task.open" | "lesson.open" | "course.open"
                        ) {
                            1
                        } else {
                            0
                        }
                    ],
                )
                .map_err(|e| e.to_string())?;
        }
        Self::prune_connection(&transaction, now()).map_err(|e| e.to_string())?;
        transaction.commit().map_err(|e| e.to_string())
    }
    fn recent(&self) -> Result<Vec<Record>, String> {
        let connection = self.connection.lock().unwrap_or_else(|e| e.into_inner());
        Self::prune_connection(&connection, now()).map_err(|e| e.to_string())?;
        let mut query = connection
            .prepare("SELECT payload FROM spans ORDER BY id")
            .map_err(|e| e.to_string())?;
        let rows = query
            .query_map([], |row| row.get::<_, String>(0))
            .map_err(|e| e.to_string())?;
        rows.map(|row| {
            serde_json::from_str(&row.map_err(|e| e.to_string())?).map_err(|e| e.to_string())
        })
        .collect()
    }
}

#[derive(Debug)]
struct LocalExporter {
    store: Arc<Store>,
}
impl SpanExporter for LocalExporter {
    async fn export(&self, batch: Vec<SpanData>) -> OTelSdkResult {
        let records: Vec<_> = batch
            .into_iter()
            .map(|span| {
                let attributes = span
                    .attributes
                    .into_iter()
                    .filter(|a| allowed(a.key.as_str()))
                    .map(|a| {
                        let value = match a.value {
                            opentelemetry::Value::Bool(v) => v.into(),
                            opentelemetry::Value::I64(v) => v.into(),
                            opentelemetry::Value::F64(v) => serde_json::json!(v),
                            v => v.to_string().chars().take(160).collect::<String>().into(),
                        };
                        (a.key.to_string(), value)
                    })
                    .chain([
                        (
                            "app.build".into(),
                            option_env!("MOLIP_BUILD")
                                .filter(|value| !value.is_empty())
                                .unwrap_or("development")
                                .into(),
                        ),
                        ("app.version".into(), env!("CARGO_PKG_VERSION").into()),
                        ("os.type".into(), std::env::consts::OS.into()),
                        ("host.arch".into(), std::env::consts::ARCH.into()),
                    ])
                    .collect();
                Record {
                    trace_id: span.span_context.trace_id().to_string(),
                    span_id: span.span_context.span_id().to_string(),
                    parent_span_id: span.parent_span_id.to_string(),
                    name: span.name.to_string(),
                    started_ms: millis(span.start_time),
                    ended_ms: millis(span.end_time),
                    duration_ms: span
                        .end_time
                        .duration_since(span.start_time)
                        .unwrap_or_default()
                        .as_millis()
                        .min(u64::MAX as u128) as u64,
                    error: matches!(span.status, opentelemetry::trace::Status::Error { .. }),
                    attributes,
                }
            })
            .collect();
        self.store
            .write(&records)
            .map_err(OTelSdkError::InternalFailure)
    }
}

#[derive(Clone)]
struct Recorder {
    provider: SdkTracerProvider,
    store: Arc<Store>,
}
pub struct Guard {
    recorder: Recorder,
    stop: mpsc::Sender<()>,
    maintenance: Option<std::thread::JoinHandle<()>>,
}
impl Drop for Guard {
    fn drop(&mut self) {
        let _ = self.recorder.provider.shutdown();
        let _ = self.stop.send(());
        if let Some(worker) = self.maintenance.take() {
            let _ = worker.join();
        }
    }
}
impl Guard {
    fn open(path: &Path) -> Result<Self, String> {
        let store = Arc::new(Store::open(path)?);
        let processor = BatchSpanProcessor::builder(LocalExporter {
            store: store.clone(),
        })
        .with_batch_config(
            BatchConfigBuilder::default()
                .with_max_queue_size(1024)
                .with_max_export_batch_size(64)
                .with_scheduled_delay(Duration::from_secs(2))
                .build(),
        )
        .build();
        let provider = SdkTracerProvider::builder()
            .with_span_processor(processor)
            .with_sampler(opentelemetry_sdk::trace::Sampler::AlwaysOn)
            .with_resource(
                Resource::builder_empty()
                    .with_service_name("molip-quest")
                    .build(),
            )
            .build();
        let (stop, receiver) = mpsc::channel();
        let cleanup = store.clone();
        let maintenance = std::thread::Builder::new()
            .name("mq-telemetry-retention".into())
            .spawn(move || {
                while receiver.recv_timeout(Duration::from_secs(30))
                    == Err(mpsc::RecvTimeoutError::Timeout)
                {
                    let _ = cleanup.prune(now());
                }
            })
            .map_err(|e| e.to_string())?;
        Ok(Self {
            recorder: Recorder { provider, store },
            stop,
            maintenance: Some(maintenance),
        })
    }
}

/// Initialize once from main. The guard flushes on ordinary process exit.
pub fn initialize() -> Result<Guard, String> {
    let guard = Guard::open(&crate::data_dir()?.join("telemetry.sqlite3"))?;
    RECORDER
        .set(guard.recorder.clone())
        .map_err(|_| "telemetry already initialized".to_string())?;
    let mut startup = operation("app.start", vec![]);
    startup.finish("ok");
    Ok(guard)
}

pub struct Operation {
    context: Context,
    ended: bool,
}
impl Operation {
    pub fn context(&self) -> Context {
        self.context.clone()
    }
    pub fn error(&mut self, error: &str) {
        let kind = if error.contains("timeout")
            || error.contains("시간 초과")
            || error.contains("시간을 초과")
        {
            "timeout"
        } else if error.contains("connect") {
            "connection"
        } else {
            "operation"
        };
        self.context
            .span()
            .set_attribute(KeyValue::new("error.kind", kind));
        if let Some(code) = error
            .split("os error ")
            .nth(1)
            .and_then(|tail| tail.split(')').next())
            .and_then(|code| code.parse::<i64>().ok())
        {
            self.context
                .span()
                .set_attribute(KeyValue::new("error.code", code));
        }
    }
    pub fn finish(&mut self, outcome: &'static str) {
        if self.ended {
            return;
        }
        let span = self.context.span();
        span.set_attribute(KeyValue::new("result.state", outcome));
        span.set_status(
            if matches!(
                outcome,
                "ok" | "passed" | "finished" | "not_passed" | "cancelled"
            ) {
                opentelemetry::trace::Status::Ok
            } else {
                opentelemetry::trace::Status::error(outcome)
            },
        );
        span.end();
        self.ended = true;
    }
}
impl Drop for Operation {
    fn drop(&mut self) {
        if !self.ended {
            self.finish(if std::thread::panicking() {
                "panic"
            } else {
                "cancelled"
            });
        }
    }
}
pub fn operation(name: &'static str, attributes: Vec<KeyValue>) -> Operation {
    let context = if let Some(recorder) = RECORDER.get() {
        let tracer = recorder.provider.tracer("mq.player");
        let mut span = tracer.start_with_context(name, &Context::current());
        let attributes = attributes
            .into_iter()
            .filter(|a| allowed(a.key.as_str()))
            .collect::<Vec<_>>();
        span.set_attributes(attributes.clone());
        let context = Context::current().with_span(span);
        if !matches!(
            name,
            "app.start"
                | "task.open"
                | "course.open"
                | "lesson.open"
                | "javascript.error"
                | "javascript.rejection"
        ) {
            let mut start = tracer.start_with_context("operation.started", &context);
            start.set_attributes(attributes);
            start.set_attribute(KeyValue::new("operation.name", name));
            start.set_attribute(KeyValue::new("result.state", "running"));
            start.end();
        }
        context
    } else {
        Context::new()
    };
    Operation {
        context,
        ended: false,
    }
}
pub async fn observe<T>(
    name: &'static str,
    attributes: Vec<KeyValue>,
    future: impl std::future::Future<Output = Result<T, String>>,
) -> Result<T, String> {
    let mut span = operation(name, attributes);
    let result = future.with_context(span.context()).await;
    if let Err(error) = &result {
        span.error(error);
    }
    span.finish(if result.is_ok() { "ok" } else { "error" });
    result
}
pub fn observe_sync<T>(
    name: &'static str,
    attributes: Vec<KeyValue>,
    work: impl FnOnce() -> Result<T, String>,
) -> Result<T, String> {
    let mut span = operation(name, attributes);
    let result = {
        let _guard = span.context().attach();
        work()
    };
    if let Err(error) = &result {
        span.error(error);
    }
    span.finish(if result.is_ok() { "ok" } else { "error" });
    result
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
pub struct WebError {
    pub kind: String,
    pub name: String,
    pub file: String,
    pub line: u32,
    pub column: u32,
    #[serde(default)]
    pub course: String,
    #[serde(default)]
    pub lesson: String,
    #[serde(default)]
    pub task: String,
}
pub fn record_web_error(error: WebError) {
    let kind = match error.kind.as_str() {
        "error" => "javascript.error",
        "unhandledrejection" => "javascript.rejection",
        _ => return,
    };
    let name = match error.name.as_str() {
        "TypeError" | "RangeError" | "SyntaxError" | "ReferenceError" | "URIError"
        | "EvalError" | "AggregateError" => error.name,
        _ => "Error".into(),
    };
    let mut attributes = vec![
        KeyValue::new("exception.type", name),
        KeyValue::new("code.line", error.line.min(1_000_000) as i64),
        KeyValue::new("code.column", error.column.min(1_000_000) as i64),
    ];
    if error.file.len() <= 80
        && error.file.ends_with(".js")
        && error
            .file
            .bytes()
            .all(|c| c.is_ascii_alphanumeric() || b"._-".contains(&c))
    {
        attributes.push(KeyValue::new("code.file", error.file));
    }
    for (key, id) in [
        ("course.id", error.course),
        ("lesson.id", error.lesson),
        ("task.id", error.task),
    ] {
        if !id.is_empty()
            && id.len() <= 100
            && id
                .bytes()
                .all(|b| b.is_ascii_alphanumeric() || b"_-".contains(&b))
        {
            attributes.push(KeyValue::new(key, id));
        }
    }
    let mut span = operation(kind, attributes);
    span.finish("error");
}

pub fn flush() {
    if let Some(recorder) = RECORDER.get() {
        let _ = recorder.provider.force_flush();
    }
}

/// A diagnostic JSON snapshot of local spans, not an OTLP wire-format export.
pub fn export_recent() -> Result<String, String> {
    let records = if let Some(recorder) = RECORDER.get() {
        recorder.provider.force_flush().map_err(|e| e.to_string())?;
        recorder.store.recent()?
    } else {
        Store::open(&crate::data_dir()?.join("telemetry.sqlite3"))?.recent()?
    };
    serde_json::to_string_pretty(&serde_json::json!({"format":"mq.otel.local.v1","retention_seconds":3600,"navigation_retention_days":180,"spans":records})).map_err(|e|e.to_string())
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn sdk_exports_parentage_failure_and_only_allowed_attributes() {
        let root = tempfile::tempdir().unwrap();
        let guard = Guard::open(&root.path().join("telemetry.sqlite3")).unwrap();
        let tracer = guard.recorder.provider.tracer("test");
        let mut parent = tracer.start("lesson.load");
        let context = Context::new().with_remote_span_context(parent.span_context().clone());
        let mut child = tracer.start_with_context("python.import", &context);
        child.set_attributes([
            KeyValue::new("package.name", "tensorflow"),
            KeyValue::new("source.code", "SECRET"),
            KeyValue::new("authorization", "TOKEN"),
        ]);
        child.set_status(opentelemetry::trace::Status::error("timeout"));
        child.end();
        parent.end();
        guard.recorder.provider.force_flush().unwrap();
        let records = guard.recorder.store.recent().unwrap();
        assert_eq!(records.len(), 2);
        let child = records.iter().find(|r| r.name == "python.import").unwrap();
        let parent = records.iter().find(|r| r.name == "lesson.load").unwrap();
        assert_eq!(child.trace_id, parent.trace_id);
        assert_eq!(child.parent_span_id, parent.span_id);
        assert!(child.error);
        let json = serde_json::to_string(&records).unwrap();
        assert!(!json.contains("SECRET") && !json.contains("TOKEN"));
        assert!(json.contains("tensorflow"));
    }
    #[test]
    fn retention_bounds_age_count_and_reopen() {
        let root = tempfile::tempdir().unwrap();
        let path = root.path().join("telemetry.sqlite3");
        let store = Store::open(&path).unwrap();
        let mut connection = store.connection.lock().unwrap();
        let transaction = connection.transaction().unwrap();
        for _ in 0..MAX_RECORDS + 20 {
            transaction
                .execute(
                    "INSERT INTO spans(ended_ms,payload) VALUES(?1,'{}')",
                    [now()],
                )
                .unwrap();
        }
        transaction
            .execute(
                "INSERT INTO spans(ended_ms,payload) VALUES(?1,'expired')",
                [now() - RETENTION_MS - 1],
            )
            .unwrap();
        transaction.commit().unwrap();
        drop(connection);
        store.prune(now()).unwrap();
        let connection = store.connection.lock().unwrap();
        assert_eq!(
            connection
                .query_row("SELECT count(*) FROM spans", [], |r| r.get::<_, usize>(0))
                .unwrap(),
            MAX_RECORDS
        );
        assert_eq!(
            connection
                .query_row(
                    "SELECT count(*) FROM spans WHERE payload='expired'",
                    [],
                    |r| r.get::<_, usize>(0)
                )
                .unwrap(),
            0
        );
        connection
            .execute(
                "INSERT INTO spans(ended_ms,payload,navigation) VALUES(?1,'navigation',1)",
                [now() - 2 * RETENTION_MS],
            )
            .unwrap();
        drop(connection);
        drop(store);
        let reopened = Store::open(&path).unwrap();
        reopened.prune(now() + RETENTION_MS + 1).unwrap();
        assert_eq!(
            reopened
                .connection
                .lock()
                .unwrap()
                .query_row("SELECT count(*) FROM spans", [], |r| r.get::<_, usize>(0))
                .unwrap(),
            1
        );
        reopened.prune(now() + NAVIGATION_MS + 1).unwrap();
        assert_eq!(
            reopened
                .connection
                .lock()
                .unwrap()
                .query_row("SELECT count(*) FROM spans", [], |r| r.get::<_, usize>(0))
                .unwrap(),
            0
        );
    }
}
