"""aice-table-csv final challenge: read a CSV, report its whole size and keep two columns, checked on other files."""
from _common import Script, todo, ids, next_revision

KEY = 'aice-table-csv'
UNIT, STEP = ids(KEY)
CSV = 'order_id,minutes,region\n101,12,서울\n102,18,부산\n103,30,서울\n104,42,부산\n105,24,서울\n'
SHAPE_TODO = 'print(df.head(2).shape)  # 1) 표 전체의 (행 수, 열 수)를 출력하세요.'
SMALL_TODO = 'small = df  # 2) 주문 번호와 배송 시간 두 열만 남긴 표를 만드세요.'
STARTER = f'''# 판다스를 pd라는 이름으로 불러와요.
import pandas as pd
# 제공 파일 delivery.csv를 읽어요. 첫 행은 열 이름이에요.
df = pd.read_csv("delivery.csv")
{SHAPE_TODO}
{SMALL_TODO}
# 3) 남긴 표의 앞 두 행을 확인해요.
print(small.head(2))
'''
SHAPE = '# head는 앞부분만 보여 줘요. 크기는 원래 표에서 읽어요.\nprint(df.shape)'
SMALL = '# 열 이름 목록을 넘기면 그 열들만 남은 표가 돼요.\nsmall = df[["order_id", "minutes"]]'
SOLUTION = STARTER.replace(SHAPE_TODO, SHAPE).replace(SMALL_TODO, SMALL)
# Other delivery files: the checker writes each one, runs main.py and compares with pandas' own result.
CHECKER = '''import subprocess
import sys
from pathlib import Path

import pandas as pd

files = [
    "order_id,minutes,region\\n201,7,부산\\n",
    "order_id,minutes,region,distance\\n301,15,서울,2\\n302,9,부산,1\\n303,40,서울,5\\n304,11,부산,1\\n305,22,서울,3\\n306,31,부산,4\\n307,5,서울,1\\n",
    "region,minutes,order_id\\n서울,50,401\\n부산,45,402\\n",
]
original = Path("delivery.csv").read_text(encoding="utf-8")
try:
    for text in files:
        Path("delivery.csv").write_text(text, encoding="utf-8")
        table = pd.read_csv("delivery.csv")
        expected = f"{table.shape}\\n{table[['order_id', 'minutes']].head(2)}"
        result = subprocess.run([sys.executable, "-I", "-X", "utf8", "main.py"], stdin=subprocess.DEVNULL,
                                capture_output=True, text=True, encoding="utf-8", timeout=30)
        if result.returncode != 0 or result.stdout.strip() != expected.strip():
            raise AssertionError("다른 배송 파일에서도 전체 크기와 두 열의 앞부분을 맞게 출력하세요.")
finally:
    Path("delivery.csv").write_text(original, encoding="utf-8")
print("다른 배송 파일 세 개에서도 통과했어요.")
'''

s = Script(STARTER)
s.say('마지막 도전이에요. 배송 파일을 읽어 표 전체의 크기를 출력하고, 주문 번호와 배송 시간 두 열만 남긴 표의 앞 두 행을 확인해요.',
      'text:크기는 앞부분이 아니라 표 전체의 크기예요.')
s.run()
s.say('(2, 3)이 나와요. 앞 두 행의 크기라서 다섯 건짜리 표와 달라요. 아래 표도 세 열이 다 보여요.', 'output')
s.patch(SHAPE_TODO, SHAPE, '크기는 원래 표 df에서 읽어요.')
s.patch(SMALL_TODO, SMALL, '두 열 이름을 목록으로 넘겨 표로 남겨요.')
s.run()
s.say('(5, 3) 아래에 order_id와 minutes 두 열만 두 행 보여요.', 'output')
s.say('조심하세요. 대괄호를 한 겹만 써서 df["order_id", "minutes"]라고 적으면 두 열을 고르지 못하고 KeyError가 나요.', 'code:small = df[["order_id", "minutes"]]')

GOAL = ('자, 마지막 도전이에요. 배송 파일 delivery.csv를 표 df로 읽었어요. 파일의 행 수와 열은 날마다 달라질 수 있어요.\n\n'
        '첫 줄에 표 전체의 (행 수, 열 수)를 출력해요. 크기는 앞부분이 아니라 표 전체의 크기예요. '
        '그다음 주문 번호와 배송 시간 두 열만 남긴 표 small을 만들어 앞 두 행을 출력해요. 지금 파일이면 첫 줄이 `(5, 3)`이에요. '
        '채점은 행·열 수와 열 순서가 다른 파일로도 실행해요.\n\n'
        + todo('코드 실행을 눌러 지금 출력을 확인하세요.',
               '첫 줄이 표 전체의 크기를 출력하도록 고치세요.',
               '두 열만 남긴 표를 small로 만드세요.',
               '다시 실행해 크기와 두 열을 확인한 뒤 제출하세요.'))

SPEC = dict(
    key=KEY, course='aice', revision=next_revision(KEY, 'aice-table-csv-5'),
    reason='CSV 읽기, 일부 관찰(head)과 전체 크기(shape)의 구별, 여러 열 선택을 한 파일에서 함께 쓰고 다른 파일로 확인하는 마지막 도전이에요.',
    grading='실제 파이썬 출력과, 행·열 수와 열 순서가 다른 배송 파일 세 개로 다시 실행해 판다스 결과와 비교해요. head의 크기, 고정 크기, 한 열만 남기기는 실패해요.',
    unit=dict(id=UNIT, title='마지막 도전', objectives=['파일의 전체 크기와 필요한 열을 함께 확인해요.'],
              premise='오늘의 배송 파일이에요. 앞 스텝과 상관없이 바로 풀 수 있어요.'),
    step=dict(id=STEP, title='배송 파일의 크기를 보고 두 열만 남기세요',
              objectives=['head와 shape를 구별하고 두 열을 표로 남겨요.'],
              core_flow='준비 코드는 df.head(2).shape와 전체 표를 출력한다. 학생은 df.shape와 df[["order_id", "minutes"]]를 쓴다. '
                        '채점: 제공 파일 실행 출력과 검사기가 다른 파일 세 개를 써서 판다스 기준 결과와 비교한다.'),
    task=dict(id=STEP, title='배송 파일의 크기를 보고 두 열만 남기세요', language='python', goal=GOAL,
              starter_code=STARTER, solution=SOLUTION, required=True, files={'delivery.csv': CSV}, checker=CHECKER,
              tests=[dict(input='', expected='(5, 3)\n   order_id  minutes\n0       101       12\n1       102       18')], narration=s.actions),
    cases=dict(expected_outputs=['(2, 3)\n   order_id  minutes region\n0       101       12     서울\n1       102       18     부산',
                                 '(5, 3)\n   order_id  minutes\n0       101       12\n1       102       18'],
               reject=[([['print(df.shape)', 'print(df.head(2).shape)']], 'The size of head is not the size of the table'),
                       ([['print(df.shape)', 'print((5, 3))']], 'A fixed size fails other files'),
                       ([['small = df[["order_id", "minutes"]]', 'small = df[["minutes"]]']], 'Both columns are needed')],
               accept=[([['small = df[["order_id", "minutes"]]', 'small = df.loc[:, ["order_id", "minutes"]]']], 'loc with a column list keeps the same two columns')]),
    review={'조심하세요. 대괄호를 한 겹만 써서 df["order_id", "minutes"]라고 적으면 두 열을 고르지 못하고 KeyError가 나요.':
            '이 수업 7번의 두 열 선택에서 실제로 흔한 표기 실수를 실제 오류 이름으로 말해요.'},
)
