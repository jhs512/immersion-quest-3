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


# ---- 2026-10-30: the ten code-reading answer fields (bits, dynamic storage) become coding steps ----------
PRD_SCOPE = ['4챕터·4단원·19스텝으로 같은 상황을 점진적으로 바꿔요.',
             '구조체 필드·복사·포인터 접근·배열·안의 문자 배열과 같은 타입의 함수 포인터를 한 줄씩 직접 써서 실행해요.',
             '비트 연산(&·&&·|·^·<<·~와 마스크)과 동적 할당(malloc 뒤 저장·calloc·같은 할당의 별칭·해제 뒤 별칭 비우기)도 한 줄씩 직접 써서 실행해요.']
PRD_GRADING = ['직접 쓴 코드는 실제 C 컴파일러로 실행해 판정해요. 실행·해설만으로 성공시키지 않아요.',
               '구조체의 어느 대상이 바뀌는지와 다른 준비 값·다른 함수 입력을 검사해요. 숫자를 적어 넣은 출력은 거절해요.',
               '비트 스텝은 다른 비트 값으로, 동적 할당 스텝은 다른 저장 값·개수로 다시 실행해 연산자를 바꾼 답(&와 &&, |와 +)과 처음 값을 적은 답을 구별해요.',
               '마지막 도전(stp_9be10228-3f66-4600-876e-589546f4a886): 시작 답안은 실패해야 해요. 실제 실행 결과 또는 각 서술형 답안 칸을 검사하고 오답과 동등한 정답도 대조해요.']
PRD_NARRATION = ['필드·대상·함수 선택·연산자·할당 한 곳씩 고치고 실제 출력으로 비교해요.',
                 '값 복사와 별칭·문자 배열과 리터럴·함수 선택과 호출·비트와 논리 연산·초기화하지 않은 저장소·해제 뒤 별칭을 조심할 지점으로 짚어요.']

C_HEAD = '#include <stdio.h>\n\nint main(void) {\n'
C_HEAP = '#include <stdio.h>\n#include <stdlib.h>\n\nint main(void) {\n'
C_END = '    return 0;\n}\n'
RUN_C = '코드 실행을 눌러 지금 출력을 확인하세요.'
SUB_C = '수정한 코드를 제출하세요.'


def bit_step(old, title, objective, core_flow, intro, instruction, edit_todo, starter, solution_line, starter_line, comment,
             script, expected, variations, review, reject, accept):
    solution = starter.replace(starter_line, comment + solution_line, 1)
    return dict(old=old, title=title, objectives=[objective], core_flow=core_flow,
                goal=intro + '\n\n' + instruction + '\n\n' + todo(RUN_C, edit_todo, '코드 실행을 눌러 결과가 바뀌었는지 확인하세요.', SUB_C),
                starter_code=starter, solution=solution, tests=[{'input': '', 'expected': expected}], variations=variations,
                narration=script.actions, review=review, reject=reject, accept=accept)


b9 = C_HEAD + '''    // 두 표시 값이에요. 5는 2진수 101, 3은 011이에요.
    unsigned int flags = 5u;
    unsigned int mask = 3u;
    // 이 줄을 고쳐 flags와 mask의 같은 자리가 모두 1인 비트만 남기세요.
    unsigned int value = 0u;
    printf("%u\\n", value);
''' + C_END
n9 = (Script(b9)
      .say('두 값의 같은 자리가 모두 1인 비트만 남겨야 해요. 비트 AND 연산자 &를 써요.', 'text:value 줄을 고쳐 flags와 mask의 같은 자리가 모두 1인 비트만 남기세요.')
      .run('printf("%u\\n", value);')
      .say('0이에요. 아직 연산 없이 0을 넣었어요.', 'output')
      .patch('    unsigned int value = 0u;\n', '    unsigned int value = flags & mask;\n', '0u를 flags & mask로 바꿔요.')
      .run('printf("%u\\n", value);')
      .say('1이에요. 101과 011에서 둘 다 1인 자리는 맨 오른쪽 하나라 1이에요.', 'output')
      .say('조심하세요. &&를 쓰면 자리마다 비교하지 않고 참 거짓만 봐요. 12와 10이면 & 결과는 8인데 &&는 1이에요.', 'code:flags & mask'))

