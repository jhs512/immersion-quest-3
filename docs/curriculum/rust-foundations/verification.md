# Rust 기초 네 수업 검증 기록

검증일: 2026-11-02. 환경: Windows 11 `10.0.26300`, `rustc 1.95.0 (59807616e 2026-04-14)`, 호스트 `x86_64-pc-windows-msvc`. macOS는 실행하지 않았다.

## 정식 수업 40스텝

```powershell
python docs/curriculum/rust-foundations/validate_rust_lessons.py --evidence
```

스텝마다 별도 임시 폴더에서 `rustc --edition=2024`로 컴파일·실행했다. 외부 크레이트와 네트워크는 쓰지 않았다. 확인한 것:

1. 준비 코드는 채점에서 실패한다(컴파일 실패 또는 다른 출력).
2. 정답은 경고 없이 컴파일되고, 테스트와 준비 값 바꾸기를 모두 통과한다.
3. 정답 코드 줄 세 개마다 주석이 하나 이상이다.
4. 해설을 처음부터 재생하면 각 실행의 출력이 기록과 같다. `expect_error` 실행은 그 진단 코드로 실패한다. 해설이 끝난 코드는 정답의 코드 줄과 같다.
5. 기록한 오답은 실패하고, 기록한 다른 정답은 통과한다. 오답은 스텝마다 하나 이상이다.

| 수업 | 스텝 | 오답·동등 정답 | 결과 | 증거 |
| --- | ---: | ---: | --- | --- |
| `rust-values` | 8 | 24 | 통과 | `evidence/rust-values-windows.json` |
| `rust-flow-functions` | 10 | 14 | 통과 | `evidence/rust-flow-functions-windows.json` |
| `rust-ownership-borrowing` | 10 | 19 | 통과 | `evidence/rust-ownership-borrowing-windows.json` |
| `rust-data-results` | 12 | 22 | 통과 | `evidence/rust-data-results-windows.json` |

## 빌드와 기록 검사

| 명령 | 결과 |
| --- | --- |
| `python tools/lesson_prd.py check <PRD> --require-approval` (네 수업) | 통과 |
| `python tools/build-redesigned-git.py --check` (전체 수업) | 통과 |
| `python tools/build-redesigned-course-bundle.py --check` | 통과. 자바 백엔드 48수업·478스텝 |
| `python tools/narration_review.py status` | 검토 안 된 문장 0 |
| `python tools/test_lesson_registry.py` | 통과(102수업) |
| `python tools/test_narration_review.py` | 통과 |
| `python tools/test_narration_openings.py` | 90건 실패. 이 작업 전 커밋 `83e96b45`에서도 같은 90건이 실패한다. 2026-10월의 고정 기준 커밋과 기존 수업을 비교하는 검사라 Rust 수업과 무관하다. Rust 수업은 기준 커밋에 없어 그 비교를 건너뛴다. |
| `python docs/curriculum/rust-foundations/verify_representatives.py` | 18건 통과(승인 때의 대표 문제 초안) |

## 런타임에 막힌 것

이 checkout의 `TaskLanguage`에는 `rust`가 없다. `cargo test --test backend_journeys --test bundled_courses --test lesson_registry --no-fail-fast`의 실제 결과:

| 테스트 | 결과 | 원인 |
| --- | --- | --- |
| `backend_journeys` (2건) | 통과 | 코스 48수업, 미리보기 48개, 모든 수업의 분류, 빈 주제 없음 |
| `bundled_courses` | 실패 | `unknown variant 'rust'` (수업 JSON 137줄의 `"language": "rust"`) |
| `lesson_registry` | 실패 | 같은 `unknown variant 'rust'` |

두 실패는 콘텐츠 오류가 아니라 엔진 미통합이다. 콘텐츠 자체의 판정은 위의 rustc 검증과 Python 빌더가 했다. 엔진 통합 뒤 실행할 검증은 [인계](handoff.md#통합-순서)에 있다.

## 확인하지 않은 범위

- macOS 컴파일·실행.
- 앱 안의 열기·제출·초기화·해설 재생, 음성과 강조의 동기.
- `cargo run --example validate_redesigned_lesson`(이 checkout에는 Rust 실행기가 없다).
- 코드 흐름 보기. Rust 스텝은 쓰지 않는다.

## 채점의 알려진 한계

채점은 출력과 준비 값 바꾸기만 본다. 출력이 같은 다른 풀이는 막지 못한다.

- R3 6번(대표 문제)의 `show(title.clone())`은 출력이 같아 통과한다. 해설이 불필요한 복사라고 짚는다. PRD 채점 항목에도 적었다.
- R4 3번은 준비 값 바꾸기가 없다. 목록 문자열을 직접 출력하는 답을 막지 못한다. 바로 다음 4번이 목록을 바꿔 같은 우회를 거절한다.
- R2 5번은 `1..=boxes` 같은 동등한 범위를 정답으로 받아들인다(기록한 동등 정답).
