"""java-collections final challenge: a Set for kinds, a Map that accumulates counts, a default for a missing key."""
from _common import Script, todo

STEP = 'stp_9e4c7a83-2b15-4f6d-8a39-c5d0e6b21f74'
FILL_TODO = '        // 여기에 items를 하나씩 읽어 kinds와 counts를 채우세요.'
STARTER = f'''import java.util.*;

public class Main {{
    public static void main(String[] args) {{
        Scanner in = new Scanner(System.in);
        // 첫 줄은 주문한 상품 이름들, 둘째 줄은 개수를 물어볼 상품 이름들이에요.
        String[] items = in.nextLine().split(" ");
        String[] queries = in.nextLine().split(" ");
        Set<String> kinds = new HashSet<>();
        Map<String, Integer> counts = new HashMap<>();
{FILL_TODO}
        System.out.println("종류: " + kinds.size());
        for (String query : queries) {{
            // 주문하지 않은 상품은 0으로 보여야 해요.
            System.out.println(query + ": " + counts.get(query));
        }}
    }}
}}
'''
KINDS = '''        for (String item : items) {
            // 집합은 같은 이름을 한 번만 남겨요.
            kinds.add(item);
        }'''
FILLED = '''        for (String item : items) {
            // 집합은 같은 이름을 한 번만 남겨요.
            kinds.add(item);
            // 이미 있던 개수에 1을 더하고, 처음이면 1로 시작해요.
            counts.put(item, counts.getOrDefault(item, 0) + 1);
        }'''
SOLUTION = STARTER.replace(FILL_TODO, FILLED).replace('counts.get(query)', 'counts.getOrDefault(query, 0)')

s = Script(STARTER)
s.say('마지막 도전이에요. 주문 목록에서 종류 수와 상품별 개수를 함께 구해요.', 'text:같은 상품이 여러 번 나올 수 있어요.')
s.say('준비 입력의 첫 줄은 pen book pen cup book pen, 둘째 줄은 pen bag이에요.', 'text:pen book pen cup book pen')
s.run()
s.say('종류: 0, pen: null, bag: null이에요. 아직 아무것도 담지 않았어요.', 'output')
s.patch(FILL_TODO, KINDS, '먼저 상품 이름을 집합에 담아요.')
s.run()
s.say('종류: 3이에요. 여섯 번 담았지만 pen, book, cup 세 이름만 남았어요.', 'output')
s.patch(KINDS, FILLED, '같은 반복에서 Map의 개수를 하나씩 늘려요.')
s.run()
s.say('pen: 3이 나와요. 그런데 bag: null이에요. 없는 키를 get으로 읽었거든요.', 'output')
s.patch('counts.get(query)', 'counts.getOrDefault(query, 0)', '없는 상품은 기본값 0으로 읽어요.')
s.run()
s.say('종류: 3, pen: 3, bag: 0이에요. 요구한 세 줄이에요.', 'output')
s.say('조심하세요. counts.put(item, 1)로 쓰면 같은 상품이 다시 나올 때 개수를 덮어써요.', 'code:counts.getOrDefault(item, 0) + 1')

GOAL = ('자, 마지막 도전이에요. 첫 줄의 주문 상품 이름들로 종류 수와 상품별 개수를 구해요. 같은 상품이 여러 번 나올 수 있어요.\n\n'
        '준비 입력은 첫 줄 `pen book pen cup book pen`, 둘째 줄 `pen bag`이에요. '
        '출력은 `종류: 3`, `pen: 3`, `bag: 0`이어야 해요. 주문하지 않은 상품은 0으로 보여요. 채점은 다른 입력으로도 실행해요.\n\n'
        + todo('코드 실행 버튼을 눌러 지금 출력을 확인하세요.',
               'items를 하나씩 읽어 상품 이름을 kinds에 담는 반복문을 쓰세요.',
               '같은 반복에서 counts의 그 상품 개수를 1 늘리세요.',
               '주문하지 않은 상품이 0으로 나오도록 개수를 읽는 줄을 고치세요.',
               '코드 실행 버튼을 눌러 세 줄이 요구와 같은지 확인하세요.',
               '수정한 코드를 제출하세요.'))

SPEC = dict(
    key='java-collections', course='java', revision='java-collections-8',
    reason='Set의 중복 제거, Map의 개수 누적, 없는 키의 기본값을 한 반복에서 직접 조합하고 여러 입력으로 채점하는 마지막 도전이에요.',
    grading='실제 JDK에 서로 다른 표준 입력 세 개를 넣어 출력을 채점해요. 목록으로 종류 세기, 개수 덮어쓰기, null 출력은 실패해요.',
    unit=dict(id='unt_3b8e6d14-5c27-4a9f-b1e0-8f2c7a43d956', title='마지막 도전',
              objectives=['Set과 Map을 한 문제에서 목적에 맞게 함께 써요.'],
              premise='주문 상품 이름이 한 줄로 들어와요. 출력 부분은 준비돼 있어요.'),
    step=dict(id=STEP, title='상품 종류 수와 상품별 개수를 함께 구하세요',
              objectives=['중복 없는 종류와 키별 누적, 없는 키의 기본값을 구별해 써요.'],
              core_flow='kinds·counts가 비어 있고 출력은 get을 쓴다. 학생은 반복에서 add와 누적 put을 쓰고 출력의 get을 기본값 조회로 고친다. '
                        '채점: 표준 입력 세 사례. put(item, 1)은 pen을 1로 덮어써 실패한다.'),
    task=dict(id=STEP, title='상품 종류 수와 상품별 개수를 함께 구하세요', language='java', goal=GOAL,
              starter_code=STARTER, solution=SOLUTION, required=True,
              tests=[dict(input='pen book pen cup book pen\npen bag', expected='종류: 3\npen: 3\nbag: 0'),
                     dict(input='cup\ncup cup', expected='종류: 1\ncup: 1\ncup: 1'),
                     dict(input='a b c d a\nd a z', expected='종류: 4\nd: 1\na: 2\nz: 0')],
              narration=s.actions),
    cases=dict(expected_outputs=['종류: 0\npen: null\nbag: null', '종류: 3\npen: null\nbag: null', '종류: 3\npen: 3\nbag: null', '종류: 3\npen: 3\nbag: 0'],
               reject=[([['counts.put(item, counts.getOrDefault(item, 0) + 1);', 'counts.put(item, 1);']], 'Overwriting loses repeated items'),
                       ([['counts.getOrDefault(query, 0)', 'counts.get(query)']], 'A missing item prints null'),
                       ([['System.out.println("종류: " + kinds.size());', 'System.out.println("종류: " + items.length);']], 'Counting every order line, not kinds')],
               accept=[([['counts.put(item, counts.getOrDefault(item, 0) + 1);', 'counts.merge(item, 1, Integer::sum);']], 'merge accumulates the same counts'),
                       ([['counts.getOrDefault(query, 0)', '(counts.containsKey(query) ? counts.get(query) : 0)']], 'An explicit containsKey check')]),
    review={'조심하세요. counts.put(item, 1)로 쓰면 같은 상품이 다시 나올 때 개수를 덮어써요.':
            '이 수업 10번의 실제 실수(누적 대신 덮어쓰기)와 이 입력에서의 결과(pen이 1)를 말해요.'},
)
