#!/usr/bin/env bash
# 몰입 퀘스트 macOS 한 줄 설치:
#   curl -fsSL https://raw.githubusercontent.com/jhs512/immersion-quest-3/main/packaging/macos/install.sh | bash
# 최신 DMG를 받아 Applications에 넣고 Java·C·Python을 진단·준비한 뒤 앱을 엽니다. curl로 받은 파일에는 격리(quarantine) 속성이 붙지 않아 Gatekeeper의
# "열지 않음" 창 없이 바로 열립니다. 이미 설치돼 있으면 앱과 환경을 최신으로 바꿉니다.
set -euo pipefail

repo=jhs512/immersion-quest-3
app="MQ.app"
# src/lib.rs data_dir(): directories crate가 macOS에서 쓰는 Application Support 경로.
support="$HOME/Library/Application Support/MolipQuest.MolipQuest"

if [ "$(uname -s)" != Darwin ]; then echo "이 설치 스크립트는 macOS 전용입니다."; exit 1; fi
case "$(uname -m)" in
  arm64) arch=arm64; python_version=3.13 ;;
  x86_64)
    if [ "$(sysctl -in sysctl.proc_translated 2>/dev/null || true)" = 1 ]; then
      echo "Apple Silicon Mac에서는 터미널의 Rosetta 실행을 해제한 뒤 다시 설치해 주세요."; exit 1
    fi
    echo "최신 설치 파일은 Apple Silicon Mac만 지원해요."; exit 1 ;;
  *) echo "지원하지 않는 Mac CPU입니다: $(uname -m)"; exit 1 ;;
esac

dest=/Applications
[ -w "$dest" ] || { dest="$HOME/Applications"; mkdir -p "$dest"; }
tmp=$(mktemp -d)
mount=""
cleanup() { [ -n "$mount" ] && hdiutil detach "$mount" -quiet 2>/dev/null; rm -rf "$tmp"; }
trap cleanup EXIT

echo "[1/3] 최신 설치 파일을 내려받습니다."
curl -fL --progress-bar -o "$tmp/molip-quest.dmg" \
  "https://github.com/$repo/releases/latest/download/molip-quest-3-macos-${arch}.dmg"
mount=$(hdiutil attach "$tmp/molip-quest.dmg" -nobrowse -readonly | awk -F'\t' '/\/Volumes\//{print $NF}' | head -n 1)
source="$mount/$app"
[ -d "$source" ] || source="$mount/몰입 퀘스트 3.app"
[ -d "$source" ] || { echo "DMG 안에서 앱을 찾지 못했습니다."; exit 1; }
# Replacing files does not restart an already running app. Quit before swapping;
# otherwise Launch Services can bring the old process back to the foreground.
osascript <<'APPLESCRIPT' >/dev/null 2>&1 || true
if application id "dev.molipquest.mq3" is running then
  tell application id "dev.molipquest.mq3" to quit
end if
APPLESCRIPT
for attempt in $(seq 1 30); do
  pgrep -x molip-quest >/dev/null || break
  sleep 1
done
if pgrep -x molip-quest >/dev/null; then
  echo "실행 중인 MQ를 종료한 뒤 설치 명령을 다시 실행해 주세요."; exit 1
fi
# Preserve prior copies in hidden folders so Spotlight/Dock do not pick an old
# copy named MQ. A previous backup must not make a third installation fail.
for old_name in "$app" "몰입 퀘스트 3.app"; do
  [ -e "$dest/$old_name" ] || continue
  identifier=$(/usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' "$dest/$old_name/Contents/Info.plist" 2>/dev/null || true)
  [ "$identifier" = dev.molipquest.mq3 ] || { echo "같은 위치의 다른 앱은 바꾸지 않습니다: $dest/$old_name"; exit 1; }
  backup=$(mktemp -d "$dest/.mq3-previous.XXXXXX")
  mv "$dest/$old_name" "$backup/$old_name"
done
ditto "$source" "$dest/$app"
hdiutil detach "$mount" -quiet; mount=""
echo "      $dest/$app"

echo "[2/3] Java·C·Python 환경을 확인하고 필요한 도구를 준비해요."
if [ -f "$dest/$app/Contents/Resources/environment-setup-v1" ]; then
  if ! "$dest/$app/Contents/MacOS/molip-quest" --prepare-environment; then
    echo "일부 도구는 추가 확인이 필요해요. 앱 설정의 환경 진단에서 결과를 확인하세요."
  fi
else
  # Do not pass new CLI options to an older GUI-only release.
  echo "이전 버전 앱에서는 Python 환경을 먼저 준비해요."
  env_dir="$support/ml-env"
  export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
  if ! command -v uv >/dev/null 2>&1; then
    curl -LsSf https://astral.sh/uv/install.sh | sh -s -- --quiet --no-modify-path
  fi
  mkdir -p "$support"
  requirements="$dest/$app/Contents/Resources/requirements-learning.txt"

  if command -v brew >/dev/null 2>&1; then
    brew list --versions libomp >/dev/null 2>&1 || brew install libomp
  fi
  uv venv "$env_dir" --python "$python_version" --clear --quiet
  uv pip install --python "$env_dir/bin/python" --quiet -r "$requirements"
  "$env_dir/bin/python" -c "import pandas, sklearn, matplotlib, tensorflow, xgboost; print('      pandas', pandas.__version__, '· scikit-learn', sklearn.__version__)" || echo "일부 Python 패키지는 앱에서 추가 확인이 필요해요."
fi

echo "[3/3] 앱을 열어요. macOS 설치 창이 표시되면 설치와 약관 확인을 완료하세요."
open "$dest/$app"
