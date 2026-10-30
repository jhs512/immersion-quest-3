"""aice-classification: 7 answer-picking steps -> coding steps (2026-10-29).

Each step edits the model line, the probability column, the confidence read from predict_proba, a
two-class guard or the evaluation rows. Real scikit-learn models are fit on small separable data with
fixed random_state; prepared cases rerun with other labels, names and rows, so typed results, a fixed
column position and the starter's setting fail."""
from _kit import Script, code_step

OPENING = ['이 수업에서는 범주를 예측하는 분류를 직접 코드로 써요. 회귀와 분류의 목표 차이를 구별해요.',
           '기준 모델·트리·로지스틱 모델을 실행해요. 확률 열과 예측 범주의 연결도 코드로 확인해요.']
PRD_SCOPE = ['두 챕터·세 단원·아홉 스텝에서 같은 배송의 정상·지연을 분류해요.',
             'DummyClassifier·DecisionTreeClassifier·classes_로 찾는 확률 열·예측 범주의 확률·LogisticRegression·두 범주 확인·평가 자료의 정확도를 한 곳씩 직접 고쳐 써요. 정확도·정밀도·재현율의 계산은 다음 수업에서 이어가요.']
PRD_GRADING = ['직접 고친 코드를 실제 파이썬·scikit-learn으로 실행해 판정해요. 실행·해설만으로 성공시키지 않아요.',
               '여러 평가 행·다른 범주 이름·다른 잎 비율·한 범주 자료로 다시 실행해 기준 풀이와 비교해요. 결과를 글자로 적은 답, 고정된 열 위치, 회귀 모델, 행 수만 보는 조건, 훈련 정확도는 거절해요.',
               '마지막 도전(stp_91a6a75b-ce1e-47e5-9d88-de2b221813f0): 실제 Python 실행과 다른 준비 자료의 결과를 검사해요. 시작 코드는 실패하고 동등한 풀이도 통과해야 해요.']
PRD_NARRATION = ['작은 표에서 모델·확률 열·조건을 고쳐 실제 예측과 확률을 비교해요.',
                 '범주 숫자의 의미·확률 열·동점·모델 이름·학습 조건·평가 자료를 조심할 지점으로 짚어요.']

SUBMIT = '수정한 코드를 제출하세요.'
W = '실제 scikit-learn 동작을 정확히 말해요.'
PAIR = '# 같은 배송의 거리와 정상0·지연1을 함께 준비해요.\n'

s1 = ('from sklearn.dummy import DummyClassifier, DummyRegressor\n\n' + PAIR + 'X_train = [[1], [2], [8], [9]]\ny_train = [0, 0, 0, 1]\nX_test = [[1], [9]]\n'
      '# 이 줄을 고쳐 평균 숫자가 아니라 가장 흔한 범주를 고르는 기준 모델을 쓰세요.\nmodel = DummyRegressor(strategy="mean")\nmodel.fit(X_train, y_train)\n'
      'print(model.predict(X_test).tolist())\n')
s1_sol = s1.replace('model = DummyRegressor(strategy="mean")', '# 분류의 기준 모델은 훈련에서 가장 흔한 범주 하나를 모든 입력에 골라요.\nmodel = DummyClassifier(strategy="most_frequent")')
n1 = (Script(s1)
      .say('정상과 지연을 맞히는 분류의 비교 기준이 필요해요. model 줄을 가장 흔한 범주를 고르는 모델로 고쳐야 해요.', 'text:model 줄을 고쳐 평균 숫자가 아니라 가장 흔한 범주를 고르는 기준 모델을 쓰세요.')
      .run('print(model.predict')
      .say('[0.25, 0.25]예요. 범주 0과 1의 평균이라 어느 범주도 아니에요.', 'output')
      .patch('model = DummyRegressor(strategy="mean")', 'model = DummyClassifier(strategy="most_frequent")', 'DummyClassifier(strategy="most_frequent")로 바꿔요.')
      .run('print(model.predict')
      .say('[0, 0]이에요. 훈련에서 가장 흔한 정상 0을 두 배송 모두에 골랐어요.', 'output')
      .say('조심하세요. 범주 0과 1은 크기가 아니라 이름이에요. 평균 0.25는 어떤 배송의 상태도 아니에요.', 'code:strategy="most_frequent"'))

