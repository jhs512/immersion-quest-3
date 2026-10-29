"""aice-selection: 7 answer-picking steps -> coding steps (2026-10-29).

Step 9 (양의 상관만으로 무엇을 말할 수 있나) stays a choice: it asks for an interpretation (상관≠인과),
not for code. Every converted step varies the prepared data (other values, another row-name order) through
prepared cases, so a typed result or a pick by position where a name is asked fails."""
from _kit import Script, code_step

OPENING = ['이 수업에서는 질문에 맞는 행과 열을 직접 코드로 골라요. 선택·정렬·요약의 차이를 실행 결과로 비교해요.',
           '배송 표의 이름과 위치로 자료를 꺼내요. 평균·중앙값·그룹 평균을 직접 계산하고 상관의 의미도 짚어요.']
PRD_SCOPE = ['세 챕터·세 단원·열한 스텝으로 같은 배송 자료를 이어 가요.',
             '열 선택, loc 이름·iloc 위치, & 조건 조합, 내림차순 정렬, 중앙값, 그룹 평균을 한 줄씩 직접 고쳐 써요. 상관≠인과 해석은 선택 문항으로 남겨요.']
PRD_GRADING = ['직접 고친 코드를 실제 파이썬·판다스로 실행해 판정해요. 실행·해설만으로 성공시키지 않아요.',
               '준비 자료(값·행 이름 순서)를 바꾼 사례로 다시 실행해 기준 풀이의 실제 결과와 비교해요. 결과를 글자로 적은 답, 이름 대신 위치로 고른 답, 조건 하나를 뺀 답은 거절해요.',
               '상관과 인과를 구별하는 스텝은 해석 문항이라 선택 답으로 판정해요.',
               '마지막 도전(stp_5f220155-e726-403c-bb0c-82bc73056881): 실제 파이썬 출력과 다른 자료·기준 세 가지로 채점해요. > 경계, 지역 조건 누락, 오름차순, 전체 표 요약은 실패해요.']
PRD_NARRATION = ['선택 기준이나 옵션 한 곳씩 고친 뒤 실행하고 결과를 읽어요.',
                 '학생 답안은 보관하고 정확한 코드 줄·버튼·결과를 짚어요.',
                 '이름/위치·짝수 개 중앙값·원본 유지·인과 오해를 조심할 지점으로 다뤄요.']

HEAD = ('# 표를 다룰 판다스를 불러와요.\nimport pandas as pd\n'
        "# 같은 네 배송의 시간·지역·거리예요.\ndata = {'minutes': [12, 18, 30, 42], 'region': ['서울', '부산', '서울', '부산'], 'distance': [1, 2, 3, 4]}\n"
        '# 각 행에는 주문 번호를 이름으로 붙여요.\norders = [101, 102, 103, 104]\ndf = pd.DataFrame(data, index=orders)\n')
LATE = HEAD.replace('[12, 18, 30, 42]', '[12, 18, 30, 102]').replace('# 같은 네 배송의 시간·지역·거리예요.', '# 부산의 마지막 배송이 102분으로 늦어졌어요.')
# Other prepared data: other values, the row names in another order, an odd number of rows.
OTHER = [{'data': {'minutes': [25, 9, 41, 33, 16], 'region': ['부산', '서울', '서울', '부산', '서울'], 'distance': [3, 1, 5, 4, 2]},
          'orders': [105, 101, 103, 102, 104]},
         {'data': {'minutes': [50, 31, 7], 'region': ['서울', '서울', '부산'], 'distance': [6, 4, 1]}, 'orders': [103, 102, 101]}]
TODO_RUN = '코드 실행을 눌러 지금 출력을 확인하세요.'
SUBMIT = '수정한 코드를 제출하세요.'

