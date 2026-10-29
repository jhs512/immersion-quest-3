from _python_final import make

START = '''import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
# 번호별 실제 시간과 예측이에요. 저장된 순서가 달라요.
truth = {101: 10, 102: 20, 103: 30}
guesses = {103: 34, 101: 10, 102: 16}
actual = pd.Series(truth)
predicted = pd.Series(guesses)
aligned = predicted
mae = mean_absolute_error(actual, aligned)
rmse = mean_squared_error(actual, aligned)
r2 = r2_score(actual, aligned)
print(round(float(mae), 6))
print(round(float(rmse), 6))
print(round(float(r2), 6))
'''
SPEC = make('aice-regression-metrics', '배송 번호를 맞추고 세 오차를 보고하세요',
    '예측을 actual의 배송 번호 순서로 맞춘 뒤 MAE, RMSE, R²를 출력해요. '
    'RMSE는 MSE의 제곱근이라 시간과 같은 분 단위예요. 지금 결과는 2.666667, 3.265986, 0.84예요.',
    '같은 배송끼리 비교하고 MAE·RMSE·R²의 의미에 맞게 보고해요.', START,
    [('aligned = predicted', 'aligned = predicted.reindex(actual.index)', '실제 값의 배송 번호 순서로 예측을 맞추세요.'),
     ('rmse = mean_squared_error(actual, aligned)', 'rmse = mean_squared_error(actual, aligned) ** 0.5', '분 단위 RMSE가 나오도록 제곱근을 구하세요.')],
    '2.666667\n3.265986\n0.84',
    [dict(values=dict(truth={1:2,2:4,3:6},guesses={3:5,1:1,2:5}),expected='1.0\n1.0\n0.625'),
     dict(values=dict(truth={7:0,8:10},guesses={8:10,7:0}),expected='0.0\n0.0\n1.0')],
    [([['predicted.reindex(actual.index)', 'predicted']], 'Stored order is not observation identity'),
     ([['mean_squared_error(actual, aligned) ** 0.5', 'mean_squared_error(actual, aligned)']], 'MSE has squared units')],
    [([['mean_squared_error(actual, aligned) ** 0.5', 'float(mean_squared_error(actual, aligned)) ** (1/2)']], 'Equivalent square root')],
    '저장 순서가 다른 배송을 비교했고 RMSE 자리에는 제곱 오차가 들어갔어요.',
    '배송 번호는 맞췄어요. RMSE도 원래 시간 단위로 바꿔야 해요.',
    '같은 배송끼리 비교한 세 지표가 각각 출력됐어요.',
    '조심하세요. 두 목록을 값순으로 따로 정렬하면 번호가 같은 배송의 오차를 잃어요.',
    probe='assert aligned.index.equals(actual.index)\nassert abs(rmse * rmse - mean_squared_error(actual, aligned)) < 1e-8',
    baseline_values={'truth': {101:10,102:20,103:30}, 'guesses': {103:34,101:10,102:16}})
