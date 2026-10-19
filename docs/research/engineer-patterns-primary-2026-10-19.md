# 정보처리기사 설계 패턴: 저자·출판사 1차 근거 보강

확인일: 2026-10-19. 조사 메모이며 생산 수업·문제·PRD를 변경하지 않았다. 예시 코드는 실행하지 않았다. 시험별 출제 빈도나 패턴별 배점은 조사 결과로 주장하지 않는다.

## 1. 확보한 근거와 검증 수준

- **A — 원저자의 정식 발췌 확인:** InformIT가 GoF 원저자 네 명의 이름과 원서를 표시하여 공개한 Abstract Factory, Adapter, Chain of Responsibility의 `Intent`, 분류 제목, 적용 조건을 실제 읽었다. 각각 [Abstract Factory](https://www.informit.com/articles/article.aspx?p=1398599), [Adapter](https://www.informit.com/articles/article.aspx?p=1398600), [Chain of Responsibility](https://www.informit.com/articles/article.aspx?p=1398601). 세 글의 게시일은 2009-10-23이다.
- **B — 다른 저자의 출판사 공식 샘플 확인:** James W. Cooper, *Python Programming with Design Patterns*의 [Pearson 공식 샘플 PDF](https://ptgmedia.pearsoncmg.com/images/9780137579938/samplepages/9780137579938_Sample.pdf)를 실제 읽었다. PDF 23–25쪽 `Book Organization`이 패턴별 장의 취지를 설명하고 생성·구조·행위로 묶는다. 이 자료는 저자 자신의 해설이며, GoF 원저자의 Intent 원문을 전부 검증한 것과는 구분한다. 페이지는 파일의 1부터 세는 PDF 쪽수다.
- **B — 저자의 원고 저장소 확인:** Robert Nystrom의 *Game Programming Patterns* 원고 중 Prototype, Flyweight, Observer, State, Singleton, Command를 저자 GitHub 저장소의 raw 파일에서 읽었다. 아래 해당 절에 직접 링크했다. 게임 사례의 설계 해설이며 시험 표준 문서가 아니다.

## 2. 23개 취지·분류 매트릭스

아래는 짧은 한국어 조사 요약이다. B행은 Cooper의 장별 소개에서 확인한 범위다. 상세한 원서 정의 전체나 모든 변형의 정의를 대신하지 않는다.

### 생성 5개

근거: [공식 샘플 PDF 23쪽, Part II / Chapters 6–10](https://ptgmedia.pearsoncmg.com/images/9780137579938/samplepages/9780137579938_Sample.pdf#page=23). Abstract Factory는 A 근거도 병기했다.

| 패턴 | 확인한 핵심 취지 | 수준·위치 |
| --- | --- | --- |
| Factory Method | 생성 결정을 하위 클래스에 위임 | B, Ch.6 |
| Abstract Factory | 관련 제품군의 생성 인터페이스 | A [Intent](https://www.informit.com/articles/article.aspx?p=1398599), B Ch.7 |
| Singleton | 단일 인스턴스와 전역 접근점 | B, Ch.8 |
| Builder | 복잡한 객체의 구성과 표현 분리 | B, Ch.9 |
| Prototype | 원형 객체를 복제하여 생성 | B, Ch.10 |

### 구조 7개

근거: [공식 샘플 PDF 24쪽, Part III / Chapters 12–18](https://ptgmedia.pearsoncmg.com/images/9780137579938/samplepages/9780137579938_Sample.pdf#page=24).

| 패턴 | 확인한 핵심 취지 | 수준·위치 |
| --- | --- | --- |
| Adapter | 기대 인터페이스로 변환 | A [Intent](https://www.informit.com/articles/article.aspx?p=1398600), B Ch.12 |
| Bridge | 인터페이스와 구현의 분리 | B, Ch.13 |
| Composite | 개별 객체와 집합의 통일 | B, Ch.14 |
| Decorator | 개별 객체의 동작 확장 | B, Ch.15 |
| Facade | 복잡한 기능의 단순한 진입점 | B, Ch.16 |
| Flyweight | 공유 데이터를 분리하여 절약 | B, Ch.17 |
| Proxy | 대리 객체로 실제 객체 접근 | B, Ch.18; 소개 사례는 지연 생성 |

### 행위 11개

근거: [공식 샘플 PDF 24–25쪽, Part IV / Chapters 20–30](https://ptgmedia.pearsoncmg.com/images/9780137579938/samplepages/9780137579938_Sample.pdf#page=24).

| 패턴 | 확인한 핵심 취지 | 수준·위치 |
| --- | --- | --- |
| Chain of Responsibility | 처리자를 찾으며 요청 전달 | A [Intent](https://www.informit.com/articles/article.aspx?p=1398601), B Ch.20 |
| Command | 실행 요청을 객체로 표현 | B, Ch.21 |
| Interpreter | 작은 언어의 해석 구조 | B, Ch.22 |
| Iterator | 컬렉션 항목의 순회 | B, Ch.23 |
| Mediator | 별도 객체가 상호 통신 조정 | B, Ch.24 |
| Memento | 내부 상태 저장·복원 | B, Ch.25 |
| Observer | 상태 변화의 관찰자 통지 | B, Ch.26 |
| State | 상태에 따른 동작 변경 | B, Ch.27 |
| Strategy | 알고리즘의 교체 | B, Ch.28 |
| Template Method | 공통 골격과 하위 단계 분리 | B, Ch.29에서는 Template로 표기 |
| Visitor | 외부 객체에 연산을 분리 | B, Ch.30 |

Cooper의 Ch.5 `Factory Pattern`은 후속 공장 패턴을 설명하기 위한 별도 기초 장이다. 위 GoF 23개에 단순 Factory를 추가하여 24개로 세지 않는다. 분류와 장명은 같은 [PDF 23쪽 및 목차](https://ptgmedia.pearsoncmg.com/images/9780137579938/samplepages/9780137579938_Sample.pdf#page=23)에서 구분된다.

## 3. 원저자 발췌에서 추가로 직접 검증한 구분

- **Abstract Factory:** 제목은 `Object Creational`; `Intent`는 구체 클래스를 지정하지 않고 관련되거나 의존하는 객체 가족을 생성하는 인터페이스를 다룬다. 단순히 조건에 따라 객체 하나를 반환하는 모든 코드를 이 패턴으로 부를 근거는 없다. [원저자 발췌, Intent / Applicability](https://www.informit.com/articles/article.aspx?p=1398599).
- **Adapter:** 제목은 `Class, Object Structural`이다. 클래스 어댑터와 객체 어댑터라는 두 구현 범위를 구분한다. “구조 패턴은 모두 객체 범위”라고 가르치면 틀린다. [원저자 발췌, Intent](https://www.informit.com/articles/article.aspx?p=1398600), [Applicability / Structure](https://www.informit.com/articles/article.aspx?p=1398600&seqNum=2).
- **Chain of Responsibility:** 제목은 `Object Behavioral`; 여러 후보가 요청을 받을 수 있도록 연결하고 한 후보가 처리할 때까지 넘긴다. 끝까지 처리되지 않을 가능성도 `Consequences`에 명시되어 있다. “모든 단계가 반드시 처리한다” 또는 “처리를 반드시 보장한다”는 설명은 부정확하다. [원저자 발췌, Intent / Consequences 3](https://www.informit.com/articles/article.aspx?p=1398601).

이 세 패턴 외에는 원저자의 정식 Intent·class/object 범위 표 전체를 직접 확인했다고 표시하지 않는다. 이번에 23개 모두에 확보한 것은 **Cooper의 공식 출판사 샘플에 실린 개요와 3분류**다.

## 4. 다른 저자의 실제 설명으로 보강한 오개념 경계

- **Strategy와 State:** Strategy는 알고리즘 계열을 같은 사용 방식으로 교체하는 관점이다. State는 객체 내부 상태의 변화에 맞춰 동작을 분리하는 관점이다. 같은 위임 구조만 보고 의도가 같다고 단정하지 않는다. [Shalloway·Trott, The Strategy Pattern / Key Features](https://www.informit.com/articles/article.aspx?p=1398602&seqNum=4), [Nystrom, The State Pattern / A state interface / Classes for each state](https://raw.githubusercontent.com/munificent/game-programming-patterns/master/book/state.markdown). 모든 if문을 제거해야 한다는 규칙도 아니다. State 원고는 간단한 if가 충분한 경우를 직접 언급한다.
- **Flyweight와 Singleton:** 공유 가능한 공통 데이터와 인스턴스별 데이터를 나누는 것이 Flyweight 설명의 핵심이다. 전역에서 오직 객체 하나만 존재하도록 보장하는 문제와 구분한다. Nystrom의 숲 사례에서 각 나무는 위치 등을 따로 가지며 모델을 공유한다. [Flyweight, Forest for the Trees](https://raw.githubusercontent.com/munificent/game-programming-patterns/master/book/flyweight.markdown), [Singleton, Restricting a Class to One Instance / Providing a Global Point of Access](https://raw.githubusercontent.com/munificent/game-programming-patterns/master/book/singleton.markdown).
- **Prototype:** 복제 대상에는 클래스 종류뿐 아니라 상태도 들어간다. 같은 종류의 객체를 새로 만드는 것과 기존 상태를 복제하는 것을 비교할 수 있다. 깊은 복사 여부까지 자동 보장하는 것으로 확대하지 않는다. [Nystrom, The Prototype Design Pattern](https://raw.githubusercontent.com/munificent/game-programming-patterns/master/book/prototype.markdown).
- **Observer와 Command:** Observer는 수신자들의 등록과 통지 관계를, Command는 호출을 데이터인 객체로 다루는 구조를 설명한다. 후자는 저장·전달·실행 취소 같은 설계를 가능하게 하지만, 단순히 명령 클래스를 만들었다고 취소 기능이 저절로 생기는 것은 아니다. [Nystrom, Observer / Achievement Unlocked](https://raw.githubusercontent.com/munificent/game-programming-patterns/master/book/observer.markdown), [Command, 도입부 / Configuring Input](https://raw.githubusercontent.com/munificent/game-programming-patterns/master/book/command.markdown).
- **Proxy의 공개 샘플 범위:** Cooper의 짧은 소개는 비용이 큰 실제 객체의 생성 지연을 중심으로 한다. 이를 근거로 모든 Proxy가 지연 생성이라고 일반화하거나 보호·원격 프록시의 상세 정의까지 확인한 것으로 표기하지 않는다. [Cooper PDF 24쪽, Ch.18](https://ptgmedia.pearsoncmg.com/images/9780137579938/samplepages/9780137579938_Sample.pdf#page=24).

위 차이를 이용한 작은 상황 비교는 연구 제안이며 아직 실행한 실습이나 확정 문제는 아니다. 예를 들어 재고 알림 수신자를 추가하는 변경은 Observer, 할인 계산 방식을 교체하는 변경은 Strategy, 주문의 상태별 허용 행동을 바꾸는 변경은 State 후보로 검토할 수 있다. 클래스 이름보다 변경의 목적을 먼저 확인하도록 구성한다.

## 5. 결합도·응집도: 검증된 범위와 남은 공백

[IEEE Computer Society SWEBOK V4.0a 공식 PDF](https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf#page=86), Software Design §1.4 `Software Design Principles`, PDF 86쪽은 결합도를 모듈 사이 의존의 정도, 응집도를 모듈 내부 요소들 사이 연관의 강도로 설명한다. 약한 결합과 높은 응집을 지향한다는 기본 원리까지 직접 확인했다. **이 절은 전통적인 세부 유형과 그 완전한 서열표를 제공하지 않는다.**

보조 탐색에서 Steve McConnell의 [출판사 공식 Code Complete 샘플](https://www.informit.com/content/images/9780735619678/samplepages/9780735619678a.pdf)의 색인에는 functional, sequential, communicational, temporal, procedural, logical, coincidental cohesion이 본문 168–170쪽 항목으로 나타난다. 그러나 공개 샘플에서 그 본문을 직접 읽지 못했으므로, **색인을 세부 정의나 서열의 검증으로 취급하지 않는다.** stamp/content/common/external/control/data 결합도 서열 역시 이번 조사에서 저자·출판사 원문으로 완전히 검증하지 못했다.

따라서 현 단계에서 자신 있게 활용 가능한 1차 근거는 SWEBOK의 기본 정의다. 전통적인 7응집도·6결합도 세부 명명과 서열을 시험 정답으로 채점하려면 별도 원문 확인이 필요하다. 기존 조사 보고서에 있는 미확인 표시를 이번 패턴 조사만으로 제거하면 안 된다.

## 6. 구현 담당자에게 전달할 제한

- 이번 확인으로 **23개 전체의 저자·출판사 공개 개요와 3분류 근거**는 확보했다. 원저자 직접 발췌는 3개다. 전체 23개의 원저자 Intent, 적용 조건, 참여자, 장단점, class/object 범위를 모두 검증한 것은 아니다.
- 출판사 샘플의 설명은 Python·게임 등 저자별 맥락을 갖는다. 언어 기능인 Python decorator와 GoF Decorator의 완전한 동일성, Singleton의 안전한 동시성, Prototype의 깊은 복사, Proxy 전체 하위 유형 등은 여기서 자동 도출하지 않는다.
- 정보처리기사 출제기준과 연결할 때는 기존 `engineer-complete-coverage-2026-10-19.md`의 Qnet 근거를 유지한다. 이 조사로 시험의 특정 패턴 출제 여부·빈도·배점을 확정하지 않는다.
