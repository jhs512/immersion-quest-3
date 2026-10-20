//! Neural Korean speech for 해설 모드: the voices of Microsoft Edge's "소리 내어 읽기" (선히, 인준,
//! 현수), through the maintained edge-tts package installed with the learning environment.
//! The page requests MP3 clips over the app's custom protocol; selected neural voices never
//! silently change to a device voice. Successful clips are cached under the app data folder.

use std::path::PathBuf;

/// Voices the settings offer; the first is the default.
pub const VOICES: [(&str, &str); 4] = [
    ("ko-KR-SunHiNeural", "선히 · 여성, 자연스러운 음성 (인터넷 필요)"),
    ("ko-KR-InJoonNeural", "인준 · 남성, 자연스러운 음성 (인터넷 필요)"),
    ("ko-KR-HyunsuMultilingualNeural", "현수 · 남성, 다국어 음성 (인터넷 필요)"),
    ("system", "기기 기본 음성 · 오프라인"),
];

pub fn default_voice() -> String {
    VOICES[0].0.to_string()
}

fn is_known_voice(voice: &str) -> bool {
    VOICES.iter().any(|(id, _)| *id == voice && *id != "system")
}

/// Use the maintained Edge client bundled in the learning environment. The old direct
/// WebSocket implementation used the retired v1 handshake and now receives HTTP 403.
fn edge_python(voice: &str, text: &str, path: &std::path::Path) -> Result<Vec<u8>, String> {
    use std::{process::{Command, Stdio}, time::{Duration, Instant}};
    let error_log = tempfile::tempfile().map_err(|e| e.to_string())?;
    let mut command = Command::new(crate::runner::python_executable());
    command.args(["-m", "edge_tts", "--voice", voice, "--text", text, "--write-media"])
        .arg(path).stdin(Stdio::null()).stdout(Stdio::null())
        .stderr(error_log.try_clone().map_err(|e|e.to_string())?);
    #[cfg(windows)] {
        use std::os::windows::process::CommandExt;
        command.creation_flags(0x08000000);
    }
    let mut child=command.spawn().map_err(|e|format!("Edge TTS를 시작하지 못했어요: {e}"))?;
    let deadline=Instant::now()+Duration::from_secs(20);
    let status=loop {
        match child.try_wait() {
            Ok(Some(status))=>break status,
            Ok(None) if Instant::now()<deadline=>std::thread::sleep(Duration::from_millis(40)),
            result=>{
                let _=child.kill();let _=child.wait();
                return Err(match result {Err(e)=>e.to_string(),_=>"Edge 음성 서버의 응답이 늦어요. 잠시 뒤 다시 재생해 주세요.".into()});
            }
        }
    };
    if !status.success() {
        use std::io::{Read,Seek,SeekFrom};
        let mut error_log=error_log;let _=error_log.seek(SeekFrom::Start(0));
        let mut stderr=String::new();let _=error_log.take(8192).read_to_string(&mut stderr);
        return Err(format!("Edge TTS 연결에 실패했어요: {}",stderr.lines().rev().find(|l|!l.trim().is_empty()).unwrap_or("음성 환경을 확인해 주세요.")));
    }
    let bytes=std::fs::read(path).map_err(|e|e.to_string())?;
    if bytes.len()<2 || !(bytes.starts_with(b"ID3") || bytes[0]==0xff && bytes[1]&0xe0==0xe0) {
        return Err("Edge TTS가 올바른 음성을 보내지 않았어요.".into());
    }
    Ok(bytes)
}

fn cache_path(voice: &str, text: &str) -> Result<PathBuf, String> {
    // A short, stable name per (voice, text): FNV-1a over both, hex.
    let mut hash: u64 = 0xcbf29ce484222325;
    for byte in voice.bytes().chain([0u8]).chain(text.bytes()) {
        hash ^= byte as u64;
        hash = hash.wrapping_mul(0x100000001b3);
    }
    let dir = crate::data_dir()?.join("tts-cache");
    std::fs::create_dir_all(&dir).map_err(|e| e.to_string())?;
    Ok(dir.join(format!("{voice}-{hash:016x}.mp3")))
}

/// MP3 bytes for the sentence and their source ("cache" or "edge-tts").
pub fn synthesize(voice: &str, text: &str) -> Result<(Vec<u8>, &'static str), String> {
    crate::telemetry::observe_sync("narration.synthesize",vec![],||synthesize_inner(voice,text))
}
fn synthesize_inner(voice: &str, text: &str) -> Result<(Vec<u8>, &'static str),String> {
    let text = text.trim();
    if text.is_empty() || text.len() > 2000 {
        return Err("문장이 비었거나 너무 깁니다.".into());
    }
    if !is_known_voice(voice) {
        return Err(format!("모르는 음성입니다: {voice}"));
    }
    let path = cache_path(voice, text)?;
    if let Ok(bytes) = std::fs::read(&path) {
        if !bytes.is_empty() {
            return Ok((bytes, "cache"));
        }
    }
    // Keep incomplete downloads out of the persistent cache, even on timeout.
    let download=tempfile::Builder::new().suffix(".mp3").tempfile_in(path.parent().unwrap())
        .map_err(|e|e.to_string())?;
    let bytes=edge_python(voice,text,download.path())?;
    let _=std::fs::write(path,&bytes);
    Ok((bytes,"edge-tts"))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rejects_unknown_voices_and_empty_text() {
        assert!(synthesize("system", "안녕").is_err());
        assert!(synthesize("ko-KR-SunHiNeural", "   ").is_err());
        assert!(is_known_voice("ko-KR-InJoonNeural"));
        assert!(!is_known_voice("system"));
    }

    #[test]
    fn cache_name_is_stable_and_distinct() {
        let a = cache_path("ko-KR-SunHiNeural", "안녕하세요").unwrap();
        let b = cache_path("ko-KR-SunHiNeural", "안녕하세요").unwrap();
        let c = cache_path("ko-KR-InJoonNeural", "안녕하세요").unwrap();
        let d = cache_path("ko-KR-SunHiNeural", "안녕하세요.").unwrap();
        assert_eq!(a, b);
        assert_ne!(a, c);
        assert_ne!(a, d);
        assert!(a.to_string_lossy().ends_with(".mp3"));
    }

    /// `cargo test --lib tts -- --ignored` talks to the real service.
    /// A never-cached phrase, so the connection path itself (timeouts included) is exercised.
    #[test]
    #[ignore]
    fn a_fresh_clip_downloads_within_the_timeouts() {
        let phrase = format!("지금 시각은 {}초예요", std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_millis());
        let started = std::time::Instant::now();
        let (bytes, engine) = synthesize(&default_voice(), &phrase).unwrap();
        assert!(!bytes.is_empty());
        assert_ne!(engine, "cache");
        assert!(started.elapsed() < std::time::Duration::from_secs(30), "{:?}", started.elapsed());
    }

    #[test]
    #[ignore]
    fn the_service_answers_with_mp3() {
        let (bytes, engine) = synthesize("ko-KR-SunHiNeural", "내장 음성 시험입니다.").unwrap();
        assert!(bytes.len() > 1000, "{engine}");
        assert!(bytes.starts_with(&[0xFF]) || bytes.starts_with(b"ID3"), "{engine}");
    }
}
