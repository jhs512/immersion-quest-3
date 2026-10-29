from _python_final import make

START = '''from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
# 입력은 거리, 정답은 배송 시간이에요. 평가는 학습에서 빼 두었어요.
X_train = [[0], [1], [2]]
y_train = [1, 3, 5]
X_test = [[3], [4]]
y_test = [7, 9]
baseline = DummyRegressor(strategy="mean").fit(X_train, y_train)
model = DummyRegressor(strategy="mean")
model.fit(X_train, y_train)
predictions = model.predict(X_train[:len(X_test)])
print(predictions.round(6).tolist())
print(round(float(mean_absolute_error(y_test, baseline.predict(X_test))), 6))
print(round(float(mean_absolute_error(y_test, predictions)), 6))
'''
SPEC = make('aice-regression', '남겨둔 배송으로 기준 모델과 회귀를 비교하세요',
    '훈련 자료로 선형 회귀를 학습해요. 평가 배송의 시간을 예측하고 평균 예측 기준 모델과 같은 평가 자료에서 MAE를 비교해요. '
    '지금 자료의 평가 예측은 7분과 9분이고 회귀의 MAE는 0이에요.',
    '훈련에서 배운 회귀를 평가 자료에 적용하고 같은 기준으로 오차를 비교해요.', START,
    [('model = DummyRegressor(strategy="mean")', 'model = LinearRegression()', '학습할 후보를 선형 회귀로 바꾸세요.'),
     ('model.predict(X_train[:len(X_test)])', 'model.predict(X_test)', '남겨둔 평가 입력의 시간을 예측하세요.')],
    '[7.0, 9.0]\n5.0\n0.0',
    [dict(values=dict(X_train=[[1],[2],[3]],y_train=[4,7,10],X_test=[[4],[5]],y_test=[13,16]),expected='[13.0, 16.0]\n7.5\n0.0'),
     dict(values=dict(X_train=[[0],[1],[2]],y_train=[0,5,10],X_test=[[3],[4]],y_test=[14,21]),expected='[15.0, 20.0]\n12.5\n1.0')],
    [([['model.predict(X_test)', 'model.predict(X_train[:len(X_test)])']], 'Evaluation uses held-out inputs'),
     ([['model = LinearRegression()', 'model = DummyRegressor(strategy="mean")']], 'A mean baseline is not a fitted linear relation')],
    [([['model.fit(X_train, y_train)', 'model = model.fit(X_train, y_train)']], 'fit returns the same trained estimator')],
    '후보도 평균 기준 모델이라 거리 변화가 예측에 반영되지 않아요.',
    '직선은 배웠지만 훈련 거리 일부를 예측하고 있어요. 평가 거리로 바꿔야 해요.',
    '같은 평가 배송에서 평균 기준과 회귀의 오차를 비교했어요.',
    '조심하세요. 훈련 자료 예측을 평가 정답과 비교하면 서로 다른 배송을 채점해요.',
    probe='assert len(predictions) == len(X_test)\nassert model.n_features_in_ == 1')
