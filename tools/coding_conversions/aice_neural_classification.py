"""aice-neural-classification: 7 answer-picking steps -> coding steps (2026-10-30).

Each step edits one line of a tiny Keras classifier on CPU: the class rule on sigmoid probabilities, the
from_logits setting, accuracy against the new rows' actual labels, the softmax output layer, the loss for
integer labels, the one-hot encoding and the class names behind argmax. Fixed weights make probabilities
exact; the one step that trains reads only thresholded predictions on well separated rows. Prepared cases
rerun with other rows, thresholds, labels and class names, so typed outputs and the starter fail."""
from _kit import Script, code_step

OPENING = ['이 수업에서는 신경망의 분류 출력과 정답 모양을 직접 코드로 맞춰요. 이진 분류와 다중 분류를 구별해요.',
           'sigmoid와 softmax 결과를 읽고, 정수·원핫 정답과 손실, 출력 위치와 이름의 연결을 실행 결과로 확인해요.']
PRD_SCOPE = ['두 챕터·두 단원·아홉 스텝으로 같은 배송 상태를 신경망으로 분류해요.',
             '확률에 규칙 적용·from_logits·새 배송의 실제 정답으로 정확도·softmax 출력층·정수 정답의 손실·원핫 정답·argmax 위치의 이름을 한 곳씩 직접 고쳐 써요.']
PRD_GRADING = ['직접 고친 코드를 실제 파이썬·TensorFlow로 실행해 판정해요. 실행·해설만으로 성공시키지 않아요.',
               '고정 가중치로 확률을 정확한 값으로 만들고, 학습하는 스텝은 멀리 떨어진 배송의 예측 범주만 비교해요. 다른 입력·경계값·정답·범주 이름으로 다시 실행해 기준 풀이와 비교해요.',
               '결과를 글자로 적은 답, 경계값을 빼는 규칙, 확률을 logit으로 다루는 손실, 훈련 예측과의 비교, sigmoid 여러 칸, 범주 수를 빠뜨린 원핫, 정렬한 이름은 거절해요.',
               '마지막 도전(stp_6e8529c4-201c-4b8d-b922-550464a4336e): 실제 Python 실행과 다른 준비 자료의 결과를 검사해요. 시작 코드는 실패하고 동등한 풀이도 통과해야 해요.']
PRD_NARRATION = ['동작 확인용 고정 가중치와 작은 실제 학습을 구별해요. 한 곳씩 고친 뒤 실제 확률·손실·이름을 읽어요.',
                 '확률과 범주·확률과 logit·새 자료의 정답·출력 칸의 합·정답 표현과 손실·위치와 이름을 조심할 지점으로 짚어요.']

HEAD = ('import os\nos.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")\nimport numpy as np\nimport tensorflow as tf\nfrom tensorflow import keras\n\n'
        '# 작은 CPU 실습의 실행 자원을 제한해요.\ntf.config.threading.set_intra_op_parallelism_threads(1)\n'
        'tf.config.threading.set_inter_op_parallelism_threads(1)\nkeras.utils.set_random_seed(7)\n')
FIXED = '# 초기 가중치는 학습 결과가 아닌 출력 동작 확인용이에요.\n'
SIG = 'model = keras.Sequential([keras.Input(shape=(1,)), keras.layers.Dense(1, activation="sigmoid", kernel_initializer="ones", bias_initializer="zeros")])\n'
SOFT = ('model = keras.Sequential([keras.Input(shape=(1,)), keras.layers.Dense(3, activation="softmax", '
        'kernel_initializer=keras.initializers.Constant([[0.0, 1.0, -1.0]]), bias_initializer="zeros")])\n')
SUB = '수정한 코드를 제출하세요.'
W = '실제 Keras 동작을 정확히 말해요.'
T = 45

# 1. A probability is not a class; apply the rule.
c1 = (HEAD + 'rows = [[0.0], [1.0]]\n# 이번 경보 규칙은 확률이 threshold 이상이면 지연 1이에요. 경계값도 지연이에요.\nthreshold = 0.5\n' + FIXED + SIG
      + 'probabilities = model.predict(np.array(rows, dtype="float32"), verbose=0).ravel()\nprint([round(float(p), 6) for p in probabilities])\n'
      '# 이 줄을 고쳐 확률에 규칙을 적용해 정상 0·지연 1을 고르세요.\nlabels = probabilities\nprint(labels.tolist())\n')
