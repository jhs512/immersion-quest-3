"""aice-regression-metrics: 7 answer-picking steps -> coding steps (2026-10-29).

Each step edits the line that computes or chooses a report value: absolute instead of signed error, the
square root of MSE, MSE as the choice rule, R² against the mean, a constant-target check, a one-row
guard and lining predictions up by delivery id. Prepared cases rerun with other targets and predictions,
so typed results, the starter's metric and order-specific shortcuts fail."""
from _kit import Script, code_step

OPENING = ['이 수업에서는 회귀 오차를 재는 기준을 직접 코드로 계산해요. 지표의 단위와 해석 차이를 구별해요.',
           '같은 예측을 MAE·MSE·RMSE로 비교해요. R제곱과 평가 자료의 제한도 코드로 확인해요.']
PRD_SCOPE = ['두 챕터·세 단원·아홉 스텝으로 같은 배송 보고서를 검토해요.',
             '절댓값 평균·MSE의 제곱근·MSE로 고르기·평균 기준의 R제곱·상수 정답 확인·한 행 확인·배송 번호로 맞추기를 한 곳씩 직접 고쳐 써요.']
PRD_GRADING = ['직접 고친 코드를 실제 파이썬·scikit-learn으로 실행해 판정해요. 실행·해설만으로 성공시키지 않아요.',
               '다른 정답·예측·순서로 다시 실행해 기준 풀이와 비교해요. 결과를 글자로 적은 답, 부호가 있는 평균, MSE 그대로의 보고, MAE로 고른 답, 뒤집기만 한 정렬은 거절해요.',
               'R제곱의 NaN과 기본 보정 0은 정상 점수처럼 다루지 않아요. 상수 정답과 한 행을 직접 확인하는 조건을 쓰고 두 경우 모두로 검사해요.',
               '마지막 도전(stp_8c2d0bff-a5ed-444e-9b9d-811d3b88f5b2): 실제 Python 실행과 다른 준비 자료의 결과를 검사해요. 시작 코드는 실패하고 동등한 풀이도 통과해야 해요.']
PRD_NARRATION = ['같은 정답과 예측을 두고 지표 계산·고르는 기준·순서를 고쳐 실제 값을 비교해요.',
                 '오차상쇄·단위·지표목적·평균기준·상수보정·표본수·행대응을 조심할 지점으로 짚어요.']

SUBMIT = '수정한 코드를 제출하세요.'
W = '실제 scikit-learn 지표 계산을 정확히 말해요.'
PAIR = '# 두 배송의 실제 시간과 같은 순서의 예측이에요.\ny_true = [10, 20]\ny_pred = [12, 18]\n'

s1 = ('from sklearn.metrics import mean_absolute_error\n\n' + PAIR
      + '# 확인용 계산: 배송마다 예측 − 실제를 구해 목록으로 모아요.\nerrors = [pred - actual for actual, pred in zip(y_true, y_pred)]\nprint(errors)\n'
      '# 이 줄을 고쳐 부호를 버린 오차 크기의 평균(MAE)을 report에 담으세요.\nreport = sum(errors) / len(errors)\nprint(float(report))\n')
s1_sol = s1.replace('report = sum(errors) / len(errors)\n',
                    '# 절댓값을 쓰면 위아래로 빗나간 오차가 서로 지워지지 않아요.\nreport = mean_absolute_error(y_true, y_pred)\n')
n1 = (Script(s1)
      .say('한 예측은 2분 크고 하나는 2분 작아요. report 줄을 고쳐 오차 크기의 평균을 구해야 해요.', 'text:report 줄을 고쳐 부호를 버린 오차 크기의 평균(MAE)을 report에 담으세요.')
      .run('print(errors)', 'print(float(report))')
      .say('[2, -2]와 0.0이에요. 반대 방향 오차가 서로 지워졌어요.', 'output')
      .patch('report = sum(errors) / len(errors)\n', 'report = mean_absolute_error(y_true, y_pred)\n', 'mean_absolute_error(y_true, y_pred)로 바꿔요.')
      .run('print(errors)', 'print(float(report))')
      .say('2.0이에요. 두 배송 모두 2분씩 빗나갔어요.', 'output')
      .say('조심하세요. 부호 있는 평균 0은 모두 맞았다는 뜻이 아니에요. 치우침만 없다는 뜻이에요.', 'code:report = mean_absolute_error'))

