"""aice-plots: 9 answer-picking steps -> coding steps (2026-10-29).

Each step draws with the real seaborn/matplotlib and prints what was actually drawn or computed (bar
heights, bin counts, areas, label). Prepared cases rerun with other delivery tables, so typed numbers
and the starter's statistic fail."""
from _kit import Script, code_step


def step(*args, **kwargs):
    # seaborn/matplotlib start slowly; the lesson's own final challenge allows 30 seconds per case too.
    return code_step(*args, timeout=30, **kwargs)

OPENING = ['이 수업에서는 그래프가 무엇을 계산해 보여 주는지 직접 코드를 고쳐 확인해요. 그림과 원자료의 차이를 구별해요.',
           '배송 자료로 개수·평균·구간·밀도·비율을 그려 비교해요. 질문에 맞는 그래프 함수와 옵션을 직접 써요.']
PRD_SCOPE = ['세 챕터·세 단원·열한 스텝으로 같은 배송표를 살펴봐요.',
             'countplot·barplot 평균, 구간 경계, 밀도 면적, 그룹별 정규화, 겹친 점, 표시 숨김, 상관 히트맵, 축 이름을 한 곳씩 직접 고쳐 비교해요.']
PRD_GRADING = ['직접 고친 그래프 코드를 실제 파이썬(seaborn·matplotlib)으로 실행해 판정해요. 실행·해설만으로 성공시키지 않아요.',
               '그려진 막대 높이·구간 개수·면적·축 이름 같은 실제 그림 정보를 출력하고, 다른 배송표로 다시 실행해 기준 풀이와 비교해요. 숫자를 글자로 적은 답, 다른 통계·분모를 쓴 답은 거절해요.',
               '독립 예상 출력과 이미지 산출을 공개 실행기로 확인해요.',
               '마지막 도전(stp_037eb885-a668-43ed-9619-6e48c0f3c20e): 실제 파이썬 실행의 막대 높이·순서·축 이름과 다른 배송 기록 세 가지로 채점해요. 건수 막대, 합계 막대, 취소 행 포함, 짧은 순서는 실패해요.']
PRD_NARRATION = ['그림과 결과를 읽고 통계·분모·표시 한 곳만 고쳐 비교해요.',
                 '개수와평균·구간 경계·밀도와확률·행삭제와표시숨김·원시값과 상관을 조심할 지점으로 짚어요.']

HEAD = ('import pandas as pd\nimport seaborn as sns\nimport matplotlib.pyplot as plt\n\n'
        '# 같은 배송표에서 개수와 측정값을 나눠 봐요.\ndata = {"region": ["north", "north", "south", "south"], "minutes": [10, 20, 30, 50], "distance": [1, 2, 3, 4]}\n'
        'df = pd.DataFrame(data)\n')
HEIGHTS = '# 확인용 출력: 그려진 막대 높이를 숫자로 보여 줘요. 이 줄의 문법은 몰라도 돼요.\nprint([round(float(p.get_height()), 5) for p in ax.patches])\nplt.show()\n'
OTHER = [{'data': {'region': ['south', 'north', 'south', 'south', 'north'], 'minutes': [12, 44, 18, 31, 7], 'distance': [2, 6, 1, 4, 3]}},
         {'data': {'region': ['north', 'south', 'south'], 'minutes': [25, 8, 40], 'distance': [5, 1, 2]}}]
SUBMIT = '수정한 코드를 제출하세요.'
W = '실제 seaborn·matplotlib 동작을 정확히 말해요.'

s1 = HEAD + '# 이 줄을 고쳐 평균 시간 대신 지역별 배송 개수를 막대로 그리세요. 지역 순서는 north, south예요.\nax = sns.barplot(data=df, x="region", y="minutes", order=["north", "south"], errorbar=None)\n' + HEIGHTS
s1_sol = s1.replace('ax = sns.barplot(data=df, x="region", y="minutes", order=["north", "south"], errorbar=None)',
                    '# countplot은 y 없이 x의 값마다 행을 세어 막대 높이로 그려요.\nax = sns.countplot(data=df, x="region", order=["north", "south"])')
