"""aice-data-quality: find blanks, duplicates and outliers, then drop or fill them and recount rows.

Every task reads a small original delivery table. Two changed tables (other row counts, blank
positions, modes and outlier sizes) make memorized output fail. The base table has two exact
duplicate pairs, a price exactly on the upper IQR bound and outliers on both sides, so boundary,
one-sided and processing-order mistakes really change the result. The changed tables add a price
on the lower bound and one that lands on the upper bound only after duplicates are dropped.
"""
from certification_course.kit import py_task
from principles_course.common import code, lesson

PATH = 'data/deliveries.csv'
SOURCES = ['https://aice.study/info/aice/asso', 'https://pandas.pydata.org/docs/user_guide/missing_data.html']

# Base: 13 rows, A03 and A09 recorded twice, blanks in area and minutes, mode north.
# Price quartiles are 14000 and 22000, so the bounds are 2000 and 34000: 1500 and 98000 are
# outliers and A08 sits exactly on the upper bound. A06's 140 minutes pulls the mean above the median.
BASE = code('''
    order_id,area,minutes,price
    A01,north,25,14000
    A02,south,31,22000
    A03,,18,17000
    A04,east,,12000
    A05,north,22,98000
    A06,east,140,19000
    A03,,18,17000
    A07,north,,1500
    A08,east,27,34000
    A09,south,20,21000
    A10,north,35,13000
    A09,south,20,21000
    A11,,29,25000
''')

# Fewer rows, one duplicate pair, the first area blank, mode south, no low price outlier.
# B03's 9750 sits exactly on the lower bound (17250 - 1.5 * 5000), so a strict `>` on low fails.
SHORTER = code('''
    order_id,area,minutes,price
    B01,,40,18000
    B02,south,33,26000
    B03,south,,9750
    B04,west,28,61000
    B05,south,36,20000
    B06,west,24,17000
    B07,,,23000
    B05,south,36,20000
    B08,east,30,16000
    B09,west,120,19000
''')

# More rows, two duplicate pairs (one with a blank area), mode east, outliers on both sides.
# C07's 32000 is above the bound with duplicates (31500) but exactly on it after dropping them
# (23000 + 1.5 * 6000), so the challenge rejects strict `<` and bounds computed before deduping.
LONGER = code('''
    order_id,area,minutes,price
    C01,east,26,15000
    C02,east,,21000
    C03,north,31,18000
    C04,,19,800
    C05,west,44,24000
    C06,east,23,16000
    C07,north,,32000
    C06,east,23,16000
    C08,,22,20000
    C09,west,21,150000
    C10,east,150,19000
    C11,north,28,22000
    C08,,22,20000
    C12,west,33,17000
    C13,,,23000
''')

HEADER = '''import pandas as pd

# 직접 만든 배달 자료예요. 실제 주문 자료가 아니에요.
df = pd.read_csv('data/deliveries.csv')
'''


def quality(id, title, principle, goal, body, before, after, *, compare, caution, hints, wrong=None,
            challenge=False):
    """One cleaning experiment on the base table plus the two changed tables."""
    scenarios = [{'files': {PATH: SHORTER}}, {'files': {PATH: LONGER}}]
    return py_task(id, title, principle, goal, HEADER + code(body), before, after, caution=caution,
                   hints=hints, scenarios=scenarios, files={PATH: BASE}, compare=compare, wrong=wrong,
                   challenge=challenge)


# Blocks reused to build processing-order edits and their mistakes.
FILL_THEN_DROP = '''# 배달 시간 빈칸에 넣을 중앙값이에요.
fill = df['minutes'].median()
# 빈칸을 그 값으로 채워 다시 담아요.
df['minutes'] = df['minutes'].fillna(fill)
# 같은 주문이 두 번 들어간 행을 지워요.
df = df.drop_duplicates()'''

