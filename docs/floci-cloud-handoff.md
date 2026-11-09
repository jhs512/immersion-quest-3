# Floci 클라우드 수업 작업 인수인계

2026-11-10. 사용자가 현재까지의 작업을 커밋하고 인수인계 문서를 남기도록 요청해 제작 프로세스를 종료했다. 이 체크포인트는 **실행기 구현 + 승인된 설계**이며, 수업 제작 완료나 배포 완료가 아니다.

## 작업 위치와 범위

- 브랜치: `feat/floci-cloud-first-lesson-20261109`
- 작업 폴더: `C:/Users/jangk/Documents/Codex/2026-10-12/immersion-quest-cloud-first-lesson-20261109`
- 기준 커밋: `0d551472b3036ae6a0920e563d3ec5970f33ef8c`
- 다른 변경이 많은 원래 `immersion-quest-3` 작업 폴더의 코드·설정은 수정하지 않았다. 그 폴더의 승인된 로컬 정책은 아래 스냅샷으로 복사했다.
- 설치된 MQ 앱 변경·재시작, 원격 게시·배포·push는 하지 않았다. 실제 AWS 계정·인증·리소스도 사용하지 않았다.

## 사용자 결정과 승인

기존 **자바 과정의 후속**이다. 네트워크·DB·JDBC·Docker·Compose 등 기존 수업 지식은 알고 있다고 전제하고 다시 묻지 않는다. 첫 수업은 VPC·서브넷·EC2의 자원 관계와 서버 배치다. 이후 수명주기, S3로 이어간다. 이후 서비스 순서는 제안 단계이며 SQS·Lambda·DB를 이번 첫 수업에 추가하지 않는다.

사용자는 구체적인 예고·PRD·대표 문제를 확인한 뒤 2026-11-09 “고고”로 다음 제작 단계를 승인했고, 2026-11-10 작업 재개를 요청했다. 생성될 정식 JSON이나 모든 문장을 사용자가 직접 검수했다고 기록하면 안 된다.

- [승인된 설계 PRD 초안](../.scratch/floci-course-wayfinder/first-lesson/prd.draft.md)
- [예고 초안](../.scratch/floci-course-wayfinder/first-lesson/lesson-preview.draft.json)
- [대표 문제](../.scratch/floci-course-wayfinder/first-lesson/representative-problem.draft.md)
- [진행 지도와 티켓](../.scratch/floci-course-wayfinder/map.md)
- [적용 정책 원문·해시](../.scratch/floci-course-wayfinder/policy-snapshot/index.json)

정책 스냅샷에는 최신 로컬 `content-rules.md`, `voice.md`, `source-of-truth.md` 원문과 Java 과정 목표·흐름 참고 자료가 있다. 전역 정책 파일을 이 브랜치의 오래된 버전으로 덮어쓰지 않는다. `tools/lesson_prd.py`는 원문을 PRD의 policy artifacts에 내장할 수 있다.

## 완료된 구현과 검증

1. **Floci 자체 사전 점검**: Windows에서 서브넷 계약 19/19, 실제 Java EC2 게스트 15/15. 최종 두 부분 모두 호스트 자원 전후 동일. Codex도 실행 중 EC2 API를 새로 조회하고 다른 서브넷에서 Java HTTP 응답을 직접 확인했다.
2. **MQ 네이티브 실행기**: `src/cloud_practice.rs`와 테스트, `assets/cloud-lab/`. `CloudExercise`의 `create_subnet`, `choose_subnet`, `launch_server`, `request_server`, `deploy_server`를 구현했다. 실제 `GitPractice` 준비·재접속·제출·초기화·해설 분리에 연결했다. 일반 Docker 이미지 허용 목록은 넓히지 않았다.
3. **이전 검증 결과**: Windows 단위 10개 통과, 실제 Docker 경로 8개 통과. 처음 두 환경/인벤토리 실패와 재실행 기록을 보존했다. 전체 네트워크 inspect(IPAM·옵션 포함)를 비교했고, 마지막 독립 조회에서 소유 컨테이너·네트워크·볼륨은 0개였다.
4. **독립 검토 수정**: AWS CLI의 축약 옵션 주소 우회를 loopback만으로 재현·수정했고 실제 CLI 8개 경우를 별도로 확인했다. 설정 파일·주소 파일 보호, 이미지 아키텍처, 제한된 save/load 전송과 프로세스 회수도 반영했다.

