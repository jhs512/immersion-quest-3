"""engineer-sql-select: 9 answer-picking steps -> query-writing steps (2026-10-29)."""
from _kit import Script, todo, sql_output

OPENING = ['이 수업에서는 SQL이 어떤 행과 열을 남기는지 질의를 직접 고쳐 가며 배워요. 조건과 NULL의 의미를 구별해요.',
           '작은 조회에서 범위·중복·조인으로 넓혀요. 하위 질의까지 직접 쓰고, 행을 바꾼 표로도 확인해요.']

PRD_SCOPE = ['두 챕터·두 단원·열한 스텝으로 같은 물건·공급처 표를 조회해요.',
             'WHERE 비교·IS NULL·AND와 OR 괄호·LIKE·BETWEEN·DISTINCT·LEFT JOIN·EXISTS·NOT EXISTS를 질의 한 곳씩 직접 써서 실행해요.']
PRD_GRADING = ['직접 쓴 질의를 실제 SQLite로 실행해 판정해요.',
               '표의 행을 바꾼 준비 자료에서도 같은 질의가 맞아야 해서, id를 적어 고르거나 결과를 글자로 적은 답은 거절해요.',
               '모든 해설의 질의 실행 결과를 실제 SQLite로 확인해요.']
PRD_NARRATION = ['준비 질의를 먼저 실행하고 조건 한 곳을 고친 뒤 다시 실행해 남은 행을 비교해요.',
                 'NULL 비교·연산자 우선순위·경계·내부 조인에서 사라지는 행·NOT IN과 NULL을 조심할 지점으로 짚어요.']

SCHEMA = ("CREATE TABLE suppliers(id INTEGER PRIMARY KEY, name TEXT NOT NULL);\n"
          "INSERT INTO suppliers VALUES(10,'north'),(20,'south'),(30,'empty');\n"
          "CREATE TABLE items(id INTEGER PRIMARY KEY, name TEXT, stock INTEGER, category TEXT, supplier INTEGER REFERENCES suppliers(id));\n")
BASE = {'setup.sql': SCHEMA + "INSERT INTO items VALUES(1,'pen',2,'A',10),(2,'book',NULL,'B',20),(3,'bag',5,'A',NULL),(4,'pen',0,'B',10);\n"}
# Changed tables for grading: other names, stocks, categories and suppliers.
V1 = {'setup.sql': SCHEMA + "INSERT INTO items VALUES(1,'pen',0,'A',10),(2,'bag',3,'B',NULL),(3,'box',NULL,'A',20),(4,'bolt',5,'C',30);\n"}
V2 = {'setup.sql': SCHEMA + "INSERT INTO items VALUES(1,'cab',7,'B',20),(2,'ball',2,'A',10),(3,'bin',6,'A',10),(4,'map',NULL,'B',NULL);\n"}


def graded(solution, *sets):
    return dict(tests=[{'input': '', 'expected': sql_output(BASE, solution)}],
                variations=[{'files': v, 'expected': sql_output(v, solution)} for v in sets])


def step(title, objectives, core_flow, goal, starter, solution, narration, review, reject, accept, sets=(V1, V2)):
    return dict(title=title, objectives=objectives, core_flow=core_flow, goal=goal, starter_code=starter, solution=solution,
                files=BASE, narration=narration.actions, review=review, reject=reject, accept=accept, **graded(solution, *sets))


s1 = '-- 이 질의에 WHERE를 더해 재고가 0보다 큰 물건만 남기세요.\nSELECT id FROM items ORDER BY id;\n'
s1_solution = '-- 이 질의에 WHERE를 더해 재고가 0보다 큰 물건만 남기세요.\n-- WHERE는 조건이 참인 행만 남겨요. NULL과 0은 0보다 크지 않아요.\nSELECT id FROM items WHERE stock > 0 ORDER BY id;\n'
n1 = (Script(s1)
      .say('SELECT는 보여 줄 열, WHERE는 남길 행이에요. 재고가 0보다 큰 행만 남겨야 해요.', 'text:FROM items 뒤에 WHERE를 더해 재고가 0보다 큰 물건만 남기세요.')
      .run('SELECT id FROM items')
      .say('1부터 4까지 모두 나와요. 아직 조건이 없어요.', 'output')
      .patch('FROM items ORDER BY', 'FROM items WHERE stock > 0 ORDER BY', 'FROM items 뒤에 WHERE stock > 0을 써요.')
      .run('SELECT id FROM items')
      .say('1과 3이에요. 재고 2와 5인 행만 남았어요.', 'output')
      .say('조심하세요. stock >= 0이면 재고 0인 ID 4도 남아요. NULL인 ID 2는 어느 쪽에서도 남지 않아요.', 'code:stock > 0'))