c1_sol = c1.replace('labels = probabilities\n', '# 비교 결과 True·False를 astype(int)로 1·0으로 바꿔요. 경계값도 지연이라 >=예요.\nlabels = (probabilities >= threshold).astype(int)\n')
d1 = (Script(c1)
      .say('sigmoid는 확률을 내요. 확률에 이번 규칙을 적용해야 정상과 지연이 정해져요.', 'text:확률에 규칙을 적용해 정상 0·지연 1을 고르세요.')
      .run('print([round(float(p), 6)', 'print(labels.tolist())')
      .say('두 줄 모두 [0.5, 0.731059]예요. 아직 확률을 그대로 범주 자리에 두었어요.', 'output')
      .patch('labels = probabilities\n', 'labels = (probabilities >= threshold).astype(int)\n', 'probabilities >= threshold를 astype(int)로 바꿔요.')
      .run('print([round(float(p), 6)', 'print(labels.tolist())')
      .say('[1, 1]이에요. 경계값 0.5도 지연이라 두 배송 모두 지연이에요.', 'output')
      .say('조심하세요. >로 쓰면 확률 0.5인 첫 배송은 정상이 돼요. 그리고 0.73은 학습 전 가중치의 값이라 실제 지연 빈도로 검증된 확률이 아니에요.', 'code:probabilities >= threshold'))

# 2. A sigmoid already gives probabilities: from_logits=False.
c2 = (HEAD + 'rows = [[0.0], [1.0]]\ny = [0.0, 1.0]\n' + FIXED + SIG
      + '# 이 줄을 고쳐 모델 출력이 이미 확률이라고 손실에 알리세요.\nloss = keras.losses.BinaryCrossentropy(from_logits=True)\n'
      'p = model.predict(np.array(rows, dtype="float32"), verbose=0)\ntarget = np.array(y, dtype="float32").reshape(-1, 1)\nvalue = float(loss(target, p))\n'
      '# 확인용: 확률로 직접 계산한 교차 엔트로피예요.\nmanual = float(-np.mean(target * np.log(p) + (1 - target) * np.log(1 - p)))\n'
      'print(round(value, 4))\nprint(bool(np.isclose(value, manual, atol=1e-4)))\n')
c2_sol = c2.replace('loss = keras.losses.BinaryCrossentropy(from_logits=True)\n',
                    '# sigmoid가 이미 확률을 냈어요. from_logits=False는 "확률을 받아요"라는 뜻이에요.\nloss = keras.losses.BinaryCrossentropy(from_logits=False)\n')
d2 = (Script(c2)
      .say('이 모델은 sigmoid가 이미 확률을 냈어요. 손실에 확률을 받는다고 알려야 해요.', 'text:모델 출력이 이미 확률이라고 손실에 알리세요.')
      .run('print(round(value, 4))', 'print(bool(np.isclose')
      .say('0.6436과 False예요. 확률을 logit으로 보고 sigmoid를 한 번 더 적용해 직접 계산과 달라요.', 'output')
      .patch('from_logits=True', 'from_logits=False', 'True를 False로 바꿔요.')
      .run('print(round(value, 4))', 'print(bool(np.isclose')
      .say('0.5032와 True예요. 확률로 직접 계산한 값과 같아요.', 'output')
      .say('조심하세요. 출력층에 활성화 없이 logit을 내는 다른 설계라면 그때 from_logits=True를 써요. 출력 형식과 옵션을 함께 맞춰요.', 'code:from_logits=False'))

