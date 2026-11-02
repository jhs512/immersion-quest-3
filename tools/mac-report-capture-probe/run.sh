#!/usr/bin/env bash
# Runs the probe as an ad-hoc signed .app launched by LaunchServices (its own TCC identity, never
# granted Screen Recording), then directly from the CI shell for comparison.
set -euo pipefail
cd "$(dirname "$0")"
out="${1:?output dir}"
mkdir -p "$out"
cargo build --release --locked 2>&1 | tail -n 3
app="$out/MQCaptureProbe.app"
rm -rf "$app" && mkdir -p "$app/Contents/MacOS"
cp target/release/mac-report-capture-probe "$app/Contents/MacOS/probe"
cat > "$app/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>CFBundleExecutable</key><string>probe</string>
<key>CFBundleIdentifier</key><string>dev.molip.capture-probe.$RANDOM</string>
<key>CFBundlePackageType</key><string>APPL</string>
<key>NSHighResolutionCapable</key><true/>
</dict></plist>
PLIST
codesign --force --deep --sign - "$app"
open -W -n "$app" --args "$out/app.json"
cat "$out/app.json"
target/release/mac-report-capture-probe "$out/shell.json" || true
cat "$out/shell.json"
