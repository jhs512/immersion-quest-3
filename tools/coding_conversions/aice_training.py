"""aice-training: 6 answer-picking steps -> coding steps (2026-10-30).

Each step edits one line of a tiny Keras training run on CPU: the number of weight updates from epochs and
batch size, restoring the best weights on early stopping, dropout only while training, the L2 penalty in
the total loss, loading the checkpoint file and the size of one SGD step. Grading reads counts, update
steps, exact one-step weights and comparisons with a control model trained one epoch; a probe checks the
restored model itself. Step 2 (what to inspect when training and validation move apart) stays a judgement
question. Prepared cases rerun with other batch sizes, epochs, patience, rates, regularization and data."""
from _kit import Script, code_step

OPENING = ['이 수업에서는 학습을 얼마나, 어떻게 진행할지 직접 코드로 정해요. 훈련과 검증의 변화를 구별해요.',
           'epoch·batch·학습률을 바꿔 갱신을 세고, 조기 중단과 최고 모델 복원, Dropout과 규제를 실행 결과로 확인해요.']
PRD_SCOPE = ['두 챕터·두 단원·아홉 스텝으로 같은 작은 학습을 조절해요.',
             'epoch와 batch로 갱신 횟수 계산·조기 중단의 최고 가중치 복원·추론 때의 Dropout·총 손실의 규제 항·저장한 최고 모델 불러오기·학습률만큼의 한 번 갱신을 한 곳씩 직접 써요. 훈련과 검증이 다르게 움직일 때의 판단은 개념 문제로 남겨요.']
PRD_GRADING = ['직접 고친 코드를 실제 파이썬·TensorFlow로 실행해 판정해요. 실행·해설만으로 성공시키지 않아요.',
               '학습한 실수 값 대신 갱신 횟수·기록 수·한 epoch만 학습한 비교 모델과의 일치·한 번 갱신한 정확한 가중치로 채점해요. 다른 batch·epoch·patience·학습률·규제·자료로 다시 실행해 기준 풀이와 비교해요.',
               '결과를 글자로 적은 답, 마지막 batch를 빼고 센 갱신, 되돌리지 않는 조기 중단, 추론 때 끈 Dropout을 흉내 낸 곱셈, 가중치 없는 규제, 메모리 모델, 학습률을 뺀 갱신은 거절해요.',
               '마지막 도전(stp_99547a1f-d0b3-4cd7-87e9-3658ad90b2f3): 실제 Python 실행과 다른 준비 자료의 결과를 검사해요. 시작 코드는 실패하고 동등한 풀이도 통과해야 해요.']
PRD_NARRATION = ['한 설정이나 한 줄씩 고친 뒤 실제 갱신 횟수·기록·가중치를 읽어요.',
                 'epoch와 갱신·되돌림과 갱신 횟수·학습과 추론·총 손실과 지표·파일과 메모리·학습률과 반복을 조심할 지점으로 짚어요.']

HEAD = ('import os\nos.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")\nimport numpy as np\nimport tensorflow as tf\nfrom tensorflow import keras\n\n'
        '# 작은 CPU 실습의 실행 자원을 제한해요.\ntf.config.threading.set_intra_op_parallelism_threads(1)\n'
        'tf.config.threading.set_inter_op_parallelism_threads(1)\nkeras.utils.set_random_seed(7)\n')
MAKE = ('def make_model(rate=0.1):\n    # 매 비교마다 같은 영 가중치에서 시작해요.\n'
        '    model = keras.Sequential([keras.Input(shape=(1,)), keras.layers.Dense(1, kernel_initializer="zeros", bias_initializer="zeros")])\n'
        '    model.compile(optimizer=keras.optimizers.SGD(learning_rate=rate), loss="mse")\n    return model\n')
VALID = ('# 동작 비교용으로 훈련과 검증의 정답 관계를 다르게 둬요.\nX_train = np.array([[1.0], [2.0]], dtype="float32")\ny_train = np.array([[2.0], [4.0]], dtype="float32")\n'
         'X_valid = np.array([[1.0], [2.0]], dtype="float32")\ny_valid = np.array([[0.0], [0.0]], dtype="float32")\n')
SUB = '수정한 코드를 제출하세요.'
W = '실제 Keras 동작을 정확히 말해요.'
T = 45

