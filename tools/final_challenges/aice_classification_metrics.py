from _python_final import make

START = '''from sklearn.metrics import precision_score, recall_score, f1_score
# 관심 대상은 late예요. 같은 자리의 실제 종류와 확률이 같은 배송이에요.
actual = ["late", "late", "ok", "ok"]
probabilities = [0.8, 0.5, 0.7, 0.1]
threshold = 0.5
predicted = ["late" if p > threshold else "ok" for p in probabilities]
positive = "ok"
print(round(float(precision_score(actual, predicted, pos_label=positive, zero_division=0)), 6))
print(round(float(recall_score(actual, predicted, pos_label=positive, zero_division=0)), 6))
print(round(float(f1_score(actual, predicted, pos_label=positive, zero_division=0)), 6))
'''
SPEC = make('aice-classification-metrics', '기준 경보의 지연 정밀도와 재현율을 구하세요',
    '확률이 threshold 이상이면 late로 판정해요. 관심 종류 late의 정밀도, 재현율, F1을 차례로 출력해요. '
    '지연으로 예측한 건이 없으면 지표를 0으로 두세요. 현재 결과는 0.666667, 1.0, 0.8이에요.',
    '같은 경보 기준을 적용하고 관심 종류의 정밀도·재현율·F1을 구해요.', START,
    [('p > threshold', 'p >= threshold', '기준과 같은 확률을 포함해 late 경보를 만드세요.'),
     ('positive = "ok"', 'positive = "late"', '관심 종류 late를 기준으로 세 지표를 계산하세요.')],
    '0.666667\n1.0\n0.8',
    [dict(values=dict(actual=['late','late','ok'],probabilities=[0.2,0.3,0.1],threshold=0.5),expected='0.0\n0.0\n0.0'),
     dict(values=dict(actual=['late','ok','ok','ok'],probabilities=[0.6,0.5,0.2,0.1],threshold=0.5),expected='0.5\n1.0\n0.666667')],
    [([['positive = "late"', 'positive = "ok"']], 'Metrics must use the requested positive label'),
     ([['p >= threshold', 'p > threshold']], 'A probability on the threshold is an alarm')],
    [([['p >= threshold', 'not (p < threshold)']], 'Equivalent inclusive threshold')],
    '경계 확률이 빠지고 관심 대상도 정상 ok로 잡혀 있어요.',
    '같은 경보 기준으로 바꿨어요. 지표는 지연 late 기준으로 읽어야 해요.',
    '경보 셋 중 실제 지연은 둘이고 실제 지연 둘을 모두 찾았어요.',
    '조심하세요. pos_label을 바꾸면 같은 예측도 다른 종류의 성능을 보고하게 돼요.')
