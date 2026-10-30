"""aice-tuning: 6 answer-picking steps -> coding steps (2026-10-29).

Step 7 (최종 평가 표는 선택에 쓰지 않아요) stays a choice: it asks about the evaluation procedure, not
code. Converted steps run real scikit-learn searches and cross-validation on small data (fixed folds
and random_state) and edit one line: the candidate count, the stratified splitter, the mean of the fold
scores, refit, the direction of a negative error score and the raw table handed to a Pipeline. Prepared
cases rerun with other grids, labels, targets and rows, so typed results and the starter's line fail."""
from _kit import Script, code_step

OPENING = ['이 수업에서는 모델 설정을 비교하고 선택하는 흐름을 직접 코드로 써요. 최종 평가 자료는 따로 남겨 둬요.',
           '후보 조합과 교차검증 점수를 계산해요. Pipeline의 전처리와 최종 재학습까지 코드로 연결해요.']
PRD_SCOPE = ['두 챕터·세 단원·아홉 스텝에서 같은 배송 모델 설정을 비교해요.',
             'ParameterGrid의 조합 수·StratifiedKFold·fold 점수의 평균·refit·음수 오차 점수의 방향·Pipeline에 원래 표 넘기기를 한 곳씩 직접 고쳐 써요. 최종 평가 표를 선택에 다시 쓰지 않는 절차 판단은 선택 문항으로 남겨요.']
PRD_GRADING = ['직접 고친 코드를 실제 파이썬·scikit-learn으로 실행해 판정해요. 실행·해설만으로 성공시키지 않아요.',
               '다른 후보 목록·정답·목표·행으로 실제 탐색과 교차검증을 다시 실행해 기준 풀이와 비교해요. 결과를 글자로 적은 답, 후보 수의 합, 범주를 무시한 분리, 첫 fold만 본 점수, refit 없는 탐색, 더 음수인 점수를 고른 답, 전체로 미리 스케일한 표는 거절해요.',
               '마지막 도전(stp_d425c897-1d63-4d4d-b506-2a6226b835eb): 실제 Python 실행과 다른 준비 자료의 결과를 검사해요. 시작 코드는 실패하고 동등한 풀이도 통과해야 해요.']
PRD_NARRATION = ['작은 자료와 후보로 같은 검증 조건을 유지하며 한 줄씩 고쳐 실제 결과를 비교해요.',
                 '조합수·범주비율·fold평균·refit·음수점수·fold전처리를 조심할 지점으로 짚어요.']

SUBMIT = '수정한 코드를 제출하세요.'
W = '실제 scikit-learn 동작을 정확히 말해요.'
DATA = '# 범주마다 네 관측이 있어 두 몫으로 나눌 수 있어요.\nX_train = [[0], [1], [2], [3], [4], [5], [6], [7]]\ny_train = [0, 0, 0, 0, 1, 1, 1, 1]\n'

s1 = ('from sklearn.model_selection import ParameterGrid\n\n# 깊이 세 후보와 잎 최소 수 두 후보예요.\ngrid = {"max_depth": [1, 2, 3], "min_samples_leaf": [1, 2]}\n'
      '# 이 줄을 고쳐 후보 수를 더하지 말고 모든 조합의 수를 count에 담으세요.\ncount = len(grid["max_depth"]) + len(grid["min_samples_leaf"])\n'
      'print(count)\nprint(len(list(ParameterGrid(grid))))\n')
s1_sol = s1.replace('count = len(grid["max_depth"]) + len(grid["min_samples_leaf"])\n',
                    '# 설정마다 후보를 하나씩 고르는 모든 조합이라 후보 수를 곱해요. ParameterGrid가 그 조합을 실제로 만들어요.\ncount = len(list(ParameterGrid(grid)))\n')
