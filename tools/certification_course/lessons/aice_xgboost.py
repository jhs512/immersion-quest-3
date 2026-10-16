"""aice-xgboost: XGBoost regression and classification with the sklearn wrapper (AICE Associate 18th lesson).

Every task reads one original synthetic cafe log, data/cafe.csv: temperature, rain, weekend and
promotion days (inputs), cups sold (regression target), a crowd level low/mid/high (three-class
target) and whether the cake sold out (0/1 target). _cafe() writes the rows from a fixed seed with
random.Random, so the bytes never depend on a library's random numbers.

- BASE (120 rows): cups follow temperature (with a jump on hot days), weekend, promotion and their
  pair; rain lowers them. Noise is large, so a depth-8 booster memorizes the training rows.
- RAINY (96 rows): rain dominates; XGBoost and the forest rank the columns differently.
- PROMO (144 rows): promotions and hot days dominate; XGBoost ranks promo first, the forest temp.
Different row counts catch arrays sized from the wrong part; changed relations change scores,
importance order, the GridSearchCV choice and how many rows a 0.7 threshold moves.

Version rules (.scratch/certification-research/aice-libraries.md §4.4 rule 27, issue 24): only the
sklearn wrapper (XGBRegressor/XGBClassifier, n_estimators, max_depth, learning_rate, random_state,
fit/predict/predict_proba/feature_importances_). Regressors always pass objective='reg:squarederror'
(xgboost 0.90 defaults to 'reg:linear' and warns). Defaults differ (0.90: depth 3, rate 0.1; 3.x:
depth 6, rate 0.3), so every model names its settings. 3.x rejects text class labels, 0.90 accepts
them; the LabelEncoder task is written so the solution means the same on both. Scores differ
between versions (0.90 starts from base_score 0.5), so no text quotes a number. Fits stay small
(at most 150 trees on about 100 rows) so a grading run ends in seconds.
"""
import random

from certification_course.kit import py_task
from principles_course.common import code, lesson

SOURCES = ['https://aice.study/board/notice/detail/16322',
           'https://xgboost.readthedocs.io/en/stable/python/python_api.html',
           'https://xgboost.readthedocs.io/en/stable/parameter.html',
           'https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.LabelEncoder.html']

PATH = 'data/cafe.csv'


def _noise(rng, size):
    # Sum of three uniforms: a bell-like noise built only from random(), stable across versions.
    return (rng.random() + rng.random() + rng.random() - 1.5) * size


def _cafe(seed, rows, w):
    """Original cafe days. w holds the effect sizes; level and soldout are cut at given shares."""
    rng = random.Random(seed)
    days = []
    for _ in range(rows):
        temp = rng.randint(-5, 33)
        rain = 1 if rng.random() < 0.3 else 0
        weekend = 1 if rng.random() < 2 / 7 else 0
        promo = 1 if rng.random() < 0.35 else 0
        cups = (w['base'] + w['temp'] * temp + (w['hot'] if temp >= 25 else 0) + w['weekend'] * weekend
                + w['promo'] * promo + w['both'] * weekend * promo - w['rain'] * rain + _noise(rng, w['noise']))
        cups = max(5, round(cups))
        crowd = cups + _noise(rng, 30)
        cake = cups + w['cake_weekend'] * weekend + _noise(rng, 40)
        days.append((temp, rain, weekend, promo, cups, crowd, cake))
    crowds = sorted(d[5] for d in days)
    low, high = crowds[int(rows * w['low'])], crowds[int(rows * (1 - w['high']))]
    cut = sorted(d[6] for d in days)[int(rows * (1 - w['sold']))]
    lines = ['temp,rain,weekend,promo,cups,level,soldout']
    for temp, rain, weekend, promo, cups, crowd, cake in days:
        level = 'low' if crowd < low else ('high' if crowd >= high else 'mid')
        lines.append(f'{temp},{rain},{weekend},{promo},{cups},{level},{int(cake >= cut)}')
    return '\n'.join(lines) + '\n'


