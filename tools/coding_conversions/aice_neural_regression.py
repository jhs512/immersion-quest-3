"""aice-neural-regression: 7 answer-picking steps -> coding steps (2026-10-30).

Each step edits one line of a tiny Keras regression on CPU: the output activation for a signed target, the
training loss, the loss history, the output units, evaluate's summary, matching actual values to the same
delivery, and the scaling rule kept with a saved model. Fixed weights make predictions exact, and the one
step that trains prints only the record count and whether the loss fell. Prepared cases rerun with other
rows, weights, targets, epochs, orders and new inputs, so typed outputs and the starter fail."""
from _kit import Script, code_step

OPENING = ['이 수업에서는 신경망을 숫자 예측에 맞추는 법을 직접 코드로 써요. 출력 범위·출력 수·손실의 관계를 확인해요.',
           '작은 모델을 학습하고 평가해요. 예측과 실제의 짝, 저장한 모델과 전처리 기준의 복원도 코드로 검증해요.']
PRD_SCOPE = ['두 챕터·두 단원·아홉 스텝으로 같은 배송 수치 모델을 검토해요.',
             '음수도 되는 목표의 출력 활성화·회귀 손실·epoch마다의 학습 기록·출력 수·evaluate의 요약·같은 배송끼리의 비교·저장한 전처리 기준을 한 곳씩 직접 고쳐 써요.']
PRD_GRADING = ['직접 고친 코드를 실제 파이썬·TensorFlow로 실행해 판정해요. 실행·해설만으로 성공시키지 않아요.',
               '고정 가중치로 예측을 정확한 값으로 만들고, 학습하는 스텝은 기록 수와 손실이 줄었는지만 비교해요. 다른 입력·가중치·정답·epoch·주문 순서·새 입력으로 다시 실행해 기준 풀이와 비교해요.',
               '결과를 글자로 적은 답, ReLU로 자른 차이, 다른 손실, 배송 수만큼의 출력, 순서가 어긋난 정답, 새 자료로 다시 구한 기준은 거절해요.',
               '마지막 도전(stp_1e68bc14-fc5b-4c8d-b02f-50f1b0a61b82): 실제 Python 실행과 다른 준비 자료의 결과를 검사해요. 시작 코드는 실패하고 동등한 풀이도 통과해야 해요.']
PRD_NARRATION = ['작은 실제 학습과 동작 확인용 고정 가중치 실험을 구별해요. 한 곳씩 고친 뒤 실제 예측·기록·지표를 읽어요.',
                 '목표범위·손실과 지표·훈련 기록·출력크기·평가 요약·행대응·전처리 보존을 조심할 지점으로 짚어요.']

HEAD = ('import os\nos.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")\nimport numpy as np\nimport tensorflow as tf\nfrom tensorflow import keras\n\n'
        '# 작은 CPU 실습의 실행 자원을 제한해요.\ntf.config.threading.set_intra_op_parallelism_threads(1)\n'
        'tf.config.threading.set_inter_op_parallelism_threads(1)\nkeras.utils.set_random_seed(7)\n')
FIXED = '# 가중치는 학습 성능이 아닌 계산 확인용으로 직접 정해요.\n'
SUB = '수정한 코드를 제출하세요.'
W = '실제 Keras 동작을 정확히 말해요.'
T = 45


def dense(activation):
    return ('model = keras.Sequential([keras.Input(shape=(1,)), keras.layers.Dense(1, activation="' + activation + '", '
            'kernel_initializer=keras.initializers.Constant(weight), bias_initializer=keras.initializers.Constant(bias))])\n')


# 1. A signed difference needs a linear output.
r1 = (HEAD + '# 목표는 기준 시간과의 차이예요. 기준보다 빠르면 음수예요.\nrows = [[1.0], [4.0]]\nweight = 2.0\nbias = -5.0\n' + FIXED
      + '# 이 줄의 출력 활성화를 고쳐 음수 차이도 그대로 내보내세요.\n' + dense('relu')
      + 'print(model.predict(np.array(rows, dtype="float32"), verbose=0).tolist())\n')
