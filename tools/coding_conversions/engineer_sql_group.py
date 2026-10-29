"""engineer-sql-group: 9 answer-picking steps -> query-writing steps (2026-10-29)."""
from _kit import Script, todo, sql_output

OPENING = ['이 수업에서는 집계의 대상과 그룹 기준을 질의로 직접 써 가며 배워요. 행 조건과 그룹 조건을 구별해요.',
           'NULL과 중복이 있는 자료를 묶어요. 순위·분할·누적 창도 직접 쓰고, 값을 바꾼 표로도 확인해요.']
PRD_SCOPE = ['SQLite 실제 실행과 방언 차이 안내를 함께 제공해요.',
             '같은 재고 표에서 집계 함수·GROUP BY·HAVING·WHERE·COUNT(DISTINCT)·RANK·PARTITION BY·누적 창을 질의 한 곳씩 직접 고쳐 써요.']
PRD_GRADING = ['직접 쓴 질의를 실제 SQLite로 실행하고, 값·NULL·분류를 바꾼 준비 표 두 개에서도 확인해요.',
               '결과를 글자로 적거나 비슷한 다른 집계·순위 함수를 쓴 답은 거절해요.',
               '마지막 도전(stp_5c00ddd4-5de1-497b-85d6-15f8c7989885): 시작 답안은 실패해야 해요. 실제 실행 결과 또는 각 서술형 답안 칸을 검사하고 오답과 동등한 정답도 대조해요.']
PRD_NARRATION = ['작은 수정·실행·결과 읽기를 반복해요.',
                 '준비 질의의 결과를 먼저 읽고, 한 곳을 고친 뒤 다시 실행해 차이를 짚어요.']

SCHEMA = 'CREATE TABLE stocks(id INTEGER PRIMARY KEY, category TEXT, qty INTEGER, price INTEGER);\n'
BASE = {'setup.sql': SCHEMA + "INSERT INTO stocks VALUES(1,'A',2,10),(2,'A',4,10),(3,'B',NULL,5),(4,'B',0,2);\n"}
V1 = {'setup.sql': SCHEMA + "INSERT INTO stocks VALUES(1,'A',NULL,8),(2,'B',5,8),(3,'C',1,8),(4,'B',3,6),(5,'A',NULL,1);\n"}
V2 = {'setup.sql': SCHEMA + "INSERT INTO stocks VALUES(1,'B',6,3),(2,'A',1,9),(3,'B',2,9);\n"}


def step(title, objectives, core_flow, goal, starter, solution, narration, review, reject, accept):
    return dict(title=title, objectives=objectives, core_flow=core_flow, goal=goal, starter_code=starter, solution=solution,
                files=BASE, narration=narration.actions, review=review, reject=reject, accept=accept,
                tests=[{'input': '', 'expected': sql_output(BASE, solution)}],
                variations=[{'files': v, 'expected': sql_output(v, solution)} for v in (V1, V2)])


s1 = '-- 이 질의를 고쳐 qty가 NULL인 행까지 전체 행 수를 세세요.\nSELECT COUNT(qty) AS n FROM stocks;\n'
s1_solution = '-- 이 질의를 고쳐 qty가 NULL인 행까지 전체 행 수를 세세요.\n-- COUNT(*)는 행을, COUNT(qty)는 qty에 값이 있는 행만 세요.\nSELECT COUNT(*) AS n FROM stocks;\n'
n1 = (Script(s1)
      .say('ID 3의 qty는 NULL이에요. NULL인 행까지 전체 행 수를 세게 고쳐야 해요.', 'text:질의를 고쳐 qty가 NULL인 행까지 전체 행 수를 세세요.')
      .run('SELECT COUNT(')
      .say('3이에요. COUNT(qty)는 qty에 값이 있는 행만 세었어요.', 'output')
      .patch('COUNT(qty)', 'COUNT(*)', 'COUNT 안을 별표로 바꿔요.')
      .run('SELECT COUNT(')
      .say('4예요. 값과 상관없이 행을 모두 세었어요.', 'output')
      .say('조심하세요. 재고 0도 값이에요. COUNT(qty)가 빼는 것은 NULL뿐이에요.', 'code:COUNT(*)'))