s2 = ('from sklearn.metrics import mean_squared_error\n\n' + PAIR
      + '# 이 줄을 고쳐 MSE에 제곱근을 씌워 실제 시간과 같은 분 단위로 보고하세요.\nreport = mean_squared_error(y_true, y_pred)\nprint(float(report))\n')
s2_sol = s2.replace('report = mean_squared_error(y_true, y_pred)\n',
                    '# MSE는 분을 제곱한 단위예요. 제곱근(** 0.5)을 씌운 RMSE가 다시 분 단위예요.\nreport = mean_squared_error(y_true, y_pred) ** 0.5\n')
n2 = (Script(s2)
      .say('실제 시간은 분 단위예요. report 줄을 고쳐 MSE에 제곱근을 씌워야 해요.', 'text:report 줄을 고쳐 MSE에 제곱근을 씌워 실제 시간과 같은 분 단위로 보고하세요.')
      .run('print(float(report))')
      .say('4.0이에요. 2분 오차를 제곱한 분제곱 단위예요.', 'output')
      .patch('report = mean_squared_error(y_true, y_pred)\n', 'report = mean_squared_error(y_true, y_pred) ** 0.5\n', '뒤에 ** 0.5를 붙여요.')
      .run('print(float(report))')
      .say('2.0이에요. 다시 분 단위인 RMSE예요.', 'output')
      .say('조심하세요. MSE 4를 4분 오차라고 보고하지 않아요. 단위가 분제곱이에요.', 'code:** 0.5'))

s3 = ('from sklearn.metrics import mean_absolute_error, mean_squared_error\n\n# 같은 정답에 두 후보 모델의 예측을 비교해요.\n'
      'y_true = [10, 20, 30]\na = [10, 20, 36]\nb = [13, 23, 33]\n'
      'print(float(mean_absolute_error(y_true, a)), float(mean_absolute_error(y_true, b)))\nprint(float(mean_squared_error(y_true, a)), float(mean_squared_error(y_true, b)))\n'
      '# 이 줄을 고쳐 MAE가 아니라 MSE가 더 작은 후보를 고르세요.\n'
      'chosen = "a" if mean_absolute_error(y_true, a) <= mean_absolute_error(y_true, b) else "b"\nprint(chosen)\n')
s3_sol = s3.replace('chosen = "a" if mean_absolute_error(y_true, a) <= mean_absolute_error(y_true, b) else "b"\n',
                    '# 이번 요구는 큰 오차를 제곱해 더 벌주는 MSE가 작은 후보예요.\nchosen = "a" if mean_squared_error(y_true, a) <= mean_squared_error(y_true, b) else "b"\n')
n3 = (Script(s3)
      .say('이번 요구는 큰 오차를 더 벌주는 MSE 최소예요. chosen 줄의 비교 지표를 MSE로 고쳐야 해요.', 'text:chosen 줄을 고쳐 MAE가 아니라 MSE가 더 작은 후보를 고르세요.')
      .run('print(float(mean_absolute_error', 'print(chosen)')
      .say('MAE는 2.0과 3.0, MSE는 12.0과 9.0이고 a를 골랐어요. MAE로 골랐어요.', 'output')
      .patch('chosen = "a" if mean_absolute_error(y_true, a) <= mean_absolute_error(y_true, b) else "b"\n',
             'chosen = "a" if mean_squared_error(y_true, a) <= mean_squared_error(y_true, b) else "b"\n', '두 mean_absolute_error를 mean_squared_error로 바꿔요.')
      .run('print(float(mean_absolute_error', 'print(chosen)')
      .say('b예요. 6분 오차 하나가 있는 a는 제곱하면 크게 벌을 받아요.', 'output')
      .say('조심하세요. 같은 예측도 지표에 따라 고르는 후보가 달라져요. 보고 전에 지표를 먼저 정해요.', 'code:mean_squared_error(y_true, a) <='))

