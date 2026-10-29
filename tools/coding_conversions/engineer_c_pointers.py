"""engineer-c-pointers: 9 answer-picking steps -> coding steps (2026-10-29)."""
from _kit import Script, todo

PRD_SCOPE = ['두 챕터·두 단원·열한 스텝으로 같은 창고 재고를 다뤄요.',
             '주소와 대상·별칭·대상 옮기기·배열 이동·함수 인자·널 확인을 한두 줄씩 직접 써서 실행해요.']
PRD_GRADING = ['직접 쓴 코드를 실제 C 컴파일러로 실행해 판정해요.',
               '작은 준비 값 여러 개와 포인터가 가리키는 대상을 바꾼 실행에서 원래 대상의 변화를 검사해요. 이름으로 직접 읽거나 숫자를 적은 우회는 거절해요.',
               '주소 문자열이나 정의되지 않은 실행 결과는 정답으로 쓰지 않아요.',
               '마지막 도전(stp_72d91c6d-4814-4b28-90c8-92f78ba9f667): 시작 답안은 실패해야 해요. 실제 실행 결과 또는 각 서술형 답안 칸을 검사하고 오답과 동등한 정답도 대조해요.']
PRD_NARRATION = ['가리키는 관계를 작은 그림으로 설명하고 한 줄씩 써 넣어 실행해요.',
                 '포인터 이동과 대상 변경·값 복사·널 역참조를 조심할 지점으로 짚어요.']

INC = '#include <stdio.h>\n\n'

s1 = INC + '''int main(void) {
    int stock = 2;
    int other = 9;
    // p에는 stock이 있는 곳(주소)을 담아요.
    int *p = &stock;
    // 이 줄을 고쳐 p가 가리키는 값을 읽어 담으세요.
    int value = 0;
    printf("%d", value);
    return 0;
}
'''
s1_solution = s1.replace('    int value = 0;\n', '    // *p는 p에 담긴 주소로 가서 그곳의 값을 읽어요.\n    int value = *p;\n')
n1 = (Script(s1)
      .say('p가 가리키는 값을 *p로 읽어 value에 담아야 해요.', 'text:value 줄을 고쳐 p가 가리키는 값을 읽어 담으세요.')
      .run('printf("%d", value);')
      .say('0이에요. 아직 p를 따라가 읽지 않았어요.', 'output')
      .patch('    int value = 0;\n', '    int value = *p;\n', 'p 앞에 별표를 붙여 가리키는 값을 읽어요.')
      .run('printf("%d", value);')
      .say('2예요. p가 가리키는 stock의 값이에요.', 'output')
      .say('조심하세요. value = stock으로 쓰면 지금은 같아도 p가 other를 가리키면 틀려요.', 'code:int value = *p;'))

s2 = INC + '''int main(void) {
    int stock = 2;
    int other = 9;
    int fresh = 5;
    // 원래 재고의 위치를 가리켜요.
    int *p = &stock;
    // 이 주석 아래에 p가 가리키는 곳에 fresh를 쓰는 줄을 쓰세요.
    printf("%d\\n%d", stock, other);
    return 0;
}
'''
s2_solution = s2.replace('    // 이 주석 아래에 p가 가리키는 곳에 fresh를 쓰는 줄을 쓰세요.\n',
                         '    // 이 주석 아래에 p가 가리키는 곳에 fresh를 쓰는 줄을 쓰세요.\n'
                         '    // *p = ...는 p가 가리키는 변수에 값을 써요. 지금은 stock이에요.\n'
                         '    *p = fresh;\n')
n2 = (Script(s2)
      .say('p가 가리키는 곳에 fresh를 써야 해요. stock 이름은 쓰지 않아요.', 'text:주석 아래에 p가 가리키는 곳에 fresh를 쓰는 줄을 쓰세요.')
      .run('printf("%d\\n%d", stock, other);')
      .say('2와 9예요. 아직 아무것도 쓰지 않았어요.', 'output')
      .patch('    // 이 주석 아래에 p가 가리키는 곳에 fresh를 쓰는 줄을 쓰세요.\n',
             '    // 이 주석 아래에 p가 가리키는 곳에 fresh를 쓰는 줄을 쓰세요.\n    *p = fresh;\n',
             '*p에 fresh를 대입해요.')
      .run('printf("%d\\n%d", stock, other);')
      .say('5와 9예요. p가 가리키는 stock이 5로 바뀌었고 other는 그대로예요.', 'output')
      .say('조심하세요. p = fresh처럼 별표를 빼면 값이 아니라 p의 주소를 바꾸려는 잘못된 코드예요.', 'code:*p = fresh;'))

