"""engineer-sql-change: 6 answer-picking DML/TCL steps -> statement-writing steps (2026-10-29).

The two PostgreSQL 18 GRANT/REVOKE steps stay answer-picking: SQLite cannot run DCL, so a real run
cannot grade them (classification.json)."""
from _kit import Script, todo, sql_output

OPENING = ['이 수업에서는 SQL로 바뀌는 행의 범위를 직접 문장을 고쳐 가며 확인해요. 자료 변경과 취소, 권한을 구별해요.',
           '추가·수정·삭제 뒤 실제 표를 확인해요. 트랜잭션과 저장 지점의 취소 범위로 이어가고, 권한은 명령의 뜻을 판단해요.']
PRD_SCOPE = ['세 챕터·세 단원·열한 스텝으로 같은 표의 변경과 권한을 다뤄요.',
             'DML/TCL은 문장을 직접 고쳐 실제 실행하고, SQLite가 실행할 수 없는 DCL(GRANT/REVOKE)은 제품 문법의 의미를 판단해요.']
PRD_GRADING = ['직접 쓴 DML/TCL을 실제 SQLite로 실행하고 after.sql로 바뀐 표 전체를 확인해요. 행을 바꾼 준비 표 두 개에서도 맞아야 해요.',
               '트랜잭션 스텝은 묶음 안에서 본 값과 끝난 뒤의 표를 함께 확인해 변경 자체를 지운 우회를 거절해요.',
               '권한 문제는 명시한 제품 문법의 의미를 직접 선택해요.',
               '마지막 도전(stp_c373e085-db0d-4fab-8d0a-a8e7258d7699): 시작 답안은 실패해야 해요. 실제 실행 결과 또는 각 서술형 답안 칸을 검사하고 오답과 동등한 정답도 대조해요.']
PRD_NARRATION = ['문장을 고치고 실행해 실제 표를 확인하는 일을 작게 반복해요.',
                 '표 변경과 권한 변경·전체 취소와 부분 취소를 조심할 지점으로 짚어요.']

SCHEMA = 'CREATE TABLE stocks(id INTEGER PRIMARY KEY, qty INTEGER);\n'
AFTER = 'SELECT id, qty FROM stocks ORDER BY id;'
BASE = {'setup.sql': SCHEMA + 'INSERT INTO stocks VALUES(1,2),(2,4),(3,NULL),(4,0);\n', 'after.sql': AFTER}
V1 = {'setup.sql': SCHEMA + 'INSERT INTO stocks VALUES(1,5),(2,0),(3,0),(6,NULL);\n'}
V2 = {'setup.sql': SCHEMA + 'INSERT INTO stocks VALUES(1,NULL),(2,3),(7,1);\n'}


def step(title, objectives, core_flow, goal, starter, solution, narration, review, reject, accept):
    return dict(title=title, objectives=objectives, core_flow=core_flow, goal=goal, starter_code=starter, solution=solution,
                files=BASE, narration=narration.actions, review=review, reject=reject, accept=accept,
                tests=[{'input': '', 'expected': sql_output(BASE, solution)}],
                variations=[{'files': v, 'expected': sql_output({**BASE, **v}, solution)} for v in (V1, V2)])


s1 = '-- 이 문장을 고쳐 기존 행은 그대로 두고 ID 5, 재고 7인 새 행을 넣으세요.\nUPDATE stocks SET qty = 7 WHERE id = 1;\n'
s1_solution = '-- 이 문장을 고쳐 기존 행은 그대로 두고 ID 5, 재고 7인 새 행을 넣으세요.\n-- INSERT는 새 행을 넣고, UPDATE는 이미 있는 행의 값을 고쳐요.\nINSERT INTO stocks VALUES(5, 7);\n'
n1 = (Script(s1)
      .say('새 ID 5로 재고 7을 넣어야 해요. 지금 문장은 기존 ID 1을 고쳐요.', 'text:문장을 고쳐 기존 행은 그대로 두고 ID 5, 재고 7인 새 행을 넣으세요.')
      .run('UPDATE stocks')
      .say('행은 그대로 네 개이고 ID 1의 재고만 7로 바뀌었어요.', 'output')
      .patch('UPDATE stocks SET qty = 7 WHERE id = 1;\n', 'INSERT INTO stocks VALUES(5, 7);\n', 'UPDATE 문장을 INSERT INTO stocks VALUES(5, 7)로 바꿔요.')
      .run('INSERT INTO')
      .say('다섯 행이에요. ID 1은 원래 2이고, 새 ID 5에 7이 들어갔어요.', 'output')
      .say('조심하세요. 이미 있는 ID로 INSERT하면 기본 키가 겹쳐 실패해요.', 'code:INSERT INTO stocks VALUES(5, 7);'))