n1 = (Script(s1)
      .say('깊이 세 후보와 잎 최소 수 두 후보예요. count 줄을 고쳐 모든 조합의 수를 세야 해요.', 'text:count 줄을 고쳐 후보 수를 더하지 말고 모든 조합의 수를 count에 담으세요.')
      .run('print(count)', 'print(len(list')
      .say('5와 6이에요. 더하기는 실제로 만들어지는 조합의 수와 달라요.', 'output')
      .patch('count = len(grid["max_depth"]) + len(grid["min_samples_leaf"])\n', 'count = len(list(ParameterGrid(grid)))\n', 'len(list(ParameterGrid(grid)))로 바꿔요.')
      .run('print(count)', 'print(len(list')
      .say('6과 6이에요. 깊이 셋마다 잎 최소 수 둘을 짝지은 3×2개예요.', 'output')
      .say('조심하세요. 설정 후보를 하나 더할 때마다 조합은 곱으로 늘어요. 학습 횟수도 그만큼 늘어요.', 'code:count = len(list(ParameterGrid'))

s2 = ('from sklearn.model_selection import KFold, StratifiedKFold\n\n' + DATA
      + '# 이 줄을 고쳐 순서대로 자르는 KFold 대신 범주 비율을 지키는 StratifiedKFold로 두 몫을 나누세요.\ncv = KFold(n_splits=2, shuffle=False)\n'
      '# 확인용 계산: fold마다 [학습 수, 검증 수, 겹친 수]와 검증 몫의 [정상 수, 지연 수]를 모아요. 이 블록의 문법은 몰라도 돼요.\n'
      'checks = []\ncounts = []\nfor train, valid in cv.split(X_train, y_train):\n'
      '    checks.append([len(train), len(valid), len(set(train) & set(valid))])\n    labels = [y_train[i] for i in valid]\n'
      '    counts.append([labels.count(0), labels.count(1)])\nprint(checks)\nprint(counts)\n')
s2_sol = s2.replace('cv = KFold(n_splits=2, shuffle=False)\n', '# 범주마다 따로 나눠 검증 몫마다 정상과 지연이 같은 비율로 들어가요.\ncv = StratifiedKFold(n_splits=2, shuffle=False)\n')
n2 = (Script(s2)
      .say('정답이 정상 넷, 지연 넷 순서로 놓였어요. cv 줄을 고쳐 범주 비율을 지키며 나눠야 해요.', 'text:cv 줄을 고쳐 순서대로 자르는 KFold 대신 범주 비율을 지키는 StratifiedKFold로 두 몫을 나누세요.')
      .run('print(checks)', 'print(counts)')
      .say('겹친 수는 0이지만 검증 몫이 [4, 0]과 [0, 4]예요. 한 몫에 한 범주만 들어갔어요.', 'output')
      .patch('cv = KFold(n_splits=2, shuffle=False)\n', 'cv = StratifiedKFold(n_splits=2, shuffle=False)\n', 'KFold를 StratifiedKFold로 바꿔요.')
      .run('print(checks)', 'print(counts)')
      .say('검증 몫마다 [2, 2]예요. 한 fold 안에서 학습과 검증은 겹치지 않고, 다음 fold에서 역할이 바뀌어요.', 'output')
      .say('조심하세요. 정렬된 표를 순서대로 자르면 검증 몫에 한 범주만 남을 수 있어요.', 'code:StratifiedKFold(n_splits=2'))

s3 = ('from sklearn.model_selection import cross_val_score, StratifiedKFold\nfrom sklearn.tree import DecisionTreeClassifier\n\n'
      '# 범주마다 네 관측이 있어 두 몫으로 나눌 수 있어요.\nX_train = [[0], [1], [2], [3], [4], [5], [6], [7]]\ny_train = [0, 0, 0, 1, 0, 1, 1, 1]\n'
      'cv = StratifiedKFold(n_splits=2, shuffle=False)\n# 매 fold에서 새로 학습한 뒤 남겨 둔 몫을 평가해요.\n'
      'scores = cross_val_score(DecisionTreeClassifier(max_depth=1, random_state=0), X_train, y_train, cv=cv, scoring="accuracy")\nprint(scores.tolist())\n'
      '# 이 줄을 고쳐 첫 fold 하나가 아니라 모든 fold 점수의 평균을 cv_score에 담으세요.\ncv_score = float(scores[0])\nprint(cv_score)\n')
