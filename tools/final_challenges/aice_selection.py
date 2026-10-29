"""aice-selection final challenge: two conditions with an inclusive boundary, a descending sort and a summary of the selection."""
from _common import Script, todo, ids, next_revision

KEY = 'aice-selection'
UNIT, STEP = ids(KEY)
PICK_TODO = 'selected = df  # 1) 기준 이상이면서 north인 배송만 고르세요.'
ORDER_TODO = 'ordered = selected  # 2) 오래 걸린 순서로 정렬하세요.'
SUMMARY_TODO = 'print(0, 0)  # 3) 고른 배송 시간의 평균과 가운데 값을 출력하세요.'
STARTER = f'''# 표를 다룰 판다스를 불러와요.
import pandas as pd
# 배송 시간과 지역이에요. 행 이름은 주문 번호예요.
data = {{"minutes": [30, 18, 45, 33, 52, 41], "region": ["north", "south", "north", "north", "south", "north"]}}
order_ids = [101, 102, 103, 104, 105, 106]
df = pd.DataFrame(data, index=order_ids)
# 기준과 같은 시간도 고르는 대상이에요.
limit = 30
{PICK_TODO}
{ORDER_TODO}
print(ordered.index.tolist())
{SUMMARY_TODO}
'''
PICK_WRONG = 'selected = df.loc[df["minutes"] >= limit]'
PICK = '''# 두 조건은 각각 괄호로 묶고 &로 이어요.
selected = df.loc[(df["minutes"] >= limit) & (df["region"] == "north")]'''
ORDER = '# ascending=False가 큰 값부터예요.\nordered = selected.sort_values("minutes", ascending=False)'
SUMMARY = '# 요약은 고른 배송만 대상으로 해요.\nprint(selected["minutes"].mean(), selected["minutes"].median())'
SOLUTION = STARTER.replace(PICK_TODO, PICK).replace(ORDER_TODO, ORDER).replace(SUMMARY_TODO, SUMMARY)

s = Script(STARTER)
s.say('마지막 도전이에요. 기준 이상이면서 north인 배송만 골라 오래 걸린 순서로 보고, 고른 배송의 평균과 가운데 값을 출력해요.',
      'text:기준과 같은 시간도 골라요.')
s.run()
s.say('여섯 주문이 원래 순서로 나오고 요약은 0이에요.', 'output')
s.patch(PICK_TODO, PICK_WRONG, '먼저 시간 조건만 걸어 볼게요.')
s.run()
s.say('south 주문 105도 섞였어요. 지역 조건이 빠졌어요.', 'output')
s.patch(PICK_WRONG, PICK, '지역 조건을 &로 더해요.')
s.patch(ORDER_TODO, ORDER, '오래 걸린 순서는 내림차순이에요.')
s.patch(SUMMARY_TODO, SUMMARY, '평균과 가운데 값은 고른 표에서 구해요.')
s.run()
s.say('103, 106, 104, 101 순서이고 평균 37.25, 가운데 값 37.0이에요. 기준과 같은 30분인 101도 들어갔어요.', 'output')
s.say('조심하세요. 요약을 df로 구하면 고르지 않은 south 배송까지 섞여 다른 평균이 나와요.', 'code:print(selected["minutes"].mean(), selected["minutes"].median())')

GOAL = ('자, 마지막 도전이에요. 배송 시간과 지역 표 df가 있어요. 행 이름은 주문 번호예요.\n\n'
        '배송 시간이 limit 이상이면서 지역이 north인 배송만 고르세요. 기준과 같은 시간도 골라요. '
        '고른 배송을 오래 걸린 순서로 정렬해 주문 번호 목록을 출력하고, 다음 줄에 고른 배송 시간의 평균과 가운데 값을 출력해요. '
        '지금 자료이면 `[103, 106, 104, 101]`, `37.25 37.0`이에요. 채점은 다른 자료와 기준으로도 실행해요.\n\n'
        + todo('코드 실행을 눌러 지금 출력을 확인하세요.',
               '두 조건으로 배송을 고르세요.',
               '고른 배송을 오래 걸린 순서로 정렬하세요.',
               '고른 배송 시간의 평균과 가운데 값을 출력하세요.',
               '다시 실행해 결과를 확인한 뒤 제출하세요.'))

