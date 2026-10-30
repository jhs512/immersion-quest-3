"""aice-tensorflow: 7 answer-picking steps -> coding steps (2026-10-30).

Each step edits one line of a tiny Keras model on CPU: the Input layer, Dense units, the computation of an
untrained prediction, compile, fit epochs, validation data and the 2-D shape of new inputs. Grading never
compares trained float values across machines: it prints shapes, counts, configured names and booleans
(weights changed, val_loss equals evaluate on the given validation table). Prepared cases rerun with
other feature counts, units, inputs, learning rates and epochs, so typed outputs and the starter fail."""
from _kit import Script, code_step

OPENING = ['이 수업에서는 Keras로 아주 작은 신경망을 직접 만들어요. 입력 모양·층·학습 규칙·학습·예측을 한 곳씩 써요.',
           '모델 만들기, compile, fit, predict가 각각 무엇을 바꾸는지 실행 결과로 구별해요.']
PRD_SCOPE = ['두 챕터·두 단원·아홉 스텝에서 같은 거리-시간 예측을 작은 Keras 모델로 다뤄요.',
             'Input의 특성 수·Dense의 출력 수·초기 가중치로 직접 계산한 예측·compile·fit의 epoch·검증 자료·새 입력의 2차원 모양을 한 곳씩 직접 고쳐 써요.']
PRD_GRADING = ['직접 고친 코드를 실제 파이썬·TensorFlow로 실행해 판정해요. 실행·해설만으로 성공시키지 않아요.',
               '학습한 실수 값은 기계마다 조금 다를 수 있어 비교하지 않아요. 모양·기록 수·설정 이름·가중치 변화 여부·검증 손실과 평가의 일치 같은 결정적인 결과로 채점해요.',
               '다른 특성 수·출력 수·입력·학습률·epoch로 다시 실행해 기준 풀이와 비교하고, 결과를 글자로 적은 답·다른 최적화기·validation_split은 거절해요.',
               '마지막 도전(stp_228a312c-44f8-4f1f-bab3-2aaa29978f5c): 실제 Python 실행과 다른 준비 자료의 결과를 검사해요. 시작 코드는 실패하고 동등한 풀이도 통과해야 해요.']
PRD_NARRATION = ['층·설정·호출 한 곳씩 고치고 실제 모양·기록·출력을 읽어요.',
                 '행 수와 특성 수·units·초기 가중치와 학습·compile과 fit·검증 자료·1차원 입력을 조심할 지점으로 짚어요.']

HEAD = ('import os\nos.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")\nimport numpy as np\nimport tensorflow as tf\nfrom tensorflow import keras\n\n'
        '# 작은 CPU 실습이 다른 작업의 자원을 지나치게 쓰지 않게 해요.\ntf.config.threading.set_intra_op_parallelism_threads(1)\n'
        'tf.config.threading.set_inter_op_parallelism_threads(1)\nkeras.utils.set_random_seed(7)\n')
SUB = '수정한 코드를 제출하세요.'
W = '실제 Keras 동작을 정확히 말해요.'
T = 45

t1 = (HEAD + '# 한 배송의 특성 수예요.\nfeatures = 1\n'
      '# 이 줄을 고쳐 맨 앞에 한 행의 특성 수 features를 받는 Input 층을 더하세요.\nmodel = keras.Sequential([keras.layers.Dense(1)])\nprint(list(model.input_shape))\n')
t1_sol = t1.replace('model = keras.Sequential([keras.layers.Dense(1)])',
                    '# Input의 shape는 한 행(배송 하나)의 모양이에요. 행 수는 정하지 않아 None으로 보여요.\nmodel = keras.Sequential([keras.Input(shape=(features,)), keras.layers.Dense(1)])')
u1 = (Script(t1)
      .say('모델이 한 배송에 특성 몇 개를 받을지 정해야 해요. 맨 앞에 Input 층을 더해요.', 'text:model 줄을 고쳐 맨 앞에 한 행의 특성 수 features를 받는 Input 층을 더하세요.')
      .run('print(list(model.input_shape))', error='AttributeError')
      .say('AttributeError예요. 입력 모양을 모르는 모델은 아직 만들어지지 않았어요.', 'output')
      .patch('keras.Sequential([keras.layers.Dense(1)])', 'keras.Sequential([keras.Input(shape=(features,)), keras.layers.Dense(1)])', '목록 맨 앞에 keras.Input(shape=(features,))를 넣어요.')
      .run('print(list(model.input_shape))')
      .say('[None, 1]이에요. 행 수는 정하지 않았고 한 행에 특성 1개예요.', 'output')
      .say('조심하세요. shape의 1은 배송 한 건만 받는다는 뜻이 아니에요. 배송 하나에 든 특성 수예요.', 'code:shape=(features,)'))

