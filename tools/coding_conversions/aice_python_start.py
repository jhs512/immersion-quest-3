"""aice-python-start: 5 answer-picking steps -> coding steps (2026-10-29)."""
from _kit import Script, todo, py_cases

OPENING = ['이 수업에서는 파이썬의 값·이름·출력을 구별해요. 자료를 읽는 기초를 직접 코드를 써 가며 만들어요.',
           '배송 시간 하나를 출력하는 것부터 시작해요. 이름을 붙이고 다시 연결한 뒤 리스트의 항목과 길이를 직접 읽어요.']
PRD_SCOPE = ['출력, 이름에 값 연결하기와 다시 연결하기를 작은 문제로 직접 써 봐요.',
             '리스트 만들기·첫 항목·길이를 준비 코드의 한 줄씩 고쳐 비교해요.',
             '두 챕터·두 단원·여덟 스텝으로 이어 가요. 수량 자체를 교육 목표로 삼지 않아요.']
PRD_GRADING = ['필수 스텝을 직접 제출해 맞히면 성공이에요. 실행·해설만으로 성공시키지 않아요.',
               '직접 쓴 코드는 실제 파이썬 실행 결과로 확인하고, 준비 값과 목록을 바꾼 실행에서도 같은 원리가 맞아야 해요. 값을 글자로 적은 답은 거절해요.',
               '첫 항목 문제는 다른 숫자 목록에서도 위치를 고르는 원리가 유지되는지 확인해요.',
               '해설을 본 뒤 풀어도 정상 성공이며 성공 전후 열람은 상세의 아이콘 정보예요.',
               '마지막 도전(stp_5b8e2c47-1d93-4f6a-a2e0-7c4b9d31f8e6): 실제 파이썬 실행 출력과 길이가 다른 목록 세 개로 채점해요. 고정 건수·고정 위치·건수를 위치로 쓰기는 실패해요.']
PRD_NARRATION = ['한 줄씩 고치고 실행해 결과를 읽어요.',
                 '설명하는 코드 줄·실행 버튼·결과를 정확히 강조하고 음성을 준비한 뒤 함께 진행해요.',
                 '첫 항목을 1로 고르기 쉬운 지점을 두 실행 결과로 비교해요. 한 번에 답안을 교체하지 않아요.']

s3 = '# 배송 시간에 minutes라는 이름을 붙여요.\nminutes = 18\n# 이 줄을 고쳐 이름 글자가 아니라 minutes에 연결된 값을 출력하세요.\nprint("minutes")\n'
s3_solution = s3.replace('print("minutes")', '# 따옴표 없이 이름을 쓰면 그 이름에 연결된 값을 읽어요.\nprint(minutes)')
n3 = (Script(s3)
      .say('minutes는 배송 시간 18에 붙인 이름이에요. 이름 글자가 아니라 값을 출력해야 해요.', 'text:print 줄을 고쳐 이름 글자가 아니라 minutes에 연결된 값을 출력하세요.')
      .run('print(')
      .say('minutes라는 글자가 나와요. 따옴표 안은 글자 그대로예요.', 'output')
      .patch('print("minutes")', 'print(minutes)', '따옴표를 지워요.')
      .run('print(')
      .say('18이에요. 이름 minutes에 연결된 값을 읽었어요.', 'output')
      .say('조심하세요. 따옴표가 있으면 이름이 아니라 글자예요.', 'code:print(minutes)'))

s4 = '# 처음 배송 시간과 정정된 시간이에요.\nminutes = 18\ncorrected = 24\n# 이 주석 아래에 minutes를 corrected의 값으로 다시 연결하세요.\nprint(minutes)\n'
s4_solution = s4.replace('# 이 주석 아래에 minutes를 corrected의 값으로 다시 연결하세요.\n',
                         '# 이 주석 아래에 minutes를 corrected의 값으로 다시 연결하세요.\n# 같은 이름에 다시 =를 쓰면 이름이 새 값을 가리켜요.\nminutes = corrected\n')
