"""engineer-java-objects: 객체·생성자·this·static·오버로딩·상속·오버라이딩·접근 제어를 자바로 따라가요.

정보처리기사 실기는 필답형이라 문제마다 실행 전에 출력이나 호출 순서를 먼저 적게 해요.
한 파일에 class Main과 다른 클래스를 함께 두고(public class 없음), 준비 코드를 실행한 뒤
한 곳만 바꿔 다시 실행해 비교해요. 계약은 main 안 준비 값을 바꿔 다시 실행하므로,
그 값이 출력에 드러나게 했어요. 다른 클래스에는 같은 이름의 초기값 선언을 두지 않아요.
field-vs-method는 Bonus 생성자 안의 times도 바꿔서, 규칙을 main에 베낀 답을 걸러요.
"""
from certification_course.kit import java_task
from principles_course.common import lesson

SOURCES = ['https://www.q-net.or.kr/pageLink.do?link=cst/cstReport&jmCd=1320&mcrtrNo=991',
           'https://www.q-net.or.kr/pageLink.do?link=cst/cstReport&jmCd=1320&mcrtrNo=1453']

# 클래스 안 멤버는 4칸, 메서드 본문은 8칸 들여 써요.
B8 = ' ' * 8


def solution_mistakes(t, *mistakes):
    """Add mistakes made on top of the solution. Each mistake is a list of (before, after) edits."""
    for edits in mistakes:
        source = t['solution']
        for before, after in edits:
            assert source.count(before) == 1, (t['id'], 'mistake edit must match once', before)
            source = source.replace(before, after, 1)
        assert source not in (t['solution'], t['starter_code']), (t['id'], 'mistake equals starter or solution')
        t['_wrong'].append(source)
    return t


