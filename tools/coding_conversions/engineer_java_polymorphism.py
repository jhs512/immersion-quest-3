"""engineer-java-polymorphism: 7 answer-picking steps -> coding steps (2026-10-29)."""
from _kit import Script, todo

PRD_SCOPE = ['두 챕터·두 단원·아홉 스텝으로 같은 발급 규칙의 호출을 읽어요.',
             '재정의·필드 숨김·static 숨김·오버로드·생성 중 호출·예외·finally를 한두 줄씩 직접 고쳐 실행하고, 마지막 합계만 짧게 직접 적어요.']
PRD_GRADING = ['직접 고친 코드를 실제 JDK 25로 실행해 판정해요. 준비 값(추가 값·문자열·재고·더할 수)을 바꾼 실행도 맞아야 해요.',
               '고정 출력과 숫자를 적어 넣은 답은 거절해요.',
               '마지막 호출 결과(stp_2b7fe0cf-5e2f-4581-8af6-52b7db75b50a)는 짧은 답안을 판정해요.',
               '마지막 도전(stp_045de1e3-6968-4517-b056-6ef2e6b13549): 시작 답안은 실패해야 해요. 실제 실행 결과 또는 각 서술형 답안 칸을 검사하고 오답과 동등한 정답도 대조해요.']
PRD_NARRATION = ['먼저 준비 코드를 실행해 실제 출력을 읽고, 한 곳을 고친 뒤 다시 실행해 차이를 짚어요.',
                 '코드 흐름 보기로 어느 클래스의 메서드가 불리는지, 생성 중 필드 값이 무엇인지 확인하게 해요.',
                 '필드와 호출·정적과 동적·생성 전 기본값·finally와 반환값을 조심할 지점으로 짚어요.']

# ---- 1. 재정의해서 실제 객체의 메서드 부르기 ------------------------------------------
s1 = '''class Rule {
    int value() { return 2; }
}
class Bonus extends Rule {
    int extra = 7;
    // 이 주석 아래에 value()를 재정의해 extra를 반환하세요.
}

public class Main {
    public static void main(String[] args) {
        Rule rule = new Bonus();
        System.out.println(rule.value());
    }
}
'''
s1_solution = s1.replace('    // 이 주석 아래에 value()를 재정의해 extra를 반환하세요.\n',
                         '    // 이 주석 아래에 value()를 재정의해 extra를 반환하세요.\n'
                         '    // 같은 이름·같은 매개변수로 다시 쓰면 실제 객체가 Bonus일 때 이 메서드가 실행돼요.\n'
                         '    @Override int value() { return extra; }\n')
n1 = (Script(s1)
      .say('rule의 선언형은 Rule이고 실제 객체는 Bonus예요. Bonus에 value()를 재정의해야 해요.', 'text:주석 아래에 value()를 재정의해 extra를 반환하는 메서드를 쓰세요.')
      .run('println(rule.value())')
      .say('2가 나와요. Bonus에 value()가 없어서 물려받은 Rule의 value()가 실행됐어요.', 'output')
      .patch('    // 이 주석 아래에 value()를 재정의해 extra를 반환하세요.\n',
             '    // 이 주석 아래에 value()를 재정의해 extra를 반환하세요.\n    @Override int value() { return extra; }\n',
             '같은 이름의 value()를 Bonus에 쓰고 extra를 반환해요.')
      .run('println(rule.value())')
      .say('7이에요. 변수는 Rule형이어도 실제 객체 Bonus의 value()가 불렸어요.', 'output')
      .say('코드 흐름 보기에서 rule.value() 줄 다음에 Bonus.value()로 들어가요.', 'text:코드 흐름 보기를 눌러 rule.value()가 어느 클래스의 value()로 들어가는지 보세요.')
      .say('조심하세요. return 7처럼 숫자를 적으면 지금은 같아도 extra가 바뀌면 틀려요.', 'code:@Override int value() { return extra; }'))

