//! Isolated GitHub transport for the debug validation course. Never falls through to gh.
use base64::Engine;
use serde_json::{json, Value};
use std::sync::{Mutex, OnceLock};

pub const REPOSITORY: &str = "mq3-validation/course";
pub fn enabled() -> bool { cfg!(debug_assertions) && std::env::var_os("MOLIP_PILOT").is_some() }

pub fn data_dir() -> Result<std::path::PathBuf, String> {
    static DIRECTORY: OnceLock<Result<tempfile::TempDir, String>> = OnceLock::new();
    DIRECTORY.get_or_init(|| tempfile::Builder::new().prefix("mq3-player-pilot-").tempdir().map_err(|error|error.to_string()))
        .as_ref().map(|directory|directory.path().to_path_buf()).map_err(Clone::clone)
}

struct Store { version: char, issue: Option<Value>, comments: Vec<Value> }
fn store() -> &'static Mutex<Store> {
    static STORE: OnceLock<Mutex<Store>> = OnceLock::new();
    STORE.get_or_init(|| Mutex::new(Store { version: 'a', issue: None, comments: vec![] }))
}
fn user() -> Value { json!({"id":987654321,"login":"mq3-validation"}) }

pub fn set_version(version: char) -> Result<(), String> {
    if !matches!(version,'a'|'b'|'c'|'d'|'e'|'f') { return Err("검증 버전을 확인하세요.".into()); }
    store().lock().map_err(|_|"검증 저장소 잠금 오류")?.version = version;
    Ok(())
}
fn snapshot(version: char, file: &str) -> Result<&'static str, String> {
    match (version, file) {
        ('a', "course.json") => Ok(include_str!("../tests/fixtures/player-pilot/a/course.json")),
        ('a', "lesson.json") => Ok(include_str!("../tests/fixtures/player-pilot/a/lesson.json")),
        ('b', "course.json") => Ok(include_str!("../tests/fixtures/player-pilot/b/course.json")),
        ('b', "lesson.json") => Ok(include_str!("../tests/fixtures/player-pilot/b/lesson.json")),
        ('c', "course.json") => Ok(include_str!("../tests/fixtures/player-pilot/c/course.json")),
        ('c', "lesson.json") => Ok(include_str!("../tests/fixtures/player-pilot/c/lesson.json")),
        ('f', "course.json") => Ok(include_str!("../tests/fixtures/player-pilot/f/course.json")),
        ('f', "lesson.json") => Ok(include_str!("../tests/fixtures/player-pilot/f/lesson.json")),
        ('e', "course.json") => Ok(include_str!("../tests/fixtures/player-pilot/e/course.json")),
        ('e', "lesson.json") => Ok(include_str!("../tests/fixtures/player-pilot/e/lesson.json")),
        ('d', "course.json") => Ok(include_str!("../tests/fixtures/player-pilot/d/course.json")),
        ('d', "lesson.json") => Ok(include_str!("../tests/fixtures/player-pilot/d/lesson.json")),
        _ => Err("검증용 콘텐츠만 불러올 수 있어요.".into()),
    }
}

pub fn request(args: &[&str], payload: Option<Value>) -> Result<Value, String> {
    if args.first() != Some(&"api") { return Err("검증 모드에서는 외부 gh 명령을 실행하지 않아요.".into()); }
    let mut method = "GET";
    let mut route = None;
    let mut index = 1;
    while index < args.len() {
        match args[index] {
            "--method" => { method = args.get(index+1).copied().ok_or("요청 방식 오류")?; index += 2; }
            "--hostname" | "--input" => index += 2,
            value if value.starts_with('-') => return Err("검증 요청 옵션을 확인하세요.".into()),
            value => { if route.replace(value).is_some() { return Err("검증 요청 경로 오류".into()); } index += 1; }
        }
    }
    let route = route.ok_or("검증 요청 경로가 없어요.")?.trim_start_matches('/');
    if method == "GET" && route == "user" { return Ok(user()); }
    let mut state = store().lock().map_err(|_|"검증 저장소 잠금 오류")?;
    for (repository, file) in [(REPOSITORY,"course.json"),("mq3-validation/lesson","lesson.json")] {
        let prefix = format!("repos/{repository}/contents/{file}?ref=");
        if method == "GET" { if let Some(revision) = route.strip_prefix(&prefix) {
            let version = if file == "course.json" && revision == "main" { state.version } else {
                match revision { "pilot-a" => 'a', "pilot-b" => 'b', "pilot-c" => 'c', "pilot-d" => 'd', "pilot-e" => 'e', "pilot-f" => 'f', _ => return Err("검증 콘텐츠 버전 오류".into()) }
            };
            let raw = snapshot(version,file)?;
            return Ok(json!({"size":raw.len(),"encoding":"base64","content":base64::engine::general_purpose::STANDARD.encode(raw)}));
        } }
    }
    let base = format!("repos/{REPOSITORY}/issues");
    if method == "GET" && route.starts_with(&format!("{base}?")) {
        return Ok(Value::Array(state.issue.iter().cloned().collect()));
    }
    if method == "GET" && route.starts_with(&format!("{base}/1/comments?")) {
        return Ok(Value::Array(state.comments.clone()));
    }
    let payload = payload.unwrap_or(Value::Null);
    if method == "POST" && route == base {
        let issue = json!({"number":1,"html_url":"https://github.com/mq3-validation/course/issues/1","user":user(),"title":payload["title"],"body":payload["body"]});
        state.issue = Some(issue.clone());
        return Ok(issue);
    }
    if method == "POST" && route == format!("{base}/1/comments") {
        let comment = json!({"body":payload["body"],"user":user()});
        state.comments.push(comment.clone());
        return Ok(comment);
    }
    if method == "PATCH" && route == format!("{base}/1") {
        let issue = state.issue.as_mut().ok_or("검증 진도 이슈가 없어요.")?;
        if let Some(body) = payload.get("body") { issue["body"] = body.clone(); }
        return Ok(issue.clone());
    }
    Err("검증용 코스 이외의 요청은 차단했어요.".into())
}
