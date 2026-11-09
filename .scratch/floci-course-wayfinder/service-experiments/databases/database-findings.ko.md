# Floci 데이터베이스 실험과 교육 범위 판단

이 문서는 실제 로컬 실험으로 데이터베이스 수업의 가능 범위를 판단하는 연구 자료다. 수업 본문·채점기·배포 구현은 만들지 않았다. Windows 11 / Docker Desktop 29.8.1 amd64에서 실행했으며 Mac 실행 증거는 없다.

## 판정 근거

`database_lab.py`가 모든 AWS CLI 요청에 `http://127.0.0.1:45671`을 지정한다. 실행마다 빈 설정 파일, 가짜 `test` 키, 메타데이터 비활성화를 사용한다. 외부 AWS API 호출은 없다. 외부 통신은 공식 문서와 공개 컨테이너 이미지 취득뿐이다.

호스트 Docker 소켓을 넘기지 않고 별도 privileged DIND 안에서 Floci와 PostgreSQL을 실행한다. 바깥 컨테이너는 CPU 4개·메모리 6GiB·PIDs 2048, Floci는 CPU 2개·2GiB·PIDs 512다. PostgreSQL은 생성 후 Docker update로 CPU 1개·512MiB·PIDs 256을 적용하고 재생성 때 다시 적용한다. **생성 시작 순간부터 개별 DB 제한이 자동 적용되는 Floci 기능은 검증하지 않았다.** 그 구간에는 바깥 DIND 제한이 적용된다. privileged DIND는 호스트와 동일한 보안 경계가 아니므로 연구용 명시적 구성으로 기록한다.

Floci 2.4.0 OCI 인덱스는 `sha256:5ee85db604c4aa74ac76e07ea5cc83086f37bb472bf3dbb97e34019e48efae9c`, DIND 29.0.1은 `sha256:ecac43e78380d9b9d3bd24f0ab42b370f6391a1a06a66065c10a00b9d6d57a3e`다. PostgreSQL 공식 `postgres:16-alpine` 취득 시 해석된 인덱스는 `sha256:aa6cb33cf4c19c765cefcf48d96176258800870a9a1e930ad126200f9d825139`이며 SQL 실제 버전은 **PostgreSQL 16.15**다. 호스트 캐시를 임시 tar로 저장·전송·load하여 내부 레지스트리 pull을 피했다. Desktop의 인덱스 ID와 DIND의 config ID는 다르므로 전체 RootFS 레이어와 아키텍처를 비교하고 대응을 기록한다. tar는 삭제하며 커밋하지 않는다.

## DynamoDB: API 에뮬레이션으로 확인한 범위

`mq-floci-db-20261109212521/ddb-summary.json`, `events.json`과 각 `request-*.json`이 근거다.

| 확인 항목 | 실제 관찰 |
|---|---|
| 생성·상태·키 | 문자열 파티션 키 `pk` + 숫자 정렬 키 `sk`; ACTIVE 확인. 숫자 pk와 누락 sk는 ValidationException으로 거절 |
| 데이터 CRUD | A/1=10, A/2=20, B/1=30을 저장·조회; A/1 조건부 수정 후 11; A/2 삭제 후 Item 없음 |
| Query와 Scan | `pk=A AND sk>=2` Query는 1개; `qty>=20` Scan은 전체 3개를 읽고 2개 반환. 정렬 키만 주는 Query 거절 |
| 조건 실패의 보존 | `qty=10` 조건 수정은 성공; 기존 A/1에 `attribute_not_exists(pk)` 쓰기는 실패하고 11 유지 |
| 작은 트랜잭션 | T/1=40 Put + A/1=11 ConditionCheck 성공. T/1=99 Put + A/1=999 조건은 실패하고 T/1=40 유지 |
| 선택 초기화 | books 삭제 후 sibling A/1=77 유지; books 조회는 ResourceNotFoundException; 같은 이름 재생성 후 기존 항목 없음 |
| 프로세스 재시작 경계 | `FLOCI_STORAGE_MODE=memory`에서 Floci 재시작 후 TableNames=[] |

이 결과는 Floci의 인프로세스 DynamoDB API 구현에 대한 증거다. 실제 DynamoDB 서버 프로세스, 운영 규모의 처리량·과금·지연·분산 일관성·IAM 격리를 검증한 것은 아니다. 메모리 모드 실험으로 영속 저장 모드의 복구·내구성을 주장하지 않는다. 작은 Put+ConditionCheck 원자성은 확인했지만 전체 트랜잭션 조합·페이지 나누기·인덱스·Streams를 포괄하지 않는다.

## RDS PostgreSQL: 관리 API와 실제 SQL을 함께 확인한 범위