# ---- 2. 필드는 선언형, 메서드는 실제 객체 ---------------------------------------------
s2 = '''class Rule {
    int count = 2;
    int value() { return count; }
}
class Bonus extends Rule {
    // 같은 이름의 필드가 Rule의 count를 가려요.
    int count;
    Bonus(int count) { this.count = count; }
    @Override int value() { return count; }
}

public class Main {
    public static void main(String[] args) {
        int given = 7;
        Rule rule = new Bonus(given);
        System.out.println(rule.count + ":" + rule.value());
        // 이 주석 아래에 rule을 Bonus로 바꿔 읽어 Bonus의 count를 출력하세요.
    }
}
'''
s2_solution = s2.replace('        // 이 주석 아래에 rule을 Bonus로 바꿔 읽어 Bonus의 count를 출력하세요.\n',
                         '        // 이 주석 아래에 rule을 Bonus로 바꿔 읽어 Bonus의 count를 출력하세요.\n'
                         '        // 필드는 변수의 선언형으로 골라요. (Bonus)로 바꿔야 Bonus의 count를 읽어요.\n'
                         '        System.out.println(((Bonus) rule).count);\n')
n2 = (Script(s2)
      .say('rule.count와 rule.value()가 같은 값을 읽는지 먼저 실행해 봐요.', 'text:rule.count와 rule.value()가 각각 무엇을 읽는지 실행해 비교하세요.')
      .run('println(rule.count + ":" + rule.value())')
      .say('2:7이에요. rule.count는 선언형 Rule의 필드, rule.value()는 실제 객체 Bonus의 메서드를 썼어요.', 'output')
      .patch('        // 이 주석 아래에 rule을 Bonus로 바꿔 읽어 Bonus의 count를 출력하세요.\n',
             '        // 이 주석 아래에 rule을 Bonus로 바꿔 읽어 Bonus의 count를 출력하세요.\n        System.out.println(((Bonus) rule).count);\n',
             'rule을 (Bonus)로 바꿔 읽은 뒤 count를 출력해요.')
      .run('println(rule.count + ":" + rule.value())', 'println(((Bonus) rule).count)')
      .say('둘째 줄은 7이에요. 같은 객체라도 Bonus형으로 읽으면 Bonus의 count가 골라져요.', 'output')
      .say('코드 흐름 보기에서 Bonus 객체 상자 하나에 count 칸이 둘 있어요.', 'text:코드 흐름 보기를 눌러 Bonus 객체 안의 두 count 칸을 보세요.')
      .say('조심하세요. 필드는 재정의되지 않아요. rule.count는 실제 객체가 Bonus여도 Rule의 count예요.', 'code:rule.count'))

# ---- 3. static 메서드는 클래스 이름으로 -----------------------------------------------
s3 = '''class Rule {
    static String code = "P";
    static String name() { return code; }
}
class Bonus extends Rule {
    static String mark = "C";
    // Rule의 name()을 가리는 static 메서드예요.
    static String name() { return mark; }
}

public class Main {
    public static void main(String[] args) {
        Rule rule = new Bonus();
        // static 메서드는 변수의 선언형으로 골라요.
        System.out.println(rule.name());
        // 이 주석 아래에 Bonus 클래스 이름으로 name()을 불러 출력하세요.
    }
}
'''
s3_solution = s3.replace('        // 이 주석 아래에 Bonus 클래스 이름으로 name()을 불러 출력하세요.\n',
                         '        // 이 주석 아래에 Bonus 클래스 이름으로 name()을 불러 출력하세요.\n'
                         '        // static 메서드는 객체가 아니라 클래스에 속해요. Bonus.name()이 Bonus 것을 불러요.\n'
                         '        System.out.println(Bonus.name());\n')
n3 = (Script(s3)
      .say('rule.name()은 static 메서드예요. Bonus의 name()을 부르는 줄을 더해야 해요.', 'text:주석 아래에 Bonus 클래스 이름으로 name()을 불러 출력하는 줄을 쓰세요.')
      .run('println(rule.name())')
      .say('P예요. 실제 객체가 Bonus여도 static 메서드는 선언형 Rule의 것이 골라졌어요.', 'output')
      .patch('        // 이 주석 아래에 Bonus 클래스 이름으로 name()을 불러 출력하세요.\n',
             '        // 이 주석 아래에 Bonus 클래스 이름으로 name()을 불러 출력하세요.\n        System.out.println(Bonus.name());\n',
             'Bonus 클래스 이름 뒤에 점을 찍고 name()을 불러요.')
      .run('println(rule.name())', 'println(Bonus.name())')
      .say('P 다음 C예요. 클래스 이름을 Bonus로 써야 Bonus의 static 메서드가 불려요.', 'output')
      .say('코드 흐름 보기에서 첫 호출은 Rule.name(), 둘째 호출은 Bonus.name()으로 들어가요.', 'text:코드 흐름 보기를 눌러 두 호출이 각각 어느 클래스의 name()으로 들어가는지 보세요.')
      .say('조심하세요. static 메서드는 재정의되지 않고 가려질 뿐이라 @Override를 붙이면 컴파일 오류예요.', 'code:static String name() { return mark; }'))

