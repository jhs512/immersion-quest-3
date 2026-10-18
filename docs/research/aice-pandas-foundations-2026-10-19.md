# AICE 표 데이터 기초 수업: pandas 근거

확인일: 2026-10-19 (한국 시간). pandas 공식 `/version/1.5/` 문서만 근거로 사용했다. 직접 열린 페이지들의 표제는 **pandas 1.5.3 documentation**이며 이번 열람에서 다른 주버전 문서로 이동하지 않았다. 이 사실은 실제 시험 커널이나 플레이어에 같은 패키지가 설치되어 있다는 증거가 아니다.

수업 PRD·학습 콘텐츠·문제·데이터·실행 코드는 만들지 않았다. 아래 표기는 API 의미를 식별하기 위한 것으로 공식 시험 데이터나 답안을 재현하지 않는다.

## 최소 구별에 필요한 사실

| 구별 | 직접 확인한 사실 | 공식 1.5 문서 |
| --- | --- | --- |
| 표·행·열 | `DataFrame`은 행과 열에 라벨이 있는 2차원 표 구조다. 딕셔너리에 열 이름을 키로, 열 데이터를 리스트로 넣어 생성할 수 있다. 일반 리스트 열들은 길이가 같아야 한다. 명시적 인덱스가 없으면 기본 행 라벨은 0부터 시작한다. | [DataFrame](https://pandas.pydata.org/pandas-docs/version/1.5/reference/api/pandas.DataFrame.html), [Intro: From dict of ndarrays / lists](https://pandas.pydata.org/pandas-docs/version/1.5/user_guide/dsintro.html#from-dict-of-ndarrays-lists) |
| 파일과 메모리 표 | `read_csv`는 경로·파일 같은 객체 등을 받아 CSV를 `DataFrame`으로 읽는다. 파일 경로 문자열과 읽은 뒤 이름에 연결된 표 객체는 다르다. | [read_csv](https://pandas.pydata.org/pandas-docs/version/1.5/reference/api/pandas.read_csv.html) |
| 헤더와 데이터 행 | 기본 `header='infer'`에서 `names`를 지정하지 않으면 `header=0`처럼 첫 유효 행을 열 이름으로 쓴다. 헤더가 없는 파일은 `header=None` 등 별도 조건을 지정해야 한다. 빈 줄과 주석 처리 조건 때문에 이를 항상 물리적 첫 줄이라고 단정하면 안 된다. | [read_csv의 header·names](https://pandas.pydata.org/pandas-docs/version/1.5/reference/api/pandas.read_csv.html) |
| 상대 파일명과 실행 위치 | 공식 예시는 현재 작업 디렉터리에 파일이 있는 조건에서 파일명만 `read_csv`에 넘긴다. 파일명만 있으면 어디서나 같은 파일을 찾는다는 뜻이 아니다. 실제 플레이어의 작업 디렉터리와 파일 배치는 별도 확인이 필요하다. | [Comparison with Stata: Reading external data](https://pandas.pydata.org/pandas-docs/version/1.5/getting_started/comparison/comparison_with_stata.html#reading-external-data) |
| 일부 관찰과 전체 | `head(n)`은 위치 기준 앞 n행을 반환하며 기본 n은 5다. 전체 행 수보다 크면 전체를 반환한다. 일부를 본 결과가 전체 데이터의 크기라는 뜻은 아니다. | [DataFrame.head](https://pandas.pydata.org/pandas-docs/version/1.5/reference/api/pandas.DataFrame.head.html) |
| 크기와 값 | `shape`는 `(행 수, 열 수)` 튜플인 속성이다. `df.shape`처럼 접근하며 `head(n)`과 호출 모양도 다르다. 크기 튜플의 두 숫자는 셀의 데이터 값이 아니다. | [DataFrame.shape](https://pandas.pydata.org/pandas-docs/version/1.5/reference/api/pandas.DataFrame.shape.html) |
| 한 열과 한 열짜리 표 | 중복 없는 일반 열 라벨을 전제로 `df['열']`은 해당 `Series`, `df[['열']]`은 열 이름 목록으로 선택한 `DataFrame`이다. 바깥 대괄호는 선택, 안쪽 대괄호는 이름 목록이며 같은 구조로 취급하면 안 된다. | [Indexing: Basics](https://pandas.pydata.org/pandas-docs/version/1.5/user_guide/indexing.html#basics) |
| 위치와 라벨 | `iloc`는 축의 0부터 길이−1까지의 정수 위치를 기준으로 고른다. `loc`는 라벨 기준이며 정수도 라벨로 해석한다. 기본 행 라벨이 0부터 연속이라고 해서 두 의미가 같아지는 것은 아니다. | [Indexing: Different choices for indexing](https://pandas.pydata.org/pandas-docs/version/1.5/user_guide/indexing.html#different-choices-for-indexing) |

## 선수 지식과 범위 검토에 남길 사항

위 구문은 Python 이름·문자열·리스트·딕셔너리·함수 호출과 속성 접근을 사용한다. 이 표만으로 초보자가 이미 해당 표기를 안다고 간주하지 않는다. 어느 표기까지 첫 수업에서 직접 다룰지, 제공 코드로 둘지, 이후 수업으로 나눌지는 이번 조사에서 결정하지 않았다.

이번 범위의 리스트 열 생성 규칙을 인덱스를 가진 `Series` 열의 자동 정렬 규칙까지 일반화하지 않는다. 단일 열 선택 설명은 중복 열 라벨·다중 인덱스를 포함한 모든 경우의 일반 법칙으로 확장하지 않는다. 필터링·결측치·정렬·형 변환·모델 입력 형상·복사와 변경의 세부 규칙은 이번 기초 조사 범위로 채택하지 않았다.

## 검증 한계

- 이번 확인은 문서 열람이다. pandas 설치·실행·CSV 파일 읽기·플레이어 파일 자원 제공 방식·출력 렌더링은 검증하지 않았다.
- AICE 환경 표기와 공식 시험 범위는 별도 [Python 기초 조사](aice-python-foundations-2026-10-19.md) 및 [시험 조사](aice-associate-exam-2026-10-18.md)를 따른다. pandas 1.5.3 문서 열람만으로 실제 회차 커널 버전 일치를 주장하지 않는다.
- 이번에 인용한 페이지는 버전 표제가 확인되었으나 앞으로 URL이 같은 본문을 계속 제공한다는 보장은 아니다. 이후 구현·실행 검증에서도 실제 패키지 버전을 기록해야 한다.
- 문제 수·순서·교육 기법·채점 기준은 미정이다. 이 노트는 언어/API 사실의 근거이며 특정 교수법의 효과나 공식 채점기의 재현을 입증하지 않는다.
