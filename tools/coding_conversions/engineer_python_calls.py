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


# ---- 2026-10-30: the eight code-reading answer fields become coding steps (user decision) ---------------
from _kit import code_step

PRD_SCOPE = ['두 챕터·두 단원·11스텝으로 같은 재고 기록 함수와 객체를 다뤄요.',
             '기본값·인수로 받은 목록 수정·클래스 속성·재정의와 super·global·try/except/finally·재귀·키워드 인수·가변 인수를 모두 한두 줄씩 직접 써서 실행해요.']
PRD_GRADING = ['직접 쓴 코드는 실제 Python으로 실행하고, 값을 바꾼 준비 자료로도 다시 실행해 기준 풀이와 비교해요.',
               '결과를 글자로 적은 답, 매개변수만 다시 대입한 답, 객체 속성을 새로 만든 답, 자기 자신을 부르는 답, finally 없이 출력 위치만 맞춘 답은 거절해요.',
               '마지막 도전: 실제 Python 실행과 다른 준비 자료의 결과를 검사해요. 시작 코드는 실패하고 동등한 풀이도 통과해야 해요.']

SUBC = '수정한 코드를 제출하세요.'
RUNC = '코드 실행을 눌러 지금 결과를 확인하세요.'
WC = '실제 Python 동작을 정확히 말해요.'

c3 = ('def add(items, value):\n    # 이 줄을 고쳐 받은 목록 자체에 value를 덧붙이세요.\n    items = items + [value]\n'
      'stocks = [2]\nadded = 4\nadd(stocks, added)\nprint(stocks)\n')
c3_sol = c3.replace('    items = items + [value]\n', '    # items는 호출한 쪽과 같은 목록을 가리켜요. append는 그 목록 자체를 바꿔요.\n    items.append(value)\n')
d3 = (Script(c3)
      .say('함수 안에서 받은 목록 자체에 값을 덧붙여야 해요. 새 목록을 만들어 이름만 바꾸지 말고 append를 써요.', 'text:items 줄을 고쳐 받은 목록 자체에 value를 덧붙이세요.')
      .run('print(stocks)')
      .say('[2]예요. items + [value]는 새 목록을 만들어 함수 안의 이름만 바꿨어요.', 'output')
      .patch('    items = items + [value]\n', '    items.append(value)\n', 'items.append(value)로 바꿔요.')
      .run('print(stocks)')
      .say('[2, 4]예요. stocks와 같은 목록에 4가 붙었어요.', 'output')
      .say('조심하세요. 함수 안에서 매개변수에 새로 대입하면 호출한 쪽의 목록은 그대로예요.', 'code:items.append(value)'))

c4 = ('class Counter:\n    total = 0\na = Counter()\nb = Counter()\namount = 2\n'
      '# 이 줄을 고쳐 모든 객체가 함께 쓰는 클래스 속성 Counter.total을 amount만큼 늘리세요.\na.total += amount\n'
      'print(str(a.total) + ":" + str(b.total))\n')
c4_sol = c4.replace('a.total += amount\n', '# 클래스 이름으로 바꿔야 모든 객체가 함께 읽는 값이 바뀌어요. a.total에 대입하면 a만의 속성이 새로 생겨요.\nCounter.total += amount\n')
d4 = (Script(c4)
      .say('모든 객체가 함께 쓰는 total을 늘려야 해요. 객체가 아니라 클래스 이름으로 바꿔요.', 'text:a.total 줄을 고쳐 모든 객체가 함께 쓰는 클래스 속성 Counter.total을 amount만큼 늘리세요.')
      .run('print(str(a.total)')
      .say('2:0이에요. a에만 total 속성이 새로 생기고 b는 클래스의 0을 읽어요.', 'output')
      .patch('a.total += amount\n', 'Counter.total += amount\n', 'a.total을 Counter.total로 바꿔요.')
      .run('print(str(a.total)')
      .say('2:2예요. 두 객체 모두 클래스의 total 2를 읽어요.', 'output')
      .say('조심하세요. 객체로 대입하면 같은 이름의 객체 속성이 생겨 클래스 값을 가려요.', 'code:Counter.total += amount'))

c5 = ('class Rule:\n    def value(self):\n        return 2\nclass Bonus(Rule):\n    def value(self):\n'
      '        # 이 줄을 고쳐 상위 규칙의 결과에 extra를 더해 돌려주세요.\n        return extra\nextra = 3\nrule = Bonus()\nprint(rule.value())\n')