# 3. Accuracy on new rows needs their actual labels.
c3 = (HEAD + 'model = keras.Sequential([keras.Input(shape=(1,)), keras.layers.Dense(1, activation="sigmoid", kernel_initializer="zeros", bias_initializer="zeros")])\n'
      'model.compile(optimizer=keras.optimizers.SGD(learning_rate=0.5), loss="binary_crossentropy")\n'
      'X_train = np.array([[-2.0], [-1.0], [1.0], [2.0]], dtype="float32")\ny_train = np.array([[0.0], [0.0], [1.0], [1.0]], dtype="float32")\n'
      'model.fit(X_train, y_train, epochs=3, batch_size=4, shuffle=False, verbose=0)\n'
      '# 학습에 넣지 않은 새 배송과 그 실제 정답이에요.\nX_new = np.array([[-3.0], [-0.5], [0.5], [3.0]], dtype="float32")\ny_new = [0, 1, 1, 1]\n'
      '# 확률 0.5 이상을 지연 1로 읽어요.\ntrain_pred = (model.predict(X_train, verbose=0).ravel() >= 0.5).astype(int)\nnew_pred = (model.predict(X_new, verbose=0).ravel() >= 0.5).astype(int)\n'
      'print(train_pred.tolist())\nprint(new_pred.tolist())\n'
      '# 이 줄을 고쳐 새 배송의 예측을 그 실제 정답 y_new와 비교한 정확도를 구하세요.\naccuracy = float((new_pred == new_pred).mean())\nprint(accuracy)\n')
c3_sol = c3.replace('accuracy = float((new_pred == new_pred).mean())\n',
                    '# 정확도는 같은 배송의 예측과 실제 정답이 같은 비율이에요.\naccuracy = float((new_pred == np.array(y_new)).mean())\n')
d3 = (Script(c3)
      .say('새 배송의 점수는 그 배송의 실제 정답과 비교해야 정해져요. accuracy 줄을 y_new와 비교하게 고쳐요.', 'text:새 배송의 예측을 그 실제 정답 y_new와 비교한 정확도를 구하세요.')
      .run('print(train_pred.tolist())', 'print(accuracy)')
      .say('[0, 0, 1, 1], [0, 0, 1, 1], 1.0이에요. 예측을 예측끼리 비교해 늘 1.0이에요.', 'output')
      .patch('(new_pred == new_pred)', '(new_pred == np.array(y_new))', '비교 대상을 np.array(y_new)로 바꿔요.')
      .run('print(train_pred.tolist())', 'print(accuracy)')
      .say('0.75예요. 거리 -0.5인 배송은 가까운데도 실제로는 지연이라 네 건 중 세 건만 맞았어요.', 'output')
      .say('조심하세요. 훈련 배송을 모두 맞혔다고 새 배송도 모두 맞히는 게 아니에요. 새 자료의 점수는 그 자료의 실제 정답으로 계산해요.', 'code:np.array(y_new)'))

# 4. Mutually exclusive classes: one softmax column per class.
c4 = (HEAD + 'classes = ["normal", "late", "cancelled"]\nrows = [[1.0], [2.0]]\n# 가중치를 영으로 정해 출력 형식만 확인해요.\n'
      '# 이 줄의 Dense를 고쳐 classes마다 한 칸씩, 확률 합이 1인 출력을 만드세요.\n'
      'model = keras.Sequential([keras.Input(shape=(1,)), keras.layers.Dense(1, activation="sigmoid", kernel_initializer="zeros", bias_initializer="zeros")])\n'
      'probabilities = model.predict(np.array(rows, dtype="float32"), verbose=0)\nprint(list(probabilities.shape))\nprint(probabilities.sum(axis=1).round(4).tolist())\n')
c4_sol = c4.replace('keras.layers.Dense(1, activation="sigmoid",',
                    '# 범주 수만큼 칸을 만들고 softmax로 각 행의 확률 합을 1로 맞춰요.\n                          keras.layers.Dense(len(classes), activation="softmax",')
d4 = (Script(c4)
      .say('정상·지연·취소 중 하나를 고르는 분류예요. 범주마다 한 칸, 행마다 확률 합이 1인 출력이 필요해요.', 'text:Dense를 고쳐 classes마다 한 칸씩, 확률 합이 1인 출력을 만드세요.')
      .run('print(list(probabilities.shape))', 'print(probabilities.sum(axis=1)')
      .say('[2, 1]과 [0.5, 0.5]예요. 배송마다 한 칸뿐이라 세 범주를 나눌 수 없어요.', 'output')
      .patch('keras.layers.Dense(1, activation="sigmoid",', 'keras.layers.Dense(len(classes), activation="softmax",', 'Dense(len(classes), activation="softmax")로 바꿔요.')
      .run('print(list(probabilities.shape))', 'print(probabilities.sum(axis=1)')
      .say('[2, 3]과 [1.0, 1.0]이에요. 두 배송에 범주 세 칸씩이고 각 행의 합이 1이에요.', 'output')
      .say('조심하세요. 칸을 셋으로 늘려도 sigmoid면 칸마다 따로 확률이라 합이 1이 아니에요. 하나만 고르는 분류는 softmax예요.', 'code:activation="softmax"'))

