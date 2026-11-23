#!/usr/bin/env bash
# Developer ID signing and notarization for the MQ.app / DMG that bundle.sh builds.
#
#   developer_id.sh keychain-setup   import MQ_MAC_DEVELOPER_ID_P12_* into a temporary keychain
#                                    and write MACOS_SIGN_IDENTITY / MQ_MAC_KEYCHAIN to $GITHUB_ENV
#   developer_id.sh sign-app APP     sign every nested Mach-O inside-out, then the bundle
#   developer_id.sh sign-dmg DMG     sign the disk image
#   developer_id.sh notarize PATH    submit (.app is zipped), wait, require Accepted, staple
#   developer_id.sh verify-app APP   strict signature, hardened runtime, entitlements, Gatekeeper, ticket
#   developer_id.sh verify-dmg DMG   signature, Gatekeeper open check, ticket
#   developer_id.sh keychain-cleanup remove the temporary keychain
#
# Every check exits non-zero on failure, so a release can never carry an unsigned or
# unnotarized image. Notary auth: an App Store Connect API key (MQ_MAC_NOTARY_KEY_ID,
# MQ_MAC_NOTARY_ISSUER_ID, MQ_MAC_NOTARY_KEY_P8_BASE64), or else an Apple ID with an
# app-specific password (MQ_MAC_NOTARY_APPLE_ID, MQ_MAC_NOTARY_APP_PASSWORD, MQ_MAC_NOTARY_TEAM_ID).
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
entitlements="$here/MQ.entitlements"
work="${RUNNER_TEMP:-${TMPDIR:-/tmp}}"

die() { echo "developer_id: $*" >&2; exit 1; }
need() { for name in "$@"; do [ -n "${!name:-}" ] || die "$name is not set"; done; }

keychain_setup() {
  need MQ_MAC_DEVELOPER_ID_P12_BASE64 MQ_MAC_DEVELOPER_ID_P12_PASSWORD
  local keychain="$work/mq-signing.keychain-db" p12="$work/mq-developer-id.p12" password
  password="$(uuidgen)"
  rm -f "$keychain"
  security create-keychain -p "$password" "$keychain"
  security set-keychain-settings -lut 21600 "$keychain"
  security unlock-keychain -p "$password" "$keychain"
  ( umask 077; printf '%s' "$MQ_MAC_DEVELOPER_ID_P12_BASE64" | base64 --decode > "$p12" )
  # security import cannot read OpenSSL 3's default PKCS#12 (PBES2/AES-256, SHA-256 MAC) and
  # reports it as "MAC verification failed (wrong password?)". Open it with OpenSSL 3, which
  # tells a wrong password apart, and repack it as SHA1/3DES PKCS#12 for the import.
  local openssl pem="$work/mq-developer-id.pem" legacy="$work/mq-developer-id-legacy.p12" transit
  openssl="$(brew --prefix openssl@3 2>/dev/null)/bin/openssl"
  [ -x "$openssl" ] || die "OpenSSL 3 (brew openssl@3) is required to read the certificate"
  transit="$(uuidgen)"
  ( umask 077
    MQ_P12_PASSWORD="$MQ_MAC_DEVELOPER_ID_P12_PASSWORD" "$openssl" pkcs12 -in "$p12" -passin env:MQ_P12_PASSWORD -noenc -out "$pem" \
      || { rm -f "$p12" "$pem"; echo "developer_id: MQ_MAC_DEVELOPER_ID_P12_PASSWORD does not open MQ_MAC_DEVELOPER_ID_P12_BASE64" >&2; exit 1; }
    MQ_P12_TRANSIT="$transit" "$openssl" pkcs12 -export -in "$pem" -keypbe PBE-SHA1-3DES -certpbe PBE-SHA1-3DES -macalg sha1 \
      -passout env:MQ_P12_TRANSIT -out "$legacy" )
  rm -f "$p12" "$pem"
  security import "$legacy" -k "$keychain" -P "$transit" -T /usr/bin/codesign -T /usr/bin/security >/dev/null
  rm -f "$legacy"
  # The identity is only valid with its issuer; runners may not have Apple's current intermediate.
  curl -fsSL --retry 3 https://www.apple.com/certificateauthority/DeveloperIDG2CA.cer -o "$work/DeveloperIDG2CA.cer"
  security import "$work/DeveloperIDG2CA.cer" -k "$keychain" >/dev/null 2>&1 || true
  rm -f "$work/DeveloperIDG2CA.cer"
  security set-key-partition-list -S apple-tool:,apple:,codesign: -s -k "$password" "$keychain" >/dev/null
  # Keep the login keychain searchable and put ours first.
  local existing=() line
  while IFS= read -r line; do line="${line#"${line%%[![:space:]]*}"}"; existing+=("${line//\"/}"); done < <(security list-keychains -d user)
  security list-keychains -d user -s "$keychain" "${existing[@]}"
  local identity
  identity="$(security find-identity -v -p codesigning "$keychain" | awk '/"Developer ID Application: /{print $2; exit}')"
  [ -n "$identity" ] || die "the p12 holds no valid Developer ID Application identity"
  if [ -n "${GITHUB_ENV:-}" ]; then
    { echo "MACOS_SIGN_IDENTITY=$identity"; echo "MQ_MAC_KEYCHAIN=$keychain"; } >> "$GITHUB_ENV"
  else
    echo "MACOS_SIGN_IDENTITY=$identity"; echo "MQ_MAC_KEYCHAIN=$keychain"
  fi
}

