"""O1 클래스와 객체: 상태·참조·생성자·복사·같음·캡슐화와 불변식 (JDK 25)."""
from common import START_NEW, START_PREV, TODO_RUN_BEFORE, TODO_RUN_AFTER, TODO_SUBMIT, java_lesson

# ---------------------------------------------------------------- unit 1: 변수와 객체
CART_COUNT = """// 장바구니 하나의 상태(담은 개수)를 가진 클래스예요.
class Cart {
    int count;

    void add(int n) {
        count += n;
    }
}
"""

S1_START = CART_COUNT + """
class Main {
    public static void main(String[] args) {
        java.util.Scanner in = new java.util.Scanner(System.in);
        int mineAdds = in.nextInt();
        int yoursAdds = in.nextInt();
        Cart mine = new Cart();
        // 고칠 곳: 친구의 장바구니를 준비하는 줄이에요.
        Cart yours = mine;
        mine.add(mineAdds);
        yours.add(yoursAdds);
        System.out.println("내 장바구니 " + mine.count + "개");
        System.out.println("친구 장바구니 " + yours.count + "개");
        System.out.println("같은 객체인가요? " + (mine == yours));
    }
}
"""
FIX1 = ("""        // 고칠 곳: 친구의 장바구니를 준비하는 줄이에요.
        Cart yours = mine;""", """        // new가 실행될 때마다 객체가 하나 생겨요. 이제 두 변수는 서로 다른 객체를 가리켜요.
        Cart yours = new Cart();""")
S1_SOLUTION = S1_START.replace(*FIX1)

S2_START = CART_COUNT + """
class Main {
    // 주문을 취소하면 장바구니를 비워요.
    static void cancel(Cart cart) {
        // 고칠 곳: 지금은 매개변수가 새 빈 장바구니를 가리키게만 해요.
        cart = new Cart();
    }

    public static void main(String[] args) {
        java.util.Scanner in = new java.util.Scanner(System.in);
        Cart mine = new Cart();
        mine.add(in.nextInt());
        System.out.println("취소 전 " + mine.count + "개");
        cancel(mine);
        System.out.println("취소 뒤 " + mine.count + "개");
    }
}
"""
FIX2 = ("""        // 고칠 곳: 지금은 매개변수가 새 빈 장바구니를 가리키게만 해요.
        cart = new Cart();""", """        // cart는 main의 mine과 같은 객체를 가리켜요. 그 객체의 필드를 바꾸면 호출한 쪽에서도 보여요.
        cart.count = 0;""")
S2_SOLUTION = S2_START.replace(*FIX2)

# ---------------------------------------------------------------- unit 2: 생성자
LIST_IMPORTS = """import java.util.ArrayList;
import java.util.List;

"""
S3_START = LIST_IMPORTS + """// 장바구니가 담은 상품 이름을 목록으로 기억해요.
class Cart {
    List<String> items;
    int limit;

    Cart(int limit) {
        this.limit = limit;
        // 고칠 곳: 상품 목록 객체를 아직 만들지 않았어요.
    }

    void add(String name) {
        items.add(name);
    }
}

class Main {
    public static void main(String[] args) {
        java.util.Scanner in = new java.util.Scanner(System.in);
        Cart cart = new Cart(3);
        while (in.hasNext()) cart.add(in.next());
        System.out.println("담은 상품 " + cart.items);
    }
}
"""
FIX3 = ("""        // 고칠 곳: 상품 목록 객체를 아직 만들지 않았어요.
""", """        // 빈 목록 객체를 만들어 필드에 넣어요. 그래야 add가 담을 곳이 있어요.
        items = new ArrayList<>();
""")
S3_SOLUTION = S3_START.replace(*FIX3)

S4_START = LIST_IMPORTS + """// 장바구니가 담은 상품 이름을 목록으로 기억해요.
class Cart {
    List<String> items;
    int limit;

    Cart(int limit) {
        // 고칠 곳: 한도가 1보다 작은 장바구니도 만들어져요.
        this.limit = limit;
        items = new ArrayList<>();
    }

    void add(String name) {
        if (items.size() >= limit) {
            System.out.println(name + " 거절: 한도 " + limit + "개");
            return;
        }
        items.add(name);
    }
}

class Main {
    public static void main(String[] args) {
        java.util.Scanner in = new java.util.Scanner(System.in);
        int limit = in.nextInt();
        try {
            Cart cart = new Cart(limit);
            while (in.hasNext()) cart.add(in.next());
            System.out.println("담은 상품 " + cart.items);
        } catch (IllegalArgumentException e) {
            System.out.println("만들지 않음: " + e.getMessage());
        }
    }
}
"""
FIX4 = ("""        // 고칠 곳: 한도가 1보다 작은 장바구니도 만들어져요.
""", """        // 규칙에 맞지 않는 값이면 객체를 만들지 않고 예외를 던져요. 잘못된 장바구니는 처음부터 생기지 않아요.
        if (limit < 1) throw new IllegalArgumentException("한도는 1 이상이어야 해요");
""")
S4_SOLUTION = S4_START.replace(*FIX4)

# ---------------------------------------------------------------- unit 3: 복사와 같음
S5_START = LIST_IMPORTS + """class Cart {
    List<String> items;

    Cart() {
        items = new ArrayList<>();
    }

    // 다른 장바구니의 상품으로 시작하는 복사 생성자예요.
    Cart(Cart other) {
        // 고칠 곳: 지금은 원래 장바구니의 목록 객체를 함께 가리켜요.
        items = other.items;
    }

    void addAll(String line) {
        for (String name : line.trim().split("\\\\s+")) {
            if (!name.isEmpty()) items.add(name);
        }
    }
}

class Main {
    public static void main(String[] args) {
        java.util.Scanner in = new java.util.Scanner(System.in);
        Cart mine = new Cart();
        mine.addAll(in.nextLine());
        Cart copy = new Cart(mine);
        copy.addAll(in.hasNextLine() ? in.nextLine() : "");
        System.out.println("내 장바구니 " + mine.items);
        System.out.println("복사본 " + copy.items);
    }
}
"""
FIX5 = ("""        // 고칠 곳: 지금은 원래 장바구니의 목록 객체를 함께 가리켜요.
        items = other.items;""", """        // 같은 상품으로 채운 새 목록 객체를 만들어요. 이제 두 장바구니가 목록을 나눠 쓰지 않아요.
        items = new ArrayList<>(other.items);""")
S5_SOLUTION = S5_START.replace(*FIX5)