s2 = '-- 이 문장에 WHERE를 더해 ID 1의 재고만 1 늘리세요.\nUPDATE stocks SET qty = qty + 1;\n'
s2_solution = '-- 이 문장에 WHERE를 더해 ID 1의 재고만 1 늘리세요.\n-- WHERE가 없으면 모든 행을 고쳐요. 조건에 맞는 행만 바뀌어요.\nUPDATE stocks SET qty = qty + 1 WHERE id = 1;\n'
n2 = (Script(s2)
      .say('ID 1의 재고만 늘려야 해요. 지금은 WHERE가 없어 모든 행을 고쳐요.', 'text:문장에 WHERE를 더해 ID 1의 재고만 1 늘리세요.')
      .run('UPDATE stocks')
      .say('3, 5, NULL, 1이에요. 모든 행이 1씩 늘었고 NULL은 더해도 NULL이에요.', 'output')
      .patch('SET qty = qty + 1;', 'SET qty = qty + 1 WHERE id = 1;', '문장 끝에 WHERE id = 1을 붙여요.')
      .run('UPDATE stocks')
      .say('ID 1만 3이 되고 나머지는 그대로예요.', 'output')
      .say('조심하세요. UPDATE와 DELETE는 WHERE를 빼면 표 전체에 적용돼요.', 'code:WHERE id = 1'))

s3 = '-- 이 문장에 WHERE를 더해 재고가 0인 행만 지우세요. 재고를 모르는 행은 남겨요.\nDELETE FROM stocks;\n'
s3_solution = '-- 이 문장에 WHERE를 더해 재고가 0인 행만 지우세요. 재고를 모르는 행은 남겨요.\n-- qty = 0은 NULL인 행에서 참이 아니라서 그 행은 지워지지 않아요.\nDELETE FROM stocks WHERE qty = 0;\n'
n3 = (Script(s3)
      .say('재고 0인 행만 지워야 해요. 재고를 모르는 ID 3은 남겨요.', 'text:문장에 WHERE를 더해 재고가 0인 행만 지우세요.')
      .run('DELETE FROM')
      .say('행 없음이에요. WHERE가 없어 표의 모든 행을 지웠어요.', 'output')
      .patch('DELETE FROM stocks;', 'DELETE FROM stocks WHERE qty = 0;', 'WHERE qty = 0을 붙여요.')
      .run('DELETE FROM')
      .say('1, 2, 3이 남았어요. 재고 0인 ID 4만 지워지고 NULL인 ID 3은 남았어요.', 'output')
      .say('조심하세요. NULL은 0이 아니에요. qty = 0은 모르는 재고를 지우지 않아요.', 'code:WHERE qty = 0'))

s4 = '-- 마지막 COMMIT을 고쳐 이 변경 묶음을 BEGIN 전으로 되돌리세요.\nBEGIN;\nUPDATE stocks SET qty = 9 WHERE id = 1;\nSELECT qty FROM stocks WHERE id = 1;\nCOMMIT;\n'
s4_solution = '-- 마지막 COMMIT을 고쳐 이 변경 묶음을 BEGIN 전으로 되돌리세요.\nBEGIN;\nUPDATE stocks SET qty = 9 WHERE id = 1;\nSELECT qty FROM stocks WHERE id = 1;\n-- ROLLBACK은 BEGIN 뒤의 변경을 모두 취소해요. 묶음 안에서는 9가 보였어도 확정되지 않아요.\nROLLBACK;\n'
n4 = (Script(s4)
      .say('BEGIN으로 시작한 묶음은 COMMIT하면 확정되고 ROLLBACK하면 되돌아가요. COMMIT을 ROLLBACK으로 고쳐야 해요.', 'text:마지막 COMMIT을 고쳐 이 변경 묶음을 BEGIN 전으로 되돌리세요.')
      .run('SELECT qty', 'COMMIT;')
      .say('묶음 안에서 9가 보였고, COMMIT 뒤의 표에도 ID 1이 9로 남았어요.', 'output')
      .patch('COMMIT;\n', 'ROLLBACK;\n', 'COMMIT을 ROLLBACK으로 바꿔요.')
      .run('SELECT qty', 'ROLLBACK;')
      .say('묶음 안에서는 9였지만, ROLLBACK 뒤의 표에서 ID 1은 원래 2예요.', 'output')
      .say('조심하세요. 묶음 안에서 바뀐 값이 보여도 COMMIT 전까지는 확정된 것이 아니에요.', 'code:ROLLBACK;'))

