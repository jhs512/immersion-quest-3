"""engineer-c-conditions: 7 answer-picking steps -> coding steps (2026-10-29)."""
from _kit import Script, todo

PRD_SCOPE = ['두 챕터·두 단원·아홉 스텝으로 같은 포장 상황을 이어 가요.',
             '몫·나머지·비교·if·else·0이 아닌 조건을 준비 코드의 한두 줄로 직접 써서 실행해요.']
PRD_GRADING = ['실행·해설만으로 성공하지 않아요. 직접 쓴 코드를 실제 C 컴파일러로 실행해 판정해요.',
               '재고와 묶음 크기를 경계 바로 전·동일·직후로 바꾼 실행도 맞아야 해서 고정 출력이나 우연한 정답을 구별해요.',
               '해설을 본 뒤 맞혀도 성공이며 전후 열람은 부가 정보로 구분해요.',
               '마지막 도전(stp_dc7e47b4-96cc-49e9-9865-af75a871cc94): 시작 답안은 실패해야 해요. 실제 실행 결과 또는 각 서술형 답안 칸을 검사하고 오답과 동등한 정답도 대조해요.']
PRD_NARRATION = ['준비 코드를 먼저 실행하고, 식이나 조건 한 곳을 써 넣은 뒤 다시 실행해요. 코드 줄·실행 버튼·결과를 차례로 짚어요.',
                 '틀리기 쉬운 경계나 대입과 비교의 차이를 실제 출력으로 비교하고 조심하세요 순간을 넣어요.',
                 '전체 답을 한 번에 갈아 끼우지 않아요. 음성은 준비한 뒤 화면과 맞춰요.']

HEAD = '#include <stdio.h>\nint main(void) {\n'

# ---- 1. 몫 ----------------------------------------------------------------------------
s1 = HEAD + '''    // 재고 일곱 개를 세 개씩 묶어요.
    int stock = 7;
    int group = 3;
    // 이 줄을 고쳐 완성한 묶음 수를 계산하세요.
    int packs = 0;
    printf("%d", packs);
    return 0;
}
'''
s1_solution = s1.replace('    int packs = 0;\n', '    // 정수끼리 나누면 소수점을 버린 몫만 남아요. 그 몫이 완성한 묶음 수예요.\n    int packs = stock / group;\n')
n1 = (Script(s1)
      .say('재고를 묶음 크기로 나눠 완성한 묶음 수를 계산해야 해요.', 'text:packs 줄을 고쳐 완성한 묶음 수를 계산하세요.')
      .run('printf("%d", packs);')
      .say('0이에요. packs에 아직 계산 없이 0을 넣었어요.', 'output')
      .patch('    int packs = 0;\n', '    int packs = stock / group;\n', 'stock을 group으로 나눈 값을 packs에 담아요.')
      .run('printf("%d", packs);')
      .say('2예요. 7을 3으로 나눈 몫 2만 남고 소수점은 버려졌어요.', 'output')
      .say('조심하세요. int끼리의 나눗셈은 반올림하지 않아요. 8 / 3도 2예요.', 'code:int packs = stock / group;'))

# ---- 2. 나머지 ------------------------------------------------------------------------
s2 = HEAD + '''    // 같은 재고를 같은 크기로 묶어요.
    int stock = 7;
    int group = 3;
    // 이 줄을 고쳐 묶고 남은 낱개 수를 계산하세요.
    int left = 0;
    printf("%d", left);
    return 0;
}
'''
s2_solution = s2.replace('    int left = 0;\n', '    // %는 나눈 뒤 남는 정수를 구해요. 묶고 남은 낱개 수예요.\n    int left = stock % group;\n')
n2 = (Script(s2)
      .say('묶고 남은 낱개 수를 % 연산으로 계산해야 해요.', 'text:left 줄을 고쳐 묶고 남은 낱개 수를 계산하세요.')
      .run('printf("%d", left);')
      .say('0이에요. 아직 계산하지 않았어요.', 'output')
      .patch('    int left = 0;\n', '    int left = stock % group;\n', 'stock을 group으로 나눈 나머지를 left에 담아요.')
      .run('printf("%d", left);')
      .say('1이에요. 7은 3씩 두 묶음이 되고 하나가 남아요.', 'output')
      .say('조심하세요. stock - group은 한 묶음만 뺀 4라서 남은 낱개가 아니에요.', 'code:int left = stock % group;'))

