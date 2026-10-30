"""aice-classification-metrics: 9 answer-picking steps -> coding steps (2026-10-29).

Each step edits the line that computes one evaluation value: recall instead of accuracy, the
false-alarm cell, the precision and recall denominators, the harmonic mean, a no-alarm guard, the
support weights, the threshold in the alarm rule and AUC from scores. Prepared cases rerun with other
labels, alarms and probabilities, so typed results, swapped cells and denominators fail."""
from _kit import Script, code_step

OPENING = ['이 수업에서는 분류 결과를 업무 목적에 맞게 직접 코드로 평가해요. 놓친 경우와 잘못 알린 경우를 구별해요.',
           '혼동행렬에서 정밀도·재현율·F1을 계산해요. 임계값과 ROC AUC의 역할도 코드로 비교해요.']
PRD_SCOPE = ['두 챕터·세 단원·열한 스텝으로 같은 배송 경보를 검토해요.',
             '재현율·혼동행렬의 칸·정밀도와 재현율의 분모·조화평균·경보 없음 확인·support 가중 평균·임계값 경보·AUC를 한 곳씩 직접 고쳐 써요.']
PRD_GRADING = ['직접 고친 코드를 실제 파이썬·scikit-learn으로 실행해 판정해요. 실행·해설만으로 성공시키지 않아요.',
               '지연 누락·완벽 탐지·경보 없음·다른 확률과 기준의 표로 다시 실행해 기준 풀이와 비교해요. 결과를 글자로 적은 답, 뒤바뀐 칸과 분모, 산술평균, 고정된 기준, 범주 예측의 정확도는 거절해요.',
               '마지막 도전(stp_208e0760-9120-4546-a215-6633fba1ea5a): 실제 Python 실행과 다른 준비 자료의 결과를 검사해요. 시작 코드는 실패하고 동등한 풀이도 통과해야 해요.']
PRD_NARRATION = ['같은 자료를 유지하며 지표의 분모·칸·평균·기준을 고쳐 실제 값을 비교해요.',
                 '높은 정확도·축·분모·조화평균·분모0·평균 무게·기준·확률 순위를 조심할 지점으로 짚어요.']

SUBMIT = '수정한 코드를 제출하세요.'
W = '실제 scikit-learn 지표 계산을 정확히 말해요.'
ALERT = '# 같은 순서의 실제 종류와 예측 경보예요. 정상0·지연1이에요.\ny_true = [0, 0, 0, 1]\ny_pred = [0, 1, 0, 1]\n'
HITS = '# 확인용 계산: 실제 지연을 지연으로 경보한 건수예요.\nhits = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1)\n'

s1 = ('from sklearn.metrics import accuracy_score, recall_score\n\n# 정상 아홉 건과 지연 한 건을 모두 정상으로 예측했어요.\ny_true = [0] * 9 + [1]\ny_pred = [0] * 10\n'
      'print(float(accuracy_score(y_true, y_pred)))\n'
      '# 이 줄을 고쳐 정확도 대신 실제 지연 중 찾아낸 비율(지연 재현율)을 report에 담으세요.\nreport = accuracy_score(y_true, y_pred)\nprint(float(report))\n')
s1_sol = s1.replace('report = accuracy_score(y_true, y_pred)\n', '# 지연 탐지의 목적은 실제 지연(1)을 얼마나 찾았는지예요.\nreport = recall_score(y_true, y_pred, pos_label=1)\n')
n1 = (Script(s1)
      .say('목적은 지연을 찾는 거예요. report 줄을 고쳐 실제 지연 중 찾아낸 비율을 구해야 해요.', 'text:report 줄을 고쳐 정확도 대신 실제 지연 중 찾아낸 비율(지연 재현율)을 report에 담으세요.')
      .run('print(float(accuracy_score', 'print(float(report))')
      .say('0.9와 0.9예요. 정확도로는 지연을 찾았는지 알 수 없어요.', 'output')
      .patch('report = accuracy_score(y_true, y_pred)\n', 'report = recall_score(y_true, y_pred, pos_label=1)\n', 'recall_score(y_true, y_pred, pos_label=1)로 바꿔요.')
      .run('print(float(accuracy_score', 'print(float(report))')
      .say('0.0이에요. 실제 지연 한 건을 하나도 못 찾았어요.', 'output')
      .say('조심하세요. 정상이 대부분이면 모두 정상이라고만 해도 정확도가 높아요. 관심 범주의 재현율을 함께 봐요.', 'code:report = recall_score'))

