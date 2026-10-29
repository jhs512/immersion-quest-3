"""engineer-c-double-pointers: 7 answer-picking steps -> coding steps (2026-10-29)."""
from _kit import Script, todo

PRD_SCOPE = ['두 챕터·두 단원·아홉 스텝으로 같은 재고를 다뤄요.',
             '이중 간접 읽기와 쓰기·한 층 주소 바꾸기·바깥 포인터 옮기기·호출자 포인터 변경·포인터 배열을 한 줄씩 직접 써서 실행해요.']
PRD_GRADING = ['직접 쓴 코드를 실제 C 컴파일러로 실행해 판정해요.',
               '값·주소를 바꾸는 층과 다른 시작 값, 다른 대상을 가리키게 바꾼 실행을 실제 검사해서 이름으로 직접 읽거나 숫자를 적은 우회를 거절해요.',
               '마지막 도전(stp_91b12cbe-e1be-4225-a7da-ff05510ff2a4): 시작 답안은 실패해야 해요. 실제 실행 결과 또는 각 서술형 답안 칸을 검사하고 오답과 동등한 정답도 대조해요.']
PRD_NARRATION = ['같은 관계를 한 단계씩 따라가며 그림과 실제 결과를 연결해요. 한 줄씩 고쳐 실행해요.',
                 '포인터 복사·주소 변경·배열 원소 타입·유효 범위를 조심할 지점으로 짚어요.']

INC = '#include <stdio.h>\n\n'
BASE = '''    int stock = 2;
    int other = 9;
    // p는 stock을, pp는 포인터 p가 있는 곳을 가리켜요.
    int *p = &stock;
    int **pp = &p;
'''

s1 = INC + 'int main(void) {\n' + BASE + '''    // 이 줄을 고쳐 pp에서 두 번 따라가 최종 값을 읽으세요.
    int value = 0;
    printf("%d", value);
    return 0;
}
'''
s1_solution = s1.replace('    int value = 0;\n', '    // *pp는 p, **pp는 p가 가리키는 stock이에요.\n    int value = **pp;\n')
n1 = (Script(s1)
      .say('pp에서 두 번 따라가 최종 값을 읽어 value에 담아야 해요.', 'text:value 줄을 고쳐 pp에서 두 번 따라가 최종 값을 읽으세요.')
      .run('printf("%d", value);')
      .say('0이에요. 아직 pp를 따라가지 않았어요.', 'output')
      .patch('    int value = 0;\n', '    int value = **pp;\n', '별표 두 개로 pp를 두 번 따라가요.')
      .run('printf("%d", value);')
      .say('2예요. pp에서 p로, p에서 stock으로 가서 읽었어요.', 'output')
      .say('조심하세요. *pp는 정수가 아니라 p에 담긴 주소예요. 정수 칸에 담으면 안 돼요.', 'code:int value = **pp;'))

s2 = INC + 'int main(void) {\n' + BASE + '''    int fresh = 5;
    // 이 주석 아래에 pp에서 두 번 따라가 최종 재고에 fresh를 쓰세요.
    printf("%d\\n%d", stock, other);
    return 0;
}
'''
s2_solution = s2.replace('    // 이 주석 아래에 pp에서 두 번 따라가 최종 재고에 fresh를 쓰세요.\n',
                         '    // 이 주석 아래에 pp에서 두 번 따라가 최종 재고에 fresh를 쓰세요.\n'
                         '    // **pp = ...는 p가 가리키는 변수의 값을 바꿔요. 주소는 그대로예요.\n'
                         '    **pp = fresh;\n')
n2 = (Script(s2)
      .say('pp에서 두 번 따라가 최종 재고에 fresh를 써야 해요.', 'text:주석 아래에 pp에서 두 번 따라가 최종 재고에 fresh를 쓰세요.')
      .run('printf("%d\\n%d", stock, other);')
      .say('2와 9예요. 아직 쓰지 않았어요.', 'output')
      .patch('    // 이 주석 아래에 pp에서 두 번 따라가 최종 재고에 fresh를 쓰세요.\n',
             '    // 이 주석 아래에 pp에서 두 번 따라가 최종 재고에 fresh를 쓰세요.\n    **pp = fresh;\n',
             '**pp에 fresh를 대입해요.')
      .run('printf("%d\\n%d", stock, other);')
      .say('5와 9예요. 최종 대상 stock의 값만 바뀌었어요.', 'output')
      .say('조심하세요. 별표 개수가 바꾸는 층을 정해요. **pp는 값, *pp는 p의 주소, pp는 pp 자신이에요.', 'code:**pp = fresh;'))

