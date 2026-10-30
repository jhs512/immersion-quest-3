"""aice-models: 6 answer-picking steps -> coding steps (2026-10-29).

Step 7 (큰 중요도만으로 현실의 원인이라 할까) stays a choice: it asks for an interpretation, not code.
Converted steps train real scikit-learn models on small deterministic data (fixed random_state, n_jobs=1)
and print learned structure or predictions; prepared cases rerun with other data, so typed results and
the starter's setting fail."""
from _kit import Script, code_step

OPENING = ['이 수업에서는 모델의 설정과 학습 결과를 직접 코드로 구별해요. 목표와 자료에 맞는 후보를 판단해요.',
           '트리와 포레스트의 동작을 실행해 살펴봐요. 훈련 점수와 특성 중요도가 뜻하는 범위도 확인해요.']
PRD_SCOPE = ['두 챕터·두 단원·아홉 스텝에서 같은 배송 모델의 후보를 비교해요.',
             '깊이 상한·실제 나무 수·회귀/분류 포레스트·스케일 뒤 KNN·SVC 결정 점수·검증 점수로 고르기를 한 곳씩 직접 고쳐 써요. 중요도와 인과의 구별은 선택 문항으로 남겨요.']
PRD_GRADING = ['직접 고친 코드를 실제 파이썬·scikit-learn으로 실행해 판정해요. 실행·해설만으로 성공시키지 않아요.',
               '실제 학습된 나무 수와 새 예측을 여러 설정·입력으로 검사해요. 준비 자료를 바꿔 다시 실행해 기준 풀이와 비교하고, 결과를 글자로 적은 답과 훈련 점수로 고른 답은 거절해요. 난수는 random_state로 고정해요.',
               '마지막 도전(stp_8f1aa06f-612a-433b-986b-d09b20cc2c46): 실제 Python 실행과 다른 준비 자료의 결과를 검사해요. 시작 코드는 실패하고 동등한 풀이도 통과해야 해요.']
PRD_NARRATION = ['같은 상황에서 모델·설정 한 곳씩 고쳐 비교해요.',
                 '깊이상한·나무수·목표종류·스케일·결정점수·훈련점수·인과를 조심할 지점으로 짚어요.']

SUBMIT = '수정한 코드를 제출하세요.'
W = '실제 scikit-learn 동작을 정확히 말해요.'

s1 = ('from sklearn.tree import DecisionTreeClassifier\n\n# 배송 거리와 정상0·지연1이에요. 거리 3만 정답이 튀어 있어요.\n'
      'X_train = [[1], [2], [3], [8], [9]]\ny_train = [0, 0, 1, 0, 1]\n'
      '# 이 줄의 설정을 고쳐 학습된 나무의 깊이가 1을 넘지 않게 하세요.\nmodel = DecisionTreeClassifier(max_depth=None, random_state=0)\nmodel.fit(X_train, y_train)\n'
      'print(model.get_params()["max_depth"])\nprint(model.get_depth())\n')
s1_sol = s1.replace('max_depth=None', 'max_depth=1').replace('# 이 줄의 설정을 고쳐 학습된 나무의 깊이가 1을 넘지 않게 하세요.\n',
                                                         '# 이 줄의 설정을 고쳐 학습된 나무의 깊이가 1을 넘지 않게 하세요.\n# max_depth는 학습 전에 정하는 깊이의 상한이에요. 실제 깊이는 자료에 따라 그보다 얕을 수 있어요.\n')
n1 = (Script(s1)
      .say('max_depth는 학습 전에 정하는 깊이의 상한이에요. 깊이가 1을 넘지 않게 설정을 고쳐야 해요.', 'text:model 줄의 설정을 고쳐 학습된 나무의 깊이가 1을 넘지 않게 하세요.')
      .run('print(model.get_params', 'print(model.get_depth')
      .say('None과 3이에요. 상한이 없어 튀는 정답까지 나누느라 세 번 내려갔어요.', 'output')
      .patch('max_depth=None', 'max_depth=1', 'max_depth를 1로 바꿔요.')
      .run('print(model.get_params', 'print(model.get_depth')
      .say('1과 1이에요. 학습된 나무가 질문을 한 번만 했어요.', 'output')
      .say('조심하세요. 상한은 약속한 최대일 뿐이에요. 정답이 모두 같으면 깊이 0인 나무도 나와요.', 'code:max_depth=1'))

