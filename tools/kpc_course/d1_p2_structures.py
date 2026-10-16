"""변수와 자료구조"""
from kpc_course.dsl import *

HOLDINGS = "holdings = [{'name': 'A', 'price': 10000, 'quantity': 3}, {'name': 'B', 'price': 20000, 'quantity': 2}, {'name': 'C', 'price': 15000, 'quantity': 4}]\n"

UNIT = unit('structures', '변수와 자료구조', [
    concept('values', '값이 여러 개면 리스트, 이름표가 있으면 딕셔너리',
        body="""
        앞 단원에서는 값 하나에 이름 하나를 붙였어요. 그런데 어떤 주식의 사흘치 가격은요? `price1`, `price2`, `price3`을 따로 만들어야겠죠. 백 일치라면요? 그래서 값 여러 개를 **한 줄로 세워 한 이름에** 담는 방법이 있어요. 바로 리스트예요.

        ```comic-gen
        제목: 값 백 개에 이름 백 개?
        등장인물:
          민지:
            그림: 사람
            이름표: 민지
            외형: {머리모양: 단발, 머리색: "#573d36", 옷: 후드, 옷색: "#609b87"}
          파이썬: {그림: 서버, 이름표: Python}
        컷:
          - 인물: [{식별자: 민지, 표정: 어리둥절}, 파이썬]
            대사:
              - {화자: 민지, 상대: 파이썬, 내용: "백 일치 가격이면 변수가 백 개야?"}
              - {화자: 파이썬, 상대: 민지, 내용: "값들을 한 줄로 세워서 이름 하나에 담아. 그게 리스트야."}
          - 구성: 이전
            인물: [{식별자: 민지, 표정: 보통}, {식별자: 파이썬, 손모양: 가리키는손}]
            대사:
              - {화자: 민지, 상대: 파이썬, 내용: "첫 값은 어떻게 꺼내?"}
              - 화자: 파이썬
                상대: 민지
                내용: |-
                  prices[0]. 자리는 0부터 세고
                  마지막은 prices[-1].
        ```

        ```python
        prices = [10000, 10200, 10100]
        print(prices[0])  # 첫 값 10000
        print(prices[-1])  # 마지막 값 10100
        print(len(prices))  # 개수 3
        print(sum(prices))  # 합계 30300
        prices.append(10300)  # 맨 뒤에 값 추가
        ```

        리스트의 자리는 **0부터**예요. 첫 값이 `prices[0]`, 둘째가 `prices[1]`이에요. 뒤에서부터 세고 싶으면 음수를 써요. `prices[-1]`은 마지막 값이죠. 없는 자리를 부르면 파이썬은 `IndexError`라는 오류로 알려 줘요. `len`은 몇 개인지, `sum`은 다 더하면 얼마인지 돌려줘요. `append`는 맨 뒤에 값을 하나 붙이고요.

        리스트는 "몇 번째"로 값을 찾아요. 그런데 종목 하나는 이름, 가격, 수량처럼 **종류가 다른 값**이 한 묶음이죠? 이때는 자리 번호보다 "가격", "수량" 같은 이름표로 찾는 쪽이 자연스러워요. 그런 묶음이 딕셔너리예요.

        ```python
        holding = {'name': '연습A', 'price': 10000, 'quantity': 3}
        print(holding['price'])  # 10000
        holding['quantity'] = 5  # 값 바꾸기
        holding['amount'] = 50000  # 새 이름표 추가
        ```

        딕셔너리는 중괄호 안에 `'이름표': 값` 쌍을 쉼표로 늘어놓아요. 이름표는 **키**(key)라고 불러요. 꺼낼 때는 `holding['price']`처럼 대괄호 안에 키를 따옴표째 적어요. 키는 글자가 정확히 같아야 해요. `'Price'`와 `'price'`는 다른 키예요. 없는 키를 부르면 `KeyError`가 나요. 리스트는 **위치**로, 딕셔너리는 **키**로. 이것만 기억하면 뒤가 편해요.
        """,
        check=short('값마다 이름표(키)를 붙여 두고 그 이름표로 값을 찾는 자료구조는 무엇인가요?', ['dict', 'dictionary', '딕셔너리', '사전'],
                    '딕셔너리(dict)예요. 키로 값을 찾아요. 리스트는 0부터 세는 위치로 값을 찾고요.')),
    coding('list-index', '리스트에서 위치로 값 꺼내기',
        goal="""
        사흘치 가격이 `prices` 리스트에 들어 있어요. 첫날 가격을 `first`에 저장하세요. 마지막 날 가격은 `last`에 저장하세요. 그리고 둘을 출력하세요.

        첫 값 10000, 마지막 값 10100이 나오면 맞게 한 거예요.
        """,
        hint="""
        리스트의 자리는 0부터 시작해요. 첫 값은 `prices[0]`, 마지막 값은 `prices[-1]`이에요. `prices[3]`은 없는 자리라서 `IndexError`가 나요.
        """,
        starter='prices = [10000, 10200, 10100]\n# first, last를 만들고 출력하세요\n',
        solution='prices = [10000, 10200, 10100]\nfirst = prices[0]\nlast = prices[-1]\nprint(first, last)\n',
        check="assert s['first'] == 10000 and s['last'] == 10100"),
    coding('list-len-sum', '개수와 합계 구하기',
        goal="""
        같은 리스트로 "며칠치인가"와 "다 더하면 얼마인가"를 구해요. 개수를 `count`에 저장하세요. 합계는 `total`에 저장하세요. 그리고 둘을 출력하세요.

        개수 3, 합계 30300이 나오면 맞게 한 거예요.
        """,
        hint="""
        `len(prices)`가 개수, `sum(prices)`가 합계예요. 각각 변수에 담으세요. 그다음 `print(count, total)`로 한 줄에 출력하면 돼요.
        """,
        starter='prices = [10000, 10200, 10100]\n# count, total을 만들고 출력하세요\n',
        solution='prices = [10000, 10200, 10100]\ncount = len(prices)\ntotal = sum(prices)\nprint(count, total)\n',
        check="assert s['count'] == 3 and s['total'] == 30300"),
    coding('dict-read', '딕셔너리에서 키로 값 읽기',
        goal="""
        종목 하나가 `holding` 딕셔너리에 들어 있어요. 가격과 수량을 키로 꺼내 곱하세요. 그 금액을 `amount`에 저장하고 출력하세요. 딕셔너리 자체는 바꾸지 않아요.

        결과가 30000이면 맞게 한 거예요.
        """,
        hint="""
        값은 `holding['price']`처럼 꺼내요. 대괄호 안에 키를 따옴표째 적는 거예요. 따옴표를 빼고 `holding[price]`라고 쓰면요? 파이썬은 `price`라는 변수를 찾다가 `NameError`를 내요.
        """,
        starter="holding = {'name': '연습A', 'price': 10000, 'quantity': 3}\n# amount를 계산하고 출력하세요\n",
        solution="holding = {'name': '연습A', 'price': 10000, 'quantity': 3}\namount = holding['price'] * holding['quantity']\nprint(amount)\n",
        check="assert s['amount'] == 30000"),
    coding('holdings-access', '리스트 안의 딕셔너리',
        goal="""
        이제 두 가지를 합쳐요. `holdings`는 종목 딕셔너리 세 개를 순서대로 담은 리스트예요. 두 번째 종목의 이름을 `second_name`에 저장하세요. 세 번째 종목의 가격은 `third_price`에 저장하세요. 그리고 둘을 출력하세요.

        각각 `B`, 15000이 나오면 맞게 한 거예요.
        """,
        hint="""
        두 단계예요. 먼저 리스트에서 위치로 딕셔너리 하나를 꺼내요. 이어서 키로 값을 꺼내요. `holdings[1]['name']`처럼 대괄호를 두 번 붙이면 돼요. 두 번째 종목의 위치는 1, 세 번째는 2예요.
        """,
        starter=HOLDINGS + "# second_name, third_price를 만들고 출력하세요\n",
        solution=HOLDINGS + "second_name = holdings[1]['name']\nthird_price = holdings[2]['price']\nprint(second_name, third_price)\n",
        check="assert s['second_name'] == 'B' and s['third_price'] == 15000"),
    coding('holding', '값을 바꾸고 다시 계산하기',
        goal="""
        읽기만 했으니 이번에는 고쳐 볼게요. `holding`의 수량을 5로 바꾸세요. 그다음 바뀐 수량으로 가격 × 수량을 계산하세요. 그 값을 `amount`라는 **새 키**에 저장하세요.

        `holding['amount']`가 50000이면 맞게 한 거예요.
        """,
        hint="""
        `holding['quantity'] = 5`처럼 키에 새 값을 넣으면 바뀌어요. 없던 키에 넣으면 추가되고요. 수량을 바꾼 **다음에** 곱해야 50000이 나와요. 순서가 바뀌면 30000이 저장돼요.
        """,
        starter="holding = {'name': '연습A', 'price': 10000, 'quantity': 3}\n# 수량을 수정하고 금액을 계산하세요\n",
        solution="holding = {'name': '연습A', 'price': 10000, 'quantity': 3}\nholding['quantity'] = 5\nholding['amount'] = holding['price'] * holding['quantity']\nprint(holding)\n",
        check="assert s['holding']['quantity'] == 5 and s['holding']['amount'] == 50000"),
    coding('price-average', '값을 추가하고 평균 내기',
        goal="""
        넷째 날 가격 10300이 들어왔어요. `prices` 맨 뒤에 추가하세요. 그다음 개수를 `count`에 담으세요. 평균은 `average`에 담고요. 그리고 둘 다 출력하세요.

        개수 4, 평균 10150이 나오면 맞게 한 거예요.
        """,
        hint="""
        1. `prices.append(10300)`으로 맨 뒤에 값을 붙여요.
        2. 평균은 **합계 ÷ 개수**예요. 파이썬 기본 함수엔 `average()`가 없어요. `sum(prices) / count`로 직접 계산하세요.
        3. 나눗셈 `/`의 결과는 소수가 될 수 있어요. 10150.0으로 보여도 괜찮아요.
        """,
        starter='prices = [10000, 10200, 10100]\n# 값을 추가하고 count, average를 계산하세요\n',
        solution='prices = [10000, 10200, 10100]\nprices.append(10300)\ncount = len(prices)\naverage = sum(prices) / count\nprint(count, average)\n',
        check="assert s['prices'] == [10000, 10200, 10100, 10300] and s['count'] == 4 and s['average'] == 10150"),
    quiz('structure-check', '단원 점검',
        short('리스트에서 첫 번째 값의 자리 번호(인덱스)는 몇인가요?', ['0'],
              '0이에요. 파이썬의 자리 번호는 0부터 시작하거든요. 세 값이 든 리스트의 마지막 자리는 2예요.'),
        choice("""
               아래 코드를 위에서부터 실행했어요. 마지막 줄 `print(amount)`는 무엇을 출력할까요?

               ```python
               price = 10000
               quantity = 3
               amount = price * quantity
               quantity = 5
               print(amount)
               ```
               """,
               ['`30000`. 계산한 순간의 값이 그대로 남아 있다', '`50000`. 수량이 바뀌면 금액도 따라 바뀐다', '오류. 수량을 두 번 정할 수 없다'], 0,
               '`30000`이에요. `amount = price * quantity`는 그 순간의 30000을 넣어 둘 뿐이에요. "앞으로 계속 곱해라"는 약속이 아니에요. 수량을 바꾼 뒤 금액도 바꾸려면 곱셈 줄을 다시 실행해야 해요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「50000」: 변수는 공식이 아니라 값이에요. 나중에 수량을 바꿔도 따라 안 바뀌어요.\n- 「오류」: 같은 변수에 다시 넣는 건 자유예요."),
        short("""
              두 종목의 가격이 같은지 **비교**하려 해요. 결과가 `True`가 되도록 빈칸 `____`에 들어갈 연산자를 입력하세요.

              ```python
              price_a = 10000
              price_b = 10000
              print(price_a ____ price_b)
              ```
              """, ['=='],
              '`==`예요. 양쪽이 같은지 묻는 비교죠. `=` 하나는 "오른쪽 값을 왼쪽 이름(변수)에 넣어라"는 뜻이라 비교가 아니에요.'),
        choice('`prices = [10000, 10200, 10100]`이에요. `prices[3]`을 실행하면 결과는 무엇인가요?',
               ['`IndexError`. 자리 3은 없다', '`10100`이 나온다', '`None`이 나온다'], 0,
               '`IndexError`가 나요. 자리 번호는 0, 1, 2까지거든요. 세 번째 값이 필요하면 `prices[2]`, 마지막 값이면 `prices[-1]`이에요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「None」: 없는 자리는 조용히 비는 게 아니라 오류로 알려 줘요.\n- 「10100」: 그 값은 자리 2(또는 -1)에 있어요."),
        choice("`holding = {'price': 10000}`이에요. `holding['Price']`를 실행하면 결과는 무엇인가요?",
               ['`KeyError`. 키는 대소문자까지 똑같아야 한다', '`10000`이 나온다. 대소문자는 구분하지 않는다', '빈 값이 나온다'], 0,
               "`KeyError`가 나요. 딕셔너리의 키는 글자가 완전히 같아야 찾거든요. `'price'`와 `'Price'`는 서로 다른 키예요." "\n\n**다른 보기는 왜 아닌가**\n\n- 「10000이 나온다」: 대소문자가 다르면 다른 키예요.\n- 「빈 값」: 없는 키는 빈 값 대신 KeyError를 내요."),
        short('리스트 `prices`의 마지막 값을 뒤에서부터 세어 꺼내려면 대괄호 안에 무엇을 넣나요? (`prices[__]`)', ['-1'],
              '`-1`이에요. 뒤에서 첫 번째, 즉 마지막 값이죠. `-2`는 뒤에서 두 번째예요.'),
        choice("""**프롬프트 고르기** · `prices` 리스트에 값을 하나 추가하고 평균을 구해야 해요. 결과는 `average` 변수에 담아요. 기본 함수만 쓰는 연습이에요. 어떤 프롬프트가 맞을까요?""",
               ["""파이썬. prices = [10000, 10200, 10100]에 10300을 append하고 평균을 average에 담아 출력. 평균은 sum/len으로, 다른 라이브러리 없이. 코드만 줘""", """리스트 평균 구해 줘""", """numpy로 prices 평균 내는 코드 줘""", """prices에 값 넣고 평균 내 줘. 변수 이름은 알아서"""], 0,
               """정답엔 자료, 추가할 값, 결과 변수 이름이 다 있어요. "sum/len으로, 다른 라이브러리 없이"라는 제약까지 적었고요. 연습이 목적이면 방법까지 지정해야 원하는 코드를 받아요.

**다른 보기는 왜 아닌가**

- 「리스트 평균 구해 줘」: 어느 리스트인지, 결과를 어디 담는지 없어요.
- 「numpy로」: 이 미션은 기본 함수 연습이라 numpy는 어긋나요.
- 「변수 이름은 알아서」: 검사기는 average라는 이름으로 읽어요. 이름을 맡기면 실패해요."""),
        choice("""**프롬프트 고르기** · `holdings[1]['name']`이 왜 두 번째 종목의 이름인지 헷갈려요. AI에게 어떻게 물어야 개념이 정리될까요?""",
               ["""holdings = [{'name':'A',...},{'name':'B',...}] 에서 holdings[1]['name']이 'B'인 이유를 리스트 자리 번호와 딕셔너리 키로 나눠서 두 줄로 설명해 줘""", """이 코드 설명해 줘""", """holdings 두 번째 이름 뽑는 코드 줘""", """파이썬 리스트랑 딕셔너리 차이 알려 줘"""], 0,
               """정답은 실제 자료 모양과 코드를 보여 줘요. 설명도 "자리 번호"와 "키" 두 단계로 나눠 달라고 했고요. 답의 구조를 지정하면 이해가 빨라져요.

**다른 보기는 왜 아닌가**

- 「이 코드 설명해 줘」: 코드가 없어요. AI는 짐작으로 답해요.
- 「코드 줘」: 코드는 이미 있고 궁금한 건 이유예요.
- 「리스트랑 딕셔너리 차이」: 일반론만 돌아와요. 내 코드의 [1]['name']은 설명이 안 돼요."""),
    ),
])