keychain_cleanup() {
  local keychain="${MQ_MAC_KEYCHAIN:-$work/mq-signing.keychain-db}"
  [ -e "$keychain" ] && security delete-keychain "$keychain" || true
  rm -f "$work/mq-developer-id.p12" "$work/mq-developer-id.pem" "$work/mq-developer-id-legacy.p12" "$work/mq-notary-key.p8"
}

# Options shared by every signature; the keychain is pinned when keychain-setup made one.
signing=(--force --timestamp)
if [ -n "${MQ_MAC_KEYCHAIN:-}" ]; then signing+=(--keychain "$MQ_MAC_KEYCHAIN"); fi

sign_app() {
  local app="$1" executable main file
  need MACOS_SIGN_IDENTITY
  [ -d "$app/Contents/MacOS" ] || die "$app is not an app bundle"
  executable="$(/usr/libexec/PlistBuddy -c 'Print :CFBundleExecutable' "$app/Contents/Info.plist")"
  main="$app/Contents/MacOS/$executable"
  # Nested code first (helpers, dylibs, extra executables), deepest paths first, then the bundle.
  while IFS= read -r file; do
    [ "$file" = "$main" ] && continue
    if file -b "$file" | grep -q 'Mach-O'; then
      codesign "${signing[@]}" --options runtime --sign "$MACOS_SIGN_IDENTITY" "$file"
    fi
  done < <(find "$app/Contents" -type f \( -perm -u+x -o -name '*.dylib' -o -name '*.so' \) | awk '{print length, $0}' | sort -rn | cut -d' ' -f2-)
  codesign "${signing[@]}" --options runtime --entitlements "$entitlements" --sign "$MACOS_SIGN_IDENTITY" "$app"
}

sign_dmg() {
  need MACOS_SIGN_IDENTITY
  codesign "${signing[@]}" --sign "$MACOS_SIGN_IDENTITY" "$1"
}

