"""java-values final challenge: combine output, concatenation with parentheses and assignment (beginner)."""
STARTER = '''void main() {
    // 장바구니에 이미 담긴 수량과 새로 더 담은 수량이에요.
    int quantity = 2;
    int added = 3;
    // 여기에 합계 출력, 수량 저장, 저장한 수량 출력을 차례로 쓰세요.
}
'''
LINE1 = '''    // 괄호로 두 수량을 먼저 더한 뒤 글자를 붙여요.
    System.out.println("합계: " + (quantity + added) + "개");'''
LINE23 = '''    // 합계를 quantity에 다시 저장해요.
    quantity = quantity + added;
    // 저장한 뒤의 quantity 값을 읽어 출력해요.
    System.out.println("저장한 수량: " + quantity);'''
PLACEHOLDER = '    // 여기에 합계 출력, 수량 저장, 저장한 수량 출력을 차례로 쓰세요.'
SOLUTION = STARTER.replace(PLACEHOLDER, LINE1 + '\n' + LINE23)
STEP = 'stp_4c1b8f0e-6d2a-4f57-9a3e-0b7c5d81e2a4'

SPEC = dict(
    key='java-values', course='java', revision='java-values-8',
    reason='출력·문자열 연결·괄호·대입을 알려 주지 않은 순서로 직접 조합하고, 두 수량을 바꿔 다시 실행해 외운 값이 아닌지 확인하는 마지막 도전이에요.',
    grading='두 줄 출력을 실제 JDK로 채점하고 두 수량을 다른 값으로 바꿔 다시 실행해요. 괄호를 빠뜨린 연결(23개), 값 직접 쓰기, 대입 누락은 실패해요.',
    unit=dict(id='unt_8a3f2c71-5b94-4e0d-a6c8-2f1e9d47b305', title='마지막 도전',
              objectives=['앞에서 익힌 출력·괄호·대입을 한 문제에서 함께 써요.'],
              premise='같은 장바구니예요. 이번에는 쓸 코드를 알려 주지 않고 나와야 할 결과만 보여 줘요.'),
    step=dict(id=STEP, title='합계를 출력하고 저장한 수량도 출력하세요',
              objectives=['덧셈·문자열 연결·대입을 스스로 조합해 두 줄의 결과를 만들어요.'],
              core_flow='준비 코드에는 quantity와 added 두 값만 있다. 학생은 출력문 두 개와 대입문 하나를 직접 쓴다. '
                        '첫 줄은 괄호로 먼저 더한 합계 뒤에 개를 붙이고, 둘째 줄은 합계를 quantity에 저장한 뒤 읽는다. '
                        '채점: 실제 JDK 출력, 두 수량을 바꾼 재실행. 괄호 없는 연결은 23개가 되어 실패한다.'),
    task=dict(
        id=STEP, title='합계를 출력하고 저장한 수량도 출력하세요', language='java',
        goal=('자, 마지막 도전이에요. 장바구니에 quantity개가 있는데 손님이 added개를 더 담았어요. 준비 코드에는 두 값만 있어요.\n\n'
              '결과 창에 두 줄이 나와야 해요. 첫 줄은 두 수량을 더한 합계 뒤에 개를 붙인 `합계: 5개`예요. '
              '둘째 줄은 합계를 quantity에 저장한 뒤 그 값을 읽은 `저장한 수량: 5`예요. '
              '채점은 두 수량을 다른 값으로 바꿔서도 실행해요.\n\n'
              '**할 일**\n\n'
              '1. 코드 실행 버튼을 눌러 아직 아무것도 나오지 않는 것을 확인하세요.\n'
              '2. 두 수량의 합계 뒤에 개가 붙는 첫 출력문을 쓰세요.\n'
              '3. quantity에 합계를 저장하는 대입문을 쓰세요.\n'
              '4. 저장한 quantity를 읽어 둘째 줄을 출력하는 출력문을 쓰세요.\n'
              '5. 코드 실행 버튼을 눌러 두 줄이 요구와 같은지 확인하세요.\n'
              '6. 수정한 코드를 제출하세요.'),
        starter_code=STARTER, solution=SOLUTION,
        tests=[dict(input='', expected='합계: 5개\n저장한 수량: 5')],
        required=True,
        variations=[dict(values=dict(quantity='7', added='2'), expected='합계: 9개\n저장한 수량: 9'),
                    dict(values=dict(quantity='10', added='0'), expected='합계: 10개\n저장한 수량: 10')],
        narration=[
            dict(action='say', text='마지막 도전이에요. 결과 두 줄만 정해져 있고 코드는 직접 써요.', target='text:결과 창에 두 줄이 나와야 해요.'),
            dict(action='say', text='quantity는 이미 담긴 2개, added는 더 담은 3개예요.', target='code:int added = 3;'),
            dict(action='run', lines=[3, 4]),
            dict(action='say', text='아무것도 안 나와요. 값만 저장했고 출력문은 아직 없거든요.', target='output'),
            dict(action='say', text='첫 줄은 합계: 5개예요. 숫자 덧셈을 글자보다 먼저 해야 해요.', target='text:합계: 5개'),
            dict(action='patch_code', before=PLACEHOLDER, after=LINE1 + '\n' + PLACEHOLDER,
                 say='두 수량을 괄호로 묶어 먼저 더하고, 앞뒤에 글자를 붙여요.'),
            dict(action='run', lines=[6, 6]),
            dict(action='say', text='합계: 5개가 나와요. 괄호 안 2 + 3이 먼저 계산됐어요.', target='output'),
            dict(action='patch_code', before='(quantity + added)', after='quantity + added',
                 say='괄호를 빼면 어떻게 되는지 볼게요.'),
            dict(action='run', lines=[6, 6]),
            dict(action='say', text='합계: 23개가 나와요. 글자 뒤에 2와 3을 차례로 이어 붙였어요.', target='output'),
            dict(action='patch_code', before='"합계: " + quantity + added + "개"', after='"합계: " + (quantity + added) + "개"',
                 say='그래서 괄호를 다시 넣어요.'),
            dict(action='say', text='둘째 줄은 합계를 quantity에 저장한 뒤의 값이에요.', target='text:합계를 quantity에 저장한 뒤 그 값을 읽은'),
            dict(action='patch_code', before=PLACEHOLDER, after=LINE23,
                 say='quantity에 지금 값과 added를 더해 다시 넣고, 그 값을 출력해요.'),
            dict(action='run', lines=[6, 10]),
            dict(action='say', text='합계: 5개 다음에 저장한 수량: 5가 나와요. 대입 뒤 quantity가 5가 됐어요.', target='output'),
            dict(action='say', text='조심하세요. 결과를 보고 5를 직접 적으면 다른 수량으로 채점할 때 틀려요.', target='code:quantity = quantity + added;'),
            dict(action='patch_code', before='int quantity = 2;', after='int quantity = 7;', say='quantity를 7로 바꿔 같은 코드가 통하는지 볼게요.'),
            dict(action='run', lines=[6, 10]),
            dict(action='say', text='합계: 10개와 저장한 수량: 10이 나와요. 식이 값을 따라 계산해요.', target='output'),
            dict(action='patch_code', before='int quantity = 7;', after='int quantity = 2;', say='준비된 수량 2로 되돌려요.'),
            dict(action='run', lines=[6, 10]),
            dict(action='say', text='다시 합계: 5개와 저장한 수량: 5예요. 요구한 두 줄과 같아요.', target='output'),
        ]),
    cases=dict(
        expected_outputs=['', '합계: 5개', '합계: 23개', '합계: 5개\n저장한 수량: 5', '합계: 10개\n저장한 수량: 10', '합계: 5개\n저장한 수량: 5'],
        reject=[([['(quantity + added)', 'quantity + added']], 'Without parentheses the text joins 2 and 3 into 23'),
                ([['(quantity + added)', '5']], 'A memorized total fails the changed quantities'),
                ([['    quantity = quantity + added;\n', '']], 'Without the assignment the second line still reads 2'),
                ([['quantity = quantity + added;', 'quantity = added;']], 'Storing only the added amount loses the cart')],
        accept=[([['quantity = quantity + added;', 'quantity += added;']], 'A compound assignment stores the same total'),
                ([['(quantity + added)', '(added + quantity)']], 'Addition order does not matter')]),
    review={'조심하세요. 결과를 보고 5를 직접 적으면 다른 수량으로 채점할 때 틀려요.':
            '이 문제에서 실제로 하기 쉬운 실수(실행 결과의 숫자를 그대로 적기)와 결과(바꾼 수량 채점 실패)를 말해요. 채점의 variations와 맞아요.'},
)
