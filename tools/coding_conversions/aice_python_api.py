"""aice-python-api: 5 answer-picking steps -> coding steps (2026-10-29)."""
from _kit import Script, todo, py_cases

OPENING = ['이 수업에서는 자료와 기능을 연결하는 표기를 직접 써 가며 배워요. 딕셔너리 키와 목록의 위치를 구별해요.',
           '자료를 꺼내고 호출에 옵션을 전달해요. 모듈과 별칭을 이용한 기능 호출로 이어가요.']
PRD_SCOPE = ['딕셔너리와 목록 값, 키 선택·길이를 한 줄씩 직접 고쳐 비교해요.',
             'sorted·reverse와 statistics.mean으로 호출·import를 직접 써요.',
             '두 챕터·두 단원·아홉 스텝으로 이어 가요.']
PRD_GRADING = ['직접 쓴 코드를 실제 파이썬으로 실행해 판정해요. 실행·해설만으로 성공하지 않아요.',
               '항목 두 개와 배송 건수가 다른 사례로 항목 수를 건수로 착각하는 풀이를 거절해요. 다른 기록·목록으로도 실행해 값을 글자로 적은 답을 거절해요.',
               '별칭은 준비 코드의 연결 관계로 판단해요. stats 철자 자체를 암기 기준으로 삼지 않아요.',
               '마지막 도전(stp_3ec1a5c3-b2a2-46e2-83c1-6d6ad7ebf28a): 실제 파이썬 출력과 다른 기록 세 개로 채점해요. 항목 수를 건수로, 원래 모듈 이름 호출, 원본 정렬은 실패해요.']
PRD_NARRATION = ['키·옵션·호출 한 곳씩 고쳐 실행해요.',
                 '키 오타와 항목 수·건수 혼동을 실제 결과로 비교해요.',
                 '정확한 코드 줄·실행 버튼·결과를 강조하고 음성 준비 후 함께 진행해요.']

s1 = '# 항목 이름인 키에 값을 연결해요.\nrecord = {"minutes": 18, "region": "서쪽"}\n# 이 줄의 키를 고쳐 배송 시간을 꺼내세요.\nprint(record["region"])\n'
s1_solution = s1.replace('print(record["region"])', '# 대괄호 안의 키가 꺼낼 값을 정해요.\nprint(record["minutes"])')
n1 = (Script(s1)
      .say('키는 값에 붙인 항목 이름이에요. 배송 시간을 꺼내도록 키를 고쳐야 해요.', 'text:print 줄의 키를 고쳐 배송 시간을 꺼내세요.')
      .run('print(record[')
      .say('서쪽이에요. region 키의 값을 꺼냈어요.', 'output')
      .patch('print(record["region"])', 'print(record["minutes"])', '키를 "minutes"로 바꿔요.')
      .run('print(record[')
      .say('18이에요. minutes 키에 연결된 배송 시간이에요.', 'output')
      .say('조심하세요. 키 이름은 글자가 정확히 같아야 해요. "minute"처럼 틀리면 KeyError예요.', 'code:record["minutes"]'))

s2 = '# 같은 이름의 항목들을 목록으로 묶어요.\ndata = {"minutes": [12, 18, 24], "region": ["서쪽", "동쪽", "서쪽"]}\n# 이 줄을 고쳐 첫 시간이 아니라 시간 목록 전체를 출력하세요.\nprint(data["minutes"][0])\n'
s2_solution = s2.replace('print(data["minutes"][0])', '# data["minutes"]에는 시간 목록 전체가 연결돼 있어요.\nprint(data["minutes"])')
n2 = (Script(s2)
      .say('배송 세 건의 시간이 한 키에 목록으로 모였어요. 목록 전체를 출력해야 해요.', 'text:print 줄을 고쳐 첫 시간이 아니라 시간 목록 전체를 출력하세요.')
      .run('print(data[')
      .say('12예요. 뒤에 붙은 [0]이 목록의 첫 항목만 골랐어요.', 'output')
      .patch('print(data["minutes"][0])', 'print(data["minutes"])', '뒤의 [0]을 지워요.')
      .run('print(data[')
      .say('[12, 18, 24]예요. 키에 연결된 목록 전체예요.', 'output')
      .say('조심하세요. 키로 꺼낸 값이 목록이면 그 뒤의 [0]은 목록 안의 위치예요.', 'code:print(data["minutes"])'))

