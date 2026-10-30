"""aice-leakage: 7 answer-picking steps -> coding steps (2026-10-29).

Each step removes one leak in real code: the target or a future column in the inputs, a reference
statistic computed with held-out rows, a split that puts one customer on both sides. Prepared cases rerun
with other tables (other extra columns, values, customers and days), so typed column lists or numbers and
the leaking starter fail."""
from _kit import Script, code_step

OPENING = ['이 수업에서는 평가에 쓰면 안 되는 정보가 섞이는 문제를 직접 코드로 고쳐요. 예측 시점과 훈련 경계를 지켜요.',
           '정답·미래 정보·평가 통계가 섞인 예를 살펴봐요. 그룹과 시간을 고려해 분리 기준을 직접 고쳐요.']
PRD_SCOPE = ['두 챕터·두 단원·아홉 스텝으로 같은 배송 평가를 다뤄요.',
             '정답/미래 열 빼기·훈련만의 평균과 중앙값·고객 단위 분리·GroupShuffleSplit·과거만의 기준을 한 곳씩 직접 고쳐 쓰고 연결해요.']
PRD_GRADING = ['직접 고친 코드를 실제 파이썬·판다스·scikit-learn으로 실행해 판정해요. 실행·해설만으로 성공시키지 않아요.',
               '훈련값이하나이상있는다른자료와평가극단값에서채움기준을검사해요. 열·값·고객·날짜가 다른 준비 자료로 다시 실행해 기준 풀이와 비교하고, 열 목록이나 숫자를 글자로 적은 답은 거절해요.',
               '행 교집합·그룹 교집합·시간 범위는 다른 조건으로 확인해요.',
               '마지막 도전(stp_aea6a5c7-61a8-48bd-b46f-891d15963afb): 실제 Python 실행과 다른 준비 자료의 결과를 검사해요. 시작 코드는 실패하고 동등한 풀이도 통과해야 해요.']
PRD_NARRATION = ['입력·통계 기준·분리 단위 한 곳씩 고치고 실제 값을 비교해요.',
                 '이름만다른미래열·전체전처리·행과개체·미래기준추정을 조심할 지점으로 짚어요.']

SUBMIT = '수정한 코드를 제출하세요.'
W = '실제 판다스 동작과 누수 위험을 정확히 말해요.'
HEAD = ('import pandas as pd\n\n# 같은 배송을 접수 시점에서 예측하려 해요. minutes는 아직 모르는 정답이에요.\n'
        'data = {"distance": [1, 2, 3], "region": ["north", "south", "north"], "minutes": [10, 20, 100]}\ndf = pd.DataFrame(data)\n')
TABLES = [{'data': {'distance': [4, 1], 'weight': [2.5, 0.5], 'region': ['east', 'west'], 'minutes': [30, 8]}},
          {'data': {'minutes': [12, 15, 9, 40], 'distance': [2, 2, 1, 6], 'floor': [1, 3, 2, 5]}}]

s1 = HEAD + '# 이 줄을 고쳐 정답 열 minutes를 뺀 나머지 열을 입력으로 쓰세요.\nX = df\nprint(X.columns.tolist())\nprint(X.shape)\n'
s1_sol = s1.replace('X = df\n', '# drop(columns=...)은 그 열만 뺀 새 표를 돌려줘요. 맞힐 정답은 입력에 넣지 않아요.\nX = df.drop(columns=["minutes"])\n')
n1 = (Script(s1)
      .say('접수 때 minutes는 아직 모르는 정답이에요. 입력 X에서 정답 열을 빼도록 고쳐야 해요.', 'text:X 줄을 고쳐 정답 열 minutes를 뺀 나머지 열을 입력으로 쓰세요.')
      .run('print(X.columns', 'print(X.shape)')
      .say("['distance', 'region', 'minutes']과 (3, 3)이에요. 맞힐 정답이 입력에 섞였어요.", 'output')
      .patch('X = df\n', 'X = df.drop(columns=["minutes"])\n', 'df.drop(columns=["minutes"])로 정답 열을 빼요.')
      .run('print(X.columns', 'print(X.shape)')
      .say("['distance', 'region']과 (3, 2)예요. 접수 때 아는 두 열만 남았어요.", 'output')
      .say('조심하세요. 정답이 입력에 있으면 평가 점수가 아주 좋아 보여도 실제 예측에는 쓸 수 없어요.', 'code:drop(columns=["minutes"])'))

