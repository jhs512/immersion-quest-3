# C++·Rust 실행·채점·코드 흐름: root 통합 계약

이 폴더와 `src/native_trace.rs`는 C++·Rust 엔진만 담는다. 과정 모델, 화면 라우팅, 공통 dispatch는 root가 붙인다.

## 공개 API (`crate::native_trace`)

| 함수 | 쓰임 |
|---|---|
| `run(NativeLanguage, source, input) -> Result<Execution, String>` | 실행과 채점. 컴파일 실패는 `state: "compile_error"`, `stderr`에 컴파일러 보고(rustc는 rendered 진단). 그 밖의 `state`는 `lesson_runner::process`와 같다(finished, runtime_error, timeout, output_limit). |
| `trace(NativeLanguage, source, input) -> Result<String, String>` | 코드 흐름 문서(JSON 문자열). `status`: ok, compile_error, uncaught_exception, step_limit, unsupported. |
| `prepare(NativeLanguage)` | 환경 설치. Windows는 Docker 이미지 빌드(이때만 네트워크), macOS Rust는 MQ 폴더에 rustup 1.29.2 → rustc 1.95.0. |
| `inspect(NativeLanguage)` | 설치 없이 작은 프로그램을 컴파일·실행해 확인. |

`run`과 `trace`는 `native_flow.py`의 같은 컴파일 명령을 쓴다. 채점은 `run`을 테스트 입력마다 부르면 된다. 추적 문서의 실행 파일이 채점한 실행 파일과 같은 명령에서 나온다.

- C++: `clang++ -std=c++17 -g -O0 -fstandalone-debug` (macOS는 `xcrun clang++`, libc++; Windows는 컨테이너의 clang 19, libstdc++ 14)
- Rust: `rustc --edition 2024 -g -C opt-level=0 --emit=link,mir` (rustc 1.95.0)

## root가 붙일 곳 (순서)

1. `src/repository_course.rs`: `TaskLanguage::Cpp`, `TaskLanguage::Rust`. `filename()`은 `main.cpp`, `main.rs`. 과제 파일이 여러 개인 문제는 아직 지원하지 않는다. 엔진은 단일 소스만 받는다.
2. `src/lesson_runner.rs::run_inner`: `TaskLanguage::Cpp|Rust => native_trace::run(lang, source, input)`. `check`도 같은 경로를 쓴다. 기존 C(TinyCC)·Java·Python은 바꾸지 않는다.
3. 코드 흐름 dispatch(현재 C는 `c_trace::trace`를 부르는 곳): Cpp/Rust면 `native_trace::trace`.
4. `assets/java-trace/core/render.js`: 문서의 `language`가 `cpp`, `rust`이다. 지금 `language === 'c'`로 고르는 이벤트 라벨(`함수 호출`)과 전역 상자 제목(`전역 변수`)을 cpp/rust에도 적용해야 한다. 적용하지 않으면 Java 라벨이 나온다. PROVENANCE.md의 해시 표도 함께 바꾼다.
5. `src/player_ui.rs`: 코드 하이라이트 언어. 환경 설치/진단 화면에서 `prepare`/`inspect`.
6. `src/lib.rs`: `pub mod native_trace;` 한 줄(이 브랜치에 있음, JS 작업자 줄과 merge 시 정리).

## 문서 계약 (TraceView, C 추적과 같은 꼴)