# ---- 3. 비교 결과 ---------------------------------------------------------------------
s3 = HEAD + '''    // 포장 한 묶음에 세 개가 필요해요.
    int stock = 3;
    int group = 3;
    // 이 줄을 고쳐 재고가 묶음 크기 이상인지 비교한 결과를 담으세요.
    int can = 0;
    printf("%d\\n", can);
    printf("%d", stock);
    return 0;
}
'''
s3_solution = s3.replace('    int can = 0;\n', '    // C의 비교는 맞으면 1, 틀리면 0이에요. 비교는 stock을 바꾸지 않아요.\n    int can = stock >= group;\n')
n3 = (Script(s3)
      .say('재고가 묶음 크기 이상인지 비교한 결과를 can에 담아야 해요.', 'text:can 줄을 고쳐 재고가 묶음 크기 이상인지 비교한 결과를 담으세요.')
      .run('printf("%d\\n", can);', 'printf("%d", stock);')
      .say('0과 3이에요. 아직 비교하지 않고 0을 넣었어요.', 'output')
      .patch('    int can = 0;\n', '    int can = stock >= group;\n', 'stock >= group 비교 결과를 can에 담아요.')
      .run('printf("%d\\n", can);', 'printf("%d", stock);')
      .say('1과 3이에요. 같아도 이상이라 비교가 맞아 1이고, 재고는 그대로 3이에요.', 'output')
      .say('조심하세요. stock = group은 비교가 아니라 대입이라 재고를 바꿔 버려요.', 'code:int can = stock >= group;'))

# ---- 4. if로 표시 켜기 ----------------------------------------------------------------
s4 = HEAD + '''    // 처음에는 포장 가능 표시를 꺼 두어요.
    int stock = 4;
    int group = 3;
    int ready = 0;
    // 이 주석 아래에 재고가 충분할 때만 ready를 1로 바꾸는 if 문을 쓰세요.
    printf("%d", ready);
    return 0;
}
'''
s4_solution = s4.replace('    // 이 주석 아래에 재고가 충분할 때만 ready를 1로 바꾸는 if 문을 쓰세요.\n',
                         '    // 이 주석 아래에 재고가 충분할 때만 ready를 1로 바꾸는 if 문을 쓰세요.\n'
                         '    // 조건이 맞을 때만 중괄호 안이 실행돼요. 모자라면 ready는 처음 값 0 그대로예요.\n'
                         '    if (stock >= group) {\n        ready = 1;\n    }\n')
n4 = (Script(s4)
      .say('재고가 충분할 때만 ready를 1로 바꾸는 if 문을 써야 해요.', 'text:주석 아래에 재고가 충분할 때만 ready를 1로 바꾸는 if 문을 쓰세요.')
      .run('printf("%d", ready);')
      .say('0이에요. 재고 4는 충분하지만 아직 표시를 켜는 코드가 없어요.', 'output')
      .patch('    // 이 주석 아래에 재고가 충분할 때만 ready를 1로 바꾸는 if 문을 쓰세요.\n',
             '    // 이 주석 아래에 재고가 충분할 때만 ready를 1로 바꾸는 if 문을 쓰세요.\n    if (stock >= group) {\n        ready = 1;\n    }\n',
             'stock >= group일 때만 ready에 1을 넣는 if 문을 써요.')
      .run('printf("%d", ready);')
      .say('1이에요. 조건이 맞아 중괄호 안의 대입이 실행됐어요.', 'output')
      .patch('    int stock = 4;\n', '    int stock = 2;\n', '재고를 2로 바꿔 볼게요.')
      .run('printf("%d", ready);')
      .say('0이에요. 조건이 틀려 중괄호 안을 건너뛰었어요.', 'output')
      .patch('    int stock = 2;\n', '    int stock = 4;\n', '재고를 처음 값 4로 되돌려요.')
      .say('조심하세요. if 없이 ready = 1만 쓰면 재고가 모자라도 표시가 켜져요.', 'code:ready = 1;'))

