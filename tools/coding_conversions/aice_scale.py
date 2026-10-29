"""aice-scale: 8 answer-picking steps -> coding steps (2026-10-29).

Each step fits a real scikit-learn transformer and prints the learned basis and the transformed values.
Prepared cases rerun with other train/test values, so refitting on the test data, typed numbers and the
starter's setting fail."""
from _kit import Script, code_step

OPENING = ['이 수업에서는 전처리 기준을 배우는 일과 적용하는 일을 직접 코드로 구별해요. 평가에도 훈련 기준을 유지해요.',
           'fit과 transform의 결과를 비교해요. 빈값·범위 밖 값·새 범주도 직접 고쳐 확인해요.']
PRD_SCOPE = ['두 챕터·두 단원·열 스텝으로 같은 배송 입력을 변환해요.',
             'fit·transform 분리, 상수열 스케일 계산, 결측 수 세기, MinMax 범위, RobustScaler, OneHotEncoder의 handle_unknown, 전처리 Pipeline을 한 곳씩 직접 고쳐 써요.',
             'Standard·MinMax·Robust의 서로 다른 기준과 범위 정책을 비교해요.']
PRD_GRADING = ['직접 고친 코드를 실제 파이썬·scikit-learn으로 실행해 판정해요. 실행·해설만으로 성공시키지 않아요.',
               '다른평균·상수열·두특성·여러평가행의실제변환값을검사해요. 준비 값을 바꿔 다시 실행해 기준 풀이와 비교하고, 평가 자료로 다시 fit한 답과 숫자를 글자로 적은 답은 거절해요.',
               '기본오류와명시적unknown정책을구별해검증해요.',
               '마지막 도전(stp_d9e36990-e641-4647-b0f0-ea0bdc24acf5): 실제 Python 실행과 다른 준비 자료의 결과를 검사해요. 시작 코드는 실패하고 동등한 풀이도 통과해야 해요.']
PRD_NARRATION = ['기준과 메서드 한 곳씩 고치고 실제 수치·오류를 읽어요.',
                 '평가재학습·상수열·결측유지·범위자르기·미지범주정보손실을 조심할 지점으로 짚어요.']

SUBMIT = '수정한 코드를 제출하세요.'
W = '실제 scikit-learn 동작을 정확히 말해요.'
STD = 'from sklearn.preprocessing import StandardScaler\n\n# 훈련과 평가 자료는 이미 나눠 두었어요.\n'
TT_CASES = [{'train_values': [[4], [8], [12]], 'test_values': [[0], [16]]}, {'train_values': [[1], [3]], 'test_values': [[3]]}]

s1 = (STD + '# 행마다 특성이 하나라서 [[0], [2]]처럼 대괄호를 두 겹으로 써요.\ntrain_values = [[0], [2]]\ntest_values = [[10]]\nscaler = StandardScaler()\n'
      '# 이 줄을 고쳐 transform 전에 훈련 자료로 기준을 배우세요.\npass\n'
      'print(scaler.mean_.tolist(), scaler.scale_.tolist())\nprint(scaler.transform(train_values).tolist())\nprint(scaler.transform(test_values).tolist())\n')
s1_sol = s1.replace('pass\n', '# fit은 훈련 자료의 평균과 스케일을 배워요. transform은 그 기준을 적용해요.\nscaler.fit(train_values)\n')
n1 = (Script(s1)
      .say('표준화는 (값 − 평균) ÷ 스케일이에요. 기준을 배우는 줄이 비어 있어 훈련 자료로 fit해야 해요.', 'text:pass 줄을 고쳐 transform 전에 훈련 자료로 기준을 배우세요.')
      .run('print(scaler.mean_', 'print(scaler.transform(test', error='AttributeError')
      .say('AttributeError예요. 아직 배운 평균 mean_이 없어요.', 'output')
      .patch('pass\n', 'scaler.fit(train_values)\n', 'pass를 scaler.fit(train_values)로 바꿔요.')
      .run('print(scaler.mean_', 'print(scaler.transform(test')
      .say('평균 1과 스케일 1을 배웠어요. 훈련은 -1과 1, 평가 10은 (10 − 1) ÷ 1인 9예요.', 'output')
      .say('조심하세요. 평가 10이 훈련 범위 밖이어도 같은 기준으로 바꿔요. 평가의 평균은 쓰지 않아요.', 'code:scaler.fit(train_values)'))

