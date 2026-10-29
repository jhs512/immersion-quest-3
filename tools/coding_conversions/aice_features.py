"""aice-features: 7 answer-picking steps -> coding steps (2026-10-29).

Each step edits one conversion (new unit column, astype, to_numeric coerce, map with unknown names,
get_dummies, dummy_na, to_datetime coerce) and is rerun with other prepared values, so typed results,
silently dropped rows and hidden conversion failures fail."""
from _kit import Script, code_step

OPENING = ['이 수업에서는 모델에 줄 입력을 직접 코드로 만들어요. 단위·범주·날짜 변환의 의미를 구별해요.',
           '자료를 바꾸며 실패한 값과 처음 보는 범주를 확인해요. 예측 시점에 알 수 있는 열만 골라요.']
PRD_SCOPE = ['두 챕터·두 단원·아홉 스텝으로 같은 배송표를 변환해요.',
             '새 단위 열·astype·to_numeric(coerce)·사전 map·get_dummies·dummy_na·to_datetime(coerce)를 한 곳씩 직접 고쳐 쓰고 입력 열 선택으로 이어 가요.']
PRD_GRADING = ['직접 고친 코드를 실제 파이썬·판다스로 실행해 판정해요. 실행·해설만으로 성공시키지 않아요.',
               '다른 거리·식별자·정답·범주 표에서 실제 입력 열과 행 값을 검사해요. 준비 값을 바꿔 다시 실행하고 기준 풀이의 실제 결과와 비교해요. 결과를 글자로 적은 답, 원래 열을 덮어쓴 답, 실패 행을 지운 답은 거절해요.',
               '마지막 도전(stp_dd7ffb3c-b10c-483d-a1a1-e7a41d7f5563): 실제 파이썬 출력과 다른 배송 자료 세 가지로 채점해요. 정답·식별자 포함, 실패를 nan으로 둔 소수 열, 실패 행 삭제는 실패해요.']
PRD_NARRATION = ['단위·변환 인자·선택열 한 곳씩 고쳐 실행해요.',
                 '원본 덮어쓰기·오류 억제·미지 범주·결측0표현·날짜 실패를 조심할 지점으로 짚어요.']

HEAD = ('import pandas as pd\n\n# 같은 배송의 원래 거리와 지역을 보관해요.\n'
        'data = {"id": [101, 102, 103, 104], "distance": [1, 2, 3, 4], "region": ["north", "south", "north", "south"], "minutes": [10, 20, 30, 40]}\n'
        'df = pd.DataFrame(data)\n')
OTHER = [{'data': {'id': [201, 202, 203], 'distance': [7, 0, 12], 'region': ['south', 'west', 'north'], 'minutes': [5, 9, 50]}},
         {'data': {'id': [301, 302], 'distance': [5, 3], 'region': ['north', 'north'], 'minutes': [15, 25]}}]
SUBMIT = '수정한 코드를 제출하세요.'
W = '실제 판다스 동작을 정확히 말해요.'

s1 = HEAD + '# 이 줄을 고쳐 원래 km 열은 두고 m 단위의 새 열 distance_m을 만드세요.\ndf["distance"] = df["distance"] * 1000\nprint(df["distance_m"].tolist())\nprint(df["distance"].tolist())\n'
s1_sol = s1.replace('df["distance"] = df["distance"] * 1000\n', '# 새 이름의 열에 담으면 원래 열은 그대로 남아요.\ndf["distance_m"] = df["distance"] * 1000\n')
n1 = (Script(s1)
      .say('거리 km를 m로 바꾼 새 열이 필요해요. 원래 열을 덮어쓰는 줄을 새 열에 담도록 고쳐야 해요.', 'text:df["distance"] 줄을 고쳐 원래 km 열은 두고 m 단위의 새 열 distance_m을 만드세요.')
      .run('print(df["distance_m"]', 'print(df["distance"]', error='KeyError')
      .say('KeyError예요. distance_m 열이 없고 원래 distance 열을 1000배로 덮어썼어요.', 'output')
      .patch('df["distance"] = df["distance"] * 1000\n', 'df["distance_m"] = df["distance"] * 1000\n', '왼쪽 열 이름을 "distance_m"으로 바꿔요.')
      .run('print(df["distance_m"]', 'print(df["distance"]')
      .say('[1000, 2000, 3000, 4000]과 [1, 2, 3, 4]예요. 새 m 열과 원래 km 열이 따로 있어요.', 'output')
      .say('조심하세요. 같은 이름에 대입하면 원래 값이 사라져요. 변환한 값은 새 열에 담아 비교해요.', 'code:df["distance_m"] = '))

