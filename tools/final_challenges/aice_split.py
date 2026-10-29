from _python_final import make

START = '''from sklearn.model_selection import train_test_split
# 배송 번호와 지연 여부예요. 두 목록의 같은 자리가 같은 배송이에요.
ids = [101, 102, 103, 104, 105, 106, 107, 108]
labels = [0, 0, 0, 0, 1, 1, 1, 1]
test_count = 4
# 두 목록은 반드시 한 번에 나눠요.
X_train, X_test, y_train, y_test = train_test_split(ids, labels, test_size=2, random_state=4)
# 확인용 출력: 평가 자료의 크기, 지연 건수, 번호와 정답의 원래 대응이에요.
print(len(X_train), len(X_test))
print(sum(y_test))
print(all(labels[ids.index(i)] == y for i, y in zip(X_test, y_test)))
'''
SPEC = make('aice-split', '배송 번호와 정답을 층화해 함께 나누세요',
    '새 배송 자료를 훈련과 평가로 나눠요. 평가 건수는 test_count를 따라요. '
    '지연과 정상의 비율을 지키고 같은 번호와 정답은 함께 움직여야 해요. '
    '지금 자료는 훈련 4건, 평가 4건이고 평가 중 지연은 2건이에요.',
    '평가 크기와 범주 비율을 지키며 입력과 정답의 짝을 보존해요.', START,
    [('test_size=2', 'test_size=test_count', '평가 크기를 test_count로 정하세요.'),
     ('random_state=4)', 'random_state=4, stratify=labels)', '정답 labels의 비율을 지키도록 층화하세요.')],
    '4 4\n2\nTrue',
    [dict(values=dict(ids=list(range(10)), labels=[0]*5+[1]*5, test_count=6), expected='4 6\n3\nTrue'),
     dict(values=dict(ids=list(range(12)), labels=[0]*6+[1]*6, test_count=4), expected='8 4\n2\nTrue'),
     dict(values=dict(ids=list(range(16)), labels=[0]*8+[1]*8, test_count=4), expected='12 4\n2\nTrue')],
    [([['stratify=labels', 'stratify=None']], 'Random splitting alone does not preserve the class proportions'),
     ([['test_size=test_count', 'test_size=4']], 'Requested evaluation size may change')],
    [([['stratify=labels', 'stratify=list(labels)']], 'A copy of labels keeps the same split contract')],
    '평가 크기가 2건이라 요구한 4건과 달라요.',
    '크기는 맞췄어요. 아직 범주별 비율은 고정하지 않았어요.',
    '평가 4건 중 지연 2건이고 번호와 정답의 짝도 그대로예요.',
    '조심하세요. 입력과 정답을 따로 섞으면 같은 위치가 다른 배송을 가리킬 수 있어요.',
    probe='assert len(X_test) == test_count\nassert len(y_test) == test_count\nassert sum(y_test) * len(labels) == sum(labels) * test_count')
