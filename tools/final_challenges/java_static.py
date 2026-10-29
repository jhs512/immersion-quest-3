"""java-static final challenge: per-order fields, a shared counter and a shared limit used by an instance method."""
from _common import Script, todo

STEP = 'stp_6c2f8e15-9a47-4b3d-b8e0-5d1a3f72c94e'
FIELDS_TODO = '    // 여기에 주문마다 따로 남는 금액 필드와, 만든 주문 수를 세는 공유 필드를 쓰세요.'
CTOR_TODO = '        // 여기에 금액을 저장하고 만든 주문 수를 1 늘리세요.'
FREE_TODO = '        return false; // 이 주문의 금액을 공유 기준과 비교하도록 고치세요.'
STARTER = f'''// 주문 하나의 금액과, 모든 주문이 함께 쓰는 값이 있어요.
class Order {{
    // 무료배송 기준은 모든 주문이 같이 써요.
    static int freeFrom = 20000;
{FIELDS_TODO}
    Order(int initial) {{
{CTOR_TODO}
    }}
    boolean isFree() {{
{FREE_TODO}
    }}
}}

class Main {{
    public static void main(String[] args) {{
        // 금액이 다른 두 주문과, 추가로 만드는 주문 수예요.
        int first = 25000;
        int second = 9000;
        int extra = 1;
        Order a = new Order(first);
        Order b = new Order(second);
        for (int i = 0; i < extra; i++) {{
            new Order(1000);
        }}
        System.out.println(a.amount + " " + a.isFree());
        System.out.println(b.amount + " " + b.isFree());
        System.out.println("주문 수: " + Order.created);
    }}
}}
'''
FIELDS = '''    // amount는 주문마다, created는 클래스에 하나만 있어요.
    int amount;
    static int created = 0;'''
CTOR = '''        amount = initial;
        // 새 주문을 만들 때마다 공유 카운터를 하나 늘려요.
        created = created + 1;'''
FREE = '''        // 이 주문의 금액을 모든 주문이 쓰는 기준과 비교해요.
        return amount >= freeFrom;'''
SOLUTION = STARTER.replace(FIELDS_TODO, FIELDS).replace(CTOR_TODO, CTOR).replace(FREE_TODO, FREE)

s = Script(STARTER)
s.say('마지막 도전이에요. 주문마다 다른 값과 모든 주문이 나누는 값을 직접 나눠요.', 'text:금액은 주문마다 따로')
s.say('main은 두 주문을 만들고, extra만큼 주문을 더 만든 뒤 세 줄을 출력해요.', 'code:new Order(1000);')
s.patch(FIELDS_TODO, '    // 금액 필드를 static으로 두면 어떻게 되는지 먼저 볼게요.\n    static int amount;\n    static int created = 0;',
        '금액도 static으로 두면 어떻게 될지 먼저 써 볼게요.')
s.patch(CTOR_TODO, CTOR, '생성자에서 금액을 저장하고 공유 카운터를 늘려요.')
s.run()
s.say('두 주문이 모두 1000으로 보여요. 클래스에 금액이 하나라 마지막 주문이 덮어썼어요.', 'output')
s.patch('    // 금액 필드를 static으로 두면 어떻게 되는지 먼저 볼게요.\n    static int amount;\n    static int created = 0;', FIELDS,
        '금액은 주문마다 남도록 static을 빼요. 카운터만 공유해요.')
s.run()
s.say('25000, 9000이 따로 남고 주문 수: 3이에요. isFree는 아직 늘 false예요.', 'output')
s.patch(FREE_TODO, FREE, 'isFree는 이 주문의 금액을 공유 기준 freeFrom과 비교해요.')
s.run()
s.say('25000 true, 9000 false, 주문 수: 3이에요. 요구한 세 줄이에요.', 'output')
s.say('조심하세요. 생성자에서 created = 1로 쓰면 주문을 몇 개 만들어도 1이에요.', 'code:created = created + 1;')
s.patch('int extra = 1;', 'int extra = 3;', '추가 주문 수를 3으로 바꿔 카운터를 확인해요.')
s.run()
s.say('주문 수: 5예요. 두 주문과 추가 세 주문을 모두 셌어요.', 'output')
s.patch('int extra = 3;', 'int extra = 1;', '준비된 수로 되돌려요.')
s.run()
s.say('다시 주문 수: 3이에요. 채점은 금액과 추가 수를 바꿔서도 실행해요.', 'output')