s2 = ('from sklearn.metrics import confusion_matrix\n\n' + ALERT + '# 행은 실제, 열은 예측이에요. 범주 순서는 0, 1이에요.\nmatrix = confusion_matrix(y_true, y_pred, labels=[0, 1]).tolist()\nprint(matrix)\n'
      '# 이 줄을 고쳐 실제 정상0인데 지연1로 경보한 칸을 false_alarms에 담으세요.\nfalse_alarms = matrix[1][0]\nprint(false_alarms)\n')
s2_sol = s2.replace('false_alarms = matrix[1][0]\n', '# 실제 0의 행(0번)에서 예측 1의 열(1번)이에요.\nfalse_alarms = matrix[0][1]\n')
n2 = (Script(s2)
      .say('혼동행렬은 실제가 행, 예측이 열이에요. false_alarms 줄을 고쳐 실제 정상·예측 지연 칸을 꺼내야 해요.', 'text:false_alarms 줄을 고쳐 실제 정상0인데 지연1로 경보한 칸을 false_alarms에 담으세요.')
      .run('print(matrix)', 'print(false_alarms)')
      .say('[[2, 1], [0, 1]]과 0이에요. 0은 실제 지연을 정상으로 놓친 칸이에요.', 'output')
      .patch('false_alarms = matrix[1][0]\n', 'false_alarms = matrix[0][1]\n', 'matrix[1][0]을 matrix[0][1]로 바꿔요.')
      .run('print(matrix)', 'print(false_alarms)')
      .say('1이에요. 실제 정상인데 지연으로 알린 경보가 한 건이에요.', 'output')
      .say('조심하세요. 행과 열을 바꿔 읽으면 놓친 지연과 잘못된 경보가 뒤바뀌어요.', 'code:matrix[0][1]'))

s3 = ('from sklearn.metrics import precision_score\n\n' + ALERT + HITS
      + '# 이 줄을 고쳐 전체 행 수가 아니라 지연 경보의 수로 나눠 정밀도를 구하세요.\nprecision = hits / len(y_true)\n'
      'print(round(precision, 6))\nprint(round(float(precision_score(y_true, y_pred, pos_label=1, zero_division=0)), 6))\n')
s3_sol = s3.replace('precision = hits / len(y_true)\n', '# 정밀도는 지연 경보(예측 1) 중 실제 지연의 비율이에요.\nprecision = hits / sum(y_pred)\n')
n3 = (Script(s3)
      .say('정밀도는 경보 중 맞은 비율이에요. precision 줄을 고쳐 지연 경보의 수로 나눠야 해요.', 'text:precision 줄을 고쳐 전체 행 수가 아니라 지연 경보의 수로 나눠 정밀도를 구하세요.')
      .run('print(round(precision', 'print(round(float(precision_score')
      .say('0.25와 0.5예요. 네 행 전체로 나눠 precision_score와 달라요.', 'output')
      .patch('precision = hits / len(y_true)\n', 'precision = hits / sum(y_pred)\n', 'len(y_true)를 sum(y_pred)로 바꿔요.')
      .run('print(round(precision', 'print(round(float(precision_score')
      .say('0.5와 0.5예요. 경보 두 건 중 한 건이 실제 지연이에요.', 'output')
      .say('조심하세요. 정밀도의 분모는 전체 행이 아니라 경보한 건수예요.', 'code:hits / sum(y_pred)'))

s4 = ('from sklearn.metrics import recall_score\n\n' + ALERT + HITS
      + '# 이 줄을 고쳐 지연 경보의 수가 아니라 실제 지연의 수로 나눠 재현율을 구하세요.\nrecall = hits / sum(y_pred)\n'
      'print(round(recall, 6))\nprint(round(float(recall_score(y_true, y_pred, pos_label=1, zero_division=0)), 6))\n')
s4_sol = s4.replace('recall = hits / sum(y_pred)\n', '# 재현율은 실제 지연(정답 1) 중 찾아낸 비율이에요.\nrecall = hits / sum(y_true)\n')
n4 = (Script(s4)
      .say('재현율은 실제 지연 중 찾은 비율이에요. recall 줄을 고쳐 실제 지연의 수로 나눠야 해요.', 'text:recall 줄을 고쳐 지연 경보의 수가 아니라 실제 지연의 수로 나눠 재현율을 구하세요.')
      .run('print(round(recall', 'print(round(float(recall_score')
      .say('0.5와 1.0이에요. 경보 수로 나누면 정밀도가 돼요.', 'output')
      .patch('recall = hits / sum(y_pred)\n', 'recall = hits / sum(y_true)\n', 'sum(y_pred)를 sum(y_true)로 바꿔요.')
      .run('print(round(recall', 'print(round(float(recall_score')
      .say('1.0과 1.0이에요. 실제 지연 한 건을 찾았어요.', 'output')
      .say('조심하세요. 정밀도와 재현율은 분자는 같고 분모만 달라요. 경보 수인지 실제 수인지 확인해요.', 'code:hits / sum(y_true)'))

