# VPC·서브넷·EC2 구성과 실제 통신은 어디까지 일치하는가

Labels: wayfinder:research
Type: research
Status: resolved
Assignee: floci_windows_lab
Blocked by: 01, 02
Parent: [Floci를 활용한 MQ 클라우드 실습의 적용 경로](../map.md)

## Question

고정한 공식 안정 Floci 이미지와 로컬 Docker를 사용해 VPC·서브넷·인스턴스를 구성하고 실제 주소와 통신을 측정한다. 같은 VPC/다른 VPC, 올바른/잘못된 서브넷, 라우팅·게이트웨이·NAT·NACL·SG 설정 전후, 재시작·정리 결과를 비교해 수업에서 검증할 수 있는 범위와 모사 한계를 구분한다. SG 선택 기능은 별도 조건으로 비교하며 실패를 AWS 동작의 증거로 해석하지 않는다.

## Comments

사용자가 문서 설명 대신 충분한 실제 실험을 요청했다. Windows Docker Desktop Linux engine에서 시작하며 Mac 실행 가능 여부도 확인한다. 기존 자원 이름과 네트워크는 보존하고 실험별 이름·라벨·CIDR·자원 ID를 기록한다. 시스템 전체 prune, Docker 재시작, 호스트 방화벽/SSH 변경, 실제 AWS 호출을 하지 않는다. 로컬 API 호출은 명시적인 loopback endpoint와 가짜 자격 증명만 사용한다.

### 사전 점검에서 확인한 조건

- Windows Docker Desktop Linux engine 29.8.1, x86_64가 응답한다. 점검 시 실행 중인 컨테이너는 없고 기존 `mq3-gitlab-6afa409d-ci` 네트워크는 보존 대상이다.
- Mac은 기존 LAN·Tailscale SSH 경로 모두 연결 시간 초과로 현재 접근할 수 없다. Mac 결과는 검증 완료로 보고하지 않는다.
- 공식 Floci 2.4.0 이미지 pull 성공. 실험 에이전트가 확인한 digest는 `sha256:5ee85db604c4aa74ac76e07ea5cc83086f37bb472bf3dbb97e34019e48efae9c`이며, 최종 증거 파일의 inspect 결과와 대조한다.
- EC2 SSH 호스트 포트 자동 공개를 기존 호스트 엔진에 직접 적용하지 않도록 전용 Docker-in-Docker 엔진을 검토한다. 외부에 공개하는 것은 명시적인 loopback Floci API뿐이며 Docker daemon/SSH 포트는 호스트에 공개하지 않는다.
- 중첩 Linux 엔진에서 측정한 통신 결과는 그 토폴로지의 결과이다. 직접 Docker Desktop 네트워크나 Mac에서의 결과로 확대하지 않는다.

### 주 에이전트의 독립 확인

- 호스트 Docker context와 daemon ID가 실험 에이전트의 대상과 일치함을 확인했다.
- 실행 중 외부 실험 컨테이너의 `HostConfig.PortBindings`를 직접 읽어 Floci API의 `127.0.0.1:45669` 바인딩 한 개뿐임을 확인했다. SSH·Docker daemon 호스트 포트는 없었다.
- 주 실행 `mq-floci-win-20261109203651`의 47개 관찰과 210개 명령 기록을 확인했다. 이 숫자는 모두 성공했다는 뜻이 아니다. 의도한 실패와 모사 한계의 관찰이 포함된다.
- 같은 실행의 AWS CLI 호출 81개 모두 명시적인 loopback endpoint를 사용했다. 실제 AWS endpoint를 사용하는 호출은 없었다.
- 같은 실행의 실험 전후 호스트 컨테이너 목록 4개, 네트워크 목록 4개, 볼륨 목록 39개가 JSON 기준 동일했다. 이는 기존의 정지된 컨테이너와 사용자 자원이 보존됐다는 근거이다.
- 원래 중지 관찰은 짧은 대기 후 아직 실행 중인 비동기 상태였다. 사용자에게 즉시 정정했고 원시 관찰을 바꾸지 않은 채 실제 정지 완료를 기다리는 별도 검증을 진행한다.
- 내려받은 임시 소스 폴더의 재귀 삭제는 자동 승인 정책에서 일반적인 차단 메시지로 거절됐다. 다른 방법으로 우회 삭제하지 않고 로컬에 남기며 연구 커밋에서 제외한다. 실행 중인 컨테이너·네트워크·볼륨의 소유 자원 정리와는 별개이다.

