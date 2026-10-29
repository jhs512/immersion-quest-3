from _engineer_final import code

SETUP = '''CREATE TABLE suppliers(id INTEGER PRIMARY KEY, name TEXT);
INSERT INTO suppliers VALUES(10,'north'),(20,'south');
CREATE TABLE items(id INTEGER PRIMARY KEY, stock INTEGER, supplier INTEGER);
INSERT INTO items VALUES(1,0,10),(2,NULL,20),(3,2,NULL),(4,5,10),(5,0,NULL);
'''
START = '''SELECT i.id, s.name AS supplier
FROM items i JOIN suppliers s ON s.id = i.supplier
WHERE i.stock = 0
ORDER BY i.id;'''
SPEC = code('engineer-sql-select', '재주문할 물건은 공급처가 없어도 남기세요',
    'NULL 조건과 외부 조인을 함께 써서 빠지는 재주문 대상을 찾아요.',
    '재고가 0이거나 아직 모르는 물건을 id순으로 조회하세요. 공급처가 없으면 물건은 남기고 supplier 열을 NULL로 표시하세요. 지금 ID 1·2·5가 나와야 해요.', 'sql', START,
    [('FROM items i JOIN suppliers s', 'FROM items i LEFT JOIN suppliers s', 'items를 기준으로 LEFT JOIN해 미등록 공급처의 물건도 남기세요.'),
     ('WHERE i.stock = 0', 'WHERE i.stock = 0 OR i.stock IS NULL', '재고가 0이거나 NULL인 두 경우를 포함하세요.')],
    'id | supplier\n1 | north\n2 | south\n5 | NULL', ['id | supplier\n1 | north', 'id | supplier\n1 | north\n2 | south\n5 | NULL'],
    [dict(files={'setup.sql': SETUP.replace('(3,2,NULL)', '(3,NULL,NULL)').replace('(5,0,NULL)', '(5,8,NULL)')}, expected='id | supplier\n1 | north\n2 | south\n3 | NULL')],
    [([['i.stock IS NULL', 'i.stock = NULL']], 'NULL은 등호로 고를 수 없어요.'),
     ([['LEFT JOIN', 'JOIN']], '공급처가 없는 물건도 재주문 대상이에요.')],
    [([['LEFT JOIN', 'LEFT OUTER JOIN']], 'OUTER를 명시해도 같은 조인이에요.')],
    '재고를 모르는 2번과 공급처가 없는 5번이 빠졌어요.', 'NULL 재고를 포함하고 공급처가 없는 5번도 남겨 세 행이 나왔어요.',
    '조심하세요. 외부 조인 뒤 공급처 열을 WHERE에서 필수로 요구하면 미일치 행이 다시 사라져요.', files={'setup.sql': SETUP})
