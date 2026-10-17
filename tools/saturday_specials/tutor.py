"""Hand-authored, symbolic memory views. Arrows are relationships, not real addresses."""
import copy
import ast
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def source_cautions():
    # Read authored literal cautions without rebuilding Java scenario expectations.
    result = {}
    for name in ('c.py', 'java.py'):
        tree = ast.parse(Path(__file__).with_name(name).read_text(encoding='utf8'))
        for call in ast.walk(tree):
            if isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.func.id == 'make':
                result[ast.literal_eval(call.args[0])] = next(ast.literal_eval(k.value) for k in call.keywords if k.arg == 'caution')
    return result

# task: anchor, explanation before editing, symbolic state before/after.
# Values use the prepared first input (C: 3 8, Java: n=3), never invented addresses.
VIEWS = {
 'address': ('int *p =', '선언의 별은 포인터라는 뜻이에요. 식의 별은 주소를 따라 값을 읽어요.', ['p → b [8]', 'a [3]'], ['p → a [3]', 'b [8]']),
 'write-through': ('int copy =', 'copy에는 숫자만 복사됐어요. p만 원본 a로 이어져 있어요.', ['p → a [3]', 'copy [8] / b [8]'], ['p → a [8]', 'copy [3] / b [8]']),
 'retarget': ('int *p =', 'p와 별을 붙인 p는 다른 칸이에요. 왼쪽에 무엇을 쓰는지 보세요.', ['p → a [8]', 'b [8]'], ['p → b [8]', 'a [3]']),
 'array-step': ('int *p =', '포인터에 하나를 더하면 다음 원소로 가요. 바이트 하나를 더하는 뜻은 아니에요.', ['p → values[0] [3]', 'values[1] [8]'], ['p + 1 → values[1] [8]', 'p → values[0] [3]']),
 'precedence': ('p++;', 'p를 늘리면 가리킬 곳이 바뀌어요. 괄호로 묶으면 그 칸의 값을 늘려요.', ['p → values[1] [8]', 'values[0] [3]'], ['p → values[0] [4]', 'values[1] [8]']),
 'pointer-array': ('int *refs', '배열에는 숫자가 아니라 주소가 들어 있어요. 인덱스를 고른 뒤 주소를 따라가요.', ['refs[0] → a [11]', 'refs[1] → b [8]'], ['refs[0] → a [3]', 'refs[1] → b [11]']),
 'double-read': ('int **pp =', 'pp의 값은 포인터 칸의 주소예요. 별 하나마다 화살표를 한 번 따라가요.', ['pp → q → b [8]', 'p → a [3]'], ['pp → p → a [3]', 'q → b [8]']),
 'double-write': ('int **pp =', '별 하나면 p 칸에 도착해요. 별 두 개면 a의 값 칸에 도착해요.', ['pp → p → a [3]', 'b [11]'], ['pp → p → a [11]', 'b [8]']),
 'double-retarget': ('int **pp =', '이번에는 값 칸을 바꾸지 않아요. p가 담은 주소만 바꿔야 해요.', ['pp → p → a [8]', 'b [8]'], ['pp → p → b [8]', 'a [3]']),
 'function-copy': ('void move', '함수의 p는 주소를 복사받은 지역 칸이에요. 그 칸만 바꿔도 호출자 변수는 그대로예요.', ['함수 p → b [8]', '호출자 a [3]'], ['함수 p → a [8]', '호출자 b [8]']),
 'function-double': ('void redirect', '호출자의 p 칸 자체를 바꾸려면요. 그 p 칸의 주소를 함수에 건네야 해요.', ['함수 pp → 호출자 p → a [3]', 'next → b [8]'], ['함수 pp → 호출자 p → b [8]', 'a [3]']),
 'row-pointer': ('int (*row)', 'row는 정수 하나가 아닌 행을 가리켜요. 행을 고른 다음 그 행의 열을 골라요.', ['row[0] → [3, 8, 11]', 'row[1] → [9, 4, 24]'], ['row[1][0] → 9', '한 행을 이동하면 정수 세 칸을 건너가요']),
 'triple': ('int ***ppp', '별의 개수를 먼저 세지 말고 칸을 따라가요. 세 번째 화살표 끝이 실제 값 칸이에요.', ['ppp → pp → p → a [3]', 'b [11]'], ['ppp → pp → p → a [11]', 'b [8]']),
 'heap': ('int *data =', '포인터 선언만으로 배열이 생기진 않아요. 필요한 개수만큼 별도 공간을 확보해요.', ['data → NULL', '아직 사용할 배열이 없어요'], ['data → 확보한 배열 [3, 4]', '사용 뒤 free(data)로 공간을 반납해요']),
 'output-allocation': ('void build', 'out은 호출자의 포인터 칸을 가리켜요. 확보한 주소를 그 칸에 써야 해요.', ['out → data → NULL', '함수 밖에 전달할 주소가 없어요'], ['out → data → 배열 [8, 9]', '호출자가 사용하고 free(data)로 반납해요']),
 'parentheses': ('int **pp =', '먼저 별을 붙여 배열의 시작 주소를 얻어요. 그 주소에서 i번째 원소를 고르는 거예요.', ['values → [5, 8, 11]', '같은 첫 칸을 세 번 덮어썼어요'], ['values → [3, 4, 5]', '(*pp)[i] → i번째 값 칸']),
 'strings': ('const char **', '첫 선택은 문자열 주소를 고르는 단계예요. 그 주소를 문자열 출력에 전달해요.', ['pnames[0] → Red', 'k = 2 / Gold를 골라야 해요'], ['pnames + 2 → names[2] → Gold', '문자열의 주소를 골라 출력해요']),
 'string-character': ('const char **', '대괄호 하나는 문자열을 골라요. 다음 대괄호는 그 안의 글자를 골라요.', ['pnames[0] → Red → [1] e', 'k = 2'], ['pnames[2] → Gold → [1] o', '문자 위치도 영부터 세요']),
 'swap-addresses': ('const char *saved', '문자열의 글자를 고치는 문제가 아니에요. 배열이 가진 두 문자열 주소를 교환해요.', ['names[0] → Red', 'names[2] → Gold / 첫 칸을 다시 되돌렸어요'], ['names[0] → Gold', 'names[2] → Red / saved로 주소를 보관했어요']),
 'shared': ('static int count', '객체가 두 개여도 static 칸은 하나예요. a로 바꾼 값을 b로 읽어도 같아요.', ['Box.count [3] ← a, b', 'a와 b에 별도 count 칸은 없어요'], ['Box.count [5] ← a, b', '두 이름으로 읽어도 같은 공유 칸이에요']),
 'individual': ('int value;', 'static이 없으면 객체마다 자기 칸이 생겨요. 이름이 같아도 같은 저장 공간은 아니에요.', ['a → value [3]', 'b → value [5]'], ['a → value [5]', 'b → value [3]']),
 'constructor-count': ('int visits;', '생성자는 객체를 만들 때마다 실행돼요. 누적할 칸은 객체 밖에 하나만 둬야 해요.', ['인스턴스 visits / 객체마다 별도 칸', 'Box.visits 접근 → 컴파일 오류'], ['Box.visits: 3 → 4 → 5', 'new Box() 두 번 → 생성자 두 번']),
 'shadow': ('int total =', '가까운 지역 변수가 같은 이름을 가려요. 클래스 이름을 붙여 공유 칸을 지정해요.', ['지역 total [13] ← total', 'Main.total [3]'], ['지역 total [13]', 'Main.total [3] ← Main.total']),
 'parameter': ('static void setCount', '양쪽 count는 모두 매개변수를 뜻해요. 공유 칸을 고르려면 소속을 적어야 해요.', ['매개변수 count [7] → 자기 자신', 'Main.count [3]'], ['매개변수 count [7] → Main.count [7]', '오른쪽 값부터 구해 왼쪽 칸에 넣어요']),
 'instance-method': ('static int read', 'static 메서드에는 this가 없어요. 하지만 받은 객체를 통해 개인 칸을 읽을 수 있어요.', ['value만 읽기 → 대상 객체 없음', '컴파일 오류 / item이 필요해요'], ['item → Box 객체 → value [3]', 'read(item) → item.value']),
 'shared-and-own': ('static int shared', '공유 칸 하나와 개인 칸 둘을 나눠 보세요. 각 출력식에서 어느 칸을 읽는지 더해요.', ['Box.shared [6]', 'a.own [3] / b.own [4]'], ['Box.shared [3]', 'a.own [6] / b.own [4]']),
 'init-order': ('int value =', 'value를 저장한 다음 생성자 본문이 실행돼요. 나중에 base가 바뀌어도 다시 계산하지 않아요.', ['Box.base: 3 → 13', 'item.value: base + 1 → 4'], ['출력할 칸: item.value [4]', 'Box.base [13]과 구분해요']),
 'class-once': ('static {', '클래스 초기화와 객체 생성을 나눠 보세요. 객체 둘을 만들어도 static 블록은 반복하지 않아요.', ['클래스 초기화 → total [4]', '객체 a, b → 같은 total을 읽어요'], ['클래스 초기화 → total [3]', '객체 a, b → 같은 total을 읽어요']),
 'hidden-method': ('Base ref', 'static 호출은 선언한 자료형으로 정해요. 실제 객체가 자식이어도 이 규칙은 같아요.', ['Child.read() → 자식 static 메서드', 'ref: 선언 Base / 실제 객체 Child'], ['ref.read() → Base.read()', '정적 메서드는 클래스 이름으로 쓰면 더 분명해요']),
 'override': ('Base ref', '이번 메서드는 static이 아니에요. 실제 객체가 재정의한 메서드로 연결돼요.', ['new Base().read() → 부모 메서드', 'ref → Child 객체'], ['ref.read() → 자식 메서드', '선언 Base / 실제 객체 Child']),
 'reference': ('Box b =', 'new는 별도 객체를 만들어요. a를 대입하면 객체가 아닌 참조를 복사해요.', ['a → 객체 A: value [3]', 'b → 객체 B: value [2]'], ['a, b → 같은 객체: value [5]', 'b로 바꾼 칸을 a로 읽어요']),
 'mixed': ('Ticket a', '생성할 때의 번호는 객체에 남아요. 공유 next만 다음 번호로 계속 움직여요.', ['a.number [3] / b.number [4]', 'Ticket.next [5] / 기존 식 결과 5'], ['b.number − a.number + n → 4', '공유 next와 저장한 번호는 달라요']),
}


