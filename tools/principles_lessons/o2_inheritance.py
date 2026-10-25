"""O2 상속과 컴포지션: 동적 디스패치·재정의와 오버로드·필드 가림·생성 순서·깨지기 쉬운 상속·컴포지션 (JDK 25)."""
from common import START_NEW, START_PREV, TODO_RUN_BEFORE, TODO_RUN_AFTER, TODO_SUBMIT, java_lesson

SHIP_MAIN = """
class Main {
    public static void main(String[] args) {
        java.util.Scanner in = new java.util.Scanner(System.in);
        List<Shipping> orders = new ArrayList<>();
        List<Integer> weights = new ArrayList<>();
        while (in.hasNext()) {
            String kind = in.next();
            int weight = in.nextInt();
            // 변수의 타입은 모두 Shipping이에요. 실제 객체는 입력에 따라 달라요.
            Shipping s = switch (kind) {
                case "express" -> new Express();
                case "pickup" -> new Pickup();
                default -> new Shipping();
            };
            orders.add(s);
            weights.add(weight);
        }
        for (int i = 0; i < orders.size(); i++) {
            Shipping s = orders.get(i);
            System.out.println(LINE);
        }
    }
}
"""
IMPORTS = "import java.util.ArrayList;\nimport java.util.List;\n\n"

S1_START = IMPORTS + """// 배송 방법의 기본 모양이에요. 기본 요금은 3000원이에요.
class Shipping {
    int fee(int weight) {
        return 3000;
    }
}

// 특급 배송은 무게 1kg마다 500원을 더해요.
class Express extends Shipping {
    @Override
    int fee(int weight) {
        return 3000 + weight * 500;
    }
}

// 매장 픽업이에요.
class Pickup extends Shipping {
    // 고칠 곳: 픽업은 배송비가 0원이어야 해요.
}
""" + SHIP_MAIN.replace('LINE', 's.getClass().getSimpleName() + " " + s.fee(weights.get(i)) + "원"')
FIX1 = ("""    // 고칠 곳: 픽업은 배송비가 0원이어야 해요.
""", """    // 같은 이름·같은 매개변수의 메서드를 다시 정의(재정의)하면, Shipping 타입 변수로 불러도 이 메서드가 실행돼요.
    @Override
    int fee(int weight) { return 0; }
""")
S1_SOLUTION = S1_START.replace(*FIX1)

S2_START = IMPORTS + """// 배송 방법의 기본 모양이에요. 기본 요금은 3000원이에요.
class Shipping {
    int fee(int weight) {
        return 3000;
    }
}

// 특급 배송은 무게 1kg마다 500원을 더해요. 동료가 무게를 long으로 받게 고쳤어요.
class Express extends Shipping {
    // 고칠 곳: @Override가 없어서 이 메서드가 재정의인지 아무도 확인하지 않아요.
    int fee(long weight) {
        return 3000 + (int) weight * 500;
    }
}

// 매장 픽업은 배송비가 없어요.
class Pickup extends Shipping {
    @Override
    int fee(int weight) { return 0; }
}
""" + SHIP_MAIN.replace('LINE', 's.getClass().getSimpleName() + " " + s.fee(weights.get(i)) + "원"')
FIX2A = ("""    // 고칠 곳: @Override가 없어서 이 메서드가 재정의인지 아무도 확인하지 않아요.
    int fee(long weight) {""", """    // @Override를 붙이면 재정의가 아닐 때 컴파일러가 막아요. 매개변수 타입까지 같아야 재정의예요.
    @Override
    int fee(long weight) {""")
FIX2B = ("""    int fee(long weight) {
        return 3000 + (int) weight * 500;""", """    int fee(int weight) {
        return 3000 + weight * 500;""")
S2_SOLUTION = S2_START.replace(*FIX2A).replace(*FIX2B)

S3_START = IMPORTS + """// 배송 방법의 기본 모양이에요. 이름과 요금을 가져요.
class Shipping {
    String name = "일반";

    int fee(int weight) {
        return 3000;
    }
}

class Express extends Shipping {
    // 고칠 곳: 이름을 바꾸려고 같은 이름의 필드를 하나 더 선언했어요.
    String name = "특급";

    @Override
    int fee(int weight) {
        return 3000 + weight * 500;
    }
}

class Pickup extends Shipping {
    Pickup() {
        name = "픽업";
    }

    @Override
    int fee(int weight) { return 0; }
}
""" + SHIP_MAIN.replace('LINE', 's.name + " " + s.fee(weights.get(i)) + "원"')
FIX3 = ("""    // 고칠 곳: 이름을 바꾸려고 같은 이름의 필드를 하나 더 선언했어요.
    String name = "특급";""", """    // 필드는 재정의되지 않아요. 새 필드를 선언하지 않고, 물려받은 name에 값을 넣어요.
    Express() { name = "특급"; }""")
S3_SOLUTION = S3_START.replace(*FIX3)

S4_START = """// 배송 방법을 만들면 등록 장부에 한 줄을 남겨요.
class Shipping {
    Shipping() {
        // 고칠 곳: 만드는 중에 재정의될 수 있는 메서드를 불러요.
        System.out.println("생성자에서 등록: " + describe());
    }

    String describe() {
        return "일반";
    }
}

class Express extends Shipping {
    private final String region;

    Express(String region) {
        super();
        this.region = region;
    }

    @Override
    String describe() {
        return "특급(" + region + ")";
    }
}

class Main {
    // 다 만든 객체를 등록해요.
    static void register(Shipping s) {
        System.out.println("등록: " + s.describe());
    }

    public static void main(String[] args) {
        java.util.Scanner in = new java.util.Scanner(System.in);
        while (in.hasNext()) {
            String kind = in.next();
            Shipping s = kind.equals("express") ? new Express(in.next()) : new Shipping();
            register(s);
        }
    }
}
"""
FIX4 = ("""        // 고칠 곳: 만드는 중에 재정의될 수 있는 메서드를 불러요.
        System.out.println("생성자에서 등록: " + describe());
""", """        // 이 생성자가 실행되는 동안 Express의 region은 아직 비어 있어요. 등록은 다 만든 뒤 register가 해요.
""")
S4_SOLUTION = S4_START.replace(*FIX4)