s2 = ('from sklearn.ensemble import RandomForestClassifier\n\n# 같은 배송 거리와 정상0·지연1을 준비해요.\nX_train = [[1], [2], [8], [9]]\ny_train = [0, 0, 1, 1]\nX_test = [[1], [9]]\n'
      'tree_count = 3\n# 작은 비교를 위해 나무 수·깊이·난수·실행 수를 명시해요.\nmodel = RandomForestClassifier(n_estimators=tree_count, max_depth=1, random_state=0, n_jobs=1)\nmodel.fit(X_train, y_train)\n'
      '# 이 줄을 고쳐 깊이가 아니라 실제로 학습된 나무의 수를 trees에 담으세요.\ntrees = model.max_depth\nprint(trees)\nprint(model.predict(X_test).tolist())\n')
s2_sol = s2.replace('trees = model.max_depth\n', '# estimators_는 학습된 나무들의 목록이에요. 그 길이가 실제 나무 수예요.\ntrees = len(model.estimators_)\n')
n2 = (Script(s2)
      .say('n_estimators=tree_count로 학습했어요. 실제로 학습된 나무의 수를 세도록 trees 줄을 고쳐야 해요.', 'text:trees 줄을 고쳐 깊이가 아니라 실제로 학습된 나무의 수를 trees에 담으세요.')
      .run('print(trees)', 'print(model.predict')
      .say('1과 [0, 1]이에요. 1은 나무 하나의 깊이 상한이에요.', 'output')
      .patch('trees = model.max_depth\n', 'trees = len(model.estimators_)\n', 'len(model.estimators_)로 학습된 나무를 세요.')
      .run('print(trees)', 'print(model.predict')
      .say('3이에요. 깊이 1인 나무 세 개가 판단을 모아 예측해요.', 'output')
      .say('조심하세요. max_depth는 나무 하나의 깊이고, 나무의 개수는 n_estimators예요.', 'code:len(model.estimators_)'))

s3 = ('from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier\n\n# 이번 목표는 종류가 아니라 연속적인 배송 시간이에요.\nX_train = [[0], [1]]\ny_train = [0.5, 1.5]\n'
      '# 이 줄을 고쳐 연속적인 시간을 예측하는 포레스트를 쓰세요.\nmodel = RandomForestClassifier(n_estimators=3, bootstrap=False, random_state=0, n_jobs=1)\nmodel.fit(X_train, y_train)\nprint(model.predict(X_train).tolist())\n')
s3_sol = s3.replace('model = RandomForestClassifier(', '# 숫자 크기 자체를 맞히는 목표는 Regressor예요. Classifier는 정해진 종류를 골라요.\nmodel = RandomForestRegressor(')
n3 = (Script(s3)
      .say('목표가 0.5분과 1.5분인 연속 시간이에요. 종류를 고르는 Classifier를 Regressor로 고쳐야 해요.', 'text:model 줄을 고쳐 연속적인 시간을 예측하는 포레스트를 쓰세요.')
      .run('print(model.predict', error='ValueError')
      .say('ValueError예요. Classifier는 0.5 같은 연속 값을 종류로 다룰 수 없어요.', 'output')
      .patch('model = RandomForestClassifier(', 'model = RandomForestRegressor(', 'RandomForestRegressor로 바꿔요.')
      .run('print(model.predict')
      .say('[0.5, 1.5]예요. 시간 크기 자체를 예측했어요.', 'output')
      .say('조심하세요. 정답이 숫자라고 모두 회귀는 아니에요. 0과 1처럼 종류를 뜻하면 분류예요.', 'code:RandomForestRegressor('))

s4 = ('from sklearn.neighbors import KNeighborsClassifier\nfrom sklearn.preprocessing import StandardScaler\nfrom sklearn.pipeline import make_pipeline\n\n'
      '# 두 특성의 숫자 단위가 크게 다른 작은 예예요.\nX_train = [[0, 0], [1, 1000]]\ny_train = [0, 1]\nX_test = [[0.9, 400]]\n'
      '# 이 줄을 고쳐 훈련 기준으로 표준화한 뒤 가장 가까운 이웃 하나를 따르게 하세요.\nmodel = KNeighborsClassifier(n_neighbors=1)\nmodel.fit(X_train, y_train)\nprint(model.predict(X_test).tolist())\n')
