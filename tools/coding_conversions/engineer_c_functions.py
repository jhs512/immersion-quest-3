"""engineer-c-functions: 9 answer-picking steps -> coding steps (2026-10-29)."""
from _kit import Script, todo

PRD_SCOPE = ['두 챕터·두 단원·열한 스텝으로 같은 재고 계산을 함수로 나눠요.',
             '반환·값 복사·반환값 저장·같은 이름의 지역 변수·static 수명·전역 변수·재귀의 끝과 복귀를 한두 줄씩 직접 써서 실행해요.']
PRD_GRADING = ['직접 쓴 코드를 실제 C 컴파일러로 실행해 판정해요.',
               '매개변수·지역 이름·반환값을 따로 관찰하고, 재고·호출 횟수·재귀 입력을 바꾼 여러 작은 실행에서 검사해요.',
               '함수 호출만으로 main의 변수가 자동 변경된다고 보지 않아요. 숫자를 적어 넣은 출력은 거절해요.',
               '마지막 도전(stp_dba636c3-ea11-4e6d-9eca-5d3006fb7b12): 시작 답안은 실패해야 해요. 실제 실행 결과 또는 각 서술형 답안 칸을 검사하고 오답과 동등한 정답도 대조해요.']
PRD_NARRATION = ['함수 본문·호출·저장을 한 곳씩 써 넣고 실행해 실제 결과를 읽어요.',
                 '복사·반환값 버림·static 수명·끝 조건을 조심할 지점으로 짚어요.',
                 '복사와 재귀의 관계를 작은 과정 그림으로 보조하고 학생 답안은 보존해요.']

INC = '#include <stdio.h>\n\n'

# ---- 1 ------------------------------------------------------------------------------
s1 = INC + '''// 받은 값보다 하나 큰 결과를 돌려줘요.
int next_stock(int value) {
    // 이 줄을 고쳐 value보다 하나 큰 값을 반환하세요.
    return 0;
}

int main(void) {
    // 원래 재고를 함수에 전달해 계산해요.
    int stock = 2;
    printf("%d", next_stock(stock));
    return 0;
}
'''
s1_solution = s1.replace('    return 0;\n}\n\nint main', '    // return 뒤의 식이 호출한 자리로 돌아가는 값이에요.\n    return value + 1;\n}\n\nint main')
n1 = (Script(s1)
      .say('next_stock이 받은 값보다 하나 큰 값을 돌려주게 return 줄을 고쳐야 해요.', 'text:next_stock의 return 줄을 고쳐 value보다 하나 큰 값을 반환하세요.')
      .run('printf("%d", next_stock(stock));')
      .say('0이에요. 함수가 아직 0을 돌려줘요.', 'output')
      .patch('    return 0;\n}\n\nint main', '    return value + 1;\n}\n\nint main', 'value에 1을 더한 값을 반환해요.')
      .run('printf("%d", next_stock(stock));')
      .say('3이에요. stock 2가 value로 전달되고 3이 호출한 자리로 돌아왔어요.', 'output')
      .say('조심하세요. return 3처럼 숫자를 적으면 재고가 바뀌어도 늘 3이에요.', 'code:return value + 1;'))

# ---- 2 ------------------------------------------------------------------------------
s2 = INC + '''// value는 호출자가 전달한 값의 복사예요.
void show_next(int value) {
    // 이 주석 아래에 value를 1 올리고 그 value를 출력하는 두 줄을 쓰세요.
}

int main(void) {
    // 함수 안 값과 main의 값을 따로 확인해요.
    int stock = 2;
    show_next(stock);
    printf("%d", stock);
    return 0;
}
'''
s2_solution = s2.replace('    // 이 주석 아래에 value를 1 올리고 그 value를 출력하는 두 줄을 쓰세요.\n',
                         '    // 이 주석 아래에 value를 1 올리고 그 value를 출력하는 두 줄을 쓰세요.\n'
                         '    // 복사본 value만 바뀌어요. main의 stock은 그대로예요.\n'
                         '    value = value + 1;\n    printf("%d\\n", value);\n')
