//! Installer handoff scripts keep the old bundle until the replacement is verified.
use std::path::Path;
pub const MAC_PENDING_FILE:&str="macos-handoff.pending";

/// A silent installer handoff relaunches the current path on success or failure.
/// A nonzero installer result remains a failure even if the old player can reopen.
pub fn windows_script(installer:&Path,executable:&Path,pid:u32)->Result<String,String> {
    let exe=|path:&Path|path.extension().and_then(|extension|extension.to_str()).is_some_and(|extension|extension.eq_ignore_ascii_case("exe"));
    if !installer.is_absolute()||!executable.is_absolute()||!exe(installer)||!exe(executable)||pid==0 {return Err("설치 파일과 앱 경로를 확인하세요.".into())}
    let quote=|path:&Path|path.to_str().filter(|value|!value.contains(['\n','\r','\0'])).map(|value|format!("'{}'",value.replace('\'',"''"))).ok_or_else(||"설치 경로를 확인하세요.".to_owned());
    Ok(format!(r#"$ErrorActionPreference='Stop'
$installer={installer}
$executable={executable}
$log="$installer.handoff.log"
Wait-Process -Id {pid} -ErrorAction SilentlyContinue
$code=1
try {{
  $installed=Start-Process -FilePath $installer -ArgumentList '/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART','/CLOSEAPPLICATIONS' -Wait -PassThru
  $code=$installed.ExitCode
  if ($code -ne 0) {{Add-Content -LiteralPath $log -Value "Installer exit: $code"}}
}} catch {{Add-Content -LiteralPath $log -Value ($_.ToString())}}
if (Test-Path -LiteralPath $executable) {{
  try {{Start-Process -FilePath $executable}} catch {{$code=1;Add-Content -LiteralPath $log -Value ($_.ToString())}}
}} else {{$code=1;Add-Content -LiteralPath $log -Value 'Player executable missing'}}
exit $code
"#,installer=quote(installer)?,executable=quote(executable)?))
}


/// The launched app acknowledges only a request for its own bundle in this update folder.
pub fn acknowledge_startup(pending:&Path,bundle:&Path)->Result<bool,String> {
    let text=match std::fs::read_to_string(pending) {Ok(text)=>text,Err(e) if e.kind()==std::io::ErrorKind::NotFound=>return Ok(false),Err(e)=>return Err(e.to_string())};
    let fields:Vec<_>=text.lines().collect();
    if text.len()>4096 || fields.len()!=3 {return Err("업데이트 시작 확인 형식 오류".into())}
    let nonce=fields[1];
    if nonce.len()!=32 || !nonce.bytes().all(|c|c.is_ascii_hexdigit()) {return Err("업데이트 시작 확인 코드 오류".into())}
    if Path::new(fields[2])!=bundle {return Ok(false)}
    let directory=pending.parent().ok_or("업데이트 확인 경로 오류")?;
    let expected=directory.join(format!("macos-startup-{nonce}.ack"));
    if Path::new(fields[0])!=expected {return Err("업데이트 시작 확인 경로 오류".into())}
    use std::io::Write;
    let mut temporary=tempfile::NamedTempFile::new_in(directory).map_err(|e|e.to_string())?;
    temporary.write_all(nonce.as_bytes()).map_err(|e|e.to_string())?;
    temporary.persist(expected).map_err(|e|e.to_string())?;
    Ok(true)
}

fn quote(path:&Path)->Result<String,String> {
    path.to_str().filter(|value|!value.contains(['\n','\r','\0'])).map(|value|format!("'{}'",value.replace('\'',"'\\''"))).ok_or("설치 경로를 확인하세요.".into())
}

pub fn macos_script(installer:&Path,bundle:&Path,pid:u32)->Result<String,String> {
    if !installer.is_absolute() || !bundle.is_absolute() || installer.extension().is_none_or(|ext|ext!="dmg") || bundle.extension().is_none_or(|ext|ext!="app") {
        return Err("설치 이미지와 앱 번들 경로를 확인하세요.".into());
    }
    let parent=bundle.parent().ok_or("앱 번들의 상위 폴더를 확인하세요.")?;
    let updates=installer.parent().ok_or("설치 이미지 폴더 오류")?;
    let nonce=crate::issue_progress::new_id();
    let ack=updates.join(format!("macos-startup-{nonce}.ack"));
    let pending=updates.join(MAC_PENDING_FILE);
    Ok(format!(r#"set -eu
installer={installer}
bundle={bundle}
parent={parent}
ack={ack}
pending={pending}
nonce={nonce}
mount=''
work=''
backup=''
candidate_pid=''
committed=0
cleanup() {{
  keep=0
  if [ "$committed" -eq 0 ] && [ -n "$candidate_pid" ]; then
    kill -TERM "$candidate_pid" 2>/dev/null || true
    grace=0
    while kill -0 "$candidate_pid" 2>/dev/null && [ "$grace" -lt 10 ]; do sleep 0.1; grace=$((grace + 1)); done
    kill -KILL "$candidate_pid" 2>/dev/null || true
    wait "$candidate_pid" 2>/dev/null || true
  fi
  if [ "$committed" -eq 0 ] && [ -d "$backup" ]; then
    if [ -e "$bundle" ]; then mv "$bundle" "$work/failed.app" || keep=1; fi
    if [ "$keep" -eq 0 ]; then mv "$backup" "$bundle" || keep=1; fi
  fi
  if [ "$committed" -eq 0 ] && [ "$keep" -eq 0 ] && [ -d "$bundle" ]; then open -n "$bundle" || true; fi
  hdiutil detach "$mount" -quiet 2>/dev/null || true
  rmdir "$mount" 2>/dev/null || true
  if [ "$keep" -eq 0 ]; then
    case "$work" in "$parent"/.mq3-update.*) rm -rf -- "$work" ;; esac
  fi
  rm -f -- "$ack"
  if [ -f "$pending" ] && [ "$(sed -n '2p' "$pending")" = "$nonce" ]; then rm -f -- "$pending"; fi
}}
trap cleanup EXIT
log="$installer.handoff.log"
exec >>"$log" 2>&1
while kill -0 {pid} 2>/dev/null; do sleep 0.5; done
mount=$(mktemp -d "${{TMPDIR:-/tmp}}/mq3-mount.XXXXXX")
work=$(mktemp -d "$parent/.mq3-update.XXXXXX")
backup="$work/previous.app"
stage="$work/new.app"
hdiutil attach "$installer" -mountpoint "$mount" -nobrowse -readonly >/dev/null
source="$mount/몰입 퀘스트 3.app"
test -x "$source/Contents/MacOS/molip-quest"
test "$(/usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' "$source/Contents/Info.plist")" = dev.molipquest.mq3
codesign --verify --deep --strict "$source"
ditto "$source" "$stage"
codesign --verify --deep --strict "$stage"
xattr -dr com.apple.quarantine "$stage" 2>/dev/null || true
mv "$bundle" "$backup"
mv "$stage" "$bundle"
printf '%s\n%s\n%s\n' "$ack" "$nonce" "$bundle" >"$pending"
"$bundle/Contents/MacOS/molip-quest" >/dev/null 2>&1 &
candidate_pid=$!
attempt=0
while [ "$attempt" -lt 60 ]; do
  if [ -f "$ack" ] && [ "$(cat "$ack")" = "$nonce" ]; then committed=1; break; fi
  attempt=$((attempt + 1))
  sleep 0.5
done
test "$committed" -eq 1
committed=1
"#,installer=quote(installer)?,bundle=quote(bundle)?,parent=quote(parent)?,ack=quote(&ack)?,pending=quote(&pending)?,nonce=nonce))
}
