# Floci 첫 수업 기술 사전 점검 (preflight)

2026-11-09, Windows 11 + Docker Desktop 29.8.1(`desktop-linux`, amd64). 실제 AWS·Mac·MQ 앱 코드는 쓰지 않았다. 이 문서는 [PRD 초안](../.scratch/floci-course-wayfinder/first-lesson/prd.draft.md)의 두 게이트를 실제 실행으로 닫으려는 기록이다. 운영 콘텐츠·해설·카탈로그·이미지 허용 목록은 바꾸지 않았다.

- 도구: `tools/floci_preflight/` (Python 표준 라이브러리 + AWS CLI v2 + Docker CLI)
- 원자료: `target/floci-preflight/<run>/` (git 제외). 실행마다 `summary.json`, 부분별 `events.json`(모든 명령 argv·rc·stdout·stderr), `cases.json`/`contract-results.json`, `host-before/after.json`, `host-diff.json`.
- 기준: 공식 Floci 2.4.0 이미지 `floci/floci@sha256:5ee85db6…`, 소스 커밋 `9be236e2890c2042a6bb819f1a9228be996acd90`(codeload tarball sha256 `aca07ce2…`를 `target/floci-preflight/_source/`에 보관).

## 재실행

```powershell
python tools/floci_preflight/run.py subnet   # 평범한 mock EC2 Floci 3개, Docker 소켓·privileged 없음
python tools/floci_preflight/run.py java     # 소유 privileged DIND 안의 실제 Java 25 EC2 게스트
python tools/floci_preflight/run.py all
python tools/floci_preflight/orphan_volumes.py <run-id> [--apply]   # 기록된 소유 컨테이너 mount로만 증명되는 익명 볼륨 정리
```

필요: `C:\Program Files\Amazon\AWSCLIV2\aws.exe`, `C:\Program Files\Git\bin\bash.exe`, Docker Desktop Linux 엔진. 포트는 Docker가 고르는 `127.0.0.1` 임의 포트라 고정 포트가 비어 있을 필요가 없다.

## 결과 요약

완전하고 깨끗한 실행은 `mq-floci-pf-20261109222727` 하나다(`summary.json`의 `all_ok: true`). 재시도를 통과로 세지 않았다. 아래 「실행 기록」의 실패 실행도 모두 남겼다.

| 부분 | 검사 | 호스트 인벤토리 |
|---|---|---|
| 서브넷 계약 (`subnet/contract-results.json`) | 19/19 | 전후 동일 (`clean: true`) |
| Java EC2 게스트 (`java/cases.json`) | 15/15 | 전후 동일 (`clean: true`) |

Java 게스트에서 실제로 관찰한 것(같은 실행):

- 게스트 `java -version`: `openjdk version "25.0.5" 2026-10-20 LTS`, Temurin-25.0.5+8, `Alpine Linux v3.24`. 이미지 amd64.
- 공식 Floci와 Temurin 모두 내부 엔진에서 **고정 digest로 pull**했다(제한 없음, save/load 불필요). 내부 `RepoDigests`에 고정 digest가 있다. 서버 이미지는 Temurin 레이어를 그대로 접두사로 갖고 레이어 1개만 더한다. 게스트 컨테이너의 이미지 ID가 빌드 결과와 같다.
- VPC `10.91.0.0/16`, 서브넷 A `10.91.1.0/24`(클라이언트 `10.91.1.10`), 학생이 만드는 B `10.91.2.0/24`.
- **잘못된 배치**: 서버를 A에 실행(`10.91.1.11`) → API running 1.88초, HTTP 준비 13.67초(그 사이 7번 `Connection refused`). 같은 VPC라 HTTP는 **응답하지만** 채점은 `server_in_wrong_subnet`으로 실패. 상태로 판정하고 도달성으로 판정하지 않는다.
- **올바른 배치**: B에 실행(`10.91.2.10`) → API running 1.77초, HTTP 준비 13.57초. A 서버가 남아 있는 동안은 실패, A를 terminate하고 실제 컨테이너가 사라진 뒤 통과.
- 채점기 요청: A의 클라이언트 게스트(`from=10.91.1.10`)에서 API 사설 IP `10.91.2.10:8080`으로 `HTTP/1.1 200 OK`, `instance=<B 서버 ID>`, `served-on=10.91.2.10`, `java.version=25.0.5`.
- user-data: 게스트의 `/var/lib/user-data.sh` sha256 = 입력 파일, marker `user-data start … instance=<서버 ID>`, 서버 프로세스 `java /opt/mq/HelloServer.java 8080`(PPid 1). user-data 없는 클라이언트는 자기 8080에서 연결 거부.
- 게스트 제한: 생성 시 Floci가 1 GiB·2 CPU(t3.micro). PID 제한은 생성 시 없음, 실행 뒤 `docker update`로 256. 게스트는 privileged.

