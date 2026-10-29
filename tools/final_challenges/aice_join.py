"""aice-join final challenge: append two months, keep every delivery while joining regions, mark unknowns, count by zone."""
from _common import Script, todo, ids, next_revision

KEY = 'aice-join'
UNIT, STEP = ids(KEY)
ROWS_TODO = 'orders = pd.DataFrame(may)  # 1) 두 달 배송을 행으로 이어 붙이세요. 번호는 새로 매겨요.'
JOIN_TODO = 'joined = orders  # 2) 모든 배송을 남기며 회원 지역을 연결하세요.'
FILL_TODO = '# 3) 지역이 없는 배송은 unknown으로 표시하세요.'
STARTER = f'''import pandas as pd

# 5월과 6월 배송이에요. 회원 4와 5는 아직 지역 조회에 없어요.
may = {{"order_id": [201, 202], "member_id": [1, 4]}}
june = {{"order_id": [203, 204, 205], "member_id": [2, 5, 1]}}
region_data = {{"member_id": [1, 2], "zone": ["north", "south"]}}
regions = pd.DataFrame(region_data)
{ROWS_TODO}
{JOIN_TODO}
{FILL_TODO}
print(joined["order_id"].tolist())
# 지역별 배송 건수예요.
print(joined["zone"].value_counts().sort_index().to_dict())
'''
ROWS = '# 같은 열의 두 표를 위아래로 이어요.\norders = pd.concat([pd.DataFrame(may), pd.DataFrame(june)], ignore_index=True)'
JOIN_WRONG = 'joined = orders.merge(regions, on="member_id", how="inner")'
JOIN = '# 왼쪽 배송은 조회가 없어도 모두 남겨요.\njoined = orders.merge(regions, on="member_id", how="left")'
FILL = 'joined["zone"] = joined["zone"].fillna("unknown")'
SOLUTION = STARTER.replace(ROWS_TODO, ROWS).replace(JOIN_TODO, JOIN).replace(FILL_TODO, FILL)

s = Script(STARTER)
s.say('마지막 도전이에요. 두 달 배송을 이어 붙이고, 모든 배송을 남기며 지역을 연결한 뒤 지역별 건수를 세요.',
      'text:조회에 없는 회원의 배송도 모두 남겨야 해요.')
s.patch(JOIN_TODO, JOIN_WRONG, '먼저 5월 배송만으로 지역을 inner로 연결해 볼게요.')
s.run()
s.say('201 한 건만 남고 north 1이에요. 6월이 빠졌고 회원 4의 202도 사라졌어요.', 'output')
s.patch(ROWS_TODO, ROWS, '두 달을 concat으로 이어 붙여요.')
s.patch(JOIN_WRONG, JOIN, '조회가 없어도 남기도록 left로 바꿔요.')
s.run()
s.say('다섯 배송이 모두 남았어요. 그런데 건수는 north 2, south 1뿐이에요. 지역이 빈 두 건은 세지 않았어요.', 'output')
s.patch(FILL_TODO, FILL, '빈 지역을 unknown으로 채워요.')
s.run()
s.say('north 2, south 1, unknown 2예요. 다섯 건이 다 세어졌어요.', 'output')
s.say('조심하세요. ignore_index 없이 이어 붙이면 행 번호 0과 1이 두 번씩 생겨 위치로 고를 때 헷갈려요.', 'code:ignore_index=True')

GOAL = ('자, 마지막 도전이에요. 5월 배송 may와 6월 배송 june, 회원 지역 조회 regions가 있어요.\n\n'
        '두 달 배송을 행으로 이어 붙이고 회원 지역을 연결해요. 조회에 없는 회원의 배송도 모두 남겨야 해요. 지역이 없는 배송은 unknown으로 표시해요. '
        '그러면 주문 번호 목록과 지역별 건수가 출력돼요. 지금 자료이면 `[201, 202, 203, 204, 205]`, `{\'north\': 2, \'south\': 1, \'unknown\': 2}`예요. '
        '채점은 다른 배송과 조회 자료로도 실행해요.\n\n'
        + todo('두 달 배송을 행으로 이어 붙이세요.',
               '모든 배송을 남기며 회원 지역을 연결하세요.',
               '지역이 없는 배송을 unknown으로 표시하세요.',
               '코드 실행을 눌러 다섯 배송과 지역별 건수를 확인한 뒤 제출하세요.'))

