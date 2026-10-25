"""O3 객체지향 패턴: 바뀌는 요구에서 출발한 Strategy·Factory·Observer (JDK 25)."""
from common import START_NEW, START_PREV, TODO_RUN_BEFORE, TODO_RUN_AFTER, TODO_SUBMIT, java_lesson

# ---------------------------------------------------------------- Strategy
POLICY_TOP = """import java.util.Map;

// 할인 정책 하나가 하는 일: 금액을 받아 할인한 금액을 돌려줘요.
interface DiscountPolicy {
    int apply(int price);
}

class NoDiscount implements DiscountPolicy {
    public int apply(int price) { return price; }
}

class TenPercent implements DiscountPolicy {
    public int apply(int price) { return price - price / 10; }
}
"""
POLICY_REST = """
// 계산대는 어떤 정책인지 몰라요. 받은 정책 객체에게 계산을 맡겨요.
class Checkout {
    private final DiscountPolicy policy;

    Checkout(DiscountPolicy policy) {
        this.policy = policy;
    }

    int total(int price) {
        return policy.apply(price);
    }
}

// 준비 코드: 정책 객체 없이 if로 짠 예전 계산대예요. 비교용이니 그대로 두세요.
class LegacyCheckout {
    static String total(String name, int price) {
        if (name.equals("none")) return price + "원";
        if (name.equals("ten")) return (price - price / 10) + "원";
        return "모르는 정책";
    }
}

class Main {
    public static void main(String[] args) {
        // 정책 이름과 정책 객체를 이어 둔 표예요.
        Map<String, DiscountPolicy> policies = Map.of(
POLICIES
        );
        java.util.Scanner in = new java.util.Scanner(System.in);
        while (in.hasNext()) {
            String name = in.next();
            int price = in.nextInt();
            DiscountPolicy policy = policies.get(name);
            if (policy == null) {
                System.out.println(name + ": 정책 없음");
                continue;
            }
            System.out.println(name + " " + new Checkout(policy).total(price) + "원 (예전 계산대: " + LegacyCheckout.total(name, price) + ")");
        }
    }
}
"""
S1_START = POLICY_TOP + """
// 고칠 곳: vip 정책 클래스를 여기에 만들어요.
""" + POLICY_REST.replace('POLICIES', """            "none", new NoDiscount(),
            "ten", new TenPercent()
            // 고칠 곳: vip 정책을 이 표에 등록해요.""")
FIX1A = ("""// 고칠 곳: vip 정책 클래스를 여기에 만들어요.
""", """// 새 정책은 같은 약속(DiscountPolicy)을 지키는 새 클래스예요. Checkout은 고치지 않아요.
class Vip implements DiscountPolicy {
    public int apply(int price) { return price * 8 / 10; }
}
""")
FIX1B = ("""            "ten", new TenPercent()
            // 고칠 곳: vip 정책을 이 표에 등록해요.""", """            "ten", new TenPercent(),
            "vip", new Vip()""")
S1_SOLUTION = S1_START.replace(*FIX1A).replace(*FIX1B)

S2_START = POLICY_TOP + """
class Vip implements DiscountPolicy {
    public int apply(int price) { return price * 8 / 10; }
}
""" + POLICY_REST.replace('POLICIES', """            "none", new NoDiscount(),
            "ten", new TenPercent(),
            "vip", new Vip()
            // 고칠 곳: coupon 정책을 클래스 없이 등록해요.""")
FIX2 = ("""            "vip", new Vip()
            // 고칠 곳: coupon 정책을 클래스 없이 등록해요.""", """            "vip", new Vip(),
            // 메서드가 하나뿐인 인터페이스는 람다로 바로 만들 수 있어요. 0원 아래로는 내려가지 않아요.
            "coupon", price -> Math.max(0, price - 1000)""")
S2_SOLUTION = S2_START.replace(*FIX2)

# ---------------------------------------------------------------- Factory
NOTIFY_TOP = """// 알림 하나를 보내는 약속이에요. 보낸 내용을 글로 돌려줘요.
interface Notifier {
    String send(String message);
}

class EmailNotifier implements Notifier {
    private final String from;

    EmailNotifier(String from) {
        this.from = from;
    }

    public String send(String message) {
        return "메일(" + from + "): " + message;
    }
}

class SmsNotifier implements Notifier {
    private final String prefix;

    SmsNotifier(String prefix) {
        this.prefix = prefix;
    }

    public String send(String message) {
        return "문자 [" + prefix + "] " + message;
    }
}

class PushNotifier implements Notifier {
    private final String prefix;

    PushNotifier(String prefix) {
        this.prefix = prefix;
    }

    public String send(String message) {
        return "푸시 [" + prefix + "] " + message;
    }
}
"""
NOTIFY_FACTORY = """
// 알림 객체를 만드는 곳이에요. 설정을 아는 곳은 여기 하나예요.
class Notifiers {
    static String from = "shop@example.com";
    static String prefix = "가게";

    static Notifier create(String kind) {
        return switch (kind) {
            case "email" -> new EmailNotifier(from);
            case "sms" -> new SmsNotifier(prefix);
CASES            default -> throw new IllegalArgumentException("모르는 알림 종류: " + kind);
        };
    }
}
"""
NOTIFY_SERVICES = """
class OrderService {
    void complete(String kind) {
        Notifier notifier = Notifiers.create(kind);
        System.out.println(notifier.send("주문 완료"));
    }
}

class RefundService {
    void refund(String kind) {
REFUND
        System.out.println(notifier.send("환불 완료"));
    }
}

class Main {
    public static void main(String[] args) {
        java.util.Scanner in = new java.util.Scanner(System.in);
        // 첫 두 단어는 설정이에요: 보내는 메일 주소, 문자 머리말.
        Notifiers.from = in.next();
        Notifiers.prefix = in.next();
        while (in.hasNext()) {
            String event = in.next();
            String kind = in.next();
            try {
                if (event.equals("order")) new OrderService().complete(kind);
                else new RefundService().refund(kind);
            } catch (IllegalArgumentException e) {
                System.out.println(event + " 실패: " + e.getMessage());
            }
        }
    }
}
"""
S3_START = NOTIFY_TOP + NOTIFY_FACTORY.replace('CASES', '') + NOTIFY_SERVICES.replace('REFUND', """        // 고칠 곳: 여기만 알림 객체를 직접 new로 만들어요.
        Notifier notifier = kind.equals("email") ? new EmailNotifier("shop@example.com") : new SmsNotifier("가게");""")