b10 = C_HEAD + '''    // 두 재고 값이에요. 둘 다 0이 아니면 포장할 수 있어요.
    int a = 2;
    int b = 1;
    // 이 줄을 고쳐 두 값이 모두 0이 아닌지 논리 AND로 판단하세요.
    int both = a & b;
    printf("%d\\n", both);
''' + C_END
n10 = (Script(b10)
       .say('두 값이 모두 0이 아닌지 판단해야 해요. 자리별 & 대신 논리 AND &&를 써요.', 'text:both 줄을 고쳐 두 값이 모두 0이 아닌지 논리 AND로 판단하세요.')
       .run('printf("%d\\n", both);')
       .say('0이에요. 2는 10, 1은 01이라 같은 자리에 함께 켜진 1이 없어요.', 'output')
       .patch('    int both = a & b;\n', '    int both = a && b;\n', '&를 &&로 바꿔요.')
       .run('printf("%d\\n", both);')
       .say('1이에요. 두 값이 모두 0이 아니라서 참 1이에요.', 'output')
       .say('조심하세요. 둘 다 0이 아닌데 &는 0이 될 수 있어요. 조건 판단에는 &&를 써요.', 'code:a && b'))

b11 = C_HEAD + '''    // 켜진 표시 5(101)에 새 표시 2(010)를 더 켜요.
    unsigned int flags = 5u;
    unsigned int extra = 2u;
    // 이 줄을 고쳐 두 값 중 하나라도 1인 자리를 모두 켜세요.
    unsigned int value = flags;
    printf("%u\\n", value);
''' + C_END
n11 = (Script(b11)
       .say('두 값의 켜진 자리를 합쳐야 해요. 비트 OR 연산자 |를 써요.', 'text:value 줄을 고쳐 두 값 중 하나라도 1인 자리를 모두 켜세요.')
       .run('printf("%u\\n", value);')
       .say('5예요. 아직 새 표시를 합치지 않았어요.', 'output')
       .patch('    unsigned int value = flags;\n', '    unsigned int value = flags | extra;\n', 'flags 뒤에 | extra를 더해요.')
       .run('printf("%u\\n", value);')
       .say('7이에요. 101과 010을 합쳐 111이 됐어요.', 'output')
       .say('조심하세요. 지금은 +로 더해도 7이지만, 6과 3처럼 겹치는 자리가 있으면 +는 9, |는 7이에요.', 'code:flags | extra'))

b12 = C_HEAD + '''    // 어제 표시 5(101)와 오늘 표시 3(011)이에요.
    unsigned int before = 5u;
    unsigned int after = 3u;
    // 이 줄을 고쳐 두 값의 서로 다른 자리만 1로 남기세요.
    unsigned int changed = before | after;
    printf("%u\\n", changed);
''' + C_END
n12 = (Script(b12)
       .say('어제와 오늘 표시 중 바뀐 자리만 남겨야 해요. 비트 XOR 연산자 ^를 써요.', 'text:changed 줄을 고쳐 두 값의 서로 다른 자리만 1로 남기세요.')
       .run('printf("%u\\n", changed);')
       .say('7이에요. |는 같은 자리의 1도 남겨서 바뀌지 않은 자리까지 켜졌어요.', 'output')
       .patch('before | after', 'before ^ after', '|를 ^로 바꿔요.')
       .run('printf("%u\\n", changed);')
       .say('6이에요. 101과 011이 다른 자리는 왼쪽 두 자리라 110, 6이에요.', 'output')
       .say('조심하세요. 두 값이 같으면 XOR은 0이에요. 바뀐 자리가 없다는 뜻이에요.', 'code:before ^ after'))

b13 = C_HEAD + '''    // 표시 1을 왼쪽으로 places 자리만큼 옮기려 해요.
    unsigned int base = 1u;
    int places = 3;
    // 이 줄을 고쳐 base의 비트를 왼쪽으로 places 자리 옮기세요.
    unsigned int value = base * places;
    printf("%u\\n", value);
''' + C_END
n13 = (Script(b13)
       .say('비트를 왼쪽으로 places 자리 옮겨야 해요. 왼쪽 시프트 <<를 써요.', 'text:value 줄을 고쳐 base의 비트를 왼쪽으로 places 자리 옮기세요.')
       .run('printf("%u\\n", value);')
       .say('3이에요. 곱하기는 자리를 옮기지 않아요.', 'output')
       .patch('base * places', 'base << places', '*를 <<로 바꿔요.')
       .run('printf("%u\\n", value);')
       .say('8이에요. 1이 세 자리 옮겨 1000이 됐어요. 한 자리마다 2배예요.', 'output')
       .say('조심하세요. 세 자리 옮기면 3배가 아니라 2를 세 번 곱한 8배예요.', 'code:base << places'))

