"""aice-model-improvement: spot overfitting, choose settings by validation, test once (AICE Associate 16th lesson).

Every task reads one original synthetic bakery log, data/bakery.csv: dough weight, proofing-room
humidity, oven temperature and baking minutes (columns in process order), with a 0/1 defect target
and about 12% flipped labels, so an unlimited decision tree memorizes noise. _batches() writes the
rows from a fixed seed; random.randint and random.random give the same text on every Python version.

- Base (120 rows): defects follow temperature and minutes. A depth-3 tree beats the unlimited tree
  on the test part; on the validation part depth 3 wins while depth 8 drops; the test part alone
  would pick depth 6, so choosing by test changes the chosen depth and inflates the score. The
  importance order differs from the column order, so an unsorted importance series fails.
- Changed tables: 96 rows where humidity and minutes drive defects, and 140 rows where weight and
  temperature do. Importance order and the weakest column (base weight, then temp, then humidity)
  change with them, so memorized orders, names or scores fail.
Models, splits and GridSearchCV use random_state=42 or deterministic 3-fold splits, so the
reference answer is stable; candidates stay few so a grading run ends in seconds.
"""
import random

from certification_course.kit import py_task
from certification_course.kit_plots import plot_task
from principles_course.common import code, lesson

SOURCES = ['https://aice.study/info/aice/asso',
           'https://scikit-learn.org/stable/modules/cross_validation.html',
           'https://scikit-learn.org/stable/modules/grid_search.html',
           'https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html']

PATH = 'data/bakery.csv'


def _batches(kind, n, seed, flip=0.12):
    """Original bakery batches. kind picks the columns that drive defects; flip adds label noise."""
    rng = random.Random(seed)
    lines = ['weight,humidity,temp,minutes,defect']
    for _ in range(n):
        temp = rng.randint(170, 230)
        minutes = rng.randint(15, 35)
        humidity = rng.randint(40, 85)
        weight = rng.randint(450, 550)
        if kind == 'base':
            bad = abs(temp - 200) > 22 or minutes > 32 or (humidity > 80 and rng.random() < 0.5)
        elif kind == 'humid':
            bad = humidity > 75 or minutes < 18 or (weight < 465 and rng.random() < 0.5)
        else:
            bad = weight < 470 or temp > 220 or (minutes > 33 and rng.random() < 0.5)
        if rng.random() < flip:
            bad = not bad
        lines.append(f'{weight},{humidity},{temp},{minutes},{int(bad)}')
    return '\n'.join(lines) + '\n'


# Seeds chosen so the base table shows each effect described in the docstring.
BASE = _batches('base', 120, 2)
HUMID = _batches('humid', 96, 4)
LIGHT = _batches('light', 140, 1)
SCENARIOS = [{'files': {PATH: HUMID}}, {'files': {PATH: LIGHT}}]

READ = '''
# 직접 만든 빵 공장 기록이에요. 실제 공장 자료가 아니에요.
df = pd.read_csv('data/bakery.csv')
# weight는 반죽 무게, humidity는 습도, temp는 오븐 온도예요.
# minutes는 굽는 시간이에요. defect가 1이면 불량 빵이에요.
X = df.drop(columns=['defect'])
y = df['defect']
# 테스트 몫 25%는 마지막 확인용으로 남겨 둬요.
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y)
'''

VALID = '''
# 훈련 자료를 한 번 더 나눠 검증 몫(30%)을 만들어요.
X_tr, X_val, y_tr, y_val = train_test_split(
    X_train, y_train, test_size=0.3, random_state=42, stratify=y_train)
'''


def header(*imports):
    """Imports the task uses, then the shared reading and train/test split."""
    return ('import pandas as pd\n# 이 문제에 쓰는 도구를 불러와요.\n' + '\n'.join(imports) + '\n' + READ)


SPLIT = 'from sklearn.model_selection import train_test_split'
TREE = 'from sklearn.tree import DecisionTreeClassifier'
FOREST = 'from sklearn.ensemble import RandomForestClassifier'
SCORE = 'from sklearn.metrics import accuracy_score'
CV = 'from sklearn.model_selection import train_test_split, cross_val_score'
GRID = 'from sklearn.model_selection import train_test_split, GridSearchCV'
PLT = 'import matplotlib.pyplot as plt'