S6_START = """import java.util.HashSet;
import java.util.Set;

// 쿠폰은 코드가 같으면 같은 쿠폰이에요.
class Coupon {
    final String code;

    Coupon(String code) {
        this.code = code;
    }

    @Override
    public boolean equals(Object other) {
        return other instanceof Coupon c && code.equals(c.code);
    }

    @Override
    public int hashCode() {
        // 고칠 곳: Object의 hashCode는 쿠폰 코드가 같다는 규칙을 반영하지 않아요.
        return super.hashCode();
    }
}

class Main {
    public static void main(String[] args) {
        java.util.Scanner in = new java.util.Scanner(System.in);
        Set<Coupon> used = new HashSet<>();
        while (in.hasNext()) {
            Coupon coupon = new Coupon(in.next());
            if (used.contains(coupon)) {
                System.out.println(coupon.code + " 이미 사용했어요");
            } else {
                used.add(coupon);
                System.out.println(coupon.code + " 사용");
            }
        }
        System.out.println("사용한 쿠폰 " + used.size() + "장");
    }
}
"""
FIX6 = ("""        // 고칠 곳: Object의 hashCode는 쿠폰 코드가 같다는 규칙을 반영하지 않아요.
        return super.hashCode();""", """        // equals가 같다고 하는 두 쿠폰은 hashCode도 같아야 해요. 같은 코드면 같은 값이 나와요.
        return code.hashCode();""")
S6_SOLUTION = S6_START.replace(*FIX6)

# ---------------------------------------------------------------- unit 4: 캡슐화와 불변식
S7_START = LIST_IMPORTS + """// 규칙: 담은 상품 수는 한도를 넘지 않아요.
class Cart {
    // 고칠 곳: 다른 클래스도 이 목록에 직접 넣을 수 있어요.
    List<String> items = new ArrayList<>();
    final int limit;

    Cart(int limit) {
        if (limit < 1) throw new IllegalArgumentException("한도는 1 이상이어야 해요");
        this.limit = limit;
    }

    boolean add(String name) {
        if (items.size() >= limit) return false;
        items.add(name);
        return true;
    }

    int size() {
        return items.size();
    }
}

// 묶음 상품을 담는 다른 팀의 코드예요.
class BundleTeam {
    static void put(Cart cart, String name) {
        cart.items.add(name);
    }
}

class Main {
    public static void main(String[] args) throws Exception {
        java.util.Scanner in = new java.util.Scanner(System.in);
        Cart cart = new Cart(in.nextInt());
        while (in.hasNext()) {
            String name = in.next();
            // +로 시작하는 이름은 묶음 상품이라 BundleTeam이 담아요.
            if (name.startsWith("+")) BundleTeam.put(cart, name.substring(1));
            else if (!cart.add(name)) System.out.println(name + " 거절");
        }
        // 준비 코드: 필드 items의 공개 범위를 실제 클래스 정보에서 읽어 보여 줘요.
        boolean hidden = java.lang.reflect.Modifier.isPrivate(Cart.class.getDeclaredField("items").getModifiers());
        System.out.println("items는 " + (hidden ? "private" : "다른 클래스에서도 보여요"));
        System.out.println("담은 수 " + cart.size() + " / 한도 " + cart.limit);
    }
}
"""
FIX7 = ("""    // 고칠 곳: 다른 클래스도 이 목록에 직접 넣을 수 있어요.
    List<String> items = new ArrayList<>();""", """    // private이면 Cart 밖에서 목록을 직접 바꿀 수 없어요. 규칙을 지키는 add만 통로로 남아요.
    private List<String> items = new ArrayList<>();""")
FIX7B = ("""        cart.items.add(name);""", """        // 목록에 직접 넣지 않고 Cart에게 부탁해요. 가득 찼으면 Cart가 거절해요.
        if (!cart.add(name)) System.out.println(name + " 거절");""")
S7_SOLUTION = S7_START.replace(*FIX7).replace(*FIX7B)

S8_START = LIST_IMPORTS + """// 규칙: 담은 상품 수는 한도를 넘지 않아요.
class Cart {
    private final List<String> items = new ArrayList<>();
    private final int limit;

    Cart(int limit) {
        if (limit < 1) throw new IllegalArgumentException("한도는 1 이상이어야 해요");
        this.limit = limit;
    }

    boolean add(String name) {
        if (items.size() >= limit) return false;
        items.add(name);
        return true;
    }

    int size() {
        return items.size();
    }

    // 화면에 보여 줄 상품 목록이에요.
    List<String> items() {
        // 고칠 곳: 안쪽 목록 객체를 그대로 내줘요.
        return items;
    }
}

class Main {
    public static void main(String[] args) {
        java.util.Scanner in = new java.util.Scanner(System.in);
        Cart cart = new Cart(in.nextInt());
        while (in.hasNext()) cart.add(in.next());
        // 화면 팀의 코드예요. 받은 목록에 표시용 줄을 덧붙여요.
        List<String> shown = cart.items();
        try {
            shown.add("(추천 상품)");
        } catch (UnsupportedOperationException e) {
            // 바꿀 수 없는 목록이면 덧붙이지 않아요.
        }
        System.out.println("담은 수 " + cart.size());
        System.out.println("장바구니 " + cart.items());
    }
}
"""
FIX8 = ("""        // 고칠 곳: 안쪽 목록 객체를 그대로 내줘요.
        return items;""", """        // 안쪽 목록 대신 바꿀 수 없는 사본을 내줘요. 받은 쪽이 고쳐도 장바구니는 그대로예요.
        return List.copyOf(items);""")
S8_SOLUTION = S8_START.replace(*FIX8)

S9_START = LIST_IMPORTS + """// 규칙: 담은 상품 수는 한도를 넘지 않고, 옮기는 중에 상품이 사라지거나 생기지 않아요.
class Cart {
    private final List<String> items = new ArrayList<>();
    private final int limit;

    Cart(int limit) {
        if (limit < 1) throw new IllegalArgumentException("한도는 1 이상이어야 해요");
        this.limit = limit;
    }

    boolean add(String name) {
        if (items.size() >= limit) return false;
        items.add(name);
        return true;
    }

    // 이 장바구니의 상품 하나를 다른 장바구니로 옮겨요. 옮겼으면 true예요.
    boolean moveTo(Cart other, String name) {
        // 고칠 곳: 실패할 수 있는 일을 확인하기 전에 먼저 빼요.
        items.remove(name);
        return other.add(name);
    }

    List<String> items() {
        return List.copyOf(items);
    }
}

class Main {
    public static void main(String[] args) {
        java.util.Scanner in = new java.util.Scanner(System.in);
        Cart a = new Cart(in.nextInt());
        Cart b = new Cart(in.nextInt());
        while (in.hasNext()) {
            String command = in.next();
            String name = command.substring(2);
            if (command.startsWith("a:")) a.add(name);
            if (command.startsWith("b:")) b.add(name);
            if (command.startsWith(">:") && !a.moveTo(b, name)) System.out.println(name + " 옮기기 거절");
        }
        System.out.println("A " + a.items() + " / B " + b.items());
    }
}
"""
FIX9 = ("""        // 고칠 곳: 실패할 수 있는 일을 확인하기 전에 먼저 빼요.
        items.remove(name);
        return other.add(name);""", """        // 이 장바구니에 없으면 옮길 것도 없어요. 상대가 가득 찼으면 add가 false라 여기서 멈춰요.
        if (!items.contains(name) || !other.add(name)) return false;
        // 상대가 받은 뒤에만 빼요. 그래서 실패해도 상품이 사라지지 않아요.
        return items.remove(name);""")
