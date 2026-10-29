"""java-arrays final challenge: loop over any length, filter by a boundary, accumulate a sum and a count."""
from _common import Script, todo

STEP = 'stp_5e8a1d36-92c4-4f7b-a1d0-3c6b8e27f94a'
LOOP = '    // 여기에 모든 가격을 읽으며 합계와 개수를 늘리는 반복문을 쓰세요.'
STARTER = f'''void main() {{
    // 장바구니 가격들이에요. 개수는 주문마다 달라요.
    int[] prices = {{1200, 3000, 2500, 800}};
    // 2,000원 이상인 가격의 합계와 그런 가격의 개수를 구해요.
    int total = 0;
    int count = 0;
{LOOP}
    System.out.println("합계: " + total);
    System.out.println("개수: " + count);
}}
'''
ALL = '''    // 처음부터 배열 길이 직전 위치까지 차례로 읽어요.
    for (int index = 0; index < prices.length; index++) {
        total = total + prices[index];
    }'''
FILTERED = '''    // 처음부터 배열 길이 직전 위치까지 차례로 읽어요.
    for (int index = 0; index < prices.length; index++) {
        // 기준 이상인 가격만 합계와 개수에 넣어요.
        if (prices[index] >= 2000) {
            total = total + prices[index];
            count = count + 1;
        }
    }'''
SOLUTION = STARTER.replace(LOOP, FILTERED)

s = Script(STARTER)
s.say('마지막 도전이에요. 기준 이상 가격의 합계와 개수를 함께 구해요.', 'text:2,000원 이상인 가격만 골라')
s.say('total과 count는 0에서 시작하고, 마지막 두 줄이 결과를 출력해요.', 'code:int count = 0;')
s.run()
s.say('합계: 0, 개수: 0이에요. 아직 배열을 읽는 반복이 없거든요.', 'output')
s.patch(LOOP, ALL, '먼저 배열 길이만큼 돌며 모든 가격을 더해 볼게요.')
s.run()
s.say('합계: 7500이에요. 네 가격을 다 더했고 개수는 아직 그대로예요.', 'output')
s.patch(ALL, FILTERED, '더하는 줄을 2,000원 이상일 때만 실행하고, 같은 자리에서 개수도 하나 늘려요.')
s.run()
s.say('합계: 5500, 개수: 2예요. 3000과 2500만 골라 더했어요.', 'output')
s.say('조심하세요. 반복 조건을 prices.length - 1로 쓰면 마지막 가격을 건너뛰어요. 지금 배열은 마지막이 800이라 티가 안 나요.', 'code:index < prices.length')
s.patch('int[] prices = {1200, 3000, 2500, 800};', 'int[] prices = {2000, 1999, 2001};', '경계 가격으로 끝나는 다른 배열로 바꿔 볼게요.')
s.run()
s.say('합계: 4001, 개수: 2예요. 기준과 같은 2000과 마지막 2001까지 셌어요.', 'output')
s.patch('int[] prices = {2000, 1999, 2001};', 'int[] prices = {1200, 3000, 2500, 800};', '준비된 가격으로 되돌려요.')
s.run()
s.say('다시 합계: 5500, 개수: 2예요. 채점은 빈 배열과 더 긴 배열로도 실행해요.', 'output')

GOAL = ('자, 마지막 도전이에요. 가격 배열 prices에서 2,000원 이상인 가격만 골라 그 합계와 개수를 구해요. '
        '출력 두 줄은 준비돼 있어요.\n\n'
        '지금 배열이면 `합계: 5500`과 `개수: 2`가 나와야 해요. 채점은 빈 배열, 경계 가격으로 끝나는 배열, 더 긴 배열로 바꿔서도 실행해요.\n\n'
        + todo('코드 실행 버튼을 눌러 지금은 합계와 개수가 0인 것을 확인하세요.',
               '배열의 모든 위치를 차례로 읽는 반복문을 쓰세요.',
               '반복 안에서 2,000원 이상인 가격만 total에 더하고 count를 1 늘리세요.',
               '코드 실행 버튼을 눌러 두 줄이 요구와 같은지 확인하세요.',
               '수정한 코드를 제출하세요.'))

SPEC = dict(
    key='java-arrays', course='java', revision='java-arrays-9',
    reason='배열 길이 기준 반복·위치 읽기·조건·누적 두 개를 직접 조합하고, 빈 배열과 길이가 다른 배열로 다시 실행해 채점하는 마지막 도전이에요.',
    grading='실제 JDK 출력과 빈 배열·경계로 끝나는 배열·다섯 원소 배열로 바꾼 재실행을 채점해요. 마지막 원소 빠뜨림, > 경계, 개수 위치 오류, 고정 반복 횟수는 실패해요.',
    unit=dict(id='unt_9c4e2b70-1d83-4a6f-b5e9-07f3a2c8d164', title='마지막 도전',
              objectives=['반복·조건·누적을 한 반복문에서 함께 써요.'],
              premise='장바구니 가격 배열이에요. 이번에는 반복문을 처음부터 직접 써요.'),
    step=dict(id=STEP, title='2,000원 이상 가격의 합계와 개수를 구하세요',
              objectives=['배열 길이에 맞춘 반복 안에서 조건과 두 누적 값을 함께 다뤄요.'],
              core_flow='준비 코드에는 배열과 0인 total·count, 출력 두 줄만 있다. 학생은 길이 기준 반복과 조건, 두 누적을 직접 쓴다. '
                        '채점: 실제 JDK 출력과 빈 배열·{2000, 1999, 2001}·다섯 원소 배열 변형. prices.length - 1은 마지막 경계 가격을 놓쳐 실패한다.'),
    task=dict(id=STEP, title='2,000원 이상 가격의 합계와 개수를 구하세요', language='java', goal=GOAL,
              starter_code=STARTER, solution=SOLUTION, tests=[dict(input='', expected='합계: 5500\n개수: 2')], required=True,
              variations=[dict(values=dict(prices='{2000, 1999, 2001}'), expected='합계: 4001\n개수: 2'),
                          dict(values=dict(prices='{}'), expected='합계: 0\n개수: 0'),
                          dict(values=dict(prices='{500, 600, 700, 9000, 2000}'), expected='합계: 11000\n개수: 2')],
              narration=s.actions),
    cases=dict(expected_outputs=['합계: 0\n개수: 0', '합계: 7500\n개수: 0', '합계: 5500\n개수: 2', '합계: 4001\n개수: 2', '합계: 5500\n개수: 2'],
               reject=[([['index < prices.length;', 'index < prices.length - 1;']], 'The last price is skipped'),
                       ([['prices[index] >= 2000', 'prices[index] > 2000']], 'A 2,000 price must count'),
                       ([['            count = count + 1;\n        }', '        }\n        count = count + 1;']], 'Counting every price, not only the chosen ones'),
                       ([['index < prices.length;', 'index < 4;']], 'A fixed loop count fails other lengths')],
               accept=[([['count = count + 1;', 'count++;']], 'Increment operator'),
                       ([['prices[index] >= 2000', 'prices[index] > 1999']], 'The same integer boundary')]),
    review={'조심하세요. 반복 조건을 prices.length - 1로 쓰면 마지막 가격을 건너뛰어요. 지금 배열은 마지막이 800이라 티가 안 나요.':
            '이 수업 8번의 실제 실수(마지막 원소 빠뜨림)가 지금 예시로는 드러나지 않는다는 점과 그래서 다른 배열로 실행한다는 이유를 말해요.'},
)
