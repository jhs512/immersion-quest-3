"""engineer-java-flow: 7 answer-picking steps -> coding steps (2026-10-29)."""
from _kit import Script, todo

PRD_SCOPE = ['두 챕터·두 단원·아홉 스텝으로 재고 계산 코드의 값과 흐름을 읽어요.',
             '나눗셈·문자열 덧셈·증가·단락 평가·switch·continue·반환값을 한두 줄씩 직접 고쳐 실행하고, 마지막 합계만 짧게 직접 적어요.']
PRD_GRADING = ['직접 고친 코드를 실제 JDK 25로 실행해 판정해요. 준비 값(개수·재고·등급·건너뛸 값)을 바꾼 실행도 맞아야 해요.',
               '고정 출력과 숫자를 적어 넣은 답은 거절해요.',
               '마지막 합계(stp_539dc525-7521-4428-ad57-f386fc8f7110)는 짧은 답안을 판정해요.',
               '마지막 도전(stp_81d6934e-8cf9-47b5-bf45-4ae4beb83506): 시작 답안은 실패해야 해요. 실제 실행 결과를 검사하고 오답과 동등한 정답도 대조해요.']
PRD_NARRATION = ['먼저 준비 코드를 실행해 실제 출력을 읽고, 한 곳을 고친 뒤 다시 실행해 차이를 짚어요.',
                 '메서드 호출 스텝은 코드 흐름 보기로 호출한 쪽 변수와 메서드 안 매개변수가 따로 있는지 확인하게 해요.',
                 '정수 나눗셈·문자열 덧셈·후위 증가·단락 평가·break 없는 case·반환값 버림을 조심할 지점으로 짚어요.']

# ---- 1. 실수 나눗셈 --------------------------------------------------------------------
s1 = '''public class Main {
    public static void main(String[] args) {
        int total = 5;
        int bundles = 2;
        // 이 줄을 고쳐 소수점까지 나눈 평균을 담으세요.
        double average = total / bundles;
        System.out.println(average);
    }
}
'''
s1_solution = s1.replace('        double average = total / bundles;\n',
                         '        // 정수끼리 나누면 몫만 남아요. 하나를 double로 바꾼 뒤 나눠야 소수점이 남아요.\n'
                         '        double average = (double) total / bundles;\n')
n1 = (Script(s1)
      .say('total과 bundles는 정수예요. 소수점까지 나눈 평균이 담기게 고쳐야 해요.', 'text:average 줄을 고쳐 소수점까지 나눈 평균을 담으세요.')
      .run('println(average)')
      .say('2.0이에요. 5 / 2를 정수끼리 먼저 계산해 2가 됐고, 그 2를 double에 담았어요.', 'output')
      .patch('        double average = total / bundles;\n', '        double average = (double) total / bundles;\n', 'total 앞에 (double)을 붙여 실수로 바꾼 뒤 나눠요.')
      .run('println(average)')
      .say('2.5예요. 실수 5.0을 2로 나눠 소수점이 남았어요.', 'output')
      .say('조심하세요. (double) (total / bundles)처럼 괄호로 먼저 나누면 여전히 2.0이에요.', 'code:(double) total / bundles'))

# ---- 2. 문자열 덧셈의 순서 ------------------------------------------------------------
s2 = '''public class Main {
    public static void main(String[] args) {
        int first = 2;
        int second = 3;
        // 이 줄을 고쳐 두 재고의 합이 sum= 뒤에 나오게 하세요.
        System.out.println("sum=" + first + second);
    }
}
'''
s2_solution = s2.replace('        System.out.println("sum=" + first + second);\n',
                         '        // 더하기는 왼쪽부터 묶여요. 괄호로 숫자끼리 먼저 더해야 합이 붙어요.\n'
                         '        System.out.println("sum=" + (first + second));\n')
