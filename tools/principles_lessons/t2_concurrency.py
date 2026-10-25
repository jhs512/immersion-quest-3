"""PostgreSQL connections with deliberate schedules, not timing guesses."""
from common import START_NEW, TODO_RUN_BEFORE, TODO_RUN_AFTER, TODO_SUBMIT
from sql_lab import PG, unit, sql_lesson

COMPOSE=f'''services:
  db:
    image: {PG}
    environment:
      POSTGRES_PASSWORD: lab
      POSTGRES_DB: lab
    ports: ["127.0.0.1::5432"]
    healthcheck:
      test: ["CMD", "pg_isready", "-h", "127.0.0.1", "-U", "postgres", "-d", "lab"]
      interval: 1s
      timeout: 1s
      retries: 60
'''
SCRIPT='''set -e
docker compose up -d --wait db >/dev/null 2>&1
address=$(docker compose port db 5432)
export MQ3_DB_URL="jdbc:postgresql://$address/lab"
"$MQ3_JAVA" -Dstdout.encoding=UTF-8 -Dstderr.encoding=UTF-8 --class-path "$MQ3_CLASSPATH" Main.java
'''
HEAD='''import java.sql.*;
import java.util.*;
import java.util.concurrent.*;
class Main {
 static Connection open() throws SQLException { return DriverManager.getConnection(System.getenv("MQ3_DB_URL"),"postgres","lab"); }
 static int value(Connection c) throws SQLException {
  try(ResultSet r=c.createStatement().executeQuery("SELECT balance FROM account WHERE id=1")) { r.next(); return r.getInt(1); }
 }
 public static void main(String[] args) throws Exception {
  try(Connection a=open(); Connection b=open()) {
   a.createStatement().execute("CREATE TABLE account(id INT PRIMARY KEY,balance INT); INSERT INTO account VALUES(1,100)");
'''
TAIL='\n  }\n }\n}\n'


def step(slug,title,concept,intro,know,before,after,expected,first,result,caution,tests=None,head=HEAD):
    focus={'snapshot':'a.setTransactionIsolation(Connection.TRANSACTION_READ_COMMITTED);',
           'lost-update':'"UPDATE account SET balance="+(oldB-second)+" WHERE id=1"',
           'row-lock':'try(ResultSet held=a.createStatement().executeQuery("SELECT balance FROM account WHERE id=1"))',
           'final-stock':'UPDATE stock SET qty=qty-1 WHERE id=1'}[slug]
    return dict(slug=slug,title=title,language='docker',docker_images=[PG],libraries=['postgresql-jdbc'],
        entry_file='Main.java',files={'compose.yaml':COMPOSE,'lab.sh':SCRIPT},start=START_NEW,
        intro=[intro],know=know,objectives=[concept],todo=[TODO_RUN_BEFORE,title,TODO_RUN_AFTER,TODO_SUBMIT],
        starter=head+before+TAIL,solution=head+after+TAIL,tests=tests or [('',expected)],success=expected,
        complexity=dict(prior='JDBC의 트랜잭션·commit·rollback을 알아요.',new=concept,changed=title,evidence=first,lines=1,services=0),
        narration=[('say',intro,'text:'+intro),('run',),('say',first,'output'),('say',concept,'code:'+focus),('patch',before,after,title),
            ('run',),('say',result,'output'),('say',caution,'text:'+know),('submit',)],
        review={intro:'준비 코드가 실제 두 DB 연결을 어떤 순서로 사용하는지 설명해요.',first:'수정 전 실제 연결의 읽기·쓰기 결과를 설명해요.',
            concept:'실제로 고칠 격리 설정이나 SQL을 강조하며 그 변경이 제공하는 보장을 설명해요.',
            title:'한 가지 SQL 또는 격리 설정을 고치도록 요구해요.',result:'수정 뒤 실제 DB가 제공하는 보장과 출력을 연결해요.',
            caution:'PostgreSQL의 해당 격리 수준과 트랜잭션 경계에 한정해 설명해요.'},
        rejects=[([(after,before)],'이전 설정이나 SQL은 요구한 격리·동시 변경 조건을 만족하지 못해요.')])

B1='''   a.setTransactionIsolation(Connection.TRANSACTION_READ_COMMITTED);
   a.setAutoCommit(false);
   System.out.println("첫 조회:"+value(a));
   b.createStatement().executeUpdate("UPDATE account SET balance=150 WHERE id=1");
   System.out.println("다시 조회:"+value(a));
   a.commit();'''
