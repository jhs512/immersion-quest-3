"""java-testing final challenge: write the JUnit checks for a new rule; the grader runs them against real faulty versions."""
from _common import Script, todo

STEP = 'stp_5b0e8c43-1d76-4a29-b3f8-9c2d6e75a1f0'
TODO = '        // 여기에 정상·경계·거절 사례를 검사하는 줄을 쓰세요.'
STARTER = f'''import org.junit.jupiter.api.Test;
import static org.assertj.core.api.Assertions.*;
class MainTest {{
    @Test void pointRules() {{
{TODO}
    }}
}}
'''
BOUNDARY = '''        // 기준 바로 아래 금액은 적립이 없어요.
        assertThat(Points.of(9999)).isEqualTo(0);
        // 기준 금액부터 1%를 적립해요.
        assertThat(Points.of(10000)).isEqualTo(100);'''
BIGGER = '''        // 기준보다 큰 금액도 그 금액의 1%예요.
        assertThat(Points.of(25000)).isEqualTo(250);'''
REJECT = '''        // 음수 금액은 약속한 예외로 거절해요.
        assertThatThrownBy(() -> Points.of(-1)).isInstanceOf(IllegalArgumentException.class);'''
SOLUTION = STARTER.replace(TODO, BOUNDARY + '\n' + BIGGER + '\n' + REJECT)
POINTS = '''class Points {
    // 만 원 이상 주문은 금액의 1%를 적립해요. 그 아래는 0점, 음수 금액은 거절해요.
    static int of(int amount) {
        if (amount < 0) throw new IllegalArgumentException("negative");
        return amount >= 10000 ? amount / 100 : 0;
    }
}
'''
MUTANTS = [POINTS.replace('amount >= 10000', 'amount > 10000'),
           POINTS.replace('return amount >= 10000 ? amount / 100 : 0;', 'return amount / 100;'),
           POINTS.replace('if (amount < 0) throw new IllegalArgumentException("negative");', 'if (amount < 0) return 0;'),
           POINTS.replace('amount / 100 : 0', 'amount / 10 : 0'),
           POINTS.replace('amount / 100 : 0', '100 : 0')]

s = Script(STARTER)
s.say('마지막 도전이에요. 새 적립 규칙을 지키는지 확인하는 테스트를 직접 써요.', 'text:만 원 이상 주문은 금액의 1%')
s.say('제출하면 이 테스트를 맞는 Points와 잘못 만든 Points 다섯 개로 실행해요.', 'text:잘못 만든 Points 다섯 개')
s.run(first='@Test void pointRules()')
s.say('테스트 1개가 통과해요. 그런데 아무것도 검사하지 않으니 어떤 구현이든 통과해요.', 'output')
s.patch(TODO, BOUNDARY + '\n' + TODO, '경계 양쪽 9999원과 10000원을 기대값으로 적어요.')
s.run(first='assertThat(Points.of(10000))')
s.say('통과예요. 맞는 구현은 9999원에 0, 10000원에 100을 돌려줘요.', 'output')
s.say('조심하세요. 기대값을 Points.of로 계산해 적으면 구현이 틀려도 같이 틀려서 잡지 못해요.', 'code:isEqualTo(100)')
s.patch(TODO, BIGGER + '\n' + TODO, '1%를 정말 계산하는지 큰 금액도 하나 확인해요.')
s.patch(TODO, REJECT, '음수 금액이 약속한 예외로 거절되는지도 검사해요.')
s.run(first='assertThatThrownBy(() -> Points.of(-1))')
s.say('네 가지 검사가 모두 통과했어요. 정상·경계·거절을 각각 다른 줄로 확인해요.', 'output')

