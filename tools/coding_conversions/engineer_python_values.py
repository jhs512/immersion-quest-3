"""engineer-python-values: 2 answer-picking slice steps -> coding steps (2026-10-29)."""
from _kit import Script, todo

PRD_SCOPE = ['두 챕터·두 단원·9스텝으로 같은 상황의 조건을 하나씩 더해요.',
             '슬라이스 두 스텝은 식을 직접 써서 실행하고, 나머지는 짧은 출력 답안으로 확인해요.']
PRD_GRADING = ['직접 쓴 슬라이스는 실제 Python으로 실행하고, 목록과 시작·끝·간격 값을 바꾼 실행에서도 확인해요. 목록을 글자로 적은 답은 거절해요.',
               '출력값 답안은 직접 제출해 판정해요. 준비 코드·비교 코드·복귀 코드를 모두 실제 실행해요.',
               '마지막 도전(stp_db97db2a-0c84-44da-947f-0cce41a180db): 실제 Python 실행과 다른 준비 자료의 결과를 검사해요. 시작 코드는 실패하고 동등한 풀이도 통과해야 해요.']
PRD_NARRATION = ['한 곳을 고친 뒤 실행해 결과를 비교해요.',
                 '어떤 값이나 대상이 달라지는지 정확한 줄과 결과로 짚어요.']

s1 = 'stocks = [2, 4, 6, 8]\nstart = 1\nend = 3\n# 이 줄을 고쳐 위치 start부터 end 앞까지 고르세요.\nprint(stocks)\n'
s1_solution = 'stocks = [2, 4, 6, 8]\nstart = 1\nend = 3\n# 이 줄을 고쳐 위치 start부터 end 앞까지 고르세요.\n# 슬라이스의 끝 위치 값은 포함하지 않아요.\nprint(stocks[start:end])\n'
n1 = (Script(s1)
      .say('위치 start부터 end 앞까지 골라야 해요. 끝 위치의 값은 들어가지 않아요.', 'text:print 줄을 고쳐 위치 start부터 end 앞까지 고르세요.')
      .run('print(stocks')
      .say('목록 전체가 나와요. 아직 슬라이스가 없어요.', 'output')
      .patch('print(stocks)', 'print(stocks[start:end])', '대괄호 안에 start:end를 써요.')
      .run('print(stocks')
      .say('[4, 6]이에요. 위치 1과 2만 골랐고 위치 3의 8은 빠졌어요.', 'output')
      .say('조심하세요. 끝 위치까지 넣으려고 end + 1을 쓰면 [4, 6, 8]이 돼요.', 'code:stocks[start:end]'))

s2 = 'stocks = [2, 4, 6, 8, 10]\nstep = 2\n# 이 줄을 고쳐 처음부터 step 칸씩 건너뛰며 고르세요.\nprint(stocks)\n'
s2_solution = 'stocks = [2, 4, 6, 8, 10]\nstep = 2\n# 이 줄을 고쳐 처음부터 step 칸씩 건너뛰며 고르세요.\n# 시작과 끝을 비우면 처음부터 끝까지예요. 세 번째 자리가 간격이에요.\nprint(stocks[::step])\n'
n2 = (Script(s2)
      .say('시작과 끝을 비우고 간격 step으로 건너뛰며 골라야 해요.', 'text:print 줄을 고쳐 처음부터 step 칸씩 건너뛰며 고르세요.')
      .run('print(stocks')
      .say('목록 전체가 나와요.', 'output')
      .patch('print(stocks)', 'print(stocks[::step])', '대괄호 안에 콜론 두 개와 step을 써요.')
      .run('print(stocks')
      .say('[2, 6, 10]이에요. 위치 0, 2, 4를 골랐어요.', 'output')
      .say('조심하세요. stocks[1::2]처럼 시작을 1로 두면 [4, 8]이 돼요. 간격은 첫 칸부터 세요.', 'code:stocks[::step]'))