s2 = ('from sklearn.dummy import DummyClassifier\nfrom sklearn.tree import DecisionTreeClassifier\n\n' + PAIR
      + 'X_train = [[1], [2], [8], [9]]\ny_train = [0, 0, 1, 1]\nX_test = [[1], [9]]\n'
      '# 이 줄을 고쳐 거리 질문 한 번으로 나누는 결정 트리를 쓰세요.\nmodel = DummyClassifier(strategy="most_frequent")\nmodel.fit(X_train, y_train)\n'
      'print(model.predict(X_test).tolist())\n')
s2_sol = s2.replace('model = DummyClassifier(strategy="most_frequent")',
                    '# 결정 트리는 "거리가 기준보다 작은가?"로 나누고, 끝 묶음(잎)에서 가장 많은 범주를 예측해요.\nmodel = DecisionTreeClassifier(max_depth=1, random_state=0)')
n2 = (Script(s2)
      .say('거리에 따라 범주가 달라져요. model 줄을 거리 질문 한 번으로 나누는 결정 트리로 고쳐야 해요.', 'text:model 줄을 고쳐 거리 질문 한 번으로 나누는 결정 트리를 쓰세요.')
      .run('print(model.predict')
      .say('[0, 0]이에요. 기준 모델은 거리를 보지 않고 흔한 범주만 골랐어요.', 'output')
      .patch('model = DummyClassifier(strategy="most_frequent")', 'model = DecisionTreeClassifier(max_depth=1, random_state=0)', 'DecisionTreeClassifier(max_depth=1, random_state=0)로 바꿔요.')
      .run('print(model.predict')
      .say('[0, 1]이에요. 가까운 배송은 정상, 먼 배송은 지연으로 나눴어요.', 'output')
      .say('조심하세요. 예측 1은 1분이 아니라 지연이라는 범주예요.', 'code:DecisionTreeClassifier(max_depth=1'))

s3 = ('from sklearn.tree import DecisionTreeClassifier\n\n# 범주를 문자 이름으로 바꿨어요.\nX_train = [[1], [2], [8], [9]]\ny_train = ["on-time", "on-time", "late", "late"]\nX_test = [[1], [9]]\n'
      'model = DecisionTreeClassifier(max_depth=1, random_state=0)\nmodel.fit(X_train, y_train)\nprint(model.classes_.tolist())\n'
      '# 이 줄을 고쳐 classes_에서 "late"가 있는 자리의 확률 열을 꺼내세요.\nlate = model.predict_proba(X_test)[:, 1]\nprint(late.tolist())\n')
s3_sol = s3.replace('late = model.predict_proba(X_test)[:, 1]\n',
                    '# 확률의 열 순서는 classes_의 순서예요. 그 목록에서 "late"의 자리를 찾아요.\nlate = model.predict_proba(X_test)[:, list(model.classes_).index("late")]\n')
n3 = (Script(s3)
      .say('범주가 문자 이름이에요. late 줄을 고쳐 classes_에서 late의 자리를 찾아 그 열을 꺼내야 해요.', 'text:late 줄을 고쳐 classes_에서 "late"가 있는 자리의 확률 열을 꺼내세요.')
      .run('print(model.classes_', 'print(late')
      .say('[\'late\', \'on-time\']과 [1.0, 0.0]이에요. 둘째 열은 on-time의 확률이에요.', 'output')
      .patch('[:, 1]', '[:, list(model.classes_).index("late")]', '1 대신 list(model.classes_).index("late")를 써요.')
      .run('print(model.classes_', 'print(late')
      .say('[0.0, 1.0]이에요. 가까운 배송은 지연 확률 0, 먼 배송은 1이에요.', 'output')
      .say('조심하세요. classes_는 정렬된 순서라 late가 먼저 와요. 열 번호를 짐작하지 않아요.', 'code:list(model.classes_).index("late")'))

