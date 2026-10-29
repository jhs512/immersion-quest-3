"""engineer-db-model: 8 answer-picking steps -> query and schema-writing steps (2026-10-29).

Steps 1-4 write SQL queries on the prepared tables. Steps 5-8 declare one constraint each in the
schema string of the same Python + SQLite harness as the lesson's final challenge: the program tries
real inserts and prints whether SQLite rejected them, and a probe reads the declared schema through
PRAGMA, so printing True/False without the constraint fails."""
from _kit import Script, todo, sql_output

OPENING = ['이 수업에서는 DB의 행·열·키·NULL을 구별해요. 질의와 스키마를 직접 고쳐 자료 구조와 업무 규칙의 관계를 배워요.',
           '기본 키·필수값·참조·복합 키를 하나씩 선언하고, DDL이 실제로 막아 주는 저장을 실행으로 확인해요.']
PRD_SCOPE = ['SQLite 실제 실행과 방언 차이 안내를 함께 제공해요.',
             '같은 재고 표에서 질의 한 곳씩 고치고, 스키마에 제약 하나씩 직접 선언해요.']
PRD_GRADING = ['질의 스텝은 실제 SQLite로 실행하고 행을 바꾼 준비 표 두 개에서도 확인해요.',
               '제약 스텝은 실제 SQLite에 잘못된 삽입과 올바른 삽입을 함께 시도해 결과를 보고, 준비 ID를 바꾼 실행과 PRAGMA로 읽은 실제 스키마까지 검사해요. True/False를 직접 출력한 답은 거절해요.',
               '마지막 도전(stp_73e5ef52-9e58-4426-9b17-b8437b6262ca): 실제 Python 실행과 다른 준비 자료의 결과를 검사해요. 시작 코드는 실패하고 동등한 풀이도 통과해야 해요.']
PRD_NARRATION = ['작은 수정·실행·결과 읽기를 반복해요.',
                 '준비 코드를 먼저 실행하고, 질의나 스키마 한 곳을 고친 뒤 다시 실행해 차이를 짚어요.']

SETUP = ("-- ID는 물건을 구별하고 이름은 겹칠 수 있어요.\n"
         "CREATE TABLE items(id INTEGER PRIMARY KEY, name TEXT NOT NULL, stock INTEGER CHECK(stock>=0));\n"
         "INSERT INTO items VALUES{items};\n"
         "CREATE TABLE lots(item_id INTEGER REFERENCES items(id), batch INTEGER, PRIMARY KEY(item_id,batch));\n"
         "INSERT INTO lots VALUES{lots};\n")
BASE = {'setup.sql': SETUP.format(items="(1,'pen',2),(2,'pen',3),(3,'book',NULL)", lots='(1,1),(1,2),(2,1)')}
V1 = {'setup.sql': SETUP.format(items="(1,'cup',NULL),(4,'cup',1),(5,'cup',NULL),(7,'map',0)", lots='(4,1),(7,3)')}
V2 = {'setup.sql': SETUP.format(items="(2,'bag',5),(3,'box',6)", lots='(3,1),(3,2),(2,9)')}


def sql_step(title, objectives, core_flow, goal, starter, solution, narration, review, reject, accept):
    return dict(title=title, objectives=objectives, core_flow=core_flow, goal=goal, starter_code=starter, solution=solution,
                language='sql', files=BASE, narration=narration.actions, review=review, reject=reject, accept=accept,
                tests=[{'input': '', 'expected': sql_output(BASE, solution)}],
                variations=[{'files': v, 'expected': sql_output(v, solution)} for v in (V1, V2)])


s1 = '-- 이 질의를 고쳐 같은 행의 id와 name을 함께 보이세요.\nSELECT id FROM items ORDER BY id;\n'
s1_solution = '-- 이 질의를 고쳐 같은 행의 id와 name을 함께 보이세요.\n-- 한 행은 한 물건이에요. 같은 행의 열끼리 그 물건의 정보예요.\nSELECT id, name FROM items ORDER BY id;\n'
n1 = (Script(s1)
      .say('items는 물건마다 한 행이에요. 같은 행의 id와 name을 함께 보여야 해요.', 'text:질의를 고쳐 같은 행의 id와 name을 함께 보이세요.')
      .run('SELECT id')
      .say('1, 2, 3이에요. 아직 id 열만 골랐어요.', 'output')
      .patch('SELECT id FROM', 'SELECT id, name FROM', 'id 뒤에 쉼표와 name을 써요.')
      .run('SELECT id')
      .say('1 pen, 2 pen, 3 book이에요. 같은 행에서 한 물건의 ID와 이름을 읽어요.', 'output')
      .say('조심하세요. 열을 따로 조회해 순서로 맞추면 다른 물건의 값이 섞일 수 있어요. 한 행에서 함께 읽어요.', 'code:SELECT id, name FROM items'))