def build():
    tasks = []

    # 1. 클래스와 new: 객체마다 필드가 따로 있어요.
    tasks.append(java_task('new-object', '객체마다 필드가 따로 있어요',
        '자, 클래스(class)는 객체를 만드는 설계도예요. 안에 적은 변수를 필드(field)라고 해요.\n'
        '`new Cup()`은 객체(object)를 하나 만들어요. 필드는 객체마다 따로 생기고, int 필드는 처음에 0이에요.\n'
        '`a.water`처럼 점을 찍어 그 객체의 필드를 써요. 실행 전에 두 줄의 출력을 먼저 적어 보세요.',
        '준비 코드를 실행해 적은 답과 비교하세요.\n'
        'b 컵에는 a 컵보다 more만큼 더 담기게 고치세요.\n'
        '더하는 줄의 오른쪽에서 b.water 대신 a.water를 읽으면 돼요.',
        '''
        class Cup {
            // 컵마다 따로 갖는 물의 양이에요.
            int water;
        }

        class Main {
            public static void main(String[] args) {
                // a 컵에 담을 양과 b 컵에 더 담을 양이에요.
                int start = 200;
                int more = 50;
                // 클래스 이름 Cup이 변수의 자료형이에요.
                // Cup 설계도로 컵 객체를 두 개 만들어요.
                Cup a = new Cup();
                Cup b = new Cup();
                // a 컵의 필드에만 값을 담아요.
                a.water = start;
                // b 컵에는 a 컵보다 more만큼 더 담으려는 줄이에요.
                b.water = b.water + more;
                // 두 컵의 물의 양을 차례로 출력해요.
                System.out.println("a: " + a.water);
                System.out.println("b: " + b.water);
            }
        }
        ''',
        'b.water = b.water + more;', 'b.water = a.water + more;',
        caution='`water`만 쓰면 어느 객체의 필드인지 몰라 오류가 나요.',
        hints=['b.water = a.water + more;로 바꿔요.'],
        scenarios=[{'start': '500', 'more': '30'}, {'start': '120', 'more': '0'}],
        wrong=[('b.water = b.water + more;', 'b.water = water + more;'),
               ('b.water = b.water + more;', 'a.water = a.water + more;'),
               ('b.water = b.water + more;', 'b.water = 250;')]))

    # 2. 생성자와 this: price = price는 매개변수를 자기 자신에 담아요.
    tasks.append(java_task('constructor-this', 'price = price는 필드를 안 바꿔요',
        '생성자(constructor)는 new로 객체를 만들 때 한 번 실행돼요. 이름은 클래스와 같아요.\n'
        '메서드는 이름 앞에 돌려줄 값의 자료형을 써요. 생성자는 그걸 안 써요.\n'
        '매개변수와 필드의 이름이 같으면, 그냥 price는 매개변수예요. this는 이 객체 자신이라 필드는 this.price로 써요. '
        '실행 전에 출력을 먼저 적어 보세요.',
        '준비 코드를 실행해 적은 답과 비교하세요.\n'
        '생성자 안의 대입 줄을 고쳐 가격이 필드에 담기게 하세요.\n'
        '왼쪽 price 앞에 this.를 붙이면 돼요.',
        '''
        class Item {
            // 상품마다 따로 갖는 가격이에요.
            int price;

            // new Item(값)을 하면 이 생성자가 실행돼요.
            Item(int price) {
                // 받은 가격을 필드에 담으려는 줄이에요.
                price = price;
            }
        }

        class Main {
            public static void main(String[] args) {
                // 상품을 만들 때 넘길 가격이에요.
                int cost = 4500;
                // 괄호 안 값이 생성자의 price로 들어가요.
                Item pen = new Item(cost);
                // 객체의 price 필드를 출력해요.
                System.out.println("가격: " + pen.price);
            }
        }
        ''',
        'price = price;', 'this.price = price;',
        caution='`price = this.price;`처럼 거꾸로 쓰면 필드는 계속 0이에요.',
        hints=['this.price = price;로 바꿔요.'],
        scenarios=[{'cost': '1200'}, {'cost': '99000'}],
        wrong=[('price = price;', 'price = this.price;'),
               ('price = price;', 'this.price = 4500;')]))

    # 3. 인스턴스 메서드: static이 없어야 부른 객체의 필드를 써요.
    tasks.append(java_task('instance-method', 'static을 빼면 객체의 메서드예요',
        'static 없이 만든 메서드는 객체에 붙어요. `pen.total(3)`처럼 객체 뒤에 점을 찍어 불러요.\n'
        '그 안의 price는 부른 객체의 필드예요.\n'
        'static 메서드는 main처럼 객체 없이 불려요. 그래서 객체의 필드를 바로 못 써요.',
        '준비 코드를 실행해 오류 메시지를 읽어 보세요.\n'
        '`non-static variable`은 static이 아닌 변수, `static context`는 static 메서드 안이에요.\n'
        'total 메서드 앞의 static만 지우세요. 다시 실행하기 전에 두 줄의 출력을 먼저 적어 보세요.\n'
        '실행해서 적은 답과 두 상품의 금액을 비교해요.',
        '''
        class Item {
            // 상품마다 따로 갖는 가격이에요.
            int price;

            // 만들 때 받은 가격을 이 객체의 필드에 담아요.
            Item(int price) {
                this.price = price;
            }

            // 개수만큼 산 금액을 돌려줘요.
            static int total(int count) {
                // price는 이 메서드를 부른 객체의 가격이어야 해요.
                return price * count;
            }
        }

        class Main {
            public static void main(String[] args) {
                // 두 상품의 가격과 살 개수예요.
                int penPrice = 1200;
                int notePrice = 3000;
                int count = 3;
                // 가격이 다른 상품 객체를 두 개 만들어요.
                Item pen = new Item(penPrice);
                Item note = new Item(notePrice);
                // 같은 메서드를 객체마다 불러요.
                System.out.println("펜: " + pen.total(count));
                System.out.println("공책: " + note.total(count));
            }
        }
        ''',
        'static int total', 'int total',
        caution='price에 static을 붙여 오류를 없애면 모든 상품이 한 가격을 써요.',
        hints=['`static int total`에서 static만 지워요.'],
        scenarios=[{'count': '10'}, {'penPrice': '2500', 'notePrice': '700'},
                   {'penPrice': '800', 'notePrice': '900', 'count': '1'}],
        wrong=[('int price;', 'static int price;'),
               ('return price * count;', 'return this.price * count;')]))

    # 4. static 필드: 모든 객체가 변수 하나를 같이 써요.
    t = java_task('static-field', '모두가 같이 쓰는 static 필드',
        '필드 앞에 static을 붙이면 클래스에 딱 하나만 생겨요. 모든 객체가 그 변수 하나를 같이 써요.\n'
        'static이 없으면 객체마다 따로 생겨요. 그래서 새 객체의 필드는 늘 0에서 시작해요.\n'
        '실행 전에 회원 번호가 어떻게 찍힐지 먼저 적어 보세요.',
        '준비 코드를 실행해 적은 답과 비교하세요.\n'
        '회원 번호가 1부터 하나씩 커지게 하세요.\n'
        '회원 수를 세는 count 필드 앞에 static을 붙이면 돼요.\n'
        'no는 static이 아니라 객체마다 따로예요. 마지막 줄이 첫 줄과 같은 번호인지 보세요.',
        '''
        class Member {
            // 지금까지 만든 회원 수를 세는 필드예요.
            int count;
            // 이 회원이 받은 번호예요.
            int no;

            // 회원 객체를 만들 때마다 실행돼요.
            Member() {
                // 회원 수를 1 늘리고 그 값을 번호로 줘요.
                count++;
                no = count;
            }
        }

        class Main {
            public static void main(String[] args) {
                // 가입시킬 회원 수예요.
                int people = 3;
                // 첫 회원은 변수에 담아 끝까지 둬요.
                Member first = new Member();
                System.out.println("첫 회원 번호: " + first.no);
                // 나머지 회원을 하나씩 만들어요.
                for (int i = 2; i <= people; i++) {
                    Member m = new Member();
                    // 방금 만든 회원의 번호를 출력해요.
                    System.out.println("회원 번호: " + m.no);
                }
                // 다 만든 뒤 첫 회원의 번호를 다시 봐요.
                System.out.println("끝난 뒤 첫 회원: " + first.no);
            }
        }
        ''',
        'int count;', 'static int count;',
        caution='no에 static을 붙이면 모든 회원이 번호 하나를 같이 써요.',
        hints=['int count;를 static int count;로 바꿔요.'],
        scenarios=[{'people': '5'}, {'people': '2'}],
        wrong=[('int no;', 'static int no;')])
    # count는 고쳤지만 no에도 static을 붙여 첫 회원 번호까지 바뀐 실수예요.
    tasks.append(solution_mistakes(t, [('int no;', 'static int no;')]))

    # 5. 오버로딩: 넘긴 값의 자료형이 메서드를 골라요.
    tasks.append(java_task('overloading', '이름이 같은 메서드 중 무엇이 불릴까요?',
        '이름이 같아도 매개변수의 자료형이나 개수가 다르면 메서드를 여럿 둘 수 있어요.\n'
        '이걸 오버로딩(overloading)이라고 해요. 넘긴 값의 자료형을 보고 맞는 메서드를 불러요.\n'
        '실행 전에 어느 half가 불릴지, each가 어떻게 찍힐지 먼저 적어 보세요.',
        '준비 코드를 실행해 적은 답과 비교하세요.\n'
        'double을 받는 half가 불리게 고치세요.\n'
        'half에 넘기는 cake를 (double) cake로 바꾸면 돼요. 앞에서 배운 형 변환이에요.',
        '''
        class Main {
            // int를 받는 half예요. int끼리 나눠서 소수 부분을 버려요.
            static int half(int x) {
                System.out.println("half(int) 실행");
                return x / 2;
            }

            // 이름은 같고 double을 받는 half예요.
            static double half(double x) {
                System.out.println("half(double) 실행");
                return x / 2;
            }

            public static void main(String[] args) {
                // 둘이 나눌 케이크 조각 수예요.
                int cake = 7;
                // 넘긴 값의 자료형을 보고 half 하나를 골라요.
                double each = half(cake);
                // 한 사람이 받는 몫을 출력해요. each는 double이라 소수점까지 찍혀요.
                System.out.println("한 사람 몫: " + each);
            }
        }
        ''',
        'half(cake)', 'half((double) cake)',
        caution='결과에 (double)을 붙이면 이미 int 쪽이 불린 뒤예요.',
        hints=['double each = half((double) cake);처럼 써요.'],
        scenarios=[{'cake': '9'}, {'cake': '10'}, {'cake': '1'}],
        wrong=[('half(cake)', '(double) half(cake)'),
               ('half(cake)', 'half(cake) * 1.0')]))

    # 6. 상속과 생성자 순서: 부모 생성자가 먼저, super(값)이 고르는 부모 생성자.
    tasks.append(java_task('super-constructor', '부모 생성자가 먼저 실행돼요',
        '`class Smart extends Phone`이면 Smart가 Phone의 필드와 메서드를 물려받아요. Phone이 부모, Smart가 자식이에요.\n'
        '생성자도 오버로딩할 수 있어요. 자식 생성자 첫 줄에 `super(값)`을 쓰면 그 값에 맞는 부모 생성자가 먼저 실행돼요.\n'
        '`super(...)`가 없으면 값을 안 받는 부모 생성자가 자동으로 먼저 불려요. 실행 전에 출력 순서를 먼저 적어 보세요.',
        '준비 코드를 실행해 적은 순서와 비교하세요.\n'
        '가격을 받는 부모 생성자가 불리게 하세요.\n'
        'Smart 생성자 안 첫 줄에 `super(price);`를 넣으세요.',
        '''
        class Phone {
            // 값을 안 받는 부모 생성자예요.
            Phone() {
                System.out.println("Phone 생성자: 가격 없음");
            }

            // 가격을 받는 부모 생성자예요. 이름은 같고 매개변수가 달라요.
            Phone(int price) {
                System.out.println("Phone 생성자: " + price + "원");
            }
        }

        // Smart는 Phone을 물려받는 자식 클래스예요.
        class Smart extends Phone {
            // 자식 생성자예요. 부모 생성자가 끝난 뒤 이 안을 마저 실행해요.
            Smart(int price) {
                System.out.println("Smart 생성자");
            }
        }

        class Main {
            public static void main(String[] args) {
                // 새 휴대폰의 가격이에요.
                int cost = 900000;
                // 자식 객체 하나만 만들어요. 생성자가 몇 번 찍히는지 봐요.
                // 변수에 담지 않아도 new는 객체를 만들고 생성자를 실행해요.
                new Smart(cost);
            }
        }
        ''',
        'Smart(int price) {\n', 'Smart(int price) {\n' + B8 + '// 가격을 받는 부모 생성자를 불러요.\n' + B8 + 'super(price);\n',
        caution='`new Phone(price);`를 쓰면 부모 객체가 따로 하나 더 생겨요.',
        hints=['Smart(int price) { 바로 아래에 super(price);를 넣어요.'],
        scenarios=[{'cost': '450000'}, {'cost': '1200000'}],
        wrong=[('Smart(int price) {\n', 'Smart(int price) {\n' + B8 + 'new Phone(price);\n'),
               ('Smart(int price) {\n', 'Smart(int price) {\n' + B8 + 'Phone(price);\n')]))

    # 7. 오버라이딩과 다형성: 변수 자료형이 아니라 실제 객체의 메서드.
    tasks.append(java_task('overriding', '실제 객체의 메서드가 불려요',
        '자식은 부모와 이름·매개변수가 같은 메서드를 다시 만들 수 있어요. 이걸 오버라이딩(overriding)이라고 해요.\n'
        '`Ticket t`처럼 클래스 이름이 변수의 자료형이 돼요. 부모 자료형 변수에는 자식 객체도 담을 수 있어요. '
        '`Ticket t = new Kid();`처럼요.\n'
        '이때 `t.fee(base)`는 실제 객체 Kid의 메서드를 불러요. 실행 전에 두 요금을 먼저 적어 보세요.',
        '준비 코드를 실행해 적은 답과 비교하세요.\n'
        'kid 변수에 Kid 객체를 담으세요.\n'
        '변수 자료형 Ticket은 그대로 두고 new 뒤만 바꿔요.',
        '''
        class Ticket {
            // 기본 요금을 그대로 돌려줘요.
            int fee(int base) {
                return base;
            }
        }

        // Kid는 Ticket을 물려받는 자식이에요.
        class Kid extends Ticket {
            // 부모와 이름·매개변수가 같은 메서드를 다시 만들어요.
            int fee(int base) {
                // 어린이는 반값이에요.
                return base / 2;
            }
        }

        class Main {
            public static void main(String[] args) {
                // 기본 요금이에요.
                int base = 12000;
                // 두 변수 모두 자료형은 Ticket이에요.
                Ticket adult = new Ticket();
                Ticket kid = new Ticket();
                // 같은 fee 호출이 담긴 객체에 따라 달라지는지 봐요.
                System.out.println("어른: " + adult.fee(base));
                System.out.println("어린이: " + kid.fee(base));
            }
        }
        ''',
        'Ticket kid = new Ticket();', 'Ticket kid = new Kid();',
        caution='변수 자료형만 Kid로 바꾸면 컴파일 오류가 나요.',
        hints=['Ticket kid = new Kid();로 바꿔요.'],
        scenarios=[{'base': '9000'}, {'base': '15000'}],
        wrong=[('Ticket kid = new Ticket();', 'Kid kid = new Ticket();'),
               ('Ticket adult = new Ticket();', 'Ticket adult = new Kid();')]))

    # 8. 접근 제어: private 필드는 밖에서 못 쓰고, 메서드가 규칙을 지켜요.
    tasks.append(java_task('private-access', 'private 필드는 밖에서 못 써요',
        '필드 앞에 private을 붙이면 그 클래스 안에서만 쓸 수 있어요. 밖에서 쓰면 컴파일 오류가 나요.\n'
        '그래서 밖에서는 메서드로 값을 읽고 바꿔요. void는 돌려주는 값이 없다는 뜻이에요.\n'
        '실행 전에 오류가 날 줄을 먼저 찾아 보세요.',
        '준비 코드를 실행해 오류 메시지를 읽어 보세요. private access는 밖에서 못 쓴다는 뜻이에요.\n'
        'private은 그대로 두고 출금 메서드로 빼게 고치세요. `acc.withdraw(money);`로 바꾸면 돼요.\n'
        'money가 잔액보다 크면 어떻게 될지 if를 보고 적어 보세요.\n'
        'money를 바꿔 확인해 봤다면 채점 전에 처음 값으로 되돌리세요.',
        '''
        class Account {
            // 클래스 밖에서는 못 쓰는 잔액이에요.
            private int balance;

            // 처음 잔액을 받아 필드에 담아요.
            Account(int balance) {
                this.balance = balance;
            }

            // 잔액을 읽어서 돌려줘요.
            int getBalance() {
                return balance;
            }

            // 돌려주는 값이 없어서 void예요.
            void withdraw(int money) {
                // 잔액보다 많이는 못 빼요.
                if (money <= balance) {
                    balance -= money;
                }
            }
        }

        class Main {
            public static void main(String[] args) {
                // 처음 잔액과 뺄 금액이에요.
                int start = 10000;
                int money = 3000;
                Account acc = new Account(start);
                // 잔액에서 money만큼 빼려는 줄이에요.
                acc.balance -= money;
                // 잔액은 메서드로 읽어요.
                System.out.println("잔액: " + acc.getBalance());
            }
        }
        ''',
        'acc.balance -= money;', 'acc.withdraw(money);',
        caution='private을 지우면 오류는 사라져도 출금 규칙을 건너뛰어요.',
        hints=['빼는 줄을 `acc.withdraw(money);`로 바꿔요.'],
        scenarios=[{'start': '5000', 'money': '8000'}, {'start': '20000', 'money': '20000'},
                   {'start': '7000', 'money': '2500'}],
        wrong=[('private int balance;', 'int balance;'),
               ('acc.balance -= money;', 'acc.getBalance() -= money;')]))

    # 9. 도전: 필드는 변수 자료형, 메서드는 실제 객체를 따라가요.
    t = java_task('field-vs-method', '도전 · 필드와 메서드는 고르는 기준이 달라요',
        '자식에 부모와 같은 이름의 필드를 또 만들면 필드가 두 개 생겨요.\n'
        '클래스 안에서 쓴 score는 그 클래스 쪽 필드예요. 밖에서 읽는 필드는 변수 자료형 쪽이에요.\n'
        '메서드는 실제 객체 쪽을 불러요. 실행 전에 출력을 먼저 적어 보세요.',
        '준비 코드를 실행해 적은 답과 비교하세요.\n'
        'Bonus가 배수를 곱해 담은 점수가 나오게 고치세요.\n'
        '변수 자료형 Point는 그대로 두고 한 곳만 고치면 돼요.',
        '''
        class Point {
            // 부모 쪽 점수 필드예요.
            int score;

            // 받은 점수를 부모 쪽 필드에 담아요.
            Point(int score) {
                this.score = score;
            }

            // 이 클래스의 score를 돌려줘요.
            int getScore() {
                return score;
            }
        }

        // Bonus는 Point를 물려받고 같은 이름 필드를 또 가져요.
        class Bonus extends Point {
            // 자식 쪽 점수 필드예요.
            int score;

            Bonus(int score) {
                // 부모 생성자가 부모 쪽 필드를 채워요.
                super(score);
                // 보너스로 곱할 배수예요.
                int times = 2;
                // 자식 쪽 필드에는 배수를 곱해 담아요.
                this.score = score * times;
            }

            // 부모 메서드를 다시 만들어 자식 쪽 score를 돌려줘요.
            int getScore() {
                return score;
            }
        }

        class Main {
            public static void main(String[] args) {
                // 처음 받은 점수예요.
                int base = 30;
                // 변수 자료형은 Point, 실제 객체는 Bonus예요.
                Point p = new Bonus(base);
                // 점수를 출력해요.
                System.out.println("점수: " + p.score);
            }
        }
        ''',
        'p.score', 'p.getScore()',
        caution='`new Point(base)`로 바꾸면 Bonus의 배수 규칙이 사라져요.',
        hints=['변수 자료형이 Point라서 p.score는 부모 쪽 필드예요.',
               '실제 객체를 따라가는 건 메서드예요. getScore()를 불러 보세요.'],
        # times도 바꿔서, main에서 2를 직접 곱한 답을 걸러요.
        scenarios=[{'base': '45'}, {'base': '7', 'times': '3'}, {'times': '5'}],
        wrong=[('Point p = new Bonus(base);', 'Point p = new Point(base);'),
               ('p.score', 'p.score * 2')],
        challenge=True)
    # 메서드는 불렀지만 자식 생성자에서 this를 빼 매개변수에 담은 실수예요.
    tasks.append(solution_mistakes(t, [('this.score = score * times;', 'score = score * times;')]))

    # 10. 도전: static 공유 + 생성자 순서 + 오버라이딩.
    tasks.append(java_task('number-ticket', '도전 · 번호표는 한 번만 받아요',
        'static 필드, 생성자 순서, 오버라이딩을 함께 따라가요.\n'
        '출력 줄마다 어느 클래스의 생성자나 메서드가 찍었는지 먼저 적어 보세요.\n'
        'next가 언제 커지는지 아래 상태표의 ?를 채우면 쉬워요.\n\n'
        '| 만드는 객체 | 찍히는 줄 | 끝난 뒤 next |\n'
        '|---|---|---|\n'
        '| 일반 손님 1 | Guest 생성자: 1, 일반 1 | 2 |\n'
        '| 일반 손님 2 | ? | ? |\n'
        '| VIP 손님 | ? | ? |\n'
        '| 마지막 손님 | ? | ? |',
        '준비 코드를 실행해 적은 답과 비교하세요.\n'
        'VIP 손님도 번호를 한 번만 받게 고치세요.\n'
        'VIP 다음 손님의 번호도 건너뛰지 않아야 해요.',
        '''
        class Guest {
            // 모든 손님이 같이 쓰는 다음 번호예요.
            // 선언하면서 1을 담아 두어서 1번부터 줘요.
            static int next = 1;
            // 이 손님이 받은 번호예요.
            int no;

            // 손님 객체를 만들 때마다 실행돼요.
            Guest() {
                // 번호를 주고 다음 번호를 1 늘려요.
                no = next;
                next++;
                System.out.println("Guest 생성자: " + no);
            }

            // 손님 종류와 번호를 돌려줘요.
            String tag() {
                return "일반 " + no;
            }
        }

        // Vip는 Guest를 물려받아요.
        class Vip extends Guest {
            // super(...)가 없으니 부모 생성자가 먼저 실행돼요.
            Vip() {
                // VIP도 번호를 받게 하려는 두 줄이에요.
                no = next;
                next++;
                System.out.println("Vip 생성자: " + no);
            }

            // 부모의 tag를 다시 만들어요.
            String tag() {
                return "VIP " + no;
            }
        }

        class Main {
            public static void main(String[] args) {
                // VIP보다 먼저 온 일반 손님 수예요.
                int normal = 2;
                for (int i = 0; i < normal; i++) {
                    // 일반 손님을 만들고 바로 이름표를 출력해요.
                    Guest g = new Guest();
                    System.out.println(g.tag());
                }
                // VIP 손님이 와요. 변수 자료형은 Guest예요.
                Guest v = new Vip();
                System.out.println(v.tag());
                // VIP 다음에 일반 손님이 한 명 더 와요.
                Guest last = new Guest();
                System.out.println(last.tag());
            }
        }
        ''',
        '// VIP도 번호를 받게 하려는 두 줄이에요.\n' + B8 + 'no = next;\n' + B8 + 'next++;\n',
        '// 번호는 부모 생성자에서 이미 받았어요.\n',
        caution='부모 생성자가 준 번호를 자식이 또 주면 번호가 건너뛰어요.',
        hints=['Vip 객체를 만들면 Guest 생성자가 먼저 실행돼요.',
               'Vip 생성자 안에서 번호를 또 주는 두 줄을 찾아 보세요.'],
        scenarios=[{'normal': '0'}, {'normal': '4'}],
        # 두 줄 중 하나만 지운 실수예요.
        wrong=[('두 줄이에요.\n' + B8 + 'no = next;\n', '두 줄이에요.\n'),
               ('no = next;\n' + B8 + 'next++;\n' + B8 + 'System.out.println("Vip',
                'no = next;\n' + B8 + 'System.out.println("Vip')],
        challenge=True))

    required = sum(item['required'] for item in tasks)
    challenges = len(tasks) - required
    return lesson('engineer-java-objects', '자바의 객체·상속·호출',
        '실기 자바 문제처럼 객체·생성자·상속을 따라가요. 어느 메서드가 불리는지 먼저 적고 실행해요. '
        f'필수 문제 {required}개와 선택 도전 {challenges}개예요.',
        SOURCES, tasks)
