"""java-methods final challenge: two returning methods (loop sum, early-return fee) combined by calls in main."""
import json
from _common import Script, contract, todo

STEP = 'stp_3a9f6c28-e1d4-4b85-9f72-6d0e8b13a5c9'
SUM_TODO = '        return 0; // 모든 가격을 더한 합을 돌려주도록 고치세요.'
FEE_TODO = '        return 2500; // 기준 이상이면 0을 돌려주도록 고치세요.'
MAIN_TODO = '        // 여기에 두 메서드를 불러 결제 금액을 출력하세요.'
STARTER = f'''class Main {{
    // 가격을 모두 더한 합을 돌려줘요.
    static int sum(int[] prices) {{
{SUM_TODO}
    }}

    // 상품 합계가 기준 이상이면 0, 아니면 2500을 돌려줘요.
    static int shipping(int amount, int freeFrom) {{
{FEE_TODO}
    }}

    public static void main(String[] args) {{
        // 주문 가격과 무료배송 기준은 준비 값이에요.
        int[] prices = {{4000, 3000}};
        int freeFrom = 10000;
{MAIN_TODO}
    }}
}}
'''
SUM = '''        int result = 0;
        // 모든 가격을 다 더한 뒤에 돌려줘요.
        for (int price : prices) {
            result = result + price;
        }
        return result;'''
FEE = '''        // 기준 이상이면 그 자리에서 0을 돌려줘요.
        if (amount >= freeFrom) {
            return 0;
        }
        return 2500;'''
MAIN = '''        // 합계를 먼저 구하고, 그 합계로 배송비를 구해 더해요.
        int amount = sum(prices);
        System.out.println("결제 금액: " + (amount + shipping(amount, freeFrom)));'''
SOLUTION = STARTER.replace(SUM_TODO, SUM).replace(FEE_TODO, FEE).replace(MAIN_TODO, MAIN)

CHECKS = ('require(Main.sum(new int[]{}) == 0 && Main.sum(new int[]{4, 2, 1}) == 7, "sum은 모든 가격의 합을 돌려줘야 해요.");\n'
          '        require(Main.shipping(10000, 10000) == 0 && Main.shipping(9999, 10000) == 2500 && Main.shipping(0, 0) == 0, '
          '"shipping은 기준 이상이면 0, 아니면 2500을 돌려줘야 해요.");')
CHECKER = json.dumps([contract('Main', 'sum', '{ return -7; }', CHECKS),
                      contract('Main', 'shipping', '{ return -7; }', CHECKS)], ensure_ascii=False)

s = Script(STARTER)
s.say('마지막 도전이에요. 결제 금액은 가격 합계에 배송비를 더한 값이에요.', 'text:결제 금액은 상품 합계에 배송비를 더한 값이에요.')
s.say('sum과 shipping은 지금 고정값만 돌려줘요. 둘 다 고쳐 main에서 불러요.', 'code:static int shipping(int amount, int freeFrom)')
s.patch(MAIN_TODO, MAIN, 'main에서 sum으로 합계를 받고, 그 합계를 shipping에 넘겨 더해요.')
s.run()
s.say('결제 금액: 2500이에요. sum이 아직 0을 돌려주거든요.', 'output')
s.patch(SUM_TODO, SUM, 'sum은 반복이 끝난 뒤에 합을 돌려주게 써요.')
s.run()
s.say('결제 금액: 9500이에요. 7000에 배송비 2500이 붙었어요.', 'output')
s.patch('int[] prices = {4000, 3000};', 'int[] prices = {6000, 4000};', '합계가 기준 10,000원과 같은 주문으로 바꿔 볼게요.')
s.run()
s.say('결제 금액: 12500이에요. 기준 이상인데 shipping이 아직 늘 2500이에요.', 'output')
s.patch(FEE_TODO, FEE, 'shipping은 기준 이상이면 바로 0을 돌려주고, 아니면 2500을 돌려줘요.')
s.run()
s.say('결제 금액: 10000이에요. 기준과 같은 합계는 배송비가 0이에요.', 'output')
s.say('조심하세요. return을 반복 안에 두면 첫 가격만 더한 값이 돌아와요. 채점은 sum을 직접 불러 확인해요.', 'code:return result;')
s.patch('int[] prices = {6000, 4000};', 'int[] prices = {4000, 3000};', '준비된 가격으로 되돌려요.')
s.run()
s.say('결제 금액: 9500이에요. 두 메서드의 반환값을 main이 조합했어요.', 'output')

