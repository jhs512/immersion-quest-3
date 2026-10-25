"""Transaction boundaries and failure, with real PostgreSQL statements and state."""
from sql_lab import sql_step, sql_lesson, unit

SEED = "CREATE TABLE account(id INT PRIMARY KEY, balance INT NOT NULL CHECK(balance>=0 AND balance<=150)); INSERT INTO account VALUES(1,100),(2,100);\n"
SHOW = "SELECT id||':'||balance FROM account ORDER BY id;\n"


def step(slug, title, concept, intro, know, starter, solution, expected, first, result, caution, *, variants=None, before=SEED):
    return sql_step(slug=slug, title=title, concept=concept, intro=intro, know=know,
                    before=before, starter=starter, solution=solution, after=SHOW,
                    expected=expected, first_output=first, result=result,
                    caution=caution, variants=variants)


S1 = step('rollback', '시험 변경을 저장하지 않고 되돌리세요', 'UPDATE의 성공과 트랜잭션 확정을 구별해요.',
          '잔액 100을 80으로 바꾸는 시험이에요. 실제 업무로 확정하면 안 되는데 준비 코드는 COMMIT해요.',
          'BEGIN부터 끝까지가 한 트랜잭션이에요. ROLLBACK은 이 트랜잭션이 바꾼 데이터를 취소해요. 끝난 뒤 SELECT로 잔액이 100인지 확인하세요.',
          'BEGIN;\nUPDATE account SET balance=80 WHERE id=1;\nCOMMIT;\n',
          'BEGIN;\nUPDATE account SET balance=80 WHERE id=1;\nROLLBACK;\n', '1:100\n2:100',
          '1번 잔액이 80이에요. 시험 변경을 COMMIT해서 남겼어요.',
          '1번 잔액이 100으로 돌아왔어요. 실행한 UPDATE를 확정하지 않았어요.',
          '조심하세요. 이미 COMMIT한 변경은 나중에 ROLLBACK을 붙여도 그 트랜잭션으로 되돌릴 수 없어요.')

TRANSFER = 'UPDATE account SET balance=balance-30 WHERE id=1;\nUPDATE account SET balance=balance+30 WHERE id=2;\n'
S2 = step('commit', '두 계좌의 이체를 함께 확정하세요', '업무 하나의 여러 변경을 같은 트랜잭션으로 묶어요.',
          '1번에서 2번으로 30을 옮겨요. 준비 코드는 두 변경을 실행하지만 마지막에 취소해요.',
          '이체가 성공하면 1번은 70, 2번은 130이어야 해요. BEGIN 뒤에 두 변경을 넣고 모두 성공했을 때 COMMIT하세요.',
          'BEGIN;\n'+TRANSFER+'ROLLBACK;\n', 'BEGIN;\n'+TRANSFER+'COMMIT;\n', '1:70\n2:130',
          '두 잔액이 모두 100이에요. 계산이 틀린 것이 아니라 마지막에 취소했어요.',
          '잔액은 70과 130이에요. 같은 트랜잭션의 두 변경을 함께 확정했어요.',
          '조심하세요. 첫 UPDATE 직후 COMMIT하면 출금과 입금이 서로 다른 업무 단위가 돼요.')

BAD = 'UPDATE account SET balance=balance-60 WHERE id=1;\nUPDATE account SET balance=balance+60 WHERE id=2;\n'
S3 = step('atomic-failure', '입금이 거절되면 출금도 남지 않게 하세요', '원자성은 중간 실패 때 일부 변경만 남기지 않는 성질이에요.',
          '계좌의 잔액 상한은 150이에요. 60을 이체하면 입금이 거절되는데 준비 코드에서는 출금 60만 남아요.',
          '이 실습의 psql은 오류 후에도 다음 문장을 읽어요. 한 트랜잭션 안에서 SQL 오류가 나면 그 트랜잭션은 실패 상태가 돼요. 마지막에 COMMIT을 요청해도 실패한 트랜잭션은 확정되지 않아요.',
          BAD, 'BEGIN;\n'+BAD+'COMMIT;\n', '1:100\n2:100',
          '1번은 40이고 2번은 100이에요. 자동 확정으로 출금 문장만 따로 저장됐어요.',
          '입금 제약 오류는 남아 있지만 두 잔액은 모두 100이에요. 출금도 함께 취소됐어요.',
          '조심하세요. SELECT 출력만 원래 잔액으로 바꾸는 것은 복구가 아니에요. 제공 조회가 실제 표를 다시 읽어요.')