# 5. Integer labels need the sparse loss.
c5 = (HEAD + 'classes = ["normal", "late", "cancelled"]\nrows = [[1.0], [-1.0]]\n# 정답은 범주 번호 하나씩이에요.\nlabels = [0, 2]\n'
      '# 가중치는 위치를 확인하기 위한 직접 지정 값이에요.\n' + SOFT
      + 'probabilities = model.predict(np.array(rows, dtype="float32"), verbose=0)\ny = np.array(labels, dtype="int32")\n'
      '# 이 줄을 고쳐 범주 번호 정답을 받는 교차 엔트로피 손실을 쓰세요.\nloss = keras.losses.CategoricalCrossentropy()\nvalue = float(loss(y, probabilities))\n'
      '# 확인용: 각 배송의 정답 칸 확률로 직접 계산한 값이에요.\nmanual = float(-np.mean(np.log(probabilities[np.arange(len(y)), y])))\n'
      'print(round(value, 4))\nprint(bool(np.isclose(value, manual, atol=1e-4)))\n')
c5_sol = c5.replace('loss = keras.losses.CategoricalCrossentropy()\n',
                    '# Sparse가 붙은 손실은 0, 2 같은 범주 번호를 그대로 받아요.\nloss = keras.losses.SparseCategoricalCrossentropy()\n')
d5 = (Script(c5)
      .say('정답이 0, 2처럼 범주 번호 하나씩이에요. 번호를 그대로 받는 손실로 고쳐야 해요.', 'text:범주 번호 정답을 받는 교차 엔트로피 손실을 쓰세요.')
      .run('print(round(value, 4))', error='ValueError')
      .say('ValueError예요. CategoricalCrossentropy는 원핫 정답을 기대해 번호 하나와 세 칸 확률의 모양이 안 맞아요.', 'output')
      .patch('keras.losses.CategoricalCrossentropy()', 'keras.losses.SparseCategoricalCrossentropy()', '앞에 Sparse를 붙여요.')
      .run('print(round(value, 4))', 'print(bool(np.isclose')
      .say('1.4076과 True예요. 각 배송의 정답 칸 확률로 직접 계산한 값과 같아요.', 'output')
      .say('조심하세요. 원핫 정답과 범주 번호 정답은 표현이 달라요. 정답 모양에 맞는 손실을 골라요.', 'code:SparseCategoricalCrossentropy()'))

# 6. One-hot labels must have one column per class.
c6 = (HEAD + 'classes = ["normal", "late", "cancelled"]\nrows = [[1.0], [-1.0]]\nlabels = [0, 2]\n# 가중치는 위치를 확인하기 위한 직접 지정 값이에요.\n' + SOFT
      + 'probabilities = model.predict(np.array(rows, dtype="float32"), verbose=0)\ny = np.array(labels, dtype="int32")\n'
      '# 이 줄을 고쳐 범주 번호를 범주 수만큼의 칸을 가진 원핫 정답으로 바꾸세요.\none_hot = y\n'
      'sparse_loss = keras.losses.SparseCategoricalCrossentropy()(y, probabilities)\n'
      'categorical_loss = keras.losses.CategoricalCrossentropy()(one_hot, probabilities)\n'
      'print(np.array(one_hot).astype(int).tolist())\nprint(bool(np.isclose(float(sparse_loss), float(categorical_loss))))\n')
c6_sol = c6.replace('one_hot = y\n', '# to_categorical은 범주 번호의 자리만 1인 목록으로 바꿔요. num_classes로 칸 수를 범주 수에 맞춰요.\n'
                    'one_hot = keras.utils.to_categorical(y, num_classes=len(classes))\n')