def line_range(source, fragment):
    start = source.find(fragment)
    assert start >= 0, ('missing tutor anchor', fragment)
    assert source.find(fragment, start + 1) < 0, ('ambiguous tutor anchor', fragment)
    return [source[:start].count('\n') + 1,
            source[:start + len(fragment)].count('\n') + 1]


def enrich(lesson):
    if not lesson['id'].startswith('sat-engineer-'):
        return
    lesson['revision'] = 'v1.0.3'
    cautions = source_cautions()
    for task in lesson['tasks']:
        anchor, explanation, before, after = VIEWS[task['id']]
        actions = task['narration']
        patch = next(a for a in actions if a['action'] == 'patch_code')
        starter = task['starter_code']
        solution = starter.replace(patch['before'], patch['after'], 1)
        setup = copy.deepcopy(next(a for a in actions if a['action'] == 'set_code'))
        setup['say'] = '먼저 입력과 변수의 연결을 살펴봐요.'
        setup['lines'] = line_range(starter, anchor)
        initial_run, final_run = [copy.deepcopy(a) for a in actions if a['action'] == 'run']
        # Run spotlights the actual button; code focus stays on the relevant expression.
        initial_run['lines'] = line_range(starter, patch['before'])
        final_run['lines'] = line_range(solution, patch['after'])
        readings = [copy.deepcopy(a) for a in actions if a['action'] == 'say' and a.get('target') == 'output']
        caution = dict(action='say', target='editor', text='조심하세요. ' + cautions[task['id']],
                       lines=line_range(starter, patch['before']))
        task['narration'] = ([dict(action='set_input', value='3 8\n')] if task['language'] == 'c' else []) + [setup,
            dict(action='say', target='editor', lines=line_range(starter, anchor), text=explanation),
            initial_run, readings[0],
            dict(action='say', target='memory', text=(
                 '첫 예제의 연결을 그림으로 짚어봐요. 주소 숫자 대신 어느 칸인지 표시했어요.' if task['language']=='c'
                 else '첫 예제를 그림과 함께 살펴봐요. 클래스와 객체의 역할을 나눠서 표시했어요.'),
                 diagram=dict(title='바꾸기 전 · 첫 예제 입력', rows=before)),
            caution, copy.deepcopy(patch), final_run, readings[1],
            dict(action='say', target='memory', text='같은 조건으로 바꾸기 전후를 비교해 보세요. 설명한 줄이 읽거나 바꾸는 대상을 짚어봐요.',
                 diagram=dict(title='바꾼 뒤 · 같은 첫 예제 입력', rows=after)),
            dict(action='say', target='editor', lines=line_range(solution, patch['after']),
                 text=('다른 예제 입력에서도 직접 실행해 보세요. 숫자가 달라도 같은 연결로 설명할 수 있나요?' if task['language']=='c'
                       else 'n을 다른 숫자로 바꿔서 실행해 보세요. 숫자가 달라도 같은 원리로 설명할 수 있나요?')),
            dict(action='submit')]
