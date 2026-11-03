# 모든 코스 레벨링·비주얼라이저 해설 감사 계획

요구 원문과 완료 조건은 `spec.md`. 결정 기록은 `decisions.tsv`(한 줄에 결정 하나, 근거 경로 포함).

## 1. 완료 판정

| 완료 조건(spec) | 판정 근거 | 상태 |
| --- | --- | --- |
| 1. manifest·수업·스텝 전수 대조 | `inventory.md`, `inventory.json` (`python tools/course_audit/inventory.py`, `--check`는 대조 실패 시 종료 코드 1) | 완료. 대조 문제 0건 |
| 2. 상위 원칙과 근거 | 루트 `AGENTS.md` 「모든 코스의 레벨링 원칙」, 각 원칙에 정책 위치 | 완료 |
| 3. 수업별 목표·선수·흐름·정답·해설 판단 | `audit/*.md` 4개 (수업별 절, 스텝 표, 결함, 계획 항목) | 98개 참조 전부 판정. 검토 깊이는 §5의 표 |
| 4. 비주얼라이저 적용/비적용/불가/보류와 근거 | §3 규칙, §4 실험, `audit/*.md`의 스텝별 판정, §6 적용 목록 | 판정 완료. 적용은 선별 15스텝, 남은 후보는 §7 |
| 5. 데이터 크기별 시간·추적 크기·메모리·UI | §4, `trace-scale.json` (`python tools/course_audit/trace_scale.py`) | Python 작업 5종 측정. TensorFlow·XGBoost는 §4 한계 |
| 6. 국소 개선 적용·검증, 구조 재설계는 계획 | §6 적용과 검증 기록, §7 계획 | 완료(§6 검증 기록) |
| 7. Rust 수업은 PRD·대표 문제 승인 뒤 | §8 | 사용자 승인 뒤 별도 작업에서 제작 중. 이 checkout은 다루지 않음 |

## 2. 범위

- 코스: 앱이 기본 제공하는 세 코스(`src/bundled_courses.rs`). 자바 백엔드 44수업, 정보처리기사 실기 30수업, AICE Associate 24수업. 참조 98개, 고유 수업 파일 107개, 스텝 1073개.
- 어느 코스에도 없는 수업 9개는 판정 대상에서 뺐다. 8개(`node-cpu-offload`, `socket-partial-frames`, `sys-*` 6개)는 `catalog.json`의 `withdrawn_lessons`라 `build.rs`가 앱에 등록하지 않고, `java-parser`는 카탈로그에 없다.
- 범위 밖: 기존 KPC 금융·`java-basics`·아침 연습 코스, Codex가 맡은 토요 특강, 런타임(`src/c_trace.rs`, `src/repository_course.rs`의 언어 enum, `src/player_ui.rs`, 설치기, release workflow), Rust 정식 수업.

## 3. 코드 흐름 보기: 실제 지원과 해설 사용 규칙

### 런타임 사실(이 checkout, 시작 커밋 0090f482)

| 언어 | 버튼 | 실제 추적 Windows | 실제 추적 macOS arm64 | 해설 `code_flow` | 근거 |
| --- | --- | --- | --- | --- | --- |
| Java | 기본 표시 | JDK 25 + ASM 추적 | 같음 | 기존 허용 | `src/java_trace.rs`, `Task::code_flow_availability` |
| Python | 기본 표시 | 수업 Python의 `sys.settrace` | 같음 | 이번에 허용 | `src/python_trace.rs`, `assets/python-trace/mq_pytrace.py` |
| C | 기본 표시 | TinyCC + dbgeng 원본 프로그램 정지 | 실험적 LLDB 백엔드(전체 79문제 검사는 Codex 진행 중) | 이번에 허용. macOS 재생은 §9 | `src/c_trace.rs` |
| C (Linux) | 사유와 함께 비활성 | 없음 | | 배포 대상 아님(release는 Windows·macOS arm64) | `.github/workflows/release.yml` |
| JavaScript·web·SQL·Docker·프로젝트·JUnit·라이브러리 | 사유와 함께 비활성 | 없음 | 없음 | 쓰지 않음 | `src/repository_course.rs` |
| C++·Rust·JS 새 추적 | 이 checkout에 없음 | | | 지원으로 세지 않음 | Codex 별도 checkout |
| Git 터미널 스텝, 예제 코드 없는 선택·빈칸 | 숨김 | | | 쓰지 않음 | `code_flow_availability` |

시작할 때 명시적 `code_flow: false`는 0개였다. 이번에 파일을 읽는 Java 스텝 10개에 넣었다(§6, §9의 1).

해설이 여는 방식: `assets/layout/agent.js`의 `code_flow` 동작은 언어와 무관하게 `.code-flow-open` 버튼을 눌러 추적하고 `{line, event, nth}` 단계로 옮긴다. 이번에 바꾼 것은 제작 검사뿐이다.

