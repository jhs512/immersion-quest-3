"""aice-data-join: read JSON, merge two tables by a key, stack two months (AICE Associate 6th lesson).

Small original order and customer files. Every scenario changes row counts, which keys are missing
or repeated, and the key values, so a memorized screen cannot pass. Data are built so pandas 1.5.3
and 3.x agree: inner merges only meet repeated keys in adjacent rows (1.5.3 groups them), JSON keys
are either 'C01'-style text or plain JSON numbers (read_json turns digit strings into integers in
both versions), and every shop file mixes 비회원 into the key so the text side stays text.
"""
from certification_course.kit import py_task
from principles_course.common import code, lesson

SOURCES = ['https://aice.study/info/aice/asso', 'https://pandas.pydata.org/docs/reference/api/pandas.read_json.html',
           'https://pandas.pydata.org/docs/reference/api/pandas.merge.html',
           'https://pandas.pydata.org/docs/reference/api/pandas.concat.html']


def renamed(text, old, new):
    # Same records with another key name, for files whose key column is named differently.
    return text.replace('"' + old + '"', '"' + new + '"')


# Base: two customers (C04, C06) have orders but no customer record; C01 orders twice in a row.
ORDERS = code('''
    order_id,customer_id,amount
    A101,C01,12000
    A102,C01,5000
    A103,C03,8000
    A104,C04,15000
    A105,C02,9000
    A106,C06,7000
''')
CUSTOMERS = code('''
    [
      {"customer_id": "C01", "region": "서울", "grade": "gold"},
      {"customer_id": "C02", "region": "부산", "grade": "silver"},
      {"customer_id": "C03", "region": "서울", "grade": "silver"},
      {"customer_id": "C05", "region": "대구", "grade": "gold"}
    ]
''')
# Fewer orders; C07 is missing twice and one listed customer never ordered.
ORDERS_B = code('''
    order_id,customer_id,amount
    B201,C04,3000
    B202,C02,11000
    B203,C07,6500
    B204,C07,4000
    B205,C06,2000
''')
CUSTOMERS_B = code('''
    [
      {"customer_id": "C02", "region": "대전", "grade": "gold"},
      {"customer_id": "C04", "region": "서울", "grade": "bronze"},
      {"customer_id": "C06", "region": "광주", "grade": "silver"}
    ]
''')
# More orders; the first order's customer is missing, three missing in all.
ORDERS_C = code('''
    order_id,customer_id,amount
    D301,C02,4500
    D302,C03,13000
    D303,C05,6000
    D304,C05,8200
    D305,C10,9900
    D306,C08,3100
    D307,C04,7600
''')
CUSTOMERS_C = code('''
    [
      {"customer_id": "C01", "region": "인천", "grade": "silver"},
      {"customer_id": "C03", "region": "부산", "grade": "gold"},
      {"customer_id": "C05", "region": "서울", "grade": "bronze"},
      {"customer_id": "C08", "region": "대구", "grade": "gold"},
      {"customer_id": "C09", "region": "서울", "grade": "silver"},
      {"customer_id": "C11", "region": "광주", "grade": "gold"}
    ]
''')
JOIN = {'data/orders.csv': ORDERS, 'data/customers.json': CUSTOMERS}
JOIN_SCENARIOS = [{'files': {'data/orders.csv': ORDERS_B, 'data/customers.json': CUSTOMERS_B}},
                  {'files': {'data/orders.csv': ORDERS_C, 'data/customers.json': CUSTOMERS_C}}]

# The member file names its key member_id.
MEMBERS = {'data/orders.csv': ORDERS, 'data/members.json': renamed(CUSTOMERS, 'customer_id', 'member_id')}
MEMBER_SCENARIOS = [
    {'files': {'data/orders.csv': ORDERS_B, 'data/members.json': renamed(CUSTOMERS_B, 'customer_id', 'member_id')}},
    {'files': {'data/orders.csv': ORDERS_C, 'data/members.json': renamed(CUSTOMERS_C, 'customer_id', 'member_id')}}]

