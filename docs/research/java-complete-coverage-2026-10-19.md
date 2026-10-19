# Java 기초 전체 범위 근거 매트릭스

확인일: 2026-10-19 (한국 시간). `.scratch/player-content-redesign/lesson-prds/java-course-map.md`의 18개 묶음 가운데 6~16을 중심으로 Oracle JLS SE 25·Java SE 25 API와 JUnit·Gradle·AssertJ 공식 문서를 직접 열었다. 조사 노트이며 PRD 승인·학습 콘텐츠·구현·실행 완료를 뜻하지 않는다. 지도나 과거 24수업의 숫자로 필요한 개념을 제한하지 않는다. 아래 비교 상황은 자체 설계 후보이며 **이번에는 직접 컴파일·실행하지 않은 명세/API 도출 또는 검증 제안**이다.

## 확인 수준과 버전

- Oracle 페이지 표제는 Java SE 25/JDK 25다. 실제 수업 JDK·컴파일 옵션·패키지 버전과의 일치는 미검증이다.
- JUnit `current/user-guide/`는 **6.1.3 overview**로 이동했다. 공식 첫 테스트 페이지도 6.1.3으로 확인했다. JUnit 6 런타임 요구는 Java 17 이상이다. 프로젝트에 6.1.3을 채택했다는 뜻은 아니다. [Overview](https://docs.junit.org/6.1.3/overview.html), [첫 테스트](https://docs.junit.org/6.1.3/writing-tests/intro.html)
- Gradle `current` 문서 표제는 **9.8.1**이었다. AssertJ 공식 통합 문서는 열렸지만 프로젝트가 사용할 정확한 artifact 버전은 이번에 정하지 않았다. [Gradle](https://docs.gradle.org/current/userguide/java_testing.html), [AssertJ](https://assertj.github.io/doc/)
- 원글·사설 해설·복원 자료는 근거로 사용하지 않았다. 기존 강의 원문의 완전성과 이번 매트릭스의 일치 여부는 미확인이다.

## 6~10: 상태와 책임의 기초

| 지도 | 관계와 직접 확인 근거 | 작은 비교·안전 경계 후보 | 먼저 빠뜨리면 안 되는 기초 |
| --- | --- | --- | --- |
| 6 반복·배열 | 배열 길이는 생성 후 고정이고 인덱스는 0~length−1이다. 기본 for는 초기화·조건·본문·갱신, 향상 for는 항목을 받는다. [JLS §10.2–4](https://docs.oracle.com/javase/specs/jls/se25/html/jls-10.html#jls-10.2), [§14.14.1–2](https://docs.oracle.com/javase/specs/jls/se25/html/jls-14.html#jls-14.14) | 주문금액 2개 합산을 1개·0개와 비교. `< length`와 마지막 인덱스 구분. 기본 합계를 0으로 두면 빈 배열은 0이라는 도출. | 인덱스와 원소 값, length와 마지막 위치, 누적값의 현재 상태, 초기화 위치. 인덱스 불필요 시 향상 for 대안도 비교. |
| 7 메서드·값 전달 | 실제 인자의 값은 새 매개변수를 초기화한다. 반환 타입과 지역 범위는 별도 규칙이다. [§8.4.1](https://docs.oracle.com/javase/specs/jls/se25/html/jls-8.html#jls-8.4.1), [§8.4.5](https://docs.oracle.com/javase/specs/jls/se25/html/jls-8.html#jls-8.4.5), [§6.3](https://docs.oracle.com/javase/specs/jls/se25/html/jls-6.html#jls-6.3), [§14.17](https://docs.oracle.com/javase/specs/jls/se25/html/jls-14.html#jls-14.17) | 배송비 메서드의 인자 이름만 바꾼 경우와 반환값을 실제 저장한 경우 비교. 0·기준 직전·기준값 사용. | 선언/호출, 인자/매개변수, 출력/반환, 호출 전후 값, void. 전체 프로그램 작성 없이 호출부와 한 반환식부터 검토 가능. |
| 8 객체·참조 | 여러 참조가 같은 객체를 가리키면 한쪽 상태 변경이 다른 참조에서도 보인다. final 참조도 객체 불변을 뜻하지 않는다. [§4.3.1](https://docs.oracle.com/javase/specs/jls/se25/html/jls-4.html#jls-4.3.1), [§4.12.4](https://docs.oracle.com/javase/specs/jls/se25/html/jls-4.html#jls-4.12.4) | 주문 a의 참조를 b에 대입한 경우와 새 주문을 만든 경우 비교. b의 필드 변경/지역 참조 재대입을 분리. null 역참조를 정상 결과 예제로 쓰지 않음. | 클래스/객체/참조 변수, new/생성자, this, 별칭 공유. Java는 참조도 값으로 전달하므로 매개변수 재대입과 객체 변경을 구분. |
| 8 동일성·동등성 보강 | 기본 Object.equals는 같은 객체일 때 참이다. 내용 동등성은 클래스의 계약에 달린다. equals를 재정의하면 hashCode 계약도 함께 고려한다. [Object.equals/hashCode](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Object.html#equals(java.lang.Object)) | 필드가 같은 두 주문을 동일 객체라고 단정하는 대안 비교. 고급 동등성 구현은 준비 코드의 계약부터 설명. | `==`/equals, 값 기준의 정의, 사용자 클래스의 기본 동작. 문자열·래퍼의 우연한 동일성에 의존하지 않음. |
| 9 인스턴스·static | static 필드는 클래스에 한 개, 인스턴스 필드는 객체마다 생긴다. static 메서드는 특정 객체 없이 호출한다. [§8.3.1.1](https://docs.oracle.com/javase/specs/jls/se25/html/jls-8.html#jls-8.3.1.1), [§8.4.3.2](https://docs.oracle.com/javase/specs/jls/se25/html/jls-8.html#jls-8.4.3.2) | 두 주문의 금액과 전체 생성 수를 각각 바꿔 소속 비교. 독립 문제마다 공유 상태 초기화. | 필드/지역 변수, 클래스명 호출/객체 호출, 공유 범위. static을 프로그램 전체 영구 저장으로 표현하지 않음. |
| 9 초기화 보강 | 기본값 준비와 명시적 초기화는 다르다. static 초기화는 사용 조건에 따라 발생하고 소스 순서를 따른다. 객체 필드도 먼저 기본값을 받는다. Java 25 생성자 절차에는 super 호출 전 허용된 prologue가 있다. [§12.3.2](https://docs.oracle.com/javase/specs/jls/se25/html/jls-12.html#jls-12.3.2), [§12.4.1–2](https://docs.oracle.com/javase/specs/jls/se25/html/jls-12.html#jls-12.4.1), [§12.5](https://docs.oracle.com/javase/specs/jls/se25/html/jls-12.html#jls-12.5) | 한 클래스의 static 초기값과 두 객체 필드 초기값 비교. 복잡한 상속/상호 초기화는 초기 필수에서 분리하는 후보. | 선언/초기화/생성, 생성자와 일반 메서드, 초기식 순서. “모든 static은 시작 때”, “super는 언제나 문법상 첫 줄”로 일반화 금지. |
| 10 인터페이스·호출 | 인터페이스 타입과 구현 객체를 구분한다. 호출 가능한 계약과 실제 구현 선택은 별도다. [§9.1](https://docs.oracle.com/javase/specs/jls/se25/html/jls-9.html#jls-9.1), [§8.1.5](https://docs.oracle.com/javase/specs/jls/se25/html/jls-8.html#jls-8.1.5), [§15.12.4.4](https://docs.oracle.com/javase/specs/jls/se25/html/jls-15.html#jls-15.12.4.4) | 같은 저장 인터페이스에 메모리 구현 두 개를 교체하고 호출부 변화 비교. 초기에는 실제 파일 실패를 섞지 않음. | implements, 선언 타입/실제 객체, Override, 메서드 시그니처. 상속과 조합을 동일시하지 않음. |
| 10 캡슐화 보강 | private의 접근 범위는 선언을 둘러싼 최상위 클래스 내부다. 접근 규칙은 도메인 규칙의 타당성을 자동 보장하지 않는다. [§6.6.1](https://docs.oracle.com/javase/specs/jls/se25/html/jls-6.html#jls-6.6.1) | 금액 직접 대입과 검증 메서드를 통한 변경 비교. 음수 거부가 제품 요구인지 먼저 명시. | public/private, 외부 호출과 내부 상태, 불변식. getter/setter를 기계적으로 추가하는 것만으로 캡슐화 완료라 하지 않음. |

## 11~13: 자료와 실패 경로

| 지도 | 관계와 직접 확인 근거 | 작은 비교·안전 경계 후보 | 먼저 빠뜨리면 안 되는 기초 |
| --- | --- | --- | --- |
| 11 리스트 | List는 순서·중복·위치 선택, ArrayList는 크기 변경 구현이다. `List.of`는 수정 불가이며 null을 허용하지 않는다. [List](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/List.html), [ArrayList](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/ArrayList.html) | 주문 0/1/2개와 같은 값 중복. 수정할 목록에 `List.of`를 고르는 대안 검토. | 배열 length와 List.size(), get/set/add/remove, 수정 가능 여부. `remove(int)`와 `remove(Object)`의 정확한 오버로드는 사용할 때 별도 실행 대조. |
| 11 맵 | Map은 키당 한 매핑, put은 기존 값을 교체한다. get의 null만으로 없음/값null을 구분할 수 없다. HashMap 순서는 보장하지 않는다. [Map](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Map.html), [HashMap](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/HashMap.html) | 주문번호 1에 두 번 저장 vs 다른 번호 저장. 없는 번호 조회. 순서 고정 출력 채점 피함. | 키/값, 번호/위치, 중복키 정책, containsKey. Map.of의 중복키 오류를 mutable put 교체와 혼동하지 않음. |
| 11 제네릭 | 매개변수화 타입은 타입 인자로 사용 범위를 표현한다. 기본형은 타입 인자가 될 수 없다. [JLS §4.5–4.5.1](https://docs.oracle.com/javase/specs/jls/se25/html/jls-4.html#jls-4.5) | `List<String>`에 문자열/정수 추가 후보 비교. `List<int>` 대신 Integer가 필요한 이유 검토. | 타입 인자, 참조 타입/기본형, boxing/unboxing의 최소 의미, 컴파일 오류/실행 오류. raw type·복잡한 wildcard·타입 소거는 별도 확장 가능. |
| 12 람다 | 람다는 목표 함수형 인터페이스에 맞는 동작을 표현한다. 캡처한 지역 이름은 final/effectively final이어야 한다. [§9.8](https://docs.oracle.com/javase/specs/jls/se25/html/jls-9.html#jls-9.8), [§15.27.2–3](https://docs.oracle.com/javase/specs/jls/se25/html/jls-15.html#jls-15.27.2) | 한 주문에서 조건을 판정하는 메서드와 같은 판단의 람다 비교. 외부 누적 지역변수 수정은 첫 예시로 피함. | 입력→반환, Predicate/Function의 구별, 화살표 몸체, 이름 범위. “람다 생성 즉시 본문 실행”으로 읽지 않음. |
| 12 스트림 | source→중간 연산→종단 연산이다. 지연 실행하며 한 번만 사용한다. filter와 map의 반환 역할이 다르다. `toList()` 결과는 수정 불가다. [Stream](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/stream/Stream.html) | 주문 0/1/여러 개에서 반복문과 선별·변환 결과 비교. 같은 스트림 재사용 대신 새 source.stream(). | 목록/스트림/결과, 선별/변환/합계. 순차 처리부터 검증하고 부수효과 출력 횟수를 채점 근거로 삼지 않음. |
| 13 예외 | throw는 실패 발생, catch는 처리, throws는 계약 전달이다. checked/unchecked는 컴파일 검사와 관련하며 복구 가능성의 단순 분류가 아니다. [JLS §11.1–11.2](https://docs.oracle.com/javase/specs/jls/se25/html/jls-11.html), [§14.20](https://docs.oracle.com/javase/specs/jls/se25/html/jls-14.html#jls-14.20) | 잘못된 금액 문자열과 파일 읽기 실패를 분리. 실패 뒤 성공 메시지를 출력하는 대안 검토. | 정상 반환/예외 경로, 예외 타입, 좁은 catch, 전파. 무조건 빈 목록을 반환하는 정책은 별도 요구 판단. |
| 13 파일 | readString/writeString 기본 문자셋은 UTF-8. writeString의 무옵션은 생성 또는 기존 파일 절단이다. IOException이 가능하다. [Files.readString/writeString](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/nio/file/Files.html#readString(java.nio.file.Path)) | 전용 임시 파일에 저장→새 객체로 읽기; 없음·빈 파일·잘못된 형식 비교. 원본 파일 덮어쓰기 피함. | 메모리 수명/파일 수명, 경로/문자열, 상대 작업 위치, 직렬화 형식/검증. API 호출 성공만으로 저장 포맷 타당성을 보장하지 않음. |

## 14~16: 작은 앱과 검증

| 지도 | 확인된 도구·언어 근거 | 비교/경계 검토 후보와 빠진 기초 |
| --- | --- | --- |
| 14 CRUD·책임 분리 | Map.put/get/remove와 List 수정 API는 저장 동작의 근거다. 입력/처리/저장으로 나누는 설계 자체를 API가 강제하지 않는다. [Map](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Map.html), [List](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/List.html) | 기존/없는 번호 수정·삭제, 중복번호, 빈 내용. 입력 해석→대상 선택→변경→저장이라는 상태 차이를 따로 관찰. 컬렉션 하나만 만든 것을 파일 영속화 완료로 취급하지 않음. |
| 15 JUnit | 공식 최소 예시는 `@Test` 메서드 안에서 expected/actual을 단언한다. [JUnit 첫 테스트](https://docs.junit.org/6.1.3/writing-tests/intro.html) | 같은 배송비 계산을 기준 직전/정확한 값/직후로 검증. 준비·행동·확인은 구성 후보이며 JUnit이 특정 교수법을 입증하지 않음. 출력 관찰과 실패하는 단언의 차이가 선수. |
| 15 AssertJ | `assertThat(actual)`만으로는 검증하지 않는다. `isEqualTo` 등 확인 호출이 필요하다. [공식 Incorrect API usage](https://assertj.github.io/doc/#assertj-core-incorrect-api-usage) | 잘못된 값에 체인 시작만 둔 테스트와 실제 단언 비교. 테스트가 통과했다는 사실과 목표 동작을 검사했다는 사실 구분. 긴 체인·고급 재귀 비교는 첫 필수로 정하지 않음. |
| 15 Gradle | Java/JVM Test 설정에서 JUnit Platform을 실행하도록 설정할 수 있다. [Gradle Java testing](https://docs.gradle.org/current/userguide/java_testing.html) | 실제 실행된 테스트/0개 발견/컴파일 실패를 구분해 검증하는 후보. 빌드와 앱 실행·테스트 실행, 의존성과 import, wrapper와 프로젝트 설정이 선수. 설정 파일 전체 타이핑을 목표로 삼지 않음. |
| 16 요청·계산기 | `Integer.parseInt`는 해석 불가능하거나 int 범위 밖이면 NumberFormatException. [Integer.parseInt](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Integer.html#parseInt(java.lang.String)) | 빈 입력·공백만·정상 숫자·범위 밖·잘못된 기호는 요구별로 정할 반례다. split/trim, 구분자, 부호, 연산 우선순위, 0 나눗셈을 한 번에 숨기지 않음. 파서가 지원할 문법은 제품 계약이며 JLS 표현식 문법과 동일하다고 가정하지 않음. |

## 누락을 막는 관계 연결

이 절은 전체 범위 위임에 따른 **검토 제안**이며 새 교수법 채택이나 고정 수업 수가 아니다.

1. 반복 전에 갱신식·누적값·배열 생성과 읽기를 확인한다. 메서드 분리 전에 호출부·반환·범위를 확인한다.
2. 객체 공유를 인자값 전달에 다시 연결한다. 필드 변경과 매개변수 재대입을 같은 “원본 변경”으로 묶지 않는다.
3. 생성자·필드 초기화와 static을 충분히 분리한다. 상속 호출·오버라이딩·오버로딩·static 숨김의 필요성을 발견하면 별도 단원으로 보강한다. 현재 18개 묶음이 이를 모두 이미 가르친다는 뜻은 아니다.
4. List/Map 도입 전에 참조 공유와 메서드 호출을 다시 확인한다. 제네릭은 무엇이 들어오고 나가는지부터 연결하고 boxing·null 경계를 누락하지 않는다.
5. 인터페이스→함수형 인터페이스→람다→스트림의 관계를 확인한다. “짧게 쓰기”보다 조건·변환·결과의 역할과 같은 결과가 되는 전제 확인이 우선이라는 설계 후보다.
6. 앱 저장 전에 예외·경로·포맷·불러온 뒤 재구성이 필요하다. 파일이 남는 것과 객체가 메모리에 남는 것을 구분한다.
7. 테스트 도구의 초록 표시만으로 끝내지 않고 실패할 입력이 실제 실패하는지 검증한다. 변경 요구와 반례의 연결은 자체 설계 판단이며 비공개 정답을 베낀 테스트로 대체하지 않는다.

## 아직 확정하지 않은 것

- 예시의 실제 Java 실행·JUnit/AssertJ/Gradle 조합·컴파일 오류 문구·파일시스템 예외 유형은 미검증이다. 각 제작 단위에서 사용 버전과 실행 증거를 따로 남겨야 한다.
- CRUD 구조의 최선 분할·도메인 예외 정책·파일 형식·계산식/요청 문자열 문법은 공식 언어/API만으로 정해지지 않는다.
- 상속·오버로딩·boxing·Optional·컬렉션 동등성·try-with-resources가 필요한 실제 예시를 선택하면 정확한 관련 절/API를 더 열고 해당 범위를 검증해야 한다. 이 노트가 관련 전 주제를 완전히 조사했다는 뜻은 아니다.
- Gradle `current`와 JUnit 리디렉션은 향후 바뀔 수 있다. 원문 링크의 최신 상태와 프로젝트에 고정한 버전을 구분한다. AssertJ 정확한 채택 버전과 기존 강의 원문 매핑은 미확인이다.
- Kotlin·새 교수법·PRD 승인·production 수정은 수행하지 않았다. 조사 범위 충족을 실제 수업 제작·수료 검증 완료로 기록하면 안 된다.
