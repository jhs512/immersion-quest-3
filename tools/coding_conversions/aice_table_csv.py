"""aice-table-csv: 7 answer-picking steps -> coding steps (2026-10-29).

Steps built from a dict vary the dict through prepared cases. Steps that read delivery.csv are graded
by rewriting delivery.csv with other files (other row counts, an extra column, another column order)
and comparing the learner's real output with the reference solution's on each file."""
from _kit import Script, todo, py_cases, file_variants_checker

OPENING = ['이 수업에서는 표의 행·열·인덱스를 구별해요. 일부를 보는 일과 전체 크기 확인도 직접 코드로 나눠 봐요.',
           'CSV에서 읽은 배송 표를 살펴봐요. 필요한 열과 항목을 직접 골라 꺼내며 표를 익혀요.']
PRD_SCOPE = ['DataFrame의 열 이름·head·shape·한 열/열 목록 선택·CSV 읽기·iloc의 첫 위치를 한 줄씩 직접 고쳐 비교해요.',
             '두 챕터·두 단원·아홉 스텝에 같은 배송 자료를 이어 써요. 매 스텝은 자기 시작 자료를 갖춰요.']
PRD_GRADING = ['직접 고친 코드를 실제 파이썬·판다스로 실행해 판정해요. 실행·해설만으로 성공시키지 않아요.',
               '출력 표의 공백 정렬이나 pandas repr 전체를 문자열로 암기해 맞히게 하지 않아요. 표 자료나 CSV 파일을 바꿔 다시 실행하고, 같은 자료에 대한 기준 풀이의 실제 결과와 비교해 행·열·선택된 값의 의미를 확인해요.',
               '해설 뒤 풀어도 정상 성공이고 전후 열람은 상세 아이콘으로 남겨요.',
               '마지막 도전(stp_85c153cc-a269-4604-a699-06c7cd6342dc): 실제 파이썬 출력과, 행·열 수와 열 순서가 다른 배송 파일 세 개로 다시 실행해 판다스 결과와 비교해요. head의 크기, 고정 크기, 한 열만 남기기는 실패해요.']
PRD_NARRATION = ['head의 숫자·열 이름·인덱스 한 곳씩 고치고 실행해 결과를 읽어요.',
                 '설명하는 표의 행·열과 코드 줄·실행·결과를 정확히 짚어요. 기본 표를 크게 한 번에 바꾸지 않아요.',
                 'head로 본 두 건이 전체가 아니란 지점을 shape과 비교해요. 음성을 준비한 뒤 화면과 맞춰요.']

DICT_HEAD = ('# 판다스(pandas)를 pd라는 짧은 이름으로 불러와요.\nimport pandas as pd\n'
             '# 같은 열의 값들을 목록으로 모아요. 목록의 길이는 같아요.\n'
             'delivery = {"order_id": [101, 102, 103, 104],\n            "minutes": [12, 18, 30, 42],\n            "region": ["서울", "부산", "서울", "부산"]}\n'
             '# 열 이름과 값 목록을 표(DataFrame)로 만들어요.\ndf = pd.DataFrame(delivery)\n')
CSV_HEAD = '# 판다스를 pd라는 이름으로 불러와요.\nimport pandas as pd\n# 제공 파일은 실행 폴더에 있어요. 첫 행은 열 이름이에요.\n'
CSV = 'order_id,minutes,region\n101,12,서울\n102,18,부산\n103,30,서울\n104,42,부산\n'
CSV5 = CSV + '105,24,서울\n'
OTHER_CSVS = [{'delivery.csv': 'order_id,minutes,region\n201,7,부산\n'},
              {'delivery.csv': 'order_id,minutes,region,distance\n301,15,서울,2\n302,9,부산,1\n303,40,서울,5\n304,11,부산,1\n305,22,서울,3\n'},
              {'delivery.csv': 'region,minutes,order_id\n서울,50,401\n부산,45,402\n부산,8,403\n'}]
