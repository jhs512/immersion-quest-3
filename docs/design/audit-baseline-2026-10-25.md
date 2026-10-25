# MQ player · baseline audit and what the station redesign changed

Baseline: commit 132cb4b, real 자바 백엔드 과정 (34 lessons) served by the isolated validation transport (`버전 본`), 1440×900 and 820×760. Captures: `target/design-audit/before/*.png`; redesign: `target/design-audit/after/*.png`.

| Finding | Severity | Evidence (before) | Change |
| --- | --- | --- | --- |
| First lesson below the fold; the course screen opens on an always-expanded name form, help text, link and tabs | High | 02-catalog-ready | Course head on three lines, saved name folds to one line, next-station panel and the route start inside the first viewport |
| No "continue where I left off"; the learner hunts through 34 cards | High | 02, 03 | Next-station panel: most recently studied unfinished lesson from recorded event time, else first unfinished required lesson; loading shown as loading |
| 34 cards × ~260px ≈ 9000px of scroll; progress bar and share button repeated at full size | High | 03-catalog-list-end | 60px station rows on one route line; share is an icon with its full name; only the next station has a filled action |
| No all-vs-category toggle; optional lessons (27–34, `required:false`) unmarked; 8 lessons with no track show nothing | High | 03 | 전체 순서 / 분류별 toggle (disabled with its reason when the course has no approved categories); 선택 label from `required`; no track label when `track` is absent |
| Internal revision id printed as a main line on every card | Medium | 02 | Kept (tests and support rely on it) as small mono meta text |
| Lesson header: about nine equal-weight controls; progress indistinct | Medium | 11-problem-editor | Navy signage band with the course line underline; progress trigger in white tabular figures; amber underline while 관리자 자동 풀이 runs |
| Step tabs scroll sideways with no position cue; passed steps are green boxes | Medium | 11 | Step strip as stations: dot, label, connector; passed filled, current ringed and underlined; current step kept in view |
| Narration and auto-run controls move with content length | Medium | 11, 30-terminal | Controls sit in a sticky bar at the foot of the brief |
| Failure shown three times (alert box, red status line, output) | Low | 13-submit-feedback | Status line hidden while the incorrect alert is shown; run errors still print their message |
| Glyph icons (ⓘ ● ⏸ ■ ▶) stand in for icons | Low | 11, 19-auto-running | Drawn SVG icons; accessible names unchanged |
| Thick left stripe on lesson asides (blockquote) | Low | git-first step 2 | 1px paper-inset panel |

Not changed: lesson content, answers, grading, progress logic, publication, voice and speed persistence, highlight cleanup, terminal and editor behaviour, auto-run sequencing.

Not captured live: the lesson-opening stage panel (the validation transport opens lessons faster than one frame); its markup and styles are covered by `tests/js/lesson-loading-layout.test.cjs`.
