"""aice-quality: 4 answer-picking steps -> coding steps (2026-10-29).

Steps 5 (모든 시간이 비면 중앙값 채움이 해결되나) and 9 (범위 밖의 실제 기록을 지울까) stay choices: they
ask for a data-handling judgment, not for code. Converted steps vary the prepared data through prepared
cases, so typed results and the starter's wrong rule fail."""
from _kit import Script, code_step

OPENING = ['이 수업에서는 결측과 중복을 다루는 기준을 직접 코드로 써 봐요. 정상 값과 검토할 값을 구별하는 게 목표예요.',
           '자료를 검사하고 처리 조건을 바꿔요. 어떤 행과 값이 남는지 실행 결과로 확인해요.']
PRD_SCOPE = ['세 챕터·세 단원·열한 스텝으로 같은 배송 파일을 정리해요.',
             '결측 표시(isna)·측정 건수(count)·전체 행 중복(duplicated)·IQR 경계 비교를 직접 고쳐 쓰고, 채움·중복 보존·처리 조합을 이어서 다뤄요. 관측 없음·실제 이상값 판단은 선택 문항으로 남겨요.']
PRD_GRADING = ['직접 고친 코드를 실제 파이썬·판다스로 실행해 판정해요. 실행·해설만으로 성공시키지 않아요.',
               '여러 자료에서 남은 주문 번호·시간·원래 결측 상태를 함께 검사해요. 준비 자료를 바꿔 다시 실행해 기준 풀이의 실제 결과와 비교하고, 결과를 글자로 적은 답이나 0을 결측으로 본 답은 거절해요.',
               '처리 정책은 문제의 업무 조건으로 명시하고 하나의 만능 처리법을 암기시키지 않아요. 관측이 없는 열과 실제 이상값의 처리는 판단 문항으로 선택 답을 판정해요.',
               '마지막 도전(stp_57fb87ab-7ab9-48e8-94d2-5cb5e2869448): 실제 파이썬 출력과 다른 자료 세 가지로 채점해요. 모든 열 dropna, 첫 수정본, 0분 제거는 실패해요.']
PRD_NARRATION = ['한 조건·한 옵션씩 고치고 실제 행·값의 차이를 확인해요.',
                 '정상0·측정 건수·전체 행 중복·경계값·관측없음·이상치 오해를 조심할 지점으로 짚어요.',
                 '정확한 줄·버튼·결과를 강조하며 학생 상태는 보존해요.']

HEAD = ('# 표를 다룰 판다스를 불러와요.\nimport pandas as pd\n'
        "# None은 측정하지 못한 값이에요. 0은 실제 시간이에요.\ndata = {'order_id': [101, 102, 103, 104], 'minutes': [0, None, 30, 42], 'region': ['서울', '부산', '서울', '부산'], 'note': [None, 'ok', 'ok', 'ok']}\n"
        '# 같은 배송 파일을 표로 확인해요.\ndf = pd.DataFrame(data)\n')
OTHER = [{'data': {'order_id': [201, 202, 203, 204, 205], 'minutes': [None, 0, None, 15, 0], 'region': ['부산', '서울', '서울', '부산', '부산'], 'note': ['ok', None, 'ok', 'ok', 'ok']}},
         {'data': {'order_id': [301, 302, 303], 'minutes': [7, 9, None], 'region': ['서울', '서울', '서울'], 'note': ['ok', 'ok', 'ok']}}]
SUBMIT = '수정한 코드를 제출하세요.'
W = '실제 판다스 동작을 정확히 말해요.'

s1 = HEAD + '# 이 줄을 고쳐 0분이 아니라 측정하지 못한 시간을 True로 표시하세요.\nmissing = df["minutes"] == 0\nprint(missing.tolist())\n'
s1_sol = s1.replace('missing = df["minutes"] == 0\n', '# isna()는 비어 있는 값(None·NaN)만 True로 표시해요. 0은 실제 값이라 False예요.\nmissing = df["minutes"].isna()\n')
n1 = (Script(s1)
      .say('측정하지 못한 시간만 찾으려 해요. 0분을 찾는 비교를 결측 표시로 고쳐야 해요.', 'text:missing 줄을 고쳐 0분이 아니라 측정하지 못한 시간을 True로 표시하세요.')
      .run('print(missing')
      .say('[True, False, False, False]예요. 실제로 0분 걸린 첫 배송을 골랐어요.', 'output')
      .patch('missing = df["minutes"] == 0\n', 'missing = df["minutes"].isna()\n', '== 0 비교를 isna()로 바꿔요.')
      .run('print(missing')
      .say('[False, True, False, False]예요. 비어 있는 두 번째 시간만 True예요.', 'output')
      .say('조심하세요. 0은 측정된 값이에요. 빈 값과 같은 뜻으로 섞으면 실제 기록을 잃어요.', 'code:isna()'))

