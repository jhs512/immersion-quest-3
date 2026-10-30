"""aice-integration: 9 answer-picking steps -> coding steps (2026-10-30).

Each step edits one line of the delivery pipeline that reads the lesson's real delivery.csv and new.csv:
the input columns, the categorical branch, transform-only on new rows, the Pipeline, cross-validating
the whole pipeline, the grid parameter path, the numeric matrix for a Keras model, index=False on export
and saving the whole pipeline. Grading reads column names, shapes, learned fill means, closed-form linear
and ridge predictions and exported ids; the Keras step reads only shapes and finiteness. Prepared cases
replace the read tables with other deliveries (other zones, blanks, orders), so typed outputs fail."""
from _kit import Script, code_step

OPENING = ['이 수업에서는 데이터 준비부터 예측 저장까지 한 흐름을 직접 코드로 이어요. 단계마다 같은 기준을 유지하는 게 목표예요.',
           '실제 파일에서 입력과 정답을 나누고 전처리를 묶어요. 교차검증·설정 탐색·신경망 입력·결과 파일·저장과 복원까지 실행해 확인해요.']
PRD_SCOPE = ['두 챕터·두 단원·열한 스텝으로 같은 배송 파일을 예측 결과 파일까지 이어요.',
             '입력 열 고르기·범주 열 원핫 갈래·새 표는 transform만·Pipeline·Pipeline 전체 교차검증·model__ 설정 경로·신경망에 숫자 행렬·index=False·전체 파이프라인 저장을 한 곳씩 직접 고쳐 써요.']
PRD_GRADING = ['직접 고친 코드를 실제 파이썬·pandas·scikit-learn(신경망 스텝은 TensorFlow)으로 실행해 판정해요. 실행·해설만으로 성공시키지 않아요.',
               '열 이름·모양·훈련에서 배운 빈칸 평균·선형 모델과 Ridge의 예측·내보낸 주문번호로 채점하고, 신경망 스텝은 모양과 유한값만 봐요. 읽은 표를 다른 배송(다른 지역·빈칸·순서)으로 바꿔 다시 실행해 기준 풀이와 비교해요.',
               '결과를 글자로 적은 답, 정답이나 주문번호를 섞은 입력, 다른 열의 원핫, 새 표로 다시 fit, 단계 순서가 바뀐 Pipeline, 미리 fit한 행렬의 교차검증, 잘못된 설정 경로, 문자열 그대로의 신경망 입력, 정렬해 바뀐 대응, 모델만 저장은 거절해요.',
               '마지막 도전(stp_86d1f031-ffaa-4e3d-8aef-d112f66496fd): 실제 Python 실행과 다른 준비 자료의 결과를 검사해요. 시작 코드는 실패하고 동등한 풀이도 통과해야 해요.']
PRD_NARRATION = ['한 줄씩 고친 뒤 실제 열·모양·기준·예측·파일을 읽어요.',
                 '입력과 정답·열 종류·새 자료의 fit·호출 순서·fold 안의 학습·설정 경로·숫자 행렬·행 번호와 대응·저장 범위를 조심할 지점으로 짚어요.']

FILES = {'delivery.csv': 'order_id,distance,zone,minutes\n101,1,north,10\n102,2,north,20\n103,3,south,30\n104,4,south,40\n105,5,north,50\n106,6,south,60\n',
         'new.csv': 'order_id,distance,zone\n201,2,north\n202,,west\n203,8,south\n'}
IMPORTS = ('import numpy as np\nimport pandas as pd\nfrom sklearn.compose import ColumnTransformer\nfrom sklearn.pipeline import Pipeline\n'
           'from sklearn.impute import SimpleImputer\nfrom sklearn.preprocessing import StandardScaler, OneHotEncoder\nfrom sklearn.linear_model import LinearRegression\n\n')
READ = ('# 파일을 열 이름별 목록으로 읽어 두고 그 목록으로 표를 만들어요. 그래서 다른 자료 목록을 넣어도 같은 코드가 돌아요.\n'
        'train_rows = pd.read_csv("delivery.csv").to_dict(orient="list")\nnew_rows = pd.read_csv("new.csv").to_dict(orient="list")\n'
        'df = pd.DataFrame(train_rows)\nnew = pd.DataFrame(new_rows)\n')
XY = 'X_train = df[["distance", "zone"]]\ny_train = df["minutes"]\nX_new = new[["distance", "zone"]]\n'
NUM = '    # 1) 숫자 열: 빈칸을 평균으로 채운 뒤 표준화해요.\n    ("num", Pipeline([("fill", SimpleImputer(strategy="mean")), ("scale", StandardScaler())]), ["distance"]),\n'
CAT = ('    # 2) 범주 열: 빈칸을 가장 흔한 값으로 채운 뒤 원핫 열로 바꿔요.\n'
       '    ("cat", Pipeline([("fill", SimpleImputer(strategy="most_frequent")), ("encode", OneHotEncoder(handle_unknown="ignore", sparse_output=False))]), ["zone"])\n')
PREP = '# 숫자와 범주 열을 각자 처리하고, ColumnTransformer가 둘을 열별로 묶어요.\npreprocess = ColumnTransformer([\n' + NUM + CAT + '])\n'
BASE = IMPORTS + READ + XY + PREP
FIT = 'pipeline = Pipeline([("prep", preprocess), ("model", LinearRegression())])\npipeline.fit(X_train, y_train)\n'
SUB = '수정한 코드를 제출하세요.'
W = '실제 pandas·scikit-learn 동작을 정확히 말해요.'
T = 30