t2 = (HEAD + '# 배송마다 만들 출력 수예요.\noutputs = 4\n# 이 줄의 Dense를 고쳐 배송마다 출력 outputs개를 만드세요.\n'
      'model = keras.Sequential([keras.Input(shape=(1,)), keras.layers.Dense(1)])\nprint(list(model.output_shape))\n')
t2_sol = t2.replace('keras.layers.Dense(1)])', '# Dense의 첫 인수 units가 그 층의 출력 수예요. 출력마다 다른 가중치로 입력 × 가중치 + 편향을 계산해요.\n                          keras.layers.Dense(outputs)])')
u2 = (Script(t2)
      .say('Dense는 출력마다 입력 × 가중치 + 편향을 계산해요. 출력 수를 outputs로 정해야 해요.', 'text:Dense를 고쳐 배송마다 출력 outputs개를 만드세요.')
      .run('print(list(model.output_shape))')
      .say('[None, 1]이에요. 배송마다 출력이 하나예요.', 'output')
      .patch('keras.layers.Dense(1)])', 'keras.layers.Dense(outputs)])', 'Dense(1)을 Dense(outputs)로 바꿔요.')
      .run('print(list(model.output_shape))')
      .say('[None, 4]예요. 배송마다 출력 네 개를 만들어요.', 'output')
      .say('조심하세요. Dense(4)의 4는 받을 배송 수가 아니라 배송마다의 출력 수예요.', 'code:Dense(outputs)'))

t3 = (HEAD + '# 가중치 1, 편향 0으로 시작하게 했어요. 아직 fit하지 않았어요.\n'
      'model = keras.Sequential([keras.Input(shape=(1,)), keras.layers.Dense(1, kernel_initializer="ones", bias_initializer="zeros")])\n'
      'rows = [[2.0], [3.0]]\nX_test = np.array(rows, dtype="float32")\nweights, bias = model.get_weights()\n'
      '# 이 줄을 고쳐 지금 가중치로 입력 × 가중치 + 편향을 직접 계산하세요.\nmanual = X_test * 0\n'
      'print(manual.tolist())\nprint(model.predict(X_test, verbose=0).tolist())\n')
t3_sol = t3.replace('manual = X_test * 0\n', '# 행렬 곱 @로 입력 × 가중치를 하고 편향을 더해요. fit 전이라 초기 가중치 그대로예요.\nmanual = X_test @ weights + bias\n')
u3 = (Script(t3)
      .say('fit 없이도 예측 숫자가 나와요. 지금 가중치로 같은 계산을 직접 해서 비교해야 해요.', 'text:manual 줄을 고쳐 지금 가중치로 입력 × 가중치 + 편향을 직접 계산하세요.')
      .run('print(manual.tolist())', 'print(model.predict')
      .say('[[0.0], [0.0]]과 [[2.0], [3.0]]이에요. 직접 계산이 아직 0이에요.', 'output')
      .patch('manual = X_test * 0\n', 'manual = X_test @ weights + bias\n', 'X_test @ weights + bias로 바꿔요.')
      .run('print(manual.tolist())', 'print(model.predict')
      .say('[[2.0], [3.0]]으로 같아요. predict는 초기 가중치 1과 편향 0으로 계산했을 뿐이에요.', 'output')
      .say('조심하세요. predict가 숫자를 냈다고 자료의 관계를 배운 게 아니에요. 아직 학습 전이에요.', 'code:X_test @ weights + bias'))

