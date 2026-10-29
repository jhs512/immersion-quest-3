"""aice-python-start final challenge: count, first and last value of a delivery list whose length changes daily."""
from _common import Script, todo

STEP = 'stp_5b8e2c47-1d93-4f6a-a2e0-7c4b9d31f8e6'
COUNT_TODO = 'print(0)  # 1) 배송 건수를 출력하세요.'
FIRST_TODO = 'print(0)  # 2) 첫 배송 시간을 출력하세요.'
LAST_TODO = 'print(0)  # 3) 마지막 배송 시간을 출력하세요.'
STARTER = f'''# 오늘 들어온 배송 시간 목록이에요. 건수는 날마다 달라요.
minutes = [15, 22, 9, 31, 18]
{COUNT_TODO}
{FIRST_TODO}
{LAST_TODO}
'''
COUNT = '# 목록에 든 항목의 개수예요.\nprint(len(minutes))'
FIRST = '# 위치는 0부터 세요.\nprint(minutes[0])'
LAST_WRONG = 'print(minutes[len(minutes)])'
LAST = '# 마지막 위치는 건수보다 1 작아요.\nprint(minutes[len(minutes) - 1])'
SOLUTION = STARTER.replace(COUNT_TODO, COUNT).replace(FIRST_TODO, FIRST).replace(LAST_TODO, LAST)

s = Script(STARTER)
s.say('마지막 도전이에요. 날마다 건수가 다른 배송 목록에서 건수, 첫 배송, 마지막 배송을 차례로 출력해요.', 'text:건수가 바뀌어도 같은 코드로 맞아야 해요.')
s.run()
s.say('세 줄 모두 0이에요. 아직 목록을 읽지 않았어요.', 'output')
s.patch(COUNT_TODO, COUNT, 'len으로 항목 수를 세요.')
s.patch(FIRST_TODO, FIRST, '첫 배송은 위치 0이에요.')
s.patch(LAST_TODO, LAST_WRONG, '마지막은 건수 위치일까요? 건수를 위치로 넣어 볼게요.')
s.run(expect_error='IndexError')
s.say('IndexError예요. 다섯 건이면 위치는 0부터 4까지라서 5번 위치는 없어요.', 'output')
s.patch(LAST_WRONG, LAST, '마지막 위치는 건수에서 1을 빼요.')
s.run()
s.say('5, 15, 18이 나와요. 건수와 위치를 구분했어요.', 'output')
s.say('조심하세요. 지금 목록만 보고 minutes[4]라고 적으면 건수가 바뀐 날에는 다른 값을 읽어요.', 'code:print(minutes[len(minutes) - 1])')

GOAL = ('자, 마지막 도전이에요. 오늘 들어온 배송 시간 목록 minutes가 있어요. 건수는 날마다 달라요.\n\n'
        '세 줄을 차례로 출력해요. 배송 건수, 첫 배송 시간, 마지막 배송 시간이에요. 지금 목록이면 `5`, `15`, `18`이에요. '
        '건수가 바뀌어도 같은 코드로 맞아야 해요. 채점은 다른 목록으로도 실행해요.\n\n'
        + todo('코드 실행을 눌러 지금 출력을 확인하세요.',
               '첫 줄이 배송 건수를 출력하도록 고치세요.',
               '둘째 줄이 첫 배송 시간을 출력하도록 고치세요.',
               '셋째 줄이 마지막 배송 시간을 출력하도록 고치세요.',
               '다시 실행해 세 줄을 확인한 뒤 제출하세요.'))

SPEC = dict(
    key='aice-python-start', course='aice', revision='aice-python-start-6',
    reason='목록의 건수(len)와 위치(0부터)를 함께 써서, 건수가 바뀌는 목록의 첫 값과 마지막 값을 고정 숫자 없이 꺼내는 마지막 도전이에요.',
    grading='실제 파이썬 실행 출력과 길이가 다른 목록 세 개로 채점해요. 고정 건수·고정 위치·건수를 위치로 쓰기는 실패해요.',
    unit=dict(id='unt_8c3f1e92-4b7d-4a05-9e61-2d7a5c0b4f83', title='마지막 도전',
              objectives=['건수와 위치를 함께 써서 바뀌는 목록을 읽어요.'],
              premise='오늘의 배송 시간 목록이에요. 앞 스텝과 상관없이 바로 풀 수 있어요.'),
    step=dict(id=STEP, title='건수가 바뀌는 목록의 처음과 끝을 읽으세요',
              objectives=['len과 위치를 함께 써서 첫 값과 마지막 값을 꺼내요.'],
              core_flow='준비 코드는 세 줄 모두 0을 출력한다. 학생은 len(minutes), minutes[0], minutes[len(minutes) - 1]을 쓴다. '
                        '해설은 건수를 위치로 넣은 IndexError를 실제로 보여 준다. 채점: 길이 1·3·7인 다른 목록.'),
    task=dict(id=STEP, title='건수가 바뀌는 목록의 처음과 끝을 읽으세요', language='python', goal=GOAL,
              starter_code=STARTER, solution=SOLUTION, required=True,
              tests=[dict(input='', expected='5\n15\n18')], narration=s.actions),
    prepared_cases=[dict(values=dict(minutes=[7]), expected='1\n7\n7'),
                    dict(values=dict(minutes=[3, 8, 12]), expected='3\n3\n12'),
                    dict(values=dict(minutes=[40, 2, 2, 9, 1, 6, 30]), expected='7\n40\n30')],
    cases=dict(expected_outputs=['0\n0\n0', '5\n15', '5\n15\n18'],
               reject=[([['print(len(minutes))', 'print(5)']], 'A fixed count fails other lists'),
                       ([['print(minutes[len(minutes) - 1])', 'print(minutes[4])']], 'A fixed last position fails other lists'),
                       ([['print(minutes[0])', 'print(minutes[1])']], 'The first position is 0')],
               accept=[([['print(minutes[len(minutes) - 1])', 'print(minutes[-1])']], 'A negative position also reads the last item')]),
    review={'조심하세요. 지금 목록만 보고 minutes[4]라고 적으면 건수가 바뀐 날에는 다른 값을 읽어요.':
            '이 도전에서 가장 흔한 지름길(지금 목록의 위치를 고정)을 다른 날의 결과로 말해요. 채점의 다른 목록이 잡아요.'},
)
