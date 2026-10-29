"""engineer-python-calls: 2 answer-picking steps -> coding steps (2026-10-29)."""
from _kit import Script, todo

PRD_SCOPE = ['두 챕터·두 단원·11스텝으로 같은 상황의 조건을 하나씩 더해요.',
             '기본 인수와 공유되는 기본 목록은 코드를 직접 써서 실행하고, 나머지는 짧은 출력 답안으로 확인해요.']
PRD_GRADING = ['직접 쓴 코드는 실제 Python으로 실행하고, 준비 값을 바꾼 실행과 실행 뒤 상태까지 확인해요. 결과를 글자로 적은 답은 거절해요.',
               '출력값 답안은 직접 제출해 판정해요. 준비 코드·비교 코드·복귀 코드를 모두 실제 실행해요.',
               '마지막 도전(stp_a474fa8a-a0c0-4eaa-99c8-31d2a5b908cf): 실제 Python 실행과 다른 준비 자료의 결과를 검사해요. 시작 코드는 실패하고 동등한 풀이도 통과해야 해요.']
PRD_NARRATION = ['한 곳을 고친 뒤 실행해 결과를 비교해요.',
                 '어떤 값이나 대상이 달라지는지 정확한 줄과 결과로 짚어요.']

s1 = 'stock = 3\n\n\n# 이 줄을 고쳐 size를 생략하면 2를 쓰게 하세요.\ndef packs(stock, size):\n    # 두 인수의 곱을 반환해요.\n    return stock * size\n\n\nprint(packs(stock))\nprint(packs(stock, 4))\n'
s1_solution = s1.replace('def packs(stock, size):', '# 기본값은 매개변수 뒤에 = 값으로 써요. 호출에서 생략하면 그 값을 써요.\ndef packs(stock, size=2):')
n1 = (Script(s1)
      .say('packs(stock)처럼 size를 생략해도 2를 쓰게 기본값을 정해야 해요.', 'text:def 줄을 고쳐 size를 생략하면 2를 쓰게 하세요.')
      .run('print(packs(stock))', 'print(packs(stock, 4))', error='TypeError')
      .say('TypeError예요. size 없이 불렀는데 기본값이 없어요.', 'output')
      .patch('def packs(stock, size):', 'def packs(stock, size=2):', 'size 뒤에 =2를 붙여요.')
      .run('print(packs(stock))', 'print(packs(stock, 4))')
      .say('6과 12예요. 생략하면 기본값 2를, 직접 준 4는 그대로 써요.', 'output')
      .say('조심하세요. 기본값이 있는 매개변수는 기본값이 없는 매개변수 뒤에 와야 해요.', 'code:def packs(stock, size=2):'))

s2 = ('a = 2\nb = 4\n\n\ndef record(value, items=[]):\n    # 기본 목록을 여러 호출이 함께 사용해요.\n    items.append(value)\n    return items\n\n\n'
      '# 이 주석 아래에 record(a)와 record(b)의 결과를 first와 second에 담으세요.\n'
      'print(first is second)\nprint(first)\n')
s2_solution = s2.replace('# 이 주석 아래에 record(a)와 record(b)의 결과를 first와 second에 담으세요.\n',
                         '# 이 주석 아래에 record(a)와 record(b)의 결과를 first와 second에 담으세요.\n'
                         '# 기본 목록은 def를 실행할 때 한 번만 만들어져요. 두 호출이 같은 목록을 돌려줘요.\n'
                         'first = record(a)\nsecond = record(b)\n')
n2 = (Script(s2)
      .say('record를 두 번 불러 결과를 담고, 두 결과가 같은 목록인지 확인해야 해요.', 'text:주석 아래에 record(a)와 record(b)의 결과를 first와 second에 담으세요.')
      .run('print(first is second)', 'print(first)', error='NameError')
      .say('NameError예요. 아직 first를 만들지 않았어요.', 'output')
      .patch('# 이 주석 아래에 record(a)와 record(b)의 결과를 first와 second에 담으세요.\n',
             '# 이 주석 아래에 record(a)와 record(b)의 결과를 first와 second에 담으세요.\nfirst = record(a)\nsecond = record(b)\n',
             'record(a)를 first에, record(b)를 second에 담아요.')
      .run('print(first is second)', 'print(first)')
      .say('True와 [2, 4]예요. 두 호출이 같은 기본 목록에 차례로 더했어요.', 'output')
      .say('조심하세요. 호출할 때마다 빈 목록이 새로 생긴다고 생각하면 [2]를 예상하게 돼요.', 'code:items=[]'))

