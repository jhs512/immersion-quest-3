"""JDBC: cursor, parameters, affected rows and a real transactional final."""
from common import START_NEW, TODO_RUN_BEFORE, TODO_RUN_AFTER, TODO_SUBMIT
from sql_lab import sql_lesson, unit

HEAD='''import java.sql.*;
import java.util.*;
class Main {
 public static void main(String[] args) throws Exception {
  try (Connection c=DriverManager.getConnection("jdbc:h2:mem:lab", "sa", "")) {
   c.createStatement().execute("CREATE TABLE member(id INT PRIMARY KEY,name VARCHAR(100),balance INT CHECK(balance>=0))");
   c.createStatement().execute("INSERT INTO member VALUES(1,'lee',100),(2,'kim',100)");
'''
TAIL='\n  }\n }\n}\n'


def step(slug,title,concept,intro,know,before,after,tests,observation,result,caution,accepts=None):
    return dict(slug=slug,title=title,language='java_libraries',libraries=['h2'],start=START_NEW,
        objectives=[concept],intro=[intro],know=know,
        todo=[TODO_RUN_BEFORE,title,TODO_RUN_AFTER,TODO_SUBMIT],
        starter=HEAD+before+TAIL,solution=HEAD+after+TAIL,tests=tests,success=tests[0][1],
        complexity=dict(prior='SELECT·UPDATE와 try-with-resources를 읽을 수 있어요.',new=concept,changed=title,evidence=observation,lines=3),
        narration=[('say',intro,'text:'+intro),('run',),('say',observation,'output'),
            ('patch',before,after,title),('run',),('say',result,'output'),('say',caution,'text:'+know),('submit',)],
        review={intro:'준비된 member 표와 현재 코드의 상태를 설명해요.',observation:'실제 JDBC 실행의 반환값·결과 행과 연결해요.',
            title:'이 단계의 구현 요구를 직접 말해요.',result:'수정 후 실제 표와 출력의 관계를 설명해요.',caution:'현재 API를 오해했을 때 생기는 구체적인 결과를 설명해요.'},
        rejects=[([(after,before)],'수정 전 코드는 변형 입력이나 실패 상황에서 요구한 DB 결과를 만들지 못해요.')],accepts=accepts or [])

B1='''   int minimum=new Scanner(System.in).nextInt();
   int count=0;
   try (PreparedStatement p=c.prepareStatement("SELECT name FROM member WHERE id>=? ORDER BY id")) {
    p.setInt(1,minimum);
    try (ResultSet rows=p.executeQuery()) {
     if (rows.next()) count++;
    }
   }
   System.out.println(count);'''
A1=B1.replace('if (rows.next())','while (rows.next())')
S1=step('cursor','조회한 모든 행을 순회해 개수를 세세요','ResultSet은 행 목록 자체가 아니라 현재 위치를 가진 커서예요.',
    'member에는 두 행이 있어요. 시작 번호 이상인 회원을 조회하지만 준비 코드는 첫 행만 세요.',
    'next()는 다음 행으로 이동하고 행이 있으면 true를 돌려줘요. 한 번의 if는 한 행만 확인해요. 행이 없어질 때까지 순회하세요.',
    B1,A1,[('1','2'),('2','1'),('3','0')],
    '입력 1에서 1만 나와요. 조회에 두 행이 있어도 커서를 한 번만 움직였어요.',
    '입력 1에서 2가 나와요. 반복 조건의 next가 더 이상 행이 없을 때 멈춰요.',
    '조심하세요. while 안에서 next를 한 번 더 부르면 두 행씩 이동해서 일부 회원을 건너뛰어요.')

B2='''   String name=new Scanner(System.in).nextLine();
   int count=0;
   String sql="SELECT id FROM member WHERE name='"+name+"'";
   try (PreparedStatement p=c.prepareStatement(sql)) {
    // 입력을 SQL 문자열에 붙이지 않고 이 자리에 값으로 전달하세요.
    try (ResultSet rows=p.executeQuery()) {
     while(rows.next()) count++;
    }
   }
   System.out.println(count);'''
A2=B2.replace('String sql="SELECT id FROM member WHERE name=\'"+name+"\'";',
              'String sql="SELECT id FROM member WHERE name=?";').replace(
              '// 입력을 SQL 문자열에 붙이지 않고 이 자리에 값으로 전달하세요.', 'p.setString(1,name);')
S2=step('parameters','회원 이름을 SQL 구문과 분리해 전달하세요','매개변수 바인딩은 입력을 SQL 코드가 아닌 값으로 전달해요.',
    '회원 이름을 검색해요. 이름에 SQL의 따옴표와 조건식이 들어오면 준비 코드는 다른 회원까지 찾아요.',
    'SQL에는 ?를 두고 PreparedStatement.setString으로 이름을 전달하세요. 값에 들어온 따옴표를 직접 바꾸지 마세요. 없는 이름은 0명이어야 해요.',
    B2,A2,[("lee' OR '1'='1",'0'),('lee','1'),("O'Reilly",'0'),('none','0')],
    '없는 이름을 넣었는데 두 회원을 모두 찾았어요. 이름에 들어온 조건식이 SQL 문법에 섞였어요.',
    '같은 입력에서 이제 0명이에요. 따옴표와 조건식이 들어온 이름을 하나의 값으로 비교했어요.',
    '조심하세요. ?를 따옴표 안에 쓰면 매개변수 자리가 아니라 물음표 글자를 비교해요.')

