"""aice-boosting: 7 answer-picking steps -> coding steps (2026-10-29).

Each step trains a small XGBoost model with every default that differs between versions written out
(depth, regularisation, base score, seed, threads) and edits one line: the fit call, the model family,
the hand-computed shrunk step, the residuals the next tree learns, the probability column of a label,
the multi-class tree count and the best round read from the recorded validation history. Only APIs
shared by the exam-era 0.90 wrapper and current releases are used (fit/predict/predict_proba,
get_booster().get_dump(), evals_result). Prepared cases rerun with other targets, rates, labels and
rounds, so typed results and the starter's line fail."""
from _kit import Script, code_step

OPENING = ['이 수업에서는 XGBoost의 학습 흐름을 직접 코드로 확인해요. 학습률·반복수·평가기록의 역할을 구별해요.',
           '회귀와 분류를 실제로 실행해요. 한 단계의 반영과 잔차, 범주별 나무 수를 직접 계산해 비교해요.']
PRD_SCOPE = ['두 챕터·세 단원·아홉 스텝에서 같은 작은 배송 표를 학습해요.',
             'fit 호출·XGBRegressor·학습률로 줄인 한 단계·다음 나무의 잔차·encoder.classes_로 찾는 확률 열·범주별 나무 수·평가 기록의 최저 round를 한 곳씩 직접 고쳐 써요. 0.90과 현재 배포에 공통인 래퍼 호출만 써요.']
PRD_GRADING = ['직접 고친 코드를 실제 파이썬·XGBoost로 실행해 판정해요. 실행·해설만으로 성공시키지 않아요.',
               '실제 모델의 예측·dump 수·평가 기록을 다른 목표·학습률·범주·반복 수로 다시 실행해 기준 풀이와 비교해요. 결과를 글자로 적은 답, 학습률을 뺀 계산, 기준값에서 잰 잔차, 고정된 열 위치, round만 센 나무 수, 마지막 round를 최선으로 읽은 답은 거절해요.',
               '마지막 도전(stp_a5d75177-1ef8-4bf6-a518-1e1a0697176d): 실제 Python 실행과 다른 준비 자료의 결과를 검사해요. 시작 코드는 실패하고 동등한 풀이도 통과해야 해요.']
PRD_NARRATION = ['설정을 명시한 작은 CPU 모델에서 한 줄씩 고쳐 실제 예측과 기록을 비교해요.',
                 '생성과학습·목표종류·학습률·잔차·확률열·다중범주의나무수·평가와중단을 조심할 지점으로 짚어요.']

SUBMIT = '수정한 코드를 제출하세요.'
W = '실제 XGBoost 동작을 정확히 말해요.'
T = 45
HEAD = ('import numpy as np\nimport xgboost as xgb\n\n# 버전 기본값 차이를 피하려 작은 실험 설정을 명시해요.\n'
        'X_train = np.array([[0.0], [1.0], [2.0], [3.0]], dtype="float32")\ntimes = [2.0, 2.0, 8.0, 8.0]\ny_train = np.array(times, dtype="float32")\n')
FIXED = ('    # 아래 설정은 작은 표의 결과가 버전과 관계없이 같도록 고정해요.\n'
         '    min_child_weight=0, reg_lambda=0, random_state=0, n_jobs=1,\n    base_score=0.5, verbosity=0)\n')


def regressor(name='model', rounds='1', rate='1.0', family='XGBRegressor'):
    return f'{name} = xgb.{family}(\n    n_estimators={rounds},\n    max_depth=1,\n    learning_rate={rate},\n' + FIXED


PAIRS = [{'times': [10.0, 12.0, 2.0, 4.0]}, {'times': [-1.0, -3.0, 5.0, 9.0]}]

s1 = (HEAD + regressor() + '# 이 자리에 fit 줄을 더해 X_train과 y_train으로 학습하세요.\n'
      'print(model.get_params()["n_estimators"])\nprint(model.predict(X_train).tolist())\n')