s2 = (HEAD + '# 숫자 모양의 글자를 수치 계산에 쓰려 해요.\nminute_text = ["10", "20", "30", "40"]\ndf["minute_text"] = minute_text\n'
      '# 이 줄을 고쳐 글자 열을 정수로 바꾼 뒤 converted에 담으세요.\nconverted = df["minute_text"]\nprint((converted + 1).tolist())\nprint(df["minute_text"].tolist())\n')
s2_sol = s2.replace('converted = df["minute_text"]\n', '# astype("int64")는 글자 "10"을 정수 10으로 바꾼 새 열을 돌려줘요.\nconverted = df["minute_text"].astype("int64")\n')
n2 = (Script(s2)
      .say('글자 시간에 1을 더하려 해요. 먼저 글자 열을 정수로 바꿔 converted에 담아야 해요.', 'text:converted 줄을 고쳐 글자 열을 정수로 바꾼 뒤 converted에 담으세요.')
      .run('print((converted', 'print(df["minute_text"]', error='TypeError')
      .say('TypeError예요. 글자에 정수 1을 더할 수 없어요.', 'output')
      .patch('converted = df["minute_text"]\n', 'converted = df["minute_text"].astype("int64")\n', '뒤에 .astype("int64")를 붙여요.')
      .run('print((converted', 'print(df["minute_text"]')
      .say("[11, 21, 31, 41]이에요. 원래 열은 글자 ['10', '20', '30', '40'] 그대로예요.", 'output')
      .say('조심하세요. 글자끼리 더하면 "10" + "1"처럼 이어 붙여 "101"이 돼요. 계산 전에 자료형을 확인해요.', 'code:.astype("int64")'))

s3 = (HEAD + '# 한 글자가 수치로 바뀌지 않는 상황이에요.\nminute_text = ["10", "20", "bad", "40"]\ndf["minute_text"] = minute_text\n'
      '# 이 줄을 고쳐 바뀌지 않는 값은 결측으로 표시하며 숫자로 바꾸세요.\nconverted = df["minute_text"].astype("int64", errors="ignore")\n'
      'print(type(converted.iloc[0]).__name__)\nprint(converted.tolist())\nprint(int(converted.isna().sum()))\n')
s3_sol = s3.replace('converted = df["minute_text"].astype("int64", errors="ignore")', '# to_numeric(errors="coerce")는 바꿀 수 없는 값을 NaN으로 남겨 실패를 보이게 해요.\nconverted = pd.to_numeric(df["minute_text"], errors="coerce")')
n3 = (Script(s3)
      .say('bad는 숫자가 될 수 없어요. 오류를 숨기는 줄을 실패한 값이 결측으로 보이게 고쳐야 해요.', 'text:converted 줄을 고쳐 바뀌지 않는 값은 결측으로 표시하며 숫자로 바꾸세요.')
      .run('print(type(converted', 'print(int(converted')
      .say("str과 ['10', '20', 'bad', '40'], 결측 0이에요. 오류는 안 났지만 글자 원본이 그대로 남았어요.", 'output')
      .patch('converted = df["minute_text"].astype("int64", errors="ignore")', 'converted = pd.to_numeric(df["minute_text"], errors="coerce")', 'pd.to_numeric(..., errors="coerce")로 바꿔요.')
      .run('print(type(converted', 'print(int(converted')
      .say('float64와 [10.0, 20.0, nan, 40.0], 결측 1이에요. bad 자리가 결측으로 드러났어요.', 'output')
      .say('조심하세요. 오류가 안 났다고 변환이 성공한 건 아니에요. 결측 수로 실패를 확인해요.', 'code:errors="coerce"'))

