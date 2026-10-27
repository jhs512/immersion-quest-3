"""MySQL schema invariants: protect data regardless of which client writes it."""
from sql_lab import sql_step, sql_lesson, unit


def constraint(slug, title, concept, starter, solution, attempts, query, expected, old, why, caution):
    intro = {
        'not-null': '첫 INSERT는 이름 우유와 NULL인 두 행을 함께 보내요. 다음 INSERT는 빵만 따로 보내요.',
        'unique': '서로 다른 두 클라이언트가 같은 lee 로그인 이름을 보내요. kim은 다른 이름이에요.',
        'primary-key': '1번 회원을 두 번 저장하고 번호 없는 회원도 저장하려 해요.',
        'check': '서로 다른 클라이언트가 잔액 0, -1, 7인 행을 보내요. 음수 잔액만 막아야 해요.',
    }[slug]
    result = {
        'not-null': '첫 INSERT 전체가 거절돼요. 뒤에서 따로 보낸 빵 한 행만 남아 두 수가 모두 1이에요.',
        'unique': '두 번째 lee가 거절돼요. kim과 lee가 각각 한 행씩 남아요.',
        'primary-key': '중복 1번과 NULL 번호가 거절돼요. 처음 1번 우유만 남아요.',
        'check': '음수 -1만 거절돼요. 0원과 7원인 두 행은 남아요.',
    }[slug]
    return sql_step(slug=slug, title=title, concept=concept,
                    intro=intro,
                    know=why, starter=starter, solution=solution,
                    after=attempts + '\n' + query + '\n', expected=expected,
                    first_output=old, result=result,
                    caution=caution, engine='mysql')

N = constraint('not-null', '이름이 없는 회원을 DB에서 거절하세요', 'NOT NULL과 빈 문자열의 차이를 이해해요.',
               'CREATE TABLE member(id INT, name VARCHAR(30));\n',
               'CREATE TABLE member(id INT, name VARCHAR(30) NOT NULL);\n',
               "INSERT INTO member VALUES (1,'우유'),(2,NULL);\nINSERT INTO member VALUES (3,'빵');",
               'SELECT COUNT(*), COUNT(name) FROM member;', '1\t1',
               '전체는 3행인데 이름은 2개예요. NULL은 아직 허용돼요.',
               'NULL은 값이 없다는 뜻이에요. COUNT(name)은 NULL을 세지 않아요. NOT NULL은 빈 문자열을 막는 규칙은 아니에요. MySQL의 이 실습은 엄격한 기본 SQL 모드예요.',
               '조심하세요. 여러 행을 한 INSERT로 보내면 한 행의 오류 때문에 그 문장 전체가 거절돼요. 뒤의 별도 INSERT와 구분하세요.')

U = constraint('unique', '같은 로그인 이름이 두 번 저장되지 않게 하세요', 'UNIQUE가 여러 클라이언트의 중복 저장을 막는다는 것을 이해해요.',
               'CREATE TABLE member(id INT, login VARCHAR(30) NOT NULL);\n',
               'CREATE TABLE member(id INT, login VARCHAR(30) NOT NULL UNIQUE);\n',
               "INSERT INTO member VALUES (1,'lee');\nINSERT INTO member VALUES (2,'lee');\nINSERT INTO member VALUES (3,'kim');",
               'SELECT login, COUNT(*) FROM member GROUP BY login ORDER BY login;', 'kim\t1\nlee\t1',
               'lee가 두 행에 저장돼요. 화면에서 검사하지 않는 다른 클라이언트도 쓰고 있어요.',
               '화면의 중복 검사만으로 모든 쓰기 경로를 보호하지 못해요. UNIQUE는 저장하는 DB에서 같은 값의 중복을 거절해요.',
               '조심하세요. id에만 UNIQUE를 붙이면 로그인 이름 중복은 그대로 허용돼요.')

