"""engineer-c-start: 1 answer-picking step -> coding step (2026-10-29)."""
from _kit import Script, todo

PRD_SCOPE = ['초기화한 int·현재 값 대입·간단한 덧셈·printf 정수 출력을 다뤄요.',
             '두 챕터·두 단원·여섯 스텝에서 같은 재고 표시를 점진적으로 바꿔요.',
             '변수 값 출력은 printf 한 줄을 직접 쓰고, 결과 직접 답안으로 저장 시점을 확인해요.']
PRD_GRADING = ['필수 문제를 직접 제출해 맞히면 성공이에요. 실행·해설 열람만으로 성공시키지 않아요.',
               '직접 쓰는 printf는 실제 C 컴파일러로 실행해 판정하고, 준비한 재고 값을 바꾼 실행도 맞아야 해요. 숫자나 이름을 글자로 적은 출력은 거절해요.',
               '결과 답안은 지정한 정수 두 개의 순서와 값을 확인해요. 앞뒤 공백과 수 사이의 연속 공백·줄바꿈만 정규화할 수 있어요. 숫자나 순서를 바꾸지는 않아요.',
               '해설 뒤 직접 풀어도 정상 성공이며 전후 열람은 상세의 작은 아이콘 정보예요.',
               '마지막 도전(stp_403cbc4b-4f0b-45f6-b4ba-8e4e237d2f5d): 시작 답안은 실패해야 해요. 실제 실행 결과 또는 각 서술형 답안 칸을 검사하고 오답과 동등한 정답도 대조해요.']

s = '''#include <stdio.h>
int main(void) {
    // 정수 재고를 stock이라는 이름에 저장해요.
    int stock = 2;
    // 이 주석 아래에 stock에 저장한 정수를 printf로 출력하세요.
    return 0;
}
'''
solution = s.replace('    // 이 주석 아래에 stock에 저장한 정수를 printf로 출력하세요.\n',
                     '    // 이 주석 아래에 stock에 저장한 정수를 printf로 출력하세요.\n'
                     '    // %d 자리에 stock 안의 정수가 들어가요. 따옴표 안에 이름을 쓰면 글자 stock이 나와요.\n'
                     '    printf("%d", stock);\n')
n = (Script(s)
     .say('stock에 저장한 정수를 출력하는 printf 한 줄을 써야 해요.', 'text:주석 아래에 stock에 저장한 정수를 printf로 출력하는 줄을 쓰세요.')
     .patch('    // 이 주석 아래에 stock에 저장한 정수를 printf로 출력하세요.\n',
            '    // 이 주석 아래에 stock에 저장한 정수를 printf로 출력하세요.\n    printf("%d", stock);\n',
            '형식 "%d" 뒤에 쉼표를 찍고 변수 stock을 넘겨요.')
     .run('printf("%d", stock);')
     .say('2예요. %d 자리에 stock 안의 정수 2가 들어갔어요.', 'output')
     .say('조심하세요. printf("stock")처럼 따옴표 안에 이름을 쓰면 값이 아니라 글자 stock이 나와요.', 'code:printf("%d", stock);'))

