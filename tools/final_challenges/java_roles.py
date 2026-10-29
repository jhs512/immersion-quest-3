"""java-roles final challenge: implement a policy behind an interface, reject an invalid object, guard a state change."""
from _common import Script, todo

STEP = 'stp_2d8b4f61-7e39-4a52-9c16-b0e3d5a8f7c2'
POLICY_TODO = '// 여기에 FeePolicy를 구현하는 MemberFee 클래스를 쓰세요. 1만 원 이상은 0원, 그 밖은 1,500원이에요.'
OPEN_TODO = '        // 음수 잔액으로 만들려고 하면 IllegalArgumentException을 던지세요.'
PAY_TODO = '        // 양수이고 잔액 이하인 결제만 허용하세요.'
STARTER = f'''interface FeePolicy {{
    // 주문 금액을 받아 배송비를 돌려줘요.
    int fee(int amount);
}}

class Checkout {{
    private final FeePolicy policy;
    Checkout(FeePolicy policy) {{ this.policy = policy; }}
    // 정책이 정한 배송비를 주문 금액에 더해요.
    int total(int amount) {{ return amount + policy.fee(amount); }}
}}

{POLICY_TODO}

class Wallet {{
    private int balance;
    Wallet(int opening) {{
{OPEN_TODO}
        balance = opening;
    }}
    boolean pay(int price) {{
{PAY_TODO}
        balance -= price;
        return true;
    }}
    int balance() {{ return balance; }}
}}

public class Main {{
    public static void main(String[] args) {{
        // 지갑의 처음 잔액과 주문 금액은 준비 값이에요.
        int opening = 20000;
        int amount = 9000;
        try {{
            Wallet wallet = new Wallet(opening);
            int total = new Checkout(new MemberFee()).total(amount);
            System.out.println(total + " " + wallet.pay(total) + " " + wallet.balance());
        }} catch (IllegalArgumentException error) {{
            System.out.println("거절");
        }} finally {{
            System.out.println("closed");
        }}
    }}
}}
'''
POLICY = '''// 회원 배송비 정책이에요. Checkout은 이 클래스의 이름을 몰라도 돼요.
class MemberFee implements FeePolicy {
    public int fee(int amount) {
        return amount >= 10000 ? 0 : 1500;
    }
}'''
OPEN = '''        // 잘못된 처음 상태로는 객체를 만들지 않아요.
        if (opening < 0) throw new IllegalArgumentException("opening");'''
PAY = '''        // 잘못된 결제는 상태를 바꾸기 전에 거절해요.
        if (price <= 0 || price > balance) return false;'''
SOLUTION = STARTER.replace(POLICY_TODO, POLICY).replace(OPEN_TODO, OPEN).replace(PAY_TODO, PAY)
BROKEN_POLICY = '''// 회원 배송비 정책이에요. Checkout은 이 클래스의 이름을 몰라도 돼요.
class MemberFee implements FeePolicy {
    public int fee(int amount) {
        return 0;
    }
}'''

s = Script(STARTER)
s.say('마지막 도전이에요. 배송비 정책을 끼우고, 지갑이 잘못된 상태를 막게 해요.', 'text:회원 배송비 정책 MemberFee')
s.say('Checkout은 FeePolicy만 알아요. 어떤 정책이 오든 fee를 불러 더해요.', 'code:int total(int amount) { return amount + policy.fee(amount); }')
s.patch(POLICY_TODO, BROKEN_POLICY, '먼저 FeePolicy를 구현하는 MemberFee를 만들어 컴파일되게 해요. 본문은 잠시 0이에요.')
s.run()
s.say('9000 true 11000이 나오고 closed도 나와요. 배송비가 빠져서 아직 틀렸어요.', 'output')
s.patch(BROKEN_POLICY, POLICY, '1만 원 이상이면 0, 아니면 1,500원을 돌려주게 해요.')
s.run()
s.say('10500 true 9500이에요. 9,000원 주문에 배송비 1,500원이 붙었어요.', 'output')
s.patch('int opening = 20000;', 'int opening = 5000;', '잔액이 모자란 지갑으로 바꿔 볼게요.')
s.run()
s.say('10500 true -5500이에요. 잔액보다 큰 결제를 허용해 음수가 됐어요.', 'output')
s.patch(PAY_TODO, PAY, '양수이고 잔액 이하가 아니면 상태를 바꾸기 전에 false를 돌려줘요.')
s.run()
s.say('10500 false 5000이에요. 거절했고 잔액은 그대로예요.', 'output')
s.patch('int opening = 5000;', 'int opening = -1;', '처음 잔액이 음수인 지갑도 확인해요.')
s.patch(OPEN_TODO, OPEN, '생성자에서 음수 잔액이면 예외를 던져 객체를 만들지 않아요.')
s.run()
s.say('거절 다음에 closed가 나와요. 예외가 나도 finally는 꼭 실행돼요.', 'output')
s.say('조심하세요. 잔액을 먼저 빼고 나중에 검사하면 거절된 결제도 잔액을 바꿔요.', 'code:if (price <= 0 || price > balance) return false;')
s.patch('int opening = -1;', 'int opening = 20000;', '준비된 잔액으로 되돌려요.')
s.run()
s.say('다시 10500 true 9500과 closed예요. 채점은 경계 금액과 잔액으로도 실행해요.', 'output')

