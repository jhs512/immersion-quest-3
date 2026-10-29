# AICE·정보처리기사 54수업 도전 판단표와 개선 이전 (2026-10-29)

`docs/plans/2026-10-29-final-challenges-all-courses.md` 4절의 실행 기록이에요. 백엔드와 같은 규칙(새 고유 코드의 새 마지막 스텝, 기존 스텝·ID·기록 불변, 자기 시작 상태에서 바로 풀기, 실제 채점기 증거)을 써요.

## 1. 지금 마지막 문제를 그대로 지정하지 않는 이유 (54수업 공통으로 직접 확인)

- AICE 24수업: 마지막 문제 22개는 「한 곳만 고치세요」 단일 수정(how, pos_label, n_estimators, patience 등), 2개(aice-python-start, aice-table-csv)는 선택형이에요. 배운 원리 여러 개를 새 조건에 옮기는 문제가 아니라서 지정하면 「임의의 마지막 연습에 이름표만 붙이기」가 돼요.
- 정보처리기사 30수업: 마지막 문제는 선택형 16, 한 칸 답 쓰기 9(실행해서 읽을 수 있는 출력 포함), 한 곳 수정 5(C·SQL)예요. 같은 이유로 지정하지 않아요.
- 따라서 54수업 모두 새 도전을 작성해요. 실제 채점기가 없는 과목은 없어서(파이썬·C·자바·SQLite·답 채점) 「도전 없음」으로 남길 수업은 지금 판단으로 없어요. 작성하지 못한 수업은 아래 표의 상태 칸에 「작성 전」으로 정확히 남기고 게시 코스에 지정하지 않아요.

## 2. 수업별 도전 설계

채점: py=실제 파이썬 실행 출력 + 준비 값 바꾸기(`prepared_cases`), c=tcc 실행 출력 + 값 바꾸기(`variations`), java=JDK 출력 + 값 바꾸기, sql=SQLite 결과 + 다른 준비 자료, 답=여러 칸 답 채점(`fill_fields`, 실기 필답형). 답 채점 도전은 실행해서 베낄 코드가 없거나 계산·판단을 여러 칸 함께 요구해요.

