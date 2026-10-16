"""aice-row-conditions: choose records with comparisons, boundaries, two conditions, loc and iloc.

Every task reads a small original visit table. Two changed tables (other row order and count) and
changed thresholds make memorized output fail and catch boundary, parenthesis and index mistakes.
"""
from certification_course.kit import py_task
from principles_course.common import code, lesson

PATH = 'data/visits.csv'

# Base table: boundary visits (4) and minutes (20), one 'App' row, a blank minute, row 0 rarely chosen.
BASE = '''channel,visits,minutes,bought
web,1,8,0
app,4,25,1
web,4,,1
App,5,30,1
app,2,12,0
web,6,40,0
app,3,20,1
web,3,15,1
app,5,18,0
'''

# Fewer rows in another order; the blank minute belongs to a bought record.
SHUFFLED = '''channel,visits,minutes,bought
app,2,15,0
web,5,22,1
app,6,,1
web,4,11,0
app,4,28,1
App,3,20,1
web,2,7,1
'''

# More rows; row 0 matches most conditions, so fixed index labels change meaning.
LONGER = '''channel,visits,minutes,bought
app,5,35,1
web,2,,0
APP,4,16,0
web,3,20,1
app,1,6,0
web,7,45,1
app,5,18,1
web,4,26,1
app,3,9,1
app,2,30,0
'''

HEADER = '''import pandas as pd

# 직접 만든 방문 자료예요. 실제 고객 자료가 아니에요.
df = pd.read_csv('data/visits.csv')
'''

FOOTER = '''# 결과를 화면에서 확인해요.
print(result)
'''

# Table results print their size first: the row count is part of what the learner compares.
TABLE_FOOTER = '''# 결과의 크기를 먼저 봐요. 앞 숫자가 행 수예요.
print(result.shape)
# 결과를 화면에서 확인해요.
print(result)
'''


def rows(id, title, principle, goal, body, before, after, *, values, caution, hints, wrong=None, challenge=False,
         table=False):
    """One table experiment: the base table plus two changed tables with their own prepared values."""
    starter = HEADER + code(body) + (TABLE_FOOTER if table else FOOTER)
    first, second = values
    scenarios = [dict(first, files={PATH: SHUFFLED}), dict(second, files={PATH: LONGER})]
    return py_task(id, title, principle, goal, starter, before, after, caution=caution, hints=hints,
                   scenarios=scenarios, files={PATH: BASE}, compare=['result'], wrong=wrong,
                   challenge=challenge)


