"""The missing first experiences, before the published SQL exercises."""
from sql_lab import sql_step, lab

ONE = "CREATE TABLE item(id INT,name VARCHAR(30),price INT,qty INT);\nINSERT INTO item VALUES(1,'milk',100,3);\n"
SEED = "CREATE TABLE item(id INT PRIMARY KEY,name VARCHAR(30),price INT,qty INT);\nINSERT INTO item VALUES(1,'milk',100,3),(2,'bread',200,0),(3,'tea',100,NULL);\n"
NAMES = 'milk\nbread\ntea'
ROWS = '1\tmilk\t100\t3\n2\tbread\t200\t0\n3\ttea\t100\tNULL'
AFTER = 'SELECT id,name,price,qty FROM item ORDER BY id;\n'


def exercise(slug,title,concept,intro,know,starter,solution,expected,first,result,caution,
             *,before=SEED,after='',variants=None,outputs=None):
    value=sql_step(slug=slug,title=title,concept=concept,intro=intro,know=know,
        before=before,starter=starter,solution=solution,after=after,expected=expected,
        first_output=first,result=result,caution=caution,engine='mysql',variants=variants)
    value['complexity']['prior']='앞에서 본 표와 조회 결과를 읽을 수 있어요.'
    value['complexity']['lines']=max(1,len(solution.strip().splitlines()))
    # These are authored expectations. Successful native execution supplies the final recordings.
    value['authored_outputs']=outputs or []
    return value


