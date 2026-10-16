"""시간 분리와 기준 모델"""
from kpc_course.dsl import *

CALLS = PD + "calls = pd.DataFrame({'week': [1] * 7 + [2] * 7, 'weekday': ['월', '화', '수', '목', '금', '토', '일'] * 2, 'calls': [1320, 980, 940, 910, 1010, 420, 380, 1410, 1020, 960, 890, 1050, 450, 360]})\n"

UNIT = unit('stock-split', '시간 분리와 기준 모델', [
    concept('temporal-boundary', '시간은 섞으면 안 되고, 경계의 하루도 조심해야 한다',
        body="""
        타이타닉에서는 `train_test_split`이 승객을 무작위로 섞었어요. 그렇게 훈련과 테스트를 나눴죠. 승객끼리는 순서가 없으니 괜찮았고요. 주가는 달라요. 날짜를 무작위로 섞으면 어떻게 될까요? 6월 가격으로 학습한 모델이 3월 가격을 맞히는 꼴이 돼요. 미래를 보고 과거를 맞히면 그건 시험이 아니죠. 그래서 시간 자료는 **앞쪽 기간으로 학습하고 뒤쪽 기간으로 테스트**해요. 여기서는 마지막 80거래일을 테스트로 떼어 둬요.

        ```comic-gen
        제목: 섞으면 점쟁이가 된다
        등장인물:
          모델: {그림: 서버, 이름표: 모델}
          강사:
            그림: 사람
            이름표: 강사
            외형: {옷: 재킷, 옷색: "#5379a7", 안경: true}
        컷:
          - 인물: [{식별자: 모델, 표정: 기쁨}, 강사]
            대사:
              - {화자: 모델, 상대: 강사, 내용: "날짜를 섞어서 나눴더니 5월 종가를 거의 다 맞혔어요!"}
              - {화자: 강사, 상대: 모델, 내용: "훈련 자료에 6월 가격이 들어 있었죠?"}
          - 구성: 이전
            인물: [{식별자: 모델, 표정: 슬픔}, {식별자: 강사, 손모양: 가리키는손}]
            대사:
              - {화자: 강사, 상대: 모델, 내용: "미래를 보고 과거를 맞힌 거예요. 실제 내일은 그렇게 안 보여요."}
              - {화자: 모델, 상대: 강사, 내용: "앞 기간으로 배우고 뒤 기간으로 채점할게요."}
        ```

        ```comic-gen
        제목: 시간은 섞지 않는다
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
          - 인물: [준호, 강사]
            대사:
              - 화자: 준호
                상대: 강사
                내용: |-
                  타이타닉처럼 train_test_split으로
                  섞으면 안 돼요?
              - {화자: 강사, 상대: 준호, 내용: "6월 가격으로 배워서 3월을 맞히게 돼요."}
          - 구성: 이전
            인물: [{식별자: 준호, 표정: 기쁨}, {식별자: 강사, 손모양: 가리키는손}]
            대사:
              - {화자: 준호, 상대: 강사, 내용: "미래를 보고 과거를 맞히는 거네요."}
              - 화자: 강사
                상대: 준호
                내용: |-
                  앞 기간으로 배우고 뒤 기간으로 채점해요.
                  그게 전부예요.
        ```

        ```interactive
        위젯: temporal
        ```

        그런데 경계를 하루 잘못 그으면 작은 누수가 숨어들어요. 테스트가 시작되는 날을 `test_start`라고 할게요. 그 바로 전날 행을 보세요. 입력 날짜는 테스트 전이라 훈련에 넣어도 될 것 같죠? 그 행의 **정답**은 `test_start` 당일 종가거든요. 테스트 첫날의 답을 훈련에서 이미 본 셈이에요.

        | 행의 날짜 | 정답 날짜 | 훈련에 넣어도 되나 |
        | --- | --- | --- |
        | test_start 이틀 전 | test_start 하루 전 | 된다 |
        | test_start 하루 전 | **test_start** | 안 된다. 정답이 테스트 기간 |
        | test_start | test_start 다음 거래일 | 테스트 |

        그래서 훈련 조건은 둘이에요. 입력 날짜도 `test_start` 전, 그리고 `target_date`도 `test_start` 전. 앞 단원에서 `target_date`를 남겨 둔 이유가 바로 이거예요.

        ```python
        test_start = frame.index[-80]
        train_mask = (frame.index < test_start) & (frame['target_date'] < test_start)
        test_mask = frame.index >= test_start
        X_train, X_test = X.loc[train_mask], X.loc[test_mask]
        ```

        나눴으면 기준 모델이에요. 분류의 "전원 사망" 자리에 오는 가장 단순한 예측이 뭘까요? **"내일 종가는 오늘 종가와 같다"**예요. 우습게 들리지만 주가에서는 이 기준을 이기기가 생각보다 어려워요.

        점수는 정확도 대신 **MAE**(평균 절대 오차)로 재요. 예측과 정답의 차이를 부호 없이 평균 낸 거예요. 그래서 단위가 원이에요. "평균 몇 원 빗나갔나"로 읽으면 돼요. 작을수록 좋고요.
        """,
        check=short('"내일 종가는 오늘 종가와 같다"처럼 가장 단순한 예측을 두고 모델과 비교해요. 이걸 뭐라고 하나요?', ['기준 모델', '기준모델', '기준 예측', '기준예측', 'baseline', '베이스라인'],
                    '기준(baseline)이 있어야 모델이 실제로 뭘 배웠는지 알 수 있죠. 주가에서는 "오늘 종가 그대로"가 생각보다 강한 기준이에요.')),
    coding('test-start', '테스트 시작일 정하기',
        goal="""
        자, 준비된 `frame`이 있어요. 마지막 80행의 첫 날짜를 `test_start`에 저장하세요. 날짜가 `test_start` 이상인 행 수는 `n_test`에 담아 출력하세요.

        `n_test`가 80이면 맞게 정한 거예요.
        """,
        hint="""
        `frame.index[-80]`이 뒤에서 80번째 날짜예요. `frame.index >= test_start`는 행마다 참·거짓이에요. `.sum()`이 참의 개수죠. `int()`로 감싸 정수로 저장하세요.
        """,
        starter=ST_FRAME + "# test_start, n_test를 만들고 출력하세요\n",
        solution=ST_FRAME + "test_start = frame.index[-80]\nn_test = int((frame.index >= test_start).sum())\nprint(test_start, n_test)\n",
        check="assert s['test_start'] == s['frame'].index[-80] and s['n_test'] == 80"),
    coding('time-boundary', '정답 날짜까지 보고 나누기',
        goal="""
        훈련·테스트를 나눠요. `test_start`를 정하세요. `train_mask`는 두 조건을 **모두** 만족하는 행이에요. 입력 날짜도, `target_date`도 `test_start` 전. 입력 날짜가 `test_start` 이상인 행이 `test_mask`고요. 그걸로 `X_train`, `X_test`, `y_train`, `y_test`를 만드세요. 두 쪽의 행 수도 출력해 보고요.

        396행이 훈련 315, 경계 하루 제외 1, 테스트 80으로 나뉘면 맞게 한 거예요. 훈련 정답의 마지막 날짜가 테스트 첫 날짜보다 앞인지도 출력해 보세요.
        """,
        hint="""
        개념에 있는 네 줄 그대로예요. 두 조건을 괄호로 감싸 `&`로 이으세요. 앞에서 배운 방법이죠. 입력과 정답은 같은 마스크로 함께 고르세요. `X.loc[train_mask]`, `y.loc[train_mask]`처럼요. 그래야 행이 안 어긋나거든요.
        """,
        starter=ST_FRAME + "feature_columns = ['close', 'return_1', 'ma5', 'lag_close_1']\nX = frame[feature_columns]\ny = frame['target_next_close']\n# test_start, 마스크와 네 자료를 만드세요\n",
        solution=ST_FRAME + TIME_SPLIT + "print(len(X_train), len(X_test))\nprint(frame.loc[train_mask, 'target_date'].max(), X_test.index.min())\n",
        check="assert len(s['X_train']) == 315 and len(s['X_test']) == 80\nassert s['frame'].loc[s['train_mask'], 'target_date'].max() < s['X_test'].index.min()\nassert set(s['X_train'].index).isdisjoint(s['X_test'].index)\nassert 'target_next_close' not in s['X_train']"),
    coding('manual-mae', 'MAE를 손으로 계산하기',
        goal="""
        ```interactive
        위젯: mae
        ```

        ```comic-gen
        제목: 얼마나 빗나갔나
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
              - {화자: 민지, 상대: 강사, 내용: "어떤 날은 +500원, 어떤 날은 -500원 빗나갔어요. 평균 내면 0인데요?"}
              - {화자: 강사, 상대: 민지, 내용: "부호를 떼고 평균 내요. 그게 MAE예요."}
          - 구성: 이전
            인물: [{식별자: 민지, 표정: 기쁨}, {식별자: 강사, 손모양: 가리키는손}]
            대사:
              - {화자: 강사, 상대: 민지, 내용: "500과 500의 평균이니 하루 평균 500원 빗나간 거죠."}
              - {화자: 민지, 상대: 강사, 내용: "숫자 하나로 들리네요. 하루 평균 500원."}
        ```

        기준 예측의 오차를 직접 계산해요. 테스트 기간에서 "내일 종가 = 오늘 종가"로 예측해요. 그러면 예측값은 `X_test['close']`예요. 정답 `y_test`와의 차이에 `.abs()`를 붙여 `errors`에 담으세요. 그 평균을 `manual_mae`에 저장하고 출력하세요.

        결과는 원 단위예요. "하루에 평균 이 정도 빗나간다"로 읽으세요. 다음 미션에서 함수로 구한 값과 같은지 비교해요.
        """,
        hint="""
        `errors = (y_test - X_test['close']).abs()`로 오차를 구하세요. 그다음 `manual_mae = errors.mean()`. 이름은 MAE지만 하는 일은 "차이의 절댓값을 평균 낸다" 두 단계뿐이에요.
        """,
        starter=ST_FRAME + TIME_SPLIT + "# errors, manual_mae를 만들고 출력하세요\n",
        solution=ST_FRAME + TIME_SPLIT + "errors = (y_test - X_test['close']).abs()\nmanual_mae = errors.mean()\nprint(manual_mae)\n",
        check="import numpy as np\n\nassert len(s['errors']) == 80 and (s['errors'] >= 0).all()\nassert abs(s['manual_mae'] - float(np.abs(s['y_test'].to_numpy() - s['X_test']['close'].to_numpy()).mean())) < 1e-8"),
    coding('close-baseline', '같은 계산을 함수로',
        goal="""
        `scikit-learn`의 `mean_absolute_error`로 같은 값을 구해요. 기준 예측 `X_test['close']`를 배열로 바꿔 `baseline_pred`에 저장하세요. 점수는 `mean_absolute_error(y_test, baseline_pred)`예요. `baseline_mae`에 담아 출력하세요.

        앞 미션의 `manual_mae`와 같은 숫자가 나와야 해요. 이 값이 이 챕터의 모든 모델이 넘어야 할 선이에요.
        """,
        hint="""
        `baseline_pred = X_test['close'].to_numpy()`로 배열을 만드세요. 점수는 `baseline_mae = mean_absolute_error(y_test, baseline_pred)`. 지표 함수는 앞서처럼 `(정답, 예측)` 순서예요.
        """,
        starter=ST_FRAME + TIME_SPLIT + "from sklearn.metrics import mean_absolute_error\n# baseline_pred와 baseline_mae를 만드세요\n",
        solution=ST_FRAME + TIME_SPLIT + "from sklearn.metrics import mean_absolute_error\n\nbaseline_pred = X_test['close'].to_numpy()\nbaseline_mae = mean_absolute_error(y_test, baseline_pred)\nprint(baseline_mae)\n",
        check="import numpy as np\n\nassert np.array_equal(s['baseline_pred'], s['X_test']['close'].to_numpy())\nassert abs(s['baseline_mae'] - float(np.abs(s['y_test'].to_numpy() - s['X_test']['close'].to_numpy()).mean())) < 1e-8"),
    coding('callcenter-baseline', '콜센터 월요일, 지난주와 같다고 보면',
        intro="""
        주가에서 잠깐 벗어나 같은 기준 모델을 콜센터에 적용해요. 어느 카드사 콜센터의 2주치 일별 통화량이 준비돼 있어요. 주말에 쌓인 전화가 몰려 월요일이 가장 많거든요. 팀장은 매주 "지난주 같은 요일과 같다"고 보고 상담원을 배치해 왔죠. 이 방법이 얼마나 빗나가는지가 통화량 예측 모델이 넘어야 할 선이에요.
        """,
        goal="""
        `calls`에서 1주차 통화량을 배열 `last_week`에 저장하세요. 2주차 통화량은 배열 `this_week`에 담고요. 1주차 값을 2주차 예측으로 쓰는 게 기준 모델이에요. 그러니 점수는 `mean_absolute_error(this_week, last_week)`예요. `baseline_mae`에 담아 출력하세요. 월요일 하루의 오차는 `monday_error`에 따로 저장하세요.

        통화 한 건에 평균 5분이 걸린다고 해 볼게요. 이 MAE는 하루에 몇 분의 통화가 밀리거나 비는지 생각해 보세요. 월요일만 보면 어떤가요?
        """,
        hint="""
        `last_week = calls[calls['week'] == 1]['calls'].to_numpy()`로 1주차를 꺼내세요. 2주차도 같은 모양이에요. 지표 함수는 `(정답, 예측)` 순서예요. 그러니 정답은 `this_week`, 예측은 `last_week`. 월요일은 두 배열의 첫 값이에요. 그래서 `monday_error = abs(this_week[0] - last_week[0])`.
        """,
        starter=CALLS + "from sklearn.metrics import mean_absolute_error\n# last_week, this_week, baseline_mae, monday_error를 만드세요\n",
        solution=CALLS + "from sklearn.metrics import mean_absolute_error\n\nlast_week = calls[calls['week'] == 1]['calls'].to_numpy()\nthis_week = calls[calls['week'] == 2]['calls'].to_numpy()\nbaseline_mae = mean_absolute_error(this_week, last_week)\nmonday_error = abs(this_week[0] - last_week[0])\nprint(baseline_mae, monday_error)\n",
        check="import numpy as np\n\nassert np.array_equal(s['last_week'], [1320, 980, 940, 910, 1010, 420, 380]) and np.array_equal(s['this_week'], [1410, 1020, 960, 890, 1050, 450, 360])\nassert abs(s['baseline_mae'] - 260 / 7) < 1e-8 and int(s['monday_error']) == 90"),
    quiz('temporal-check', '단원 점검',
        choice('주가 자료를 `train_test_split`처럼 무작위로 섞어 나누면 어떤 문제가 생기나요?',
               ['미래 가격으로 훈련해 과거를 맞히게 되어 점수를 믿을 수 없다', '행 수가 줄어든다', '아무 문제 없다'], 0,
               '미래로 과거를 맞히게 돼서 점수를 믿을 수 없어요. 승객은 순서가 없지만 날짜는 순서가 있거든요. 시간 자료는 앞 기간으로 학습하고 뒤 기간으로 테스트해요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「행 수가 줄어든다」: 행 수는 같아요. 순서가 섞여요.\n- 「아무 문제 없다」: 미래로 과거를 맞히게 돼요."),
        choice('`test_start` 하루 전 행을 훈련에서 빼야 하는 이유는 무엇인가요?',
               ['그 행의 정답이 `test_start` 당일 종가라 테스트 첫날의 답을 훈련에서 보게 된다', '입력이 비어 있어서', '가격이 너무 높아서'], 0,
               '그 행의 정답이 `test_start` 당일 종가라서예요. 입력 날짜만 보면 훈련 같지만 정답 날짜가 테스트 기간이죠. 그래서 `target_date`도 `test_start` 전이어야 해요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「가격이 너무 높아서」: 가격 크기와 무관해요.\n- 「입력이 비어 있어서」: 입력은 다 있어요. 정답 날짜가 문제예요."),
        short('396행을 나누면 테스트 80행, 경계 제외 1행, 훈련은 몇 행인가요?', ['315', '315행'],
              '396에서 80과 1을 빼면 315예요. 두 조건을 모두 만족하는 행만 훈련에 들어가요.'),
        choice('MAE가 1500이면 무슨 뜻인가요?',
               ['예측이 하루 평균 약 1500원 빗나간다', '정확도가 15%다', '1500일을 예측했다'], 0,
               '예측이 하루 평균 약 1500원 빗나간다는 뜻이에요. MAE는 예측과 정답의 차이를 부호 없이 평균 낸 값이에요. 그래서 단위가 정답과 같은 원이죠. 작을수록 좋고요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「정확도 15%」: 회귀에는 정확도가 없어요.\n- 「1500일」: 날짜 수가 아니라 원 단위 오차예요."),
        choice('"내일 종가는 오늘 종가와 같다"는 기준 예측은 어떤 역할을 하나요?',
               ['모델이 이 오차보다 작아야 무언가 배운 것이라는 선', '가장 좋은 모델', '쓸모없는 농담'], 0,
               '모델이 넘어야 할 선이에요. 분류의 "전원 사망"과 같은 역할이죠. 주가에서는 이 단순한 기준을 이기기가 쉽지 않아요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「쓸모없는 농담」: 이기기 어려운 진지한 기준이에요.\n- 「가장 좋은 모델」: 모델이 아니라 비교 기준이에요."),
        choice("""**프롬프트 고르기** · 주가 자료를 훈련·테스트로 나눠요. 경계 하루의 누수까지 막아야 해요. 어떤 프롬프트가 맞을까요?""",
               ["""pandas. test_start = frame.index[-80]. 입력 날짜와 target_date가 둘 다 test_start 전인 행을 train_mask, 입력 날짜가 test_start 이상인 행을 test_mask로 만들어 X_train, X_test, y_train, y_test. 훈련 315, 테스트 80. 코드만""", """train_test_split으로 8:2 나눠 줘""", """마지막 80일을 테스트로 떼 줘""", """시간 순서대로 나눠 줘"""], 0,
               """정답은 시간 분리에 더해 경계 조건까지 적었어요. "target_date도 test_start 전"이라는 조건이요. 이 조건은 AI가 거의 항상 빼먹어요.

**다른 보기는 왜 아닌가**

- 「train_test_split으로」: 날짜를 섞어 미래로 과거를 맞혀요.
- 「마지막 80일을 테스트로」: 경계 하루(정답이 테스트 기간인 행)가 훈련에 남아요.
- 「시간 순서대로」: 경계 조건과 행 수 검산이 없어요."""),
        choice("""**프롬프트 고르기** · "내일 종가 = 오늘 종가" 기준 예측의 MAE를 구해야 해요. 함수 인자 순서까지 맞춘 프롬프트는 무엇인가요?""",
               ["""scikit-learn. 기준 예측 X_test['close'].to_numpy()를 baseline_pred에, mean_absolute_error(y_test, baseline_pred)를 baseline_mae에 담아 출력. 코드만""", """기준 모델 점수 내 줘""", """mean_absolute_error(baseline_pred, y_test) 계산해 줘""", """오늘 종가로 내일 맞히면 몇 점이야?"""], 0,
               """정답은 셋을 적었어요. 기준 예측이 무엇인지, 지표 함수의 (정답, 예측) 순서, 결과 변수.

**다른 보기는 왜 아닌가**

- 「기준 모델 점수」: 어떤 기준, 어떤 지표인지 없어요.
- 「(baseline_pred, y_test)」: 인자 순서가 바뀌었어요. MAE는 값이 같지만, 이 버릇은 다른 지표에서 값을 바꿔요.
- 「몇 점이야?」: 숫자만 오고 변수가 없어요."""),
    ),
])
