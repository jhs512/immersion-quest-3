"""aice-data-types: CSV를 읽고 자료형 점검하기 (AICE Associate 5번째 수업).

Small original order tables. Every scenario changes rows, values, blanks or header spacing so a
memorized screen cannot pass, and each listed mistake is a real beginner slip proven to fail.
"""
from certification_course.kit import py_task
from principles_course.common import code, lesson

SOURCES = ['https://aice.study/info/aice/asso', 'https://aice.study/certi/examGuide']

# Base order table: zero-padded codes, quoted thousands, '개' units, blanks and 모름.
ORDERS = code('''
    order_id,channel,price,quantity,minutes
    007,web,"1,200",2개,15
    012,app,800,1개,모름
    031,web,"2,500",3개,
    044,app,"1,050",1개,20
    105,web,950,4개,8
    120,app,"3,000",2개,모름
''')
ORDERS_B = code('''
    order_id,channel,price,quantity,minutes
    003,app,"2,100",1개,30
    018,web,700,5개,
    027,app,"1,400",2개,12
    090,web,"4,800",1개,모름
    101,app,650,3개,25
''')
ORDERS_C = code('''
    order_id,channel,price,quantity,minutes
    001,web,"1,000",1개,10
    002,web,"1,500",2개,미상
    009,app,900,6개,
    015,app,"12,300",1개,
    040,web,500,10개,5
    077,app,"2,250",3개,모름
    099,web,"1,800",2개,18
''')
ORDER_SCENARIOS = [{'files': {'data/orders.csv': ORDERS_B}}, {'files': {'data/orders.csv': ORDERS_C}}]

# Tables whose column types differ from the base, so a remembered dtypes list fails.
TYPES_B = code('''
    order_id,channel,price,quantity,minutes
    003,app,700,1,30
    018,web,650,5,
    027,app,900,2,12
''')
TYPES_C = code('''
    order_id,channel,price,quantity,minutes
    001,web,"1,000",1개,10
    002,web,"1,500",2개,7
    009,app,900,6개,4
    040,web,500,10개,5
''')

# Header spacing differs in every file.
BRANCH = code('''
    order_id, channel , price,quantity
    007,web,1200,2
    012,app,800,1
    031,web,2500,3
    044,app,1050,1
''')
BRANCH_B = code('''
    order_id,channel,price ,quantity
    003,app,2100,1
    018,web,700,5
    027,app,1400,2
''')
BRANCH_C = code('''
    order_id ,  channel,  price  ,quantity
    001,web,1000,1
    002,web,1500,2
    009,app,900,6
    040,web,500,10
    077,app,2250,3
''')

# Prices mixing thousands, 문의/협의 and blanks keep the whole column as text.
QUOTES = code('''
    order_id,channel,price
    007,web,"1,200"
    012,app,문의
    031,web,"2,500"
    044,app,950
    105,web,
    120,app,"3,000"
''')
QUOTES_B = code('''
    order_id,channel,price
    003,app,"2,100"
    018,web,700
    027,app,문의
    090,web,"4,800"
''')
QUOTES_C = code('''
    order_id,channel,price
    001,web,"1,000"
    002,web,"1,500"
    009,app,협의
    015,app,"12,300"
    040,web,500
    077,app,
    099,web,문의
''')

# Codes with leading zeros next to a real number column.
CODES = code('''
    order_id,channel,quantity
    007,web,2
    012,app,1
    031,web,3
    105,app,4
''')
CODES_B = code('''
    order_id,channel,quantity
    0003,app,5
    0018,web,1
    0270,app,2
''')
CODES_C = code('''
    order_id,channel,quantity
    009,web,1
    010,web,7
    099,app,2
    100,app,3
    008,web,6
''')