s3 = '# 같은 이름의 항목들을 목록으로 묶어요.\ndata = {"minutes": [12, 18, 24], "region": ["서쪽", "동쪽", "서쪽"]}\n# 이 줄을 고쳐 항목 수가 아니라 배송 건수를 count에 담으세요.\ncount = len(data)\nprint(count)\n'
s3_solution = s3.replace('count = len(data)\n', '# 딕셔너리의 len은 키 개수예요. 건수는 시간 목록의 길이예요.\ncount = len(data["minutes"])\n')
n3 = (Script(s3)
      .say('항목은 두 종류지만 배송은 세 건이에요. 배송 건수를 count에 담아야 해요.', 'text:count 줄을 고쳐 항목 수가 아니라 배송 건수를 count에 담으세요.')
      .run('print(count)')
      .say('2예요. len(data)는 키 minutes와 region의 개수예요.', 'output')
      .patch('count = len(data)\n', 'count = len(data["minutes"])\n', '시간 목록 data["minutes"]의 길이를 세요.')
      .run('print(count)')
      .say('3이에요. 시간 목록에 든 배송 건수예요.', 'output')
      .say('조심하세요. 지금처럼 항목 수와 건수가 비슷하면 우연히 맞을 수 있어요. 무엇의 길이인지 확인해요.', 'code:len(data["minutes"])'))

s5 = '# 원래 시간 목록은 그대로 두고 기능에 전달해요.\nminutes = [24, 12, 18]\n# 이 줄을 고쳐 sorted에 minutes를 전달한 결과를 ordered에 담으세요.\nordered = minutes\nprint(ordered)\nprint(minutes)\n'
s5_solution = s5.replace('ordered = minutes\n', '# sorted는 작은 값부터 정렬한 새 목록을 돌려줘요. 원래 목록은 그대로예요.\nordered = sorted(minutes)\n')
n5 = (Script(s5)
      .say('시간을 짧은 순서로 보고 싶어요. sorted 괄호 안에 minutes를 전달해야 해요.', 'text:ordered 줄을 고쳐 sorted에 minutes를 전달한 결과를 ordered에 담으세요.')
      .run('print(ordered)', 'print(minutes)')
      .say('두 줄 모두 [24, 12, 18]이에요. 아직 정렬하지 않았어요.', 'output')
      .patch('ordered = minutes\n', 'ordered = sorted(minutes)\n', 'sorted(minutes)의 결과를 ordered에 담아요.')
      .run('print(ordered)', 'print(minutes)')
      .say('[12, 18, 24]와 [24, 12, 18]이에요. 새 목록만 정렬됐고 원래 목록은 그대로예요.', 'output')
      .say('조심하세요. minutes.sort()는 원래 목록을 바꾸고 None을 돌려줘요.', 'code:ordered = sorted(minutes)'))

s7 = '# 평균 기능을 가진 모듈을 불러와요.\nimport statistics\nminutes = [12, 18, 24]\n# 이 줄을 고쳐 statistics 모듈 안의 mean 기능으로 평균을 구하세요.\nprint(mean(minutes))\n'
s7_solution = s7.replace('print(mean(minutes))', '# 점 앞은 모듈 이름, 점 뒤는 그 모듈 안의 기능 이름이에요.\nprint(statistics.mean(minutes))')
n7 = (Script(s7)
      .say('mean은 import로 불러온 statistics 모듈 안의 기능이에요. 모듈 이름을 붙여 불러야 해요.', 'text:print 줄을 고쳐 statistics 모듈 안의 mean 기능으로 평균을 구하세요.')
      .run('print(', error='NameError')
      .say('NameError예요. mean이라는 이름만으로는 찾을 수 없어요.', 'output')
      .patch('print(mean(minutes))', 'print(statistics.mean(minutes))', 'mean 앞에 statistics.을 붙여요.')
      .run('print(')
      .say('18이에요. 시간의 합 54를 건수 3으로 나눴어요.', 'output')
      .say('조심하세요. import statistics는 모듈 이름만 불러와요. 안의 기능은 statistics.mean처럼 점으로 꺼내요.', 'code:statistics.mean(minutes)'))

