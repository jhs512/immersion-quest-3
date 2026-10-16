"""세 분류 모델과 기준 비교"""
from kpc_course.dsl import *

MODEL_PREP = TI + FEATURES + SPLIT + PREP

UNIT = unit('classifiers', '세 분류 모델과 기준 비교', [
    concept('baselines', '"좋다"고 말하려면 비교할 기준이 있어야 한다',
        body="""
        손질이 끝났으니 모델을 고를 차례예요. 이 수업에서는 세 가지를 써요. 수식 없이 각각이 뭘 하는지만 잡아 두면 돼요.

        **로지스틱 회귀**(`LogisticRegression`)는 입력마다 점수를 매겨 더해요. 합이 어떤 선을 넘으면 생존, 못 넘으면 사망으로 갈라요. 어느 열이 얼마나 중요한지가 점수로 남아서 설명하기 쉬워요.

        **결정 트리**(`DecisionTreeClassifier`)는 스무고개예요. "여성인가? → 3등실인가? → 나이가 15세 이하인가?" 같은 질문을 가지처럼 뻗어 가며 갈라요. 질문을 끝없이 늘리면 훈련 자료를 통째로 외워 버려요. 그래서 `max_depth`로 질문 깊이를 제한해요.

        **랜덤 포레스트**(`RandomForestClassifier`)는 서로 조금씩 다른 트리를 수십 개 만들어요. 그 다수결로 정하죠. 한 트리의 실수를 다른 트리들이 덮어 줘요. 그래서 보통 트리 하나보다 안정적이에요.

        ```interactive
        위젯: overfit
        ```

        모델이 몇 개든 비교 방식은 하나예요. **같은 훈련 자료로 배우고, 같은 테스트 자료로 채점한다.** 그런데 그 전에 물어야 할 게 있어요. 정확도 78%는 좋은 걸까요? 테스트 262명 중 사망이 162명이거든요. 그러니 **아무것도 안 보고 전원 사망으로 찍어도 62%**가 나와요. 모델의 실력은 이 "찍기 점수"와 비교해야 보이죠. 그래서 가장 많은 답만 찍는 `DummyClassifier`를 기준 모델로 먼저 돌려요. 기준보다 못한 모델은 아무것도 못 배운 거예요. 현장도 마찬가지고요. 콜센터 팀장이 월요일 인력을 짤 때 가장 단순한 방법은 "지난주 월요일과 같게"죠. 통화량 예측 모델을 들여왔는데 이 방법보다 더 빗나가요? 그럼 팀장의 감보다 못한 거예요.

        ```comic-gen
        제목: 팀장의 감과 모델
        등장인물:
          팀장:
            그림: 사람
            이름표: 콜센터 팀장
            외형: {머리모양: 긴머리, 머리색: "#2f2a33", 옷: 재킷, 옷색: "#7a5a9e"}
          민지:
            그림: 사람
            이름표: 민지
            외형: {머리모양: 단발, 머리색: "#573d36", 옷: 후드, 옷색: "#609b87"}
        컷:
          - 인물: [팀장, 민지]
            대사:
              - 화자: 팀장
                상대: 민지
                내용: |-
                  월요일 인력은
                  지난주 월요일과 같게 짜요.
              - {화자: 민지, 상대: 팀장, 내용: "저는 통화량 예측 모델을 만들었어요!"}
          - 구성: 이전
            인물: [{식별자: 팀장, 표정: 어리둥절}, {식별자: 민지, 표정: 어리둥절}]
            대사:
              - {화자: 팀장, 상대: 민지, 내용: "그래서 내 방법보다 덜 빗나가나요?"}
              - {화자: 민지, 상대: 팀장, 내용: "...그걸 아직 안 재 봤네요."}
          - 구성: 이전
            인물: [{식별자: 팀장, 표정: 기쁨}, {식별자: 민지, 표정: 기쁨}]
            대사:
              - 화자: 민지
                상대: 팀장
                내용: |-
                  팀장님 방법이 기준 모델이에요.
                  그걸 먼저 재고 비교할게요.
              - {화자: 팀장, 상대: 민지, 내용: "제 방법보다 못 맞히면 안 쓰는 걸로 하죠."}
        ```

        ```python
        model = Pipeline([('prepare', make_preprocessor()), ('model', LogisticRegression(max_iter=2000))])
        model.fit(X_train, y_train)
        pred = model.predict(X_test)
        accuracy_score(y_test, pred)
        ```

        준비 코드의 `make_preprocessor()`는 앞 단원에서 만든 손질기예요. 숫자용 묶음(채우기+표준화)과 글자용 묶음(채우기+One-hot)을 합친 거예요. 그 뒤에 모델을 붙인 게 위의 `Pipeline`이에요. `fit` 한 번에 손질과 학습이 끝나요. `predict` 한 번에 손질과 예측이 끝나고요. 모델을 바꿀 때는 `('model', ...)` 자리만 바꿔요.

        점수는 정확도(accuracy, 전체 중 맞힌 비율) 하나만 보지 않아요. 생존자가 적은 자료에서는 생존자를 얼마나 잘 찾았는지도 봐야 해요. 그래서 F1 점수도 같이 적어요. 자세한 뜻은 뒤 단원에서 다뤄요. 지금은 "두 점수를 표로 나란히 적는다"까지만.
        """,
        check=short('입력을 안 보고 가장 많은 답만 찍는 기준 모델이 있죠. `scikit-learn`에서의 이름이 뭔가요?', ['DummyClassifier', 'Dummy', '더미 분류기', '더미분류기'],
                    '`DummyClassifier(strategy="most_frequent")`가 기준이에요. 이 점수를 못 넘는 모델은 아무것도 못 배운 거예요.')),
    coding('dummy-only', '찍기 점수부터 재기',
        goal="""
        기준 모델만 먼저 돌려요. `DummyClassifier(strategy='most_frequent')`를 `dummy`에 만드세요. `X_train`, `y_train`으로 학습하세요. 그다음 `X_test`를 예측한 정확도를 `dummy_accuracy`에 담아 출력하세요.

        입력을 안 보니 손질이 필요 없어요. 테스트 262명 중 사망이 162명이라 162/262가 나와요. 이 숫자가 이 단원의 기준 모델의 점수예요.
        """,
        hint="""
        `dummy.fit(X_train, y_train)`을 먼저 해요. 그다음 `accuracy_score(y_test, dummy.predict(X_test))`예요. 예측값을 출력해 보면 전부 0이에요.
        """,
        starter=TI + FEATURES + SPLIT + "from sklearn.dummy import DummyClassifier\nfrom sklearn.metrics import accuracy_score\n# dummy를 학습하고 dummy_accuracy를 구하세요\n",
        solution=TI + FEATURES + SPLIT + "from sklearn.dummy import DummyClassifier\nfrom sklearn.metrics import accuracy_score\n\ndummy = DummyClassifier(strategy='most_frequent')\ndummy.fit(X_train, y_train)\ndummy_accuracy = accuracy_score(y_test, dummy.predict(X_test))\nprint(dummy_accuracy)\n",
        check="assert abs(s['dummy_accuracy'] - 162 / 262) < 1e-10\nassert set(s['dummy'].predict(s['X_test'])) == {0}"),
    coding('model-comparison', '네 모델을 한 표에서 비교하기',
        goal="""
        자, 기준 모델과 세 모델을 같은 조건에서 비교해요. `models` 딕셔너리에 `Dummy`, `Logistic`, `Tree`, `Forest` 이름으로 모델을 넣으세요. 각각을 `Pipeline([('prepare', make_preprocessor()), ('model', ...)])`로 묶어 학습하고 예측하세요. `accuracy`와 `f1`을 구해 `results` 표를 만드세요. `Forest`는 `n_estimators=50, max_depth=5, random_state=42`예요.

        `results`는 모델 이름이 인덱스이고 `accuracy`, `f1` 두 열이에요. 기준 모델의 정확도가 앞 미션의 162/262와 같고 F1이 0이면 돼요. 그럼 표가 맞게 만들어진 거예요. 어느 모델이 기준을 얼마나 넘는지 보세요.
        """,
        hint="""
        표 만들기 패턴이에요. 빈 리스트 `rows = []`를 두세요. `for name, estimator in models.items():` 안에서 네 가지를 해요. (1) `Pipeline`을 새로 만들고 (2) `fit` (3) `predict` (4) `rows.append({'model': name, 'accuracy': ..., 'f1': f1_score(y_test, pred, zero_division=0)})`예요. 반복이 끝나면 `results = pd.DataFrame(rows).set_index('model')`이에요. 학습한 모델 자체도 `fitted[name] = model`로 보관해 두세요.
        """,
        starter=MODEL_PREP + "from sklearn.dummy import DummyClassifier\nfrom sklearn.linear_model import LogisticRegression\nfrom sklearn.tree import DecisionTreeClassifier\nfrom sklearn.ensemble import RandomForestClassifier\nfrom sklearn.metrics import accuracy_score, f1_score\n# models 딕셔너리와 results를 만드세요\n",
        solution=MODEL_PREP + "from sklearn.dummy import DummyClassifier\nfrom sklearn.linear_model import LogisticRegression\nfrom sklearn.tree import DecisionTreeClassifier\nfrom sklearn.ensemble import RandomForestClassifier\nfrom sklearn.metrics import accuracy_score, f1_score\n\nmodels = {'Dummy': DummyClassifier(strategy='most_frequent'), 'Logistic': LogisticRegression(max_iter=2000), 'Tree': DecisionTreeClassifier(max_depth=4, random_state=42), 'Forest': RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42)}\nrows = []\nfitted = {}\nfor name, estimator in models.items():\n    model = Pipeline([('prepare', make_preprocessor()), ('model', estimator)])\n    model.fit(X_train, y_train)\n    pred = model.predict(X_test)\n    fitted[name] = model\n    rows.append({'model': name, 'accuracy': accuracy_score(y_test, pred), 'f1': f1_score(y_test, pred, zero_division=0)})\nresults = pd.DataFrame(rows).set_index('model')\nresults\n",
        check="assert set(s['results'].index) == {'Dummy', 'Logistic', 'Tree', 'Forest'}\nassert set(s['results'].columns) == {'accuracy', 'f1'}\nassert ((s['results'] >= 0) & (s['results'] <= 1)).all().all()\nassert abs(s['results'].loc['Dummy', 'accuracy'] - 162 / 262) < 1e-10\nassert s['results'].loc['Dummy', 'f1'] == 0"),
    coding('train-vs-test', '외운 모델 잡아내기',
        goal="""
        ```comic-gen
        제목: 답만 외운 학생
        등장인물:
          모델: {그림: 서버, 이름표: 모델}
          강사:
            그림: 사람
            이름표: 강사
            외형: {옷: 재킷, 옷색: "#5379a7", 안경: true}
        컷:
          - 인물: [{식별자: 모델, 표정: 기쁨}, 강사]
            대사:
              - {화자: 모델, 상대: 강사, 내용: "문제집 1,047문제, 전부 외웠어요! 98점!"}
              - {화자: 강사, 상대: 모델, 내용: "좋아요. 그럼 처음 보는 262문제."}
          - 구성: 이전
            인물: [{식별자: 모델, 표정: 슬픔}]
            대사:
              - {화자: 모델, 상대: 강사, 내용: "숫자가 조금 다르니까… 76점이요."}
              - {화자: 강사, 상대: 모델, 내용: "답을 외운 거지 규칙을 배운 게 아니죠. 과적합."}
          - 구성: 이전
            인물: [{식별자: 모델, 표정: 보통}, {식별자: 강사, 손모양: 가리키는손}]
            대사:
              - {화자: 모델, 상대: 강사, 내용: "그럼 어떻게 해요?"}
              - 화자: 강사
                상대: 모델
                내용: |-
                  질문 횟수를 제한해요(max_depth).
                  덜 외우고 큰 규칙만 배우게.
        ```

        질문 깊이를 제한하지 않은 `DecisionTreeClassifier(random_state=42)`를 써요. 손질기와 묶어 `model`에 학습하세요. 그리고 정확도를 두 번 재요. 훈련 자료로 잰 `train_accuracy`와 테스트 자료로 잰 `test_accuracy`예요. 둘을 출력하세요.

        훈련 점수는 90%를 훌쩍 넘어요. 그런데 테스트 점수는 한참 낮아요. 문제집은 거의 다 맞히는데 모의고사는 못 봐요. **외운 모델**이에요. 이 현상을 과적합이라고 해요.
        """,
        hint="""
        `model = Pipeline([('prepare', make_preprocessor()), ('model', DecisionTreeClassifier(random_state=42))])`를 만들어 `fit(X_train, y_train)`하세요. 그다음 점수를 둘 재요. `accuracy_score(y_train, model.predict(X_train))`이 훈련 점수예요. `accuracy_score(y_test, model.predict(X_test))`가 테스트 점수고요. 각각 저장하세요.
        """,
        starter=MODEL_PREP + "from sklearn.tree import DecisionTreeClassifier\nfrom sklearn.metrics import accuracy_score\n# model, train_accuracy, test_accuracy를 만드세요\n",
        solution=MODEL_PREP + "from sklearn.tree import DecisionTreeClassifier\nfrom sklearn.metrics import accuracy_score\n\nmodel = Pipeline([('prepare', make_preprocessor()), ('model', DecisionTreeClassifier(random_state=42))])\nmodel.fit(X_train, y_train)\ntrain_accuracy = accuracy_score(y_train, model.predict(X_train))\ntest_accuracy = accuracy_score(y_test, model.predict(X_test))\nprint(train_accuracy, test_accuracy)\n",
        check="assert 0 <= s['test_accuracy'] <= 1 and 0 <= s['train_accuracy'] <= 1\nassert s['train_accuracy'] > s['test_accuracy']\nassert s['train_accuracy'] > 0.9\nassert abs(s['train_accuracy'] - (s['model'].predict(s['X_train']) == s['y_train']).mean()) < 1e-12"),
    concept('hyperparameters', '공부 내용과 공부법: 파라미터와 하이퍼파라미터',
        body="""
        앞 미션에서 질문 횟수를 `max_depth`로 제한하면 덜 외운다고 했죠? 그런데 이 숫자는 누가 정할까요? 모델 안에는 두 종류의 값이 있어요. **학습하면서 기계가 스스로 찾는 값**이 파라미터예요. **학습을 시작하기 전에 사람이 정해 주는 값**이 하이퍼파라미터고요.

        ```mapping
        제목: 파라미터와 하이퍼파라미터
        종류: 비교
        왼쪽: 파라미터
        오른쪽: 하이퍼파라미터
        학습 중에 기계가 찾는다 → 학습 전에 사람이 정한다
        공부 내용 → 공부법
        선형 회귀의 가중치, 트리의 질문들 → max_depth, n_estimators, alpha
        fit()이 채운다 → 괄호 안에 적는다
        ```

        ```comic-gen
        제목: 공부 내용과 공부법
        등장인물:
          민지:
            그림: 사람
            이름표: 민지 · 수강생
            외형: {머리모양: 단발, 옷: 후드, 옷색: "#4f8a8b"}
          강사:
            그림: 사람
            이름표: 강사
            외형: {옷: 재킷, 옷색: "#5379a7", 안경: true}
        컷:
          - 인물: [{식별자: 민지, 표정: 어리둥절}, 강사]
            대사:
              - {화자: 민지, 상대: 강사, 내용: "max_depth도 모델이 알아서 정하면 안 돼요?"}
              - {화자: 강사, 상대: 민지, 내용: "공부 내용은 학생이 익히죠. 그런데 하루 몇 시간, 어떤 방법으로 할지는 공부 전에 정하잖아요."}
          - 구성: 이전
            인물: [{식별자: 민지, 표정: 기쁨}, {식별자: 강사, 손모양: 가리키는손}]
            대사:
              - {화자: 강사, 상대: 민지, 내용: "그 공부법이 하이퍼파라미터예요. 몇 가지 후보를 시켜 보고 점수가 좋은 쪽을 골라요."}
              - {화자: 민지, 상대: 강사, 내용: "공부법을 고르는 것도 결국 점수로 하네요."}
        ```

        ```python
        from sklearn.model_selection import cross_val_score

        for depth in [2, 3, 5, 8, 12]:
            model = Pipeline([('prepare', make_preprocessor()), ('model', DecisionTreeClassifier(max_depth=depth, random_state=42))])
            score = cross_val_score(model, X_train, y_train, cv=5).mean()  # 훈련 자료 안에서 5번 나눠 채점한 평균
            print(depth, round(score, 3))
        ```

        고르는 방법이 **튜닝**이에요. 후보를 몇 개 두고요. **훈련 자료 안에서** 다시 나눠 채점한 점수로 비교해요. 이게 교차 검증이죠. 테스트 자료로 고르면 안 돼요. 그러면 테스트가 더는 "처음 보는 자료"가 아니거든요. 시험지를 보고 공부법을 고른 셈이죠. 테스트는 다 고른 뒤 마지막에 한 번만 써요. `GridSearchCV`는 이 반복문을 대신 돌려 주는 도구예요.

        한 가지 더. 파라미터는 원래부터 기계가 학습으로 찾는 값이죠? 요즘은 **하이퍼파라미터 고르기와 모델 고르기까지 기계가** 해요. 이걸 AutoML이라고 부르죠. `auto-sklearn` 같은 라이브러리나 클라우드 서비스가 그 일을 해요. 후보를 돌려 가며 알아서 고르고요. 그래도 사람이 정하는 게 있거든요. 어떤 점수로 비교할지, 후보 범위를 어디까지 둘지, 그 결과를 믿어도 되는지예요. AI에게 "해 줘"라고 할 때 한 줄 보태 보세요. **"max_depth 후보를 교차 검증으로 골라 줘"**라고요. 그게 이 단원에서 가져갈 말이에요.
        """,
        check=short("`max_depth`처럼 학습을 시작하기 전에 사람이 정해 주는 값을 무엇이라고 부르나요?", ['하이퍼파라미터', '하이퍼 파라미터', 'hyperparameter', 'hyper parameter', '초매개변수'],
                    '하이퍼파라미터는 공부법처럼 학습 전에 정하는 값이에요. 파라미터는 공부 내용처럼 학습하면서 기계가 채우는 값이고요. 후보를 두고 훈련 자료 안의 교차 검증 점수로 골라요.')),
    coding('tune-depth', '공부법 고르기: max_depth 튜닝',
        goal="""
        자, 트리의 깊이 후보 `depths`가 준비돼 있어요. 후보마다 손질기와 묶은 `DecisionTreeClassifier(max_depth=깊이, random_state=42)`를 만드세요. `cross_val_score(모델, X_train, y_train, cv=5)`의 평균으로 채점하세요. 그 점수를 `cv_scores`에 깊이 → 평균 점수 딕셔너리로 담으세요. 점수가 가장 높은 깊이를 `best_depth`에 고르세요. 그 깊이로 `model`을 다시 학습하세요. 그 테스트 정확도를 `test_accuracy`에 담아 출력하세요.

        깊이를 고를 때 테스트 자료를 쓰면 안 돼요. 테스트는 `best_depth`를 정한 뒤 한 번만 써요.
        """,
        hint="""
        `for depth in depths:` 안에서 `Pipeline([('prepare', make_preprocessor()), ('model', DecisionTreeClassifier(max_depth=depth, random_state=42))])`를 만들어요. 그리고 `cv_scores[depth] = cross_val_score(model, X_train, y_train, cv=5).mean()`이에요. 가장 큰 값의 키는 `max(cv_scores, key=cv_scores.get)`으로 찾아요. 그다음 `best_depth`로 모델을 새로 만들어 `fit(X_train, y_train)`하세요. 끝으로 `accuracy_score(y_test, model.predict(X_test))`예요.
        """,
        starter=MODEL_PREP + "from sklearn.tree import DecisionTreeClassifier\nfrom sklearn.model_selection import cross_val_score\nfrom sklearn.metrics import accuracy_score\n\ndepths = [2, 3, 5, 8, 12]\ncv_scores = {}\n# cv_scores, best_depth, model, test_accuracy를 만드세요\n",
        solution=MODEL_PREP + "from sklearn.tree import DecisionTreeClassifier\nfrom sklearn.model_selection import cross_val_score\nfrom sklearn.metrics import accuracy_score\n\ndepths = [2, 3, 5, 8, 12]\ncv_scores = {}\nfor depth in depths:\n    model = Pipeline([('prepare', make_preprocessor()), ('model', DecisionTreeClassifier(max_depth=depth, random_state=42))])\n    cv_scores[depth] = cross_val_score(model, X_train, y_train, cv=5).mean()\nbest_depth = max(cv_scores, key=cv_scores.get)\nmodel = Pipeline([('prepare', make_preprocessor()), ('model', DecisionTreeClassifier(max_depth=best_depth, random_state=42))])\nmodel.fit(X_train, y_train)\ntest_accuracy = accuracy_score(y_test, model.predict(X_test))\nprint({depth: round(float(score), 3) for depth, score in cv_scores.items()})\nprint(f'고른 깊이 {best_depth}, 테스트 정확도 {test_accuracy:.3f}')\n",
        check="assert set(s['cv_scores']) == {2, 3, 5, 8, 12}\nassert all(0 <= v <= 1 for v in s['cv_scores'].values())\nassert s['best_depth'] == max(s['cv_scores'], key=s['cv_scores'].get)\nassert s['model'].get_params()['model__max_depth'] == s['best_depth']\nassert abs(s['test_accuracy'] - (s['model'].predict(s['X_test']) == s['y_test']).mean()) < 1e-9"),
    concept('save-model', '한 번 만든 모델은 저장해서 다시 쓴다',
        body="""
        지금까지 모든 미션은 실행할 때마다 `fit`부터 다시 했어요. 승객 1,047명이면 1초라 괜찮아요. 그런데 회사 자료는 수백만 행이에요. 학습에 몇 시간이 걸리기도 해요. 예측할 때마다 다시 배우게 할 이유가 없죠. 배운 모델은 **파일로 저장**해 둬요. 쓸 때는 **불러와서 `predict`만** 해요.

        ```comic-gen
        제목: 어제 훈련한 모델은 어디 갔나
        등장인물:
          공장장:
            그림: 사람
            이름표: 빵 공장장
            외형: {피부색: "#d6a279", 머리모양: 민머리, 옷색: "#8a6d4b"}
          모델: {그림: 서버, 이름표: 모델}
        컷:
          - 인물: [{식별자: 공장장, 표정: 어리둥절}, {식별자: 모델, 표정: 보통}]
            대사:
              - {화자: 공장장, 상대: 모델, 내용: "어제 세 시간 걸려 훈련했는데, 오늘 또 처음부터?"}
              - {화자: 모델, 상대: 공장장, 내용: "프로그램이 끝나면 저는 사라져요. 저장 안 하셨잖아요."}
          - 구성: 이전
            인물: [{식별자: 공장장, 손모양: 가리키는손}, {식별자: 모델, 표정: 기쁨}]
            대사:
              - {화자: 공장장, 상대: 모델, 내용: "joblib.dump로 파일에 넣어 둘게."}
              - {화자: 모델, 상대: 공장장, 내용: "그럼 내일 새벽엔 불러와서 바로 예측만 하면 돼요."}
        ```

        ```python
        import joblib

        joblib.dump(model, 'titanic_model.joblib')  # 훈련 끝난 모델을 파일로
        loaded = joblib.load('titanic_model.joblib')  # 다른 날, 다른 프로그램에서 불러오기
        loaded.predict(X_new)  # 훈련 없이 바로 예측
        ```

        `joblib`은 `scikit-learn`과 함께 설치되는 저장 도구예요. 저장하는 건 모델 하나가 아니라 **파이프라인 전체**예요. 그래서 앞 단원에서 훈련 자료로 정한 기준도 파일 안에 같이 들어가요. 나이의 중앙값, One-hot 열 목록, 표준화 기준이요. 새 자료에도 같은 손질이 그대로 적용되죠. 손질과 모델을 한 줄로 묶어 둔 또 하나의 이유예요.

        현장에서는 이렇게 돌아가요. 빵 공장은 **매주 월요일에 한 번** 지난 기록으로 다시 학습해 파일을 갈아 끼워요. **매일 새벽에는 불러와서 오늘 생산량만** 예측하고요. 콜센터의 월요일 인원 예측도 같은 모양이죠. AI에게 "해 줘"라고 시킬 때도 한 줄 보태 보세요. **"모델은 파일로 저장하고, 예측 스크립트는 불러오기만 하게"**라고요. 그럼 매번 학습하는 코드를 안 받거든요.

        주의할 점 두 가지. 저장한 파일은 같은 버전의 `scikit-learn`에서 열어야 안전해요. 자료가 많이 바뀌면(새 메뉴, 새 상품) 다시 학습해야 해요. 파일은 "그때 배운 규칙"일 뿐이니까요.
        """,
        check=short("학습이 끝난 파이프라인을 파일로 저장할 때 쓰는 함수는 무엇인가요? `joblib.____(model, 'titanic_model.joblib')`", ['dump', 'joblib.dump'],
                    '`joblib.dump`가 저장, `joblib.load`가 불러오기예요. 파이프라인째 저장하면 손질 기준도 함께 들어가요. 그래서 새 자료에 바로 `predict`할 수 있어요.')),
    coding('save-and-load', '모델을 파일로 저장하고 다시 불러오기',
        goal="""
        로지스틱 회귀를 손질기와 묶어 `model`에 학습하세요. 그걸 `joblib.dump`로 `titanic_model.joblib`에 저장하세요. 그다음 `joblib.load`로 `loaded`에 다시 불러오세요. 그 테스트 정확도를 `test_accuracy`에 담아 출력하세요.

        불러온 모델의 예측은 원래 모델과 완전히 같아야 해요. 저장과 불러오기 사이에 학습은 없어요.
        """,
        hint="""
        먼저 `model = Pipeline([('prepare', make_preprocessor()), ('model', LogisticRegression(max_iter=1000))])`를 만들어 `fit(X_train, y_train)`하세요. 저장은 `joblib.dump(model, 'titanic_model.joblib')`예요. 불러오기는 `loaded = joblib.load('titanic_model.joblib')`고요. 끝으로 `test_accuracy = accuracy_score(y_test, loaded.predict(X_test))`예요.
        """,
        starter=MODEL_PREP + "import joblib\nfrom sklearn.linear_model import LogisticRegression\nfrom sklearn.metrics import accuracy_score\n# model을 학습해 저장하고, loaded로 불러와 test_accuracy를 구하세요\n",
        solution=MODEL_PREP + "import joblib\nfrom sklearn.linear_model import LogisticRegression\nfrom sklearn.metrics import accuracy_score\n\nmodel = Pipeline([('prepare', make_preprocessor()), ('model', LogisticRegression(max_iter=1000))])\nmodel.fit(X_train, y_train)\njoblib.dump(model, 'titanic_model.joblib')\nloaded = joblib.load('titanic_model.joblib')\ntest_accuracy = accuracy_score(y_test, loaded.predict(X_test))\nprint(f'불러온 모델의 테스트 정확도: {test_accuracy:.3f}')\n",
        check="from pathlib import Path\n\nassert Path('titanic_model.joblib').exists()\nassert (s['loaded'].predict(s['X_test']) == s['model'].predict(s['X_test'])).all()\nassert abs(s['test_accuracy'] - (s['loaded'].predict(s['X_test']) == s['y_test']).mean()) < 1e-9"),
    quiz('model-check', '단원 점검',
        choice('`max_depth` 후보 중 하나를 고를 때 어떤 자료의 점수로 비교해야 하나요?',
               ['훈련 자료 안에서 다시 나눠 채점한 교차 검증 점수', '테스트 자료의 정확도', '훈련 자료 전체를 그대로 다시 채점한 점수'], 0,
               '테스트는 다 고른 뒤 한 번만 써요. 고르는 데 쓰면 더는 처음 보는 자료가 아니에요. 훈련 자료를 그대로 채점하면 깊은 트리가 늘 이겨요(외운 점수).' "\n\n**다른 보기는 왜 아닌가**\n\n- 「테스트 자료의 정확도」: 시험지를 보고 공부법을 고르는 셈이에요. 점수가 부풀려져요.\n- 「훈련 자료 전체」: 외운 점수라 깊을수록 좋아 보여요. 그래서 과적합을 골라요."),
        choice('내일 새벽에도 오늘 훈련한 모델로 예측하려면 어떻게 해야 하나요?',
               ['`joblib.dump`로 파이프라인째 파일에 저장하고, 쓸 때 `joblib.load`로 불러와 `predict`만 한다', '매일 새벽 `fit`부터 다시 돌린다', '오늘 예측 결과 표만 저장해 둔다'], 0,
               '저장한 파일에는 모델과 손질 기준이 함께 들어 있어요. 그래서 새 자료에 바로 예측할 수 있어요. 학습은 자료가 바뀔 때만 다시 해요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「매일 fit부터」: 몇 시간짜리 학습을 매일 반복하는 셈이에요.\n- 「결과 표만 저장」: 내일 새 입력에는 쓸 수 없어요."),
        choice('정확도 78%짜리 모델이 좋은지 판단하려면 무엇과 비교해야 하나요?',
               ['아무것도 보지 않고 가장 많은 답만 찍은 기준 모델의 점수', '훈련 자료로 잰 점수', '100%'], 0,
               '테스트 262명 중 162명이 사망이라 전원 사망으로 찍어도 62%예요. 기준을 넘는 만큼이 모델이 배운 몫이에요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「100%」: 100%는 기준이 아니라 불가능한 목표예요.\n- 「훈련 자료로 잰 점수」: 외운 점수라 비교 대상이 못 돼요."),
        choice('훈련 정확도 98%, 테스트 정확도 76%인 모델은 어떤 상태인가요?',
               ['훈련 자료를 외운 과적합', '완벽한 모델', '학습이 덜 된 모델'], 0,
               '문제집은 다 맞히고 모의고사는 못 보는 상태예요. 실력은 테스트 점수에 더 가까워요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「완벽한 모델」: 테스트 76%는 완벽과 거리가 멀어요.\n- 「학습이 덜 된」: 덜 됐으면 훈련 점수도 낮아요."),
        short('서로 조금씩 다른 결정 트리를 수십 개 만들어 다수결로 정해요. 이 모델 이름이 뭔가요?', ['RandomForest', 'Random Forest', '랜덤 포레스트', '랜덤포레스트', 'RandomForestClassifier'],
              '랜덤 포레스트는 트리 여러 개의 다수결이에요. 한 트리의 실수를 다른 트리들이 덮어 줘요.'),
        choice("`DecisionTreeClassifier(max_depth=4)`예요. 여기서 `max_depth`는 뭘 하나요?",
               ['스무고개 질문의 깊이를 제한해 외우는 것을 막는다', '정확도를 4%로 고정한다', '트리를 4개 만든다'], 0,
               '질문을 끝없이 늘리면 훈련 자료를 통째로 외워요. 깊이 제한이 과적합을 줄이는 가장 간단한 방법이에요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「정확도를 4%로」: 정확도와 무관해요.\n- 「트리를 4개」: 트리 개수는 n_estimators(랜덤 포레스트)예요."),
        choice('모델 네 개를 공정하게 비교하려면 무엇이 같아야 하나요?',
               ['훈련 자료, 테스트 자료, 손질 방법, 점수 종류', '모델 이름의 길이', '학습에 걸린 시간'], 0,
               '조건이 하나라도 다르면 점수 차이의 이유를 몰라요. 모델 때문인지 조건 때문인지 못 가려요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「이름의 길이」: 이름은 결과와 무관해요.\n- 「학습 시간」: 시간이 달라도 공정한 비교예요."),
        short('전원 사망으로 찍는 기준 모델은 테스트 262명 중 몇 명을 맞히나요?', ['162', '162명'],
              '가장 많은 답(사망)만 찍으면 사망자 수만큼 맞혀요. 162/262, 약 62%예요.'),
        choice("""**프롬프트 고르기** · 로지스틱 회귀 정확도 78%가 좋은 건지 모르겠어요. AI에게 어떻게 물어야 제대로 된 비교를 받을까요?""",
               ["""같은 X_train, X_test, y_train, y_test로 DummyClassifier(strategy='most_frequent') 기준선의 정확도를 먼저 구하고, 로지스틱 회귀 정확도와 F1을 같은 테스트 자료에서 비교하는 표를 만들어 줘. 코드만""", """78%면 좋은 거야?""", """정확도를 90%로 올려 줘""", """더 좋은 모델 추천해 줘"""], 0,
               """정답은 기준 모델(baseline)의 점수를 같은 자료에서 먼저 재라고 했어요. 그리고 같은 종류의 점수로 비교하라고 했죠. 점수는 기준과 비교해야 뜻이 생겨요.

**다른 보기는 왜 아닌가**

- 「좋은 거야?」: AI가 그럴듯하게 답하지만 근거가 없어요.
- 「90%로 올려 줘」: 누수나 테스트 자료 바꾸기로 점수를 부풀릴 위험이 커요.
- 「더 좋은 모델 추천」: 기준 없이 모델 이름만 바뀌어요."""),
        choice("""**프롬프트 고르기** · 훈련 정확도 98%, 테스트 정확도 76%인 결정 트리를 받았어요. 다음 프롬프트로 가장 적절한 건 뭘까요?""",
               ["""훈련 98%, 테스트 76%면 과적합이야. DecisionTreeClassifier에 max_depth=5를 두고 같은 분할·같은 전처리 Pipeline으로 다시 학습해 두 점수를 함께 출력해 줘""", """테스트 점수도 98%로 맞춰 줘""", """훈련 점수가 높으니 이 모델로 가자""", """테스트 자료를 훈련에 합쳐서 다시 학습해 줘"""], 0,
               """정답은 증상을 과적합이라고 이름 붙였어요. 해결책(깊이 제한)과 공정한 비교 조건(같은 분할·같은 손질)도 적었어요.

**다른 보기는 왜 아닌가**

- 「테스트도 98%로」: 불가능하거나 누수로만 가능해요.
- 「훈련 점수가 높으니」: 훈련 점수는 외운 점수예요.
- 「테스트를 훈련에 합쳐」: 채점할 자료가 사라지는 누수예요."""),
    ),
])
