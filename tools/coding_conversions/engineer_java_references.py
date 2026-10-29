"""engineer-java-references: 7 answer-picking steps -> coding steps (2026-10-29)."""
from _kit import Script, todo

PRD_SCOPE = ['두 챕터·두 단원·여덟 스텝으로 창고 자료의 공유를 읽어요.',
             '참조 공유를 실행으로 확인한 뒤 복사·필드 수정·재대입·비교·null 확인 코드를 직접 고쳐요. 마지막 결과 읽기만 짧게 직접 적어요.']
PRD_GRADING = ['직접 고친 코드를 실제 JDK 25로 실행해 판정해요. 준비 값(배열 내용·새 값·글)을 바꾼 실행도 맞아야 해요.',
               '고정 출력, 복사본 대신 같은 값을 다시 쓴 배열, 다른 객체를 바꾼 답은 거절해요.',
               '마지막 결과 읽기(stp_1615d484-b23a-4557-ada9-fcf5da81a21c)는 짧은 답안을 판정해요.',
               '마지막 도전(stp_386c6124-e3ed-4cab-8223-61ef33179153): 시작 답안은 실패해야 해요. 실제 실행 결과 또는 각 서술형 답안 칸을 검사하고 오답과 동등한 정답도 대조해요.']
PRD_NARRATION = ['먼저 준비 코드를 실행해 공유나 재대입의 실제 결과를 읽어요. 한 줄을 고친 뒤 다시 실행해 차이를 짚어요.',
                 '참조 화살표가 도움이 되는 스텝은 코드 흐름 보기로 같은 대상과 다른 대상을 확인하게 해요.',
                 '전체 답을 한 번에 갈아 끼우지 않아요. 음성은 준비한 뒤 화면과 맞춰요.']

STOCK = '''class Stock {
    int count;
    // 각 객체의 재고 값을 따로 준비해요.
    Stock(int count) { this.count = count; }
}
'''

# ---- 1. 같은 배열 → 복사본 --------------------------------------------------------------
s1 = '''public class Main {
    public static void main(String[] args) {
        int[] a = {2, 3};
        // 이 줄을 고쳐 b가 a의 복사본을 갖게 하세요.
        int[] b = a;
        b[0] = 7;
        System.out.println(a[0]);
        System.out.println(b[0] + " " + b[1]);
    }
}
'''
s1_solution = s1.replace('        int[] b = a;\n', '        // clone()은 같은 내용의 새 배열을 만들어요. 이제 b를 바꿔도 a는 그대로예요.\n        int[] b = a.clone();\n')
n1 = (Script(s1)
      .say('재고 배열 a를 b에 대입했어요. b의 첫 칸만 7로 바꿔야 해요.', 'text:b를 만드는 줄 한 곳을 고쳐 b가 a의 복사본을 갖게 하세요.')
      .run('println(a[0])', 'println(b[0] + " " + b[1])')
      .say('a[0]도 7이에요. b = a는 배열 자체가 아니라 그 배열의 참조값만 복사했거든요.', 'output')
      .say('코드 흐름 보기에서는 a와 b의 화살표가 배열 하나로 모여요.', 'text:코드 흐름 보기를 눌러 a와 b의 화살표가 같은 배열을 가리키는지 보세요.')
      .patch('        int[] b = a;\n', '        int[] b = a.clone();\n', 'a.clone()으로 같은 내용의 새 배열을 만들어 b에 담아요.')
      .run('println(a[0])', 'println(b[0] + " " + b[1])')
      .say('a는 처음 값 2 그대로이고 b는 7과 3이에요. b가 a의 내용을 담은 다른 배열이에요.', 'output')
      .say('조심하세요. {2, 3}을 b에 직접 적으면 지금은 같아 보여요. 하지만 a가 다른 값이면 복사본이 아니라서 틀려요.', 'code:a.clone()'))