s2 = (HEAD + '# 완료 시각은 배송이 끝난 뒤에만 알 수 있어요.\ndelivered = ["10:10", "10:20", "11:40"]\ndf["delivered_at"] = delivered\n'
      '# 이 줄을 고쳐 정답과 완료 시각을 모두 뺀 열을 입력으로 쓰세요.\nX = df.drop(columns=["minutes"])\nprint(X.columns.tolist())\n')
s2_sol = s2.replace('X = df.drop(columns=["minutes"])', '# 열 이름이 정답과 달라도 예측 시점에 모르는 미래 정보면 함께 빼요.\nX = df.drop(columns=["minutes", "delivered_at"])')
n2 = (Script(s2)
      .say('minutes는 뺐지만 완료 시각이 남았어요. 완료 시각도 빼도록 고쳐야 해요.', 'text:X 줄을 고쳐 정답과 완료 시각을 모두 뺀 열을 입력으로 쓰세요.')
      .run('print(X.columns')
      .say("['distance', 'region', 'delivered_at']이에요. 배송이 끝난 뒤에야 아는 열이 남았어요.", 'output')
      .patch('df.drop(columns=["minutes"])', 'df.drop(columns=["minutes", "delivered_at"])', '빼는 목록에 "delivered_at"을 더해요.')
      .run('print(X.columns')
      .say("['distance', 'region']이에요. 접수 시점에 아는 열만 남았어요.", 'output')
      .say('조심하세요. 정답과 이름이 달라도 정답을 거의 알려 주는 미래 정보예요. 언제 아는 값인지로 판단해요.', 'code:["minutes", "delivered_at"]'))

SER = ('import pandas as pd\n\n# 앞의 관측은 훈련, 뒤의 값은 평가용이에요.\ntrain_values = [10, 20]\ntest_values = [100]\n'
       'train = pd.Series(train_values)\ntest = pd.Series(test_values)\n')
SER_CASES = [{'train_values': [4, 8, 6], 'test_values': [1000, 2]}, {'train_values': [30], 'test_values': [5]}]
s3 = SER + '# 이 줄을 고쳐 평가 값을 빼고 훈련 값만으로 기준 평균을 구하세요.\nreference = pd.concat([train, test]).mean()\nprint(round(float(reference), 3))\n'
s3_sol = s3.replace('reference = pd.concat([train, test]).mean()', '# 기준은 훈련에서만 배워요. 남겨 둔 평가 값이 기준을 바꾸면 안 돼요.\nreference = train.mean()')
n3 = (Script(s3)
      .say('남겨 둔 평가 값이 기준에 섞였어요. 훈련 값만으로 평균을 구하도록 고쳐야 해요.', 'text:reference 줄을 고쳐 평가 값을 빼고 훈련 값만으로 기준 평균을 구하세요.')
      .run('print(round')
      .say('43.333이에요. 평가의 100이 기준 평균을 끌어올렸어요.', 'output')
      .patch('pd.concat([train, test]).mean()', 'train.mean()', 'train.mean()으로 바꿔요.')
      .run('print(round')
      .say('15.0이에요. 훈련 값 10과 20만의 평균이라 평가 값이 바뀌어도 그대로예요.', 'output')
      .say('조심하세요. 전체로 만든 기준은 평가 자료가 바뀔 때마다 함께 바뀌어요.', 'code:train.mean()'))

s4 = (SER.replace('test_values = [100]', 'test_values = [None, 100]') + '# 이 줄을 고쳐 평가가 아니라 훈련에서 채움 기준을 정하세요.\nreference = test.median()\n'
      'print(float(reference))\nprint(test.fillna(reference).tolist())\n')
