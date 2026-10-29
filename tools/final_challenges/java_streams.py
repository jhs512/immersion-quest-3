"""java-streams final challenge: filter with a boundary, map, sum, count from a fresh stream and an Optional for none."""
from _common import Script, todo

STEP = 'stp_1c7e4a92-5b38-4d6f-9e21-8a0d3f6b5c47'
COUNT_TODO = '        long count = 0; // 기준 이상인 가격의 개수로 고치세요.'
SUM_TODO = '        int discounted = 0; // 기준 이상인 가격에서 100원씩 뺀 값의 합으로 고치세요.'
MAX_TODO = '        String highest = "없음"; // 기준 이상인 가격 중 가장 큰 값, 없으면 없음으로 고치세요.'
STARTER = f'''import java.util.*;
import java.util.stream.*;

public class Main {{
    public static void main(String[] args) {{
        Scanner in = new Scanner(System.in);
        // 첫 줄은 장바구니 가격들(비어 있을 수 있어요), 둘째 줄은 기준 금액이에요.
        List<Integer> prices = Arrays.stream(in.nextLine().trim().split(" "))
            .filter(text -> !text.isEmpty()).map(Integer::parseInt).toList();
        int minimum = Integer.parseInt(in.nextLine().trim());
{COUNT_TODO}
{SUM_TODO}
{MAX_TODO}
        System.out.println("개수: " + count);
        System.out.println("할인 합계: " + discounted);
        System.out.println("최고가: " + highest);
    }}
}}
'''
COUNT = '''        // 원본 목록에서 매번 새 흐름을 만들어요.
        long count = prices.stream().filter(price -> price >= minimum).count();'''
SUM = '''        int discounted = prices.stream().filter(price -> price >= minimum)
            .mapToInt(price -> price - 100).sum();'''
MAX = '''        // 고른 가격이 없으면 Optional이 비어 있어요.
        String highest = prices.stream().filter(price -> price >= minimum)
            .max(Integer::compare).map(String::valueOf).orElse("없음");'''
SOLUTION = STARTER.replace(COUNT_TODO, COUNT).replace(SUM_TODO, SUM).replace(MAX_TODO, MAX)

s = Script(STARTER)
s.say('마지막 도전이에요. 기준 이상 가격의 개수, 할인 합계, 최고가를 스트림으로 구해요.', 'text:기준 금액 이상인 가격만 골라')
s.say('준비 입력은 1200 3000 2500 800과 기준 2000이에요.', 'text:1200 3000 2500 800')
s.patch(COUNT_TODO, COUNT, '먼저 기준 이상만 걸러 개수를 세요.')
s.run()
s.say('개수: 2예요. 3000과 2500이 남았어요. 나머지 두 줄은 아직 처음 값이에요.', 'output')
s.patch(SUM_TODO, SUM, '같은 조건으로 다시 거른 뒤 100원씩 빼서 더해요.')
s.run()
s.say('할인 합계: 5300이에요. 2900과 2400을 더했어요.', 'output')
s.patch(MAX_TODO, MAX, '최고가는 max로 찾고, 없을 때를 위해 orElse로 없음을 정해요.')
s.run()
s.say('최고가: 3000이에요. 세 줄이 모두 요구와 같아요.', 'output')
s.say('조심하세요. 셀 때 쓴 스트림을 변수에 두고 다시 쓰면 이미 소비돼 예외가 나요.', 'code:prices.stream().filter(price -> price >= minimum).count()')
s.say('빈 장바구니도 확인해요. 고른 가격이 없을 때의 약속이에요.', 'text:고른 가격이 없으면 합계는 0, 최고가는 없음이에요.')
s.input('\n1000')
s.run()
s.say('개수: 0, 할인 합계: 0, 최고가: 없음이에요. 빈 결과에서 orElse의 값이 쓰였어요.', 'output')

GOAL = ('자, 마지막 도전이에요. 첫 줄의 가격들 중 기준 금액 이상인 가격만 골라 세 값을 구해요. 셋 다 스트림으로 써요.\n\n'
        '개수는 고른 가격의 수, 할인 합계는 고른 가격에서 100원씩 뺀 값의 합, 최고가는 고른 가격 중 가장 큰 값이에요. '
        '기준과 같은 가격도 골라요. 고른 가격이 없으면 합계는 0, 최고가는 없음이에요. '
        '준비 입력 `1200 3000 2500 800`과 기준 `2000`이면 `개수: 2`, `할인 합계: 5300`, `최고가: 3000`이 나와야 해요. '
        '채점은 빈 장바구니와 경계 가격으로도 실행해요.\n\n'
        + todo('기준 이상 가격의 개수를 세는 스트림을 쓰세요.',
               '기준 이상 가격에서 100원씩 뺀 값을 더하는 스트림을 쓰세요.',
               '기준 이상 가격 중 최고가를 찾고, 없으면 없음이 되게 쓰세요.',
               '코드 실행 버튼을 눌러 세 줄이 요구와 같은지 확인하세요.',
               '수정한 코드를 제출하세요.'))