# ---- 5. else 경로 ---------------------------------------------------------------------
s5 = HEAD + '''    // 포장할 수 있으면 묶음 수를 표시해요.
    int stock = 2;
    int group = 3;
    int packs = -1;
    if (stock >= group) {
        packs = stock / group;
    }
    // 이 if 문 끝에 else를 이어 붙여 모자라면 packs를 0으로 정하세요.
    printf("%d", packs);
    return 0;
}
'''
s5_solution = s5.replace('        packs = stock / group;\n    }\n',
                         '        packs = stock / group;\n'
                         '    // else는 조건이 틀릴 때만 실행돼요. 두 경로 중 한쪽만 실행해요.\n'
                         '    } else {\n        packs = 0;\n    }\n')
n5 = (Script(s5)
      .say('재고가 모자랄 때의 경로를 else로 이어 붙여 packs를 0으로 정해야 해요.', 'text:if 문 끝에 else를 이어 붙여 모자라면 packs를 0으로 정하세요.')
      .run('printf("%d", packs);')
      .say('-1이에요. 재고 2는 모자라서 if 안을 건너뛰었고 packs는 처음 값 그대로예요.', 'output')
      .patch('        packs = stock / group;\n    }\n', '        packs = stock / group;\n    } else {\n        packs = 0;\n    }\n',
             'if의 닫는 중괄호 뒤에 else를 붙이고 packs에 0을 넣어요.')
      .run('printf("%d", packs);')
      .say('0이에요. 조건이 틀려서 else 쪽만 실행됐어요.', 'output')
      .say('조심하세요. else 없이 packs = 0을 if 아래에 쓰면 포장할 수 있을 때도 0으로 덮어써요.', 'code:packs = 0;'))

# ---- 6. 0이 아닌 값은 참 ---------------------------------------------------------------
s6 = HEAD + '''    // C의 조건은 0인지 아닌지를 봐요.
    int stock = 2;
    int ready = 0;
    // 이 주석 아래에 stock 자체를 조건으로 써서 재고가 있으면 ready를 1로 바꾸세요.
    printf("%d", ready);
    return 0;
}
'''
s6_solution = s6.replace('    // 이 주석 아래에 stock 자체를 조건으로 써서 재고가 있으면 ready를 1로 바꾸세요.\n',
                         '    // 이 주석 아래에 stock 자체를 조건으로 써서 재고가 있으면 ready를 1로 바꾸세요.\n'
                         '    // 0이 아닌 값은 참이에요. stock이 2여도 ready에는 1을 넣어요.\n'
                         '    if (stock) {\n        ready = 1;\n    }\n')
n6 = (Script(s6)
      .say('비교식 없이 stock 자체를 조건으로 써서 재고가 있으면 ready를 1로 바꿔야 해요.', 'text:주석 아래에 stock 자체를 조건으로 써서 재고가 있으면 ready를 1로 바꾸세요.')
      .run('printf("%d", ready);')
      .say('0이에요. 아직 조건문이 없어요.', 'output')
      .patch('    // 이 주석 아래에 stock 자체를 조건으로 써서 재고가 있으면 ready를 1로 바꾸세요.\n',
             '    // 이 주석 아래에 stock 자체를 조건으로 써서 재고가 있으면 ready를 1로 바꾸세요.\n    if (stock) {\n        ready = 1;\n    }\n',
             '괄호 안에 stock만 쓰고 ready에 1을 넣어요.')
      .run('printf("%d", ready);')
      .say('1이에요. stock 2는 0이 아니라서 조건이 참이었어요.', 'output')
      .say('조심하세요. ready = stock으로 쓰면 1이 아니라 재고 2가 표시돼요.', 'code:ready = 1;'))