GOAL = ('자, 마지막 도전이에요. 결제 금액은 상품 합계에 배송비를 더한 값이에요. '
        'sum은 가격 배열의 합을, shipping은 합계가 기준 이상이면 0을, 아니면 2500을 돌려줘야 해요. 지금은 둘 다 고정값만 돌려줘요.\n\n'
        '지금 주문이면 `결제 금액: 9500`이 나와야 해요. 채점은 두 메서드를 직접 불러 보고, 다른 가격과 기준으로도 실행해요.\n\n'
        + todo('main에서 sum과 shipping을 불러 결제 금액을 출력하는 줄을 쓰세요.',
               'sum이 모든 가격을 더한 뒤 합을 돌려주도록 고치세요.',
               'shipping이 기준 이상이면 0을 돌려주도록 고치세요.',
               '코드 실행 버튼을 눌러 결제 금액을 확인하세요.',
               '수정한 코드를 제출하세요.'))

SPEC = dict(
    key='java-methods', course='java', revision='java-methods-8',
    reason='반환값이 있는 메서드 두 개(반복 뒤 return, 조기 return)를 직접 쓰고 main에서 반환값을 조합해, 직접 호출과 다른 입력으로 채점하는 마지막 도전이에요.',
    grading='실제 JDK 출력, 다른 가격·기준 변형, sum·shipping 직접 호출, 각 메서드 계산을 바꿨을 때 main 결과가 바뀌는지(실제 호출)를 채점해요.',
    unit=dict(id='unt_6b1d9f47-28ac-4e3b-93f5-c0e72a8d5b16', title='마지막 도전',
              objectives=['반환값이 있는 메서드를 나눠 쓰고 main에서 조합해요.'],
              premise='결제 금액 계산이에요. 메서드 머리는 준비돼 있고 본문과 호출을 직접 써요.'),
    step=dict(id=STEP, title='합계와 배송비 메서드를 완성해 결제 금액을 출력하세요',
              objectives=['반복 뒤 return과 조기 return을 쓰고, 반환값을 다른 호출의 인수로 이어요.'],
              core_flow='sum과 shipping은 고정값만 돌려준다. 학생은 두 본문과 main의 호출·출력을 쓴다. 채점: 실제 출력, 가격·기준 변형, '
                        '직접 호출 계약, 메서드 계산을 바꾼 소스로 main 결과가 바뀌는지. 반복 안 return과 경계 미포함은 실패한다.'),
    task=dict(id=STEP, title='합계와 배송비 메서드를 완성해 결제 금액을 출력하세요', language='java', goal=GOAL,
              starter_code=STARTER, solution=SOLUTION, tests=[dict(input='', expected='결제 금액: 9500')], required=True,
              checker=CHECKER,
              variations=[dict(values=dict(prices='{6000, 4000}'), expected='결제 금액: 10000'),
                          dict(values=dict(prices='{}'), expected='결제 금액: 2500'),
                          dict(values=dict(prices='{5000}', freeFrom='5000'), expected='결제 금액: 5000')],
              narration=s.actions),
    cases=dict(expected_outputs=['결제 금액: 2500', '결제 금액: 9500', '결제 금액: 12500', '결제 금액: 10000', '결제 금액: 9500'],
               reject=[([['            result = result + price;\n        }', '            result = result + price;\n            return result;\n        }']], 'Returning inside the loop sums only the first price'),
                       ([['amount >= freeFrom', 'amount > freeFrom']], 'A total equal to the limit is free'),
                       ([['(amount + shipping(amount, freeFrom))', '(amount + 2500)']], 'main must use shipping'),
                       ([['int amount = sum(prices);', 'int amount = 7000;']], 'main must use sum')],
               accept=[([['        if (amount >= freeFrom) {\n            return 0;\n        }\n        return 2500;', '        return amount >= freeFrom ? 0 : 2500;']], 'A conditional expression returns the same fees')]),
    review={'조심하세요. return을 반복 안에 두면 첫 가격만 더한 값이 돌아와요. 채점은 sum을 직접 불러 확인해요.':
            '이 수업 7번의 실제 실수(반복 안 return)와 그 결과, 그리고 채점이 직접 호출로 잡는다는 사실을 말해요.'},
)
