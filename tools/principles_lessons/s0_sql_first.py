"""Small relational experiments before constraints, joins and JDBC."""
from sql_lab import MYSQL, sql_step, sql_lesson, unit

SEED="""CREATE TABLE item(id INT PRIMARY KEY,name VARCHAR(30),price INT,qty INT);
INSERT INTO item VALUES(1,'milk',100,3),(2,'bread',200,0),(3,'tea',100,NULL);
"""


def step(slug,title,concept,intro,know,before,after,expected,first,result,caution,*,check='',variants=None):
    return sql_step(slug=slug,title=title,concept=concept,intro=intro,know=know,before=SEED,
        starter=before,solution=after,after=check,expected=expected,first_output=first,
        result=result,caution=caution,engine='mysql',variants=variants)


S1=step('row-and-column','상품 이름만 번호 순서로 조회하세요','조회할 열과 원래 저장된 행을 구별해요.',
    '표에는 번호·이름·가격·재고가 있어요. 이번 화면에는 이름만 보여야 해요.',
    'SELECT 뒤에는 결과에 필요한 열을 쓰고 FROM 뒤에는 읽을 표를 써요. 조회할 열을 바꿔도 표에 저장된 열이 없어지지는 않아요. ORDER BY id로 결과 순서를 정해요.',
    'SELECT * FROM item ORDER BY id;\n','SELECT name FROM item ORDER BY id;\n','milk\nbread\ntea',
    '상품마다 네 값이 나와요. 별표는 모든 열을 결과에 넣으라는 뜻이에요.',
    '이름만 세 줄로 나와요. 표의 가격이나 재고를 지운 것이 아니라 보여 줄 열을 고른 거예요.',
    '조심하세요. SELECT로 이름만 골랐다고 원본 표가 이름만 가진 표로 바뀌지는 않아요.')

S2=step('row-condition','가격이 100이고 재고가 있는 상품을 조회하세요','WHERE는 각 행에 대해 참인 조건을 만족하는 행을 남겨요.',
    'milk는 가격 100·재고 3, tea는 가격 100·재고 미정이에요. 지금 살 수 있는 100원 상품을 찾아야 해요.',
    '가격 조건과 재고 조건을 AND로 묶으세요. OR로 묶으면 둘 중 하나만 맞는 상품도 포함돼요. 재고 미정인 NULL은 양수라는 조건을 만족했다고 볼 수 없어요.',
    'SELECT name FROM item WHERE price=100 OR qty>0 ORDER BY id;\n',
    'SELECT name FROM item WHERE price=100 AND qty>0 ORDER BY id;\n','milk',
    'milk와 tea가 나와요. tea는 재고가 확인되지 않아도 가격 조건 하나만 맞아 포함됐어요.',
    'milk만 나와요. 가격과 실제 양수 재고를 동시에 만족하는 행을 골랐어요.',
    '조심하세요. 조건을 말로만 읽지 말고 각 행의 값에 대입해 보세요. AND와 OR는 남기는 행이 달라요.',
    variants=[dict(files={'before.sql':SEED.replace("(3,'tea',100,NULL)","(3,'tea',100,2)")},expected='milk\ntea')])

S3=step('unknown-value','재고가 아직 확인되지 않은 상품을 찾으세요','NULL은 숫자 0이 아니라 값이 없거나 아직 정해지지 않았음을 나타내요.',
    'bread의 재고는 0이고 tea의 재고는 NULL이에요. 품절 상품이 아니라 재고를 아직 확인하지 않은 상품을 찾아요.',
    'NULL 여부는 IS NULL로 검사하세요. = NULL은 비교할 값을 모르는 상태라 참인 행을 만들지 못해요. 0과 NULL을 같은 것으로 처리하지 마세요.',
    'SELECT name FROM item WHERE qty=NULL ORDER BY id;\n',
    'SELECT name FROM item WHERE qty IS NULL ORDER BY id;\n','tea',
    '아무 행도 나오지 않아요. NULL과 같다는 비교 결과를 참으로 확정할 수 없어요.',
    '재고가 미정인 tea가 나와요. 재고 0인 bread는 미정이 아니라 확인된 품절이에요.',
    '조심하세요. qty=0으로 바꾸면 품절 상품을 찾는 다른 요구가 돼요. 아직 모르는 것과 없다고 확인한 것은 달라요.')