BASE = _cafe(3, 120, dict(base=90, temp=2.5, hot=25, weekend=35, promo=20, both=25, rain=30, noise=40,
                          cake_weekend=30, low=0.35, high=0.25, sold=0.35))
RAINY = _cafe(5, 96, dict(base=110, temp=1.2, hot=10, weekend=20, promo=10, both=10, rain=55, noise=36,
                          cake_weekend=10, low=0.3, high=0.3, sold=0.4))
PROMO = _cafe(8, 144, dict(base=70, temp=1.8, hot=35, weekend=15, promo=45, both=30, rain=15, noise=44,
                           cake_weekend=45, low=0.4, high=0.2, sold=0.3))
SCENARIOS = [{'files': {PATH: RAINY}}, {'files': {PATH: PROMO}}]

READ = '''
# 직접 만든 카페 하루 기록이에요. 실제 가게 자료가 아니에요.
df = pd.read_csv('data/cafe.csv')
# temp는 기온이에요. rain, weekend, promo는 비·주말·할인인 날 1이에요.
X = df[['temp', 'rain', 'weekend', 'promo']]
'''

CUPS = '''# 정답 y는 그날 판매한 잔 수예요.
y = df['cups']
# 훈련 75%, 테스트 25%로 나눠요. random_state로 늘 같게 나눠요.
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
'''

STRATIFIED = '''# 종류의 비율이 두 몫에서 같도록 stratify=y로 나눠요.
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y)
'''

PANDAS = 'import pandas as pd'
SPLIT = 'from sklearn.model_selection import train_test_split'
MAE = 'from sklearn.metrics import mean_absolute_error'
FOREST = 'from sklearn.ensemble import RandomForestRegressor'
REGRESSOR = 'from xgboost import XGBRegressor'
CLASSIFIER = 'from xgboost import XGBClassifier'

# A wrong entry ('fixed', old, new) is a mistake made after the intended edit: old -> new in the solution.
FIXED = 'fixed'


def cafe(id, title, principle, goal, imports, setup, body, before, after, *, compare, caution, hints, wrong,
         challenge=False):
    """One experiment on the base cafe log, graded on the rainy and promotion logs too."""
    head = '# 이번 문제에 쓰는 도구를 불러와요.\n' + '\n'.join(imports) + '\n' + READ + setup
    starter = head + '\n' + code(body)
    solution = code(starter).replace(before, after, 1)
    edits = []
    for item in wrong:
        if item[0] == FIXED:
            _, old, new = item
            assert solution.count(old) == 1, (id, old)
            edits.append((solution, solution.replace(old, new, 1)))
        else:
            edits.append(item)
    return py_task(id, title, principle, goal, starter, before, after, caution=caution, hints=hints,
                   scenarios=SCENARIOS, files={PATH: BASE}, compare=compare, wrong=edits, challenge=challenge)


# Challenge: the grid searches on all rows, and the base model leaves the rate to the version default.
GRID_START = '''base = XGBRegressor(objective='reg:squarederror', random_state=42)
# 후보마다 3몫 교차검증을 해요.
grid = GridSearchCV(base, param_grid, cv=3)
grid.fit(X, y)'''

GRID_DONE = '''base = XGBRegressor(objective='reg:squarederror', learning_rate=0.1, random_state=42)
# 후보마다 3몫 교차검증을 해요.
grid = GridSearchCV(base, param_grid, cv=3)
grid.fit(X_train, y_train)'''

RESPLIT = 'X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=7)\n'


