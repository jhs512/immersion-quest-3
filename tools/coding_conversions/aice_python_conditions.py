"""aice-python-conditions: 4 answer-picking steps -> coding steps (2026-10-29)."""
from _kit import Script, todo, py_cases

OPENING = ['이 수업에서는 비교 결과와 조건 선택을 직접 써 가며 배워요. 기준과 같은 값이 포함되는지 판단해요.',
           '배송 자료에 조건을 하나씩 적용해요. 반복과 조건으로 필요한 자료를 골라 새 목록에 모아요.']
PRD_SCOPE = ['작은 숫자 비교와 경계값, if/else를 직접 써요.',
             '완성된 for에 조건과 append를 적용해 새 목록으로 모아요.',
             '두 챕터·두 단원·아홉 스텝으로 이어 가요.']
PRD_GRADING = ['직접 제출한 코드를 실제 파이썬으로 실행해 판정해요. 실행·해설만으로 성공하지 않아요.',
               '경계보다 작은 값·같은 값·큰 값에서 요청한 조건을 확인해요.',
               '목록의 다른 값에서도 작동하는지 확인하고 출력 값을 고정한 코드는 거절해요.',
               '마지막 도전(stp_981a0d0f-555b-492d-87c6-b668734543df): 실제 파이썬 출력과 다른 목록·기준 세 가지로 채점해요. > 경계, 고정 건수, 반복 안에서 목록 초기화는 실패해요.']
PRD_NARRATION = ['비교 기호나 한 줄을 써 넣고 실행해요. 경계값을 놓치는 순간을 실제 출력으로 보여줘요.',
                 '조건 줄·실행 버튼·나온 결과만 정확히 강조해요. 음성 준비 후 화면과 함께 진행해요.']

s1 = '# 배송 시간이 기준 이상인지 비교해요.\nminutes = 31\nlimit = 30\n# 이 줄을 고쳐 minutes가 limit 이상인지 비교한 결과를 late에 담으세요.\nlate = False\nprint(late)\n'
s1_solution = s1.replace('late = False\n', '# 비교식의 결과는 True 또는 False예요.\nlate = minutes >= limit\n')
n1 = (Script(s1)
      .say('minutes가 limit 이상인지 비교한 결과를 late에 담아야 해요. >=는 기준 이상인지 확인해요.', 'text:late 줄을 고쳐 minutes가 limit 이상인지 비교한 결과를 late에 담으세요.')
      .run('print(late)')
      .say('False예요. 아직 비교하지 않고 False를 넣었어요.', 'output')
      .patch('late = False\n', 'late = minutes >= limit\n', 'late에 minutes >= limit을 담아요.')
      .run('print(late)')
      .say('True예요. 31은 30 이상이에요.', 'output')
      .say('조심하세요. 비교 결과는 숫자 31이 아니라 참과 거짓이에요.', 'code:late = minutes >= limit'))

s2 = '# 30분과 같은 배송도 지연에 포함해요.\nminutes = 30\nlimit = 30\n# 이 줄의 비교를 고쳐 기준과 같은 값도 True가 되게 하세요.\nprint(minutes > limit)\n'
s2_solution = s2.replace('print(minutes > limit)', '# >=는 같은 값도 포함해요. >는 같은 값을 빼요.\nprint(minutes >= limit)')
n2 = (Script(s2)
      .say('기준과 같은 30분도 지연이에요. 같은 값도 포함하는 비교로 고쳐야 해요.', 'text:print 줄의 비교를 고쳐 기준과 같은 값도 True가 되게 하세요.')
      .run('print(minutes')
      .say('False예요. >는 30과 30이 같으면 거짓이에요.', 'output')
      .patch('print(minutes > limit)', 'print(minutes >= limit)', '>를 >=로 바꿔요.')
      .run('print(minutes')
      .say('True예요. 같은 값도 포함했어요.', 'output')
      .say('조심하세요. 경계값 하나 차이로 결과가 달라져요. 기준과 같은 값을 꼭 실행해 확인해요.', 'code:minutes >= limit'))

