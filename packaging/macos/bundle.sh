#!/usr/bin/env bash
# Wrap the release binary in an .app bundle, sign it, and pack a .dmg.
# With MACOS_SIGN_IDENTITY set (a "Developer ID Application: …" certificate in the keychain)
# the bundle gets a hardened-runtime signature that CI can notarize. Without it the bundle is
# ad-hoc signed, which Apple Silicon needs to launch at all; Gatekeeper then blocks the first
# launch and the student follows "먼저 읽어 주세요.txt" in the image (System Settings → 그래도 열기).
set -euo pipefail
cd "$(dirname "$0")/../.."

version=$(sed -n 's/^version = "\([^"]*\)"/\1/p' Cargo.toml | head -n 1)
app="target/bundle/몰입 퀘스트.app"
rm -rf target/bundle target/installers/molip-quest-macos-arm64.dmg
mkdir -p "$app/Contents/MacOS" "$app/Contents/Resources" target/installers

cp target/release/molip-quest "$app/Contents/MacOS/molip-quest"
sed "s/APP_VERSION/$version/g" packaging/macos/Info.plist > "$app/Contents/Info.plist"
cp README.md requirements-learning.txt "$app/Contents/Resources/"

# App icon: build an .icns from the 1024px master with the system tools.
iconset=target/bundle/AppIcon.iconset
rm -rf "$iconset" && mkdir -p "$iconset"
for size in 16 32 128 256 512; do
  sips -z $size $size assets/icon/icon-1024.png --out "$iconset/icon_${size}x${size}.png" >/dev/null
  double=$((size * 2))
  sips -z $double $double assets/icon/icon-1024.png --out "$iconset/icon_${size}x${size}@2x.png" >/dev/null
done
iconutil -c icns "$iconset" -o "$app/Contents/Resources/AppIcon.icns"

if [ -n "${MACOS_SIGN_IDENTITY:-}" ]; then
  codesign --force --deep --options runtime --timestamp --sign "$MACOS_SIGN_IDENTITY" "$app"
else
  codesign --force --deep --sign - "$app"
fi

cp "packaging/macos/먼저 읽어 주세요.txt" target/bundle/
ln -s /Applications target/bundle/Applications
hdiutil create -volname "몰입 퀘스트" -srcfolder target/bundle -ov -format UDZO \
  target/installers/molip-quest-macos-arm64.dmg
