//! Auto-update from GitHub Releases (desktop only).
//!
//! Every push to main publishes a release tagged `v<version>-build.<run>` (release.yml) and the
//! workflow bakes that run number into the executable as `MOLIP_BUILD`. The app asks the API
//! for the latest release, compares build numbers, and when a newer one exists downloads this
//! platform's installer and hands over to a small script that waits for the app to exit,
//! installs, and starts the new build. Drafts and progress are saved as the student works, so
//! closing is safe at any moment.
//!
//! Development builds (no `MOLIP_BUILD`) never update themselves unless `MOLIP_UPDATE_CHECK=1`.
use std::path::PathBuf;

pub const REPO: &str = "jhs512/immersion-quest-3";
const API_LATEST: &str = "https://api.github.com/repos/jhs512/immersion-quest-3/releases/latest";
const WEB_LATEST: &str = "https://github.com/jhs512/immersion-quest-3/releases/latest";

/// Monotonic elapsed seconds; one startup check and no overlapping requests.
#[derive(Default)]
pub struct UpdateSchedule { last: Option<u64>, checking: bool }
impl UpdateSchedule {
    pub fn begin(&mut self, now:u64, manual:bool)->bool {
        if self.checking || (!manual && self.last.is_some_and(|last|now.saturating_sub(last)<300)) {return false}
        self.last=Some(now);self.checking=true;true
    }
    pub fn finish(&mut self) {self.checking=false;}
}

#[derive(Clone, Debug, PartialEq)]
pub struct Release {
    pub build: u64,
    pub tag: String,
    pub title: String,
    pub asset_name: String,
    pub asset_url: String,
    pub size: u64,
}

/// The build number this executable was published as; 0 for a development build.
pub fn current_build() -> u64 {
    option_env!("MOLIP_BUILD")
        .and_then(|b| b.trim().parse().ok())
        .unwrap_or(0)
}

/// Whether this build should look for updates at all.
pub fn enabled() -> bool {
    if crate::pilot_source::enabled() {return true;}
    if cfg!(target_os = "android") {
        return false;
    }
    current_build() > 0 || std::env::var_os("MOLIP_UPDATE_CHECK").is_some()
}

/// "v0.1.0-build.42" → 42.
pub fn build_of(tag: &str) -> Option<u64> {
    tag.rsplit("build.").next()?.trim().parse().ok()
}

/// The installer this platform wants from a release's asset list.
pub fn asset_for_platform() -> Option<&'static str> {
    if cfg!(target_os = "windows") {
        Some("molip-quest-3-windows-x64-setup.exe")
    } else if cfg!(all(target_os = "macos", target_arch = "aarch64")) {
        Some("molip-quest-3-macos-arm64.dmg")
    } else if cfg!(all(target_os = "macos", target_arch = "x86_64")) {
        Some("molip-quest-3-macos-x64.dmg")
    } else {
        None
    }
}

/// The newer release in a `releases/latest` JSON body, or None when it is not newer than
/// `current` or carries no installer for this platform.
pub fn newer_in(json: &serde_json::Value, current: u64) -> Option<Release> {
    let tag = json["tag_name"].as_str()?;
    let build = build_of(tag)?;
    if build <= current {
        return None;
    }
    let wanted = asset_for_platform()?;
    let asset = json["assets"]
        .as_array()?
        .iter()
        .find(|a| a["name"].as_str() == Some(wanted))?;
    Some(Release {
        build,
        tag: tag.to_string(),
        title: json["name"].as_str().unwrap_or(tag).to_string(),
        asset_name: wanted.to_string(),
        asset_url: asset["browser_download_url"].as_str()?.to_string(),
        size: asset["size"].as_u64().unwrap_or(0),
    })
}

#[cfg(not(target_os = "android"))]
fn agent() -> ureq::Agent {
    use ureq::tls::{TlsConfig, TlsProvider};
    let config = ureq::Agent::config_builder()
        .tls_config(
            TlsConfig::builder()
                .provider(TlsProvider::NativeTls)
                .build(),
        )
        .user_agent(format!("molip-quest/{}", current_build()))
        .timeout_global(Some(std::time::Duration::from_secs(600)))
        .build();
    ureq::Agent::new_with_config(config)
}