s3 = INC + '''int main(void) {
    int stock = 2;
    int other = 9;
    int *p = &stock;
    // 이 줄을 고쳐 q가 p와 같은 대상을 가리키게 하세요.
    int *q = &other;
    // q를 통해 쓴 뒤 p와 원래 이름으로 읽어요.
    *q = 7;
    printf("%d\\n%d\\n%d", *p, stock, other);
    return 0;
}
'''
s3_solution = s3.replace('    int *q = &other;\n', '    // p에 담긴 주소를 q에 복사해요. 이제 두 포인터가 같은 변수를 가리켜요.\n    int *q = p;\n')
n3 = (Script(s3)
      .say('q가 p와 같은 대상을 가리키게 q의 처음 값을 고쳐야 해요.', 'text:q 줄을 고쳐 q가 p와 같은 대상을 가리키게 하세요.')
      .run('printf("%d\\n%d\\n%d", *p, stock, other);')
      .say('2, 2, 7이에요. q가 other를 가리켜서 other만 7이 됐어요.', 'output')
      .patch('    int *q = &other;\n', '    int *q = p;\n', 'q에 p의 값, 곧 stock의 주소를 담아요.')
      .run('printf("%d\\n%d\\n%d", *p, stock, other);')
      .say('7, 7, 9예요. q와 p가 같은 stock을 가리켜 q로 쓴 값이 p와 stock으로도 보여요.', 'output')
      .say('조심하세요. int *q = &stock으로 고정하면 지금은 같아도 p가 다른 곳을 가리키면 달라져요.', 'code:int *q = p;'))

s4 = INC + '''int main(void) {
    // 두 재고는 서로 다른 변수예요.
    int stock = 2;
    int other = 7;
    int *p = &stock;
    // 이 줄을 고쳐 stock은 그대로 두고 p가 other를 가리키게 하세요.
    *p = other;
    printf("%d\\n%d", *p, stock);
    return 0;
}
'''
s4_solution = s4.replace('    *p = other;\n', '    // 별표 없이 p에 대입하면 가리키는 곳만 바뀌어요. stock의 값은 그대로예요.\n    p = &other;\n')
n4 = (Script(s4)
      .say('지금 줄은 stock에 other의 값을 써요. p가 가리키는 곳만 other로 옮기게 고쳐야 해요.', 'text:*p = other; 줄을 고쳐 stock은 그대로 두고 p가 other를 가리키게 하세요.')
      .run('printf("%d\\n%d", *p, stock);')
      .say('7과 7이에요. *p = other가 stock을 7로 덮어썼어요.', 'output')
      .patch('    *p = other;\n', '    p = &other;\n', '별표를 빼고 p에 other의 주소를 담아요.')
      .run('printf("%d\\n%d", *p, stock);')
      .say('7과 2예요. p는 other를 가리키고 stock은 2로 남았어요.', 'output')
      .say('조심하세요. *p = ...는 가리키는 값을 바꾸고, p = ...는 가리키는 곳을 바꿔요.', 'code:p = &other;'))

