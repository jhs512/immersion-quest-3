"""One ★ 도전 과제 per chapter: a capstone that needs everything the chapter taught.

Each challenge is appended to the chapter's last unit by chapters.build(). Starter code is
minimal on purpose; the human prompt is registered here so the build check passes.
"""
from kpc_course.dsl import *
from kpc_course.prompts import PROMPTS, TAIL

CROISSANT = PD + "sales = pd.read_csv('data/croissant.csv')\n"

CHALLENGES = {
    "python": challenge('week-plan', '일주일 생산 계획표',
        intro="""
        자, 파리바게뜨 공장의 지난주 요일별 크루아상 판매량이 `sales` 딕셔너리에 있어요. 공장 규칙은 "판매량의 1.1배를 반올림해 굽는다"예요. 1장에서 배운 걸 전부 써요. 변수, 리스트, 딕셔너리, 반복, 조건, 표까지요. 그걸로 생산 계획표를 만들어요.
        """,
        goal="""
        1. `for`로 요일을 하나씩 돌아요. 요일마다 `{'요일': ..., '판매량': ..., '계획': round(판매량 * 1.1)}` 딕셔너리를 만들어요. 그걸 `plans` 리스트에 모으세요.
        2. 계획 수량의 합계를 `total_plan`에 누적하세요. `sum()`은 금지예요. 반복문 안에서 누적해요.
        3. `max()` 없이 `if`로 판매량이 가장 많은 요일을 찾아요. 그 요일을 `best_day`에 담으세요.
        4. `plans`로 `DataFrame`을 만들어 `df`에 담으세요. 마지막 줄에 `df`를 적으면 표가 떠요.

        7행 3열 표가 나오고 `best_day`가 `토`면 맞게 한 거예요.
        """,
        hint="""
        `for day, sold in sales.items():`로 키와 값을 함께 꺼내요. 최댓값 찾기는 앞에서 본 `highest` 패턴 그대로예요. 반복 안에서 `best_day = day`도 같이 갱신하면 돼요.
        """,
        starter="import pandas as pd\n\nsales = {'월': 412, '화': 388, '수': 455, '목': 430, '금': 520, '토': 610, '일': 580}\nplans = []\ntotal_plan = 0\n# plans, total_plan, best_day, df를 만드세요\n",
        solution="import pandas as pd\n\nsales = {'월': 412, '화': 388, '수': 455, '목': 430, '금': 520, '토': 610, '일': 580}\nplans = []\ntotal_plan = 0\nbest_day = None\nbest_sold = 0\nfor day, sold in sales.items():\n    plan = round(sold * 1.1)\n    plans.append({'요일': day, '판매량': sold, '계획': plan})\n    total_plan += plan\n    if sold > best_sold:\n        best_sold = sold\n        best_day = day\ndf = pd.DataFrame(plans)\nprint(total_plan, best_day)\ndf\n",
        check="assert [p['요일'] for p in s['plans']] == ['월', '화', '수', '목', '금', '토', '일']\nassert [p['계획'] for p in s['plans']] == [round(v * 1.1) for v in s['sales'].values()]\nassert s['total_plan'] == sum(round(v * 1.1) for v in s['sales'].values())\nassert s['best_day'] == '토'\nassert s['df'].shape == (7, 3) and list(s['df'].columns) == ['요일', '판매량', '계획']"),

    "pandas": challenge('croissant-clean', '크루아상 판매 기록 정리',
        intro="""
        `data/croissant.csv`는 빵 공장의 8주치 일별 판매 기록이에요. 열은 날짜·요일·날씨·기온·판매량이고 56행이에요. 판매량이 비어 있는 날이 있어요. 2장에서 배운 읽기, 결측, 조건 선택, 저장을 한 번에 써요.
        """,
        goal="""
        1. 판매량의 결측 개수를 `int`로 `n_missing`에 담으세요.
        2. 판매량 결측을 **중앙값**으로 채운 새 표를 `filled`에 담으세요. 원본 `sales`는 그대로 둬요.
        3. `filled`에서 날씨가 `비`인 행만 `rainy`에 담으세요.
        4. `filled`에서 요일이 `토`나 `일`인 행을 골라요. 그 판매량 평균을 `weekend_mean`에 담으세요.
        5. `filled`를 `croissant_clean.csv`로 저장하세요(`index=False`). 다시 읽어 `saved`에 담으세요.

        `n_missing`이 2, `rainy`가 15행, `saved`가 56행 5열이면 맞게 한 거예요.
        """,
        hint="""
        결측 세기는 `isna().sum()`이에요. 채우기는 `fillna(중앙값)`을 **새 변수**에 담아요. 조건은 참·거짓 마스크고요. 토·일은 `isin(['토', '일'])`가 편하죠. 저장은 앞 단원의 `to_csv(index=False)`예요.
        """,
        starter=CROISSANT + "# n_missing, filled, rainy, weekend_mean, saved를 만드세요\n",
        solution=CROISSANT + "n_missing = int(sales['판매량'].isna().sum())\nfilled = sales.copy()\nfilled['판매량'] = filled['판매량'].fillna(sales['판매량'].median())\nrainy = filled[filled['날씨'] == '비']\nweekend_mean = filled[filled['요일'].isin(['토', '일'])]['판매량'].mean()\nfilled.to_csv('croissant_clean.csv', index=False)\nsaved = pd.read_csv('croissant_clean.csv')\nprint(n_missing, len(rainy), round(weekend_mean, 1), saved.shape)\n",
        check="assert s['n_missing'] == 2 and s['sales']['판매량'].isna().sum() == 2\nassert s['filled']['판매량'].isna().sum() == 0 and abs(s['filled']['판매량'].sum() - 25174) < 1e-6\nassert len(s['rainy']) == 15 and (s['rainy']['날씨'] == '비').all()\nassert abs(s['weekend_mean'] - 557.5625) < 1e-6\nassert s['saved'].shape == (56, 5) and list(s['saved'].columns) == ['날짜', '요일', '날씨', '기온', '판매량']"),

    "eda": challenge('family-survival', '가족 동반 여부별 생존',
        intro="""
        표에 없는 열을 직접 만들어 집계해 봐요. 그게 탐색의 완성이죠. 형제·배우자 수와 부모·자녀 수를 더해서 "가족과 함께 탔는가" 열을 새로 만들어요. 3장에서 배운 타깃, 분모, `groupby`, 교차표를 다 쓰게 돼요.
        """,
        goal="""
        1. `형제배우자 + 부모자녀`가 1 이상이면 `True`인 열 `가족동반`을 `titanic`에 추가하세요.
        2. `가족동반`으로 `생존`을 묶어요. `count`, `sum`, `mean`을 `family_summary`에 담으세요.
        3. `객실등급`과 `가족동반`으로 묶어 생존율을 구하세요. `unstack('가족동반')`으로 펼치면 3행 2열 표예요. `by_class`에 담아 마지막 줄에 적으세요.

        `family_summary`의 `count` 합이 1309이고 `by_class`가 3행 2열이면 맞게 한 거예요. 가족과 함께 탄 쪽의 생존율이 등급마다 어떻게 다른지 읽어 보세요.
        """,
        hint="""
        새 열은 `titanic['가족동반'] = (titanic['형제배우자'] + titanic['부모자녀']) >= 1`이에요. 두 열로 묶기는 `groupby(['객실등급', '가족동반'])['생존'].mean()` 뒤에 `unstack`이에요.
        """,
        starter=TI + "# 가족동반 열, family_summary, by_class를 만드세요\n",
        solution=TI + "titanic['가족동반'] = (titanic['형제배우자'] + titanic['부모자녀']) >= 1\nfamily_summary = titanic.groupby('가족동반')['생존'].agg(['count', 'sum', 'mean'])\nby_class = titanic.groupby(['객실등급', '가족동반'])['생존'].mean().unstack('가족동반')\nprint(family_summary)\nby_class\n",
        check="assert s['titanic']['가족동반'].dtype == bool and s['titanic']['가족동반'].sum() == int(((s['titanic']['형제배우자'] + s['titanic']['부모자녀']) >= 1).sum())\nassert list(s['family_summary'].columns) == ['count', 'sum', 'mean'] and s['family_summary']['count'].sum() == 1309 and s['family_summary']['sum'].sum() == 500\nassert s['by_class'].shape == (3, 2) and list(s['by_class'].index) == [1, 2, 3]\nimport numpy as np\n\nassert np.allclose(s['by_class'].to_numpy(), s['titanic'].groupby(['객실등급', '가족동반'])['생존'].mean().unstack('가족동반').to_numpy())"),

    "visualization": challenge('two-charts', '한 장에 두 그림',
        intro="""
        보고서 한 장엔 보통 그래프가 둘 이상 들어가요. `plt.subplots(1, 2)`는 종이 한 장에 그래프 영역 두 개를 나란히 만들어요. 4장에서 배운 묶음 막대와 히스토그램을 한 종이(Figure)에 그려요.
        """,
        goal="""
        1. `fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4))`로 영역 두 개를 만드세요.
        2. 왼쪽 `ax1`: `객실등급`×`성별` 생존율을 퍼센트로 펼쳐 `wide`에 담으세요. `wide.plot.bar(ax=ax1, ylim=(0, 100), rot=0)`으로 그려요. y축 이름 `생존율 (%)`을 붙여요.
        3. 오른쪽 `ax2`: 나이가 기록된 승객의 나이를 `bins=20` 히스토그램으로 그리세요(`ax=ax2`).
        4. 두 영역에 제목을 붙이세요. `plt.show()`로 띄워요.

        왼쪽에 막대 여섯 개, 오른쪽에 막대 스무 개가 보이면 맞게 한 거예요.
        """,
        hint="""
        `wide = titanic.groupby(['객실등급', '성별'])['생존'].mean().unstack('성별') * 100`이에요. 히스토그램은 `sns.histplot(data=known_age, x='나이', bins=20, ax=ax2)`예요. `ax=ax2`가 빠지면 엉뚱한 곳에 그려져요.
        """,
        starter=TI + PLOT + "# fig, ax1, ax2와 wide를 만들고 두 그림을 그리세요\n",
        solution=TI + PLOT + "wide = titanic.groupby(['객실등급', '성별'])['생존'].mean().unstack('성별') * 100\nknown_age = titanic[titanic['나이'].notna()]\nfig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4))\nwide.plot.bar(ax=ax1, ylim=(0, 100), rot=0)\nax1.set_ylabel('생존율 (%)')\nax1.set_title('등급과 성별에 따른 생존율')\nsns.histplot(data=known_age, x='나이', bins=20, ax=ax2)\nax2.set_title('나이 분포')\nplt.show()\n",
        check="assert s['fig'].axes[0] is s['ax1'] and s['fig'].axes[1] is s['ax2']\nassert len(s['ax1'].patches) == 6 and s['ax1'].get_ylim()[1] == 100 and s['ax1'].get_ylabel() == '생존율 (%)'\nassert len(s['ax2'].patches) == 20 and abs(sum(p.get_height() for p in s['ax2'].patches) - 1046) < 1e-6\nassert s['ax1'].get_title() and s['ax2'].get_title()\nassert s['wide'].shape == (3, 2) and s['wide'].to_numpy().max() <= 100"),

    "modeling": challenge('full-comparison', '기준과 세 모델, 처음부터 끝까지',
        intro="""
        5장을 한 번에 복습해요. 이번에는 준비 코드가 거의 없어요. 자료 읽기부터 입력·정답 분리, 층화 분할, 손질기, 네 모델 비교표까지 직접 써요. 분할보다 손질이 먼저 오면 조용한 누수가 생겨요.
        """,
        goal="""
        1. `data/titanic.csv`를 읽으세요. `features = ['객실등급', '성별', '나이', '형제배우자', '부모자녀', '요금', '탑승항구']`로 `X`를 만들어요. `y`는 정수로 바꾼 `생존`이에요.
        2. `train_test_split(test_size=0.2, stratify=y, random_state=42)`로 나누세요.
        3. `ColumnTransformer`를 `preprocessor`에 만드세요. 숫자 열은 중앙값 채우기+표준화예요. 글자 열은 최빈값 채우기+One-hot(`handle_unknown='ignore'`)이에요.
        4. `models`에 넷을 넣으세요. `Dummy`는 가장 많은 답 찍기, `Logistic`은 반복 2000회예요. `Tree`는 깊이 5에 난수 42, `Forest`는 트리 50개에 깊이 5, 난수 42예요.
        5. 모델마다 `Pipeline([('prepare', preprocessor), ('model', m)])`로 학습·예측하세요. `accuracy`, `f1` 두 열짜리 `results` 표를 만드세요.
        6. F1이 가장 높은 모델 이름을 `best_model`에 담으세요.

        `Dummy`의 정확도가 162/262이고 `best_model`이 `Dummy`가 아니면 맞게 한 거예요.
        """,
        hint="""
        앞 단원의 `make_preprocessor()`를 떠올리세요. 수치형은 `['객실등급', '나이', '형제배우자', '부모자녀', '요금']`이에요. 범주형은 `['성별', '탑승항구']`고요. `Pipeline`은 모델마다 새로 만들어야 해요. `preprocessor`는 같은 걸 다시 써도 돼요. 매번 같은 훈련 자료로 다시 `fit`되거든요. 마지막은 `best_model = results['f1'].idxmax()`예요.
        """,
        starter="import pandas as pd\nfrom sklearn.model_selection import train_test_split\nfrom sklearn.compose import ColumnTransformer\nfrom sklearn.impute import SimpleImputer\nfrom sklearn.pipeline import Pipeline\nfrom sklearn.preprocessing import OneHotEncoder, StandardScaler\nfrom sklearn.dummy import DummyClassifier\nfrom sklearn.linear_model import LogisticRegression\nfrom sklearn.tree import DecisionTreeClassifier\nfrom sklearn.ensemble import RandomForestClassifier\nfrom sklearn.metrics import accuracy_score, f1_score\n# X, y, 분할, preprocessor, models, results, best_model을 만드세요\n",
        solution="import pandas as pd\nfrom sklearn.model_selection import train_test_split\nfrom sklearn.compose import ColumnTransformer\nfrom sklearn.impute import SimpleImputer\nfrom sklearn.pipeline import Pipeline\nfrom sklearn.preprocessing import OneHotEncoder, StandardScaler\nfrom sklearn.dummy import DummyClassifier\nfrom sklearn.linear_model import LogisticRegression\nfrom sklearn.tree import DecisionTreeClassifier\nfrom sklearn.ensemble import RandomForestClassifier\nfrom sklearn.metrics import accuracy_score, f1_score\n\ntitanic = pd.read_csv('data/titanic.csv')\nfeatures = ['객실등급', '성별', '나이', '형제배우자', '부모자녀', '요금', '탑승항구']\nX = titanic[features].copy()\ny = titanic['생존'].astype(int)\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)\npreprocessor = ColumnTransformer(\n    [\n        ('numeric', Pipeline([('fill', SimpleImputer(strategy='median')), ('scale', StandardScaler())]), ['객실등급', '나이', '형제배우자', '부모자녀', '요금']),\n        ('category', Pipeline([('fill', SimpleImputer(strategy='most_frequent')), ('encode', OneHotEncoder(handle_unknown='ignore'))]), ['성별', '탑승항구']),\n    ]\n)\nmodels = {\n    'Dummy': DummyClassifier(strategy='most_frequent'),\n    'Logistic': LogisticRegression(max_iter=2000),\n    'Tree': DecisionTreeClassifier(max_depth=5, random_state=42),\n    'Forest': RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42),\n}\nrows = {}\nfor name, model in models.items():\n    pipeline = Pipeline([('prepare', preprocessor), ('model', model)])\n    pipeline.fit(X_train, y_train)\n    pred = pipeline.predict(X_test)\n    rows[name] = {'accuracy': accuracy_score(y_test, pred), 'f1': f1_score(y_test, pred)}\nresults = pd.DataFrame(rows).T\nbest_model = results['f1'].idxmax()\nprint(best_model)\nresults\n",
        check="assert s['X'].shape == (1309, 7) and int(s['y'].sum()) == 500\nassert len(s['X_train']) == 1047 and len(s['X_test']) == 262 and abs(s['y_train'].mean() - s['y_test'].mean()) < 0.02\nassert set(s['results'].index) == {'Dummy', 'Logistic', 'Tree', 'Forest'} and list(s['results'].columns) == ['accuracy', 'f1']\nassert abs(s['results'].loc['Dummy', 'accuracy'] - 162 / 262) < 1e-9 and s['results'].loc['Dummy', 'f1'] == 0\nassert s['best_model'] != 'Dummy' and s['best_model'] == s['results']['f1'].idxmax()\nassert (s['results'].loc[['Logistic', 'Tree', 'Forest'], 'accuracy'] > 162 / 262).all()"),

    "credit": challenge('threshold-cost', '기준값과 비용',
        intro="""
        은행은 지표가 아니라 돈으로 결정해요. 부도를 놓치면(FN) 100만 원을 떼여요. 멀쩡한 고객에게 경고하면(FP) 5만 원이 들어요. 6장에서 배운 확률, 기준값, 혼동행렬로 두 기준값의 비용을 비교해요.
        """,
        goal="""
        1. 준비 코드의 `model`로 테스트 부도 확률을 구해 `probabilities`에 담으세요. `predict_proba(...)[:, 1]`이에요.
        2. 기준값 0.5와 0.3으로 예측을 만드세요. `confusion_matrix(y_test, pred, labels=[0, 1])`로 혼동행렬을 만들어요. 0.5는 `cm_05`, 0.3은 `cm_03`에 담으세요.
        3. 비용은 `FN × 1_000_000 + FP × 50_000`이에요. `cost_05`, `cost_03`에 담으세요(정수).
        4. 비용이 더 싼 기준값(0.5 또는 0.3)을 `cheaper`에 담으세요. 두 비용을 출력해요.

        혼동행렬의 FP는 `[0, 1]` 칸, FN은 `[1, 0]` 칸이에요. 어느 쪽이 싼지, 그 차이가 얼마인지 보세요.
        """,
        hint="""
        예측은 `pred_05 = (probabilities >= 0.5).astype(int)`처럼 만들어요. 비용은 `int(cm[1, 0]) * 1_000_000 + int(cm[0, 1]) * 50_000`이에요. 마지막은 `cheaper = 0.3 if cost_03 < cost_05 else 0.5`예요.
        """,
        starter=CR + "from sklearn.model_selection import train_test_split\nfrom sklearn.pipeline import Pipeline\nfrom sklearn.preprocessing import StandardScaler\nfrom sklearn.linear_model import LogisticRegression\nfrom sklearn.metrics import confusion_matrix\n\nfeatures = ['상환_9월', '신용한도', '나이']\nX = credit[features]\ny = credit[target]\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)\nmodel = Pipeline([('scale', StandardScaler()), ('model', LogisticRegression(max_iter=1000))]).fit(X_train, y_train)\n# probabilities, cm_05, cm_03, cost_05, cost_03, cheaper를 만드세요\n",
        solution=CR + "from sklearn.model_selection import train_test_split\nfrom sklearn.pipeline import Pipeline\nfrom sklearn.preprocessing import StandardScaler\nfrom sklearn.linear_model import LogisticRegression\nfrom sklearn.metrics import confusion_matrix\n\nfeatures = ['상환_9월', '신용한도', '나이']\nX = credit[features]\ny = credit[target]\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)\nmodel = Pipeline([('scale', StandardScaler()), ('model', LogisticRegression(max_iter=1000))]).fit(X_train, y_train)\nprobabilities = model.predict_proba(X_test)[:, 1]\ncm_05 = confusion_matrix(y_test, (probabilities >= 0.5).astype(int), labels=[0, 1])\ncm_03 = confusion_matrix(y_test, (probabilities >= 0.3).astype(int), labels=[0, 1])\ncost_05 = int(cm_05[1, 0]) * 1_000_000 + int(cm_05[0, 1]) * 50_000\ncost_03 = int(cm_03[1, 0]) * 1_000_000 + int(cm_03[0, 1]) * 50_000\ncheaper = 0.3 if cost_03 < cost_05 else 0.5\nprint(cost_05, cost_03, cheaper)\n",
        check="import numpy as np\n\nassert len(s['probabilities']) == len(s['y_test']) and 0 <= s['probabilities'].min() and s['probabilities'].max() <= 1\nfor name, t in (('cm_05', 0.5), ('cm_03', 0.3)):\n    cm = s[name]\n    assert cm.shape == (2, 2) and cm.sum() == len(s['y_test'])\n    assert (cm == np.array([[int(((s['probabilities'] < t) & (s['y_test'].to_numpy() == 0)).sum()), int(((s['probabilities'] >= t) & (s['y_test'].to_numpy() == 0)).sum())], [int(((s['probabilities'] < t) & (s['y_test'].to_numpy() == 1)).sum()), int(((s['probabilities'] >= t) & (s['y_test'].to_numpy() == 1)).sum())]])).all()\nassert s['cost_05'] == int(s['cm_05'][1, 0]) * 1_000_000 + int(s['cm_05'][0, 1]) * 50_000\nassert s['cost_03'] == int(s['cm_03'][1, 0]) * 1_000_000 + int(s['cm_03'][0, 1]) * 50_000\nassert s['cheaper'] == (0.3 if s['cost_03'] < s['cost_05'] else 0.5)"),

    "stock": challenge('window-rematch', '창을 바꿔 다시 겨루기',
        intro="""
        주가 챕터 전체를 한 번에 복습해요. 이번에는 이동평균 창을 5일에서 **10일**로 바꿔요. 입력 열 만들기, 시간 분리(경계 하루 빼기), 기준 모델, 릿지 비교, 보고 딕셔너리. 전부 직접 써요.
        """,
        goal="""
        1. `prices`에서 `frame`을 만드세요. 열은 여섯이에요: `close`, `return_1`, `ma10`(`rolling(10).mean()`), `lag_close_1`, `target_next_close`, `target_date`. 마지막에 `dropna()` 뒤 `.copy()`를 해요.
        2. `feature_columns = ['close', 'return_1', 'ma10', 'lag_close_1']`로 `X`, `y`를 만드세요. 마지막 80행이 테스트예요. 훈련은 입력 날짜와 `target_date`가 **모두** `test_start` 전인 행만 써요.
        3. 기준 예측(오늘 종가)의 MAE를 `baseline_mae`에 담으세요. `StandardScaler`+`Ridge(alpha=1)` 파이프라인의 테스트 MAE는 `ridge_mae`에 담으세요.
        4. `report` 딕셔너리를 만들어 출력하세요. 내용은 `{'window': 10, 'rows': len(frame), 'baseline_mae': ..., 'ridge_mae': ..., 'improved': ridge_mae < baseline_mae}`예요.

        `frame`이 391행, 훈련 310행, 테스트 80행이면 분리가 맞은 거예요. `improved`가 `False`여도 그대로 둬요.
        """,
        hint="""
        앞에서 만든 여섯 열에서 `rolling(5)`만 `rolling(10)`으로 바꾸세요. 처음 아홉 행이 비어 391행이 남아요. 앞 단원의 `train_mask = (frame.index < test_start) & (frame['target_date'] < test_start)`를 그대로 쓰세요.
        """,
        starter=ST + "from sklearn.pipeline import Pipeline\nfrom sklearn.preprocessing import StandardScaler\nfrom sklearn.linear_model import Ridge\nfrom sklearn.metrics import mean_absolute_error\n# frame, X_train, X_test, y_train, y_test, baseline_mae, ridge_mae, report를 만드세요\n",
        solution=ST + "from sklearn.pipeline import Pipeline\nfrom sklearn.preprocessing import StandardScaler\nfrom sklearn.linear_model import Ridge\nfrom sklearn.metrics import mean_absolute_error\n\nframe = pd.DataFrame(index=prices.index)\nframe['close'] = prices['종가']\nframe['return_1'] = prices['종가'].pct_change()\nframe['ma10'] = prices['종가'].rolling(10).mean()\nframe['lag_close_1'] = prices['종가'].shift(1)\nframe['target_next_close'] = prices['종가'].shift(-1)\nframe['target_date'] = pd.Series(prices.index, index=prices.index).shift(-1)\nframe = frame.dropna().copy()\nfeature_columns = ['close', 'return_1', 'ma10', 'lag_close_1']\nX = frame[feature_columns]\ny = frame['target_next_close']\ntest_start = frame.index[-80]\ntrain_mask = (frame.index < test_start) & (frame['target_date'] < test_start)\ntest_mask = frame.index >= test_start\nX_train, X_test = X.loc[train_mask], X.loc[test_mask]\ny_train, y_test = y.loc[train_mask], y.loc[test_mask]\nbaseline_mae = mean_absolute_error(y_test, X_test['close'].to_numpy())\nmodel = Pipeline([('scale', StandardScaler()), ('model', Ridge(alpha=1))]).fit(X_train, y_train)\nridge_mae = mean_absolute_error(y_test, model.predict(X_test))\nreport = {'window': 10, 'rows': len(frame), 'baseline_mae': baseline_mae, 'ridge_mae': ridge_mae, 'improved': ridge_mae < baseline_mae}\nprint(report)\n",
        check="import numpy as np\n\nassert len(s['frame']) == 391 and 'ma10' in s['frame'].columns and 'ma5' not in s['frame'].columns\nassert len(s['X_train']) == 310 and len(s['X_test']) == 80 and list(s['X_train'].columns) == ['close', 'return_1', 'ma10', 'lag_close_1']\nassert s['frame'].loc[s['X_train'].index, 'target_date'].max() < s['X_test'].index.min()\nassert abs(s['baseline_mae'] - float(np.abs(s['y_test'].to_numpy() - s['X_test']['close'].to_numpy()).mean())) < 1e-6\nr = s['report']\nassert r['window'] == 10 and r['rows'] == 391 and abs(r['baseline_mae'] - s['baseline_mae']) < 1e-9 and abs(r['ridge_mae'] - s['ridge_mae']) < 1e-9 and r['improved'] == (s['ridge_mae'] < s['baseline_mae'])"),
}

