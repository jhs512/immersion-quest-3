"""java-rq final challenge: build the request parser from scratch with every rule the lesson established."""
from _common import Script, todo

STEP = 'stp_3d6b9f52-8a17-4e4c-b9a5-1c0e7d82f36b'
CTOR_TODO = '''        // 여기에 ? 앞의 작업 이름과 ? 뒤의 조건들을 나눠 저장하세요.
        actionName = request;
        params = Map.of();'''
GET_TODO = '    String getParam(String name, String fallback) { return fallback; } // 조건 값을 돌려주도록 고치세요.'
INT_TODO = '    int getIntParam(String name, int fallback) { return fallback; } // 조건 값을 정수로 돌려주도록 고치세요.'
STARTER = f'''import java.util.*;
import java.util.stream.Collectors;

class Rq {{
    private final String actionName;
    private final Map<String, String> params;
    Rq(String request) {{
{CTOR_TODO}
    }}
    String getActionName() {{ return actionName; }}
{GET_TODO}
{INT_TODO}
}}

public class Main {{
    public static void main(String[] args) {{
        // 목록 요청에서 작업 이름, 검색어, 쪽 번호를 꺼내요.
        try {{
            Rq rq = new Rq(new Scanner(System.in).nextLine());
            // 세 값을 모두 읽은 뒤에 출력해요. 하나라도 잘못되면 invalid만 나와요.
            String keyword = rq.getParam("keyword", "전체");
            int page = rq.getIntParam("page", 1);
            System.out.println(rq.getActionName());
            System.out.println(keyword);
            System.out.println(page);
        }} catch (IllegalArgumentException error) {{
            System.out.println("invalid");
        }}
    }}
}}
'''
SPLIT = '''        String[] parts = request.split("\\\\?", 2);
        actionName = parts[0];
        // 조건이 없으면 빈 Map이에요.
        if (parts.length == 1 || parts[1].isEmpty()) { params = Map.of(); return; }
        params = Arrays.stream(parts[1].split("&", -1))
            .map(part -> part.split("=", -1))
            .collect(Collectors.toMap(pair -> pair[0], pair -> pair[1]));'''
CTOR = '''        String[] parts = request.split("\\\\?", 2);
        actionName = parts[0];
        // 조건이 없으면 빈 Map이에요.
        if (parts.length == 1 || parts[1].isEmpty()) { params = Map.of(); return; }
        params = Arrays.stream(parts[1].split("&", -1))
            .map(Rq::pair)
            .collect(Collectors.toMap(pair -> pair[0], pair -> pair[1], Rq::duplicate));
    }
    private static String[] pair(String part) {
        // 값 안의 등호와 빈 값은 보존하고, 등호 없는 조각은 거절해요.
        String[] pair = part.split("=", 2);
        if (pair.length != 2 || pair[0].isBlank()) throw new IllegalArgumentException("parameter");
        return pair;
    }
    // 같은 이름이 두 번 오면 하나를 몰래 고르지 않고 거절해요.
    private static String duplicate(String oldValue, String newValue) {
        throw new IllegalArgumentException("duplicate");'''
GET = '    String getParam(String name, String fallback) { return params.getOrDefault(name, fallback); }'
INT = '''    // 없으면 기본값, 있으면 정수로 바꿔요. 숫자가 아니면 parseInt가 거절해요.
    int getIntParam(String name, int fallback) {
        String value = params.get(name);
        return value == null ? fallback : Integer.parseInt(value);
    }'''
SOLUTION = STARTER.replace(CTOR_TODO, CTOR).replace(GET_TODO, GET).replace(INT_TODO, INT)
RUN = 'System.out.println(page);'

s = Script(STARTER)
s.say('마지막 도전이에요. 빈 Rq를 처음부터 완성해 목록 요청을 해석해요.', 'text:Rq의 생성자와 두 조회 메서드를 완성해요.')
s.say('main은 작업 이름, 검색어, 쪽 번호를 차례로 출력해요. 준비 입력은 list?page=2&keyword=java예요.', 'code:String keyword = rq.getParam("keyword", "전체");')
s.run(RUN)
s.say('요청 전체가 이름으로 나오고, 검색어와 쪽은 기본값이에요. 아직 나누지 않았거든요.', 'output')
s.patch(CTOR_TODO, SPLIT, '?로 이름과 조건을 나누고, &와 =로 조건을 Map에 모아요.')
s.patch(GET_TODO, GET, '검색어는 Map에서 읽고 없으면 기본값을 돌려줘요.')
s.patch(INT_TODO, INT, '쪽 번호는 문자열을 정수로 바꿔요.')
s.run(RUN)
s.say('list, java, 2가 나와요. 이름으로 조회해서 조건 순서와 상관없어요.', 'output')
s.input('list?keyword=a=b')
s.run(RUN)
s.say('list, a, 1이에요. = 로 전부 나누면 a=b가 세 조각이 돼 b를 잃어요.', 'output')
s.patch(SPLIT, CTOR, '= 는 처음 한 번만 나누고, 등호 없는 조각과 같은 이름의 반복은 거절해요.')
s.run(RUN)
s.say('list, a=b, 1이에요. 값 안의 등호가 남았고 쪽은 기본값이에요.', 'output')
s.say('조심하세요. 같은 이름이 두 번 와도 뒤의 값으로 덮으면 어떤 값을 썼는지 숨겨요. 그래서 거절해요.', 'code:throw new IllegalArgumentException("duplicate");')
s.input('list?page=2&keyword=java')
s.run(RUN)
s.say('다시 list, java, 2예요. 채점은 빈 값·잘못된 숫자·중복 이름으로도 실행해요.', 'output')

