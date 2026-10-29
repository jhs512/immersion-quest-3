---
name: MQ
description: A learning player where each course is a metro line and each lesson a station.
colors:
  station-wall: "#eef1f5"
  paper: "#ffffff"
  paper-inset: "#f6f8fa"
  rule: "#d3dae3"
  rule-strong: "#7d8a9c"
  ink: "#152233"
  ink-secondary: "#4b5b6d"
  ink-tertiary: "#5c6b7e"
  signage-navy: "#1c2b4a"
  signage-navy-raised: "#253858"
  signage-muted: "#b6c3da"
  focus-blue: "#1f5fd6"
  focus-on-navy: "#8fb8ff"
  java-line: "#009b4c"
  java-line-ink: "#00703a"
  engineer-line: "#0052a4"
  aice-line: "#e0700f"
  aice-line-ink: "#a64a00"
  pass-green: "#11753f"
  fail-red: "#b42318"
  admin-amber: "#ffc04d"
  admin-amber-ink: "#8a4b00"
  admin-amber-soft: "#fff3d6"
  voice-violet: "#6b46c1"
  voice-violet-soft: "#efe9fb"
  challenge-purple-ink: "#7b1fa2"
  challenge-purple-soft: "#f6e7fa"
  night-challenge-ink: "#e2a8f2"
  night-challenge-fill: "#a64ccc"
  well: "#111a27"
  well-raised: "#18233a"
  well-rule: "#33445c"
  well-ink: "#e3ebf5"
  well-muted: "#a9b8ca"
  paper-hover: "#e9eef4"
  paper-pressed: "#dde4ec"
  link-hover: "#123f94"
  signage-rule: "#3c5175"
  signage-rule-strong: "#5a6f93"
  scrollbar: "#a7b2c0"
  handle: "#8d9aab"
  inline-code: "#7a2e0e"
  voice-violet-deep: "#5a37ad"
  voice-disabled-ink: "#6f6290"
  admin-amber-hover: "#ffe7ad"
  admin-amber-rule: "#e9c36f"
  admin-amber-dark: "#2b1a00"
  stop-red-deep: "#912018"
  error-toast: "#4a1410"
  well-deep: "#0c131e"
  well-control: "#22314a"
  well-control-hover: "#2b3d5b"
  well-control-rule: "#3d5170"
  well-control-rule-hover: "#4a5d7c"
  well-control-disabled: "#1a2436"
  well-control-disabled-rule: "#26354c"
  well-control-disabled-ink: "#7f8ea3"
  well-selection: "#2f4a6e"
  well-fail-fill: "#3a1716"
  well-fail-rule: "#7a2b26"
  well-fail-ink: "#ffb4a8"
  night-wall: "#161f2e"
  night-paper: "#1d2738"
  night-paper-inset: "#232f42"
  night-rule: "#334258"
  night-rule-strong: "#71829a"
  night-ink: "#e7eef7"
  night-ink-secondary: "#b4c2d4"
  night-ink-tertiary: "#97a7bc"
  night-signage: "#0d1524"
  night-focus: "#8fb8ff"
  night-well: "#0b111a"
  java-line-bright: "#3ccf7e"
  engineer-line-bright: "#7fb2ff"
  aice-line-bright: "#ffa152"