s2 = HEAD + '# 전체 행 수를 먼저 확인해요.\nprint(len(df))\n# 이 줄을 고쳐 행 수가 아니라 시간이 실제로 있는 건수를 지역별로 세세요.\nprint(df.groupby("region").size().to_dict())\n'
s2_sol = s2.replace('print(df.groupby("region").size().to_dict())', '# count()는 비어 있지 않은 값만 세요. size()는 빈 값도 포함한 행 수예요.\nprint(df.groupby("region")["minutes"].count().to_dict())')
n2 = (Script(s2)
      .say('부산 배송은 두 건이에요. 시간이 실제로 있는 건수를 지역별로 세도록 고쳐야 해요.', 'text:마지막 print 줄을 고쳐 행 수가 아니라 시간이 실제로 있는 건수를 지역별로 세세요.')
      .run('print(len(df))', 'print(df.groupby')
      .say("4와 {'부산': 2, '서울': 2}예요. size는 시간이 비어 있는 행도 세요.", 'output')
      .patch('df.groupby("region").size()', 'df.groupby("region")["minutes"].count()', 'size() 대신 minutes 열의 count()를 써요.')
      .run('print(len(df))', 'print(df.groupby')
      .say("{'부산': 1, '서울': 2}예요. 부산 두 건 중 한 건의 시간이 비어 있어요. 행을 지운 게 아니에요.", 'output')
      .say('조심하세요. 서울의 0분도 실제 값이라 셌어요. count는 빈 값만 빼요.', 'code:["minutes"].count()'))

DUP = HEAD.replace("{'order_id': [101, 102, 103, 104], 'minutes': [0, None, 30, 42], 'region': ['서울', '부산', '서울', '부산'], 'note': [None, 'ok', 'ok', 'ok']}",
                   "{'order_id': [101, 102, 103, 103], 'minutes': [12, 18, 30, 42], 'region': ['서울', '부산', '서울', '서울'], 'note': ['ok', 'ok', 'ok', 'ok']}") \
    .replace('# None은 측정하지 못한 값이에요. 0은 실제 시간이에요.', '# 주문 103이 두 번 기록됐고 마지막 기록의 시간만 42예요.')
s6 = DUP + '# 주문 번호가 같은 기록을 세요.\nprint(df.duplicated(subset=["order_id"]).sum())\n# 이 줄을 고쳐 주문 번호만이 아니라 모든 항목이 같은 행을 세세요.\nprint(df.duplicated(subset=["order_id"]).sum())\n'
s6 = s6.replace('# 이 줄을 고쳐 주문 번호만이 아니라 모든 항목이 같은 행을 세세요.\nprint(df.duplicated(subset=["order_id"]).sum())',
                '# 이 줄을 고쳐 주문 번호만이 아니라 모든 항목이 같은 행을 세세요.\nsame_rows = df.duplicated(subset=["order_id"]).sum()\nprint(same_rows)')
s6_sol = s6.replace('same_rows = df.duplicated(subset=["order_id"]).sum()', '# subset 없이 쓰면 모든 열이 같아야 앞 행의 중복이에요.\nsame_rows = df.duplicated().sum()')
n6 = (Script(s6)
      .say('주문 103이 두 번 기록됐지만 시간이 달라요. 모든 항목이 같은 행만 세도록 고쳐야 해요.', 'text:same_rows 줄을 고쳐 주문 번호만이 아니라 모든 항목이 같은 행을 세세요.')
      .run('print(df.duplicated', 'print(same_rows)')
      .say('두 줄 모두 1이에요. 둘 다 주문 번호만 비교했어요.', 'output')
      .patch('same_rows = df.duplicated(subset=["order_id"]).sum()', 'same_rows = df.duplicated().sum()', 'subset을 지워 모든 열을 비교해요.')
      .run('print(df.duplicated', 'print(same_rows)')
      .say('1과 0이에요. 주문 번호는 겹치지만 시간 30과 42가 달라서 전체 행 중복은 없어요.', 'output')
      .say('조심하세요. 주문 번호가 같다고 같은 기록은 아니에요. 어떤 열이 같아야 중복인지 정하고 세요.', 'code:df.duplicated().sum()'))

IQR = ('# 기준 자료로 사분위수와 가운데 범위를 구해요.\nimport pandas as pd\nbase = [10, 12, 14, 16, 18]\nreference = pd.Series(base)\n'
       'q1 = reference.quantile(0.25)\nq3 = reference.quantile(0.75)\niqr = q3 - q1\n'
       '# 이번 검토 규칙은 이 범위의 바깥만 후보로 표시해요. 끝 값은 범위 안이에요.\nlower = q1 - 1.5 * iqr\nupper = q3 + 1.5 * iqr\n'
       'values = [5, 6, 22, 23]\nminutes = pd.Series(values)\nprint(lower, upper)\n')
