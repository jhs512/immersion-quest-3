"""aice-plots final challenge: pick finished deliveries, plot the mean time per region (not counts) longest first, name the axis."""
from _common import Script, todo, ids, next_revision

KEY = 'aice-plots'
UNIT, STEP = ids(KEY)
DONE_TODO = 'done = df  # 1) 배송이 끝난(done) 행만 고르세요.'
ORDER_TODO = 'order = ["north", "south", "west"]  # 2) 평균 시간이 긴 지역부터 순서를 정하세요.'
PLOT_TODO = 'ax = sns.countplot(data=done, x="region", order=order)  # 3) 지역별 평균 시간 막대로 바꾸세요.'
LABEL_TODO = 'ax.set_ylabel("count")  # 4) 세로축 이름을 평균 배송 시간(분)으로 고치세요.'
STARTER = f'''import pandas as pd
import seaborn as sns

# 배송 기록이에요. cancel은 취소돼 시간이 의미 없는 행이에요.
data = {{"region": ["north", "north", "south", "south", "south", "west"],
        "status": ["done", "done", "done", "cancel", "done", "done"],
        "minutes": [20, 40, 50, 5, 70, 35]}}
df = pd.DataFrame(data)
{DONE_TODO}
{ORDER_TODO}
{PLOT_TODO}
{LABEL_TODO}
print(order)
# 확인용 출력: 그려진 막대 높이를 숫자로 보여 줘요. 이 줄의 문법은 몰라도 돼요.
print([round(float(p.get_height()), 5) for p in ax.patches])
print(ax.get_ylabel())
'''
DONE = '# 취소된 배송은 시간이 의미 없어 빼요.\ndone = df[df["status"] == "done"]'
ORDER = ('# 지역마다 평균 시간을 구하고 긴 순서로 지역 이름만 꺼내요.\n'
         'order = done.groupby("region")["minutes"].mean().sort_values(ascending=False).index.tolist()')
PLOT_WRONG = 'ax = sns.barplot(data=done, x="region", y="minutes", order=order, estimator="sum", errorbar=None)'
PLOT = '# 막대 높이는 지역별 평균 시간이에요. 오차 막대는 그리지 않아요.\nax = sns.barplot(data=done, x="region", y="minutes", order=order, errorbar=None)'
LABEL = '# 축 이름이 막대가 무엇인지 말해 줘요.\nax.set_ylabel("평균 배송 시간(분)")'
SOLUTION = STARTER.replace(DONE_TODO, DONE).replace(ORDER_TODO, ORDER).replace(PLOT_TODO, PLOT).replace(LABEL_TODO, LABEL)

s = Script(STARTER)
s.say('마지막 도전이에요. 끝난 배송만으로 지역별 평균 배송 시간을 긴 순서로 그리고, 축 이름도 내용에 맞춰요.',
      'text:막대 높이는 건수가 아니라 평균 시간이에요.')
s.run()
s.say('막대가 2, 3, 1이에요. 시간이 아니라 행 수를 셌고, 취소된 배송까지 들어갔어요.', 'output')
s.patch(DONE_TODO, DONE, '먼저 끝난 배송만 골라요.')
s.patch(ORDER_TODO, ORDER, '평균 시간이 긴 지역부터 순서를 정해요.')
s.patch(PLOT_TODO, PLOT_WRONG, '시간 열을 세로축에 두고 합계로 그려 볼게요.')
s.run()
s.say('south, west, north 순서인데 막대는 120, 35, 60이에요. 배송이 많은 지역이 커 보여 순서와 높이가 어긋났어요.', 'output')
s.patch(PLOT_WRONG, PLOT, '합계 대신 기본값인 평균으로 그려요.')
s.patch(LABEL_TODO, LABEL, '세로축 이름도 평균 배송 시간으로 고쳐요.')
s.run()
s.say('60, 35, 30이 긴 순서로 섰고 축 이름도 평균 배송 시간(분)이에요.', 'output')
s.say('조심하세요. 취소 행을 남긴 채 평균을 내면 5분짜리 취소가 섞여 south 평균이 41.67로 내려가요.', 'code:done = df[df["status"] == "done"]')

GOAL = ('자, 마지막 도전이에요. 배송 기록 df에 끝난 배송(done)과 취소된 배송(cancel)이 섞여 있어요.\n\n'
        '끝난 배송만으로 지역별 평균 배송 시간을 막대로 그려요. 막대 높이는 건수가 아니라 평균 시간이에요. '
        '평균이 긴 지역부터 왼쪽에 두고, 세로축 이름은 `평균 배송 시간(분)`으로 해요. '
        '그러면 지역 순서, 막대 높이, 축 이름이 출력돼요. 지금 자료이면 `[\'south\', \'west\', \'north\']`, `[60.0, 35.0, 30.0]`, `평균 배송 시간(분)`이에요. '
        '채점은 다른 배송 기록으로도 실행해요.\n\n'
        + todo('코드 실행을 눌러 지금 막대가 무엇을 세는지 확인하세요.',
               '끝난 배송만 고르세요.',
               '평균 시간이 긴 지역부터 순서를 정하세요.',
               '지역별 평균 시간 막대로 바꾸고 세로축 이름을 고치세요.',
               '다시 실행해 순서와 막대 높이가 맞는지 확인한 뒤 제출하세요.'))

