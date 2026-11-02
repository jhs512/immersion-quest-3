#!/bin/sh
# docker_trace.sh <fixture> <cpp|rust> [mode]: run the tracer in the project image against one fixture.
set -eu
root=$(cd "$(dirname "$0")/../.." && pwd)
work="$root/.scratch/native-languages/run/$(basename "$1")-${3:-trace}"
rm -rf "$work"; mkdir -p "$work/case"
cp "$1" "$work/case/src"; : > "$work/case/stdin.txt"
MSYS_NO_PATHCONV=1 docker run --rm --name "mq-native-trace-$$" --label mq.owner=mq-native-trace \
  --network none --cap-drop ALL --security-opt no-new-privileges --memory 512m --pids-limit 128 --cpus 2 \
  -v "$(cygpath -w "$root/assets/native-trace" 2>/dev/null || echo "$root/assets/native-trace"):/tool:ro" \
  -v "$(cygpath -w "$work/case" 2>/dev/null || echo "$work/case"):/case" \
  mq-native-trace:exp1 python3 /tool/native_flow.py "${3:-trace}" /case "$2" < "$work/case/stdin.txt"
echo "$work/case"
