"""aice-regression: predict a number, score it with MAE/RMSE and beat the mean baseline (AICE Associate 14th lesson).

Every task reads one original delivery log (order_id, distance km, items, rush 0/1, minutes) and
splits it 75/25 with random_state=42. The three logs come from a fixed integer generator, so the
bytes never depend on a library's random numbers:
- BASE (60 rows): minutes grow linearly with distance, items and rush; one very late delivery
  lands in the test part, so RMSE sits far above MAE. The unlimited tree memorizes the training
  rows, a tree on order_id alone loses to the mean baseline, and with random_state=42 the linear
  model narrowly beats the forest in the challenge (most other seeds flip it; the goal says so).
- SHORTER (44 rows): a jump after 5 km and a rush effect that grows with distance; the forest wins.
- LONGER (76 rows): other coefficients and more rows; the linear model wins again.
Different row counts catch arrays sized from the wrong part; different values make memorized
output fail. Fits stay tiny (at most 30 trees on 57 rows) so a grade finishes in seconds.
"""
from certification_course.kit import py_task
from principles_course.common import code, lesson

SOURCES = ['https://aice.study/info/aice/asso',
           'https://aice.study/certi/practice',
           'https://scikit-learn.org/stable/modules/model_evaluation.html#regression-metrics',
           'https://scikit-learn.org/stable/modules/ensemble.html#random-forests']

PATH = 'data/delivery.csv'


def numbers(seed):
    """A fixed linear congruential sequence in [0, 1); the same on every Python."""
    state = seed
    while True:
        state = (state * 1103515245 + 12345) % 2147483648
        yield state / 2147483648


def delivery(seed, rows, first_id, minutes_of):
    """Delivery log: noise within 4 minutes, and about one row in twenty arrives 18 minutes late."""
    draw = numbers(seed)
    lines = ['order_id,distance,items,rush,minutes']
    for i in range(rows):
        distance = round(0.5 + 8.5 * next(draw), 1)
        items = 1 + int(6 * next(draw))
        rush = int(next(draw) < 0.4)
        noise = 8 * next(draw) - 4
        late = 18 if next(draw) < 0.05 else 0
        minutes = round(minutes_of(distance, items, rush) + noise + late)
        lines.append(f'{first_id + i},{distance},{items},{rush},{minutes}')
    return '\n'.join(lines) + '\n'


BASE = delivery(29, 60, 5001, lambda d, i, r: 10 + 3.2 * d + 1.5 * i + 6 * r)
SHORTER = delivery(11, 44, 7101, lambda d, i, r: 14 + 2 * d + (12 if d > 5 else 0) + 2 * i + r * 1.5 * d)
LONGER = delivery(23, 76, 3301, lambda d, i, r: 8 + 4 * d + 1 * i + 9 * r)

XY = '''# 입력 X는 거리·메뉴 수·혼잡 여부, 정답 y는 배달 시간(분)이에요.
X = df[['distance', 'items', 'rush']]
y = df['minutes']
# 훈련 75%, 테스트 25%로 나눠요. random_state로 늘 같게 나눠요.
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
'''

LINEAR = 'from sklearn.linear_model import LinearRegression'
TREE = 'from sklearn.tree import DecisionTreeRegressor'
FOREST = 'from sklearn.ensemble import RandomForestRegressor'
MAE = 'from sklearn.metrics import mean_absolute_error'


def header(tools, *, numpy=False, xy=True):
    """Imports only what the solution uses, the delivery log and (usually) X, y and the split."""
    text = ('# 표 도구 pandas와 숫자 도구 numpy를 불러와요.\nimport pandas as pd\nimport numpy as np\n' if numpy
            else '# 표 도구 pandas를 불러와요.\nimport pandas as pd\n')
    text += '# 자료를 나누는 함수예요.\nfrom sklearn.model_selection import train_test_split\n'
    text += '# 이번 문제에 쓸 도구를 불러와요.\n' + ''.join(line + '\n' for line in tools)
    text += "\n# 직접 만든 배달 기록이에요. 실제 주문이 아니에요.\ndf = pd.read_csv('data/delivery.csv')\n"
    return text + (XY if xy else '')