# 1. Updates = epochs x batches per epoch (the last partial batch counts).
t1 = (HEAD + 'import math\n\n' + MAKE + '# 네 관측을 batch_size개씩 묶어 epochs번 반복해요.\nrows = [0.0, 1.0, 2.0, 3.0]\nepochs = 2\nbatch_size = 2\n'
      'X_train = np.array([[x] for x in rows], dtype="float32")\ny_train = 2 * X_train\nmodel = make_model()\n'
      'model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, shuffle=False, verbose=0)\n'
      '# 이 줄을 고쳐 epoch마다 batch 수만큼 갱신하는 횟수를 계산하세요. 남는 관측도 한 batch예요.\nupdates = epochs\n'
      'print(updates, int(model.optimizer.iterations.numpy()))\n')
t1_sol = t1.replace('updates = epochs\n', '# epoch 한 번에 batch 수만큼 가중치를 고쳐요. 나누어떨어지지 않으면 올림해 남은 관측도 한 번 더 세요.\n'
                    'updates = epochs * math.ceil(len(X_train) / batch_size)\n')
u1 = (Script(t1)
      .say('가중치는 batch마다 한 번씩 고쳐져요. 계산한 횟수를 실제 갱신 횟수와 비교해야 해요.', 'text:epoch마다 batch 수만큼 갱신하는 횟수를 계산하세요.')
      .run('print(updates')
      .say('2 4예요. epoch 수만 셌는데 실제로는 네 번 갱신했어요.', 'output')
      .patch('updates = epochs\n', 'updates = epochs * math.ceil(len(X_train) / batch_size)\n', 'epochs에 math.ceil(len(X_train) / batch_size)를 곱해요.')
      .run('print(updates')
      .say('4 4예요. epoch마다 batch 둘, 두 epoch라 네 번이에요.', 'output')
      .say('조심하세요. 관측 수가 batch_size로 나누어떨어지지 않으면 남은 관측도 한 batch라 한 번 더 갱신해요. 그래서 올림해요.', 'code:math.ceil(len(X_train) / batch_size)'))

# 3. EarlyStopping keeps the best epoch only with restore_best_weights=True.
t3 = (HEAD + MAKE + VALID + 'patience = 0\nmodel = make_model()\n'
      '# 이 줄을 고쳐 멈출 때 검증 손실이 가장 작았던 epoch의 가중치로 되돌리세요.\n'
      'callback = keras.callbacks.EarlyStopping(monitor="val_loss", mode="min", patience=patience)\n'
      'history = model.fit(X_train, y_train, validation_data=(X_valid, y_valid), epochs=6, batch_size=2, shuffle=False, callbacks=[callback], verbose=0)\n'
      '# 비교 모델: 같은 시작에서 딱 한 epoch만 학습해요. 이 자료에서는 첫 epoch의 검증 손실이 가장 작아요.\n'
      'control = make_model()\ncontrol.fit(X_train, y_train, epochs=1, batch_size=2, shuffle=False, verbose=0)\n'
      'print(len(history.history["loss"]))\nprint(bool(np.allclose(model.predict(X_valid, verbose=0), control.predict(X_valid, verbose=0))))\n'
      'print(int(model.optimizer.iterations.numpy()))\n')
t3_sol = t3.replace('mode="min", patience=patience)', 'mode="min", patience=patience,\n'
                    '                                         # 멈출 때 가장 좋았던 epoch의 가중치로 돌아가요. 없으면 마지막 가중치가 남아요.\n'
                    '                                         restore_best_weights=True)')
u3 = (Script(t3)
      .say('검증 손실은 첫 epoch 뒤부터 나빠져요. 멈출 때 가장 좋았던 가중치로 되돌리게 설정해야 해요.', 'text:멈출 때 검증 손실이 가장 작았던 epoch의 가중치로 되돌리세요.')
      .run('print(len(history', 'print(int(model.optimizer')
      .say('2, False, 2예요. 두 번째 epoch에서 멈췄지만 나빠진 마지막 가중치가 남아 한 epoch 모델과 달라요.', 'output')
      .patch('patience=patience)', 'patience=patience, restore_best_weights=True)', '괄호 안에 restore_best_weights=True를 더해요.')
      .run('print(len(history', 'print(int(model.optimizer')
      .say('2, True, 2예요. 첫 epoch의 가중치로 돌아가 한 epoch만 학습한 모델과 예측이 같아요.', 'output')
      .say('조심하세요. 마지막 줄의 갱신 횟수는 2 그대로예요. 되돌리는 것은 모델 가중치뿐이고 optimizer의 갱신 횟수는 돌아가지 않아요.', 'code:restore_best_weights=True'))

