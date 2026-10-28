# 해설 전수 점검 (첫 자바 수업 제외) — 계획과 진행

요청: 2026-10-28 사용자 「첫 자바 수업 빼고 다」. 원문 지시: C:/Users/jangk/Documents/Codex/2026-10-24/d/claude-narration-review-except-first-java-20261028.md

## 범위

- catalog = 공개 코스 핀 = 로컬 코스 번들: 자바 백엔드 40, AICE 24, 정보처리기사 30 = 94수업 (2026-10-28 확인, 누락·추가 없음).
- 제외: java-values(「자바 · 값이 계산되고 표시되는 과정」, 공개 핀 java-values-7). 원본·캐시·수업 파일·pilot n·검토 대장 항목을 수정하지 않는다.
- 대상: 93수업, 916문제, 상세 발화 5,429개 + 수업 소개(narration-openings.json) + 문제 도입 문장(narration_openings.py 생성).
- 수업별 목록: target/narration-audit/scope.json (과정, 키, 폴더, 제목, 문제 수, 발화 수, 개정, 해시 일치).

## 작업 전 경계

- HEAD 4576b6f (branch codex/sql-table-browser). 기존 미커밋 변경 13파일 + 미추적 3파일은 모두 java-values 관련 사용자 작업 → 보존.
- 기록: target/narration-audit/boundary-status.txt, boundary.diff, boundary-sha.txt.
- 기존 상태 검사: build-redesigned-git.py --check 전 수업 통과, narration_review status uncovered 0, course bundle --check 통과.

## 우선 처리: Vim wq 발음 (2026-10-28 사용자 제보)

- 원인(텍스트 변환으로 확인): `:wq` → 「콜론 wq」. wq·w·q가 영문 그대로 음성 엔진에 전달됐다. :w/:q/:q!도 같은 구조.
- 수정: assets/speech/pronunciation.js LEXICON에 vim-commands(scope vim-ex) 추가, 단어 첫머리 콜론 뒤 w/q/wq(+!)만 낱자 이름.
  결과: 콜론 더블유큐, 콜론 더블유, 콜론 큐, 콜론 큐 느낌표, 콜론 더블유큐 느낌표. 화면·자막·명령 원문은 그대로.
- 검증: 공개 수업 음성 문장 19,936줄 전후 비교 → 변경 23줄, 모두 vim-basics의 :w/:q/:q!/:wq 문장.
  symbols-lexicon/speech 테스트 36개 통과. pronunciation-review.test.mjs의 기존 실패 2개는 수정 전과 출력이 동일(사전 인벤토리 미갱신·멱등 예외, 이번 변경과 무관).
- 실제 합성 음성 청취: 하지 않음.
- 사용자 반영: 모듈이 src/main.rs에서 include_str!로 앱에 내장 → 앱 개정 필요(커밋→immersion-quest-3 main 푸시→release.yml 빌드→자동 업데이트). 최신 릴리즈 v0.1.0-build.148. 수업 게시로는 반영되지 않는다. 푸시·배포는 이번 권한 밖.

## 진행 방식

1. 수업별 packet 생성(target/narration-audit/packets/<key>.txt): 목표·본문·코드·시연 상태·해설(도입 포함)·run 실제 출력(tests/lesson-cases).
2. 전수 읽기 → 수업별 판정을 progress.json에 기록(유지/수정/미해결, 근거).
3. 수정은 narration_review.py record로 원문 문장만 교체 → 빌더로 캐시·수업 파일 재생성 → 개정 번호 증가.
4. 해설 외 필드 불변 증명, 실제 실행 검사, 공개본 충돌 확인 후 수정 수업만 게시.

## 진행 상태

progress.json 참조. 이어갈 위치는 그 파일의 next 필드.

## 마무리 (2026-10-28)

- 남은 실행 검증 5수업을 현재 해시로 개별 재실행해 모두 통과(java-class-objects, h2-memory-file, java-jdbc, sql-transactions, sql-isolation-locks).
  이전 FAIL은 출력 없는 연속 실패(일괄 실행 세션 종료)였고 수업 내용 문제가 아니었다.
- 상태 검사: build-redesigned-git.py --check, build-redesigned-course-bundle.py --check 통과, narration_review status uncovered 0 · open 0.
- 자바 백엔드 31수업 게시(tools/publish-narration-audit.py, target/narration-audit/publish-java.out). 원격 메타데이터(lesson_previews·change_history·scope_note)와
  다른 행 필드는 그대로 두고 31개 핀만 바꿨다. 읽기 확인: java-backend 40/40, aice-associate 24/24, engineer-practical 30/30 핀 = 로컬.
- 커밋은 java-values 사용자 작업(경계 13파일 중 해당 부분과 미추적 3파일)을 뺀 감사 범위만 담는다. 공유 파일의 java-values 줄은 HEAD 값으로 두고
  course-prd content_sha256은 생성기 방식으로 다시 계산했다.