s4 = ('from sklearn.metrics import r2_score\n\n# 같은 평가 정답에 크게 빗나간 예측이에요.\ny_true = [10, 20, 30]\ny_pred = [100, 100, 100]\n'
      'mean = sum(y_true) / len(y_true)\nsse = sum((t - p) ** 2 for t, p in zip(y_true, y_pred))\n'
      '# 이 줄을 고쳐 0이 아니라 평균 mean에서 잰 제곱 차이의 합을 sst에 담으세요.\nsst = sum((t - 0) ** 2 for t in y_true)\n'
      'print(round(1 - sse / sst, 6))\nprint(round(float(r2_score(y_true, y_pred)), 6))\n')
s4_sol = s4.replace('sst = sum((t - 0) ** 2 for t in y_true)\n',
                    '# R제곱의 비교 기준은 언제나 평균만 내는 예측이에요.\nsst = sum((t - mean) ** 2 for t in y_true)\n')
n4 = (Script(s4)
      .say('R제곱은 평균만 내는 예측과 비교해요. sst 줄을 고쳐 평균에서 잰 제곱 차이의 합을 구해야 해요.', 'text:sst 줄을 고쳐 0이 아니라 평균 mean에서 잰 제곱 차이의 합을 sst에 담으세요.')
      .run('print(round(1 - sse', 'print(round(float(r2_score')
      .say('-12.857143과 -96.0이에요. 0을 기준으로 삼아 r2_score와 달라요.', 'output')
      .patch('(t - 0) ** 2', '(t - mean) ** 2', 't - 0을 t - mean으로 바꿔요.')
      .run('print(round(1 - sse', 'print(round(float(r2_score')
      .say('둘 다 -96.0이에요. 평균 예측보다 훨씬 나빠 음수가 됐어요.', 'output')
      .say('조심하세요. R제곱은 0에서 멈추지 않아요. 평균 예측보다 나쁘면 음수예요.', 'code:(t - mean) ** 2'))

s5 = ('from sklearn.metrics import r2_score, mean_absolute_error\n\n# 실제 정답이 모두 같은 특수한 평가 표예요.\ny_true = [5, 5, 5]\ny_pred = [6, 6, 6]\n'
      'r2 = float(r2_score(y_true, y_pred, force_finite=True))\n'
      '# 이 줄을 고쳐 y_true의 값이 모두 같은지를 constant에 담으세요.\nconstant = False\n'
      'print(r2, constant)\nprint(float(mean_absolute_error(y_true, y_pred)))\n')
s5_sol = s5.replace('constant = False\n', '# 서로 다른 값이 하나뿐이면 정답이 모두 같아요. 이때 R제곱은 비교할 퍼짐이 없어 보정값이에요.\nconstant = len(set(y_true)) == 1\n')
n5 = (Script(s5)
      .say('정답이 모두 5예요. constant 줄을 고쳐 y_true의 값이 모두 같은지 직접 확인해야 해요.', 'text:constant 줄을 고쳐 y_true의 값이 모두 같은지를 constant에 담으세요.')
      .run('print(r2, constant)', 'print(float(mean_absolute_error')
      .say('0.0 False와 1.0이에요. R제곱 0이 보정값인지 모르고 지나쳐요.', 'output')
      .patch('constant = False\n', 'constant = len(set(y_true)) == 1\n', 'len(set(y_true)) == 1로 바꿔요.')
      .run('print(r2, constant)', 'print(float(mean_absolute_error')
      .say('0.0 True예요. R제곱 0은 보정값이고 MAE로 보면 1분 오차가 남아요.', 'output')
      .say('조심하세요. 정답이 모두 같으면 R제곱은 비교할 퍼짐이 없어요. 이때는 MAE 같은 오차로 판단해요.', 'code:len(set(y_true)) == 1'))

s6 = ('from sklearn.metrics import r2_score, mean_absolute_error\n\n# 평가 관측이 하나뿐일 수 있어요.\ny_true = [5]\ny_pred = [6]\n'
      '# 이 줄을 고쳐 평가 관측이 두 개 이상일 때만 R제곱을 계산하고, 아니면 None으로 두세요.\nr2 = float(r2_score(y_true, y_pred))\n'
      'print(r2)\nprint(float(mean_absolute_error(y_true, y_pred)))\n')
s6_sol = s6.replace('r2 = float(r2_score(y_true, y_pred))\n',
                    '# 한 관측에는 퍼짐이 없어 R제곱을 정의할 수 없어요. MAE는 한 행도 계산돼요.\nr2 = float(r2_score(y_true, y_pred)) if len(y_true) >= 2 else None\n')