PROMPTS.update({
    'week-plan': ("파이썬. sales = {'월': 412, ..., '일': 580} 딕셔너리. for로 요일마다 {'요일','판매량','계획': round(판매량*1.1)} 딕셔너리를 plans에 모으고, 계획 합계는 total_plan에 누적(sum 금지), 판매량 최대 요일은 if로 best_day에(max 금지). plans로 DataFrame df 만들어 마지막 줄에 df." + TAIL,
                  "- `sum 금지`, `max 금지` → 1장에서 배운 반복·조건을 쓰게 하는 제약.\n- `{'요일', '판매량', '계획'}` → 딕셔너리 키가 그대로 열 이름이 된다.\n- `마지막 줄에 df` → 앱이 표로 보여 준다."),
    'croissant-clean': ("pandas. data/croissant.csv(날짜·요일·날씨·기온·판매량). 판매량 결측 개수를 int로 n_missing, 결측을 중앙값으로 채운 새 표를 filled(원본 sales는 그대로), 날씨가 '비'인 행을 rainy, 요일이 토·일인 행의 판매량 평균을 weekend_mean, filled를 croissant_clean.csv(index=False)로 저장 후 다시 읽어 saved." + TAIL,
                        "- `원본 sales는 그대로` → inplace 금지. 검사기가 원본을 본다.\n- `isin` 대신 `토·일` → 조건을 말로 적어도 AI가 isin을 고른다.\n- `index=False` → 행 번호 열 방지."),
    'family-survival': ("pandas. titanic DataFrame. (형제배우자 + 부모자녀) >= 1 이면 True인 열 가족동반을 추가. 가족동반으로 groupby한 생존의 agg(['count','sum','mean'])을 family_summary에, ['객실등급','가족동반'] groupby 생존 mean을 unstack('가족동반')해서 by_class에. 마지막 줄에 by_class." + TAIL,
                        "- `>= 1 이면 True` → 새 열의 규칙을 식으로.\n- `count·sum·mean` → 분모를 함께.\n- `unstack('가족동반')` → 3행 2열 교차표."),
    'two-charts': ("pandas + matplotlib + seaborn. fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4)). ax1: 객실등급×성별 생존율 unstack('성별')*100을 wide에 담아 wide.plot.bar(ax=ax1, ylim=(0,100), rot=0), ylabel '생존율 (%)'. ax2: 나이 결측 제외 후 sns.histplot(x='나이', bins=20, ax=ax2). 둘 다 제목 붙이고 plt.show()." + TAIL,
                   "- `subplots(1, 2)` → 종이 하나에 영역 둘.\n- `ax=ax1`, `ax=ax2` → 어느 영역에 그릴지. 빠지면 엉뚱한 곳에 그린다.\n- `ylim = (0, 100)`과 `*100` → 퍼센트 축 한 세트."),
    'full-comparison': ("scikit-learn. data/titanic.csv에서 features 7개로 X, y(생존 int). train_test_split(test_size=0.2, stratify=y, random_state=42). ColumnTransformer: 수치형 5열은 SimpleImputer(median)+StandardScaler, 범주형(성별, 탑승항구)은 SimpleImputer(most_frequent)+OneHotEncoder(handle_unknown='ignore'). models = Dummy(most_frequent), Logistic(max_iter=2000), Tree(max_depth=5, random_state=42), Forest(n_estimators=50, max_depth=5, random_state=42). 각각 Pipeline([('prepare', preprocessor), ('model', m)])로 fit/predict해 accuracy, f1 두 열 DataFrame results. best_model = results['f1'].idxmax()." + TAIL,
                        "- `stratify`, `random_state` → 재현 가능한 공정한 분할.\n- `ColumnTransformer` 안의 `SimpleImputer`/`OneHotEncoder` → 기준은 훈련에서만 정해진다.\n- `Dummy`가 표의 한 행 → 기준선 없이는 점수가 뜻이 없다."),
    'threshold-cost': ("scikit-learn. 학습된 model, X_test, y_test. model.predict_proba(X_test)[:, 1]을 probabilities에. 기준값 0.5와 0.3으로 (p >= t).astype(int) 예측을 만들어 confusion_matrix(y_test, pred, labels=[0,1])를 cm_05, cm_03에. 비용 = cm[1,0](FN)*1_000_000 + cm[0,1](FP)*50_000 을 cost_05, cost_03에(int). 싼 쪽 기준값을 cheaper에." + TAIL,
                       "- `[:, 1]` → 부도일 확률 열.\n- `labels = [0, 1]` → 혼동행렬 칸 위치 고정. FN은 [1,0], FP는 [0,1].\n- 비용식을 숫자로 → 기준값은 비용을 아는 사람이 정한다."),
    'window-rematch': ("pandas + scikit-learn. prices(날짜 인덱스, 종가). frame에 close, return_1(pct_change), ma10(rolling(10).mean()), lag_close_1(shift(1)), target_next_close(shift(-1)), target_date(날짜 shift(-1)) 만들고 dropna().copy(). feature_columns=['close','return_1','ma10','lag_close_1']. test_start = frame.index[-80], 훈련은 입력 날짜와 target_date 둘 다 test_start 전. baseline_mae = MAE(y_test, X_test['close']), StandardScaler+Ridge(alpha=1) 파이프라인 MAE를 ridge_mae. report = {'window':10,'rows':len(frame),'baseline_mae','ridge_mae','improved': ridge_mae < baseline_mae}. improved가 False여도 그대로." + TAIL,
                       "- `rolling(10)` → 창 크기만 바꾼 재실험. 다른 조건은 같아야 비교된다.\n- `target_date도 test_start 전` → 경계 하루 누수 방지.\n- `False여도 그대로` → 결과를 고르지 않는다."),
})
