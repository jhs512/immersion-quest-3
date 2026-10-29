from _engineer_final import code

START = '''CREATE TABLE deliveries (
    id INTEGER,
    item_id INTEGER,
    qty INTEGER
);
'''
AFTER = '''SELECT
 (SELECT COUNT(*) FROM pragma_table_info('deliveries') WHERE name='id' AND pk=1) AS pk,
 (SELECT COUNT(*) FROM pragma_table_info('deliveries') WHERE name='qty' AND "notnull"=1) AS required,
 (SELECT COUNT(*) FROM pragma_foreign_key_list('deliveries') WHERE "from"='item_id' AND "table"='items' AND "to"='id') AS links;'''
SPEC = code('engineer-db-model', '배송 표에 식별·필수값·참조 규칙을 선언하세요',
    '기본 키·NOT NULL·외래 키를 서로 다른 무결성 규칙으로 적용해요.',
    '실습 SQL 엔진은 SQLite예요. items(id 기본 키)는 준비돼 있어요. deliveries.id는 기본 키, qty는 필수값, item_id는 items.id를 참조하도록 표를 만드세요. 실행 뒤 세 규칙이 있으면 pk·required·links가 모두 1로 나와요.', 'sql', START,
    [('\n    id INTEGER,', '\n    id INTEGER PRIMARY KEY,', 'id에 PRIMARY KEY를 선언하세요.'),
     ('item_id INTEGER,', 'item_id INTEGER REFERENCES items(id),', 'item_id가 items의 id를 참조하게 하세요.'),
     ('qty INTEGER\n', 'qty INTEGER NOT NULL\n', 'qty에 NOT NULL을 선언하세요.')],
    'pk | required | links\n1 | 1 | 1', ['pk | required | links\n0 | 0 | 0', 'pk | required | links\n1 | 1 | 1'], [],
    [([['qty INTEGER NOT NULL', 'qty INTEGER']], '외래 키가 있어도 필수값 규칙은 별도로 필요해요.'),
     ([['REFERENCES items(id)', '']], '열 이름만 같아서는 외래 키가 아니에요.')],
    [([['item_id INTEGER REFERENCES items(id),', 'item_id INTEGER,\n    FOREIGN KEY (item_id) REFERENCES items(id),']], '표 수준 외래 키도 같은 규칙이에요.')],
    '열은 있지만 세 무결성 규칙은 없어 모두 0이에요.', '중복 식별 방지, 필수 수량, 기존 물건 참조를 각각 선언해 세 값이 1이에요.',
    '조심하세요. NOT NULL은 값의 존재를 검사하고 외래 키는 참조 대상의 존재를 검사해요.',
    files={'setup.sql': 'PRAGMA foreign_keys=ON;\nCREATE TABLE items(id INTEGER PRIMARY KEY);\nINSERT INTO items VALUES(1);', 'after.sql': AFTER})