SPECS = [
    dict(old='stp_0bd93ffe-5c65-4e6b-9b6f-fc7e487f2980', title='stock에 저장한 정수를 printf로 출력하세요',
         objectives=['변수 이름이 아니라 변수에 저장한 값을 출력해요.'],
         core_flow='int stock=2를 printf("%d", stock)으로 출력해 2를 확인한다. 따옴표 안의 이름은 글자로 나온다. 채점은 stock의 처음 값을 바꿔 실행한다.',
         goal='stock은 재고 정수를 저장하는 이름이에요. `printf("%d", stock)`처럼 형식 문자열의 %d 자리에 변수를 넘기면 그 안에 저장한 정수가 출력돼요.\n\n'
              '주석 아래에 stock에 저장한 정수를 printf로 출력하는 줄을 쓰세요. 채점은 stock의 처음 값을 바꿔서도 실행해요.\n\n'
              + todo('주석 아래에 `printf("%d", stock);`를 쓰세요.', '코드 실행을 눌러 2가 나오는지 확인하세요.', '작성한 코드를 제출하세요.'),
         starter_code=s, solution=solution, tests=[{'input': '', 'expected': '2'}],
         variations=[{'values': {'stock': '5'}, 'expected': '5'}, {'values': {'stock': '0'}, 'expected': '0'}],
         narration=n.actions,
         review={'조심하세요. printf("stock")처럼 따옴표 안에 이름을 쓰면 값이 아니라 글자 stock이 나와요.': '실제 흔한 실수와 그 실제 출력을 말해요.'},
         reject=[([['    printf("%d", stock);\n', '    printf("2");\n']], 'Printing typed text'),
                 ([['    printf("%d", stock);\n', '    printf("stock");\n']], 'Printing the name')],
         accept=[([['    printf("%d", stock);\n', '    printf("%i", stock);\n']], '%i also prints an int')]),
]


# ---- 2026-10-30: the five code-reading answer fields become coding steps (user decision) ----------------
PRD_SCOPE = ['초기화한 int·현재 값 대입·간단한 덧셈·printf 정수 출력을 다뤄요.',
             '두 챕터·두 단원·일곱 스텝에서 같은 재고 표시를 점진적으로 바꿔요.',
             '모든 스텝에서 printf 인수·대입·복사·계산·줄 순서를 한 곳씩 직접 써서 실제 C로 실행해요.']
PRD_GRADING = ['필수 문제를 직접 제출해 맞히면 성공이에요. 실행·해설만으로 성공시키지 않아요.',
               '직접 쓴 코드는 실제 C 컴파일러로 실행해 판정하고, 준비한 재고 값을 바꾼 실행도 맞아야 해요. 숫자를 글자로 적은 출력, 대입·복사 시점이 다른 코드는 거절해요.',
               '해설 뒤 직접 풀어도 정상 성공이며 전후 열람은 상세의 작은 아이콘 정보예요.',
               '마지막 도전(stp_403cbc4b-4f0b-45f6-b4ba-8e4e237d2f5d): 시작 답안은 실패해야 해요. 실제 실행 결과 또는 각 서술형 답안 칸을 검사하고 오답과 동등한 정답도 대조해요.']
PRD_NARRATION = ['준비 코드를 먼저 실행하고 한 줄을 고친 뒤 다시 실행해요. 고친 줄과 출력을 차례로 짚어요.',
                 '값 대신 이름을 넣는 실수, 복사·계산 시점, 줄 순서를 실제 출력으로 비교해요.']

MAIN = '#include <stdio.h>\n\nint main(void) {\n'

f1 = MAIN + '''    // 오늘 들어온 상자 수예요.
    int count = 4;
    // 이 줄을 고쳐 정수 2 대신 count의 값이 %d 자리에 들어가게 하세요.
    printf("%d", 2);
    return 0;
}
'''
f1_sol = f1.replace('    printf("%d", 2);\n', '    // %d 자리에는 쉼표 뒤에 넘긴 값이 들어가요. 변수를 넘기면 그 안의 정수가 나와요.\n    printf("%d", count);\n')
m1 = (Script(f1)
      .say('printf는 쉼표 뒤에 넘긴 값을 %d 자리에 넣어요. 2 대신 count를 넘겨야 해요.', 'text:printf 줄을 고쳐 정수 2 대신 count의 값이 %d 자리에 들어가게 하세요.')
      .run('printf("%d", 2);')
      .say('2예요. 상자 수와 상관없이 적어 둔 2가 그대로 나왔어요.', 'output')
      .patch('printf("%d", 2);', 'printf("%d", count);', '2를 count로 바꿔요.')
      .run('printf("%d", count);')
      .say('4예요. count에 저장한 상자 수가 %d 자리에 들어갔어요.', 'output')
      .say('조심하세요. printf("4")처럼 숫자를 글자로 적으면 상자 수가 바뀌어도 4만 나와요.', 'code:printf("%d", count);'))