# Customer lists with a repeated customer. C keeps a changed grade below, so only the key decides.
DUPLICATED = code('''
    [
      {"customer_id": "C01", "region": "서울", "grade": "gold"},
      {"customer_id": "C02", "region": "부산", "grade": "silver"},
      {"customer_id": "C03", "region": "서울", "grade": "silver"},
      {"customer_id": "C02", "region": "부산", "grade": "silver"}
    ]
''')
DUPLICATED_B = code('''
    [
      {"customer_id": "C02", "region": "대전", "grade": "gold"},
      {"customer_id": "C04", "region": "서울", "grade": "bronze"},
      {"customer_id": "C04", "region": "서울", "grade": "bronze"},
      {"customer_id": "C06", "region": "광주", "grade": "silver"},
      {"customer_id": "C06", "region": "광주", "grade": "silver"}
    ]
''')
DUPLICATED_C = code('''
    [
      {"customer_id": "C01", "region": "인천", "grade": "silver"},
      {"customer_id": "C03", "region": "부산", "grade": "gold"},
      {"customer_id": "C05", "region": "서울", "grade": "bronze"},
      {"customer_id": "C05", "region": "서울", "grade": "gold"},
      {"customer_id": "C08", "region": "대구", "grade": "gold"}
    ]
''')

# Shop files: numeric customer numbers, and 비회원 keeps the order key a text column.
SHOP_ORDERS = code('''
    order_id,customer_id,amount
    S01,101,12000
    S02,비회원,5000
    S03,103,8000
    S04,104,15000
    S05,103,6000
''')
SHOP_CUSTOMERS = code('''
    [
      {"customer_id": 101, "region": "서울", "grade": "gold"},
      {"customer_id": 103, "region": "부산", "grade": "silver"},
      {"customer_id": 105, "region": "대구", "grade": "gold"}
    ]
''')
SHOP_ORDERS_B = code('''
    order_id,customer_id,amount
    S11,비회원,7000
    S12,102,3000
    S13,107,9500
    S14,비회원,4000
''')
SHOP_CUSTOMERS_B = code('''
    [
      {"customer_id": 102, "region": "광주", "grade": "silver"},
      {"customer_id": 107, "region": "서울", "grade": "bronze"},
      {"customer_id": 108, "region": "대전", "grade": "gold"}
    ]
''')
SHOP_ORDERS_C = code('''
    order_id,customer_id,amount
    S21,110,5500
    S22,111,8800
    S23,비회원,2500
    S24,112,13000
    S25,110,4100
    S26,113,6600
''')
SHOP_CUSTOMERS_C = code('''
    [
      {"customer_id": 110, "region": "부산", "grade": "gold"},
      {"customer_id": 112, "region": "인천", "grade": "silver"},
      {"customer_id": 113, "region": "서울", "grade": "silver"},
      {"customer_id": 114, "region": "대구", "grade": "bronze"}
    ]
''')

# Two months with the same columns; each scenario changes both row counts.
MONTH9 = code('''
    order_id,customer_id,amount
    A101,C01,12000
    A102,C01,5000
    A103,C03,8000
''')
MONTH10 = code('''
    order_id,customer_id,amount
    A104,C04,15000
    A105,C02,9000
    A106,C06,7000
    A107,C03,4000
''')
MONTH9_B = code('''
    order_id,customer_id,amount
    B201,C04,3000
    B202,C02,11000
''')
MONTH10_B = code('''
    order_id,customer_id,amount
    B203,C07,6500
    B204,C06,2000
    B205,C04,5200
''')
MONTH9_C = code('''
    order_id,customer_id,amount
    D301,C02,4500
    D302,C03,13000
    D303,C05,6000
    D304,C05,8200
''')
MONTH10_C = code('''
    order_id,customer_id,amount
    D305,C10,9900
    D306,C08,3100
''')
MONTHS = {'data/orders_09.csv': MONTH9, 'data/orders_10.csv': MONTH10}
MONTH_SCENARIOS = [{'files': {'data/orders_09.csv': MONTH9_B, 'data/orders_10.csv': MONTH10_B}},
                   {'files': {'data/orders_09.csv': MONTH9_C, 'data/orders_10.csv': MONTH10_C}}]