S5_START = """import java.util.Collection;
import java.util.HashSet;
import java.util.List;

// 집합에 넣으려고 시도한 횟수(addCount)를 세는 집합이에요. HashSet을 상속해요.
class CountingSet extends HashSet<String> {
    int addCount = 0;

    @Override
    public boolean add(String e) {
        addCount++;
        return super.add(e);
    }

    @Override
    public boolean addAll(Collection<? extends String> c) {
        // 고칠 곳: 한꺼번에 넣는 개수를 여기서도 더해요.
        addCount += c.size();
        return super.addAll(c);
    }
}

class Main {
    public static void main(String[] args) {
        java.util.Scanner in = new java.util.Scanner(System.in);
        CountingSet set = new CountingSet();
        // 첫 줄의 단어는 하나씩 넣어요.
        for (String word : in.nextLine().trim().split("\\\\s+")) set.add(word);
        // 둘째 줄의 단어는 addAll로 한꺼번에 넣어요.
        set.addAll(List.of(in.nextLine().trim().split("\\\\s+")));
        System.out.println("시도 " + set.addCount + "번, 저장 " + set.size() + "개");
    }
}
"""
FIX5 = ("""        // 고칠 곳: 한꺼번에 넣는 개수를 여기서도 더해요.
        addCount += c.size();
""", """        // HashSet의 addAll은 원소마다 add를 불러요. 그 add가 이미 세니까 여기서 또 더하지 않아요.
        // 이 고침은 HashSet이 안에서 add를 부른다는 구현에 기대고 있어요.
""")
S5_SOLUTION = S5_START.replace(*FIX5)

S6_START = """import java.util.Collection;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.TreeSet;

// 이제 집합을 상속하지 않아요. 안에 집합 하나를 두고 일을 맡겨요(컴포지션).
class CountingSet {
    private final Set<String> inner;
    private int addCount = 0;

    CountingSet(Set<String> inner) {
        this.inner = inner;
    }

    boolean add(String e) {
        addCount++;
        return inner.add(e);
    }

    boolean addAll(Collection<String> c) {
        // 고칠 곳: 앞 스텝처럼 안쪽 집합이 add를 불러 줄 거라고 기대해요.
        return inner.addAll(c);
    }

    int addCount() { return addCount; }

    int size() { return inner.size(); }
}

// 준비 코드: 앞 스텝의 상속 버전을 TreeSet으로 바꾼 것이에요. 비교용이니 그대로 두세요.
class InheritedTreeCounter extends TreeSet<String> {
    int addCount = 0;

    @Override
    public boolean add(String e) { addCount++; return super.add(e); }

    @Override
    public boolean addAll(Collection<? extends String> c) { return super.addAll(c); }
}

class Main {
    public static void main(String[] args) {
        java.util.Scanner in = new java.util.Scanner(System.in);
        String kind = in.next();
        String first = in.next();
        List<String> words = List.of(in.nextLine().trim().split("\\\\s+"));
        // 안쪽 집합의 종류는 입력으로 골라요. CountingSet의 코드는 같아요.
        CountingSet set = new CountingSet(kind.equals("tree") ? new TreeSet<>() : new HashSet<>());
        set.add(first);
        set.addAll(new TreeSet<>(words));
        System.out.println("컴포지션(" + kind + ") 시도 " + set.addCount() + "번, 저장 " + set.size() + "개");
        InheritedTreeCounter old = new InheritedTreeCounter();
        old.addAll(new TreeSet<>(words));
        System.out.println("상속 버전(TreeSet) 시도 " + old.addCount + "번");
    }
}
"""
FIX6 = ("""        // 고칠 곳: 앞 스텝처럼 안쪽 집합이 add를 불러 줄 거라고 기대해요.
        return inner.addAll(c);""", """        // 세는 일은 CountingSet이 직접 해요. 안쪽 집합이 add를 부르든 말든 결과가 같아요.
        addCount += c.size();
        return inner.addAll(c);""")
S6_SOLUTION = S6_START.replace(*FIX6)

S7_START = """// 영수증의 순서(제목 → 본문 → 인사)는 Receipt가 정해요. 하위 클래스는 제목과 본문만 채워요.
abstract class Receipt {
    // final이라 하위 클래스가 순서를 바꿀 수 없어요.
    final void print(int amount) {
        System.out.println("[" + title() + "]");
        System.out.println(body(amount));
        System.out.println("감사합니다");
    }

    abstract String title();

    abstract String body(int amount);
}

class CardReceipt extends Receipt {
    String title() { return "카드 영수증"; }

    String body(int amount) { return "카드 결제 " + amount + "원"; }
}

class CashReceipt extends Receipt {
    String title() { return "현금 영수증"; }
    // 고칠 곳: 본문을 채우지 않았어요.
}

class Main {
    public static void main(String[] args) {
        java.util.Scanner in = new java.util.Scanner(System.in);
        while (in.hasNext()) {
            String kind = in.next();
            Receipt receipt = kind.equals("cash") ? new CashReceipt() : new CardReceipt();
            receipt.print(in.nextInt());
        }
    }
}
"""
FIX7 = ("""    // 고칠 곳: 본문을 채우지 않았어요.
""", """    // Receipt가 비워 둔 자리(추상 메서드)를 채워요. 순서는 Receipt의 print가 그대로 지켜요.
    String body(int amount) { return "현금 결제 " + amount + "원"; }
""")
S7_SOLUTION = S7_START.replace(*FIX7)