/// Ask GitHub for the latest release. Blocking; call from a worker thread.
#[cfg(not(target_os = "android"))]
pub fn check() -> Result<Option<Release>, String> {
    if crate::pilot_source::enabled() {
        return Ok(asset_for_platform().map(|name|Release{build:current_build()+1,tag:"pilot-update".into(),title:"검증용 새 버전".into(),asset_name:name.into(),asset_url:"https://example.invalid/never-download".into(),size:1}));
    }
    if !enabled() {
        return Ok(None);
    }
    // MQ3 uses the same gh login as learning. It also reads private release metadata.
    if let Ok(json) = crate::course_authoring::gh(&["api", "--hostname", "github.com",
        &format!("repos/{REPO}/releases/latest")], None) {
        return Ok(newer_in(&json, current_build()));
    }
    check_sources(&agent(), API_LATEST, WEB_LATEST, current_build())
}

#[cfg(not(target_os = "android"))]
fn check_sources(
    client: &ureq::Agent,
    api: &str,
    web: &str,
    current: u64,
) -> Result<Option<Release>, String> {
    let primary = (|| {
        let mut response = client
            .get(api)
            .header("Accept", "application/vnd.github+json")
            .config()
            .timeout_global(Some(std::time::Duration::from_secs(30)))
            .build()
            .call()
            .map_err(|e| format!("업데이트 확인 실패: {e}"))?;
        let json: serde_json::Value = response
            .body_mut()
            .read_json()
            .map_err(|e| format!("업데이트 정보를 읽지 못했습니다: {e}"))?;
        Ok(newer_in(&json, current))
    })();
    primary.or_else(|api_error: String| {
        // Public release redirects do not consume the unauthenticated API quota.
        // Read Location without downloading the release HTML or following it.
        let fallback = (|| {
            let response = client
                .head(web)
                .config()
                .max_redirects(0)
                .timeout_global(Some(std::time::Duration::from_secs(30)))
                .build()
                .call()
                .map_err(|e| e.to_string())?;
            if !response.status().is_redirection() {
                return Err("최신 릴리즈 이동 경로가 없습니다.".into());
            }
            let location = response
                .headers()
                .get("Location")
                .and_then(|v| v.to_str().ok())
                .ok_or("최신 릴리즈 주소가 없습니다.")?;
            release_from_redirect(location, current)
        })();
        fallback.map_err(|error: String| format!("{api_error} · 공개 릴리즈 확인도 실패: {error}"))
    })
}

fn release_from_redirect(location: &str, current: u64) -> Result<Option<Release>, String> {
    let tag = location
        .strip_prefix("https://github.com/jhs512/immersion-quest-3/releases/tag/")
        .ok_or("몰입 퀘스트 릴리즈 주소가 아닙니다.")?;
    if !tag.starts_with('v')
        || !tag
            .chars()
            .all(|c| c.is_ascii_alphanumeric() || c == '.' || c == '-')
    {
        return Err("릴리즈 태그 형식이 잘못되었습니다.".into());
    }
    let build = build_of(tag).ok_or("릴리즈 빌드 번호가 없습니다.")?;
    let Some(wanted) = asset_for_platform() else {
        return Ok(None);
    };
    if build <= current {
        return Ok(None);
    }
    Ok(Some(Release {
        build,
        tag: tag.into(),
        title: tag.into(),
        asset_name: wanted.into(),
        asset_url: format!("https://github.com/{REPO}/releases/download/{tag}/{wanted}"),
        size: 0, // The download response supplies Content-Length.
    }))
}