서브넷 계약 19개 사례: 초기 상태 실패, 준비 코드 그대로(10.92.2.0/24 → `InvalidSubnet.Range`) 실패, 10.0.2.0/24 실패, 한 줄 수정 통과(diff 1줄), 같은 명령 두 번(두 번째 `InvalidSubnet.Conflict`) 통과, 다른 VPC 같은 CIDR(학생 `LAB_VPC_ID` 변경) 실패, 범위 안 다른 CIDR 실패, 추가 서브넷 실패, 출력만 위조(stdout에 목표 CIDR) 실패, 직접 API 통과, 삭제 후 재생성 통과, reset 후 새 VPC ID·학생이 만든 VPC 없음·준비 파일 바이트 복원, 해설 레인 시연(통과) 뒤 학생 레인 상태·파일·VPC ID 그대로, `10.73.0.0/16`/`10.73.2.0/24` 변형 4건(초기 실패, 준비 코드 `10.74.2.0/24` 실패, 기존 목표 `10.91.2.0/24` 거절, 수정 통과), 소유 VPC 삭제는 `fail`(`owned_vpc_missing`), 레인 중지는 `env_error`(`endpoint_unreachable`). 세 레인 모두 privileged 아님, 마운트 0개, Docker 소켓 없음, 게시 포트는 `127.0.0.1` 하나.

## 1. Java EC2 게스트 (PRD 스텝 3.1.1 게이트)

구성: 소유 네트워크·라벨 볼륨 위의 `docker:29.0.1-dind`(`--privileged --cgroupns=host`, 생성 시 4 CPU/6 GiB/2048 PID, 외부 게시는 `127.0.0.1:<임의>→4566` 하나) → 내부 엔진에 공식 Floci(생성 시 2 CPU/2 GiB/512 PID, 내부 소켓 `/var/run/docker.sock`과 카탈로그 파일 `:ro`만 bind) → EC2 게스트 컨테이너.

- **이미지 카탈로그**: `FLOCI_SERVICES_EC2_IMAGE_CATALOG_PATH=/etc/floci/image-catalog.yaml`. 스키마는 고정 커밋의 `Ec2ImageCatalog.java`(필수 `defaultDockerImage`, 항목별 `imageId/dockerImage/name/description/architecture/creationDate`, 144–149행, 필드 186–218행)와 `docs/services/ec2.md` 「External image catalog」(1447–1454행)로 확인했다. `dockerImage`에 내부에서 빌드한 이미지 ID(`sha256:…`)를 넣었다. `ImageCacheService.ensureImageExists`는 이미지 ID·로컬 이미지면 pull하지 않는다(64–96행).
- **카탈로그 교체 확인**: 우리 AMI는 정의한 이름·설명으로 조회된다. 번들 AL2023 AMI ID는 오류가 아니라 "Floci fallback image" 합성 항목으로 답한다. 번들 메타데이터(`Amazon Linux 2023 AMI`)가 사라진 것을 교체 증거로 삼는다.
- **서버 이미지**: `guest/Dockerfile`은 고정 Temurin `25-jdk-alpine` digest에 `HelloServer.java`·`HttpCheck.java` 두 파일만 더한다(레이어 1개 추가, 기반 레이어가 접두사인지 확인). CMD로 서버를 띄우지 않는다. Floci가 게스트를 `tail -f /dev/null`로 실행한다(`Ec2ContainerManager.java` 703행).
- **user-data**: `guest/server-user-data.sh`(LF 고정)를 `run-instances --user-data file://…`로 넘겼다. Floci는 `markRunning` 뒤 sshd 시작 다음에 `/var/lib/user-data.sh`로 복사해 `docker exec`한다(`Ec2ContainerManager.java` 536–575행, `UserDataPipeline.java` 276–286행). 성공 증거는 게스트 안의 파일 sha256이 입력과 같음, marker에 해당 인스턴스 ID, `server.pid`의 cmdline이 `java /opt/mq/HelloServer.java 8080`이고 PPid 1(exec 종료 뒤 남음), user-data가 없는 클라이언트 게스트에는 서버가 없음(자기 IP 8080 연결 거부)이다. 하네스는 서버를 수동으로 띄우지 않았다. `docker exec`는 관찰(`java -version`, 파일 읽기)과 채점기 HTTP 요청에만 썼다.
- **HTTP 서버**: `network_http` 수업과 같은 `ServerSocket` 원리지만 계속 도는 별도 프로그램이다. 기존 수업 연습 코드와 바이트 동일하다고 주장하지 않는다. 응답 본문에 `instance`(Floci가 넣는 `AWS_EC2_INSTANCE_ID`), `served-on`(받은 로컬 주소), `java.version`을 담는다.
- **채점기(3.1.1 시제품)**: 소유 기록(VPC·서브넷 A·클라이언트 ID·AMI·목표 CIDR)만 신뢰한다. 소유 VPC 서브넷/인스턴스 상태를 API로 읽고, 정확히 하나의 서버가 목표 서브넷에서 running이고 사설 IP가 목표 CIDR 안일 때만 소유 클라이언트 게스트에서 `HttpCheck`로 그 API 사설 IP에 새 요청을 보낸다. 응답의 instance·served-on·Java 25를 모두 맞춰야 통과다.

