"""engineer-java-static: 7 answer-picking steps -> coding steps (2026-10-29)."""
from _kit import Script, todo

PRD_SCOPE = ['두 챕터·두 단원·여덟 스텝으로 표 발급 창구의 클래스 값과 객체 값을 나눠요.',
             '클래스 변수·객체 변수·생성자·초기화 순서를 실행으로 확인하고 한두 줄을 직접 고쳐요. 마지막 생성 순서만 짧게 직접 적어요.']
PRD_GRADING = ['직접 고친 코드를 실제 JDK 25로 실행해 판정해요. 준비 값(처음 값·장수·더할 수)을 바꾼 실행도 맞아야 해요.',
               '고정 출력, 객체를 만들어 우회한 답, 같은 객체를 두 이름으로 센 답은 거절해요.',
               '마지막 생성 순서(stp_3e1bfdc6-f723-432e-975f-008b07d17ee3)는 짧은 답안을 판정해요.',
               '마지막 도전(stp_1b79ae00-24ed-4ce1-bc83-5ee7121d3a93): 시작 답안은 실패해야 해요. 실제 실행 결과 또는 각 서술형 답안 칸을 검사하고 오답과 동등한 정답도 대조해요.']
PRD_NARRATION = ['먼저 준비 코드를 실행해 클래스 값과 객체 값의 실제 출력을 읽어요. 한 곳을 고친 뒤 다시 실행해 차이를 짚어요.',
                 '코드 흐름 보기로 static 초기화가 한 번인지, 생성자가 new마다 불리는지, 값이 클래스와 객체 중 어디에 있는지 확인하게 해요.',
                 '전체 답을 한 번에 갈아 끼우지 않아요. 음성은 준비한 뒤 화면과 맞춰요.']

# ---- 1. 객체 없이 클래스 값 읽기 -------------------------------------------------------
s1 = '''class Ticket {
    // 모든 표가 함께 읽는 클래스 변수예요.
    static int total = 4;
    // 표를 만들면 이 줄이 출력돼요.
    Ticket() { System.out.println("new ticket"); }
}
public class Main {
    public static void main(String[] args) {
        // 이 주석 아래 줄에 표를 만들지 않고 클래스 이름으로 total을 출력하세요.
    }
}
'''
s1_solution = s1.replace('        // 이 주석 아래 줄에 표를 만들지 않고 클래스 이름으로 total을 출력하세요.\n',
                         '        // 이 주석 아래 줄에 표를 만들지 않고 클래스 이름으로 total을 출력하세요.\n'
                         '        // static 변수는 클래스에 하나 있어요. new 없이 Ticket.total로 읽어요.\n        System.out.println(Ticket.total);\n')
n1 = (Script(s1)
      .say('표를 만들지 않고 클래스 변수 total을 읽어야 해요.', 'text:주석 아래 줄에 표를 만들지 않고 클래스 이름으로 total을 출력하세요.')
      .patch('        // 이 주석 아래 줄에 표를 만들지 않고 클래스 이름으로 total을 출력하세요.\n',
             '        // 이 주석 아래 줄에 표를 만들지 않고 클래스 이름으로 total을 출력하세요.\n        System.out.println(Ticket.total);\n',
             '클래스 이름 Ticket 뒤에 점을 찍고 total을 읽어요.')
      .run('println(Ticket.total)')
      .say('4가 나와요. new ticket 줄은 없으니 표를 하나도 만들지 않았어요.', 'output')
      .say('코드 흐름 보기에서는 static 변수 칸에 total이 있고 Ticket() 호출은 없어요.', 'text:코드 흐름 보기를 눌러 객체 없이 static 변수 칸에서 total을 찾으세요.')
      .say('조심하세요. new Ticket().total로 읽어도 값은 같지만 표가 하나 만들어져 new ticket이 출력돼요.', 'code:System.out.println(Ticket.total);'))