s5 = ('from sklearn.metrics import f1_score, precision_score, recall_score\n\n' + ALERT
      + 'precision = float(precision_score(y_true, y_pred, pos_label=1))\nrecall = float(recall_score(y_true, y_pred, pos_label=1))\nprint(precision, recall)\n'
      '# 이 줄을 고쳐 산술평균이 아니라 정밀도와 재현율의 조화평균(F1)을 구하세요.\nf1 = (precision + recall) / 2\n'
      'print(round(f1, 6))\nprint(round(float(f1_score(y_true, y_pred, pos_label=1)), 6))\n')
s5_sol = s5.replace('f1 = (precision + recall) / 2\n', '# 조화평균은 둘 중 낮은 쪽에 더 끌려요. 한쪽만 높아서는 F1이 높지 않아요.\nf1 = 2 * precision * recall / (precision + recall)\n')
n5 = (Script(s5)
      .say('정밀도 0.5·재현율 1이에요. f1 줄을 고쳐 산술평균이 아니라 조화평균을 구해야 해요.', 'text:f1 줄을 고쳐 산술평균이 아니라 정밀도와 재현율의 조화평균(F1)을 구하세요.')
      .run('print(precision, recall)', 'print(round(float(f1_score')
      .say('0.75와 0.666667이에요. 산술평균은 f1_score와 달라요.', 'output')
      .patch('f1 = (precision + recall) / 2\n', 'f1 = 2 * precision * recall / (precision + recall)\n', '2 × 정밀도 × 재현율 ÷ (정밀도 + 재현율)로 바꿔요.')
      .run('print(precision, recall)', 'print(round(float(f1_score')
      .say('0.666667과 0.666667이에요. 낮은 정밀도 쪽으로 끌렸어요.', 'output')
      .say('조심하세요. F1을 두 수의 단순 평균으로 보고하지 않아요. 한쪽이 낮으면 F1도 낮아요.', 'code:2 * precision * recall'))

s6 = ('from sklearn.metrics import precision_score, recall_score\n\n# 지연 경보가 아예 없을 수 있어요.\ny_true = [0, 1]\ny_pred = [0, 0]\n'
      '# 이 줄을 고쳐 지연 경보가 하나 이상일 때만 정밀도를 계산하고, 아니면 None으로 두세요.\nprecision = float(precision_score(y_true, y_pred, zero_division=1))\n'
      'print(precision)\nprint(float(recall_score(y_true, y_pred, zero_division=0)))\n')
s6_sol = s6.replace('precision = float(precision_score(y_true, y_pred, zero_division=1))\n',
                    '# 경보가 없으면 정밀도의 분모가 0이에요. zero_division 값은 그때 돌려줄 약속일 뿐이에요.\nprecision = float(precision_score(y_true, y_pred, zero_division=1)) if sum(y_pred) > 0 else None\n')
n6 = (Script(s6)
      .say('지연 경보가 하나도 없어요. precision 줄을 고쳐 경보가 있을 때만 정밀도를 계산해야 해요.', 'text:precision 줄을 고쳐 지연 경보가 하나 이상일 때만 정밀도를 계산하고, 아니면 None으로 두세요.')
      .run('print(precision)', 'print(float(recall_score')
      .say('1.0과 0.0이에요. 정밀도 1은 분모가 0일 때 돌려준 약속값이에요.', 'output')
      .patch('zero_division=1))\n', 'zero_division=1)) if sum(y_pred) > 0 else None\n', '뒤에 if sum(y_pred) > 0 else None을 붙여요.')
      .run('print(precision)', 'print(float(recall_score')
      .say('None과 0.0이에요. 정밀도는 정할 수 없고 실제 지연은 하나도 못 찾았어요.', 'output')
      .say('조심하세요. 분모가 0일 때의 1을 경보가 모두 맞았다고 읽지 않아요. 재현율을 함께 봐요.', 'code:sum(y_pred) > 0'))

s7 = ('from sklearn.metrics import recall_score\n\n# 세 범주의 크기가 세 건·한 건·한 건으로 달라요.\ny_true = [0, 0, 0, 1, 2]\ny_pred = [0, 0, 0, 0, 0]\nlabels = [0, 1, 2]\n'
      'per_class = recall_score(y_true, y_pred, labels=labels, average=None, zero_division=0).tolist()\nsupport = [y_true.count(label) for label in labels]\nprint(per_class, support)\n'
      '# 이 줄을 고쳐 범주마다 같은 무게가 아니라 실제 건수 support로 가중 평균하세요.\nweighted = sum(per_class) / len(per_class)\n'
      'print(round(weighted, 6))\nprint(round(float(recall_score(y_true, y_pred, labels=labels, average="weighted", zero_division=0)), 6))\n')