s4_sol = s4.replace('model = KNeighborsClassifier(n_neighbors=1)', '# 거리를 재기 전에 특성마다 훈련 기준으로 표준화해 단위의 영향을 맞춰요.\nmodel = make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=1))')
n4 = (Script(s4)
      .say('KNN은 특성 값의 거리로 가까운 이웃을 찾아요. 표준화한 뒤 이웃을 찾도록 model 줄을 고쳐야 해요.', 'text:model 줄을 고쳐 훈련 기준으로 표준화한 뒤 가장 가까운 이웃 하나를 따르게 하세요.')
      .run('print(model.predict')
      .say('[0]이에요. 둘째 특성의 큰 단위 때문에 400이 1000보다 0에 가깝다고 판단했어요.', 'output')
      .patch('model = KNeighborsClassifier(n_neighbors=1)', 'model = make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=1))', 'make_pipeline으로 StandardScaler 다음에 KNN을 둬요.')
      .run('print(model.predict')
      .say('[1]이에요. 단위를 맞추니 첫 특성 0.9가 1에 가까운 것이 반영됐어요.', 'output')
      .say('조심하세요. 거리 모델은 단위가 큰 특성이 거리를 거의 다 정해요. 스케일 기준은 훈련에서 배워요.', 'code:StandardScaler()'))

s5 = ('from sklearn.svm import SVC\n\n# 같은 배송 거리와 정상0·지연1을 준비해요.\nX_train = [[1], [2], [8], [9]]\ny_train = [0, 0, 1, 1]\nX_test = [[1], [9]]\n'
      'model = SVC(kernel="linear")\nmodel.fit(X_train, y_train)\nprint(model.predict(X_test).tolist())\n'
      '# 이 줄을 고쳐 확률 대신 경계선까지의 결정 점수를 scores에 담으세요.\nscores = model.predict_proba(X_test)\nprint(scores.round(3).tolist())\n')
s5_sol = s5.replace('scores = model.predict_proba(X_test)', '# 기본 SVC는 확률을 주지 않아요. decision_function은 경계선의 어느 쪽에 얼마나 떨어졌는지예요.\nscores = model.decision_function(X_test)')
n5 = (Script(s5)
      .say('SVC는 두 종류 사이에 경계선을 그어요. 확률 대신 결정 점수를 담도록 scores 줄을 고쳐야 해요.', 'text:scores 줄을 고쳐 확률 대신 경계선까지의 결정 점수를 scores에 담으세요.')
      .run('print(model.predict', 'print(scores', error='AttributeError')
      .say('[0, 1] 뒤에 AttributeError예요. 기본 SVC에는 확률을 주는 predict_proba가 없어요.', 'output')
      .patch('scores = model.predict_proba(X_test)', 'scores = model.decision_function(X_test)', 'decision_function으로 바꿔요.')
      .run('print(model.predict', 'print(scores')
      .say('[-1.333, 1.333]이에요. 음수는 정상 쪽, 양수는 지연 쪽으로 경계선에서 떨어진 정도예요.', 'output')
      .say('조심하세요. 결정 점수는 0에서 1 사이의 확률이 아니에요. 크기를 확률로 읽지 않아요.', 'code:decision_function'))

s6 = ('from sklearn.tree import DecisionTreeClassifier\n\n# 거리 3인 배송 하나만 정답이 튀어 있는 훈련 표예요.\nX_train = [[1], [2], [3], [4], [6], [7], [8], [9]]\ny_train = [0, 0, 1, 0, 1, 1, 1, 1]\n'
      '# 두 후보를 같은 검증 자료로 비교해요.\nX_valid = [[2.8], [3.2], [6.8], [7.2]]\ny_valid = [0, 0, 1, 1]\n'
      'deep = DecisionTreeClassifier(random_state=0)\nshallow = DecisionTreeClassifier(max_depth=1, random_state=0)\ndeep.fit(X_train, y_train)\nshallow.fit(X_train, y_train)\n'
      'print(float(deep.score(X_train, y_train)), float(shallow.score(X_train, y_train)))\nprint(float(deep.score(X_valid, y_valid)), float(shallow.score(X_valid, y_valid)))\n'
      '# 이 줄을 고쳐 훈련이 아니라 같은 검증 자료의 정확도로 후보를 고르세요.\nchosen = "deep" if deep.score(X_train, y_train) >= shallow.score(X_train, y_train) else "shallow"\nprint(chosen)\n')
