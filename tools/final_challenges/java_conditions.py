"""java-conditions final challenge: an else-if chain with two boundaries plus a branch for the message."""
from _common import Script, todo

STEP = 'stp_7d2e9a41-3c58-4b1f-8e06-a95c2d17f3b8'
TIERS = '    // 여기에 구간에 맞게 fee를 정하는 조건문을 쓰세요.'
MESSAGE = '    // 여기에 fee가 0이면 무료배송, 아니면 배송비를 출력하는 조건문을 쓰세요.'
STARTER = f'''void main() {{
    // 주문 금액이에요.
    int amount = 32000;
    // 3만 원 이상은 무료, 1만 5천 원 이상은 1,500원, 그 밖은 3,000원이에요.
    int fee = 3000;
{TIERS}
{MESSAGE}
}}
'''
TIER_CODE = '''    // 높은 구간부터 검사해 한 갈래만 실행해요.
    if (amount >= 30000) {
        fee = 0;
    } else if (amount >= 15000) {
        fee = 1500;
    }'''
MESSAGE_CODE = '''    // 정해진 배송비로 안내 문구를 골라요.
    if (fee == 0) {
        System.out.println("무료배송");
    } else {
        System.out.println("배송비 " + fee + "원");
    }'''
SOLUTION = STARTER.replace(TIERS, TIER_CODE).replace(MESSAGE, MESSAGE_CODE)

s = Script(STARTER)
s.say('마지막 도전이에요. 배송비 구간 셋과 안내 문구를 직접 정해요.', 'text:3만 원 이상은 무료배송')
s.say('fee는 3,000원으로 시작해요. 조건이 맞으면 값을 바꿔요.', 'code:int fee = 3000;')
s.say('먼저 안내 문구부터 써서 지금 fee가 어떻게 보이는지 볼게요.', 'text:fee가 0이면 무료배송을, 아니면')
s.patch(MESSAGE, MESSAGE_CODE, 'fee가 0인지 비교해 두 문구 중 하나만 출력해요.')
s.run()
s.say('배송비 3000원이 나와요. 아직 구간 조건이 없어 기본값 그대로예요.', 'output')
s.patch(TIERS, TIER_CODE, '높은 구간부터 if와 else if로 이어 써요. 한 갈래만 실행돼요.')
s.run()
s.say('32,000원은 무료배송이에요. 첫 조건이 참이라 뒤 조건은 건너뛰었어요.', 'output')
s.say('조심하세요. else 없이 if를 따로 쓰면 32,000원도 둘째 조건에서 1,500원으로 덮어써요.', 'code:} else if (amount >= 15000) {')
s.patch('int amount = 32000;', 'int amount = 30000;', '경계 금액 30,000원으로 바꿔 볼게요.')
s.run()
s.say('30,000원도 무료배송이에요. 이상을 뜻하는 >=라 기준 금액을 포함해요.', 'output')
s.patch('int amount = 30000;', 'int amount = 29999;', '1원 모자란 29,999원도 확인해요.')
s.run()
s.say('배송비 1500원이에요. 첫 조건은 거짓, 둘째 조건이 참이었어요.', 'output')
s.patch('int amount = 29999;', 'int amount = 32000;', '준비된 금액 32,000원으로 되돌려요.')
s.run()
s.say('다시 무료배송이에요. 채점은 경계 금액들로도 실행해요.', 'output')

