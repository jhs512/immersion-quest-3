# Windows 로컬 Floci 네트워크 실측

2026-11-09. 문서의 지원 목록과 실제 패킷 결과를 구별하기 위한 실험이다. 실제 AWS 계정·클라우드 자원은 사용하지 않았다. 이 결과는 **Windows Docker Desktop 안의 별도 Linux Docker 엔진(DIND)** 에 한정한다. Windows 호스트에서 EC2 IP로 직접 접속하는 실험이나 macOS 검증은 아니다.

## 재현 환경과 격리

- 호스트: Windows 11, Docker Desktop Linux 엔진 29.8.1, `desktop-linux`, WSL2 커널 `6.6.87.2-microsoft-standard-WSL2`, amd64.
- 내부 엔진: `docker:29.0.1-dind`, digest `sha256:ecac43e78380d9b9d3bd24f0ab42b370f6391a1a06a66065c10a00b9d6d57a3e`.
- Floci: 공식 안정판 2.4.0, 소스 커밋 `9be236e2890c2042a6bb819f1a9228be996acd90`, 이미지 인덱스 digest `sha256:5ee85db604c4aa74ac76e07ea5cc83086f37bb472bf3dbb97e34019e48efae9c`. 실제 amd64 매니페스트는 `sha256:7ab87e9a83909072aceb33d7026f8127a5f5dd693a974e0d30a0474eafcf91b9`이다. arm64 존재도 조회했으나 실행하지 않았다. 서명 검증은 하지 않았다.
- 게스트: `ami-alpine`이 가리키는 Alpine을 digest `sha256:f59abe656b692d901e184be3445e084786602108599d2a51d229c0f5a48c71bf`로 pull하고 카탈로그의 태그에 연결했다. 게스트 SSH 준비 과정의 apk 패키지 버전까지 고정한 것은 아니다.
- DIND는 전용 네트워크·볼륨, unix Docker 소켓만 사용한다. 외부 호스트 소켓·홈·SSH·AWS 자격 증명 디렉터리는 마운트하지 않았다. 외부 포트는 **`127.0.0.1:45669 → 4566/tcp` 하나**다. 내부 EC2의 SSH `0.0.0.0:2200…`은 DIND 네트워크 안에 머문다. 내부 2375/2376 데몬 포트를 게시하지 않았다.
- DIND `4 CPU / 6 GiB / 2048 PID`, Floci `2 CPU / 2 GiB / 512 PID`, EC2 `t3.nano`는 실제 inspect에서 각 `2 CPU / 512 MiB`였다. `--cgroupns=host`를 사용하므로 외부 컨테이너 상한이 내부 자식 전체의 합산 상한이라고 해석하지 않는다. 게스트별 상한은 별도로 확인했다. privileged DIND는 신뢰하지 않는 코드의 보안 경계로 채택한 구성이 아니다.
- 모든 AWS CLI 요청은 명시적 loopback endpoint, `test/test`, 빈 임시 설정·자격 증명 파일, 메타데이터 자격 증명 탐색 비활성화로 실행했다. 개인 자격 증명 파일은 읽지 않았다.