s8 = IQR + '# 이 줄의 비교 기호를 고쳐 범위 끝 값은 후보에서 빼세요.\nflag = (minutes <= lower) | (minutes >= upper)\nprint(flag.tolist())\n'
s8_sol = s8.replace('flag = (minutes <= lower) | (minutes >= upper)', '# <와 >는 끝 값을 포함하지 않아요. 6과 22는 범위 안이에요.\nflag = (minutes < lower) | (minutes > upper)')
n8 = (Script(s8)
      .say('이번 검토 범위는 6분부터 22분까지예요. 끝 값이 후보가 되지 않게 비교 기호를 고쳐야 해요.', 'text:flag 줄의 비교 기호를 고쳐 범위 끝 값은 후보에서 빼세요.')
      .run('print(lower', 'print(flag')
      .say('6.0 22.0과 [True, True, True, True]예요. <=와 >=라서 끝 값 6과 22도 후보가 됐어요.', 'output')
      .patch('(minutes <= lower) | (minutes >= upper)', '(minutes < lower) | (minutes > upper)', '<=를 <로, >=를 >로 바꿔요.')
      .run('print(lower', 'print(flag')
      .say('[True, False, False, True]예요. 범위 밖인 5와 23만 후보예요.', 'output')
      .say('조심하세요. 후보로 표시된 값도 바로 지우지 않아요. 기록의 뜻을 확인한 뒤 처리 기준을 정해요.', 'code:(minutes < lower) | (minutes > upper)'))

IQR_CASES = [{'base': [20, 22, 24, 26, 28], 'values': [4, 13, 14, 32, 33, 25]}, {'base': [1, 2, 3, 4, 5], 'values': [-2, -1, 7, 8]}]