n1 = (Script(s1)
      .say('같은 표에서 지역별 배송 개수를 보려 해요. 평균을 그리는 barplot 줄을 고쳐야 해요.', 'text:ax 줄을 고쳐 평균 시간 대신 지역별 배송 개수를 막대로 그리세요.')
      .run('print([round')
      .say('[15.0, 40.0]이에요. north 10·20과 south 30·50의 평균 시간이에요.', 'output')
      .patch('ax = sns.barplot(data=df, x="region", y="minutes", order=["north", "south"], errorbar=None)',
             'ax = sns.countplot(data=df, x="region", order=["north", "south"])', 'countplot으로 바꾸고 y와 errorbar를 지워요.')
      .run('print([round')
      .say('[2.0, 2.0]이에요. 지역마다 행 두 개를 센 높이예요.', 'output')
      .say('조심하세요. 지금은 두 지역의 건수가 같아요. 막대가 세는 것인지 평균인지는 함수와 y로 판단해요.', 'code:sns.countplot'))

s2 = HEAD + '# 이 줄을 고쳐 개수 대신 지역별 평균 시간을 막대로 그리세요. y에 시간 열을 연결해요.\nax = sns.countplot(data=df, x="region", order=["north", "south"])\n' + HEIGHTS
s2_sol = s2.replace('ax = sns.countplot(data=df, x="region", order=["north", "south"])',
                    '# barplot은 y 열을 x의 값마다 평균 내요. errorbar=None은 오차 막대를 그리지 않아요.\nax = sns.barplot(data=df, x="region", y="minutes", order=["north", "south"], errorbar=None)')
n2 = (Script(s2)
      .say('이번에는 시간 열을 y에 연결해 평균을 보려 해요. countplot 줄을 고쳐야 해요.', 'text:ax 줄을 고쳐 개수 대신 지역별 평균 시간을 막대로 그리세요.')
      .run('print([round')
      .say('[2.0, 2.0]이에요. 지역별 배송 개수예요.', 'output')
      .patch('ax = sns.countplot(data=df, x="region", order=["north", "south"])',
             'ax = sns.barplot(data=df, x="region", y="minutes", order=["north", "south"], errorbar=None)', 'barplot으로 바꾸고 y="minutes"와 errorbar=None을 넣어요.')
      .run('print([round')
      .say('[15.0, 40.0]이에요. north와 south의 평균 시간이에요.', 'output')
      .say('조심하세요. barplot의 기본 통계는 합계가 아니라 평균이에요.', 'code:sns.barplot'))

s3 = (HEAD + '# 경계 0, 20, 60으로 구간 두 개를 만들어 세어요.\ncounts, edges, bars = plt.hist(df["minutes"], bins=[0, 20, 60])\nprint(counts.tolist())\n'
      '# 이 줄의 옵션을 고쳐 hist처럼 왼쪽 경계를 포함하는 구간으로 나누세요.\ngroups = pd.cut(df["minutes"], bins=[0, 20, 60], right=True)\n'
      'print(groups.value_counts(sort=False).tolist())\nplt.show()\n')
s3_sol = s3.replace('groups = pd.cut(df["minutes"], bins=[0, 20, 60], right=True)',
                    '# right=False면 [0, 20), [20, 60)처럼 왼쪽 경계를 포함해요. 20은 둘째 구간이에요.\ngroups = pd.cut(df["minutes"], bins=[0, 20, 60], right=False)')
n3 = (Script(s3)
      .say('경계에 딱 걸린 20이 어느 쪽에 세어지는지 봐요. pd.cut의 경계 옵션을 고쳐 hist와 맞춰야 해요.', 'text:groups 줄의 옵션을 고쳐 hist처럼 왼쪽 경계를 포함하는 구간으로 나누세요.')
      .run('print(counts', 'print(groups')
      .say('hist는 [1.0, 3.0]인데 pd.cut은 [2, 2]예요. right=True는 20을 첫 구간에 넣었어요.', 'output')
      .patch('right=True', 'right=False', 'right를 False로 바꿔요.')
      .run('print(counts', 'print(groups')
      .say('둘 다 1과 3이에요. hist도 20을 20부터 60까지의 둘째 구간에 셌어요.', 'output')
      .say('조심하세요. hist의 마지막 구간만 오른쪽 끝 값도 포함해요. 그 앞 구간들은 오른쪽 경계를 빼요.', 'code:right=False'))

s4 = (HEAD + '# 폭이 다른 두 구간에서 밀도와 면적을 나눠 봐요.\nheights, edges, bars = plt.hist(df["minutes"], bins=[0, 20, 60], density=True)\nprint(heights.tolist())\n'
      'widths = edges[1:] - edges[:-1]\n# 이 줄을 고쳐 첫 막대의 높이가 아니라 면적(너비×높이)을 share에 담으세요.\nshare = heights[0]\nprint(round(float(share), 5))\nplt.show()\n')