# ---- 4. 오버로드는 선언형으로 고르기 --------------------------------------------------
s4 = '''class View {
    static String show(Object value) { return "O"; }
    static String show(String value) { return "S" + value.length(); }
}

public class Main {
    public static void main(String[] args) {
        // 이 줄의 선언형을 고쳐 String을 받는 show가 골라지게 하세요.
        Object text = "ticket";
        System.out.println(View.show(text));
    }
}
'''
s4_solution = s4.replace('        Object text = "ticket";\n',
                         '        // 오버로드는 컴파일할 때 인수의 선언형으로 골라요. String형이면 show(String)이에요.\n'
                         '        String text = "ticket";\n')
n4 = (Script(s4)
      .say('text에는 문자열이 들어 있지만 선언형은 Object예요. 선언형을 고쳐야 해요.', 'text:text의 선언형을 고쳐 String을 받는 show가 골라지게 하세요.')
      .run('println(View.show(text))')
      .say('O예요. 오버로드는 실제 값이 아니라 선언형 Object로 show(Object)를 골랐어요.', 'output')
      .patch('        Object text = "ticket";\n', '        String text = "ticket";\n', 'text의 선언형을 String으로 바꿔요.')
      .run('println(View.show(text))')
      .say('S6이에요. 이제 show(String)이 골라져 ticket의 길이 6을 붙였어요.', 'output')
      .say('조심하세요. 오버로드는 실행 중에 다시 고르지 않아요. 재정의와 달리 선언형이 정해요.', 'code:static String show(Object value)'))

# ---- 5. 상위 생성자에서 불린 재정의 메서드 -------------------------------------------
s5 = '''class Rule {
    Rule() { show(); }
    void show() { System.out.print("base"); }
}
class Bonus extends Rule {
    int value = 7;
    @Override void show() { System.out.print(value); }
}

public class Main {
    public static void main(String[] args) {
        Bonus rule = new Bonus();
        // 이 주석 아래에서 다 만들어진 rule의 show()를 한 번 더 부르세요.
        System.out.println();
    }
}
'''
s5_solution = s5.replace('        // 이 주석 아래에서 다 만들어진 rule의 show()를 한 번 더 부르세요.\n',
                         '        // 이 주석 아래에서 다 만들어진 rule의 show()를 한 번 더 부르세요.\n'
                         '        // 생성이 끝나 value = 7 초기화가 지난 뒤라 이번에는 7을 출력해요.\n'
                         '        rule.show();\n')
n5 = (Script(s5)
      .say('Rule 생성자가 show()를 불러요. 생성이 끝난 뒤에도 한 번 더 불러 값을 비교해야 해요.', 'text:주석 아래에서 다 만들어진 rule의 show()를 한 번 더 부르는 줄을 쓰세요.')
      .run('println()')
      .say('0이에요. 상위 생성자가 Bonus의 show()를 불렀는데 value = 7은 아직 실행되지 않았어요.', 'output')
      .patch('        // 이 주석 아래에서 다 만들어진 rule의 show()를 한 번 더 부르세요.\n',
             '        // 이 주석 아래에서 다 만들어진 rule의 show()를 한 번 더 부르세요.\n        rule.show();\n',
             'new Bonus() 다음 줄에서 rule.show()를 불러요.')
      .run('println()')
      .say('07이에요. 생성 중에는 0, 생성이 끝난 뒤에는 7이 나왔어요.', 'output')
      .say('코드 흐름 보기에서 Rule() 안의 show() 호출이 Bonus.show()로 들어가고 그때 value는 0이에요.', 'text:코드 흐름 보기를 눌러 Rule() 안에서 불린 show()가 value를 몇으로 읽는지 보세요.')
      .say('조심하세요. 필드 초기화 value = 7은 상위 생성자 Rule()이 끝난 뒤에 실행돼요.', 'code:int value = 7;'))

