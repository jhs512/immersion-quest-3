# Floci 클라우드 실습 — MQ 네이티브 런타임 통합 기록

2026-11-09~10, Windows 11 + Docker Desktop 29.8.1(amd64) + Git Bash + AWS CLI v2. 이 문서는 **MQ Rust 코드(`GitPractice`)를 통한 네이티브 통합**만 다룬다. 앞선 Python 사전 점검 결과는 [floci-first-lesson-preflight.md](floci-first-lesson-preflight.md)에 따로 있고, 여기서 다시 세지 않는다. 운영 콘텐츠·카탈로그·해설·이미지 허용 목록은 바꾸지 않았다. 커밋하지 않았다.

## 바뀐 파일

| 파일 | 내용 |
|---|---|
| `src/cloud_practice.rs` (새 파일) | `CloudExercise` 스키마·검증, 소유 상태 `cloud-state.json`, 두 런타임(mock 레인 / DIND 게스트), 준비·재접속·채점·정리, 실습 터미널의 `aws`·`client-request` 래퍼 |
| `src/cloud_practice_tests.rs` (새 파일) | 단위 검사와 실제 Docker 네이티브 검사. 2차 검토 뒤 Windows 단위 총 10개(설정 파일 검사 포함), Docker 네이티브 8개(`#[ignore]`) |
| `assets/cloud-lab/` (새 폴더) | 게스트 입력: `Dockerfile`(고정 Temurin 25 digest), `HelloServer.java`, `HttpCheck.java`, `server-user-data.sh`(LF 고정). 앱에 `include_str!`로 들어간다 |
| `src/git_practice.rs` | 선택 필드 `GitExercise.cloud`(기본값 `None`)·`cloud_demonstration`, 검증, `open_terminal`에서 `prepare_cloud`, 스토어 reset·`cleanup_network_labs`·`GitPractice::reset`에서 클라우드 정리 |
| `src/shell_practice.rs` | `check_shell` → `check_cloud` 분기 |
| `src/network_practice.rs` | 터미널 종료 훅 `release_network_demo`가 해설용 클라우드 런타임도 정리 |

`NetworkExercise`의 종류 목록에는 아무것도 더하지 않았다. 클라우드와 네트워크를 함께 쓴 실습은 검증에서 거절한다.

## 실제 수명주기 연결

| 앱 동작 | 호출 경로 | 클라우드 동작 |
|---|---|---|
| 실습 열기·재접속 | `git_terminal_ui` → `GitPracticeStore::open`/`reset_step` → `open_terminal` | `prepare_cloud`: 상태 파일이 없으면 새로 준비. 있으면 버전·fixture 해시·준비 완료·컨테이너 실행·소유 라벨·게시 포트·API 응답을 확인하고 그대로 이어 쓴다. 하나라도 어긋나면 오류(「초기화하세요」)이고, 다시 만들거나 오답 처리하지 않는다 |
| 제출 | `check_exercise` → `check_shell` → `check_cloud` | 소유 기록과 실제 API 상태, 채점기 자신의 HTTP 요청으로 판정한다. 런타임 문제는 `Err`(환경 오류)로, 오답은 `TestReport.passed=false`로 돌려준다(네트워크 실습과 같은 의미) |
| 「다시 시작」 | `reset_step` → `reset_from_locked` | 이전 폴더의 소유 자원만 정리한다. 이전 폴더는 복구 사본으로 남는다. 새 폴더에 준비 파일을 다시 쓰고, 다음 열기에서 새 런타임을 만든다 |
| 해설 | `GitPractice::new(exercise.demonstration())` | 임시 폴더라 소유 태그가 달라 별도 자원을 쓴다. 터미널을 닫으면 `release_network_demo` → `release_cloud_demo`가 그 자원만 지운다 |
| 파일럿 스토어 정리 | `cleanup_network_labs` | 각 실습 폴더에 `cloud_practice::cleanup_at` |

준비는 실습 터미널을 열 때만 한다. 모든 스텝을 미리 띄우지 않는다. 자원을 만들기 전에 상태 파일(`ready:false`)을 먼저 쓴다. 준비가 실패하면 `cleanup_at`이 그 실습의 라벨 자원을 지운다.

