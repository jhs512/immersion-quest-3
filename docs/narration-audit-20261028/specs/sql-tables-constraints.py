KEY = 'sql-tables-constraints'
T = '템플릿 결함: 목표+DROP 안내 문단과 상황 문단을 그대로 다시 읽고, 개념 문장이 바로 앞 목표 문장을 반복하며 CREATE 줄 전체를 강조하고, 코드 변경 중 제목 명령문을 말하고, 경고가 알아두세요 전체를 강조한다. 모두 고쳤다. '
U = '미해결(본문): 상황 문단이 목표 문장+같은 DROP 안내로 시작, 할 일 2번이 제목 복사(마침표 없음).'
REREAD = '본문 문단을 그대로 다시 읽는다(콘텐츠 룰).'
REPEAT = '바로 앞에서 읽은 목표 문장을 그대로 반복하고, 강조한 CREATE 줄의 현재 상태를 설명하지 않는다.'
TITLE = '코드를 바꾸는 동안 제목 명령문을 그대로 말해 무엇을 바꾸는지 알려 주지 않는다.'
NOTES = {
    1: '전수 검토 2026-10-28: name 제약 없음 → 3행/이름 2 → NOT NULL → 첫 INSERT 전체 거절, 빵만 1/1. ' + T + U + ' 목표(NOT NULL과 빈 문자열의 차이)는 시연에 빈 문자열이 없어 확인되지 않는다(본문·설계).',
    2: '전수 검토 2026-10-28: lee 2행 → UNIQUE → kim 1, lee 1. ' + T + U,
    3: '전수 검토 2026-10-28: NULL·중복 1 → PRIMARY KEY → 1 우유만. ' + T + U,
    4: '전수 검토 2026-10-28: 99번 회원 주문 저장 → FOREIGN KEY → 10번만. ' + T + U,
    5: '전수 검토 2026-10-28: -1 저장 → CHECK(balance >= 0) → 0·7. ' + T + U,
    6: '전수 검토 2026-10-28: 다섯 예약 저장 → CHECK·조합 UNIQUE·FOREIGN KEY → 1·3번. ' + T + U,
}
TARGETS = [
    (1, '조심하세요. 여러 행을', 'text:첫 INSERT는 이름 우유와 NULL인 두 행을 함께 보내요.'),
    (2, '조심하세요. id에만', 'text:UNIQUE는 저장하는 DB에서 같은 값의 중복을 거절해요.'),
    (3, '조심하세요. 이름에 기본 키를', 'text:이름이 같을 수 있으니 이름을 키로 정하지 않아요.'),
    (4, '조심하세요. 주문 번호와', 'text:FOREIGN KEY는 참조할 행이 존재해야 한다는 규칙이에요.'),
    (5, '조심하세요. 0도 허용되는', 'text:CHECK는 각 행의 조건을 검사해요.'),
    (6, '조심하세요. room_id만', 'text:room_id만 UNIQUE면 다른 시간의 정상 예약까지 막아요.'),
]
CODE = [  # concept sentence (code highlight kept, retargeted to the column it describes)
    (1, 'NOT NULL과 빈 문자열의 차이를 이해해요.', 'code:name VARCHAR(30)', '지금 name 열에는 제약이 없어 NULL도 들어가요.'),
    (2, 'UNIQUE가 여러 클라이언트의 중복 저장을 막는다는 것을 이해해요.', 'code:login VARCHAR(30) NOT NULL', '지금 login 열은 NULL만 막아요. 같은 값이 두 번 와도 받아들여요.'),
    (3, 'PRIMARY KEY는 행을 식별하고 중복과 NULL을 막는다는 것을 이해해요.', 'code:id INT', '지금 id는 그냥 정수 열이에요. 겹치거나 비어도 막지 않아요.'),
    (4, '외래 키가 두 표 사이의 존재 규칙을 지켜요.', 'code:member_id INT NOT NULL', '지금 member_id는 숫자만 받아요. 그 번호의 회원이 있는지는 보지 않아요.'),
    (5, 'CHECK는 저장되는 각 행의 값 범위를 보호해요.', 'code:balance INT NOT NULL', '지금 balance는 NOT NULL뿐이라 값만 있으면 음수도 받아요.'),
    (6, '기본 키·외래 키·조합 UNIQUE·CHECK를 서로 다른 규칙에 적용해요.', 'code:people INT NOT NULL', '지금은 모든 열이 NOT NULL뿐이에요. 중복·없는 방·0명을 막지 못해요.'),
]
TARGETS += [(n, old, target) for n, old, target, _ in CODE]
PATCH = {
    1: ('이름이 없는 회원을 DB에서 거절하세요', 'name 열 뒤에 NOT NULL을 붙여요.'),
    2: ('같은 로그인 이름이 두 번 저장되지 않게 하세요', 'login 열에 UNIQUE를 더해요.'),
    3: ('회원 번호가 없거나 겹치는 행을 막으세요', 'id 열을 PRIMARY KEY로 정해요.'),
    4: ('없는 회원의 주문을 저장하지 못하게 하세요', 'member_id가 member.id를 가리키는 FOREIGN KEY를 더해요.'),
    5: ('금액이 음수인 행을 DB에서 막으세요', 'balance에 0 이상이라는 CHECK를 더해요.'),
    6: ('다른 클라이언트가 와도 예약 규칙을 지키세요', '인원 CHECK, 방·시간 조합 UNIQUE, 방 FOREIGN KEY를 더해요.'),
}
DROP = {
    1: ('NOT NULL과 빈 문자열의 차이를 이해해요. 실행할 때', 'DROP TABLE 줄은 이 실험용 member 표만 새로 만들어요. 실행할 때마다 같은 조건에서 시작해요.'),
    2: ('UNIQUE가 여러 클라이언트의 중복 저장을 막는다는 것을 이해해요. 실행할 때', '이번에도 DROP TABLE 줄이 member 표를 새로 만들어요. 앞 실행의 행은 남지 않아요.'),
    3: ('PRIMARY KEY는 행을 식별하고 중복과 NULL을 막는다는 것을 이해해요. 실행할 때', '이번 member 표도 DROP TABLE로 새로 만들어요. 번호 규칙만 바꿔 비교해요.'),
    4: ('외래 키가 두 표 사이의 존재 규칙을 지켜요. 실행할 때', 'DROP TABLE 줄은 orders 표만 다시 만들어요. member 표는 그대로예요.'),
    5: ('CHECK는 저장되는 각 행의 값 범위를 보호해요. 실행할 때', 'DROP TABLE 줄이 wallet 표를 새로 만들어요. 잔액 규칙만 바꿔 비교해요.'),
    6: ('기본 키·외래 키·조합 UNIQUE·CHECK를 서로 다른 규칙에 적용해요. 실행할 때', '마지막도 DROP TABLE 줄이 reservation 표를 새로 만들어요. 이번에는 규칙 네 개를 함께 선언해요.'),
}
SITU = {
    1: ('첫 INSERT는 이름 우유와', '검사 SQL은 우유와 NULL 두 행을 한 문장으로 넣고, 빵은 따로 넣어요.'),
    2: ('서로 다른 두 클라이언트가', '두 클라이언트가 각자 lee를 보내고, kim도 하나 들어와요.'),
    3: ('1번 회원을 두 번 저장하고', '검사 SQL은 1번을 두 번, 번호 없는 회원을 한 번 넣어요.'),
    4: ('회원 표에는 1번만 있어요', '회원은 1번만 있는데, 검사 SQL이 99번 회원의 주문도 보내요.'),
    5: ('서로 다른 클라이언트가 잔액', '검사 SQL은 잔액 0, -1, 7을 넣어요. 막을 것은 음수 하나예요.'),
    6: ('방은 여러 시간에 예약할 수', '한 방을 여러 시간에 예약할 수 있어요. 막을 것은 같은 방·같은 시간의 두 번째 예약이에요.'),
}
FIXES = {}
for n in range(1, 7):
    FIXES[n] = [
        (DROP[n][0], DROP[n][1], REREAD + ' 목표 문장과 모든 스텝에 같은 DROP 안내를 함께 읽는다.', 'DROP TABLE의 이유(같은 조건 비교)를 스텝마다 다른 말로 짧게 말한다.'),
        (SITU[n][0], SITU[n][1], REREAD, '검사 SQL이 넣는 값과 막을 대상을 말한다(실제 결과 표와 대응).'),
        (CODE[n - 1][1], CODE[n - 1][3], REPEAT, '강조를 그 열 정의로 옮기고 현재 열이 무엇을 막지 못하는지 말한다.'),
        (PATCH[n][0], PATCH[n][1], TITLE, 'patch_code의 실제 차이를 말한다.'),
    ]
