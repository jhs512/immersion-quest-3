# Windows 이어가기: MQ 자바 백엔드 확장

기록일: 2026-10-20. 이 파일은 컴퓨터와 대화가 바뀌어도 이어가기 위한 작업 기준이다.

## 현재 지시와 재개 조건

사용자는 첫 수업의 PRD·대표 문제에 “이 구성으로 첫 수업부터 제작”이라고 승인했다. 이후 “잠시만 계획만 세우고 진행은 하지 말아봐”라고 제작을 중지했다. 마지막 요청은 계획과 현재 변경을 커밋·푸시하여 Windows에서 pull 후 “계획 마저 진행해”라고 하면 이어갈 수 있게 하는 것이다.

**현재는 계획만 보존한다. pull 자체로 제작을 시작하지 않는다.** 사용자가 “계획 마저 진행해”라고 하면 이 파일과 아래 원본을 읽고 첫 수업 제작을 재개한다. 이미 승인된 8스텝의 제작 승인을 다시 묻지 않는다. 범위를 바꾸면 변경 부분만 검토한다. Windows로 원격 접속하거나 새 대화를 만드는 작업은 수행하지 않았다.

## 원본과 우선순위

1. `AGENTS.md`, `CONTEXT.md`, `docs/content-rules.md`, `docs/voice.md`, `docs/agents/narration.md`를 따른다.
2. 전체 계획: `docs/curriculum/java-backend-expansion.md`.
3. 후보 44개·추천 의존 관계: `tools/redesigned_courses/java/backend-extension-plan.json`.
4. 승인된 첫 수업: `tools/redesigned_lessons/java_launch/approved-prd.json` 및 `approved-prd.md`. `draft-prd.*`는 검토 당시 초안으로 보존한다.
5. 8스텝의 명령·기대 결과·선택지·문구 변경: `tools/redesigned_lessons/java_launch/prototype.json`.
6. 실제 JDK 검증 재현: `tools/verify-java-launch-prototype.py`.

`.scratch/`와 `target/`는 Git에서 제외된다. 이전 로컬 이슈나 검증 출력이 Windows에 없더라도 이 문서와 추적되는 원본으로 재개한다. 출력은 다시 생성한다. 새 이슈를 만들 때는 `docs/agents/issue-tracker.md`를 먼저 읽는다.

## 절대 놓치지 않을 제작 기준

목적은 이해다. 완전히 간단한 정상 예제에서 시작해 한 번에 조건 하나만 바꾼다. 기술·파일·설정·작성량으로 난도를 올리지 않는다.

- 첫 수업은 Main.java 하나, 출력 문구 하나, 외부 서비스 0개다.
- 새 개념은 스텝당 하나, 학생 수정은 보통 1~3줄이다.
- 각 스텝은 시작 상태 → 순서 있는 **할 일** → 실행 → 실제 결과 관찰을 명확히 보여 준다.
- 파일을 뒤에서 몰래 바꾸지 않는다. 제공된 준비 코드와 해설용 준비 상태는 먼저 설명한다.
- 명령 하나를 실행하고 결과를 짚은 뒤 다음 명령으로 넘어간다.
- 같은 실습 폴더를 이어 쓰고 학생의 파일·선택·진도를 보존한다. 해설은 별도 폴더에서 수행한다.
- 문구·가격·띄어쓰기·발음은 공통 정책을 따른다. Git은 “깃”, .git은 “깃 폴더”다. 불필요한 명령 인수 따옴표를 쓰지 않는다.
- 선택지만 맞혀 통과시키지 않는다. 실제 작업·산출물과 선택 답을 함께 검사한다.
- 첫 SQL에 Spring을, 첫 컨테이너에 DB·Redis·Kafka를 한꺼번에 붙이지 않는다. 전체 후보를 한 번에 구현하지 않는다.

## 현재 구현과 미구현을 구분하기