GOAL = ('자, 마지막 도전이에요. 회원 배송비 정책 MemberFee를 FeePolicy로 구현해 Checkout에 끼우고, Wallet이 잘못된 상태를 막게 해요.\n\n'
        'MemberFee는 1만 원 이상 주문은 0원, 그 밖은 1,500원을 돌려줘요. Wallet은 음수 잔액으로 만들 수 없고, 양수이면서 잔액 이하인 결제만 허용해요. '
        '거절한 결제는 잔액을 바꾸지 않아요. 지금 준비 값이면 `10500 true 9500`과 `closed`가 나와야 해요. '
        'Checkout과 main은 고치지 않아요. 채점은 주문 금액과 처음 잔액을 바꿔서도 실행해요.\n\n'
        + todo('FeePolicy를 구현하는 MemberFee 클래스를 쓰세요.',
               'Wallet 생성자가 음수 잔액이면 IllegalArgumentException을 던지게 하세요.',
               'pay가 양수이고 잔액 이하인 결제만 허용하게 하세요.',
               '코드 실행 버튼을 눌러 두 줄이 요구와 같은지 확인하세요.',
               '수정한 코드를 제출하세요.'))

SPEC = dict(
    key='java-roles', course='java', revision='java-roles-7',
    reason='인터페이스 구현을 끼우는 조합, 생성자의 예외, 상태를 지키는 거절 조건, finally를 한 프로그램에서 직접 완성하고 여러 금액·잔액으로 채점하는 마지막 도전이에요.',
    grading='실제 JDK 출력과 주문 금액·처음 잔액 변형을 채점해요. 배송비 경계 오류, 음수·초과 결제 허용, 음수 잔액 생성 허용은 실패해요.',
    unit=dict(id='unt_7f3a9c52-1b64-4e8d-a2f7-6d0b3e91c845', title='마지막 도전',
              objectives=['정책 객체를 끼우고 상태 규칙을 지키는 객체를 함께 완성해요.'],
              premise='결제 화면의 배송비 정책과 지갑이에요. Checkout과 main은 준비돼 있어요.'),
    step=dict(id=STEP, title='회원 배송비 정책을 끼우고 지갑의 규칙을 지키세요',
              objectives=['인터페이스 계약을 구현하고, 생성과 변경 시점에 잘못된 상태를 막아요.'],
              core_flow='MemberFee가 없고 Wallet은 검사 없이 상태를 바꾼다. 학생은 MemberFee 구현, 생성자 예외, pay 거절 조건을 쓴다. '
                        '채점: 출력과 금액·잔액 변형(10,000 경계, 잔액 부족, 정확히 잔액, 음수 잔액). 검사 전 차감은 거절해도 잔액이 바뀌어 실패한다.'),
    task=dict(id=STEP, title='회원 배송비 정책을 끼우고 지갑의 규칙을 지키세요', language='java', goal=GOAL,
              starter_code=STARTER, solution=SOLUTION, tests=[dict(input='', expected='10500 true 9500\nclosed')], required=True,
              variations=[dict(values=dict(amount='10000'), expected='10000 true 10000\nclosed'),
                          dict(values=dict(opening='5000'), expected='10500 false 5000\nclosed'),
                          dict(values=dict(opening='10500'), expected='10500 true 0\nclosed'),
                          dict(values=dict(opening='-1'), expected='거절\nclosed'),
                          dict(values=dict(opening='0', amount='-1500'), expected='0 false 0\nclosed')],
              narration=s.actions),
    cases=dict(expected_outputs=['9000 true 11000\nclosed', '10500 true 9500\nclosed', '10500 true -5500\nclosed', '10500 false 5000\nclosed',
                                 '거절\nclosed', '10500 true 9500\nclosed'],
               reject=[([['amount >= 10000 ? 0 : 1500', 'amount > 10000 ? 0 : 1500']], 'A 10,000 order is free'),
                       ([['price <= 0 || price > balance', 'price > balance']], 'A zero or negative payment must be refused'),
                       ([['price <= 0 || price > balance', 'price <= 0']], 'A payment above the balance must be refused'),
                       ([['        if (opening < 0) throw new IllegalArgumentException("opening");\n', '']], 'A negative wallet must not be created')],
               accept=[([['        if (price <= 0 || price > balance) return false;\n        balance -= price;\n        return true;','        if (price > 0 && price <= balance) {\n            balance -= price;\n            return true;\n        }\n        return false;']], 'Allow-first condition with the same rule')]),
    review={'조심하세요. 잔액을 먼저 빼고 나중에 검사하면 거절된 결제도 잔액을 바꿔요.':
            '이 문제의 pay에서 실제로 하기 쉬운 순서 실수와 결과(거절했는데 잔액이 변함)를 말해요. 잔액 부족 변형이 잡아요.'},
)