f3 = MAIN + '''    // 처음 재고는 2예요.
    int stock = 2;
    // 다시 센 재고예요.
    int counted = 5;
    // 이 주석 아래에 stock의 현재 값을 counted로 정정하는 대입문을 쓰세요.
    printf("%d", stock);
    return 0;
}
'''
f3_sol = f3.replace('    // 이 주석 아래에 stock의 현재 값을 counted로 정정하는 대입문을 쓰세요.\n',
                    '    // 이 주석 아래에 stock의 현재 값을 counted로 정정하는 대입문을 쓰세요.\n'
                    '    // 이미 있는 변수에 대입하면 예전 값은 사라지고 새 값만 남아요. int를 다시 쓰지 않아요.\n'
                    '    stock = counted;\n')
m3 = (Script(f3)
      .say('재고를 다시 셌어요. stock에 counted를 대입해 현재 값을 정정해야 해요.', 'text:주석 아래에 stock의 현재 값을 counted로 정정하는 대입문을 쓰세요.')
      .run('printf("%d", stock);')
      .say('2예요. 아직 정정하지 않아 처음 값이 그대로예요.', 'output')
      .patch('    printf("%d", stock);\n', '    stock = counted;\n    printf("%d", stock);\n', 'printf 앞에 stock = counted;를 써요.')
      .run('printf("%d", stock);')
      .say('5예요. 대입한 뒤에는 stock에 새 값 5만 남았어요.', 'output')
      .say('조심하세요. int stock = counted;처럼 int를 다시 쓰면 같은 이름을 두 번 선언해 컴파일 오류가 나요.', 'code:stock = counted;'))

TAIL = '''    // stock, shown 순서로 두 값을 표시해요.
    printf("%d %d", stock, shown);
    return 0;
}
'''
f4 = MAIN + '''    // 처음 재고와 다시 센 재고예요.
    int stock = 2;
    int counted = 5;
    // 이 줄을 고쳐 정정하기 전 stock의 값을 shown에 복사하세요.
    int shown = 0;
    stock = counted;
''' + TAIL
f4_sol = f4.replace('    int shown = 0;\n', '    // 대입은 그 순간의 값을 복사해요. 나중에 stock이 바뀌어도 shown은 그대로예요.\n    int shown = stock;\n')
m4 = (Script(f4)
      .say('정정하기 전 재고를 표시용으로 남겨 두려 해요. shown에 그때의 stock을 복사해야 해요.', 'text:shown 줄을 고쳐 정정하기 전 stock의 값을 shown에 복사하세요.')
      .run('printf("%d %d", stock, shown);')
      .say('5 0이에요. shown에 아직 아무것도 복사하지 않았어요.', 'output')
      .patch('    int shown = 0;\n', '    int shown = stock;\n', '0을 stock으로 바꿔요.')
      .run('printf("%d %d", stock, shown);')
      .say('5 2예요. shown은 복사한 순간의 2를 그대로 갖고 있어요.', 'output')
      .say('조심하세요. 복사는 이름을 연결하지 않아요. stock을 정정해도 shown은 따라 바뀌지 않아요.', 'code:int shown = stock;'))

