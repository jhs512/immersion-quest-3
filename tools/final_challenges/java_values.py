"""java-values final challenge: print each quantity with its unit, then the total (beginner).

2026-10-30 redesign (user: 「마지막 문제는 … 이것만 봐서는 뭘하라는건지 모르겠어 문제 자체를 바꾸자」).
The earlier challenge (stp_4c1b8f0e…, revision 8: a total line plus a re-stored quantity line) asked for two
abstract outcomes in one sentence. This one is a single shop situation with the three result lines shown
up front, one print statement per line, and only what steps 1–9 taught: int variables, println, "글자" + 값,
+ "개" and parentheses so the numbers add before they join the text. It is a new step with a new code, so
passes of the old challenge stay with revision 8.
"""
STARTER = '''void main() {
    // 장바구니에 담은 우유와 빵의 수량이에요.
    int milk = 2;
    int bread = 3;
    // 이 주석 아래에 세 줄을 출력하는 출력문 세 개를 쓰세요.
}
'''
PLACEHOLDER = '    // 이 주석 아래에 세 줄을 출력하는 출력문 세 개를 쓰세요.'
MILK = '''    // 글자 뒤에 우유 수량과 단위를 붙여 출력해요.
    System.out.println("우유: " + milk + "개");'''
BREAD = '''    // 빵 수량도 같은 모양으로 출력해요.
    System.out.println("빵: " + bread + "개");'''
TOTAL = '''    // 괄호로 두 수량을 먼저 더한 뒤 글자와 단위를 붙여요.
    System.out.println("합계: " + (milk + bread) + "개");'''
SOLUTION = STARTER.replace(PLACEHOLDER, MILK + '\n' + BREAD + '\n' + TOTAL)
STEP = 'stp_a802a18d-6f68-41cf-8655-f0e62134c57b'
TITLE = '우유·빵 수량과 합계를 세 줄로 출력하세요'