s3_sol = s3.replace('cv_score = float(scores[0])\n', '# 여러 몫의 평가를 모은 평균이에요. 봉인한 최종 테스트 점수가 아니라 훈련 안에서 나눈 추정이에요.\ncv_score = float(scores.mean())\n')
n3 = (Script(s3)
      .say('두 fold의 점수가 나왔어요. cv_score 줄을 고쳐 모든 fold 점수의 평균을 구해야 해요.', 'text:cv_score 줄을 고쳐 첫 fold 하나가 아니라 모든 fold 점수의 평균을 cv_score에 담으세요.')
      .run('print(scores', 'print(cv_score)')
      .say('[0.5, 0.75]와 0.5예요. 한 번의 분리만 보면 다른 몫의 결과를 놓쳐요.', 'output')
      .patch('cv_score = float(scores[0])\n', 'cv_score = float(scores.mean())\n', 'scores[0]을 scores.mean()으로 바꿔요.')
      .run('print(scores', 'print(cv_score)')
      .say('0.625예요. 두 몫의 평가를 모은 교차검증 평균이에요.', 'output')
      .say('조심하세요. 교차검증 평균은 훈련 안에서 나눈 추정이에요. 봉인한 최종 테스트 점수가 아니에요.', 'code:scores.mean()'))

s4 = ('from sklearn.model_selection import GridSearchCV, StratifiedKFold\nfrom sklearn.tree import DecisionTreeClassifier\n\n' + DATA
      + 'cv = StratifiedKFold(n_splits=2, shuffle=False)\n# 같은 분리와 같은 정확도에서 네 후보를 비교해요.\n'
      '# 이 줄의 refit을 고쳐 고른 설정으로 전달한 훈련 표 전체를 다시 학습하게 하세요.\n'
      'search = GridSearchCV(DecisionTreeClassifier(random_state=0), {"max_depth": [1, 2], "min_samples_leaf": [1, 2]}, scoring="accuracy", cv=cv, refit=False, n_jobs=1, error_score="raise")\n'
      'search.fit(X_train, y_train)\nprint(search.best_params_)\n'
      '# 확인용 출력: 최종 모델이 학습한 행 수와 새 배송 두 건의 예측이에요.\nprint(int(search.best_estimator_.tree_.n_node_samples[0]))\nprint(search.predict([[0], [7]]).tolist())\n')
s4_sol = s4.replace('refit=False, ', 'refit=True, ').replace('# 이 줄의 refit을 고쳐 고른 설정으로 전달한 훈련 표 전체를 다시 학습하게 하세요.\n',
                                                         '# 이 줄의 refit을 고쳐 고른 설정으로 전달한 훈련 표 전체를 다시 학습하게 하세요.\n# refit=True는 최선 설정을 고른 뒤 그 설정으로 fit에 준 훈련 표 전체를 다시 학습해요.\n')
n4 = (Script(s4)
      .say('최선 설정을 골랐어요. refit을 고쳐 그 설정으로 훈련 표 전체를 다시 학습하게 해야 해요.', 'text:search 줄의 refit을 고쳐 고른 설정으로 전달한 훈련 표 전체를 다시 학습하게 하세요.')
      .run('print(search.best_params_)', 'print(int(search.best_estimator_', error='AttributeError')
      .say('최선 설정은 나오지만 AttributeError예요. refit=False라 최종 모델이 없어요.', 'output')
      .patch('refit=False, ', 'refit=True, ', 'refit=False를 refit=True로 바꿔요.')
      .run('print(search.best_params_)', 'print(search.predict')
      .say('8과 [0, 1]이에요. 고른 설정으로 훈련 표 여덟 행 전체를 다시 학습했어요.', 'output')
      .say('조심하세요. refit은 최종 테스트 정답을 쓰지 않아요. fit에 넘긴 훈련 표만 써요.', 'code:refit=True'))