s3 = INC + 'int main(void) {\n' + BASE + '''    // 이 줄을 고쳐 stock은 그대로 두고 p가 other를 가리키게 하세요.
    **pp = other;
    printf("%d\\n%d", *p, stock);
    return 0;
}
'''
s3_solution = s3.replace('    **pp = other;\n', '    // *pp는 p 자신이에요. 여기에 주소를 쓰면 p가 가리키는 곳이 바뀌어요.\n    *pp = &other;\n')
n3 = (Script(s3)
      .say('지금 줄은 stock에 other의 값을 써요. 한 번만 따라가 p의 주소를 바꾸게 고쳐야 해요.', 'text:**pp = other; 줄을 고쳐 stock은 그대로 두고 p가 other를 가리키게 하세요.')
      .run('printf("%d\\n%d", *p, stock);')
      .say('9와 9예요. **pp = other가 stock을 9로 덮어썼어요.', 'output')
      .patch('    **pp = other;\n', '    *pp = &other;\n', '별표 하나로 p에 other의 주소를 써요.')
      .run('printf("%d\\n%d", *p, stock);')
      .say('9와 2예요. p가 other를 가리키고 stock은 2로 남았어요.', 'output')
      .say('조심하세요. *pp = &other와 **pp = other는 출력 첫 줄이 같아도 stock에 하는 일이 달라요.', 'code:*pp = &other;'))

s4 = INC + 'int main(void) {\n' + BASE + '''    // 별도 포인터 q는 다른 재고를 가리켜요.
    int *q = &other;
    // 이 줄을 고쳐 p는 그대로 두고 pp만 q가 있는 곳을 가리키게 하세요.
    *pp = q;
    printf("%d\\n%d", **pp, *p);
    return 0;
}
'''
s4_solution = s4.replace('    *pp = q;\n', '    // 별표 없이 pp에 대입하면 가장 바깥 포인터만 옮겨요. p는 그대로 stock을 가리켜요.\n    pp = &q;\n')
n4 = (Script(s4)
      .say('지금 줄은 p를 바꿔요. p는 두고 pp만 q가 있는 곳으로 옮겨야 해요.', 'text:*pp = q; 줄을 고쳐 p는 그대로 두고 pp만 q가 있는 곳을 가리키게 하세요.')
      .run('printf("%d\\n%d", **pp, *p);')
      .say('9와 9예요. *pp = q가 p를 other 쪽으로 바꿨어요.', 'output')
      .patch('    *pp = q;\n', '    pp = &q;\n', '별표를 빼고 pp에 q의 주소를 담아요.')
      .run('printf("%d\\n%d", **pp, *p);')
      .say('9와 2예요. pp는 q를 따라 other를 읽고, p는 그대로 stock을 가리켜요.', 'output')
      .say('조심하세요. pp를 옮겨도 p가 따라 바뀌지 않아요. 각 포인터는 따로 있는 변수예요.', 'code:pp = &q;'))

s5 = INC + '''// target은 호출자의 포인터 p가 있는 곳이에요.
void redirect(int **target, int *other) {
    // 이 주석 아래에 호출자의 포인터가 other를 가리키게 하는 줄을 쓰세요.
}

int main(void) {
    // p 자체가 있는 곳을 함수에 넘겨요.
    int stock = 2;
    int other = 7;
    int *p = &stock;
    redirect(&p, &other);
    printf("%d\\n%d", *p, stock);
    return 0;
}
'''
s5_solution = s5.replace('    // 이 주석 아래에 호출자의 포인터가 other를 가리키게 하는 줄을 쓰세요.\n',
                         '    // 이 주석 아래에 호출자의 포인터가 other를 가리키게 하는 줄을 쓰세요.\n'
                         '    // *target은 main의 p예요. 여기에 주소를 쓰면 main의 p가 바뀌어요.\n'
                         '    *target = other;\n')
