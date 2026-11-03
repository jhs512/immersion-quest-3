# 밝게 테마 객관식 선택 대비

Status: done (branch `codex/light-choice-contrast-20261103`, base main 215b109c)

## 원인

학생 플레이어 객관식(`interaction_ui.rs` → `.answer-option`)의 선택 상태가 `repository-player.css`에 어두운 테마 값 `#17473f` 배경, `#58cdb4` 테두리·라디오로 고정돼 있었다. 글자는 우물 토큰을 따라 밝게에서 `#152233`이 되어, 짙은 초록 위의 짙은 남색 글자가 됐다.

## 수정

`station.css`의 테마별 우물 토큰에 `--answer-chosen-bg`, `--answer-chosen-rule`을 더했다. 밝게는 `#e4f3ea`/`#11753f`(기존 `--feedback-good-bg`, `--ok` 값)를 쓰고, 어둡게와 시스템-어둡게는 기존 값 `#17473f`/`#58cdb4`를 그대로 둔다. `repository-player.css`의 선택 배경·테두리·라디오 강조색이 이 토큰을 읽는다. 채점, 문제 ID, 콘텐츠, 진도는 바꾸지 않았다.

## 실제 화면 측정 (MOLIP_PILOT, 버전 정, 「DB · 종속·저장·조회 로직의 역할을 읽어요」 문제 1)

`node tools/design-capture.cjs tools/design-scenarios/choice-contrast.cjs <out>`

| 상태 | before 글자 대비 | after 글자 대비 | 테두리 대 우물 before → after |
|---|---|---|---|
| 밝게 선택 전 | 16.05 | 16.05 | 7.67 → 7.67 |
| 밝게 선택 | 1.54 | 13.99 | 1.94 → 5.77 |
| 밝게 오답 제출 뒤 | 1.54 | 13.99 | 1.94 → 5.77 |
| 밝게 키보드로 선택 이동 | 1.54 | 13.99 | 1.94 → 5.77 |
| 밝게 잠김(fieldset disabled) | 1.54 | 13.99 | 1.94 → 5.77 |
| 어둡게 선택 전 | 15.75 | 15.75 | 그대로 |
| 어둡게 선택 | 8.69 | 8.69 | 9.74 → 9.74 |

선택지 자체에는 정답/오답 표시가 없다. 채점 결과는 결과 칸에 나온다. hover 규칙도 없다. 잠김 상태는 해설·채점 중 상태를 DOM에서 fieldset을 잠가 흉내 냈다.

스크린샷: `before/`, `after/` (`*-choices.png`는 선택지 부분, `capture.json`은 측정값). 이 폴더는 git에서 무시된다.

## 확인하지 못한 것

- 레거시 `.quiz-option`(디버그 전용 `MOLIP_LEGACY` Workspace)은 학생 플레이어 경로가 아니라 바꾸지 않았다.
- 시스템(OS 어둡게) 경로는 같은 토큰 블록을 복사해 두었지만 화면으로 따로 찍지 않았다.
- `tests/js/answer-choice-layout.test.cjs`, `lesson-loading-layout.test.cjs`는 수정 전 HEAD CSS에서도 픽스처 수업을 찾지 못해 실패한다(이번 변경과 무관).