# ---- 7. 더 필요한 낱개 -----------------------------------------------------------------
s7 = HEAD + '''    // 재고 일곱 개를 세 개씩 나눠요.
    int stock = 7;
    int group = 3;
    int packs = stock / group;
    int left = stock % group;
    int display;
    if (left == 0) {
        display = 0;
    } else {
        // 이 줄을 고쳐 한 묶음을 더 채우는 데 필요한 개수를 담으세요.
        display = left;
    }
    printf("%d\\n", packs);
    printf("%d", display);
    return 0;
}
'''
s7_solution = s7.replace('        display = left;\n', '        // 한 묶음은 group개예요. 이미 left개가 있으니 group - left개가 더 필요해요.\n        display = group - left;\n')
n7 = (Script(s7)
      .say('남은 낱개가 아니라 한 묶음을 채우는 데 더 필요한 개수를 담아야 해요.', 'text:else 안의 display 줄을 고쳐 한 묶음을 더 채우는 데 필요한 개수를 담으세요.')
      .run('printf("%d\\n", packs);', 'printf("%d", display);')
      .say('2와 1이에요. 둘째 줄은 남은 낱개 1이라 아직 필요한 개수가 아니에요.', 'output')
      .patch('        display = left;\n', '        display = group - left;\n', '묶음 크기에서 남은 낱개를 빼요.')
      .run('printf("%d\\n", packs);', 'printf("%d", display);')
      .say('2와 2예요. 낱개 1개에 2개를 더하면 세 개 한 묶음이 돼요.', 'output')
      .say('조심하세요. if (left = 0)처럼 =를 하나만 쓰면 비교가 아니라 left에 0을 넣어요.', 'code:if (left == 0) {'))

