from _python_final import make

START = '''from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeRegressor
X_train = [[0], [1], [2], [3], [8], [9], [10], [11]]
y_train = [0, 0, 0, 0, 10, 10, 10, 10]
depths = [1, 2]
pipeline = Pipeline([("scale", StandardScaler()), ("model", DecisionTreeRegressor(random_state=0))])
search = GridSearchCV(pipeline, {"max_depth": [1]}, cv=2, scoring="neg_mean_squared_error", n_jobs=1, error_score="raise")
search.fit(X_train, y_train)
reported_error = search.best_score_
print(len(search.cv_results_["params"]))
print(search.best_params_["model__max_depth"] in depths)
print(reported_error >= 0)
'''
SPEC = make('aice-tuning', '파이프라인 후보를 연결하고 오차 방향을 맞추세요',
    '파이프라인 model 단계의 깊이를 depths의 모든 값으로 비교해요. 교차검증 점수는 음수 MSE예요. '
    '보고할 오차는 원래 부호로 돌려 양수 또는 0으로 표시해요. 후보 수, 고른 깊이가 후보에 있는지, 오차가 음수가 아닌지를 출력해요.',
    '파이프라인 내부 설정 경로와 음수 오차 점수의 방향을 함께 맞춰요.', START,
    [('"max_depth": [1]', '"model__max_depth": [1]', '단계 이름 model을 붙여 깊이 설정의 경로를 고치세요.'),
     ('"model__max_depth": [1]', '"model__max_depth": depths', 'depths의 모든 후보를 비교하세요.'),
     ('reported_error = search.best_score_', 'reported_error = -search.best_score_', '음수 점수를 원래 MSE의 부호로 돌려 보고하세요.')],
    '2\nTrue\nTrue',
    [dict(values=dict(depths=[1]),expected='1\nTrue\nTrue'),dict(values=dict(depths=[1,2,3]),expected='3\nTrue\nTrue')],
    [([['"model__max_depth": depths','"model__max_depth": [1]']], 'All configured candidates must be compared'),
     ([['reported_error = -search.best_score_','reported_error = search.best_score_']], 'The score is negative MSE, not reportable MSE')],
    [([['-search.best_score_', 'abs(search.best_score_)']], 'The known nonpositive score has the same magnitude')],
    'Pipeline에는 max_depth라는 직접 설정이 없어 오류가 나요.',
    '단계 경로는 맞았지만 후보 하나만 비교하고 오차 부호도 그대로예요.',
    '모든 후보를 비교하고 선택된 음수 점수를 원래 오차 방향으로 돌렸어요.',
    '조심하세요. 음수 MSE에서 가장 작은 수를 고르면 실제 오차가 큰 모델을 고르게 돼요.',
    probe='assert len(search.cv_results_["params"]) == len(depths)\nassert abs(reported_error + search.best_score_) < 1e-8', first_error='ValueError')
