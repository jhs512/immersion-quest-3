# DB 기초 선수 개념과 실제 실행 경로 보강

2026-10-26. 기존 수업 ID와 진도는 보존한다. 수업별 문제 수를 맞추는 작업이 아니라, SQL을 처음 보는 학생에게 없던 첫 경험과 재실행 결함을 보강한다.

## 발견과 변경

기존 SQL 기초는 첫 문제에서 SELECT/FROM/ORDER BY를 함께 요구하고, 이후 AND/OR·NULL·집계·UPDATE로 넘어갔다. 표를 만드는 일, 행을 저장하는 일, WHERE만으로 한 행을 고르는 일, 식별자와 참조를 처음 관찰하는 단계가 없었다. 이 부분이 제약·JOIN·JDBC의 선수 개념 공백이었다.

SQL 기초를 6개에서 18개로 보강했다. 원래 6개 스텝과 단원 ID는 유지하고, 새 스텝에만 새 ID를 부여했다.

1. 왜 데이터를 프로그램 밖에 보관하는지, DB와 SQL·행·열의 역할
2. 모든 열 → 필요한 두 열 → WHERE 한 조건 → ORDER BY 한 기준
3. 기존 조회 → NULL → AND → 같은 가격의 정렬과 LIMIT
4. COUNT(*)와 COUNT(열) → SUM → 합계가 없는 경우의 COALESCE
5. CREATE TABLE의 자료형 → INSERT → UPDATE → DELETE
6. 동명이인의 식별자 → 주문 번호와 회원 참조 번호
7. 최종 도전: 다른 상품을 보존하고 재고 한 행만 차감

CREATE에서 사용하는 INSERT는 제공된 관찰 코드임을 밝히고 바로 다음 문제에서 직접 작성한다. INSERT 문제는 실제 첫 MySQL 클라이언트를 종료한 뒤 두 번째 클라이언트로 저장 행을 읽는다. DB 서버를 종료하거나 파일로 저장했다는 실험은 하지 않았으며 그렇게 설명하지 않는다.

## 후속 수업의 경계

기존 과정 순서와 선수 관계는 유지한다: Docker → SQL 기초 → 제약 → JOIN/트랜잭션 → H2 → JDBC → 인덱스 → 격리·잠금 → Compose·DB.

- MySQL 제약: 키/관계/CREATE/INSERT 선수 관계를 명시한다. 기본 키·외래 키·NOT NULL·UNIQUE·CHECK를 다른 저장 실패로 비교한다.
- PostgreSQL JOIN: MySQL에서 PostgreSQL로 엔진이 바뀐다는 점과 제공된 두 표, `||` 문자열 연결을 밝힌다. JOIN과 GROUP BY는 이 수업에서 처음 다룬다.
- 트랜잭션: UPDATE/WHERE와 제약 거절을 먼저 배웠음을 명시한다. COMMIT/ROLLBACK, 중간 실패, SAVEPOINT의 범위를 실제 잔액으로 비교한다.
- H2: JDBC API·연결 주소·저장소를 두 연결의 쓰기/읽기 결과에 연결한다. Java 프로세스 안에서 실행하는 H2와 Docker의 외부 DB 서버는 다르다.
- JDBC: 제공된 H2 드라이버, DriverManager, Connection, SQL 문장이 실제 두 회원 조회와 어떻게 연결되는지 먼저 설명한다. 이후 커서·값 바인딩·변경 행 수·이체로 이어진다.
- 인덱스: SQL 조건과 키를 선수로 두고, 인덱스와 실행 계획은 여기서 처음 관찰한다. 이 과제는 고정 데이터/통계/쿼리에서 계획을 비교하며 일반 운영 최적화의 모든 경우를 보장하지 않는다.
- 격리·잠금: JDBC/트랜잭션이 선수다. 스레드·장벽 코드는 제공하고 두 연결의 읽기/쓰기 순서를 고정해 재현한다. 원자적 재고 변경 한 문장과 여러 표의 업무 트랜잭션은 구별한다.
- Compose·DB: Docker와 SQL 이후에 서비스 주소·저장 경로·기존 데이터의 스키마 변경을 비교한다. 입문부터 Compose를 요구하지 않는다.

## 정상 실행과 채점의 차이

현재 앱은 같은 SQL 문제의 일반 실행에서 DB 변경을 유지한다. 제출/해설 검사는 별도 준비 DB에서 수행한다. 따라서 신선한 fixture에서만 정답이 되는지 확인하는 것만으로 학생의 `준비 코드 실행 → 수정 → 재실행` 경로를 보장할 수 없다.

이번 보강은 런타임이나 컨테이너 수명 정책을 변경하지 않는다.