- `tools/build-redesigned-git.py`: Java·Python·C, 터미널 아님, 예제 없는 문항 아님일 때만 해설 `code_flow`를 받는다. `tools/test_redesigned_highlights.py`가 이 계약을 검사한다.
- `examples/validate_redesigned_lesson.rs`: 앱과 같은 `code_flow_availability()`와 같은 추적기(`java_trace`, 과제 files를 넘기는 `python_trace`, `c_trace`)로 해설의 단계를 실제 기록에서 찾는다. 없으면 실패한다.

### 해설에서 쓰는 규칙

적용(APPLY)은 출력이 보여 주지 못하는 상태가 이해의 핵심일 때만이다.

- 같은 대상을 가리키는 두 이름(참조·포인터 별칭), 호출 중인 함수의 스택과 인자 복사, 반복 중 바뀌는 변수, 재귀, static과 인스턴스, 생성 순서.
- 출력 한 줄로 이미 보이는 값, 표·그래프가 결과인 단계, 문법 오류 단계에는 쓰지 않는다(NOT-APPLY).
- 추적이 없는 언어·스텝은 불가(IMPOSSIBLE). 추적은 되지만 화면이 실제 상태를 보여 주지 못하면 보류(HOLD). pandas·numpy·scikit-learn 객체는 이름만 보인다(§4).

## 4. 데이터 크기 실험

가설: 「빅데이터는 시각화가 힘들 것이다」. 결과: 비용 가설은 반만 맞다. 진짜 문제는 비용이 아니라 화면이 보여 주는 정보다.

방법: `tools/course_audit/trace_scale.py`. 앱의 수업 Python(3.13.13, pandas 3.0.6, numpy 2.5.3, scikit-learn 1.9.1, `%LOCALAPPDATA%\MolipQuest\MolipQuest\data\ml-env`, 실행만 하고 바꾸지 않음)으로 채점 실행기를 그대로 한 번, 앱 추적기를 그대로(1000단계) 한 번 실행했다. 최대 메모리는 `GetProcessMemoryInfo`의 최대 작업 집합이다. 화면은 앱의 `TraceView`(`assets/java-trace/core/render.js`)로 가장 무거운 한 단계를 헤드리스 Chrome에서 그렸다. 앱은 WebView2라 같은 Chromium 계열이지만 같은 프로그램은 아니다. 각 칸 1회 측정이다. 패키지 import가 시간의 대부분이고, 첫 실행은 1초가량 더 느렸다(pandas 10행 2.05초, 1000행 0.95초). 그 정도 차이는 잡음으로 본다. 원자료: `trace-scale.json`.

| 작업 | 행 | 그냥 실행 | 추적 실행 | 추적 기록 | 화면이 보여 주는 데이터 | 버린 줄 실행 | 한 단계 그리기 |
| --- | ---: | --- | --- | ---: | --- | ---: | --- |
| Python 목록 + 짧은 반복 | 10 | 0.10초 · 15MB | 0.11초 · 17MB | 6KB | 원소 10개 전부 | 0 | 55ms · 노드 110 |
| | 1,000 | 0.10초 · 15MB | 0.12초 · 17MB | 74KB | 1,000개 전부 | 0 | 72ms · 3,080 |
| | 100,000 | 0.09초 · 19MB | 0.56초 · 34MB | 9.7MB | 100,000개 전부 | 0 | 3.1초 · 300,080 |
| | 1,000,000 | 0.12초 · 55MB | 4.5초 · 176MB | 110MB | 1,000,000개 전부 | 0 | 240초 안에 끝나지 않음 |
| pandas read_csv + groupby | 10~1,000,000 | 0.95~1.25초 · 71~128MB | 1.0~1.25초 · 72~129MB | 3KB 고정 | DataFrame·Series 이름만 | 0 | 46~66ms · 97 |
| pandas iterrows 반복 | 10 | 1.04초 | 1.37초 | 14KB | 이름만 | 0 | 46ms |
| | 1,000 | 0.98초 | 1.05초 · 단계 한도 | 469KB | 이름만 | 1,495 / 2,495 | 50ms |
| | 1,000,000 | 12.95초 · 230MB | 1.38초 · 단계 한도 | 469KB | 이름만 | 2,489,005 / 2,490,005 | 43ms |
| numpy 벡터 연산 | 10~1,000,000 | 0.29~0.33초 · 29~45MB | 0.27~0.34초 · 30~46MB | 2KB 고정 | ndarray 이름만 | 0 | 40~47ms · 90 |
| scikit-learn 분할 + 학습 | 10~1,000,000 | 2.6~4.7초 · 148~268MB | 3.0~4.2초 · 150~270MB | 21KB 고정 | 모델·표는 이름만(분할 결과 목록 3개는 원소) | 0 | 44~55ms · 538 |

판정:

- **벡터화된 pandas·numpy·scikit-learn은 크기와 무관하게 싸다.** 추적은 학습자 `main.py`의 줄만 기록하고 라이브러리 내부는 기록하지 않는다. 100만 행에서도 추가 시간은 0.5초 안팎이고 기록은 수 KB다. 그러나 화면에는 `DataFrame` 같은 이름만 나온다(`mq_pytrace.py`의 `obj()`가 `OPAQUE`로 적는다). 행·열·모양·값은 하나도 보이지 않는다. 그래서 데이터 수업에서 코드 흐름의 이점이 없는 이유는 크기가 아니라 **보여 줄 상태가 없어서**다(NOT-APPLY 또는 HOLD-OPAQUE).
- **행마다 도는 Python 반복은 앞부분만 남는다.** 1000단계 한도에서 약 400행 뒤 멈춘다(`step_limit`). 100만 행이면 줄 실행의 99.96%를 버린다. 남은 것은 앞쪽 행이지 표본이 아니다. 이것을 전체 상태라고 설명하면 안 된다.
- **큰 Python 목록은 화면이 먼저 무너진다.** 단계마다 목록 전체를 다시 적어서 100만 원소에 기록 110MB, 추적 4.5초다. 앱의 20초 제한 안이다. 그런데 그리기는 원소마다 칸을 만든다. 10만 개에 3.1초·노드 30만 개였고, 100만 개는 240초 안에 끝나지 않았다. Rust에서 웹뷰로 110MB 문서를 넘기는 비용은 측정하지 않았다.
- **이미 있는 출력이 더 정직한 요약이다.** 일반 실행의 표 출력은 앞 100행·30열을 보여 주면서 전체 행·열 수를 함께 적는다(`assets/python/rich_runner.py`의 `capture_table`). 데이터 수업은 이 출력과 `shape`·`head()`·`value_counts()`를 읽게 하는 편이 맞다.
- **교육적 결론.** 데이터 수업에서 코드 흐름이 이기는 곳은 작은 순수 Python 자료(목록·딕셔너리·반복·함수 호출)다. AICE 감사가 꼽은 15곳이 그렇다(`audit/aice-associate.md`). 추적기가 DataFrame·ndarray의 작은 요약(모양, 열 이름·자료형, 앞 몇 행, 원소 20개 이하 배열 값)을 기록하면 HOLD-OPAQUE 22곳 중 일부가 적용 대상이 된다. 그 경우에도 「앞 n행」이라고 화면에 적어 전체처럼 보이지 않게 해야 한다(§9의 5).

한계:

- TensorFlow·XGBoost: 이 컴퓨터의 앱 수업 Python에 설치돼 있지 않아(`ModuleNotFoundError`) 위 표에 없다. 텐서도 같은 `OPAQUE` 경로라 기록이 작을 것으로 **추정**하지만 측정하지 않았다. 내용 검증에는 별도 임시 venv를 썼다(§6 검증 기록).
- C·Java의 큰 자료는 측정하지 않았다. 수업의 C·Java 예제는 원소 수십 개 이하다.
- macOS에서는 측정하지 않았다. 메모리 측정은 Windows API라 Windows 전용이다.
- 한 번씩만 측정했다. 몇 배·몇 자리의 차이만 결론에 쓰고 10% 단위 차이는 쓰지 않는다.

## 5. 수업 감사

네 개의 격리된 읽기 전용 검토가 98개 코스 참조(고유 수업 98개)와 그 1031스텝(코스 묶음 기준 438·365·228)을 나눠 판정했다. 보고는 `audit/`에 있다.

| 보고 | 범위 | 비주얼라이저 판정 | 결함 | 검토 깊이와 한계 |
| --- | --- | --- | --- | --- |
| `audit/java-backend-01-22.md` | 자바 백엔드 1~22, 214스텝 | APPLY 25, HOLD 2, IMPOSSIBLE 85 | 결함 6, 경미 29 | Java 정답 129개를 JDK 25로 실행해 모두 통과, 준비 코드는 1개 빼고 실패. 터미널 수업 8개는 Git Bash로 재연. 위임분은 표본만 다시 확인 |
| `audit/java-backend-23-44.md` | 자바 백엔드 23~44, 225스텝 | APPLY 9, HOLD 2(JS) | 결함 2묶음, 경미 13묶음 | 27~30은 실행·해설 재연, 34~41은 기록 출력과 대조만, 나머지는 자동 검사와 일부 정독 |
| `audit/engineer-practical.md` | 정보처리기사 30수업, 365스텝 | APPLY 31, HOLD 2, NOT-APPLY 109 | 결함 5, 경미 16 | 실행 없이 코드와 기록 출력으로 판정(C 출력은 손 계산) |
| `audit/aice-associate.md` | AICE 24수업, 228스텝 | APPLY 15, HOLD-OPAQUE 22 | 결함 15, 경미 85 | 기록 출력과 대조. 시험 버전(pandas 1.5.3 등)·TF는 실행 없음 |

검토가 찾은 결함 가운데 내가 직접 확인하고 고친 것은 §6에 있다. 고치지 않은 것과 구조 문제는 §7에 있다. 검토자의 APPLY 줄·단계 추정은 넣기 전에 검증기로 다시 확인했다. 두 개는 틀려서 고쳤다(§6).

## 6. 적용한 국소 개선