n4 = (Script(s4)
      .say('배송 시간을 정정했어요. minutes가 corrected의 값을 가리키게 다시 연결해야 해요.', 'text:주석 아래에 minutes를 corrected의 값으로 다시 연결하세요.')
      .run('print(minutes)')
      .say('18이에요. 아직 처음 값에 연결돼 있어요.', 'output')
      .patch('# 이 주석 아래에 minutes를 corrected의 값으로 다시 연결하세요.\n',
             '# 이 주석 아래에 minutes를 corrected의 값으로 다시 연결하세요.\nminutes = corrected\n', 'minutes = corrected를 써요.')
      .run('print(minutes)')
      .say('24예요. 마지막에 연결한 값이 출력돼요.', 'output')
      .say('조심하세요. 코드는 위에서 아래로 실행돼요. print 아래에 쓰면 출력은 18 그대로예요.', 'code:minutes = corrected'))

s5 = '# 배송 세 건의 시간이에요.\nfirst = 12\nsecond = 18\nthird = 24\n# 이 줄을 고쳐 세 시간을 차례로 담은 목록을 minutes에 연결하세요.\nminutes = first\nprint(minutes)\n'
s5_solution = s5.replace('minutes = first\n', '# 대괄호 안에 쉼표로 이어 쓰면 순서가 있는 목록이에요.\nminutes = [first, second, third]\n')
n5 = (Script(s5)
      .say('배송이 세 건으로 늘었어요. 세 시간을 차례로 담은 목록을 만들어야 해요.', 'text:minutes 줄을 고쳐 세 시간을 차례로 담은 목록을 minutes에 연결하세요.')
      .run('print(minutes)')
      .say('12예요. 지금은 첫 시간 하나만 연결돼 있어요.', 'output')
      .patch('minutes = first\n', 'minutes = [first, second, third]\n', '대괄호 안에 first, second, third를 차례로 써요.')
      .run('print(minutes)')
      .say('[12, 18, 24]예요. 세 값이 순서대로 한 목록에 담겼어요.', 'output')
      .say('조심하세요. 목록을 출력하면 대괄호와 쉼표까지 함께 보여요. 개수는 따로 len으로 구해요.', 'code:minutes = [first, second, third]'))

s6 = '# 배송 시간 목록이에요.\nminutes = [12, 18, 24]\n# 이 줄을 고쳐 첫 배송의 시간을 출력하세요.\nprint(minutes[1])\n'
s6_solution = s6.replace('print(minutes[1])', '# 목록의 위치는 0부터 세어요. 첫 항목은 [0]이에요.\nprint(minutes[0])')
n6 = (Script(s6)
      .say('첫 배송의 시간을 출력해야 해요. 지금 위치가 맞는지 먼저 실행해 봐요.', 'text:print 줄을 고쳐 첫 배송의 시간을 출력하세요.')
      .run('print(minutes[')
      .say('18이에요. 위치 1은 두 번째 항목이에요.', 'output')
      .patch('print(minutes[1])', 'print(minutes[0])', '위치를 0으로 바꿔요.')
      .run('print(minutes[')
      .say('12예요. 위치 0이 첫 항목이에요.', 'output')
      .say('조심하세요. 사람이 세는 첫째는 1이지만 파이썬 목록의 첫 위치는 0이에요.', 'code:print(minutes[0])'))

s7 = '# 배송 한 건이 추가됐어요.\nminutes = [12, 18, 24, 9]\nprint(minutes[0])\n# 이 줄을 고쳐 목록에 든 배송 건수를 count에 담으세요.\ncount = 0\nprint(count)\n'
s7_solution = s7.replace('count = 0\n', '# len은 목록에 든 항목의 개수예요. 위치 번호가 아니에요.\ncount = len(minutes)\n')
n7 = (Script(s7)
      .say('len은 목록에 든 항목의 개수를 돌려줘요. 배송 건수를 count에 담아야 해요.', 'text:count 줄을 고쳐 목록에 든 배송 건수를 count에 담으세요.')
      .run('print(minutes[0])', 'print(count)')
      .say('12와 0이에요. 아직 건수를 세지 않았어요.', 'output')
      .patch('count = 0\n', 'count = len(minutes)\n', 'count에 len(minutes)를 담아요.')
      .run('print(minutes[0])', 'print(count)')
      .say('12와 4예요. 첫 배송은 12분이고 배송은 모두 네 건이에요.', 'output')
      .say('조심하세요. 건수 4는 위치가 아니에요. 마지막 항목의 위치는 3이에요.', 'code:count = len(minutes)'))

