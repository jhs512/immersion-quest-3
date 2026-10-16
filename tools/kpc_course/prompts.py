"""The answer prompt for every coding problem, written the way a person actually types it.

Each entry is (prompt, why). `prompt` is what "프롬프트 복사 · 인간 버전" copies: two to five
short lines a student would type into an AI, ending with "코드만 줘". The analyst's vocabulary
(temporal split, 누수, stratify, baseline, ...) sits only where it changes the answer. `why`
is the whole guide for that prompt: a few "단어 → 이유" lines, nothing more.
"""

TAIL = "\n\n---\n코드만 줘"


def p(body, why):
    return (body.strip() + TAIL, why.strip())


PROMPTS = {
    # ----
    "hello": p("""
파이썬에서 "Hello, KPC!" 출력하는 코드
""", """
- `파이썬` → 언어를 정한다.
- `"Hello, KPC!"` → 글자 단위로 채점. 따옴표 안 그대로.
- `코드만 줘` → 설명이 섞이면 붙여 넣을 때 깨진다.
"""),
    "print-calc": p("""
파이썬. 10000 * 3을 계산해서 결과 30000만 출력. 따옴표로 감싼 글자 말고 실제 계산.
""", """
- `계산해서` → `print("30000")`처럼 글자로 박는 답을 막는다.
- `30000만 출력` → 다른 글자 없이 숫자만.
"""),
    "variable-print": p("""
파이썬. price = 10000, quantity = 3 이 있어. 둘을 곱한 값을 amount 변수에 저장하고 print(amount).
변수 이름 그대로 써.
""", """
- `amount` → 검사기는 변수 이름으로 읽는다. 이름이 다르면 정답도 실패.
- `변수 이름 그대로` → AI가 이름을 바꾸는 버릇을 막는다.
"""),
    "single-input": p("""
파이썬. 표준 입력 한 줄로 수량(정수)이 들어와. int로 받아서 가격 10000과 곱한 금액을 출력.
입력 3이면 30000.
""", """
- `표준 입력` → `input()`. 안내 문구 없이 읽게 한다.
- `int로 받아서` → 글자를 숫자로 형 변환해야 곱셈이 된다.
- `입력 3이면 30000` → 예시 한 쌍이 형식 설명을 대신한다.
"""),
    "amount-input": p("""
파이썬. 표준 입력 한 줄에 "가격 수량"이 공백으로 들어와. 둘 다 int로 받아 곱한 금액만 출력.
입력 "10000 3" → 출력 30000
""", """
- `한 줄에 공백으로` → 입력 형식. 안 적으면 두 줄로 받는다.
- `금액만 출력` → "금액: 30000"처럼 꾸미지 않게.
"""),
    "fstring-report": p("""
파이썬. 표준 입력 한 줄 "가격 수량"(공백, 정수). 곱한 금액을 f-string으로 "금액: 30000원" 형식 그대로 출력.
콜론 뒤 공백 하나, 숫자 뒤에 바로 "원".
""", """
- `f-string` → 글자와 값을 섞는 표준 방법을 지정.
- `콜론 뒤 공백 하나` → 띄어쓰기까지 채점한다.
"""),
    # ----
    "list-index": p("""
파이썬. prices = [10000, 10200, 10100] 에서 첫 값을 first, 마지막 값을 last에 담고 둘 다 출력.
인덱스로 꺼내.
""", """
- `인덱스로 꺼내` → `prices[0]`, `prices[-1]`. min/max로 우연히 맞히는 답을 막는다.
- `first`, `last` → 검사기가 읽는 이름.
"""),
    "list-len-sum": p("""
파이썬. prices = [10000, 10200, 10100]. 개수를 count, 합계를 total에 담고 출력. len과 sum 써.
""", """
- `len과 sum 써` → 반복문 대신 내장 함수. 원하는 도구는 이름으로 부른다.
"""),
    "dict-read": p("""
파이썬. holding = {'name':'연습A', 'price':10000, 'quantity':3} 딕셔너리에서 price와 quantity를 키로 꺼내 곱한 값을 amount에 저장하고 출력.
딕셔너리는 수정하지 마.
""", """
- `키로 꺼내` → `holding['price']` 방식.
- `수정하지 마` → 검사기가 원본 딕셔너리를 확인한다.
"""),
    "holdings-access": p("""
파이썬. holdings 는 종목 딕셔너리 3개가 든 리스트야 (키: name, price, quantity).
두 번째 종목의 name을 second_name, 세 번째 종목의 price를 third_price에 담고 출력.
""", """
- `딕셔너리 3개가 든 리스트 (키: …)` → 구조를 말하면 `holdings[1]['name']`이 바로 나온다.
"""),
    "holding": p("""
파이썬. holding = {'name':'연습A', 'price':10000, 'quantity':3}. quantity를 5로 바꾸고, price * quantity를 새 키 amount에 저장. holding['amount']가 50000이어야 해.
""", """
- `새 키 amount에 저장` → 딕셔너리를 수정하라는 뜻.
- `50000이어야 해` → 바뀐 수량으로 계산했는지 AI가 스스로 검산.
"""),
    "price-average": p("""
파이썬. prices = [10000, 10200, 10100]에 10300을 append하고, 개수를 count, 평균을 average에 담아 출력.
평균은 sum/len으로.
""", """
- `append` → 맨 뒤에 추가하는 메서드 지정.
- `sum/len으로` → numpy·statistics를 끌어오지 않게.
"""),
    # ----
    "simple-if": p("""
파이썬. 표준 입력으로 가격(정수) 한 줄. 10000 이상이면 "기준 이상", 아니면 "기준 미만" 출력. if/else로.
10000은 "기준 이상".
""", """
- `10000은 "기준 이상"` → 경계값을 예시로 못 박아 `>`/`>=` 혼동을 막는다.
"""),
    "for-sum": p("""
파이썬. prices = [10000,10200,9900,10100]. sum() 쓰지 말고 for 반복문으로 total에 누적해서 출력.
""", """
- `sum() 쓰지 말고 for로` → 금지와 지정을 한 줄에. 연습 목적이면 쉬운 길을 막는다.
"""),
    "above-count": p("""
파이썬. prices = [10000,10200,9900,10100]. for 한 번 돌면서 합계는 total, 10000 이상인 값의 개수는 above_count에 누적. 둘 다 출력.
""", """
- `for 한 번 돌면서` → 반복 안에 if를 넣는 구조를 요구. 안 적으면 따로따로 계산한다.
"""),
    "max-price": p("""
파이썬. prices = [10000,10200,9900,10100]. max() 쓰지 말고, highest = prices[0]에서 시작해 for와 if로 더 큰 값 만나면 갱신. 결과 highest 출력.
""", """
- `prices[0]에서 시작해 … 갱신` → 알고리즘을 한 문장으로. AI는 옮겨 적기만 한다.
- `max() 쓰지 말고` → 쉬운 길 금지.
"""),
    "croissant-plan": p("""
파이썬. 지난 사흘 크루아상 판매량 sold = [412, 388, 455].
for로 합계를 total에 누적(sum 금지), 평균을 average에, 평균의 1.1배를 round한 정수를 plan에 담아 "오늘 생산 계획: 460개" 형식으로 출력.
""", """
- `1.1배를 round한 정수` → "여유 있게"를 계산식으로. 규칙은 숫자로 적는다.
- `"오늘 생산 계획: 460개" 형식` → 출력 모양 고정.
"""),
    "holdings-amounts": p("""
파이썬. holdings 는 {'name','price','quantity'} 딕셔너리 3개가 든 리스트. for로 돌면서 각 딕셔너리에 price*quantity를 amount 키로 추가. holdings 자체를 수정.
""", """
- `holdings 자체를 수정` → 새 리스트를 만들면 실패. 결과를 어디에 남길지 적는다.
"""),
    "holdings-total": p("""
파이썬. holdings 리스트의 각 딕셔너리에 amount 키가 있어. 세 amount를 더해 total_amount에 담고 출력. 결과 130000.
""", """
- `결과 130000` → 답을 알면 적는다. AI가 quantity를 더하는 실수를 스스로 거른다.
"""),
    "holdings-frame": p("""
pandas. holdings(딕셔너리 리스트, 키 name·price·quantity·amount)를 DataFrame으로 만들어 df에 담고 마지막 줄에 df.
열 순서 name, price, quantity, amount.
""", """
- `pandas`, `DataFrame` → 이제 도구가 바뀐다고 선언.
- `열 순서` → 검사기가 순서를 본다.
- `마지막 줄에 df` → 이 앱은 마지막 표현식을 표로 보여 준다.
"""),
    "frame-column-sum": p("""
pandas. df(열 name·price·quantity·amount)에서 amount 열의 합을 .sum()으로 구해 total_amount에 담고 출력.
""", """
- `amount 열의 합을 .sum()으로` → 반복문 대신 열 연산. `df['amount'].sum()` 한 줄.
"""),
    "numpy-race": p("""
파이썬. values 리스트(0~999999)와 같은 값의 넘파이 배열 array가 있어.
for 반복문 합계는 total, array.sum()은 numpy_total에 담고
time.perf_counter()로 걸린 시간을 loop_seconds, numpy_seconds에 재서 두 시간과 몇 배 빠른지 출력
""", """
- `time.perf_counter()` → 시간 재는 함수를 지정해야 `time.time()`처럼 거친 시계를 안 쓴다.
- `total`, `numpy_total`, `loop_seconds`, `numpy_seconds` → 검사기가 읽는 이름 넷.
- `몇 배 빠른지` → 숫자 둘만 찍고 끝내지 않게.
"""),
    # ----
    "inspect-frame": p("""
pandas. orders DataFrame(열 product, price, quantity, 4행)이 있어. 행 수 n_rows, 열 수 n_columns, 열 이름 리스트 column_names에 담고 출력.
shape와 columns 써.
""", """
- `shape와 columns` → 표의 뼈대를 보는 속성 이름.
- `열 이름 리스트` → `list(df.columns)`. Index 그대로면 검사 실패.
"""),
    "to-csv": p("""
pandas. orders DataFrame을 orders.csv로 저장(index=False)하고 다시 read_csv로 읽어 saved에 담아. 마지막 줄에 saved.
""", """
- `index=False` → 없으면 행 번호가 열로 끼어들어 4열이 된다.
"""),
    "csv-excel": p("""
pandas. orders DataFrame을 CSV와 Excel(xlsx) 두 형식으로 저장(둘 다 index=False)하고 각각 다시 읽어 csv_df, excel_df에 담아.
Excel은 openpyxl 엔진.
""", """
- `openpyxl 엔진` → 이 환경에 설치된 Excel 라이브러리를 지정.
- `둘 다 index=False` → 행 번호 열 방지.
"""),
    "series-vs-frame": p("""
pandas. orders DataFrame에서 orders['price']를 price_series, orders[['price']]를 price_frame에 담고 각각 type() 출력.
""", """
- `orders['price']` / `orders[['price']]` → 대괄호 한 겹·두 겹을 코드로 그대로. 말로 풀면 오해가 생긴다.
"""),
    "selection": p("""
pandas. orders DataFrame에서 product, price 두 열만 고른 표를 selected에, iloc으로 첫 두 행만 고른 표를 first_two에 담아.
""", """
- `iloc으로` → 자리 번호로 행 고르기. 안 적으면 `head(2)`를 준다.
"""),
    "loc-condition": p("""
pandas. orders DataFrame에서 quantity가 3 이상인 행만 불리언 마스크로 골라 many에 담고 마지막 줄에 many.
""", """
- `불리언 마스크` → 참·거짓 마스크. 행마다 참·거짓을 매겨 참인 행만 남긴다: `orders[orders['quantity'] >= 3]`.
"""),
    "read-csv-titanic": p("""
pandas. data/titanic.csv를 read_csv로 읽어 titanic에 담고, titanic.shape 출력, 마지막 줄에 titanic.head().
""", """
- `data/titanic.csv` → 경로를 그대로. 안 적으면 AI가 URL이나 다른 경로를 가정한다.
- `shape`, `head()` → 새 자료를 받으면 처음 보는 두 가지.
"""),
    # ----
    "count-missing": p("""
pandas. orders DataFrame(price 열에 결측 1개). isna().sum()으로 열별 결측 개수를 missing_counts에 담고, price 열 결측 개수를 int로 n_missing_price에 담아 출력.
""", """
- `결측`, `isna().sum()` → 빈칸을 세는 표준 용어와 메서드.
- `int로` → pandas 숫자형이 아니라 파이썬 정수. 검사기가 자료형을 본다.
"""),
    "fill-median": p("""
pandas. orders['price']에 결측 1개. 중앙값을 median_price에, 결측을 중앙값으로 채운 열을 filled_price에 담아 둘 다 출력.
원본 orders는 바꾸지 마 (fillna 결과를 새 변수에).
""", """
- `중앙값으로 채운` → 결측 처리 방법을 지정.
- `원본은 바꾸지 마` → `inplace=True`를 막는다. 검사기가 원본을 본다.
"""),
    "drop-missing": p("""
pandas. orders DataFrame에서 price가 결측인 행을 dropna로 빼서 dropped에 담고, 남은 행 수를 int로 n_left에. 둘 다 출력, 마지막 줄에 dropped.
""", """
- `dropna로 빼서` → 채우기의 반대편 길을 메서드 이름으로.
"""),
    "filter-orders": p("""
pandas. orders에서 price >= 12000 이고 quantity >= 2 인 행만 골라 selected에 담아. 두 조건은 & 로 묶고 각각 괄호. 결과에 .copy().
열은 product, price, quantity 유지.
""", """
- `& 로 묶고 각각 괄호` → pandas에서 가장 흔한 실수(`and`, 괄호 누락)를 미리 막는다.
- `.copy()` → 뒤에서 고쳐도 원본이 안 바뀌게. 검사기가 본다.
"""),
    "or-filter": p("""
pandas. orders에서 product == 'A' 이거나 quantity == 1 인 행을 | 로 골라 either에 담고 마지막 줄에 either.
""", """
- `| 로` → pandas의 "또는". 파이썬 `or`를 쓰면 오류.
"""),
    "missing-totals": p("""
pandas. orders(price 결측 1개). 결측을 중앙값으로 채운 표를 filled, 결측 행을 뺀 표를 dropped에 만들고, 각 표에 price*quantity 열 amount를 추가해 합계를 filled_total, dropped_total에 담아 둘 다 출력.
둘 다 원본은 건드리지 말고 .copy().
""", """
- `채운 표 filled`, `뺀 표 dropped` → 두 처리를 나란히. 결측 처리에 따라 합계가 달라진다는 걸 보이는 설계.
- `.copy()` → 원본 보호.
"""),
    # ----
    "string-to-int": p("""
파이썬. price_text = '10,000'. 쉼표를 지우고 int로 바꿔 price에 담은 뒤 price * 3 출력.
""", """
- `쉼표를 지우고 int로` → 순서가 중요. `'10,000'`은 그대로 `int()`에 넣으면 오류.
"""),
    "select-one": p("""
파이썬 BeautifulSoup. soup 객체가 있어(data/prices.html). CSS 선택자 "#prices li"에 해당하는 요소 개수를 n_items에, 첫 요소 안 ".name"의 텍스트를 first_name에 담고 출력.
select와 select_one 써.
""", """
- `CSS 선택자 "#prices li"` → 선택자를 그대로 주면 AI는 옮겨 적기만 한다.
- `select`, `select_one` → 여러 개 / 하나 찾기 메서드.
"""),
    "select-prices": p("""
파이썬 BeautifulSoup. soup 객체가 있어. "#prices li b" 요소들의 텍스트를 꺼내 쉼표 제거 후 int로 바꿔 prices 리스트에 모아 출력. 결과 [10000, 20000].
""", """
- `텍스트 → 쉼표 제거 → int → 리스트` → 수집의 네 단계를 순서대로. 하나라도 빠지면 다른 답.
"""),
    "parse-html": p("""
파이썬 BeautifulSoup + pandas. data/prices.html을 읽어 soup를 만들고, "#prices li"를 돌면서 data-code 속성, .name 텍스트, b 텍스트(쉼표 제거 후 int)를 딕셔너리로 rows 리스트에 모은 뒤 pd.DataFrame(rows)를 df에. 열 이름 code, name, price.
""", """
- `data-code 속성` vs `.name 텍스트` → 속성과 글자를 구분해서 요청.
- `딕셔너리로 rows에 모아 DataFrame` → 수집 결과를 표로 만드는 표준 패턴.
"""),
    # ----
    "titanic-shape": p("""
pandas. titanic = pd.read_csv('data/titanic.csv'). 행 수 n_rows, 열 수 n_columns, 열 이름 리스트 columns에 담고 출력.
""", """
- `titanic = pd.read_csv(...)` → 준비 코드를 그대로 보여 주면 경로·이름을 안 틀린다.
"""),
    "survived-counts": p("""
pandas. titanic DataFrame. 생존 열을 value_counts()해서 counts에 담고, 0(사망) 인원을 n_dead, 1(생존) 인원을 n_alive에 int로 담아 출력.
""", """
- `value_counts()` → 범주를 세는 표준 메서드.
- `0(사망)`, `1(생존)` → 값의 뜻을 적어야 두 변수가 안 바뀐다.
"""),
    "missing-per-column": p("""
pandas. titanic DataFrame. isna().sum()을 missing에 담고, 나이와 요금의 결측 수를 int로 age_missing, fare_missing에 담아 출력.
""", """
- `isna().sum()` → 열별 결측. 자료를 받으면 제일 먼저.
- `int로` → 검사기 자료형.
"""),
    "titanic-counts": p("""
pandas. titanic DataFrame. 전체 인원 n_total, 나이가 기록된 인원 n_known, 나이가 결측인 인원 n_unknown을 int로, 생존의 평균을 survival_rate에 담아 전부 출력.
n_known + n_unknown == n_total 이어야 해.
""", """
- `생존의 평균` → 0/1 열의 평균이 곧 비율.
- `n_known + n_unknown == n_total` → 검산식을 주면 AI가 스스로 확인한다.
"""),
    # ----
    "sex-counts": p("""
pandas. titanic DataFrame. 성별 열 value_counts()를 gender_counts에 담고 출력.
""", """
- `value_counts()` → 비율 전에 분모(인원)부터.
"""),
    "sex-mean": p("""
pandas. titanic DataFrame. groupby('성별')['생존'].mean()을 rates에 담고 출력.
""", """
- `groupby('성별')['생존'].mean()` → 그룹별 비율 공식을 코드로. 코드로 쓸 수 있으면 그게 제일 정확하다.
"""),
    "sex-summary": p("""
pandas. titanic DataFrame. 성별로 groupby한 생존에 agg(['count','sum','mean'])을 적용한 표를 gender_summary에 담고 마지막 줄에 gender_summary.
""", """
- `agg(['count','sum','mean'])` → 인원·생존자·생존율을 한 표에. "몇 명 중"을 늘 같이 본다.
"""),
    "pclass-summary": p("""
pandas. titanic DataFrame. 객실등급으로 groupby한 생존에 agg(['count','sum','mean'])을 적용해 pclass_summary에.
""", """
- 앞 프롬프트에서 `성별`을 `객실등급`으로만 바꿈. 같은 집계는 프롬프트도 복사해서 쓴다.
"""),
    "age-groups": p("""
pandas. titanic DataFrame. pd.cut으로 나이를 bins=[0, 20, 40, 60, float('inf')], labels=['0~19','20~39','40~59','60+'], right=False 로 나눈 열 age_group을 titanic에 추가하고, age_group으로 groupby한 생존의 agg(['count','sum','mean'])을 age_summary에.
""", """
- `bins=…, labels=…` → "20대, 30대"라고 하면 경계가 AI마다 다르다. 숫자로.
- `right=False` → 20살이 `20~39`에 들어가게. 구간 문제의 단골 실수.
"""),
    # ----
    "simple-bar": p("""
matplotlib. names = ['A','B','C'], amounts = [30000,40000,60000]. fig, ax = plt.subplots()로 만들고 ax.bar로 막대그래프. ax.set(title='종목별 금액', ylabel='금액'). plt.show().
""", """
- `fig, ax = plt.subplots()`, `ax.bar` → 검사기는 `ax` 객체를 읽는다. `plt.bar()`는 못 읽는다.
- 제목·축 이름 문자열 → 그대로 채점.
"""),
    "sex-bar": p("""
pandas + matplotlib. titanic DataFrame. groupby('성별')['생존'].mean()을 rates에 담고, rates*100을 ax.bar로 그려. ylim=(0,100), xlabel '성별', ylabel '생존율 (%)'. fig, ax = plt.subplots() 방식, plt.show().
""", """
- `rates*100` + `ylim=(0,100)` → 퍼센트 축은 둘이 한 세트. 하나만 적으면 축과 값이 안 맞는다.
"""),
    "pclass-bar": p("""
pandas + matplotlib. titanic DataFrame. groupby('객실등급')['생존'].mean()을 rates에 담고 rates*100을 ax.bar로. ylim=(0,100), xlabel '객실등급', ylabel '생존율 (%)'. fig, ax 방식, plt.show().
""", """
- 앞 프롬프트에서 열 이름과 축 이름만 바꿈.
"""),
    # ----
    "age-hist": p("""
pandas + seaborn. titanic DataFrame. 나이가 결측이 아닌 행만 known_age에 담고, fig, ax = plt.subplots() 뒤 sns.histplot(data=known_age, x='나이', bins=20, ax=ax). 축 이름과 제목 붙이고 plt.show().
""", """
- `결측이 아닌 행만` → 그림 전에 자료부터 거른다.
- `bins=20` → 검사 조건.
- `ax=ax` → seaborn을 우리 Axes에 그리게. 빠지면 검사기가 그림을 못 찾는다.
"""),
    "fare-scatter": p("""
pandas + matplotlib. titanic DataFrame. 나이와 요금 둘 다 결측이 아닌 행만 known에 담고, fig, ax 만든 뒤 ax.scatter(known['나이'], known['요금']). xlabel '나이', ylabel '요금'. plt.show().
""", """
- `둘 다 결측이 아닌 행만` → 산점도의 전제.
- `scatter(known['나이'], known['요금'])` → x, y 순서 고정.
"""),
    "correlation": p("""
pandas + seaborn. titanic DataFrame. columns=['객실등급','나이','형제배우자','부모자녀','요금','생존'] 열의 상관계수 표를 corr에 담고(titanic[columns].corr()), sns.heatmap(corr, annot=True, vmin=-1, vmax=1, ax=ax)로 그려. fig, ax 방식, plt.show().
""", """
- `.corr()` → 상관계수 표.
- `vmin=-1, vmax=1` → 색 범위를 고정해야 다른 자료와 비교된다.
- `annot=True` → 칸에 숫자.
"""),
    # ----
    "embarked-rate": p("""
pandas. titanic DataFrame. 탑승항구로 groupby한 생존의 agg(['count','mean'])을 by_port에 담고 마지막 줄에 by_port.
""", """
- `count`를 같이 → 항구별 인원이 다르면 비율의 신뢰도도 다르다.
"""),
    "sex-pclass-table": p("""
pandas. titanic DataFrame. ['성별','객실등급']로 groupby한 생존의 agg(['count','mean'])을 grouped에, grouped['mean'].unstack('객실등급')를 wide에 담고 마지막 줄에 wide.
""", """
- `['성별','객실등급']로 groupby` → 두 조건으로 묶기.
- `unstack('객실등급')` → 긴 표를 행×열 교차표로 펼치는 메서드.
"""),
    "combined-groups": p("""
pandas + matplotlib. titanic DataFrame. ['성별','객실등급'] groupby 생존 agg(['count','mean'])을 grouped에, grouped['mean'].unstack('객실등급')*100을 wide에. ax = wide.plot.bar(ylim=(0,100), rot=0)로 그리고 ylabel과 title 붙여 plt.show().
""", """
- `wide.plot.bar(...)` → 표에서 바로 묶음 막대. 반환값을 `ax`에 담아야 검사기가 읽는다.
- `rot=0` → x축 글자 안 눕히기.
"""),
    # ----
    "drop-columns": p("""
pandas. titanic DataFrame. drop(columns=[...])으로 생존, 이름, 티켓, 선실, 구명보트, 시신번호, 출신목적지 를 빼서 candidates에 담고 열 이름 출력. 7열 남아야 해.
""", """
- `구명보트, 시신번호` 빼기 → 사고 뒤에 적히는 열. 넣으면 누수. 이 판단은 자료를 아는 사람이 한다.
- `7열 남아야 해` → 검산.
"""),
    "xy-separation": p("""
pandas. titanic DataFrame. features = ['객실등급','성별','나이','형제배우자','부모자녀','요금','탑승항구'] 리스트를 만들고, X = titanic[features].copy(), y = titanic['생존'].astype(int).
""", """
- `X`, `y` → 입력과 정답. 머신러닝의 첫 줄.
- `.copy()`, `.astype(int)` → 뒤에서 나는 경고·자료형 문제를 미리 막는다.
"""),
    "column-types": p("""
pandas. X DataFrame(열 객실등급, 성별, 나이, 형제배우자, 부모자녀, 요금, 탑승항구). 숫자형 열 이름 리스트를 numeric_columns, 문자(범주형) 열 이름 리스트를 category_columns에 담고 출력. select_dtypes 써.
""", """
- `숫자형` / `범주형` → 다음 단원에서 다르게 손질할 두 종류.
- `select_dtypes` → 자료형으로 열을 가르는 메서드.
"""),
    "get-dummies": p("""
pandas. titanic DataFrame. pd.get_dummies(titanic[['성별']])로 성별 열을 One-hot 인코딩해 encoded에 담고 마지막 줄에 encoded.head(). 성별_여성, 성별_남성 두 열이 나와야 해.
""", """
- `One-hot 인코딩` → 글자 열을 0/1 열로 바꾸는 표준 용어. `map({'남성':0})` 같은 임의 코드를 막는다.
"""),
    # ----
    "stratified-split": p("""
scikit-learn. X, y가 있어. train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)로 X_train, X_test, y_train, y_test 만들고 두 쪽 행 수와 y 평균(생존 비율) 출력.
""", """
- `stratify=y` → 두 쪽의 생존 비율을 같게(층화 분할).
- `random_state=42` → 누가 돌려도 같은 분할(재현성). 둘 다 AI가 잘 빼먹는다.
"""),
    "first-model": p("""
scikit-learn. X_train, X_test, y_train, y_test가 있어. simple = ['객실등급','형제배우자','부모자녀'] 세 열만 써서 LogisticRegression(max_iter=1000)을 model에 만들고 fit. X_test[simple] 예측의 accuracy_score를 accuracy에 담고 출력.
""", """
- `세 열만` → 빈칸 없는 숫자 열만 골라 손질 없이 돌리는 의도.
- `fit → predict → accuracy_score` → 모델 프롬프트의 기본 골격.
"""),
    "train-imputer": p("""
scikit-learn. X_train, X_test가 있어. SimpleImputer(strategy='median')를 imputer에 만들고, X_train[['나이','요금']]에 fit_transform한 결과를 train_values, X_test[['나이','요금']]에 transform한 결과를 test_values에. 둘의 shape 출력.
""", """
- 훈련은 `fit_transform`, 테스트는 `transform` → 중앙값은 훈련 자료에서만 정한다. 둘 다 fit하면 누수.
"""),
    "onehot-fit": p("""
scikit-learn. X_train, X_test가 있어. OneHotEncoder(handle_unknown='ignore', sparse_output=False)를 encoder에 만들고 X_train[['성별']]에 fit_transform → train_encoded, X_test[['성별']]에 transform → test_encoded. shape 출력.
""", """
- `handle_unknown='ignore'` → 테스트에 처음 보는 값이 와도 오류 대신 0.
- `sparse_output=False` → 일반 배열로 받기.
"""),
    "pipeline-build": p("""
scikit-learn. X_train, X_test가 있고 numeric = ['객실등급','나이','형제배우자','부모자녀','요금']. Pipeline([('fill', SimpleImputer(strategy='median')), ('scale', StandardScaler())])를 numeric_pipeline에 만들고, X_train[numeric]에 fit_transform → train_values, X_test[numeric]에 transform → test_values. shape 출력.
""", """
- `Pipeline([...])` → 채우기와 표준화를 한 객체로. 단계가 늘면 순서가 꼬이니 묶는다.
- `'fill'`, `'scale'` → 단계 이름. 나중에 이 이름으로 꺼낸다.
"""),
    # ----
    "dummy-only": p("""
scikit-learn. X_train, X_test, y_train, y_test가 있어. DummyClassifier(strategy='most_frequent')를 dummy에 만들어 fit하고 X_test 예측의 accuracy_score를 dummy_accuracy에 담아 출력.
""", """
- `DummyClassifier(strategy='most_frequent')` → 기준 모델(baseline). 모델보다 먼저 "찍기 점수"를 잰다.
"""),
    "model-comparison": p("""
scikit-learn. X_train, X_test, y_train, y_test와 make_preprocessor()가 있어. models = {'Dummy': DummyClassifier(strategy='most_frequent'), 'Logistic': LogisticRegression(max_iter=2000), 'Tree': DecisionTreeClassifier(max_depth=5, random_state=42), 'Forest': RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42)}.
각각 Pipeline([('prepare', make_preprocessor()), ('model', m)])로 fit/predict해서 accuracy_score와 f1_score를 구하고, 모델 이름을 인덱스로 accuracy, f1 두 열인 DataFrame results를 만들어.
""", """
- 같은 `Pipeline`, 같은 분할, 같은 지표 → 공정한 비교. Dummy가 표의 첫 행.
- `max_depth=5` → Tree와 Forest를 같은 조건으로. 깊이는 재현성이 아니라 공정한 비교 조건.
- `random_state=42` → 재현성. 누가 돌려도 같은 표.
"""),
    "train-vs-test": p("""
scikit-learn. X_train, X_test, y_train, y_test, make_preprocessor()가 있어. Pipeline([('prepare', make_preprocessor()), ('model', DecisionTreeClassifier(random_state=42))])를 model에 fit하고, 훈련 자료 정확도를 train_accuracy, 테스트 자료 정확도를 test_accuracy에 담아 둘 다 출력.
""", """
- 훈련 정확도와 테스트 정확도를 둘 다 → 과적합을 잡는 방법.
- `max_depth` 없음 → 일부러 제한 없는 트리. 두 점수가 벌어지는 걸 본다.
"""),
    "save-and-load": p("""
scikit-learn. X_train, X_test, y_train, y_test, 손질기 make_preprocessor()가 있어. make_preprocessor()와 LogisticRegression(max_iter=1000)을 Pipeline으로 묶어 model에 fit.
joblib.dump로 titanic_model.joblib에 저장하고 joblib.load로 loaded에 불러와
테스트 정확도를 test_accuracy에 담아 출력. 불러온 뒤에 다시 훈련하지 마
""", """
- `joblib.dump`, `joblib.load` → 저장 도구를 정해 준다. 안 정하면 pickle이 올 수도 있다.
- `Pipeline으로 묶어` → 손질 기준까지 파일에 들어가게.
- `다시 훈련하지 마` → 불러온 모델로 predict만 하는 코드를 받는다.
"""),
    "tune-depth": p("""
scikit-learn. X_train, X_test, y_train, y_test, make_preprocessor()가 있어. depths = [2, 3, 5, 8, 12] 후보마다 make_preprocessor()와 DecisionTreeClassifier(max_depth=깊이, random_state=42)를 Pipeline으로 묶고
cross_val_score(cv=5) 평균을 cv_scores 딕셔너리에. 최고 깊이를 best_depth에 고르고 그 깊이로 다시 fit한 model의 테스트 정확도를 test_accuracy에 출력.
테스트 자료는 깊이 고르는 데 쓰지 마
""", """
- `cross_val_score(cv=5)` → 훈련 자료 안에서 고르게 한다. 안 쓰면 테스트로 고르는 코드가 온다.
- `random_state=42` → 후보마다 같은 조건.
- `테스트 자료는 … 쓰지 마` → 튜닝과 채점을 분리한다.
"""),
    # ----
    "credit-shape": p("""
pandas. credit = pd.read_csv('data/credit.csv'), target = '다음달 부도'. 행 수 n_rows, 열 수 n_columns에 담고, credit[target].value_counts()를 target_counts에 담아 출력.
""", """
- `target = '...'` → 열 이름에 공백이 있어 변수에 담아 둠. 말로 풀면 AI가 밑줄로 바꾼다.
"""),
    "default-summary": p("""
pandas. credit DataFrame, target = '다음달 부도'. 부도(1) 인원을 default_count, 부도율(타깃 평균)을 default_rate에 담고, 고객번호와 target 열을 drop한 입력 표를 X에 만들어. 셋 다 출력.
""", """
- `고객번호 … drop` → 고객 번호는 그냥 번호 열. 넣으면 모델이 번호를 외운다.
- `부도율(타깃 평균)` → 0/1 평균 = 비율.
"""),
    "limit-by-default": p("""
pandas. credit DataFrame, target 변수에 타깃 열 이름. target으로 groupby한 신용한도의 mean을 limit_by_default에 담고 출력.
""", """
- `target으로 groupby한 신용한도의 mean` → 타깃으로 묶어 입력 열 평균 비교. 열의 관련성을 보는 가장 빠른 길.
"""),
    "delay-groups": p("""
pandas. credit DataFrame, target, pay_columns = ['상환_9월','상환_8월','상환_7월','상환_6월','상환_5월','상환_4월']. (credit[pay_columns] >= 1).any(axis=1)을 credit['has_delay']에 넣고, has_delay로 groupby한 target의 agg(['count','sum','mean'])을 summary에.
""", """
- `(… >= 1).any(axis=1)` → "여섯 열 중 하나라도"를 한 줄로. 말로 풀면 반복문이 나온다.
"""),
    "pay0-rate": p("""
pandas. credit DataFrame, target. 상환_9월로 groupby한 target의 agg(['count','mean'])을 pay0_summary에 담고, 상태 0의 부도율을 rate_0, 상태 2의 부도율을 rate_2에 담아 출력.
""", """
- `count`도 같이 → 인원 적은 상태의 비율은 못 믿는다.
- `상태 0의 부도율` → 집계표에서 특정 행 꺼내기(`.loc[0, 'mean']`).
"""),
    # ----
    "manual-metrics": p("""
파이썬. tp, fp, fn, tn = 2, 1, 1, 2. precision = tp/(tp+fp), recall = tp/(tp+fn), accuracy = (tp+tn)/(tp+fp+fn+tn) 계산해서 세 변수에 담고 출력.
""", """
- 공식을 그대로 → 정의를 아는 사람의 프롬프트. AI는 계산만.
- `tp, fp, fn, tn` → 혼동행렬 네 칸의 공통 언어.
"""),
    "metrics-matrix": p("""
scikit-learn. y_true=[0,0,1,1,1,0], y_pred=[0,1,1,0,1,0]. accuracy_score, precision_score, recall_score, f1_score를 같은 이름 키('accuracy','precision','recall','f1')로 metrics 딕셔너리에 담고, confusion_matrix(y_true, y_pred, labels=[0,1])를 matrix에. 둘 다 출력.
""", """
- `(y_true, y_pred)` → 인자 순서. 바꾸면 값이 달라진다.
- `labels=[0,1]` → 혼동행렬 칸 위치 고정.
"""),
    "credit-model": p("""
scikit-learn. X_train, X_test, y_train, y_test가 있어(입력 상환_9월, 신용한도, 나이). models = {'Dummy': DummyClassifier(strategy='most_frequent'), 'Logistic': LogisticRegression(max_iter=1000)}. 각각 Pipeline([('scale', StandardScaler()), ('model', m)])로 fit/predict해서 accuracy, precision, recall, f1 네 지표를 구하고 모델 이름을 인덱스로 한 DataFrame results를 만들어. precision은 zero_division=0.
""", """
- 네 지표 함께 → 불균형 자료에서 accuracy만 보면 속는다.
- `zero_division=0` → Dummy는 부도를 안 찍어 0으로 나누기가 난다. 미리 처리.
"""),
    "predict-proba": p("""
scikit-learn. 학습된 Pipeline model과 X_test가 있어. model.predict_proba(X_test)[:, 1]을 probabilities에 담고, 0.5 이상인 개수를 n_positive_05, 0.3 이상인 개수를 n_positive_03에 int로 담아 출력.
""", """
- `predict_proba(...)[:, 1]` → 부도일 확률 열. `[:, 1]` 없으면 두 열.
- `0.5`, `0.3` → 기준값은 모델이 아니라 사람이 정한다.
"""),
    "thresholds": p("""
numpy. probabilities = np.array([0.1,0.35,0.49,0.51,0.8]). 0.5 이상이면 1 아니면 0인 정수 배열을 pred_05, 0.3 이상이면 1인 배열을 pred_03에 담고 각각 1의 개수 출력. (probabilities >= 0.5).astype(int) 식으로.
""", """
- `(probabilities >= 0.5).astype(int)` → 기준값을 배열 전체에 한 번에 적용. 반복문 없이 한 줄. `int`까지 맞춰야 채점 통과.
"""),
    # ----
    "stock-load": p("""
pandas. data/stock.csv를 parse_dates=['날짜']로 읽고 set_index('날짜').sort_index()해서 prices에. 행·열 수를 n_rows, n_columns에 담고, 첫 날짜와 마지막 날짜 출력.
""", """
- `parse_dates` → 글자를 날짜로.
- `set_index('날짜').sort_index()` → 날짜 인덱스 + 정렬. 빠지면 뒤의 shift/rolling이 엉킨다.
"""),
    "close-plot": p("""
pandas + matplotlib. prices(날짜 인덱스, 종가 열)가 있어. fig, ax = plt.subplots() 뒤 ax.plot(prices.index, prices['종가']). xlabel '날짜', ylabel '종가'. plt.show().
""", """
- `ax.plot` → 시간 자료는 선그래프. x축은 날짜 인덱스.
"""),
    "price-range": p("""
pandas. prices(날짜 인덱스, 종가 열). 첫 날짜 first_date, 마지막 날짜 last_date, 최고 종가 max_close, 그 날짜 max_date에 담고 전부 출력. 날짜는 index.min()/max(), 최고 종가 날짜는 idxmax().
""", """
- `idxmax()` → 최댓값이 "언제"인지. 모르면 정렬해서 첫 행 꺼내는 긴 코드가 온다.
"""),
    # ----
    "daily-return": p("""
pandas. prices(날짜 인덱스, 종가 열). prices['종가'].pct_change()를 return_1 열로 추가하고 prices.head() 출력.
""", """
- `pct_change()` → 일별 수익률 한 줄. 말로 풀면 `diff()/shift()`가 나온다.
"""),
    "moving-average": p("""
pandas. prices(날짜 인덱스, 종가 열). prices['종가'].rolling(5).mean()을 ma5 열로 추가하고 prices.head(6) 출력.
""", """
- `rolling(5).mean()` → 5거래일 이동평균. 창 크기는 숫자로.
"""),
    "lag-next": p("""
pandas. prices(날짜 인덱스, 종가 열). prices['종가'].shift(1)을 lag_close_1 열로, shift(-1)을 target_next_close 열로 추가.
""", """
- `shift(1)` 어제, `shift(-1)` 내일 → 부호를 틀리면 과거·미래가 바뀌어 누수.
"""),
    "stock-frame": p("""
pandas. prices(날짜 인덱스, 종가 열)와 빈 frame=pd.DataFrame(index=prices.index)가 있어. frame에 close(종가), return_1(pct_change), ma5(rolling(5).mean()), lag_close_1(shift(1)), target_next_close(shift(-1)), target_date(pd.Series(prices.index, index=prices.index).shift(-1)) 여섯 열을 만들고 frame = frame.dropna().copy(). 396행이어야 해.
""", """
- `target_date` → 정답 날짜를 남겨 둔다. 다음 단원의 경계 누수를 막기 위해.
- `dropna()` → 불완전한 행 제거. `396행` → 검산.
"""),
    # ----
    "test-start": p("""
pandas. frame(날짜 인덱스, 396행)이 있어. 마지막 80행의 첫 날짜를 test_start에 담고, 인덱스가 test_start 이상인 행 수를 int로 n_test에 담아 출력. frame.index[-80] 써.
""", """
- `frame.index[-80]` → "마지막 80거래일을 테스트로"를 코드로. `n_test == 80` 검산.
"""),
    "time-boundary": p("""
pandas. frame(날짜 인덱스, 열 close, return_1, ma5, lag_close_1, target_next_close, target_date). test_start = frame.index[-80].
입력 날짜와 target_date가 둘 다 test_start 전인 행을 train_mask, 입력 날짜가 test_start 이상인 행을 test_mask로.
feature_columns=['close','return_1','ma5','lag_close_1']로 X_train, X_test, y_train(target_next_close), y_test 만들어.
두 쪽 행 수 출력(훈련 315, 테스트 80).
""", """
- `target_date도 test_start 전` → 이 조건이 없으면 테스트 첫날 정답을 훈련에서 본다(경계 누수). AI는 거의 항상 빼먹는다.
- `훈련 315, 테스트 80` → 검산.
"""),
    "manual-mae": p("""
pandas. X_test(close 열)와 y_test가 있어. "내일 종가 = 오늘 종가" 기준 예측의 오차 (y_test - X_test['close']).abs()를 errors에, 그 평균을 manual_mae에 담아 출력.
""", """
- `(y_test - X_test['close']).abs()` 평균 → MAE의 정의를 코드로. 함수 전에 손으로.
- `내일 종가 = 오늘 종가` → 순진한 기준(naive) 예측. 가장 단순한 기준 모델.
"""),
    "close-baseline": p("""
scikit-learn. X_test(close 열), y_test. 기준 예측 X_test['close'].to_numpy()를 baseline_pred에, mean_absolute_error(y_test, baseline_pred)를 baseline_mae에 담아 출력.
""", """
- `mean_absolute_error(정답, 예측)` → 인자 순서.
- `baseline_mae` → 이후 모든 모델이 넘어야 할 선.
"""),
    "callcenter-baseline": p("""
pandas + scikit-learn. calls DataFrame(열 week 1/2, weekday 월~일, calls). 1주차 calls를 배열 last_week, 2주차 calls를 this_week에 담고, mean_absolute_error(this_week, last_week)를 baseline_mae에, 월요일 오차 abs(this_week[0]-last_week[0])를 monday_error에 담아 출력.
""", """
- `mean_absolute_error(this_week, last_week)` → 정답(이번 주), 예측(지난주). "지난주와 같다"가 기준 모델.
"""),
    # ----
    "linear-only": p("""
scikit-learn. X_train, X_test, y_train, y_test가 있어(temporal split 완료). Pipeline([('scale', StandardScaler()), ('model', LinearRegression())])를 model에 fit. 테스트 예측을 prediction, mean_absolute_error를 linear_mae에 담아 출력하고 model.named_steps['model'].coef_도 출력.
""", """
- `temporal split 완료` → 다시 섞지 말라는 뜻.
- `StandardScaler` + `Pipeline` → 표준화 뒤 회귀. 계수를 비교하려면 필수.
- `named_steps['model'].coef_` → 단계 이름으로 계수 꺼내기.
"""),
    "regression-table": p("""
scikit-learn. X_train, X_test, y_train, y_test(temporal split).
models = {'Linear': LinearRegression(), 'Ridge': Ridge(alpha=1), 'Lasso': Lasso(alpha=10, max_iter=20000, tol=0.001)}.
각각 StandardScaler와 Pipeline으로 fit해서 fitted 딕셔너리에 보관하고 테스트 예측을 predictions 딕셔너리에 모아.
predictions['Baseline']은 X_test['close'] 값.
네 예측 각각 MAE, RMSE, R2를 구해 인덱스가 모델 이름이고 열이 MAE, RMSE, R2인 DataFrame results를 만들어. RMSE는 mean_squared_error의 제곱근.
""", """
- `predictions['Baseline']` → 기준 예측을 표의 한 행으로.
- `RMSE는 mean_squared_error의 제곱근` → 정의를 적어 다른 공식을 막는다.
- `alpha=…` → 브레이크 세기. 숫자를 정해 줘야 누가 돌려도 같은 표가 나온다.
"""),
    "beat-baseline": p("""
scikit-learn. X_train, X_test, y_train, y_test(temporal split). 기준 예측 X_test['close']의 MAE를 baseline_mae, Pipeline(StandardScaler, Ridge(alpha=1))의 테스트 MAE를 ridge_mae에 담고, improved = ridge_mae < baseline_mae. 셋 다 출력. improved가 False여도 그대로 둬.
""", """
- `False여도 그대로 둬` → "개선"을 요구하면 AI는 기간이나 하이퍼파라미터를 바꿔 이기는 결과를 만든다. 정직한 비교.
"""),
    "forecast-plot": p("""
scikit-learn + matplotlib. frame, X_train, X_test, y_train, y_test, test_mask(temporal split). Pipeline(StandardScaler, Ridge(alpha=1))을 fit해 prediction을 구하고, frame.loc[test_mask, 'target_date']를 인덱스로 actual(y_test 값)과 prediction 두 열인 comparison DataFrame을 만들어. fig, ax에 두 선을 그리고 xlabel '정답 날짜', 범례 표시, plt.show().
""", """
- `target_date를 인덱스로` → x축은 정답 날짜. 입력 날짜로 그리면 예측이 하루 앞당겨 보인다.
"""),
    "final-report": p("""
scikit-learn. X_train, X_test, y_train, y_test(temporal split, 테스트 80거래일), models = {'Linear': ..., 'Ridge': ...}가 있어. 각 모델을 StandardScaler Pipeline으로 fit해 테스트 MAE를 maes 딕셔너리에 모으고, 기준(X_test['close']) MAE와 비교해 report 딕셔너리를 만들어. 키: test_days, baseline_mae, best_model(MAE 최소 모델 이름), best_mae, improved(best_mae < baseline_mae). 결론 세 줄 출력: ① 무엇을 언제 예측했고 어떻게 나눴는지 ② 기준 MAE와 최선 MAE ③ 개선 여부. improved가 False면 그대로 적어.
""", """
- `report` 다섯 키 → 보고서의 구조를 프롬프트에. 무엇을·언제·어떻게 나눠·기준 대비·개선 여부.
- `False면 그대로 적어` → 못 했으면 못 했다고.
"""),
    "rate-by-attribute": p("""
pandas. credit 표에서 '다음달 부도' 평균을 '성별'로, '학력'으로 각각 groupby해서 rate_by_sex, rate_by_education에.
'나이'는 pd.cut(bins=[20,30,40,50,60,80], right=False, labels=['20대','30대','40대','50대','60대 이상'])로 '나이대' 열을 만들고
observed=True로 groupby한 평균을 rate_by_age에. 셋 다 출력.
""", """
- `평균` → 0/1 타깃의 평균이 곧 부도율. 비율을 따로 계산하지 않게 한다.
- `bins, right=False, labels` → 구간의 경계와 이름을 지정하지 않으면 AI가 임의로 자른다.
- `observed=True` → 범주형으로 묶을 때 비어 있는 구간을 빼고 경고를 막는다.
"""),
    "live-crawl": p("""
파이썬. requests로 https://en.wikipedia.org/wiki/KOSPI 를 받고(User-Agent 헤더, timeout 10) BeautifulSoup으로 읽어.
wikitable 중 'Closing level'이 든 표에서 행마다 td 글자를 뽑아 연도(int), 종가(쉼표 제거 float), 변화율(넷째 칸, '−'를 '-'로, float) 열의 kospi 표.
칸이 4개 미만이거나 변화율이 빈 행은 제외. 변화율 최대인 연도를 best_year, 변화율>0인 해의 수를 up_years에.
""", """
- `User-Agent 헤더` → 없으면 거절하는 사이트가 있다.
- `'Closing level'이 든 표` → 페이지에 wikitable이 여럿이라 고르는 기준을 줘야 한다.
- `'−'를 '-'로` → 위키의 음수 기호는 유니코드라 float()이 실패한다. 이걸 모르면 AI 코드도 깨진다.
- `빈 행은 제외` → 첫해는 등락률이 없다.
"""),
    "live-prices": p("""
파이썬. FinanceDataReader로 삼성전자 005930을 2026-01-01부터 받아 날짜순 정렬한 live.
마지막 Close를 int로 latest_close, Close의 5일 rolling 평균 마지막 값을 ma5에. tail과 마지막 날짜, 두 값 출력.
""", """
- `FinanceDataReader` → 국내 종목 코드를 그대로 쓰는 쪽. yfinance면 '005930.KS'와 multi_level_index=False가 필요하다.
- `날짜순 정렬` → 받은 순서를 믿지 않는다. 시간 자료의 첫 습관.
- `5일 rolling 평균` → 뒤 단원에서 입력으로 쓰는 ma5와 같은 계산이다.
"""),
}