# A wrong entry ('fixed', old, new) is a mistake made after the intended edit: old -> new in the solution.
FIXED = 'fixed'


def experiment(id, title, principle, goal, head, body, before, after, *, compare, caution, hints, wrong,
               plot=False, challenge=False):
    """One experiment on the base table, graded on the two changed tables too."""
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
    maker = plot_task if plot else py_task
    return maker(id, title, principle, goal, starter, before, after, caution=caution, hints=hints,
                 scenarios=SCENARIOS, files={PATH: BASE}, compare=compare, wrong=edits, challenge=challenge)


GRID_FIT = '''grid.fit(X, y)
# 튜닝 모델의 점수예요.
tuned_acc = grid.best_score_'''

GRID_FIT_DONE = '''grid.fit(X_train, y_train)
# 튜닝 모델의 점수예요.
tuned_acc = accuracy_score(y_test, grid.best_estimator_.predict(X_test))'''

DROP_START = '''weakest = imp.idxmax()
print('뺄 열:', weakest)
# 모든 열을 쓸 때와 그 열을 뺐을 때의 교차검증 평균이에요.
full = cross_val_score(model, X_train, y_train, cv=3).mean()
small = cross_val_score(model, X_test.drop(columns=[weakest]), y_test, cv=3).mean()'''

DROP_DONE = DROP_START.replace('imp.idxmax()', 'imp.idxmin()') \
    .replace('X_test.drop(columns=[weakest]), y_test', 'X_train.drop(columns=[weakest]), y_train')