## 안전 규칙 (구현된 것)

- 소유: 모든 외부 자원에 라벨 `gg.molip.cloud-practice=<실습 루트 경로 sha256 앞 16자>`를 붙인다. 정리는 그 정확한 값의 라벨 필터로만 찾는다(컨테이너 `rm -f -v`, 네트워크, 이름 볼륨). prune이나 이름 기반 삭제는 없다.
- mock 레인(서브넷 목표): `--user 1001:0 --cap-drop ALL --security-opt no-new-privileges`, `/app/data`는 64 MiB tmpfs, 마운트·Docker 소켓 없음, 1 CPU/1 GiB/512 PID, `127.0.0.1` 임의 포트.
- 게스트 런타임(서버 목표): 라벨 네트워크와 라벨 이름 볼륨 위의 `docker:29.0.1-dind`(`--privileged --cgroupns=host`, 4 CPU/6 GiB/2048 PID, `127.0.0.1` 임의 포트 → 4566 하나). 내부 Floci는 내부 소켓과 카탈로그 파일만 bind한다. 공식 `FLOCI_SERVICES_EC2_IMAGE_CATALOG_PATH` 카탈로그가 앱에 내장된 소스로 빌드한 이미지 ID를 가리킨다. 이미지는 고정 digest로 pull하고 `RepoDigests`로 확인한다. pull이 실패하면 호스트 캐시를 시간 제한 안에서 save/load한다. 이때는 내용(레이어·플랫폼·설정)이 호스트의 고정 digest 이미지와 같을 때만 쓴다(아래 2차 반영).
- 백엔드 AWS 호출: `MOLIP_AWS` → PATH → 설치 위치(Windows `Program Files\Amazon\AWSCLIV2`, macOS/Linux 표준 경로) 순으로 찾는다. `aws-cli/2.`가 아니거나 없으면 준비 오류다. 자식 프로세스는 상속된 `AWS_*`를 모두 지우고 `test/test`, 소유 빈 설정 파일, 메타데이터 비활성, `us-east-1`만 쓴다. 모든 호출에 `--endpoint-url http://127.0.0.1:<소유 포트>`를 명시한다.
- 실습 터미널의 `aws`: 실습 폴더의 `cloud-bin/aws`가 PATH 맨 앞에 온다. `--endpoint-url`은 소유 URL과 정확히 같을 때만 허용한다. `--profile`·`--ca-bundle`·`--no-verify-ssl`·`--no-sign-request`는 실행 전에 거절한다. 셸의 `AWS_*`를 모두 지우고 더미 값만 다시 넣는다. 끝점을 지워도 소유 URL로 실행한다. MQ가 제공하는 `aws` 진입점을 막는 장치일 뿐이다. 학생이 실제 `aws.exe`를 전체 경로로 부르거나 다른 프로그램을 쓰는 것까지 막는 네트워크 격리는 아니다.
- 채점 근거: 소유 상태 파일의 VPC ID·준비 서브넷 ID·준비 인스턴스 ID와 API의 `VpcId`/`CidrBlock`/`State`/`SubnetId`/`ImageId`/`PrivateIpAddress`. 서브넷은 필터 없이 전부 받아 `VpcId`로 직접 나눈다. 학생 변수(`LAB_VPC_ID`)·명령 문자열·터미널 출력은 읽지 않는다.
- HTTP 채점: 주소 파일에서 IPv4를 읽어 API 사설 주소와 비교한다. 같을 때만 채점기가 소유 클라이언트 게스트 안에서 `HttpCheck`로 새 요청을 보낸다. 응답의 `instance`(서버 인스턴스 ID), `served-on`(그 주소), `from`(클라이언트 API 주소), `java.version` 25.x, 게스트 컨테이너 이미지가 빌드 결과와 같은지를 모두 맞춰야 한다. 방금 실행한 인스턴스는 정해진 시간(running 90초, HTTP 90초) 안의 상태로 판정한다. API `running`과 HTTP 준비는 따로 기다린다.