/// Download the release's installer into the app data folder, reporting (done, total) bytes.
/// Blocking; call from a worker thread.
#[cfg(not(target_os = "android"))]
pub fn download(release: &Release, mut progress: impl FnMut(u64, u64)) -> Result<PathBuf, String> {
    if crate::pilot_source::enabled() {return Err("검증 모드에서는 실제 설치 파일을 받지 않아요.".into());}
    use std::io::{Read, Write};
    let dir = crate::data_dir()?.join("updates");
    std::fs::create_dir_all(&dir).map_err(|e| e.to_string())?;
    let path = dir.join(format!("build-{}-{}", release.build, release.asset_name));
    if Some(release.asset_name.as_str()) != asset_for_platform() {
        return Err("이 플랫폼의 설치 파일이 아니에요.".into());
    }
    // gh keeps credentials in its own credential store. No token is exposed to a command line.
    let mut command = std::process::Command::new(crate::setup_terminal::gh_executable());
    command.args(["release", "download", "--repo", REPO, "--pattern", &release.asset_name,
        "--output"]).arg(&path).args(["--clobber", "--", &release.tag])
        .env("GH_HOST", "github.com").env("GH_PROMPT_DISABLED", "1");
    #[cfg(windows)] {
        use std::os::windows::process::CommandExt;
        command.creation_flags(0x0800_0000);
    }
    progress(0, release.size);
    if command.output().is_ok_and(|out| out.status.success()) {
        let size = std::fs::metadata(&path).map_err(|e|e.to_string())?.len();
        if size == 0 || (release.size > 0 && size != release.size) {
            let _ = std::fs::remove_file(&path);
            return Err("설치 파일이 불완전해요.".into());
        }
        progress(size, size);
        return Ok(path);
    }
    let mut response = agent()
        .get(&release.asset_url)
        .call()
        .map_err(|e| format!("설치 파일을 받지 못했습니다: {e}"))?;
    let total = response
        .headers()
        .get("Content-Length")
        .and_then(|v| v.to_str().ok())
        .and_then(|v| v.parse().ok())
        .unwrap_or(release.size);
    let mut reader = response.body_mut().with_config().limit(1 << 30).reader();
    let mut file = std::fs::File::create(&path).map_err(|e| e.to_string())?;
    let mut buffer = vec![0u8; 256 * 1024];
    let mut done = 0u64;
    loop {
        let n = reader
            .read(&mut buffer)
            .map_err(|e| format!("내려받는 중 끊겼습니다: {e}"))?;
        if n == 0 {
            break;
        }
        file.write_all(&buffer[..n]).map_err(|e| e.to_string())?;
        done += n as u64;
        progress(done, total);
    }
    file.flush().map_err(|e| e.to_string())?;
    if total > 0 && done != total {
        let _ = std::fs::remove_file(&path);
        return Err(format!(
            "설치 파일이 불완전합니다 ({done} / {total} 바이트)."
        ));
    }
    Ok(path)
}

#[cfg(target_os = "windows")]
fn windows_update_command(script: &str) -> std::process::Command {
    use std::os::windows::process::CommandExt;
    let mut command = std::process::Command::new("powershell");
    command.args([
        "-NoProfile",
        "-NonInteractive",
        "-WindowStyle",
        "Hidden",
        "-Command",
        script,
    ]);
    // Windows PowerShell exits without evaluating -Command when started with
    // DETACHED_PROCESS. CREATE_NO_WINDOW alone hides it and lets it outlive the app.
    command.creation_flags(0x0800_0000); // CREATE_NO_WINDOW
    command.stdin(std::process::Stdio::null());
    command
}

