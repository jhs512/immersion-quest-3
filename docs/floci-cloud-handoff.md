# Floci 클라우드 수업 작업 인수인계

2026-11-10 두 번째 세션(Claude Code). 체크포인트 `873fdc4b`에서 이어서 단위 검사 실패를 고쳤다. 승인된 첫 수업을 7개 실습으로 제작·등록했고, 공개 수업 JSON을 실제 Docker·Floci에서 네이티브 제출 경로로 실행해 검증했다. **배포·게시·설치 앱 반영은 하지 않았다.** 실제 AWS 계정·인증·과금 자원은 쓰지 않았다.

## 작업 위치와 범위

- 브랜치: `feat/floci-cloud-first-lesson-20261109`
- 작업 폴더: `C:/Users/jangk/Documents/Codex/2026-10-12/immersion-quest-cloud-first-lesson-20261109`
- 이전 체크포인트: `873fdc4b`(실행기 + 승인 설계, 단위 9 통과·1 실패·8 ignored)
- 원래 `immersion-quest-3` 작업 폴더의 코드·설정은 수정하지 않았다. 정책은 [스냅샷](../.scratch/floci-course-wayfinder/policy-snapshot/index.json)을 PRD에 내장해 적용했고, 이 브랜치의 전역 정책 파일은 바꾸지 않았다.

## 사용자 결정과 승인

기존 **자바 과정의 후속**이다. 네트워크·DB·JDBC·Docker·Compose 지식은 선수 지식으로 전제하고 다시 가르치지 않는다. 첫 수업 범위는 VPC·서브넷·EC2 배치다. 수명주기·S3·SQS·DB·Lambda는 넣지 않았다.

- 2026-11-09 사용자가 예고·PRD·대표 문제 초안을 확인하고 「고고」로 다음 제작 단계를 승인했다.
- 2026-11-10 사용자: 승인된 예고·PRD·대표 문제로 첫 수업을 완성하고, 방향 확인 없이 구현·검증까지 진행하라고 지시했다.
- 정식 PRD의 `approval.by`는 「Claude Code: 사용자 승인 초안에 따른 본편·해설 제작」이다. **생성된 JSON이나 개별 문장을 사용자가 검수했다고 기록하지 않았다.** 해설 의미 검토(`narration-review.json`)와 예고 정렬 검토(`preview-alignment.json`)도 작성자 자체 검토다.

## 이번 세션에 완료하고 검증한 것

### 1. 단위 검사 실패 원인과 수정

- 원인: PowerShell에서 실행하면 Git Bash가 `--noprofile`로 떠서 `/usr/bin`이 PATH 앞에 없다. 래퍼와 테스트 대역의 `#!/usr/bin/env bash`가 상속 PATH의 `C:/Windows/System32/bash.exe`(WSL)를 골랐다. WSL은 `C:/...`를 상대 경로로 읽어 `No such file or directory`로 실패했다. stderr를 단언에 싣고 재현해 확인했다.
- 수정: `aws`·`client-request` 래퍼와 대역의 shebang을 `#!/bin/bash`로 바꿨다(`src/java_build_practice.rs`와 같은 관례). 실제 실습 터미널은 `docker_lab::search_path`가 Git의 `usr/bin`을 앞에 둬서 이미 Git bash를 골랐다. 이제 PATH 순서에 기대지 않는다.
- CRLF 변경: `client-request` 인자 정리를 앞뒤 공백·CR/LF 제거로 좁혔다(내부 공백은 거절). 새 단위 검사가 대역 docker로 허용·거절을 확인한다. 실제 6·7번의 Windows `--output text` 파일 경로도 네이티브 실행에서 200 응답을 받았다.
- 결과: `cargo test --lib cloud_practice -- --test-threads=1` **PowerShell·Git Bash 모두 12 통과 / 0 실패 / 10 ignored**(수정 직후 11/0/8, 편집 파일 검사·수업 검사 추가 뒤 12/0/10). 기록: [checkpoint-validation.json](../.scratch/floci-course-wayfinder/checkpoint-validation.json).

### 2. 실행기·플레이어 변경

