"""aice-target-features: choose the target y and the input columns X (AICE Associate 10th lesson).

Four small original member tables, each with two changed copies (other rows, ids and values):
- members.csv: one regression target (amount), a numeric id, a text grade and a float minutes column,
  so include='int' loses a column, and visits == 0 rows in the middle so cutting y from the front
  pairs the wrong answers.
- next_month.csv: both a regression candidate (amount, 0 when nothing was bought) and a 0/1 target
  (bought). For bought, amount is a result known only next month, so it leaks the answer.
- members_points.csv: points earned by next month's purchase (amount / 100, plus 100 for gold),
  whose correlation with amount is near 1 while the real inputs stay far below it.
- members_blank.csv: blanks in an input (age) and in the target (amount) on different rows, so
  dropping blanks from X and y separately can leave equal row counts that are paired wrongly.
The changed members and next_month tables add one numeric input (coupons) or one text column
(channel), so a hand-written column list or dropping grade by name fails where select_dtypes passes.
"""
from certification_course.kit import py_task
from principles_course.common import code, lesson

SOURCES = ['https://aice.study/info/aice/asso',
           'https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.drop.html',
           'https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.select_dtypes.html']

# Regression table. Visits are 0 on rows 2 and 6, so a filter removes rows from the middle.
MEMBERS = code('''
    member_id,age,visits,minutes,grade,amount
    101,34,6,42.5,gold,58000
    102,27,2,12.0,bronze,15000
    103,45,0,0.0,silver,9000
    104,31,4,30.5,silver,36000
    105,52,8,55.0,gold,71000
    106,23,1,6.5,bronze,8000
    107,38,0,0.0,bronze,12000
    108,41,5,38.0,silver,44000
    109,29,3,21.5,gold,30000
    110,36,7,47.0,gold,62000
''')

# Fewer rows; the first row has no visits. One more numeric input (coupons used last month),
# so a hand-written list of the base table's columns misses it.
MEMBERS_B = code('''
    member_id,age,visits,minutes,coupons,grade,amount
    201,26,0,0.0,0,bronze,7000
    202,48,5,36.5,2,gold,52000
    203,33,3,18.0,1,silver,24000
    204,40,6,44.0,3,silver,49000
    205,22,2,9.5,0,bronze,13000
    206,57,9,61.0,4,gold,83000
    207,35,0,0.0,1,silver,11000
    208,30,4,27.5,2,bronze,31000
''')

# More rows; three members without visits. One more text column (channel), so dropping grade by
# name instead of keeping numeric columns leaves text in X.
MEMBERS_C = code('''
    member_id,age,visits,minutes,channel,grade,amount
    301,39,5,33.5,app,silver,41000
    302,25,1,7.0,web,bronze,9000
    303,44,7,50.5,app,gold,66000
    304,31,0,0.0,web,bronze,10000
    305,28,3,19.0,app,silver,27000
    306,50,8,58.0,web,gold,74000
    307,36,2,13.5,app,bronze,16000
    308,42,0,0.0,web,silver,8000
    309,33,4,29.0,web,silver,35000
    310,47,6,41.5,app,gold,57000
    311,24,0,0.0,app,bronze,6000
    312,38,5,35.0,web,gold,48000
''')

# Two target candidates. amount is 0 exactly when bought is 0.
NEXT = code('''
    member_id,age,visits,minutes,grade,amount,bought
    601,31,5,34.5,silver,41000,1
    602,26,1,6.0,bronze,0,0
    603,47,7,51.0,gold,66000,1
    604,38,0,0.0,silver,0,0
    605,29,3,22.5,bronze,18000,1
    606,55,2,11.5,gold,0,0
    607,34,6,40.0,silver,52000,1
    608,23,4,27.0,bronze,23000,1
    609,42,1,8.5,silver,0,0
    610,36,8,57.5,gold,73000,1
''')

# Fewer rows and more members who did not buy. One more numeric input known last month (coupons).
NEXT_B = code('''
    member_id,age,visits,minutes,coupons,grade,amount,bought
    901,44,2,14.5,1,silver,0,0
    902,30,6,45.0,3,gold,58000,1
    903,25,1,5.5,0,bronze,0,0
    904,37,0,0.0,0,silver,0,0
    905,49,4,31.0,2,gold,39000,1
    906,28,3,20.5,1,bronze,0,0
    907,33,5,36.5,2,silver,47000,1
    908,41,1,9.0,0,bronze,0,0
''')

