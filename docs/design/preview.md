# Station redesign · local preview

Branch `design/mq3-comprehensive-intent-20261025`, worktree `C:\Users\jangk\Documents\Codex\2026-10-12\mq3-comprehensive-design`. Validation mode only: no GitHub account, no real progress, no real student data.

## Open it yourself (Windows, PowerShell)

```powershell
cd C:\Users\jangk\Documents\Codex\2026-10-12\mq3-comprehensive-design
cargo build --locked --bin molip-quest
$env:MOLIP_PILOT='1'
& .\target\debug\molip-quest.exe
```

Then open 「개발 검증 도구」 (bottom right) and press 「버전 본」 for the real 자바 백엔드 과정 (34 lessons) or 「버전 분」 for the same course with the unapproved category proposal applied (to see 분류별). Enter any course name and press 「이름 저장 후 시작」. The theme is in 「앱 설정」 → 화면 테마.

Each launch without `MOLIP_PILOT_DIRECTORY` uses a fresh temporary folder, so the theme choice is kept only while that folder is reused. To check restart persistence by hand, set `MOLIP_PILOT_DIRECTORY` and `MOLIP_PILOT_OWNER` as `tools/design-capture.cjs` does.

## Repeatable captures

```powershell
node tools\design-capture.cjs tools\design-scenarios\flows.cjs target\design-audit\after
node tools\design-capture.cjs tools\design-scenarios\theme.cjs target\design-audit\theme
node tools\design-capture.cjs tools\design-scenarios\review.cjs .impeccable\review
```

Each run starts its own app with a private folder and a DevTools port chosen by the OS (port 0, 127.0.0.1), and stops only the process it started. The theme scenario emulates the OS colour scheme through DevTools; it never changes the Windows setting.