## Answer

2026-11-09 해결. 7회 실행 중 환경·하네스 오류를 보존한 부분 실행 4회와 완료 실행 3회(주 실험, 깨끗한 양방향 피어링, 비동기 수명주기 보강)를 구분했다. 완료 실행에는 총 58개 관찰 레코드가 있으며, 이를 58개 통과 테스트라고 세지 않는다. 전체 637개 명령 이벤트와 AWS CLI 208개 호출이 기록됐다. 주 에이전트도 집계를 재계산했고 AWS 호출 모두 명시적인 loopback endpoint임을 확인했다.

### 검증된 범위

- VPC·서브넷 생성/조회, 잘못된 CIDR·예약/범위 밖 주소 거절, 자원 의존성에 따른 삭제 순서는 실제 동작했다.
- 기본 모드의 API 사설 IP와 실제 VPC Docker IP가 일치했으며 같은 서브넷 및 같은 VPC의 다른 서브넷 간 HTTP marker 통신이 성공했다. 다른 주소 대역에서도 기본 결과를 재현했다.
- 다른 VPC의 사설 IP 통신은 실패했으나 공통 Docker bridge IP로 같은 대상에 도달했다. 전체 격리 보장과 구분해야 한다.
- Route table·IGW·NAT 상태를 변경해도 관찰한 커널 경로와 통신 결과는 변하지 않았다. NAT의 SNAT와 인터넷 출구는 측정하지 않았다.
- NACL deny-all을 소스 서브넷에 연결해도 다른 서브넷 통신이 계속 성공했다. 동일 서브넷 통신은 NACL의 경계 동작을 판단하는 근거로 쓰지 않았다.
- 양방향 피어링 경로·기본 허용 NACL을 별도로 구성한 보강 실험에서도 사설 IP 통신은 열리지 않았다.
- SG 선택 모드는 실제 transport IP에서 ingress·egress 각각 deny→allow→revoke→restore 효과를 보였다. 그러나 API가 알려준 논리 사설 IP는 허용 후에도 연결되지 않아 이 토폴로지에서 그 주소를 그대로 쓰는 학습 환경은 미해결이다.
- 실제 stopped 상태와 Docker Running=false까지 기다린 보강 실험에서 통신 차단, start 후 시험 서버 재기동에 따른 복구, terminate 후 실제 컨테이너 제거를 확인했다. 이전의 짧은 대기 관찰은 덮어쓰지 않았다.

### 판정과 한계

수업 후보는 VPC·서브넷의 구성·입력 검증·의존성·EC2 수명주기다. AWS의 실제 라우팅·NACL·NAT·피어링을 Floci API 생성 성공만으로 가르치거나 채점할 근거는 없다. SG는 실제 필터 효과가 있지만 주소 매핑과 실행 환경 설계를 먼저 해결해야 한다. 첫 수업 순서와 CLI·SDK 선택은 여전히 사용자 결정 사항이다.

결과는 Windows Docker Desktop에 올린 격리된 Linux DIND 엔진에 한정한다. Mac은 SSH에 응답하지 않아 미검증이며 직접 Docker Desktop 네트워크의 동작으로 일반화하지 않는다. MQ 실행기나 수업 콘텐츠를 구현하지 않았다.

모든 실행의 호스트 컨테이너·네트워크·볼륨 전후 차이는 없고 최종 실험 소유 자원도 없다. 이미지 캐시와 자동 삭제가 차단된 로컬 임시 소스는 남겼다. 비밀 형태 패턴과 endpoint 감사 결과를 별도 보존했다.

Assets: [Windows Floci 실제 실험 보고서](C:/Users/jangk/Documents/Codex/2026-10-12/immersion-quest-floci-vpc-experiments-20261109/.scratch/floci-course-wayfinder/experiments/windows-floci-lab.md), [증거 감사](C:/Users/jangk/Documents/Codex/2026-10-12/immersion-quest-floci-vpc-experiments-20261109/.scratch/floci-course-wayfinder/experiments/audit.json).

Remote context: [불변 연구 자료](https://github.com/jhs512/immersion-quest-3/blob/0cb94f9d19c4a25cbf0d2e845ee99cccf44d7a7a/.scratch/floci-course-wayfinder/experiments/windows-floci-lab.md), branch `research/floci-vpc-experiments-20261109`. 연구 자료만 commit/push했으며 PR·병합·운영 배포는 하지 않았다.