s5 = INC + '''int main(void) {
    // 같은 배열 안의 위치를 골라요.
    int bins[] = {2, 5, 7};
    int *p = bins;
    // 이 줄을 고쳐 p에서 한 칸 뒤의 값을 포인터 덧셈으로 읽으세요.
    int next = *p;
    printf("%d", next);
    return 0;
}
'''
s5_solution = s5.replace('    int next = *p;\n', '    // p + 1은 int 한 칸 뒤의 주소예요. 별표로 그곳의 값을 읽어요.\n    int next = *(p + 1);\n')
n5 = (Script(s5)
      .say('p는 배열의 첫 원소를 가리켜요. 한 칸 뒤의 값을 *(p + 1)로 읽어야 해요.', 'text:next 줄을 고쳐 p에서 한 칸 뒤의 값을 포인터 덧셈으로 읽으세요.')
      .run('printf("%d", next);')
      .say('2예요. *p는 첫 원소예요.', 'output')
      .patch('    int next = *p;\n', '    int next = *(p + 1);\n', 'p에 1을 더한 주소의 값을 읽어요.')
      .run('printf("%d", next);')
      .say('5예요. p + 1은 바로 다음 원소를 가리켜요.', 'output')
      .say('조심하세요. *p + 1은 첫 원소에 1을 더한 3이에요. 괄호가 위치를 정해요.', 'code:int next = *(p + 1);'))

s6 = INC + '''int main(void) {
    // 첫 원소와 다음 원소는 서로 다른 값이에요.
    int bins[] = {2, 5};
    int *p = bins;
    // 이 줄을 고쳐 값이 아니라 포인터를 한 원소 앞으로 옮기세요.
    (*p)++;
    printf("%d\\n%d", *p, bins[0]);
    return 0;
}
'''
s6_solution = s6.replace('    (*p)++;\n', '    // p++는 p가 다음 원소를 가리키게 해요. 배열 값은 바뀌지 않아요.\n    p++;\n')
n6 = (Script(s6)
      .say('지금 줄은 첫 원소의 값을 1 올려요. 포인터를 다음 원소로 옮기게 고쳐야 해요.', 'text:(*p)++; 줄을 고쳐 값이 아니라 포인터를 한 원소 앞으로 옮기세요.')
      .run('printf("%d\\n%d", *p, bins[0]);')
      .say('3과 3이에요. 가리키는 첫 원소 2가 3으로 바뀌었어요.', 'output')
      .patch('    (*p)++;\n', '    p++;\n', '괄호와 별표를 빼고 p 자체를 1 올려요.')
      .run('printf("%d\\n%d", *p, bins[0]);')
      .say('5와 2예요. p는 둘째 원소를 가리키고 첫 원소는 그대로 2예요.', 'output')
      .say('조심하세요. (*p)++는 값을, p++는 위치를 바꿔요.', 'code:p++;'))

s7 = INC + '''// p는 호출자가 전달한 포인터 값의 복사예요. 바꾼 포인터를 돌려줘요.
int *redirect(int *p, int *other) {
    p = other;
    return p;
}

int main(void) {
    int stock = 2;
    int other = 7;
    int *p = &stock;
    // 이 줄을 고쳐 redirect가 돌려준 포인터를 main의 p에 저장하세요.
    redirect(p, &other);
    printf("%d", *p);
    return 0;
}
'''
s7_solution = s7.replace('    redirect(p, &other);\n', '    // 함수 안의 p는 복사본이에요. 돌려받아 대입해야 main의 p가 바뀌어요.\n    p = redirect(p, &other);\n')
n7 = (Script(s7)
      .say('함수 안에서 바꾼 p는 복사본이에요. 돌려준 포인터를 main의 p에 저장해야 해요.', 'text:호출 줄을 고쳐 redirect가 돌려준 포인터를 main의 p에 저장하세요.')
      .run('printf("%d", *p);')
      .say('2예요. 함수 안의 복사본만 other를 가리켰고 main의 p는 그대로예요.', 'output')
      .patch('    redirect(p, &other);\n', '    p = redirect(p, &other);\n', '호출 앞에 p =을 붙여 돌려받은 주소를 담아요.')
      .run('printf("%d", *p);')
      .say('7이에요. main의 p가 돌려받은 other의 주소를 가리켜요.', 'output')
      .say('조심하세요. 포인터도 값처럼 복사돼 전달돼요. 함수 안의 p = other는 main의 p를 바꾸지 않아요.', 'code:p = other;'))