typography:
  headline:
    fontFamily: "Pretendard, Segoe UI, Apple SD Gothic Neo, Malgun Gothic, sans-serif"
    fontSize: "23px"
    fontWeight: 750
    lineHeight: 1.35
    letterSpacing: "-0.01em"
  title:
    fontFamily: "Pretendard, Segoe UI, Apple SD Gothic Neo, Malgun Gothic, sans-serif"
    fontSize: "18px"
    fontWeight: 750
    lineHeight: 1.4
  station-title:
    fontFamily: "Pretendard, Segoe UI, Apple SD Gothic Neo, Malgun Gothic, sans-serif"
    fontSize: "15px"
    fontWeight: 700
    lineHeight: 1.45
  body:
    fontFamily: "Pretendard, Segoe UI, Apple SD Gothic Neo, Malgun Gothic, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.65
  brand:
    fontFamily: "Pretendard, Segoe UI, Apple SD Gothic Neo, Malgun Gothic, sans-serif"
    fontSize: "17px"
    fontWeight: 750
  station-number:
    fontFamily: "Pretendard, Segoe UI, Apple SD Gothic Neo, Malgun Gothic, sans-serif"
    fontSize: "16px"
    fontWeight: 800
  body-small:
    fontFamily: "Pretendard, Segoe UI, Apple SD Gothic Neo, Malgun Gothic, sans-serif"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.6
  chip:
    fontFamily: "Pretendard, Segoe UI, Apple SD Gothic Neo, Malgun Gothic, sans-serif"
    fontSize: "11px"
    fontWeight: 700
    lineHeight: 1.6
  label:
    fontFamily: "Pretendard, Segoe UI, Apple SD Gothic Neo, Malgun Gothic, sans-serif"
    fontSize: "12px"
    fontWeight: 600
    lineHeight: 1.4
  code:
    fontFamily: "JetBrains Mono, Pretendard, Consolas, monospace"
    fontSize: "12px"
    fontWeight: 400
    lineHeight: 1.5
rounded:
  hairline: "1px"
  stroke: "2px"
  chip: "3px"
  group-marker: "5px"
  control: "6px"
  caption: "8px"
  dialog: "10px"
  station: "50%"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
components:
  button-primary:
    backgroundColor: "{colors.java-line-ink}"
    textColor: "{colors.paper}"
    rounded: "{rounded.control}"
    padding: "6px 14px"
    height: "34px"
  button-secondary:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "6px 14px"
  button-on-signage:
    backgroundColor: "{colors.signage-navy}"
    textColor: "{colors.signage-muted}"
    rounded: "{rounded.control}"
    height: "32px"
  button-voice:
    backgroundColor: "{colors.voice-violet}"
    textColor: "{colors.paper}"
    rounded: "{rounded.control}"
  button-admin:
    backgroundColor: "{colors.admin-amber-soft}"
    textColor: "{colors.admin-amber-ink}"
    rounded: "{rounded.control}"
  segmented-selected:
    backgroundColor: "{colors.signage-navy}"
    textColor: "{colors.paper}"
    height: "34px"
  station-row:
    backgroundColor: "{colors.station-wall}"
    textColor: "{colors.ink}"
    height: "60px"
  station-row-next:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
  code-well:
    backgroundColor: "{colors.well}"
    textColor: "{colors.well-ink}"
    rounded: "{rounded.control}"
---

# Design System: MQ

## Overview

**Creative North Star: "The Line Map"**

A course is a metro line and each lesson a station on it. A learner reads the course the way a commuter reads a line map: where they are, where they last got off, which stops are optional, and the next stop, all at a glance. The world lends the product four things only: a station-wall light ground with deep navy signage bands, one saturated line colour per course, tabular station numbers in rings, and the route line itself. Navigation, controls and dialogs stay standard.

The tool comes first. The editor, terminal and results sit in dark wells set into the wall, because that is how learners already see code; the brief, the course and the settings are paper on the wall. Density is commuter density: a 34-lesson course fits in compact 60px station rows on one route, and the next station is the one filled action on the page.

State is carried by shape before colour: a hollow ring is not started, a half-filled ring is in progress, a filled ring is complete, a filled ring with an inner paper ring is cleared by the final challenge, a dashed ring is still loading, a smaller ring is optional. Admin tools are amber and the narrator is violet, so a teacher action is never mistaken for a learner action.

**Key Characteristics:**
- Light station-wall ground, navy signage band on every screen (50px catalog, 42px lesson).
- One line colour per course, carried by the band's underline, route line, rings and primary actions.
- Route line through compact station rows; next station panel above the list.
- Dark code wells for editor, terminal, answers and results.
- Shape-coded state; amber admin, violet narration.
- Two looks of one world, chosen in 앱 설정 (시스템, 밝게, 어둡게): the day station and the night station.