n2 = (Script(s2)
      .say('show_next 안에서 매개변수 value를 1 올리고 출력해야 해요.', 'text:주석 아래에 value를 1 올리고 그 value를 출력하는 두 줄을 쓰세요.')
      .run('show_next(stock);', 'printf("%d", stock);')
      .say('2만 나와요. 함수가 아직 아무것도 하지 않고 main이 stock을 출력했어요.', 'output')
      .patch('    // 이 주석 아래에 value를 1 올리고 그 value를 출력하는 두 줄을 쓰세요.\n',
             '    // 이 주석 아래에 value를 1 올리고 그 value를 출력하는 두 줄을 쓰세요.\n    value = value + 1;\n    printf("%d\\n", value);\n',
             'value를 1 올리고 줄바꿈과 함께 출력해요.')
      .run('show_next(stock);', 'printf("%d", stock);')
      .say('3 다음 2예요. 함수 안의 복사본은 3이 됐지만 main의 stock은 2로 남았어요.', 'output')
      .say('조심하세요. 함수 안에서 stock = stock + 1로 쓰면 main의 stock이 보이지 않아 컴파일 오류예요.', 'code:value = value + 1;'))

# ---- 3 ------------------------------------------------------------------------------
s3 = INC + '''// 받은 값보다 하나 큰 결과를 돌려줘요.
int next_stock(int value) {
    return value + 1;
}

int main(void) {
    int stock = 2;
    // 이 줄을 고쳐 반환값을 stock에 저장하세요.
    next_stock(stock);
    printf("%d", stock);
    return 0;
}
'''
s3_solution = s3.replace('    next_stock(stock);\n', '    // 반환값은 대입해야 남아요. 함수가 stock을 직접 바꾸지는 않아요.\n    stock = next_stock(stock);\n')
n3 = (Script(s3)
      .say('함수의 결과로 main의 재고도 바꾸려면 반환값을 stock에 저장해야 해요.', 'text:호출 줄을 고쳐 반환값을 stock에 저장하세요.')
      .run('printf("%d", stock);')
      .say('2예요. 반환된 3을 아무 데도 저장하지 않고 버렸어요.', 'output')
      .patch('    next_stock(stock);\n', '    stock = next_stock(stock);\n', '호출 앞에 stock =을 붙여요.')
      .run('printf("%d", stock);')
      .say('3이에요. 반환값을 stock에 대입했어요.', 'output')
      .say('조심하세요. 함수가 같은 값을 받았다고 호출한 쪽 변수가 저절로 바뀌지는 않아요.', 'code:stock = next_stock(stock);'))

# ---- 4 ------------------------------------------------------------------------------
s4 = INC + '''// 이 함수의 stock은 main의 같은 이름과 별개예요.
int adjusted(int value) {
    // 이 주석 아래에 이 함수만의 stock을 10으로 만들고, 반환 줄을 stock + value로 고치세요.
    return value;
}

int main(void) {
    // 입력한 재고를 main의 stock에 담아요.
    int stock;
    scanf("%d", &stock);
    printf("%d\\n", adjusted(stock));
    printf("%d", stock);
    return 0;
}
'''
s4_solution = s4.replace('    return value;\n',
                         '    // 함수 안에서 만든 지역 변수 stock은 main의 stock과 다른 칸이에요.\n'
                         '    int stock = 10;\n    return stock + value;\n')
n4 = (Script(s4)
      .say('adjusted 안에 같은 이름 stock을 10으로 만들고 stock + value를 반환해야 해요.', 'text:주석 아래에 이 함수만의 stock을 10으로 만들고, 반환 줄을 stock + value로 고치세요.')
      .run('printf("%d\\n", adjusted(stock));', 'printf("%d", stock);')
      .say('2와 2예요. 지금 함수는 받은 값을 그대로 돌려줘요.', 'output')
      .patch('    return value;\n', '    int stock = 10;\n    return stock + value;\n', '함수 안에 stock을 10으로 만들고 value를 더해 반환해요.')
      .run('printf("%d\\n", adjusted(stock));', 'printf("%d", stock);')
      .say('12와 2예요. 함수 안의 stock 10에 2를 더했고, main의 stock은 그대로 2예요.', 'output')
      .say('조심하세요. 이름이 같아도 함수마다 따로 있는 지역 변수예요. 함수의 stock = 10이 main의 stock을 바꾸지 않아요.', 'code:int stock = 10;'))