# ---- 2. 중첩 배열의 안쪽 ---------------------------------------------------------------
s2 = '''public class Main {
    public static void main(String[] args) {
        int[][] a = {{2, 4}, {3}};
        // 바깥 배열만 새로 만들어요. 안쪽 배열은 아직 a와 함께 써요.
        int[][] b = a.clone();
        // 이 주석 아래 줄에 b의 첫 안쪽 배열을 따로 복사하세요.
        b[0][0] = 7;
        System.out.println(a[0][0]);
        System.out.println(b[0][0] + " " + b[0][1]);
    }
}
'''
s2_solution = s2.replace('        // 이 주석 아래 줄에 b의 첫 안쪽 배열을 따로 복사하세요.\n',
                         '        // 이 주석 아래 줄에 b의 첫 안쪽 배열을 따로 복사하세요.\n        // 안쪽 배열도 clone()해야 b[0]이 a[0]과 다른 배열을 가리켜요.\n        b[0] = a[0].clone();\n')
n2 = (Script(s2)
      .say('바깥 배열은 clone()으로 새로 만들었어요. 그래도 b[0][0]을 바꾸면 a가 바뀌는지 봐요.', 'text:바깥 배열은 새로 만들었지만')
      .run('println(a[0][0])', 'println(b[0][0] + " " + b[0][1])')
      .say('a[0][0]도 7이에요. 새 바깥 배열 칸에 같은 안쪽 배열의 참조값이 복사됐거든요.', 'output')
      .say('코드 흐름 보기에서 바깥 배열은 둘이지만 첫 칸의 화살표는 같은 안쪽 배열로 가요.', 'text:코드 흐름 보기를 눌러 a와 b의 첫 칸이 어느 안쪽 배열을 가리키는지 보세요.')
      .patch('        // 이 주석 아래 줄에 b의 첫 안쪽 배열을 따로 복사하세요.\n',
             '        // 이 주석 아래 줄에 b의 첫 안쪽 배열을 따로 복사하세요.\n        b[0] = a[0].clone();\n',
             'b[0]에 a[0]의 복사본을 담아요. 이 줄은 b[0][0] = 7보다 먼저 와야 해요.')
      .run('println(a[0][0])', 'println(b[0][0] + " " + b[0][1])')
      .say('a는 2, b는 7과 4예요. 첫 안쪽 배열도 내용을 복사한 별도 배열이에요.', 'output')
      .say('조심하세요. 복사 줄을 b[0][0] = 7 아래에 두면 이미 a까지 바뀐 뒤라 2를 되찾지 못해요.', 'code:b[0] = a[0].clone();'))

# ---- 3. 받은 객체의 필드를 바꿔요 ------------------------------------------------------
s3 = STOCK + '''class Changes {
    static void change(Stock value, int next) {
        // 이 줄을 고쳐 전달받은 객체의 count를 next로 바꾸세요.
        value = new Stock(next);
    }
}

public class Main {
    public static void main(String[] args) {
        int next = 7;
        Stock a = new Stock(2);
        Changes.change(a, next);
        System.out.println(a.count);
    }
}
'''
s3_solution = s3.replace('        value = new Stock(next);\n',
                         '        // value에는 a와 같은 객체의 참조값이 복사돼 있어요. 그 객체의 필드를 바꿔요.\n        value.count = next;\n')
n3 = (Script(s3)
      .say('change가 a가 가리키는 재고를 next로 바꿔야 해요. 지금은 새 객체를 만들어요.', 'text:change 메서드의 한 줄을 고쳐 a가 가리키는 재고의 count를 next로 바꾸세요.')
      .run('println(a.count)')
      .say('2가 나와요. value에 새 객체를 연결해도 호출한 쪽의 a는 그대로예요.', 'output')
      .say('코드 흐름 보기에서 change가 시작될 때 value와 a는 같은 Stock을 가리켜요.', 'text:코드 흐름 보기를 눌러 change 안의 value와 main의 a가 처음에 같은 Stock을 가리키는지 보세요.')
      .patch('        value = new Stock(next);\n', '        value.count = next;\n', 'value가 가리키는 객체의 count에 next를 넣어요.')
      .run('println(a.count)')
      .say('7이 나와요. value와 a가 같은 객체를 가리키니 a.count도 7이에요.', 'output')
      .say('조심하세요. value.count = 7로 숫자를 적으면 next가 바뀐 채점에서 틀려요.', 'code:value.count = next;'))

