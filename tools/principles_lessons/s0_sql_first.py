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
    '한 고객이 milk 한 개를 샀어요. 준비 코드는 조회만 해서 재고를 아직 바꾸지 않았어요. 다른 상품의 재고는 그대로 두세요.',
    'id=1인 상품만 바꾸도록 UPDATE에 WHERE를 붙이세요. qty=qty-1은 현재 수량에서 하나를 빼요. 같은 UPDATE를 재실행하면 한 번 더 차감돼요. 제출 검사는 새 준비 DB에서 한 번 실행해 확인해요. 제공 조회가 모든 상품을 다시 읽어요.',
    'SELECT name,qty FROM item ORDER BY id;\n','UPDATE item SET qty=qty-1 WHERE id=1;\n',
    'milk:2\nbread:0\ntea:unknown',
    '아직 조회만 했어요. milk는 3, bread는 0이고 tea는 미정이에요.',
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

from sql_foundations import additions
EXTRA = additions()
original = LESSON['chapters'][0]
original['identity'] = 'c0'
for index, existing_unit in enumerate(original['units']):
    existing_unit['identity'] = f'c0u{index}'
query_unit, result_unit, final_unit = original['units']
query_unit['steps'] = [S1,S3,S2]
result_unit['steps'] = [S4,EXTRA['e'],EXTRA['f'],S5]
original['units'] = [query_unit,result_unit]
original['title'] = '행을 찾고 조회 결과의 규칙을 정해요'
LESSON['chapters'] = [
    dict(identity='db-foundations', title='왜 DB에 저장하고 표에서 읽을까요?',
         objectives=['DB·SQL·테이블의 역할을 구별해요.', '행·열·조건·정렬을 하나씩 관찰해요.'],
         units=[unit('표와 조회','한 행의 열을 읽고 필요한 열을 선택해요.',[EXTRA['a'],EXTRA['b']]),
                unit('조건과 순서','WHERE와 ORDER BY가 서로 다른 대상을 정함을 이해해요.',[EXTRA['c'],EXTRA['d']])]),
    original,
    dict(identity='data-lifecycle', title='표를 만들고 데이터를 추가·수정·삭제해요',
         objectives=['테이블의 모양과 저장된 행을 구별해요.', '데이터 변경 뒤 다른 연결의 조회 결과를 확인해요.'],
         units=[unit('테이블과 새 행','열의 자료형을 정하고 새 행을 저장해요.',[EXTRA['j'],EXTRA['g']]),
                unit('바꿀 범위와 지울 범위','WHERE로 실제 수정·삭제할 행을 제한해요.',[EXTRA['h'],EXTRA['i']])]),
    dict(identity='keys-relations', title='행의 정체성과 표 사이의 관계를 읽어요',
         objectives=['이름과 행 식별자를 구별해요.', '자기 행 번호와 다른 표를 가리키는 번호를 구별해요.'],
         units=[unit('식별자와 참조','중복 이름과 회원별 주문을 번호의 역할로 구별해요.',[EXTRA['k'],EXTRA['l']])]),
    dict(identity='final-mutation', title='최종 도전: 실제 재고 한 행만 바꿔요',
         objectives=['조회·조건·변경의 의미를 조합해 다른 상품을 보존해요.'], units=[final_unit]),
]
LESSON['revision']=3
LESSON['audience']='DB와 SQL을 처음 배우는 학습자'
LESSON['prerequisites']=['터미널이나 코드 실행 버튼으로 결과를 읽을 수 있어요.', 'Docker Desktop을 실행할 수 있어요. SQL·행·열은 여기서 처음 배워요.']
LESSON['objectives']=['왜 데이터를 프로그램 밖의 DB에 보관하는지 설명해요.',
    '행·열·테이블에서 SELECT·FROM·WHERE·ORDER BY를 하나씩 적용해요.',
    '테이블을 만들고 행을 추가·수정·삭제한 실제 결과를 확인해요.',
    '행의 식별자·관계·NULL·행 수와 수량 합계를 구별해요.']
LESSON['scope']=LESSON['objectives']
LESSON['description']='왜 DB가 필요한지에서 출발해 표와 조회를 익혀요. 저장·변경·삭제 뒤 실제 행을 읽고 키와 관계의 의미로 연결해요.'
LESSON['brief']=(
    '프로그램을 닫아도 남겨야 할 데이터에서 시작해 DB·SQL·표를 구별해요.',
    '다른 상품은 보존하면서 팔린 상품 한 행의 재고만 차감하세요.',
    ['한 행의 열을 읽고 WHERE와 ORDER BY를 나눠 익혀요.',
     '행 수와 수량 합계를 구별해요.', '표를 만들고 추가·수정·삭제해요.',
     '새 연결에서 저장 결과를 읽고 키·관계의 의미로 연결해요.'],
    'MySQL 8.4 실습 DB를 제공해요. 같은 문제의 재실행은 상태를 이어가고 제출 검사는 별도 준비 DB에서 해요. 호스트의 고정 DB 포트는 쓰지 않아요.',
    '화면에 글자를 출력하는 것과 DB에 행을 저장하는 것은 어떻게 다를까요?')
# New scenarios supply the SQL foundations rather than assuming SELECT/INSERT in their own prerequisites.
for c in LESSON['chapters']:
    for u in c['units']:
        for s in u['steps']:
            if s['slug'] not in ('table-first-row','choose-two-columns'):
                s['complexity']['prior']='앞 문제에서 테이블의 행·열과 조회를 확인했어요.'
EXTRA['a']['complexity']['prior']='SQL이나 행·열을 몰라도 시작할 수 있어요.'
EXTRA['b']['complexity']['prior']='한 상품 행에서 모든 열을 조회했어요.'
