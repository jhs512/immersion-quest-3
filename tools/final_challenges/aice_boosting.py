from _python_final import make

START = '''import numpy as np
from xgboost import XGBRegressor
# 같은 값 두 묶음으로 반영 비율과 반복 횟수만 관찰해요.
X_train = np.array([[0.0], [1.0], [8.0], [9.0]], dtype="float32")
y_train = np.array([2.0, 2.0, 8.0, 8.0], dtype="float32")
rate = 0.5
rounds = 2
X_test = np.array([[0.0], [9.0]], dtype="float32")
model = XGBRegressor(n_estimators=1, learning_rate=1.0, max_depth=1,
    min_child_weight=0, reg_lambda=0, random_state=0, n_jobs=1,
    base_score=0.5, objective="reg:squarederror", verbosity=0)
model.fit(X_train, y_train)
print(model.get_booster().num_boosted_rounds())
print(model.get_params()["learning_rate"])
print(model.predict(X_test).round(6).tolist())
'''
SPEC = make('aice-boosting', '반영 비율과 반복 횟수를 학습에 연결하세요',
    '정해 둔 rounds번만 학습하고 매 반복의 반영 비율은 rate를 따라요. 실제 반복 횟수, 학습률, 두 배송의 예측을 출력해요. '
    '현재 두 번·0.5 비율이면 예측은 1.625와 6.125예요.',
    '학습률과 반복 수를 실제 학습된 부스팅 모델에서 확인해요.', START,
    [('n_estimators=1', 'n_estimators=rounds', '학습 반복 횟수를 rounds에 연결하세요.'),
     ('learning_rate=1.0', 'learning_rate=rate', '학습 반영 비율을 rate에 연결하세요.')],
    '2\n0.5\n[1.625, 6.125]',
    [dict(values=dict(rounds=1,rate=0.5),expected='1\n0.5\n[1.25, 4.25]'),
     dict(values=dict(rounds=2,rate=0.25),expected='2\n0.25\n[1.15625, 3.78125]')],
    [([['n_estimators=rounds','n_estimators=1']], 'The requested number of rounds changes'),
     ([['learning_rate=rate','learning_rate=1.0']], 'Learning rate must not remain at the default')],
    [([['n_estimators=rounds','n_estimators=int(rounds)']], 'Equivalent integer round count')],
    '학습은 한 번, 반영 비율은 1로 고정돼 있어요.',
    '반복 횟수는 맞췄어요. 비율이 1이면 한 번에 각 묶음의 정답까지 반영해요.',
    '두 번에 나눠 정해 둔 비율만큼 반영한 예측이 나왔어요.',
    '조심하세요. 변수 rate만 바꾸고 모델 설정에 연결하지 않으면 학습 결과는 그대로예요.',
    probe='assert model.get_booster().num_boosted_rounds() == rounds\nassert model.get_params()["learning_rate"] == rate')