s4_sol = s4.replace('share = heights[0]\n', '# 밀도 막대에서는 면적이 그 구간에 든 관측의 비율이에요.\nshare = heights[0] * widths[0]\n')
n4 = (Script(s4)
      .say('개수 대신 밀도를 그렸어요. 0부터 20분 구간의 비율은 첫 막대의 면적이라 share 줄을 고쳐야 해요.', 'text:share 줄을 고쳐 첫 막대의 높이가 아니라 면적(너비×높이)을 share에 담으세요.')
      .run('print(heights', 'print(round')
      .say('높이는 0.0125와 0.01875이고 share도 0.0125예요. 높이만으로는 비율이 아니에요.', 'output')
      .patch('share = heights[0]\n', 'share = heights[0] * widths[0]\n', '첫 막대 높이에 너비 widths[0]을 곱해요.')
      .run('print(heights', 'print(round')
      .say('0.25예요. 네 배송 중 10분 한 건이 첫 구간이에요.', 'output')
      .say('조심하세요. 밀도 막대는 높이의 합이 아니라 면적의 합이 1이에요.', 'code:heights[0] * widths[0]'))

s5 = (HEAD + '# 이 줄의 옵션을 고쳐 전체가 아니라 지역마다 따로 비율을 내세요.\n'
      'ax = sns.histplot(data=df, x="minutes", hue="region", bins=[0, 20, 60], stat="probability", multiple="dodge", common_norm=True)\n'
      + HEIGHTS.replace('print([round(float(p.get_height()), 5) for p in ax.patches])', 'print(sorted(round(float(p.get_height()), 5) for p in ax.patches))'))
s5_sol = s5.replace('common_norm=True)', 'common_norm=False)').replace('# 이 줄의 옵션을 고쳐 전체가 아니라 지역마다 따로 비율을 내세요.\n',
                                                                   '# 이 줄의 옵션을 고쳐 전체가 아니라 지역마다 따로 비율을 내세요.\n# common_norm=False면 지역마다 그 지역의 관측 수를 분모로 써요.\n')
n5 = (Script(s5)
      .say('지금은 전체 관측을 분모로 지역을 나눴어요. common_norm 옵션을 고쳐 지역마다 따로 비율을 내야 해요.', 'text:ax 줄의 옵션을 고쳐 전체가 아니라 지역마다 따로 비율을 내세요.')
      .run('print(sorted')
      .say('[0.0, 0.25, 0.25, 0.5]예요. 막대 넷의 합이 1이라 전체 네 건을 분모로 나눴어요.', 'output')
      .patch('common_norm=True)', 'common_norm=False)', 'common_norm을 False로 바꿔요.')
      .run('print(sorted')
      .say('[0.0, 0.5, 0.5, 1.0]이에요. north는 0.5와 0.5, south는 0.0과 1.0으로 지역마다 합이 1이에요.', 'output')
      .say('조심하세요. 비율을 비교할 때는 분모가 전체인지 그룹인지 먼저 확인해요.', 'code:common_norm=False'))

OVER = HEAD.replace('"minutes": [10, 20, 30, 50], "distance": [1, 2, 3, 4]', '"minutes": [10, 10, 20, 30], "distance": [1, 1, 2, 3]') \
    .replace('# 같은 배송표에서 개수와 측정값을 나눠 봐요.', '# 첫 두 배송은 거리와 시간이 같아 같은 좌표에 겹쳐요.')
s6 = (OVER + 'ax = sns.scatterplot(data=df, x="distance", y="minutes", alpha=0.5)\n# 확인용 출력: 그림에서 서로 다른 점 위치의 수예요.\n'
      'print(len(df.drop_duplicates(subset=["distance", "minutes"])))\n# 이 줄을 고쳐 점 위치의 수가 아니라 그린 배송 건수를 count에 담으세요.\n'
      'count = len(df.drop_duplicates(subset=["distance", "minutes"]))\nprint(count)\nplt.show()\n')