## 2. 대표 문제 서브넷 런타임·채점 계약 시제품

`subnet_lab.py`의 `Lane.init/reset/cleanup`과 `check()`, `subnet_contract.py`의 시나리오. 레인 하나가 Floci 프로세스 하나다(`FLOCI_SERVICES_EC2_MOCK=true`, `FLOCI_STORAGE_MODE=memory`, `--user 1001:0 --cap-drop ALL --security-opt no-new-privileges`, `/app/data`는 64 MiB tmpfs, 1 CPU/1 GiB/512 PID, 마운트·Docker 소켓 없음, `127.0.0.1` 임의 포트). 학생·해설·환경오류 확인 레인을 따로 띄운다.

- init: VPC 생성 → `available`까지 대기 → `control/owned.json`(VPC ID·CIDR·목표 CIDR·endpoint·준비 파일 sha256)을 작업 폴더 밖에 기록 → `workspace/create-subnet.sh` 준비 파일 작성. 학생 셸에는 `LAB_ENDPOINT`·`LAB_VPC_ID`·더미 자격 값만 준다(안전망으로 `AWS_ENDPOINT_URL`도 loopback).
- check: 소유 기록의 VPC를 `DescribeVpcs`로, 전체 서브넷을 `DescribeSubnets`로 읽어 **응답의 `VpcId`로 직접 나눈다**(필터를 믿지 않음). 명령 문자열·stdout·학생 변수는 읽지 않는다. 결과는 `pass`/`fail`/`env_error`와 코드·피드백·관찰 상태.
- env_error: endpoint 연결 실패·타임아웃·응답 해석 불가. 학생이 소유 VPC를 지운 경우는 `fail`(`owned_vpc_missing`)로 구별한다.
- reset(「다시 시작」): 같은 레인에 `POST /_floci/state/reset`(`EmulatorInfoController.java` 190–195행) 후 init 재실행, 준비 파일을 바이트 그대로 복원. endpoint가 바뀌지 않는다.
- 학생 행동은 실제 Git Bash로 `bash create-subnet.sh`를 실행하거나 AWS CLI argv를 직접 실행한다. 모의 객체는 없다.

이것은 런타임/채점 계약 테스트다. MQ 네이티브 통합 테스트가 아니다. MQ 코드는 한 줄도 거치지 않는다.

## 격리·안전 점검