s4 = ('from sklearn.tree import DecisionTreeClassifier\n\n' + PAIR + 'X_train = [[1], [2], [8], [9]]\ny_train = [0, 1, 1, 1]\n'
      '# 잎마다 배송이 두 개 이상 남게 해요.\nmodel = DecisionTreeClassifier(max_depth=1, min_samples_leaf=2, random_state=0)\nmodel.fit(X_train, y_train)\n'
      'print(model.predict([[1]]).tolist())\n'
      '# 이 줄을 고쳐 예측한 범주의 확률을 predict_proba에서 꺼내 confidence에 담으세요.\nconfidence = 1.0\nprint(round(confidence, 3))\n')
s4_sol = s4.replace('confidence = 1.0\n', '# 잎 안의 범주 비율이 확률이에요. 예측한 범주는 그중 가장 큰 확률의 범주예요.\nconfidence = float(model.predict_proba([[1]]).max())\n')
n4 = (Script(s4)
      .say('예측했다고 확실한 건 아니에요. confidence 줄을 고쳐 예측한 범주의 확률을 꺼내야 해요.', 'text:confidence 줄을 고쳐 예측한 범주의 확률을 predict_proba에서 꺼내 confidence에 담으세요.')
      .run('print(model.predict', 'print(round(confidence')
      .say('[0]과 1.0이에요. 예측이 0이니 확실하다고 적어 두었어요.', 'output')
      .patch('confidence = 1.0\n', 'confidence = float(model.predict_proba([[1]]).max())\n', 'predict_proba([[1]])의 가장 큰 확률을 꺼내요.')
      .run('print(model.predict', 'print(round(confidence')
      .say('0.5예요. 잎에 정상과 지연이 하나씩이라 반반이고, 동점은 앞의 범주 0으로 정했어요.', 'output')
      .say('조심하세요. 예측 범주만 보면 반반인 판단도 확실해 보여요. 확률을 함께 봐요.', 'code:predict_proba([[1]]).max()'))

s5 = ('from sklearn.linear_model import LinearRegression, LogisticRegression\n\n' + PAIR + 'X_train = [[1], [2], [8], [9]]\ny_train = [0, 0, 1, 1]\nX_test = [[1], [9]]\n'
      '# 이 줄을 고쳐 범주 0·1을 예측하는 로지스틱 분류 모델을 쓰세요.\nmodel = LinearRegression()\nmodel.fit(X_train, y_train)\n'
      'print(model.predict(X_test).round(3).tolist())\nprint(list(model.predict_proba(X_test).shape))\n')
s5_sol = s5.replace('model = LinearRegression()', '# 이름에 Regression이 있지만 LogisticRegression은 범주와 그 확률을 내는 분류기예요.\nmodel = LogisticRegression(random_state=0)')
n5 = (Script(s5)
      .say('정답이 정상0·지연1인 범주예요. model 줄을 로지스틱 분류 모델로 고쳐야 해요.', 'text:model 줄을 고쳐 범주 0·1을 예측하는 로지스틱 분류 모델을 쓰세요.')
      .run('print(model.predict', 'print(list(model.predict_proba', error='AttributeError')
      .say('[-0.06, 1.06] 뒤에 AttributeError예요. 직선 회귀는 범주가 아닌 숫자를 내고 확률도 없어요.', 'output')
      .patch('model = LinearRegression()', 'model = LogisticRegression(random_state=0)', 'LogisticRegression(random_state=0)으로 바꿔요.')
      .run('print(model.predict', 'print(list(model.predict_proba')
      .say('[0, 1]과 [2, 2]예요. 두 배송마다 범주 두 개의 확률이 나왔어요.', 'output')
      .say('조심하세요. 이름의 Regression만 보고 시간 예측 모델로 쓰지 않아요. 무엇을 내는지 확인해요.', 'code:LogisticRegression(random_state=0)'))

s6 = ('from sklearn.linear_model import LogisticRegression\n\n' + PAIR + 'X_train = [[1], [2], [8], [9]]\ny_train = [0, 0, 0, 0]\nX_test = [[1], [9]]\n'
      'model = LogisticRegression(random_state=0)\n'
      '# 이 조건을 고쳐 훈련 정답에 서로 다른 범주가 두 개 이상일 때만 학습하세요.\nif len(y_train) >= 2:\n'
      '    model.fit(X_train, y_train)\n    print(model.predict(X_test).tolist())\nelse:\n    print("범주가 하나뿐이라 학습하지 않아요")\n')