f5 = MAIN + '''    // 처음 재고와 다시 센 재고예요.
    int stock = 2;
    int counted = 5;
    // 이 줄을 고쳐 정정하기 전 stock보다 하나 큰 값을 shown에 저장하세요.
    int shown = stock;
    stock = counted;
''' + TAIL
f5_sol = f5.replace('    int shown = stock;\n', '    // 계산 결과가 저장돼요. 식이 stock과 계속 연결되지 않아요.\n    int shown = stock + 1;\n')
m5 = (Script(f5)
      .say('표시값은 정정하기 전 재고보다 하나 커야 해요. shown에 stock + 1을 저장해야 해요.', 'text:shown 줄을 고쳐 정정하기 전 stock보다 하나 큰 값을 shown에 저장하세요.')
      .run('printf("%d %d", stock, shown);')
      .say('5 2예요. 지금은 재고를 그대로 복사했어요.', 'output')
      .patch('    int shown = stock;\n', '    int shown = stock + 1;\n', '끝에 + 1을 더해요.')
      .run('printf("%d %d", stock, shown);')
      .say('5 3이에요. 계산한 순간의 재고 2에 1을 더한 3이 저장됐어요.', 'output')
      .say('조심하세요. shown이 정정한 재고 5를 따라 6이 되지는 않아요. 저장한 건 식이 아니라 계산 결과예요.', 'code:int shown = stock + 1;'))

f6 = MAIN + '''    // 처음 재고와 다시 센 재고예요.
    int stock = 2;
    int counted = 5;
    // 아래 두 줄의 순서를 바꿔 정정한 재고보다 하나 큰 값을 shown에 저장하세요.
    int shown = stock + 1;
    stock = counted;
''' + TAIL
f6_sol = f6.replace('    int shown = stock + 1;\n    stock = counted;\n',
                    '    // 먼저 정정해야 다음 줄의 계산이 정정한 재고를 읽어요.\n    stock = counted;\n    int shown = stock + 1;\n')
m6 = (Script(f6)
      .say('이번에는 표시값이 정정한 재고보다 하나 커야 해요. 계산과 정정 줄의 순서를 바꿔야 해요.', 'text:아래 두 줄의 순서를 바꿔 정정한 재고보다 하나 큰 값을 shown에 저장하세요.')
      .run('printf("%d %d", stock, shown);')
      .say('5 3이에요. 정정하기 전의 2로 계산했어요.', 'output')
      .patch('    int shown = stock + 1;\n    stock = counted;\n', '    stock = counted;\n    int shown = stock + 1;\n', '정정 줄을 계산 줄 위로 올려요.')
      .run('printf("%d %d", stock, shown);')
      .say('5 6이에요. 정정한 5를 읽고 1을 더했어요.', 'output')
      .say('조심하세요. C는 위에서 아래로 한 줄씩 실행해요. 같은 두 줄도 순서가 바뀌면 결과가 달라요.', 'code:int shown = stock + 1;'))