t4 = (HEAD + 'model = keras.Sequential([keras.Input(shape=(1,)), keras.layers.Dense(1, kernel_initializer="zeros", bias_initializer="zeros")])\n'
      'rate = 0.1\n# 확인용: compile 전 가중치를 복사해 둬요.\nbefore = [w.copy() for w in model.get_weights()]\n'
      '# 이 주석 아래에 학습률 rate의 SGD와 mse 손실로 학습 규칙을 정하는 compile 줄을 쓰세요.\n'
      'print(model.optimizer.__class__.__name__)\nprint(round(float(model.optimizer.learning_rate.numpy()), 4))\n'
      '# 확인용 출력: 가중치가 복사본과 모두 같으면 True예요. 이 줄의 문법은 몰라도 돼요.\n'
      'print(all(np.array_equal(a, b) for a, b in zip(before, model.get_weights())))\n')
t4_sol = t4.replace('# 이 주석 아래에 학습률 rate의 SGD와 mse 손실로 학습 규칙을 정하는 compile 줄을 쓰세요.\n',
                    '# 이 주석 아래에 학습률 rate의 SGD와 mse 손실로 학습 규칙을 정하는 compile 줄을 쓰세요.\n'
                    '# compile은 학습 규칙(최적화 방법·손실)만 정해요. 가중치는 아직 그대로예요.\n'
                    'model.compile(optimizer=keras.optimizers.SGD(learning_rate=rate), loss="mse")\n')
u4 = (Script(t4)
      .say('학습하기 전에 학습 규칙을 정해야 해요. compile 줄에 SGD와 mse를 써요.', 'text:주석 아래에 학습률 rate의 SGD와 mse 손실로 학습 규칙을 정하는 compile 줄을 쓰세요.')
      .run('print(model.optimizer', error='AttributeError')
      .say('NoneType 뒤에 AttributeError예요. compile 전이라 최적화기가 없어요.', 'output')
      .patch('print(model.optimizer.__class__.__name__)\n', 'model.compile(optimizer=keras.optimizers.SGD(learning_rate=rate), loss="mse")\nprint(model.optimizer.__class__.__name__)\n',
             'print 앞에 compile 줄을 써요.')
      .run('print(model.optimizer', 'print(all(')
      .say('SGD, 0.1, True예요. 규칙이 정해졌고 가중치는 그대로예요.', 'output')
      .say('조심하세요. compile에 자료를 넘기지 않아요. 가중치를 바꾸는 건 다음의 fit이에요.', 'code:model.compile('))

FIT_HEAD = (HEAD + 'model = keras.Sequential([keras.Input(shape=(1,)), keras.layers.Dense(1, kernel_initializer="zeros", bias_initializer="zeros")])\n'
            'X_train = np.array([[1.0], [2.0]], dtype="float32")\ny_train = np.array([[2.0], [4.0]], dtype="float32")\n'
            'model.compile(optimizer=keras.optimizers.SGD(learning_rate=0.1), loss="mse")\n')
t5 = (FIT_HEAD + '# 훈련 표 전체를 학습할 횟수예요.\nrounds = 1\n# 확인용: fit 전 가중치를 복사해 둬요.\nbefore = [w.copy() for w in model.get_weights()]\n'
      '# 이 줄을 고쳐 훈련 표 전체를 rounds번 학습하세요.\nhistory = model.fit(X_train, y_train, epochs=0, batch_size=2, shuffle=False, verbose=0)\n'
      'print(len(history.history.get("loss", [])))\n'
      '# 확인용 출력: 가중치가 하나라도 바뀌었으면 True예요. 이 줄의 문법은 몰라도 돼요.\n'
      'print(any(not np.array_equal(a, b) for a, b in zip(before, model.get_weights())))\n')
t5_sol = t5.replace('epochs=0,', 'epochs=rounds,').replace('# 이 줄을 고쳐 훈련 표 전체를 rounds번 학습하세요.\n',
                                                         '# 이 줄을 고쳐 훈련 표 전체를 rounds번 학습하세요.\n# epochs는 훈련 표 전체를 몇 번 학습할지예요. fit이 실제로 가중치를 바꿔요.\n')
u5 = (Script(t5)
      .say('fit이 훈련 표를 학습하게 해야 해요. epochs를 rounds로 고쳐요.', 'text:fit 줄을 고쳐 훈련 표 전체를 rounds번 학습하세요.')
      .run('print(len(history', 'print(any(')
      .say('0과 False예요. epochs=0이라 한 번도 학습하지 않았어요.', 'output')
      .patch('epochs=0,', 'epochs=rounds,', 'epochs=0을 epochs=rounds로 바꿔요.')
      .run('print(len(history', 'print(any(')
      .say('1과 True예요. 한 epoch 학습해 loss 기록이 하나 생기고 가중치가 바뀌었어요.', 'output')
      .say('조심하세요. loss 기록은 배송 한 건마다가 아니라 epoch마다 하나씩 쌓여요.', 'code:epochs=rounds'))