# ---- 5 ------------------------------------------------------------------------------
s5 = INC + '''// 호출 횟수를 세어 돌려줘요.
int bump(void) {
    // 이 선언에 static을 붙여 호출 사이에도 calls가 남게 하세요.
    int calls = 0;
    calls = calls + 1;
    return calls;
}

int main(void) {
    int times = 2;
    for (int i = 0; i < times; i++) {
        printf("%d\\n", bump());
    }
    return 0;
}
'''
s5_solution = s5.replace('    int calls = 0;\n', '    // static 지역 변수는 프로그램이 끝날 때까지 남고, 처음 한 번만 0으로 준비돼요.\n    static int calls = 0;\n')
n5 = (Script(s5)
      .say('calls 선언에 static을 붙여 호출 사이에도 값이 남게 해야 해요.', 'text:calls 선언에 static을 붙여 호출 사이에도 calls가 남게 하세요.')
      .run('printf("%d\\n", bump());')
      .say('1과 1이에요. 부를 때마다 calls를 새로 0으로 만들었어요.', 'output')
      .patch('    int calls = 0;\n', '    static int calls = 0;\n', 'int 앞에 static을 붙여요.')
      .run('printf("%d\\n", bump());')
      .say('1과 2예요. 두 번째 호출이 첫 호출에서 남은 1에 이어 셌어요.', 'output')
      .say('조심하세요. static 지역 변수도 이름은 bump 안에서만 보여요. 남는 것은 값이에요.', 'code:static int calls = 0;'))

# ---- 6 ------------------------------------------------------------------------------
s6 = INC + '''// 함수 밖에 둔 재고를 함께 읽어요.
int stock = 2;

void increase(void) {
    // 이 주석 아래에 함수 밖의 stock을 1 늘리는 줄을 쓰세요. 새 변수를 만들지 않아요.
}

int main(void) {
    increase();
    printf("%d", stock);
    return 0;
}
'''
s6_solution = s6.replace('    // 이 주석 아래에 함수 밖의 stock을 1 늘리는 줄을 쓰세요. 새 변수를 만들지 않아요.\n',
                         '    // 이 주석 아래에 함수 밖의 stock을 1 늘리는 줄을 쓰세요. 새 변수를 만들지 않아요.\n'
                         '    // 함수 안에 같은 이름 선언이 없으니 stock은 전역 변수를 가리켜요.\n'
                         '    stock = stock + 1;\n')
n6 = (Script(s6)
      .say('increase가 함수 밖의 stock을 1 늘리게 해야 해요. 함수 안에 새 변수는 만들지 않아요.', 'text:주석 아래에 함수 밖의 stock을 1 늘리는 줄을 쓰세요.')
      .run('printf("%d", stock);')
      .say('2예요. increase가 아직 아무것도 바꾸지 않아요.', 'output')
      .patch('    // 이 주석 아래에 함수 밖의 stock을 1 늘리는 줄을 쓰세요. 새 변수를 만들지 않아요.\n',
             '    // 이 주석 아래에 함수 밖의 stock을 1 늘리는 줄을 쓰세요. 새 변수를 만들지 않아요.\n    stock = stock + 1;\n',
             '선언 없이 stock = stock + 1을 써요.')
      .run('printf("%d", stock);')
      .say('3이에요. 함수 안에 같은 이름이 없어서 함수 밖의 전역 stock을 바꿨어요.', 'output')
      .say('조심하세요. int stock = 3;처럼 선언하면 함수 안의 새 지역 변수가 생겨 전역 stock은 2로 남아요.', 'code:stock = stock + 1;'))

# ---- 7 ------------------------------------------------------------------------------
s7 = INC + '''// 더 작은 값으로 자신을 부르되 0에서 멈춰요.
int sum_to(int n) {
    if (n == 0) {
        // 이 주석 아래에 0을 반환하는 끝 조건을 쓰세요.
    }
    return n + sum_to(n - 1);
}

int main(void) {
    // 입력은 0 이상 5 이하인 작은 정수예요.
    int count = 0;
    printf("%d", sum_to(count));
    return 0;
}
'''
s7_solution = s7.replace('        // 이 주석 아래에 0을 반환하는 끝 조건을 쓰세요.\n',
                         '        // 이 주석 아래에 0을 반환하는 끝 조건을 쓰세요.\n'
                         '        // 끝 조건에서 반환하지 않으면 n이 0보다 작아지며 끝없이 자신을 불러요.\n'
                         '        return 0;\n')
n7 = (Script(s7)
      .say('n이 0이면 더 부르지 않고 0을 반환하는 끝 조건을 써야 해요. 지금은 0에서도 멈추지 않아요.', 'text:if 안의 주석 아래에 0을 반환하는 끝 조건을 쓰세요.')
      .patch('        // 이 주석 아래에 0을 반환하는 끝 조건을 쓰세요.\n',
             '        // 이 주석 아래에 0을 반환하는 끝 조건을 쓰세요.\n        return 0;\n',
             'if 안에 return 0을 써요.')
      .run('printf("%d", sum_to(count));')
      .say('0이에요. 입력 0은 끝 조건에서 바로 0을 반환했어요.', 'output')
      .patch('    int count = 0;\n', '    int count = 4;\n', '입력을 4로 바꿔 볼게요.')
      .run('printf("%d", sum_to(count));')
      .say('10이에요. 4, 3, 2, 1을 거쳐 0에서 멈춘 뒤 더해 돌아왔어요.', 'output')
      .patch('    int count = 4;\n', '    int count = 0;\n', '입력을 처음 값 0으로 되돌려요.')
      .say('조심하세요. 끝 조건이 비어 있으면 0에서도 sum_to(-1)을 불러 스택이 넘칠 때까지 멈추지 않아요.', 'code:return n + sum_to(n - 1);'))

