"""aice-data-summary: count, share, middle value, group comparison and ranking (AICE Associate 7th lesson).

Every task reads a small original branch order table. Blanks in amount separate count() from len()
and size(), one large order pulls the mean away from the median, ties sit at the head(n) cut, and a
boundary amount equals the threshold. Two changed tables (other rows, branches, blanks and outlier)
and changed thresholds make memorized output fail; listed mistakes are realistic slips proven to fail.
"""
from certification_course.kit import py_task
from principles_course.common import code, lesson

SOURCES = ['https://aice.study/info/aice/asso',
           'https://pandas.pydata.org/docs/user_guide/basics.html#descriptive-statistics',
           'https://pandas.pydata.org/docs/user_guide/groupby.html']

PATH = 'data/orders.csv'

# Base: 10 orders, 3 branches, blank amounts in seoul and daegu, one huge seoul order (98000),
# two 12000 orders that tie at the third place and sit on the 12000 threshold.
BASE = '''branch,channel,amount,items
seoul,app,12000,2
busan,web,8000,1
seoul,web,,3
daegu,app,15000,2
busan,app,9000,1
seoul,app,98000,6
daegu,web,12000,2
busan,web,7000,1
daegu,app,,2
seoul,web,11000,3
'''

# Fewer rows, a fourth branch, the blank and the huge order both in busan, a tie at second place.
SHUFFLED = '''branch,channel,amount,items
busan,app,14000,2
incheon,web,6000,1
seoul,app,9000,2
busan,web,,1
daegu,app,12000,3
busan,app,76000,5
incheon,app,11000,2
seoul,web,14000,1
'''

# More rows, other branches, two blanks, the huge order in daegu and two 13000 orders on the threshold.
LONGER = '''branch,channel,amount,items
daegu,web,13000,2
seoul,app,8000,1
gwangju,app,,2
daegu,app,64000,4
seoul,web,10000,2
gwangju,web,9000,1
seoul,app,13000,3
daegu,app,,1
gwangju,app,10000,2
seoul,web,7000,1
daegu,web,12000,2
seoul,app,15000,3
'''

HEADER = '''import pandas as pd

# 직접 만든 지점 주문 자료예요. 실제 자료가 아니에요.
df = pd.read_csv('data/orders.csv')
'''

FOOTER = '''# 결과를 화면에서 확인해요.
print(result)
'''


def summary(id, title, principle, goal, body, before, after, *, values=({}, {}), caution, hints, wrong=None,
            challenge=False):
    """One summary experiment: the base table plus two changed tables with their own prepared values."""
    starter = HEADER + code(body) + FOOTER
    first, second = values
    scenarios = [dict(first, files={PATH: SHUFFLED}), dict(second, files={PATH: LONGER})]
    return py_task(id, title, principle, goal, starter, before, after, caution=caution, hints=hints,
                   scenarios=scenarios, files={PATH: BASE}, compare=['result'], wrong=wrong,
                   challenge=challenge)


