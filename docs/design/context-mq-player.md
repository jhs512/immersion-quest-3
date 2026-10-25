# MQ player · whole-product redesign (station world)

## Users

- 학습자: cohort students working through 자바 백엔드 (34 lessons), 정보처리기사 실기 (30) and AICE Associate (24) in long desktop sessions, alternating between a problem brief, a real editor or terminal, runs and submissions. Many meet Bash, Git and Vim for the first time; some type Korean through a macOS IME [docs/verification/macos-ime-2026-10-24.md].
- 관리자: the course owner, who replays narration and grades every step with 관리자 자동 풀이 until Esc, only on courses where the GitHub account can edit the course repository [src/player_ui.rs].

## Product

A Dioxus desktop learning player (Windows, macOS; WebView UI) that loads public course and lesson repositories, runs code, terminals, Git, Vim and Java builds locally, narrates explanations with AI voice, and keeps an append-only progress record per learner in the course repository [README.md, CONTEXT.md]. Free; no business model in the UI.

## Constraints

- Learner code drafts, progress journal and background upload, voice and 0.75–3× speed persistence, narration highlight cleanup, reset-once and cumulative practice, continuous next-lesson auto run until Esc with admin check, window/editor/terminal affordances and lab ports are behaviour that the redesign must not touch.
- Lesson classification shows only recorded data: `track` (every lesson that existed on 2026-10-25 is 기본, which is neither required nor easy), `required` (course completion), and `category` only when approved in the course manifest. The category proposal file is not student-approved.
- Lesson band ≤42px and catalog band ≤50px on windows 700px and wider; no added header row; no obstructive help; motion only for state, removed under reduced motion.
- Pretendard for UI text and JetBrains Mono for code are bundled and kept.

## Ethical stance

Utility over engagement. No streaks, badges, fake counts or completion nudges; every number on screen comes from recorded events. The continuous auto run is an admin tool, visible in amber the whole time it runs and stopped by Esc or the stop button. No new data collection.

## Success

- A returning learner finds and opens the lesson they last studied in one action from the course screen.
- Every lesson state on the route is read correctly from shape and text alone (no colour-only state).
- Existing pilot, layout and native regression checks pass unchanged in meaning.

## Open questions

- Should the shell offer a dark variant for evening study, or is the light station wall with dark code wells enough?
