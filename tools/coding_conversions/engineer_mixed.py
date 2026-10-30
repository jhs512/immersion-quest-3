"""engineer-mixed: 10 code-reading answer fields -> coding steps (2026-10-30 user decision).

Steps 1-9 showed finished C/Java/Python/SQL code and asked for its output; each now asks for the one
edit that produces the behaviour, graded with changed prepared values (C/Java declarations, Python
top-level names, SQL setup tables) so typed output fails. The final challenge (15) keeps its reference
sharing and NULL-count halves as Python code; its regression-test term is theory already practised in
step 12 and is not part of the coding challenge. Steps 10-14 (requirements, boundary, test double,
verification source, exam scope) stay as they are."""
from _kit import Script, todo, sql_output, code_step

PRD_SCOPE = ['3챕터·3단원·14스텝으로 같은 상황을 점진적으로 바꿔요.',
             'C·Java·Python·SQL 코드 스텝은 실행 결과를 적는 대신 한 곳을 직접 고쳐 실제로 실행해요. 문서 판단 스텝은 실행 결과와 구별해요.',
             '마지막 도전은 Python 코드에서 안쪽 목록까지 복사하기와 NULL을 뺀 개수 세기를 함께 써요.']
PRD_GRADING = ['코드·SQL 스텝은 직접 고친 코드를 실제 C·JDK 25·Python·SQLite로 실행하고, 준비 값·표를 바꾼 실행도 맞아야 해요. 결과를 글자로 적은 답은 거절해요.',
               '문서 판단 스텝은 짧은 용어 답안과 선택을 직접 제출해요.',
               '마지막 도전: 시작 답안은 실패해야 해요. 다른 목록과 값으로 다시 실행해 바깥만 복사한 답과 0을 빼고 센 답을 거절해요.']
PRD_NARRATION = ['준비 코드를 먼저 실행하고 한 곳을 고친 뒤 다시 실행해 차이를 짚어요.',
                 '조심할 오해를 짚되 학습자에게 긴 글을 반복해서 읽게 하지 않아요.']

RUN = '코드 실행을 눌러 지금 결과를 확인하세요.'
SUB = '수정한 코드를 제출하세요.'

# ---- 1. C 포인터 이동 -------------------------------------------------------------------
m1 = '''#include <stdio.h>
int main(void) {
    int values[] = {3, 7, 9};
    int *p = values;
    // 이 주석 아래에 p를 다음 원소로 한 칸 옮기는 줄을 쓰세요.
    printf("%d\\n", *p);
    return 0;
}
'''
m1_sol = m1.replace('    // 이 주석 아래에 p를 다음 원소로 한 칸 옮기는 줄을 쓰세요.\n',
                    '    // 이 주석 아래에 p를 다음 원소로 한 칸 옮기는 줄을 쓰세요.\n    // p++는 주소를 원소 하나 크기만큼 옮겨요. 값에 1을 더하는 게 아니에요.\n    p++;\n')
k1 = (Script(m1)
      .say('p는 배열의 첫 원소를 가리켜요. 다음 원소를 읽도록 p를 한 칸 옮겨야 해요.', 'text:주석 아래에 p를 다음 원소로 한 칸 옮기는 줄을 쓰세요.')
      .run('printf("%d\\n", *p);')
      .say('3이에요. 아직 첫 원소를 가리켜요.', 'output')
      .patch('    printf("%d\\n", *p);\n', '    p++;\n    printf("%d\\n", *p);\n', 'printf 앞에 p++;를 써요.')
      .run('printf("%d\\n", *p);')
      .say('7이에요. p가 둘째 원소로 옮겨 갔어요.', 'output')
      .say('조심하세요. *p + 1은 첫 원소 3에 1을 더한 4예요. 옮기는 건 주소예요.', 'code:p++;'))

# ---- 2. C 재귀 누적 ---------------------------------------------------------------------
m2 = '''#include <stdio.h>
// 이 함수를 고쳐 n이 0이 아니면 n과 sum(n - 1)을 더해 돌려주세요.
int sum(int n) { return n == 0 ? 0 : n; }
int main(void) {
    int count = 3;
    printf("%d\\n", sum(count));
    return 0;
}
'''
m2_sol = m2.replace('int sum(int n) { return n == 0 ? 0 : n; }\n',
                    '// 0이면 멈추고, 아니면 한 단계 작은 sum의 반환값에 n을 더해 돌아와요.\nint sum(int n) { return n == 0 ? 0 : n + sum(n - 1); }\n')