s8 = INC + '''// 복사한 주소로 원래 대상의 값을 바꿔요.
void add(int *p) {
    // 이 주석 아래에 p가 가리키는 값을 1 올리는 줄을 쓰세요.
}

int main(void) {
    // 원래 stock의 주소를 전달해요.
    int stock = 2;
    add(&stock);
    printf("%d", stock);
    return 0;
}
'''
s8_solution = s8.replace('    // 이 주석 아래에 p가 가리키는 값을 1 올리는 줄을 쓰세요.\n',
                         '    // 이 주석 아래에 p가 가리키는 값을 1 올리는 줄을 쓰세요.\n'
                         '    // 주소는 복사본이어도 같은 stock을 가리켜요. *p에 쓰면 main의 stock이 바뀌어요.\n'
                         '    *p = *p + 1;\n')
n8 = (Script(s8)
      .say('add가 주소를 받아요. 그 주소가 가리키는 값을 1 올려야 해요.', 'text:주석 아래에 p가 가리키는 값을 1 올리는 줄을 쓰세요.')
      .run('printf("%d", stock);')
      .say('2예요. add가 아직 아무것도 하지 않아요.', 'output')
      .patch('    // 이 주석 아래에 p가 가리키는 값을 1 올리는 줄을 쓰세요.\n',
             '    // 이 주석 아래에 p가 가리키는 값을 1 올리는 줄을 쓰세요.\n    *p = *p + 1;\n',
             '*p에 *p + 1을 써요.')
      .run('printf("%d", stock);')
      .say('3이에요. 함수가 main의 stock을 직접 바꿨어요.', 'output')
      .say('조심하세요. *p++처럼 쓰면 값이 아니라 포인터를 옮겨 stock은 그대로예요.', 'code:*p = *p + 1;'))

s9 = INC + '''// 대상이 없는 경우를 먼저 확인해요.
int read_or_zero(int *p) {
    if (p == NULL) {
        // 이 주석 아래에 가리킬 대상이 없으면 0을 돌려주는 줄을 쓰세요.
    }
    // 실제 대상이 있을 때만 그 값을 읽어요.
    return *p;
}

int main(void) {
    // NULL은 가리킬 재고가 없다는 뜻이에요.
    int stock = 2;
    int *p = NULL;
    printf("%d", read_or_zero(p));
    return 0;
}
'''
s9_solution = s9.replace('        // 이 주석 아래에 가리킬 대상이 없으면 0을 돌려주는 줄을 쓰세요.\n',
                         '        // 이 주석 아래에 가리킬 대상이 없으면 0을 돌려주는 줄을 쓰세요.\n'
                         '        // NULL을 따라가 읽으면 안 돼요. 여기서 바로 돌아가요.\n'
                         '        return 0;\n')
n9 = (Script(s9)
      .say('p가 NULL이면 *p를 읽기 전에 0을 돌려줘야 해요. 지금은 if 안이 비어 NULL을 따라가 읽어요.', 'text:if 안의 주석 아래에 가리킬 대상이 없으면 0을 돌려주는 줄을 쓰세요.')
      .patch('        // 이 주석 아래에 가리킬 대상이 없으면 0을 돌려주는 줄을 쓰세요.\n',
             '        // 이 주석 아래에 가리킬 대상이 없으면 0을 돌려주는 줄을 쓰세요.\n        return 0;\n',
             'if 안에 return 0을 써요.')
      .run('printf("%d", read_or_zero(p));')
      .say('0이에요. NULL을 확인하고 *p를 읽기 전에 돌아왔어요.', 'output')
      .patch('    int *p = NULL;\n', '    int *p = &stock;\n', 'p가 stock을 가리키게 바꿔 볼게요.')
      .run('printf("%d", read_or_zero(p));')
      .say('2예요. 대상이 있으면 if를 지나 *p를 읽어요.', 'output')
      .patch('    int *p = &stock;\n', '    int *p = NULL;\n', 'p를 처음처럼 NULL로 되돌려요.')
      .say('조심하세요. NULL을 역참조하면 정해진 결과가 없고 보통 프로그램이 멈춰요.', 'code:return *p;'))