## 콘텐츠 작성 계약

`GitExercise`에 `cloud`와 `shell`을 함께 둔다. `initial_history`는 `uninitialized`로 둔다. 준비 파일(예: `create-subnet.sh`, 주소 파일)은 `shell.start.files`와 `shell.demo.files`에 넣는다. `shell.commands`는 비워도 된다(상태 채점).

```json
{"cloud":{"goal":"create_subnet","vpc_cidr":"10.91.0.0/16","target_cidr":"10.91.2.0/24"},
 "initial_history":"uninitialized",
 "shell":{"step_id":"cloud-1-2-2","start":{"files":{"create-subnet.sh":"..."}},"goal":{},"demo":{"files":{"create-subnet.sh":"..."}}}}
```

| goal | 필수 필드 | 준비되는 것 | 통과 조건 |
|---|---|---|---|
| `create_subnet` | `target_cidr`(VPC 안, 준비 서브넷과 겹치지 않음) | VPC, 선택한 `subnets` | 준비 서브넷 그대로 + 새 서브넷이 정확히 하나이고 `target_cidr`·available |
| `choose_subnet` | `subnets`(1개 이상), `new_prefix` | VPC, 준비 서브넷 | 준비 서브넷 그대로 + 새 `/new_prefix` 서브넷 정확히 하나 |
| `launch_server` | `subnets`(2개 이상), `target_subnet` | VPC, 서브넷, 서버 이미지 | 새 서브넷 없음 + 새 인스턴스 정확히 하나, 준비 AMI, running, `target_subnet`, IP가 그 CIDR 안 |
| `request_server` | `subnets`, `client_subnet`≠`server_subnet`, `address_file` | 클라이언트·서버(user-data로 자바 서버 시작, HTTP 준비까지 대기) | 새 자원 없음 + 주소 파일 = 서버 API 사설 주소 + 채점기 HTTP 확인 |
| `deploy_server` | `subnets`, `client_subnet`, `target_cidr`, `address_file` | VPC, 클라이언트 서브넷·클라이언트, 서버 이미지 | 새 서브넷 `target_cidr` 하나 + 그 안의 서버 한 대 + 주소 파일 일치 + 채점기 HTTP 확인 |

선택 필드 `editable`(최대 4개)은 터미널 위 편집기에 보여 줄 준비 파일 목록이다(2026-11-10 추가). 모든 항목이 `shell.start.files`와 `shell.demo.files`에 있어야 한다. 목록에 없는 준비 파일(`list-subnets.sh` 같은 조회 명령)은 터미널 폴더에만 있다. 편집기는 Compose와 같은 `editable_files`/`save_editable` 경로를 쓰고, 해설의 `patch_code`도 `file`로 이 파일을 고친다.

목표가 쓰지 않는 필드는 비워야 검증을 통과한다. 서브넷 이름은 대문자·숫자 8자 이하이고, 환경 변수 이름이 된다. VPC는 `/16`~`/24`이다. 실습 터미널 환경 변수는 다음과 같다.

- `LAB_ENDPOINT`, `LAB_VPC_ID`, `LAB_SUBNET_<이름>_ID`
- 서버 목표: `LAB_SERVER_AMI`, `LAB_CLIENT_ID`, `LAB_SERVER_ID`
- 더미 AWS 값

서버 목표에서는 런타임이 작업 폴더에 `server-user-data.sh`를 내장 원본으로 쓴다. 클라이언트가 있으면 `client-request <IPv4>`(소유 클라이언트에서 HTTP 요청)를 PATH에 둔다. 학생에게 보이는 피드백은 `TestCaseResult`의 `input`/`expected`/`stdout`이며 해요체다. 컨테이너 이름 같은 구현 정보는 넣지 않는다.

PRD 스텝과의 대응:

| PRD 스텝 | goal |
|---|---|
| 1.2.1, 대표 1.2.2 | `create_subnet` |
| 1.2.3 | `choose_subnet` |
| 2.1.1, 2.1.2(잘못 배치 → 「다시 시작」 → 수정) | `launch_server` |
| 2.2.1 | `request_server` |
| 3.1.1 | `deploy_server` |