b14 = C_HEAD + '''    // 네 개의 표시 중 5(0101)가 켜져 있어요. mask 15는 아래 네 비트(1111)예요.
    unsigned int flags = 5u;
    unsigned int mask = 15u;
    // 이 줄을 고쳐 flags를 반전한 뒤 mask로 아래 네 비트만 남기세요.
    unsigned int value = ~flags;
    printf("%u\\n", value);
''' + C_END
n14 = (Script(b14)
       .say('꺼진 표시를 찾으려 반전해요. 반전한 뒤 아래 네 비트만 남기도록 mask를 &로 걸어야 해요.', 'text:value 줄을 고쳐 flags를 반전한 뒤 mask로 아래 네 비트만 남기세요.')
       .run('printf("%u\\n", value);')
       .say('4294967290이에요. unsigned 32비트의 앞자리까지 모두 1로 뒤집혔어요.', 'output')
       .patch('    unsigned int value = ~flags;\n', '    unsigned int value = (~flags) & mask;\n', '~flags를 괄호로 묶고 & mask를 더해요.')
       .run('printf("%u\\n", value);')
       .say('10이에요. 0101을 뒤집은 1010만 남았어요.', 'output')
       .say('조심하세요. 마스크 없이 반전하면 앞의 28비트도 1이 돼 엄청 큰 수가 나와요.', 'code:(~flags) & mask'))

b15 = C_HEAP + '''    // 저장할 재고예요.
    int stock = 7;
    // 정수 한 개의 공간을 확보해요. 확보만 할 뿐 값은 채우지 않아요.
    int *p = malloc(sizeof *p);
    if (p == NULL) return 1;
    // 이 줄을 고쳐 p가 가리키는 저장소에 stock을 저장하세요.
    *p = 0;
    printf("%d\\n", *p);
    free(p);
''' + C_END
n15 = (Script(b15)
       .say('malloc은 공간만 확보해요. 읽기 전에 p가 가리키는 저장소에 stock을 저장해야 해요.', 'text:*p 줄을 고쳐 p가 가리키는 저장소에 stock을 저장하세요.')
       .run('printf("%d\\n", *p);')
       .say('0이에요. 지금은 자리 표시로 0을 저장했어요.', 'output')
       .patch('    *p = 0;\n', '    *p = stock;\n', '0을 stock으로 바꿔요.')
       .run('printf("%d\\n", *p);')
       .say('7이에요. 확보한 저장소에 재고 7을 저장한 뒤 읽었어요.', 'output')
       .say('조심하세요. *p = stock; 없이 바로 읽으면 malloc이 채우지 않은 값을 읽어요. 실행할 때마다 다를 수 있어요.', 'code:*p = stock;'))

b16 = C_HEAP + '''    // 정수 칸 count개를 확보하고 둘째 칸에만 bonus를 더해요.
    int count = 3;
    int bonus = 4;
    // 이 줄을 고쳐 count개의 정수 칸을 모두 0으로 채워 확보하세요.
    int *p = NULL;
    if (p == NULL) {
        printf("확보하지 못했어요\\n");
        return 0;
    }
    p[1] += bonus;
    // 모든 칸을 더해요. 다른 칸이 0이면 합계는 bonus예요.
    int total = 0;
    for (int i = 0; i < count; i++) total += p[i];
    printf("%d %d\\n", p[1], total);
    free(p);
''' + C_END
n16 = (Script(b16)
       .say('count개의 칸을 0으로 채워 확보해야 해요. calloc(개수, 크기)를 써요.', 'text:p 줄을 고쳐 count개의 정수 칸을 모두 0으로 채워 확보하세요.')
       .run('printf("%d %d\\n", p[1], total);')
       .say('확보하지 못했어요가 나와요. p가 NULL이라 칸을 쓰기 전에 멈췄어요.', 'output')
       .patch('    int *p = NULL;\n', '    int *p = calloc(count, sizeof *p);\n', 'NULL을 calloc(count, sizeof *p)로 바꿔요.')
       .run('printf("%d %d\\n", p[1], total);')
       .say('4 4예요. 둘째 칸만 4가 됐고 나머지 칸은 0이라 합계도 4예요.', 'output')
       .say('조심하세요. malloc으로 바꾸면 칸이 0으로 시작한다는 보장이 없어요. p[1] += bonus도 모르는 값에 더해요.', 'code:calloc(count, sizeof *p)'))

