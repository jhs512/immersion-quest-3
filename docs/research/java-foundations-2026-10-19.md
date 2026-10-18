# Java 기초 수업 PRD를 위한 언어 사실 확인

확인일: 2026-10-19 (한국 시간). Java SE 25 언어 명세를 직접 열어 확인했다. 첫 값·표현식 수업의 범위 판단에 필요한 내부 조사이며 수업 본문, 교육 기법 채택, 문제·정답 코드 제작은 아니다. 아래 짧은 식의 결과는 명세에서 도출한 것으로 이번 조사에서 Java 실행기로 실행하지 않았다.

## 원자료의 확인 한계

- [원글 14146](https://slog.gg/p/14146)은 이번 웹 도구에서 접근 불가였다. 원글의 실제 제목·본문·예제·난이도·순서는 확인하지 못했으며 원글을 읽은 것으로 취급하면 안 된다.
- 저장소 `tools/backend_course/foundations.py`의 14146 참조는 출처 연결의 내부 흔적이다. 원문을 보존했다는 증거는 아니다. 원문과 새 수업의 일치 여부는 별도 확인이 필요하다.
- `dev.java`는 이번 조사 근거로 사용하지 않았다. 아래 근거는 Oracle이 공개한 Java SE 25 JLS다.

## 확인된 언어 규칙

### 값 표기와 타입

- 접미사 없는 정수 리터럴은 `int`, `L`/`l` 접미사가 있으면 `long`이다. 부동소수점 리터럴은 `F`/`f`가 있으면 `float`, 없으면 `double`이다. 따라서 `2`와 `2.0`은 같은 표기가 아니다. [JLS 3.10.1](https://docs.oracle.com/javase/specs/jls/se25/html/jls-3.html#jls-3.10.1), [3.10.2](https://docs.oracle.com/javase/specs/jls/se25/html/jls-3.html#jls-3.10.2)
- 문자열 리터럴은 큰따옴표로 감싸며 빈 문자열도 가능하고 타입은 `String`이다. 따라서 `2`와 `"2"`를 구분해야 한다. 작은따옴표 문자 리터럴까지 한꺼번에 숫자와 문자열의 두 종류로 일반화하지 않는다. [JLS 3.10.4](https://docs.oracle.com/javase/specs/jls/se25/html/jls-3.html#jls-3.10.4), [3.10.5](https://docs.oracle.com/javase/specs/jls/se25/html/jls-3.html#jls-3.10.5)

### 계산과 문자열 연결

- `+`의 한쪽 피연산자가 `String`이면 문자열 연결이며 다른 쪽도 문자열로 변환한다. `+`와 `-`는 같은 우선순위이고 왼쪽으로 묶인다. 따라서 `1 + 2 + "개"`는 `"3개"`, `"개" + 1 + 2`는 `"개12"`, `"개" + (1 + 2)`는 `"개3"`이다. [JLS 15.18 및 15.18.1](https://docs.oracle.com/javase/specs/jls/se25/html/jls-15.html#jls-15.18)
- 곱셈 계열은 덧셈 계열보다 강하게 묶이며 괄호는 묶음을 바꾼다. `2 + 3 * 4`와 `(2 + 3) * 4`는 각각 14와 20이다. 이 우선순위와 이항 연산자의 왼쪽 피연산자 먼저 평가 규칙을 혼동하지 않는다. [JLS 15.7.1](https://docs.oracle.com/javase/specs/jls/se25/html/jls-15.html#jls-15.7.1), [15.7.3](https://docs.oracle.com/javase/specs/jls/se25/html/jls-15.html#jls-15.7.3), [15.17](https://docs.oracle.com/javase/specs/jls/se25/html/jls-15.html#jls-15.17)
- 정수 나눗셈은 0 방향으로 버린다. `5 / 2`는 2다. 산술 피연산자 중 `double`이 있으면 수치 승격으로 `double` 연산을 하므로 `5 / 2.0`은 2.5다. [JLS 15.17.2](https://docs.oracle.com/javase/specs/jls/se25/html/jls-15.html#jls-15.17.2), [5.6](https://docs.oracle.com/javase/specs/jls/se25/html/jls-5.html#jls-5.6)

### 변수와 대입

- 변수는 타입이 연결된 저장 위치다. 대입은 저장된 값을 바꾸며 타입 호환성 검사를 받는다. 지역 변수는 읽기 전에 초기화 또는 대입되어야 한다. 필드의 기본값 규칙을 지역 변수에 적용하면 안 된다. [JLS 4.12](https://docs.oracle.com/javase/specs/jls/se25/html/jls-4.html#jls-4.12), [4.12.5](https://docs.oracle.com/javase/specs/jls/se25/html/jls-4.html#jls-4.12.5), [15.26.1](https://docs.oracle.com/javase/specs/jls/se25/html/jls-15.html#jls-15.26.1)
- 지역 변수 선언은 초기값을 포함할 수 있다. 선언의 초기식은 선언문 실행 시 평가되어 저장된다. `int total = price * 2;`는 이후 `price`가 바뀔 때 자동 재계산되는 관계 선언이 아니다. 다시 계산하려면 표현식을 다시 평가하여 대입해야 한다. [JLS 14.4.2](https://docs.oracle.com/javase/specs/jls/se25/html/jls-14.html#jls-14.4.2)

## PRD에 넘기는 범위와 미확인 사항

- 확인된 구별은 숫자/숫자 모양 문자열, 수치 덧셈/문자열 연결, 우선순위/괄호, 정수/부동소수점 나눗셈, 초기화/재대입/현재 값이다. 이는 언어 사실이며 수업 순서나 필수 문제 수를 결정하는 연구 근거는 아니다.
- 최소 타이핑, 점진적인 작은 문제, AI가 만든 코드의 선택 이유를 이해한다는 사용자 방향은 제품 요구다. JLS가 해당 교육 방식의 학습 효과를 검증한다고 주장하지 않는다.
- 명세 전체를 첫 수업 범위로 옮기지 않는다. 상속·컬렉션·예외·모든 타입·형 변환·증감/복합 대입·오버플로·부동소수점 정밀도·문자열 객체 동일성은 이번 첫 수업의 필수 범위로 결정하지 않았다.
- 실제 플레이어의 실행 JDK, 출력 API/보일러플레이트, 입력 편집 단위, 채점 방식은 조사하지 않았다. 명세 버전 25 확인과 런타임 버전 확인은 별개다.
