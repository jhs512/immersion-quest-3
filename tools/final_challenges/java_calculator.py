"""java-calculator final challenge: add subtraction at the addition level, left to right, keeping validation."""
from _common import Script, todo

STEP = 'stp_8f1a6c34-7e29-4d5b-a3c8-0b9d2e64f71a'
LOOP = '        while (accept(\'+\')) value += term(); // 뺄셈도 같은 단계에서 왼쪽부터 계산하도록 고치세요.'
STARTER = f'''import java.util.Scanner;

class Calculator {{
    private final String text;
    private int position;
    Calculator(String text) {{ this.text = text; }}
    // 전체 입력을 다 읽었는지도 마지막에 확인해요.
    int evaluate() {{
        int value = expression();
        if (position != text.length()) throw new IllegalArgumentException("trailing");
        return value;
    }}
    // 덧셈 단계는 먼저 완성된 곱셈 항끼리 계산해요.
    private int expression() {{
        int value = term();
{LOOP}
        return value;
    }}
    // 곱셈 항의 책임은 숫자나 괄호 결과를 곱하는 거예요.
    private int term() {{
        int value = factor();
        while (accept('*')) value *= factor();
        return value;
    }}
    private int factor() {{
        // 괄호 안에서는 같은 표현식 규칙을 다시 호출해요.
        if (accept('(')) {{
            int value = expression();
            if (!accept(')')) throw new IllegalArgumentException("close");
            return value;
        }}
        int start = position;
        // 이번 작은 문법의 숫자는 ASCII 정수예요.
        while (position < text.length() && text.charAt(position) >= '0' && text.charAt(position) <= '9') position++;
        if (start == position) throw new IllegalArgumentException("number");
        return Integer.parseInt(text.substring(start, position));
    }}
    // 원하는 기호가 있을 때만 읽기 위치를 한 칸 옮겨요.
    private boolean accept(char symbol) {{
        if (position < text.length() && text.charAt(position) == symbol) {{
            position++;
            return true;
        }}
        return false;
    }}
}}

public class Main {{
    public static void main(String[] args) {{
        // 계산기의 입력은 공백 없는 정수·덧셈·뺄셈·곱셈·괄호예요.
        try {{
            String expression = new Scanner(System.in).nextLine();
            System.out.println(new Calculator(expression).evaluate());
        }} catch (IllegalArgumentException error) {{
            System.out.println("invalid");
        }}
    }}
}}
'''
RIGHT_ASSOC = '''        while (true) {
            if (accept('+')) value += term();
            // 기호 뒤를 전체 식으로 읽으면 오른쪽부터 묶여요.
            else if (accept('-')) value -= expression();
            else return value;
        }'''
LEFT = '''        while (true) {
            // 덧셈과 뺄셈은 같은 우선순위라 만나는 순서대로, 왼쪽부터 계산해요.
            if (accept('+')) value += term();
            else if (accept('-')) value -= term();
            else return value;
        }'''
SOLUTION = STARTER.replace(LOOP + '\n        return value;', LEFT)

s = Script(STARTER)
s.say('마지막 도전이에요. 계산기에 뺄셈을 더해요. 곱셈보다 늦게, 덧셈과 같은 순서로 계산해야 해요.', 'text:뺄셈은 덧셈과 같은 우선순위')
s.say('지금 덧셈 단계는 + 기호만 받아요. 준비 입력은 10-2*3이에요.', 'code:while (accept(\'+\')) value += term();')
s.run(first='System.out.println(new Calculator(expression).evaluate());')
s.say('invalid가 나와요. - 기호를 읽지 못해 10 뒤가 남은 입력이 됐어요.', 'output')
s.patch(LOOP + '\n        return value;', RIGHT_ASSOC, '- 뒤를 다시 식 전체로 읽어 볼게요. 쉽게 떠올리는 방식이에요.')
s.run(first='System.out.println(new Calculator(expression).evaluate());')
s.say('4가 나와요. 곱셈 2*3을 먼저 하고 10에서 뺐어요.', 'output')
s.input('10-2-3')
s.run(first='System.out.println(new Calculator(expression).evaluate());')
s.say('11이 나와요. 2-3을 먼저 묶어 10-(2-3)으로 계산했어요. 답은 5여야 해요.', 'output')
s.patch(RIGHT_ASSOC, LEFT, '- 뒤도 곱셈 항 하나만 읽고 바로 빼요. 반복이 왼쪽부터 차례로 계산해요.')
s.run(first='System.out.println(new Calculator(expression).evaluate());')
s.say('5가 나와요. 10-2를 먼저 하고 3을 뺐어요.', 'output')
s.say('조심하세요. 뺄셈을 곱셈 단계에 넣으면 10-2*3을 (10-2)*3처럼 계산해요.', 'code:while (accept(\'*\')) value *= factor();')
s.input('10-2*3')
s.run(first='System.out.println(new Calculator(expression).evaluate());')
s.say('다시 4예요. 채점은 괄호·음수 결과·잘못된 식으로도 실행해요.', 'output')