SPEC = dict(
    key=KEY, course='aice', revision=next_revision(KEY, 'aice-plots-5'),
    reason='그릴 행 고르기, 개수·합계·평균의 구별, 통계에서 정한 축 순서, 축 이름 검토를 새 배송 기록에 함께 쓰는 마지막 도전이에요.',
    grading='실제 파이썬 실행의 막대 높이·순서·축 이름과 다른 배송 기록 세 가지로 채점해요. 건수 막대, 합계 막대, 취소 행 포함, 짧은 순서는 실패해요.',
    unit=dict(id=UNIT, title='마지막 도전', objectives=['고른 행의 평균을 순서와 축 이름까지 맞게 그려요.'],
              premise='끝난 배송과 취소 배송이 섞인 기록이에요. 앞 스텝과 상관없이 바로 풀 수 있어요.'),
    step=dict(id=STEP, title='끝난 배송으로 지역별 평균 시간 막대를 만드세요',
              objectives=['행을 고르고 평균 막대를 긴 순서로 그려 축 이름까지 맞춰요.'],
              core_flow='준비 코드는 전체 행의 건수 막대를 그린다. 학생은 status 조건, groupby 평균 정렬로 순서, barplot(y=minutes, errorbar=None), set_ylabel을 쓴다. '
                        '해설은 건수 막대와 합계 막대의 실제 높이를 보여 준다. 채점: 다른 지역 수, 취소가 순서를 바꾸는 자료, 한 지역뿐인 자료.'),
    task=dict(id=STEP, title='끝난 배송으로 지역별 평균 시간 막대를 만드세요', language='python', goal=GOAL,
              starter_code=STARTER, solution=SOLUTION, required=True,
              tests=[dict(input='', expected="['south', 'west', 'north']\n[60.0, 35.0, 30.0]\n평균 배송 시간(분)")], narration=s.actions),
    prepared_timeout_seconds=30,
    prepared_cases=[dict(values=dict(data={'region': ['a', 'b', 'b', 'c'], 'status': ['done', 'done', 'done', 'done'], 'minutes': [10, 30, 50, 20]}),
                         expected="['b', 'c', 'a']\n[40.0, 20.0, 10.0]\n평균 배송 시간(분)"),
                    dict(values=dict(data={'region': ['x', 'x', 'y', 'y'], 'status': ['done', 'cancel', 'done', 'done'], 'minutes': [30, 0, 20, 30]}),
                         expected="['x', 'y']\n[30.0, 25.0]\n평균 배송 시간(분)"),
                    dict(values=dict(data={'region': ['east', 'east', 'east'], 'status': ['done', 'cancel', 'done'], 'minutes': [8, 90, 12]}),
                         expected="['east']\n[10.0]\n평균 배송 시간(분)")],
    cases=dict(expected_images=[1, 1, 1], expected_outputs=["['north', 'south', 'west']\n[2.0, 3.0, 1.0]\ncount",
                                 "['south', 'west', 'north']\n[120.0, 35.0, 60.0]\ncount",
                                 "['south', 'west', 'north']\n[60.0, 35.0, 30.0]\n평균 배송 시간(분)"],
               reject=[([['ax = sns.barplot(data=done, x="region", y="minutes", order=order, errorbar=None)',
                          'ax = sns.countplot(data=done, x="region", order=order)']], 'Bars are mean minutes, not counts'),
                       ([['errorbar=None)', 'estimator="sum", errorbar=None)']], 'Bars are means, not sums'),
                       ([['done = df[df["status"] == "done"]', 'done = df']], 'Cancelled rows are excluded'),
                       ([['sort_values(ascending=False)', 'sort_values()']], 'Longest mean first')],
               accept=[([['order = done.groupby("region")["minutes"].mean().sort_values(ascending=False).index.tolist()',
                          'means = done.groupby("region")["minutes"].mean()\norder = means.sort_values(ascending=False).index.tolist()']],
                         'The same order through a named Series')]),
    review={'조심하세요. 취소 행을 남긴 채 평균을 내면 5분짜리 취소가 섞여 south 평균이 41.67로 내려가요.':
            '이 수업의 「표시를 숨겨도 행은 남아요」와 분모 확인을 이 도전의 행 고르기로 말해요. 채점의 두 번째 사례가 실제로 순서를 바꿔요.'},
)