- 모든 AWS CLI argv에 `--endpoint-url http://127.0.0.1:<port>`(코드에서 assert), 자식 환경의 `AWS_*`를 모두 지우고 `test/test`, 빈 소유 설정 파일, `AWS_EC2_METADATA_DISABLED=true`. 원래 환경은 출력·기록하지 않았다.
- 외부 자원은 모두 `mq.lab=<run>` 라벨. 삭제 전에 라벨을 다시 확인한다(`Run.owned`). prune·데몬 설정 변경·다른 자원 정리 없음.
- 호스트 전후 스냅숏: 컨테이너, 네트워크 전체 inspect(ID·IPAM·옵션 포함), 볼륨, context. 비교는 `docker ps`의 상대 시간 문자열과 `Networks` 나열 순서만 정규화하고 원본 스냅숏은 그대로 둔다.
- privileged DIND와 `--cgroupns=host`는 실험 경계일 뿐이다. 신뢰하지 않는 코드의 보안 경계나 합산 CPU/메모리 상한으로 입증된 것이 아니다. 게스트별 제한: Floci가 생성 시 인스턴스 유형대로 메모리·CPU를 건다(t3.micro → 1 GiB, 2 CPU). PID 256은 **실행 뒤** `docker update`로 건 값이다. Floci 게스트는 privileged로 생성된다(`withPrivileged(namespace == null)`, 702행).
- 게스트 SSH 포트 바인딩은 내부 엔진 안에 머문다. 외부 컨테이너의 게시 포트는 4566 하나다.
- Floci는 부팅 중 게스트에 `apk add openssh`와 메타데이터 도구를 설치한다(1659행, `Ec2MetadataProxy.java` 47행). 이 패키지 버전은 고정되지 않았다.

## 실행 기록 (실패 포함, 모두 보존)

| run | 부분 | 결과 | 원인과 처리 |
|---|---|---|---|
| `mq-floci-pf-20261109221336` | subnet | 실패, 0건, 인벤토리 불일치 | `--cap-drop ALL`이 Floci entrypoint의 `chroot --userspec`을 막아 레인 종료. 이후 `--user 1001:0`. 기본 `bridge` 네트워크 ID가 13:13:40.750Z(로컬 22:13:40.750)에 바뀜. 첫 변경 명령(22:13:41.663 종료, 0.194초)보다 앞이다. 원인은 단정하지 않는다. 익명 볼륨 1개는 처음에 무관하다고 잘못 적었고, 기록된 소유 컨테이너 mount(`/app/data`)로 이 실행 소유임을 확인해 정정을 덧붙였다(`INCIDENT.md`). |
| `mq-floci-pf-20261109221703` | subnet | 19/19, 인벤토리 불일치 | 레인 3개의 이미지 `VOLUME /app/data` 익명 볼륨이 `rm -f`로 남음. 이후 tmpfs `/app/data`와 `rm -v`. |
| `mq-floci-pf-20261109222304` | java | 12/14, 인벤토리 불일치 | 기준 오류 2개: 번들 AMI 조회가 오류 대신 fallback 항목으로 답함, 호스트(containerd 저장소)와 내부 엔진의 이미지 Id 의미가 달라 비교 불가. 기준을 각각 「번들 메타데이터 소멸」, 「내부 RepoDigests에 고정 digest」로 고침. 정리 버그로 소유 네트워크·이름 볼륨이 남음(이름 볼륨을 익명으로 오판). |
| `mq-floci-pf-20261109222523` | all | subnet 19/19 뒤 하네스 예외 | 비교 함수 버그로 요약 미작성, java 미실행. 저장된 스냅숏으로 다시 계산하면 clean. 완전한 실행으로 세지 않음. |
| `mq-floci-pf-20261109222727` | all | **subnet 19/19, java 15/15, 둘 다 clean** | 완전한 실행 |

나중에 한 소유 자원 정리는 원 실행의 `host-diff.json`(clean=false)을 고치지 않고 `ownership-cleanup.json`에 따로 기록했다. 221336·221703의 익명 볼륨 4개는 `orphan_volumes.py --apply`가 확인한 조건(기록된 라벨 컨테이너 mount와 이름 일치, 익명 라벨, host-before에 없음, 참조 컨테이너 없음)을 모두 만족할 때만 지웠다. 222304의 네트워크·이름 볼륨은 `mq.lab` 라벨 확인과 참조 컨테이너 없음 확인 뒤 지웠다. 지금 `mq.lab` 라벨 컨테이너·네트워크·볼륨은 없다. 이미지 캐시는 남겼다.

## Codex 독립 검토

최종 실행의 원본 이벤트를 별도로 처리해 AWS CLI 호출 111개가 모두 명시적 loopback endpoint를 사용한 것과 34개 검사 결과를 확인했다(`target/floci-preflight/mq-floci-pf-20261109222727/codex-final-review.json`). 이 호출 수에는 아래의 독립 조회가 포함되지 않는다.

