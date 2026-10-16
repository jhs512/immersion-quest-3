from .common import *

QUOTE_TESTS='''
@Test void crudAndStableIds() {
    var store = new QuoteStore();
    assertThat(store.list()).isEmpty();
    int first = store.add("시작", "민수"); int second = store.add("계속", "영희");
    assertThat(first).isEqualTo(1); assertThat(second).isEqualTo(2);
    assertThat(store.list()).containsExactly(new Quote(1,"시작","민수"),new Quote(2,"계속","영희"));
    assertThat(store.update(1,"다시","민수")).isTrue();
    assertThat(store.delete(1)).isTrue(); assertThat(store.delete(1)).isFalse();
    assertThat(store.update(99,"없음","없음")).isFalse();
    assertThat(store.add("끝", "수지")).isEqualTo(3);
    assertThat(store.list()).containsExactly(new Quote(2,"계속","영희"),new Quote(3,"끝","수지"));
}
@Test void returnedListCannotChangeStorage() {
    var store = new QuoteStore(); store.add("하나","가");
    try { store.list().clear(); } catch (UnsupportedOperationException ignored) { }
    assertThat(store.list()).hasSize(1);
}
'''
ARRAY='''
import java.util.*;
record Quote(int id, String content, String author) {}
class QuoteStore {
    // 인덱스는 저장 위치이고, ID는 삭제 후에도 재사용하지 않아요.
    private Quote[] data = new Quote[2];
    // 사용 중인 칸의 수와 다음 ID는 따로 관리해요.
    private int size = 0, nextId = 1;
    int add(String content, String author) {
        // 꽉 차면 더 큰 배열로 복사해요.
        if (size == data.length) data = Arrays.copyOf(data, data.length * 2);
        int id = nextId++;
        // 배열 끝에 새 객체를 넣고 사용 중인 길이를 늘려요.
        data[size++] = new Quote(id, content, author);
        return id;
    }
    List<Quote> list() {
        // 저장소의 배열을 밖으로 직접 내보내지 않아요.
        return List.copyOf(Arrays.asList(Arrays.copyOf(data, size)));
    }
    boolean update(int id, String content, String author) {
        // 저장 위치가 바뀌어도 ID로 같은 명언을 찾아요.
        for (int i = 0; i < size; i++) {
            if (data[i].id() == id) {
                data[i] = new Quote(id, content, author);
                // 찾은 자리만 바꾸고 탐색을 끝내요.
                return true;
            }
        }
        return false;
    }
    boolean delete(int id) {
        // 없는 ID이면 끝까지 확인한 뒤 false를 반환해요.
        for (int i = 0; i < size; i++) {
            if (data[i].id() == id) {
                // 뒤 원소를 앞으로 옮기고 끝의 참조를 비워요.
                System.arraycopy(data, i + 1, data, i, size - i - 1);
                data[--size] = null;
                return true;
            }
        }
        return false;
    }
}
'''
LIST='''
import java.util.*;
record Quote(int id, String content, String author) {}
class QuoteStore {
    private final List<Quote> data = new ArrayList<>();
    // 삭제해도 증가하는 ID는 되돌리지 않아요.
    private int nextId = 1;
    int add(String content, String author) {
        // 반환한 ID와 저장한 객체의 ID를 같게 유지해요.
        int id = nextId++;
        data.add(new Quote(id, content, author));
        return id;
    }
    List<Quote> list() { return List.copyOf(data); }
    // 수정은 새 record로 교체해 기존 ID를 보존해요.
    boolean update(int id, String content, String author) {
        for (int i = 0; i < data.size(); i++) {
            // 위치가 아닌 객체의 ID를 비교해요.
            if (data.get(i).id() == id) {
                data.set(i, new Quote(id, content, author));
                return true;
            }
        }
        return false;
    }
    boolean delete(int id) {
        // 삭제 여부를 호출한 쪽에 알려줘요.
        return data.removeIf(q -> q.id() == id);
    }
}
'''
CRUD_GOAL='''`record Quote(int id, String content, String author)`를 만드세요.
`QuoteStore`는 `add`, `list`, `update`, `delete`를 제공해요.
add는 1부터 증가하는 ID를 반환해요.
list는 등록 순서의 List<Quote>를 반환해요.
update(id, content, author)는 찾으면 수정하고 true예요.
delete(id)는 찾으면 삭제하고 true예요.
없는 ID는 false예요. 삭제한 ID는 재사용하지 마세요.
외부에서 list 결과를 바꿔도 원본은 유지돼야 해요.'''
lesson('wise-array','명언 게시판 1 · 배열 CRUD','명언의 ID와 저장 위치를 구분하며 CRUD를 만들어요.',[14145,14146],[
('요구사항을 자료와 동작으로 나누기','''
    명언은 ID, 내용, 작가를 가진 자료예요.
    등록·조회·수정·삭제를 CRUD라고 불러요.
    먼저 저장소만 만들고 콘솔 화면은 나중에 붙여요.
    입력과 출력을 한꺼번에 만들면 실수를 찾기 어렵죠.
    record는 값 묶음을 표현하는 자바 문법이에요.
    배열 길이는 고정이라 꽉 차면 복사해야 해요.
    이번에는 삭제 뒤 빈 자리를 앞으로 당겨요.
    조심하세요. 배열 위치를 ID로 사용하면 안 돼요.
    두 번째 명언을 지워도 세 번째 ID는 그대로예요.
    각 문제의 테스트 파일도 펼쳐서 읽어보세요.
    검사 버튼은 그 테스트를 실제로 실행해요.
'''),
('작게 만들고 확인하기','''
    먼저 add와 list를 구현해 실행하세요.
    첫 등록의 ID와 목록의 크기를 확인해요.
    다음에는 두 개를 등록하고 앞 항목을 지워요.
    남은 ID가 바뀌지 않았는지 보세요.
    마지막으로 없는 ID의 수정과 삭제를 확인해요.
    한꺼번에 정답을 붙이기 전에 실패를 읽어보세요.
    반복문 경계는 `i < size`여야 해요.
    배열 길이 전체를 돌면 비어 있는 칸도 만나죠.
''')],[jt('array-crud','배열로 명언 저장소 만들기',CRUD_GOAL+'\n내부 저장은 Quote[] 배열을 사용하세요.',ARRAY,QUOTE_TESTS,
starter='import java.util.*;\nrecord Quote(int id, String content, String author) {}\nclass QuoteStore {\n    // 배열과 CRUD 메서드를 작성하세요.\n}')],['java-objects'])