s2 = '-- 이 질의에 열을 더해 이름 종류 수 옆에 ID 종류 수도 보이세요.\nSELECT COUNT(DISTINCT name) AS names FROM items;\n'
s2_solution = '-- 이 질의에 열을 더해 이름 종류 수 옆에 ID 종류 수도 보이세요.\n-- 이름은 겹칠 수 있지만 ID는 물건마다 달라 물건 수와 같아요.\nSELECT COUNT(DISTINCT name) AS names, COUNT(DISTINCT id) AS ids FROM items;\n'
n2 = (Script(s2)
      .say('이름이 pen인 물건이 둘이에요. 이름 종류 수 옆에 ID 종류 수도 세어 비교해야 해요.', 'text:질의에 열을 더해 이름 종류 수 옆에 ID 종류 수도 보이세요.')
      .run('SELECT COUNT(')
      .say('2예요. 세 물건인데 이름은 pen과 book 두 종류예요.', 'output')
      .patch('AS names FROM', 'AS names, COUNT(DISTINCT id) AS ids FROM', 'COUNT(DISTINCT id) AS ids 열을 더해요.')
      .run('SELECT COUNT(')
      .say('이름은 2, ID는 3이에요. 세 물건을 하나씩 구별하는 열은 ID예요.', 'output')
      .say('조심하세요. 지금 이름이 겹치지 않는다고 이름을 식별자로 쓰면 같은 이름의 새 물건을 구별하지 못해요.', 'code:COUNT(DISTINCT id)'))

s3 = '-- 이 질의에 열을 더해 재고를 아는 물건 수 옆에 전체 행 수도 보이세요.\nSELECT COUNT(stock) AS known FROM items;\n'
s3_solution = '-- 이 질의에 열을 더해 재고를 아는 물건 수 옆에 전체 행 수도 보이세요.\n-- 재고가 NULL이어도 그 물건 행은 있어요. COUNT(*)는 그 행도 세요.\nSELECT COUNT(stock) AS known, COUNT(*) AS rows FROM items;\n'
n3 = (Script(s3)
      .say('book의 재고는 NULL이에요. 재고를 아는 수 옆에 전체 행 수도 세어야 해요.', 'text:질의에 열을 더해 재고를 아는 물건 수 옆에 전체 행 수도 보이세요.')
      .run('SELECT COUNT(')
      .say('2예요. 재고 값이 있는 두 행만 세었어요.', 'output')
      .patch('AS known FROM', 'AS known, COUNT(*) AS rows FROM', 'COUNT(*) AS rows 열을 더해요.')
      .run('SELECT COUNT(')
      .say('2와 3이에요. 재고를 모르는 book도 행으로는 있어요.', 'output')
      .say('조심하세요. NULL은 「값을 모른다」는 표시예요. 행이 없다는 뜻이 아니에요.', 'code:COUNT(*) AS rows'))

s4 = '-- 이 질의에 JOIN을 더해 로트마다 물건 이름을 보이세요.\nSELECT lots.item_id, lots.batch FROM lots ORDER BY lots.item_id, lots.batch;\n'
s4_solution = ('-- 이 질의에 JOIN을 더해 로트마다 물건 이름을 보이세요.\n'
               '-- lots.item_id는 items.id를 가리키는 번호예요. 같은 번호의 items 행과 이어 이름을 읽어요.\n'
               'SELECT lots.item_id, lots.batch, items.name FROM lots JOIN items ON lots.item_id = items.id ORDER BY lots.item_id, lots.batch;\n')
n4 = (Script(s4)
      .say('lots에는 물건 이름 없이 item_id 번호만 있어요. items와 이어 이름을 보여야 해요.', 'text:질의에 JOIN을 더해 로트마다 물건 이름을 보이세요.')
      .run('SELECT lots.item_id')
      .say('번호와 로트만 나와요. 어떤 물건인지는 items에 있어요.', 'output')
      .patch('SELECT lots.item_id, lots.batch FROM lots ORDER BY', 'SELECT lots.item_id, lots.batch, items.name FROM lots JOIN items ON lots.item_id = items.id ORDER BY',
             'items.name을 고르고 lots.item_id = items.id로 items를 이어요.')
      .run('SELECT lots.item_id')
      .say('로트 1과 2는 pen, 물건 2의 로트도 pen이에요. 이름은 같아도 item_id로 서로 다른 물건이에요.', 'output')
      .say('조심하세요. 이름 글자로 이으면 이름이 같은 pen 두 개가 서로 섞여요.', 'code:lots.item_id = items.id'))