OTHER_DICTS = [{'delivery': {'order_id': [201], 'minutes': [7], 'region': ['부산']}},
               {'delivery': {'order_id': [301, 302, 303, 304, 305], 'minutes': [15, 9, 40, 11, 22], 'region': ['서울', '부산', '서울', '부산', '서울'], 'distance': [2, 1, 5, 1, 3]}},
               {'delivery': {'minutes': [50, 45], 'region': ['서울', '부산'], 'order_id': [401, 402]}}]
CSV_MESSAGE = '다른 배송 파일에서도 같은 원리로 맞는 결과가 나와야 해요.'

s1 = DICT_HEAD + '# 이 줄을 고쳐 표 전체 대신 열 이름 목록을 출력하세요.\nprint(df)\n'
s1_solution = DICT_HEAD + '# 이 줄을 고쳐 표 전체 대신 열 이름 목록을 출력하세요.\n# columns는 표가 가진 열 이름들이에요. list로 바꾸면 이름만 보기 쉬워요.\nprint(list(df.columns))\n'
n1 = (Script(s1)
      .say('표의 맨 위에 열 이름이, 왼쪽에 인덱스가 보여요. 열 이름만 목록으로 출력해야 해요.', 'text:print 줄을 고쳐 표 전체 대신 열 이름 목록을 출력하세요.')
      .run('print(df)')
      .say('표 전체가 나와요. 맨 위 order_id, minutes, region이 열 이름이고 왼쪽 0부터 3은 인덱스예요.', 'output')
      .patch('print(df)\n', 'print(list(df.columns))\n', 'df.columns를 list로 바꿔 출력해요.')
      .run('print(list(df.columns))')
      .say("['order_id', 'minutes', 'region']이에요. 배송 시간은 minutes 열에 있어요.", 'output')
      .say('조심하세요. 왼쪽의 0, 1, 2, 3은 열 이름이 아니라 행을 가리키는 인덱스예요.', 'code:df.columns'))

s3 = DICT_HEAD + '# 두 건만 본 뒤 원래 표의 크기를 확인해요.\nprint(df.head(2))\n# 이 줄을 고쳐 앞부분이 아니라 원래 표 df의 크기를 출력하세요.\nprint(df.head(2).shape)\n'
s3_solution = s3.replace('print(df.head(2).shape)', '# shape은 괄호 없이 읽는 속성이에요. head 결과가 아니라 df에서 읽어요.\nprint(df.shape)')
n3 = (Script(s3)
      .say('head(2)처럼 괄호가 붙은 것은 호출이고, shape은 표가 가진 정보예요. 원래 표의 크기를 출력해야 해요.', 'text:마지막 print 줄을 고쳐 앞부분이 아니라 원래 표 df의 크기를 출력하세요.')
      .run('print(df.head(2))', 'print(df.head(2).shape)')
      .say('앞 두 건과 (2, 3)이에요. head(2)로 자른 표의 크기를 읽었어요.', 'output')
      .patch('print(df.head(2).shape)', 'print(df.shape)', '.head(2)를 지우고 df.shape을 읽어요.')
      .run('print(df.head(2))', 'print(df.shape)')
      .say('(4, 3)이에요. 원래 표는 4행 3열이에요.', 'output')
      .say('조심하세요. head는 보여 주기만 해요. 원래 df의 행을 줄이지 않아요.', 'code:print(df.shape)'))