RQ='''
import java.util.*;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
class Rq {
    // 파싱은 생성할 때 한 번만 하고 조회는 저장한 값을 사용해요.
    private final String action;
    private final Map<String,String> params = new HashMap<>();
    Rq(String command) {
        // 첫 물음표에서만 동작과 쿼리를 나눠요.
        String[] parts = command.split("\\\\?", 2);
        action = parts[0];
        // 쿼리가 없으면 매개변수는 빈 사전으로 남아요.
        if (parts.length < 2 || parts[1].isEmpty()) return;
        for (String pair : parts[1].split("&")) {
            // 값 안의 등호는 보존해요. 빈 값도 남겨요.
            String[] kv = pair.split("=", 2);
            String key = decode(kv[0]);
            String value = kv.length == 2 ? decode(kv[1]) : "";
            // 같은 키가 반복되면 마지막 값을 선택해요.
            params.put(key, value);
        }
    }
    private String decode(String text) {
        // URL 인코딩의 바이트를 UTF-8 문자열로 되돌려요.
        return URLDecoder.decode(text, StandardCharsets.UTF_8);
    }
    String action() { return action; }
    // 키가 없을 때만 기본값을 반환해요. 빈 값은 그대로예요.
    String param(String key, String fallback) {
        return params.getOrDefault(key, fallback);
    }
    int intParam(String key, int fallback) {
        // 숫자 범위를 넘거나 숫자가 아니면 지정한 기본값을 줘요.
        try { return Integer.parseInt(params.get(key)); }
        catch (NumberFormatException e) { return fallback; }
    }
}
'''
RQ_TESTS='''
@Test void separatesActionAndQuery() {
    var rq = new Rq("수정?id=3&text=a=b");
    assertThat(rq.action()).isEqualTo("수정");
    assertThat(rq.intParam("id",-1)).isEqualTo(3);
    assertThat(rq.param("text","없음")).isEqualTo("a=b");
    assertThat(rq.intParam("missing",9)).isEqualTo(9);
}
@Test void emptyInvalidDuplicateAndEncoding() {
    var rq = new Rq("목록?x=&id=no&id=12&name=%ED%95%9C%EA%B8%80+%EC%9E%85%EB%A0%A5");
    assertThat(rq.param("x","기본")).isEmpty();
    assertThat(rq.intParam("id",-1)).isEqualTo(12);
    assertThat(rq.param("name","")).isEqualTo("한글 입력");
    assertThat(new Rq("목록").action()).isEqualTo("목록");
    assertThat(new Rq("목록?").param("id","기본")).isEqualTo("기본");
    assertThat(new Rq("목록?id=abc").intParam("id",7)).isEqualTo(7);
}
'''
lesson('wise-list','명언 게시판 2 · 컬렉션과 요청','배열 저장소를 List로 바꾸고 요청을 구분해요.',[14145],[
('동작은 유지하고 저장 방법 바꾸기','''
    앞 저장소의 호출 방법은 그대로 유지해요.
    배열의 복사와 자리 이동을 ArrayList에 맡겨요.
    이때 기존 테스트가 변경을 지켜줘요.
    외부에 원본 List를 그대로 반환하면 위험해요.
    호출한 쪽이 clear하면 저장소도 비워지거든요.
    List.copyOf로 변경할 수 없는 복사본을 줘요.
    Quote 자체도 record라 값을 직접 바꾸지 못해요.
'''),
('콘솔 명령에 조건 붙이기','''
    `삭제?id=3`은 동작과 조건을 함께 담아요.
    물음표 앞은 동작이고 뒤는 쿼리 문자열이에요.
    쿼리는 `&`로 여러 값을 연결해요.
    각 값은 첫 `=`에서만 나눠야 해요.
    조심하세요. 값 안에도 등호가 올 수 있어요.
    파싱을 Rq로 나누면 CRUD는 파싱을 몰라도 돼요.
    다음 TDD 수업에서 Rq를 경계값으로 검증해요.
''')],[jt('list-crud','같은 계약을 List로 구현하기',CRUD_GOAL+'\n내부 저장은 List<Quote>로 바꾸세요.',LIST,QUOTE_TESTS,
starter='import java.util.*;\nrecord Quote(int id, String content, String author) {}\nclass QuoteStore {\n}')],['java-design'])