OTHER_TRAIN = {'order_id': [1, 2, 3, 4, 5, 6], 'distance': [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
               'zone': ['north', 'north', 'south', 'south', 'north', 'south'], 'minutes': [5.0, 10.0, 15.0, 20.0, 25.0, 30.0]}
THREE_ZONES = {'order_id': [1, 2, 3, 4, 5, 6], 'distance': [1.0, 2.0, None, 4.0, 5.0, 6.0],
               'zone': ['north', 'east', 'south', 'east', 'north', 'south'], 'minutes': [11.0, 19.0, 32.0, 41.0, 48.0, 62.0]}
NEW_A = {'order_id': [7, 8], 'distance': [1.0, 3.0], 'zone': ['north', 'south']}
NEW_DESC = {'order_id': [9, 8, 7], 'distance': [8.0, 2.0, None], 'zone': ['south', 'north', 'west']}

# 1. Inputs are only what a new delivery already has.
g1 = (IMPORTS + READ + '# 이 줄을 고쳐 X_train에 새 배송에도 있는 입력 distance와 zone만 남기세요.\nX_train = df.drop(columns=["order_id"])\n'
      'y_train = df["minutes"]\nX_new = new[["distance", "zone"]]\nprint(X_train.columns.tolist())\nprint(y_train.tolist())\n'
      '# 훈련 입력과 새 입력의 열이 같아야 같은 모델에 넣을 수 있어요.\nprint(X_train.columns.tolist() == X_new.columns.tolist())\n')
g1_sol = g1.replace('X_train = df.drop(columns=["order_id"])\n', '# 정답 minutes와 단순 번호 order_id는 입력이 아니에요. 새 배송이 가진 열만 입력이에요.\nX_train = df[["distance", "zone"]]\n')
h1 = (Script(g1)
      .say('새 배송은 아직 걸린 시간을 몰라요. 예측할 때 넣을 수 있는 열만 입력으로 남겨야 해요.', 'text:X_train에 새 배송에도 있는 입력 distance와 zone만 남기세요.')
      .run('print(X_train.columns', 'print(X_train.columns.tolist() ==')
      .say("['distance', 'zone', 'minutes']와 False예요. 맞혀야 할 minutes가 입력에 섞여 새 입력과 열이 달라요.", 'output')
      .patch('X_train = df.drop(columns=["order_id"])\n', 'X_train = df[["distance", "zone"]]\n', 'df[["distance", "zone"]]로 바꿔요.')
      .run('print(X_train.columns', 'print(X_train.columns.tolist() ==')
      .say("['distance', 'zone']과 True예요. 정답 열은 y_train에 따로 있어요.", 'output')
      .say('조심하세요. 정답 열을 입력에 넣으면 훈련 점수는 좋아 보여도 새 배송에는 그 열이 없어 쓸 수 없어요. 주문번호도 의미 없는 입력이에요.', 'code:df[["distance", "zone"]]'))

# 2. The categorical branch one-hot encodes zone.
g2 = (IMPORTS + READ + XY + '# 숫자와 범주 열을 각자 처리하고, ColumnTransformer가 둘을 열별로 묶어요.\npreprocess = ColumnTransformer([\n' + NUM
      + '    # 이 자리에 zone 열을 가장 흔한 값으로 채운 뒤 원핫 열로 바꾸는 "cat" 갈래를 더하세요.\n])\n'
      'matrix = preprocess.fit_transform(X_train)\nprint(list(matrix.shape))\nprint(preprocess.get_feature_names_out().tolist())\n')
g2_sol = g2.replace('    # 이 자리에 zone 열을 가장 흔한 값으로 채운 뒤 원핫 열로 바꾸는 "cat" 갈래를 더하세요.\n',
                    '    # 이 자리에 zone 열을 가장 흔한 값으로 채운 뒤 원핫 열로 바꾸는 "cat" 갈래를 더하세요.\n'
                    '    # 범주 열은 숫자 크기가 없어요. 지역마다 0과 1의 열 하나씩을 만들어요.\n'
                    '    ("cat", Pipeline([("fill", SimpleImputer(strategy="most_frequent")), ("encode", OneHotEncoder(handle_unknown="ignore", sparse_output=False))]), ["zone"])\n')
CAT_LINE = '    ("cat", Pipeline([("fill", SimpleImputer(strategy="most_frequent")), ("encode", OneHotEncoder(handle_unknown="ignore", sparse_output=False))]), ["zone"])\n'
h2 = (Script(g2)
      .say('지금은 거리만 처리해요. 지역 zone을 원핫 열로 바꾸는 갈래를 더해야 해요.', 'text:zone 열을 가장 흔한 값으로 채운 뒤 원핫 열로 바꾸는 "cat" 갈래를 더하세요.')
      .run('print(list(matrix.shape))', 'print(preprocess.get_feature_names_out')
      .say("[6, 1]과 ['num__distance']예요. 지역 열은 버려졌어요.", 'output')
      .patch('    # 이 자리에 zone 열을 가장 흔한 값으로 채운 뒤 원핫 열로 바꾸는 "cat" 갈래를 더하세요.\n',
             '    # 이 자리에 zone 열을 가장 흔한 값으로 채운 뒤 원핫 열로 바꾸는 "cat" 갈래를 더하세요.\n' + CAT_LINE, '주석 아래에 "cat" 갈래를 써요.')
      .run('print(list(matrix.shape))', 'print(preprocess.get_feature_names_out')
      .say("[6, 3]이에요. 숫자 열 하나와 north·south 원핫 열 두 개예요.", 'output')
      .say('조심하세요. ColumnTransformer에 적지 않은 열은 기본으로 버려져요. 출력 열 이름으로 무엇이 남았는지 확인해요.', 'code:["zone"])'))

# 3. New rows are only transformed with the training rule.
g3 = (BASE + 'preprocess.fit(X_train)\n# 이 줄을 고쳐 새 표에는 훈련에서 배운 기준을 transform으로만 적용하세요.\nnew_matrix = preprocess.fit_transform(X_new)\n'
      'print(list(new_matrix.shape))\nprint(float(preprocess.named_transformers_["num"].named_steps["fill"].statistics_[0]))\nprint(new_matrix[1, 1:].tolist())\n')
g3_sol = g3.replace('new_matrix = preprocess.fit_transform(X_new)\n', '# transform은 훈련에서 배운 평균·표준편차·지역 목록을 그대로 써요. 새 표로 다시 배우지 않아요.\nnew_matrix = preprocess.transform(X_new)\n')
h3 = (Script(g3)
      .say('새 표에는 빈 거리와 훈련에 없던 지역 west가 있어요. 훈련 기준을 그대로 적용해야 해요.', 'text:새 표에는 훈련에서 배운 기준을 transform으로만 적용하세요.')
      .run('print(list(new_matrix.shape))', 'print(new_matrix[1, 1:]')
      .say('[3, 4], 5.0, [0.0, 0.0, 1.0]이에요. 새 표로 다시 배워 평균이 5.0이 되고 west 열까지 생겼어요.', 'output')
      .patch('new_matrix = preprocess.fit_transform(X_new)\n', 'new_matrix = preprocess.transform(X_new)\n', 'fit_transform을 transform으로 바꿔요.')
      .run('print(list(new_matrix.shape))', 'print(new_matrix[1, 1:]')
      .say('[3, 3], 3.5, [0.0, 0.0]이에요. 빈 거리는 훈련 평균 3.5로 채우고 처음 보는 west는 두 칸 모두 0이에요.', 'output')
      .say('조심하세요. 새 표에 fit하면 기준과 열 수가 바뀌어 훈련한 모델과 맞지 않아요. 새 자료에는 transform만 해요.', 'code:preprocess.transform(X_new)'))

# 4. A Pipeline joins preprocessing and the model.
g4 = (BASE + '# 이 줄을 고쳐 전처리 preprocess 다음에 LinearRegression이 오는 Pipeline을 만드세요.\npipeline = Pipeline([("model", LinearRegression())])\n'
      'pipeline.fit(X_train, y_train)\nprint(pipeline.predict(X_new).round(6).tolist())\n')
g4_sol = g4.replace('pipeline = Pipeline([("model", LinearRegression())])\n',
                    '# fit은 전처리 기준을 배운 뒤 모델을 학습하고, predict는 배운 기준으로 바꾼 뒤 예측만 해요.\npipeline = Pipeline([("prep", preprocess), ("model", LinearRegression())])\n')
h4 = (Script(g4)
      .say('모델은 숫자만 받아요. 전처리를 모델 앞에 묶어 한 번의 fit과 predict로 이어야 해요.', 'text:전처리 preprocess 다음에 LinearRegression이 오는 Pipeline을 만드세요.')
      .run('print(pipeline.predict', error='ValueError')
      .say("ValueError예요. 전처리 없이 지역 글자 'north'를 숫자로 바꿀 수 없어요.", 'output')
      .patch('Pipeline([("model", LinearRegression())])', 'Pipeline([("prep", preprocess), ("model", LinearRegression())])', '목록 맨 앞에 ("prep", preprocess)를 넣어요.')
      .run('print(pipeline.predict')
      .say('[20.0, 35.0, 80.0]이에요. 빈 거리는 훈련 평균 3.5로 채워져 35.0이 됐어요.', 'output')
      .say('조심하세요. predict는 아무것도 다시 배우지 않아요. 새 표로 fit하면 기준이 새 자료에 맞춰져 다른 예측이 나와요.', 'code:("prep", preprocess)'))

# 5. Cross-validate the whole pipeline so each fold learns its own preprocessing.
g5 = (BASE + 'from sklearn.model_selection import KFold, cross_validate\n\npipeline = Pipeline([("prep", preprocess), ("model", LinearRegression())])\n'
      '# 이 줄을 고쳐 미리 fit한 행렬 대신 pipeline 전체와 원래 표 X_train을 교차검증에 넘기세요.\n'
      'result = cross_validate(LinearRegression(), preprocess.fit_transform(X_train), y_train, cv=KFold(n_splits=3), return_estimator=True)\n'
      '# 확인용 출력: fold마다 거리 빈칸을 채운 평균이에요. 미리 fit했다면 모두 전체 평균이에요. 이 줄의 문법은 몰라도 돼요.\n'
      'print([float(getattr(m, "named_steps", {"prep": preprocess})["prep"].named_transformers_["num"].named_steps["fill"].statistics_[0]) for m in result["estimator"]])\n')
g5_sol = g5.replace('result = cross_validate(LinearRegression(), preprocess.fit_transform(X_train), y_train,',
                    '# Pipeline 전체를 넘기면 fold마다 그 훈련 몫으로만 전처리 기준을 다시 배워요.\nresult = cross_validate(pipeline, X_train, y_train,')
h5 = (Script(g5)
      .say('전처리를 전체 표로 미리 fit하면 평가 몫의 정보가 기준에 섞여요. pipeline 전체를 교차검증에 넘겨야 해요.', 'text:미리 fit한 행렬 대신 pipeline 전체와 원래 표 X_train을 교차검증에 넘기세요.')
      .run('print([float(getattr')
      .say('[3.5, 3.5, 3.5]예요. 세 fold가 모두 전체 표의 평균을 함께 썼어요.', 'output')
      .patch('cross_validate(LinearRegression(), preprocess.fit_transform(X_train), y_train,', 'cross_validate(pipeline, X_train, y_train,', 'pipeline과 X_train을 넘겨요.')
      .run('print([float(getattr')
      .say('[4.5, 3.5, 2.5]예요. fold마다 자기 훈련 몫의 거리로만 평균을 배웠어요.', 'output')
      .say('조심하세요. 교차검증 밖에서 전체 표로 전처리를 먼저 fit해 공유하지 않아요. 평가 몫이 기준에 들어가요.', 'code:cross_validate(pipeline, X_train, y_train,'))

# 6. Grid parameters address the step by name: model__alpha.
g6 = (BASE + 'from sklearn.linear_model import Ridge\nfrom sklearn.model_selection import GridSearchCV, KFold\n\n'
      '# Ridge는 계수가 너무 커지지 않게 벌점을 주는 선형 회귀이고, alpha가 그 세기예요.\nalphas = [0.1, 1.0]\n'
      'pipeline = Pipeline([("prep", preprocess), ("model", Ridge())])\n'
      '# 이 줄을 고쳐 Pipeline 안 model 단계의 alpha 후보를 탐색하세요.\n'
      'search = GridSearchCV(pipeline, {"prep__alpha": alphas}, scoring="neg_mean_squared_error", cv=KFold(n_splits=3), n_jobs=1)\n'
      'search.fit(X_train, y_train)\nprint(len(search.cv_results_["params"]))\nprint(list(search.predict(X_new).shape))\n'
      '# 교차검증 RMSE: negMSE 점수의 부호를 바꿔 제곱근을 구하면 분 단위 예상 오차예요.\nprint(round(float((-search.best_score_) ** 0.5), 3))\n')
g6_sol = g6.replace('{"prep__alpha": alphas}', '{"model__alpha": alphas}').replace(
    '# 이 줄을 고쳐 Pipeline 안 model 단계의 alpha 후보를 탐색하세요.\n',
    '# 이 줄을 고쳐 Pipeline 안 model 단계의 alpha 후보를 탐색하세요.\n# 단계 이름 model과 설정 이름 alpha를 밑줄 두 개로 이어요.\n')
h6 = (Script(g6)
      .say('alpha는 Ridge의 설정이에요. Pipeline 안에서는 단계 이름과 설정 이름을 밑줄 두 개로 이어 적어야 해요.', 'text:Pipeline 안 model 단계의 alpha 후보를 탐색하세요.')
      .run('print(len(search', error='ValueError')
      .say('ValueError예요. 전처리 단계 prep에는 alpha라는 설정이 없어요.', 'output')
      .patch('{"prep__alpha": alphas}', '{"model__alpha": alphas}', 'prep__alpha를 model__alpha로 바꿔요.')
      .run('print(len(search', 'print(round(float(')
      .say('2, [3], 1.85예요. 후보 두 개를 비교했고 새 예측 세 개가 나왔어요. 교차검증 RMSE는 1.85분이에요.', 'output')
      .say('조심하세요. 후보 비교는 교차검증 점수예요. 실제 정답이 없는 새 표의 정확도는 아직 몰라요.', 'code:{"model__alpha": alphas}'))

# 7. A Keras model gets the preprocessed numeric matrix.
TF = ('import os\nos.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")\nimport tensorflow as tf\nfrom tensorflow import keras\n'
      'tf.config.threading.set_intra_op_parallelism_threads(1)\ntf.config.threading.set_inter_op_parallelism_threads(1)\nkeras.utils.set_random_seed(7)\n')
g7 = (TF + BASE + '# 이 줄을 고쳐 훈련 표를 전처리로 바꾼 숫자 행렬로 만드세요. 전처리 기준도 여기서 배워요.\ntrain_matrix = X_train\n'
      'new_matrix = preprocess.transform(X_new).astype("float32")\n'
      'model = keras.Sequential([keras.Input(shape=(train_matrix.shape[1],)), keras.layers.Dense(4, activation="relu"), keras.layers.Dense(1)])\n'
      'model.compile(optimizer="adam", loss="mse")\nmodel.fit(train_matrix, y_train.to_numpy(dtype="float32"), epochs=2, batch_size=3, shuffle=False, verbose=0)\n'
      'predictions = model.predict(new_matrix, verbose=0)\nprint(list(predictions.shape))\nprint(bool(np.isfinite(predictions).all()))\n')
g7_sol = g7.replace('train_matrix = X_train\n', '# Dense는 숫자만 계산해요. 훈련 표로 기준을 배우고 같은 전처리로 바꾼 행렬을 넘겨요.\ntrain_matrix = preprocess.fit_transform(X_train).astype("float32")\n')
h7 = (Script(g7)
      .say('Dense 층은 숫자만 계산해요. 지역 글자 대신 전처리로 바꾼 숫자 행렬을 넘겨야 해요.', 'text:훈련 표를 전처리로 바꾼 숫자 행렬로 만드세요.')
      .run('print(list(predictions.shape))', error='NotFittedError')
      .say('NotFittedError예요. 전처리 기준을 아직 배우지 않아 새 표를 바꿀 수 없어요.', 'output')
      .patch('train_matrix = X_train\n', 'train_matrix = preprocess.fit_transform(X_train).astype("float32")\n', 'preprocess.fit_transform(X_train).astype("float32")로 바꿔요.')
      .run('print(list(predictions.shape))', 'print(bool(np.isfinite')
      .say('[3, 1]과 True예요. 짧게 학습한 뒤 새 배송 세 건에 출력 하나씩 나왔어요.', 'output')
      .say('조심하세요. 모양이 맞아 실행된 것만으로 새 예측의 성능까지 보장하지는 않아요.', 'code:preprocess.fit_transform(X_train)'))

# 8. Export ids and predictions without pandas' row numbers.
g8 = (BASE + FIT + '# 새 입력 순서와 원래 주문번호의 대응을 그대로 보존해요.\n'
      'answer = pd.DataFrame({"order_id": new["order_id"], "minutes": pipeline.predict(X_new).round(6)})\n'
      '# 이 줄을 고쳐 판다스의 행 번호는 빼고 두 열만 파일에 쓰세요.\nanswer.to_csv("answer.csv")\n'
      'restored = pd.read_csv("answer.csv")\nprint(restored.columns.tolist())\nprint(restored["order_id"].tolist())\nprint(restored["minutes"].tolist())\n')
g8_sol = g8.replace('answer.to_csv("answer.csv")\n', '# index=False면 판다스의 행 번호를 열로 쓰지 않아요.\nanswer.to_csv("answer.csv", index=False)\n')
h8 = (Script(g8)
      .say('제출 파일에는 주문번호와 예측만 있어야 해요. 판다스의 행 번호를 쓰지 않게 옵션을 더해요.', 'text:판다스의 행 번호는 빼고 두 열만 파일에 쓰세요.')
      .run('print(restored.columns', 'print(restored["minutes"]')
      .say("['Unnamed: 0', 'order_id', 'minutes']예요. 행 번호가 이름 없는 열로 들어갔어요.", 'output')
      .patch('answer.to_csv("answer.csv")\n', 'answer.to_csv("answer.csv", index=False)\n', '괄호 안에 index=False를 더해요.')
      .run('print(restored.columns', 'print(restored["minutes"]')
      .say("['order_id', 'minutes'], [201, 202, 203], [20.0, 35.0, 80.0]이에요. 두 열이고 새 배송 순서를 유지했어요.", 'output')
      .say('조심하세요. 결과를 예측값 순으로 정렬해 쓰면 행 순서가 바뀌어요. 주문번호와 예측의 짝은 그대로 지켜요.', 'code:index=False'))

# 9. Save the whole pipeline, not only the model.
g9 = (BASE + FIT + 'import joblib\n\nbefore = pipeline.predict(X_new)\n# 이 줄을 고쳐 전처리 기준까지 든 pipeline 전체를 저장하세요.\n'
      'joblib.dump(pipeline.named_steps["model"], "delivery-pipeline.joblib")\nrestored = joblib.load("delivery-pipeline.joblib")\n'
      'print(bool(np.allclose(before, restored.predict(X_new))))\nprint(float(restored.named_steps["prep"].named_transformers_["num"].named_steps["fill"].statistics_[0]))\n')
g9_sol = g9.replace('joblib.dump(pipeline.named_steps["model"], "delivery-pipeline.joblib")\n',
                    '# Pipeline 전체를 저장하면 학습한 전처리 기준과 모델이 함께 파일에 들어가요.\njoblib.dump(pipeline, "delivery-pipeline.joblib")\n')
h9 = (Script(g9)
      .say('모델만 저장하면 전처리 기준이 빠져요. 다시 열어도 같은 예측이 나오게 pipeline 전체를 저장해야 해요.', 'text:전처리 기준까지 든 pipeline 전체를 저장하세요.')
      .run('print(bool(np.allclose', error='ValueError')
      .say('ValueError예요. 모델만 불러와 지역 글자가 든 새 표를 받을 수 없어요.', 'output')
      .patch('joblib.dump(pipeline.named_steps["model"],', 'joblib.dump(pipeline,', 'pipeline.named_steps["model"]을 pipeline으로 바꿔요.')
      .run('print(bool(np.allclose', 'print(float(restored')
      .say('True와 3.5예요. 다시 연 파이프라인이 같은 예측을 하고 거리 대체 평균 3.5도 함께 돌아왔어요.', 'output')
      .say('조심하세요. 같은 환경에서 직접 저장한 파일만 열어요. 믿을 수 없는 joblib 파일은 열 때 코드가 실행될 수 있어요.', 'code:joblib.dump(pipeline,'))

C_TRAIN = [{'train_rows': OTHER_TRAIN, 'new_rows': NEW_A}, {'train_rows': THREE_ZONES}]

SPECS = [
    code_step('stp_7824a8e7-ed48-4ffb-a642-bc7db40ce978', 'df[["distance", "zone"]]로 예측할 입력만 고르세요', '예측할 때 쓸 입력과 맞힐 정답, 보관만 할 번호를 나눠 직접 골라요.',
              'order_id만 빼면 minutes가 입력에 남아 새 입력과 열이 다르다. df[["distance", "zone"]]로 고쳐 True를 확인한다. 채점은 다른 배송 표로 실행한다.',
              'delivery.csv에는 주문번호·거리·지역·걸린 시간이 있고, new.csv의 새 배송은 걸린 시간을 아직 몰라요. 입력은 예측할 때 이미 아는 열, 정답은 맞힐 열이에요.',
              'X_train 줄을 고쳐 X_train에 새 배송에도 있는 입력 distance와 zone만 남기세요. 채점은 다른 배송 표로도 실행해요.',
              ['코드 실행을 눌러 입력 열을 확인하세요.', '`df.drop(columns=["order_id"])`를 `df[["distance", "zone"]]`로 고치세요.', '코드 실행을 눌러 True가 나오는지 확인하세요.', SUB],
              g1, g1_sol, h1, {h1.actions[-1]['text']: W}, files=FILES, cases=C_TRAIN,
              reject=[([['X_train = df[["distance", "zone"]]\n', 'X_train = df.drop(columns=["minutes"])\n']], 'Keeping the order number'),
                      ([['print(y_train.tolist())\n', 'print([10, 20, 30, 40, 50, 60])\n']], 'Typing the answers')],
              accept=[([['X_train = df[["distance", "zone"]]\n', 'X_train = df.drop(columns=["order_id", "minutes"])\n']], 'Dropping both')], timeout=T),
    code_step('stp_04e49b70-d4bd-4228-be8d-600ca82ba5a0', '"cat" 갈래로 zone을 원핫 열로 바꾸세요', '숫자 열과 범주 열을 각자 처리해 ColumnTransformer로 묶고 출력 열을 확인해요.',
              '숫자 갈래만 있으면 [6, 1]이다. "cat" 갈래를 더해 [6, 3]과 north·south 원핫 열을 확인한다. 채점은 지역이 셋인 표로 실행한다.',
              '`ColumnTransformer`는 열마다 다른 전처리를 적용해 한 행렬로 묶고, 적지 않은 열은 버려요. 범주 열은 빈칸을 가장 흔한 값으로 채운 뒤 `OneHotEncoder`로 지역마다 0·1 열을 만들어요.',
              '주석 자리를 고쳐 zone 열을 가장 흔한 값으로 채운 뒤 원핫 열로 바꾸는 "cat" 갈래를 더하세요. 채점은 지역이 셋인 표로도 실행해요.',
              ['코드 실행을 눌러 출력 열을 확인하세요.', '주석 아래에 `("cat", Pipeline([("fill", SimpleImputer(strategy="most_frequent")), ("encode", OneHotEncoder(handle_unknown="ignore", sparse_output=False))]), ["zone"])`를 쓰세요.',
               '코드 실행을 눌러 [6, 3]이 나오는지 확인하세요.', SUB],
              g2, g2_sol, h2, {h2.actions[-1]['text']: W}, files=FILES, cases=C_TRAIN,
              reject=[([[', sparse_output=False))]), ["zone"])\n', ', sparse_output=False))]), ["distance"])\n']], 'One-hot of the distance'),
                      ([['print(list(matrix.shape))\n', 'print([6, 3])\n']], 'Typing the shape')],
              accept=[([['OneHotEncoder(handle_unknown="ignore", sparse_output=False)', 'OneHotEncoder(sparse_output=False, handle_unknown="ignore")']], 'Keyword order')], timeout=T),
    code_step('stp_cf760835-2939-47bb-8d48-fe23da31864b', 'preprocess.transform(X_new)로 훈련 기준만 적용하세요', '새 표에는 훈련에서 배운 기준을 transform으로만 적용하고 다시 fit하지 않아요.',
              'fit_transform이면 새 표로 다시 배워 [3, 4], 평균 5.0이다. transform으로 고쳐 [3, 3], 3.5, west의 [0.0, 0.0]을 확인한다. 채점은 다른 훈련·새 표로 실행한다.',
              '새 표에는 빈 거리와 훈련에 없던 지역 west가 있어요. `fit`은 기준을 배우고 `transform`은 배운 기준을 적용해요. 출력은 새 행렬의 모양, 훈련에서 배운 거리 평균, 둘째 새 배송의 지역 칸이에요.',
              'new_matrix 줄을 고쳐 새 표에는 훈련에서 배운 기준을 transform으로만 적용하세요. 채점은 다른 표로도 실행해요.',
              ['코드 실행을 눌러 세 줄을 확인하세요.', '`preprocess.fit_transform(X_new)`를 `preprocess.transform(X_new)`로 고치세요.', '코드 실행을 눌러 3.5가 나오는지 확인하세요.', SUB],
              g3, g3_sol, h3, {h3.actions[-1]['text']: W}, files=FILES, cases=[{'train_rows': THREE_ZONES}, {'train_rows': OTHER_TRAIN, 'new_rows': NEW_DESC}],
              reject=[([['new_matrix = preprocess.transform(X_new)\n', 'new_matrix = preprocess.fit(X_new).transform(X_new)\n']], 'Refitting on the new table'),
                      ([['print(float(preprocess.named_transformers_["num"].named_steps["fill"].statistics_[0]))\n', 'print(3.5)\n']], 'Typing the mean')],
              accept=[([['new_matrix = preprocess.transform(X_new)\n', 'new_matrix = preprocess.fit(X_train).transform(X_new)\n']], 'Refitting on the training table')], timeout=T),
    code_step('stp_1300dfb3-6b1d-40a8-b531-7c350058d033', 'Pipeline에 ("prep", preprocess)를 앞세우세요', '전처리와 모델을 Pipeline으로 묶어 fit은 둘 다 배우고 predict는 배운 기준으로 예측만 하게 해요.',
              '모델만 있는 Pipeline은 지역 글자를 바꾸지 못해 ValueError다. ("prep", preprocess)를 앞에 넣어 [20.0, 35.0, 80.0]을 확인한다. 채점은 다른 훈련·새 표로 실행한다.',
              '`Pipeline([(이름, 단계), ...])`은 단계를 차례로 이어요. fit은 앞 단계의 기준을 배우며 다음 단계로 넘기고, predict는 배운 기준으로 바꾼 뒤 마지막 모델로 예측해요.',
              'pipeline 줄을 고쳐 전처리 preprocess 다음에 LinearRegression이 오는 Pipeline을 만드세요. 채점은 다른 표로도 실행해요.',
              ['코드 실행을 눌러 ValueError가 나오는지 확인하세요.', '목록 맨 앞에 `("prep", preprocess)`를 넣으세요.', '코드 실행을 눌러 [20.0, 35.0, 80.0]이 나오는지 확인하세요.', SUB],
              g4, g4_sol, h4, {h4.actions[-1]['text']: W}, files=FILES, cases=[{'train_rows': OTHER_TRAIN, 'new_rows': NEW_DESC}, {'train_rows': THREE_ZONES}],
              reject=[([['Pipeline([("prep", preprocess), ("model", LinearRegression())])', 'Pipeline([("model", LinearRegression()), ("prep", preprocess)])']], 'Model before preprocessing'),
                      ([['print(pipeline.predict(X_new).round(6).tolist())\n', 'print([20.0, 35.0, 80.0])\n']], 'Typing the predictions')],
              accept=[([['pipeline = Pipeline([("prep", preprocess), ("model", LinearRegression())])\n', 'from sklearn.pipeline import make_pipeline\npipeline = make_pipeline(preprocess, LinearRegression())\n']], 'make_pipeline')], timeout=T),
    code_step('stp_1042f95e-0b9a-49ca-986c-ac76492213d6', 'cross_validate에 pipeline 전체를 넘기세요', '교차검증에서는 fold마다 그 훈련 몫으로 전처리까지 다시 배워야 함을 직접 확인해요.',
              '미리 fit한 행렬을 넘기면 세 fold가 모두 평균 3.5를 쓴다. cross_validate(pipeline, X_train, y_train, ...)로 고쳐 [4.5, 3.5, 2.5]를 확인한다. 채점은 다른 훈련 표로 실행한다.',
              '`cross_validate`는 표를 fold로 나눠 번갈아 평가해요. `return_estimator=True`면 fold마다 학습한 모델을 돌려줘요. 전처리를 밖에서 전체 표로 fit하면 평가 몫의 거리도 평균에 들어가요.',
              'result 줄을 고쳐 미리 fit한 행렬 대신 pipeline 전체와 원래 표 X_train을 교차검증에 넘기세요. 채점은 다른 훈련 표로도 실행해요.',
              ['코드 실행을 눌러 fold별 평균을 확인하세요.', '`LinearRegression(), preprocess.fit_transform(X_train)`을 `pipeline, X_train`으로 고치세요.', '코드 실행을 눌러 평균이 fold마다 다른지 확인하세요.', SUB],
              g5, g5_sol, h5, {h5.actions[-1]['text']: W}, files=FILES, cases=[{'train_rows': THREE_ZONES}, {'train_rows': OTHER_TRAIN}],
              reject=[([['result = cross_validate(pipeline, X_train, y_train,', 'result = cross_validate(pipeline, preprocess.fit_transform(X_train), y_train,']], 'Pipeline on the prefitted matrix'),
                      ([['print([float(getattr(m, "named_steps", {"prep": preprocess})["prep"].named_transformers_["num"].named_steps["fill"].statistics_[0]) for m in result["estimator"]])\n',
                         'print([4.5, 3.5, 2.5])\n']], 'Typing the means')],
              accept=[([['result = cross_validate(pipeline, X_train, y_train,', 'result = cross_validate(estimator=pipeline, X=X_train, y=y_train,']], 'Keyword arguments')], timeout=T),
    code_step('stp_fc59b750-a4d9-4feb-8db8-8314d41c7fb0', 'model__alpha로 Pipeline 안 Ridge의 설정을 탐색하세요', 'Pipeline 안 단계의 설정은 단계 이름과 설정 이름을 밑줄 두 개로 이어 지정해요.',
              'prep__alpha는 없는 설정이라 ValueError다. model__alpha로 고쳐 후보 2, 예측 [3], RMSE 1.85를 확인한다. 채점은 다른 후보와 표로 실행한다.',
              '`GridSearchCV`는 설정 후보를 교차검증으로 비교해 가장 좋은 설정으로 다시 학습해요. Pipeline 안의 설정은 `단계이름__설정이름`으로 적어요. 여기서 Ridge 단계의 이름은 model이에요.',
              'search 줄을 고쳐 Pipeline 안 model 단계의 alpha 후보를 탐색하세요. 채점은 다른 후보와 표로도 실행해요.',
              ['코드 실행을 눌러 ValueError가 나오는지 확인하세요.', '`"prep__alpha"`를 `"model__alpha"`로 고치세요.', '코드 실행을 눌러 RMSE가 나오는지 확인하세요.', SUB],
              g6, g6_sol, h6, {h6.actions[-1]['text']: W}, files=FILES, cases=[{'alphas': [10.0]}, {'train_rows': THREE_ZONES, 'alphas': [0.01, 0.1, 1.0]}],
              reject=[([['{"model__alpha": alphas}', '{"alpha": alphas}']], 'Missing the step name'),
                      ([['print(round(float((-search.best_score_) ** 0.5), 3))\n', 'print(1.85)\n']], 'Typing the RMSE')],
              accept=[([['{"model__alpha": alphas}', 'dict(model__alpha=list(alphas))']], 'dict keyword')], timeout=T),
    code_step('stp_ee0ebbeb-e420-422d-af9d-d2aaba66f930', 'preprocess.fit_transform(X_train)로 신경망에 숫자 행렬을 넘기세요', '신경망에는 같은 전처리로 만든 숫자 행렬을 넘기고, 기준은 훈련 표로 배워요.',
              '표 그대로면 전처리 기준이 없어 NotFittedError다. preprocess.fit_transform(X_train).astype("float32")로 고쳐 [3, 1], True를 확인한다. 채점은 다른 표로 모양과 유한값만 본다.',
              'Keras의 Dense 층은 숫자만 계산해요. 그래서 지역 글자는 전처리로 원핫 숫자 열로 바꾼 뒤 넘겨요. 훈련 표로 기준을 배운 뒤 새 표에는 같은 기준을 적용해요. 학습한 실수 값은 비교하지 않아요.',
              'train_matrix 줄을 고쳐 훈련 표를 전처리로 바꾼 숫자 행렬로 만드세요. 채점은 다른 표로도 실행해요.',
              ['코드 실행을 눌러 NotFittedError가 나오는지 확인하세요.', '`train_matrix = X_train`을 `train_matrix = preprocess.fit_transform(X_train).astype("float32")`로 고치세요.', '코드 실행을 눌러 [3, 1]이 나오는지 확인하세요.', SUB],
              g7, g7_sol, h7, {h7.actions[-1]['text']: '실제 Keras·scikit-learn 동작을 정확히 말해요.'}, files=FILES, cases=[{'new_rows': NEW_A}, {'train_rows': THREE_ZONES}],
              reject=[([['train_matrix = preprocess.fit_transform(X_train).astype("float32")\n', 'train_matrix = X_train.to_numpy()\n']], 'Strings into Dense'),
                      ([['print(list(predictions.shape))\n', 'print([3, 1])\n']], 'Typing the shape')],
              accept=[([['train_matrix = preprocess.fit_transform(X_train).astype("float32")\n', 'train_matrix = np.asarray(preprocess.fit_transform(X_train), dtype="float32")\n']], 'np.asarray')], timeout=45),
    code_step('stp_c9ec6bf7-8d92-4182-8519-3deb715aed81', 'index=False로 주문번호와 예측만 파일에 쓰세요', '결과 파일에 판다스의 행 번호를 넣지 않고 주문번호와 예측의 대응을 지켜요.',
              'to_csv 기본값이면 Unnamed: 0 열이 생긴다. index=False를 더해 [\'order_id\', \'minutes\']와 새 배송 순서를 확인한다. 채점은 예측이 거꾸로 커지는 새 표로도 실행한다.',
              '`to_csv`는 표를 파일로 내보내요. 기본으로는 판다스의 행 번호도 첫 열로 써서, 다시 읽으면 이름 없는 열이 생겨요. 주문번호는 원래 순서 그대로 예측과 짝을 이뤄요.',
              'to_csv 줄을 고쳐 판다스의 행 번호는 빼고 두 열만 파일에 쓰세요. 채점은 다른 새 표로도 실행해요.',
              ['코드 실행을 눌러 열 이름을 확인하세요.', '`answer.to_csv("answer.csv")`에 `index=False`를 더하세요.', '코드 실행을 눌러 두 열만 나오는지 확인하세요.', SUB],
              g8, g8_sol, h8, {h8.actions[-1]['text']: W}, files=FILES, cases=[{'new_rows': NEW_DESC}, {'train_rows': THREE_ZONES, 'new_rows': NEW_A}],
              reject=[([['answer.to_csv("answer.csv", index=False)\n', 'answer.sort_values("minutes").to_csv("answer.csv", index=False)\n']], 'Sorting breaks the original order'),
                      ([['print(restored["order_id"].tolist())\n', 'print([201, 202, 203])\n']], 'Typing the ids')],
              accept=[([['answer.to_csv("answer.csv", index=False)\n', 'answer.to_csv("answer.csv", index=False, header=True)\n']], 'Explicit header')], timeout=T),
    code_step('stp_126392df-cd64-4c73-88d1-a266183d1bf9', 'joblib.dump(pipeline, ...)로 전처리까지 저장하세요', 'Pipeline 전체를 저장해야 학습한 전처리 기준과 모델이 함께 복원됨을 직접 확인해요.',
              '모델만 저장하면 다시 연 쪽이 지역 글자를 받지 못해 ValueError다. joblib.dump(pipeline, ...)로 고쳐 True와 3.5를 확인한다. 채점은 다른 훈련·새 표로 실행한다.',
              '`joblib.dump`는 파이썬 객체를 파일에 저장하고 `joblib.load`가 다시 열어요. 모델 단계만 저장하면 전처리 기준이 빠지고, Pipeline 전체를 저장하면 둘이 함께 들어가요.',
              'joblib.dump 줄을 고쳐 전처리 기준까지 든 pipeline 전체를 저장하세요. 채점은 다른 표로도 실행해요.',
              ['코드 실행을 눌러 ValueError가 나오는지 확인하세요.', '`pipeline.named_steps["model"]`을 `pipeline`으로 고치세요.', '코드 실행을 눌러 True와 3.5가 나오는지 확인하세요.', SUB],
              g9, g9_sol, h9, {h9.actions[-1]['text']: W, h9.actions[0]['text']: '저장 범위와 같은 예측의 관계를 실제 실행 결과대로 말해요.'}, files=FILES, cases=[{'train_rows': THREE_ZONES}, {'train_rows': OTHER_TRAIN, 'new_rows': NEW_DESC}],
              reject=[([['joblib.dump(pipeline, "delivery-pipeline.joblib")\n', 'joblib.dump(preprocess, "delivery-pipeline.joblib")\n']], 'Saving only the preprocessing'),
                      ([['print(bool(np.allclose(before, restored.predict(X_new))))\n', 'print(True)\n'],
                        ['print(float(restored.named_steps["prep"].named_transformers_["num"].named_steps["fill"].statistics_[0]))\n', 'print(3.5)\n']], 'Typing the result')],
              accept=[([['joblib.dump(pipeline, "delivery-pipeline.joblib")\n', 'joblib.dump(pipeline, filename="delivery-pipeline.joblib")\n']], 'filename keyword')], timeout=T),
]
