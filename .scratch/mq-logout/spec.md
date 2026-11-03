# GitHub 로그아웃 (토큰 삭제)

Status: implemented, awaiting root review

## Request
Add a logout button that deletes the stored GitHub token, so a learner can undo the gh login MQ relies on.

## Facts found
- MQ stores no token. Every GitHub call goes through the installed `gh` (`course_authoring::gh`, `updater::download`, `bug_report::gh_request`); `github_player.rs` says the player never copies a token.
- gh keeps the token in the OS store (Windows Credential Manager / macOS Keychain, service `gh:github.com`) or, as fallback, in `hosts.yml` under the gh config dir (`%AppData%\GitHub CLI` on Windows, `~/.config/gh` on macOS, or `GH_CONFIG_DIR`). MQ does not touch these directly; it asks gh.
- `gh auth logout --help` (gh 2.87.3): removes the stored configuration locally and "does not revoke authentication tokens". Revocation is GitHub settings, Applications, GitHub CLI, Revoke Access, which revokes gh tokens on all devices.
- Probed with real gh 2.87.3 on a fake host in a temp `GH_CONFIG_DIR` (never github.com, so no real keyring entry):
  - logging out the active one of two accounts prints `✓ Switched active account for <host> to <other>` (exit 0);
  - an absent account prints `not logged in to <host> account <x>` / `not logged in to any hosts` (exit 1);
  - with a token variable set, gh refuses: `The value of the ... environment variable is being used for authentication.` (exit 1).
- gh with a single account on a host also deletes the keyring entry `gh:<host>` with an empty user. Never run gh logout against github.com in tests.

## Behaviour
- Header button 로그아웃 next to 진도 초기화 opens a confirm dialog (취소 / Esc changes nothing).
- Confirm writes `github-signed-out` (the login) into MQ's data dir first, then runs `gh auth logout --hostname github.com --user <login>` with `GH_TOKEN`/`GITHUB_TOKEN` removed for that child only.
- While the marker exists every gh call path returns `SIGNED_OUT_ERROR` without spawning gh, and startup shows the signed-out screen instead of connecting. Only 다시 연결 removes the marker.
- Signed-out screen reports removed / already absent / failed (with 토큰 삭제 다시 시도), the account gh switched to, any token variable still set, and the revoke link.
- Progress journal, drafts and course snapshots are untouched (pilot digest of the data dir showed no changed file).

## Verification
- `cargo test --lib github_logout` (5 tests).
- Native pilot (fake `mq3-validation`, temp data and WebView folder, gh never runs): `node tools/design-capture.cjs .scratch/mq-logout/logout-scenario.cjs <out>` with `MQ_LOGOUT_STEP=logout|restart`, `MQ3_CAPTURE_DATA_DIR`, `MOLIP_PILOT_LOGOUT=switched|absent|failed`.

## Open
- macOS run not done on this machine; data dir comes from `directories::ProjectDirs` as before.
- Signing in again as a different account leaves the old account's unsent progress waiting until that account reconnects (journal is keyed by user id; unchanged behaviour).