s4_sol = s4.replace('reference = test.median()', '# 채움 값도 훈련에서 배운 기준이에요. 평가에는 그 값을 적용만 해요.\nreference = train.median()')
n4 = (Script(s4)
      .say('평가 자료의 빈값을 채우려 해요. 채움 기준을 훈련에서 정하도록 고쳐야 해요.', 'text:reference 줄을 고쳐 평가가 아니라 훈련에서 채움 기준을 정하세요.')
      .run('print(float', 'print(test.fillna')
      .say('100.0과 [100.0, 100.0]이에요. 평가에서 기준을 다시 배웠어요.', 'output')
      .patch('reference = test.median()', 'reference = train.median()', 'test를 train으로 바꿔요.')
      .run('print(float', 'print(test.fillna')
      .say('15.0과 [15.0, 100.0]이에요. 훈련에서 정한 15로 채웠어요.', 'output')
      .say('조심하세요. 평가의 중앙값으로 채우면 평가 정보가 기준에 섞여요.', 'code:train.median()'))

s5 = ('import pandas as pd\n\n# 새 고객의 배송을 평가하는 게 목표예요.\ndata = {"customer": ["A", "A", "B", "B"], "minutes": [10, 12, 20, 22]}\ndf = pd.DataFrame(data)\n'
      'test_customers = ["B"]\n# 이 두 줄을 고쳐 test_customers의 고객 행은 모두 평가로, 나머지 고객 행은 훈련으로 나누세요.\n'
      'train = df.iloc[0::2]\ntest = df.iloc[1::2]\n'
      '# 확인용 출력: 두 쪽에 같은 고객이 있으면 True예요.\nprint(bool(set(train["customer"]) & set(test["customer"])))\nprint(train["minutes"].tolist(), test["minutes"].tolist())\n')
s5_sol = s5.replace('train = df.iloc[0::2]\ntest = df.iloc[1::2]\n', '# isin은 고객이 목록에 있는지 확인해요. 같은 고객의 행은 모두 한쪽으로 가요.\ntrain = df[~df["customer"].isin(test_customers)]\ntest = df[df["customer"].isin(test_customers)]\n')
n5 = (Script(s5)
      .say('행은 겹치지 않지만 고객 A와 B가 양쪽에 있어요. 고객 단위로 나누도록 두 줄을 고쳐야 해요.', 'text:두 줄을 고쳐 test_customers의 고객 행은 모두 평가로, 나머지 고객 행은 훈련으로 나누세요.')
      .run('print(bool', 'print(train["minutes"]')
      .say('True예요. 행을 번갈아 나눠 두 고객이 훈련과 평가에 모두 있어요.', 'output')
      .patch('train = df.iloc[0::2]\ntest = df.iloc[1::2]\n', 'train = df[~df["customer"].isin(test_customers)]\ntest = df[df["customer"].isin(test_customers)]\n', 'isin으로 평가 고객과 나머지 고객을 나눠요.')
      .run('print(bool', 'print(train["minutes"]')
      .say('False와 [10, 12] [20, 22]예요. 고객 A는 훈련, 고객 B는 평가에만 있어요.', 'output')
      .say('조심하세요. 행이 겹치지 않아도 같은 고객이 양쪽에 있으면 새 고객 평가가 아니에요.', 'code:~df["customer"].isin(test_customers)'))

s6 = ('from sklearn.model_selection import ShuffleSplit, GroupShuffleSplit\n\n# 고객마다 두 관측씩 있고 고객 하나를 평가에 남겨요.\n'
      'groups = ["A", "A", "B", "B", "C", "C"]\nrows = list(range(len(groups)))\n'
      '# 이 줄을 고쳐 행이 아니라 고객 그룹 하나를 평가로 남기세요.\ntrain, test = next(ShuffleSplit(n_splits=1, test_size=2, random_state=0).split(rows))\n'
      '# 확인용 출력: 평가 행 수, 평가 고객 수, 양쪽에 같은 고객이 있는지예요.\nprint(len(test), len({groups[i] for i in test}))\nprint(bool({groups[i] for i in train} & {groups[i] for i in test}))\n')
