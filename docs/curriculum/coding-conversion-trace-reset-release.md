# 코딩 문제 전환 · 코드 흐름 보기 · 전체 진도 초기화 — 2026-10-29 배포분

사용자 요청(Codex 경유): 「정처기 에서도 코딩문제에서는 객관식 다 지우자 에이쓰에서도」 → 「지우는게 아니라 바꾸자
객관식에서 순수 코딩 문제로」, 비주얼라이저(java-memory-visualizer)의 핵심을 수업에서 활용, 「모든 내 기록 초기화 기능,
수업별 초기화 기능 어딨어?」, 그리고 「배포」 「그 비주얼라이저 활용해서 해설하는 스텝이 어디야?」.

이 문서는 이번 배포에 들어간 것과 **아직 남은 것**을 구별해 적는다. 전체 전환 완료가 아니다.

## 1. 코딩 문제 전환 (기준: 공개 main `c593fb76`)

| 과정 | 원래 선택 문제 | 남은 선택 문제 | 코딩으로 바꾼 문제 | 바뀐 수업 |
|---|---:|---:|---:|---:|
| 정보처리기사 실기 (`engineer-practical`) | 240 | 128 | 112 | 17 |
| AICE Associate (`aice-associate`) | 170 | 94 | 76 | 12 |
| 합계 | 410 | 222 | **188** | 29 |

- 정보처리기사: C 7수업(start 1, conditions 7, arrays 8, functions 9, pointers 9, double-pointers 7, structures 7),
  Java 4수업(flow·references·static·polymorphism 각 7), Python 2수업(values 2, calls 2), SQL·DB 4수업
  (db-model 8, sql-select 9, sql-group 9, sql-change 6).
- AICE: python-start 5, python-conditions 4, python-api 5, table-csv 7, selection 7, quality 4, join 7, plots 9,
  features 7, scale 8, regression 6, regression-metrics 7.
- 바꾼 문제는 새 스텝 ID(`tools/coding_conversion.py::new_step_id`)와 올린 수업 버전으로 열린다. 이전 선택 문제의 완료
  기록은 이전 스텝·버전에 남고 새 코딩 능력으로 세지 않는다.
- 각 수업은 현재 바이트 그대로 헤드리스 검증을 통과했다(`target/mcq/<key>.json`, `lesson_sha256` 일치): 시작 코드는
  실패, 해답은 통과, 해설 실행 결과는 고정값과 같음, 기록한 오답·하드코딩 답은 거절, 다른 올바른 답은 통과.
  AICE의 ML 문제는 학습 점수 같은 흔들리는 값이 아니라 선택한 열·모양·설정·누수 여부를 바꾼 준비 자료로 채점한다.
- 그림을 그리는 스텝의 준비 자료 검사는 `MPLBACKEND=Agg`로 실행한다. 앱은 학습자 실행에만 이 값을 주고 검사기의 자식
  실행에는 주지 않아 `plt.show()`가 창을 기다릴 수 있었다. 그림이 없는 수업의 검사기 바이트는 그대로다.

### 남은 선택 문제 (이번 배포에 없음)

- 정보처리기사 128: db-storage 16, requirements 8, design 25, server 9, interfaces 10, ui 8, test-cases 6,
  test-integration 6, security 14, os 8, network 7, build 6, mixed 3, sql-change 2. 대부분 설계·테스트·보안·운영
  개념 문제다. 개념/코딩 분류를 수업마다 마치기 전에는 "128개의 미완료 코딩 문제"라고 부르지 않는다.
- AICE 94: 바꾼 수업에 남긴 개념 문제 4(selection 1, quality 2, regression 1)와 아직 바꾸지 않은 12수업
  (split 9, leakage 7, classification 7, classification-metrics 9, models 7, boosting 7, tuning 7, tensorflow 7,
  neural-regression 7, neural-classification 7, training 7, integration 9). split·leakage는 전환 초안이 아직 검증을
  통과하지 못했고(split: 시작 코드가 이미 통과하는 스텝, leakage: 오답이 통과), models·classification·
  classification-metrics·tuning·boosting은 명세 초안만 있다. 초안은 `wip/aice-conversion-drafts-20261029`
  브랜치에 보존했고 공개 수업에는 넣지 않았다.

## 2. 코드 흐름 보기 (Java 메모리 시각화 핵심 재사용)

핵심은 java-memory-visualizer의 ASM `Instrumenter`·`Tracer`·`TraceView`를 바꾸지 않고 쓴다
(`assets/java-trace/PROVENANCE.md`, 해시 고정 테스트). 학습자 편집기의 `Main.java`를 수업과 같은 JDK 25 `javac --release 25`로
컴파일해 실행한 실제 기록이다. 새 컴파일러나 손으로 만든 상태는 없다. 채점·진도와 무관하다.