notary_auth() {
  if [ -n "${MQ_MAC_NOTARY_KEY_ID:-}" ]; then
    need MQ_MAC_NOTARY_ISSUER_ID MQ_MAC_NOTARY_KEY_P8_BASE64
    local key="$work/mq-notary-key.p8"
    printf '%s' "$MQ_MAC_NOTARY_KEY_P8_BASE64" | base64 --decode > "$key"
    chmod 600 "$key"
    notary=(--key "$key" --key-id "$MQ_MAC_NOTARY_KEY_ID" --issuer "$MQ_MAC_NOTARY_ISSUER_ID")
  elif [ -n "${MQ_MAC_NOTARY_APPLE_ID:-}" ]; then
    need MQ_MAC_NOTARY_APP_PASSWORD MQ_MAC_NOTARY_TEAM_ID
    notary=(--apple-id "$MQ_MAC_NOTARY_APPLE_ID" --password "$MQ_MAC_NOTARY_APP_PASSWORD" --team-id "$MQ_MAC_NOTARY_TEAM_ID")
  else
    die "no notary credentials: set MQ_MAC_NOTARY_KEY_ID/ISSUER_ID/KEY_P8_BASE64 (or APPLE_ID/APP_PASSWORD/TEAM_ID)"
  fi
}

notarize() {
  local target="$1" upload="$1" result id status
  notary_auth
  if [ -d "$target" ]; then
    upload="$work/$(basename "$target" .app)-notarize.zip"
    rm -f "$upload"
    ditto -c -k --sequesterRsrc --keepParent "$target" "$upload"
  fi
  result="$work/notary-$(basename "$target").json"
  xcrun notarytool submit "$upload" "${notary[@]}" --wait --timeout 30m --output-format json > "$result"
  id="$(/usr/bin/plutil -extract id raw -o - "$result")"
  status="$(/usr/bin/plutil -extract status raw -o - "$result")"
  echo "notary submission $id: $status"
  if [ "$status" != Accepted ]; then
    xcrun notarytool log "$id" "${notary[@]}" || true
    die "notarization of $target was $status"
  fi
  [ "$upload" = "$target" ] || rm -f "$upload"
  xcrun stapler staple "$target"
  xcrun stapler validate "$target"
}

verify_app() {
  local app="$1" details
  codesign --verify --deep --strict --verbose=2 "$app"
  details="$(codesign -dvv "$app" 2>&1)"
  grep -q '^Authority=Developer ID Application: ' <<<"$details" || die "$app is not signed with Developer ID Application"
  grep -Eq '^CodeDirectory .*flags=.*runtime' <<<"$details" || die "$app has no hardened runtime"
  grep -q '^Timestamp=' <<<"$details" || die "$app has no secure timestamp"
  # The signed entitlements must be exactly the reviewed file.
  diff <(codesign -d --entitlements - --xml "$app" 2>/dev/null | plutil -convert xml1 -o - -) \
       <(plutil -convert xml1 -o - "$entitlements") >/dev/null || die "$app entitlements differ from $entitlements"
  spctl -a -t exec -vv "$app"
  xcrun stapler validate "$app"
}

verify_dmg() {
  local dmg="$1" details
  codesign --verify --strict --verbose=2 "$dmg"
  details="$(codesign -dvv "$dmg" 2>&1)"
  grep -q '^Authority=Developer ID Application: ' <<<"$details" || die "$dmg is not signed with Developer ID Application"
  grep -q '^Timestamp=' <<<"$details" || die "$dmg has no secure timestamp"
  spctl -a -t open --context context:primary-signature -vv "$dmg"
  xcrun stapler validate "$dmg"
}

command="${1:-}"; shift || true
case "$command" in
  keychain-setup) keychain_setup ;;
  keychain-cleanup) keychain_cleanup ;;
  sign-app) sign_app "$@" ;;
  sign-dmg) sign_dmg "$@" ;;
  notarize) notarize "$@" ;;
  verify-app) verify_app "$@" ;;
  verify-dmg) verify_dmg "$@" ;;
  *) die "usage: developer_id.sh keychain-setup|keychain-cleanup|sign-app APP|sign-dmg DMG|notarize PATH|verify-app APP|verify-dmg DMG" ;;
esac