s1 = HEAD + '# 이 줄을 고쳐 표 전체 대신 배송시간 목록만 출력하세요.\nprint(df)\n'
s1_sol = HEAD + '# 이 줄을 고쳐 표 전체 대신 배송시간 목록만 출력하세요.\n# 대괄호에 열 이름을 주면 그 열만 골라요. tolist()는 값 목록으로 보여 줘요.\nprint(df["minutes"].tolist())\n'
n1 = (Script(s1)
      .say('시간 열만 골라 보려 해요. 표 전체를 출력하는 줄을 고쳐야 해요.', 'text:print 줄을 고쳐 표 전체 대신 배송시간 목록만 출력하세요.')
      .run('print(df)')
      .say('왼쪽에 주문 번호 101부터 104, 위에 minutes·region·distance 세 열이 있는 표 전체예요.', 'output')
      .patch('print(df)\n', 'print(df["minutes"].tolist())\n', 'df["minutes"]로 시간 열을 고르고 tolist()로 목록을 만들어요.')
      .run('print(df[')
      .say('[12, 18, 30, 42]예요. 시간 열의 값 네 개만 나왔어요.', 'output')
      .say('조심하세요. df["region"]처럼 다른 열 이름을 쓰면 지역이 나와요. 질문에 맞는 열 이름을 골라요.', 'code:df["minutes"]'))

s2 = HEAD + '# 이 줄을 고쳐 주문 101의 시간을 출력하세요.\nprint(df.loc[0, "minutes"])\n'
s2_sol = s2.replace('print(df.loc[0, "minutes"])', '# loc는 행 이름과 열 이름으로 찾아요. 행 이름은 주문 번호예요.\nprint(df.loc[101, "minutes"])')
n2 = (Script(s2)
      .say('행 이름을 주문 번호로 붙였어요. loc의 행 자리에 주문 번호를 써야 해요.', 'text:print 줄을 고쳐 주문 101의 시간을 출력하세요.')
      .run('print(df.loc', error='KeyError')
      .say('KeyError: 0이에요. 행 이름에 0이 없어요. 이름은 101부터 104예요.', 'output')
      .patch('df.loc[0, "minutes"]', 'df.loc[101, "minutes"]', '행 자리에 주문 번호 101을 써요.')
      .run('print(df.loc')
      .say('12예요. 이름이 101인 행의 minutes 값이에요.', 'output')
      .say('조심하세요. 지금은 101이 첫 행이라 위치로 골라도 같아 보여요. 행 순서가 바뀌면 위치로 고른 답은 틀려요.', 'code:df.loc[101, "minutes"]'))

s3 = HEAD + '# 이 줄의 행 위치를 고쳐 첫 행의 첫 열을 출력하세요.\nprint(df.iloc[101, 0])\n'
s3_sol = s3.replace('print(df.iloc[101, 0])', '# iloc는 0부터 세는 위치로 찾아요. 첫 행은 위치 0이에요.\nprint(df.iloc[0, 0])')
n3 = (Script(s3)
      .say('이번에는 이름 대신 위치로 찾아요. iloc의 행 위치를 고쳐야 해요.', 'text:print 줄의 행 위치를 고쳐 첫 행의 첫 열을 출력하세요.')
      .run('print(df.iloc', error='IndexError')
      .say('IndexError예요. iloc의 101은 이름이 아니라 위치라서 네 행의 범위를 벗어나요.', 'output')
      .patch('df.iloc[101, 0]', 'df.iloc[0, 0]', '행 위치를 0으로 바꿔요.')
      .run('print(df.iloc')
      .say('12예요. 첫 행의 첫 열 minutes 값이에요.', 'output')
      .say('조심하세요. iloc는 행 이름과 상관없이 위치만 봐요. 위치는 0부터 세어요.', 'code:df.iloc[0, 0]'))

s5 = HEAD + '# 이 줄의 연결 기호를 고쳐 30분 이상이면서 서울인 배송만 고르세요.\nprint(df.loc[(df["minutes"] >= 30) | (df["region"] == "서울"), "minutes"].tolist())\n'
s5_sol = s5.replace('print(df.loc[(df["minutes"] >= 30) | (df["region"] == "서울"), "minutes"].tolist())',
                    '# 두 조건은 각각 괄호로 묶고 &로 연결해요. &는 두 조건을 모두 만족하는 행이에요.\nprint(df.loc[(df["minutes"] >= 30) & (df["region"] == "서울"), "minutes"].tolist())')