바뀐 수업은 34개다(자바 백엔드 9, 정보처리기사 13, AICE 12). 각각 시작 커밋(0090f482)의 revision보다 정확히 하나 크다. 작업 중 5개 수업이 두 번 올라갔다가 바로잡았다. 비교 기준을 매 빌드마다 다시 쓰이는 작업 manifest로 잡은 탓이었고, `apply_flow.py`는 이제 시작 커밋과 비교한다(`MQ_AUDIT_BASE`). 해설 검토 기록(`tools/redesigned_lessons/narration-review.json`)은 바뀐 스텝의 새 내용에 다시 묶었다. 바뀐 50개 기록은 모두 이전에도 「reviewed」였고, 바뀌지 않은 문장의 검토 메모는 그대로 옮겼다. PRD를 바꾼 경우에는 기존 승인 근거 뒤에 2026-11-02 변경 사유를 덧붙여 다시 찍었다. 모두 목표·교육 기법이 그대로인 명백한 오류 수정이다.

### 내용 오류

| 수정 | 수업 | 근거 | 방법 |
| --- | --- | --- | --- |
| 마지막 도전 문제가 목표 출력을 「지금/현재 결과는 X」로 적어 첫 실행 결과와 어긋남 → 「완성하면 X가 나와요」 | AICE 10개, 정보처리기사 11개 | 각 수업 `tests/lesson-cases`의 첫 실행 출력과 대조(예: aice-regression-metrics 첫 실행 `16.0 / 290.666667 / -3.36`) | 생성기 `tools/final_challenges/*.py`를 고쳐 `apply-final-challenges.py`로 다시 만듦. 시작 커밋과 비교해 바뀐 과제 필드는 goal과 단원 전제뿐이다. 예외로 engineer-c-pointers 도전 과제의 명시적 `"code_flow": true`가 빠졌는데, 생략하면 true라(`src/repository_course.rs:133`) 버튼은 그대로다 |
| 해설 숫자 0.6436 → 0.6835, 1.4076 → 0.9076 | aice-neural-classification 2·5번 | 기록 출력과 손 계산(BCE 평균, softmax 교차 엔트로피 평균) | `narration_review.py record`의 fixed 기록 |
| 시연 라벨 BAG → FAG(비하어) → BIG → FIG | engineer-c-arrays 2.1.2 | 해설·채점 변형·기록 출력 세 곳 | 같은 원리(첫 칸만 바뀜)를 보이는 무해한 라벨 |
| 단원 전제의 참조열 1,2,3,1,4,2 → 코드·채점과 같은 1,2,3,4,1,2 | engineer-os | FIFO 3프레임에서 코드는 페이지 부재 6회, 전제대로면 4회 | 이 수업의 도전 생성기는 이후 교체돼 낡았으므로 내용과 PRD를 직접 고침 |
| 오탈자 「늘 계획이」 → 「늘릴 계획이」 | java-oop-patterns | 원본 생성기 `tools/principles_lessons/o3_patterns.py`도 고침 | |
| 파일을 읽는 Java 스텝 10개에 `code_flow: false` | java-crud 2개, java-files 8개 | Java 추적은 `Main.java`와 입력만 쓴다(`src/java_trace.rs:103-111`). 앱의 추적기로 java-files 2번 정답을 추적하니 `NoSuchFileException: quotes.txt`로 끝났고, 채점 실행은 통과 | 런타임이 과제 파일을 넘기면 되돌린다(§9의 1) |

### 선별 시각화 해설(13수업 15스텝, 동작 17개)

출력이 보여 주지 못하는 상태(같은 객체를 가리키는 두 이름, 따로 있는 두 프레임, 반복 중간값, 재귀 스택, static 칸)를 보여 줄 때만 넣었다. 모든 문장은 검증기가 실제 추적에서 찾은 단계의 기록(`target/mcq/<key>.json`의 `code_flow`)과 대조했다.

| 수업 · 스텝 | 언어 | 단계 | 실제 기록에서 확인한 상태 |
| --- | --- | --- | --- |
| aice-python-api 2.1.1 (두 번) | Python | 5행 | 고치기 전 `ordered`·`minutes`가 같은 객체 1개, 고친 뒤 객체 2개 |
| aice-python-conditions 2.1.3 | Python | 9행 2번째 | `minute` 42, `delayed`는 아직 원소 하나 |
| engineer-python-values 1.1.4 (두 번) | Python | 6행 | 고치기 전 `stocks`·`backup`이 같은 객체, 고친 뒤 둘 |
| engineer-python-calls 1.1.2 | Python | 7행 2번째 | `record` 두 번째 호출(value 4)에서 같은 기본 목록 |
| engineer-python-calls 2.1.3 | Python | 3행 | `multiply` 프레임 4개 |
| engineer-c-pointers 1.1.3 | C | 11행 | `p`·`q` 모두 `stock`, stock 7 |
| engineer-c-double-pointers 1.1.3 | C | 11행 | `pp → p`, `p → other`, stock 2 |
| engineer-c-double-pointers 1.1.4 | C | 13행 | `pp → q`, `q → other`, `p → stock` |
| engineer-c-functions 2.1.2 | C | 6행 | `sum_to` 프레임 4개, 맨 위 n 0 |
| java-methods 2 | Java | 4행 call | 프레임 `main`·`add_fee`, add_fee의 amount 2000 |
| java-references 6 | Java | 12행 call | `replace`의 item과 a가 같은 객체(힙 1개) |
| java-arrays 5 | Java | 11행 2번째 | index 1에서 total 2000(덮어쓰기) |
| java-conditions 7 | Java | 9행 | 두 번째 if 직전 fee 0 |
| java-static 7 | Java | 17행 | 객체 둘. amount는 static 칸에 있음(같은 수업 기존 해설과 같은 화면 영역) |
| java-roles 5 | Java | 7행 call | 스택 `main → total → fee` |