def build():
    return lesson('aice-xgboost', 'XGBoost로 회귀·분류하기',
        'XGBoost의 회귀·분류 모델을 sklearn 모델처럼 써 봐요. '
        '기본값이 버전마다 달라서 설정을 직접 적어요. '
        '다른 모델과는 같은 잣대로 견줘요. '
        '필수 문제 8개와 선택 도전 1개예요.',
        SOURCES, [
        cafe('first-xgb', 'XGBoost도 fit과 predict로 써요',
            'XGBoost는 나무를 하나씩 더하며 배워요. 새 나무는 앞 나무들이 틀린 만큼을 고쳐요.\n'
            '이런 방식을 부스팅(boosting)이라고 해요. 회귀 모델 이름은 `XGBRegressor`예요.\n'
            'sklearn 모델처럼 `fit`으로 배우고 `predict`로 예측해요. 괄호 속 설정은 뒤 문제에서 봐요.',
            '자, 먼저 실행해서 랜덤포레스트의 예측과 테스트 MAE를 보세요.\n'
            '`model = forest`를 `model = xgb`로 바꾸세요. fit과 predict 줄은 그대로 둬요.\n'
            '다시 실행해서 예측과 MAE가 어떻게 바뀌었는지 봐요.\n'
            '어느 모델이 나은지는 자료마다 달라요.',
            [PANDAS, SPLIT, MAE, FOREST, REGRESSOR], CUPS,
            '''
            # 앞 수업의 랜덤포레스트예요. 아직 fit 전이에요.
            forest = RandomForestRegressor(n_estimators=50, random_state=42)
            # XGBoost 회귀 모델이에요. 설정을 모두 적어 둬요.
            xgb = XGBRegressor(objective='reg:squarederror', n_estimators=50,
                               max_depth=3, learning_rate=0.1, random_state=42)
            # 이번에 쓸 모델을 골라요.
            model = forest
            # 아래 줄은 어느 모델이든 똑같아요.
            model.fit(X_train, y_train)
            pred = model.predict(X_test)
            # 앞 5개 예측과 테스트 MAE를 봐요.
            print(pred[:5].round(1))
            mae = mean_absolute_error(y_test, pred)
            print('테스트 MAE', round(mae, 2))
            ''',
            'model = forest', 'model = xgb', compare=['pred', 'mae'],
            caution="`model = 'xgb'`처럼 따옴표를 붙이면 모델이 아닌 글자가 돼요.",
            hints=['`model = xgb`로 바꿔요.'],
            wrong=[('model = forest', "model = 'xgb'"),
                   # A fresh model with the version's defaults instead of the prepared settings.
                   ('model = forest', 'model = XGBRegressor()')]),
        cafe('objective-name', '회귀는 objective를 적어요',
            '`objective`는 모델이 무엇을 줄이며 배울지 정해요. 회귀는 `reg:squarederror`를 써요.\n'
            '오차를 제곱해 줄인다는 뜻이에요. `reg:linear`는 같은 계산의 옛 이름이라 경고가 나와요.\n'
            '시험 환경의 0.90은 objective를 안 적으면 이 옛 이름을 써요. 그래서 회귀는 늘 적어요.',
            '먼저 실행해서 결과 옆에 뜬 경고(WARNING)를 읽으세요. 무엇 대신 무엇을 쓰래요?\n'
            "`objective = 'reg:linear'`를 `objective = 'reg:squarederror'`로 바꾸세요.\n"
            '다시 실행해서 경고가 사라졌는지 보세요. 예측과 MAE는 그대로예요.',
            [PANDAS, SPLIT, MAE, REGRESSOR], CUPS,
            '''
            # 무엇을 줄이며 배울지 정하는 이름이에요. 옛 글에서 옮겨 왔어요.
            objective = 'reg:linear'
            # objective= 자리에 위의 이름을 넣어요.
            model = XGBRegressor(objective=objective, n_estimators=50,
                                 max_depth=3, learning_rate=0.1, random_state=42)
            # 훈련 자료로 배우고 테스트 행을 예측해요.
            model.fit(X_train, y_train)
            pred = model.predict(X_test)
            # 모델이 쓰는 objective와 예측, MAE를 봐요.
            print('objective:', model.objective)
            print(pred[:5].round(1))
            print('테스트 MAE', round(mean_absolute_error(y_test, pred), 2))
            ''',
            "objective = 'reg:linear'", "objective = 'reg:squarederror'", compare=['objective', 'pred'],
            caution="`'squarederror'`처럼 `reg:`를 빼면 모르는 이름이라 오류가 나요.",
            hints=["`objective = 'reg:squarederror'`로 바꿔요."],
            wrong=[("objective = 'reg:linear'", "objective = 'squarederror'"),
                   ("objective = 'reg:linear'", "objective = 'reg:absoluteerror'"),
                   # Deleting the setting hides the warning here, but 0.90 falls back to reg:linear.
                   ('XGBRegressor(objective=objective, n_estimators=50,', 'XGBRegressor(n_estimators=50,')]),
        cafe('trees-and-rate', '나무 수와 학습률은 함께 봐요',
            '`n_estimators`는 나무 수예요. `learning_rate`(학습률)는 새 나무가 남은 오차를 얼마나 고칠지 정해요.\n'
            '학습률이 작으면 조금씩 고쳐요. 그래서 나무가 더 많이 필요해요.\n'
            '학습률이 크면 적은 나무로도 훈련 MAE가 빨리 줄어요.',
            '먼저 실행해서 나무 수가 늘 때 두 MAE가 어떻게 바뀌는지 보세요.\n'
            '`rate = 0.05`를 `rate = 0.3`으로 바꾸세요.\n'
            '다시 실행해서 같은 나무 수끼리 견줘 보세요. 어느 쪽이 빨리 줄어드나요?\n'
            '테스트 MAE도 훈련 MAE만큼 줄어드는지 함께 봐요.',
            [PANDAS, SPLIT, MAE, REGRESSOR], CUPS,
            '''
            # 학습률이에요. 새 나무가 남은 오차를 얼마나 고칠지 정해요.
            rate = 0.05


            def maes(n):
                # 나무 n그루와 위의 학습률로 배워요.
                model = XGBRegressor(objective='reg:squarederror', n_estimators=n,
                                     max_depth=3, learning_rate=rate, random_state=42)
                model.fit(X_train, y_train)
                # 훈련 MAE와 테스트 MAE를 함께 돌려줘요.
                train_mae = mean_absolute_error(y_train, model.predict(X_train))
                test_mae = mean_absolute_error(y_test, model.predict(X_test))
                return [train_mae, test_mae]


            # 나무 수마다 두 MAE를 한 행씩 표로 모아요. 행 이름이 나무 수예요.
            table = pd.DataFrame([maes(5), maes(20), maes(80)],
                                 index=[5, 20, 80], columns=['train', 'test'])
            print(table.round(1))
            ''',
            'rate = 0.05', 'rate = 0.3', compare=['table'],
            caution='학습률을 fit 괄호에 넣으면 TypeError가 나요.',
            hints=['`rate = 0.3`으로 바꿔요.'],
            wrong=[('    model.fit(X_train, y_train)', '    model.fit(X_train, y_train, learning_rate=rate)'),
                   ('rate = 0.05', 'rate = 0.03')]),
        cafe('depth-overfit', '깊이를 적고 과적합을 봐요',
            '`max_depth`는 나무 하나가 질문을 몇 단계까지 할지 정해요.\n'
            '깊으면 훈련 행을 외우듯 맞혀요. 훈련 MAE만 작아지는 과적합이 생겨요.\n'
            '기본 깊이는 버전마다 달라요. 시험 환경의 0.90은 3, 새 버전은 6이에요. 그래서 늘 적어요.',
            '먼저 실행해서 훈련 MAE와 테스트 MAE의 차이를 보세요.\n'
            '`max_depth=8`을 `max_depth=2`로 바꾸세요.\n'
            '다시 실행해서 차이가 어떻게 바뀌는지 봐요.\n'
            '테스트 MAE가 늘 줄진 않아요. 깊이는 검증 자료로 골라요.',
            [PANDAS, SPLIT, MAE, REGRESSOR], CUPS,
            '''
            # 깊이 8인 나무 100그루로 배워요.
            model = XGBRegressor(objective='reg:squarederror', n_estimators=100,
                                 max_depth=8, learning_rate=0.3, random_state=42)
            model.fit(X_train, y_train)
            # 같은 모델을 훈련 자료와 테스트 자료로 각각 채점해요.
            train_mae = mean_absolute_error(y_train, model.predict(X_train))
            test_mae = mean_absolute_error(y_test, model.predict(X_test))
            print('훈련 MAE', round(train_mae, 2))
            print('테스트 MAE', round(test_mae, 2))
            # 차이가 크면 과적합을 의심해요.
            print('차이', round(test_mae - train_mae, 2))
            ''',
            'max_depth=8', 'max_depth=2', compare=['train_mae', 'test_mae'],
            caution='훈련 MAE만 보고 깊이를 고르면 가장 깊은 나무가 뽑혀요.',
            hints=['`max_depth=2`로 바꿔요.'],
            wrong=[('model.fit(X_train, y_train)', 'model.fit(X_train, y_train, max_depth=2)'),
                   ('n_estimators=100', 'n_estimators=2')]),
        cafe('classifier-labels', '분류 정답은 0부터 번호로',
            '`XGBClassifier`는 XGBoost의 분류 모델이에요. 쓰는 법은 회귀와 같아요.\n'
            '새 버전은 정답이 0부터 세는 번호여야 해요. 글자 정답은 오류가 나요.\n'
            '그래서 `LabelEncoder`로 정답을 0, 1, 2로 바꿔요. 번호는 abc 순서로 붙어요.',
            '자, 먼저 실행해서 오류의 마지막 줄을 읽으세요. 무엇을 기대했대요?\n'
            "`y = df['level']`을 `y = le.fit_transform(df['level'])`로 바꾸세요.\n"
            '다시 실행해서 예측 번호와 정확도를 보세요.\n'
            '번호가 어느 등급인지 `classes_`와 견줘 봐요.',
            [PANDAS, SPLIT, 'from sklearn.metrics import accuracy_score',
             'from sklearn.preprocessing import LabelEncoder', CLASSIFIER],
            '''# 라벨 인코더를 하나 만들어 le에 담아요.
le = LabelEncoder()
# 정답 y는 그날 붐빈 정도(low, mid, high)예요.
y = df['level']
''' + STRATIFIED,
            '''
            # 분류 모델도 설정을 모두 적어요.
            model = XGBClassifier(n_estimators=50, max_depth=3, learning_rate=0.1, random_state=42)
            model.fit(X_train, y_train)
            # 앞 5개 예측과 정확도를 봐요.
            pred = model.predict(X_test)
            print(pred[:5])
            print('정확도', round(accuracy_score(y_test, pred), 3))
            # 인코더가 배운 종류예요. 이 순서대로 0, 1, 2예요.
            print(le.classes_)
            ''',
            "y = df['level']", "y = le.fit_transform(df['level'])", compare=['pred'],
            caution='low가 0일 거라 짐작하면 틀려요. 번호는 abc 순서예요.',
            hints=["`y = le.fit_transform(df['level'])`로 바꿔요."],
            wrong=[("y = df['level']", "y = df['level'].map({'low': 1, 'mid': 2, 'high': 3})"),
                   ("y = df['level']", "y = le.fit(df['level'])")]),
        cafe('proba-half', 'predict는 확률 0.5로 답해요',
            '`predict_proba`는 행마다 [0일 확률, 1일 확률]을 줘요. XGBoost도 같아요.\n'
            '`predict`는 1일 확률이 0.5보다 크면 1이라고 답해요.\n'
            '기준을 옮기고 싶으면 확률에서 직접 정하면 돼요.',
            '먼저 실행해서 확률 세 줄과 predict와 다른 행 수를 보세요.\n'
            '`threshold = 0.7`을 `threshold = 0.5`로 바꾸세요.\n'
            '다시 실행해서 다른 행 수를 보세요. 0이면 predict도 0.5를 쓰는 거예요.',
            [PANDAS, SPLIT, CLASSIFIER],
            '''# 정답 y는 케이크 품절 여부예요. 품절이면 1이에요.
y = df['soldout']
''' + STRATIFIED,
            '''
            # 품절 여부를 맞히는 분류 모델을 배워요.
            model = XGBClassifier(n_estimators=50, max_depth=3, learning_rate=0.1, random_state=42)
            model.fit(X_train, y_train)
            # 행마다 [0일 확률, 1일 확률]이에요. 앞의 세 행을 봐요.
            proba = model.predict_proba(X_test)
            print(proba[:3].round(2))
            # 1일 확률, 곧 품절 확률만 꺼내요.
            p1 = proba[:, 1]
            # 기준값이에요. 품절 확률이 이보다 크면 1로 답해요.
            threshold = 0.7
            mine = (p1 > threshold).astype(int)
            # predict의 답과 견줘서 다른 행을 세요.
            pred = model.predict(X_test)
            diff = (mine != pred).sum()
            print('predict와 다른 행 수:', diff)
            ''',
            'threshold = 0.7', 'threshold = 0.5', compare=['mine', 'diff'],
            caution='`threshold = 50`처럼 퍼센트로 쓰면 모든 행이 0이 돼요.',
            hints=['`threshold = 0.5`로 바꿔요.'],
            wrong=[('threshold = 0.7', 'threshold = 50'),
                   (FIXED, 'p1 = proba[:, 1]', 'p1 = proba[:, 0]')]),
        cafe('importance-names', '중요도에 열 이름을 붙여요',
            '`feature_importances_`는 열마다 쓰인 정도예요. XGBoost 모델에도 있어요.\n'
            '이 값은 이름 없는 숫자 배열이에요. Series로 만들 때 `index=X_train.columns`로 이름을 붙여요.\n'
            '두 Series를 표로 모으면 같은 이름끼리 한 행에 놓여요.',
            '먼저 실행해서 표의 행 수와 빈칸(NaN)을 보세요. xgb 쪽엔 0부터 번호가 붙었죠?\n'
            '`xgb_imp` 줄의 닫는 괄호 앞에 `, index=X_train.columns`를 넣으세요.\n'
            '다시 실행해서 두 모델의 중요도 순서와 크기를 견줘 보세요.',
            [PANDAS, SPLIT, FOREST, REGRESSOR], CUPS,
            '''
            # 두 모델을 같은 훈련 자료로 배워요.
            forest = RandomForestRegressor(n_estimators=50, random_state=42)
            forest.fit(X_train, y_train)
            xgb = XGBRegressor(objective='reg:squarederror', n_estimators=50,
                               max_depth=3, learning_rate=0.1, random_state=42)
            xgb.fit(X_train, y_train)
            # 중요도 숫자를 Series로 만들어요.
            forest_imp = pd.Series(forest.feature_importances_, index=X_train.columns)
            xgb_imp = pd.Series(xgb.feature_importances_)
            # 두 Series를 열로 놓아요. 같은 이름끼리 한 행에 모여요.
            imp = pd.DataFrame({'forest': forest_imp, 'xgb': xgb_imp})
            # XGBoost 중요도가 큰 순서로 정렬해요.
            imp = imp.sort_values('xgb', ascending=False)
            print(imp.round(3))
            ''',
            'xgb_imp = pd.Series(xgb.feature_importances_)',
            'xgb_imp = pd.Series(xgb.feature_importances_, index=X_train.columns)', compare=['imp'],
            caution='`index=df.columns`를 쓰면 정답 열까지 들어가 길이가 안 맞아요.',
            hints=['`xgb_imp = pd.Series(xgb.feature_importances_, index=X_train.columns)`로 바꿔요.'],
            wrong=[('xgb_imp = pd.Series(xgb.feature_importances_)',
                    'xgb_imp = pd.Series(xgb.feature_importances_, index=df.columns)'),
                   ('xgb_imp = pd.Series(xgb.feature_importances_)',
                    'xgb_imp = pd.Series(sorted(xgb.feature_importances_, reverse=True), index=X_train.columns)')]),
        cafe('same-split', '같은 몫으로 배우고 채점해요',
            '두 모델은 같은 훈련 자료로 배우고 같은 테스트 자료로 채점해야 견줄 수 있어요.\n'
            '테스트 행이 다르면 문제가 달라져요. 쉬운 모의고사를 푼 쪽이 이겨 보이죠.\n'
            '나누기는 맨 위에서 한 번만 해요. 모든 모델이 그 몫을 써요.',
            '먼저 실행해서 두 MAE와 더 나은 모델을 보세요.\n'
            'XGBoost 쪽에서 `train_test_split`을 한 번 더 불러요. random_state도 달라요.\n'
            '그 줄을 지우고 다시 실행해서 두 MAE와 더 나은 모델을 견줘 보세요.',
            [PANDAS, SPLIT, MAE, FOREST, REGRESSOR], CUPS,
            code('''
            # 랜덤포레스트를 배우고 테스트 MAE를 재요.
            forest = RandomForestRegressor(n_estimators=50, random_state=42)
            forest.fit(X_train, y_train)
            forest_mae = mean_absolute_error(y_test, forest.predict(X_test))

            # XGBoost 차례예요. 두 모델이 같은 몫을 써야 공정해요.
            ''') + RESPLIT + code('''
            # XGBoost를 배우고 테스트 MAE를 재요.
            xgb = XGBRegressor(objective='reg:squarederror', n_estimators=50,
                               max_depth=3, learning_rate=0.1, random_state=42)
            xgb.fit(X_train, y_train)
            xgb_mae = mean_absolute_error(y_test, xgb.predict(X_test))

            # 이름표를 붙여 두 MAE를 모아요.
            scores = pd.Series({'forest': forest_mae, 'xgb': xgb_mae})
            print(scores.round(2))
            # MAE가 더 작은 모델의 이름이에요.
            best = scores.idxmin()
            print('더 나은 모델:', best)
            '''),
            RESPLIT, '', compare=['scores', 'best'],
            caution='모델마다 다시 나누면 테스트 행이 바뀌어 비교가 흔들려요.',
            hints=['XGBoost 쪽의 `train_test_split` 줄을 지워요.'],
            wrong=[('random_state=7)', 'random_state=0)'),
                   (FIXED, 'xgb_mae = mean_absolute_error(y_test, xgb.predict(X_test))',
                    'xgb_mae = mean_absolute_error(y_train, xgb.predict(X_train))')]),
        cafe('grid-xgb', '도전 · 깊이와 나무 수를 교차검증으로',
            '`GridSearchCV`는 XGBoost 모델에도 그대로 써요. 후보는 `param_grid`에 적어요.\n'
            '후보에 없는 설정은 기본 모델에 직접 적어요. 안 적으면 버전마다 다른 기본값이 쓰여요.\n'
            '고르기는 훈련 자료로만 하고, 고른 모델은 테스트 자료로 한 번 채점해요.',
            '깊이와 나무 수를 3몫 교차검증으로 고르고 테스트 MAE를 재게 하세요.\n'
            '학습률은 0.1로 정해요. 준비 코드는 두 군데가 틀렸어요.\n'
            '기본 모델의 괄호와 fit에 넣은 자료를 살펴봐요.',
            [PANDAS, 'from sklearn.model_selection import train_test_split, GridSearchCV', MAE, REGRESSOR],
            CUPS,
            code('''
            # 깊이와 나무 수 후보예요.
            param_grid = {'max_depth': [2, 4], 'n_estimators': [50, 150]}
            # 후보 말고 나머지 설정은 기본 모델에 적어요.
            ''') + GRID_START + '\n' + code('''
            print('고른 설정:', grid.best_params_)
            # 고른 모델을 테스트 자료로 한 번 채점해요.
            test_mae = mean_absolute_error(y_test, grid.best_estimator_.predict(X_test))
            print('테스트 MAE', round(test_mae, 2))
            '''),
            GRID_START, GRID_DONE, compare=['test_mae'], challenge=True,
            caution='`grid.fit`에 X, y 전체를 넣으면 테스트 행이 고르기에 섞여요.',
            hints=['학습률을 기본 모델에 적고, 찾기는 훈련 자료로만 해요.',
                   "`XGBRegressor(objective='reg:squarederror', learning_rate=0.1, random_state=42)`로 바꾸고 "
                   '`grid.fit(X_train, y_train)`으로 고쳐요.'],
            wrong=[(GRID_START, GRID_START.replace('grid.fit(X, y)', 'grid.fit(X_train, y_train)')),
                   (GRID_START, GRID_DONE.replace('grid.fit(X_train, y_train)', 'grid.fit(X, y)'))]),
    ])