def orders(id, title, principle, goal, body, before, after, *, tools, numpy=False, xy=True, compare,
           caution, hints, wrong=None, challenge=False, volatile=False):
    """One experiment on the base log plus the shorter and longer logs.

    volatile: the starter's forest has no random_state, so narration must not quote one run's numbers.
    """
    scenarios = [{'files': {PATH: SHORTER}}, {'files': {PATH: LONGER}}]
    return py_task(id, title, principle, goal, header(tools, numpy=numpy, xy=xy) + code(body), before, after,
                   caution=caution, hints=hints, scenarios=scenarios, files={PATH: BASE}, compare=compare,
                   wrong=wrong, challenge=challenge, volatile=volatile)


# The fitted linear model and its test predictions, shared by the scoring tasks.
FIT = '''# 선형회귀를 훈련 자료로 배우고 테스트 행을 예측해요.
model = LinearRegression()
model.fit(X_train, y_train)
pred = model.predict(X_test)
'''

# fit-predict: a mistake on the solution, predicting the training rows after the right fit.
FIT_DONE = '''model.fit(X_train, y_train)
# 배운 대로 테스트 행의 배달 시간을 예측해요.
pred = model.predict(X_test)'''

# Challenge: the forest has no fixed seed and is scored on its own training rows.
PAIR_START = '''forest = RandomForestRegressor(n_estimators=30)
forest.fit(X_train, y_train)
# 두 모델의 MAE를 재요.
linear_mae = mean_absolute_error(y_test, linear.predict(X_test))
forest_mae = mean_absolute_error(y_train, forest.predict(X_train))'''

PAIR_DONE = PAIR_START.replace('n_estimators=30)', 'n_estimators=30, random_state=42)') \
    .replace('mean_absolute_error(y_train, forest.predict(X_train))', 'mean_absolute_error(y_test, forest.predict(X_test))')


