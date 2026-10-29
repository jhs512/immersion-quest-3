from _python_final import make

START = '''import os
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
import numpy as np
import tensorflow as tf
from tensorflow import keras
tf.config.threading.set_intra_op_parallelism_threads(1)
tf.config.threading.set_inter_op_parallelism_threads(1)
keras.utils.set_random_seed(7)
# 훈련 관계와 다른 검증 정답을 두어 과도한 훈련을 관찰해요.
rows = np.array([[1.0],[2.0]],dtype="float32")
targets = np.array([[2.0],[4.0]],dtype="float32")
wait = 2
rate = 0.1
model = keras.Sequential([keras.Input(shape=(1,)),keras.layers.Dense(1,kernel_initializer="zeros",bias_initializer="zeros")])
model.compile(optimizer=keras.optimizers.SGD(learning_rate=rate),loss="mse")
callback = keras.callbacks.EarlyStopping(monitor="val_loss",mode="min",patience=0,restore_best_weights=False)
history = model.fit(rows,targets,validation_data=(rows,np.zeros_like(targets)),epochs=8,batch_size=2,
    shuffle=False,callbacks=[callback],verbose=0)
print(len(history.history["loss"]))
print(model(rows,training=False).numpy().round(6).tolist())
'''
SPEC = make('aice-training', '정한 횟수만 기다리고 가장 좋던 가중치를 복원하세요',
    '검증 손실이 나빠져도 wait번까지 기다려요. 멈춘 뒤에는 검증이 가장 좋던 가중치를 복원해요. '
    '고정된 작은 실험에서 첫 epoch의 검증 손실이 가장 작아요. 현재 wait=2이면 세 epoch 뒤 첫 가중치의 예측으로 돌아와야 해요.',
    '조기 종료의 기다림과 최적 가중치 복원을 실제 학습으로 확인해요.', START,
    [('patience=0','patience=wait','검증 손실을 기다릴 횟수를 wait에 연결하세요.'),
     ('restore_best_weights=False','restore_best_weights=True','중단 뒤 가장 좋던 검증 가중치를 복원하세요.')],
    '3\n[[1.6], [2.6]]',
    [dict(values=dict(wait=1),expected='2\n[[1.6], [2.6]]'),
     dict(values=dict(wait=2,rate=0.05),expected='3\n[[0.8], [1.3]]')],
    [([['patience=wait','patience=0']], 'The waiting policy is a configurable value'),
     ([['restore_best_weights=True','restore_best_weights=False']], 'Stopping alone does not restore the best weights')],
    [([['patience=wait','patience=int(wait)']], 'Equivalent integer patience')],
    '한 번 나빠지자 바로 멈추고 마지막 가중치를 그대로 쓰고 있어요.',
    '기다릴 횟수는 맞췄어요. 멈춘 뒤 마지막 가중치가 남는 문제도 고쳐야 해요.',
    '정한 횟수만 기다린 뒤 검증이 가장 좋던 첫 가중치의 예측으로 돌아왔어요.',
    '조심하세요. 학습을 중단하는 것과 가장 좋던 가중치를 복원하는 것은 별도 설정이에요.',
    probe='assert len(history.history["loss"]) == wait+1\nassert callback.restore_best_weights is True', timeout=45)
