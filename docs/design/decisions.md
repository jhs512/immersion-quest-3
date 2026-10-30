## 2026-10-30 · Every popup is paper of the current look; every disabled button shares one legible look
- Decided by: owner report (screenshots: 진도 초기화 with an invisible title, a faint 닫기, a literal @{user.login}, a clipped sentence; the GitHub check screen with faint band buttons mid-screen) and the follow-up 「라이트 모드 전체 버튼이랑 팝업 다 점검」.
- Why: Dialogs and the 환경 진단 panel live inside the navy band in the DOM and inherited its light ink, one-line layout and transparent band buttons; the code-flow dialog lives on <body> outside every button rule; a disabled primary drew white text on a pale tint. Popups now take the paper tokens (dialog and [role=dialog] inside the band, the code-flow dialog, 환경 진단 checks by surface tint with a 1px rule), the band stays on top on the GitHub screens, and every disabled button is paper-2 / rule / ink-3 (≥5:1). Modal state follows the native cancel (Esc with focus anywhere), and the first focus is inside the dialog.
- Rejected: Recolouring only the reported dialog; a thick coloured side stripe for check states.
- Rests on: tools/design-scenarios/ui-inventory.cjs, account-reset-dialog.cjs, modal-cycle.cjs, doctor-check.cjs, git-graph-themes.cjs captures.

## 2026-10-30 · 밝게 lights the code wells too: editor, terminal, output and Git graph follow the theme
- Decided by: owner (reported that choosing 밝게 still showed a dark editor and terminal; asked that the whole screen match light mode)
- Why: A light choice that leaves the largest surface dark reads as broken. The well, editor (CodeMirror via CSS variables plus its dark flag), terminal (xterm palette swapped live on mq-theme) and Git graph now take per-theme tokens; 어둡게 keeps the night well unchanged.
- Rejected: Keeping dark wells in both looks (the 2026-10-25 decisions below, now superseded); an invert filter (breaks syntax and status colours).
- Supersedes: "The editor and terminal stay dark wells in both themes" and the "code wells stay dark" half of the station-wall decision.
- Rests on: assets/station.css "Code wells per theme"; tools/design-scenarios/light-audit.cjs captures.

## 2026-10-25 · PRODUCT.md is written from repository evidence without an interview
- Decided by: Claude (default; owner delegated judgment)
- Why: The brief asked for no unneeded interviews; README, CONTEXT.md, voice.md, course manifests and student reports answer users, purpose, constraints and voice.
- Rejected: A three-question init round, because the owner said the answers were delegated.
- Rests on: 2026-10-25 redesign brief; PRODUCT.md "Inferred from" line.

## 2026-10-25 · The assigned direction, the Seoul metro line map, is built without a decision page round
- Decided by: Claude (default; owner delegated judgment)
- Why: concept-seed assigned candidate 4 of 7 (seed:f7ef066bbb9340dc); the owner asked for an implemented preview, not a choice round.
- Rejected: Presenting three cards and waiting; the airport yellow wayfinding challenger held product clarity but lost audience identification; the other five challengers were declined and donated one discipline each (listed in the surface brief).
- Rests on: .impeccable/surfaces/src-player-ui-rs.md.

## 2026-10-25 · The shell becomes a light station-wall ground with navy signage bands; code wells stay dark
- Decided by: Claude (default)
- Why: Learners read Korean prose for hours in lit classrooms and at desks; dark text on light reads better for prose, while editor and terminal keep their dark, familiar tool look.
- Rejected: Keeping the all-dark navy shell, because that polishes the discarded look; a full light theme including code wells, because it would change the editor and terminal the learner already trusts.
- Rests on: PRODUCT.md Operating Context; baseline screens target/design-audit/before.

## 2026-10-25 · Lesson cards become 56px station rows on one route line, with a next-station panel above
- Decided by: Claude (default)
- Why: The baseline put lesson 1 below the 900px fold and needed about 9000px to scroll 34 lessons; learners return to resume, so the next lesson must be the first thing seen.
- Rejected: A card grid (same scroll problem in two columns); hiding the list behind a "continue" screen (hides free choice the course promises).
- Rests on: target/design-audit/before/02-catalog-ready.png, 03-catalog-list-end.png.

