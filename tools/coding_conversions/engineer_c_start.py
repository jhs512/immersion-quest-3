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