첫 서비스 실행에서 실제 SQL CRUD·제약·트랜잭션·중지/시작 데이터 보존까지 통과했다. 스냅샷 복원 뒤 컨테이너 이름을 인스턴스 식별자로 찾는 **하네스 오류**가 발생했으며 `rds-failure.json`에 그대로 남겼다. API는 DbiResourceId 기반 이름을 쓰므로 소유 컨테이너 집합의 차이로 찾도록 수정했다. 이는 Floci 기능 실패로 집계하지 않는다. 복원 데이터 검증을 위한 RDS 집중 반복 결과는 아래 최종 증거 표에 기록한다.

SQL은 소유 DB 컨테이너의 psql로 실행한다. 로컬 소켓 경로와 Floci 인증 프록시 경로를 구별한다. 프록시는 내부 DIND 호스트 네트워크에 있고 DB 클라이언트는 bridge에 있으므로 광고된 loopback 대신 **내부 bridge gateway + 광고 포트**를 쓴다. 이 경로는 호스트에 노출하지 않는다. 실제 SQL 접속 성공이 확인되어야 API의 available을 준비 완료로 판단한다.

최종 실행 `mq-floci-db-20261109212654`는 exit 0으로 끝났다. `rds-summary.json`, `events.json`, `rds-cgroup-before.json`, `rds-cgroup-restarted.json`이 근거다.

| 확인 항목 | 실제 관찰 |
|---|---|
| 실제 프로세스·버전 | postgres와 checkpointer/walwriter 등 실제 프로세스 확인; SELECT version()은 PostgreSQL 16.15 |
| 개별 자원 제한 | cgroup memory.max=536870912, cpu.max=`100000 100000`, pids.max=256; 재시작 뒤 동일 |
| 프록시 경로 | 직접 경로와 프록시의 pg_control_system().system_identifier=7706147333637394472 일치; 직접 삽입한 qty10을 프록시에서 조회 |
| CRUD·제약 | id1 qty10 삽입·조회; 중복 PK와 qty=-1 CHECK 위반은 psql exit1; 다시 조회한 qty10 유지; id2 삽입·삭제 후 한 행 |
| 실제 트랜잭션 | BEGIN/UPDATE20/ROLLBACK 뒤 10, BEGIN/UPDATE30/COMMIT 뒤 새 psql 세션에서 30 |
| 중지·시작 | stopped 뒤 실제 backend 컨테이너가 없어 psql 실행 실패; 시작 뒤 재생성된 DB에 재접속하여 qty30 확인 |
| 스냅샷·복원 | qty30 상태의 스냅샷 뒤 id3=55 추가; 새 인스턴스 복원 SQL에서 qty30 존재, id3 개수0 |
| 선택 삭제 | 원본 인스턴스를 삭제한 뒤 복원 인스턴스에서 qty30 조회 성공; 복원 인스턴스·스냅샷도 API로 삭제 |

스냅샷은 이 한 PostgreSQL 인스턴스의 로컬 복원 내용만 검증했다. 관리형 AWS 백업의 지속 시간·암호화·장애 복구·자동 보존 정책 검증으로 확장하지 않는다. 중지 상태에서는 기존 컨테이너가 삭제되므로 장시간 유지된 SQL 연결의 실패 양상이나 자동 재연결 라이브러리까지 시험한 것은 아니다. FK·격리 수준·경합·복제·HA와 잘못된 비밀번호 거절도 이번 검증 범위에 없다.

## 재시도와 정리 감사

- `mq-floci-db-20261109212444`: 서비스 실행 전 이미지 전송 검증 오류. Desktop 인덱스 ID를 DIND config ID로 간주해 tag가 실패했다. 레이어·아키텍처 검증으로 수정했다.
- `mq-floci-db-20261109212521`: DynamoDB 전체 및 RDS 중지/시작까지 검증. 복원 인스턴스의 컨테이너 이름 탐색 오류를 보존했다.
- `mq-floci-db-20261109212654`: RDS 집중 반복 전체 통과. DynamoDB 전체를 불필요하게 반복하지 않았다.

모든 시도에서 finally 정리 후 호스트 컨테이너 ID·네트워크·볼륨 목록이 실행 전과 같았다. 기존 중지 컨테이너와 볼륨을 보존했다. `audit_database_evidence.py`는 AWS 명령의 전용 loopback endpoint, 바깥 컨테이너의 단일 loopback 공개 포트, 전용 볼륨만 장착, 실행별 재고 동일성, DB 실험 소유 자원 부재, 포트 반환과 알려진 자격증명 패턴 부재를 검증한다. 알려진 패턴 검사는 임의의 비밀값이 전혀 없다는 형식적 증명은 아니다. 가짜 실습 비밀번호는 증거에 의도적으로 남는다. 공개 이미지 캐시는 보존하며 기존 자원을 지우는 prune은 쓰지 않았다.

## 교육 목표·선수·순서 제안

사용자가 승인한 VPC/EC2 → S3 이후 후보를 판단하는 자료이며 이후 순서를 확정하지 않는다. Lambda를 먼저 채택하더라도 DB 수업의 도입 예제는 Lambda 구현에 의존하지 않게 준비할 수 있다.

