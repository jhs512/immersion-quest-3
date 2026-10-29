"""engineer-c-structures: 7 answer-picking steps -> coding steps (2026-10-29)."""
from _kit import Script, todo

PRD_SCOPE = ['4챕터·4단원·19스텝으로 같은 상황을 점진적으로 바꿔요.',
             '구조체 필드·복사·포인터 접근·배열·안의 문자 배열과 같은 타입의 함수 포인터를 한 줄씩 직접 써서 실행해요.',
             '기존 문제의 본질과 코드를 유지하며 비트·동적 할당의 스텝을 이어 가요.']
PRD_GRADING = ['직접 쓴 코드는 실제 C 컴파일러로 실행해 판정하고, 짧은 답안은 제출한 답을 판정해요.',
               '구조체의 어느 대상이 바뀌는지와 다른 준비 값·다른 함수 입력을 검사해요. 숫자를 적어 넣은 출력은 거절해요.',
               '마지막 도전(stp_9be10228-3f66-4600-876e-589546f4a886): 시작 답안은 실패해야 해요. 실제 실행 결과 또는 각 서술형 답안 칸을 검사하고 오답과 동등한 정답도 대조해요.']
PRD_NARRATION = ['필드·대상·함수 선택 한 곳씩 고치고 실제 출력으로 비교해요.',
                 '값 복사와 별칭·문자 배열과 리터럴·함수 선택과 호출을 조심할 지점으로 짚어요.']

STOCK = '''#include <stdio.h>

// 관련된 두 숫자를 한 값으로 묶어요.
typedef struct {
    int count;
    int code;
} Stock;

'''

s1 = STOCK + '''int main(void) {
    Stock item = {2, 7};
    printf("%d\\n", item.count);
    // 이 줄을 고쳐 같은 item의 code 필드를 출력하세요.
    printf("%d", item.count);
    return 0;
}
'''
s1_solution = s1.replace('    printf("%d", item.count);\n', '    // 점 뒤의 필드 이름이 묶음 안에서 읽을 값을 골라요.\n    printf("%d", item.code);\n')
n1 = (Script(s1)
      .say('둘째 줄이 같은 item의 code를 출력하게 필드 이름을 고쳐야 해요.', 'text:둘째 printf를 고쳐 같은 item의 code 필드를 출력하세요.')
      .run('printf("%d\\n", item.count);', 'printf("%d", item.count);')
      .say('2와 2예요. 두 줄 모두 count를 읽었어요.', 'output')
      .patch('    printf("%d", item.count);\n', '    printf("%d", item.code);\n', '점 뒤의 필드 이름을 code로 바꿔요.')
      .run('printf("%d\\n", item.count);', 'printf("%d", item.code);')
      .say('2와 7이에요. 같은 묶음에서 필드 이름으로 다른 값을 골랐어요.', 'output')
      .say('조심하세요. 중괄호 초기화는 선언한 필드 순서대로 들어가요. {2, 7}이면 count가 2, code가 7이에요.', 'code:Stock item = {2, 7};'))

s2 = STOCK + '''int main(void) {
    Stock a = {2, 7};
    int fresh = 5;
    // 구조체 값 자체를 다른 변수로 복사해요.
    Stock b = a;
    // 이 주석 아래에 복사한 b의 count만 fresh로 바꾸세요.
    printf("%d\\n%d", a.count, b.count);
    return 0;
}
'''
s2_solution = s2.replace('    // 이 주석 아래에 복사한 b의 count만 fresh로 바꾸세요.\n',
                         '    // 이 주석 아래에 복사한 b의 count만 fresh로 바꾸세요.\n'
                         '    // b는 a의 모든 필드를 복사한 별도 값이에요. b를 바꿔도 a는 그대로예요.\n'
                         '    b.count = fresh;\n')
n2 = (Script(s2)
      .say('b는 a를 복사한 구조체예요. b의 count만 fresh로 바꿔야 해요.', 'text:주석 아래에 복사한 b의 count만 fresh로 바꾸세요.')
      .run('printf("%d\\n%d", a.count, b.count);')
      .say('2와 2예요. 복사한 직후라 두 값이 같아요.', 'output')
      .patch('    // 이 주석 아래에 복사한 b의 count만 fresh로 바꾸세요.\n',
             '    // 이 주석 아래에 복사한 b의 count만 fresh로 바꾸세요.\n    b.count = fresh;\n',
             'b.count에 fresh를 대입해요.')
      .run('printf("%d\\n%d", a.count, b.count);')
      .say('2와 5예요. b만 바뀌고 a는 그대로예요.', 'output')
      .say('조심하세요. 구조체 대입은 별칭이 아니라 값 복사예요. 같은 대상을 함께 보려면 포인터가 필요해요.', 'code:Stock b = a;'))