n5 = (Script(s5)
      .say('redirect는 p가 있는 곳을 받았어요. 그 포인터가 other를 가리키게 써야 해요.', 'text:주석 아래에 호출자의 포인터가 other를 가리키게 하는 줄을 쓰세요.')
      .run('printf("%d\\n%d", *p, stock);')
      .say('2와 2예요. 함수가 아직 아무것도 바꾸지 않아요.', 'output')
      .patch('    // 이 주석 아래에 호출자의 포인터가 other를 가리키게 하는 줄을 쓰세요.\n',
             '    // 이 주석 아래에 호출자의 포인터가 other를 가리키게 하는 줄을 쓰세요.\n    *target = other;\n',
             '*target에 other를 대입해요.')
      .run('printf("%d\\n%d", *p, stock);')
      .say('7과 2예요. main의 p가 other를 가리키게 됐고 stock은 그대로예요.', 'output')
      .say('조심하세요. **target = *other로 쓰면 p는 그대로이고 stock이 7로 덮어써져요.', 'code:*target = other;'))

s6 = INC + '''int main(void) {
    // int* 값 두 개를 배열 원소로 담아요.
    int stock = 2;
    int other = 7;
    int *choices[] = {&stock, &other};
    // pp는 첫 번째 포인터 원소를 가리켜요.
    int **pp = choices;
    // 이 줄을 고쳐 pp에서 한 칸 뒤의 포인터 원소를 따라가 읽으세요.
    int value = **pp;
    printf("%d", value);
    return 0;
}
'''
s6_solution = s6.replace('    int value = **pp;\n', '    // pp + 1은 둘째 포인터 원소예요. 두 번 따라가면 그 원소가 가리키는 재고예요.\n    int value = **(pp + 1);\n')
n6 = (Script(s6)
      .say('pp는 포인터 배열의 첫 원소를 가리켜요. 한 칸 뒤의 포인터 원소를 따라가 읽어야 해요.', 'text:value 줄을 고쳐 pp에서 한 칸 뒤의 포인터 원소를 따라가 읽으세요.')
      .run('printf("%d", value);')
      .say('2예요. 첫 원소 &stock을 따라가 stock을 읽었어요.', 'output')
      .patch('    int value = **pp;\n', '    int value = **(pp + 1);\n', 'pp에 1을 더한 뒤 두 번 따라가요.')
      .run('printf("%d", value);')
      .say('7이에요. 둘째 원소 &other를 따라가 other를 읽었어요.', 'output')
      .say('조심하세요. **pp + 1은 stock에 1을 더한 3이에요. 괄호가 어느 층에서 움직일지 정해요.', 'code:int value = **(pp + 1);'))

s7 = INC + '''int main(void) {
    // p는 재고 배열의 첫 원소를 가리켜요.
    int bins[] = {2, 5, 7};
    int *p = bins;
    int **pp = &p;
    // 이 줄을 고쳐 *pp가 가진 배열 주소에서 한 원소 이동한 값을 읽으세요.
    int next = **pp;
    printf("%d", next);
    return 0;
}
'''
s7_solution = s7.replace('    int next = **pp;\n', '    // *pp는 p의 값(배열 주소)이에요. 거기서 한 원소 이동한 뒤 따라가요.\n    int next = *(*pp + 1);\n')
n7 = (Script(s7)
      .say('*pp는 p가 가진 배열 주소예요. 그 주소에서 한 원소 이동한 값을 읽어야 해요.', 'text:next 줄을 고쳐 *pp가 가진 배열 주소에서 한 원소 이동한 값을 읽으세요.')
      .run('printf("%d", next);')
      .say('2예요. **pp는 첫 원소예요.', 'output')
      .patch('    int next = **pp;\n', '    int next = *(*pp + 1);\n', '*pp에 1을 더한 주소를 따라가요.')
      .run('printf("%d", next);')
      .say('5예요. 배열 안에서 다음 원소로 이동했어요.', 'output')
      .say('조심하세요. **(pp + 1)은 배열이 아니라 pp 옆 메모리로 가서 정해진 결과가 없어요.', 'code:int next = *(*pp + 1);'))

