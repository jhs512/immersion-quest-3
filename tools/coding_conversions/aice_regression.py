"""aice-regression: 6 answer-picking steps -> coding steps (2026-10-29).

Step 6 (실행 성공과 현실의 타당성은 달라요) stays a choice: it asks whether a computed value is believable,
an interpretation, not code. Converted steps fit real scikit-learn models on small exact data and print
predictions, coefficients or errors; prepared cases rerun with other distances and times, so typed
results, a hardcoded target list and the starter's setting fail."""
from _kit import Script, code_step

OPENING = ['이 수업에서는 숫자를 예측하는 회귀의 흐름을 직접 코드로 써요. 모델 생성·학습·예측을 구별해요.',
           '간단한 기준 모델과 선형 회귀를 비교해요. 남겨 둔 자료와 새 입력으로 예측을 확인해요.']
PRD_SCOPE = ['두 챕터·세 단원·아홉 스텝으로 같은 배송 시간을 예측해요.',
             '평균 기준의 strategy·LinearRegression·fit 호출·2차원 입력·절편을 더한 직접 예측·남겨 둔 자료의 오차를 한 곳씩 직접 고쳐 써요. 실행 결과의 현실 타당성 판단은 선택 문항으로 남겨요.']
PRD_GRADING = ['직접 고친 코드를 실제 파이썬·scikit-learn으로 실행해 판정해요. 실행·해설만으로 성공시키지 않아요.',
               '다른 선형 관계·다른 새 거리·다른 평가 정답으로 다시 실행해 기준 풀이와 비교해요. 결과를 글자로 적은 답, 정답 목록을 직접 적은 학습, 절편을 뺀 계산, 훈련 오차는 거절해요.',
               '미학습 모델·1차원 입력의 오류는 실패로 설명하며 정상 예측과 구별해요.',
               '마지막 도전(stp_8f967e0e-fb58-44c3-b9ba-2b94b21bb01b): 실제 Python 실행과 다른 준비 자료의 결과를 검사해요. 시작 코드는 실패하고 동등한 풀이도 통과해야 해요.']
PRD_NARRATION = ['설정·호출·입력 모양을 고치고 실제 예측과 오류를 읽어요.',
                 '기준모델/입력무시·객체생성/학습·2차원모양·절편·훈련/평가를 조심할 지점으로 짚어요.']

SUBMIT = '수정한 코드를 제출하세요.'
W = '실제 scikit-learn 동작을 정확히 말해요.'
PAIR = '# 같은 관측의 거리와 실제 시간을 함께 준비해요.\n'

s1 = ('from sklearn.dummy import DummyRegressor\n\n' + PAIR + 'X_train = [[1], [2], [3]]\ny_train = [10, 20, 60]\n'
      '# 이 줄의 strategy를 고쳐 훈련 정답의 평균을 예측하는 기준 모델을 만드세요.\nmodel = DummyRegressor(strategy="median")\nmodel.fit(X_train, y_train)\n'
      'print(model.predict([[4], [5]]).round(6).tolist())\n')
s1_sol = s1.replace('model = DummyRegressor(strategy="median")', '# 기준 모델은 입력을 보지 않고 훈련 정답의 평균 하나만 기억해요.\nmodel = DummyRegressor(strategy="mean")')
n1 = (Script(s1)
      .say('비교 기준으로 쓸 단순한 모델이에요. strategy를 고쳐 훈련 정답의 평균을 예측하게 해야 해요.', 'text:model 줄의 strategy를 고쳐 훈련 정답의 평균을 예측하는 기준 모델을 만드세요.')
      .run('print(model.predict')
      .say('[20.0, 20.0]이에요. 가운데 값인 중앙값 20을 두 거리에 똑같이 냈어요.', 'output')
      .patch('strategy="median"', 'strategy="mean"', 'strategy를 "mean"으로 바꿔요.')
      .run('print(model.predict')
      .say('[30.0, 30.0]이에요. 10·20·60의 평균 30이에요.', 'output')
      .say('조심하세요. 기준 모델은 거리를 보지 않아요. 거리 4와 5의 예측이 같은 이유예요.', 'code:strategy="mean"'))

