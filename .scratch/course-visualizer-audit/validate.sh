#!/bin/sh
# Run the lesson validator for each key in an isolated data dir (no learner files), course Python, existing TinyCC.
cd "$(dirname "$0")/../.."
export MOLIP_DATA_DIR="$(mktemp -d)"
export MOLIP_PYTHON="${MOLIP_PYTHON:-$LOCALAPPDATA/MolipQuest/MolipQuest/data/ml-env/python.exe}"
export MOLIP_TCC="$LOCALAPPDATA/MolipQuest/MolipQuest/data/course-tools/tcc-0.9.27/tcc/tcc.exe"
for key in "$@"; do
  if ./target/debug/examples/validate_redesigned_lesson.exe "tests/lesson-cases/$key.json" "target/mcq/$key.json" > "target/mcq/$key.log" 2>&1; then
    echo "PASS $key $(tail -1 target/mcq/$key.log)"
  else
    echo "FAIL $key $(tail -1 target/mcq/$key.log)"
  fi
done
rm -rf "$MOLIP_DATA_DIR"
