# Docker·DB·객체지향 원리 수업 확장 (2026-10-26)

## 사용자 지시와 범위

2026-10-26 사용자(Codex 경유): 「도커랑 DB 수업도 클로드가 마저 만들어. 사용법만 알려주지 말고 원리를 이해하게 하고, 나한테 물어보지 말고 끝까지 만들어서 배포해. 클래스, 상속, 객체지향 패턴 몇개 수업도 만들고, 알지 중요한건 원리 이해야. 길어도 돼.」

- 이 범위에서는 이전의 「최종 문제부터 검수」 절차가 면제됐어요. PRD 승인 방식은 `delegated_scope`(사용자 위임)이고, 사람이 문항을 하나씩 검토했다고 기록하지 않아요.
- 모든 새 스텝은 직접 코딩·명령 작성형이에요. 객관식·보기 선택·빈칸 정답 맞추기는 없어요(동시 진행 중인 객관식 전환 작업과 같은 기준).
- 채점은 실제 실행 결과(출력·파일·프로세스·DB·Docker 상태)로만 해요. 해설·예고 열람만으로는 완료 기록이 생기지 않아요.
- 되살리지 않는 것: 2026-10-26 사용자가 삭제한 27~34번 CS 수업 8개.
- 제외 유지: PostgreSQL PL/pgSQL·RLS·PG 트리거·Supabase. MySQL 프로시저·함수·트리거는 별도 후보로 남겨요(핵심 원리보다 뒤). PGroonga·pgvector·PostGIS는 기존 백로그로 남겨요.
- Spring/JPA/REST 초안 13개는 DB 원리 수업에 필요하지 않아 이번에 수업으로 만들지 않아요. 진도는 따로 보고해요(아래 표).

## 학습 설계 원칙 (이번 확장에 적용)

1. 정상 동작을 먼저 실행한다 → 조건 하나를 바꿔 예상과 다른 실제 결과를 본다 → 원인 모델을 말로 정리한다 → 1~3줄을 고쳐 해결한다 → 바뀐 자료·입력으로 다시 검증한다.
2. 한 스텝에 새 개념 하나. 단원 안에서는 같은 상황이 이어지고, 다음 스텝의 준비 파일에 앞 스텝의 정답 상태를 넣어요(학습자에게 「앞 스텝의 정답 상태에서 시작해요」라고 알려요).
3. 실행마다 같은 시작 상태에서 시작해요. Docker·DB 실습은 실행 한 번이 자기 소유의 Compose 프로젝트를 새로 만들고, 끝나면 지워요. 앞 실험의 잔여 상태가 다음 판정을 바꾸지 않게 하려는 선택이에요. 그 대신 「다시 만들어도 남는가」는 한 번의 실행 안에서 실제로 지우고 다시 만들어 관찰해요.
4. 모형(시뮬레이션)은 쓰지 않아요. Docker는 실제 Docker 엔진, DB는 실제 MySQL 8.4·PostgreSQL 18·H2 2.4.240, 객체지향은 실제 JDK 25예요. 엔진 결과를 다른 엔진의 결과라고 말하지 않아요.
5. 패턴은 이름부터 외우지 않아요. 패턴 없이 짠 코드에 바뀐 요구를 넣어 깨지는 곳을 먼저 보고, 최소 구조로 고쳐요. 필요 없는 경우의 판단도 해설과 단원 목표에 적어요.

## 실습 환경 (앱 기능, 수업보다 먼저 릴리스)

| 실행 방식 | 무엇을 실행하나 | 격리·정리 |
| --- | --- | --- |
| `java` (기존) | JDK 25 단일 파일 | 실행마다 새 폴더 |
| `java_libraries` (신규) | JDK 25 + 앱이 고정한 라이브러리 묶음(H2 2.4.240, PostgreSQL JDBC, MySQL Connector/J). Maven Central 경로 + sha256 고정, 수업은 묶음 이름만 고름 | 실행마다 새 폴더. 라이브러리는 `course-tools`에 해시 확인 뒤 보관 |
| `docker` (신규) | 수업의 실습 스크립트(`lab.sh`)를 Bash로 실행. 실제 Docker 엔진·Compose 사용 | 실행마다 `mq3lab-` 접두어의 고유 Compose 프로젝트. 학습자 compose 파일을 실행 전에 검사(고정 호스트 포트·0.0.0.0 공개·`container_name`·호스트 네트워크·특권·폴더 밖 바인드 거절). 공개 포트는 `127.0.0.1::<포트>`로만, 실제 포트는 실행 중에 다시 읽어요. 끝나면(실패·시간 초과·취소 포함) 그 프로젝트 라벨의 컨테이너·네트워크·볼륨·빌드 이미지만 지워요. 앱이 강제로 꺼져 남은 프로젝트는 다음 실행·다음 시작 때 같은 라벨 기준으로 정리해요 |