s6_sol = s6.replace('chosen = "deep" if deep.score(X_train, y_train) >= shallow.score(X_train, y_train) else "shallow"',
                    '# 새 배송에 쓸 모델은 학습에 쓰지 않은 검증 자료의 점수로 골라요.\nchosen = "deep" if deep.score(X_valid, y_valid) >= shallow.score(X_valid, y_valid) else "shallow"')
n6 = (Script(s6)
      .say('두 후보를 같은 검증 자료로 비교해 고르려 해요. 훈련 정확도로 고르는 chosen 줄을 고쳐야 해요.', 'text:chosen 줄을 고쳐 훈련이 아니라 같은 검증 자료의 정확도로 후보를 고르세요.')
      .run('print(float(deep.score(X_train', 'print(chosen)')
      .say('훈련은 1.0과 0.875, 검증은 0.5와 1.0이고 deep을 골랐어요. 튀는 정답까지 외운 훈련 점수로 골랐어요.', 'output')
      .patch('deep.score(X_train, y_train) >= shallow.score(X_train, y_train) else', 'deep.score(X_valid, y_valid) >= shallow.score(X_valid, y_valid) else', 'X_train, y_train을 X_valid, y_valid로 바꿔요.')
      .run('print(float(deep.score(X_train', 'print(chosen)')
      .say('shallow예요. 학습에 쓰지 않은 검증 자료에서 더 잘 맞았어요.', 'output')
      .say('조심하세요. 훈련 점수가 높다고 새 배송도 잘 맞히는 건 아니에요.', 'code:deep.score(X_valid, y_valid) >='))