TDD_IMPL=code('''
class Calculator {
    static int add(int a, int b) { return a + b; }
}
''')
TDD_TEST=code('''
import org.junit.jupiter.api.Test;
import static org.assertj.core.api.Assertions.*;
class CalculatorTest {
    @Test void differentPositiveValues() {
        // 같은 숫자만 검사하면 한쪽을 두 번 더해도 몰라요.
        assertThat(Calculator.add(2, 5)).isEqualTo(7);
    }
    @Test void zeroAndNegative() {
        // 0과 음수도 실제 입력의 일부예요.
        assertThat(Calculator.add(0, -3)).isEqualTo(-3);
        assertThat(Calculator.add(-4, 6)).isEqualTo(2);
    }
}
''')
tdd_files=junit('');tdd_files.pop('ExerciseTest.java');tdd_files['Calculator.java']=TDD_IMPL
tdd=task('write-tests','잘못된 덧셈을 잡는 테스트','Calculator.add의 JUnit 테스트를 작성하세요.\n서로 다른 양수, 0, 음수를 검사하세요.\n정상 구현은 통과하고 결함 구현은 실패해야 해요.\n빈 테스트나 무조건 통과하는 테스트는 인정하지 않아요.',TDD_TEST,entry='CalculatorTest.java',files=tdd_files,
starter='import org.junit.jupiter.api.Test;\nimport static org.assertj.core.api.Assertions.*;\nclass CalculatorTest {\n    // @Test 메서드를 작성하세요.\n}',mutations=[
{'Calculator.java':'class Calculator { static int add(int a,int b) { return a+a; } }'},
{'Calculator.java':'class Calculator { static int add(int a,int b) { return Math.abs(a)+Math.abs(b); } }'},
{'Calculator.java':'class Calculator { static int add(int a,int b) { return 7; } }'}])
lesson('tdd-basics','JUnit·AssertJ·Gradle과 TDD','실패를 먼저 확인하고 작은 구현으로 통과해요.',[14156],[
('실패를 확인하는 이유','''
    테스트 주도 개발(TDD)은 검사를 먼저 적어요.
    Red는 기대한 이유로 실패하는 단계예요.
    Green은 통과할 만큼만 구현하는 단계죠.
    Refactor는 동작을 유지하며 구조를 다듬어요.
    컴파일 실패와 기대값 불일치는 구분하세요.
    함수가 없으면 먼저 최소 선언부터 만들어요.
    다음에는 틀린 반환값을 두고 검사를 실행해요.
    실패를 읽고 실제 덧셈으로 바꿔 다시 실행해요.
    조심하세요. 통과만 보면 검사 자체의 오류를 몰라요.
    일부러 잘못된 구현을 넣어 실패도 확인하세요.
'''),
('JUnit과 Gradle 프로젝트','''
    JUnit의 @Test가 실행할 테스트를 지정해요.
    AssertJ의 assertThat은 결과를 비교해요.
    프로젝트 설정은 build.gradle에서 확인하세요.
    이 실습은 JUnit 5.13.4를 사용해요.
    AssertJ는 3.27.7로 고정했어요.
    JDK는 앞에서 설치한 25를 사용해요.
    Gradle이 설치돼 있으면 `gradle test`로 실행해요.
    앱은 같은 라이브러리를 콘솔 런처로 실행해요.
    첫 실행에는 의존성을 내려받아야 해요.
''')],[tdd,jt('make-green','테스트를 통과하는 덧셈','`Calculator.add(int,int)`를 구현하세요.\n정수 범위 안에서 두 값의 합을 반환해요.',TDD_IMPL, '''
@Test void addition() {
    assertThat(Calculator.add(2,5)).isEqualTo(7);
    assertThat(Calculator.add(-4,6)).isEqualTo(2);
    assertThat(Calculator.add(0,0)).isZero();
}
''',starter='class Calculator {\n    static int add(int a,int b) { return 0; }\n}')],['java-streams'])