java-methods·java-references는 처음에 `step_line`으로 적었다가 검증기가 「그 줄에 그 단계가 없다」로 거부했다. Java 추적은 메서드 첫 줄을 `call` 단계로 기록하므로 `call`로 고쳐 통과했다. 위 C 단계는 Windows 추적으로만 확인했고 macOS LLDB 추적에서는 확인하지 않았다(§9의 3). 실제 앱에서 음성과 강조가 맞물리는지는 듣지 않았다.

판정하고 넣지 않은 예: aice-python-start 1.1.4는 정수 재대입이라 출력이 이미 보여 준다(NOT-APPLY).

### 검증 기록

모든 수업 검증은 `.scratch/course-visualizer-audit/validate.sh`로 했다. `MOLIP_DATA_DIR`은 임시 폴더였고, 학습자 진도·초안·앱 프로필은 읽거나 쓰지 않았다. 수업 Python은 앱의 ml-env를 실행만 했다. 그 ml-env에는 TensorFlow·XGBoost가 없어서, 그 수업은 `requirements-learning.txt`로 만든 임시 venv(TF 2.21.0, XGBoost 3.4.1, pandas 3.0.6, scikit-learn 1.9.1)로 검증했다.

| 검사 | 결과 |
| --- | --- |
| `validate_redesigned_lesson` (앱 ml-env) | 통과 30수업: aice-split, aice-regression, aice-regression-metrics, aice-classification, aice-classification-metrics, aice-models, aice-python-api, aice-python-conditions, engineer-c-arrays, engineer-c-conditions, engineer-c-double-pointers, engineer-c-functions, engineer-c-pointers, engineer-c-structures, engineer-java-flow, engineer-java-references, engineer-java-static, engineer-python-values, engineer-python-calls, engineer-sql-group, engineer-os, java-methods, java-references, java-arrays, java-conditions, java-static, java-roles, java-crud, java-files, java-oop-patterns |
| `validate_redesigned_lesson` (임시 venv) | 통과: aice-boosting(9스텝), aice-tensorflow(9), aice-neural-regression(9). aice-neural-classification(9) |
| 증거와 현재 바이트 | 바뀐 34수업마다 `target/mcq/<key>.json`의 `lesson_sha256`이 지금 `courses/redesigned/<key>.json`과 같은지 확인했다. 34개 중 34개가 통과 기록이고 해시가 같다. 증거 파일은 git 밖(`target/`)이라 다시 만들려면 위 스크립트를 다시 돌린다 |
| `build-redesigned-git.py --check`, `build-redesigned-course-bundle.py --check` | 통과 |
| `test_lesson_prd`, `test_narration_review`, `test_lesson_registry`, `test_redesigned_highlights`(새 계약으로 고침) | 통과 |
| `cargo test --test code_flow_policy --test lesson_registry` | 통과(5, 1) |
| `build-kpc-course.py` | 통과, `kpc-finance.json` 변화 없음 |
| `test_narration_openings.py` | 실패 90건. 시작 커밋에서도 89건 실패한다(2026-10월 고정 기준과 내용 비교). 늘어난 1건은 java-oop-patterns 오탈자 수정이다. 검사 자체가 낡았다(§7의 8) |

## 7. 구조 재설계 계획(적용하지 않음)

새 개념 위치·스텝 분할·수업 순서는 대표 재설계와 근거를 먼저 남기고 승인 뒤 적용한다. 각 항목의 근거는 해당 감사 보고에 있다.