RUN1 = '코드 실행을 눌러 지금 출력을 확인하세요.'
SUBMIT_C = '수정한 코드를 제출하세요.'
SPECS += [
    dict(old='stp_fe05535f-5efc-4f80-ab7b-e9d362efb915', title='printf에 count를 넘겨 상자 수를 출력하세요',
         objectives=['printf의 %d 자리에 쉼표 뒤에 넘긴 값이 들어가는 것을 써서 확인해요.'],
         core_flow='printf("%d", 2)는 언제나 2를 출력한다. 2를 count로 바꿔 count의 값 4를 출력한다. 채점은 count의 처음 값을 바꿔 실행한다.',
         goal='printf의 형식 문자열 "%d"는 정수가 들어갈 자리예요. 쉼표 뒤에 넘긴 값이 그 자리에 들어가요.\n\n'
              'printf 줄을 고쳐 정수 2 대신 count의 값이 %d 자리에 들어가게 하세요. 채점은 count의 처음 값을 바꿔서도 실행해요.\n\n'
              + todo(RUN1, '`printf("%d", 2);`의 2를 `count`로 고치세요.', '코드 실행을 눌러 4가 나오는지 확인하세요.', SUBMIT_C),
         starter_code=f1, solution=f1_sol, tests=[{'input': '', 'expected': '4'}],
         variations=[{'values': {'count': '7'}, 'expected': '7'}, {'values': {'count': '0'}, 'expected': '0'}],
         narration=m1.actions,
         review={m1.actions[-1]['text']: '실제 흔한 실수와 그 결과를 말해요.'},
         reject=[([['    printf("%d", count);\n', '    printf("4");\n']], 'Typing the number'),
                 ([['    printf("%d", count);\n', '    printf("%d", 4);\n']], 'Literal 4')],
         accept=[([['    printf("%d", count);\n', '    printf("%i", count);\n']], '%i also prints an int')]),
    dict(old='stp_d16d5e3a-f90d-4a2d-a072-ec9e4353ae23', title='stock = counted로 재고를 정정하세요',
         objectives=['이미 있는 변수에 대입하면 현재 값이 새 값으로 바뀌는 것을 써서 확인해요.'],
         core_flow='대입 전 printf는 처음 값 2다. printf 앞에 stock = counted;를 써서 5를 확인한다. 채점은 두 값을 바꿔 실행한다.',
         goal='재고를 다시 셌더니 counted였어요. 이미 선언한 변수에 `=`로 대입하면 예전 값은 사라지고 새 값만 남아요.\n\n'
              '주석 아래에 stock의 현재 값을 counted로 정정하는 대입문을 쓰세요. 채점은 처음 재고와 다시 센 재고를 바꿔서도 실행해요.\n\n'
              + todo(RUN1, '주석 아래에 `stock = counted;`를 쓰세요.', '코드 실행을 눌러 5가 나오는지 확인하세요.', SUBMIT_C),
         starter_code=f3, solution=f3_sol, tests=[{'input': '', 'expected': '5'}],
         variations=[{'values': {'stock': '9', 'counted': '1'}, 'expected': '1'}, {'values': {'counted': '12'}, 'expected': '12'}],
         narration=m3.actions,
         review={m3.actions[-1]['text']: '실제 컴파일 오류가 나는 흔한 실수예요.'},
         reject=[([['    stock = counted;\n', '    stock = 5;\n']], 'Typing the number'),
                 ([['    stock = counted;\n', '    counted = stock;\n']], 'Assigning the other way')],
         accept=[([['    stock = counted;\n', '    stock = 0 + counted;\n']], 'Same value through an expression')]),
    dict(old='stp_fcc5537b-0955-41e8-84e1-03543f28afef', title='int shown = stock으로 정정 전 재고를 복사하세요',
         objectives=['대입은 그 순간의 값을 복사하며 원본이 바뀌어도 복사본은 그대로임을 써서 확인해요.'],
         core_flow='shown = 0이면 5 0이다. int shown = stock으로 고쳐 정정 전 2가 남는 5 2를 확인한다. 채점은 두 값을 바꿔 실행한다.',
         goal='정정하기 전 재고를 표시용 shown에 남겨 두려 해요. `int shown = stock;`은 그 순간 stock의 값을 복사해요.\n\n'
              'shown 줄을 고쳐 정정하기 전 stock의 값을 shown에 복사하세요. 채점은 처음 재고와 다시 센 재고를 바꿔서도 실행해요.\n\n'
              + todo(RUN1, '`int shown = 0;`을 `int shown = stock;`으로 고치세요.', '코드 실행을 눌러 5 2가 나오는지 확인하세요.', SUBMIT_C),
         starter_code=f4, solution=f4_sol, tests=[{'input': '', 'expected': '5 2'}],
         variations=[{'values': {'stock': '7', 'counted': '3'}, 'expected': '3 7'}, {'values': {'stock': '0', 'counted': '8'}, 'expected': '8 0'}],
         narration=m4.actions,
         review={m4.actions[-1]['text']: '복사 시점의 흔한 오해를 실제 출력과 함께 말해요.'},
         reject=[([['    int shown = stock;\n', '    int shown = 2;\n']], 'Typing the old value'),
                 ([['    int shown = stock;\n    stock = counted;\n', '    stock = counted;\n    int shown = stock;\n']], 'Copying after the correction')],
         accept=[([['    int shown = stock;\n', '    int shown;\n    shown = stock;\n']], 'Declare, then assign')]),
    dict(old='stp_b6835e5e-2fa2-4a4f-b196-51b286940636', title='int shown = stock + 1로 그때의 계산값을 저장하세요',
         objectives=['계산식의 결과가 그 순간 저장되고 식이 원본과 계속 연결되지 않음을 써서 확인해요.'],
         core_flow='복사만 하면 5 2다. int shown = stock + 1로 고쳐 계산 순간의 2에 1을 더한 5 3을 확인한다. 채점은 두 값을 바꿔 실행한다.',
         goal='표시값은 정정하기 전 재고보다 하나 커야 해요. `int shown = stock + 1;`은 그 순간 계산한 결과를 저장해요.\n\n'
              'shown 줄을 고쳐 정정하기 전 stock보다 하나 큰 값을 shown에 저장하세요. 채점은 처음 재고와 다시 센 재고를 바꿔서도 실행해요.\n\n'
              + todo(RUN1, '`int shown = stock;` 끝에 `+ 1`을 더하세요.', '코드 실행을 눌러 5 3이 나오는지 확인하세요.', SUBMIT_C),
         starter_code=f5, solution=f5_sol, tests=[{'input': '', 'expected': '5 3'}],
         variations=[{'values': {'stock': '7', 'counted': '3'}, 'expected': '3 8'}, {'values': {'stock': '-1', 'counted': '4'}, 'expected': '4 0'}],
         narration=m5.actions,
         review={m5.actions[-1]['text']: '저장 시점의 흔한 오해를 실제 출력과 함께 말해요.'},
         reject=[([['    int shown = stock + 1;\n', '    int shown = 3;\n']], 'Typing the value'),
                 ([['    int shown = stock + 1;\n', '    int shown = counted + 1;\n']], 'Using the corrected stock')],
         accept=[([['    int shown = stock + 1;\n', '    int shown = 1 + stock;\n']], 'Operands swapped')]),
    dict(old='stp_e1a10053-efd4-42c3-b133-55bcb9cb2563', title='두 줄의 순서를 바꿔 정정한 재고로 계산하세요',
         objectives=['같은 줄도 실행 순서가 바뀌면 결과가 달라지는 것을 써서 확인해요.'],
         core_flow='계산 줄이 정정 줄보다 위면 5 3이다. 정정 줄을 위로 올려 정정한 5에 1을 더한 5 6을 확인한다. 채점은 두 값을 바꿔 실행한다.',
         goal='이번에는 표시값이 정정한 재고보다 하나 커야 해요. C는 위에서 아래로 한 줄씩 실행하므로 줄의 순서가 결과를 정해요.\n\n'
              '아래 두 줄의 순서를 바꿔 정정한 재고보다 하나 큰 값을 shown에 저장하세요. 채점은 처음 재고와 다시 센 재고를 바꿔서도 실행해요.\n\n'
              + todo(RUN1, '`stock = counted;` 줄을 `int shown = stock + 1;` 줄 위로 옮기세요.', '코드 실행을 눌러 5 6이 나오는지 확인하세요.', SUBMIT_C),
         starter_code=f6, solution=f6_sol, tests=[{'input': '', 'expected': '5 6'}],
         variations=[{'values': {'stock': '7', 'counted': '3'}, 'expected': '3 4'}, {'values': {'counted': '0'}, 'expected': '0 1'}],
         narration=m6.actions,
         review={m6.actions[-1]['text']: '실행 순서의 실제 결과 차이를 말해요.'},
         reject=[([['    stock = counted;\n    int shown = stock + 1;\n', '    int shown = stock + 1;\n    stock = counted;\n']], 'Original order'),
                 ([['    int shown = stock + 1;\n', '    int shown = 6;\n']], 'Typing the value')],
         accept=[([['    int shown = stock + 1;\n', '    int shown = counted + 1;\n']], 'Same value from counted after the correction')]),
]
