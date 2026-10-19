# 정보처리기사 실기: C3~7·Java8~11·Python12~13 언어 근거

확인일: **2026-10-19**. 정보처리기사 독립 코스 지도에 대한 제작자용 조사다. Java 백엔드·AICE 수업이나 학습 기록과 공유하지 않는다. 생산 콘텐츠·PRD·채점기·런타임은 변경하지 않았다.

## 출처 판과 검증 수준

- C: [WG14 N1570](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf), **2011-04-12 C11 계열 공개 위원회 초안**. PDF 해당 절을 직접 읽었다. 시험이 이 표준을 지정했다는 뜻은 아니다.
- Java: Oracle **Java SE25 JLS**의 아래 링크 절을 직접 확인했다. 실제 시험 Java 버전은 미확인이다. Java25의 간소화 main·생성자 신기능을 기존 시험 코드의 필수 전제로 삼지 않는다.
- Python: 공식 **3.14 버전 경로**를 사용했다. 확인 시 문서 표제는3.14.8이며 `/3/`는3.15로 연결되어 피했다. 문서 판과 앱 설치 인터프리터·시험 환경을 동일시하지 않는다.
- 아래 코드·예상값은 **직접 만든 검토 사례이며 이번 조사에서는 실행하지 않은 언어 규칙 기반 추론**이다. 코드 조각은 표준 헤더·완전한 클래스/함수·main 등 필요한 틀에 배치한다. 제작 시 실제 빌드·실행과 경계 판정을 확인한다.

## C3~7 매트릭스

| 지도 수업 | 확인할 관계 | 원문의 정확한 절 | 안전한 작은 검토 사례·예상값 |
| --- | --- | --- | --- |
| 3 반복·배열·문자열 | 반복 조건은 검사 시점이 있고 배열 인덱스는0부터다. 문자열은 끝의 널 문자까지 포함한 저장소가 필요하다. | N1570 §6.8.5.1~3, §6.5.2.1¶2, §6.4.5¶6, §7.1.1¶1, §7.24.6.3 | `int a[3]={2,4,1}; int total=0; for(int i=0;i<3;i++){total=total+a[i];}` → total7. `char label[]="AB"; label[0]='C';` → 문자열CB, strlen2, 배열요소3. |
| 4 함수·재귀 | 인자 값이 매개변수에 전달된다. 반환·재귀 호출은 각 호출의 상태로 추적한다. | §6.5.2.2¶7·10~11, §6.9.1¶9~11, §6.8.6.4 | `int down(int n){if(n==0){return 0;} return n+down(n-1);}` → down(3)=6. n은0~3만 제공한다. |
| 5 포인터·배열 | 주소/역참조, 배열식의 포인터 변환, 같은 배열 안 포인터 이동을 구별한다. | §6.5.3.2, §6.3.2.1¶3, §6.5.6¶7~9 | `int a[3]={2,4,1}; int *p=a; p=p+1; *p=5;` → a[1]=5. a와p를 같은 종류의 객체라고 하지 않는다. |
| 6 다중 포인터·함수 전달 | 포인터 값도 복사된다. 호출자 포인터를 바꾸려면 그 포인터의 주소를 통해 접근한다. 함수 포인터는 호환된 선언을 쓴다. | §6.9.1¶10, §6.7.6.3¶7~8, §6.5.2.2¶7·9, §6.5.3.2 | `void pick(int **out,int *item){*out=item;}`. x2,y5,p=&x에서 pick(&p,&y) 후 *p5·x2. `int inc(int n){return n+1;}`를 `int (*f)(int)=inc;`에 저장하면 f(2)=3. |
| 7 구조체 조합 | `.`/`->`, 구조체 값 복사, 멤버별 상태를 읽는다. | §6.5.2.3¶3~4, §6.5.16.1¶1~2, §6.7.9 | `struct Item{int qty;}; struct Item a={2}; struct Item b=a; b.qty=5;` → a2·b5. struct Item *p=&a 후 p->qty=4이면 a4·b5. |

