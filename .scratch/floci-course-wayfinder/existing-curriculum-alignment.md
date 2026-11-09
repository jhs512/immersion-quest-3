# 기존 자바 수업을 전제로 한 클라우드 후속의 출발점

2026-11-09. 사용자는 기존 자바 코스의 네트워크·DB·JDBC 등 이미 있는 수업 지식은 안다고 가정하라고 명시했다. 선수 범위를 다시 묻는 대신 실제 목표와 실습을 확인해 아래처럼 연결한다.

## 확인한 기준

기준 소스는 로컬 최신 main의 불변 커밋 `0d551472b3036ae6a0920e563d3ec5970f33ef8c`이며, 해당 소스를 보존한 연구 worktree에서 자바 코스 카탈로그와 관련 수업 20개의 교육 목표·실습 제목을 확인했다. 전체 원고와 모든 해설을 정독했다는 주장은 아니다. 중요한 JDBC 실습은 실제 준비·정답 코드와 라이브러리 선언도 확인했다.

## 이미 있는 수업과 새로 다룰 차이

| 기존 범위 | 확인한 학습·실습 | 클라우드 후속에서 새로 다룰 것 |
|---|---|---|
| 네트워크 8개 수업 | 바이트·주소/포트·IPv4/마스크·인터페이스·주소 할당, 다음 홉/반환 경로/NAT, DNS/캐시, TCP 메시지 경계, UDP, HTTP | 이미 아는 CIDR로 VPC·서브넷을 선언하고 서버를 배치한다. 비트 계산·소켓 기초를 처음부터 다시 가르치지 않는다. Floci에서 실제 동작하지 않은 AWS 경로 제어는 만들었다고 간주하지 않는다. |
| Docker 이미지·컨테이너 | pull/run/ps/logs/exec/stop/start/rm, PID1, 쓰기 레이어·볼륨·재생성, Dockerfile·캐시 | 직접 관리한 컨테이너와 클라우드 인스턴스 관리 API의 상태·의존성·비동기 완료를 비교한다. |
| Docker 네트워크·포트 | localhost 경계, 서비스 이름·바인드·네트워크 연결·호스트 포트 | 클라우드 endpoint와 실제 클라이언트의 접속 위치를 비교한다. 기존 포트 기초를 재도입하지 않는다. |
| 파일·예외·자료 보존 | UTF-8 파일, 읽기/쓰기 실패·예외 전파, append·자원 종료, 메모리/파일의 수명 | 같은 바이트를 원격 객체 key로 저장하고 읽는다. 파일 경로와 S3 key, 로컬 파일과 별도 저장 서비스의 차이를 관찰한다. |
| SQL 기초·제약·관계 | CRUD, NULL, PK·UNIQUE·FK·CHECK, JOIN·집계 | RDS 도입에서 SQL 기초를 새 목표로 반복하지 않는다. 익숙한 질의를 별도 관리형 인스턴스에서 실행한다. |
| 인덱스·트랜잭션·격리 | 실제 실행 계획, COMMIT/ROLLBACK·savepoint, 스냅샷·잠금·갱신 손실·조건부 변경 | 기존 자료 규칙이 관리형 DB에서도 유지됨을 확인하고, 인스턴스 관리 상태와 데이터 상태를 구분한다. |
| H2 수명·JDBC | 연결·메모리 DB·JVM·파일의 수명, 결과 커서·변경 행 수·입력 바인딩·연결 트랜잭션 | 같은 JDBC 역할을 유지하고 RDS 접속 정보·드라이버·DB 준비와 수명주기를 바꾼다. Java 클라이언트 연결 검증은 해당 실행 환경에서 따로 한다. |
| Compose DB | app→db 서비스 연결, 저장 경로·볼륨 수명, 초기화와 기존 데이터 마이그레이션 | DB를 app 밖의 관리형 서비스로 다룬다. 네트워크 주소·자격 값·재생성·복원과 데이터 보존을 구별한다. |

근거: [자바 코스 카탈로그](https://github.com/jhs512/immersion-quest-3/blob/0d551472b3036ae6a0920e563d3ec5970f33ef8c/tools/redesigned_courses/catalog.json), [IP](https://github.com/jhs512/immersion-quest-3/blob/0d551472b3036ae6a0920e563d3ec5970f33ef8c/tools/redesigned_lessons/network_ip/content.json), [라우팅](https://github.com/jhs512/immersion-quest-3/blob/0d551472b3036ae6a0920e563d3ec5970f33ef8c/tools/redesigned_lessons/network_routing/content.json), [JDBC](https://github.com/jhs512/immersion-quest-3/blob/0d551472b3036ae6a0920e563d3ec5970f33ef8c/tools/redesigned_lessons/java_jdbc/content.json), [Compose DB](https://github.com/jhs512/immersion-quest-3/blob/0d551472b3036ae6a0920e563d3ec5970f33ef8c/tools/redesigned_lessons/docker_compose_db/content.json), [격리·잠금](https://github.com/jhs512/immersion-quest-3/blob/0d551472b3036ae6a0920e563d3ec5970f33ef8c/tools/redesigned_lessons/sql_isolation_locks/content.json).

## 반영할 원칙

- 대상은 기존 자바 과정의 관련 기초를 아는 학습자다. SQL·JDBC를 배웠는지 다시 묻거나 클라우드 앞에 기초 DB 수업을 새로 끼우지 않는다.
- RDS는 새 SQL 수업이 아니라 이미 아는 DB를 관리형 자원으로 사용·운영하는 후속이다.
- Lambda도 기존 자바의 함수·입력·출력·실패 경험에 연결한다. 이번 실측은 Python 3.12이므로 이를 Java Lambda 검증 완료로 간주하지 않는다. 익숙한 Java로 학생 코드를 제공하려면 해당 런타임과 의존성 검증이 구현 준비 작업으로 남는다.
- DynamoDB는 SQL·JDBC 재입문이 아니라 다른 key 중심 접근 모델의 비교 후보다.
- 다음 교육 설계는 첫 VPC·서브넷·EC2 수업의 예고·목표·대표 문제다. 이미 확인된 기초를 이유 없이 다시 그릴링하지 않는다.