s6_sol = s6.replace('train, test = next(ShuffleSplit(n_splits=1, test_size=2, random_state=0).split(rows))',
                    '# GroupShuffleSplit의 test_size=1은 그룹 하나예요. groups로 같은 고객의 행을 함께 옮겨요.\ntrain, test = next(GroupShuffleSplit(n_splits=1, test_size=1, random_state=0).split(rows, groups=groups))')
n6 = (Script(s6)
      .say('새 고객 평가는 고객 그룹을 나눠요. 행을 섞는 줄을 그룹 단위 분리로 고쳐야 해요.', 'text:train 줄을 고쳐 행이 아니라 고객 그룹 하나를 평가로 남기세요.')
      .run('print(len(test)', 'print(bool')
      .say('2 2와 True예요. 평가 두 행이 서로 다른 고객이고 그 고객들이 훈련에도 있어요.', 'output')
      .patch('next(ShuffleSplit(n_splits=1, test_size=2, random_state=0).split(rows))', 'next(GroupShuffleSplit(n_splits=1, test_size=1, random_state=0).split(rows, groups=groups))',
             'GroupShuffleSplit에 test_size=1을 주고 split에 groups를 넘겨요.')
      .run('print(len(test)', 'print(bool')
      .say('2 1과 False예요. 고객 하나의 두 행이 모두 평가로 갔어요.', 'output')
      .say('조심하세요. 그룹 분리의 test_size=1은 행 하나가 아니라 그룹 하나예요.', 'code:test_size=1'))

s7 = (HEAD + '# 날짜 2까지 알 수 있는 자료로 기준을 정해요. 날짜 3은 미래 평가 관측이에요.\ndays = [1, 2, 3]\ndf["day"] = days\ntrain = df[df["day"] <= 2]\n'
      '# 이 줄을 고쳐 미래 관측을 빼고 과거 훈련 자료의 평균 시간을 기준으로 쓰세요.\nreference = df["minutes"].mean()\nprint(round(float(reference), 3))\n')
s7_sol = s7.replace('reference = df["minutes"].mean()', '# 기준은 그 시점까지 알 수 있는 훈련 행에서만 계산해요.\nreference = train["minutes"].mean()')
n7 = (Script(s7)
      .say('날짜 3은 미래 평가 관측이에요. 날짜 2까지의 훈련 자료로만 평균을 내도록 고쳐야 해요.', 'text:reference 줄을 고쳐 미래 관측을 빼고 과거 훈련 자료의 평균 시간을 기준으로 쓰세요.')
      .run('print(round')
      .say('43.333이에요. 미래 관측 100이 기준에 섞였어요.', 'output')
      .patch('df["minutes"].mean()', 'train["minutes"].mean()', 'df를 train으로 바꿔요.')
      .run('print(round')
      .say('15.0이에요. 날짜 1과 2의 10과 20만 평균 냈어요.', 'output')
      .say('조심하세요. 날짜순으로 정렬했다고 미래 값이 기준에서 빠지지는 않아요. 시점으로 행을 걸러요.', 'code:train["minutes"].mean()'))
# Rows are not in day order: a future day comes first, and the past has three rows, so taking the first
# rows instead of filtering by day gives a different reference.
DAY_CASES = [{'data': {'distance': [1, 2, 3, 4], 'region': ['a', 'b', 'a', 'b'], 'minutes': [50, 7, 9, 60]}, 'days': [3, 1, 2, 4]},
             {'data': {'distance': [5, 6, 7, 8], 'region': ['a', 'b', 'a', 'b'], 'minutes': [10, 20, 30, 99]}, 'days': [1, 2, 2, 3]}]