1. **가르치기 전에 쓰는 문법(자바).** java-roles 8번이 앞에 없는 `||`를 「2번에서 본」이라 부른다. java-class-objects 6번(`@Override`, `super.hashCode()`, 패턴 `instanceof`), java-inheritance-composition 1~3번(`switch` 식, `getClass().getSimpleName()`), java-streams 11번(`max`, `Optional.map`, 메서드 참조), java-oop-patterns 4번(`switch` 화살표), java-calculator(재귀). 대표 재설계: 그 스텝 바로 앞에 그 문법 하나만 관찰하는 작은 스텝을 두거나, 준비 코드를 이미 배운 문법으로 바꾼다. 문제 본질이 바뀌면 새 스텝 코드가 필요하다.
2. **java-react(자바 과정 43번)는 JavaScript를 처음 쓴다.** 앞 수업 어디에도 JS가 없다. 화면 이해 보조라는 위치(`docs/redesigned-courses.md`)에 맞게, 첫 단원에 JS 값·함수 하나를 관찰하는 도입을 두는 안.
3. **SQL 수업이 MySQL에서 PostgreSQL로 말없이 바뀐다.** split 한도 개념은 java-regex와 java-rq에서 세 번 반복된다.
4. **정보처리기사.** engineer-c-structures(19스텝, 목표 5개)를 나누는 안. 10개 수업의 목표·전제가 「직접 답해요/적으세요」를 약속하지만 그런 스텝이 없다(목표 문장 수정이라 PRD 재승인 범위로 보류). engineer-mixed 3.2.1은 약속한 회귀 테스트 판단을 채점하지 않는다. 퀴즈만 있는 내용 일부(테스트 커버리지, 페이지 교체, 멱등성)를 작은 Python 실행 스텝으로 바꾸는 안.
5. **AICE.** 마지막 도전이 가르치지 않은 문법(삼항식, 리스트 내포, 키워드 전용 `*`)을 쓴다. manifest의 선수 관계가 24개 수업 모두 비어 있다(PRD는 앞 수업을 선수로 적음). 시험 환경의 xgboost 0.90에서 aice-boosting 2·9번이 다르게 동작할 수 있다(소스 읽기 근거, 실행 안 함).
6. **반복 패턴.** 「문제가 말한 한 곳을 고치세요」류 막연한 할 일(자바 69스텝, AICE 약 20스텝), 목표 문장을 그대로 읽는 해설 60스텝, 쓰지 않는 import(java-crud 8, h2-memory-file 3, AICE 약 20), 붙어 쓴 띄어쓰기 오탈자 묶음(`audit/engineer-practical.md` D9). 하나씩 고치면 수십 개 revision이 바뀌므로 검사 도구를 먼저 만들고 한 번에 처리한다(아래 8).
7. **남은 시각화 후보.** 감사가 APPLY로 판정한 약 80곳 중 15곳만 넣었다. 남은 후보와 정확한 줄·단계 추정은 각 보고의 APPLY 목록에 있다. 같은 방법으로 이어서 넣는다: Python은 `tools/course_audit/flow_probe.py`로 단계를 확인하고, `apply_flow.py`로 넣은 뒤 검증기로 재생한다. 다음 순서는 java-calculator·java-rq·java-regex(자바 23~44)와 정보처리기사의 C 구조체·힙 스텝이다.
8. **빌드 검사로 만들 것.** (a) 문제 목표의 「지금/현재 출력·결과는 X」를 준비 코드 첫 실행과 대조해 다르면 거부한다. 이번에 손으로 찾은 23곳의 재발 방지다. (b) 할 일에 「코드 흐름 보기」가 있으면 해설에 `code_flow`가 있어야 한다(자바 12스텝이 안내만 함). (c) 과제 `files`가 있는 Java 스텝은 런타임이 파일을 넘기기 전까지 `code_flow: false`여야 한다. (d) `test_narration_openings.py`는 고정 기준 대신 현재 수업과 소개 문장의 관계만 검사하도록 바꾼다.

## 8. Rust 기초 수업

사용자가 Rust 기초 4수업의 PRD와 대표 문제를 승인했다(root 전달, 2026-11-02). 정식 제작은 별도 checkout에서 진행 중이다. 이 checkout은 Rust 수업을 만들거나 코스에 넣지 않는다. 루트 `AGENTS.md`의 공통 원칙과 §3의 시각화 규칙은 Rust 수업에도 같다. Rust 코드 흐름은 런타임 지원이 이 저장소에 들어온 뒤 §3 규칙으로 판정한다.

## 9. 런타임 담당자에게 넘길 계약

이 checkout은 아래 런타임 파일을 바꾸지 않았다. 필요한 변경과 그 이유만 적는다.