Floci 기본 EC2 생성은 SSH 포트를 호스트 전체 인터페이스에 게시한다. 사전 소스 확인 후 호스트 데몬에 직접 실행하지 않고 DIND로 격리했다. 이는 MQ에 곧바로 통합된 실행 환경이 아니라 이번 실험용 후보 구성이다. ([EC2 생성 소스](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/src/main/java/io/github/hectorvent/floci/services/ec2/Ec2ContainerManager.java#L716), [포트 바인딩 소스](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/src/main/java/io/github/hectorvent/floci/core/common/docker/ContainerLifecycleManager.java#L1586))

## 방법

API 성공 응답을 패킷 성공으로 세지 않았다. 실제 Docker 컨테이너·네트워크·IP·상태·자원 제한을 inspect하고, 게스트 안에서 BusyBox `nc`로 인스턴스 ID를 담은 HTTP 응답을 제공했다. 다른 게스트의 새 `wget` 프로세스가 응답을 받아 **정확한 대상 ID**와 일치해야 통신 성공이다. 닫힌 8081 포트를 음성 대조군으로 사용했다. API 라우팅 변경 전후에는 실제 `ip route`도 기록했다.

주 실험의 순서별 응답 벡터는 `[같은 서브넷, 같은 VPC 다른 서브넷, 다른 VPC 사설 IP, 닫힌 포트, 다른 VPC의 공통 Docker bridge IP]`다. 기본·IGW 경로 변경·deny NACL·peering·NAT 단계에서 모두 `[성공, 성공, 실패, 실패, 성공]`이었다. 같은 서브넷 통신은 NACL의 서브넷 경계 효과를 판정하는 근거로 쓰지 않았다.

## 실제 관찰과 판정

| 항목 | 관찰 | 판정 / 수업에서의 범위 |
|---|---|---|
| VPC·서브넷 생성/조회 | CIDR·연결 ID 조회, 실제 EC2 생성 시 VPC별 Docker bridge 생성 | 기본 자원 관계·조회 실습 가능 |
| 입력 검증 | 중첩 `/25` → `InvalidSubnet.Conflict`; VPC 밖 CIDR·`/29` → `InvalidSubnet.Range`; 예약 `.1`·서브넷 밖 IP → `InvalidParameterValue` | 검사한 잘못된 입력은 올바르게 거절 |
| 의존성 | 서브넷이 있는 VPC 및 실행 인스턴스가 있는 서브넷 삭제 → `DependencyViolation` | 선택 삭제 순서 실습 가능 |
| 기본 EC2 IP | 10.91.1.10/.11, 10.91.2.10이 API와 Docker VPC IP에서 일치. 동일 VPC 두 서브넷은 하나의 실제 `/16` bridge에 연결 | IP·서브넷 소속 관찰 가능. 별도 AWS 서브넷 라우터로 설명하면 안 됨 |
| 기본 SG | ingress 규칙이 없는 사용자 SG로도 HTTP 성공 | 기본 설정은 SG 차단 수업에 부적합 |
| VPC 구별 | 다른 VPC의 10.92.1.10은 timeout. 동일 대상의 공통 bridge 172.17.0.5는 성공 | VPC IP 기준 분리는 관찰됨. 전체 네트워크 격리 보장은 실패 |
| Route table·IGW | attach 및 더 구체적인 IGW 경로가 API에는 active. 커널 경로와 패킷 벡터는 그대로 | API 저장 상태와 실제 경로를 구별하는 실습만 가능 |
| NACL | 소스 서브넷에 ingress·egress deny-all rule 1을 연결했어도 **다른 서브넷 대상** HTTP 성공 | 이 구성에서는 NACL 패킷 필터가 작동하지 않음 |
| Peering | 별도 보강 실험에서 양쪽 서브넷의 route table, 양방향 peer 경로, default allow NACL, active peer 확인. 생성 전/후/삭제 후 모두 양방향 VPC 사설 IP timeout, bridge 대조군 성공 | peer 제어면 상태는 저장되나 실제 peer 경로 생성은 관찰되지 않음 |
| NAT | EIP `203.0.113.1`, NAT available, default NAT route 저장. 기존 패킷 벡터와 커널 경로 동일 | NAT API 관계만 검증. **SNAT·인터넷 출구·사설 서브넷 인터넷 접근을 실증한 것은 아님** |
| SG opt-in ingress | helper transport IP에서 기본 deny → allow 8080 성공 → revoke 실패 → restore 성공 | Linux netns SG 필터의 실제 패킷 효과 확인 |
| SG opt-in egress | 대상 ingress 유지, 소스 egress 제거 실패 → 8080만 허용 성공 → revoke 실패 → 전체 egress 복구 성공 | ingress와 egress를 따로 바꾸는 실습 가능 |
| SG opt-in IP 한계 | helper 실제 주소는 172.17.0.2/.3. API 사설 IP 10.94.1.11은 ingress 허용 후에도 timeout | SG 결과는 transport IP 기준. API 사설 IP를 그대로 사용하는 EC2 수업에는 추가 해결 필요 |
| 수명주기 | 보강 실험은 API stopped **및** 실제 Docker Running=false까지 poll 후 패킷 실패. start 뒤 marker 서버 재기동 시 성공. terminate 뒤 실제 컨테이너 없음 | 비동기 완료를 기다리는 수명주기 실습 가능 |
| 다른 CIDR 반복 | 10.93.1.10/.11도 API=실제 VPC IP, 새 HTTP marker 성공. 두 인스턴스 종료 후 서브넷·사용자 SG·VPC 선택 삭제 성공 | 기본 결과의 두 번째 CIDR 재현 확인 |

이 표의 제한은 실제 AWS와 동등한 네트워크 동작을 주장하지 못한다는 뜻이다. 특히 주 실험의 VPC 내부 목적지→IGW 경로를 AWS에서도 같은 조건으로 받아들인다고 가정하지 않는다. AWS 실서비스 대조 실험은 하지 않았다. 관찰 범위와 공식 소스 설명은 일치한다. ([Floci SG 문서: 라우팅·NACL·NAT·peering 제외 범위](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/ec2.md#security-group-port-publishing), [VPC 구현](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/src/main/java/io/github/hectorvent/floci/services/ec2/net/VpcNetworkManager.java))

## 실행 기록

| 디렉터리 | 상태와 의미 |
|---|---|
| `mq-floci-win-20261109203257` | 준비 실패: 기본 cgroup namespace에서 내부 Floci 생성의 cgroupv2 오류. `--cgroupns=host`로 해결 |
| `mq-floci-win-20261109203335` | 부분 실행: Alpine에 `httpd` 실행 파일이 없어 probe 서버 준비 실패. `nc` 서버로 수정 |
| `mq-floci-win-20261109203423` | 부분 실행: NACL CLI에 필수 Egress 값 누락. 서비스 오류가 아닌 하네스 오류 |
| `mq-floci-win-20261109203533` | 부분 실행: 설치된 AWS CLI가 `--no-egress`를 거절. offline skeleton 확인 후 JSON `Egress:false/true`로 직렬화 |
| `mq-floci-win-20261109203651` | 주 실험 완료. 47개 관찰 레코드, 210개 명령 이벤트. 고정 3초 뒤 stop snapshot은 **아직 Running=true/패킷 성공**이며 실패 자료를 그대로 보존함 |
| `mq-floci-win-20261109203948` | 깨끗한 양방향 peering 보강 완료. 주 실험의 단방향 route 및 deny NACL 잔존 조건을 제거 |
| `mq-floci-win-20261109204107` | 실제 stopped 상태 polling을 추가한 수명주기 보강 완료. 주 실험의 성급한 stop 해석을 대체 |

47개를 모두 통과 테스트라고 세지 않는다. 입력 거절·실제 성공·기능 경계·대조군·중간 상태가 함께 들어 있는 관찰 기록이다. `events.json`은 명령/종료코드/실제 stdout·stderr, `instance-*.json`은 API와 실제 컨테이너·helper inspect, `matrix.json`/`peering-matrix.json`/`lifecycle-matrix.json`은 비교 결과다. `fatal.json`은 부분 실행의 실제 실패 이유다.

## 정리·검증과 재실행

모든 실행은 `finally`에서 소유 라벨을 검사한 외부 컨테이너·볼륨·네트워크만 제거했다. 전후 전체 인벤토리 비교에서 기존 컨테이너·네트워크·볼륨 추가/삭제 차이가 없으며 기존 `mq3-gitlab-6afa409d-ci`도 보존했다. 이미지 캐시는 남겼고 실행 중인 실험 자원은 없다. `audit.json`에 각 실행의 차이, loopback endpoint 검사, 제한된 자격 증명 패턴 검사 결과를 기록했다. 패턴 검사는 비밀 탐지의 완전성을 보장하는 도구는 아니며, 컨테이너 Env와 마운트 경로도 별도로 확인했다.

재실행은 Windows PowerShell에서 이 디렉터리의 `windows_lab.py`, `windows_peering.py`, `windows_lifecycle.py`를 **하나씩 순서대로** Python으로 실행하고, 끝에 `audit_evidence.py`를 실행한다. AWS CLI 경로와 Docker Desktop Linux 엔진이 필요하다. `45669`가 비어 있어야 한다. 각 실행은 고유 run ID와 빈 내부 엔진을 만든다. 외부 데몬 설정·방화벽·기존 네트워크 변경이나 prune은 하지 않는다. 환경 정보와 매니페스트는 `provenance.json`, `floci-manifest.txt`, `dind-manifest.txt`, `source-check.json`에 있다.

수업 후보는 **VPC/서브넷 제어면·입력 오류·의존성·EC2 실제 컨테이너 수명주기**다. SG는 opt-in의 실제 필터를 쓸 수 있지만 transport 주소를 다루는 실행 환경 설계가 먼저 필요하다. 라우팅·NACL·NAT·peering의 실제 AWS 패킷 원리를 Floci API 생성 성공만으로 채점하는 코스는 이 실측으로 정당화되지 않는다.