SPECS = [
    dict(old='stp_53e610bf-edef-4a4c-b9b5-0df26de86266', title='**pp로 두 번 따라가 최종 값을 읽으세요',
         objectives=['이중 포인터를 두 번 역참조해 최종 대상의 값을 읽어요.'],
         core_flow='p=&stock, pp=&p에서 value=**pp로 2를 읽는다. 채점은 stock 값과 p가 가리키는 대상(other)을 바꿔 이름으로 읽는 우회를 거절한다.',
         goal='pp는 포인터 p가 있는 곳을 가리켜요. `*pp`는 p, `**pp`는 p가 가리키는 stock이에요.\n\n'
              'value 줄을 고쳐 pp에서 두 번 따라가 최종 값을 읽으세요. 채점은 p가 다른 재고를 가리키게 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 0이 나오는지 확인하세요.', '`int value = 0;`의 0을 `**pp`로 바꾸세요.', '코드 실행을 눌러 2가 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s1, solution=s1_solution, tests=[{'input': '', 'expected': '2'}],
         variations=[{'values': {'p': '&other'}, 'expected': '9'}, {'values': {'stock': '6'}, 'expected': '6'}],
         narration=n1.actions,
         review={'조심하세요. *pp는 정수가 아니라 p에 담긴 주소예요. 정수 칸에 담으면 안 돼요.': '실제 C 타입(int*)과 흔한 실수를 정확히 말해요.'},
         reject=[([['    int value = **pp;\n', '    int value = stock;\n']], 'Reading the name directly'),
                 ([['    int value = **pp;\n', '    int value = 2;\n']], 'Typing the value')],
         accept=[([['    int value = **pp;\n', '    int value = *p;\n']], 'p is *pp')]),
    dict(old='stp_f3513a6f-ab32-4393-adc3-5efcb3d6acd6', title='**pp에 fresh를 써서 최종 재고를 바꾸세요',
         objectives=['이중 간접 대입이 최종 대상의 값을 바꿈을 확인해요.'],
         core_flow='**pp = fresh로 stock을 5로 바꾸고 other는 9로 남는다. 채점은 fresh와 p의 대상을 바꿔 이름으로 쓰는 우회를 거절한다.',
         goal='`**pp = 값`은 pp에서 두 번 따라간 최종 대상, 곧 p가 가리키는 변수에 값을 써요. 주소들은 그대로예요.\n\n'
              '주석 아래에 pp에서 두 번 따라가 최종 재고에 fresh를 쓰세요. 채점은 fresh와 p가 가리키는 대상을 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 2와 9가 나오는지 확인하세요.', '주석 아래에 `**pp = fresh;`를 쓰세요.', '코드 실행을 눌러 5와 9가 나오는지 확인하세요.', '작성한 코드를 제출하세요.'),
         starter_code=s2, solution=s2_solution, tests=[{'input': '', 'expected': '5\n9'}],
         variations=[{'values': {'fresh': '8'}, 'expected': '8\n9'}, {'values': {'p': '&other'}, 'expected': '2\n5'}],
         narration=n2.actions,
         review={'조심하세요. 별표 개수가 바꾸는 층을 정해요. **pp는 값, *pp는 p의 주소, pp는 pp 자신이에요.': '실제 C 의미를 층별로 정확히 말해요.'},
         reject=[([['    **pp = fresh;\n', '    stock = fresh;\n']], 'Writing the name directly'),
                 ([['    **pp = fresh;\n', '    **pp = 5;\n']], 'Typing the value')],
         accept=[([['    **pp = fresh;\n', '    *p = fresh;\n']], 'p is *pp')]),
    dict(old='stp_e19cf6be-f01b-4d94-bb33-305d266b7e47', title='*pp에 주소를 써서 p가 other를 가리키게 하세요',
         objectives=['한 번 따라가 포인터의 대상을 바꾸는 것과 값을 바꾸는 것을 구별해요.'],
         core_flow='**pp = other는 stock을 덮어써 9,9다. *pp = &other로 고쳐 9,2를 확인한다. 채점은 other와 stock을 바꿔 실행한다.',
         goal='`*pp`는 포인터 p 자신이에요. 여기에 주소를 쓰면 p가 가리키는 곳이 바뀌어요. 지금 줄은 두 번 따라가 stock의 값을 덮어써요.\n\n'
              '`**pp = other;` 줄을 고쳐 stock은 그대로 두고 p가 other를 가리키게 하세요. 채점은 두 재고 값을 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 9와 9가 나오는지 확인하세요.', '`**pp = other;`를 *pp에 other의 주소를 쓰는 줄로 고치세요.', '코드 실행을 눌러 9와 2가 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s3, solution=s3_solution, tests=[{'input': '', 'expected': '9\n2'}],
         variations=[{'values': {'other': '4'}, 'expected': '4\n2'}, {'values': {'stock': '6'}, 'expected': '9\n6'}],
         narration=n3.actions,
         review={'조심하세요. *pp = &other와 **pp = other는 출력 첫 줄이 같아도 stock에 하는 일이 달라요.': '실제 두 실행 결과(9,2와 9,9)로 확인되는 대조예요.'},
         reject=[([['    *pp = &other;\n', '    **pp = other;\n']], 'Overwriting stock')],
         accept=[([['    *pp = &other;\n', '    p = &other;\n']], 'Writing p directly')]),
    dict(old='stp_777a745f-1ba0-4952-976c-7b133c14e3e4', title='p는 두고 pp만 q가 있는 곳을 가리키게 하세요',
         objectives=['가장 바깥 포인터를 옮기는 것과 안쪽 포인터를 바꾸는 것을 구별해요.'],
         core_flow='*pp = q는 p를 other 쪽으로 바꿔 9,9다. pp = &q로 고쳐 **pp는 9, *p는 2를 확인한다. 채점은 other와 stock을 바꿔 실행한다.',
         goal='별도 포인터 q는 다른 재고 other를 가리켜요. 지금 `*pp = q;`는 pp가 가리키는 p를 바꿔요. 별표 없이 `pp = 주소`로 쓰면 가장 바깥 포인터 pp만 옮겨요.\n\n'
              '`*pp = q;` 줄을 고쳐 p는 그대로 두고 pp만 q가 있는 곳을 가리키게 하세요. 채점은 두 재고 값을 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 9와 9가 나오는지 확인하세요.', '`*pp = q;`를 pp에 q의 주소를 담는 줄로 고치세요.', '코드 실행을 눌러 9와 2가 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s4, solution=s4_solution, tests=[{'input': '', 'expected': '9\n2'}],
         variations=[{'values': {'other': '4'}, 'expected': '4\n2'}, {'values': {'stock': '6'}, 'expected': '9\n6'}],
         narration=n4.actions,
         review={'조심하세요. pp를 옮겨도 p가 따라 바뀌지 않아요. 각 포인터는 따로 있는 변수예요.': '실제 C 의미와 실제 출력 *p=2를 정확히 말해요.'},
         reject=[([['    pp = &q;\n', '    *pp = q;\n']], 'Changing p')],
         accept=[([['    pp = &q;\n', '    int **moved = &q;\n    pp = moved;\n']], 'Through another double pointer')]),
    dict(old='stp_acf409e5-adc2-480d-8c6b-d74bd61f5403', title='*target에 써서 호출자의 포인터를 바꾸세요',
         objectives=['포인터의 주소를 넘겨 함수에서 호출자의 포인터를 바꿔요.'],
         core_flow='redirect(&p, &other)는 p가 있는 곳을 넘긴다. 함수 안에 *target = other를 써서 *p가 7, stock이 2임을 확인한다. 채점은 other와 stock을 바꿔 실행한다.',
         goal='이번에는 p가 있는 곳 `&p`를 넘겼어요. 함수 안의 `*target`은 main의 p 자신이라서, 여기에 주소를 쓰면 main의 p가 바뀌어요.\n\n'
              'redirect 안의 주석 아래에 호출자의 포인터가 other를 가리키게 하는 줄을 쓰세요. 채점은 두 재고 값을 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 2와 2가 나오는지 확인하세요.', '주석 아래에 `*target = other;`를 쓰세요.', '코드 실행을 눌러 7과 2가 나오는지 확인하세요.', '작성한 코드를 제출하세요.'),
         starter_code=s5, solution=s5_solution, tests=[{'input': '', 'expected': '7\n2'}],
         variations=[{'values': {'other': '4'}, 'expected': '4\n2'}, {'values': {'stock': '9'}, 'expected': '7\n9'}],
         narration=n5.actions,
         review={'조심하세요. **target = *other로 쓰면 p는 그대로이고 stock이 7로 덮어써져요.': '실제 흔한 실수와 그 실제 결과(7,7)를 말해요.'},
         reject=[([['    *target = other;\n', '    **target = *other;\n']], 'Overwriting stock instead of redirecting')],
         accept=[([['    *target = other;\n', '    int *next = other;\n    *target = next;\n']], 'Through a local pointer')]),
    dict(old='stp_29b58424-c1dc-44bc-b60f-3af03b8feb0c', title='pp에서 한 칸 뒤 포인터 원소를 따라가 읽으세요',
         objectives=['포인터 배열의 원소 타입과 이중 포인터 이동을 연결해요.'],
         core_flow='choices={&stock, &other}, pp=choices에서 **pp는 2다. **(pp + 1)로 고쳐 7을 읽는다. 채점은 배열 순서와 other를 바꿔 실행한다.',
         goal='포인터 두 개를 배열 choices에 담았어요. 원소 하나하나가 int*라서 그 배열을 가리키는 pp는 int**예요. `pp + 1`은 둘째 포인터 원소예요.\n\n'
              'value 줄을 고쳐 pp에서 한 칸 뒤의 포인터 원소를 따라가 읽으세요. 채점은 배열 순서와 재고 값을 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 2가 나오는지 확인하세요.', '`**pp`를 `**(pp + 1)`로 고치세요.', '코드 실행을 눌러 7이 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s6, solution=s6_solution, tests=[{'input': '', 'expected': '7'}],
         variations=[{'values': {'choices': '{&other, &stock}'}, 'expected': '2'}, {'values': {'other': '4'}, 'expected': '4'}],
         narration=n6.actions,
         review={'조심하세요. **pp + 1은 stock에 1을 더한 3이에요. 괄호가 어느 층에서 움직일지 정해요.': '실제 연산자 우선순위와 실제 값을 말해요.'},
         reject=[([['    int value = **(pp + 1);\n', '    int value = **pp + 1;\n']], 'Adding to the value'),
                 ([['    int value = **(pp + 1);\n', '    int value = other;\n']], 'Reading the name directly')],
         accept=[([['    int value = **(pp + 1);\n', '    int value = *pp[1];\n']], 'Index then dereference')]),
    dict(old='stp_96c98942-dbab-4d57-a084-b7ff7744f904', title='*(*pp + 1)로 배열 안 다음 원소를 읽으세요',
         objectives=['이중 포인터에서 어느 층의 주소를 옮기는지 구별해요.'],
         core_flow='p=bins, pp=&p에서 **pp는 2다. *(*pp + 1)로 고쳐 5를 읽는다. **(pp + 1)은 배열 밖이다. 채점은 bins와 p의 시작 위치를 바꿔 실행한다.',
         goal='p는 재고 배열의 첫 원소를 가리키고 pp는 p를 가리켜요. `*pp`는 p의 값, 곧 배열 주소예요. 그 주소에서 한 원소 이동하면 배열의 다음 칸이에요.\n\n'
              'next 줄을 고쳐 *pp가 가진 배열 주소에서 한 원소 이동한 값을 읽으세요. 채점은 배열 값과 p의 시작 위치를 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 2가 나오는지 확인하세요.', '`**pp`를 `*(*pp + 1)`로 고치세요.', '코드 실행을 눌러 5가 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s7, solution=s7_solution, tests=[{'input': '', 'expected': '5'}],
         variations=[{'values': {'bins': '{1, 8, 3}'}, 'expected': '8'}, {'values': {'p': 'bins + 1'}, 'expected': '7'}],
         narration=n7.actions,
         review={'조심하세요. **(pp + 1)은 배열이 아니라 pp 옆 메모리로 가서 정해진 결과가 없어요.': '실제 C 규칙(유효 범위 밖 접근은 정의되지 않은 동작)을 정확히 말해요.'},
         reject=[([['    int next = *(*pp + 1);\n', '    int next = **pp + 1;\n']], 'Adding to the value'),
                 ([['    int next = *(*pp + 1);\n', '    int next = bins[1];\n']], 'Ignoring where p starts')],
         accept=[([['    int next = *(*pp + 1);\n', '    int next = (*pp)[1];\n']], 'Index on *pp')]),
]