s1_sol = s1.replace('# 이 자리에 fit 줄을 더해 X_train과 y_train으로 학습하세요.\n',
                    '# 이 자리에 fit 줄을 더해 X_train과 y_train으로 학습하세요.\n# 설정은 만들 때 정해지고, 자료의 관계는 fit에서 배워요.\nmodel.fit(X_train, y_train)\n')
n1 = (Script(s1)
      .say('모델을 만들고 설정만 정했어요. print 줄 앞에 fit 줄을 더해 자료로 학습해야 해요.', 'text:print 줄 앞에 model.fit(X_train, y_train) 줄을 더해 학습하세요.')
      .run('print(model.get_params', 'print(model.predict', error='NotFittedError')
      .say('설정 1은 읽히지만 예측에서 NotFittedError예요. 아직 학습한 나무가 없어요.', 'output')
      .patch('print(model.get_params', 'model.fit(X_train, y_train)\nprint(model.get_params', 'print 줄 앞에 model.fit(X_train, y_train)을 써요.')
      .run('print(model.get_params', 'print(model.predict')
      .say('1과 [2.0, 2.0, 8.0, 8.0]이에요. 나무 하나가 거리 1과 2 사이를 나눠 배웠어요.', 'output')
      .say('조심하세요. get_params로 설정을 읽을 수 있다고 학습된 건 아니에요.', 'code:model.fit(X_train, y_train)'))

s2 = (HEAD + '# 이 줄을 고쳐 배송 시간이라는 수치 목표를 예측하는 회귀 모델을 쓰세요.\n' + regressor(family='XGBClassifier')
      + 'model.fit(X_train, y_train)\nprint(model.predict(X_train).tolist())\n')
s2_sol = s2.replace('model = xgb.XGBClassifier(', '# 목표가 크기 있는 숫자면 Regressor예요. Classifier는 0부터 센 범주 번호를 받아요.\nmodel = xgb.XGBRegressor(')
n2 = (Script(s2)
      .say('목표는 2분과 8분 같은 배송 시간이에요. model 줄을 회귀 모델로 고쳐야 해요.', 'text:model 줄을 고쳐 배송 시간이라는 수치 목표를 예측하는 회귀 모델을 쓰세요.')
      .run('print(model.predict', error='ValueError')
      .say('ValueError예요. 분류기는 범주 번호 0과 1을 기대했는데 2와 8을 받았어요.', 'output')
      .patch('model = xgb.XGBClassifier(', 'model = xgb.XGBRegressor(', 'XGBClassifier를 XGBRegressor로 바꿔요.')
      .run('print(model.predict')
      .say('[2.0, 2.0, 8.0, 8.0]이에요. 시간 크기를 예측했어요.', 'output')
      .say('조심하세요. 예측값이 두 가지뿐이어도 목표가 시간이면 회귀예요. 값의 종류 수가 아니라 목표의 뜻으로 정해요.', 'code:xgb.XGBRegressor('))

s3 = (HEAD + '# 이번에 쓸 학습률이에요.\nrate = 0.5\n' + regressor(rate='rate') + 'model.fit(X_train, y_train)\n'
      '# 확인용 계산: 나무가 나눈 두 묶음(거리 0·1과 2·3)의 목표 평균이에요.\nleaf_means = [float(y_train[:2].mean()), float(y_train[2:].mean())]\n'
      '# 이 줄을 고쳐 기준값 0.5에 (묶음 평균 - 0.5)를 학습률만큼만 더하세요.\nexpected = [0.5 + (m - 0.5) for m in leaf_means]\n'
      'print([round(v, 4) for v in expected])\nprint(model.predict(np.array([[0.0], [3.0]], dtype="float32")).astype("float64").round(4).tolist())\n')