SPECS = [
    code_step('stp_70f3948e-7301-4e32-9e06-49251673f030', 'isna()로 측정하지 못한 시간을 표시하세요', '비어 있는 값과 실제 값 0을 구별해요.',
              'df["minutes"] == 0은 실제 0분을 고른다. isna()로 고쳐 비어 있는 시간만 True로 확인한다. 채점은 0과 빈 값이 섞인 다른 자료로 실행한다.',
              '측정하지 못한 시간만 찾으려 해요. 표에서 비어 있는 값은 None이나 NaN이고, `isna()`는 그런 값만 True로 표시해요. 0은 실제로 잰 시간이에요.',
              'missing 줄을 고쳐 0분이 아니라 측정하지 못한 시간을 True로 표시하세요. 채점은 다른 자료로도 실행해요.',
              ['코드 실행을 눌러 첫 배송이 True인지 확인하세요.', '`df["minutes"] == 0`을 `df["minutes"].isna()`로 고치세요.', '코드 실행을 눌러 두 번째 배송만 True인지 확인하세요.', SUBMIT],
              s1, s1_sol, n1, {n1.actions[-1]['text']: '실제 자료 처리의 위험을 정확히 말해요.'}, cases=OTHER,
              reject=[([['missing = df["minutes"].isna()\n', 'missing = df["minutes"] == 0\n']], 'Zero minutes'),
                      ([['missing = df["minutes"].isna()\n', 'missing = df["note"].isna()\n']], 'Another column'),
                      ([['print(missing.tolist())', 'print([False, True, False, False])']], 'Typing the list')],
              accept=[([['missing = df["minutes"].isna()\n', 'missing = ~df["minutes"].notna()\n']], 'Not notna')]),
    code_step('stp_4ff1e472-cd71-4821-9033-6e07a78d3fb0', 'count()로 지역별 측정 건수를 세세요', '행 수와 값이 있는 건수를 구별해요.',
              'groupby("region").size()는 빈 시간도 센 행 수다. ["minutes"].count()로 고쳐 부산 1건을 확인한다. 한 건의 시간이 비어 있을 뿐 행은 그대로다. 채점은 다른 자료로 실행한다.',
              '부산 배송은 두 건인데 시간이 있는 기록은 몇 건일까요? `size()`는 묶음의 행 수이고, `["minutes"].count()`는 그 열에서 비어 있지 않은 값의 수예요.',
              '마지막 print 줄을 고쳐 행 수가 아니라 시간이 실제로 있는 건수를 지역별로 세세요. 채점은 다른 자료로도 실행해요.',
              ['코드 실행을 눌러 지역별 행 수를 확인하세요.', '`df.groupby("region").size()`를 `df.groupby("region")["minutes"].count()`로 고치세요.', '코드 실행을 눌러 부산의 측정 건수를 확인하세요.', SUBMIT],
              s2, s2_sol, n2, {n2.actions[-1]['text']: W}, cases=OTHER,
              reject=[([['df.groupby("region")["minutes"].count()', 'df.groupby("region").size()']], 'Rows including empty times'),
                      ([['df.groupby("region")["minutes"].count()', 'df[df["minutes"] != 0].groupby("region").size()']], 'Dropping zero minutes instead of empty ones'),
                      ([['print(df.groupby("region")["minutes"].count().to_dict())', "print({'부산': 1, '서울': 2})"]], 'Typing the dict')],
              accept=[([['print(df.groupby("region")["minutes"].count().to_dict())', 'print(df["minutes"].notna().groupby(df["region"]).sum().to_dict())']], 'Summing notna by region')]),
    code_step('stp_8535b868-816a-4180-9e73-eb7d3cf160ff', 'duplicated()로 모든 항목이 같은 행을 세세요', '중복을 어떤 열로 판단할지 정해 세어요.',
              '주문 103 두 기록의 시간이 30과 42다. subset=["order_id"]는 1이고, subset을 지운 duplicated()는 0이다. 채점은 완전히 같은 행이 있는 다른 자료로도 실행한다.',
              '주문 103이 두 번 기록됐는데 마지막 기록의 시간만 42예요. `duplicated()`는 앞에 같은 행이 있으면 True로 세고, `subset`을 주면 그 열만 비교해요.',
              'same_rows 줄을 고쳐 주문 번호만이 아니라 모든 항목이 같은 행을 세세요. 채점은 다른 자료로도 실행해요.',
              ['코드 실행을 눌러 두 줄이 같은지 확인하세요.', '`df.duplicated(subset=["order_id"])`에서 subset을 지워 `df.duplicated()`로 고치세요.', '코드 실행을 눌러 두 수를 비교하세요.', SUBMIT],
              s6, s6_sol, n6, {n6.actions[-1]['text']: '실제 중복 판단 기준을 정확히 말해요.'},
              cases=[{'data': {'order_id': [7, 7, 8, 9, 9], 'minutes': [5, 5, 6, 9, 10], 'region': ['서울', '서울', '부산', '부산', '부산'], 'note': ['ok', 'ok', 'ok', 'ok', 'ok']}},
                     {'data': {'order_id': [1, 2, 1, 2], 'minutes': [3, 4, 3, 4], 'region': ['서울', '부산', '서울', '부산'], 'note': ['ok', 'ok', 'ok', 'ok']}}],
              reject=[([['same_rows = df.duplicated().sum()', 'same_rows = df.duplicated(subset=["order_id"]).sum()']], 'Order number only'),
                      ([['same_rows = df.duplicated().sum()', 'same_rows = 0']], 'Typing the count')],
              accept=[([['same_rows = df.duplicated().sum()', 'same_rows = len(df) - len(df.drop_duplicates())']], 'Rows removed by drop_duplicates')]),
    code_step('stp_608a399d-d732-487f-afcb-3e97586839f3', '< 와 >로 범위 끝 값은 후보에서 빼세요', 'IQR 검토 범위의 끝 값을 범위 안으로 다뤄요.',
              '<=·>= 비교는 끝 값 6과 22도 후보로 표시한다. <·>로 고쳐 5와 23만 후보임을 확인한다. 채점은 다른 기준 자료와 끝 값이 들어간 값으로 실행한다.',
              '이번 검토 범위는 기준 자료의 사분위수로 정한 lower부터 upper까지예요. 범위의 끝 값은 범위 안이고, 그 바깥만 검토 후보예요.',
              'flag 줄의 비교 기호를 고쳐 범위 끝 값은 후보에서 빼세요. 채점은 다른 기준 자료로도 실행해요.',
              ['코드 실행을 눌러 네 값이 모두 True인지 확인하세요.', '`<=`를 `<`로, `>=`를 `>`로 고치세요.', '코드 실행을 눌러 끝 값 6과 22가 False인지 확인하세요.', SUBMIT],
              s8, s8_sol, n8, {n8.actions[-1]['text']: '수업의 뒤 스텝(실제 이상값 검토)과 맞는 경고예요.'}, cases=IQR_CASES,
              reject=[([['(minutes < lower) | (minutes > upper)', '(minutes <= lower) | (minutes >= upper)']], 'Boundaries included'),
                      ([['(minutes < lower) | (minutes > upper)', '(minutes < 6) | (minutes > 22)']], 'Typing this data\'s bounds'),
                      ([['print(flag.tolist())', 'print([True, False, False, True])']], 'Typing the list')],
              accept=[([['flag = (minutes < lower) | (minutes > upper)', 'flag = ~minutes.between(lower, upper)']], 'Not between (inclusive)')]),
]