n6 = (Script(s6)
      .say('평가 관측이 하나뿐이에요. r2 줄을 고쳐 두 개 이상일 때만 R제곱을 계산해야 해요.', 'text:r2 줄을 고쳐 평가 관측이 두 개 이상일 때만 R제곱을 계산하고, 아니면 None으로 두세요.')
      .run('print(r2)', 'print(float(mean_absolute_error')
      .say('nan과 1.0이에요. R제곱은 정의되지 않아 nan이에요.', 'output')
      .patch('r2 = float(r2_score(y_true, y_pred))\n', 'r2 = float(r2_score(y_true, y_pred)) if len(y_true) >= 2 else None\n', '뒤에 if len(y_true) >= 2 else None을 붙여요.')
      .run('print(r2)', 'print(float(mean_absolute_error')
      .say('None과 1.0이에요. 계산할 수 없는 R제곱은 없다고 두고 MAE로 1분 오차를 봐요.', 'output')
      .say('조심하세요. nan을 점수처럼 보고서에 옮기지 않아요. 평가 행 수부터 확인해요.', 'code:len(y_true) >= 2'))

s7 = ('from sklearn.metrics import mean_absolute_error\n\n# 실제 시간은 true_ids 순서, 예측은 pred_ids 순서로 왔어요.\n'
      'true_ids = [101, 102, 103]\ny_true = [10, 20, 30]\npred_ids = [103, 102, 101]\ny_pred = [30, 20, 10]\n'
      '# 이 줄을 고쳐 같은 배송 번호의 예측을 true_ids 순서로 맞추세요.\naligned = y_pred\n'
      'print(aligned)\nprint(round(float(mean_absolute_error(y_true, aligned)), 6))\n')
s7_sol = s7.replace('aligned = y_pred\n', '# 위치가 아니라 배송 번호로 짝을 찾아요. 각 실제 배송 번호의 예측을 꺼내요.\naligned = [y_pred[pred_ids.index(i)] for i in true_ids]\n')
n7 = (Script(s7)
      .say('길이는 같지만 예측의 배송 순서가 달라요. aligned 줄을 고쳐 배송 번호로 예측을 맞춰야 해요.', 'text:aligned 줄을 고쳐 같은 배송 번호의 예측을 true_ids 순서로 맞추세요.')
      .run('print(aligned)', 'print(round(float')
      .say('[30, 20, 10]과 13.333333이에요. 다른 배송끼리 비교했어요.', 'output')
      .patch('aligned = y_pred\n', 'aligned = [y_pred[pred_ids.index(i)] for i in true_ids]\n', 'true_ids의 번호마다 pred_ids에서 자리를 찾아 예측을 꺼내요.')
      .run('print(aligned)', 'print(round(float')
      .say('[10, 20, 30]과 0.0이에요. 같은 배송끼리 맞추니 오차가 없어요.', 'output')
      .say('조심하세요. 길이가 같다고 짝이 맞는 건 아니에요. 지표를 내기 전에 번호로 대응을 확인해요.', 'code:pred_ids.index(i)'))

