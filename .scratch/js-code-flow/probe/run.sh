#!/bin/sh
# usage: run.sh <main.js> [stdin text]  -> prints summary of the trace document
set -e
root=$(mktemp -d)
mkdir -p "$root/ws" "$root/cap"
cp "$1" "$root/ws/main.js"
printf '%s' "${2:-}" > "$root/stdin.txt"
node "$(dirname "$0")/../../../assets/js-trace/mq_jstrace.cjs" "$root/ws" "$root/stdin.txt" "$root/cap" "$root/out.json" ${BUDGET:-1000} ${DEADLINE:-20000}
echo "$root/out.json"