## Colors

Restrained paper and navy with one committed line colour per course and three state voices.

### Primary
- **Course line** (java-line / java-line-ink; engineer-line; aice-line / aice-line-ink): the course's line colour. The saturated value draws the route line, station rings and the band underline (≥3:1 on paper); the ink value fills primary buttons and labels text (≥4.5:1 with white). Set per course on the player root as `--line`, `--line-ink`, `--line-soft`.

### Secondary
- **Signage Navy** (signage-navy): the header band, selected segmented controls, the floating status line and toasts.
- **Voice Violet** (voice-violet): narration only, the 해설 재생 button, the narrator's caption border and the spoken-target ring.
- **Admin Amber** (admin-amber, admin-amber-ink, admin-amber-soft): 관리자 자동 풀이 only; while a run is active the band underline turns amber.
- **Challenge Purple** (challenge-purple-ink, challenge-purple-soft; night: night-challenge-ink, night-challenge-fill): a magenta-leaning purple, kept apart from the narrator's blue violet. It marks only a lesson cleared by its designated final challenge: the station ring (filled, with an inner paper ring), the 「도전 통과」 chip with a drawn diamond, and the 「수업 클리어」 headline. The practice gauge beside it keeps the line colour and the true count.

### Neutral
- **Station Wall** (station-wall): page ground behind everything.
- **Paper** (paper) and **Paper Inset** (paper-inset): problem brief, dialogs, menus, the next-station panel, sticky narration bar.
- **Ink** (ink, ink-secondary, ink-tertiary): text at 14:1, 6.2:1 and 4.6:1.
- **Rule** (rule, rule-strong): 1px dividers; rule-strong for control borders (≥3:1).
- **Well** (well, well-raised, well-rule, well-ink, well-muted): the dark code surfaces.

### Night station (dark theme)
The same roles, re-lit: night-wall ground, night-paper panels, a signage band darker than the ground, night-ink text (12.8:1 on paper), and each course line drawn in its bright tone (java-line-bright, engineer-line-bright, aice-line-bright, ≥6:1 on paper) for the route, rings and labels. Filled actions keep the darker line ink with white text. Wells are darker than the ground so the tool still reads as set into the wall. Admin amber and narrator violet keep their jobs.

### Named Rules
**The Same Station Rule.** Light and dark are one world: every role keeps its job, only the lighting changes; nothing is inverted with a filter.
**The One Line Rule.** A screen shows one course line colour, and only on the route, rings, the band underline and primary actions; never as decoration.
**The Voices Rule.** Violet speaks for the narrator and amber for the admin; neither colour is used for anything else. Challenge purple belongs to one state (cleared by the final challenge) and always comes with its words and diamond.

## Typography

**Body Font:** Pretendard (with Segoe UI, Apple SD Gothic Neo, Malgun Gothic)
**Code Font:** JetBrains Mono (Korean in code falls back to Pretendard)

**Character:** One workhorse sans for every UI role, ranked by weight (400 to 800) rather than by face; mono appears only for code, file names and revision ids.

### Hierarchy
- **Headline** (750, 23px, 1.35): the course name.
- **Title** (750, 18px, 1.4): the next-station lesson title, problem title.
- **Station title** (700, 15px, 1.45): a lesson in the route list.
- **Body** (400, 14px, 1.65): course description, problem brief; prose capped at 72ch.
- **Label** (600, 12–13px): segmented controls, meta chips, progress counts; tabular numerals for every count.
- **Code** (400, 11–12px mono): revision ids, file names in the well heading.

### Named Rules
**The Numbers Rule.** Station numbers and progress counts use tabular figures so a column of rows reads as a timetable.

## Layout

Catalog: navy band (50px), then a 260px course legend column beside the course column (max 1200px). The course column stacks the course head (name, description, facts on one line), the folded course-name line, the next-station panel, one toolbar row (lesson/challenge view, 전체 순서/분류별, track filter when two tracks exist), then the route. Station rows use a four-column grid: ring (44px), title and meta, progress (150–200px), actions. Below 900px progress drops under the title; below 640px the legend stacks above.