# ---- 2. 객체마다의 값과 공유 값 --------------------------------------------------------
s2 = '''class Ticket {
    static int total = 0;
    // local은 각 객체에 따로 있어요.
    int local = 0;
}
public class Main {
    public static void main(String[] args) {
        Ticket a = new Ticket();
        Ticket b = new Ticket();
        a.local++;
        Ticket.total++;
        // 이 주석 아래에 b의 local을 1 늘리고 공유 total도 1 늘리세요.
        System.out.println(a.local + ":" + b.local + ":" + Ticket.total);
    }
}
'''
s2_solution = s2.replace('        // 이 주석 아래에 b의 local을 1 늘리고 공유 total도 1 늘리세요.\n',
                         '        // 이 주석 아래에 b의 local을 1 늘리고 공유 total도 1 늘리세요.\n'
                         '        // b.local은 b 객체의 칸이고, Ticket.total은 두 표가 함께 쓰는 하나뿐인 칸이에요.\n        b.local++;\n        Ticket.total++;\n')
n2 = (Script(s2)
      .say('a에 한 장을 더했어요. 이번에는 b의 local과 공유 total을 하나씩 늘려야 해요.', 'text:주석 아래에 b의 local을 1 늘리고 공유 total도 1 늘리는 두 줄을 쓰세요.')
      .run('println(a.local + ":" + b.local + ":" + Ticket.total)')
      .say('1:0:1이에요. a.local만 늘었고 b.local은 아직 0이에요.', 'output')
      .patch('        // 이 주석 아래에 b의 local을 1 늘리고 공유 total도 1 늘리세요.\n',
             '        // 이 주석 아래에 b의 local을 1 늘리고 공유 total도 1 늘리세요.\n        b.local++;\n',
             'b.local을 1 늘려요.')
      .run('println(a.local + ":" + b.local + ":" + Ticket.total)')
      .say('1:1:1이에요. b의 칸만 늘고 total은 그대로예요.', 'output')
      .patch('        b.local++;\n', '        b.local++;\n        Ticket.total++;\n', 'Ticket.total도 1 늘려요.')
      .run('println(a.local + ":" + b.local + ":" + Ticket.total)')
      .say('1:1:2예요. total은 두 표가 함께 쓰는 하나의 칸이라 두 번 늘었어요.', 'output')
      .say('코드 흐름 보기에서 local은 두 Ticket 상자 안에, total은 static 변수 칸에 하나 있어요.', 'text:코드 흐름 보기를 눌러 local과 total이 각각 어디에 있는지 보세요.')
      .say('조심하세요. b.local 대신 a.local을 한 번 더 늘리면 b는 0으로 남아요.', 'code:b.local++;'))

# ---- 3. 생성자는 new마다 ---------------------------------------------------------------
s3 = '''class Ticket {
    static int total = 0;
    // new로 만들 때마다 이 생성자가 실행돼요.
    Ticket() { total++; }
}
public class Main {
    public static void main(String[] args) {
        Ticket a = new Ticket();
        // 이 줄을 고쳐 b가 새 표를 만들게 하세요.
        Ticket b = a;
        System.out.println(Ticket.total);
        System.out.println(a == b);
    }
}
'''
s3_solution = s3.replace('        Ticket b = a;\n', '        // new를 한 번 더 써야 생성자가 다시 실행되고 다른 객체가 생겨요.\n        Ticket b = new Ticket();\n')
n3 = (Script(s3)
      .say('생성자는 total을 1 늘려요. b도 새 표가 되게 만들어야 해요.', 'text:b를 만드는 줄을 고쳐 b가 새 Ticket 객체가 되게 하세요.')
      .run('println(Ticket.total)', 'println(a == b)')
      .say('1과 true예요. b = a는 표를 만들지 않고 같은 객체를 한 번 더 가리켰어요.', 'output')
      .patch('        Ticket b = a;\n', '        Ticket b = new Ticket();\n', 'new Ticket()으로 두 번째 표를 만들어요.')
      .run('println(Ticket.total)', 'println(a == b)')
      .say('2와 false예요. 생성자가 두 번 실행됐고 a와 b는 다른 객체예요.', 'output')
      .flow('Ticket() { total++; }', '코드 흐름 보기로 첫 new Ticket()이 생성자 Ticket()을 부른 단계를 열었어요. static 변수 total은 아직 0이에요.', event='call', target='flow_statics')
      .flow('Ticket() { total++; }', '두 번째 new Ticket()의 생성자가 끝나는 단계예요. total은 2이고 객체 칸에는 Ticket이 두 개예요.', event='return', nth=2)
      .say('조심하세요. 변수 이름의 개수가 객체 수는 아니에요. 생성자는 new를 쓸 때만 실행돼요.', 'code:Ticket b = new Ticket();'))