SPEC = dict(
    key='java-values', course='java', revision='java-values-9',
    reason='한 장바구니 상황에서 저장한 값 출력·글자와 단위 붙이기·괄호로 먼저 더하기를 직접 조합해, 보여 준 세 줄과 같은 결과를 만들고 두 수량을 바꿔 다시 실행해 외운 값이 아닌지 확인하는 마지막 도전이에요.',
    grading='세 줄 출력을 실제 JDK로 채점하고 두 수량을 다른 값으로 바꿔 다시 실행해요. 괄호를 빠뜨린 연결(합계: 23개), 합계 숫자 직접 쓰기, 단위 빠뜨리기는 실패해요.',
    unit=dict(id='unt_8a3f2c71-5b94-4e0d-a6c8-2f1e9d47b305', title='마지막 도전',
              objectives=['앞에서 익힌 출력·글자 붙이기·괄호를 한 문제에서 함께 써요.'],
              premise='같은 장바구니예요. 이번에는 쓸 코드를 알려 주지 않고 나와야 할 세 줄만 보여 줘요.'),
    step=dict(id=STEP, title=TITLE,
              objectives=['저장한 두 수량으로 각 수량과 합계를 단위와 함께 출력해요.'],
              core_flow='준비 코드에는 milk와 bread 두 값만 있다. 학생은 출력문 세 개를 직접 쓴다. '
                        '첫 줄과 둘째 줄은 글자 뒤에 각 수량과 개를 붙이고, 셋째 줄은 괄호로 두 수량을 먼저 더한 합계 뒤에 개를 붙인다. '
                        '채점: 실제 JDK 출력, 두 수량을 바꾼 재실행. 괄호 없는 연결은 합계: 23개가 되어 실패한다.'),
    task=dict(
        id=STEP, title=TITLE, language='java',
        goal=('자, 마지막 도전이에요. 장바구니에 우유 milk개와 빵 bread개를 담았어요. 준비 코드에는 두 수량만 있어요.\n\n'
              '결과 창에 아래 세 줄이 나오게 출력문을 쓰세요. 숫자는 직접 적지 말고 milk와 bread에서 가져와요. '
              '채점은 두 수량을 다른 값으로 바꿔서도 실행해요.\n\n'
              '```text\n우유: 2개\n빵: 3개\n합계: 5개\n```\n\n'
              '**할 일**\n\n'
              '1. 코드 실행 버튼을 눌러 아직 아무것도 나오지 않는 것을 확인하세요.\n'
              '2. milk로 첫 줄 `우유: 2개`를 출력하는 출력문을 쓰세요.\n'
              '3. bread로 둘째 줄 `빵: 3개`를 출력하는 출력문을 쓰세요.\n'
              '4. 두 수량을 더한 셋째 줄 `합계: 5개`를 출력하는 출력문을 쓰세요.\n'
              '5. 코드 실행 버튼을 눌러 세 줄이 위 결과와 같은지 확인하세요.\n'
              '6. 수정한 코드를 제출하세요.'),
        starter_code=STARTER, solution=SOLUTION,
        tests=[dict(input='', expected='우유: 2개\n빵: 3개\n합계: 5개')],
        required=True,
        variations=[dict(values=dict(milk='7', bread='2'), expected='우유: 7개\n빵: 2개\n합계: 9개'),
                    dict(values=dict(milk='10', bread='0'), expected='우유: 10개\n빵: 0개\n합계: 10개')],
        narration=[
            dict(action='say', text='마지막 도전이에요. 나와야 할 세 줄만 정해져 있고 코드는 직접 써요.', target='text:결과 창에 아래 세 줄이 나오게 출력문을 쓰세요.'),
            dict(action='say', text='milk는 우유 2개, bread는 빵 3개예요.', target='code:int bread = 3;'),
            dict(action='run', lines=[3, 4]),
            dict(action='say', text='아무것도 안 나와요. 값만 저장했고 출력문은 아직 없거든요.', target='output'),
            dict(action='patch_code', before=PLACEHOLDER, after=MILK + '\n' + PLACEHOLDER,
                 say='글자 우유: 뒤에 milk를 붙이고, 끝에 개를 붙여요.'),
            dict(action='run', lines=[6, 6]),
            dict(action='say', text='우유: 2개가 나와요. 첫 줄이 맞아요.', target='output'),
            dict(action='patch_code', before=PLACEHOLDER, after=BREAD + '\n' + PLACEHOLDER,
                 say='빵도 같은 모양으로 bread를 붙여요.'),
            dict(action='run', lines=[6, 8]),
            dict(action='say', text='빵: 3개가 둘째 줄로 이어서 나와요.', target='output'),
            dict(action='say', text='셋째 줄은 합계: 5개예요. 숫자 덧셈을 글자보다 먼저 해야 해요.', target='text:합계: 5개#1'),
            dict(action='patch_code', before=PLACEHOLDER, after=TOTAL,
                 say='두 수량을 괄호로 묶어 먼저 더하고, 앞뒤에 글자를 붙여요.'),
            dict(action='run', lines=[6, 10]),
            dict(action='say', text='합계: 5개까지 세 줄이 나와요. 괄호 안 2 + 3이 먼저 계산됐어요.', target='output'),
            dict(action='patch_code', before='(milk + bread)', after='milk + bread',
                 say='괄호를 빼면 어떻게 되는지 볼게요.'),
            dict(action='run', lines=[6, 10]),
            dict(action='say', text='셋째 줄이 합계: 23개가 돼요. 글자 뒤에 2와 3을 차례로 이어 붙였어요.', target='output'),
            dict(action='patch_code', before='"합계: " + milk + bread + "개"', after='"합계: " + (milk + bread) + "개"',
                 say='그래서 괄호를 다시 넣어요.'),
            dict(action='say', text='조심하세요. 결과를 보고 5를 직접 적으면 다른 수량으로 채점할 때 틀려요.', target='code:(milk + bread)'),
            dict(action='patch_code', before='int milk = 2;', after='int milk = 7;', say='milk를 7로 바꿔 같은 코드가 통하는지 볼게요.'),
            dict(action='run', lines=[6, 10]),
            dict(action='say', text='우유: 7개, 빵: 3개, 합계: 10개가 나와요. 식이 값을 따라 계산해요.', target='output'),
            dict(action='patch_code', before='int milk = 7;', after='int milk = 2;', say='준비된 수량 2로 되돌려요.'),
            dict(action='run', lines=[6, 10]),
            dict(action='say', text='다시 우유: 2개, 빵: 3개, 합계: 5개예요. 보여 준 세 줄과 같아요.', target='output'),
        ]),
    cases=dict(
        expected_outputs=['', '우유: 2개', '우유: 2개\n빵: 3개', '우유: 2개\n빵: 3개\n합계: 5개',
                          '우유: 2개\n빵: 3개\n합계: 23개', '우유: 7개\n빵: 3개\n합계: 10개', '우유: 2개\n빵: 3개\n합계: 5개'],
        reject=[([['(milk + bread)', 'milk + bread']], 'Without parentheses the text joins 2 and 3 into 23'),
                ([['(milk + bread)', '5']], 'A memorized total fails the changed quantities'),
                ([['"우유: " + milk + "개"', '"우유: 2개"']], 'A memorized first line fails the changed quantities'),
                ([['"빵: " + bread + "개"', '"빵: " + bread']], 'The unit 개 is part of the required line')],
        accept=[([['(milk + bread)', '(bread + milk)']], 'Addition order does not matter'),
                ([['System.out.println("합계: " + (milk + bread) + "개");', 'int total = milk + bread;\n    System.out.println("합계: " + total + "개");']],
                 'Storing the total in a variable first prints the same line')]),
    review={'조심하세요. 결과를 보고 5를 직접 적으면 다른 수량으로 채점할 때 틀려요.':
            '이 문제에서 실제로 하기 쉬운 실수(실행 결과의 숫자를 그대로 적기)와 결과(바꾼 수량 채점 실패)를 말해요. 채점의 variations와 맞아요.'},
)