SPECS = [
    dict(old='stp_1cf728cd-3be4-458f-8502-6a862e608209', title='stocks[start:end]로 끝 위치 앞까지 고르세요',
         objectives=['슬라이스의 끝 위치가 포함되지 않음을 써서 확인해요.'],
         core_flow='print(stocks)를 stocks[start:end]로 고쳐 [4, 6]을 확인한다. 끝 위치 3의 값은 빠진다. 채점은 목록과 start·end를 바꿔 실행한다.',
         goal='`stocks[시작:끝]`은 시작 위치부터 끝 위치 앞까지 골라요. 끝 위치의 값은 들어가지 않아요.\n\n'
              'print 줄을 고쳐 위치 start부터 end 앞까지 고르세요. 채점은 목록과 start·end를 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 목록 전체가 나오는지 확인하세요.', '`print(stocks)`를 `print(stocks[start:end])`로 고치세요.', '코드 실행을 눌러 [4, 6]이 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s1, solution=s1_solution, tests=[{'input': '', 'expected': '[4, 6]'}],
         prepared_cases=[{'values': {'stocks': [2, 4, 6, 8]}, 'expected': '[4, 6]'},
                         {'values': {'stocks': [9, 8, 7, 6, 5], 'start': 0, 'end': 4}, 'expected': '[9, 8, 7, 6]'},
                         {'values': {'stocks': [1, 2, 3], 'start': 2, 'end': 2}, 'expected': '[]'}],
         narration=n1.actions,
         review={'조심하세요. 끝 위치까지 넣으려고 end + 1을 쓰면 [4, 6, 8]이 돼요.': '실제 결과를 정확히 말해요.'},
         reject=[([['print(stocks[start:end])', 'print(stocks[start:end + 1])']], 'Including the end'), ([['print(stocks[start:end])', 'print([4, 6])']], 'Typing the list')],
         accept=[([['print(stocks[start:end])', 'print([stocks[i] for i in range(start, end)])']], 'Comprehension over the positions')]),
    dict(old='stp_8a204e20-04c8-4a7c-acfa-c59875ccda75', title='stocks[::step]으로 간격을 두고 고르세요',
         objectives=['슬라이스의 간격으로 위치를 건너뛰어 골라요.'],
         core_flow='print(stocks)를 stocks[::step]으로 고쳐 [2, 6, 10]을 확인한다. 시작과 끝을 비우면 처음부터 끝까지다. 채점은 목록과 step을 바꿔 실행한다.',
         goal='`stocks[::간격]`은 시작과 끝을 비워 처음부터 끝까지, 간격만큼 위치를 건너뛰며 골라요.\n\n'
              'print 줄을 고쳐 처음부터 step 칸씩 건너뛰며 고르세요. 채점은 목록과 step을 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 목록 전체가 나오는지 확인하세요.', '`print(stocks)`를 `print(stocks[::step])`으로 고치세요.', '코드 실행을 눌러 [2, 6, 10]이 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s2, solution=s2_solution, tests=[{'input': '', 'expected': '[2, 6, 10]'}],
         prepared_cases=[{'values': {'stocks': [2, 4, 6, 8, 10]}, 'expected': '[2, 6, 10]'},
                         {'values': {'stocks': [1, 2, 3, 4, 5, 6, 7], 'step': 3}, 'expected': '[1, 4, 7]'},
                         {'values': {'stocks': [5, 6], 'step': 1}, 'expected': '[5, 6]'}],
         narration=n2.actions,
         review={'조심하세요. stocks[1::2]처럼 시작을 1로 두면 [4, 8]이 돼요. 간격은 첫 칸부터 세요.': '실제 결과를 정확히 말해요.'},
         reject=[([['print(stocks[::step])', 'print(stocks[1::step])']], 'Starting at position 1'), ([['print(stocks[::step])', 'print(stocks[::2])']], 'Typing the step')],
         accept=[([['print(stocks[::step])', 'print(stocks[0:len(stocks):step])']], 'Explicit start and end')]),
]
