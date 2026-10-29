"""aice-python-api final challenge: read a list from a dictionary by key, count it, average it with an aliased module, sort a copy."""
from _common import Script, todo, ids, next_revision

KEY = 'aice-python-api'
UNIT, STEP = ids(KEY)
COUNT_TODO = 'print(len(record))  # 1) 배송 건수를 출력하세요.'
MEAN_TODO = 'print(0)  # 2) 배송 시간의 평균을 출력하세요.'
SORT_TODO = 'print(record)  # 3) 짧은 시간부터 정렬한 새 목록을 출력하세요.'
STARTER = f'''# 평균 기능이 든 모듈을 st라는 이름으로 불러와요.
import statistics as st
# 지역 하나의 배송 기록이에요. 항목 이름으로 값을 꺼내요.
record = {{"region": "north", "minutes": [30, 12, 18, 20], "distance": [4, 1, 2, 3]}}
{COUNT_TODO}
{MEAN_TODO}
{SORT_TODO}
# 원래 시간 목록은 그대로여야 해요.
print(record["minutes"])
'''
COUNT = '# 항목 수가 아니라 시간 목록의 길이예요.\nprint(len(record["minutes"]))'
MEAN_WRONG = 'print(statistics.mean(record["minutes"]))'
MEAN = '# 위에서 붙인 이름 st로 불러요.\nprint(st.mean(record["minutes"]))'
SORT = '# sorted는 정렬한 새 목록을 돌려주고 원래 목록은 두어요.\nprint(sorted(record["minutes"]))'
SOLUTION = STARTER.replace(COUNT_TODO, COUNT).replace(MEAN_TODO, MEAN).replace(SORT_TODO, SORT)

s = Script(STARTER)
s.say('마지막 도전이에요. 배송 기록 딕셔너리에서 시간 목록을 항목 이름으로 꺼내 건수, 평균, 정렬한 새 목록을 출력해요.',
      'text:원래 시간 목록은 그대로 둬야 해요.')
s.run()
s.say('첫 줄이 3이에요. 딕셔너리 항목이 세 개라서 나온 값이지 배송 건수가 아니에요.', 'output')
s.patch(COUNT_TODO, COUNT, '시간 목록을 항목 이름으로 꺼내 길이를 세요.')
s.patch(MEAN_TODO, MEAN_WRONG, '평균은 statistics.mean으로 구해 볼게요.')
s.run(expect_error='NameError')
s.say('NameError예요. 이 코드에서는 모듈을 st라는 이름으로 불러왔어요.', 'output')
s.patch(MEAN_WRONG, MEAN, '붙인 이름 st로 불러요.')
s.patch(SORT_TODO, SORT, '정렬은 sorted로 새 목록을 만들어요.')
s.run()
s.say('4, 20, [12, 18, 20, 30]이 나오고 원래 목록 [30, 12, 18, 20]도 그대로예요.', 'output')
s.say('조심하세요. record["minutes"].sort()를 출력하면 None이 나오고 원래 목록이 바뀌어요.', 'code:print(sorted(record["minutes"]))')

GOAL = ('자, 마지막 도전이에요. 지역 하나의 배송 기록 record가 딕셔너리로 있어요. 시간은 "minutes" 항목의 목록이에요.\n\n'
        '세 줄을 차례로 출력해요. 배송 건수, 배송 시간 평균, 짧은 시간부터 정렬한 새 목록이에요. 마지막 줄은 원래 시간 목록이에요. '
        '원래 시간 목록은 그대로 둬야 해요. 지금 자료이면 `4`, `20`, `[12, 18, 20, 30]`, `[30, 12, 18, 20]`이에요. 채점은 다른 기록으로도 실행해요.\n\n'
        + todo('코드 실행을 눌러 지금 출력을 확인하세요.',
               '첫 줄이 시간 목록의 건수를 출력하도록 고치세요.',
               '둘째 줄이 st 모듈로 평균을 출력하도록 고치세요.',
               '셋째 줄이 정렬한 새 목록을 출력하도록 고치세요.',
               '다시 실행해 네 줄을 확인한 뒤 제출하세요.'))

SPEC = dict(
    key=KEY, course='aice', revision=next_revision(KEY, 'aice-python-api-5'),
    reason='딕셔너리 항목 이름, 목록 길이와 항목 수의 구별, 모듈 별칭 호출, 원본을 두는 sorted를 한 기록에서 함께 쓰는 마지막 도전이에요.',
    grading='실제 파이썬 출력과 다른 기록 세 개로 채점해요. 항목 수를 건수로, 원래 모듈 이름 호출, 원본 정렬은 실패해요.',
    unit=dict(id=UNIT, title='마지막 도전', objectives=['기록에서 목록을 꺼내 세고 평균 내고 정렬해요.'],
              premise='지역 하나의 배송 기록이에요. 앞 스텝과 상관없이 바로 풀 수 있어요.'),
    step=dict(id=STEP, title='배송 기록에서 건수·평균·정렬 목록을 꺼내세요',
              objectives=['항목 이름으로 목록을 꺼내 별칭 모듈과 sorted에 전달해요.'],
              core_flow='준비 코드는 len(record), 0, record를 출력한다. 학생은 record["minutes"]를 len·st.mean·sorted에 전달한다. '
                        '해설은 원래 모듈 이름의 NameError를 실제로 보여 준다. 채점: 한 건, 홀수 건, 평균이 소수인 기록.'),
    task=dict(id=STEP, title='배송 기록에서 건수·평균·정렬 목록을 꺼내세요', language='python', goal=GOAL,
              starter_code=STARTER, solution=SOLUTION, required=True,
              tests=[dict(input='', expected='4\n20\n[12, 18, 20, 30]\n[30, 12, 18, 20]')], narration=s.actions),
    prepared_cases=[dict(values=dict(record={'region': 'south', 'minutes': [9], 'distance': [1]}), expected='1\n9\n[9]\n[9]'),
                    dict(values=dict(record={'region': 'x', 'minutes': [5, 1, 3], 'distance': [1, 1, 1]}), expected='3\n3\n[1, 3, 5]\n[5, 1, 3]'),
                    dict(values=dict(record={'region': 'y', 'minutes': [15, 10], 'distance': [2, 1]}), expected='2\n12.5\n[10, 15]\n[15, 10]')],
    cases=dict(expected_outputs=['3\n0\n{\'region\': \'north\', \'minutes\': [30, 12, 18, 20], \'distance\': [4, 1, 2, 3]}\n[30, 12, 18, 20]', '4', '4\n20\n[12, 18, 20, 30]\n[30, 12, 18, 20]'],
               reject=[([['print(len(record["minutes"]))', 'print(len(record))']], 'The number of keys is not the number of deliveries'),
                       ([['print(sorted(record["minutes"]))', 'print(record["minutes"].sort())']], 'sort() returns None and changes the original'),
                       ([['print(st.mean(record["minutes"]))', 'print(20)']], 'A fixed mean fails other records')],
               accept=[([['print(st.mean(record["minutes"]))', 'print(st.mean(record.get("minutes")))']], 'get reads the same item')]),
    review={'조심하세요. record["minutes"].sort()를 출력하면 None이 나오고 원래 목록이 바뀌어요.':
            '이 수업 6번의 sorted(원본 유지)와 대비되는 실제 결과를 말해요. 채점의 마지막 줄이 잡아요.'},
)