b17 = C_HEAP + '''    int value = 9;
    int *p = malloc(sizeof *p);
    if (p == NULL) return 1;
    *p = 0;
    int other = 0;
    // 이 줄을 고쳐 q가 p와 같은 저장소를 가리키게 하세요.
    int *q = &other;
    // q로 쓴 값을 p로 읽어요.
    *q = value;
    printf("%d\\n", *p);
    free(p);
''' + C_END
n17 = (Script(b17)
       .say('q로 쓴 값을 p로 읽으려 해요. q가 p와 같은 저장소를 가리키도록 주소를 복사해야 해요.', 'text:q 줄을 고쳐 q가 p와 같은 저장소를 가리키게 하세요.')
       .run('printf("%d\\n", *p);')
       .say('0이에요. q는 other를 가리켜서 9가 other에 저장됐어요.', 'output')
       .patch('    int *q = &other;\n', '    int *q = p;\n', '&other를 p로 바꿔요.')
       .run('printf("%d\\n", *p);')
       .say('9예요. q와 p가 같은 저장소를 가리켜 q로 쓴 값을 p로 읽었어요.', 'output')
       .say('조심하세요. 별칭이 둘이어도 저장소는 하나예요. free는 한 번만 해요.', 'code:int *q = p;'))

b18 = C_HEAP + '''    // 같은 할당을 가리키는 별칭을 count개 만들어요.
    int count = 3;
    int *p = malloc(sizeof *p);
    if (p == NULL) return 1;
    *p = 3;
    int *alias[4];
    for (int i = 0; i < count; i++) alias[i] = p;
    // 저장소의 수명은 여기서 끝나요.
    free(p);
    p = NULL;
    // 이 줄을 고쳐 별칭 count개를 모두 NULL로 비우세요.
    alias[0] = NULL;
    // NULL로 비운 별칭의 수를 세요.
    int cleared = 0;
    for (int i = 0; i < count; i++) cleared += alias[i] == NULL;
    printf("%d %d\\n", p == NULL, cleared);
''' + C_END
n18 = (Script(b18)
       .say('free 뒤에는 그 할당을 가리키는 모든 별칭이 쓸 수 없는 주소를 갖고 있어요. 별칭 count개를 모두 비워야 해요.', 'text:alias[0] 줄을 고쳐 별칭 count개를 모두 NULL로 비우세요.')
       .run('printf("%d %d\\n", p == NULL, cleared);')
       .say('1 1이에요. p와 첫 별칭만 비웠고 나머지 두 별칭은 해제된 주소를 그대로 갖고 있어요.', 'output')
       .patch('    alias[0] = NULL;\n', '    for (int i = 0; i < count; i++) alias[i] = NULL;\n', '반복문으로 별칭 count개를 모두 NULL로 바꿔요.')
       .run('printf("%d %d\\n", p == NULL, cleared);')
       .say('1 3이에요. 별칭 세 개를 모두 비웠어요.', 'output')
       .say('조심하세요. p = NULL은 p만 바꿔요. 같은 주소를 복사한 다른 포인터는 따로 비워야 해요.', 'code:alias[i] = NULL;'))