s3 = STOCK + '''int main(void) {
    Stock item = {2, 7};
    Stock other = {4, 1};
    int fresh = 5;
    // 구조체가 있는 곳을 p가 가리켜요.
    Stock *p = &item;
    // 이 주석 아래에 p가 가리키는 구조체의 count를 fresh로 바꾸세요.
    printf("%d\\n%d", item.count, other.count);
    return 0;
}
'''
s3_solution = s3.replace('    // 이 주석 아래에 p가 가리키는 구조체의 count를 fresh로 바꾸세요.\n',
                         '    // 이 주석 아래에 p가 가리키는 구조체의 count를 fresh로 바꾸세요.\n'
                         '    // p->count는 (*p).count와 같아요. p가 가리키는 구조체의 필드예요.\n'
                         '    p->count = fresh;\n')
n3 = (Script(s3)
      .say('p가 가리키는 구조체의 count를 화살표 연산자로 바꿔야 해요.', 'text:주석 아래에 p가 가리키는 구조체의 count를 fresh로 바꾸세요.')
      .run('printf("%d\\n%d", item.count, other.count);')
      .say('2와 4예요. 아직 바꾸지 않았어요.', 'output')
      .patch('    // 이 주석 아래에 p가 가리키는 구조체의 count를 fresh로 바꾸세요.\n',
             '    // 이 주석 아래에 p가 가리키는 구조체의 count를 fresh로 바꾸세요.\n    p->count = fresh;\n',
             'p->count에 fresh를 대입해요.')
      .run('printf("%d\\n%d", item.count, other.count);')
      .say('5와 4예요. p가 가리키는 item의 count가 바뀌었어요.', 'output')
      .say('조심하세요. *p.count는 점이 먼저 묶여 p.count를 찾으므로 컴파일 오류예요. (*p).count나 p->count로 써요.', 'code:p->count = fresh;'))

s4 = STOCK + '''int main(void) {
    // 배열의 각 원소가 구조체 한 개예요.
    Stock items[] = {{2, 7}, {5, 9}};
    // 이 줄을 고쳐 둘째 원소의 count를 담으세요.
    int second = items[0].count;
    printf("%d", second);
    return 0;
}
'''
s4_solution = s4.replace('    int second = items[0].count;\n', '    // 먼저 [1]로 둘째 원소를 고르고, 점으로 그 안의 count를 읽어요.\n    int second = items[1].count;\n')
n4 = (Script(s4)
      .say('둘째 원소를 고른 뒤 그 count를 읽도록 위치를 고쳐야 해요.', 'text:second 줄을 고쳐 둘째 원소의 count를 담으세요.')
      .run('printf("%d", second);')
      .say('2예요. 첫째 원소의 count예요.', 'output')
      .patch('    int second = items[0].count;\n', '    int second = items[1].count;\n', '위치를 1로 바꿔 둘째 원소를 골라요.')
      .run('printf("%d", second);')
      .say('5예요. 둘째 원소 {5, 9}의 count예요.', 'output')
      .say('조심하세요. items[1].code는 같은 원소의 다른 필드 9예요.', 'code:int second = items[1].count;'))

s5 = '''#include <stdio.h>

// 문자열 리터럴 포인터 대신 수정 가능한 배열을 담아요.
typedef struct {
    char text[8];
} Label;

int main(void) {
    char first = 'R';
    // 구조체 대입은 안에 든 문자 배열 값도 복사해요.
    Label a = {"ready"};
    Label b = a;
    // 이 주석 아래에 b의 첫 글자를 first로 바꾸세요.
    printf("%s\\n%s", a.text, b.text);
    return 0;
}
'''
s5_solution = s5.replace('    // 이 주석 아래에 b의 첫 글자를 first로 바꾸세요.\n',
                         '    // 이 주석 아래에 b의 첫 글자를 first로 바꾸세요.\n'
                         '    // b.text는 b 안에 복사된 배열이에요. 바꿔도 a.text는 그대로예요.\n'
                         '    b.text[0] = first;\n')
