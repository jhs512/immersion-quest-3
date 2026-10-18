# AICE Python 기초와 표 데이터 사이의 선수 지식 조사

확인일: 2026-10-19 (한국 시간). Python 공식 `/3.10/` 언어 참조·튜토리얼을 직접 열었다. 표제는 **Python 3.10.22 documentation**이다. 시험 가이드의 Python 3.10.13과 패치 버전이 같다는 뜻이 아니며 시험 커널·플레이어에서는 실행하지 않았다. 수업 2·3의 범위 검토를 위한 내부 근거이며 수업 PRD·본문·문제·구현을 만들지 않았다.

## 비교·조건·반복

| 항목 | 확인된 언어 사실 | 1차 출처 |
| --- | --- | --- |
| 비교 | `<`, `<=`, `>`, `>=`, `==`, `!=`는 각각 작음·이하·큼·이상·같음·다름이다. 값 비교 `==`와 객체 동일성 `is`를 혼용하지 않는다. | [Built-in Types: Comparisons](https://docs.python.org/3.10/library/stdtypes.html#comparisons) |
| bool·진릿값 | `True`·`False`는 불리언 값이다. 조건에서는 다른 객체도 진릿값 검사를 받으며 0·빈 문자열·빈 리스트·빈 딕셔너리 등은 거짓이다. 문자열 `'False'`를 불리언 `False`와 동일시하면 안 된다. | [Truth Value Testing](https://docs.python.org/3.10/library/stdtypes.html#truth-value-testing) |
| 논리 연산 | `and`·`or`는 필요한 경우에만 오른쪽을 평가하며 피연산자 중 하나를 반환한다. 항상 새 bool을 반환한다고 일반화하지 않는다. `not`은 bool을 반환한다. | [Boolean Operations](https://docs.python.org/3.10/library/stdtypes.html#boolean-operations-and-or-not) |
| if | 조건을 순서대로 검사하고 처음 참인 분기만 실행한다. 모두 거짓이면 존재하는 `else`를 실행한다. 조건별 `if` 여러 개와 하나의 `if/elif/else` 사슬을 동일하게 취급하면 안 된다. | [Language Reference 8.1](https://docs.python.org/3.10/reference/compound_stmts.html#the-if-statement) |
| 블록 | `if`·`for` 뒤의 콜론과 들여쓰기는 구문 구조다. 같은 블록의 문장은 같은 들여쓰기 수준으로 묶인다. | [Compound statements 도입](https://docs.python.org/3.10/reference/compound_stmts.html) |
| for | 리스트의 항목을 나타난 순서대로 순회한다. 반복 변수는 자동 인덱스가 아니라 각 항목을 받는다. 순회 중 같은 컬렉션을 변경하는 경우는 별도 검토가 필요하다. | [Tutorial 4.2](https://docs.python.org/3.10/tutorial/controlflow.html#for-statements) |

## 딕셔너리와 여러 레코드

- 딕셔너리는 키와 값의 쌍으로 구성되며 `{키: 값}` 표기를 사용한다. 기존 키로 다시 저장하면 그 키의 값을 바꾼다. [Tutorial 5.5](https://docs.python.org/3.10/tutorial/datastructures.html#dictionaries)
- 일반 `dict`에서 `record['키']`는 그 키에 연결된 값을 읽는다. 없는 키는 `KeyError`다. 문자열 키의 따옴표를 빼면 문자열 대신 이름을 평가하므로 서로 다른 구문이다. [Mapping Types: dict](https://docs.python.org/3.10/library/stdtypes.html#mapping-types-dict), [Subscriptions](https://docs.python.org/3.10/reference/expressions.html#subscriptions)
- 리스트 항목으로 딕셔너리를 넣을 수 있다. `rows[0]['키']`는 리스트에서 첫 딕셔너리를 고른 뒤 그 딕셔너리의 키를 고르는 두 선택이다. 이는 리스트 표시·딕셔너리 표시·구독 규칙을 조합한 도출이며 이번에 실행한 예제가 아니다. [List displays](https://docs.python.org/3.10/reference/expressions.html#list-displays), [Dictionary displays](https://docs.python.org/3.10/reference/expressions.html#dictionary-displays), [Subscriptions](https://docs.python.org/3.10/reference/expressions.html#subscriptions)
- `for record in rows`는 각 레코드를 받지만 `for key in record`는 딕셔너리 키를 순회한다. 행 목록·한 레코드·한 필드 값을 구별해야 한다. [Tutorial 4.2](https://docs.python.org/3.10/tutorial/controlflow.html#for-statements), [dict의 iter](https://docs.python.org/3.10/library/stdtypes.html#mapping-types-dict)

## 라이브러리 API를 읽는 표기

| 항목 | 확인된 사실과 혼동 지점 | 1차 출처 |
| --- | --- | --- |
| 함수 호출 | 괄호 안의 인자 표현식은 호출 전에 평가된다. 함수 이름만 읽는 것과 괄호로 호출하는 것은 다르다. 호출은 값을 반환하며 그 값은 `None`일 수도 있다. | [Calls](https://docs.python.org/3.10/reference/expressions.html#calls) |
| 키워드 인자 | `name=value`는 호출에서 매개변수 이름으로 값을 전달하는 구문이다. 일반적인 호출에서는 위치 인자 뒤에 키워드 인자를 쓴다. 중복 지정·미지원 이름은 오류가 될 수 있다. 이 표기는 호출 밖 대입문이나 `==` 비교와 역할이 다르다. | [Tutorial 4.8.2](https://docs.python.org/3.10/tutorial/controlflow.html#keyword-arguments), [Calls](https://docs.python.org/3.10/reference/expressions.html#calls) |
| import 별칭 | `import module as alias`는 찾고 불러온 모듈을 별칭 이름에 연결한다. 별칭은 Python의 고정 예약명이 아니다. 불러오기 성공을 패키지 설치·버전 검증과 동일시하지 않는다. | [Import statement](https://docs.python.org/3.10/reference/simple_stmts.html#the-import-statement) |
| 속성 | `object.name`은 객체에 해당 속성을 요청한다. `object.name(...)`은 그 결과가 호출 가능한 경우 호출을 추가한다. 점 뒤 이름을 모든 객체에서 같은 뜻이라고 해석하면 안 된다. 없는 속성은 `AttributeError`가 될 수 있다. | [Attribute references](https://docs.python.org/3.10/reference/expressions.html#attribute-references), [Calls](https://docs.python.org/3.10/reference/expressions.html#calls) |

## pandas로 자동 확장하면 안 되는 부분

이번 조사 대상은 Python 내장 값과 일반 구문이다. 표·Series에 대한 비교 결과, 여러 조건을 결합하는 연산자, 열 이름 선택, 라벨 정렬, 표의 진릿값은 객체가 정하는 별도 규칙이다. 내장 단일 숫자·딕셔너리에서 확인한 결과를 pandas 전체에 그대로 적용하는 근거는 아니다. pandas 범위는 [별도 1.5 문서 조사](aice-pandas-foundations-2026-10-19.md)를 따른다.

특히 딕셔너리의 목록과 리스트 열을 담은 딕셔너리는 바깥 구조가 다르다. 각각의 언어 표기를 읽을 근거는 위에 있으나 어떤 구조를 DataFrame으로 바꿀지, 어떤 pandas 생성 API를 쓸지는 그 API의 문서와 별도로 대조해야 한다.

## 미확정 범위

이 노트는 최소 선수 표기와 혼동 지점을 조사했다. 해당 항목을 모두 수업 2·3에 채택하거나 이 순서대로 가르치기로 결정한 것은 아니다. 함수 직접 정의·가변 인자·컴프리헨션·복사와 공유·예외 처리·객체 모델 전체는 이번 필수 범위로 정하지 않았다.

AICE 출제 비중·공식 기출·미공개 채점 알고리즘·최신 패키지 버전은 재조사하지 않았다. 시험 관련 사실과 접근 한계는 [기존 Python 기초 조사](aice-python-foundations-2026-10-19.md)를 따른다. 공식 시험 데이터·문제·정답은 사용하지 않았으며 이 문서는 공식 시험 환경 재현이나 교육 기법 효과의 증거가 아니다.