GOAL = ('자, 마지막 도전이에요. Order의 필드와 생성자, isFree를 직접 완성해요. '
        '금액은 주문마다 따로 남고, 만든 주문 수와 무료배송 기준은 모든 주문이 함께 써요.\n\n'
        '지금 준비 값이면 `25000 true`, `9000 false`, `주문 수: 3`이 나와야 해요. 채점은 두 금액과 추가 주문 수를 바꿔서도 실행해요.\n\n'
        + todo('주문마다 남는 금액 필드와 만든 주문 수를 세는 공유 필드를 쓰세요.',
               '생성자에서 금액을 저장하고 만든 주문 수를 1 늘리세요.',
               'isFree가 이 주문의 금액을 공유 기준과 비교하도록 고치세요.',
               '코드 실행 버튼을 눌러 세 줄이 요구와 같은지 확인하세요.',
               '수정한 코드를 제출하세요.'))

SPEC = dict(
    key='java-static', course='java', revision='java-static-9',
    reason='객체별 필드·static 카운터·공유 기준을 쓰는 인스턴스 메서드를 직접 설계하고 금액과 생성 수를 바꿔 채점하는 마지막 도전이에요.',
    grading='실제 JDK 출력과 금액·추가 주문 수를 바꾼 재실행을 채점해요. 금액을 static으로 두거나 created를 1로 고정하거나 기준을 직접 적으면 실패해요.',
    unit=dict(id='unt_1e9c5a27-3f84-4b6d-a0e2-7c4d8b15f39a', title='마지막 도전',
              objectives=['객체별 값과 공유 값을 한 클래스에서 직접 나눠요.'],
              premise='주문 클래스의 필드와 생성자가 비어 있어요. main은 준비돼 있어요.'),
    step=dict(id=STEP, title='주문별 금액과 공유 주문 수를 직접 나누세요',
              objectives=['인스턴스 필드와 static 필드를 목적에 맞게 고르고, 인스턴스 메서드에서 공유 기준을 읽어요.'],
              core_flow='Order에는 static 기준만 있다. 학생은 int amount, static created, 생성자의 저장·증가, isFree의 비교를 쓴다. '
                        '채점: 세 줄 출력과 금액·extra 변형. static amount는 두 주문이 마지막 금액으로 같아져 실패한다.'),
    task=dict(id=STEP, title='주문별 금액과 공유 주문 수를 직접 나누세요', language='java', goal=GOAL,
              starter_code=STARTER, solution=SOLUTION, tests=[dict(input='', expected='25000 true\n9000 false\n주문 수: 3')], required=True,
              variations=[dict(values=dict(first='20000', second='19999'), expected='20000 true\n19999 false\n주문 수: 3'),
                          dict(values=dict(extra='0'), expected='25000 true\n9000 false\n주문 수: 2'),
                          dict(values=dict(extra='4', first='100'), expected='100 false\n9000 false\n주문 수: 6')],
              narration=s.actions),
    cases=dict(expected_outputs=['1000 false\n1000 false\n주문 수: 3', '25000 false\n9000 false\n주문 수: 3', '25000 true\n9000 false\n주문 수: 3',
                                 '25000 true\n9000 false\n주문 수: 5', '25000 true\n9000 false\n주문 수: 3'],
               reject=[([['    int amount;\n', '    static int amount;\n']], 'A shared amount makes every order show the last one'),
                       ([['created = created + 1;', 'created = 1;']], 'The counter must grow with each order'),
                       ([['return amount >= freeFrom;', 'return amount >= 25000;']], 'The shared limit must be used'),
                       ([['return amount >= freeFrom;', 'return amount > freeFrom;']], 'An order equal to the limit is free')],
               accept=[([['created = created + 1;', 'created++;']], 'Increment operator'),
                       ([['        amount = initial;', '        this.amount = initial;']], 'this.amount names the same field')]),
    review={'조심하세요. 생성자에서 created = 1로 쓰면 주문을 몇 개 만들어도 1이에요.':
            '이 수업 8번의 실제 실수와 그 결과를 이 문제의 카운터로 말해요. 채점의 extra 변형이 잡아요.'},
)