s6_sol = s6.replace('if len(y_train) >= 2:\n', '# 분류 모델은 서로 다른 범주가 둘 이상 있어야 경계를 배울 수 있어요.\nif len(set(y_train)) >= 2:\n')
n6 = (Script(s6)
      .say('훈련 정답에 정상 0만 남았어요. if 조건을 고쳐 서로 다른 범주가 두 개 이상일 때만 학습해야 해요.', 'text:if 조건을 고쳐 훈련 정답에 서로 다른 범주가 두 개 이상일 때만 학습하세요.')
      .run('if len(y_train)', 'print("범주가', error='ValueError')
      .say('ValueError예요. 행은 네 개지만 범주가 하나뿐이라 학습할 수 없어요.', 'output')
      .patch('if len(y_train) >= 2:\n', 'if len(set(y_train)) >= 2:\n', 'len(y_train)을 len(set(y_train))으로 바꿔요.')
      .run('if len(set(y_train))', 'print("범주가')
      .say('범주가 하나뿐이라 학습하지 않는다고 알렸어요.', 'output')
      .say('조심하세요. 행이 많아도 범주가 하나면 분류를 배울 수 없어요. 행 수가 아니라 범주 수를 세요.', 'code:len(set(y_train))'))

s7 = ('from sklearn.tree import DecisionTreeClassifier\n\n' + PAIR + 'X_train = [[1], [2], [8], [9]]\ny_train = [0, 0, 1, 1]\nX_test = [[1], [9]]\n'
      'model = DecisionTreeClassifier(max_depth=1, random_state=0)\nmodel.fit(X_train, y_train)\n'
      '# 평가 정답은 학습에 넣지 않고 예측과 비교해요.\ny_test = [1, 0]\nprint(model.predict(X_test).tolist())\n'
      '# 이 줄을 고쳐 훈련이 아니라 X_test와 y_test로 정확도를 매기세요.\naccuracy = model.score(X_train, y_train)\nprint(float(accuracy))\n')
s7_sol = s7.replace('accuracy = model.score(X_train, y_train)\n', '# 새 배송을 맞히는지는 학습에 쓰지 않은 평가 자료로 재요.\naccuracy = model.score(X_test, y_test)\n')
n7 = (Script(s7)
      .say('새 배송의 실제 정답은 1·0이에요. accuracy 줄을 고쳐 평가 자료로 정확도를 매겨야 해요.', 'text:accuracy 줄을 고쳐 훈련이 아니라 X_test와 y_test로 정확도를 매기세요.')
      .run('print(model.predict', 'print(float(accuracy')
      .say('[0, 1]과 1.0이에요. 훈련 자료는 모두 맞혔어요.', 'output')
      .patch('model.score(X_train, y_train)', 'model.score(X_test, y_test)', 'X_train, y_train을 X_test, y_test로 바꿔요.')
      .run('print(model.predict', 'print(float(accuracy')
      .say('0.0이에요. 새 예측 0·1과 실제 1·0이 모두 달라요.', 'output')
      .say('조심하세요. 훈련을 맞혔다고 새 배송도 맞는 건 아니에요. 평가 자료로 따로 재요.', 'code:model.score(X_test, y_test)'))

SEP = {'X_train': [[3], [4], [10], [12], [13]], 'y_train': [1, 1, 0, 0, 0], 'X_test': [[2], [11], [5]]}