# ---- constraint steps: Python + real SQLite --------------------------------------------
HARNESS_HEAD = '''import sqlite3
{values}
db = sqlite3.connect(":memory:")
db.execute("PRAGMA foreign_keys=ON")
# 이 문자열 안의 SQL만 고치세요. 실행과 검사 코드는 준비돼 있어요.
schema = """{schema}"""
db.executescript(schema)
{prepare}
db.commit()


def rejected(sql, values):
    # DB가 IntegrityError로 거절하면 True, 받아들이면 False예요.
    try:
        db.execute(sql, values)
        db.rollback()
        return False
    except sqlite3.IntegrityError:
        db.rollback()
        return True


'''


def harness(values, schema, prepare, checks):
    return HARNESS_HEAD.format(values=values, schema=schema, prepare=prepare) + checks


ITEMS = 'CREATE TABLE items(\n    id INTEGER,\n    name TEXT NOT NULL,\n    stock INTEGER CHECK(stock >= 0)\n);'
s5 = harness('existing_id = 1', ITEMS, 'db.execute("INSERT INTO items VALUES(?, \'pen\', 2)", (existing_id,))',
             '# 이미 있는 ID와 새 ID로 각각 넣어 봐요.\nprint(rejected("INSERT INTO items VALUES(?, \'bag\', 1)", (existing_id,)))\nprint(rejected("INSERT INTO items VALUES(?, \'bag\', 1)", (existing_id + 1,)))\n')
s5_solution = s5.replace('\n    id INTEGER,', '\n    id INTEGER PRIMARY KEY,')
n5 = (Script(s5)
      .say('schema의 id에 기본 키를 선언해야 해요. 그러면 같은 ID의 두 번째 물건을 DB가 거절해요.', 'text:schema 문자열의 id에 PRIMARY KEY를 선언하세요.')
      .run('print(rejected(', 'existing_id + 1')
      .say('False와 False예요. 아직 기본 키가 없어 같은 ID도 받아들였어요.', 'output')
      .patch('\n    id INTEGER,', '\n    id INTEGER PRIMARY KEY,', 'id INTEGER 뒤에 PRIMARY KEY를 써요.')
      .run('print(rejected(', 'existing_id + 1')
      .say('True와 False예요. 같은 ID는 거절하고 새 ID는 받아들여요.', 'output')
      .say('조심하세요. INSERT OR REPLACE를 쓰면 같은 ID의 기존 행을 지우고 새 행으로 바꿔 넣어요. 기본 키가 거절하는 것은 보통 INSERT예요.', 'code:id INTEGER PRIMARY KEY'))

ITEMS_NAME = 'CREATE TABLE items(\n    id INTEGER PRIMARY KEY,\n    name TEXT,\n    stock INTEGER CHECK(stock >= 0)\n);'
s6 = harness('new_id = 4', ITEMS_NAME, 'db.execute("INSERT INTO items VALUES(1, \'pen\', 2)")',
             '# 이름 없이(NULL) 넣을 때와 이름이 있을 때를 비교해요.\nprint(rejected("INSERT INTO items VALUES(?, NULL, 1)", (new_id,)))\nprint(rejected("INSERT INTO items VALUES(?, \'cap\', 1)", (new_id,)))\n')
s6_solution = s6.replace('\n    name TEXT,', '\n    name TEXT NOT NULL,')
n6 = (Script(s6)
      .say('name에 NOT NULL을 선언해야 해요. 그러면 이름 없는 물건을 DB가 거절해요.', 'text:schema 문자열의 name에 NOT NULL을 선언하세요.')
      .run('print(rejected(', "'cap', 1)")
      .say('False와 False예요. 이름이 NULL이어도 받아들였어요.', 'output')
      .patch('\n    name TEXT,', '\n    name TEXT NOT NULL,', 'name TEXT 뒤에 NOT NULL을 써요.')
      .run('print(rejected(', "'cap', 1)")
      .say('True와 False예요. 이름 없는 물건만 거절했어요.', 'output')
      .say("조심하세요. NOT NULL은 빈 글자 ''를 막지 않아요. ''는 NULL이 아니라 길이 0인 값이에요.", 'code:name TEXT NOT NULL'))

LOTS_FK = ('CREATE TABLE items(id INTEGER PRIMARY KEY, name TEXT NOT NULL);\n'
           'CREATE TABLE lots(\n    item_id INTEGER,\n    batch INTEGER,\n    PRIMARY KEY(item_id, batch)\n);')
