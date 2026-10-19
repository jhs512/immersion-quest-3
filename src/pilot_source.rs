//! Isolated GitHub transport for the debug validation course. Never falls through to gh.
use base64::Engine;
use serde_json::{json, Value};
use std::sync::{Mutex, OnceLock};

pub const REPOSITORY: &str = "mq3-validation/course";
pub fn enabled() -> bool { cfg!(debug_assertions) && std::env::var_os("MOLIP_PILOT").is_some() }

pub fn data_dir() -> Result<std::path::PathBuf, String> {
    if let Some(directory)=crate::pilot_session::shared_directory()? {return Ok(directory)}
    static DIRECTORY: OnceLock<Result<tempfile::TempDir, String>> = OnceLock::new();
    DIRECTORY.get_or_init(|| tempfile::Builder::new().prefix("mq3-player-pilot-").tempdir().map_err(|error|error.to_string()))
        .as_ref().map(|directory|directory.path().to_path_buf()).map_err(Clone::clone)
}

#[derive(Clone,serde::Serialize,serde::Deserialize)]
struct Store { corrupted:bool, version: char, issue: Option<Value>, comments: Vec<Value> }
impl Store {
    fn load()->Result<Self,String> {
        match std::fs::read(data_dir()?.join("pilot-remote.json")) {
            Ok(raw) if raw.len()<=8_000_000=>serde_json::from_slice(&raw).map_err(|e|e.to_string()),
            Ok(_)=>Err("검증 데이터가 너무 커요.".into()),
            Err(error) if error.kind()==std::io::ErrorKind::NotFound=>Ok(Self{corrupted:false,version:'a',issue:None,comments:vec![]}),
            Err(error)=>Err(error.to_string()),
        }
    }
    fn save(&self)->Result<(),String> {
        use std::io::Write;
        let directory=data_dir()?;
        let mut pending=tempfile::NamedTempFile::new_in(&directory).map_err(|e|e.to_string())?;
        pending.write_all(&serde_json::to_vec(self).map_err(|e|e.to_string())?).map_err(|e|e.to_string())?;
        pending.as_file().sync_all().map_err(|e|e.to_string())?;
        pending.persist(directory.join("pilot-remote.json")).map_err(|e|e.to_string())?;
        Ok(())
    }
}
fn commit<T>(state:&mut Store,update:impl FnOnce(&mut Store)->Result<T,String>)->Result<T,String> {
    let mut next=state.clone();let result=update(&mut next)?;next.save()?;*state=next;Ok(result)
}
fn store() -> Result<&'static Mutex<Store>,String> {
    static STORE: OnceLock<Result<Mutex<Store>,String>> = OnceLock::new();
    STORE.get_or_init(||Store::load().map(Mutex::new)).as_ref().map_err(Clone::clone)
}
fn user() -> Value { json!({"id":987654321,"login":"mq3-validation"}) }