s2 = (STD + 'train_values = [[0], [2]]\ntest_values = [[10]]\nscaler = StandardScaler()\nscaler.fit(train_values)\n'
      '# 이 줄을 고쳐 평가 자료에서 다시 배우지 말고 훈련 기준만 적용하세요.\nprint(scaler.fit_transform(test_values).tolist())\nprint(scaler.mean_.tolist())\n')
s2_sol = s2.replace('print(scaler.fit_transform(test_values).tolist())', '# 이미 fit한 기준으로 바꿀 때는 transform만 써요. fit_transform은 기준을 다시 배워요.\nprint(scaler.transform(test_values).tolist())')
n2 = (Script(s2)
      .say('평가에서 fit_transform을 다시 했어요. 훈련 기준을 유지하도록 그 줄을 고쳐야 해요.', 'text:print 줄을 고쳐 평가 자료에서 다시 배우지 말고 훈련 기준만 적용하세요.')
      .run('print(scaler.fit_transform', 'print(scaler.mean_')
      .say('[[0.0]]과 평균 [10.0]이에요. 평가 하나로 기준을 다시 배워 평균이 10이 됐어요.', 'output')
      .patch('scaler.fit_transform(test_values)', 'scaler.transform(test_values)', 'fit_transform을 transform으로 바꿔요.')
      .run('print(scaler.transform(test', 'print(scaler.mean_')
      .say('[[9.0]]과 평균 [1.0]이에요. 훈련에서 배운 기준이 그대로예요.', 'output')
      .say('조심하세요. 평가 자료로 기준을 다시 배우면 평가 정보가 전처리에 섞여요.', 'code:scaler.transform(test_values)'))

s3 = (STD + 'train_values = [[5], [5]]\ntest_values = [[7]]\nscaler = StandardScaler()\nscaler.fit(train_values)\n'
      '# 값이 모두 같으면 퍼짐이 0이라 스케일러는 스케일을 1로 둬요.\nprint(scaler.scale_.tolist())\nprint(scaler.transform(test_values).tolist())\n'
      '# 이 줄을 고쳐 배운 평균과 스케일로 새 값을 직접 계산하세요.\nmanual = 0\nprint(manual)\n')
s3_sol = s3.replace('manual = 0\n', '# (값 − 배운 평균) ÷ 배운 스케일이에요.\nmanual = (test_values[0][0] - scaler.mean_[0]) / scaler.scale_[0]\n')
n3 = (Script(s3)
      .say('훈련 값이 모두 5였어요. 배운 평균과 스케일로 새 값 7을 직접 계산해 transform과 비교해야 해요.', 'text:manual 줄을 고쳐 배운 평균과 스케일로 새 값을 직접 계산하세요.')
      .run('print(scaler.scale_', 'print(manual)')
      .say('스케일 [1.0], 변환 [[2.0]], manual 0이에요. 새 값이 0이 된다고 미리 적었어요.', 'output')
      .patch('manual = 0\n', 'manual = (test_values[0][0] - scaler.mean_[0]) / scaler.scale_[0]\n', '(새 값 − mean_[0]) ÷ scale_[0]으로 계산해요.')
      .run('print(scaler.scale_', 'print(manual)')
      .say('manual도 2.0이에요. 평균 5를 빼고 스케일 1로 나눴어요.', 'output')
      .say('조심하세요. 훈련 값이 모두 같아도 새 값까지 0이 되지는 않아요. 0은 훈련 평균과 같은 값뿐이에요.', 'code:scaler.scale_[0]'))