SPECS = [
    code_step('stp_a88ba144-7ee8-414c-ac3e-caf975390c5d', 'DummyClassifier로 가장 흔한 범주를 고르세요', '분류의 비교 기준은 범주를 고르는 모델임을 구별해요.',
              '평균 기준 회귀는 0.25라는 범주가 아닌 숫자를 낸다. DummyClassifier(strategy="most_frequent")로 고쳐 [0, 0]을 확인한다. 채점은 흔한 범주가 다른 자료로 실행한다.',
              '이번 정답은 정상0·지연1인 범주예요. 분류의 비교 기준은 입력을 보지 않고 훈련에서 가장 흔한 범주 하나를 골라요. `DummyClassifier(strategy="most_frequent")`가 그 기준이에요.',
              'model 줄을 고쳐 평균 숫자가 아니라 가장 흔한 범주를 고르는 기준 모델을 쓰세요. 채점은 다른 범주 자료로도 실행해요.',
              ['코드 실행을 눌러 예측을 확인하세요.', '`DummyRegressor(strategy="mean")`을 `DummyClassifier(strategy="most_frequent")`로 고치세요.', '코드 실행을 눌러 예측한 범주를 확인하세요.', SUBMIT],
              s1, s1_sol, n1, {n1.actions[-1]['text']: W},
              cases=[{'y_train': [1, 1, 0, 1], 'X_test': [[1], [5], [9]]}, {'X_train': [[0], [1], [2]], 'y_train': ['late', 'ok', 'ok'], 'X_test': [[7]]}],
              reject=[([['model = DummyClassifier(strategy="most_frequent")', 'model = DummyRegressor(strategy="mean")']], 'Mean of the labels'),
                      ([['print(model.predict(X_test).tolist())', 'print([0, 0])']], 'Typing the labels')],
              accept=[([['model = DummyClassifier(strategy="most_frequent")', 'model = DummyClassifier(strategy="prior")']], 'prior predicts the most frequent class')]),
    code_step('stp_85d73cee-019d-4092-a548-42e15308c963', 'DecisionTreeClassifier로 거리와 범주를 배우세요', '입력에 따라 범주를 나누는 결정 트리를 학습해요.',
              '기준 모델은 거리와 상관없이 [0, 0]이다. DecisionTreeClassifier(max_depth=1, random_state=0)로 고쳐 [0, 1]을 확인한다. 채점은 다른 경계의 자료로 실행한다.',
              '결정 트리는 "거리가 기준보다 작은가?" 같은 질문으로 자료를 나누고(분기), 나뉜 끝 묶음(잎)에서 가장 많은 범주를 예측해요. `max_depth=1`은 질문을 한 번만 해요.',
              'model 줄을 고쳐 거리 질문 한 번으로 나누는 결정 트리를 쓰세요. 채점은 다른 자료로도 실행해요.',
              ['코드 실행을 눌러 예측을 확인하세요.', '`DummyClassifier(strategy="most_frequent")`를 `DecisionTreeClassifier(max_depth=1, random_state=0)`으로 고치세요.', '코드 실행을 눌러 예측이 거리에 따라 달라지는지 확인하세요.', SUBMIT],
              s2, s2_sol, n2, {n2.actions[-1]['text']: W}, cases=[SEP, {'X_train': [[1], [2], [3], [7]], 'y_train': [0, 0, 0, 1], 'X_test': [[8], [0]]}],
              reject=[([['model = DecisionTreeClassifier(max_depth=1, random_state=0)', 'model = DummyClassifier(strategy="most_frequent")']], 'Baseline'),
                      ([['print(model.predict(X_test).tolist())', 'print([0, 1])']], 'Typing the labels')],
              accept=[([['model = DecisionTreeClassifier(max_depth=1, random_state=0)', 'model = DecisionTreeClassifier(max_depth=1, criterion="entropy", random_state=0)']], 'Entropy split')]),
    code_step('stp_6ecac607-bc82-4f32-97d9-5104c4e95b55', 'classes_로 "late" 확률의 열을 찾으세요', '확률 열의 순서가 classes_의 순서임을 써서 원하는 범주의 확률을 꺼내요.',
              '열 1은 on-time의 확률이다. list(model.classes_).index("late")로 고쳐 late의 확률 [0.0, 1.0]을 확인한다. 채점은 범주 이름이 다른 자료로 실행한다.',
              '범주를 문자 이름으로 바꿨어요. `predict_proba`의 열은 `model.classes_`의 같은 자리 범주의 확률이고, `classes_`는 정렬된 순서예요. `목록.index(값)`은 그 값의 자리를 돌려줘요.',
              'late 줄을 고쳐 classes_에서 "late"가 있는 자리의 확률 열을 꺼내세요. 채점은 다른 범주 이름으로도 실행해요.',
              ['코드 실행을 눌러 classes_와 late를 확인하세요.', '`[:, 1]`의 1을 `list(model.classes_).index("late")`로 고치세요.', '코드 실행을 눌러 late의 확률을 확인하세요.', SUBMIT],
              s3, s3_sol, n3, {n3.actions[-1]['text']: W},
              cases=[{'y_train': ['early', 'early', 'late', 'late']}, {'X_train': [[1], [2], [3], [8], [9], [10]], 'y_train': ['late', 'late', 'late', 'ok', 'ok', 'ok'], 'X_test': [[2], [9], [6]]}],
              reject=[([['[:, list(model.classes_).index("late")]', '[:, 1]']], 'Second column'),
                      ([['[:, list(model.classes_).index("late")]', '[:, 0]']], 'First column')],
              accept=[([['late = model.predict_proba(X_test)[:, list(model.classes_).index("late")]\n',
                         'column = model.classes_.tolist().index("late")\nlate = model.predict_proba(X_test)[:, column]\n']], 'Column first')]),
    code_step('stp_4c58faec-3d29-408d-b5b0-86644c4f67aa', 'predict_proba로 예측한 범주의 확률을 읽으세요', '예측 범주와 그 확률을 구별해 반반인 판단을 확인해요.',
              '예측 0을 보고 confidence를 1.0으로 적었다. predict_proba([[1]]).max()로 고쳐 잎의 비율 0.5를 확인한다. 채점은 잎 비율이 다른 자료로 실행한다.',
              '잎은 트리가 나눈 끝 묶음이에요. `predict_proba`는 그 잎 안의 범주 비율을 확률로 보여 주고, 예측 범주는 가장 큰 확률의 범주예요. 동점이면 `classes_`에서 앞에 있는 범주를 골라요.',
              'confidence 줄을 고쳐 예측한 범주의 확률을 predict_proba에서 꺼내 confidence에 담으세요. 채점은 다른 자료로도 실행해요.',
              ['코드 실행을 눌러 예측과 confidence를 확인하세요.', '`confidence = 1.0`을 `confidence = float(model.predict_proba([[1]]).max())`로 고치세요.', '코드 실행을 눌러 확률을 확인하세요.', SUBMIT],
              s4, s4_sol, n4, {n4.actions[-1]['text']: W},
              cases=[{'X_train': [[1], [2], [3], [8], [9], [10]], 'y_train': [0, 1, 0, 1, 1, 1]}, {'X_train': [[1], [2], [3], [8], [9], [10]], 'y_train': [1, 1, 0, 0, 0, 1]}],
              reject=[([['confidence = float(model.predict_proba([[1]]).max())\n', 'confidence = float(model.predict_proba([[1]])[0][0])\n']], 'Probability of class 0 always'),
                      ([['confidence = float(model.predict_proba([[1]]).max())\n', 'confidence = 0.5\n']], 'Typing the probability')],
              accept=[([['confidence = float(model.predict_proba([[1]]).max())\n',
                         'predicted = model.predict([[1]])[0]\nconfidence = float(model.predict_proba([[1]])[0][list(model.classes_).index(predicted)])\n']], 'Column of the predicted class')]),
    code_step('stp_b428710e-c1bf-4b55-a667-4a16a69c9247', 'LogisticRegression으로 범주와 확률을 예측하세요', '이름에 Regression이 있어도 범주를 예측하는 분류기를 구별해 써요.',
              'LinearRegression은 범주가 아닌 숫자를 내고 predict_proba가 없어 AttributeError다. LogisticRegression(random_state=0)으로 고쳐 [0, 1]과 확률 모양 [2, 2]를 확인한다. 채점은 다른 자료로 실행한다.',
              '이번 정답은 정상0·지연1인 범주예요. `LinearRegression`은 연속 숫자를 예측해요. `LogisticRegression`은 이름에 Regression이 있지만 범주와 범주별 확률(`predict_proba`)을 내는 분류기예요.',
              'model 줄을 고쳐 범주 0·1을 예측하는 로지스틱 분류 모델을 쓰세요. 채점은 다른 자료로도 실행해요.',
              ['코드 실행을 눌러 AttributeError가 나오는지 확인하세요.', '`LinearRegression()`을 `LogisticRegression(random_state=0)`으로 고치세요.', '코드 실행을 눌러 범주와 확률 모양을 확인하세요.', SUBMIT],
              s5, s5_sol, n5, {n5.actions[-1]['text']: W},
              cases=[SEP, {'X_train': [[0], [1], [5], [6], [7], [8]], 'y_train': [0, 0, 0, 1, 1, 1], 'X_test': [[0.5]]}],
              reject=[([['model = LogisticRegression(random_state=0)', 'model = LinearRegression()']], 'Linear regression'),
                      ([['print(list(model.predict_proba(X_test).shape))', 'print([2, 2])']], 'Typing the shape')],
              accept=[([['model = LogisticRegression(random_state=0)', 'model = LogisticRegression()']], 'Default random_state')]),
    code_step('stp_7fe94b48-9022-43ef-9de9-00f1e0b51c86', 'len(set(y_train))로 범주가 두 개 이상인지 확인하세요', '분류 학습에는 서로 다른 범주가 둘 이상 필요함을 확인해요.',
              '행 수만 보는 조건은 범주가 하나여도 학습해 ValueError다. len(set(y_train)) >= 2로 고쳐 학습하지 않는다는 안내를 확인한다. 채점은 범주가 두 개인 자료로도 실행한다.',
              '훈련 정답에 정상0만 남았어요. 로지스틱 모델은 범주 사이의 경계를 배우므로 서로 다른 범주가 둘 이상 있어야 해요. `set(목록)`은 서로 다른 값만 남겨요.',
              'if 조건을 고쳐 훈련 정답에 서로 다른 범주가 두 개 이상일 때만 학습하세요. 채점은 범주가 두 개인 자료로도 실행해요.',
              ['코드 실행을 눌러 ValueError가 나오는지 확인하세요.', '`len(y_train)`을 `len(set(y_train))`으로 고치세요.', '코드 실행을 눌러 안내를 확인하세요.', SUBMIT],
              s6, s6_sol, n6, {n6.actions[-1]['text']: W},
              cases=[{'y_train': [0, 0, 1, 1]}, {'X_train': [[3], [5]], 'y_train': [1, 1], 'X_test': [[4]]}],
              reject=[([['if len(set(y_train)) >= 2:\n', 'if len(y_train) >= 2:\n']], 'Counting rows'),
                      ([['if len(set(y_train)) >= 2:\n', 'if False:\n']], 'Never fitting')],
              accept=[([['if len(set(y_train)) >= 2:\n', 'if min(y_train) != max(y_train):\n']], 'min differs from max')]),
    code_step('stp_1e941992-8426-4332-acf1-e55bdbc8bd00', 'model.score(X_test, y_test)로 새 배송의 정확도를 매기세요', '훈련 정확도와 평가 자료의 정확도를 구별해요.',
              '훈련 정확도는 1.0이다. score(X_test, y_test)로 고쳐 새 배송의 정확도 0.0을 확인한다. 채점은 다른 평가 정답으로 실행한다.',
              '훈련은 모두 맞혔지만 새 배송의 실제 정답은 1·0이에요. `model.score(입력, 정답)`은 그 자료에서 맞힌 비율(정확도)이에요. 새 배송에서의 성능은 학습에 쓰지 않은 평가 자료로 재요.',
              'accuracy 줄을 고쳐 훈련이 아니라 X_test와 y_test로 정확도를 매기세요. 채점은 다른 평가 정답으로도 실행해요.',
              ['코드 실행을 눌러 예측과 정확도를 확인하세요.', '`model.score(X_train, y_train)`을 `model.score(X_test, y_test)`로 고치세요.', '코드 실행을 눌러 새 배송의 정확도를 확인하세요.', SUBMIT],
              s7, s7_sol, n7, {n7.actions[-1]['text']: W},
              cases=[{'X_test': [[1], [9], [2], [8]], 'y_test': [0, 1, 1, 1]}, {'X_test': [[0]], 'y_test': [0]}],
              reject=[([['accuracy = model.score(X_test, y_test)\n', 'accuracy = model.score(X_train, y_train)\n']], 'Training accuracy'),
                      ([['accuracy = model.score(X_test, y_test)\n', 'accuracy = 0.0\n']], 'Typing the accuracy')],
              accept=[([['accuracy = model.score(X_test, y_test)\n', 'from sklearn.metrics import accuracy_score\naccuracy = accuracy_score(y_test, model.predict(X_test))\n']], 'accuracy_score')]),
]