s4 = (HEAD + '# 사전에 없는 지역 이름 하나가 들어왔어요.\nregions = ["north", "south", "west", "north"]\ndf["region"] = regions\nmapping = {"north": 0, "south": 1}\n'
      '# 이 줄을 고쳐 사전에 없는 이름의 행도 결측으로 남기세요.\nencoded = df["region"].map(mapping).dropna()\nprint(encoded.isna().tolist())\nprint(len(encoded))\n')
s4_sol = s4.replace('encoded = df["region"].map(mapping).dropna()', '# map은 사전에 없는 이름을 NaN으로 바꿔요. 행을 지우지 않고 그대로 둬요.\nencoded = df["region"].map(mapping)')
n4 = (Script(s4)
      .say('사전에는 north와 south만 있어요. 사전에 없는 west의 행도 결측으로 남기도록 고쳐야 해요.', 'text:encoded 줄을 고쳐 사전에 없는 이름의 행도 결측으로 남기세요.')
      .run('print(encoded.isna', 'print(len(encoded))')
      .say('결측이 없고 길이 3이에요. dropna가 west 행을 지웠어요.', 'output')
      .patch('df["region"].map(mapping).dropna()', 'df["region"].map(mapping)', '뒤의 .dropna()를 지워요.')
      .run('print(encoded.isna', 'print(len(encoded))')
      .say('[False, False, True, False]와 4예요. west 자리가 결측으로 남고 행은 그대로예요.', 'output')
      .say('조심하세요. 처음 보는 이름을 조용히 지우면 그 배송이 분석에서 사라져요. 결측 수를 먼저 확인해요.', 'code:map(mapping)'))

s5 = (HEAD + '# 이 줄을 고쳐 지역마다 해당하면 1인 표시 열을 만드세요.\nencoded = df[["region"]]\nprint(encoded.columns.tolist())\nprint(encoded.values.tolist())\n')
s5_sol = s5.replace('encoded = df[["region"]]', '# get_dummies는 범주마다 열을 만들고 그 범주에 해당하면 1, 아니면 0을 적어요.\nencoded = pd.get_dummies(df["region"], dtype=int)')
n5 = (Script(s5)
      .say('지역 글자를 모델이 쓰는 숫자로 바꾸려 해요. 지역마다 해당 여부를 표시하는 열로 고쳐야 해요.', 'text:encoded 줄을 고쳐 지역마다 해당하면 1인 표시 열을 만드세요.')
      .run('print(encoded.columns', 'print(encoded.values')
      .say("['region']과 지역 글자 네 개예요. 아직 글자 한 열이에요.", 'output')
      .patch('encoded = df[["region"]]', 'encoded = pd.get_dummies(df["region"], dtype=int)', 'pd.get_dummies(df["region"], dtype=int)로 바꿔요.')
      .run('print(encoded.columns', 'print(encoded.values')
      .say("['north', 'south'] 두 열과 [1, 0], [0, 1]이 번갈아 나와요. 1은 그 지역에 해당한다는 표시예요.", 'output')
      .say('조심하세요. 표시 열의 1과 0은 크기나 순위가 아니에요. 해당하는지 여부만 뜻해요.', 'code:pd.get_dummies'))

s6 = (HEAD + '# 결측과 기준 범주가 같은 표시가 되는지 확인해요.\nregions = ["north", "south", None, "north"]\ndf["region"] = regions\n'
      '# 이 줄의 옵션을 고쳐 결측을 따로 표시하는 열도 만드세요.\nencoded = pd.get_dummies(df["region"], drop_first=True, dummy_na=False, dtype=int)\n'
      'print(encoded.columns.tolist())\nprint(encoded.values.tolist())\n')
s6_sol = s6.replace('dummy_na=False, dtype=int)', 'dummy_na=True, dtype=int)').replace('# 이 줄의 옵션을 고쳐 결측을 따로 표시하는 열도 만드세요.\n',
                                                                                 '# 이 줄의 옵션을 고쳐 결측을 따로 표시하는 열도 만드세요.\n# dummy_na=True면 결측 열이 생겨 기준 범주 north와 결측이 다른 표시가 돼요.\n')
