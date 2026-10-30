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


# ---- 2026-10-30: the six code-reading answer fields become coding steps (user decision) -----------------
from _kit import code_step

PRD_SCOPE = ['두 챕터·두 단원·9스텝으로 같은 상황의 조건을 하나씩 더해요.',
             '슬라이스·역순·별칭과 복사·깊은 복사·집합 연산·사전의 기본값·나누고 잇기를 모두 한 줄씩 직접 써서 실행해요.']
PRD_GRADING = ['직접 쓴 코드는 실제 Python으로 실행하고, 목록·집합·사전·글을 바꾼 준비 자료로도 다시 실행해 기준 풀이와 비교해요.',
               '결과를 글자로 적은 답, 같은 목록을 가리키는 복사, 바깥만 복사한 목록, 키를 넣어 버리는 읽기는 거절해요.',
               '마지막 도전(stp_db97db2a-0c84-44da-947f-0cce41a180db): 실제 Python 실행과 다른 준비 자료의 결과를 검사해요. 시작 코드는 실패하고 동등한 풀이도 통과해야 해요.']
PRD_NARRATION = ['한 곳을 고친 뒤 실행해 결과를 비교해요.',
                 '어떤 값이나 대상이 달라지는지 정확한 줄과 결과로 짚어요.']

SUB = '수정한 코드를 제출하세요.'
RUN = '코드 실행을 눌러 지금 결과를 확인하세요.'
W = '실제 Python 동작을 정확히 말해요.'

v3 = 'stocks = [2, 4, 6, 8]\n# 이 줄을 고쳐 stocks를 마지막부터 처음 방향으로 읽으세요.\nprint(stocks)\n'
v3_sol = v3.replace('print(stocks)\n', '# 간격이 -1이면 끝에서부터 한 칸씩 거꾸로 읽어요. 시작과 끝을 비우면 전체예요.\nprint(stocks[::-1])\n')
w3 = (Script(v3)
      .say('목록을 마지막부터 처음 방향으로 읽어야 해요. 슬라이스의 간격을 -1로 써요.', 'text:print 줄을 고쳐 stocks를 마지막부터 처음 방향으로 읽으세요.')
      .run('print(stocks')
      .say('[2, 4, 6, 8]이에요. 아직 처음부터 읽어요.', 'output')
      .patch('print(stocks)', 'print(stocks[::-1])', '대괄호 안에 ::-1을 써요.')
      .run('print(stocks')
      .say('[8, 6, 4, 2]예요. 끝에서부터 한 칸씩 거꾸로 읽었어요.', 'output')
      .say('조심하세요. 지금은 정렬해 뒤집어도 같아 보이지만, [5, 1, 9]라면 역순은 [9, 1, 5]이고 큰 순서는 [9, 5, 1]이에요.', 'code:stocks[::-1]'))

v4 = ('stocks = [2, 4]\nadded = 6\n# 이 줄을 고쳐 backup을 stocks와 따로 쓰는 복사본으로 만드세요.\nbackup = stocks\nbackup.append(added)\n'
      'print(stocks)\nprint(backup)\n')
v4_sol = v4.replace('backup = stocks\n', '# copy()는 같은 값을 담은 새 목록을 만들어요. backup을 바꿔도 stocks는 그대로예요.\nbackup = stocks.copy()\n')
w4 = (Script(v4)
      .say('backup에 덧붙여도 stocks는 그대로여야 해요. 이름만 하나 더 붙이지 말고 새 목록으로 복사해야 해요.', 'text:backup 줄을 고쳐 backup을 stocks와 따로 쓰는 복사본으로 만드세요.')
      .run('print(stocks)', 'print(backup)')
      .say('[2, 4, 6]과 [2, 4, 6]이에요. 같은 목록에 이름이 둘이라 stocks도 바뀌었어요.', 'output')
      .patch('backup = stocks\n', 'backup = stocks.copy()\n', 'stocks 뒤에 .copy()를 붙여요.')
      .run('print(stocks)', 'print(backup)')
      .say('[2, 4]와 [2, 4, 6]이에요. backup만 새 목록이라 6이 backup에만 붙었어요.', 'output')
      .say('조심하세요. backup = stocks는 복사가 아니에요. 같은 목록에 이름을 하나 더 붙일 뿐이에요.', 'code:stocks.copy()'))