현재 자바 백엔드 과정은 **20수업 187스텝**이다. Bash 23스텝과 별도 Vim 14스텝, Git 수업과 자바 스트림 10스텝이 포함돼 있다. 기존 수업 개선, MQ 이름, 단축키·실패 표시, 실제 Vim 상태 확인 및 제출 준비 버그 수정은 작업 트리에 구현되어 이번 인계 커밋에 보존한다.

새 java-launch 수업은 **아직 앱에 등록하지 않았다.** 승인 PRD와 실행 프로토타입만 있다. `content.json`, 해설 캐시, 런타임 수업 JSON 및 새 편집기·JDK 연동은 제작 전이다. 제작 중단 직전 시도한 런타임 패치는 적용에 실패하여 파일 변경이 없었다. 승인 기록만 추가됐다.

macOS에서는 기존 기능을 실제 앱에서 확인했다. Windows 실제 동작은 미검증이다. macOS의 `/Applications/MQ.app`, 개인 데이터 폴더, 로컬 진도·실습 디렉터리는 Git에 들어가지 않는다. Windows에서는 기존 설치·데이터를 보존하며 저장소의 설치·실행 방법을 따른다. 앱 표시 이름은 MQ이며 기존 내부 식별자·데이터 경로를 이름 변경 때문에 바꾸지 않는다.

## 첫 제작 범위: 승인된 8스텝

추가 위치는 java-crud 뒤, java-testing 앞이다. 수업 ID는 `lsn_2a4d9041-b87a-401c-a0e8-6128415e6b2f`이며 원본 스텝 ID도 그대로 유지한다.

| 단계 | 학생 행동 | 확인할 차이 |
| --- | --- | --- |
| 1 | 제공된 Main.java를 cat으로 읽기 | 출력문 안의 첫 메모 위치 |
| 2 | java Main.java | 첫 메모 출력, Main.class 없음 |
| 3 | 편집기에서 첫 메모를 둘째 메모로 바꾸고 소스 실행 | 둘째 메모 출력 |
| 4 | javac Main.java 후 이미 배운 ls | Main.class 생성, 컴파일 자체는 문구를 출력하지 않음 |
| 5 | java Main | 컴파일된 클래스에서 둘째 메모 출력 |
| 6 | 소스만 셋째 메모로 수정하고 결과 예측 후 java Main | 여전히 둘째 메모, class는 바뀌지 않음 |
| 7 | javac Main.java | 바뀐 소스로 class 다시 생성 |
| 8 | java Main | 셋째 메모 출력 |

## 재개 후 작업 순서