SPEC = dict(
    key=KEY, course='aice', revision=next_revision(KEY, 'aice-join-5'),
    reason='행 추가(concat)와 키 결합(merge)의 구별, 원본 행 보존(left), 결측 키 표시, 집계까지 새 자료에서 함께 쓰는 마지막 도전이에요.',
    grading='실제 파이썬 출력과 다른 배송·조회 자료 세 가지로 채점해요. inner 결합, 한 달만 사용, 빈 지역을 세지 않기는 실패해요.',
    unit=dict(id=UNIT, title='마지막 도전', objectives=['붙이기와 연결을 구별해 모든 배송을 지역별로 세요.'],
              premise='두 달 배송과 회원 지역 조회예요. 앞 스텝과 상관없이 바로 풀 수 있어요.'),
    step=dict(id=STEP, title='두 달 배송을 붙이고 지역별로 세세요',
              objectives=['concat과 left merge로 모든 배송을 남겨 지역별로 세요.'],
              core_flow='준비 코드는 5월만 남기고 연결하지 않는다. 학생은 concat(ignore_index=True), merge(how="left"), fillna("unknown")을 쓴다. '
                        '해설은 inner와 빈 지역 미집계의 실제 결과를 차례로 보여 준다. 채점: 모두 조회되는 자료, 모두 미등록인 자료, 다른 지역 이름.'),
    task=dict(id=STEP, title='두 달 배송을 붙이고 지역별로 세세요', language='python', goal=GOAL,
              starter_code=STARTER, solution=SOLUTION, required=True,
              tests=[dict(input='', expected="[201, 202, 203, 204, 205]\n{'north': 2, 'south': 1, 'unknown': 2}")], narration=s.actions),
    prepared_cases=[dict(values=dict(may={'order_id': [1], 'member_id': [2]}, june={'order_id': [2], 'member_id': [1]}),
                         expected="[1, 2]\n{'north': 1, 'south': 1}"),
                    dict(values=dict(region_data={'member_id': [9], 'zone': ['west']}),
                         expected="[201, 202, 203, 204, 205]\n{'unknown': 5}"),
                    dict(values=dict(june={'order_id': [210], 'member_id': [2]}, region_data={'member_id': [1, 2], 'zone': ['east', 'east']}),
                         expected="[201, 202, 210]\n{'east': 2, 'unknown': 1}")],
    cases=dict(expected_outputs=["[201]\n{'north': 1}", "[201, 202, 203, 204, 205]\n{'north': 2, 'south': 1}",
                                 "[201, 202, 203, 204, 205]\n{'north': 2, 'south': 1, 'unknown': 2}"],
               reject=[([['how="left"', 'how="inner"']], 'Every delivery must stay'),
                       ([['orders = pd.concat([pd.DataFrame(may), pd.DataFrame(june)], ignore_index=True)', 'orders = pd.DataFrame(may)']], 'Both months are needed'),
                       ([['joined["zone"] = joined["zone"].fillna("unknown")', 'pass']], 'Missing zones must be counted as unknown')],
               accept=[([['joined = orders.merge(regions, on="member_id", how="left")', 'joined = pd.merge(orders, regions, how="left", on="member_id")']], 'pd.merge with the same keys')]),
    review={'조회가 없어도 남기도록 left로 바꿔요.':
            '양보 「없어도」 뒤에 실제 동작(왼쪽 행 보존)이 와요. 바로 앞 실행에서 사라진 202가 근거예요.',
            '조심하세요. ignore_index 없이 이어 붙이면 행 번호 0과 1이 두 번씩 생겨 위치로 고를 때 헷갈려요.':
            '이 수업 2번의 행 추가에서 실제로 생기는 중복 행 번호를 말해요. 출력에는 영향이 없지만 다음 단계의 위치 선택을 흐려요.'},
)