## 2026-10-25 · The list toggle is 「전체 순서」 / 「분류별」, and 분류별 is disabled with its reason when the course has no approved categories
- Decided by: Claude (default)
- Why: The brief asks for an all-vs-category toggle; the shipped manifests have no approved categories, and the proposal file is not student-approved, so the grouped view must not invent groups.
- Rejected: Reading tools/redesigned_courses/lesson-classification.json at runtime (publishes an unapproved proposal); hiding the toggle (the learner cannot learn that grouping exists).
- Rests on: src/lesson_categories.rs; lesson-classification.json status "proposed".

## 2026-10-25 · Optional lessons are labelled 「선택」 from `required:false`; a missing `track` shows no track label
- Decided by: Claude (default)
- Why: Lessons 27–34 of 자바 백엔드 are not counted toward completion but the baseline did not say so; `required` is recorded fact, `track` absence is unknown and must not be guessed.
- Rejected: Labelling unknown tracks 「기본」 (an invented classification); a 「미분류」 chip on every unlabelled card (noise without a decision).
- Rests on: courses/redesigned-courses/java-backend.json; PRODUCT.md Capabilities.

## 2026-10-25 · The next station is the most recently studied unfinished lesson
- Decided by: Claude (default)
- Why: In the first build the panel pointed at lesson 1 after the learner had just studied lesson 2; recorded event time (`at`) already says where the learner left off, so the panel uses it and falls back to the first unfinished required lesson when there is no history.
- Rejected: Recommended order only (sends a returning learner back to a lesson they skipped on purpose); a separate "recent lessons" list (a second place to look).
- Rests on: target/design-audit/iter2/40-catalog-after-study.png; src/issue_progress.rs LearningEvent.at.

## 2026-10-25 · The narration and auto-run controls sit in a sticky bar at the foot of the problem brief
- Decided by: Claude (default)
- Why: In the baseline the bar moved with the length of each brief; a fixed place keeps 해설 재생, 멈춤, speed and 관리자 자동 풀이 findable without scrolling, without adding a header row.
- Rejected: Moving them into the lesson band (breaks the 42px band budget the toolbar tests enforce).
- Rests on: tests/js/compact-toolbar.test.cjs; tools/player-pilot-auto-review.js layout checks.

## 2026-10-25 · Evaluation substitutions
- Decided by: Claude (default)
- Why: This harness has no subagent tool, so the Impeccable finish review and documenter ran inline from their degraded instructions; the decision page was not served because the owner delegated the direction choice.
- Rejected: Skipping the finish review or DESIGN.md.
- Rests on: impeccable reference/degraded/finish-reviewer.md, degraded/documenter.md.

## 2026-10-25 · Screen theme: 시스템 / 밝게 / 어둡게, default 시스템, stored in prefs.json
- Decided by: owner (feature and default); Claude (storage and mechanism, default)
- Why: The owner asked for a real selector where 시스템 follows the OS now and at runtime and explicit choices hold. prefs.json already holds per-computer display preferences and is read before the window opens, so the choice can be written into the page head before the first paint; missing fields (older files) and unknown values resolve to 시스템.
- Rejected: localStorage (only readable after the page loads, so explicit dark would flash light, and the pilot profile is per run); a CSS-only toggle without stored state; an invert filter for dark (breaks syntax colours, images and the narration highlight).
- Rests on: src/prefs.rs ThemeChoice; target/design-audit/theme-restart, theme-corrupt, theme-broken, theme-legacy capture notes.

## 2026-10-25 · The editor and terminal stay dark wells in both themes
- Decided by: Claude (default)
- Why: The editor and xterm bundles carry their own dark syntax and ANSI palettes; keeping one well across looks keeps code legible and identical whatever the shell does, with no second palette to keep in sync.
- Rejected: A light editor and terminal for 밝게 (new syntax and ANSI palettes, terminal colour regressions in lessons that print coloured output).
- Rests on: target/design-audit/theme/t10-problem-dark.png, t22-problem-light.png.

## 2026-10-25 · Dark draws each course line in a brighter tone of the same hue
- Decided by: Claude (default)
- Why: The engineer blue (1.96:1), purple and magenta lines fall below 3:1 on dark paper; a per-course bright tone (≥6:1) keeps rings, route and labels legible while filled actions keep the darker ink under white text (≥5.8:1).
- Rejected: One shared accent in dark (loses which course is open).
- Rests on: contrast calculations in this session; tests/js/theme.test.cjs.
