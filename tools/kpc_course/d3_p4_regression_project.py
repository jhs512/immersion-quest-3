"""회귀 비교와 최종 결과"""
from kpc_course.dsl import *

STOCK_MODEL = ST_FRAME + TIME_SPLIT + REG

UNIT = unit('regression-project', '회귀 비교와 최종 결과', [
    concept('regression-metrics', '직선 맞추기, 그리고 기준보다 못한 결과도 그대로 보고하기',
        body="""
        마지막 단원이에요. 입력은 네 열이에요. 오늘 종가, 수익률, 5일 평균, 어제 종가. 이걸로 내일 종가를 맞히는 회귀 모델을 세 개 돌려요. 그리고 앞 단원의 기준과 비교해서 결론을 써요.

        **선형 회귀**(`LinearRegression`)는 입력마다 가중치를 곱해 더한 값으로 정답을 맞혀요. 입력이 하나면 점들 사이에 가장 잘 맞는 직선을 그어요. 넷이면 네 방향으로 기울어진 판을 맞추는 거예요. 학습이 끝나면 `coef_`에 가중치 네 개가 남아요. 어느 입력이 얼마나 영향을 줬는지 거기서 읽을 수 있죠.

        **릿지**(`Ridge`)와 **라쏘**(`Lasso`)는 같은 직선 맞추기에 **브레이크**를 단 거예요. 가중치가 너무 커지면 벌점을 매겨요. 훈련 자료의 우연한 흔들림까지 외우는 걸 막는 거죠. 라쏘는 브레이크가 세서 쓸모없는 입력의 가중치를 아예 0으로 만들기도 해요. 입력 크기가 제각각이면 브레이크가 공평하지 않아요. 그래서 분류에서처럼 `StandardScaler`와 묶어 써요.

        ```python
        model = Pipeline([('scale', StandardScaler()), ('model', Ridge(alpha=1))])
        model.fit(X_train, y_train)
        prediction = model.predict(X_test)
        mean_absolute_error(y_test, prediction)
        ```

        점수는 셋을 함께 적어요. **MAE**는 앞 단원 그대로, 하루 평균 몇 원 빗나갔나. **RMSE**(평균 제곱근 오차)는 차이를 제곱해 평균 낸 뒤 제곱근을 씌워요. 단위는 똑같이 원인데 **큰 실수에 더 민감**하죠. 어쩌다 한 번 크게 틀리는 모델은 MAE보다 RMSE가 많이 커지거든요.

        **R²**(결정계수)는 "정답의 평균값으로만 찍었을 때보다 얼마나 나은가"예요. 1이 만점이고요. 평균보다 못하면 음수도 나와요. 주의할 게 하나 있어요. R²의 비교 대상은 "평균으로 찍기"지 우리 기준 "오늘 종가 그대로"가 아니에요. R²가 높아 보여도 기준 MAE를 못 넘을 수 있어요.

        ```comic-gen
        제목: 평균 30개와 큰 실수
        등장인물:
          공장장:
            그림: 사람
            이름표: 빵 공장장
            외형: {피부색: "#d6a279", 머리모양: 민머리, 옷색: "#8a6d4b"}
          민지:
            그림: 사람
            이름표: 민지 · 수강생
            외형: {머리모양: 단발, 옷: 후드, 옷색: "#4f8a8b"}
        컷:
          - 인물: [{식별자: 공장장, 표정: 어리둥절}, 민지]
            대사:
              - {화자: 공장장, 상대: 민지, 내용: "MAE 30개면 뭐예요?"}
              - {화자: 민지, 상대: 공장장, 내용: "하루 평균 30개를 더 굽거나 덜 굽는다는 뜻이에요."}
          - 구성: 이전
            인물: [공장장, {식별자: 민지, 손모양: 가리키는손}]
            대사:
              - {화자: 공장장, 상대: 민지, 내용: "RMSE는 왜 더 커요?"}
              - {화자: 민지, 상대: 공장장, 내용: "200개 빗나간 날에 벌점을 더 줘요. 큰 실수가 있으면 RMSE가 벌어져요."}
        ```

        숫자가 현장에서 무슨 뜻인지 한 번 옮겨 볼게요. 크루아상 판매량 예측의 MAE가 30개라고 해요. 하루 평균 30개를 더 굽거나 덜 굽는다는 뜻이에요. 더 구우면 저녁에 폐기해요. 덜 구우면 오후에 빈 진열대 앞에서 손님을 돌려보내고요. 평소엔 20개쯤 빗나가다가 명절 전날 하루만 300개 틀리는 모델을 생각해 보세요. MAE는 그럭저럭인데 RMSE가 크게 뛰죠. 콜센터도 같아요. 월요일 통화량 예측이 100통 빗나가면요? 상담원이 모자라 통화가 밀리고 고객은 대기음을 10분씩 들어요. 반대로 상담원이 남아 자리가 비기도 하고요. 어느 지표를 더 무겁게 볼지는 현장에 달렸어요. "가끔 크게 틀리기"와 "늘 조금씩 틀리기" 중 어느 쪽이 더 비싼지 보면 돼요.

        ```comic-gen
        제목: 30개와 300개
        등장인물:
          공장장:
            그림: 사람
            이름표: 빵 공장장
            외형: {피부색: "#d6a279", 머리모양: 민머리, 옷색: "#8a6d4b"}
          강사:
            그림: 사람
            이름표: 강사
            외형: {옷: 재킷, 옷색: "#5379a7", 안경: true}
        컷:
          - 인물: [공장장, 강사]
            대사:
              - {화자: 공장장, 상대: 강사, 내용: "MAE 30개면 쓸 만한가요?"}
              - 화자: 강사
                상대: 공장장
                내용: |-
                  하루 평균 30개를
                  더 굽거나 덜 굽는다는 뜻이죠.
          - 구성: 이전
            인물: [{식별자: 공장장, 표정: 슬픔}, {식별자: 강사, 손모양: 가리키는손}]
            대사:
              - {화자: 공장장, 상대: 강사, 내용: "명절 전날은 300개나 틀렸는데요."}
              - 화자: 강사
                상대: 공장장
                내용: |-
                  그런 날은 RMSE가 크게 뛰어요.
                  큰 실수에 민감하거든요.
          - 구성: 이전
            인물: [{식별자: 공장장, 표정: 보통}, {식별자: 강사, 손모양: null}]
            대사:
              - {화자: 공장장, 상대: 강사, 내용: "그럼 어느 숫자를 봐야 하죠?"}
              - 화자: 강사
                상대: 공장장
                내용: |-
                  가끔 크게 틀리는 게 더 비싸면
                  RMSE를 보세요.
        ```

        결론을 쓰는 순서는 셋이에요. ① 무엇을 언제 예측했고 훈련·테스트를 어떻게 나눴는지. ② 기준 MAE와 모델 MAE, 그 차이. ③ 이 파일, 이 기간에서만 본 결과라는 한계. 모델이 기준보다 나쁘면 **나쁘다고 적어요.** 이 수업의 검사는 "이기는 모델"을 요구하지 않아요. 같은 테스트 기간에서 정직하게 비교했는지를 보죠. 테스트 점수가 마음에 안 든다고 기간을 바꿔 가며 다시 돌리면요? 모의고사 문제를 바꿔 가며 좋은 점수만 고르는 거예요.
        """,
        check=short('예측과 정답의 차이를 제곱해 평균 낸 뒤 제곱근을 씌운 지표예요. 큰 실수에 더 민감하죠. 약어는 무엇인가요?', ['RMSE', 'rmse'],
                    'RMSE예요. 제곱하니까 큰 오차를 더 크게 세죠. MAE와 단위는 같아요. 그런데 가끔 크게 틀리는 모델에서는 둘의 차이가 벌어져요.')),
    coding('linear-only', '선형 회귀 하나만 먼저',
        goal="""
        `StandardScaler`와 `LinearRegression`을 `Pipeline`으로 묶으세요. `model`에 담고 학습하세요. 테스트 예측은 `prediction`에 저장하세요. MAE는 `linear_mae`에 저장해 출력하세요. `model.named_steps['model'].coef_`로 가중치 네 개도 출력하세요.

        `linear_mae`를 앞 단원의 기준 MAE와 비교해 보세요. 가중치 네 개 중 어느 것이 가장 큰지도 보세요.
        """,
        hint="""
        분류와 같은 흐름이에요. `Pipeline([('scale', StandardScaler()), ('model', LinearRegression())])` → `fit(X_train, y_train)` → `predict(X_test)`. 점수는 `mean_absolute_error(y_test, prediction)`.
        """,
        starter=STOCK_MODEL + "# model, prediction, linear_mae를 만들고 출력하세요\n",
        solution=STOCK_MODEL + "model = Pipeline([('scale', StandardScaler()), ('model', LinearRegression())])\nmodel.fit(X_train, y_train)\nprediction = model.predict(X_test)\nlinear_mae = mean_absolute_error(y_test, prediction)\nprint(linear_mae)\nprint(model.named_steps['model'].coef_)\n",
        check="import numpy as np\n\nassert len(s['prediction']) == 80 and np.isfinite(s['linear_mae'])\nassert len(s['model'].named_steps['model'].coef_) == 4\nassert abs(s['linear_mae'] - float(np.abs(s['y_test'].to_numpy() - s['prediction']).mean())) < 1e-8"),
    coding('regression-table', '기준과 세 모델을 한 표에',
        goal="""
        분류 비교표와 같은 표를 회귀로 만들어요. `models`에 `Linear`, `Ridge(alpha=1)`, `Lasso(alpha=10, max_iter=20000, tol=0.001)`를 넣으세요. 각각 `StandardScaler`와 묶어 학습하세요. 테스트 예측은 `predictions` 딕셔너리에 모으세요. `predictions`에는 기준 예측 `Baseline`(오늘 종가)도 함께 넣고요. 그다음 네 예측 각각의 `MAE`, `RMSE`, `R2`를 구해 `results` 표를 만드세요. 학습한 모델은 `fitted`에 보관하고요.

        `results`는 네 행 세 열이에요. 기준을 넘는 모델이 있는지, RMSE가 MAE보다 얼마나 큰지 보세요.
        """,
        hint="""
        시작은 `predictions = {'Baseline': X_test['close'].to_numpy()}`예요. `for name, estimator in models.items():` 안에서 `Pipeline`을 만들어 `fit`하세요. 그리고 `predictions[name] = model.predict(X_test)`, `fitted[name] = model`. 둘째 반복 `for name, pred in predictions.items():` 안에는 이 한 줄만 들어가요. `rows.append({'model': name, 'MAE': mean_absolute_error(y_test, pred), 'RMSE': mean_squared_error(y_test, pred) ** 0.5, 'R2': r2_score(y_test, pred)})`. 끝으로 `results = pd.DataFrame(rows).set_index('model')`.
        """,
        starter=STOCK_MODEL + "# models, predictions, results를 만드세요\n",
        solution=STOCK_MODEL + "models = {'Linear': LinearRegression(), 'Ridge': Ridge(alpha=1), 'Lasso': Lasso(alpha=10, max_iter=20000, tol=0.001)}\npredictions = {'Baseline': X_test['close'].to_numpy()}\nfitted = {}\nfor name, estimator in models.items():\n    model = Pipeline([('scale', StandardScaler()), ('model', estimator)])\n    model.fit(X_train, y_train)\n    predictions[name] = model.predict(X_test)\n    fitted[name] = model\nrows = []\nfor name, pred in predictions.items():\n    rows.append({'model': name, 'MAE': mean_absolute_error(y_test, pred), 'RMSE': mean_squared_error(y_test, pred) ** 0.5, 'R2': r2_score(y_test, pred)})\nresults = pd.DataFrame(rows).set_index('model')\nresults\n",
        check="import numpy as np\n\nassert set(s['results'].index) == {'Baseline', 'Linear', 'Ridge', 'Lasso'}\nassert set(s['results'].columns) == {'MAE', 'RMSE', 'R2'}\nassert np.isfinite(s['results'].to_numpy()).all()\nassert (s['results']['RMSE'] >= s['results']['MAE']).all()\nassert all(len(p) == 80 for p in s['predictions'].values())\nassert set(s['fitted']) == {'Linear', 'Ridge', 'Lasso'}\nassert all(m.named_steps['scale'].n_samples_seen_ == 315 for m in s['fitted'].values())"),
    quiz('midpoint', '비교표 중간 확인',
        choice('네 예측의 점수를 비교할 때 반드시 같아야 하는 것은 무엇인가요?',
               ['테스트 기간과 정답 `y_test`', '모델 이름의 길이', '학습에 걸린 시간'], 0,
               '테스트 기간과 정답 `y_test`예요. 다른 기간의 점수는 비교할 수 없어요. 기준과 세 모델 모두 같은 80일, 같은 정답으로 채점했어요. 그래서 이 표를 믿고 읽을 수 있어요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「이름의 길이」: 결과와 무관해요.\n- 「학습 시간」: 달라도 비교는 공정해요."),
        choice('어떤 모델의 RMSE가 MAE보다 유난히 크다면 무엇을 뜻하나요?',
               ['가끔 크게 틀리는 날이 있다', '항상 조금씩 틀린다', '예측이 전부 맞았다'], 0,
               '가끔 크게 틀리는 날이 있다는 뜻이에요. RMSE는 큰 오차를 제곱해 더 무겁게 세거든요. 둘의 차이가 크면 오차가 고르지 않고 몇몇 날에 몰려 있는 거죠.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「항상 조금씩」: 그러면 둘이 비슷해요.\n- 「전부 맞았다」: 둘 다 0이 돼요."),
    ),
    coding('beat-baseline', '기준보다 나아졌는지 판정하기',
        goal="""
        ```comic-gen
        제목: 이길 때까지 돌리면
        등장인물:
          민지:
            그림: 사람
            이름표: 민지
            외형: {머리모양: 단발, 머리색: "#573d36", 옷: 후드, 옷색: "#609b87"}
          강사:
            그림: 사람
            이름표: 강사
            외형: {옷: 재킷, 옷색: "#5379a7", 안경: true}
        컷:
          - 인물: [{식별자: 민지, 표정: 슬픔}, 강사]
            대사:
              - {화자: 민지, 상대: 강사, 내용: "릿지가 기준보다 못해요. 기간을 바꿔 다시 돌릴까요?"}
              - {화자: 강사, 상대: 민지, 내용: "그건 모의고사 문제를 고르는 거예요."}
          - 구성: 이전
            인물: [{식별자: 민지, 표정: 보통}, {식별자: 강사, 손모양: 가리키는손}]
            대사:
              - {화자: 강사, 상대: 민지, 내용: "개선 못 했으면 못 했다고 그대로 적으세요."}
              - {화자: 민지, 상대: 강사, 내용: "못 이긴 것도 결과네요."}
        ```

        비교를 참·거짓 하나로 정리해요. 기준 예측의 MAE를 `baseline_mae`에 저장하세요. `Ridge(alpha=1)` 파이프라인의 MAE는 `ridge_mae`에 저장하세요. `improved`에는 `ridge_mae < baseline_mae`의 결과를 담으세요. 세 값을 출력하세요.

        `improved`가 `False`로 나와도 틀린 게 아니에요. 그게 이 기간의 사실이에요. 검사는 계산이 맞는지만 봐요.
        """,
        hint="""
        `baseline_mae = mean_absolute_error(y_test, X_test['close'])`로 기준부터 구하세요. 릿지는 `Pipeline([('scale', StandardScaler()), ('model', Ridge(alpha=1))])`예요. 학습·예측해서 MAE를 구하세요. 끝으로 `improved = bool(ridge_mae < baseline_mae)`.
        """,
        starter=STOCK_MODEL + "# baseline_mae, ridge_mae, improved를 만들고 출력하세요\n",
        solution=STOCK_MODEL + "baseline_mae = mean_absolute_error(y_test, X_test['close'])\nridge = Pipeline([('scale', StandardScaler()), ('model', Ridge(alpha=1))])\nridge.fit(X_train, y_train)\nridge_mae = mean_absolute_error(y_test, ridge.predict(X_test))\nimproved = bool(ridge_mae < baseline_mae)\nprint(baseline_mae, ridge_mae, improved)\n",
        check="import numpy as np\n\nassert abs(s['baseline_mae'] - float(np.abs(s['y_test'].to_numpy() - s['X_test']['close'].to_numpy()).mean())) < 1e-8\nassert np.isfinite(s['ridge_mae'])\nassert s['improved'] == (s['ridge_mae'] < s['baseline_mae'])"),
    coding('forecast-plot', '정답 날짜 위에 실제와 예측을 겹쳐 그리기',
        goal="""
        마지막 그래프예요. 릿지 파이프라인을 학습해 `prediction`을 구하세요. 그다음 `target_date`를 인덱스로 `comparison` 표를 만드세요. 열은 `actual`(실제 다음 종가)과 `prediction` 둘이에요. `fig, ax`에 두 선을 같은 날짜 축에 그리세요. x축 이름은 `정답 날짜`, 범례도 표시하고요.

        x축이 입력 날짜가 아니라 **정답 날짜**인 이유를 생각해 보세요. 예측이 실제를 얼마나 따라가는지, 어느 구간에서 벌어지는지 보세요.
        """,
        hint="""
        표는 `comparison = pd.DataFrame({'actual': y_test.to_numpy(), 'prediction': prediction}, index=pd.DatetimeIndex(frame.loc[test_mask, 'target_date']))`로 만들어요. 실제 선은 `ax.plot(comparison.index, comparison['actual'], label='Actual next close')`로 그려요. 예측 선도 하나 더요. 마무리는 `ax.set(xlabel='정답 날짜', ...)`, `ax.legend()`, `plt.show()`.
        """,
        starter=STOCK_MODEL + PLOT + "# model, prediction, comparison, fig, ax를 만드세요\n",
        solution=STOCK_MODEL + PLOT + "model = Pipeline([('scale', StandardScaler()), ('model', Ridge(alpha=1))])\nmodel.fit(X_train, y_train)\nprediction = model.predict(X_test)\ncomparison = pd.DataFrame({'actual': y_test.to_numpy(), 'prediction': prediction}, index=pd.DatetimeIndex(frame.loc[test_mask, 'target_date']))\nfig, ax = plt.subplots()\nax.plot(comparison.index, comparison['actual'], label='Actual next close')\nax.plot(comparison.index, comparison['prediction'], label='Ridge')\nax.set(xlabel='정답 날짜', ylabel='Price', title='Held-out next trading day')\nax.legend()\nplt.show()\ncomparison.head()\n",
        check="assert s['comparison'].shape == (80, 2) and list(s['comparison'].columns) == ['actual', 'prediction']\nassert list(s['comparison'].index) == list(s['frame'].loc[s['test_mask'], 'target_date'])\nassert len(s['ax'].lines) == 2 and s['ax'].get_xlabel() == '정답 날짜'\nassert s['ax'].get_legend() is not None"),
    coding('final-report', '최종 보고: 숫자 다섯 개와 결론 세 줄',
        goal="""
        수업의 결론을 코드로 적어요. 준비된 `models`(`Linear`, `Ridge`)를 각각 학습해 테스트 MAE를 `maes` 딕셔너리에 모으세요. 기준 MAE와 비교해 `report` 딕셔너리를 만드세요. 키는 다섯 개예요.

        - `test_days`: 테스트 거래일 수
        - `baseline_mae`: 기준 MAE
        - `best_model`: MAE가 가장 작은 모델 이름
        - `best_mae`: 그 모델의 MAE
        - `improved`: 최선 모델이 기준보다 나은지

        그리고 결론 세 줄을 출력하세요. ① 무엇을 언제 예측했고 어떻게 나눴는지 ② 기준 MAE와 최선 모델 MAE ③ 개선했는지 못 했는지.

        검사는 다섯 숫자가 실제 계산과 맞는지만 봐요. `improved`가 `False`여도 정직하게 적은 보고가 정답이에요.
        """,
        hint="""
        `maes = {}`를 두세요. `for name, estimator in models.items():` 안에서 파이프라인을 학습하세요. 점수는 `maes[name] = mean_absolute_error(y_test, model.predict(X_test))`. 최선 모델은 `best_model = min(maes, key=maes.get)`. `report = {'test_days': len(X_test), 'baseline_mae': ..., 'best_model': best_model, 'best_mae': maes[best_model], 'improved': bool(maes[best_model] < baseline_mae)}`. 출력은 `print(f'...{report["baseline_mae"]:.0f}원...')`처럼 f-string으로.
        """,
        starter=STOCK_MODEL + "models = {'Linear': LinearRegression(), 'Ridge': Ridge(alpha=1)}\n# maes, report를 만들고 결론 세 줄을 출력하세요\n",
        solution=STOCK_MODEL + "models = {'Linear': LinearRegression(), 'Ridge': Ridge(alpha=1)}\nbaseline_mae = mean_absolute_error(y_test, X_test['close'])\nmaes = {}\nfor name, estimator in models.items():\n    model = Pipeline([('scale', StandardScaler()), ('model', estimator)])\n    model.fit(X_train, y_train)\n    maes[name] = mean_absolute_error(y_test, model.predict(X_test))\nbest_model = min(maes, key=maes.get)\nreport = {'test_days': len(X_test), 'baseline_mae': baseline_mae, 'best_model': best_model, 'best_mae': maes[best_model], 'improved': bool(maes[best_model] < baseline_mae)}\nprint(f\"다음 거래일 종가를 예측했고, 마지막 {report['test_days']}거래일을 테스트로 두었으며 훈련 정답은 모두 테스트 시작 전이다.\")\nprint(f\"기준 예측(오늘 종가 그대로) MAE {baseline_mae:.0f}원, 최선 모델 {best_model} MAE {maes[best_model]:.0f}원.\")\nprint('최선 모델이 기준보다 오차를 줄였다.' if report['improved'] else '최선 모델도 기준보다 오차를 줄이지 못했다. 이 파일, 이 기간의 결과다.')\n",
        check="import numpy as np\n\nr = s['report']\nassert {'test_days', 'baseline_mae', 'best_model', 'best_mae', 'improved'} <= set(r)\nassert r['test_days'] == 80\nassert abs(r['baseline_mae'] - float(np.abs(s['y_test'].to_numpy() - s['X_test']['close'].to_numpy()).mean())) < 1e-8\nassert set(s['maes']) == {'Linear', 'Ridge'} and all(np.isfinite(v) for v in s['maes'].values())\nassert r['best_model'] == min(s['maes'], key=s['maes'].get) and abs(r['best_mae'] - min(s['maes'].values())) < 1e-9\nassert r['improved'] == (r['best_mae'] < r['baseline_mae'])"),
    quiz('final-check', '단원 점검',
        short('예측과 정답의 차이를 부호 없이 평균 낸 지표예요. 원 단위로 읽죠. 약어는 무엇인가요?', ['MAE', 'mae', 'mean absolute error'],
              'MAE는 "하루 평균 몇 원 빗나갔나"예요. 주가 챕터 내내 기준과 모델을 비교한 잣대죠.'),
        choice('R²가 음수로 나왔어요. 무슨 뜻인가요?',
               ['정답의 평균값으로만 찍은 것보다도 못 맞혔다', '계산이 틀렸다', '모델이 완벽하다'], 0,
               '평균으로만 찍은 것보다도 못 맞혔다는 뜻이에요. R²는 "평균으로 찍기"와 비교해 1을 만점으로 적은 값이에요. 그보다 못하면 음수가 되죠. 비교 대상이 우리의 기준(오늘 종가)이 아니라는 점도 기억하세요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「완벽하다」: 완벽하면 1이에요.\n- 「계산이 틀렸다」: 음수는 정상적으로 나올 수 있어요."),
        choice('릿지 MAE 1800원, 기준 MAE 1500원이면 보고서에 어떻게 적어야 하나요?',
               ['이 기간에서 릿지는 기준보다 오차가 커 개선하지 못했다', '릿지가 더 복잡한 모델이니 더 좋다', '기준은 모델이 아니므로 무시한다'], 0,
               '개선하지 못했다고 적어요. 같은 기간, 같은 정답에서 숫자를 그대로 비교해 적는 거예요. 기준보다 못한 결과도 결과예요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「복잡하니 더 좋다」: 복잡함은 점수가 아니에요.\n- 「기준은 무시」: 기준이 바로 비교의 선이에요."),
        short('마지막 그래프의 x축은 입력 날짜가 아니라 어느 날짜였나요? (열 이름)', ['target_date', '정답 날짜', '정답날짜'],
              '`target_date`예요. 실제값과 예측값은 모두 "다음 거래일"의 값이에요. 그래서 그 날짜 위에 그려야 맞아요.'),
        choice('테스트 점수가 마음에 안 들어요. 기간을 바꿔 가며 다시 돌리면 어떤 문제가 생기나요?',
               ['모의고사 문제를 고르는 셈이라 점수가 실력을 반영하지 않게 된다', '컴퓨터가 느려진다', '아무 문제 없다'], 0,
               '점수가 실력을 보여 주지 못해요. 테스트는 한 번만 채점하는 모의고사거든요. 기간을 고르기 시작하면 테스트가 훈련의 일부가 돼요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「컴퓨터가 느려진다」: 속도 문제가 아니에요.\n- 「아무 문제 없다」: 좋은 점수만 고르는 셈이 돼요."),
        short('선형 회귀가 학습한 입력별 가중치를 보는 속성은 무엇인가요? (`model.named_steps[\'model\'].____`)', ['coef_', 'coef'],
              '`coef_`예요. 입력 열마다 가중치가 하나씩 들어 있어요. 표준화된 입력 기준이라 크기를 서로 비교할 수 있죠.'),
    ),
    quiz('course-wrap', '수업을 한 줄로 잇기',
        choice('타이타닉의 `구명보트` 열과 주가의 `target_next_close` 열의 공통점은 무엇인가요?',
               ['맞히려는 시점에 알 수 없는 정보라 입력에 넣으면 누수다', '둘 다 글자 열이다', '둘 다 빈칸이 많다'], 0,
               '둘 다 맞히려는 시점에 알 수 없는 정보예요. 하나는 사고 뒤에 적힌 정보, 하나는 내일의 값이죠. 자료가 달라도 "맞히는 시점에 아는 것만 입력"이라는 원칙은 같아요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「둘 다 글자 열」: 종가는 숫자예요.\n- 「빈칸이 많다」: 빈칸이 문제가 아니라 시점이에요."),
        choice('타이타닉의 "전원 사망"과 주가의 "오늘 종가 그대로" 예측은 어떤 역할이었나요?',
               ['모델이 넘어야 할 기준', '가장 정확한 모델', '오류를 내는 예'], 0,
               '모델이 넘어야 할 기준이에요. 분류든 회귀든 기준이 있어야 모델이 배운 몫이 보이죠. 기준을 못 넘으면 아무것도 배우지 못한 거예요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「가장 정확한 모델」: 가장 단순한 비교 기준이에요.\n- 「오류를 내는 예」: 오류 없이 정상 동작해요."),
        choice('타이타닉은 무작위로 나누고 주가는 날짜순으로 나눈 이유는 무엇인가요?',
               ['승객끼리는 순서가 없지만 날짜는 순서가 있어서', '주가 자료가 더 커서', '분류와 회귀의 차이 때문에'], 0,
               '승객끼리는 순서가 없지만 날짜는 순서가 있어서예요. 시간 순서가 있는 자료를 무작위로 섞으면 미래로 과거를 맞히게 돼요. 나누는 방법은 자료의 성질이 정해요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「자료가 더 커서」: 크기와 무관해요.\n- 「분류와 회귀의 차이」: 분류라도 시간 자료면 날짜순이에요."),
        choice('빈 나이를 중앙값으로 채울 때 그 중앙값을 훈련 자료에서만 구한 이유는 무엇인가요?',
               ['테스트 자료를 미리 보는 작은 누수를 막으려고', '테스트 자료에는 빈칸이 없어서', '계산이 빨라서'], 0,
               '테스트 자료를 미리 보는 작은 누수를 막으려고요. 손질 기준을 정하는 것도 학습이에요. 훈련에서 정하고 테스트에는 적용만 하는 규칙이 `Pipeline`으로 이어졌죠.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「테스트에 빈칸이 없어서」: 테스트에도 빈칸이 있어요.\n- 「계산이 빨라서」: 속도 문제가 아니에요."),
        choice('분류의 정확도와 회귀의 MAE에 공통으로 적용되는 주의점은 무엇인가요?',
               ['숫자 하나만 보지 말고 기준과 비교하고, 무엇을 몇 개로 잰 점수인지 함께 적는다', '높을수록 무조건 좋다', '훈련 자료로 재야 정확하다'], 0,
               '기준과 비교하고, 무엇을 몇 개로 잰 점수인지 함께 적어야 해요. 정확도 78%도, MAE 1500원도 혼자서는 뜻이 없거든요. 기준과 분모가 붙어야 읽을 수 있는 숫자가 되죠.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「훈련 자료로 재야」: 훈련 점수는 외운 점수예요.\n- 「높을수록 좋다」: MAE는 낮을수록 좋아요. 정확도도 기준과 비교해야 하고요."),
        choice("""**프롬프트 고르기** · 릿지 MAE가 기준보다 나쁘게 나왔어요. AI에게 다음 작업을 시킬 때 올바른 프롬프트는 무엇인가요?""",
               ["""같은 테스트 기간에서 기준 MAE와 릿지 MAE를 그대로 적고, improved = ridge_mae < baseline_mae가 False라는 결론을 보고서에 그대로 써 줘. 기간이나 하이퍼파라미터를 바꿔 다시 돌리지 마""", """기준을 이길 때까지 alpha 바꿔 가며 돌려 줘""", """테스트 기간을 바꿔서 다시 해 봐""", """기준 모델은 빼고 릿지 결과만 보고해 줘"""], 0,
               """정답은 정직한 비교를 요구하고 결과를 고르지 말라고 못 박았어요. AI한테 "개선"을 시키면 조건을 바꿔서라도 이기는 결과를 만들려고 해요.

**다른 보기는 왜 아닌가**

- 「이길 때까지 alpha」: 테스트로 하이퍼파라미터를 고르는 누수예요.
- 「테스트 기간을 바꿔」: 모의고사를 골라 치는 셈이에요.
- 「기준 모델은 빼고」: 비교의 선이 사라져요."""),
        choice("""**프롬프트 고르기** · 최종 보고를 AI에게 쓰게 하려고 해요. 어떤 프롬프트가 수업에서 요구한 구조의 보고서를 줄까요?""",
               ["""report 딕셔너리(test_days, baseline_mae, best_model, best_mae, improved) 값을 그대로 써서 세 줄로: ① 무엇을 언제 예측했고 어떻게 나눴는지 ② 기준 MAE와 최선 MAE ③ 개선 여부. 이 파일·이 기간에서만 본 결과라는 한계 한 줄 추가""", """멋진 보고서 써 줘""", """모델이 얼마나 좋은지 강조해서 써 줘""", """결과 요약해 줘"""], 0,
               """정답은 숫자의 출처(report 변수), 세 줄 구조, 한계 문장까지 지정했어요. 보고서의 구조를 주면 AI는 그 틀을 채워요.

**다른 보기는 왜 아닌가**

- 「멋진 보고서」: 구조도 숫자도 없어 꾸밈말이 와요.
- 「좋은지 강조」: 기준보다 못한 결과를 숨기게 돼요.
- 「결과 요약해 줘」: 무엇을 어떤 순서로 요약할지 없어요."""),
    ),
])