- 일반 수정 연습의 starter는 조회로 대상을 관찰하도록 바꿨다. 학생이 UPDATE/DELETE를 하기 전에 데이터를 바꾸지 않는다.
- SQL 자료형/제약 비교는 코드 맨 위에 **해당 연습 표만** `DROP TABLE IF EXISTS` 후 다시 만드는 준비를 공개한다. 이는 DDL 비교의 재시험 조건이며 일반 운영 DB의 초기화 지시가 아니다.
- 트랜잭션 문제는 코드 맨 위에 **해당 두 연습 계좌**를 100으로 맞추는 UPDATE를 공개한다. 이것이 앞선 COMMIT의 rollback이라고 설명하지 않는다.
- 인덱스 문제는 해당 연습에서 만든 보조 인덱스만 DROP 후 비교한다. 행과 기본 키 인덱스는 보존한다.
- 두 연결 동시성 실험은 제공한 Java 준비 코드가 해당 연습 표만 다시 만든다. 사용자 DB와 컨테이너는 초기화하지 않는다.
- Compose 볼륨 실험은 제공한 스크립트가 연습 memo 한 행을 준비하고, **관찰 대상인** 재시작/재생성/down을 직접 수행한다. 일반 SQL 실행마다 컨테이너를 내린다는 뜻이 아니다.
- Compose 마이그레이션은 `ADD COLUMN IF NOT EXISTS`로 같은 열 추가를 재실행할 수 있게 한다. 기존 열의 자료형·제약까지 일치한다고 보장하는 기능은 아니다.

`examples/validate_lesson_continuity.rs`는 같은 LessonSession에서 starter 다음 solution을 실행해 이 경로를 검사한다. 기존 `validate_redesigned_lesson`의 정답/오답/변형/해설 proof와 별개로 결과를 남긴다.

## 검증 근거와 한계

최종 엔진 proof는 `target/mcq/<lesson-key>.json`에 정확한 공개 JSON SHA와 함께 저장한다. 일반 연속 실행 proof는 `target/mcq/<lesson-key>-continuity.json`이다. 실제 음성을 청취했거나 전체 네이티브 UI를 검수했다는 의미가 아니다. 변형은 실제 공개 grader의 `variations`로 실행한다. SQL 기초의 대표 하드코딩 반례와 동등 SQL도 lesson-cases에 기록한다.

## 공식 근거

- [MySQL 8.4 SELECT](https://dev.mysql.com/doc/refman/8.4/en/select.html): 조회의 열·조건·순서 의미
- [MySQL 8.4 implicit commit](https://dev.mysql.com/doc/refman/8.4/en/implicit-commit.html): 일반 CREATE/DROP TABLE을 트랜잭션 rollback과 혼동하지 않기
- [PostgreSQL 18 transactions](https://www.postgresql.org/docs/18/tutorial-transactions.html): 확정·취소·savepoint
- [PostgreSQL 18 ALTER TABLE](https://www.postgresql.org/docs/18/sql-altertable.html): ADD COLUMN IF NOT EXISTS의 범위
- [PostgreSQL 18 transaction isolation](https://www.postgresql.org/docs/18/transaction-iso.html): 읽기 스냅샷과 동시 변경
- [H2 in-memory databases](https://h2database.com/html/features.html#in_memory_databases): 연결 이름, 마지막 연결, JVM의 공유 범위
- [Java 25 JDBC API](https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/java/sql/package-summary.html): 드라이버·연결·문장·결과 커서의 역할
- [Postgres Docker image](https://hub.docker.com/_/postgres): PostgreSQL 18 이미지의 데이터 경로와 첫 초기화 조건

## 최종 검증 결과

최종 원본 기준으로 실제 엔진 55문제를 통과했다. Docker 기반 7개 수업은 같은 문제의 일반 실행 상태를 유지하는 별도 경로에서도 46문제 모두 `starter → solution`을 통과했다. H2/JDBC 9문제는 실제 JDK/H2로 검사했고 각 Java 실행이 새 JVM에서 시작하는 구조다.

| 수업 키 | 실제 채점·해설 문제 | 일반 연속 실행 |
|---|---:|---:|
| sql-first | 18 | 18 |
| sql-tables-constraints | 6 | 6 |
| sql-join-group | 6 | 6 |
| sql-index-plan | 4 | 4 |
| sql-transactions | 5 | 5 |
| h2-memory-file | 5 | 새 JVM |
| java-jdbc | 4 | 새 JVM |
| sql-isolation-locks | 4 | 4 |
| docker-compose-db | 3 | 3 |

SQL 기초는 공개 grader의 변형 13개, 오답 20개 거부, 동등 SQL 3개 허용까지 확인했다. 실제 실행에서 기록한 모든 `teacher_outputs`가 최종 lesson-cases의 기대 출력과 일치하고, 9개 엔진 proof 및 7개 연속 실행 proof의 SHA가 최종 JSON과 일치한다. 9개 원본/해설 캐시 검사와 전체 과정 bundle 검사도 통과했다.

검증용 `validate_redesigned_lesson_in_session`은 기존 검증의 정답·오답·변형·해설·SHA 검사를 유지하며 실제 플레이어의 `check_in_lesson`/`LessonSession::demonstrate` API를 사용한다. 처음 별도 컨테이너를 매번 생성하는 검증에서 발생한 일시적 MySQL 시작 실패는 성공으로 덮어 해석하지 않았다. 초기 결과와 개별 재실행을 보존하고, 최종 SHA의 전체 실제 session 검사와 전체 일반 연속 실행을 새로 완료했다. 앱 실행기 자체는 바꾸지 않았다.
