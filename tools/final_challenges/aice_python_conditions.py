"""aice-python-conditions final challenge: collect the deliveries at or over a limit into a new list and count them."""
from _common import Script, todo, ids, next_revision

KEY = 'aice-python-conditions'
UNIT, STEP = ids(KEY)
LOOP_TODO = '# 1) 기준 이상인 배송만 delayed에 모으세요.'
COUNT_TODO = 'print(0)  # 2) 모은 건수를 출력하세요.'
STARTER = f'''# 오늘 배송 시간 목록과 지연 기준이에요. 기준과 같은 시간도 지연이에요.
minutes = [25, 40, 12, 40, 55]
limit = 40
# 새 목록은 반복을 시작하기 전에 한 번만 준비해요.
delayed = []
{LOOP_TODO}
print(delayed)
{COUNT_TODO}
'''
LOOP_WRONG = '''for minute in minutes:
    if minute > limit:
        delayed.append(minute)'''
LOOP = '''for minute in minutes:
    # 기준과 같은 시간도 지연이라서 >= 를 써요.
    if minute >= limit:
        delayed.append(minute)'''
COUNT = 'print(len(delayed))'
SOLUTION = STARTER.replace(LOOP_TODO, LOOP).replace(COUNT_TODO, COUNT)

s = Script(STARTER)
s.say('마지막 도전이에요. 기준 이상인 배송만 새 목록에 모으고, 모은 목록과 건수를 출력해요.', 'text:기준과 같은 시간도 지연이에요.')
s.run()
s.say('빈 목록과 0이 나와요. 아직 고르지 않았어요.', 'output')
s.patch(COUNT_TODO, COUNT, '건수는 모은 목록의 len이에요.')
s.patch(LOOP_TODO, LOOP_WRONG, '한 건씩 보며 기준보다 큰 배송을 모아 볼게요.')
s.run()
s.say('55 한 건뿐이에요. 기준과 같은 40 두 건이 빠졌어요.', 'output')
s.patch(LOOP_WRONG, LOOP, '같은 값도 넣도록 >= 로 바꿔요.')
s.run()
s.say('40, 40, 55와 3이 나와요.', 'output')
s.say('조심하세요. delayed = []를 반복 안으로 옮기면 매번 비워져서 마지막 한 건만 남아요.', 'code:delayed = []')

GOAL = ('자, 마지막 도전이에요. 오늘 배송 시간 minutes와 지연 기준 limit이 있어요. 기준과 같은 시간도 지연이에요.\n\n'
        '지연인 배송만 새 목록 delayed에 모아 출력하고, 다음 줄에 그 건수를 출력해요. 지금 자료이면 `[40, 40, 55]`, `3`이에요. '
        '채점은 다른 목록과 기준으로도 실행해요.\n\n'
        + todo('코드 실행을 눌러 지금 출력을 확인하세요.',
               '반복과 조건으로 기준 이상인 배송만 delayed에 모으세요.',
               '둘째 출력이 모은 건수가 되도록 고치세요.',
               '다시 실행해 기준과 같은 값이 들어갔는지 확인한 뒤 제출하세요.'))

SPEC = dict(
    key=KEY, course='aice', revision=next_revision(KEY, 'aice-python-conditions-6'),
    reason='비교의 경계(>=), 반복, 조건, 새 목록에 모으기, 건수를 직접 조합해 다른 자료에도 맞게 고르는 마지막 도전이에요.',
    grading='실제 파이썬 출력과 다른 목록·기준 세 가지로 채점해요. > 경계, 고정 건수, 반복 안에서 목록 초기화는 실패해요.',
    unit=dict(id=UNIT, title='마지막 도전', objectives=['조건으로 고른 배송을 새 목록에 모아 세요.'],
              premise='오늘 배송 시간과 기준이에요. 앞 스텝과 상관없이 바로 풀 수 있어요.'),
    step=dict(id=STEP, title='기준 이상인 배송을 모아 건수를 세세요',
              objectives=['경계를 포함하는 조건으로 고르고 모은 건수를 출력해요.'],
              core_flow='준비 코드는 빈 목록과 0을 출력한다. 학생은 for·if >= ·append와 len을 쓴다. 해설은 > 로 같은 값이 빠지는 결과를 실제로 보여 준다. '
                        '채점: 빈 결과, 경계 값, 한 건짜리 목록.'),
    task=dict(id=STEP, title='기준 이상인 배송을 모아 건수를 세세요', language='python', goal=GOAL,
              starter_code=STARTER, solution=SOLUTION, required=True,
              tests=[dict(input='', expected='[40, 40, 55]\n3')], narration=s.actions),
    prepared_cases=[dict(values=dict(minutes=[10, 20], limit=30), expected='[]\n0'),
                    dict(values=dict(minutes=[30, 29, 31], limit=30), expected='[30, 31]\n2'),
                    dict(values=dict(minutes=[5], limit=5), expected='[5]\n1')],
    cases=dict(expected_outputs=['[]\n0', '[55]\n1', '[40, 40, 55]\n3'],
               reject=[([['    if minute >= limit:', '    if minute > limit:']], 'The limit itself is a delay'),
                       ([['print(len(delayed))', 'print(3)']], 'A fixed count fails other lists'),
                       ([['for minute in minutes:\n', 'for minute in minutes:\n    delayed = []\n']], 'Resetting inside the loop keeps only the last one')],
               accept=[([['    if minute >= limit:', '    if not minute < limit:']], 'The same condition written as not <')]),
    review={'조심하세요. delayed = []를 반복 안으로 옮기면 매번 비워져서 마지막 한 건만 남아요.':
            '이 수업 7번에서 강조한 준비 위치를 이 도전의 결과로 다시 말해요. 채점 사례가 잡아요.'},
)