s4 = '# 조건에 맞는 갈래 하나만 실행해요.\nminutes = 25\nlimit = 30\nif minutes >= limit:\n    print("지연")\n# 이 주석 아래에 else를 써서 조건이 아니면 정상을 출력하세요.\n'
s4_solution = s4 + '# if 조건이 거짓일 때만 else 쪽이 실행돼요.\nelse:\n    print("정상")\n'
n4 = (Script(s4)
      .say('조건이 맞으면 지연, 아니면 정상을 출력해야 해요. else 쪽을 직접 써요.', 'text:if 아래에 else를 써서 조건이 아니면 정상을 출력하세요.')
      .run('print("지연")')
      .say('아무것도 나오지 않아요. 25분은 기준보다 작고 else가 없어요.', 'output')
      .patch('# 이 주석 아래에 else를 써서 조건이 아니면 정상을 출력하세요.\n', '# 이 주석 아래에 else를 써서 조건이 아니면 정상을 출력하세요.\nelse:\n    print("정상")\n',
             'if와 같은 들여쓰기로 else:를 쓰고 그 안에 정상을 출력해요.')
      .run('print("지연")', 'print("정상")')
      .say('정상이에요. 조건이 거짓이라 else 쪽만 실행됐어요.', 'output')
      .say('조심하세요. if와 else 중 한쪽만 실행돼요. 두 표시가 함께 나오지 않아요.', 'code:else:'))

s7 = '# 기준 이상인 배송만 새 목록에 모아요.\nminutes = [12, 30, 42]\nlimit = 30\n# 새 목록은 반복을 시작하기 전에 한 번만 준비해요.\ndelayed = []\nfor minute in minutes:\n    if minute >= limit:\n        # 이 주석 아래에 조건에 맞는 minute을 delayed 끝에 넣으세요.\n        pass\nprint(delayed)\n'
s7_solution = s7.replace('        # 이 주석 아래에 조건에 맞는 minute을 delayed 끝에 넣으세요.\n        pass\n',
                         '        # 이 주석 아래에 조건에 맞는 minute을 delayed 끝에 넣으세요.\n        # append는 목록 끝에 값 하나를 넣어요.\n        delayed.append(minute)\n')
n7 = (Script(s7)
      .say('조건에 맞는 배송을 append로 delayed 끝에 넣어야 해요.', 'text:if 안의 주석 아래에 조건에 맞는 minute을 delayed 끝에 넣으세요.')
      .run('print(delayed)')
      .say('[]예요. 조건은 확인하지만 아직 모으지 않아요.', 'output')
      .patch('        # 이 주석 아래에 조건에 맞는 minute을 delayed 끝에 넣으세요.\n        pass\n',
             '        # 이 주석 아래에 조건에 맞는 minute을 delayed 끝에 넣으세요.\n        delayed.append(minute)\n', 'pass를 delayed.append(minute)로 바꿔요.')
      .run('print(delayed)')
      .say('[30, 42]예요. 기준 이상인 두 건이 차례로 모였어요.', 'output')
      .say('조심하세요. delayed = []를 반복 안에 두면 매번 비워져 마지막 한 건만 남아요.', 'code:delayed = []'))