GOAL = ('자, 마지막 도전이에요. 계산기에 뺄셈 -를 더해요. 뺄셈은 덧셈과 같은 우선순위예요. 곱셈은 먼저 계산하고, 덧셈·뺄셈은 왼쪽부터 차례로 계산해요.\n\n'
        '준비 입력 `10-2*3`은 `4`예요. `10-2-3`은 `5`, `(10-2)*3`은 `24`, `5-10`은 `-5`예요. '
        '`2-`처럼 끝나지 않은 식과 `2+3x`처럼 남은 입력이 있는 식은 지금처럼 `invalid`예요.\n\n'
        + todo('코드 실행 버튼을 눌러 지금 결과를 확인하세요.',
               '덧셈 단계가 + 와 - 를 만나는 순서대로 계산하도록 반복을 고치세요.',
               '실행 입력을 `10-2-3`으로 바꿔 실행하고 5가 나오는지 확인하세요.',
               '수정한 코드를 제출하세요.'))

SPEC = dict(
    key='java-calculator', course='java', revision='java-calculator-7',
    reason='우선순위 단계·왼쪽부터 계산·괄호 재귀·남은 입력 검사를 함께 지키며 새 연산자를 직접 더하고 여러 식으로 채점하는 마지막 도전이에요.',
    grading='실제 JDK에 식 여덟 개를 넣어 채점해요. 오른쪽부터 묶기(10-2-3=11), 곱셈 단계의 뺄셈((10-2)*3), 남은 입력 허용은 실패해요.',
    unit=dict(id='unt_6e3b9d27-5a14-4c8f-b2e6-8d7f1a03c495', title='마지막 도전',
              objectives=['새 연산자를 알맞은 단계에 더해 우선순위와 계산 방향을 지켜요.'],
              premise='앞에서 완성한 계산기예요. 이번에는 바꿀 줄을 직접 찾아 고쳐요.'),
    step=dict(id=STEP, title='뺄셈을 덧셈과 같은 단계에서 왼쪽부터 계산하세요',
              objectives=['연산자의 우선순위 단계와 결합 방향을 코드 구조로 구현해요.'],
              core_flow='계산기는 +만 받는다. 학생은 덧셈 단계의 반복이 +와 -를 순서대로 처리하게 고친다. 채점: 식 여덟 개. '
                        '- 뒤를 expression()으로 읽으면 10-2-3이 11이 되어 실패하고, term 단계에 넣으면 10-2*3이 24가 되어 실패한다.'),
    task=dict(id=STEP, title='뺄셈을 덧셈과 같은 단계에서 왼쪽부터 계산하세요', language='java', goal=GOAL,
              starter_code=STARTER, solution=SOLUTION, required=True,
              tests=[dict(input='10-2*3', expected='4'), dict(input='10-2-3', expected='5'), dict(input='(10-2)*3', expected='24'),
                     dict(input='5-10', expected='-5'), dict(input='8-(3+1)', expected='4'), dict(input='2-', expected='invalid'),
                     dict(input='2+3x', expected='invalid'), dict(input='1+2*3-4', expected='3')],
              narration=s.actions),
    cases=dict(expected_outputs=['invalid', '4', '11', '5', '4'],
               reject=[([['else if (accept(\'-\')) value -= term();', 'else if (accept(\'-\')) value -= expression();']], 'Right-associative subtraction gives 10-2-3 = 11'),
                       ([['            else if (accept(\'-\')) value -= term();\n', ''], ['while (accept(\'*\')) value *= factor();', "while (true) {\n            if (accept('*')) value *= factor();\n            else if (accept('-')) value -= factor();\n            else break;\n        }"]], 'Subtraction at the multiplication level'),
                       ([['        if (position != text.length()) throw new IllegalArgumentException("trailing");\n', '']], 'Trailing input must still be rejected')],
               accept=[([[LEFT, '''        while (position < text.length() && (text.charAt(position) == '+' || text.charAt(position) == '-')) {
            // 기호를 확인한 뒤 같은 단계에서 왼쪽부터 계산해요.
            char symbol = text.charAt(position++);
            int next = term();
            value = symbol == '+' ? value + next : value - next;
        }
        return value;''']], 'Reading the operator character directly')]),
    review={'조심하세요. 뺄셈을 곱셈 단계에 넣으면 10-2*3을 (10-2)*3처럼 계산해요.':
            '이 수업의 단계 분리(곱셈 항 → 덧셈) 원리를 새 연산자에 적용할 때 실제로 하기 쉬운 배치 실수와 결과를 말해요. 반례 채점으로 확인해요.'},
)