n5 = (Script(s5)
      .say('b 안의 문자 배열에서 첫 글자를 first로 바꿔야 해요.', 'text:주석 아래에 b의 첫 글자를 first로 바꾸세요.')
      .run('printf("%s\\n%s", a.text, b.text);')
      .say('ready와 ready예요. 복사한 직후라 같아요.', 'output')
      .patch('    // 이 주석 아래에 b의 첫 글자를 first로 바꾸세요.\n',
             '    // 이 주석 아래에 b의 첫 글자를 first로 바꾸세요.\n    b.text[0] = first;\n',
             'b.text의 위치 0에 first를 대입해요.')
      .run('printf("%s\\n%s", a.text, b.text);')
      .say('ready와 Ready예요. 구조체 안의 배열까지 복사돼 b만 바뀌었어요.', 'output')
      .say('조심하세요. 필드가 char *였다면 같은 문자열을 가리키는 주소만 복사돼요. 여기서는 배열이라 글자가 복사돼요.', 'code:char text[8];'))

FUNCS = '''#include <stdio.h>

// 같은 함수 타입의 두 계산 규칙이에요.
int add_one(int value) {
    return value + 1;
}

int twice(int value) {
    return value * 2;
}

'''
s6 = FUNCS + '''int main(void) {
    int value = 2;
    // 이 줄을 고쳐 rule이 하나 더하는 함수를 가리키게 하세요.
    int (*rule)(int) = twice;
    // 이 줄을 고쳐 rule로 value를 계산해 출력하세요.
    printf("%d", value);
    return 0;
}
'''
s6_solution = s6.replace('    int (*rule)(int) = twice;\n', '    // 함수 이름은 그 함수의 주소예요. rule에 담으면 rule(...)로 부를 수 있어요.\n    int (*rule)(int) = add_one;\n') \
                .replace('    printf("%d", value);\n', '    printf("%d", rule(value));\n')
n6 = (Script(s6)
      .say('rule이 add_one을 가리키게 하고, rule로 value를 계산해 출력해야 해요.', 'text:rule이 하나 더하는 함수를 가리키게 고친 뒤 rule로 value를 계산해 출력하세요.')
      .run('printf("%d", value);')
      .say('2예요. 아직 rule을 부르지 않고 value를 그대로 출력해요.', 'output')
      .patch('    printf("%d", value);\n', '    printf("%d", rule(value));\n', 'printf 안에서 rule(value)를 불러요.')
      .run('printf("%d", rule(value));')
      .say('4예요. rule이 아직 twice를 가리켜 두 배를 계산했어요.', 'output')
      .patch('    int (*rule)(int) = twice;\n', '    int (*rule)(int) = add_one;\n', 'rule에 add_one을 담아요.')
      .run('printf("%d", rule(value));')
      .say('3이에요. 같은 rule(value) 호출이 이번에는 add_one을 실행했어요.', 'output')
      .say('조심하세요. rule = add_one(value)처럼 괄호를 붙이면 함수가 아니라 계산 결과를 담으려는 잘못된 코드예요.', 'code:int (*rule)(int) = add_one;'))

s7 = FUNCS + '''// 받은 규칙을 현재 값에 적용해요.
int apply(int value, int (*rule)(int)) {
    // 이 줄을 고쳐 넘겨받은 rule을 value에 적용한 결과를 반환하세요.
    return value * 2;
}

int main(void) {
    int value = 2;
    printf("%d\\n", apply(value, add_one));
    printf("%d", apply(value, twice));
    return 0;
}
'''
s7_solution = s7.replace('    return value * 2;\n}\n\nint main', '    // 어떤 계산을 할지는 호출한 쪽이 넘긴 rule이 정해요.\n    return rule(value);\n}\n\nint main')
n7 = (Script(s7)
      .say('apply가 넘겨받은 규칙을 쓰도록 return 줄을 고쳐야 해요.', 'text:apply의 return 줄을 고쳐 넘겨받은 rule을 value에 적용한 결과를 반환하세요.')
      .run('printf("%d\\n", apply(value, add_one));', 'printf("%d", apply(value, twice));')
      .say('4와 4예요. add_one을 넘겨도 apply가 늘 두 배만 계산해요.', 'output')
      .patch('    return value * 2;\n}\n\nint main', '    return rule(value);\n}\n\nint main', 'rule(value)를 반환해요.')
      .run('printf("%d\\n", apply(value, add_one));', 'printf("%d", apply(value, twice));')
      .say('3과 4예요. 넘긴 규칙에 따라 하나 더하거나 두 배를 했어요.', 'output')
      .say('조심하세요. 인수로 넘길 때는 add_one처럼 이름만 써요. add_one(value)는 이미 계산한 정수예요.', 'code:apply(value, add_one)'))

