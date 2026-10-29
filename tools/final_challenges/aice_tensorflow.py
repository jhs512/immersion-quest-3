from _python_final import make

START = '''import os
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
import numpy as np
import tensorflow as tf
from tensorflow import keras
tf.config.threading.set_intra_op_parallelism_threads(1)
tf.config.threading.set_inter_op_parallelism_threads(1)
keras.utils.set_random_seed(7)
# 행 수와 한 배송의 특성 수는 서로 달라요.
rows = [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]
targets = [[1.0], [2.0], [3.0]]
features = 2
model = keras.Sequential([keras.Input(shape=(len(rows),)), keras.layers.Dense(2, kernel_initializer="zeros")])
model.compile(optimizer="sgd", loss="mse")
loss = model.train_on_batch(np.array(rows, dtype="float32"), np.array(targets, dtype="float32"))
predictions = model(np.array(rows, dtype="float32"), training=False).numpy()
print(list(model.input_shape[1:]))
print(list(predictions.shape))
print(bool(np.isfinite(loss)))
'''
SPEC = make('aice-tensorflow', '배송 특성 수와 예측 한 칸을 연결하세요',
    '입력에는 배송 한 건의 특성 수 features를 써요. 배송 시간 예측은 한 칸이에요. '
    '실제 한 묶음 학습과 예측 뒤 입력 모양, 예측 표 모양, 손실이 유한한지 출력해요. '
    '현재 입력은 [2], 예측은 [3, 1]이에요.',
    '관측 수와 특성 수를 구분하고 실제 학습·예측의 입출력 모양을 맞춰요.', START,
    [('shape=(len(rows),)', 'shape=(features,)', '입력 모양에 행 수가 아닌 특성 수를 넣으세요.'),
     ('keras.layers.Dense(2,', 'keras.layers.Dense(1,', '시간을 한 값으로 예측하도록 출력 칸을 하나로 바꾸세요.')],
    '[2]\n[3, 1]\nTrue',
    [dict(values=dict(rows=[[1.0],[2.0]],targets=[[3.0],[4.0]],features=1),expected='[1]\n[2, 1]\nTrue'),
     dict(values=dict(rows=[[1.0,2.0,3.0]],targets=[[2.0]],features=3),expected='[3]\n[1, 1]\nTrue')],
    [([['shape=(features,)','shape=(len(rows),)']], 'Batch length is not feature count'),
     ([['keras.layers.Dense(1,','keras.layers.Dense(2,']], 'A scalar target needs one output')],
    [([['shape=(features,)','shape=(len(rows[0]),)']], 'Reading the actual row width is equivalent')],
    '입력은 세 특성을 기다리는데 한 배송에는 두 값만 있어 오류가 나요.',
    '입력 모양은 맞았어요. 예측 표의 두 칸도 한 칸으로 줄여야 해요.',
    '세 배송마다 시간 한 값을 예측했고 실제 학습 손실도 유한해요.',
    '조심하세요. 배송 건수를 입력 특성 수로 쓰면 자료의 행 수만 바뀌어도 실행이 깨져요.',
    probe='assert model.input_shape[-1] == features\nassert predictions.shape == (len(rows), 1)', first_error='ValueError', timeout=45)