# ---- 4. 돌려받은 새 객체를 다시 담아요 -------------------------------------------------
s4 = STOCK + '''class Changes {
    static Stock replace(Stock value, int fresh) {
        // 인수 이름만 새 객체로 연결하고 그 참조값을 반환해요.
        value = new Stock(fresh);
        return value;
    }
}

public class Main {
    public static void main(String[] args) {
        int fresh = 9;
        Stock a = new Stock(2);
        // 이 줄을 고쳐 돌려받은 새 객체를 a에 담으세요.
        Changes.replace(a, fresh);
        System.out.println(a.count);
    }
}
'''
s4_solution = s4.replace('        Changes.replace(a, fresh);\n',
                         '        // 반환된 새 객체의 참조값을 a에 대입해야 a가 그 객체를 가리켜요.\n        a = Changes.replace(a, fresh);\n')
n4 = (Script(s4)
      .say('replace는 새 재고 객체를 만들어 돌려줘요. a가 그 새 객체를 가리키게 해야 해요.', 'text:main의 호출 줄을 고쳐 replace가 돌려준 새 객체를 a에 담으세요.')
      .run('println(a.count)')
      .say('2가 나와요. replace 안의 value만 새 객체로 옮겨 갔고 a는 그대로예요.', 'output')
      .say('코드 흐름 보기에서 replace가 반환한 뒤에도 a의 화살표는 처음 Stock에 남아 있어요.', 'text:코드 흐름 보기를 눌러 replace가 끝난 뒤 a가 어느 Stock을 가리키는지 보세요.')
      .patch('        Changes.replace(a, fresh);\n', '        a = Changes.replace(a, fresh);\n', '돌려받은 참조값을 a에 대입해요.')
      .run('println(a.count)')
      .say('9가 나와요. 이제 a가 replace가 만든 새 객체를 가리켜요.', 'output')
      .say('조심하세요. a.count = 9로 고치면 출력은 같아도 처음 객체를 바꾼 거예요. fresh가 바뀌면 틀려요.', 'code:a = Changes.replace(a, fresh);'))

# ---- 5. 문자열은 새 값을 만들어요 ------------------------------------------------------
s5 = '''public class Main {
    public static void main(String[] args) {
        String a = "go";
        String b = a;
        // 새 글을 b에만 연결해요.
        b = b + "!";
        // 이 주석 아래 줄에 a에도 느낌표를 붙인 새 글을 담으세요.
        System.out.println(a + ":" + b);
    }
}
'''
s5_solution = s5.replace('        // 이 주석 아래 줄에 a에도 느낌표를 붙인 새 글을 담으세요.\n',
                         '        // 이 주석 아래 줄에 a에도 느낌표를 붙인 새 글을 담으세요.\n        // String은 바뀌지 않아요. a + "!"로 만든 새 글을 a에 다시 대입해요.\n        a = a + "!";\n')
n5 = (Script(s5)
      .say('b에 느낌표를 붙였어요. 이번에는 a에도 느낌표가 붙은 글이 담겨야 해요.', 'text:주석 아래 줄에 a에도 느낌표를 붙인 새 글을 담으세요.')
      .run('println(a + ":" + b)')
      .say('go:go!가 나와요. b + "!"는 원래 글을 고치지 않고 새 글을 만들어 b에만 담았어요.', 'output')
      .patch('        // 이 주석 아래 줄에 a에도 느낌표를 붙인 새 글을 담으세요.\n',
             '        // 이 주석 아래 줄에 a에도 느낌표를 붙인 새 글을 담으세요.\n        a = a + "!";\n',
             'a + "!"로 새 글을 만들어 a에 다시 대입해요.')
      .run('println(a + ":" + b)')
      .say('go!:go!예요. a도 새 글을 가리키게 됐어요.', 'output')
      .say('조심하세요. a + "!"만 쓰고 a에 대입하지 않으면 새 글은 버려지고 a는 그대로예요.', 'code:a = a + "!";'))

