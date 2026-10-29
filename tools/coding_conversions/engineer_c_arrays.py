"""engineer-c-arrays: 8 answer-picking steps -> coding steps (2026-10-29)."""
from _kit import Script, todo

PRD_SCOPE = ['두 챕터·두 단원·열한 스텝으로 같은 창고 재고와 표시를 다뤄요.',
             '배열 위치·개수·위치 이동·for와 while 합계·초기화 위치·빈 자료·널 종료 문자열을 한두 줄씩 직접 써서 실행해요.']
PRD_GRADING = ['직접 쓴 코드를 실제 C 컴파일러로 실행해 판정해요.',
               '칸 수·자료를 바꾼 실행도 맞아야 해서 마지막 원소 누락과 고정 출력을 구별해요.',
               '문자 배열의 변경 검사는 한 글자 이상인 널 종료 라벨만 써요.',
               '마지막 도전(stp_23473fd3-7d92-4ed4-bcb7-382927ce49c1): 시작 답안은 실패해야 해요. 실제 실행 결과 또는 각 서술형 답안 칸을 검사하고 오답과 동등한 정답도 대조해요.']
PRD_NARRATION = ['준비 코드를 먼저 실행하고 위치·식·반복 한 곳을 써 넣은 뒤 다시 실행해 결과를 읽어요.',
                 '초기화 위치·개수와 위치·0으로 나누기·문자열 종료의 오해를 친절히 짚어요.',
                 '학생 상태는 보존하고 정확한 줄·실행 버튼·결과를 강조해요.']

HEAD = '#include <stdio.h>\n\nint main(void) {\n    // 같은 창고의 칸별 재고예요.\n    int bins[] = {2, 4, 6};\n'

# ---- 1 ------------------------------------------------------------------------------
s1 = HEAD + '''    // 이 줄을 고쳐 첫 칸의 재고를 담으세요. 배열 위치는 0부터 세어요.
    int first = 0;
    printf("%d", first);
    return 0;
}
'''
s1_solution = s1.replace('    int first = 0;\n', '    // 첫 칸은 위치 0이에요. bins[1]은 둘째 칸이에요.\n    int first = bins[0];\n')
n1 = (Script(s1)
      .say('첫 칸의 재고를 배열 위치로 읽어 first에 담아야 해요.', 'text:first 줄을 고쳐 첫 칸의 재고를 담으세요.')
      .run('printf("%d", first);')
      .say('0이에요. 아직 배열을 읽지 않았어요.', 'output')
      .patch('    int first = 0;\n', '    int first = bins[0];\n', '대괄호 안에 위치 0을 써서 첫 칸을 읽어요.')
      .run('printf("%d", first);')
      .say('2예요. 위치 0에 있는 첫 칸의 재고예요.', 'output')
      .say('조심하세요. bins[1]은 첫 칸이 아니라 둘째 칸 4를 읽어요.', 'code:int first = bins[0];'))

# ---- 2 ------------------------------------------------------------------------------
s2 = HEAD + '''    // 이 줄을 고쳐 전체 저장 크기를 한 원소 크기로 나눠 칸 수를 구하세요.
    int count = 0;
    // 마지막 위치는 개수보다 하나 작아요.
    printf("%d\\n%d", count, count - 1);
    return 0;
}
'''
s2_solution = s2.replace('    int count = 0;\n', '    // sizeof bins는 배열 전체의 바이트 수, sizeof bins[0]은 한 칸의 바이트 수예요.\n    int count = sizeof bins / sizeof bins[0];\n')
n2 = (Script(s2)
      .say('sizeof로 칸 수를 구해 count에 담아야 해요. 숫자를 직접 적지 않아요.', 'text:count 줄을 고쳐 전체 저장 크기를 한 원소 크기로 나눠 칸 수를 구하세요.')
      .run('printf("%d\\n%d", count, count - 1);')
      .say('0과 -1이에요. 아직 칸 수를 구하지 않았어요.', 'output')
      .patch('    int count = 0;\n', '    int count = sizeof bins / sizeof bins[0];\n', '배열 전체 크기를 한 칸 크기로 나눠요.')
      .run('printf("%d\\n%d", count, count - 1);')
      .say('3과 2예요. 칸은 세 개이고 마지막 위치는 2예요.', 'output')
      .say('조심하세요. 칸 수 3은 위치로 쓸 수 없어요. bins[3]은 배열 밖이에요.', 'code:count - 1'))

