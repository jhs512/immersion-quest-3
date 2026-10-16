"""aice-classification: predict a kind, then read what the model gets wrong (AICE Associate 15th lesson).

Binary tasks read an original web-shop visit table (visits, minutes, cart, coupon -> bought). The
tables come from a seeded generator below: a noisy score decides who bought, and only the given
share of rows with the highest score bought, so the 1 share is exact. The base table has 96 rows
with 25% buyers; the changed tables have 80 rows (20%) and 112 rows (30%). The baseline task also
reads a 72-row table where 65% bought, so a baseline that always says 0 fails there, and a 76-row
half-bought table whose training and test parts have different majorities, so fitting on the test
part fails there.
On the base table the baseline scores 0.75, the logistic model 0.79 with recall 0.5, and a depth-1
tree has the best accuracy but lower recall, so accuracy alone picks the wrong model. False
negatives differ from false positives in the base and 80-row tables, so a swapped confusion matrix
changes; at threshold 0.3 recall rises and precision falls on the base table.
The three-class task reads an original member table (months, visits, spend -> bronze/silver/gold).
Every split is train_test_split(test_size=0.25, random_state=42, stratify=y).
"""
import random

from certification_course.kit import py_task
from principles_course.common import code, lesson

SOURCES = ['https://aice.study/info/aice/asso',
           'https://scikit-learn.org/stable/modules/model_evaluation.html#classification-metrics',
           'https://scikit-learn.org/stable/modules/generated/sklearn.dummy.DummyClassifier.html']

VISITS = 'data/visits.csv'
MEMBERS = 'data/members.csv'


def noise(rng, size):
    # Sum of three uniforms: a bell-like noise built only from random(), stable across versions.
    return (rng.random() + rng.random() + rng.random() - 1.5) * size


def shop(seed, rows, ones):
    """Visit table: bought is 1 for the `ones` share of rows with the highest noisy score."""
    rng = random.Random(seed)
    items = []
    for _ in range(rows):
        visits = rng.randint(1, 14)
        minutes = visits * rng.randint(2, 6) + rng.randint(0, 9)
        cart = rng.randint(0, 6)
        coupon = 1 if rng.random() < 0.35 else 0
        score = 0.25 * visits + 0.04 * minutes + 0.6 * cart + 1.0 * coupon + noise(rng, 4.0)
        items.append((visits, minutes, cart, coupon, score))
    order = sorted(range(rows), key=lambda i: -items[i][4])
    top = set(order[:round(rows * ones)])
    lines = ['visits,minutes,cart,coupon,bought']
    lines += [f'{v},{m},{c},{k},{int(i in top)}' for i, (v, m, c, k, _) in enumerate(items)]
    return '\n'.join(lines) + '\n'


def grades(seed, rows, bronze, silver):
    """Member table: the grade comes from a noisy spend score, cut at the given shares."""
    rng = random.Random(seed)
    items = []
    for _ in range(rows):
        months = rng.randint(1, 48)
        visits = rng.randint(1, 20)
        spend = rng.randint(2, 30)
        score = 0.6 * spend + 0.25 * visits + 0.05 * months + noise(rng, 7.0)
        items.append((months, visits, spend, score))
    order = sorted(range(rows), key=lambda i: items[i][3])
    cut = (round(rows * bronze), round(rows * (bronze + silver)))
    label = {i: 'bronze' if rank < cut[0] else 'silver' if rank < cut[1] else 'gold'
             for rank, i in enumerate(order)}
    lines = ['months,visits,spend,grade']
    lines += [f'{m},{v},{s},{label[i]}' for i, (m, v, s, _) in enumerate(items)]
    return '\n'.join(lines) + '\n'


SHOP = shop(7, 96, 0.25)
SHOP_FEWER = shop(11, 80, 0.2)
SHOP_MORE = shop(23, 112, 0.3)
# Most visitors bought here, so the most frequent kind is 1.
SHOP_MOSTLY_BUY = shop(31, 72, 0.65)
# Half bought: the split leaves 29 vs 28 in training but 9 vs 10 in test, so a baseline fitted
# on the test part answers the other kind.
SHOP_EVEN = shop(37, 76, 0.5)