# ---- 8 ------------------------------------------------------------------------------
s8 = INC + '''// 더 작은 값으로 자신을 부르되 0에서 멈춰요.
int sum_to(int n) {
    if (n == 0) {
        return 0;
    }
    // 이 줄을 고쳐 n에 sum_to(n - 1)이 돌려준 부분 합을 더해 반환하세요.
    return n;
}

int main(void) {
    int count = 3;
    printf("%d", sum_to(count));
    return 0;
}
'''
s8_solution = s8.replace('    return n;\n', '    // 더 작은 문제 sum_to(n - 1)의 결과에 현재 n을 더해 돌려줘요.\n    return n + sum_to(n - 1);\n')
n8 = (Script(s8)
      .say('n에 더 작은 문제의 결과 sum_to(n - 1)을 더해 반환해야 해요.', 'text:마지막 return 줄을 고쳐 n에 sum_to(n - 1)이 돌려준 부분 합을 더해 반환하세요.')
      .run('printf("%d", sum_to(count));')
      .say('3이에요. 지금은 자신을 부르지 않고 입력 3만 돌려줘요.', 'output')
      .patch('    return n;\n', '    return n + sum_to(n - 1);\n', 'n에 sum_to(n - 1)의 결과를 더해 반환해요.')
      .run('printf("%d", sum_to(count));')
      .say('6이에요. sum_to(0)이 0, sum_to(1)이 1, sum_to(2)가 3을 돌려주고 마지막에 3을 더했어요.', 'output')
      .say('조심하세요. 마지막 결과는 맨 안쪽 호출의 0이 아니라 돌아오며 쌓인 합이에요.', 'code:return n + sum_to(n - 1);'))

# ---- 9 ------------------------------------------------------------------------------
s9 = INC + '''// 자기 호출 앞뒤에 현재 값을 각각 표시해요.
void visit(int n) {
    printf("%d", n);
    if (n > 0) {
        visit(n - 1);
    }
    // 이 주석 아래에 돌아온 뒤 현재 n을 한 번 더 출력하는 줄을 쓰세요.
}

int main(void) {
    int count = 2;
    visit(count);
    printf("\\n");
    return 0;
}
'''
s9_solution = s9.replace('    // 이 주석 아래에 돌아온 뒤 현재 n을 한 번 더 출력하는 줄을 쓰세요.\n',
                         '    // 이 주석 아래에 돌아온 뒤 현재 n을 한 번 더 출력하는 줄을 쓰세요.\n'
                         '    // 안쪽 호출이 모두 끝난 뒤 이 줄로 돌아와요. 그래서 작은 값부터 거꾸로 출력돼요.\n'
                         '    printf("%d", n);\n')
n9 = (Script(s9)
      .say('자기 호출이 돌아온 뒤에도 현재 n을 출력하는 줄을 써야 해요.', 'text:주석 아래에 돌아온 뒤 현재 n을 한 번 더 출력하는 줄을 쓰세요.')
      .run('visit(count);', 'printf("\\n");')
      .say('210이에요. 호출하러 내려가며 2, 1, 0을 출력했어요.', 'output')
      .patch('    // 이 주석 아래에 돌아온 뒤 현재 n을 한 번 더 출력하는 줄을 쓰세요.\n',
             '    // 이 주석 아래에 돌아온 뒤 현재 n을 한 번 더 출력하는 줄을 쓰세요.\n    printf("%d", n);\n',
             '함수 끝에 printf로 n을 한 번 더 출력해요.')
      .run('visit(count);', 'printf("\\n");')
      .say('210012예요. 내려가며 2, 1, 0, 돌아오며 0, 1, 2를 출력했어요.', 'output')
      .say('조심하세요. 호출 뒤의 줄은 안쪽 호출이 모두 끝난 뒤에야 실행돼요.', 'code:visit(n - 1);'))

