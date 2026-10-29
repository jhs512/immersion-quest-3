from _python_final import make

START = '''import pandas as pd
# 정답 minutes와 배송이 끝난 뒤에만 아는 actual_end는 예측 시점에 몰라요.
train_rows = {"distance": [2, None, 6], "minutes": [20, 30, 40], "actual_end": [8, 9, 10]}
test_rows = {"distance": [None, 10], "minutes": [50, 60], "actual_end": [11, 12]}
train = pd.DataFrame(train_rows)
test = pd.DataFrame(test_rows)
reference = pd.concat([train, test])["distance"].mean()
X_train = train.copy()
X_test = test.copy()
X_train = X_train.fillna(reference)
X_test = X_test.fillna(reference)
print(round(float(reference), 6))
print(X_train.columns.tolist())
print(X_train["distance"].tolist())
print(X_test["distance"].tolist())
'''
SPEC = make('aice-leakage', '접수 시점의 열과 훈련 기준만 남기세요',
    '접수한 거리로 시간을 예측하려 해요. 거리의 빈칸은 훈련 거리의 평균으로 채워요. '
    '입력에는 distance만 남겨요. 평가 자료와 정답, 배송 완료 뒤 정보가 기준에 섞이면 안 돼요.',
    '예측 시점의 입력 열을 고르고 훈련에서 구한 기준을 평가에도 적용해요.', START,
    [('reference = pd.concat([train, test])["distance"].mean()', 'reference = train["distance"].mean()', '빈칸을 채울 평균은 훈련 자료에서만 구하세요.'),
     ('X_train = train.copy()\nX_test = test.copy()', 'X_train = train[["distance"]].copy()\nX_test = test[["distance"]].copy()', '두 입력 표에서 정답과 미래 정보를 빼고 distance만 남기세요.')],
    "4.0\n['distance']\n[2.0, 4.0, 6.0]\n[4.0, 10.0]",
    [dict(values=dict(train_rows={'distance':[1,None,9],'minutes':[10,20,30],'actual_end':[1,2,3]},test_rows={'distance':[None,100],'minutes':[90,80],'actual_end':[4,5]}),expected="5.0\n['distance']\n[1.0, 5.0, 9.0]\n[5.0, 100.0]")],
    [([['reference = train["distance"].mean()', 'reference = test["distance"].mean()']], 'Evaluation statistics must not define preprocessing'),
     ([['train[["distance"]].copy()', 'train[["distance", "minutes"]].copy()']], 'The target must not become an input')],
    [([['train["distance"].mean()', 'train.distance.mean()']], 'Equivalent access to the training column')],
    '평가의 큰 거리까지 평균에 섞이고 입력에는 정답과 완료 정보도 남았어요.',
    '평균은 훈련 거리만으로 정했어요. 입력 열도 접수 시점에 맞춰야 해요.',
    '입력 열은 distance 하나이고 평가의 빈칸도 훈련 평균으로 채워졌어요.',
    '조심하세요. 정답이나 완료 정보를 입력에 남기면 접수할 때 할 수 없는 예측이 돼요.',
    probe='assert X_train.columns.tolist() == ["distance"]\nassert X_test.columns.tolist() == ["distance"]\nassert reference == train.distance.mean()')