s5 = ('from sklearn.dummy import DummyRegressor\nfrom sklearn.linear_model import LinearRegression\nfrom sklearn.model_selection import KFold, cross_val_score\n\n'
      '# 거리와 시간이에요. 두 후보를 같은 분리로 비교해요.\nX_train = [[0], [1], [2], [3]]\ny_train = [0, 2, 4, 6]\ncv = KFold(n_splits=2)\n'
      'dummy = cross_val_score(DummyRegressor(strategy="mean"), X_train, y_train, cv=cv, scoring="neg_mean_squared_error").mean()\n'
      'linear = cross_val_score(LinearRegression(), X_train, y_train, cv=cv, scoring="neg_mean_squared_error").mean()\n'
      'print(round(float(dummy), 3), round(float(linear), 3))\n'
      '# 이 줄을 고쳐 음수 오차 점수가 더 큰(0에 가까운) 후보를 best에 담으세요.\nbest = "dummy" if dummy < linear else "linear"\nprint(best)\n')
s5_sol = s5.replace('best = "dummy" if dummy < linear else "linear"\n', '# scikit-learn 점수는 클수록 좋게 맞춰요. 오차에 −를 붙였으니 0에 가까울수록 오차가 작아요.\nbest = "dummy" if dummy > linear else "linear"\n')
n5 = (Script(s5)
      .say('scoring이 neg_mean_squared_error예요. best 줄을 고쳐 점수가 더 큰 후보를 골라야 해요.', 'text:best 줄을 고쳐 음수 오차 점수가 더 큰(0에 가까운) 후보를 best에 담으세요.')
      .run('print(round(float(dummy)', 'print(best)')
      .say('-17.0과 -0.0인데 dummy를 골랐어요. 더 음수인 쪽, 즉 MSE 17을 골랐어요.', 'output')
      .patch('dummy < linear', 'dummy > linear', '<를 >로 바꿔요.')
      .run('print(round(float(dummy)', 'print(best)')
      .say('linear예요. 점수 -0.0은 MSE가 0에 가까운 쪽이에요.', 'output')
      .say('조심하세요. neg 점수는 숫자가 작을수록 오차가 커요. 부호를 떼어 MSE로 읽어요.', 'code:dummy > linear'))

s6 = ('from sklearn.model_selection import cross_validate, StratifiedKFold\nfrom sklearn.pipeline import Pipeline\nfrom sklearn.preprocessing import StandardScaler\n'
      'from sklearn.tree import DecisionTreeClassifier\n\n' + DATA + 'cv = StratifiedKFold(n_splits=2, shuffle=False)\n'
      '# 스케일러와 트리를 한 모델로 묶었어요.\nmodel = Pipeline([("scale", StandardScaler()), ("model", DecisionTreeClassifier(max_depth=1, random_state=0))])\n'
      '# 전체 훈련 표로 미리 스케일한 표예요.\nX_scaled = StandardScaler().fit_transform(X_train).tolist()\n'
      '# 이 줄을 고쳐 X_scaled 대신 원래 X_train을 넘겨 fold마다 훈련 몫에서 스케일 기준을 배우게 하세요.\n'
      'result = cross_validate(model, X_scaled, y_train, cv=cv, return_estimator=True)\n'
      '# 확인용 출력: fold마다 스케일러가 배운 평균과 전체 표의 평균이에요. 이 줄의 문법은 몰라도 돼요.\n'
      'print([round(float(fold.named_steps["scale"].mean_[0]), 3) for fold in result["estimator"]])\nprint(sum(row[0] for row in X_train) / len(X_train))\n')
s6_sol = s6.replace('result = cross_validate(model, X_scaled, y_train, cv=cv, return_estimator=True)\n',
                    '# 원래 표를 넘기면 Pipeline이 fold마다 훈련 몫에서만 스케일 기준을 배워 검증 몫에 적용해요.\nresult = cross_validate(model, X_train, y_train, cv=cv, return_estimator=True)\n')