# Challenge customers: one repeated customer who ordered, and ordering customers with no record.
REPORT_CUSTOMERS = code('''
    [
      {"customer_id": "C01", "region": "서울", "grade": "gold"},
      {"customer_id": "C02", "region": "부산", "grade": "silver"},
      {"customer_id": "C02", "region": "부산", "grade": "silver"},
      {"customer_id": "C03", "region": "서울", "grade": "silver"},
      {"customer_id": "C05", "region": "대구", "grade": "gold"}
    ]
''')
REPORT_SCENARIOS = [
    {'files': {'data/orders_09.csv': MONTH9_B, 'data/orders_10.csv': MONTH10_B, 'data/customers.json': DUPLICATED_B}},
    {'files': {'data/orders_09.csv': MONTH9_C, 'data/orders_10.csv': MONTH10_C, 'data/customers.json': DUPLICATED_C}}]


def build():
    shop = {'data/shop_orders.csv': SHOP_ORDERS, 'data/shop_customers.json': SHOP_CUSTOMERS}
    shop_scenarios = [
        {'files': {'data/shop_orders.csv': SHOP_ORDERS_B, 'data/shop_customers.json': SHOP_CUSTOMERS_B}},
        {'files': {'data/shop_orders.csv': SHOP_ORDERS_C, 'data/shop_customers.json': SHOP_CUSTOMERS_C}}]
    shop_members = {'data/shop_orders.csv': SHOP_ORDERS,
                    'data/shop_members.json': renamed(SHOP_CUSTOMERS, 'customer_id', 'member_no')}
    shop_member_scenarios = [
        {'files': {'data/shop_orders.csv': SHOP_ORDERS_B,
                   'data/shop_members.json': renamed(SHOP_CUSTOMERS_B, 'customer_id', 'member_no')}},
        {'files': {'data/shop_orders.csv': SHOP_ORDERS_C,
                   'data/shop_members.json': renamed(SHOP_CUSTOMERS_C, 'customer_id', 'member_no')}}]
    return lesson('aice-data-join', '여러 파일을 읽어 하나의 표로',
        'JSON과 CSV를 읽어 같은 키로 합치고, 두 달 자료를 위아래로 이어요. '
        '합친 뒤에는 행 수와 빈칸을 꼭 확인해요. 필수 문제 7개와 선택 도전 2개예요.', SOURCES, [
      py_task('read-json', 'JSON 파일을 표로 읽어요',
        'JSON은 `{"이름": 값}` 묶음을 `[ ]` 안에 늘어놓은 글자 파일이에요.\n'
        '묶음 하나가 한 행이 되고, 이름은 열 이름이 돼요.\n'
        '`pd.read_json`은 이런 JSON 파일을 읽어 표로 만들어요.',
        '자, 먼저 코드 실행을 누르세요. JSON 파일을 read_csv로 읽었어요.\n'
        '표의 크기와 열 이름을 보세요. 고객 한 명이 한 행이 됐나요?\n'
        '`pd.read_csv`를 `pd.read_json`으로 바꾸고 다시 실행하세요.\n'
        '크기와 열 이름을 처음 결과와 비교해요.',
        '''
        import pandas as pd

        # 직접 만든 고객 자료예요. 실제 고객 자료가 아니에요.
        # 고객 파일은 JSON인데 CSV를 읽는 함수로 읽었어요.
        customers = pd.read_csv('data/customers.json')
        # 표의 크기를 확인해요. 앞 숫자가 행 수예요.
        print(customers.shape)
        # 표 전체를 봐요. 맨 위 줄이 열 이름이에요.
        print(customers)
        ''',
        "pd.read_csv('data/customers.json')", "pd.read_json('data/customers.json')",
        files={'data/customers.json': CUSTOMERS}, compare=['customers'],
        scenarios=[{'files': {'data/customers.json': CUSTOMERS_B}}, {'files': {'data/customers.json': CUSTOMERS_C}}],
        wrong=[("pd.read_csv('data/customers.json')", "pd.read_json('data/customers.json', lines=True)"),
               ("pd.read_csv('data/customers.json')", "pd.read_json('customers.json')")],
        caution='JSON을 read_csv로 읽어도 오류 없이 엉뚱한 표가 나와요.',
        hints=["`pd.read_json('data/customers.json')`로 바꿔요. 경로는 그대로 둬요."]),
      py_task('merge-on', '같은 키로 두 표를 합쳐요',
        "`pd.merge(왼쪽, 오른쪽, on='열')`은 두 표를 하나로 합쳐요.\n"
        'on에 적은 열을 키라고 해요. 키 값이 같은 행끼리 옆으로 붙어요.\n'
        '따로 정하지 않으면 두 표에 모두 있는 키만 남아요.',
        '먼저 실행해서 두 행 수를 보세요. 아직 합치지 않아서 같아요.\n'
        "`merged = orders`를 `merged = pd.merge(orders, customers, on='customer_id')`로 바꾸세요.\n"
        '다시 실행해서 행 수를 비교해요.\n'
        '빠진 주문의 customer_id를 고객 파일에서 찾아보세요.',
        '''
        import pandas as pd

        # 주문 표예요. 누가 샀는지 customer_id로 적혀 있어요.
        orders = pd.read_csv('data/orders.csv')
        # 고객 표예요. 같은 이름의 customer_id 열이 있어요.
        customers = pd.read_json('data/customers.json')
        # 합친 결과를 merged에 담아요. 지금은 주문 표 그대로예요.
        merged = orders
        # len(표)는 행 수예요. 합치기 전과 뒤를 비교해요.
        print(len(orders), len(merged))
        # 합친 표를 확인해요.
        print(merged)
        ''',
        'merged = orders', "merged = pd.merge(orders, customers, on='customer_id')",
        files=JOIN, scenarios=JOIN_SCENARIOS, compare=['merged'],
        wrong=[('merged = orders', "merged = pd.merge(customers, orders, on='customer_id')"),
               ('merged = orders', 'merged = pd.merge(orders, customers, on=customer_id)')],
        caution='두 표의 순서를 바꾸면 고객 표의 열이 앞에 와요.',
        hints=["`pd.merge(orders, customers, on='customer_id')`로 써요. 열 이름은 따옴표로 감싸요."]),
      py_task('how-left', '주문은 모두 남기고 빈칸으로 둬요',
        "`how='left'`를 넣으면 왼쪽 표의 행을 모두 남겨요.\n"
        '짝이 없는 행의 오른쪽 열은 NaN(빈칸)이 돼요.\n'
        '`isna()`는 빈칸이면 True예요. `.sum()`을 붙이면 빈칸 수가 나와요.',
        '먼저 실행해서 두 행 수와 빈칸 수를 보세요.\n'
        "merge 괄호 끝에 `, how='left'`를 넣으세요.\n"
        '다시 실행해서 행 수와 빈칸 수를 비교해요.\n'
        'NaN이 생긴 주문의 customer_id도 확인하세요.',
        '''
        import pandas as pd

        # 주문 표와 고객 표를 읽어요.
        orders = pd.read_csv('data/orders.csv')
        customers = pd.read_json('data/customers.json')
        # customer_id가 같은 행끼리 합쳐요.
        merged = pd.merge(orders, customers, on='customer_id')
        # 합치기 전과 뒤의 행 수예요.
        print(len(orders), len(merged))
        # grade가 빈칸인 행 수예요.
        print(merged['grade'].isna().sum())
        # 합친 표를 확인해요.
        print(merged)
        ''',
        "on='customer_id')", "on='customer_id', how='left')",
        files=JOIN, scenarios=JOIN_SCENARIOS, compare=['merged'],
        wrong=[("on='customer_id')", "on='customer_id', how='right')"),
               ("pd.merge(orders, customers, on='customer_id')",
                "pd.merge(customers, orders, on='customer_id', how='left')")],
        caution="`how='right'`로 쓰면 주문 대신 고객 표의 행이 모두 남아요.",
        hints=["`pd.merge(orders, customers, on='customer_id', how='left')`처럼 써요."]),
      py_task('left-right-on', '키 열 이름이 서로 달라요',
        '두 표가 같은 키를 다른 이름으로 적기도 해요.\n'
        '그럴 땐 `left_on`에 왼쪽 표의 열, `right_on`에 오른쪽 표의 열을 적어요.\n'
        '합친 표에는 두 키 열이 모두 남아요.',
        '먼저 실행해서 두 열 이름 목록과 KeyError를 보세요.\n'
        'KeyError는 그런 이름의 열이 없다는 뜻이에요.\n'
        "`on='customer_id'`를 `left_on='customer_id', right_on='member_id'`로 바꾸세요.\n"
        '다시 실행해서 합친 표의 두 키 열을 비교해요.',
        '''
        import pandas as pd

        # 주문 표와 회원 표를 읽어요.
        orders = pd.read_csv('data/orders.csv')
        members = pd.read_json('data/members.json')
        # 두 표의 열 이름을 리스트로 바꿔 확인해요.
        print(orders.columns.tolist())
        print(members.columns.tolist())
        # 주문은 모두 남기고 회원 정보를 붙여요.
        merged = pd.merge(orders, members, on='customer_id', how='left')
        # 합치기 전과 뒤의 행 수와 합친 표를 봐요.
        print(len(orders), len(merged))
        print(merged)
        ''',
        "on='customer_id'", "left_on='customer_id', right_on='member_id'",
        files=MEMBERS, scenarios=MEMBER_SCENARIOS, compare=['merged'],
        wrong=[("on='customer_id'", "on='member_id'"),
               ("on='customer_id'", "left_on='member_id', right_on='customer_id'"),
               ("on='customer_id', how='left'", "left_on='customer_id', right_on='member_id'")],
        caution='왼쪽과 오른쪽 열 이름을 바꿔 적으면 KeyError가 나요.',
        hints=["`left_on='customer_id', right_on='member_id'`처럼 두 이름을 따로 적어요."]),
      py_task('key-dtype', '두 키의 자료형을 맞춰요',
        "merge는 키 값이 같아야 짝을 지어요. 정수 101과 글자 '101'은 달라요.\n"
        '두 키가 정수 열과 글자 열이면 merge가 ValueError를 내요.\n'
        '`astype(str)`로 정수 쪽을 글자로 바꾸면 두 키가 맞아요.',
        '먼저 실행해서 두 키의 자료형과 오류의 마지막 줄을 보세요.\n'
        '주문 키는 비회원이 섞여 글자 열이에요. str이나 object로 보여요.\n'
        "자료형을 맞추는 주석 아래에 `customers['customer_id'] = customers['customer_id'].astype(str)`을 넣으세요.\n"
        '다시 실행해서 두 자료형과 합친 표를 확인해요.',
        '''
        import pandas as pd

        # 매장 주문이에요. 회원이 아니면 비회원으로 적었어요.
        orders = pd.read_csv('data/shop_orders.csv')
        # 고객 파일의 customer_id는 따옴표 없는 숫자예요.
        customers = pd.read_json('data/shop_customers.json')
        # 이 아래에서 두 키의 자료형을 맞춰요.
        # 열 하나의 자료형은 dtype으로 봐요.
        print(orders['customer_id'].dtype, customers['customer_id'].dtype)
        # 주문은 모두 남기고 고객 정보를 붙여요.
        merged = pd.merge(orders, customers, on='customer_id', how='left')
        # 합치기 전과 뒤의 행 수와 합친 표를 봐요.
        print(len(orders), len(merged))
        print(merged)
        ''',
        '# 이 아래에서 두 키의 자료형을 맞춰요.',
        "# 이 아래에서 두 키의 자료형을 맞춰요.\ncustomers['customer_id'] = customers['customer_id'].astype(str)",
        files=shop, scenarios=shop_scenarios, compare=['merged'],
        wrong=[('# 이 아래에서 두 키의 자료형을 맞춰요.',
                "# 이 아래에서 두 키의 자료형을 맞춰요.\norders['customer_id'] = orders['customer_id'].astype(int)"),
               ('# 이 아래에서 두 키의 자료형을 맞춰요.',
                "# 이 아래에서 두 키의 자료형을 맞춰요.\ncustomers['customer_id'].astype(str)"),
               ('# 이 아래에서 두 키의 자료형을 맞춰요.',
                "# 이 아래에서 두 키의 자료형을 맞춰요.\n"
                "orders['customer_id'] = pd.to_numeric(orders['customer_id'], errors='coerce')")],
        caution='주문 키를 `astype(int)`로 바꾸면 비회원 때문에 ValueError가 나요.',
        hints=["주석 아래에 `customers['customer_id'] = customers['customer_id'].astype(str)`을 넣어요."]),
      py_task('duplicate-key', '합친 뒤 행 수가 늘었어요',
        '오른쪽 표에 같은 키가 두 번 있으면 왼쪽 행이 두 번 붙어요.\n'
        '그래서 합친 뒤에는 행 수를 꼭 확인해요.\n'
        "`drop_duplicates(subset='customer_id')`는 id가 같은 행 중 맨 위 행만 남겨요.",
        "먼저 실행해서 두 행 수를 보세요. `how='left'`인데 늘었죠?\n"
        '합친 표에서 두 번 나온 order_id를 찾아보세요.\n'
        "중복을 지우는 주석 아래에 `customers = customers.drop_duplicates(subset='customer_id')`를 넣으세요.\n"
        '다시 실행해서 두 행 수를 비교해요.',
        '''
        import pandas as pd

        # 주문 표와 고객 표를 읽어요.
        orders = pd.read_csv('data/orders.csv')
        customers = pd.read_json('data/customers.json')
        # 이 아래에서 같은 customer_id의 중복을 지워요.
        # 주문은 모두 남기고 고객 정보를 붙여요.
        merged = pd.merge(orders, customers, on='customer_id', how='left')
        # 합치기 전과 뒤의 행 수예요. 같아야 해요.
        print(len(orders), len(merged))
        # 합친 표를 확인해요.
        print(merged)
        ''',
        '# 이 아래에서 같은 customer_id의 중복을 지워요.',
        "# 이 아래에서 같은 customer_id의 중복을 지워요.\ncustomers = customers.drop_duplicates(subset='customer_id')",
        files={'data/orders.csv': ORDERS, 'data/customers.json': DUPLICATED}, compare=['merged'],
        scenarios=[{'files': {'data/orders.csv': ORDERS_B, 'data/customers.json': DUPLICATED_B}},
                   {'files': {'data/orders.csv': ORDERS_C, 'data/customers.json': DUPLICATED_C}}],
        wrong=[('# 이 아래에서 같은 customer_id의 중복을 지워요.',
                "# 이 아래에서 같은 customer_id의 중복을 지워요.\ncustomers.drop_duplicates(subset='customer_id')"),
               ('# 이 아래에서 같은 customer_id의 중복을 지워요.',
                '# 이 아래에서 같은 customer_id의 중복을 지워요.\ncustomers = customers.drop_duplicates()'),
               ('# 합치기 전과 뒤의 행 수예요. 같아야 해요.',
                'merged = merged.drop_duplicates()\n# 합치기 전과 뒤의 행 수예요. 같아야 해요.')],
        caution='subset 없이 지우면 등급만 다른 중복 행은 남아요.',
        hints=["주석 아래에 `customers = customers.drop_duplicates(subset='customer_id')`를 넣어요."]),
      py_task('concat-months', '두 달 자료를 위아래로 이어요',
        '`pd.concat([표1, 표2])`는 열 이름이 같은 표를 위아래로 이어요.\n'
        '원래 행 번호를 그대로 가져와서 번호가 겹쳐요.\n'
        '`ignore_index=True`를 넣으면 0부터 새로 번호를 매겨요.',
        '먼저 실행해서 세 행 수와 왼쪽의 행 번호를 보세요.\n'
        '번호가 0부터 다시 시작하는 곳이 있죠?\n'
        'concat 괄호의 리스트 뒤에 `, ignore_index=True`를 넣으세요.\n'
        '다시 실행해서 행 번호를 비교해요.',
        '''
        import pandas as pd

        # 9월과 10월 주문이에요. 열 이름과 순서가 같아요.
        month9 = pd.read_csv('data/orders_09.csv')
        month10 = pd.read_csv('data/orders_10.csv')
        # 두 표를 리스트에 담아 위아래로 이어요.
        both = pd.concat([month9, month10])
        # 두 달의 행 수와 이은 표의 행 수예요.
        print(len(month9), len(month10), len(both))
        # 표 왼쪽의 행 번호를 보세요.
        print(both)
        ''',
        'pd.concat([month9, month10])', 'pd.concat([month9, month10], ignore_index=True)',
        files=MONTHS, scenarios=MONTH_SCENARIOS, compare=['both'],
        wrong=[('pd.concat([month9, month10])', 'pd.concat([month9, month10], axis=1)'),
               ('pd.concat([month9, month10])', 'pd.merge(month9, month10)'),
               ('pd.concat([month9, month10])', 'pd.concat([month10, month9], ignore_index=True)')],
        caution='`axis=1`을 넣으면 위아래가 아니라 옆으로 붙어요.',
        hints=['`pd.concat([month9, month10], ignore_index=True)`로 바꿔요.']),
      py_task('month-report', '도전 · 두 달 주문에 고객 정보 붙이기',
        '이어 붙이기, how, 중복 키를 함께 써요.\n'
        '고객 정보를 붙인 뒤에도 행 수는 주문 수와 같아야 해요.',
        '준비 코드는 두 달 주문에 고객 정보를 붙여 report.csv로 저장해요.\n'
        '먼저 실행해서 두 행 수를 비교하세요.\n'
        '주문이 빠지거나 두 번 들어가지 않게 고치세요. 고객 정보가 없으면 빈칸으로 둬요.\n'
        '고칠 곳은 직접 찾아보세요.',
        '''
        import pandas as pd

        # 두 달 주문을 읽어 위아래로 이어요.
        month9 = pd.read_csv('data/orders_09.csv')
        month10 = pd.read_csv('data/orders_10.csv')
        orders = pd.concat([month9, month10], ignore_index=True)
        # 고객 표를 읽어요.
        customers = pd.read_json('data/customers.json')
        # 고객 정보를 붙여요.
        merged = pd.merge(orders, customers, on='customer_id')
        # 붙이기 전과 뒤의 행 수예요. 같아야 해요.
        print(len(orders), len(merged))
        # 등급이 빈칸인 주문 수예요.
        print(merged['grade'].isna().sum())
        # 정해진 이름으로 행 번호 없이 저장해요.
        merged.to_csv('report.csv', index=False)
        ''',
        "# 고객 정보를 붙여요.\nmerged = pd.merge(orders, customers, on='customer_id')",
        "# 같은 고객이 여러 번 있으면 맨 위 행만 남겨요.\n"
        "customers = customers.drop_duplicates(subset='customer_id')\n"
        "# 고객 정보를 붙여요.\nmerged = pd.merge(orders, customers, on='customer_id', how='left')",
        files={**MONTHS, 'data/customers.json': REPORT_CUSTOMERS}, scenarios=REPORT_SCENARIOS,
        compare=['merged'], challenge=True,
        wrong=[("merged = pd.merge(orders, customers, on='customer_id')",
                "merged = pd.merge(orders, customers, on='customer_id', how='left')"),
               ("merged = pd.merge(orders, customers, on='customer_id')",
                "customers = customers.drop_duplicates(subset='customer_id')\n"
                "merged = pd.merge(orders, customers, on='customer_id')")],
        caution='how만 고치면 중복 고객 때문에 행 수가 주문 수보다 많아져요.',
        hints=['행 수가 줄어든 이유와 늘어난 이유가 따로 있어요. 고객 파일도 살펴보세요.',
               "merge 앞에서 고객 중복을 지우고, merge에 `how='left'`를 넣어요."]),
      py_task('member-types', '도전 · 이름도 자료형도 다른 키',
        'left_on·right_on과 astype을 함께 써요.\n'
        '오류를 하나 고치면 다음 오류가 나올 수 있어요.',
        '매장 주문에 회원 정보를 붙여 member_orders.csv로 저장해요.\n'
        '주문은 모두 남기고, 회원 정보가 없으면 빈칸으로 두세요.\n'
        '오류가 나면 마지막 줄을 읽고 하나씩 고치세요.\n'
        '두 파일의 키 열은 「함께 제공한 파일」에서 확인해요.',
        '''
        import pandas as pd

        # 매장 주문이에요. 회원이 아니면 비회원으로 적었어요.
        orders = pd.read_csv('data/shop_orders.csv')
        # 회원 파일이에요. 회원 번호를 따옴표 없는 숫자로 적었어요.
        members = pd.read_json('data/shop_members.json')
        # 주문은 모두 남기고 회원 정보를 붙여요.
        merged = pd.merge(orders, members, on='customer_id', how='left')
        # 붙이기 전과 뒤의 행 수예요.
        print(len(orders), len(merged))
        # 등급이 빈칸인 주문 수예요.
        print(merged['grade'].isna().sum())
        # 정해진 이름으로 행 번호 없이 저장해요.
        merged.to_csv('member_orders.csv', index=False)
        ''',
        "# 주문은 모두 남기고 회원 정보를 붙여요.\nmerged = pd.merge(orders, members, on='customer_id', how='left')",
        "# 회원 번호를 글자로 바꿔 주문 키와 자료형을 맞춰요.\n"
        "members['member_no'] = members['member_no'].astype(str)\n"
        "# 주문은 모두 남기고 회원 정보를 붙여요.\n"
        "merged = pd.merge(orders, members, left_on='customer_id', right_on='member_no', how='left')",
        files=shop_members, scenarios=shop_member_scenarios, compare=['merged'], challenge=True,
        wrong=[("merged = pd.merge(orders, members, on='customer_id', how='left')",
                "merged = pd.merge(orders, members, left_on='customer_id', right_on='member_no', how='left')"),
               ("merged = pd.merge(orders, members, on='customer_id', how='left')",
                "orders['customer_id'] = orders['customer_id'].astype(int)\n"
                "merged = pd.merge(orders, members, left_on='customer_id', right_on='member_no', how='left')")],
        caution='키 이름만 고치면 자료형이 달라 ValueError가 나요.',
        hints=['회원 파일의 키 열은 member_no예요. 번호가 정수로 읽혀요.',
               "`members['member_no'] = members['member_no'].astype(str)`를 넣고 `left_on`, `right_on`을 써요."]),
    ])