def additions():
    a=exercise('table-first-row','상품 한 행의 네 열을 조회하세요',
        '테이블은 같은 종류의 데이터를 행과 열로 묶어요.',
        '프로그램을 닫아도 주문은 남아야 해요. 여러 프로그램이 같은 상품도 읽어야 하죠. 파일로도 저장할 수 있지만 검색·변경·관계 규칙을 직접 관리해야 해요. 데이터베이스는 구조에 맞게 모은 데이터의 저장소예요. MySQL 같은 관리 프로그램이 저장·검색·변경과 규칙 검사를 맡아요. 지금은 실제 MySQL 서버에 상품 표 하나를 준비했어요.',
        'MySQL은 DB 관리 프로그램이고 SQL은 여기에 요청하는 언어예요. 상품 하나가 행 하나예요. 번호·이름·가격·재고는 열이에요. SELECT는 결과로 읽을 값을 고르고 FROM은 읽을 테이블을 정해요. 별표는 모든 열이에요. 지금 표에는 한 행만 있어 순서 문제는 없어요. 표를 만드는 준비 SQL은 제공했어요.',
        'SELECT 1;\n','SELECT * FROM item;\n','1\tmilk\t100\t3',
        '1만 나와요. 이 식은 상품 표를 읽지 않았어요.',
        '한 상품의 번호·이름·가격·재고가 한 행으로 나와요.',
        '조심하세요. 지금 결과는 조회예요. 화면에 보였다는 것과 새 데이터를 저장했다는 것은 달라요.',
        before=ONE,outputs=['1','1\tmilk\t100\t3'])
    b=exercise('choose-two-columns','이름과 가격 두 열만 조회하세요',
        '행을 없애지 않고 결과에 보일 열만 고를 수 있어요.',
        '상품 행은 그대로 두고 이름과 가격만 보려 해요. 지금은 네 열이 모두 보여요.',
        'SELECT name,price는 두 열을 그 순서로 읽어요. FROM item은 같은 표를 가리켜요. 결과의 열 수가 줄어도 원래 테이블의 열이 삭제되지는 않아요.',
        'SELECT * FROM item;\n','SELECT name,price FROM item;\n','milk\t100',
        '번호와 재고까지 네 값이 나와요.', '이름과 가격 두 값만 나와요. 원본 상품은 그대로예요.',
        '조심하세요. 조회할 열을 고르는 일과 행을 지우는 일은 다른 명령이에요.',
        before=ONE,outputs=['1\tmilk\t100\t3','milk\t100'])
    c=exercise('where-one-row','2번 상품 한 행만 조회하세요',
        'WHERE는 조건이 참인 행만 조회 결과에 남겨요.',
        '상품이 세 행으로 늘었어요. 이번에는 2번 상품의 이름 하나만 찾아요.',
        'id는 번호 열이에요. WHERE id=2는 각 행의 번호를 비교해요. 조건이 참인 행만 결과에 남아요. 이 조회는 조건에 맞지 않는 행을 DB에서 삭제하지 않아요.',
        'SELECT name FROM item WHERE id=1;\n','SELECT name FROM item WHERE id=2;\n','bread',
        'milk가 나와요. 현재 조건은 번호 1을 찾았어요.', '번호 2인 bread만 나와요. 나머지 행도 DB에는 남아 있어요.',
        '조심하세요. WHERE는 지금 SELECT의 조회 범위예요. 원본 행을 지우는 명령이 아니에요.',outputs=['milk','bread'])
    order_seed=SEED.replace("(3,'tea',100,NULL)","(3,'tea',50,NULL)")
    d=exercise('order-one-column','가격이 작은 상품부터 조회하세요',
        'ORDER BY는 결과 행을 나열할 기준을 정해요.',
        '번호가 작은 상품이 가장 싼 것은 아니에요. 가격은 tea 50, milk 100, bread 200이에요.',
        'ORDER BY price는 가격이 작은 행부터 나열해요. DESC를 붙이면 큰 값부터예요. ORDER BY가 없을 때 우연히 보인 순서를 규칙으로 삼지 않아요. 지금은 세 가격이 달라 같은 값의 순서는 뒤에서 다뤄요.',
        'SELECT name FROM item ORDER BY id;\n','SELECT name FROM item ORDER BY price;\n','tea\nmilk\nbread',
        '번호 순서라 milk, bread, tea로 나와요.', '가격이 작은 tea, milk, bread 순서로 나와요.',
        '조심하세요. 표를 넣은 순서와 결과를 정렬하는 기준은 달라요.',before=order_seed,
        outputs=[NAMES,'tea\nmilk\nbread'])
    e=exercise('count-rows','재고가 미정이어도 상품 행은 세세요',
        'COUNT(*)는 행을 세고 COUNT(열)은 값이 있는 행을 세요.',
        '상품은 세 행인데 COUNT(qty)는 두 개라고 해요. tea의 재고가 아직 NULL이에요.',
        'COUNT(*)는 모든 행을 세어요. COUNT(qty)는 qty가 NULL인 행을 세지 않아요. 상품 수와 재고가 확인된 상품 수는 다른 질문이에요.',
        'SELECT COUNT(qty) FROM item;\n','SELECT COUNT(*) FROM item;\n','3',
        '재고 값이 있는 두 행만 세었어요.', '재고가 미정인 tea도 상품 행으로 세어 3이에요.',
        '조심하세요. 상품 세 종류라는 말이 재고 세 개라는 뜻은 아니에요.',outputs=['2','3'])
    sum_seed=SEED.replace('100,3)','100,7)')
    f=exercise('sum-values','상품 종류 수 대신 확인된 수량을 더하세요',
        'SUM은 행 수가 아니라 열에 저장된 숫자를 더해요.',
        '상품은 세 종류예요. milk 재고는 7개, bread는 0개이고 tea는 미정이에요.',
        'COUNT(*)는 상품 행 수를 세어요. SUM(qty)는 NULL을 빼고 확인된 수량을 더해요. 더할 값이 하나도 없는 경우는 다음 문제에서 따로 확인해요.',
        'SELECT COUNT(*) FROM item;\n','SELECT SUM(qty) FROM item;\n','7',
        '3은 상품 종류 수예요.', '7은 확인된 재고 수량의 합이에요.',
        '조심하세요. COUNT(qty)로 바꿔도 수량을 더하는 것은 아니에요.',before=sum_seed,outputs=['3','7'])
    j=exercise('create-text-table','글자 메모를 담을 테이블을 만드세요',
        'CREATE TABLE은 테이블의 열 이름과 저장할 값의 자료형을 정해요.',
        '이번 실습에는 메모 표가 아직 없어요. 준비 코드가 content를 정수 열로 만들어 글자 메모를 넣지 못해요. 제공된 검사 SQL이 글자를 저장하고 다시 읽어요.',
        'CREATE TABLE memo는 memo라는 테이블을 만들어요. 괄호 안에 열 이름과 자료형을 써요. INT는 정수, VARCHAR(30)은 길이 제한이 있는 글자예요. 표를 만든 것만으로 메모 행이 생기지는 않아요. 글자를 넣는 INSERT는 다음 문제에서 직접 써요.',
        'CREATE TABLE memo(content INT);\n','CREATE TABLE memo(content VARCHAR(30));\n','first memo',
        '글자를 정수 열에 넣는 문장이 거절돼 메모 행이 없어요.', '글자를 담는 열이라 first memo가 저장되고 다시 읽혀요.',
        '조심하세요. 테이블의 모양을 만드는 것과 데이터 한 행을 넣는 것은 다른 일이에요.',before='',
        after="INSERT INTO memo(content) VALUES('first memo');\nSELECT content FROM memo;\n",outputs=['','first memo'])
    g=exercise('insert-persistent-row','coffee 상품 한 행을 저장하세요',
        'INSERT는 테이블에 새 행을 저장해 다른 연결에서도 읽게 해요.',
        '현재 상품은 세 행이에요. coffee를 번호 4, 가격 300, 재고 2로 저장하세요. 이 문제는 여러분의 SQL 클라이언트를 닫은 뒤 새 연결에서 표를 읽어요. DB 서버와 컨테이너는 끄지 않아요.',
        'INSERT INTO item 뒤에 값을 넣을 열을 쓰고 VALUES 뒤에 같은 순서의 값을 써요. SELECT로 coffee라는 글자만 출력하는 것과 달라요. 여기서 확인하는 것은 클라이언트 연결이 끝나도 같은 DB 서버에 행이 남는다는 사실이에요. 서버나 볼륨을 삭제한 뒤의 보존은 별도 수업이에요.',
        'SELECT name FROM item WHERE id=4;\n',"INSERT INTO item(id,name,price,qty) VALUES(4,'coffee',300,2);\n",ROWS+'\n4\tcoffee\t300\t2',
        '새 연결에서 읽어도 기존 세 상품만 있어요.', '원래 연결을 닫은 뒤 새 연결에서 coffee 행까지 읽었어요.',
        '조심하세요. 같은 INSERT를 다시 실행하면 같은 번호가 겹칠 수 있어요. 조회처럼 실행할 때마다 같은 효과인 명령은 아니에요.',
        after=AFTER,outputs=[ROWS,ROWS+'\n4\tcoffee\t300\t2'])
    # This task really closes one SQL client before starting the observer client.
    g['files']['lab.sh']=lab('mysql', separate_observer=True)
    h=exercise('update-one-value','milk의 가격만 150으로 바꾸세요',
        'UPDATE의 SET은 바꿀 열과 새 값을 정하고 WHERE는 바꿀 행을 정해요.',
        'milk 가격을 100에서 150으로 바꾸려 해요. 준비 코드는 아직 조회만 해요.',
        'UPDATE item SET price=150 WHERE id=1은 1번 행의 가격만 바꿔요. 이름·재고·다른 상품은 유지돼요. WHERE를 빼면 모든 상품의 가격을 바꿔 버려요. 수정 전에는 같은 조건의 SELECT로 대상을 확인하세요.',
        'SELECT name,price FROM item WHERE id=1;\n','UPDATE item SET price=150 WHERE id=1;\n',
        '1\tmilk\t150\t3\n2\tbread\t200\t0\n3\ttea\t100\tNULL',
        '조회에는 milk 가격 100이 나와요. 뒤의 전체 조회에서도 아직 바뀌지 않았어요.',
        'milk 가격만 150이에요. 나머지 값과 행은 그대로예요.',
        '조심하세요. SELECT의 별칭으로 150을 보여 주는 것과 실제 price를 변경하는 것은 달라요.',after=AFTER,
        outputs=['milk\t100\n'+ROWS,'1\tmilk\t150\t3\n2\tbread\t200\t0\n3\ttea\t100\tNULL'])
    i=exercise('delete-one-row','2번 상품 행만 삭제하세요',
        'DELETE는 WHERE를 만족하는 행을 테이블에서 없애요.',
        '판매를 중단한 bread 한 행만 지우려 해요. 준비 코드는 대상을 조회만 해요.',
        'DELETE FROM item WHERE id=2는 2번 행을 지워요. 테이블이나 열의 모양을 지우는 것은 아니에요. WHERE를 빼면 모든 행이 대상이에요. 실제 사용자 DB가 아니라 제공된 연습 DB에서만 실습해요.',
        'SELECT name FROM item WHERE id=2;\n','DELETE FROM item WHERE id=2;\n','milk\ntea',
        'bread를 조회했지만 뒤의 전체 목록에는 세 상품이 그대로 있어요.', '전체 목록에서 bread만 없어졌어요. milk와 tea는 남았어요.',
        '조심하세요. DELETE의 WHERE는 실제로 없앨 행을 정해요. 화면에서 안 보이게 하는 필터가 아니에요.',
        after='SELECT name FROM item ORDER BY id;\n',outputs=['bread\n'+NAMES,'milk\ntea'])
    key_seed="CREATE TABLE member(id INT,name VARCHAR(30));\nINSERT INTO member VALUES(1,'lee'),(2,'lee');\n"
    k=exercise('identify-same-name','이름이 같아도 2번 회원만 조회하세요',
        '사람 이름과 행을 구별할 식별자는 역할이 달라요.',
        '회원 두 명의 이름이 모두 lee예요. 한 사람을 고르려고 이름으로 찾으면 두 행이 나와요.',
        '이 연습 표는 회원마다 다른 id를 준비했어요. id로 행을 구별해요. 이름은 같은 사람이 있을 수 있죠. 다음 제약 수업의 PRIMARY KEY는 이런 식별자가 비거나 겹치지 않게 DB가 지키도록 만드는 규칙이에요.',
        "SELECT id,name FROM member WHERE name='lee' ORDER BY id;\n",'SELECT id,name FROM member WHERE id=2;\n','2\tlee',
        '이름 조건으로는 lee 두 사람을 모두 찾았어요.', 'id가 2인 lee 한 사람만 찾았어요.',
        '조심하세요. 이름이 같다는 이유로 두 행을 같은 사람으로 합치면 안 돼요.',before=key_seed,
        outputs=['1\tlee\n2\tlee','2\tlee'])
    relation_seed=key_seed+"CREATE TABLE orders(id INT,member_id INT);\nINSERT INTO orders VALUES(10,2),(11,2),(12,1);\n"
    l=exercise('reference-member-id','2번 회원의 주문 번호를 조회하세요',
        '주문 번호와 주문한 회원을 가리키는 번호는 다른 열이에요.',
        '10번과 11번 주문은 2번 회원의 주문이에요. 12번 주문은 1번 회원의 주문이에요.',
        'orders.id는 주문 자체를 구별해요. orders.member_id는 member.id를 가리켜요. 여러 주문이 한 회원을 가리킬 수 있어요. 지금은 저장된 번호의 관계를 읽어요. 다음 수업에서는 없는 회원 번호를 저장하지 못하게 제약을 걸어요.',
        'SELECT id FROM orders WHERE id=2 ORDER BY id;\n','SELECT id FROM orders WHERE member_id=2 ORDER BY id;\n','10\n11',
        '2번 주문은 없어서 결과가 비었어요.', '회원 번호가 2인 주문 10번과 11번이 나와요.',
        '조심하세요. 주문 번호가 2라는 것과 주문한 회원 번호가 2라는 것은 다른 조건이에요.',before=relation_seed,
        outputs=['','10\n11'])
    a['variations']=[dict(files={'before.sql':ONE.replace("'milk',100,3","'juice',250,8")},expected='1\tjuice\t250\t8')]
    b['variations']=[dict(files={'before.sql':ONE.replace("'milk',100,3","'juice',250,8")},expected='juice\t250')]
    c['variations']=[dict(files={'before.sql':SEED.replace("'bread'","'cake'")},expected='cake')]
    d['variations']=[dict(files={'before.sql':order_seed.replace("'tea',50","'tea',350")},expected=NAMES)]
    e['variations']=[dict(files={'before.sql':SEED.replace("(3,'tea',100,NULL);","(3,'tea',100,NULL),(4,'coffee',300,2);")},expected='4')]
    f['variations']=[dict(files={'before.sql':sum_seed.replace('100,7)','100,9)')},expected='9')]
    k['variations']=[dict(files={'before.sql':key_seed.replace("'lee'","'park'")},expected='2\tpark')]
    l['variations']=[dict(files={'before.sql':relation_seed.replace('(11,2)','(11,1)')},expected='10')]
    a['accepts']=[([('SELECT * FROM item;','SELECT id,name,price,qty FROM item;')],'모든 열을 명시해서 읽어도 같은 실제 행이에요.')]
    a['rejects'].append(([('SELECT * FROM item;',"SELECT 1,'milk',100,3;")],'표를 읽지 않고 답을 출력하면 변형 상품의 값이 달라져 실패해야 해요.'))
    c['accepts']=[([('WHERE id=2','WHERE id IN (2)')],'한 식별자 집합으로 같은 행을 읽는 동등한 조건도 인정해요.')]
    c['rejects'].append(([('SELECT name FROM item WHERE id=2;',"SELECT 'bread';")],'결과 문자열을 하드코딩하면 실제 상품 이름이 바뀐 경우 실패해야 해요.'))
    e['accepts']=[([('COUNT(*)','COUNT(1)')],'모든 행에 있는 상수를 세는 동등한 행 수 집계도 인정해요.')]
    prefix='-- 이 문제의 표만 다시 만들어 자료형을 비교하는 재시험 준비예요.\nDROP TABLE IF EXISTS memo;\n'
    j['starter']=prefix+j['starter']
    j['solution']=prefix+j['solution']
    preparation='이 자료형 비교 문제는 보이는 DROP TABLE로 연습용 memo 표만 다시 만들어요. 일반 DB 실행마다 표를 지우라는 뜻은 아니에요.'
    j['intro'].append(preparation)
    j['narration'].insert(0,('say',preparation,'text:'+preparation))
    j['review'][preparation]='이 자료형 실험의 반복 준비가 공개 코드에 있고 해당 연습 표만 지운다는 사실을 밝혀요.'
    return dict(a=a,b=b,c=c,d=d,e=e,f=f,g=g,h=h,i=i,j=j,k=k,l=l)