SPECS = [
    dict(old='stp_be3ac498-bec9-4719-9bd5-acf535d126aa', title='같은 item의 code 필드를 출력하세요',
         objectives=['구조체 변수에서 필드 이름으로 값을 골라 읽어요.'],
         core_flow='Stock item={2,7}에서 둘째 printf를 item.code로 고쳐 2와 7을 확인한다. 채점은 item의 두 값을 바꿔 실행한다.',
         goal='같은 재고의 count와 code를 구조체 Stock 하나로 묶었어요. `변수.필드`로 묶음 안의 값을 이름으로 골라 읽어요.\n\n'
              '둘째 printf를 고쳐 같은 item의 code 필드를 출력하세요. 채점은 item의 값을 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 2와 2가 나오는지 확인하세요.', '둘째 printf의 `item.count`를 `item.code`로 고치세요.', '코드 실행을 눌러 2와 7이 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s1, solution=s1_solution, tests=[{'input': '', 'expected': '2\n7'}],
         variations=[{'values': {'item': '{4, 9}'}, 'expected': '4\n9'}],
         narration=n1.actions,
         review={'조심하세요. 중괄호 초기화는 선언한 필드 순서대로 들어가요. {2, 7}이면 count가 2, code가 7이에요.': '실제 C 초기화 규칙을 정확히 말해요.'},
         reject=[([['    printf("%d", item.code);\n', '    printf("7");\n']], 'Printing typed text')],
         accept=[([['    printf("%d", item.code);\n', '    printf("%d", (&item)->code);\n']], 'Through its address')]),
    dict(old='stp_ace371fc-9879-433a-889f-3b93a055efc1', title='복사한 b의 count만 fresh로 바꾸세요',
         objectives=['구조체 대입이 값 복사임을 확인해요.'],
         core_flow='Stock b=a로 복사한 뒤 b.count=fresh를 써서 a는 2, b는 5임을 확인한다. 채점은 a와 fresh를 바꿔 실행한다.',
         goal='`Stock b = a;`는 a의 모든 필드를 b로 복사해요. 복사한 뒤에는 서로 다른 값이라 b를 바꿔도 a는 그대로예요.\n\n'
              '주석 아래에 복사한 b의 count만 fresh로 바꾸세요. 채점은 a와 fresh를 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 2와 2가 나오는지 확인하세요.', '주석 아래에 `b.count = fresh;`를 쓰세요.', '코드 실행을 눌러 2와 5가 나오는지 확인하세요.', '작성한 코드를 제출하세요.'),
         starter_code=s2, solution=s2_solution, tests=[{'input': '', 'expected': '2\n5'}],
         variations=[{'values': {'a': '{4, 1}'}, 'expected': '4\n5'}, {'values': {'fresh': '8'}, 'expected': '2\n8'}],
         narration=n2.actions,
         review={'조심하세요. 구조체 대입은 별칭이 아니라 값 복사예요. 같은 대상을 함께 보려면 포인터가 필요해요.': '실제 C 의미를 정확히 말해요.'},
         reject=[([['    b.count = fresh;\n', '    a.count = fresh;\n']], 'Changing a instead'),
                 ([['    b.count = fresh;\n', '    b.count = 5;\n']], 'Typing the value')],
         accept=[([['    b.count = fresh;\n', '    Stock *q = &b;\n    q->count = fresh;\n']], 'Through a pointer to b')]),
    dict(old='stp_31650ad6-c09d-4e52-94b2-c0f37d2d3b87', title='p->count로 가리킨 구조체의 count를 바꾸세요',
         objectives=['포인터로 구조체 필드에 접근하는 ->를 써요.'],
         core_flow='Stock *p=&item에서 p->count=fresh로 item.count를 5로 바꾸고 other는 그대로다. 채점은 p가 other를 가리키게 바꿔 이름으로 쓰는 우회를 거절한다.',
         goal='p는 구조체 item이 있는 곳을 가리켜요. `p->count`는 `(*p).count`와 같은 뜻으로, p가 가리키는 구조체의 count 필드예요.\n\n'
              '주석 아래에 p가 가리키는 구조체의 count를 fresh로 바꾸세요. item 이름은 쓰지 않아요. 채점은 p가 다른 구조체를 가리키게 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 2와 4가 나오는지 확인하세요.', '주석 아래에 `p->count = fresh;`를 쓰세요.', '코드 실행을 눌러 5와 4가 나오는지 확인하세요.', '작성한 코드를 제출하세요.'),
         starter_code=s3, solution=s3_solution, tests=[{'input': '', 'expected': '5\n4'}],
         variations=[{'values': {'p': '&other'}, 'expected': '2\n5'}, {'values': {'fresh': '8'}, 'expected': '8\n4'}],
         narration=n3.actions,
         review={'조심하세요. *p.count는 점이 먼저 묶여 p.count를 찾으므로 컴파일 오류예요. (*p).count나 p->count로 써요.': '실제 C 우선순위와 실제 컴파일 결과를 정확히 말해요.'},
         reject=[([['    p->count = fresh;\n', '    item.count = fresh;\n']], 'Writing item by name')],
         accept=[([['    p->count = fresh;\n', '    (*p).count = fresh;\n']], 'Dereference then dot')]),
    dict(old='stp_7fcc7e79-fc73-4882-97aa-48fd684246dc', title='items[1]의 count를 담으세요',
         objectives=['구조체 배열에서 원소를 고른 뒤 필드를 읽어요.'],
         core_flow='items={{2,7},{5,9}}에서 second=items[1].count로 5를 읽는다. items[1].code는 9다. 채점은 배열 값을 바꿔 실행한다.',
         goal='배열의 각 원소가 구조체 한 개예요. `items[위치]`로 원소를 고른 뒤 `.필드`로 그 안의 값을 읽어요.\n\n'
              'second 줄을 고쳐 둘째 원소의 count를 담으세요. 채점은 배열 값을 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 2가 나오는지 확인하세요.', '`items[0]`의 위치를 둘째 원소로 고치세요.', '코드 실행을 눌러 5가 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s4, solution=s4_solution, tests=[{'input': '', 'expected': '5'}],
         variations=[{'values': {'items': '{{1, 2}, {8, 3}}'}, 'expected': '8'}],
         narration=n4.actions,
         review={'조심하세요. items[1].code는 같은 원소의 다른 필드 9예요.': '실제 혼동과 실제 값을 말해요.'},
         reject=[([['    int second = items[1].count;\n', '    int second = items[1].code;\n']], 'Wrong field'),
                 ([['    int second = items[1].count;\n', '    int second = 5;\n']], 'Typing the value')],
         accept=[([['    int second = items[1].count;\n', '    int second = (items + 1)->count;\n']], 'Pointer arithmetic on the array')]),
    dict(old='stp_87c24da0-82fa-4aab-a0f1-140d46467d6d', title='복사한 b의 첫 글자를 first로 바꾸세요',
         objectives=['구조체 안의 문자 배열도 대입할 때 값으로 복사됨을 확인해요.'],
         core_flow='Label b=a로 복사한 뒤 b.text[0]=first를 써서 a는 ready, b는 Ready임을 확인한다. 채점은 first와 a의 글자를 바꿔 실행한다.',
         goal='Label 안의 text는 여덟 칸짜리 문자 배열이에요. 구조체를 대입하면 안에 든 배열의 글자까지 복사돼요.\n\n'
              '주석 아래에 b의 첫 글자를 first로 바꾸세요. 채점은 first와 a의 글자를 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 ready와 ready가 나오는지 확인하세요.', '주석 아래에 `b.text[0] = first;`를 쓰세요.', '코드 실행을 눌러 ready와 Ready가 나오는지 확인하세요.', '작성한 코드를 제출하세요.'),
         starter_code=s5, solution=s5_solution, tests=[{'input': '', 'expected': 'ready\nReady'}],
         variations=[{'values': {'first': "'X'"}, 'expected': 'ready\nXeady'}, {'values': {'a': '{"bin"}'}, 'expected': 'bin\nRin'}],
         narration=n5.actions,
         review={'조심하세요. 필드가 char *였다면 같은 문자열을 가리키는 주소만 복사돼요. 여기서는 배열이라 글자가 복사돼요.': '실제 C 의미(포인터 필드는 얕은 복사)를 정확히 대조해요.'},
         reject=[([['    b.text[0] = first;\n', '    a.text[0] = first;\n']], 'Changing a instead'),
                 ([['    b.text[0] = first;\n', "    b.text[0] = 'R';\n"]], 'Typing the letter')],
         accept=[([['    b.text[0] = first;\n', '    *b.text = first;\n']], 'Dereferencing the array')]),
    dict(old='stp_5bd91b09-1389-4813-9e40-867f670ccaac', title='rule이 add_one을 가리키게 하고 rule로 계산하세요',
         objectives=['함수 포인터에 함수를 담아 그 포인터로 호출해요.'],
         core_flow='int (*rule)(int)에 twice가 담겨 있고 printf는 value만 출력한다. printf를 rule(value)로 바꾸면 4, rule에 add_one을 담으면 3이다. 채점은 value를 바꿔 실행한다.',
         goal='add_one과 twice는 int를 받아 int를 돌려주는 같은 타입의 함수예요. `int (*rule)(int)`는 그런 함수를 가리키는 변수라서, 함수 이름을 담은 뒤 `rule(값)`으로 부를 수 있어요.\n\n'
              'rule이 하나 더하는 함수를 가리키게 고친 뒤 rule로 value를 계산해 출력하세요. 채점은 value를 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 2가 나오는지 확인하세요.', 'printf의 `value`를 `rule(value)`로 고치세요.', '코드 실행을 눌러 4가 나오는지 확인하세요.',
                     '`= twice`를 `= add_one`으로 고치세요.', '코드 실행을 눌러 3이 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s6, solution=s6_solution, tests=[{'input': '', 'expected': '3'}],
         variations=[{'values': {'value': '5'}, 'expected': '6'}, {'values': {'value': '0'}, 'expected': '1'}],
         narration=n6.actions,
         review={'조심하세요. rule = add_one(value)처럼 괄호를 붙이면 함수가 아니라 계산 결과를 담으려는 잘못된 코드예요.': '실제 흔한 실수(int를 함수 포인터에 대입)를 정확히 말해요.'},
         reject=[([['    int (*rule)(int) = add_one;\n', '    int (*rule)(int) = twice;\n']], 'rule still points at twice'),
                 ([['    printf("%d", rule(value));\n', '    printf("3");\n']], 'Printing typed text')],
         accept=[([['    printf("%d", rule(value));\n', '    printf("%d", (*rule)(value));\n']], 'Explicit dereference call')]),
    dict(old='stp_2afdfe4e-ffc3-4472-b4d2-df8d95fe93ab', title='apply가 넘겨받은 rule을 적용하게 하세요',
         objectives=['함수 포인터를 인수로 받아 호출한 쪽이 고른 계산을 실행해요.'],
         core_flow='apply가 늘 value*2를 반환해 add_one을 넘겨도 4,4다. return rule(value)로 고쳐 3,4를 확인한다. 채점은 value를 바꿔 실행한다.',
         goal='계산 규칙도 인수로 전달할 수 있어요. apply는 규칙 rule을 받지만 지금은 받은 규칙을 무시하고 늘 두 배만 계산해요.\n\n'
              'apply의 return 줄을 고쳐 넘겨받은 rule을 value에 적용한 결과를 반환하세요. 채점은 value를 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 4와 4가 나오는지 확인하세요.', 'apply 안의 `return value * 2;`를 `return rule(value);`로 고치세요.', '코드 실행을 눌러 3과 4가 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s7, solution=s7_solution, tests=[{'input': '', 'expected': '3\n4'}],
         variations=[{'values': {'value': '5'}, 'expected': '6\n10'}, {'values': {'value': '0'}, 'expected': '1\n0'}],
         narration=n7.actions,
         review={'조심하세요. 인수로 넘길 때는 add_one처럼 이름만 써요. add_one(value)는 이미 계산한 정수예요.': '실제 C 의미(함수 지정자와 호출 결과)를 정확히 말해요.'},
         reject=[([['    return rule(value);\n}\n\nint main', '    return add_one(value);\n}\n\nint main']], 'Always add_one'),
                 ([['    return rule(value);\n}\n\nint main', '    return value + 1;\n}\n\nint main']], 'Ignoring the rule')],
         accept=[([['    return rule(value);\n}\n\nint main', '    int result = (*rule)(value);\n    return result;\n}\n\nint main']], 'Explicit dereference call')]),
]