s2 = '-- 이 질의를 고쳐 알려진 qty를 모두 더한 합계를 구하세요.\nSELECT AVG(qty) AS amount FROM stocks;\n'
s2_solution = '-- 이 질의를 고쳐 알려진 qty를 모두 더한 합계를 구하세요.\n-- SUM과 AVG는 NULL을 빼고 계산해요. AVG의 분모도 값이 있는 행 수예요.\nSELECT SUM(qty) AS amount FROM stocks;\n'
n2 = (Script(s2)
      .say('qty는 2, 4, NULL, 0이에요. 평균이 아니라 알려진 재고를 모두 더한 합계가 필요해요.', 'text:질의를 고쳐 알려진 qty를 모두 더한 합계를 구하세요.')
      .run('SELECT ')
      .say('2.0이에요. AVG는 NULL을 빼고 2, 4, 0 세 값으로 나눴어요.', 'output')
      .patch('AVG(qty)', 'SUM(qty)', 'AVG를 SUM으로 바꿔요.')
      .run('SELECT ')
      .say('6이에요. 알려진 2, 4, 0을 더했어요.', 'output')
      .say('조심하세요. AVG의 분모는 네 행이 아니라 값이 있는 세 행이라 1.5가 아니에요.', 'code:SUM(qty)'))

s3 = '-- 이 질의에 GROUP BY를 더해 분류별 합계를 한 행씩 내세요.\nSELECT category, SUM(qty) AS n FROM stocks ORDER BY category;\n'
s3_solution = '-- 이 질의에 GROUP BY를 더해 분류별 합계를 한 행씩 내세요.\n-- GROUP BY category는 분류가 같은 행끼리 묶어 묶음마다 SUM을 한 행씩 내요.\nSELECT category, SUM(qty) AS n FROM stocks GROUP BY category ORDER BY category;\n'
n3 = (Script(s3)
      .say('분류가 같은 행끼리 묶어 합계를 내야 해요. GROUP BY를 더해요.', 'text:질의에 GROUP BY를 더해 분류별 합계를 한 행씩 내세요.')
      .run('SELECT category')
      .say('한 행만 나와요. GROUP BY가 없으면 전체를 한 묶음으로 더해요.', 'output')
      .patch('FROM stocks ORDER BY', 'FROM stocks GROUP BY category ORDER BY', 'FROM stocks 뒤에 GROUP BY category를 써요.')
      .run('SELECT category')
      .say('A는 6, B는 0이에요. 분류마다 한 행씩 합계를 냈어요.', 'output')
      .say('조심하세요. SQLite는 GROUP BY 없이 category를 써도 오류를 내지 않지만, 그 category는 임의의 한 행에서 온 값이에요.', 'code:GROUP BY category'))

s4 = '-- 이 질의에 HAVING을 더해 분류 합계가 5 이상인 분류만 남기세요.\nSELECT category, SUM(qty) AS n FROM stocks GROUP BY category ORDER BY category;\n'
s4_solution = '-- 이 질의에 HAVING을 더해 분류 합계가 5 이상인 분류만 남기세요.\n-- HAVING은 묶은 뒤 그룹의 집계값에 거는 조건이에요.\nSELECT category, SUM(qty) AS n FROM stocks GROUP BY category HAVING SUM(qty) >= 5 ORDER BY category;\n'
n4 = (Script(s4)
      .say('묶은 뒤의 합계로 분류를 골라야 해요. GROUP BY 뒤에 HAVING을 써요.', 'text:질의에 HAVING을 더해 분류 합계가 5 이상인 분류만 남기세요.')
      .run('SELECT category')
      .say('A는 6, B는 0이에요. 아직 두 분류가 모두 남아요.', 'output')
      .patch('GROUP BY category ORDER BY', 'GROUP BY category HAVING SUM(qty) >= 5 ORDER BY', 'GROUP BY 뒤에 HAVING SUM(qty) >= 5를 써요.')
      .run('SELECT category')
      .say('A만 남았어요. 합계 6만 5 이상이에요.', 'output')
      .say('조심하세요. WHERE qty >= 5는 묶기 전 행마다 걸러서 재고 5 이상인 행이 없는 이 표에서는 아무것도 남지 않아요.', 'code:HAVING SUM(qty) >= 5'))