# More rows and more members who bought. One more text column (channel).
NEXT_C = code('''
    member_id,age,visits,minutes,channel,grade,amount,bought
    1001,35,4,28.5,app,silver,33000,1
    1002,22,0,0.0,web,bronze,0,0
    1003,46,7,49.0,app,gold,69000,1
    1004,39,2,15.0,web,silver,0,0
    1005,27,5,37.5,app,bronze,26000,1
    1006,53,3,22.0,web,gold,41000,1
    1007,31,1,7.5,web,bronze,0,0
    1008,44,6,43.0,app,silver,54000,1
    1009,29,2,12.5,app,bronze,14000,1
    1010,37,8,60.5,web,gold,82000,1
    1011,24,1,4.0,app,bronze,0,0
    1012,50,4,30.0,web,gold,38000,1
''')

# points = amount / 100, plus 100 for gold: correlation with amount stays near 1 (0.98 or more).
POINTS = code('''
    member_id,age,visits,minutes,grade,points,amount
    501,33,4,25.5,silver,420,42000
    502,46,2,40.0,gold,850,75000
    503,28,6,18.5,bronze,180,18000
    504,39,1,9.0,silver,610,61000
    505,52,5,33.0,gold,380,28000
    506,24,3,52.5,bronze,330,33000
    507,41,7,22.0,silver,240,24000
    508,35,2,14.5,bronze,560,56000
    509,30,8,47.0,gold,990,89000
    510,44,0,0.0,silver,50,5000
''')

POINTS_B = code('''
    member_id,age,visits,minutes,grade,points,amount
    701,29,3,31.0,bronze,270,27000
    702,51,6,12.5,gold,740,64000
    703,37,1,44.5,silver,390,39000
    704,26,5,20.0,silver,150,15000
    705,43,2,9.5,gold,460,36000
    706,32,7,36.0,bronze,710,71000
    707,48,4,27.5,silver,480,48000
    708,22,0,0.0,bronze,30,3000
''')

POINTS_C = code('''
    member_id,age,visits,minutes,grade,points,amount
    801,45,2,16.0,silver,510,51000
    802,27,6,43.5,bronze,220,22000
    803,38,4,11.0,gold,780,68000
    804,31,1,29.5,silver,140,14000
    805,54,7,38.0,gold,460,36000
    806,23,3,50.0,bronze,410,41000
    807,40,5,8.5,silver,630,63000
    808,36,0,0.0,bronze,40,4000
    809,29,8,46.5,gold,870,77000
    810,49,2,21.0,silver,260,26000
    811,34,6,33.5,bronze,450,45000
    812,42,3,18.0,gold,650,55000
''')

# Base: age blank on row 3, amount blank on row 7. Dropping each side alone leaves 9 and 9 rows.
BLANK = code('''
    member_id,age,visits,minutes,grade,amount
    121,32,5,37.0,silver,46000
    122,26,2,11.5,bronze,14000
    123,48,6,44.5,gold,63000
    124,,3,20.0,silver,27000
    125,37,1,6.5,bronze,9000
    126,55,7,52.0,gold,78000
    127,29,4,26.5,bronze,31000
    128,41,2,13.0,silver,
    129,34,8,58.5,gold,85000
    130,23,3,18.0,bronze,22000
''')

# Two age blanks and one amount blank.
BLANK_B = code('''
    member_id,age,visits,minutes,grade,amount
    221,45,4,30.5,gold,51000
    222,,2,12.0,bronze,13000
    223,31,5,35.5,silver,
    224,27,1,5.0,bronze,7000
    225,39,6,47.0,gold,66000
    226,,3,21.5,silver,29000
    227,52,7,53.5,gold,74000
    228,24,2,10.0,bronze,12000
''')

# One age blank and two amount blanks, the first on the very first row.
BLANK_C = code('''
    member_id,age,visits,minutes,grade,amount
    321,36,3,22.5,silver,
    322,28,5,34.0,bronze,38000
    323,47,7,50.5,gold,72000
    324,33,2,13.5,silver,17000
    325,,4,27.0,bronze,30000
    326,51,1,8.0,gold,11000
    327,25,6,41.5,bronze,49000
    328,42,3,19.5,silver,25000
    329,30,8,61.0,gold,88000
    330,38,2,14.0,silver,
    331,22,5,33.5,bronze,36000
    332,46,4,29.0,gold,43000
''')