c5_sol = c5.replace('        return extra\n', '        # super().value()는 재정의하기 전 Rule의 value를 불러요.\n        return super().value() + extra\n')
d5 = (Script(c5)
      .say('Bonus의 value는 상위 규칙의 결과에 extra를 더해야 해요. super()로 Rule의 value를 불러요.', 'text:return 줄을 고쳐 상위 규칙의 결과에 extra를 더해 돌려주세요.')
      .run('print(rule.value())')
      .say('3이에요. 상위 규칙의 2를 쓰지 않고 extra만 돌려줬어요.', 'output')
      .patch('        return extra\n', '        return super().value() + extra\n', 'return 뒤를 super().value() + extra로 바꿔요.')
      .run('print(rule.value())')
      .say('5예요. Rule의 2에 extra 3을 더했어요.', 'output')
      .say('조심하세요. self.value()를 쓰면 Bonus가 자기 자신을 계속 불러 RecursionError가 나요.', 'code:super().value()'))

c6 = ('total = 2\nnew_total = 9\ndef change():\n    # 이 함수의 첫 줄에 global 선언을 더해 바깥 total을 바꾸게 하세요.\n    total = new_total\nchange()\nprint(total)\n')
c6_sol = c6.replace('    total = new_total\n', '    # global이 있으면 이 함수 안의 total은 바깥 이름이에요. 없으면 지역 이름이 새로 생겨요.\n    global total\n    total = new_total\n')
d6 = (Script(c6)
      .say('함수 안의 대입이 바깥 total을 바꿔야 해요. 함수 첫 줄에 global total을 더해요.', 'text:함수의 첫 줄에 global 선언을 더해 바깥 total을 바꾸게 하세요.')
      .run('print(total)')
      .say('2예요. 함수 안의 total은 지역 이름이라 바깥 total은 그대로예요.', 'output')
      .patch('    total = new_total\n', '    global total\n    total = new_total\n', '대입 앞에 global total을 써요.')
      .run('print(total)')
      .say('9예요. 함수 안의 대입이 바깥 total을 바꿨어요.', 'output')
      .say('조심하세요. global 없이 같은 이름에 대입하면 오류 없이 지역 이름만 생겨요. 결과로 확인해요.', 'code:global total'))

c7 = ('value = -1\ndef process(value):\n    try:\n        print("A", end="")\n        if value == 0:\n            return\n        if value < 0:\n            raise ValueError("bad")\n'
      '        print("B", end="")\n        # 이 F 출력을 finally 블록으로 옮겨 예외나 return이 있어도 실행되게 하세요.\n        print("F", end="")\n'
      '    except ValueError:\n        print("C", end="")\nprocess(value)\nprint("D")\n')
c7_sol = c7.replace('        print("B", end="")\n        # 이 F 출력을 finally 블록으로 옮겨 예외나 return이 있어도 실행되게 하세요.\n        print("F", end="")\n    except ValueError:\n        print("C", end="")\n',
                    '        print("B", end="")\n    except ValueError:\n        print("C", end="")\n'
                    '    # finally는 예외가 나도, try에서 return해도 마지막에 반드시 실행돼요.\n    finally:\n        print("F", end="")\n')
d7 = (Script(c7)
      .say('F는 예외가 나도, 중간에 return해도 꼭 출력돼야 해요. try 끝의 F 출력을 finally 블록으로 옮겨요.', 'text:F 출력을 finally 블록으로 옮겨 예외나 return이 있어도 실행되게 하세요.')
      .run('process(value)', 'print("D")')
      .say('ACD예요. A 다음 예외가 나서 try의 나머지 B와 F를 건너뛰었어요.', 'output')
      .patch('        print("F", end="")\n    except ValueError:\n        print("C", end="")\n',
             '    except ValueError:\n        print("C", end="")\n    finally:\n        print("F", end="")\n', 'F 출력을 지우고 except 뒤에 finally 블록을 만들어요.')
      .run('process(value)', 'print("D")')
      .say('ACFD예요. except 다음에 finally의 F가 실행됐어요.', 'output')
      .say('조심하세요. F를 try 블록 바깥 아래에 그냥 두면 value가 0일 때처럼 return하면 실행되지 않아요.', 'code:finally:'))