lesson('tdd-rq','TDD로 요청 파서 만들기','정상 입력과 경계값을 구분하며 Rq를 구현해요.',[14156,14145],[
('Rq의 계약을 먼저 정하기','''
    Rq는 명령을 실행하지 않고 해석만 해요.
    동작 이름과 매개변수를 읽는 역할이에요.
    값이 없을 때의 기본값도 계약의 일부죠.
    빈 문자열은 없는 키와 다르게 취급해요.
    중복 키는 마지막 값을 사용하기로 정해요.
    URL 인코딩된 한글은 UTF-8로 해독해요.
    더하기 기호는 이 형식에서 공백을 뜻해요.
    숫자 변환 실패는 호출자가 정한 기본값을 줘요.
    조심하세요. split은 끝의 빈 값을 버릴 수 있어요.
    두 조각으로 제한해서 빈 값도 보존하세요.
'''),
('경계값으로 구현을 늘리기','''
    먼저 쿼리 없는 명령만 통과시켜 보세요.
    다음은 id 한 개, 여러 키 순서로 늘려요.
    값 안의 등호와 빈 값은 별도로 검사하세요.
    테스트 한 묶음이 통과할 때마다 실행해요.
    마지막에 변환과 파싱 메서드를 분리해요.
    이전 동작이 유지되는지 모든 테스트를 다시 돌려요.
''')],[jt('request-parser','Rq의 경계값 통과하기','`Rq(String)`을 구현하세요.\n`action()`, `param(String,String)`, `intParam(String,int)`를 제공해요.\n기본값과 중복 키 규칙은 개념 설명과 같아요.',RQ,RQ_TESTS,starter='class Rq {\n    // 파싱과 조회 메서드를 작성하세요.\n}')],['tdd-basics'])