v5 = ('import copy\nrows = [[2], [4]]\nadded = 6\n# 이 줄을 고쳐 안쪽 목록까지 새로 만드는 복사본을 backup에 담으세요.\nbackup = rows.copy()\n'
      '# 복사본의 안쪽 첫 목록을 바꿔요.\nbackup[0].append(added)\nprint(rows)\nprint(backup)\n')
v5_sol = v5.replace('backup = rows.copy()\n', '# deepcopy는 안쪽 목록까지 모두 새로 만들어요. copy()는 바깥 목록만 새로 만들어요.\nbackup = copy.deepcopy(rows)\n')
w5 = (Script(v5)
      .say('복사본의 안쪽 목록을 바꿔도 rows는 그대로여야 해요. 안쪽 목록까지 새로 만드는 깊은 복사를 써요.', 'text:backup 줄을 고쳐 안쪽 목록까지 새로 만드는 복사본을 backup에 담으세요.')
      .run('print(rows)', 'print(backup)')
      .say('[[2, 6], [4]]와 [[2, 6], [4]]예요. 바깥만 복사해서 안쪽 첫 목록을 함께 써요.', 'output')
      .patch('backup = rows.copy()\n', 'backup = copy.deepcopy(rows)\n', 'rows.copy()를 copy.deepcopy(rows)로 바꿔요.')
      .run('print(rows)', 'print(backup)')
      .say('[[2], [4]]와 [[2, 6], [4]]예요. 안쪽 목록도 새로 만들어 rows는 그대로예요.', 'output')
      .say('조심하세요. list(rows)나 rows[:]도 바깥만 복사해요. 안쪽 목록은 여전히 함께 써요.', 'code:copy.deepcopy(rows)'))

v6 = ('today_ids = [2, 4, 4]\ntomorrow_ids = [4, 6]\n# set은 목록의 번호를 중복 없이 모은 집합을 만들어요.\ntoday = set(today_ids)\ntomorrow = set(tomorrow_ids)\n# 이 두 줄을 고쳐 common에는 양쪽에 모두 있는 번호, either에는 어느 한쪽에라도 있는 번호를 담으세요.\n'
      'common = today\neither = today\n# 순서와 무관한 집합을 정렬해 표시해요.\nprint(sorted(common))\nprint(sorted(either))\n')
v6_sol = v6.replace('common = today\neither = today\n', '# &는 양쪽에 모두 있는 값, |는 어느 한쪽에라도 있는 값이에요. 중복은 하나로 모여요.\ncommon = today & tomorrow\neither = today | tomorrow\n')
w6 = (Script(v6)
      .say('오늘과 내일 재고 번호를 비교해요. 공통 번호는 &, 둘 중 하나라도 있는 번호는 |로 구해요.', 'text:두 줄을 고쳐 common에는 양쪽에 모두 있는 번호, either에는 어느 한쪽에라도 있는 번호를 담으세요.')
      .run('print(sorted(common))', 'print(sorted(either))')
      .say('[2, 4]와 [2, 4]예요. 둘 다 아직 오늘 집합 그대로이고, 중복된 4는 하나로 모였어요.', 'output')
      .patch('common = today\n', 'common = today & tomorrow\n', 'common 줄에 & tomorrow를 더해요.')
      .patch('either = today\n', 'either = today | tomorrow\n', 'either 줄에 | tomorrow를 더해요.')
      .run('print(sorted(common))', 'print(sorted(either))')
      .say('[4]와 [2, 4, 6]이에요. 공통은 4 하나, 합치면 세 번호예요.', 'output')
      .say('조심하세요. &와 |를 바꿔 쓰면 공통과 전체가 뒤바뀌어요.', 'code:today & tomorrow'))

v7 = ('counts = {"pen": 2}\nitem = "book"\n# 이 줄을 고쳐 item이 없으면 0을 읽고, 사전에는 키를 넣지 마세요.\nvalue = counts[item]\n'
      'print(str(value) + ":" + str(len(counts)))\n')