s2 = ('from sklearn.dummy import DummyRegressor\nfrom sklearn.linear_model import LinearRegression\n\n' + PAIR
      + 'X_train = [[1], [2], [3]]\ny_train = [10, 20, 30]\nX_test = [[4]]\n'
      '# 이 줄을 고쳐 거리에 따른 직선 관계를 배우는 LinearRegression을 쓰세요.\nmodel = DummyRegressor(strategy="mean")\nmodel.fit(X_train, y_train)\n'
      'print(model.predict(X_test).round(6).tolist())\n')
s2_sol = s2.replace('model = DummyRegressor(strategy="mean")', '# 선형 회귀는 거리가 1 늘 때 시간이 얼마나 느는지(기울기)를 배워요.\nmodel = LinearRegression()')
n2 = (Script(s2)
      .say('거리마다 시간이 10씩 늘어요. 이 관계를 배우도록 model 줄을 LinearRegression으로 고쳐야 해요.', 'text:model 줄을 고쳐 거리에 따른 직선 관계를 배우는 LinearRegression을 쓰세요.')
      .run('print(model.predict')
      .say('[20.0]이에요. 기준 모델은 거리 4에도 평균 20을 냈어요.', 'output')
      .patch('model = DummyRegressor(strategy="mean")', 'model = LinearRegression()', 'LinearRegression()으로 바꿔요.')
      .run('print(model.predict')
      .say('[40.0]이에요. 거리마다 10씩 느는 직선을 거리 4까지 이었어요.', 'output')
      .say('조심하세요. 직선은 배운 범위 밖으로도 계속 이어져요. 훈련에 없던 먼 거리는 결과를 따로 검토해요.', 'code:LinearRegression()'))

s3 = ('from sklearn.linear_model import LinearRegression\n\n' + PAIR + 'X_train = [[1], [2], [3]]\ny_train = [10, 20, 30]\nX_test = [[4]]\n'
      '# 새 객체를 만든 것과 학습한 것은 달라요.\nmodel = LinearRegression()\n'
      '# 이 자리에 fit 줄을 더해 훈련 입력과 정답으로 학습하세요.\nprint(model.predict(X_test).round(6).tolist())\n')
s3_sol = s3.replace('# 이 자리에 fit 줄을 더해 훈련 입력과 정답으로 학습하세요.\n',
                    '# 이 자리에 fit 줄을 더해 훈련 입력과 정답으로 학습하세요.\n# fit이 훈련 짝에서 기울기와 절편을 배워요. 그 뒤에야 predict를 쓸 수 있어요.\nmodel.fit(X_train, y_train)\n')
n3 = (Script(s3)
      .say('모델 객체만 만들고 바로 예측했어요. 예측 전에 fit 줄을 더해 훈련 입력과 정답으로 학습해야 해요.', 'text:print 줄 앞에 model.fit(X_train, y_train) 줄을 더해 훈련 입력과 정답으로 학습하세요.')
      .run('print(model.predict', error='NotFittedError')
      .say('NotFittedError예요. 아직 배운 기울기와 절편이 없어요.', 'output')
      .patch('print(model.predict', 'model.fit(X_train, y_train)\nprint(model.predict', 'print 줄 앞에 model.fit(X_train, y_train)을 써요.')
      .run('print(model.predict')
      .say('[40.0]이에요. 학습한 뒤에 새 거리 4를 예측했어요.', 'output')
      .say('조심하세요. LinearRegression()에 자료를 넣지 않아요. 자료는 fit에 넘겨요.', 'code:model.fit(X_train, y_train)'))

s4 = ('from sklearn.linear_model import LinearRegression\n\n' + PAIR + 'X_train = [[1], [2], [3]]\ny_train = [10, 20, 30]\n'
      '# 예측할 새 배송 하나의 거리예요.\ndistance = 4\n'
      '# 이 줄을 고쳐 distance를 한 행 한 열의 2차원 입력으로 만드세요.\nX_test = [distance]\n'
      'model = LinearRegression()\nmodel.fit(X_train, y_train)\nprint(model.predict(X_test).round(6).tolist())\n')