s2 = '-- 이 질의에 WHERE를 더해 재고를 모르는(NULL) 물건만 남기세요.\nSELECT id FROM items ORDER BY id;\n'
s2_solution = '-- 이 질의에 WHERE를 더해 재고를 모르는(NULL) 물건만 남기세요.\n-- NULL은 = 로 비교할 수 없어요. IS NULL로 물어요.\nSELECT id FROM items WHERE stock IS NULL ORDER BY id;\n'
n2 = (Script(s2)
      .say('재고를 아직 모르는 물건은 stock이 NULL이에요. IS NULL로 그 행만 남겨야 해요.', 'text:FROM items 뒤에 WHERE를 더해 재고를 모르는(NULL) 물건만 남기세요.')
      .run('SELECT id FROM items')
      .say('네 행이 모두 나와요.', 'output')
      .patch('FROM items ORDER BY', 'FROM items WHERE stock = NULL ORDER BY', '먼저 stock = NULL로 써 볼게요.')
      .run('SELECT id FROM items')
      .say('행 없음이에요. = NULL은 어떤 행에서도 참이 되지 않아요.', 'output')
      .patch('stock = NULL', 'stock IS NULL', '= NULL을 IS NULL로 고쳐요.')
      .run('SELECT id FROM items')
      .say('2예요. 재고를 모르는 book만 남았어요.', 'output')
      .say('조심하세요. 재고 0은 NULL이 아니에요. stock = 0은 ID 4를 찾아요.', 'code:stock IS NULL'))

s3 = "-- 재고가 양수이면서 분류가 A 또는 B인 물건이에요. 괄호를 더해 OR을 먼저 묶으세요.\nSELECT id FROM items WHERE stock > 0 AND category = 'A' OR category = 'B' ORDER BY id;\n"
s3_solution = "-- 재고가 양수이면서 분류가 A 또는 B인 물건이에요. 괄호를 더해 OR을 먼저 묶으세요.\n-- 괄호가 없으면 AND가 먼저 묶여 B 분류는 재고와 상관없이 남아요.\nSELECT id FROM items WHERE stock > 0 AND (category = 'A' OR category = 'B') ORDER BY id;\n"
n3 = (Script(s3)
      .say('재고가 양수이면서 분류가 A 또는 B여야 해요. OR 쪽을 괄호로 묶어야 해요.', "text:괄호를 더해 category = 'A' OR category = 'B'를 먼저 묶으세요.")
      .run('SELECT id FROM items')
      .say('1, 2, 3, 4가 모두 나와요. 재고를 모르는 2와 재고 0인 4도 B라서 남았어요.', 'output')
      .patch("AND category = 'A' OR category = 'B'", "AND (category = 'A' OR category = 'B')", 'OR로 이은 두 분류 조건을 괄호로 묶어요.')
      .run('SELECT id FROM items')
      .say('1과 3이에요. 이제 모든 행에서 재고 양수 조건이 필요해요.', 'output')
      .say('조심하세요. 괄호가 없으면 AND가 OR보다 먼저 묶여요.', "code:(category = 'A' OR category = 'B')"))

s4 = "-- 이 조건을 고쳐 이름이 b로 시작하는 물건을 고르세요.\nSELECT id FROM items WHERE name = 'b' ORDER BY id;\n"
s4_solution = "-- 이 조건을 고쳐 이름이 b로 시작하는 물건을 고르세요.\n-- %는 몇 글자든 아무 글자예요. 'b%'는 b로 시작하는 모든 이름이에요.\nSELECT id FROM items WHERE name LIKE 'b%' ORDER BY id;\n"
n4 = (Script(s4)
      .say("name = 'b'는 이름이 정확히 b인 행만 찾아요. LIKE 무늬로 b로 시작하는 이름을 골라야 해요.", 'text:조건을 고쳐 이름이 b로 시작하는 물건을 고르세요.')
      .run('SELECT id FROM items')
      .say('행 없음이에요. 이름이 b 한 글자인 물건은 없어요.', 'output')
      .patch("name = 'b'", "name LIKE 'b%'", "= 'b'를 LIKE 'b%'로 고쳐요.")
      .run('SELECT id FROM items')
      .say('2와 3이에요. b로 시작하는 book과 bag이에요.', 'output')
      .say("조심하세요. '%b%'는 b가 어디에 있든 남겨서 시작 글자 조건이 아니에요.", "code:LIKE 'b%'"))