/// Hand over to the installer and leave: a background script waits for this process to exit,
/// installs the new build over the current one and starts it. Returns only on failure.
#[cfg(not(target_os = "android"))]
pub fn install_and_restart(installer: &PathBuf) -> Result<(), String> {
    if crate::pilot_source::enabled() {return Err("검증 모드에서는 실제 앱을 교체하지 않아요.".into());}
    let exe = std::env::current_exe().map_err(|e| e.to_string())?;
    let pid = std::process::id();
    #[cfg(target_os = "windows")]
    {
        // Silent per-user reinstall into the same folder (Inno remembers it), then relaunch.
        let script = format!(
            "Wait-Process -Id {pid} -ErrorAction SilentlyContinue; \
             $p = Start-Process -FilePath '{installer}' -ArgumentList '/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART','/CLOSEAPPLICATIONS' -Wait -PassThru; \
             Start-Process -FilePath '{exe}'",
            installer = installer.display().to_string().replace('\'', "''"),
            exe = exe.display().to_string().replace('\'', "''"),
        );
        windows_update_command(&script)
            .stdout(std::process::Stdio::null())
            .stderr(std::process::Stdio::null())
            .spawn()
            .map_err(|e| format!("업데이트 스크립트를 시작하지 못했습니다: {e}"))?;
    }
    #[cfg(target_os = "macos")]
    {
        // The bundle is three levels above the binary: X.app/Contents/MacOS/molip-quest.
        let bundle = exe
            .ancestors()
            .nth(3)
            .filter(|p| p.extension().is_some_and(|e| e == "app"))
            .ok_or("앱 번들 밖에서 실행 중이라 자동 업데이트를 할 수 없습니다.")?
            .to_path_buf();
        let script = format!(
            "while kill -0 {pid} 2>/dev/null; do sleep 0.5; done; \
             mount=$(hdiutil attach '{dmg}' -nobrowse -readonly | awk -F'\\t' '/\\/Volumes\\//{{print $NF}}' | head -n 1); \
             app=$(ls -d \"$mount\"/*.app | head -n 1); \
             rm -rf '{bundle}'; ditto \"$app\" '{bundle}'; xattr -dr com.apple.quarantine '{bundle}' 2>/dev/null; \
             hdiutil detach \"$mount\" -quiet; open -n '{bundle}'",
            dmg = installer.display().to_string().replace('\'', "'\\''"),
            bundle = bundle.display().to_string().replace('\'', "'\\''"),
        );
        std::process::Command::new("sh")
            .args(["-c", &script])
            .stdin(std::process::Stdio::null())
            .stdout(std::process::Stdio::null())
            .stderr(std::process::Stdio::null())
            .spawn()
            .map_err(|e| format!("업데이트 스크립트를 시작하지 못했습니다: {e}"))?;
    }
    #[cfg(not(any(target_os = "windows", target_os = "macos")))]
    {
        let _ = (exe, pid);
        return Err("이 플랫폼은 자동 업데이트를 지원하지 않습니다.".into());
    }
    #[allow(unreachable_code)]
    {
        std::process::exit(0);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn public_redirect_requires_this_repository_and_a_newer_build() {
        let url = "https://github.com/jhs512/immersion-quest-3/releases/tag/v0.1.0-build.155";
        assert!(release_from_redirect(url, 155).unwrap().is_none());
        assert!(release_from_redirect(url, 156).unwrap().is_none());
        assert!(
            release_from_redirect("https://example.com/releases/tag/v0.1.0-build.155", 0).is_err()
        );
        assert!(release_from_redirect(&format!("{url}/other"), 0).is_err());
    }

    #[test]
    #[ignore = "requires GitHub and installer download"]
    #[cfg(not(target_os = "android"))]
    fn public_fallback_downloads_real_installer() {
        let found = check_sources(&agent(), "http://127.0.0.1:1/api", WEB_LATEST, 0)
            .unwrap()
            .expect("published release");
        assert_eq!(found.size, 0);
        let mut last = (0, 0);
        let path = download(&found, |done, total| last = (done, total)).unwrap();
        assert!(last.0 > 1_000_000 && last.0 == last.1);
        assert_eq!(std::fs::metadata(&path).unwrap().len(), last.0);
        std::fs::remove_file(path).unwrap();
    }

    #[test]
    #[cfg(not(target_os = "android"))]
    fn api_403_uses_public_latest_redirect() {
        use std::io::{BufRead, BufReader, Write};
        let listener = std::net::TcpListener::bind("127.0.0.1:0").unwrap();
        let address = listener.local_addr().unwrap();
        let server = std::thread::spawn(move || {
            for index in 0..2 {
                let (mut stream, _) = listener.accept().unwrap();
                stream
                    .set_read_timeout(Some(std::time::Duration::from_secs(3)))
                    .unwrap();
                let mut reader = BufReader::new(stream.try_clone().unwrap());
                let mut line = String::new();
                loop {
                    line.clear();
                    reader.read_line(&mut line).unwrap();
                    if line == "\r\n" || line.is_empty() {
                        break;
                    }
                }
                let response = if index == 0 {
                    "HTTP/1.1 403 Forbidden\r\nContent-Length: 0\r\nConnection: close\r\n\r\n"
                } else {
                    "HTTP/1.1 302 Found\r\nLocation: https://github.com/jhs512/immersion-quest-3/releases/tag/v0.1.0-build.155\r\nContent-Length: 0\r\nConnection: close\r\n\r\n"
                };
                stream.write_all(response.as_bytes()).unwrap();
            }
        });
        let found = check_sources(
            &agent(),
            &format!("http://{address}/api"),
            &format!("http://{address}/latest"),
            154,
        )
        .expect("API 403 must not block an available public release");
        if asset_for_platform().is_some() {
            let release = found.unwrap();
            assert_eq!(release.build, 155);
            assert!(release
                .asset_url
                .contains("/releases/download/v0.1.0-build.155/"));
        }
        server.join().unwrap();
    }

    #[cfg(target_os = "windows")]
    #[test]
    fn hidden_update_helper_actually_executes_its_script() {
        let output = windows_update_command("Write-Output 'updater-handoff-ready'")
            .output()
            .expect("launch update helper");
        assert!(output.status.success());
        assert_eq!(
            String::from_utf8_lossy(&output.stdout).trim(),
            "updater-handoff-ready",
            "PowerShell exited without running the update script"
        );
    }

    fn latest(tag: &str) -> serde_json::Value {
        serde_json::json!({
            "tag_name": tag,
            "name": format!("{tag} — subject"),
            "assets": [
                {"name": "molip-quest-3-windows-x64-setup.exe", "browser_download_url": "https://example.com/w.exe", "size": 10},
                {"name": "molip-quest-3-macos-arm64.dmg", "browser_download_url": "https://example.com/m.dmg", "size": 20},
                {"name": "molip-quest-3-macos-x64.dmg", "browser_download_url": "https://example.com/intel.dmg", "size": 20},
                {"name": "molip-quest-android.apk", "browser_download_url": "https://example.com/a.apk", "size": 30}
            ]
        })
    }

    #[test]
    fn build_numbers_come_from_the_tag() {
        assert_eq!(build_of("v0.1.0-build.42"), Some(42));
        assert_eq!(build_of("v1.2.3-build.7"), Some(7));
        assert_eq!(build_of("v0.1.0"), None);
    }

    #[test]
    fn only_a_newer_release_with_this_platforms_installer_counts() {
        let newer = newer_in(&latest("v0.1.0-build.42"), 41);
        if let Some(wanted) = asset_for_platform() {
            let release = newer.expect("newer");
            assert_eq!(release.build, 42);
            assert_eq!(release.asset_name, wanted);
            assert!(release.asset_url.starts_with("https://example.com/"));
        } else {
            assert!(newer.is_none());
        }
        assert!(newer_in(&latest("v0.1.0-build.42"), 42).is_none());
        assert!(newer_in(&latest("v0.1.0-build.42"), 50).is_none());
        let mut no_assets = latest("v0.1.0-build.42");
        no_assets["assets"] = serde_json::json!([]);
        assert!(newer_in(&no_assets, 1).is_none());
    }

    /// Needs the network and ~40 MB: `cargo test -- --ignored installer_downloads`.
    #[test]
    #[ignore]
    #[cfg(not(target_os = "android"))]
    fn installer_downloads_completely() {
        std::env::set_var("MOLIP_UPDATE_CHECK", "1");
        let release = check().unwrap().expect("a release");
        let mut last = (0, 0);
        let path = download(&release, |done, total| last = (done, total)).unwrap();
        let size = std::fs::metadata(&path).unwrap().len();
        assert!(
            size > 1_000_000 && size == release.size,
            "{size} vs {}",
            release.size
        );
        let _ = std::fs::remove_file(path);
    }

    /// Needs the network: `cargo test -- --ignored latest_release`.
    #[test]
    #[ignore]
    #[cfg(not(target_os = "android"))]
    fn latest_release_is_reachable() {
        std::env::set_var("MOLIP_UPDATE_CHECK", "1");
        let found = check().unwrap();
        assert!(found.is_some(), "a release newer than build 0 should exist");
    }
}
