"""조건 필터와 결측"""
from kpc_course.dsl import *

UNIT = unit('missing', '조건 필터와 결측', [
    concept('missing-values', '빈칸은 0이 아니다',
        body="""
        자, 앞 단원의 `orders` 표에는 가격이 비어 있는 거래가 한 건 있었죠? 설문지를 떠올려 보세요. 어떤 사람이 나이 칸을 비워 뒀어요. 그 사람의 나이는 0살일까요? 아니에요. **모른다**가 정답이에요. 표에서 비어 있는 칸을 결측(missing)이라고 불러요. `pandas`는 그 자리에 `NaN`이라고 표시하고요. 결측과 0을 섞으면 평균이 엉뚱하게 내려가요. 그 평균으로 한 계산도 전부 같이 틀어지고요.

        ```comic-gen
        제목: 빈칸은 0이 아니다
        등장인물:
          준호:
            그림: 사람
            이름표: 준호 · 은행 직원
            외형: {머리색: "#303746", 옷색: "#b88646"}
          강사:
            그림: 사람
            이름표: 강사
            외형: {옷: 재킷, 옷색: "#5379a7", 안경: true}
        컷:
          - 인물: [준호, 강사]
            대사:
              - {화자: 준호, 상대: 강사, 내용: "나이 칸이 비었으면 0으로 채울까요?"}
              - {화자: 강사, 상대: 준호, 내용: "그러면 0살 고객이 생깁니다."}
          - 구성: 이전
            인물: [{식별자: 준호, 표정: 어리둥절}, {식별자: 강사, 손모양: 가리키는손}]
            대사:
              - {화자: 준호, 상대: 강사, 내용: "평균 나이가 확 내려가겠네요."}
              - 화자: 강사
                상대: 준호
                내용: |-
                  빈칸은 '모른다'로 두고
                  먼저 몇 개인지 세어 보죠.
        ```

        그러니 분석을 시작하기 전에 어디가 얼마나 비어 있는지부터 세어 보세요. `isna()`는 빈칸을 `True`로 표시한 표를 돌려줘요. 거기에 `.sum()`을 붙이면 열마다 `True`의 개수가 나와요. 그게 결측 개수예요.

        ```python
        orders.isna().sum()  # 열마다 빈 칸 개수
        filled = orders['price'].fillna(12000)  # 빈 칸을 12000으로 채운 새 열
        dropped = orders.dropna(subset=['price'])  # 가격이 빈 행을 뺀 새 표
        ```

        비어 있는 칸을 다루는 길은 두 가지뿐이에요. 어떤 값으로 **채우거나**(`fillna`), 그 행을 **빼거나**(`dropna`). 무엇을 채울지는 사람이 정해요. 흔한 선택은 그 열의 중앙값이에요. 값들을 크기순으로 세웠을 때 한가운데 값이죠. 어느 쪽이 옳은지는 상황마다 달라요. 두 선택의 결과가 얼마나 달라지는지는 이 단원 마지막 미션에서 직접 봐요.

        하나 조심할 게 있어요. `fillna`와 `dropna`는 **새 표를 돌려줄 뿐 원본은 그대로**예요. 바꾼 결과를 쓰려면 변수에 받아 둬야 해요.

        ```comic-gen
        제목: 빈칸을 0으로 넣으면
        등장인물:
          공장장:
            그림: 사람
            이름표: 빵 공장장
            외형: {피부색: "#d6a279", 머리모양: 민머리, 옷색: "#8a6d4b"}
          강사:
            그림: 사람
            이름표: 강사
            외형: {옷: 재킷, 옷색: "#5379a7", 안경: true}
        컷:
          - 인물: [{식별자: 공장장, 표정: 보통}, 강사]
            대사:
              - {화자: 공장장, 상대: 강사, 내용: "지난 화요일 판매량을 안 적었어요. 0으로 넣을게요."}
              - {화자: 강사, 상대: 공장장, 내용: "그러면 화요일에 한 개도 못 판 날이 돼요. 평균이 확 내려가요."}
          - 구성: 이전
            인물: [{식별자: 공장장, 표정: 기쁨}, {식별자: 강사, 손모양: 가리키는손}]
            대사:
              - {화자: 강사, 상대: 공장장, 내용: "모르면 모른다고 두고, 중앙값으로 채우거나 그 날을 빼세요."}
              - {화자: 공장장, 상대: 강사, 내용: "빈칸은 0이 아니라 모름. 알겠어요."}
        ```

        조건으로 행 고르기도 한 단계 더 나아가요. 앞 단원에서는 조건이 하나였죠? "가격이 12000 이상**이고** 수량이 2 이상"처럼 둘을 합칠 때가 있어요. 그러면 각 조건을 괄호로 감싸고 `&`(그리고)로 이어요. "제품이 A**이거나** 수량이 1"은 `|`(또는)이고요. 괄호를 빼면 파이썬이 계산 순서를 다르게 읽어 오류가 나요.

        ```python
        both = orders.loc[(orders['price'] >= 12000) & (orders['quantity'] >= 2)]
        either = orders.loc[(orders['product'] == 'A') | (orders['quantity'] == 1)]
        ```
        """,
        check=short('표에서 값이 비어 있는 칸을 가리키는 말은 무엇인가요?', ['결측', '결측치', '결측값', 'missing', 'missing value', 'NaN'],
                    '비어 있는 칸은 결측(missing)이에요. `pandas`는 `NaN`으로 표시해요. 0은 "값이 0"이라는 정보예요. 결측은 "모른다"는 뜻이라 서로 달라요.')),
    coding('count-missing', '비어 있는 값 세기',
        goal="""
        `orders`에서 열마다 빈칸이 몇 개인지 세어 보세요. `orders.isna().sum()`의 결과를 `missing_counts`에 담으세요. 그중 `price` 열의 결측 개수는 정수로 `n_missing_price`에 담고요. 둘 다 출력하세요.

        가격 열에만 1개가 비어 있으면 맞게 센 거예요.
        """,
        hint="""
        `orders.isna()`는 빈칸을 `True`로 표시해요. `.sum()`은 열마다 `True`를 세고요. 결과는 열 이름으로 꺼내는 `Series`예요. `missing_counts['price']`로 가격 열 값을 꺼내세요. 그걸 `int()`로 감싸고요.
        """,
        starter=ORDERS + "# missing_counts, n_missing_price를 만들고 출력하세요\n",
        solution=ORDERS + "missing_counts = orders.isna().sum()\nn_missing_price = int(missing_counts['price'])\nprint(missing_counts)\nprint(n_missing_price)\n",
        check="assert s['missing_counts']['price'] == 1 and s['missing_counts']['product'] == 0\nassert s['n_missing_price'] == 1"),
    coding('fill-median', '결측을 중앙값으로 채우기',
        goal="""
        첫 번째 길, 채우기예요. `orders['price']`의 중앙값을 `median_price`에 담으세요. 빈칸을 그 값으로 채운 열은 `filled_price`에 담고요. 둘 다 출력하세요. 원본 `orders`는 건드리지 마세요.

        중앙값이 12000이면 맞아요. 채운 열은 10000, 20000, 12000, 12000이 나와야 하고요.
        """,
        hint="""
        `orders['price'].median()`은 빈칸을 빼고 중앙값을 구해요. `orders['price'].fillna(median_price)`는 **새** 열을 돌려줘요. 빈칸만 그 값으로 바꾼 열이죠. 원본은 그대로예요. 그래서 변수에 받아야 해요.
        """,
        starter=ORDERS + "# median_price, filled_price를 만들고 출력하세요\n",
        solution=ORDERS + "median_price = orders['price'].median()\nfilled_price = orders['price'].fillna(median_price)\nprint(median_price)\nprint(filled_price)\n",
        check="assert s['median_price'] == 12000\nassert s['filled_price'].tolist() == [10000, 20000, 12000, 12000]\nassert s['orders']['price'].isna().sum() == 1"),
    coding('drop-missing', '결측 행 제외하기',
        goal="""
        두 번째 길, 빼기예요. 가격이 빈 행을 뺀 표를 `dropped`에 담으세요. 남은 행 수는 `n_left`에 담아 출력하세요. 마지막 줄에 `dropped`를 적어 표도 확인하세요.

        3행이 남으면 맞게 한 거예요.
        """,
        hint="""
        `orders.dropna(subset=['price'])`는 `price`가 빈 행만 빼요. `subset`을 빼고 `orders.dropna()`라고 쓰면요? 어느 열이든 빈 행을 전부 빼요. 이 표에서는 결과가 같아요. 열이 많은 표에서는 크게 달라지고요.
        """,
        starter=ORDERS + "# dropped, n_left를 만들고 출력하세요\n",
        solution=ORDERS + "dropped = orders.dropna(subset=['price'])\nn_left = len(dropped)\nprint(n_left)\ndropped\n",
        check="assert len(s['dropped']) == 3 and s['n_left'] == 3\nassert s['dropped']['product'].tolist() == ['A', 'B', 'A']"),
    coding('filter-orders', '두 조건을 모두 만족하는 거래',
        goal="""
        가격이 12000 이상**이고** 수량도 2 이상인 거래만 고르세요. 결과는 `selected`에 담고요. 열은 `product`, `price`, `quantity` 세 개를 그대로 두세요. 뒤에서 고쳐도 원본이 안 바뀌게 `.copy()`를 붙이세요.

        제품 B(수량 2)와 A(수량 4) 두 건이 남으면 맞게 한 거예요. 가격이 빈 C는 비교 자체가 안 돼서 빠져요.
        """,
        hint="""
        각 조건을 괄호로 감싸고 `&`로 이으세요. `loc`의 쉼표 뒤에 열 이름 리스트를 넣으면 행과 열을 한 번에 골라요. `orders.loc[조건, ['product', 'price', 'quantity']].copy()`처럼요.
        """,
        starter=ORDERS + "# selected를 만드세요\n",
        solution=ORDERS + "selected = orders.loc[(orders['price'] >= 12000) & (orders['quantity'] >= 2), ['product', 'price', 'quantity']].copy()\nselected\n",
        check="assert s['selected']['product'].tolist() == ['B', 'A'] and s['selected']['quantity'].tolist() == [2, 4]"),
    coding('or-filter', '둘 중 하나만 만족해도 고르기',
        goal="""
        이번에는 "또는"이에요. 제품이 A**이거나** 수량이 1인 거래를 `either`에 담으세요. 마지막 줄에 `either`를 적어 확인하세요.

        A, A, C 세 건이 남으면 맞게 한 거예요.
        """,
        hint="""
        `&`가 "그리고", `|`가 "또는"이에요. 조건마다 괄호를 꼭 치세요. `(orders['product'] == 'A') | (orders['quantity'] == 1)`처럼요. 괄호가 없으면 파이썬이 `'A' | orders['quantity']`를 먼저 계산하려고 해요. 그래서 오류가 나요.
        """,
        starter=ORDERS + "# either를 만들고 표를 표시하세요\n",
        solution=ORDERS + "either = orders.loc[(orders['product'] == 'A') | (orders['quantity'] == 1)]\neither\n",
        check="assert s['either']['product'].tolist() == ['A', 'A', 'C']"),
    coding('missing-totals', '채우기와 빼기, 합계는 얼마나 달라질까',
        goal="""
        두 길의 결과를 나란히 놓고 비교해요. `filled`는 가격 결측을 중앙값으로 채운 표예요. `dropped`는 가격이 빈 행을 뺀 표고요. 각 표에 가격 × 수량 열 `amount`를 만드세요. `filled`의 `amount` 합계는 `filled_total`에 담으세요. `dropped`의 `amount` 합계는 `dropped_total`에 담고요. 둘 다 출력하세요.

        두 합계가 서로 다르게 나와요. 어느 쪽도 "진짜 전체 금액"은 아니에요. 빈칸 하나를 어떻게 다루느냐에 따라 답이 달라지죠. 그래서 보고서에는 그 선택을 적어야 하고요. 이게 이 미션의 요점이에요.
        """,
        hint="""
        `filled = orders.copy()`를 먼저 만드세요. `filled['price'] = filled['price'].fillna(filled['price'].median())`로 채워요. 뺀 표는 `dropped = orders.dropna(subset=['price']).copy()`예요. 두 표 각각 `amount` 열을 가격 × 수량으로 만들어요. `filled['amount'] = filled['price'] * filled['quantity']`처럼요. 합계는 `filled['amount'].sum()`처럼 구해요.
        """,
        starter=ORDERS + "# 두 처리 방법과 합계를 비교하세요\n",
        solution=ORDERS + "filled = orders.copy()\nfilled['price'] = filled['price'].fillna(filled['price'].median())\nfilled['amount'] = filled['price'] * filled['quantity']\ndropped = orders.dropna(subset=['price']).copy()\ndropped['amount'] = dropped['price'] * dropped['quantity']\nfilled_total = filled['amount'].sum()\ndropped_total = dropped['amount'].sum()\nprint(filled_total, dropped_total)\nfilled\n",
        check="assert s['filled_total'] == 130000 and s['dropped_total'] == 118000\nassert len(s['filled']) == 4 and len(s['dropped']) == 3"),
    quiz('missing-check', '단원 점검',
        choice('가격이 비어 있는 칸을 0으로 채우면 무슨 일이 생기나요?',
               ['"모른다"는 정보가 "공짜였다"로 바뀌어 평균이 내려간다', '빈 칸이 사라져 더 정확해진다', '아무 영향이 없다'], 0,
               '0으로 채우면 없던 공짜 거래가 생긴 셈이라 평균과 합계가 왜곡돼요. 결측은 모른다는 뜻이고 0은 실제 값이거든요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「더 정확해진다」: 없는 값을 지어낸 거라 더 틀려져요.\n- 「아무 영향이 없다」: 평균과 합계가 함께 내려가요."),
        short('두 조건을 **모두** 만족하는 행을 고를 때 조건 사이에 넣는 기호는 무엇인가요?', ['&'],
              '`&`가 "그리고"예요. 조건마다 괄호로 감싸고 `&`로 이어요.'),
        short('두 조건 중 **하나만** 만족해도 고를 때 넣는 기호는 무엇인가요?', ['|'],
              '`|`가 "또는"이에요. 역시 조건마다 괄호가 필요해요.'),
        choice("`orders['price'].fillna(0)`을 실행한 뒤 `orders`를 출력하면 빈칸이 채워져 있을까요?",
               ['아니요. 새 열을 돌려줄 뿐 원본은 그대로다', '네. 원본이 바로 바뀐다', '첫 번째 빈 칸만 바뀐다'], 0,
               "`fillna`는 결과를 돌려주기만 해요. 원본은 그대로죠. 원본을 바꾸려면 다시 저장해야 해요. `orders['price'] = orders['price'].fillna(0)`처럼요." "\n\n**다른 보기는 왜 아닌가**\n\n- 「원본이 바로 바뀐다」: 돌려준 결과를 저장하지 않으면 사라져요.\n- 「첫 번째 빈 칸만」: 모든 빈칸을 채운 새 열을 돌려줘요."),
        choice("`orders.dropna()`와 `orders.dropna(subset=['price'])`의 차이는 무엇인가요?",
               ['앞은 어느 열이든 빈 행을 다 빼고, 뒤는 가격이 빈 행만 뺀다', '둘은 항상 같다', '앞은 열을 빼고 뒤는 행을 뺀다'], 0,
               '`subset`으로 기준 열을 정하지 않으면 모든 열을 검사해요. 열이 많은 표에서는 생각보다 많은 행이 사라질 수 있어요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「열을 빼고 행을 뺀다」: 둘 다 행을 빼요. 기준 열이 다를 뿐이에요.\n- 「항상 같다」: 다른 열에도 빈칸이 있으면 결과가 달라져요."),
        choice("`orders.loc[orders['price'] >= 12000 & orders['quantity'] >= 2]`처럼 괄호를 빼면 어떻게 되나요?",
               ['계산 순서가 달라져 오류가 난다', '괄호가 있을 때와 같다', '첫 조건만 적용된다'], 0,
               '계산 순서가 달라져 오류가 나요. 파이썬은 `&`를 `>=`보다 먼저 계산하거든요. 그래서 `12000 & orders[\'quantity\']`부터 시도하다 오류를 내요. 조건마다 괄호를 치세요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「괄호가 있을 때와 같다」: 연산 순서가 달라 오류가 나요.\n- 「첫 조건만 적용」: 적용되기 전에 오류가 나요."),
        choice("""**프롬프트 고르기** · `orders['price']`에 빈칸이 하나 있어요. 중앙값으로 채우되 원본은 그대로 둬야 해요. 어떤 프롬프트가 검사를 통과할까요?""",
               ["""pandas. orders['price']에 결측 1개. 중앙값을 median_price에, 결측을 중앙값으로 채운 열을 filled_price에 담아 출력. 원본 orders는 바꾸지 마. 코드만""", """빈 칸 채워 줘""", """orders의 결측을 중앙값으로 채워 줘. inplace로""", """결측치 처리하는 코드 줘"""], 0,
               """정답에는 어느 열을 어떤 값으로 채워 어디에 담을지가 있어요. "원본은 바꾸지 마"라는 제약까지 있고요. 검사기는 원본이 그대로인지도 봐요.

**다른 보기는 왜 아닌가**

- 「빈 칸 채워 줘」: 무엇으로 채울지, 어느 열인지 없어요.
- 「inplace로」: 원본이 바뀌어 검사에 실패해요.
- 「결측치 처리하는 코드」: 채우기인지 빼기인지조차 없어요."""),
        choice("""**프롬프트 고르기** · "가격 12000 이상이고 수량 2 이상"인 거래만 골라야 해요. 그런데 AI가 준 코드가 오류를 내요. 다시 부탁할 때 무엇을 적어야 할까요?""",
               ["""pandas. orders에서 price >= 12000 이고 quantity >= 2 인 행만 골라 selected에. 두 조건은 각각 괄호로 감싸 & 로 묶고 결과에 .copy(). 코드만""", """오류 나. 고쳐 줘""", """조건 두 개로 행 고르는 코드 줘. and 써서""", """가격이랑 수량 조건 걸어 줘"""], 0,
               """정답은 흔한 함정(괄호, &, copy)을 미리 적었어요. 아는 함정은 프롬프트에 적어야 같은 오류를 두 번 안 받아요.

**다른 보기는 왜 아닌가**

- 「오류 나. 고쳐 줘」: 오류 메시지도 코드도 없어요.
- 「and 써서」: pandas 조건에는 and가 아니라 &예요. 틀린 지시예요.
- 「조건 걸어 줘」: 경계값(이상)도 결과 변수도 없어요."""),
    ),
])