n2 = (Script(s2)
      .say('두 재고의 합이 sum= 뒤에 나와야 해요. 지금 출력부터 봐요.', 'text:출력 줄을 고쳐 두 재고의 합이 sum= 뒤에 나오게 하세요.')
      .run('println("sum="')
      .say('sum=23이에요. 문자열 sum=에 2를 붙이고 다시 3을 붙였어요.', 'output')
      .patch('        System.out.println("sum=" + first + second);\n', '        System.out.println("sum=" + (first + second));\n', 'first + second를 괄호로 묶어 먼저 더해요.')
      .run('println("sum="')
      .say('sum=5예요. 괄호 안의 숫자 덧셈을 먼저 한 뒤 문자열에 붙였어요.', 'output')
      .say('조심하세요. 문자열이 왼쪽에 있으면 그 뒤의 +는 모두 문자열 붙이기가 돼요.', 'code:"sum=" + (first + second)'))

# ---- 3. 전위 증가 --------------------------------------------------------------------
s3 = '''public class Main {
    public static void main(String[] args) {
        int stock = 3;
        // 이 줄을 고쳐 saved에 1 늘어난 뒤의 값이 담기게 하세요.
        int saved = stock++;
        System.out.println(saved + ":" + stock);
    }
}
'''
s3_solution = s3.replace('        int saved = stock++;\n',
                         '        // ++를 앞에 쓰면 먼저 1 늘리고 그 새 값을 식에 써요.\n        int saved = ++stock;\n')
n3 = (Script(s3)
      .say('saved에 1 늘어난 뒤의 값이 담기게 증가 연산자의 위치를 고쳐야 해요.', 'text:saved 줄을 고쳐 saved에 1 늘어난 뒤의 값이 담기게 하세요.')
      .run('println(saved + ":" + stock)')
      .say('3:4예요. 후위 stock++는 이전 값 3을 saved에 담은 뒤 stock을 늘렸어요.', 'output')
      .patch('        int saved = stock++;\n', '        int saved = ++stock;\n', '++를 stock 앞으로 옮겨요.')
      .run('println(saved + ":" + stock)')
      .say('4:4예요. 전위 ++stock은 먼저 늘린 새 값 4를 saved에 담았어요.', 'output')
      .say('조심하세요. 두 경우 모두 stock은 4가 돼요. 다른 것은 식에 쓰인 값이에요.', 'code:int saved = ++stock;'))

# ---- 4. 단락 평가로 0 나눗셈 막기 ----------------------------------------------------
s4 = '''public class Main {
    public static void main(String[] args) {
        int boxes = 6;
        int stock = 0;
        // 두 조건의 순서를 바꿔 stock이 0이면 나눗셈을 하지 않게 하세요.
        boolean enough = boxes / stock > 1 && stock > 0;
        System.out.println(enough);
    }
}
'''
s4_solution = s4.replace('        boolean enough = boxes / stock > 1 && stock > 0;\n',
                         '        // &&는 왼쪽이 거짓이면 오른쪽을 계산하지 않아요. 0 검사를 왼쪽에 둬요.\n'
                         '        boolean enough = stock > 0 && boxes / stock > 1;\n')
n4 = (Script(s4)
      .say('stock이 0인데 먼저 나눠요. 조건 순서를 바꿔 0일 때 나눗셈을 막아야 해요.', 'text:두 조건의 순서를 바꿔 stock이 0이면 나눗셈을 하지 않게 하세요.')
      .run('println(enough)', error='ArithmeticException')
      .say('ArithmeticException이에요. 왼쪽의 boxes / stock이 0으로 나누기를 했어요.', 'output')
      .patch('        boolean enough = boxes / stock > 1 && stock > 0;\n', '        boolean enough = stock > 0 && boxes / stock > 1;\n', 'stock > 0을 && 왼쪽으로 옮겨요.')
      .run('println(enough)')
      .say('false예요. 왼쪽 stock > 0이 거짓이라 오른쪽 나눗셈은 계산하지 않았어요.', 'output')
      .say('조심하세요. & 하나를 쓰면 왼쪽이 거짓이어도 오른쪽을 계산해 다시 0으로 나눠요.', 'code:stock > 0 && boxes / stock > 1'))