r1_sol = r1.replace(dense('relu'), '# linear는 계산값을 그대로 내보내요. 음수 차이도 잘리지 않아요.\n' + dense('linear'))
q1 = (Script(r1)
      .say('목표가 기준과의 차이라 음수도 나와야 해요. 출력 활성화가 음수를 막지 않는지 봐야 해요.', 'text:출력 활성화를 고쳐 음수 차이도 그대로 내보내세요.')
      .run('print(model.predict')
      .say('[[0.0], [3.0]]이에요. 첫 배송의 계산값 -3.0이 ReLU에서 0.0으로 잘렸어요.', 'output')
      .patch('activation="relu"', 'activation="linear"', 'relu를 linear로 바꿔요.')
      .run('print(model.predict')
      .say('[[-3.0], [3.0]]이에요. 기준보다 3분 빠른 차이를 그대로 표현해요.', 'output')
      .say('조심하세요. 출력 활성화는 목표가 허용하는 범위에 맞춰요. 시간처럼 음수가 없는 목표라면 그때는 ReLU가 맞아요.', 'code:activation="linear"'))

# 2. Regression trains on mse; mae is only watched.
r2 = (HEAD + 'rows = [[1.0]]\ntargets = [[-1.0]]\nweight = 2.0\nbias = -5.0\n' + FIXED + dense('linear')
      + '# 이 줄을 고쳐 학습 손실은 평균 제곱 오차 mse로 정하고 mae는 지표로만 두세요.\nmodel.compile(optimizer="sgd", loss="mae", metrics=["mae"])\n'
      'result = model.evaluate(np.array(rows, dtype="float32"), np.array(targets, dtype="float32"), return_dict=True, verbose=0)\n'
      'print(round(float(result["loss"]), 4), round(float(result["mae"]), 4))\n')
r2_sol = r2.replace('model.compile(optimizer="sgd", loss="mae", metrics=["mae"])',
                    '# loss는 학습이 줄이는 오차, metrics는 함께 지켜보는 지표예요. 회귀 학습은 오차를 제곱해 평균한 mse로 해요.\n'
                    'model.compile(optimizer="sgd", loss="mse", metrics=["mae"])')
q2 = (Script(r2)
      .say('예측 -3.0과 정답 -1.0은 2만큼 달라요. 학습 손실을 mse로 정하고 mae는 지표로만 둬야 해요.', 'text:학습 손실은 평균 제곱 오차 mse로 정하고 mae는 지표로만 두세요.')
      .run('print(round(float(result["loss"])')
      .say('2.0 2.0이에요. 손실도 절대 오차라 지표와 같은 값이에요.', 'output')
      .patch('loss="mae"', 'loss="mse"', 'loss를 "mse"로 바꿔요.')
      .run('print(round(float(result["loss"])')
      .say('4.0 2.0이에요. 손실은 오차 2를 제곱한 4.0이고 지표 mae는 2.0 그대로예요.', 'output')
      .say('조심하세요. accuracy는 종류를 맞힌 비율이라 숫자 예측의 손실이 아니에요. 학습할 손실과 지켜볼 지표는 역할이 달라요.', 'code:loss="mse"'))

# 3. One loss record per epoch.
r3 = (HEAD + '# 작은 관계를 실제 자료로 학습하는 예예요.\nepochs = 10\n'
      'X_train = np.array([[0.0], [1.0], [2.0], [3.0]], dtype="float32")\ny_train = np.array([[1.0], [3.0], [5.0], [7.0]], dtype="float32")\n'
      'model = keras.Sequential([keras.Input(shape=(1,)), keras.layers.Dense(1, kernel_initializer="zeros", bias_initializer="zeros")])\n'
      'model.compile(optimizer=keras.optimizers.SGD(learning_rate=0.05), loss="mse")\n'
      'history = model.fit(X_train, y_train, epochs=epochs, batch_size=4, shuffle=False, verbose=0)\n'
      '# 이 줄을 고쳐 fit이 남긴 history에서 훈련 손실 기록 목록을 꺼내세요.\nlosses = []\n'
      'print(len(losses))\n# 첫 기록이 마지막 기록보다 크면 학습하며 훈련 오차가 줄었다는 뜻이에요.\nprint(losses[0] > losses[-1])\n')