SPECS = [
    dict(old='stp_b595397f-14d1-4dd9-a661-45def01e7a63', title='next_stock이 받은 값보다 하나 큰 값을 반환하게 하세요',
         objectives=['함수에 값을 전달하고 반환값을 호출한 자리에서 받아요.'],
         core_flow='next_stock(int value)의 return을 value + 1로 고쳐 stock 2에서 3을 확인한다. 채점은 stock을 바꿔 실행한다.',
         goal='재고 하나를 더하는 계산을 함수 next_stock으로 나눴어요. 호출하면 stock의 값이 value로 전달되고, return 뒤의 값이 호출한 자리로 돌아와요.\n\n'
              'next_stock의 return 줄을 고쳐 value보다 하나 큰 값을 반환하세요. 채점은 재고를 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 0이 나오는지 확인하세요.', 'next_stock 안의 `return 0;`을 value에 1을 더해 반환하는 줄로 고치세요.', '코드 실행을 눌러 3이 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s1, solution=s1_solution, tests=[{'input': '', 'expected': '3'}],
         variations=[{'values': {'stock': '7'}, 'expected': '8'}, {'values': {'stock': '0'}, 'expected': '1'}],
         narration=n1.actions,
         review={'조심하세요. return 3처럼 숫자를 적으면 재고가 바뀌어도 늘 3이에요.': '실제 우회와 그 결과(재고 변경 채점 실패)를 말해요.'},
         reject=[([['    return value + 1;\n}\n\nint main', '    return 3;\n}\n\nint main']], 'Returning a typed number'),
                 ([['    return value + 1;\n}\n\nint main', '    return value;\n}\n\nint main']], 'Returning the same value')],
         accept=[([['    return value + 1;\n}\n\nint main', '    value++;\n    return value;\n}\n\nint main']], 'Increasing the copy, then returning it')]),
    dict(old='stp_bb058cd6-2242-4058-915d-5205f3742be2', title='함수 안에서 복사본 value를 1 올려 출력하세요',
         objectives=['매개변수가 호출자 값의 복사임을 써서 확인해요.'],
         core_flow='show_next(int value) 안에 value=value+1과 printf를 써서 3을 출력하고, main의 stock은 2로 남는다. 채점은 stock을 바꿔 실행한다.',
         goal='value는 호출자가 전달한 값의 복사예요. 함수 안에서 value를 바꿔도 main의 stock은 바뀌지 않아요.\n\n'
              'show_next 안의 주석 아래에 value를 1 올리고 그 value를 출력하는 두 줄을 쓰세요. 출력 뒤에는 줄을 바꿔요. 채점은 재고를 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 2만 나오는지 확인하세요.', '주석 아래에 `value = value + 1;`을 쓰세요.', '그 아래에 value를 `printf("%d\\n", value);`로 출력하세요.',
                     '코드 실행을 눌러 3 다음 2가 나오는지 확인하세요.', '작성한 코드를 제출하세요.'),
         starter_code=s2, solution=s2_solution, tests=[{'input': '', 'expected': '3\n2'}],
         variations=[{'values': {'stock': '5'}, 'expected': '6\n5'}, {'values': {'stock': '-1'}, 'expected': '0\n-1'}],
         narration=n2.actions,
         review={'조심하세요. 함수 안에서 stock = stock + 1로 쓰면 main의 stock이 보이지 않아 컴파일 오류예요.': '실제 C 범위 규칙과 실제 컴파일 결과를 말해요.'},
         reject=[([['    printf("%d\\n", value);\n', '    printf("3\\n");\n']], 'Printing typed text'),
                 ([['    value = value + 1;\n    printf("%d\\n", value);\n', '    printf("%d\\n", value);\n    value = value + 1;\n']], 'Printing before increasing')],
         accept=[([['    value = value + 1;\n    printf("%d\\n", value);\n', '    printf("%d\\n", ++value);\n']], 'Prefix increment inside printf')]),
    dict(old='stp_6e421aba-b4dd-4d74-8011-de2908d06de9', title='next_stock의 반환값을 stock에 저장하세요',
         objectives=['반환값을 대입해야 호출한 쪽 변수가 바뀜을 확인해요.'],
         core_flow='next_stock(stock)만 부르면 반환값을 버려 2다. stock = next_stock(stock)으로 고쳐 3을 확인한다. 채점은 stock을 바꿔 실행한다.',
         goal='함수의 결과로 main의 재고도 바꾸려 해요. 지금은 next_stock을 부르기만 하고 돌아온 값을 저장하지 않아요.\n\n'
              '호출 줄을 고쳐 반환값을 stock에 저장하세요. 채점은 재고를 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 2가 나오는지 확인하세요.', '`next_stock(stock);` 앞에 `stock =`을 붙이세요.', '코드 실행을 눌러 3이 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s3, solution=s3_solution, tests=[{'input': '', 'expected': '3'}],
         variations=[{'values': {'stock': '9'}, 'expected': '10'}],
         narration=n3.actions,
         review={'조심하세요. 함수가 같은 값을 받았다고 호출한 쪽 변수가 저절로 바뀌지는 않아요.': '실제 C 값 전달 규칙을 정확히 말해요.'},
         reject=[([['    stock = next_stock(stock);\n', '    next_stock(stock);\n    stock = 3;\n']], 'Typing the value'),
                 ([['    stock = next_stock(stock);\n', '    next_stock(stock);\n']], 'Discarding the return value')],
         accept=[([['    stock = next_stock(stock);\n', '    int next = next_stock(stock);\n    stock = next;\n']], 'Through another variable')]),
    dict(old='stp_fe856be5-cb40-4e52-a93d-5ec90ccc6c6e', title='함수 안에 같은 이름의 stock을 만들어 따로 계산하세요',
         objectives=['같은 이름이어도 함수마다 지역 변수 공간이 다름을 확인해요.'],
         core_flow='adjusted 안에 int stock=10을 만들고 stock+value를 반환한다. 입력 2에서 12와 2가 나온다. main의 stock은 바뀌지 않는다. 채점은 입력 재고를 바꿔 실행한다.',
         goal='함수 안에도 stock이라는 이름을 만들 수 있어요. 함수 안에서 선언한 지역 변수는 그 함수에만 있는 칸이라서, main의 stock과 이름만 같고 서로 다른 값이에요.\n\n'
              'adjusted 안의 주석 아래에 이 함수만의 stock을 10으로 만들고, 반환 줄을 stock + value로 고치세요. 재고는 입력으로 받아요. 채점은 다른 입력으로도 실행해요.\n\n'
              + todo('코드 실행을 눌러 2와 2가 나오는지 확인하세요.', 'adjusted 안에 `int stock = 10;`을 쓰세요.', '`return value;`를 `return stock + value;`로 고치세요.',
                     '코드 실행을 눌러 12와 2가 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s4, solution=s4_solution, tests=[{'input': '2', 'expected': '12\n2'}, {'input': '5', 'expected': '15\n5'}, {'input': '0', 'expected': '10\n0'}],
         narration=n4.actions,
         review={'조심하세요. 이름이 같아도 함수마다 따로 있는 지역 변수예요. 함수의 stock = 10이 main의 stock을 바꾸지 않아요.': '실제 C 범위 규칙을 정확히 말해요. 「같아도」 대조가 출력 12와 2로 확인돼요.'},
         reject=[([['    int stock = 10;\n    return stock + value;\n', '    return 12;\n']], 'Returning a typed number'),
                 ([['    int stock = 10;\n    return stock + value;\n', '    return 10 + 2;\n']], 'Ignoring value')],
         accept=[([['    int stock = 10;\n    return stock + value;\n', '    int stock = 10;\n    stock = stock + value;\n    return stock;\n']], 'Adding into the local first')]),
    dict(old='stp_9753c53b-dc61-4770-8590-4d509bff115f', title='calls에 static을 붙여 호출 사이에도 값이 남게 하세요',
         objectives=['static 지역 변수의 수명과 일반 지역 변수를 구별해요.'],
         core_flow='bump의 int calls=0은 호출마다 새로 준비돼 1, 1이다. static을 붙여 1, 2를 확인한다. 채점은 호출 횟수 times를 바꿔 실행한다.',
         goal='같은 함수를 여러 번 차례로 불러요. 일반 지역 변수는 호출할 때마다 새로 만들어지고, static 지역 변수는 처음 한 번만 준비돼 호출 사이에도 값이 남아요.\n\n'
              'calls 선언에 static을 붙여 호출 사이에도 calls가 남게 하세요. 채점은 호출 횟수를 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 1과 1이 나오는지 확인하세요.', '`int calls = 0;` 앞에 static을 붙이세요.', '코드 실행을 눌러 1과 2가 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s5, solution=s5_solution, tests=[{'input': '', 'expected': '1\n2'}],
         variations=[{'values': {'times': '3'}, 'expected': '1\n2\n3'}, {'values': {'times': '1'}, 'expected': '1'}],
         narration=n5.actions,
         review={'조심하세요. static 지역 변수도 이름은 bump 안에서만 보여요. 남는 것은 값이에요.': '실제 C 규칙(범위와 수명의 구별)을 정확히 말해요.'},
         reject=[([['    static int calls = 0;\n    calls = calls + 1;\n    return calls;\n', '    static int calls = 0;\n    calls = calls + 1;\n    return calls > 1 ? 2 : 1;\n']], 'Capping at two'),
                 ([['    static int calls = 0;\n', '    int calls = 1;\n']], 'Starting at one')],
         accept=[([['    static int calls = 0;\n    calls = calls + 1;\n    return calls;\n', '    static int calls;\n    return ++calls;\n']], 'Static storage starts at zero')]),
    dict(old='stp_f6a7609d-443d-4eee-b646-421c32417f79', title='increase가 함수 밖의 stock을 1 늘리게 하세요',
         objectives=['함수 안에 같은 이름 선언이 없을 때 전역 변수를 바꿈을 확인해요.'],
         core_flow='전역 int stock=2가 있고 increase 안에 선언 없이 stock=stock+1을 써서 3을 확인한다. 같은 이름을 선언하면 지역 변수가 생겨 전역은 2로 남는다. 채점은 전역 stock의 처음 값을 바꿔 실행한다.',
         goal='함수 밖에 선언한 변수(전역 변수)는 여러 함수가 함께 읽고 바꿀 수 있어요. 함수 안에 같은 이름 선언이 없으면 그 이름은 전역 변수를 가리켜요.\n\n'
              'increase 안의 주석 아래에 함수 밖의 stock을 1 늘리는 줄을 쓰세요. 함수 안에 새 변수를 만들지 않아요. 채점은 stock의 처음 값을 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 2가 나오는지 확인하세요.', '주석 아래에 선언 없이 `stock = stock + 1;`을 쓰세요.', '코드 실행을 눌러 3이 나오는지 확인하세요.', '작성한 코드를 제출하세요.'),
         starter_code=s6, solution=s6_solution, tests=[{'input': '', 'expected': '3'}],
         variations=[{'values': {'stock': '7'}, 'expected': '8'}, {'values': {'stock': '0'}, 'expected': '1'}],
         narration=n6.actions,
         review={'조심하세요. int stock = 3;처럼 선언하면 함수 안의 새 지역 변수가 생겨 전역 stock은 2로 남아요.': '실제 흔한 실수(가림)와 그 실제 출력을 말해요.'},
         reject=[([['    stock = stock + 1;\n', '    int stock = 3;\n']], 'A new local hides the global'),
                 ([['    stock = stock + 1;\n', '    stock = 3;\n']], 'Typing the value')],
         accept=[([['    stock = stock + 1;\n', '    stock++;\n']], 'Increment operator')]),
    dict(old='stp_d1e47b9f-c87c-40a9-93fe-c22d54d40c67', title='sum_to에 0을 반환하는 끝 조건을 쓰세요',
         objectives=['재귀가 끝 조건에서 멈춰야 함을 써서 확인해요.'],
         core_flow='sum_to의 if (n == 0) 안이 비어 0에서도 sum_to(-1)을 부른다. return 0을 써서 입력 0에서 0, 입력 4에서 10을 확인한다. 채점은 입력 0, 1, 5로 실행한다.',
         goal='sum_to는 자기 자신을 더 작은 값으로 다시 부르는 재귀 함수예요. 재귀에는 더 부르지 않고 바로 값을 돌려주는 끝 조건이 꼭 있어야 해요. 지금은 if 안이 비어 있어 0에서도 멈추지 않아요.\n\n'
              'if 안의 주석 아래에 0을 반환하는 끝 조건을 쓰세요. 입력은 0 이상 5 이하인 작은 정수예요. 채점은 입력을 바꿔서도 실행해요.\n\n'
              + todo('if 안의 주석 아래에 `return 0;`을 쓰세요.', '코드 실행을 눌러 0이 나오는지 확인하세요.', 'count를 4로 바꿔 실행해 10이 나오는지 확인한 뒤 0으로 되돌리세요.', '작성한 코드를 제출하세요.'),
         starter_code=s7, solution=s7_solution, tests=[{'input': '', 'expected': '0'}],
         variations=[{'values': {'count': '1'}, 'expected': '1'}, {'values': {'count': '5'}, 'expected': '15'}],
         narration=n7.actions,
         review={'10이에요. 4, 3, 2, 1을 거쳐 0에서 멈춘 뒤 더해 돌아왔어요.': '실제 sum_to(4) 실행 결과와 맞아요.',
                 '조심하세요. 끝 조건이 비어 있으면 0에서도 sum_to(-1)을 불러 스택이 넘칠 때까지 멈추지 않아요.': '실제 시작 코드의 동작(무한 재귀 → 스택 넘침)을 정확히 말해요. 채점에서 시작 코드가 실패해요.'},
         reject=[([['        return 0;\n', '        return 1;\n']], 'Wrong value at the base case'),
                 ([['    printf("%d", sum_to(count));\n', '    printf("0");\n']], 'Printing typed text')],
         accept=[([['    if (n == 0) {\n', '    if (n <= 0) {\n']], 'Stopping at zero or below')]),
    dict(old='stp_7a317dc7-f3c3-4a4a-91a7-407cf7ae00c6', title='현재 수에 더 작은 sum_to의 결과를 더해 반환하세요',
         objectives=['재귀 호출이 돌려준 부분 합을 쌓아 최종 결과를 만들어요.'],
         core_flow='끝 조건 return 0은 있고 마지막 줄이 return n이라 3이다. return n + sum_to(n - 1)로 고쳐 6을 확인한다. 채점은 count를 0, 1, 5로 바꿔 실행한다.',
         goal='입력 3의 합 3+2+1을 더 작은 함수 결과로 계산해요. sum_to(3)은 3에 sum_to(2)가 돌려준 부분 합을 더하면 돼요. 끝 조건은 준비돼 있어요.\n\n'
              '마지막 return 줄을 고쳐 n에 sum_to(n - 1)이 돌려준 부분 합을 더해 반환하세요. 채점은 count를 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 3이 나오는지 확인하세요.', '`return n;`을 `return n + sum_to(n - 1);`로 고치세요.', '코드 실행을 눌러 6이 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s8, solution=s8_solution, tests=[{'input': '', 'expected': '6'}],
         variations=[{'values': {'count': '5'}, 'expected': '15'}, {'values': {'count': '1'}, 'expected': '1'}, {'values': {'count': '0'}, 'expected': '0'}],
         narration=n8.actions,
         review={'조심하세요. 마지막 결과는 맨 안쪽 호출의 0이 아니라 돌아오며 쌓인 합이에요.': '실제 흔한 혼동(끝 조건 값 = 결과)을 정확히 말해요.'},
         reject=[([['    return n + sum_to(n - 1);\n', '    return 6;\n']], 'Typing the value'),
                 ([['    return n + sum_to(n - 1);\n', '    return sum_to(n - 1);\n']], 'Dropping the current number')],
         accept=[([['    return n + sum_to(n - 1);\n', '    return n * (n + 1) / 2;\n']], 'Closed form gives the same sums')]),
    dict(old='stp_e9d3e0ca-505d-48bb-99d5-a9eb64fc3187', title='돌아온 뒤 현재 n을 한 번 더 출력하세요',
         objectives=['자기 호출 뒤의 줄이 돌아오는 순서로 실행됨을 확인해요.'],
         core_flow='visit(n)은 n을 출력하고 n>0이면 visit(n-1)을 부른다. 함수 끝에 printf로 n을 한 번 더 써서 210이 210012가 된다. 채점은 count를 바꿔 실행한다.',
         goal='visit은 현재 값을 출력한 뒤 더 작은 값으로 자신을 불러요. 자기 호출 뒤에 있는 줄은 안쪽 호출이 모두 끝나고 돌아온 다음에 실행돼요.\n\n'
              'visit의 주석 아래에 돌아온 뒤 현재 n을 한 번 더 출력하는 줄을 쓰세요. 채점은 count를 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 210이 나오는지 확인하세요.', '주석 아래에 `printf("%d", n);`을 쓰세요.', '코드 실행을 눌러 210012가 나오는지 확인하세요.', '작성한 코드를 제출하세요.'),
         starter_code=s9, solution=s9_solution, tests=[{'input': '', 'expected': '210012'}],
         variations=[{'values': {'count': '1'}, 'expected': '1001'}, {'values': {'count': '3'}, 'expected': '32100123'}],
         narration=n9.actions,
         review={'조심하세요. 호출 뒤의 줄은 안쪽 호출이 모두 끝난 뒤에야 실행돼요.': '실제 재귀 복귀 순서를 정확히 말해요.'},
         reject=[([['    printf("\\n");\n', '    printf("012\\n");\n'], ['    // 안쪽 호출이 모두 끝난 뒤 이 줄로 돌아와요. 그래서 작은 값부터 거꾸로 출력돼요.\n    printf("%d", n);\n', '']], 'Printing typed text'),
                 ([['    printf("%d", n);\n    if (n > 0) {\n', '    if (n > 0) {\n']], 'Only printing on the way back')],
         accept=[]),
]
