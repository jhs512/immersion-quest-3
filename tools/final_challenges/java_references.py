"""java-references final challenge: an alias versus a real copy, observed through changes and ==."""
from _common import Script, todo

STEP = 'stp_8b3e5a19-4c72-4d06-a9f1-2e6c7b04d38f'
COPY_TODO = '        return original; // 같은 재고 수를 가진 새 상자를 돌려주도록 고치세요.'
CHANGE_TODO = '        // 여기에 b를 통해 상자의 재고를 2 늘리는 줄을 쓰세요.'
STARTER = f'''// 재고 상자예요. 생성자에서 처음 재고를 받아요.
class Box {{
    int count;
    Box(int count) {{
        this.count = count;
    }}
}}

class Main {{
    // 원래 상자와 같은 재고 수를 가진 새 상자를 만들어 돌려줘요.
    static Box copy(Box original) {{
{COPY_TODO}
    }}

    public static void main(String[] args) {{
        Box a = new Box(5);
        // b는 a와 같은 상자, c는 a를 복사한 새 상자예요.
        Box b = a;
        Box c = copy(a);
{CHANGE_TODO}
        System.out.println(a.count);
        System.out.println(c.count);
        System.out.println(a == b);
        System.out.println(a == c);
    }}
}}
'''
COPY = '''        // 새 객체를 만들어야 원래 상자와 따로 바뀌어요.
        return new Box(original.count);'''
CHANGE = '''        // b는 a와 같은 상자를 가리키므로 a에서도 바뀐 값이 보여요.
        b.count = b.count + 2;'''
SOLUTION = STARTER.replace(COPY_TODO, COPY).replace(CHANGE_TODO, CHANGE)

s = Script(STARTER)
s.say('마지막 도전이에요. 같은 상자를 가리키는 b와 복사한 새 상자 c를 구별해요.', 'text:b는 a와 같은 상자, c는 a를 복사한 새 상자예요.')
s.say('copy는 지금 받은 상자를 그대로 돌려줘요. 그러면 c도 a와 같은 상자예요.', 'code:return original;')
s.patch(CHANGE_TODO, CHANGE, '먼저 b를 통해 재고를 2 늘려요.')
s.run()
s.say('7, 7, true, true예요. c까지 바뀌었고 a == c도 true라 복사가 아니에요.', 'output')
s.patch(COPY_TODO, COPY, 'copy가 원래 재고 수로 새 Box를 만들어 돌려주게 고쳐요.')
s.run()
s.say('7, 5, true, false예요. b로 바꾼 값은 a에 보이고, 새 상자 c는 5 그대로예요.', 'output')
s.say('조심하세요. 상자를 대입만 하면 복사가 아니라 같은 상자를 하나 더 가리킬 뿐이에요.', 'code:Box b = a;')
s.patch('Box a = new Box(5);', 'Box a = new Box(1);', '처음 재고를 1로 바꿔도 같은 관계인지 볼게요.')
s.run()
s.say('3, 1, true, false예요. 처음 값이 달라도 별칭과 복사의 관계는 같아요.', 'output')
s.patch('Box a = new Box(1);', 'Box a = new Box(5);', '준비된 재고 5로 되돌려요.')
s.run()
s.say('다시 7, 5, true, false예요. 요구한 네 줄이에요.', 'output')

GOAL = ('자, 마지막 도전이에요. b는 a와 같은 상자, c는 a를 복사한 새 상자예요. b를 통해 재고를 2 늘린 뒤 네 줄을 출력해요.\n\n'
        '지금 상자면 `7`, `5`, `true`, `false`가 차례로 나와야 해요. a의 재고는 b의 변경을 함께 보여 주고, c는 복사한 순간의 5를 지켜야 해요. '
        '채점은 처음 재고를 다른 값으로 바꿔서도 실행해요.\n\n'
        + todo('b를 통해 상자의 재고를 2 늘리는 줄을 쓰세요.',
               '코드 실행 버튼을 눌러 c도 함께 바뀌는지 확인하세요.',
               'copy가 같은 재고 수를 가진 새 상자를 돌려주도록 고치세요.',
               '코드 실행 버튼을 눌러 네 줄이 요구와 같은지 확인하세요.',
               '수정한 코드를 제출하세요.'))

SPEC = dict(
    key='java-references', course='java', revision='java-references-10',
    reason='별칭으로 바꾼 값과 새 객체 복사, == 비교를 한 프로그램에서 함께 관찰하고 처음 재고를 바꿔 다시 채점하는 마지막 도전이에요.',
    grading='실제 JDK의 네 줄 출력과 처음 재고를 바꾼 재실행을 채점해요. copy가 같은 상자를 돌려주면 c가 바뀌고 a == c가 true라 실패해요.',
    unit=dict(id='unt_4d7a1e93-6b28-4f05-8c3d-91e5f2a06b7c', title='마지막 도전',
              objectives=['별칭과 복사를 같은 프로그램에서 구별해요.'],
              premise='재고 상자 하나와 그것을 가리키는 변수 셋이에요. 복사 메서드는 직접 고쳐요.'),
    step=dict(id=STEP, title='별칭으로 바꾸고 복사본은 지키세요',
              objectives=['참조 대입과 새 객체 생성의 차이를 변경 결과와 == 비교로 증명해요.'],
              core_flow='copy는 받은 참조를 그대로 돌려준다. 학생은 b로 재고를 늘리는 줄과 copy의 새 Box 생성을 쓴다. '
                        '채점: 7·5·true·false 출력과 처음 재고 변형. 참조를 그대로 돌려주면 7·7·true·true가 되어 실패한다.'),
    task=dict(id=STEP, title='별칭으로 바꾸고 복사본은 지키세요', language='java', goal=GOAL,
              starter_code=STARTER, solution=SOLUTION, tests=[dict(input='', expected='7\n5\ntrue\nfalse')], required=True,
              variations=[dict(values=dict(a='new Box(1)'), expected='3\n1\ntrue\nfalse'),
                          dict(values=dict(a='new Box(0)'), expected='2\n0\ntrue\nfalse')],
              narration=s.actions),
    cases=dict(expected_outputs=['7\n7\ntrue\ntrue', '7\n5\ntrue\nfalse', '3\n1\ntrue\nfalse', '7\n5\ntrue\nfalse'],
               reject=[([['return new Box(original.count);', 'return original;']], 'Returning the same reference is not a copy'),
                       ([['return new Box(original.count);', 'return new Box(5);']], 'A fixed copy fails other starting counts'),
                       ([['b.count = b.count + 2;', 'c.count = c.count + 2;']], 'Changing the copy leaves the shared box')],
               accept=[([['b.count = b.count + 2;', 'a.count += 2;']], 'a and b are the same box'),
                       ([['return new Box(original.count);', 'Box fresh = new Box(0);\n        fresh.count = original.count;\n        return fresh;']], 'Copying the field after creating the box')]),
    review={'조심하세요. 상자를 대입만 하면 복사가 아니라 같은 상자를 하나 더 가리킬 뿐이에요.':
            '이 문제의 copy 첫 상태(받은 참조 반환)가 바로 그 실수이고, 바로 앞 실행 결과(7, 7, true, true)로 확인했어요.',
            '3, 1, true, false예요. 처음 값이 달라도 별칭과 복사의 관계는 같아요.':
            '양보 「달라도」 뒤에 실제 대조(숫자는 바뀌었지만 a==b true, a==c false라는 관계는 그대로)가 와요. 앞 실행 7·5와 지금 3·1을 비교한 결과와 맞아요.'},
)