s3_sol = s3.replace('expected = [0.5 + (m - 0.5) for m in leaf_means]\n',
                    '# 첫 나무는 기준값과 목표의 차이를 배우고, 학습률은 그 차이를 얼마나 반영할지 정해요.\nexpected = [0.5 + rate * (m - 0.5) for m in leaf_means]\n')
n3 = (Script(s3)
      .say('학습률 0.5로 학습했어요. expected 줄을 고쳐 한 단계의 차이를 학습률만큼만 더해야 해요.', 'text:expected 줄을 고쳐 기준값 0.5에 (묶음 평균 - 0.5)를 학습률만큼만 더하세요.')
      .run('print([round(v', 'print(model.predict')
      .say('[2.0, 8.0]과 [1.25, 4.25]예요. 손 계산은 차이를 다 더해 모델과 달라요.', 'output')
      .patch('0.5 + (m - 0.5)', '0.5 + rate * (m - 0.5)', '(m - 0.5) 앞에 rate *를 붙여요.')
      .run('print([round(v', 'print(model.predict')
      .say('[1.25, 4.25]와 [1.25, 4.25]예요. 차이의 절반만 반영했어요.', 'output')
      .say('조심하세요. 학습률은 나무 수가 아니라 한 단계에서 반영하는 크기를 바꿔요.', 'code:rate * (m - 0.5)'))

s4 = (HEAD + 'rate = 0.5\n' + regressor('first', '1', 'rate') + regressor('second', '2', 'rate')
      + 'first.fit(X_train, y_train)\nsecond.fit(X_train, y_train)\npredicted = first.predict(X_train)\n'
      '# 이 줄을 고쳐 기준값 0.5가 아니라 첫 단계의 예측 predicted가 남긴 차이를 잔차로 구하세요.\nresiduals = y_train - 0.5\n'
      'print(residuals.astype("float64").round(4).tolist())\n# 둘째 나무는 잔차를 배워 학습률만큼 더해요.\nprint((predicted + rate * residuals).astype("float64").round(4).tolist())\nprint(second.predict(X_train).astype("float64").round(4).tolist())\n')
s4_sol = s4.replace('residuals = y_train - 0.5\n', '# 다음 나무가 줄일 차이는 지금까지의 예측이 남긴 차이(목표 − 예측)예요.\nresiduals = y_train - predicted\n')
n4 = (Script(s4)
      .say('둘째 나무는 남은 차이를 배워요. residuals 줄을 고쳐 첫 단계의 예측이 남긴 차이를 구해야 해요.', 'text:residuals 줄을 고쳐 기준값 0.5가 아니라 첫 단계의 예측 predicted가 남긴 차이를 잔차로 구하세요.')
      .run('print(residuals', 'print(second.predict')
      .say('잔차 [1.5, 1.5, 7.5, 7.5]로 더하면 [2.0, 2.0, 8.0, 8.0]인데 두 단계 모델은 [1.625, 1.625, 6.125, 6.125]예요.', 'output')
      .patch('residuals = y_train - 0.5\n', 'residuals = y_train - predicted\n', '0.5를 predicted로 바꿔요.')
      .run('print(residuals', 'print(second.predict')
      .say('잔차 [0.75, 0.75, 3.75, 3.75]로 더하니 두 단계 모델과 같아요. 예측이 2와 8에 더 가까워졌어요.', 'output')
      .say('조심하세요. 다음 나무는 처음 목표가 아니라 지금까지의 예측이 남긴 잔차를 배워요.', 'code:y_train - predicted'))