s5 = '-- 이 질의에 WHERE를 더해 qty가 3 이상인 행만 남긴 뒤 분류별로 더하세요.\nSELECT category, SUM(qty) AS n FROM stocks GROUP BY category ORDER BY category;\n'
s5_solution = '-- 이 질의에 WHERE를 더해 qty가 3 이상인 행만 남긴 뒤 분류별로 더하세요.\n-- WHERE는 묶기 전에 행을 걸러요. 남은 행만 묶여 더해져요.\nSELECT category, SUM(qty) AS n FROM stocks WHERE qty >= 3 GROUP BY category ORDER BY category;\n'
n5 = (Script(s5)
      .say('묶기 전에 qty가 3 이상인 행만 남겨야 해요. WHERE는 FROM 바로 뒤에 와요.', 'text:질의에 WHERE를 더해 qty가 3 이상인 행만 남긴 뒤 분류별로 더하세요.')
      .run('SELECT category')
      .say('A는 6, B는 0이에요. 모든 행을 묶었어요.', 'output')
      .patch('FROM stocks GROUP BY', 'FROM stocks WHERE qty >= 3 GROUP BY', 'FROM stocks 뒤에 WHERE qty >= 3을 써요.')
      .run('SELECT category')
      .say('A의 4만 남았어요. 재고 4인 행만 걸러진 뒤 묶였고, B는 남은 행이 없어 사라졌어요.', 'output')
      .say('조심하세요. HAVING SUM(qty) >= 3은 묶은 뒤 합계로 고르므로 A의 합계 6이 그대로 나와요.', 'code:WHERE qty >= 3'))

s6 = '-- 이 질의를 고쳐 중복 없는 분류의 수를 세세요.\nSELECT COUNT(category) AS n FROM stocks;\n'
s6_solution = '-- 이 질의를 고쳐 중복 없는 분류의 수를 세세요.\n-- 집계 안의 DISTINCT는 같은 분류 값을 하나로 줄인 뒤 세요.\nSELECT COUNT(DISTINCT category) AS n FROM stocks;\n'
n6 = (Script(s6)
      .say('분류 값이 A, A, B, B예요. 중복을 뺀 분류의 수를 세야 해요.', 'text:질의를 고쳐 중복 없는 분류의 수를 세세요.')
      .run('SELECT COUNT(')
      .say('4예요. 분류가 있는 행을 모두 세었어요.', 'output')
      .patch('COUNT(category)', 'COUNT(DISTINCT category)', 'COUNT 괄호 안에 DISTINCT를 써요.')
      .run('SELECT COUNT(')
      .say('2예요. A와 B 두 종류예요.', 'output')
      .say('조심하세요. SELECT DISTINCT COUNT(category)는 결과 한 행의 중복을 없앨 뿐이라 여전히 4예요.', 'code:COUNT(DISTINCT category)'))

s7 = '-- 이 순위 함수를 고쳐 같은 가격은 같은 순위, 그다음은 동점 수만큼 건너뛰게 하세요.\nSELECT id, ROW_NUMBER() OVER(ORDER BY price DESC) AS r FROM stocks ORDER BY id;\n'
s7_solution = '-- 이 순위 함수를 고쳐 같은 가격은 같은 순위, 그다음은 동점 수만큼 건너뛰게 하세요.\n-- RANK는 동점에 같은 순위를 주고 다음 순위를 건너뛰어요. DENSE_RANK는 건너뛰지 않아요.\nSELECT id, RANK() OVER(ORDER BY price DESC) AS r FROM stocks ORDER BY id;\n'
n7 = (Script(s7)
      .say('ID 1과 2는 가격이 같은 10이에요. 동점에 같은 순위를 주는 함수로 바꿔야 해요.', 'text:순위 함수를 고쳐 같은 가격은 같은 순위, 그다음은 동점 수만큼 건너뛰게 하세요.')
      .run('SELECT id,')
      .say('1, 2, 3, 4예요. ROW_NUMBER는 동점이어도 번호를 따로 매겨요.', 'output')
      .patch('ROW_NUMBER()', 'RANK()', 'ROW_NUMBER를 RANK로 바꿔요.')
      .run('SELECT id,')
      .say('1, 1, 3, 4예요. 1등이 둘이라 다음은 3등이에요.', 'output')
      .say('조심하세요. DENSE_RANK였다면 동점 다음이 2등이에요.', 'code:RANK() OVER(ORDER BY price DESC)'))