S4=step('deterministic-order','가장 싼 상품을 가격·번호 순서로 두 개 조회하세요','행의 저장 순서와 조회 결과의 정렬 규칙은 달라요.',
    'milk와 tea는 같은 가격 100이에요. 싼 상품 두 개를 보여 주되 같은 가격이면 번호가 작은 상품이 먼저여야 해요.',
    'ORDER BY price,id로 가격이 같을 때의 순서까지 정한 뒤 LIMIT 2를 적용하세요. 표의 행을 넣은 순서나 우연히 보인 순서를 결과 규칙으로 가정하지 마세요.',
    'SELECT name FROM item ORDER BY price DESC,id LIMIT 2;\n',
    'SELECT name FROM item ORDER BY price,id LIMIT 2;\n','milk\ntea',
    'bread부터 나와요. DESC로 큰 가격부터 정렬했어요.',
    '가격 100인 milk와 tea가 번호 순서로 나와요. 같은 가격일 때의 규칙도 명시했어요.',
    '조심하세요. LIMIT만 붙이면 가장 싼 두 상품이라는 뜻이 되지 않아요. 먼저 어떤 순서의 앞 두 행인지 정해야 해요.',
    variants=[dict(files={'before.sql':SEED.replace("(2,'bread',200,0)","(2,'bread',50,0)")},expected='bread\nmilk')])

S5=step('aggregate','확인된 재고 수량의 합계를 구하세요','행의 개수와 각 행에 저장된 수량의 합은 서로 달라요.',
    '상품은 세 종류지만 확인된 재고 수량은 7개예요. 준비 코드는 상품 행 수를 재고 합계처럼 사용해요.',
    'SUM(qty)로 수량을 더하세요. COUNT(*)는 NULL이 있더라도 행을 세요. 합계 대상 값이 하나도 없으면 SUM은 NULL이므로 화면의 0으로 바꾸세요.',
    'SELECT COUNT(*) FROM item;\n','SELECT COALESCE(SUM(qty),0) FROM item;\n','7',
    '3이 나와요. 상품 세 종류를 센 값이어서 실제 재고 일곱 개와 달라요.',
    '재고 열을 합산해 7이 나와요. 변형 검사에서는 수량이 달라지거나 모두 미정일 때도 확인해요.',
    '조심하세요. COUNT(qty)도 수량의 합이 아니에요. NULL이 아닌 재고 값이 있는 행의 개수예요.',
    variants=[dict(files={'before.sql':SEED},expected='3'),
              dict(files={'before.sql':SEED.replace('100,3)','100,NULL)').replace('200,0)','200,NULL)')},expected='0')])
S5['files']['before.sql']=SEED.replace('100,3)','100,7)')

S6=step('targeted-change','milk 재고만 한 개 차감하세요','UPDATE는 WHERE를 만족하는 모든 행을 변경해요.',
    '한 고객이 milk 한 개를 샀어요. 준비 코드는 표의 모든 상품에서 수량을 차감해 bread 재고까지 -1로 만들어요.',
    'id=1인 상품만 바꾸도록 UPDATE에 WHERE를 붙이세요. SELECT로 화면만 고치는 대신 실제 표에 올바른 변경이 저장되어야 해요. 제공 조회가 모든 상품을 다시 읽어요.',
    'UPDATE item SET qty=qty-1;\n','UPDATE item SET qty=qty-1 WHERE id=1;\n',
    'milk:2\nbread:0\ntea:unknown',
    'milk뿐 아니라 bread도 -1이 됐어요. WHERE가 없는 UPDATE는 표의 모든 행을 대상으로 했어요.',
    'milk만 2가 되고 bread는 0, tea는 미정으로 유지됐어요. 변경 대상을 실제 행 조건으로 제한했어요.',
    '조심하세요. UPDATE 뒤의 WHERE는 결과 화면 필터가 아니라 실제로 바꿀 행의 범위예요. 실행 전에 그 조건의 SELECT로 대상을 확인할 수 있어요.',
    check="SELECT CONCAT(name,':',COALESCE(CAST(qty AS CHAR),'unknown')) FROM item ORDER BY id;\n",
    variants=[dict(files={'before.sql':SEED.replace('100,3)','100,8)')},expected='milk:7\nbread:0\ntea:unknown')])

LESSON=sql_lesson(key='sql-first',folder='sql_first',pilot='쿼',title='SQL 기초 · 행을 고르고 값을 바꾼다는 것',
    objectives=['행·열·조건과 NULL의 의미를 구별해요.', '정렬과 집계의 결과 규칙을 명시해요.', '변경할 행을 제한하고 원본 데이터에서 검증해요.'],
    units=[unit('행과 값','조회가 표의 어떤 부분을 선택하는지 이해해요.',[S1,S2,S3]),
           unit('결과의 규칙','순서와 집계가 무엇을 의미하는지 비교해요.',[S4,S5]),
           unit('실제 데이터 변경','조회와 변경의 차이를 실행해 확인해요.',[S6])],final_slug='targeted-change',engine='mysql',
    sources=[('https://dev.mysql.com/doc/refman/8.4/en/select.html','SELECT·NULL·집계·UPDATE의 의미를 확인해요.','실제 MySQL 8.4의 행과 결과를 비교해요.')])
LESSON['prerequisites']=['표의 행과 열이라는 표현을 알아요.','Docker Desktop을 실행할 수 있어요.']