s7 = harness('parent_id = 1\nmissing_id = 9', LOTS_FK, 'db.execute("INSERT INTO items VALUES(?, \'pen\')", (parent_id,))',
             '# 없는 물건과 있는 물건의 로트를 각각 넣어 봐요.\nprint(rejected("INSERT INTO lots VALUES(?, 1)", (missing_id,)))\nprint(rejected("INSERT INTO lots VALUES(?, 1)", (parent_id,)))\n')
s7_solution = s7.replace('\n    item_id INTEGER,', '\n    item_id INTEGER REFERENCES items(id),')
n7 = (Script(s7)
      .say('lots의 item_id가 items의 id를 참조하게 선언해야 해요. 그러면 없는 물건의 로트를 거절해요.', 'text:schema 문자열의 lots.item_id가 items(id)를 참조하게 선언하세요.')
      .run('print(rejected(', '(parent_id,)))')
      .say('False와 False예요. ID 9인 물건이 없어도 로트를 받아들였어요.', 'output')
      .patch('\n    item_id INTEGER,', '\n    item_id INTEGER REFERENCES items(id),', 'item_id INTEGER 뒤에 REFERENCES items(id)를 써요.')
      .run('print(rejected(', '(parent_id,)))')
      .say('True와 False예요. 없는 물건의 로트만 거절했어요.', 'output')
      .say('조심하세요. SQLite는 PRAGMA foreign_keys=ON일 때만 참조를 검사해요. 준비 코드가 처음에 켜 두었어요.', 'code:db.execute("PRAGMA foreign_keys=ON")'))

LOTS_PK = ('CREATE TABLE items(id INTEGER PRIMARY KEY, name TEXT NOT NULL);\n'
           'CREATE TABLE lots(\n    item_id INTEGER REFERENCES items(id),\n    batch INTEGER,\n    PRIMARY KEY(item_id)\n);')
s8 = harness('item = 1\nbatch = 1', LOTS_PK, 'db.execute("INSERT INTO items VALUES(?, \'pen\')", (item,))\ndb.execute("INSERT INTO lots VALUES(?, ?)", (item, batch))',
             '# 같은 쌍과, 같은 물건의 새 로트를 각각 넣어 봐요.\nprint(rejected("INSERT INTO lots VALUES(?, ?)", (item, batch)))\nprint(rejected("INSERT INTO lots VALUES(?, ?)", (item, batch + 1)))\n')
s8_solution = s8.replace('\n    PRIMARY KEY(item_id)\n', '\n    PRIMARY KEY(item_id, batch)\n')
n8 = (Script(s8)
      .say('로트는 물건 번호와 로트 번호의 쌍으로 구별해요. 기본 키를 두 열의 쌍으로 고쳐야 해요.', 'text:schema 문자열의 PRIMARY KEY(item_id)를 item_id와 batch의 쌍으로 고치세요.')
      .run('print(rejected(', 'batch + 1)))')
      .say('True와 True예요. 기본 키가 item_id 하나라 같은 물건의 새 로트도 거절했어요.', 'output')
      .patch('\n    PRIMARY KEY(item_id)\n', '\n    PRIMARY KEY(item_id, batch)\n', 'PRIMARY KEY 괄호에 batch를 더해요.')
      .run('print(rejected(', 'batch + 1)))')
      .say('True와 False예요. 같은 쌍만 거절하고 같은 물건의 새 로트는 받아들여요.', 'output')
      .say('조심하세요. PRIMARY KEY를 열마다 따로 두 번 쓸 수는 없어요. 복합 키는 괄호 하나에 열을 함께 써요.', 'code:PRIMARY KEY(item_id, batch)'))


def py_step(title, objectives, core_flow, goal, starter, solution, narration, review, reject, accept, cases, probe, expected):
    return dict(title=title, objectives=objectives, core_flow=core_flow, goal=goal, starter_code=starter, solution=solution,
                language='python', narration=narration.actions, review=review, reject=reject, accept=accept,
                tests=[{'input': '', 'expected': expected}], prepared_cases=cases, prepared_probes=probe)


def typed(starter_checks, printed):
    """A rejected answer: the schema stays as given and the program prints the expected words."""
    return [[starter_checks, printed]]


