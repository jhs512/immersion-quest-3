# Rust 기초 네 수업 인계

상태(2026-11-02): PRD와 대표 문제는 승인됐다([승인 기록](README.md#승인-기록)). 네 수업의 정식 콘텐츠와 자바 백엔드 코스 연결은 이 브랜치(`feat/rust-course-draft`)에 있다. 앱에는 아직 `rust` 언어가 없어서 수업을 열거나 채점할 수 없다. 이 문서는 런타임 통합 담당자가 지켜야 할 콘텐츠 계약과 통합 순서다.

## 이 브랜치가 바꾼 것과 바꾸지 않은 것

바꾼 것: Rust 수업 네 개의 원본(`tools/redesigned_lessons/rust_*`), 빌드 산출물(`courses/redesigned/rust-*.json`), 검증 사례(`tests/lesson-cases/rust-*.json`), 검증 코스(`tests/fixtures/player-pilot/{룬,렌,롤,륵}/course.json`), 코스 등록(`catalog.json`, `backend-sequence.json`, `lesson-challenges.json`, `backend_previews.py`, `release.json`), 해설 소개·검토 기록, 수업 수를 세는 테스트의 숫자.

바꾸지 않은 것: `src/`, `examples/`, `build.rs`, Cargo 파일, 설치·배포 스크립트, 공통 빌드 도구(`tools/*.py`), 다른 수업. 런타임과 공통 dispatch는 다른 checkout에서 통합한다.

## Rust 콘텐츠 계약

수업 JSON은 기존 `redesigned` 코딩 수업과 같은 스키마다. 새 필드는 없다. 런타임이 맞춰야 할 것은 아래뿐이다.

| 항목 | 계약 |
| --- | --- |
| 언어 값 | `task.language == "rust"`. `TaskLanguage`에 `Rust`(serde `rust`)가 필요하다. 지금은 알 수 없는 variant라 `Lesson::parse`가 실패한다. |
| 파일 | `entry_file`이 비어 있으면 `main.rs`. `files`는 쓰지 않는다. 외부 크레이트·Cargo 없음. |
| 실행 | 새 임시 폴더에 `main.rs`를 쓰고 `rustc --edition=2024 -o main[.exe] main.rs`로 컴파일한 뒤 실행 파일을 표준 입력과 함께 실행한다. 입력은 모두 빈 문자열이다. |
| 컴파일 실패 | `success: false`. `stderr`에 rustc 진단 원문을 그대로 둔다. 해설의 `run.expect_error`(`E0384`, `E0382`, `E0308`, `E0499`, `E0596`, `E0599`, `E0594` 등)는 `stderr`에 그 코드가 들어 있는지만 본다. 번역·요약하면 검증이 깨진다. |
| 경고 | 경고는 실패가 아니다. 모든 정답은 경고 없이 컴파일된다(검증기가 확인). |
| 채점 | `check_c`와 같다. 각 `tests` 사례의 stdout에서 끝 줄바꿈을 뗀 값이 `expected`와 같아야 한다. 모두 통과하면 `variations`를 적용한다. |
| 준비 값 바꾸기 | `variations[].values`의 각 이름에 대해 주석·문자열 밖의 첫 `let [mut] 이름[: 타입] = 초기식;`의 초기식을 값으로 바꾼다. 초기식은 괄호 깊이 0의 `;`까지다(`vec![1, 2]`, `String::from("MQ")` 포함). `mutate_c`는 `: i32` 같은 타입 표기를 처리하지 못하므로 그대로 쓰면 R1 4번 등이 실패한다. 기준 구현은 `validate_rust_lessons.py`의 `mutate_rust`다. 선언이 없으면 「준비 코드의 … 선언과 처음 값은 그대로 두세요」로 실패한다(C와 같다). |
| 시간 제한 | 컴파일 60초, 실행 15초로 검증했다. 첫 컴파일이 느린 기기는 컴파일 시간을 따로 준다. |
| 편집기 | 강조 문법이 없으면 Java 문법을 써도 된다(C와 같은 방식). |
| 코드 흐름 보기 | 쓰지 않는다. 어느 Rust 스텝에도 `code_flow`가 없다. Rust 추적기가 입증되기 전에는 버튼을 보이지 않아야 한다. 해설은 진단과 출력만 말하고 메모리·소유권 그림을 만들지 않는다. |
| 해설 동작 | `say`, `run`(`lines`, 선택 `expect_error`), `patch_code`, `submit`만 쓴다. `validate_redesigned_lesson`이 이미 재생하는 동작이다. |
| 도구 준비 | 실행 전에 `rustc`가 있는지 확인하고 없으면 설치 안내를 보인다. Windows 검증은 `x86_64-pc-windows-msvc` 툴체인이었다. 이 툴체인은 MSVC 링커가 있어야 실행 파일을 만든다. |

## 지금 상태를 검증하는 명령

런타임 없이 콘텐츠만 검증한다.

```powershell
python docs/curriculum/rust-foundations/validate_rust_lessons.py --evidence
python tools/build-redesigned-git.py --check --lesson rust-values   # 네 수업 각각
python tools/build-redesigned-course-bundle.py --check
```

첫 명령은 실제 rustc로 스텝마다 아래를 확인한다. 준비 코드는 채점에서 실패한다. 정답은 테스트와 준비 값 바꾸기를 모두 통과한다. 해설을 재생한 출력이 기록과 같다. 기록한 오답은 실패하고 다른 정답은 통과한다. 결과는 `evidence/<key>-<os>.json`에 남는다.

## 런타임 통합 순서

1. `TaskLanguage::Rust`, `filename()`의 `main.rs`, `editor()`, `lesson_runner`의 `run`·`check` 분기, Rust용 준비 값 바꾸기를 더한다. 이 브랜치의 콘텐츠 파일은 그대로 둔다.
2. `tools/build-redesigned-git.py`의 실행 강조 검사 언어 목록(`('java', 'python', 'c')`)에 `rust`를 더한다. 지금은 `validate_rust_lessons.py`가 같은 검사를 한다.
3. 이 브랜치를 합친 뒤 `cargo run --example validate_redesigned_lesson -- tests/lesson-cases/rust-values.json target/rust-values.json`을 네 수업에 대해 실행한다. 이 검증기와 `validate_rust_lessons.py`의 결과가 같아야 한다.
4. `cargo test --test lesson_registry --test bundled_courses --test backend_journeys`를 실행한다. 이 테스트의 수업 수는 이미 Rust 네 수업을 포함하도록 바꿨다.
5. 앱에서 네 수업을 열어 정답·오답·실행·해설 재생·초기화를 직접 확인한다. 실제 음성과 강조가 맞는지는 들어 보고 확인한다.
6. macOS에서 1과 3을 실제로 실행하거나 CI 증거를 남긴다. 그전까지 macOS는 미검증이다.
7. 실제 채점을 확인한 뒤 마지막 도전 지정(`lesson-challenges.json`)과 주제 분류를 따로 검토한다.

## 남은 일

- 런타임 통합(위 1~4). 이 브랜치에서는 하지 않는다.
- macOS 검증. 지금 증거는 Windows뿐이다.
- 앱 안의 실제 재생·음성 확인. 정적 검사와 rustc 재생만 했다.
- 게시. `tools/publish-*.py`는 실행하지 않았다. main에 push하거나 배포하지 않았다.