def build():
    return lesson('aice-data-summary', '개수·분포·그룹별 비교',
        '표를 숫자 몇 개로 요약해요. 개수와 분모를 구별하고 그룹끼리 비교해요. '
        '필수 문제 8개와 선택 도전 2개예요.',
        SOURCES, [
        summary('describe-rows', 'describe 표에서 중앙값 행을 꺼내요',
            '`describe()`는 숫자 열마다 요약 값을 한 표로 보여 줘요.\n'
            '행 이름 count는 빈칸을 뺀 값의 개수, mean은 평균이에요.\n'
            '50%는 크기순으로 놓았을 때 가운데 값, 중앙값이에요.',
            '자, 먼저 실행해서 나온 열을 보세요. 글자 열인 branch와 channel은 빠져요.\n'
            'amount의 count를 shape의 앞 숫자(전체 행 수)와 비교해 보세요.\n'
            "result 줄 끝에 `.loc['50%']`를 붙이고 다시 실행하세요.\n"
            '열마다 중앙값만 남았는지 확인해요. 맨 아래 Name은 꺼낸 행의 이름 50%예요.',
            '''
            # 표의 크기예요. 앞 숫자가 전체 행 수예요.
            print(df.shape)
            # 숫자 열마다 요약 값을 한 표로 만들어요.
            # 행 이름은 count, mean, std, min, 25%, 50%, 75%, max예요.
            result = df.describe()
            ''',
            'result = df.describe()', "result = df.describe().loc['50%']",
            caution="`df.describe()['50%']`처럼 쓰면 열에서 찾아 KeyError가 나요.",
            hints=["`df.describe().loc['50%']`로 바꿔요. 행은 loc으로 골라요."],
            wrong=[('result = df.describe()', "result = df.describe()['50%']"),
                   ('result = df.describe()', "result = df.describe().loc['50']"),
                   ('result = df.describe()', "result = df.describe().loc['mean']")]),
        summary('count-len', '값이 적힌 개수는 count로 세요',
            '`len(df)`는 표의 행 수예요. 빈칸이 있는 행도 한 행으로 세요.\n'
            '열 하나에 len을 써도 빈칸까지 세요.\n'
            '`count()`는 열에서 빈칸(NaN)을 뺀 값의 개수예요.',
            '금액이 기록된 주문 수를 구해요. 먼저 실행해서 두 숫자를 비교하세요.\n'
            "`len(df['amount'])`를 `df['amount'].count()`로 바꾸세요.\n"
            '다시 실행해서 줄어든 수를 보세요.\n'
            '「함께 제공한 파일」에서 금액 칸이 빈 행(`,,`)을 세어 맞춰 봐요.',
            '''
            # 전체 주문 수예요. 한 행이 주문 하나예요.
            print(len(df))
            # 금액이 기록된 주문 수를 구하려고 해요.
            result = len(df['amount'])
            ''',
            "len(df['amount'])", "df['amount'].count()",
            caution='열에 len을 쓰면 금액이 빈 주문까지 세어요.',
            hints=["`result = df['amount'].count()`로 바꿔요. 괄호까지 붙여요."],
            wrong=[("len(df['amount'])", "df['amount'].size"),
                   ("len(df['amount'])", 'df.count()'),
                   ("len(df['amount'])", "df['amount'].count")]),
        summary('value-ratio', '범주마다 개수와 비율을 봐요',
            '`value_counts()`는 값마다 몇 행인지 세어 많은 순서로 보여 줘요.\n'
            '`normalize=True`를 넣으면 개수 대신 0과 1 사이 비율이 나와요.\n'
            '비율을 모두 더하면 1이에요.',
            '지점마다 주문 비율을 구해요. 먼저 실행해서 지점별 주문 수를 보세요.\n'
            '숫자 위아래 줄은 결과에 붙은 이름표예요. 지점 이름과 숫자만 보면 돼요.\n'
            'value_counts 괄호 안에 `normalize=True`를 넣으세요.\n'
            '다시 실행해서 개수를 전체 주문 수로 나눈 값인지 확인해요.',
            '''
            # 전체 주문 수예요.
            print(len(df))
            # 지점 열의 값마다 행을 세요. normalize=True면 비율이 나와요.
            result = df['branch'].value_counts()
            ''',
            'value_counts()', 'value_counts(normalize=True)',
            caution='열을 고르지 않고 `df.value_counts()`를 쓰면 행 전체 조합을 세요.',
            hints=["`df['branch'].value_counts(normalize=True)`로 바꿔요."],
            wrong=[("df['branch'].value_counts()", 'df.value_counts(normalize=True)'),
                   ('value_counts()', 'value_counts(Normalize=True)')]),
        summary('mean-median', '큰 값 하나에 끌려가는 평균',
            '`mean()`은 평균, `median()`은 중앙값을 구해요. 둘 다 빈칸은 빼요.\n'
            '아주 큰 값이 하나 있으면 평균은 그쪽으로 끌려가요.\n'
            '중앙값은 가운데 자리 값이라 덜 흔들려요.',
            '보통 주문 한 건의 금액을 값 하나로 나타내요.\n'
            '먼저 실행해서 금액들과 평균을 비교하세요. 평균보다 작은 금액이 많죠?\n'
            '`mean()`을 `median()`으로 바꾸고 다시 실행하세요.\n'
            'describe의 50% 행에서 본 값과도 비교해 보세요.',
            '''
            # 금액을 모두 봐요. NaN은 빈칸이에요.
            print(df['amount'])
            # 보통 주문 한 건의 금액을 값 하나로 나타내요.
            result = df['amount'].mean()
            ''',
            "df['amount'].mean()", "df['amount'].median()",
            caution='`df.median()`처럼 열을 안 고르면 글자 열 때문에 오류가 나요. 옛 pandas는 글자 열을 조용히 빼요.',
            hints=["`df['amount'].median()`으로 바꿔요. 괄호를 꼭 붙여요."],
            wrong=[("df['amount'].mean()", "df['amount'].median"),
                   ("df['amount'].mean()", 'df.median()')]),
        summary('true-ratio', 'True의 합은 개수, 평균은 비율',
            '비교 결과의 True는 1, False는 0으로 계산해요.\n'
            '그래서 `sum()`은 True의 개수, `mean()`은 True의 비율이에요.\n'
            '비율의 분모는 비교한 전체 행 수예요. 빈칸은 비교하면 False예요.',
            '전체 주문 중 금액이 limit 이상인 비율을 구해요.\n'
            '먼저 실행해서 조건에 맞는 주문 수를 보세요.\n'
            '`above.sum()`을 `above.mean()`으로 바꾸세요.\n'
            '다시 실행해서 개수를 전체 행 수로 나눈 값인지 확인해요.',
            '''
            # 기준 금액이에요.
            limit = 12000
            # 금액이 limit 이상인지 행마다 비교해요.
            above = df['amount'] >= limit
            # True는 1, False는 0으로 계산해요.
            result = above.sum()
            # 전체 행 수도 함께 봐요.
            print(len(df))
            ''',
            'above.sum()', 'above.mean()',
            values=[{'limit': 14000}, {'limit': 13000}],
            caution='`count()`로 나누면 금액이 빈 주문이 분모에서 빠져요.',
            hints=['`result = above.mean()`으로 바꿔요.'],
            wrong=[('above.sum()', "above.sum() / df['amount'].count()"),
                   ("df['amount'] >= limit\n# True는 1, False는 0으로 계산해요.\nresult = above.mean()",
                    "df['amount'] > limit\n# True는 1, False는 0으로 계산해요.\nresult = above.mean()")]),
        summary('group-mean', '지점별 평균은 열을 골라서',
            "`groupby('열')`은 그 열 값이 같은 행끼리 묶어요.\n"
            '뒤에 `mean()`을 붙이면 묶음마다 평균을 내요.\n'
            '글자 열은 평균을 못 내요. 그래서 계산할 열을 먼저 골라요.',
            '지점(branch)별 평균 금액을 구해요. 먼저 실행해서 오류의 마지막 줄을 읽으세요.\n'
            'str 자료형은 mean 계산을 못 한다는 뜻이에요. 시험의 옛 pandas는 오류 없이 글자 열을 빼기도 해요.\n'
            'branch는 묶는 기준이라 계산에서 빠져요. 남은 글자 열은 channel이죠.\n'
            "`groupby('branch')` 바로 뒤에 `['amount']`를 넣고 다시 실행하세요.",
            '''
            # 지점이 같은 행끼리 묶어요.
            # 묶음마다 평균을 내려고 해요.
            result = df.groupby('branch').mean()
            ''',
            "df.groupby('branch').mean()", "df.groupby('branch')['amount'].mean()",
            caution='두 열 이름의 자리를 바꾸면 같은 TypeError가 나요.',
            hints=["`df.groupby('branch')['amount'].mean()`으로 바꿔요."],
            wrong=[("df.groupby('branch').mean()", "df.groupby('amount')['branch'].mean()"),
                   ("df.groupby('branch').mean()", "df['amount'].groupby('branch').mean()")]),
        summary('group-size', '묶음의 행 수는 size로 세요',
            'groupby 뒤 `count()`는 묶음마다 빈칸을 뺀 값의 개수예요.\n'
            '`size()`는 빈칸이 있어도 묶음의 행 수를 모두 세요.\n'
            'count와 len의 차이와 같아요.',
            '지점별 주문 건수를 구해요. 금액이 빈 주문도 주문이에요.\n'
            '먼저 실행해서 지점별 개수를 보세요.\n'
            '`count()`를 `size()`로 바꾸고 다시 실행하세요.\n'
            '지점별 숫자를 더하면 전체 주문 수와 같아져요.',
            '''
            # 전체 주문 수예요.
            print(len(df))
            # 지점이 같은 행끼리 묶고 amount 열을 골라요.
            # count는 빈칸을 빼고 세요. size는 빈칸까지 세요.
            result = df.groupby('branch')['amount'].count()
            ''',
            'count()', 'size()',
            caution='groupby 결과를 len으로 감싸면 지점 수가 나와요.',
            hints=["`df.groupby('branch')['amount'].size()`로 바꿔요."],
            wrong=[("df.groupby('branch')['amount'].count()", "len(df.groupby('branch')['amount'])"),
                   ("df.groupby('branch')['amount'].count()", "df.groupby('branch').count()")]),
        summary('sort-top', '큰 순서로 정렬해 앞의 n개',
            "`sort_values('열')`은 그 열 값으로 행을 정렬해요. 기본은 작은 값부터예요.\n"
            '`ascending=False`를 넣으면 큰 값부터 정렬해요.\n'
            '정렬한 표에 `head(n)`을 붙이면 앞의 n행만 남아요.',
            '금액이 큰 주문 n건을 골라요. 먼저 실행해서 어떤 주문이 남는지 보세요.\n'
            "sort_values 괄호 안 'amount' 뒤에 `, ascending=False`를 넣고 다시 실행하세요.\n"
            '마지막 행과 금액이 같은 주문을 「함께 제공한 파일」에서 찾아보세요.\n'
            'head(n)은 같은 금액이 더 있어도 n행에서 잘라요. 확인만 하고 코드는 그대로 둬요.',
            '''
            # 남길 주문 수예요.
            n = 3
            # 금액 순서로 정렬한 뒤 앞의 n행을 남겨요.
            result = df.sort_values('amount').head(n)
            # 남은 표의 크기예요. 앞 숫자가 행 수예요.
            print(result.shape)
            ''',
            "df.sort_values('amount')", "df.sort_values('amount', ascending=False)",
            values=[{'n': 2}, {'n': 4}],
            caution='sorted처럼 `reverse=True`를 쓰면 TypeError가 나요.',
            hints=["`df.sort_values('amount', ascending=False).head(n)` 모양이에요."],
            wrong=[("df.sort_values('amount')", "df.sort_values('amount', reverse=True)"),
                   ("df.sort_values('amount').head(n)", "df.sort_values('amount').tail(n)"),
                   ("df.sort_values('amount').head(n)", "df.head(n).sort_values('amount', ascending=False)")]),
        summary('app-share', '도전 · app 주문 중 비율',
            '행 고르기 `df[조건]`과 True의 평균을 함께 써요.\n'
            '비율은 무엇이 분모인지부터 정해요.',
            'app 주문 중에서 금액이 limit 이상인 주문의 비율을 구하세요.\n'
            '금액이 빈 app 주문도 분모에 들어가요.\n'
            '지금 코드는 전체 주문이 분모예요.\n'
            '고칠 줄은 직접 찾아보세요.',
            '''
            # 기준 금액이에요.
            limit = 12000
            # 금액이 limit 이상인지 행마다 비교해요.
            above = df['amount'] >= limit
            # True의 비율이에요. 분모는 비교한 행 수예요.
            result = above.mean()
            ''',
            "above = df['amount'] >= limit", "above = df[df['channel'] == 'app']['amount'] >= limit",
            values=[{'limit': 14000}, {'limit': 13000}],
            caution='두 조건을 &로 묶어 평균을 내면 분모가 전체 주문이 돼요.',
            hints=["app 주문만 고르는 식은 `df[df['channel'] == 'app']`예요. 이 표에서 amount를 꺼내 비교해요.",
                   "above 줄을 `df[df['channel'] == 'app']['amount'] >= limit`로 바꿔요."],
            wrong=[("above = df['amount'] >= limit",
                    "above = (df['channel'] == 'app') & (df['amount'] >= limit)"),
                   ("above = df['amount'] >= limit", "above = df[df['channel'] == 'app']['amount'] > limit")],
            challenge=True),
        summary('app-rank', '도전 · app 주문으로 매긴 지점 순위',
            '행 고르기, groupby, 정렬을 이어 써요.\n'
            'groupby로 한 열을 계산한 결과는 Series예요. 정렬할 때 열 이름을 넣지 않아요.',
            'app 주문만으로 지점별 평균 금액을 구하세요.\n'
            '평균이 큰 지점부터 보이게 정렬하세요.\n'
            '고칠 줄은 직접 찾아보세요.',
            '''
            # 지점이 같은 행끼리 묶어 amount의 평균을 내요.
            # groupby 결과는 지점 이름 순서로 나와요.
            result = df.groupby('branch')['amount'].mean()
            ''',
            "result = df.groupby('branch')['amount'].mean()",
            "result = df[df['channel'] == 'app'].groupby('branch')['amount'].mean().sort_values(ascending=False)",
            caution="Series에 `sort_values('amount')`처럼 열 이름을 넣으면 오류가 나요.",
            hints=['groupby 앞의 df 자리에 app 주문만 고른 표를 넣어요.',
                   '`mean()` 뒤에 `.sort_values(ascending=False)`를 붙여요.'],
            wrong=[('mean().sort_values(ascending=False)', "mean().sort_values('amount', ascending=False)"),
                   ("result = df.groupby('branch')['amount'].mean()",
                    "result = df.groupby('branch')['amount'].mean().sort_values(ascending=False)"),
                   ('.sort_values(ascending=False)', '.sort_values()')],
            challenge=True),
    ])