s5 = ('-- ROLLBACK 줄을 고쳐 저장 지점 middle 뒤의 변경만 취소하고, 그 아래에 COMMIT을 써서 확정하세요.\n'
      'BEGIN;\nUPDATE stocks SET qty = 3 WHERE id = 1;\nSAVEPOINT middle;\nUPDATE stocks SET qty = 9 WHERE id = 1;\nSELECT qty FROM stocks WHERE id = 1;\nROLLBACK;\n')
s5_solution = ('-- ROLLBACK 줄을 고쳐 저장 지점 middle 뒤의 변경만 취소하고, 그 아래에 COMMIT을 써서 확정하세요.\n'
               'BEGIN;\nUPDATE stocks SET qty = 3 WHERE id = 1;\nSAVEPOINT middle;\nUPDATE stocks SET qty = 9 WHERE id = 1;\nSELECT qty FROM stocks WHERE id = 1;\n'
               '-- ROLLBACK TO는 저장 지점 뒤의 변경만 취소하고 묶음은 계속돼요. COMMIT으로 3을 확정해요.\nROLLBACK TO middle;\nCOMMIT;\n')
n5 = (Script(s5)
      .say('저장 지점 middle 뒤의 9만 취소하고 3은 확정해야 해요.', 'text:ROLLBACK 줄을 고쳐 저장 지점 middle 뒤의 변경만 취소하고, 그 아래에 COMMIT을 써서 확정하세요.')
      .run('SELECT qty', 'ROLLBACK;')
      .say('묶음 안에서는 9였지만, 전체 ROLLBACK이 BEGIN 전으로 되돌려 ID 1은 2예요.', 'output')
      .patch('ROLLBACK;\n', 'ROLLBACK TO middle;\nCOMMIT;\n', 'ROLLBACK을 ROLLBACK TO middle로 고치고 아래에 COMMIT을 써요.')
      .run('SELECT qty', 'COMMIT;')
      .say('ID 1이 3이에요. 저장 지점 뒤의 9만 취소되고 그 앞의 3은 확정됐어요.', 'output')
      .say('조심하세요. ROLLBACK TO 뒤에도 묶음은 끝나지 않아요. COMMIT을 해야 확정돼요.', 'code:ROLLBACK TO middle;'))

s6 = '-- 이 문장에 조건을 더해 재고가 양수인 행만 ID에 10을 더해 복사하세요.\nINSERT INTO stocks(id, qty) SELECT id + 10, qty FROM stocks;\n'
s6_solution = '-- 이 문장에 조건을 더해 재고가 양수인 행만 ID에 10을 더해 복사하세요.\n-- INSERT ... SELECT는 조회 결과의 행들을 새 행으로 넣어요. WHERE가 복사할 행을 골라요.\nINSERT INTO stocks(id, qty) SELECT id + 10, qty FROM stocks WHERE qty > 0;\n'
n6 = (Script(s6)
      .say('조회 결과의 행을 새 행으로 넣어요. 재고가 양수인 행만 복사해야 해요.', 'text:문장에 조건을 더해 재고가 양수인 행만 ID에 10을 더해 복사하세요.')
      .run('INSERT INTO')
      .say('11부터 14까지 네 행이 더 생겼어요. NULL과 0인 행까지 모두 복사했어요.', 'output')
      .patch('SELECT id + 10, qty FROM stocks;', 'SELECT id + 10, qty FROM stocks WHERE qty > 0;', 'SELECT 끝에 WHERE qty > 0을 붙여요.')
      .run('INSERT INTO')
      .say('11과 12만 새로 생겼어요. 재고 2와 4인 행만 복사됐어요.', 'output')
      .say('조심하세요. 새 ID가 기존 ID와 겹치면 기본 키 때문에 문장 전체가 실패해요.', 'code:id + 10'))