S9_SOLUTION = S9_START.replace(*FIX9)


def step(**fields):
    fields.setdefault('language', 'java')
    return fields


LESSON = java_lesson(
    key='java-class-objects', folder='java_class_objects', pilot='기', revision=1,
    title='클래스와 객체 · 상태를 가진 객체가 스스로 규칙을 지켜요',
    category='java', category_title='자바', track=None,
    category_evidence='JDK 25로 실행하는 자바 클래스·객체 수업이에요.',
    track_evidence='트랙 없음: 「기본」은 2026-10-25에 있던 수업에만 붙인 사용자 결정이고, 새 수업의 트랙(필수·고급)은 사용자 승인 없이 정하지 않아요.',
    audience='변수·조건·반복·메서드를 익히고 클래스를 처음 설계해 보는 자바 학습자',
    prerequisites=['변수·조건·반복문·메서드 호출을 읽고 고칠 수 있어요.', 'List와 Scanner로 입력을 읽는 짧은 코드를 실행해 봤어요.'],
    objectives=['같은 클래스로 만든 객체가 저마다 상태를 갖고, 변수는 그 객체를 가리키는 참조라는 것을 실행 결과로 설명해요.',
                '생성자·복사·equals와 hashCode·private으로 객체의 처음 상태와 규칙(불변식)을 지키는 코드를 직접 고쳐요.'],
    scope=['객체와 참조 변수, 메서드에 넘긴 참조, 생성자 초기화와 검사, 얕은·깊은 복사, equals와 hashCode, private과 내부 목록 유출, 두 객체 사이의 불변식'],
    out_of_scope=['상속과 다형성(다음 수업 java-inheritance-composition)', '스레드에서의 공유 상태', 'record·불변 객체의 모든 규칙'],
    sources=[
        ('https://docs.oracle.com/javase/specs/jls/se25/html/jls-4.html#jls-4.3.1', '참조 값은 객체를 가리키는 포인터이고, 같은 객체를 여러 참조가 가리킬 수 있어요.', 'JLS 25의 정의를 JDK 25 실행 결과로 확인해요.'),
        ('https://docs.oracle.com/javase/specs/jls/se25/html/jls-8.html#jls-8.4.1', '메서드 호출의 인수 값은 새로 만든 매개변수 변수에 복사돼요.', 'JLS 25의 정의를 JDK 25 실행 결과로 확인해요.'),
        ('https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Object.html#hashCode()', 'equals가 같다고 판단한 두 객체는 같은 hashCode를 돌려줘야 해요.', '공식 API 계약이에요. HashSet 동작을 JDK 25로 실행해 확인해요.'),
        ('https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/List.html#copyOf(java.util.Collection)', 'List.copyOf는 바꿀 수 없는 목록을 돌려줘요.', '공식 API예요. 바꾸려 하면 UnsupportedOperationException이 나는 것을 실행으로 확인해요.'),
    ],
    description='장바구니(Cart) 하나에서 시작해 객체의 상태·참조·생성자·복사·같음·캡슐화를 차례로 고쳐요.',
    brief=('객체와 참조, 생성자, 복사, equals·hashCode, 캡슐화와 불변식을 다뤄요.',
           '두 장바구니 사이에서 상품을 옮겨도 규칙이 깨지지 않게 해요.',
           ['변수 두 개와 객체 두 개를 구별해요.', '생성자로 처음 상태와 규칙을 정해요.', '복사·같음·private으로 상태를 지켜요.'],
           '실제 JDK 25로 실행해요. 입력은 미리 정해 둔 상품 이름과 수예요.',
           '객체의 규칙을 지키는 책임은 어느 코드에 있어야 할까요?'),
    representative=dict(slug='move-between-carts', expected_action='실패할 수 있는 확인을 먼저 하고, 성공한 뒤에만 원래 장바구니에서 빼요.',
                        acceptance='가득 찬 장바구니·없는 상품·정상 이동의 세 입력에서 상품이 사라지거나 생기지 않아야 해요.',
                        reset='준비 코드와 입력으로 돌아가요.', narration='가득 찬 장바구니로 옮길 때 상품이 사라지는 것을 보고, 순서를 바꿔 다시 실행해요.'),
    chapters=[
        dict(title='객체는 저마다 상태를 가져요', objectives=['new로 만든 객체와 그 객체를 가리키는 참조 변수를 구별해요.', '생성자가 객체의 처음 상태와 규칙을 정한다는 것을 확인해요.'],
             units=[
                 dict(title='변수와 객체를 나눠 세요', objectives=['참조를 대입하거나 메서드에 넘길 때 무엇이 복사되는지 실행 결과로 설명해요.'],
                      premise='Cart는 장바구니 하나가 담은 개수(count)를 가져요. 입력으로 받은 수만큼 장바구니에 담아요.',
                      steps=[
                          step(slug='two-carts', title='친구의 장바구니를 새 객체로 만드세요',
                               objectives=['변수 두 개가 객체 두 개를 뜻하지 않는다는 것을 확인하고, new로 독립된 객체를 만들어요.'],
                               start=START_NEW,
                               intro=['입력 `2 3`의 2는 내 장바구니에, 3은 친구 장바구니에 담아요. 그런데 실행하면 두 장바구니의 개수가 똑같이 나와요.'],
                               know='`new Cart()`가 실행될 때마다 객체가 하나 생겨요. 변수에는 그 객체를 가리키는 참조가 들어가요. `==`는 두 참조가 같은 객체를 가리키는지 비교해요.',
                               todo=[TODO_RUN_BEFORE + ' 두 개수와 `같은 객체인가요?` 줄을 읽으세요.',
                                     '`Cart yours = mine;` 줄을 친구의 새 장바구니를 만드는 코드로 고치세요.',
                                     TODO_RUN_AFTER, TODO_SUBMIT],
                               starter=S1_START, solution=S1_SOLUTION,
                               tests=[('2 3', '내 장바구니 2개\n친구 장바구니 3개\n같은 객체인가요? false'),
                                      ('4 1', '내 장바구니 4개\n친구 장바구니 1개\n같은 객체인가요? false'),
                                      ('0 5', '내 장바구니 0개\n친구 장바구니 5개\n같은 객체인가요? false')],
                               success='두 장바구니가 각자 받은 수만 세고, 서로 다른 객체예요.',
                               complexity=dict(prior='변수 대입과 메서드 호출을 해 봤어요.', new='참조 변수와 객체의 구별',
                                               changed='두 번째 변수가 가리킬 객체', evidence='두 개수와 == 비교 결과', lines=1),
                               narration=[
                                   ('say', '입력의 2와 3을 서로 다른 장바구니에 담으려는 코드예요.', 'text:입력 2 3의 2는 내 장바구니에, 3은 친구 장바구니에 담아요.'),
                                   ('run',),
                                   ('say', '둘 다 5개예요. 같은 객체인가요? 줄도 true예요.', 'output'),
                                   ('say', '이 줄은 객체를 만들지 않아요. mine이 가리키는 객체를 yours도 가리켜요.', 'code:Cart yours = mine;'),
                                   ('say', '그래서 2와 3이 한 객체의 count에 모두 더해졌어요.', 'code:yours.add(yoursAdds);'),
                                   ('patch', *FIX1, 'new로 두 번째 장바구니를 만들어요.'),
                                   ('run',),
                                   ('say', '내 것은 2개, 친구 것은 3개예요. 같은 객체인가요? 줄은 false예요.', 'output'),
                                   ('say', '조심하세요. 대입으로 객체를 복사했다고 생각하기 쉬워요. 대입은 참조만 하나 더 만들어요.', 'text:변수에는 그 객체를 가리키는 참조가 들어가요.'),
                                   ('submit',)],
                               review={'조심하세요. 대입으로 객체를 복사했다고 생각하기 쉬워요. 대입은 참조만 하나 더 만들어요.':
                                       '이 스텝의 시작 코드가 바로 그 오해(Cart yours = mine;)예요. 결과(두 장바구니가 같이 바뀜)는 앞 실행에서 봤어요.'},
                               rejects=[([('Cart yours = new Cart();', 'Cart yours = new Cart();\n        yours = mine;')], '새 객체를 만든 뒤 다시 mine을 가리키면 여전히 한 객체예요.')]),
                          step(slug='pass-reference', title='취소하면 호출한 쪽의 장바구니가 비게 하세요',
                               objectives=['메서드에는 참조의 복사본이 넘어간다는 것을 확인하고, 매개변수에 대입하는 것과 객체를 바꾸는 것을 구별해요.'],
                               start=START_NEW,
                               intro=['cancel은 주문을 취소하면 장바구니를 비워야 해요. 입력 `3`으로 3개를 담은 뒤 취소해요. 그런데 취소 뒤에도 3개가 남아요.'],
                               know='자바는 인수의 값을 매개변수에 복사해 넘겨요. 참조를 넘기면 참조가 복사돼요. 매개변수에 새 객체를 대입하면 매개변수만 바뀌어요. 매개변수가 가리키는 객체의 필드를 바꾸면 호출한 쪽도 같은 객체를 봐요.',
                               todo=[TODO_RUN_BEFORE, '`cancel` 안의 `cart = new Cart();` 줄을 넘겨받은 장바구니의 개수를 0으로 바꾸는 코드로 고치세요.', TODO_RUN_AFTER, TODO_SUBMIT],
                               starter=S2_START, solution=S2_SOLUTION,
                               tests=[('3', '취소 전 3개\n취소 뒤 0개'), ('7', '취소 전 7개\n취소 뒤 0개'), ('0', '취소 전 0개\n취소 뒤 0개')],
                               success='취소 뒤 main의 장바구니가 0개예요.',
                               complexity=dict(prior='참조 변수와 객체를 구별했어요.', new='메서드 매개변수로 복사되는 참조',
                                               changed='매개변수에 대입하는 대신 객체의 필드를 바꿈', evidence='취소 뒤 개수', lines=1),
                               narration=[
                                   ('say', '3개를 담고 취소했는데 3개가 남는 문제예요.', 'text:그런데 취소 뒤에도 3개가 남아요.'),
                                   ('run',),
                                   ('say', '취소 전도 뒤도 3개예요.', 'output'),
                                   ('say', '이 줄은 매개변수 cart가 새 객체를 가리키게 할 뿐이에요. main의 mine은 그대로 처음 객체를 가리켜요.', 'code:cart = new Cart();'),
                                   ('patch', *FIX2, '넘겨받은 참조로 그 객체의 count를 0으로 바꿔요.'),
                                   ('run',),
                                   ('say', '취소 뒤 0개예요. cart와 mine이 같은 객체를 가리키니까 main에서도 보여요.', 'output'),
                                   ('say', '매개변수에 대입한 것은 메서드 밖에 보이지 않았고, 객체를 바꾼 것은 보였어요.', 'text:매개변수에 새 객체를 대입하면 매개변수만 바뀌어요.'),
                                   ('submit',)],
                               accepts=[([('        cart.count = 0;', '        cart.add(-cart.count);')], 'add로 현재 개수만큼 빼도 같은 객체를 비워요.')],
                               rejects=[([('        cart.count = 0;', '        cart = null;')], '매개변수에 null을 대입해도 호출한 쪽의 객체는 그대로예요.')]),
                      ]),
                 dict(title='생성자가 처음 상태를 정해요', objectives=['객체가 쓰이기 전에 필요한 상태와 규칙을 생성자에서 보장해요.'],
                      premise='Cart가 담은 상품 이름을 목록(items)으로 기억하고, 최대 개수(limit)도 가져요.',
                      steps=[
                          step(slug='constructor-init', title='생성자에서 상품 목록을 만들어 두세요',
                               objectives=['필드의 기본값(null)과 생성자에서 만든 객체를 구별하고, 처음 상태를 생성자에서 준비해요.'],
                               start=START_NEW,
                               intro=['입력 `우유 빵`을 장바구니에 담으려는데 실행하면 NullPointerException이 나요. 오류 메시지에 null인 것이 무엇인지 적혀 있어요.'],
                               know='객체의 필드는 처음에 기본값이에요. 숫자는 0, 참조는 null이에요. null은 아무 객체도 가리키지 않는다는 뜻이라 메서드를 부를 수 없어요.',
                               todo=[TODO_RUN_BEFORE + ' 오류 메시지에서 null인 필드 이름을 찾으세요.', '생성자의 `고칠 곳` 주석 자리에 빈 `ArrayList` 목록을 만들어 `items`에 넣는 줄을 쓰세요.', TODO_RUN_AFTER, TODO_SUBMIT],
                               starter=S3_START, solution=S3_SOLUTION,
                               tests=[('우유 빵', '담은 상품 [우유, 빵]'), ('사과', '담은 상품 [사과]'), ('', '담은 상품 []')],
                               success='입력한 상품이 순서대로 목록에 담겨요. 입력이 없으면 빈 목록이에요.',
                               complexity=dict(prior='객체를 new로 만들어 필드를 읽어 봤어요.', new='필드의 기본값과 생성자 초기화',
                                               changed='생성자에서 목록 객체를 만듦', evidence='NullPointerException 메시지와 출력된 목록', lines=1),
                               narration=[
                                   ('say', '우유와 빵을 담으려는데 예외가 나는 문제예요.', 'text:실행하면 NullPointerException이 나요.'),
                                   ('run', None, 'NullPointerException'),
                                   ('say', '메시지에 this.items is null이라고 나와요. items가 아무 목록도 가리키지 않아요.', 'output'),
                                   ('say', '생성자는 limit만 정하고 목록은 만들지 않았어요.', 'code:this.limit = limit;'),
                                   ('patch', *FIX3, '생성자에서 빈 목록 객체를 만들어 items에 넣어요.'),
                                   ('run',),
                                   ('say', '이제 담은 상품 [우유, 빵]이 나와요.', 'output'),
                                   ('say', '조심하세요. List<String> items라고 선언만 해도 목록이 생긴 줄 알기 쉬워요. 선언은 참조를 담을 칸만 만들어요.', 'text:참조는 null이에요.'),
                                   ('submit',)],
                               review={'조심하세요. List<String> items라고 선언만 해도 목록이 생긴 줄 알기 쉬워요. 선언은 참조를 담을 칸만 만들어요.':
                                       '이 스텝의 시작 코드가 선언만 하고 객체를 만들지 않아 NullPointerException이 나는 바로 그 실수예요.'},
                               accepts=[([('    List<String> items;', '    List<String> items = new ArrayList<>();'), ('        items = new ArrayList<>();\n', '')], '필드 선언에서 바로 목록을 만들어도 객체가 만들어질 때 준비돼요.')],
                               rejects=[([('        items = new ArrayList<>();\n', '        items = List.of();\n')], 'List.of()는 바꿀 수 없는 목록이라 add에서 예외가 나요.')]),
                          step(slug='constructor-guard', title='한도가 1보다 작으면 장바구니를 만들지 마세요',
                               objectives=['생성자에서 규칙을 검사해 잘못된 상태의 객체가 처음부터 생기지 않게 해요.'],
                               start=START_PREV,
                               intro=['첫 입력은 한도(limit)이고, 나머지는 담을 상품이에요. 입력 `0 우유`처럼 한도가 0이면 아무것도 담을 수 없는 장바구니가 만들어져요.',
                                      '한도가 1보다 작으면 생성자에서 `IllegalArgumentException`을 던지세요. 메시지는 `한도는 1 이상이어야 해요`예요.'],
                               todo=[TODO_RUN_BEFORE, '생성자의 `고칠 곳` 주석 자리에 한도가 1보다 작으면 예외를 던지는 `if` 문 한 줄을 쓰세요.', TODO_RUN_AFTER, TODO_SUBMIT],
                               starter=S4_START, solution=S4_SOLUTION,
                               tests=[('0 우유', '만들지 않음: 한도는 1 이상이어야 해요'),
                                      ('2 우유 빵 사과', '사과 거절: 한도 2개\n담은 상품 [우유, 빵]'),
                                      ('-3', '만들지 않음: 한도는 1 이상이어야 해요'),
                                      ('1 우유', '담은 상품 [우유]')],
                               success='한도가 1 이상이면 담고, 1보다 작으면 객체가 만들어지지 않아요.',
                               complexity=dict(prior='생성자에서 필드를 준비해 봤어요.', new='생성자에서 규칙을 검사하는 것',
                                               changed='잘못된 한도로 생성할 때 예외', evidence='만들지 않음 줄과 경계값 1의 결과', lines=1),
                               narration=[
                                   ('say', '한도가 0이면 아무것도 담을 수 없는 장바구니가 생기는 문제예요.', 'text:한도가 0이면 아무것도 담을 수 없는 장바구니가 만들어져요.'),
                                   ('run',),
                                   ('say', '우유 거절: 한도 0개가 나오고 빈 장바구니가 남았어요.', 'output'),
                                   ('say', '이 객체는 규칙에 맞지 않는 상태로 이미 만들어졌어요.', 'code:this.limit = limit;'),
                                   ('patch', *FIX4, '한도가 1보다 작으면 생성자에서 예외를 던져요.'),
                                   ('run',),
                                   ('say', '만들지 않음: 한도는 1 이상이어야 해요가 나왔어요. 잘못된 장바구니는 생기지 않았어요.', 'output'),
                                   ('say', '조심하세요. limit < 0으로 쓰기 쉬운데, 그러면 한도 0인 장바구니가 그대로 만들어져요.', 'code:limit < 1'),
                                   ('submit',)],
                               review={'조심하세요. limit < 0으로 쓰기 쉬운데, 그러면 한도 0인 장바구니가 그대로 만들어져요.':
                                       '0이 경계값이에요. 입력 0 우유가 바로 이 실수를 드러내고, 기록된 오답(limit < 0)으로 실제 거절을 확인해요.'},
                               accepts=[([('limit < 1', 'limit <= 0')], 'limit <= 0도 같은 정수 범위를 거절해요.')],
                               rejects=[([('limit < 1', 'limit < 0')], '한도 0을 허용해요.'), ([('limit < 1', 'limit <= 1')], '한도 1인 정상 장바구니까지 거절해요.')]),
                      ]),
             ]),
        dict(title='복사와 같음을 구별해요', objectives=['객체를 복사할 때 안쪽 객체까지 나뉘는지, 두 객체를 같다고 볼 기준이 무엇인지 확인해요.'],
             units=[
                 dict(title='복사한 장바구니와 같은 쿠폰', objectives=['얕은 복사와 깊은 복사, equals와 hashCode의 짝을 실행 결과로 구별해요.'],
                      premise='내 장바구니를 복사해 친구에게 줘요. 쿠폰은 코드가 같으면 같은 쿠폰으로 봐요.',
                      steps=[
                          step(slug='deep-copy', title='복사본에 담아도 원래 장바구니는 그대로 두세요',
                               objectives=['복사 생성자가 안쪽 목록 객체까지 새로 만들어야 두 객체가 상태를 나눠 쓰지 않는다는 것을 확인해요.'],
                               start=START_NEW,
                               intro=['첫 줄 `우유 빵`은 내 장바구니에 담고, 복사본을 만든 뒤 둘째 줄 `사과`를 복사본에만 담아요. 그런데 내 장바구니에도 사과가 생겨요.'],
                               know='`new Cart(mine)`은 새 Cart 객체를 만들어요. 그 안의 `items`가 원래 목록 객체를 그대로 가리키면 목록은 하나뿐이에요. 이것을 얕은 복사라고 해요.',
                               todo=[TODO_RUN_BEFORE, '복사 생성자의 `items = other.items;` 줄을 같은 상품으로 채운 새 목록을 만드는 코드로 고치세요.', TODO_RUN_AFTER, TODO_SUBMIT],
                               starter=S5_START, solution=S5_SOLUTION,
                               tests=[('우유 빵\n사과', '내 장바구니 [우유, 빵]\n복사본 [우유, 빵, 사과]'),
                                      ('계란\n김 파', '내 장바구니 [계란]\n복사본 [계란, 김, 파]'),
                                      ('쌀\n', '내 장바구니 [쌀]\n복사본 [쌀]')],
                               success='복사본에 더 담아도 원래 장바구니의 목록은 바뀌지 않아요.',
                               complexity=dict(prior='참조를 대입하면 같은 객체를 가리킨다는 것을 봤어요.', new='얕은 복사와 깊은 복사',
                                               changed='복사 생성자에서 새 목록 객체를 만듦', evidence='원래 장바구니와 복사본의 목록', lines=1),
                               narration=[
                                   ('say', '복사본에만 사과를 담았는데 내 장바구니에도 생기는 문제예요.', 'text:그런데 내 장바구니에도 사과가 생겨요.'),
                                   ('run',),
                                   ('say', '두 줄 모두 우유, 빵, 사과예요.', 'output'),
                                   ('say', 'Cart 객체는 두 개지만, 이 줄 때문에 목록 객체는 하나를 같이 가리켜요.', 'code:items = other.items;'),
                                   ('patch', *FIX5, '원래 상품으로 채운 새 목록 객체를 만들어요.'),
                                   ('run',),
                                   ('say', '내 장바구니는 우유, 빵이고 복사본만 사과까지 있어요.', 'output'),
                                   ('say', '조심하세요. Cart를 new로 만들었으니 다 복사됐다고 생각하기 쉬워요. 안쪽의 목록까지 새로 만들어야 나뉘어요.', 'text:이것을 얕은 복사라고 해요.'),
                                   ('submit',)],
                               review={'조심하세요. Cart를 new로 만들었으니 다 복사됐다고 생각하기 쉬워요. 안쪽의 목록까지 새로 만들어야 나뉘어요.':
                                       '시작 코드가 new Cart(mine)으로 새 객체를 만들면서 목록은 공유하는 바로 그 상황이에요.'},
                               accepts=[([('items = new ArrayList<>(other.items);', 'items = new ArrayList<>();\n        items.addAll(other.items);')], '빈 목록을 만든 뒤 addAll로 채워도 목록이 나뉘어요.')],
                               rejects=[([('items = new ArrayList<>(other.items);', 'items = other.items.subList(0, other.items.size());')], 'subList는 원래 목록의 일부를 보여 주는 창이라 원래 목록이 함께 바뀌어요.')]),
                          step(slug='equals-hashcode', title='같은 코드의 쿠폰을 한 번만 쓰게 하세요',
                               objectives=['HashSet이 hashCode로 먼저 찾고 equals로 확인한다는 것을 보고, equals와 짝이 맞는 hashCode를 만들어요.'],
                               start=START_NEW,
                               intro=['입력 `SALE10 SALE10 WELCOME`의 쿠폰을 차례로 써요. 같은 코드의 쿠폰은 한 번만 쓸 수 있어야 해요. 그런데 SALE10이 두 번 사용돼요.',
                                      'Coupon의 equals는 코드가 같으면 같다고 판단해요. hashCode만 고치세요.'],
                               know='HashSet은 객체를 찾을 때 hashCode로 먼저 칸을 고르고, 그 칸 안에서 equals로 비교해요. 그래서 equals가 같다고 하는 두 객체는 hashCode도 같아야 해요.',
                               todo=[TODO_RUN_BEFORE, '`hashCode`가 쿠폰 코드(`code`)로 정해진 값을 돌려주도록 `return` 줄을 고치세요.', TODO_RUN_AFTER, TODO_SUBMIT],
                               starter=S6_START, solution=S6_SOLUTION,
                               tests=[('SALE10 SALE10 WELCOME', 'SALE10 사용\nSALE10 이미 사용했어요\nWELCOME 사용\n사용한 쿠폰 2장'),
                                      ('A B A B C', 'A 사용\nB 사용\nA 이미 사용했어요\nB 이미 사용했어요\nC 사용\n사용한 쿠폰 3장'),
                                      ('ONLY', 'ONLY 사용\n사용한 쿠폰 1장')],
                               success='같은 코드의 쿠폰은 두 번째부터 이미 사용했어요로 나와요.',
                               complexity=dict(prior='equals로 내용을 비교하는 것을 알아요.', new='hashCode와 해시 기반 컬렉션',
                                               changed='hashCode가 code로 정해짐', evidence='이미 사용했어요 줄과 사용한 쿠폰 수', lines=1),
                               narration=[
                                   ('say', '같은 코드의 쿠폰이 두 번 사용되는 문제예요.', 'text:그런데 SALE10이 두 번 사용돼요.'),
                                   ('run',),
                                   ('say', 'SALE10 사용이 두 번 나오고, 사용한 쿠폰이 3장이에요.', 'output'),
                                   ('say', 'equals는 코드가 같으면 true예요. 문제는 그 전에 칸을 고르는 hashCode예요.', 'code:return other instanceof Coupon c && code.equals(c.code);'),
                                   ('say', 'Object의 hashCode는 쿠폰 코드를 보지 않아요. 같은 코드인 두 쿠폰의 해시 값이 같다는 보장이 없어요.', 'code:return super.hashCode();'),
                                   ('patch', *FIX6, '쿠폰 코드의 hashCode를 그대로 돌려줘요.'),
                                   ('run',),
                                   ('say', '이제 두 번째 SALE10은 이미 사용했어요로 나오고, 쿠폰은 2장이에요.', 'output'),
                                   ('say', '조심하세요. equals만 고치고 hashCode를 두면 HashSet과 HashMap에서 같은 값을 못 찾아요.', 'text:그래서 equals가 같다고 하는 두 객체는 hashCode도 같아야 해요.'),
                                   ('submit',)],
                               review={'조심하세요. equals만 고치고 hashCode를 두면 HashSet과 HashMap에서 같은 값을 못 찾아요.':
                                       '시작 코드가 equals만 재정의한 상태이고, 실행에서 contains가 false인 결과를 봤어요.'},
                               accepts=[([('return code.hashCode();', 'return java.util.Objects.hash(code);')], 'Objects.hash(code)도 같은 코드에 같은 값을 줘요.')],
                               rejects=[([('return code.hashCode();', 'return System.identityHashCode(this);')], '객체의 식별 해시는 쿠폰 코드가 같으면 해시도 같아야 한다는 계약을 보장하지 않아요.'),
                                        ([('return code.hashCode();', 'return (int) (Math.random() * 1000);')], '부를 때마다 값이 달라 같은 쿠폰을 찾지 못해요.')]),
                      ]),
             ]),
        dict(title='캡슐화로 규칙을 지켜요', objectives=['객체의 규칙(불변식)을 지키는 코드가 그 객체 안에만 있도록 상태를 숨기고 통로를 좁혀요.'],
             units=[
                 dict(title='규칙을 지키는 통로는 Cart의 메서드뿐이에요', objectives=['private, 바꿀 수 없는 사본, 실패할 일을 먼저 확인하는 순서로 불변식을 지켜요.'],
                      premise='장바구니의 규칙: 담은 상품 수는 한도를 넘지 않아요. 이 규칙은 Cart의 메서드가 지켜요.',
                      steps=[
                          step(slug='private-field', title='묶음 상품도 한도를 넘지 않게 하세요',
                               objectives=['private으로 상태를 숨기면 규칙을 우회하는 코드를 컴파일러가 찾아 준다는 것을 확인해요.'],
                               start=START_NEW,
                               intro=['첫 입력은 한도이고, `+`로 시작하는 이름은 묶음 상품이에요. 묶음 상품은 BundleTeam 클래스가 담아요. 입력 `2 우유 +빵 +사과`에서 한도 2를 넘어 3개가 담겨요.',
                                      'Cart의 `items`를 `private`으로 바꾸세요. 그러면 BundleTeam의 줄이 컴파일되지 않아요. 그 줄을 `cart.add`를 쓰는 코드로 고치세요. 담지 못하면 `이름 거절`을 출력하세요.'],
                               know='`private` 필드는 그 클래스 안에서만 읽고 쓸 수 있어요. 규칙을 지키는 메서드만 상태를 바꾸게 하는 것을 캡슐화라고 해요.',
                               todo=[TODO_RUN_BEFORE, 'Cart의 `items` 선언 앞에 `private`을 붙이세요.', '코드 실행 버튼을 눌러 컴파일 오류가 가리키는 줄을 찾으세요.',
                                     '그 줄을 `cart.add(name)`의 결과가 false면 `이름 거절`을 출력하는 코드로 고치세요.', TODO_RUN_AFTER, TODO_SUBMIT],
                               starter=S7_START, solution=S7_SOLUTION,
                               tests=[('2 우유 +빵 +사과', '사과 거절\nitems는 private\n담은 수 2 / 한도 2'),
                                      ('1 +세트 우유', '우유 거절\nitems는 private\n담은 수 1 / 한도 1'),
                                      ('3 +a +b', 'items는 private\n담은 수 2 / 한도 3')],
                               success='묶음 상품도 한도를 넘지 못하고, items는 private이에요.',
                               complexity=dict(prior='메서드로 상태를 바꾸고 생성자에서 규칙을 검사해 봤어요.', new='private과 캡슐화',
                                               changed='items의 공개 범위와 BundleTeam의 담는 방법', evidence='컴파일 오류 위치, 담은 수, items의 공개 범위', lines=2),
                               narration=[
                                   ('say', '한도가 2인데 묶음 상품까지 3개가 담기는 문제예요.', 'text:입력 2 우유 +빵 +사과에서 한도 2를 넘어 3개가 담겨요.'),
                                   ('run',),
                                   ('say', '담은 수 3 / 한도 2예요. items도 다른 클래스에서 보인다고 나와요.', 'output'),
                                   ('say', 'BundleTeam은 add를 거치지 않고 목록에 바로 넣어요. 그래서 Cart의 검사가 실행되지 않아요.', 'code:cart.items.add(name);'),
                                   ('patch', *FIX7, 'items를 private으로 숨겨요.'),
                                   ('run', None, 'has private access'),
                                   ('say', 'items has private access 오류가 BundleTeam의 줄을 가리켜요. 규칙을 우회하던 곳이에요.', 'output'),
                                   ('patch', *FIX7B, '그 줄도 Cart의 add를 거치게 바꿔요.'),
                                   ('run',),
                                   ('say', '사과 거절이 나오고 담은 수 2 / 한도 2예요. items는 private이에요.', 'output'),
                                   ('say', '조심하세요. BundleTeam만 고치고 private을 빼면 지금은 통과해도, 다음 사람이 또 목록에 직접 넣을 수 있어요.', 'code:private List<String> items'),
                                   ('submit',)],
                               review={'조심하세요. BundleTeam만 고치고 private을 빼면 지금은 통과해도, 다음 사람이 또 목록에 직접 넣을 수 있어요.':
                                       'private 없이 BundleTeam만 고치는 것이 이 스텝에서 하기 쉬운 지름길이에요. 실제로는 items 공개 범위 줄이 달라 채점에서 실패해요. 경고는 그 지름길의 실제 결과(다른 코드가 다시 우회 가능)를 말해요.'},
                               rejects=[([('    private List<String> items = new ArrayList<>();', '    List<String> items = new ArrayList<>();')], 'BundleTeam만 고치면 items가 여전히 다른 클래스에 열려 있어요.')]),
                          step(slug='copy-on-read', title='보여 준 목록을 고쳐도 장바구니는 그대로 두세요',
                               objectives=['내부 목록 객체를 그대로 내주면 private이어도 밖에서 상태를 바꿀 수 있다는 것을 보고, 바꿀 수 없는 사본을 내줘요.'],
                               start=START_NEW,
                               intro=['이제 items는 private이에요. 그런데 `items()` 메서드가 안쪽 목록 객체를 그대로 내줘요. 화면 팀이 받은 목록에 `(추천 상품)`을 덧붙이자 장바구니의 담은 수가 늘어요.',
                                      '`items()`가 안쪽 목록 대신 사본을 돌려주게 고치세요.'],
                               know='`List.copyOf(목록)`은 같은 원소를 가진, 바꿀 수 없는 새 목록을 돌려줘요. 바꾸려 하면 `UnsupportedOperationException`이 나요.',
                               todo=[TODO_RUN_BEFORE, '`items()`의 `return items;` 줄을 사본을 돌려주는 코드로 고치세요.', TODO_RUN_AFTER, TODO_SUBMIT],
                               starter=S8_START, solution=S8_SOLUTION,
                               tests=[('2 우유 빵', '담은 수 2\n장바구니 [우유, 빵]'), ('3 사과', '담은 수 1\n장바구니 [사과]'), ('1', '담은 수 0\n장바구니 []')],
                               success='화면 팀이 받은 목록을 고쳐도 장바구니의 담은 수와 목록은 그대로예요.',
                               complexity=dict(prior='private으로 필드를 숨겨 봤어요.', new='참조를 내주는 메서드로 새는 상태',
                                               changed='items()가 돌려주는 목록', evidence='담은 수와 장바구니 목록', lines=1),
                               narration=[
                                   ('say', 'private인데도 밖에서 덧붙인 줄이 장바구니에 들어가는 문제예요.', 'text:화면 팀이 받은 목록에 (추천 상품)을 덧붙이자 장바구니의 담은 수가 늘어요.'),
                                   ('run',),
                                   ('say', '담은 수가 3이고 장바구니에 (추천 상품)이 있어요. 한도 2를 넘었어요.', 'output'),
                                   ('say', 'private은 필드 이름을 숨길 뿐이에요. 이 줄이 목록 객체의 참조를 밖으로 내줘요.', 'code:        return items;'),
                                   ('patch', *FIX8, '바꿀 수 없는 사본을 돌려줘요.'),
                                   ('run',),
                                   ('say', '담은 수 2, 장바구니는 우유와 빵이에요. 화면 팀의 덧붙이기는 사본에서 거절됐어요.', 'output'),
                                   ('say', '조심하세요. subList처럼 원래 목록을 보여 주는 창을 돌려주면 다시 안쪽이 바뀌어요.', 'text:items()가 안쪽 목록 대신 사본을 돌려주게 고치세요.'),
                                   ('submit',)],
                               review={'조심하세요. subList처럼 원래 목록을 보여 주는 창을 돌려주면 다시 안쪽이 바뀌어요.':
                                       '사본처럼 보이지만 원래 목록의 창인 subList가 이 수정에서 하기 쉬운 실수예요. 기록된 오답으로 실제 실패를 확인해요.'},
                               accepts=[([('        return List.copyOf(items);', '        return new ArrayList<>(items);')], '바꿀 수 있는 사본이어도 장바구니의 목록과는 다른 객체예요.'),
                                        ([('        return List.copyOf(items);', '        return java.util.Collections.unmodifiableList(items);')], '바꿀 수 없는 보기로 감싸도 밖에서 고칠 수 없어요.')],
                               rejects=[([('        return List.copyOf(items);', '        return items.subList(0, items.size());')], 'subList는 원래 목록의 창이라 덧붙이면 장바구니가 바뀌어요.')]),
                          step(slug='move-between-carts', title='옮기다 실패해도 상품이 사라지지 않게 하세요',
                               objectives=['두 객체에 걸친 규칙은 실패할 수 있는 일을 먼저 확인하고, 성공한 뒤에만 상태를 바꿔 지켜요.'],
                               start=START_NEW,
                               intro=['최종 도전이에요. 첫 두 수는 장바구니 A와 B의 한도예요. `a:이름`은 A에, `b:이름`은 B에 담고, `>:이름`은 A의 상품을 B로 옮겨요. 옮기지 못하면 A에 그대로 있어야 해요.',
                                      '입력 `2 1 a:우유 a:빵 b:사과 >:우유`에서 B는 이미 가득 찼어요. 그런데 실행하면 우유가 A에서도 B에서도 사라져요. 없는 상품을 옮기면 B에 새로 생기기도 해요.'],
                               todo=[TODO_RUN_BEFORE, '`moveTo`를 고치세요. A에 없는 상품이거나 B가 받지 못하면 아무것도 바꾸지 않고 false를 돌려줘요.', '이렇게 하려면 B에 담는 일을 먼저 하고, 성공했을 때만 A에서 빼세요.', TODO_RUN_AFTER, TODO_SUBMIT],
                               starter=S9_START, solution=S9_SOLUTION,
                               tests=[('2 1\na:우유 a:빵 b:사과 >:우유', '우유 옮기기 거절\nA [우유, 빵] / B [사과]'),
                                      ('2 2\na:우유 a:빵 >:우유', 'A [빵] / B [우유]'),
                                      ('1 1\na:우유 >:빵', '빵 옮기기 거절\nA [우유] / B []'),
                                      ('3 3\na:김 >:김 >:김', '김 옮기기 거절\nA [] / B [김]')],
                               success='가득 찬 장바구니·없는 상품·정상 이동 모두에서 상품 수가 보존돼요.',
                               complexity=dict(prior='메서드가 규칙을 지키고 상태를 private으로 숨겨 봤어요.', new='여러 객체에 걸친 불변식과 작업 순서',
                                               changed='moveTo에서 확인과 변경의 순서', evidence='거절 줄과 두 장바구니의 목록', lines=2),
                               narration=[
                                   ('say', 'B가 가득 찼을 때 옮기면 우유가 그대로 A에 있어야 해요.', 'text:옮기지 못하면 A에 그대로 있어야 해요.'),
                                   ('run',),
                                   ('say', '우유 옮기기 거절은 나오는데, A에는 빵만 남았어요. 우유가 사라졌어요.', 'output'),
                                   ('say', '먼저 A에서 빼고 나서 B가 받을 수 있는지 알게 돼요. 실패하면 되돌릴 방법이 없어요.', 'code:items.remove(name);'),
                                   ('patch', *FIX9, 'A에 있는지와 B가 받는지를 먼저 확인해요. 둘 다 됐을 때만 A에서 빼요.'),
                                   ('run',),
                                   ('say', '거절된 뒤에도 A는 우유와 빵, B는 사과 그대로예요.', 'output'),
                                   ('say', '조심하세요. contains 확인을 빼면 A에 없는 상품이 B에 새로 생겨요. 입력 a:우유 >:빵이 그 경우예요.', 'code:!items.contains(name)'),
                                   ('submit',)],
                               review={'조심하세요. contains 확인을 빼면 A에 없는 상품이 B에 새로 생겨요. 입력 a:우유 >:빵이 그 경우예요.':
                                       'B에 먼저 담는 순서만 바꾸고 A에 있는지 확인을 빠뜨리는 것이 이 수정에서 실제로 하기 쉬운 실수예요. 셋째 입력과 기록된 오답이 그 결과를 보여 줘요.'},
                               accepts=[([('        if (!items.contains(name) || !other.add(name)) return false;\n', '        if (!items.contains(name)) return false;\n        if (!other.add(name)) return false;\n')], '확인을 두 줄로 나눠도 같은 순서예요.')],
                               rejects=[([('if (!items.contains(name) || !other.add(name)) return false;', 'if (!other.add(name)) return false;')], 'A에 없는 상품도 B에 담겨요.'),
                                        ([('        if (!items.contains(name) || !other.add(name)) return false;', '        if (!items.remove(name)) return false;'), ('        return items.remove(name);', '        return other.add(name);')], 'A에서 먼저 빼면 B가 가득 찼을 때 상품이 사라져요.')]),
                      ]),
             ]),
    ],
)
