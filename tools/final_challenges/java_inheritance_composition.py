"""java-inheritance-composition final challenge: two subclasses override behind a final template; dispatch picks them."""
from _common import Script, todo

STEP = 'stp_4f9d2b67-8c31-4e5a-b7d0-1a6e3c94f825'
PICKUP_TODO = '    // 여기에 배송비가 0원이 되도록 fee를 재정의하세요.'
EXPRESS_BUG = '    int fee(long amount) { return 2000; } // 기본 배송비에 2,000원을 더하도록 고치세요.'
STARTER = f'''import java.util.Scanner;

// 모든 배송이 같은 영수증 모양을 써요. 이름과 배송비만 종류마다 달라요.
abstract class Delivery {{
    abstract String name();
    // 기본 배송비예요.
    int fee(int amount) {{ return 3000; }}
    // 영수증 순서는 바꿀 수 없어요. 실제 객체의 name과 fee가 불려요.
    final String receipt(int amount) {{
        return name() + " " + amount + "원 + 배송비 " + fee(amount) + "원";
    }}
}}

class Standard extends Delivery {{
    String name() {{ return "일반"; }}
}}

// 픽업은 배송비가 없어요.
class Pickup extends Delivery {{
    @Override String name() {{ return "픽업"; }}
{PICKUP_TODO}
}}

// 특급은 기본 배송비에 2,000원을 더해요.
class Express extends Delivery {{
    @Override String name() {{ return "특급"; }}
{EXPRESS_BUG}
}}

class Main {{
    // 입력한 종류에 맞는 객체를 만들어요. 변수 타입은 늘 Delivery예요.
    static Delivery of(String kind) {{
        if (kind.equals("pickup")) return new Pickup();
        if (kind.equals("express")) return new Express();
        return new Standard();
    }}

    public static void main(String[] args) {{
        Scanner in = new Scanner(System.in);
        while (in.hasNext()) {{
            Delivery delivery = of(in.next());
            System.out.println(delivery.receipt(in.nextInt()));
        }}
    }}
}}
'''
PICKUP = '    @Override int fee(int amount) { return 0; }'
EXPRESS_HALF = '    int fee(long amount) { return super.fee((int) amount) + 2000; }'
EXPRESS = '    @Override int fee(int amount) { return super.fee(amount) + 2000; }'
SOLUTION = STARTER.replace(PICKUP_TODO, PICKUP).replace(EXPRESS_BUG, EXPRESS)
RUN = 'System.out.println(delivery.receipt(in.nextInt()));'

s = Script(STARTER)
s.say('마지막 도전이에요. 새 배송 두 종류의 배송비를 하위 클래스에서 바로잡아요. 영수증 코드는 그대로예요.', 'text:Delivery와 receipt는 고치지 않아요.')
s.say('main은 변수 타입이 늘 Delivery예요. 실제 객체가 어떤 클래스인지에 따라 fee가 달라져야 해요.', 'code:Delivery delivery = of(in.next());')
s.run(RUN)
s.say('세 영수증 모두 배송비 3000원이에요. 픽업과 특급의 fee가 한 번도 불리지 않았어요.', 'output')
s.patch(PICKUP_TODO, PICKUP, '픽업은 같은 모양의 fee를 재정의해 0원을 돌려줘요.')
s.run(RUN)
s.say('픽업 8000원 + 배송비 0원이에요. receipt가 실제 객체 Pickup의 fee를 불렀어요.', 'output')
s.patch(EXPRESS_BUG, EXPRESS_HALF, '특급의 본문만 기본 배송비에 2,000원을 더하게 바꿔 볼게요.')
s.run(RUN)
s.say('특급은 여전히 3000원이에요. fee(long)은 매개변수 타입이 달라 재정의가 아니라 새 메서드예요.', 'output')
s.patch(EXPRESS_HALF, EXPRESS, '@Override를 붙이고 매개변수를 int로 맞춰요. super.fee에 2,000원을 더해요.')
s.run(RUN)
s.say('특급 12000원 + 배송비 5000원이에요. 세 영수증이 요구와 같아요.', 'output')
s.say('조심하세요. @Override 없이 매개변수 타입을 바꾸면 컴파일은 되지만 재정의가 아니에요.', 'code:@Override int fee(int amount) { return super.fee(amount) + 2000; }')

GOAL = ('자, 마지막 도전이에요. 배송 종류 Pickup과 Express를 Delivery의 하위 클래스로 더해요. Delivery와 receipt는 고치지 않아요.\n\n'
        '픽업은 이름이 픽업이고 배송비가 0원이에요. 특급은 이름이 특급이고 기본 배송비에 2,000원을 더해요. '
        '준비 입력 `standard 10000 pickup 8000 express 12000`이면 '
        '`일반 10000원 + 배송비 3000원`, `픽업 8000원 + 배송비 0원`, `특급 12000원 + 배송비 5000원`이 나와야 해요. '
        '채점은 다른 입력으로도 실행해요.\n\n'
        + todo('코드 실행 버튼을 눌러 세 영수증의 배송비를 확인하세요.',
               'Pickup에 배송비 0원을 돌려주는 fee 재정의를 쓰세요.',
               'Express의 fee가 Delivery의 fee를 재정의하고 기본 배송비에 2,000원을 더하도록 고치세요.',
               '코드 실행 버튼을 눌러 세 영수증이 요구와 같은지 확인하세요.',
               '수정한 코드를 제출하세요.'))