SPEC = dict(
    key='java-streams', course='java', revision='java-streams-8',
    reason='filter·map·합계·개수·Optional을 한 문제에서 직접 조합하고, 빈 장바구니·경계 가격으로 계약을 채점하는 마지막 도전이에요.',
    grading='실제 JDK에 표준 입력 네 개(일반, 빈 장바구니, 경계, 모두 탈락)를 넣어 채점해요. 경계 제외, 빈 결과의 예외, 없음 대신 0 출력은 실패해요.',
    unit=dict(id='unt_5a1f8c36-2e97-4d4b-8b0c-6e9d3a72f158', title='마지막 도전',
              objectives=['여러 스트림 연산과 빈 결과 처리를 함께 써요.'],
              premise='장바구니 가격과 기준 금액이 입력으로 들어와요. 출력 세 줄은 준비돼 있어요.'),
    step=dict(id=STEP, title='기준 이상 가격의 개수·할인 합계·최고가를 구하세요',
              objectives=['filter·mapToInt·sum·count·max와 Optional의 기본값을 조합해 빈 결과까지 맞게 처리해요.'],
              core_flow='세 값이 처음 값으로 고정돼 있다. 학생은 원본에서 새 흐름을 만들어 개수, 할인 합계, Optional 최고가를 쓴다. '
                        '채점: 표준 입력 네 사례. > 경계는 2000을 빼먹고, get()은 빈 결과에서 예외가 나 실패한다.'),
    task=dict(id=STEP, title='기준 이상 가격의 개수·할인 합계·최고가를 구하세요', language='java', goal=GOAL,
              starter_code=STARTER, solution=SOLUTION, required=True,
              tests=[dict(input='1200 3000 2500 800\n2000', expected='개수: 2\n할인 합계: 5300\n최고가: 3000'),
                     dict(input='\n1000', expected='개수: 0\n할인 합계: 0\n최고가: 없음'),
                     dict(input='2000 1999\n2000', expected='개수: 1\n할인 합계: 1900\n최고가: 2000'),
                     dict(input='500 700\n1000', expected='개수: 0\n할인 합계: 0\n최고가: 없음')],
              narration=s.actions),
    cases=dict(expected_outputs=['개수: 2\n할인 합계: 0\n최고가: 없음', '개수: 2\n할인 합계: 5300\n최고가: 없음', '개수: 2\n할인 합계: 5300\n최고가: 3000', '개수: 0\n할인 합계: 0\n최고가: 없음'],
               reject=[([['long count = prices.stream().filter(price -> price >= minimum).count();', 'long count = prices.stream().filter(price -> price > minimum).count();']], 'A price equal to the minimum counts'),
                       ([['.max(Integer::compare).map(String::valueOf).orElse("없음");', '.max(Integer::compare).get().toString();']], 'An empty result must not throw'),
                       ([['.max(Integer::compare).map(String::valueOf).orElse("없음");', '.max(Integer::compare).map(String::valueOf).orElse("0");']], 'None is not the price 0'),
                       ([['.mapToInt(price -> price - 100).sum();', '.mapToInt(price -> price).sum();']], 'Each chosen price is discounted')],
               accept=[([['.max(Integer::compare).map(String::valueOf).orElse("없음");', '.mapToInt(Integer::intValue).max().stream().mapToObj(String::valueOf).findFirst().orElse("없음");']], 'An OptionalInt route to the same result'),
                       ([['.mapToInt(price -> price - 100).sum();', '.map(price -> price - 100).reduce(0, Integer::sum);']], 'reduce with identity 0 sums the same')]),
    review={'조심하세요. 셀 때 쓴 스트림을 변수에 두고 다시 쓰면 이미 소비돼 예외가 나요.':
            '이 수업 5번에서 본 실제 실수(소비된 스트림 재사용)를 이 문제처럼 같은 조건을 여러 번 쓸 때 저지르기 쉬워요. 그래서 매번 prices.stream()으로 새로 만들어요.'},
)