s5 = ('import numpy as np\nimport xgboost as xgb\nfrom sklearn.preprocessing import LabelEncoder\n\n# 문자 정답을 0부터 센 번호로 바꿔 넘겨요.\n'
      'X_train = np.array([[0.0], [1.0], [2.0], [3.0]], dtype="float32")\nlabels = ["on-time", "on-time", "late", "late"]\n'
      'encoder = LabelEncoder()\ny_train = encoder.fit_transform(labels)\n'
      + regressor(rounds='3', family='XGBClassifier') + 'model.fit(X_train, y_train)\nprint(encoder.classes_.tolist())\n'
      '# 이 줄을 고쳐 encoder.classes_에서 "late"가 있는 자리를 column에 담으세요.\ncolumn = 1\n'
      'print(model.predict_proba(X_train)[:, column].astype("float64").round(3).tolist())\n')
s5_sol = s5.replace('column = 1\n', '# 확률 열 순서는 학습에 넘긴 번호 순서이고, 그 번호는 encoder.classes_의 자리예요.\ncolumn = list(encoder.classes_).index("late")\n')
n5 = (Script(s5)
      .say('정답을 번호로 바꿔 학습했어요. column 줄을 고쳐 late의 번호를 encoder.classes_에서 찾아야 해요.', 'text:column 줄을 고쳐 encoder.classes_에서 "late"가 있는 자리를 column에 담으세요.')
      .run('print(encoder.classes_', 'print(model.predict_proba')
      .say('[\'late\', \'on-time\']이에요. 열 1은 on-time의 확률이라 앞의 두 배송이 높게 나왔어요.', 'output')
      .patch('column = 1\n', 'column = list(encoder.classes_).index("late")\n', '1 대신 list(encoder.classes_).index("late")를 써요.')
      .run('print(encoder.classes_', 'print(model.predict_proba')
      .say('뒤의 두 배송의 late 확률이 높아요. 거리 2와 3이 지연이었어요.', 'output')
      .say('조심하세요. 두 번째 열이 늘 관심 범주는 아니에요. 번호를 만든 encoder.classes_로 확인해요.', 'code:list(encoder.classes_).index("late")'))

s6 = ('import numpy as np\nimport xgboost as xgb\nfrom sklearn.preprocessing import LabelEncoder\n\n# 0부터 시작하는 정수 정답을 넘겨요.\n'
      'rows = [[0.0], [1.0], [4.0], [5.0], [8.0], [9.0]]\nlabels = ["normal", "normal", "late", "late", "cancelled", "cancelled"]\nrounds = 3\n'
      'X_train = np.array(rows, dtype="float32")\nencoder = LabelEncoder()\ny_train = encoder.fit_transform(labels)\n'
      + regressor(rounds='rounds', family='XGBClassifier').replace('    base_score=0.5, verbosity=0)\n', '    base_score=0.5, objective="multi:softprob", verbosity=0)\n')
      + 'model.fit(X_train, y_train)\nprint(encoder.classes_.tolist())\n'
      '# 이 줄을 고쳐 round마다 범주별로 하나씩 만드는 나무의 수를 trees에 담으세요.\ntrees = rounds\n'
      'print(trees)\nprint(len(model.get_booster().get_dump()))\n')
s6_sol = s6.replace('trees = rounds\n', '# 다중 분류는 round마다 범주의 수만큼 나무를 만들어요.\ntrees = rounds * len(encoder.classes_)\n')
n6 = (Script(s6)
      .say('세 범주를 세 round 학습했어요. trees 줄을 고쳐 범주별로 만드는 나무까지 세야 해요.', 'text:trees 줄을 고쳐 round마다 범주별로 하나씩 만드는 나무의 수를 trees에 담으세요.')
      .run('print(encoder.classes_', 'print(len(model.get_booster')
      .say('trees는 3인데 실제 나무는 9개예요.', 'output')
      .patch('trees = rounds\n', 'trees = rounds * len(encoder.classes_)\n', 'rounds에 len(encoder.classes_)를 곱해요.')
      .run('print(encoder.classes_', 'print(len(model.get_booster')
      .say('9와 9예요. round 셋마다 범주 셋의 나무를 하나씩 만들었어요.', 'output')
      .say('조심하세요. 다중 분류에서 n_estimators는 round 수예요. 실제 나무 수와 같지 않아요.', 'code:rounds * len(encoder.classes_)'))