s7_sol = s7.replace('weighted = sum(per_class) / len(per_class)\n',
                    '# weighted는 범주마다 실제 건수만큼 무게를 줘요. 같은 무게로 나누는 평균은 macro예요.\nweighted = sum(r * s for r, s in zip(per_class, support)) / sum(support)\n')
n7 = (Script(s7)
      .say('범주의 크기가 3·1·1로 달라요. weighted 줄을 고쳐 실제 건수 support로 가중 평균해야 해요.', 'text:weighted 줄을 고쳐 범주마다 같은 무게가 아니라 실제 건수 support로 가중 평균하세요.')
      .run('print(per_class, support)', 'print(round(float(recall_score')
      .say('같은 무게의 평균은 0.333333, weighted는 0.6이에요. 지금 식은 macro예요.', 'output')
      .patch('weighted = sum(per_class) / len(per_class)\n', 'weighted = sum(r * s for r, s in zip(per_class, support)) / sum(support)\n', '재현율마다 support를 곱해 더하고 sum(support)로 나눠요.')
      .run('print(per_class, support)', 'print(round(float(recall_score')
      .say('0.6과 0.6이에요. 큰 범주 0의 재현율 1이 무게 3을 받았어요.', 'output')
      .say('조심하세요. weighted는 큰 범주가 결과를 끌어요. 작은 범주를 놓친 것은 macro로 드러나요.', 'code:zip(per_class, support)'))

s8 = ('from sklearn.metrics import precision_score, recall_score\n\n# 같은 지연 확률을 어떤 기준에서 경보로 바꿀지 정해요.\ny_true = [0, 0, 1, 1]\nprobabilities = [0.1, 0.6, 0.4, 0.8]\nthreshold = 0.3\n'
      '# 이 줄을 고쳐 0.5 대신 threshold 이상인 확률을 경보 1로 바꾸세요.\npredictions = [int(p >= 0.5) for p in probabilities]\n'
      'print(predictions)\nprint(round(float(precision_score(y_true, predictions, zero_division=0)), 6))\nprint(round(float(recall_score(y_true, predictions, zero_division=0)), 6))\n')
s8_sol = s8.replace('predictions = [int(p >= 0.5) for p in probabilities]\n', '# 확률은 그대로이고, 기준이 낮아지면 기준 이상인 확률이 늘어 경보가 늘어요.\npredictions = [int(p >= threshold) for p in probabilities]\n')
n8 = (Script(s8)
      .say('기준을 0.3으로 낮추려 해요. predictions 줄을 고쳐 0.5 대신 threshold를 써야 해요.', 'text:predictions 줄을 고쳐 0.5 대신 threshold 이상인 확률을 경보 1로 바꾸세요.')
      .run('print(predictions)', 'print(round(float(recall_score')
      .say('[0, 1, 0, 1]과 정밀도 0.5·재현율 0.5예요. 0.4인 지연을 놓쳤어요.', 'output')
      .patch('p >= 0.5', 'p >= threshold', '0.5를 threshold로 바꿔요.')
      .run('print(predictions)', 'print(round(float(recall_score')
      .say('[0, 1, 1, 1]과 정밀도 0.666667·재현율 1.0이에요. 경보가 하나 늘고 놓친 지연을 찾았어요.', 'output')
      .say('조심하세요. 기준을 낮추면 놓침은 줄지만 잘못된 경보가 늘 수 있어요. 두 지표를 함께 봐요.', 'code:p >= threshold'))

s9 = ('from sklearn.metrics import accuracy_score, roc_auc_score\n\n# 지연1에 해당하는 확률이에요.\ny_true = [0, 0, 1, 1]\nscores = [0.1, 0.6, 0.4, 0.8]\n'
      '# 두 범주가 있어야 순위를 비교할 수 있어요.\nif len(set(y_true)) != 2:\n    print("AUC 정의 불가")\nelse:\n'
      '    # 이 줄을 고쳐 0.5 기준 정확도가 아니라 확률의 순위로 AUC를 구하세요.\n    auc = accuracy_score(y_true, [int(s >= 0.5) for s in scores])\n    print(round(float(auc), 4))\n')
s9_sol = s9.replace('    auc = accuracy_score(y_true, [int(s >= 0.5) for s in scores])\n',
                    '    # AUC는 기준 없이 확률 그대로, 지연 쪽 점수가 정상보다 높은 짝의 비율이에요.\n    auc = roc_auc_score(y_true, scores)\n')