SPEC = dict(
    key='java-inheritance-composition', course='java', revision='java-inheritance-composition-3',
    reason='재정의와 오버로드 구별·super 호출·final 템플릿을 묶어 새 종류의 배송비를 바로잡고, 변수 타입이 아닌 실제 객체가 메서드를 고르는지 여러 입력으로 채점하는 마지막 도전이에요.',
    grading='실제 JDK에 표준 입력 세 개를 넣어 영수증 출력을 채점해요. fee(long) 같은 오버로드, 고정 금액, 이름 오류는 실패해요.',
    unit=dict(id='unt_8e2c6a41-9d73-4b5f-a1e8-3c7f0b29d614', title='마지막 도전',
              objectives=['하위 클래스를 더해도 공통 코드가 실제 객체의 동작을 쓰게 해요.'],
              premise='배송 영수증이에요. 공통 영수증 코드와 main은 준비돼 있어요.'),
    step=dict(id=STEP, title='새 배송 두 종류의 배송비가 영수증에 반영되게 하세요',
              objectives=['재정의와 super 호출로 새 종류의 배송비를 바로잡고, 동적 디스패치로 같은 코드가 다르게 동작하는 것을 확인해요.'],
              core_flow='Pickup은 fee를 재정의하지 않았고 Express는 fee(long)으로 오버로드했다. 학생은 Pickup의 fee 재정의 한 줄과 Express의 fee 한 줄(@Override, int, super.fee + 2000)을 쓴다. '
                        '채점: 표준 입력 세 사례의 영수증. fee(long)은 오버로드라 기본 3000원이 나와 실패한다.',
              complexity=dict(new_concepts=[], prerequisite_experience='재정의·@Override·오버로드 구별·super 호출·final 템플릿을 각각 익혔어요.',
                              changed_condition='새 배송 두 종류의 fee 두 줄', observable_evidence='표준 입력 세 사례의 영수증 배송비',
                              learner_edited_lines=2, new_external_services=0)),
    task=dict(id=STEP, title='새 배송 두 종류의 배송비가 영수증에 반영되게 하세요', language='java', goal=GOAL,
              starter_code=STARTER, solution=SOLUTION, required=True,
              tests=[dict(input='standard 10000 pickup 8000 express 12000', expected='일반 10000원 + 배송비 3000원\n픽업 8000원 + 배송비 0원\n특급 12000원 + 배송비 5000원'),
                     dict(input='express 0', expected='특급 0원 + 배송비 5000원'),
                     dict(input='pickup 1 pickup 2 standard 3', expected='픽업 1원 + 배송비 0원\n픽업 2원 + 배송비 0원\n일반 3원 + 배송비 3000원')],
              narration=s.actions),
    cases=dict(expected_outputs=['일반 10000원 + 배송비 3000원\n픽업 8000원 + 배송비 3000원\n특급 12000원 + 배송비 3000원',
                                 '일반 10000원 + 배송비 3000원\n픽업 8000원 + 배송비 0원\n특급 12000원 + 배송비 3000원',
                                 '일반 10000원 + 배송비 3000원\n픽업 8000원 + 배송비 0원\n특급 12000원 + 배송비 3000원',
                                 '일반 10000원 + 배송비 3000원\n픽업 8000원 + 배송비 0원\n특급 12000원 + 배송비 5000원'],
               reject=[([['    @Override int fee(int amount) { return super.fee(amount) + 2000; }', '    int fee(long amount) { return super.fee((int) amount) + 2000; }']], 'An overload is not an override'),
                       ([['    @Override int fee(int amount) { return 0; }\n', '']], 'Pickup must override the fee'),
                       ([['return super.fee(amount) + 2000;', 'return 2000;']], 'Express adds to the base fee')],
               accept=[([['return super.fee(amount) + 2000;', 'return 5000;']], 'The same fee written as a number (the base fee is fixed)'),
                       ([['    @Override int fee(int amount) { return 0; }', '    int fee(int amount) { return 0; }']], '@Override is a check, not required for a correct override')]),
    review={'조심하세요. @Override 없이 매개변수 타입을 바꾸면 컴파일은 되지만 재정의가 아니에요.':
            '바로 앞 실행에서 fee(long)이 기본 배송비 3000원을 낸 실제 실수와 그 이유를 말해요. 이 수업 2번의 @Override 검사와 이어져요.'},
)