s4_sol = s4.replace('X_test = [distance]\n', '# 바깥 목록은 행(배송), 안쪽 목록은 특성 열이에요. 특성이 하나여도 2차원이에요.\nX_test = [[distance]]\n')
n4 = (Script(s4)
      .say('새 배송 하나를 넘겨요. X_test 줄을 고쳐 한 행 한 열의 2차원 입력으로 만들어야 해요.', 'text:X_test 줄을 고쳐 distance를 한 행 한 열의 2차원 입력으로 만드세요.')
      .run('print(model.predict', error='ValueError')
      .say('ValueError예요. [4]는 행과 열이 없는 1차원이라 몇 행인지 알 수 없어요.', 'output')
      .patch('X_test = [distance]\n', 'X_test = [[distance]]\n', '[distance]를 한 번 더 감싸 [[distance]]로 바꿔요.')
      .run('print(model.predict')
      .say('[40.0]이에요. 한 행의 예측 하나가 나왔어요.', 'output')
      .say('조심하세요. 훈련 입력과 예측 입력은 같은 열 구성의 2차원이어야 해요.', 'code:X_test = [[distance]]'))

s5 = ('from sklearn.linear_model import LinearRegression\n\n' + PAIR + 'X_train = [[1], [2], [3]]\ny_train = [15, 25, 35]\nX_test = [[4]]\n'
      'model = LinearRegression()\nmodel.fit(X_train, y_train)\n'
      '# 이 줄을 고쳐 기울기×거리에 절편을 더해 새 거리의 시간을 직접 계산하세요.\nmanual = model.coef_[0] * X_test[0][0]\n'
      'print(round(float(manual), 6))\nprint(model.predict(X_test).round(6).tolist())\n')
s5_sol = s5.replace('manual = model.coef_[0] * X_test[0][0]\n',
                    '# 직선의 값은 기울기×거리 + 절편이에요. 절편은 거리가 0일 때의 시작 위치예요.\nmanual = model.coef_[0] * X_test[0][0] + model.intercept_\n')
n5 = (Script(s5)
      .say('시간이 15·25·35로 바뀌었어요. manual 줄을 고쳐 기울기×거리에 절편을 더해 직접 계산해야 해요.', 'text:manual 줄을 고쳐 기울기×거리에 절편을 더해 새 거리의 시간을 직접 계산하세요.')
      .run('print(round(float(manual)', 'print(model.predict')
      .say('40.0과 [45.0]이에요. 기울기 10만 곱해서 모델의 예측과 5가 달라요.', 'output')
      .patch('manual = model.coef_[0] * X_test[0][0]\n', 'manual = model.coef_[0] * X_test[0][0] + model.intercept_\n', '뒤에 + model.intercept_를 더해요.')
      .run('print(round(float(manual)', 'print(model.predict')
      .say('45.0과 [45.0]이에요. 같은 기울기 10에 시작 위치 5가 더해졌어요.', 'output')
      .say('조심하세요. 기울기가 같아도 절편이 다르면 예측이 달라요. 계수만 보고 예측값을 말하지 않아요.', 'code:model.intercept_'))

s7 = ('from sklearn.linear_model import LinearRegression\n\n' + PAIR + 'X_train = [[1], [2]]\ny_train = [10, 20]\nX_test = [[3]]\n'
      '# 평가 정답은 학습에 넣지 않고 비교할 때만 사용해요.\ny_test = [100]\nmodel = LinearRegression()\nmodel.fit(X_train, y_train)\n'
      '# 이 줄을 고쳐 훈련이 아니라 남겨 둔 X_test의 예측과 y_test의 차이를 구하세요.\nerror = abs(model.predict(X_train) - y_train).max()\n'
      'print(model.predict(X_test).round(6).tolist())\nprint(round(float(error), 6))\n')
s7_sol = s7.replace('error = abs(model.predict(X_train) - y_train).max()\n',
                    '# 학습에 쓰지 않은 남겨 둔 배송에서 재야 새 배송에서의 오차를 알 수 있어요.\nerror = abs(model.predict(X_test) - y_test).max()\n')
