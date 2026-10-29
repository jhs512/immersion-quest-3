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
struct Store { corrupted:bool, version: char, issue: Option<Value>, comments: Vec<Value>, #[serde(default)] enrollments:Vec<Value> }
impl Store {
    fn load()->Result<Self,String> {
        match std::fs::read(data_dir()?.join("pilot-remote.json")) {
            Ok(raw) if raw.len()<=8_000_000=>serde_json::from_slice(&raw).map_err(|e|e.to_string()),
            Ok(_)=>Err("검증 데이터가 너무 커요.".into()),
            Err(error) if error.kind()==std::io::ErrorKind::NotFound=>Ok(Self{corrupted:false,version:'a',issue:None,comments:vec![],enrollments:vec![]}),
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

const LEGACY_VERSIONS: &[char] = &['a','b','c','d','e','f','g','h','i','j','m'];
pub fn versions()->Vec<char> { LEGACY_VERSIONS.iter().copied().chain(crate::lesson_registry::LESSONS.iter().map(|row|row.pilot)).chain([AUTO_CHAIN_VERSION,MAIN_COURSE_VERSION,CATEGORY_PREVIEW_VERSION,AICE_COURSE_VERSION,ENGINEER_COURSE_VERSION]).collect() }
/// Whole-course UI checks for both certification courses, still using only the isolated transport.
pub const AICE_COURSE_VERSION: char = '에';
pub const ENGINEER_COURSE_VERSION: char = '정';
fn certification_course_source(version: char) -> Result<&'static str, String> {
    static AICE: OnceLock<Result<String, String>> = OnceLock::new();
    static ENGINEER: OnceLock<Result<String, String>> = OnceLock::new();
    let (cache, raw) = if version == AICE_COURSE_VERSION {
        (&AICE, include_str!("../courses/redesigned-courses/aice-associate.json"))
    } else if version == ENGINEER_COURSE_VERSION {
        (&ENGINEER, include_str!("../courses/redesigned-courses/engineer-practical.json"))
    } else {return Err("검증 과정 버전을 확인하세요.".into())};
    cache.get_or_init(|| {
        let mut course: Value = serde_json::from_str(raw).map_err(|e|e.to_string())?;
        course["repository"] = REPOSITORY.into();
        for reference in course["lessons"].as_array_mut().ok_or("검증 과정 형식 오류")? {
            reference["repository"] = "mq3-validation/lesson".into();
        }
        serde_json::to_string(&course).map_err(|e|e.to_string())
    }).as_ref().map(String::as_str).map_err(Clone::clone)
}
/// Design validation: the bundled 자바 백엔드 과정 (all its lessons, labels and order) served through
/// this isolated transport, so the real course screens can be inspected without an account.
pub const MAIN_COURSE_VERSION: char = '본';
/// The same course with the unapproved category proposal applied, only to render the grouped list.
pub const CATEGORY_PREVIEW_VERSION: char = '분';
fn main_course(categories: bool) -> Result<String, String> {
    let mut course: Value = serde_json::from_str(include_str!("../courses/redesigned-courses/java-backend.json")).map_err(|e| e.to_string())?;
    course["id"] = "crs_3f59e7bd-70c1-4e81-9cb0-000000000001".into();
    course["repository"] = REPOSITORY.into();
    let proposal: Value = serde_json::from_str(include_str!("../tools/redesigned_courses/lesson-classification.json")).map_err(|e| e.to_string())?;
    if categories { course["categories"] = proposal["courses"]["java"]["categories"].clone(); }
    for lesson in course["lessons"].as_array_mut().ok_or("검증 코스 형식 오류")? {
        let key = lesson["repository"].as_str().unwrap_or("").trim_start_matches("jhs512/mq3-lesson-redesigned-").to_owned();
        lesson["repository"] = "mq3-validation/lesson".into();
        if categories { if let Some(id) = proposal["courses"]["java"]["lessons"][&key]["category"].as_str() { lesson["category"] = id.into(); } }
    }
    serde_json::to_string(&course).map_err(|e| e.to_string())
}
fn main_course_source(categories: bool) -> Result<&'static str, String> {
    static PLAIN: OnceLock<Result<String, String>> = OnceLock::new();
    static GROUPED: OnceLock<Result<String, String>> = OnceLock::new();
    (if categories { &GROUPED } else { &PLAIN }).get_or_init(|| main_course(categories)).as_ref().map(String::as_str).map_err(Clone::clone)
}
/// 관리자 자동 풀이 validation: one course with two registered lessons (Bash, then Java), so a
/// run can be seen moving from one lesson to the next. It reuses the registered lesson files.
pub const AUTO_CHAIN_VERSION: char = '연';
fn auto_chain_course() -> Result<&'static str, String> {
    static COURSE: OnceLock<Result<String, String>> = OnceLock::new();
    COURSE.get_or_init(|| {
        let mut course: Value = serde_json::from_str(crate::lesson_registry::find("bash-basics").ok_or("Bash 검증 수업이 없어요.")?.course).map_err(|e| e.to_string())?;
        let java: Value = serde_json::from_str(crate::lesson_registry::find("java-launch").ok_or("자바 검증 수업이 없어요.")?.course).map_err(|e| e.to_string())?;
        course["lessons"].as_array_mut().ok_or("검증 코스 형식 오류")?.extend(java["lessons"].as_array().cloned().unwrap_or_default());
        serde_json::to_string(&course).map_err(|e| e.to_string())
    }).as_ref().map(String::as_str).map_err(Clone::clone)
}

pub fn set_version(version: char) -> Result<(), String> {
    if !versions().contains(&version) { return Err("검증 버전을 확인하세요.".into()); }
    let mut state=store()?.lock().map_err(|_|"검증 저장소 잠금 오류")?;
    commit(&mut state,|next|{next.version=version;next.corrupted=false;Ok(())})
}
pub fn corrupt_update()->Result<(),String> {
    let mut state=store()?.lock().map_err(|_|"검증 저장소 잠금 오류")?;
    commit(&mut state,|next|{next.version='b';next.corrupted=true;Ok(())})
}
fn snapshot(version: char, file: &str) -> Result<&'static str, String> {
    if matches!(version, AICE_COURSE_VERSION | ENGINEER_COURSE_VERSION) && file == "course.json" { return certification_course_source(version); }
    if version == AUTO_CHAIN_VERSION && file == "course.json" { return auto_chain_course(); }
    if matches!(version, MAIN_COURSE_VERSION | CATEGORY_PREVIEW_VERSION) && file == "course.json" { return main_course_source(version == CATEGORY_PREVIEW_VERSION); }
    if let Some(lesson)=crate::lesson_registry::by_version(version) {
        return match file {"course.json"=>Ok(lesson.course),"lesson.json"=>Ok(lesson.lesson),_=>Err("검증 파일을 확인하세요.".into())};
    }
    match (version, file) {
        ('m', "course.json") => Ok(include_str!("../tests/fixtures/player-pilot/m/course.json")),
        ('m', "lesson.json") => Ok(include_str!("../tests/fixtures/player-pilot/m/lesson.json")),
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
    // Fault injection exists only in this isolated debug transport.
    if method=="POST"&&route.ends_with("/comments")&&data_dir()?.join("pilot-progress-blocked").exists(){
        use std::io::Write;
        let mut log=std::fs::OpenOptions::new().create(true).append(true).open(data_dir()?.join("pilot-progress-attempts")).map_err(|e|e.to_string())?;
        writeln!(log,"blocked").map_err(|e|e.to_string())?;
        return Err("Injected progress upload outage".into());
    }
    // Progress reads (issue lists and their comments) can be slowed down or cut off, to show
    // that the catalog never waits for them. Each read is logged before it is served.
    if method=="GET"&&route.starts_with(&format!("repos/{REPOSITORY}/issues")){
        use std::io::Write;
        let directory=data_dir()?;
        let mut log=std::fs::OpenOptions::new().create(true).append(true).open(directory.join("pilot-remote-reads")).map_err(|e|e.to_string())?;
        writeln!(log,"{route}").map_err(|e|e.to_string())?;
        if let Some(delay)=std::fs::read_to_string(directory.join("pilot-remote-read-delay-ms")).ok().and_then(|raw|raw.trim().parse::<u64>().ok()){
            std::thread::sleep(std::time::Duration::from_millis(delay.min(30_000)));
        }
        if directory.join("pilot-remote-offline").exists(){return Err("Injected progress read outage".into());}
    }

    // 도전 과제: reviewer permission and a future-problem fixture are files in the isolated data folder.
    if method == "GET" && route == format!("repos/{REPOSITORY}") {
        return Ok(json!({"full_name":REPOSITORY,"permissions":{"pull":true,"push":data_dir()?.join("pilot-course-reviewer").exists()}}));
    }
    if method == "GET" && route == format!("repos/{REPOSITORY}/contents/{}?ref=main",crate::challenges::FUTURE_FILE) {
        let raw=std::fs::read_to_string(data_dir()?.join("pilot-future-challenges.json")).map_err(|_|"gh: Not Found (HTTP 404)".to_string())?;
        return Ok(json!({"size":raw.len(),"encoding":"base64","content":base64::engine::general_purpose::STANDARD.encode(raw.as_bytes())}));
    }
    let mut state = store()?.lock().map_err(|_|"검증 저장소 잠금 오류")?;
    for (repository, file) in [(REPOSITORY,"course.json"),("mq3-validation/lesson","lesson.json")] {
        let prefix = format!("repos/{repository}/contents/{file}?ref=");
        if method == "GET" { if let Some(revision) = route.strip_prefix(&prefix) {
            let version = if file == "course.json" && revision == "main" { state.version } else {
                crate::lesson_registry::by_revision(revision).map(|row|row.pilot).or_else(|| {
                    let suffix=revision.strip_prefix("pilot-")?;
                    let mut chars=suffix.chars();let version=chars.next()?;
                    (chars.next().is_none()&&LEGACY_VERSIONS.contains(&version)).then_some(version)
                }).ok_or("검증 콘텐츠 버전 오류")?
            };
            let raw = snapshot(version,file)?;
            let damaged=if state.corrupted && file=="lesson.json" {format!("{raw} ")}else{raw.to_owned()};
            let raw=damaged;
            return Ok(json!({"size":raw.len(),"encoding":"base64","content":base64::engine::general_purpose::STANDARD.encode(raw.as_bytes())}));
        } }
    }
    let base = format!("repos/{REPOSITORY}/issues");
    if method == "GET" && route.starts_with(&format!("{base}?")) {
        return Ok(Value::Array(state.issue.iter().cloned().chain(state.enrollments.clone()).collect()));
    }
    if method == "GET" && route.starts_with(&format!("{base}/1/comments?")) {
        let query = route.split_once('?').map(|(_, query)| query).unwrap_or("");
        let number = |name: &str, default: usize| -> Result<usize, String> {
            match query.split('&').filter_map(|part| part.split_once('=')).find(|(key, _)| *key == name) {
                None => Ok(default),
                Some((_, value)) => value.parse::<usize>().ok().filter(|value| *value > 0)
                    .ok_or_else(|| "검증 댓글 페이지를 확인하세요.".into()),
            }
        };
        let page = number("page", 1)?;
        let per_page = number("per_page", 30)?.min(100);
        let offset = page.saturating_sub(1).saturating_mul(per_page);
        return Ok(Value::Array(state.comments.iter().skip(offset).take(per_page).cloned().collect()));
    }
    let payload = payload.unwrap_or(Value::Null);
    if method == "POST" && route == base && payload["body"].as_str().is_some_and(|b|b.contains("<!-- mq3-enrollment:")) {
        let number=1000+state.enrollments.len();
        let issue=json!({"number":number,"html_url":format!("https://github.com/mq3-validation/course/issues/{number}"),"user":user(),"title":payload["title"],"body":payload["body"]});
        return commit(&mut state,|next|{next.enrollments.push(issue.clone());Ok(issue)});
    }
    if method == "PATCH" {if let Some(number)=route.strip_prefix(&format!("{base}/")).and_then(|n|n.parse::<u64>().ok()).filter(|n|*n>=1000) {
        return commit(&mut state,|next|{let issue=next.enrollments.iter_mut().find(|i|i["number"].as_u64()==Some(number)).ok_or("검증 등록 이슈 없음")?;issue["body"]=payload["body"].clone();issue["title"]=payload["title"].clone();Ok(issue.clone())});
    }}
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