GRADE = grades(5, 90, 0.5, 0.32)
GRADE_FEWER = grades(13, 72, 0.45, 0.35)
GRADE_MORE = grades(29, 108, 0.55, 0.28)

SHOP_HEADER = '''# 표 도구 pandas와 자료를 나누는 함수를 불러와요.
import pandas as pd
from sklearn.model_selection import train_test_split
# 이번 문제에 쓸 도구를 불러와요.
{imports}
# 직접 만든 쇼핑몰 방문 자료예요. 실제 고객 자료가 아니에요.
df = pd.read_csv('data/visits.csv')
# visits는 이번 달 방문 수, minutes는 머문 시간(분)이에요.
# cart는 장바구니 상품 수, coupon은 쿠폰을 받았으면 1이에요.
# bought는 다음 주에 샀으면 1, 안 샀으면 0이에요.
y = df['bought']
X = df.drop(columns=['bought'])
# 1의 비율이 두 몫에서 같도록 stratify=y로 나눠요.
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

'''

GRADE_HEADER = '''# 표 도구 pandas와 자료를 나누는 함수를 불러와요.
import pandas as pd
from sklearn.model_selection import train_test_split
# 이번 문제에 쓸 도구를 불러와요.
{imports}
# 직접 만든 회원 등급 자료예요. 실제 회원 자료가 아니에요.
df = pd.read_csv('data/members.csv')
# months는 가입 개월 수, visits는 이번 달 방문 수예요.
# spend는 이번 달 쓴 돈(만 원), grade는 다음 달 등급이에요.
y = df['grade']
X = df.drop(columns=['grade'])
# 세 등급의 비율이 두 몫에서 같도록 stratify=y로 나눠요.
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

'''


def buy(id, title, principle, goal, imports, body, before, after, *, compare, caution, hints, wrong=None,
        changed=(SHOP_FEWER, SHOP_MORE), challenge=False):
    """One experiment on the visit table, graded on the changed tables too."""
    header = SHOP_HEADER.format(imports=code(imports))
    scenarios = [{'files': {VISITS: table}} for table in changed]
    return py_task(id, title, principle, goal, header + code(body), before, after, caution=caution,
                   hints=hints, scenarios=scenarios, files={VISITS: SHOP}, compare=compare, wrong=wrong,
                   challenge=challenge)


def members(id, title, principle, goal, imports, body, before, after, *, compare, caution, hints, wrong=None):
    """One experiment on the member grade table, graded on the changed tables too."""
    header = GRADE_HEADER.format(imports=code(imports))
    scenarios = [{'files': {MEMBERS: GRADE_FEWER}}, {'files': {MEMBERS: GRADE_MORE}}]
    return py_task(id, title, principle, goal, header + code(body), before, after, caution=caution,
                   hints=hints, scenarios=scenarios, files={MEMBERS: GRADE}, compare=compare, wrong=wrong)


# Shared start of the logistic tasks: the same model on the same split.
LOGISTIC = code('''
    # 로지스틱 회귀로 배우고 테스트를 예측해요.
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)
''')

# Challenge 1: the table shows accuracy only; the learner adds recall and sorts by it.
TABLE_START = '''                 accuracy_score(y_test, tree_pred)],
}, index=['base', 'logistic', 'tree'])'''

TABLE_DONE = '''                 accuracy_score(y_test, tree_pred)],
    # 같은 모델 순서로 재현율도 모아요.
    'recall': [recall_score(y_test, base_pred), recall_score(y_test, logistic_pred),
               recall_score(y_test, tree_pred)],
}, index=['base', 'logistic', 'tree'])
# 재현율이 높은 모델부터 줄을 세워요.
table = table.sort_values('recall', ascending=False)'''