# ---- 5. switch에 break 넣기 ----------------------------------------------------------
s5 = '''public class Main {
    public static void main(String[] args) {
        int grade = 2;
        switch (grade) {
            case 1: System.out.print("A"); break;
            // 이 case 끝에 break를 넣어 2등급은 B만 출력하게 하세요.
            case 2: System.out.print("B");
            case 3: System.out.print("C"); break;
            default: System.out.print("X");
        }
        System.out.println();
    }
}
'''
s5_solution = s5.replace('            case 2: System.out.print("B");\n',
                         '            // break가 없으면 다음 case로 이어져요. break로 switch를 빠져나가요.\n'
                         '            case 2: System.out.print("B"); break;\n')
n5 = (Script(s5)
      .say('2등급이 B만 출력하도록 case 2에 break를 넣어야 해요.', 'text:case 2 끝에 break를 넣어 2등급은 B만 출력하게 하세요.')
      .run('switch (grade)', 'println()')
      .say('BC예요. case 2에 break가 없어서 case 3의 C까지 이어서 실행했어요.', 'output')
      .patch('            case 2: System.out.print("B");\n', '            case 2: System.out.print("B"); break;\n', 'case 2의 출력 뒤에 break를 써요.')
      .run('switch (grade)', 'println()')
      .say('B예요. break에서 switch를 빠져나가 C는 실행하지 않았어요.', 'output')
      .say('조심하세요. case 라벨은 들어가는 곳만 정해요. 빠져나가는 곳은 break예요.', 'code:case 3: System.out.print("C"); break;'))

# ---- 6. continue로 건너뛰기 -----------------------------------------------------------
s6 = '''public class Main {
    public static void main(String[] args) {
        int last = 5;
        int skip = 3;
        int total = 0;
        for (int item = 1; item <= last; item++) {
            // 이 주석 아래에 item이 skip과 같으면 이번 회차만 건너뛰는 줄을 쓰세요.
            total += item;
        }
        System.out.println(total);
    }
}
'''
s6_solution = s6.replace('            // 이 주석 아래에 item이 skip과 같으면 이번 회차만 건너뛰는 줄을 쓰세요.\n',
                         '            // 이 주석 아래에 item이 skip과 같으면 이번 회차만 건너뛰는 줄을 쓰세요.\n'
                         '            // continue는 아래 total += item을 건너뛰고 다음 item으로 가요. break라면 반복을 끝내요.\n'
                         '            if (item == skip) continue;\n')
n6 = (Script(s6)
      .say('1부터 last까지 더하되 skip 하나만 빼야 해요. 반복은 끝내지 않아요.', 'text:주석 아래에 item이 skip과 같으면 이번 회차만 건너뛰는 줄을 쓰세요.')
      .run('println(total)')
      .say('15예요. 아직 1부터 5까지 모두 더했어요.', 'output')
      .patch('            // 이 주석 아래에 item이 skip과 같으면 이번 회차만 건너뛰는 줄을 쓰세요.\n',
             '            // 이 주석 아래에 item이 skip과 같으면 이번 회차만 건너뛰는 줄을 쓰세요.\n            if (item == skip) continue;\n',
             'item이 skip과 같으면 continue로 이번 회차를 건너뛰어요.')
      .run('println(total)')
      .say('12예요. 3만 빼고 1, 2, 4, 5를 더했어요.', 'output')
      .say('조심하세요. continue 대신 break를 쓰면 3에서 반복이 끝나 1과 2만 더한 3이 나와요.', 'code:if (item == skip) continue;'))