- 사용자의 기존 컨테이너·볼륨·이미지·DB·서버는 건드리지 않아요. 3306/5432/8080/6379 같은 고정 포트를 쓰지 않아요.
- Docker Desktop 설치·시작은 학습자가 해요. 엔진에 연결하지 못하면 실행이 실패로 끝나고 공식 설치 안내를 보여 줘요. 완료로 기록하지 않아요.
- 이미지는 공식 이미지를 digest로 고정해요(busybox·postgres·mysql). 처음 실행 때 내려받아요.
- 옛 앱(새 실행 방식을 모르는 앱)은 새 수업이 든 코스를 해석하지 못해 이전 코스를 그대로 써요(가짜 수업을 보여 주지 않아요). 그래서 앱 릴리스를 먼저 하고, 그 뒤에 코스를 게시해요.

## 수업 목록과 전수 현황표

진도 열: 설계 = PRD·스텝 구성 / 제작 = content·해설 / 검증 = 실제 채점기(정답 통과·시작 코드 실패·오답 거절·변형) / 게시 = 수업 태그·코스 반영.

| # | 키 | 분류 | 실행 | 핵심 원리 | 최종 도전 | 설계 | 제작 | 검증 | 게시 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| O1 | java-class-objects | 자바 | java | 같은 클래스의 독립 객체, 생성자의 초기 상태, this, 별칭과 복사(얕은·깊은), equals·hashCode, 캡슐화와 불변식, 내부 목록 유출 | 불변식을 지키는 장바구니 | ◐ | | | |
| O2 | java-inheritance-composition | 자바 | java | 동적 디스패치, 오버라이드와 오버로드, 필드는 다형적이지 않음, 생성자에서 부른 재정의 메서드, 상속이 깨지는 경우(HashSet.addAll), is-a가 아닌 상속(Stack), 컴포지션·전달 | 세는 집합을 컴포지션으로 | ◐ | | | |
| O3 | java-oop-patterns | 자바 | java | Strategy(바뀌는 정책), Factory(생성 책임), Observer(구독·해제·전달 중 실패), 패턴이 필요 없을 때 | 주문 완료 알림 | ◐ | | | |
| H1 | h2-memory-file | DB | java_libraries(H2) | 메모리 DB의 수명(연결·프로세스), 이름 있는 메모리 DB, 파일 DB | 기존 초안 h2-memory-file | ◐ | | | |
| S1 | sql-tables-constraints | DB | docker(MySQL 8.4) | 표·행·SELECT, NOT NULL·UNIQUE·PK·AUTO_INCREMENT·FK, DB가 모든 클라이언트에 같은 규칙을 적용 | 기존 초안 sql-constraints | ◐ | | | |
| S2 | sql-join-group | DB | docker(MySQL 8.4) | 표를 나누는 이유(갱신 이상), JOIN의 ON, LEFT JOIN, COUNT(*)와 COUNT(열), ON과 WHERE, ONLY_FULL_GROUP_BY | 기존 초안 sql-join-group | ◐ | | | |
| S3 | sql-index-plan | DB | docker(MySQL 8.4) | 실제 읽은 행 수(Handler_read), EXPLAIN의 type·key, 열에 함수를 씌우면, 복합 인덱스의 앞 열, UNIQUE 인덱스 | 기존 초안 sql-index-explain | ◐ | | | |
| S4 | sql-engine-differences | DB | docker(MySQL 8.4 + PostgreSQL 18) | 같은 SQL의 다른 의미(`||`, 문자열 비교 규칙), 생성 키 받기 | 기존 초안 mysql-differences | ◐ | | | |
| J1 | jdbc-basics | DB | docker(PostgreSQL 18) + PostgreSQL JDBC | 연결·조회·ResultSet, 파라미터 바인딩과 SQL 주입, 영향받은 행 수, 생성 키, 연결 닫기와 연결 수 한도 | 기존 초안 jdbc-postgresql | ◐ | | | |
| T1 | db-transactions | DB | docker(PostgreSQL 18) | 자동 커밋과 중간 실패, BEGIN·COMMIT·ROLLBACK, 실패한 트랜잭션, JDBC 경계, 커밋 전 다른 연결의 시야 | 기존 초안 sql-transaction-rollback | ◐ | | | |
| T2 | db-concurrency-locks | DB | docker(PostgreSQL 18) + JDBC | 갱신 손실 재현(두 연결의 정해진 순서), 원자적 UPDATE, 조건부 UPDATE와 행 수, SELECT FOR UPDATE의 대기, 버전 열(낙관적 락), REPEATABLE READ의 직렬화 실패와 재시도 | 기존 초안 database-concurrency | ◐ | | | |
| D1 | docker-image-container | Docker | docker(busybox) | 이미지와 컨테이너(프로세스), PID 1과 종료, 같은 이미지의 독립 컨테이너, 레이어와 빌드 캐시, 쓰기 레이어, 볼륨과 데이터 영속성 | 다시 만들어도 남는 메모 | ◐ | | | |
| D2 | docker-network-ports | Docker | docker(busybox) | 컨테이너마다 다른 localhost, 서비스 이름과 네트워크, 포트 공개(루프백·동적), 컨테이너 안 127.0.0.1에만 연 서버, 컨테이너 포트와 호스트 포트 | 두 서비스와 호스트를 잇기 | ◐ | | | |
| D3 | docker-compose-db | Docker | docker(PostgreSQL 18) | 환경 변수로 초기화, 데이터 디렉터리와 볼륨, 초기화는 빈 볼륨에서만, 서비스 이름으로 DB 찾기, 시작 순서와 준비 상태(healthcheck), restart·재생성·down·down -v에서 남는 것 | 앱+DB 구성 | ◐ | | | |