r3_sol = r3.replace('losses = []\n', '# history.history["loss"]에는 epoch마다 훈련 표 전체에서 잰 손실이 하나씩 쌓여요.\nlosses = history.history["loss"]\n')
q3 = (Script(r3)
      .say('fit이 남긴 기록을 읽어요. history에서 훈련 손실 목록을 꺼내야 해요.', 'text:fit이 남긴 history에서 훈련 손실 기록 목록을 꺼내세요.')
      .run('print(len(losses))', error='IndexError')
      .say('0과 IndexError예요. 빈 목록이라 첫 기록이 없어요.', 'output')
      .patch('losses = []\n', 'losses = history.history["loss"]\n', '빈 목록을 history.history["loss"]로 바꿔요.')
      .run('print(len(losses))', 'print(losses[0] > losses[-1])')
      .say('10과 True예요. 훈련 배송은 네 건인데 기록은 epochs만큼 열 개이고, 학습하며 오차가 줄었어요.', 'output')
      .say('조심하세요. 이 기록은 훈련 표에서 잰 오차예요. 줄었다는 것만으로 새 배송의 성능까지 말하지는 않아요.', 'code:history.history["loss"]'))

# 4. One target per delivery needs one output unit.
r4 = (HEAD + 'rows = [[1.0], [2.0]]\ntargets = [[3.0], [5.0]]\n'
      '# 이 줄의 Dense를 고쳐 배송마다 시간 차이 하나만 내보내세요.\nmodel = keras.Sequential([keras.Input(shape=(1,)), keras.layers.Dense(2)])\n'
      'predictions = model.predict(np.array(rows, dtype="float32"), verbose=0)\nprint(list(predictions.shape))\n'
      '# 예측에서 정답을 빼 차이가 몇 개 생기는지 세요.\nprint((predictions - np.array(targets)).size)\n')
r4_sol = r4.replace('keras.layers.Dense(2)])', '# Dense의 units는 배송마다 내보낼 값의 수예요. 목표가 하나라 1이에요.\n                          keras.layers.Dense(1)])')
q4 = (Script(r4)
      .say('배송마다 보고할 값은 하나예요. Dense의 출력 수를 목표 수와 맞춰야 해요.', 'text:Dense를 고쳐 배송마다 시간 차이 하나만 내보내세요.')
      .run('print(list(predictions.shape))', 'print((predictions - np.array(targets)).size)')
      .say('[2, 2]와 4예요. 배송 둘에 출력이 둘씩이고, 한 열 정답이 두 열로 늘어나 차이가 네 개 생겼어요.', 'output')
      .patch('keras.layers.Dense(2)])', 'keras.layers.Dense(1)])', 'Dense(2)를 Dense(1)로 바꿔요.')
      .run('print(list(predictions.shape))', 'print((predictions - np.array(targets)).size)')
      .say('[2, 1]과 2예요. 배송마다 출력 하나라 차이도 배송 수만큼이에요.', 'output')
      .say('조심하세요. 출력 수가 요구와 달라도 배열이 저절로 늘어나 계산이 멈추지 않아요. 모양을 직접 확인해요.', 'code:Dense(1)'))

# 5. evaluate summarizes the whole evaluation table.
r5 = (HEAD + 'X_test = [[1.0], [2.0]]\ny_test = [[4.0], [6.0]]\nweight = 2.0\nbias = 1.0\n' + FIXED + dense('linear')
      + 'model.compile(optimizer="sgd", loss="mse", metrics=["mae"])\n'
      'X = np.array(X_test, dtype="float32")\ny = np.array(y_test, dtype="float32")\n'
      'print(model.predict(X, verbose=0).tolist())\n'
      '# 이 줄을 고쳐 평가 자료 전체의 loss와 mae를 evaluate로 계산하세요.\nresult = {"loss": 0.0, "mae": 0.0}\n'
      'print(round(float(result["loss"]), 4), round(float(result["mae"]), 4))\n')