실행 중인 소유 DIND의 라벨·포트 바인딩을 다시 확인한 뒤 EC2 API에서 서버와 클라이언트 정보를 새로 조회했다. 소유 클라이언트에서 서버의 API 사설 주소로 별도 HTTP 요청을 보내, 출발지 `10.91.1.10`, 목적지 `10.91.2.10`, HTTP 200, 서버 인스턴스 ID와 Java 25.0.5를 확인했다(`java/codex-live-http-check.json`, `success: true`). 첫 Java 실행에서는 정리가 이미 끝나 직접 조회하지 못한 사실도 해당 실행의 별도 파일에 남겼다. 그것을 성공으로 바꾸지 않았다.

고정 Floci·Temurin 이미지의 레지스트리 manifest에는 linux/amd64와 linux/arm64가 있다. 이는 Mac 런타임 실행 검증과 다르다. MQ 네이티브 코드와 UI는 이 사전 점검에서 실행하지 않았다.

## MQ 통합의 다음 구현 지점 (실제 소스 기준)

현재 MQ에는 Floci 실행기·소유 기록·상태 채점·초기화 통합이 없다. 가장 가까운 선례는 네트워크 실습이다.

1. 실습 정의: `src/git_practice.rs:25`의 `pub network: Option<NetworkExercise>` 옆에 `cloud: Option<CloudExercise>`를 둔다. 종류 검증은 `src/network_practice.rs:16-33` `NetworkExercise::validate`와 같은 방식.
2. 준비·터미널 환경: `src/git_practice.rs:461` `environment.extend(self.prepare_network()?)` 옆에 `prepare_cloud()`. 이 도구의 `Lane.start/init`과 `student_env()`가 내보낼 값의 계약이다(`LAB_ENDPOINT`, `LAB_VPC_ID`, 더미 자격 값, 빈 설정 파일).
3. 소유 상태 파일: `src/network_practice.rs:36-44`의 `State`와 `network-state.json`(121, 160행)처럼 `cloud-state.json`에 `owned.json` 필드를 저장. 재접속 시 라벨 확인은 `prepare_network`(327–382행)를 따른다.
4. 채점: `src/shell_practice.rs:278` `if self.exercise.network.is_some(){return self.check_network();}` 옆에 cloud 분기. `check_network`(`src/network_practice.rs:785`)처럼 `TestReport`를 돌려주고, 판정 로직은 `subnet_lab.check()`를 옮긴다. `env_error`를 실패와 다른 보고로 표현할 필드가 `TestReport`에 필요한지 결정해야 한다.
5. 정리·초기화: `cleanup_at`(`src/network_practice.rs:301`), `src/git_practice.rs:95/102/179`의 정리 호출, `reset`(`src/git_practice.rs:641`)에 레인 정리와 `/_floci/state/reset`을 연결. 컨테이너 삭제는 `-v`와 tmpfs `/app/data`로 익명 볼륨을 남기지 않는다.
6. 이미지 정책: `src/docker_lab.rs:561`의 Compose 이미지 허용 목록은 학생 Compose 파일용이다. Floci 레인은 실행기가 고정 digest로 직접 띄우므로 이 목록을 넓히지 않는다. 정책 결정은 남아 있다.

## 남은 게이트

- MQ 실행기 통합(위 1–6)과 그 네이티브 테스트. 이 도구의 결과는 MQ 통과 근거가 아니다.
- `--endpoint-url`을 지운 오답: 이 도구는 안전망 `AWS_ENDPOINT_URL`로 로컬에 머물게 했다. 실제 외부 AWS 차단(네트워크 수준)은 미구현·미검증.
- 학생 터미널도 같은 endpoint의 `/_floci/state/reset`을 부를 수 있다. 소유 VPC ID가 바뀌므로 채점은 실패하지만, 관리 경로 차단 여부는 결정되지 않았다.
- Java 게스트 경로의 privileged DIND와 privileged 게스트는 제품 보안 경계가 아니다. 학생 PC에서 쓸 격리 방식은 미결정.
- 3.1.1의 학생용 `run-instances` 준비 파일·요청 대상 파일 형식, 해설 레인의 Java 게스트 대기 시간(이번 측정: API running 약 1.8초, 실제 HTTP 준비 약 13.6초)은 제작 전 결정 사항.
- Floci 게스트 부팅의 `apk` 설치가 인터넷을 필요로 한다. 오프라인 동작은 확인하지 않았다.
- Mac은 확인하지 않았다. 같은 결과라는 것은 계획상 가정이다.
- CloudWatch Logs로 user-data 출력이 오는지는 이 구성에서 로그 그룹이 없어 확인되지 않았다. user-data 실행은 게스트 내부 증거로만 입증했다.