## 실행한 명령과 결과

| 명령 | 결과 |
|---|---|
| `cargo test --lib cloud_practice` | 단위 5 통과(스키마 왕복·unknown 필드 거절, 목표별 검증, 네트워크와 혼용 거절·주소 파일 준비 요구, fixture 해시, 래퍼 가드). 래퍼 가드는 argv만 출력하는 대역 CLI로 확인했다. 끝점이 주입되고 상속된 프로필·키가 바뀌며, 외부·다른 포트 끝점과 `--profile`·`--no-verify-ssl`이 실행 전에 거절된다 |
| `cargo test --lib cloud_practice::tests::docker_cloud -- --ignored --test-threads=1 --nocapture` (run 1, 345초) | 6개 중 5개 통과. `changed_fixture_and_choose_subnet`은 본문 단언은 모두 통과했다. 그러나 호스트 인벤토리 가드가 실패했다. 기본 `bridge` 네트워크 ID가 `8f93c436` → `40f8b1ea`로 바뀌었다(생성 시각 23:51:03, 이 테스트의 before 스냅숏 5초 뒤). 다른 컨테이너·네트워크·볼륨 변화와 소유 잔여물은 없었다. 원인은 확인하지 않았다(`run1-INCIDENT.txt`, `run1-fixtures-*.json`) |
| 같은 명령, 해당 테스트만(run 2, 43초) | 통과, 호스트 인벤토리 동일. **재시도 통과**다 |
| `cargo test --lib git_practice` | 19 통과(기존 shell/network/docker 단위 포함), 10 ignored |
| `cargo check --bins --lib` | 성공. 경고 3개는 기존 `native_trace.rs`의 것 |
| `cargo test --test lesson_registry` | **실패**: `LESSONS.len()` 110 ≠ 102. 이 작업이 건드리지 않은 레지스트리의 기존 상태다 |
| `cargo check --all-targets` | `kpc_learning`·`narration_replay` 테스트가 gitignore된 생성 파일 `courses/kpc-solutions.json`이 없어 컴파일되지 않는다. 기존 환경 문제다 |

네이티브 테스트가 실제로 확인한 것(로그: `target/cloud-native-evidence/native-run-1.log`, 테스트별 `*-before/after.json`):

- **대표 문제**(`GitPracticeStore` 경로, 실제 Git Bash에서 `bash create-subnet.sh` 실행)
  - 초기 상태 실패
  - 준비 코드 그대로 실행하면 `InvalidSubnet.Range`로 실패
  - 성공처럼 보이는 JSON을 출력만 하면 실패
  - 학생이 만든 VPC에 같은 CIDR을 만들면 실패(「다른 자리」 피드백)
  - 범위 안의 다른 CIDR 실패, 목표에 추가 서브넷까지 있으면 실패
  - 추가 서브넷을 직접 명령으로 지우면 통과
  - 래퍼: 외부 끝점 거절, 끝점을 생략하면 소유 VPC 조회, `--profile` 거절
  - 재접속: 같은 VPC로 통과 유지
  - 해설 레인: 다른 포트에서 시연하고 통과, 닫으면 그 런타임만 제거, 학생 상태·파일 그대로
  - 학생 런타임을 멈추면 채점과 재접속 모두 `Err`
  - `reset_step`: 이전 런타임 제거, 이전 폴더 보존, 준비 파일 바이트 복원, 초기 실패, 한 줄 수정 통과
  - 목표가 바뀐 콘텐츠로 열면 재접속 거절
- **변형 fixture**: `10.73.0.0/16`/`10.73.2.0/24`에서 초기 실패, 준비 코드 실패, `10.91.2.0/24` 거절, 수정 통과.
- **`choose_subnet`**: 겹치는 `/25` 거절, 빈 `/24` 통과, 두 번째 새 서브넷 실패, 준비 서브넷을 지우면 실패.
- **외부 라벨 자원**: 같은 이름의 외부 라벨 컨테이너가 있으면 준비가 실패한다. 실패한 준비는 자기 네트워크와 상태 파일만 지우고, 외부 컨테이너는 그대로 남는다.
- **`launch_server`**(실제 게스트)
  - 준비 스크립트 그대로(A)면 「목표 서브넷이 아닌 곳」(`10.91.1.11`)으로 실패
  - `reset_step` 뒤 새 런타임에서 초기 실패
  - B로 고치면 통과(`10.91.2.10 running`)
