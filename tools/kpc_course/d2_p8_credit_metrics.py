"""네 지표와 확률 기준"""
from kpc_course.dsl import *

CREDIT_SPLIT = CR + "from sklearn.model_selection import train_test_split\nfrom sklearn.pipeline import Pipeline\nfrom sklearn.preprocessing import StandardScaler\n"

UNIT = unit('credit-metrics', '네 지표와 확률 기준', [
    coding('manual-metrics', '혼동행렬로 네 지표 손계산',
        intro="""
        자, 이 단원은 개념 미션 없이 문제 안에서 설명해요. 앞 단원의 부도율은 약 22%였죠? 뒤집으면 **전원 "정상"이라고 찍어도 정확도 78%**라는 뜻이에요. 이렇게 한쪽이 훨씬 많은 자료를 불균형 자료라고 해요. 그런데 그 모델은 부도 고객을 한 명도 못 찾아요. 카드사가 원하는 건 정확도가 아니에요. "부도 날 사람을 미리 찾는 것"이죠. 정확도 하나로는 모델을 평가할 수 없어요. 그래서 맞힘과 틀림을 네 칸으로 나눠 봐요.

        부도(1)를 양성(positive)이라고 부를게요. 실제와 예측을 표로 놓으면 이렇게 돼요. 이 표가 혼동행렬(confusion matrix)이에요.

        | | 예측: 정상(0) | 예측: 부도(1) |
        | --- | --- | --- |
        | **실제: 정상(0)** | TN (맞게 정상) | FP (멀쩡한 사람을 부도로 경고) |
        | **실제: 부도(1)** | FN (부도를 놓침) | TP (맞게 부도) |

        네 칸에서 지표 네 개가 나와요.

        - **정확도**(accuracy)는 전체 중 맞힌 비율이에요. (TP+TN)/전체.
        - **정밀도**(precision)는 부도 경고 중 진짜 부도였던 비율이에요. TP/(TP+FP). 경고의 신뢰도죠.
        - **재현율**(recall)은 진짜 부도 중 미리 찾아낸 비율이에요. TP/(TP+FN). 놓치지 않은 정도죠.
        - **F1**은 정밀도와 재현율을 하나로 합친 점수예요. 둘 다 높아야 높아져요.

        전원 정상으로 찍은 모델은 TP가 0이에요. 그래서 정밀도·재현율·F1이 전부 0이에요. 정확도 78%의 정체가 이렇게 드러나요.

        어느 지표가 중요한지는 실수의 비용에 달렸어요. 부도를 놓치면(FN) 돈을 떼이죠. 멀쩡한 고객에게 경고하면(FP) 고객을 잃고요. 떼이는 쪽이 더 아프면 재현율을 더 봐요. 고객을 잃는 쪽이 더 아프면 정밀도를 더 보고요.
        """,
        goal="""
        ```comic-gen
        제목: 경고를 보낸 100명, 실제 부도 50명
        등장인물:
          준호:
            그림: 사람
            이름표: 준호 · 은행 직원
            외형: {머리색: "#303746", 옷색: "#b88646"}
          강사:
            그림: 사람
            이름표: 강사
            외형: {옷: 재킷, 옷색: "#5379a7", 안경: true}
        컷:
          - 인물: [{식별자: 준호, 표정: 어리둥절}, 강사]
            대사:
              - {화자: 준호, 상대: 강사, 내용: "100명에게 부도 경고를 보냈는데 20명만 진짜였어요."}
              - {화자: 강사, 상대: 준호, 내용: "보낸 경고 중 맞은 비율이 정밀도예요. 20/100."}
          - 구성: 이전
            인물: [{식별자: 준호, 표정: 보통}, {식별자: 강사, 손모양: 가리키는손}]
            대사:
              - {화자: 준호, 상대: 강사, 내용: "실제 부도는 50명이었는데 20명만 잡았고요."}
              - {화자: 강사, 상대: 준호, 내용: "진짜 부도 중 잡은 비율이 재현율이에요. 20/50."}
          - 구성: 이전
            인물: [{식별자: 준호, 표정: 기쁨}, {식별자: 강사, 손모양: null}]
            대사:
              - {화자: 준호, 상대: 강사, 내용: "놓친 30명이 돈을 떼이는 쪽이네요."}
              - {화자: 강사, 상대: 준호, 내용: "그래서 은행은 재현율을 먼저 봐요."}
        ```

        작은 예로 공식을 손에 익혀요. `tp, fp, fn, tn`이 준비돼 있어요. 위에서 본 공식대로 `precision`, `recall`, `accuracy`를 계산해 담고 출력하세요.

        세 값이 모두 약 0.667이면 맞게 한 거예요.
        """,
        hint="""
        정밀도의 분모는 "부도라고 예측한 수" `tp + fp`예요. 재현율의 분모는 "진짜 부도 수" `tp + fn`이고요. 정확도는 `(tp + tn) / (tp + fp + fn + tn)`이에요.
        """,
        starter='tp, fp, fn, tn = 2, 1, 1, 2\n# precision, recall, accuracy를 계산하고 출력하세요\n',
        solution='tp, fp, fn, tn = 2, 1, 1, 2\nprecision = tp / (tp + fp)\nrecall = tp / (tp + fn)\naccuracy = (tp + tn) / (tp + fp + fn + tn)\nprint(precision, recall, accuracy)\n',
        check="assert abs(s['precision'] - 2 / 3) < 1e-12 and abs(s['recall'] - 2 / 3) < 1e-12 and abs(s['accuracy'] - 2 / 3) < 1e-12"),
    coding('metrics-matrix', '같은 계산을 함수로',
        goal="""
        손으로 한 계산을 이번엔 `scikit-learn` 함수로 해요. 정답 `y_true`와 예측 `y_pred` 여섯 개가 준비돼 있어요. `accuracy_score`, `precision_score`, `recall_score`, `f1_score`로 네 값을 구하세요. 같은 이름의 키로 `metrics` 딕셔너리에 담아요. `confusion_matrix(y_true, y_pred, labels=[0, 1])`는 `matrix`에 담고요. 둘 다 출력하세요.

        `matrix`가 `[[2, 1], [1, 2]]`면 TN 2, FP 1, FN 1, TP 2예요. 앞 미션과 같은 상황이죠. 네 지표도 같은 값이 나와야 해요.
        """,
        hint="""
        지표 함수는 전부 `(정답, 예측)` 순서로 넣어요. `metrics = {'accuracy': accuracy_score(y_true, y_pred), 'precision': precision_score(y_true, y_pred), ...}`처럼 적어요. 혼동행렬의 `labels = [0, 1]`은 행·열 순서를 0, 1로 고정해요.
        """,
        starter='from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix\n\ny_true = [0, 0, 1, 1, 1, 0]\ny_pred = [0, 1, 1, 0, 1, 0]\n# metrics와 matrix를 만드세요\n',
        solution="from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix\n\ny_true = [0, 0, 1, 1, 1, 0]\ny_pred = [0, 1, 1, 0, 1, 0]\nmetrics = {'accuracy': accuracy_score(y_true, y_pred), 'precision': precision_score(y_true, y_pred), 'recall': recall_score(y_true, y_pred), 'f1': f1_score(y_true, y_pred)}\nmatrix = confusion_matrix(y_true, y_pred, labels=[0, 1])\nprint(metrics)\nprint(matrix)\n",
        check="assert set(s['metrics']) == {'accuracy', 'precision', 'recall', 'f1'}\nassert all(abs(v - 2 / 3) < 1e-10 for v in s['metrics'].values())\nassert s['matrix'].tolist() == [[2, 1], [1, 2]]"),
    coding('credit-model', '부도 모델과 기준 모델을 네 지표로 비교',
        goal="""
        이제 진짜 자료예요. 준비 코드가 `상환_9월`, `신용한도`, `나이` 세 열을 입력으로 삼았어요. 훈련 자료와 테스트 자료도 나눠 뒀고요. `models`에 `Dummy`와 `Logistic`을 넣으세요. 각각 `StandardScaler`와 묶은 `Pipeline`으로 훈련하고 예측해요. 그다음 네 지표 `accuracy`, `precision`, `recall`, `f1`을 구하세요. `results` 표로 만들고요.

        기준 모델의 정확도는 78% 근처예요. 그런데 재현율은 0이에요. 로지스틱 회귀가 재현율을 얼마나 끌어올리는지 보세요. 그 대가로 정확도는 어떻게 되는지도요.
        """,
        hint="""
        앞 단원의 표 만들기 패턴 그대로예요. `for name, estimator in models.items():` 안에서 `Pipeline([('scale', StandardScaler()), ('model', estimator)])`를 만들어요. `fit`, `predict`하고 네 지표를 딕셔너리로 `rows`에 모아요. 정밀도·재현율·F1에는 `zero_division=0`을 주세요. 기준 모델처럼 TP가 0일 때 경고 없이 0이 나와요.
        """,
        starter=CREDIT_SPLIT + "from sklearn.dummy import DummyClassifier\nfrom sklearn.linear_model import LogisticRegression\nfrom sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score\n\nX = credit[['상환_9월', '신용한도', '나이']]\ny = credit[target]\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)\n# models와 results를 만드세요\n",
        solution=CREDIT_SPLIT + "from sklearn.dummy import DummyClassifier\nfrom sklearn.linear_model import LogisticRegression\nfrom sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score\n\nX = credit[['상환_9월', '신용한도', '나이']]\ny = credit[target]\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)\nmodels = {'Dummy': DummyClassifier(strategy='most_frequent'), 'Logistic': LogisticRegression(max_iter=2000)}\nrows = []\nfor name, estimator in models.items():\n    model = Pipeline([('scale', StandardScaler()), ('model', estimator)])\n    model.fit(X_train, y_train)\n    pred = model.predict(X_test)\n    rows.append({'model': name, 'accuracy': accuracy_score(y_test, pred), 'precision': precision_score(y_test, pred, zero_division=0), 'recall': recall_score(y_test, pred, zero_division=0), 'f1': f1_score(y_test, pred, zero_division=0)})\nresults = pd.DataFrame(rows).set_index('model')\nresults\n",
        check="assert set(s['results'].index) == {'Dummy', 'Logistic'}\nassert set(s['results'].columns) == {'accuracy', 'precision', 'recall', 'f1'}\nassert s['results'].loc['Dummy', 'recall'] == 0\nassert ((s['results'] >= 0) & (s['results'] <= 1)).all().all()\nassert len(s['X_test']) == 6000"),
    coding('predict-proba', '모델은 사실 확률을 내놓는다',
        goal="""
        ```interactive
        위젯: threshold
        ```

        로지스틱 회귀는 "부도/정상"을 바로 고르지 않아요. **부도일 확률**을 먼저 계산해요. 그게 0.5를 넘으면 부도라고 답하죠. 위 위젯에서 선을 움직여 보세요. 기준값에 따라 경고와 놓침이 어떻게 바뀌는지 보여요.

        준비 코드가 `model`을 훈련까지 해 뒀어요. `model.predict_proba(X_test)[:, 1]`로 부도 확률을 `probabilities`에 담으세요. 확률이 0.5 이상인 고객 수는 `n_positive_05`예요. 0.3 이상은 `n_positive_03`이고요. 둘 다 담아 출력하세요.

        기준을 0.5에서 0.3으로 낮추면 부도라고 경고하는 고객이 늘어요. 얼마나 늘어나는지 보세요.
        """,
        hint="""
        `predict_proba`는 행마다 `[정상 확률, 부도 확률]` 두 열을 돌려줘요. 그래서 `[:, 1]`로 부도 확률만 골라요. `(probabilities >= 0.5)`는 참·거짓 배열이에요. `.sum()`이 참의 개수고요. `int()`로 감싸 정수로 담으세요.
        """,
        starter=CREDIT_SPLIT + "from sklearn.linear_model import LogisticRegression\n\nX = credit[['상환_9월', '신용한도', '나이']]\ny = credit[target]\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)\nmodel = Pipeline([('scale', StandardScaler()), ('model', LogisticRegression(max_iter=2000))])\nmodel.fit(X_train, y_train)\n# probabilities, n_positive_05, n_positive_03을 만들고 출력하세요\n",
        solution=CREDIT_SPLIT + "from sklearn.linear_model import LogisticRegression\n\nX = credit[['상환_9월', '신용한도', '나이']]\ny = credit[target]\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)\nmodel = Pipeline([('scale', StandardScaler()), ('model', LogisticRegression(max_iter=2000))])\nmodel.fit(X_train, y_train)\nprobabilities = model.predict_proba(X_test)[:, 1]\nn_positive_05 = int((probabilities >= 0.5).sum())\nn_positive_03 = int((probabilities >= 0.3).sum())\nprint(n_positive_05, n_positive_03)\n",
        check="import numpy as np\n\nassert len(s['probabilities']) == 6000 and ((s['probabilities'] >= 0) & (s['probabilities'] <= 1)).all()\nassert np.allclose(s['probabilities'], s['model'].predict_proba(s['X_test'])[:, 1])\nassert s['n_positive_05'] == int((s['probabilities'] >= 0.5).sum()) and s['n_positive_03'] == int((s['probabilities'] >= 0.3).sum())\nassert s['n_positive_03'] > s['n_positive_05']"),
    coding('thresholds', '기준값을 바꿔 0과 1로',
        goal="""
        ```comic-gen
        제목: 기준값은 모델이 아니라 사람이 정한다
        등장인물:
          준호:
            그림: 사람
            이름표: 준호 · 은행 직원
            외형: {머리색: "#303746", 옷색: "#b88646"}
          모델: {그림: 서버, 이름표: 모델}
        컷:
          - 인물: [준호, 모델]
            대사:
              - {화자: 모델, 상대: 준호, 내용: "이 고객 부도 확률 35%."}
              - {화자: 준호, 상대: 모델, 내용: "경고를 보내, 말아?"}
          - 구성: 이전
            인물: [{식별자: 준호, 손모양: 가리키는손}, {식별자: 모델, 표정: 보통}]
            대사:
              - 화자: 모델
                상대: 준호
                내용: |-
                  기준이 0.5면 안 보내고
                  0.3이면 보내. 그 기준은 네가 정해.
              - {화자: 준호, 상대: 모델, 내용: "놓치는 게 더 비싸니까 0.3으로."}
        ```

        확률을 0과 1로 바꾸는 규칙을 이번엔 손으로 써 봐요. 확률 다섯 개가 `probabilities`에 있어요. 0.5 이상이면 1인 배열을 `pred_05`로 만드세요. 0.3 이상이면 1인 배열은 `pred_03`이고요. 각각 1의 개수를 출력하세요.

        같은 확률인데 기준을 낮추니 부도 경고가 둘에서 넷으로 늘어요. 경고를 늘리면 놓치는 부도(FN)는 줄어요. 대신 멀쩡한 고객 경고(FP)는 늘고요. 기준값은 모델이 아니라 **비용을 아는 사람**이 정하는 숫자예요.
        """,
        hint="""
        `(probabilities >= 0.5)`는 참·거짓 배열이에요. 뒤에 `.astype(int)`를 붙이면 참이 1, 거짓이 0이 돼요. 개수는 `.sum()`이고요.
        """,
        starter='import numpy as np\n\nprobabilities = np.array([0.1, 0.35, 0.49, 0.51, 0.8])\n# pred_05, pred_03을 만드세요\n',
        solution='import numpy as np\n\nprobabilities = np.array([0.1, 0.35, 0.49, 0.51, 0.8])\npred_05 = (probabilities >= 0.5).astype(int)\npred_03 = (probabilities >= 0.3).astype(int)\nprint(pred_05.sum(), pred_03.sum())\n',
        check="assert s['pred_05'].tolist() == [0, 0, 0, 1, 1]\nassert s['pred_03'].tolist() == [0, 1, 1, 1, 1]"),
    quiz('metrics-check', '단원 점검',
        choice('부도율 22%인 자료에서 전원 "정상"으로 찍은 모델이 있어요. 정확도와 재현율은 각각 얼마인가요?',
               ['정확도 약 78%, 재현율 0', '정확도 0, 재현율 약 78%', '둘 다 약 78%'], 0,
               '정상이 78%라 정확도는 78%예요. 그런데 부도를 한 명도 못 찾으니 재현율은 0이에요. 정확도만 보면 속아요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「둘 다 78%」: 재현율은 부도를 찾은 비율이라 0이에요.\n- 「정확도 0」: 정상을 다 맞혀 정확도는 78%예요."),
        short('부도라고 경고한 사람 중 진짜 부도였던 비율, TP/(TP+FP)예요. 무엇이라고 하나요?', ['정밀도', 'precision', '프리시전'],
              '정밀도(precision)는 경고의 신뢰도예요. 멀쩡한 고객에게 경고하는 FP가 많으면 떨어져요.'),
        short('진짜 부도 중 미리 찾아낸 비율, TP/(TP+FN)예요. 무엇이라고 하나요?', ['재현율', 'recall', '리콜'],
              '재현율(recall)은 놓치지 않은 정도예요. 부도를 놓치는 FN이 많으면 떨어져요.'),
        choice('혼동행렬에서 "진짜 부도인데 정상이라고 예측한" 칸은 어느 것인가요?',
               ['FN', 'FP', 'TN'], 0,
               'F는 틀림, N은 "정상"이라고 예측했다는 뜻이에요. 부도를 놓친 칸이라 돈을 떼이는 실수죠.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「TN」: 정상을 정상이라 맞힌 칸이에요.\n- 「FP」: 정상인데 부도라고 한 칸이에요."),
        choice('부도를 놓치는 손해가 멀쩡한 고객에게 경고하는 손해보다 훨씬 커요. 어느 지표를 더 봐야 하나요?',
               ['재현율', '정밀도', '정확도'], 0,
               '놓치는 실수 FN을 줄이려는 거니까 재현율이에요. 반대 상황이면 정밀도고요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「정밀도」: 멀쩡한 고객 경고(FP)가 비쌀 때 보는 지표예요.\n- 「정확도」: 불균형 자료에서는 전원 정상으로도 높아요."),
        choice('부도 확률 기준값을 0.5에서 0.3으로 낮추면 일반적으로 어떻게 되나요?',
               ['경고가 늘어 재현율은 오르고 정밀도는 내려간다', '모든 지표가 함께 오른다', '아무 변화가 없다'], 0,
               '낮은 확률도 부도로 보니 놓치는 사람은 줄어요. 대신 멀쩡한 사람 경고가 늘어요. 기준값은 실수의 비용을 아는 사람이 정해요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「아무 변화가 없다」: 경고 대상이 늘어나요.\n- 「모든 지표가 오른다」: 재현율과 정밀도는 보통 반대로 움직여요."),
        choice("""**프롬프트 고르기** · 부도 모델을 기준 모델과 비교해요. 그런데 기준 모델의 precision에서 0으로 나누기 경고가 나요. 어떤 프롬프트가 맞을까요?""",
               ["""scikit-learn. Dummy와 Logistic을 StandardScaler Pipeline으로 학습해 accuracy, precision, recall, f1 네 지표 표 results를 만들어. precision은 zero_division=0. 코드만""", """경고 없애 줘""", """정확도만 비교해 줘""", """경고 나는 모델은 빼 줘"""], 0,
               """정답은 네 지표를 함께 요구했어요. zero_division=0으로 경고 처리 방법까지 정했고요. 불균형 자료에서는 정확도만 보면 속아요.

**다른 보기는 왜 아닌가**

- 「경고 없애 줘」: 경고를 숨기는 코드가 올 수 있어요. 원인 처리가 아니에요.
- 「정확도만」: 기준 모델도 78%라 차이가 안 보여요.
- 「경고 나는 모델은 빼」: 기준 모델을 빼면 비교가 사라져요."""),
        choice("""**프롬프트 고르기** · 부도를 놓치는 손해가 멀쩡한 고객에게 경고하는 손해보다 훨씬 커요. 기준값을 어떻게 다루라고 해야 할까요?""",
               ["""model.predict_proba(X_test)[:, 1]로 부도 확률을 받고 기준값을 0.5와 0.3으로 각각 적용해 recall과 precision이 어떻게 달라지는지 표로 보여 줘. 놓치는 부도(FN)가 비싸니 recall을 우선해""", """제일 정확한 기준값 찾아 줘""", """0.5로 그냥 가자""", """부도를 다 잡게 전부 부도로 예측해 줘"""], 0,
               """정답은 확률을 꺼내는 방법과 비교할 기준값을 적었어요. 비용 판단(FN이 비싸니 recall 우선)도 있고요. 기준값은 비용을 아는 사람이 정해요.

**다른 보기는 왜 아닌가**

- 「제일 정확한 기준값」: '정확'의 기준이 없고 비용이 빠졌어요.
- 「0.5로 그냥」: 기본값이 내 비용에 맞는지 확인을 안 했어요.
- 「전부 부도로」: recall은 100%예요. 그런데 precision이 무너져 쓸 수 없어요."""),
    ),
])
