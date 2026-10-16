"""aice-visualization: choose a graph for the question and give it readable axes.

Every task reads one small original delivery table: a zone category, distance and minutes that rise
together, a price that barely follows distance in the base table, and one late delivery that a box plot shows as a point. Two changed
tables (other rows, counts, zones and outlier) make memorized pictures fail; plot_task compares the
learner's figure with the reference figure on each table, and the listed mistakes are proven to fail.
"""
from certification_course.kit import py_task
from certification_course.kit_plots import plot_task
from principles_course.common import code, lesson

PATH = 'data/delivery.csv'
SOURCES = ['https://aice.study/info/aice/asso', 'https://matplotlib.org/stable/api/pyplot_summary.html',
           'https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.boxplot.html',
           'https://seaborn.pydata.org/generated/seaborn.heatmap.html']

# Base table: zones 5/4/3 (no ties), one late delivery in 남부, distance and minutes rise together.
BASE = code('''
    zone,distance,minutes,price
    북부,1.2,15,18000
    남부,3.5,31,22000
    북부,2.0,19,9000
    동부,4.1,36,15000
    남부,0.8,12,27000
    북부,2.6,24,12000
    남부,2.9,64,16000
    동부,3.0,28,31000
    북부,4.4,39,14000
    남부,2.2,21,25000
    북부,3.8,33,19000
    동부,1.0,14,11000
''')

# Fewer rows in another order; 동부 leads the counts and holds the late delivery.
FEWER = code('''
    zone,distance,minutes,price
    동부,2.4,22,14000
    북부,0.9,13,21000
    동부,3.6,34,17000
    남부,1.8,18,26000
    동부,3.1,61,12000
    북부,4.0,37,15000
    동부,2.9,27,23000
    남부,3.3,30,10000
    북부,1.6,16,19000
''')

# More rows and a fourth zone; the late delivery moves to 북부.
MORE = code('''
    zone,distance,minutes,price
    서부,2.1,20,16000
    남부,4.6,41,13000
    서부,1.4,15,24000
    북부,3.1,29,18000
    남부,0.7,11,20000
    서부,3.9,35,9000
    북부,3.3,75,27000
    동부,1.9,18,15000
    서부,4.2,38,22000
    남부,2.8,26,12000
    서부,1.0,13,30000
    북부,3.4,32,17000
    동부,0.5,10,21000
    남부,3.7,33,14000
''')

SCENARIOS = [{'files': {PATH: FEWER}}, {'files': {PATH: MORE}}]

READ = '''
# 직접 만든 배달 기록이에요. 실제 고객 자료가 아니에요.
df = pd.read_csv('data/delivery.csv')
# zone은 구역, distance는 거리(km)예요.
# minutes는 배달 시간(분), price는 주문 금액(원)이에요.
'''

PLOT_HEADER = 'import pandas as pd\n# 그래프 도구를 plt라는 별명으로 불러와요.\nimport matplotlib.pyplot as plt\n' + READ
SEABORN_HEADER = ('import pandas as pd\nimport matplotlib.pyplot as plt\n'
                  '# 통계 그래프 도구를 sns라는 별명으로 불러와요.\nimport seaborn as sns\n' + READ)
TABLE_HEADER = 'import pandas as pd\n' + READ


def graph(id, title, principle, goal, body, before, after, *, caution, hints, wrong, header=PLOT_HEADER,
          challenge=False):
    """One figure experiment on the base table, graded on the two changed tables too."""
    starter = header + '\n' + code(body)
    return plot_task(id, title, principle, goal, starter, before, after, caution=caution, hints=hints,
                     scenarios=SCENARIOS, files={PATH: BASE}, wrong=wrong, challenge=challenge)