# 4. Dropout only drops while training.
t4 = (HEAD + '# 무작위 위치를 외우지 않고 학습·추론의 규칙을 봐요.\nrate = 0.5\nwidth = 4\nlayer = keras.layers.Dropout(rate, seed=7)\ninputs = tf.ones((1, width))\n'
      '# 이 줄을 고쳐 추론 때처럼 Dropout을 적용하지 않게 부르세요.\ninference = layer(inputs, training=True).numpy()\n'
      'training = layer(inputs, training=True).numpy()\nprint(inference.tolist())\n'
      '# 확인용: 학습 때는 0이거나 1 / (1 - rate)로 키운 값만 나와요.\nkept = 1 / (1 - rate)\n'
      'print(bool(np.all(np.isclose(training, 0.0) | np.isclose(training, kept))))\n')
t4_sol = t4.replace('inference = layer(inputs, training=True).numpy()\n',
                    '# training=False면 Dropout은 아무것도 끄지 않고 입력을 그대로 넘겨요.\ninference = layer(inputs, training=False).numpy()\n')
u4 = (Script(t4)
      .say('Dropout은 학습할 때만 일부 입력을 쉬게 해요. 추론 때처럼 부르도록 training을 고쳐야 해요.', 'text:추론 때처럼 Dropout을 적용하지 않게 부르세요.')
      .run('print(inference.tolist())', 'print(bool(np.all')
      .say('일부가 0.0이고 남은 값이 2.0이에요. 추론 쪽도 학습처럼 불러 입력을 지웠어요.', 'output')
      .patch('inference = layer(inputs, training=True)', 'inference = layer(inputs, training=False)', '첫 줄의 training을 False로 바꿔요.')
      .run('print(inference.tolist())', 'print(bool(np.all')
      .say('[[1.0, 1.0, 1.0, 1.0]]과 True예요. 추론은 그대로이고, 학습 때는 0 또는 2.0만 나와요.', 'output')
      .say('조심하세요. Dropout은 자료에서 특성을 지우는 게 아니에요. 그리고 학습 때 지워지는 위치나 개수는 무작위라 외우지 않아요.', 'code:training=False'))

# 5. The total loss adds the L2 penalty to the data error.
t5 = (HEAD + '# 가중치 1 두 개에 L2 규제를 걸어요.\nl2 = 0.1\nrows = [[1.0, 2.0]]\ntargets = [[3.0]]\n'
      'model = keras.Sequential([keras.Input(shape=(2,)), keras.layers.Dense(1, use_bias=False, kernel_initializer="ones", kernel_regularizer=keras.regularizers.l2(l2))])\n'
      'model.compile(optimizer="sgd", loss="mse", metrics=["mse"])\n'
      'result = model.evaluate(np.array(rows, dtype="float32"), np.array(targets, dtype="float32"), return_dict=True, verbose=0)\n'
      '# 이 줄을 고쳐 규제 항, 곧 l2 × 가중치 제곱의 합을 계산하세요.\npenalty = 0.0\n'
      'print(round(float(result["mse"]), 6), round(float(penalty), 6))\n'
      '# 확인용: 총 loss가 자료 오차와 규제 항의 합인지 비교해요.\nprint(bool(np.isclose(float(result["loss"]), float(result["mse"]) + float(penalty), atol=1e-5)))\n')
t5_sol = t5.replace('penalty = 0.0\n', '# L2 규제는 가중치를 제곱해 더한 값에 l2를 곱해요. 학습은 이 벌점까지 더한 loss를 줄여요.\n'
                    'penalty = l2 * np.sum(np.square(model.get_weights()[0]))\n')
u5 = (Script(t5)
      .say('예측 3.0이 정답과 같아 자료 오차는 0이에요. 총 loss에 더해지는 규제 항을 직접 계산해야 해요.', 'text:규제 항, 곧 l2 × 가중치 제곱의 합을 계산하세요.')
      .run('print(round(float(result["mse"])', 'print(bool(np.isclose')
      .say('0.0 0.0과 False예요. 총 loss는 0이 아니라서 자료 오차만으로는 맞지 않아요.', 'output')
      .patch('penalty = 0.0\n', 'penalty = l2 * np.sum(np.square(model.get_weights()[0]))\n', 'l2 * np.sum(np.square(model.get_weights()[0]))로 바꿔요.')
      .run('print(round(float(result["mse"])', 'print(bool(np.isclose')
      .say('0.0 0.2와 True예요. 가중치 1 두 개의 제곱합 2에 0.1을 곱한 0.2가 총 loss예요.', 'output')
      .say('조심하세요. 총 loss와 자료 오차 지표는 같은 값이 아니에요. 규제를 걸면 정답을 맞혀도 loss가 0이 아닐 수 있어요.', 'code:np.square(model.get_weights()[0])'))