s4 = ('import pandas as pd\n' + STD + 'train_values = [[0], [float("nan")], [2]]\ntest_values = [[float("nan")], [10]]\nscaler = StandardScaler()\nscaler.fit(train_values)\n'
      'result = scaler.transform(test_values)\nprint(result.tolist())\n# 이 줄을 고쳐 변환 결과에 남은 결측 개수를 세세요.\nmissing = 0\nprint(missing)\n')
s4_sol = s4.replace('missing = 0\n', '# 스케일러는 결측을 채우지 않아요. isna로 남은 결측을 세요.\nmissing = int(pd.isna(result).sum())\n')
n4 = (Script(s4)
      .say('평가의 첫 값은 결측이에요. 스케일한 결과에 결측이 몇 개 남았는지 세도록 고쳐야 해요.', 'text:missing 줄을 고쳐 변환 결과에 남은 결측 개수를 세세요.')
      .run('print(result', 'print(missing)')
      .say('[[nan], [9.0]]과 0이에요. 결측이 남았는데 0이라고 적혀 있어요.', 'output')
      .patch('missing = 0\n', 'missing = int(pd.isna(result).sum())\n', 'pd.isna(result).sum()으로 세요.')
      .run('print(result', 'print(missing)')
      .say('1이에요. 결측은 그대로 남고 10만 9로 바뀌었어요.', 'output')
      .say('조심하세요. 스케일은 결측을 채우지 않아요. 채움은 SimpleImputer 같은 단계로 따로 해요.', 'code:pd.isna(result)'))

s5 = ('from sklearn.preprocessing import MinMaxScaler\n\n# 훈련 범위로 기준을 정해요.\ntrain = [[0], [2]]\ntest = [[10]]\n'
      '# 이 줄의 옵션을 고쳐 훈련 범위 밖의 값도 잘라 내지 않고 같은 식으로 바꾸세요.\nscaler = MinMaxScaler(clip=True)\nscaler.fit(train)\nprint(scaler.transform(test).tolist())\n')
s5_sol = s5.replace('scaler = MinMaxScaler(clip=True)', '# clip=False(기본값)는 범위 밖 값을 0~1로 자르지 않아요.\nscaler = MinMaxScaler(clip=False)')
n5 = (Script(s5)
      .say('MinMaxScaler는 (값 − 훈련 최솟값) ÷ (훈련 최댓값 − 최솟값)이에요. 범위 밖 값이 잘리지 않게 옵션을 고쳐야 해요.', 'text:scaler 줄의 옵션을 고쳐 훈련 범위 밖의 값도 잘라 내지 않고 같은 식으로 바꾸세요.')
      .run('print(scaler.transform')
      .say('[[1.0]]이에요. clip=True가 10을 훈련 범위 끝 1로 잘랐어요.', 'output')
      .patch('MinMaxScaler(clip=True)', 'MinMaxScaler(clip=False)', 'clip을 False로 바꿔요.')
      .run('print(scaler.transform')
      .say('[[5.0]]이에요. (10 − 0) ÷ (2 − 0)이라 훈련 범위보다 훨씬 큰 값임이 남아요.', 'output')
      .say('조심하세요. 훈련이 0~1이 됐다고 평가도 0~1 안이라는 보장은 없어요.', 'code:clip=False'))

s6 = ('from sklearn.preprocessing import StandardScaler, RobustScaler\n\n# 큰 값이 포함된 훈련 표예요.\ntrain = [[0], [1], [2], [3], [100]]\n'
      '# 이 줄을 고쳐 평균·표준편차 대신 중앙값과 사분위 범위로 기준을 정하세요.\nscaler = StandardScaler()\nscaler.fit(train)\n'
      'print(scaler.transform([[4], [100]]).round(3).tolist())\nprint(len(scaler.transform(train)))\n')