# ---- 3 ------------------------------------------------------------------------------
s3 = HEAD + '''    // index에는 읽을 위치를 저장해요.
    int index = 0;
    printf("%d\\n", bins[index]);
    // 이 주석 아래에 재고가 아니라 위치 index만 하나 올리는 줄을 쓰세요.
    printf("%d", bins[index]);
    return 0;
}
'''
s3_solution = s3.replace('    // 이 주석 아래에 재고가 아니라 위치 index만 하나 올리는 줄을 쓰세요.\n',
                         '    // 이 주석 아래에 재고가 아니라 위치 index만 하나 올리는 줄을 쓰세요.\n'
                         '    // 위치가 바뀌면 같은 bins[index]가 다음 칸을 읽어요. 칸의 재고는 그대로예요.\n'
                         '    index = index + 1;\n')
n3 = (Script(s3)
      .say('두 번째 출력이 다음 칸을 읽도록 위치 index만 하나 올려야 해요.', 'text:주석 아래에 재고가 아니라 위치 index만 하나 올리는 줄을 쓰세요.')
      .run('printf("%d\\n", bins[index]);', 'printf("%d", bins[index]);')
      .say('2와 2예요. 위치가 그대로라 같은 칸을 두 번 읽었어요.', 'output')
      .patch('    // 이 주석 아래에 재고가 아니라 위치 index만 하나 올리는 줄을 쓰세요.\n',
             '    // 이 주석 아래에 재고가 아니라 위치 index만 하나 올리는 줄을 쓰세요.\n    index = index + 1;\n',
             'index에 1을 더해 다음 위치로 옮겨요.')
      .run('printf("%d\\n", bins[index]);', 'printf("%d", bins[index]);')
      .say('2와 4예요. 같은 bins[index]가 이번에는 위치 1의 칸을 읽었어요.', 'output')
      .say('조심하세요. bins[index] = bins[index] + 2처럼 재고를 바꾸면 지금은 4가 나와도 다른 칸을 읽은 게 아니에요.', 'code:index = index + 1;'))

# ---- 4 ------------------------------------------------------------------------------
s4 = HEAD + '''    // 사용할 칸 수는 실제 저장공간을 넘지 않아요.
    int count = 3;
    int total = 0;
    for (int index = 0; index < count; index = index + 1) {
        // 이 주석 아래에 현재 칸의 재고를 total에 더하는 줄을 쓰세요.
    }
    printf("%d", total);
    return 0;
}
'''
s4_solution = s4.replace('        // 이 주석 아래에 현재 칸의 재고를 total에 더하는 줄을 쓰세요.\n',
                         '        // 이 주석 아래에 현재 칸의 재고를 total에 더하는 줄을 쓰세요.\n'
                         '        // 지금까지의 합에 이번 칸을 더해 다시 저장해요.\n'
                         '        total = total + bins[index];\n')
n4 = (Script(s4)
      .say('반복할 때마다 현재 칸의 재고를 total에 더하는 줄을 써야 해요.', 'text:반복 안의 주석 아래에 현재 칸의 재고를 total에 더하는 줄을 쓰세요.')
      .run('printf("%d", total);')
      .say('0이에요. 반복은 세 번 돌지만 아직 더하는 줄이 없어요.', 'output')
      .patch('        // 이 주석 아래에 현재 칸의 재고를 total에 더하는 줄을 쓰세요.\n',
             '        // 이 주석 아래에 현재 칸의 재고를 total에 더하는 줄을 쓰세요.\n        total = total + bins[index];\n',
             'total에 bins[index]를 더해 다시 total에 저장해요.')
      .run('printf("%d", total);')
      .say('12예요. 2, 4, 6을 차례로 더했어요.', 'output')
      .say('조심하세요. total = bins[index]로 쓰면 더하지 않고 덮어써서 마지막 칸 6만 남아요.', 'code:total = total + bins[index];'))