# ---- 6. 예외를 받는 catch 쓰기 --------------------------------------------------------
s6 = '''public class Main {
    public static void main(String[] args) {
        int stock = 0;
        try {
            System.out.print("A");
            if (stock == 0) throw new IllegalArgumentException("bad");
            System.out.print("B");
        // 이 주석 아래에 IllegalArgumentException을 받아 C를 출력하는 catch를 쓰세요.
        } finally {
            System.out.print("F");
        }
        System.out.println("D");
    }
}
'''
s6_solution = s6.replace('        // 이 주석 아래에 IllegalArgumentException을 받아 C를 출력하는 catch를 쓰세요.\n',
                         '        // 이 주석 아래에 IllegalArgumentException을 받아 C를 출력하는 catch를 쓰세요.\n'
                         '        // 예외가 나면 B를 건너뛰고 이 catch로 와요. 받은 뒤에는 finally, 그다음 D로 이어져요.\n'
                         '        } catch (IllegalArgumentException error) {\n'
                         '            System.out.print("C");\n')
n6 = (Script(s6)
      .say('재고가 0이면 예외가 나요. 이 예외를 받아 C를 출력하는 catch를 써야 해요.', 'text:주석 아래에 IllegalArgumentException을 받아 C를 출력하는 catch를 쓰세요.')
      .run('print("A")', 'println("D")', error='IllegalArgumentException')
      .say('AF 뒤에 IllegalArgumentException 오류가 나요. 받는 catch가 없어서 finally만 실행되고 D는 출력되지 않았어요.', 'output')
      .patch('        // 이 주석 아래에 IllegalArgumentException을 받아 C를 출력하는 catch를 쓰세요.\n',
             '        // 이 주석 아래에 IllegalArgumentException을 받아 C를 출력하는 catch를 쓰세요.\n'
             '        } catch (IllegalArgumentException error) {\n            System.out.print("C");\n',
             'try 블록을 닫고 IllegalArgumentException을 받는 catch에서 C를 출력해요.')
      .run('print("A")', 'println("D")')
      .say('ACFD예요. 예외 뒤의 B는 건너뛰고, catch의 C, finally의 F, 그다음 D가 나왔어요.', 'output')
      .say('조심하세요. 예외가 난 줄 아래의 try 안 코드는 catch 뒤에 다시 실행되지 않아요.', 'code:System.out.print("B");'))

# ---- 7. finally 뒤에서 반환하기 -------------------------------------------------------
s7 = '''class Rule {
    static int choose(int bonus) {
        int value = 2;
        // 반환을 finally 뒤로 옮겨 finally에서 바꾼 값을 반환하세요.
        try { return value; }
        finally {
            value += bonus;
            System.out.print("F");
        }
    }
}

public class Main {
    public static void main(String[] args) {
        int bonus = 7;
        System.out.println(Rule.choose(bonus));
    }
}
'''
s7_solution = s7.replace('        try { return value; }\n        finally {\n            value += bonus;\n            System.out.print("F");\n        }\n',
                         '        // try 안의 return은 finally 전에 반환값을 정해 둬요. 바뀐 값을 돌려주려면 finally 뒤에서 반환해요.\n'
                         '        try { System.out.print(""); }\n        finally {\n            value += bonus;\n            System.out.print("F");\n        }\n        return value;\n')
n7 = (Script(s7)
      .say('try 안에서 value를 반환하고 finally에서 value를 바꿔요. 반환을 finally 뒤로 옮겨야 해요.', 'text:try 안의 return을 finally 뒤로 옮겨 finally에서 바꾼 value를 반환하세요.')
      .run('println(Rule.choose(bonus))')
      .say('F2예요. finally가 F를 출력했지만 반환값은 finally 전에 정한 2예요.', 'output')
      .patch('        try { return value; }\n', '        try { System.out.print(""); }\n', 'try 안의 return을 지워요.')
      .patch('            System.out.print("F");\n        }\n', '            System.out.print("F");\n        }\n        return value;\n', 'finally 블록 뒤에 return value를 써요.')
      .run('println(Rule.choose(bonus))')
      .say('F9예요. finally에서 7을 더한 뒤 value를 반환했어요.', 'output')
      .say('조심하세요. finally 안에서 변수를 바꿔도 try에서 이미 정한 반환값은 바뀌지 않아요.', 'code:value += bonus;'))