k2 = (Script(m2)
      .say('조건 ? 값1 : 값2는 조건이 참이면 값1이에요. 0이 아니면 n과 sum(n - 1)을 더하게 고쳐야 해요.', 'text:함수를 고쳐 n이 0이 아니면 n과 sum(n - 1)을 더해 돌려주세요.')
      .run('printf("%d\\n", sum(count));')
      .say('3이에요. 작은 문제를 부르지 않고 n만 돌려줬어요.', 'output')
      .patch('? 0 : n; }', '? 0 : n + sum(n - 1); }', 'n 뒤에 + sum(n - 1)을 더해요.')
      .run('printf("%d\\n", sum(count));')
      .say('6이에요. 3 + 2 + 1 + 0을 돌아오면서 더했어요.', 'output')
      .say('조심하세요. n == 0인 멈춤 조건이 없으면 sum이 끝없이 자신을 불러요.', 'code:n == 0 ? 0'))

# ---- 3. Java static 공유 수 -------------------------------------------------------------
m3 = '''class Report {
    // 이 줄을 고쳐 생성 횟수를 모든 보고 객체가 함께 쓰게 하세요.
    int count = 0;
    int qty = 3;
    Report() { count++; }
}

public class Main {
    public static void main(String[] args) {
        Report first = new Report();
        Report second = new Report();
        second.qty = 8;
        System.out.println(first.count + ":" + first.qty);
    }
}
'''
m3_sol = m3.replace('    int count = 0;\n', '    // static이면 객체마다가 아니라 클래스에 하나만 있어요. 두 생성자가 같은 count를 늘려요.\n    static int count = 0;\n')
k3 = (Script(m3)
      .say('생성 횟수는 모든 보고 객체가 함께 써야 해요. count 필드를 static으로 바꿔요.', 'text:count 줄을 고쳐 생성 횟수를 모든 보고 객체가 함께 쓰게 하세요.')
      .run('System.out.println(first.count')
      .say('1:3이에요. 객체마다 count가 따로 있어 first는 자기 생성만 셌어요.', 'output')
      .patch('    int count = 0;\n', '    static int count = 0;\n', 'int 앞에 static을 붙여요.')
      .run('System.out.println(first.count')
      .say('2:3이에요. 두 생성이 같은 count를 늘렸고, qty는 객체마다 따로라 first는 3이에요.', 'output')
      .say('조심하세요. qty까지 static으로 바꾸면 second.qty = 8이 first.qty도 바꿔요.', 'code:static int count = 0;'))

# ---- 4. Java 재정의 ---------------------------------------------------------------------
m4 = '''class Report { int read() { return 3; } }
class Child extends Report {
    static int extra = 9;
    // 이 클래스 안에 상위의 read()를 재정의해 extra를 돌려주는 메서드를 쓰세요.
}

public class Main {
    public static void main(String[] args) {
        Report report = new Child();
        System.out.println(report.read());
    }
}
'''
m4_sol = m4.replace('    // 이 클래스 안에 상위의 read()를 재정의해 extra를 돌려주는 메서드를 쓰세요.\n',
                    '    // 이 클래스 안에 상위의 read()를 재정의해 extra를 돌려주는 메서드를 쓰세요.\n'
                    '    // 이름과 매개변수가 같아야 재정의예요. 변수 타입이 Report여도 실제 객체의 read가 실행돼요.\n'
                    '    @Override int read() { return extra; }\n')
k4 = (Script(m4)
      .say('변수 타입은 Report지만 실제 객체는 Child예요. Child에 read를 재정의해 extra를 돌려주게 해요.', 'text:클래스 안에 상위의 read()를 재정의해 extra를 돌려주는 메서드를 쓰세요.')
      .run('System.out.println(report.read());')
      .say('3이에요. Child에 read가 없어 Report의 read가 실행됐어요.', 'output')
      .patch('    static int extra = 9;\n', '    static int extra = 9;\n    @Override int read() { return extra; }\n', 'extra 아래에 @Override int read() { return extra; }를 써요.')
      .run('System.out.println(report.read());')
      .say('9예요. 실제 객체 Child의 read가 실행됐어요.', 'output')
      .say('조심하세요. read(int x)처럼 매개변수를 바꾸면 재정의가 아니라 새 메서드라 3이 그대로 나와요.', 'code:@Override int read()'))

# ---- 5. Python 안쪽 목록 복사 -----------------------------------------------------------
m5 = 'a = [[3]]\nnew = 8\n# 이 줄을 고쳐 b를 바꿔도 a가 그대로이게 안쪽 목록까지 복사하세요.\nb = a[:]\nb[0][0] = new\nprint(a[0][0])\nprint(b[0][0])\n'
m5_sol = m5.replace('b = a[:]\n', '# a[:]는 바깥 목록만 복사해요. 안쪽 목록도 하나씩 새로 만들어야 따로 써요.\nb = [row[:] for row in a]\n')
k5 = (Script(m5)
      .say('b의 안쪽 값을 바꿔도 a는 그대로여야 해요. 안쪽 목록까지 하나씩 복사해요.', 'text:b 줄을 고쳐 b를 바꿔도 a가 그대로이게 안쪽 목록까지 복사하세요.')
      .run('print(a[0][0])', 'print(b[0][0])')
      .say('8과 8이에요. 바깥만 복사해서 안쪽 목록을 함께 써요.', 'output')
      .patch('b = a[:]\n', 'b = [row[:] for row in a]\n', 'a[:]를 [row[:] for row in a]로 바꿔요.')
      .run('print(a[0][0])', 'print(b[0][0])')
      .say('3과 8이에요. 안쪽 목록도 새로 만들어 a는 그대로예요.', 'output')
      .say('조심하세요. list(a)도 a[:]처럼 바깥만 복사해요.', 'code:[row[:] for row in a]'))