# ---- 7. 반환값 받아 두기 --------------------------------------------------------------
s7 = '''class Counter {
    // 전달받은 값으로 새 값을 계산해 반환해요.
    static int add(int value) { return value + 1; }
}
public class Main {
    public static void main(String[] args) {
        int stock = 3;
        // 이 줄을 고쳐 add가 반환한 값을 stock에 담으세요.
        Counter.add(stock);
        System.out.println(stock);
    }
}
'''
s7_solution = s7.replace('        Counter.add(stock);\n',
                         '        // 메서드는 stock의 값을 복사해 받아요. 반환값을 대입해야 stock이 바뀌어요.\n'
                         '        stock = Counter.add(stock);\n')
n7 = (Script(s7)
      .say('add는 새 값을 반환만 해요. 반환값을 stock에 담게 호출 줄을 고쳐야 해요.', 'text:호출 줄을 고쳐 add가 반환한 값을 stock에 담으세요.')
      .run('println(stock)')
      .say('3이에요. add 안의 value는 복사본이고, 반환한 4는 아무 데도 담지 않았어요.', 'output')
      .patch('        Counter.add(stock);\n', '        stock = Counter.add(stock);\n', '호출 앞에 stock =을 붙여 반환값을 담아요.')
      .run('println(stock)')
      .say('4예요. 반환된 값이 stock에 대입됐어요.', 'output')
      .say('코드 흐름 보기에서 add 칸의 value와 main 칸의 stock이 따로 있고, 돌아온 뒤 stock이 4로 바뀌어요.', 'text:코드 흐름 보기를 눌러 add 안의 value와 main의 stock이 따로 있는지 보세요.')
      .say('조심하세요. add 안에서 value를 바꿔도 호출한 쪽 stock은 바뀌지 않아요.', 'code:static int add(int value) { return value + 1; }'))

