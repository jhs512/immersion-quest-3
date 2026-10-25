---
version: 1
slug: "src-player-ui-rs"
primary_target: "src/player_ui.rs"
related_targets: ["src/main.rs","src/challenge_ui.rs","assets/product-ui.css"]
---

## Scope and mode

Operate. The whole learning player (src/player_ui.rs with src/main.rs shell, challenge_ui, course_guide_ui, interaction_ui, git_terminal_ui): course picker, course lesson list (all / category toggle, 기본·필수·고급 labels), lesson workspace (problem, editor, terminal, result), narration and 관리자 자동 풀이, progress and next lesson, settings, loading/error/empty states.

## Audience, job, constraints

학습자 opens a course, finds where they left off, opens the next lesson, solves steps in the real editor or terminal, submits, and moves on. 관리자 runs continuous auto review until Esc. Product truth, data safety and native affordances from PRODUCT.md bind every change; classification shown only as recorded (`track`, `required`, approved `category`), unknown shown as unknown.

## Direction contract

THESIS: The course is a metro line and each lesson a station: the learner always sees the line, where they stand on it and the next stop. Refuses the category default of a tall card grid with a progress bar on every card.

OWN-WORLD: Station-wall light ground (cool white tile) with deep navy signage bands for the shell; each course carries one saturated line colour used for its route line, station rings, current marker and primary action; editor and terminal stay dark wells set into the wall. Pretendard for all UI, tabular station numbers in line-colour rings, JetBrains Mono in code. One 1px rule weight, 6px radius, no shadows except overlays.

STORY: The learner understands which course they are on, how far along the line they are from recorded progress only, which stations are optional, and boards the next station with one action.

FIRST VIEWPORT: Catalog: navy signage band (MQ, course name, account and settings) over a two-column body: left the course switcher (line-colour chips); right a "이어서" next-station panel (lesson number ring, title, state, 학습 시작) then the vertical route of 34 compact station rows (56px), each with ring state, number, title, 기본/선택 labels and progress text. Workspace: navy band with back, lesson title and a horizontal station strip of steps; problem pane left, dark editor/terminal well right with run/submit in its header.

FORM: Seoul metro wayfinding and line map, candidate 4 of 7. seed:f7ef066bbb9340dc. Raises: from emission-line rail, state is carried by ring shape (filled, half, hollow, struck) not hue alone; from terminal yellow wayfinding, the followed destination (current lesson, current step) is restated identically on every surface; from star atlas, one fixed size ramp; from saville catalog sleeve, one element owns each screen (the code well); from centre-rail reference setting, one ruling weight; from Japanese high-density web, density courage in the station list.

Signature interaction: the route line. Catalog station rings fill from recorded progress; the current/next station is ringed and labelled; in the workspace the step strip shows passed, current and remaining stops, and moving to the next step slides the current marker 160ms along the line (instant under reduced motion).

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance

## Unresolved

- Screen theme 시스템 / 밝게 / 어둡게 (owner request, 2026-10-25): the night station is the same world re-lit; code wells stay dark in both.
- Category grouping renders only when the course manifest carries approved categories; the proposal file stays unpublished.