# 6. ModelCheckpoint writes a file; the memory model is not replaced.
t6 = (HEAD + 'from pathlib import Path\n\n' + MAKE + VALID + 'epochs = 3\nmodel = make_model()\n'
      'checkpoint = keras.callbacks.ModelCheckpoint("best.keras", monitor="val_loss", mode="min", save_best_only=True)\n'
      'model.fit(X_train, y_train, validation_data=(X_valid, y_valid), epochs=epochs, batch_size=2, shuffle=False, callbacks=[checkpoint], verbose=0)\n'
      '# 이 줄을 고쳐 검증 손실이 가장 작았을 때 저장한 파일에서 모델을 불러오세요.\nrestored = model\n'
      'print(Path("best.keras").is_file())\nprint(float(restored.evaluate(X_valid, y_valid, verbose=0)) < float(model.evaluate(X_valid, y_valid, verbose=0)))\n')
t6_sol = t6.replace('restored = model\n', '# 최고 모델은 파일에만 있어요. 메모리의 model은 마지막 epoch 상태 그대로라 직접 불러와요.\n'
                    'restored = keras.models.load_model("best.keras")\n')
u6 = (Script(t6)
      .say('ModelCheckpoint는 최고 모델을 파일에 저장해요. 그 파일에서 모델을 불러와야 해요.', 'text:검증 손실이 가장 작았을 때 저장한 파일에서 모델을 불러오세요.')
      .run('print(Path("best.keras")', 'print(float(restored.evaluate')
      .say('True와 False예요. 파일은 있지만 restored가 메모리의 마지막 모델 그 자체라 더 나을 수 없어요.', 'output')
      .patch('restored = model\n', 'restored = keras.models.load_model("best.keras")\n', 'keras.models.load_model("best.keras")로 바꿔요.')
      .run('print(Path("best.keras")', 'print(float(restored.evaluate')
      .say('True와 True예요. 불러온 최고 모델의 검증 오차가 마지막 모델보다 작아요.', 'output')
      .say('조심하세요. 최고 모델을 저장해도 메모리의 모델이 바뀌지는 않아요. 쓰려면 파일을 직접 불러와요.', 'code:keras.models.load_model("best.keras")'))

# 7. The learning rate sets the size of one update.
t7 = (HEAD + MAKE + '# 같은 한 batch에서 학습률만 다르게 비교해요.\nrates = [0.1, 0.01]\ntargets = [[2.0], [4.0]]\nX_train = np.array([[1.0], [2.0]], dtype="float32")\ny_train = np.array(targets, dtype="float32")\n'
      '# 시작 가중치 0에서 mse 손실의 기울기예요. 확인용 계산이라 식은 몰라도 돼요.\ngrad = float(np.mean(2 * (0 - y_train) * X_train))\n\n'
      'def updated(rate):\n    # 이 줄을 고쳐 가중치 0에서 기울기 반대 방향으로 rate × grad만큼 한 번 옮긴 값을 돌려주세요.\n    return 0.0\n\n'
      'models = [make_model(rate) for rate in rates]\nfor model in models:\n    model.fit(X_train, y_train, epochs=1, batch_size=2, shuffle=False, verbose=0)\n'
      'print([round(updated(rate), 6) for rate in rates])\nprint([round(float(model.get_weights()[0][0, 0]), 6) for model in models])\n'
      'print([int(model.optimizer.iterations.numpy()) for model in models])\n')