n6 = (Script(s6)
      .say('첫 범주 열을 줄였어요. 결측이 기준 범주와 같은 0으로 보이지 않게 옵션을 고쳐야 해요.', 'text:encoded 줄의 옵션을 고쳐 결측을 따로 표시하는 열도 만드세요.')
      .run('print(encoded.columns', 'print(encoded.values')
      .say("['south'] 한 열과 [0], [1], [0], [0]이에요. north와 결측이 모두 0이라 구별할 수 없어요.", 'output')
      .patch('dummy_na=False', 'dummy_na=True', 'dummy_na를 True로 바꿔요.')
      .run('print(encoded.columns', 'print(encoded.values')
      .say('south와 결측 열 두 개예요. 셋째 행만 결측 열이 1이라 north와 구별돼요.', 'output')
      .say('조심하세요. drop_first를 쓰면 모든 열이 0인 행이 기준 범주예요. 결측도 같은 모양이 되지 않게 확인해요.', 'code:dummy_na=True'))

s7 = (HEAD + '# 요일은 월요일 0부터 일요일 6까지예요.\nplanned = ["2024-01-01", "2024-01-02", "bad", "2024-01-07"]\ndf["planned"] = planned\n'
      '# 이 줄의 옵션을 고쳐 날짜가 아닌 값은 결측으로 남기며 변환하세요.\nparsed = pd.to_datetime(df["planned"], format="%Y-%m-%d", errors="raise")\n'
      '# -1은 화면에서 결측을 구별할 표시용 값이에요.\nprint(parsed.dt.dayofweek.fillna(-1).astype("int64").tolist())\nprint(len(parsed))\n')
s7_sol = s7.replace('errors="raise")', 'errors="coerce")').replace('# 이 줄의 옵션을 고쳐 날짜가 아닌 값은 결측으로 남기며 변환하세요.\n',
                                                              '# 이 줄의 옵션을 고쳐 날짜가 아닌 값은 결측으로 남기며 변환하세요.\n# errors="coerce"는 바꿀 수 없는 값을 날짜 결측 NaT로 남기고 행은 그대로 둬요.\n')
n7 = (Script(s7)
      .say('날짜로 바꿀 수 없는 bad가 있어요. 변환을 멈추지 않고 결측으로 남기도록 옵션을 고쳐야 해요.', 'text:parsed 줄의 옵션을 고쳐 날짜가 아닌 값은 결측으로 남기며 변환하세요.')
      .run('print(parsed.dt', 'print(len(parsed))', error='ValueError')
      .say('ValueError예요. errors="raise"는 bad에서 변환을 멈춰요.', 'output')
      .patch('errors="raise"', 'errors="coerce"', 'errors를 "coerce"로 바꿔요.')
      .run('print(parsed.dt', 'print(len(parsed))')
      .say('[0, 1, -1, 6]과 4예요. 월요일, 화요일, 결측, 일요일이고 네 행이 그대로예요.', 'output')
      .say('조심하세요. coerce는 실패를 지우지 않고 결측으로 남겨요. 결측 수를 세어 실패를 확인해요.', 'code:errors="coerce"'))