1. Windows의 git 상태와 origin/main을 확인하고 사용자 변경을 보존한다. Rust/Cargo, JDK 25의 java와 javac, Git for Windows의 Bash·Vim 실행 경로를 확인한다. 이전 Mac 경로를 복사하지 않는다.
2. 실제 Main.java 편집기·PTY 터미널이 동일한 소유 실습 폴더를 사용하도록 최소 범위로 연결한다. 저장 완료 전에 명령이 실행되는 경쟁을 막는다. 단계 이동·앱 재실행에도 같은 폴더를 유지한다.
3. `src/shell_practice.rs`의 현재 파일 검사는 모든 파일을 UTF-8로 읽는다. Main.class는 바이너리이므로 그대로 재사용하지 않는다. 실제 class 산출물·출력을 검사하는 별도 명시적 계약을 설계한다. 타입이나 명령 기록만 보고 class가 맞다고 판정하지 않는다. 학생 코드 실행에는 시간·출력 제한과 자식 프로세스 정리를 둔다.
4. 교사용 시작 상태는 격리된 폴더에 재현한다. 6스텝은 둘째 메모로 컴파일된 class와 수정 전 소스를 준비해 수정→실행을 보여 준다. 학생의 실제 소스·class·답을 덮어쓰지 않는다. 해설 완료·중단·오류 후에도 학생 터미널이 사라지지 않아야 한다.
5. 승인 PRD와 prototype을 바탕으로 production `content.json` 및 단계별 해설을 작성한다. 한 동작→관찰→설명 순서, 주의할 지점, 하이라이트를 포함한다. 내용과 파생물 해시를 함께 갱신한다.
6. `tools/redesigned_courses/catalog.json`에 고유 pilot 키로 java-launch를 등록한다. 기존 식별자·순서를 보존하고 추가 위치만 반영한다. `tools/build-redesigned-git.py`, `tools/build-redesigned-course-bundle.py`로 빌드한다. 완료 시 해당 과정은 21수업 195스텝, 전체 레지스트리는 75수업 734스텝이어야 한다. 숫자만 바꿔 테스트를 통과시키지 않는다.
7. 실제 PTY·JDK로 8단계를 검증한다. 미실행·오답·컴파일 실패·소스만 변경·재컴파일·재접속·초기화·해설 중단을 확인한다. 해설이 학생 파일·class·선택·진도를 바꾸지 않는지도 검증한다. 기존 Bash·Vim·Git과 키보드 조합을 회귀 검사한다.
8. Windows 실제 MQ 화면에서 편집·입력·실행·제출·단계 이동 및 레이아웃을 확인한다. 로컬 앱과 과정에 반영하고 결과·한계를 기록한다. 이후 수업은 이 작은 첫 수업의 이해 흐름을 확인한 뒤 계획 순서대로 점진적으로 진행한다.

## 구현을 볼 위치

- 소유 실습 폴더·공유·복구: `src/git_practice.rs` (`GitPracticeStore`, `workspace_group`, `workspace_revision`).
- 실제 Bash 명령 완료·폴더 검사: `src/shell_practice.rs`.
- PTY와 프로세스 종료: `src/setup_terminal.rs`.
- 학생/해설 터미널과 readiness: `src/git_terminal_ui.rs`, `assets/terminal/terminal.js`.
- 실제 Vim 검사: `src/vim_practice.rs`, `assets/vim/practice.vim`.
- 편집·선택·제출·해설 복구: `src/player_ui.rs`, `src/explanation_session.rs`.
- 해설 액션: `assets/layout/agent.js`.
- JDK 실행 경로·제한: `src/java.rs`.터미널에서도 같은 JDK의 java/javac를 사용하도록 보장한다.
- PRD 승인·난도 검증: `tools/lesson_prd.py`, `tools/test_lesson_prd.py`.
- 레지스트리·등록 검증: `tools/lesson_registry.py`, `tests/lesson_registry.rs`, `tools/test_lesson_registry.py`.

## 기본 검증 명령

저장소 루트에서 실행한다. Windows의 Python 명령이 py이면 python3 대신 py를 사용한다. prototype은 JDK를 찾도록 JAVA_HOME 또는 검사 도구의 도움말에 나온 경로 옵션을 설정한다.

```text
python3 tools/test_lesson_prd.py
python3 tools/test_lesson_registry.py
python3 tools/build-redesigned-git.py --check
python3 tools/build-redesigned-course-bundle.py --check
python3 tools/verify-java-launch-prototype.py --help
cargo test --test lesson_registry
cargo test --test bash_basics
cargo test --test vim_practice
```

이전 Mac 검증 결과를 Windows 검증으로 보고하지 않는다. prototype 검증은 앱 구현 완료를 뜻하지 않는다. 서비스·모델 설치나 원격 과정 게시를 선행하지 않는다.

## Windows에서 사용자에게 필요한 동작

기존 저장소에서 `git pull --ff-only origin main`을 실행한 뒤 이 저장소를 Codex에서 열고 **“계획 마저 진행해. docs/curriculum/windows-handoff.md부터 읽어.”**라고 요청하면 된다. pull이 로컬 수정 때문에 막히면 기존 변경을 보존하고 원인을 확인한다. 강제 초기화하지 않는다.