SPECS = [
    dict(old='stp_af249ad3-6a04-4487-a2c5-10d94ef1dbdc', title='Bonus에 value()를 재정의해 실제 객체의 메서드가 불리게 하세요',
         objectives=['참조형과 실제 객체형에 따른 오버라이딩 호출을 읽어요.'],
         core_flow='Rule rule=new Bonus()에서 Bonus에 value()가 없어 2가 나온다. Bonus에 value()를 재정의해 extra를 반환하면 7이다. 코드 흐름 보기에서 Bonus.value()로 들어간다. 채점은 extra를 바꿔 실행한다.',
         goal='rule 변수의 선언형은 Rule이고 실제로 만든 객체는 Bonus예요. 하위 클래스가 같은 이름·같은 매개변수의 메서드를 다시 쓰면(재정의) 실행할 때 실제 객체의 메서드가 불려요.\n\n'
              '주석 아래에 value()를 재정의해 extra를 반환하는 메서드를 쓰세요. 채점은 extra의 값을 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 2가 나오는지 확인하세요.', '주석 아래에 extra를 반환하는 `int value()`를 쓰세요.', '코드 실행을 눌러 7이 나오는지 확인하세요.',
                     '코드 흐름 보기를 눌러 rule.value()가 어느 클래스의 value()로 들어가는지 보세요.', '작성한 코드를 제출하세요.'),
         starter_code=s1, solution=s1_solution, tests=[{'input': '', 'expected': '7'}],
         variations=[{'values': {'extra': '9'}, 'expected': '9'}, {'values': {'extra': '0'}, 'expected': '0'}],
         code_flow=True, narration=n1.actions,
         review={'7이에요. 변수는 Rule형이어도 실제 객체 Bonus의 value()가 불렸어요.': '「이어도」 대조가 실제 실행(선언형 Rule, 출력 7)과 맞아요.', '조심하세요. return 7처럼 숫자를 적으면 지금은 같아도 extra가 바뀌면 틀려요.': '실제 우회(숫자 반환)와 그 결과(값 바꾼 채점 실패)를 말해요.'},
         reject=[([['    @Override int value() { return extra; }\n', '    @Override int value() { return 7; }\n']], 'Returning a typed number'),
                 ([['        System.out.println(rule.value());\n', '        System.out.println(7);\n']], 'Printing a typed value')],
         accept=[([['    @Override int value() { return extra; }\n', '    int value() {\n        return this.extra;\n    }\n']], 'Override without the annotation')]),
    dict(old='stp_32d717ac-d05b-4e45-b6af-6de8a5d5e73c', title='rule을 Bonus로 바꿔 읽어 Bonus의 count를 출력하세요',
         objectives=['숨겨진 필드와 오버라이딩 메서드의 선택을 구별해요.'],
         core_flow='Rule.count=2, Bonus.count=given(7)이 같은 이름으로 있고 rule.count+":"+rule.value()는 2:7이다. ((Bonus) rule).count를 출력하는 줄을 더해 7을 확인한다. 코드 흐름 보기에서 Bonus 객체 안 count 두 칸을 본다. 채점은 given을 바꿔 실행한다.',
         goal='Bonus는 Rule과 같은 이름의 필드 count를 따로 가져요. 필드는 재정의되지 않아서 변수의 선언형으로 골라져요. 메서드 value()는 재정의라 실제 객체로 골라져요.\n\n'
              'rule.count와 rule.value()가 각각 무엇을 읽는지 실행해 비교하세요. 그다음 주석 아래에 rule을 `(Bonus)`로 바꿔 읽어 Bonus의 count를 출력하는 줄을 쓰세요. 채점은 given의 값을 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 2:7이 나오는지 확인하세요.', '주석 아래에 `((Bonus) rule).count`를 출력하는 줄을 쓰세요.', '코드 실행을 눌러 둘째 줄에 7이 나오는지 확인하세요.',
                     '코드 흐름 보기를 눌러 Bonus 객체 안의 두 count 칸을 보세요.', '작성한 코드를 제출하세요.'),
         starter_code=s2, solution=s2_solution, tests=[{'input': '', 'expected': '2:7\n7'}],
         variations=[{'values': {'given': '9'}, 'expected': '2:9\n9'}, {'values': {'given': '2'}, 'expected': '2:2\n2'}],
         code_flow=True, narration=n2.actions,
         review={'둘째 줄은 7이에요. 같은 객체라도 Bonus형으로 읽으면 Bonus의 count가 골라져요.': '「라도」 대조가 실제 실행(같은 객체, 선언형만 바꿈)과 맞아요.', '조심하세요. 필드는 재정의되지 않아요. rule.count는 실제 객체가 Bonus여도 Rule의 count예요.': '실제 오개념(필드도 실제 객체로 고른다)과 이 스텝의 첫 줄 2로 확인되는 사실을 말해요.'},
         reject=[([['        System.out.println(((Bonus) rule).count);\n', '        System.out.println(rule.count);\n']], 'Reading through the Rule type'),
                 ([['        System.out.println(((Bonus) rule).count);\n', '        System.out.println(7);\n']], 'Printing a typed value')],
         accept=[([['        System.out.println(((Bonus) rule).count);\n', '        Bonus bonus = (Bonus) rule;\n        System.out.println(bonus.count);\n']], 'Casting into a Bonus variable first')]),
    dict(old='stp_dcf0ddf2-a6e2-4377-92b5-c5ada59baf21', title='Bonus 클래스 이름으로 static name()을 불러 출력하세요',
         objectives=['정적 숨김과 인스턴스 오버라이딩을 구별해요.'],
         core_flow='Rule.name()과 Bonus.name()은 static이다. Rule rule=new Bonus(); rule.name()은 선언형 Rule로 골라 P다. Bonus.name()을 부르는 줄을 더해 C를 확인한다. 코드 흐름 보기에서 두 호출이 각각 Rule.name(), Bonus.name()으로 들어간다. 채점은 mark를 바꿔 실행한다.',
         goal='static 메서드는 객체가 아니라 클래스에 속해요. 하위 클래스가 같은 static 메서드를 쓰면 재정의가 아니라 가리는 것이라서, 변수로 부르면 실제 객체가 아니라 선언형으로 골라져요.\n\n'
              '주석 아래에 Bonus 클래스 이름으로 name()을 불러 출력하는 줄을 쓰세요. 채점은 mark의 값을 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 P가 나오는지 확인하세요.', '주석 아래에 `Bonus.name()`을 출력하는 줄을 쓰세요.', '코드 실행을 눌러 P 다음 줄에 C가 나오는지 확인하세요.',
                     '코드 흐름 보기를 눌러 두 호출이 각각 어느 클래스의 name()으로 들어가는지 보세요.', '작성한 코드를 제출하세요.'),
         starter_code=s3, solution=s3_solution, tests=[{'input': '', 'expected': 'P\nC'}],
         variations=[{'values': {'mark': '"K"'}, 'expected': 'P\nK'}, {'values': {'code': '"Q"'}, 'expected': 'Q\nC'}],
         code_flow=True, narration=n3.actions,
         review={'조심하세요. static 메서드는 재정의되지 않고 가려질 뿐이라 @Override를 붙이면 컴파일 오류예요.': '실제 javac 동작(static에 @Override는 오류)과 숨김 개념을 정확히 말해요.'},
         reject=[([['        System.out.println(Bonus.name());\n', '        System.out.println(rule.name());\n']], 'Calling through the Rule variable again'),
                 ([['        System.out.println(Bonus.name());\n', '        System.out.println("C");\n']], 'Printing typed text')],
         accept=[([['        System.out.println(Bonus.name());\n', '        Bonus bonus = new Bonus();\n        System.out.println(bonus.name());\n']], 'A Bonus-typed variable picks Bonus.name() too')]),
    dict(old='stp_054d2905-9281-4fef-87eb-fdeb9f3fa412', title='text의 선언형을 String으로 바꿔 show(String)이 골라지게 하세요',
         objectives=['오버로드 선택과 실행 시 오버라이딩을 구별해요.'],
         core_flow='show(Object)는 O, show(String)은 S+길이를 반환한다. Object text="ticket"이면 O다. 선언형을 String으로 바꿔 S6을 확인한다. 채점은 text의 문자열을 바꿔 실행한다.',
         goal='이름이 같고 매개변수형이 다른 메서드(오버로드) 중 무엇을 부를지는 컴파일할 때 인수의 선언형으로 정해져요. 지금 text의 선언형은 Object라 실제 값이 문자열이어도 show(Object)가 골라져요.\n\n'
              'text의 선언형을 고쳐 String을 받는 show가 골라지게 하세요. 채점은 text에 넣는 문자열을 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 O가 나오는지 확인하세요.', '`Object text`의 선언형을 String으로 바꾸세요.', '코드 실행을 눌러 S6이 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s4, solution=s4_solution, tests=[{'input': '', 'expected': 'S6'}],
         variations=[{'values': {'text': '"bus"'}, 'expected': 'S3'}, {'values': {'text': '""'}, 'expected': 'S0'}],
         narration=n4.actions,
         review={'조심하세요. 오버로드는 실행 중에 다시 고르지 않아요. 재정의와 달리 선언형이 정해요.': '실제 Java 규칙(오버로드는 컴파일 시 선택)과 재정의와의 대조를 말해요.'},
         reject=[([['        String text = "ticket";\n', '        Object text = "ticket";\n']], 'Keeping the Object type'),
                 ([['        System.out.println(View.show(text));\n', '        System.out.println("S6");\n']], 'Printing typed text')],
         accept=[([['        String text = "ticket";\n', '        var text = "ticket";\n']], 'var infers String')]),
    dict(old='stp_932d8712-b8d0-4ceb-9b2d-a060b36aebe4', title='다 만들어진 rule의 show()를 한 번 더 불러 생성 중 값과 비교하세요',
         objectives=['생성 도중의 오버라이딩과 기본값을 연결해요.'],
         core_flow='Rule() 생성자가 show()를 부르고 Bonus가 show()를 재정의해 value를 출력한다. 생성 중에는 value 초기화 전이라 0이다. 생성 뒤 rule.show()를 더해 07을 확인한다. 코드 흐름 보기에서 Rule() 안의 호출이 Bonus.show()로 들어가고 value가 0이다. 채점은 value를 바꿔 실행한다.',
         goal='new Bonus()를 하면 먼저 상위 생성자 Rule()이 실행되고, 그다음 Bonus의 필드 초기화 `value = 7`이 실행돼요. Rule()이 부르는 show()는 재정의된 Bonus의 show()예요.\n\n'
              '주석 아래에서 다 만들어진 rule의 show()를 한 번 더 부르는 줄을 쓰세요. 생성 중 출력과 생성 뒤 출력이 이어서 한 줄에 나와요. 채점은 value의 값을 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 0이 나오는지 확인하세요.', '주석 아래에 `rule.show();`를 쓰세요.', '코드 실행을 눌러 07이 나오는지 확인하세요.',
                     '코드 흐름 보기를 눌러 Rule() 안에서 불린 show()가 value를 몇으로 읽는지 보세요.', '작성한 코드를 제출하세요.'),
         starter_code=s5, solution=s5_solution, tests=[{'input': '', 'expected': '07'}],
         variations=[{'values': {'value': '9'}, 'expected': '09'}, {'values': {'value': '3'}, 'expected': '03'}],
         code_flow=True, narration=n5.actions,
         review={'조심하세요. 필드 초기화 value = 7은 상위 생성자 Rule()이 끝난 뒤에 실행돼요.': '실제 Java 객체 초기화 순서를 정확히 말해요.'},
         reject=[([['        rule.show();\n', '        System.out.print(7);\n']], 'Printing a typed value'),
                 ([['        rule.show();\n', '        new Bonus();\n']], 'Creating another object prints 0 again')],
         accept=[([['        rule.show();\n', '        System.out.print(rule.value);\n']], 'Reading the field after construction')]),
    dict(old='stp_96c42520-57e4-4d77-a0d1-2ba45975c03d', title='예외를 받는 catch를 써 ACFD가 나오게 하세요',
         objectives=['예외 뒤 건너뛴 줄과 catch 뒤 흐름을 구별해요.'],
         core_flow='stock==0이면 IllegalArgumentException이 나고 catch가 없어 AF 뒤 프로그램이 오류로 멈춘다. catch(IllegalArgumentException)에서 C를 출력해 ACFD를 확인한다. B는 건너뛴다. 채점은 stock을 바꿔 예외가 없는 ABFD도 확인한다.',
         goal='try 안에서 예외가 나면 그 아래 줄은 건너뛰고, 그 예외를 받는 catch로 가요. finally는 예외가 있든 없든 실행돼요. 지금은 받는 catch가 없어서 finally만 실행되고 프로그램이 오류로 멈춰요.\n\n'
              '주석 아래에 IllegalArgumentException을 받아 C를 출력하는 catch를 쓰세요. try 블록을 닫는 `}` 뒤에 이어서 써요. 채점은 stock을 바꿔 예외가 나지 않는 경우도 실행해요.\n\n'
              + todo('코드 실행을 눌러 AF 뒤 IllegalArgumentException 오류가 나는지 확인하세요.', '주석 아래에 `} catch (IllegalArgumentException error) {`와 C를 출력하는 줄을 쓰세요.',
                     '코드 실행을 눌러 ACFD가 나오는지 확인하세요.', '작성한 코드를 제출하세요.'),
         starter_code=s6, solution=s6_solution, tests=[{'input': '', 'expected': 'ACFD'}],
         variations=[{'values': {'stock': '3'}, 'expected': 'ABFD'}],
         narration=n6.actions,
         review={'조심하세요. 예외가 난 줄 아래의 try 안 코드는 catch 뒤에 다시 실행되지 않아요.': '실제 Java 예외 흐름(B 건너뜀)을 정확히 말해요.'},
         reject=[([['        } catch (IllegalArgumentException error) {\n', '        } catch (ArithmeticException error) {\n']], 'Catching an exception that is not thrown'),
                 ([['            if (stock == 0) throw new IllegalArgumentException("bad");\n', '            if (stock == 0) System.out.print("C");\n']], 'Removing the exception')],
         accept=[([['        } catch (IllegalArgumentException error) {\n', '        } catch (RuntimeException error) {\n']], 'Catching a parent exception type')]),
    dict(old='stp_25d18823-5a88-4ce2-8eb8-4008c5c5fef5', title='반환을 finally 뒤로 옮겨 바뀐 값을 반환하세요',
         objectives=['반환식 값 결정과 finally 부작용의 순서를 구별해요.'],
         core_flow='try { return value; } finally { value += bonus; F }는 F2다. 반환값은 finally 전에 정해진다. return을 finally 뒤로 옮겨 F9를 확인한다. 채점은 bonus를 바꿔 실행한다.',
         goal='try 안의 `return value;`는 finally를 실행하기 전에 반환할 값을 정해 둬요. 그래서 finally에서 value를 바꿔도 반환값은 그대로예요.\n\n'
              'try 안의 return을 finally 뒤로 옮겨 finally에서 바꾼 value를 반환하세요. try 블록은 비지 않게 `System.out.print("");`를 남겨 둬요. 채점은 bonus의 값을 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 F2가 나오는지 확인하세요.', '`try { return value; }`를 `try { System.out.print(\"\"); }`로 바꾸세요.', 'finally 블록이 끝난 뒤에 `return value;`를 쓰세요.',
                     '코드 실행을 눌러 F9가 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s7, solution=s7_solution, tests=[{'input': '', 'expected': 'F9'}],
         variations=[{'values': {'bonus': '3'}, 'expected': 'F5'}, {'values': {'bonus': '0'}, 'expected': 'F2'}],
         narration=n7.actions,
         review={'조심하세요. finally 안에서 변수를 바꿔도 try에서 이미 정한 반환값은 바뀌지 않아요.': '실제 Java 규칙(반환값은 finally 전에 정해짐)을 정확히 말해요.'},
         reject=[([['        return value;\n    }\n}\n', '        return 9;\n    }\n}\n']], 'Returning a typed number'),
                 ([['        try { System.out.print(""); }\n', '        try { return value; }\n'], ['        return value;\n    }\n}\n', '    }\n}\n']], 'Keeping the early return')],
         accept=[([['        try { System.out.print(""); }\n        finally {\n            value += bonus;\n            System.out.print("F");\n        }\n        return value;\n',
                    '        value += bonus;\n        System.out.print("F");\n        return value;\n']], 'Without try and finally')]),
]