def build():
    item = lesson('aice-regression', '숫자를 예측하는 기준과 모델',
        '배달 시간 같은 숫자를 예측하는 회귀 모델을 배우고 채점해요. '
        '평균만 쓰는 기준 모델과도 견줘요. '
        '필수 문제 8개와 선택 도전 1개예요.',
        SOURCES, [
        orders('fit-predict', '모델은 훈련 자료로 배워요',
            '모델(model)은 입력 X와 정답 y의 관계를 배우는 도구예요.\n'
            '`fit(X, y)`로 배우고, `predict(X)`로 정답을 예측해요.\n'
            '선형회귀(LinearRegression)는 입력마다 곱할 수를 배워요. 끝에 더할 수도 하나 배워요.',
            '자, 먼저 실행해서 배운 수들과 앞 5개 예측을 보세요.\n'
            '지금은 채점용으로 남긴 테스트 자료로 배웠어요. 시험지 답을 보고 공부한 셈이죠.\n'
            'fit 괄호 안을 `X_train, y_train`으로 바꾸고 다시 실행해 보세요.\n'
            '배운 수와 예측이 달라졌죠? 출력만 봐선 반칙이 티 나지 않아요. 그래서 처음부터 훈련 자료로만 배워요.',
            '''
            # 선형회귀 모델을 만들어요. 아직 아무것도 안 배웠어요.
            model = LinearRegression()
            # fit으로 입력과 정답의 관계를 배워요.
            model.fit(X_test, y_test)
            # 배운 대로 테스트 행의 배달 시간을 예측해요.
            pred = model.predict(X_test)
            # coef_는 거리, 메뉴 수, 혼잡 여부에 곱할 수예요.
            print(model.coef_.round(2))
            # intercept_는 곱한 값들에 끝으로 더할 수예요.
            print(round(model.intercept_, 2))
            # 앞 5개 예측을 소수 첫째 자리까지 봐요.
            print(pred[:5].round(1))
            ''',
            'model.fit(X_test, y_test)', 'model.fit(X_train, y_train)', tools=[LINEAR], compare=['pred'],
            caution='X_train과 y_test처럼 몫을 섞으면 행 수가 달라 오류가 나요.',
            hints=['`model.fit(X_train, y_train)`으로 바꿔요.'],
            wrong=[('model.fit(X_test, y_test)', 'model.fit(X_train, y_test)'),
                   ('model.fit(X_test, y_test)', 'model.fit(X, y)'),
                   (FIT_DONE, FIT_DONE.replace('model.predict(X_test)', 'model.predict(X_train)'))]),
        orders('side-by-side', '실제 시간과 예측을 나란히 봐요',
            '예측 pred는 행 번호 없이 순서만 있는 배열이에요.\n'
            'y_test는 섞어 나눈 원래 행 번호를 달고 있어요. 배열은 그 옆에 순서대로 붙어요.\n'
            '`pd.Series`로 감싸면 0부터 새 번호가 붙어요. 표는 같은 번호끼리 짝을 지어요.',
            '먼저 실행해서 테스트 행 수와 표의 행 수를 견줘 보세요. 빈칸(NaN)도 보이죠?\n'
            "`'pred': pd.Series(pred)`를 `'pred': pred`로 바꾸세요.\n"
            'y_test의 행 번호는 그대로 두세요. 원래 주문을 찾을 때 써요.\n'
            '다시 실행해서 행 수와 error 열을 보세요. 많이 틀린 행도 찾아봐요.',
            FIT + code('''
            # 테스트 행 수예요. 표도 이만큼이어야 해요.
            print(len(y_test))
            # 실제 시간과 예측을 나란히 놓은 표예요.
            result = pd.DataFrame({'actual': y_test, 'pred': pd.Series(pred)})
            # 오차는 실제에서 예측을 뺀 값이에요.
            result['error'] = result['actual'] - result['pred']
            # 표의 행 수와 표를 봐요. 소수 첫째 자리까지예요.
            # -0.0은 0보다 아주 조금 작은 오차를 반올림한 값이에요.
            print(len(result))
            print(result.round(1))
            '''),
            "'pred': pd.Series(pred)", "'pred': pred", tools=[LINEAR], compare=['result'],
            caution='NaN 행을 dropna로 지우면 엉뚱한 짝이 남아요.',
            hints=["`'pred': pd.Series(pred)`를 `'pred': pred`로 바꿔요."],
            wrong=[("result = pd.DataFrame({'actual': y_test, 'pred': pd.Series(pred)})",
                    "result = pd.DataFrame({'actual': y_test, 'pred': pd.Series(pred)}).dropna()"),
                   ("{'actual': y_test, 'pred': pd.Series(pred)}", "{'actual': y_test.sort_index(), 'pred': pred}"),
                   ("{'actual': y_test, 'pred': pd.Series(pred)}", "{'actual': y_test.values, 'pred': pred}")]),
        orders('mae-test', 'MAE는 테스트 자료로 재요',
            '평균 절대 오차(MAE)는 오차의 크기만 모아 평균 낸 값이에요.\n'
            '`mean_absolute_error(정답, 예측)`이 계산해요. 단위는 y와 같은 분이에요.\n'
            '채점은 테스트 자료로 해요. 훈련 자료는 모델이 이미 본 문제집이에요. 그래서 실력보다 덜 틀려 보여요.',
            '먼저 실행해서 두 숫자를 견줘 보세요. 위는 테스트 오차를 직접 잰 값이에요.\n'
            '아래 mae 줄은 훈련 자료로 채점하고 있어요.\n'
            'mae 줄을 `mae = mean_absolute_error(y_test, pred)`로 바꾸세요.\n'
            '다시 실행해서 두 숫자가 같아졌는지 봐요. 평균 몇 분 틀렸나요?',
            FIT + code('''
            # 테스트 오차의 크기를 직접 평균 내요. abs()는 부호를 떼요.
            manual = (y_test - pred).abs().mean()
            print(round(manual, 2))
            # 같은 일을 하는 함수예요. 정답, 예측 순서로 넣어요.
            mae = mean_absolute_error(y_train, model.predict(X_train))
            print(round(mae, 2))
            '''),
            'mae = mean_absolute_error(y_train, model.predict(X_train))', 'mae = mean_absolute_error(y_test, pred)',
            tools=[LINEAR, MAE], compare=['mae'],
            caution='abs 없이 오차를 평균 내면 +와 -가 지워져 작게 나와요.',
            hints=['`mae = mean_absolute_error(y_test, pred)`로 바꿔요.'],
            wrong=[('mae = mean_absolute_error(y_train, model.predict(X_train))', 'mae = (y_test - pred).mean()'),
                   ('mae = mean_absolute_error(y_train, model.predict(X_train))',
                    'mae = mean_absolute_error(y_test, model.predict(X_train))'),
                   ('mae = mean_absolute_error(y_train, model.predict(X_train))',
                    'mae = mean_absolute_error(y, model.predict(X))')]),
        orders('rmse', 'RMSE는 큰 오차에 더 민감해요',
            '평균 제곱 오차(MSE)는 오차를 제곱해 평균 낸 값이에요. 단위가 분의 제곱이라 읽기 어려워요.\n'
            'RMSE는 MSE의 제곱근이에요. 다시 분 단위가 되고, 큰 오차가 더 크게 들어가요.\n'
            'numpy를 np로 불러오면 `np.sqrt(값)`으로 제곱근을 구해요.',
            '먼저 실행해서 MAE, MSE, RMSE를 견줘 보세요. 지금 RMSE는 MSE 그대로예요.\n'
            'rmse 줄을 `rmse = np.sqrt(mse)`로 바꾸세요.\n'
            '다시 실행해 보세요. RMSE는 늘 MAE와 같거나 커요.\n'
            '둘의 차이가 크면 크게 틀린 행이 섞인 거예요. 앞에서 표로 찾은 많이 틀린 행처럼요.',
            FIT + code('''
            # 평균 절대 오차예요.
            mae = mean_absolute_error(y_test, pred)
            # 오차를 제곱해 평균 낸 MSE예요.
            mse = mean_squared_error(y_test, pred)
            # RMSE는 MSE의 제곱근이어야 해요.
            rmse = mse
            # 세 지표를 소수 둘째 자리까지 봐요.
            print('MAE', round(mae, 2))
            print('MSE', round(mse, 2))
            print('RMSE', round(rmse, 2))
            '''),
            'rmse = mse', 'rmse = np.sqrt(mse)', numpy=True,
            tools=[LINEAR, 'from sklearn.metrics import mean_absolute_error, mean_squared_error'], compare=['rmse'],
            caution='MSE를 그대로 보고하면 분의 제곱이라 크게 부풀어 보여요.',
            hints=['`rmse = np.sqrt(mse)`로 바꿔요.'],
            wrong=[('rmse = mse', 'rmse = np.sqrt(mean_squared_error(y_train, model.predict(X_train)))'),
                   ('rmse = mse', 'rmse = np.sqrt(mae)')]),
        orders('mean-baseline', '평균으로 맞히는 기준 모델',
            '기준 모델(baseline)은 아무것도 안 배우고 내는 예측이에요.\n'
            '훈련 정답의 평균 하나로 모든 테스트 행을 맞혀요. 모델은 이보다 나아야 해요.\n'
            '`np.full(개수, 값)`은 같은 값을 개수만큼 담은 배열을 만들어요.',
            '먼저 실행해서 기준값과 기준 MAE를 보세요.\n'
            '지금 기준값은 테스트 정답의 평균이에요. 예측할 땐 모르는 값이죠?\n'
            '`y_test.mean()`을 `y_train.mean()`으로 바꾸고 다시 실행해 보세요.\n'
            '엿봐도 MAE가 늘 작아지진 않아요. 점수와 상관없이 모르는 값을 쓰면 반칙이에요.',
            '''
            # 기준값이에요. 모든 테스트 행을 이 값 하나로 맞혀요.
            base_value = y_test.mean()
            print(round(base_value, 2))
            # 테스트 행 수만큼 기준값을 채운 예측 배열이에요.
            base = np.full(len(y_test), base_value)
            print(base[:3].round(1))
            # 기준 모델도 MAE로 채점해요.
            base_mae = mean_absolute_error(y_test, base)
            print(round(base_mae, 2))
            ''',
            'base_value = y_test.mean()', 'base_value = y_train.mean()', numpy=True, tools=[MAE],
            compare=['base', 'base_mae'],
            caution='테스트 평균을 쓰면 채점할 답을 미리 엿본 셈이에요.',
            hints=['`base_value = y_train.mean()`으로 바꿔요.'],
            wrong=[('base_value = y_test.mean()', 'base_value = y.mean()'),
                   ('base = np.full(len(y_test), base_value)', 'base = np.full(len(y_train), base_value)')]),
        orders('tree-depth', '결정트리는 깊이를 정해요',
            '결정트리(decision tree)는 질문으로 행을 나눠요. 거리가 4km 이하인지 같은 질문이죠.\n'
            '질문을 다 거쳐 같은 무리에 모인 훈련 행의 정답 평균으로 예측해요. 끝까지 나누면 행을 거의 외워요.\n'
            '`max_depth`는 질문을 몇 단계까지 할지 정해요. 이렇게 학습 전에 정하는 값이 하이퍼파라미터예요.',
            '먼저 실행해서 훈련 MAE와 테스트 MAE를 견줘 보세요. 답만 외운 학생 같죠?\n'
            '`DecisionTreeRegressor(` 괄호 맨 앞에 `max_depth=3, `을 넣으세요.\n'
            '다시 실행해서 두 MAE의 차이가 어떻게 바뀌는지 봐요.\n'
            '테스트 MAE가 조금 더 작아도 괜찮아요. 테스트 행이 적어 운도 섞이거든요.',
            '''
            # 결정트리예요. max_depth를 안 주면 끝까지 나눠요.
            # 똑같이 좋은 질문이 여럿이면 무작위로 골라요. random_state로 고정해요.
            model = DecisionTreeRegressor(random_state=42)
            model.fit(X_train, y_train)
            # 훈련 자료와 테스트 자료로 각각 채점해요.
            train_mae = mean_absolute_error(y_train, model.predict(X_train))
            test_mae = mean_absolute_error(y_test, model.predict(X_test))
            # 두 MAE를 소수 둘째 자리까지 봐요.
            print('훈련 MAE', round(train_mae, 2))
            print('테스트 MAE', round(test_mae, 2))
            ''',
            'DecisionTreeRegressor(random_state=42)', 'DecisionTreeRegressor(max_depth=3, random_state=42)',
            tools=[TREE, MAE], compare=['train_mae', 'test_mae'],
            caution='`DecisionTreeRegressor(3)`처럼 이름 없이 넣으면 TypeError가 나요.',
            hints=['`DecisionTreeRegressor(max_depth=3, random_state=42)`로 바꿔요.'],
            wrong=[('DecisionTreeRegressor(random_state=42)', 'DecisionTreeRegressor(3, random_state=42)'),
                   ('model.fit(X_train, y_train)', 'model.fit(X_train, y_train, max_depth=3)')]),
        orders('forest-seed', '랜덤포레스트는 무작위를 고정해요',
            '랜덤포레스트(random forest)는 결정트리 여러 그루의 예측을 평균 내요.\n'
            '나무마다 훈련 행을 무작위로 뽑아 배워요. 그래서 실행마다 결과가 달라요.\n'
            '`n_estimators`는 나무 수, `random_state`는 무작위를 고정하는 값이에요.',
            '먼저 코드 실행을 두 번 눌러 MAE를 견줘 보세요.\n'
            '`n_estimators=20` 뒤에 `, random_state=42`를 넣으세요.\n'
            '다시 두 번 실행해 보세요. 이제 두 결과가 같아 남의 답과도 견줄 수 있어요.\n'
            '42는 점수를 올리는 값이 아니에요. 여러 결과 중 하나로 고정할 뿐이죠.',
            '''
            # 나무 20그루로 된 랜덤포레스트예요.
            model = RandomForestRegressor(n_estimators=20)
            model.fit(X_train, y_train)
            # 테스트 행을 예측하고 MAE로 채점해요.
            pred = model.predict(X_test)
            mae = mean_absolute_error(y_test, pred)
            # 실행할 때마다 이 값을 견줘요.
            print(round(mae, 2))
            ''',
            'RandomForestRegressor(n_estimators=20)', 'RandomForestRegressor(n_estimators=20, random_state=42)',
            tools=[FOREST, MAE], compare=['pred', 'mae'], volatile=True,
            caution='`random_state`를 fit 괄호에 넣으면 TypeError가 나요.',
            hints=['`RandomForestRegressor(n_estimators=20, random_state=42)`로 바꿔요.'],
            wrong=[('model.fit(X_train, y_train)', 'model.fit(X_train, y_train, random_state=42)'),
                   ('RandomForestRegressor(n_estimators=20)', 'RandomForestRegressor(random_state=42)')]),
        orders('beat-baseline', '모델이 기준보다 나은지 견줘요',
            'MAE 숫자 하나만 봐서는 좋은 모델인지 몰라요.\n'
            '같은 테스트 자료로 잰 기준 MAE와 견줘요. 기준보다 크면 평균만도 못해요.\n'
            '`mae < base_mae`가 True면 모델이 기준보다 덜 틀린 거예요.',
            '먼저 실행해서 두 MAE와 True/False를 보세요. 입력이 주문 번호뿐이에요.\n'
            '주문 번호는 접수 차례로 붙인 이름표라 배달 시간과 상관없어요.\n'
            "X 줄을 `X = df[['distance', 'items', 'rush']]`로 바꾸세요.\n"
            '다시 실행해서 모델이 기준보다 나아졌는지 봐요.',
            '''
            # 입력 X로 쓸 열을 골라요. 정답 y는 배달 시간이에요.
            X = df[['order_id']]
            y = df['minutes']
            # 훈련 75%, 테스트 25%로 나눠요.
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
            # 깊이 3인 결정트리로 배우고 테스트 MAE를 재요.
            model = DecisionTreeRegressor(max_depth=3, random_state=42)
            model.fit(X_train, y_train)
            mae = mean_absolute_error(y_test, model.predict(X_test))
            # 기준 모델의 MAE예요. 훈련 평균으로 모두 맞혀요.
            base_mae = mean_absolute_error(y_test, np.full(len(y_test), y_train.mean()))
            print('모델 MAE', round(mae, 2))
            print('기준 MAE', round(base_mae, 2))
            # 모델이 기준보다 덜 틀렸나요?
            better = mae < base_mae
            print(better)
            ''',
            "X = df[['order_id']]", "X = df[['distance', 'items', 'rush']]", numpy=True, xy=False,
            tools=[TREE, MAE], compare=['mae', 'base_mae', 'better'],
            caution='주문 번호를 X에 남기면 의미 없는 번호로도 행을 나눌 수 있어요.',
            hints=["`X = df[['distance', 'items', 'rush']]`로 바꿔요."],
            wrong=[("X = df[['order_id']]", "X = df.drop(columns=['minutes'])"),
                   ("X = df[['order_id']]", "X = df.drop(columns=['order_id'])")]),
        orders('pick-model', '도전 · 덜 틀리는 모델 고르기',
            '두 모델은 같은 훈련 자료로 배우고 같은 테스트 자료로 채점해요. 그래야 견줄 수 있죠.\n'
            '랜덤포레스트는 random_state를 정해야 결과가 늘 같아요. 이 수업은 늘 42로 정해요.\n'
            '`idxmin()`은 Series에서 가장 작은 값의 이름을 돌려줘요.',
            'MAE가 더 작은 모델의 이름이 best에 담기게 하세요.\n'
            '준비 코드는 두 군데가 틀렸어요. 고칠 곳은 직접 찾아보세요.\n'
            '두 MAE를 어느 자료로 쟀는지, 실행마다 같은지 보세요.\n'
            'MAE 차이가 작으면 random_state만 바꿔도 순위가 뒤집힐 수 있어요.',
            code('''
            # 선형회귀를 훈련 자료로 배워요.
            linear = LinearRegression()
            linear.fit(X_train, y_train)
            # 나무 30그루짜리 랜덤포레스트도 배워요.
            ''') + PAIR_START + '\n' + code('''
            # 이름표를 붙여 Series로 모아요.
            scores = pd.Series({'linear': linear_mae, 'forest': forest_mae})
            print(scores.round(2))
            # MAE가 가장 작은 모델의 이름이에요.
            best = scores.idxmin()
            print(best)
            '''),
            PAIR_START, PAIR_DONE, tools=[LINEAR, FOREST, MAE], compare=['scores', 'best'], challenge=True,
            volatile=True,
            caution='훈련 자료로 채점하면 많이 외운 모델이 유리해 보여요.',
            hints=['하나는 채점에 쓴 자료, 하나는 무작위 고정이에요.',
                   'forest에 `random_state=42`를 넣고, forest_mae는 `y_test`와 `forest.predict(X_test)`로 재요.'],
            wrong=[(PAIR_START, PAIR_START.replace('n_estimators=30)', 'n_estimators=30, random_state=42)')),
                   (PAIR_START, PAIR_START.replace('mean_absolute_error(y_train, forest.predict(X_train))',
                                                   'mean_absolute_error(y_test, forest.predict(X_test))')),
                   (PAIR_START, PAIR_DONE.replace('forest.predict(X_test)', 'forest.predict(X_train)'))]),
    ])
    # These starters train a forest without random_state, so their first run differs every time.
    for t in item['tasks']:
        if t['id'] in ('forest-seed', 'pick-model'):
            t['_volatile'] = True
    return item
