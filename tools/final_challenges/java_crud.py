"""java-crud final challenge: a small service that keeps ids unique, rejects missing and blank input and hands out copies."""
from _common import Script, todo

STEP = 'stp_6a2e8d71-4f39-4b6c-8d05-7c1f3b94e2a8'
ADD_TODO = '        return 0; // 빈 글은 거절하고, 한 번도 쓰지 않은 새 번호로 저장해 돌려주세요.'
UPDATE_TODO = '        return false; // 있는 글만 바꾸고, 빈 글은 거절하세요.'
DELETE_TODO = '        return false; // 있는 글만 지우고 결과를 돌려주세요.'
LIST_TODO = '        return quotes; // 돌려받은 쪽이 바꿔도 원본이 남도록 고치세요.'
STARTER = f'''import java.util.*;

class QuoteService {{
    // 글 번호와 내용이에요. 넣은 순서대로 보여요.
    private final Map<Integer, String> quotes = new LinkedHashMap<>();
    // 마지막으로 발급한 번호예요.
    private int lastId = 0;
    int add(String text) {{
{ADD_TODO}
    }}
    boolean update(int id, String text) {{
{UPDATE_TODO}
    }}
    boolean delete(int id) {{
{DELETE_TODO}
    }}
    Map<Integer, String> list() {{
{LIST_TODO}
    }}
}}

public class Main {{
    public static void main(String[] args) {{
        QuoteService service = new QuoteService();
        Scanner in = new Scanner(System.in);
        // 한 줄에 명령 하나예요: add 글, update 번호 글, delete 번호, clear, list
        while (in.hasNextLine()) {{
            String[] command = in.nextLine().split(" ", 3);
            try {{
                switch (command[0]) {{
                    case "add" -> System.out.println(service.add(command.length > 1 ? command[1] : ""));
                    case "update" -> System.out.println(service.update(Integer.parseInt(command[1]), command.length > 2 ? command[2] : ""));
                    case "delete" -> System.out.println(service.delete(Integer.parseInt(command[1])));
                    case "clear" -> {{ service.list().clear(); System.out.println("cleared"); }}
                    default -> System.out.println(service.list());
                }}
            }} catch (IllegalArgumentException error) {{
                System.out.println("invalid");
            }}
        }}
    }}
}}
'''
ADD = '''        // 잘못된 입력은 저장하기 전에 거절해요.
        if (text.isBlank()) throw new IllegalArgumentException("blank");
        // 지운 번호를 다시 쓰지 않도록 마지막 번호 다음을 발급해요.
        lastId++;
        quotes.put(lastId, text);
        return lastId;'''
ADD_REUSE = '''        // 잘못된 입력은 저장하기 전에 거절해요.
        if (text.isBlank()) throw new IllegalArgumentException("blank");
        int id = quotes.size() + 1;
        quotes.put(id, text);
        return id;'''
UPDATE = '''        if (!quotes.containsKey(id)) return false;
        if (text.isBlank()) throw new IllegalArgumentException("blank");
        quotes.put(id, text);
        return true;'''
DELETE = '        return quotes.remove(id) != null;'
LIST = '''        // 사본을 돌려줘야 바깥에서 비워도 저장한 글이 남아요.
        return new LinkedHashMap<>(quotes);'''
SOLUTION = STARTER.replace(ADD_TODO, ADD).replace(UPDATE_TODO, UPDATE).replace(DELETE_TODO, DELETE).replace(LIST_TODO, LIST)
RUN = 'default -> System.out.println(service.list());'

s = Script(STARTER)
s.say('마지막 도전이에요. 명령 줄로 움직이는 글 서비스를 완성해요. main은 준비돼 있어요.', 'text:QuoteService의 네 메서드를 완성해요.')
s.say('준비 입력은 add 시작, add 다음, delete 1, add 셋째, list예요. 번호는 한 번만 써야 해요.', 'text:지운 번호도 다시 쓰지 않아요.')
s.patch(DELETE_TODO, DELETE, '삭제는 있던 글을 지웠는지 remove의 결과로 알려 줘요.')
s.patch(ADD_TODO, ADD_REUSE, '추가는 먼저 글 개수로 번호를 정해 볼게요.')
s.run(RUN)
s.say('1, 2, true 다음 셋째가 2번이 돼 다음을 덮어썼어요. 개수로 번호를 정하면 지운 뒤 겹쳐요.', 'output')
s.patch(ADD_REUSE, ADD, '마지막으로 발급한 번호 다음을 써요. 지워도 번호는 줄지 않아요.')
s.run(RUN)
s.say('셋째가 3번이고 목록은 2=다음, 3=셋째예요.', 'output')
s.patch(UPDATE_TODO, UPDATE, '수정은 없는 번호면 false, 빈 글이면 예외로 원본을 지켜요.')
s.patch(LIST_TODO, LIST, '목록은 사본을 돌려줘요.')
s.input('add 남김\nupdate 9 없음\nupdate 1 \nclear\nlist')
s.run(RUN)
s.say('1, false, invalid, cleared 다음 목록에 1=남김이 그대로 있어요.', 'output')
s.say('조심하세요. list에서 원본 Map을 그대로 돌려주면 clear가 저장한 글까지 지워요.', 'code:return new LinkedHashMap<>(quotes);')