# ---- 6. Python 몫과 나머지 --------------------------------------------------------------
m6 = ('total = -5\nsize = 2\n# 이 두 줄을 고쳐 Python의 몫 연산자 //와 나머지 연산자 %로 계산하세요.\nq = int(total / size)\nr = total - q * size\nprint(q, r)\n')
m6_sol = m6.replace('q = int(total / size)\nr = total - q * size\n',
                    '# //는 몫을 아래쪽 정수로 내려요. %의 결과는 나누는 수와 같은 부호예요.\nq = total // size\nr = total % size\n')
k6 = (Script(m6)
      .say('음수를 나눌 때 Python의 몫과 나머지 규칙을 써야 해요. //와 %로 바꿔요.', 'text:두 줄을 고쳐 Python의 몫 연산자 //와 나머지 연산자 %로 계산하세요.')
      .run('print(q, r)')
      .say('-2 -1이에요. int는 0 쪽으로 버려 -2.5를 -2로 만들었어요.', 'output')
      .patch('q = int(total / size)\n', 'q = total // size\n', 'q 줄을 total // size로 바꿔요.')
      .patch('r = total - q * size\n', 'r = total % size\n', 'r 줄을 total % size로 바꿔요.')
      .run('print(q, r)')
      .say('-3 1이에요. //는 아래쪽인 -3으로 내렸고, -3 × 2 + 1이 -5예요.', 'output')
      .say('조심하세요. 양수끼리는 두 방법이 같아요. 음수가 섞이면 C나 int와 결과가 달라요.', 'code:total // size'))

# ---- 7–9. SQL ---------------------------------------------------------------------------
Q_SCHEMA = 'CREATE TABLE stock(qty INTEGER);\n'
Q_BASE = {'setup.sql': Q_SCHEMA + 'INSERT INTO stock VALUES(2),(NULL),(4);\n'}
Q_V1 = {'setup.sql': Q_SCHEMA + 'INSERT INTO stock VALUES(NULL),(NULL),(0),(7);\n'}
Q_V2 = {'setup.sql': Q_SCHEMA + 'INSERT INTO stock VALUES(5);\n'}
J_SCHEMA = 'CREATE TABLE product(id INTEGER);\nCREATE TABLE orders(product_id INTEGER);\n'
J_BASE = {'setup.sql': J_SCHEMA + 'INSERT INTO product VALUES(1),(2);\nINSERT INTO orders VALUES(1),(1);\n'}
J_V1 = {'setup.sql': J_SCHEMA + 'INSERT INTO product VALUES(1),(2),(3);\nINSERT INTO orders VALUES(3);\n'}
J_V2 = {'setup.sql': J_SCHEMA + 'INSERT INTO product VALUES(1),(2);\nINSERT INTO orders VALUES(1),(1),(1);\n'}
G_SCHEMA = 'CREATE TABLE stock(category TEXT, qty INTEGER);\n'
G_BASE = {'setup.sql': G_SCHEMA + "INSERT INTO stock VALUES('A',2),('A',2),('B',1);\n"}
G_V1 = {'setup.sql': G_SCHEMA + "INSERT INTO stock VALUES('A',1),('B',5),('C',2),('C',2);\n"}
G_V2 = {'setup.sql': G_SCHEMA + "INSERT INTO stock VALUES('A',9),('B',4);\n"}


def sql_step(old, title, objective, core_flow, intro, instruction, edit, base, variants, starter, solution, script, review, reject, accept):
    expected = sql_output(base, solution)
    return dict(old=old, title=title, objectives=[objective], core_flow=core_flow, language='sql',
                goal=intro + '\n\n' + instruction + '\n\n' + todo(RUN, edit, '코드 실행을 눌러 결과가 바뀌었는지 확인하세요.', SUB),
                starter_code=starter, solution=solution, files=base, tests=[{'input': '', 'expected': expected}],
                variations=[{'files': v, 'expected': sql_output(v, solution)} for v in variants],
                narration=script.actions, review=review, reject=reject, accept=accept)