s6_sol = s6.replace('scaler = StandardScaler()', '# RobustScaler는 중앙값을 빼고 사분위 범위(IQR)로 나눠요. 극단값 행을 지우지 않아요.\nscaler = RobustScaler()')
n6 = (Script(s6)
      .say('훈련 표에 100이 있어요. 중앙값과 사분위 범위로 기준을 정하도록 스케일러를 고쳐야 해요.', 'text:scaler 줄을 고쳐 평균·표준편차 대신 중앙값과 사분위 범위로 기준을 정하세요.')
      .run('print(scaler.transform', 'print(len')
      .say('[[-0.436], [1.999]]과 5예요. 100이 평균을 21.2로 끌어올려 4가 평균보다 작게 나왔어요.', 'output')
      .patch('scaler = StandardScaler()', 'scaler = RobustScaler()', 'RobustScaler()로 바꿔요.')
      .run('print(scaler.transform', 'print(len')
      .say('[[1.0], [49.0]]과 5예요. 중앙값 2와 IQR 2로 바꿨고 100도 지워지지 않고 49로 남았어요.', 'output')
      .say('조심하세요. RobustScaler는 기준만 극단값에 덜 흔들려요. 극단값 행을 빼 주지 않아요.', 'code:RobustScaler()'))

s7 = ('from sklearn.preprocessing import OneHotEncoder\n\n# 훈련에 있던 두 지역으로 표시 열을 배워요.\ntrain = [["north"], ["south"]]\ntest = [["west"]]\n'
      '# 이 줄의 옵션을 고쳐 처음 보는 지역은 오류 대신 모두 0으로 표시하세요.\nencoder = OneHotEncoder(sparse_output=False)\nencoder.fit(train)\n'
      'print(encoder.categories_[0].tolist())\nprint(encoder.transform(test).tolist())\n')
s7_sol = s7.replace('encoder = OneHotEncoder(sparse_output=False)', '# handle_unknown="ignore"는 처음 보는 범주를 모든 표시 열 0으로 바꿔요.\nencoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")')
n7 = (Script(s7)
      .say('처음 보는 west를 변환하려 해요. 기본 인코더는 멈추므로 처리 옵션을 고쳐야 해요.', 'text:encoder 줄의 옵션을 고쳐 처음 보는 지역은 오류 대신 모두 0으로 표시하세요.')
      .run('print(encoder.categories_', 'print(encoder.transform', error='ValueError')
      .say("['north', 'south']를 배운 뒤 west에서 ValueError예요. 기본은 알 수 없는 범주에서 오류를 내요.", 'output')
      .patch('OneHotEncoder(sparse_output=False)', 'OneHotEncoder(sparse_output=False, handle_unknown="ignore")', 'handle_unknown="ignore"를 더해요.')
      .run('print(encoder.categories_', 'print(encoder.transform')
      .say('[[0.0, 0.0]]이에요. 새 열은 생기지 않고 west는 모든 표시가 0이에요.', 'output')
      .say('조심하세요. ignore는 west라는 정보를 버려요. 처음 보는 범주가 얼마나 오는지 따로 확인해요.', 'code:handle_unknown="ignore"'))

s8 = ('from sklearn.impute import SimpleImputer\nfrom sklearn.preprocessing import StandardScaler\nfrom sklearn.pipeline import Pipeline\n\n'
      '# 전처리 두 단계 모두 훈련에서 기준을 배워요.\ntrain = [[0], [float("nan")], [2]]\ntest = [[10], [float("nan")]]\n'
      'prep = Pipeline([("fill", SimpleImputer(strategy="median")), ("scale", StandardScaler())])\nprep.fit(train)\n'
      '# 이 줄을 고쳐 평가에도 훈련에서 배운 두 단계의 기준을 그대로 적용하세요.\nresult = prep.fit_transform(test)\n'
      'print(prep.named_steps["fill"].statistics_.tolist())\nprint(prep.named_steps["scale"].mean_.tolist())\nprint(result.round(3).tolist())\n')
