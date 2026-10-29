from _engineer_final import code

SETUP = '''CREATE TABLE stocks(id INTEGER PRIMARY KEY, category TEXT, qty INTEGER);
INSERT INTO stocks VALUES(1,'A',2),(2,'A',4),(3,'A',0),(4,'B',3),(5,'B',NULL),(6,'C',7),(7,'C',1);
'''
START = '''SELECT category, SUM(qty) AS total, COUNT(*) AS n
FROM stocks
GROUP BY category
HAVING COUNT(*) >= 1
ORDER BY category;'''
SPEC = code('engineer-sql-group', '양수 재고만 모아 기준을 넘는 분류를 보고하세요',
    '집계 전 행 조건과 집계 후 그룹 조건을 구별하고 결과 순서를 정해요.',
    'qty가 양수인 행만 모으세요. 그 행이 2개 이상이고 합계가 6 이상인 분류만 남기세요. 합계 내림차순, 동점이면 분류 오름차순으로 출력하세요. 지금 C 8 2 다음 A 6 2예요.', 'sql', START,
    [('FROM stocks\nGROUP BY', 'FROM stocks\nWHERE qty > 0\nGROUP BY', '양수 행만 먼저 거르세요.'),
     ('HAVING COUNT(*) >= 1', 'HAVING COUNT(*) >= 2 AND SUM(qty) >= 6', '그룹의 행 수와 합계가 모두 기준을 만족하게 하세요.'),
     ('ORDER BY category;', 'ORDER BY total DESC, category ASC;', '합계 내림차순 뒤 분류 오름차순으로 정렬하세요.')],
    'category | total | n\nC | 8 | 2\nA | 6 | 2', ['category | total | n\nA | 6 | 3\nB | 3 | 2\nC | 8 | 2', 'category | total | n\nC | 8 | 2\nA | 6 | 2'],
    [dict(files={'setup.sql': SETUP.replace("(6,'C',7)", "(6,'C',5)")}, expected='category | total | n\nA | 6 | 2\nC | 6 | 2')],
    [([['WHERE qty > 0', 'WHERE qty >= 0']], '0 재고 행은 집계 수에서도 빠져야 해요.'),
     ([['ORDER BY total DESC, category ASC;', 'ORDER BY total DESC, category DESC;']], '동점 분류 순서도 검사해요.')],
    [([['SUM(qty) >= 6', '6 <= SUM(qty)']], '비교 방향을 바꿔도 같은 합계 조건이에요.')],
    '0이나 NULL 행도 행 수에 들어가고 B까지 남았어요.', '양수만 집계해 C와 A를 남기고 합계가 큰 C부터 출력했어요.',
    '조심하세요. WHERE는 합치기 전 행을, HAVING은 합친 뒤 그룹을 거릅니다.', files={'setup.sql': SETUP})