- 스택 지역 변수: 정수(2^53 넘으면 `["LONG", "..."]`), 실수(`["SPECIAL_FLOAT", "nan"|"inf"|long double 원문]`), bool, `["CHAR", c]`(C++ char류, Rust `char`). Rust `u8`/`i8`은 숫자다.
- `["C_PTR", "이름"]`: 이름 있는 스택·전역 칸을 가리키는 포인터·참조. 칸 이름표는 (주소, canonical 자료형)이다. 그래서 `&pair.first`는 `pair`가 아니라 `pair.first`가 된다.
- `["REF", id]` → `heap[id]`: 구조체·배열·벡터는 `INSTANCE`/`ARRAY`. 객체 identity는 (주소, canonical 자료형). 컨테이너 버퍼는 (버퍼 주소, 자료형). C++ 동적 할당 보기는 (serial, offset, 자료형). Rust `String`의 힙 버퍼는 `["STRING", text]`이다. 그래서 clone은 새 상자, move는 같은 상자로 그려진다. C++ `std::string`은 SSO가 있어 인라인 문자열이다.
- Rust enum(Option/Result/사용자 enum): `["INSTANCE", "Option<i32>::Some", ["0", 값]]`. 필드 없는 variant는 필드 없는 INSTANCE다.
- `["C_NOTE", 글]`: 관측하지 않거나 따라가지 않는 값.
  - `옮겨진 값(move) · 이 이름으로는 더 쓸 수 없어요`: Rust move. 부분 move는 구조체의 해당 필드만 이렇게 그린다.
  - `0x… · 해제된 동적 메모리`: C++ delete/free 뒤의 포인터.
  - `0x… · 대상 범위를 몰라 따라가지 않아요`: C++의 모르는 주소.
- 프레임: `func_name`, `frame_id`(재귀·같은 줄 재호출도 서로 다른 id), `declared_without_initializer`(C++ 초기값 없는 지역 변수), 가려진 Rust 바인딩은 `x · 가려짐(27행)`.
- `verification`: `original_source`(src와 컴파일한 사본이 바이트 단위로 같음), `compile_command`, `native_debugger: "LLDB"`, `program_runs: 1`, `ownership`(Rust: 같은 rustc의 MIR).

## Rust move 근거와 한계

- LLDB/DWARF에는 move 정보가 없다. move된 바인딩의 스택 비트가 그대로 읽힌다(관찰: `let moved = first;` 뒤에도 LLDB가 `first="pen"`).
- 같은 rustc가 `RUSTC_BOOTSTRAP=1 -Zmir-include-spans=yes -Zdump-mir=built`로 만든 built MIR에서 move/재대입 사건을 읽는다. 그 컴파일의 final MIR이 실행 파일을 만든 stable 빌드의 final MIR과 주석을 빼고 같을 때만 쓴다. 다르면 `status: unsupported`로 흐름을 그리지 않는다. stable final MIR은 마지막 사용의 `move`를 `copy`로 바꾸므로 쓰지 않는다.
- 사건은 줄 단위로 적용한다. 프레임이 그 줄을 끝내고 다른 줄에서 멈출 때 적용하고, 호출 중인 caller는 그 호출의 인자 move까지만 적용한다. 같은 줄의 분기 양쪽에서 move하면 둘 다 move로 그린다. borrow checker 기준으로 둘 다 더는 쓸 수 없어서다. 멈춤이 없는 줄에서 move 뒤에 재대입하면 move로 남는다. 틀린 값을 보이지 않는 보수적 실패다.
- borrow 상태(누가 빌렸는지)는 그리지 않는다. 참조는 대상 칸을 가리키는 `C_PTR`/`REF`다.
- unsafe/raw pointer, 스레드, async는 지원 범위 밖이다(스레드는 `unsupported`).

## 실행 제한과 정리

- 단계 1000, 디버거 멈춤 20000, 사용자 프레임 깊이 64, 자식 64개. 추적 150초, 실행 40초.
- Windows 컨테이너: `--network none --cap-drop ALL --security-opt no-new-privileges --memory 512m --pids-limit 128 --cpus 2`, 기본 seccomp. 마운트는 이 시도의 임시 tool(ro)/case 폴더뿐. 이름 `mq-native-<id>`와 라벨 `mq.owner=mq-native-trace`. 시간 초과 때는 그 이름의 컨테이너만 `docker rm -f`한다. 이미지 태그는 Dockerfile 내용 해시다.
- macOS: LLDB 프로세스 그룹을 시간 초과 때 SIGKILL한다.
- Docker Desktop이 꺼져 있으면 `run`/`trace`가 docker 오류를 그대로 돌려준다. 엔진 자동 시작은 root가 `docker_lab`의 시작 흐름을 재사용해 붙인다.