v7_sol = v7.replace('value = counts[item]\n', '# get은 키가 없으면 기본값을 돌려줘요. 읽기만 하고 사전은 바꾸지 않아요.\nvalue = counts.get(item, 0)\n')
w7 = (Script(v7)
      .say('없는 item을 읽어도 멈추지 않고 0을 써야 해요. 사전에 키를 넣지 않는 get을 써요.', 'text:value 줄을 고쳐 item이 없으면 0을 읽고, 사전에는 키를 넣지 마세요.')
      .run('print(str(value)', error='KeyError')
      .say("KeyError: 'book'이에요. 대괄호로 없는 키를 읽으면 멈춰요.", 'output')
      .patch('value = counts[item]\n', 'value = counts.get(item, 0)\n', 'counts[item]을 counts.get(item, 0)으로 바꿔요.')
      .run('print(str(value)')
      .say('0:1이에요. 기본값 0을 읽었고 사전의 키는 여전히 하나예요.', 'output')
      .say('조심하세요. setdefault(item, 0)도 0을 돌려주지만 사전에 book을 넣어 키가 둘이 돼요.', 'code:counts.get(item, 0)'))

v8 = 'text = "pen,book,bag"\n# 이 줄을 고쳐 쉼표로 나눈 조각들을 슬래시로 이어 출력하세요.\nprint(text)\n'
v8_sol = v8.replace('print(text)\n', '# split(",")이 쉼표마다 나눈 목록을 만들고, "/".join이 조각 사이에 슬래시를 넣어 이어요.\nprint("/".join(text.split(",")))\n')
w8 = (Script(v8)
      .say('쉼표로 나눈 조각을 슬래시로 다시 이어야 해요. split으로 나눈 뒤 join으로 이어요.', 'text:print 줄을 고쳐 쉼표로 나눈 조각들을 슬래시로 이어 출력하세요.')
      .run('print(')
      .say('pen,book,bag이에요. 아직 원래 글 그대로예요.', 'output')
      .patch('print(text)\n', 'print("/".join(text.split(",")))\n', 'text.split(",")를 "/".join으로 감싸요.')
      .run('print(')
      .say('pen/book/bag이에요. 세 조각 사이에 슬래시가 들어갔어요.', 'output')
      .say('조심하세요. "/".join(text)처럼 나누지 않고 이으면 글자 하나하나 사이에 슬래시가 들어가요.', 'code:text.split(",")'))