# path, base table, changed tables, comment lines that explain the columns.
DATA = {
    'members': ('data/members.csv', MEMBERS, [MEMBERS_B, MEMBERS_C],
                '# visits는 지난달 방문 수, minutes는 지난달 머문 시간(분)이에요.\n'
                '# amount는 다음 달 구매 금액(원)이에요.\n'),
    'next': ('data/next_month.csv', NEXT, [NEXT_B, NEXT_C],
             '# amount는 다음 달 구매 금액(원)이에요. 안 샀으면 0이에요.\n'
             '# bought는 다음 달에 샀으면 1, 안 샀으면 0이에요.\n'),
    'points': ('data/members_points.csv', POINTS, [POINTS_B, POINTS_C],
               '# amount는 다음 달 구매 금액(원)이에요.\n'
               '# points는 다음 달 구매로 쌓인 포인트예요.\n'),
    'blank': ('data/members_blank.csv', BLANK, [BLANK_B, BLANK_C],
              '# amount는 다음 달 구매 금액(원)이에요.\n'
              '# age와 amount에 빈칸이 섞여 있어요.\n'),
}


def xy(id, title, principle, goal, body, before, after, *, data, compare, caution, hints, wrong=None,
       challenge=False):
    """One X/y experiment on a base table, graded on its two changed tables too."""
    path, base, changed, columns = DATA[data]
    header = ('import pandas as pd\n\n# 직접 만든 회원 자료예요. 실제 고객 자료가 아니에요.\n'
              f"df = pd.read_csv('{path}')\n" + columns)
    scenarios = [{'files': {path: table}} for table in changed]
    return py_task(id, title, principle, goal, header + '\n' + code(body), before, after, caution=caution,
                   hints=hints, scenarios=scenarios, files={path: base}, compare=compare, wrong=wrong,
                   challenge=challenge)


# The challenge's reference: drop the blank rows from df first, then split.
SPLIT_THEN_DROP = '''# 타깃은 amount예요. 정답 y로 꺼내요.
y = df['amount']
# id와 타깃을 빼서 입력 X를 만들어요.
X = df.drop(columns=['member_id', 'amount'])
# X에서 빈칸이 있는 행을 지워요.
X = X.dropna()'''

DROP_THEN_SPLIT = '''# 빈칸이 있는 행을 df에서 먼저 지워요.
df = df.dropna()
# 타깃은 amount예요. 정답 y로 꺼내요.
y = df['amount']
# id와 타깃을 빼서 입력 X를 만들어요.
X = df.drop(columns=['member_id', 'amount'])'''

# Shared ending: both row counts, then X and y with their index labels on the left, so equal
# counts with different labels (blanks dropped from X and y separately) show on screen.
REPORT = '''# 두 행 수를 비교해요. 수가 같아도 짝이 맞는지는 번호로 봐요.
print(X.shape[0], y.shape[0])
# X에 남은 행과 왼쪽 번호예요.
print(X)
# y에 남은 정답과 왼쪽 번호예요. X와 번호가 하나하나 같아야 짝이 맞아요.
# NaN은 빈칸이에요. 빈칸이 섞였던 열은 소수(float64)로 읽혀요.
print(y)
'''

BUY_INPUTS ="X = df.drop(columns=['member_id', 'amount', 'bought']).select_dtypes(include='number')"