s5 = '-- 이 조건을 BETWEEN으로 고쳐 재고가 2 이상 5 이하인 물건을 고르세요.\nSELECT id FROM items WHERE stock > 2 AND stock < 5 ORDER BY id;\n'
s5_solution = '-- 이 조건을 BETWEEN으로 고쳐 재고가 2 이상 5 이하인 물건을 고르세요.\n-- BETWEEN 2 AND 5는 양 끝 2와 5를 포함해요.\nSELECT id FROM items WHERE stock BETWEEN 2 AND 5 ORDER BY id;\n'
n5 = (Script(s5)
      .say('2 이상 5 이하는 양 끝을 포함하는 범위예요. BETWEEN으로 고쳐야 해요.', 'text:조건을 BETWEEN으로 고쳐 재고가 2 이상 5 이하인 물건을 고르세요.')
      .run('SELECT id FROM items')
      .say('행 없음이에요. 재고 2와 5는 > 2, < 5에서 모두 빠졌어요.', 'output')
      .patch('stock > 2 AND stock < 5', 'stock BETWEEN 2 AND 5', 'stock BETWEEN 2 AND 5로 고쳐요.')
      .run('SELECT id FROM items')
      .say('1과 3이에요. 경계값 2와 5도 범위에 들어가요.', 'output')
      .say('조심하세요. BETWEEN은 작은 값을 앞에 써요. BETWEEN 5 AND 2는 아무 행도 남기지 않아요.', 'code:BETWEEN 2 AND 5'))

s6 = '-- 이 질의를 고쳐 분류를 중복 없이 한 번씩만 보이세요.\nSELECT category FROM items ORDER BY category;\n'
s6_solution = '-- 이 질의를 고쳐 분류를 중복 없이 한 번씩만 보이세요.\n-- DISTINCT는 조회 결과에서 같은 값을 하나로 줄여요. 표의 행은 그대로예요.\nSELECT DISTINCT category FROM items ORDER BY category;\n'
n6 = (Script(s6)
      .say('분류가 A, B, A, B로 겹쳐요. 조회 결과에서 같은 값을 하나로 줄여야 해요.', 'text:질의를 고쳐 분류를 중복 없이 한 번씩만 보이세요.')
      .run('SELECT category FROM items')
      .say('A, A, B, B예요. 물건마다 한 줄씩 나와요.', 'output')
      .patch('SELECT category', 'SELECT DISTINCT category', 'SELECT 뒤에 DISTINCT를 써요.')
      .run('SELECT DISTINCT category')
      .say('A와 B예요. 결과의 중복만 줄었고 items 표의 행은 그대로예요.', 'output')
      .say('조심하세요. DISTINCT는 표에서 행을 지우지 않아요. 보여 주는 결과만 줄여요.', 'code:SELECT DISTINCT category'))

s7 = '-- 이 조인을 고쳐 공급처가 없는 물건도 결과에 남기세요.\nSELECT i.id, s.name FROM items i JOIN suppliers s ON i.supplier = s.id ORDER BY i.id;\n'
s7_solution = '-- 이 조인을 고쳐 공급처가 없는 물건도 결과에 남기세요.\n-- LEFT JOIN은 왼쪽 items의 행을 모두 남기고, 맞는 공급처가 없으면 NULL로 채워요.\nSELECT i.id, s.name FROM items i LEFT JOIN suppliers s ON i.supplier = s.id ORDER BY i.id;\n'
n7 = (Script(s7)
      .say('공급처가 없는 bag도 남아야 해요. 왼쪽 표의 행을 모두 남기는 조인으로 고쳐야 해요.', 'text:조인을 고쳐 공급처가 없는 물건도 결과에 남기세요.')
      .run('SELECT i.id, s.name')
      .say('1, 2, 4만 나와요. 내부 조인은 짝이 없는 bag, ID 3을 뺐어요.', 'output')
      .patch('FROM items i JOIN', 'FROM items i LEFT JOIN', 'JOIN 앞에 LEFT를 붙여요.')
      .run('SELECT i.id, s.name')
      .say('3도 NULL 공급처와 함께 남았어요.', 'output')
      .say('조심하세요. LEFT JOIN 뒤에 WHERE s.name IS NOT NULL을 쓰면 다시 내부 조인처럼 bag이 빠져요.', 'code:LEFT JOIN suppliers s'))