SPECS = [
    dict(old='stp_e131c37e-e4fd-47e7-a511-a0bed9dc9303', title='size에 기본값 2를 정해 생략한 호출도 되게 하세요',
         objectives=['기본 인수와 직접 준 값의 차이를 써서 확인해요.'],
         core_flow='packs(stock, size)에 기본값이 없어 packs(stock)은 TypeError다. size=2로 고쳐 6과 12를 확인한다. 채점은 stock을 바꿔 실행한다.',
         goal='매개변수에 `size=2`처럼 기본값을 정하면 호출에서 그 인수를 생략할 수 있어요. 직접 값을 주면 기본값 대신 그 값을 써요.\n\n'
              'def 줄을 고쳐 size를 생략하면 2를 쓰게 하세요. 채점은 stock을 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 TypeError가 나오는지 확인하세요.', '`def packs(stock, size):`의 size 뒤에 `=2`를 붙이세요.', '코드 실행을 눌러 6과 12가 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s1, solution=s1_solution, tests=[{'input': '', 'expected': '6\n12'}],
         prepared_cases=[{'values': {'stock': 3}, 'expected': '6\n12'}, {'values': {'stock': 5}, 'expected': '10\n20'}, {'values': {'stock': 0}, 'expected': '0\n0'}],
         narration=n1.actions,
         review={'packs(stock)처럼 size를 생략해도 2를 쓰게 기본값을 정해야 해요.': '「생략해도」는 기본 인수의 실제 의미와 맞아요.', '조심하세요. 기본값이 있는 매개변수는 기본값이 없는 매개변수 뒤에 와야 해요.': '실제 Python 문법 규칙을 정확히 말해요.'},
         reject=[([['def packs(stock, size=2):', 'def packs(stock, size=4):']], 'Wrong default'),
                 ([['print(packs(stock))\nprint(packs(stock, 4))\n', 'print(6)\nprint(12)\n']], 'Typing the results')],
         accept=[([['def packs(stock, size=2):', 'def packs(stock, size=None):\n    if size is None:\n        size = 2']], 'None sentinel')]),
    dict(old='stp_12c58c54-416f-4e12-ba60-29a57b8675f1', title='record를 두 번 불러 기본 목록이 공유되는지 확인하세요',
         objectives=['가변 기본 인수가 호출 사이에 공유됨을 실행으로 확인해요.'],
         core_flow='record(value, items=[])를 두 번 불러 first와 second에 담는다. first is second가 True이고 목록은 [2, 4]다. 채점은 a와 b를 바꾸고 실행 뒤 first·second가 실제로 record의 기본 목록 그 자체인지 검사한다.',
         goal='`items=[]`처럼 기본값을 목록으로 두면 그 목록은 함수를 정의할 때 한 번만 만들어져요. 그래서 items를 생략한 호출은 모두 같은 목록을 함께 써요. `is`는 두 이름이 같은 객체인지 확인해요.\n\n'
              '주석 아래에 record(a)와 record(b)의 결과를 first와 second에 담으세요. 채점은 a와 b를 바꾸고 실행 뒤의 first와 second도 확인해요.\n\n'
              + todo('코드 실행을 눌러 NameError가 나오는지 확인하세요.', '주석 아래에 `first = record(a)`와 `second = record(b)`를 쓰세요.', '코드 실행을 눌러 True와 [2, 4]가 나오는지 확인하세요.', '작성한 코드를 제출하세요.'),
         starter_code=s2, solution=s2_solution, tests=[{'input': '', 'expected': 'True\n[2, 4]'}],
         prepared_cases=[{'values': {'a': 2, 'b': 4}, 'expected': 'True\n[2, 4]'}, {'values': {'a': 7, 'b': 1}, 'expected': 'True\n[7, 1]'}],
         prepared_probes='assert first is second is record.__defaults__[0] and first == [a, b]',
         narration=n2.actions,
         review={'조심하세요. 호출할 때마다 빈 목록이 새로 생긴다고 생각하면 [2]를 예상하게 돼요.': '실제 흔한 오개념과 그 예상 출력을 말해요.'},
         reject=[([['first = record(a)\nsecond = record(b)\n', 'first = [a, b]\nsecond = first\n']], 'Building the list by hand'),
                 ([['first = record(a)\nsecond = record(b)\n', 'first = record(a)\nsecond = record(b, [])\n']], 'Passing a new list for the second call')],
         accept=[([['first = record(a)\nsecond = record(b)\n', 'first, second = record(a), record(b)\n']], 'Tuple assignment')]),
]