### C 안전 경계

- **수명과 범위**: [§6.2.4¶2·5~6](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf#page=56). 호출 중 살아 있는 지역 변수 주소를 매개변수로 전달할 수 있다. 함수가 끝난 지역 객체를 가리키는 포인터로 값을 읽는 예시는 고정 출력 문제로 만들지 않는다.
- **배열 끝**: [§6.5.6¶8](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf#page=111). a+3은 위3요소 배열의 끝 다음 위치로 만들 수 있지만 역참조하지 않는다. a[3]이나 더 먼 포인터 계산을 정상 값처럼 채점하지 않는다.
- **평가 순서**: [§6.5¶2~3](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf#page=94), §6.5.2.2¶10. C의 함수 인자 평가를 왼쪽부터라고 가정하지 않는다. 같은 식에서 i의 변경과 읽기를 섞는 퍼즐을 제외하고 부수효과를 문장별로 분리한다.
- **문자열**: `char label[]`의 쓰기와 문자열 리터럴 저장소 수정을 혼동하지 않는다(§6.4.5¶7). 널 종료 없는 버퍼에 strlen/%s를 적용하지 않는다. strlen의 형은size_t이므로 출력 틀은 `%zu`를 쓴다. 실제 컴파일러 지원은 별도 확인한다.
- **형과 메모리**: 2차원 배열을 int**로 강제 변환하지 않는다. 함수의 배열 매개변수는 포인터로 조정되므로 그 안의sizeof로 호출자 배열 길이를 구한다고 설명하지 않는다. 구조체 패딩·포인터 숫자 주소·int크기·char부호는 고정값을 요구하지 않는다.

## Java8~11 매트릭스

| 지도 수업 | 확인할 관계 | 공식 근거 | 안전한 작은 검토 사례·예상값 |
| --- | --- | --- | --- |
| 8 값·제어·배열 | 기본값 복사, boolean조건, 반복 경계·배열 접근, 계산 결과 | [JLS4.12.1·4.12.5](https://docs.oracle.com/javase/specs/jls/se25/html/jls-4.html#jls-4.12.1), [14.9·14.14](https://docs.oracle.com/javase/specs/jls/se25/html/jls-14.html#jls-14.9), [10.4](https://docs.oracle.com/javase/specs/jls/se25/html/jls-10.html#jls-10.4), [15.17.2](https://docs.oracle.com/javase/specs/jls/se25/html/jls-15.html#jls-15.17.2) | `{2,4,1}`의 배열 합7. int7/3은2. 조건은 `qty>0`이며 C처럼 `if(qty)`를 허용하지 않는다. |
| 9 객체·참조·인자 | 참조 복사와 객체 변경, 매개변수 값 전달·재대입 구별 | [4.12.2](https://docs.oracle.com/javase/specs/jls/se25/html/jls-4.html#jls-4.12.2), [8.4.1](https://docs.oracle.com/javase/specs/jls/se25/html/jls-8.html#jls-8.4.1), [15.12.4.2](https://docs.oracle.com/javase/specs/jls/se25/html/jls-15.html#jls-15.12.4.2) | `Item a=new Item(); a.qty=2; Item b=a; b.qty=5;` → a.qty5. 메서드 안에서 b를new Item으로 다시 대입해도 호출자a의 참조는 교체되지 않는다. |
| 10 static·초기화 | 클래스 공유 필드와 인스턴스 상태, 클래스 초기화·생성 순서 | [8.3.1.1](https://docs.oracle.com/javase/specs/jls/se25/html/jls-8.html#jls-8.3.1.1), [12.4.2](https://docs.oracle.com/javase/specs/jls/se25/html/jls-12.html#jls-12.4.2), [12.5](https://docs.oracle.com/javase/specs/jls/se25/html/jls-12.html#jls-12.5) | static count를0부터 생성자에서1씩 증가시키고 객체2개 생성→count2. 각qty를2로 초기화하면 각각2. 문제별 새JVM에서 최초 초기화를 추적한다. |
| 11 상속·호출·예외 | 오버라이드·필드 숨김·static 숨김·오버로드·예외 구별 | [8.4.8.1·8.4.8.2·8.4.9](https://docs.oracle.com/javase/specs/jls/se25/html/jls-8.html#jls-8.4.8.1), [15.11.1](https://docs.oracle.com/javase/specs/jls/se25/html/jls-15.html#jls-15.11.1), [15.12.2·15.12.4.4](https://docs.oracle.com/javase/specs/jls/se25/html/jls-15.html#jls-15.12.2), [14.20.2](https://docs.oracle.com/javase/specs/jls/se25/html/jls-14.html#jls-14.20.2) | 아래 대조표로 이름이 같으면 모두 동적으로 바뀐다는 오해를 구분한다. |

### Java에서 혼동하지 않을 호출 규칙

자체 검토용 타입 정의:

```java
class Base {
    int qty = 2;
    int read() { return qty; }
    static int tag() { return 1; }
}
class Child extends Base {
    int qty = 5;
    @Override int read() { return qty; }
    static int tag() { return 9; }
}
```

`Base item=new Child();`를 전제로 한 **미실행 예측**:

| 식 | 예상값 | 판단 기준 |
| --- | --- | --- |
| `item.qty` | 2 | 필드는 식의 정적 타입으로 선택(JLS15.11.1) |
| `item.read()` | 5 | 선택된 인스턴스 메서드를 실제 객체에서 탐색(15.12.4.4) |
| `item.tag()` | 1 | static 호출은 오버라이드가 아니라 숨김이다(8.4.8.2). 보통 작성 표기는Base.tag()로 한다 |
| `((Child)item).qty` | 5 | 명시적 캐스트 뒤 타입이 다르다. 실제 객체가Child이므로 이 캐스트는 성립한다 |

오버로드는 별도 규칙이다. `choose(Object)`와`choose(String)`에 선언 타입Object인 변수를 전달하면 전자를 선택한다. 실제 문자열 객체라는 이유로 후자를 다시 선택하지 않는다. 호출 시그니처 결정과 같은 시그니처의 오버라이드 탐색은 서로 다른 단계다.

초기화는 단순 상속과 명시적super() 코드로 설명한다. Java25에서 생성자의 첫 문장은 항상super/this라는 과거 제약을 일반화하지 않는다. 생성자 안의 가상 메서드 호출·순환static 초기화·상수 인라인을 첫 예시에 섞지 않는다. finally는 정상 복귀에도 실행되지만 JVM 강제 종료에도 반드시 실행된다고 하지 않는다. finally의return으로 결과를 덮어쓰는 것을 일반적인 구현 습관으로 만들지 않는다.

Java 배열 범위 밖 접근은 예외이며 C의UB와 같지 않다. Java는[JLS15.7.1/15.12.4.2](https://docs.oracle.com/javase/specs/jls/se25/html/jls-15.html#jls-15.7.1)에서 평가 순서를 정하지만 여러++를 난이도의 대용품으로 쓰지 않는다. String·박싱 정수의 참조 동일성·캐시에 의존하는 값 맞히기를 피한다.

## Python12~13 매트릭스

| 지도 수업 | 확인할 관계 | 공식 문서 위치 | 작은 검토 예·예상값 |
| --- | --- | --- | --- |
| 12 자료·연산 | 시퀀스·첨자·슬라이스·가변성·딕셔너리/집합·복사 | [Built-in Types: Common Sequence Operations / Lists / Mapping Types / Set Types](https://docs.python.org/3.14/library/stdtypes.html), [copy: shallow/deep 구분](https://docs.python.org/3.14/library/copy.html), [대입문](https://docs.python.org/3.14/reference/simple_stmts.html#assignment-statements) | `a=[[2]]; b=a[:]; b[0][0]=5` → a[0][0]도5, a is b는False, a[0] is b[0]은True. 얕은 복사는 내부 객체를 재귀적으로 복사하지 않는다. |
| 13 함수·클래스·예외 | 이름 바인딩, 변경과 재바인딩, 기본값, 클래스/인스턴스 속성, 예외 경로 | [Tutorial4.9.1 Default Argument Values](https://docs.python.org/3.14/tutorial/controlflow.html#default-argument-values), [Tutorial9.3.5 Class and Instance Variables](https://docs.python.org/3.14/tutorial/classes.html#class-and-instance-variables), [Reference8.7 try](https://docs.python.org/3.14/reference/compound_stmts.html#the-try-statement), [Reference8.10 Function Definitions](https://docs.python.org/3.14/reference/compound_stmts.html#function-definitions) | `def adjust(items): items.append(5); items=[9]`. a=[2]를 전달한 뒤a는[2,5]. 함수 안의 재바인딩은 호출자 이름을 교체하지 않는다. |

### Python의 짧은 경계·반례

- `stock=[2,4,1]`에서`stock[1:3]`→[4,1], `stock[::-1]`→[1,4,2]. 슬라이스의 끝은 제외한다. 범위 밖 슬라이스와 범위 밖 단일 첨자를 같은 오류로 취급하지 않는다.
- 숫자의 [공식 규칙](https://docs.python.org/3.14/library/stdtypes.html#numeric-types-int-float-complex)에서`7//3=2`, `-5//2=-3`, `-5%2=1`. C의0방향 절단과Python의floor를 혼동하지 않는다. 부동소수점의 미세한 반올림 사례는 도입에서 제외한다.
- 딕셔너리는 삽입 순서를 유지하고 기존 키 갱신으로 위치가 바뀌지 않는다(3.7이후 언어 보장). 집합에는 그 보장이 없다. 집합 열거 문자열을 고정하지 않고 정수 집합이면sorted로 순서를 명시한다.
- 가변 기본 인자는 정의 시 한 번 평가된다. 여러 호출에 리스트가 남는 원인을 진단하고None을 기본값으로 두어 호출마다 새로 만드는 설계와 비교한다. 문제 사이의 같은 프로세스 잔존 상태에 의존하지 않는다.
- 클래스의 리스트 속성 하나를 만들어append하면 인스턴스 사이에 공유될 수 있다. `__init__`에서 각각self.items를 만드는 경우와 비교한다. Python 속성 탐색을Java 필드 숨김과 같다고 하지 않는다.
- `try/except/else/finally`는 블록을 하나씩 추가한다. else는try가 예외 없이 정상 완료한 경로, finally는 정상 종료·예외 경로의 후처리로 추적한다. 모든 환경에서 무조건 실행된다고 하지 않는다.
- [식 평가 순서](https://docs.python.org/3.14/reference/expressions.html#evaluation-order)는 왼쪽부터지만 공유 변경을 한 줄에 몰아넣지 않는다. is를 수치/문자열의 동등 비교로 쓰거나 우연한intern·id값을 정답으로 삼지 않는다.

## 제작 시 검증 경계

위 예측은 시험 컴파일러의 결과도 실행한 회귀 테스트도 아니다. 제작 시 최소 완전 프로그램으로 만들고 사용한C컴파일러/옵션·JDK·Python판을 기록하며 정답·경계·오답을 실행 확인한다. C의 정의되지 않은 동작을 특정 실행에서 나온 값으로 정답 고정하지 않는다. Java 컴파일 오류·실행 예외·정상 출력과Python 예외·가변 상태를 구분해 판정한다.

같은 재고 상황을 수업 안에서 조금씩 넓히고 상태표·짧은 결과·한 곳 수정을 중심으로 구성한다. 언어 사이의 유사성은 차이를 설명하는 데 쓰며 별도 코스의 수업/진도를 공유하는 이유로 삼지 않는다. 위 모든 항목을 한 문제에 동시에 넣을 필요는 없다.