SPECS = [
    dict(old='stp_dc797113-a7ed-444d-ab5c-86dedec06100', **step(
        'UPDATE를 INSERT로 고쳐 새 행을 넣으세요', ['INSERT와 UPDATE가 바꾸는 대상을 구별해요.'],
        'UPDATE stocks SET qty=7 WHERE id=1은 기존 행을 고친다. INSERT INTO stocks VALUES(5, 7)로 바꿔 다섯 행과 그대로인 ID 1을 확인한다. 채점은 행을 바꾼 표로도 after.sql 전체를 비교한다.',
        'stocks에는 ID 1~4 네 행이 있어요. INSERT는 새 행을 넣고, UPDATE는 이미 있는 행의 값을 고쳐요. 실행이 끝나면 준비된 확인 질의가 표 전체를 보여 줘요.\n\n'
        '문장을 고쳐 기존 행은 그대로 두고 ID 5, 재고 7인 새 행을 넣으세요. 채점은 행을 바꾼 표로도 실행해요.\n\n'
        + todo('코드 실행을 눌러 ID 1의 재고가 7로 바뀌는지 확인하세요.', 'UPDATE 문장을 `INSERT INTO stocks VALUES(5, 7);`로 바꾸세요.', '코드 실행을 눌러 ID 5인 새 행이 생기고 ID 1은 그대로인지 확인하세요.', '수정한 문장을 제출하세요.'),
        s1, s1_solution, n1,
        {'조심하세요. 이미 있는 ID로 INSERT하면 기본 키가 겹쳐 실패해요.': '실제 SQLite 동작(UNIQUE constraint failed)을 정확히 말해요.'},
        [([['INSERT INTO stocks VALUES(5, 7);', 'INSERT INTO stocks VALUES(5, 7);\nUPDATE stocks SET qty = 7 WHERE id = 1;']], 'Also changing ID 1'),
         ([['INSERT INTO stocks VALUES(5, 7);', 'INSERT INTO stocks VALUES(5, 2);']], 'Wrong stock')],
        [([['INSERT INTO stocks VALUES(5, 7);', 'INSERT INTO stocks(qty, id) VALUES(7, 5);']], 'Named columns in another order')])),
    dict(old='stp_bf300281-03df-4ff3-9f09-99bb813cca0a', **step(
        'WHERE id = 1을 더해 한 행의 재고만 늘리세요', ['UPDATE의 WHERE가 고칠 행을 정함을 확인해요.'],
        'WHERE 없는 UPDATE는 모든 행을 1씩 늘린다. WHERE id = 1을 더해 ID 1만 3이 되는 것을 확인한다. 채점은 행을 바꾼 표로도 after.sql 전체를 비교한다.',
        '`UPDATE ... SET qty = qty + 1`은 WHERE가 없으면 모든 행을 고쳐요. WHERE를 붙이면 조건에 맞는 행만 고쳐요.\n\n'
        '문장에 WHERE를 더해 ID 1의 재고만 1 늘리세요. 채점은 행을 바꾼 표로도 실행해요.\n\n'
        + todo('코드 실행을 눌러 모든 행이 늘어나는지 확인하세요.', '문장 끝에 `WHERE id = 1`을 붙이세요.', '코드 실행을 눌러 ID 1만 3이 되는지 확인하세요.', '수정한 문장을 제출하세요.'),
        s2, s2_solution, n2,
        {'3, 5, NULL, 1이에요. 모든 행이 1씩 늘었고 NULL은 더해도 NULL이에요.': '실제 출력과 SQL 의미(NULL + 1 = NULL)가 맞아요.',
         '조심하세요. UPDATE와 DELETE는 WHERE를 빼면 표 전체에 적용돼요.': '실제 SQL 의미를 정확히 말해요.'},
        [([['WHERE id = 1;', ';']], 'No WHERE'), ([['SET qty = qty + 1 WHERE id = 1;', 'SET qty = 3 WHERE id = 1;']], 'Typing the new value')],
        [([['SET qty = qty + 1 WHERE id = 1;', 'SET qty = 1 + qty WHERE 1 = id;']], 'Operands swapped')])),
    dict(old='stp_73f9f2cc-669d-475b-9164-631cdd0287ea', **step(
        'WHERE qty = 0을 더해 재고 0인 행만 지우세요', ['DELETE 조건과 NULL의 비교를 구별해요.'],
        'WHERE 없는 DELETE는 모든 행을 지운다. WHERE qty = 0을 더해 ID 4만 지워지고 NULL인 ID 3은 남는 것을 확인한다. 채점은 0이 여러 개인 표로도 after.sql 전체를 비교한다.',
        '`DELETE ... WHERE 조건`은 조건이 참인 행만 지워요. ID 3의 qty는 NULL(모름), ID 4는 0이에요. 모르는 재고는 지우지 않아요.\n\n'
        '문장에 WHERE를 더해 재고가 0인 행만 지우세요. 채점은 0인 행이 여러 개인 표로도 실행해요.\n\n'
        + todo('코드 실행을 눌러 모든 행이 지워지는지 확인하세요.', '문장 끝에 `WHERE qty = 0`을 붙이세요.', '코드 실행을 눌러 ID 4만 지워지는지 확인하세요.', '수정한 문장을 제출하세요.'),
        s3, s3_solution, n3,
        {'조심하세요. NULL은 0이 아니에요. qty = 0은 모르는 재고를 지우지 않아요.': '실제 SQL 삼값 논리를 정확히 말해요.'},
        [([['DELETE FROM stocks WHERE qty = 0;', 'DELETE FROM stocks WHERE id = 4;']], 'Deleting the id by hand'),
         ([['DELETE FROM stocks WHERE qty = 0;', 'DELETE FROM stocks WHERE qty = 0 OR qty IS NULL;']], 'Deleting the unknown stock too')],
        [([['DELETE FROM stocks WHERE qty = 0;', 'DELETE FROM stocks WHERE NOT qty <> 0;']], 'Negated inequality')])),
    dict(old='stp_f58afedd-a77e-4969-980d-1c9a508b9596', **step(
        'COMMIT을 ROLLBACK으로 고쳐 변경 묶음을 되돌리세요', ['ROLLBACK이 BEGIN 뒤의 변경을 모두 취소함을 확인해요.'],
        'BEGIN 뒤 qty=9로 바꾸고 묶음 안에서 9를 본다. COMMIT을 ROLLBACK으로 바꿔 끝난 뒤의 표에서 ID 1이 2인 것을 확인한다. 채점은 묶음 안 값과 끝난 뒤 표를 함께 비교한다.',
        'BEGIN으로 시작한 변경 묶음은 COMMIT하면 확정되고, ROLLBACK하면 BEGIN 전으로 되돌아가요. 준비 문장은 재고를 9로 바꾸고 묶음 안에서 한 번 조회해요.\n\n'
        '마지막 COMMIT을 고쳐 이 변경 묶음을 BEGIN 전으로 되돌리세요. UPDATE와 묶음 안의 조회는 그대로 둬요. 채점은 행을 바꾼 표로도 실행해요.\n\n'
        + todo('코드 실행을 눌러 묶음 안의 9와 끝난 뒤 표의 9를 확인하세요.', '`COMMIT;`을 `ROLLBACK;`으로 고치세요.', '코드 실행을 눌러 끝난 뒤 표에서 ID 1이 2인지 확인하세요.', '수정한 문장을 제출하세요.'),
        s4, s4_solution, n4,
        {'묶음 안에서는 9였지만, ROLLBACK 뒤의 표에서 ID 1은 원래 2예요.': '실제 두 출력(9와 2)과 맞는 대조예요.',
         '조심하세요. 묶음 안에서 바뀐 값이 보여도 COMMIT 전까지는 확정된 것이 아니에요.': '실제 트랜잭션 의미를 정확히 말해요. 「보여도」 대조가 실제 출력과 맞아요.'},
        [([['UPDATE stocks SET qty = 9 WHERE id = 1;\n', ''], ['ROLLBACK;\n', 'COMMIT;\n']], 'Removing the change instead of rolling back'),
         ([['ROLLBACK;\n', 'COMMIT;\nUPDATE stocks SET qty = 2 WHERE id = 1;\n']], 'Writing the old value back by hand')],
        [([['ROLLBACK;\n', 'ROLLBACK TRANSACTION;\n']], 'ROLLBACK TRANSACTION')])),
    dict(old='stp_37ce9c6a-74d8-4023-91a5-81c650f7571d', **step(
        'ROLLBACK TO middle로 저장 지점 뒤만 취소하고 확정하세요', ['저장 지점까지의 부분 취소와 전체 취소를 구별해요.'],
        '3으로 바꾸고 SAVEPOINT middle 뒤 9로 바꾼다. 전체 ROLLBACK은 2로 되돌린다. ROLLBACK TO middle과 COMMIT으로 고쳐 3을 확인한다. 채점은 묶음 안 값과 끝난 뒤 표를 함께 비교한다.',
        '`SAVEPOINT middle`은 묶음 안의 중간 저장 지점이에요. `ROLLBACK TO middle`은 그 지점 뒤의 변경만 취소하고 묶음은 계속돼요. 지금 마지막 줄은 묶음 전체를 취소해요.\n\n'
        'ROLLBACK 줄을 고쳐 저장 지점 middle 뒤의 변경만 취소하고, 그 아래에 COMMIT을 써서 확정하세요. 채점은 행을 바꾼 표로도 실행해요.\n\n'
        + todo('코드 실행을 눌러 끝난 뒤 표에서 ID 1이 2인지 확인하세요.', '`ROLLBACK;`을 `ROLLBACK TO middle;`로 고치세요.', '그 아래에 `COMMIT;`을 쓰세요.',
               '코드 실행을 눌러 ID 1이 3인지 확인하세요.', '수정한 문장을 제출하세요.'),
        s5, s5_solution, n5,
        {'묶음 안에서는 9였지만, 전체 ROLLBACK이 BEGIN 전으로 되돌려 ID 1은 2예요.': '실제 두 출력(9와 2)과 맞는 대조예요.',
         '조심하세요. ROLLBACK TO 뒤에도 묶음은 끝나지 않아요. COMMIT을 해야 확정돼요.': '실제 SQLite 의미를 정확히 말해요.'},
        [([['ROLLBACK TO middle;\nCOMMIT;\n', 'COMMIT;\n']], 'Committing the 9'),
         ([['UPDATE stocks SET qty = 9 WHERE id = 1;\n', ''], ['ROLLBACK TO middle;\nCOMMIT;\n', 'COMMIT;\n']], 'Removing the change instead of rolling back')],
        [([['ROLLBACK TO middle;\nCOMMIT;\n', 'ROLLBACK TO SAVEPOINT middle;\nRELEASE middle;\nCOMMIT;\n']], 'With SAVEPOINT keyword and RELEASE')])),
    dict(old='stp_21e2172c-4f17-468a-b8cd-d1301b1925b3', **step(
        'WHERE qty > 0을 더해 양수 재고 행만 복사하세요', ['INSERT ... SELECT가 조회 결과의 행을 새 행으로 넣음을 확인해요.'],
        'INSERT INTO stocks SELECT id+10, qty FROM stocks는 네 행을 모두 복사한다. WHERE qty > 0을 더해 11과 12만 생기는 것을 확인한다. 채점은 행을 바꾼 표로도 after.sql 전체를 비교한다.',
        '`INSERT INTO ... SELECT`는 조회 결과의 행들을 새 행으로 넣어요. 준비 문장은 ID에 10을 더해 모든 행을 복사해요.\n\n'
        '문장에 조건을 더해 재고가 양수인 행만 ID에 10을 더해 복사하세요. 채점은 행을 바꾼 표로도 실행해요.\n\n'
        + todo('코드 실행을 눌러 11~14 네 행이 생기는지 확인하세요.', 'SELECT 끝에 `WHERE qty > 0`을 붙이세요.', '코드 실행을 눌러 11과 12만 생기는지 확인하세요.', '수정한 문장을 제출하세요.'),
        s6, s6_solution, n6,
        {'조심하세요. 새 ID가 기존 ID와 겹치면 기본 키 때문에 문장 전체가 실패해요.': '실제 SQLite 동작을 정확히 말해요.'},
        [([['FROM stocks WHERE qty > 0;', 'FROM stocks WHERE qty >= 0;']], 'Copying zero stock too'),
         ([['INSERT INTO stocks(id, qty) SELECT id + 10, qty FROM stocks WHERE qty > 0;', 'INSERT INTO stocks VALUES(11, 2), (12, 4);']], 'Typing the rows')],
        [([['FROM stocks WHERE qty > 0;', 'FROM stocks WHERE qty IS NOT NULL AND qty <> 0 AND qty > 0;']], 'Extra but harmless conditions')])),
]