c8 = ('def multiply(n):\n    if n <= 1:\n        return 1\n    # 이 줄을 고쳐 n과 multiply(n - 1)의 결과를 곱해 돌려주세요.\n    return n\nnumber = 4\nprint(multiply(number))\n')
c8_sol = c8.replace('    return n\n', '    # 한 단계 작은 문제의 답을 돌려받아 n을 곱해요. n이 1 이하가 되면 멈춰요.\n    return n * multiply(n - 1)\n')
d8 = (Script(c8)
      .say('작은 문제의 답을 돌려받아 곱해야 해요. n과 multiply(n - 1)을 곱해 돌려줘요.', 'text:return n 줄을 고쳐 n과 multiply(n - 1)의 결과를 곱해 돌려주세요.')
      .run('print(multiply(number))')
      .say('4예요. 작은 문제를 부르지 않고 n만 돌려줬어요.', 'output')
      .patch('    return n\n', '    return n * multiply(n - 1)\n', 'return n 뒤에 * multiply(n - 1)을 더해요.')
      .run('print(multiply(number))')
      .say('24예요. 4 × 3 × 2 × 1을 돌아오면서 곱했어요.', 'output')
      .say('조심하세요. n * (n - 1)처럼 한 번만 곱하면 12에서 멈춰요. 작은 문제의 답을 다시 불러야 해요.', 'code:n * multiply(n - 1)'))

c9 = ('def label(count, price):\n    return str(count) + ":" + str(price)\ncount = 2\nprice = 4\n'
      '# 이 줄을 고쳐 키워드 인수로 price에는 price를, count에는 count를 연결하세요. price를 먼저 써요.\nprint(label(price, count))\n')
c9_sol = c9.replace('print(label(price, count))\n', '# 키워드 인수는 위치가 아니라 이름으로 매개변수에 연결돼요. 순서가 바뀌어도 맞게 들어가요.\nprint(label(price=price, count=count))\n')
d9 = (Script(c9)
      .say('price를 먼저 넘겨도 count와 price가 맞게 들어가야 해요. 이름으로 연결하는 키워드 인수를 써요.', 'text:print 줄을 고쳐 키워드 인수로 price에는 price를, count에는 count를 연결하세요.')
      .run('print(label(')
      .say('4:2예요. 위치대로 연결돼 price가 count 자리에 들어갔어요.', 'output')
      .patch('print(label(price, count))\n', 'print(label(price=price, count=count))\n', '각 인수 앞에 price=, count=을 붙여요.')
      .run('print(label(')
      .say('2:4예요. 이름으로 연결해 순서와 상관없이 맞게 들어갔어요.', 'output')
      .say('조심하세요. 키워드 인수를 쓴 뒤에 위치 인수를 쓰면 SyntaxError예요. 위치 인수가 먼저예요.', 'code:price=price'))

c10 = ('# 이 정의를 고쳐 넘긴 인수를 개수와 상관없이 stocks 하나에 묶어 받으세요.\ndef total(stocks):\n    result = 0\n    for stock in stocks:\n'
       '        # 양수인 재고만 합계에 포함해요.\n        if stock > 0:\n            result += stock\n    return result\nfirst = 2\nsecond = -1\nthird = 3\nprint(total(first, second, third))\n')
c10_sol = c10.replace('def total(stocks):\n', '# 별표가 붙은 매개변수는 넘긴 인수를 모두 튜플 하나로 묶어 받아요.\ndef total(*stocks):\n')
d10 = (Script(c10)
      .say('인수 세 개를 넘겨요. 매개변수 앞에 별표를 붙여 개수와 상관없이 하나로 묶어 받아야 해요.', 'text:정의를 고쳐 넘긴 인수를 개수와 상관없이 stocks 하나에 묶어 받으세요.')
      .run('print(total(', error='TypeError')
      .say('TypeError예요. 매개변수는 하나인데 인수를 세 개 넘겼어요.', 'output')
      .patch('def total(stocks):\n', 'def total(*stocks):\n', 'stocks 앞에 별표를 붙여요.')
      .run('print(total(')
      .say('5예요. 2, -1, 3을 튜플 하나로 받아 양수 2와 3만 더했어요.', 'output')
      .say('조심하세요. 별표 없이 total([2, -1, 3])처럼 목록 하나를 넘기는 호출과 섞으면 받는 방식이 달라져요.', 'code:*stocks'))