r5_sol = r5.replace('result = {"loss": 0.0, "mae": 0.0}\n',
                    '# evaluate는 평가 자료 전체를 한 번에 요약해요. return_dict=True면 이름으로 꺼내요.\n'
                    'result = model.evaluate(X, y, return_dict=True, verbose=0)\n')
q5 = (Script(r5)
      .say('predict는 배송마다 값을 내요. 평가 자료 전체의 요약은 evaluate로 따로 구해야 해요.', 'text:평가 자료 전체의 loss와 mae를 evaluate로 계산하세요.')
      .run('print(model.predict', 'print(round(float(result["loss"])')
      .say('[[3.0], [5.0]]과 0.0 0.0이에요. 아직 평가를 하지 않은 빈 값이에요.', 'output')
      .patch('result = {"loss": 0.0, "mae": 0.0}\n', 'result = model.evaluate(X, y, return_dict=True, verbose=0)\n', '빈 사전을 model.evaluate(X, y, return_dict=True, verbose=0)로 바꿔요.')
      .run('print(model.predict', 'print(round(float(result["loss"])')
      .say('1.0 1.0이에요. 두 배송 모두 1분씩 빗나가 MSE와 MAE가 1.0이에요.', 'output')
      .say('조심하세요. evaluate의 두 수는 배송별 예측이 아니에요. 평가 자료 전체를 요약한 손실과 지표예요.', 'code:model.evaluate(X, y'))

# 6. Compare each prediction with the same delivery's actual value.
r6 = (HEAD + 'from sklearn.metrics import mean_absolute_error\n\n'
      '# 예측할 배송 번호 순서와, 번호별 실제 시간이에요.\norders = [101, 102]\nX_test = [[1.0], [2.0]]\nactual_by_order = {102: 5.0, 101: 3.0}\n'
      'weight = 2.0\nbias = 1.0\n' + FIXED + dense('linear')
      + 'predictions = model.predict(np.array(X_test, dtype="float32"), verbose=0).ravel()\n'
      '# 이 줄을 고쳐 orders 순서대로 같은 배송의 실제 시간을 꺼내세요.\ny_true = list(actual_by_order.values())\n'
      'print(predictions.tolist())\nprint(y_true)\nprint(float(mean_absolute_error(y_true, predictions)))\n')
r6_sol = r6.replace('y_true = list(actual_by_order.values())\n',
                    '# 예측과 같은 순서가 되도록 배송 번호로 실제 시간을 하나씩 찾아요.\ny_true = [actual_by_order[order] for order in orders]\n')
q6 = (Script(r6)
      .say('실제 시간은 배송 번호별로 저장돼 있어요. 예측과 같은 배송끼리 비교하도록 orders 순서로 꺼내야 해요.', 'text:orders 순서대로 같은 배송의 실제 시간을 꺼내세요.')
      .run('print(predictions.tolist())', 'print(float(mean_absolute_error')
      .say('[3.0, 5.0]과 [5.0, 3.0], 오차 2.0이에요. 길이는 같지만 다른 배송끼리 비교했어요.', 'output')
      .patch('y_true = list(actual_by_order.values())\n', 'y_true = [actual_by_order[order] for order in orders]\n', 'orders의 번호마다 actual_by_order[order]를 꺼내요.')
      .run('print(predictions.tolist())', 'print(float(mean_absolute_error')
      .say('[3.0, 5.0]과 [3.0, 5.0], 오차 0.0이에요. 같은 배송의 실제와 예측을 짝지었어요.', 'output')
      .say('조심하세요. 길이만 같다고 바른 평가가 아니에요. 정렬도 짝을 바꿀 수 있어요. 같은 관측끼리 맞췄는지 먼저 확인해요.', 'code:actual_by_order[order]'))

