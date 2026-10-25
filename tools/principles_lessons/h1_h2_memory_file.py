"""H2: 연결 이름, 마지막 연결, 프로세스, 파일의 서로 다른 수명을 실제로 비교한다."""
from common import START_NEW, TODO_RUN_BEFORE, TODO_RUN_AFTER, TODO_SUBMIT, java_lesson

HEAD = 'import java.sql.*;\nimport java.util.*;\nclass Main {\n    public static void main(String[] args) throws Exception {\n'
TAIL = '\n    }\n}\n'

CHILD = '''// 제공 코드: 별도의 Java 프로세스에서 DB를 열어요. 이 파일은 바꾸지 않아요.
import java.sql.*;
class Child {
    public static void main(String[] args) throws Exception {
        try (Connection c = DriverManager.getConnection(args[0], "sa", "")) {
            if (args[1].equals("write")) {
                c.createStatement().execute("CREATE TABLE IF NOT EXISTS memo(title VARCHAR(100))");
                try (PreparedStatement p = c.prepareStatement("INSERT INTO memo VALUES (?)")) {
                    p.setString(1, args[2]); p.executeUpdate();
                }
            } else {
                try (ResultSet r = c.createStatement().executeQuery("SELECT title FROM memo ORDER BY title")) {
                    java.util.List<String> names = new java.util.ArrayList<>();
                    while (r.next()) names.add(r.getString(1));
                    System.out.println(String.join(", ", names));
                } catch (SQLException e) {
                    if (e.getSQLState().equals("42S04") || e.getSQLState().equals("42S02"))
                        System.out.println("표 없음");
                    else throw e;
                }
            }
        }
    }
}
'''

PROCESS_HELPER = '''
    // 제공 코드: 프로세스가 끝날 때까지 기다리고 실제 출력을 돌려줘요.
    static String child(String url, String action, String value) throws Exception {
        String exe = java.nio.file.Path.of(System.getProperty("java.home"), "bin", "java").toString();
        Process p = new ProcessBuilder(exe, "-Dstdout.encoding=UTF-8", "-Dstderr.encoding=UTF-8", "--class-path", System.getProperty("java.class.path"),
                "Child.java", url, action, value).redirectErrorStream(true).start();
        String out = new String(p.getInputStream().readAllBytes(), java.nio.charset.StandardCharsets.UTF_8).trim();
        if (p.waitFor() != 0) throw new IllegalStateException(out);
        return out;
    }
'''


def source(body, helper=''):
    return HEAD + body + TAIL[:-2] + helper + '}\n'


def problem(slug, title, new, intro, know, before, after, change, tests, observation, explanation,
            *, files=None, rejects=None):
    starter = source(before, PROCESS_HELPER if files else '')
    solution = source(after, PROCESS_HELPER if files else '')
    caution = {
        'connection-name': '조심하세요. mem: 뒤에 이름이 없으면 두 연결의 주소가 똑같아 보여도 서로 다른 DB예요.',
        'last-connection': '조심하세요. 연결을 닫지 않는 코드로 숨기면 자원이 새요. 연결은 닫고 DB의 수명을 따로 설정하세요.',
        'process-boundary': '조심하세요. DB_CLOSE_DELAY=-1은 같은 JVM 안의 설정이에요. 프로그램을 끄면 메모리 DB도 없어져요.',
        'file-identity': '조심하세요. 파일 DB도 주소가 같으면 메모가 섞여요. 프로세스가 다르다고 가게 데이터가 분리되지는 않아요.',
        'final-restart': '조심하세요. 매번 다른 파일 이름을 만들면 이전 메모를 못 찾아요. 세 프로세스가 같은 파일을 열어야 해요.',
    }[slug]
    return dict(slug=slug, title=title, language='java_libraries', libraries=['h2'],
                objectives=[new], start=START_NEW, intro=[intro], know=know,
                todo=[TODO_RUN_BEFORE, change, TODO_RUN_AFTER, TODO_SUBMIT],
                starter=starter, solution=solution, tests=tests, files=files or {},
                success=tests[0][1],
                complexity=dict(prior='기본 SQL과 try-with-resources로 연결을 닫는 코드를 읽어 봤어요.',
                                new=new, changed=change, evidence=observation, lines=2),
                narration=[('say', intro, 'text:' + intro), ('run',),
                           ('say', observation, 'output'),
                           ('patch', before, after, change), ('run',),
                           ('say', explanation, 'output'),
                           ('say', caution, 'text:' + know),
                           ('submit',)],
                review={observation: '제공 코드의 연결·프로세스 경계와 실패 출력을 설명해요. 별도 연결과 저장소의 공유 범위를 혼동하지 않게 해요.',
                        explanation: '수정 후 실제로 공유하는 저장소와 출력의 관계를 설명해요. 파일과 메모리의 수명을 구별해요.',
                        intro: '문제의 시작 코드가 만드는 상태를 설명해요. 학습자가 앞 스텝에서 만든 상태라고 주장하지 않아요.',
                        caution: '해당 스텝에서 혼동하기 쉬운 연결·JVM·파일의 경계를 구체적으로 지적해요. 실제 시작 상태와 수정 요구에 대응해요.'},
                rejects=rejects or [([(after, before)], '저장소의 경계를 바꾸기 전 코드로 되돌리면 메모가 사라지거나 섞여요.')])