def build():
    return lesson('aice-model-improvement', '공정하게 모델을 비교하고 개선하기',
        '훈련 점수만 높은 과적합을 알아봐요. '
        '설정은 검증과 교차검증으로 고르고, 테스트 자료는 마지막에 한 번만 써요. '
        '필수 문제 8개와 선택 도전 2개예요.',
        SOURCES, [
        experiment('overfit-gap', '훈련 점수만 높으면 과적합이에요',
            '자료엔 우연히 틀린 기록, 곧 잡음(noise)이 섞여요. 잡음까지 외운 모델은 답만 외운 학생 같아요.\n'
            '훈련 점수는 높은데 처음 보는 자료에선 떨어져요. 이걸 과적합(overfitting)이라고 해요.\n'
            '`max_depth`는 결정트리가 몇 단계까지 갈라질지 정해요. None이면 끝까지 갈라져요.',
            '자, 먼저 실행해서 훈련 정확도와 테스트 정확도의 차이를 보세요.\n'
            '`max_depth=None`을 `max_depth=3`으로 바꾸세요.\n'
            '다시 실행해서 두 점수와 차이가 어떻게 달라졌는지 비교해요.',
            header(SPLIT, TREE, SCORE),
            '''
            # max_depth로 나무의 깊이를 정해요. None은 제한 없음이에요.
            model = DecisionTreeClassifier(max_depth=None, random_state=42)
            # 학습은 훈련 자료로만 해요.
            model.fit(X_train, y_train)
            # 같은 모델을 훈련 자료와 테스트 자료로 각각 채점해요.
            train_acc = accuracy_score(y_train, model.predict(X_train))
            test_acc = accuracy_score(y_test, model.predict(X_test))
            print('훈련 정확도:', round(train_acc, 3))
            print('테스트 정확도:', round(test_acc, 3))
            # 차이가 크면 과적합을 의심해요.
            print('차이:', round(train_acc - test_acc, 3))
            ''',
            'max_depth=None', 'max_depth=3', compare=['train_acc', 'test_acc'],
            caution="`max_depth='3'`처럼 숫자에 따옴표를 붙이면 오류가 나요.",
            hints=['`DecisionTreeClassifier(max_depth=3, random_state=42)`로 바꿔요.'],
            wrong=[('max_depth=None', "max_depth='3'"),
                   (FIXED, 'model.fit(X_train, y_train)', 'model.fit(X_test, y_test)')]),
        experiment('valid-not-train', '후보는 검증 점수로 비교해요',
            'max_depth처럼 학습 전에 사람이 정하는 설정이 하이퍼파라미터예요.\n'
            '훈련 자료를 한 번 더 나눠 검증 몫을 떼요. 후보는 남은 훈련 몫으로 학습하고, 검증 몫 점수로 골라요.\n'
            "`표['열'].idxmax()`는 그 열 값이 가장 큰 행의 이름을 돌려줘요. `idxmin()`의 반대예요.",
            '먼저 실행해서 깊이별 train 점수와 valid 점수를 보세요.\n'
            'train은 깊을수록 커지죠? 그래서 train으로 고르면 가장 깊은 나무가 뽑혀요.\n'
            "best 줄의 `'train'`을 `'valid'`로 바꾸세요.\n"
            '다시 실행해서 고른 깊이를 비교해요.',
            header(SPLIT, TREE, SCORE) + VALID + '\n',
            '''
            def scores(depth):
                # 그 깊이의 결정트리를 훈련 몫으로 학습해요.
                model = DecisionTreeClassifier(max_depth=depth, random_state=42)
                model.fit(X_tr, y_tr)
                # 훈련 몫 점수와 검증 몫 점수를 함께 돌려줘요.
                train_acc = accuracy_score(y_tr, model.predict(X_tr))
                valid_acc = accuracy_score(y_val, model.predict(X_val))
                return [train_acc, valid_acc]


            # 깊이 후보마다 두 점수를 한 행씩 표로 모아요.
            table = pd.DataFrame([scores(1), scores(2), scores(3), scores(5), scores(8)],
                                 index=[1, 2, 3, 5, 8], columns=['train', 'valid'])
            # 행 이름이 깊이예요. 위로 갈수록 얕은 나무예요.
            print('깊이별 정확도')
            print(table.round(3))
            # 점수가 가장 높은 행의 이름, 곧 깊이를 골라요.
            best = table['train'].idxmax()
            print('고른 깊이:', best)
            ''',
            "table['train'].idxmax()", "table['valid'].idxmax()", compare=['best'],
            caution='`.max()`를 쓰면 깊이가 아니라 가장 높은 점수가 나와요.',
            hints=["`best = table['valid'].idxmax()`로 바꿔요."],
            wrong=[("table['train'].idxmax()", "table['valid'].max()"),
                   # Smallest train-valid gap: sounds safe, but picks the too-simple tree.
                   ("table['train'].idxmax()", "(table['train'] - table['valid']).idxmin()")]),
        experiment('test-peek', '테스트 자료로 고르면 안 돼요',
            '후보를 테스트 점수로 고르면 테스트 자료를 고르기에 쓴 거예요.\n'
            '모의고사를 미리 풀고 답을 고친 셈이죠. 그 점수는 실력보다 좋아 보여요.\n'
            '고르기는 검증 몫으로 하고, 테스트는 마지막에 한 번만 채점해요.',
            '먼저 실행해서 고른 깊이와 테스트 정확도를 적어 두세요.\n'
            '`pick_score`의 return 줄에서 `y_test`, `X_test`를 `y_val`, `X_val`로 바꾸세요.\n'
            '다시 실행해서 고른 깊이와 테스트 정확도를 견줘 보세요.\n'
            '테스트 점수가 내려가도 이쪽이 정직한 점수예요.',
            header(SPLIT, TREE, SCORE) + VALID + '\n',
            '''
            def pick_score(depth):
                # 그 깊이의 결정트리를 훈련 몫으로 학습해요.
                model = DecisionTreeClassifier(max_depth=depth, random_state=42)
                model.fit(X_tr, y_tr)
                # 후보를 고르는 점수예요. 어느 자료로 채점하는지 보세요.
                return accuracy_score(y_test, model.predict(X_test))


            # 깊이 후보마다 고르는 점수를 매겨요.
            scores = pd.Series([pick_score(2), pick_score(3), pick_score(4), pick_score(6)],
                               index=[2, 3, 4, 6])
            print(scores.round(3))
            # 고르는 점수가 가장 높은 깊이예요.
            best = scores.idxmax()
            # 고른 깊이로 다시 학습하고, 테스트 자료로 한 번 채점해요.
            final = DecisionTreeClassifier(max_depth=best, random_state=42)
            final.fit(X_tr, y_tr)
            test_acc = accuracy_score(y_test, final.predict(X_test))
            print('고른 깊이:', best)
            print('테스트 정확도:', round(test_acc, 3))
            ''',
            'return accuracy_score(y_test, model.predict(X_test))',
            'return accuracy_score(y_val, model.predict(X_val))', compare=['best', 'test_acc'],
            caution='`y_val`과 `X_test`처럼 짝을 섞으면 행 수가 달라 오류가 나요.',
            hints=['`return accuracy_score(y_val, model.predict(X_val))`로 바꿔요.'],
            wrong=[('return accuracy_score(y_test, model.predict(X_test))',
                    'return accuracy_score(y_tr, model.predict(X_tr))'),
                   ('return accuracy_score(y_test, model.predict(X_test))',
                    'return accuracy_score(y_val, model.predict(X_test))')]),
        experiment('cross-val-mean', '교차검증은 점수 여러 개의 평균이에요',
            '검증 몫 하나의 점수는 어떤 행이 들어갔느냐에 따라 흔들려요.\n'
            '교차검증(cross validation)은 훈련 자료를 여러 몫으로 나눠요. 한 몫씩 돌아가며 검증에 써요.\n'
            '`cross_val_score(모델, X, y, cv=3)`은 몫마다 낸 점수 3개를 배열로 돌려줘요.',
            '먼저 실행해서 점수 3개가 서로 같은지 보세요.\n'
            '준비 코드는 첫 점수 하나만 대표 점수로 써요.\n'
            '`scores[0]`을 `scores.mean()`으로 바꾸세요.\n'
            '다시 실행해서 대표 점수가 어떻게 달라졌는지 봐요.',
            header(CV, TREE),
            '''
            # 깊이 3인 결정트리예요. 아직 학습하지 않았어요.
            model = DecisionTreeClassifier(max_depth=3, random_state=42)
            # 훈련 자료를 3몫으로 나눠 학습과 채점을 세 번 해요.
            scores = cross_val_score(model, X_train, y_train, cv=3)
            # 몫마다 나온 점수 3개예요.
            print(scores.round(3))
            # 이 모델의 대표 점수예요.
            cv_score = scores[0]
            print('교차검증 점수:', round(cv_score, 3))
            ''',
            'cv_score = scores[0]', 'cv_score = scores.mean()', compare=['cv_score'],
            caution='`cross_val_score`에 X, y 전체를 넣으면 테스트 몫이 검증에 섞여요.',
            hints=['`cv_score = scores.mean()`으로 바꿔요.'],
            wrong=[('cv_score = scores[0]', 'cv_score = scores.max()'),
                   (FIXED, 'cross_val_score(model, X_train, y_train, cv=3)', 'cross_val_score(model, X, y, cv=3)')]),
        experiment('grid-search', 'GridSearchCV로 조합을 모두 시험해요',
            '`GridSearchCV`는 후보 설정의 모든 조합을 하나씩 교차검증해요.\n'
            '후보는 `param_grid` 딕셔너리에 적어요. 설정 이름마다 값 목록을 줘요.\n'
            '`fit`이 끝나면 `best_params_`에 가장 좋은 설정이 담겨요.',
            '먼저 실행해서 후보 표와 고른 설정을 보세요.\n'
            'min_samples_leaf는 나무 끝 칸(잎)에 남길 최소 행 수예요. 기본값은 1이에요.\n'
            "`'max_depth'` 줄과 `}` 사이에 `'min_samples_leaf': [1, 5],`를 넣으세요. 들여쓰기는 윗줄과 맞춰요.\n"
            '다시 실행해서 후보 수와 고른 설정을 비교해요. 잎 1이 뽑히면 기본값이 더 나았던 거예요.',
            header(GRID, TREE),
            '''
            # 시험할 설정 이름과 값 목록이에요.
            param_grid = {
                'max_depth': [2, 3, 4, 6],
            }
            # 후보마다 3몫 교차검증을 하는 도구예요.
            grid = GridSearchCV(DecisionTreeClassifier(random_state=42), param_grid, cv=3)
            # 찾기도 훈련 자료로만 해요.
            grid.fit(X_train, y_train)
            # 후보별 교차검증 평균이에요. 이름과 달리 테스트 자료 점수가 아니에요.
            result = pd.DataFrame(grid.cv_results_)
            print('후보별 교차검증 평균')
            print(result[['params', 'mean_test_score']].round(3))
            # 가장 좋은 설정과 그 교차검증 평균이에요.
            best = grid.best_params_
            print('고른 설정:', best)
            print('교차검증 점수:', round(grid.best_score_, 3))
            ''',
            "    'max_depth': [2, 3, 4, 6],\n", "    'max_depth': [2, 3, 4, 6],\n    'min_samples_leaf': [1, 5],\n",
            compare=['best'],
            caution="`'min_samples_leaf': 5`처럼 목록 없이 쓰면 TypeError가 나요.",
            hints=["`'max_depth'` 줄과 `}` 사이에 `'min_samples_leaf': [1, 5],`를 넣어요."],
            wrong=[("    'max_depth': [2, 3, 4, 6],\n", "    'max_depth': [2, 3, 4, 6],\n    'min_samples_leaf': 5,\n"),
                   (FIXED, 'grid.fit(X_train, y_train)', 'grid.fit(X, y)')]),
        experiment('test-once', '고른 모델은 테스트로 한 번만 채점해요',
            '`best_score_`는 교차검증 평균이에요. 훈련 자료 안에서 낸 검증 점수죠.\n'
            '`best_estimator_`는 고른 설정으로 훈련 자료 전체에 다시 학습한 모델이에요.\n'
            '마지막 성적은 이 모델로 테스트 자료를 한 번 채점해서 내요.',
            '먼저 실행해서 교차검증 점수와 테스트 정확도가 같은지 보세요.\n'
            'test_acc 줄을 아래처럼 바꾸세요.\n'
            '`test_acc = accuracy_score(y_test, grid.best_estimator_.predict(X_test))`\n'
            '다시 실행해서 두 점수를 견줘 보세요. 달라도 괜찮아요. 보고할 성적은 테스트 정확도예요.',
            header(GRID, TREE, SCORE),
            '''
            # 앞 문제에서 넓힌 후보예요.
            param_grid = {'max_depth': [2, 3, 4, 6], 'min_samples_leaf': [1, 5]}
            grid = GridSearchCV(DecisionTreeClassifier(random_state=42), param_grid, cv=3)
            # 찾기는 훈련 자료로만 해요.
            grid.fit(X_train, y_train)
            print('고른 설정:', grid.best_params_)
            print('교차검증 점수:', round(grid.best_score_, 3))
            # 고른 모델의 마지막 성적이에요. 테스트 자료로 한 번만 채점해요.
            test_acc = grid.best_score_
            print('테스트 정확도:', round(test_acc, 3))
            ''',
            'test_acc = grid.best_score_',
            'test_acc = accuracy_score(y_test, grid.best_estimator_.predict(X_test))', compare=['test_acc'],
            caution='`best_score_`를 테스트 점수로 적으면 검증 점수를 두 번 적는 셈이에요.',
            hints=['`test_acc = accuracy_score(y_test, grid.best_estimator_.predict(X_test))`로 바꿔요.'],
            wrong=[('test_acc = grid.best_score_',
                    'test_acc = accuracy_score(y_train, grid.best_estimator_.predict(X_train))'),
                   # A fresh default tree instead of the chosen one.
                   ('test_acc = grid.best_score_',
                    'test_acc = accuracy_score(y_test, DecisionTreeClassifier(random_state=42)'
                    '.fit(X_train, y_train).predict(X_test))')]),
        experiment('importance-sort', '특성 중요도를 큰 순서로 봐요',
            '트리 모델은 학습 뒤 `feature_importances_`에 열마다 쓰인 정도를 담아요.\n'
            '이 값을 특성 중요도(feature importance)라고 해요. 모두 더하면 1이에요.\n'
            '숫자만 보면 어느 열인지 몰라요. 그래서 열 이름과 짝지어 Series로 봐요.',
            '먼저 실행해서 열 이름과 중요도를 보세요. 지금은 X의 열 순서예요.\n'
            '`imp = pd.Series(...)` 줄 끝에 `.sort_values(ascending=False)`를 붙이세요.\n'
            '다시 실행해서 가장 많이 쓰인 열이 맨 위에 오는지 봐요.',
            header(SPLIT, FOREST),
            '''
            # 랜덤포레스트를 훈련 자료로 학습해요.
            model = RandomForestClassifier(random_state=42)
            model.fit(X_train, y_train)
            # 중요도 숫자에 열 이름을 붙여 Series로 만들어요.
            imp = pd.Series(model.feature_importances_, index=X_train.columns)
            print(imp.round(3))
            # 중요도를 모두 더하면 1이에요.
            print('합:', round(imp.sum(), 3))
            ''',
            'imp = pd.Series(model.feature_importances_, index=X_train.columns)',
            'imp = pd.Series(model.feature_importances_, index=X_train.columns).sort_values(ascending=False)',
            compare=['imp'],
            caution='숫자만 따로 정렬하면 열 이름과 짝이 어긋나요.',
            hints=['`imp = pd.Series(model.feature_importances_, index=X_train.columns)` 끝에 '
                   '`.sort_values(ascending=False)`를 붙여요.'],
            wrong=[(FIXED, '.sort_values(ascending=False)', '.sort_values()'),
                   ('imp = pd.Series(model.feature_importances_, index=X_train.columns)',
                    'imp = pd.Series(sorted(model.feature_importances_, reverse=True), index=X_train.columns)')]),
        experiment('importance-barh', '중요도는 가로 막대로 그려요',
            "`kind='barh'`는 가로 막대를 그려요. 열 이름이 세로축에 가로로 적혀요.\n"
            '가로 막대는 Series의 첫 값을 맨 아래에 그려요.\n'
            '큰 막대를 맨 위에 두려면 작은 순서로 정렬해서 그려요.',
            '먼저 실행해서 가장 긴 막대가 어디에 있는지 보세요.\n'
            '`sort_values` 괄호 안의 `ascending=False`를 지우세요.\n'
            '다시 실행해서 막대의 위아래 순서를 비교해요.',
            header(SPLIT, FOREST).replace('import pandas as pd\n', 'import pandas as pd\n' + PLT + '\n', 1),
            '''
            # 랜덤포레스트를 훈련 자료로 학습해요.
            model = RandomForestClassifier(random_state=42)
            model.fit(X_train, y_train)
            # 중요도 숫자에 열 이름을 붙여요.
            imp = pd.Series(model.feature_importances_, index=X_train.columns)
            # 중요도를 정렬해요. 기본은 작은 순서, ascending=False면 큰 순서예요.
            imp = imp.sort_values(ascending=False)
            print(imp.round(3))
            # 가로 막대로 그려요. Series의 첫 값이 맨 아래에 놓여요.
            imp.plot(kind='barh')
            plt.xlabel('중요도')
            plt.title('불량 예측에 쓰인 정도')
            plt.show()
            ''',
            'imp.sort_values(ascending=False)', 'imp.sort_values()', compare=['imp'], plot=True,
            caution='정렬하지 않고 그리면 막대가 X의 열 순서대로 놓여요.',
            hints=['`imp = imp.sort_values()`로 바꿔요.'],
            wrong=[('imp = imp.sort_values(ascending=False)', 'imp = imp'),
                   (FIXED, "imp.plot(kind='barh')", "imp.plot(kind='bar')")]),
        experiment('fair-compare', '도전 · 기본 모델과 튜닝 모델을 같은 잣대로',
            '하이퍼파라미터를 골라 모델을 고치는 걸 튜닝(tuning)이라고 해요. 튜닝은 훈련 자료 안에서만 해요.\n'
            '기본 설정 모델과 튜닝한 모델은 같은 테스트 자료로 한 번씩 채점해 비교해요.\n'
            '한쪽만 검증 점수로 적으면 공정한 비교가 아니에요.',
            '두 모델의 테스트 정확도를 같은 방법으로 출력하게 하세요.\n'
            '준비 코드는 튜닝 쪽에서 두 군데가 틀렸어요. 고칠 곳은 직접 찾아보세요.\n'
            'fit에 넣은 자료와 tuned_acc가 무슨 점수인지 확인해요.',
            header(GRID, TREE, SCORE),
            code('''
            # 기본 설정 결정트리를 훈련 자료로 학습해요.
            base = DecisionTreeClassifier(random_state=42)
            base.fit(X_train, y_train)
            # 기본 모델의 테스트 정확도예요.
            base_acc = accuracy_score(y_test, base.predict(X_test))

            # 깊이와 잎 크기 후보를 교차검증으로 골라요.
            param_grid = {'max_depth': [2, 3, 4, 6], 'min_samples_leaf': [1, 5]}
            grid = GridSearchCV(DecisionTreeClassifier(random_state=42), param_grid, cv=3)
            ''') + GRID_FIT + '\n' + code('''
            # 두 점수를 나란히 봐요.
            print('고른 설정:', grid.best_params_)
            print('기본 모델:', round(base_acc, 3))
            print('튜닝 모델:', round(tuned_acc, 3))
            '''),
            GRID_FIT, GRID_FIT_DONE, compare=['base_acc', 'tuned_acc'], challenge=True,
            caution='`grid.fit`에 X, y 전체를 넣으면 테스트 행이 튜닝에 섞여요.',
            hints=['튜닝도 훈련 자료로만 하고, 튜닝 점수도 테스트 정확도로 맞춰요.',
                   '`grid.fit(X_train, y_train)`으로 바꿔요. '
                   'tuned_acc는 `accuracy_score(y_test, grid.best_estimator_.predict(X_test))`예요.'],
            wrong=[(GRID_FIT, GRID_FIT.replace('grid.fit(X, y)', 'grid.fit(X_train, y_train)')),
                   (GRID_FIT, GRID_FIT_DONE.replace('grid.fit(X_train, y_train)', 'grid.fit(X, y)'))]),
        experiment('drop-weakest', '도전 · 가장 덜 쓰인 열을 빼 봐요',
            '중요도가 가장 낮은 열은 빼도 점수가 비슷할 수 있어요.\n'
            '뺄지 말지는 훈련 자료의 교차검증 평균으로 비교해서 정해요. 뺀 뒤 평균이 떨어지면 그 열은 남겨요.\n'
            '테스트 자료는 이 비교에 쓰지 않아요.',
            '중요도가 가장 낮은 열을 빼고 교차검증 평균을 다시 재게 하세요.\n'
            '준비 코드는 두 군데가 틀렸어요. 고칠 곳은 직접 찾아보세요.\n'
            '뺄 열 이름과 두 평균 점수를 확인해요.',
            header(CV, FOREST),
            code('''
            # 랜덤포레스트로 열마다 중요도를 구해요.
            model = RandomForestClassifier(random_state=42)
            model.fit(X_train, y_train)
            # 중요도에 열 이름을 붙여 Series로 봐요.
            imp = pd.Series(model.feature_importances_, index=X_train.columns)
            print(imp.round(3))
            # 중요도가 가장 낮은 열 이름이에요.
            ''') + DROP_START + '\n' + code('''
            # 두 평균을 견줘 봐요.
            print('모든 열:', round(full, 3))
            print('뺀 뒤:', round(small, 3))
            '''),
            DROP_START, DROP_DONE, compare=['weakest', 'full', 'small'], challenge=True,
            caution='열 이름을 직접 적으면 자료가 바뀔 때 엉뚱한 열을 빼요.',
            hints=['가장 작은 값의 열을 고르고, 두 평균 모두 훈련 자료로 재요.',
                   '`imp.idxmin()`으로 고르고, small은 `X_train.drop(columns=[weakest])`와 `y_train`으로 재요.'],
            wrong=[(DROP_START, DROP_START.replace('imp.idxmax()', 'imp.idxmin()')),
                   (DROP_START, DROP_DONE.replace('imp.idxmin()', "'weight'")),
                   (DROP_START, DROP_DONE.replace('imp.idxmin()', 'imp.idxmax()'))]),
    ])