# 7. Keep the scaling rule with the saved model.
r7 = (HEAD + 'import json\nfrom pathlib import Path\n\n'
      'X_train = np.array([[1.0], [3.0]], dtype="float32")\nX_new = [[2.0], [5.0]]\nweight = 2.0\nbias = 1.0\n'
      '# 훈련 표에서 배운 전처리 기준이에요. 모델 밖에서 계산했어요.\nmean = float(X_train.mean())\nstd = float(X_train.std())\n' + FIXED + dense('linear')
      + 'new = np.array(X_new, dtype="float32")\nbefore = model.predict((new - mean) / std, verbose=0)\n'
      '# 이 실습에서 직접 만든 모델과 기준을 저장해요.\nmodel.save("delivery.keras")\nPath("scale.json").write_text(json.dumps({"mean": mean, "std": std}), encoding="utf-8")\n\n'
      '# 다른 곳에서 다시 열었다고 생각해요.\nrestored = keras.models.load_model("delivery.keras")\nsaved = json.loads(Path("scale.json").read_text(encoding="utf-8"))\n'
      '# 이 줄을 고쳐 저장한 기준 saved로 새 입력을 바꾸세요.\nscaled = (new - new.mean()) / new.std()\n'
      'after = restored.predict(scaled, verbose=0)\nprint(after.round(4).ravel().tolist())\nprint(bool(np.allclose(before, after)))\n')
r7_sol = r7.replace('scaled = (new - new.mean()) / new.std()\n',
                    '# 훈련 때의 평균과 표준편차를 그대로 써요. 새 자료로 기준을 다시 구하지 않아요.\nscaled = (new - saved["mean"]) / saved["std"]\n')
q7 = (Script(r7)
      .say('모델 파일에는 모델 밖에서 계산한 기준이 없어요. 함께 저장한 scale.json의 기준으로 새 입력을 바꿔야 해요.', 'text:저장한 기준 saved로 새 입력을 바꾸세요.')
      .run('print(after.round(4)', 'print(bool(np.allclose')
      .say('[-1.0, 3.0]과 False예요. 새 입력으로 기준을 다시 구해 저장 전 예측과 달라졌어요.', 'output')
      .patch('scaled = (new - new.mean()) / new.std()\n', 'scaled = (new - saved["mean"]) / saved["std"]\n', 'new.mean()과 new.std()를 saved["mean"]과 saved["std"]로 바꿔요.')
      .run('print(after.round(4)', 'print(bool(np.allclose')
      .say('[1.0, 7.0]과 True예요. 훈련 기준 평균 2와 표준편차 1을 그대로 써서 저장 전과 같아요.', 'output')
      .say('조심하세요. 모델 파일이 모델 밖의 전처리 기준까지 자동으로 보존하지는 않아요. 기준도 함께 저장하고 불러와요.', 'code:saved["mean"]'))

