# 정보처리기사 실기 바텀업 보강

사용자는 분류1·2에 해당하는 지식을 MQ3의 기존 실기 과정에 통합하고, 중단된 제작과 실패한 검사를 Codex가 직접 마무리하도록 지시했다. 기출 원문을 옮기는 대신 원리를 확인하는 독자 예제를 추가했다.

## 반영 범위

- 분류1 222문항·분류2 163문항의 요구 능력을 183개 개념으로 연결했다. 이 숫자는 분석 자료의 대응 범위이며 공식 출제 비율이나 합격 보장이 아니다.
- 기존 30수업·335스텝 사이에 32수업·329스텝을 추가했다. 통합 과정은 62수업·664스텝이다.
- 새 실습은 C 78개, Java 55개, Python 147개, SQL 49개다. 모두 코드를 직접 고치고 실행해 채점한다.
- 기존 수업·문제 식별자와 학습 기록을 보존한다. 게시할 때도 원격의 최신 기존 수업을 로컬의 오래된 버전으로 덮어쓰지 않는다.
- 요구사항, 설계, 서버·인터페이스, 테스트, 보안, 운영체제, 네트워크, 빌드·복구는 작은 실행 모델로 원리를 확인한다. 교육용 XOR·JWT 검증 상태·배포 모델을 실제 보안이나 운영 시스템 전체의 구현이라고 설명하지 않는다.
- 분석 대상 기출의 문제·정답·이미지를 배포물에 넣지 않았다. 대응표에는 문항 식별자와 분류, 독자적으로 정리한 원리, 수업·스텝 식별자만 있다.

## 수정한 검사와 원인

| 발견 | 수정과 확인 |
|---|---|
| Python 준비 값을 JSON에 저장하면 정수 사전 키와 튜플·바이트의 형식이 바뀜 | 안전한 리터럴 메타데이터를 보존한다. 실행식은 거절하고 기존 출력 검사와 호환되는지 확인했다. |
| 일부 해설 검사에 실행 결과 배열이 덜 채워져 중단됨 | 실제 실행에서 결과를 추출하고 해설 문장과 대조했다. 기대값 비교를 삭제하지 않았다. |
| 정렬된 DB 범위 조회의 블록 수가 잘못 계산됨 | 300~500 구간을 두 행씩 담으면 세 블록이라는 기대값으로 수정했다. |
| 재고 변형 자료에서 ‘유효 주문’ 입력이 0이 됨 | 최소 유효 수량 1을 보존하도록 예제를 수정했다. |
| 같은 코드가 두 곳에 있어 강조 대상을 구분하지 못함 | 해설에서 정확한 코드 발생 위치를 지정했다. |
| ALL·ANY를 MAX·MIN으로 옮기는 설명이 빈 목록·NULL에도 일반적으로 성립하는 것처럼 읽힘 | 현재 자료가 비어 있지 않고 가격에 NULL이 없다는 조건을 명시했다. 빈 목록은 뒤 스텝에서 따로 비교한다. |
| 이름 저장이 필요한 현재 앱에서 검사 도구가 학습 시작을 기다리기만 함 | 검증용 격리 코스에 이름을 입력·저장한 뒤 수업을 여는 실제 절차를 검사 도구에 반영했다. |
| Python 내부 변형 여러 개가 공개 채점 결과 한 건으로 보고됨 | 공개 결과 수 대신 실제 준비 자료의 변형 수와 실행 증거를 함께 검사한다. |

## 검증

실제 동작을 확인하는 **Prove It Works** 원칙에 따라 컴파일이나 제작자의 완료 보고로 대체하지 않았다. 애플리케이션의 실제 채점기로 새 329스텝의 준비 코드 실패, 정답 통과, 준비 자료 변형, 오답 446건 거절, 동등 정답 180건 수용, 해설 실행 836회를 검증했다. 각 결과의 수업 SHA-256을 실제 통합 목록과 대조했다.

원격 코스는 **Separate Before Serializing Shared State** 원칙에 따라 새 수업을 독립 저장소에 먼저 게시하고, 마지막에 현재 원격 코스에 새 참조만 합친다. 원격 파일의 SHA를 조건으로 갱신하며 기존 수업과 다른 작업자의 변경을 보존한다. 충돌 거절·반복 실행·기존 내용 보존 검사를 포함한다.

레지스트리 112수업·1,125스텝의 실제 격리 전송 경로와 통합 스냅샷 생성, 잘못된 해시 거절, 기존 과정·저장 목록 보존 검사도 통과했다. 세 과정 전체를 새로 설계한 것은 아니며, 기존 선택형을 이번에 모두 없앴다는 뜻도 아니다.

Windows 실제 앱 검사 결과와 게시 확인은 함께 저장한 `engineer-bottom-up-2026-11-03-evidence.json`을 따른다. 자동 UI 검사에서는 음성을 끄므로 음성을 직접 듣고 검수했다고 주장하지 않는다. 이번 완료 검증은 Codex가 수행했으며 독립 심사 결과로 표시하지 않는다.

## 재검증

```text
python -X utf8 tools/build-redesigned-course-bundle.py --check
python -X utf8 tools/test_lesson_prd.py
python -X utf8 tools/test_lesson_registry.py
python -X utf8 tools/test_python_prepared_checks.py
python -X utf8 tools/test_publish_engineer_bottom_up.py
cargo test --locked --target-dir target/cert-test --test lesson_registry
cargo test --locked --target-dir target/cert-test --lib redesigned_defaults_open_complete_independent_snapshots_and_preserve_added_courses
cargo build --locked --target-dir target/cert-test --example validate_redesigned_lesson
python -X utf8 tools/verify_engineer_bottom_up.py --execute
```

`--execute`는 실제 채점기로 결과를 다시 만든다. `--structural-only`는 원본·파생물·식별자·대응표 검사만 수행하므로 실행 검증 완료로 보고하지 않는다. `tools/publish_engineer_bottom_up.py`의 기본 동작은 게시 전 검사이며, `--publish`가 검증된 새 수업과 통합 코스를 게시한다.