SPECS = [
    code_step('stp_db7b18b4-f9b6-43ab-8866-6020301a260e', 'drop으로 정답 열 minutes를 입력에서 빼세요', '맞힐 정답을 입력에 섞지 않아요.',
              'X = df에는 정답 minutes가 들어 있다. df.drop(columns=["minutes"])로 고쳐 접수 때 아는 열만 남긴다. 채점은 열 구성이 다른 표로 실행한다.',
              '접수 때 minutes는 아직 모르는 정답이에요. 정답은 y로 따로 두고 입력 X에는 넣지 않아요. `df.drop(columns=[열])`은 그 열만 뺀 새 표를 돌려줘요.',
              'X 줄을 고쳐 정답 열 minutes를 뺀 나머지 열을 입력으로 쓰세요. 채점은 열 구성이 다른 표로도 실행해요.',
              ['코드 실행을 눌러 입력 열을 확인하세요.', '`X = df`를 `X = df.drop(columns=["minutes"])`로 고치세요.', '코드 실행을 눌러 정답 열이 빠졌는지 확인하세요.', SUBMIT],
              s1, s1_sol, n1, {n1.actions[-1]['text']: W}, cases=TABLES,
              reject=[([['X = df.drop(columns=["minutes"])\n', 'X = df[["distance", "region"]]\n']], 'Typing this table\'s columns'),
                      ([['X = df.drop(columns=["minutes"])\n', 'X = df.drop(columns=["distance"])\n']], 'Dropping another column')],
              accept=[([['X = df.drop(columns=["minutes"])\n', 'X = df.loc[:, df.columns != "minutes"]\n']], 'Boolean column mask')]),
    code_step('stp_09e61173-47f5-4a23-963b-fc1cd186e2df', '완료 시각 delivered_at도 입력에서 빼세요', '예측 시점에 모르는 미래 열을 입력에서 빼요.',
              'minutes만 빼면 완료 시각 delivered_at이 남는다. drop 목록에 delivered_at을 더해 접수 때 아는 열만 남긴다. 채점은 열 구성이 다른 표로 실행한다.',
              'minutes는 뺐지만 완료 시각을 넣었어요. 완료 시각은 배송이 끝난 뒤에만 알 수 있어요. 정답과 열 이름이 달라도 예측 시점에 모르는 값은 입력에 넣지 않아요.',
              'X 줄을 고쳐 정답과 완료 시각을 모두 뺀 열을 입력으로 쓰세요. 채점은 열 구성이 다른 표로도 실행해요.',
              ['코드 실행을 눌러 남은 입력 열을 확인하세요.', '`["minutes"]`를 `["minutes", "delivered_at"]`로 고치세요.', '코드 실행을 눌러 미래 열이 빠졌는지 확인하세요.', SUBMIT],
              s2, s2_sol, n2, {n2.actions[-1]['text']: W}, cases=[dict(TABLES[0], delivered=['09:00', '09:30']), dict(TABLES[1], delivered=['1', '2', '3', '4'])],
              reject=[([['X = df.drop(columns=["minutes", "delivered_at"])', 'X = df.drop(columns=["minutes"])']], 'Keeping the delivery time'),
                      ([['X = df.drop(columns=["minutes", "delivered_at"])', 'X = df[["distance", "region"]]']], 'Typing this table\'s columns')],
              accept=[([['X = df.drop(columns=["minutes", "delivered_at"])', 'X = df.drop(columns="minutes").drop(columns="delivered_at")']], 'Two drops')]),
    code_step('stp_83c77f58-dc74-4c7f-9c57-784b41ce0cd9', 'train.mean()으로 훈련만의 기준을 구하세요', '남겨 둔 평가 값이 기준 통계를 바꾸지 않게 해요.',
              '훈련과 평가를 합친 평균은 43.333이다. train.mean()으로 고쳐 15.0을 확인한다. 채점은 평가 극단값이 다른 자료로 실행한다.',
              '앞의 두 관측은 훈련, 마지막 값은 평가용이에요. 전처리 기준은 훈련에서만 배워요. 평가 값이 섞인 기준은 평가 자료가 바뀌면 함께 바뀌어요.',
              'reference 줄을 고쳐 평가 값을 빼고 훈련 값만으로 기준 평균을 구하세요. 채점은 다른 자료로도 실행해요.',
              ['코드 실행을 눌러 기준 평균을 확인하세요.', '`pd.concat([train, test]).mean()`을 `train.mean()`으로 고치세요.', '코드 실행을 눌러 훈련 평균을 확인하세요.', SUBMIT],
              s3, s3_sol, n3, {n3.actions[-1]['text']: W, n3.actions[5]['text']: '실제 훈련 평균과 기준의 독립성을 정확히 말해요.'}, cases=SER_CASES,
              reject=[([['reference = train.mean()', 'reference = pd.concat([train, test]).mean()']], 'Mean with the test values'), ([['reference = train.mean()', 'reference = 15.0']], 'Typing the mean')],
              accept=[([['reference = train.mean()', 'reference = sum(train_values) / len(train_values)']], 'Mean by hand')]),
    code_step('stp_e6057b0b-85f5-4ad8-b36e-cf4c957e51ff', 'train.median()으로 채움 기준을 정하세요', '빈값을 채우는 기준도 훈련에서 배워 평가에 적용해요.',
              '평가 중앙값 100으로 채우면 평가가 기준을 정한다. train.median()으로 고쳐 15로 채운 [15.0, 100.0]을 확인한다. 채점은 다른 자료로 실행한다.',
              '평가 자료의 빈값을 채우려 해요. 채움 값도 훈련에서 배운 기준이에요. `fillna(값)`은 빈값을 그 값으로 채워요.',
              'reference 줄을 고쳐 평가가 아니라 훈련에서 채움 기준을 정하세요. 채점은 다른 자료로도 실행해요.',
              ['코드 실행을 눌러 채움 값을 확인하세요.', '`test.median()`을 `train.median()`으로 고치세요.', '코드 실행을 눌러 훈련 기준으로 채웠는지 확인하세요.', SUBMIT],
              s4, s4_sol, n4, {n4.actions[-1]['text']: W}, cases=[{'train_values': [4, 8, 6], 'test_values': [None, 1000, None]}, {'train_values': [30], 'test_values': [5, None]}],
              reject=[([['reference = train.median()', 'reference = test.median()']], 'Median of the test'), ([['reference = train.median()', 'reference = pd.concat([train, test]).median()']], 'Median of everything')],
              accept=[([['reference = train.median()', 'reference = train.quantile(0.5)']], 'Half quantile')]),
    code_step('stp_f9bcb716-4fa1-4b04-b068-1857c58aa38a', 'isin으로 고객 단위로 훈련과 평가를 나누세요', '같은 고객의 자료가 훈련과 평가 양쪽에 걸치지 않게 나눠요.',
              '행을 번갈아 나누면 두 고객이 양쪽에 있어 True다. isin(test_customers)로 고객 단위로 나눠 False를 확인한다. 채점은 고객이 다른 자료로 실행한다.',
              '새 고객의 배송을 평가하는 게 목표예요. 행이 겹치지 않아도 같은 고객이 양쪽에 있으면 그 고객을 이미 본 셈이에요. `df["customer"].isin(목록)`은 고객이 목록에 있으면 True예요.',
              '두 줄을 고쳐 test_customers의 고객 행은 모두 평가로, 나머지 고객 행은 훈련으로 나누세요. 채점은 다른 고객 자료로도 실행해요.',
              ['코드 실행을 눌러 True가 나오는지 확인하세요.', 'train 줄을 `df[~df["customer"].isin(test_customers)]`로 고치세요.', 'test 줄을 `df[df["customer"].isin(test_customers)]`로 고치세요.', '코드 실행을 눌러 False와 고객별 시간을 확인하세요.', SUBMIT],
              s5, s5_sol, n5, {n5.actions[-1]['text']: W},
              cases=[{'data': {'customer': ['B', 'C', 'B', 'A', 'C'], 'minutes': [5, 6, 7, 8, 9]}, 'test_customers': ['C']},
                     {'data': {'customer': ['A', 'B', 'C', 'A'], 'minutes': [1, 2, 3, 4]}, 'test_customers': ['A', 'C']}],
              reject=[([['test = df[df["customer"].isin(test_customers)]\n', 'test = df.iloc[1::2]\n']], 'Rows still alternate'),
                      ([['train = df[~df["customer"].isin(test_customers)]\ntest = df[df["customer"].isin(test_customers)]\n', 'train = df[df["customer"] == "A"]\ntest = df[df["customer"] == "B"]\n']], 'Typing this data\'s customers')],
              accept=[([['train = df[~df["customer"].isin(test_customers)]\n', 'train = df.drop(index=df[df["customer"].isin(test_customers)].index)\n']], 'Dropping the test rows')]),
    code_step('stp_c3deb2cf-dc1b-4dcd-81cf-641100d3fa05', 'GroupShuffleSplit으로 고객 그룹 하나를 평가로 남기세요', '그룹 분리에서 test_size가 그룹 수임을 확인해요.',
              'ShuffleSplit(test_size=2)는 평가 두 행이 서로 다른 고객이라 True다. GroupShuffleSplit(test_size=1)과 groups로 고쳐 2 1과 False를 확인한다. 채점은 다른 그룹 자료로 실행한다.',
              '고객마다 관측이 두 개씩 있고 고객 하나를 평가에 남겨요. `GroupShuffleSplit(test_size=1)`의 1은 그룹 하나이고, `split(rows, groups=groups)`로 같은 고객의 행을 함께 옮겨요.',
              'train 줄을 고쳐 행이 아니라 고객 그룹 하나를 평가로 남기세요. 채점은 다른 그룹 자료로도 실행해요.',
              ['코드 실행을 눌러 평가 고객 수와 겹침을 확인하세요.', '`ShuffleSplit(n_splits=1, test_size=2, random_state=0).split(rows)`를 `GroupShuffleSplit(n_splits=1, test_size=1, random_state=0).split(rows, groups=groups)`로 고치세요.', '코드 실행을 눌러 고객 하나가 평가로 갔는지 확인하세요.', SUBMIT],
              s6, s6_sol, n6, {n6.actions[-1]['text']: W, n6.actions[2]['text']: '실제 ShuffleSplit 결과를 정확히 말해요.'},
              cases=[{'groups': ['x', 'y', 'x', 'z', 'z', 'z', 'y']}, {'groups': ['p', 'p', 'p', 'q']}],
              reject=[([['split(rows, groups=groups))', 'split(rows, groups=list(range(len(groups)))))']], 'Every row its own group'),
                      ([['GroupShuffleSplit(n_splits=1, test_size=1, random_state=0)', 'ShuffleSplit(n_splits=1, test_size=2, random_state=0)'], ['split(rows, groups=groups)', 'split(rows)']], 'Rows again')],
              accept=[([['test_size=1, random_state=0)', 'test_size=1, random_state=0, train_size=None)']], 'Explicit train_size')]),
    code_step('stp_1bac5ff3-c7cc-4257-8ded-2d005be9e5ac', 'train["minutes"].mean()으로 과거만의 기준을 쓰세요', '미래 관측으로 과거 기준을 만들지 않아요.',
              '전체 평균 43.333에는 미래 날짜 3의 100이 섞인다. train["minutes"].mean()으로 고쳐 15.0을 확인한다. 채점은 날짜 순서·값이 다른 자료로 실행한다.',
              '날짜 3은 미래 평가 관측이에요. 날짜 2까지 알 수 있는 자료로 기준을 정해요. `train`은 날짜 2 이하의 행만 남긴 표예요.',
              'reference 줄을 고쳐 미래 관측을 빼고 과거 훈련 자료의 평균 시간을 기준으로 쓰세요. 채점은 다른 날짜 자료로도 실행해요.',
              ['코드 실행을 눌러 기준 평균을 확인하세요.', '`df["minutes"].mean()`을 `train["minutes"].mean()`으로 고치세요.', '코드 실행을 눌러 과거 평균을 확인하세요.', SUBMIT],
              s7, s7_sol, n7, {n7.actions[-1]['text']: W}, cases=DAY_CASES,
              reject=[([['reference = train["minutes"].mean()', 'reference = df["minutes"].mean()']], 'Mean with the future'),
                      ([['reference = train["minutes"].mean()', 'reference = df["minutes"].head(2).mean()']], 'First two rows regardless of day')],
              accept=[([['reference = train["minutes"].mean()', 'reference = df.loc[df["day"] <= 2, "minutes"].mean()']], 'loc with the day condition')]),
]