SPECS = [
    dict(old='stp_b8e2b0df-b86c-4377-b758-bad85d831756', **sql_step(
        '같은 행의 id와 name을 함께 조회하세요', ['한 행의 열들이 같은 물건의 값임을 확인해요.'],
        'SELECT id에 name 열을 더해 한 행에서 같은 물건의 ID와 이름을 읽는다. 채점은 행을 바꾼 표로도 실행한다.',
        'items 표는 물건마다 한 행이고 id·name·stock 열이 있어요. SELECT 뒤에 쉼표로 열을 이어 쓰면 같은 행의 여러 열을 함께 보여 줘요.\n\n'
        '질의를 고쳐 같은 행의 id와 name을 함께 보이세요. 채점은 행을 바꾼 표로도 실행해요.\n\n'
        + todo('코드 실행을 눌러 id만 나오는지 확인하세요.', '`SELECT id`를 `SELECT id, name`으로 고치세요.', '코드 실행을 눌러 각 ID 옆에 이름이 나오는지 확인하세요.', '수정한 질의를 제출하세요.'),
        s1, s1_solution, n1,
        {'조심하세요. 열을 따로 조회해 순서로 맞추면 다른 물건의 값이 섞일 수 있어요. 한 행에서 함께 읽어요.': '실제 관계형 모델 원칙(행 단위 사실)을 학습자 수준으로 말해요.'},
        [([['SELECT id, name FROM items ORDER BY id;', 'SELECT name, id FROM items ORDER BY id;']], 'Columns in another order'),
         ([['SELECT id, name FROM items ORDER BY id;', "SELECT 1 AS id, 'pen' AS name;"]], 'Typing a row')],
        [([['SELECT id, name FROM items ORDER BY id;', 'SELECT items.id, items.name FROM items ORDER BY items.id;']], 'Table-qualified columns')])),
    dict(old='stp_10120cb0-f8e8-40b9-b7ee-f6d40905335f', **sql_step(
        '이름 종류 수 옆에 ID 종류 수를 세세요', ['겹칠 수 있는 이름과 물건을 구별하는 ID를 비교해요.'],
        'COUNT(DISTINCT name)은 2다. COUNT(DISTINCT id) AS ids를 더해 3을 확인한다. 세 물건을 구별하는 열은 ID다. 채점은 이름이 더 겹치는 표로도 실행한다.',
        'items에는 이름이 pen인 물건이 둘 있어요. `COUNT(DISTINCT 열)`은 그 열의 서로 다른 값 개수를 세요.\n\n'
        '질의에 열을 더해 이름 종류 수 옆에 ID 종류 수도 보이세요. 열 이름은 ids로 해요. 채점은 이름이 더 겹치는 표로도 실행해요.\n\n'
        + todo('코드 실행을 눌러 이름 종류 수 2가 나오는지 확인하세요.', '`AS names` 뒤에 `, COUNT(DISTINCT id) AS ids`를 쓰세요.', '코드 실행을 눌러 이름 2, ID 3이 나오는지 확인하세요.', '수정한 질의를 제출하세요.'),
        s2, s2_solution, n2,
        {'조심하세요. 지금 이름이 겹치지 않는다고 이름을 식별자로 쓰면 같은 이름의 새 물건을 구별하지 못해요.': '실제 설계 원칙(식별자 선택)을 정확히 말해요.'},
        [([['COUNT(DISTINCT id) AS ids', 'COUNT(DISTINCT name) AS ids']], 'Counting names twice'), ([['COUNT(DISTINCT id) AS ids', '3 AS ids']], 'Typing the count')],
        [([['COUNT(DISTINCT id) AS ids', 'COUNT(*) AS ids']], 'Rows equal ids because id is the primary key')])),
    dict(old='stp_d5a9be0f-aa9c-4da6-a907-0d1136434970', **sql_step(
        '재고를 아는 수 옆에 전체 행 수를 세세요', ['NULL 값이 있어도 행은 있음을 행 수로 확인해요.'],
        'COUNT(stock)은 NULL을 빼 2다. COUNT(*) AS rows를 더해 3을 확인한다. 채점은 NULL이 더 많은 표로도 실행한다.',
        '세 번째 물건 book은 재고를 아직 몰라 stock이 NULL이에요. `COUNT(stock)`은 재고 값이 있는 행만, `COUNT(*)`는 행 자체를 세요.\n\n'
        '질의에 열을 더해 재고를 아는 물건 수 옆에 전체 행 수도 보이세요. 열 이름은 rows로 해요. 채점은 NULL이 더 많은 표로도 실행해요.\n\n'
        + todo('코드 실행을 눌러 2가 나오는지 확인하세요.', '`AS known` 뒤에 `, COUNT(*) AS rows`를 쓰세요.', '코드 실행을 눌러 2와 3이 나오는지 확인하세요.', '수정한 질의를 제출하세요.'),
        s3, s3_solution, n3,
        {'조심하세요. NULL은 「값을 모른다」는 표시예요. 행이 없다는 뜻이 아니에요.': '실제 SQL 의미를 정확히 말해요.'},
        [([['COUNT(*) AS rows', 'COUNT(stock) AS rows']], 'Only known values'), ([['COUNT(*) AS rows', '3 AS rows']], 'Typing the count')],
        [([['COUNT(*) AS rows', 'COUNT(id) AS rows']], 'Counting the never-NULL key')])),
    dict(old='stp_6febadfa-0994-46f4-a8d5-92f32767c21a', **sql_step(
        'JOIN으로 로트마다 물건 이름을 보이세요', ['외래 키 번호로 다른 표의 행을 이어 읽어요.'],
        'lots에는 item_id 번호만 있다. JOIN items ON lots.item_id = items.id로 items.name을 함께 보인다. 이름이 같은 물건도 번호로 구별된다. 채점은 행을 바꾼 표로도 실행한다.',
        'lots 표는 물건 이름 없이 item_id 번호만 가져요. setup.sql은 item_id를 `REFERENCES items(id)`로 만들었어요. `JOIN items ON lots.item_id = items.id`는 lots의 각 행을 같은 번호의 items 행과 이어 붙여요.\n\n'
        '질의에 JOIN을 더해 로트마다 물건 이름을 보이세요. 이름 열은 lots.batch 뒤에 둬요. 채점은 행을 바꾼 표로도 실행해요.\n\n'
        + todo('코드 실행을 눌러 번호와 로트만 나오는지 확인하세요.', 'SELECT에 `items.name`을 더하고 `FROM lots` 뒤에 `JOIN items ON lots.item_id = items.id`를 쓰세요.',
               '코드 실행을 눌러 로트마다 이름이 나오는지 확인하세요.', '수정한 질의를 제출하세요.'),
        s4, s4_solution, n4,
        {'로트 1과 2는 pen, 물건 2의 로트도 pen이에요. 이름은 같아도 item_id로 서로 다른 물건이에요.': '실제 출력(세 줄 모두 pen)과 맞고, 「같아도」 대조가 item_id 1과 2로 확인돼요.',
         '조심하세요. 이름 글자로 이으면 이름이 같은 pen 두 개가 서로 섞여요.': '실제 결과(이름 조인 시 행 중복)를 정확히 말해요.'},
        [([['JOIN items ON lots.item_id = items.id', 'JOIN items ON lots.batch = items.id']], 'Joining the wrong column'),
         ([['FROM lots JOIN items ON lots.item_id = items.id', 'FROM lots, items']], 'Every pair without a condition')],
        [([['FROM lots JOIN items ON lots.item_id = items.id', 'FROM lots INNER JOIN items ON items.id = lots.item_id']], 'INNER JOIN with operands swapped')])),
    dict(old='stp_408577f8-70ac-4673-ab29-c637d16c04ec', **py_step(
        'schema의 id에 PRIMARY KEY를 선언하세요', ['기본 키가 같은 ID의 두 번째 행을 실제로 거절함을 확인해요.'],
        'Python 준비 코드가 실제 SQLite에 schema를 만든다. id에 PRIMARY KEY를 선언하면 같은 ID 삽입은 거절(True), 새 ID는 허용(False)이다. 채점은 준비 ID를 바꾸고 PRAGMA table_info로 실제 기본 키를 확인한다.',
        '실제 SQLite를 실행하는 Python 준비 코드예요. schema 문자열 안의 SQL만 고쳐요. 준비된 검사는 이미 있는 ID와 새 ID로 각각 물건을 넣어 보고, DB가 거절하면 True를 출력해요.\n\n'
        'schema 문자열의 id에 PRIMARY KEY를 선언하세요. 같은 ID는 True, 새 ID는 False가 되어야 해요. 채점은 준비 ID를 바꾸고 실제 스키마도 확인해요.\n\n'
        + todo('코드 실행을 눌러 False와 False가 나오는지 확인하세요.', 'schema의 `id INTEGER` 뒤에 `PRIMARY KEY`를 쓰세요.', '코드 실행을 눌러 True와 False가 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
        s5, s5_solution, n5,
        {'조심하세요. INSERT OR REPLACE를 쓰면 같은 ID의 기존 행을 지우고 새 행으로 바꿔 넣어요. 기본 키가 거절하는 것은 보통 INSERT예요.': '실제 SQLite 동작(REPLACE 충돌 해결)을 정확히 말해요.'},
        [([['print(rejected("INSERT INTO items VALUES(?, \'bag\', 1)", (existing_id,)))\n', 'print(True)\n'], ['\n    id INTEGER PRIMARY KEY,', '\n    id INTEGER,']], 'Printing True without the key'),
         ([['\n    id INTEGER PRIMARY KEY,', '\n    id INTEGER UNIQUE,'], ['    name TEXT NOT NULL,', '    name TEXT NOT NULL UNIQUE,']], 'Unique names reject the new id too')],
        [([['\n    id INTEGER PRIMARY KEY,', '\n    id INTEGER,'], ['    stock INTEGER CHECK(stock >= 0)\n);', '    stock INTEGER CHECK(stock >= 0),\n    PRIMARY KEY(id)\n);']], 'Table-level primary key')],
        [{'values': {'existing_id': 1}, 'expected': 'True\nFalse'}, {'values': {'existing_id': 42}, 'expected': 'True\nFalse'}],
        'assert next(r for r in db.execute("PRAGMA table_info(items)") if r[1] == "id")[5] == 1', 'True\nFalse')),
    dict(old='stp_ac2732a0-6c29-4b2f-b2cd-bddb338fa894', **py_step(
        'schema의 name에 NOT NULL을 선언하세요', ['필수값 제약이 NULL 저장을 실제로 거절함을 확인해요.'],
        'name에 NOT NULL을 선언하면 이름 없는 삽입은 거절(True), 이름 있는 삽입은 허용(False)이다. 채점은 준비 ID를 바꾸고 PRAGMA table_info로 실제 NOT NULL을 확인한다.',
        '이름 없는 물건은 저장하면 안 돼요. `NOT NULL`을 선언한 열에는 NULL을 넣을 수 없어요. 준비된 검사는 같은 새 ID로 이름이 NULL인 물건과 이름이 있는 물건을 각각 넣어 보고, DB가 거절하면 True를 출력해요.\n\n'
        'schema 문자열의 name에 NOT NULL을 선언하세요. 이름 없는 물건은 True, 이름 있는 물건은 False가 되어야 해요. 채점은 준비 ID를 바꾸고 실제 스키마도 확인해요.\n\n'
        + todo('코드 실행을 눌러 False와 False가 나오는지 확인하세요.', 'schema의 `name TEXT` 뒤에 `NOT NULL`을 쓰세요.', '코드 실행을 눌러 True와 False가 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
        s6, s6_solution, n6,
        {'False와 False예요. 이름이 NULL이어도 받아들였어요.': '「이어도」 대조가 실제 출력(제약 없이 허용)과 맞아요.',
         "조심하세요. NOT NULL은 빈 글자 ''를 막지 않아요. ''는 NULL이 아니라 길이 0인 값이에요.": '실제 SQL 의미를 정확히 말해요.'},
        [([['print(rejected("INSERT INTO items VALUES(?, NULL, 1)", (new_id,)))\n', 'print(True)\n'], ['\n    name TEXT NOT NULL,', '\n    name TEXT,']], 'Printing True without the constraint'),
         ([['\n    name TEXT NOT NULL,', "\n    name TEXT CHECK(name <> ''),"]], 'A CHECK that NULL passes')],
        [([['\n    name TEXT NOT NULL,', '\n    name TEXT CHECK(name IS NOT NULL) NOT NULL,']], 'NOT NULL with an extra CHECK')],
        [{'values': {'new_id': 4}, 'expected': 'True\nFalse'}, {'values': {'new_id': 77}, 'expected': 'True\nFalse'}],
        'assert next(r for r in db.execute("PRAGMA table_info(items)") if r[1] == "name")[3] == 1', 'True\nFalse')),
    dict(old='stp_9b281cb9-6312-43d5-a022-e61bee8a8e6f', **py_step(
        'lots.item_id가 items(id)를 참조하게 선언하세요', ['외래 키가 없는 부모를 가리키는 행을 실제로 거절함을 확인해요.'],
        'lots.item_id에 REFERENCES items(id)를 선언하면 없는 물건 ID 9의 로트는 거절(True), 있는 물건의 로트는 허용(False)이다. 채점은 준비 ID를 바꾸고 PRAGMA foreign_key_list로 실제 참조를 확인한다.',
        'lots의 item_id는 items의 id를 가리켜야 해요. `REFERENCES items(id)`로 선언하면 items에 없는 번호를 가진 로트를 DB가 거절해요. 준비된 검사는 없는 물건과 있는 물건의 로트를 각각 넣어 보고, 거절하면 True를 출력해요.\n\n'
        'schema 문자열의 lots.item_id가 items(id)를 참조하게 선언하세요. 없는 물건은 True, 있는 물건은 False가 되어야 해요. 채점은 준비 ID를 바꾸고 실제 스키마도 확인해요.\n\n'
        + todo('코드 실행을 눌러 False와 False가 나오는지 확인하세요.', 'lots의 `item_id INTEGER` 뒤에 `REFERENCES items(id)`를 쓰세요.', '코드 실행을 눌러 True와 False가 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
        s7, s7_solution, n7,
        {'False와 False예요. ID 9인 물건이 없어도 로트를 받아들였어요.': '「없어도」 대조가 실제 출력(참조 없이 허용)과 맞아요.',
         '조심하세요. SQLite는 PRAGMA foreign_keys=ON일 때만 참조를 검사해요. 준비 코드가 처음에 켜 두었어요.': '실제 SQLite 동작(외래 키 검사는 기본으로 꺼짐)을 정확히 말해요.'},
        [([['print(rejected("INSERT INTO lots VALUES(?, 1)", (missing_id,)))\n', 'print(True)\n'], ['\n    item_id INTEGER REFERENCES items(id),', '\n    item_id INTEGER,']], 'Printing True without the reference'),
         ([['\n    item_id INTEGER REFERENCES items(id),', '\n    item_id INTEGER CHECK(item_id < 5),']], 'A range check instead of a reference')],
        [([['\n    item_id INTEGER REFERENCES items(id),', '\n    item_id INTEGER,'], ['    PRIMARY KEY(item_id, batch)\n);', '    PRIMARY KEY(item_id, batch),\n    FOREIGN KEY(item_id) REFERENCES items(id)\n);']], 'Table-level foreign key')],
        [{'values': {'parent_id': 1, 'missing_id': 9}, 'expected': 'True\nFalse'}, {'values': {'parent_id': 3, 'missing_id': 2}, 'expected': 'True\nFalse'}],
        'assert any(r[2] == "items" and r[3] == "item_id" and r[4] == "id" for r in db.execute("PRAGMA foreign_key_list(lots)"))', 'True\nFalse')),
    dict(old='stp_1b02a8fc-876f-422a-849d-ab9f20da3971', **py_step(
        '기본 키를 item_id와 batch의 쌍으로 고치세요', ['두 열을 묶은 복합 키가 쌍의 중복만 거절함을 확인해요.'],
        'PRIMARY KEY(item_id)는 같은 물건의 새 로트도 거절해 True, True다. PRIMARY KEY(item_id, batch)로 고쳐 같은 쌍만 거절(True), 새 로트는 허용(False)이다. 채점은 준비 번호를 바꾸고 PRAGMA table_info로 두 열의 키 순서를 확인한다.',
        '로트는 물건 번호와 로트 번호의 쌍으로 구별해요. 기본 키를 `PRIMARY KEY(item_id, batch)`처럼 두 열로 묶으면 쌍이 겹칠 때만 거절해요. 지금은 item_id 하나만 기본 키예요.\n\n'
        'schema 문자열의 PRIMARY KEY(item_id)를 item_id와 batch의 쌍으로 고치세요. 같은 쌍은 True, 같은 물건의 새 로트는 False가 되어야 해요. 채점은 준비 번호를 바꾸고 실제 스키마도 확인해요.\n\n'
        + todo('코드 실행을 눌러 True와 True가 나오는지 확인하세요.', '`PRIMARY KEY(item_id)`를 `PRIMARY KEY(item_id, batch)`로 고치세요.', '코드 실행을 눌러 True와 False가 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
        s8, s8_solution, n8,
        {'조심하세요. PRIMARY KEY를 열마다 따로 두 번 쓸 수는 없어요. 복합 키는 괄호 하나에 열을 함께 써요.': '실제 SQLite 오류(more than one primary key)를 학습자 수준으로 말해요.'},
        [([['print(rejected("INSERT INTO lots VALUES(?, ?)", (item, batch + 1)))\n', 'print(False)\n'], ['\n    PRIMARY KEY(item_id, batch)\n', '\n    PRIMARY KEY(item_id)\n']], 'Printing False without the pair key'),
         ([['\n    PRIMARY KEY(item_id, batch)\n', '\n    PRIMARY KEY(batch)\n']], 'Only the batch')],
        [([['\n    PRIMARY KEY(item_id, batch)\n', '\n    PRIMARY KEY(item_id, batch) ON CONFLICT ABORT\n']], 'Explicit default conflict clause')],
        [{'values': {'item': 1, 'batch': 1}, 'expected': 'True\nFalse'}, {'values': {'item': 5, 'batch': 3}, 'expected': 'True\nFalse'}],
        'cols = {r[1]: r[5] for r in db.execute("PRAGMA table_info(lots)")}\nassert cols["item_id"] == 1 and cols["batch"] == 2', 'True\nFalse')),
]