1. **Java 추적에 과제 파일 전달.** `src/java_trace.rs::trace`와 `src/player_ui.rs`의 호출이 `task.files`를 받아 작업 폴더에 써야 한다(Python 추적은 이미 그렇게 한다). root 보고(2026-11-02)로는 통합 checkout `mq-code-flow-default`에 Java `trace_files`가 들어가 준비 데이터 파일을 넘기는 실제 검사가 통과했다. 이 checkout에서는 확인하지 않았다. 병합 뒤 java-crud·java-files의 `code_flow: false` 10개를 지우고, 검증기(`examples/validate_redesigned_lesson.rs`)의 Java 분기가 같은 파일을 넘기게 바꾼 다음 두 수업을 다시 검증한다.
2. **해설의 `code_flow`를 열 수 없을 때.** `assets/layout/agent.js`의 `code_flow`는 버튼이 없거나 비활성이면 최대 180초 기다린 뒤 오류로 해설을 멈춘다. 지원하지 않는 OS(예: Linux의 C)나 추적 실패 때는 그 동작을 건너뛰고 문장만 읽는 편이 안전하다. 지금 배포 대상(Windows, macOS arm64)은 Java·Python·C를 모두 추적하므로 현재 해설에는 영향이 없다.
3. **macOS C 추적 확인.** 이번에 넣은 C 해설 4곳(engineer-c-pointers 1.1.3, engineer-c-double-pointers 1.1.3·1.1.4, engineer-c-functions 2.1.2)의 단계를 LLDB 백엔드에서 같은 줄·같은 상태로 재생해 확인해야 한다. 전체 79문제 검사에 이 네 단계를 넣으면 된다.
4. **큰 목록 그리기 상한.** `render.js`는 원소마다 칸을 만든다. 10만 원소에 3.1초가 걸렸고 100만은 그리지 못했다. 앞 n개와 「총 N개 중」 표시가 필요하다. 추적기도 단계마다 큰 목록 전체를 다시 적는다.
5. **데이터 객체 요약(선택).** DataFrame·Series·ndarray를 이름만이 아니라 모양·열 이름·자료형·앞 몇 행(「앞 n행」 표기)으로 기록하면 AICE의 HOLD-OPAQUE 22곳 중 일부를 적용할 수 있다. 원소 20개 이하 배열 값만 보여도 5곳이 바로 적용 대상이 된다.
6. **언어 확대.** root 보고로는 통합 checkout에 C++·Rust 언어·실행·채점·플레이어 시각화가 들어갔다(이 checkout에는 없고 확인하지 않았다). 병합 뒤 `tools/build-redesigned-git.py`의 언어 목록(`('java', 'python', 'c')`)과 검증기의 추적기 분기를 함께 넓힌다. java-react 3.1.4·3.1.5가 JS의 첫 후보다.

## 10. 통합 순서와 게시

1. 이 브랜치의 커밋을 리뷰한 뒤 병합한다. main에 직접 push하지 않았다.
2. 바뀐 수업은 모두 새 revision이다. 수업 저장소에 새 태그를 게시하고 코스 manifest가 새 revision·SHA-256을 참조하게 하는 일은 `docs/redesigned-courses.md` 「최초 게시 후 개정」 절차로 따로 한다. 이 checkout은 게시하지 않았다.
3. 통합 checkout의 Java `trace_files`와 함께 병합한 뒤 §9의 1의 opt-out 되돌리기와 검증기 변경을 한 커밋으로 한다.
4. 병합할 때 충돌 가능 파일: `tools/redesigned_courses/catalog.json`(revision), `courses/redesigned-courses/*.json`·`courses/redesigned/*.json`(빌드 산출물, 충돌 시 원본에서 다시 빌드), `tools/redesigned_lessons/narration-review.json`, `examples/validate_redesigned_lesson.rs`(통합 checkout도 추적기 호출을 바꿨다면 수동 병합). 산출물은 손으로 고치지 말고 `build-redesigned-git.py --lesson all`과 `build-redesigned-course-bundle.py`로 다시 만든다.

## 11. 통합 브랜치 결과(`feat/course-audit-rust-release`, 2026-11-03)

기준은 build165와 같은 `b9fb3a99`다. 이 감사 브랜치의 `57f3406d`·`070f725c`와 Rust 4수업 커밋 7개를 합쳤다. main push와 게시는 root가 한다.

### 앱에 실제로 보이는 코스(§2 범위 대조)

- 배포 빌드는 `RepositoryPlayer`만 띄운다(`src/main.rs`의 `MOLIP_LEGACY` 분기는 debug 빌드 전용). KPC 금융·`java-basics`·아침 연습은 배포 앱에 보이지 않는다.
- 보이는 것은 기본 세 코스(`src/bundled_courses.rs`)와 각 수업의 도전 과제, 학습자가 불러오는 공개 코스다. 통합 뒤 참조 102개, 스텝 1113개(`inventory.md`). 자바 백엔드는 48수업이고 Rust 4수업이 `java-launch` 바로 뒤에 이어진다.
- 감사 범위 밖으로 남은 것: Rust 4수업의 레벨링 감사(§5 방식의 의미 검토는 하지 않았다. 사용자가 승인한 PRD·대표 문제와 실제 채점 검증만 있다), 학습자가 만든 공개 코스, Codex가 맡은 토요 특강.

### 코드 흐름 보기(§3 갱신)

- 런타임은 Java·Python·JavaScript(모든 OS), C·C++·Rust(Windows·macOS)를 추적한다(`Task::code_flow_availability`). 해설 `code_flow`도 여섯 언어를 받는다.
- §9의 1을 끝냈다. java-crud·java-files의 `code_flow: false` 10개를 지웠다. 두 수업은 build165와 바이트가 같아져 revision을 `java-crud-9`·`java-files-8`로 되돌렸고, 그 내용에 남긴 검토 기록을 복원했다. 지금 명시적 `code_flow: false`는 0개다. 숨김은 터미널 스텝과 예제 없는 문항뿐이다.
- 검증기에 `MQ3_VALIDATE_TRACE_ALL`을 더했다. 버튼이 보이는 모든 스텝의 준비 코드·정답을 모든 테스트 입력으로 추적해 채점 실행과 출력·성공 여부가 같은지 본다.
- 이 검사로 Rust 결함 하나를 찾아 고쳤다. `println!`만 있는 `main`(rust-values 1번)은 단계가 0개였다(`native_lldb.py`의 `early()`). 회귀 테스트는 `native_trace::tests::rust_runs_grades_and_traces_moves_from_one_build`.

