from _engineer_final import code

SETUP = 'CREATE TABLE stocks(id INTEGER PRIMARY KEY, qty INTEGER);\nINSERT INTO stocks VALUES(1,2),(2,NULL),(3,0),(4,5);'
START = '''UPDATE stocks SET qty = 0 WHERE qty = NULL;
DELETE FROM stocks WHERE qty = 0;'''
SPEC = code('engineer-sql-change', '확인 안 된 재고를 정정한 다음 빈 재고 행을 지우세요',
    'NULL 조건과 여러 변경문의 실행 순서로 최종 표를 만들어요.',
    '먼저 qty를 모르는 행을 0으로 정정하고, 그다음 qty가 0인 모든 행을 삭제하세요. 양수 재고는 보존하세요. 실행 뒤 최종 표가 자동으로 조회돼요. 지금 1번 2개와 4번 5개만 남아야 해요.', 'sql', START,
    [('WHERE qty = NULL;', 'WHERE qty IS NULL;', '먼저 UPDATE의 NULL 비교를 IS NULL로 고치세요.')],
    'id | qty\n1 | 2\n4 | 5', ['id | qty\n1 | 2\n2 | NULL\n4 | 5', 'id | qty\n1 | 2\n4 | 5'],
    [dict(files={'setup.sql': SETUP.replace('(1,2),(2,NULL),(3,0),(4,5)', '(1,NULL),(2,6),(3,0),(4,NULL)')}, expected='id | qty\n2 | 6')],
    [([['UPDATE stocks SET qty = 0 WHERE qty IS NULL;\nDELETE FROM stocks WHERE qty = 0;', 'DELETE FROM stocks WHERE qty = 0;\nUPDATE stocks SET qty = 0 WHERE qty IS NULL;']], '삭제 후 정정하면 새 0 행이 남아요.')],
    [([['qty IS NULL', 'qty ISNULL']], 'SQLite의 ISNULL도 같은 NULL 조건이에요.')],
    'NULL 행은 정정되지 않아 2번이 남았어요.', '모르는 재고도 먼저 0이 돼 함께 삭제되고 양수 두 행은 그대로예요.',
    '조심하세요. DELETE를 먼저 하면 나중에 0으로 정정한 행은 삭제되지 않아요.',
    files={'setup.sql': SETUP, 'after.sql': 'SELECT id, qty FROM stocks ORDER BY id;'})