s4 = DICT_HEAD + '# 이 줄의 열 이름을 고쳐 배송시간 값들을 꺼내세요.\nprint(df["region"].tolist())\n'
s4_solution = s4.replace('print(df["region"].tolist())', '# 대괄호에 열 이름 하나를 주면 그 열의 값들을 골라요.\nprint(df["minutes"].tolist())')
n4 = (Script(s4)
      .say('배송시간 네 개만 확인하려 해요. 열 이름을 고쳐 minutes 열을 골라야 해요.', 'text:print 줄의 열 이름을 고쳐 배송시간 값들을 꺼내세요.')
      .run('print(df[')
      .say('서울, 부산 같은 지역이 나와요. region 열을 골랐어요.', 'output')
      .patch('df["region"]', 'df["minutes"]', '열 이름을 "minutes"로 바꿔요.')
      .run('print(df[')
      .say('[12, 18, 30, 42]예요. 배송시간 열의 값 네 개예요.', 'output')
      .say('조심하세요. df.head(1)은 첫 행 하나예요. 한 열의 값들을 고르는 것과 달라요.', 'code:df["minutes"]'))

s5 = CSV_HEAD + '# 이 줄의 파일 이름을 고쳐 제공된 배송 파일을 읽으세요.\ndf = pd.read_csv("minutes.csv")\nprint(df.shape)\n'
s5_solution = s5.replace('df = pd.read_csv("minutes.csv")', '# read_csv는 실행 폴더에서 이 이름의 파일을 찾아 표로 읽어요.\ndf = pd.read_csv("delivery.csv")')
n5 = (Script(s5)
      .say('제공된 파일은 delivery.csv예요. read_csv가 찾을 파일 이름을 고쳐야 해요.', 'text:read_csv 줄의 파일 이름을 고쳐 제공된 배송 파일을 읽으세요.')
      .run('print(df.shape)', error='FileNotFoundError')
      .say('FileNotFoundError예요. 실행 폴더에 minutes.csv가 없어요.', 'output')
      .patch('pd.read_csv("minutes.csv")', 'pd.read_csv("delivery.csv")', '파일 이름을 delivery.csv로 바꿔요.')
      .run('print(df.shape)')
      .say('(4, 3)이에요. 파일의 첫 행은 열 이름이 되고 나머지 네 줄이 행이 됐어요.', 'output')
      .say('조심하세요. 열 이름 minutes는 파일 이름이 아니에요. 괄호 안에는 실제 파일 이름을 써요.', 'code:pd.read_csv("delivery.csv")'))

s6 = CSV_HEAD + 'df = pd.read_csv("delivery.csv")\n# 이 줄의 위치를 고쳐 minutes 열의 첫 항목을 출력하세요.\nprint(df["minutes"].iloc[1])\n'
s6_solution = s6.replace('print(df["minutes"].iloc[1])', '# iloc의 위치도 0부터 세어요. 첫 항목은 0이에요.\nprint(df["minutes"].iloc[0])')
n6 = (Script(s6)
      .say('첫 배송시간을 꺼내야 해요. iloc의 위치를 확인해요.', 'text:print 줄의 위치를 고쳐 minutes 열의 첫 항목을 출력하세요.')
      .run('print(df[')
      .say('18이에요. 위치 1은 두 번째 항목이에요.', 'output')
      .patch('.iloc[1]', '.iloc[0]', '위치를 0으로 바꿔요.')
      .run('print(df[')
      .say('12예요. 위치 0의 첫 항목이에요.', 'output')
      .say('조심하세요. iloc은 위치로, 인덱스 이름과 상관없이 고르는 방법이에요. 첫 위치는 0이에요.', 'code:.iloc[0]'))