상세와 재현 명령:

- [사전 점검 기록](floci-first-lesson-preflight.md)
- [네이티브 연결·콘텐츠 작성 계약](floci-cloud-native-runtime.md)
- [독립 검토 기록](../.scratch/floci-course-wayfinder/native-review.md)

원자료는 이 컴퓨터의 `target/floci-preflight/`, `target/cloud-native-evidence/`에 있다. 큰 로그·이미지·임시 소스는 커밋하지 않았다. 같은 코드를 다시 실행할 도구는 커밋에 포함된다. 기존 S3/Lambda·DB 연구의 위치와 한계는 지도·티켓 07/08과 `service-teaching-plan.md`에 있다.

## 마지막 확인에서 남은 문제 — 먼저 확인할 것

사용자의 체크포인트 요청 뒤 PowerShell에서 다음을 실행했다.

```powershell
cargo test --lib cloud_practice -- --test-threads=1
```

**9 통과 / 1 실패 / 8 ignored**였다. 실패는 `aws_wrapper_guards_endpoint_profile_and_environment`, `src/cloud_practice_tests.rs:166`의 첫 대역 CLI 실행 성공 검사다. 단언문이 stderr를 버려 원인은 아직 확인되지 않았다. 이전 Claude/Git Bash 문맥에서는 10개가 통과했으므로 현재 체크포인트를 모두 녹색이라고 보고하면 안 된다. 재개 시 stderr와 셸/PATH 차이를 먼저 확인한다. 원래 계정 정보나 실제 키를 출력하지 않는다.

[체크포인트 검증 기록](../.scratch/floci-course-wayfinder/checkpoint-validation.json)에 결과를 남겼다. `git diff --check`는 통과했다. 제작 프로세스의 마지막 작은 변경은 `client-request` 인자의 CRLF/공백 제거이며, 이 부분은 별도 실제 호출 검증을 하지 않았다. 현재 변경을 보존했으며 과거 통과 결과와 구분한다.

기존 별도 문제: `lesson_registry` 기대값은 102인데 이 브랜치의 기존 수업은 이미 110개다. 새 수업 등록 시 111개가 되므로 관련 기대값·등록 검사를 함께 고친다. `kpc_learning`/`narration_replay`는 생성 파일 `courses/kpc-solutions.json`을 먼저 준비해야 컴파일된다.

## 아직 하지 않은 수업 제작

`tools/redesigned_lessons/cloud_vpc_subnet_ec2/`는 **아직 생성되지 않았다.** 정식 예고·approved PRD·본문·해설 캐시·카탈로그 등록·컴파일된 수업·수업별 실제 정답 실행 검증은 남아 있다. 임의 생성한 자원 코드는 등록 전이며, 추출된 경우 `first-lesson/reserved-resource-ids.json`에만 있다.

읽기 전용 VPC 도입은 본문/전제로 배치해 가짜 채점 문제를 만들지 않는다. 승인된 7개 실습은 아래와 같다.

| 순서 | 행동 | 실행기 목표 |
|---|---|---|
| 1 | 준비된 정상 서브넷 명령을 실제 실행 | `create_subnet` |
| 2 | VPC 밖 CIDR 한 곳을 안으로 수정 | `create_subnet` |
| 3 | 준비 서브넷을 보존하고 겹치지 않는 /25 선택 | `choose_subnet` |
| 4 | 준비된 정상 서버 배치 명령 실행 | `launch_server` |
| 5 | 잘못된 A 배치를 관찰·다시 시작 후 B로 수정 | `launch_server` |
| 6 | 주소 파일을 API가 알려 준 사설 IP로 수정 | `request_server` |
| 7 | 새 서브넷 + Java 서버 배치 + HTTP를 조합 | `deploy_server` |