def build():
    return lesson('aice-row-conditions', '조건으로 원하는 기록 고르기',
        '조건에 맞는 기록만 표에서 골라요. 경계값과 두 조건을 작은 실험으로 익혀요. '
        '필수 문제 8개와 선택 도전 2개예요.',
        ['https://aice.study/info/aice/asso'], [
        rows('compare-rows', '비교 결과로 행을 골라요',
            '열을 숫자와 비교하면 행마다 True나 False가 하나씩 나와요.\n'
            '행마다 값이 하나씩 줄지은 것을 Series라고 해요. 열 하나를 꺼낸 것도 Series예요.\n'
            '이 결과를 `df[ ]` 안에 넣으면 True인 행만 남아요.',
            '먼저 실행해서 True와 False를 보세요.\n'
            '맨 위 크기는 숫자가 하나예요. Series에는 열 수 없이 행 수만 있거든요.\n'
            '비교식 전체를 `df[ ]`로 감싸 result에 담고 다시 실행하세요.\n'
            '표 왼쪽 번호와 True 자리를 맞춰 봐요. 크기의 앞 숫자(행 수)가 몇으로 줄었는지도 보세요.',
            '''
            # 비교할 기준 방문 횟수예요.
            limit = 4
            # visits 값이 limit보다 큰지 행마다 비교해요.
            result = df['visits'] > limit
            ''',
            "result = df['visits'] > limit", "result = df[df['visits'] > limit]",
            table=True, values=[{'limit': 3}, {'limit': 4}],
            caution="`df[df['visits']] > limit`처럼 대괄호를 먼저 닫으면 오류가 나요.",
            hints=["`result = df[df['visits'] > limit]`로 바꿔요."],
            wrong=[("result = df['visits'] > limit", "result = df[df['visits']] > limit"),
                   ("result = df['visits'] > limit", "result = df['visits'][df['visits'] > limit]")]),
        rows('boundary-include', '기준과 같은 값도 넣을까요?',
            '`>`는 기준보다 큰 값만 True예요. 초과라고 해요.\n'
            '`>=`는 기준과 같은 값도 True예요. 이상이라고 해요.\n'
            '기준과 딱 같은 값을 경계값이라고 불러요.',
            '방문 횟수가 limit 이상인 기록을 골라요.\n'
            '먼저 실행해서 남은 행을 확인하세요.\n'
            '`>`를 `>=`로 바꾸고 다시 실행하세요.\n'
            'visits가 limit과 같은 행을 찾아보세요.',
            '''
            # 이 기준 이상인 기록을 고르려고 해요.
            limit = 4
            # 비교 결과가 True인 행만 남겨요.
            result = df[df['visits'] > limit]
            ''',
            "df['visits'] > limit", "df['visits'] >= limit",
            table=True, values=[{'limit': 5}, {'limit': 4}],
            caution='`=>`처럼 기호 순서를 바꾸면 문법 오류가 나요.',
            hints=['이상은 기준값도 포함해요. `>=`를 써요.'],
            wrong=[("df['visits'] > limit", "df['visits'] => limit")]),
        rows('text-match', '글자는 대소문자까지 같아야 해요',
            '`==`는 두 값이 같은지 비교해요.\n'
            '글자는 대소문자까지 똑같아야 True예요.\n'
            '`=` 하나는 값을 저장하는 기호라 비교에 못 써요.',
            'channel이 소문자 app인 기록을 골라요.\n'
            '먼저 실행해서 어떤 행이 나오는지 보세요.\n'
            "'App'을 'app'으로 바꾸고 다시 실행하세요.\n"
            'App으로 적힌 행이 어떻게 됐는지 비교해요.',
            '''
            # 접속 경로가 같은지 행마다 비교해요.
            # 비교할 글자는 따옴표로 감싸요.
            result = df[df['channel'] == 'App']
            ''',
            "'App'", "'app'",
            table=True, values=[{}, {}],
            caution='`==` 대신 `=`를 쓰면 문법 오류가 나요.',
            hints=['따옴표 안을 소문자 app으로 바꿔요.'],
            wrong=[("== 'App'", "= 'app'"), ("== 'App'", '== app')]),
        rows('both-and', '두 조건은 and 대신 &로 묶어요',
            'and는 True나 False 값 하나끼리 묶는 말이에요.\n'
            '비교 결과처럼 행마다 값이 있으면 `&`를 써요.\n'
            '`&`는 두 조건이 모두 True인 행만 True예요.',
            '방문이 limit 이상이고 구매한 기록을 골라요.\n'
            '먼저 실행해서 오류의 마지막 줄을 읽으세요. Series의 참·거짓을 하나로 못 정한다(ambiguous)는 뜻이에요.\n'
            '뒤에 권하는 `a.any()`, `a.all()`은 여기서 쓰지 않아요.\n'
            '`and`를 `&`로 바꾸고 다시 실행하세요.',
            '''
            # 기준 방문 횟수예요.
            limit = 4
            # bought가 1이면 구매한 기록이에요.
            # 두 조건을 각각 괄호로 묶었어요.
            result = df[(df['visits'] >= limit) and (df['bought'] == 1)]
            ''',
            ' and ', ' & ',
            table=True, values=[{'limit': 4}, {'limit': 5}],
            caution='괄호를 빼고 `&`만 쓰면 같은 ValueError가 나요.',
            hints=['`and`만 `&`로 바꿔요. 괄호는 그대로 둬요.'],
            wrong=[("(df['visits'] >= limit) and (df['bought'] == 1)",
                    "df['visits'] >= limit & df['bought'] == 1")]),
        rows('both-parens', '&를 쓸 때는 조건마다 괄호',
            'Python은 `&`를 `>=`나 `==`보다 먼저 계산해요.\n'
            "괄호가 없으면 `mins & df['bought']`부터 계산해요. 그러면 남은 `>=`와 `==`가 한 비교로 이어져요.\n"
            '이어진 비교는 속에서 and로 묶여요. 그래서 조건마다 괄호로 순서를 정해요.',
            '이용 시간이 mins분 이상인데 구매하지 않은 기록이에요.\n'
            '먼저 실행해서 오류를 확인하세요. `&`를 썼는데도 and 때와 같은 ValueError예요.\n'
            '두 비교식을 각각 괄호로 묶고 다시 실행하세요.',
            '''
            # 기준 이용 시간(분)이에요.
            mins = 18
            # bought가 0이면 구매하지 않은 기록이에요.
            # 두 조건을 &로 이어 함께 따져요.
            result = df[df['minutes'] >= mins & df['bought'] == 0]
            ''',
            "df['minutes'] >= mins & df['bought'] == 0", "(df['minutes'] >= mins) & (df['bought'] == 0)",
            table=True, values=[{'mins': 15}, {'mins': 16}],
            caution='한쪽만 묶으면 오류 없이 틀린 행이 나올 수 있어요.',
            hints=["`(df['minutes'] >= mins) & (df['bought'] == 0)` 모양이에요."],
            # bought == 0 keeps both one-sided groupings wrong; with == 1 the left one passes by 0/1 luck.
            wrong=[("df['minutes'] >= mins & df['bought'] == 0",
                    "df['minutes'] >= mins & (df['bought'] == 0)"),
                   ("df['minutes'] >= mins & df['bought'] == 0",
                    "(df['minutes'] >= mins) & df['bought'] == 0")]),
        rows('either-or', '하나만 맞아도 고르려면 |',
            '`|`는 두 조건 중 하나만 True여도 True예요.\n'
            '`&`처럼 조건마다 괄호로 묶어요.\n'
            '`|`는 Shift와 ₩(\\) 키를 함께 눌러 입력해요.',
            '방문이 limit 이상이거나 구매한 기록을 골라요.\n'
            '준비 코드는 두 조건이 다 맞는 기록만 골라요.\n'
            '`&`를 `|`로 바꾸고 다시 실행하세요.\n'
            '두 결과의 행 수를 비교해요.',
            '''
            # 기준 방문 횟수예요.
            limit = 4
            # 조건마다 괄호로 묶고 기호로 이어요.
            result = df[(df['visits'] >= limit) & (df['bought'] == 1)]
            ''',
            ') & (', ') | (',
            table=True, values=[{'limit': 3}, {'limit': 5}],
            caution='`|` 대신 or를 쓰면 and 때처럼 ValueError가 나요.',
            hints=['가운데 `&` 하나만 `|`로 바꿔요.'],
            wrong=[(') & (', ') or (')]),
        rows('loc-column', 'loc로 행과 열을 함께 골라요',
            '`df.loc[행, 열]`은 행과 열을 한 번에 골라요.\n'
            '쉼표 앞 행 자리에 조건을 넣어요.\n'
            '쉼표 뒤 열 자리에 열 이름을 넣어요.',
            '방문이 limit 이상인 기록의 이용 시간만 봐요.\n'
            '먼저 실행해서 모든 열이 나오는 걸 보세요.\n'
            "조건 뒤, 닫는 `]` 바로 앞에 `, 'minutes'`를 넣고 다시 실행하세요.\n"
            '열 하나만 고르면 결과가 Series로 나와요. 맨 아래 Name이 고른 열 이름이에요.',
            '''
            # 기준 방문 횟수예요.
            limit = 4
            # 쉼표 앞은 행 자리, 뒤는 열 자리예요.
            result = df.loc[df['visits'] >= limit]
            ''',
            "df.loc[df['visits'] >= limit]", "df.loc[df['visits'] >= limit, 'minutes']",
            values=[{'limit': 5}, {'limit': 3}],
            caution='행과 열의 자리를 바꾸면 오류가 나요.',
            hints=["`df.loc[df['visits'] >= limit, 'minutes']`로 바꿔요."],
            wrong=[("df.loc[df['visits'] >= limit]", "df.loc['minutes', df['visits'] >= limit]"),
                   ("df.loc[df['visits'] >= limit]", "df[df['visits'] >= limit, 'minutes']"),
                   ("df.loc[df['visits'] >= limit]", "df.loc[df['visits'] >= limit, ['minutes']]")]),
        rows('iloc-first', '고른 표의 첫 행은 iloc[0]',
            '표 왼쪽 번호(인덱스)는 행을 골라도 그대로 남아요.\n'
            '`loc[0]`은 인덱스가 0인 행을 찾아요.\n'
            '`iloc[0]`은 인덱스와 상관없이 첫 자리 행이에요.',
            '방문이 limit 이상인 기록 중 첫 기록을 꺼내요.\n'
            '먼저 실행해서 오류의 마지막 줄을 읽으세요. `KeyError: 0`은 인덱스가 0인 행이 없다는 뜻이에요.\n'
            '`loc`을 `iloc`으로 바꾸고 다시 실행하세요.\n'
            '행 하나를 꺼내면 열 이름이 왼쪽에 세로로 나와요. 맨 아래 Name이 그 행의 인덱스예요.',
            '''
            # 기준 방문 횟수예요.
            limit = 4
            # 조건에 맞는 기록만 골라 picked에 담아요.
            picked = df[df['visits'] >= limit]
            # 고른 표에서 첫 기록을 꺼내요.
            result = picked.loc[0]
            ''',
            'picked.loc[0]', 'picked.iloc[0]',
            values=[{'limit': 4}, {'limit': 5}],
            caution='화면의 인덱스를 `loc`에 직접 적으면 자료가 바뀔 때 틀려요.',
            hints=['`picked.iloc[0]`으로 바꿔요.'],
            wrong=[('picked.loc[0]', 'df.iloc[0]'), ('picked.loc[0]', 'picked.loc[1]')]),
        rows('range-count', '도전 · 범위 안의 app 기록 수',
            '`<=`는 이하예요. 기준과 같은 값도 True예요.\n'
            '경계값, `&`, 괄호를 함께 써요.\n'
            '`shape[0]`이 표의 행 수였던 것도 떠올려요.',
            'app 기록 중 방문이 low 이상 high 이하인 기록 수를 구해요.\n'
            '지금 코드는 high 조건이 빠졌어요.\n'
            '표 대신 행 수를 result에 담으세요.',
            '''
            # 범위의 아래 끝과 위 끝이에요. 둘 다 포함해요.
            low = 2
            high = 4
            # 조건마다 괄호로 묶어 &로 이어요.
            result = df[(df['channel'] == 'app') & (df['visits'] >= low)]
            ''',
            "result = df[(df['channel'] == 'app') & (df['visits'] >= low)]",
            "result = df[(df['channel'] == 'app') & (df['visits'] >= low) & (df['visits'] <= high)].shape[0]",
            values=[{'high': 5}, {'low': 3, 'high': 5}],
            caution='이하를 `<`로 쓰면 high와 같은 기록이 빠져요.',
            hints=["`(df['visits'] <= high)`를 `&`로 하나 더 이어요.", '고른 표 뒤에 `.shape[0]`을 붙여요.'],
            wrong=[('<= high', '< high'), ('.shape[0]', '.shape[1]')], challenge=True),
        rows('loc-two-conditions', '도전 · 두 조건으로 고른 기록의 한 열',
            '`loc`의 행 자리에도 `&`로 묶은 조건을 넣어요.\n'
            '빈칸(NaN)은 `>=`로 비교하면 False가 나와요.',
            '구매했고 이용 시간이 mins분 이상인 기록을 골라요.\n'
            '그 기록들의 channel 열만 result에 담으세요.\n'
            '지금 코드에는 구매 조건만 있어요.',
            '''
            # 기준 이용 시간(분)이에요.
            mins = 20
            # 행 자리에 조건, 열 자리에 열 이름을 넣었어요.
            result = df.loc[df['bought'] == 1, 'channel']
            ''',
            "df['bought'] == 1, 'channel'", "(df['bought'] == 1) & (df['minutes'] >= mins), 'channel'",
            values=[{'mins': 22}, {'mins': 26}],
            caution='괄호를 빼면 `&`가 먼저 계산돼 오류가 나요.',
            hints=['행 자리의 조건 뒤에 `&`로 조건을 하나 더 이어요.', '조건마다 괄호로 묶고 이상은 `>=`를 써요.'],
            wrong=[("(df['bought'] == 1) & (df['minutes'] >= mins)", "df['bought'] == 1 & df['minutes'] >= mins"),
                   ("df['minutes'] >= mins", "df['minutes'] > mins")], challenge=True),
    ])