SPECS = [
    dict(old='stp_699a35bd-9696-4762-b8dc-ce25348123f6', title='minutes >= limit의 결과를 late에 담으세요',
         objectives=['비교식이 참·거짓을 만드는 것을 써서 확인해요.'],
         core_flow='late = False를 late = minutes >= limit으로 고쳐 True를 확인한다. 채점은 기준보다 작은 값·같은 값·큰 값으로 실행한다.',
         goal='`>=`는 기준 이상인지 확인하는 비교예요. 비교식을 실행하면 True(참) 또는 False(거짓)가 나와요.\n\n'
              'late 줄을 고쳐 minutes가 limit 이상인지 비교한 결과를 late에 담으세요. 채점은 시간과 기준을 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 False가 나오는지 확인하세요.', '`late = False`를 `late = minutes >= limit`으로 고치세요.', '코드 실행을 눌러 True가 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s1, solution=s1_solution, tests=[{'input': '', 'expected': 'True'}],
         prepared_cases=py_cases(s1_solution, {'minutes': 31}, {'minutes': 29}, {'minutes': 30}, {'minutes': 50, 'limit': 60}),
         narration=n1.actions,
         review={'조심하세요. 비교 결과는 숫자 31이 아니라 참과 거짓이에요.': '실제 파이썬 의미를 정확히 말해요.'},
         reject=[([['late = minutes >= limit\n', 'late = True\n']], 'Typing True'), ([['late = minutes >= limit\n', 'late = minutes > limit\n']], 'Excluding the boundary')],
         accept=[([['late = minutes >= limit\n', 'late = not minutes < limit\n']], 'Negated less-than')]),
    dict(old='stp_75a91f16-862a-4a95-bea3-706bf91ead27', title='>를 >=로 고쳐 기준과 같은 값도 포함하세요',
         objectives=['경계값을 포함하는 비교와 빼는 비교를 구별해요.'],
         core_flow='minutes=30에서 minutes > limit은 False다. >=로 고쳐 True를 확인한다. 채점은 29, 31과 다른 기준으로도 실행한다.',
         goal='30분과 같은 배송도 지연에 포함해요. `>`는 기준과 같은 값을 빼고, `>=`는 같은 값도 포함해요.\n\n'
              'print 줄의 비교를 고쳐 기준과 같은 값도 True가 되게 하세요. 채점은 시간과 기준을 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 False가 나오는지 확인하세요.', '`>`를 `>=`로 고치세요.', '코드 실행을 눌러 True가 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s2, solution=s2_solution, tests=[{'input': '', 'expected': 'True'}],
         prepared_cases=py_cases(s2_solution, {'minutes': 30}, {'minutes': 29}, {'minutes': 31}, {'minutes': 45, 'limit': 45}),
         narration=n2.actions,
         review={'조심하세요. 경계값 하나 차이로 결과가 달라져요. 기준과 같은 값을 꼭 실행해 확인해요.': '실제 결과(> 와 >= 의 차이)를 정확히 말해요.'},
         reject=[([['print(minutes >= limit)', 'print(True)']], 'Typing True'), ([['print(minutes >= limit)', 'print(minutes == limit)']], 'Only the boundary')],
         accept=[([['print(minutes >= limit)', 'print(limit <= minutes)']], 'Operands swapped')]),
    dict(old='stp_4b78e11d-4464-4af1-9180-97bce84fa831', title='else를 써서 조건이 아니면 정상을 출력하세요',
         objectives=['조건에 따라 if와 else 중 한쪽만 실행됨을 써서 확인해요.'],
         core_flow='if minutes >= limit에 지연만 있고 25분은 아무것도 나오지 않는다. else: print("정상")을 더해 정상을 확인한다. 채점은 기준보다 작은 값·같은 값·큰 값으로 실행한다.',
         goal='조건이 맞으면 if 쪽, 아니면 else 쪽을 실행해요. 지금은 else가 없어서 조건이 거짓이면 아무것도 출력하지 않아요.\n\n'
              'if 아래에 else를 써서 조건이 아니면 정상을 출력하세요. else는 if와 같은 들여쓰기로 써요. 채점은 시간을 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 아무것도 나오지 않는지 확인하세요.', '주석 아래에 `else:`와 들여 쓴 `print("정상")`을 쓰세요.', '코드 실행을 눌러 정상이 나오는지 확인하세요.', '작성한 코드를 제출하세요.'),
         starter_code=s4, solution=s4_solution, tests=[{'input': '', 'expected': '정상'}],
         prepared_cases=py_cases(s4_solution, {'minutes': 25}, {'minutes': 30}, {'minutes': 31}, {'minutes': 29}),
         narration=n4.actions,
         review={'조심하세요. if와 else 중 한쪽만 실행돼요. 두 표시가 함께 나오지 않아요.': '실제 파이썬 의미를 정확히 말해요.'},
         reject=[([['else:\n    print("정상")\n', 'print("정상")\n']], 'Always printing normal'),
                 ([['if minutes >= limit:\n    print("지연")\n', 'if False:\n    print("지연")\n']], 'Never delayed')],
         accept=[([['else:\n    print("정상")\n', 'if minutes < limit:\n    print("정상")\n']], 'A second if with the opposite condition')]),
    dict(old='stp_6a06c6d6-63d6-4b42-a156-7c30b50148b5', title='append로 기준 이상인 배송을 delayed에 모으세요',
         objectives=['반복 안에서 조건에 맞는 값을 새 목록 끝에 모아요.'],
         core_flow='반복과 조건은 준비돼 있고 pass뿐이라 []다. delayed.append(minute)로 고쳐 [30, 42]를 확인한다. 채점은 다른 목록과 기준으로 실행한다.',
         goal='`append`는 목록 끝에 값 하나를 넣어요. 새 목록 delayed는 반복을 시작하기 전에 한 번만 준비돼 있어요.\n\n'
              'if 안의 주석 아래에 조건에 맞는 minute을 delayed 끝에 넣으세요. 채점은 다른 목록과 기준으로도 실행해요.\n\n'
              + todo('코드 실행을 눌러 []가 나오는지 확인하세요.', '`pass`를 `delayed.append(minute)`로 바꾸세요.', '코드 실행을 눌러 [30, 42]가 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s7, solution=s7_solution, tests=[{'input': '', 'expected': '[30, 42]'}],
         prepared_cases=py_cases(s7_solution, {'minutes': [12, 30, 42]}, {'minutes': [5, 60, 31, 29], 'limit': 31}, {'minutes': [1, 2]}),
         narration=n7.actions,
         review={'조심하세요. delayed = []를 반복 안에 두면 매번 비워져 마지막 한 건만 남아요.': '실제 흔한 실수와 그 결과를 정확히 말해요.'},
         reject=[([['        delayed.append(minute)\n', '        delayed = [minute]\n']], 'Replacing the list each time'),
                 ([['print(delayed)', 'print([30, 42])']], 'Typing the list')],
         accept=[([['        delayed.append(minute)\n', '        delayed += [minute]\n']], 'Extending with a one-item list')]),
]