# ---- 5 ------------------------------------------------------------------------------
s5 = HEAD + '''    // 같은 사용 개수와 합계를 준비해요.
    int count = 3;
    int total = 0;
    int index = 0;
    // 이 주석 아래에 index가 count보다 작을 동안 현재 칸을 더하고 index를 1 올리는 while 문을 쓰세요.
    printf("%d", total);
    return 0;
}
'''
s5_solution = s5.replace('    // 이 주석 아래에 index가 count보다 작을 동안 현재 칸을 더하고 index를 1 올리는 while 문을 쓰세요.\n',
                         '    // 이 주석 아래에 index가 count보다 작을 동안 현재 칸을 더하고 index를 1 올리는 while 문을 쓰세요.\n'
                         '    // while은 조건만 검사해요. 위치를 옮기는 줄을 빼면 반복이 끝나지 않아요.\n'
                         '    while (index < count) {\n        total = total + bins[index];\n        index = index + 1;\n    }\n')
n5 = (Script(s5)
      .say('같은 합계를 while 문으로 구해야 해요. 위치를 옮기는 줄도 직접 써요.', 'text:주석 아래에 index가 count보다 작을 동안 현재 칸을 더하고 index를 1 올리는 while 문을 쓰세요.')
      .run('printf("%d", total);')
      .say('0이에요. 아직 반복이 없어요.', 'output')
      .patch('    // 이 주석 아래에 index가 count보다 작을 동안 현재 칸을 더하고 index를 1 올리는 while 문을 쓰세요.\n',
             '    // 이 주석 아래에 index가 count보다 작을 동안 현재 칸을 더하고 index를 1 올리는 while 문을 쓰세요.\n'
             '    while (index < count) {\n        total = total + bins[index];\n        index = index + 1;\n    }\n',
             'index < count인 동안 현재 칸을 더하고 index를 1 올려요.')
      .run('printf("%d", total);')
      .say('12예요. for 문과 같은 세 칸을 읽었어요.', 'output')
      .say('조심하세요. index = index + 1을 빼면 조건이 계속 참이라 반복이 끝나지 않아요.', 'code:index = index + 1;'))

# ---- 6 ------------------------------------------------------------------------------
s6 = HEAD + '''    // 사용할 칸 수는 실제 저장공간을 넘지 않아요.
    int count = 3;
    int total = 0;
    for (int index = 0; index < count; index = index + 1) {
        // 반복 안에서 합계를 지우는 줄이 있어요. 이 줄을 지우세요.
        total = 0;
        total = total + bins[index];
    }
    printf("%d", total);
    return 0;
}
'''
s6_solution = s6.replace('        // 반복 안에서 합계를 지우는 줄이 있어요. 이 줄을 지우세요.\n        total = 0;\n',
                         '        // 합계는 반복 전에 한 번만 0으로 준비해요. 반복 안에서는 더하기만 해요.\n')
n6 = (Script(s6)
      .say('반복 안에서 합계를 0으로 지우는 줄을 지워야 해요.', 'text:반복 안에서 total을 0으로 바꾸는 줄을 지우세요.')
      .run('printf("%d", total);')
      .say('6이에요. 매번 0으로 지운 뒤 더해서 마지막 칸만 남았어요.', 'output')
      .patch('        total = 0;\n', '', '반복 안의 total = 0; 줄을 지워요.')
      .run('printf("%d", total);')
      .say('12예요. 합계가 반복 사이에 남아 세 칸이 모두 더해졌어요.', 'output')
      .say('조심하세요. 반복 전의 int total = 0;까지 지우면 합계가 준비되지 않은 값에서 시작해요.', 'code:int total = 0;'))