m7 = '-- 이 질의를 고쳐 qty에 값이 있는 행만 세세요.\nSELECT COUNT(*) AS n FROM stock;\n'
m7_sol = '-- 이 질의를 고쳐 qty에 값이 있는 행만 세세요.\n-- COUNT(qty)는 qty가 NULL인 행을 빼고 세요. COUNT(*)는 모든 행을 세요.\nSELECT COUNT(qty) AS n FROM stock;\n'
k7 = (Script(m7)
      .say('수량은 2, NULL, 4예요. 값이 있는 수량만 세도록 COUNT 안을 고쳐야 해요.', 'text:질의를 고쳐 qty에 값이 있는 행만 세세요.')
      .run('SELECT COUNT(')
      .say('3이에요. COUNT(*)는 NULL인 행까지 모든 행을 세었어요.', 'output')
      .patch('COUNT(*)', 'COUNT(qty)', '별표를 qty로 바꿔요.')
      .run('SELECT COUNT(')
      .say('2예요. NULL인 행을 빼고 세었어요.', 'output')
      .say('조심하세요. 수량 0은 NULL이 아니라 값이라 COUNT(qty)가 세요.', 'code:COUNT(qty)'))

m8 = '-- 이 질의를 고쳐 주문이 없는 상품도 한 행으로 남겨 전체 행을 세세요.\nSELECT COUNT(*) AS n FROM product p\nJOIN orders o ON p.id = o.product_id;\n'
m8_sol = ('-- 이 질의를 고쳐 주문이 없는 상품도 한 행으로 남겨 전체 행을 세세요.\n-- LEFT JOIN은 왼쪽 상품을 모두 남겨요. 주문이 없으면 주문 쪽 열이 NULL인 한 행이 돼요.\n'
          'SELECT COUNT(*) AS n FROM product p\nLEFT JOIN orders o ON p.id = o.product_id;\n')
k8 = (Script(m8)
      .say('상품 A에는 주문이 두 개, B에는 없어요. 주문이 없는 상품도 남도록 LEFT JOIN으로 고쳐야 해요.', 'text:질의를 고쳐 주문이 없는 상품도 한 행으로 남겨 전체 행을 세세요.')
      .run('SELECT COUNT(*)', 'JOIN orders')
      .say('2예요. JOIN은 짝이 맞는 A의 두 행만 남겼어요.', 'output')
      .patch('\nJOIN orders', '\nLEFT JOIN orders', 'JOIN 앞에 LEFT를 붙여요.')
      .run('SELECT COUNT(*)', 'LEFT JOIN orders')
      .say('3이에요. A의 두 행과 주문이 없는 B의 한 행이에요.', 'output')
      .say('조심하세요. 주문이 여러 개인 상품은 LEFT JOIN에서도 주문 수만큼 행이 늘어요.', 'code:LEFT JOIN'))

m9 = ('-- 안쪽 질의에 HAVING을 더해 수량 합계가 3을 넘는 분류만 남기세요.\nSELECT COUNT(*) AS n FROM (\n SELECT category FROM stock\n GROUP BY category\n) AS totals;\n')
m9_sol = ('-- 안쪽 질의에 HAVING을 더해 수량 합계가 3을 넘는 분류만 남기세요.\n-- HAVING은 묶은 뒤의 합계로 그룹을 걸러요. 바깥 질의는 남은 그룹 수를 세요.\n'
          'SELECT COUNT(*) AS n FROM (\n SELECT category FROM stock\n GROUP BY category HAVING SUM(qty) > 3\n) AS totals;\n')
k9 = (Script(m9)
      .say('FROM 뒤 괄호 안의 질의 결과를 표처럼 써요. 안쪽 질의에 HAVING을 더해 합계가 3을 넘는 분류만 남겨야 해요.', 'text:안쪽 질의에 HAVING을 더해 수량 합계가 3을 넘는 분류만 남기세요.')
      .run('SELECT COUNT(*)', ') AS totals;')
      .say('2예요. 분류 A와 B를 모두 세었어요.', 'output')
      .patch(' GROUP BY category\n', ' GROUP BY category HAVING SUM(qty) > 3\n', 'GROUP BY category 뒤에 HAVING SUM(qty) > 3을 써요.')
      .run('SELECT COUNT(*)', ') AS totals;')
      .say('1이에요. 합계 4인 A만 남았고 합계 1인 B는 빠졌어요.', 'output')
      .say('조심하세요. WHERE qty > 3은 묶기 전에 행 하나씩 걸러요. 합계 조건은 HAVING에 써요.', 'code:HAVING SUM(qty) > 3'))

# ---- 15. 마지막 도전 --------------------------------------------------------------------
m15 = ('rows = [[2], [5]]\nqty = [2, None, 0]\nadded = 3\n'
       '# 1) 이 줄을 고쳐 copy를 바꿔도 rows가 그대로이게 안쪽 목록까지 복사하세요.\ncopy = rows[:]\ncopy[0][0] += added\nprint(rows[0][0], copy[0][0])\n'
       '# 2) 이 줄을 고쳐 SQL의 COUNT(qty)처럼 None이 아닌 값만 세세요. 0도 값이에요.\ncount = len(qty)\nprint(count)\n')