d6 = (Script(c6)
      .say('같은 정답을 원핫으로 바꿔 원핫용 손실과 비교해요. 범주 번호를 범주 수만큼의 칸으로 바꿔야 해요.', 'text:범주 번호를 범주 수만큼의 칸을 가진 원핫 정답으로 바꾸세요.')
      .run('print(np.array(one_hot)', error='ValueError')
      .say('ValueError예요. 번호 그대로는 세 칸 확률과 모양이 안 맞아요.', 'output')
      .patch('one_hot = y\n', 'one_hot = keras.utils.to_categorical(y, num_classes=len(classes))\n', 'keras.utils.to_categorical(y, num_classes=len(classes))로 바꿔요.')
      .run('print(np.array(one_hot)', 'print(bool(np.isclose')
      .say('[[1, 0, 0], [0, 0, 1]]과 True예요. 첫 칸과 셋째 칸이 1이고 두 손실이 같아요. 표현만 다르고 정답의 뜻은 같아요.', 'output')
      .say('조심하세요. num_classes를 빼면 정답에 나온 가장 큰 번호까지만 칸을 만들어요. 정답이 0과 1뿐이면 두 칸이 돼 모양이 어긋나요.', 'code:num_classes=len(classes)'))

# 7. argmax gives positions; map them to the class names.
c7 = (HEAD + 'classes = ["normal", "late", "cancelled"]\nrows = [[1.0], [-1.0]]\n# 가중치는 위치와 이름을 확인하기 위한 직접 지정 값이에요.\n' + SOFT
      + 'probabilities = model.predict(np.array(rows, dtype="float32"), verbose=0)\nindices = probabilities.argmax(axis=1)\nprint(indices.tolist())\n'
      '# 이 줄을 고쳐 위치 번호마다 classes에서 같은 자리의 이름을 꺼내세요.\nnames = indices\nprint(names.tolist())\n')
c7_sol = c7.replace('names = indices\n', '# 이름 목록을 배열로 바꾸면 위치 번호 배열로 같은 자리의 이름을 한 번에 꺼내요.\nnames = np.array(classes)[indices]\n')
d7 = (Script(c7)
      .say('argmax는 확률이 가장 큰 칸의 위치 번호를 줘요. 그 번호를 학습 때의 classes 순서로 이름에 연결해야 해요.', 'text:위치 번호마다 classes에서 같은 자리의 이름을 꺼내세요.')
      .run('print(indices.tolist())', 'print(names.tolist())')
      .say('[1, 2]가 두 번이에요. 번호 자체는 이름이 아니에요.', 'output')
      .patch('names = indices\n', 'names = np.array(classes)[indices]\n', 'np.array(classes)[indices]로 바꿔요.')
      .run('print(indices.tolist())', 'print(names.tolist())')
      .say("['late', 'cancelled']예요. 위치 1과 2를 classes의 같은 자리 이름에 연결했어요.", 'output')
      .say('조심하세요. 이름을 정렬하면 순서가 바뀌어 다른 범주가 나와요. 학습 때 정한 순서 그대로 보존해요.', 'code:np.array(classes)[indices]'))