# ---- 7 ------------------------------------------------------------------------------
s7 = HEAD + '''    // 사용할 칸 수는 실제 저장공간을 넘지 않아요. 0일 수도 있어요.
    int count = 3;
    int total = 0;
    for (int index = 0; index < count; index = index + 1) {
        total = total + bins[index];
    }
    int average = 0;
    // 이 주석 아래에 count가 0보다 클 때만 average에 total / count를 담는 if 문을 쓰세요.
    printf("%d\\n%d", total, average);
    return 0;
}
'''
s7_solution = s7.replace('    // 이 주석 아래에 count가 0보다 클 때만 average에 total / count를 담는 if 문을 쓰세요.\n',
                         '    // 이 주석 아래에 count가 0보다 클 때만 average에 total / count를 담는 if 문을 쓰세요.\n'
                         '    // 사용할 칸이 없으면 반복은 한 번도 돌지 않고, 0으로 나누면 안 되니 평균은 0으로 둬요.\n'
                         '    if (count > 0) {\n        average = total / count;\n    }\n')
n7 = (Script(s7)
      .say('사용할 칸이 있을 때만 평균을 계산하는 if 문을 써야 해요.', 'text:주석 아래에 count가 0보다 클 때만 average에 total / count를 담는 if 문을 쓰세요.')
      .run('printf("%d\\n%d", total, average);')
      .say('12와 0이에요. 합계는 구했지만 평균은 아직 계산하지 않았어요.', 'output')
      .patch('    // 이 주석 아래에 count가 0보다 클 때만 average에 total / count를 담는 if 문을 쓰세요.\n',
             '    // 이 주석 아래에 count가 0보다 클 때만 average에 total / count를 담는 if 문을 쓰세요.\n    if (count > 0) {\n        average = total / count;\n    }\n',
             'count > 0일 때만 total을 count로 나눠요.')
      .run('printf("%d\\n%d", total, average);')
      .say('12와 4예요. 세 칸의 평균을 계산했어요.', 'output')
      .patch('    int count = 3;\n', '    int count = 0;\n', '사용할 칸을 0으로 바꿔 볼게요.')
      .run('printf("%d\\n%d", total, average);')
      .say('0과 0이에요. 반복은 한 번도 돌지 않았고 if가 0으로 나누기를 막았어요.', 'output')
      .patch('    int count = 0;\n', '    int count = 3;\n', 'count를 처음 값 3으로 되돌려요.')
      .say('조심하세요. if 없이 total / count를 쓰면 count가 0일 때 0으로 나누어 프로그램이 멈춰요.', 'code:average = total / count;'))

# ---- 8 ------------------------------------------------------------------------------
s8 = '''#include <stdio.h>
#include <string.h>

int main(void) {
    // 여덟 칸을 잡고 BOX를 넣었어요. 글자 뒤에는 끝을 알리는 널 문자가 붙어요.
    char label[8] = "BOX";
    int cells = sizeof label / sizeof label[0];
    // 이 줄을 고쳐 strlen으로 널 문자 앞까지의 글자 수를 구하세요.
    int letters = 0;
    printf("%d\\n%d", cells, letters);
    return 0;
}
'''
s8_solution = s8.replace('    int letters = 0;\n', '    // strlen은 널 문자를 만날 때까지 센 글자 수예요. 저장 칸 수와 달라요.\n    int letters = strlen(label);\n')
n8 = (Script(s8)
      .say('저장 칸 수는 sizeof로 구했어요. 글자 수는 strlen으로 구해야 해요.', 'text:letters 줄을 고쳐 strlen으로 널 문자 앞까지의 글자 수를 구하세요.')
      .run('printf("%d\\n%d", cells, letters);')
      .say('8과 0이에요. 칸은 여덟 개이고 글자 수는 아직 구하지 않았어요.', 'output')
      .patch('    int letters = 0;\n', '    int letters = strlen(label);\n', 'strlen에 label을 넘겨요.')
      .run('printf("%d\\n%d", cells, letters);')
      .say('8과 3이에요. 칸은 여덟 개지만 널 문자 앞의 글자는 B, O, X 세 개예요.', 'output')
      .say('조심하세요. sizeof는 잡아 둔 칸 수라 글자 수가 아니에요. cells - 1도 여기서는 7이에요.', 'code:int cells = sizeof label / sizeof label[0];'))


