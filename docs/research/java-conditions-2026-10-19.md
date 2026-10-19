# Java 비교·조건 수업을 위한 조사

확인일: 2026-10-19 (한국 시간). Oracle의 Java SE 25 JLS만 직접 열어 확인했다. 승인된 값 수업 다음의 PRD를 위한 조사이며 다음 수업 승인·학습 콘텐츠·핵심 흐름·해설 대본을 작성한 것이 아니다. 아래 숫자는 배송비라는 한 상황을 유지하기 위한 자체 검토값이다. 실행 검증 결과나 원자료의 수업 예제가 아니다.

## 확인한 언어 규칙

| 범위 | 확인된 사실 | 정확한 근거 |
| --- | --- | --- |
| int 비교 | `<`·`<=`·`>`·`>=`는 미만·이하·초과·이상이며 결과는 `boolean`이다. | [JLS §15.20, §15.20.1](https://docs.oracle.com/javase/specs/jls/se25/html/jls-15.html#jls-15.20.1) |
| int 동등성 | `==`는 같음, `!=`는 다름을 판단한다. 대입 `=`와 역할이 다르다. | [§15.21.1](https://docs.oracle.com/javase/specs/jls/se25/html/jls-15.html#jls-15.21.1), [§15.26.1](https://docs.oracle.com/javase/specs/jls/se25/html/jls-15.html#jls-15.26.1) |
| boolean | 값은 `true`·`false` 두 가지다. 정수를 조건으로 자동 해석하지 않는다. | [§4.2.5](https://docs.oracle.com/javase/specs/jls/se25/html/jls-4.html#jls-4.2.5) |
| if 조건 | 조건식은 `boolean` 또는 `Boolean`이어야 한다. 이번 범위는 기본형 `boolean`으로 제한한다. `if (1)`은 컴파일 오류다. | [§14.9](https://docs.oracle.com/javase/specs/jls/se25/html/jls-14.html#jls-14.9) |
| if 실행 | 참이면 본문을 실행하고 거짓이면 건너뛴다. | [§14.9.1](https://docs.oracle.com/javase/specs/jls/se25/html/jls-14.html#jls-14.9.1) |
| if/else | 정상 평가된 조건이 참이면 앞 문장, 거짓이면 뒤 문장 하나만 실행한다. | [§14.9.2](https://docs.oracle.com/javase/specs/jls/se25/html/jls-14.html#jls-14.9.2) |
| 별개 if와 else if | 정상적으로 순차 진행하는 별개 `if`는 각각 평가된다. `else if`는 앞 조건이 거짓일 때 실행되는 뒤쪽 `if`라는 문장 조합이다. 앞 조건이 참이면 뒤쪽 조건은 평가하지 않는다. | [§14.2](https://docs.oracle.com/javase/specs/jls/se25/html/jls-14.html#jls-14.2), [§14.9 문법·§14.9.2](https://docs.oracle.com/javase/specs/jls/se25/html/jls-14.html#jls-14.9.2) |
| 조건 결합 | `&&`는 왼쪽부터 평가하며 왼쪽이 거짓이면 오른쪽을 평가하지 않는다. 두 피연산자는 `boolean`/`Boolean`이어야 한다. | [§15.23](https://docs.oracle.com/javase/specs/jls/se25/html/jls-15.html#jls-15.23) |

## 안전한 경계 검토값

주문금액 `amount`와 기준 20,000원을 사용한 명세 도출이다. 작은 비음수 `int`와 부수효과 없는 식만 다룬다.

| amount | `< 20000` | `<= 20000` | `> 20000` | `>= 20000` | `== 20000` | `!= 20000` |
| --- | --- | --- | --- | --- | --- | --- |
| 19999 | true | true | false | false | false | true |
| 20000 | false | true | false | true | true | false |
| 20001 | false | false | true | true | false | true |

근거: [§15.20.1](https://docs.oracle.com/javase/specs/jls/se25/html/jls-15.html#jls-15.20.1), [§15.21.1](https://docs.oracle.com/javase/specs/jls/se25/html/jls-15.html#jls-15.21.1). 기준값과 정확히 같은 사례를 빼면 `>`와 `>=`의 차이를 판별할 수 없다.

## 오해와 범위 제한

- 숫자 조건의 `=`는 `==`의 짧은 표기가 아니다. 다만 대입을 조건에 쓰면 항상 문법 오류라는 일반화도 피한다. 이번 수업에서는 조건 내부 대입을 사용하지 않는 안이 적절하다. [§15.26.1](https://docs.oracle.com/javase/specs/jls/se25/html/jls-15.html#jls-15.26.1), [§14.9](https://docs.oracle.com/javase/specs/jls/se25/html/jls-14.html#jls-14.9)
- `a < b < c`를 수학식처럼 쓰면 안 된다. 두 비교를 결합해야 한다. [§15.20](https://docs.oracle.com/javase/specs/jls/se25/html/jls-15.html#jls-15.20)
- 별개 `if` 두 개가 모두 참이면 뒤쪽 대입으로 배송비를 다시 바꿀 수 있다. 조건 순서와 연결 방식은 사업 규칙과 함께 판단해야 한다. [§14.2](https://docs.oracle.com/javase/specs/jls/se25/html/jls-14.html#jls-14.2), [§14.9.1–2](https://docs.oracle.com/javase/specs/jls/se25/html/jls-14.html#jls-14.9.1)
- 정수 동등성만 확인했으므로 문자열 내용 비교나 참조 동일성으로 일반화하지 않는다. 부동소수점·래퍼·null·중첩 분기·삼항 연산자·switch는 이번 필수 범위로 정하지 않았다.

`&&`는 명세상 확인됐지만 첫 조건 수업에 반드시 넣을 필요는 없다는 조사자의 제안이다. 단일 기준과 분기 구조를 익힌 뒤 두 조건이 필요한 다음 범위로 남길 수 있다. 포함한다면 회원 여부와 금액 조건을 결합하는 정도로 제한하고 예외·함수 부수효과를 새 선수 지식으로 요구하지 않는 안을 권한다. 단락 평가의 관찰을 학습 완료 필수로 채택한 것은 아니다.

## 승인 전 8스텝 배열 후보

이는 제작용 스텝 원문이나 교육 효과가 입증된 방법이 아니다. 사용자 방향인 낮은 타이핑 부담·이어지는 배송비 상황·AI 코드의 선택 이유 이해에 맞춘 조사자의 제한된 제안이다. 각 스텝의 교육 목표·핵심 흐름·판정은 다음 PRD에서 별도로 정해야 한다.

1. 무료배송의 금액 기준을 비교 결과와 연결한다.
2. 같은 기준의 직전·정확한 값·직후를 비교한다.
3. 정확히 같은 금액과 다른 금액을 구별한다.
4. 판단 결과를 `boolean` 이름에 연결해 읽는다.
5. 기본 배송비에서 조건에 맞을 때만 무료로 바꾸는 흐름을 본다.
6. `else`로 두 배송비 중 하나를 선택한다.
7. 높은 금액 할인·낮은 금액 할인 조건이 겹치는 경우 별개 `if`와 사슬의 차이를 본다.
8. 새 금액으로 AI 코드의 경계·분기 선택을 검토하고 최소 수정 이유를 확인한다.

수치 정책 후보는 20,000원 이상 무료 한 가지로 시작한다. 7번에서만 별도 할인 구간을 추가할지 검토한다. 정책의 숫자·할인 액수 자체는 JLS 사실이 아니며 아직 확정하지 않았다. `&&`를 억지로 이 8개에 추가하지 않는 안이다.

## 검증 한계

JLS 25 언어 의미만 확인했다. 실제 플레이어 JDK·컴파일 명령·실행 출력·입력 편집 및 채점 방식은 확인하지 않았다. 경계 표는 컴파일러 실행 로그가 아니며 생산용 정답 코드도 아니다. 기존 승인된 값 수업의 변경·다음 PRD 승인·수업 제작은 이번 작업에 포함하지 않았다.
