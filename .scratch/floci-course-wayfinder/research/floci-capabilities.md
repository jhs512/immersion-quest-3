# Floci로 어떤 AWS 학습 목표를 실제로 검증할 수 있는가

- 작성일: 2026-11-09 (KST)
- 성격: 계획용 조사 보고서. 근거와 후보 교육 목표만 정리한다.
- **범위 결정 없음:** 이 문서는 학습자의 학습 범위나 코스·수업 구성을 정하지 않는다. 후보 목록은 판단 재료일 뿐이다.

---

## 0. 요약

- Floci는 MIT 라이선스의 로컬 AWS 에뮬레이터다. 공식 문서는 계정, 인증 토큰, 기능 제한 없이 `http://localhost:4566`에서 AWS 형태의 API를 제공한다고 설명한다. ([README.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/README.md), [LICENSE](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/LICENSE))
- 아래에 해당하는 학습 목표는 API 상태나 Docker 상태로 채점할 수 있는 후보다.
  - S3, SQS, DynamoDB의 데이터 동작
  - IAM 정책 평가(강제 모드를 켠 경우)
  - EC2 인스턴스 수명주기
  - VPC 안 주소 배정
- 기본 VPC Docker 브리지 모드는 SG/NACL 방화벽을 강제하지 않는다. 별도 opt-in SG 기능은 Linux 네트워크 네임스페이스와 nftables로 실제 패킷을 거른다고 문서화돼 있다. 이것도 VPC 라우팅·NACL·NAT·피어링 구현은 아니다. 실제 AWS 가상화·성능·과금·IAM 완전 동등성을 증명하는 환경으로 볼 수 없다. ([docs/services/ec2.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/ec2.md))
- 최신 안정 릴리스 2.4.0의 GitHub 릴리스 자산(assets)은 **비어 있다**. 그래서 문서가 말하는 네이티브 바이너리는 실제로 있는지 확인되지 않았고, 사전 점검이 필요하다.

---

## 1. 근거의 종류: 검토한 것과 직접 확인한 것

