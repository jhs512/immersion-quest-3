# 정보처리기사 실기 30수업 지도: 전체 범위 조사

확인일: **2026-10-19**. 제작자용 근거·설계 메모다. 사용자가 과정 전체 제작을 위임한 최신 방향을 전제로 하며, 반복적인 수업 승인 요청을 새로 요구하지 않는다. 이 조사 자체는 생산 콘텐츠·PRD·실행기·게시물을 수정하지 않는다. Java 백엔드·AICE의 수업과 진도는 가져오지 않는다.

## 1. 공식 범위와 지도 연결

공식 원문은 [큐넷 2026 출제기준](https://www.q-net.or.kr/pageLink.do?link=cst/cstReport&jmCd=1320&mcrtrNo=991)과 [2027~2029 출제기준](https://www.q-net.or.kr/pageLink.do?link=cst/cstReport&jmCd=1320&mcrtrNo=1453)이다. 10월16일 공식 뷰어에서 PDF 저장 후 본문을 확인한 보존본을 재사용한다. 실기 시작은 각각 PDF 11쪽·10쪽이며 12개 주요항목을 다룬다. 아래 매핑은 `.scratch/player-content-redesign/lesson-prds/engineer-course-map.md`를 읽고 만든 **교육 설계 배정**이며 공식 출제 비중이나 제작 완료표가 아니다.

| 공식 실기 주요항목 | 지도 수업 번호·담당 | 누락 방지 세부점 |
| --- | --- | --- |
| 1 요구사항 확인 | 19 요구사항·20 분석모델/설계 | 현행 시스템·제약·검증·모델 타당성 |
| 2 데이터 입출력 구현 | 14 관계형 구조·17 변경·18 저장/처리 | 논리·물리 저장소·프로시저·성능 |
| 3 통합 구현 | 22 연계/인터페이스 | 데이터 표준·송수신·실패·검증 |
| 4 서버프로그램 구현 | 21 모듈/업무 | 개발환경·형상관리·공통 모듈·배치 |
| 5 인터페이스 구현 | 22·26 보안 | 설계서·데이터·오류·보안·구현 검증 |
| 6 화면 설계 | 23 화면/폼 | UI 지침·프로토타입·입력/흐름 |
| 7 애플리케이션 테스트 관리 | 24 케이스/결함·25 통합/성능 | 테스트 범위·통합·성능 개선 |
| 8 SQL 응용 | 15 조회/결합·16 그룹/순서·17·18 | 절차형 SQL·응용 SQL·DCL 포함 |
| 9 소프트웨어 개발 보안 구축 | 26 | 요구→설계→구현→검증→결함 관리 |
| 10 프로그래밍 언어 활용 | 1~7 C·8~11 Java·12~13 Python | 언어 개념·기초 문법·라이브러리 |
| 11 응용 SW 기초 기술 활용 | 14·18·27 OS·28 네트워크/환경 | OS·DB·네트워크·기반 서버 |
| 12 제품소프트웨어 패키징 | 29 빌드/배포 | 패키징·릴리즈노트·매뉴얼·버전 |

30번은 코드·SQL·이론 답안 사이의 전환 확인용 자체 문제이며 독립 공식 영역이 아니다. 공식 기준이 C/Java/Python의 버전, 시험 DBMS, 표준 SQL 판, 부분점수, 동의어 허용 범위, 고정 배점을 확정했다는 근거는 없다. 공식 문서의 일반 범위를 특정 제품 문법과 동일시하지 않는다.

## 2. 요구사항·모델·설계: 확인한 정의와 작은 사례

| 대상 | 확인한 원리·출처의 정확한 위치 | 자체 사례·주의 |
| --- | --- | --- |
| 요구사항 검증 | 이해관계자의 실제 필요를 올바르게 표현했는지 확인한다. [IEEE CS SWEBOK 공개 PDF](https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf), Software Requirements §5 Requirements Validation, PDF57쪽. 현 URL 본문은 **V4.0a** 표기다. | 재고 조회 ‘빠르게’와 ‘동시 10요청에서 1초 이내’를 비교한다. 숫자는 수업용 요구이며 공식 SLA가 아니다. |
| 요구의 추적 | 요구→설계→검증 관계를 연결한다. [NASA SEH §4.2 Technical Requirements Definition](https://www.nasa.gov/reference/4-0-system-design-processes/#h-4-2-technical-requirements-definition), [NPR7123.1C Appendix A 정의](https://nodis3.gsfc.nasa.gov/displayAll.cfm?Internal_ID=N_PR_7123_001C_&page_name=all). | ‘음수 재고 거절’ 요구에 대응하는 입력 경계와 테스트가 없는 부분을 찾는다. 검증을 단순 프로그램 실행과 동일시하지 않는다. |
| 유스케이스 | 외부 행위자에게 가치 있는 관찰 가능 결과를 내는 시스템 행동을 기술한다. [OMG UML2.5.1 §18.1.3.1](https://www.omg.org/spec/UML/2.5.1/PDF#page=681). | 점원·관리자와 재고 조회/정정의 관계를 읽는다. 화면 버튼 하나를 항상 유스케이스 하나로 계산하지 않는다. |
| 연관과 상호작용 | 연관은 타입 인스턴스 사이의 의미 관계, 상호작용은 메시지 전달 행동에 초점을 둔다. [UML §11.5.3.1](https://www.omg.org/spec/UML/2.5.1/PDF#page=241), [§17.2.3.1](https://www.omg.org/spec/UML/2.5.1/PDF#page=609). | 상품–재고 관계와 점원→서비스→저장소 호출을 구분한다. 선의 모양만 암기하는 문제로 끝내지 않는다. |
| 결합도·응집도 | 모듈 사이 의존 정도와 모듈 내부 요소의 관련 정도다. [SWEBOK Software Design §1.4 Software Design Principles](https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf#page=86). | 재고 정정 모듈이 메일 설정까지 직접 바꾸는 설계와 명시적 인터페이스를 쓰는 설계를 비교한다. 줄 수·클래스 수가 지표 자체가 아니다. |
| 화면 오류와 안내 | 입력에는 필요한 라벨/설명이 있어야 하고 감지한 오류를 식별·설명해야 한다. [W3C WCAG2.2 §3.3.1, §3.3.2](https://www.w3.org/TR/WCAG22/#input-assistance). | 재고 수량 칸에 단위가 없는 화면→라벨 추가→범위 밖 입력 안내 순서. WCAG가 큐넷의 유일 UI 규정이라고 하지 않는다. |

SWEBOK의 설계 원칙을 읽었다는 이유로 GoF 패턴 전체의 정의·동의어 순서를 확정하지 않는다. 패턴별 문제를 제작할 때 각각의 1차 근거를 추가해야 한다. 같은 원칙으로 전통적인 결합도·응집도 세부 분류의 서열을 이 조사만으로 인증하지 않는다.

## 3. 연계·테스트·성능

인터페이스는 입력·출력·실패·중복 요청의 약속을 구분한다. [RFC9110 §9.2.2 Idempotent Methods](https://www.rfc-editor.org/rfc/rfc9110.html#name-idempotent-methods)는 같은 요청의 반복 효과가 의도한 효과 측면에서 한 번과 같다는 의미를 설명한다. ‘재고를 7로 정정’과 ‘재고를 1 늘림’의 중복 도착을 비교할 수 있다. **POST가 언제나 중복 안전하거나 HTTP 메서드만으로 업무 중복 처리가 해결된다고 가르치지 않는다.** 예외·재시도 정책은 문제에 제공한다.

[ISTQB CTFL4.0.1 공식 syllabus](https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf)의 확인 지점은 §4.2.1 동등 분할, §4.2.2 경계값, §4.3.1 문장 커버리지, §4.3.2 분기 커버리지, §2.2.1 테스트 레벨, §5.5 결함 관리다. 이것은 설명 근거이며 정보처리기사와 ISTQB가 같은 시험이라는 뜻은 아니다.

- 수량 허용 범위 1~9라면 0·1·9·10의 기대 결과를 먼저 정한다. 숫자는 자체 사례다. 동등 분할의 대표값 통과가 그 구간의 무결함을 증명하지 않는다.
- `if (stock > 0) { shipped = 1; }`에서 양수 하나만 검사하면 대입문은 실행해도 거짓 분기는 지나지 않는다. **문장 100%가 모든 분기·모든 경로·무결함을 뜻하지 않는다.** 커버리지 계산 시 대상 문장/제어흐름 그래프를 문제에 명시한다.
- 재고 서비스→창고 연결의 통합 검사에서 실제 하위 연결 대신 고정 응답을 주는 대역과, 상위 호출을 흉내 내는 드라이버의 역할을 구분한다. 모든 테스트 대역을 동일한 의미의 mock으로 부르지 않는다.
- 실패는 관찰된 현상, 결함은 그 원인이 될 수 있는 산출물 문제로 구분한다. 결함 기록에는 재현 조건·기대·실제 결과를 연결한다.
- 성능은 목표·부하·측정 환경을 고정해 비교한다. [PostgreSQL18 §11.1](https://www.postgresql.org/docs/18/indexes-intro.html)은 인덱스가 검색을 돕지만 변경 유지 비용을 더하며 플래너가 사용을 선택함을 설명한다. 3행 실습의 속도 차이로 실서비스 성능 개선을 증명하지 않는다.

## 4. 보안·인증·암호

보안 수업은 기능과 별개 암기 단원이 아니라 요구·설계·구현·검증·결함 처리에 연결한다. [NIST SP800-218 SSDF1.1 Table1 PW.1/PW.2/PW.7/PW.8/RV.1~3](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-218.pdf)은 보안 요구·설계 검토·코드/실행 검증·취약점 대응을 구분한다. OWASP 공격 문자열이나 실제 외부 시스템을 대상으로 하는 실습 없이 자체 입력과 역할 표로도 원리를 확인할 수 있다.

| 구분 | 1차 정의 출처 | 안전한 자체 사례 |
| --- | --- | --- |
| 인증 / 인가 | [NIST authentication Definitions](https://csrc.nist.gov/glossary/term/authentication), [authorization Definitions](https://csrc.nist.gov/glossary/term/authorization). 각각 신원 확인과 권한 부여/판단이라는 문맥을 선택한다. NIST 용어집은 여러 문서의 정의를 함께 싣는다. | 로그인한 점원도 관리자 전용 재고 정정은 거절되는 역할 표. 인증 성공=모든 권한 획득이 아니다. |
| 대칭 / 비대칭 | [NIST symmetric key algorithm](https://csrc.nist.gov/glossary/term/symmetric_key_algorithm), [asymmetric key algorithm](https://csrc.nist.gov/glossary/term/asymmetric_key_algorithm), 각각 Definitions. | 공유 비밀키와 공개/개인키 쌍의 소유자를 연결한다. 알고리즘마다 가능한 용도가 다르다. |
| 해시 / 서명 | [NIST cryptographic hash function](https://csrc.nist.gov/glossary/term/cryptographic_hash_function), [digital signature](https://csrc.nist.gov/glossary/term/digital_signature), Definitions. | 바뀐 릴리즈 파일의 해시 불일치를 찾는다. 해시는 복호화가 아니며, 해시 값만 믿을 출처 없이 주면 진위가 보장되지 않는다. 서명은 기밀성 암호화 자체가 아니다. |

해시 충돌이 절대로 불가능하다고 말하지 않는다. 비밀번호를 일반 고속 해시 한 번으로 저장하는 방법을 안전한 구현으로 제시하지 않는다. 암호 강도·알고리즘 권고를 제작할 때는 당시 유효한 공식 보안 지침을 별도 확인한다.

## 5. OS·메모리·네트워크: 계산 가능한 작은 모델

OS 설명은 저자 공개 원문 OSTEP [Ch7 §7.2~7.6 CPU scheduling](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-sched.pdf), [Ch18 §18.1 Paging](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-paging.pdf), [Ch32 §32.3 Deadlock](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-bugs.pdf)을 읽었다. 저자 교재의 모형이며 실제 Windows 스케줄러를 재현했다고 하지 않는다.

- 자체 계산안: CPU 하나, 도착시간 모두0, I/O·교체비용0, 작업 A=4·B=2, 동률은 A 먼저. FCFS A→B의 대기시간은0·4, 평균2. SJF B→A는0·2, 평균1. 반환시간과 대기시간을 구분한다. RR은 시간할당량과 동시 도착 처리 순서가 주어져야 답이 정해진다.
- 자체 주소안: 페이지 크기4바이트, 가상 주소9는 페이지2·오프셋1. 표에서 페이지2→프레임5라고 주면 물리 주소21이다. 가상 페이지와 물리 프레임의 번호가 같아야 한다는 오해를 확인한다. 페이지 크기는 실제 기기 값이 아닌 작은 모형이다.
- 자체 교착안: 두 작업이 각각 프린터·파일 잠금을 하나씩 보유하고 반대 자원을 기다린다. 순환 대기만 떼어 모든 실제 상황의 교착을 증명하지 않고, 보유·비선점·배타 조건을 함께 준다. 예방·회피·탐지를 동의어로 처리하지 않는다.

CIDR 근거는 [RFC4632 §3.1](https://www.rfc-editor.org/rfc/rfc4632.html#section-3.1), 예외 경계는 [RFC3021 §2.1](https://www.rfc-editor.org/rfc/rfc3021.html#section-2.1)이다. 자체 문제 `192.0.2.8/29`는 총8주소, 네트워크 .8, 일반적인 브로드캐스트 서브넷의 브로드캐스트 .15, 호스트 .9~.14다. `/31` point-to-point 예외가 있으므로 모든 프리픽스에 ‘항상2를 뺀다’를 일반화하지 않는다. 주소 범위는 계산 모형이며 외부 연결을 요구하지 않는다.

전송 계층 설명은 [RFC9293 §2.2 TCP](https://www.rfc-editor.org/rfc/rfc9293.html#section-2.2), [RFC768 User Interface / IP Interface](https://www.rfc-editor.org/rfc/rfc768.html)를 따른다. TCP의 순서 있는 바이트 스트림과 UDP 데이터그램을 구분하되 TCP면 어떤 조건에서도 업무 처리 성공을 보장한다거나 UDP가 모든 앱에서 항상 빠르다는 결론을 내리지 않는다. 네트워크 계층 모델의 이름·순서는 별도 출제 문제에 사용할 명시적 모델을 제공한다.

위 숫자는 근거에서 **자체 산출한 설계 검토값**이며 이번 조사에서 프로그램 실행으로 검증하지 않았다. 제작 단계에서 표·자동 계산·해설 값을 대조해야 한다.

## 6. SQL: SQLite에서 확인할 수 있는 것과 없는 것

공식 시험의 DBMS·방언은 미확인이다. SQLite를 사용한 채점이 표준 SQL 전체 또는 Oracle/PostgreSQL을 검증하지 않는다. 문항마다 실행 엔진·버전·자료형·초기 자료·정렬 기준을 적고, 지원하지 않는 기능은 실행 성공을 가장하지 않는다.

| 주제 | 확인한 규칙·정확한 공식 문서 위치 | 제작 시 피할 함정 |
| --- | --- | --- |
| NULL·조건 | [SQLite Expressions §2, §8, §14](https://www.sqlite.org/lang_expr.html). 일반 비교의 NULL과 `IS NULL`을 구분하며 WHERE는 참인 행을 남긴다. | NULL을0·빈 문자열과 같다고 채점하지 않는다. `NOT IN`에 NULL이 들어간 사례는 결과를 따로 추적한다. |
| 조인 | [SQLite SELECT §2.1 FROM, §2.3 WHERE](https://www.sqlite.org/lang_select.html). 외부 조인은 미일치 행을 NULL로 확장한 뒤 WHERE를 적용한다. | ON 필터를 WHERE로 옮기면 미일치 행이 사라질 수 있다. 중복 키가 만든 모든 조합을 센다. |
| 집계·그룹 | [SQLite Aggregate Functions §3 count/avg/sum](https://www.sqlite.org/lang_aggfunc.html), [SELECT §2.4, §2.5](https://www.sqlite.org/lang_select.html). `COUNT(*)`는 행, `COUNT(x)`는 비NULL을 센다. | 집계 밖 비그룹 열을 허용하는 SQLite bare-column 확장을 정답 표준으로 삼지 않는다. 빈 집합 AVG/SUM은0으로 가정하지 않는다. |
| 순서·윈도우 | [SELECT §4 ORDER BY](https://www.sqlite.org/lang_select.html), [Window Functions §2.2 Window Frames](https://www.sqlite.org/windowfunctions.html). | ORDER BY 없이 행 순서를 고정하지 않는다. 누적합에는 동률·프레임을 명시하고 `ROWS`/`RANGE` 차이를 숨기지 않는다. |
| 제약 | [SQLite FK §2 Enabling](https://www.sqlite.org/foreignkeys.html#fk_enable), [PostgreSQL18 §5.5 Constraints](https://www.postgresql.org/docs/18/ddl-constraints.html). | SQLite FK 집행 설정을 확인한다. CHECK와 NOT NULL은 다른 제약이다. 제품별 PK/NULL 예외를 표준으로 일반화하지 않는다. |
| 트랜잭션 | [SQLite Transaction §2](https://www.sqlite.org/lang_transaction.html), [PostgreSQL18 §3.4](https://www.postgresql.org/docs/18/tutorial-transactions.html). | BEGIN→변경→ROLLBACK과 COMMIT을 구별한다. SQLite BEGIN 중첩은 SAVEPOINT와 다르다. 에러 한 번이면 언제나 전체 자동 취소된다고 가정하지 않는다. |
| DCL | [SQLite Omitted GRANT/REVOKE](https://www.sqlite.org/omitted.html), [PostgreSQL18 GRANT Description](https://www.postgresql.org/docs/18/sql-grant.html). | SQLite에는 GRANT/REVOKE가 없으므로 권한 문제를 SQLite 실행으로 통과했다고 하지 않는다. 역할 표 또는 명시한 실제 DBMS 검증을 사용한다. |
| 프로시저·함수·트리거 | [PostgreSQL18 CREATE PROCEDURE Description/Compatibility](https://www.postgresql.org/docs/18/sql-createprocedure.html), [SQLite Application-Defined Functions §1](https://www.sqlite.org/appfunc.html), [CREATE TRIGGER §2](https://www.sqlite.org/lang_createtrigger.html). | SQLite 애플리케이션 등록 함수와 SQL 저장 프로시저는 다르다. 행 트리거를 문장 트리거로 일반화하지 않는다. PostgreSQL/PLpgSQL 문법을 시험의 고정 정답이라고 하지 않는다. |

자체 자료 검토안: 상품 A·B, 주문 두 행 모두A. LEFT JOIN은 A의 두 일치행과 B의 NULL 확장 한 행으로 **3행**이다. `COUNT(*)=3`, `COUNT(order_id)=2`. WHERE에서 `order_id IS NOT NULL`을 적용하면 **2행**이다. 수량 `[2,NULL,4]`의 `COUNT(*)=3`, `COUNT(qty)=2`, `AVG(qty)=3`이다. 실제 실행은 제작 단계에 남긴다.

정규화·논리/물리 구분은 독립 학습으로 남겨야 한다. [Microsoft의 정규화 입문 설명](https://learn.microsoft.com/en-us/previous-versions/troubleshoot/microsoft-365/microsoft-365-apps/access/database-normalization-description#description-of-normalization)은 중복·갱신 불일치 문제의 벤더 설명 근거로만 제한한다. **그 문서에는 BCNF를4NF와 혼동한 표현이 있어 정규형의 엄밀 정의·서열 근거로 쓰지 않는다.** 후보키·함수 종속·3NF/BCNF 구별의 정식 문제를 제작할 때 별도 1차 이론 근거를 보강해야 한다. 인덱스·프로시저 학습으로 정규화가 대체되지 않는다.

## 7. 빌드·릴리즈·패키징

- [Reproducible Builds Definition](https://reproducible-builds.org/docs/definition/)은 같은 소스·환경·지시로 바이트 단위로 같은 산출물을 만들 수 있는 성질을 설명한다. ‘내 컴퓨터에서 빌드 성공’과 구분한다.
- [SemVer2.0.0 규칙1~8](https://semver.org/)은 공개 API와 호환성을 전제로 major/minor/patch의 의미를 정한다. 모든 프로젝트가 SemVer를 쓰거나 날짜 태그가 틀렸다는 뜻은 아니다.
- [NIST SSDF PS.2/PS.3](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-218.pdf#page=19)는 릴리즈 무결성 검증 정보와 릴리즈 보존을 구분한다. 버전 번호·파일 해시·변경 설명·설치 매뉴얼은 서로 다른 역할이다.
- 자체 짧은 흐름은 소스 정정→테스트→빌드 산출물→버전/변경 기록→설치·검증→이전 릴리즈 비교다. 재고0 표시 수정의 릴리즈노트와 새 기능 추가의 노트를 구분하고, 매뉴얼에는 실행 전제·설치·시작·복구를 연결한다. 실제 배포는 이 조사 범위 밖이다.

## 8. 같은 상황을 이어가는 연구용 진행안

단원별 공통 상황은 작은 매장의 **재고·주문·창고 연결**이다. 처음 C 재고 표시에서 시작하되 이론 단원마다 필요한 두세 개 자료만 남긴다. 긴 서비스 프로젝트 전체를 학생이 구현하게 하지 않는다.

1. 재고 정정 규칙 하나를 요구로 구체화하고 기대 결과를 고른다.
2. 상품·주문 표에서 중복/키·미일치 행을 확인한다.
3. 조회 조건·조인·집계를 한 곳씩 바꿔 결과를 답한다.
4. 점원·서비스·창고의 책임/메시지와 실패 결과를 연결한다.
5. 입력 경계·실행 분기·결함 기록을 같은 요구에 추적한다.
6. 점원·관리자 권한과 릴리즈 파일 무결성을 구분한다.
7. 창고 작업 두 개의 CPU·페이지·주소 계산을 작은 표로 풀어본다.
8. 변경을 테스트·빌드·릴리즈노트에 연결하고, 다른 조건을 조합한 짧은 도전을 선택 제공한다.

이 흐름은 연구 제안이며 수업별 스텝 수를8개로 강제하지 않는다. 준비 코드·표·문장을 제공하고 학생은 결과·빈칸·한 곳 수정으로 핵심 관계를 다룬다. 해설 열람만으로 학습 완료를 판단하지 않는다.

## 9. 제작 전 확인 한계

이 문서는 공식12영역의 **누락 점검과 근거 출발점**이다. 30수업 모든 문항·해설의 검증 완료 증거가 아니다. 특히 디자인패턴별 상세 의미, 전통적 결합도/응집도 분류, 정규형 엄밀 정의, 모든 보안 용어를 다 검증했다고 말하지 않는다. 실제 제작되는 항목마다 1차 근거를 확장한다. SQL은 SQLite로 가능한 실행과 권한·프로시저 등 다른 방언/개념 판정을 명시적으로 분리하며 공식 시험 채점과 동일하다고 주장하지 않는다.

## 10. 추가 조사: 정규화의 엄밀한 구분

추가 확인일: 2026-10-19. 위 §6·§9에서 남긴 **정규형 정의의 근거 공백을 이 절로 보강**한다. 실제 콘텐츠를 제작·검증했다는 뜻은 아니다. 관계 이론의 집합 모델을 사용하며 SQL의 중복 행·NULL·부분 유일 인덱스와 혼동하지 않는다.

### 10.1 원문과 출처의 역할

- **원 연구**: Ronald Fagin, *Multivalued Dependencies and a New Normal Form for Relational Databases*, ACM TODS2(3), 1977, pp262~278. [IBM Research 공식 서지·초록](https://research.ibm.com/publications/multivalued-dependencies-and-a-new-normal-form-for-relational-databases), [NUS 교수 자료실의 원 논문 PDF](https://www.comp.nus.edu.sg/~lingtw/papers/fagin.pdf). PDF 본문을 직접 읽었다. §2/Theorem1(인쇄266쪽, PDF5쪽)은 MVD와 무손실 조인 분해, §3(인쇄267쪽, PDF6쪽)은 BCNF·4NF 정의 및 Theorem2를 담는다. ACM 직접 다운로드는403이었으므로 ACM에서 전문을 읽었다고 하지 않는다.
- **저자 직접 공개 교재 자료**: Silberschatz·Korth·Sudarshan, [Database System Concepts7판 Chapter7 PDF](https://www.db-book.com/slides-dir/PDF-dir/ch7.pdf). 슬라이드 번호와 PDF 쪽수가 다르다. FD/키는 PDF11~15쪽, 무손실 조건16쪽, BCNF20쪽, 3NF25쪽, MVD70~72쪽, 4NF76쪽, 1NF92~93쪽을 확인했다.
- **공식 대학 강의 원문**: Chris Pollett, SJSU CS157a, [2018-10-08 강의의 Third Normal Form / 1NF and2NF / Dependency Preservation 절](https://www.cs.sjsu.edu/faculty/pollett/157a.3.18f/Lec20181008.html). 2NF가 선택된 주키 하나가 아닌 **모든 후보키**를 기준으로 함을 직접 확인했다.
- 대학 도메인이라는 이유만으로 출처를 채택하지 않았다. 검색 중 확인한 Ontario Tech 페이지에는 LLM 생성 과정이 노출되어 있어 이번 엄밀 정의 근거에서 제외했다. Berkeley 입문 슬라이드의 간략 BCNF 설명도 필요충분조건으로 확대하지 않았다. Microsoft 입문 문서의 BCNF/4NF 혼동은 여전히 채택하지 않는다.

### 10.2 기호·종속·분해

관계 스키마를 `R`, 속성 집합을 `X,Y`, 단일 속성을 `A`, 주어진 FD의 논리적 폐포를 `F+`로 쓴다. **슈퍼키**는 `R`의 모든 속성을 결정하고, **후보키**는 불필요한 속성을 뺄 수 없는 최소 슈퍼키다. **주요 속성(prime)**은 어느 후보키에라도 포함되는 속성이다. 주키로 선택했는지만 보지 않는다. 근거: 저자 교재 PDF13쪽, SJSU Third Normal Form 절.

| 개념 | 검토에 사용할 정확한 뜻 | 근거 |
| --- | --- | --- |
| 함수 종속 `X→Y` | 모든 합법적 관계 인스턴스의 두 튜플이 X에서 같으면 Y에서도 같다. 현재 몇 행이 우연히 맞는 것만으로 스키마 종속을 증명하지 못한다. | 저자 교재 PDF11·14쪽 |
| 완전/부분 함수 종속 | `X→A`가 성립하고 X의 어떤 진부분집합도 A를 결정하지 못하면 완전 종속이다. 진부분집합이 결정하면 부분 종속이다. 2NF에서는 후보키에 대한 **비주요 속성**의 부분 종속을 검사한다. | SJSU 1NF and2NF 절. 완전 종속은 이 조건의 반대로 풀어 쓴 정의 |
| 이행 종속 | `X→Y`, `Y→Z`이면 `X→Z`를 추론한다. 하지만 이행 추론이 존재한다는 이유만으로 모두3NF 위반은 아니다. 위반 판단에는 결정자의 슈퍼키 여부와 오른쪽 속성의 prime 여부가 필요하다. | 저자 교재 PDF12·25쪽 |
| 다치 종속 `X↠Y` | X가 같을 때 Y와 나머지 속성의 값 조합을 교환해 얻은 튜플도 존재해야 한다. `Z=R−(X∪Y)`일 때 `(x,y1,z1)`, `(x,y2,z2)`로부터 `(x,y1,z2)`, `(x,y2,z1)`이 있어야 한다. 단순히 ‘여러 값이 나온다’와 다르다. | Fagin §2/Theorem1, 저자 교재 PDF70~72쪽 |
| 무손실 분해 | 모든 합법적 r에 대해 분해한 투영들의 자연조인이 원래 r과 정확히 같다. 행이 사라지지 않는 것뿐 아니라 **가짜 조합이 추가되지 않아야** 한다. | Fagin Theorem1; 저자 교재 PDF6·16쪽 |

FD만을 제약으로 고려한 이진 분해 `R=R1∪R2`에서는 `(R1∩R2)→R1` 또는 `(R1∩R2)→R2`가 `F+`에 있으면, 그리고 그 경우에만 무손실이다. MVD 등 다른 제약이 있으면 이를 유일한 필요조건으로 일반화하지 않는다. `X↠Y`는 `XY`와 `XZ`로의 무손실 분해와 동치다. **무손실**과 **종속 보존**은 다른 성질이다. BCNF 무손실 분해가 원래 모든 FD를 개별 테이블에서 검사 가능하게 하지는 않는다. 근거: 저자 교재 PDF16쪽, Fagin Theorem1, SJSU Dependency Preservation 절.

### 10.3 1NF·2NF·3NF·BCNF·4NF

아래 종속은 주어진 목록만이 아니라 그 논리적 귀결까지 고려한다. 1NF는 이후 정규형의 전제다.

| 정규형 | 정의·구분 | 근거 |
| --- | --- | --- |
| 1NF | 각 속성 도메인의 값이 사용 맥락에서 원자 단위다. 한 칸에 반복 항목 집합을 넣는 모델과 구분한다. 모든 문자열에 구분 기호가 없어야 한다거나 모든 실제 단어가 더 쪼개질 수 없어야 한다는 뜻은 아니다. | 저자 교재 PDF92~93쪽 |
| 2NF | 1NF이며 어떤 비주요 속성도 **어느 후보키의 진부분집합에도** 종속하지 않는다. | SJSU 1NF and2NF 절 |
| 3NF | 각 비자명 FD `X→A`에 대해 X가 슈퍼키이거나 A가 주요 속성이다. 비자명은 `A∉X`다. ‘이행 종속이 전혀 없음’만을 일반 정의로 쓰지 않는다. | SJSU Third Normal Form 절, 저자 교재 PDF25쪽 |
| BCNF | 각 비자명 FD의 결정자 X가 **슈퍼키**다. ‘모든 결정자가 최소 후보키’라고 좁히지 않는다. 3NF의 오른쪽 주요 속성 예외를 허용하지 않는다. | Fagin §3, 저자 교재 PDF20쪽 |
| 4NF | 각 비자명 MVD `X↠Y`의 X가 슈퍼키다. MVD가 자명한 경우는 `Y⊆X` 또는 `X∪Y=R`이다. | Fagin §3, 저자 교재 PDF76쪽 |

**4NF ⇒ BCNF ⇒ 3NF ⇒ 2NF ⇒ 1NF**이며 역은 일반적으로 성립하지 않는다. 특히 **BCNF≠4NF**다. Fagin §3/Theorem2는4NF가 BCNF를 함의함을 보이고, 같은 절은 BCNF보다 엄격함을 밝힌다. ‘4NF에는 MVD가 하나도 없다’는 말도 틀리다. 자명한 MVD와 슈퍼키가 결정하는 MVD는 허용된다.

부분·이행의 작은 기호 판별안: `주문상품(주문,상품,상품명,수량)`에서 후보키 `(주문,상품)`, `상품→상품명`이면 비주요 상품명의 부분 종속 때문에2NF 위반이다. 별도 `상품공급(상품,공급처,전화)`에서 `상품→공급처`, `공급처→전화`, 후보키 상품만 주면2NF이지만3NF는 아니다. 전화는 비주요이고 공급처는 슈퍼키가 아니다. **둘 다 자체 추론 예이며 실제 DB 실행은 하지 않았다.**

### 10.4 반례1: 3NF이지만 BCNF가 아닌 관계

자체 설계안 `배정(상품P, 지역R, 담당자M)`에 **모든 합법적 자료에서** `PR→M`, `M→R`만을 기본 FD로 준다. 후보키는 `PR`, `PM`이다. 세 속성 모두 prime이지만 M 혼자서는 P를 결정하지 못한다.

| P | R | M |
| --- | --- | --- |
| 사과 | 동쪽 | 민 |
| 배 | 동쪽 | 민 |
| 사과 | 서쪽 | 준 |

후보 답안:

- ‘최고 정규형을 BCNF까지 판정’ → **3NF**. `M→R`의 R은 prime이므로3NF 조건을 만족하지만 M은 슈퍼키가 아니어서 BCNF 위반이다.
- ‘`MR`과 `PM`으로 분해하면 무손실인가’ → **예**. 공통 M이 MR을 결정한다.
- ‘무손실이면 `PR→M`도 각 테이블만 보고 항상 보존되는가’ → **아니요**. 분해 후 `MR={(민,동쪽),(준,동쪽)}`, `PM={(사과,민),(사과,준)}`은 각 테이블의 투영 FD를 만족하지만 조인하면 같은 상품·지역에 담당자 둘이 생긴다. 무손실 보장과 이후 독립 갱신의 종속 보존은 구별해야 한다.

FD·키를 명시한 **자체 반례 및 논리 추론**이다. 표의 행만 관찰해 미지의 모든 FD를 찾아냈다고 말하지 않으며 SQL로 실행한 결과도 아니다. 이론 근거는 SJSU의 Bookings 반례와 Dependency Preservation 절이지만 상품 상황·자료는 별도로 만들었다.

### 10.5 반례2: BCNF이지만4NF가 아닌 관계와 가짜 조합

자체 설계안 `취급(P상품,S공급처,W창고)`에서 **상품별 공급처와 창고는 독립적으로 조합 가능**하다고 명시한다. FD는 전체 속성 키에서 오는 것 외에는 없고, `P↠S`를 제약으로 준다.

| P | S | W |
| --- | --- | --- |
| 사과 | 갑 | 북 |
| 사과 | 갑 | 남 |
| 사과 | 을 | 북 |
| 사과 | 을 | 남 |

후보 답안:

- ‘BCNF인가’ → **예**. 주어진 제약에서 비자명한 FD 위반이 없다.
- ‘4NF인가’ → **아니요**. `P↠S`는 비자명하며 P는 슈퍼키가 아니다.
- ‘`PS`와 `PW`로 분해한 뒤 자연조인’ → **원래4행**. 독립 조합이라는 MVD 제약 덕분에 무손실이다.
- 반대로 ‘갑은 북에만, 을은 남에만’이라는 **다른 업무**에서 대각선2행만 허용된다면 그 MVD를 가정할 수 없다. 같은 두 투영을 조인하면4행이 되어 원래 없던2행이 생긴다. 이때 해당 분해는 손실 분해다. 데이터 값이 소실되어야만 ‘손실’이라는 뜻이 아니다.

이는 Fagin Theorem1을 적용한 자체 모형·계산이며 실제 SQL 실행은 하지 않았다. 한 상품에 두 공급처가 보인다는 사실만으로 공급처와 창고의 독립성을 선언하면 안 된다.

## 11. 추가 조사: 디자인패턴 분류의 확인 수준

1차 발행처인 [Pearson의 GoF 원서 페이지 Table of contents](https://www.pearson.com/en-us/subject-catalog/p/design-patterns-elements-of-reusable-object-oriented-software/P200000009480/9780321700698)에서 제3장 생성, 제4장 구조, 제5장 행위라는 대분류를 확인했다. [InformIT 발행처의 같은 책 Preface](https://www.informit.com/store/design-patterns-elements-of-reusable-object-oriented-9780201633610)는 저자들이 반복 설계 문제와 해결을 정리한 패턴집이라는 성격을 설명한다.

이 두 공개 페이지는 개별23패턴의 전체 Intent·Applicability와 세부 분류표를 제공하지 않는다. 따라서 이번 보강에서 **Observer/Strategy/Factory Method 등 개별 정의를 원서 전문으로 검증했다고 쓰지 않는다**. 비공식 무단 배포 PDF로 빈칸을 채우지 않았다. 필요하면 발행처가 공개한 해당 장의 미리보기 또는 저자 직접 원문을 추가로 확보한다. 대분류의 존재를 확인한 것과 패턴별 실제 문항의 정확성을 확인한 것은 다르며 시험 빈도·필출 순위는 주장하지 않는다.
