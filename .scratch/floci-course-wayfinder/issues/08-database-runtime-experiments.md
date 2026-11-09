# DynamoDB와 RDS의 실제 데이터 동작 중 무엇을 수업에 쓸 수 있는가

Labels: wayfinder:research
Type: research
Status: resolved
Assignee: floci_database_lab
Blocked by: 01, 06
Parent: [Floci를 활용한 MQ 클라우드 실습의 적용 경로](../map.md)

## Question

Floci의 DynamoDB와 Docker 기반 RDS PostgreSQL을 구분해 실제 데이터 저장·읽기·갱신·실패 조건을 검증한다. DynamoDB는 키·조건부 쓰기·질의·원자성 등 범위를 작게 나누고, RDS는 인스턴스 상태뿐 아니라 실제 SQL 접속·제약·트랜잭션·수명주기를 확인한다. 데이터베이스 공통 원리와 AWS 관리형 서비스 모사 범위를 구분해 수업 후보를 정한다.

## Comments

다른 서비스 실험과 호스트 자원 검증이 섞이지 않도록 Docker 실행은 순서대로 한다. DB 연구 에이전트는 문서·하네스 준비 후 주 에이전트의 실행 시작 메시지를 기다린다. 실제 AWS나 기존 DB·사용자 자격 증명은 사용하지 않는다. 준비·정답·흔한 오답 상태를 서비스 응답과 실제 데이터로 구분하고 선택 삭제·격리·정리를 기록한다.

## Answer

2026-11-09 해결. DynamoDB의 복합 키·자료형 검증, CRUD, Query/Scan, 조건부 수정과 조건 실패 시 값 보존, 작은 트랜잭션 성공과 실패 시 원자적 보존을 확인했다. 테이블 선택 삭제·재생성은 다른 테이블을 보존했고, 명시적 memory 모드의 Floci 재시작은 데이터를 초기화했다. 이것은 DynamoDB 전체 분산 동작이나 영속 모드를 검증한 결과가 아니다.

RDS는 API 상태만 보지 않고 실제 PostgreSQL 16.15와 SQL·프록시 연결을 확인했다. CRUD·PK/CHECK 거절·COMMIT/ROLLBACK, stop/start 후 자료 보존, 스냅샷 시점의 실제 값 복원과 이후 삽입 행 부재, 원본 삭제 후 복원본 독립성을 검증했다. 프록시는 내부 Docker gateway와 광고 포트를 사용하는 실험 환경의 주소 조정이 필요했다.

초기 이미지 식별자 비교와 복원 컨테이너 식별 가정의 하네스 오류를 보존하고 수정 후 재실행했다. 세 시도 모두 실험 전후 기존 컨테이너·네트워크·볼륨 목록이 동일했다. 주 에이전트도 60개 AWS CLI 요청이 모두 명시적 loopback endpoint임을 재계산했고 최종 DB 소유 자원이 없음을 확인했다.

DB별 생성 시점의 자동 자원 제한은 검증하지 않았다. 측정된 CPU·메모리·PID 제한은 수동 적용 후의 값이며, `--cgroupns=host`에서 외부 DIND 한도가 내부 자식 전체의 합산 한도라고 주장하지 않는다. 실제 AWS의 HA·failover·관리형 백업 내구성·IAM·VPC 보안을 입증하지 않았다.

Assets: [DynamoDB·RDS 실제 실행 보고서](C:/Users/jangk/Documents/Codex/2026-10-12/immersion-quest-floci-databases-20261109/.scratch/floci-course-wayfinder/service-experiments/databases/database-findings.ko.md), [증거 감사](C:/Users/jangk/Documents/Codex/2026-10-12/immersion-quest-floci-databases-20261109/.scratch/floci-course-wayfinder/service-experiments/databases/audit.json).

Remote context: [불변 연구 자료](https://github.com/jhs512/immersion-quest-3/blob/f6bed92034f62b83e66c5d3677177ae152542318/.scratch/floci-course-wayfinder/service-experiments/databases/database-findings.ko.md), branch `research/floci-databases-20261109`. 연구 자료만 commit/push했으며 PR·병합·운영 배포는 하지 않았다.