SPECS = [
    dict(old='stp_65ea997d-2965-4d20-9acd-be74f694e32f', title='따옴표를 지워 minutes에 연결된 값을 출력하세요',
         objectives=['이름 글자와 이름에 연결된 값을 구별해요.'],
         core_flow='print("minutes")는 글자 minutes를 출력한다. 따옴표를 지워 print(minutes)로 18을 확인한다. 채점은 minutes의 값을 바꿔 실행한다.',
         goal='minutes는 배송 시간에 붙인 이름이에요. 따옴표 안에 쓴 것은 글자 그대로 출력되고, 따옴표 없이 이름을 쓰면 그 이름에 연결된 값을 읽어요.\n\n'
              'print 줄을 고쳐 이름 글자가 아니라 minutes에 연결된 값을 출력하세요. 채점은 minutes의 값을 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 minutes라는 글자가 나오는지 확인하세요.', '`print("minutes")`의 따옴표를 지우세요.', '코드 실행을 눌러 18이 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s3, solution=s3_solution, tests=[{'input': '', 'expected': '18'}],
         prepared_cases=py_cases(s3_solution, {'minutes': 18}, {'minutes': 7}, {'minutes': 41}),
         narration=n3.actions,
         review={'조심하세요. 따옴표가 있으면 이름이 아니라 글자예요.': '실제 파이썬 의미를 정확히 말해요.'},
         reject=[([['print(minutes)', 'print(18)']], 'Typing the value')],
         accept=[([['print(minutes)', 'value = minutes\nprint(value)']], 'Through another name')]),
    dict(old='stp_0489e00e-1fdf-4841-9240-c7e0b12a5ca9', title='minutes를 corrected의 값으로 다시 연결하세요',
         objectives=['같은 이름에 새 값을 다시 연결하면 마지막 값이 쓰임을 확인해요.'],
         core_flow='minutes=18, corrected=24에서 print 위에 minutes = corrected를 써서 24를 확인한다. 채점은 두 값을 바꿔 실행한다.',
         goal='배송 시간을 정정했어요. 같은 이름에 다시 `=`를 쓰면 그 이름이 새 값을 가리키고, 그 뒤의 코드는 새 값을 읽어요.\n\n'
              '주석 아래에 minutes를 corrected의 값으로 다시 연결하세요. 숫자를 직접 쓰지 않아요. 채점은 두 시간을 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 18이 나오는지 확인하세요.', '주석 아래에 `minutes = corrected`를 쓰세요.', '코드 실행을 눌러 24가 나오는지 확인하세요.', '작성한 코드를 제출하세요.'),
         starter_code=s4, solution=s4_solution, tests=[{'input': '', 'expected': '24'}],
         prepared_cases=py_cases(s4_solution, {'corrected': 24}, {'minutes': 5, 'corrected': 31}, {'corrected': 0}),
         narration=n4.actions,
         review={'조심하세요. 코드는 위에서 아래로 실행돼요. print 아래에 쓰면 출력은 18 그대로예요.': '실제 실행 순서와 그 결과를 말해요.'},
         reject=[([['minutes = corrected\n', 'minutes = 24\n']], 'Typing the value')],
         accept=[([['minutes = corrected\n', 'minutes = corrected + 0\n']], 'Same value through an expression')]),
    dict(old='stp_ccb54028-dba8-4b6e-9312-4bad3cb30455', title='세 시간을 담은 목록을 minutes에 연결하세요',
         objectives=['여러 값을 순서가 있는 목록 하나로 묶어요.'],
         core_flow='minutes = first는 12 하나다. [first, second, third]로 고쳐 [12, 18, 24]를 확인한다. 채점은 세 값을 바꿔 실행한다.',
         goal='배송이 세 건으로 늘었어요. 대괄호 안에 쉼표로 값을 이어 쓰면 순서가 있는 목록이 돼요. 목록을 출력하면 대괄호와 함께 모든 항목이 보여요.\n\n'
              'minutes 줄을 고쳐 세 시간을 차례로 담은 목록을 minutes에 연결하세요. 채점은 세 값을 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 12가 나오는지 확인하세요.', '`minutes = first`를 `minutes = [first, second, third]`로 고치세요.', '코드 실행을 눌러 [12, 18, 24]가 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s5, solution=s5_solution, tests=[{'input': '', 'expected': '[12, 18, 24]'}],
         prepared_cases=py_cases(s5_solution, {'first': 12}, {'first': 3, 'second': 9, 'third': 27}, {'second': 40}),
         narration=n5.actions,
         review={'조심하세요. 목록을 출력하면 대괄호와 쉼표까지 함께 보여요. 개수는 따로 len으로 구해요.': '실제 출력 형식과 다음 스텝 개념을 정확히 말해요.'},
         reject=[([['minutes = [first, second, third]\n', 'minutes = [12, 18, 24]\n']], 'Typing the numbers'),
                 ([['minutes = [first, second, third]\n', 'minutes = [third, second, first]\n']], 'Wrong order')],
         accept=[([['minutes = [first, second, third]\n', 'minutes = []\nminutes.append(first)\nminutes.append(second)\nminutes.append(third)\n']], 'Appending in order')]),
    dict(old='stp_c4811193-58a8-467a-82ba-02b549a9329e', title='minutes[0]으로 첫 배송을 출력하세요',
         objectives=['목록의 위치가 0부터 시작함을 써서 확인해요.'],
         core_flow='print(minutes[1])은 두 번째 18이다. minutes[0]으로 고쳐 12를 확인한다. 채점은 다른 숫자 목록으로 실행한다.',
         goal='목록의 항목은 `minutes[위치]`로 골라요. 위치는 0부터 세어서 첫 항목은 `[0]`이에요.\n\n'
              'print 줄을 고쳐 첫 배송의 시간을 출력하세요. 채점은 다른 숫자 목록으로도 실행해요.\n\n'
              + todo('코드 실행을 눌러 18이 나오는지 확인하세요.', '`minutes[1]`의 위치를 0으로 고치세요.', '코드 실행을 눌러 12가 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s6, solution=s6_solution, tests=[{'input': '', 'expected': '12'}],
         prepared_cases=py_cases(s6_solution, {'minutes': [12, 18, 24]}, {'minutes': [30, 5, 9, 2]}, {'minutes': [7]}),
         narration=n6.actions,
         review={'조심하세요. 사람이 세는 첫째는 1이지만 파이썬 목록의 첫 위치는 0이에요.': '실제 파이썬 인덱스 규칙과 흔한 혼동을 정확히 대조해요.'},
         reject=[([['print(minutes[0])', 'print(minutes[1])']], 'Second item'), ([['print(minutes[0])', 'print(12)']], 'Typing the value')],
         accept=[([['print(minutes[0])', 'print(minutes[-len(minutes)])']], 'Negative index of the first item')]),
    dict(old='stp_12d1bd54-56af-4280-a0be-36b5f0f70bd1', title='len(minutes)로 배송 건수를 count에 담으세요',
         objectives=['목록의 항목 개수와 위치 번호를 구별해요.'],
         core_flow='count = 0을 len(minutes)로 고쳐 첫 시간 12와 건수 4를 확인한다. 건수는 위치가 아니다. 채점은 길이가 다른 목록으로 실행한다.',
         goal='배송 한 건이 추가됐어요. `len(목록)`은 목록에 든 항목의 개수를 돌려줘요. 위치 번호와는 달라요.\n\n'
              'count 줄을 고쳐 목록에 든 배송 건수를 count에 담으세요. 채점은 길이가 다른 목록으로도 실행해요.\n\n'
              + todo('코드 실행을 눌러 12와 0이 나오는지 확인하세요.', '`count = 0`을 `count = len(minutes)`로 고치세요.', '코드 실행을 눌러 12와 4가 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s7, solution=s7_solution, tests=[{'input': '', 'expected': '12\n4'}],
         prepared_cases=py_cases(s7_solution, {'minutes': [12, 18, 24, 9]}, {'minutes': [3, 5]}, {'minutes': [8, 1, 1, 1, 1, 6]}),
         narration=n7.actions,
         review={'조심하세요. 건수 4는 위치가 아니에요. 마지막 항목의 위치는 3이에요.': '실제 의미를 정확히 대조해요.'},
         reject=[([['count = len(minutes)\n', 'count = 4\n']], 'Typing the count'), ([['count = len(minutes)\n', 'count = len(minutes) - 1\n']], 'Last position instead of count')],
         accept=[([['count = len(minutes)\n', 'count = sum(1 for _ in minutes)\n']], 'Counting by iterating')]),
]


# ---- 2026-10-30: the first output field becomes a coding step (user decision) --------------------------
from _kit import code_step

s1 = ('# print는 괄호 안의 값을 화면에 표시해요.\nprint(12)\n# 오늘 둘째 배송 시간이에요. minutes라는 이름을 붙였어요.\nminutes = 30\n'
      '# 이 주석 아래에 print로 minutes의 값을 화면에 표시하세요.\n')
s1_solution = s1 + '# 이름 minutes에 연결된 값을 괄호 안에 넣어 표시해요.\nprint(minutes)\n'
n1 = (Script(s1)
      .say('print는 괄호 안의 값을 결과 창에 보여 줘요. 둘째 배송 시간도 print로 표시해야 해요.', 'text:주석 아래에 print로 minutes의 값을 화면에 표시하세요.')
      .run('print(12)')
      .say('12만 나와요. 아직 minutes를 표시하는 줄이 없어요.', 'output')
      .patch('# 이 주석 아래에 print로 minutes의 값을 화면에 표시하세요.\n', '# 이 주석 아래에 print로 minutes의 값을 화면에 표시하세요.\nprint(minutes)\n', '주석 아래에 print(minutes)를 써요.')
      .run('print(12)', 'print(minutes)')
      .say('12 다음 줄에 30이 나와요. print 한 줄마다 결과가 한 줄씩 나와요.', 'output')
      .say('조심하세요. print 없이 minutes만 적으면 결과 창에 아무것도 나오지 않아요. 보여 주려면 print로 감싸요.', 'code:print(minutes)'))

SPECS += [
    code_step('stp_25ab6ac1-c2dc-4dd6-838f-9d28ffaa9aa1', 'print(minutes)로 배송 시간을 화면에 표시하세요', 'print가 괄호 안의 값을 결과 창에 한 줄씩 보여 주는 것을 직접 써서 확인해요.',
              'print(12)만 있으면 12 한 줄이다. 주석 아래에 print(minutes)를 써서 12와 30을 확인한다. 채점은 다른 배송 시간으로 실행한다.',
              '`print(값)`은 괄호 안의 값을 결과 창에 한 줄로 보여 줘요. 이름을 붙인 값도 괄호 안에 이름을 쓰면 그 값을 보여 줘요.',
              '주석 아래에 print로 minutes의 값을 화면에 표시하세요. 채점은 minutes의 값을 바꿔서도 실행해요.',
              ['코드 실행을 눌러 결과를 확인하세요.', '주석 아래에 `print(minutes)`를 쓰세요.', '코드 실행을 눌러 12 다음에 30이 나오는지 확인하세요.', '수정한 코드를 제출하세요.'],
              s1, s1_solution, n1, {n1.actions[-1]['text']: '실제 파이썬 동작을 정확히 말해요.'}, cases=[{'minutes': 45}, {'minutes': 7}],
              reject=[([['print(minutes)\n', 'print(30)\n']], 'Typing the value'), ([['print(minutes)\n', 'minutes\n']], 'No print')],
              accept=[([['print(minutes)\n', 'print(str(minutes))\n']], 'Printing the text of the value')]),
]