A1=B1.replace('TRANSACTION_READ_COMMITTED','TRANSACTION_REPEATABLE_READ')
S1=step('snapshot','한 트랜잭션에서 같은 잔액을 다시 읽게 하세요','격리 수준은 트랜잭션이 다른 확정 변경을 언제 볼지 정해요.',
    '연결 A가 잔액 100을 읽고, B가 150으로 변경해 확정한 뒤, A가 다시 읽어요. 연결 두 개를 실제로 열어 정해진 순서대로 실행해요.',
    'PostgreSQL의 READ COMMITTED는 문장마다 새 스냅샷을 봐요. A에서 첫 조회 전에 REPEATABLE READ를 설정해 같은 트랜잭션의 스냅샷을 유지하세요. 설정은 첫 조회 전에 해야 해요.',
    B1,A1,'첫 조회:100\n다시 조회:100',
    '100 다음에 150이 나와요. 트랜잭션을 시작했다는 것만으로 같은 조회 결과가 보장되지는 않아요.',
    '두 조회가 모두 100이에요. B의 변경이 실패한 것이 아니라 A가 이전 스냅샷을 유지한 거예요.',
    '조심하세요. 스냅샷을 유지하는 것은 다른 연결의 쓰기를 막는 잠금과 달라요. 이 예제에서 B는 정상적으로 변경을 확정했어요.')

B2='''   Scanner input=new Scanner(System.in);
   int first=input.nextInt(), second=input.nextInt();
   int oldA=value(a), oldB=value(b);
   a.createStatement().executeUpdate("UPDATE account SET balance="+(oldA-first)+" WHERE id=1");
   b.createStatement().executeUpdate("UPDATE account SET balance="+(oldB-second)+" WHERE id=1");
   System.out.println(value(a));'''
A2=B2.replace('"UPDATE account SET balance="+(oldB-second)+" WHERE id=1"',
               '"UPDATE account SET balance=balance-"+second+" WHERE id=1"')
S2=step('lost-update','두 차감을 모두 잔액에 반영하세요','예전에 읽은 값으로 덮어쓰기와 DB의 현재 값에서 계산하기를 구별해요.',
    'A와 B가 모두 100을 읽었어요. A가 10을 차감하고 확정한 뒤 B가 예전 100에서 20을 뺀 80으로 덮어써요.',
    'B의 UPDATE가 예전 oldB를 쓰지 않고 DB 행의 현재 balance에서 second를 빼도록 고치세요. 입력 숫자는 Scanner가 읽은 정수예요. 한 문장의 계산이 직전 확정 값을 사용하게 해요.',
    B2,A2,'70','결과가 80이에요. A가 차감한 10이 B의 예전 값 덮어쓰기로 사라졌어요.',
    '결과가 70이에요. B의 문장이 현재 잔액 90에서 20을 차감했어요.',
    '조심하세요. Java 변수 oldB를 바꾸는 것으로 다른 연결이 이미 저장한 값을 자동으로 알 수는 없어요.',
    tests=[('10 20','70'),('5 7','88')])

B3='''   a.setAutoCommit(false); b.setAutoCommit(false);
   try(ResultSet held=a.createStatement().executeQuery("SELECT balance FROM account WHERE id=1")) { held.next(); }
   b.createStatement().execute("SET LOCAL lock_timeout='200ms'");
   try {
    b.createStatement().executeUpdate("UPDATE account SET balance=balance+5 WHERE id=1");
    b.commit();
    System.out.println("다른 변경:성공");
   } catch(SQLException e) {
    if(!"55P03".equals(e.getSQLState())) throw e;
    b.rollback();
    System.out.println("다른 변경:잠금 대기 취소");
   }
   a.rollback();
   System.out.println("잔액:"+value(b));
   b.rollback();'''
A3=B3.replace('executeQuery("SELECT balance FROM account WHERE id=1")',
              'executeQuery("SELECT balance FROM account WHERE id=1 FOR UPDATE")')
S3=step('row-lock','읽은 행을 다른 연결이 바로 수정하지 못하게 하세요','FOR UPDATE의 행 잠금은 트랜잭션이 끝날 때까지 유지돼요.',
    'A가 읽은 행을 기준으로 결정하는 동안 B가 그 행을 수정하려 해요. B에는 대기 취소용 lock_timeout을 준비했어요.',
    'A의 SELECT에 FOR UPDATE를 붙이세요. B의 변경이 실제 잠금에 막히면 PostgreSQL의 SQLSTATE 55P03을 확인해요. 대기 시간이 빠르냐 느리냐로 채점하지 않아요. A가 rollback하면 잠금이 풀려요.',
    B3,A3,'다른 변경:잠금 대기 취소\n잔액:100',
    '일반 SELECT는 B의 수정을 막지 않아서 잔액이 105가 됐어요.',
    'B의 UPDATE가 실제 행 잠금에 막혀 취소됐어요. 잠금을 푼 뒤 읽은 잔액은 100이에요.',
    '조심하세요. ResultSet을 닫는 것과 트랜잭션을 끝내는 것은 달라요. FOR UPDATE 잠금은 여기서 commit이나 rollback까지 유지돼요.')