s8 = '-- 이 창에 PARTITION BY를 더해 분류마다 번호를 1부터 다시 매기세요.\nSELECT id, ROW_NUMBER() OVER(ORDER BY id) AS r FROM stocks ORDER BY id;\n'
s8_solution = '-- 이 창에 PARTITION BY를 더해 분류마다 번호를 1부터 다시 매기세요.\n-- PARTITION BY category는 분류마다 따로 창을 나눠요. 행은 지우지 않아요.\nSELECT id, ROW_NUMBER() OVER(PARTITION BY category ORDER BY id) AS r FROM stocks ORDER BY id;\n'
n8 = (Script(s8)
      .say('분류가 바뀌면 번호가 1부터 다시 시작해야 해요. OVER 안에 PARTITION BY를 더해요.', 'text:창에 PARTITION BY를 더해 분류마다 번호를 1부터 다시 매기세요.')
      .run('SELECT id,')
      .say('1, 2, 3, 4예요. 전체를 한 창으로 번호를 매겼어요.', 'output')
      .patch('OVER(ORDER BY id)', 'OVER(PARTITION BY category ORDER BY id)', 'OVER 괄호 맨 앞에 PARTITION BY category를 써요.')
      .run('SELECT id,')
      .say('1, 2, 1, 2예요. B 분류의 ID 3에서 번호가 1로 다시 시작했어요.', 'output')
      .say('조심하세요. 윈도우 함수는 GROUP BY와 달리 행을 줄이지 않아요. 네 행이 그대로 남아요.', 'code:PARTITION BY category'))

s9 = '-- 이 창을 고쳐 ID 순서로 첫 행부터 지금 행까지의 누적 합을 보이세요.\nSELECT id, SUM(qty) OVER() AS n FROM stocks ORDER BY id;\n'
s9_solution = ('-- 이 창을 고쳐 ID 순서로 첫 행부터 지금 행까지의 누적 합을 보이세요.\n'
               '-- 창 안의 ORDER BY와 ROWS 범위가 「처음부터 지금 행까지」를 정해요. NULL은 더하지 않아요.\n'
               'SELECT id, SUM(qty) OVER(ORDER BY id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS n FROM stocks ORDER BY id;\n')
n9 = (Script(s9)
      .say('지금은 모든 행에 전체 합계가 보여요. ID 순서로 지금 행까지의 합만 보이게 창을 고쳐야 해요.', 'text:창을 고쳐 ID 순서로 첫 행부터 지금 행까지의 누적 합을 보이세요.')
      .run('SELECT id,')
      .say('모든 행이 6이에요. 빈 OVER()는 전체를 한 창으로 더해요.', 'output')
      .patch('OVER()', 'OVER(ORDER BY id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)', 'OVER 안에 ORDER BY id와 처음부터 지금 행까지의 범위를 써요.')
      .run('SELECT id,')
      .say('2, 6, 6, 6이에요. NULL인 ID 3과 재고 0인 ID 4에서는 누적 합이 그대로예요.', 'output')
      .say('조심하세요. 창의 ORDER BY는 누적 순서를, 맨 끝 ORDER BY는 결과를 보여 줄 순서만 정해요.', 'code:OVER(ORDER BY id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)'))

