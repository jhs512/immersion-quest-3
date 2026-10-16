"""조건·반복과 표"""
from kpc_course.dsl import *

HOLDINGS = "holdings = [{'name': 'A', 'price': 10000, 'quantity': 3}, {'name': 'B', 'price': 20000, 'quantity': 2}, {'name': 'C', 'price': 15000, 'quantity': 4}]\n"
HOLDINGS_WITH_AMOUNT = "holdings = [{'name': 'A', 'price': 10000, 'quantity': 3, 'amount': 30000}, {'name': 'B', 'price': 20000, 'quantity': 2, 'amount': 40000}, {'name': 'C', 'price': 15000, 'quantity': 4, 'amount': 60000}]\n"

UNIT = unit('control', '조건·반복과 표', [
    concept('flow', '조건에 따라 고르고, 여러 값에 같은 일을 반복하기',
        body="""
        지금까지의 코드는 위에서 아래로 한 번 흘러가면 끝이었어요. 그런데 **경우에 따라 다르게** 하고 싶을 때가 있어요. "가격이 만 원 이상일 때만 알려 줘" 같은 거요. **같은 일을 여러 번** 하고 싶을 때도 있죠. "사흘치 가격을 하나씩 다 더해 줘"처럼요. 앞의 게 `if`, 뒤의 게 `for`예요.

        ```comic-gen
        제목: 고르기와 반복하기
        등장인물:
          준호:
            그림: 사람
            이름표: 준호 · 은행 직원
            외형: {머리색: "#303746", 옷색: "#b88646"}
          파이썬: {그림: 서버, 이름표: Python}
        컷:
          - 인물: [준호, 파이썬]
            대사:
              - {화자: 준호, 상대: 파이썬, 내용: "만 원 이상일 때만 알려 줘."}
              - {화자: 파이썬, 상대: 준호, 내용: "그게 if야. 조건에 맞을 때만 할게."}
          - 구성: 이전
            대사:
              - {화자: 준호, 상대: 파이썬, 내용: "사흘치 가격을 하나씩 다 더해 줘."}
              - {화자: 파이썬, 상대: 준호, 내용: "그게 for야. 값이 다 떨어질 때까지 하나씩 반복할게."}
          - 구성: 이전
            인물: [{식별자: 준호, 표정: 어리둥절}, {식별자: 파이썬, 표정: 어리둥절}]
            대사:
              - {화자: 준호, 상대: 파이썬, 내용: "들여쓰기는 왜 자꾸 틀렸다고 해?"}
              - 화자: 파이썬
                상대: 준호
                내용: |-
                  네 칸 들여쓴 줄만
                  if에 딸린 일로 알아듣거든.
        ```

        ```python
        price = 10200
        if price >= 10000:
            print('기준 이상')
        else:
            print('기준 미만')
        ```

        `if` 뒤에 조건을 쓰고 콜론 `:`을 찍어요. 다음 줄엔 **그 조건이 참일 때 할 일을 공백 네 칸 들여서** 적어요. 들여쓰기가 "이 줄은 `if`에 속한다"는 표시예요. 그래서 들여쓰기를 빼면 파이썬이 `IndentationError`를 내죠. 조건이 거짓일 때 할 일은 `else:` 아래에 적어요. 비교 기호도 정확히 봐야 해요. `>`는 초과(10000은 포함 안 됨), `>=`는 이상(10000도 포함)이에요.

        ```python
        prices = [10000, 10200, 9900, 10100]
        total = 0
        for price in prices:
            total += price
        print(total)
        ```

        `for price in prices:`는 이런 뜻이에요. "리스트의 값을 하나씩 꺼내 `price`라는 이름에 넣고, 아래 들여쓴 줄을 실행해라. 값이 떨어질 때까지." 네 값이 있으니 들여쓴 줄이 네 번 실행돼요. `total += price`는 `total = total + price`를 짧게 쓴 거예요. 지금까지의 합에 이번 값을 더해 다시 저장해요. 합계를 담을 `total = 0`은 반복이 시작되기 **전에** 한 번만 만들어야 해요. 반복 안에서 만들면 매번 0으로 돌아가서 마지막 값만 남아요.

        `for` 안에 `if`를 넣을 수도 있어요. 그러면 `if`에 속한 줄은 공백 여덟 칸이 돼요. 들여쓰기 깊이가 곧 "누구에게 속한 줄인가"를 나타내요.
        """,
        check=short("`if price >= 10000:` 아래에 속한 줄은 공백 몇 칸을 들여써야 하나요? 숫자로 답하세요.", ['4', '네', '네칸', '4칸'],
                    '네 칸이에요. 파이썬은 공백 네 칸 들여쓰기로 "이 줄은 위 조건문에 속한다"를 표시해요. 들여쓰기가 빠지면 오류예요. 깊이가 다르면 다른 문장에 딸린 줄이 돼요.')),
    coding('simple-if', '조건에 따라 다른 문장 출력',
        goal="""
        실행 입력에 가격이 한 줄로 들어와요. 가격이 10000 **이상**이면 `기준 이상`, 아니면 `기준 미만`을 출력하세요.

        예: 입력 `10200` → `기준 이상`, 입력 `9900` → `기준 미만`. 10000을 넣으면 어느 쪽이 나와야 할지 생각해 보세요.
        """,
        hint="""
        `if price >= 10000:`처럼 조건 뒤에 콜론을 찍으세요. 다음 줄은 공백 네 칸 들여서 `print('기준 이상')`이에요. 그 아래 `else:`와 들여쓴 `print('기준 미만')`을 같은 모양으로 쓰세요. 10000도 "이상"에 포함되니까 `>`가 아니라 `>=`예요.
        """,
        starter='price = int(input())\n# if와 else로 출력하세요\n',
        solution="price = int(input())\nif price >= 10000:\n    print('기준 이상')\nelse:\n    print('기준 미만')\n",
        tests=[io('10200\n', '기준 이상\n'), io('9900\n', '기준 미만\n'), io('10000\n', '기준 이상\n')]),
    coding('for-sum', '반복문으로 합계 누적하기',
        goal="""
        앞 단원에서는 `sum()`이 합계를 구해 줬죠? 이번에는 그 일을 직접 해요. `prices`의 값을 `for`로 하나씩 꺼내 `total`에 더하세요. 반복이 끝나면 `total`을 출력하세요.

        결과가 40200이면 맞게 한 거예요. `sum()`을 쓰지 않고 누적하세요.
        """,
        hint="""
        `for price in prices:`라고 쓰면 `price`에 값이 하나씩 들어와요. 그때마다 아래 들여쓴 줄이 반복돼요. 그 안에서 `total += price`로 누적하세요. `print(total)`은 들여쓰기 없이 반복문 **밖**에 두세요. 그래야 마지막에 한 번만 출력돼요.
        """,
        starter='prices = [10000, 10200, 9900, 10100]\ntotal = 0\n# for 반복문으로 total에 누적하세요\n',
        solution='prices = [10000, 10200, 9900, 10100]\ntotal = 0\nfor price in prices:\n    total += price\nprint(total)\n',
        check="assert s['total'] == 40200"),
    coding('above-count', '반복하면서 조건으로 세기',
        goal="""
        합계를 구하면서 기준 10000 이상인 날이 며칠인지도 같이 세어 볼게요. 합계는 `total`에 저장하세요. 기준 이상인 값의 개수는 `above_count`에 저장하세요.

        합계 40200, 개수 3이 나오면 맞게 한 거예요.
        """,
        hint="""
        `for price in prices:` 안에서 매번 `total += price`를 해요. 그 아래 `if price >= 10000:`이면 `above_count += 1`이에요. `if`에 속한 줄은 공백 여덟 칸이에요.
        """,
        starter='prices = [10000, 10200, 9900, 10100]\ntotal = 0\nabove_count = 0\n# 반복문을 작성하세요\n',
        solution='prices = [10000, 10200, 9900, 10100]\ntotal = 0\nabove_count = 0\nfor price in prices:\n    total += price\n    if price >= 10000:\n        above_count += 1\nprint(total, above_count)\n',
        check="assert s['total'] == 40200 and s['above_count'] == 3"),
    coding('max-price', '반복문으로 최댓값 찾기',
        goal="""
        가장 비쌌던 날의 가격을 찾아요. `max()` 함수를 쓰면 한 줄이죠. 그런데 이번에는 반복문과 `if`로 직접 찾아 `highest`에 저장하세요. 첫 값을 일단 최고로 두고, 더 큰 값을 만날 때마다 바꾸는 방식이에요.

        결과가 10200이면 맞게 한 거예요.
        """,
        hint="""
        준비 코드가 `highest`를 첫 값으로 시작해 둬요. 반복 안에서 `if price > highest:`를 확인해요. 참일 때만 `highest = price`로 갈아 끼우세요. 반복이 끝나면 가장 큰 값이 남아요.
        """,
        starter='prices = [10000, 10200, 9900, 10100]\nhighest = prices[0]\n# 반복문과 if로 highest를 갱신하세요\n',
        solution='prices = [10000, 10200, 9900, 10100]\nhighest = prices[0]\nfor price in prices:\n    if price > highest:\n        highest = price\nprint(highest)\n',
        check="assert s['highest'] == 10200"),
    coding('croissant-plan', '오늘 크루아상 몇 개 구울까',
        intro="""
        파리바게뜨 공장의 생산 담당자는 새벽마다 오늘 크루아상을 몇 개 구울지 정해요. 너무 많이 구우면 저녁에 버리고, 너무 적게 구우면 오후에 품절이에요. 가장 단순한 방법은 최근 판매량 평균에서 출발하는 거예요. 이 공장은 "품절보다 폐기가 싸다"고 보고 평균보다 10% 많이 굽기로 정했어요.
        """,
        goal="""
        지난 사흘 판매량 `sold`가 준비되어 있어요. `for`로 합계를 `total`에 누적하세요. 평균은 `average`에 저장하세요. 평균의 1.1배를 반올림한 정수는 `plan`에 저장하세요. 그리고 `오늘 생산 계획: 460개` 형식으로 출력하세요.

        합계 1255, 평균 약 418.3, 계획 460이 나오면 맞게 한 거예요. `sum()`을 쓰지 말고 반복문으로 누적하세요.
        """,
        hint="""
        `for count in sold:` 안에서 `total += count`를 해요. 반복이 끝난 뒤 `average = total / len(sold)`로 평균을 내요. 반올림은 `round(average * 1.1)`이고 결과는 정수예요. 출력은 f-문자열 `print(f'오늘 생산 계획: {plan}개')`로 하면 돼요.
        """,
        starter='sold = [412, 388, 455]\ntotal = 0\n# total, average, plan을 만들고 출력하세요\n',
        solution="sold = [412, 388, 455]\ntotal = 0\nfor count in sold:\n    total += count\naverage = total / len(sold)\nplan = round(average * 1.1)\nprint(f'오늘 생산 계획: {plan}개')\n",
        check="assert s['total'] == 1255 and abs(s['average'] - 1255 / 3) < 1e-9\nassert s['plan'] == 460 and isinstance(s['plan'], int)"),
    coding('holdings-amounts', '세 종목의 금액 계산하기',
        goal="""
        리스트 안의 값이 숫자가 아니라 딕셔너리여도 `for`는 똑같이 돌아요. 세 종목이 든 `holdings`를 돌면서 각 종목의 가격 × 수량을 계산하세요. 그 값을 그 종목의 `amount` 키에 저장하세요.

        세 종목의 금액이 30000, 40000, 60000이면 맞게 한 거예요. 합계는 다음 미션에서 구해요.
        """,
        hint="""
        `for holding in holdings:`라고 쓰세요. `holding`에 종목 딕셔너리가 하나씩 들어와요. 그 안에서 새 키를 추가하세요. `holding['amount'] = holding['price'] * holding['quantity']`로요. 반복이 끝난 뒤 `print(holdings)`로 세 종목을 확인하세요.
        """,
        starter=HOLDINGS + "# 각 종목에 amount를 추가하세요\n",
        solution=HOLDINGS + "for holding in holdings:\n    holding['amount'] = holding['price'] * holding['quantity']\nprint(holdings)\n",
        check="assert len(s['holdings']) == 3\nassert [h['amount'] for h in s['holdings']] == [30000, 40000, 60000]"),
    coding('holdings-total', '세 종목의 금액 합산하기',
        goal="""
        준비 코드에는 각 종목의 금액이 이미 계산돼 있어요. 세 종목의 `amount`를 모두 더해 `total_amount`에 저장하세요. 그리고 출력하세요.

        결과가 130000이면 맞게 한 거예요.
        """,
        hint="""
        앞의 「반복문으로 합계 누적하기」 미션과 같은 모양이에요. 반복 전에 `total_amount = 0`을 만들어요. 반복 안에서 `total_amount += holding['amount']`로 더해요. 반복이 끝난 뒤 출력하면 돼요.
        """,
        starter=HOLDINGS_WITH_AMOUNT + "# total_amount를 계산하고 출력하세요\n",
        solution=HOLDINGS_WITH_AMOUNT + "total_amount = 0\nfor holding in holdings:\n    total_amount += holding['amount']\nprint(total_amount)\n",
        check="assert s['total_amount'] == 130000"),
    concept('first-dataframe', '딕셔너리 묶음은 사실 표였다',
        body="""
        방금 다룬 `holdings`를 종이에 적어 보면 이렇게 돼요. 종목 하나가 한 줄, 이름·가격·수량·금액이 한 칸씩.

        ```comic-gen
        제목: 딕셔너리 묶음이 표가 되기까지
        등장인물:
          강사:
            그림: 사람
            이름표: 강사
            외형: {옷: 재킷, 옷색: "#5379a7", 안경: true}
        컷:
          - 인물: [{식별자: 강사, 손모양: 가리키는손}]
            대사: [{화자: 강사, 내용: "같은 키를 가진 딕셔너리를 줄줄이 세우면 그게 표예요."}]
            다이어그램:
              종류: 머메이드
              제목: holdings → DataFrame
              높이: 560
              원문: |
                flowchart TB
                  A["딕셔너리 A"] --> D
                  B["딕셔너리 B"] --> D
                  C["딕셔너리 C"] --> D
                  D["pd.DataFrame(holdings)"] --> E["3행 × 3열 표"]
                  E --> F["키 = 열 이름, 딕셔너리 하나 = 한 행"]
        ```

        | name | price | quantity | amount |
        | --- | ---: | ---: | ---: |
        | A | 10000 | 3 | 30000 |
        | B | 20000 | 2 | 40000 |
        | C | 15000 | 4 | 60000 |

        딕셔너리 하나는 표의 **한 행**이에요. 딕셔너리를 모은 리스트는 **표 전체**고요. 그런데 열 하나 더하기, 조건에 맞는 행 고르기를 매번 반복문으로 짜면 번거롭죠? 그래서 표를 전문으로 다루는 도구 `pandas`를 써요. `pandas`가 다루는 표를 `DataFrame`이라고 불러요. 리스트에 든 딕셔너리들을 넘기면 바로 표가 돼요.

        ```python
        import pandas as pd

        df = pd.DataFrame(holdings)
        print(df.shape)  # (3, 4) → 3행 4열
        df
        ```

        첫 줄 `import pandas as pd`는 이런 선언이에요. "pandas를 가져와서 짧게 `pd`라고 부르겠다." 그래서 표를 쓰는 모든 코드의 맨 위에 오죠. `df.shape`는 (행 수, 열 수)예요. 행 번호인 인덱스는 열 수에 들어가지 않아요. 그리고 코드 **마지막 줄에 `df`만 적으면** 이 앱이 표를 그려서 보여 줘요. `print(df)`도 되지만 글자로만 나와요. 그러니 마지막 줄 방식을 쓰세요.

        한 열 전체를 더하는 일은 반복문 없이 `df['amount'].sum()` 한 줄이에요. 앞 미션에서 반복문으로 했던 일이 어떻게 한 줄로 줄어들까요? 다음 두 미션에서 직접 봐요.
        """,
        check=short("""
                    `pandas`에서 행과 열로 된 표를 뭐라고 부르나요? 변수 이름 `df`가 아니라 자료구조 이름을 답하세요.

                    ```python
                    import pandas as pd

                    df = pd.____(holdings)
                    ```
                    """, ['DataFrame', '데이터프레임'],
                    '`DataFrame`이에요. `pandas`의 표 자료구조죠. `df`는 그 표를 담은 변수 이름일 뿐이에요. `pd`는 `pandas`를 짧게 부르는 별칭이고요.')),
    coding('holdings-frame', '세 종목을 표로 보기',
        goal="""
        금액까지 들어 있는 `holdings`를 `DataFrame`으로 만들어 `df`에 저장하세요. 마지막 줄에 `df`를 적어 표를 띄워 보세요.

        3행 4열이면 맞게 한 거예요. 열 이름은 `name`, `price`, `quantity`, `amount` 순이고요.
        """,
        hint="""
        `df = pd.DataFrame(holdings)` 한 줄이면 돼요. 그다음 줄에 `df`만 적으세요. `print()`나 합계는 필요 없어요.
        """,
        starter="import pandas as pd\n" + HOLDINGS_WITH_AMOUNT + "# df를 만들고 표를 표시하세요\n",
        solution="import pandas as pd\n" + HOLDINGS_WITH_AMOUNT + "df = pd.DataFrame(holdings)\ndf\n",
        check="assert s['df'].shape == (3, 4)\nassert list(s['df'].columns) == ['name', 'price', 'quantity', 'amount']\nassert s['df']['name'].tolist() == ['A', 'B', 'C']\nassert s['df']['amount'].tolist() == [30000, 40000, 60000]"),
    coding('frame-column-sum', '표의 한 열을 합산하기',
        goal="""
        조금 전 반복문으로 구했던 전체 금액을 이번에는 표로 구해요. `df`의 `amount` 열을 골라 `.sum()`으로 합계를 내세요. 그 값을 `total_amount`에 저장하고 출력하세요.

        결과는 역시 130000이에요. 두 방법의 코드 길이를 비교해 보세요.
        """,
        hint="""
        `df['amount']`가 한 열이에요. 뒤에 `.sum()`을 붙이면 그 열의 합계예요. 반복문도 `total_amount = 0`도 필요 없어요.
        """,
        starter="import pandas as pd\n" + HOLDINGS_WITH_AMOUNT + "df = pd.DataFrame(holdings)\n# total_amount를 계산하고 출력하세요\n",
        solution="import pandas as pd\n" + HOLDINGS_WITH_AMOUNT + "df = pd.DataFrame(holdings)\ntotal_amount = df['amount'].sum()\nprint(total_amount)\n",
        check="assert s['total_amount'] == 130000"),
    concept('why-fast', '리스트로도 되는데 왜 pandas인가',
        body="""
        방금 같은 합계를 반복문으로도, 표로도 구했죠? 그러니 이런 질문이 나올 만해요. "리스트 안의 딕셔너리로도 다 되는데, 왜 굳이 `pandas`를 배우나요?" 답은 두 가지예요. **짧고, 빨라요.** 짧은 건 방금 봤어요. 빠른 건 `pandas`가 **넘파이**(NumPy) 위에 지어져서예요. 넘파이는 숫자 배열 도구고요.

        ```comic-gen
        제목: 백만 개 더하기 시합
        등장인물:
          준호:
            그림: 사람
            이름표: 준호 · 은행 직원
            외형: {머리색: "#303746", 옷색: "#b88646"}
          파이썬: {그림: 서버, 이름표: Python 반복문}
          넘파이: {그림: 서버, 이름표: NumPy}
        컷:
          - 인물: [준호, 파이썬, 넘파이]
            대사:
              - {화자: 준호, 상대: 파이썬, 내용: "숫자 백만 개 더해 줘."}
              - {화자: 파이썬, 상대: 준호, 내용: "하나 꺼내고, 숫자인지 보고, 더하고… 백만 번."}
          - 구성: 이전
            인물: [{식별자: 준호, 표정: 어리둥절}, 파이썬, {식별자: 넘파이, 표정: 기쁨}]
            대사:
              - {화자: 넘파이, 상대: 준호, 내용: "저는 백만 개를 한 덩어리로 받아서 C 언어로 한 번에 더해요."}
              - {화자: 준호, 상대: 넘파이, 내용: "그래서 백 배 빠른 거구나."}
        ```

        파이썬 반복문은 값을 하나 꺼낼 때마다 매번 확인해요. "이게 숫자인가, 더할 수 있나" 하고요. 넘파이는 같은 종류의 숫자를 **메모리 한 덩어리**에 나란히 둬요. 그걸 C 언어로 짜인 반복문이 한 번에 훑어요. 요즘 CPU는 숫자 여러 개를 한 명령으로 처리하거든요. 코어도 여러 개라서 큰 계산은 **여러 코어가 나눠서 병렬로** 해요. 그래서 백만 행이면 수십 배에서 수백 배 차이가 나죠.

        ```mapping
        제목: 반복문과 넘파이의 차이
        종류: 비교
        왼쪽: Python 반복문
        오른쪽: NumPy 배열
        값 하나씩 꺼낸다 → 덩어리째 넘긴다
        매번 종류를 확인한다 → 종류는 처음 한 번만
        Python이 한 줄씩 실행 → C 코드가 한 번에 실행
        코어 하나 → 코어 여러 개가 나눠서
        ```

        ```python
        import numpy as np

        values = np.array([10000, 10200, 9900, 10100])
        print(values.sum())  # 40200, 반복문 없이
        print(values * 1.1)  # 네 값 전부에 한 번에 1.1배
        ```

        넘파이의 자리는 생각보다 커요. `pandas`의 표 한 열이 넘파이 배열이에요. 뒤에서 쓸 `scikit-learn`도 넘파이 배열을 주고받아요. 그래프를 그리는 `matplotlib`도요. 딥러닝 도구(PyTorch, TensorFlow)가 다루는 텐서는 넘파이 배열의 사촌이에요. 사진 한 장도 컴퓨터 안에서는 숫자 배열이거든요. 이 수업에서 `import numpy`를 직접 칠 일은 거의 없어요. 그래도 쓰는 도구 전부가 그 위에 서 있죠.

        여기서 옛날이야기 하나. 넘파이는 C 코드라서 설치하려면 **컴파일**(C 코드를 기계어로 바꾸는 일)이 필요했어요. 윈도우에서는 그게 자주 실패했고요. 그래서 미리 컴파일된 패키지를 묶어 주는 **아나콘다**(conda)가 거의 필수였죠. 지금은 `pip`이 미리 컴파일된 파일(wheel)을 그대로 받아와요. 그래서 `pip install pandas` 한 줄이면 끝이에요. 이 앱도 conda 없이 돌아가요. 오래된 자료가 "먼저 아나콘다를 설치하세요"라고 하면 그 시절 이야기죠.

        정리하면 "리스트로도 된다"는 말도 맞고, "표는 `pandas`로"라는 말도 맞아요. 값이 네 개면 차이가 없어요. 백만 행이면 차이가 백 배죠. 다음 미션에서 그 차이를 직접 재요.
        """,
        check=short("`pandas`는 이 숫자 배열 도구 위에 지어져서 반복문보다 빨라요. 그 도구 이름이 뭘까요?", ['numpy', 'NumPy', '넘파이', 'np'],
                    '넘파이(NumPy)예요. 같은 종류의 숫자를 메모리 한 덩어리에 두고 C 코드로 한 번에 계산해요. `pandas`도 `scikit-learn`도 `matplotlib`도 그 위에 서 있어요. 딥러닝 도구도요.')),
    coding('numpy-race', '백만 개 더하기 시합',
        goal="""
        숫자 0부터 999,999까지가 준비되어 있어요. 리스트 `values`에도, 넘파이 배열 `array`에도요. 같은 합계를 두 방법으로 구하고 걸린 시간을 재요. `for` 반복문으로 더한 합계는 `total`에, 그 시간은 `loop_seconds`에 담으세요. `array.sum()`의 결과는 `numpy_total`에, 그 시간은 `numpy_seconds`에 담으세요. 그리고 두 시간과 몇 배 빠른지를 출력하세요.

        합계는 둘 다 499,999,500,000이에요. 넘파이 쪽 시간이 훨씬 짧아야 해요. 몇 배인지는 컴퓨터마다 달라요.
        """,
        hint="""
        시간 재기는 `start = time.perf_counter()`로 시작해요. 끝난 뒤 `time.perf_counter() - start`를 하면 걸린 초가 나와요. 반복문 구간과 `array.sum()` 구간을 각각 감싸세요. 출력은 f-문자열 `{loop_seconds:.4f}`처럼 소수 네 자리로 해요. 배수는 `loop_seconds / numpy_seconds`를 `:.0f`로 찍어요.
        """,
        starter='import time\nimport numpy as np\n\nvalues = list(range(1_000_000))\narray = np.array(values)\n# total, loop_seconds, numpy_total, numpy_seconds를 만들고 출력하세요\n',
        solution="import time\nimport numpy as np\n\nvalues = list(range(1_000_000))\narray = np.array(values)\nstart = time.perf_counter()\ntotal = 0\nfor value in values:\n    total += value\nloop_seconds = time.perf_counter() - start\nstart = time.perf_counter()\nnumpy_total = array.sum()\nnumpy_seconds = time.perf_counter() - start\nprint(f'반복문 {loop_seconds:.4f}초, 넘파이 {numpy_seconds:.4f}초')\nprint(f'넘파이가 {loop_seconds / numpy_seconds:.0f}배 빠르다')\n",
        check="assert s['total'] == 499999500000 and int(s['numpy_total']) == 499999500000\nassert s['loop_seconds'] > s['numpy_seconds'] > 0"),
    quiz('control-check', '단원 점검',
        choice('`if price >= 10000:`에서 `price`가 정확히 10000이면 어떻게 되나요?',
               ['조건이 참이라 아래 줄이 실행된다', '조건이 거짓이라 건너뛴다', '같은 값은 오류가 난다'], 0,
               '조건이 참이라 아래 줄이 실행돼요. `>=`는 "이상"이라 같은 값도 포함하거든요. 같은 값을 빼고 싶을 때만 `>`를 써요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「거짓이라 건너뛴다」: 그건 `>`일 때 이야기예요.\n- 「같은 값은 오류」: 비교는 참·거짓만 돌려주고 오류를 안 내요."),
        choice('`for price in prices:` 바로 아래 줄을 들여쓰지 않으면 어떻게 되나요?',
               ['`IndentationError`가 난다', '그 줄이 한 번만 실행된다', '그 줄이 무시된다'], 0,
               '`IndentationError`가 나요. 반복할 줄은 반드시 들여써야 하거든요. 들여쓰기가 없으면 파이썬은 "반복할 내용이 없다"고 보고 오류를 내요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「한 번만 실행된다」: 실행까지 가지 못하고 문법 오류가 나요.\n- 「무시된다」: 파이썬은 조용히 넘어가지 않아요."),
        choice('합계를 담을 `total = 0`은 어디에 두어야 하나요?',
               ['반복문이 시작되기 전에 한 번', '반복문 안에 매번', '반복문이 끝난 뒤'], 0,
               '반복문이 시작되기 전에 한 번이에요. 반복 안에 두면 매번 0으로 돌아가 마지막 값만 남아요. 반복 뒤에 두면 더한 결과를 0으로 덮어쓰고요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「반복문 안에 매번」: 매번 0으로 초기화되어 합계가 안 쌓여요.\n- 「반복문이 끝난 뒤」: 다 더한 결과를 0으로 덮어써요."),
        short('`total = total + price`를 짧게 쓰는 연산자는 무엇인가요? (`total __ price`)', ['+=', '+ ='],
              '`+=`예요. "지금 값에 더해서 다시 저장해라"라는 뜻이에요. 반복문 안에서 누적할 때 늘 써요.'),
        short('3행 4열 표의 `df.shape`는 무엇인가요?', ['(3,4)', '3,4', '(3, 4)'],
              '(3, 4)예요. `shape`는 (행 수, 열 수) 순서거든요. 행 번호인 인덱스는 열 수에 들어가지 않아요.'),
        choice('표를 앱 화면에 그려서 보려면 코드 마지막 줄에 무엇을 적나요?',
               ['`df`', "`print('df')`", '`df.sum()`'], 0,
               "마지막 줄에 `df`만 적으면 앱이 표로 그려 줘요." "\n\n**다른 보기는 왜 아닌가**\n\n- 「print('df')」: 따옴표 안 글자 df 두 글자가 출력돼요.\n- 「df.sum()」: 열별 합계만 나와요. 표 전체는 안 보여요."),
        choice('표 계산이 반복문보다 빠른 진짜 이유는 무엇인가요?',
               ['`pandas`가 C로 짜인 NumPy 배열을 한 덩어리로 한 번에 계산해서', 'Python 반복문은 원래 쓰면 안 되는 문법이라서', '표가 화면에 예쁘게 그려져서'], 0,
               '넘파이가 덩어리째 계산해서예요. 같은 종류의 숫자를 메모리 한 덩어리에 둬요. 그걸 C 코드가 한 번에, 코어 여러 개가 나눠서 계산해요. 반복문은 값마다 종류를 확인하며 한 줄씩 가고요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「반복문은 쓰면 안 되는 문법」: 반복문은 멀쩡한 문법이에요. 값이 몇 개면 차이도 없고요.\n- 「예쁘게 그려져서」: 보기 좋은 것과 빠른 것은 다른 이야기예요."),
        choice("""**프롬프트 고르기** · `sum()`을 쓰지 않고 `for`로 합계를 누적하는 연습 문제예요. 어떤 프롬프트가 연습 목적에 맞는 코드를 받을까요?""",
               ["""파이썬. prices = [10000,10200,9900,10100]. sum() 쓰지 말고 for 반복문으로 total에 누적해서 출력. 코드만 줘""", """리스트 합계 구하는 가장 짧은 코드 줘""", """prices 합계 출력해 줘""", """파이썬 반복문 예제 하나 줘"""], 0,
               """정답은 "sum() 쓰지 말고 for로"예요. 막을 것과 시킬 것이 한 줄에 있죠. 쉬운 길을 막지 않으면 AI는 늘 sum()을 써요.

**다른 보기는 왜 아닌가**

- 「가장 짧은 코드」: sum(prices)가 돌아와요. 연습이 안 돼요.
- 「합계 출력해 줘」: 방법을 안 정했으니 역시 sum()이에요.
- 「반복문 예제 하나」: 내 자료, 내 변수 이름과 무관한 예제가 와요."""),
        choice("""**프롬프트 고르기** · 빵 공장 규칙을 코드로 받으려 해요. 규칙은 "지난 사흘 판매량 평균보다 10% 여유 있게 굽는다"예요. 어떤 프롬프트가 검사를 통과하는 숫자를 줄까요?""",
               ["""파이썬. sold = [412, 388, 455]. for로 합계를 total에, 평균을 average에, 평균의 1.1배를 round한 정수를 plan에 담아 "오늘 생산 계획: 460개" 형식으로 출력. 코드만 줘""", """크루아상 몇 개 구울지 정하는 코드 줘""", """판매량 평균보다 조금 여유 있게 생산량 정해 줘""", """sold 리스트로 생산 계획 세워 줘. 넉넉하게"""], 0,
               """정답은 현장 규칙을 숫자와 함수(1.1배, round, 정수)로 번역했어요. 출력 형식까지 고정했고요. "조금", "넉넉하게"는 AI마다 다른 숫자를 줘요.

**다른 보기는 왜 아닌가**

- 「몇 개 구울지 정하는 코드」: 자료도 규칙도 없어요.
- 「조금 여유 있게」: 1.05배인지 1.2배인지 AI가 정해요.
- 「넉넉하게」: 결과를 담을 변수 이름도 출력 형식도 없어요. 검사기가 못 읽어요."""),
    ),
])