Lesson: navy band (42px, never a second row at ≥700px), the step strip, then the split workspace: paper brief on the left, dark well on the right, both resizable. Spacing steps are 4, 8, 16 and 24px.

## Elevation & Depth

Flat by default: depth comes from paper on the wall and wells set into it, separated by 1px rules. Shadows appear only on things that float above the page.

### Shadow Vocabulary
- **Menu** (`box-shadow: 0 12px 32px #15223329, 0 2px 6px #1522331a`): settings menus dropping from the band.
- **Dialog** (`box-shadow: 0 24px 64px #15223340`): lesson information, passed dialog, shortcut sheet.

### Named Rules
**The Flat Wall Rule.** Nothing resting on the page casts a shadow; only menus, dialogs and the narrator's caption float.

## Shapes

Controls and panels share one gentle corner (6px); chips are nearly square (3px); dialogs 10px. Stations are circles. One rule weight (1px) everywhere; the route line and the band underline are the only thick strokes (4px and 3px), and both are the line colour.

## Components

### Buttons
- **Shape:** gentle corner (6px), 1px border.
- **Primary:** line-ink fill, white text; the only filled primary in the catalog is the next station's action, other rows show it as an outline in line-ink.
- **Hover / Focus:** hover raises contrast with an inner hairline; focus is a 2px focus-blue outline offset 2px (light blue on navy).
- **Secondary:** paper with rule-strong border.
- **Voice:** violet fill (해설 재생). **Admin:** amber-soft with amber-ink border and a drawn play icon (관리자 자동 풀이).

### Chips
- **Style:** 1px border, 3px corner, 11px bold label: 기본 (solid), 필수 (ink border), 고급 (dashed), 선택 (dotted), 다음 (line-ink fill).

### Cards / Containers
- **Next station panel:** paper, 1px rule, a 44px ring with a 4px line-colour stroke.
- **Problem brief:** paper with a sticky narration bar at its foot.

### Inputs / Fields
- **Style:** paper, rule-strong border, 6px corner; in the well, near-black fill with well-rule border.
- **Focus:** 2px focus-blue outline.

### Navigation
- **Signage band:** navy, white title, muted controls with navy-raised hover; underline in the course line colour (amber during an admin run).
- **Segmented controls:** joined buttons in one bordered group; the selected segment is navy.
- **Course legend:** each course a ring and name; the selected course is paper with its ring in its line colour.

### Theme control
- **Place:** first block of 앱 설정, so it is reachable from the course list and from every lesson.
- **Form:** three joined native radios (시스템, 밝게, 어둡게) in a labelled group; the selected one is navy; arrow keys move the choice; a sentence under it states the look in effect and, for 시스템, that it follows the OS.

### Route and step strip (signature)
- **Route:** a 4px line-colour line through 30px rings; next station 36px with a wall-coloured halo; optional stations 24px.
- **Step strip:** dot, label, connector; passed steps are filled dots on line-colour connectors, the current step is a 16px ring; one ink marker slides under the current step (160ms, none under reduced motion).

## Do's and Don'ts

### Do:
- **Do** derive every station state from recorded progress only, and show unknown (dashed ring, 진도를 확인하고 있어요) instead of a guess.
- **Do** keep the editor, terminal, answers and results inside the dark well.
- **Do** keep the lesson band at 42px and the catalog band at 50px on windows 700px and wider.
- **Do** give every icon-only control its full Korean name as its accessible name.

- **Do** define every colour as a role token with a value for each look; a literal colour that only works on one ground is a bug.

### Don't:
- **Don't** use the line colour, violet or amber for decoration.
- **Don't** add side stripes thicker than 1px to callouts, rows or alerts; asides are paper-inset panels with a 1px rule.
- **Don't** draw a second filled primary action in the station list.
- **Don't** add entrance animation; motion is limited to 160ms colour and dot-scale changes, removed under reduced motion.