**여는 방법**: 아래 스텝의 코드 편집기 아래 `코드 실행` 옆 **`코드 흐름 보기`** 버튼. 이전/다음·처음/마지막·슬라이더·←→로
단계를 옮기며, 다음에 실행할 줄·호출 스택·지역 변수·static 변수·객체와 참조 화살표·출력을 본다. 닫으면 같은 화면으로 돌아온다.

과정: 정보처리기사 실기 → 분류 「프로그래밍 언어 · Java·Python」.

| 수업 | 스텝 | 해설의 사용 |
|---|---|---|
| Java · 같은 객체와 다른 이름을 구별해요 | 1. b를 a와 따로 쓰는 배열로 만드세요 | **해설이 직접 연다**: b = a 다음 단계에서 a·b가 배열 하나를 가리킴 → clone() 뒤 같은 단계에서 배열 둘 |
| | 2. 안쪽 배열까지 복사해 원본을 지키세요 | 버튼 안내 |
| | 3. change가 받은 재고 객체의 count를 바꾸게 하세요 | **해설이 직접 연다**: change 호출 단계에서 value와 a가 같은 Stock → main으로 돌아오면 새 Stock은 사라지고 count 2 → 고친 뒤 count 7 |
| | 4. replace가 돌려준 새 객체를 a에 다시 담으세요 | 버튼 안내 |
| Java · 공유 번호와 생성 순서를 읽어요 | 1, 2, 4, 5, 6, 7 | 버튼 안내 |
| | 3. b를 새 표로 만들어 생성자가 두 번 실행되게 하세요 | **해설이 직접 연다**: 첫 `Ticket()`(인수 없는 생성자) 호출 단계에서 static total 0 → 두 번째 생성자가 끝나는 단계에서 total 2, 객체 둘 |
| Java · 호출 규칙과 예외 뒤 순서를 읽어요 | 1, 2, 3 | 버튼 안내 |
| | 5. 다 만들어진 rule의 show()를 한 번 더 불러 생성 중 값과 비교하세요 | **해설이 직접 연다**: Rule() 생성자 안의 show()가 Bonus.show()로 들어간 단계(value 0) → 필드 초기화 value = 7 → main의 rule.show() 직전(value 7) |
| Java · 재고 계산의 실행 순서를 읽어요 | 7. add가 반환한 값을 stock에 담으세요 | 버튼 안내 |

- 버튼이 있는 스텝 16개, 그중 해설이 직접 여는 스텝 4개. 나머지 12개의 해설은 "코드 흐름 보기를 눌러 …"라고 안내만
  한다(자동 시연이 아니다).
- 해설이 열 때(`code_flow` 동작, `assets/layout/agent.js`): 선생님이 편집기에 고친 코드를 앱이 실제로 추적하고, 지정한 줄의
  n번째 기록 단계로 옮긴 뒤 그 단계를 설명한다. 모달 배경 없이 열려 자막·강조·멈춤을 쓸 수 있고, 다음 편집·실행 전에 닫히며,
  해설이 끝나거나 멈추면 닫히고 학생 코드가 돌아온다. 해설 중 직접 닫으면 해설도 멈춘다.
- 검증: 수업 검증기가 해설의 각 `code_flow`를 실제 추적 기록에 재생해 그 단계가 없으면 실패한다(증거에 스택·지역 변수·객체
  수 기록). 빌드는 그때의 코드에 그 줄이 있는지 검사한다. 브라우저 테스트(`tests/js/code-flow-narration.test.cjs`)와
  네이티브 플레이어 시험(`tools/player-pilot-code-lesson.js`)이 열린 줄·비모달·같은 프로그램·닫힘·학생 코드 복원을 확인한다.
- 한계: JDK 25와 ASM 9.9(처음 사용할 때 Maven Central에서 해시 고정으로 받음)가 필요하다. 1000단계·20초에서 기록을 멈춘다.
  compact source의 인스턴스 `main`이면 실행기가 만드는 `new Main()`은 기록하지 않는다. C·Python 코드 흐름은 근거 있는 기존
  엔진이 없어 제공하지 않는다.

## 3. 학습 진도 초기화

- **수업 하나**: 수업 화면 머리글의 진도 `% · n ⓘ` → `학습 정보` → `이 수업 진도 초기화` → 확인. (그대로)
- **내 전체 학습 진도**: 과정 목록 머리글의 계정 `gh · @아이디` 옆 **`진도 초기화`** → `내 전체 학습 진도 초기화` 대화상자.
  GitHub 진도 기록을 먼저 읽고, 기록이 있는 과정·수업 수를 보여 준 뒤 `전체 진도 초기화`로 확인한다. 로그인한 모든 학습자가
  쓸 수 있다(관리자 전용 아님). 원래 기록은 지우지 않고 초기화 기록을 더한다(기기 저장소와 GitHub 진도 이슈에 그대로 남음).
  작성한 코드 초안·실습 폴더·앱 설정·다른 계정의 진도는 그대로다. 재시작·동기화 뒤에도 초기화 전 완료가 다시 살아나지 않는다
  (`tests/progress_reset.rs`, 격리된 저장소와 계정으로만 시험).