SPECS = [
    dict(old='stp_c4e8d8ac-c06d-4386-879c-043eb8de84b6', title='재고를 묶음 크기로 나눠 완성한 묶음 수를 계산하세요',
         objectives=['정수 나눗셈의 몫을 완성한 묶음 수로 읽어요.'],
         core_flow='stock=7, group=3에서 packs=stock/group으로 2를 확인한다. 정수 나눗셈은 소수점을 버린다. 채점은 stock과 group을 바꿔 실행한다.',
         goal='재고 일곱 개를 세 개씩 묶어요. int끼리 나누면 소수점 아래를 버린 몫만 남고, 그 몫이 완성한 묶음 수예요.\n\n'
              'packs 줄을 고쳐 완성한 묶음 수를 계산하세요. 채점은 재고와 묶음 크기를 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 0이 나오는지 확인하세요.', '`int packs = 0;`의 0을 stock을 group으로 나누는 식으로 바꾸세요.', '코드 실행을 눌러 2가 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s1, solution=s1_solution, tests=[{'input': '', 'expected': '2'}],
         variations=[{'values': {'stock': '9'}, 'expected': '3'}, {'values': {'stock': '8'}, 'expected': '2'}, {'values': {'stock': '2'}, 'expected': '0'}, {'values': {'group': '7'}, 'expected': '1'}],
         narration=n1.actions,
         review={'조심하세요. int끼리의 나눗셈은 반올림하지 않아요. 8 / 3도 2예요.': '실제 C 정수 나눗셈 규칙(0 쪽 버림)과 확인 가능한 예를 말해요.'},
         reject=[([['    int packs = stock / group;\n', '    int packs = 2;\n']], 'Typing the value'),
                 ([['    int packs = stock / group;\n', '    int packs = stock % group;\n']], 'Remainder instead of quotient')],
         accept=[([['    int packs = stock / group;\n', '    int packs = (stock - stock % group) / group;\n']], 'Removing the remainder first')]),
    dict(old='stp_46043d03-defc-4cb0-8b73-7b72557fa324', title='% 연산으로 묶고 남은 낱개 수를 계산하세요',
         objectives=['나머지 연산으로 묶고 남은 낱개를 구해요.'],
         core_flow='stock=7, group=3에서 left=stock%group으로 1을 확인한다. stock-group은 4라 다르다. 채점은 stock과 group을 바꿔 실행한다.',
         goal='이번에는 묶고 남은 낱개를 구해요. `%`는 나눈 뒤 남는 정수를 구하는 연산이에요.\n\n'
              'left 줄을 고쳐 묶고 남은 낱개 수를 계산하세요. 채점은 재고와 묶음 크기를 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 0이 나오는지 확인하세요.', '`int left = 0;`의 0을 stock을 group으로 나눈 나머지로 바꾸세요.', '코드 실행을 눌러 1이 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s2, solution=s2_solution, tests=[{'input': '', 'expected': '1'}],
         variations=[{'values': {'stock': '9'}, 'expected': '0'}, {'values': {'stock': '8'}, 'expected': '2'}, {'values': {'group': '4'}, 'expected': '3'}],
         narration=n2.actions,
         review={'조심하세요. stock - group은 한 묶음만 뺀 4라서 남은 낱개가 아니에요.': '실제 흔한 혼동과 그 실제 값(4)을 말해요.'},
         reject=[([['    int left = stock % group;\n', '    int left = 1;\n']], 'Typing the value'),
                 ([['    int left = stock % group;\n', '    int left = stock - group;\n']], 'Subtracting one group')],
         accept=[([['    int left = stock % group;\n', '    int left = stock - stock / group * group;\n']], 'Subtracting the full groups')]),
    dict(old='stp_069db997-de6d-4199-9d81-a8c9950fd454', title='재고가 묶음 크기 이상인지 비교한 결과를 담으세요',
         objectives=['비교 결과가 1 또는 0이고 원래 값을 바꾸지 않음을 확인해요.'],
         core_flow='stock=3, group=3에서 can=stock>=group은 1이고 stock은 3 그대로다. 대입 =는 값을 바꾼다. 채점은 stock을 2, 5로 바꿔 0과 1을 모두 확인한다.',
         goal='포장 한 묶음에 세 개가 필요해요. C에서 비교식은 맞으면 1, 틀리면 0이 되고, 비교한다고 원래 재고가 바뀌지는 않아요.\n\n'
              'can 줄을 고쳐 재고가 묶음 크기 이상인지 비교한 결과를 담으세요. 채점은 재고를 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 0과 3이 나오는지 확인하세요.', '`int can = 0;`의 0을 stock이 group 이상인지 비교하는 식으로 바꾸세요.', '코드 실행을 눌러 1과 3이 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s3, solution=s3_solution, tests=[{'input': '', 'expected': '1\n3'}],
         variations=[{'values': {'stock': '2'}, 'expected': '0\n2'}, {'values': {'stock': '5'}, 'expected': '1\n5'}],
         narration=n3.actions,
         review={'1과 3이에요. 같아도 이상이라 비교가 맞아 1이고, 재고는 그대로 3이에요.': '「같아도」는 >= 경계(3 >= 3)를 실제 출력과 맞게 말해요.', '조심하세요. stock = group은 비교가 아니라 대입이라 재고를 바꿔 버려요.': '실제 C 흔한 실수(대입/비교 혼동)와 그 결과를 말해요.'},
         reject=[([['    int can = stock >= group;\n', '    int can = stock == group;\n']], 'Only equal counts'),
                 ([['    int can = stock >= group;\n', '    int can = 1;\n']], 'Typing the value'),
                 ([['    int can = stock >= group;\n', '    int can = stock > group;\n']], 'Excluding the boundary')],
         accept=[([['    int can = stock >= group;\n', '    int can = !(stock < group);\n']], 'Negating less-than')]),
    dict(old='stp_7c65a811-0d76-4f47-9fc6-ae7c0d61cd55', title='재고가 충분할 때만 ready를 1로 바꾸는 if 문을 쓰세요',
         objectives=['조건이 맞을 때만 대입을 실행하는 if 문을 써요.'],
         core_flow='ready=0에서 시작한다. if (stock >= group) { ready = 1; }를 써서 stock=4면 1, stock=2로 바꾸면 0을 확인한다. 채점은 stock을 경계 2, 3과 4로 바꿔 실행한다.',
         goal='처음에는 포장 가능 표시 ready를 0으로 꺼 두어요. if 문은 괄호 안 조건이 맞을 때만 중괄호 안을 실행해요.\n\n'
              '주석 아래에 재고가 충분할 때만 ready를 1로 바꾸는 if 문을 쓰세요. 채점은 재고를 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 0이 나오는지 확인하세요.', '주석 아래에 `stock >= group`일 때 ready를 1로 바꾸는 if 문을 쓰세요.', '코드 실행을 눌러 1이 나오는지 확인하세요.', '작성한 코드를 제출하세요.'),
         starter_code=s4, solution=s4_solution, tests=[{'input': '', 'expected': '1'}],
         variations=[{'values': {'stock': '2'}, 'expected': '0'}, {'values': {'stock': '3'}, 'expected': '1'}],
         narration=n4.actions,
         review={'조심하세요. if 없이 ready = 1만 쓰면 재고가 모자라도 표시가 켜져요.': '실제 우회와 그 결과(재고 2 채점 실패)를 말해요.'},
         reject=[([['    if (stock >= group) {\n        ready = 1;\n    }\n', '    ready = 1;\n']], 'Always on'),
                 ([['    if (stock >= group) {\n', '    if (stock > group) {\n']], 'Excluding the boundary')],
         accept=[([['    if (stock >= group) {\n        ready = 1;\n    }\n', '    if (group <= stock) ready = 1;\n']], 'Without braces, operands swapped')]),
    dict(old='stp_19dabbcd-b9ea-4d37-8abe-bfc0777939fb', title='else를 이어 붙여 재고가 모자라면 packs를 0으로 정하세요',
         objectives=['if와 else 중 조건에 따라 한쪽만 실행됨을 써서 확인해요.'],
         core_flow='packs=-1에서 if (stock >= group)만 있어 stock=2면 -1이 남는다. else { packs = 0; }를 붙여 0을 확인한다. 채점은 stock을 7, 3, 0으로 바꿔 if 경로와 else 경로를 모두 확인한다.',
         goal='포장할 수 있으면 묶음 수를 packs에 담아요. 지금은 모자랄 때의 경로가 없어서 packs가 처음 값 -1로 남아요. else는 if 조건이 틀릴 때만 실행돼요.\n\n'
              'if 문 끝에 else를 이어 붙여 모자라면 packs를 0으로 정하세요. 채점은 재고를 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 -1이 나오는지 확인하세요.', 'if의 닫는 중괄호 뒤에 `else`와 packs를 0으로 정하는 중괄호를 쓰세요.', '코드 실행을 눌러 0이 나오는지 확인하세요.', '작성한 코드를 제출하세요.'),
         starter_code=s5, solution=s5_solution, tests=[{'input': '', 'expected': '0'}],
         variations=[{'values': {'stock': '7'}, 'expected': '2'}, {'values': {'stock': '3'}, 'expected': '1'}, {'values': {'stock': '0'}, 'expected': '0'}],
         narration=n5.actions,
         review={'조심하세요. else 없이 packs = 0을 if 아래에 쓰면 포장할 수 있을 때도 0으로 덮어써요.': '실제 흔한 실수와 그 결과(재고 7 채점 실패)를 말해요.'},
         reject=[([['    } else {\n        packs = 0;\n    }\n', '    }\n    packs = 0;\n']], 'Overwriting after the if'),
                 ([['    } else {\n        packs = 0;\n    }\n', '    }\n    printf("0");\n    return 0;\n']], 'Printing a typed zero')],
         accept=[([['    } else {\n        packs = 0;\n    }\n', '    }\n    if (stock < group) {\n        packs = 0;\n    }\n']], 'A second if with the opposite condition')]),
    dict(old='stp_7f5d67c1-1b32-44ec-b6f3-7a6640f7978f', title='stock 자체를 조건으로 써서 재고가 있으면 ready를 1로 바꾸세요',
         objectives=['C 조건이 0이 아닌 값을 참으로 보는 것을 써서 확인해요.'],
         core_flow='if (stock) { ready = 1; }로 stock=2면 1이다. 0이 아닌 값은 참이고 ready에는 stock이 아니라 1이 들어간다. 채점은 stock을 0과 5로 바꿔 실행한다.',
         goal='C의 조건은 값이 0인지 아닌지를 봐요. 0이면 거짓, 0이 아닌 값은 모두 참이에요. 그래서 `if (stock)`은 재고가 0이 아닐 때 실행돼요.\n\n'
              '주석 아래에 stock 자체를 조건으로 써서 재고가 있으면 ready를 1로 바꾸세요. 채점은 재고를 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 0이 나오는지 확인하세요.', '주석 아래에 `if (stock)`과 ready를 1로 바꾸는 중괄호를 쓰세요.', '코드 실행을 눌러 1이 나오는지 확인하세요.', '작성한 코드를 제출하세요.'),
         starter_code=s6, solution=s6_solution, tests=[{'input': '', 'expected': '1'}],
         variations=[{'values': {'stock': '0'}, 'expected': '0'}, {'values': {'stock': '5'}, 'expected': '1'}],
         narration=n6.actions,
         review={'조심하세요. ready = stock으로 쓰면 1이 아니라 재고 2가 표시돼요.': '실제 흔한 혼동(참 = 값 그대로)과 그 실제 출력을 말해요.'},
         reject=[([['    if (stock) {\n        ready = 1;\n    }\n', '    ready = stock;\n']], 'Copying the stock'),
                 ([['    if (stock) {\n        ready = 1;\n    }\n', '    ready = 1;\n']], 'Always on')],
         accept=[([['    if (stock) {\n', '    if (stock != 0) {\n']], 'Explicit not-zero comparison')]),
    dict(old='stp_855eb259-cf79-4e88-a396-c239b00608db', title='한 묶음을 더 채우는 데 필요한 낱개 수를 계산하세요',
         objectives=['몫·나머지와 == 비교를 이어 완성 묶음과 부족한 개수를 계산해요.'],
         core_flow='packs=stock/group, left=stock%group이다. left==0이면 0, 아니면 display를 group-left로 고쳐 2와 2를 확인한다. 채점은 stock과 group을 바꿔 남지 않는 경우와 남는 경우를 확인한다.',
         goal='완성한 묶음과, 남은 낱개로 한 묶음을 더 채우려면 몇 개가 더 필요한지 표시해요. `==`는 두 값이 같은지 비교하고, 하나짜리 `=`는 대입이에요. 지금 else 쪽은 남은 낱개를 그대로 표시해요.\n\n'
              'else 안의 display 줄을 고쳐 한 묶음을 더 채우는 데 필요한 개수를 담으세요. 채점은 재고와 묶음 크기를 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 2와 1이 나오는지 확인하세요.', '`display = left;`를 묶음 크기에서 남은 낱개를 빼는 식으로 고치세요.', '코드 실행을 눌러 2와 2가 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s7, solution=s7_solution, tests=[{'input': '', 'expected': '2\n2'}],
         variations=[{'values': {'stock': '9'}, 'expected': '3\n0'}, {'values': {'stock': '8'}, 'expected': '2\n1'}, {'values': {'group': '4'}, 'expected': '1\n1'}],
         narration=n7.actions,
         review={'조심하세요. if (left = 0)처럼 =를 하나만 쓰면 비교가 아니라 left에 0을 넣어요.': '실제 C 흔한 실수와 그 동작을 정확히 말해요.'},
         reject=[([['        display = group - left;\n', '        display = 2;\n']], 'Typing the value'),
                 ([['        display = group - left;\n', '        display = left;\n']], 'Showing the leftover')],
         accept=[([['        display = group - left;\n', '        display = (packs + 1) * group - stock;\n']], 'Next full count minus stock')]),
]