s6_sol = s6.replace('count = len(df.drop_duplicates(subset=["distance", "minutes"]))', '# 겹친 점도 각각 한 건의 배송이에요. 그린 행 수를 그대로 세요.\ncount = len(df)')
n6 = (Script(s6)
      .say('점 위치가 세 곳만 보여요. 그래도 그린 배송 건수를 count에 담아야 해요.', 'text:count 줄을 고쳐 점 위치의 수가 아니라 그린 배송 건수를 count에 담으세요.')
      .run('print(len(df.drop', 'print(count)')
      .say('두 줄 모두 3이에요. 겹친 두 배송을 한 곳으로 셌어요.', 'output')
      .patch('count = len(df.drop_duplicates(subset=["distance", "minutes"]))', 'count = len(df)', 'len(df)로 그린 행 수를 세요.')
      .run('print(len(df.drop', 'print(count)')
      .say('3과 4예요. 네 배송이 세 위치에 겹쳐 그려졌어요.', 'output')
      .say('조심하세요. 겹친 점은 alpha로 진하게 보여요. 점 위치 수를 자료 수로 읽지 않아요.', 'code:alpha=0.5'))

BOX = ('import matplotlib.pyplot as plt\n\n# 이 배송 시간 다섯 개는 정상 관측으로 확인했어요.\nminutes = [10, 11, 12, 13, 100]\n'
       '# 이 두 줄을 고쳐 100을 지우지 말고 그림에서만 후보 점을 숨기세요.\nminutes = [m for m in minutes if m < 100]\nparts = plt.boxplot(minutes)\n'
       'print(len(minutes), max(minutes))\n# 확인용 출력: 그림에 그린 후보 점 묶음의 수예요.\nprint(len(parts["fliers"]))\nplt.show()\n')
s7 = BOX
s7_sol = BOX.replace('minutes = [m for m in minutes if m < 100]\nparts = plt.boxplot(minutes)\n',
                     '# 자료는 그대로 두고, showfliers=False로 그림의 후보 점 표시만 숨겨요.\nparts = plt.boxplot(minutes, showfliers=False)\n')
n7 = (Script(s7)
      .say('후보 점을 그림에서만 숨기려 해요. 자료에서 100을 지우는 줄과 boxplot 줄을 고쳐야 해요.', 'text:두 줄을 고쳐 100을 지우지 말고 그림에서만 후보 점을 숨기세요.')
      .run('print(len(minutes)', 'print(len(parts')
      .say('4 13과 1이에요. 100이 자료에서 지워졌어요.', 'output')
      .patch('minutes = [m for m in minutes if m < 100]\nparts = plt.boxplot(minutes)\n', 'parts = plt.boxplot(minutes, showfliers=False)\n',
             '지우는 줄을 빼고 boxplot에 showfliers=False를 넣어요.')
      .run('print(len(minutes)', 'print(len(parts')
      .say('5 100과 0이에요. 다섯 자료와 100은 남고, 후보 점 표시만 숨겼어요.', 'output')
      .say('조심하세요. 상자 그림의 수염과 상자는 숨긴 점까지 포함한 자료로 계산돼요.', 'code:showfliers=False'))

s8 = (HEAD + '# 이 줄을 고쳐 원시값 대신 거리와 시간의 상관계수 표를 색칠하세요.\nmatrix = df[["distance", "minutes"]]\nsns.heatmap(matrix, annot=True)\n'
      'print(matrix.shape)\nprint(matrix.round(3).values.tolist())\nplt.show()\n')
s8_sol = s8.replace('matrix = df[["distance", "minutes"]]\n', '# heatmap은 받은 표를 그대로 색칠해요. 상관계수는 corr()로 먼저 계산해요.\nmatrix = df[["distance", "minutes"]].corr()\n')
n8 = (Script(s8)
      .say('heatmap이 상관을 보여 주게 하려 해요. 넘기는 표를 상관계수 표로 고쳐야 해요.', 'text:matrix 줄을 고쳐 원시값 대신 거리와 시간의 상관계수 표를 색칠하세요.')
      .run('print(matrix.shape)', 'print(matrix.round')
      .say('(4, 2)와 원래 거리·시간 값 네 행이에요. 원시값을 그대로 색칠했어요.', 'output')
      .patch('matrix = df[["distance", "minutes"]]\n', 'matrix = df[["distance", "minutes"]].corr()\n', '뒤에 .corr()를 붙여요.')
      .run('print(matrix.shape)', 'print(matrix.round')
      .say('(2, 2)와 대각선 1.0, 거리와 시간의 상관 0.983이에요.', 'output')
      .say('조심하세요. heatmap은 계산하지 않고 칠하기만 해요. 무엇을 넘겼는지 확인해요.', 'code:.corr()'))