# ---- 4. static 초기화 순서 ------------------------------------------------------------
s4 = '''class Ticket {
    // 두 선언의 순서를 바꿔 a가 b의 7을 읽게 하세요.
    static int a = read();
    static int b = 7;
    static int read() { return b; }
}
public class Main {
    public static void main(String[] args) {
        System.out.println(Ticket.a + ":" + Ticket.b);
    }
}
'''
s4_solution = s4.replace('    static int a = read();\n    static int b = 7;\n',
                         '    // static 초기화식은 위에서 아래 순서로 실행돼요. b를 먼저 준비해요.\n    static int b = 7;\n    static int a = read();\n')
n4 = (Script(s4)
      .say('a는 read()로 b를 읽어요. a가 7을 갖게 선언 순서를 바꿔야 해요.', 'text:두 static 선언의 순서를 바꿔 a가 b의 7을 읽게 하세요.')
      .run('println(Ticket.a + ":" + Ticket.b)')
      .say('0:7이에요. a를 준비할 때 b는 아직 기본값 0이었어요.', 'output')
      .say('코드 흐름 보기에서 Ticket static 초기화가 a 줄을 먼저 실행하는 걸 볼 수 있어요.', 'text:코드 흐름 보기를 눌러 static 초기화가 어느 줄부터 실행되는지 보세요.')
      .patch('    static int a = read();\n    static int b = 7;\n', '    static int b = 7;\n    static int a = read();\n', 'b 선언을 a 선언 위로 올려요.')
      .run('println(Ticket.a + ":" + Ticket.b)')
      .say('7:7이에요. b가 먼저 7이 된 뒤 a가 read()로 그 값을 읽었어요.', 'output')
      .say('조심하세요. a = 7처럼 숫자를 적으면 지금은 맞아도 b가 바뀌면 a와 달라져요.', 'code:static int a = read();'))

# ---- 5. static 블록은 한 번 ------------------------------------------------------------
s5 = '''class Ticket {
    static { System.out.print("S"); }
    { System.out.print("I"); }
    Ticket() { System.out.print("C"); }
}
public class Main {
    public static void main(String[] args) {
        int count = 2;
        // 이 주석 아래에 count장만큼 new Ticket()을 반복해 만드세요.
        System.out.println();
    }
}
'''
s5_solution = s5.replace('        // 이 주석 아래에 count장만큼 new Ticket()을 반복해 만드세요.\n',
                         '        // 이 주석 아래에 count장만큼 new Ticket()을 반복해 만드세요.\n'
                         '        // static 블록 S는 첫 사용 때 한 번, I와 C는 표를 만들 때마다 출력돼요.\n'
                         '        for (int i = 0; i < count; i++) {\n            new Ticket();\n        }\n')
n5 = (Script(s5)
      .say('count장만큼 표를 만들어야 해요. 지금은 한 장도 만들지 않아요.', 'text:주석 아래에 count장만큼 new Ticket()을 반복해 만드는 for 문을 쓰세요.')
      .run('println()')
      .say('빈 줄만 나와요. Ticket을 한 번도 쓰지 않아서 static 블록도 실행되지 않았어요.', 'output')
      .patch('        // 이 주석 아래에 count장만큼 new Ticket()을 반복해 만드세요.\n',
             '        // 이 주석 아래에 count장만큼 new Ticket()을 반복해 만드세요.\n        for (int i = 0; i < count; i++) {\n            new Ticket();\n        }\n',
             'i가 0부터 count보다 작을 동안 new Ticket()을 반복해요.')
      .run('println()')
      .say('SICIC예요. S는 처음 한 번, I와 C는 두 표마다 출력됐어요.', 'output')
      .say('코드 흐름 보기에서 Ticket static 초기화는 한 번, Ticket()은 두 번 불려요.', 'text:코드 흐름 보기를 눌러 static 초기화와 Ticket() 호출 횟수를 비교하세요.')
      .say('조심하세요. static 블록도 객체마다 실행된다고 생각하면 SICSIC를 예상하게 돼요.', 'code:static { System.out.print("S"); }'))