def step(**fields):
    fields.setdefault('language', 'java')
    return fields


LESSON = java_lesson(
    key='java-inheritance-composition', folder='java_inheritance_composition', pilot='니', revision=1,
    title='상속과 컴포지션 · 호출할 메서드는 실제 객체가 정해요',
    category='java', category_title='자바', track='basic',
    category_evidence='JDK 25로 실행하는 자바 상속·컴포지션 수업이에요.',
    track_evidence='다형성과 상속·컴포지션의 기초 원리라 기본으로 분류해요. 필수 여부나 난이도를 바꾸지 않아요.',
    audience='클래스와 객체·생성자·private을 익힌 자바 학습자(앞 수업 java-class-objects)',
    prerequisites=['클래스·객체·생성자·private을 다뤄 봤어요.', 'List·Set과 for·while 반복을 읽을 수 있어요.'],
    objectives=['변수의 타입이 아니라 실제 객체가 호출할 메서드를 정한다는 것(동적 디스패치)과 그 예외(오버로드·필드·생성 중 호출)를 실행으로 설명해요.',
                '상위 클래스의 내부 구현에 기대는 상속이 깨지는 경우를 직접 보고, 컴포지션이나 확장용으로 설계된 상속으로 고쳐요.'],
    scope=['재정의와 동적 디스패치, @Override와 오버로드, 필드 가림, 생성자에서 부른 재정의 메서드, HashSet·TreeSet의 addAll 차이로 보는 깨지기 쉬운 상속, 컴포지션, 추상 클래스의 템플릿 메서드'],
    out_of_scope=['인터페이스의 default 메서드 충돌', '제네릭 상속 규칙', '리플렉션·프록시'],
    sources=[
        ('https://docs.oracle.com/javase/specs/jls/se25/html/jls-15.html#jls-15.12.4', '호출할 인스턴스 메서드는 실행 중에 대상 객체의 클래스에서 찾아요.', 'JLS 25의 정의를 JDK 25 실행 결과로 확인해요.'),
        ('https://docs.oracle.com/javase/specs/jls/se25/html/jls-8.html#jls-8.3', '하위 클래스가 같은 이름의 필드를 선언하면 상위 클래스의 필드를 가려요(재정의가 아니에요).', 'JLS 25의 정의를 JDK 25 실행 결과로 확인해요.'),
        ('https://docs.oracle.com/javase/specs/jls/se25/html/jls-12.html#jls-12.5', '상위 클래스 생성자는 하위 클래스의 필드 초기화보다 먼저 실행돼요.', 'JLS 25의 정의를 JDK 25 실행 결과로 확인해요.'),
        ('https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/AbstractCollection.html#addAll(java.util.Collection)', 'AbstractCollection의 addAll은 원소마다 add를 부르도록 구현돼 있다고 문서에 적혀 있어요.', '공식 API 문서예요. TreeSet은 빈 집합에 정렬된 집합을 넣을 때 다른 경로를 써서 add를 부르지 않는 것을 JDK 25 실행으로 확인했어요.'),
    ],
    description='배송 방법과 집합 예제로 동적 디스패치, 상속이 깨지는 경우, 컴포지션과 확장용 상속을 차례로 고쳐요.',
    brief=('재정의·동적 디스패치·상속과 컴포지션의 차이를 다뤄요.',
           '상위 클래스의 구현이 바뀌어도 세는 결과가 맞도록 컴포지션으로 고쳐요.',
           ['실제 객체의 메서드가 호출되는 것을 확인해요.', '오버로드·필드·생성 중 호출의 함정을 봐요.', '상속 대신 컴포지션으로 바꿔 비교해요.'],
           '실제 JDK 25로 실행해요. HashSet·TreeSet 같은 표준 라이브러리의 실제 동작을 관찰해요.',
           '상위 클래스의 코드가 바뀌면 내 하위 클래스는 왜 틀릴 수 있을까요?'),
    representative=dict(slug='composition', expected_action='세는 일을 CountingSet 안에서 직접 해, 안쪽 집합의 구현과 상관없이 같은 결과를 내요.',
                        acceptance='HashSet·TreeSet 두 안쪽 집합과 중복 단어 입력에서 시도 횟수와 저장 수가 맞아야 해요.',
                        reset='준비 코드와 입력으로 돌아가요.', narration='안쪽 집합이 add를 부르지 않아 0번이 나오는 것을 보고, 직접 세도록 고쳐 다시 실행해요.'),
    chapters=[
        dict(title='호출할 메서드는 실제 객체가 정해요', objectives=['Shipping 타입 변수로 불러도 실제 객체의 재정의 메서드가 실행되는 것과, 그렇지 않은 경우를 구별해요.'],
             units=[
                 dict(title='재정의와 그 함정', objectives=['재정의·오버로드·필드 가림을 실행 결과로 구별해요.'],
                      premise='배송 방법(Shipping)마다 요금 계산이 달라요. 주문 목록은 모두 Shipping 타입 변수로 다뤄요. 입력은 「종류 무게」의 반복이에요.',
                      steps=[
                          step(slug='override', title='픽업 배송비를 0원으로 재정의하세요',
                               objectives=['상위 타입 변수로 불러도 실제 객체 클래스의 재정의 메서드가 실행된다는 것을 확인해요.'],
                               start=START_NEW,
                               intro=['입력 `basic 2 express 2 pickup 5`의 세 주문 요금을 출력해요. 특급은 무게마다 요금이 붙고, 매장 픽업은 0원이어야 해요. 그런데 픽업이 3000원으로 나와요.'],
                               know='하위 클래스가 상위 클래스의 메서드와 이름·매개변수가 같은 메서드를 다시 정의하면 재정의(override)예요. `s.fee(...)`를 부를 때 어느 메서드가 실행될지는 변수 s의 타입이 아니라 실행 중의 실제 객체가 정해요.',
                               todo=[TODO_RUN_BEFORE + ' 각 줄의 클래스 이름과 요금을 읽으세요.', 'Pickup 클래스의 `고칠 곳` 자리에 0원을 돌려주는 `fee` 재정의를 쓰세요. `@Override`를 붙이세요.', TODO_RUN_AFTER, TODO_SUBMIT],
                               starter=S1_START, solution=S1_SOLUTION,
                               tests=[('basic 2 express 2 pickup 5', 'Shipping 3000원\nExpress 4000원\nPickup 0원'),
                                      ('pickup 1 express 3', 'Pickup 0원\nExpress 4500원'),
                                      ('express 0 basic 9 pickup 9', 'Express 3000원\nShipping 3000원\nPickup 0원')],
                               success='픽업 주문은 0원, 다른 주문은 원래 요금이에요.',
                               complexity=dict(prior='클래스·객체·메서드 호출을 다뤄 봤어요.', new='재정의와 동적 디스패치',
                                               changed='Pickup에 fee 재정의를 추가', evidence='각 주문 줄의 클래스 이름과 요금', lines=2),
                               narration=[
                                   ('say', '세 주문 중 픽업만 0원이어야 하는 문제예요.', 'text:매장 픽업은 0원이어야 해요.'),
                                   ('run',),
                                   ('say', 'Express는 4000원인데 Pickup은 3000원이에요.', 'output'),
                                   ('say', 'Express는 fee를 재정의했어요. 그래서 Shipping 타입 변수로 불러도 Express의 fee가 실행됐어요.', 'code:return 3000 + weight * 500;'),
                                   ('say', 'Pickup에는 fee가 없어서 물려받은 Shipping의 fee가 실행돼요.', 'code:class Pickup extends Shipping {'),
                                   ('patch', *FIX1, 'Pickup에서 fee를 재정의해 0원을 돌려줘요.'),
                                   ('run',),
                                   ('say', '이제 Pickup 0원이에요. 부르는 코드는 그대로 s.fee인데 실행된 메서드가 달라졌어요.', 'output'),
                                   ('say', '조심하세요. 매개변수 타입을 하나라도 다르게 쓰면 재정의가 아니라 새 메서드가 돼요. 다음 스텝에서 그 경우를 봐요.', 'text:이름·매개변수가 같은 메서드를 다시 정의하면 재정의(override)예요.'),
                                   ('submit',)],
                               review={'조심하세요. 매개변수 타입을 하나라도 다르게 쓰면 재정의가 아니라 새 메서드가 돼요. 다음 스텝에서 그 경우를 봐요.':
                                       '재정의를 처음 쓸 때 시그니처를 다르게 쓰는 것이 가장 흔한 실수예요. 기록된 오답(fee(long))으로 실제 실패를 확인해요.'},
                               accepts=[([('    @Override\n    int fee(int weight) { return 0; }', '    @Override\n    int fee(int weight) {\n        return 0;\n    }')], '중괄호를 여러 줄로 써도 같은 재정의예요.')],
                               rejects=[([('    @Override\n    int fee(int weight) { return 0; }', '    int fee(long weight) { return 0; }')], 'long을 받는 fee는 재정의가 아니라 새 메서드라 픽업이 3000원이에요.')]),
                          step(slug='override-annotation', title='@Override로 재정의가 아닌 메서드를 찾아 고치세요',
                               objectives=['오버로드는 컴파일할 때 변수 타입으로, 재정의는 실행할 때 객체로 고른다는 것을 구별하고 @Override로 실수를 막아요.'],
                               start=START_NEW,
                               intro=['동료가 Express의 fee를 무게를 long으로 받게 고쳤어요. 입력 `express 2 pickup 1`에서 특급이 4000원이어야 하는데 3000원으로 나와요.',
                                      '먼저 Express의 fee 위에 `@Override`를 붙이고 실행해 컴파일러의 판단을 보세요. 그다음 매개변수를 Shipping과 같은 `int`로 고치세요.'],
                               know='이름은 같고 매개변수 타입이 다른 메서드는 오버로드(overload)예요. 오버로드는 컴파일할 때 변수의 타입을 보고 골라요. Shipping 타입에는 `fee(int)`만 있으니 그 메서드가 불려요.',
                               todo=[TODO_RUN_BEFORE, 'Express의 `fee` 위에 `@Override`를 붙이세요.', '코드 실행 버튼을 눌러 컴파일 오류 메시지를 읽으세요.', '`fee`의 매개변수 타입을 `int`로 바꾸고 계산식의 `(int)` 변환을 지우세요.', TODO_RUN_AFTER, TODO_SUBMIT],
                               starter=S2_START, solution=S2_SOLUTION,
                               tests=[('express 2 pickup 1', 'Express 4000원\nPickup 0원'), ('express 5', 'Express 5500원'), ('basic 1 express 0', 'Shipping 3000원\nExpress 3000원')],
                               success='특급 요금이 무게에 따라 계산되고, Express의 fee에 @Override가 있어요.',
                               complexity=dict(prior='재정의로 실제 객체의 메서드가 불리는 것을 봤어요.', new='오버로드와 재정의의 구별',
                                               changed='@Override 추가와 매개변수 타입', evidence='컴파일 오류 메시지와 Express 요금', lines=2),
                               narration=[
                                   ('say', '특급이 무게와 상관없이 3000원으로 나오는 문제예요.', 'text:특급이 4000원이어야 하는데 3000원으로 나와요.'),
                                   ('run',),
                                   ('say', 'Express 3000원이에요. Express의 fee가 실행되지 않았어요.', 'output'),
                                   ('say', '이 메서드는 long을 받아요. Shipping의 fee(int)와 다른 메서드라 재정의가 아니에요.', 'code:int fee(long weight) {'),
                                   ('patch', *FIX2A, '@Override를 붙여 컴파일러에게 재정의인지 확인하게 해요.'),
                                   ('run', None, 'does not override'),
                                   ('say', 'method does not override 오류예요. 컴파일러가 재정의가 아니라고 알려 줬어요.', 'output'),
                                   ('patch', *FIX2B, '매개변수를 Shipping과 같은 int로 맞춰요.'),
                                   ('run',),
                                   ('say', 'Express 4000원이에요. 이제 재정의라 실제 객체의 fee가 불려요.', 'output'),
                                   ('say', '조심하세요. @Override 없이 시그니처만 바꾸면 컴파일은 잘 되고 결과만 조용히 틀려요.', 'text:먼저 Express의 fee 위에 @Override를 붙이고 실행해 컴파일러의 판단을 보세요.'),
                                   ('submit',)],
                               review={'조심하세요. @Override 없이 시그니처만 바꾸면 컴파일은 잘 되고 결과만 조용히 틀려요.':
                                       '이 스텝의 시작 코드가 정확히 그 상태(@Override 없는 fee(long))이고, 실행 결과가 오류 없이 3000원으로 틀렸어요.'},
                               rejects=[([('class Shipping {\n    int fee(int weight) {', 'class Shipping {\n    int fee(long weight) {'), ('    int fee(int weight) {\n        return 3000 + weight * 500;', '    int fee(long weight) {\n        return 3000 + (int) weight * 500;')], '상위 클래스의 fee를 long으로 바꾸면 Pickup의 fee(int) 재정의가 깨져요.')]),
                          step(slug='field-hiding', title='특급 배송의 이름이 특급으로 보이게 하세요',
                               objectives=['필드는 재정의되지 않고 변수의 타입으로 정해진다는 것을 확인하고, 같은 이름의 필드를 새로 선언하지 않아요.'],
                               start=START_NEW,
                               intro=['이제 Shipping에 이름(name)이 생겼어요. 입력 `express 2 pickup 1`에서 첫 줄은 `특급 4000원`이어야 하는데 `일반 4000원`으로 나와요. 요금은 맞는데 이름만 틀려요.'],
                               know='하위 클래스가 상위 클래스와 같은 이름의 필드를 선언하면 필드가 하나 더 생겨요. 이것을 필드 가림(hiding)이라고 해요. `s.name`은 변수 s의 타입(Shipping)의 필드를 읽어요. 메서드와 달리 필드는 실행 중의 객체로 고르지 않아요.',
                               todo=[TODO_RUN_BEFORE, 'Express의 `String name = "특급";` 줄을, 생성자에서 물려받은 `name`에 `"특급"`을 넣는 코드로 바꾸세요.', TODO_RUN_AFTER, TODO_SUBMIT],
                               starter=S3_START, solution=S3_SOLUTION,
                               tests=[('express 2 pickup 1', '특급 4000원\n픽업 0원'), ('basic 3 express 1', '일반 3000원\n특급 3500원'), ('express 0', '특급 3000원')],
                               success='특급 주문의 이름이 특급으로 나와요.',
                               complexity=dict(prior='재정의된 메서드가 실제 객체로 골라지는 것을 봤어요.', new='필드 가림',
                                               changed='같은 이름의 필드 선언을 생성자 대입으로', evidence='각 줄의 이름', lines=1),
                               narration=[
                                   ('say', '요금은 맞는데 특급의 이름만 일반으로 나오는 문제예요.', 'text:요금은 맞는데 이름만 틀려요.'),
                                   ('run',),
                                   ('say', '일반 4000원이에요. fee는 Express 것이 불렸는데 name은 아니에요.', 'output'),
                                   ('say', '이 줄은 Shipping의 name을 바꾸지 않아요. Express 안에 name이라는 필드를 하나 더 만들어요.', 'code:String name = "특급";'),
                                   ('say', 's의 타입이 Shipping이라 s.name은 Shipping의 필드를 읽어요.', 'code:s.name'),
                                   ('patch', *FIX3, '새 필드 대신 생성자에서 물려받은 name에 넣어요.'),
                                   ('run',),
                                   ('say', '특급 4000원이에요. 필드가 하나뿐이라 어느 타입으로 읽어도 같아요.', 'output'),
                                   ('say', '조심하세요. Pickup처럼 생성자에서 넣는 대신 필드를 다시 선언하기 쉬워요. 그러면 이름이 두 개가 돼요.', 'code:name = "픽업";'),
                                   ('submit',)],
                               review={'조심하세요. Pickup처럼 생성자에서 넣는 대신 필드를 다시 선언하기 쉬워요. 그러면 이름이 두 개가 돼요.':
                                       '시작 코드의 Express가 바로 필드를 다시 선언한 경우이고, 같은 코드의 Pickup이 올바른 방법을 보여 줘요. 실행에서 이름이 일반으로 나온 결과를 봤어요.',
                                       '특급 4000원이에요. 필드가 하나뿐이라 어느 타입으로 읽어도 같아요.':
                                       '「읽어도 같아요」는 앞 실행에서 타입(Shipping)에 따라 다른 필드를 읽었던 것과 대조돼요. 고친 뒤에는 필드가 하나라 실제로 같은 값이 나와요.'},
                               accepts=[([('    Express() { name = "특급"; }', '    Express() {\n        this.name = "특급";\n    }')], 'this.name으로 써도 물려받은 같은 필드예요.')],
                               rejects=[([('    Express() { name = "특급"; }', '    static String name = "특급";')], 'static 필드도 같은 이름의 새 필드라 Shipping의 name을 가려요.')]),
                      ]),
                 dict(title='만드는 중에는 아직 다 만들어지지 않았어요', objectives=['객체가 만들어지는 순서를 실행 결과로 따라가요.'],
                      premise='배송 방법을 만들면 등록 장부에 「등록: 설명」 한 줄을 남겨요. 입력은 종류와, 특급이면 지역이에요.',
                      steps=[
                          step(slug='constructor-dispatch', title='등록 장부에 지역이 비어 나오지 않게 하세요',
                               objectives=['상위 클래스 생성자가 하위 클래스 필드보다 먼저 실행되고, 그 안에서도 재정의 메서드가 불린다는 것을 확인해요.'],
                               start=START_NEW,
                               intro=['입력 `express 서울 basic`이면 장부는 `등록: 특급(서울)`과 `등록: 일반` 두 줄이어야 해요. 그런데 Shipping 생성자도 등록을 시도해서 `생성자에서 등록: 특급(null)` 같은 줄이 더 나와요.',
                                      'region은 final 필드인데도 null로 보여요. 생성자의 등록 줄을 지워 다 만든 뒤의 register만 남기세요.'],
                               know='`new Express("서울")`은 먼저 Shipping 생성자를 끝까지 실행하고, 그다음 Express 생성자의 나머지 줄을 실행해요. 생성자 안에서 부른 describe도 실제 객체인 Express의 것이 실행돼요.',
                               todo=[TODO_RUN_BEFORE + ' `생성자에서 등록` 줄의 지역을 읽으세요.', 'Shipping 생성자의 `System.out.println("생성자에서 등록: " + describe());` 줄을 지우세요.', TODO_RUN_AFTER, TODO_SUBMIT],
                               starter=S4_START, solution=S4_SOLUTION,
                               tests=[('express 서울 basic', '등록: 특급(서울)\n등록: 일반'), ('basic express 부산 express 제주', '등록: 일반\n등록: 특급(부산)\n등록: 특급(제주)')],
                               success='장부에는 다 만든 뒤의 등록 줄만 있고 지역이 정확해요.',
                               complexity=dict(prior='재정의된 메서드가 실제 객체로 골라지는 것을 봤어요.', new='객체 생성 순서',
                                               changed='생성자 안의 재정의 메서드 호출을 지움', evidence='생성자에서 등록 줄의 null', lines=1),
                               narration=[
                                   ('say', '특급 서울을 만들었는데 장부에 null이 섞여 나오는 문제예요.', 'text:생성자에서 등록: 특급(null) 같은 줄이 더 나와요.'),
                                   ('run',),
                                   ('say', '생성자에서 등록: 특급(null)이 먼저 나오고, 등록: 특급(서울)이 뒤에 나와요.', 'output'),
                                   ('say', '이 줄은 Shipping 생성자 안이에요. 이때 Express의 region에는 아직 값이 없어요.', 'code:System.out.println("생성자에서 등록: " + describe());'),
                                   ('say', 'region은 super 뒤의 이 줄에서야 채워져요.', 'code:this.region = region;'),
                                   ('patch', *FIX4, '생성자의 등록 줄을 지우고 다 만든 뒤의 register에 맡겨요.'),
                                   ('run',),
                                   ('say', '등록: 특급(서울)과 등록: 일반, 두 줄만 남았어요.', 'output'),
                                   ('say', '조심하세요. final 필드는 처음부터 값이 있다고 믿기 쉬워요. 생성자가 끝나기 전에는 기본값 null을 읽을 수 있어요.', 'text:region은 final 필드인데도 null로 보여요.'),
                                   ('submit',)],
                               review={'조심하세요. final 필드는 처음부터 값이 있다고 믿기 쉬워요. 생성자가 끝나기 전에는 기본값 null을 읽을 수 있어요.':
                                       '실행 결과에서 final인 region이 null로 출력된 것을 봤어요. 이 스텝의 핵심 오해예요.'},
                               rejects=[([('        // 이 생성자가 실행되는 동안 Express의 region은 아직 비어 있어요. 등록은 다 만든 뒤 register가 해요.\n', '        System.out.println("생성자에서 등록: " + describe());\n')], '생성자에서 등록하면 특급의 지역이 null로 남아요.')]),
                      ]),
             ]),
        dict(title='상속 대신 컴포지션', objectives=['상위 클래스의 내부 구현에 기대는 상속이 언제 깨지는지 보고, 컴포지션과 확장용 상속을 구별해요.'],
             units=[
                 dict(title='세는 집합', objectives=['상속한 메서드가 서로를 부르는 방식에 하위 클래스가 기대면 생기는 문제를 실행으로 확인하고 컴포지션으로 고쳐요.'],
                      premise='CountingSet은 집합에 넣으려고 시도한 횟수(addCount)를 세요. 첫 줄 단어는 하나씩, 둘째 줄 단어는 한꺼번에 넣어요.',
                      steps=[
                          step(slug='fragile-base', title='한꺼번에 넣은 단어를 두 번 세지 않게 하세요',
                               objectives=['HashSet의 addAll이 안에서 add를 부르기 때문에 두 번 세는 것을 확인해요.'],
                               start=START_NEW,
                               intro=['입력 첫 줄 `x y`는 하나씩, 둘째 줄 `a b c`는 addAll로 한꺼번에 넣어요. 시도는 5번이어야 하는데 8번으로 나와요.'],
                               know='상속하면 상위 클래스의 메서드가 서로를 부르는 방식도 함께 물려받아요. HashSet의 addAll은 원소마다 add를 불러요. 그 add는 재정의한 CountingSet의 add예요.',
                               todo=[TODO_RUN_BEFORE, 'CountingSet의 `addAll` 안에서 `addCount += c.size();` 줄을 지우세요.', TODO_RUN_AFTER, TODO_SUBMIT],
                               starter=S5_START, solution=S5_SOLUTION,
                               tests=[('x y\na b c', '시도 5번, 저장 5개'), ('a a\na b', '시도 4번, 저장 2개'), ('k\nk', '시도 2번, 저장 1개')],
                               success='하나씩 넣은 것과 한꺼번에 넣은 것을 한 번씩만 세요.',
                               complexity=dict(prior='재정의된 메서드가 실제 객체로 불리는 것을 봤어요.', new='상속한 메서드끼리의 호출(자기 호출)',
                                               changed='addAll에서 직접 세는 줄을 지움', evidence='시도 횟수', lines=1),
                               narration=[
                                   ('say', '다섯 단어를 넣었는데 시도가 8번으로 세지는 문제예요.', 'text:시도는 5번이어야 하는데 8번으로 나와요.'),
                                   ('run',),
                                   ('say', '시도 8번, 저장 5개예요. 한꺼번에 넣은 세 단어가 두 번 세졌어요.', 'output'),
                                   ('say', '여기서 3을 더하고, super.addAll이 안에서 add를 세 번 불러 또 3을 더해요.', 'code:addCount += c.size();'),
                                   ('patch', *FIX5, '여기서 더하는 줄을 지워요. add가 이미 세요.'),
                                   ('run',),
                                   ('say', '시도 5번, 저장 5개예요.', 'output'),
                                   ('say', '조심하세요. 이 고침은 HashSet이 안에서 add를 부른다는 사실에 기대요. 상위 클래스가 바뀌면 다시 틀릴 수 있어요.', 'code:return super.addAll(c);'),
                                   ('submit',)],
                               review={'조심하세요. 이 고침은 HashSet이 안에서 add를 부른다는 사실에 기대요. 상위 클래스가 바뀌면 다시 틀릴 수 있어요.':
                                       '다음 스텝에서 TreeSet으로 바꾸면 실제로 0번이 되는 것을 보여 줘요. 이 고침을 일반 원칙으로 오해하기 쉬워 경고해요.'},
                               rejects=[([('        return super.addAll(c);', '        addCount += c.size();\n        return super.addAll(c);')], '두 번 세요.')]),
                          step(slug='composition', title='안쪽 집합이 바뀌어도 맞게 세도록 고치세요',
                               objectives=['컴포지션은 안쪽 객체의 구현에 기대지 않고 자기 규칙을 직접 지킨다는 것을 확인해요.'],
                               start=START_NEW,
                               intro=['CountingSet을 상속 대신 컴포지션으로 바꿨어요. 안쪽 집합은 입력의 첫 단어로 고르고(`hash` 또는 `tree`), 둘째 단어는 add로 하나, 나머지는 addAll로 한꺼번에 넣어요.',
                                      '입력 `tree z a b c`에서 시도가 4번이어야 하는데 1번이에요. 비교용 상속 버전은 빈 TreeSet에 `a b c`를 한꺼번에 넣는데 0번이에요. TreeSet의 addAll은 빈 집합에 정렬된 집합을 넣을 때 add를 부르지 않거든요.'],
                               know='컴포지션(composition)은 객체를 상속하지 않고 필드로 가지고, 필요한 일을 그 객체에게 맡기는 구조예요. 맡긴 객체가 안에서 무엇을 하든 내 클래스의 규칙은 내 메서드가 지켜요.',
                               todo=[TODO_RUN_BEFORE + ' 컴포지션 줄과 상속 버전 줄의 시도 횟수를 읽으세요.', 'CountingSet의 `addAll`에서 `inner.addAll(c)` 앞에 넣으려는 개수를 직접 더하는 줄을 쓰세요.', TODO_RUN_AFTER, TODO_SUBMIT],
                               starter=S6_START, solution=S6_SOLUTION,
                               tests=[('tree z a b c', '컴포지션(tree) 시도 4번, 저장 4개\n상속 버전(TreeSet) 시도 0번'),
                                      ('hash z a b c', '컴포지션(hash) 시도 4번, 저장 4개\n상속 버전(TreeSet) 시도 0번'),
                                      ('tree a a b', '컴포지션(tree) 시도 3번, 저장 2개\n상속 버전(TreeSet) 시도 0번')],
                               success='안쪽 집합이 HashSet이든 TreeSet이든 시도 횟수가 맞아요.',
                               complexity=dict(prior='상속한 addAll이 add를 불러 두 번 세는 것을 봤어요.', new='컴포지션과 전달',
                                               changed='addAll에서 직접 세는 줄', evidence='hash·tree 두 경우의 시도 횟수와 상속 버전 비교', lines=1),
                               narration=[
                                   ('say', '네 단어를 넣으려 했는데 시도가 1번으로만 세지는 문제예요.', 'text:입력 tree z a b c에서 시도가 4번이어야 하는데 1번이에요.'),
                                   ('run',),
                                   ('say', '컴포지션은 시도 1번, 상속 버전은 0번이에요.', 'output'),
                                   ('say', '상속 버전은 앞 스텝의 고침 그대로예요. HashSet에서는 맞았는데 TreeSet에서는 틀려요.', 'code:class InheritedTreeCounter extends TreeSet<String> {'),
                                   ('say', '컴포지션 쪽도 안쪽 집합이 add를 불러 주길 기대해요. 그런데 inner.addAll은 CountingSet의 add를 부르지 않아요.', 'code:return inner.addAll(c);'),
                                   ('patch', *FIX6, '넣으려는 개수를 CountingSet이 직접 더해요.'),
                                   ('run',),
                                   ('say', '컴포지션(tree) 시도 4번이에요. 상속 버전은 여전히 0번이에요.', 'output'),
                                   ('say', '이제 안쪽이 HashSet이어도 같은 코드로 4번이에요. 내 규칙을 남의 구현에 맡기지 않았거든요.', 'text:맡긴 객체가 안에서 무엇을 하든 내 클래스의 규칙은 내 메서드가 지켜요.'),
                                   ('submit',)],
                               review={'이제 안쪽이 HashSet이어도 같은 코드로 4번이에요. 내 규칙을 남의 구현에 맡기지 않았거든요.':
                                       '「HashSet이어도」는 앞 스텝에서 HashSet이 add를 불러 줘야 맞던 것과 대조돼요. 두 번째 입력(hash z a b c)이 실제로 4번이에요.'},
                               rejects=[([('        addCount += c.size();\n        return inner.addAll(c);', '        boolean changed = inner.addAll(c);\n        if (changed) addCount += inner.size();\n        return changed;')], '저장된 수를 세면 시도 횟수와 달라요.')]),
                      ]),
                 dict(title='확장하라고 만든 상속', objectives=['상위 클래스가 순서를 고정하고 채울 자리만 열어 둔 상속(템플릿 메서드)이 왜 안전한지 확인해요.'],
                      premise='영수증은 제목 → 본문 → 인사 순서예요. Receipt가 순서를 정하고, 하위 클래스는 제목과 본문만 채워요. 입력은 「종류 금액」의 반복이에요.',
                      steps=[
                          step(slug='template-method', title='현금 영수증의 본문을 채우세요',
                               objectives=['abstract로 비워 둔 자리를 채우면 상위 클래스가 정한 순서는 그대로 지켜진다는 것을 확인해요.'],
                               start=START_NEW,
                               intro=['입력 `card 5000 cash 7000`의 두 영수증을 출력해요. 그런데 실행하면 컴파일 오류가 나요. CashReceipt가 본문(body)을 채우지 않았어요.',
                                      '본문은 `현금 결제 금액원` 모양이에요. 예를 들어 7000이면 `현금 결제 7000원`이에요.'],
                               know='`abstract` 메서드는 몸체가 없는 메서드예요. 추상 클래스를 상속한 클래스는 그 메서드를 모두 채워야 컴파일돼요. 순서를 정한 `print`는 `final`이라 하위 클래스가 바꿀 수 없어요.',
                               todo=[TODO_RUN_BEFORE + ' 컴파일 오류가 말하는 빠진 메서드 이름을 읽으세요.', 'CashReceipt의 `고칠 곳` 자리에 `body` 메서드를 쓰세요.', TODO_RUN_AFTER, TODO_SUBMIT],
                               starter=S7_START, solution=S7_SOLUTION,
                               tests=[('card 5000 cash 7000', '[카드 영수증]\n카드 결제 5000원\n감사합니다\n[현금 영수증]\n현금 결제 7000원\n감사합니다'),
                                      ('cash 100', '[현금 영수증]\n현금 결제 100원\n감사합니다')],
                               success='현금 영수증도 같은 순서로 금액에 맞는 본문을 출력해요.',
                               complexity=dict(prior='상속이 상위 클래스 구현에 기대면 깨지는 것을 봤어요.', new='추상 메서드와 템플릿 메서드',
                                               changed='CashReceipt에 body를 채움', evidence='컴파일 오류와 영수증 출력', lines=1),
                               narration=[
                                   ('say', '현금 영수증이 본문을 채우지 않아 실행되지 않는 문제예요.', 'text:CashReceipt가 본문(body)을 채우지 않았어요.'),
                                   ('run', None, 'does not override abstract method'),
                                   ('say', 'CashReceipt is not abstract and does not override abstract method body 오류예요.', 'output'),
                                   ('say', 'Receipt가 이 자리를 비워 두고, 채우라고 요구해요.', 'code:abstract String body(int amount);'),
                                   ('patch', *FIX7, 'CashReceipt에 body를 채워요.'),
                                   ('run',),
                                   ('say', '카드와 현금 영수증이 같은 순서로 나왔어요.', 'output'),
                                   ('say', '이 상속은 Receipt가 처음부터 확장하라고 만든 거예요. 순서는 final인 print가 지키고, 채울 자리만 열려 있어요.', 'code:final void print(int amount) {'),
                                   ('submit',)],
                               accepts=[([('    String body(int amount) { return "현금 결제 " + amount + "원"; }', '    @Override\n    String body(int amount) {\n        return "현금 결제 " + amount + "원";\n    }')], '@Override를 붙여 여러 줄로 써도 같아요.')],
                               rejects=[([('    String body(int amount) { return "현금 결제 " + amount + "원"; }', '    String body(int amount) { return "현금 결제 7000원"; }')], '금액을 고정하면 다른 금액의 영수증이 틀려요.')]),
                      ]),
             ]),
    ],
)