LAYERS='''
import java.util.*;
record Quote(int id, String content, String author) {}
interface QuoteRepository {
    int save(String content, String author);
    List<Quote> findAll();
}
class MemoryQuoteRepository implements QuoteRepository {
    // 저장된 자료는 외부에서 직접 수정하지 못하게 숨겨요.
    private final List<Quote> rows = new ArrayList<>();
    public int save(String content, String author) {
        // 저장 방법과 ID 부여는 저장소의 책임이에요.
        int id = rows.size() + 1;
        rows.add(new Quote(id, content, author));
        return id;
    }
    public List<Quote> findAll() { return List.copyOf(rows); }
}
class QuoteService {
    // 구체적인 메모리 저장소 대신 인터페이스를 보관해요.
    private final QuoteRepository repository;
    QuoteService(QuoteRepository repository) { this.repository = repository; }
    int register(String content, String author) {
        // 입력 규칙은 화면이나 저장 방식과 분리해요.
        if (content == null || content.isBlank() || author == null || author.isBlank())
            throw new IllegalArgumentException("내용과 작가");
        return repository.save(content.trim(), author.trim());
    }
    List<Quote> list() { return repository.findAll(); }
}
class QuoteController {
    // 컨트롤러는 규칙을 복제하지 않고 서비스에 요청해요.
    private final QuoteService service;
    QuoteController(QuoteService service) { this.service = service; }
    String register(String content, String author) {
        // 사용자에게 보여줄 문구는 컨트롤러가 만들어요.
        return service.register(content, author) + "번 등록";
    }
}
'''
lesson('wise-layers','명언 게시판 3 · 역할과 테스트','Controller·Service·Repository를 분리해요.',[14145,14156],[
('세 역할의 경계','''
    컨트롤러는 요청을 받고 응답 문구를 만들어요.
    서비스는 명언 등록의 규칙을 지켜요.
    저장소는 자료를 저장하고 찾아줘요.
    클래스 수를 늘리는 것이 목적은 아니에요.
    화면과 저장 방법이 바뀌는 이유를 분리해요.
    저장소 인터페이스는 서비스가 필요한 동작만 둬요.
    조심하세요. 서비스에서 콘솔을 직접 읽지 마세요.
    그래야 입력 도구 없이도 규칙을 검사할 수 있어요.
'''),
('가짜 저장소로 규칙 확인하기','''
    테스트용 저장소로 전달된 값을 기록해요.
    공백을 정리한 값이 저장되는지 확인하세요.
    빈 내용은 저장소 호출 전에 거부해야 해요.
    실제 저장소 테스트는 저장 결과를 확인해요.
    서비스와 저장소의 검사를 따로 유지해보세요.
    마지막에 컨트롤러 응답까지 연결해서 확인해요.
''')],[jt('separate-roles','교체 가능한 저장소로 등록하기','제공한 테스트의 인터페이스를 구현하세요.\nQuoteRepository는 save와 findAll을 제공해요.\nMemoryQuoteRepository와 QuoteService를 만드세요.\nregister는 앞뒤 공백을 제거해요. 빈 내용·작가는 거부해요.\nQuoteController.register는 `ID번 등록`을 반환해요.',LAYERS, '''
@Test void wiringAndValidation() {
    var repo = new MemoryQuoteRepository(); var service = new QuoteService(repo);
    var controller = new QuoteController(service);
    assertThat(controller.register(" 시작 "," 민수 ")).isEqualTo("1번 등록");
    assertThat(service.list()).containsExactly(new Quote(1,"시작","민수"));
    assertThatThrownBy(() -> service.register(" ","작가")).isInstanceOf(IllegalArgumentException.class);
    assertThat(service.list()).hasSize(1);
}
@Test void serviceUsesInjectedRepository() {
    var seen = new java.util.ArrayList<String>();
    QuoteRepository fake = new QuoteRepository() {
        public int save(String c,String a) { seen.add(c+":"+a); return 73; }
        public java.util.List<Quote> findAll() { return java.util.List.of(); }
    };
    assertThat(new QuoteService(fake).register(" 글 "," 나 ")).isEqualTo(73);
    assertThat(seen).containsExactly("글:나");
}
''',starter='import java.util.*;\nrecord Quote(int id, String content, String author) {}\n// 인터페이스와 세 역할을 작성하세요.')],['tdd-rq'])