t7_sol = t7.replace('    return 0.0\n', '    # SGD는 가중치에서 학습률 × 기울기를 빼요. 학습률이 한 번에 움직이는 크기를 정해요.\n    return 0.0 - rate * grad\n')
u7 = (Script(t7)
      .say('두 모델은 똑같이 한 번 갱신해요. 학습률이 한 번에 얼마나 옮기는지 직접 계산해 실제 가중치와 비교해야 해요.', 'text:가중치 0에서 기울기 반대 방향으로 rate × grad만큼 한 번 옮긴 값을 돌려주세요.')
      .run('print([round(updated', 'print([int(model.optimizer')
      .say('[0.0, 0.0], [1.0, 0.1], [1, 1]이에요. 실제 가중치는 학습률마다 다르게 움직였어요.', 'output')
      .patch('    return 0.0\n', '    return 0.0 - rate * grad\n', '0.0 - rate * grad를 돌려줘요.')
      .run('print([round(updated', 'print([int(model.optimizer')
      .say('[1.0, 0.1]로 실제 가중치와 같아요. 기울기 -10에 학습률을 곱한 만큼 옮겼고 둘 다 한 번 갱신했어요.', 'output')
      .say('조심하세요. 학습률은 반복 횟수가 아니라 한 번의 크기예요. 크게 움직였다고 항상 더 좋은 학습률인 것도 아니에요.', 'code:0.0 - rate * grad'))

PROBE6 = ('assert restored is not model, "파일에서 불러온 모델을 쓰세요."\n'
          'control = make_model()\ncontrol.fit(X_train, y_train, epochs=1, batch_size=2, shuffle=False, verbose=0)\n'
          'assert np.allclose(restored.predict(X_valid, verbose=0), control.predict(X_valid, verbose=0)), "검증 손실이 가장 작았던 epoch의 모델인지 확인하세요."')