def build():
    return lesson('aice-visualization', '그래프로 분포와 관계 확인하기',
        '질문에 맞는 그래프를 골라 분포와 관계를 봐요. 축 이름과 제목도 읽히게 붙여요. '
        '필수 문제 8개와 선택 도전 2개예요.',
        SOURCES, [
        graph('count-bar', '글자 열은 세어서 막대로 그려요',
            '그래프는 matplotlib으로 그려요. `import matplotlib.pyplot as plt`로 불러와요.\n'
            "`표.plot(kind='bar')`는 표에 든 숫자를 막대 높이로 그려요.\n"
            '`plt.show()`는 그린 그림을 화면에 보여 줘요.',
            '자, 먼저 실행해서 오류의 마지막 줄을 읽으세요. 그릴 숫자가 없다는 뜻이에요.\n'
            'zone 열은 글자라서 막대 높이가 될 수 없어요.\n'
            "`df['zone']` 뒤에 `.value_counts()`를 붙여 구역별 건수를 세세요.\n"
            '다시 실행해서 출력된 건수와 막대 높이를 비교해요.',
            '''
            # 구역별 건수를 counts에 담으려고 해요.
            counts = df['zone']
            # 그릴 표를 먼저 화면에서 봐요.
            print(counts)

            # counts의 숫자를 막대로 그려요.
            counts.plot(kind='bar')
            # 그린 그림을 화면에 보여 줘요.
            plt.show()
            ''',
            "counts = df['zone']", "counts = df['zone'].value_counts()",
            caution='value_counts 대신 count를 쓰면 숫자 하나만 나와 오류가 나요.',
            hints=["`counts = df['zone'].value_counts()`로 바꿔요."],
            wrong=[("counts = df['zone']", "counts = df['zone'].count()"),
                   ("counts = df['zone']", "counts = df['zone'].value_counts")]),
        graph('ratio-label', '축 이름은 막대가 뭔지 알려 줘요',
            '`plt.xlabel`은 가로축, `plt.ylabel`은 세로축에 이름을 붙여요.\n'
            '`plt.title`은 그래프 맨 위에 제목을 달아요.\n'
            "축 이름에는 막대가 무슨 값인지 적어요. 단위는 `'시간(분)'`처럼 괄호에 넣어요.",
            '먼저 실행해서 축 이름과 제목이 어디 붙는지 보세요.\n'
            '`value_counts()` 괄호 안에 `normalize=True`를 넣어 비율로 바꾸세요.\n'
            "세로축 이름 `'건수'`도 `'비율'`로 고치세요.\n"
            '다시 실행해서 막대 높이와 세로축 숫자를 비교해요.',
            '''
            # 구역별로 세어 표로 만들어요. normalize=True면 비율이 나와요.
            counts = df['zone'].value_counts()
            # 표를 보고 막대로 그려요.
            print(counts)
            counts.plot(kind='bar')

            # 축 이름과 제목은 그래프를 그린 다음에 붙여요.
            plt.xlabel('구역')
            plt.ylabel('건수')
            # 그래프 맨 위에 제목을 달아요.
            plt.title('구역별 배달')
            plt.show()
            ''',
            "value_counts()\n# 표를 보고 막대로 그려요.\nprint(counts)\ncounts.plot(kind='bar')\n\n"
            "# 축 이름과 제목은 그래프를 그린 다음에 붙여요.\nplt.xlabel('구역')\nplt.ylabel('건수')",
            "value_counts(normalize=True)\n# 표를 보고 막대로 그려요.\nprint(counts)\ncounts.plot(kind='bar')\n\n"
            "# 축 이름과 제목은 그래프를 그린 다음에 붙여요.\nplt.xlabel('구역')\nplt.ylabel('비율')",
            caution='`plt.xlabel`을 plot 줄보다 먼저 쓰면 열 이름으로 덮일 수 있어요.',
            hints=["`value_counts(normalize=True)`와 `plt.ylabel('비율')` 두 곳을 고쳐요."],
            wrong=[('value_counts()', 'value_counts(normalize=True)'),
                   ("plt.ylabel('건수')", "plt.ylabel('비율')")]),
        graph('group-mean-bar', '막대 높이를 그룹 평균으로 바꿔요',
            '`groupby`로 만든 그룹별 평균 표도 막대로 그릴 수 있어요.\n'
            '막대 높이와 순서는 언제나 표에 든 그대로예요.\n'
            '그래서 그래프를 바꾸려면 그릴 표를 바꿔요.',
            '질문은 구역별 평균 배달 시간이에요.\n'
            '먼저 실행해서 막대가 무엇을 그렸는지 보세요. 세로축 이름과 맞나요?\n'
            "table 줄을 `df.groupby('zone')['minutes'].mean()`으로 바꾸세요.\n"
            '다시 실행해서 막대 순서와 높이를 출력 표와 비교해요. groupby 표는 구역 이름 순서예요.',
            '''
            # 질문: 구역마다 배달 시간은 평균 몇 분일까요?
            table = df['zone'].value_counts()
            print(table)
            # table의 숫자가 막대 높이가 돼요.
            table.plot(kind='bar')

            # 축 이름에 단위까지 적었어요.
            plt.xlabel('구역')
            plt.ylabel('평균 시간(분)')
            # 제목을 달고 그림을 보여 줘요.
            plt.title('구역별 평균 배달 시간')
            plt.show()
            ''',
            "table = df['zone'].value_counts()", "table = df.groupby('zone')['minutes'].mean()",
            caution='groupby 뒤에 열을 고르지 않으면 숫자 열마다 막대가 생겨요.',
            hints=["`table = df.groupby('zone')['minutes'].mean()`로 바꿔요."],
            wrong=[("table = df['zone'].value_counts()", "table = df.groupby('zone').mean()"),
                   ("table = df['zone'].value_counts()", "table = df.groupby('zone')['minutes'].sum()")]),
        graph('hist-bins', '히스토그램의 구간 수를 바꿔요',
            '히스토그램은 숫자 범위를 구간으로 나눠요. 구간마다 개수를 막대로 그려요.\n'
            '`plt.hist(열, bins=3)`의 bins는 구간 수예요.\n'
            'plt.hist는 구간별 개수, 구간 경계, 막대 세 가지를 돌려줘요.',
            '먼저 실행해서 막대 수와 출력된 구간별 개수를 보세요.\n'
            '`bins=3`을 `bins=8`로 바꾸세요.\n'
            '다시 실행해서 분포(값이 몰리고 퍼진 모양)를 비교해요.\n'
            '비어 있는 구간도 찾아보세요.',
            '''
            # 배달 시간이 어떻게 퍼져 있는지 봐요.
            # 돌려준 세 값을 차례로 이름 셋에 나눠 받아요.
            counts, edges, bars = plt.hist(df['minutes'], bins=3)
            # 구간마다 몇 건인지 글자로도 봐요.
            # 개수가 실수로 나와서 숫자 끝에 점(.)이 붙어요.
            print(counts)

            # 가로축은 시간, 세로축은 건수예요.
            plt.xlabel('배달 시간(분)')
            plt.ylabel('건수')
            # 제목을 달고 그림을 보여 줘요.
            plt.title('배달 시간 분포')
            plt.show()
            ''',
            'bins=3', 'bins=8',
            caution="`bins='8'`처럼 따옴표로 감싸면 ValueError가 나요.",
            hints=['`bins=8`로 숫자만 바꿔요.'],
            wrong=[('bins=3', "bins='8'"), ('bins=3', 'bin=8')]),
        graph('box-outlier', '상자그림에서 이상치 점을 찾아요',
            "`df.boxplot(column='열 이름')`은 상자그림(boxplot)을 그려요.\n"
            '상자는 25%에서 75%까지, 가운데 선은 중앙값(50%)이에요.\n'
            '위아래 선(수염)보다 먼 값은 점으로 따로 찍혀요. 이상치 후보예요.',
            '먼저 실행해서 distance의 상자그림과 describe 표를 보세요.\n'
            "col 값을 `'minutes'`로 바꾸세요.\n"
            '다시 실행해서 따로 찍힌 점을 찾으세요. describe의 max와 비교해요.\n'
            '상자 가운데 선은 50%와 비교해 봐요.',
            '''
            # 상자그림으로 볼 열 이름이에요.
            col = 'distance'
            # 그 열의 요약 숫자를 먼저 봐요.
            print(df[col].describe())

            # column에 넣은 열로 상자그림을 그려요.
            df.boxplot(column=col)
            plt.title('상자그림')
            plt.show()
            ''',
            "col = 'distance'", "col = 'minutes'",
            caution='그리는 줄만 바꾸면 표와 그림이 서로 다른 열을 보여 줘요.',
            hints=["`col = 'minutes'`로 바꿔요."],
            wrong=[("col = 'distance'", "col = 'Minutes'"),
                   ('df.boxplot(column=col)', "df.boxplot(column='minutes')")]),
        graph('scatter-xy', '산점도는 x, y 순서로 넣어요',
            '산점도는 두 숫자 열의 관계를 점으로 보여 줘요.\n'
            '`plt.scatter(x, y)`의 첫째 값은 가로축, 둘째 값은 세로축이에요.\n'
            '영향을 주는 쪽을 보통 가로축에 둬요. 여기서는 거리예요.',
            '먼저 실행해서 오류의 마지막 줄을 읽으세요. y 값이 빠졌다는 뜻이에요.\n'
            "`df['distance']` 뒤에 `, df['minutes']`를 넣으세요.\n"
            '다시 실행해서 점들이 놓인 방향을 보세요. 혼자 먼 점도 찾아요.',
            '''
            # 거리가 멀수록 배달 시간도 길까요?
            # 가로축 값, 세로축 값 순서로 넣어요.
            plt.scatter(df['distance'])

            # 축 이름이 가로·세로 순서와 맞는지 봐요.
            plt.xlabel('거리(km)')
            plt.ylabel('시간(분)')
            # 제목을 달고 그림을 보여 줘요.
            plt.title('거리와 배달 시간')
            plt.show()
            ''',
            "plt.scatter(df['distance'])", "plt.scatter(df['distance'], df['minutes'])",
            caution='x와 y를 바꿔 넣으면 오류 없이 축이 뒤바뀐 그림이 나와요.',
            hints=["`plt.scatter(df['distance'], df['minutes'])`로 바꿔요."],
            wrong=[("plt.scatter(df['distance'])", "plt.scatter(df['minutes'], df['distance'])"),
                   ("plt.scatter(df['distance'])", "plt.scatter('distance', 'minutes')")]),
        py_task('corr-columns', '상관계수는 숫자 열끼리 구해요',
            '상관계수는 두 열이 함께 움직이는 정도예요. -1부터 1 사이 값이에요.\n'
            '1에 가까우면 함께 늘고, -1에 가까우면 반대로 움직여요. 0 근처면 직선 관계가 약해요.\n'
            '`표.corr()`는 열끼리의 상관계수를 표로 보여 줘요.',
            '먼저 실행해서 오류의 마지막 줄을 읽으세요. 글자를 숫자로 못 바꾼다는 뜻이에요.\n'
            '글자 열인 zone까지 계산하려고 해서 그래요. 다른 pandas 버전은 오류 없이 글자 열을 빼기도 해요.\n'
            "`df.corr()`를 `df[['distance', 'minutes', 'price']].corr()`로 바꾸세요.\n"
            'distance와 minutes 칸을 앞 문제의 산점도와 비교해요.',
            TABLE_HEADER + '\n' + code('''
            # 숫자 열끼리 상관계수 표를 만들려고 해요.
            table = df.corr()
            # 표 이름을 먼저 적고, 소수 둘째 자리까지 봐요.
            print('상관계수 표')
            print(table.round(2))
            '''),
            'table = df.corr()', "table = df[['distance', 'minutes', 'price']].corr()",
            scenarios=SCENARIOS, files={PATH: BASE}, compare=['table'],
            caution="`df['distance', 'minutes']`처럼 대괄호를 하나만 쓰면 KeyError가 나요.",
            hints=["`df[['distance', 'minutes', 'price']]`처럼 대괄호를 두 겹으로 써요."],
            wrong=[('table = df.corr()', "table = df['distance', 'minutes', 'price'].corr()"),
                   ('table = df.corr()', "table = df[['distance', 'minutes']].corr()")]),
        graph('heatmap-corr', '히트맵에는 상관표를 넣어요',
            'seaborn은 통계 그래프를 쉽게 그리는 도구예요.\n'
            '`sns.heatmap(표)`는 표의 숫자를 칸마다 색으로 칠해요.\n'
            '`annot=True`를 넣으면 칸 안에 숫자도 적어요.',
            '먼저 실행해서 칸이 몇 줄 생겼는지 보세요. 배달 기록 한 행이 한 줄이에요.\n'
            'table 줄 끝에 `.corr()`를 붙여 상관표로 바꾸세요.\n'
            '다시 실행해서 칸 수와 색을 비교해요. 대각선 칸의 값도 보세요.\n'
            '대각선은 한 열이 자기 자신과 만나는 칸이에요.',
            '''
            # 숫자 열 세 개로 그릴 표를 만들어요.
            table = df[['distance', 'minutes', 'price']]
            # 표의 크기(행 수, 열 수)부터 봐요.
            print(table.shape)
            print(table.round(2))

            # table의 숫자를 칸마다 색으로 칠해요.
            # annot=True라서 칸 안에 숫자도 적혀요.
            sns.heatmap(table, annot=True)
            plt.title('상관 히트맵')
            plt.show()
            ''',
            "table = df[['distance', 'minutes', 'price']]", "table = df[['distance', 'minutes', 'price']].corr()",
            header=SEABORN_HEADER,
            caution='`.corr`처럼 괄호를 빼면 표 대신 함수가 담겨 오류가 나요.',
            hints=["`table = df[['distance', 'minutes', 'price']].corr()`로 바꿔요."],
            wrong=[("table = df[['distance', 'minutes', 'price']]", 'table = df.corr()'),
                   ("table = df[['distance', 'minutes', 'price']]",
                    "table = df[['distance', 'minutes', 'price']].corr")]),
        graph('box-by-zone', '도전 · 구역별 분포를 상자로 비교해요',
            "`df.boxplot(column='minutes', by='zone')`은 구역마다 상자를 그려요.\n"
            '평균 막대는 퍼짐과 이상치를 숨겨요. 분포를 비교할 땐 상자그림을 써요.\n'
            '상자 가운데 선이 중앙값이었던 것도 떠올려요.',
            '질문은 구역마다 배달 시간이 어떻게 퍼져 있는지예요.\n'
            '평균 막대를 구역별 상자그림으로 바꾸세요.\n'
            '출력 표는 상자 가운데 선과 맞게 중앙값으로 바꾸세요.\n'
            "세로축 이름은 `'시간(분)'`으로 고쳐요.",
            '''
            # 질문: 구역마다 배달 시간이 얼마나 퍼져 있을까요?
            # 늦은 배달이 어느 구역에 있는지도 보고 싶어요.
            table = df.groupby('zone')['minutes'].mean()
            print(table)
            # 질문에 맞는 그래프를 그려요.
            table.plot(kind='bar')

            # 축 이름이 그린 값과 맞는지 봐요.
            plt.ylabel('평균 시간(분)')
            plt.title('구역별 배달 시간')
            plt.show()
            ''',
            "mean()\nprint(table)\n# 질문에 맞는 그래프를 그려요.\ntable.plot(kind='bar')\n\n"
            "# 축 이름이 그린 값과 맞는지 봐요.\nplt.ylabel('평균 시간(분)')",
            "median()\nprint(table)\n# 질문에 맞는 그래프를 그려요.\ndf.boxplot(column='minutes', by='zone')\n\n"
            "# 축 이름이 그린 값과 맞는지 봐요.\nplt.ylabel('시간(분)')",
            caution='by 없이 그리면 구역을 나누지 않은 상자 하나만 나와요.',
            hints=["그리는 줄을 `df.boxplot(column='minutes', by='zone')`로 바꿔요.",
                   "table은 `.median()`, 세로축 이름은 `'시간(분)'`이에요."],
            # Each mistake keeps the median table, so only the drawn figure is wrong.
            wrong=[("df.boxplot(column='minutes', by='zone')", "df.boxplot(column='minutes')"),
                   ("df.boxplot(column='minutes', by='zone')", "table.plot(kind='box')"),
                   ("plt.ylabel('시간(분)')", "plt.ylabel('평균 시간(분)')")], challenge=True),
        graph('scatter-corr', '도전 · 관계를 그림과 숫자로 봐요',
            '산점도는 `plt.scatter(x, y)` 순서로 넣었어요.\n'
            "두 열의 상관계수는 `df[['열1', '열2']].corr()`로 구했죠.\n"
            '그림과 숫자가 같은 두 열을 봐야 서로 맞춰 볼 수 있어요.',
            '질문은 거리가 멀수록 배달 시간도 긴지예요.\n'
            '지금 코드는 질문과 다른 열을 보고 있어요. 축 이름은 맞아요.\n'
            '표와 그림이 모두 거리와 시간을 보게 두 줄을 고치세요.\n'
            '점도 축 이름처럼 가로가 거리, 세로가 시간이어야 해요.',
            '''
            # 질문: 거리가 멀수록 배달 시간도 길까요?
            # 비교할 두 열을 골라 상관계수를 봐요.
            pair = df[['distance', 'price']]
            print('상관계수 표')
            print(pair.corr().round(2))

            # 같은 두 열을 점으로 찍어요.
            plt.scatter(df['price'], df['distance'])
            plt.xlabel('거리(km)')
            plt.ylabel('시간(분)')
            # 제목을 달고 그림을 보여 줘요.
            plt.title('거리와 배달 시간')
            plt.show()
            ''',
            "pair = df[['distance', 'price']]\nprint('상관계수 표')\nprint(pair.corr().round(2))\n\n"
            "# 같은 두 열을 점으로 찍어요.\nplt.scatter(df['price'], df['distance'])",
            "pair = df[['distance', 'minutes']]\nprint('상관계수 표')\nprint(pair.corr().round(2))\n\n"
            "# 같은 두 열을 점으로 찍어요.\nplt.scatter(df['distance'], df['minutes'])",
            caution='표만 고치고 그림을 그대로 두면 숫자와 그림이 다른 관계를 말해요.',
            hints=["pair 줄의 `'price'`를 `'minutes'`로 바꿔요.",
                   "`plt.scatter(df['distance'], df['minutes'])` 순서로 넣어요."],
            wrong=[("pair = df[['distance', 'price']]", "pair = df[['distance', 'minutes']]"),
                   ("plt.scatter(df['distance'], df['minutes'])", "plt.scatter(df['minutes'], df['distance'])")],
            challenge=True),
    ])