- `CloudExercise.editable`(선택, 최대 4개): 편집기에 보여 줄 준비 파일 목록. 준비·해설 파일에 있어야 검증을 통과한다. Compose와 같은 `editable_files`/`save_editable` 경로를 쓴다. `git_terminal_ui`, `auto_review`, `player_ui` 라벨, 빌더의 강조 검사가 이 목록을 인식한다.
- 채점 피드백의 「다시 시작」을 실제 버튼 이름 「초기화」로 고쳤다(`src/cloud_practice.rs`).
- 클라우드 실습 준비가 Docker 수업과 같이 `docker_lab::ensure_engine`으로 꺼진 로컬 Docker Desktop을 한 번 켜고 엔진을 최대 120초 기다린다(2026-11-10 앱 검증 중 발견: 전에는 「Docker 엔진에 연결하지 못했어요」로 멈췄다).
- 문서: [네이티브 연결·콘텐츠 계약](floci-cloud-native-runtime.md)에 `editable`을 추가했다.

### 3. 첫 수업 `cloud-vpc-subnet-ec2` 제작·등록

소스: `tools/redesigned_lessons/cloud_vpc_subnet_ec2/`(content·approved-prd(.md)·lesson-preview·preview-alignment·narration_cache). 생성 도구: [author_lesson.py](../.scratch/floci-course-wayfinder/first-lesson/author_lesson.py), 등록: [register_lesson.py](../.scratch/floci-course-wayfinder/first-lesson/register_lesson.py). 예약 ID를 그대로 썼다.

| 순서 | 스텝 | goal | 학생이 바꾸는 곳 |
|---|---|---|---|
| 1 | 준비된 명령으로 VPC 안에 서브넷을 만드세요 | `create_subnet` | 없음(실행 과제). VPC 조회는 이 스텝의 첫 관찰과 단원 전제 |
| 2 | 범위 밖 서브넷을 VPC 안으로 고치세요(대표) | `create_subnet` | `--cidr-block` 10.92→10.91 |
| 3 | 준비된 서브넷과 겹치지 않는 범위를 고르세요 | `choose_subnet` | 겹치지 않는 /25 하나 |
| 4 | 지정한 서브넷에서 서버 한 대를 실행하세요 | `launch_server` | 없음(실행 과제) |
| 5 | 엉뚱한 서브넷에 놓이는 명령을 고치세요 | `launch_server` | 관찰 → 「초기화」 → A→B 변수 |
| 6 | 다른 서브넷의 서버에 사설 주소로 요청하세요 | `request_server` | `server-address.txt` |
| 7 | 자바 서버를 10.91.2.0/24에 배치하세요 | `deploy_server` | CIDR·`subnet-id.sh` 범위·주소(세 곳) |

- 7번은 새 서브넷의 ID 변수가 없으므로 `launch-server.sh`가 `subnet-id.sh <CIDR>`로 ID를 찾는다. 해설의 `patch_code`가 정적 값만 고칠 수 있기 때문이기도 하다. `LAB_SUBNET_B_ID`를 가정하지 않고 ID·주소를 하드코딩하지 않는다.
- 해설은 동적 주소만 `aws ... --output text > server-address.txt`로 옮겨 적고 그 사실을 말한다. 5번 해설은 시연 화면에 초기화가 없어 처음 명령을 말로 짚고 바로 고친다. 그래야 해설 재생(자동 풀이와 같은 경로)이 시작 상태에서 통과 상태에 이른다.
- 라우팅·NACL·NAT·피어링·보안 그룹을 가르치지 않고, 예고 제약에 「다루지 않아요」로 적었다.
- 등록: Java 카탈로그(선택 수업, `cloud-vpc-subnet-ec2-1`, 검증 코스 `클`), `backend-sequence` 흐름(docker-compose-db 다음, 선수 6개, `cloud_rationale`), 마지막 문제 지정, 분류(사용자 결정으로 새 「클라우드」 분류), release 변경 기록, 해설 도입문, 의미 검토 기록.
- 기존 수업·목표·진도 보존: 기존 수업의 ID·revision·순서·본문은 바뀌지 않았다. 과정 흐름이 바뀌어 네트워크 8개 예고의 `course_intent_sha256`과 정렬 해시만 다시 찍었다(`intent_restamped` 메모). 다시 찍기 전에 기존 해시가 맞았는지 먼저 확인했다. `build-redesigned-git.py --check`가 전체 수업에서 통과한다.
- `network-`만 보던 정식 예고 경로를 `CANONICAL_PREVIEW_PREFIXES = ('network-', 'cloud-')`로 넓혔다.

### 4. 실제 수업 데이터의 네이티브 실행(Windows, Docker Desktop 29.8.1, AWS CLI v2)