SPECS = [
    dict(old='stp_10377fe6-6c7f-410d-92c9-a3d416ca17c5', title='키 minutes로 배송 시간을 꺼내세요',
         objectives=['딕셔너리에서 키로 값을 꺼내요.'],
         core_flow='record["region"]은 서쪽이다. 키를 "minutes"로 고쳐 18을 확인한다. 채점은 다른 기록으로 실행한다.',
         goal='딕셔너리의 키는 값에 붙인 항목 이름이에요. `record["키"]`로 그 키에 연결된 값을 꺼내요.\n\n'
              'print 줄의 키를 고쳐 배송 시간을 꺼내세요. 채점은 다른 기록으로도 실행해요.\n\n'
              + todo('코드 실행을 눌러 서쪽이 나오는지 확인하세요.', '키 `"region"`을 `"minutes"`로 고치세요.', '코드 실행을 눌러 18이 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s1, solution=s1_solution, tests=[{'input': '', 'expected': '18'}],
         prepared_cases=py_cases(s1_solution, {'record': {'minutes': 18, 'region': '서쪽'}}, {'record': {'minutes': 33, 'region': '북쪽'}}),
         narration=n1.actions,
         review={'조심하세요. 키 이름은 글자가 정확히 같아야 해요. "minute"처럼 틀리면 KeyError예요.': '실제 파이썬 동작을 정확히 말해요.'},
         reject=[([['print(record["minutes"])', 'print(18)']], 'Typing the value')],
         accept=[([['print(record["minutes"])', 'print(record.get("minutes"))']], 'dict.get')]),
    dict(old='stp_a38fc186-b43e-4233-9d36-433664dec5bf', title='data["minutes"]로 시간 목록 전체를 출력하세요',
         objectives=['키로 꺼낸 목록 전체와 목록 안의 한 위치를 구별해요.'],
         core_flow='data["minutes"][0]은 첫 시간 12다. [0]을 지워 [12, 18, 24]를 확인한다. 채점은 다른 자료로 실행한다.',
         goal='배송 세 건의 시간이 한 키 minutes에 목록으로 모였어요. `data["minutes"]`는 그 목록 전체이고, 뒤에 `[0]`을 붙이면 목록의 첫 항목이에요.\n\n'
              'print 줄을 고쳐 첫 시간이 아니라 시간 목록 전체를 출력하세요. 채점은 다른 자료로도 실행해요.\n\n'
              + todo('코드 실행을 눌러 12가 나오는지 확인하세요.', '`data["minutes"]` 뒤의 `[0]`을 지우세요.', '코드 실행을 눌러 [12, 18, 24]가 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s2, solution=s2_solution, tests=[{'input': '', 'expected': '[12, 18, 24]'}],
         prepared_cases=py_cases(s2_solution, {'data': {'minutes': [12, 18, 24], 'region': ['서쪽', '동쪽', '서쪽']}}, {'data': {'minutes': [7, 40], 'region': ['남쪽', '서쪽']}}),
         narration=n2.actions,
         review={'조심하세요. 키로 꺼낸 값이 목록이면 그 뒤의 [0]은 목록 안의 위치예요.': '실제 파이썬 의미를 정확히 말해요.'},
         reject=[([['print(data["minutes"])', 'print(data["region"])']], 'Wrong key'), ([['print(data["minutes"])', 'print([12, 18, 24])']], 'Typing the list')],
         accept=[([['print(data["minutes"])', 'print(list(data["minutes"]))']], 'Copy of the list')]),
    dict(old='stp_1b46cb1c-3e19-41e1-9e6c-3733d82f84ae', title='len(data["minutes"])로 배송 건수를 세세요',
         objectives=['딕셔너리의 항목 수와 목록의 건수를 구별해요.'],
         core_flow='len(data)는 키 개수 2다. len(data["minutes"])로 고쳐 3을 확인한다. 채점은 키 개수와 건수가 다른 자료로 실행한다.',
         goal='항목은 minutes와 region 두 종류지만 배송은 세 건이에요. 딕셔너리에 len을 쓰면 키의 개수가 나오고, 배송 건수는 시간 목록의 길이예요.\n\n'
              'count 줄을 고쳐 항목 수가 아니라 배송 건수를 count에 담으세요. 채점은 키 개수와 건수가 다른 자료로도 실행해요.\n\n'
              + todo('코드 실행을 눌러 2가 나오는지 확인하세요.', '`len(data)`를 `len(data["minutes"])`로 고치세요.', '코드 실행을 눌러 3이 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s3, solution=s3_solution, tests=[{'input': '', 'expected': '3'}],
         prepared_cases=py_cases(s3_solution, {'data': {'minutes': [12, 18, 24], 'region': ['서쪽', '동쪽', '서쪽']}},
                                 {'data': {'minutes': [5, 6, 7, 8, 9], 'region': ['a', 'b', 'c', 'd', 'e']}}, {'data': {'minutes': [30, 31], 'region': ['a', 'b']}}),
         narration=n3.actions,
         review={'조심하세요. 지금처럼 항목 수와 건수가 비슷하면 우연히 맞을 수 있어요. 무엇의 길이인지 확인해요.': '실제 위험(키 2개·건수 2개면 우연히 같음, 채점 사례에 포함)을 정확히 말해요.'},
         reject=[([['count = len(data["minutes"])\n', 'count = 3\n']], 'Typing the count'), ([['count = len(data["minutes"])\n', 'count = len(data)\n']], 'Number of keys')],
         accept=[([['count = len(data["minutes"])\n', 'count = len(data["region"])\n']], 'Any column of the same records has the same length')]),
    dict(old='stp_58ab4230-8042-4f48-85e3-5bf324f1feae', title='sorted(minutes)의 결과를 ordered에 담으세요',
         objectives=['기능에 자료를 전달하고 돌려받은 새 값을 써요.'],
         core_flow='ordered = minutes는 정렬되지 않는다. ordered = sorted(minutes)로 고쳐 [12, 18, 24]와 그대로인 원래 목록을 확인한다. 채점은 다른 목록으로 실행한다.',
         goal='시간을 짧은 순서로 보고 싶어요. `sorted(목록)`은 괄호 안에 전달한 목록을 작은 값부터 정렬한 새 목록을 돌려줘요. 원래 목록은 바꾸지 않아요.\n\n'
              'ordered 줄을 고쳐 sorted에 minutes를 전달한 결과를 ordered에 담으세요. 채점은 다른 목록으로도 실행해요.\n\n'
              + todo('코드 실행을 눌러 두 줄이 같은지 확인하세요.', '`ordered = minutes`를 `ordered = sorted(minutes)`로 고치세요.', '코드 실행을 눌러 정렬된 목록과 원래 목록을 비교하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s5, solution=s5_solution, tests=[{'input': '', 'expected': '[12, 18, 24]\n[24, 12, 18]'}],
         prepared_cases=py_cases(s5_solution, {'minutes': [24, 12, 18]}, {'minutes': [9, 3, 7, 1]}),
         narration=n5.actions,
         review={'조심하세요. minutes.sort()는 원래 목록을 바꾸고 None을 돌려줘요.': '실제 파이썬 동작을 정확히 말해요.'},
         reject=[([['ordered = sorted(minutes)\n', 'minutes.sort()\nordered = minutes\n']], 'Sorting the original in place'),
                 ([['ordered = sorted(minutes)\n', 'ordered = [12, 18, 24]\n']], 'Typing the list')],
         accept=[([['ordered = sorted(minutes)\n', 'ordered = list(minutes)\nordered.sort()\n']], 'Sorting a copy')]),
    dict(old='stp_cb4ab2ac-d4b3-4bfe-8898-628a99e37a6c', title='statistics.mean으로 모듈 안의 평균 기능을 부르세요',
         objectives=['import한 모듈 안의 기능을 점 표기로 불러요.'],
         core_flow='import statistics 뒤 mean(minutes)는 NameError다. statistics.mean(minutes)로 고쳐 18을 확인한다. 채점은 다른 목록으로 실행한다.',
         goal='평균은 시간의 합을 건수로 나눈 값이에요. `import statistics`로 평균 기능을 가진 모듈을 불러왔어요. 점(.) 앞은 모듈 이름, 점 뒤는 그 모듈 안의 기능 이름이에요.\n\n'
              'print 줄을 고쳐 statistics 모듈 안의 mean 기능으로 평균을 구하세요. 채점은 다른 목록으로도 실행해요.\n\n'
              + todo('코드 실행을 눌러 NameError가 나오는지 확인하세요.', '`mean(minutes)`를 `statistics.mean(minutes)`로 고치세요.', '코드 실행을 눌러 18이 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s7, solution=s7_solution, tests=[{'input': '', 'expected': '18'}],
         prepared_cases=py_cases(s7_solution, {'minutes': [12, 18, 24]}, {'minutes': [5, 10]}, {'minutes': [7, 7, 8]}),
         narration=n7.actions,
         review={'조심하세요. import statistics는 모듈 이름만 불러와요. 안의 기능은 statistics.mean처럼 점으로 꺼내요.': '실제 파이썬 import 의미를 정확히 말해요.'},
         reject=[([['print(statistics.mean(minutes))', 'print(18)']], 'Typing the value'),
                 ([['print(statistics.mean(minutes))', 'print(statistics.median(minutes))']], 'Median instead of mean')],
         accept=[([['print(statistics.mean(minutes))', 'from statistics import mean\nprint(mean(minutes))']], 'Importing the function itself')]),
]