n5 = (Script(s5)
      .say('30분 이상 중 서울 배송만 보고 싶어요. 두 조건을 잇는 기호를 고쳐야 해요.', 'text:print 줄의 연결 기호를 고쳐 30분 이상이면서 서울인 배송만 고르세요.')
      .run('print(df.loc')
      .say('[12, 30, 42]예요. |는 둘 중 하나만 맞아도 골라서 서울의 12분과 부산의 42분도 들어왔어요.', 'output')
      .patch(') | (', ') & (', '|를 &로 바꿔요.')
      .run('print(df.loc')
      .say('[30]이에요. 30분 이상이면서 서울인 배송은 한 건이에요.', 'output')
      .say('조심하세요. 판다스 조건은 and가 아니라 &로 잇고, 각 조건을 괄호로 묶어요.', 'code:) & ('))

s6 = HEAD + '# 이 줄의 옵션을 고쳐 오래 걸린 배송부터 정렬하세요.\nprint(df.sort_values("minutes", ascending=True)["minutes"].tolist())\n# 원래 표의 순서도 확인해요.\nprint(df["minutes"].tolist())\n'
s6_sol = s6.replace('print(df.sort_values("minutes", ascending=True)["minutes"].tolist())',
                    '# ascending=False는 큰 값부터예요. sort_values는 정렬한 새 표를 돌려주고 원래 표는 그대로예요.\nprint(df.sort_values("minutes", ascending=False)["minutes"].tolist())')
n6 = (Script(s6)
      .say('오래 걸린 배송부터 보려 해요. 정렬 방향 옵션을 고쳐야 해요.', 'text:첫 print 줄의 옵션을 고쳐 오래 걸린 배송부터 정렬하세요.')
      .run('print(df.sort_values', 'print(df["minutes"]')
      .say('두 줄 모두 [12, 18, 30, 42]예요. ascending=True는 작은 값부터예요.', 'output')
      .patch('ascending=True', 'ascending=False', 'ascending을 False로 바꿔요.')
      .run('print(df.sort_values', 'print(df["minutes"]')
      .say('첫 줄은 [42, 30, 18, 12], 둘째 줄은 원래 순서 [12, 18, 30, 42]예요.', 'output')
      .say('조심하세요. sort_values는 원래 표를 바꾸지 않아요. 정렬 결과를 쓰려면 그 결과를 받아 써요.', 'code:ascending=False'))

s7 = LATE + '# 평균을 먼저 확인해요.\nprint(df["minutes"].mean())\n# 이 줄을 고쳐 평균 대신 가운데 값(중앙값)을 middle에 담으세요.\nmiddle = df["minutes"].mean()\nprint(middle)\n'
s7_sol = s7.replace('middle = df["minutes"].mean()', '# median은 크기순으로 놓았을 때 가운데 값이에요. 개수가 짝수면 가운데 두 값의 평균이에요.\nmiddle = df["minutes"].median()')
n7 = (Script(s7)
      .say('가장 늦은 배송 한 건만 더 늦어졌어요. 평균 대신 가운데 값을 middle에 담아 비교해야 해요.', 'text:middle 줄을 고쳐 평균 대신 가운데 값(중앙값)을 middle에 담으세요.')
      .run('print(df["minutes"].mean())', 'print(middle)')
      .say('두 줄 모두 40.5예요. 102분 한 건이 평균을 끌어올렸어요.', 'output')
      .patch('middle = df["minutes"].mean()', 'middle = df["minutes"].median()', 'mean을 median으로 바꿔요.')
      .run('print(df["minutes"].mean())', 'print(middle)')
      .say('40.5와 24.0이에요. 가운데 두 값 18과 30의 평균이라 늦어진 한 건에 흔들리지 않았어요.', 'output')
      .say('조심하세요. 개수가 짝수면 가운데 한 값만 고르면 안 돼요. 가운데 두 값의 평균이에요.', 'code:median()'))