`src/cloud_practice_tests.rs`의 두 ignored 검사가 **빌드된 `courses/redesigned/cloud-vpc-subnet-ec2.json`**의 `git_terminal`과 해설을 읽는다. 해설의 `patch_code`·`bash_command`를 학생 폴더에서 재생하고, 채점은 모두 `check_exercise()`(앱의 제출 분기)로 한다.

| 검사 | 결과 | 확인한 것 |
|---|---|---|
| `docker_cloud_lesson_subnet_steps` | **통과**(117초, 호스트 인벤토리 전후 동일) | 1: 초기 실패→준비 명령 통과. 2: 초기·준비 명령(InvalidSubnet.Range)·출력 위조 실패, **해설 레인**이 별도 자원에서 통과하고 학생 상태·파일 불변, 학생 수정 통과, VPC 10.73 변형에서 기본 답 거절·변형 답 통과. 3: 겹침(InvalidSubnet.Conflict) 거절, /24 실패, 해설 /25 통과, 다른 빈 /25 통과 |
| `docker_cloud_lesson_server_steps` | **통과**(314초, 동일) | 4: 초기 실패→준비 명령 통과(10.91.2.10 running). 5: 준비 명령 A 배치 실패, A를 남긴 채 B 추가 「서버가 2대」 실패, **초기화**가 이전 런타임 제거·준비 파일 복원·초기 실패, 해설 통과. 6: 자리표시·출력 위조 실패, 해설 통과(채점기 HTTP: from 10.91.1.10, served-on 10.91.2.10, java 25.0.5). 7: 서버를 A에 두면 실패, 초기화 뒤 해설 통과(running 뒤 Connection refused 2회 → 200) |

- 원자료: `target/cloud-native-evidence/lesson-run-1-*.log`, 명령별 `lesson-<스텝>-<lane>-<n>.txt`. 같은 내용을 [evidence/native](../.scratch/floci-course-wayfinder/evidence/native/)에 커밋했다.
- 실행 뒤 바꾼 것은 해설의 말 문장뿐이다. 최종 수업의 명령·편집 순서가 실행한 순서와 같은지 대조했다(7개 스텝 모두 일치). 그래서 Docker 검사를 다시 돌리지 않았다.
- 해설 문장의 결과 설명은 위 실측 출력(오류 코드, pending→running, CONNECT_FAIL, 응답 필드)에 맞췄다.

### 5. 빌드·회귀 검사

| 명령 | 결과 |
|---|---|
| `python tools/build-redesigned-git.py --check`(전체) | 통과 |
| `python tools/build-redesigned-course-bundle.py --check` | 통과(java 57 / 525 스텝, aice 24, engineer 30) |
| `python tools/narration_review.py status` | uncovered 0 |
| `python tools/build-kpc-course.py` | 통과 |
| `cargo check --bins --lib` | 통과(기존 경고만) |
| `cargo test --lib` | `course_authoring_tests`의 Java 수업 수 56→57 갱신 뒤 통과 |
| `cargo test --test lesson_registry` | 통과. 기대값을 실제 111개 / 1118 스텝으로 고쳤다(이전 102/1071은 네트워크 8개 추가 전부터 낡은 값) |
| `bundled_courses`·`backend_journeys`·`challenges`·`network_foundations` | 통과(Java 수업 수 57) |
| `cargo test --tests --no-fail-fast` | 125개 묶음: 400 통과 / **1 실패** / 177 ignored. 실패는 기존 `redesigned_java_values`였고 뒤에 고쳐 통과한다(아래 6) |

## 작업 폴더 증거의 저장소 사본

이 작업 폴더의 `target/`(git 제외)에만 있던 실행 증거를 `.scratch/floci-course-wayfinder/evidence/`에 복사해 커밋했다(230개, 약 4.7 MB).

- `evidence/preflight/`: `target/floci-preflight/`의 사전 점검 실행 5회와 `preflight-index.json`. 내려받은 Floci 원본 소스(`_source/`, 약 130 MB, 외부 프로젝트 코드)는 넣지 않았다. 같은 커밋(`9be236e`)을 Floci 저장소에서 다시 받을 수 있다.
- `evidence/native/`: `target/cloud-native-evidence/`의 네이티브 검사 로그·호스트 인벤토리(before/after)·수업 실행 명령별 출력.
- 커밋 전 검사: 들어 있는 자격 값은 실습용 `test` 더미뿐이다. 실제 키 형식(AKIA·ASIA·ghp_ 등)은 없었다. 인벤토리는 컨테이너 Config·Env를 담지 않는다.
- 앞으로 실행한 증거는 다시 `target/`에 쌓인다. 남길 실행만 이 폴더에 복사한다.

