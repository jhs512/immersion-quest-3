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
- Confirm writes `github-signed-out` (JSON: login and gh result) into MQ's data dir first, then runs `gh auth logout --hostname github.com --user <login>` with `GH_TOKEN`/`GITHUB_TOKEN` removed for that child only.
- While the marker exists every gh call path returns `SIGNED_OUT_ERROR` without spawning gh, and startup shows the signed-out screen instead of connecting. Only 다시 연결 removes the marker.
- Signed-out screen reports removed / already absent / failed (with 토큰 삭제 다시 시도), the account gh switched to, any token variable still set, and the revoke link.
- Progress journal, drafts and course snapshots are untouched (pilot digest of the data dir showed no changed file).

## Verification
- `cargo test --lib github_logout` (6 tests).
- Native pilot (fake `mq3-validation`, temp data and WebView folder, gh never runs): `node tools/design-capture.cjs .scratch/mq-logout/logout-scenario.cjs <out>` with `MQ_LOGOUT_STEP=logout|restart`, `MQ3_CAPTURE_DATA_DIR`, `MOLIP_PILOT_LOGOUT=switched|absent|failed`.

## Open
- macOS run not done on this machine; data dir comes from `directories::ProjectDirs` as before.
- Signing in again as a different account leaves the old account's unsent progress waiting until that account reconnects (journal is keyed by user id; unchanged behaviour).

## Review round 1 (fixed in the follow-up commit)
- The updater skips only the gh download branch when signed out and uses the public asset URL.
- The marker keeps gh's result, so a failed or unverified removal (with 토큰 삭제 다시 시도) survives a restart.
- An unreadable marker or data folder counts as signed out (fail closed).
- gh auth logout has a 30 s deadline. NO_COLOR is set and CLICOLOR_FORCE/GH_FORCE_TTY are removed for that child.
- busy is held during logout (lesson links wait), connect() clears an open lesson, and 다시 연결 waits for a running retry.

## Review round 2
- Fixes 1, 2 and 4 to 7 confirmed. The lesson-link race was only partly closed. Now 로그아웃 cannot be confirmed while another task holds busy, and a link load that finishes after logout is discarded.
- A failed 토큰 삭제 다시 시도 now shows its error.
- Accepted: if `data_dir()` itself fails, MQ counts as signed out and 다시 연결 cannot clear it (fail closed; same folder failure blocks the app's other storage too).

## Root review follow-up
- GitHub PR practice: `github_json` (grading reads) calls `ensure_signed_in` before starting gh. The practice terminal's git credential helper is now `github_logout::git_credential_helper`: a shell function that checks the marker on every git credential request and exits before gh when signed out. A terminal opened before logout therefore gets no credential afterwards. With no usable marker path the helper is empty, which resets git's helper list.
- Test `practice_git_stops_asking_gh_for_credentials_once_signed_out` uses real git and sh, a fake gh script, `GIT_CONFIG_NOSYSTEM` and a temp global config. Signed in: git gets the fake credential. With the marker: no credential, and the fake gh is never started. Mutation check: removing the marker test from the helper makes it fail.
- Not covered: a learner typing `gh` by hand in a practice terminal opened before logout runs their own gh. MQ does not kill or wrap processes it does not own.
- release.yml: Windows and macOS each get a "Verify GitHub logout with a fake gh" step running `cargo test --release --locked --lib github_logout::tests`. That filter matches only the 7 logout tests, and none of the existing filters match them.
- Baseline (not fixed here): both lib failures reproduce at 215b109c in a separate temp worktree and target folder, with the same values. `java_trace::tests::vendored_core_matches_the_recorded_upstream_bytes`: core/render.js is ea6786… but expected 275db1…, and the committed blob already hashes to ea6786…. `course_authoring_tests::redesigned_defaults…`: java-backend.json has 48 lessons but expected 44. The fixtures are byte-identical in 215b109c and this branch. fix/all-course-spacing 9791d8f1 changes only aice-associate and engineer-practical (lesson counts unchanged, 24 and 30) and has the same java-backend.json and java-trace files.