GOAL = ('자, 마지막 도전이에요. QuoteService의 네 메서드를 완성해요. main은 한 줄에 명령 하나를 읽어 결과를 출력해요.\n\n'
        '규칙은 이래요. add는 빈 글을 거절하고 새 번호를 돌려줘요. 번호는 1부터 차례로 발급하고, 지운 번호도 다시 쓰지 않아요. '
        'update와 delete는 있는 번호만 바꾸거나 지우고 true, 없으면 false예요. 빈 글로 수정하면 거절해요. 거절하면 `invalid`가 나와요. '
        'list가 돌려준 목록을 바깥에서 비워도 저장한 글은 남아야 해요. '
        '준비 입력이면 `1`, `2`, `true`, `3`, `{2=다음, 3=셋째}`가 나와야 해요. 채점은 다른 명령 순서로도 실행해요.\n\n'
        + todo('delete가 있는 글만 지우고 결과를 돌려주도록 고치세요.',
               'add가 빈 글을 거절하고 한 번도 쓰지 않은 새 번호로 저장하도록 고치세요.',
               '코드 실행 버튼을 눌러 지운 뒤 추가한 글의 번호를 확인하세요.',
               'update가 있는 글만 바꾸고 빈 글은 거절하도록 고치세요.',
               'list가 원본 대신 사본을 돌려주도록 고치세요.',
               '수정한 코드를 제출하세요.'))

SPEC = dict(
    key='java-crud', course='java', revision='java-crud-9',
    reason='추가·조회·수정·삭제의 정상·없는 대상·빈 입력 규칙, 재사용하지 않는 번호, 사본 반환을 한 서비스에서 직접 구현하고 명령 순서 네 개로 채점하는 마지막 도전이에요.',
    grading='실제 JDK에 명령 순서 네 개를 넣어 채점해요. 개수로 번호 발급, 없는 번호 수정 허용, 빈 글 저장, 원본 Map 반환은 실패해요.',
    unit=dict(id='unt_5c8f1a49-2d73-4e6b-9a07-4b3e6d81f2c5', title='마지막 도전',
              objectives=['네 동작의 규칙을 한 서비스에서 함께 지켜요.'],
              premise='명령 줄로 움직이는 글 서비스예요. main은 준비돼 있고 서비스 메서드는 비어 있어요.'),
    step=dict(id=STEP, title='네 동작의 규칙을 지키는 글 서비스를 완성하세요',
              objectives=['고유 번호·없는 대상·잘못된 입력·사본 반환 규칙을 함께 구현해요.'],
              core_flow='네 메서드가 고정값을 돌려준다. 학생은 add의 빈 글 거절과 lastId 발급, update·delete의 존재 확인, list의 사본을 쓴다. '
                        '채점: 명령 순서 네 개. 개수로 번호를 정하면 delete 뒤 add가 기존 글을 덮어 실패한다.'),
    task=dict(id=STEP, title='네 동작의 규칙을 지키는 글 서비스를 완성하세요', language='java', goal=GOAL,
              starter_code=STARTER, solution=SOLUTION, required=True,
              tests=[dict(input='add 시작\nadd 다음\ndelete 1\nadd 셋째\nlist', expected='1\n2\ntrue\n3\n{2=다음, 3=셋째}'),
                     dict(input='add 하나\nupdate 9 없음\nupdate 1 바꿈\nlist', expected='1\nfalse\ntrue\n{1=바꿈}'),
                     dict(input='add \nadd 진짜\ndelete 5\nupdate 1 \nlist', expected='invalid\n1\nfalse\ninvalid\n{1=진짜}'),
                     dict(input='add 남김\nclear\ndelete 1\nadd 다시\nlist', expected='1\ncleared\ntrue\n2\n{2=다시}')],
              narration=s.actions),
    cases=dict(expected_outputs=['1\n2\ntrue\n2\n{2=셋째}', '1\n2\ntrue\n3\n{2=다음, 3=셋째}', '1\nfalse\ninvalid\ncleared\n{1=남김}'],
               reject=[([[ADD, ADD_REUSE]], 'Numbering by size reuses an id after delete'),
                       ([['        if (!quotes.containsKey(id)) return false;\n', '']], 'Updating a missing id must be refused'),
                       ([['return new LinkedHashMap<>(quotes);', 'return quotes;']], 'Returning the stored map lets clear delete the quotes'),
                       ([['        if (text.isBlank()) throw new IllegalArgumentException("blank");\n        // 지운', '        // 지운']], 'A blank quote must be refused')],
               accept=[([['return new LinkedHashMap<>(quotes);', 'return new TreeMap<>(quotes);']], 'A sorted copy keeps the same order because ids only grow'),
                       ([['        return quotes.remove(id) != null;', '        if (!quotes.containsKey(id)) return false;\n        quotes.remove(id);\n        return true;']], 'Checking before removing')]),
    review={'조심하세요. list에서 원본 Map을 그대로 돌려주면 clear가 저장한 글까지 지워요.':
            '이 수업 6번의 실제 실수(원본 반환)를 이 서비스의 clear 명령 결과로 말해요. 채점 넷째 사례가 잡아요.'},
)