SPEC = dict(
    key=KEY, course='aice', revision=next_revision(KEY, 'aice-selection-5'),
    reason='경계를 포함한 조건, 두 조건의 결합, 내림차순 정렬, 고른 자료만의 평균·중앙값을 한 표에서 함께 쓰는 마지막 도전이에요.',
    grading='실제 파이썬 출력과 다른 자료·기준 세 가지로 채점해요. > 경계, 지역 조건 누락, 오름차순, 전체 표 요약은 실패해요.',
    unit=dict(id=UNIT, title='마지막 도전', objectives=['조건·정렬·요약을 이어 필요한 배송을 보고해요.'],
              premise='여섯 배송의 시간과 지역 표예요. 앞 스텝과 상관없이 바로 풀 수 있어요.'),
    step=dict(id=STEP, title='두 조건으로 고르고 정렬해 요약하세요',
              objectives=['경계 포함 조건과 지역 조건으로 고르고 고른 자료만 요약해요.'],
              core_flow='준비 코드는 전체 표와 0을 출력한다. 학생은 (>= limit) & (== north), sort_values(ascending=False), mean·median을 쓴다. '
                        '해설은 지역 조건이 빠진 실제 결과를 보여 준다. 채점: 경계값만 맞는 자료, 고를 것이 하나인 자료, 다른 기준.'),
    task=dict(id=STEP, title='두 조건으로 고르고 정렬해 요약하세요', language='python', goal=GOAL,
              starter_code=STARTER, solution=SOLUTION, required=True,
              tests=[dict(input='', expected='[103, 106, 104, 101]\n37.25 37.0')], narration=s.actions),
    prepared_cases=[dict(values=dict(data={'minutes': [20, 25, 31], 'region': ['north', 'north', 'south']}, order_ids=[1, 2, 3], limit=25), expected='[2]\n25.0 25.0'),
                    dict(values=dict(limit=40), expected='[103, 106]\n43.0 43.0'),
                    dict(values=dict(data={'minutes': [12, 50, 30, 41, 35, 60], 'region': ['north', 'north', 'south', 'north', 'north', 'south']}, order_ids=[11, 12, 13, 14, 15, 16], limit=35),
                         expected='[12, 14, 15]\n42.0 41.0')],
    cases=dict(expected_outputs=['[101, 102, 103, 104, 105, 106]\n0 0', '[101, 103, 104, 105, 106]\n0 0', '[103, 106, 104, 101]\n37.25 37.0'],
               reject=[([['(df["minutes"] >= limit)', '(df["minutes"] > limit)']], 'The limit itself is selected'),
                       ([['sort_values("minutes", ascending=False)', 'sort_values("minutes", ascending=True)']], 'Longest first means descending'),
                       ([['print(selected["minutes"].mean(), selected["minutes"].median())', 'print(df["minutes"].mean(), df["minutes"].median())']], 'Summarize only the selection'),
                       ([['selected = df.loc[(df["minutes"] >= limit) & (df["region"] == "north")]', 'selected = df.loc[df["minutes"] >= limit]']], 'Both conditions are required')],
               accept=[([['selected = df.loc[(df["minutes"] >= limit) & (df["region"] == "north")]', 'selected = df[(df["region"] == "north") & (df["minutes"] >= limit)]']], 'Boolean indexing without loc, conditions swapped')]),
    review={'조심하세요. 요약을 df로 구하면 고르지 않은 south 배송까지 섞여 다른 평균이 나와요.':
            '이 수업 7·8번의 요약 대상 구별을 이 도전의 결과로 말해요. 채점 사례가 잡아요.'},
)