s9 = (HEAD + 'ax = sns.barplot(data=df, x="region", y="minutes", order=["north", "south"], errorbar=None)\n'
      '# 이 줄을 고쳐 세로축 이름을 실제 통계에 맞는 "Mean minutes"로 바꾸세요.\nax.set_ylabel("Orders")\nprint(ax.get_ylabel())\n' + HEIGHTS)
s9_sol = s9.replace('ax.set_ylabel("Orders")', '# 막대는 평균 시간이에요. 축 이름도 그 통계를 말해야 해요.\nax.set_ylabel("Mean minutes")')
n9 = (Script(s9)
      .say('평균 시간 막대인데 세로축 이름은 Orders예요. 축 이름을 고쳐야 해요.', 'text:set_ylabel 줄을 고쳐 세로축 이름을 실제 통계에 맞는 "Mean minutes"로 바꾸세요.')
      .run('print(ax.get_ylabel())', 'print([round')
      .say('Orders와 [15.0, 40.0]이에요. 높이는 평균 시간인데 이름은 주문 수예요.', 'output')
      .patch('ax.set_ylabel("Orders")', 'ax.set_ylabel("Mean minutes")', '이름을 "Mean minutes"로 바꿔요.')
      .run('print(ax.get_ylabel())', 'print([round')
      .say('Mean minutes와 [15.0, 40.0]이에요. 같은 막대를 정확한 이름으로 설명해요.', 'output')
      .say('조심하세요. 축 이름은 그림을 고치지 않아요. 그린 통계를 먼저 확인하고 이름을 맞춰요.', 'code:ax.set_ylabel("Mean minutes")'))

