# Local diagnostics and bug reports

OpenTelemetry is the only instrumentation SDK in this change. No Sentry, PostHog,
GA, remote collector or automatic usability issue submission is enabled.

## Retention

- Detailed completed spans: one hour, at most 10,000 records.
- Small navigation events (course/lesson/task identity): 180 days, at most 50,000.
- SQLite has a 64 MiB page limit. Expiration runs periodically and on read/write.
- Code, commands, terminal output, tokens, full paths and exception messages are
  excluded by an attribute allowlist. An incorrect learner answer is not an app error.

## Report interaction

The report shortcut must not rely on a healthy WebView. A separate helper process
owns an OS hotkey and opens a separate native report dialog. Ordinary UI entry can
request the same dialog. Escape remains a cancel key, not a report shortcut.
The helper takes a snapshot of retained diagnostics and captures only the player's
window, never the desktop. Screenshot failure must not prevent a textual report.

The dialog previews the capture, accepts additional comments, lets the user exclude
the capture, and sends only after confirmation. A completely frozen OS, a helper
that could not start, or unavailable capture permissions remain explicit limits.

Application reports go to `jhs512/immersion-quest-3`. The visible **문제 신고**
button in each task sends content reports to that lesson's repository. Its exact
revision and task identifier are included. The containing course is not the target.

Emergency chords (Control on both platforms, Alt = Option on Mac):
- Control + Alt + Shift + B: application bug report.
- Control + Alt + Shift + P: current lesson's problem report.

 GitHub's ordinary
issue API does not attach arbitrary local files, and its new CLI media attachment
feature requires push access. Learners generally do not have that access. Use the
reporter's existing gh account to store diagnostic files in an unlisted Gist and
link it from the issue. Unlisted is not private: the dialog must explain link access.
No new upload server or embedded GitHub credential is needed.

Preserve a compressed local report draft and its remote identifiers for safe retries
within the dialog. Keep the ten most recent local report folders. A new report
captures a new snapshot. Uploaded Gists remain available until the owner removes them.
Screenshots are self-contained `screen.html` files; full traces are gzip/base64 JSON,
with decoding described in the Gist README. They are links, not inline issue images. A test
must not submit real reports. Verify failed/lost responses with a fake transport.

## Implementation verification

Rust and WebView instrumentation, retention, context propagation, cancellation and
privacy filtering need automated checks. On Windows, suspend the main process and
verify the helper still opens a native report dialog. macOS capture permission and
native dialog behavior require validation on a Mac before claiming parity.

## Verified on Windows

The native regression test suspends its own host process, triggers the OS hotkey,
checks that the separate report dialog opens, enters additional comments, and
cancels without sending anything. It also verifies content-report repository routing.
Run `cargo test --test diagnostics_native -- --ignored --nocapture` on an interactive
Windows desktop. No GitHub issue is created by that test.