m15_sol = (m15.replace('copy = rows[:]\n', '# 바깥만 복사하면 안쪽 목록을 함께 써요. 안쪽 목록도 하나씩 새로 만들어요.\ncopy = [row[:] for row in rows]\n')
           .replace('count = len(qty)\n', '# None만 빼고 세요. 0은 None이 아니라서 세요.\ncount = sum(1 for value in qty if value is not None)\n'))
k15 = (Script(m15)
       .say('마지막 도전이에요. 참조 공유와 NULL 집계를 서로 다른 근거로 코드에 써요.', 'text:참조 공유와 NULL 집계를 서로 다른 근거로 코드에 써요.')
       .run('print(rows[0][0]', 'print(count)')
       .say('5 5와 3이에요. rows도 바뀌었고, None까지 세었어요.', 'output')
       .patch('copy = rows[:]\n', 'copy = [row[:] for row in rows]\n', 'rows[:]를 [row[:] for row in rows]로 바꿔요.')
       .run('print(rows[0][0]', 'print(count)')
       .say('2 5예요. 안쪽 목록까지 복사해 rows는 그대로예요.', 'output')
       .patch('count = len(qty)\n', 'count = sum(1 for value in qty if value is not None)\n', 'None이 아닌 값만 세는 식으로 바꿔요.')
       .run('print(rows[0][0]', 'print(count)')
       .say('2예요. None 하나를 빼고 2와 0을 세었어요.', 'output')
       .say('조심하세요. if value처럼 참 거짓으로 거르면 0까지 빠져 1이 돼요. None인지 직접 비교해요.', 'code:value is not None'))