SPECS = [
    step('stp_7b5e40c5-b3eb-4c86-a29e-afceacc720d4', 'countplot으로 지역별 배송 개수를 그리세요', '막대가 행의 개수를 세는 그래프를 직접 그려요.',
              'barplot(y="minutes")는 [15.0, 40.0] 평균이다. countplot으로 고쳐 [2.0, 2.0] 개수를 확인한다. 채점은 지역별 건수가 다른 표로 실행한다.',
              '같은 표에서 지역별 막대를 그려요. `sns.countplot(x=열)`은 그 열의 값마다 행을 세어 높이로 그리고, `sns.barplot(x=열, y=열)`은 y 값을 평균 내요.',
              'ax 줄을 고쳐 평균 시간 대신 지역별 배송 개수를 막대로 그리세요. 지역 순서는 north, south예요. 채점은 다른 배송표로도 실행해요.',
              ['코드 실행을 눌러 막대 높이를 확인하세요.', '`sns.barplot(...)`을 `sns.countplot(data=df, x="region", order=["north", "south"])`로 고치세요.', '코드 실행을 눌러 막대 높이가 개수인지 확인하세요.', SUBMIT],
              s1, s1_sol, n1, {n1.actions[-1]['text']: '실제 위험(건수가 같으면 우연히 비슷함, 채점 표는 건수가 달라요)을 정확히 말해요.'}, cases=OTHER,
              reject=[([['ax = sns.countplot(data=df, x="region", order=["north", "south"])', 'ax = sns.barplot(data=df, x="region", y="minutes", order=["north", "south"], errorbar=None, estimator="sum")']], 'Sum of minutes'),
                      ([['print([round(float(p.get_height()), 5) for p in ax.patches])', 'print([2.0, 2.0])']], 'Typing the heights')],
              accept=[([['ax = sns.countplot(data=df, x="region", order=["north", "south"])', 'ax = sns.countplot(x=df["region"], order=["north", "south"])']], 'Passing the column itself')]),
    step('stp_e057e76a-a2ed-4edd-ae7c-6450c000b849', 'barplot에 y="minutes"로 지역별 평균 시간을 그리세요', '막대가 y 열의 평균을 그리는 그래프를 직접 그려요.',
              'countplot은 [2.0, 2.0] 개수다. barplot(y="minutes", errorbar=None)로 고쳐 [15.0, 40.0] 평균을 확인한다. 채점은 다른 표로 실행한다.',
              '이번에는 시간 열을 y에 연결해요. `sns.barplot(x=열, y=열)`은 x의 값마다 y 값을 평균 내어 높이로 그려요. `errorbar=None`은 오차 막대를 그리지 않아요.',
              'ax 줄을 고쳐 개수 대신 지역별 평균 시간을 막대로 그리세요. 채점은 다른 배송표로도 실행해요.',
              ['코드 실행을 눌러 막대 높이를 확인하세요.', '`sns.countplot(...)`을 `sns.barplot(data=df, x="region", y="minutes", order=["north", "south"], errorbar=None)`로 고치세요.', '코드 실행을 눌러 막대 높이가 평균인지 확인하세요.', SUBMIT],
              s2, s2_sol, n2, {n2.actions[-1]['text']: W}, cases=OTHER,
              reject=[([['errorbar=None)', 'errorbar=None, estimator="sum")']], 'Sum instead of mean'),
                      ([['print([round(float(p.get_height()), 5) for p in ax.patches])', 'print([15.0, 40.0])']], 'Typing the heights')],
              accept=[([['errorbar=None)', 'errorbar=None, estimator="mean")']], 'Explicit mean')]),
    step('stp_47832dfe-6f32-417e-8567-89ecaa5c5c80', 'pd.cut(right=False)로 hist와 같은 구간을 세세요', '구간 경계값이 어느 구간에 세어지는지 확인해요.',
              'hist는 [1.0, 3.0]인데 pd.cut(right=True)는 20을 첫 구간에 넣어 [2, 2]다. right=False로 고쳐 [1, 3]을 확인한다. 채점은 경계값이 든 다른 표로 실행한다.',
              '시간을 두 구간으로 나눴어요. bins=[0, 20, 60]은 경계 세 개로 구간 두 개를 만들어요. `plt.hist`는 각 구간에 왼쪽 경계를 포함하고 오른쪽 경계는 빼요(마지막 구간만 끝 값도 포함). `pd.cut`의 `right=False`도 왼쪽 경계를 포함해요.',
              'groups 줄의 옵션을 고쳐 hist처럼 왼쪽 경계를 포함하는 구간으로 나누세요. 채점은 경계값이 든 다른 배송표로도 실행해요.',
              ['코드 실행을 눌러 두 개수를 비교하세요.', '`right=True`를 `right=False`로 고치세요.', '코드 실행을 눌러 두 개수가 같은지 확인하세요.', SUBMIT],
              s3, s3_sol, n3, {n3.actions[-1]['text']: '실제 matplotlib 구간 규칙(마지막 구간 양끝 포함)을 정확히 말해요.'},
              cases=[{'data': {'region': ['north', 'south', 'south', 'north', 'south'], 'minutes': [20, 20, 0, 19, 45], 'distance': [1, 2, 3, 4, 5]}},
                     {'data': {'region': ['north', 'south', 'north'], 'minutes': [5, 21, 33], 'distance': [1, 2, 3]}}],
              reject=[([['right=False)', 'right=True)']], 'Right edge included'),
                      ([['print(groups.value_counts(sort=False).tolist())', 'print([1, 3])']], 'Typing the counts')],
              accept=[([['groups = pd.cut(df["minutes"], bins=[0, 20, 60], right=False)', 'groups = pd.cut(df["minutes"], [0, 20, 60], right=False)']], 'Positional bins')]),
    step('stp_f3cd7df9-114e-4929-b956-7be6fa044909', '밀도 막대의 면적으로 첫 구간의 비율을 구하세요', '밀도 그래프에서 비율은 높이가 아니라 면적임을 계산해 확인해요.',
              'density=True 막대에서 heights[0]은 0.0125다. 너비를 곱한 heights[0] * widths[0]으로 고쳐 0.25를 확인한다. 채점은 다른 표로 실행한다.',
              '이번에는 개수 대신 밀도를 그렸어요. 밀도 막대는 높이에 너비를 곱한 면적이 그 구간에 든 관측의 비율이에요. `widths`에 막대 너비가 들어 있어요.',
              'share 줄을 고쳐 첫 막대의 높이가 아니라 면적(너비×높이)을 share에 담으세요. 채점은 다른 배송표로도 실행해요.',
              ['코드 실행을 눌러 높이와 share를 확인하세요.', '`heights[0]`을 `heights[0] * widths[0]`로 고치세요.', '코드 실행을 눌러 첫 구간의 비율을 확인하세요.', SUBMIT],
              s4, s4_sol, n4, {n4.actions[-1]['text']: W}, cases=OTHER,
              reject=[([['share = heights[0] * widths[0]\n', 'share = heights[0]\n']], 'Height only'),
                      ([['share = heights[0] * widths[0]\n', 'share = 0.25\n']], 'Typing the share')],
              accept=[([['share = heights[0] * widths[0]\n', 'share = (df["minutes"] < 20).mean()\n']], 'Counting the share directly')]),
    step('stp_dec3abb2-9301-43c9-be23-39c999ce7beb', 'common_norm=False로 지역마다 따로 비율을 내세요', '비율의 분모를 전체와 그룹 중에서 정해요.',
              '구간 두 개에서 common_norm=True는 전체 네 건을 분모로 막대 넷의 합이 1이다. False로 고쳐 지역마다 합이 1인 [0.0, 0.5, 0.5, 1.0]을 확인한다. 채점은 지역별 건수가 다른 표로 실행한다.',
              '두 구간에 지역별 관측 비율을 나눠 그렸어요. `common_norm=True`는 전체 관측 수를 분모로, `common_norm=False`는 지역마다 그 지역의 관측 수를 분모로 써요.',
              'ax 줄의 옵션을 고쳐 전체가 아니라 지역마다 따로 비율을 내세요. 채점은 다른 배송표로도 실행해요.',
              ['코드 실행을 눌러 막대 높이를 확인하세요.', '`common_norm=True`를 `common_norm=False`로 고치세요.', '코드 실행을 눌러 지역마다 합이 1인지 확인하세요.', SUBMIT],
              s5, s5_sol, n5, {n5.actions[-1]['text']: '실제 분석 습관을 정확히 말해요.'},
              cases=OTHER,
              reject=[([['common_norm=False)', 'common_norm=True)']], 'Shared denominator'),
                      ([['print(sorted(round(float(p.get_height()), 5) for p in ax.patches))', 'print([0.0, 0.5, 0.5, 1.0])']], 'Typing the heights')],
              accept=[([['stat="probability"', 'stat="proportion"']], 'proportion is the same statistic')]),
    step('stp_9c37861b-82de-44dd-99a7-ebd4e716e5ff', 'len(df)로 겹친 점까지 배송 건수를 세세요', '겹쳐 보이는 점도 각각의 관측임을 세어 확인해요.',
              '점 위치 수와 count가 모두 3이다. count = len(df)로 고쳐 4를 확인한다. 네 배송이 세 위치에 겹친다. 채점은 겹침이 다른 표로 실행한다.',
              '첫 두 배송의 거리와 시간이 같아 점 위치가 세 곳만 보여요. 같은 좌표의 점은 겹쳐 그려지고 `alpha=0.5`라서 진하게 보여요.',
              'count 줄을 고쳐 점 위치의 수가 아니라 그린 배송 건수를 count에 담으세요. 채점은 다른 배송표로도 실행해요.',
              ['코드 실행을 눌러 두 줄을 확인하세요.', '`count = len(df.drop_duplicates(...))`를 `count = len(df)`로 고치세요.', '코드 실행을 눌러 점 위치 수와 배송 건수를 비교하세요.', SUBMIT],
              s6, s6_sol, n6, {n6.actions[-1]['text']: W},
              cases=[{'data': {'region': ['north', 'south', 'south', 'north', 'south'], 'minutes': [5, 5, 5, 9, 9], 'distance': [1, 1, 1, 2, 2]}},
                     {'data': {'region': ['north', 'south'], 'minutes': [3, 8], 'distance': [1, 2]}}],
              reject=[([['count = len(df)', 'count = len(df.drop_duplicates(subset=["distance", "minutes"]))']], 'Distinct positions'),
                      ([['count = len(df)', 'count = 4']], 'Typing the count')],
              accept=[([['count = len(df)', 'count = len(ax.collections[0].get_offsets())']], 'Points actually drawn')]),
    step('stp_2d3886de-c0ca-44f4-b427-480c7675db90', 'showfliers=False로 자료는 두고 표시만 숨기세요', '그림의 표시를 숨기는 것과 자료를 지우는 것을 구별해요.',
              '목록에서 100을 지우면 4 13과 후보 묶음 1이다. 지우는 줄을 빼고 showfliers=False로 고쳐 5 100과 0을 확인한다. 채점은 다른 시간 목록으로 실행한다.',
              '이 배송 시간 다섯 개는 정상 관측으로 확인했어요. 100은 상자 그림에서 후보 점으로 표시돼요. `plt.boxplot(자료, showfliers=False)`는 자료를 그대로 두고 후보 점 표시만 숨겨요.',
              '두 줄을 고쳐 100을 지우지 말고 그림에서만 후보 점을 숨기세요. 채점은 다른 시간 목록으로도 실행해요.',
              ['코드 실행을 눌러 남은 자료 수와 최댓값을 확인하세요.', '`minutes = [m for m ...]` 줄을 지우세요.', '`plt.boxplot(minutes)`를 `plt.boxplot(minutes, showfliers=False)`로 고치세요.', '코드 실행을 눌러 자료가 그대로인지 확인하세요.', SUBMIT],
              s7, s7_sol, n7, {n7.actions[-1]['text']: '실제 matplotlib 계산(표시만 숨김)을 정확히 말해요.'},
              cases=[{'minutes': [3, 40, 41, 42, 43, 44]}, {'minutes': [100, 104, 106, 108, 250]}, {'minutes': [7, 8, 9]}],
              reject=[([['parts = plt.boxplot(minutes, showfliers=False)\n', 'minutes = [m for m in minutes if m < 100]\nparts = plt.boxplot(minutes, showfliers=False)\n']], 'Still deleting 100'),
                      ([['parts = plt.boxplot(minutes, showfliers=False)\n', 'parts = plt.boxplot(minutes)\n']], 'Showing the candidates')],
              accept=[([['parts = plt.boxplot(minutes, showfliers=False)\n', 'parts = plt.gca().boxplot(list(minutes), showfliers=False)\n']], 'Axes method on a copy')]),
    step('stp_772a6640-96bb-4784-a2d5-c0372575a277', 'corr()로 상관계수 표를 heatmap에 넘기세요', 'heatmap에 무엇을 계산해 넘길지 정해요.',
              '원시값 표는 (4, 2)로 그대로 색칠된다. df[["distance", "minutes"]].corr()로 고쳐 (2, 2) 상관 표를 확인한다. 채점은 다른 표로 실행한다.',
              '표를 heatmap에 넘기면 받은 표의 숫자를 그대로 색칠해요. 거리와 시간의 상관을 보려면 `.corr()`로 상관계수 표를 먼저 계산해 넘겨요.',
              'matrix 줄을 고쳐 원시값 대신 거리와 시간의 상관계수 표를 색칠하세요. 채점은 다른 배송표로도 실행해요.',
              ['코드 실행을 눌러 표의 크기와 값을 확인하세요.', '`df[["distance", "minutes"]]` 뒤에 `.corr()`를 붙이세요.', '코드 실행을 눌러 2×2 상관 표를 확인하세요.', SUBMIT],
              s8, s8_sol, n8, {n8.actions[-1]['text']: W}, cases=OTHER,
              reject=[([['matrix = df[["distance", "minutes"]].corr()\n', 'matrix = df[["distance", "minutes"]].cov()\n']], 'Covariance'),
                      ([['matrix = df[["distance", "minutes"]].corr()\n', 'matrix = df[["distance", "minutes"]]\n']], 'Raw values')],
              accept=[([['matrix = df[["distance", "minutes"]].corr()\n', 'matrix = df[["distance", "minutes"]].corr(method="pearson")\n']], 'Explicit Pearson')]),
    step('stp_23611ddd-8d1c-4cbc-ae80-a65feaaa3961', 'set_ylabel을 실제 통계에 맞게 고치세요', '그래프의 축 이름을 그린 통계에 맞춰요.',
              '평균 시간 막대의 세로축 이름이 Orders다. "Mean minutes"로 고쳐 같은 막대 [15.0, 40.0]를 정확히 설명한다. 채점은 다른 표로 실행한다.',
              '평균 시간 막대인데 세로축 이름은 Orders예요. 축 이름은 그린 통계를 말해야 해요. `ax.set_ylabel(이름)`이 세로축 이름을 정해요.',
              'set_ylabel 줄을 고쳐 세로축 이름을 실제 통계에 맞는 "Mean minutes"로 바꾸세요. 채점은 다른 배송표로도 실행해요.',
              ['코드 실행을 눌러 축 이름과 막대 높이를 확인하세요.', '`"Orders"`를 `"Mean minutes"`로 고치세요.', '코드 실행을 눌러 축 이름이 바뀌었는지 확인하세요.', SUBMIT],
              s9, s9_sol, n9, {n9.actions[-1]['text']: '실제 matplotlib 의미를 정확히 말해요.'}, cases=OTHER,
              reject=[([['ax.set_ylabel("Mean minutes")', 'ax.set_ylabel("Orders")']], 'Wrong label'),
                      ([['ax = sns.barplot(data=df, x="region", y="minutes", order=["north", "south"], errorbar=None)', 'ax = sns.countplot(data=df, x="region", order=["north", "south"])']], 'Relabeling a count plot')],
              accept=[([['ax.set_ylabel("Mean minutes")', 'ax.set(ylabel="Mean minutes")']], 'Axes.set')]),
]