SPECS = [
    dict(old='stp_e89108e7-6f81-4a7f-984b-320d809b411b', title='total을 double로 바꿔 소수점까지 나눈 평균을 담으세요',
         objectives=['정수 나눗셈 뒤 실수 변환과 실수 나눗셈을 구별해요.'],
         core_flow='int total=5, bundles=2로 double average=total/bundles는 2.0이다. (double) total / bundles로 고쳐 2.5를 확인한다. 채점은 total과 bundles를 바꿔 실행한다.',
         goal='정수끼리 나누면 몫만 남아요. 그 결과를 double 변수에 담아도 이미 버린 소수점은 돌아오지 않아요. 나누기 전에 한쪽을 double로 바꿔야 소수점까지 계산해요.\n\n'
              'average 줄을 고쳐 소수점까지 나눈 평균을 담으세요. 채점은 total과 bundles를 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 2.0이 나오는지 확인하세요.', 'total 앞에 `(double)`을 붙여 나누는 식으로 고치세요.', '코드 실행을 눌러 2.5가 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s1, solution=s1_solution, tests=[{'input': '', 'expected': '2.5'}],
         variations=[{'values': {'total': '7'}, 'expected': '3.5'}, {'values': {'bundles': '4'}, 'expected': '1.25'}],
         narration=n1.actions,
         review={'조심하세요. (double) (total / bundles)처럼 괄호로 먼저 나누면 여전히 2.0이에요.': '실제 흔한 실수와 그 결과(2.0)를 정확히 말해요.'},
         reject=[([['        double average = (double) total / bundles;\n', '        double average = (double) (total / bundles);\n']], 'Casting after the integer division'),
                 ([['        double average = (double) total / bundles;\n', '        double average = 2.5;\n']], 'Typing the value')],
         accept=[([['        double average = (double) total / bundles;\n', '        double average = total / (double) bundles;\n']], 'Casting the divisor'),
                 ([['        double average = (double) total / bundles;\n', '        double average = total * 1.0 / bundles;\n']], 'Multiplying by 1.0 first')]),
    dict(old='stp_4703ac8b-8927-4838-b3dc-33fd8a1ebeac', title='괄호로 두 재고를 먼저 더해 sum= 뒤에 합이 나오게 하세요',
         objectives=['왼쪽부터 묶이는 문자열 연결과 숫자 덧셈을 구별해요.'],
         core_flow='"sum=" + first + second는 sum=23이다. 왼쪽 문자열에 차례로 붙기 때문이다. (first + second)로 묶어 sum=5를 확인한다. 채점은 first와 second를 바꿔 실행한다.',
         goal='+는 왼쪽부터 차례로 묶여요. 왼쪽이 문자열이면 +는 숫자를 더하지 않고 글자로 붙여요.\n\n'
              '출력 줄을 고쳐 두 재고의 합이 sum= 뒤에 나오게 하세요. 채점은 first와 second를 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 sum=23이 나오는지 확인하세요.', '`first + second`를 괄호로 묶으세요.', '코드 실행을 눌러 sum=5가 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s2, solution=s2_solution, tests=[{'input': '', 'expected': 'sum=5'}],
         variations=[{'values': {'first': '4'}, 'expected': 'sum=7'}, {'values': {'second': '10'}, 'expected': 'sum=12'}],
         narration=n2.actions,
         review={'조심하세요. 문자열이 왼쪽에 있으면 그 뒤의 +는 모두 문자열 붙이기가 돼요.': '실제 Java 규칙(왼쪽 결합, String 연결)을 말해요.'},
         reject=[([['        System.out.println("sum=" + (first + second));\n', '        System.out.println("sum=5");\n']], 'Printing typed text'),
                 ([['        System.out.println("sum=" + (first + second));\n', '        System.out.println("sum=" + first + second);\n']], 'No parentheses')],
         accept=[([['        System.out.println("sum=" + (first + second));\n', '        int sum = first + second;\n        System.out.println("sum=" + sum);\n']], 'Adding into a variable first')]),
    dict(old='stp_eee53a84-54ae-4421-a53d-0909c3afb1a5', title='전위 증가로 바꿔 saved에 늘어난 값을 담으세요',
         objectives=['후위 증가와 전위 증가가 식에 쓰는 값을 구별해요.'],
         core_flow='int saved=stock++는 이전 값 3을 담아 3:4다. ++stock으로 고쳐 4:4를 확인한다. 채점은 stock을 바꿔 실행한다.',
         goal='`stock++`(후위)는 지금 값을 식에 쓴 뒤 1 늘리고, `++stock`(전위)은 먼저 1 늘린 뒤 새 값을 식에 써요.\n\n'
              'saved 줄을 고쳐 saved에 1 늘어난 뒤의 값이 담기게 하세요. 채점은 stock의 처음 값을 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 3:4가 나오는지 확인하세요.', '`stock++`를 전위 증가로 바꾸세요.', '코드 실행을 눌러 4:4가 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s3, solution=s3_solution, tests=[{'input': '', 'expected': '4:4'}],
         variations=[{'values': {'stock': '8'}, 'expected': '9:9'}, {'values': {'stock': '0'}, 'expected': '1:1'}],
         narration=n3.actions,
         review={'조심하세요. 두 경우 모두 stock은 4가 돼요. 다른 것은 식에 쓰인 값이에요.': '실제 차이(식의 값)와 공통점(변수의 새 값)을 정확히 말해요.'},
         reject=[([['        int saved = ++stock;\n', '        int saved = 4;\n        stock++;\n']], 'Typing the value'),
                 ([['        int saved = ++stock;\n', '        int saved = stock + 1;\n']], 'stock itself does not change')],
         accept=[([['        int saved = ++stock;\n', '        stock += 1;\n        int saved = stock;\n']], 'Increasing first in its own line')]),
    dict(old='stp_67c726e2-693f-4c3c-96c0-0bc088b71fe0', title='조건 순서를 바꿔 재고가 0이면 나누지 않게 하세요',
         objectives=['&&의 단락 평가로 오른쪽 계산을 건너뛰는 흐름을 이해해요.'],
         core_flow='boxes / stock > 1 && stock > 0은 stock=0에서 ArithmeticException이다. stock > 0 && boxes / stock > 1로 바꿔 false를 확인한다. 왼쪽이 거짓이면 오른쪽은 계산하지 않는다. 채점은 stock과 boxes를 바꿔 true와 false를 모두 확인한다.',
         goal='`&&`는 왼쪽이 거짓이면 결과가 이미 거짓이라 오른쪽을 계산하지 않아요(단락 평가). 그래서 위험한 계산 앞에 그 계산을 막는 조건을 두면 돼요. 지금은 나눗셈이 왼쪽에 있어 재고가 0이면 오류가 나요.\n\n'
              '두 조건의 순서를 바꿔 stock이 0이면 나눗셈을 하지 않게 하세요. 채점은 stock과 boxes를 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 ArithmeticException 오류가 나는지 확인하세요.', '`stock > 0`을 `&&`의 왼쪽으로 옮기세요.', '코드 실행을 눌러 false가 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s4, solution=s4_solution, tests=[{'input': '', 'expected': 'false'}],
         variations=[{'values': {'stock': '2'}, 'expected': 'true'}, {'values': {'stock': '3', 'boxes': '2'}, 'expected': 'false'}],
         narration=n4.actions,
         review={'조심하세요. & 하나를 쓰면 왼쪽이 거짓이어도 오른쪽을 계산해 다시 0으로 나눠요.': '실제 Java 규칙(&는 단락 평가 없음)과 그 결과를 정확히 말해요.'},
         reject=[([['        boolean enough = stock > 0 && boxes / stock > 1;\n', '        boolean enough = stock > 0 & boxes / stock > 1;\n']], 'Non-short-circuit & still divides'),
                 ([['        boolean enough = stock > 0 && boxes / stock > 1;\n', '        boolean enough = false;\n']], 'Typing the value')],
         accept=[([['        boolean enough = stock > 0 && boxes / stock > 1;\n', '        boolean enough = stock != 0 && boxes / stock > 1;\n']], 'Checking not zero')]),
    dict(old='stp_69d4efab-7283-4ffa-8963-dc78aff1221e', title='case 2에 break를 넣어 2등급은 B만 출력하게 하세요',
         objectives=['switch에서 break가 없을 때 다음 case로 이어지는 흐름을 구별해요.'],
         core_flow='grade=2에서 case 2에 break가 없어 BC다. case 2 끝에 break를 넣어 B를 확인한다. 채점은 grade를 1, 3, 9로 바꿔 A, C, X도 확인한다.',
         goal='switch는 값이 맞는 case로 들어간 뒤 break를 만날 때까지 아래 문장을 이어서 실행해요. 지금 case 2에는 break가 없어요.\n\n'
              'case 2 끝에 break를 넣어 2등급은 B만 출력하게 하세요. 다른 case는 그대로 둬요. 채점은 grade를 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 BC가 나오는지 확인하세요.', '`case 2:` 줄의 출력 뒤에 `break;`를 쓰세요.', '코드 실행을 눌러 B만 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s5, solution=s5_solution, tests=[{'input': '', 'expected': 'B'}],
         variations=[{'values': {'grade': '3'}, 'expected': 'C'}, {'values': {'grade': '1'}, 'expected': 'A'}, {'values': {'grade': '9'}, 'expected': 'X'}],
         narration=n5.actions,
         review={'조심하세요. case 라벨은 들어가는 곳만 정해요. 빠져나가는 곳은 break예요.': '실제 switch 의미(라벨=진입점)를 정확히 말해요.'},
         reject=[([['            case 2: System.out.print("B"); break;\n            case 3: System.out.print("C"); break;\n', '            case 2: System.out.print("B");\n            case 3: break;\n']], 'Removing C from case 3'),
                 ([['        switch (grade) {\n', '        System.out.print("B");\n        if (false) switch (grade) {\n']], 'Printing typed text')],
         accept=[([['            case 2: System.out.print("B"); break;\n', '            case 2: {\n                System.out.print("B");\n                break;\n            }\n']], 'A block with break')]),
    dict(old='stp_bf5dad24-2d50-4d47-8ac5-e487ad597ccb', title='continue로 skip 하나만 건너뛰고 나머지를 더하세요',
         objectives=['continue와 break가 반복에 미치는 차이를 구별해요.'],
         core_flow='1부터 last까지 더하는 반복이 15다. item==skip이면 continue를 넣어 12를 확인한다. break라면 3에서 끝나 3이다. 채점은 skip과 last를 바꿔 실행한다.',
         goal='`continue`는 이번 회차의 남은 문장만 건너뛰고 다음 회차로 가요. `break`는 반복 전체를 끝내요.\n\n'
              '주석 아래에 item이 skip과 같으면 이번 회차만 건너뛰는 줄을 쓰세요. 채점은 skip과 last를 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 15가 나오는지 확인하세요.', '주석 아래에 `item == skip`일 때 continue하는 if 문을 쓰세요.', '코드 실행을 눌러 12가 나오는지 확인하세요.', '작성한 코드를 제출하세요.'),
         starter_code=s6, solution=s6_solution, tests=[{'input': '', 'expected': '12'}],
         variations=[{'values': {'skip': '5'}, 'expected': '10'}, {'values': {'last': '6', 'skip': '1'}, 'expected': '20'}, {'values': {'skip': '9'}, 'expected': '15'}],
         narration=n6.actions,
         review={'조심하세요. continue 대신 break를 쓰면 3에서 반복이 끝나 1과 2만 더한 3이 나와요.': '실제 흔한 혼동과 그 실제 출력(3)을 정확히 말해요.'},
         reject=[([['            if (item == skip) continue;\n', '            if (item == skip) break;\n']], 'break ends the loop'),
                 ([['            if (item == skip) continue;\n', '            if (item == 3) continue;\n']], 'Typing 3 instead of skip')],
         accept=[([['            if (item == skip) continue;\n            total += item;\n', '            if (item != skip) {\n                total += item;\n            }\n']], 'Adding only when different')]),
    dict(old='stp_9d38c622-cee3-4679-ae1f-ebb0b644e473', title='add가 반환한 값을 stock에 담으세요',
         objectives=['값 전달과 반환값 대입을 구별해요.'],
         core_flow='Counter.add(stock)의 반환값을 버려 stock은 3이다. stock = Counter.add(stock)으로 고쳐 4를 확인한다. 코드 흐름 보기에서 add의 value와 main의 stock이 따로 있다. 채점은 stock을 바꿔 실행한다.',
         goal='메서드를 부르면 stock의 값이 복사돼 매개변수 value로 들어가요. add는 value + 1을 반환할 뿐이라, 반환값을 받아 대입하지 않으면 호출한 쪽 stock은 그대로예요.\n\n'
              '호출 줄을 고쳐 add가 반환한 값을 stock에 담으세요. 채점은 stock의 처음 값을 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 3이 나오는지 확인하세요.', '`Counter.add(stock);` 앞에 `stock =`을 붙이세요.', '코드 실행을 눌러 4가 나오는지 확인하세요.',
                     '코드 흐름 보기를 눌러 add 안의 value와 main의 stock이 따로 있는지 보세요.', '수정한 코드를 제출하세요.'),
         starter_code=s7, solution=s7_solution, tests=[{'input': '', 'expected': '4'}],
         variations=[{'values': {'stock': '9'}, 'expected': '10'}, {'values': {'stock': '-1'}, 'expected': '0'}],
         code_flow=True, narration=n7.actions,
         review={'조심하세요. add 안에서 value를 바꿔도 호출한 쪽 stock은 바뀌지 않아요.': '실제 Java 값 전달 규칙을 정확히 말해요.'},
         reject=[([['        stock = Counter.add(stock);\n', '        Counter.add(stock);\n        stock = 4;\n']], 'Typing the value'),
                 ([['        stock = Counter.add(stock);\n', '        Counter.add(stock);\n']], 'Discarding the return value')],
         accept=[([['        stock = Counter.add(stock);\n', '        int next = Counter.add(stock);\n        stock = next;\n']], 'Through another variable')]),
]