s7 = (HEAD + regressor(rounds='3', rate='0.5') + '# 이 평가 표는 학습 정답에 합치지 않아요.\n'
      'X_valid = np.array([[0.25], [2.75]], dtype="float32")\nvalid_times = [2.0, 6.0]\ny_valid = np.array(valid_times, dtype="float32")\n'
      'model.fit(X_train, y_train, eval_set=[(X_valid, y_valid)], verbose=False)\n'
      'rmse = model.evals_result()["validation_0"]["rmse"]\nprint([round(v, 3) for v in rmse])\n'
      '# 이 줄을 고쳐 마지막 round가 아니라 검증 rmse가 가장 낮은 round(1부터 셈)를 best_round에 담으세요.\nbest_round = len(rmse)\n'
      'print(best_round)\nprint(len(model.get_booster().get_dump()))\n')
s7_sol = s7.replace('best_round = len(rmse)\n', '# eval_set은 round마다 점수를 기록만 해요. 가장 좋은 round는 기록에서 직접 찾아요.\nbest_round = rmse.index(min(rmse)) + 1\n')
n7 = (Script(s7)
      .say('eval_set으로 검증 점수를 기록했어요. best_round 줄을 고쳐 rmse가 가장 낮은 round를 찾아야 해요.', 'text:best_round 줄을 고쳐 마지막 round가 아니라 검증 rmse가 가장 낮은 round(1부터 셈)를 best_round에 담으세요.')
      .run('print([round(v', 'print(len(model.get_booster')
      .say('rmse는 둘째 round에서 가장 낮고 셋째에 다시 올랐어요. 그래도 best_round는 3이고 나무도 3개예요.', 'output')
      .patch('best_round = len(rmse)\n', 'best_round = rmse.index(min(rmse)) + 1\n', 'rmse.index(min(rmse)) + 1로 바꿔요.')
      .run('print([round(v', 'print(len(model.get_booster')
      .say('2예요. 나무는 여전히 3개라 평가가 나빠져도 학습은 멈추지 않았어요.', 'output')
      .say('조심하세요. 평가 표를 준 것만으로 자동 중단되지 않아요. 기록과 조기중단 설정은 별개예요.', 'code:rmse.index(min(rmse))'))