SPECS = [
    code_step('stp_a58d4015-0279-4269-97a6-46124844215f', 'mean_absolute_error로 오차 크기의 평균을 구하세요', '반대 방향 오차가 지워지지 않게 오차 크기를 평균내요.',
              '부호 있는 평균은 2와 -2가 상쇄돼 0이다. mean_absolute_error로 고쳐 MAE 2를 확인한다. 채점은 다른 정답과 예측으로 실행한다.',
              '한 예측은 2분 크고 하나는 2분 작아요. 예측 − 실제를 그대로 평균내면 반대 방향 오차가 서로 지워져요. `mean_absolute_error(y_true, y_pred)`는 오차의 절댓값을 평균낸 MAE예요.',
              'report 줄을 고쳐 부호를 버린 오차 크기의 평균(MAE)을 report에 담으세요. 채점은 다른 예측으로도 실행해요.',
              ['코드 실행을 눌러 오차 목록과 report를 확인하세요.', '`sum(errors) / len(errors)`를 `mean_absolute_error(y_true, y_pred)`로 고치세요.', '코드 실행을 눌러 report를 다시 확인하세요.', SUBMIT],
              s1, s1_sol, n1, {n1.actions[-1]['text']: W},
              cases=[{'y_true': [3, 8, 1], 'y_pred': [5, 4, 4]}, {'y_true': [7, 7], 'y_pred': [7, 9]}],
              reject=[([['report = mean_absolute_error(y_true, y_pred)\n', 'report = sum(errors) / len(errors)\n']], 'Signed mean'),
                      ([['report = mean_absolute_error(y_true, y_pred)\n', 'report = 2\n']], 'Typing the error')],
              accept=[([['report = mean_absolute_error(y_true, y_pred)\n', 'report = sum(abs(e) for e in errors) / len(errors)\n']], 'Absolute values by hand')]),
    code_step('stp_4c614280-b039-46d2-9de3-b1f9a2edcfc9', '** 0.5로 RMSE를 분 단위로 보고하세요', '제곱 오차와 제곱근을 씌운 오차의 단위를 구별해요.',
              'MSE 4.0은 분제곱 단위다. ** 0.5를 붙여 분 단위 RMSE 2.0을 확인한다. 채점은 다른 정답과 예측으로 실행한다.',
              '실제 시간은 분 단위예요. `mean_squared_error`(MSE)는 오차를 제곱해 평균내서 단위가 분의 제곱이에요. 제곱근을 씌운 RMSE가 다시 분 단위예요.',
              'report 줄을 고쳐 MSE에 제곱근을 씌워 실제 시간과 같은 분 단위로 보고하세요. 채점은 다른 예측으로도 실행해요.',
              ['코드 실행을 눌러 report를 확인하세요.', 'report 줄 끝에 `** 0.5`를 붙이세요.', '코드 실행을 눌러 분 단위 값을 확인하세요.', SUBMIT],
              s2, s2_sol, n2, {n2.actions[-1]['text']: W},
              cases=[{'y_true': [0, 0, 0, 0], 'y_pred': [3, 3, 3, 3]}, {'y_true': [10, 20, 30], 'y_pred': [10, 20, 36]}],
              reject=[([['report = mean_squared_error(y_true, y_pred) ** 0.5\n', 'report = mean_squared_error(y_true, y_pred)\n']], 'MSE in squared minutes'),
                      ([['report = mean_squared_error(y_true, y_pred) ** 0.5\n', 'report = 2\n']], 'Typing the value')],
              accept=[([['report = mean_squared_error(y_true, y_pred) ** 0.5\n', 'import math\nreport = math.sqrt(mean_squared_error(y_true, y_pred))\n']], 'math.sqrt')]),
    code_step('stp_5145836d-ef50-4155-aafc-1818867327cf', 'mean_squared_error로 MSE가 작은 후보를 고르세요', '보고 요구에 맞는 지표로 후보를 비교해 골라요.',
              'MAE로 고르면 a다. 비교를 mean_squared_error로 고쳐 큰 오차를 더 벌주는 기준의 b를 확인한다. 채점은 다른 후보 예측으로 실행한다.',
              '이번 요구는 큰 오차를 제곱해 더 벌주는 MSE가 가장 작은 후보예요. a는 6분 오차 하나, b는 3분 오차 세 개예요.',
              'chosen 줄을 고쳐 MAE가 아니라 MSE가 더 작은 후보를 고르세요. 채점은 다른 후보로도 실행해요.',
              ['코드 실행을 눌러 두 지표와 고른 후보를 확인하세요.', 'chosen 줄의 두 `mean_absolute_error`를 `mean_squared_error`로 고치세요.', '코드 실행을 눌러 고른 후보를 확인하세요.', SUBMIT],
              s3, s3_sol, n3, {n3.actions[-1]['text']: W},
              cases=[{'y_true': [0, 0, 0, 0], 'a': [1, 1, 1, 1], 'b': [0, 0, 0, 5]}, {'y_true': [5, 5], 'a': [5, 9], 'b': [7, 7]}],
              reject=[([['chosen = "a" if mean_squared_error(y_true, a) <= mean_squared_error(y_true, b) else "b"\n',
                         'chosen = "a" if mean_absolute_error(y_true, a) <= mean_absolute_error(y_true, b) else "b"\n']], 'MAE rule'),
                      ([['chosen = "a" if mean_squared_error(y_true, a) <= mean_squared_error(y_true, b) else "b"\n', 'chosen = "b"\n']], 'Typing the name')],
              accept=[([['chosen = "a" if mean_squared_error(y_true, a) <= mean_squared_error(y_true, b) else "b"\n',
                         'scores = {"a": mean_squared_error(y_true, a), "b": mean_squared_error(y_true, b)}\nchosen = min(scores, key=scores.get)\n']], 'min over a dict')]),
    code_step('stp_d0fb9983-3f54-4e66-a754-3d7c1bdd6afa', '평균에서 잰 sst로 R제곱을 직접 계산하세요', 'R제곱이 평균 예측과의 비교임을 계산해 음수도 확인해요.',
              '0에서 잰 sst로는 -12.857로 r2_score -96과 다르다. (t - mean)으로 고쳐 두 값이 -96.0으로 같음을 확인한다. 채점은 다른 정답과 예측으로 실행한다.',
              'R제곱은 1 − (예측의 제곱 오차 합 `sse`) ÷ (평균만 낸 예측의 제곱 오차 합 `sst`)예요. 그래서 평균 예측과 같으면 0, 완벽하면 1, 평균보다 나쁘면 음수예요.',
              'sst 줄을 고쳐 0이 아니라 평균 mean에서 잰 제곱 차이의 합을 sst에 담으세요. 채점은 다른 예측으로도 실행해요.',
              ['코드 실행을 눌러 직접 계산과 r2_score를 비교하세요.', 'sst 줄의 `t - 0`을 `t - mean`으로 고치세요.', '코드 실행을 눌러 두 값이 같은지 확인하세요.', SUBMIT],
              s4, s4_sol, n4, {n4.actions[-1]['text']: W},
              cases=[{'y_true': [2, 4, 9], 'y_pred': [3, 4, 8]}, {'y_true': [1, 2, 3, 4], 'y_pred': [2.5, 2.5, 2.5, 2.5]}],
              reject=[([['sst = sum((t - mean) ** 2 for t in y_true)\n', 'sst = sum((t - 0) ** 2 for t in y_true)\n']], 'Zero baseline'),
                      ([['print(round(1 - sse / sst, 6))', 'print(-96.0)']], 'Typing the score')],
              accept=[([['sst = sum((t - mean) ** 2 for t in y_true)\n', 'import numpy as np\nsst = float(np.var(y_true)) * len(y_true)\n']], 'Variance times count')]),
    code_step('stp_853b4d2b-830a-41ba-9f1d-a27ce46850fd', 'len(set(y_true))로 정답이 모두 같은지 확인하세요', 'R제곱의 보정값과 실제 오차를 구별해요.',
              '정답이 모두 5면 R제곱 0은 force_finite 보정값이다. constant = len(set(y_true)) == 1로 고쳐 True와 MAE 1을 함께 확인한다. 채점은 정답이 다양한 자료로도 실행한다.',
              '정답이 모두 같으면 R제곱의 분모(평균에서의 퍼짐)가 0이에요. `force_finite=True`는 이때 나눗셈 대신 정해진 보정값(0 또는 완벽하면 1)을 줘요. 그래서 R제곱 0만 보고 판단할 수 없어요.',
              'constant 줄을 고쳐 y_true의 값이 모두 같은지를 constant에 담으세요. 채점은 정답이 다양한 자료로도 실행해요.',
              ['코드 실행을 눌러 R제곱과 constant를 확인하세요.', '`constant = False`를 `constant = len(set(y_true)) == 1`로 고치세요.', '코드 실행을 눌러 constant와 MAE를 확인하세요.', SUBMIT],
              s5, s5_sol, n5, {n5.actions[-1]['text']: W},
              cases=[{'y_true': [5, 5, 5], 'y_pred': [5, 5, 5]}, {'y_true': [10, 20, 30], 'y_pred': [20, 20, 20]}],
              reject=[([['constant = len(set(y_true)) == 1\n', 'constant = r2 == 0\n']], 'Reading R² zero as constant'),
                      ([['constant = len(set(y_true)) == 1\n', 'constant = True\n']], 'Typing True')],
              accept=[([['constant = len(set(y_true)) == 1\n', 'constant = min(y_true) == max(y_true)\n']], 'min equals max')]),
    code_step('stp_3308b7b4-beee-4241-955a-e97399178eed', 'len(y_true) >= 2일 때만 R제곱을 계산하세요', '평가 관측 수가 R제곱을 정의할 수 있는지 확인해요.',
              '한 관측의 R제곱은 nan이다. 두 개 이상일 때만 계산하고 아니면 None으로 고쳐 None과 MAE 1을 확인한다. 채점은 여러 관측 자료로도 실행한다.',
              '평가 관측이 하나뿐이면 평균에서의 퍼짐이 없어 R제곱을 정의할 수 없어요. `r2_score`는 이때 nan을 내요. MAE는 한 관측에서도 계산돼요.',
              'r2 줄을 고쳐 평가 관측이 두 개 이상일 때만 R제곱을 계산하고, 아니면 None으로 두세요. 채점은 여러 관측 자료로도 실행해요.',
              ['코드 실행을 눌러 R제곱과 MAE를 확인하세요.', 'r2 줄 끝에 `if len(y_true) >= 2 else None`을 붙이세요.', '코드 실행을 눌러 두 값을 확인하세요.', SUBMIT],
              s6, s6_sol, n6, {n6.actions[-1]['text']: W},
              cases=[{'y_true': [10, 20, 30], 'y_pred': [12, 18, 30]}, {'y_true': [8], 'y_pred': [3]}],
              reject=[([['r2 = float(r2_score(y_true, y_pred)) if len(y_true) >= 2 else None\n', 'r2 = float(r2_score(y_true, y_pred))\n']], 'nan as a score'),
                      ([['r2 = float(r2_score(y_true, y_pred)) if len(y_true) >= 2 else None\n', 'r2 = None\n']], 'Never computing')],
              accept=[([['r2 = float(r2_score(y_true, y_pred)) if len(y_true) >= 2 else None\n',
                         'if len(y_true) < 2:\n    r2 = None\nelse:\n    r2 = float(r2_score(y_true, y_pred))\n']], 'if block')]),
    code_step('stp_0cf0390a-d3df-4414-95b2-679d6c1008dd', 'pred_ids로 같은 배송의 예측을 맞추세요', '지표를 내기 전에 실제와 예측을 같은 관측끼리 대응시켜요.',
              '순서가 뒤집힌 예측은 MAE 13.333이다. pred_ids.index로 배송 번호마다 예측을 맞춰 [10, 20, 30]과 MAE 0을 확인한다. 채점은 다른 순서로 실행한다.',
              '실제와 예측의 길이는 같지만 예측은 다른 배송 순서로 왔어요. 지표는 같은 자리끼리 비교하므로 먼저 배송 번호로 짝을 맞춰야 해요. `목록.index(값)`은 그 값이 있는 자리를 돌려줘요.',
              'aligned 줄을 고쳐 같은 배송 번호의 예측을 true_ids 순서로 맞추세요. 채점은 다른 순서로도 실행해요.',
              ['코드 실행을 눌러 aligned와 MAE를 확인하세요.', '`aligned = y_pred`를 `aligned = [y_pred[pred_ids.index(i)] for i in true_ids]`로 고치세요.', '코드 실행을 눌러 순서와 MAE를 확인하세요.', SUBMIT],
              s7, s7_sol, n7, {n7.actions[-1]['text']: W},
              cases=[{'true_ids': [7, 3, 5], 'y_true': [11, 40, 25], 'pred_ids': [3, 5, 7], 'y_pred': [42, 25, 10]},
                     {'true_ids': [1, 2], 'y_true': [9, 4], 'pred_ids': [1, 2], 'y_pred': [8, 6]}],
              reject=[([['aligned = [y_pred[pred_ids.index(i)] for i in true_ids]\n', 'aligned = y_pred[::-1]\n']], 'Reversing'),
                      ([['aligned = [y_pred[pred_ids.index(i)] for i in true_ids]\n', 'aligned = sorted(y_pred)\n']], 'Sorting the values')],
              accept=[([['aligned = [y_pred[pred_ids.index(i)] for i in true_ids]\n', 'lookup = dict(zip(pred_ids, y_pred))\naligned = [lookup[i] for i in true_ids]\n']], 'A dict by id')]),
]