- **`request_server`**
  - 자리표시 주소 `10.91.2.99` 실패
  - 같은 서버의 Docker 주소 `172.17.0.3`은 「API가 알려 준 … 아니에요」로 실패
  - 출력 위조 실패
  - `describe-instances`로 받은 주소면 통과. 채점기 HTTP: `from=10.91.1.10`, `served-on=10.91.2.10`, `instance=<서버 ID>`, `java.version=25.0.5`
  - 학생용 `client-request`도 200 응답
- **`deploy_server`**
  - 학생이 `10.91.2.0/24`를 만들고 A에 서버를 실행하면 실패
  - 그 서버를 종료하고 새 서브넷에 실행하면 통과(같은 HTTP 신원 확인)
- 각 Docker 테스트 전후의 호스트 컨테이너·네트워크·볼륨·context가 같고, `gg.molip.cloud-practice` 라벨 자원 0개. run 1의 fixtures 테스트만 예외(위 표).

## 독립 검토 반영 (2차, 2026-11-10)

검토 원문: `.scratch/floci-course-wayfinder/native-review.md`(Codex).

**루트가 먼저 고친 두 가지.** 내 구현 중에 `src/cloud_practice.rs`에 직접 반영됐고, 그대로 유지했다.

- `aws` 래퍼가 `--endp`처럼 줄여 쓴 위험 전역 옵션도 거절한다.
- 소유 빈 설정 파일이 링크·디렉터리·내용 있는 파일을 거절하고 `create_new`로만 만든다. 버전 조회도 명시적인 빈 설정을 쓴다.

Codex는 렌더링한 래퍼 원문을 **실제 AWS CLI**와 loopback 수신기 두 개로 따로 검사했다(8/8, 원래 채팅 작업 폴더의 `work/cloud-wrapper-review/fixed-results.json`). 실제 AWS에는 접속하지 않았다. 그 결과는 스크립트 단독 회귀 검사이고, 아래의 네이티브 검사와 별개다.

**이번에 고친 것**

| 검토 항목 | 수정 |
|---|---|
| 제출 경로 | 네이티브 Docker 테스트의 채점이 전부 `check_exercise()` → `check_shell()` → `check_cloud()`, 곧 앱의 제출 분기를 거친다. 테스트에서 `check_cloud()`를 직접 부르지 않는다 |
| 호스트 인벤토리 | 원본: `docker ps`/`volume ls` 행(컨테이너 Config·Env 없음), 모든 네트워크의 전체 `network inspect`(IPAM·Options·Labels·Created).<br>비교 보기: 네트워크를 Id로 묶어 bridge 교체를 차이로 남긴다. 연결 목록과 상대 시간만 원본 파일에 둔다.<br>테스트 전: 엔진 응답을 확인하고, 2초 간격 두 스냅숏이 같을 때까지 반복한다. 실패·불일치 탐침도 파일로 남긴다.<br>실행마다 시각 접미사를 붙여 이전 증거를 덮어쓰지 않는다 |
| AMI 아키텍처 | 빌드한 게스트 이미지의 `Architecture`에서 정한다(amd64→x86_64, arm64→arm64, 그 밖은 준비 오류) |
| 주소 파일 | 링크가 아닌 일반 파일이고 256바이트 이하인지 먼저 확인한다. 읽기도 257바이트로 제한한다. 내용은 피드백에 쓰지 않고, 정상 IPv4로 해석된 값만 쓴다 |
| 추가 서브넷 피드백 | 목표가 아닌 새 서브넷 하나만 있을 때도 「목표가 아닌 새 서브넷이 있어요: 10.91.3.0/24」로 관찰한 상태를 말한다(전에는 「추가 서브넷이 없어요」) |
| 이미지 전송 | `docker save` → `docker exec -i … docker load`를 한 시간 제한(600초) 안에서 둘 다 감시한다. 어느 쪽이든 실패하거나 시간이 지나면 두 프로세스를 kill하고 wait로 회수한다 |
| 전송 뒤 출처 | 실측 결과 archive load 뒤 digest 참조는 남지 않았다(`No such image: …@sha256:c7c3…`). 그래서 불러온 이미지의 RootFS 레이어·OS·아키텍처·Env/Cmd/Entrypoint/WorkingDir/User를 호스트의 고정 digest 이미지와 비교한다. 같을 때만 그 ID에 소유 태그 `mq-cloud-verified/<이름>:<ID 16자>`를 붙여 Dockerfile `FROM`과 Floci 실행에 쓴다. 다른 이미지는 거절한다. registry에서 pull했을 때는 이전처럼 `RepoDigests`로 확인한다 |