SPECS = [
    code_step('stp_bb2c83e6-1ccf-45a9-b620-77ad97a30b81', 'model.fit으로 XGBoost를 학습하세요', '모델 생성·설정과 자료로 학습하기를 구별해요.',
              '설정만 정한 모델의 predict는 NotFittedError다. print 앞에 model.fit(X_train, y_train)을 더해 학습된 예측을 확인한다. 채점은 다른 목표로 실행한다.',
              '`xgb.XGBRegressor(...)`는 설정을 정한 모델 객체를 만들 뿐이에요. 자료의 관계는 `model.fit(입력, 정답)`에서 나무를 만들며 배우고, 그 뒤에야 `predict`를 쓸 수 있어요.',
              'print 줄 앞에 model.fit(X_train, y_train) 줄을 더해 학습하세요. 채점은 다른 목표로도 실행해요.',
              ['코드 실행을 눌러 NotFittedError가 나오는지 확인하세요.', 'print 줄 앞에 `model.fit(X_train, y_train)`을 쓰세요.', '코드 실행을 눌러 예측을 확인하세요.', SUBMIT],
              s1, s1_sol, n1, {n1.actions[-1]['text']: W}, cases=PAIRS,
              reject=[([['model.fit(X_train, y_train)\n', 'model.fit(X_train, np.array([2.0, 2.0, 8.0, 8.0], dtype="float32"))\n']], 'Typing the targets'),
                      ([['print(model.predict(X_train).tolist())', 'print([2.0, 2.0, 8.0, 8.0])']], 'Typing the predictions')],
              accept=[([['model.fit(X_train, y_train)\n', 'model = model.fit(X_train, y_train)\n']], 'fit returns the model')], timeout=T),
    code_step('stp_bcf6b46c-2213-4a68-863a-818c760abcd1', 'XGBRegressor로 배송 시간을 예측하세요', '목표의 뜻으로 회귀와 분류 모델을 골라요.',
              'XGBClassifier는 범주 번호가 아닌 2·8에서 ValueError다. XGBRegressor로 고쳐 시간 예측 [2.0, 2.0, 8.0, 8.0]을 확인한다. 채점은 다른 시간으로 실행한다.',
              '이번 목표는 배송 시간이라는 수치예요. `XGBRegressor`는 크기 있는 숫자를, `XGBClassifier`는 0부터 센 범주 번호를 예측해요.',
              'model 줄을 고쳐 배송 시간이라는 수치 목표를 예측하는 회귀 모델을 쓰세요. 채점은 다른 시간으로도 실행해요.',
              ['코드 실행을 눌러 ValueError가 나오는지 확인하세요.', '`xgb.XGBClassifier(`를 `xgb.XGBRegressor(`로 고치세요.', '코드 실행을 눌러 예측한 시간을 확인하세요.', SUBMIT],
              s2, s2_sol, n2, {n2.actions[-1]['text']: W}, cases=PAIRS,
              reject=[([['model = xgb.XGBRegressor(', 'model = xgb.XGBClassifier(']], 'Classifier'),
                      ([['print(model.predict(X_train).tolist())', 'print(y_train.tolist())']], 'Printing the targets')],
              accept=[([['model = xgb.XGBRegressor(', 'model = xgb.XGBRegressor(objective="reg:squarederror",']], 'Explicit squared error')], timeout=T),
    code_step('stp_87819b82-e4bd-46e6-8329-1ffd14689cd5', 'rate를 곱해 한 단계의 반영 크기를 계산하세요', '학습률이 한 단계에서 반영하는 차이의 크기를 계산해 확인해요.',
              '차이를 모두 더하면 [2.0, 8.0]으로 학습률 0.5 모델의 [1.25, 4.25]와 다르다. rate * (m - 0.5)로 고쳐 같은 값을 확인한다. 채점은 다른 학습률과 목표로 실행한다.',
              '첫 나무는 기준값 0.5와 각 묶음 목표의 차이를 배워요. 학습률(`learning_rate`)은 그 차이를 이번 단계에 얼마나 반영할지 곱하는 비율이에요. 그래서 한 단계의 예측은 0.5 + 학습률 × (묶음 평균 − 0.5)예요.',
              'expected 줄을 고쳐 기준값 0.5에 (묶음 평균 - 0.5)를 학습률만큼만 더하세요. 채점은 다른 학습률로도 실행해요.',
              ['코드 실행을 눌러 손 계산과 모델 예측을 비교하세요.', '`(m - 0.5)` 앞에 `rate *`를 붙이세요.', '코드 실행을 눌러 두 값이 같은지 확인하세요.', SUBMIT],
              s3, s3_sol, n3, {n3.actions[-1]['text']: W},
              cases=[{'rate': 0.25, 'times': [10.0, 12.0, 2.0, 4.0]}, {'rate': 0.8, 'times': [-1.0, -3.0, 5.0, 9.0]}],
              reject=[([['0.5 + rate * (m - 0.5)', '0.5 + (m - 0.5)']], 'Whole difference'),
                      ([['0.5 + rate * (m - 0.5)', '0.5 + 0.5 * (m - 0.5)']], 'Typing 0.5 as the rate')],
              accept=[([['expected = [0.5 + rate * (m - 0.5) for m in leaf_means]\n', 'expected = [(1 - rate) * 0.5 + rate * m for m in leaf_means]\n']], 'Weighted form')], timeout=T),
    code_step('stp_9b3d3c93-9e9b-455e-8c38-1e837d4502e1', 'predicted로 다음 나무가 배울 잔차를 구하세요', '부스팅이 앞 단계의 예측이 남긴 잔차를 차례로 줄이는 것을 계산해 확인해요.',
              '기준값 0.5에서 잰 잔차로 더하면 두 단계 모델 [1.625, 6.125]와 다르다. y_train - predicted로 고쳐 같은 예측을 확인한다. 채점은 다른 학습률과 목표로 실행한다.',
              '부스팅은 나무를 차례로 더해요. 다음 나무는 앞 단계까지의 예측이 남긴 차이(잔차, 목표 − 예측)를 배우고, 그 값을 학습률만큼 더해요. `predicted`는 첫 단계 모델의 예측이에요.',
              'residuals 줄을 고쳐 기준값 0.5가 아니라 첫 단계의 예측 predicted가 남긴 차이를 잔차로 구하세요. 채점은 다른 학습률로도 실행해요.',
              ['코드 실행을 눌러 잔차와 두 예측을 비교하세요.', '`y_train - 0.5`를 `y_train - predicted`로 고치세요.', '코드 실행을 눌러 두 예측이 같은지 확인하세요.', SUBMIT],
              s4, s4_sol, n4, {n4.actions[-1]['text']: W},
              cases=[{'rate': 0.25, 'times': [10.0, 10.0, 2.0, 2.0]}, {'rate': 0.6, 'times': [-3.0, -3.0, 9.0, 9.0]}],
              reject=[([['residuals = y_train - predicted\n', 'residuals = y_train - 0.5\n']], 'Residuals from the base score'),
                      ([['residuals = y_train - predicted\n', 'residuals = y_train - y_train.mean()\n']], 'Residuals from the mean')],
              accept=[([['residuals = y_train - predicted\n', 'residuals = np.subtract(y_train, first.predict(X_train))\n']], 'np.subtract')], timeout=T),
    code_step('stp_dba36fc9-edb8-4db0-b42a-bc388ca26759', 'encoder.classes_로 "late" 확률의 열을 찾으세요', '확률 열의 순서를 번호를 만든 encoder.classes_로 맞춰요.',
              '열 1은 on-time의 확률이다. list(encoder.classes_).index("late")로 고쳐 late의 확률 열을 확인한다. 채점은 범주 이름이 다른 자료로 실행한다.',
              'XGBClassifier는 0부터 센 범주 번호를 받아서, 문자 정답은 `LabelEncoder`로 번호를 만들어 넘겨요. `encoder.classes_`의 자리가 그 번호이고, `predict_proba`의 열도 같은 번호 순서예요.',
              'column 줄을 고쳐 encoder.classes_에서 "late"가 있는 자리를 column에 담으세요. 채점은 다른 범주 이름으로도 실행해요.',
              ['코드 실행을 눌러 classes_와 확률을 확인하세요.', '`column = 1`을 `column = list(encoder.classes_).index("late")`로 고치세요.', '코드 실행을 눌러 late의 확률을 확인하세요.', SUBMIT],
              s5, s5_sol, n5, {n5.actions[-1]['text']: W},
              cases=[{'labels': ['early', 'early', 'late', 'late']}, {'labels': ['late', 'ok', 'ok', 'ok']}],
              reject=[([['column = list(encoder.classes_).index("late")\n', 'column = 1\n']], 'Second column'),
                      ([['column = list(encoder.classes_).index("late")\n', 'column = 0\n']], 'First column')],
              accept=[([['column = list(encoder.classes_).index("late")\n', 'column = int(encoder.transform(["late"])[0])\n']], 'encoder.transform')], timeout=T),
    code_step('stp_a4c4c921-a9eb-4805-9761-71f28cee2b6a', 'rounds * len(encoder.classes_)로 나무 수를 세세요', '다중 분류에서 round 수와 실제 나무 수를 구별해요.',
              'trees = rounds는 3인데 실제 dump는 9개다. rounds * len(encoder.classes_)로 고쳐 9를 확인한다. 채점은 범주 수와 round가 다른 자료로 실행한다.',
              '세 범주를 세 round 학습했어요. 다중 분류(`multi:softprob`)에서는 round마다 범주별로 나무를 하나씩 만들어요. `get_booster().get_dump()`는 실제 나무 목록이에요.',
              'trees 줄을 고쳐 round마다 범주별로 하나씩 만드는 나무의 수를 trees에 담으세요. 채점은 다른 범주 수로도 실행해요.',
              ['코드 실행을 눌러 trees와 실제 나무 수를 비교하세요.', '`trees = rounds`를 `trees = rounds * len(encoder.classes_)`로 고치세요.', '코드 실행을 눌러 두 값이 같은지 확인하세요.', SUBMIT],
              s6, s6_sol, n6, {n6.actions[-1]['text']: W},
              cases=[{'rounds': 2, 'rows': [[0.0], [1.0], [4.0], [5.0], [8.0], [9.0], [12.0], [13.0]], 'labels': ['a', 'a', 'b', 'b', 'c', 'c', 'd', 'd']},
                     {'rounds': 4, 'rows': [[0.0], [1.0], [5.0], [6.0], [9.0], [10.0]], 'labels': ['z', 'z', 'x', 'x', 'y', 'y']}],
              reject=[([['trees = rounds * len(encoder.classes_)\n', 'trees = rounds\n']], 'Rounds only'),
                      ([['trees = rounds * len(encoder.classes_)\n', 'trees = rounds * 3\n']], 'Typing three classes')],
              accept=[([['trees = rounds * len(encoder.classes_)\n', 'trees = rounds * len(set(labels))\n']], 'Distinct labels')], timeout=T),
    code_step('stp_5112d317-54df-45bd-a2ab-80ca1599b3e1', 'rmse 기록에서 가장 낮은 round를 찾으세요', '평가 기록과 조기중단을 구별하고 기록에서 가장 좋은 round를 찾아요.',
              'eval_set만 주면 rmse를 기록하고 세 round를 모두 학습해 best_round도 3이다. rmse.index(min(rmse)) + 1로 고쳐 2를 확인한다. 나무는 여전히 3개다. 채점은 다른 검증 자료로 실행한다.',
              '`fit(..., eval_set=[(X_valid, y_valid)])`은 round마다 검증 rmse를 기록만 해요. 평가가 나빠져도 조기중단 설정 없이는 학습을 멈추지 않아요. 기록은 `model.evals_result()["validation_0"]["rmse"]`에 round 순서로 들어 있어요.',
              'best_round 줄을 고쳐 마지막 round가 아니라 검증 rmse가 가장 낮은 round(1부터 셈)를 best_round에 담으세요. 채점은 다른 검증 자료로도 실행해요.',
              ['코드 실행을 눌러 기록과 best_round를 확인하세요.', '`len(rmse)`를 `rmse.index(min(rmse)) + 1`로 고치세요.', '코드 실행을 눌러 best_round와 나무 수를 확인하세요.', SUBMIT],
              s7, s7_sol, n7, {n7.actions[-1]['text']: W},
              cases=[{'valid_times': [1.0, 4.0]}, {'valid_times': [2.0, 8.0]}],
              reject=[([['best_round = rmse.index(min(rmse)) + 1\n', 'best_round = len(rmse)\n']], 'Last round'),
                      ([['best_round = rmse.index(min(rmse)) + 1\n', 'best_round = 2\n']], 'Typing the round')],
              accept=[([['best_round = rmse.index(min(rmse)) + 1\n', 'best_round = min(range(1, len(rmse) + 1), key=lambda r: rmse[r - 1])\n']], 'min over rounds')], timeout=T),
]