FILES='''
import java.util.*;
import java.nio.file.*;
import java.io.IOException;
class Exercise {
    static void save(Path file, List<String> rows) throws IOException {
        // JSON 문자열은 역슬래시와 따옴표를 먼저 보호해요.
        var escaped = rows.stream().map(s -> "\\\"" + s.replace("\\\\","\\\\\\\\").replace("\\\"","\\\\\\\"").replace("\\n","\\\\n").replace("\\r","\\\\r").replace("\\t","\\\\t") + "\\\"").toList();
        Files.writeString(file, "[" + String.join(",", escaped) + "]", java.nio.charset.StandardCharsets.UTF_8);
    }
    static List<String> load(Path file) throws IOException {
        // 존재하지 않는 파일은 첫 실행으로 취급해요.
        if (!Files.exists(file)) return List.of();
        String text = Files.readString(file).trim();
        // 문자열의 시작과 끝을 직접 따라가며 배열을 복원해요.
        var rows = new ArrayList<String>();
        int i = 1;
        if (!text.startsWith("[") || !text.endsWith("]")) throw new IOException("JSON 배열");
        while (i < text.length() - 1) {
            // 항목 사이 구분자를 건너뛰고 여는 따옴표를 확인해요.
            while (Character.isWhitespace(text.charAt(i)) || text.charAt(i) == ',') i++;
            if (text.charAt(i++) != '"') throw new IOException("JSON 문자열");
            var value = new StringBuilder(); boolean closed = false;
            // 닫는 따옴표를 만날 때까지 문자열 하나를 읽어요.
            while (i < text.length() - 1) {
                char c = text.charAt(i++);
                if (c == '"') { closed = true; break; }
                if (c == '\\\\') {
                    // 이스케이프는 두 문자를 실제 문자 하나로 바꿔요.
                    if (i >= text.length() - 1) throw new IOException("이스케이프");
                    char escaped = text.charAt(i++);
                    c = switch (escaped) { case 'n' -> '\\n'; case 'r' -> '\\r'; case 't' -> '\\t'; case '"' -> '"'; case '\\\\' -> '\\\\'; default -> throw new IOException("이스케이프"); };
                }
                value.append(c);
            }
            if (!closed) throw new IOException("닫는 따옴표");
            // 정상적으로 닫힌 문자열만 결과 목록에 넣어요.
            rows.add(value.toString());
        }
        return rows;
    }
    static List<String> page(List<String> rows, String keyword, int page, int size) {
        if (page < 1 || size < 1) throw new IllegalArgumentException("페이지");
        // 검색한 결과를 기준으로 페이지를 잘라요.
        return rows.stream().filter(s -> s.contains(keyword)).skip((long)(page - 1) * size).limit(size).toList();
    }
}
'''
lesson('wise-files','명언 게시판 4 · 파일·JSON·검색','종료 뒤에도 남는 자료와 검색·페이지를 만들어요.',[14145],[
('메모리와 파일은 수명이 달라요','''
    메모리 목록은 프로그램을 종료하면 사라져요.
    파일에 쓰고 다시 읽으면 다음 실행에도 남아요.
    UTF-8로 한글을 같은 방식으로 읽고 써요.
    JSON은 자료를 주고받는 텍스트 형식이에요.
    이번 문제는 문자열 배열 형식만 다뤄요.
    범용 JSON 파서를 만드는 문제는 아니에요.
    따옴표·역슬래시·줄바꿈·탭을 이스케이프해요.
    실제 서비스에서는 검증된 JSON 라이브러리를 써요.
    조심하세요. 문자열을 쉼표로만 나누면 깨져요.
    명언 내용에도 쉼표나 따옴표가 올 수 있거든요.
'''),
('검색한 뒤 페이지 나누기','''
    전체 자료를 먼저 검색 조건으로 걸러요.
    그 결과에 페이지 번호와 크기를 적용해요.
    페이지는 1부터 시작하기로 정해요.
    건너뛸 수는 `(page - 1) * size`예요.
    범위를 넘는 페이지는 빈 목록을 반환해요.
    자료가 없는 첫 실행도 정상 상태로 다뤄요.
    이번 범위에서는 MySQL 연결은 다루지 않아요.
''')],[jt('json-persistence','문자열 배열 저장·복원·페이지','`save(Path,List<String>)`, `load(Path)`를 구현하세요.\nUTF-8 JSON 문자열 배열로 저장해요.\n따옴표·역슬래시·개행·탭의 왕복을 보장하세요.\n없는 파일은 빈 목록이에요.\n`page(List<String>,String,int,int)`는 검색 후 페이지예요.',FILES, '''
@Test void roundTrip() throws Exception {
    var dir = java.nio.file.Files.createTempDirectory("mq3-json"); var file = dir.resolve("quotes.json");
    assertThat(Exercise.load(file)).isEmpty();
    var rows = java.util.List.of("한글, 쉼표", "따옴표 \\\"", "역슬래시 \\\\", "줄\\n바꿈", "탭\\t문자");
    Exercise.save(file,rows); assertThat(Exercise.load(file)).isEqualTo(rows);
    assertThat(java.nio.file.Files.readString(file)).startsWith("[").endsWith("]");
    Exercise.save(file,java.util.List.of()); assertThat(Exercise.load(file)).isEmpty();
}
@Test void searchThenPage() {
    var rows = java.util.List.of("a1","b2","a3","a4","b5");
    assertThat(Exercise.page(rows,"a",2,2)).containsExactly("a4");
    assertThat(Exercise.page(rows,"없음",1,2)).isEmpty();
    assertThatThrownBy(() -> Exercise.page(rows,"",0,2)).isInstanceOf(IllegalArgumentException.class);
}
''')],['wise-layers'])