pub fn set_version(version: char) -> Result<(), String> {
    if !matches!(version,'a'|'b'|'c'|'d'|'e'|'f'|'g'|'h'|'i'|'j'|'k'|'l'|'m'|'n'|'o'|'p'|'q'|'r'|'s'|'t'|'u'|'v'|'w'|'x'|'y'|'z'|'1'|'2'|'3'|'4'|'5'|'6'|'7'|'8'|'9'|'가'|'나'|'다'|'0') { return Err("검증 버전을 확인하세요.".into()); }
    let mut state=store()?.lock().map_err(|_|"검증 저장소 잠금 오류")?;
    commit(&mut state,|next|{next.version=version;next.corrupted=false;Ok(())})
}
pub fn corrupt_update()->Result<(),String> {
    let mut state=store()?.lock().map_err(|_|"검증 저장소 잠금 오류")?;
    commit(&mut state,|next|{next.version='b';next.corrupted=true;Ok(())})
}
fn snapshot(version: char, file: &str) -> Result<&'static str, String> {
    match (version, file) {
        ('다', "course.json") => Ok(include_str!("../tests/fixtures/player-pilot/다/course.json")),
        ('다', "lesson.json") => Ok(include_str!("../courses/redesigned/aice-regression-metrics.json")),
        ('나', "course.json") => Ok(include_str!("../tests/fixtures/player-pilot/나/course.json")),
        ('나', "lesson.json") => Ok(include_str!("../courses/redesigned/aice-regression.json")),
        ('가', "course.json") => Ok(include_str!("../tests/fixtures/player-pilot/가/course.json")),
        ('가', "lesson.json") => Ok(include_str!("../courses/redesigned/aice-scale.json")),
        ('9', "course.json") => Ok(include_str!("../tests/fixtures/player-pilot/9/course.json")),
        ('9', "lesson.json") => Ok(include_str!("../courses/redesigned/aice-leakage.json")),
        ('8', "course.json") => Ok(include_str!("../tests/fixtures/player-pilot/8/course.json")),
        ('8', "lesson.json") => Ok(include_str!("../courses/redesigned/aice-split.json")),
        ('7', "course.json") => Ok(include_str!("../tests/fixtures/player-pilot/7/course.json")),
        ('7', "lesson.json") => Ok(include_str!("../courses/redesigned/aice-features.json")),
        ('6', "course.json") => Ok(include_str!("../tests/fixtures/player-pilot/6/course.json")),
        ('6', "lesson.json") => Ok(include_str!("../courses/redesigned/java-static.json")),
        ('5', "course.json") => Ok(include_str!("../tests/fixtures/player-pilot/5/course.json")),
        ('5', "lesson.json") => Ok(include_str!("../courses/redesigned/engineer-c-structures.json")),
        ('4', "course.json") => Ok(include_str!("../tests/fixtures/player-pilot/4/course.json")),
        ('4', "lesson.json") => Ok(include_str!("../courses/redesigned/engineer-c-double-pointers.json")),
        ('3', "course.json") => Ok(include_str!("../tests/fixtures/player-pilot/3/course.json")),
        ('3', "lesson.json") => Ok(include_str!("../courses/redesigned/java-references.json")),
        ('2', "course.json") => Ok(include_str!("../tests/fixtures/player-pilot/2/course.json")),
        ('2', "lesson.json") => Ok(include_str!("../courses/redesigned/aice-plots.json")),
        ('1', "course.json") => Ok(include_str!("../tests/fixtures/player-pilot/1/course.json")),
        ('1', "lesson.json") => Ok(include_str!("../courses/redesigned/engineer-c-pointers.json")),
        ('0', "course.json") => Ok(include_str!("../tests/fixtures/player-pilot/0/course.json")),
        ('0', "lesson.json") => Ok(include_str!("../courses/redesigned/java-methods.json")),
        ('y', "course.json") => Ok(include_str!("../tests/fixtures/player-pilot/y/course.json")),
        ('y', "lesson.json") => Ok(include_str!("../courses/redesigned/aice-quality.json")),
        ('z', "course.json") => Ok(include_str!("../tests/fixtures/player-pilot/z/course.json")),
        ('z', "lesson.json") => Ok(include_str!("../courses/redesigned/engineer-c-functions.json")),
        ('x', "course.json") => Ok(include_str!("../tests/fixtures/player-pilot/x/course.json")),
        ('x', "lesson.json") => Ok(include_str!("../courses/redesigned/engineer-c-arrays.json")),
        ('v', "course.json") => Ok(include_str!("../tests/fixtures/player-pilot/v/course.json")),
        ('v', "lesson.json") => Ok(include_str!("../courses/redesigned/aice-selection.json")),
        ('w', "course.json") => Ok(include_str!("../tests/fixtures/player-pilot/w/course.json")),
        ('w', "lesson.json") => Ok(include_str!("../courses/redesigned/java-arrays.json")),
        ('t', "course.json") => Ok(include_str!("../tests/fixtures/player-pilot/t/course.json")),
        ('t', "lesson.json") => Ok(include_str!("../courses/redesigned/java-conditions.json")),
        ('u', "course.json") => Ok(include_str!("../tests/fixtures/player-pilot/u/course.json")),
        ('u', "lesson.json") => Ok(include_str!("../courses/redesigned/engineer-c-conditions.json")),
        ('s', "course.json") => Ok(include_str!("../tests/fixtures/player-pilot/s/course.json")),
        ('s', "lesson.json") => Ok(include_str!("../courses/redesigned/aice-python-api.json")),
        ('r', "course.json") => Ok(include_str!("../tests/fixtures/player-pilot/r/course.json")),
        ('r', "lesson.json") => Ok(include_str!("../courses/redesigned/engineer-c-start.json")),
        ('q', "course.json") => Ok(include_str!("../tests/fixtures/player-pilot/q/course.json")),
        ('q', "lesson.json") => Ok(include_str!("../courses/redesigned/aice-table-csv.json")),
        ('p', "course.json") => Ok(include_str!("../tests/fixtures/player-pilot/p/course.json")),
        ('p', "lesson.json") => Ok(include_str!("../courses/redesigned/aice-python-conditions.json")),
        ('o', "course.json") => Ok(include_str!("../tests/fixtures/player-pilot/o/course.json")),
        ('o', "lesson.json") => Ok(include_str!("../courses/redesigned/aice-python-start.json")),
        ('n', "course.json") => Ok(include_str!("../tests/fixtures/player-pilot/n/course.json")),
        ('n', "lesson.json") => Ok(include_str!("../courses/redesigned/java-values.json")),
        ('m', "course.json") => Ok(include_str!("../tests/fixtures/player-pilot/m/course.json")),
        ('m', "lesson.json") => Ok(include_str!("../tests/fixtures/player-pilot/m/lesson.json")),
        ('l', "course.json") => Ok(include_str!("../tests/fixtures/player-pilot/l/course.json")),
        ('l', "lesson.json") => Ok(include_str!("../courses/redesigned/git-branch.json")),
        ('k', "course.json") => Ok(include_str!("../tests/fixtures/player-pilot/k/course.json")),
        ('k', "lesson.json") => Ok(include_str!("../courses/redesigned/git-first.json")),
        ('j', "course.json") => Ok(include_str!("../tests/fixtures/player-pilot/j/course.json")),
        ('j', "lesson.json") => Ok(include_str!("../tests/fixtures/player-pilot/j/lesson.json")),
        ('a', "course.json") => Ok(include_str!("../tests/fixtures/player-pilot/a/course.json")),
        ('a', "lesson.json") => Ok(include_str!("../tests/fixtures/player-pilot/a/lesson.json")),
        ('i', "course.json") => Ok(include_str!("../tests/fixtures/player-pilot/i/course.json")),
        ('i', "lesson.json") => Ok(include_str!("../tests/fixtures/player-pilot/i/lesson.json")),
        ('b', "course.json") => Ok(include_str!("../tests/fixtures/player-pilot/b/course.json")),
        ('b', "lesson.json") => Ok(include_str!("../tests/fixtures/player-pilot/b/lesson.json")),
        ('c', "course.json") => Ok(include_str!("../tests/fixtures/player-pilot/c/course.json")),
        ('c', "lesson.json") => Ok(include_str!("../tests/fixtures/player-pilot/c/lesson.json")),
        ('h', "course.json") => Ok(include_str!("../tests/fixtures/player-pilot/h/course.json")),
        ('h', "lesson.json") => Ok(include_str!("../tests/fixtures/player-pilot/h/lesson.json")),
        ('g', "course.json") => Ok(include_str!("../tests/fixtures/player-pilot/g/course.json")),
        ('g', "lesson.json") => Ok(include_str!("../tests/fixtures/player-pilot/g/lesson.json")),
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
    let mut state = store()?.lock().map_err(|_|"검증 저장소 잠금 오류")?;
    for (repository, file) in [(REPOSITORY,"course.json"),("mq3-validation/lesson","lesson.json")] {
        let prefix = format!("repos/{repository}/contents/{file}?ref=");
        if method == "GET" { if let Some(revision) = route.strip_prefix(&prefix) {
            let version = if file == "course.json" && revision == "main" { state.version } else {
                match revision { "pilot-a" => 'a', "pilot-b" => 'b', "pilot-c" => 'c', "pilot-d" => 'd', "pilot-e" => 'e', "pilot-f" => 'f', "pilot-g" => 'g', "pilot-h" => 'h', "pilot-i" => 'i', "pilot-j" => 'j', "git-first-1" => 'k', "git-branch-1" => 'l', "pilot-m" => 'm', "java-values-1" => 'n', "aice-python-start-1" => 'o', "aice-python-conditions-1" => 'p', "aice-table-csv-1" => 'q', "engineer-c-start-1" => 'r', "aice-python-api-1" => 's', "java-conditions-1" => 't', "engineer-c-conditions-1" => 'u', "aice-selection-1" => 'v', "java-arrays-1" => 'w', "engineer-c-arrays-1" => 'x', "aice-quality-1" => 'y', "engineer-c-functions-1" => 'z', "engineer-c-pointers-1" => '1', "aice-plots-1" => '2', "java-references-1" => '3', "engineer-c-double-pointers-1" => '4', "engineer-c-structures-1" => '5', "java-static-1" => '6', "aice-features-1" => '7', "aice-split-1" => '8', "aice-leakage-1" => '9', "aice-scale-1" => '가', "aice-regression-1" => '나', "aice-regression-metrics-1" => '다', "java-methods-1" => '0', _ => return Err("검증 콘텐츠 버전 오류".into()) }
            };
            let raw = snapshot(version,file)?;
            let damaged=if state.corrupted && file=="lesson.json" {format!("{raw} ")}else{raw.to_owned()};
            let raw=damaged;
            return Ok(json!({"size":raw.len(),"encoding":"base64","content":base64::engine::general_purpose::STANDARD.encode(raw.as_bytes())}));
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
        return commit(&mut state,|next|{next.issue=Some(issue.clone());Ok(issue)});
    }
    if method == "POST" && route == format!("{base}/1/comments") {
        let comment = json!({"body":payload["body"],"user":user()});
        return commit(&mut state,|next|{next.comments.push(comment.clone());Ok(comment)});
    }
    if method == "PATCH" && route == format!("{base}/1") {
        return commit(&mut state,|next|{
            let issue=next.issue.as_mut().ok_or("검증 진도 이슈가 없어요.")?;
            if let Some(body)=payload.get("body"){issue["body"]=body.clone();}
            Ok(issue.clone())
        });
    }
    Err("검증용 코스 이외의 요청은 차단했어요.".into())
}