SPECS = [
    dict(old='stp_4d3ceb33-1159-48d5-9a8b-d1dd429423f6', title='p++로 포인터를 다음 원소로 옮기세요', language='c',
         objectives=['포인터에 1을 더하면 주소가 원소 하나만큼 옮겨 다음 원소를 가리키는 것을 써서 확인해요.'],
         core_flow='p가 첫 원소를 가리키면 3이다. printf 앞에 p++;를 써서 다음 원소 7을 읽는다. 채점은 다른 배열로 실행한다.',
         goal='p는 배열 values의 첫 원소를 가리켜요. `p++`는 p가 가리키는 주소를 원소 하나 크기만큼 옮겨요.\n\n'
              '주석 아래에 p를 다음 원소로 한 칸 옮기는 줄을 쓰세요. 채점은 다른 배열로도 실행해요.\n\n'
              + todo(RUN, '주석 아래에 `p++;`를 쓰세요.', '코드 실행을 눌러 7이 나오는지 확인하세요.', SUB),
         starter_code=m1, solution=m1_sol, tests=[{'input': '', 'expected': '7'}],
         variations=[{'values': {'values': '{5, 1, 8}'}, 'expected': '1'}, {'values': {'values': '{0, -4}'}, 'expected': '-4'}],
         narration=k1.actions, review={k1.actions[-1]['text']: '실제 값으로 주소 이동과 값 더하기를 구별해요.'},
         reject=[([['    p++;\n    printf("%d\\n", *p);\n', '    printf("%d\\n", *p + 1);\n']], 'Adding one to the value'),
                 ([['    printf("%d\\n", *p);\n', '    printf("7\\n");\n']], 'Typing the value')],
         accept=[([['    p++;\n', '    p = p + 1;\n']], 'p = p + 1')]),
    dict(old='stp_326e20d4-d68b-4e5f-a82e-9aa6f543e783', title='n + sum(n - 1)로 돌아오며 더하세요', language='c',
         objectives=['재귀 호출의 반환값을 받아 누적하는 식을 직접 써요.'],
         core_flow='n만 돌려주면 3이다. n + sum(n - 1)로 고쳐 3 + 2 + 1 + 0인 6을 확인한다. 채점은 다른 count로 실행한다.',
         goal='`조건 ? 값1 : 값2`는 조건이 참이면 값1, 거짓이면 값2가 되는 C의 삼항 연산자예요. sum은 n이 0이면 0을 돌려줘요.\n\n'
              '함수를 고쳐 n이 0이 아니면 n과 sum(n - 1)을 더해 돌려주세요. 채점은 다른 count로도 실행해요.\n\n'
              + todo(RUN, '`: n; }`을 `: n + sum(n - 1); }`로 고치세요.', '코드 실행을 눌러 6이 나오는지 확인하세요.', SUB),
         starter_code=m2, solution=m2_sol, tests=[{'input': '', 'expected': '6'}],
         variations=[{'values': {'count': '5'}, 'expected': '15'}, {'values': {'count': '0'}, 'expected': '0'}],
         narration=k2.actions, review={k2.actions[-1]['text']: '멈춤 조건의 실제 역할을 말해요.'},
         reject=[([['n + sum(n - 1); }', 'n + (n - 1); }']], 'One step only'), ([['    printf("%d\\n", sum(count));\n', '    printf("6\\n");\n']], 'Typing the sum')],
         accept=[([['int sum(int n) { return n == 0 ? 0 : n + sum(n - 1); }\n', 'int sum(int n) {\n    if (n == 0) return 0;\n    return n + sum(n - 1);\n}\n']], 'if statement')]),
    dict(old='stp_43d45dac-fcc9-4746-9568-015cda569df9', title='static count로 생성 횟수를 함께 쓰세요', language='java',
         objectives=['static 필드는 클래스에 하나라 모든 객체가 공유하고, 일반 필드는 객체마다 따로임을 써서 확인해요.'],
         core_flow='count가 객체 필드면 1:3이다. static을 붙여 두 생성이 같은 count를 늘린 2:3을 확인한다. 채점은 처음 count와 qty를 바꿔 실행한다.',
         goal='같은 보고 객체를 두 개 만들어요. 생성 횟수는 모든 객체가 함께 쓰고, 수량은 객체마다 따로 둬요. `static` 필드는 클래스에 하나만 있어요.\n\n'
              'count 줄을 고쳐 생성 횟수를 모든 보고 객체가 함께 쓰게 하세요. 채점은 처음 count와 qty를 바꿔서도 실행해요.\n\n'
              + todo(RUN, '`int count = 0;`을 `static int count = 0;`으로 고치세요.', '코드 실행을 눌러 2:3이 나오는지 확인하세요.', SUB),
         starter_code=m3, solution=m3_sol, tests=[{'input': '', 'expected': '2:3'}],
         variations=[{'values': {'count': '10'}, 'expected': '12:3'}, {'values': {'qty': '5'}, 'expected': '2:5'}],
         narration=k3.actions, review={k3.actions[-1]['text']: '실제 출력이 바뀌는 흔한 실수예요.'},
         reject=[([['    static int count = 0;\n', '    int count = 0;\n']], 'Instance field'),
                 ([['        System.out.println(first.count + ":" + first.qty);\n', '        System.out.println("2:3");\n']], 'Typing the result')],
         accept=[([['        System.out.println(first.count + ":" + first.qty);\n', '        System.out.println(Report.count + ":" + first.qty);\n']], 'Reading through the class name')]),
    dict(old='stp_87b6c04a-c073-41ca-afa5-94c1296ca76c', title='Child에 read()를 재정의해 extra를 돌려주세요', language='java',
         objectives=['상위 타입 변수로 불러도 실제 객체의 재정의한 메서드가 실행되는 것을 써서 확인해요.'],
         core_flow='Child에 read가 없으면 Report의 3이다. @Override int read() { return extra; }를 써서 9를 확인한다. 채점은 다른 extra로 실행한다.',
         goal='`Report report = new Child();`로 같은 보고를 상위 타입으로 읽어요. 하위 클래스가 이름과 매개변수가 같은 메서드를 다시 정의하면(재정의) 실제 객체의 메서드가 실행돼요.\n\n'
              '클래스 안에 상위의 read()를 재정의해 extra를 돌려주는 메서드를 쓰세요. 채점은 다른 extra로도 실행해요.\n\n'
              + todo(RUN, 'Child 안에 `@Override int read() { return extra; }`를 쓰세요.', '코드 실행을 눌러 9가 나오는지 확인하세요.', SUB),
         starter_code=m4, solution=m4_sol, tests=[{'input': '', 'expected': '9'}],
         variations=[{'values': {'extra': '4'}, 'expected': '4'}, {'values': {'extra': '-1'}, 'expected': '-1'}],
         narration=k4.actions, review={k4.actions[-1]['text']: '재정의와 새 메서드의 실제 차이를 말해요.'},
         reject=[([['    @Override int read() { return extra; }\n', '    int read(int x) { return extra; }\n']], 'Overloading instead of overriding'),
                 ([['        System.out.println(report.read());\n', '        System.out.println(9);\n']], 'Typing the value')],
         accept=[([['    @Override int read() { return extra; }\n', '    int read() { return extra; }\n']], 'Override without the annotation')]),
    code_step('stp_2bb502e2-2f32-4ae1-ab12-e0749ab5b802', '안쪽 목록까지 복사해 a를 지키세요', '바깥만 복사한 목록은 안쪽 목록을 함께 쓰는 것을 확인하고 안쪽까지 복사해요.',
              'a[:]는 안쪽 목록을 함께 써서 a도 8이다. [row[:] for row in a]로 고쳐 a의 3이 그대로인지 확인한다. 채점은 다른 목록과 값으로 실행한다.',
              '보고 목록 a의 안쪽에 목록이 있어요. `a[:]`는 바깥 목록만 복사하고 안쪽 목록은 함께 써요.',
              'b 줄을 고쳐 b를 바꿔도 a가 그대로이게 안쪽 목록까지 복사하세요. 채점은 다른 목록과 값으로도 실행해요.',
              [RUN, '`b = a[:]`를 `b = [row[:] for row in a]`로 고치세요.', '코드 실행을 눌러 a가 그대로인지 확인하세요.', SUB],
              m5, m5_sol, k5, {k5.actions[-1]['text']: '실제 Python 동작을 정확히 말해요.'}, cases=[{'a': [[1, 2], [9]], 'new': 0}, {'a': [[7]], 'new': -1}],
              reject=[([['b = [row[:] for row in a]\n', 'b = list(a)\n']], 'Shallow list()'), ([['print(a[0][0])\n', 'print(3)\n']], 'Typing the value')],
              accept=[([['b = [row[:] for row in a]\n', 'import copy\nb = copy.deepcopy(a)\n']], 'deepcopy')]),
    code_step('stp_a556dfeb-8dcf-4945-ba16-aa0f2052406d', '//와 %로 Python의 몫과 나머지를 구하세요', 'Python의 //는 아래쪽으로 내리고 %는 나누는 수의 부호를 따르는 것을 써서 확인해요.',
              'int(total / size)는 0 쪽으로 버려 -2 -1이다. total // size와 total % size로 고쳐 -3 1을 확인한다. 채점은 다른 수로 실행한다.',
              'Python의 `//`는 몫을 아래쪽 정수로 내림하고, `%`는 몫 × 나누는 수 + 나머지 = 원래 수가 되도록 나머지를 정해요. 그래서 나머지는 나누는 수와 같은 부호예요.',
              '두 줄을 고쳐 Python의 몫 연산자 //와 나머지 연산자 %로 계산하세요. 채점은 다른 수로도 실행해요.',
              [RUN, '`q = int(total / size)`를 `q = total // size`로 고치세요.', '`r = total - q * size`를 `r = total % size`로 고치세요.', '코드 실행을 눌러 -3 1이 나오는지 확인하세요.', SUB],
              m6, m6_sol, k6, {k6.actions[-1]['text']: '실제 Python 규칙을 정확히 말해요.'}, cases=[{'total': -7, 'size': 3}, {'total': 9, 'size': 4}],
              reject=[([['q = total // size\nr = total % size\n', 'q = int(total / size)\nr = total - q * size\n']], 'Truncating toward zero'),
                      ([['print(q, r)\n', 'print(-3, 1)\n']], 'Typing the numbers')],
              accept=[([['q = total // size\nr = total % size\n', 'q, r = divmod(total, size)\n']], 'divmod')]),
    sql_step('stp_f74ad57d-7a8e-40fe-9340-839600210433', 'COUNT(qty)로 값이 있는 행만 세세요', 'COUNT(열)이 NULL인 행을 빼고 세는 것을 써서 확인해요.',
             'COUNT(*)는 NULL 행까지 3이다. COUNT(qty)로 고쳐 2를 확인한다. 채점은 NULL과 0이 섞인 다른 표로 실행한다.',
             '수량은 2, NULL, 4예요. `COUNT(*)`는 모든 행을, `COUNT(qty)`는 qty에 값이 있는 행만 세요.',
             '질의를 고쳐 qty에 값이 있는 행만 세세요. 채점은 다른 표로도 실행해요.', '`COUNT(*)`를 `COUNT(qty)`로 고치세요.',
             Q_BASE, (Q_V1, Q_V2), m7, m7_sol, k7, {k7.actions[-1]['text']: 'NULL과 0의 실제 차이를 말해요.'},
             [([['SELECT COUNT(qty) AS n FROM stock;', 'SELECT COUNT(*) AS n FROM stock;']], 'Counting every row'), ([['SELECT COUNT(qty) AS n FROM stock;', 'SELECT 2 AS n;']], 'Typing the count')],
             [([['SELECT COUNT(qty) AS n FROM stock;', 'SELECT COUNT(*) AS n FROM stock WHERE qty IS NOT NULL;']], 'Filtering NULL first')]),
    sql_step('stp_17f3de4c-d014-4fc7-9f99-9833a7ae0555', 'LEFT JOIN으로 주문 없는 상품도 남기세요', 'LEFT JOIN이 짝이 없는 왼쪽 행도 남기고 짝이 여러 개면 행이 늘어나는 것을 써서 확인해요.',
             'JOIN은 짝이 맞는 2행이다. LEFT JOIN으로 고쳐 주문 없는 상품까지 3행을 확인한다. 채점은 다른 상품·주문 표로 실행한다.',
             '상품 A·B가 있고 주문 두 개는 모두 A예요. `JOIN`은 짝이 맞는 행만 남기고, `LEFT JOIN`은 왼쪽 상품을 모두 남겨요. 주문이 여러 개인 상품은 주문 수만큼 행이 생겨요.',
             '질의를 고쳐 주문이 없는 상품도 한 행으로 남겨 전체 행을 세세요. 채점은 다른 표로도 실행해요.', '`JOIN`을 `LEFT JOIN`으로 고치세요.',
             J_BASE, (J_V1, J_V2), m8, m8_sol, k8, {k8.actions[-1]['text']: 'LEFT JOIN의 실제 행 수 규칙을 말해요.'},
             [([['\nLEFT JOIN orders', '\nJOIN orders']], 'Inner join'), ([['SELECT COUNT(*) AS n FROM product p\nLEFT JOIN orders o ON p.id = o.product_id;', 'SELECT 3 AS n;']], 'Typing the count')],
             [([['SELECT COUNT(*) AS n FROM product p\nLEFT JOIN orders o ON p.id = o.product_id;', 'SELECT COUNT(*) AS n FROM orders o\nRIGHT JOIN product p ON p.id = o.product_id;']], 'RIGHT JOIN from the other side')]),
    sql_step('stp_aa7c3968-df66-48e4-9085-b7b9ee6bf693', 'HAVING으로 합계가 3을 넘는 분류만 세세요', '묶은 뒤의 합계 조건은 HAVING으로 걸러야 함을 써서 확인해요.',
             'HAVING이 없으면 분류 2개를 모두 센다. GROUP BY 뒤에 HAVING SUM(qty) > 3을 더해 1을 확인한다. 채점은 다른 분류 표로 실행한다.',
             '`FROM (SELECT …) AS totals`처럼 FROM 뒤 괄호 안의 질의 결과를 하나의 표처럼 쓰는 것을 파생 테이블이라고 해요. 바깥 질의는 그 표의 행 수, 곧 남은 분류 수를 세요.',
             '안쪽 질의에 HAVING을 더해 수량 합계가 3을 넘는 분류만 남기세요. 채점은 다른 표로도 실행해요.', '`GROUP BY category` 뒤에 `HAVING SUM(qty) > 3`을 쓰세요.',
             G_BASE, (G_V1, G_V2), m9, m9_sol, k9, {k9.actions[-1]['text']: 'WHERE와 HAVING의 실제 차이를 말해요.'},
             [([[' GROUP BY category HAVING SUM(qty) > 3\n', ' WHERE qty > 3\n GROUP BY category\n']], 'Row filter instead of the sum'),
              ([[' GROUP BY category HAVING SUM(qty) > 3\n', ' GROUP BY category HAVING COUNT(*) > 1\n']], 'Counting rows instead of summing')],
             [([[' GROUP BY category HAVING SUM(qty) > 3\n', ' GROUP BY category HAVING SUM(qty) >= 4\n']], 'Integer bound >= 4')]),
    code_step('stp_bcbe58d4-35f4-4f8d-b899-992f20c12b4c', '안쪽 목록 복사와 None을 뺀 개수를 함께 맞추세요', '참조 공유와 NULL 집계를 서로 다른 근거로 코드에 써요.',
              '처음 코드는 5 5와 3이다. 안쪽 목록까지 복사하고 None이 아닌 값만 세어 2 5와 2를 확인한다. 채점은 다른 목록·값과 0이 섞인 목록으로 실행한다.',
              '참조 공유와 NULL 집계를 서로 다른 근거로 코드에 써요.\n\nrows의 바깥만 복사하면 안쪽 목록을 함께 써요. qty의 None은 SQL의 NULL과 같은 빈 값이고, `COUNT(qty)`는 NULL만 빼고 세요. 0은 값이에요.',
              '두 주석의 지시대로 고치세요. 채점은 다른 목록과 값으로도 실행해요.',
              ['코드 실행을 눌러 수정 전 결과를 확인하세요.', '`copy = rows[:]`를 `copy = [row[:] for row in rows]`로 고치세요.',
               '`count = len(qty)`를 `count = sum(1 for value in qty if value is not None)`으로 고치세요.', '다시 실행해 결과를 확인하고 작성한 코드를 제출하세요.'],
              m15, m15_sol, k15, {k15.actions[-1]['text']: '0을 빼 버리는 흔한 실수와 실제 결과를 말해요.'},
              cases=[{'rows': [[1], [9]], 'qty': [None, None, 4], 'added': 0}, {'rows': [[0, 1]], 'qty': [0, 0], 'added': 5}],
              reject=[([['count = sum(1 for value in qty if value is not None)\n', 'count = len([value for value in qty if value])\n']], 'Dropping zeros'),
                      ([['copy = [row[:] for row in rows]\n', 'copy = list(rows)\n']], 'Shallow copy')],
              accept=[([['count = sum(1 for value in qty if value is not None)\n', 'count = len(qty) - qty.count(None)\n']], 'Subtracting the None count')]),
]