SPECS = [
    code_step('stp_f079304d-1221-4ace-b5aa-d6b707cedd80', 'epochs × batch 수로 갱신 횟수를 계산하세요', 'epoch와 batch를 구별해 가중치 갱신 횟수를 직접 계산하고 실제 횟수와 비교해요.',
              'updates가 epochs면 2 4다. epochs * math.ceil(len(X_train) / batch_size)로 고쳐 4 4를 확인한다. 채점은 다른 batch 크기와 epoch로 실행한다.',
              'epoch는 훈련 표 전체를 한 번 도는 단위, batch는 한 번에 가중치를 고칠 때 쓰는 관측 묶음이에요. `model.optimizer.iterations`는 실제로 가중치를 고친 횟수예요. `math.ceil`은 올림이에요.',
              'updates 줄을 고쳐 epoch마다 batch 수만큼 갱신하는 횟수를 계산하세요. 채점은 다른 batch 크기와 epoch로도 실행해요.',
              ['코드 실행을 눌러 두 수를 비교하세요.', '`updates = epochs`를 `updates = epochs * math.ceil(len(X_train) / batch_size)`로 고치세요.', '코드 실행을 눌러 4 4가 나오는지 확인하세요.', SUB],
              t1, t1_sol, u1, {u1.actions[-1]['text']: W}, cases=[{'batch_size': 3}, {'epochs': 3, 'batch_size': 1}, {'batch_size': 4}],
              reject=[([['updates = epochs * math.ceil(len(X_train) / batch_size)\n', 'updates = epochs * len(X_train) // batch_size\n']], 'Dropping the last partial batch'),
                      ([['updates = epochs * math.ceil(len(X_train) / batch_size)\n', 'updates = 4\n']], 'Typing four')],
              accept=[([['updates = epochs * math.ceil(len(X_train) / batch_size)\n', 'updates = epochs * -(-len(X_train) // batch_size)\n']], 'Ceiling by negative floor division')], timeout=T),
    code_step('stp_2e7defee-f547-45a1-b05d-d9ea109c05f2', 'restore_best_weights=True로 가장 좋았던 가중치로 되돌리세요', '조기 중단이 멈춘 순간과 가장 좋았던 순간을 구별해 최고 가중치를 되돌려요.',
              '되돌리지 않으면 2, False, 2다. restore_best_weights=True를 더해 2, True, 2를 확인한다. 채점은 다른 patience로 실행한다.',
              '`EarlyStopping`은 검증 손실이 patience번 연속 좋아지지 않으면 학습을 멈춰요. 이 자료에서는 첫 epoch 뒤부터 검증 손실이 나빠져요. 비교 모델 control은 같은 시작에서 한 epoch만 학습해요.',
              'callback 줄을 고쳐 멈출 때 검증 손실이 가장 작았던 epoch의 가중치로 되돌리세요. 채점은 다른 patience로도 실행해요.',
              ['코드 실행을 눌러 세 줄을 확인하세요.', 'EarlyStopping 괄호 안에 `restore_best_weights=True`를 더하세요.', '코드 실행을 눌러 둘째 줄이 True인지 확인하세요.', SUB],
              t3, t3_sol, u3, {u3.actions[-1]['text']: W}, cases=[{'patience': 1}, {'patience': 2}],
              reject=[([['mode="min", patience=patience,', 'mode="max", patience=patience,']], 'Watching for the largest loss'),
                      ([['print(len(history.history["loss"]))\nprint(bool(np.allclose(model.predict(X_valid, verbose=0), control.predict(X_valid, verbose=0))))\nprint(int(model.optimizer.iterations.numpy()))\n',
                         'print(2)\nprint(True)\nprint(2)\n']], 'Typing the result')],
              accept=[([['callback = keras.callbacks.EarlyStopping(monitor="val_loss", mode="min", patience=patience,', 'callback = keras.callbacks.EarlyStopping(patience=patience,']], 'Default monitor val_loss')], timeout=T),
    code_step('stp_ae460898-4f86-4d24-9859-f9c1d8124ec4', 'training=False로 추론 때는 Dropout을 끄세요', 'Dropout이 학습 때만 일부 입력을 쉬게 하고 추론 때는 그대로 넘기는 것을 써서 확인해요.',
              'training=True면 추론 쪽도 일부가 0이고 나머지가 2.0이다. training=False로 고쳐 [[1.0, 1.0, 1.0, 1.0]]과 True를 확인한다. 채점은 다른 비율과 폭으로 실행한다.',
              '`Dropout(rate)`은 학습할 때 입력의 일부를 0으로 쉬게 하고, 남은 값을 1 / (1 - rate)배로 키워 합을 맞춰요. 층을 부를 때 `training=False`면 추론처럼 아무것도 끄지 않아요.',
              'inference 줄을 고쳐 추론 때처럼 Dropout을 적용하지 않게 부르세요. 채점은 다른 비율과 입력 폭으로도 실행해요.',
              ['코드 실행을 눌러 추론 쪽에 0이 있는지 확인하세요.', '첫 호출의 `training=True`를 `training=False`로 고치세요.', '코드 실행을 눌러 모두 1.0인지 확인하세요.', SUB],
              t4, t4_sol, u4, {u4.actions[-1]['text']: W}, cases=[{'rate': 0.25}, {'width': 6}],
              reject=[([['inference = layer(inputs, training=False).numpy()\n', 'inference = (inputs * (1 - rate)).numpy()\n']], 'Scaling down at inference'),
                      ([['inference = layer(inputs, training=False).numpy()\n', 'inference = np.ones((1, 4))\n']], 'Typing four ones')],
              accept=[([['inference = layer(inputs, training=False).numpy()\n', 'inference = layer(inputs).numpy()\n']], 'Direct call defaults to inference')], timeout=T),
    code_step('stp_b9326c99-7b82-4c59-9eea-97a24ee5dea9', 'l2 × 가중치 제곱합으로 규제 항을 구하세요', '총 loss가 자료 오차에 규제 벌점을 더한 값임을 직접 계산해 확인해요.',
              'penalty가 0이면 0.0 0.0, False다. l2 * np.sum(np.square(model.get_weights()[0]))로 고쳐 0.0 0.2, True를 확인한다. 채점은 다른 규제 세기와 정답으로 실행한다.',
              'L2 규제는 가중치가 너무 커지지 않게 벌점을 더해요. 벌점은 l2 × (가중치 제곱의 합)이고, 학습은 자료 오차와 이 벌점을 더한 총 loss를 줄여요. `model.get_weights()[0]`은 Dense의 가중치예요.',
              'penalty 줄을 고쳐 규제 항, 곧 l2 × 가중치 제곱의 합을 계산하세요. 채점은 다른 규제 세기와 정답으로도 실행해요.',
              ['코드 실행을 눌러 세 값을 확인하세요.', '`penalty = 0.0`을 `penalty = l2 * np.sum(np.square(model.get_weights()[0]))`로 고치세요.', '코드 실행을 눌러 True가 나오는지 확인하세요.', SUB],
              t5, t5_sol, u5, {u5.actions[-1]['text']: W}, cases=[{'l2': 0.05}, {'targets': [[1.0]]}, {'rows': [[1.0, 1.0], [0.0, 2.0]], 'targets': [[2.0], [0.0]], 'l2': 0.3}],
              reject=[([['penalty = l2 * np.sum(np.square(model.get_weights()[0]))\n', 'penalty = l2\n']], 'The strength without the weights'),
                      ([['penalty = l2 * np.sum(np.square(model.get_weights()[0]))\n', 'penalty = 0.2\n']], 'Typing the penalty')],
              accept=[([['penalty = l2 * np.sum(np.square(model.get_weights()[0]))\n', 'penalty = l2 * float((model.get_weights()[0] ** 2).sum())\n']], 'Power and sum')], timeout=T),
    code_step('stp_c2b23086-5c99-45d9-8db0-2fdd3163f44e', 'load_model("best.keras")로 저장한 최고 모델을 불러오세요', '최고 모델을 파일로 저장하는 것과 메모리의 모델을 바꾸는 것을 구별해 직접 불러와요.',
              'restored가 메모리의 model이면 True, False다. keras.models.load_model("best.keras")로 고쳐 True, True를 확인한다. 채점은 다른 epoch로 실행하고 불러온 모델이 첫 epoch의 모델인지 검사한다.',
              '`ModelCheckpoint(save_best_only=True)`는 검증 손실이 가장 작았던 epoch의 모델을 파일 best.keras에 저장해요. 이 자료에서는 첫 epoch가 가장 좋아요. 메모리의 model은 마지막 epoch 상태 그대로예요.',
              'restored 줄을 고쳐 검증 손실이 가장 작았을 때 저장한 파일에서 모델을 불러오세요. 채점은 다른 epoch로도 실행해요.',
              ['코드 실행을 눌러 두 줄을 확인하세요.', '`restored = model`을 `restored = keras.models.load_model("best.keras")`로 고치세요.', '코드 실행을 눌러 True와 True가 나오는지 확인하세요.', SUB],
              t6, t6_sol, u6, {u6.actions[-1]['text']: W}, cases=[{'epochs': 2}, {'epochs': 4}], probe=PROBE6,
              reject=[([['print(Path("best.keras").is_file())\nprint(float(restored.evaluate(X_valid, y_valid, verbose=0)) < float(model.evaluate(X_valid, y_valid, verbose=0)))\n',
                         'print(True)\nprint(True)\n']], 'Typing the result'),
                      ([['restored = keras.models.load_model("best.keras")\n', 'restored = make_model()\n']], 'A fresh untrained model')],
              accept=[([['restored = keras.models.load_model("best.keras")\n', 'restored = keras.saving.load_model("best.keras")\n']], 'keras.saving.load_model')], timeout=T),
    code_step('stp_b0aebfbb-fe0e-46f8-a732-ed82ff789c6a', '학습률 × 기울기만큼 한 번 옮긴 가중치를 계산하세요', '학습률이 반복 횟수가 아니라 한 번 갱신하는 크기임을 직접 계산해 실제 가중치와 비교해요.',
              'updated가 0.0이면 실제 가중치 [1.0, 0.1]과 다르다. 0.0 - rate * grad로 고쳐 [1.0, 0.1]과 갱신 [1, 1]을 확인한다. 채점은 다른 학습률과 정답으로 실행한다.',
              '학습률은 한 번 갱신할 때 가중치를 얼마나 움직일지 정해요. SGD는 가중치에서 학습률 × 기울기를 빼요. 두 모델은 같은 한 batch로 한 번씩만 갱신하고 학습률만 달라요.',
              'updated의 return 줄을 고쳐 가중치 0에서 기울기 반대 방향으로 rate × grad만큼 한 번 옮긴 값을 돌려주세요. 채점은 다른 학습률과 정답으로도 실행해요.',
              ['코드 실행을 눌러 계산과 실제 가중치를 비교하세요.', '`return 0.0`을 `return 0.0 - rate * grad`로 고치세요.', '코드 실행을 눌러 두 목록이 같은지 확인하세요.', SUB],
              t7, t7_sol, u7, {u7.actions[-1]['text']: W}, cases=[{'rates': [0.2, 0.05]}, {'targets': [[1.0], [0.0]]}],
              reject=[([['    return 0.0 - rate * grad\n', '    return -grad\n']], 'Leaving out the rate'),
                      ([['    return 0.0 - rate * grad\n', '    return rate * grad\n']], 'Moving along the gradient')],
              accept=[([['    return 0.0 - rate * grad\n', '    return -rate * grad\n']], 'Negated product')], timeout=T),
]