| 수업 | 지금 마지막 문제 | 도전 상황(배운 원리의 전이) | 채점 | 막을 오답 | 상태 |
| --- | --- | --- | --- | --- | --- |
| aice-python-start | 선택형 | 배송 시간 목록의 건수·첫 값·마지막 값(위치=건수-1)을 출력 | py | 3·[2] 고정, 값 직접 적기 | 작성 전 |
| aice-python-conditions | 한 곳 수정 | 기준 이상(같음 포함) 배송만 새 목록에 모으고 건수 출력 | py | > 경계, 고정 개수 | 작성 전 |
| aice-python-api | 한 곳 수정 | 딕셔너리 자료에서 항목 이름으로 목록을 꺼내 별칭 모듈로 평균, 건수와 항목 수 구별 | py | 위치로 접근, 키 수를 건수로 | 작성 전 |
| aice-table-csv | 선택형 | CSV를 읽어 전체 크기와 두 열의 앞 두 행을 출력 | py | head를 크기로, 열 하나만 | 작성 전 |
| aice-selection | 한 곳 수정 | 경계 포함 조건+지역 조건으로 고르고 오래 걸린 순 정렬, 평균·중앙값 | py | 경계 제외, 오름차순 | 작성 전 |
| aice-quality | 한 곳 수정 | 빈 시간 제외·주문별 마지막 수정본·0분 유지 후 건수와 평균 | py | 0분 삭제, 첫 수정본 | 작성 전 |
| aice-join | 한 곳 수정 | 두 달 배송을 붙이고 회원 지역을 left로 연결, 미등록은 unknown, 지역별 건수 | py | inner, 순서 잃음 | 작성 전 |
| aice-plots | 한 곳 수정 | 지역별 평균 거리 막대를 그리고 막대 높이를 출력 | py | 개수 막대, 합계 | 작성 전 |
| aice-features | 한 곳 수정 | 숫자 변환 실패 표시, 범주 표시 열, 입력 열에서 정답·식별자 제외 | py | 오류 숨김, id 포함 | 작성 전 |
| aice-split | 한 곳 수정 | X·y를 함께 층화 분할하고 크기·비율·짝 확인 | py | 따로 섞기, 반환 순서 | 작성 전 |
| aice-leakage | 한 곳 수정 | 정답·미래 열 제외, 훈련 평균으로 두 자료 채우기 | py | 전체 평균, 정답 포함 | 작성 전 |
| aice-scale | 한 곳 수정 | 결측 채움→스케일을 훈련에서 배우고 평가에는 transform만 | py | 평가에서 fit | 작성 전 |
| aice-regression | 한 곳 수정 | 기준 모델과 선형 회귀를 훈련해 남겨둔 자료 MAE 비교 | py | 훈련 자료 예측 | 작성 전 |
| aice-regression-metrics | 한 곳 수정 | 행 대응을 맞춘 뒤 MAE·RMSE·R²를 함께 보고 | py | 정렬 어긋남, MSE 단위 | 작성 전 |
| aice-classification | 한 곳 수정 | 분류 모델 학습 후 classes_로 late 확률 열을 찾아 기준 이상 경보 | py | 고정 열 번호 | 작성 전 |
| aice-classification-metrics | 한 곳 수정 | late 기준 정밀도·재현율·F1과 임계값 변경 | py | pos_label 기본값 | 작성 전 |
| aice-models | 한 곳 수정 | 같은 검증 자료로 두 후보를 학습·비교해 MSE 작은 쪽 고르기 | py | 훈련 점수 비교 | 작성 전 |
| aice-boosting | 한 곳 수정 | XGBoost 회귀에 정한 학습률·반복 수를 연결하고 문자 범주를 인덱스로 | py | 기본 설정 | 작성 전 |
| aice-tuning | 한 곳 수정 | Pipeline+GridSearchCV 그리드 키와 음수 점수 방향 | py | 키 이름, 부호 | 작성 전 |
| aice-tensorflow | 한 곳 수정 | 입력 특성 수·출력 칸·compile·fit·predict 모양 | py | 행 수를 특성 수로 | 작성 전 |
| aice-neural-regression | 한 곳 수정 | 음수 불가 목표의 출력 활성화·회귀 손실·평가 | py | sigmoid, 분류 손실 | 작성 전 |
| aice-neural-classification | 한 곳 수정 | 다중 범주 softmax 출력 수·정수 정답 손실·이름 연결 | py | 원핫 손실, 위치 착오 | 작성 전 |
| aice-training | 한 곳 수정 | 조기 종료 patience·최고 가중치 복원·멈춘 epoch | py | 복원 없음 | 작성 전 |
| aice-integration | 한 곳 수정 | 열 종류별 전처리+모델 파이프라인, 새 파일 예측을 주문번호와 출력 | py | 열 누락, 번호 잃음 | 작성 전 |
| engineer-c-start | 한 칸 답 | 대입 순서가 섞인 재고 계산 코드의 세 출력 | 답 | 최종값만 | 작성 전 |
| engineer-c-conditions | 선택형 | 몫·나머지·경계 조건으로 포장 수와 부족분을 출력하는 코드 완성 | c | 경계 > | 작성 전 |
| engineer-c-arrays | 한 곳 수정 | 사용 개수까지 반복해 합계와 최댓값 위치 | c | count-1, 고정 길이 | 작성 전 |
| engineer-c-functions | 한 곳 수정 | 재귀 합과 static 호출 횟수 | c | 끝 조건 누락 | 작성 전 |
| engineer-c-pointers | 한 곳 수정 | 포인터로 두 재고를 바꾸는 함수 | c | 값 복사 | 작성 전 |
| engineer-c-double-pointers | 한 곳 수정 | 이중 포인터로 호출자의 포인터를 최소 재고 칸으로 옮기기 | c | 한 층만 | 작성 전 |
| engineer-c-structures | 한 칸 답 | 구조체 배열과 함수 포인터로 규칙을 골라 합계 | c | 값 복사 수정 | 작성 전 |
| engineer-java-flow | 한 칸 답 | 정수 나눗셈·단락 평가·continue가 섞인 집계 메서드 완성 | java | 순서 착오 | 작성 전 |
| engineer-java-references | 한 칸 답 | 원본을 지키는 배열 복사와 필드 수정 메서드 | java | 별칭 반환 | 작성 전 |
| engineer-java-static | 한 칸 답 | 공유 일련번호와 객체 필드를 나누는 클래스 | java | 객체마다 번호 | 작성 전 |
| engineer-java-polymorphism | 한 칸 답 | 재정의·finally 순서가 섞인 호출 결과 세 줄 | 답 | 선언형 호출 | 작성 전 |
| engineer-python-values | 한 칸 답 | 슬라이스·얕은 복사·딕셔너리 기본값 처리 함수 | py | 공유 목록 수정 | 작성 전 |
| engineer-python-calls | 한 칸 답 | 가변 기본 인수 없이 누적하는 함수와 키워드 인수 | py | 공유 기본값 | 작성 전 |
| engineer-db-model | 선택형 | 기본키·외래키·NOT NULL로 재고 표 정의 | sql | 중복·없는 참조 허용 | 작성 전 |
| engineer-sql-select | 한 곳 수정 | NULL·범위·외부 조인이 섞인 재주문 조회 | sql | NULL 누락 | 작성 전 |
| engineer-sql-group | 한 곳 수정 | WHERE·GROUP BY·HAVING·정렬을 함께 쓰는 보고 | sql | 행 조건 혼동 | 작성 전 |
| engineer-sql-change | 선택형 | 모르는 재고만 0으로 고치고 0 재고만 지우는 변경 | sql | NULL 비교 | 작성 전 |
| engineer-db-storage | 선택형 | 정규형 판단·인덱스·트리거 역할 세 칸 | 답 | — | 작성 전 |
| engineer-requirements | 선택형 | 요구 분류·검증 방법·영향 범위 세 칸 | 답 | — | 작성 전 |
| engineer-design | 선택형 | 세 상황의 패턴 이름 | 답 | — | 작성 전 |
| engineer-server | 한 칸 답 | 결합도·응집도·배치 재처리 판단 세 칸 | 답 | — | 작성 전 |
| engineer-interfaces | 선택형 | 단위·멱등·중복 방지 판단 세 칸 | 답 | — | 작성 전 |
| engineer-ui | 선택형 | 오류 안내·키보드 순서·상태 판단 세 칸 | 답 | — | 작성 전 |
| engineer-test-cases | 선택형 | 경계값 두 개와 기법 이름 | 답 | — | 작성 전 |
| engineer-test-integration | 선택형 | 문장·분기 커버리지와 스텁/드라이버 | 답 | — | 작성 전 |
| engineer-security | 선택형 | 인증/인가·해시·SQL 분리 판단 세 칸 | 답 | — | 작성 전 |
| engineer-os | 선택형 | SJF 평균 대기·페이지 부재 수·교착 조건 | 답 | — | 작성 전 |
| engineer-network | 한 칸 답 | 서브넷 블록의 네트워크·브로드캐스트·호스트 수 | 답 | — | 작성 전 |
| engineer-build | 선택형 | 버전 판단 세 칸 | 답 | — | 작성 전 |
| engineer-mixed | 선택형 | 코드·SQL·검증 범위를 잇는 세 칸 | 답 | — | 작성 전 |

## 3. 개선 이전 상태 (계획 4절 표의 실행)

| 개선 | AICE | 정보처리기사 | 메모 |
| --- | --- | --- | --- |
| 1 수업별 진도 초기화 | 앱 공통(코드 분기 없음) | 같음 | 대표 수업 실제 화면 확인 대상 |
| 2 마지막 도전 클리어 | 위 표 | 위 표 | 지정은 작성·검증·게시한 수업만 |
| 3 분류 묶음 | 제안 6분류 검토 후 승인 예정 | 제안 7분류 검토 후 승인 예정 | track은 2026-10-25 결정(기본) 유지 |
| 3'' 진입 안내 | 도전 작성 뒤 작성 | 같음 | |
| 4 할 일·해설 형식 | 빌드 공통 검사 적용됨 | 같음 | 새 도전에만 추가 적용 |
| 5 해설 속도·발음 | 앱 공통 | 같음 | |
| 6 실습 환경 수명 | 외부 자원 없음 | 같음 | 해당 없음 |
| 7 테마·통계 | 앱 공통 | 같음 | |