### 6. 실제 앱(개발 빌드)에서의 확인

`tests/player_cloud_native.rs`가 디버그 플레이어를 파일럿 모드(검증 코스 `클`)로 띄우고 `tools/player-pilot-code-lesson.js`의 클라우드 분기를 실행한다. 설치 앱은 쓰지 않았다.

- 결과: **7개 스텝 모두 통과**(1034초), 수업 완료 이벤트 1개, 통과 문제 7개. 기록: [evidence/native/pilot-run-2.log](../.scratch/floci-course-wayfinder/evidence/native/pilot-run-2.log), [결과 JSON](../.scratch/floci-course-wayfinder/evidence/native/pilot-cloud-vpc-subnet-ec2-result.json).
- 스텝마다 확인: 편집기 탭이 `editable`과 같고 준비 파일을 보여 줌 → 시작 상태 제출 거절 → 해설의 편집·명령을 **학생 편집기와 터미널**에서 실행해 통과 → **해설 재생**(별도 런타임)이 모든 명령을 끝내고 학생 파일·상태를 바꾸지 않음 → 「초기화」가 새 런타임과 원래 파일을 주고 다시 거절.
- 첫 시도(`pilot-run-1.log`)는 Docker Desktop이 꺼져 있어 클라우드 준비가 엔진 연결에서 멈췄다. 이를 고쳐(위 2) 두 번째 실행은 Docker Desktop이 꺼진 상태에서 시작해 앱이 켰다.
- 실행 뒤 `gg.molip.cloud-practice` 라벨 컨테이너는 0개였다.
- 이번 변경 뒤 다시 실행: `cargo test --lib` 142 통과, lesson_registry·bundled_courses·backend_journeys·challenges·network_foundations·redesigned_java_values 통과, `test_narration_openings.py` OK, `build-redesigned-git.py --check` 전체 통과.

### 7. AWS CLI 컨테이너 실행과 해설 대기 버그 (2026-11-10, 사용자 결정 「추천대로」)

- 학생 컴퓨터에 AWS CLI를 설치하지 않는다. 학생의 `aws`와 채점기가 고정 공식 이미지 `public.ecr.aws/aws-cli/aws-cli:2.39.7@sha256:73f81e…`(amd64·arm64)를 실습 네트워크에서 실행한다(`82a156e0`). 수업 JSON은 바이트까지 같아 게시된 수업 태그가 그대로 유효하다. Windows 실제 실행: 서브넷 133초, 서버 333초 통과. aws 호출 하나가 약 0.7초→1.2초로 늘었다.
- **앱 버그(고침)**: 「해설 재생」이 해설 화면 준비를 45초까지만 기다리고 「해설 시연을 준비하지 못했어요」로 끝냈다(`src/player_ui.rs`). 서버 문제의 해설용 클라우드 준비는 45초를 넘을 수 있다(6번 실측 45.5~45.7초, 맥은 더 길다). 클라우드 실습만 15분으로 늘렸고 다른 수업은 45초 그대로다.
- **안내 추가**: 클라우드 실습 준비 중 학생·해설 화면에 준비 안내를 띄운다(`src/git_terminal_ui.rs`).
- 파일럿 보강: 해설 시작 15분 대기, `MOLIP_PILOT_FROM`(특정 스텝부터 시작), 앱 로그 보존(`target/pilot-<수업>-app.log`).
- 결과: 앱 파일럿 실패 2회(`pilot-run-3/4`, 6번 해설 시작) → 원인 재현(`pilot-run-5-from6`, 해설 터미널이 ready 전에 닫힘) → 수정 뒤 6번부터 통과(`pilot-run-6-from6`) → **전체 7/7 통과**(`pilot-run-7`, 1110초, 남은 라벨 자원 0). 해설 옆 학생 환경 재현 검사 `docker_cloud_lesson_request_demo_beside_student` 통과(학생 46.6초, 해설 46.5초).

## 실패·미검증으로 남은 것