GOAL = ('자, 마지막 도전이에요. 주문 금액 amount로 배송비 fee를 정하고 안내 문구를 출력해요.\n\n'
        '규칙은 3만 원 이상은 무료배송, 1만 5천 원 이상은 1,500원, 그 밖은 3,000원이에요. '
        '출력은 fee가 0이면 무료배송을, 아니면 `배송비 1500원`처럼 금액을 붙인 문구를 한 줄로 내요. '
        '채점은 30,000원·29,999원·15,000원·14,999원 같은 경계 금액으로 바꿔서도 실행해요.\n\n'
        + todo('코드 실행 버튼을 눌러 지금은 아무것도 나오지 않는 것을 확인하세요.',
               '금액 구간에 따라 fee를 한 번만 정하는 조건문을 쓰세요.',
               'fee가 0인지에 따라 두 문구 중 하나를 출력하는 조건문을 쓰세요.',
               '코드 실행 버튼을 눌러 32,000원 주문의 문구를 확인하세요.',
               'amount를 경계 금액으로 바꿔 실행해 본 뒤 32,000원으로 되돌리세요.',
               '수정한 코드를 제출하세요.'))

SPEC = dict(
    key='java-conditions', course='java', revision='java-conditions-9',
    reason='비교·경계 포함·else if 사슬·if/else 출력을 알려 주지 않은 구조로 조합하고, 경계 금액 네 개로 다시 실행해 채점하는 마지막 도전이에요.',
    grading='실제 JDK 출력과 경계 금액 30,000·29,999·15,000·14,999원으로 바꾼 재실행을 채점해요. 따로 쓴 if의 덮어쓰기, > 경계 오류, 문구 직접 출력은 실패해요.',
    unit=dict(id='unt_2f6b8d13-7a49-4c5e-b0d2-8e1f4a96c7d5', title='마지막 도전',
              objectives=['구간 조건과 출력 분기를 한 프로그램에서 함께 정해요.'],
              premise='같은 가게의 배송비 규칙이에요. 이번에는 조건문의 모양을 알려 주지 않아요.'),
    step=dict(id=STEP, title='세 구간 배송비와 안내 문구를 직접 정하세요',
              objectives=['경계를 포함하는 비교와 else if·else를 조합해 규칙 전체를 구현해요.'],
              core_flow='준비 코드에는 amount와 기본 fee만 있다. 학생은 높은 구간부터 else if 사슬로 fee를 한 번만 정하고, '
                        'fee == 0 여부로 두 문구 중 하나를 출력한다. 채점: 실제 JDK 출력과 경계 금액 네 개로 바꾼 재실행. '
                        '따로 쓴 if는 32,000원을 1,500원으로 덮어써 실패한다.'),
    task=dict(id=STEP, title='세 구간 배송비와 안내 문구를 직접 정하세요', language='java', goal=GOAL,
              starter_code=STARTER, solution=SOLUTION, tests=[dict(input='', expected='무료배송')], required=True,
              variations=[dict(values=dict(amount='30000'), expected='무료배송'),
                          dict(values=dict(amount='29999'), expected='배송비 1500원'),
                          dict(values=dict(amount='15000'), expected='배송비 1500원'),
                          dict(values=dict(amount='14999'), expected='배송비 3000원')],
              narration=s.actions),
    cases=dict(expected_outputs=['배송비 3000원', '무료배송', '무료배송', '배송비 1500원', '무료배송'],
               reject=[([['    } else if (amount >= 15000) {', '    }\n    if (amount >= 15000) {']], 'Two separate ifs overwrite the free tier'),
                       ([['amount >= 30000', 'amount > 30000']], 'The 30,000 boundary must be free'),
                       ([['amount >= 15000', 'amount > 15000']], 'The 15,000 boundary must cost 1,500'),
                       ([['System.out.println("배송비 " + fee + "원");', 'System.out.println("배송비 1500원");']], 'A typed fee fails the 14,999 order')],
               accept=[([['if (fee == 0) {', 'if (fee < 1) {']], 'Another comparison that means free'),
                       ([['amount >= 15000', '15000 <= amount']], 'The same comparison written the other way')]),
    review={'조심하세요. else 없이 if를 따로 쓰면 32,000원도 둘째 조건에서 1,500원으로 덮어써요.':
            '이 수업 7번에서 본 실제 실수(따로 쓴 if 두 개)가 이 문제에서 내는 결과를 정확한 금액으로 말해요. 채점의 32,000원 기본 사례가 이를 잡아요.'},
)