B1 = '''        String name = new Scanner(System.in).nextLine();
        String url = "jdbc:h2:mem:";
        try (Connection a = DriverManager.getConnection(url, "sa", "");
             Connection b = DriverManager.getConnection(url, "sa", "")) {
            a.createStatement().execute("CREATE TABLE memo(title VARCHAR(100))");
            try (PreparedStatement p = a.prepareStatement("INSERT INTO memo VALUES (?)")) {
                p.setString(1, name); p.executeUpdate();
            }
            try (ResultSet r = b.createStatement().executeQuery("SELECT title FROM memo")) {
                r.next(); System.out.println(r.getString(1));
            } catch (SQLException e) {
                if (e.getSQLState().equals("42S04") || e.getSQLState().equals("42S02"))
                    System.out.println("다른 연결: 표 없음");
                else throw e;
            }
        }'''
A1 = B1.replace('jdbc:h2:mem:"', 'jdbc:h2:mem:shared"')

B2 = '''        String name = new Scanner(System.in).nextLine();
        String url = "jdbc:h2:mem:shared";
        try (Connection a = DriverManager.getConnection(url, "sa", "")) {
            a.createStatement().execute("CREATE TABLE memo(title VARCHAR(100))");
            try (PreparedStatement p = a.prepareStatement("INSERT INTO memo VALUES (?)")) {
                p.setString(1, name); p.executeUpdate();
            }
        }
        // 이 시점에는 열린 DB 연결이 하나도 없어요. 같은 프로세스에서 다시 열어요.
        try (Connection b = DriverManager.getConnection(url, "sa", "")) {
            try (ResultSet r = b.createStatement().executeQuery("SELECT title FROM memo")) {
                r.next(); System.out.println(r.getString(1));
            } catch (SQLException e) {
                if (e.getSQLState().equals("42S04") || e.getSQLState().equals("42S02"))
                    System.out.println("다시 연결: 표 없음");
                else throw e;
            }
        }'''
A2 = B2.replace('jdbc:h2:mem:shared"', 'jdbc:h2:mem:shared;DB_CLOSE_DELAY=-1"')

B3 = '''        String title = new Scanner(System.in).nextLine();
        String url = "jdbc:h2:mem:shared;DB_CLOSE_DELAY=-1";
        child(url, "write", title);
        // 쓰는 프로세스는 이미 끝났어요. 읽기는 다른 프로세스에서 해요.
        System.out.println("다른 프로세스: " + child(url, "read", ""));'''
A3 = B3.replace('jdbc:h2:mem:shared;DB_CLOSE_DELAY=-1', 'jdbc:h2:file:./memo')

B4 = '''        Scanner in = new Scanner(System.in);
        String first = in.next(); String second = in.next();
        String a = "jdbc:h2:file:./shared";
        String b = "jdbc:h2:file:./shared";
        child(a, "write", first); child(b, "write", second);
        System.out.println("A: " + child(a, "read", ""));
        System.out.println("B: " + child(b, "read", ""));'''
A4 = B4.replace('String a = "jdbc:h2:file:./shared";', 'String a = "jdbc:h2:file:./shop-a";').replace(
    'String b = "jdbc:h2:file:./shared";', 'String b = "jdbc:h2:file:./shop-b";')

