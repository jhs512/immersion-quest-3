from _python_final import make

START = '''from sklearn.tree import DecisionTreeRegressor
from sklearn.dummy import DummyRegressor
from sklearn.metrics import mean_squared_error
# 두 후보는 같은 훈련 자료로 배우고 같은 검증 자료로 비교해요.
X_train = [[0], [1], [8], [9]]
y_train = [0, 0, 10, 10]
X_valid = [[0], [9]]
y_valid = [0, 10]
models = {"mean": DummyRegressor(strategy="mean"), "tree": DecisionTreeRegressor(max_depth=1, random_state=0)}
for model in models.values():
    model.fit(X_train, y_train)
truth = y_train[:len(X_valid)]
scores = {name: round(float(mean_squared_error(truth, model.predict(X_valid))), 6) for name, model in models.items()}
winner = max(scores, key=scores.get)
print(scores)
print(winner)
'''
SPEC = make('aice-models', '같은 검증 오차로 두 후보 중 하나를 고르세요',
    '평균 기준 모델과 트리가 같은 검증 배송을 예측해요. 검증 정답 y_valid와 비교한 MSE를 구하고 작은 후보 이름을 출력해요. '
    '현재 mean의 MSE는 25, tree는 0이므로 tree를 골라야 해요.',
    '같은 검증 자료와 오차 방향으로 후보 모델을 비교해요.', START,
    [('truth = y_train[:len(X_valid)]', 'truth = y_valid', '훈련 정답 일부 대신 검증 배송의 정답을 사용하세요.'),
     ('winner = max(scores, key=scores.get)', 'winner = min(scores, key=scores.get)', '오차가 가장 작은 후보를 고르세요.')],
    "{'mean': 25.0, 'tree': 0.0}\ntree",
    [dict(values=dict(y_train=[2,2,8,8],y_valid=[2,8]),expected="{'mean': 9.0, 'tree': 0.0}\ntree"),
     dict(values=dict(y_train=[0,0,10,10],y_valid=[5,5]),expected="{'mean': 0.0, 'tree': 25.0}\nmean")],
    [([['winner = min(scores, key=scores.get)', 'winner = max(scores, key=scores.get)']], 'MSE is smaller-is-better'),
     ([['truth = y_valid', 'truth = y_train[:len(X_valid)]']], 'Evaluation targets must match the validation observations')],
    [([['min(scores, key=scores.get)', 'sorted(scores, key=scores.get)[0]']], 'Sorting by the same held-out error is equivalent')],
    '검증 입력에 훈련 정답 일부를 붙이고 큰 오차를 고르고 있어요.',
    '검증 배송의 정답으로 비교했어요. 작은 오차를 선택해야 해요.',
    '같은 검증 배송에서 오차가 작은 후보를 골랐어요.',
    '조심하세요. 훈련 점수가 좋은 후보를 고르면 새 배송에서의 성능 비교가 빠져요.',
    probe='assert truth == y_valid\nassert scores[winner] == min(scores.values())')