FIX3 = ("""        // 고칠 곳: 여기만 알림 객체를 직접 new로 만들어요.
        Notifier notifier = kind.equals("email") ? new EmailNotifier("shop@example.com") : new SmsNotifier("가게");""",
        """        // 만드는 방법과 설정은 Notifiers만 알아요. 여기서는 종류만 말해요.
        Notifier notifier = Notifiers.create(kind);""")
S3_SOLUTION = S3_START.replace(*FIX3)

S4_START = NOTIFY_TOP + NOTIFY_FACTORY.replace('CASES', """            // 고칠 곳: push 알림을 만들 수 있게 해요.
""") + NOTIFY_SERVICES.replace('REFUND', """        Notifier notifier = Notifiers.create(kind);""")
FIX4 = ("""            // 고칠 곳: push 알림을 만들 수 있게 해요.
""", """            // 새 종류는 만드는 곳 한 군데에만 더해요. 주문·환불 코드는 그대로 push를 쓸 수 있어요.
            case "push" -> new PushNotifier(prefix);
""")
S4_SOLUTION = S4_START.replace(*FIX4)

# ---------------------------------------------------------------- Observer
OBS_TOP = """import java.util.ArrayList;
import java.util.List;

// 주문 완료를 듣는 쪽의 약속이에요.
interface OrderListener {
    void onCompleted(int amount);
}

// 주문은 누가 듣는지 몰라요. 구독한 목록에게 알리기만 해요.
class Order {
    private final List<OrderListener> listeners = new ArrayList<>();

    void subscribe(OrderListener listener) {
        listeners.add(listener);
    }

    void unsubscribe(OrderListener listener) {
        listeners.remove(listener);
    }

    void complete(int amount) {
        System.out.println("주문 완료 " + amount + "원");
NOTIFY
    }
}

class Stock implements OrderListener {
    public void onCompleted(int amount) {
        System.out.println("  재고: 1개 줄임");
    }
}

class Points implements OrderListener {
    public void onCompleted(int amount) {
        System.out.println("  포인트: " + amount / 100 + "점 적립");
    }
}
"""
COUPON = """
// 첫 주문에만 쿠폰을 주고, 알림을 받은 뒤 스스로 구독을 끊어요.
class FirstOrderCoupon implements OrderListener {
    private final Order order;

    FirstOrderCoupon(Order order) {
        this.order = order;
    }

    public void onCompleted(int amount) {
        System.out.println("  쿠폰: 첫 주문 쿠폰 발급");
        order.unsubscribe(this);
    }
}
"""
MAIL = """
// 메일 서버가 1000원 미만 주문의 메일을 거절해요.
class Mail implements OrderListener {
    public void onCompleted(int amount) {
        if (amount < 1000) throw new IllegalStateException("메일 서버가 거절했어요");
        System.out.println("  메일: 주문 확인 메일 보냄");
    }
}
"""
OBS_MAIN = """
class Main {
    public static void main(String[] args) {
        java.util.Scanner in = new java.util.Scanner(System.in);
        Order order = new Order();
SUBS
        while (in.hasNextInt()) order.complete(in.nextInt());
    }
}
"""
S5_START = OBS_TOP.replace('NOTIFY', """        // 고칠 곳: 구독한 누구에게도 알리지 않아요.""") + OBS_MAIN.replace('SUBS', """        order.subscribe(new Stock());
        order.subscribe(new Points());""")
FIX5 = ("""        // 고칠 곳: 구독한 누구에게도 알리지 않아요.""", """        // 구독한 순서대로 하나씩 알려요. 주문은 듣는 쪽이 재고인지 포인트인지 몰라도 돼요.
        for (OrderListener listener : listeners) listener.onCompleted(amount);""")
S5_SOLUTION = S5_START.replace(*FIX5)

S6_START = OBS_TOP.replace('NOTIFY', """        // 고칠 곳: 알리는 동안 듣는 쪽이 구독을 끊으면 목록이 바뀌어요.
        for (OrderListener listener : listeners) listener.onCompleted(amount);""") + COUPON + OBS_MAIN.replace('SUBS', """        order.subscribe(new FirstOrderCoupon(order));
        order.subscribe(new Stock());
        order.subscribe(new Points());""")
FIX6 = ("""        // 고칠 곳: 알리는 동안 듣는 쪽이 구독을 끊으면 목록이 바뀌어요.
        for (OrderListener listener : listeners) listener.onCompleted(amount);""", """        // 알리기 전에 목록의 사본을 만들어요. 알리는 중에 구독을 끊어도 이번 반복은 사본을 돌아요.
        for (OrderListener listener : List.copyOf(listeners)) listener.onCompleted(amount);""")
S6_SOLUTION = S6_START.replace(*FIX6)

