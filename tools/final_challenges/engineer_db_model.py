from _python_final import make

START = '''import sqlite3
parent_id = 1
missing_id = 99
db = sqlite3.connect(":memory:")
db.execute("PRAGMA foreign_keys=ON")
db.execute("CREATE TABLE items(id INTEGER PRIMARY KEY)")
db.execute("INSERT INTO items VALUES(?)", (parent_id,))
# 이 문자열 안의 SQL만 고치세요. 실행과 검사 코드는 준비돼 있어요.
schema = """CREATE TABLE deliveries (
    id INTEGER,
    item_id INTEGER,
    qty INTEGER
);"""
db.executescript(schema)
db.execute("INSERT INTO deliveries VALUES(1,?,2)", (parent_id,))
db.commit()
def rejected(sql, values):
    try:
        db.execute(sql, values)
        db.rollback()
        return False
    except sqlite3.IntegrityError:
        db.rollback()
        return True
# 중복 식별자, 필수값 누락, 없는 부모 참조를 각각 실제로 시도해요.
print(rejected("INSERT INTO deliveries VALUES(1,?,3)", (parent_id,)))
print(rejected("INSERT INTO deliveries VALUES(2,?,NULL)", (parent_id,)))
print(rejected("INSERT INTO deliveries VALUES(3,?,2)", (missing_id,)))
'''
SPEC = make('engineer-db-model', '배송 표에 식별·필수값·참조 규칙을 선언하세요',
    '실제 SQLite를 실행하는 Python 준비 코드예요. schema 문자열 안의 SQL만 고치세요. '
    'deliveries.id는 기본 키, qty는 필수값, item_id는 items.id를 참조하도록 정의하세요. '
    '준비된 검사는 중복 ID·NULL 수량·없는 물건 참조를 차례로 넣어 봐요. DB가 거절하면 True예요. 세 줄 모두 True가 되어야 해요.',
    '기본 키·NOT NULL·외래 키를 각각 실제 잘못된 삽입으로 검증해요.', START,
    [('\n    id INTEGER,', '\n    id INTEGER PRIMARY KEY,', 'schema의 id에 PRIMARY KEY를 선언하세요.'),
     ('item_id INTEGER,', 'item_id INTEGER REFERENCES items(id),', 'item_id가 items의 id를 참조하게 하세요.'),
     ('qty INTEGER\n', 'qty INTEGER NOT NULL\n', 'qty에 NOT NULL을 선언하세요.')],
    'True\nTrue\nTrue',
    [dict(values=dict(parent_id=7, missing_id=42), expected='True\nTrue\nTrue')],
    [([['qty INTEGER NOT NULL', 'qty INTEGER']], '필수 수량 규칙도 독립적으로 필요해요.'),
     ([['REFERENCES items(id)', '']], '열 이름만 같아서는 참조 규칙이 생기지 않아요.')],
    [([['item_id INTEGER REFERENCES items(id),\n    qty INTEGER NOT NULL', 'item_id INTEGER,\n    qty INTEGER NOT NULL,\n    FOREIGN KEY (item_id) REFERENCES items(id)']], '표 수준 외래 키도 같은 무결성 규칙이에요.')],
    '아직 제약이 없어 세 잘못된 삽입을 모두 허용해 False가 세 번 나와요.',
    '기본 키를 추가해 중복 ID만 거절해요. NULL 수량과 없는 물건 참조도 막아야 해요.',
    '중복 ID·NULL 수량·없는 물건 참조가 모두 실제 DB에서 거절됐어요.',
    '조심하세요. NOT NULL은 값의 존재를 검사하고 외래 키는 참조 대상의 존재를 검사해요.',
    probe='assert next(r for r in db.execute("PRAGMA table_info(deliveries)") if r[1] == "id")[5] == 1\nassert next(r for r in db.execute("PRAGMA table_info(deliveries)") if r[1] == "qty")[3] == 1\nassert any(r[2] == "items" and r[3] == "item_id" and r[4] == "id" for r in db.execute("PRAGMA foreign_key_list(deliveries)"))')
SPEC['course'] = 'engineer'