1·4는 초기 자원 상태가 실패하고 정상 명령을 실행하면 통과하는 실행 과제다. 정상 명령 자체가 실패했다고 보고하지 않는다. 오류 수정 과제는 준비 명령으로 실패·정답으로 성공을 실제 확인한다. API `running`과 HTTP 준비는 다르다. 최종 과제에서 B는 처음에 없으므로 미리 존재하는 `LAB_SUBNET_B_ID`를 가정하지 않는다. ID·실제 주소를 하드코딩하지 않는다.

## 재개 순서

1. 위 체크포인트 단위 검사 실패를 짧게 재현·진단한다. 완료된 Floci 실험 전체를 다시 돌리지 않는다.
2. 승인된 설계를 7개 실습의 예고·PRD·본문으로 작성한다. 단계별 목표·작은 수정·실행·관찰·해요체·실제 해설 동작을 지킨다.
3. Java 과정의 기존 목표·수업·진도 코드를 보존하며 새 수업만 등록한다. 이 브랜치에는 `core_flow`가 없고 정책 스냅샷의 Java 참고 자료에는 있으므로 관련 흐름만 검토해 적용한다. 기존 예고 본문은 그대로 두고 필요한 intent 메타데이터만 갱신한다.
4. 빌드된 공개 수업의 실제 `GitExercise`와 원본 정답을 ID로 연결해 7개를 네이티브로 실행·채점한다. 해설은 새 미션만 생성/갱신하고 기존 빌더·재생 검사를 수행한다.
5. 기존 본문·PRD 보존은 로컬 `target/cloud-authoring-baseline/` 해시 목록과 비교할 수 있다. 기록은 119개 기존 소스 폴더를 대상으로 했으며 등록된 수업 개수와 다른 수치다.

기본 명령(구체적인 콘텐츠 생성 뒤 문서의 도구 도움말에 맞춰 실행):

```powershell
cargo test --lib cloud_practice -- --test-threads=1
cargo check --bins --lib
python tools/build-redesigned-git.py --lesson cloud-vpc-subnet-ec2
python tools/narrate.py --redesigned-git --lesson cloud-vpc-subnet-ec2
python tools/build-redesigned-course-bundle.py --check
cargo test --test lesson_registry
```

기존 Docker 통합 검사는 `docs/floci-cloud-native-runtime.md`의 명령을 사용하되, 변경·실패가 관련된 검사만 직렬 실행한다. 원본 실패·스냅샷을 숨기거나 덮어쓰지 않는다. Mac·화면·실제 음성 재생·설치 앱 반영·배포는 수행하지 않은 수준을 명확히 구분한다.

## 작업 운영

MQ 저장소는 Claude Code 실행을 기본으로 하고 Codex가 검토한다. 별도 브리지는 앞선 사용자 요청으로 제거되어 직접 CLI를 사용했다. 기존 Claude CLI 대화는 `4d26ee33-b883-4489-8f76-dec764dcb350`이지만, 저장된 대화 없이도 이 문서와 승인 설계·소스·정책 스냅샷으로 재개할 수 있어야 한다. 이 체크포인트 시점의 제작 프로세스는 종료했으므로 중복 실행하지 않는다.

공식 고정 Floci·Java 이미지의 amd64/arm64 manifest는 확인했지만 Mac 실제 실행은 미검증이다. DIND·게스트 권한은 로컬 신뢰 실습 수준이며 다중 사용자 보안 샌드박스라고 부르지 않는다. 사용자 인증·원본 프로젝트·다른 Docker 자원·설치된 앱은 보존한다.