s7 = CSV_HEAD + 'df = pd.read_csv("delivery.csv")\n# 이 줄을 고쳐 주문번호와 배송시간 두 열이 남은 표를 만드세요.\nsmall = df["minutes"]\nprint(small)\n'
s7_solution = s7.replace('small = df["minutes"]', '# 열 이름 목록을 대괄호 안에 넣으면 그 열들만 남은 표가 돼요.\nsmall = df[["order_id", "minutes"]]')
n7 = (Script(s7)
      .say('주문번호와 배송시간 두 열만 전달하려 해요. 열 이름 목록으로 골라야 해요.', 'text:small 줄을 고쳐 주문번호와 배송시간 두 열이 남은 표를 만드세요.')
      .run('print(small)')
      .say('배송시간 한 열만 나와요.', 'output')
      .patch('small = df["minutes"]', 'small = df[["order_id", "minutes"]]', '대괄호 안에 ["order_id", "minutes"] 목록을 넣어요.')
      .run('print(small)')
      .say('order_id와 minutes 두 열이 남은 표예요. region은 빠졌어요.', 'output')
      .say('조심하세요. 대괄호가 두 겹이에요. 바깥은 고르기, 안쪽은 열 이름 목록이에요.', 'code:df[["order_id", "minutes"]]'))

s8 = CSV_HEAD + 'df = pd.read_csv("delivery.csv")\n# 앞부분과 원래 표의 행 수를 비교해요.\nprint(df.head(2))\n# 이 줄을 고쳐 앞부분이 아니라 원래 표의 행 수를 담으세요.\nrows = len(df.head(2))\nprint(rows)\n'
s8_solution = s8.replace('rows = len(df.head(2))', '# head를 본 뒤에도 df는 그대로예요. 행 수는 df에서 세요.\nrows = len(df)')
n8 = (Script(s8)
      .say('배송 한 건이 더 들어왔어요. 앞부분을 본 뒤 원래 표의 행 수를 담아야 해요.', 'text:rows 줄을 고쳐 앞부분이 아니라 원래 표의 행 수를 담으세요.')
      .run('print(df.head(2))', 'print(rows)')
      .say('앞 두 건과 2예요. head(2)의 행 수를 셌어요.', 'output')
      .patch('rows = len(df.head(2))', 'rows = len(df)', '.head(2)를 지우고 df의 행 수를 세요.')
      .run('print(df.head(2))', 'print(rows)')
      .say('5예요. 새 배송까지 다섯 건이에요.', 'output')
      .say('조심하세요. 파일이 바뀌면 행 수도 바뀌어요. 숫자를 적지 말고 표에서 세요.', 'code:rows = len(df)'))