| 구분 | 내용 |
|---|---|
| 직접 확인 | [최신 릴리스 API](https://api.github.com/repos/floci-io/floci/releases/latest), [태그 ref API](https://api.github.com/repos/floci-io/floci/git/ref/tags/2.4.0), [커밋 API](https://api.github.com/repos/floci-io/floci/commits/9be236e2890c2042a6bb819f1a9228be996acd90)를 조회했다. 결과는 tag `2.4.0`, published `2026-10-31T22:10:55Z`, commit `9be236e2890c2042a6bb819f1a9228be996acd90`, `assets: []`이다. 릴리스 페이지는 [2.4.0](https://github.com/floci-io/floci/releases/tag/2.4.0)이다. |
| 검토만 함 | 위 커밋 기준 README, LICENSE, 설치·이미지·저장소·멀티 계정 문서, 서비스 문서와 초기화 컨트롤러 소스를 검토했다. 문서의 **주장**과 코드가 표현하는 동작을 읽었으며 실행 결과는 아니다. |
| 하지 않음 | Docker 이미지 pull·실행, AWS CLI/SDK 호출, 실제 AWS 접속, 이미지 digest 조회, 바이너리 다운로드, 코스 구현, 채점기 실행 |

이 보고서에서 "된다"는 표현은 모두 "공식 문서가 그렇게 주장한다"는 뜻이다. 로컬 서비스 동작을 실측한 근거는 없다.

---

## 2. 버전, 릴리스, 재현성

**릴리스 채널.** 공식 문서상 릴리스 이미지는 매월 15일과 말일에, nightly는 매일 발행된다. 같은 날 nightly를 다시 실행하면 dated nightly 태그도 다시 발행된다. 그래서 문서는 재현이 필요하면 릴리스 버전을 고정하라고 권한다. ([docs/configuration/docker-images.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/configuration/docker-images.md))

**태그는 바뀔 수 있다.** 문서 스스로 "태그는 바뀔 수 있으니 믿을 수 있는 검증은 digest(`floci/floci@sha256:...`)로 하라"고 적는다. 서명은 릴리스 이미지에만 있고(cosign keyless, v2.6.3 이상 필요), nightly에는 없다. ([docs/configuration/docker-images.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/configuration/docker-images.md))

**digest는 아직 모른다.** 이번 조사에서는 digest를 조회하지 않았다. 이 문서에 digest 값은 **없다**. `floci/floci:2.4.0` 태그가 Docker Hub에 실제로 있는지도 확인하지 않았다.

**재현성 고정 항목(후보):**

| 고정 대상 | 이유 | 근거 |
|---|---|---|
| `floci/floci:2.4.0` **태그와 digest를 함께** | 태그만으로는 바뀔 수 있다 | [docker-images.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/configuration/docker-images.md) |
| EC2 AMI가 매핑되는 자식 이미지 | AMI ID를 카탈로그(`image-catalog.yaml`)로 `public.ecr.aws/...` 이미지에 매핑한다 | [docs/services/ec2.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/ec2.md) |
| Lambda 런타임 이미지 `public.ecr.aws/lambda/*`, k8s 실행기의 init 이미지(`busybox` 기본) | 함수 실행이 이 이미지들에 의존한다 | [docs/services/lambda.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/lambda.md) |
| AWS CLI, SDK(boto3 등) 버전 | compat 이미지는 CLI와 boto3를 함께 넣지만 버전이 고정되지 않으면 바뀐다 | [docker-images.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/configuration/docker-images.md) |
| Floci CLI(`floci start`) 버전 | Quick Start가 별도 저장소의 CLI를 쓴다 | [README.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/README.md) |
| Docker 엔진 종류와 버전 | VPC 사이 격리는 Docker 데몬이 정한다(아래 4절) | [ec2.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/ec2.md) |

**네이티브 바이너리.** 설치 문서는 "모든 릴리스에 플랫폼별 실행 파일과 `sha256sums.txt`, `.sigstore.json`이 첨부된다"고 주장한다. ([docs/getting-started/installation.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/getting-started/installation.md)) 그러나 실제로 조회한 2.4.0 릴리스의 assets 배열은 비어 있다. 바이너리 경로는 **사용할 수 있는지 확인되지 않았다.** 쓰려면 다운로드, 체크섬, 서명을 먼저 점검해야 한다.

---

## 3. 라이선스와 비용

- MIT 라이선스다. 사용, 수정, 배포, 판매가 무상으로 허용된다. ([LICENSE](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/LICENSE))
- README는 "No account. No auth token. No feature gates"라고 밝힌다. 자격 증명은 비어 있지 않은 아무 값이면 된다(서명 검증 등을 켜지 않은 경우). ([README.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/README.md))
- 학습자가 클라우드 계정이나 결제 수단을 만들 필요가 없다는 점은 문서상 주장이다. 실제 AWS 과금은 발생하지 않지만, 바로 그 이유로 과금 학습에는 쓸 수 없다(8절).

---

## 4. 플랫폼 요건

| 플랫폼 | 문서상 요건과 주의점 | 근거 |
|---|---|---|
| 공통(Docker 방식) | Docker 20.10 이상, `docker compose` v2 플러그인 | [installation.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/getting-started/installation.md) |
| 이미지 아키텍처 | standard와 compat은 `linux/amd64`, `linux/arm64` 멀티 아키텍처다. baseline은 arm64 전용이다 | [docker-images.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/configuration/docker-images.md) |
| LSE가 없는 arm64(Raspberry Pi 4급) | standard 이미지가 `CPU features ... LSE not supported`로 종료되면 `x.y.z-baseline`을 쓴다 | [docker-images.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/configuration/docker-images.md) |
| Windows | 바이너리 표에는 `windows-amd64`만 있고 **Windows arm64용 항목은 문서 표에 없다**. Docker Desktop for Windows에서는 컨테이너 주소에 호스트가 직접 접속할 수 없다 | [installation.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/getting-started/installation.md), [ec2.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/ec2.md) |
| macOS | darwin arm64와 amd64 자산이 있다고 주장한다. 브라우저로 받은 파일은 Gatekeeper 격리를 해제해야 한다(`xattr -d`). Docker Desktop for macOS도 호스트에서 컨테이너 IP로 접속할 수 없다 | [installation.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/getting-started/installation.md), [ec2.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/ec2.md) |
| Linux 바이너리 | glibc 2.34 이상이 필요하다. Alpine(musl), RHEL 8, AL2에서는 실행할 수 없다 | [installation.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/getting-started/installation.md) |
| OrbStack | 공식 문서에 따르면 OrbStack에서는 서로 다른 네트워크의 컨테이너끼리 통신할 수 있다(실측 29.4.0). VPC 경계가 주소 경계에 그친다 | [ec2.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/ec2.md) |
| Lambda 아키텍처 | 기본은 호스트 아키텍처다. 선언한 아키텍처를 따르게 하려면 플래그와 에뮬레이션(QEMU 등)이 필요하다 | [lambda.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/lambda.md) |

**Docker 없이 실행할 때.** 문서는 Lambda, ECS 등은 요청 자체가 실패하고, EC2, RDS 등은 제어면만 남는다고 설명한다. 따라서 컨테이너 기반 채점은 Docker 소켓이 있어야 한다. ([installation.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/getting-started/installation.md), [lambda.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/lambda.md))

---

## 5. 서비스별 충실도

### 5.1 EC2와 VPC: 실제 Docker로 동작하는 부분과 강제되지 않는 부분

- **인스턴스 = 실제 컨테이너.** `RunInstances`는 실제 Docker 컨테이너를 만든다. stop은 `docker stop`, start는 `docker start`, terminate는 `docker rm -f`, reboot는 `docker restart`에 대응한다. 종료된 인스턴스는 1시간 동안 조회할 수 있다. CPU와 메모리는 인스턴스 타입 카탈로그 값으로 제한된다. ([ec2.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/ec2.md))
- **VPC = 실제 Docker 네트워크.** VPC 하나가 Docker 네트워크 하나다(서브넷마다 따로 만들지 않는다). 보고되는 사설 IP는 컨테이너가 실제로 가진 주소다. 같은 VPC 안에서는 서로 통신한다. CIDR이 충돌하면 fallback 대역을 쓰고, 그 사실을 WARN 로그로 남긴다. ([ec2.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/ec2.md))
- **기본 모드의 경계.** VPC Docker 브리지만으로는 SG/NACL을 강제하지 않는다. 기본 브리지 모드의 VPC 사이 격리는 Docker 데몬 규칙에 기대며, 문서는 OrbStack 29.4.0에서 별도 브리지 사이 통신이 가능했다고 보고한다. 이것은 이번 조사의 실측이 아니다. ([ec2.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/ec2.md))
- **별도 SG 패킷 필터 기능.** `FLOCI_NETWORK_SECURITY_GROUP_ENFORCEMENT_ENABLED=true`(기본 false)는 Docker EC2와 ECS awsvpc에 대해 Linux netns+nftables 기본 거부 정책을 만들고, 새 연결의 발신 egress/수신 ingress 및 응답 conntrack을 검사한다고 설명한다. **VPC 라우팅·NACL·NAT·피어링은 에뮬레이트하지 않는다.** rootless Docker와 Windows 컨테이너는 미지원이다. Docker Desktop의 Linux 컨테이너와 Windows 컨테이너를 구별해야 하며, 전자에서 이 기능이 안정적으로 동작하는지는 별도 실측이 필요하다. 호스트에 공개한 포트는 Docker가 보게 되는 출발지 주소에 의존한다. ([ec2.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/ec2.md#security-group-port-publishing), [환경 변수](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/configuration/environment-variables.md))
- **기본 모드의 포트 공개는 방화벽이 아니다.** CIDR 소스 TCP 규칙은 socat 프록시의 호스트 포트를 만들지만 CIDR 값 자체를 제한하지 않는다. SG 강제 모드를 켜면 이 기존 애플리케이션 프록시는 꺼진다. 따라서 localhost 연결 성공만으로 SG 출발지 제한을 배웠다고 채점하면 안 된다. ([ec2.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/ec2.md#security-group-port-publishing))
- **기본 서브넷 공유.** 기본 서브넷 ID는 모든 계정에서 같다. 그래서 같은 데몬 위에서는 계정이 달라도 같은 네트워크를 공유한다. ([ec2.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/ec2.md))
- **vCPU 할당량.** opt-in 기능이다(`FLOCI_SERVICES_EC2_ENFORCE_VCPU_QUOTAS`). 요청을 받을 때 검사할 뿐, 사용량을 예약해 두는 장부는 아니다. ([ec2.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/ec2.md))

### 5.2 IAM: 기본값과 우회 규칙

- **기본은 허용.** 아무 자격 증명이나 받고, 정책을 평가하지 않는다. `FLOCI_SERVICES_IAM_ENFORCEMENT_ENABLED=true`를 줘야 평가기가 동작한다. 이름을 틀리게 쓰면(예: `FLOCI_IAM_STRICT_VALIDATION`) 아무 경고 없이 무시된다. 실제 상태는 시작 배너 `IAM: policy enforcement enabled/disabled`로 확인해야 한다. ([docs/services/iam.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/iam.md))
- **평가 순서(문서 주장).** SCP → 명시적 Deny → identity Allow → 세션 정책 → 권한 경계 → 암묵적 거부. ([iam.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/iam.md))
- **우회 규칙.** 강제 모드에서도 다음은 통과한다. ([iam.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/iam.md))
  - 액세스 키 `test`는 항상 허용된다.
  - IAM 액션으로 매핑할 수 없는 요청은 허용된다.
  - 정책에 매핑되지 않는 세션은 허용된다.
  - 서명 없는 REST 요청(서명 없는 S3 호출 포함)은 검사하지 않는다.
- **인증과 인가의 구별.** `FLOCI_AUTH_VALIDATE_SIGNATURES=true`는 서명 검증만 하고 정책 평가는 하지 않는다(기본 false). S3는 별도로 `FLOCI_SERVICES_S3_ENFORCE_AUTH=true`를 켜면 서명과 버킷 정책·ACL 및 익명 접근을 검사한다. IAM 강제 플래그 하나가 AWS 인증·인가 전체를 대신한다고 설명하면 안 된다. 조건 키도 문서가 열거한 요청 컨텍스트 범위를 개별 확인해야 한다. ([환경 변수](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/configuration/environment-variables.md), [S3](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/s3.md#signature-verification), [IAM](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/iam.md#supported-policy-features))
- **채점 함의.** IAM 거부를 채점하려면 강제 모드 배너 확인, `test`가 아닌 키, 서명된 요청이 모두 필요하다. 서명 없는 S3 요청이 통과한 것을 IAM 판정의 근거로 삼으면 안 된다.

### 5.3 멀티 계정

12자리 AKID가 곧 계정 ID가 되고, 저장소가 계정별로 분리된다. 하지만 문서는 계정 선택이 비밀 키를 가졌다는 증명이 아니므로 "보안 경계로 취급하지 말라"고 명시한다. 학습자를 서로 격리하는 수단으로는 부적합하다. ([docs/configuration/multi-account.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/configuration/multi-account.md))

### 5.4 S3, SQS, DynamoDB, Lambda의 범위와 한계

| 서비스 | 지원(문서 주장) | 한계(문서 주장) | 근거 |
|---|---|---|---|
| S3 | 버킷·객체, 멀티파트, 버전 관리, 정책, presigned URL, 이벤트 알림(SQS/SNS/Lambda) | `RestoreObject`는 202만 돌려주는 스텁이다. Replication은 설정만 저장하고 복제는 하지 않는다. ListBuckets 필터링·페이지네이션은 미구현이다. 알림 대상의 리소스 정책 권한은 검사하지 않는다. 버킷 액세스 로깅·요청자 지불 미지원 | [docs/services/s3.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/s3.md) |
| SQS | 표준/FIFO, 가시성 타임아웃, 롱 폴링(0~20초 검증), DLQ 재처리. 메시지를 소비하지 않고 들여다보는 `GET /_aws/sqs/messages` 제공 | `CancelMessageMoveTask`, `AddPermission`, `RemovePermission`에는 설명이 비어 있어 충실도를 판단할 수 없다 | [docs/services/sqs.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/sqs.md) |
| DynamoDB | 기본 native 백엔드에서 Query/Scan, 트랜잭션, TTL, PITR, 백업 | 선택 사항인 `local` 백엔드는 Amazon DynamoDB Local을 따로 실행해야 한다. 이 백엔드는 `POST /_floci/state/reset`을 409로 거부하고, 복제본·백엔드 간 데이터 이전·`TableId`·태그 검증이 없다 | [docs/services/dynamodb.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/dynamodb.md) |
| Lambda | Docker 런타임 실행(ZIP, 이미지, Runtime API), SQS/Kinesis/DDB Streams 이벤트 소스 매핑, 재시도와 OnFailure | 기본 Docker executor에는 소켓이 필요하다(별도 Kubernetes executor도 있다). 레이어 권한 API와 `InvokeWithResponseStream`이 없다. 코드 서명은 연결만 되고 강제되지 않는다. | [docs/services/lambda.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/lambda.md) |

---

## 6. 초기화와 학습자별 독립 인스턴스

- **저장 모드.** 공개 이미지의 기본 저장 모드는 `memory`라서 재시작하면 상태가 사라진다. 다만 Java 코드의 기본값은 `hybrid`다. 바이너리나 소스로 실행하면 기본값이 다를 수 있으니 `FLOCI_STORAGE_MODE`를 명시해야 한다. ([docs/configuration/storage.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/configuration/storage.md))
- **재시작과 reset은 구별한다.** memory 모드는 Floci 저장소의 재시작 생존 여부를 정한다. 외부 서비스·자식 컨테이너·네트워크·볼륨까지 모두 사라진다는 보장은 아니다. 컨테이너 저장소는 별도 named volume을 쓰는 서비스가 있으므로 초기화 뒤 API 데이터와 Docker 잔여 자원을 함께 확인해야 한다. 이는 실행 검증이 필요한 운영 제안이다. ([storage.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/configuration/storage.md#container-storage-rds-opensearch-msk-ecr))
- **reset 소스 검토.** `POST /_floci/state/reset`은 모든 서비스의 `checkReset()`을 먼저 호출하고, 추적된 컨테이너 teardown, `storageFactory.clearAll()`, 서비스 clear 및 afterReset 순으로 처리한다. 즉 자식 컨테이너 정리를 의도한 구현이 있다. 모든 서비스·볼륨에서 완전한 초기화를 달성한다는 실행 증거는 아직 없다. 외부 DynamoDB Local 백엔드는 이 요청을 HTTP 409로 거부하므로 그 인스턴스를 별도로 초기화해야 한다. ([EmulatorInfoController.java](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/src/main/java/io/github/hectorvent/floci/lifecycle/EmulatorInfoController.java), [dynamodb.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/dynamodb.md#limits))
- **학습자별 격리.** 계정 네임스페이스는 보안 경계가 아니다(5.3). 기본 서브넷 네트워크도 공유된다(5.1). 그래서 학습자마다 **프로세스, 포트, 데이터 경로를 따로 쓰는 독립 인스턴스**가 후보가 된다. 문서상 근거는 다음과 같다. ([installation.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/getting-started/installation.md))
  - 바이너리가 만드는 컨테이너는 `host-<port>` 네임스페이스로 구분된다.
  - 영속 모드에서는 인스턴스마다 `FLOCI_STORAGE_PERSISTENT_PATH`를 달리 줘야 한다.
  - 여러 호스트가 원격 데몬 하나를 공유하면 `FLOCI_DOCKER_RESOURCE_NAMESPACE`를 달리 줘야 한다.
- **하나의 데몬을 공유할 때.** VPC CIDR 충돌은 fallback 대역으로 바뀐다. 그러면 학습자가 선언한 IP와 실제 IP가 달라질 수 있으므로, 채점은 WARN 로그를 확인해야 한다. ([ec2.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/ec2.md))

---

## 7. 후보 교육 목표

아래는 **선택하지 않은 후보**다. 채점 단언은 관찰할 수 있는 값으로 적었다. 공통 사전 점검(9절)에 더해 행마다 필요한 점검을 적었다.

| # | 후보 교육 목표 | 관찰 가능한 채점 단언 | 사전 점검 | 근거 |
|---|---|---|---|---|
| 1 | S3 버킷과 객체의 생성·조회·버전 관리를 이해한다 | `GetObject` 본문이 기대 바이트와 같고 `HeadObject` 크기가 일치한다. ETag를 일반적인 파일 해시로 단정하지 않는다. 버전 관리를 켠 뒤 같은 키를 두 번 PUT하면 `ListObjectVersions`가 2건을 돌려준다 | 저장 모드가 memory인지, 시작할 때 버킷이 0개인지 | [s3.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/s3.md) |
| 2 | SQS 가시성 타임아웃과 재수신을 이해한다 | 첫 수신 뒤 삭제하지 않으면 제한 시간 안에는 재수신되지 않고, 가시성 만료 후 다시 수신할 때 같은 메시지가 오며 수신 횟수가 증가한다. inspection은 관찰용으로만 쓴다 | inspection 엔드포인트 응답 형태 | [sqs.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/sqs.md) |
| 3 | DLQ와 maxReceiveCount를 이해한다 | 수신 횟수를 넘긴 메시지가 DLQ로 옮겨진다. `ListDeadLetterSourceQueues`가 원본 큐를 돌려준다 | 실제 이동 시점(시간 의존 여부) | [sqs.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/sqs.md) |
| 4 | DynamoDB 키 설계와 Query/Scan의 차이를 이해한다 | 파티션 키로 Query한 결과 건수가 기대값과 같다. 조건부 쓰기가 `ConditionalCheckFailedException`을 낸다 | native 백엔드인지(local 아님) | [dynamodb.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/dynamodb.md) |
| 5 | IAM 명시적 Deny가 Allow보다 우선함을 이해한다 | `s3:*` Allow와 특정 버킷 Deny를 가진 사용자의 서명된 요청이 403 `AccessDenied`를 받는다. 같은 사용자의 다른 버킷 요청은 성공한다 | 배너가 enforcement enabled인지, `test` 키를 쓰지 않는지, 서명된 요청인지 | [iam.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/iam.md) |
| 6 | 권한 경계가 허용 범위를 줄임을 이해한다 | 경계를 붙이기 전에는 성공하던 호출이 붙인 뒤 거부된다 | 5와 같음 | [iam.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/iam.md) |
| 7 | EC2 인스턴스 상태 전이를 이해한다 | `stop-instances` 뒤 상태가 `stopped`이고 대응하는 Docker 컨테이너가 Exited다. terminate 뒤에는 컨테이너가 없다 | Docker 소켓, AMI 매핑 이미지를 pull할 수 있는지 | [ec2.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/ec2.md) |
| 8 | 서브넷 CIDR과 사설 IP 배정을 이해한다 | 보고된 `PrivateIpAddress`가 서브넷 CIDR 안에 있고 컨테이너가 실제로 가진 IP와 같다. WARN fallback 로그가 없다 | 데몬에서 CIDR이 충돌하지 않는지 | [ec2.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/ec2.md) |
| 9 | 같은 VPC 안의 통신을 확인한다 | 같은 VPC의 두 인스턴스가 컨테이너끼리 사설 IP로 통신된다(호스트에서는 확인하지 않음) | 컨테이너 안에서 명령을 실행할 수단 | [ec2.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/ec2.md) |
| 10 | S3 이벤트 → SQS 연결을 이해한다 | 설정 직후 `s3:TestEvent`가 들어오고, PUT 뒤 `Records`가 있는 메시지가 큐에 있다 | 대상 큐를 미리 만들었는지 | [s3.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/s3.md) |
| 11 | SQS → Lambda 이벤트 소스 매핑을 이해한다 | 메시지를 보낸 뒤 함수의 부작용(예: DDB 항목)이 생기고, 성공 처리 후 메시지가 삭제된다. 단순 빈 Receive 응답은 삭제 증거로 쓰지 않는다 | Docker 소켓, 런타임 이미지 digest, 호스트 아키텍처 | [lambda.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/lambda.md) |

**SG 후보는 별도 조건부 실험이다.** 기본 모드에서는 `DescribeSecurityGroups`의 규칙 상태만 검증할 수 있다. opt-in SG 모드에서는 관리 컨테이너 사이 허용/거부와 응답 흐름을 관찰하는 후보가 생긴다. 동일 연결 재사용·conntrack·출발지 주소 변환을 통제하고, 규칙 변경 전후 실제 새 연결로 대조해야 한다. 지원 호스트·helper 이미지·필터 준비 상태를 실측하기 전에는 채점 가능하다고 확정하지 않는다. NACL과 VPC 라우팅은 이 SG 실험의 검증 대상이 아니다. ([ec2.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/ec2.md#security-group-port-publishing))

---

## 8. Floci로 검증할 수 없어 보류하는 것

| 항목 | 이유 | 근거 |
|---|---|---|
| 실제 AWS 패킷 라우팅, IGW/NAT 경로, NACL·피어링 | 기본 모드는 Docker 브리지이며 opt-in SG 패킷 필터도 이 기능들은 구현하지 않는다 | [ec2.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/ec2.md) |
| 하이퍼바이저와 가상화 특성(Nitro, 인스턴스 스토어 등) | 인스턴스가 컨테이너다 | [ec2.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/ec2.md) |
| 실제 운영 성능, 지연, 처리량 | 로컬 메모리 에뮬레이터다. 문서의 ~24ms, ~13MiB는 Floci 자체의 수치다 | [installation.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/getting-started/installation.md) |
| 과금과 비용 최적화 | 과금이 없다 | [README.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/README.md) |
| IAM의 AWS 완전 동등성 | 기본값이 허용이다. `test` 키 우회, 매핑 불가 액션 허용, 서명 없는 REST 미검사가 있다 | [iam.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/iam.md) |
| 계정 간 보안 격리 | AKID 기반 네임스페이스일 뿐이다 | [multi-account.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/configuration/multi-account.md) |
| S3 복제, Glacier 복원, 액세스 로깅 | 설정만 저장하거나 스텁이거나 미지원이다 | [s3.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/s3.md) |
| Lambda 응답 스트리밍, 코드 서명 강제 | 구현되지 않았다 | [lambda.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/lambda.md) |
| DynamoDB 글로벌 테이블 복제(local 백엔드) | 거부된다 | [dynamodb.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/dynamodb.md) |

---

## 9. 공통 사전 점검 목록(채점기 구현 전)

1. `floci/floci:2.4.0`이 실제로 있는지 확인하고, `docker buildx imagetools inspect`로 **digest를 기록**한다. cosign(v2.6.3 이상)으로 서명을 검증한다. ([docker-images.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/configuration/docker-images.md))
2. 네이티브 바이너리를 쓴다면 2.4.0에 자산이 비어 있다는 점을 먼저 해결한다. 다른 릴리스에 자산이 있는지, `sha256sums.txt`와 `.sigstore.json`이 있는지 확인한다. ([installation.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/getting-started/installation.md))
3. 자식 이미지(AMI 매핑, `public.ecr.aws/lambda/*`)와 CLI/SDK 버전을 고정한다.
4. 시작 로그에서 IAM 강제 모드 상태, Docker 연결 경고, CIDR fallback WARN을 확인한다. ([iam.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/iam.md), [ec2.md](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/docs/services/ec2.md))
5. Windows, macOS(Docker Desktop), Linux, arm64, OrbStack에서 같은 채점이 같은 결과를 내는지 플랫폼별로 실측한다.
6. 초기화 뒤 문제별 소유 자원이 제거되고 기본 seed만 남았는지 API 목록과 Docker 잔여 자원(컨테이너, 네트워크, 볼륨)으로 확인한다. 다른 학습자 자원과 무관한 범위에서만 정리한다.
7. 준비 상태는 실패하고, 정답은 통과하고, 흔한 오답은 거절되는지 실제 채점기로 확인한다.

---

## 10. 결정하지 않은 것

- 어떤 코스나 수업에 Floci를 쓸지, 위 후보 중 무엇을 교육 목표로 채택할지는 **결정하지 않았다.**
- Docker 방식과 바이너리 방식 중 무엇을 쓸지, 학습자 인스턴스를 어디에 둘지(로컬인지 서버인지)도 정하지 않았다.
- 이 보고서의 동작 서술은 모두 공식 문서의 주장이다. 직접 실행해 확인한 것은 GitHub 릴리스·태그·커밋 메타데이터 조회뿐이다. Docker 서비스 동작은 미검증이다.

작성 흐름: 공식 자료 수집 후 Claude Code CLI로 초안을 만들고, Codex가 출처와 대조하여 SG opt-in 기능·초기화 소스·SQS 재수신 판정·S3 본문 판정을 교정했다. 코스 구현·배포·실제 AWS 작업은 하지 않았다.