lesson('java-recursion','재귀와 종료 조건','더 작은 문제를 호출하며 결과를 합쳐요.',[14151,14146],[
('호출마다 다른 값이 있어요','''
    재귀는 메서드가 자기 자신을 호출하는 방식이에요.
    종료 조건이 없으면 호출이 끝나지 않아요.
    매번 문제의 크기가 줄어드는지도 확인해야 해요.
    합계를 구할 때 n과 n-1의 합계로 나눠봐요.
    n이 0이면 더 호출하지 않고 0을 반환해요.
    조심하세요. 큰 입력은 호출 스택을 넘칠 수 있어요.
    재귀가 모든 반복문보다 좋은 것은 아니에요.
    이번에는 작은 수와 중첩 구조를 연습해요.
'''),
('괄호 깊이를 따라가기','''
    수식은 괄호 안에 또 수식이 들어갈 수 있어요.
    이처럼 중첩된 구조에 재귀가 잘 맞아요.
    `(`를 만나면 안쪽 문제를 처리해요.
    `)`를 만나면 안쪽 호출이 끝나야 하죠.
    현재 읽는 위치도 함께 움직여야 해요.
    계산기에서는 같은 문자를 두 번 읽지 않게 해요.
''')],[jt('recursive-sum','작은 문제로 합계 나누기','`sum(int n)`은 0부터 n까지 합을 반환해요.\n0 이상 1000 이하를 다뤄요. 음수는 거부하세요.\n반복문 대신 재귀 호출을 사용해보세요.', '''
class Exercise {
    static int sum(int n) {
        // 종료할 수 없는 입력을 먼저 거부해요.
        if (n < 0) throw new IllegalArgumentException("음수");
        if (n == 0) return 0;
        // 한 단계 작은 문제의 결과에 현재 수를 더해요.
        return n + sum(n - 1);
    }
}
''','''
@Test void baseCaseAndProgress() {
    assertThat(Exercise.sum(0)).isZero(); assertThat(Exercise.sum(1)).isEqualTo(1);
    assertThat(Exercise.sum(10)).isEqualTo(55); assertThat(Exercise.sum(1000)).isEqualTo(500500);
    assertThatThrownBy(() -> Exercise.sum(-1)).isInstanceOf(IllegalArgumentException.class);
}
''')],['wise-files'])

SEQUENCES='''
class Calc {
    static int run(String input) {
        // 공백을 건너뛰며 덧셈과 뺄셈의 부호를 기억해요.
        String text = input.replaceAll("\\\\s+", "");
        int total = 0, sign = 1, i = 0;
        // 한 반복마다 읽는 위치가 반드시 앞으로 움직여요.
        while (i < text.length()) {
            char c = text.charAt(i);
            // 연산자를 만나면 다음 숫자에 적용할 부호를 바꿔요.
            if (c == '+') { sign = 1; i++; continue; }
            if (c == '-') { sign = -1; i++; continue; }
            int value = 0;
            while (i < text.length() && Character.isDigit(text.charAt(i))) {
                // 여러 자리 숫자를 한 숫자로 조립해요.
                value = value * 10 + text.charAt(i++) - '0';
            }
            total += sign * value;
        }
        return total;
    }
}
'''
original=json.loads((ROOT/'.scratch/repo-curriculum/sources/arithmetic-cases.json').read_text(encoding='utf-8'))
def calc_tests(cases):
    return '@Test void originalCases() {\n'+ '\n'.join('    assertThat(Calc.run('+json.dumps(c['input'],ensure_ascii=False)+')).as("source case '+str(c['id'])+'").isEqualTo('+str(c['expected'])+');' for c in cases)+'\n}'
lesson('calculator-sequences','TDD 계산기 1 · 연속 덧셈·뺄셈','여러 자리 숫자와 연속 연산을 처리해요.',[14151],[
('원문 사례에서 한 단계씩','''
    처음에는 `1 + 1`을 통과시켜요.
    다음에는 다른 두 숫자를 넣어봐요.
    정답을 상수로 반환하면 바로 실패하죠.
    원문 사례 1~11은 덧셈과 뺄셈이에요.
    이 단계는 곱셈과 괄호를 아직 다루지 않아요.
    연산자는 왼쪽부터 차례로 적용해요.
    조심하세요. split("-")만으로 음수는 못 나눠요.
    숫자를 읽는 위치와 부호를 구분해 관리하세요.
    같은 테스트를 유지하며 중복 코드를 정리해요.
''')],[jt('sequential-calc','연속 정수 수식 계산하기','`Calc.run(String)`을 구현하세요.\n여러 자리 정수와 +, -를 처리해요.\n공백은 무시하세요. 입력은 유효한 수식이에요.',SEQUENCES,calc_tests(original[:11]),starter='class Calc {\n    static int run(String input) { return 0; }\n}')],['java-recursion'])

