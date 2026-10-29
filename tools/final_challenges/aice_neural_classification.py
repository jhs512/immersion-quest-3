from _python_final import make

START = '''import os
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
import numpy as np
import tensorflow as tf
from tensorflow import keras
tf.config.threading.set_intra_op_parallelism_threads(1)
tf.config.threading.set_inter_op_parallelism_threads(1)
names = ["normal", "early", "late"]
rows = [[1.0], [2.0]]
labels = [0, 2]
biases = [0.0, 0.0, 2.0]
# 고정 가중치로 확률 모양과 이름 연결을 확인해요.
model = keras.Sequential([keras.Input(shape=(1,)), keras.layers.Dense(len(names), activation="sigmoid",
    kernel_initializer="zeros", bias_initializer=keras.initializers.Constant(biases))])
model.compile(optimizer="sgd", loss="categorical_crossentropy")
error = model.evaluate(np.array(rows,dtype="float32"), np.array(labels,dtype="int32"), verbose=0)
probabilities = model(np.array(rows,dtype="float32"), training=False).numpy()
predicted = [names[0] for i in probabilities.argmax(axis=1)]
print(list(probabilities.shape))
print(probabilities.sum(axis=1).round(6).tolist())
print(predicted)
'''
SPEC = make('aice-neural-classification', '정수 정답과 다중 확률을 종류 이름에 연결하세요',
    '정답 labels는 정수 인덱스예요. 알맞은 손실로 평가하고 각 행의 종류 확률 합을 1로 만들어요. '
    '가장 큰 확률의 위치를 names에 연결해 이름을 출력해요. 현재 두 배송의 예측 이름은 모두 late예요.',
    '정수 정답의 손실과 softmax 확률, 종류 이름 연결을 함께 맞춰요.', START,
    [('loss="categorical_crossentropy"','loss="sparse_categorical_crossentropy"','정수 인덱스 정답에 맞는 손실로 바꾸세요.'),
     ('activation="sigmoid"','activation="softmax"','한 배송의 종류 확률 합이 1이 되게 바꾸세요.'),
     ('names[0] for i','names[int(i)] for i','각 예측 위치가 가리키는 실제 종류 이름을 꺼내세요.')],
    "[2, 3]\n[1.0, 1.0]\n['late', 'late']",
    [dict(values=dict(names=['ok','urgent'],rows=[[1.0],[2.0],[3.0]],labels=[0,1,0],biases=[0.0,2.0]),expected="[3, 2]\n[1.0, 1.0, 1.0]\n['urgent', 'urgent', 'urgent']"),
     dict(values=dict(names=['late','ok','early'],rows=[[1.0]],labels=[1],biases=[0.0,2.0,0.0]),expected="[1, 3]\n[1.0]\n['ok']")],
    [([['activation="softmax"','activation="sigmoid"']], 'Independent sigmoid outputs do not sum to one'),
     ([['names[int(i)] for i','names[0] for i']], 'Prediction names must follow predicted indices')],
    [([['names[int(i)] for i','names[i] for i']], 'Numpy integer indices can index a list')],
    '정수 정답에 원핫 정답용 손실을 써서 모양 오류가 나요.',
    '정답 손실은 맞췄어요. 확률 합과 예측 이름도 고쳐야 해요.',
    '각 행의 확률 합이 1이고 가장 큰 위치의 종류 이름이 나왔어요.',
    '조심하세요. argmax의 위치를 종류 이름으로 바꾸지 않으면 화면의 범주를 잘못 해석해요.',
    probe='assert np.allclose(probabilities.sum(axis=1),1)\nassert predicted == [names[int(i)] for i in probabilities.argmax(axis=1)]',first_error='ValueError',timeout=45)