**2차 실행 결과**

- `cargo test --lib cloud_practice`: **10 통과**.
  - 단위 7개: 래퍼(정확·등호·중복 owned 허용, 외부·다른 포트·빈 값·값 없음·중복 중 하나가 다른 경우·`--endp`·`--endpoint`·`--prof`·`--ca-b`·`--no-verify`·`--no-sign` 거절. argv만 출력하는 대역 CLI라 아무 곳에도 접속하지 않음), 주소 파일(초과·큰 파일·잘못된 UTF-8·두 줄·디렉터리·없는 파일), 아키텍처 대응, 기존 스키마·검증 4개.
  - Windows 공통 `config_file_regressions` 3개.
  - Unix 전용 링크 검사 2개(설정 파일, 주소 파일 부분)는 Windows에서 컴파일되지 않으므로 통과로 세지 않는다.
- `native-run-3.log`(Docker, 테스트별 순서 실행):
  - `docker_cloud_transfer_cached_image_and_verify_provenance` **실패**. 테스트 본문 전의 before 인벤토리에서 `network inspect`가 `network 40f8b1ea… not found`를 냈다. 그 시점까지는 읽기 명령만 실행했다. 이후 기본 bridge는 `94e13c67…`(Created 15:09:33Z)로 바뀌어 있었다. 원인은 확인하지 않았다. 인벤토리 함수가 그 오류를 재시도하지 않고 멈춘 것은 하네스 결함이라 고쳤다(재시도하고 오류 탐침을 파일로 남김).
  - `docker_cloud_transfer_failure_reaps_both_processes` 통과. 없는 수신 컨테이너면 215 ms에 `Err`, 두 프로세스 회수.
  - `docker_cloud_representative_subnet_lifecycle` 통과(75초, 새 인벤토리 동일, 추가 서브넷 피드백 단언 포함).
  - `docker_cloud_changed_fixture_and_choose_subnet` 통과(47초, 동일).
  - `docker_cloud_guest_deploy_java_server` 통과(74초, 동일). 제출 분기, pull 출처 경로, 이미지 기반 아키텍처 카탈로그를 거친 최종 서버 smoke다.
- `native-run-4-transfer.log`: 전송 출처 검사 재실행 **통과**(21초, 인벤토리 동일). `--network none` 소유 DIND에 pull 없이 8.6초 만에 load했다. digest 참조는 없었고, 내용 비교로 `mq-cloud-verified/eclipse-temurin:e53000d4fa5dd385`를 받았다. 네트워크 없이 `java -version` 25가 실행됐다. 같은 load 결과를 Floci 이미지로 주장하면 거절됐다. **재시도 통과**다.
- launch·request 게스트 테스트는 이번 변경과 관계없는 경로라 다시 돌리지 않았다(1차 결과 유지).
- `cargo test --lib git_practice`: 21 통과(cloud 단위 10 + 기존 11), 12 ignored, 0 실패.
- 모든 실행 뒤 `gg.molip.cloud-practice` 라벨 컨테이너·네트워크·볼륨 0개.