SPECS = [
    code_step('stp_c6f4dc1f-64dd-4e79-a180-537f51755d94', 'activation="linear"로 음수 차이도 내보내세요', '목표가 허용하는 범위에 맞는 출력 활성화를 써서 음수 차이를 보존해요.',
              'ReLU 출력은 -3.0을 0.0으로 자른다. activation="linear"로 고쳐 [[-3.0], [3.0]]을 확인한다. 채점은 다른 입력·가중치·편향으로 실행한다.',
              '이번 목표는 기준 시간과의 차이예요. 기준보다 빠르면 음수예요. ReLU는 음수를 0으로 바꾸고, linear는 계산값 입력 × 가중치 + 편향을 그대로 내보내요.',
              'model 줄의 출력 활성화를 고쳐 음수 차이도 그대로 내보내세요. 채점은 다른 입력과 가중치로도 실행해요.',
              ['코드 실행을 눌러 음수가 0으로 바뀌었는지 확인하세요.', '`activation="relu"`를 `activation="linear"`로 고치세요.', '코드 실행을 눌러 [[-3.0], [3.0]]이 나오는지 확인하세요.', SUB],
              r1, r1_sol, q1, {q1.actions[-1]['text']: W}, cases=[{'rows': [[0.0], [2.0], [3.0]]}, {'rows': [[1.0]], 'weight': -1.0, 'bias': 0.5}],
              reject=[([['activation="linear"', 'activation="sigmoid"']], 'Sigmoid squeezes into 0..1'),
                      ([['print(model.predict(np.array(rows, dtype="float32"), verbose=0).tolist())', 'print([[-3.0], [3.0]])']], 'Typing the predictions')],
              accept=[([['activation="linear", ', '']], 'Dense default is linear')], timeout=T),
    code_step('stp_880b5026-588a-4edc-82bc-a538418dbe83', 'loss="mse"로 회귀 학습 손실을 정하세요', '회귀가 줄이는 손실 mse와 함께 지켜보는 지표 mae를 구별해 써요.',
              '손실이 mae면 손실과 지표가 모두 2.0이다. loss="mse"로 고쳐 4.0 2.0을 확인한다. 채점은 다른 정답으로 실행한다.',
              '`compile`의 loss는 학습이 줄이려는 오차, metrics는 함께 지켜보는 지표예요. mse는 오차를 제곱해 평균하고, mae는 절댓값을 평균해요. 고정 가중치로 예측은 -3.0이에요.',
              'compile 줄을 고쳐 학습 손실은 평균 제곱 오차 mse로 정하고 mae는 지표로만 두세요. 채점은 다른 정답으로도 실행해요.',
              ['코드 실행을 눌러 손실과 지표를 확인하세요.', '`loss="mae"`를 `loss="mse"`로 고치세요.', '코드 실행을 눌러 4.0 2.0이 나오는지 확인하세요.', SUB],
              r2, r2_sol, q2, {q2.actions[-1]['text']: W}, cases=[{'targets': [[0.0]]}, {'rows': [[1.0], [2.0]], 'targets': [[-2.0], [0.0]]}],
              reject=[([['loss="mse", metrics=["mae"]', 'loss="mae", metrics=["mse"]']], 'Swapping loss and metric'),
                      ([['print(round(float(result["loss"]), 4), round(float(result["mae"]), 4))', 'print(4.0, 2.0)']], 'Typing the numbers')],
              accept=[([['loss="mse"', 'loss="mean_squared_error"']], 'Full loss name')], timeout=T),
    code_step('stp_dc24177d-8da9-41ce-8fde-f322d8cecb3a', 'history.history["loss"]로 epoch마다의 기록을 꺼내세요', '학습 기록은 배송마다가 아니라 epoch마다 하나씩 쌓이는 것을 직접 꺼내 확인해요.',
              'losses가 빈 목록이면 0과 IndexError다. history.history["loss"]로 고쳐 10과 True를 확인한다. 채점은 다른 epoch 수로 실행한다.',
              '훈련 배송 네 건으로 학습해요. epoch는 훈련 표 전체를 한 번 학습하는 단위예요. `fit`이 돌려준 history의 `history["loss"]`에는 epoch마다 잰 훈련 손실이 쌓여요.',
              'losses 줄을 고쳐 fit이 남긴 history에서 훈련 손실 기록 목록을 꺼내세요. 채점은 다른 epoch 수로도 실행해요.',
              ['코드 실행을 눌러 IndexError가 나오는지 확인하세요.', '`losses = []`를 `losses = history.history["loss"]`로 고치세요.', '코드 실행을 눌러 10과 True가 나오는지 확인하세요.', SUB],
              r3, r3_sol, q3, {q3.actions[-1]['text']: W}, cases=[{'epochs': 3}, {'epochs': 1}],
              reject=[([['losses = history.history["loss"]\n', 'losses = [10.0] * 10\n']], 'Typing ten records'),
                      ([['losses = history.history["loss"]\n', 'losses = list(range(len(X_train), 0, -1))\n']], 'One record per delivery')],
              accept=[([['losses = history.history["loss"]\n', 'losses = list(history.history.get("loss"))\n']], 'get and list')], timeout=T),
    code_step('stp_2c4f572f-d874-445d-bbc2-9605dc9af635', 'Dense(1)로 배송마다 값 하나를 내보내세요', '목표 수와 출력 수를 맞추고, 어긋난 모양이 조용히 늘어나는 것을 확인해요.',
              'Dense(2)는 [2, 2]이고 정답과의 차이가 4개다. Dense(1)로 고쳐 [2, 1]과 2를 확인한다. 채점은 다른 배송 수로 실행한다.',
              '배송마다 기준과의 시간 차이 하나를 보고해야 해요. Dense의 units는 배송마다 내보내는 값의 수예요. 정답 targets는 배송마다 한 열이에요.',
              'model 줄의 Dense를 고쳐 배송마다 시간 차이 하나만 내보내세요. 채점은 다른 배송 수로도 실행해요.',
              ['코드 실행을 눌러 출력 모양과 차이의 수를 확인하세요.', '`Dense(2)`를 `Dense(1)`로 고치세요.', '코드 실행을 눌러 [2, 1]과 2가 나오는지 확인하세요.', SUB],
              r4, r4_sol, q4, {q4.actions[-1]['text']: W}, cases=[{'rows': [[1.0], [2.0], [3.0]], 'targets': [[1.0], [2.0], [3.0]]}, {'rows': [[5.0]], 'targets': [[0.0]]}],
              reject=[([['keras.layers.Dense(1)])', 'keras.layers.Dense(len(rows))])']], 'One output per delivery row'),
                      ([['print(list(predictions.shape))', 'print([2, 1])']], 'Typing the shape')],
              accept=[([['keras.layers.Dense(1)])', 'keras.layers.Dense(units=1)])']], 'units keyword')], timeout=T),
    code_step('stp_523413c5-c858-4ed3-825a-83e4d7231fd1', 'evaluate로 평가 자료 전체의 손실과 지표를 구하세요', 'predict의 배송별 값과 evaluate의 전체 요약을 구별해 직접 계산해요.',
              'result가 빈 값이면 0.0 0.0이다. model.evaluate(X, y, return_dict=True, verbose=0)로 고쳐 1.0 1.0을 확인한다. 채점은 다른 평가 정답으로 실행한다.',
              '고정 가중치라 예측은 3.0과 5.0이에요. `predict`는 배송마다 값을 하나씩 내고, `evaluate`는 평가 자료 전체에 compile에서 정한 loss와 지표를 한 번씩 계산해요.',
              'result 줄을 고쳐 평가 자료 전체의 loss와 mae를 evaluate로 계산하세요. 채점은 다른 평가 정답으로도 실행해요.',
              ['코드 실행을 눌러 지금 결과를 확인하세요.', '`result = {"loss": 0.0, "mae": 0.0}`을 `result = model.evaluate(X, y, return_dict=True, verbose=0)`으로 고치세요.', '코드 실행을 눌러 1.0 1.0이 나오는지 확인하세요.', SUB],
              r5, r5_sol, q5, {q5.actions[-1]['text']: W}, cases=[{'y_test': [[3.0], [7.0]]}, {'X_test': [[0.0]], 'y_test': [[4.0]]}],
              reject=[([['result = model.evaluate(X, y, return_dict=True, verbose=0)\n', 'result = {"loss": 1.0, "mae": 1.0}\n']], 'Typing the summary'),
                      ([['result = model.evaluate(X, y, return_dict=True, verbose=0)\n', 'result = model.evaluate(X, X, return_dict=True, verbose=0)\n']], 'Inputs as the answers')],
              accept=[([['result = model.evaluate(X, y, return_dict=True, verbose=0)\n', 'result = dict(zip(["loss", "mae"], model.evaluate(X, y, verbose=0)))\n']], 'List result zipped with names')], timeout=T),
    code_step('stp_66008cb7-3573-4a2b-9186-d7fd08a95a0e', '배송 번호로 같은 배송의 실제 시간을 꺼내세요', '예측과 실제를 같은 관측끼리 짝지어야 평가가 의미 있음을 직접 맞춰 확인해요.',
              '사전 값 순서대로 꺼내면 다른 배송끼리 비교해 오차 2.0이다. [actual_by_order[order] for order in orders]로 고쳐 오차 0.0을 확인한다. 채점은 다른 주문 순서와 시간으로 실행한다.',
              '예측은 orders 순서(101, 102)로 나와요. 실제 시간은 배송 번호별 사전 actual_by_order에 다른 순서로 저장돼 있어요. `ravel()`은 한 열 예측을 일렬로 펼쳐요.',
              'y_true 줄을 고쳐 orders 순서대로 같은 배송의 실제 시간을 꺼내세요. 채점은 다른 주문 순서로도 실행해요.',
              ['코드 실행을 눌러 오차를 확인하세요.', '`list(actual_by_order.values())`를 `[actual_by_order[order] for order in orders]`로 고치세요.', '코드 실행을 눌러 오차 0.0이 나오는지 확인하세요.', SUB],
              r6, r6_sol, q6, {q6.actions[-1]['text']: W},
              cases=[{'orders': [7, 3, 5], 'X_test': [[0.0], [1.0], [2.0]], 'actual_by_order': {3: 4.0, 5: 3.0, 7: 1.0}},
                     {'orders': [2, 1], 'actual_by_order': {1: 4.0, 2: 5.0}}],
              reject=[([['y_true = [actual_by_order[order] for order in orders]\n', 'y_true = sorted(actual_by_order.values())\n']], 'Sorting the actual values'),
                      ([['y_true = [actual_by_order[order] for order in orders]\n', 'y_true = [3.0, 5.0]\n']], 'Typing the actual values')],
              accept=[([['y_true = [actual_by_order[order] for order in orders]\n', 'y_true = list(map(actual_by_order.get, orders))\n']], 'map with get')], timeout=T),
    code_step('stp_d4e9c028-d71d-4e3c-9421-3482ec6e5f26', '저장한 기준 saved로 새 입력을 바꾸세요', '모델 밖에서 배운 전처리 기준을 모델과 함께 저장하고 같은 기준으로 복원해요.',
              '새 입력으로 기준을 다시 구하면 [-1.0, 3.0], False다. saved["mean"]과 saved["std"]로 고쳐 [1.0, 7.0], True를 확인한다. 채점은 다른 새 입력으로 실행한다.',
              '훈련 표의 평균과 표준편차로 입력을 바꾼 뒤 예측해요. `model.save`는 모델만 저장하므로 그 기준은 scale.json에 따로 저장했어요. 다시 연 쪽에서 같은 기준을 써야 저장 전과 같은 예측이 나와요.',
              'scaled 줄을 고쳐 저장한 기준 saved로 새 입력을 바꾸세요. 채점은 다른 새 입력으로도 실행해요.',
              ['코드 실행을 눌러 저장 전과 예측이 같은지 확인하세요.', '`(new - new.mean()) / new.std()`를 `(new - saved["mean"]) / saved["std"]`로 고치세요.', '코드 실행을 눌러 True가 나오는지 확인하세요.', SUB],
              r7, r7_sol, q7, {q7.actions[-1]['text']: W}, cases=[{'X_new': [[0.0], [4.0], [6.0]]}, {'X_new': [[3.0], [3.0]]}],
              reject=[([['scaled = (new - saved["mean"]) / saved["std"]\n', 'scaled = new\n']], 'No scaling'),
                      ([['print(after.round(4).ravel().tolist())\nprint(bool(np.allclose(before, after)))\n', 'print([1.0, 7.0])\nprint(True)\n']], 'Typing the result')],
              accept=[([['scaled = (new - saved["mean"]) / saved["std"]\n', 'scaled = np.divide(new - saved["mean"], saved["std"])\n']], 'np.divide')], timeout=T),
]