n6 = (Script(s6)
      .say('전체 표로 미리 스케일하면 검증 몫의 값도 기준에 섞여요. result 줄에 원래 X_train을 넘겨야 해요.', 'text:result 줄을 고쳐 X_scaled 대신 원래 X_train을 넘겨 fold마다 훈련 몫에서 스케일 기준을 배우게 하세요.')
      .run('print([round(float(fold', 'print(sum(row')
      .say('[0.436, -0.436]과 3.5예요. 이미 전체 기준으로 바뀐 값을 다시 배웠어요.', 'output')
      .patch('cross_validate(model, X_scaled,', 'cross_validate(model, X_train,', 'X_scaled를 X_train으로 바꿔요.')
      .run('print([round(float(fold', 'print(sum(row')
      .say('[4.5, 2.5]와 3.5예요. fold마다 그 fold의 훈련 몫 평균만 배웠어요.', 'output')
      .say('조심하세요. 교차검증 전에 전체 표로 스케일하면 검증 몫의 정보가 기준에 새어 들어가요.', 'code:cross_validate(model, X_train,'))

SPECS = [
    code_step('stp_d5b4f4b3-8eb5-4754-801c-1b94b9d5a777', 'ParameterGrid로 설정 조합의 수를 세세요', '설정 후보의 조합이 곱으로 늘어나는 것을 계산해 확인해요.',
              '후보 수를 더하면 5로 실제 조합 6과 다르다. len(list(ParameterGrid(grid)))로 고쳐 3×2인 6을 확인한다. 채점은 다른 후보 목록으로 실행한다.',
              '`ParameterGrid(grid)`는 설정마다 후보를 하나씩 골라 만든 모든 조합을 만들어요. GridSearchCV도 이 조합을 하나씩 학습해 비교해요.',
              'count 줄을 고쳐 후보 수를 더하지 말고 모든 조합의 수를 count에 담으세요. 채점은 다른 후보 목록으로도 실행해요.',
              ['코드 실행을 눌러 count와 실제 조합 수를 비교하세요.', 'count 줄을 `count = len(list(ParameterGrid(grid)))`로 고치세요.', '코드 실행을 눌러 두 값이 같은지 확인하세요.', SUBMIT],
              s1, s1_sol, n1, {n1.actions[-1]['text']: W},
              cases=[{'grid': {'max_depth': [1, 2, 3, 4], 'min_samples_leaf': [1, 2, 5]}}, {'grid': {'max_depth': [2], 'min_samples_leaf': [1, 3]}}],
              reject=[([['count = len(list(ParameterGrid(grid)))\n', 'count = len(grid["max_depth"]) + len(grid["min_samples_leaf"])\n']], 'Adding the candidates'),
                      ([['count = len(list(ParameterGrid(grid)))\n', 'count = 6\n']], 'Typing the count')],
              accept=[([['count = len(list(ParameterGrid(grid)))\n', 'import math\ncount = math.prod(len(values) for values in grid.values())\n']], 'Product of the lengths')]),
    code_step('stp_0814f53d-977d-4785-8811-764348a7d5ac', 'StratifiedKFold로 범주 비율을 지켜 나누세요', 'fold마다 학습과 검증을 나누고 검증 몫의 범주 비율을 지켜요.',
              '정렬된 표를 KFold로 자르면 검증 몫이 [4, 0]과 [0, 4]다. StratifiedKFold로 고쳐 겹침 0과 몫마다 [2, 2]를 확인한다. 채점은 다른 정답 순서로 실행한다.',
              '교차검증은 훈련 표를 몫(fold)으로 나눠 한 몫씩 검증에 쓰고 나머지로 학습해요. `KFold`는 순서대로 자르고, `StratifiedKFold`는 범주마다 나눠 몫마다 범주 비율을 비슷하게 맞춰요.',
              'cv 줄을 고쳐 순서대로 자르는 KFold 대신 범주 비율을 지키는 StratifiedKFold로 두 몫을 나누세요. 채점은 다른 정답 순서로도 실행해요.',
              ['코드 실행을 눌러 fold마다의 수와 범주를 확인하세요.', '`KFold(`를 `StratifiedKFold(`로 고치세요.', '코드 실행을 눌러 검증 몫의 범주를 확인하세요.', SUBMIT],
              s2, s2_sol, n2, {n2.actions[-1]['text']: W},
              cases=[{'y_train': [1, 1, 1, 1, 0, 0, 0, 0]}, {'X_train': [[0], [1], [2], [3], [4], [5]], 'y_train': [0, 0, 1, 1, 1, 1]}],
              reject=[([['cv = StratifiedKFold(n_splits=2, shuffle=False)\n', 'cv = KFold(n_splits=2, shuffle=False)\n']], 'Plain KFold'),
                      ([['print(counts)', 'print([[2, 2], [2, 2]])']], 'Typing the counts')],
              accept=[([['cv = StratifiedKFold(n_splits=2, shuffle=False)\n', 'cv = StratifiedKFold(n_splits=2)\n']], 'Default shuffle')]),
    code_step('stp_49835fc1-36eb-4889-9ddb-1d9202724d2f', 'scores.mean()으로 교차검증 평균을 구하세요', '한 번의 분리보다 여러 fold 평가의 평균을 써요.',
              '첫 fold 점수만 쓰면 0.5다. scores.mean()으로 고쳐 두 fold의 평균 0.625를 확인한다. 채점은 다른 정답으로 실행한다.',
              '`cross_val_score`는 fold마다 새로 학습하고 남겨 둔 몫으로 점수를 매겨 fold 수만큼 점수를 돌려줘요. 한 번의 분리는 운에 따라 달라서 모든 fold 점수의 평균을 써요.',
              'cv_score 줄을 고쳐 첫 fold 하나가 아니라 모든 fold 점수의 평균을 cv_score에 담으세요. 채점은 다른 정답으로도 실행해요.',
              ['코드 실행을 눌러 fold 점수와 cv_score를 확인하세요.', '`scores[0]`을 `scores.mean()`으로 고치세요.', '코드 실행을 눌러 평균을 확인하세요.', SUBMIT],
              s3, s3_sol, n3, {n3.actions[-1]['text']: W},
              cases=[{'y_train': [0, 0, 0, 0, 1, 1, 1, 1]}, {'y_train': [1, 1, 1, 0, 1, 0, 0, 0]}],
              reject=[([['cv_score = float(scores.mean())\n', 'cv_score = float(scores[0])\n']], 'First fold only'),
                      ([['cv_score = float(scores.mean())\n', 'cv_score = 0.625\n']], 'Typing the mean')],
              accept=[([['cv_score = float(scores.mean())\n', 'cv_score = float(sum(scores) / len(scores))\n']], 'sum over len')]),
    code_step('stp_f5fb6ed5-cb74-48b4-91fd-65117126f41c', 'refit=True로 고른 설정을 훈련 표 전체로 다시 학습하세요', '설정을 고른 뒤 최종 모델을 훈련 표 전체로 다시 학습해요.',
              'refit=False면 최선 설정만 고르고 최종 모델이 없어 AttributeError다. refit=True로 고쳐 여덟 행 전체로 다시 학습한 예측을 확인한다. 채점은 다른 훈련 자료로 실행한다.',
              '`GridSearchCV`는 같은 분리와 같은 기준으로 후보를 비교해 `best_params_`를 골라요. `refit=True`(기본값)는 그 설정으로 `fit`에 넘긴 훈련 표 전체를 다시 학습해 `best_estimator_`와 `predict`를 만들어요.',
              'search 줄의 refit을 고쳐 고른 설정으로 전달한 훈련 표 전체를 다시 학습하게 하세요. 채점은 다른 훈련 자료로도 실행해요.',
              ['코드 실행을 눌러 AttributeError가 나오는지 확인하세요.', '`refit=False`를 `refit=True`로 고치세요.', '코드 실행을 눌러 최종 모델의 학습 행 수와 예측을 확인하세요.', SUBMIT],
              s4, s4_sol, n4, {n4.actions[-1]['text']: W},
              cases=[{'X_train': [[0], [1], [2], [3], [4], [5], [6], [7], [8], [9]], 'y_train': [1, 1, 1, 1, 1, 0, 0, 0, 0, 0]}, {'y_train': [0, 0, 0, 1, 0, 1, 1, 1]}],
              reject=[([['refit=True, ', 'refit=False, ']], 'No refit'),
                      ([['print(search.predict([[0], [7]]).tolist())', 'print([0, 1])']], 'Typing the predictions')],
              accept=[([['refit=True, ', '']], 'Default refit')]),
    code_step('stp_a465ce45-1868-4214-9e2a-57ecd936e928', '음수 오차 점수가 더 큰 후보를 고르세요', 'neg 오차 점수의 방향을 읽어 오차가 작은 후보를 골라요.',
              'dummy < linear는 더 음수인 MSE 17의 dummy를 고른다. >로 고쳐 0에 가까운 linear를 확인한다. 채점은 dummy가 나은 자료로도 실행한다.',
              'scikit-learn의 점수는 언제나 클수록 좋게 맞춰요. 그래서 오차 지표는 `neg_mean_squared_error`처럼 −를 붙여 돌려줘요. −17은 MSE 17, −25는 MSE 25라서 −17이 더 나아요.',
              'best 줄을 고쳐 음수 오차 점수가 더 큰(0에 가까운) 후보를 best에 담으세요. 채점은 다른 자료로도 실행해요.',
              ['코드 실행을 눌러 두 점수와 고른 후보를 확인하세요.', '`dummy < linear`를 `dummy > linear`로 고치세요.', '코드 실행을 눌러 고른 후보를 확인하세요.', SUBMIT],
              s5, s5_sol, n5, {n5.actions[-1]['text']: W},
              cases=[{'y_train': [5, 1, 4, 2]}, {'y_train': [3, 9, 1, 7]}],
              reject=[([['dummy > linear', 'dummy < linear']], 'More negative'),
                      ([['best = "dummy" if dummy > linear else "linear"\n', 'best = "linear"\n']], 'Typing the name')],
              accept=[([['best = "dummy" if dummy > linear else "linear"\n', 'best = "dummy" if -dummy < -linear else "linear"\n']], 'Comparing MSE')]),
    code_step('stp_2ae67437-08c2-4fe0-a939-681c7c5b564b', 'Pipeline에 원래 X_train을 넘겨 fold 안에서 스케일하세요', '전처리 기준도 fold마다 훈련 몫에서만 배우게 해요.',
              '전체로 미리 스케일한 X_scaled를 넘기면 fold 스케일러가 이미 바뀐 값을 배운다. 원래 X_train을 넘겨 fold마다 훈련 몫의 평균 [4.5, 2.5]를 배우는 것을 확인한다. 채점은 다른 행으로 실행한다.',
              '`Pipeline`으로 스케일과 트리를 묶었어요. 교차검증에 원래 표를 넘기면 fold마다 훈련 몫에서만 스케일 기준을 배워 검증 몫에 적용해요. 전체 훈련 표의 평균은 3.5예요.',
              'result 줄을 고쳐 X_scaled 대신 원래 X_train을 넘겨 fold마다 훈련 몫에서 스케일 기준을 배우게 하세요. 채점은 다른 행으로도 실행해요.',
              ['코드 실행을 눌러 fold마다 배운 평균을 확인하세요.', 'result 줄의 `X_scaled`를 `X_train`으로 고치세요.', '코드 실행을 눌러 fold마다 배운 평균을 다시 확인하세요.', SUBMIT],
              s6, s6_sol, n6, {n6.actions[-1]['text']: W},
              cases=[{'X_train': [[10], [20], [30], [40], [50], [60], [70], [80]]}, {'X_train': [[1], [1], [2], [9], [3], [5], [8], [13]]}],
              reject=[([['cross_validate(model, X_train,', 'cross_validate(model, X_scaled,']], 'Scaled with the whole table'),
                      ([['print([round(float(fold.named_steps["scale"].mean_[0]), 3) for fold in result["estimator"]])', 'print([4.5, 2.5])']], 'Typing the means')],
              accept=[([['result = cross_validate(model, X_train, y_train, cv=cv, return_estimator=True)\n',
                         'result = cross_validate(model, X=X_train, y=y_train, cv=cv, return_estimator=True)\n']], 'Keyword arguments')]),
]