# ---- 6. 내용과 같은 대상 -------------------------------------------------------------
s6 = '''public class Main {
    public static void main(String[] args) {
        String a = new String("go");
        String b = new String("go");
        // 같은 대상인지 비교해요.
        System.out.println(a == b);
        // 이 주석 아래 줄에 두 글의 내용이 같은지 출력하세요.
    }
}
'''
s6_solution = s6.replace('        // 이 주석 아래 줄에 두 글의 내용이 같은지 출력하세요.\n',
                         '        // 이 주석 아래 줄에 두 글의 내용이 같은지 출력하세요.\n        // equals는 글자 내용을 비교해요. ==는 같은 객체인지를 봐요.\n        System.out.println(a.equals(b));\n')
n6 = (Script(s6)
      .say('같은 글 go로 객체를 두 개 만들었어요. 내용이 같은지도 출력해야 해요.', 'text:주석 아래 줄에 두 글의 내용이 같은지 출력하세요.')
      .run('println(a == b)')
      .say('false가 나와요. ==는 두 변수가 같은 객체인지 비교하는데 new로 따로 만들었거든요.', 'output')
      .patch('        // 이 주석 아래 줄에 두 글의 내용이 같은지 출력하세요.\n',
             '        // 이 주석 아래 줄에 두 글의 내용이 같은지 출력하세요.\n        System.out.println(a.equals(b));\n',
             'a.equals(b)로 글자 내용을 비교해 출력해요.')
      .run('println(a == b)', 'println(a.equals(b))')
      .say('false 다음에 true예요. 다른 객체지만 내용은 같아요.', 'output')
      .say('조심하세요. 글이 같은지 물을 때 ==를 쓰면 다른 객체라서 false가 나올 수 있어요.', 'code:a.equals(b)'))

# ---- 7. 없는 대상을 먼저 확인해요 ------------------------------------------------------
s7 = '''public class Main {
    public static void main(String[] args) {
        String text = null;
        try {
            // 이 조건을 고쳐 text가 null이면 길이를 묻지 않게 하세요.
            System.out.println(text != null & text.length() > 0);
        } catch (NullPointerException error) {
            System.out.println("missing");
        }
    }
}
'''
s7_solution = s7.replace('            System.out.println(text != null & text.length() > 0);\n',
                         '            // &&는 왼쪽이 false면 오른쪽을 실행하지 않아요. null이면 length()를 부르지 않아요.\n            System.out.println(text != null && text.length() > 0);\n')
n7 = (Script(s7)
      .say('text가 아직 null이에요. null이면 길이를 묻지 말고 false가 나와야 해요.', 'text:조건의 연산자 한 곳을 고쳐 text가 null이면 길이를 묻지 않고 false가 나오게 하세요.')
      .run('println(text != null & text.length() > 0)', 'println("missing")')
      .say('missing이 나와요. &는 왼쪽이 false여도 오른쪽 text.length()까지 실행해서 예외가 났어요.', 'output')
      .patch('text != null & text.length() > 0', 'text != null && text.length() > 0', '&를 &&로 바꿔요.')
      .run('println(text != null && text.length() > 0)', 'println("missing")')
      .say('false가 나와요. 왼쪽이 false라서 &&가 오른쪽을 건너뛰었어요.', 'output')
      .say('조심하세요. 두 조건의 순서를 바꿔 text.length()를 앞에 두면 &&여도 먼저 예외가 나요.', 'code:text != null && text.length() > 0'))