n7 = (Script(s7)
      .say('훈련 자료는 직선이 다 맞혀요. error 줄을 고쳐 남겨 둔 배송의 예측과 실제의 차이를 구해야 해요.', 'text:error 줄을 고쳐 훈련이 아니라 남겨 둔 X_test의 예측과 y_test의 차이를 구하세요.')
      .run('print(model.predict(X_test)', 'print(round(float(error)')
      .say('[30.0]과 0.0이에요. 훈련 오차는 0이지만 남겨 둔 배송의 예측은 30이에요.', 'output')
      .patch('error = abs(model.predict(X_train) - y_train).max()\n', 'error = abs(model.predict(X_test) - y_test).max()\n', 'X_train, y_train을 X_test, y_test로 바꿔요.')
      .run('print(model.predict(X_test)', 'print(round(float(error)')
      .say('70.0이에요. 새 예측 30과 실제 100이 70 차이 나요.', 'output')
      .say('조심하세요. 훈련 자료를 잘 맞혀도 남겨 둔 자료는 다를 수 있어요. 평가는 학습에 안 쓴 자료로 해요.', 'code:model.predict(X_test) - y_test'))

SPECS = [
    code_step('stp_0b6a63f4-0ec1-4e1b-bc32-754f3a22ff69', 'strategy="mean"으로 평균 기준 모델을 만드세요', '입력을 보지 않고 훈련 정답의 평균을 내는 비교 기준을 만들어요.',
              'strategy="median"은 10·20·60의 중앙값 20을 낸다. strategy="mean"으로 고쳐 두 거리 모두 평균 30을 확인한다. 채점은 다른 훈련 시간으로 실행한다.',
              '`DummyRegressor`는 입력을 보지 않는 단순한 비교 기준이에요. `strategy="mean"`은 훈련 정답의 평균을, `strategy="median"`은 가운데 값을 모든 입력에 똑같이 예측해요.',
              'model 줄의 strategy를 고쳐 훈련 정답의 평균을 예측하는 기준 모델을 만드세요. 채점은 다른 시간으로도 실행해요.',
              ['코드 실행을 눌러 거리 4와 5의 예측을 확인하세요.', '`strategy="median"`을 `strategy="mean"`으로 고치세요.', '코드 실행을 눌러 예측이 평균인지 확인하세요.', SUBMIT],
              s1, s1_sol, n1, {n1.actions[-1]['text']: W},
              cases=[{'X_train': [[1], [2], [3], [4]], 'y_train': [4, 4, 8, 100]}, {'X_train': [[5], [9]], 'y_train': [7, 12]}],
              reject=[([['strategy="mean"', 'strategy="median"']], 'Median'),
                      ([['print(model.predict([[4], [5]]).round(6).tolist())', 'print([30.0, 30.0])']], 'Typing the predictions')],
              accept=[([['model = DummyRegressor(strategy="mean")', 'model = DummyRegressor()']], 'mean is the default')]),
    code_step('stp_159f4ebf-a230-454e-bf2d-afde5a20eb71', 'LinearRegression으로 거리에 따른 시간을 배우세요', '입력과 정답의 직선 관계를 배우는 모델로 새 입력을 예측해요.',
              '평균 기준 모델은 거리 4에도 평균 20이다. LinearRegression()으로 고쳐 10씩 느는 직선의 예측 40을 확인한다. 채점은 다른 직선 관계로 실행한다.',
              '이번 작은 표는 거리마다 시간이 10씩 늘어요. `LinearRegression`은 훈련 짝에서 기울기와 절편을 배워 새 거리의 시간을 직선 위의 값으로 예측해요.',
              'model 줄을 고쳐 거리에 따른 직선 관계를 배우는 LinearRegression을 쓰세요. 채점은 다른 관계로도 실행해요.',
              ['코드 실행을 눌러 거리 4의 예측을 확인하세요.', '`DummyRegressor(strategy="mean")`을 `LinearRegression()`으로 고치세요.', '코드 실행을 눌러 예측이 바뀌는지 확인하세요.', SUBMIT],
              s2, s2_sol, n2, {n2.actions[-1]['text']: W},
              cases=[{'y_train': [5, 7, 9], 'X_test': [[10]]}, {'X_train': [[0], [2], [4]], 'y_train': [3, 2, 1], 'X_test': [[1], [6]]}],
              reject=[([['model = LinearRegression()', 'model = DummyRegressor(strategy="mean")']], 'Mean baseline'),
                      ([['print(model.predict(X_test).round(6).tolist())', 'print([40.0])']], 'Typing the prediction')],
              accept=[([['model = LinearRegression()', 'model = LinearRegression(fit_intercept=True)']], 'Explicit intercept')]),
    code_step('stp_b5504e23-5059-4cd5-982a-7bd111334ddd', 'model.fit으로 학습한 뒤 예측하세요', '모델 객체 만들기와 훈련 자료로 학습하기를 구별해요.',
              '학습 전 predict는 NotFittedError다. print 앞에 model.fit(X_train, y_train)을 더해 예측 40을 확인한다. 채점은 다른 훈련 자료로 실행한다.',
              '`LinearRegression()`은 빈 모델 객체를 만들 뿐이에요. `model.fit(입력, 정답)`이 훈련 짝에서 기울기와 절편을 배우고, 그 뒤에야 `predict`로 새 입력을 예측할 수 있어요.',
              'print 줄 앞에 model.fit(X_train, y_train) 줄을 더해 훈련 입력과 정답으로 학습하세요. 채점은 다른 훈련 자료로도 실행해요.',
              ['코드 실행을 눌러 NotFittedError가 나오는지 확인하세요.', 'print 줄 앞에 `model.fit(X_train, y_train)`을 쓰세요.', '코드 실행을 눌러 예측을 확인하세요.', SUBMIT],
              s3, s3_sol, n3, {n3.actions[-1]['text']: W},
              cases=[{'X_train': [[0], [1]], 'y_train': [2, 5], 'X_test': [[3]]}, {'y_train': [9, 6, 3], 'X_test': [[0], [5]]}],
              reject=[([['model.fit(X_train, y_train)\n', 'model.fit(X_train, [10, 20, 30])\n']], 'Typing the targets'),
                      ([['model.fit(X_train, y_train)\n', 'model.fit(X_test, [40])\n']], 'Fitting on the question')],
              accept=[([['model = LinearRegression()', 'model = LinearRegression().fit(X_train, y_train)'], ['model.fit(X_train, y_train)\n', '']], 'Chained fit')]),
    code_step('stp_90fdca82-9335-4dc0-830f-bc26f72bbe8c', '[[distance]]로 한 행 한 열의 입력을 넘기세요', '특성이 하나여도 예측 입력은 행과 열의 2차원임을 지켜요.',
              '1차원 [distance]는 ValueError다. [[distance]]로 고쳐 한 행의 예측 40을 확인한다. 채점은 다른 거리와 관계로 실행한다.',
              'scikit-learn의 입력은 행(관측)과 열(특성)의 2차원이에요. 바깥 목록이 행, 안쪽 목록이 그 행의 특성 값이에요. 거리 하나뿐인 새 배송도 한 행 한 열이에요.',
              'X_test 줄을 고쳐 distance를 한 행 한 열의 2차원 입력으로 만드세요. 채점은 다른 거리로도 실행해요.',
              ['코드 실행을 눌러 ValueError가 나오는지 확인하세요.', '`X_test = [distance]`를 `X_test = [[distance]]`로 고치세요.', '코드 실행을 눌러 예측을 확인하세요.', SUBMIT],
              s4, s4_sol, n4, {n4.actions[-1]['text']: W},
              cases=[{'distance': 7}, {'distance': 0.5, 'y_train': [3, 1, -1]}],
              reject=[([['X_test = [[distance]]\n', 'X_test = [[4]]\n']], 'Typing the distance'),
                      ([['X_test = [[distance]]\n', 'X_test = [distance]\n']], 'One-dimensional')],
              accept=[([['X_test = [[distance]]\n', 'import numpy as np\nX_test = np.array([distance]).reshape(1, -1)\n']], 'reshape(1, -1)')]),
    code_step('stp_d43879ba-684e-4a8b-90b2-d43e5cbffa5c', 'intercept_를 더해 직선의 예측을 직접 계산하세요', '기울기가 같아도 절편이 예측을 바꾸는 것을 계산해 확인해요.',
              '기울기×거리만 계산하면 40으로 모델 예측 45와 다르다. + model.intercept_를 더해 45를 확인한다. 채점은 다른 관계와 거리로 실행한다.',
              '시간이 15·25·35로 바뀌었어요. 학습된 직선은 `model.coef_[0]`(기울기)과 `model.intercept_`(거리 0일 때의 절편)로 정해지고, 예측은 기울기×거리 + 절편이에요.',
              'manual 줄을 고쳐 기울기×거리에 절편을 더해 새 거리의 시간을 직접 계산하세요. 채점은 다른 관계로도 실행해요.',
              ['코드 실행을 눌러 manual과 모델 예측을 비교하세요.', 'manual 줄 끝에 `+ model.intercept_`를 더하세요.', '코드 실행을 눌러 두 값이 같은지 확인하세요.', SUBMIT],
              s5, s5_sol, n5, {n5.actions[-1]['text']: W},
              cases=[{'y_train': [-2, 1, 4], 'X_test': [[10]]}, {'X_train': [[0], [5]], 'y_train': [8, 3], 'X_test': [[2]]}],
              reject=[([['manual = model.coef_[0] * X_test[0][0] + model.intercept_\n', 'manual = model.coef_[0] * X_test[0][0]\n']], 'Slope only'),
                      ([['manual = model.coef_[0] * X_test[0][0] + model.intercept_\n', 'manual = 45\n']], 'Typing the prediction')],
              accept=[([['manual = model.coef_[0] * X_test[0][0] + model.intercept_\n', 'manual = model.intercept_ + X_test[0][0] * model.coef_[0]\n']], 'Intercept first')]),
    code_step('stp_592e9505-8588-475f-9584-2504f18fc201', 'X_test와 y_test로 남겨 둔 배송의 오차를 구하세요', '훈련 오차와 남겨 둔 자료의 오차를 구별해요.',
              '훈련 오차는 0이다. error를 X_test 예측과 y_test의 차이로 고쳐 남겨 둔 배송의 오차 70을 확인한다. 채점은 다른 평가 자료로 실행한다.',
              '남겨 둔 배송의 실제 시간은 100이에요. 학습에 쓴 자료의 오차는 그 자료를 얼마나 따라 했는지만 말해요. 새 배송에서의 오차는 학습에 쓰지 않은 `X_test`·`y_test`로 재요.',
              'error 줄을 고쳐 훈련이 아니라 남겨 둔 X_test의 예측과 y_test의 차이를 구하세요. 채점은 다른 평가 자료로도 실행해요.',
              ['코드 실행을 눌러 예측과 오차를 확인하세요.', 'error 줄의 `X_train`·`y_train`을 `X_test`·`y_test`로 고치세요.', '코드 실행을 눌러 남겨 둔 배송의 오차를 확인하세요.', SUBMIT],
              s7, s7_sol, n7, {n7.actions[-1]['text']: W},
              cases=[{'X_test': [[3], [5]], 'y_test': [31, 44]}, {'X_train': [[0], [4]], 'y_train': [1, 9], 'X_test': [[2]], 'y_test': [8]}],
              reject=[([['error = abs(model.predict(X_test) - y_test).max()\n', 'error = abs(model.predict(X_train) - y_train).max()\n']], 'Training error'),
                      ([['error = abs(model.predict(X_test) - y_test).max()\n', 'error = 70\n']], 'Typing the error')],
              accept=[([['error = abs(model.predict(X_test) - y_test).max()\n', 'from sklearn.metrics import max_error\nerror = max_error(y_test, model.predict(X_test))\n']], 'max_error')]),
]