SPECS = [
    dict(old='stp_f7b0188e-642a-48bd-8538-e99f9aed0247', title='df.columns로 열 이름 목록을 출력하세요',
         objectives=['표의 열 이름과 인덱스를 구별해요.'],
         core_flow='print(df)로 표 전체를 본 뒤 list(df.columns)로 열 이름 목록을 출력해 배송시간 열 minutes를 찾는다. 왼쪽 0~3은 인덱스다. 채점은 열 구성이 다른 자료로 실행한다.',
         goal='판다스의 표(DataFrame)는 맨 위에 열 이름, 왼쪽에 행을 가리키는 인덱스가 있어요. `df.columns`는 표가 가진 열 이름들이에요.\n\n'
              'print 줄을 고쳐 표 전체 대신 열 이름 목록을 출력하세요. `list(df.columns)`로 써요. 채점은 열 구성이 다른 자료로도 실행해요.\n\n'
              + todo('코드 실행을 눌러 표 전체가 나오는지 확인하세요.', '`print(df)`를 `print(list(df.columns))`로 고치세요.', '코드 실행을 눌러 열 이름 세 개가 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s1, solution=s1_solution, tests=[{'input': '', 'expected': "['order_id', 'minutes', 'region']"}],
         prepared_cases=py_cases(s1_solution, *OTHER_DICTS),
         narration=n1.actions,
         review={'조심하세요. 왼쪽의 0, 1, 2, 3은 열 이름이 아니라 행을 가리키는 인덱스예요.': '실제 판다스 표시 형식을 정확히 말해요.'},
         reject=[([['print(list(df.columns))', "print(['order_id', 'minutes', 'region'])"]], 'Typing the names'), ([['print(list(df.columns))', 'print(list(df.index))']], 'The index instead of the columns')],
         accept=[([['print(list(df.columns))', 'print(df.columns.tolist())']], 'Index.tolist')]),
    dict(old='stp_b2770a40-abcf-4130-a60f-65d8214ba3b1', title='df.shape으로 원래 표의 크기를 출력하세요',
         objectives=['앞부분 보기와 원래 표의 크기를 구별해요.'],
         core_flow='df.head(2).shape은 (2, 3)이다. df.shape으로 고쳐 (4, 3)을 확인한다. head는 df를 바꾸지 않는다. 채점은 행·열 수가 다른 자료로 실행한다.',
         goal='앞의 두 건만 봤어요. `head(2)`처럼 괄호가 붙은 것은 일을 시키는 호출이고, `shape`처럼 괄호 없이 점 뒤에 이름만 쓰는 것은 표가 이미 가진 정보(속성)를 읽는 거예요. shape은 (행 수, 열 수)예요.\n\n'
              '마지막 print 줄을 고쳐 앞부분이 아니라 원래 표 df의 크기를 출력하세요. 채점은 행·열 수가 다른 자료로도 실행해요.\n\n'
              + todo('코드 실행을 눌러 (2, 3)이 나오는지 확인하세요.', '`df.head(2).shape`을 `df.shape`으로 고치세요.', '코드 실행을 눌러 (4, 3)이 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s3, solution=s3_solution, tests=[{'input': '', 'expected': py_cases(s3_solution, {'delivery': {"order_id": [101, 102, 103, 104], "minutes": [12, 18, 30, 42], "region": ["서울", "부산", "서울", "부산"]}})[0]['expected']}],
         prepared_cases=py_cases(s3_solution, *OTHER_DICTS),
         narration=n3.actions,
         review={'조심하세요. head는 보여 주기만 해요. 원래 df의 행을 줄이지 않아요.': '실제 판다스 의미(head는 새 표를 돌려줌)를 정확히 말해요.'},
         reject=[([['print(df.shape)', 'print((4, 3))']], 'Typing the size'), ([['print(df.shape)', 'print(df.head(2).shape)']], 'Size of the head')],
         accept=[([['print(df.shape)', 'print((len(df), len(df.columns)))']], 'Counting rows and columns')]),
    dict(old='stp_8bef9af7-84ab-4006-9836-85dda69def1d', title='df["minutes"]로 배송시간 열을 꺼내세요',
         objectives=['열 이름 하나로 그 열의 값들을 골라요.'],
         core_flow='df["region"]은 지역 값이다. 열 이름을 "minutes"로 고쳐 [12, 18, 30, 42]를 확인한다. 채점은 열 순서와 값이 다른 자료로 실행한다.',
         goal='배송시간 네 개만 확인하려 해요. `df["열 이름"]`은 그 열의 값들을 골라요. `.tolist()`는 고른 값을 목록으로 보여 줘요.\n\n'
              'print 줄의 열 이름을 고쳐 배송시간 값들을 꺼내세요. 채점은 열 순서와 값이 다른 자료로도 실행해요.\n\n'
              + todo('코드 실행을 눌러 지역 값이 나오는지 확인하세요.', '열 이름 `"region"`을 `"minutes"`로 고치세요.', '코드 실행을 눌러 [12, 18, 30, 42]가 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s4, solution=s4_solution, tests=[{'input': '', 'expected': '[12, 18, 30, 42]'}],
         prepared_cases=py_cases(s4_solution, *OTHER_DICTS),
         narration=n4.actions,
         review={'조심하세요. df.head(1)은 첫 행 하나예요. 한 열의 값들을 고르는 것과 달라요.': '실제 의미를 정확히 대조해요.'},
         reject=[([['print(df["minutes"].tolist())', 'print([12, 18, 30, 42])']], 'Typing the list'), ([['print(df["minutes"].tolist())', 'print(df.iloc[:, 1].tolist())']], 'Second column by position breaks when the order changes')],
         accept=[([['print(df["minutes"].tolist())', 'print(df.minutes.tolist())']], 'Attribute access')]),
    dict(old='stp_1103f3b5-48c1-44fe-9b28-198c3ad26f10', title='read_csv의 파일 이름을 delivery.csv로 고치세요',
         objectives=['read_csv가 실행 폴더의 실제 파일을 읽어 표로 만드는 것을 확인해요.'],
         core_flow='read_csv("minutes.csv")는 FileNotFoundError다. 파일 이름을 delivery.csv로 고쳐 (4, 3)을 확인한다. 채점은 다른 배송 파일로 바꿔 기준 풀이의 결과와 비교한다.',
         goal='같은 자료를 파일로 받았어요. `read_csv`는 괄호 안 파일명을 실행 폴더에서 찾아 표로 읽어요. 제공된 파일 이름은 delivery.csv이고 첫 행은 열 이름이에요.\n\n'
              'read_csv 줄의 파일 이름을 고쳐 제공된 배송 파일을 읽으세요. 채점은 delivery.csv의 내용을 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 FileNotFoundError가 나오는지 확인하세요.', '`"minutes.csv"`를 `"delivery.csv"`로 고치세요.', '코드 실행을 눌러 (4, 3)이 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s5, solution=s5_solution, files={'delivery.csv': CSV}, tests=[{'input': '', 'expected': '(4, 3)'}],
         checker=file_variants_checker(s5_solution, OTHER_CSVS, CSV_MESSAGE),
         narration=n5.actions,
         review={'조심하세요. 열 이름 minutes는 파일 이름이 아니에요. 괄호 안에는 실제 파일 이름을 써요.': '실제 흔한 혼동을 정확히 말해요.'},
         reject=[([['print(df.shape)', 'print((4, 3))']], 'Typing the size')],
         accept=[([['df = pd.read_csv("delivery.csv")', 'from pathlib import Path\ndf = pd.read_csv(Path("delivery.csv"))']], 'A Path object')]),
    dict(old='stp_5e5384be-4ac4-4cd2-a5a3-ef57320adaf6', title='iloc[0]으로 첫 배송시간을 출력하세요',
         objectives=['iloc의 위치가 0부터 시작함을 써서 확인해요.'],
         core_flow='df["minutes"].iloc[1]은 두 번째 18이다. iloc[0]으로 고쳐 12를 확인한다. 채점은 다른 배송 파일로 기준 풀이와 비교한다.',
         goal='`iloc[위치]`는 위치로 항목을 골라요. 위치는 0부터 세어서 첫 항목은 `iloc[0]`이에요.\n\n'
              'print 줄의 위치를 고쳐 minutes 열의 첫 항목을 출력하세요. 채점은 delivery.csv의 내용을 바꿔서도 실행해요.\n\n'
              + todo('코드 실행을 눌러 18이 나오는지 확인하세요.', '`.iloc[1]`을 `.iloc[0]`으로 고치세요.', '코드 실행을 눌러 12가 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s6, solution=s6_solution, files={'delivery.csv': CSV}, tests=[{'input': '', 'expected': '12'}],
         checker=file_variants_checker(s6_solution, OTHER_CSVS, CSV_MESSAGE),
         narration=n6.actions,
         review={'조심하세요. iloc은 위치로, 인덱스 이름과 상관없이 고르는 방법이에요. 첫 위치는 0이에요.': '실제 판다스 의미를 정확히 말해요.'},
         reject=[([['print(df["minutes"].iloc[0])', 'print(12)']], 'Typing the value'), ([['.iloc[0]', '.iloc[1]']], 'Second item')],
         accept=[([['print(df["minutes"].iloc[0])', 'print(df["minutes"].head(1).item())']], 'One-item head')]),
    dict(old='stp_7644b2c6-aeb1-47da-a776-94ac3feb410f', title='df[["order_id", "minutes"]]로 두 열만 남기세요',
         objectives=['열 이름 목록으로 필요한 열들만 남긴 표를 만들어요.'],
         core_flow='small = df["minutes"]는 한 열뿐이다. df[["order_id", "minutes"]]로 고쳐 두 열 표를 확인한다. 채점은 열 순서가 다른 파일 등으로 기준 풀이와 비교한다.',
         goal='주문번호와 배송시간만 전달하려 해요. 대괄호 안에 열 이름 하나를 주면 한 열, 열 이름 목록을 주면 그 열들로 된 표가 돼요.\n\n'
              'small 줄을 고쳐 주문번호와 배송시간 두 열이 남은 표를 만드세요. 채점은 열 순서가 다른 파일로도 실행해요.\n\n'
              + todo('코드 실행을 눌러 한 열만 나오는지 확인하세요.', '`df["minutes"]`를 `df[["order_id", "minutes"]]`로 고치세요.', '코드 실행을 눌러 두 열이 남은 표를 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s7, solution=s7_solution, files={'delivery.csv': CSV},
         tests=[{'input': '', 'expected': '   order_id  minutes\n0       101       12\n1       102       18\n2       103       30\n3       104       42'}],
         checker=file_variants_checker(s7_solution, OTHER_CSVS, CSV_MESSAGE),
         narration=n7.actions,
         review={'조심하세요. 대괄호가 두 겹이에요. 바깥은 고르기, 안쪽은 열 이름 목록이에요.': '실제 판다스 문법을 정확히 말해요.'},
         reject=[([['small = df[["order_id", "minutes"]]', 'small = df.iloc[:, :2]']], 'First two columns by position'),
                 ([['small = df[["order_id", "minutes"]]', 'small = df[["minutes", "order_id"]]']], 'Columns in another order')],
         accept=[([['small = df[["order_id", "minutes"]]', 'small = df.loc[:, ["order_id", "minutes"]]']], 'loc with a column list')]),
    dict(old='stp_44f23f0c-39aa-4135-9a56-af6901ab9e8b', title='len(df)로 원래 표의 행 수를 세세요',
         objectives=['앞부분을 본 뒤에도 원래 표가 그대로임을 확인해요.'],
         core_flow='새 배송이 더해진 파일에서 len(df.head(2))는 2다. len(df)로 고쳐 5를 확인한다. 채점은 행 수가 다른 파일로 기준 풀이와 비교한다.',
         goal='배송 한 건이 더 들어왔어요. `head(2)`로 앞부분을 본 뒤에도 원래 표 df는 그대로예요. `len(표)`는 행 수예요.\n\n'
              'rows 줄을 고쳐 앞부분이 아니라 원래 표의 행 수를 담으세요. 채점은 행 수가 다른 파일로도 실행해요.\n\n'
              + todo('코드 실행을 눌러 2가 나오는지 확인하세요.', '`len(df.head(2))`를 `len(df)`로 고치세요.', '코드 실행을 눌러 5가 나오는지 확인하세요.', '수정한 코드를 제출하세요.'),
         starter_code=s8, solution=s8_solution, files={'delivery.csv': CSV5},
         tests=[{'input': '', 'expected': '   order_id  minutes region\n0       101       12     서울\n1       102       18     부산\n5'}],
         checker=file_variants_checker(s8_solution, OTHER_CSVS, CSV_MESSAGE),
         narration=n8.actions,
         review={'조심하세요. 파일이 바뀌면 행 수도 바뀌어요. 숫자를 적지 말고 표에서 세요.': '실제 채점(다른 파일)과 맞는 경고예요.'},
         reject=[([['rows = len(df)', 'rows = 5']], 'Typing the count'), ([['rows = len(df)', 'rows = len(df.columns)']], 'Column count')],
         accept=[([['rows = len(df)', 'rows = df.shape[0]']], 'shape[0]')]),
]