STOCK_HEAD=HEAD.replace('CREATE TABLE account(id INT PRIMARY KEY,balance INT); INSERT INTO account VALUES(1,100)',
    'CREATE TABLE stock(id INT PRIMARY KEY,qty INT); INSERT INTO stock VALUES(1,1)')
B4='''   CyclicBarrier bothRead=new CyclicBarrier(2);
   ExecutorService pool=Executors.newFixedThreadPool(2);
   try {
    Callable<Integer> buy=()->{
     try(Connection c=open()) {
      int remaining;
      try(ResultSet r=c.createStatement().executeQuery("SELECT qty FROM stock WHERE id=1")) { r.next(); remaining=r.getInt(1); }
      bothRead.await(10,TimeUnit.SECONDS);
      if(remaining<=0) return 0;
      return c.createStatement().executeUpdate("UPDATE stock SET qty=qty-1 WHERE id=1");
     }
    };
    Future<Integer> one=pool.submit(buy), two=pool.submit(buy);
    System.out.println("판매:"+(one.get(20,TimeUnit.SECONDS)+two.get(20,TimeUnit.SECONDS)));
    try(ResultSet r=a.createStatement().executeQuery("SELECT qty FROM stock WHERE id=1")) {r.next(); System.out.println("재고:"+r.getInt(1));}
   } finally {pool.shutdownNow();}'''
A4=B4.replace('UPDATE stock SET qty=qty-1 WHERE id=1','UPDATE stock SET qty=qty-1 WHERE id=1 AND qty>0')
S4=step('final-stock','마지막 재고 하나가 두 번 팔리지 않게 하세요','조회한 뒤 검사하는 것과 조건을 가진 변경 한 문장은 달라요.',
    '구매자 두 명이 재고 1을 모두 읽은 뒤 동시에 구매해요. 제공 장벽이 두 조회가 끝날 때까지 기다려 재현 순서를 고정해요.',
    'UPDATE 자체에 qty>0 조건을 넣으세요. PostgreSQL READ COMMITTED에서 한 UPDATE가 기다린 뒤 최신 행에 조건을 다시 검사해요. 변경 행 수 1을 판매 성공으로 세므로 다른 구매자는 0을 받아야 해요.',
    B4,A4,'판매:1\n재고:0','판매가 2, 재고가 -1이에요. 두 구매자가 모두 예전 재고 1을 보고 통과했어요.',
    '한 UPDATE만 행을 바꿔 판매 1과 재고 0이 됐어요. 조건 검사와 차감을 DB의 같은 문장에 넣었어요.',
    '조심하세요. 이 원리는 이 한 행의 재고 변경에 대한 것이에요. 여러 표를 바꾸는 주문 전체의 원자성은 별도의 트랜잭션 경계가 필요해요.',head=STOCK_HEAD)

LESSON=sql_lesson(key='sql-isolation-locks',folder='sql_isolation_locks',pilot='락',title='격리·잠금 · 동시에 읽은 값이 서로를 덮어요',
    objectives=['스냅샷과 잠금을 구별해요.', '오래된 조회값으로 생기는 갱신 손실을 재현해요.', 'DB 조건과 변경을 한 문장으로 묶어 동시 구매를 지켜요.'],
    units=[unit('무엇을 보는가','트랜잭션과 읽기 스냅샷의 경계를 확인해요.',[S1]),
           unit('누가 바꿀 수 있는가','갱신 손실과 행 잠금을 실제 연결로 관찰해요.',[S2,S3]),
           unit('최종 동시 구매','동시에 온 두 요청에서 한 재고만 팔아요.',[S4])],final_slug='final-stock',
    sources=[('https://www.postgresql.org/docs/18/transaction-iso.html','READ COMMITTED·REPEATABLE READ의 보장을 확인해요.','실제 PostgreSQL 연결과 장벽으로 동시 실행을 재현해요.')])
LESSON['prerequisites']=['JDBC와 트랜잭션의 기본을 알아요.','Docker Desktop을 실행할 수 있어요.']
LESSON['brief']=(LESSON['objectives'][0],'마지막 재고를 두 명이 동시에 사도 한 번만 판매하세요.',
    ['읽기 스냅샷','갱신 손실과 행 잠금','조건부 변경'],'실제 PostgreSQL 18과 JDBC 연결 두 개를 사용해요. PC에는 자동 배정한 루프백 포트만 열어요.',
    '잔액이나 재고를 읽고 확인했는데 왜 다른 결과가 생길까요?')