s8 = '-- 이 주석 아래 WHERE에 EXISTS 하위 질의를 써서 양수 재고 물건이 있는 공급처만 남기세요.\nSELECT s.id FROM suppliers s\nORDER BY s.id;\n'
s8_solution = ('-- 이 주석 아래 WHERE에 EXISTS 하위 질의를 써서 양수 재고 물건이 있는 공급처만 남기세요.\n'
               '-- 하위 질의가 행을 하나라도 돌려주면 EXISTS가 참이에요. i.supplier = s.id가 바깥 공급처와 이어요.\n'
               'SELECT s.id FROM suppliers s\nWHERE EXISTS (SELECT 1 FROM items i WHERE i.supplier = s.id AND i.stock > 0)\nORDER BY s.id;\n')
n8 = (Script(s8)
      .say('공급처마다 양수 재고 물건이 하나라도 있는지 EXISTS로 물어야 해요.', 'text:WHERE에 EXISTS 하위 질의를 써서 양수 재고 물건이 있는 공급처만 남기세요.')
      .run('SELECT s.id')
      .say('10, 20, 30이 모두 나와요. 아직 조건이 없어요.', 'output')
      .patch('SELECT s.id FROM suppliers s\n', 'SELECT s.id FROM suppliers s\nWHERE EXISTS (SELECT 1 FROM items i WHERE i.supplier = s.id AND i.stock > 0)\n',
             '하위 질의에서 바깥 공급처 s.id와 이어지고 재고가 양수인 물건을 찾아요.')
      .run('SELECT s.id', 'ORDER BY s.id;')
      .say('10이에요. 20의 book은 재고를 모르고, 30은 물건이 없어요.', 'output')
      .say('조심하세요. 하위 질의에 i.supplier = s.id가 없으면 어느 공급처든 물건이 하나만 있어도 참이 돼요.', 'code:i.supplier = s.id'))

s9 = '-- 이 질의를 NOT EXISTS로 고쳐 물건이 하나도 없는 공급처를 찾으세요.\nSELECT s.id FROM suppliers s\nWHERE s.id NOT IN (SELECT supplier FROM items)\nORDER BY s.id;\n'
s9_solution = ('-- 이 질의를 NOT EXISTS로 고쳐 물건이 하나도 없는 공급처를 찾으세요.\n'
               '-- NOT IN 목록에 NULL이 섞이면 결과가 비어요. NOT EXISTS는 이어지는 물건 행이 없는지만 물어요.\n'
               'SELECT s.id FROM suppliers s\nWHERE NOT EXISTS (SELECT 1 FROM items i WHERE i.supplier = s.id)\nORDER BY s.id;\n')
n9 = (Script(s9)
      .say('물건이 없는 공급처를 찾아야 해요. NOT IN 대신 NOT EXISTS로 고쳐야 해요.', 'text:질의를 NOT EXISTS로 고쳐 물건이 하나도 없는 공급처를 찾으세요.')
      .run('SELECT s.id', 'ORDER BY s.id;')
      .say('행 없음이에요. bag의 supplier가 NULL이라 NOT IN 목록에 NULL이 섞였어요.', 'output')
      .patch('WHERE s.id NOT IN (SELECT supplier FROM items)\n', 'WHERE NOT EXISTS (SELECT 1 FROM items i WHERE i.supplier = s.id)\n',
             'NOT EXISTS 하위 질의로 이 공급처와 이어지는 물건 행이 있는지 물어요.')
      .run('SELECT s.id', 'ORDER BY s.id;')
      .say('30이에요. 이어지는 물건이 없는 공급처만 남았어요.', 'output')
      .say('조심하세요. x NOT IN (…, NULL)은 참이 될 수 없어요. NULL과의 비교는 알 수 없음이에요.', 'code:WHERE NOT EXISTS (SELECT 1'))