**bridge 교체 관찰.** 사전 점검 run 1, 네이티브 run 1, 네이티브 run 3에서 각각 한 번씩, 조용한 시간 뒤의 첫 Docker 사용 무렵에 기본 bridge ID가 바뀌었다. run 3에서는 테스트가 자원을 바꾸기 전, 읽기 명령만 실행한 시점이었다. 원인은 단정하지 않는다. 비교에서 이 차이를 없애지 않는다.

## 한계 (그대로)

- 신뢰된 로컬 Docker Desktop 실습이지, 다중 사용자·보안 샌드박스가 아니다.
  - 서버 목표는 privileged DIND(`--cgroupns=host`)와 Floci가 privileged로 만드는 게스트를 쓴다.
  - 외부 컨테이너 상한은 내부 자식 전체의 합산 상한으로 입증되지 않았다.
  - 게스트 PID 상한은 걸지 않았다.
- 게스트 부팅 중 Floci가 `apk add`로 패키지를 설치하고, 준비가 이미지를 pull한다. 인터넷이 필요하다. 준비 전체(`prepare_cloud`)가 save/load 대체 경로로 끝까지 간 실행은 없다. 그 경로의 전송·출처 함수만 위 2차 전송 테스트로 확인했다.
- mock 레인은 메모리 저장이다. 컨테이너가 멈추면 상태가 사라지므로 재접속은 오류를 내고 초기화를 요구한다. 학생이 같은 끝점의 `/_floci/state/reset`을 부르면 VPC가 사라져 「준비된 VPC가 없어졌어요」 실패가 된다. 막지 않았다.
- `aws` 래퍼는 MQ의 진입점 가드다. 전체 경로 `aws.exe`·`curl` 등 다른 프로그램의 외부 호출은 막지 않는다. 실습 셸에는 `AWS_ENDPOINT_URL`을 소유 주소로 넣어 두었을 뿐이다.
- 카탈로그 `architecture`는 빌드한 이미지에서 정한다. arm64에서 실행하지 않았으므로 arm64 경로와 Mac은 검증되지 않았다. Mac·Linux 코드 경로는 컴파일 조건만 있고 실행하지 않았다.
- 캐시 전송 경로는 이미지 하나를 네트워크 없는 내부 엔진에 넣는 데까지 확인했다. 게스트 부팅 중 `apk` 설치는 여전히 인터넷이 필요하다. 오프라인 실습 전체를 지원한다고 주장하지 않는다.
- 앱 UI(`GitTerminal`)로 화면을 열어 보지 않았다. 검증은 같은 `GitPractice`/`GitPracticeStore` API를 테스트에서 직접 부른 것이다.
- 서버 목표 준비 시간은 따로 재지 않았다(6개 Docker 테스트 전체 345초). 해설 레인이 게스트 런타임을 하나 더 띄우는 비용도 콘텐츠 설계에서 정해야 한다.
- 기본 `bridge` 네트워크 교체가 사전 점검 run 1과 네이티브 run 1에서 각각 한 번 관찰됐다. 이 작업은 데몬·bridge를 바꾸는 명령을 실행하지 않는다. 원인은 확인하지 않았다.

## 재실행

```powershell
cargo test --lib cloud_practice
cargo test --lib cloud_practice::tests::docker_cloud -- --ignored --test-threads=1 --nocapture
```

`cargo test --lib cloud_practice`는 `tests`와 `config_file_regressions`를 모두 포함한다. `docker_cloud` 필터에는 전송 테스트 두 개도 들어간다. Docker 테스트는 `--test-threads=1`로 실행한다(테스트마다 호스트 전체 인벤토리를 비교한다). 결과물은 `target/cloud-native-evidence/`(git 제외)에 남는다. 원본 `*-raw.json`, 비교용 `*.json`, 탐침 `*-before-probe-*`가 있다.

## 다음 단계

승인된 첫 수업의 콘텐츠 작성이다. 위 「콘텐츠 작성 계약」의 다섯 goal과 환경 변수, 준비 파일 규칙에 맞춰 스텝을 만든다. 런타임 스키마를 바꾸려면 이 문서와 테스트를 함께 고친다.