SPECS = [
    code_step('stp_506b5b9b-6de5-4103-9815-4340d4798cc5', 'max_depth=1로 나무 깊이의 상한을 정하세요', '학습 전 설정인 깊이 상한과 학습된 실제 깊이를 구별해요.',
              'max_depth=None은 튀는 정답 때문에 깊이 3인 나무를 만든다. max_depth=1로 고쳐 설정 1과 실제 깊이 1을 확인한다. 채점은 정답이 모두 같아 깊이 0이 되는 자료 등으로 실행한다.',
              '`max_depth`는 학습 전에 정하는 분기 깊이의 상한이에요. `get_params()["max_depth"]`는 설정값, `get_depth()`는 학습된 나무의 실제 깊이예요.',
              'model 줄의 설정을 고쳐 학습된 나무의 깊이가 1을 넘지 않게 하세요. 채점은 다른 자료로도 실행해요.',
              ['코드 실행을 눌러 설정과 실제 깊이를 확인하세요.', '`max_depth=None`을 `max_depth=1`로 고치세요.', '코드 실행을 눌러 두 값을 다시 확인하세요.', SUBMIT],
              s1, s1_sol, n1, {n1.actions[-1]['text']: W},
              cases=[{'X_train': [[1], [2], [3]], 'y_train': [1, 1, 1]}, {'X_train': [[5], [1], [9], [3], [7]], 'y_train': [1, 0, 0, 1, 0]}],
              reject=[([['max_depth=1, random_state=0)', 'max_depth=2, random_state=0)']], 'Depth two'),
                      ([['print(model.get_depth())', 'print(1)']], 'Typing the depth')],
              accept=[([['model = DecisionTreeClassifier(max_depth=1, random_state=0)', 'model = DecisionTreeClassifier(random_state=0)\nmodel.set_params(max_depth=1)']], 'set_params')]),
    code_step('stp_44197264-1b07-443a-b046-dd07509369ac', 'len(model.estimators_)로 실제 나무 수를 세세요', '포레스트의 나무 수와 나무 하나의 깊이를 구별해요.',
              'model.max_depth는 나무 하나의 깊이 1이다. len(model.estimators_)로 고쳐 실제 학습된 나무 3개를 확인한다. 채점은 tree_count가 다른 자료로 실행한다.',
              '포레스트는 여러 나무의 판단을 모아요. `n_estimators`는 학습할 나무의 수이고, 학습된 나무들은 `model.estimators_` 목록에 들어 있어요. `max_depth`는 나무 하나의 깊이예요.',
              'trees 줄을 고쳐 깊이가 아니라 실제로 학습된 나무의 수를 trees에 담으세요. 채점은 tree_count가 다른 자료로도 실행해요.',
              ['코드 실행을 눌러 trees를 확인하세요.', '`model.max_depth`를 `len(model.estimators_)`로 고치세요.', '코드 실행을 눌러 나무 수를 확인하세요.', SUBMIT],
              s2, s2_sol, n2, {n2.actions[-1]['text']: W}, cases=[{'tree_count': 5}, {'tree_count': 1}],
              reject=[([['trees = len(model.estimators_)\n', 'trees = 3\n']], 'Typing the count'), ([['trees = len(model.estimators_)\n', 'trees = model.max_depth\n']], 'Depth')],
              accept=[([['trees = len(model.estimators_)\n', 'trees = model.n_estimators\n']], 'The setting equals the trained count')]),
    code_step('stp_6a8cf0fb-ad90-4692-aa43-1c7b308dd3ce', 'RandomForestRegressor로 연속 시간을 예측하세요', '목표가 연속 값인지 종류인지로 모델 계열을 골라요.',
              'RandomForestClassifier는 연속 목표 0.5·1.5에서 ValueError다. RandomForestRegressor로 고쳐 [0.5, 1.5]를 확인한다. 채점은 다른 연속 시간으로 실행한다.',
              '이번 목표는 종류가 아니라 0.5분·1.5분 같은 연속 시간이에요. 같은 포레스트 계열이라도 크기를 맞히는 목표는 `RandomForestRegressor`, 종류를 고르는 목표는 `RandomForestClassifier`예요.',
              'model 줄을 고쳐 연속적인 시간을 예측하는 포레스트를 쓰세요. 채점은 다른 시간으로도 실행해요.',
              ['코드 실행을 눌러 ValueError가 나오는지 확인하세요.', '`RandomForestClassifier(`를 `RandomForestRegressor(`로 고치세요.', '코드 실행을 눌러 예측한 시간을 확인하세요.', SUBMIT],
              s3, s3_sol, n3, {n3.actions[-1]['text']: W},
              cases=[{'X_train': [[0], [1], [2]], 'y_train': [2.25, 7.5, 3.0]}, {'X_train': [[4], [9]], 'y_train': [0.1, 0.9]}],
              reject=[([['print(model.predict(X_train).tolist())', 'print(y_train)']], 'Printing the targets'),
                      ([['model = RandomForestRegressor(', 'model = RandomForestClassifier(']], 'Classifier')],
              accept=[([['n_estimators=3, bootstrap=False', 'n_estimators=5, bootstrap=False']], 'More trees without bootstrap')]),
    code_step('stp_754801ed-fb91-4f97-afc2-fcc5dd7a2805', 'StandardScaler와 KNN을 make_pipeline으로 이으세요', '거리 모델 앞에 훈련 기준 표준화를 둬 단위의 영향을 맞춰요.',
              '표준화 없는 KNN은 큰 단위의 둘째 특성 때문에 [0]이다. make_pipeline(StandardScaler(), KNN)으로 고쳐 [1]을 확인한다. 채점은 다른 평가 입력으로 실행한다.',
              'KNN(K-최근접 이웃)은 새 배송과 가장 가까운 훈련 배송 K개의 종류를 따라가요. `n_neighbors=1`이면 가장 가까운 하나만 봐요. 가까움은 특성 값의 거리로 재서 단위가 큰 특성이 거리를 좌우해요.',
              'model 줄을 고쳐 훈련 기준으로 표준화한 뒤 가장 가까운 이웃 하나를 따르게 하세요. 채점은 다른 평가 입력으로도 실행해요.',
              ['코드 실행을 눌러 예측을 확인하세요.', '`KNeighborsClassifier(n_neighbors=1)`을 `make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=1))`으로 고치세요.', '코드 실행을 눌러 예측이 바뀌는지 확인하세요.', SUBMIT],
              s4, s4_sol, n4, {n4.actions[-1]['text']: W}, cases=[{'X_test': [[0.2, 900], [0.95, 50]]}, {'X_test': [[0.4, 450], [0.6, 600]]}],
              reject=[([['model = make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=1))', 'model = KNeighborsClassifier(n_neighbors=1)']], 'Raw distance'),
                      ([['print(model.predict(X_test).tolist())', 'print([1])']], 'Typing the class')],
              accept=[([['model = make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=1))', 'from sklearn.pipeline import Pipeline\nmodel = Pipeline([("scale", StandardScaler()), ("knn", KNeighborsClassifier(n_neighbors=1))])']], 'Pipeline with names')]),
    code_step('stp_b3c38cb6-a565-4543-8567-d21d420235c3', 'decision_function으로 SVC의 결정 점수를 읽으세요', '결정 점수와 확률 지원을 구별해 맞는 API를 써요.',
              '기본 SVC의 predict_proba는 AttributeError다. decision_function으로 고쳐 [-1.333, 1.333] 결정 점수를 확인한다. 채점은 다른 훈련·평가 거리로 실행한다.',
              'SVC는 두 종류 사이에 경계선을 긋고, 새 배송이 경계선의 어느 쪽에 얼마나 떨어졌는지(결정 점수)로 종류를 골라요. 기본 설정의 SVC는 확률을 주는 `predict_proba`를 제공하지 않고 `decision_function`으로 점수를 줘요.',
              'scores 줄을 고쳐 확률 대신 경계선까지의 결정 점수를 scores에 담으세요. 채점은 다른 거리로도 실행해요.',
              ['코드 실행을 눌러 AttributeError가 나오는지 확인하세요.', '`model.predict_proba(X_test)`를 `model.decision_function(X_test)`로 고치세요.', '코드 실행을 눌러 결정 점수를 확인하세요.', SUBMIT],
              s5, s5_sol, n5, {n5.actions[-1]['text']: W, n5.actions[2]['text']: '실제 sklearn 동작(probability=False의 predict_proba 없음)을 정확히 말해요.'},
              cases=[{'X_train': [[0], [4], [10], [12]], 'X_test': [[2], [11], [7]]}, {'X_train': [[3], [5], [6], [8]], 'X_test': [[5.5]]}],
              reject=[([['scores = model.decision_function(X_test)', 'scores = model.predict(X_test)']], 'Predicted classes are not scores'),
                      ([['scores = model.decision_function(X_test)', 'scores = model.decision_function(X_train)']], 'Scores of the training rows')],
              accept=[([['scores = model.decision_function(X_test)', 'import numpy as np\nscores = np.asarray(X_test) @ model.coef_.T + model.intercept_\nscores = scores.ravel()']], 'The linear boundary by hand')]),
    code_step('stp_0800a4d0-3b43-47c9-bc52-171cb69bc055', '검증 정확도로 두 후보 중 하나를 고르세요', '학습에 쓰지 않은 같은 검증 자료로 후보를 비교해 골라요.',
              '훈련 정확도로 고르면 튀는 정답까지 외운 deep을 고른다. 검증 정확도로 고쳐 shallow를 확인한다. 채점은 다른 훈련·검증 자료로 실행한다.',
              '후보 두 개를 같은 훈련 자료로 학습하고, 학습에 쓰지 않은 같은 검증 자료로 정확도(score)를 매겨요. 새 배송에 쓸 모델은 검증 점수로 골라요.',
              'chosen 줄을 고쳐 훈련이 아니라 같은 검증 자료의 정확도로 후보를 고르세요. 채점은 다른 자료로도 실행해요.',
              ['코드 실행을 눌러 점수와 고른 후보를 확인하세요.', 'chosen 줄의 `X_train, y_train`을 `X_valid, y_valid`로 고치세요.', '코드 실행을 눌러 고른 후보를 확인하세요.', SUBMIT],
              s6, s6_sol, n6, {n6.actions[-1]['text']: W, n6.actions[2]['text']: '실제 출력 점수를 정확히 말해요.'},
              cases=[{'X_train': [[1], [2], [3], [4], [5], [6]], 'y_train': [0, 0, 0, 1, 1, 1], 'X_valid': [[1.5], [5.5]], 'y_valid': [0, 1]},
                     {'X_train': [[1], [2], [6], [7], [8], [9]], 'y_train': [0, 1, 0, 1, 1, 1], 'X_valid': [[1.9], [6.1]], 'y_valid': [1, 0]}],
              reject=[([['deep.score(X_valid, y_valid) >= shallow.score(X_valid, y_valid)', 'deep.score(X_train, y_train) >= shallow.score(X_train, y_train)']], 'Training accuracy'),
                      ([['chosen = "deep" if deep.score(X_valid, y_valid) >= shallow.score(X_valid, y_valid) else "shallow"', 'chosen = "shallow"']], 'Typing the name')],
              accept=[([['chosen = "deep" if deep.score(X_valid, y_valid) >= shallow.score(X_valid, y_valid) else "shallow"',
                         'scores = {"deep": deep.score(X_valid, y_valid), "shallow": shallow.score(X_valid, y_valid)}\nchosen = "deep" if scores["deep"] >= scores["shallow"] else "shallow"']], 'Scores in a dict')]),
]
