#!/usr/bin/env bash
# Wrap the release binary in an .app bundle, sign it, and pack a .dmg.
# With MACOS_SIGN_IDENTITY set (a "Developer ID Application: …" certificate in the keychain)
# the bundle gets a hardened-runtime signature that CI can notarize. Without it the bundle is
# ad-hoc signed, which Apple Silicon needs to launch at all; Gatekeeper then blocks the first
# launch and the student follows "먼저 읽어 주세요.txt" in the image (System Settings → 그래도 열기).
set -euo pipefail
cd "$(dirname "$0")/../.."

version=$(sed -n 's/^version = "\([^"]*\)"/\1/p' Cargo.toml | head -n 1)
arch="${MQ3_MAC_ARCH:-$(uname -m)}"
case "$arch" in arm64|x86_64) ;; *) echo "Unsupported Mac architecture: $arch" >&2; exit 1 ;; esac
app="target/bundle/MQ.app"
image="target/installers/molip-quest-3-macos-${arch}.dmg"
rm -rf target/bundle
rm -f "$image"
mkdir -p "$app/Contents/MacOS" "$app/Contents/Resources" target/installers

cp target/release/molip-quest "$app/Contents/MacOS/molip-quest"
sed -e "s/APP_VERSION/$version/g" -e "s/APP_BUILD/${MOLIP_BUILD:-0}/g" packaging/macos/Info.plist > "$app/Contents/Info.plist"
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
python3 packaging/macos/create_dmg.py --volume "MQ" \
  --source target/bundle --destination "$image"