B5 = '''        Scanner in = new Scanner(System.in);
        String a = in.nextLine(); String b = in.nextLine();
        String url = "jdbc:h2:mem:final;DB_CLOSE_DELAY=-1";
        child(url, "write", a);
        child(url, "write", b);
        System.out.println("재시작 후: " + child(url, "read", ""));'''
A5 = B5.replace('jdbc:h2:mem:final;DB_CLOSE_DELAY=-1', 'jdbc:h2:file:./final')

STEPS = [
    problem('connection-name', '두 연결에서 같은 메모를 읽게 하세요', '이름 없는 메모리 DB와 이름 있는 메모리 DB를 구분해요.',
            '연결 a에서 쓴 메모를 연결 b가 찾지 못해요. 두 연결은 동시에 열려 있어요.',
            '`jdbc:h2:mem:`은 연결마다 별도 DB예요. `jdbc:h2:mem:이름`은 같은 JVM 안에서 이름이 같은 DB를 공유해요.',
            B1, A1, 'URL에 같은 메모리 DB 이름을 넣으세요. 메모 문자열과 조회 코드는 유지하세요.',
            [('우유', '우유'), ('빵', '빵'), ('안녕 H2', '안녕 H2')],
            '다른 연결: 표 없음이 나와요. 열린 연결이 둘이어도 이름 없는 DB는 서로 달라요.',
            '우유가 나와요. 두 연결이 이름 있는 shared DB를 함께 봐요.'),
    problem('last-connection', '마지막 연결을 닫아도 JVM 안에서는 메모를 남기세요', '메모리 DB의 마지막 연결 종료와 JVM 종료를 구분해요.',
            '같은 이름으로 다시 열었는데 표가 사라져요. 첫 연결은 이미 닫혔어요.',
            'H2 메모리 DB는 기본적으로 마지막 연결이 닫히면 없어져요. `DB_CLOSE_DELAY=-1`은 JVM이 살아 있는 동안 DB를 유지해요. 프로세스 종료 뒤까지 저장하지는 않아요.',
            B2, A2, 'URL에 DB_CLOSE_DELAY=-1을 설정하세요. 연결을 닫는 코드는 유지하세요.',
            [('우유', '우유'), ('사과', '사과'), ('메모 2', '메모 2')],
            '다시 연결: 표 없음이에요. 닫힌 마지막 연결이 DB의 수명도 끝냈어요.',
            '우유가 나와요. 연결은 닫았지만 이 JVM은 아직 살아 있어요.'),
    problem('process-boundary', '쓰는 프로세스가 끝나도 메모를 남기세요', '파일 DB가 프로세스 밖에 데이터를 남기는 원리를 확인해요.',
            'write 프로세스를 끝낸 뒤 별도 read 프로세스를 실행해요. 같은 DB 이름인데 메모가 없어요.',
            '제공된 child 함수는 실제 별도 Java 프로세스를 만들어요. 메모리 DB 이름은 JVM 사이에서 공유되지 않아요. `jdbc:h2:file:./memo`는 현재 실습 폴더의 파일에 저장해요.',
            B3, A3, 'DB URL을 실습 폴더의 파일 DB로 바꾸세요. 두 프로세스는 그대로 두세요.',
            [('우유', '다른 프로세스: 우유'), ('빵', '다른 프로세스: 빵')],
            '다른 프로세스: 표 없음이에요. -1은 프로세스 종료를 견디는 저장 기능이 아니에요.',
            '다른 프로세스: 우유예요. 종료된 JVM 대신 파일이 메모를 보관했어요.', files={'Child.java': CHILD}),
    problem('file-identity', '두 가게의 저장 파일을 분리하세요', 'DB의 이름이나 파일 경로가 저장소의 정체성을 정한다는 것을 이해해요.',
            'A와 B가 같은 shared 파일 DB에 메모를 써요. 가게가 다른데 내용이 섞여요.',
            '서로 다른 연결이나 프로세스라고 해서 데이터가 자동으로 분리되지는 않아요. 같은 파일 DB 경로는 같은 저장소예요. 상대 경로는 실습 폴더를 기준으로 해요.',
            B4, A4, '두 URL이 서로 다른 파일을 가리키도록 고치세요. 실제 쓰기·읽기 코드는 유지하세요.',
            [('우유 빵', 'A: 우유\nB: 빵'), ('사과 귤', 'A: 사과\nB: 귤')],
            'A와 B에 같은 메모 두 개가 나와요. 두 주소가 같은 파일을 가리켜요.',
            'A에는 우유, B에는 빵만 나와요. 연결 수가 아니라 저장소 주소로 분리했어요.', files={'Child.java': CHILD}),
    problem('final-restart', '여러 번 재시작해도 두 메모를 보관하세요', '연결·JVM·파일의 수명 중 요구사항에 맞는 저장 방식을 골라요.',
            '메모를 한 줄씩 쓰는 프로세스가 매번 끝나요. 마지막 프로세스가 두 메모를 모두 읽어야 해요.',
            '이번 실행은 세 프로세스를 순서대로 실행해요. 앞에서 만든 파일 DB의 수명을 적용하세요. 제출을 다시 실행하면 새 실습 폴더에서 시작해요.',
            B5, A5, '세 프로세스가 함께 쓸 파일 DB URL을 구현하세요. 입력 메모를 코드에 직접 쓰지 마세요.',
            [('우유\n빵', '재시작 후: 빵, 우유'), ('귤\n사과', '재시작 후: 귤, 사과')],
            '재시작 후: 표 없음이에요. 두 번의 write가 끝날 때마다 JVM의 메모리도 사라졌어요.',
            '재시작 후: 빵, 우유예요. 마지막 JVM이 앞 두 JVM이 남긴 파일을 읽었어요.', files={'Child.java': CHILD}),
]