t6 = (FIT_HEAD + '# 검증 표는 이 fit의 가중치 학습에 직접 넣지 않아요.\nvalid_rows = [[3.0]]\nvalid_targets = [[6.0]]\nX_valid = np.array(valid_rows, dtype="float32")\ny_valid = np.array(valid_targets, dtype="float32")\nrounds = 3\n'
      '# 이 줄에 validation_data를 더해 epoch마다 검증 표의 손실도 기록하세요.\n'
      'history = model.fit(X_train, y_train, epochs=rounds, batch_size=2, shuffle=False, verbose=0)\n'
      'print(sorted(history.history))\nprint(len(history.history.get("val_loss", [])))\n'
      '# 확인용 출력: 마지막 val_loss가 검증 표를 따로 평가한 값과 같으면 True예요. 이 줄의 문법은 몰라도 돼요.\n'
      'print(bool(np.isclose(history.history.get("val_loss", [np.nan])[-1], model.evaluate(X_valid, y_valid, verbose=0))))\n')
t6_sol = t6.replace('batch_size=2, shuffle=False, verbose=0)\nprint(sorted', 'batch_size=2, shuffle=False, verbose=0,\n                    validation_data=(X_valid, y_valid))\nprint(sorted').replace(
    '# 이 줄에 validation_data를 더해 epoch마다 검증 표의 손실도 기록하세요.\n',
    '# 이 줄에 validation_data를 더해 epoch마다 검증 표의 손실도 기록하세요.\n# validation_data의 표로 epoch가 끝날 때마다 손실을 재요. 가중치 학습에는 쓰지 않아요.\n')
u6 = (Script(t6)
      .say('훈련 손실과 따로 검증 표의 손실도 보고 싶어요. fit에 validation_data를 더해야 해요.', 'text:fit 줄에 validation_data를 더해 epoch마다 검증 표의 손실도 기록하세요.')
      .run('print(sorted(history', 'print(bool(')
      .say("['loss'], 0, False예요. 훈련 손실만 기록됐어요.", 'output')
      .patch('batch_size=2, shuffle=False, verbose=0)\nprint(sorted', 'batch_size=2, shuffle=False, verbose=0,\n                    validation_data=(X_valid, y_valid))\nprint(sorted',
             '괄호 안 끝에 validation_data=(X_valid, y_valid)를 더해요.')
      .run('print(sorted(history', 'print(bool(')
      .say("['loss', 'val_loss'], 3, True예요. epoch마다 검증 손실이 쌓였고 마지막 값은 검증 표를 평가한 값과 같아요.", 'output')
      .say('조심하세요. validation_split은 훈련 표의 일부를 떼어 써요. 따로 준비한 검증 표를 쓰려면 validation_data예요.', 'code:validation_data=(X_valid, y_valid)'))

t7 = (FIT_HEAD + 'model.fit(X_train, y_train, epochs=1, batch_size=2, shuffle=False, verbose=0)\n# 예측할 새 배송들의 거리예요.\ndistances = [3.0, 4.0]\n'
      '# 이 줄을 고쳐 새 배송마다 한 행, 특성 한 열인 2차원 입력을 만드세요.\nX_test = np.array([distances], dtype="float32")\n'
      'predictions = model.predict(X_test, verbose=0)\nprint(list(predictions.shape))\n')
t7_sol = t7.replace('X_test = np.array([distances], dtype="float32")\n', '# 바깥 목록이 행(배송), 안쪽 목록이 그 배송의 특성이에요. 배송마다 [거리] 한 칸이에요.\nX_test = np.array([[d] for d in distances], dtype="float32")\n')
u7 = (Script(t7)
      .say('새 배송 두 건을 한 번에 예측해요. 배송마다 한 행, 특성 한 열로 입력을 만들어야 해요.', 'text:X_test 줄을 고쳐 새 배송마다 한 행, 특성 한 열인 2차원 입력을 만드세요.')
      .run('print(list(predictions.shape))', error='ValueError')
      .say('ValueError예요. 한 행에 거리 두 개를 넣어 특성 1개짜리 입력과 맞지 않아요.', 'output')
      .patch('X_test = np.array([distances], dtype="float32")\n', 'X_test = np.array([[d] for d in distances], dtype="float32")\n', '거리마다 [d]로 감싸 한 행씩 만들어요.')
      .run('print(list(predictions.shape))')
      .say('[2, 1]이에요. 앞은 새 배송 수, 뒤는 배송마다 나온 예측값 수예요.', 'output')
      .say('조심하세요. [distances]는 행이 하나예요. 배송 수만큼 행을 만들어야 해요.', 'code:[[d] for d in distances]'))

