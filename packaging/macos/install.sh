#!/usr/bin/env bash
# 몰입 퀘스트 macOS 한 줄 설치:
#   curl -fsSL https://raw.githubusercontent.com/jhs512/molip-quest/main/packaging/macos/install.sh | bash
# 최신 DMG를 받아 Applications에 넣고, 학습용 Python 환경(pandas·scikit-learn 등)을 앱 데이터 폴더에
# 만든 뒤 앱을 엽니다. curl로 받은 파일에는 격리(quarantine) 속성이 붙지 않아 Gatekeeper의
# "열지 않음" 창 없이 바로 열립니다. 이미 설치돼 있으면 앱과 환경을 최신으로 바꿉니다.
set -euo pipefail

repo=jhs512/molip-quest
app="몰입 퀘스트.app"
# src/lib.rs data_dir(): directories crate가 macOS에서 쓰는 Application Support 경로.
support="$HOME/Library/Application Support/MolipQuest.MolipQuest"
env_dir="$support/ml-env"

if [ "$(uname -s)" != Darwin ]; then echo "이 설치 스크립트는 macOS 전용입니다."; exit 1; fi
if [ "$(uname -m)" != arm64 ]; then echo "Apple Silicon(M1 이상) Mac만 지원합니다. 이 Mac은 $(uname -m)입니다."; exit 1; fi

dest=/Applications
[ -w "$dest" ] || { dest="$HOME/Applications"; mkdir -p "$dest"; }
tmp=$(mktemp -d)
mount=""
cleanup() { [ -n "$mount" ] && hdiutil detach "$mount" -quiet 2>/dev/null; rm -rf "$tmp"; }
trap cleanup EXIT

echo "[1/3] 최신 설치 파일을 내려받습니다."
curl -fL --progress-bar -o "$tmp/molip-quest.dmg" \
  "https://github.com/$repo/releases/latest/download/molip-quest-macos-arm64.dmg"
mount=$(hdiutil attach "$tmp/molip-quest.dmg" -nobrowse -readonly | awk -F'\t' '/\/Volumes\//{print $NF}' | head -n 1)
[ -d "$mount/$app" ] || { echo "DMG 안에서 앱을 찾지 못했습니다."; exit 1; }
rm -rf "$dest/$app"
ditto "$mount/$app" "$dest/$app"
xattr -dr com.apple.quarantine "$dest/$app" 2>/dev/null || true
hdiutil detach "$mount" -quiet; mount=""
echo "      $dest/$app"

echo "[2/3] 학습용 Python 환경을 준비합니다 (처음에는 몇 분 걸립니다)."
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh -s -- --quiet --no-modify-path
fi
mkdir -p "$support"
uv venv "$env_dir" --python 3.13 --quiet
uv pip install --python "$env_dir/bin/python" --quiet -r "$dest/$app/Contents/Resources/requirements-learning.txt"
"$env_dir/bin/python" -c "import pandas, sklearn, matplotlib; print('      pandas', pandas.__version__, '· scikit-learn', sklearn.__version__)"

echo "[3/3] 앱을 엽니다. 앱 안의 「환경 진단」에서 모두 준비됨인지 확인하세요."
open "$dest/$app"
