# 정보처리기사 보강 조사: 응집도·결합도, 5NF, C 비트·동적 할당

확인일: 2026-10-19. 연구 메모다. 생산 콘텐츠·PRD·실행기·체커를 변경하지 않았다. 아래 작은 사례의 결과는 문헌을 적용한 추론이며 직접 실행한 결과가 아니다. Qnet가 특정 교재의 세부 분류표나 C 구현을 시험 표준으로 지정했다고 주장하지 않는다.

## 1. 출처의 성격

| 출처 | 실제 읽은 위치 | 활용 범위 |
| --- | --- | --- |
| Diomidis Spinellis, 대학 공식 저자 강의 | [Basic Design Principles, Cohesion / Coupling](https://www2.dmst.aueb.gr/dds/etech/arch/conc.htm) | 저자 자신의 순서 명시 분류; 원전이나 시험 공식 분류로 확대하지 않음 |
| Northeastern CS3100 공식 수업 자료 | [Changeability II, 각 응집도·결합도 소제목](https://neu-pdi.github.io/CS3100-Spring-2026/lecture-notes/l7-design-for-change/) | 수업 운영 주체가 공개한 정의·예시; 전통 모델의 교육적 설명 |
| Arnold 외 5인, NSA SAWG 활동 보고 | [NIST 보관 1992 NCSC 논문집](https://csrc.nist.gov/CSRC/media/Publications/conference-paper/1992/10/13/proceedings-15th-national-computer-security-conference-1992/documents/1992-15th-NCSC-proceedings-vol-1.pdf#page=59), Assessing Modularity in Trusted Computing Bases, §§3.1, 3.3 | 다른 공식 평가 모델과의 차이; 저자들이 보고하는 SAWG 결과 |
| IIT Bombay R. K. Joshi 강의 | [Structured Programming, PDF 36쪽 Module Coupling](https://www.cse.iitb.ac.in/~rkj/talks/structuredprogramming.pdf#page=36) | 메시지 결합과 OO 관련 확장이 존재함; 전체 강도 서열은 없음 |
| Silberschatz·Korth·Sudarshan 저자 공식 교재 사이트 | [Database System Concepts 온라인 Ch.28](https://www.db-book.com/online-chapters-dir/28.pdf), §§28.2.1–28.2.2 | JD와 PJNF/5NF 정의 |
| WG14 공식 공개 문서 | [N1570](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf), 2011-04-12 위원회 초안 | C11 초안의 언어 규칙; 실제 시험 버전은 미확인 |

## 2. 전통적 응집도 7종: 정의와 서열을 따로 확인

Spinellis는 낮은 쪽에서 높은 쪽으로 **우연적 → 논리적 → 시간적 → 절차적 → 통신적 → 순차적 → 기능적** 순서를 명시한다. 같은 자료의 `Cohesion` 절에서 확인했으며, 전통적 교육 모델로 사용할 수 있다. [저자 강의, Cohesion](https://www2.dmst.aueb.gr/dds/etech/arch/conc.htm).

아래 뜻은 Northeastern 수업 자료의 동명 절을 짧게 요약했다. 한 모듈이 여러 특징을 동시에 보일 수 있으며, 상황 정보 없이 이름 하나를 무조건 정답으로 확정하지 않는다. [공식 강의, Cohesion 소제목 전체](https://neu-pdi.github.io/CS3100-Spring-2026/lecture-notes/l7-design-for-change/#define-and-recognize-cases-of-coincidental-logical-temporal-procedural-communication-sequential-and-functional-cohesion-15-minutes).

| 분류 | 구분할 핵심 |
| --- | --- |
| Coincidental / 우연적 | 기능적 관련 없이 묶임 |
| Logical / 논리적 | 비슷한 종류의 작업을 묶음 |
| Temporal / 시간적 | 실행 시점·생명주기가 공통 |
| Procedural / 절차적 | 같은 작업의 처리 절차로 연결 |
| Communicational / 통신적 | 같은 입력·출력 데이터를 다룸 |
| Sequential / 순차적 | 앞 처리 결과를 후속 처리에 사용 |
| Functional / 기능적 | 하나의 명확한 기능에 집중 |

연구용 작은 비교(추론): 서로 무관한 문자열 변환과 온도 계산을 편의상 같은 파일에 둔 경우는 우연적 후보다. 시작 시 DB·메일·캐시를 초기화하는 경우는 시간적 후보다. 재고 수량을 읽고 계산 결과를 다음 처리로 전달하는 사례는 순차적 특징을 강조할 수 있다. “순서대로 작성됨”만으로 순차적이라고 채점하지 말고 **데이터가 이어지는지**를 명시해야 한다.

### 공식 자료도 모델이 다르다

NIST 논문집의 *Assessing Modularity in Trusted Computing Bases* §3.1, 인쇄 49–50쪽/PDF 64–65쪽은 functional, sequential, communicational, temporal, **logical(procedural)**, coincidental의 6종이다. 절차적을 별도로 두는 위 7종과 다르다. functional을 최고, coincidental을 최저로 설명하지만 이 문헌의 6종을 수험용 7종 표에 억지로 맞추면 안 된다. [해당 논문 원문](https://csrc.nist.gov/CSRC/media/Publications/conference-paper/1992/10/13/proceedings-15th-national-computer-security-conference-1992/documents/1992-15th-NCSC-proceedings-vol-1.pdf#page=64).

## 3. 결합도: 확인한 공통 뜻과 서로 다른 분류

Northeastern은 **data → stamp → control → common → content** 순으로 설명하며 뒤쪽을 더 좋지 않은 결합으로 제시한다. 아래 다섯 뜻은 이 자료의 동명 소제목 및 NIST §3.3에 공통으로 확인한 범위를 중심으로 정리했다. [강의, Coupling](https://neu-pdi.github.io/CS3100-Spring-2026/lecture-notes/l7-design-for-change/#define-and-recognize-cases-of-data-coupling-stamp-coupling-control-coupling-common-coupling-and-content-coupling-20-minutes), [NIST, 인쇄 51–52쪽/PDF 66–67쪽](https://csrc.nist.gov/CSRC/media/Publications/conference-paper/1992/10/13/proceedings-15th-national-computer-security-conference-1992/documents/1992-15th-NCSC-proceedings-vol-1.pdf#page=66).

| 분류 | 확인한 뜻 | 경계 |
| --- | --- | --- |
| Data / 자료 | 필요한 자료를 호출 인자로 전달 | NIST는 단일 자료 항목을 명시 |
| Stamp / 스탬프 | 내부 구조를 가진 복합 자료를 전달 | NIST 정의는 “일부만 사용”을 필수로 적지 않음 |
| Control / 제어 | 상대 내부 처리 흐름을 정하는 정보 전달 | 단지 인자가 존재한다는 뜻은 아님 |
| Common / 공통 | 모듈들이 공통 자원·전역 상태를 공유 | 호출 인자로 같은 값을 전달하는 것과 구분 |
| Content / 내용 | 다른 모듈 내부 구현에 직접 의존·접근 | 공개된 인터페이스 사용과 구분 |

**외부 결합의 위치·정의는 확인 공백을 남긴다.** Spinellis는 여섯 종을 data, stamp, control, **common, external**, content 순으로 명시한다. 흔히 기대하는 data, stamp, control, external, common, content와 중간 둘의 순서가 다르다. 이 강의는 external의 상세 의미를 설명하지 않는다. 따라서 이번 근거로 “공식 6종의 유일한 서열” 또는 “external의 엄밀한 정의까지 확인”이라고 쓰면 안 된다. [저자 강의, Coupling](https://www2.dmst.aueb.gr/dds/etech/arch/conc.htm).

NIST §3.3은 data/stamp/control을 **call coupling의 하위 유형**으로 둔다. 또 이 분석의 목적은 정밀한 강도 순위보다 허용/비허용 판단이라고 직접 밝힌다. 모든 시대·설계 맥락에 적용되는 단일 수치 서열로 읽지 않는다. [NIST PDF 67쪽](https://csrc.nist.gov/CSRC/media/Publications/conference-paper/1992/10/13/proceedings-15th-national-computer-security-conference-1992/documents/1992-15th-NCSC-proceedings-vol-1.pdf#page=67).

**OO 확장 분리:** Joshi의 대학 공식 강의 PDF 36쪽은 message coupling을 메시지 전달에 의한 통신으로 설명하고, subclass upward / superclass downward / synchronization coupling도 별도 열거한다. 이 페이지는 메시지를 전통적 6종 아래에 붙인 보편적 최저 단계로 순위 매기지 않는다. [IIT Bombay 강의](https://www.cse.iitb.ac.in/~rkj/talks/structuredprogramming.pdf#page=36).

출판사 근거의 한계: Vlad Khononov의 [Pearson 공식 샘플](https://www.informit.com/content/images/9780137353484/samplepages/9780137353484_Sample.pdf#page=10) 목차는 Ch.5에 여섯 유형과 비교 절을 보여 주지만, 샘플에는 그 장의 본문이 없다. 목차를 정의·서열의 본문 검증으로 사용하지 않았다. 새로운 Balanced Coupling 모델도 저자 자신의 별도 모델로 구분해야 한다. [저자 모델 소개](https://coupling.dev/).

## 4. JD와 5NF: 저자 공식 교재의 정의

Database System Concepts Ch.28 §28.2.1, PDF 6쪽에서 JD `*(R1,...,Rn)`는 모든 합법적인 관계 인스턴스가 해당 투영들의 자연 조인으로 원래대로 복구된다는 제약이다: `r = πR1(r) ⋈ ... ⋈ πRn(r)`. 어느 Ri가 R 전체이면 자명한 JD다. [저자 공식 교재](https://www.db-book.com/online-chapters-dir/28.pdf#page=6).

같은 교재 §28.2.2, PDF 9쪽은 비자명 JD마다 각 Ri가 R의 슈퍼키인 PJNF를 정의하고, 일부 문헌에서 이를 **5NF**라고 부른다고 밝힌다. 5NF는 4NF를 함의하지만 역은 보장되지 않는다. 2분해 JD와 MVD의 연결은 §28.2.1에 있으며, 3개 이상 투영의 JD를 MVD만으로 모두 대신할 수는 없다. [§28.2.2](https://www.db-book.com/online-chapters-dir/28.pdf#page=9), [§28.2.1 PDF 7–8쪽](https://www.db-book.com/online-chapters-dir/28.pdf#page=7).

작은 반례(직접 실행하지 않은 집합 추론): R(A,B,C)에 `(1,1,1), (1,2,2), (2,1,2)`만 있으면 AB·BC·AC 투영을 조인할 때 원래 없던 `(1,1,2)`가 생성된다. 그러므로 “열을 2개씩 세 테이블로 나누면 언제나 무손실”은 틀리다. JD가 성립한다는 **업무 제약**이 필요하다. 현재 데이터 몇 줄이 우연히 복원된다는 관찰만으로 모든 합법적 인스턴스의 JD를 증명할 수도 없다.

원 논문의 존재와 범위도 확인했다. Fagin의 1979 논문 공식 IBM 초록은 4NF이면서 PJ/NF가 아닌 스키마 가능성과, 3분해를 2분해의 연속으로 항상 대체할 수 없음을 설명한다. 이번에는 초록을 확인했으며 그 논문 전체 증명을 읽었다고 표시하지 않는다. [IBM Research, Normal forms and relational database operators](https://research.ibm.com/publications/normal-forms-and-relational-database-operators).

## 5. C 비트 연산: 안전한 작은 값의 경계

근거는 [WG14 N1570](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)의 §§6.5.3.3, 6.5.7, 6.5.10–6.5.14다. **C11 위원회 초안**이며 시험 버전·정수 폭을 확정하지 않는다.

| 규칙 | 작은 추론 사례 |
| --- | --- |
| `&`, `|`, `^`는 대응 비트 연산 | `5u & 3u`→1, `5u | 2u`→7, `5u ^ 3u`→6 |
| `~`는 정수 승격 후 비트 반전 | `(~5u) & 15u`→10; “4비트 정수”라고 일반화하지 않음 |
| unsigned 시프트 | `1u << 3`→8, `5u >> 1`→2 |
| 시프트 수는 승격된 왼쪽 타입 폭보다 작고 음수가 아니어야 함 | 위반은 UB; unsigned여도 예외 아님 |
| `&&`, `||`는 논리값과 단락 평가 | `2u & 1u`→0, `2u && 1u`→1 |

unsigned 왼쪽 시프트는 해당 타입 범위의 모듈러 규칙을 따른다. signed 음수의 오른쪽 시프트는 구현 정의이며, signed 왼쪽 시프트에는 추가 표현 가능 조건이 있다. 초보 실습은 `unsigned int`와 작은 상수로 한정하고, `unsigned char`도 정수 승격을 겪는다는 점을 놓치지 않는다. [§6.5.7 PDF 112–113쪽](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf#page=112), [§6.5.3.3 PDF 107쪽](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf#page=107).

## 6. C 동적 할당: 확인한 실습 범위

근거: N1570 §§7.22.3, 7.22.3.2–7.22.3.4, §6.2.4. [할당 함수 PDF 365–367쪽](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf#page=365).

| 항목 | 보장·금지 경계 |
| --- | --- |
| malloc | 지정 바이트 확보; 내용은 불확정, 실패 시 null |
| calloc | 원소 수×원소 크기 확보; 모든 비트 0으로 초기화 |
| free | 할당 시작 포인터를 해제; null이면 동작 없음 |
| 수명 | 할당부터 해제까지; 해제 뒤 접근·중복 해제 금지 |

연구용 최소 사례는 `malloc(sizeof *p)` 후 null 검사 → 정수 대입 → 값 읽기 → `free(p)` 흐름이다. calloc으로 확보한 int 원소의 0과 malloc의 미초기화 값을 비교하되, malloc의 미초기화 읽기를 출력 예측 문제로 실행하지 않는다. calloc의 비트 0은 임의의 부동소수점 0·null 포인터 표현까지 보장하지 않는다(각주296). `free(p + 1)`이나 지역변수 주소 해제는 정당한 할당 시작 포인터가 아니므로 금지한다. `p = NULL`은 다른 별칭 포인터까지 고치지 않는다. 0바이트 요청은 구현 정의이므로 첫 실습에서 제외한다. 크기 곱셈 오버플로와 배열 범위도 별도 점검한다. [§7.22.3](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf#page=365), [calloc/free 및 각주296](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf#page=366), [객체 수명 §6.2.4](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf#page=56).

## 7. 채점·콘텐츠 반영 전 남은 확인

- 7응집도 순서와 뜻은 위 대학 공식 강의 자료에 근거를 확보했다. 다만 원래 구조적 설계 저자들의 전체 원문과 동일하다고 주장하지 않는다.
- external 결합의 상세 정의와 common/external의 수험용 고정 서열은 이번 저자·출판사 본문 조사에서 확정하지 못했다. 모호한 외부 파일 사례를 단일 정답으로 채점하지 않는다.
- 메시지 결합은 별도 OO 확장 모델로 표시한다. 다른 모델의 서열에 자동 삽입하지 않는다.
- C 규칙의 근거와 시험 환경의 근거를 분리한다. 메모리 주소·할당 성공·정수 폭을 고정하지 않으며, UB나 구현 정의를 특정 출력으로 채점하지 않는다.
