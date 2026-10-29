from _python_final import make

START = '''import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
# 훈련과 평가는 이미 분리했어요. 한 열에 빈 값이 있어요.
train_rows = [[0.0], [None], [4.0]]
test_rows = [[None], [8.0]]
# 실제 숫자 배열로 바꿔 None을 빈 숫자 NaN으로 통일해요.
train_rows = np.asarray(train_rows, dtype=float)
test_rows = np.asarray(test_rows, dtype=float)
prep = Pipeline([("fill", SimpleImputer(strategy="constant", fill_value=0)), ("scale", StandardScaler())])
prep.fit(train_rows)
result = prep.fit_transform(test_rows)
# 확인용 출력: 학습한 빈칸 기준, 중심, 새 자료 변환 값이에요.
print(prep.named_steps["fill"].statistics_.astype(float).round(6).tolist())
print(prep.named_steps["scale"].mean_.round(6).tolist())
print(result.round(6).tolist())
'''
SPEC = make('aice-scale', '훈련 평균으로 채운 뒤 같은 척도로 바꾸세요',
    '훈련 자료에서 거리 평균을 배워 빈칸을 채우고 표준화해요. 평가 자료는 기준을 다시 배우지 않고 변환만 해요. '
    '현재 훈련 거리의 평균은 2예요. 평가의 빈칸은 중심으로, 8은 중심보다 큰 값으로 바뀌어야 해요.',
    '빈칸 처리와 표준화를 훈련에서 학습하고 평가에는 변환만 적용해요.', START,
    [('SimpleImputer(strategy="constant", fill_value=0)', 'SimpleImputer(strategy="mean")', '훈련 평균으로 빈칸을 채우도록 바꾸세요.'),
     ('result = prep.fit_transform(test_rows)', 'result = prep.transform(test_rows)', '평가 자료에서는 fit 없이 transform만 사용하세요.')],
    '[2.0]\n[2.0]\n[[0.0], [3.674235]]',
    [dict(values=dict(train_rows=[[0.0],[None],[2.0]],test_rows=[[None],[3.0]]),expected='[1.0]\n[1.0]\n[[0.0], [2.44949]]'),
     dict(values=dict(train_rows=[[2.0],[None],[6.0]],test_rows=[[4.0],[None]]),expected='[4.0]\n[4.0]\n[[0.0], [0.0]]'),
     dict(values=dict(train_rows=[[0.0],[None],[2.0],[10.0]],test_rows=[[None],[8.0]]),expected='[4.0]\n[4.0]\n[[0.0], [1.069045]]')],
    [([['prep.transform(test_rows)', 'prep.fit_transform(test_rows)']], 'Evaluation data must not refit the pipeline'),
     ([['SimpleImputer(strategy="mean")', 'SimpleImputer(strategy="median")']], 'The requested statistic is the training mean')],
    [([['prep.fit(train_rows)', 'prep.fit_transform(train_rows)']], 'Training may fit and transform once')],
    '평가에서 다시 학습해 중심이 바뀌었어요. 빈칸 기준도 0으로 고정돼 있어요.',
    '빈칸 기준은 평균으로 바꿨어요. 평가에서 다시 fit하면 여전히 평가 기준이 돼요.',
    '훈련의 빈칸 기준과 중심이 2로 유지되고 새 거리만 변환됐어요.',
    '조심하세요. fit_transform을 평가 자료에 쓰면 훈련 기준을 지운 뒤 새 기준을 배워요.',
    probe='import numpy as np\nassert np.allclose(prep.named_steps["fill"].statistics_.astype(float), np.nanmean(np.asarray(train_rows,dtype=float),axis=0))')