DROP_THEN_FILL = '''# 같은 주문이 두 번 들어간 행을 지워요.
df = df.drop_duplicates()
# 배달 시간 빈칸에 넣을 중앙값이에요.
fill = df['minutes'].median()
# 빈칸을 그 값으로 채워 다시 담아요.
df['minutes'] = df['minutes'].fillna(fill)'''

# Moved only below the fill line: the median still counts the duplicates.
HALF_MOVED = '''# 배달 시간 빈칸에 넣을 중앙값이에요.
fill = df['minutes'].median()
# 같은 주문이 두 번 들어간 행을 지워요.
df = df.drop_duplicates()
# 빈칸을 그 값으로 채워 다시 담아요.
df['minutes'] = df['minutes'].fillna(fill)'''

KEEP_INSIDE = "df = df[(df['price'] >= low) & (df['price'] <= high)]"


def build():
    return lesson('aice-data-quality', '빈칸·중복·이상치 진단하기',
        '빈칸·중복·이상치를 찾아 지우거나 채워요. 처리 전후 행 수를 늘 확인해요. '
        '필수 문제 8개와 선택 도전 2개예요.',
        SOURCES, [
        quality('count-blanks', '열마다 빈칸이 몇 개일까요?',
            '`isna()`는 칸마다 빈칸(NaN)이면 True를 돌려줘요.\n'
            'True는 1, False는 0으로 더해져요.\n'
            '그래서 `.sum()`을 붙이면 열마다 빈칸 수가 나와요.',
            '자, 먼저 실행해서 열마다 True가 몇 개인지 세어 보세요.\n'
            'result 줄의 `df.isna()` 뒤에 `.sum()`을 붙이세요.\n'
            '다시 실행해서 열마다 나온 숫자가 센 개수와 맞는지 봐요.\n'
            '맨 위 행 수와 견주면 빈칸이 얼마나 많은지 보여요. 빈칸이 없는 열은 0이에요.',
            '''
            # 처리 전 행 수예요.
            print(len(df))
            # isna()는 칸마다 빈칸이면 True, 값이 있으면 False예요.
            # 뒤에 sum()을 붙이면 열마다 True를 더해 빈칸 수가 돼요.
            result = df.isna()
            # 결과를 화면에서 확인해요.
            print(result)
            ''',
            'result = df.isna()', 'result = df.isna().sum()', compare=['result'],
            caution='`count()`를 쓰면 빈칸이 아니라 값이 있는 칸을 세요.',
            hints=['`result = df.isna().sum()`으로 바꿔요.'],
            wrong=[('result = df.isna()', 'result = df.count()'),
                   ('result = df.isna()', 'result = df.isna().sum().sum()')]),
        quality('drop-blank-rows', '한 열의 빈칸만 보고 지워요',
            '`dropna()`는 빈칸이 하나라도 있는 행을 통째로 지워요.\n'
            "`subset=['열 이름']`을 넣으면 그 열의 빈칸만 따져요.\n"
            '지운 뒤에는 행 수를 다시 세서 얼마나 줄었는지 봐요.',
            '배달 시간이 빈 주문만 지우려고 해요. 지역 빈칸은 남겨요.\n'
            '먼저 실행해서 처리 전후 행 수를 보세요.\n'
            "`dropna()` 괄호 안에 `subset=['minutes']`를 넣으세요.\n"
            '다시 실행해서 행 수와 area 열에 남은 NaN을 비교해요.',
            '''
            # 처리 전 행 수예요.
            print(len(df))
            # 빈칸을 보고 행을 지운 새 표를 담아요.
            # 괄호가 비면 모든 열의 빈칸을 따져요.
            result = df.dropna()
            # 처리 후 남은 표와 행 수를 확인해요.
            print(result)
            print(len(result))
            ''',
            'df.dropna()', "df.dropna(subset=['minutes'])", compare=['result'],
            caution="`subset=` 없이 `['minutes']`만 넣으면 TypeError가 나요.",
            hints=["`df.dropna(subset=['minutes'])`로 바꿔요."],
            wrong=[('df.dropna()', "df.dropna(['minutes'])"),
                   ('df.dropna()', "df['minutes'].dropna()")]),
        quality('fill-median', '숫자 빈칸은 중앙값으로 채워요',
            '`fillna(값)`은 빈칸(NaN)에 그 값을 넣어요.\n'
            '0으로 채우면 없던 값을 0으로 꾸며서 평균이 내려가요.\n'
            '평균은 큰 값 하나에 끌려가니, 숫자 빈칸은 중앙값으로 많이 채워요.',
            '먼저 실행해서 0으로 채운 자리와 평균을 보세요.\n'
            "fillna 괄호 안의 0을 `df['minutes'].median()`으로 바꾸세요.\n"
            '다시 실행해서 채운 값과 평균을 비교해요.',
            '''
            # 채우기 전 값을 봐요. NaN이 빈칸이에요.
            print(df['minutes'])
            # 빈칸을 괄호 안 값으로 채워 열에 다시 담아요.
            df['minutes'] = df['minutes'].fillna(0)
            # 채운 뒤의 열과 평균을 확인해요.
            result = df['minutes']
            print(result)
            print(result.mean())
            ''',
            'fillna(0)', "fillna(df['minutes'].median())", compare=['result'],
            caution='`median` 뒤 괄호를 빼면 숫자 대신 함수가 빈칸에 들어가요.',
            hints=["`df['minutes'].fillna(df['minutes'].median())` 모양이에요."],
            wrong=[('fillna(0)', "fillna(df['minutes'].median)"),
                   ('fillna(0)', "fillna(df['minutes'].mean())"),
                   # Filled but never stored back into the table.
                   ("df['minutes'] = df['minutes'].fillna(0)", "df['minutes'].fillna(df['minutes'].median())")]),
        quality('fill-mode', '글자 빈칸은 최빈값으로 채워요',
            "글자 열은 평균을 못 구해요. 가장 많이 나온 값(최빈값)이나 '모름'으로 채워요.\n"
            '`mode()`는 최빈값을 목록(Series)으로 돌려줘요. 동률이면 여럿이거든요.\n'
            'fillna에 목록을 넣으면 인덱스가 같은 행끼리 짝지어 채워요.',
            '먼저 실행해서 area의 빈칸이 그대로인지 보세요.\n'
            '최빈값 목록은 인덱스 0뿐이에요. 0번 행은 빈칸이 아니라서 안 채워졌죠?\n'
            'fillna 괄호 안 `mode()` 바로 뒤에 `[0]`을 붙여 첫 값을 꺼내세요.\n'
            '다시 실행해서 남은 빈칸 수를 비교해요.',
            '''
            # 가장 많이 나온 지역이에요. 왼쪽 0은 인덱스예요.
            print(df['area'].mode())
            # area의 빈칸을 최빈값으로 채워 다시 담아요.
            df['area'] = df['area'].fillna(df['area'].mode())
            # 채운 뒤의 지역 열을 확인해요.
            result = df['area']
            print(result)
            # area에 남은 빈칸 수예요.
            print(result.isna().sum())
            ''',
            "fillna(df['area'].mode())", "fillna(df['area'].mode()[0])", compare=['result'],
            caution='화면에 보인 지역 이름을 직접 적으면 자료가 바뀔 때 틀려요.',
            hints=["`df['area'].fillna(df['area'].mode()[0])`처럼 써요."],
            wrong=[("fillna(df['area'].mode())", "fillna('north')"),
                   ("df['area'] = df['area'].fillna(df['area'].mode())",
                    "df['area'].fillna(df['area'].mode()[0])")]),
        quality('drop-duplicates', '같은 주문이 두 번 들어갔어요',
            '`duplicated()`는 모든 열 값이 같은 행이 위에 이미 있으면 True예요.\n'
            '처음 나온 행은 False라서 남아요.\n'
            '`drop_duplicates()`는 True인 행을 뺀 새 표를 돌려줘요. df 자체는 그대로예요.',
            '먼저 실행해서 True인 행과 처리 전후 행 수를 보세요.\n'
            '지웠는데 행 수가 그대로죠?\n'
            '`df.drop_duplicates()` 앞에 `df = `를 붙여 다시 담으세요.\n'
            '다시 실행해서 줄어든 행 수를 True 개수와 비교해요.',
            '''
            # 모든 열 값이 같은 행이 위에 이미 있으면 True예요.
            print(df.duplicated())
            # True를 더하면 중복 행의 수예요.
            print(df.duplicated().sum())
            # 처리 전 행 수예요.
            print(len(df))
            # 중복 행을 지워요.
            df.drop_duplicates()
            # 처리 후 행 수를 확인해요.
            print(len(df))
            ''',
            'df.drop_duplicates()', 'df = df.drop_duplicates()', compare=['df'],
            caution='`df[df.duplicated()]`는 지운 표가 아니라 중복 행만 고른 표예요.',
            hints=['`df = df.drop_duplicates()`로 바꿔요.'],
            wrong=[('df.drop_duplicates()', 'df = df[df.duplicated()]'),
                   ('df.drop_duplicates()', 'df = df.duplicated()')]),
        quality('quartiles', '가운데 절반의 폭, IQR',
            '`quantile(0.25)`는 작은 값부터 25% 자리의 값이에요. Q1이라고 해요.\n'
            '`quantile(0.75)`는 75% 자리의 값, Q3예요.\n'
            'Q3 - Q1을 사분위수 범위(IQR)라고 해요. 가운데 절반이 퍼진 폭이에요.',
            '먼저 실행해서 q1, q3, iqr을 보세요. iqr이 0이죠?\n'
            'q3 줄은 q1 줄을 복사해 만들었어요.\n'
            'q3 줄의 `0.25`를 `0.75`로 바꾸세요.\n'
            '다시 실행해서 describe의 25%, 75% 줄과 비교해요.',
            '''
            # 가격 분포를 요약해요. 25%와 75% 줄을 봐 두세요.
            print(df['price'].describe())
            # 작은 값부터 25% 자리의 값(Q1)이에요.
            q1 = df['price'].quantile(0.25)
            # 75% 자리의 값(Q3)이에요.
            q3 = df['price'].quantile(0.25)
            # 가운데 절반이 퍼진 폭(IQR)이에요.
            iqr = q3 - q1
            print(q1, q3, iqr)
            ''',
            "q3 = df['price'].quantile(0.25)", "q3 = df['price'].quantile(0.75)", compare=['q1', 'q3', 'iqr'],
            caution='`quantile(75)`처럼 퍼센트 숫자를 넣으면 ValueError가 나요.',
            hints=["`q3 = df['price'].quantile(0.75)`로 바꿔요."],
            wrong=[("q3 = df['price'].quantile(0.25)", "q3 = df['price'].quantile(75)"),
                   ('quantile(0.75)\n# 가운데 절반이 퍼진 폭(IQR)이에요.\niqr = q3 - q1',
                    'quantile(0.75)\n# 가운데 절반이 퍼진 폭(IQR)이에요.\niqr = q1 - q3')]),
        quality('iqr-bounds', '경계 안의 행만 남겨요',
            '아래 경계는 `q1 - 1.5 * iqr`, 위 경계는 `q3 + 1.5 * iqr`이에요.\n'
            '두 경계 밖의 값을 이상치로 봐요. 경계와 같은 값은 남겨요.\n'
            '상자그림에서 따로 찍힌 점도 같은 기준이에요.',
            '먼저 실행해서 두 경계와 처리 전후 행 수를 보세요.\n'
            '지금 조건은 위 경계만 따져요. 남은 가격을 low와 견줘 보세요.\n'
            "kept 줄의 조건을 `(df['price'] >= low) & (df['price'] <= high)`로 바꾸세요.\n"
            '다시 실행해서 남은 행 수를 비교해요.',
            '''
            # Q1, Q3, IQR을 구해요.
            q1 = df['price'].quantile(0.25)
            q3 = df['price'].quantile(0.75)
            iqr = q3 - q1
            # IQR의 1.5배만큼 바깥에 경계를 둬요.
            low = q1 - 1.5 * iqr
            high = q3 + 1.5 * iqr
            print(low, high)
            # 처리 전 행 수예요.
            print(len(df))
            # 경계 안의 행만 남겨요.
            kept = df[df['price'] <= high]
            # 처리 후 남은 표와 행 수를 확인해요.
            print(kept)
            print(len(kept))
            ''',
            "df['price'] <= high", "(df['price'] >= low) & (df['price'] <= high)", compare=['kept'],
            caution='`>`와 `<`를 쓰면 경계와 딱 같은 값까지 지워져요.',
            hints=["`kept = df[(df['price'] >= low) & (df['price'] <= high)]` 모양이에요."],
            wrong=[("df['price'] <= high", "(df['price'] > low) & (df['price'] < high)"),
                   ("df['price'] <= high", "(df['price'] >= low) | (df['price'] <= high)"),
                   ("df['price'] <= high", "df['price'] >= low & df['price'] <= high")]),
        quality('clean-order', '중복부터 지우고 채워요',
            '중복 행은 같은 주문이 두 번 들어간 거예요.\n'
            '지우기 전에 중앙값을 구하면 그 주문이 두 번 세어져요.\n'
            '그래서 지울 행을 먼저 지우고, 남은 값으로 채워요.',
            '먼저 실행해서 fill 값과 처리 후 표를 보세요.\n'
            '중복을 지우는 두 줄(주석 한 줄과 코드 한 줄)을 찾으세요.\n'
            '그 두 줄을 fill 위의 주석보다 위로 옮기세요.\n'
            '다시 실행해서 fill 값을 비교해요. 빈칸이던 A04, A07의 minutes도 봐요.',
            FILL_THEN_DROP + '\n# 처리 후 행 수와 표, 빈칸에 넣은 값을 확인해요.\nprint(len(df))\nprint(df)\nprint(fill)\n',
            FILL_THEN_DROP, DROP_THEN_FILL, compare=['df', 'fill'],
            caution='fill을 구한 줄보다 아래로 옮기면 중복이 섞인 중앙값을 써요.',
            hints=['중복을 지우는 두 줄을 read_csv 줄 바로 아래로 옮겨요.'],
            wrong=[(FILL_THEN_DROP, HALF_MOVED),
                   (FILL_THEN_DROP, DROP_THEN_FILL.replace('df = df.drop_duplicates()', 'df.drop_duplicates()'))]),
        quality('clean-pipeline', '도전 · 정리한 뒤 행 수와 평균',
            '중복 지우기, IQR 경계로 이상치 지우기, 중앙값 채우기를 조합해요.\n'
            '지울 행을 다 지운 뒤에 남은 값으로 채워요.\n'
            '경계는 중복을 지운 표로 다시 구해요. 앞 문제에서 지운 주문이 남을 수도 있어요.',
            '가격이 경계 밖인 주문을 지우는 줄이 빠졌어요.\n'
            '경계와 같은 값은 남겨요. 지운 표는 df에 다시 담아요.\n'
            '그 줄을 어디에 넣을지가 핵심이에요.\n'
            '처리 전후 행 수와 배달 시간 평균을 비교해요.',
            '''
            # 처리 전 행 수예요.
            print(len(df))
            # 같은 주문이 두 번 들어간 행을 지워요.
            df = df.drop_duplicates()
            # 가격의 Q1, Q3, IQR이에요.
            q1 = df['price'].quantile(0.25)
            q3 = df['price'].quantile(0.75)
            iqr = q3 - q1
            # 아래 경계와 위 경계예요.
            low = q1 - 1.5 * iqr
            high = q3 + 1.5 * iqr
            # 배달 시간 빈칸을 남은 값의 중앙값으로 채워요.
            df['minutes'] = df['minutes'].fillna(df['minutes'].median())
            # 처리 후 행 수와 배달 시간 평균이에요.
            count = len(df)
            result = df['minutes'].mean()
            print(count, result)
            ''',
            'high = q3 + 1.5 * iqr', 'high = q3 + 1.5 * iqr\n# 경계 밖의 행을 지워요.\n' + KEEP_INSIDE,
            compare=['count', 'result'], challenge=True,
            caution='경계로 지우는 줄을 채운 뒤에 넣으면 지울 행까지 중앙값에 섞여요.',
            hints=['경계로 지우는 줄은 빈칸을 채우는 줄보다 위에 넣어요. kept가 아니라 df에 담아요.',
                   f'high 줄 바로 아래에 `{KEEP_INSIDE}`를 넣어요.'],
            wrong=[('# 처리 후 행 수와 배달 시간 평균이에요.',
                    KEEP_INSIDE + '\n# 처리 후 행 수와 배달 시간 평균이에요.'),
                   ('high = q3 + 1.5 * iqr', "high = q3 + 1.5 * iqr\ndf = df[df['price'] <= high]"),
                   # Quartiles mistaken for the bounds.
                   ('high = q3 + 1.5 * iqr',
                    "high = q3 + 1.5 * iqr\ndf = df[(df['price'] >= q1) & (df['price'] <= q3)]")]),
        quality('unknown-share', '도전 · 모르는 지역까지 넣은 비율',
            '`value_counts(normalize=True)`는 빈칸을 빼고 비율을 내요.\n'
            "빈칸을 '모름'으로 채우면 분모에 들어가요.\n"
            '중복 행이 남으면 같은 주문이 두 번 세어져요.',
            '중복을 뺀 주문 중 지역별 비율을 구하세요.\n'
            "지역 빈칸은 '모름'으로 채워 함께 세요.\n"
            '준비 코드는 두 가지를 빠뜨렸어요. 고칠 곳은 직접 찾아보세요.',
            '''
            # 지역별 주문 비율을 구해요.
            result = df['area'].value_counts(normalize=True)
            # 맨 아래 Name의 proportion은 비율이라는 뜻이에요.
            print(result)
            # 비율을 구한 표의 행 수를 확인해요.
            print(len(df))
            ''',
            '# 지역별 주문 비율을 구해요.',
            "# 같은 주문이 두 번 들어간 행을 지워요.\ndf = df.drop_duplicates()\n"
            "# 모르는 지역은 '모름'으로 채워 다시 담아요.\ndf['area'] = df['area'].fillna('모름')\n"
            '# 지역별 주문 비율을 구해요.',
            compare=['result'], challenge=True,
            caution="`fillna('모름')` 결과를 열에 다시 담지 않으면 빈칸이 빠져요.",
            hints=["중복 지우기와 '모름' 채우기, 두 가지가 빠졌어요.",
                   "`df['area'] = df['area'].fillna('모름')`처럼 열에 다시 담아요."],
            wrong=[('# 지역별 주문 비율을 구해요.',
                    "df['area'] = df['area'].fillna('모름')\n# 지역별 주문 비율을 구해요."),
                   ('# 지역별 주문 비율을 구해요.',
                    'df = df.drop_duplicates()\n# 지역별 주문 비율을 구해요.'),
                   ('# 지역별 주문 비율을 구해요.',
                    "df = df.drop_duplicates()\ndf['area'].fillna('모름')\n# 지역별 주문 비율을 구해요.")]),
    ])
