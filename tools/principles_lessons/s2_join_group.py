"""Observe relation cardinality, missing rows and aggregation on PostgreSQL."""
from sql_lab import sql_step, sql_lesson, unit

SEED = '''CREATE TABLE member(id INT PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE orders(id INT PRIMARY KEY, member_id INT REFERENCES member(id), amount INT NOT NULL);
INSERT INTO member VALUES(1,'A'),(2,'B'),(3,'C');
INSERT INTO orders VALUES(10,1,10),(11,1,20),(12,2,0);
'''


def step(slug, title, concept, intro, know, starter, solution, expected, old, result, caution, **extra):
    return sql_step(slug=slug, title=title, concept=concept, intro=intro, know=know,
                    before=extra.pop('before', SEED), starter=starter, solution=solution,
                    expected=expected, first_output=old, result=result, caution=caution, **extra)

S1 = step('join-condition', '주문을 실제 회원과만 연결하세요', 'JOIN 조건이 두 표에서 어떤 행을 짝지을지 정한다는 것을 이해해요.',
          '회원은 세 명, 주문은 세 건이에요. 이름과 주문을 모두 조합하면 주문이 아홉 번 나와요.',
          '표를 나누면 이름을 한 번만 저장해요. 다시 조회할 때는 orders.member_id와 member.id의 관계로 연결해야 해요. 행 번호나 나열 순서는 관계가 아니에요.',
          "SELECT m.name || ':' || o.id FROM member m CROSS JOIN orders o ORDER BY o.id,m.id;\n",
          "SELECT m.name || ':' || o.id FROM member m JOIN orders o ON o.member_id=m.id ORDER BY o.id,m.id;\n",
          'A:10\nA:11\nB:12', '주문 하나가 세 회원에게 붙어요. 두 표의 관계를 제한하지 않았어요.',
          '10번과 11번은 A, 12번은 B에게만 연결돼요.',
          '조심하세요. m.id=o.id는 주문 번호와 회원 번호를 비교해요. 서로 다른 식별자예요.')

S2 = step('missing-member', '주문이 없는 회원도 남기세요', 'LEFT JOIN의 보존하는 쪽과 NULL 확장을 이해해요.',
          'C도 회원인데 주문 목록 화면에서 사라져요. 주문이 없는 회원은 없음으로 보여야 해요.',
          'INNER JOIN은 짝이 있는 행만 남겨요. LEFT JOIN은 왼쪽 행을 보존하고 오른쪽 짝이 없으면 NULL을 붙여요. COALESCE는 표시할 대체 값을 골라요.',
          "SELECT m.name || ':' || COALESCE(o.id::text,'없음') FROM member m JOIN orders o ON o.member_id=m.id ORDER BY m.id,o.id;\n",
          "SELECT m.name || ':' || COALESCE(o.id::text,'없음') FROM member m LEFT JOIN orders o ON o.member_id=m.id ORDER BY m.id,o.id;\n",
          'A:10\nA:11\nB:12\nC:없음', 'A와 B만 나와요. C는 짝지을 주문이 없어요.',
          'C:없음이 마지막에 보여요. 회원 행은 보존됐고 주문 번호가 NULL이에요.',
          '조심하세요. orders를 왼쪽에 두면 주문을 보존해요. 이 화면에서 빠지면 안 되는 것은 회원이에요.')

S3 = step('count-null', '주문 없는 회원의 주문 수를 0으로 세세요', 'COUNT(*)와 COUNT(열)이 세는 대상의 차이를 이해해요.',
          'LEFT JOIN으로 C를 남겼더니 주문 수도 1로 나와요. 화면의 한 행과 실제 주문 한 건은 달라요.',
          'COUNT(*)는 NULL로 확장된 행도 세어요. COUNT(o.id)는 NULL이 아닌 주문 번호만 세어요. 기본 키 id는 실제 주문이면 NULL일 수 없어요.',
          "SELECT m.name || ':' || COUNT(*) FROM member m LEFT JOIN orders o ON o.member_id=m.id GROUP BY m.id,m.name ORDER BY m.id;\n",
          "SELECT m.name || ':' || COUNT(o.id) FROM member m LEFT JOIN orders o ON o.member_id=m.id GROUP BY m.id,m.name ORDER BY m.id;\n",
          'A:2\nB:1\nC:0', 'C:1이에요. 실제 주문 대신 NULL을 붙인 행 하나를 셌어요.',
          'C:0이에요. B의 금액 0원 주문은 번호가 있으므로 한 건으로 세어요.',
          '조심하세요. 금액이 0인 주문도 주문이에요. amount > 0으로 세면 그 주문을 빼요.')