P = constraint('primary-key', '회원 번호가 없거나 겹치는 행을 막으세요', 'PRIMARY KEY는 행을 식별하고 중복과 NULL을 막는다는 것을 이해해요.',
               'CREATE TABLE member(id INT, name VARCHAR(30));\n',
               'CREATE TABLE member(id INT PRIMARY KEY, name VARCHAR(30));\n',
               "INSERT INTO member VALUES (1,'우유');\nINSERT INTO member VALUES (1,'빵');\nINSERT INTO member VALUES (NULL,'귤');",
               'SELECT id, name FROM member ORDER BY id;', '1\t우유',
               '회원 번호 1이 두 번 나오고 번호가 없는 행도 저장돼요.',
               '기본 키는 행을 구별하는 기준이에요. PRIMARY KEY는 그 열을 UNIQUE이면서 NOT NULL로 만들어요. 이름이 같을 수 있으니 이름을 키로 정하지 않아요.',
               '조심하세요. 이름에 기본 키를 붙이면 동명이인을 거절해요. 이 문제에서 식별자는 회원 번호예요.')

F = sql_step(slug='foreign-key', title='없는 회원의 주문을 저장하지 못하게 하세요', concept='외래 키가 두 표 사이의 존재 규칙을 지켜요.',
             intro='회원 표에는 1번만 있어요. 다른 클라이언트가 99번 회원의 주문을 보내요.',
             know='FOREIGN KEY는 참조할 행이 존재해야 한다는 규칙이에요. 참조 번호로 다른 표를 조회하는 것과 잘못된 참조 번호의 저장 자체를 거절하는 것은 다른 일이에요.',
             before="CREATE TABLE member(id INT PRIMARY KEY);\nINSERT INTO member VALUES(1);\n",
             starter='CREATE TABLE orders(id INT PRIMARY KEY, member_id INT NOT NULL);\n',
             solution='CREATE TABLE orders(id INT PRIMARY KEY, member_id INT NOT NULL, FOREIGN KEY(member_id) REFERENCES member(id));\n',
             after='INSERT INTO orders VALUES(10,1);\nINSERT INTO orders VALUES(11,99);\nSELECT id, member_id FROM orders ORDER BY id;\n',
             expected='10\t1', first_output='99번 회원의 주문도 저장돼요. 회원이 없는 주문이 생겼어요.',
             result='외래 키 오류가 나고 10번 주문만 남아요.',
             caution='조심하세요. 주문 번호와 회원 번호는 다른 역할이에요. member_id가 참조할 대상은 member.id예요.', engine='mysql')

C = constraint('check', '금액이 음수인 행을 DB에서 막으세요', 'CHECK는 저장되는 각 행의 값 범위를 보호해요.',
               'CREATE TABLE wallet(id INT PRIMARY KEY, balance INT NOT NULL);\n',
               'CREATE TABLE wallet(id INT PRIMARY KEY, balance INT NOT NULL CHECK(balance >= 0));\n',
               'INSERT INTO wallet VALUES(1,0);\nINSERT INTO wallet VALUES(2,-1);\nINSERT INTO wallet VALUES(3,7);',
               'SELECT id, balance FROM wallet ORDER BY id;', '1\t0\n3\t7',
               '잔액 -1인 행도 남아요. NOT NULL은 음수를 막지 않아요.',
               'NOT NULL은 값의 존재만 검사해요. CHECK는 각 행의 조건을 검사해요. MySQL 8.4는 CHECK를 실제로 적용해요.',
               '조심하세요. 0도 허용되는 잔액이에요. > 0으로 검사하면 정상인 0원을 거절해요.')