SPECS += [
    code_step('stp_a1998754-ef4e-4953-8b34-0560e93bd108', 'stocks[::-1]로 뒤에서부터 읽으세요', '슬라이스의 간격 -1로 목록을 끝에서부터 거꾸로 읽어요.',
              'print(stocks)를 stocks[::-1]로 고쳐 [8, 6, 4, 2]를 확인한다. 채점은 정렬되지 않은 목록으로 실행해 큰 순서 정렬과 구별한다.',
              '간격이 -1이면 끝에서부터 한 칸씩 거꾸로 읽어요. 시작과 끝을 비우면 목록 전체예요.',
              'print 줄을 고쳐 stocks를 마지막부터 처음 방향으로 읽으세요. 채점은 다른 목록으로도 실행해요.',
              [RUN, '`print(stocks)`를 `print(stocks[::-1])`로 고치세요.', '코드 실행을 눌러 [8, 6, 4, 2]가 나오는지 확인하세요.', SUB],
              v3, v3_sol, w3, {w3.actions[-1]['text']: W}, cases=[{'stocks': [5, 1, 9]}, {'stocks': []}],
              reject=[([['print(stocks[::-1])', 'print(sorted(stocks, reverse=True))']], 'Largest first'), ([['print(stocks[::-1])', 'print([8, 6, 4, 2])']], 'Typing the list')],
              accept=[([['print(stocks[::-1])', 'print(list(reversed(stocks)))']], 'reversed')]),
    code_step('stp_aa3b0e18-d06c-433d-822f-0455415054b0', 'stocks.copy()로 따로 쓰는 복사본을 만드세요', '대입은 같은 목록에 이름을 더할 뿐이고 copy()가 새 목록을 만드는 것을 구별해요.',
              'backup = stocks면 덧붙인 6이 stocks에도 보인다. stocks.copy()로 고쳐 stocks [2, 4]와 backup [2, 4, 6]을 확인한다. 채점은 다른 목록과 값으로 실행한다.',
              '`backup = stocks`는 목록을 복사하지 않고 같은 목록에 이름을 하나 더 붙여요. `stocks.copy()`는 같은 값을 담은 새 목록을 만들어요.',
              'backup 줄을 고쳐 backup을 stocks와 따로 쓰는 복사본으로 만드세요. 채점은 다른 목록으로도 실행해요.',
              [RUN, '`backup = stocks`를 `backup = stocks.copy()`로 고치세요.', '코드 실행을 눌러 stocks가 그대로인지 확인하세요.', SUB],
              v4, v4_sol, w4, {w4.actions[-1]['text']: W, w4.actions[0]['text']: '덧붙여도 stocks가 그대로라는 대조가 이 스텝의 목표 그대로예요.'}, cases=[{'stocks': [1], 'added': 9}, {'stocks': [], 'added': 3}],
              reject=[([['backup = stocks.copy()\n', 'backup = stocks\n']], 'Same list'), ([['print(stocks)\n', 'print([2, 4])\n']], 'Typing the list')],
              accept=[([['backup = stocks.copy()\n', 'backup = stocks[:]\n']], 'Full slice')]),
    code_step('stp_4074b59c-c331-4d4d-b21e-94e813495d93', 'copy.deepcopy로 안쪽 목록까지 복사하세요', '바깥만 복사한 목록은 안쪽 목록을 함께 쓰는 것을 확인하고 깊은 복사로 나눠요.',
              'rows.copy()는 안쪽 목록을 함께 써서 rows도 [[2, 6], [4]]가 된다. copy.deepcopy(rows)로 고쳐 rows가 그대로인지 확인한다. 채점은 다른 중첩 목록으로 실행한다.',
              '`rows.copy()`는 바깥 목록만 새로 만들고 안쪽 목록은 함께 써요. `copy.deepcopy(rows)`는 안쪽 목록까지 모두 새로 만들어요.',
              'backup 줄을 고쳐 안쪽 목록까지 새로 만드는 복사본을 backup에 담으세요. 채점은 다른 중첩 목록으로도 실행해요.',
              [RUN, '`rows.copy()`를 `copy.deepcopy(rows)`로 고치세요.', '코드 실행을 눌러 rows가 그대로인지 확인하세요.', SUB],
              v5, v5_sol, w5, {w5.actions[-1]['text']: W}, cases=[{'rows': [[1, 2], [3]], 'added': 0}, {'rows': [[], [5]], 'added': 7}],
              reject=[([['backup = copy.deepcopy(rows)\n', 'backup = list(rows)\n']], 'Shallow list()'), ([['backup = copy.deepcopy(rows)\n', 'backup = rows.copy()\n']], 'Shallow copy()')],
              accept=[([['backup = copy.deepcopy(rows)\n', 'backup = [row[:] for row in rows]\n']], 'Copying each inner list')]),
    code_step('stp_827dd588-04d5-41ea-aaa5-70c0c1c89ee5', '&와 |로 공통 번호와 전체 번호를 구하세요', '집합의 교집합과 합집합을 직접 써서 구별해요.',
              'common과 either가 오늘 집합 그대로면 [2, 4]다. today & tomorrow와 today | tomorrow로 고쳐 [4]와 [2, 4, 6]을 확인한다. 채점은 다른 집합으로 실행한다.',
              '집합은 중복 없이 값을 모아요. `&`는 양쪽에 모두 있는 값, `|`는 어느 한쪽에라도 있는 값이에요. 오늘과 내일의 재고 번호를 비교해요.',
              '두 줄을 고쳐 common에는 양쪽에 모두 있는 번호, either에는 어느 한쪽에라도 있는 번호를 담으세요. 채점은 다른 번호로도 실행해요.',
              [RUN, '`common = today`를 `common = today & tomorrow`로 고치세요.', '`either = today`를 `either = today | tomorrow`로 고치세요.', '코드 실행을 눌러 두 결과를 확인하세요.', SUB],
              v6, v6_sol, w6, {w6.actions[-1]['text']: W, w6.actions[0]['text']: '「하나라도」는 합집합의 정의를 정확히 말해요.'}, cases=[{'today_ids': [1, 3, 5], 'tomorrow_ids': [3, 5, 7]}, {'today_ids': [9], 'tomorrow_ids': []}],
              reject=[([['common = today & tomorrow\neither = today | tomorrow\n', 'common = today | tomorrow\neither = today & tomorrow\n']], 'Swapped operators'),
                      ([['common = today & tomorrow\n', 'common = {4}\n']], 'Typing the common set')],
              accept=[([['common = today & tomorrow\neither = today | tomorrow\n', 'common = today.intersection(tomorrow)\neither = today.union(tomorrow)\n']], 'Method names')]),
    code_step('stp_abac6677-eb8c-44e9-a954-c698fd21a228', 'counts.get(item, 0)으로 없는 키를 읽으세요', '없는 키를 기본값으로 읽되 사전을 바꾸지 않는 get을 구별해요.',
              'counts[item]은 KeyError다. counts.get(item, 0)으로 고쳐 0:1을 확인한다. 채점은 키가 있는 사전과 빈 사전으로 실행해 setdefault와 구별한다.',
              '`counts[키]`는 없는 키를 읽으면 KeyError로 멈춰요. `counts.get(키, 기본값)`은 키가 없으면 기본값을 돌려주지만 사전에 키를 넣지는 않아요.',
              'value 줄을 고쳐 item이 없으면 0을 읽고, 사전에는 키를 넣지 마세요. 채점은 다른 사전과 키로도 실행해요.',
              ['코드 실행을 눌러 KeyError가 나오는지 확인하세요.', '`counts[item]`을 `counts.get(item, 0)`으로 고치세요.', '코드 실행을 눌러 0:1이 나오는지 확인하세요.', SUB],
              v7, v7_sol, w7, {w7.actions[-1]['text']: W, w7.actions[0]['text']: '없는 키를 읽어도 멈추지 않는다는 대조가 실제 KeyError와 get의 차이예요.'}, cases=[{'counts': {'book': 3}}, {'counts': {}, 'item': 'x'}],
              reject=[([['value = counts.get(item, 0)\n', 'value = counts.setdefault(item, 0)\n']], 'setdefault adds the key'),
                      ([['value = counts.get(item, 0)\n', 'value = 0\n']], 'Always zero')],
              accept=[([['value = counts.get(item, 0)\n', 'value = counts[item] if item in counts else 0\n']], 'Membership test')]),
    code_step('stp_e3dbf632-4a34-4c0b-818e-c4251dbd20a4', 'split과 join으로 조각을 슬래시로 이어 출력하세요', '글을 구분자로 나눈 목록과 다른 구분자로 잇는 과정을 직접 써요.',
              'print(text)는 원래 글이다. "/".join(text.split(","))로 고쳐 pen/book/bag을 확인한다. 채점은 다른 글로 실행한다.',
              '`split(",")`은 쉼표마다 글을 나눠 목록을 만들고, `"/".join(목록)`은 목록의 글 사이에 슬래시를 넣어 이어요.',
              'print 줄을 고쳐 쉼표로 나눈 조각들을 슬래시로 이어 출력하세요. 채점은 다른 글로도 실행해요.',
              [RUN, '`print(text)`를 `print("/".join(text.split(",")))`로 고치세요.', '코드 실행을 눌러 pen/book/bag이 나오는지 확인하세요.', SUB],
              v8, v8_sol, w8, {w8.actions[-1]['text']: W}, cases=[{'text': 'a,b'}, {'text': 'solo'}],
              reject=[([['print("/".join(text.split(",")))\n', 'print("/".join(text))\n']], 'Joining letters'), ([['print("/".join(text.split(",")))\n', 'print("pen/book/bag")\n']], 'Typing the text')],
              accept=[([['print("/".join(text.split(",")))\n', 'print(text.replace(",", "/"))\n']], 'replace gives the same text')]),
]