SPECS = [
    code_step('stp_7c799198-5712-48f1-8def-b6a2f5c726ca', 'Input(shape=(features,))로 한 행의 특성 수를 정하세요', 'Input의 shape는 행 수가 아니라 한 행의 특성 수임을 써서 확인해요.',
              'Input 없이 만든 모델은 input_shape가 없어 AttributeError다. keras.Input(shape=(features,))를 맨 앞에 더해 [None, 1]을 확인한다. 채점은 다른 특성 수로 실행한다.',
              '`keras.Input(shape=(특성 수,))`는 모델이 한 행(배송 하나)에 받을 특성 수를 정해요. 행 수는 정하지 않아서 input_shape의 앞자리는 None이에요.',
              'model 줄을 고쳐 맨 앞에 한 행의 특성 수 features를 받는 Input 층을 더하세요. 채점은 다른 특성 수로도 실행해요.',
              ['코드 실행을 눌러 AttributeError가 나오는지 확인하세요.', '목록 맨 앞에 `keras.Input(shape=(features,))`를 넣으세요.', '코드 실행을 눌러 [None, 1]이 나오는지 확인하세요.', SUB],
              t1, t1_sol, u1, {u1.actions[-1]['text']: W}, cases=[{'features': 3}, {'features': 7}],
              reject=[([['keras.Input(shape=(features,))', 'keras.Input(shape=(1,))']], 'Typing one feature'),
                      ([['keras.Input(shape=(features,))', 'keras.Input(shape=(features, 1))']], 'An extra dimension')],
              accept=[([['keras.Input(shape=(features,))', 'keras.Input((features,))']], 'Positional shape')], timeout=T),
    code_step('stp_88881a17-200b-4d8e-8e4b-ceb0c583ca64', 'Dense(outputs)로 출력 수를 정하세요', 'Dense의 units가 배송마다의 출력 수임을 써서 확인해요.',
              'Dense(1)은 출력이 하나다. Dense(outputs)로 고쳐 [None, 4]를 확인한다. 채점은 다른 출력 수로 실행한다.',
              'Dense 층은 출력마다 입력 × 가중치 + 편향을 계산해요. 회귀 수업의 기울기와 절편이 가중치와 편향에 해당해요. `Dense(4)`는 이 계산을 서로 다른 가중치로 네 번 해요.',
              'Dense를 고쳐 배송마다 출력 outputs개를 만드세요. 채점은 다른 출력 수로도 실행해요.',
              ['코드 실행을 눌러 출력 모양을 확인하세요.', '`Dense(1)`을 `Dense(outputs)`로 고치세요.', '코드 실행을 눌러 [None, 4]가 나오는지 확인하세요.', SUB],
              t2, t2_sol, u2, {u2.actions[-1]['text']: W}, cases=[{'outputs': 2}, {'outputs': 9}],
              reject=[([['keras.layers.Dense(outputs)])', 'keras.layers.Dense(4)])']], 'Typing four'), ([['keras.layers.Dense(outputs)])', 'keras.layers.Dense(1)])']], 'One output')],
              accept=[([['keras.layers.Dense(outputs)])', 'keras.layers.Dense(units=outputs)])']], 'units keyword')], timeout=T),
    code_step('stp_f6f4f1b8-055f-4426-b368-3ba57037145f', 'X_test @ weights + bias로 학습 전 예측을 직접 계산하세요', 'fit 전 predict는 초기 가중치의 계산일 뿐임을 직접 계산해 확인해요.',
              '직접 계산이 0이면 predict와 다르다. X_test @ weights + bias로 고쳐 predict와 같은 [[2.0], [3.0]]을 확인한다. 채점은 다른 입력으로 실행한다.',
              '가중치를 1(ones), 편향을 0(zeros)으로 시작하게 했어요. 아직 fit하지 않았어요. `model.get_weights()`는 지금의 가중치와 편향을 돌려주고, `@`는 행렬 곱이에요.',
              'manual 줄을 고쳐 지금 가중치로 입력 × 가중치 + 편향을 직접 계산하세요. 채점은 다른 입력으로도 실행해요.',
              ['코드 실행을 눌러 manual과 predict를 비교하세요.', '`X_test * 0`을 `X_test @ weights + bias`로 고치세요.', '코드 실행을 눌러 두 결과가 같은지 확인하세요.', SUB],
              t3, t3_sol, u3, {u3.actions[-1]['text']: W}, cases=[{'rows': [[5.0], [-1.0], [0.5]]}, {'rows': [[10.0]]}],
              reject=[([['manual = X_test @ weights + bias\n', 'manual = X_test * 0\n']], 'Zeros'),
                      ([['manual = X_test @ weights + bias\n', 'manual = np.array([[2.0], [3.0]])\n']], 'Typing this input\'s predictions')],
              accept=[([['manual = X_test @ weights + bias\n', 'manual = np.dot(X_test, weights) + bias\n']], 'np.dot')], timeout=T),
    code_step('stp_eb667050-c744-4915-9c64-41dc71423fc8', 'compile로 SGD와 mse 학습 규칙을 정하세요', 'compile은 학습 규칙만 정하고 가중치를 바꾸지 않는 것을 써서 확인해요.',
              'compile 전에는 최적화기가 없어 AttributeError다. compile(optimizer=SGD(learning_rate=rate), loss="mse")를 써서 SGD, 학습률, 가중치 그대로(True)를 확인한다. 채점은 다른 학습률로 실행한다.',
              '`model.compile`은 학습 규칙을 정해요. optimizer는 가중치를 고치는 방법, loss는 오차를 재는 방법이에요. SGD는 기울기 방향으로 학습률만큼 고쳐요.',
              '주석 아래에 학습률 rate의 SGD와 mse 손실로 학습 규칙을 정하는 compile 줄을 쓰세요. 채점은 다른 학습률로도 실행해요.',
              ['코드 실행을 눌러 AttributeError가 나오는지 확인하세요.', '주석 아래에 `model.compile(optimizer=keras.optimizers.SGD(learning_rate=rate), loss="mse")`를 쓰세요.', '코드 실행을 눌러 SGD와 학습률을 확인하세요.', SUB],
              t4, t4_sol, u4, {u4.actions[-1]['text']: W}, cases=[{'rate': 0.05}, {'rate': 0.5}],
              reject=[([['keras.optimizers.SGD(learning_rate=rate)', 'keras.optimizers.Adam(learning_rate=rate)']], 'Adam instead of SGD'),
                      ([['keras.optimizers.SGD(learning_rate=rate)', 'keras.optimizers.SGD(learning_rate=0.1)']], 'Typing the rate')],
              accept=[([['model.compile(optimizer=keras.optimizers.SGD(learning_rate=rate), loss="mse")\n',
                         'model.compile(loss=keras.losses.MeanSquaredError(), optimizer=keras.optimizers.SGD(learning_rate=rate))\n']], 'Loss object first')], timeout=T),
    code_step('stp_b7bee97e-9f29-4439-abc6-40eaae2641aa', 'fit의 epochs=rounds로 실제로 학습하세요', 'fit이 가중치를 바꾸고 epoch마다 loss 기록을 남기는 것을 써서 확인해요.',
              'epochs=0은 기록 0개, 가중치 그대로다. epochs=rounds로 고쳐 기록 1개와 바뀐 가중치(True)를 확인한다. 채점은 다른 epoch 수로 실행한다.',
              'compile로 학습 규칙을 정했어요. `fit`은 훈련 표로 실제 학습해 가중치를 바꿔요. epochs는 훈련 표 전체를 몇 번 학습할지이고, history.history["loss"]에는 epoch마다 손실이 하나씩 쌓여요.',
              'fit 줄을 고쳐 훈련 표 전체를 rounds번 학습하세요. 채점은 다른 epoch 수로도 실행해요.',
              ['코드 실행을 눌러 기록 수와 가중치 변화를 확인하세요.', '`epochs=0`을 `epochs=rounds`로 고치세요.', '코드 실행을 눌러 기록 수와 True를 확인하세요.', SUB],
              t5, t5_sol, u5, {u5.actions[-1]['text']: W}, cases=[{'rounds': 3}, {'rounds': 2}],
              reject=[([['epochs=rounds,', 'epochs=1,']], 'Typing one epoch'), ([['epochs=rounds,', 'epochs=0,']], 'No training')],
              accept=[([['epochs=rounds,', 'epochs=int(rounds),']], 'int(rounds)')], timeout=T),
    code_step('stp_4278f468-bffc-4c1b-bdfc-595f0c50ae26', 'validation_data로 검증 손실을 따로 기록하세요', '훈련 손실과 따로 준 검증 표의 손실을 구별해 기록해요.',
              'validation_data가 없으면 loss만 있다. validation_data=(X_valid, y_valid)를 더해 val_loss 3개와 평가 일치(True)를 확인한다. 채점은 다른 검증 표와 epoch로 실행해 validation_split과 구별한다.',
              'epochs마다 history.history에 기록이 쌓여요. `validation_data=(입력, 정답)`을 주면 epoch가 끝날 때마다 그 검증 표의 손실을 val_loss로 기록해요. 검증 표는 가중치 학습에 쓰지 않아요.',
              'fit 줄에 validation_data를 더해 epoch마다 검증 표의 손실도 기록하세요. 채점은 다른 검증 표로도 실행해요.',
              ['코드 실행을 눌러 기록 이름을 확인하세요.', 'fit 괄호 끝에 `validation_data=(X_valid, y_valid)`를 더하세요.', '코드 실행을 눌러 val_loss와 True를 확인하세요.', SUB],
              t6, t6_sol, u6, {u6.actions[-1]['text']: W, u6.actions[5]['text']: '실제 기록과 평가의 일치를 정확히 말해요.'},
              cases=[{'valid_rows': [[0.0], [5.0]], 'valid_targets': [[1.0], [9.0]], 'rounds': 2}, {'rounds': 4}],
              reject=[([['verbose=0,\n                    validation_data=(X_valid, y_valid))', 'verbose=0,\n                    validation_split=0.5)']], 'validation_split from the training rows'),
                      ([['verbose=0,\n                    validation_data=(X_valid, y_valid))', 'verbose=0,\n                    validation_data=(X_train, y_train))']], 'Validating on the training table')],
              accept=[([['verbose=0,\n                    validation_data=(X_valid, y_valid))', 'verbose=0,\n                    validation_data=[X_valid, y_valid])']], 'A list instead of a tuple')], timeout=T),
    code_step('stp_417ce7a7-0874-4d19-946a-327a20effbd3', '[[d] for d in distances]로 새 배송을 행으로 넘기세요', '예측 입력과 결과의 모양이 (배송 수, 특성 수)·(배송 수, 출력 수)임을 써서 확인해요.',
              '[distances]는 한 행에 거리 두 개라 ValueError다. [[d] for d in distances]로 고쳐 예측 모양 [2, 1]을 확인한다. 채점은 다른 거리 수로 실행한다.',
              '학습한 모델로 새 배송을 예측해요. 입력은 배송마다 한 행, 특성 수만큼의 열이에요. 이 모델은 특성이 거리 하나예요.',
              'X_test 줄을 고쳐 새 배송마다 한 행, 특성 한 열인 2차원 입력을 만드세요. 채점은 다른 거리 수로도 실행해요.',
              ['코드 실행을 눌러 ValueError가 나오는지 확인하세요.', '`np.array([distances], ...)`를 `np.array([[d] for d in distances], ...)`로 고치세요.', '코드 실행을 눌러 [2, 1]이 나오는지 확인하세요.', SUB],
              t7, t7_sol, u7, {u7.actions[-1]['text']: W}, cases=[{'distances': [1.0, 2.0, 5.0]}, {'distances': [7.0]}],
              reject=[([['X_test = np.array([[d] for d in distances], dtype="float32")\n', 'X_test = np.array([distances], dtype="float32")\n']], 'One row'),
                      ([['print(list(predictions.shape))\n', 'print([2, 1])\n']], 'Typing the shape')],
              accept=[([['X_test = np.array([[d] for d in distances], dtype="float32")\n', 'X_test = np.array(distances, dtype="float32").reshape(-1, 1)\n']], 'reshape(-1, 1)')], timeout=T),
]