- 수업 머리글의 `초기화`는 코드와 실습 환경만 되돌리며 진도 초기화가 아니다.

## 4. 배포 순서

1. 앱: 이 브랜치를 main에 fast-forward로 올려 `MQ3 desktop release` 워크플로가 Windows·macOS 설치 파일을 만든다.
   `code_flow` 스텝·동작은 이 앱부터 동작한다.
2. 과정: 공개 릴리스에 두 설치 파일과 런타임 커밋이 있는지 확인한 뒤
   `python tools/publish-coding-trace-reset.py --runtime-release <tag> --runtime-commit <sha> --publish`.
   29수업은 새 버전 태그(불변)를 만들고, 두 과정의 `course.json`은 blob SHA 비교 교체(CAS)로 해당 행의 `revision`·`sha256`만
   바꾸고 변경 기록 한 줄을 더한다. 다른 수업·순서·선수 관계·미리보기·도전 지정은 원격 그대로다. 쓴 바이트는 모두 다시 읽어 확인한다.
3. 백엔드 과정(GitLab MR 9스텝·CI 10스텝·git-remote-13)과 학습자 GitHub 실험 보류 상태는 건드리지 않는다.

## 5. 이번 작업에서 확인한 시험

- 헤드리스 수업 검증: 29수업 전부 현재 바이트로 통과(Java 3수업은 `code_flow` 재생 포함 재검증, AICE 6수업은 그림 검사기 범위 수정 뒤 재검증).
- `cargo test --lib java_trace -- --ignored`: 모든 `code_flow` 스텝의 시작·해답 코드를 채점과 같은 JDK 25로 추적, 참조·인수 없는
  생성자·static·동적 바인딩 확인.
- 필수 릴리스 묶음 중 내용 관련: `progress_reset`, `bundled_courses`, `challenges`, `step_reset`, `lesson_reset_challenge`,
  `cross_course_improvements`, `content_updates`, `repository_lessons`, `redesigned_git_*`, `progress_sync`.
- 바뀐 수업의 예전 수업 시험 8개는 읽기 스텝 시절 출력을 고정하고 있어 이미 실패하던 것을, 검증된 수업 사례 재생으로 바꿨다.
- 브라우저: `code-flow-narration`(새), 해설·편집·자막·속도·개요 시험. 설치되지 않은 Playwright Chromium 대신 설치된 Edge로
  실행한 것이 있다.
- 이번 변경과 무관하게 기준 커밋에서도 실패하는 `tools/test_redesigned_highlights.py`의 bash-basics 문장 하나는 그대로다(워크플로 밖).

## Publication result (2026-10-29 UTC)

- Runtime: run 155 (a79d9697) failed on macOS `player_loading_native`: the loading self-test still measured the
  plots lesson's answer-choice panel, which the conversion removed. Fixed in 846504af (checks task/editor/result panes
  and that no choices remain). Run 156 https://github.com/jhs512/immersion-quest-3/actions/runs/40897443218 passed
  windows, macOS arm64, principles/actual-engines and release.
- Public Latest `v0.1.0-build.156` → 846504afb5d1f52e1231bf5d3df89cb366cd4f3d (contains a79d9697 and d66c2e6f).
  `molip-quest-3-windows-x64-setup.exe` 156a4a710cfe827126001a86e26f6ac3e92b1f599ae5faeb8dfa969173d99d42,
  `molip-quest-3-macos-arm64.dmg` 0f008668ac77f329095fa052f460a3dbfb619b545b67d10eaa95b859bed45965; both match SHA256SUMS.
- Publisher baseline: `BASELINE` was `origin/main`, which after a79d9697 already names the new revisions; it is now pinned
  to c593fb76 (public build 154, where this work started). Run with
  `--runtime-release v0.1.0-build.156 --runtime-commit a79d9697…`.
- Courses: engineer-practical main 10fd4f817a398737541ee5b64a52b090dfd33fcf (course.json sha256 744e8ce2…),
  aice-associate main 462a953c46ea7350018930facc734b77dd35f8a4 (edb51d30…). Independent readback
  (`target/readback156/check.py`, GitHub API only): order, top-level fields and every non-target row equal the parent
  commit; only revision/sha256 changed on 17 + 12 rows; each tagged lesson.json hashes to its pin; old choice ids gone,
  new ids are coding steps: 112 + 76 = 188. code_flow buttons 16; narrated code_flow 4
  (references#1, references#3, static#3, polymorphism#5). java-backend course untouched (main c10097db, 09:33Z).
- Native `aice_plots_restore_student_state` (not in release CI) now passes locally (544 s) after counting 11 coding
  steps and allowing long narrations up to 180 s per wait (step 11 has 14 actions with 6 typed patches).