# ---- 6. 상위 클래스부터 ----------------------------------------------------------------
s6 = '''class Parent {
    static { System.out.print("P"); }
    { System.out.print("p"); }
    Parent() { System.out.print("1"); }
}
// 이 줄을 고쳐 Ticket이 Parent를 상속하게 하세요.
class Ticket {
    static { System.out.print("C"); }
    { System.out.print("c"); }
    Ticket() { System.out.print("2"); }
}
public class Main {
    public static void main(String[] args) {
        int count = 1;
        for (int i = 0; i < count; i++) {
            new Ticket();
        }
        System.out.println();
    }
}
'''
s6_solution = s6.replace('class Ticket {\n', '// extends Parent: Ticket을 만들기 전에 Parent 부분부터 준비해요.\nclass Ticket extends Parent {\n')
n6 = (Script(s6)
      .say('Ticket이 Parent를 상속하게 클래스 선언 한 줄을 고쳐야 해요.', 'text:Ticket 클래스 선언을 고쳐 Ticket이 Parent를 상속하게 하세요.')
      .run('println()')
      .say('Cc2예요. 지금은 Parent와 관계가 없어서 Ticket 부분만 준비돼요.', 'output')
      .patch('class Ticket {\n', 'class Ticket extends Parent {\n', 'class Ticket 뒤에 extends Parent를 붙여요.')
      .run('println()')
      .say('PCp1c2예요. 클래스는 P, C 순서로 준비되고 객체도 Parent 쪽 p1 뒤에 c2가 와요.', 'output')
      .say('코드 흐름 보기에서 Parent() 생성자가 Ticket() 생성자보다 먼저 끝나요.', 'text:코드 흐름 보기를 눌러 Parent()와 Ticket() 생성자의 순서를 보세요.')
      .say('조심하세요. 하위 클래스를 먼저 준비한다고 생각하면 CPc2p1을 예상하게 돼요.', 'code:class Ticket extends Parent {'))

# ---- 7. 공유 필드로 바꾸기 -------------------------------------------------------------
s7 = '''class Ticket {
    // 이 선언을 고쳐 두 표가 같은 total을 함께 쓰게 하세요.
    int total;
    int local;
}
public class Main {
    public static void main(String[] args) {
        int step = 2;
        Ticket a = new Ticket();
        Ticket b = new Ticket();
        a.total += step;
        System.out.println(b.total + ":" + b.local);
    }
}
'''
s7_solution = s7.replace('    int total;\n', '    // static을 붙이면 total은 객체마다가 아니라 클래스에 하나만 있어요.\n    static int total;\n')
n7 = (Script(s7)
      .say('a에서 늘린 total을 b에서도 읽어야 해요. total을 공유하는 칸으로 바꿔요.', 'text:total 선언을 고쳐 두 표가 같은 total을 함께 쓰게 하세요.')
      .run('println(b.total + ":" + b.local)')
      .say('0:0이에요. 지금 total은 객체마다 따로 있어서 a의 total만 2가 됐어요.', 'output')
      .patch('    int total;\n', '    static int total;\n', 'total 앞에 static을 붙여요.')
      .run('println(b.total + ":" + b.local)')
      .say('2:0이에요. b.total도 클래스에 하나뿐인 total을 읽어요. local은 그대로 0이에요.', 'output')
      .say('코드 흐름 보기에서 total이 객체 상자에서 빠져 static 변수 칸으로 옮겨 가요.', 'text:코드 흐름 보기를 눌러 total이 객체 안에 있는지 static 변수 칸에 있는지 보세요.')
      .say('조심하세요. b.total += 2를 한 줄 더 쓰면 지금은 2가 나와도 공유한 값이 아니에요.', 'code:static int total;'))