SPECS = [
    dict(old='stp_e2114356-fc80-4ae9-b1f2-7b0ed97850d3', **step(
        'WHERE stock > 0으로 재고가 있는 물건만 남기세요', ['SELECT의 열과 WHERE의 행 조건을 구별해 써요.'],
        '준비 질의는 모든 id를 보인다. WHERE stock > 0을 더해 1과 3을 확인한다. 0과 NULL은 남지 않는다. 채점은 행을 바꾼 표 두 개로도 실행한다.',
        'items에서 재고가 0보다 큰 물건의 id만 보려 해요. SELECT 뒤는 보여 줄 열, WHERE 뒤는 남길 행의 조건이에요.\n\n'
        'FROM items 뒤에 WHERE를 더해 재고가 0보다 큰 물건만 남기세요. 채점은 행을 바꾼 표로도 실행해요.\n\n'
        + todo('코드 실행을 눌러 모든 id가 나오는지 확인하세요.', '`FROM items` 뒤에 `WHERE stock > 0`을 쓰세요.', '코드 실행을 눌러 1과 3만 나오는지 확인하세요.', '수정한 질의를 제출하세요.'),
        s1, s1_solution, n1,
        {'조심하세요. stock >= 0이면 재고 0인 ID 4도 남아요. NULL인 ID 2는 어느 쪽에서도 남지 않아요.': '실제 두 결과(>=0이면 4 포함, NULL은 비교 불가)를 정확히 말해요.'},
        [([['WHERE stock > 0', 'WHERE stock >= 0']], 'Including zero'), ([['WHERE stock > 0', 'WHERE id IN (1, 3)']], 'Picking ids by hand')],
        [([['WHERE stock > 0', 'WHERE NOT stock <= 0']], 'Negated comparison')])),
    dict(old='stp_1dc3a31a-949e-4939-9f93-154e00ac62d9', **step(
        'IS NULL로 재고를 모르는 물건을 찾으세요', ['NULL은 = 대신 IS NULL로 확인해요.'],
        '준비 질의는 모든 id를 보인다. stock = NULL은 행 없음, stock IS NULL로 고쳐 2를 확인한다. 채점은 행을 바꾼 표로도 실행한다.',
        'book은 재고를 아직 몰라 stock이 NULL이에요. NULL은 값이 아니라 모른다는 표시라서 `=`로 비교하면 참이 되지 않아요. `IS NULL`은 값이 NULL인지 묻는 조건이에요.\n\n'
        'FROM items 뒤에 WHERE를 더해 재고를 모르는(NULL) 물건만 남기세요. 채점은 행을 바꾼 표로도 실행해요.\n\n'
        + todo('코드 실행을 눌러 모든 id가 나오는지 확인하세요.', '`FROM items` 뒤에 `WHERE stock IS NULL`을 쓰세요.', '코드 실행을 눌러 2만 나오는지 확인하세요.', '수정한 질의를 제출하세요.'),
        s2, s2_solution, n2,
        {'조심하세요. 재고 0은 NULL이 아니에요. stock = 0은 ID 4를 찾아요.': '실제 혼동(0과 NULL)과 실제 결과를 말해요.'},
        [([['WHERE stock IS NULL', 'WHERE stock = NULL']], '= NULL is never true'), ([['WHERE stock IS NULL', 'WHERE stock = 0']], 'Zero is not unknown'),
         ([['WHERE stock IS NULL', 'WHERE id = 2']], 'Picking the id by hand')],
        [([['WHERE stock IS NULL', 'WHERE coalesce(stock, -1) = -1']], 'coalesce to a marker')])),
    dict(old='stp_aeb660c1-9763-4b34-a253-04fb6b2e61cb', **step(
        '괄호로 OR을 먼저 묶어 재고 조건을 모든 분류에 적용하세요', ['AND가 OR보다 먼저 묶이는 우선순위를 괄호로 바꿔요.'],
        "stock > 0 AND category='A' OR category='B'는 B를 재고와 상관없이 남겨 1,2,3,4다. OR 쪽을 괄호로 묶어 1,3을 확인한다. 채점은 행을 바꾼 표로도 실행한다.",
        '괄호가 없으면 AND가 OR보다 먼저 묶여요. 지금 조건은 「A이면서 재고 양수」 또는 「B」라서 B 분류는 재고와 상관없이 남아요. 원하는 것은 재고가 양수이면서 분류가 A 또는 B인 물건이에요.\n\n'
        "괄호를 더해 category = 'A' OR category = 'B'를 먼저 묶으세요. 채점은 행을 바꾼 표로도 실행해요.\n\n"
        + todo('코드 실행을 눌러 1, 2, 3, 4가 나오는지 확인하세요.', "`category = 'A' OR category = 'B'`를 괄호로 묶으세요.", '코드 실행을 눌러 1과 3이 나오는지 확인하세요.', '수정한 질의를 제출하세요.'),
        s3, s3_solution, n3,
        {'조심하세요. 괄호가 없으면 AND가 OR보다 먼저 묶여요.': '실제 SQL 우선순위를 정확히 말해요.'},
        [([["(category = 'A' OR category = 'B')", "category = 'A' OR category = 'B'"]], 'No parentheses'), ([["stock > 0 AND (category = 'A' OR category = 'B')", "id IN (1, 3)"]], 'Picking ids by hand')],
        [([["(category = 'A' OR category = 'B')", "category IN ('A', 'B')"]], 'IN list')])),
    dict(old='stp_caea3553-3477-459b-8797-b9d3ae1f4338', **step(
        "LIKE 'b%'로 b로 시작하는 이름을 고르세요", ['LIKE 무늬의 %로 시작 글자 조건을 써요.'],
        "name = 'b'는 행 없음이다. LIKE 'b%'로 고쳐 book과 bag을 확인한다. '%b%'는 가운데 b도 남긴다. 채점은 이름을 바꾼 표로도 실행한다.",
        "LIKE 무늬에서 `%`는 몇 글자든 아무 글자를 뜻해요. 그래서 `'b%'`는 b로 시작하는 모든 이름이에요. 지금 조건은 이름이 정확히 b인 행만 찾아요.\n\n"
        '조건을 고쳐 이름이 b로 시작하는 물건을 고르세요. 채점은 이름을 바꾼 표로도 실행해요.\n\n'
        + todo('코드 실행을 눌러 행 없음이 나오는지 확인하세요.', "`name = 'b'`를 `name LIKE 'b%'`로 고치세요.", '코드 실행을 눌러 2와 3이 나오는지 확인하세요.', '수정한 질의를 제출하세요.'),
        s4, s4_solution, n4,
        {"조심하세요. '%b%'는 b가 어디에 있든 남겨서 시작 글자 조건이 아니에요.": '실제 의미와, 채점 표(cab)에서 드러나는 차이를 말해요.'},
        [([["LIKE 'b%'", "LIKE '%b%'"]], 'b anywhere'), ([["name LIKE 'b%'", 'id IN (2, 3)']], 'Picking ids by hand')],
        [([["name LIKE 'b%'", "substr(name, 1, 1) = 'b'"]], 'First letter with substr')])),
    dict(old='stp_662bc322-6d1b-4ccd-9776-23398ffc796c', **step(
        'BETWEEN 2 AND 5로 양 끝을 포함한 범위를 고르세요', ['BETWEEN이 양 끝을 포함하는 범위임을 써서 확인해요.'],
        'stock > 2 AND stock < 5는 경계 2와 5를 빼 행 없음이다. BETWEEN 2 AND 5로 고쳐 1과 3을 확인한다. 채점은 행을 바꾼 표로도 실행한다.',
        '`BETWEEN 2 AND 5`는 2 이상 5 이하, 곧 양 끝을 포함하는 범위예요. 지금 조건은 `>`와 `<`라서 경계값 2와 5를 빼요.\n\n'
        '조건을 BETWEEN으로 고쳐 재고가 2 이상 5 이하인 물건을 고르세요. 채점은 행을 바꾼 표로도 실행해요.\n\n'
        + todo('코드 실행을 눌러 행 없음이 나오는지 확인하세요.', '`stock > 2 AND stock < 5`를 `stock BETWEEN 2 AND 5`로 고치세요.', '코드 실행을 눌러 1과 3이 나오는지 확인하세요.', '수정한 질의를 제출하세요.'),
        s5, s5_solution, n5,
        {'조심하세요. BETWEEN은 작은 값을 앞에 써요. BETWEEN 5 AND 2는 아무 행도 남기지 않아요.': '실제 SQLite 동작(x >= 5 AND x <= 2)을 정확히 말해요.'},
        [([['stock BETWEEN 2 AND 5', 'stock > 2 AND stock < 5']], 'Excluding the ends'), ([['stock BETWEEN 2 AND 5', 'stock BETWEEN 5 AND 2']], 'Reversed bounds')],
        [([['stock BETWEEN 2 AND 5', 'stock >= 2 AND stock <= 5']], 'Inclusive comparisons')])),
    dict(old='stp_916dfe17-bddb-4481-9db2-91076141350d', **step(
        'DISTINCT로 분류의 중복을 없애세요', ['DISTINCT가 조회 결과의 중복만 줄임을 확인해요.'],
        'SELECT category는 A,A,B,B다. DISTINCT를 붙여 A,B를 확인한다. 표의 행은 그대로다. 채점은 분류를 바꾼 표로도 실행한다.',
        '네 물건의 분류는 A, B, A, B예요. `DISTINCT`는 조회 결과에서 같은 값을 하나로 줄여요. 표의 행을 지우지는 않아요.\n\n'
        '질의를 고쳐 분류를 중복 없이 한 번씩만 보이세요. 채점은 분류를 바꾼 표로도 실행해요.\n\n'
        + todo('코드 실행을 눌러 A, A, B, B가 나오는지 확인하세요.', '`SELECT` 뒤에 `DISTINCT`를 쓰세요.', '코드 실행을 눌러 A와 B가 나오는지 확인하세요.', '수정한 질의를 제출하세요.'),
        s6, s6_solution, n6,
        {'조심하세요. DISTINCT는 표에서 행을 지우지 않아요. 보여 주는 결과만 줄여요.': '실제 SQL 의미를 정확히 말해요.'},
        [([['SELECT DISTINCT category FROM items', "SELECT 'A' AS category UNION ALL SELECT 'B'"], ['ORDER BY category;\n', ';\n']], 'Typing the categories')],
        [([['SELECT DISTINCT category FROM items ORDER BY category;', 'SELECT category FROM items GROUP BY category ORDER BY category;']], 'GROUP BY also gives one row per value')])),
    dict(old='stp_b6294710-885b-4292-91bc-e113c224821e', **step(
        'LEFT JOIN으로 공급처가 없는 물건도 남기세요', ['내부 조인과 왼쪽 외부 조인이 남기는 행을 구별해요.'],
        'JOIN은 공급처가 없는 bag(3)을 빼 1,2,4다. LEFT JOIN으로 고쳐 3이 NULL 공급처와 함께 남는 것을 확인한다. 채점은 공급처를 바꾼 표로도 실행한다.',
        '`JOIN … ON i.supplier = s.id`는 ON 조건이 맞는 물건과 공급처 행끼리만 이어 붙이는 내부 조인이에요. bag은 공급처가 없어 결과에서 빠져요. `LEFT JOIN`은 왼쪽 표 items의 행을 모두 남기고 짝이 없으면 NULL로 채워요.\n\n'
        '조인을 고쳐 공급처가 없는 물건도 결과에 남기세요. 채점은 공급처를 바꾼 표로도 실행해요.\n\n'
        + todo('코드 실행을 눌러 1, 2, 4만 나오는지 확인하세요.', '`JOIN` 앞에 `LEFT`를 붙이세요.', '코드 실행을 눌러 3이 NULL 공급처와 함께 나오는지 확인하세요.', '수정한 질의를 제출하세요.'),
        s7, s7_solution, n7,
        {'조심하세요. LEFT JOIN 뒤에 WHERE s.name IS NOT NULL을 쓰면 다시 내부 조인처럼 bag이 빠져요.': '실제 흔한 실수와 그 결과를 정확히 말해요.'},
        [([['LEFT JOIN suppliers s ON i.supplier = s.id ORDER BY', 'LEFT JOIN suppliers s ON i.supplier = s.id WHERE s.name IS NOT NULL ORDER BY']], 'Filtering the NULL rows away'),
         ([['FROM items i LEFT JOIN', 'FROM items i JOIN']], 'Inner join')],
        [([['FROM items i LEFT JOIN suppliers s ON i.supplier = s.id', 'FROM items i LEFT OUTER JOIN suppliers s ON s.id = i.supplier']], 'LEFT OUTER JOIN')])),
    dict(old='stp_fdeb9075-80bc-444b-8695-e1e7501f645f', **step(
        'EXISTS 하위 질의로 양수 재고 물건이 있는 공급처를 찾으세요', ['바깥 행과 이어지는 상관 하위 질의의 존재 여부를 EXISTS로 물어요.'],
        'suppliers 전체에 WHERE EXISTS (SELECT 1 FROM items i WHERE i.supplier = s.id AND i.stock > 0)을 더해 10을 확인한다. 채점은 공급처·재고를 바꾼 표로도 실행한다.',
        '괄호 안 SELECT는 바깥 질의가 쓰는 하위 질의예요. `EXISTS (하위 질의)`는 그 하위 질의가 행을 하나라도 돌려주면 참이에요. 하위 질의 안에서 `s.id`를 쓰면 바깥에서 지금 보는 공급처를 가리켜요.\n\n'
        'WHERE에 EXISTS 하위 질의를 써서 양수 재고 물건이 있는 공급처만 남기세요. 채점은 공급처와 재고를 바꾼 표로도 실행해요.\n\n'
        + todo('코드 실행을 눌러 10, 20, 30이 모두 나오는지 확인하세요.', '`FROM suppliers s` 다음 줄에 `WHERE EXISTS (SELECT 1 FROM items i WHERE i.supplier = s.id AND i.stock > 0)`를 쓰세요.',
               '코드 실행을 눌러 10만 나오는지 확인하세요.', '작성한 질의를 제출하세요.'),
        s8, s8_solution, n8,
        {'공급처마다 양수 재고 물건이 하나라도 있는지 EXISTS로 물어야 해요.': '「하나라도」는 EXISTS의 실제 의미(행이 하나 이상)와 맞아요.',
         '조심하세요. 하위 질의에 i.supplier = s.id가 없으면 어느 공급처든 물건이 하나만 있어도 참이 돼요.': '실제 흔한 실수(상관 조건 누락)와 그 결과를 정확히 말해요.'},
        [([['WHERE i.supplier = s.id AND i.stock > 0', 'WHERE i.stock > 0']], 'Missing the correlation'), ([['WHERE i.supplier = s.id AND i.stock > 0', 'WHERE i.supplier = s.id']], 'Any stock')],
        [([['WHERE EXISTS (SELECT 1 FROM items i WHERE i.supplier = s.id AND i.stock > 0)', 'WHERE s.id IN (SELECT supplier FROM items WHERE stock > 0)']], 'IN with a non-NULL list')])),
    dict(old='stp_a479e334-6bf7-420d-a963-b221c0f8a425', **step(
        'NOT EXISTS로 물건이 없는 공급처를 찾으세요', ['NOT IN 목록의 NULL이 결과를 비우는 이유를 알고 NOT EXISTS로 고쳐요.'],
        'NOT IN (SELECT supplier FROM items)는 bag의 NULL 때문에 행 없음이다. NOT EXISTS (… i.supplier = s.id)로 고쳐 30을 확인한다. 채점은 공급처를 바꾼 표로도 실행한다.',
        '`NOT IN (하위 질의)`는 하위 질의가 돌려준 목록에 없을 때 참이에요. 그런데 bag의 supplier가 NULL이라 목록에 NULL이 섞여요. NULL과 비교하면 결과를 알 수 없어서, 물건이 없는 공급처 30도 참이 되지 않아요.\n\n'
        '질의를 NOT EXISTS로 고쳐 물건이 하나도 없는 공급처를 찾으세요. 채점은 공급처를 바꾼 표로도 실행해요.\n\n'
        + todo('코드 실행을 눌러 행 없음이 나오는지 확인하세요.', 'WHERE 줄을 `WHERE NOT EXISTS (SELECT 1 FROM items i WHERE i.supplier = s.id)`로 고치세요.', '코드 실행을 눌러 30이 나오는지 확인하세요.', '수정한 질의를 제출하세요.'),
        s9, s9_solution, n9,
        {'조심하세요. x NOT IN (…, NULL)은 참이 될 수 없어요. NULL과의 비교는 알 수 없음이에요.': '실제 SQL 삼값 논리를 정확히 말해요.'},
        [([['WHERE NOT EXISTS (SELECT 1 FROM items i WHERE i.supplier = s.id)', 'WHERE s.id NOT IN (SELECT supplier FROM items)']], 'NOT IN with a NULL'),
         ([['WHERE NOT EXISTS (SELECT 1 FROM items i WHERE i.supplier = s.id)', 'WHERE s.id = 30']], 'Picking the id by hand')],
        [([['WHERE NOT EXISTS (SELECT 1 FROM items i WHERE i.supplier = s.id)', 'WHERE s.id NOT IN (SELECT supplier FROM items WHERE supplier IS NOT NULL)']], 'NOT IN without NULLs')])),
]