FINAL = sql_step(slug='final-reservation', title='다른 클라이언트가 와도 예약 규칙을 지키세요',
                 concept='기본 키·외래 키·조합 UNIQUE·CHECK를 서로 다른 규칙에 적용해요.',
                 intro='방은 여러 시간에 예약할 수 있어요. 같은 방과 같은 시간의 중복 예약만 막아야 해요.',
                 know='UNIQUE(room_id, slot)은 두 값의 조합을 검사해요. room_id만 UNIQUE면 다른 시간의 정상 예약까지 막아요. 사람 수와 방 존재 규칙은 별도로 선언해요.',
                 before='CREATE TABLE room(id INT PRIMARY KEY);\nINSERT INTO room VALUES(1),(2);\n',
                 starter='CREATE TABLE reservation(id INT PRIMARY KEY, room_id INT NOT NULL, slot INT NOT NULL, people INT NOT NULL);\n',
                 solution='''CREATE TABLE reservation(
    id INT PRIMARY KEY,
    room_id INT NOT NULL,
    slot INT NOT NULL,
    people INT NOT NULL CHECK(people > 0),
    UNIQUE(room_id, slot),
    FOREIGN KEY(room_id) REFERENCES room(id)
);
''',
                 after='''INSERT INTO reservation VALUES(1,1,9,2);
INSERT INTO reservation VALUES(2,1,9,3);
INSERT INTO reservation VALUES(3,1,10,1);
INSERT INTO reservation VALUES(4,99,9,1);
INSERT INTO reservation VALUES(5,2,9,0);
SELECT id, room_id, slot, people FROM reservation ORDER BY id;
''', expected='1\t1\t9\t2\n3\t1\t10\t1',
                 first_output='다섯 예약이 모두 저장돼요. 같은 시간의 중복, 없는 방, 0명 예약도 남아요.',
                 result='1번과 3번 예약만 남아요. 같은 방의 다른 시간은 허용되고 잘못된 쓰기는 DB가 거절해요.',
                 caution='조심하세요. room_id만 UNIQUE로 만들면 그 방을 다시는 예약할 수 없어요. 시간까지 묶어 비교하세요.',
                 engine='mysql', rejects=[([('UNIQUE(room_id, slot)', 'UNIQUE(room_id)')], '다른 시간의 정상 예약도 거절해요.'),
                                          ([('CHECK(people > 0)', 'CHECK(people >= 0)')], '0명 예약이 남아요.')])

LESSON = sql_lesson(key='sql-tables-constraints', folder='sql_tables_constraints', pilot='제',
                    title='MySQL · 화면을 우회해도 데이터 규칙을 지켜요', engine='mysql',
                    objectives=['값이 있는 것과 올바른 값을 구분해요.', '여러 클라이언트의 쓰기를 DB 제약으로 보호해요.', '관계와 예약 정체성에 맞는 제약을 설계해요.'],
                    units=[unit('행 안의 규칙', 'NOT NULL·UNIQUE·기본 키의 서로 다른 책임을 구분해요.', [N,U,P]),
                           unit('관계와 범위', '참조 존재와 숫자 범위를 각각 보호해요.', [F,C]),
                           unit('최종 도전: 예약 저장소', '정상 예약은 허용하고 잘못된 예약만 거절해요.', [FINAL])],
                    final_slug='final-reservation',
                    sources=[('https://dev.mysql.com/doc/refman/8.4/en/constraints.html', '제약이 위반된 문장을 DB가 거절해요.', 'MySQL 8.4 공식 문서와 실제 실행을 대조해요.')])

# DDL is not transactional in MySQL. Make repeated schema experiments explicit
# in the learner's code; never silently rebuild the server/container on each run.
for task, table in [(N,'member'),(U,'member'),(P,'member'),(F,'orders'),(C,'wallet'),(FINAL,'reservation')]:
    prefix=f'-- 이 제약 비교 실험의 연습용 {table} 표만 다시 만드는 준비예요.\nDROP TABLE IF EXISTS {table};\n'
    task['starter']=prefix+task['starter']
    task['solution']=prefix+task['solution']
    preparation=f'{task["objectives"][0]} 실행할 때 보이는 DROP TABLE이 이 실험의 {table} 표만 다시 만들어요. 앞 실행의 잘못된 표에 CREATE를 덧붙이지 않고 두 제약을 같은 조건에서 비교해요. 운영 DB에서 표를 지우라는 뜻은 아니에요.'
    task['intro'].append(preparation)
    task['narration'].insert(0,('say',preparation,'text:'+preparation))
    task['review'][preparation]='반복 DDL 실험의 준비가 코드에 공개되어 있고 이 과제 표에만 적용됨을 설명해요.'
LESSON['revision']=3
LESSON['prerequisites']=['SQL 기초에서 CREATE TABLE·INSERT·조회·행 식별자와 관계를 확인했어요.', 'MySQL 실습 환경을 실행할 수 있어요.']