n9 = (Script(s9)
      .say('AUC는 기준을 정하지 않고 확률의 순위를 평가해요. auc 줄을 roc_auc_score로 고쳐야 해요.', 'text:auc 줄을 고쳐 0.5 기준 정확도가 아니라 확률의 순위로 AUC를 구하세요.')
      .run('print(round(float(auc')
      .say('0.5예요. 0.5 기준으로 자른 범주의 정확도예요.', 'output')
      .patch('auc = accuracy_score(y_true, [int(s >= 0.5) for s in scores])\n', 'auc = roc_auc_score(y_true, scores)\n', 'roc_auc_score(y_true, scores)로 바꿔요.')
      .run('print(round(float(auc')
      .say('0.75예요. 지연·정상 짝 네 개 중 세 개에서 지연 쪽 확률이 더 높았어요.', 'output')
      .say('조심하세요. AUC 0.75는 정답률 75%가 아니에요. 확률 순위의 평가예요.', 'code:roc_auc_score(y_true, scores)'))

SPECS = [
    code_step('stp_32e5ad72-73aa-4cb3-8e04-7950edb27f38', 'recall_score로 지연을 찾은 비율을 보고하세요', '높은 정확도와 관심 범주의 재현율을 구별해요.',
              '모두 정상으로 예측하면 정확도 0.9다. recall_score(pos_label=1)로 고쳐 지연 재현율 0을 확인한다. 채점은 다른 경보 표로 실행한다.',
              '재현율은 실제 지연 중 모델이 지연으로 찾아낸 비율이에요. 정상 아홉 건과 지연 한 건을 모두 정상으로 예측했어요. `recall_score(y_true, y_pred, pos_label=1)`은 지연(1)의 재현율이에요.',
              'report 줄을 고쳐 정확도 대신 실제 지연 중 찾아낸 비율(지연 재현율)을 report에 담으세요. 채점은 다른 경보로도 실행해요.',
              ['코드 실행을 눌러 정확도와 report를 확인하세요.', '`accuracy_score(y_true, y_pred)`를 `recall_score(y_true, y_pred, pos_label=1)`로 고치세요.', '코드 실행을 눌러 지연 재현율을 확인하세요.', SUBMIT],
              s1, s1_sol, n1, {n1.actions[-1]['text']: W},
              cases=[{'y_true': [0, 0, 1, 1], 'y_pred': [0, 0, 1, 0]}, {'y_true': [1, 0, 1], 'y_pred': [1, 1, 1]}],
              reject=[([['report = recall_score(y_true, y_pred, pos_label=1)\n', 'report = accuracy_score(y_true, y_pred)\n']], 'Accuracy'),
                      ([['report = recall_score(y_true, y_pred, pos_label=1)\n', 'report = 0\n']], 'Typing the recall')],
              accept=[([['report = recall_score(y_true, y_pred, pos_label=1)\n', 'report = sum(1 for t, p in zip(y_true, y_pred) if t == p == 1) / y_true.count(1)\n']], 'Counting by hand')]),
    code_step('stp_e89aec00-5536-4f2b-b5c6-52c6f961ec4f', 'matrix[0][1]로 잘못된 경보를 세세요', '혼동행렬의 실제 행과 예측 열을 읽어 잘못된 경보를 찾아요.',
              'matrix[1][0]은 놓친 지연 0이다. matrix[0][1]로 고쳐 실제 정상·예측 지연의 1건을 확인한다. 채점은 다른 경보 표로 실행한다.',
              '`confusion_matrix(y_true, y_pred, labels=[0, 1])`는 행이 실제, 열이 예측인 표예요. `matrix[행][열]`로 칸을 읽어요. 실제 정상0인데 지연1로 알린 것이 잘못된 경보예요.',
              'false_alarms 줄을 고쳐 실제 정상0인데 지연1로 경보한 칸을 false_alarms에 담으세요. 채점은 다른 경보로도 실행해요.',
              ['코드 실행을 눌러 표와 false_alarms를 확인하세요.', '`matrix[1][0]`을 `matrix[0][1]`로 고치세요.', '코드 실행을 눌러 잘못된 경보 수를 확인하세요.', SUBMIT],
              s2, s2_sol, n2, {n2.actions[-1]['text']: W},
              cases=[{'y_true': [0, 0, 1, 1, 0], 'y_pred': [1, 1, 0, 1, 1]}, {'y_true': [1, 1, 0], 'y_pred': [0, 0, 0]}],
              reject=[([['false_alarms = matrix[0][1]\n', 'false_alarms = matrix[1][0]\n']], 'Missed delays'),
                      ([['false_alarms = matrix[0][1]\n', 'false_alarms = 1\n']], 'Typing the count')],
              accept=[([['false_alarms = matrix[0][1]\n', 'false_alarms = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 1)\n']], 'Counting pairs')]),
    code_step('stp_922fb8db-9496-46fe-8061-8d571ebb7f07', 'sum(y_pred)로 나눠 정밀도를 구하세요', '정밀도의 분모가 지연 경보의 수임을 계산해 확인해요.',
              '전체 네 행으로 나누면 0.25다. hits / sum(y_pred)로 고쳐 경보 두 건 중 맞은 비율 0.5를 확인한다. 채점은 다른 경보 표로 실행한다.',
              '정밀도는 지연이라고 경보한 것 중 실제 지연의 비율이에요. `hits`는 실제 지연을 지연으로 경보한 건수예요. 경보 1은 `y_pred`에서 1인 자리이므로 `sum(y_pred)`가 경보 수예요.',
              'precision 줄을 고쳐 전체 행 수가 아니라 지연 경보의 수로 나눠 정밀도를 구하세요. 채점은 다른 경보로도 실행해요.',
              ['코드 실행을 눌러 직접 계산과 precision_score를 비교하세요.', '`len(y_true)`를 `sum(y_pred)`로 고치세요.', '코드 실행을 눌러 두 값이 같은지 확인하세요.', SUBMIT],
              s3, s3_sol, n3, {n3.actions[-1]['text']: W},
              cases=[{'y_true': [1, 1, 0, 1, 0], 'y_pred': [1, 1, 1, 1, 0]}, {'y_true': [1, 0], 'y_pred': [1, 1]}],
              reject=[([['precision = hits / sum(y_pred)\n', 'precision = hits / len(y_true)\n']], 'All rows'),
                      ([['precision = hits / sum(y_pred)\n', 'precision = hits / sum(y_true)\n']], 'Recall denominator')],
              accept=[([['precision = hits / sum(y_pred)\n', 'precision = hits / y_pred.count(1)\n']], 'count(1)')]),
    code_step('stp_4848ba0b-2efb-4226-a61c-21ae32231f99', 'sum(y_true)로 나눠 재현율을 구하세요', '재현율의 분모가 실제 지연의 수임을 계산해 확인해요.',
              '경보 수로 나누면 정밀도와 같은 0.5다. hits / sum(y_true)로 고쳐 실제 지연 한 건을 찾은 재현율 1.0을 확인한다. 채점은 다른 경보 표로 실행한다.',
              '재현율은 실제 지연 중 찾아낸 비율이에요. 분자 `hits`는 정밀도와 같고, 분모가 실제 지연의 수 `sum(y_true)`예요.',
              'recall 줄을 고쳐 지연 경보의 수가 아니라 실제 지연의 수로 나눠 재현율을 구하세요. 채점은 다른 경보로도 실행해요.',
              ['코드 실행을 눌러 직접 계산과 recall_score를 비교하세요.', '`sum(y_pred)`를 `sum(y_true)`로 고치세요.', '코드 실행을 눌러 두 값이 같은지 확인하세요.', SUBMIT],
              s4, s4_sol, n4, {n4.actions[-1]['text']: W},
              cases=[{'y_true': [1, 1, 0, 1, 0], 'y_pred': [1, 0, 1, 0, 1]}, {'y_true': [1, 1, 1, 0], 'y_pred': [1, 1, 1, 1]}],
              reject=[([['recall = hits / sum(y_true)\n', 'recall = hits / sum(y_pred)\n']], 'Precision denominator'),
                      ([['recall = hits / sum(y_true)\n', 'recall = 1.0\n']], 'Typing the recall')],
              accept=[([['recall = hits / sum(y_true)\n', 'recall = hits / y_true.count(1)\n']], 'count(1)')]),
    code_step('stp_6b339386-deb4-4076-a0fd-bd1fa4d4c96e', '조화평균으로 F1을 직접 계산하세요', 'F1이 정밀도와 재현율의 조화평균임을 계산해 확인해요.',
              '산술평균은 0.75로 f1_score 0.666667과 다르다. 2 * precision * recall / (precision + recall)로 고쳐 두 값이 같음을 확인한다. 채점은 다른 경보 표로 실행한다.',
              '정밀도 0.5·재현율 1이에요. F1은 두 지표의 조화평균 2 × 정밀도 × 재현율 ÷ (정밀도 + 재현율)이에요. 조화평균은 둘 중 낮은 쪽에 더 끌려요.',
              'f1 줄을 고쳐 산술평균이 아니라 정밀도와 재현율의 조화평균(F1)을 구하세요. 채점은 다른 경보로도 실행해요.',
              ['코드 실행을 눌러 직접 계산과 f1_score를 비교하세요.', '`(precision + recall) / 2`를 `2 * precision * recall / (precision + recall)`로 고치세요.', '코드 실행을 눌러 두 값이 같은지 확인하세요.', SUBMIT],
              s5, s5_sol, n5, {n5.actions[-1]['text']: W},
              cases=[{'y_true': [1, 1, 1, 1, 0], 'y_pred': [1, 0, 0, 0, 0]}, {'y_true': [1, 0, 1, 0], 'y_pred': [1, 1, 1, 0]}],
              reject=[([['f1 = 2 * precision * recall / (precision + recall)\n', 'f1 = (precision + recall) / 2\n']], 'Arithmetic mean'),
                      ([['print(round(f1, 6))', 'print(0.666667)']], 'Typing the F1')],
              accept=[([['f1 = 2 * precision * recall / (precision + recall)\n', 'f1 = 2 / (1 / precision + 1 / recall)\n']], 'Reciprocal form')]),
    code_step('stp_388c1239-87b9-4423-a434-61ad24e377c7', 'sum(y_pred) > 0일 때만 정밀도를 계산하세요', '분모가 없는 정밀도의 약속값과 실제 성능을 구별해요.',
              '경보가 없어 zero_division=1이 정밀도 1.0을 돌려준다. 경보가 있을 때만 계산하고 아니면 None으로 고쳐 None과 재현율 0을 확인한다. 채점은 경보가 있는 자료로도 실행한다.',
              '지연 경보가 아예 없으면 정밀도의 분모(경보 수)가 0이에요. `zero_division=1`은 그때 1을 돌려주라는 약속일 뿐, 경보가 맞았다는 뜻이 아니에요.',
              'precision 줄을 고쳐 지연 경보가 하나 이상일 때만 정밀도를 계산하고, 아니면 None으로 두세요. 채점은 경보가 있는 자료로도 실행해요.',
              ['코드 실행을 눌러 정밀도와 재현율을 확인하세요.', 'precision 줄 끝에 `if sum(y_pred) > 0 else None`을 붙이세요.', '코드 실행을 눌러 두 값을 확인하세요.', SUBMIT],
              s6, s6_sol, n6, {n6.actions[-1]['text']: W},
              cases=[{'y_true': [0, 1, 1], 'y_pred': [1, 1, 0]}, {'y_true': [1, 1, 0, 0], 'y_pred': [0, 0, 0, 0]}],
              reject=[([['zero_division=1)) if sum(y_pred) > 0 else None\n', 'zero_division=1))\n']], 'Policy value as a score'),
                      ([['precision = float(precision_score(y_true, y_pred, zero_division=1)) if sum(y_pred) > 0 else None\n', 'precision = None\n']], 'Never computing')],
              accept=[([['precision = float(precision_score(y_true, y_pred, zero_division=1)) if sum(y_pred) > 0 else None\n',
                         'precision = None\nif 1 in y_pred:\n    precision = float(precision_score(y_true, y_pred))\n']], 'if block')]),
    code_step('stp_42d6681d-b5bb-4ef3-bd4f-14ac71094689', 'support로 가중 평균한 재현율을 구하세요', 'macro와 weighted 평균의 무게 차이를 계산해 확인해요.',
              '같은 무게의 평균은 macro 0.333333이다. 재현율마다 support를 곱해 sum(support)로 나누도록 고쳐 weighted 0.6을 확인한다. 채점은 범주 크기가 다른 자료로 실행한다.',
              '범주별 재현율은 1·0·0이고, 실제 건수(support)는 3·1·1이에요. macro는 범주마다 같은 무게로, weighted는 support만큼 무게를 줘 평균내요.',
              'weighted 줄을 고쳐 범주마다 같은 무게가 아니라 실제 건수 support로 가중 평균하세요. 채점은 다른 자료로도 실행해요.',
              ['코드 실행을 눌러 범주별 재현율과 두 평균을 확인하세요.', 'weighted 줄을 `sum(r * s for r, s in zip(per_class, support)) / sum(support)`로 고치세요.', '코드 실행을 눌러 두 값이 같은지 확인하세요.', SUBMIT],
              s7, s7_sol, n7, {n7.actions[-1]['text']: W},
              cases=[{'y_true': [0, 1, 1, 1, 2, 2], 'y_pred': [0, 1, 0, 0, 2, 2]}, {'y_true': [2, 2, 2, 2, 0, 1], 'y_pred': [2, 2, 0, 0, 0, 1]}],
              reject=[([['weighted = sum(r * s for r, s in zip(per_class, support)) / sum(support)\n', 'weighted = sum(per_class) / len(per_class)\n']], 'macro'),
                      ([['print(round(weighted, 6))', 'print(0.6)']], 'Typing the score')],
              accept=[([['weighted = sum(r * s for r, s in zip(per_class, support)) / sum(support)\n', 'import numpy as np\nweighted = float(np.average(per_class, weights=support))\n']], 'np.average')]),
    code_step('stp_433c9dc6-3b49-4b6b-8982-4ae6c839fd73', 'threshold로 경보 기준을 바꾸세요', '같은 확률에 다른 경보 기준을 적용해 경보와 지표의 변화를 확인해요.',
              '0.5에 고정된 규칙은 0.4인 지연을 놓친다. p >= threshold로 고쳐 기준 0.3의 경보 [0, 1, 1, 1]과 재현율 1.0을 확인한다. 채점은 다른 확률과 기준으로 실행한다.',
              '확률마다 기준 이상이면 1(경보), 아니면 0으로 바꿔요. `threshold`에 이번 기준 0.3이 들어 있어요. 확률은 그대로이고 기준만 바뀌어요.',
              'predictions 줄을 고쳐 0.5 대신 threshold 이상인 확률을 경보 1로 바꾸세요. 채점은 다른 기준으로도 실행해요.',
              ['코드 실행을 눌러 경보와 두 지표를 확인하세요.', '`p >= 0.5`를 `p >= threshold`로 고치세요.', '코드 실행을 눌러 경보와 지표의 변화를 확인하세요.', SUBMIT],
              s8, s8_sol, n8, {n8.actions[-1]['text']: W},
              cases=[{'threshold': 0.7, 'probabilities': [0.65, 0.9, 0.7, 0.2]}, {'threshold': 0.4, 'y_true': [1, 0, 1], 'probabilities': [0.4, 0.45, 0.1]}],
              reject=[([['p >= threshold', 'p >= 0.5']], 'Fixed 0.5'),
                      ([['p >= threshold', 'p > threshold']], 'Strictly above')],
              accept=[([['predictions = [int(p >= threshold) for p in probabilities]\n', 'import numpy as np\npredictions = (np.array(probabilities) >= threshold).astype(int).tolist()\n']], 'numpy comparison')]),
    code_step('stp_b36bfae9-1b3e-4c1b-9fbd-66eaadac180b', 'roc_auc_score로 확률의 순위를 평가하세요', '기준을 정한 정확도와 확률 순위의 AUC를 구별해요.',
              '0.5 기준으로 자른 정확도는 0.5다. roc_auc_score(y_true, scores)로 고쳐 확률 순위의 AUC 0.75를 확인한다. 채점은 다른 확률과 한 범주 자료로 실행한다.',
              'AUC는 실제 지연 하나와 실제 정상 하나를 짝지었을 때 지연 쪽 점수가 더 높은 짝의 비율이에요. 기준을 정하지 않고 확률 그대로 `roc_auc_score(y_true, scores)`로 구해요.',
              'auc 줄을 고쳐 0.5 기준 정확도가 아니라 확률의 순위로 AUC를 구하세요. 채점은 다른 확률로도 실행해요.',
              ['코드 실행을 눌러 auc를 확인하세요.', 'auc 줄을 `auc = roc_auc_score(y_true, scores)`로 고치세요.', '코드 실행을 눌러 AUC를 확인하세요.', SUBMIT],
              s9, s9_sol, n9, {n9.actions[-1]['text']: W},
              cases=[{'y_true': [1, 0, 1, 0, 0], 'scores': [0.3, 0.2, 0.9, 0.45, 0.35]}, {'y_true': [1, 1], 'scores': [0.2, 0.7]}],
              reject=[([['    auc = roc_auc_score(y_true, scores)\n', '    auc = accuracy_score(y_true, [int(s >= 0.5) for s in scores])\n']], 'Accuracy at 0.5'),
                      ([['    auc = roc_auc_score(y_true, scores)\n', '    auc = roc_auc_score(y_true, [int(s >= 0.5) for s in scores])\n']], 'AUC of cut labels')],
              accept=[([['    auc = roc_auc_score(y_true, scores)\n',
                         '    pos = [s for s, t in zip(scores, y_true) if t == 1]\n    neg = [s for s, t in zip(scores, y_true) if t == 0]\n'
                         '    auc = sum((p > n) + 0.5 * (p == n) for p in pos for n in neg) / (len(pos) * len(neg))\n']], 'Counting pairs')]),
]