PARSER='''
class Calc {
    // 원문과 현재 위치는 이 파서 객체 안에서만 사용해요.
    private final String text;
    private int pos;
    private Calc(String text) { this.text = text; }
    static int run(String text) {
        // 호출마다 파서를 새로 만들어 위치를 공유하지 않아요.
        var parser = new Calc(text);
        int value = parser.expression();
        // 식 하나를 읽은 뒤 남은 글자가 있으면 유효하지 않아요.
        parser.space();
        if (parser.pos != text.length()) throw new IllegalArgumentException("남은 입력");
        return value;
    }
    private void space() {
        // 숫자 안의 공백까지 합치지 않고 토큰 사이만 건너뛰어요.
        while (pos < text.length() && Character.isWhitespace(text.charAt(pos))) pos++;
    }
    private boolean take(char expected) {
        // 기대한 기호가 있을 때만 위치를 한 칸 움직여요.
        space();
        if (pos < text.length() && text.charAt(pos) == expected) { pos++; return true; }
        return false;
    }
    private int expression() {
        // 곱셈을 먼저 완성한 항끼리 더하고 빼요.
        int value = term();
        // 같은 우선순위의 연산은 왼쪽 결과에 차례로 적용해요.
        while (true) {
            if (take('+')) value += term();
            else if (take('-')) value -= term();
            // 다음 연산자가 없으면 현재 식의 결과를 돌려줘요.
            else return value;
        }
    }
    private int term() {
        // 단항 값을 읽은 뒤 곱셈만 이 단계에서 반복해요.
        int value = unary();
        while (take('*')) value *= unary();
        return value;
    }
    private int unary() {
        // 단항 음수는 괄호나 숫자 앞에도 붙을 수 있어요.
        if (take('+')) return unary();
        if (take('-')) return -unary();
        // 괄호 안은 같은 문법의 작은 식이므로 재귀로 읽어요.
        if (take('(')) {
            int value = expression();
            if (!take(')')) throw new IllegalArgumentException("닫는 괄호");
            return value;
        }
        space(); int start = pos, value = 0;
        // 숫자 하나를 여러 자리의 정수로 조립해요.
        while (pos < text.length() && Character.isDigit(text.charAt(pos))) {
            value = value * 10 + text.charAt(pos++) - '0';
        }
        if (pos == start) throw new IllegalArgumentException("숫자");
        return value;
    }
}
'''
lesson('calculator-parser','TDD 계산기 2 · 우선순위·괄호·단항 음수','재귀 하강 파서로 원문 28개 사례를 통과해요.',[14151],[
('문법을 메서드로 나누기','''
    원문 제목은 다항식 계산기예요.
    실제 사례는 정수 수식 계산을 요구해요.
    여기서는 정수와 +, -, *, 괄호를 다뤄요.
    나눗셈·변수·소수는 이번 계약에 없어요.
    식(expression)은 항의 덧셈과 뺄셈이에요.
    항(term)은 단항 값의 곱셈이에요.
    단항 값은 부호·숫자·괄호 안 식이에요.
    이 순서로 호출하면 곱셈 우선순위가 생겨요.
    괄호 안에서는 다시 식 메서드를 호출해요.
    별도 Stack 자료구조 없이 재귀로 처리하세요.
'''),
('실패가 가리키는 문법 보기','''
    처음에는 곱셈 사례까지만 통과시켜 보세요.
    다음에는 괄호 하나와 중첩 괄호를 늘려요.
    마지막에 괄호 앞의 음수까지 처리해요.
    조심하세요. 빼기와 단항 음수는 역할이 달라요.
    `5 - (1 + 5)`의 첫 기호는 이항 연산이에요.
    `-(10 + 5)`의 기호는 값 하나의 부호예요.
    원문 28개를 모두 그대로 검사해요.
    공백·잘못된 괄호·연속 호출도 보강했어요.
    입력을 끝까지 읽었는지 확인해야 해요.
''')],[jt('recursive-parser','원문 28개와 경계값 통과하기','`Calc.run(String)`을 구현하세요.\n연산은 정수 +, -, *와 괄호예요. 단항 +/-도 허용해요.\n공백은 무시하고 곱셈을 먼저 계산해요.\n잘못된 입력은 IllegalArgumentException이에요.\n정수 범위 안의 작은 수식을 다뤄요.',PARSER,calc_tests(original)+'''
@Test void additionalBoundaries() {
    assertThat(Calc.run(" 2*(3 + 4) ")).isEqualTo(14);
    assertThat(Calc.run("--2 + -3")).isEqualTo(-1);
    assertThat(Calc.run("8-3-2")).isEqualTo(3);
    assertThat(Calc.run("+(2*3)")).isEqualTo(6);
    for (String s : new String[]{"", "(1+2", "1+", "2x", "()", "1 2"})
        assertThatThrownBy(() -> Calc.run(s)).isInstanceOf(IllegalArgumentException.class);
}
''',starter='class Calc {\n    static int run(String input) { return 0; }\n}')],['calculator-sequences'])