SPECS = [
    dict(old='stp_68769bbd-f702-41a1-a19b-5880bd011556', title='b를 a와 따로 쓰는 배열로 만드세요',
         objectives=['참조값 복사와 배열 복사를 구별해 배열을 따로 복사해요.'],
         core_flow='재고 배열 a={2,3}을 b=a로 대입한 준비 코드를 실행하면 b[0]=7 뒤 a[0]도 7이다. 코드 흐름 보기에서 두 화살표가 같은 배열을 가리킨다. b=a.clone()으로 한 곳을 고쳐 원본 2가 유지되는 것을 확인한다. 채점은 a의 처음 값을 바꿔 복사본인지 확인한다.',
         goal='재고 배열 a를 b에 대입했어요. 지금은 b[0]을 7로 바꾸면 a[0]도 7이 돼요. 배열 변수에는 배열 자체가 아니라 배열을 가리키는 참조값이 들어 있어서, `b = a`는 같은 배열을 함께 가리키게 해요.\n\n'
              'b를 만드는 줄 한 곳을 고쳐 b가 a의 복사본을 갖게 하세요. `a.clone()`은 같은 내용의 새 배열을 만들어요. 채점은 a의 처음 값을 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 a[0]과 b[0]이 모두 7로 나오는지 확인하세요.', '코드 흐름 보기를 눌러 a와 b의 화살표가 같은 배열을 가리키는지 보세요.',
                     '`int[] b = a;`를 a의 복사본을 담는 줄로 고치세요.', '코드 실행을 눌러 a는 처음 값 2, b는 7과 3으로 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s1, solution=s1_solution, tests=[{'input': '', 'expected': '2\n7 3'}],
         variations=[{'values': {'a': '{5, 9}'}, 'expected': '5\n7 9'}, {'values': {'a': '{0, 8, 1}'}, 'expected': '0\n7 8'}],
         code_flow=True, narration=n1.actions,
         review={'조심하세요. {2, 3}을 b에 직접 적으면 지금은 같아 보여요. 하지만 a가 다른 값이면 복사본이 아니라서 틀려요.':
                 '실제 흔한 우회: 같은 값을 다시 적은 배열은 a와 무관해요. 채점의 a 변경에서 드러나는 결과를 말해요.'},
         reject=[([['        int[] b = a.clone();\n', '        int[] b = {2, 3};\n']], 'Writing the same values instead of copying a'),
                 ([['        int[] b = a.clone();\n', '        int[] b = a;\n']], 'Still sharing the array'),
                 ([['        System.out.println(a[0]);\n', '        System.out.println(2);\n']], 'Printing a typed value')],
         accept=[([['        int[] b = a.clone();\n', '        int[] b = java.util.Arrays.copyOf(a, a.length);\n']], 'Arrays.copyOf is also a copy')]),
    dict(old='stp_21399b21-7735-4294-bb08-9699cf3dc676', title='안쪽 배열까지 복사해 원본을 지키세요',
         objectives=['바깥 배열 복사 뒤 안쪽 배열까지 따로 복사해요.'],
         core_flow='int[][] a={{2,4},{3}}를 clone한 준비 코드에서 b[0][0]=7이면 a[0][0]도 7이다. 코드 흐름 보기에서 바깥 배열은 둘이지만 첫 칸이 같은 안쪽 배열을 가리킨다. b[0]=a[0].clone()을 변경 전에 넣어 원본 2를 지킨다. 채점은 a의 안쪽 값을 바꿔 실행한다.',
         goal='바깥 배열은 새로 만들었지만 그 칸에는 안쪽 배열의 참조값이 그대로 복사돼요. 그래서 지금은 b[0][0]을 7로 바꾸면 a[0][0]도 7이 돼요.\n\n'
              '주석 아래 줄에 b의 첫 안쪽 배열을 a[0]의 복사본으로 바꾸는 줄을 쓰세요. 채점은 a의 안쪽 값을 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 a[0][0]과 b[0][0]이 모두 7로 나오는지 확인하세요.', '코드 흐름 보기를 눌러 a와 b의 첫 칸이 어느 안쪽 배열을 가리키는지 보세요.',
                     '주석 아래 줄에 `b[0]`에 a의 첫 안쪽 배열 복사본을 담는 줄을 쓰세요.', '코드 실행을 눌러 a는 2, b는 7과 4로 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s2, solution=s2_solution, tests=[{'input': '', 'expected': '2\n7 4'}],
         variations=[{'values': {'a': '{{5, 6}, {3}}'}, 'expected': '5\n7 6'}, {'values': {'a': '{{1, 8, 2}, {6}}'}, 'expected': '1\n7 8'}],
         code_flow=True, narration=n2.actions,
         review={'조심하세요. 복사 줄을 b[0][0] = 7 아래에 두면 이미 a까지 바뀐 뒤라 2를 되찾지 못해요.':
                 '실제 실수: 복사 시점이 늦으면 공유된 안쪽 배열이 이미 바뀌어 있어요. 이 스텝의 주석 위치와 결과로 확인돼요.'},
         reject=[([['        b[0] = a[0].clone();\n', '        b[0] = new int[]{2, 4};\n']], 'Typed inner values instead of a copy'),
                 ([['        b[0] = a[0].clone();\n', '        b = a;\n']], 'Sharing everything again')],
         accept=[([['        b[0] = a[0].clone();\n', '        b[0] = java.util.Arrays.copyOf(a[0], a[0].length);\n']], 'Arrays.copyOf of the inner array')]),
    dict(old='stp_3629b57c-f0d1-4afa-86b0-3a15a59ab359', title='change가 받은 재고 객체의 count를 바꾸게 하세요',
         objectives=['복사된 참조값으로 같은 객체의 필드를 바꿔요.'],
         core_flow='Stock count2를 change(a, next)로 전달한다. 준비 코드의 value=new Stock(next)는 매개변수만 새 객체로 옮겨 호출자는 2다. 코드 흐름 보기에서 처음 value와 a가 같은 객체를 가리킨다. value.count=next로 고쳐 호출자 7을 확인한다. 채점은 next를 바꿔 실행한다.',
         goal='Java는 메서드에 인수의 값을 복사해서 넘겨요. 객체를 넘기면 그 객체를 가리키는 참조값이 복사돼서, change 안의 value와 main의 a는 같은 Stock을 가리켜요.\n\n'
              'change 메서드의 한 줄을 고쳐 a가 가리키는 재고의 count를 next로 바꾸세요. 채점은 next를 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 a.count가 처음 값 2로 남는지 확인하세요.', '코드 흐름 보기를 눌러 change 안의 value와 main의 a가 처음에 같은 Stock을 가리키는지 보세요.',
                     '`value = new Stock(next);`를 value가 가리키는 객체의 count를 바꾸는 줄로 고치세요.', '코드 실행을 눌러 7이 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s3, solution=s3_solution, tests=[{'input': '', 'expected': '7'}],
         variations=[{'values': {'next': '4'}, 'expected': '4'}, {'values': {'next': '0', 'a': 'new Stock(9)'}, 'expected': '0'}],
         code_flow=True, narration=n3.actions,
         review={'조심하세요. value.count = 7로 숫자를 적으면 next가 바뀐 채점에서 틀려요.': '실제 흔한 하드코딩 실수와 그 결과(준비 값 변경 채점)를 말해요.',
                 '2가 나와요. value에 새 객체를 연결해도 호출한 쪽의 a는 그대로예요.': '대조가 맞아요: 매개변수에 새 객체를 연결하면 a도 바뀔 거라는 예상과 달리 실제 출력 2(a 그대로)가 이어져요.'},
         reject=[([['        value.count = next;\n', '        value.count = 7;\n']], 'Typed 7 instead of next'),
                 ([['        System.out.println(a.count);\n', '        System.out.println(7);\n']], 'Printing a typed value'),
                 ([['        value.count = next;\n', '        value = new Stock(next);\n']], 'Rebinding the parameter only')],
         accept=[([['        value.count = next;\n', '        value.count = value.count - value.count + next;\n']], 'Same field update written differently')]),
    dict(old='stp_d3cb6832-b8de-40be-8a87-cebc11821878', title='replace가 돌려준 새 객체를 a에 다시 담으세요',
         objectives=['매개변수 재대입과 호출자 참조 변경을 구별해 반환값을 대입해요.'],
         core_flow='replace에서 value=new Stock(fresh)를 대입해도 호출자 count2는 남는다. 코드 흐름 보기에서 반환 뒤에도 a가 처음 객체를 가리킨다. a=Changes.replace(a, fresh)로 반환된 참조를 대입해 9를 확인한다. Java를 참조에 의한 전달이라고 설명하지 않는다. 채점은 fresh를 바꿔 실행한다.',
         goal='replace는 매개변수 value에 새 Stock을 연결하고 그 참조값을 반환해요. 매개변수는 호출한 쪽 변수의 복사본이라, 반환값을 받지 않으면 main의 a는 처음 객체를 그대로 가리켜요.\n\n'
              'main의 호출 줄을 고쳐 replace가 돌려준 새 객체를 a에 담으세요. 채점은 fresh를 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 a.count가 처음 값 2로 남는지 확인하세요.', '코드 흐름 보기를 눌러 replace가 끝난 뒤 a가 어느 Stock을 가리키는지 보세요.',
                     '`Changes.replace(a, fresh);`를 반환값을 a에 대입하는 줄로 고치세요.', '코드 실행을 눌러 9가 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s4, solution=s4_solution, tests=[{'input': '', 'expected': '9'}],
         variations=[{'values': {'fresh': '4'}, 'expected': '4'}, {'values': {'fresh': '12', 'a': 'new Stock(1)'}, 'expected': '12'}],
         code_flow=True, narration=n4.actions,
         review={'조심하세요. a.count = 9로 고치면 출력은 같아도 처음 객체를 바꾼 거예요. fresh가 바뀌면 틀려요.':
                 '실제 우회: 처음 객체의 필드를 숫자로 바꾸는 답. 「같아도」 뒤에 「처음 객체를 바꾼 것」이라는 대조가 실제로 이어져요.'},
         reject=[([['        a = Changes.replace(a, fresh);\n', '        a.count = 9;\n']], 'Changing the first object with a typed value'),
                 ([['        a = Changes.replace(a, fresh);\n', '        a = new Stock(9);\n']], 'A new object with a typed value'),
                 ([['        a = Changes.replace(a, fresh);\n', '        Changes.replace(a, fresh);\n']], 'Ignoring the return value')],
         accept=[([['        a = Changes.replace(a, fresh);\n', '        Stock replaced = Changes.replace(a, fresh);\n        a = replaced;\n']], 'Through a local variable')]),
    dict(old='stp_aeb1564a-08f6-4c14-82d8-2da837bde352', title='a에도 느낌표를 붙인 새 글을 담으세요',
         objectives=['String의 불변성과 변수 재대입을 구별해 새 글을 대입해요.'],
         core_flow='a=go와 b=a 뒤 b=b+!이면 a는 go, b는 go!다. 문자열 자체를 수정한 것이 아니라 새 문자열의 참조를 b에 담았다. a=a+"!"를 추가해 a도 새 글을 가리키게 하고 go!:go!를 확인한다. 채점은 a의 처음 글을 바꿔 실행한다.',
         goal='String은 한 번 만든 글자를 바꾸지 않아요. `b + "!"`는 b의 글을 고치지 않고 느낌표가 붙은 새 글을 만들어요. 그래서 b에만 새 글이 담기고 a는 go 그대로예요.\n\n'
              '주석 아래 줄에 a에도 느낌표를 붙인 새 글을 담으세요. 채점은 a의 처음 글을 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 a는 go, b는 go!로 나오는지 확인하세요.', '주석 아래 줄에 a에 느낌표를 붙인 새 글을 대입하는 줄을 쓰세요.',
                     '코드 실행을 눌러 go!:go!가 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s5, solution=s5_solution, tests=[{'input': '', 'expected': 'go!:go!'}],
         variations=[{'values': {'a': '"hi"'}, 'expected': 'hi!:hi!'}, {'values': {'a': '"stock"'}, 'expected': 'stock!:stock!'}],
         narration=n5.actions,
         review={'조심하세요. a + "!"만 쓰고 a에 대입하지 않으면 새 글은 버려지고 a는 그대로예요.': '실제 실수(불변 문자열을 고친다고 생각해 대입을 빠뜨림)와 결과를 말해요.'},
         reject=[([['        a = a + "!";\n', '        a = "go!";\n']], 'Typed text instead of building from a'),
                 ([['        System.out.println(a + ":" + b);\n', '        System.out.println("go!:go!");\n']], 'Printing typed text')],
         accept=[([['        a = a + "!";\n', '        a = b;\n']], 'a may point to the same new text as b'),
                 ([['        a = a + "!";\n', '        a = a.concat("!");\n']], 'concat also returns a new String')]),
    dict(old='stp_9c4b39dc-6f37-429b-b730-cb387879d7da', title='두 글의 내용이 같은지 equals로 출력하세요',
         objectives=['equals와 참조 동일성 비교를 구별해 내용을 비교해요.'],
         core_flow='new String으로 만든 같은 글 두 개를 ==로 비교하면 false다. a.equals(b)를 출력하는 줄을 추가해 true를 확인한다. 문자열 풀 최적화 결과 암기 대신 명확히 서로 다른 객체를 준비한다. 채점은 b의 글을 바꿔 equals가 내용을 보는지 확인한다.',
         goal='`new String("go")`를 두 번 써서 같은 글 go를 담은 객체를 두 개 만들었어요. `==`는 두 변수가 같은 객체를 가리키는지 비교하고, `equals`는 글자 내용이 같은지 비교해요.\n\n'
              '주석 아래 줄에 두 글의 내용이 같은지 출력하세요. 채점은 b의 글을 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 `a == b`의 결과를 확인하세요.', '주석 아래 줄에 equals로 a와 b의 내용을 비교해 출력하는 줄을 쓰세요.',
                     '코드 실행을 눌러 false 다음에 true가 나오는지 확인하세요.', '작성한 코드를 제출하세요.'),
         starter_code=s6, solution=s6_solution, tests=[{'input': '', 'expected': 'false\ntrue'}],
         variations=[{'values': {'b': 'new String("no")'}, 'expected': 'false\nfalse'}, {'values': {'a': 'new String("ok")', 'b': 'new String("ok")'}, 'expected': 'false\ntrue'}],
         narration=n6.actions,
         review={'조심하세요. 글이 같은지 물을 때 ==를 쓰면 다른 객체라서 false가 나올 수 있어요.': '실제 흔한 실수(문자열 내용 비교에 ==)와 결과를 말해요.'},
         reject=[([['        System.out.println(a.equals(b));\n', '        System.out.println(true);\n']], 'Printing a typed true'),
                 ([['        System.out.println(a.equals(b));\n', '        System.out.println(a.length() == b.length());\n']], 'Comparing only the length')],
         accept=[([['        System.out.println(a.equals(b));\n', '        System.out.println(b.equals(a));\n']], 'equals is symmetric here'),
                 ([['        System.out.println(a.equals(b));\n', '        System.out.println(java.util.Objects.equals(a, b));\n']], 'Objects.equals compares content')]),
    dict(old='stp_b2531f88-d023-46a0-9b49-d606db2ad97b', title='text가 null이면 길이를 묻지 않게 조건을 고치세요',
         objectives=['null 참조와 메서드 호출 조건을 구별해 단락 평가로 확인해요.'],
         core_flow='String text=null에서 준비 조건 text!=null & text.length()>0는 오른쪽까지 실행해 NullPointerException을 잡아 missing을 출력한다. &&로 고쳐 false를 확인한다. 채점은 text를 go와 빈 글로 바꿔 실행한다.',
         goal='`text`는 아직 어떤 글도 가리키지 않는 null이에요. null에서 `length()`를 부르면 NullPointerException이 나요. `&`는 양쪽을 모두 계산하지만, `&&`는 왼쪽이 false면 오른쪽을 계산하지 않아요.\n\n'
              '조건의 연산자 한 곳을 고쳐 text가 null이면 길이를 묻지 않고 false가 나오게 하세요. 채점은 text를 다른 글로 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 missing이 나오는지 확인하세요.', '조건의 `&`를 왼쪽이 false면 오른쪽을 건너뛰는 연산자로 고치세요.',
                     '코드 실행을 눌러 false가 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s7, solution=s7_solution, tests=[{'input': '', 'expected': 'false'}],
         variations=[{'values': {'text': '"go"'}, 'expected': 'true'}, {'values': {'text': '""'}, 'expected': 'false'}],
         narration=n7.actions,
         review={'조심하세요. 두 조건의 순서를 바꿔 text.length()를 앞에 두면 &&여도 먼저 예외가 나요.':
                 '실제 실수: 단락 평가는 왼쪽부터라 순서가 바뀌면 보호가 사라져요. 「&&여도」 뒤에 「예외가 난다」는 대조가 실제로 맞아요.'},
         reject=[([['            System.out.println(text != null && text.length() > 0);\n', '            System.out.println(false);\n']], 'Printing a typed false'),
                 ([['text != null && text.length() > 0', 'text.length() > 0 && text != null']], 'Wrong order still calls length() on null')],
         accept=[([['text != null && text.length() > 0', 'text != null && !text.isEmpty()']], 'isEmpty after the null guard')]),
]