SPECS = [
    dict(old='stp_0be9cf14-1870-4dff-a6cd-84a56c0fb7c8', title='위치 0으로 첫 칸의 재고를 읽으세요',
         objectives=['배열 위치가 0부터 시작함을 써서 확인해요.'],
         core_flow='bins={2,4,6}에서 first=bins[0]으로 2를 확인한다. bins[1]은 둘째 칸이다. 채점은 bins 자료를 바꿔 실행한다.',
         goal='칸별 재고를 한 배열 bins에 담았어요. 배열의 칸은 `bins[위치]`로 읽고, 위치는 0부터 세어요.\n\n'
              'first 줄을 고쳐 첫 칸의 재고를 담으세요. 채점은 bins의 재고를 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 0이 나오는지 확인하세요.', '`int first = 0;`의 0을 첫 칸을 읽는 `bins[...]`로 바꾸세요.', '코드 실행을 눌러 2가 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s1, solution=s1_solution, tests=[{'input': '', 'expected': '2'}],
         variations=[{'values': {'bins': '{7, 4, 6}'}, 'expected': '7'}, {'values': {'bins': '{0, 1}'}, 'expected': '0'}],
         narration=n1.actions,
         review={'조심하세요. bins[1]은 첫 칸이 아니라 둘째 칸 4를 읽어요.': '실제 흔한 혼동(1부터 세기)과 그 실제 값을 말해요.'},
         reject=[([['    int first = bins[0];\n', '    int first = bins[1];\n']], 'Second cell'),
                 ([['    int first = bins[0];\n', '    int first = 2;\n']], 'Typing the value')],
         accept=[([['    int first = bins[0];\n', '    int first = *bins;\n']], 'Pointer to the first element')]),
    dict(old='stp_e9419774-38c0-4772-98ec-19754f86cca9', title='sizeof로 칸 수를 구해 마지막 위치를 표시하세요',
         objectives=['배열 개수와 마지막 위치를 구별해요.'],
         core_flow='count=sizeof bins / sizeof bins[0]으로 3을 구하고 마지막 위치 count-1인 2를 함께 출력한다. 채점은 칸 수가 다른 bins로 실행한다.',
         goal='칸의 개수와 마지막 위치를 표시해요. `sizeof bins`는 배열 전체의 바이트 수, `sizeof bins[0]`은 한 칸의 바이트 수라서 나누면 칸 수가 나와요. 마지막 위치는 개수보다 하나 작아요.\n\n'
              'count 줄을 고쳐 전체 저장 크기를 한 원소 크기로 나눠 칸 수를 구하세요. 채점은 칸 수가 다른 배열로도 실행해요.\n\n'
              + todo('코드 실행을 눌러 0과 -1이 나오는지 확인하세요.', '`int count = 0;`의 0을 `sizeof bins / sizeof bins[0]`으로 바꾸세요.', '코드 실행을 눌러 3과 2가 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s2, solution=s2_solution, tests=[{'input': '', 'expected': '3\n2'}],
         variations=[{'values': {'bins': '{1, 2, 3, 4, 5}'}, 'expected': '5\n4'}, {'values': {'bins': '{9}'}, 'expected': '1\n0'}],
         narration=n2.actions,
         review={'조심하세요. 칸 수 3은 위치로 쓸 수 없어요. bins[3]은 배열 밖이에요.': '실제 C 범위 규칙(0..n-1)을 정확히 말해요.'},
         reject=[([['    int count = sizeof bins / sizeof bins[0];\n', '    int count = 3;\n']], 'Typing the count'),
                 ([['    int count = sizeof bins / sizeof bins[0];\n', '    int count = sizeof bins;\n']], 'Bytes are not cells')],
         accept=[([['    int count = sizeof bins / sizeof bins[0];\n', '    int count = sizeof(bins) / sizeof(int);\n']], 'Dividing by sizeof(int)')]),
    dict(old='stp_b40eaef2-b5f2-4e31-9726-aaf699bc83d7', title='index만 하나 올려 다음 칸의 재고를 읽으세요',
         objectives=['위치 변수를 바꿔 다음 칸을 읽고 재고는 바꾸지 않아요.'],
         core_flow='index=0으로 bins[index]를 읽은 뒤 index=index+1을 써서 다음 칸 4를 읽는다. 재고를 바꾸는 우회는 다른 자료에서 드러난다. 채점은 bins와 index를 바꿔 실행한다.',
         goal='index에는 읽을 위치를 저장해요. 같은 `bins[index]`라도 index가 바뀌면 다른 칸을 읽어요.\n\n'
              '두 출력 사이의 주석 아래에 재고가 아니라 위치 index만 하나 올리는 줄을 쓰세요. 채점은 bins와 처음 위치를 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 2와 2가 나오는지 확인하세요.', '주석 아래에 `index = index + 1;`을 쓰세요.', '코드 실행을 눌러 2와 4가 나오는지 확인하세요.', '작성한 코드를 제출하세요.'),
         starter_code=s3, solution=s3_solution, tests=[{'input': '', 'expected': '2\n4'}],
         variations=[{'values': {'bins': '{9, 8, 7}'}, 'expected': '9\n8'}, {'values': {'index': '1'}, 'expected': '4\n6'}],
         narration=n3.actions,
         review={'조심하세요. bins[index] = bins[index] + 2처럼 재고를 바꾸면 지금은 4가 나와도 다른 칸을 읽은 게 아니에요.': '실제 우회와 그 한계(다른 자료에서 실패)를 말해요. 「나와도」 대조가 맞아요.'},
         reject=[([['    index = index + 1;\n', '    bins[index] = bins[index] + 2;\n']], 'Changing the stock instead of the position'),
                 ([['    index = index + 1;\n', '    index = 1;\n']], 'Typing position 1')],
         accept=[([['    index = index + 1;\n', '    index++;\n']], 'Increment operator')]),
    dict(old='stp_f611f7a1-b7c2-4ffd-a94b-c1a1c9dae69b', title='for 반복 안에서 칸마다 재고를 total에 더하세요',
         objectives=['반복으로 사용할 칸을 차례로 누적해요.'],
         core_flow='for (index=0; index<count; ...) 안에 total=total+bins[index]를 써서 12를 확인한다. 덮어쓰기 total=bins[index]는 6이다. 채점은 bins와 count를 바꿔 실행한다.',
         goal='사용할 세 칸의 재고를 차례로 더해요. for 문은 index를 0, 1, 2로 바꾸며 중괄호 안을 반복해요.\n\n'
              '반복 안의 주석 아래에 현재 칸의 재고를 total에 더하는 줄을 쓰세요. 채점은 bins와 사용할 칸 수를 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 0이 나오는지 확인하세요.', '반복 안에 `total = total + bins[index];`를 쓰세요.', '코드 실행을 눌러 12가 나오는지 확인하세요.', '작성한 코드를 제출하세요.'),
         starter_code=s4, solution=s4_solution, tests=[{'input': '', 'expected': '12'}],
         variations=[{'values': {'bins': '{5, 1, 9}'}, 'expected': '15'}, {'values': {'count': '2'}, 'expected': '6'}, {'values': {'count': '0'}, 'expected': '0'}],
         narration=n4.actions,
         review={'조심하세요. total = bins[index]로 쓰면 더하지 않고 덮어써서 마지막 칸 6만 남아요.': '실제 흔한 실수와 그 실제 출력을 말해요.'},
         reject=[([['        total = total + bins[index];\n', '        total = bins[index];\n']], 'Overwriting'),
                 ([['        total = total + bins[index];\n', '        total = 12;\n']], 'Typing the total')],
         accept=[([['        total = total + bins[index];\n', '        total += bins[index];\n']], 'Compound assignment')]),
    dict(old='stp_208736a9-7954-44d0-80cc-9a9e90fc56ee', title='같은 합계를 while 문으로 직접 쓰세요',
         objectives=['조건 검사와 위치 이동을 나눠 쓰는 while 반복을 이해해요.'],
         core_flow='index=0에서 while (index < count) 안에 현재 칸을 더하고 index를 1 올려 12를 확인한다. 위치 이동을 빼면 끝나지 않는다. 채점은 bins와 count를 바꿔 실행한다.',
         goal='같은 작업을 while로 표현해요. while은 조건만 검사하므로, 반복 안에서 현재 칸을 더하고 위치 index를 직접 옮겨야 해요.\n\n'
              '주석 아래에 index가 count보다 작을 동안 현재 칸을 더하고 index를 1 올리는 while 문을 쓰세요. 채점은 bins와 사용할 칸 수를 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 0이 나오는지 확인하세요.', '주석 아래에 `while (index < count)`와 중괄호를 쓰세요.', '중괄호 안에 현재 칸을 total에 더하는 줄과 index를 1 올리는 줄을 쓰세요.',
                     '코드 실행을 눌러 12가 나오는지 확인하세요.', '작성한 코드를 제출하세요.'),
         starter_code=s5, solution=s5_solution, tests=[{'input': '', 'expected': '12'}],
         variations=[{'values': {'bins': '{5, 1, 9}'}, 'expected': '15'}, {'values': {'count': '1'}, 'expected': '2'}, {'values': {'count': '0'}, 'expected': '0'}],
         narration=n5.actions,
         review={'조심하세요. index = index + 1을 빼면 조건이 계속 참이라 반복이 끝나지 않아요.': '실제 무한 반복 원인을 정확히 말해요.'},
         reject=[([['        total = total + bins[index];\n        index = index + 1;\n', '        index = index + 1;\n        total = total + bins[index];\n']], 'Moving before reading skips the first cell'),
                 ([['    while (index < count) {\n', '    while (index < 3) {\n']], 'Ignoring count')],
         accept=[([['    while (index < count) {\n        total = total + bins[index];\n        index = index + 1;\n    }\n', '    while (index < count) {\n        total += bins[index++];\n    }\n']], 'Post-increment inside the index')]),
    dict(old='stp_c2dc6627-81bf-4d6e-a893-a81f166d0e8f', title='반복 안에서 합계를 지우는 줄을 지우세요',
         objectives=['누적값의 초기화 위치가 반복 밖이어야 함을 고쳐서 확인해요.'],
         core_flow='반복 안의 total=0 때문에 마지막 칸 6만 남는다. 그 줄을 지워 12를 확인한다. 반복 밖의 초기화는 남긴다. 채점은 bins를 바꿔 실행한다.',
         goal='반복 안에서 합계를 자꾸 0으로 바꾸고 있어요. 합계는 반복 전에 한 번만 0으로 준비해야 반복 사이에 값이 남아요.\n\n'
              '반복 안에서 total을 0으로 바꾸는 줄을 지우세요. 반복 전의 `int total = 0;`은 그대로 둬요. 채점은 bins를 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 6이 나오는지 확인하세요.', '반복 안의 `total = 0;` 줄을 지우세요.', '코드 실행을 눌러 12가 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s6, solution=s6_solution, tests=[{'input': '', 'expected': '12'}],
         variations=[{'values': {'bins': '{5, 1, 9}'}, 'expected': '15'}, {'values': {'bins': '{6, 4, 2}'}, 'expected': '12'}],
         narration=n6.actions,
         review={'조심하세요. 반복 전의 int total = 0;까지 지우면 합계가 준비되지 않은 값에서 시작해요.': '실제 C 규칙(초기화하지 않은 지역 변수)을 정확히 말해요.'},
         reject=[([['    printf("%d", total);\n', '    printf("12");\n']], 'Printing typed text')],
         accept=[([['        total = total + bins[index];\n', '        total += bins[index];\n']], 'Compound assignment')]),
    dict(old='stp_af6c17c8-0654-4afc-bea9-5468c8a718f3', title='사용할 칸이 있을 때만 평균을 계산하세요',
         objectives=['빈 자료에서 반복이 한 번도 돌지 않음을 알고 0으로 나누기를 막아요.'],
         core_flow='count=3이면 합계 12, 평균 4다. if (count > 0)로 나눗셈을 감싼다. count=0으로 바꾸면 반복이 돌지 않아 합계 0이고 평균은 0으로 남는다. 채점은 count를 0, 2로 바꿔 실행한다.',
         goal='저장공간은 있어도 지금 사용할 칸 count가 0일 수 있어요. count가 0이면 반복은 한 번도 돌지 않아 합계는 0이고, 0으로 나누면 프로그램이 멈춰요.\n\n'
              '주석 아래에 count가 0보다 클 때만 average에 total / count를 담는 if 문을 쓰세요. 채점은 count를 0으로 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 12와 0이 나오는지 확인하세요.', '주석 아래에 `count > 0`일 때 `average = total / count;`를 실행하는 if 문을 쓰세요.', '코드 실행을 눌러 12와 4가 나오는지 확인하세요.', '작성한 코드를 제출하세요.'),
         starter_code=s7, solution=s7_solution, tests=[{'input': '', 'expected': '12\n4'}],
         variations=[{'values': {'count': '0'}, 'expected': '0\n0'}, {'values': {'count': '2'}, 'expected': '6\n3'}, {'values': {'bins': '{5, 1, 9}'}, 'expected': '15\n5'}],
         narration=n7.actions,
         review={'0과 0이에요. 반복은 한 번도 돌지 않았고 if가 0으로 나누기를 막았어요.': '실제 count=0 실행 결과와 맞아요.',
                 '조심하세요. if 없이 total / count를 쓰면 count가 0일 때 0으로 나누어 프로그램이 멈춰요.': '실제 C 정수 0 나누기(정의되지 않은 동작, 보통 비정상 종료)를 학습자 수준으로 말해요. 채점의 count=0 실행이 이를 확인해요.'},
         reject=[([['    if (count > 0) {\n        average = total / count;\n    }\n', '    average = total / count;\n']], 'No guard'),
                 ([['    if (count > 0) {\n        average = total / count;\n    }\n', '    average = 4;\n']], 'Typing the average')],
         accept=[([['    if (count > 0) {\n        average = total / count;\n    }\n', '    average = count ? total / count : 0;\n']], 'Conditional expression')]),
    dict(old='stp_d4d10fdc-175c-443d-8bca-cd99110f47e9', title='strlen으로 저장 칸 수와 다른 글자 수를 구하세요',
         objectives=['배열 저장 칸 수와 널 문자 앞 글자 수를 구별해요.'],
         core_flow='char label[8]="BOX"에서 cells=sizeof로 8, letters=strlen(label)로 3을 출력한다. sizeof는 칸 수, strlen은 널 문자 앞 글자 수다. 채점은 label 글자를 바꿔 실행한다.',
         goal='창고 표시 BOX를 여덟 칸짜리 문자 배열에 넣었어요. 글자 뒤에는 문자열 끝을 알리는 널 문자가 붙고, 나머지 칸도 비어 있어요. `strlen`은 널 문자 앞까지의 글자 수를 세요.\n\n'
              'letters 줄을 고쳐 strlen으로 널 문자 앞까지의 글자 수를 구하세요. 채점은 표시 글자를 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 8과 0이 나오는지 확인하세요.', '`int letters = 0;`의 0을 `strlen(label)`로 바꾸세요.', '코드 실행을 눌러 8과 3이 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s8, solution=s8_solution, tests=[{'input': '', 'expected': '8\n3'}],
         variations=[{'values': {'label': '"CRATE"'}, 'expected': '8\n5'}, {'values': {'label': '"A"'}, 'expected': '8\n1'}],
         narration=n8.actions,
         review={'조심하세요. sizeof는 잡아 둔 칸 수라 글자 수가 아니에요. cells - 1도 여기서는 7이에요.': '실제 우회(cells - 1)와 이 코드에서의 실제 값(7)을 말해요.'},
         reject=[([['    int letters = strlen(label);\n', '    int letters = cells - 1;\n']], 'Cells minus one'),
                 ([['    int letters = strlen(label);\n', '    int letters = 3;\n']], 'Typing the value')],
         accept=[([['    int letters = strlen(label);\n', '    int letters = 0;\n    while (label[letters] != \'\\0\') letters++;\n']], 'Counting up to the null character')]),
]