s8 = LATE + '# 이 줄을 고쳐 전체 평균 대신 지역별 평균을 사전으로 출력하세요.\nprint(df["minutes"].mean())\n'
s8_sol = s8.replace('print(df["minutes"].mean())', '# groupby로 지역마다 묶은 뒤 각 묶음의 시간을 평균 내요.\nprint(df.groupby("region")["minutes"].mean().to_dict())')
n8 = (Script(s8)
      .say('지역별 평균을 나눠 보려 해요. 전체 평균 줄을 지역으로 묶어 평균 내도록 고쳐야 해요.', 'text:print 줄을 고쳐 전체 평균 대신 지역별 평균을 사전으로 출력하세요.')
      .run('print(df')
      .say('40.5예요. 지역을 가리지 않은 전체 평균이에요.', 'output')
      .patch('print(df["minutes"].mean())', 'print(df.groupby("region")["minutes"].mean().to_dict())', 'groupby("region")으로 묶고 minutes의 평균을 사전으로 바꿔요.')
      .run('print(df')
      .say("{'부산': 60.0, '서울': 21.0}이에요. 서울은 12와 30의 평균 그대로고, 102분이 된 배송은 부산 평균만 바꿨어요.", 'output')
      .say('조심하세요. groupby 뒤에 sum을 쓰면 평균이 아니라 합계예요. 요약 함수를 질문에 맞게 골라요.', 'code:.mean().to_dict()'))