SPECS = [
    dict(old='stp_5bd0f589-2a7b-474b-b2bf-736f896921ff', **step(
        'COUNT(*)로 NULL 행까지 모든 행을 세세요', ['COUNT(*)와 COUNT(열)이 세는 대상을 구별해요.'],
        'COUNT(qty)는 NULL을 빼 3이다. COUNT(*)로 고쳐 4를 확인한다. 채점은 NULL 수가 다른 표로도 실행한다.',
        'stocks에는 네 물건이 있고 ID 3의 qty는 NULL이에요. `COUNT(*)`는 행을, `COUNT(열)`은 그 열에 값이 있는 행을 세요.\n\n'
        '질의를 고쳐 qty가 NULL인 행까지 전체 행 수를 세세요. 채점은 NULL 수가 다른 표로도 실행해요.\n\n'
        + todo('코드 실행을 눌러 3이 나오는지 확인하세요.', '`COUNT(qty)`를 `COUNT(*)`로 고치세요.', '코드 실행을 눌러 4가 나오는지 확인하세요.', '수정한 질의를 제출하세요.'),
        s1, s1_solution, n1,
        {'조심하세요. 재고 0도 값이에요. COUNT(qty)가 빼는 것은 NULL뿐이에요.': '실제 SQL 의미를 정확히 말해요.'},
        [([['SELECT COUNT(*) AS n', 'SELECT COUNT(qty) AS n']], 'Only known values'), ([['SELECT COUNT(*) AS n FROM stocks;', 'SELECT 4 AS n;']], 'Typing the count')],
        [([['SELECT COUNT(*) AS n', 'SELECT COUNT(id) AS n']], 'Counting the never-NULL key')])),
    dict(old='stp_7bf866e4-1440-4cec-b230-17d32c9b6b4f', **step(
        'SUM으로 알려진 재고의 합계를 구하세요', ['SUM과 AVG가 NULL을 빼고 계산함을 확인해요.'],
        'AVG(qty)는 NULL을 뺀 세 값의 평균 2.0이다. SUM(qty)로 고쳐 6을 확인한다. 채점은 값이 다른 표로도 실행한다.',
        'qty는 2, 4, NULL, 0이에요. `SUM`과 `AVG`는 NULL을 빼고 계산해요. 그래서 AVG의 분모도 값이 있는 행의 수예요.\n\n'
        '질의를 고쳐 알려진 qty를 모두 더한 합계를 구하세요. 채점은 값이 다른 표로도 실행해요.\n\n'
        + todo('코드 실행을 눌러 2.0이 나오는지 확인하세요.', '`AVG(qty)`를 `SUM(qty)`로 고치세요.', '코드 실행을 눌러 6이 나오는지 확인하세요.', '수정한 질의를 제출하세요.'),
        s2, s2_solution, n2,
        {'조심하세요. AVG의 분모는 네 행이 아니라 값이 있는 세 행이라 1.5가 아니에요.': '실제 SQL 의미와 실제 값(2.0)으로 오개념(1.5)을 정확히 짚어요.'},
        [([['SUM(qty)', 'AVG(qty)']], 'Average instead of sum'), ([['SELECT SUM(qty) AS amount FROM stocks;', 'SELECT 6 AS amount;']], 'Typing the sum')],
        [([['SELECT SUM(qty) AS amount FROM stocks;', 'SELECT SUM(coalesce(qty, 0)) AS amount FROM stocks;']], 'NULL as zero gives the same sum')])),
    dict(old='stp_84cef749-ba19-4d41-9d67-b81cc742a8ce', **step(
        'GROUP BY category로 분류별 합계를 내세요', ['GROUP BY가 같은 값끼리 묶어 묶음마다 한 행을 냄을 확인해요.'],
        'GROUP BY 없이 SUM하면 전체 한 행이다. GROUP BY category를 더해 A 6, B 0을 확인한다. 채점은 분류가 다른 표로도 실행한다.',
        '`GROUP BY category`는 분류가 같은 행끼리 묶어, 묶음마다 집계를 한 행씩 내요. 지금 질의에는 GROUP BY가 없어서 전체가 한 묶음이에요.\n\n'
        '질의에 GROUP BY를 더해 분류별 합계를 한 행씩 내세요. 채점은 분류가 다른 표로도 실행해요.\n\n'
        + todo('코드 실행을 눌러 한 행만 나오는지 확인하세요.', '`FROM stocks` 뒤에 `GROUP BY category`를 쓰세요.', '코드 실행을 눌러 A와 B가 각각 나오는지 확인하세요.', '수정한 질의를 제출하세요.'),
        s3, s3_solution, n3,
        {'조심하세요. SQLite는 GROUP BY 없이 category를 써도 오류를 내지 않지만, 그 category는 임의의 한 행에서 온 값이에요.': '실제 SQLite 동작(bare column)과 다른 DBMS의 차이를 정확히 말해요. 「않지만」 대조가 맞아요.'},
        [([["SELECT category, SUM(qty) AS n FROM stocks GROUP BY category ORDER BY category;", "SELECT 'A' AS category, 6 AS n UNION ALL SELECT 'B', 0;"]], 'Typing the rows')],
        [([['GROUP BY category ORDER BY', 'GROUP BY 1 ORDER BY']], 'Group by the first column')])),
    dict(old='stp_2d84191f-6af1-4b64-a8af-fe7c9f28607f', **step(
        'HAVING으로 합계가 5 이상인 분류만 남기세요', ['그룹 집계값에 거는 HAVING과 행 조건 WHERE를 구별해요.'],
        'GROUP BY category 뒤에 HAVING SUM(qty) >= 5를 더해 A만 남는 것을 확인한다. WHERE qty >= 5는 묶기 전 행을 걸러 결과가 비어 버린다. 채점은 값이 다른 표로도 실행한다.',
        '`HAVING`은 GROUP BY로 묶은 뒤 그룹의 집계값에 거는 조건이에요. 분류 합계가 5 이상인 분류만 보려 해요.\n\n'
        '질의에 HAVING을 더해 분류 합계가 5 이상인 분류만 남기세요. 채점은 값이 다른 표로도 실행해요.\n\n'
        + todo('코드 실행을 눌러 A와 B가 모두 나오는지 확인하세요.', '`GROUP BY category` 뒤에 `HAVING SUM(qty) >= 5`를 쓰세요.', '코드 실행을 눌러 A만 나오는지 확인하세요.', '수정한 질의를 제출하세요.'),
        s4, s4_solution, n4,
        {'조심하세요. WHERE qty >= 5는 묶기 전 행마다 걸러서 재고 5 이상인 행이 없는 이 표에서는 아무것도 남지 않아요.': '실제 흔한 혼동과 이 표에서의 실제 결과를 말해요.'},
        [([['FROM stocks GROUP BY category HAVING SUM(qty) >= 5', 'FROM stocks WHERE qty >= 5 GROUP BY category']], 'Row filter instead of group filter'),
         ([['HAVING SUM(qty) >= 5', "HAVING category = 'A'"]], 'Picking the category by hand')],
        [([['HAVING SUM(qty) >= 5', 'HAVING n >= 5']], 'Using the alias')])),
    dict(old='stp_7155b2a4-71c0-4f85-baf8-3c33bb06ac6d', **step(
        'WHERE로 행을 먼저 거른 뒤 분류별로 더하세요', ['WHERE가 묶기 전에 행을 거르는 순서를 확인해요.'],
        'GROUP BY 앞에 WHERE qty >= 3을 더해 A 합계 4만 남는 것을 확인한다. HAVING으로 쓰면 묶은 뒤 합계로 걸러 A 6이 된다. 채점은 값이 다른 표로도 실행한다.',
        '`WHERE`는 묶기 전에 행을 거르는 조건이에요. qty가 3 이상인 행만 남긴 뒤 분류별로 더해요.\n\n'
        '질의에 WHERE를 더해 qty가 3 이상인 행만 남긴 뒤 분류별로 더하세요. 채점은 값이 다른 표로도 실행해요.\n\n'
        + todo('코드 실행을 눌러 A 6과 B 0이 나오는지 확인하세요.', '`FROM stocks` 뒤에 `WHERE qty >= 3`을 쓰세요.', '코드 실행을 눌러 A 4만 나오는지 확인하세요.', '수정한 질의를 제출하세요.'),
        s5, s5_solution, n5,
        {'조심하세요. HAVING SUM(qty) >= 3은 묶은 뒤 합계로 고르므로 A의 합계 6이 그대로 나와요.': '실제 혼동과 실제 결과를 말해요.'},
        [([['FROM stocks WHERE qty >= 3 GROUP BY category', 'FROM stocks GROUP BY category HAVING SUM(qty) >= 3']], 'Group filter instead of row filter')],
        [([['WHERE qty >= 3', 'WHERE NOT qty < 3']], 'Negated comparison')])),
    dict(old='stp_48327545-cfb5-4bc0-ac9e-fba78f15aefe', **step(
        'COUNT(DISTINCT category)로 분류 종류 수를 세세요', ['집계 안의 DISTINCT로 중복 값을 빼고 세요.'],
        'COUNT(category)는 4다. COUNT(DISTINCT category)로 고쳐 2를 확인한다. 채점은 분류 종류가 다른 표로도 실행한다.',
        '`COUNT(DISTINCT category)`는 집계 안에서 분류 값의 중복을 빼고 세요. 지금 질의는 분류가 있는 행을 모두 세요.\n\n'
        '질의를 고쳐 중복 없는 분류의 수를 세세요. 채점은 분류 종류가 다른 표로도 실행해요.\n\n'
        + todo('코드 실행을 눌러 4가 나오는지 확인하세요.', '`COUNT(category)`를 `COUNT(DISTINCT category)`로 고치세요.', '코드 실행을 눌러 2가 나오는지 확인하세요.', '수정한 질의를 제출하세요.'),
        s6, s6_solution, n6,
        {'조심하세요. SELECT DISTINCT COUNT(category)는 결과 한 행의 중복을 없앨 뿐이라 여전히 4예요.': '실제 흔한 실수와 실제 결과를 말해요.'},
        [([['SELECT COUNT(DISTINCT category) AS n', 'SELECT DISTINCT COUNT(category) AS n']], 'DISTINCT outside the aggregate'), ([['SELECT COUNT(DISTINCT category) AS n FROM stocks;', 'SELECT 2 AS n;']], 'Typing the count')],
        [([['SELECT COUNT(DISTINCT category) AS n FROM stocks;', 'SELECT COUNT(*) AS n FROM (SELECT DISTINCT category FROM stocks);']], 'Counting a DISTINCT subquery')])),
    dict(old='stp_f84c654f-64d7-420e-8b96-83f3f8eec1d0', **step(
        'RANK로 같은 가격에 같은 순위를 주세요', ['RANK·ROW_NUMBER·DENSE_RANK의 동점 처리를 구별해요.'],
        'ROW_NUMBER는 동점에도 1,2,3,4다. RANK()로 고쳐 1,1,3,4를 확인한다. DENSE_RANK는 1,1,2,3이다. 채점은 가격이 다른 표로도 실행한다.',
        '`RANK() OVER(ORDER BY price DESC)`는 가격이 높은 순서로 순위를 매기고, 같은 가격에는 같은 순위를 줘요. 그다음 순위는 동점 수만큼 건너뛰어요. ID 1과 2는 가격이 같은 10이에요.\n\n'
        '순위 함수를 고쳐 같은 가격은 같은 순위, 그다음은 동점 수만큼 건너뛰게 하세요. 채점은 가격이 다른 표로도 실행해요.\n\n'
        + todo('코드 실행을 눌러 1, 2, 3, 4가 나오는지 확인하세요.', '`ROW_NUMBER()`를 `RANK()`로 고치세요.', '코드 실행을 눌러 1, 1, 3, 4가 나오는지 확인하세요.', '수정한 질의를 제출하세요.'),
        s7, s7_solution, n7,
        {'1, 2, 3, 4예요. ROW_NUMBER는 동점이어도 번호를 따로 매겨요.': '「동점이어도」는 실제 ROW_NUMBER 결과(ID 1, 2가 1, 2)와 맞아요.',
         '조심하세요. DENSE_RANK였다면 동점 다음이 2등이에요.': '실제 DENSE_RANK 동작을 정확히 말해요.'},
        [([['RANK()', 'DENSE_RANK()']], 'No gap after ties'), ([['RANK()', 'ROW_NUMBER()']], 'Separate numbers for ties')],
        [([['RANK() OVER(ORDER BY price DESC)', '(SELECT COUNT(*) FROM stocks t WHERE t.price > stocks.price) + 1']], 'Counting higher prices')])),
    dict(old='stp_e910888c-b30f-47d7-bdb9-2d0ef1eb83ae', **step(
        'PARTITION BY로 분류마다 번호를 다시 매기세요', ['PARTITION BY가 행을 줄이지 않고 창만 나눔을 확인해요.'],
        'ROW_NUMBER() OVER(ORDER BY id)는 1,2,3,4다. PARTITION BY category를 더해 1,2,1,2를 확인한다. 행 수는 그대로다. 채점은 분류가 다른 표로도 실행한다.',
        '`ROW_NUMBER() OVER(PARTITION BY category ORDER BY id)`는 분류마다 따로 1부터 번호를 매기는 윈도우 함수예요. 지금 창에는 분류 구분이 없어요.\n\n'
        '창에 PARTITION BY를 더해 분류마다 번호를 1부터 다시 매기세요. 채점은 분류가 다른 표로도 실행해요.\n\n'
        + todo('코드 실행을 눌러 1, 2, 3, 4가 나오는지 확인하세요.', '`OVER(` 바로 뒤에 `PARTITION BY category`를 쓰세요.', '코드 실행을 눌러 1, 2, 1, 2가 나오는지 확인하세요.', '수정한 질의를 제출하세요.'),
        s8, s8_solution, n8,
        {'조심하세요. 윈도우 함수는 GROUP BY와 달리 행을 줄이지 않아요. 네 행이 그대로 남아요.': '실제 SQL 의미를 정확히 대조해요.'},
        [([['OVER(PARTITION BY category ORDER BY id)', 'OVER(PARTITION BY category ORDER BY id DESC)']], 'Numbering from the wrong end'),
         ([['OVER(PARTITION BY category ORDER BY id)', 'OVER(ORDER BY id)']], 'One window')],
        [([['ROW_NUMBER() OVER(PARTITION BY category ORDER BY id)', '(SELECT COUNT(*) FROM stocks t WHERE t.category = stocks.category AND t.id <= stocks.id)']], 'Counting earlier rows of the same category')])),
    dict(old='stp_9ff15bee-38b5-458e-9b34-dec3d1467076', **step(
        '창을 고쳐 지금 행까지의 누적 합을 보이세요', ['누적 창의 순서와 범위가 각 행의 합계를 정함을 확인해요.'],
        'SUM(qty) OVER()는 모든 행에 6이다. OVER(ORDER BY id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)로 고쳐 2,6,6,6을 확인한다. 채점은 값이 다른 표로도 실행한다.',
        '`SUM(qty) OVER(ORDER BY id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)`는 ID 순서로 첫 행부터 지금 행까지의 합이에요. 빈 `OVER()`는 모든 행을 한 창으로 더해요.\n\n'
        '창을 고쳐 ID 순서로 첫 행부터 지금 행까지의 누적 합을 보이세요. 채점은 값이 다른 표로도 실행해요.\n\n'
        + todo('코드 실행을 눌러 모든 행에 6이 나오는지 확인하세요.', '`OVER()` 괄호 안에 `ORDER BY id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`를 쓰세요.', '코드 실행을 눌러 2, 6, 6, 6이 나오는지 확인하세요.', '수정한 질의를 제출하세요.'),
        s9, s9_solution, n9,
        {'조심하세요. 창의 ORDER BY는 누적 순서를, 맨 끝 ORDER BY는 결과를 보여 줄 순서만 정해요.': '실제 SQL 의미를 정확히 대조해요.'},
        [([['OVER(ORDER BY id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)', 'OVER()']], 'Whole-table total'),
         ([['OVER(ORDER BY id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)', 'OVER(ORDER BY id DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)']], 'Accumulating from the last row')],
        [([['OVER(ORDER BY id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)', 'OVER(ORDER BY id)']], 'Default frame with a unique order')])),
]