SPECS = [
    dict(old='stp_14f1574d-6b8e-4d73-a6e9-e01f3f9d64df', title='표를 만들지 않고 Ticket.total을 출력하세요',
         objectives=['객체 없이 클래스 이름으로 static 변수를 읽어요.'],
         core_flow='Ticket.total=4를 new 없이 클래스 이름으로 읽어 4를 확인한다. 생성자가 new ticket을 출력하므로 객체를 만드는 우회가 출력에 드러난다. 코드 흐름 보기에서 static 변수 칸과 Ticket 생성자 호출 없음이 보인다. 채점은 total의 처음 값을 바꿔 실행한다.',
         goal='static이 붙은 total은 표 객체마다 있는 값이 아니라 Ticket 클래스에 하나만 있는 클래스 변수예요. 그래서 표를 만들지 않아도 `Ticket.total`처럼 클래스 이름으로 읽을 수 있어요. 표를 만들면 생성자가 new ticket을 출력해요.\n\n'
              '주석 아래 줄에 표를 만들지 않고 클래스 이름으로 total을 출력하세요. 채점은 total의 처음 값을 바꿔서도 실행해요.\n\n'
              + todo('주석 아래 줄에 클래스 이름 Ticket으로 total을 읽어 출력하는 줄을 쓰세요.', '코드 실행을 눌러 4만 나오고 new ticket은 없는지 확인하세요.',
                     '코드 흐름 보기를 눌러 객체 없이 static 변수 칸에서 total을 찾으세요.', '작성한 코드를 제출하세요.'),
         starter_code=s1, solution=s1_solution, tests=[{'input': '', 'expected': '4'}],
         variations=[{'values': {'total': '5'}, 'expected': '5'}, {'values': {'total': '0'}, 'expected': '0'}],
         code_flow=True, narration=n1.actions,
         review={'조심하세요. new Ticket().total로 읽어도 값은 같지만 표가 하나 만들어져 new ticket이 출력돼요.':
                 '실제 흔한 우회(객체로 static 접근)와 그 결과(생성자 출력)를 말해요. 「읽어도 값은 같지만」 뒤에 표가 만들어진다는 대조가 실제로 맞아요.'},
         reject=[([['        System.out.println(Ticket.total);\n', '        System.out.println(4);\n']], 'Printing a typed value'),
                 ([['        System.out.println(Ticket.total);\n', '        System.out.println(new Ticket().total);\n']], 'Creating a ticket to read the class value')],
         accept=[([['        System.out.println(Ticket.total);\n', '        int current = Ticket.total;\n        System.out.println(current);\n']], 'Reading into a local first')]),
    dict(old='stp_20d58796-0ca6-4ff8-aa05-72ed1210a56b', title='b의 local과 공유 total을 하나씩 늘리세요',
         objectives=['각 객체의 필드와 공유 static 필드를 나눠 바꿔요.'],
         core_flow='두 Ticket을 만든 뒤 a.local++와 Ticket.total++가 준비돼 1:0:1이다. b.local++와 Ticket.total++를 차례로 더해 1:1:1, 1:1:2를 비교한다. 코드 흐름 보기에서 local은 객체마다, total은 static 칸에 하나 있다. 채점은 처음 값을 바꿔 실행한다.',
         goal='a와 b는 Ticket 객체 두 개예요. local은 객체마다 따로 있는 값이고, static total은 두 표가 함께 쓰는 하나의 값이에요. 준비 코드는 a의 local과 total을 1씩 늘렸어요.\n\n'
              '주석 아래에 b의 local을 1 늘리고 공유 total도 1 늘리는 두 줄을 쓰세요. 채점은 local과 total의 처음 값을 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 1:0:1이 나오는지 확인하세요.', '주석 아래에 b의 local을 1 늘리는 줄을 쓰세요.', '그 아래에 Ticket.total을 1 늘리는 줄을 쓰세요.',
                     '코드 실행을 눌러 1:1:2가 나오는지 확인하세요.', '코드 흐름 보기를 눌러 local과 total이 각각 어디에 있는지 보세요.', '작성한 코드를 제출하세요.'),
         starter_code=s2, solution=s2_solution, tests=[{'input': '', 'expected': '1:1:2'}],
         variations=[{'values': {'total': '5'}, 'expected': '1:1:7'}, {'values': {'local': '3'}, 'expected': '4:4:2'}],
         code_flow=True, narration=n2.actions,
         review={'조심하세요. b.local 대신 a.local을 한 번 더 늘리면 b는 0으로 남아요.': '실제 실수(다른 객체의 같은 이름 필드)와 결과를 말해요.'},
         reject=[([['        b.local++;\n', '        a.local++;\n']], 'Changing a again instead of b'),
                 ([['        System.out.println(a.local + ":" + b.local + ":" + Ticket.total);\n', '        System.out.println("1:1:2");\n']], 'Printing typed text'),
                 ([['        Ticket.total++;\n        System.out.println', '        System.out.println']], 'Forgetting the shared total')],
         accept=[([['        b.local++;\n        Ticket.total++;\n', '        b.local += 1;\n        b.total++;\n']], 'b.total is the same class variable')]),
    dict(old='stp_23dfa767-4f28-4677-be2e-78ada16be33c', title='b를 새 표로 만들어 생성자가 두 번 실행되게 하세요',
         objectives=['참조 대입과 new로 만든 새 객체를 생성자 실행 횟수로 구별해요.'],
         core_flow='생성자에서 total++한다. Ticket a=new Ticket, b=a면 total1, a==b true다. b=new Ticket()으로 고쳐 total2, a==b false를 확인한다. 코드 흐름 보기에서 Ticket() 호출이 두 번 지나간다. 채점은 total의 처음 값을 바꿔 실행한다.',
         goal='Ticket()은 표를 만들 때마다 total을 1 늘리는 생성자예요. 지금 b는 a가 가리키는 표를 함께 가리킬 뿐이라 생성자는 한 번만 실행돼요.\n\n'
              'b를 만드는 줄을 고쳐 b가 새 Ticket 객체가 되게 하세요. 출력의 둘째 줄 `a == b`는 두 변수가 같은 객체인지 보여 줘요. 채점은 total의 처음 값을 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 1과 true가 나오는지 확인하세요.', '`Ticket b = a;`를 새 표를 만드는 줄로 고치세요.', '코드 실행을 눌러 2와 false가 나오는지 확인하세요.',
                     '코드 흐름 보기를 눌러 Ticket() 생성자가 몇 번 불리는지 세어 보세요.', '수정한 코드를 제출하세요.'),
         starter_code=s3, solution=s3_solution, tests=[{'input': '', 'expected': '2\nfalse'}],
         variations=[{'values': {'total': '3'}, 'expected': '5\nfalse'}],
         code_flow=True, narration=n3.actions,
         review={'조심하세요. 변수 이름의 개수가 객체 수는 아니에요. 생성자는 new를 쓸 때만 실행돼요.': '실제 오개념(변수 수 = 객체 수)과 이 스텝의 b = a 결과로 확인되는 사실을 말해요.'},
         reject=[([['        Ticket b = new Ticket();\n', '        Ticket b = a;\n        Ticket.total++;\n']], 'Counting by hand while sharing one object'),
                 ([['        System.out.println(Ticket.total);\n', '        System.out.println(2);\n']], 'Printing a typed count')],
         accept=[([['        Ticket b = new Ticket();\n', '        Ticket b;\n        b = new Ticket();\n']], 'Declaring first, then creating')]),
    dict(old='stp_c69f0ad6-4fc0-415c-a31d-0647e10db4dd', title='a가 b의 7을 읽도록 static 선언 순서를 바꾸세요',
         objectives=['static 필드의 기본값과 선언 순서대로 실행되는 초기화를 구별해요.'],
         core_flow='static int a=read(); static int b=7; read는 b 반환으로 0:7이다. 준비 단계의 기본값 0을 선언 순서 실행에서 읽은 것이다. 두 선언의 순서를 바꿔 7:7을 확인한다. 코드 흐름 보기에서 Ticket static 초기화의 줄 순서를 본다. 채점은 b의 값을 바꿔 a가 실제로 b를 읽는지 확인한다.',
         goal='클래스를 처음 쓸 때 static 필드는 먼저 모두 기본값 0으로 준비되고, 그다음 위에서 아래 순서로 초기화식이 실행돼요. 지금은 a를 준비할 때 read()가 아직 0인 b를 읽어요.\n\n'
              '두 static 선언의 순서를 바꿔 a가 b의 7을 읽게 하세요. read()와 출력문은 그대로 둬요. 채점은 b의 값을 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 0:7이 나오는지 확인하세요.', '코드 흐름 보기를 눌러 static 초기화가 어느 줄부터 실행되는지 보세요.',
                     '`static int b = 7;` 줄을 `static int a = read();` 줄 위로 옮기세요.', '코드 실행을 눌러 7:7이 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s4, solution=s4_solution, tests=[{'input': '', 'expected': '7:7'}],
         variations=[{'values': {'b': '9'}, 'expected': '9:9'}, {'values': {'b': '0'}, 'expected': '0:0'}],
         code_flow=True, narration=n4.actions,
         review={'조심하세요. a = 7처럼 숫자를 적으면 지금은 맞아도 b가 바뀌면 a와 달라져요.': '실제 우회(숫자 대입)와 결과(b 변경 채점)를 말해요. 「지금은 맞아도」 뒤에 「달라진다」는 대조가 이어져요.'},
         reject=[([['    static int a = read();\n', '    static int a = 7;\n']], 'Typing 7 instead of reading b'),
                 ([['        System.out.println(Ticket.a + ":" + Ticket.b);\n', '        System.out.println("7:7");\n']], 'Printing typed text')],
         accept=[([['    static int a = read();\n', '    static int a = b;\n']], 'Reading b directly after it is ready')]),
    dict(old='stp_4c2c4b7d-5e31-4145-a7db-af2778f04224', title='count장만큼 표를 만들어 static 블록이 몇 번 실행되는지 보세요',
         objectives=['클래스 초기화 블록은 한 번, 인스턴스 초기화와 생성자는 new마다 실행됨을 구별해요.'],
         core_flow='Ticket static 블록S, 인스턴스 블록I, 생성자C가 있다. 준비 코드는 표를 만들지 않아 빈 줄이고 static 블록도 실행되지 않는다. count장을 for로 만들어 SICIC를 확인한다. 코드 흐름 보기에서 static 초기화 한 번, Ticket() 두 번을 본다. 채점은 count를 3, 1, 0으로 바꿔 실행한다.',
         goal='`static { }` 블록은 클래스 초기화 블록이라 클래스가 처음 쓰일 때 한 번만 실행돼요. 이름 없는 `{ }` 블록은 인스턴스 초기화 블록이라 객체를 만들 때마다 생성자 직전에 실행돼요.\n\n'
              '주석 아래에 count장만큼 new Ticket()을 반복해 만드는 for 문을 쓰세요. 채점은 count를 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 빈 줄만 나오는지 확인하세요.', '주석 아래에 i를 0부터 count보다 작을 동안 늘리며 new Ticket()을 실행하는 for 문을 쓰세요.',
                     '코드 실행을 눌러 SICIC가 나오는지 확인하세요.', '코드 흐름 보기를 눌러 static 초기화와 Ticket() 호출 횟수를 비교하세요.', '작성한 코드를 제출하세요.'),
         starter_code=s5, solution=s5_solution, tests=[{'input': '', 'expected': 'SICIC'}],
         variations=[{'values': {'count': '3'}, 'expected': 'SICICIC'}, {'values': {'count': '1'}, 'expected': 'SIC'}, {'values': {'count': '0'}, 'expected': ''}],
         code_flow=True, narration=n5.actions,
         review={'조심하세요. static 블록도 객체마다 실행된다고 생각하면 SICSIC를 예상하게 돼요.': '실제 흔한 오개념과 그 오개념이 낳는 예상 출력을 말해요.'},
         reject=[([['        for (int i = 0; i < count; i++) {\n            new Ticket();\n        }\n', '        new Ticket();\n        new Ticket();\n']], 'Two fixed tickets ignore count'),
                 ([['        System.out.println();\n', '        System.out.println("SICIC");\n']], 'Printing typed text')],
         accept=[([['        for (int i = 0; i < count; i++) {\n            new Ticket();\n        }\n', '        int made = 0;\n        while (made < count) {\n            new Ticket();\n            made++;\n        }\n']], 'A while loop')]),
    dict(old='stp_ebefb8d5-1f0d-4ac3-8bdf-9315fcb49434', title='Ticket이 Parent를 상속하게 해 준비 순서를 확인하세요',
         objectives=['상위 클래스의 클래스 준비와 객체 준비가 먼저 실행됨을 이해해요.'],
         core_flow='Parent staticP/instancep/ctor1, Ticket staticC/instancec/ctor2가 있고 준비 코드는 상속이 없어 Cc2다. extends Parent를 붙여 PCp1c2를 확인한다. 코드 흐름 보기에서 Parent()가 Ticket()보다 먼저 끝난다. 채점은 count를 2로 바꿔 PCp1c2p1c2인지 확인한다.',
         goal='하위 클래스 객체를 만들면 상위 클래스 부분이 먼저 준비돼요. 클래스 준비(static 블록)도 상위 클래스부터 한 번씩, 객체 준비(인스턴스 블록·생성자)도 상위부터 차례로 실행돼요. 지금 Ticket은 Parent와 관계가 없어요.\n\n'
              'Ticket 클래스 선언을 고쳐 Ticket이 Parent를 상속하게 하세요. 채점은 만드는 장수 count를 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 Cc2가 나오는지 확인하세요.', '`class Ticket {`에 Parent를 상속하는 extends를 붙이세요.', '코드 실행을 눌러 PCp1c2가 나오는지 확인하세요.',
                     '코드 흐름 보기를 눌러 Parent()와 Ticket() 생성자의 순서를 보세요.', '수정한 코드를 제출하세요.'),
         starter_code=s6, solution=s6_solution, tests=[{'input': '', 'expected': 'PCp1c2'}],
         variations=[{'values': {'count': '2'}, 'expected': 'PCp1c2p1c2'}, {'values': {'count': '0'}, 'expected': ''}],
         code_flow=True, narration=n6.actions,
         review={'조심하세요. 하위 클래스를 먼저 준비한다고 생각하면 CPc2p1을 예상하게 돼요.': '실제 흔한 오개념과 그 오개념의 예상 출력을 말해요.'},
         reject=[([['        System.out.println();\n', '        System.out.println("PCp1c2");\n']], 'Printing typed text'),
                 ([['class Ticket extends Parent {\n', 'class Ticket {\n']], 'No inheritance')],
         accept=[]),
    dict(old='stp_b01a729c-a939-454c-a4d3-c63defef2630', title='total을 static으로 바꿔 두 표가 함께 쓰게 하세요',
         objectives=['인스턴스 필드와 static 필드의 차이를 선언으로 구별해요.'],
         core_flow='Ticket의 total이 인스턴스 필드라 a.total+=step 뒤 b.total은 0이다. static을 붙여 b.total도 2가 되는 것을 확인한다. b.local은 0으로 남는다. 코드 흐름 보기에서 total이 객체 상자에서 static 칸으로 옮겨 간다. 채점은 step을 바꿔 실행한다.',
         goal='지금 total은 객체마다 따로 있는 인스턴스 필드예요. 그래서 a의 total을 늘려도 b의 total은 0이에요. static을 붙인 필드는 클래스에 하나만 있어서 어느 객체로 읽어도 같은 값이에요.\n\n'
              'total 선언을 고쳐 두 표가 같은 total을 함께 쓰게 하세요. 다른 줄은 그대로 둬요. 채점은 더하는 값 step을 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 0:0이 나오는지 확인하세요.', '`int total;` 선언에 static을 붙이세요.', '코드 실행을 눌러 2:0이 나오는지 확인하세요.',
                     '코드 흐름 보기를 눌러 total이 객체 안에 있는지 static 변수 칸에 있는지 보세요.', '수정한 코드를 제출하세요.'),
         starter_code=s7, solution=s7_solution, tests=[{'input': '', 'expected': '2:0'}],
         variations=[{'values': {'step': '5'}, 'expected': '5:0'}, {'values': {'step': '0'}, 'expected': '0:0'}],
         code_flow=True, narration=n7.actions,
         review={'조심하세요. b.total += 2를 한 줄 더 쓰면 지금은 2가 나와도 공유한 값이 아니에요.': '실제 우회와 그 한계(공유가 아님, step 변경 채점)를 말해요. 「나와도」 뒤 「공유한 값이 아니다」 대조가 맞아요.'},
         reject=[([['    static int total;\n', '    int total;\n'], ['        a.total += step;\n', '        a.total += step;\n        b.total += 2;\n']], 'Adding to b separately with a typed 2'),
                 ([['        System.out.println(b.total + ":" + b.local);\n', '        System.out.println("2:0");\n']], 'Printing typed text')],
         accept=[]),
]
