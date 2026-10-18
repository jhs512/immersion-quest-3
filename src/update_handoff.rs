//! Installer handoff scripts keep the old bundle until the replacement is verified.
use std::path::Path;

fn quote(path:&Path)->Result<String,String> {
    path.to_str().filter(|value|!value.contains(['\n','\r','\0'])).map(|value|format!("'{}'",value.replace('\'',"'\\''"))).ok_or("설치 경로를 확인하세요.".into())
}

pub fn macos_script(installer:&Path,bundle:&Path,pid:u32)->Result<String,String> {
    if !installer.is_absolute() || !bundle.is_absolute() || installer.extension().is_none_or(|ext|ext!="dmg") || bundle.extension().is_none_or(|ext|ext!="app") {
        return Err("설치 이미지와 앱 번들 경로를 확인하세요.".into());
    }
    let parent=bundle.parent().ok_or("앱 번들의 상위 폴더를 확인하세요.")?;
    Ok(format!(r#"set -eu
installer={installer}
bundle={bundle}
parent={parent}
log="$installer.handoff.log"
exec >>"$log" 2>&1
while kill -0 {pid} 2>/dev/null; do sleep 0.5; done
mount=$(mktemp -d "${{TMPDIR:-/tmp}}/mq3-mount.XXXXXX")
work=$(mktemp -d "$parent/.mq3-update.XXXXXX")
backup="$work/previous.app"
stage="$work/new.app"
committed=0
cleanup() {{
  keep=0
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
}}
trap cleanup EXIT
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
open -n "$bundle"
committed=1
"#,installer=quote(installer)?,bundle=quote(bundle)?,parent=quote(parent)?))
}