- **고침(기존 실패)**: `tools/test_narration_openings.py`가 91개 수업에서 실패했다. 도입문을 넣기 전 고정 커밋 `8520082b`의 수업과 그대로 같아야 한다고 비교했는데, 그 뒤 정상적으로 바뀐 수업이 많았다. 이제 현재 원본(`content.json`)과 비교해 해설 말 이외의 필드·채점·동작이 그대로인지 확인한다. 전체 스텝 수도 1118로 고쳤다. 정답 필드나 명령 하나를 바꾸면 실패하는 것을 확인했다.
- **고침(기존 실패)**: `tests/redesigned_java_values.rs`. 커밋 `1f22299d`가 java-values 마지막 문제를 우유·빵 합계로 바꿨는데 검사는 아직 `(quantity + added)`를 치환했다. 이제 `(milk + bread)`를 치환하고, 치환이 실제로 일어났는지도 확인한다. 통과.
- **미검증**: 실제 음성 재생과 음성·강조의 동기화는 듣지 않았다(파일럿은 음성을 끈다).
- **맥**: Docker 서브넷·서버 검사는 통과, 앱 파일럿은 미검증(아래 「맥 검증」). **미검증**: 오프라인 준비(게스트 부팅 중 `apk` 설치에 인터넷 필요), 다중 사용자 격리.
- **분류**: 2026-11-10 사용자 결정 「클라우드 새로 만들고」로 자바 과정에 「클라우드」 분류를 새로 만들고 이 수업을 옮겼다. 다른 수업의 분류는 그대로다.
- **배포 안 함**: 수업 저장소 게시·과정 매니페스트 배포·설치 앱 반영·push 외 원격 작업은 하지 않았다. 게시하려면 기존 게시 절차(`tools/publish-*.py` 계열)를 별도로 검토해야 한다.

## 맥 검증 (2026-11-10)

환경: macOS 26.5.1(25F80), Apple M4(arm64), Docker Desktop 4.87.0(엔진 29.7.2, linux/arm64, containerd 이미지 저장소), cargo/rustc 1.99.1. **AWS CLI 없음**, 설치하지 않았다. 실행 위치: worktree `~/.paseo/worktrees/30z2wfxb/feat-floci-cloud-first-lesson-20261109`.

### run-1 (커밋 `7c9aa89e`, 새 clone)

단위 13/0/10 통과. 두 Docker 검사는 호스트 AWS CLI가 없어 준비 단계에서 멈췄고(5초), 파일럿은 실행하지 않았다. 증거: [evidence/mac](../.scratch/floci-course-wayfinder/evidence/mac/).

### run-2 (커밋 `82a156e0` + 아래 맥 수정, 고정 AWS CLI 컨테이너)

| 검사 | 결과 |
|---|---|
| `cargo test --lib cloud_practice -- --test-threads=1` | 수정 전 **통과** 12/0/10(빌드 포함 233초). 수정 후 **통과** 13/0/10(13초, 추가 검사 1개) |
| `docker_cloud_lesson_subnet_steps` | 수정 전 **통과**(168.6초), 수정 후 다시 **통과**(176.3초) |
| `docker_cloud_lesson_server_steps` | 수정 전 **실패**(50초): RunInstances가 「arm64 이미지는 t3.micro와 맞지 않음」으로 거절. 수정 후 **통과**(391초, 게스트 Java 25.0.5가 다른 서브넷 요청에 응답) |
| `cargo test --test player_cloud_native` | **실패 2회**. 아래 참고. 앱 파일럿 7스텝 통과는 **미검증** |

**맥 수정(`src/cloud_practice.rs`)**: 게스트 기반 이미지(Temurin)를 호스트와 상관없이 `linux/amd64`로 받고 빌드한다(`GUEST_PLATFORM`, `image_platform`). Floci는 카탈로그 `architecture`로 게스트를 `--platform`과 함께 실행하고 x86_64 전용 `t3.micro`에 arm64 AMI를 거절한다. 라벨만 `x86_64`로 바꾸는 시도는 Floci가 arm64 이미지를 `linux/amd64`로 실행하려다 404로 실패해 되돌렸다(`diag-attempt-3/`). Apple Silicon에서는 게스트가 Docker Desktop의 x86_64 에뮬레이션으로 돈다(게스트 `uname -m` = `x86_64`). amd64 호스트(Windows)에서는 원래 기본 플랫폼이라 받는 이미지·빌드·카탈로그 값이 같다. 수업 내용(`t3.micro`)은 바꾸지 않았다. 단위 검사 `guest_base_is_x86_64_for_the_lessons_t3_micro_and_floci_is_native`를 더했다.