◐ = 이 문서의 설계 단계. 표는 진행하면서 갱신해요.

### 기존 초안 22개의 처리

| 축 | 초안 | 이번 처리 |
| --- | --- | --- |
| DB 9 | sql-constraints, sql-join-group, sql-index-explain, mysql-differences, h2-memory-file, jdbc-postgresql, sql-transaction-rollback, database-concurrency | 각 수업의 최종 도전으로 재사용(빌드업 스텝을 새로 붙임). 앱 실행 방식으로 다시 검증 |
| DB 9 | jdbc-simpledb (MySQL) | 이번에는 수업으로 만들지 않아요. jdbc-basics가 같은 원리(파라미터 순서·생성 키·영향 행 수)를 PostgreSQL에서 다뤄요. 초안은 보존 |
| IoC 2 | ioc-container-principle, spring-beans-autowired | 이번 범위 밖(DB 연결에 필요 없음). 초안 보존 |
| JPA·트랜잭션·락 7 | jpa-* , spring-transaction-boundary, jpa-optimistic-lock | 범위 밖. 앱에 Spring·Gradle 실행 경로가 없어요. 초안 보존 |
| REST 4 | spring-boot-first, spring-rest-validation, rest-crud-persistence, rest-api-test | 범위 밖. 초안 보존 |

## 순서

1. 이 계획과 현황표 저장.
2. 앱: `docker`·`java_libraries` 실행 방식 + 검사·정리 + 단위 시험 → 커밋 → main 푸시 → 릴리스 CI → 앱 릴리스 확인.
3. 객체지향 3수업(기존 JDK, 앱 대기 없음) 제작·검증 → 게시(원격 course.json을 다시 읽어 객관식 전환 작업의 변경과 합침).
4. H2·DB·Docker 수업 제작·검증(실제 엔진) → 앱 릴리스가 공개된 뒤 게시.
5. GitHub 이슈 진도 갱신, 공개 파일 재조회, 실제 앱 확인, 최종 보고.