SPECS = [
    code_step('stp_5beb9fe5-4691-4022-9d24-9820dd6e2c49', '확률 >= threshold로 지연 여부를 고르세요', 'sigmoid 확률과 규칙을 적용해 고른 범주를 구별해 직접 써요.',
              'labels가 확률 그대로면 [0.5, 0.731059]다. (probabilities >= threshold).astype(int)로 고쳐 [1, 1]을 확인한다. 채점은 다른 입력과 경계값으로 실행한다.',
              'sigmoid는 계산값을 0과 1 사이 확률로 바꿔요. 범주는 확률에 규칙을 적용해 골라요. `astype(int)`는 True·False를 1·0으로 바꿔요.',
              'labels 줄을 고쳐 확률에 규칙을 적용해 정상 0·지연 1을 고르세요. 채점은 다른 입력과 경계값으로도 실행해요.',
              ['코드 실행을 눌러 두 줄을 비교하세요.', '`labels = probabilities`를 `labels = (probabilities >= threshold).astype(int)`로 고치세요.', '코드 실행을 눌러 [1, 1]이 나오는지 확인하세요.', SUB],
              c1, c1_sol, d1, {d1.actions[-1]['text']: W}, cases=[{'threshold': 0.8}, {'rows': [[-2.0], [0.0], [3.0]]}],
              reject=[([['(probabilities >= threshold)', '(probabilities > threshold)']], 'Leaving out the boundary'),
                      ([['labels = (probabilities >= threshold).astype(int)\n', 'labels = np.array([1, 1])\n']], 'Typing the labels')],
              accept=[([['labels = (probabilities >= threshold).astype(int)\n', 'labels = np.where(probabilities >= threshold, 1, 0)\n']], 'np.where')], timeout=T),
    code_step('stp_4ab1ddd7-24a0-46aa-bb53-fc03d115890b', 'from_logits=False로 확률 출력을 알리세요', '출력이 확률인지 logit인지에 맞춰 손실 옵션을 직접 정해요.',
              'from_logits=True면 확률에 sigmoid를 한 번 더 적용해 0.6436, False다. from_logits=False로 고쳐 0.5032, True를 확인한다. 채점은 다른 입력과 정답으로 실행한다.',
              'logit은 sigmoid에 넣기 전의 값, 곧 입력 × 가중치 + 편향이에요. `from_logits=True`는 "모델 출력이 아직 logit이에요"라고 손실에 알리는 설정이에요. 이 모델은 sigmoid가 이미 확률을 냈어요.',
              'loss 줄을 고쳐 모델 출력이 이미 확률이라고 손실에 알리세요. 채점은 다른 입력과 정답으로도 실행해요.',
              ['코드 실행을 눌러 직접 계산과 같은지 확인하세요.', '`from_logits=True`를 `from_logits=False`로 고치세요.', '코드 실행을 눌러 True가 나오는지 확인하세요.', SUB],
              c2, c2_sol, d2, {d2.actions[-1]['text']: W}, cases=[{'y': [1.0, 1.0]}, {'rows': [[-1.0], [2.0], [0.5]], 'y': [0.0, 1.0, 0.0]}],
              reject=[([['print(round(value, 4))\nprint(bool(np.isclose(value, manual, atol=1e-4)))\n', 'print(0.5032)\nprint(True)\n']], 'Typing the result'),
                      ([['loss = keras.losses.BinaryCrossentropy(from_logits=False)\n', 'loss = keras.losses.MeanSquaredError()\n']], 'A regression loss')],
              accept=[([['loss = keras.losses.BinaryCrossentropy(from_logits=False)\n', 'loss = keras.losses.BinaryCrossentropy()\n']], 'Default is False')], timeout=T),
    code_step('stp_bec54e30-2b92-459b-9c3e-9453778a1997', '새 배송의 실제 정답 y_new로 정확도를 구하세요', '새 자료의 정확도는 그 자료의 실제 정답과 짝지어 계산하는 것을 직접 써요.',
              '예측을 예측끼리 비교하면 늘 1.0이다. (new_pred == np.array(y_new))로 고쳐 0.75를 확인한다. 채점은 다른 실제 정답으로 실행한다.',
              '작은 이진 분류를 세 epoch 학습했어요. 학습에 넣지 않은 새 배송 네 건과 그 실제 정답 y_new가 있어요. 정확도는 예측과 실제 정답이 같은 배송의 비율이에요.',
              'accuracy 줄을 고쳐 새 배송의 예측을 그 실제 정답 y_new와 비교한 정확도를 구하세요. 채점은 다른 실제 정답으로도 실행해요.',
              ['코드 실행을 눌러 정확도를 확인하세요.', '`(new_pred == new_pred)`를 `(new_pred == np.array(y_new))`로 고치세요.', '코드 실행을 눌러 0.75가 나오는지 확인하세요.', SUB],
              c3, c3_sol, d3, {d3.actions[-1]['text']: W}, cases=[{'y_new': [0, 0, 1, 1]}, {'y_new': [1, 1, 0, 0]}],
              reject=[([['(new_pred == np.array(y_new))', '(new_pred == train_pred)']], 'Comparing with the training predictions'),
                      ([['accuracy = float((new_pred == np.array(y_new)).mean())\n', 'accuracy = 0.75\n']], 'Typing the accuracy')],
              accept=[([['accuracy = float((new_pred == np.array(y_new)).mean())\n', 'from sklearn.metrics import accuracy_score\naccuracy = float(accuracy_score(y_new, new_pred))\n']], 'accuracy_score')], timeout=T),
    code_step('stp_0092328f-5a3c-4511-ad6b-c74391c88cf8', 'Dense(len(classes), activation="softmax")로 범주 칸을 만드세요', '배타적인 여러 범주에는 범주마다 한 칸, 합이 1인 softmax 출력을 써요.',
              'sigmoid 한 칸이면 [2, 1], 합 0.5다. Dense(len(classes), activation="softmax")로 고쳐 [2, 3], 합 1.0을 확인한다. 채점은 다른 범주 수와 배송 수로 실행한다.',
              '정상·지연·취소 세 종류 중 하나를 골라요. softmax는 출력 칸들을 확률 합이 1이 되게 바꿔요. 출력 모양 [배송 수, 범주 수]의 둘째 숫자가 범주 칸이에요.',
              'model 줄의 Dense를 고쳐 classes마다 한 칸씩, 확률 합이 1인 출력을 만드세요. 채점은 다른 범주 수로도 실행해요.',
              ['코드 실행을 눌러 출력 모양과 합을 확인하세요.', '`Dense(1, activation="sigmoid", ...)`를 `Dense(len(classes), activation="softmax", ...)`로 고치세요.', '코드 실행을 눌러 [2, 3]과 [1.0, 1.0]이 나오는지 확인하세요.', SUB],
              c4, c4_sol, d4, {d4.actions[-1]['text']: W}, cases=[{'classes': ['a', 'b', 'c', 'd']}, {'rows': [[0.0], [1.0], [5.0]]}],
              reject=[([['keras.layers.Dense(len(classes), activation="softmax",', 'keras.layers.Dense(len(classes), activation="sigmoid",']], 'Sigmoid per column'),
                      ([['keras.layers.Dense(len(classes), activation="softmax",', 'keras.layers.Dense(3, activation="softmax",']], 'Typing three classes')],
              accept=[([['keras.layers.Dense(len(classes), activation="softmax",', 'keras.layers.Dense(units=len(classes), activation="softmax",']], 'units keyword')], timeout=T),
    code_step('stp_a2b9df5d-19ef-46b7-a445-3646926ab552', 'SparseCategoricalCrossentropy로 범주 번호 정답을 받으세요', '정답이 범주 번호일 때 그 표현에 맞는 손실을 직접 골라 써요.',
              'CategoricalCrossentropy는 번호 정답과 모양이 안 맞아 ValueError다. SparseCategoricalCrossentropy()로 고쳐 1.4076, True를 확인한다. 채점은 다른 입력과 정답으로 실행한다.',
              '정답이 0, 2처럼 범주 번호 하나씩이에요. `CategoricalCrossentropy`는 원핫 정답을, `SparseCategoricalCrossentropy`는 범주 번호 정답을 받아요. 교차 엔트로피는 정답 칸 확률의 -log 평균이에요.',
              'loss 줄을 고쳐 범주 번호 정답을 받는 교차 엔트로피 손실을 쓰세요. 채점은 다른 입력과 정답으로도 실행해요.',
              ['코드 실행을 눌러 ValueError가 나오는지 확인하세요.', '`CategoricalCrossentropy()`를 `SparseCategoricalCrossentropy()`로 고치세요.', '코드 실행을 눌러 True가 나오는지 확인하세요.', SUB],
              c5, c5_sol, d5, {d5.actions[-1]['text']: W}, cases=[{'labels': [1, 1]}, {'rows': [[2.0], [0.0], [-2.0]], 'labels': [1, 0, 2]}],
              reject=[([['loss = keras.losses.SparseCategoricalCrossentropy()\n', 'loss = keras.losses.SparseCategoricalCrossentropy(from_logits=True)\n']], 'Probabilities as logits'),
                      ([['print(round(value, 4))\nprint(bool(np.isclose(value, manual, atol=1e-4)))\n', 'print(1.4076)\nprint(True)\n']], 'Typing the result')],
              accept=[([['loss = keras.losses.SparseCategoricalCrossentropy()\n', 'loss = keras.losses.SparseCategoricalCrossentropy(from_logits=False)\n']], 'Explicit from_logits=False')], timeout=T),
    code_step('stp_8bb8b9d8-b04e-42d8-9581-68e4df72181e', 'to_categorical(y, num_classes=len(classes))로 원핫 정답을 만드세요', '범주 번호와 원핫은 같은 정답의 다른 표현이며 칸 수를 범주 수에 맞춰야 함을 써서 확인해요.',
              '번호 그대로는 원핫 손실과 모양이 안 맞아 ValueError다. to_categorical(y, num_classes=len(classes))로 고쳐 [[1, 0, 0], [0, 0, 1]]과 True를 확인한다. 채점은 2가 없는 정답으로도 실행한다.',
              '`keras.utils.to_categorical(번호, num_classes=범주 수)`는 각 번호의 자리만 1인 목록으로 바꿔요. 같은 정답을 원핫으로 바꿔 원핫용 손실과 번호용 손실을 비교해요.',
              'one_hot 줄을 고쳐 범주 번호를 범주 수만큼의 칸을 가진 원핫 정답으로 바꾸세요. 채점은 다른 정답으로도 실행해요.',
              ['코드 실행을 눌러 ValueError가 나오는지 확인하세요.', '`one_hot = y`를 `one_hot = keras.utils.to_categorical(y, num_classes=len(classes))`로 고치세요.', '코드 실행을 눌러 True가 나오는지 확인하세요.', SUB],
              c6, c6_sol, d6, {d6.actions[-1]['text']: W}, cases=[{'labels': [0, 1]}, {'rows': [[2.0], [0.0], [-2.0]], 'labels': [1, 1, 2]}],
              reject=[([['keras.utils.to_categorical(y, num_classes=len(classes))', 'keras.utils.to_categorical(y)']], 'No num_classes'),
                      ([['one_hot = keras.utils.to_categorical(y, num_classes=len(classes))\n', 'one_hot = np.array([[1, 0, 0], [0, 0, 1]])\n']], 'Typing the one-hot rows')],
              accept=[([['one_hot = keras.utils.to_categorical(y, num_classes=len(classes))\n', 'one_hot = np.eye(len(classes))[y]\n']], 'Identity rows')], timeout=T),
    code_step('stp_ee524730-dffa-42d4-bf7a-a4dd2f4c7fa0', 'np.array(classes)[indices]로 위치를 이름에 연결하세요', 'argmax의 위치 번호를 학습 때의 범주 순서로 실제 이름에 연결해 써요.',
              'names가 번호 그대로면 [1, 2]다. np.array(classes)[indices]로 고쳐 [\'late\', \'cancelled\']를 확인한다. 채점은 다른 이름과 입력으로 실행한다.',
              '`argmax(axis=1)`은 행마다 확률이 가장 큰 칸의 위치 번호를 줘요. 출력 칸의 순서는 학습 때 정한 classes 순서예요. 이름 목록을 `np.array`로 바꾸면 위치 번호 배열로 같은 자리의 이름을 꺼낼 수 있어요.',
              'names 줄을 고쳐 위치 번호마다 classes에서 같은 자리의 이름을 꺼내세요. 채점은 다른 이름과 입력으로도 실행해요.',
              ['코드 실행을 눌러 두 줄을 비교하세요.', '`names = indices`를 `names = np.array(classes)[indices]`로 고치세요.', "코드 실행을 눌러 ['late', 'cancelled']가 나오는지 확인하세요.", SUB],
              c7, c7_sol, d7, {d7.actions[-1]['text']: W}, cases=[{'classes': ['ok', 'slow', 'lost']}, {'rows': [[0.0], [2.0], [-3.0]]}],
              reject=[([['names = np.array(classes)[indices]\n', 'names = np.array(sorted(classes))[indices]\n']], 'Sorted names'),
                      ([['names = np.array(classes)[indices]\n', 'names = np.array(["late", "cancelled"])\n']], 'Typing the names')],
              accept=[([['names = np.array(classes)[indices]\n', 'names = np.array([classes[i] for i in indices])\n']], 'One name per position')], timeout=T),
]
