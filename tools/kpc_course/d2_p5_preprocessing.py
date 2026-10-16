"""분리와 전처리 Pipeline"""
from kpc_course.dsl import *

UNIT = unit('preprocessing', '분리와 전처리 Pipeline', [
    concept('fit-train', '기준은 훈련 자료에서만 정한다',
        body="""
        앞 단원에서 입력 `X`와 정답 `y`를 만들었죠? 이제 둘을 훈련 자료와 테스트 자료로 나눠요. 손으로 자르지 않고 `train_test_split`에 맡기죠. 인자 세 개의 뜻만 알면 되거든요. `test_size=0.2`는 20%를 테스트로 떼어 두라는 뜻이에요. `stratify=y`는 두 쪽의 생존 비율을 비슷하게 맞추라는 뜻이고요. `random_state=42`는 누가 실행해도 똑같이 나뉘게 하는 고정 번호예요. 돌려주는 순서는 훈련 입력, 테스트 입력, 훈련 정답, 테스트 정답이에요.

        ```interactive
        위젯: stratify
        ```

        ```comic-gen
        제목: 기준은 훈련 자료에서만
        등장인물:
          강사:
            그림: 사람
            이름표: 강사
            외형: {옷: 재킷, 옷색: "#5379a7", 안경: true}
        컷:
          - 인물: [{식별자: 강사, 손모양: 가리키는손}]
            대사: [{화자: 강사, 내용: "중앙값은 훈련 자료에서 정하고, 테스트에는 그 값을 적용만 해요."}]
            다이어그램:
              종류: 머메이드
              제목: fit과 transform
              높이: 440
              원문: |
                sequenceDiagram
                  participant 훈련
                  participant I as SimpleImputer
                  participant 테스트
                  훈련->>I: fit_transform
                  I-->>훈련: 중앙값 정하고 채움
                  테스트->>I: transform
                  I-->>테스트: 같은 중앙값으로 채움
        ```

        ```python
        from sklearn.model_selection import train_test_split

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
        ```

        나눈 다음에 손질을 시작해요. 나이의 빈칸을 중앙값으로 채우려면 중앙값이 얼마인지 먼저 알아야 해요. `성별`을 One-hot으로 바꾸려면 어떤 값들이 있는지 알아야 하고요. 이렇게 손질의 **기준을 정하는 일** 자체가 자료를 들여다보는 학습이거든요. 그래서 기준은 **훈련 자료에서만** 정해요. 테스트 자료에는 정해진 기준을 **적용만** 하고요. 테스트의 나이까지 넣어 중앙값을 구하면 모의고사 문제를 미리 본 셈이죠. 작은 누수예요.

        ```comic-gen
        제목: 중앙값은 어디서 구하나
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
          - 인물: [{식별자: 민지, 표정: 기쁨}, 강사]
            대사:
              - {화자: 민지, 상대: 강사, 내용: "빈 나이를 채울 중앙값, 1,309명 전체에서 구하면 더 정확하지 않아요?"}
              - {화자: 강사, 상대: 민지, 내용: "그 1,309명 안에 테스트 262명이 들어 있죠."}
          - 구성: 이전
            인물: [{식별자: 민지, 표정: 어리둥절}, {식별자: 강사, 손모양: 가리키는손}]
            대사:
              - {화자: 강사, 상대: 민지, 내용: "시험지를 보고 공부하는 셈이에요. 기준은 훈련 1,047명에서만."}
              - {화자: 민지, 상대: 강사, 내용: "훈련에서 정하고, 테스트에는 적용만. 알겠어요."}
        ```

        `scikit-learn`의 손질 도구는 이 구분을 메서드 이름으로 드러내요. `fit`은 기준 정하기, `transform`은 적용하기예요. `fit_transform`은 둘을 한 번에 하고요. 그러니 훈련에는 `fit_transform`, 테스트에는 `transform`이에요.

        ```python
        from sklearn.impute import SimpleImputer

        imputer = SimpleImputer(strategy='median')
        train_values = imputer.fit_transform(X_train[['나이', '요금']])  # 훈련에서 중앙값을 정하고 채움
        test_values = imputer.transform(X_test[['나이', '요금']])  # 같은 중앙값으로 채우기만
        ```

        이 규칙은 빈칸 채우기만이 아니에요. One-hot 인코딩, 숫자 크기 맞추기(표준화)도 똑같아요. 한 번 더 요약하면, **훈련에서 정하고 테스트에는 적용만.**
        """,
        check=short('빈칸 채우기와 원핫 인코딩은 훈련·테스트 자료 모두에 적용해요. 다만 채울 중앙값과 인코딩할 범주 목록은 어느 자료로만 정해야 하나요?', ['훈련 자료', '훈련자료', '훈련', '훈련 데이터', '훈련데이터', 'train', 'X_train'],
                    '정답은 훈련 자료예요. 훈련 자료로 중앙값과 범주 목록을 정해요(`fit`). 그 기준으로 양쪽 자료의 빈칸을 채워요. 원핫 인코딩도 양쪽 모두에 적용해요(`transform`). 테스트 자료에서 기준을 새로 정하지 않아요. 테스트에도 전처리를 한다는 점을 기억하세요.')),
    coding('stratified-split', '훈련 자료와 테스트 자료로 나누기',
        goal="""
        ```comic-gen
        제목: 나눴더니 한쪽에 몰렸다
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
          - 인물: [{식별자: 민지, 표정: 어리둥절}, 강사]
            대사:
              - {화자: 민지, 상대: 강사, 내용: "무작위로 나눴는데 테스트에 생존자가 거의 없어요."}
              - {화자: 강사, 상대: 민지, 내용: "우연히 몰린 거예요. 그럼 채점이 치우치죠."}
          - 구성: 이전
            인물: [{식별자: 민지, 표정: 기쁨}, {식별자: 강사, 손모양: 가리키는손}]
            대사:
              - {화자: 강사, 상대: 민지, 내용: "stratify=y를 켜면 양쪽 생존 비율을 같게 나눠요."}
              - {화자: 민지, 상대: 강사, 내용: "random_state=42를 주면 누가 실행해도 똑같이 나뉘고요!"}
        ```

        `X`, `y`를 `train_test_split`으로 나눠 `X_train`, `X_test`, `y_train`, `y_test`를 만드세요. 인자는 `test_size=0.2`, `stratify=y`, `random_state=42`로 주세요. 두 쪽의 행 수와 생존 비율을 출력하세요.

        훈련 1047명, 테스트 262명으로 나뉘어야 해요. 두 쪽의 생존 비율도 거의 같으면 맞게 한 거예요.
        """,
        hint="""
        `train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)`가 네 변수를 순서대로 돌려줘요. 훈련 입력, 테스트 입력, 훈련 정답, 테스트 정답이에요. 행 수는 `len()`으로 재요. 생존 비율은 `y_train.mean()`과 `y_test.mean()`이에요.
        """,
        starter=TI + FEATURES + "from sklearn.model_selection import train_test_split\n# 네 변수를 만드세요\n",
        solution=TI + FEATURES + SPLIT + "print(len(X_train), len(X_test))\nprint(y_train.mean(), y_test.mean())\n",
        check="assert len(s['X_train']) == 1047 and len(s['X_test']) == 262\nassert set(s['X_train'].index).isdisjoint(s['X_test'].index)\nassert len(s['y_train']) == 1047 and len(s['y_test']) == 262\nassert abs(s['y_train'].mean() - s['y_test'].mean()) < 0.01"),
    coding('first-model', '손질 없이 첫 모델 돌려 보기',
        goal="""
        손질을 배우기 전에 모델이 실제로 어떻게 돌아가는지 한 번 봐요. 빈칸이 없고 이미 숫자인 열 `객실등급`, `형제배우자`, `부모자녀` 세 개만 써요. `LogisticRegression(max_iter=1000)`을 `model`에 만드세요. `X_train[simple]`, `y_train`으로 학습하세요. 그다음 `X_test[simple]`을 예측해 정확도를 `accuracy`에 담고 출력하세요.

        정확도는 0과 1 사이 값이 나와요. 재료가 셋뿐이니 높지 않아요. 이 숫자를 기억해 두세요. 이 챕터의 남은 미션은 이 숫자를 올리는 일이에요.
        """,
        hint="""
        모델은 늘 세 단계예요. 만들기는 `model = LogisticRegression(max_iter=1000)`이에요. 학습은 `model.fit(X_train[simple], y_train)`이고요. 예측은 `pred = model.predict(X_test[simple])`예요. 그다음 `accuracy = accuracy_score(y_test, pred)`가 테스트 정답과 예측이 일치한 비율이에요.
        """,
        starter=TI + FEATURES + SPLIT + "from sklearn.linear_model import LogisticRegression\nfrom sklearn.metrics import accuracy_score\n\nsimple = ['객실등급', '형제배우자', '부모자녀']\n# model을 학습하고 accuracy를 구하세요\n",
        solution=TI + FEATURES + SPLIT + "from sklearn.linear_model import LogisticRegression\nfrom sklearn.metrics import accuracy_score\n\nsimple = ['객실등급', '형제배우자', '부모자녀']\nmodel = LogisticRegression(max_iter=1000)\nmodel.fit(X_train[simple], y_train)\npred = model.predict(X_test[simple])\naccuracy = accuracy_score(y_test, pred)\nprint(accuracy)\n",
        check="assert 0 <= s['accuracy'] <= 1\nassert s['model'].n_features_in_ == 3\nassert abs(s['accuracy'] - (s['model'].predict(s['X_test'][['객실등급', '형제배우자', '부모자녀']]) == s['y_test']).mean()) < 1e-12"),
    coding('train-imputer', '빈 나이와 요금을 훈련 기준으로 채우기',
        goal="""
        나이와 요금의 빈칸을 채워요. `SimpleImputer(strategy='median')`를 `imputer`에 만드세요. 훈련 표의 `['나이', '요금']`에 `fit_transform`한 결과는 `train_values`에 담으세요. 테스트 표의 같은 열에 `transform`한 결과는 `test_values`에 담으세요. 두 결과의 `shape`를 출력하세요.

        훈련 1047행, 테스트 262행에 열 두 개씩이어야 해요. 빈 값이 하나도 없으면 맞게 한 거예요.
        """,
        hint="""
        `imputer.fit_transform(X_train[['나이', '요금']])`는 훈련 자료에서 중앙값을 정하고 바로 채워요. 테스트에는 같은 `imputer`로 `imputer.transform(X_test[['나이', '요금']])`만 부르세요. 테스트에 `fit`을 다시 하면 기준이 바뀌어요.
        """,
        starter=TI + FEATURES + SPLIT + "from sklearn.impute import SimpleImputer\n# imputer와 두 변환 결과를 만드세요\n",
        solution=TI + FEATURES + SPLIT + "from sklearn.impute import SimpleImputer\n\nimputer = SimpleImputer(strategy='median')\ntrain_values = imputer.fit_transform(X_train[['나이', '요금']])\ntest_values = imputer.transform(X_test[['나이', '요금']])\nprint(train_values.shape, test_values.shape)\n",
        check="import numpy as np\n\nassert s['train_values'].shape == (1047, 2) and s['test_values'].shape == (262, 2)\nassert np.isfinite(s['train_values']).all() and np.isfinite(s['test_values']).all()\nassert np.allclose(s['imputer'].statistics_, s['X_train'][['나이', '요금']].median().to_numpy())"),
    coding('onehot-fit', '글자 열을 훈련 기준으로 One-hot',
        goal="""
        앞 단원의 `get_dummies`를 모델 흐름에 맞는 도구로 바꿔요. `OneHotEncoder(handle_unknown='ignore', sparse_output=False)`를 `encoder`에 만드세요. `X_train[['성별']]`에 `fit_transform`한 결과는 `train_encoded`에 담으세요. `X_test[['성별']]`에 `transform`한 결과는 `test_encoded`에 담으세요. 둘의 `shape`를 출력하세요.

        두 결과 모두 열이 2개(여성, 남성)면 맞게 한 거예요.
        """,
        hint="""
        빈칸 채우기와 똑같은 모양이에요. 훈련에는 `fit_transform`, 테스트에는 `transform`. `handle_unknown='ignore'`는 테스트에 처음 보는 값이 나와도 오류 대신 0으로 두라는 뜻이에요. `sparse_output=False`는 결과를 보통 배열로 달라는 뜻이고요.
        """,
        starter=TI + FEATURES + SPLIT + "from sklearn.preprocessing import OneHotEncoder\n# encoder, train_encoded, test_encoded를 만드세요\n",
        solution=TI + FEATURES + SPLIT + "from sklearn.preprocessing import OneHotEncoder\n\nencoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False)\ntrain_encoded = encoder.fit_transform(X_train[['성별']])\ntest_encoded = encoder.transform(X_test[['성별']])\nprint(train_encoded.shape, test_encoded.shape)\n",
        check="assert s['train_encoded'].shape == (1047, 2) and s['test_encoded'].shape == (262, 2)\nassert sorted(s['encoder'].categories_[0]) == ['남성', '여성']\nassert (s['train_encoded'].sum(axis=1) == 1).all()"),
    concept('why-pipeline', '손질이 늘어나면 순서가 꼬인다, 그래서 한 줄로 묶는다',
        body="""
        지금까지 손질 도구를 둘 썼어요. 빈칸 채우기, One-hot. 실제로는 하나 더 필요해요. 나이는 0~80, 요금은 0~500, `형제배우자`는 0~8이에요. 열마다 숫자 크기가 제각각이죠. 그러면 어떤 모델은 큰 숫자 열에 끌려가요. 그래서 **표준화**(`StandardScaler`)를 해요. 각 열을 "평균 0, 퍼짐 1"로 맞추는 거예요. 이것도 기준(평균과 퍼짐)을 훈련에서 정하고 테스트에 적용하는 도구예요.

        ```comic-gen
        제목: 손질을 한 줄로 묶기
        등장인물:
          강사:
            그림: 사람
            이름표: 강사
            외형: {옷: 재킷, 옷색: "#5379a7", 안경: true}
        컷:
          - 인물: [강사]
            대사: [{화자: 강사, 내용: "손질 단계가 늘수록 fit과 transform을 헷갈릴 자리도 늘어나요. 그래서 한 줄로 묶어요."}]
            다이어그램:
              종류: 머메이드
              제목: Pipeline
              높이: 520
              원문: |
                flowchart TB
                  X["X_train"] --> F["fill: SimpleImputer"]
                  F --> S["scale: StandardScaler"]
                  S --> M["model: LogisticRegression"]
                  M --> P["fit 한 번에 세 단계 모두"]
        ```

        손질이 셋이 되면 코드가 길어져요. 무엇보다 **순서와 짝을 틀리기 쉬워져요.** 훈련에는 `fit_transform`, 테스트에는 `transform`. 이 짝을 셋 다 정확히 맞춰야 해요. 모델에 넣기 전에 결과도 다시 합쳐야 하고요. 한 군데라도 테스트에 `fit`을 하면 조용히 누수가 생겨요. 오류가 안 나서 알아차리기 어렵죠.

        ```comic-gen
        제목: 세 번의 손질, 한 번의 fit
        등장인물:
          준호:
            그림: 사람
            이름표: 준호 · 은행 직원
            외형: {머리색: "#303746", 옷색: "#b88646"}
          파이프라인: {그림: 서버, 이름표: Pipeline}
        컷:
          - 인물: [{식별자: 준호, 표정: 슬픔}, 파이프라인]
            대사:
              - {화자: 준호, 상대: 파이프라인, 내용: "빈칸 채우기, 표준화, One-hot… 테스트에 fit_transform을 써 버렸어."}
              - {화자: 파이프라인, 상대: 준호, 내용: "셋을 순서대로 저한테 넣어 두세요."}
          - 구성: 이전
            인물: [{식별자: 준호, 표정: 기쁨}, {식별자: 파이프라인, 표정: 기쁨}]
            대사:
              - {화자: 파이프라인, 상대: 준호, 내용: "fit 한 번이면 안에서 차례로 기준을 정하고, 테스트엔 적용만 해요."}
              - {화자: 준호, 상대: 파이프라인, 내용: "짝을 틀릴 자리가 아예 없어지네."}
            다이어그램:
              종류: 머메이드
              제목: Pipeline 안의 순서
              높이: 220
              원문: |
                flowchart LR
                  A["빈칸 채우기"] --> B["표준화"] --> C["One-hot"] --> D["모델"]
        ```

        `Pipeline`은 이 단계들을 **순서대로 한 줄에 묶어** 주는 도구예요. 묶고 나서 `fit`을 한 번 부르면 안쪽 단계들이 차례로 훈련 자료에서 기준을 정해요. `transform`이나 `predict`를 부르면 같은 순서로 적용만 하고요. 짝을 틀릴 자리가 없어져요.

        ```python
        from sklearn.pipeline import Pipeline

        numeric_pipeline = Pipeline(
            [
                ('fill', SimpleImputer(strategy='median')),  # 1단계: 빈칸 채우기
                ('scale', StandardScaler()),  # 2단계: 크기 맞추기
            ]
        )
        train_values = numeric_pipeline.fit_transform(X_train[numeric])  # 두 단계 모두 훈련에서 fit
        test_values = numeric_pipeline.transform(X_test[numeric])  # 두 단계 모두 적용만
        ```

        `(이름, 도구)` 쌍을 리스트에 순서대로 넣으면 끝이에요. 다음 단원에서는 숫자 열용 묶음과 글자 열용 묶음을 합쳐요. 그 끝에 모델까지 붙인 완성형을 써요. `fit` 한 번으로 손질과 학습이 끝나죠.
        """,
        check=short('빈칸 채우기, 표준화 같은 손질 단계를 순서대로 묶어요. 그러면 `fit` 한 번에 다 처리돼요. 이 `scikit-learn` 도구 이름이 뭔가요?', ['Pipeline', 'pipeline', '파이프라인'],
                    '`Pipeline`에 `(이름, 도구)` 쌍을 순서대로 넣어요. 그러면 훈련에서는 차례로 `fit`, 테스트에서는 차례로 `transform`만 해요.')),
    coding('pipeline-build', '빈칸 채우기와 표준화를 한 줄로 묶기',
        goal="""
        `Pipeline([('fill', SimpleImputer(strategy='median')), ('scale', StandardScaler())])`를 `numeric_pipeline`에 만드세요. 숫자 열 `numeric`에 훈련은 `fit_transform`, 테스트는 `transform`하세요. 결과는 `train_values`, `test_values`에 담고 `shape`를 출력하세요.

        훈련 1047행 5열, 테스트 262행 5열이면 맞게 한 거예요. 표준화를 거친 훈련 자료는 열마다 평균이 0에 가까워요.
        """,
        hint="""
        `Pipeline`의 괄호 안에 리스트, 리스트 안에 `(이름, 도구)` 쌍 두 개예요. 만든 뒤에는 도구 하나처럼 써요. 훈련에는 `numeric_pipeline.fit_transform(X_train[numeric])`, 테스트에는 `numeric_pipeline.transform(X_test[numeric])`예요.
        """,
        starter=TI + FEATURES + SPLIT + "from sklearn.impute import SimpleImputer\nfrom sklearn.pipeline import Pipeline\nfrom sklearn.preprocessing import StandardScaler\n\nnumeric = ['객실등급', '나이', '형제배우자', '부모자녀', '요금']\n# numeric_pipeline, train_values, test_values를 만드세요\n",
        solution=TI + FEATURES + SPLIT + "from sklearn.impute import SimpleImputer\nfrom sklearn.pipeline import Pipeline\nfrom sklearn.preprocessing import StandardScaler\n\nnumeric = ['객실등급', '나이', '형제배우자', '부모자녀', '요금']\nnumeric_pipeline = Pipeline([('fill', SimpleImputer(strategy='median')), ('scale', StandardScaler())])\ntrain_values = numeric_pipeline.fit_transform(X_train[numeric])\ntest_values = numeric_pipeline.transform(X_test[numeric])\nprint(train_values.shape, test_values.shape)\n",
        check="import numpy as np\n\nassert s['train_values'].shape == (1047, 5) and s['test_values'].shape == (262, 5)\nassert np.isfinite(s['train_values']).all() and np.isfinite(s['test_values']).all()\nassert np.allclose(s['train_values'].mean(axis=0), 0, atol=1e-8)\nassert list(s['numeric_pipeline'].named_steps) == ['fill', 'scale']"),
    quiz('pipeline-check', '단원 점검',
        choice('올바른 손질 순서는 어느 것인가요?',
               ['훈련·테스트를 먼저 나누고, 훈련에서 `fit`, 테스트에는 `transform`', '전체 자료에서 `fit`한 뒤 나눈다', '테스트에서 `fit`하고 훈련에 `transform`'], 0,
               '기준을 정하는 `fit`에 테스트가 섞이면 모의고사를 미리 본 셈이에요. 나누는 게 먼저예요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「테스트에서 fit」: 기준을 테스트로 정하는 누수예요.\n- 「전체에서 fit한 뒤 나눈다」: 테스트 자료가 기준에 섞여요."),
        short('`train_test_split`에 넣는 고정 번호 인자예요. 누가 실행해도 똑같이 나뉘게 해요. 이름이 뭔가요?', ['random_state'],
              '`random_state=42`처럼 같은 번호를 쓰면 누가 돌려도 똑같이 나뉘어요. 결과를 비교하려면 분리가 같아야 해요.'),
        choice('`stratify=y`는 무엇을 맞추려는 것인가요?',
               ['훈련과 테스트의 생존 비율이 비슷하도록', '행 수가 같도록', '나이 순서대로 나뉘도록'], 0,
               '무작위로 나누다 보면 한쪽에 생존자가 몰릴 수 있어요. `stratify`는 정답 비율을 양쪽에 비슷하게 유지해요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「행 수가 같도록」: 행 수는 test_size가 정해요.\n- 「나이 순서대로」: 무작위 분할에 순서는 없어요."),
        choice("`encoder.fit_transform(X_test[['성별']])`처럼 테스트에 `fit`을 했어요. 무슨 문제가 생기나요?",
               ['테스트 자료로 기준을 정하는 누수가 된다', '더 정확해진다', '열 수가 바뀐다'], 0,
               '값 목록·중앙값·평균 같은 기준은 훈련에서만 정해요. 테스트에는 정해진 기준을 적용만 해야 해요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「열 수가 바뀐다」: 바뀔 수도 있지만 핵심은 누수예요.\n- 「더 정확해진다」: 점수는 올라 보여도 못 믿어요."),
        choice('`Pipeline`을 쓰는 가장 큰 이유는 무엇인가요?',
               ['손질 단계마다 `fit`과 `transform` 짝을 틀릴 자리를 없애려고', '코드가 더 길어져서', '정확도가 자동으로 오르기 때문에'], 0,
               '단계를 묶으면 `fit` 한 번에 모든 단계가 훈련 자료에서 기준을 정해요. 적용할 때는 전부 적용만 하고요. 조용한 누수를 막아요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「코드가 길어져서」: 오히려 짧아져요.\n- 「정확도가 자동으로」: Pipeline은 점수를 올리지 않아요. 실수를 막아요."),
        choice('1309명을 `test_size=0.2`로 나누면 테스트 자료는 약 몇 명인가요?',
               ['약 262명', '약 1047명', '약 20명'], 0,
               '20%가 테스트예요. 1309의 20%는 약 262명이에요. 나머지 1047명이 훈련이고요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「약 20명」: 20%지 20명이 아니에요.\n- 「약 1047명」: 그건 훈련 자료예요."),
        choice("""**프롬프트 고르기** · 훈련·테스트를 나눠요. 두 쪽의 생존 비율이 같아야 하고, 누가 실행해도 같은 결과여야 해요. 어떤 프롬프트가 맞을까요?""",
               ["""scikit-learn. train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)로 X_train, X_test, y_train, y_test 만들고 두 쪽 행 수와 생존 비율 출력. 코드만""", """데이터 8:2로 나눠 줘""", """train_test_split 써서 나눠 줘""", """훈련이랑 테스트 나눠 줘. 랜덤으로"""], 0,
               """정답은 stratify=y(층화 분할, 생존 비율 맞추기)와 random_state=42(고정 번호)를 적었어요. 이 두 인자는 AI가 잘 빼먹어요. 빼먹으면 누가 돌려도 같은 결과가 안 나와요.

**다른 보기는 왜 아닌가**

- 「8:2로」: 생존 비율 맞추기와 고정 번호가 없어요.
- 「train_test_split 써서」: 함수 이름만 있고 인자가 없어요.
- 「랜덤으로」: 실행마다 다른 결과가 나와요."""),
        choice("""**프롬프트 고르기** · 나이의 빈칸을 중앙값으로 채워요. 누수가 없어야 해요. 어떤 프롬프트가 맞을까요?""",
               ["""scikit-learn. SimpleImputer(strategy='median')를 imputer에 만들고, X_train[['나이','요금']]에는 fit_transform, X_test[['나이','요금']]에는 transform만. 결과를 train_values, test_values에 담고 shape 출력. 코드만""", """빈 나이를 중앙값으로 채워 줘""", """전체 자료의 중앙값으로 나이를 채운 다음 나눠 줘""", """imputer로 훈련이랑 테스트 둘 다 fit_transform 해 줘"""], 0,
               """정답은 "훈련에는 fit_transform, 테스트에는 transform만"을 적었어요. 중앙값 같은 기준은 훈련 자료에서만 정해야 누수가 없어요.

**다른 보기는 왜 아닌가**

- 「중앙값으로 채워 줘」: 어느 자료로 기준을 정할지가 없어요. 그러면 전체에서 구하기 쉬워요.
- 「전체 자료의 중앙값으로 채운 다음 나눠」: 테스트가 기준에 섞이는 누수예요.
- 「둘 다 fit_transform」: 테스트에서 기준을 다시 정하는 누수예요."""),
    ),
])