SPECS = [
    code_step('stp_c8bc3b3d-5a2d-4a9c-b351-f020717e5b98', 'distance_m 새 열에 m 단위를 담으세요', '변환한 값을 새 열에 담아 원래 열을 보존해요.',
              'df["distance"]에 대입하면 원래 km 열을 덮어쓰고 distance_m이 없어 KeyError다. df["distance_m"]에 담아 새 m 열과 원래 km 열을 확인한다. 채점은 다른 거리로 실행한다.',
              '거리 km를 m로 바꾼 열이 필요해요. `df["새 열"] = 계산식`은 새 열을 만들고, 이미 있는 열 이름에 대입하면 그 열의 값을 덮어써요.',
              'df["distance"] 줄을 고쳐 원래 km 열은 두고 m 단위의 새 열 distance_m을 만드세요. 채점은 다른 거리로도 실행해요.',
              ['코드 실행을 눌러 KeyError가 나오는지 확인하세요.', '왼쪽의 `df["distance"]`를 `df["distance_m"]`으로 고치세요.', '코드 실행을 눌러 새 열과 원래 열을 비교하세요.', SUBMIT],
              s1, s1_sol, n1, {n1.actions[-1]['text']: W}, cases=OTHER,
              reject=[([['df["distance_m"] = df["distance"] * 1000\n', 'df["distance"] = df["distance"] * 1000\ndf["distance_m"] = df["distance"]\n']], 'Overwriting the original'),
                      ([['df["distance_m"] = df["distance"] * 1000\n', 'df["distance_m"] = [1000, 2000, 3000, 4000]\n']], 'Typing the meters')],
              accept=[([['df["distance_m"] = df["distance"] * 1000\n', 'df = df.assign(distance_m=df["distance"] * 1000)\n']], 'assign')]),
    code_step('stp_0fe50a13-3ac6-4ab5-b596-cb7046491e5b', 'astype("int64")로 글자 시간을 정수로 바꾸세요', '숫자 모양의 글자를 계산 전에 정수로 바꿔요.',
              '글자 열에 1을 더하면 TypeError다. astype("int64")로 바꿔 [11, 21, 31, 41]과 그대로인 원래 글자 열을 확인한다. 채점은 다른 글자 시간으로 실행한다.',
              '글자 "10"은 숫자 모양이지만 글자예요. `astype("int64")`는 열을 정수로 바꾼 새 열을 돌려줘요. 원래 열은 그대로예요.',
              'converted 줄을 고쳐 글자 열을 정수로 바꾼 뒤 converted에 담으세요. 채점은 다른 글자 시간으로도 실행해요.',
              ['코드 실행을 눌러 TypeError가 나오는지 확인하세요.', '`df["minute_text"]` 뒤에 `.astype("int64")`를 붙이세요.', '코드 실행을 눌러 1을 더한 결과를 확인하세요.', SUBMIT],
              s2, s2_sol, n2, {n2.actions[-1]['text']: '실제 문자열 덧셈 동작을 정확히 말해요.'},
              cases=[{'minute_text': ['5', '7', '99', '0']}, {'minute_text': ['12', '3', '40', '8']}],
              reject=[([['converted = df["minute_text"].astype("int64")\n', 'converted = pd.Series([10, 20, 30, 40])\n']], 'Typing the numbers')],
              accept=[([['converted = df["minute_text"].astype("int64")\n', 'converted = pd.to_numeric(df["minute_text"])\n']], 'to_numeric')]),
    code_step('stp_46543cf8-acbc-4a44-b27e-970372b682e3', 'to_numeric(errors="coerce")로 실패를 결측으로 드러내세요', '변환 실패를 숨기지 않고 결측으로 확인해요.',
              'astype(errors="ignore")는 오류 없이 글자 원본을 그대로 둔다. pd.to_numeric(errors="coerce")로 고쳐 bad가 NaN이 되고 결측 1을 확인한다. 채점은 실패 위치·수가 다른 자료로 실행한다.',
              '변환 오류를 ignore로 숨겼어요. 오류가 안 나도 값이 바뀌었는지는 따로 확인해야 해요. `pd.to_numeric(열, errors="coerce")`는 바꿀 수 없는 값을 결측(NaN)으로 남겨요.',
              'converted 줄을 고쳐 바뀌지 않는 값은 결측으로 표시하며 숫자로 바꾸세요. 채점은 다른 자료로도 실행해요.',
              ['코드 실행을 눌러 자료형과 값을 확인하세요.', '`df["minute_text"].astype("int64", errors="ignore")`를 `pd.to_numeric(df["minute_text"], errors="coerce")`로 고치세요.', '코드 실행을 눌러 결측 수를 확인하세요.', SUBMIT],
              s3, s3_sol, n3, {n3.actions[-1]['text']: W, n3.actions[2]['text']: '실제 ignore 결과(글자 원본, 결측 0)를 정확히 말해요.'},
              cases=[{'minute_text': ['x', '8', 'y', '1']}, {'minute_text': ['3', '4', '5', '6']}],
              reject=[([['converted = pd.to_numeric(df["minute_text"], errors="coerce")', 'converted = df["minute_text"].astype("int64", errors="ignore")']], 'Hidden failure'),
                      ([['converted = pd.to_numeric(df["minute_text"], errors="coerce")', 'converted = pd.to_numeric(df["minute_text"], errors="coerce").dropna()']], 'Dropping the failures')],
              accept=[([['converted = pd.to_numeric(df["minute_text"], errors="coerce")', 'converted = pd.to_numeric(df["minute_text"].where(df["minute_text"].str.isdigit()))']], 'Keeping only digit text')]),
    code_step('stp_497bb535-83c6-447f-a6e6-56041c85e5ba', 'map 결과에서 dropna를 지워 모든 행을 남기세요', '사전에 없는 범주가 결측이 되고 행은 남는 것을 확인해요.',
              'map(mapping).dropna()는 west 행을 지워 길이 3이다. dropna를 지워 west 자리가 결측인 길이 4를 확인한다. 채점은 다른 지역 목록으로 실행한다.',
              '사전에는 north와 south만 있어요. `map(사전)`은 사전에 있는 이름을 그 값으로 바꾸고, 없는 이름은 결측(NaN)으로 둬요. `dropna()`는 결측 행을 지워요.',
              'encoded 줄을 고쳐 사전에 없는 이름의 행도 결측으로 남기세요. 채점은 다른 지역 목록으로도 실행해요.',
              ['코드 실행을 눌러 길이가 3인지 확인하세요.', '`.map(mapping)` 뒤의 `.dropna()`를 지우세요.', '코드 실행을 눌러 결측 위치와 길이를 확인하세요.', SUBMIT],
              s4, s4_sol, n4, {n4.actions[-1]['text']: '실제 분석 위험(행 손실)을 정확히 말해요.'},
              cases=[{'regions': ['east', 'east', 'south', 'north']}, {'regions': ['south', 'north', 'north', 'south']}],
              reject=[([['encoded = df["region"].map(mapping)', 'encoded = df["region"].map(mapping).dropna()']], 'Dropping unknown names'),
                      ([['encoded = df["region"].map(mapping)', 'encoded = df["region"].map(mapping).fillna(0)']], 'Unknown as north')],
              accept=[([['encoded = df["region"].map(mapping)', 'encoded = df["region"].map(lambda name: mapping.get(name))']], 'dict.get per name')]),
    code_step('stp_a09b00ec-aef9-4858-8da0-d5452ecd52e4', 'get_dummies로 지역마다 표시 열을 만드세요', '범주마다 해당 여부를 1/0으로 표시하는 열을 만들어요.',
              'df[["region"]]은 글자 한 열이다. pd.get_dummies(df["region"], dtype=int)로 고쳐 north·south 열과 1/0 표시를 확인한다. 채점은 범주 수가 다른 자료로 실행한다.',
              '지역 글자를 모델이 쓰는 숫자로 바꿔요. `pd.get_dummies(열, dtype=int)`는 범주마다 열을 만들고 그 범주에 해당하면 1, 아니면 0을 적어요.',
              'encoded 줄을 고쳐 지역마다 해당하면 1인 표시 열을 만드세요. 채점은 범주가 다른 자료로도 실행해요.',
              ['코드 실행을 눌러 글자 한 열인지 확인하세요.', '`df[["region"]]`을 `pd.get_dummies(df["region"], dtype=int)`로 고치세요.', '코드 실행을 눌러 표시 열을 확인하세요.', SUBMIT],
              s5, s5_sol, n5, {n5.actions[-1]['text']: '실제 원-핫 표시의 의미를 정확히 말해요.'}, cases=OTHER,
              reject=[([['encoded = pd.get_dummies(df["region"], dtype=int)', 'encoded = df[["region"]].replace({"north": 0, "south": 1})']], 'One column of codes'),
                      ([['encoded = pd.get_dummies(df["region"], dtype=int)', 'encoded = pd.get_dummies(df["region"], drop_first=True, dtype=int)']], 'Dropping the first region')],
              accept=[([['encoded = pd.get_dummies(df["region"], dtype=int)', 'encoded = pd.crosstab(df.index, df["region"])']], 'crosstab of row and region')]),
    code_step('stp_6083b3b4-81ce-4a82-a9de-9bf182d3e6a3', 'dummy_na=True로 결측을 기준 범주와 구별하세요', '기준 범주를 줄인 표시에서 결측이 따로 보이게 해요.',
              'drop_first=True, dummy_na=False는 north와 결측을 모두 [0]으로 만든다. dummy_na=True로 고쳐 결측 열이 생기고 셋째 행만 1임을 확인한다. 채점은 다른 지역 목록으로 실행한다.',
              '첫 범주 열을 줄였어요(`drop_first=True`). 그러면 모든 표시가 0인 행이 기준 범주 north예요. 결측 표시를 끄면(`dummy_na=False`) 결측도 같은 0으로 보여요.',
              'encoded 줄의 옵션을 고쳐 결측을 따로 표시하는 열도 만드세요. 채점은 다른 지역 목록으로도 실행해요.',
              ['코드 실행을 눌러 north와 결측의 표시를 비교하세요.', '`dummy_na=False`를 `dummy_na=True`로 고치세요.', '코드 실행을 눌러 결측 열을 확인하세요.', SUBMIT],
              s6, s6_sol, n6, {n6.actions[-1]['text']: W},
              cases=[{'regions': [None, None, 'south', 'north']}, {'regions': ['north', 'east', 'south', None]}],
              reject=[([['dummy_na=True, dtype=int)', 'dummy_na=False, dtype=int)']], 'Missing looks like north'),
                      ([['encoded = pd.get_dummies(df["region"], drop_first=True, dummy_na=True, dtype=int)', 'encoded = pd.get_dummies(df["region"].fillna("north"), drop_first=True, dtype=int)']], 'Filling missing as north')],
              accept=[([['encoded = pd.get_dummies(df["region"], drop_first=True, dummy_na=True, dtype=int)', 'encoded = pd.get_dummies(df["region"], dummy_na=True, dtype=int).iloc[:, 1:]']], 'Dropping the first column afterwards')]),
    code_step('stp_f9dcd6ab-8631-4bdf-980b-8e7af27b666d', 'to_datetime(errors="coerce")로 실패를 결측으로 남기세요', '날짜로 바꿀 수 없는 값을 결측으로 남기고 행을 유지해요.',
              'errors="raise"는 bad에서 ValueError다. errors="coerce"로 고쳐 요일 [0, 1, -1, 6]과 네 행을 확인한다. 채점은 다른 날짜 목록으로 실행한다.',
              '날짜로 바꿀 수 없는 bad가 있어요. `pd.to_datetime(열, format=..., errors=...)`에서 `errors="raise"`는 실패하면 멈추고, `errors="coerce"`는 실패한 값을 날짜 결측 NaT로 남겨요.',
              'parsed 줄의 옵션을 고쳐 날짜가 아닌 값은 결측으로 남기며 변환하세요. 채점은 다른 날짜 목록으로도 실행해요.',
              ['코드 실행을 눌러 ValueError가 나오는지 확인하세요.', '`errors="raise"`를 `errors="coerce"`로 고치세요.', '코드 실행을 눌러 요일과 행 수를 확인하세요.', SUBMIT],
              s7, s7_sol, n7, {n7.actions[-1]['text']: W},
              cases=[{'planned': ['2024-02-29', 'oops', 'later', '2024-03-03']}, {'planned': ['2023-12-25', '2024-01-05', '2024-01-06', '2024-01-08']}],
              reject=[([['print(parsed.dt.dayofweek.fillna(-1).astype("int64").tolist())', 'print([0, 1, -1, 6])']], 'Typing the weekdays'),
                      ([['parsed = pd.to_datetime(df["planned"], format="%Y-%m-%d", errors="coerce")', 'parsed = pd.to_datetime(df["planned"], format="%Y-%m-%d", errors="coerce").dropna()']], 'Dropping failed dates')],
              accept=[([['parsed = pd.to_datetime(df["planned"], format="%Y-%m-%d", errors="coerce")', 'parsed = pd.to_datetime(df["planned"].where(df["planned"].str.match(r"\\d{4}-\\d{2}-\\d{2}$")), format="%Y-%m-%d")']], 'Blanking non-dates first')]),
]