GOAL = ('자, 마지막 도전이에요. 적립 규칙 Points.of를 검사하는 JUnit 테스트를 써요. Points.java는 준비돼 있고 고치지 않아요.\n\n'
        '규칙은 만 원 이상 주문은 금액의 1%를 적립하고, 그 아래는 0점, 음수 금액은 IllegalArgumentException으로 거절하는 거예요. '
        '제출하면 맞는 Points와 잘못 만든 Points 다섯 개로 테스트를 실행해요. 맞는 구현에서는 통과하고, 잘못된 구현에서는 모두 실패해야 해요. '
        '기대값은 규칙에서 직접 계산해 적어요.\n\n'
        + todo('코드 실행 버튼을 눌러 빈 테스트가 아무것도 검사하지 않고 통과하는 것을 확인하세요.',
               '기준 바로 아래 금액과 기준 금액의 적립 점수를 검사하는 줄을 쓰세요.',
               '기준보다 큰 금액의 적립 점수를 검사하는 줄을 쓰세요.',
               '음수 금액이 IllegalArgumentException으로 거절되는지 검사하는 줄을 쓰세요.',
               '코드 실행 버튼을 눌러 맞는 구현에서 테스트가 통과하는지 확인하세요.',
               '작성한 테스트를 제출하세요.'))

SPEC = dict(
    key='java-testing', course='java', revision='java-testing-8',
    reason='새 규칙의 정상·경계·거절 사례를 스스로 골라 JUnit으로 쓰고, 실제 결함 구현 다섯 개를 모두 잡는지 채점하는 마지막 도전이에요.',
    grading='작성한 테스트를 맞는 Points로 실행해 통과하고, 경계·기준 없음·예외 없음·비율 오류·고정값 결함 구현 다섯 개에서 모두 실패해야 해요.',
    unit=dict(id='unt_9d6a2f71-4c38-4b05-8e9a-3f1b7c50d286', title='마지막 도전',
              objectives=['새 규칙의 테스트 사례를 직접 골라 결함을 잡아요.'],
              premise='새 적립 규칙이 생겼어요. 구현은 준비돼 있고 테스트 메서드는 비어 있어요.'),
    step=dict(id=STEP, title='새 적립 규칙의 테스트를 직접 쓰세요',
              objectives=['요구에서 정상·경계·거절 사례를 고르고 독립적으로 계산한 기대값으로 결함 구현을 잡아요.'],
              core_flow='Points.of와 빈 @Test가 있다. 학생은 경계 양쪽, 큰 금액, 음수 거절을 검사한다. 채점: 맞는 구현 통과 + 결함 다섯 개 탐지. '
                        '경계 검사가 없으면 > 결함을, 큰 금액이 없으면 고정값 결함을, 거절 검사가 없으면 예외 없음 결함을 놓쳐 실패한다.'),
    task=dict(id=STEP, title='새 적립 규칙의 테스트를 직접 쓰세요', language='junit', goal=GOAL,
              starter_code=STARTER, solution=SOLUTION, required=True, tests=[], entry_file='MainTest.java',
              files={'Points.java': POINTS}, mutations=[{'Points.java': mutant} for mutant in MUTANTS],
              narration=s.actions),
    cases=dict(expected_outputs=[{'junit_summary': dict(found=1, successful=1, failed=0)}] * 3,
               reject=[([[BOUNDARY, '        assertThat(Points.of(9999)).isEqualTo(0);']], 'Without the 10,000 case the > boundary bug passes'),
                       ([[BIGGER + '\n', '']], 'Without a larger amount a fixed 100 passes'),
                       ([['\n' + REJECT, '']], 'Without the rejection check the silent 0 passes'),
                       ([['isEqualTo(100);', 'isEqualTo(Points.of(10000));']], 'An expectation computed by the implementation catches nothing')],
               accept=[([['Points.of(25000)).isEqualTo(250)', 'Points.of(30000)).isEqualTo(300)']], 'Another larger amount'),
                       ([['Points.of(9999)).isEqualTo(0)', 'Points.of(5000)).isEqualTo(0)']], 'Another amount below the limit')]),
    review={'조심하세요. 기대값을 Points.of로 계산해 적으면 구현이 틀려도 같이 틀려서 잡지 못해요.':
            '이 수업 2번(구현과 독립된 기대값)의 실제 실수를 새 규칙에 옮겨 말해요. 반례 채점이 결함을 놓치는 것으로 확인해요.'},
)
