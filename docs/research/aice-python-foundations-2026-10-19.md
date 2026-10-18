# AICE 첫 Python 기초 수업을 위한 사실 확인

확인일: 2026-10-19 (한국 시간). Python 3.10 공식 문서와 AICE 공식 가이드북 HTML을 직접 열었다. 내부 근거 조사이며 수업 PRD·학습 콘텐츠·교육 기법·채점기를 제작하거나 채택하지 않았다. 시험 문제·데이터·공식 예제 답안을 복제하지 않았다. 실제 시험 커널·샘플 시험 세션·플레이어 실행은 확인하지 않았다.

## Python 언어 근거

이번에 열린 `/3.10/` 문서의 표제 버전은 **3.10.22**다. 가이드북의 시험 환경 표기 **3.10.13**과 패치 버전이 같다거나 시험 커널로 검증했다고 표현하면 안 된다.

| 구분 | 직접 확인한 사실 | 1차 출처 |
| --- | --- | --- |
| 출력 | `print`는 값을 텍스트로 바꿔 출력 스트림에 쓴다. 기본 구분자는 공백, 끝 문자는 줄바꿈이다. 출력한 텍스트와 이름에 묶인 값은 구분해야 한다. | [Python 3.10 내장 함수 print](https://docs.python.org/3.10/library/functions.html#print) |
| 대입과 이름 | 대입문은 오른쪽 표현식을 평가하고 결과 객체를 대상에 연결한다. 이름에 대한 대입은 이름을 객체에 묶거나 이미 있던 연결을 다시 묶는다. 따라서 이전에 계산한 결과가 나중에 다른 이름의 변경을 따라 자동 재계산되는 관계는 아니다. | [Python 3.10 언어 참조 7.2](https://docs.python.org/3.10/reference/simple_stmts.html#assignment-statements) |
| 정의 전 사용 | 아직 값을 대입하지 않은 이름을 읽으면 `NameError`가 발생할 수 있다. 대입문 자체는 대화형 프롬프트에서 결과를 표시하지 않는다. | [공식 튜토리얼 3.1.1](https://docs.python.org/3.10/tutorial/introduction.html#numbers) |
| 리스트 | 대괄호 안에 쉼표로 구분한 항목을 쓸 수 있다. 리스트는 항목을 담는 시퀀스이고 인덱스 0이 첫 항목이다. 인덱스로 항목을 고르는 것과 리스트 전체를 읽는 것은 다르다. | [공식 튜토리얼 3.1.3](https://docs.python.org/3.10/tutorial/introduction.html#lists) |
| 길이 | `len`은 항목 수를 반환하며 리스트에도 적용한다. 길이가 3인 리스트의 첫 항목 인덱스는 0이며, 길이 3을 마지막 인덱스로 해석하면 안 된다. | [Python 3.10 내장 함수 len](https://docs.python.org/3.10/library/functions.html#len), [공식 튜토리얼 리스트](https://docs.python.org/3.10/tutorial/introduction.html#lists) |

Python 참조는 대화형 모드의 표현식 표시와 명시적인 `print`를 구분한다. 수업 실행기가 스크립트를 실행하는지 노트북 셀을 실행하는지 확인하기 전, 표현식을 마지막 줄에 적으면 항상 출력된다고 가정하지 않는다. [언어 참조 7.1](https://docs.python.org/3.10/reference/simple_stmts.html#expression-statements)

## AICE Associate와의 연결: 이번 재확인

- 가이드북은 Python 코드 입력 중심의 주관식과 결과 해석 단답형을 명시하고, Associate 범위에서 객관식을 제외한다. 지정 답안 셀과 문제에서 지정한 변수명을 사용하도록 안내한다. [공식 가이드북 Associate 5.b·5.d](https://www.aice.team/guidebook)
- 공개 범위는 정형 데이터 로딩·저장·구성 확인, 전처리·시각화, 머신러닝과 딥러닝 모델 학습·성능 평가·개선이다. 따라서 첫 Python 기초만으로 Associate 대비 전체가 완료된다고 할 수 없다. [공식 가이드북 Associate 5.c](https://www.aice.team/guidebook)
- Jupyter Notebook을 시험 도구로 안내한다. 설치 SW 표는 Python 3.10.13, TensorFlow 2.13.1, pandas 1.5.3, NumPy 1.23.5, matplotlib 3.7.1, seaborn 0.12.1이다. 이 표에는 scikit-learn 버전이 없다. 실제 회차 커널을 직접 읽은 결과가 아니다. [공식 가이드북 Associate 5.e·7](https://www.aice.team/guidebook)
- 가이드북 HTML에서 `scikit`라는 문자열은 확인되지 않았다. TensorFlow의 환경 표기는 확인했지만 이 사실만으로 모델별 출제 목록을 도출하지 않는다. [공식 가이드북](https://www.aice.team/guidebook)

## 접근·버전·자료의 한계

| 자료 | 이번 접근 결과와 취급 |
| --- | --- |
| [2026 환경 공지 16322](https://aice.study/board/notice/detail/16322) | 웹 도구에서 본문 없는 SPA였다. 최신 공지의 scikit-learn 1.3.2 등 버전은 이번에 재확인하지 못했다. |
| [현행 수험자 가이드](https://aice.study/certi/examGuide) | 웹 도구에서 본문 없는 SPA였다. 가이드북과 현재 회차 환경의 일치 여부는 미확정이다. |
| [KT·AICE 안내서, 대학 배포본](https://research.uos.ac.kr/sites/default/files/2025-11/AICE%20%EC%9E%90%EA%B2%A9%EC%A6%9D%20%EC%95%88%EB%82%B4%EC%84%9C_%EC%B5%9C%EC%A2%85.pdf) | 14쪽 PDF 응답은 얻었지만 이번 도구에서 텍스트와 열람 가능한 페이지 이미지를 얻지 못했다. 이번에 본문을 재확인한 자료로 취급하지 않는다. |

이전 [2026-10-18 시험 조사](aice-associate-exam-2026-10-18.md)는 주관기관 안내서에서 **scikit-learn과 TensorFlow를 함께 사용하는 Associate 범위**를 확인했다고 기록한다. 이 부분은 이전 조사 인계로 보존하며 이번 가이드북 HTML에서 두 프레임워크 범위를 모두 직접 확인한 사실로 승격하지 않는다. 이전 자료의 scikit-learn 버전·샘플 문제·환경 공지도 같은 한계를 유지한다.

첫 수업에 출력·이름·리스트·인덱스·길이를 담는 구체적인 순서, 최소 타이핑 방식, 문제 수와 판정 기준은 이 조사에서 정하지 않았다. 공식 문서가 특정 교육 방식의 효과를 검증한다는 주장도 하지 않는다. 자체 데이터·독립 과제를 만들 수 있다는 제품 판단과 시험 원문 사용·공식 채점 재현 주장은 분리해야 한다.