SPECS = [
    dict(old='stp_78b1c519-f8fb-43a4-b610-1b373a50a41c', title='*p로 p가 가리키는 값을 읽으세요',
         objectives=['포인터가 가리키는 대상의 값을 역참조로 읽어요.'],
         core_flow='int *p=&stock에서 value=*p로 2를 읽는다. 채점은 stock 값과 p가 가리키는 대상(other)을 바꿔 이름으로 직접 읽는 우회를 거절한다.',
         goal='p는 stock이 있는 곳(주소)을 담은 포인터예요. `*p`는 p에 담긴 주소로 가서 그곳의 값을 읽어요.\n\n'
              'value 줄을 고쳐 p가 가리키는 값을 읽어 담으세요. 채점은 p가 다른 변수를 가리키게 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 0이 나오는지 확인하세요.', '`int value = 0;`의 0을 `*p`로 바꾸세요.', '코드 실행을 눌러 2가 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s1, solution=s1_solution, tests=[{'input': '', 'expected': '2'}],
         variations=[{'values': {'stock': '6'}, 'expected': '6'}, {'values': {'p': '&other'}, 'expected': '9'}],
         narration=n1.actions,
         review={'조심하세요. value = stock으로 쓰면 지금은 같아도 p가 other를 가리키면 틀려요.': '실제 우회와 그 한계(대상 바꾼 채점)를 말해요. 「같아도」 대조가 맞아요.'},
         reject=[([['    int value = *p;\n', '    int value = stock;\n']], 'Reading the name directly'),
                 ([['    int value = *p;\n', '    int value = 2;\n']], 'Typing the value')],
         accept=[([['    int value = *p;\n', '    int value = p[0];\n']], 'Index zero through the pointer')]),
    dict(old='stp_4812b613-fbc9-40d5-b4d0-e923806e71bf', title='*p에 fresh를 써서 가리킨 변수를 바꾸세요',
         objectives=['포인터로 가리킨 원래 변수의 값을 바꿔요.'],
         core_flow='*p = fresh로 p가 가리키는 stock을 5로 바꾸고 other는 9로 남는다. 채점은 fresh와 p의 대상을 바꿔 stock 이름으로 직접 쓰는 우회를 거절한다.',
         goal='`*p = 값`은 p가 가리키는 변수에 값을 써요. 지금 p는 stock을 가리켜요.\n\n'
              '주석 아래에 p가 가리키는 곳에 fresh를 쓰는 줄을 쓰세요. stock 이름은 쓰지 않아요. 채점은 fresh와 p가 가리키는 대상을 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 2와 9가 나오는지 확인하세요.', '주석 아래에 `*p = fresh;`를 쓰세요.', '코드 실행을 눌러 5와 9가 나오는지 확인하세요.', '작성한 코드를 제출하세요.'),
         starter_code=s2, solution=s2_solution, tests=[{'input': '', 'expected': '5\n9'}],
         variations=[{'values': {'fresh': '8'}, 'expected': '8\n9'}, {'values': {'p': '&other'}, 'expected': '2\n5'}],
         narration=n2.actions,
         review={'조심하세요. p = fresh처럼 별표를 빼면 값이 아니라 p의 주소를 바꾸려는 잘못된 코드예요.': '실제 흔한 실수(int를 포인터에 대입, 컴파일 경고/오류)를 정확히 말해요.'},
         reject=[([['    *p = fresh;\n', '    stock = fresh;\n']], 'Writing the name directly'),
                 ([['    *p = fresh;\n', '    *p = 5;\n']], 'Typing the value')],
         accept=[([['    *p = fresh;\n', '    p[0] = fresh;\n']], 'Index zero through the pointer')]),
    dict(old='stp_8a08759a-a241-402f-890f-eee4ee5ad024', title='q가 p와 같은 대상을 가리키게 하세요',
         objectives=['포인터 복사로 두 이름이 같은 대상을 가리키는 별칭을 만들어요.'],
         core_flow='int *q=&other면 *q=7이 other만 바꿔 2,2,7이다. int *q=p로 고쳐 7,7,9를 확인한다. 채점은 p의 대상을 other로 바꿔 q가 정말 p를 따라가는지 확인한다.',
         goal='포인터 변수끼리 대입하면 주소가 복사돼요. 그러면 두 포인터가 같은 변수를 가리켜, 한쪽으로 쓴 값이 다른 쪽으로도 보여요.\n\n'
              'q 줄을 고쳐 q가 p와 같은 대상을 가리키게 하세요. 채점은 p가 다른 변수를 가리키게 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 2, 2, 7이 나오는지 확인하세요.', '`int *q = &other;`를 p의 값을 복사하는 선언으로 고치세요.', '코드 실행을 눌러 7, 7, 9가 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s3, solution=s3_solution, tests=[{'input': '', 'expected': '7\n7\n9'}],
         variations=[{'values': {'p': '&other'}, 'expected': '7\n2\n7'}, {'values': {'stock': '4'}, 'expected': '7\n7\n9'}],
         narration=n3.actions,
         review={'조심하세요. int *q = &stock으로 고정하면 지금은 같아도 p가 다른 곳을 가리키면 달라져요.': '실제 우회와 그 한계(대상 바꾼 채점)를 말해요.'},
         reject=[([['    int *q = p;\n', '    int *q = &stock;\n']], 'Pointing at stock by name')],
         accept=[([['    int *q = p;\n', '    int *q = &*p;\n']], 'Address of what p points to')]),
    dict(old='stp_03b7959c-42a1-4a35-8b7e-233701e935e1', title='stock은 두고 p가 other를 가리키게 고치세요',
         objectives=['포인터의 대상 변경과 대상 값 변경을 구별해요.'],
         core_flow='*p = other는 stock을 7로 덮어써 7,7이다. p = &other로 고쳐 7,2를 확인한다. 채점은 other와 stock을 바꿔 실행한다.',
         goal='두 재고 stock과 other는 서로 다른 변수예요. `*p = 값`은 가리키는 변수의 값을 바꾸고, `p = 주소`는 p가 가리키는 곳만 바꿔요. 지금 줄은 stock의 값을 덮어써요.\n\n'
              '`*p = other;` 줄을 고쳐 stock은 그대로 두고 p가 other를 가리키게 하세요. 채점은 두 재고 값을 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 7과 7이 나오는지 확인하세요.', '`*p = other;`를 p에 other의 주소를 담는 줄로 고치세요.', '코드 실행을 눌러 7과 2가 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s4, solution=s4_solution, tests=[{'input': '', 'expected': '7\n2'}],
         variations=[{'values': {'other': '4'}, 'expected': '4\n2'}, {'values': {'stock': '9'}, 'expected': '7\n9'}],
         narration=n4.actions,
         review={'조심하세요. *p = ...는 가리키는 값을 바꾸고, p = ...는 가리키는 곳을 바꿔요.': '실제 C 의미를 정확히 대조해요.'},
         reject=[([['    p = &other;\n', '    *p = other;\n']], 'Overwriting stock'),
                 ([['    printf("%d\\n%d", *p, stock);\n', '    printf("7\\n2");\n']], 'Printing typed text')],
         accept=[([['    p = &other;\n', '    int *moved = &other;\n    p = moved;\n']], 'Through another pointer')]),
    dict(old='stp_a7372ab7-62c4-4769-bd7d-043fef74e694', title='*(p + 1)로 한 칸 뒤의 값을 읽으세요',
         objectives=['포인터 덧셈으로 배열의 다음 원소를 읽어요.'],
         core_flow='p=bins는 첫 원소를 가리킨다. next=*(p + 1)로 5를 읽는다. *p + 1은 3이다. 채점은 bins와 p의 시작 위치를 바꿔 실행한다.',
         goal='배열 이름 bins는 첫 원소의 주소처럼 쓰여서 p는 첫 원소를 가리켜요. `p + 1`은 int 한 칸 뒤의 주소예요.\n\n'
              'next 줄을 고쳐 p에서 한 칸 뒤의 값을 포인터 덧셈으로 읽으세요. 채점은 배열 값과 p의 시작 위치를 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 2가 나오는지 확인하세요.', '`*p`를 `*(p + 1)`로 고치세요.', '코드 실행을 눌러 5가 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s5, solution=s5_solution, tests=[{'input': '', 'expected': '5'}],
         variations=[{'values': {'bins': '{1, 8, 3}'}, 'expected': '8'}, {'values': {'p': 'bins + 1'}, 'expected': '7'}],
         narration=n5.actions,
         review={'조심하세요. *p + 1은 첫 원소에 1을 더한 3이에요. 괄호가 위치를 정해요.': '실제 연산자 우선순위와 그 실제 값을 말해요.'},
         reject=[([['    int next = *(p + 1);\n', '    int next = *p + 1;\n']], 'Adding to the value'),
                 ([['    int next = *(p + 1);\n', '    int next = bins[1];\n']], 'Ignoring where p starts')],
         accept=[([['    int next = *(p + 1);\n', '    int next = p[1];\n']], 'Index through the pointer')]),
    dict(old='stp_f22733cc-b63f-40ab-b199-442ca98d3b91', title='(*p)++를 p++로 고쳐 포인터를 옮기세요',
         objectives=['포인터 이동과 가리킨 값의 증가를 구별해요.'],
         core_flow='(*p)++는 첫 원소를 3으로 바꿔 3,3이다. p++로 고쳐 5,2를 확인한다. 채점은 bins를 바꿔 실행한다.',
         goal='포인터에 ++를 쓰면 다음 원소를 가리키고, 괄호로 `(*p)++`라고 쓰면 가리킨 값을 1 올려요. 지금 줄은 첫 원소의 값을 바꿔요.\n\n'
              '`(*p)++;` 줄을 고쳐 값이 아니라 포인터를 한 원소 앞으로 옮기세요. 채점은 배열 값을 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 3과 3이 나오는지 확인하세요.', '`(*p)++;`를 `p++;`로 고치세요.', '코드 실행을 눌러 5와 2가 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s6, solution=s6_solution, tests=[{'input': '', 'expected': '5\n2'}],
         variations=[{'values': {'bins': '{4, 9}'}, 'expected': '9\n4'}],
         narration=n6.actions,
         review={'조심하세요. (*p)++는 값을, p++는 위치를 바꿔요.': '실제 C 의미를 정확히 대조해요.'},
         reject=[([['    p++;\n', '    (*p)++;\n']], 'Increasing the value'),
                 ([['    p++;\n', '    bins[0] = 5;\n']], 'Typing the value')],
         accept=[([['    p++;\n', '    p = p + 1;\n']], 'Adding one to the pointer')]),
    dict(old='stp_1073c6fc-089d-417e-8961-197a591c145d', title='redirect가 돌려준 포인터를 main의 p에 저장하세요',
         objectives=['포인터 인자도 값처럼 복사됨을 알고 돌려받아 저장해요.'],
         core_flow='redirect 안의 p=other는 복사본만 바꿔 main의 *p는 2다. p = redirect(p, &other)로 고쳐 7을 확인한다. 채점은 other와 stock을 바꿔 실행한다.',
         goal='함수에 포인터를 넘기면 포인터 값(주소)이 복사돼요. 함수 안에서 그 복사본에 다른 주소를 담아도 main의 p는 그대로예요. redirect는 바꾼 포인터를 돌려줘요.\n\n'
              '호출 줄을 고쳐 redirect가 돌려준 포인터를 main의 p에 저장하세요. 채점은 두 재고 값을 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 2가 나오는지 확인하세요.', '`redirect(p, &other);` 앞에 `p =`를 붙이세요.', '코드 실행을 눌러 7이 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s7, solution=s7_solution, tests=[{'input': '', 'expected': '7'}],
         variations=[{'values': {'other': '4'}, 'expected': '4'}, {'values': {'stock': '9'}, 'expected': '7'}],
         narration=n7.actions,
         review={'조심하세요. 포인터도 값처럼 복사돼 전달돼요. 함수 안의 p = other는 main의 p를 바꾸지 않아요.': '실제 C 값 전달 규칙을 포인터에 맞게 말해요.'},
         reject=[([['    p = redirect(p, &other);\n', '    redirect(p, &other);\n']], 'Discarding the returned pointer'),
                 ([['    p = redirect(p, &other);\n', '    redirect(p, &other);\n    stock = 7;\n']], 'Typing the value into stock')],
         accept=[([['    p = redirect(p, &other);\n', '    int *moved = redirect(p, &other);\n    p = moved;\n']], 'Through another pointer')]),
    dict(old='stp_cadcf645-6dd6-4462-b67a-b6c0cd2e2775', title='add에서 *p를 1 올려 main의 stock을 바꾸세요',
         objectives=['주소를 받아 함수에서 원래 대상의 값을 바꿔요.'],
         core_flow='add(&stock)에 주소를 넘기고 add 안에서 *p = *p + 1을 써서 stock 3을 확인한다. 채점은 stock을 바꿔 실행한다.',
         goal='add는 stock의 주소를 받아요. 주소 자체는 복사본이어도 같은 stock을 가리키므로 `*p`에 쓰면 main의 stock이 바뀌어요.\n\n'
              'add 안의 주석 아래에 p가 가리키는 값을 1 올리는 줄을 쓰세요. 채점은 stock을 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 2가 나오는지 확인하세요.', '주석 아래에 `*p = *p + 1;`을 쓰세요.', '코드 실행을 눌러 3이 나오는지 확인하세요.', '작성한 코드를 제출하세요.'),
         starter_code=s8, solution=s8_solution, tests=[{'input': '', 'expected': '3'}],
         variations=[{'values': {'stock': '9'}, 'expected': '10'}, {'values': {'stock': '-1'}, 'expected': '0'}],
         narration=n8.actions,
         review={'조심하세요. *p++처럼 쓰면 값이 아니라 포인터를 옮겨 stock은 그대로예요.': '실제 우선순위(*p++ = *(p++))와 그 결과를 말해요.'},
         reject=[([['    *p = *p + 1;\n', '    *p++;\n']], 'Moving the pointer'),
                 ([['    *p = *p + 1;\n', '    *p = 3;\n']], 'Typing the value')],
         accept=[([['    *p = *p + 1;\n', '    (*p)++;\n']], 'Parenthesized increment')]),
    dict(old='stp_c879a47e-352e-4ccb-84f8-6f048de496e9', title='p가 NULL이면 0을 돌려주는 줄을 쓰세요',
         objectives=['역참조 전에 NULL을 확인해 대상이 없는 경우를 막아요.'],
         core_flow='p가 NULL인데 if 안이 비어 *p를 읽는다. if 안에 return 0을 써서 0을 확인하고, p=&stock이면 2를 읽는다. 채점은 NULL과 실제 대상을 모두 실행한다.',
         goal='NULL은 가리킬 재고가 없다는 뜻이에요. NULL을 따라가 읽으면(역참조) 정해진 결과가 없어 프로그램이 멈출 수 있어요. 그래서 읽기 전에 먼저 확인해요. 지금은 if 안이 비어 있어요.\n\n'
              'if 안의 주석 아래에 가리킬 대상이 없으면 0을 돌려주는 줄을 쓰세요. 채점은 p가 실제 재고를 가리키는 경우도 실행해요.\n\n'
              + todo('if 안의 주석 아래에 `return 0;`을 쓰세요.', '코드 실행을 눌러 0이 나오는지 확인하세요.', '작성한 코드를 제출하세요.'),
         starter_code=s9, solution=s9_solution, tests=[{'input': '', 'expected': '0'}],
         variations=[{'values': {'p': '&stock'}, 'expected': '2'}, {'values': {'p': '&stock', 'stock': '6'}, 'expected': '6'}],
         narration=n9.actions,
         review={'2예요. 대상이 있으면 if를 지나 *p를 읽어요.': '실제 p=&stock 실행 결과와 맞아요.',
                 '조심하세요. NULL을 역참조하면 정해진 결과가 없고 보통 프로그램이 멈춰요.': '실제 C 규칙(정의되지 않은 동작)을 정확히 말해요. 시작 코드는 채점에서 실패해요.'},
         reject=[([['        return 0;\n    }\n    // 실제', '    }\n    // 실제'], ['    return *p;\n', '    return 0;\n']], 'Always zero ignores the target'),
                 ([['        return 0;\n    }\n', '        return 1;\n    }\n']], 'Wrong value without a target')],
         accept=[([['    if (p == NULL) {\n', '    if (!p) {\n']], 'Negated pointer test')]),
]
