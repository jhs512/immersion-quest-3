from _python_final import make

START = '''import os
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
import numpy as np
import tensorflow as tf
from tensorflow import keras
tf.config.threading.set_intra_op_parallelism_threads(1)
tf.config.threading.set_inter_op_parallelism_threads(1)
rows = [[1.0], [4.0]]
targets = [[0.0], [3.0]]
weight = 2.0
bias = -5.0
# 고정 가중치의 동작 비교예요. 이 실험은 학습 성능을 증명하지 않아요.
model = keras.Sequential([keras.Input(shape=(1,)), keras.layers.Dense(1, activation="linear",
    kernel_initializer=keras.initializers.Constant(weight), bias_initializer=keras.initializers.Constant(bias))])
model.compile(optimizer="sgd", loss="binary_crossentropy")
predictions = model(np.array(rows, dtype="float32"), training=False).numpy()
error = model.evaluate(np.array(rows, dtype="float32"), np.array(targets, dtype="float32"), verbose=0)
print(predictions.round(6).tolist())
print(model.loss)
print(round(float(error), 6))
'''
SPEC = make('aice-neural-regression', '음수가 없는 시간 예측과 회귀 오차를 맞추세요',
    '시간은 음수가 될 수 없어요. 음수 출력을 0으로 막는 출력 활성화를 고르고 오차는 mse로 평가해요. '
    '고정 가중치는 동작 비교용이에요. 현재 예측은 0분과 3분이고 MSE는 0이에요.',
    '수치 목표의 범위에 맞는 출력과 회귀 손실을 함께 선택해요.', START,
    [('activation="linear"','activation="relu"','시간이 음수가 되지 않도록 출력 활성화를 고치세요.'),
     ('loss="binary_crossentropy"','loss="mse"','회귀의 평균 제곱 오차로 평가하세요.')],
    '[[0.0], [3.0]]\nmse\n0.0',
    [dict(values=dict(rows=[[1.0],[5.0]],targets=[[0.0],[5.0]]),expected='[[0.0], [5.0]]\nmse\n0.0'),
     dict(values=dict(rows=[[1.0],[4.0]],targets=[[1.0],[5.0]]),expected='[[0.0], [3.0]]\nmse\n2.5')],
    [([['activation="relu"','activation="linear"']], 'Negative times must be clipped'),
     ([['loss="mse"','loss="mae"']], 'The specified loss is squared, not absolute error')],
    [([['activation="relu"','activation=keras.activations.relu']], 'The activation callable is equivalent')],
    '음수 시간이 나오고 평가 손실도 이진 분류용으로 잡혀 있어요.',
    '음수는 0이 됐어요. 시간 오차를 세는 회귀 손실도 맞춰야 해요.',
    '목표 범위에 맞는 출력과 MSE를 같은 배송에서 확인했어요.',
    '조심하세요. sigmoid로 시간을 막으면 1분보다 큰 목표도 0과 1 사이로 눌려요.',
    probe='assert np.all(predictions >= 0)\nassert abs(float(error)-float(np.mean((predictions-np.array(targets))**2))) < 1e-5', timeout=45)
