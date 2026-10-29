from _python_final import make

START = '''from sklearn.tree import DecisionTreeClassifier
# 거리로 지연 여부를 분류해요. 정답 이름의 정렬 순서는 바뀔 수 있어요.
X_train = [[1], [2], [8], [9]]
labels = ["ok", "ok", "late", "late"]
X_test = [[1], [9]]
threshold = 1.0
model = DecisionTreeClassifier(max_depth=1, random_state=0).fit(X_train, labels)
late_probability = model.predict_proba(X_test)[:, 1]
alarms = [float(p) > threshold for p in late_probability]
print(late_probability.round(6).tolist())
print(alarms)
'''
SPEC = make('aice-classification', '지연 확률의 열을 찾아 기준 이상을 알리세요',
    'classes_에서 late가 있는 열을 찾아 지연 확률을 읽어요. 확률이 threshold 이상인 배송에만 True를 출력해요. '
    '기준과 같은 확률도 경보 대상이에요. 지금 확률은 0과 1이고 경보는 False, True예요.',
    '범주 이름으로 확률 열을 찾고 경계값을 포함해 경보를 정해요.', START,
    [('model.predict_proba(X_test)[:, 1]', 'model.predict_proba(X_test)[:, list(model.classes_).index("late")]', 'classes_에서 late 열의 위치를 찾아 확률을 읽으세요.'),
     ('float(p) > threshold', 'float(p) >= threshold', '기준과 같은 확률도 경보에 포함하세요.')],
    '[0.0, 1.0]\n[False, True]',
    [dict(values=dict(labels=['early','early','late','late'],threshold=1.0),expected='[0.0, 1.0]\n[False, True]'),
     dict(values=dict(X_test=[[1],[8],[9]],threshold=0.0),expected='[0.0, 1.0, 1.0]\n[True, True, True]')],
    [([['list(model.classes_).index("late")', '0']], 'The positive class is not a fixed column'),
     ([['float(p) >= threshold', 'float(p) > threshold']], 'The decision threshold is inclusive')],
    [([['list(model.classes_).index("late")', 'model.classes_.tolist().index("late")']], 'Equivalent lookup by class name')],
    '다른 종류의 확률을 읽고 기준과 같은 값도 경보에서 빠졌어요.',
    '지연 확률 열은 맞아요. 확률이 기준과 같은 배송도 포함해야 해요.',
    '지연 확률이 0인 배송은 False, 기준 1에 닿은 배송은 True예요.',
    '조심하세요. 두 번째 열을 지연이라고 고정하면 범주 이름 순서가 바뀔 때 반대로 읽어요.',
    probe='assert late_probability.tolist() == model.predict_proba(X_test)[:, model.classes_.tolist().index("late")].tolist()')