### §9의 3: macOS C 해설 재생

Windows(TinyCC)와 macOS arm64(LLDB, CI run 41408030077)에서 C 해설 4곳의 단계를 비교했다. 4곳 모두 줄·종류·호출 스택·지역 값이 같다(예: engineer-c-pointers 11행 `p`·`q`가 둘 다 `stock`, `stock`은 7). 전체 단계 번호만 다르다(macOS가 선언 줄에서 더 멈춘다). 해설은 `line`·`event`·`nth`로 찾으므로 영향이 없다.

### §4·§9의 4: 큰 자료 상한

- Python 추적기는 list·tuple·set·dict의 앞 100개, 「… N개 더」, 실제 크기를 기록한다. 문자열은 2000자에서 자르고 전체 길이를 붙인다(JavaScript 추적기와 같은 방식). 뷰어는 실제 크기를 제목에 쓰고 어떤 언어든 칸을 200개까지만 그린다.
- 같은 100만 원소 실험(Windows, 1회): 추적 0.15초·12KB·그리기 50ms(전: 4.5초·110MB·240초 안에 못 그림). 상한이 없는 100만 칸 배열도 52ms다.
- pandas·ndarray는 여전히 이름만 보인다. 해설 시각화를 더하지 않았다.

### 검증 기록

| 검사 | Windows | macOS arm64 |
| --- | --- | --- |
| `validate_redesigned_lesson` + 전 스텝 추적: Rust 4수업(40스텝), engineer-c-pointers·double-pointers·functions, java-crud·java-files | 통과(Rust는 Docker 이미지 `249ce3e12f2e`) | 통과(run 41408030077, 41559343966) |
| `native_trace` Rust·C++ 테스트 | 통과 | 통과 |
| `python_trace` 테스트 3개(큰 자료 상한 포함) | 통과 | 상한 테스트만 통과 |
| `js_trace` 테스트 5개 | 통과 | 통과(run 41559343966) |
| 실제 앱(임시 프로필) Rust 수업 열기·해설 재생 후 학습자 상태 복원·오답·정답·초기화 | 4수업 통과(353·570·423·481초) | 4수업 통과(313·506·345·409초, run 41561837242) |
| `build-redesigned-git.py --check`, `build-redesigned-course-bundle.py --check`, `test_lesson_prd`·`test_narration_review`·`test_lesson_registry`·`test_redesigned_highlights`·`test_build_inputs`, `inventory.py --check` | 통과 | |
| `cargo test --test bundled_courses --test lesson_registry --test backend_journeys --test code_flow_policy` | 통과 | |
| `test_narration_openings.py` | 실패 91건. build165에서 90건. 늘어난 1건은 java-oop-patterns 오탈자 수정(낡은 고정 기준과 비교, §7의 8) | |

실제 음성과 강조가 맞물리는지는 들어 보지 않았다. 정적 검사와 재생 통과를 음성 확인으로 보지 않는다.

### 시간이 드는 곳

Windows의 Rust 실행 한 번은 약 1.8~2.2초다. 컨테이너 시작이 1.0~1.2초, rustc 컴파일 약 0.45초, 프로그램 실행 약 6ms다(24스레드 PC, 다른 앱 검사와 동시에 3회). 앱 자체 검사는 스텝마다 해설 실행·오답·정답·초기화 제출로 여러 번 컴파일하므로 rust-values 8스텝이 353초, rust-flow-functions 10스텝이 570초, rust-ownership-borrowing 10스텝이 423초, rust-data-results 12스텝이 481초 걸렸다. macOS는 컨테이너 없이 같은 검증기가 수업당 44~75초다(Windows 108~146초). 그런데 컨테이너가 없는 macOS 실제 앱 검사도 313~506초로 비슷했다. 한 번의 실행은 컨테이너 시작이 대부분이지만, 수업 전체 자체 검사 시간은 해설 재생·화면 대기·스텝마다 여러 번의 제출이 대부분이다. 그래서 앱 자체 검사의 수업 전체 시간 한도만 AICE 긴 수업과 같은 1200초로 올렸다. 학습자가 겪는 컴파일 60초·실행 15초 한도는 바꾸지 않았다. 저사양 PC에서는 Windows 컨테이너 시작 시간이 그대로 학습자 대기로 보인다. 저사양 기기는 측정하지 않았다(저사양 실행 개선은 사용자가 폐기했다).

macOS 실제 앱 검사가 찾은 결함: 데이터 폴더에 MQ의 rustc가 없으면 Rust 실행이 `FileNotFoundError`를 보였다. 이제 환경 점검과 같은 「Rust 컴파일러가 없어요. 환경 설치로 준비하세요.」를 보인다(macOS 테스트 `rust_without_the_toolchain_asks_for_the_environment_install`). `MOLIP_RUST_HOME`은 검증 실행이 설치된 도구를 다시 쓰게 한다(`MOLIP_TCC`와 같은 방식).