s8_sol = s8.replace('result = prep.fit_transform(test)', '# Pipeline의 transform은 채움과 스케일을 훈련 기준으로 차례대로 적용해요.\nresult = prep.transform(test)')
n8 = (Script(s8)
      .say('빈값 채움 다음에 스케일을 적용해요. 평가에서 두 단계를 다시 배우지 않도록 고쳐야 해요.', 'text:result 줄을 고쳐 평가에도 훈련에서 배운 두 단계의 기준을 그대로 적용하세요.')
      .run('print(prep.named_steps["fill"]', 'print(result')
      .say('채움 값 10, 평균 10, 결과 [[0.0], [0.0]]이에요. 평가로 두 단계를 다시 배웠어요.', 'output')
      .patch('prep.fit_transform(test)', 'prep.transform(test)', 'fit_transform을 transform으로 바꿔요.')
      .run('print(prep.named_steps["fill"]', 'print(result')
      .say('채움 값 1과 평균 1을 유지했어요. 10은 11.023, 빈값은 훈련 중앙값 1로 채워 0.0이에요.', 'output')
      .say('조심하세요. Pipeline을 써도 평가에서 fit을 부르면 모든 단계가 다시 배워요.', 'code:prep.transform(test)'))

SPECS = [
    code_step('stp_86be259b-275c-4a53-8b70-7ba225697042', 'scaler.fit(train_values)로 훈련 기준을 배우세요', '훈련 자료로 표준화 기준을 배우고 같은 기준을 평가에 적용해요.',
              'fit 없이 mean_을 읽으면 AttributeError다. scaler.fit(train_values)로 평균 1·스케일 1을 배우고 평가 10이 9가 됨을 확인한다. 채점은 다른 훈련·평가 값으로 실행한다.',
              '표준화는 (값 − 평균) ÷ 스케일이에요. `scaler.fit(훈련)`은 훈련 자료의 평균과 스케일을 배우고, `scaler.transform(자료)`는 배운 기준을 적용해요.',
              'pass 줄을 고쳐 transform 전에 훈련 자료로 기준을 배우세요. 채점은 다른 훈련·평가 값으로도 실행해요.',
              ['코드 실행을 눌러 AttributeError가 나오는지 확인하세요.', '`pass`를 `scaler.fit(train_values)`로 고치세요.', '코드 실행을 눌러 배운 기준과 변환값을 확인하세요.', SUBMIT],
              s1, s1_sol, n1, {n1.actions[-1]['text']: W}, cases=TT_CASES,
              reject=[([['scaler.fit(train_values)\n', 'scaler.fit(test_values)\n']], 'Fitting on the test data'),
                      ([['scaler.fit(train_values)\n', 'scaler.fit(train_values + test_values)\n']], 'Fitting on both')],
              accept=[([['scaler.fit(train_values)\n', 'scaler = scaler.fit(train_values)\n']], 'Keeping the returned scaler')]),
    code_step('stp_b90c45ec-26b6-4596-bf35-df47b960fa5f', 'transform만 써서 평가에 훈련 기준을 적용하세요', '평가 자료에서 기준을 다시 배우지 않고 훈련 기준을 적용해요.',
              '평가에서 fit_transform은 평균을 10으로 다시 배워 [[0.0]]이다. transform으로 고쳐 [[9.0]]과 평균 [1.0]을 확인한다. 채점은 다른 값으로 실행한다.',
              '훈련에서 이미 fit했어요. `fit_transform`은 기준을 다시 배운 뒤 바꾸고, `transform`은 이미 배운 기준으로만 바꿔요.',
              'print 줄을 고쳐 평가 자료에서 다시 배우지 말고 훈련 기준만 적용하세요. 채점은 다른 훈련·평가 값으로도 실행해요.',
              ['코드 실행을 눌러 평균이 바뀌는지 확인하세요.', '`scaler.fit_transform(test_values)`를 `scaler.transform(test_values)`로 고치세요.', '코드 실행을 눌러 훈련 평균이 유지되는지 확인하세요.', SUBMIT],
              s2, s2_sol, n2, {n2.actions[-1]['text']: '실제 누수 위험을 정확히 말해요.'}, cases=TT_CASES,
              reject=[([['print(scaler.transform(test_values).tolist())', 'print(scaler.fit_transform(test_values).tolist())']], 'Refitting on the test data'),
                      ([['print(scaler.transform(test_values).tolist())', 'print([[9.0]])']], 'Typing the value')],
              accept=[([['print(scaler.transform(test_values).tolist())', 'print(((__import__("numpy").array(test_values) - scaler.mean_) / scaler.scale_).tolist())']], 'Applying the learned basis by hand')]),
    code_step('stp_3f0bca24-be1a-485d-b153-177f131ccc52', '배운 평균과 스케일로 새 값을 직접 계산하세요', '훈련 값이 모두 같을 때의 스케일과 새 값 변환을 계산해 확인해요.',
              '훈련 값이 모두 5면 스케일은 1이고 새 값 7은 [[2.0]]이다. manual = (값 − mean_[0]) ÷ scale_[0]으로 고쳐 2.0을 확인한다. 채점은 다른 상수·새 값으로 실행한다.',
              '훈련 값이 모두 5였어요. 값이 모두 같으면 퍼짐이 0이라, 스케일러는 0으로 나누지 않도록 스케일을 1로 둬요. 배운 평균은 `scaler.mean_[0]`, 스케일은 `scaler.scale_[0]`이에요.',
              'manual 줄을 고쳐 배운 평균과 스케일로 새 값을 직접 계산하세요. 채점은 다른 값으로도 실행해요.',
              ['코드 실행을 눌러 transform 결과와 manual을 비교하세요.', '`manual = 0`을 `manual = (test_values[0][0] - scaler.mean_[0]) / scaler.scale_[0]`로 고치세요.', '코드 실행을 눌러 두 값이 같은지 확인하세요.', SUBMIT],
              s3, s3_sol, n3, {n3.actions[-1]['text']: W},
              cases=[{'train_values': [[3], [3], [3]], 'test_values': [[-1]]}, {'train_values': [[2], [6]], 'test_values': [[10]]}],
              reject=[([['manual = (test_values[0][0] - scaler.mean_[0]) / scaler.scale_[0]\n', 'manual = 2.0\n']], 'Typing the value'),
                      ([['manual = (test_values[0][0] - scaler.mean_[0]) / scaler.scale_[0]\n', 'manual = test_values[0][0] - scaler.mean_[0]\n']], 'Forgetting the scale')],
              accept=[([['manual = (test_values[0][0] - scaler.mean_[0]) / scaler.scale_[0]\n', 'manual = float(scaler.transform(test_values)[0][0])\n']], 'Reading the transform')]),
    code_step('stp_861af409-6d51-4d80-a6e7-00e3167c31b6', 'pd.isna로 변환 뒤 남은 결측을 세세요', '스케일링이 결측을 채우지 않음을 세어 확인해요.',
              '변환 결과 [[nan], [9.0]]에 결측이 남는데 missing은 0이다. int(pd.isna(result).sum())으로 고쳐 1을 확인한다. 채점은 결측 수가 다른 평가 자료로 실행한다.',
              '평가의 첫 값은 결측이에요. StandardScaler는 결측을 무시하고 기준을 배우고, 변환할 때도 결측을 그대로 둬요. `pd.isna(배열)`은 결측 자리를 True로 표시해요.',
              'missing 줄을 고쳐 변환 결과에 남은 결측 개수를 세세요. 채점은 결측 수가 다른 자료로도 실행해요.',
              ['코드 실행을 눌러 결과와 missing을 확인하세요.', '`missing = 0`을 `missing = int(pd.isna(result).sum())`로 고치세요.', '코드 실행을 눌러 남은 결측 수를 확인하세요.', SUBMIT],
              s4, s4_sol, n4, {n4.actions[-1]['text']: W},
              cases=[{'train_values': [[1], [3]], 'test_values': [[None], [None], [5]]}, {'train_values': [[0], [4]], 'test_values': [[2]]}],
              reject=[([['missing = int(pd.isna(result).sum())\n', 'missing = 1\n']], 'Typing the count'),
                      ([['missing = int(pd.isna(result).sum())\n', 'missing = int(pd.isna(train_values).sum())\n']], 'Counting the training data')],
              accept=[([['missing = int(pd.isna(result).sum())\n', 'missing = int(sum(1 for row in result for value in row if value != value))\n']], 'NaN is not equal to itself')]),
    code_step('stp_f9faaf00-f154-44ce-9607-c80f39eb7b5a', 'clip=False로 범위 밖 값도 같은 식으로 바꾸세요', 'MinMax 기준에서 훈련 범위 밖 값이 0~1을 벗어날 수 있음을 확인해요.',
              'clip=True는 10을 [[1.0]]로 자른다. clip=False로 고쳐 (10 − 0) ÷ (2 − 0)인 [[5.0]]을 확인한다. 채점은 다른 훈련 범위로 실행한다.',
              '훈련은 0~1로 바뀌었어요. MinMaxScaler는 (값 − 훈련 최솟값) ÷ (훈련 최댓값 − 최솟값)이에요. `clip=True`면 결과를 0~1로 잘라요.',
              'scaler 줄의 옵션을 고쳐 훈련 범위 밖의 값도 잘라 내지 않고 같은 식으로 바꾸세요. 채점은 다른 훈련 범위로도 실행해요.',
              ['코드 실행을 눌러 [[1.0]]이 나오는지 확인하세요.', '`clip=True`를 `clip=False`로 고치세요.', '코드 실행을 눌러 범위 밖 값을 확인하세요.', SUBMIT],
              s5, s5_sol, n5, {n5.actions[-1]['text']: W},
              cases=[{'train': [[10], [20]], 'test': [[5], [40]]}, {'train': [[0], [4]], 'test': [[2]]}],
              reject=[([['scaler = MinMaxScaler(clip=False)', 'scaler = MinMaxScaler(clip=True)']], 'Clipping'),
                      ([['print(scaler.transform(test).tolist())', 'print([[5.0]])']], 'Typing the value')],
              accept=[([['scaler = MinMaxScaler(clip=False)', 'scaler = MinMaxScaler()']], 'Default setting')]),
    code_step('stp_ae569cc8-c606-44ad-a5a7-376f1dc2baca', 'RobustScaler로 중앙값과 IQR 기준을 쓰세요', '극단값이 있는 훈련 자료에서 중앙값·사분위 범위 기준으로 바꿔요.',
              'StandardScaler는 100에 끌려 4를 -0.456으로 바꾼다. RobustScaler로 고쳐 중앙값 2·IQR 2 기준의 [[1.0], [49.0]]과 그대로인 5행을 확인한다. 채점은 다른 훈련 자료로 실행한다.',
              '큰 값 100이 포함된 훈련 표예요. StandardScaler는 평균과 표준편차를, `RobustScaler`는 중앙값과 사분위 범위(IQR)를 기준으로 써요.',
              'scaler 줄을 고쳐 평균·표준편차 대신 중앙값과 사분위 범위로 기준을 정하세요. 채점은 다른 훈련 자료로도 실행해요.',
              ['코드 실행을 눌러 변환값과 행 수를 확인하세요.', '`StandardScaler()`를 `RobustScaler()`로 고치세요.', '코드 실행을 눌러 변환값과 행 수를 다시 확인하세요.', SUBMIT],
              s6, s6_sol, n6, {n6.actions[-1]['text']: W},
              cases=[{'train': [[10], [12], [14], [16], [500], [18]]}, {'train': [[1], [2], [3]]}],
              reject=[([['scaler = RobustScaler()', 'scaler = StandardScaler()']], 'Mean and standard deviation'),
                      ([['print(scaler.transform([[4], [100]]).round(3).tolist())', 'print([[1.0], [49.0]])']], 'Typing the values')],
              accept=[([['scaler = RobustScaler()', 'scaler = RobustScaler(quantile_range=(25.0, 75.0))']], 'Explicit quartiles')]),
    code_step('stp_fad82ade-0901-4a25-bafd-aec8ed56545c', 'handle_unknown="ignore"로 처음 보는 지역을 0으로 표시하세요', '처음 보는 범주를 처리하는 인코더 정책을 직접 정해요.',
              '기본 OneHotEncoder는 west에서 ValueError다. handle_unknown="ignore"로 고쳐 [[0.0, 0.0]]을 확인한다. 새 열은 생기지 않는다. 채점은 다른 훈련·평가 범주로 실행한다.',
              '훈련에 있던 두 지역으로 표시 열을 배웠어요. 기본 OneHotEncoder는 처음 보는 범주에서 오류를 내요. `handle_unknown="ignore"`는 처음 보는 범주를 모든 표시 열 0으로 바꿔요.',
              'encoder 줄의 옵션을 고쳐 처음 보는 지역은 오류 대신 모두 0으로 표시하세요. 채점은 다른 범주로도 실행해요.',
              ['코드 실행을 눌러 ValueError가 나오는지 확인하세요.', '`OneHotEncoder(sparse_output=False)`에 `handle_unknown="ignore"`를 더하세요.', '코드 실행을 눌러 west의 표시를 확인하세요.', SUBMIT],
              s7, s7_sol, n7, {n7.actions[-1]['text']: '실제 정보 손실 위험을 정확히 말해요.'},
              cases=[{'train': [['a'], ['b'], ['c']], 'test': [['b'], ['z']]}, {'train': [['north'], ['south']], 'test': [['south']]}],
              reject=[([['encoder.fit(train)\n', 'encoder.fit(train + test)\n']], 'Learning the test categories'),
                      ([['print(encoder.transform(test).tolist())', 'print([[0.0, 0.0]])']], 'Typing the row')],
              accept=[([['handle_unknown="ignore")', 'handle_unknown="infrequent_if_exist")']], 'infrequent_if_exist without infrequent categories ignores too')]),
    code_step('stp_ff7710f5-7f6e-4cbd-a872-78f84fa4f3ff', 'prep.transform으로 두 단계의 훈련 기준을 적용하세요', '전처리 Pipeline의 모든 단계에 훈련 기준을 유지해요.',
              '평가에서 fit_transform은 채움 값과 평균을 10으로 다시 배워 [[0.0], [0.0]]이다. prep.transform(test)로 고쳐 채움 1·평균 1을 유지하고 [[11.023], [0.0]]을 확인한다. 채점은 다른 값으로 실행한다.',
              '빈값 채움 다음에 스케일을 적용하는 Pipeline이에요. `prep.fit(훈련)`은 두 단계의 기준을 차례로 배우고, `prep.transform(자료)`는 배운 기준으로 차례대로 바꿔요.',
              'result 줄을 고쳐 평가에도 훈련에서 배운 두 단계의 기준을 그대로 적용하세요. 채점은 다른 값으로도 실행해요.',
              ['코드 실행을 눌러 배운 기준이 바뀌는지 확인하세요.', '`prep.fit_transform(test)`를 `prep.transform(test)`로 고치세요.', '코드 실행을 눌러 훈련 기준과 결과를 확인하세요.', SUBMIT],
              s8, s8_sol, n8, {n8.actions[-1]['text']: W},
              cases=[{'train': [[2], [4], [None], [9]], 'test': [[None], [0]]}, {'train': [[1], [3]], 'test': [[2], [5]]}],
              reject=[([['result = prep.transform(test)', 'result = prep.fit_transform(test)']], 'Refitting on the test data'),
                      ([['result = prep.transform(test)', 'result = StandardScaler().fit(train).transform(test)']], 'Skipping the fill step')],
              accept=[([['result = prep.transform(test)', 'result = prep.named_steps["scale"].transform(prep.named_steps["fill"].transform(test))']], 'Applying each fitted step')]),
]