# Challenge 2: the probability column and the confusion matrix order are both wrong.
MISSED_START = '''p1 = proba[:, 0]
# 1일 확률이 0.3 이상이면 1로 답해요.
pred = (p1 >= 0.3).astype(int)
# 행은 실제, 열은 예측인 혼동행렬이에요.
cm = confusion_matrix(pred, y_test)'''

MISSED_DONE = MISSED_START.replace('proba[:, 0]', 'proba[:, 1]') \
    .replace('confusion_matrix(pred, y_test)', 'confusion_matrix(y_test, pred)')


def build():
    return lesson('aice-classification', '종류를 예측하고 오류 읽기',
        '산다·안 산다 같은 종류를 맞히는 분류 모델을 써요. '
        '정확도만 보지 않고 무엇을 틀렸는지 읽어요. '
        '필수 문제 8개와 선택 도전 2개예요.',
        SOURCES, [
        buy('majority-baseline', '많은 쪽으로 전부 답하는 기준',
            '기준 모델은 입력을 보지 않고 정해진 규칙으로만 답해요.\n'
            "`DummyClassifier(strategy='most_frequent')`는 훈련 y에서 가장 많은 종류로 답해요.\n"
            '정확도(accuracy)는 맞힌 행의 비율이에요. `accuracy_score(y_test, pred)`로 구해요.',
            '자, 지금 기준 모델은 모든 손님이 산다(1)고 답해요.\n'
            '먼저 실행해서 예측과 정확도를 보세요.\n'
            "괄호 안을 `strategy='most_frequent'`로 바꾸고 다시 실행하세요.\n"
            '정확도를 테스트 y의 0 비율과 견줘 보세요. 앞으로 만들 모델은 이 기준 정확도를 넘어야 해요.',
            '''
            from sklearn.dummy import DummyClassifier
            from sklearn.metrics import accuracy_score
            ''',
            '''
            # 기준 모델이에요. strategy가 답하는 규칙이에요.
            base = DummyClassifier(strategy='constant', constant=1)
            # 기준 모델도 훈련 자료로 fit해요. 입력 X는 보지 않아요.
            base.fit(X_train, y_train)
            pred = base.predict(X_test)
            print(pred)
            # 맞힌 비율인 정확도예요.
            acc = accuracy_score(y_test, pred)
            print(acc)
            # 테스트 정답에서 종류별 비율이에요.
            print(y_test.value_counts(normalize=True))
            ''',
            "strategy='constant', constant=1", "strategy='most_frequent'",
            changed=(SHOP_FEWER, SHOP_MOSTLY_BUY, SHOP_EVEN), compare=['pred', 'acc'],
            caution='`constant=0`처럼 직접 적으면 1이 많은 자료에서 틀려요.',
            hints=["`DummyClassifier(strategy='most_frequent')`로 바꿔요. constant는 지워요."],
            wrong=[("strategy='constant', constant=1", "strategy='constant', constant=0"),
                   # The right strategy, but the baseline learns the most frequent kind from the test part.
                   ("strategy='most_frequent')\n# 기준 모델도 훈련 자료로 fit해요. 입력 X는 보지 않아요.\n"
                    'base.fit(X_train, y_train)',
                    "strategy='most_frequent')\n# 기준 모델도 훈련 자료로 fit해요. 입력 X는 보지 않아요.\n"
                    'base.fit(X_test, y_test)')]),
        buy('logistic-model', '분류는 분류 모델로 맞혀요',
            '분류(classification)는 정해진 종류 중 하나를 맞혀요.\n'
            '선형회귀는 소수점이 있는 숫자로 답해서 분류 채점 함수가 받지 못해요.\n'
            '로지스틱 회귀(`LogisticRegression`)는 분류 모델이라 종류 중 하나로 답해요.',
            '먼저 실행해서 예측값과 오류의 마지막 줄을 읽으세요. '
            'binary는 0과 1 두 종류, continuous는 소수점이 있는 숫자예요.\n'
            '두 줄의 `LinearRegression`을 `LogisticRegression`으로 바꾸세요.\n'
            '괄호 안에는 `max_iter=1000`을 넣어요. 배우기를 반복하는 최대 횟수예요.\n'
            '다시 실행해서 정확도를 앞 문제의 기준 정확도와 견줘 보세요.',
            '''
            from sklearn.metrics import accuracy_score
            ''',
            '''
            # 모델을 가져와 만들어요.
            from sklearn.linear_model import LinearRegression
            model = LinearRegression()
            # 훈련 자료로 배우고 테스트 자료를 예측해요.
            model.fit(X_train, y_train)
            pred = model.predict(X_test)
            # 앞의 다섯 예측을 봐요.
            print(pred[:5])
            # 맞힌 비율인 정확도예요.
            acc = accuracy_score(y_test, pred)
            print(acc)
            ''',
            'from sklearn.linear_model import LinearRegression\nmodel = LinearRegression()',
            'from sklearn.linear_model import LogisticRegression\nmodel = LogisticRegression(max_iter=1000)',
            compare=['pred', 'acc'],
            caution='회귀 예측을 `round()`로 반올림하면 오류는 사라져도 분류 모델은 아니에요.',
            hints=['`from sklearn.linear_model import LogisticRegression`과 '
                   '`model = LogisticRegression(max_iter=1000)`으로 바꿔요.'],
            wrong=[('pred = model.predict(X_test)', 'pred = model.predict(X_test).round()'),
                   ('LogisticRegression(max_iter=1000)\n# 훈련 자료로 배우고 테스트 자료를 예측해요.\n'
                    'model.fit(X_train, y_train)',
                    'LogisticRegression(max_iter=1000)\n# 훈련 자료로 배우고 테스트 자료를 예측해요.\n'
                    'model.fit(X_test, y_test)')]),
        buy('tree-questions', '트리는 질문을 이어 가요',
            '결정트리 분류(`DecisionTreeClassifier`)는 예/아니요 질문으로 자료를 나눠요.\n'
            '끝 칸(잎)에서는 그 칸에서 가장 많은 종류로 답해요. `max_depth`는 질문을 잇는 최대 횟수예요.\n'
            '`export_text`는 트리가 만든 질문을 글로 보여 줘요.',
            '먼저 실행해서 질문이 몇 개인지, 어느 열을 묻는지 보세요. '
            '`<=` 줄과 `>` 줄 한 쌍이 질문 하나예요.\n'
            '`class: 1`인 칸이 1이라고 답하는 칸이에요.\n'
            '`max_depth=1`을 `max_depth=2`로 바꾸고 다시 실행하세요.\n'
            '질문 수와 1이라고 답한 수, 정확도를 비교해요. 질문을 늘린다고 정확도가 꼭 오르지는 않아요.',
            '''
            from sklearn.metrics import accuracy_score
            from sklearn.tree import DecisionTreeClassifier, export_text
            ''',
            '''
            # 질문을 몇 번까지 이을지 max_depth로 정해요.
            tree = DecisionTreeClassifier(max_depth=1, random_state=42)
            tree.fit(X_train, y_train)
            # 트리가 배운 질문을 글로 봐요. 열 이름도 넘겨요.
            print(export_text(tree, feature_names=list(X_train.columns)))
            # 테스트를 예측해요. 합계는 1이라고 답한 수예요.
            pred = tree.predict(X_test)
            print(pred.sum())
            # 맞힌 비율인 정확도예요.
            acc = accuracy_score(y_test, pred)
            print(acc)
            ''',
            'max_depth=1', 'max_depth=2', compare=['pred', 'acc'],
            caution='`export_text`에 `max_depth`를 넣으면 보여 주는 깊이만 바뀌어요.',
            hints=['`DecisionTreeClassifier(max_depth=2, random_state=42)`로 바꿔요.'],
            wrong=[('feature_names=list(X_train.columns))', 'feature_names=list(X_train.columns), max_depth=2)'),
                   ('DecisionTreeClassifier(max_depth=1, random_state=42)',
                    'DecisionTreeClassifier(2, random_state=42)')]),
        buy('forest-vote', '숲은 여러 트리의 투표예요',
            '랜덤포레스트(`RandomForestClassifier`)는 트리를 여러 그루 키워요.\n'
            '그루마다 훈련 행을 무작위로 뽑아 배워요. 예측은 트리들이 투표해서 정해요.\n'
            '`n_estimators`는 그루 수, `random_state`는 무작위 뽑기를 고정하는 번호예요.',
            '먼저 실행해서 트리 수, 1이라고 답한 수, 정확도를 보세요.\n'
            '`n_estimators=1`을 `n_estimators=100`으로 바꾸고 다시 실행하세요.\n'
            '`random_state=42`는 그대로 둬요. 빼면 실행마다 달라질 수 있어요.\n'
            '1그루일 때와 세 값을 비교해요. 자료에 따라 숲이 1그루보다 못할 때도 있어서 늘 견줘 봐야 해요.',
            '''
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.metrics import accuracy_score
            ''',
            '''
            # 트리 몇 그루로 숲을 만들지 n_estimators로 정해요.
            forest = RandomForestClassifier(n_estimators=1, random_state=42)
            forest.fit(X_train, y_train)
            # 숲에 자란 트리 수예요.
            print(len(forest.estimators_))
            # 테스트를 예측해요. 합계는 1이라고 답한 수예요.
            pred = forest.predict(X_test)
            print(pred.sum())
            # 맞힌 비율인 정확도예요.
            acc = accuracy_score(y_test, pred)
            print(acc)
            ''',
            'n_estimators=1,', 'n_estimators=100,', compare=['pred', 'acc'],
            caution='`n_estimator`처럼 끝의 s를 빼면 TypeError가 나요.',
            hints=['`RandomForestClassifier(n_estimators=100, random_state=42)`로 바꿔요.'],
            wrong=[('RandomForestClassifier(n_estimators=1,', 'RandomForestClassifier(n_estimator=100,'),
                   ('forest = RandomForestClassifier(n_estimators=1, random_state=42)',
                    'from sklearn.ensemble import RandomForestRegressor\n'
                    'forest = RandomForestRegressor(n_estimators=100, random_state=42)')]),
        buy('confusion-matrix', '혼동행렬로 틀린 곳 읽기',
            '혼동행렬(confusion matrix)은 실제와 예측의 짝을 세는 표예요.\n'
            '`confusion_matrix(y_test, pred)`에서 행은 실제, 열은 예측이에요.\n'
            '행과 열 번호는 0부터 세요. `cm[1, 0]`은 1번 행 0번 열, 실제 1인데 0이라고 답한 수예요.',
            '먼저 실행해서 표와 missed 값을 보세요.\n'
            '지금은 인자 순서가 거꾸로라 행이 예측이에요.\n'
            '괄호 안을 `(y_test, pred)` 순서로 바꾸고 다시 실행하세요.\n'
            '표가 어떻게 바뀌었나요? missed는 놓친 구매 손님 수예요.',
            '''
            from sklearn.linear_model import LogisticRegression
            from sklearn.metrics import confusion_matrix
            ''',
            LOGISTIC + code('''
            pred = model.predict(X_test)
            # 혼동행렬을 만들어요. 앞 인자가 행이 돼요.
            cm = confusion_matrix(pred, y_test)
            print(cm)
            # 0부터 센 1번 행, 0번 열이에요. 실제 1인데 0이라고 답한 수예요.
            missed = cm[1, 0]
            print(missed)
            '''),
            'confusion_matrix(pred, y_test)', 'confusion_matrix(y_test, pred)', compare=['cm', 'missed'],
            caution='`labels=[1, 0]`으로 순서를 바꾸면 칸의 뜻도 바뀌어요.',
            hints=['`cm = confusion_matrix(y_test, pred)`로 바꿔요. 정답이 앞이에요.'],
            wrong=[('confusion_matrix(pred, y_test)', 'confusion_matrix(y_test, pred, labels=[1, 0])'),
                   ('confusion_matrix(pred, y_test)', 'confusion_matrix(y_train, model.predict(X_train))'),
                   # missed comes out right, but the printed table still has predictions as rows.
                   ('missed = cm[1, 0]', 'missed = cm[0, 1]')]),
        buy('precision-recall', '정밀도와 재현율',
            '정밀도(precision)는 1이라고 답한 것 중 진짜 1의 비율이에요.\n'
            '재현율(recall)은 진짜 1 중에서 1이라고 찾아낸 비율이에요.\n'
            '`precision_score`와 `recall_score` 모두 `(y_test, pred)` 순서로 넣어요.',
            '먼저 실행해서 혼동행렬과 두 값을 보세요. 두 값이 같죠?\n'
            'recall 줄은 정밀도 줄을 복사하고 함수 이름을 안 고쳤어요.\n'
            'recall 줄의 `precision_score`를 `recall_score`로 바꾸세요.\n'
            '다시 실행해서 두 값을 혼동행렬로 직접 계산해 봐요. 오른쪽 아래 칸이 맞힌 1이에요. '
            '정밀도는 이 칸을 1번 열(예측 1)의 합으로 나눠요. 재현율은 1번 행(실제 1)의 합으로 나눠요.',
            '''
            from sklearn.linear_model import LogisticRegression
            from sklearn.metrics import confusion_matrix, precision_score, recall_score
            ''',
            LOGISTIC + code('''
            pred = model.predict(X_test)
            # 행은 실제, 열은 예측인 혼동행렬이에요.
            print(confusion_matrix(y_test, pred))
            # 정밀도: 1이라고 답한 것 중 진짜 1의 비율이에요.
            precision = precision_score(y_test, pred)
            # 재현율: 진짜 1 중에서 1이라고 찾아낸 비율이에요.
            recall = precision_score(y_test, pred)
            print(precision, recall)
            '''),
            'recall = precision_score(y_test, pred)', 'recall = recall_score(y_test, pred)',
            compare=['precision', 'recall'],
            caution='`recall_score(pred, y_test)`처럼 순서를 바꾸면 정밀도가 나와요.',
            hints=['`recall = recall_score(y_test, pred)`로 바꿔요.'],
            wrong=[('recall = precision_score(y_test, pred)', 'recall = recall_score(pred, y_test)')]),
        buy('threshold', '확률의 기준값을 옮겨요',
            '`predict_proba`는 행마다 [0일 확률, 1일 확률]을 줘요. '
            '`proba[:, 1]`은 모든 행의 1일 확률이에요.\n'
            '기준값(threshold)은 1과 0을 가르는 확률이에요. `predict`는 0.5를 써요.\n'
            '기준값을 낮추면 1이라고 더 자주 답해요.',
            '먼저 실행하세요. 확률 세 줄, 1이라고 답한 수, 재현율, 정밀도 순서로 나와요.\n'
            'threshold를 0.3과 0.7 중 재현율이 오르는 쪽으로 바꾸세요.\n'
            '헷갈리면 둘 다 해 보고 비교해도 돼요.\n'
            '재현율이 오를 때 정밀도는 어떻게 되나요?',
            '''
            from sklearn.linear_model import LogisticRegression
            from sklearn.metrics import precision_score, recall_score
            ''',
            LOGISTIC + code('''
            # 행마다 [0일 확률, 1일 확률]이에요. 앞의 세 행을 봐요.
            proba = model.predict_proba(X_test)
            print(proba[:3].round(2))
            # 모든 행에서 1번 열, 곧 1일 확률만 꺼내요.
            p1 = proba[:, 1]
            # 기준값이에요. 1일 확률이 이 값 이상이면 1로 답해요.
            threshold = 0.5
            # 비교 결과 True/False를 astype(int)로 1과 0으로 바꿔요.
            pred = (p1 >= threshold).astype(int)
            # 1이라고 답한 수와 재현율이에요.
            print(pred.sum())
            print(recall_score(y_test, pred))
            # 1이라고 답한 행이 없으면 정밀도를 0으로 쳐요.
            print(precision_score(y_test, pred, zero_division=0))
            '''),
            'threshold = 0.5', 'threshold = 0.3', compare=['pred'],
            caution='`proba[:, 0]`을 쓰면 0일 확률로 1을 고르게 돼요.',
            hints=['`threshold = 0.3`으로 바꿔요. 낮출수록 1이라고 자주 답해요.'],
            wrong=[('threshold = 0.5', 'threshold = 0.7'),
                   ('p1 = proba[:, 1]', 'p1 = proba[:, 0]')]),
        members('three-grades', '종류가 셋이면 종류마다 읽어요',
            '종류가 셋이어도 fit과 predict 쓰는 법은 같아요.\n'
            '재현율은 종류마다 따로 나와요. 이걸 어떻게 묶을지 `average`로 정해요.\n'
            '`average=None`은 묶지 않고 종류마다 하나씩 돌려줘요.',
            '자, 이번엔 회원 등급 bronze, silver, gold를 맞혀요.\n'
            '먼저 실행해서 오류의 마지막 줄을 읽으세요. multiclass는 종류가 셋 이상이라는 뜻이에요. '
            "기본값 `average='binary'`는 두 종류일 때만 써요.\n"
            'recall_score 괄호 끝에 `, average=None`을 넣고 다시 실행하세요. '
            'micro·macro·weighted는 값 하나로 묶어서 이번엔 안 써요.\n'
            '값은 `model.classes_` 순서예요. 이름의 abc 순서라 위 등급 순서와 달라요. '
            '재현율이 가장 낮은 등급을 찾아봐요. 그 등급을 가장 자주 놓쳤어요.',
            '''
            from sklearn.linear_model import LogisticRegression
            from sklearn.metrics import accuracy_score, recall_score
            ''',
            LOGISTIC + code('''
            pred = model.predict(X_test)
            # 예측은 등급 이름으로 나와요. 앞의 다섯 개를 봐요.
            print(pred[:5])
            print(accuracy_score(y_test, pred))
            # 모델이 배운 종류의 순서예요.
            print(model.classes_)
            # 종류마다 재현율을 구해요.
            recall = recall_score(y_test, pred)
            print(recall)
            '''),
            'recall_score(y_test, pred)', 'recall_score(y_test, pred, average=None)',
            compare=['pred', 'recall'],
            caution="`average='micro'`를 쓰면 정확도와 같은 값 하나만 나와요.",
            hints=['`recall = recall_score(y_test, pred, average=None)`로 바꿔요.'],
            wrong=[('recall_score(y_test, pred)', "recall_score(y_test, pred, average='macro')"),
                   ('recall_score(y_test, pred)', "recall_score(y_test, pred, average='micro')"),
                   ('recall_score(y_test, pred)', 'recall_score(pred, y_test, average=None)')]),
        buy('accuracy-trap', '도전 · 정확도만 높은 모델 가려내기',
            '정확도는 많은 쪽만 맞혀도 높게 나와요.\n'
            '재현율을 함께 보면 1을 실제로 찾는 모델이 드러나요.\n'
            '기준 모델과 같은 테스트 자료로 견줘야 공정해요.',
            '표에 재현율 열 recall을 더하세요. 값은 세 모델 순서대로예요.\n'
            '그다음 표를 재현율이 높은 모델부터 정렬하세요.\n'
            '정확도 순위와 재현율 순위를 견줘 보세요.',
            '''
            from sklearn.dummy import DummyClassifier
            from sklearn.linear_model import LogisticRegression
            from sklearn.metrics import accuracy_score, recall_score
            from sklearn.tree import DecisionTreeClassifier
            ''',
            '''
            # 세 모델을 같은 훈련 자료로 배우고 같은 테스트로 예측해요.
            # fit은 모델 자신을 돌려줘서 predict를 바로 이어 쓸 수 있어요.
            base_pred = DummyClassifier(strategy='most_frequent').fit(X_train, y_train).predict(X_test)
            logistic_pred = LogisticRegression(max_iter=1000).fit(X_train, y_train).predict(X_test)
            tree_pred = DecisionTreeClassifier(max_depth=1, random_state=42).fit(X_train, y_train).predict(X_test)
            # 테스트 정답에서 1의 비율이에요. 0과 1의 평균이라 비율이 돼요.
            print(y_test.mean())
            # 모델마다 정확도를 모아 표로 만들어요. index는 모델 이름이에요.
            table = pd.DataFrame({
                'accuracy': [accuracy_score(y_test, base_pred), accuracy_score(y_test, logistic_pred),
                             accuracy_score(y_test, tree_pred)],
            }, index=['base', 'logistic', 'tree'])
            print(table)
            ''',
            TABLE_START, TABLE_DONE, compare=['table'], challenge=True,
            caution='`ascending=False`를 빼면 재현율이 낮은 모델부터 나와요.',
            hints=["표에 'recall' 열을 더하고 `sort_values`로 정렬해요.",
                   "`'recall': [recall_score(y_test, base_pred), ...]`를 넣어요. "
                   "`print(table)` 바로 위에 `table = table.sort_values('recall', ascending=False)`를 넣어요."],
            wrong=[(TABLE_START, TABLE_DONE.replace(", ascending=False", '')),
                   (TABLE_START, TABLE_DONE.replace("sort_values('recall'", "sort_values('accuracy'")),
                   (TABLE_START, TABLE_DONE.replace('recall_score(y_test, base_pred)', 'recall_score(base_pred, y_test)')
                    .replace('recall_score(y_test, logistic_pred)', 'recall_score(logistic_pred, y_test)')
                    .replace('recall_score(y_test, tree_pred)', 'recall_score(tree_pred, y_test)'))]),
        buy('missed-buyers', '도전 · 놓친 손님 수 바로잡기',
            '1일 확률로 기준값을 옮기려면 확률의 1번 열을 써야 해요.\n'
            '혼동행렬은 정답이 앞 인자라야 행이 실제가 돼요.\n'
            '놓친 1은 실제 1행, 예측 0열의 칸이에요.',
            '기준값 0.3으로 예측할 때 놓친 구매 손님 수를 구해요.\n'
            '준비 코드는 두 군데가 틀렸어요. 고칠 곳은 직접 찾아보세요.\n'
            '주석이 말하는 일과 코드가 하는 일을 견줘 보세요.',
            '''
            from sklearn.linear_model import LogisticRegression
            from sklearn.metrics import confusion_matrix
            ''',
            LOGISTIC + code('''
            # 행마다 [0일 확률, 1일 확률]이에요.
            proba = model.predict_proba(X_test)
            # 1일 확률 열을 꺼내요.
            ''') + MISSED_START + '\n' + code('''
            print(cm)
            # 실제 1인데 0이라고 답한, 놓친 구매 손님 수예요.
            missed = cm[1, 0]
            print(missed)
            '''),
            MISSED_START, MISSED_DONE, compare=['pred', 'cm', 'missed'], challenge=True,
            caution='확률 열만 고치면 행과 열이 뒤바뀐 표가 나와요.',
            hints=['확률의 열 번호와 `confusion_matrix`의 인자 순서를 봐요.',
                   '`p1 = proba[:, 1]`, `cm = confusion_matrix(y_test, pred)`로 바꿔요.'],
            wrong=[(MISSED_START, MISSED_START.replace('proba[:, 0]', 'proba[:, 1]')),
                   (MISSED_START, MISSED_START.replace('confusion_matrix(pred, y_test)',
                                                       'confusion_matrix(y_test, pred)'))]),
    ])