S7_START = OBS_TOP.replace('NOTIFY', """        for (OrderListener listener : List.copyOf(listeners)) {
            // 고칠 곳: 한 곳이 실패하면 뒤의 구독자는 알림을 받지 못해요.
            listener.onCompleted(amount);
        }""") + MAIL + OBS_MAIN.replace('SUBS', """        order.subscribe(new Mail());
        order.subscribe(new Stock());
        order.subscribe(new Points());""")
FIX7 = ("""            // 고칠 곳: 한 곳이 실패하면 뒤의 구독자는 알림을 받지 못해요.
            listener.onCompleted(amount);""", """            // 구독자마다 따로 실패를 받아요. 한 곳이 실패해도 나머지에게는 계속 알려요.
            try {
                listener.onCompleted(amount);
            } catch (RuntimeException e) {
                System.out.println("  알림 실패: " + e.getMessage());
            }""")
S7_SOLUTION = S7_START.replace(*FIX7)


def step(**fields):
    fields.setdefault('language', 'java')
    return fields


LESSON = java_lesson(
    key='java-oop-patterns', folder='java_oop_patterns', pilot='디', revision=1,
    title='객체지향 패턴 · 바뀌는 부분을 객체로 떼어 내요',
    category='java', category_title='자바', track='advanced',
    category_evidence='JDK 25로 실행하는 자바 설계 패턴 수업이에요.',
    track_evidence='클래스·상속·컴포지션 뒤에 설계 판단을 넓히는 수업이라 고급으로 분류해요. 필수 여부를 바꾸지 않아요.',
    audience='클래스·인터페이스·상속과 컴포지션을 익힌 자바 학습자(앞 수업 java-inheritance-composition)',
    prerequisites=['인터페이스를 구현하고 재정의한 메서드가 실제 객체로 불리는 것을 알아요.', 'Map·List와 switch·try/catch를 읽을 수 있어요.'],
    objectives=['바뀌는 요구(새 할인 정책·새 알림 종류·새 구독자)를 넣을 때 고칠 곳이 한 군데로 모이도록 Strategy·Factory·Observer 구조를 직접 완성해요.',
                '알리는 중에 구독을 끊을 때와 구독자가 실패할 때 실제로 생기는 문제를 실행으로 보고 고쳐요. 패턴이 필요 없는 경우도 판단해요.'],
    scope=['Strategy(인터페이스 구현과 람다), 생성 책임을 한곳에 모으는 정적 팩토리 메서드, Observer의 구독·알림·구독 해제·실패 격리'],
    out_of_scope=['패턴 이름 암기와 23가지 GoF 목록', '스레드에서 안전한 Observer(CopyOnWriteArrayList 등)', '의존성 주입 프레임워크'],
    sources=[
        ('https://docs.oracle.com/javase/specs/jls/se25/html/jls-9.html#jls-9.8', '추상 메서드가 하나인 인터페이스는 함수형 인터페이스라 람다로 구현할 수 있어요.', 'JLS 25의 정의를 JDK 25 실행 결과로 확인해요.'),
        ('https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/ArrayList.html', 'ArrayList의 반복자는 반복 중 목록이 구조적으로 바뀌면 ConcurrentModificationException을 던져요(fail-fast).', '공식 API 문서예요. 구독 해제 중 실제 예외를 JDK 25로 확인해요.'),
        ('https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/List.html#copyOf(java.util.Collection)', 'List.copyOf는 반복 시점의 원소로 바꿀 수 없는 새 목록을 만들어요.', '공식 API예요. 사본을 돌면 구독 해제가 이번 반복에 영향을 주지 않는 것을 실행으로 확인해요.'),
    ],
    description='할인 정책·알림·주문 완료 예제로, 바뀌는 요구가 들어올 때 고칠 곳을 한 군데로 모으는 구조를 직접 완성해요.',
    brief=('Strategy·Factory·Observer를 바뀌는 요구에서 출발해 다뤄요.',
           '구독자 하나가 실패해도 다른 구독자에게 주문 완료를 알려요.',
           ['새 정책을 계산대 수정 없이 더해요.', '흩어진 new를 만드는 곳 하나로 모아요.', '구독·해제·실패 격리를 고쳐요.'],
           '실제 JDK 25로 실행해요. 패턴 이름보다 바뀌는 곳과 고칠 곳의 관계를 봐요.',
           '새 요구가 올 때마다 고쳐야 하는 파일이 여러 개라면 무엇이 잘못 나뉜 걸까요?'),
    representative=dict(slug='observer-isolation', expected_action='구독자마다 호출을 try/catch로 감싸 실패를 기록하고 다음 구독자에게 계속 알려요.',
                        acceptance='메일이 실패하는 주문과 성공하는 주문 모두에서 재고·포인트 알림이 나와야 해요.',
                        reset='준비 코드와 입력으로 돌아가요.', narration='메일 실패로 재고·포인트 알림이 사라지는 것을 보고, 구독자별로 실패를 받게 고쳐 다시 실행해요.'),
    chapters=[
        dict(title='바뀌는 정책을 객체로', objectives=['정책을 객체로 떼어 내면 새 정책을 더해도 쓰는 쪽 코드를 고치지 않는다는 것을 확인해요.'],
             units=[
                 dict(title='할인 정책 갈아 끼우기(Strategy)', objectives=['같은 약속을 지키는 새 정책 객체를 더해 계산대 수정 없이 동작을 바꿔요.', '정책이 하나뿐이고 바뀔 일이 없으면 if 한 줄이 더 단순하다는 판단도 해요.'],
                      premise='계산대(Checkout)는 받은 할인 정책 객체에게 계산을 맡겨요. 비교용 예전 계산대는 정책마다 if를 써요. 입력은 「정책이름 금액」의 반복이에요.',
                      steps=[
                          step(slug='strategy-new-policy', title='계산대를 고치지 않고 vip 정책을 더하세요',
                               objectives=['같은 인터페이스를 구현한 새 클래스를 표에 등록하면 쓰는 코드가 그대로 새 정책을 쓴다는 것을 확인해요.'],
                               start=START_NEW,
                               intro=['입력 `vip 10000 ten 10000 none 500`을 계산해요. vip는 20% 할인이에요. 할인한 금액은 `price * 8 / 10`이에요. 그런데 지금은 `vip: 정책 없음`이 나와요.',
                                      'Checkout과 LegacyCheckout은 고치지 마세요. vip 정책 클래스를 만들고 정책 표에 등록하세요.'],
                               know='인터페이스는 「무엇을 하는지」의 약속이에요. 계산대는 DiscountPolicy라는 약속만 알고 apply를 불러요. 어떤 클래스의 객체인지는 실행 중에 정해져요.',
                               todo=[TODO_RUN_BEFORE, '`고칠 곳: vip 정책 클래스` 자리에 DiscountPolicy를 구현한 `Vip` 클래스를 쓰세요.', '정책 표의 `고칠 곳` 자리에 `"vip"`와 `new Vip()`을 등록하세요. 앞 줄 끝에 쉼표가 필요해요.', TODO_RUN_AFTER, TODO_SUBMIT],
                               starter=S1_START, solution=S1_SOLUTION,
                               tests=[('vip 10000 ten 10000 none 500', 'vip 8000원 (예전 계산대: 모르는 정책)\nten 9000원 (예전 계산대: 9000원)\nnone 500원 (예전 계산대: 500원)'),
                                      ('vip 2500 gold 100', 'vip 2000원 (예전 계산대: 모르는 정책)\ngold: 정책 없음'),
                                      ('ten 990 vip 990', 'ten 891원 (예전 계산대: 891원)\nvip 792원 (예전 계산대: 모르는 정책)')],
                               success='vip 주문이 20% 할인되고, Checkout 코드는 그대로예요.',
                               complexity=dict(prior='인터페이스를 구현하고 재정의 메서드가 실제 객체로 불리는 것을 봤어요.', new='Strategy: 바뀌는 계산을 객체로 넘기기',
                                               changed='새 정책 클래스와 표의 한 줄', evidence='vip 줄의 금액과 예전 계산대 비교', lines=3),
                               narration=[
                                   ('say', 'vip 정책이 없어 정책 없음이 나오는 문제예요.', 'text:그런데 지금은 vip: 정책 없음이 나와요.'),
                                   ('run',),
                                   ('say', 'vip: 정책 없음이에요. ten과 none은 두 계산대 모두 같은 금액이에요.', 'output'),
                                   ('say', '계산대는 정책이 무엇인지 묻지 않고 apply만 불러요.', 'code:return policy.apply(price);'),
                                   ('patch', *FIX1A, 'DiscountPolicy를 구현한 Vip 클래스를 만들어요.'),
                                   ('patch', *FIX1B, '정책 표에 vip를 등록해요.'),
                                   ('run',),
                                   ('say', 'vip 8000원이에요. 예전 계산대는 모르는 정책이라고 나와요.', 'output'),
                                   ('say', '예전 계산대는 정책이 늘 때마다 if를 고쳐야 해요. 새 계산대는 한 줄도 고치지 않았어요.', 'code:if (name.equals("ten")) return (price - price / 10) + "원";'),
                                   ('say', '조심하세요. 표에 등록하는 줄의 앞 줄 끝 쉼표를 빼기 쉬워요. 빼면 Map.of 호출이 컴파일되지 않아요.', 'text:앞 줄 끝에 쉼표가 필요해요.'),
                                   ('submit',)],
                               review={'조심하세요. 표에 등록하는 줄의 앞 줄 끝 쉼표를 빼기 쉬워요. 빼면 Map.of 호출이 컴파일되지 않아요.':
                                       '준비 코드의 마지막 원소 "ten", new TenPercent() 뒤에는 쉼표가 없어서, 그 뒤에 한 줄을 더할 때 실제로 자주 빠뜨려요.'},
                               accepts=[([('    public int apply(int price) { return price * 8 / 10; }', '    public int apply(int price) { return price - price / 5; }')], '5로 나누어떨어지는 금액에서는 price - price / 5도 20% 할인이에요.')],
                               rejects=[([('    public int apply(int price) { return price * 8 / 10; }', '    public int apply(int price) { return price - 2000; }')], '고정 금액을 빼면 금액이 바뀔 때 20% 할인이 아니에요.')]),
                          step(slug='strategy-lambda', title='coupon 정책을 클래스 없이 람다로 더하세요',
                               objectives=['메서드가 하나인 인터페이스는 람다로 바로 구현할 수 있어, 전략이 꼭 새 클래스일 필요는 없다는 것을 확인해요.'],
                               start=START_PREV,
                               intro=['coupon 정책은 1000원을 빼요. 0원 아래로는 내려가지 않아요. 입력 `coupon 5000 coupon 300`은 4000원과 0원이 나와야 해요.',
                                      '이번에는 클래스를 만들지 말고 정책 표에 람다로 등록하세요.'],
                               know='`price -> Math.max(0, price - 1000)`은 apply 하나를 가진 DiscountPolicy 객체예요. 정책이 짧고 한 곳에서만 쓰이면 람다가 더 단순해요. 반대로 정책이 하나뿐이고 바뀔 계획이 없다면 인터페이스 없이 if 한 줄로 충분해요.',
                               todo=[TODO_RUN_BEFORE, '정책 표의 `고칠 곳` 자리에 `"coupon"`과 람다를 등록하세요. 앞 줄 끝에 쉼표를 붙이세요.', TODO_RUN_AFTER, TODO_SUBMIT],
                               starter=S2_START, solution=S2_SOLUTION,
                               tests=[('coupon 5000 coupon 300', 'coupon 4000원 (예전 계산대: 모르는 정책)\ncoupon 0원 (예전 계산대: 모르는 정책)'),
                                      ('coupon 1000 vip 1000', 'coupon 0원 (예전 계산대: 모르는 정책)\nvip 800원 (예전 계산대: 모르는 정책)')],
                               success='coupon은 1000원을 빼되 0원 아래로 내려가지 않아요.',
                               complexity=dict(prior='새 정책 클래스를 표에 등록해 봤어요.', new='함수형 인터페이스와 람다',
                                               changed='정책 표에 람다 한 줄', evidence='coupon 줄의 금액', lines=1),
                               narration=[
                                   ('say', '1000원을 빼되 0원 아래로 내려가지 않는 정책을 더해요.', 'text:0원 아래로는 내려가지 않아요.'),
                                   ('run',),
                                   ('say', '두 줄 모두 coupon: 정책 없음이에요.', 'output'),
                                   ('patch', *FIX2, '정책 표에 람다로 coupon을 등록해요.'),
                                   ('run',),
                                   ('say', 'coupon 4000원과 coupon 0원이에요. 300원에서 1000원을 빼도 0원에서 멈췄어요.', 'output'),
                                   ('say', '이 람다가 apply 메서드의 몸체예요. Vip처럼 클래스를 만들지 않았어요.', 'code:price -> Math.max(0, price - 1000)'),
                                   ('say', '조심하세요. Math.max 없이 price - 1000만 쓰면 300원 주문이 -700원이 돼요.', 'code:Math.max(0, price - 1000)'),
                                   ('submit',)],
                               review={'조심하세요. Math.max 없이 price - 1000만 쓰면 300원 주문이 -700원이 돼요.':
                                       '0원 하한을 빠뜨리는 것이 이 정책에서 실제로 하기 쉬운 실수예요. 입력 coupon 300과 기록된 오답이 결과(-700원)를 보여 줘요.',
                                       'coupon 4000원과 coupon 0원이에요. 300원에서 1000원을 빼도 0원에서 멈췄어요.':
                                       '「빼도 0원에서 멈췄어요」는 뺄셈이면 음수가 될 것이라는 예상과 실제 결과 0원의 대조예요.'},
                               rejects=[([('price -> Math.max(0, price - 1000)', 'price -> price - 1000')], '300원 주문이 -700원이 돼요.')]),
                      ]),
             ]),
        dict(title='만드는 책임을 한곳에', objectives=['객체를 만드는 방법과 설정을 한 곳에 모으면 설정 변경과 새 종류가 그 한 곳에서 끝난다는 것을 확인해요.'],
             units=[
                 dict(title='알림 객체 만들기(Factory)', objectives=['흩어진 new 때문에 설정이 어긋나는 것을 보고, 만드는 메서드 하나로 모아요.'],
                      premise='주문·환불 서비스가 알림(Notifier)을 보내요. 첫 두 단어는 설정(보내는 메일 주소, 문자 머리말)이고, 그 뒤는 「사건 종류」의 반복이에요.',
                      steps=[
                          step(slug='factory-scattered-new', title='환불 알림도 설정을 따르게 하세요',
                               objectives=['직접 new로 만든 곳은 설정을 모른다는 것을 보고, 만드는 책임을 Notifiers.create 하나에 모아요.'],
                               start=START_NEW,
                               intro=['입력 `help@shop.kr 몰입 order email refund email`은 보내는 주소를 help@shop.kr로 바꿔요. 주문 메일은 새 주소로 가는데 환불 메일은 예전 주소로 가요.',
                                      'RefundService만 알림 객체를 직접 new로 만들어요. 그 줄을 Notifiers.create를 쓰는 코드로 고치세요. 모르는 종류(fax)는 Notifiers가 거절해요.'],
                               know='객체를 만드는 코드가 여러 곳에 흩어지면, 만드는 방법이나 설정이 바뀔 때 모든 곳을 찾아 고쳐야 해요. 만드는 일을 한 메서드에 맡기면 그 메서드만 고치면 돼요. 이런 메서드를 팩토리 메서드라고 해요.',
                               todo=[TODO_RUN_BEFORE + ' 주문 메일과 환불 메일의 보내는 주소를 비교하세요.', 'RefundService의 `Notifier notifier = ...` 줄을 `Notifiers.create(kind)`를 쓰는 코드로 고치세요.', TODO_RUN_AFTER, TODO_SUBMIT],
                               starter=S3_START, solution=S3_SOLUTION,
                               tests=[('help@shop.kr 몰입 order email refund email', '메일(help@shop.kr): 주문 완료\n메일(help@shop.kr): 환불 완료'),
                                      ('a@b.kr 두번째 refund sms order sms', '문자 [두번째] 환불 완료\n문자 [두번째] 주문 완료'),
                                      ('x@y.kr 가게 refund fax', 'refund 실패: 모르는 알림 종류: fax')],
                               success='환불 알림도 설정의 주소·머리말을 쓰고, 모르는 종류는 거절돼요.',
                               complexity=dict(prior='인터페이스 타입으로 객체를 다뤄 봤어요.', new='생성 책임을 한 곳에 모으는 팩토리 메서드',
                                               changed='RefundService가 객체를 만드는 방법', evidence='환불 메일의 주소와 fax 거절', lines=1),
                               narration=[
                                   ('say', '주소 설정을 바꿨는데 환불 메일만 예전 주소로 가는 문제예요.', 'text:주문 메일은 새 주소로 가는데 환불 메일은 예전 주소로 가요.'),
                                   ('run',),
                                   ('say', '주문은 help@shop.kr, 환불은 shop@example.com이에요.', 'output'),
                                   ('say', '이 줄은 설정을 읽지 않고 예전 주소를 직접 적어 만들어요.', 'code:new EmailNotifier("shop@example.com")'),
                                   ('patch', *FIX3, '만드는 일을 Notifiers.create에 맡겨요.'),
                                   ('run',),
                                   ('say', '두 메일 모두 help@shop.kr이에요.', 'output'),
                                   ('say', '이제 주소가 바뀌면 Notifiers 한 곳만 알면 돼요. 모르는 종류를 거절하는 규칙도 이곳 하나에 있어요.', 'code:default -> throw new IllegalArgumentException("모르는 알림 종류: " + kind);'),
                                   ('submit',)],
                               rejects=[([('        Notifier notifier = Notifiers.create(kind);\n        System.out.println(notifier.send("환불 완료"));', '        Notifier notifier = kind.equals("email") ? new EmailNotifier(Notifiers.from) : new SmsNotifier(Notifiers.prefix);\n        System.out.println(notifier.send("환불 완료"));')], '설정은 읽지만 모르는 종류(fax)를 문자로 보내 버려요.')]),
                          step(slug='factory-new-kind', title='push 알림을 만드는 곳 한 군데에 더하세요',
                               objectives=['만드는 곳이 하나면 새 종류도 그곳에만 더해 모든 서비스가 쓸 수 있다는 것을 확인해요.'],
                               start=START_PREV,
                               intro=['이제 두 서비스 모두 Notifiers.create를 써요. 새로 push 알림이 생겼어요. PushNotifier 클래스는 준비돼 있어요. 입력 `a@b.kr 몰입 order push refund push`는 두 줄 모두 푸시여야 해요.',
                                      'OrderService와 RefundService는 고치지 마세요. Notifiers.create에만 push를 더하세요.'],
                               todo=[TODO_RUN_BEFORE, 'Notifiers.create의 `고칠 곳` 자리에 `push`일 때 `PushNotifier`를 만드는 `case` 줄을 쓰세요.', TODO_RUN_AFTER, TODO_SUBMIT],
                               starter=S4_START, solution=S4_SOLUTION,
                               tests=[('a@b.kr 몰입 order push refund push', '푸시 [몰입] 주문 완료\n푸시 [몰입] 환불 완료'),
                                      ('a@b.kr 가게 order email refund push order fax', '메일(a@b.kr): 주문 완료\n푸시 [가게] 환불 완료\norder 실패: 모르는 알림 종류: fax')],
                               success='주문과 환불 모두 push를 쓸 수 있고, 서비스 코드는 그대로예요.',
                               complexity=dict(prior='만드는 일을 Notifiers.create 하나로 모았어요.', new='',
                                               changed='팩토리에 새 종류 한 줄', evidence='두 서비스의 푸시 줄', lines=1),
                               narration=[
                                   ('say', '서비스는 그대로 두고 push 알림을 쓰게 하는 문제예요.', 'text:Notifiers.create에만 push를 더하세요.'),
                                   ('run',),
                                   ('say', '주문도 환불도 모르는 알림 종류: push로 실패해요.', 'output'),
                                   ('patch', *FIX4, 'create에 push 줄을 더해요.'),
                                   ('run',),
                                   ('say', '두 줄 모두 푸시 [몰입]이에요. 서비스 코드는 한 줄도 바뀌지 않았어요.', 'output'),
                                   ('say', '조심하세요. 서비스마다 if로 push를 처리하면 앞 스텝처럼 다시 흩어져요. 한 서비스만 고치고 다른 서비스를 놓치기 쉬워요.', 'code:Notifier notifier = Notifiers.create(kind);#2'),
                                   ('submit',)],
                               review={'조심하세요. 서비스마다 if로 push를 처리하면 앞 스텝처럼 다시 흩어져요. 한 서비스만 고치고 다른 서비스를 놓치기 쉬워요.':
                                       '앞 스텝에서 환불 서비스 하나가 설정을 놓친 사례를 실제로 봤어요. 새 종류를 서비스 쪽에 넣는 것이 흔한 실수예요.'},
                               rejects=[([('            case "push" -> new PushNotifier(prefix);\n', '            case "push" -> new PushNotifier("가게");\n')], '머리말 설정을 무시하고 직접 적으면 설정이 바뀔 때 틀려요.')]),
                      ]),
             ]),
        dict(title='변화를 듣는 쪽에 알리기', objectives=['알리는 쪽이 듣는 쪽을 몰라도 되게 나누고, 구독 해제와 실패가 섞일 때도 알림이 이어지게 해요.'],
             units=[
                 dict(title='주문 완료 알림(Observer)', objectives=['구독 목록에 알리는 반복을 완성하고, 반복 중 구독 해제와 구독자 실패를 실행으로 다뤄요.'],
                      premise='주문(Order)이 완료되면 구독한 쪽(재고·포인트·쿠폰·메일)에 알려요. 주문은 누가 듣는지 몰라요. 입력은 주문 금액의 목록이에요.',
                      steps=[
                          step(slug='observer-notify', title='구독한 모두에게 주문 완료를 알리세요',
                               objectives=['알리는 쪽은 듣는 쪽의 인터페이스만 알고 목록을 돌며 알린다는 것을 확인해요.'],
                               start=START_NEW,
                               intro=['재고(Stock)와 포인트(Points)가 주문을 구독했어요. 입력 `12000 500`의 두 주문 뒤에 각각 재고와 포인트 줄이 나와야 해요. 그런데 주문 완료 줄만 나와요.'],
                               know='주문은 OrderListener라는 약속만 알아요. 새 구독자(예: 메일)를 더할 때 Order를 고치지 않고 main에서 subscribe만 하면 돼요. 이런 구조를 Observer라고 불러요. 구독자가 하나뿐이고 늘 계획이 없으면 직접 호출해도 충분해요.',
                               todo=[TODO_RUN_BEFORE, 'Order.complete의 `고칠 곳` 자리에 구독 목록을 돌며 `onCompleted(amount)`를 부르는 반복문을 쓰세요.', TODO_RUN_AFTER, TODO_SUBMIT],
                               starter=S5_START, solution=S5_SOLUTION,
                               tests=[('12000 500', '주문 완료 12000원\n  재고: 1개 줄임\n  포인트: 120점 적립\n주문 완료 500원\n  재고: 1개 줄임\n  포인트: 5점 적립'),
                                      ('300', '주문 완료 300원\n  재고: 1개 줄임\n  포인트: 3점 적립')],
                               success='주문마다 구독한 순서대로 재고와 포인트 줄이 나와요.',
                               complexity=dict(prior='인터페이스 목록을 반복해 다뤄 봤어요.', new='Observer: 구독 목록에 알리기',
                                               changed='complete에서 구독자에게 알리는 반복', evidence='주문마다 이어지는 재고·포인트 줄', lines=1),
                               narration=[
                                   ('say', '구독은 했는데 아무도 알림을 받지 못하는 문제예요.', 'text:그런데 주문 완료 줄만 나와요.'),
                                   ('run',),
                                   ('say', '주문 완료 두 줄만 있어요.', 'output'),
                                   ('patch', *FIX5, '구독 목록을 돌며 하나씩 알려요.'),
                                   ('run',),
                                   ('say', '주문마다 재고와 포인트 줄이 이어져요. 500원 주문은 포인트 5점이에요.', 'output'),
                                   ('say', 'Order는 재고나 포인트 클래스를 이름으로 부르지 않아요. 약속인 onCompleted만 불러요.', 'code:listener.onCompleted(amount);'),
                                   ('submit',)],
                               rejects=[([('        for (OrderListener listener : listeners) listener.onCompleted(amount);', '        if (!listeners.isEmpty()) listeners.get(0).onCompleted(amount);')], '첫 구독자에게만 알리면 포인트가 빠져요.')]),
                          step(slug='observer-unsubscribe', title='알리는 중에 구독을 끊어도 알림이 이어지게 하세요',
                               objectives=['반복 중에 목록을 바꾸면 ArrayList가 ConcurrentModificationException을 던지는 것을 보고, 사본을 돌아 고쳐요.'],
                               start=START_PREV,
                               intro=['첫 주문 쿠폰(FirstOrderCoupon)이 맨 앞에 구독했어요. 쿠폰은 알림을 받으면 쿠폰을 주고 스스로 구독을 끊어요. 입력 `10000 2000`을 실행하면 첫 주문에서 예외가 나요.',
                                      '첫 주문은 쿠폰·재고·포인트, 둘째 주문은 재고·포인트만 나와야 해요.'],
                               know='for-each 반복은 목록의 반복자로 돌아요. ArrayList의 반복자는 반복 중에 목록이 바뀐 것을 알아채면 ConcurrentModificationException을 던져요. 알리기 전에 목록의 사본을 만들면 이번 반복은 사본을 돌아요.',
                               todo=[TODO_RUN_BEFORE + ' 예외 이름과 어느 주문에서 멈췄는지 확인하세요.', 'complete의 반복이 `listeners`의 사본을 돌도록 고치세요.', TODO_RUN_AFTER, TODO_SUBMIT],
                               starter=S6_START, solution=S6_SOLUTION,
                               tests=[('10000 2000', '주문 완료 10000원\n  쿠폰: 첫 주문 쿠폰 발급\n  재고: 1개 줄임\n  포인트: 100점 적립\n주문 완료 2000원\n  재고: 1개 줄임\n  포인트: 20점 적립'),
                                      ('500 500 500', '주문 완료 500원\n  쿠폰: 첫 주문 쿠폰 발급\n  재고: 1개 줄임\n  포인트: 5점 적립\n주문 완료 500원\n  재고: 1개 줄임\n  포인트: 5점 적립\n주문 완료 500원\n  재고: 1개 줄임\n  포인트: 5점 적립')],
                               success='첫 주문은 세 구독자 모두, 이후 주문은 쿠폰 없이 알림을 받아요.',
                               complexity=dict(prior='구독 목록을 돌며 알리는 반복을 썼어요.', new='반복 중 목록 변경과 fail-fast 반복자',
                                               changed='사본을 도는 반복', evidence='ConcurrentModificationException과 둘째 주문의 알림', lines=1),
                               narration=[
                                   ('say', '쿠폰이 알림을 받는 도중 구독을 끊어서 생기는 문제예요.', 'text:쿠폰은 알림을 받으면 쿠폰을 주고 스스로 구독을 끊어요.'),
                                   ('run', None, 'ConcurrentModificationException'),
                                   ('say', '쿠폰 줄 뒤에 ConcurrentModificationException이 나고 멈췄어요. 재고와 포인트는 알림을 못 받았어요.', 'output'),
                                   ('say', '쿠폰의 이 줄이 반복 중인 바로 그 목록에서 자기를 지워요.', 'code:order.unsubscribe(this);'),
                                   ('patch', *FIX6, '사본을 돌도록 바꿔요.'),
                                   ('run',),
                                   ('say', '첫 주문은 쿠폰·재고·포인트, 둘째 주문은 재고·포인트예요.', 'output'),
                                   ('say', '조심하세요. 인덱스 반복으로 바꾸면 예외는 안 나지만, 쿠폰이 빠진 자리 때문에 재고를 건너뛰어요.', 'code:List.copyOf(listeners)'),
                                   ('submit',)],
                               review={'조심하세요. 인덱스 반복으로 바꾸면 예외는 안 나지만, 쿠폰이 빠진 자리 때문에 재고를 건너뛰어요.':
                                       '예외를 피하려고 인덱스 반복으로 바꾸는 것이 흔한 대처예요. 기록된 오답으로 실제로 재고 줄이 빠지는 것을 확인해요.'},
                               accepts=[([('List.copyOf(listeners)', 'new ArrayList<>(listeners)')], '바꿀 수 있는 사본도 원래 목록과 다른 객체예요.')],
                               rejects=[([('        for (OrderListener listener : List.copyOf(listeners)) listener.onCompleted(amount);', '        for (int i = 0; i < listeners.size(); i++) listeners.get(i).onCompleted(amount);')], '쿠폰이 빠지며 자리가 당겨져 재고를 건너뛰어요.')]),
                          step(slug='observer-isolation', title='메일이 실패해도 재고와 포인트에는 알리세요',
                               objectives=['한 구독자의 예외가 나머지 알림을 막는 것을 보고, 구독자마다 실패를 받아 기록해요.'],
                               start=START_NEW,
                               intro=['최종 도전이에요. 메일(Mail)이 맨 앞에 구독했어요. 메일 서버는 1000원 미만 주문의 메일을 거절해요. 입력 `500 3000`의 첫 주문에서 예외가 나 재고와 포인트도 알림을 못 받아요.',
                                      '구독자 하나가 실패하면 `  알림 실패: 메시지`를 출력하고 다음 구독자에게 계속 알리세요. 줄 앞의 공백 두 칸도 출력해요.'],
                               todo=[TODO_RUN_BEFORE, 'complete의 `listener.onCompleted(amount);` 줄을 `try`로 감싸고, `RuntimeException`을 잡으면 `"  알림 실패: " + e.getMessage()`를 출력하세요.', TODO_RUN_AFTER, TODO_SUBMIT],
                               starter=S7_START, solution=S7_SOLUTION,
                               tests=[('500 3000', '주문 완료 500원\n  알림 실패: 메일 서버가 거절했어요\n  재고: 1개 줄임\n  포인트: 5점 적립\n주문 완료 3000원\n  메일: 주문 확인 메일 보냄\n  재고: 1개 줄임\n  포인트: 30점 적립'),
                                      ('999', '주문 완료 999원\n  알림 실패: 메일 서버가 거절했어요\n  재고: 1개 줄임\n  포인트: 9점 적립')],
                               success='메일이 실패한 주문에서도 재고·포인트 알림이 나오고, 실패가 한 줄로 기록돼요.',
                               complexity=dict(prior='구독 목록의 사본을 돌며 알렸어요.', new='구독자별 실패 격리',
                                               changed='알림 호출을 try/catch로 감쌈', evidence='알림 실패 줄 뒤의 재고·포인트 줄', lines=3),
                               narration=[
                                   ('say', '메일 하나가 실패하면 뒤의 재고와 포인트가 알림을 못 받는 문제예요.', 'text:입력 500 3000의 첫 주문에서 예외가 나 재고와 포인트도 알림을 못 받아요.'),
                                   ('run', None, 'IllegalStateException'),
                                   ('say', '주문 완료 500원 뒤에 IllegalStateException이 나고 프로그램이 멈췄어요.', 'output'),
                                   ('say', '예외가 이 줄에서 반복 밖으로 빠져나가서 다음 구독자로 가지 못해요.', 'code:            listener.onCompleted(amount);'),
                                   ('patch', *FIX7, '구독자마다 try로 감싸 실패를 받아 적어요.'),
                                   ('run',),
                                   ('say', '알림 실패 줄 뒤에 재고와 포인트가 이어져요. 3000원 주문은 메일까지 성공했어요.', 'output'),
                                   ('say', '조심하세요. try를 반복문 바깥에 두면 예외가 잡히긴 해도 반복이 이미 끝나서 재고와 포인트가 빠져요.', 'code:            try {'),
                                   ('submit',)],
                               review={'조심하세요. try를 반복문 바깥에 두면 예외가 잡히긴 해도 반복이 이미 끝나서 재고와 포인트가 빠져요.':
                                       'try 위치를 반복 밖에 두는 것이 이 수정에서 실제로 하기 쉬운 실수예요. 기록된 오답으로 재고·포인트 줄이 빠지는 결과를 확인해요.'},
                               accepts=[([('            } catch (RuntimeException e) {', '            } catch (IllegalStateException e) {')], '이 구독자들이 던지는 예외만 잡아도 이 입력에서는 같아요.')],
                               rejects=[([('        for (OrderListener listener : List.copyOf(listeners)) {\n            // 구독자마다', '        try {\n        for (OrderListener listener : List.copyOf(listeners)) {\n            // 구독자마다'),
                                          ('            try {\n                listener.onCompleted(amount);\n            } catch (RuntimeException e) {\n                System.out.println("  알림 실패: " + e.getMessage());\n            }\n        }', '                listener.onCompleted(amount);\n        }\n        } catch (RuntimeException e) {\n            System.out.println("  알림 실패: " + e.getMessage());\n        }')],
                                         'try를 반복문 바깥에 두면 실패 뒤의 구독자가 알림을 못 받아요.')]),
                      ]),
             ]),
    ],
)