W = '실제 판다스 동작을 정확히 말해요.'
SPECS = [
    code_step('stp_9419d079-d5ee-464a-8514-b461383aadee', 'df["minutes"]로 배송시간 목록을 꺼내세요', '열 이름으로 필요한 열 하나를 골라요.',
              'print(df)는 표 전체다. df["minutes"].tolist()로 고쳐 [12, 18, 30, 42]를 확인한다. 채점은 값과 행 이름이 다른 자료로 실행한다.',
              '시간 열만 골라 보려 해요. `df["열 이름"]`은 그 열 하나를 골라요. `.tolist()`는 고른 값을 목록으로 보여 줘요.',
              'print 줄을 고쳐 표 전체 대신 배송시간 목록만 출력하세요. 채점은 값이 다른 자료로도 실행해요.',
              [TODO_RUN, '`print(df)`를 `print(df["minutes"].tolist())`로 고치세요.', '코드 실행을 눌러 시간 네 개만 나오는지 확인하세요.', SUBMIT],
              s1, s1_sol, n1, {n1.actions[-1]['text']: W}, cases=OTHER,
              reject=[([['print(df["minutes"].tolist())', 'print([12, 18, 30, 42])']], 'Typing the list'),
                      ([['print(df["minutes"].tolist())', 'print(df["region"].tolist())']], 'Another column')],
              accept=[([['print(df["minutes"].tolist())', 'print(list(df.minutes))']], 'Attribute access and list')]),
    code_step('stp_10e6578a-7824-4147-a3c1-7436c6caebcf', 'df.loc[101, "minutes"]로 주문 101의 시간을 읽으세요', '행 이름과 열 이름으로 값 하나를 찾아요.',
              'df.loc[0, "minutes"]는 KeyError다. 행 이름 101로 고쳐 12를 확인한다. 채점은 행 이름 순서가 다른 자료로 실행해 위치로 고른 답을 거절한다.',
              '행 이름을 주문 번호로 붙였어요. `df.loc[행 이름, 열 이름]`은 이름으로 값을 찾아요.',
              'print 줄을 고쳐 주문 101의 시간을 출력하세요. 채점은 주문 순서가 다른 자료로도 실행해요.',
              ['코드 실행을 눌러 KeyError가 나오는지 확인하세요.', '`df.loc[0, "minutes"]`의 0을 `101`로 고치세요.', '코드 실행을 눌러 12가 나오는지 확인하세요.', SUBMIT],
              s2, s2_sol, n2, {n2.actions[-1]['text']: '실제 채점(행 순서를 바꾼 자료)과 맞는 경고예요.'}, cases=OTHER,
              reject=[([['print(df.loc[101, "minutes"])', 'print(df.iloc[0]["minutes"])']], 'First row by position'),
                      ([['print(df.loc[101, "minutes"])', 'print(12)']], 'Typing the value')],
              accept=[([['print(df.loc[101, "minutes"])', 'print(df.at[101, "minutes"])']], 'at with labels')]),
    code_step('stp_59a7388c-c92c-4572-895b-0c412f2aaa53', 'df.iloc[0, 0]으로 첫 행의 첫 열을 읽으세요', '0부터 세는 위치로 값 하나를 찾아요.',
              'df.iloc[101, 0]은 IndexError다. 위치 0으로 고쳐 12를 확인한다. 채점은 행 이름 순서가 다른 자료로 실행해 이름으로 고른 답을 거절한다.',
              '이번에는 이름 대신 위치로 찾아요. `df.iloc[행 위치, 열 위치]`는 0부터 세는 위치예요.',
              'print 줄의 행 위치를 고쳐 첫 행의 첫 열을 출력하세요. 채점은 주문 순서가 다른 자료로도 실행해요.',
              ['코드 실행을 눌러 IndexError가 나오는지 확인하세요.', '`df.iloc[101, 0]`의 101을 `0`으로 고치세요.', '코드 실행을 눌러 12가 나오는지 확인하세요.', SUBMIT],
              s3, s3_sol, n3, {n3.actions[-1]['text']: W}, cases=OTHER,
              reject=[([['print(df.iloc[0, 0])', 'print(df.loc[101, "minutes"])']], 'Row name 101 instead of the first position'),
                      ([['print(df.iloc[0, 0])', 'print(df.iloc[1, 0])']], 'Second position')],
              accept=[([['print(df.iloc[0, 0])', 'print(df.iat[0, 0])']], 'iat')]),
    code_step('stp_34063150-4732-45c4-8209-6ab8cbe91df5', '&로 두 조건을 모두 만족하는 배송을 고르세요', '두 조건을 &로 이어 모두 만족하는 행을 골라요.',
              '| 연결은 [12, 30, 42]다. &로 고쳐 [30]을 확인한다. 채점은 다른 자료로 실행해 조건 하나만 쓴 답을 거절한다.',
              '30분 이상 중 서울 배송만 보고 싶어요. 판다스 조건은 각각 괄호로 묶고 `&`(모두 만족) 또는 `|`(하나라도 만족)로 이어요.',
              'print 줄의 연결 기호를 고쳐 30분 이상이면서 서울인 배송만 고르세요. 채점은 다른 자료로도 실행해요.',
              ['코드 실행을 눌러 세 건이 나오는지 확인하세요.', '두 조건 사이의 `|`를 `&`로 고치세요.', '코드 실행을 눌러 [30]이 나오는지 확인하세요.', SUBMIT],
              s5, s5_sol, n5, {n5.actions[-1]['text']: W, n5.actions[2]['text']: '실제 출력(서울 12·30, 부산 42)과 | 의미를 정확히 말해요.'}, cases=OTHER,
              reject=[([[') & (', ') | (']], 'Either condition'),
                      ([['(df["minutes"] >= 30) & (df["region"] == "서울")', 'df["minutes"] >= 30']], 'Only the time condition'),
                      ([['print(df.loc[(df["minutes"] >= 30) & (df["region"] == "서울"), "minutes"].tolist())', 'print([30])']], 'Typing the list')],
              accept=[([['print(df.loc[(df["minutes"] >= 30) & (df["region"] == "서울"), "minutes"].tolist())',
                         'print(df.query(\'minutes >= 30 and region == "서울"\')["minutes"].tolist())']], 'query with and')]),
    code_step('stp_189893c9-eb2a-4aec-83c6-3bdcd96a0a0e', 'ascending=False로 오래 걸린 순서로 정렬하세요', '정렬 방향 옵션으로 큰 값부터 정렬해요.',
              'ascending=True는 [12, 18, 30, 42]다. False로 고쳐 [42, 30, 18, 12]와 그대로인 원래 순서를 확인한다. 채점은 다른 자료로 실행한다.',
              '오래 걸린 배송부터 보려 해요. `sort_values(열, ascending=...)`의 ascending이 True면 작은 값부터, False면 큰 값부터예요.',
              '첫 print 줄의 옵션을 고쳐 오래 걸린 배송부터 정렬하세요. 채점은 다른 자료로도 실행해요.',
              ['코드 실행을 눌러 두 줄이 같은지 확인하세요.', '`ascending=True`를 `ascending=False`로 고치세요.', '코드 실행을 눌러 정렬 결과와 원래 순서를 비교하세요.', SUBMIT],
              s6, s6_sol, n6, {n6.actions[-1]['text']: W}, cases=OTHER,
              reject=[([['print(df.sort_values("minutes", ascending=False)', 'print(df.sort_values("minutes", ascending=True)']], 'Ascending'),
                      ([['print(df.sort_values("minutes", ascending=False)["minutes"].tolist())', 'print([42, 30, 18, 12])']], 'Typing the list')],
              accept=[([['print(df.sort_values("minutes", ascending=False)["minutes"].tolist())', 'print(sorted(df["minutes"], reverse=True))']], 'sorted with reverse')]),
    code_step('stp_6684b395-b2a5-42e2-be66-6def5ef18576', 'median()으로 가운데 값을 middle에 담으세요', '튀는 값 하나에 평균과 중앙값이 다르게 움직이는 것을 비교해요.',
              '102분이 된 자료에서 평균과 middle이 모두 40.5다. median()으로 고쳐 24.0을 확인한다. 채점은 짝수·홀수 개 다른 자료로 실행한다.',
              '가장 늦은 배송 한 건만 102분으로 더 늦어졌어요. 중앙값은 시간을 크기순으로 놓았을 때 가운데 값이에요. 개수가 짝수면 가운데 두 값의 평균이에요.',
              'middle 줄을 고쳐 평균 대신 가운데 값(중앙값)을 middle에 담으세요. 채점은 개수가 다른 자료로도 실행해요.',
              ['코드 실행을 눌러 두 줄이 같은지 확인하세요.', '`df["minutes"].mean()`을 `df["minutes"].median()`으로 고치세요.', '코드 실행을 눌러 평균과 중앙값을 비교하세요.', SUBMIT],
              s7, s7_sol, n7, {n7.actions[-1]['text']: '실제 중앙값 정의를 정확히 말해요. 채점 사례에 짝수 개가 있어요.'}, cases=OTHER,
              reject=[([['middle = df["minutes"].median()', 'middle = sorted(df["minutes"])[len(df) // 2]']], 'Upper middle item only'),
                      ([['middle = df["minutes"].median()', 'middle = 24.0']], 'Typing the value')],
              accept=[([['middle = df["minutes"].median()', 'middle = df["minutes"].quantile(0.5)']], 'Half quantile')]),
    code_step('stp_fcd1377b-9ab4-437d-9c53-ab5d60bcc59b', 'groupby로 지역별 평균을 출력하세요', '지역으로 묶어 각 묶음을 따로 요약해요.',
              '부산 배송 하나가 102분인 자료에서 전체 평균은 40.5다. groupby("region")["minutes"].mean()으로 고쳐 부산 60.0·서울 21.0을 확인한다. 채점은 다른 자료로 실행한다.',
              '부산의 42분 배송이 102분으로 늦어졌어요. `df.groupby("region")`은 지역마다 행을 묶고, 뒤의 `["minutes"].mean()`은 묶음마다 시간 평균을 내요.',
              'print 줄을 고쳐 전체 평균 대신 지역별 평균을 사전으로 출력하세요. 채점은 다른 자료로도 실행해요.',
              [TODO_RUN, '`df["minutes"].mean()`을 `df.groupby("region")["minutes"].mean().to_dict()`로 고치세요.', '코드 실행을 눌러 어느 지역 평균이 바뀌었는지 확인하세요.', SUBMIT],
              s8, s8_sol, n8, {n8.actions[-1]['text']: W}, cases=OTHER,
              reject=[([['["minutes"].mean().to_dict()', '["minutes"].sum().to_dict()']], 'Sum instead of mean'),
                      ([['print(df.groupby("region")["minutes"].mean().to_dict())', "print({'부산': 60.0, '서울': 21.0})"]], 'Typing the dict')],
              accept=[([['print(df.groupby("region")["minutes"].mean().to_dict())', 'print(df.groupby("region").mean(numeric_only=True)["minutes"].to_dict())']], 'Mean of every numeric column')]),
]