- 서버 검사 4번째 시도는 내부 엔진의 Temurin pull이 한 번 실패해 캐시 전송으로 넘어갔고, 호스트에 amd64 Temurin이 없어 실패했다. 같은 코드로 바로 다시 돌린 실행은 pull이 성공해 통과했다. pull 실패 원인은 확인하지 못했다(일시적 레지스트리 오류로 추정). Apple Silicon에서 캐시 전송 대체 경로는 호스트에 amd64 Temurin이 있어야 하고, 실행하지 않았다.
- 파일럿 1회(152초): 1번 스텝 학생 채점은 통과했고, 「해설 재생」 뒤 `cloud teacher begins` 60초 대기에서 실패했다. 해설 런타임이 준비 중에 남아 라벨 컨테이너·네트워크 1개씩을 정리했다.
- 파일럿 2회(5718초): 로컬에서 파일럿의 해설 시작 대기만 15분으로 늘려(커밋 안 함) 다시 돌렸다. 전체 제한 5700초에 걸려 결과 JSON 없이 끝났다. 마지막 활동은 12:13 KST의 서버 스텝 런타임이었고, 그 게스트는 x86_64에서 Java 서버가 8080으로 떠 있었다. 원인은 Windows 작업자가 찾은 앱 쪽 해설 준비 45초 제한으로 보인다(`1aa46ab5`에서 고침). 남은 라벨 자원(컨테이너 5·네트워크 5·볼륨 2)은 앱 종료를 확인한 뒤 정리했다.
- Docker 검사는 모두 호스트 인벤토리 전후가 같았다. 마지막에 `gg.molip.cloud-practice` 라벨 컨테이너·네트워크·볼륨·이미지 0개.
- 증거: [evidence/mac/run-2](../.scratch/floci-course-wayfinder/evidence/mac/run-2/)(검사 로그, 실패 시도 로그, `cloud-native-evidence/` 이번 실행분, 진단 Floci 로그, 파일럿 로그·결과).
- 다음: `1aa46ab5` 위에서 단위 검사와 앱 파일럿을 다시 돌린다(run-3).

## 재개 순서

1. 앱에서 이 수업을 열어 편집기·초기화·해설 재생을 확인한다(설치 앱이 아닌 개발 빌드). 문제가 있으면 `author_lesson.py`를 고치고 다시 실행한 뒤 `build-redesigned-git.py --lesson cloud-vpc-subnet-ec2`로 빌드한다. 해설이 바뀌면 `narration_review.py record`로 다시 검토를 남긴다.
2. 명령·편집이 바뀌면 관련 Docker 검사만 직렬로 다시 돌린다.

```powershell
cargo test --lib cloud_practice -- --test-threads=1
cargo test --lib cloud_practice::tests::docker_cloud_lesson_subnet_steps -- --ignored --test-threads=1 --nocapture
cargo test --lib cloud_practice::tests::docker_cloud_lesson_server_steps -- --ignored --test-threads=1 --nocapture
python tools/build-redesigned-git.py --check
python tools/build-redesigned-course-bundle.py --check
cargo test --test lesson_registry
```

3. 다음 수업(EC2 수명주기·삭제 의존성)은 별도 예고·PRD 승인부터 시작한다. S3·SQS·DB·Lambda는 그 뒤 묶음이다([추천 순서](../.scratch/floci-course-wayfinder/service-teaching-plan.md)).

## 이전 기록

- [사전 점검 기록](floci-first-lesson-preflight.md), [네이티브 연결·콘텐츠 계약](floci-cloud-native-runtime.md), [독립 검토 기록](../.scratch/floci-course-wayfinder/native-review.md)
- [승인 PRD 초안](../.scratch/floci-course-wayfinder/first-lesson/prd.draft.md), [예고 초안](../.scratch/floci-course-wayfinder/first-lesson/lesson-preview.draft.json), [대표 문제](../.scratch/floci-course-wayfinder/first-lesson/representative-problem.draft.md), [지도](../.scratch/floci-course-wayfinder/map.md)
- 공식 고정 Floci·Java 이미지의 amd64/arm64 manifest는 확인했으나 Mac 실행은 미검증이다. DIND·게스트 권한은 로컬 신뢰 실습 수준이다.