SPECS += [
    code_step('stp_5d9b8a77-c6a3-40dc-9f72-6e56d7b14a81', 'items.append(value)로 받은 목록 자체를 바꾸세요', '함수가 받은 목록을 수정하는 것과 매개변수에 새로 대입하는 것을 구별해요.',
              'items = items + [value]는 stocks를 바꾸지 못해 [2]다. items.append(value)로 고쳐 [2, 4]를 확인한다. 채점은 다른 목록과 값으로 실행한다.',
              '함수에 목록을 넘기면 매개변수 items가 같은 목록을 가리켜요. `items.append(값)`은 그 목록 자체를 바꾸고, `items = items + [값]`은 새 목록을 만들어 함수 안의 이름만 바꿔요.',
              'items 줄을 고쳐 받은 목록 자체에 value를 덧붙이세요. 채점은 다른 목록과 값으로도 실행해요.',
              [RUNC, '`items = items + [value]`를 `items.append(value)`로 고치세요.', '코드 실행을 눌러 [2, 4]가 나오는지 확인하세요.', SUBC],
              c3, c3_sol, d3, {d3.actions[-1]['text']: WC}, cases=[{'stocks': [], 'added': 7}, {'stocks': [1, 1], 'added': 0}],
              reject=[([['    items.append(value)\n', '    items = items + [value]\n']], 'Rebinding the parameter'), ([['print(stocks)\n', 'print([2, 4])\n']], 'Typing the list')],
              accept=[([['    items.append(value)\n', '    items += [value]\n']], '+= extends the same list')]),
    code_step('stp_c890127e-a892-498a-b22e-a688f1232e34', 'Counter.total로 클래스 속성을 늘리세요', '클래스 속성과 같은 이름의 객체 속성을 구별해요.',
              'a.total += amount는 a에만 속성을 만들어 2:0이다. Counter.total += amount로 고쳐 2:2를 확인한다. 채점은 다른 양으로 실행한다.',
              '`Counter.total`은 모든 객체가 함께 읽는 클래스 속성이에요. `a.total += 2`는 a에 같은 이름의 객체 속성을 새로 만들어 클래스 값을 가려요.',
              'a.total 줄을 고쳐 모든 객체가 함께 쓰는 클래스 속성 Counter.total을 amount만큼 늘리세요. 채점은 다른 양으로도 실행해요.',
              [RUNC, '`a.total += amount`를 `Counter.total += amount`로 고치세요.', '코드 실행을 눌러 2:2가 나오는지 확인하세요.', SUBC],
              c4, c4_sol, d4, {d4.actions[-1]['text']: WC}, cases=[{'amount': 5}, {'amount': -1}],
              reject=[([['Counter.total += amount\n', 'a.total += amount\n']], 'Instance attribute'), ([['Counter.total += amount\n', 'a.total = b.total = 2\n']], 'Typing both values')],
              accept=[([['Counter.total += amount\n', 'type(a).total += amount\n']], 'Through type(a)')]),
    code_step('stp_36b5babb-b0c9-4bc9-9d0c-7e6ec5f7b63a', 'super().value()로 상위 규칙의 결과를 이어 쓰세요', '재정의한 메서드 안에서 super()로 상위 메서드를 불러 결과를 확장해요.',
              'Bonus가 extra만 돌려주면 3이다. super().value() + extra로 고쳐 5를 확인한다. 채점은 다른 extra로 실행한다.',
              'Bonus는 Rule을 상속해 value를 다시 정의했어요. 변수 rule에는 Bonus 객체가 들어 있어서 Bonus의 value가 실행돼요. `super().value()`는 그 안에서 Rule의 원래 value를 불러요.',
              'return 줄을 고쳐 상위 규칙의 결과에 extra를 더해 돌려주세요. 채점은 다른 extra로도 실행해요.',
              [RUNC, '`return extra`를 `return super().value() + extra`로 고치세요.', '코드 실행을 눌러 5가 나오는지 확인하세요.', SUBC],
              c5, c5_sol, d5, {d5.actions[-1]['text']: WC}, cases=[{'extra': 0}, {'extra': -5}],
              reject=[([['        return super().value() + extra\n', '        return self.value() + extra\n']], 'Calling itself'), ([['        return super().value() + extra\n', '        return 5\n']], 'Typing the result')],
              accept=[([['        return super().value() + extra\n', '        return Rule.value(self) + extra\n']], 'Calling Rule.value directly')]),
    code_step('stp_6479b10b-4401-4386-96fc-f25fd8dbecaf', 'global total로 바깥 이름을 바꾸세요', '함수 안의 대입이 지역 이름을 만드는 것과 global로 바깥 이름을 바꾸는 것을 구별해요.',
              'global 없이 대입하면 바깥 total은 2 그대로다. global total을 더해 9를 확인한다. 채점은 다른 새 값으로 실행한다.',
              '함수 안에서 `total = 9`처럼 대입하면 그 함수의 지역 이름이 새로 생겨요. 함수 안에 `global total`이라고 적어야 바깥 이름을 바꿔요.',
              '함수의 첫 줄에 global 선언을 더해 바깥 total을 바꾸게 하세요. 채점은 다른 새 값으로도 실행해요.',
              [RUNC, '함수 안 대입 앞에 `global total`을 쓰세요.', '코드 실행을 눌러 9가 나오는지 확인하세요.', SUBC],
              c6, c6_sol, d6, {d6.actions[-1]['text']: WC}, cases=[{'new_total': 0}, {'total': 5, 'new_total': -3}],
              probe='assert total == new_total, "함수 안의 대입이 바깥 total을 바꿨는지 확인하세요."',
              reject=[([['    global total\n', '']], 'No global'), ([['    global total\n', ''], ['print(total)\n', 'print(new_total)\n']], 'Printing the new value without changing total')],
              accept=[([['def change():\n', 'def change():\n    """바깥 total을 바꿔요."""\n']], 'Docstring before global')]),
    code_step('stp_9123b419-c4e7-49fb-a405-b9b486dd4fca', 'F 출력을 finally로 옮겨 항상 실행되게 하세요', '예외로 건너뛴 줄과 except·finally가 실행되는 순서를 써서 확인해요.',
              'F가 try 끝에 있으면 예외 때 건너뛰어 ACD다. F를 finally로 옮겨 ACFD를 확인한다. 채점은 예외 없는 값과 중간에 return하는 값으로도 실행한다.',
              'try 안에서 예외가 나면 그 뒤 줄은 건너뛰고 except로 가요. finally는 예외가 있든 없든, try에서 return해도 마지막에 실행돼요. value가 음수면 A 다음에 예외가 나요.',
              'F 출력을 finally 블록으로 옮겨 예외나 return이 있어도 실행되게 하세요. 채점은 다른 value로도 실행해요.',
              [RUNC, 'try 끝의 `print("F", end="")`를 지우세요.', 'except 블록 뒤에 `finally:` 블록을 만들고 그 안에 `print("F", end="")`를 쓰세요.', '코드 실행을 눌러 ACFD가 나오는지 확인하세요.', SUBC],
              c7, c7_sol, d7, {d7.actions[-1]['text']: WC}, cases=[{'value': 3}, {'value': 0}],
              reject=[([['    finally:\n        print("F", end="")\n', '    print("F", end="")\n']], 'F after the try without finally'),
                      ([['print("D")\n', 'print("FD")\n']], 'Typing F')],
              accept=[([['    except ValueError:\n        print("C", end="")\n    # finally는 예외가 나도, try에서 return해도 마지막에 반드시 실행돼요.\n    finally:\n        print("F", end="")\n',
                         '    except ValueError as error:\n        print("C", end="")\n    finally:\n        print("F", end="")\n']], 'Naming the exception')]),
    code_step('stp_efe3749f-8240-4bae-8e68-56f475bda1b4', 'n * multiply(n - 1)로 작아지는 호출을 곱하세요', '재귀 호출이 작은 문제의 반환값을 받아 결과를 만드는 것을 써서 확인해요.',
              'return n은 4다. return n * multiply(n - 1)로 고쳐 24를 확인한다. 채점은 다른 n으로 실행한다.',
              '`multiply(n)`은 n이 1 이하면 1을 돌려주고, 아니면 n과 `multiply(n - 1)`의 결과를 곱해요. 한 단계 작은 문제의 답을 돌려받아 쓰는 재귀예요.',
              'return n 줄을 고쳐 n과 multiply(n - 1)의 결과를 곱해 돌려주세요. 채점은 다른 n으로도 실행해요.',
              [RUNC, '`return n`을 `return n * multiply(n - 1)`로 고치세요.', '코드 실행을 눌러 24가 나오는지 확인하세요.', SUBC],
              c8, c8_sol, d8, {d8.actions[-1]['text']: WC}, cases=[{'number': 1}, {'number': 5}],
              reject=[([['    return n * multiply(n - 1)\n', '    return n * (n - 1)\n']], 'One multiplication'), ([['print(multiply(number))\n', 'print(24)\n']], 'Typing the result')],
              accept=[([['    return n * multiply(n - 1)\n', '    smaller = multiply(n - 1)\n    return n * smaller\n']], 'Named smaller result')]),
    code_step('stp_f74284e4-e018-4672-9fd2-294676264541', 'price=와 count=로 키워드 인수를 연결하세요', '키워드 인수가 위치가 아니라 이름으로 매개변수에 연결되는 것을 써서 확인해요.',
              'label(price, count)는 위치대로 들어가 4:2다. label(price=price, count=count)로 고쳐 2:4를 확인한다. 채점은 다른 값으로 실행한다.',
              '`label(count, price)`는 이 순서로 정의했어요. `price=값`처럼 이름을 붙인 키워드 인수는 위치가 아니라 이름으로 매개변수에 연결돼요.',
              'print 줄을 고쳐 키워드 인수로 price에는 price를, count에는 count를 연결하세요. price를 먼저 써요. 채점은 다른 값으로도 실행해요.',
              [RUNC, '`label(price, count)`를 `label(price=price, count=count)`로 고치세요.', '코드 실행을 눌러 2:4가 나오는지 확인하세요.', SUBC],
              c9, c9_sol, d9, {d9.actions[-1]['text']: WC}, cases=[{'count': 7, 'price': 1}, {'count': 0, 'price': 0}],
              reject=[([['print(label(price=price, count=count))\n', 'print(label(price, count))\n']], 'Positional order'), ([['print(label(price=price, count=count))\n', 'print("2:4")\n']], 'Typing the label')],
              accept=[([['print(label(price=price, count=count))\n', 'print(label(count=count, price=price))\n']], 'Keywords in definition order')]),
    code_step('stp_0d4249ca-9eda-47f1-8660-998655ac7891', '*stocks로 여러 인수를 하나로 묶어 받으세요', '가변 인수가 넘긴 인수를 개수와 상관없이 튜플 하나로 묶는 것을 써서 확인해요.',
              '매개변수가 하나면 인수 세 개로 TypeError다. def total(*stocks)로 고쳐 양수만 더한 5를 확인한다. 채점은 다른 세 값으로 실행한다.',
              '`def total(*stocks)`의 별표는 넘긴 인수를 개수와 상관없이 튜플 하나로 묶어 stocks에 담아요. 함수는 반복하며 양수만 더해요.',
              '정의를 고쳐 넘긴 인수를 개수와 상관없이 stocks 하나에 묶어 받으세요. 채점은 다른 값으로도 실행해요.',
              ['코드 실행을 눌러 TypeError가 나오는지 확인하세요.', '`def total(stocks):`를 `def total(*stocks):`로 고치세요.', '코드 실행을 눌러 5가 나오는지 확인하세요.', SUBC],
              c10, c10_sol, d10, {d10.actions[-1]['text']: WC}, cases=[{'first': -4, 'second': 6, 'third': 1}, {'first': 0, 'second': 0, 'third': 0}],
              reject=[([['def total(*stocks):\n', 'def total(stocks):\n']], 'One parameter'), ([['print(total(first, second, third))\n', 'print(5)\n']], 'Typing the total')],
              accept=[([['    result = 0\n    for stock in stocks:\n        # 양수인 재고만 합계에 포함해요.\n        if stock > 0:\n            result += stock\n    return result\n',
                         '    return sum(stock for stock in stocks if stock > 0)\n']], 'sum over the positive values')]),
]

# 코드 흐름 보기 (src/python_trace.rs): steps about references, the call stack, objects and recursion.
CODE_FLOW_TITLES = {
    'record를 두 번 불러 기본 목록이 공유되는지 확인하세요',
    'items.append(value)로 받은 목록 자체를 바꾸세요',
    'Counter.total로 클래스 속성을 늘리세요',
    'super().value()로 상위 규칙의 결과를 이어 쓰세요',
    'n * multiply(n - 1)로 작아지는 호출을 곱하세요',
    '생략한 기록 목록은 호출마다 새로 만드세요',
}
for _spec in SPECS:
    if _spec['title'] in CODE_FLOW_TITLES:
        _spec['code_flow'] = True