B3='''   int id=new Scanner(System.in).nextInt();
   try (PreparedStatement p=c.prepareStatement("UPDATE member SET balance=balance+10 WHERE id=?")) {
    p.setInt(1,id);
    p.executeUpdate();
    System.out.println("saved");
   }'''
A3=B3.replace('p.executeUpdate();\n    System.out.println("saved");', 'int changed=p.executeUpdate();\n    System.out.println(changed==1 ? "saved" : "missing");')
S3=step('affected-rows','수정된 회원이 없으면 missing을 출력하세요','SQL 문장의 성공과 실제로 바뀐 행의 존재를 구별해요.',
    '지정한 회원에게 10을 더해요. 존재하지 않는 번호를 넣어도 준비 코드는 saved라고 말해요.',
    'executeUpdate가 돌려준 변경 행 수를 확인하세요. 이 표에서 id는 기본 키라서 변경 행은 0개 또는 1개예요. SQL 오류가 없다는 것만으로 저장 성공을 판단하지 마세요.',
    B3,A3,[('9','missing'),('1','saved'),('2','saved')],
    '없는 9번 회원에게 saved라고 했어요. SQL 오류는 없지만 실제로 바뀐 행은 없어요.',
    '있는 회원은 saved, 없는 번호는 missing이에요. DB가 보고한 변경 행 수를 사용했어요.',
    '조심하세요. 다른 DB와 드라이버에서는 같은 값을 다시 쓰는 UPDATE의 행 수 의미가 다를 수 있어요. 여기서는 잔액을 실제로 10 늘려요.')

B4='''   int amount=new Scanner(System.in).nextInt();
   try {
    try (PreparedStatement out=c.prepareStatement("UPDATE member SET balance=balance-? WHERE id=1");
         PreparedStatement in=c.prepareStatement("UPDATE member SET balance=balance+? WHERE id=2")) {
     out.setInt(1,amount); out.executeUpdate();
     in.setInt(1,amount); in.executeUpdate();
    }
   } catch(SQLException error) {
    // 실패했을 때 이체 전체를 되돌려야 해요.
   }
   try (ResultSet rows=c.createStatement().executeQuery("SELECT balance FROM member ORDER BY id")) {
    while(rows.next()) System.out.println(rows.getInt(1));
   }'''
# The receiving account has a trigger-free CHECK to make the second statement fail.
PREFIX4='   c.createStatement().execute("ALTER TABLE member ADD CONSTRAINT cap CHECK(balance<=150)");\n'
A4=PREFIX4+B4.replace('   try {','   c.setAutoCommit(false);\n   try {',1).replace('   } catch(SQLException error) {','    c.commit();\n   } catch(SQLException error) {').replace('// 실패했을 때 이체 전체를 되돌려야 해요.','c.rollback();')
S4=step('final-transaction','JDBC 이체가 중간에 실패하면 전체를 취소하세요','Connection의 자동 확정과 명시적 트랜잭션 경계를 제어해요.',
    '잔액은 각각 100이고 상한은 150이에요. 60을 이체하면 출금은 성공하지만 입금은 제약 오류가 나요.',
    '첫 UPDATE 전에 setAutoCommit(false)를 호출하세요. 두 변경이 성공한 뒤 commit하고 SQLException을 받으면 rollback하세요. 준비된 표와 마지막 조회는 그대로 두세요.',
    PREFIX4+B4,A4,[('60','100\n100'),('30','70\n130'),('10','90\n110')],
    '60을 이체했더니 출금만 확정되어 40과 100이 남았어요. 입금이 실패했는데 돈이 줄었어요.',
    '정상 이체는 두 잔액이 함께 바뀌고 입금이 실패한 경우에는 둘 다 100으로 돌아와요.',
    '조심하세요. 예외를 잡아 메시지만 출력하면 이미 확정한 출금이 취소되지는 않아요. 자동 확정부터 끄고 실패 시 rollback해야 해요.')

LESSON=sql_lesson(key='java-jdbc',folder='java_jdbc',pilot='쟈',title='JDBC · 코드와 데이터베이스 사이의 계약',
    objectives=['결과 커서와 변경 행 수를 해석해요.', '입력을 SQL 문법에서 분리해요.', '연결의 트랜잭션으로 업무 경계를 구현해요.'],
    units=[unit('조회와 값 전달','JDBC의 결과와 입력이 무엇인지 확인해요.',[S1,S2]),
           unit('변경과 업무 결과','실제 변경 여부와 원자성을 코드로 지켜요.',[S3,S4])],final_slug='final-transaction',
    sources=[('https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/java/sql/package-summary.html','JDBC API 계약을 확인해요.','고정된 H2 드라이버에서 실제 결과와 실패를 확인해요.')])
LESSON.update(prerequisites=['기본 SQL과 트랜잭션을 알아요.', 'Java의 try-with-resources와 예외 처리를 알아요.'],
              description='실제 H2 드라이버로 SQL 결과·입력·실패를 연결해서 이해해요.')
LESSON['brief']=(LESSON['objectives'][0],'마지막 도전에서 정상 이체와 실패한 이체를 모두 처리하세요.',
    ['조회와 값 전달','변경과 업무 결과'],'실제 JDK 25와 고정된 H2 JDBC 드라이버를 사용해요. 실행마다 새 메모리 DB예요. Docker는 필요 없어요.',
    'SQL 실행에 성공했다는 말만으로 업무도 성공했다고 할 수 있을까요?')