def build():
    orders = {'data/orders.csv': ORDERS}
    return lesson('aice-data-types', 'CSV를 읽고 자료형 점검하기',
        'CSV를 읽고 숫자로 읽히지 않은 열을 찾아 고쳐요. 저장한 파일도 다시 읽어 확인해요. '
        '필수 문제 8개와 선택 도전 2개예요.', SOURCES, [
      py_task('file-path', '파일이 있는 폴더까지 적어요',
        'CSV는 쉼표로 칸을 나눈 글자 파일이에요.\n`pd.read_csv`는 CSV 파일을 읽어 표로 만들어요.\n'
        '괄호 안에 적는 파일 위치를 경로라고 해요. 경로는 main.py가 있는 폴더에서 시작해요.',
        '자, 먼저 코드 실행을 누르세요. 오류의 마지막 줄에서 찾지 못한 파일 이름을 읽어요.\n'
        '자료는 data 폴더 안에 있어요. 폴더와 파일 이름은 /로 이어요.\n'
        '경로를 `\'data/orders.csv\'`로 바꾸고 다시 실행하세요.\n'
        '파일 내용은 문제 아래 「함께 제공한 파일」에서 볼 수 있어요.',
        '''
        import pandas as pd

        # 직접 만든 주문 자료예요. 실제 고객 자료가 아니에요.
        # 괄호 안의 경로에서 CSV 파일을 찾아 읽어요.
        df = pd.read_csv('orders.csv')
        # 표의 크기와 앞의 세 행을 확인해요.
        print(df.shape)
        result = df.head(3)
        print(result)
        ''',
        "'orders.csv'", "'data/orders.csv'", files=orders, scenarios=ORDER_SCENARIOS, compare=['result'],
        wrong=[("'orders.csv'", "'data/orders'"), ("'orders.csv'", "'data/order.csv'")],
        caution='폴더 이름을 빼면 파일 이름이 맞아도 찾지 못해요.',
        hints=["`pd.read_csv('data/orders.csv')`로 바꿔요. 확장자 .csv도 적어요."]),
      py_task('dtypes', '숫자처럼 보여도 글자일 수 있어요',
        '값의 종류를 자료형이라고 해요. 정수는 int64, 소수는 float64, 글자는 str이에요.\n'
        'pandas는 열마다 자료형을 하나 정해요. 숫자가 아닌 값이 한 칸만 섞여도 그 열은 str이 돼요.\n'
        '`df.dtypes`는 열마다 그 자료형을 보여 줘요.',
        '먼저 실행해서 표의 값을 보세요.\nresult 줄의 `df.head(3)`을 `df.dtypes`로 바꾸세요.\n'
        '숫자처럼 보이는데 str인 열을 찾아보세요. 처음 본 표에서 그 열에 섞인 글자를 찾아요.\n'
        'pandas 버전에 따라 str 대신 object로도 보여요. 맨 아래 dtype 줄은 목록 자체의 자료형이에요.',
        '''
        import pandas as pd

        # 직접 만든 주문 자료예요. 실제 고객 자료가 아니에요.
        df = pd.read_csv('data/orders.csv')
        # 점검할 내용을 result에 담아요.
        result = df.head(3)
        # 담은 값을 화면에 보여 줘요.
        print(result)
        ''',
        'result = df.head(3)', 'result = df.dtypes', files=orders, compare=['result'],
        scenarios=[{'files': {'data/orders.csv': TYPES_B}}, {'files': {'data/orders.csv': TYPES_C}}],
        wrong=[('result = df.head(3)', 'result = df.dtypes()'), ('result = df.head(3)', 'result = df.dtype')],
        caution='`dtypes` 뒤에 괄호를 붙이면 TypeError가 나요.',
        hints=['`result = df.dtypes`로 바꿔요. shape처럼 괄호는 붙이지 않아요.']),
      py_task('info', '빈칸이 아닌 값의 개수를 세어요',
        '`df.info()`는 표의 요약을 한 번에 보여 줘요.\n'
        '`RangeIndex` 줄의 entries 앞 숫자가 행 수예요. 열마다 자료형과 Non-Null Count도 나와요.\n'
        'Non-Null Count는 빈칸이 아닌 값의 개수예요.',
        '먼저 실행해서 minutes의 값과 자료형 목록을 보세요.\n`print(df.dtypes)` 줄을 `df.info()`로 바꾸세요.\n'
        'minutes의 Non-Null Count를 행 수와 비교해요.\n'
        'NaN과 모름 중 어느 쪽이 빈칸으로 세어졌는지 확인하세요.',
        '''
        import pandas as pd

        # 직접 만든 주문 자료예요. 실제 고객 자료가 아니에요.
        df = pd.read_csv('data/orders.csv')
        # minutes 열의 값을 모두 봐요. NaN은 빈칸이에요.
        print(df['minutes'])
        # 열의 정보를 화면에 보여 줘요.
        print(df.dtypes)
        ''',
        'print(df.dtypes)', 'df.info()', files=orders, scenarios=ORDER_SCENARIOS,
        wrong=[('print(df.dtypes)', 'print(df.info())'), ('print(df.dtypes)', 'df.info')],
        caution='`info()`를 print로 감싸면 끝에 None이 한 줄 더 나와요.',
        hints=['info는 괄호를 붙여야 실행돼요. 스스로 출력하니 `df.info()` 한 줄이면 돼요.']),
      py_task('thousands', '쉼표 섞인 가격을 숫자로 읽어요',
        '`sum()`은 열의 값을 모두 더해요.\n글자 열이면 더하지 않고 글자를 이어 붙여요.\n'
        "`thousands=','`는 쉼표를 천 단위 표시로 읽게 해요.",
        '먼저 실행해서 합계가 어떻게 나오는지 보세요.\n'
        '가격 글자가 사이 없이 붙어 나와요. 첫 가격부터 끊어 읽어 보세요.\n'
        "read_csv의 경로 뒤에 `, thousands=','`를 넣으세요.\n"
        '다시 실행해서 두 합계를 비교해요.',
        '''
        import pandas as pd

        # 파일에는 "1,200"처럼 따옴표로 감싸 한 칸으로 둬요.
        # 읽는 규칙은 경로 뒤에 이름 붙은 인자로 더해요.
        df = pd.read_csv('data/orders.csv')
        # price 열의 값을 모두 더해요.
        result = df['price'].sum()
        # 합계를 확인해요. 글자 열이면 값이 이어 붙어요.
        print(result)
        ''',
        "pd.read_csv('data/orders.csv')", "pd.read_csv('data/orders.csv', thousands=',')",
        files=orders, scenarios=ORDER_SCENARIOS, compare=['result'],
        wrong=[("result = df['price'].sum()", "result = int(df['price'].sum())"),
               ("pd.read_csv('data/orders.csv')", "pd.read_csv('data/orders.csv', ',')")],
        caution='이어 붙인 글자를 `int()`로 감싸면 ValueError가 나요.',
        hints=["`pd.read_csv('data/orders.csv', thousands=',')`로 읽어요."]),
      py_task('to-numeric', '숫자가 아닌 값은 빈칸으로 바꿔요',
        '`pd.to_numeric`은 열의 값을 숫자로 바꿔요.\n숫자로 못 읽는 값이 하나라도 있으면 오류가 나요.\n'
        "`errors='coerce'`는 그런 값을 NaN(빈칸)으로 바꿔요.",
        '먼저 실행해서 오류의 마지막 줄을 읽으세요. `Unable to parse string`은 숫자로 못 읽었다는 뜻이에요.\n'
        '`position` 뒤 숫자는 0부터 센 자리예요. 위에 출력된 값의 왼쪽 번호와 맞춰 보세요.\n'
        "to_numeric 괄호 끝에 `, errors='coerce'`를 넣으세요.\n"
        '다시 실행해서 NaN이 된 값과 맨 아래 dtype을 확인해요.',
        '''
        import pandas as pd

        # minutes에는 빈칸과 모름이 섞여 있어요.
        df = pd.read_csv('data/orders.csv')
        # 바꾸기 전 값을 먼저 봐요. 왼쪽 번호는 0부터 세요.
        print(df['minutes'])
        # minutes 열을 숫자로 바꿔 다시 담아요.
        df['minutes'] = pd.to_numeric(df['minutes'])
        # 바꾼 열과 자료형을 확인해요. NaN이 섞인 숫자 열은 float64가 돼요.
        result = df['minutes']
        print(result)
        ''',
        "pd.to_numeric(df['minutes'])", "pd.to_numeric(df['minutes'], errors='coerce')",
        files=orders, scenarios=ORDER_SCENARIOS, compare=['result'],
        wrong=[("pd.to_numeric(df['minutes'])", "pd.to_numeric(df['minutes'].str.replace('모름', '0'))"),
               ("pd.to_numeric(df['minutes'])", "pd.to_numeric(df['minutes'], errors='ignore')")],
        caution='모름을 0으로 바꾸면 모르는 시간이 0분이 돼요.',
        hints=["`pd.to_numeric(df['minutes'], errors='coerce')`로 바꿔요."]),
      py_task('astype', '정리한 글자를 정수로 바꿔요',
        '`.str`을 붙이면 열의 값마다 글자 메서드를 써요.\n개를 지워도 자료형은 여전히 글자예요.\n'
        '`astype(int)`는 열을 정수 자료형으로 바꿔요.',
        "먼저 실행해서 합계가 어떻게 나오는지 보세요.\n`replace('개', '')` 바로 뒤에 `.astype(int)`를 붙이세요.\n"
        '다시 실행해서 두 합계를 비교해요.',
        '''
        import pandas as pd

        # quantity에는 2개처럼 개가 붙어 있어요.
        df = pd.read_csv('data/orders.csv')
        # .str.replace로 값마다 개를 지우고 다시 담아요.
        df['quantity'] = df['quantity'].str.replace('개', '')
        # 수량을 모두 더해 확인해요.
        result = df['quantity'].sum()
        print(result)
        ''',
        "df['quantity'].str.replace('개', '')", "df['quantity'].str.replace('개', '').astype(int)",
        files=orders, scenarios=ORDER_SCENARIOS, compare=['result', 'df'],
        wrong=[("result = df['quantity'].sum()", "df['quantity'].astype(int)\nresult = df['quantity'].sum()"),
               ("result = df['quantity'].sum()", "result = int(df['quantity'].sum())"),
               ("result = df['quantity'].sum()", "result = df['quantity'].astype(int).sum()")],
        caution='astype 결과를 열에 다시 담지 않으면 df는 그대로예요.',
        hints=["`df['quantity'].str.replace('개', '').astype(int)`처럼 이어 써요."]),
      py_task('column-names', '열 이름의 공백을 지워요',
        '`df.columns`는 표의 열 이름 목록이에요.\n이름 앞뒤에 공백이 붙으면 다른 이름이 돼요.\n'
        '`df.columns.str.strip()`은 모든 열 이름의 앞뒤 공백을 지워요.',
        '먼저 실행해서 열 이름 목록과 오류를 보세요. `KeyError`는 그런 이름의 열이 없다는 뜻이에요.\n'
        '목록의 따옴표 안을 보면 이름 앞뒤의 공백이 보여요.\n'
        '공백을 지우는 주석 아래에 `df.columns = df.columns.str.strip()`을 넣으세요.\n'
        '다시 실행해서 price 열과 맨 아래 새 목록을 보세요.',
        '''
        import pandas as pd

        # 다른 지점에서 받은 주문 자료예요.
        df = pd.read_csv('data/branch.csv')
        # 지우기 전의 열 이름 목록을 먼저 확인해요.
        print(df.columns)
        # 이 아래에서 열 이름의 앞뒤 공백을 지워요.
        # 가격 열만 꺼내 확인해요.
        result = df['price']
        print(result)
        # 지운 뒤의 열 이름 목록도 확인해요.
        print(df.columns)
        ''',
        '# 이 아래에서 열 이름의 앞뒤 공백을 지워요.',
        '# 이 아래에서 열 이름의 앞뒤 공백을 지워요.\ndf.columns = df.columns.str.strip()',
        files={'data/branch.csv': BRANCH}, compare=['result'],
        scenarios=[{'files': {'data/branch.csv': BRANCH_B}}, {'files': {'data/branch.csv': BRANCH_C}}],
        wrong=[("result = df['price']", "result = df[' price']"),
               ('# 이 아래에서 열 이름의 앞뒤 공백을 지워요.',
                '# 이 아래에서 열 이름의 앞뒤 공백을 지워요.\ndf.columns = df.columns.strip()')],
        caution='공백까지 따라 적으면 다른 파일에서 또 KeyError가 나요.',
        hints=['주석 아래에 `df.columns = df.columns.str.strip()`을 넣어요. columns 뒤의 .str을 빼먹지 마세요.']),
      py_task('save-csv', '저장한 파일을 다시 읽어 확인해요',
        '`to_csv`는 표를 CSV 파일로 저장해요.\n'
        '표 왼쪽의 0, 1, 2는 행 번호(인덱스)예요. 따로 말하지 않으면 함께 저장돼요.\n'
        '`index=False`를 넣으면 행 번호는 빼고 저장해요.',
        '먼저 실행해서 다시 읽은 표의 크기와 첫 열을 보세요.\n'
        'Unnamed: 0은 이름 없이 저장된 행 번호 열이에요.\n'
        'to_csv의 파일 이름 뒤에 `, index=False`를 넣으세요.\n'
        '다시 실행해서 열 수와 첫 열을 비교해요. 다시 읽는 줄은 그대로 두세요.',
        '''
        import pandas as pd

        # 쉼표 숫자를 숫자로 읽어요.
        df = pd.read_csv('data/orders.csv', thousands=',')
        # 정해진 이름 result.csv로 저장해요.
        df.to_csv('result.csv')
        # 저장한 파일을 다시 읽어요.
        saved = pd.read_csv('result.csv')
        # 다시 읽은 표의 크기와 앞부분을 확인해요.
        print(saved.shape)
        print(saved.head(3))
        ''',
        "df.to_csv('result.csv')", "df.to_csv('result.csv', index=False)",
        files=orders, scenarios=ORDER_SCENARIOS, compare=['saved'],
        wrong=[("saved = pd.read_csv('result.csv')", "saved = pd.read_csv('result.csv', index=False)"),
               ("df.to_csv('result.csv')", "df.to_csv('result.csv', header=False)")],
        caution='index=False는 읽을 때가 아니라 저장할 때 넣어요.',
        hints=["`df.to_csv('result.csv', index=False)`로 저장해요."]),
      py_task('price-total', '도전 · 쉼표와 문의가 섞인 가격 합계',
        '쉼표 지우기, coerce, 합계를 조합해요.\n숫자가 아닌 값이 섞이면 열 전체가 글자로 남아요.',
        '먼저 실행해서 NaN이 된 가격을 보세요. 이번 자료는 prices.csv예요.\n'
        'NaN이 된 행의 원래 값은 「함께 제공한 파일」에서 찾아요.\n'
        '쉼표가 있는 가격도 합계에 넣으세요. 문의처럼 숫자가 아닌 값만 NaN으로 두세요.\n'
        '제출 전에 쉼표 가격이 숫자로 나오는지 확인하세요.',
        '''
        import pandas as pd

        # 앞 문제와 다른 자료예요. 가격에 쉼표, 문의, 빈칸이 섞였어요.
        df = pd.read_csv('data/prices.csv')
        # 숫자로 못 읽는 값은 NaN으로 바꿔 다시 담아요.
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        # 바뀐 가격을 먼저 확인해요.
        print(df['price'])
        # 합계는 NaN을 빼고 더해요.
        result = df['price'].sum()
        print(result)
        ''',
        "pd.to_numeric(df['price'], errors='coerce')", "pd.to_numeric(df['price'].str.replace(',', ''), errors='coerce')",
        files={'data/prices.csv': QUOTES}, compare=['result'], challenge=True,
        scenarios=[{'files': {'data/prices.csv': QUOTES_B}}, {'files': {'data/prices.csv': QUOTES_C}}],
        wrong=[("pd.read_csv('data/prices.csv')", "pd.read_csv('data/prices.csv', thousands=',')"),
               ("pd.to_numeric(df['price'], errors='coerce')", "pd.to_numeric(df['price'].str.replace(',', ''))"),
               ("pd.to_numeric(df['price'], errors='coerce')",
                "pd.to_numeric(df['price'].replace(',', ''), errors='coerce')")],
        caution='coerce는 쉼표가 있는 숫자도 NaN으로 바꿔요.',
        hints=["문의가 섞인 열에서는 `thousands=','`도 쉼표를 못 지워요.",
               "to_numeric 괄호 안의 `df['price']` 바로 뒤에 `.str.replace(',', '')`를 붙여요."]),
      py_task('code-roundtrip', '도전 · 다시 읽어도 007을 지켜요',
        "주문 번호 007은 계산하지 않는 코드예요. 숫자로 읽으면 앞자리 0이 사라져요.\n"
        "`dtype={'order_id': str}`은 그 열을 글자로 읽게 해요.\n"
        '읽을 때 넣는 인자라 열을 보는 `df.dtypes`와 달리 s가 없어요.',
        '준비 코드는 codes.csv를 읽어 저장하고 다시 읽어요.\n다시 읽은 주문 번호도 앞자리 0을 지키게 하세요.\n'
        '다른 열의 자료형은 바꾸지 마세요.\n고칠 줄은 직접 찾아보세요.',
        '''
        import pandas as pd

        # dtype으로 order_id 열을 글자로 읽어요.
        df = pd.read_csv('data/codes.csv', dtype={'order_id': str})
        # 두 열만 골라 행 번호 없이 저장해요.
        df[['order_id', 'quantity']].to_csv('result.csv', index=False)
        # 저장한 파일을 다시 읽어요.
        saved = pd.read_csv('result.csv')
        # 다시 읽은 주문 번호를 확인해요.
        result = saved['order_id']
        print(result)
        ''',
        "saved = pd.read_csv('result.csv')", "saved = pd.read_csv('result.csv', dtype={'order_id': str})",
        files={'data/codes.csv': CODES}, compare=['result', 'saved'], challenge=True,
        scenarios=[{'files': {'data/codes.csv': CODES_B}}, {'files': {'data/codes.csv': CODES_C}}],
        wrong=[("result = saved['order_id']", "result = saved['order_id'].astype(str)"),
               ("saved = pd.read_csv('result.csv')", "saved = pd.read_csv('result.csv', dtype=str)")],
        caution='`astype(str)`로는 이미 사라진 앞자리 0이 돌아오지 않아요.',
        hints=['저장한 파일에는 007이 그대로 있어요. 다시 읽는 줄을 보세요.',
               "다시 읽는 read_csv에도 `dtype={'order_id': str}`을 넣어요."]),
    ])
