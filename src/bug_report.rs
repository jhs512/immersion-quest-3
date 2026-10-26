//! User-confirmed reports through gh. Payload files use an unlisted Gist, not an upload server.
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::{
    io::Write,
    path::{Path, PathBuf},
};

pub const PLAYER_REPOSITORY: &str = "jhs512/immersion-quest-3";
#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct Location {
    pub course_id: String,
    pub course_title: String,
    pub lesson_id: String,
    pub lesson_title: String,
    pub lesson_repository: String,
    pub revision: String,
    pub task_id: String,
    pub task_title: String,
}
pub fn forget() {
    if let Ok(root) = crate::data_dir() {
        let _ =
            std::fs::remove_file(root.join(format!("report-location-{}.json", std::process::id())));
    }
}
pub fn remember(location: &Location) {
    if let Ok(root) = crate::data_dir() {
        let _ = atomic_json(
            &root.join(format!("report-location-{}.json", std::process::id())),
            location,
        );
    }
}
fn atomic_json(path: &Path, value: &impl Serialize) -> Result<(), String> {
    let mut pending = tempfile::NamedTempFile::new_in(path.parent().ok_or("report path")?)
        .map_err(|e| e.to_string())?;
    pending
        .write_all(&serde_json::to_vec(value).map_err(|e| e.to_string())?)
        .map_err(|e| e.to_string())?;
    pending.persist(path).map_err(|e| e.to_string())?;
    Ok(())
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Draft {
    pub id: String,
    pub kind: String,
    pub repository: String,
    pub location: Location,
    pub created_at: u64,
    pub build: String,
    pub os: String,
    pub architecture: String,
    #[serde(with = "compressed_snapshot")]
    pub diagnostics: Value,
    pub description: String,
    pub include_screen: bool,
    pub gist: Option<String>,
    pub issue: Option<String>,
    #[serde(default)]
    pub reporter: Option<u64>,
}
mod compressed_snapshot {
    use super::*;
    use base64::Engine;
    use serde::{Deserializer, Serializer};
    use std::io::Read;
    pub fn serialize<S: Serializer>(value: &Value, serializer: S) -> Result<S::Ok, S::Error> {
        let mut encoder = flate2::write::GzEncoder::new(Vec::new(), flate2::Compression::default());
        serde_json::to_writer(&mut encoder, value).map_err(serde::ser::Error::custom)?;
        let bytes = encoder.finish().map_err(serde::ser::Error::custom)?;
        serializer.serialize_str(&base64::engine::general_purpose::STANDARD.encode(bytes))
    }
    pub fn deserialize<'de, D: Deserializer<'de>>(deserializer: D) -> Result<Value, D::Error> {
        let text = String::deserialize(deserializer)?;
        let bytes = base64::engine::general_purpose::STANDARD
            .decode(text)
            .map_err(serde::de::Error::custom)?;
        let mut output = String::new();
        flate2::read::GzDecoder::new(&bytes[..])
            .take(80_000_001)
            .read_to_string(&mut output)
            .map_err(serde::de::Error::custom)?;
        if output.len() > 80_000_000 {
            return Err(serde::de::Error::custom("diagnostic snapshot too large"));
        }
        serde_json::from_str(&output).map_err(serde::de::Error::custom)
    }
}
fn prune_reports(root: &Path) -> Result<(), String> {
    let canonical = root.canonicalize().map_err(|e| e.to_string())?;
    let mut entries = std::fs::read_dir(root)
        .map_err(|e| e.to_string())?
        .filter_map(Result::ok)
        .filter(|entry| {
            let name = entry.file_name();
            let name = name.to_string_lossy();
            name.len() == 32
                && name.bytes().all(|b| b.is_ascii_hexdigit())
                && entry
                    .file_type()
                    .is_ok_and(|t| t.is_dir() && !t.is_symlink())
        })
        .collect::<Vec<_>>();
    entries
        .sort_by_key(|entry| std::cmp::Reverse(entry.metadata().and_then(|m| m.modified()).ok()));
    for entry in entries.into_iter().skip(9) {
        // Only app-generated report folders, checked as absolute paths before removal.
        let path = entry.path().canonicalize().map_err(|e| e.to_string())?;
        if path.parent() == Some(canonical.as_path()) {
            std::fs::remove_dir_all(path).map_err(|e| e.to_string())?;
        }
    }
    Ok(())
}
pub fn prepare(parent: u32, kind: &str) -> Result<PathBuf, String> {
    let root = crate::data_dir()?;
    let reports = root.join("bug-reports");
    std::fs::create_dir_all(&reports).map_err(|e| e.to_string())?;
    prune_reports(&reports)?;
    let location = std::fs::read(root.join(format!("report-location-{parent}.json")))
        .ok()
        .and_then(|b| serde_json::from_slice::<Location>(&b).ok())
        .unwrap_or_default();
    let repository = if kind == "content" {
        if !crate::repository_course::valid_repository(&location.lesson_repository) {
            return Err("열린 수업이 없어요. 문제 신고는 수업 안에서 사용하세요.".into());
        }
        location.lesson_repository.clone()
    } else {
        PLAYER_REPOSITORY.into()
    };
    let diagnostics = crate::telemetry::export_recent()
        .ok()
        .and_then(|s| serde_json::from_str(&s).ok())
        .unwrap_or_else(|| json!({"spans":[],"diagnostic_status":"unavailable"}));
    let id = crate::issue_progress::new_id();
    let folder = reports.join(&id);
    std::fs::create_dir(&folder).map_err(|e| e.to_string())?;
    let draft = Draft {
        id,
        kind: if kind == "content" { "content" } else { "bug" }.into(),
        repository,
        location,
        created_at: crate::issue_progress::now(),
        build: option_env!("MOLIP_BUILD")
            .filter(|value| !value.is_empty())
            .unwrap_or("development")
            .into(),
        os: std::env::consts::OS.into(),
        architecture: std::env::consts::ARCH.into(),
        diagnostics,
        description: String::new(),
        include_screen: true,
        gist: None,
        issue: None,
        reporter: None,
    };
    let path = folder.join("draft.json");
    save(&path, &draft)?;
    Ok(path)
}
pub fn load(path: &Path) -> Result<Draft, String> {
    serde_json::from_slice(&std::fs::read(path).map_err(|e| e.to_string())?)
        .map_err(|e| e.to_string())
}
pub fn save(path: &Path, draft: &Draft) -> Result<(), String> {
    atomic_json(path, draft)
}

/// Called in a disposable capture child so a hung window cannot hang the report dialog.
#[cfg(any(target_os = "windows", target_os = "macos"))]
pub fn capture(parent: u32, path: &Path) -> Result<(), String> {
    let window = xcap::Window::all()
        .map_err(|e| e.to_string())?
        .into_iter()
        .filter(|w| {
            w.pid().ok() == Some(parent)
                && w.title().is_ok_and(|t| t == "MQ")
                && !w.is_minimized().unwrap_or(true)
        })
        .max_by_key(|w| w.width().unwrap_or(0) as u64 * w.height().unwrap_or(0) as u64)
        .ok_or("MQ window unavailable")?;
    let image = window.capture_image().map_err(|e| e.to_string())?;
    if image.width() as u64 * image.height() as u64 > 32_000_000 {
        return Err("capture too large".into());
    }
    let image = xcap::image::DynamicImage::ImageRgba8(image).thumbnail(1600, 1200);
    let mut data = std::io::Cursor::new(Vec::new());
    image
        .write_to(&mut data, xcap::image::ImageFormat::Png)
        .map_err(|e| e.to_string())?;
    if data.get_ref().len() > 4_000_000 {
        return Err("capture too large".into());
    }
    std::fs::write(path, data.into_inner()).map_err(|e| e.to_string())
}

fn files(draft: &Draft, screen: &Path) -> Result<Value, String> {
    use base64::Engine;
    let mut encoder = flate2::write::GzEncoder::new(Vec::new(), flate2::Compression::default());
    serde_json::to_writer(&mut encoder, &draft.diagnostics).map_err(|e| e.to_string())?;
    let compressed = encoder.finish().map_err(|e| e.to_string())?;
    if compressed.len() > 8_000_000 {
        return Err("진단 파일이 너무 커요.".into());
    }
    let mut files = json!({"diagnostics.json.gz.base64":{"content":base64::engine::general_purpose::STANDARD.encode(compressed)},"README.md":{"content":"MQ diagnostic snapshot. diagnostics.json.gz.base64 is base64-encoded gzip JSON (mq.otel.local.v1). Decode base64, then decompress gzip. screen.html, when present, is a self-contained image preview; download and open locally. This unlisted Gist is accessible to anyone with its link."}});
    if draft.include_screen && screen.is_file() {
        let data = std::fs::read(screen).map_err(|e| e.to_string())?;
        if data.len() > 4_000_000 {
            return Err("캡처 파일이 너무 커요.".into());
        }
        files["screen.html"] = json!({"content":format!("<!doctype html><html lang=\"ko\"><meta charset=\"utf-8\"><title>MQ report screenshot</title><style>body{{margin:0;background:#162735}}img{{max-width:100%;height:auto}}</style><img alt=\"MQ report screenshot\" src=\"data:image/png;base64,{}\"></html>",base64::engine::general_purpose::STANDARD.encode(data))});
    }
    Ok(files)
}
fn title(draft: &Draft) -> String {
    format!(
        "[{}] {} · {}",
        if draft.kind == "content" {
            "문제 신고"
        } else {
            "앱 오류 신고"
        },
        draft.location.lesson_title,
        draft.location.task_title
    )
    .chars()
    .take(160)
    .collect()
}
fn body(draft: &Draft, user: &str, gist: &str) -> String {
    let spans = draft.diagnostics["spans"].as_array();
    let mut slow: Vec<_> = spans
        .into_iter()
        .flatten()
        .filter(|s| s["error"] == true || s["duration_ms"].as_u64().unwrap_or(0) >= 2000)
        .collect();
    slow.sort_by_key(|s| std::cmp::Reverse(s["duration_ms"].as_u64().unwrap_or(0)));
    let mut summary = String::new();
    for span in slow.into_iter().take(12) {
        summary.push_str(&format!(
            "- `{}` · {} ms · {}\n",
            span["name"].as_str().unwrap_or("operation"),
            span["duration_ms"],
            if span["error"] == true {
                "오류"
            } else {
                "지연 관측"
            }
        ));
    }
    let location = &draft.location;
    format!("<!-- mq-report:{} -->\n## 설명\n{}\n\n## 위치·환경\n- 사용자: @{}\n- 코스: {} (`{}`)\n- 수업: {} (`{}`), 버전 `{}`\n- 단계: {} (`{}`)\n- 앱 빌드: {}\n- OS / CPU: {} / {}\n\n## 주요 관측\n{}\n## 진단 파일\n[전체 기록과 화면 캡처 파일]({})\n\n상세 실행 기록: 최근 한 시간. 이동 이력: 최대 180일, 용량·건수 상한 적용.\n캡처 포함 요청: {}. 첨부 화면은 screen.html을 내려받아 열 수 있어요.\n",draft.id,draft.description,user,location.course_title,location.course_id,location.lesson_title,location.lesson_id,location.revision,location.task_title,location.task_id,draft.build,draft.os,draft.architecture,if summary.is_empty(){"특별한 오류·지연 관측이 없어요."}else{&summary},gist,draft.include_screen)
}
#[cfg(not(target_os = "android"))]
pub fn submit(path: &Path) -> Result<String, String> {
    let runtime = tokio::runtime::Builder::new_current_thread()
        .enable_all()
        .build()
        .map_err(|e| e.to_string())?;
    let deadline = std::time::Instant::now() + std::time::Duration::from_secs(90);
    submit_with(path, |method, endpoint, payload| {
        let remaining = deadline.saturating_duration_since(std::time::Instant::now());
        runtime.block_on(async {
            tokio::time::timeout(remaining, gh_request(method, endpoint, payload))
                .await
                .map_err(|_| "신고 전송 시간이 초과됐어요. 다시 시도할 수 있어요.".to_string())?
        })
    })
}
#[cfg(not(target_os = "android"))]
async fn gh_request(method: &str, endpoint: &str, payload: Value) -> Result<Value, String> {
    use tokio::io::AsyncWriteExt;
    let mut command = tokio::process::Command::new(crate::setup_terminal::gh_executable());
    command
        .args([
            "api",
            "--hostname",
            "github.com",
            "--method",
            method,
            endpoint,
        ])
        .env("GH_HOST", "github.com")
        .env("GH_PROMPT_DISABLED", "1")
        .stdin(std::process::Stdio::piped())
        .stdout(std::process::Stdio::piped())
        .stderr(std::process::Stdio::piped())
        .kill_on_drop(true);
    if method != "GET" {
        command.args(["--input", "-"]);
    }
    #[cfg(windows)]
    command.creation_flags(0x08000000);
    let mut child = command.spawn().map_err(|e| e.to_string())?;
    let mut stdin = child.stdin.take().ok_or("GitHub input unavailable")?;
    let input = if method == "GET" {
        Vec::new()
    } else {
        serde_json::to_vec(&payload).map_err(|e| e.to_string())?
    };
    let output = tokio::time::timeout(std::time::Duration::from_secs(60), async move {
        let write = async move {
            stdin.write_all(&input).await.map_err(|e| e.to_string())?;
            drop(stdin);
            Ok::<_, String>(())
        };
        let read = async move { child.wait_with_output().await.map_err(|e| e.to_string()) };
        let (_, output) = tokio::try_join!(write, read)?;
        Ok::<_, String>(output)
    })
    .await
    .map_err(|_| "GitHub 응답 시간이 초과됐어요.".to_string())??;
    if !output.status.success() {
        crate::content_lifecycle::note_github_failure(&String::from_utf8_lossy(&output.stderr));
        return Err(format!(
            "GitHub 요청 실패: {}",
            String::from_utf8_lossy(&output.stderr)
                .chars()
                .take(800)
                .collect::<String>()
        ));
    }
    serde_json::from_slice(&output.stdout).map_err(|e| e.to_string())
}
#[cfg(target_os = "android")]
pub fn submit(_path: &Path) -> Result<String, String> {
    Err("이 기기에서는 신고 전송을 지원하지 않아요.".into())
}
fn valid_issue_url(repository: &str, url: &str) -> bool {
    url.strip_prefix(&format!("https://github.com/{repository}/issues/"))
        .is_some_and(|n| !n.is_empty() && n.bytes().all(|b| b.is_ascii_digit()))
}
fn submit_with(
    path: &Path,
    mut request: impl FnMut(&str, &str, Value) -> Result<Value, String>,
) -> Result<String, String> {
    let mut draft = load(path)?;
    if let Some(issue) = &draft.issue {
        if valid_issue_url(&draft.repository, issue) {
            return Ok(issue.clone());
        }
        return Err("신고 이슈 주소를 확인하세요.".into());
    }
    if draft.description.chars().count() > 4000 {
        return Err("추가 설명은 4,000자 이내로 적어주세요.".into());
    }
    // Read authenticated account through gh; never copy its credential into the app.
    let user = request("GET", "/user", Value::Null)?;
    let login = user["login"]
        .as_str()
        .filter(|s| s.bytes().all(|b| b.is_ascii_alphanumeric() || b == b'-'))
        .ok_or("GitHub 계정을 확인하세요.")?;
    let reporter = user["id"]
        .as_u64()
        .ok_or("GitHub 계정 식별자를 확인하세요.")?;
    if draft.reporter.is_some_and(|id| id != reporter) {
        return Err("신고를 준비한 GitHub 계정과 현재 계정이 달라요.".into());
    }
    draft.reporter = Some(reporter);
    save(path, &draft)?;
    if !crate::repository_course::valid_repository(&draft.repository) {
        return Err("신고 저장소를 확인하세요.".into());
    }
    let marker = format!("<!-- mq-report:{} -->", draft.id);
    // Recover a POST whose response was lost. No search-index delay is involved.
    let issues = request(
        "GET",
        &format!(
            "/repos/{}/issues?creator={login}&state=all&per_page=100",
            draft.repository
        ),
        Value::Null,
    )?;
    if let Some(url) = issues
        .as_array()
        .into_iter()
        .flatten()
        .find(|i| i["body"].as_str().is_some_and(|b| b.contains(&marker)))
        .and_then(|i| i["html_url"].as_str())
    {
        if !valid_issue_url(&draft.repository, url) {
            return Err("신고 이슈 주소를 확인하세요.".into());
        }
        draft.issue = Some(url.into());
        save(path, &draft)?;
        return Ok(url.into());
    }
    let gist = if let Some(url) = &draft.gist {
        url.clone()
    } else {
        let description = format!("MQ diagnostic report {}", draft.id);
        let existing = request("GET", "/gists?per_page=100", Value::Null)?;
        let recovered = existing
            .as_array()
            .into_iter()
            .flatten()
            .find(|g| g["description"] == description)
            .and_then(|g| g["html_url"].as_str());
        let url = if let Some(url) = recovered {
            url.to_owned()
        } else {
            let response = request(
                "POST",
                "/gists",
                json!({"description":description,"public":false,"files":files(&draft,&path.parent().unwrap().join("screen.png"))?}),
            )?;
            response["html_url"]
                .as_str()
                .ok_or("진단 파일 주소를 확인하지 못했어요.")?
                .to_owned()
        };
        if !url.starts_with("https://gist.github.com/") {
            return Err("진단 파일 주소를 확인하세요.".into());
        }
        draft.gist = Some(url.clone());
        save(path, &draft)?;
        url
    };
    if !draft.include_screen {
        let id = gist
            .rsplit('/')
            .next()
            .filter(|id| id.bytes().all(|b| b.is_ascii_alphanumeric()))
            .ok_or("진단 파일 주소 오류")?;
        let current = request("GET", &format!("/gists/{id}"), Value::Null)?;
        if current["files"]["screen.html"].is_object() {
            request(
                "PATCH",
                &format!("/gists/{id}"),
                json!({"files":{"screen.html":null}}),
            )?;
        }
    }
    let response = request(
        "POST",
        &format!("/repos/{}/issues", draft.repository),
        json!({"title":title(&draft),"body":body(&draft,login,&gist)}),
    )?;
    let url = response["html_url"]
        .as_str()
        .ok_or("신고 이슈 주소를 확인하지 못했어요.")?
        .to_owned();
    if !valid_issue_url(&draft.repository, &url) {
        return Err("신고 이슈 주소를 확인하세요.".into());
    }
    draft.issue = Some(url.clone());
    save(path, &draft)?;
    Ok(url)
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn report_retries_reuse_files_and_issue_and_route_content_to_lesson() {
        let root = tempfile::tempdir().unwrap();
        let path = root.path().join("draft.json");
        let draft = Draft {
            id: "test-report".into(),
            kind: "content".into(),
            repository: "owner/lesson".into(),
            location: Location::default(),
            created_at: 0,
            build: "test".into(),
            os: "windows".into(),
            architecture: "x86_64".into(),
            diagnostics: json!({"spans":[]}),
            description: "문제 확인".into(),
            include_screen: false,
            gist: None,
            issue: None,
            reporter: None,
        };
        save(&path, &draft).unwrap();
        let mut created = 0;
        let mut posts = 0;
        let first = submit_with(&path, |method, url, _| match (method, url) {
            ("GET", "/user") => Ok(json!({"login":"tester","id":7})),
            ("GET", _) => Ok(json!([])),
            ("PATCH", _) => Ok(json!({})),
            ("POST", "/gists") => {
                created += 1;
                Ok(json!({"html_url":"https://gist.github.com/tester/report"}))
            }
            ("POST", p) => {
                assert_eq!(p, "/repos/owner/lesson/issues");
                posts += 1;
                Err("response lost".into())
            }
            _ => unreachable!(),
        });
        assert!(first.is_err());
        assert_eq!(created, 1);
        let result=submit_with(&path,|method,url,_|{
            assert_eq!(method,"GET");
            if url=="/user"{Ok(json!({"login":"tester","id":7}))}else{Ok(json!([{"html_url":"https://github.com/owner/lesson/issues/1","body":"<!-- mq-report:test-report -->"}]))}
        }).unwrap();
        assert!(result.ends_with("/1"));
        assert_eq!(posts, 1);
        assert_eq!(
            submit_with(&path, |_, _, _| panic!("already sent")).unwrap(),
            result
        );
    }
    #[test]
    fn full_snapshot_can_be_recovered_from_compressed_attachment() {
        use base64::Engine;
        use std::io::Read;
        let draft = Draft {
            id: "id".into(),
            kind: "bug".into(),
            repository: PLAYER_REPOSITORY.into(),
            location: Location::default(),
            created_at: 0,
            build: "test".into(),
            os: "windows".into(),
            architecture: "x86_64".into(),
            diagnostics: json!({"spans":[{"name":"code.execute"}]}),
            description: String::new(),
            include_screen: false,
            gist: None,
            issue: None,
            reporter: None,
        };
        let files = files(&draft, Path::new("absent.png")).unwrap();
        let data = base64::engine::general_purpose::STANDARD
            .decode(
                files["diagnostics.json.gz.base64"]["content"]
                    .as_str()
                    .unwrap(),
            )
            .unwrap();
        let mut text = String::new();
        flate2::read::GzDecoder::new(&data[..])
            .read_to_string(&mut text)
            .unwrap();
        assert_eq!(
            serde_json::from_str::<Value>(&text).unwrap(),
            draft.diagnostics
        );
        assert!(files.get("screen.html").is_none());
    }
}