S4 = step('savepoint', '선택 작업의 실패만 취소하세요', 'SAVEPOINT는 한 트랜잭션 안에서 되돌아갈 지점을 만들어요.',
          '먼저 10을 입금하고 보너스를 더하려 해요. 보너스 100은 상한을 넘으므로 취소하되 처음 입금 10은 남겨야 해요.',
          '보너스를 시도하기 직전에 SAVEPOINT bonus를 만드세요. 오류가 나면 ROLLBACK TO bonus로 실패 상태를 해제하고 앞의 정상 변경을 COMMIT하세요.',
          'BEGIN;\nUPDATE account SET balance=balance+10 WHERE id=1;\nUPDATE account SET balance=balance+100 WHERE id=1;\nROLLBACK;\n',
          'BEGIN;\nUPDATE account SET balance=balance+10 WHERE id=1;\nSAVEPOINT bonus;\nUPDATE account SET balance=balance+100 WHERE id=1;\nROLLBACK TO bonus;\nCOMMIT;\n',
          '1:110\n2:100', '전체 ROLLBACK으로 정상 입금 10까지 사라졌어요.',
          '1번은 110이에요. 보너스 직전으로 돌아가고 그 전의 정상 작업은 확정했어요.',
          '조심하세요. SAVEPOINT가 오류를 자동으로 무시하지는 않아요. 실패 후 되돌릴 지점을 명시해야 계속 진행할 수 있어요.')

REQUEST = 'CREATE TABLE request(amount INT); INSERT INTO request VALUES(30);\n'
BODY = 'UPDATE account SET balance=balance-(SELECT amount FROM request) WHERE id=1;\nUPDATE account SET balance=balance+(SELECT amount FROM request) WHERE id=2;\n'
S5 = step('final-transfer', '정상 이체는 확정하고 실패한 이체는 전부 취소하세요', '성공과 중간 오류를 같은 트랜잭션 경계로 처리해요.',
          '입력 표 request의 금액을 이체하세요. 정상 금액과 입금 상한을 넘는 금액을 모두 검사해요.',
          '준비된 account·request와 마지막 조회는 바꾸지 않아요. 두 UPDATE가 같은 트랜잭션에 속하도록 구현하세요. 실제 애플리케이션에서는 예외 처리에서 rollback하고 사용자에게 실패를 알려야 해요.',
          BODY, 'BEGIN;\n'+BODY+'COMMIT;\n', '1:70\n2:130',
          '30인 이번 입력은 우연히 두 문장 모두 성공해요. 오류 입력에서 일부 변경이 남는지도 검사해야 해요.',
          '정상 금액은 두 계좌에 반영돼요. 입금이 실패하는 검사에서는 출금도 취소되는지 함께 확인해요.',
          '조심하세요. 이 실습의 오류 후 계속 읽기 설정은 관찰을 위한 준비 코드예요. 운영 코드에서 오류를 무시하라는 뜻은 아니에요.',
          before=SEED+REQUEST,
          variants=[dict(files={'before.sql': SEED+REQUEST.replace('(30)','(60)')}, expected='1:100\n2:100'),
                    dict(files={'before.sql': SEED+REQUEST.replace('(30)','(10)')}, expected='1:90\n2:110')])
# The initial final problem can succeed on a normal amount, so verify it against
# both normal and failing inputs rather than declaring the normal run a failure.

LESSON = sql_lesson(key='sql-transactions', folder='sql_transactions', pilot='트',
                    title='트랜잭션 · 절반만 끝난 이체를 막아요',
                    objectives=['문장 실행과 업무 확정을 구별해요.', '중간 실패에서 원자성을 확인해요.', '정상·실패 입력에 맞는 트랜잭션 경계를 구현해요.'],
                    units=[unit('확정과 취소', '여러 변경의 저장 시점을 정해요.', [S1,S2]),
                           unit('실패에서 원리 찾기', '오류의 영향을 관찰하고 취소 범위를 정해요.', [S3,S4]),
                           unit('최종 이체', '오류가 없는 경우와 있는 경우를 모두 지켜요.', [S5])],
                    final_slug='final-transfer', sources=[('https://www.postgresql.org/docs/18/tutorial-transactions.html','원자성·SAVEPOINT·오류 후 실패 상태를 확인해요.','실제 psql 오류와 최종 표 상태를 대조해요.')])