def build():
    return lesson('aice-target-features', '입력 X와 정답 y 정하기',
        '모델이 맞힐 정답 y와 단서가 될 입력 X를 나눠요. 예측할 때 모르는 열은 X에서 빼요. '
        '필수 문제 8개와 선택 도전 2개예요.',
        SOURCES, [
        xy('target-kind', '회귀일까요, 분류일까요?',
            '타깃(target)은 모델이 맞힐 열이에요. 금액처럼 크기를 재는 숫자면 회귀(regression)예요.\n'
            '산다·안 산다처럼 종류 중 하나면 분류(classification)예요. 종류를 0·1로 적어도 분류예요.\n'
            '`nunique()`는 열에 서로 다른 값이 몇 종류인지 세요.',
            '자, 질문은 회원이 다음 달에 살지 말지예요.\n'
            '먼저 실행해서 amount의 값 종류 수와 값별 행 수를 보세요.\n'
            "target을 `'bought'`로 바꾸고 다시 실행하세요.\n"
            '두 결과를 비교해요. 0과 1 두 종류뿐이면 분류 타깃이에요.',
            '''
            # 질문: 회원이 다음 달에 살까요, 안 살까요?
            # 맞힐 열(타깃)의 이름이에요.
            target = 'amount'
            # 타깃에 서로 다른 값이 몇 개인지 세요.
            kinds = df[target].nunique()
            print(kinds)
            # 값마다 몇 행인지 봐요.
            print(df[target].value_counts())
            ''',
            "target = 'amount'", "target = 'bought'", data='next', compare=['target', 'kinds'],
            caution='`unique()`는 개수가 아니라 서로 다른 값의 목록을 돌려줘요.',
            hints=["`target = 'bought'`로 바꿔요. 열 이름은 따옴표로 감싸요."],
            wrong=[("'bought'\n# 타깃에 서로 다른 값이 몇 개인지 세요.\nkinds = df[target].nunique()",
                    "'bought'\n# 타깃에 서로 다른 값이 몇 개인지 세요.\nkinds = df[target].unique()"),
                   ("'bought'\n# 타깃에 서로 다른 값이 몇 개인지 세요.\nkinds = df[target].nunique()",
                    "'bought'\n# 타깃에 서로 다른 값이 몇 개인지 세요.\nkinds = len(df[target])")]),
        xy('pick-y', '정답 y는 열 하나로 꺼내요',
            '정답 y는 타깃 열 하나예요. 행마다 정답이 하나씩 있죠.\n'
            '`df[target]`처럼 대괄호 한 겹이면 Series가 나와요.\n'
            '`df[[target]]`처럼 두 겹이면 열이 하나뿐인 표(DataFrame)예요.',
            '이번엔 다음 달 구매 금액을 맞히는 회귀 문제예요.\n'
            '먼저 실행해서 y의 크기(shape)와 앞의 세 행을 보세요. 크기에 숫자가 둘이죠?\n'
            'y 줄의 대괄호를 한 겹으로 바꾸고 다시 실행하세요.\n'
            '크기에 행 수만 남았는지 봐요. 맨 아래 Name은 꺼낸 열 이름이에요.',
            '''
            # 맞힐 열(타깃)의 이름이에요.
            target = 'amount'
            # 정답 y로 타깃 열을 꺼내요.
            y = df[[target]]
            # y의 크기(shape)예요. (행 수, 열 수) 순서예요.
            # Series면 열 수 없이 (행 수,)처럼 숫자 하나만 나와요.
            print(y.shape)
            # 앞의 세 행을 봐요.
            print(y.head(3))
            ''',
            'y = df[[target]]', 'y = df[target]', data='members', compare=['y'],
            caution="`df['target']`처럼 변수 이름에 따옴표를 붙이면 KeyError가 나요.",
            hints=['`y = df[target]`로 바꿔요. target에는 따옴표를 붙이지 않아요.'],
            wrong=[('y = df[[target]]', "y = df['target']"), ('y = df[[target]]', 'y = target')]),
        xy('drop-target', '입력 X에서 정답 열을 빼요',
            '입력 X는 모델이 보고 맞힐 단서 열들이에요.\n'
            '정답 열이 X에 남으면 시험지에 답을 적어 둔 셈이에요.\n'
            "`df.drop(columns=['열'])`은 그 열을 뺀 새 표를 돌려줘요. df는 그대로예요.",
            '먼저 실행해서 X의 열 이름과 두 표의 크기를 보세요.\n'
            "X 줄을 `X = df.drop(columns=['amount'])`로 바꾸세요.\n"
            '다시 실행해서 열 이름과 열 수를 비교해요.\n'
            'member_id 열은 뒤에서 따로 다뤄요.',
            '''
            # 타깃은 amount예요. 정답 y로 꺼내요.
            y = df['amount']
            # 입력 X예요. 지금은 표 전체를 그대로 써요.
            X = df
            # X의 열 이름을 봐요. 정답 열이 남았나요?
            # Index([...])는 pandas가 이름을 담는 목록이에요. 안의 이름만 보면 돼요.
            print(X.columns)
            # 원래 표와 X의 크기를 비교해요.
            print(df.shape, X.shape)
            ''',
            'X = df\n', "X = df.drop(columns=['amount'])\n", data='members', compare=['X', 'y'],
            caution='drop 결과를 X에 담지 않으면 정답 열이 X에 그대로 남아요.',
            hints=["`X = df.drop(columns=['amount'])`로 바꿔요."],
            wrong=[('X = df\n', "df.drop(columns=['amount'])\nX = df\n"),
                   ('X = df\n', "X = df[['amount']]\n")]),
        xy('drop-axis', 'drop에게 열이라고 알려 줘요',
            '표에는 두 방향(축, axis)이 있어요. axis=0은 행, axis=1은 열이에요.\n'
            'drop은 따로 말하지 않으면 표 왼쪽의 행 이름(인덱스)에서 찾아요.\n'
            '그래서 열을 뺄 땐 `axis=1`이나 `columns=`를 넣어요.',
            '먼저 실행해서 오류의 마지막 줄을 읽으세요.\n'
            '`not found in axis`는 그 축에서 이름을 못 찾았다는 뜻이에요.\n'
            "drop 괄호 안 `'amount'` 뒤에 `, axis=1`을 넣으세요.\n"
            '다시 실행해서 X의 열 이름을 확인해요.',
            '''
            # 타깃은 amount예요. 정답 y로 꺼내요.
            y = df['amount']
            # 정답 열을 빼서 입력 X를 만들어요.
            X = df.drop('amount')
            # X의 열 이름을 확인해요. 열 이름도 Index([...]) 목록에 담겨 나와요.
            print(X.columns)
            ''',
            "df.drop('amount')", "df.drop('amount', axis=1)", data='members', compare=['X', 'y'],
            caution="옛 예제의 `df.drop('amount', 1)`처럼 1만 넣으면 새 pandas에선 TypeError가 나요.",
            hints=["`df.drop('amount', axis=1)`로 바꿔요. `columns=['amount']`도 돼요."],
            wrong=[("df.drop('amount')", "df.drop('amount', 1)"),
                   ("df.drop('amount')", "df.drop('amount', axis=0)")]),
        xy('drop-id', 'id와 정답을 함께 빼요',
            'id는 회원마다 붙인 번호표예요. 숫자로 적혀도 크기에 뜻이 없어요.\n'
            '맞힐 값과 상관없는 열이라 입력 X에서 빼요.\n'
            '`columns=` 목록에 이름을 여럿 넣으면 한 번에 빠져요.',
            '먼저 실행해서 X에 남은 열과 앞의 세 행을 보세요.\n'
            "drop 목록의 `'amount'` 앞에 `'member_id', `를 넣으세요.\n"
            '다시 실행해서 열 이름과 앞의 세 행을 비교해요.',
            '''
            # 타깃은 amount예요. 정답 y로 꺼내요.
            y = df['amount']
            # 빼고 싶은 열 이름을 목록에 넣어요.
            X = df.drop(columns=['amount'])
            # X의 열 이름과 앞의 세 행을 확인해요.
            print(X.columns)
            print(X.head(3))
            ''',
            "columns=['amount']", "columns=['member_id', 'amount']", data='members', compare=['X', 'y'],
            caution='이름 사이 쉼표를 빼면 두 이름이 붙어 KeyError가 나요.',
            hints=["`df.drop(columns=['member_id', 'amount'])`로 바꿔요."],
            wrong=[("columns=['amount']", "columns=['member_id' 'amount']"),
                   ("columns=['amount']", "columns=['member_id']"),
                   ("columns=['amount']", "columns='member_id', 'amount'")]),
        xy('numeric-inputs', '숫자 입력 열만 골라요',
            '모델은 숫자만 계산해요. 글자 열을 숫자로 바꾸는 법은 뒤에서 배워요.\n'
            "`select_dtypes(include='number')`는 숫자 자료형 열만 남겨요.\n"
            '정수(int64) 열과 소수(float64) 열이 모두 남아요.',
            '먼저 실행해서 X의 열마다 자료형을 보세요. grade는 글자(str)예요.\n'
            "X 줄 끝에 `.select_dtypes(include='number')`를 붙이세요.\n"
            '다시 실행해서 남은 열과 열 수를 비교해요.',
            '''
            # id와 타깃을 빼서 입력 X를 만들어요.
            X = df.drop(columns=['member_id', 'amount'])
            # X의 열마다 자료형을 봐요. 맨 아래 dtype 줄은 이 목록 자체의 자료형이에요.
            print(X.dtypes)
            # 남은 열 수를 확인해요. shape[1]은 크기의 두 번째 숫자, 열 수예요.
            print(X.shape[1])
            ''',
            "X = df.drop(columns=['member_id', 'amount'])",
            "X = df.drop(columns=['member_id', 'amount']).select_dtypes(include='number')",
            data='members', compare=['X'],
            caution="`include='int'`로 쓰면 소수 열인 minutes가 빠져요.",
            hints=["X 줄 끝에 `.select_dtypes(include='number')`를 붙여요."],
            wrong=[("X = df.drop(columns=['member_id', 'amount'])",
                    "X = df.drop(columns=['member_id', 'amount']).select_dtypes(include='int')"),
                   # Dropping the one text column by name works only while the table has no other.
                   ("X = df.drop(columns=['member_id', 'amount'])",
                    "X = df.drop(columns=['member_id', 'amount', 'grade'])"),
                   ("X = df.drop(columns=['member_id', 'amount'])", "X = df.select_dtypes(include='number')")]),
        xy('leak-column', '결과로 생기는 열은 빼요',
            '예측할 때는 모르는 정보가 X에 섞이는 걸 누수(leakage)라고 해요.\n'
            '포인트는 구매가 끝나야 쌓여요. 금액을 맞히는 데 넣으면 답을 엿보는 셈이죠.\n'
            '타깃과의 상관계수가 1에 아주 가까운 열은 누수를 의심해요.',
            '먼저 실행해서 열마다 amount와의 상관계수를 보세요.\n'
            'amount 자신은 1이에요. 그다음으로 1에 가까운 열을 찾아보세요.\n'
            '그 열 이름을 drop 목록 끝에 더하세요.\n'
            '다시 실행해서 X의 열 이름을 비교해요.',
            '''
            # 타깃은 amount예요. 정답 y로 꺼내요.
            y = df['amount']
            # 숫자 열끼리 상관계수 표를 만들어요.
            table = df[['age', 'visits', 'minutes', 'points', 'amount']].corr()
            # amount 열만 꺼내 소수 둘째 자리까지 봐요.
            print(table['amount'].round(2))
            # id와 타깃을 빼서 입력 X를 만들어요.
            X = df.drop(columns=['member_id', 'amount'])
            print(X.columns)
            ''',
            "columns=['member_id', 'amount']", "columns=['member_id', 'amount', 'points']",
            data='points', compare=['X', 'y'],
            caution='누수 열을 넣다가 타깃을 목록에서 지우면 정답이 X에 남아요.',
            hints=["`df.drop(columns=['member_id', 'amount', 'points'])`로 바꿔요."],
            wrong=[("columns=['member_id', 'amount']", "columns=['member_id', 'points']"),
                   ("columns=['member_id', 'amount']", "columns=['amount', 'points']")]),
        xy('same-rows', 'X와 y는 같은 행끼리 짝이에요',
            'X의 한 행은 회원 한 명의 단서, y의 같은 행은 그 회원의 정답이에요.\n'
            '그래서 행을 고르면 X와 y에 같은 조건을 함께 써요.\n'
            '행 수가 다르면 짝이 어긋난 거예요. `shape[0]`으로 비교해요.',
            '지난달 방문이 0인 회원은 빼려고 해요.\n'
            '먼저 실행해서 두 행 수와 y 왼쪽의 번호(인덱스)를 보세요.\n'
            '`X = X[keep]` 아래에 `y = y[keep]`를 넣으세요.\n'
            '다시 실행해서 두 행 수와 남은 번호를 비교해요.',
            '''
            # 지난달 방문이 1번 이상인 행만 True예요.
            keep = df['visits'] > 0
            # 정답 y와 입력 X를 나눠요.
            y = df['amount']
            X = df.drop(columns=['member_id', 'amount'])
            # keep이 True인 행만 남겨요.
            X = X[keep]
            # 두 행 수를 비교해요. 같아야 짝이 맞아요.
            print(X.shape[0], y.shape[0])
            # 남은 정답과 왼쪽 번호를 확인해요.
            print(y)
            ''',
            'X = X[keep]', 'X = X[keep]\ny = y[keep]', data='members', compare=['X', 'y'],
            caution='행 수만 맞추려고 y를 앞에서 자르면 다른 회원의 정답과 짝지어져요.',
            hints=['`X = X[keep]` 바로 아래에 `y = y[keep]`를 넣어요.'],
            wrong=[('X = X[keep]', 'X = X[keep]\ny = y[:X.shape[0]]'),
                   ('X = X[keep]', "X = X[keep]\ny = y[X['visits'] > 0]")]),
        xy('buy-inputs', '도전 · 구매 여부를 맞힐 입력 X',
            '여러 열 빼기, 누수 빼기, 숫자 열만 고르기를 함께 써요.\n'
            'id와 타깃도 숫자라서 숫자 열만 고르면 X에 남아요.',
            '질문은 회원이 다음 달에 살지 말지예요. y는 이미 맞아요.\n'
            'X에는 지난달까지 알 수 있는 숫자 열만 남기세요.\n'
            '준비 코드는 숫자 열을 다 골랐어요. 섞인 열을 찾아 고치세요.',
            '''
            # 질문: 회원이 다음 달에 살까요, 안 살까요?
            # 정답 y는 구매 여부예요.
            y = df['bought']
            # 숫자 열을 모두 골라 입력 X로 써요.
            X = df.select_dtypes(include='number')
            # X의 열 이름과 두 행 수를 확인해요.
            print(X.columns)
            print(X.shape[0], y.shape[0])
            ''',
            "X = df.select_dtypes(include='number')", BUY_INPUTS, data='next', compare=['X', 'y'],
            challenge=True,
            caution='다음 달 금액을 남기면 금액이 0인지만 봐도 구매 여부가 보여요.',
            hints=['id, 타깃, 다음 달에야 아는 금액까지 세 열을 빼요.',
                   "`df.drop(columns=['member_id', 'amount', 'bought'])` 뒤에 select_dtypes를 붙여요."],
            wrong=[(BUY_INPUTS, "X = df.drop(columns=['member_id', 'bought']).select_dtypes(include='number')"),
                   (BUY_INPUTS, "X = df.drop(columns=['member_id', 'amount']).select_dtypes(include='number')"),
                   (BUY_INPUTS, "X = df.drop(columns=['member_id', 'amount', 'bought'])")]),
        xy('blank-rows', '도전 · 빈칸 행을 지우고 X와 y 나누기',
            '`dropna()`는 빈칸이 있는 행을 지워요. X와 y는 같은 행끼리 짝이에요.\n'
            '정답이 빈 행은 맞힐 답이 없어서 학습에 못 써요.',
            '금액을 맞히는 X와 y를 만들어요. 나이나 금액이 빈 회원은 빼요.\n'
            '지금은 X에서만 빈칸 행을 지워 두 행 수가 달라요.\n'
            '고칠 곳은 직접 찾아보세요. 행 수와 X·y의 왼쪽 번호를 함께 확인해요.\n'
            '행 수가 같아도 번호가 다르면 다른 회원끼리 짝지은 거예요.',
            SPLIT_THEN_DROP + '\n' + REPORT,
            SPLIT_THEN_DROP, DROP_THEN_SPLIT, data='blank', compare=['X', 'y'], challenge=True,
            caution='X와 y에서 따로 지우면 행 수가 같아도 짝이 어긋날 수 있어요.',
            hints=['dropna를 df에 먼저 쓰고 나서 X와 y를 나눠요.',
                   "`df = df.dropna()`를 '타깃은 amount' 주석보다 위에 넣어요. X의 dropna 줄과 그 주석은 지워요."],
            wrong=[('X = X.dropna()', 'X = X.dropna()\ny = y.dropna()'),
                   ('X = X.dropna()', 'df = df.dropna()'),
                   ('df = df.dropna()', "df = df.dropna(subset=['age'])")]),
    ])