1. **DynamoDB 도입 목표:** 키를 정하면 원하는 항목을 찾는 방법과 필요한 조회 조건이 달라진다는 점을 설명하고 관찰한다. 준비된 CLI에서 키 값 한두 개를 바꾸고 GetItem → Query → Scan 출력의 차이를 비교한다. 선수는 JSON의 문자열/숫자, CLI 요청과 응답, 키로 항목을 구분하는 개념이다. 기본 CRUD가 익숙해진 뒤 조건부 쓰기, 마지막으로 작은 트랜잭션을 선택 심화로 둔다. 첫 수업부터 인덱스·Streams·Lambda·VPC를 함께 넣지 않는다.
2. **관계형 DB 도입 목표:** 표의 열·행과 제약으로 잘못된 상태를 막고 여러 변경을 트랜잭션으로 함께 확정하거나 되돌린다. 준비된 SQL 연결에서 qty 하나를 바꾸어 정상 수정 → 음수 거절 → 원래 값 확인 → ROLLBACK/COMMIT을 비교한다. 선수는 기본 SELECT/INSERT/UPDATE/DELETE와 행 식별자이며, SQL이 처음이면 이를 앞 스텝에서 최소 예제로 설명한다. 접속 비밀번호·DB 생성·포트 설정은 준비 자료가 제공한다.
3. **DB 순서 판단:** 추가 SQL 선수가 없는 학습자에게는 API 조작이 작은 DynamoDB를 먼저 두고 RDS로 제약과 트랜잭션을 비교하는 구성이 가능하다. 이미 SQL을 배운 학습자라면 RDS → DynamoDB 순서도 자연스럽다. 이 실험은 어느 순서가 학습 효과가 더 큰지 평가하지 않았다. 실제 코스의 SQL 선수 여부를 확인해 루트 의사결정에서 정한다.
4. **운영 심화의 경계:** 중지/시작과 로컬 스냅샷 복원은 관찰 가능한 선택 실습이다. Multi-AZ, 장애 전환, 리드 레플리카, 관리형 백업 SLA, AWS VPC 데이터 경로를 성공한 기능처럼 가르치지 않는다. 메타데이터 필드의 존재만으로 기능 증거를 만들지 않는다.

한 수업은 한 목표, 한 스텝은 새 개념 하나를 유지한다. 코딩 문제는 독립된 준비 데이터로 시작하며 다른 문제의 DB나 앞 수업 결과를 요구하지 않는다. 잘못된 키·조건·제약이 거절될 때 데이터가 보존되는지를 실제로 확인하는 문제가 이 실험에서 검증 가능한 평가다.

## 일차 자료

- [DynamoDB core components](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.CoreComponents.html): 테이블·항목·기본 키의 공식 개념.
- [DynamoDB transaction APIs](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/transaction-apis.html): AWS의 트랜잭션 의미와 제약. 이 실험의 작은 조합은 전체 AWS 호환성 검증이 아니다.
- [PostgreSQL 16 constraints](https://www.postgresql.org/docs/16/ddl-constraints.html), [PostgreSQL transactions tutorial](https://www.postgresql.org/docs/current/tutorial-transactions.html): 제약과 BEGIN/COMMIT/ROLLBACK의 공식 의미.
- [RDS stopping a DB instance](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_StopInstance.html): 실제 AWS 운영 의미와 로컬 실험의 경계를 구분할 자료.
- [Floci pinned RDS service](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/src/main/java/io/github/hectorvent/floci/services/rds/RdsService.java), [RDS container manager](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/src/main/java/io/github/hectorvent/floci/services/rds/container/RdsContainerManager.java), [EmulatorConfig](https://github.com/floci-io/floci/blob/9be236e2890c2042a6bb819f1a9228be996acd90/src/main/java/io/github/hectorvent/floci/config/EmulatorConfig.java): mock 모드와 실 DB 모드, 엔진 이미지 선택, 소켓 부재 시 available 메타데이터만 존재할 수 있는 구현을 확인했다. 이 때문에 실제 SQL을 독립 판정 기준으로 사용했다.

## 실행자와 검증

기본 Claude 실행자 정책에 맞춰 직접 `claude.exe -p`에 제한된 읽기 전용 계획 검토를 맡겼다(`claude-plan-review.txt`). 별도 브리지는 제거된 상태였다. 검토의 보완점 중 실제 SQL 준비, 조건 실패 데이터 보존, 재생성 제한 재적용, 프록시 실제 경로, 스냅샷 뒤 표식 비교를 반영했다. 가짜 키로 실제 AWS에 음성 대조 요청하자는 제안은 로컬 전용 범위에 맞지 않아 실행하지 않았다. 하네스와 연구 산출물은 사용자가 승인한 Codex 파일 작성 도구로 작성했고 결과를 직접 검증했다. 승인 정책을 바꾸지 않았다.