# ---- 2026-10-30: the line-count field becomes a coding step (user decision) ----------------------------
from _kit import code_step

s5 = '# 배송 시간 목록이에요.\nminutes = [12, 30, 42]\n# 이 줄을 고쳐 for로 minutes의 시간을 한 건씩 한 줄에 출력하세요.\nprint(minutes)\n'
s5_solution = s5.replace('print(minutes)\n', '# for는 목록의 항목을 하나씩 minute에 담아 아래 줄을 되풀이해요.\nfor minute in minutes:\n    print(minute)\n')
n5 = (Script(s5)
      .say('for는 목록의 항목을 하나씩 minute에 담아 같은 줄을 되풀이해요. 한 건씩 한 줄에 출력하게 고쳐야 해요.', 'text:for로 minutes의 시간을 한 건씩 한 줄에 출력하세요.')
      .run('print(minutes)')
      .say('[12, 30, 42]예요. 목록 전체가 한 줄에 나왔어요.', 'output')
      .patch('print(minutes)\n', 'for minute in minutes:\n    print(minute)\n', 'for minute in minutes: 아래에 print(minute)를 들여 써요.')
      .run('print(minute)')
      .say('12, 30, 42가 각각 한 줄씩 나왔어요. 배송 세 건이라 세 번 되풀이했어요.', 'output')
      .say('조심하세요. 반복 안에서 print(minutes)를 쓰면 목록 전체가 세 번 나와요. 한 건은 minute이에요.', 'code:print(minute)'))

SPECS += [
    code_step('stp_1f28d9ac-43b5-44aa-926a-f98048c71ac5', 'for minute in minutes로 한 건씩 출력하세요', 'for가 목록의 항목마다 같은 줄을 되풀이하는 것을 직접 써서 출력 줄로 확인해요.',
              'print(minutes)는 목록 전체를 한 줄에 낸다. for minute in minutes:와 print(minute)로 고쳐 세 줄을 확인한다. 채점은 길이가 다른 목록으로 실행한다.',
              '`for 이름 in 목록:`은 목록의 항목을 앞에서부터 하나씩 이름에 담고, 그 아래 들여 쓴 줄을 항목마다 한 번씩 실행해요.',
              'print 줄을 고쳐 for로 minutes의 시간을 한 건씩 한 줄에 출력하세요. 채점은 길이가 다른 목록으로도 실행해요.',
              ['코드 실행을 눌러 출력을 확인하세요.', '`print(minutes)`를 `for minute in minutes:`와 그 아래 들여 쓴 `print(minute)`로 고치세요.', '코드 실행을 눌러 세 줄이 나오는지 확인하세요.', '수정한 코드를 제출하세요.'],
              s5, s5_solution, n5, {n5.actions[-1]['text']: '실제 파이썬 동작을 정확히 말해요.'}, cases=[{'minutes': [5]}, {'minutes': [1, 2, 3, 4]}],
              reject=[([['    print(minute)\n', '    print(minutes)\n']], 'Printing the whole list each time'),
                      ([['for minute in minutes:\n    print(minute)\n', 'print(12)\nprint(30)\nprint(42)\n']], 'Typing the three lines')],
              accept=[([['for minute in minutes:\n    print(minute)\n', 'for i in range(len(minutes)):\n    print(minutes[i])\n']], 'Index loop')]),
]