LESSON = java_lesson(
    key='h2-memory-file', folder='h2_memory_file', pilot='히', revision=1,
    title='H2 · 연결을 닫는 것과 프로그램을 끄는 것은 달라요',
    category='db', category_title='DB', track=None,
    category_evidence='실제 H2와 JDBC로 저장소의 수명을 확인해요.',
    track_evidence='기존 수업 기본 표시는 유지하고 새 수업의 트랙은 임의 확정하지 않아요.',
    audience='연결을 닫거나 프로그램을 다시 켰을 때 데이터가 남는 이유를 알고 싶은 학습자',
    prerequisites=['Java의 메서드 호출과 try-with-resources를 읽을 수 있어요.', '표 생성·INSERT·SELECT의 기본 의미를 알아요.'],
    objectives=['연결·이름 있는 메모리 DB·JVM·파일의 수명을 구분해요.', '프로세스를 바꾸는 실제 실험에서 메모리와 파일 DB의 차이를 설명해요.'],
    scope=['연결별 메모리 DB, 이름 있는 메모리 DB, 마지막 연결 종료, DB_CLOSE_DELAY, JVM 경계, 파일 경로'],
    out_of_scope=['H2와 다른 DB의 SQL 호환성', '여러 프로세스의 파일 DB 동시 접속', '운영 DB 구성'],
    sources=[('https://h2database.com/html/features.html#in_memory_databases', '이름 없는 DB와 이름 있는 DB, DB_CLOSE_DELAY의 범위를 확인해요.', 'H2 공식 문서와 실제 실행을 대조해요.')],
    description='메모 하나를 다른 연결, 다른 프로세스로 읽으며 무엇이 실제로 남는지 확인해요.',
    brief=('연결과 JVM, 파일의 서로 다른 수명을 배워요.', '매번 끝나는 프로그램에서도 두 메모를 보관해요.',
           ['동시에 열린 두 연결을 비교해요.', '마지막 연결을 닫고 다시 열어요.', '다른 JVM에서 파일 DB를 읽어요.'],
           '앱이 고정한 H2 2.4.240과 실제 JDK를 써요. 외부 DB 서버는 없어요.', '프로그램이 끝났는데 무엇이 메모를 기억할까요?'),
    representative=dict(slug='final-restart', expected_action='실제 파일 DB URL을 구현해요.', acceptance='세 프로세스가 순서대로 끝나도 두 입력 메모를 읽어요.',
                        reset='새 실습 폴더에서 시작해요.', narration='프로세스 종료 뒤 메모가 사라지는 것을 보고 파일 URL로 바꿔요.'),
    chapters=[dict(title='메모는 어디까지 살아 있나요?', objectives=['실제 연결·프로세스 경계를 바꾸어 저장소의 수명을 비교해요.'],
                   units=[dict(title='연결과 저장소의 경계', objectives=['같은 연결 문자열이 뜻하는 공유 범위를 설명해요.'],
                               premise='메모 한 줄을 실제 H2에서 쓰고 다른 곳에서 읽어요.', steps=STEPS)])])