GOAL = ('자, 마지막 도전이에요. Rq의 생성자와 두 조회 메서드를 완성해요. 요청은 `작업이름?이름=값&이름=값` 모양이에요.\n\n'
        '규칙은 이 수업에서 정한 그대로예요. 조건이 없으면 기본값을 써요. 값 안의 등호와 빈 값은 그대로 보존해요. '
        '등호 없는 조건, 같은 이름의 반복, 정수가 아닌 쪽 번호는 `invalid`예요. '
        '준비 입력 `list?page=2&keyword=java`이면 `list`, `java`, `2`가 차례로 나와야 해요. 채점은 다른 요청 여러 개로도 실행해요.\n\n'
        + todo('코드 실행 버튼을 눌러 지금 결과를 확인하세요.',
               '생성자에서 ? 앞을 작업 이름으로, 뒤의 조건들을 이름과 값의 Map으로 저장하세요.',
               'getParam이 조건 값을, 없으면 기본값을 돌려주도록 고치세요.',
               'getIntParam이 조건 값을 정수로, 없으면 기본값을 돌려주도록 고치세요.',
               '실행 입력을 `list?keyword=a=b`로 바꿔 값 안의 등호가 남는지 확인하세요.',
               '수정한 코드를 제출하세요.'))

SPEC = dict(
    key='java-rq', course='java', revision='java-rq-7',
    reason='요청 분리·이름별 조회·값 보존·빈 값·중복 거절·정수 변환을 처음부터 직접 조합하고 요청 여덟 개로 채점하는 마지막 도전이에요.',
    grading='실제 JDK에 요청 여덟 개를 넣어 채점해요. = 를 전부 나누기, 중복 허용, 등호 없는 조각 허용, 빈 값을 기본값으로 바꾸기는 실패해요.',
    unit=dict(id='unt_0a7d4e96-3b52-4f81-a6c9-5e2b8f13d740', title='마지막 도전',
              objectives=['요청 해석 규칙 전체를 빈 Rq에 직접 구현해요.'],
              premise='목록 요청을 해석하는 빈 Rq예요. main은 준비돼 있어요.'),
    step=dict(id=STEP, title='빈 Rq를 완성해 목록 요청을 해석하세요',
              objectives=['요청 해석 책임을 Rq에 모으고 이 수업의 모든 경계 규칙을 지켜요.'],
              core_flow='Rq는 요청 전체를 이름으로 두고 기본값만 돌려준다. 학생은 ? 분리, & 분리, = 한 번 분리, 중복·등호 없음 거절, '
                        'getOrDefault, parseInt를 쓴다. 채점: 요청 여덟 개. split("=")는 a=b를 잃고 merge 없는 toMap은 다른 예외로 실패한다.'),
    task=dict(id=STEP, title='빈 Rq를 완성해 목록 요청을 해석하세요', language='java', goal=GOAL,
              starter_code=STARTER, solution=SOLUTION, required=True,
              tests=[dict(input='list?page=2&keyword=java', expected='list\njava\n2'),
                     dict(input='list', expected='list\n전체\n1'),
                     dict(input='list?keyword=', expected='list\n\n1'),
                     dict(input='list?keyword=a=b&page=10', expected='list\na=b\n10'),
                     dict(input='list?page=two', expected='invalid'),
                     dict(input='list?page=1&page=2', expected='invalid'),
                     dict(input='list?page', expected='invalid'),
                     dict(input='list?', expected='list\n전체\n1')],
              narration=s.actions),
    cases=dict(expected_outputs=['list?page=2&keyword=java\n전체\n1', 'list\njava\n2', 'list\na\n1', 'list\na=b\n1', 'list\njava\n2'],
               reject=[([['String[] pair = part.split("=", 2);', 'String[] pair = part.split("=");']], 'Splitting every = loses a=b and the empty value'),
                       ([['.collect(Collectors.toMap(pair -> pair[0], pair -> pair[1], Rq::duplicate));', '.collect(Collectors.toMap(pair -> pair[0], pair -> pair[1], (a, b) -> b));']], 'A repeated name must be refused'),
                       ([['if (pair.length != 2 || pair[0].isBlank())', 'if (pair[0].isBlank())']], 'A condition without = must be refused'),
                       ([['return params.getOrDefault(name, fallback);', 'return params.getOrDefault(name, "").isEmpty() ? fallback : params.get(name);']], 'An empty value is kept, not replaced')],
               accept=[([['            .map(Rq::pair)\n            .collect(Collectors.toMap(pair -> pair[0], pair -> pair[1], Rq::duplicate));',
                          '            .map(Rq::pair)\n            .collect(Collectors.toMap(pair -> pair[0], pair -> pair[1], Rq::duplicate, LinkedHashMap::new));']], 'Another map type with the same rules')]),
    review={'조심하세요. 같은 이름이 두 번 와도 뒤의 값으로 덮으면 어떤 값을 썼는지 숨겨요. 그래서 거절해요.':
            '이 수업 11번의 규칙(중복 거절)을 그대로 지켜야 하는 이유를 말해요. 양보 「와도」 뒤에 실제 대조(덮으면 숨겨짐)가 와요.'},
)
