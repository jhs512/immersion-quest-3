# Product

<!-- impeccable:product-schema 1 -->

Inferred from repository evidence (README.md, CONTEXT.md, docs/voice.md, docs/verification, src/player_ui.rs, courses/redesigned-courses) and the 2026-10-25 redesign brief; the owner delegated judgment and asked for no interview. Facts marked (inferred) await owner confirmation.

## Platform

web

The player is a Dioxus desktop app (Windows x64, macOS Apple Silicon; Android APK exists) whose UI is HTML/CSS in the system WebView. Its design language is its own, not native OS chrome.

## Users

- **학습자 (primary):** Korean-speaking students in cohort courses (e.g. 「[BE16]홍길동」 names) learning Java backend, 정보처리기사 실기 and AICE Associate. They study for long sessions on a laptop or desktop, alternating between reading a problem, editing code or typing in a real terminal, running, and submitting. Many are beginners with the shell, Git and Vim; some use macOS with a Korean IME. (inferred from course content, IME reports and cohort name examples)
- **강사·관리자 (secondary):** the course owner who checks content by letting 관리자 자동 풀이 play narration, enter the official answer, run and grade every step continuously until Esc. Only accounts with edit permission on the course repository see it.

## Product Purpose

MQ (몰입 퀘스트 3) is a learning player: one app that loads public course/lesson repositories, runs real code, terminals, Git, Vim and Java builds locally, grades submissions, narrates explanations with AI voice, and records append-only progress per learner in the course repository's GitHub issues. Success is a learner who knows where they are in a course, opens the next lesson without hunting, solves each step with the real tool, and trusts that their code, progress and recordings survive any interruption.

## Positioning

The lesson is practiced in the real tool, not a simulation: a real Bash/Git PTY, real Vim, a real JDK, with a teacher-style narrated demonstration that replays on a separate demo workspace and returns the learner's own work untouched. Progress is an open, append-only public record the learner and instructor can both read.

## Operating Context

- Desktop window, often split with other apps; also fullscreen (F11). Narrow windows around 800px wide occur.
- Long-running sessions; app may be closed at any moment (drafts saved on input, progress journaled before upload).
- Keyboard-heavy: Ctrl+Enter run, Ctrl+Shift+Enter submit, Ctrl+/ shortcut sheet, Ctrl+Alt+↑/↓ voice speed, Space/Esc for auto run.
- Network may be slow or offline; GitHub progress sync happens in the background; packaged courses bootstrap offline.

## Capabilities and Constraints

- Courses list lessons in a recommended order; learners may open any lesson. Lessons have chapters/units/steps; steps are concept sections or problems (code, choice/fill interaction, terminal, Vim, Java build, GitHub PR).
- Lesson classification: optional `category` and `track` (기본/필수/고급). Every lesson that existed on 2026-10-25 is 「기본」 by owner decision; 기본 means neither required nor easy. `required` alone decides course completion. Categories are only a proposal (tools/redesigned_courses/lesson-classification.json, status proposed) and are not shown to students until approved.
- Progress: 수업 완료 (all required problems in the current revision), 추가 학습 (a revised lesson with new required work), 복습 기록 separate. Numbers shown must come from recorded events; no invented statistics.
- Must preserve: learner code drafts, progress journal and async upload, voice choice and 0.75–3× speed persistence, narration highlight cleanup and offsets, reset-once and cumulative terminal practice, continuous next-lesson auto run until Esc with admin check, native window/editor/terminal affordances, dynamic lab ports and process ownership.
- No fixed header rows added, no obstructive help overlays, no motion without purpose; honor reduced motion.

## Brand Commitments

- Name shown as 「MQ」.
- Pretendard (bundled variable font) for UI text; JetBrains Mono for code. Owner preference recorded before this redesign.
- Voice: docs/voice.md (해요체, short sentences, Korean term first). UI strings follow the same voice.

## Evidence on Hand

- Real course manifests: courses/redesigned-courses/*.json (자바 백엔드 34 lessons, 정보처리기사 30, AICE 24).
- Student issue reviews: docs/verification/student-reports-*.md.
- No usage analytics, satisfaction scores, completion-rate benchmarks or testimonials exist; none may be fabricated.

## Product Principles

1. The learner's work is sacred: nothing in the UI may risk code, answers, progress or recordings.
2. Where am I, what's next: every screen answers position, state and the next action without a hunt.
3. Honest state: show only recorded facts; unknown classification or loading is shown as such, never guessed.
4. The real tool leads: editor and terminal get the space; chrome recedes.
5. Teacher tools stay out of the learner's way and are unmistakable when active.

## Accessibility & Inclusion

Keyboard operation for every action, visible focus, WCAG 2.2 AA contrast, reduced-motion support, Korean IME correctness in editor and terminal, readable at 14px base on 800px-wide windows.