S4 = step('on-versus-where', '유료 주문이 없는 회원도 집계에 남기세요', 'ON의 짝짓기 조건과 WHERE의 결과 제거 조건을 구별해요.',
          '유료 주문 건수를 세려 해요. WHERE amount>0을 붙이자 B와 C가 모두 사라져요.',
          'ON은 오른쪽에서 짝지을 대상을 정해요. WHERE는 JOIN 결과를 만든 뒤 행을 거르므로 NULL 확장된 행도 제거할 수 있어요.',
          "SELECT m.name || ':' || COUNT(o.id) FROM member m LEFT JOIN orders o ON o.member_id=m.id WHERE o.amount>0 GROUP BY m.id,m.name ORDER BY m.id;\n",
          "SELECT m.name || ':' || COUNT(o.id) FROM member m LEFT JOIN orders o ON o.member_id=m.id AND o.amount>0 GROUP BY m.id,m.name ORDER BY m.id;\n",
          'A:2\nB:0\nC:0', 'A:2만 나와요. WHERE가 B의 0원 행과 C의 NULL 행을 지웠어요.',
          'A:2, B:0, C:0이에요. 유료 주문만 짝짓고 회원은 남겼어요.',
          '조심하세요. WHERE에 OR o.id IS NULL만 더하면 C는 돌아와도 B는 사라져요. B에는 이미 0원 주문이 짝지어졌어요.')

S5 = step('join-multiplication', '두 관계를 연결해도 주문 합계를 두 번 세지 마세요', '일대다 관계를 두 번 JOIN할 때 행이 늘어나는 원리를 이해해요.',
          'A는 주문 두 건과 태그 두 개가 있어요. 두 표를 한꺼번에 연결하면 주문 금액이 두 배로 나와요.',
          '회원당 주문 N개와 태그 M개를 함께 연결하면 N×M행이 돼요. 먼저 주문을 회원당 한 행으로 집계하고 태그 집계와 연결하세요. SUM(DISTINCT amount)는 같은 금액의 다른 주문도 합쳐 버려요.',
          "SELECT m.name || ':' || COALESCE(SUM(o.amount),0) FROM member m LEFT JOIN orders o ON o.member_id=m.id LEFT JOIN tag t ON t.member_id=m.id GROUP BY m.id,m.name ORDER BY m.id;\n",
          "WITH totals AS (SELECT member_id,SUM(amount) AS total FROM orders GROUP BY member_id) SELECT m.name || ':' || COALESCE(x.total,0) FROM member m LEFT JOIN totals x ON x.member_id=m.id ORDER BY m.id;\n",
          'A:30\nB:0\nC:0', 'A:60이에요. 주문 금액 10과 20이 태그 수만큼 두 번 더해졌어요.',
          'A:30이에요. 주문을 회원당 한 행으로 만든 뒤 연결했어요.',
          '조심하세요. SUM(DISTINCT amount)는 행 중복이 아니라 금액 중복을 없애요. 같은 금액인 별도 주문을 놓쳐요.',
          before=SEED+"CREATE TABLE tag(member_id INT, label TEXT); INSERT INTO tag VALUES(1,'vip'),(1,'mail');\n",
          variants=[dict(files={'before.sql': SEED.replace('(11,1,20)', '(11,1,10)')+"CREATE TABLE tag(member_id INT,label TEXT); INSERT INTO tag VALUES(1,'x'),(1,'y');\n"},
                         expected='A:20\nB:0\nC:0')])

START = "SELECT m.name || ':' || COUNT(*) || ':' || SUM(o.amount) FROM member m JOIN orders o ON o.member_id=m.id WHERE o.amount>0 GROUP BY m.id,m.name ORDER BY m.id;\n"
SOLUTION = "SELECT m.name || ':' || COUNT(o.id) || ':' || COALESCE(SUM(o.amount),0) FROM member m LEFT JOIN orders o ON o.member_id=m.id AND o.amount>0 GROUP BY m.id,m.name ORDER BY m.id;\n"
S6 = step('final-report', '모든 회원의 유료 주문 수와 합계를 구현하세요', '보존할 행·집계 대상·NULL 처리를 함께 설계해요.',
          '관리 화면에는 모든 회원이 있어야 해요. 유료 주문이 없으면 건수와 합계는 모두 0이에요.',
          '기준 표는 member예요. 유료 주문만 연결한 뒤 주문 번호를 세고 금액을 더하세요. SUM에 더할 값이 없으면 NULL이므로 화면의 0으로 바꿔야 해요.',
          START, SOLUTION, 'A:2:30\nB:0:0\nC:0:0', 'A:2:30만 보여요. 집계 대상과 보여 줄 회원을 함께 걸렀어요.',
          '회원 세 명이 모두 나와요. 주문이 없는 C와 무료 주문만 있는 B는 각각 0:0이에요.',
          '조심하세요. COALESCE만 붙여도 사라진 회원은 돌아오지 않아요. 행을 보존하는 JOIN부터 확인하세요.',
          variants=[dict(files={'before.sql': SEED.replace('(11,1,20)', '(11,3,7)')}, expected='A:1:10\nB:0:0\nC:1:7')])

LESSON = sql_lesson(key='sql-join-group', folder='sql_join_group', pilot='쥬', title='JOIN·집계 · 사라진 행과 늘어난 합계를 찾아요',
                    objectives=['관계로 행을 연결하고 보존할 대상을 정해요.', 'NULL과 실제 주문을 구분해 집계해요.', 'JOIN의 행 수 증가를 이해하고 정확한 보고서를 구현해요.'],
                    units=[unit('행을 짝짓고 남기기', 'JOIN 조건과 보존하는 쪽을 이해해요.', [S1,S2]),
                           unit('NULL과 집계', '건수와 필터의 적용 지점을 구별해요.', [S3,S4]),
                           unit('관계가 늘어나는 보고서', '집계 전 행 수를 따져 중복 합산을 막아요.', [S5,S6])],
                    final_slug='final-report')