SPECS += [
    bit_step('stp_da803331-6926-4d74-a1d9-8f8500674931', 'flags & mask로 같은 자리의 공통 비트를 남기세요',
             '비트 AND가 두 값의 같은 자리가 모두 1인 비트만 남기는 것을 써서 확인해요.',
             'value = 0u를 flags & mask로 고쳐 101과 011의 공통 비트 1을 확인한다. 채점은 다른 비트 값으로 실행해 &&와 구별한다.',
             '2진수는 오른쪽 자리부터 1, 2, 4, 8을 나타내요. 5는 101, 3은 011이에요. 비트 AND(&)는 두 값의 같은 자리가 모두 1인 자리만 1로 남겨요.',
             'value 줄을 고쳐 flags와 mask의 같은 자리가 모두 1인 비트만 남기세요. 채점은 다른 비트 값으로도 실행해요.',
             '`0u`를 `flags & mask`로 고치세요.', b9, 'unsigned int value = flags & mask;\n', 'unsigned int value = 0u;\n',
             '// &는 자리마다 비교해 둘 다 1인 비트만 남겨요.\n    ', n9, '1',
             [{'values': {'flags': '12u', 'mask': '10u'}, 'expected': '8'}, {'values': {'flags': '7u', 'mask': '2u'}, 'expected': '2'}],
             {n9.actions[-1]['text']: '실제 연산 결과로 흔한 실수를 짚어요.'},
             [([['flags & mask;', 'flags && mask;']], 'Logical AND'), ([['flags & mask;', '1u;']], 'Typing the result')],
             [([['flags & mask;', 'mask & flags;']], 'Operands swapped')]),
    bit_step('stp_0abc1f21-07ab-4694-bd02-223bae8e6977', 'a && b로 두 값이 모두 0이 아닌지 판단하세요',
             '논리 AND는 자리별 비교 없이 두 값이 모두 0이 아닌지만 판단함을 써서 확인해요.',
             'a & b는 2와 1의 공통 비트가 없어 0이다. a && b로 고쳐 참 1을 확인한다. 채점은 0이 섞인 값과 공통 비트 없는 값으로 실행한다.',
             '이번에는 두 재고가 모두 있는지 판단해요. 논리 AND(&&)는 두 값이 모두 0이 아니면 참 1, 하나라도 0이면 거짓 0을 돌려줘요. 자리마다 비교하지 않아요.',
             'both 줄을 고쳐 두 값이 모두 0이 아닌지 논리 AND로 판단하세요. 채점은 다른 값으로도 실행해요.',
             '`a & b`를 `a && b`로 고치세요.', b10, 'int both = a && b;\n', 'int both = a & b;\n',
             '// &&는 두 값이 모두 0이 아니면 1, 아니면 0이에요.\n    ', n10, '1',
             [{'values': {'a': '0', 'b': '5'}, 'expected': '0'}, {'values': {'a': '4', 'b': '8'}, 'expected': '1'}],
             {n10.actions[-1]['text']: '실제 출력으로 확인한 흔한 실수예요.'},
             [([['a && b;', 'a & b;']], 'Bitwise AND'), ([['a && b;', '1;']], 'Typing true')],
             [([['a && b;', '(a != 0) && (b != 0);']], 'Explicit comparisons')]),
    bit_step('stp_dbdc3cbb-64aa-4b43-9616-d245f5a8aa75', 'flags | extra로 켜진 자리를 합치세요',
             '비트 OR가 두 값의 같은 자리 중 하나라도 1이면 켜는 것을 써서 확인해요.',
             'value = flags는 5다. flags | extra로 고쳐 101과 010을 합친 7을 확인한다. 채점은 겹치는 자리가 있는 값으로 실행해 +와 구별한다.',
             '켜진 표시 5(101)에 새 표시 2(010)를 더 켜요. 비트 OR(|)는 같은 자리 중 하나라도 1이면 1로 남겨요.',
             'value 줄을 고쳐 두 값 중 하나라도 1인 자리를 모두 켜세요. 채점은 다른 비트 값으로도 실행해요.',
             '`flags`를 `flags | extra`로 고치세요.', b11, 'unsigned int value = flags | extra;\n', 'unsigned int value = flags;\n',
             '// |는 같은 자리 중 하나라도 1이면 1이에요. 이미 켜진 자리는 그대로예요.\n    ', n11, '7',
             [{'values': {'flags': '6u', 'extra': '3u'}, 'expected': '7'}, {'values': {'flags': '8u', 'extra': '1u'}, 'expected': '9'}],
             {n11.actions[-1]['text']: '실제 출력이 같아 보이는 경우와 달라지는 경우를 짚어요.'},
             [([['flags | extra;', 'flags + extra;']], 'Adding instead'), ([['flags | extra;', '7u;']], 'Typing the result')],
             [([['flags | extra;', 'extra | flags;']], 'Operands swapped')]),
    bit_step('stp_f37704d1-d8e1-40fe-93e8-96c481c22983', 'before ^ after로 바뀐 자리만 남기세요',
             '비트 XOR가 두 값의 같은 자리가 다를 때만 1을 남기는 것을 써서 확인해요.',
             'before | after는 같은 자리의 1도 남겨 7이다. before ^ after로 고쳐 바뀐 자리 110, 6을 확인한다. 채점은 다른 값과 같은 두 값으로 실행한다.',
             '어제 표시 5(101)와 오늘 표시 3(011)에서 바뀐 자리를 찾아요. 비트 XOR(^)는 같은 자리가 서로 다르면 1, 같으면 0으로 남겨요.',
             'changed 줄을 고쳐 두 값의 서로 다른 자리만 1로 남기세요. 채점은 다른 값으로도 실행해요.',
             '`before | after`를 `before ^ after`로 고치세요.', b12, 'unsigned int changed = before ^ after;\n', 'unsigned int changed = before | after;\n',
             '// ^는 같은 자리의 비트가 다를 때만 1이에요. 바뀐 자리만 남아요.\n    ', n12, '6',
             [{'values': {'before': '12u', 'after': '10u'}, 'expected': '6'}, {'values': {'before': '7u', 'after': '7u'}, 'expected': '0'}],
             {n12.actions[-1]['text']: '실제 XOR 결과의 의미를 말해요.'},
             [([['before ^ after;', 'before | after;']], 'OR keeps unchanged bits'), ([['before ^ after;', 'before - after;']], 'Subtracting')],
             [([['before ^ after;', '(before | after) & ~(before & after);']], 'OR without the common bits')]),
    bit_step('stp_b282ba4d-5049-43f9-ae77-7ed91635acaf', 'base << places로 비트를 왼쪽으로 옮기세요',
             '왼쪽 시프트가 한 자리마다 값을 2배로 만드는 것을 써서 확인해요.',
             'base * places는 3이다. base << places로 고쳐 1을 세 자리 옮긴 8을 확인한다. 채점은 다른 값과 자리 수로 실행한다.',
             '왼쪽 시프트(<<)는 비트를 왼쪽으로 옮기고 오른쪽을 0으로 채워요. 한 자리 옮길 때마다 값이 2배가 돼요.',
             'value 줄을 고쳐 base의 비트를 왼쪽으로 places 자리 옮기세요. 채점은 다른 값으로도 실행해요.',
             '`base * places`를 `base << places`로 고치세요.', b13, 'unsigned int value = base << places;\n', 'unsigned int value = base * places;\n',
             '// <<는 비트를 places 자리 왼쪽으로 옮겨요. 한 자리마다 2배예요.\n    ', n13, '8',
             [{'values': {'base': '3u', 'places': '2'}, 'expected': '12'}, {'values': {'base': '5u', 'places': '0'}, 'expected': '5'}],
             {n13.actions[-1]['text']: '실제 시프트 결과로 흔한 오해를 짚어요.'},
             [([['base << places;', 'base * places;']], 'Multiplying by places'), ([['base << places;', 'base << 3;']], 'Typing the places')],
             [([['base << places;', 'base * (1u << places);']], 'Multiplying by two to the places')]),
    bit_step('stp_73085838-4fe3-46ae-8f5a-db60b66a6cff', '(~flags) & mask로 꺼진 아래 네 비트를 읽으세요',
             '반전은 모든 비트를 뒤집으므로 필요한 자리만 마스크로 남겨야 함을 써서 확인해요.',
             '~flags는 32비트 전체가 뒤집혀 4294967290이다. (~flags) & mask로 고쳐 아래 네 비트 1010, 10을 확인한다. 채점은 다른 표시와 마스크로 실행한다.',
             '반전(~)은 모든 비트를 뒤집어요. unsigned 정수는 32비트라 앞자리도 모두 1이 돼요. mask 15(1111)를 &로 걸면 아래 네 비트만 남아요.',
             'value 줄을 고쳐 flags를 반전한 뒤 mask로 아래 네 비트만 남기세요. 채점은 다른 값으로도 실행해요.',
             '`~flags`를 `(~flags) & mask`로 고치세요.', b14, 'unsigned int value = (~flags) & mask;\n', 'unsigned int value = ~flags;\n',
             '// 반전하면 앞의 비트까지 1이 돼요. mask로 필요한 아래 비트만 남겨요.\n    ', n14, '10',
             [{'values': {'flags': '0u'}, 'expected': '15'}, {'values': {'flags': '9u', 'mask': '7u'}, 'expected': '6'}],
             {n14.actions[-1]['text']: '실제 출력으로 확인한 마스크의 필요성이에요.'},
             [([['(~flags) & mask;', '~flags;']], 'No mask'), ([['(~flags) & mask;', 'mask - flags;']], 'Subtracting from the mask'),
              ([['(~flags) & mask;', 'flags ^ mask;']], 'XOR with the mask differs once flags has bits outside the mask (9u, 7u)')],
             [([['(~flags) & mask;', 'mask & ~flags;']], 'Mask first, without parentheses')]),
    dict(old='stp_aec61cad-840d-4ef4-82b2-0dfdcd538eca', title='*p = stock으로 확보한 저장소에 값을 저장하세요',
         objectives=['malloc은 저장소를 확보만 하므로 읽기 전에 값을 저장해야 함을 써서 확인해요.'],
         core_flow='*p = 0 자리를 *p = stock으로 고쳐 확보한 저장소에 7을 저장하고 읽는다. 채점은 다른 재고 값으로 실행한다.',
         goal='malloc은 저장소를 확보만 하고 값은 채우지 않아요. 실패하면 NULL을 돌려주니 먼저 확인하고, 값을 저장한 뒤에 읽어요.\n\n'
              '*p 줄을 고쳐 p가 가리키는 저장소에 stock을 저장하세요. 채점은 다른 재고 값으로도 실행해요.\n\n'
              + todo(RUN_C, '`*p = 0;`을 `*p = stock;`으로 고치세요.', '코드 실행을 눌러 7이 나오는지 확인하세요.', SUB_C),
         starter_code=b15, solution=b15.replace('    *p = 0;\n', '    // 확보한 저장소에 값을 먼저 저장해요. 그 뒤에야 *p를 읽을 수 있어요.\n    *p = stock;\n'),
         tests=[{'input': '', 'expected': '7'}],
         variations=[{'values': {'stock': '12'}, 'expected': '12'}, {'values': {'stock': '-3'}, 'expected': '-3'}],
         narration=n15.actions, review={n15.actions[-1]['text']: '초기화하지 않은 저장소를 읽는 실제 위험을 말해요.'},
         reject=[([['    *p = stock;\n', '    *p = 7;\n']], 'Typing the value'), ([['    *p = stock;\n', '    stock = *p;\n']], 'Assigning the other way')],
         accept=[([['    *p = stock;\n', '    p[0] = stock;\n']], 'Index form')]),
    dict(old='stp_ed61deb4-523d-40be-8f31-41e520fe9fb2', title='calloc(count, sizeof *p)로 0으로 채운 칸을 확보하세요',
         objectives=['calloc이 저장소를 확보하면서 모든 칸을 0으로 채우는 것을 써서 확인해요.'],
         core_flow='p = NULL이면 확보하지 못했다는 안내만 나온다. calloc(count, sizeof *p)로 고쳐 둘째 칸만 bonus인 4 4를 확인한다. 채점은 다른 개수와 bonus로 실행한다.',
         goal='calloc(개수, 크기)은 저장소를 확보하면서 모든 바이트를 0으로 채워요. 그래서 정수 칸은 0으로 시작해요. 이번 코드는 둘째 칸에만 bonus를 더한 뒤 모든 칸을 더해요.\n\n'
              'p 줄을 고쳐 count개의 정수 칸을 모두 0으로 채워 확보하세요. 채점은 다른 개수와 bonus로도 실행해요.\n\n'
              + todo('코드 실행을 눌러 확보하지 못했다는 안내가 나오는지 확인하세요.', '`int *p = NULL;`을 `int *p = calloc(count, sizeof *p);`로 고치세요.', '코드 실행을 눌러 4 4가 나오는지 확인하세요.', SUB_C),
         starter_code=b16, solution=b16.replace('    int *p = NULL;\n', '    // calloc은 count개의 칸을 확보하고 모두 0으로 채워요.\n    int *p = calloc(count, sizeof *p);\n'),
         tests=[{'input': '', 'expected': '4 4'}],
         variations=[{'values': {'count': '5', 'bonus': '9'}, 'expected': '9 9'}, {'values': {'count': '2', 'bonus': '-1'}, 'expected': '-1 -1'}],
         narration=n16.actions, review={n16.actions[-1]['text']: 'malloc과 calloc의 실제 차이를 말해요.'},
         reject=[([['    int *p = calloc(count, sizeof *p);\n', '    int *p = NULL;\n']], 'Never allocating'),
                 ([['    printf("%d %d\\n", p[1], total);\n', '    printf("4 4\\n");\n']], 'Typing the output')],
         accept=[([['    int *p = calloc(count, sizeof *p);\n', '    int *p = calloc(count, sizeof(int));\n']], 'sizeof(int)')]),
    dict(old='stp_0fc0aa15-ca6d-4174-bfce-f7b510c386c6', title='int *q = p로 같은 할당의 별칭을 만드세요',
         objectives=['포인터를 복사하면 새 저장소가 아니라 같은 주소를 가리키는 별칭이 됨을 써서 확인해요.'],
         core_flow='q가 other를 가리키면 *p는 0이다. int *q = p로 고쳐 q로 쓴 9를 p로 읽는다. 채점은 다른 값으로 실행한다.',
         goal='`int *q = p;`는 새 저장소를 만들지 않고 p의 주소를 복사해요. 그래서 q로 쓴 값을 p로 읽어요.\n\n'
              'q 줄을 고쳐 q가 p와 같은 저장소를 가리키게 하세요. 채점은 다른 값으로도 실행해요.\n\n'
              + todo(RUN_C, '`int *q = &other;`를 `int *q = p;`로 고치세요.', '코드 실행을 눌러 9가 나오는지 확인하세요.', SUB_C),
         starter_code=b17, solution=b17.replace('    int *q = &other;\n', '    // 포인터를 복사하면 같은 주소를 가리켜요. q와 p는 같은 저장소의 두 이름이에요.\n    int *q = p;\n'),
         tests=[{'input': '', 'expected': '9'}],
         variations=[{'values': {'value': '4'}, 'expected': '4'}, {'values': {'value': '-8'}, 'expected': '-8'}],
         narration=n17.actions, review={n17.actions[-1]['text']: '별칭과 해제 횟수의 실제 관계를 말해요.'},
         reject=[([['    int *q = p;\n', '    int *q = &other;\n']], 'Another variable'), ([['    printf("%d\\n", *p);\n', '    printf("9\\n");\n']], 'Typing the value')],
         accept=[([['    int *q = p;\n', '    int *q = &*p;\n']], 'Address of the pointed storage')]),
    dict(old='stp_d867bd24-fc5a-4133-9f9d-0f1825167574', title='free 뒤 같은 할당의 별칭을 모두 NULL로 바꾸세요',
         objectives=['p = NULL은 p만 바꾸므로 같은 주소를 복사한 별칭도 따로 비워야 함을 써서 확인해요.'],
         core_flow='alias[0]만 비우면 1 1이다. 반복문으로 별칭 count개를 모두 NULL로 바꿔 1 3을 확인한다. 채점은 다른 별칭 개수로 실행한다.',
         goal='free(p) 뒤에 p = NULL;로 p만 비웠어요. 해제 전에 같은 주소를 복사한 별칭들은 여전히 해제된 주소를 갖고 있어요. ==는 같으면 1, 다르면 0이에요.\n\n'
              'alias[0] 줄을 고쳐 별칭 count개를 모두 NULL로 비우세요. 채점은 다른 별칭 개수로도 실행해요.\n\n'
              + todo(RUN_C, '`alias[0] = NULL;`을 `for (int i = 0; i < count; i++) alias[i] = NULL;`로 고치세요.', '코드 실행을 눌러 1 3이 나오는지 확인하세요.', SUB_C),
         starter_code=b18, solution=b18.replace('    alias[0] = NULL;\n', '    // 같은 주소를 복사한 별칭마다 따로 NULL을 넣어야 해요.\n    for (int i = 0; i < count; i++) alias[i] = NULL;\n'),
         tests=[{'input': '', 'expected': '1 3'}],
         variations=[{'values': {'count': '2'}, 'expected': '1 2'}, {'values': {'count': '4'}, 'expected': '1 4'}],
         narration=n18.actions, review={n18.actions[-1]['text']: '해제 뒤 별칭의 실제 상태를 말해요.'},
         reject=[([['    for (int i = 0; i < count; i++) alias[i] = NULL;\n', '    alias[0] = NULL;\n']], 'Only the first alias'),
                 ([['    for (int i = 0; i < count; i++) alias[i] = NULL;\n', '    for (int i = 0; i < 3; i++) alias[i] = NULL;\n']], 'Typing three aliases')],
         accept=[([['    for (int i = 0; i < count; i++) alias[i] = NULL;\n', '    int i = 0;\n    while (i < count) {\n        alias[i] = NULL;\n        i++;\n    }\n']], 'while loop')]),
]
