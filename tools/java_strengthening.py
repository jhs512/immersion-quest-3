"""Focused object practice and compiler-backed contracts for the Java course."""
from pathlib import Path
import runpy
import json

contract = runpy.run_path(str(Path(__file__).with_name("java-contract.py")))["contract"]


def strengthen(lessons, program):
    method = lessons[8]
    method["checker"] = contract("Main", "twice", "{ return value * 3; }", '''
        var m = Main.class.getDeclaredMethod("twice", int.class);
        require(java.lang.reflect.Modifier.isStatic(m.getModifiers()), "twice에는 static을 붙이세요.");
        for (int v : new int[]{-997, -1, 0, 13, 1000})
            require(Main.twice(v) == v * 2, "twice는 전달한 값의 두 배를 반환해야 해요.");''')
    method["cases"] += [("13\n", "26\n"), ("-997\n", "-1994\n")]

    counter_type = '''    // 인스턴스 필드는 객체마다 따로 보관해요.
    static class Counter {
        int value;
        // 반환형이 없는 생성자로 처음 값을 정해요.
        Counter(int initial) { value = initial; }
        // 이 객체의 값만 전달한 만큼 늘려요.
        void add(int amount) { value += amount; }
    }
'''
    object_lesson = lessons[10]
    object_lesson["body"] = '''클래스는 데이터와 동작을 함께 정의해요.
객체는 그 클래스로 만든 실제 값이에요.
생성자(constructor)는 새 객체의 처음 값을 정해요.
이름이 클래스와 같고 반환형을 쓰지 않아요.

`new Counter(5)`는 처음 값이 5인 객체예요.
`Counter first`는 객체를 가리키는 참조예요.
참조(reference)는 객체 자체와 달라요.
`first.add(2)`는 그 객체의 값을 늘려요.

`new`를 두 번 쓰면 서로 다른 객체가 생겨요.
인스턴스 필드(instance field)는 각자 보관하죠.
`Counter alias = first;`는 새 객체를 만들지 않아요.
두 참조로 같은 객체를 가리켜요.

static 필드와 메서드는 클래스에 속해요.
인스턴스 메서드는 특정 객체의 값을 다뤄요.
static 중첩 클래스도 객체를 따로 만들 수 있어요.
아래 Counter는 Main 안에 둔 중첩 클래스예요.'''
    object_lesson.update(
        goal="처음 값과 늘릴 양을 정수로 입력받아요.\n각 값은 -100부터 100까지예요.\nCounter(int initial)과 void add(int amount)를 만드세요.\nint value는 인스턴스 필드예요.\n객체를 만들고 add를 호출한 뒤 value를 출력하세요.",
        hint="생성자는 value에 initial을 저장해요.\nadd는 그 객체의 value에 amount를 더해요.",
        caution="value에 static을 붙이면 객체끼리 공유해요. 각자의 값에는 붙이지 마세요.",
        solution=program('''// 입력을 읽고 처음 값을 가진 객체를 만들어요.
var scanner = new java.util.Scanner(System.in, "UTF-8");
Counter counter = new Counter(scanner.nextInt());
// 메서드가 객체의 값을 바꾸게 해요.
counter.add(scanner.nextInt());
System.out.println(counter.value);''', counter_type),
        stage=program("// 생성자로 정한 처음 값을 읽어요.\nCounter counter = new Counter(5);\nSystem.out.println(counter.value);", counter_type),
        example_output="5\n", cases=[("5 2\n", "7\n"), ("-4 9\n", "5\n"), ("0 -8\n", "-8\n"), ("100 -100\n", "0\n")],
        checker=contract("Counter", "add", "{ value += amount + 7; }", '''
        var field = Main.Counter.class.getDeclaredField("value");
        require(!java.lang.reflect.Modifier.isStatic(field.getModifiers()), "value는 객체마다 따로 보관하세요.");
        var a = new Main.Counter(-3); var b = new Main.Counter(17);
        require(a.value == -3 && b.value == 17 && a != b, "생성자가 각자의 처음 값을 정해야 해요.");
        a.add(8); a.add(-2);
        require(a.value == 3 && b.value == 17, "add는 호출한 객체의 값만 바꿔야 해요.");'''))

    def practice(suffix, title, goal, body, code, cases, extra, checks, owner="Counter", mutate="{ value += amount + 7; }"):
        return dict(suffix=suffix, title=title, goal=goal, body=body,
            solution=program(code, extra), cases=cases,
            hint="예제 숫자를 직접 적지 말고 입력값을 사용하세요.",
            caution="참조를 복사하는 것과 new로 객체를 만드는 것을 구분하세요.",
            checker=contract(owner, "add", mutate, checks))

    object_lesson["practices"] = [
        practice("two", "두 객체와 생성자", "정수 a, b, amount를 입력받아요.\n범위는 -100부터 100까지예요.\nnew Counter(a)와 new Counter(b)를 만드세요.\n첫 객체에만 add(amount)를 호출하세요.\n첫 객체와 둘째 객체의 value를 순서대로 출력하세요.",
            "new를 각각 호출해 두 객체를 만들어요.\n첫 객체를 바꿔도 둘째 값은 그대로예요.",
            '''// 각 입력값으로 서로 다른 객체를 만들어요.
var scanner = new java.util.Scanner(System.in, "UTF-8");
Counter first = new Counter(scanner.nextInt());
Counter second = new Counter(scanner.nextInt());
// 첫 객체만 바꾼 뒤 두 값을 비교해요.
first.add(scanner.nextInt());
System.out.println(first.value);
System.out.println(second.value);''',
            [("5 20 3\n", "8\n20\n"), ("-2 7 -5\n", "-7\n7\n"), ("0 0 9\n", "9\n0\n")], counter_type,
            '''var a = new Main.Counter(4); var b = new Main.Counter(9);
        a.add(6); require(a.value == 10 && b.value == 9 && a != b, "객체의 값은 따로 보관하세요.");'''),
        practice("alias", "참조를 공유하면", "정수 initial과 amount를 입력받아요.\n범위는 -100부터 100까지예요.\nCounter first = new Counter(initial)을 만드세요.\nCounter alias = first로 참조를 복사하세요.\nalias.add(amount)를 호출하세요.\nfirst.value와 alias.value를 순서대로 출력하세요.\n마지막 줄에는 first == alias를 출력하세요.",
            "참조를 대입해도 객체가 복사되지는 않아요.\nalias로 바꾼 값은 first로도 읽을 수 있어요.",
            '''// 객체는 하나이고 참조는 두 개예요.
var scanner = new java.util.Scanner(System.in, "UTF-8");
Counter first = new Counter(scanner.nextInt());
Counter alias = first;
// alias로 바꿔도 같은 객체의 값이 바뀌어요.
alias.add(scanner.nextInt());
System.out.println(first.value);
System.out.println(alias.value);
// ==로 같은 객체를 가리키는지 확인해요.
System.out.println(first == alias);''',
            [("5 3\n", "8\n8\ntrue\n"), ("-9 4\n", "-5\n-5\ntrue\n"), ("0 -7\n", "-7\n-7\ntrue\n")], counter_type,
            '''var a = new Main.Counter(3); var alias = a;
        alias.add(11); require(a.value == 14 && a == alias, "같은 객체의 필드를 바꾸세요.");'''),
        practice("static", "static 필드와 객체의 필드", "정수 a, b, x, y를 입력받아요.\n범위는 -100부터 100까지예요.\nCounter의 int value는 객체마다 따로 둬요.\nstatic int totalAdded는 늘린 양을 공유해요.\n생성자는 value만 초기화해요.\nadd(amount)는 value와 totalAdded에 amount를 더해요.\n두 객체를 만들고 각각 x, y만큼 늘리세요.\n두 value와 Counter.totalAdded를 순서대로 출력하세요.",
            "static 필드는 클래스에 한 개만 있어요.\n인스턴스 필드와 나란히 비교해 보세요.",
            '''// 두 객체는 각자의 value를 가지고 시작해요.
var scanner = new java.util.Scanner(System.in, "UTF-8");
Counter first = new Counter(scanner.nextInt());
Counter second = new Counter(scanner.nextInt());
// 각 객체를 바꾸며 공유 누적값도 늘려요.
first.add(scanner.nextInt());
second.add(scanner.nextInt());
System.out.println(first.value);
System.out.println(second.value);
// 공유 필드는 클래스 이름으로 읽어요.
System.out.println(Counter.totalAdded);''',
            [("5 20 3 4\n", "8\n24\n7\n"), ("-2 8 -5 7\n", "-7\n15\n2\n"), ("0 0 9 -9\n", "9\n-9\n0\n")],
            counter_type.replace("int value;", "int value;\n        // 모든 객체가 공유하는 누적값이에요.\n        static int totalAdded = 0;").replace("value += amount;", "value += amount; totalAdded += amount;"),
            '''require(java.lang.reflect.Modifier.isStatic(Main.Counter.class.getDeclaredField("totalAdded").getModifiers()), "totalAdded에는 static을 붙이세요.");
        require(!java.lang.reflect.Modifier.isStatic(Main.Counter.class.getDeclaredField("value").getModifiers()), "value는 인스턴스 필드예요.");
        Main.Counter.totalAdded = 0;
        var a = new Main.Counter(4); a.add(7); var b = new Main.Counter(9);
        require(Main.Counter.totalAdded == 7, "생성자에서 공유 누적값을 지우지 마세요.");
        b.add(-2); require(a.value == 11 && b.value == 7 && Main.Counter.totalAdded == 5, "객체 값과 공유 누적값을 함께 확인하세요.");''',
            mutate="{ value += amount + 7; totalAdded += amount + 7; }")]
    alias = object_lesson["practices"][1]
    alias["goal"] += "\n참조 변수 이름 first와 alias를 그대로 사용하세요."
    alias["checker"] = json.dumps([alias["checker"], contract("Main", "var:alias", "new Counter(first.value)", "")])
    shared = object_lesson["practices"][2]
    shared["checker"] = json.dumps([shared["checker"], contract("Counter", "var:totalAdded", "7", "")])

    final = lessons[11]
    extra = '''    // 점수 기록 객체가 합과 합격 인원을 보관해요.
    static class ScoreBook {
        int sum;
        int passed;
        // 배열의 길이를 생성자로 전달해요.
        final int count;
        ScoreBook(int count) { this.count = count; }
        // 공통 판단은 static 메서드로 나눠요.
        static boolean isPassed(int score) { return score >= 60; }
        // 점수마다 객체의 상태를 갱신해요.
        void add(int score) {
            sum += score;
            if (isPassed(score)) { passed++; }
        }
        // 객체에 보관한 값으로 정수 평균을 구해요.
        int average() { return sum / count; }
    }
'''
    final["body"] += "\n\n배열에 입력을 담고 메서드로 동작을 나눠요.\nScoreBook 객체가 합과 합격 인원을 보관해요.\n생성자로 인원을 전달해 평균을 구해요.\nstatic 판단 메서드는 객체 없이도 호출해요."
    final["goal"] += "\nScoreBook(int count)로 인원을 저장하세요.\nint sum, passed는 인스턴스 필드예요.\nvoid add(int score)는 합과 합격 수를 늘려요.\nstatic boolean isPassed(int score)는 60 이상을 판단해요.\nint average()는 정수 평균을 반환해요.\nmain은 객체에 점수를 전달하고 결과를 읽어요."
    final["hint"] = "ScoreBook의 add에서 isPassed를 호출하세요.\nmain의 반복문에서는 book.add(score)를 호출해요."
    final["solution"] = program('''// 배열에 학생들의 점수를 보관해요.
var scanner = new java.util.Scanner(System.in, "UTF-8");
int n = scanner.nextInt();
int[] scores = new int[n];
for (int i = 0; i < n; i++) {
    scores[i] = scanner.nextInt();
}
// 생성자에 인원을 전달하고 객체에 점수를 모아요.
ScoreBook book = new ScoreBook(n);
for (int score : scores) { book.add(score); }
// 객체가 보관한 결과와 메서드의 결과를 읽어요.
System.out.println(book.sum);
System.out.println(book.passed);
System.out.println(book.average());''', extra)
    final["checker"] = contract("ScoreBook", "add", "{ sum += score + 1; if (isPassed(score)) passed++; }", '''
        require(java.lang.reflect.Modifier.isStatic(Main.ScoreBook.class.getDeclaredMethod("isPassed", int.class).getModifiers()), "isPassed는 static 메서드예요.");
        for (int s : new int[]{0, 59, 60, 61, 100}) require(Main.ScoreBook.isPassed(s) == (s >= 60), "합격 경계값을 확인하세요.");
        var a = new Main.ScoreBook(3); var b = new Main.ScoreBook(1);
        a.add(59); a.add(60); a.add(100); b.add(0);
        require(a.sum == 219 && a.passed == 2 && a.average() == 73 && b.sum == 0 && b.average() == 0, "객체별 합과 평균을 확인하세요.");''')
    final["checker"] = json.dumps([final["checker"],
        contract("ScoreBook", "isPassed", "{ return false; }", ""),
        contract("ScoreBook", "average", "{ return -123; }", "")])
    # Code-reading questions replace exact repeats of the concept checks.
    reviews = {
        0: ('System.out.println("안녕");을 두 번 호출해요.\n출력은 몇 줄인가요?', ["2", "2줄"], "println은 호출할 때마다 줄을 바꿔요.\n두 번 호출하면 두 줄이 나와요."),
        1: ("int price = 5; int quantity = 4;\nprice * quantity의 결과는 무엇인가요?", ["20"], "두 정수 변수의 값을 곱해요.\n5에 4를 곱하면 20이에요."),
        2: ("정수 11을 4로 나눠요.\n몫과 나머지를 공백으로 구분하세요.", ["2 3"], "4가 두 번 들어가고 3이 남아요.\n/는 몫, %는 나머지를 구해요."),
        3: ("입력이 7 -2예요. nextInt()를 두 번 읽어요.\n두 값의 합은 무엇인가요?", ["5"], "두 입력은 7과 -2예요.\n음수도 정수 덧셈에 그대로 사용해요."),
        4: ("score가 60일 때 score > 60은 참인가요?\ntrue 또는 false로 답하세요.", ["false"], ">는 같은 값을 포함하지 않아요.\n60도 포함하려면 >=를 사용하세요."),
        5: ("sum은 0이에요. i가 1부터 3까지 늘어요.\nsum += i를 반복한 뒤 sum은 무엇인가요?", ["6"], "반복 밖에 둔 sum에 값을 누적해요.\n1, 2, 3을 더하면 6이에요."),
        6: ("0 전까지 더하는 while에 5 -2 0을 넣어요.\n출력할 합은 무엇인가요?", ["3"], "5와 -2만 더해요.\n0은 종료 신호로 사용해요."),
        7: ("int[] values = {4, 8, 12};\nvalues[1]의 값은 무엇인가요?", ["8"], "인덱스는 0부터 세어요.\n인덱스 1은 둘째 값인 8이에요."),
        8: ("twice(twice(3))의 결과는 무엇인가요?", ["12"], "안쪽 호출이 6을 반환해요.\n바깥 호출이 다시 두 배로 만들어요."),
        9: ('String a = new String("java");\nString b = new String("java");\na.equals(b)는 true 또는 false 중 무엇인가요?', ["true"], "두 객체가 달라도 문자열 내용은 같아요.\n내용을 비교할 때는 equals를 사용해요."),
        10: ("Counter a = new Counter(2); Counter b = a;\nb.add(5); 뒤의 a.value는 무엇인가요?", ["7"], "두 참조가 같은 객체를 가리켜요.\nb로 바꾼 값이 a로도 보여요."),
        11: ("점수 59, 60을 add로 넣으면 passed와 average는?\n두 값을 공백으로 구분하세요.", ["1 59"], "60만 합격이에요.\n119를 2로 정수 나눗셈하면 59예요.")}
    for i, review in reviews.items():
        lessons[i]["review"] = review
