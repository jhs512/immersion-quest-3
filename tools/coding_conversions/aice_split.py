"""aice-split: 9 answer-picking steps -> coding steps (2026-10-29).

Each step edits one argument or line around train_test_split and prints the real pairs, sizes or
labels. Prepared cases rerun with other deliveries (other lengths, orders and labels), so typed results,
positional picks and the starter's split fail. The stratify step that cannot work with a one-member
class becomes a guard the learner writes, graded on data where stratifying is and is not possible."""
from _kit import Script, code_step

OPENING = ['이 수업에서는 훈련·검증·테스트의 역할을 직접 코드로 나눠요. 입력과 정답의 짝을 지키는 게 목표예요.',
           '배송 자료를 여러 조건으로 나눠요. 크기·재현성·범주 비율·시간순서를 실행 결과로 비교해요.']
PRD_SCOPE = ['세 챕터·세 단원·열한 스텝으로 같은 배송 관측을 나눠요.',
             '짝 찾기·shuffle·비율의 올림·시드·함께 나누기·층화·층화 가능 확인·정렬 뒤 분리·검증 점수로 고르기를 한 곳씩 직접 고쳐 써요.']
PRD_GRADING = ['직접 고친 코드를 실제 파이썬·scikit-learn으로 실행해 판정해요. 실행·해설만으로 성공시키지 않아요.',
               '임의정답·다른자료길이·테스트개수에서짝과길이를검사해요. 준비 자료를 바꿔 다시 실행해 기준 풀이와 비교하고, 결과를 글자로 적은 답·위치로 짝지은 답·따로 섞은 답은 거절해요.',
               '층화 실패는 실패로 설명하며 통과한 실행처럼 다루지 않아요. 층화할 수 없는 자료를 확인하는 조건을 직접 쓰고, 층화할 수 있는 자료와 없는 자료 모두로 검사해요.',
               '마지막 도전(stp_4664135d-7073-47a2-9c52-b0081fafd1f9): 실제 Python 실행과 다른 준비 자료의 결과를 검사해요. 시작 코드는 실패하고 동등한 풀이도 통과해야 해요.']
PRD_NARRATION = ['분리 한 조건을 고치고 같은 행 대응과 개수를 실제 출력으로 읽어요.',
                 '개수/비율·시드/누수·층화최소표본·순서/시간정렬·반환순서·테스트로 조정을 조심할 지점으로 짚어요.']

SUBMIT = '수정한 코드를 제출하세요.'
W = '실제 scikit-learn 동작을 정확히 말해요.'
TTS = 'from sklearn.model_selection import train_test_split\n\n'
PAIRS = '# 확인용 출력: 같은 자리의 입력과 정답을 (입력, 정답) 쌍으로 묶어 보여 줘요.\n'
XY = '# 각 위치의 입력과 정답은 같은 배송을 나타내요.\nX = [1, 2, 3, 4, 5, 6]\ny = [10, 20, 30, 40, 50, 60]\n'
XY_CASES = [{'X': [7, 3, 9, 1, 5, 2, 8], 'y': [70, 30, 90, 10, 50, 20, 80]}, {'X': [4, 6, 5, 2], 'y': [40, 60, 50, 20]}]

s1 = (TTS + XY.replace('X = [1, 2, 3, 4, 5, 6]\ny = [10, 20, 30, 40, 50, 60]', 'X = [3, 5, 1, 6, 2, 4]\ny = [30, 50, 10, 60, 20, 40]')
      + '# 이 줄을 고쳐 입력 5가 있는 자리의 정답을 꺼내세요.\nanswer = y[5]\nprint(answer)\n')
s1_sol = s1.replace('answer = y[5]\n', '# 값 5의 자리를 X.index로 찾고 y의 같은 자리를 읽어요.\nanswer = y[X.index(5)]\n')
n1 = (Script(s1)
      .say('같은 위치의 입력과 정답이 한 배송이에요. 입력 5가 있는 자리를 찾아 그 자리의 정답을 꺼내야 해요.', 'text:answer 줄을 고쳐 입력 5가 있는 자리의 정답을 꺼내세요.')
      .run('print(answer)')
      .say('40이에요. y[5]는 여섯째 자리, 입력 4의 정답이에요.', 'output')
      .patch('answer = y[5]\n', 'answer = y[X.index(5)]\n', 'X.index(5)로 5의 자리를 찾아 y의 같은 자리를 읽어요.')
      .run('print(answer)')
      .say('50이에요. 입력 5는 둘째 자리이고 같은 자리의 정답이 50이에요.', 'output')
      .say('조심하세요. 값 5와 자리 5는 달라요. 자리는 0부터 세요.', 'code:X.index(5)'))

s2 = (TTS + XY + '# 이 줄의 옵션을 고쳐 섞지 말고 마지막 두 배송을 평가용으로 남기세요.\n'
      'X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=2, random_state=1)\n'
      + PAIRS + 'print(list(zip(X_train, y_train)))\n' + PAIRS + 'print(list(zip(X_test, y_test)))\n')
s2_sol = s2.replace('test_size=2, random_state=1)', 'test_size=2, shuffle=False)').replace('# 이 줄의 옵션을 고쳐 섞지 말고 마지막 두 배송을 평가용으로 남기세요.\n',
                                                                                    '# 이 줄의 옵션을 고쳐 섞지 말고 마지막 두 배송을 평가용으로 남기세요.\n# shuffle=False면 섞지 않고 뒤의 두 관측을 테스트로 남겨요. X와 y를 함께 넣어 짝이 유지돼요.\n')
n2 = (Script(s2)
      .say('마지막 두 배송을 평가용으로 남기려 해요. 섞는 옵션을 고쳐야 해요.', 'text:train_test_split 줄의 옵션을 고쳐 섞지 말고 마지막 두 배송을 평가용으로 남기세요.')
      .run('print(list(zip(X_train', 'print(list(zip(X_test')
      .say('테스트가 (3, 30)과 (2, 20)이에요. 섞어서 마지막 두 배송이 아니에요.', 'output')
      .patch('test_size=2, random_state=1)', 'test_size=2, shuffle=False)', 'random_state=1을 shuffle=False로 바꿔요.')
      .run('print(list(zip(X_train', 'print(list(zip(X_test')
      .say('테스트가 (5, 50)과 (6, 60)이에요. 섞어도 안 섞어도 X와 y를 함께 넣어 짝은 그대로예요.', 'output')
      .say('조심하세요. 반환값은 X_train, X_test, y_train, y_test 순서예요. 이름의 자리를 바꾸면 짝이 엉켜요.', 'code:shuffle=False'))

s3 = ('import math\n' + TTS + '# 각 위치의 입력과 정답은 같은 배송을 나타내요.\nX = [1, 2, 3, 4, 5, 6, 7]\n'
      '# 실수 test_size는 비율이에요.\na, b = train_test_split(X, test_size=0.25, shuffle=False)\nprint(len(a), len(b))\n'
      '# 이 줄을 고쳐 테스트 개수를 비율로 직접 계산하세요. 소수는 올려요.\nexpected = int(len(X) * 0.25)\nprint(expected)\n')
s3_sol = s3.replace('expected = int(len(X) * 0.25)\n', '# 테스트 개수는 전체 × 비율을 올린 값이에요. int는 버려서 1이 돼요.\nexpected = math.ceil(len(X) * 0.25)\n')
n3 = (Script(s3)
      .say('일곱 행의 25%를 테스트로 남겨요. 실제 나뉜 개수와 같도록 테스트 개수 계산을 고쳐야 해요.', 'text:expected 줄을 고쳐 테스트 개수를 비율로 직접 계산하세요.')
      .run('print(len(a)', 'print(expected)')
      .say('5 2와 1이에요. 실제 테스트는 2개인데 int가 1.75를 1로 버렸어요.', 'output')
      .patch('int(len(X) * 0.25)', 'math.ceil(len(X) * 0.25)', 'int를 math.ceil로 바꿔요.')
      .run('print(len(a)', 'print(expected)')
      .say('2예요. 1.75를 올린 2가 실제 테스트 개수와 같아요.', 'output')
      .say('조심하세요. 실수는 비율, 정수는 개수예요. test_size=2는 두 행이에요.', 'code:math.ceil'))

s4 = (TTS + XY + '# 이 두 줄의 시드를 맞춰 같은 조건으로 두 번 나누세요.\na_train, a_test = train_test_split(X, test_size=2, random_state=42)\n'
      'b_train, b_test = train_test_split(X, test_size=2, random_state=7)\nprint(a_test == b_test)\nprint(a_test, b_test)\n')
s4_sol = s4.replace('random_state=7)', 'random_state=42)').replace('# 이 두 줄의 시드를 맞춰 같은 조건으로 두 번 나누세요.\n',
                                                              '# 이 두 줄의 시드를 맞춰 같은 조건으로 두 번 나누세요.\n# 같은 자료·같은 random_state·같은 조건이면 같은 분할이 다시 나와요.\n')
n4 = (Script(s4)
      .say('같은 분할을 다시 만들려 해요. 두 호출의 시드를 같게 고쳐야 해요.', 'text:두 줄의 시드를 맞춰 같은 조건으로 두 번 나누세요.')
      .run('print(a_test == b_test)', 'print(a_test, b_test)')
      .say('False예요. 시드 42와 7은 다르게 섞어요.', 'output')
      .patch('random_state=7)', 'random_state=42)', '둘째 줄의 random_state를 42로 바꿔요.')
      .run('print(a_test == b_test)', 'print(a_test, b_test)')
      .say('True이고 두 테스트가 [1, 2]로 같아요. 같은 호출 조건을 재현했어요.', 'output')
      .say('조심하세요. 자료의 순서나 test_size가 바뀌면 같은 시드라도 다른 분할이에요.', 'code:random_state=42)#2'))

CHECK = '# 확인용 출력: 테스트의 모든 쌍이 원래 짝(정답 = 입력 × 10)이면 True예요. 이 줄의 문법은 몰라도 돼요.\nprint(all(target == distance * 10 for distance, target in zip(X_test, y_test)))\n'
s5 = (TTS + XY + '# 이 두 줄을 고쳐 X와 y를 한 번에 함께 나누세요.\nX_train, X_test = train_test_split(X, test_size=2, random_state=42)\n'
      'y_train, y_test = train_test_split(y, test_size=2, random_state=7)\n' + CHECK + 'print(len(X_test), len(y_test))\n')
s5_sol = s5.replace('X_train, X_test = train_test_split(X, test_size=2, random_state=42)\ny_train, y_test = train_test_split(y, test_size=2, random_state=7)\n',
                    '# 한 호출에 X와 y를 함께 넣으면 같은 섞기로 나눠 짝이 유지돼요.\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=2, random_state=42)\n')
n5 = (Script(s5)
      .say('X와 y를 서로 다른 시드로 따로 나눴어요. 한 호출로 함께 나누도록 두 줄을 고쳐야 해요.', 'text:두 줄을 고쳐 X와 y를 한 번에 함께 나누세요.')
      .run('print(all(', 'print(len(X_test)')
      .say('False와 2 2예요. 길이는 같지만 테스트의 입력과 정답이 다른 배송끼리 짝지어졌어요.', 'output')
      .patch('X_train, X_test = train_test_split(X, test_size=2, random_state=42)\ny_train, y_test = train_test_split(y, test_size=2, random_state=7)\n',
             'X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=2, random_state=42)\n', '두 줄을 X와 y를 함께 넣는 한 줄로 바꿔요.')
      .run('print(all(', 'print(len(X_test)')
      .say('True와 2 2예요. 같은 섞기로 나눠 모든 쌍이 원래 짝이에요.', 'output')
      .say('조심하세요. 길이가 같다고 같은 관측끼리인 건 아니에요. 짝을 확인해요.', 'code:train_test_split(X, y,'))

STRAT = TTS + '# 두 분류의 개수는 여섯 개와 두 개예요.\ny = [0, 0, 0, 0, 0, 0, 1, 1]\nX = list(range(len(y)))\n'
s6 = (STRAT + '# 이 줄에 옵션을 더해 양쪽의 분류 비율을 원래 비율에 가깝게 나누세요.\na, b, ya, yb = train_test_split(X, y, test_size=0.5, random_state=25)\n'
      'print(ya.count(0), ya.count(1))\nprint(yb.count(0), yb.count(1))\n')
s6_sol = s6.replace('test_size=0.5, random_state=25)', 'test_size=0.5, random_state=25, stratify=y)').replace(
    '# 이 줄에 옵션을 더해 양쪽의 분류 비율을 원래 비율에 가깝게 나누세요.\n', '# 이 줄에 옵션을 더해 양쪽의 분류 비율을 원래 비율에 가깝게 나누세요.\n# stratify=y는 분류 정답의 비율을 훈련과 테스트에 비슷하게 나눠요.\n')
n6 = (Script(s6)
      .say('분류 1은 두 개뿐이에요. 양쪽에 비율이 비슷하게 가도록 옵션을 더해야 해요.', 'text:train_test_split 줄에 옵션을 더해 양쪽의 분류 비율을 원래 비율에 가깝게 나누세요.')
      .run('print(ya.count', 'print(yb.count')
      .say('훈련 2 2, 테스트 4 0이에요. 분류 1 두 개가 모두 훈련으로 가서 테스트에는 하나도 없어요.', 'output')
      .patch('random_state=25)', 'random_state=25, stratify=y)', '끝에 stratify=y를 더해요.')
      .run('print(ya.count', 'print(yb.count')
      .say('양쪽 모두 3 1이에요. 0과 1의 비율 6:2를 절반씩 나눴어요.', 'output')
      .say('조심하세요. 층화는 개수를 같게 만들지 않아요. 원래 비율을 유지해요.', 'code:stratify=y'))

s7 = (TTS + '# 한 분류에는 관측이 하나뿐일 수 있어요.\ny = [0, 0, 0, 0, 0, 1]\nX = list(range(len(y)))\n'
      '# 이 줄을 고쳐 모든 분류에 관측이 둘 이상일 때만 y로 층화하고, 아니면 None으로 두세요.\nuse = y\n'
      'a, b, ya, yb = train_test_split(X, y, test_size=2, random_state=42, stratify=use)\nprint(use is None)\nprint(yb.count(0), yb.count(1))\n')
s7_sol = s7.replace('use = y\n', '# 층화하려면 각 분류에 관측이 둘 이상 있어야 해요. 가장 적은 분류의 개수를 확인해요.\nuse = y if min(y.count(label) for label in set(y)) >= 2 else None\n')
n7 = (Script(s7)
      .say('한 분류의 관측이 하나뿐이에요. 층화할 수 있는지 확인하는 조건으로 use 줄을 고쳐야 해요.', 'text:use 줄을 고쳐 모든 분류에 관측이 둘 이상일 때만 y로 층화하고, 아니면 None으로 두세요.')
      .run('print(use is None)', 'print(yb.count', error='ValueError')
      .say('ValueError예요. 관측이 하나뿐인 분류는 양쪽에 나눌 수 없어요.', 'output')
      .patch('use = y\n', 'use = y if min(y.count(label) for label in set(y)) >= 2 else None\n', '가장 적은 분류가 둘 이상일 때만 y를 써요.')
      .run('print(use is None)', 'print(yb.count')
      .say('True와 2 0이에요. 이번 자료는 층화하지 않고 나눠 분류 1이 훈련에만 있어요.', 'output')
      .say('조심하세요. 층화 없이 나누면 하나뿐인 분류가 한쪽에만 있어요. 결과의 분류 개수를 확인해요.', 'code:min(y.count(label)'))

s8 = (TTS + '# 숫자는 같은 달의 날짜예요. 아직 정렬하지 않았어요.\ndates = [3, 1, 4, 2]\n# 이 줄을 고쳐 날짜를 작은 순서로 정렬한 뒤 나누세요.\nordered = dates\n'
      'train, test = train_test_split(ordered, test_size=2, shuffle=False)\nprint(train, test)\nprint(min(test) > max(train))\n')
s8_sol = s8.replace('ordered = dates\n', '# shuffle=False는 받은 순서를 지킬 뿐이에요. 시간순서는 sorted로 먼저 만들어요.\nordered = sorted(dates)\n')
n8 = (Script(s8)
      .say('섞지 않아도 날짜가 정렬되지는 않아요. 날짜를 먼저 정렬하도록 ordered 줄을 고쳐야 해요.', 'text:ordered 줄을 고쳐 날짜를 작은 순서로 정렬한 뒤 나누세요.')
      .run('print(train, test)', 'print(min(test)')
      .say('[3, 1] [4, 2]와 False예요. 입력 순서를 그대로 지켜 날짜 2가 평가 쪽에, 날짜 3이 훈련 쪽에 있어요.', 'output')
      .patch('ordered = dates\n', 'ordered = sorted(dates)\n', 'sorted(dates)로 정렬해요.')
      .run('print(train, test)', 'print(min(test)')
      .say('[1, 2] [3, 4]와 True예요. 앞 날짜로 훈련하고 뒤 날짜로 평가해요.', 'output')
      .say('조심하세요. shuffle=False는 입력 순서를 유지할 뿐이에요. 시간순서는 정렬해서 만들어요.', 'code:sorted(dates)'))

s9 = ('# 세 역할이 겹치지 않게 나눈 뒤 두 설정의 점수를 쟀어요.\nvalid_scores = {"small": 0.81, "large": 0.74}\ntest_scores = {"small": 0.70, "large": 0.79}\n'
      '# 이 줄을 고쳐 마지막 테스트가 아니라 검증 점수로 설정을 고르세요.\nbest = max(test_scores, key=test_scores.get)\nprint(best)\n'
      '# 고른 설정의 마지막 테스트 점수는 한 번만 보고해요.\nprint(test_scores[best])\n')
s9_sol = s9.replace('best = max(test_scores, key=test_scores.get)', '# 모델 선택은 검증 점수로 해요. 테스트는 고른 뒤 마지막에 한 번만 봐요.\nbest = max(valid_scores, key=valid_scores.get)')
n9 = (Script(s9)
      .say('검증과 마지막 테스트를 따로 남겼어요. 설정은 검증 점수로 고르도록 best 줄을 고쳐야 해요.', 'text:best 줄을 고쳐 마지막 테스트가 아니라 검증 점수로 설정을 고르세요.')
      .run('print(best)', 'print(test_scores[best])')
      .say('large와 0.79예요. 테스트 점수를 보고 골라 마지막 평가가 고르는 데 쓰였어요.', 'output')
      .patch('max(test_scores, key=test_scores.get)', 'max(valid_scores, key=valid_scores.get)', 'test_scores를 valid_scores로 바꿔요.')
      .run('print(best)', 'print(test_scores[best])')
      .say('small과 0.7이에요. 검증에서 고른 설정의 테스트 점수를 그대로 보고해요.', 'output')
      .say('조심하세요. 테스트 점수가 낮게 나왔다고 다시 고르면 테스트도 조정용이 돼요.', 'code:max(valid_scores'))

SPECS = [
    code_step('stp_fb7e690b-c690-48ff-856d-b6330792e82e', 'X.index로 입력 5와 짝인 정답을 꺼내세요', '입력과 정답이 같은 자리끼리 한 관측임을 써서 확인해요.',
              'y[5]는 여섯째 자리의 정답 40이다. y[X.index(5)]로 고쳐 입력 5의 짝 50을 확인한다. 채점은 순서가 다른 자료로 실행한다.',
              '같은 위치의 거리와 시간이 한 배송이에요. `X.index(값)`은 그 값이 있는 자리를 돌려주고, `y[자리]`는 같은 자리의 정답이에요.',
              'answer 줄을 고쳐 입력 5가 있는 자리의 정답을 꺼내세요. 채점은 순서가 다른 자료로도 실행해요.',
              ['코드 실행을 눌러 40이 나오는지 확인하세요.', '`y[5]`를 `y[X.index(5)]`로 고치세요.', '코드 실행을 눌러 50이 나오는지 확인하세요.', SUBMIT],
              s1, s1_sol, n1, {n1.actions[-1]['text']: '실제 파이썬 의미를 정확히 말해요.'},
              cases=[{'X': [5, 1, 2], 'y': [15, 11, 12]}, {'X': [9, 8, 7, 6, 5], 'y': [1, 2, 3, 4, 5]}],
              reject=[([['answer = y[X.index(5)]\n', 'answer = y[5]\n']], 'Position 5'), ([['answer = y[X.index(5)]\n', 'answer = 50\n']], 'Typing the answer')],
              accept=[([['answer = y[X.index(5)]\n', 'answer = dict(zip(X, y))[5]\n']], 'Pairing with zip')]),
    code_step('stp_1fb9323e-edb1-4dd7-a24b-42f57d45a0cc', 'shuffle=False로 마지막 두 배송을 평가용으로 남기세요', '입력과 정답을 함께 나눠 같은 관측끼리 테스트에 남겨요.',
              'random_state=1로 섞으면 테스트가 마지막 두 배송이 아니다. shuffle=False로 고쳐 (5, 50)과 (6, 60)을 확인한다. 채점은 다른 자료로 실행한다.',
              '마지막 두 배송을 평가용으로 남기려 해요. `train_test_split(X, y, ...)`에 X와 y를 함께 넣으면 같은 관측끼리 나뉘고, `shuffle=False`면 섞지 않고 뒤의 관측을 테스트로 남겨요.',
              'train_test_split 줄의 옵션을 고쳐 섞지 말고 마지막 두 배송을 평가용으로 남기세요. 채점은 다른 자료로도 실행해요.',
              ['코드 실행을 눌러 테스트 쌍을 확인하세요.', '`random_state=1`을 `shuffle=False`로 고치세요.', '코드 실행을 눌러 마지막 두 배송이 테스트인지 확인하세요.', SUBMIT],
              s2, s2_sol, n2, {n2.actions[-1]['text']: W, n2.actions[5]['text']: '실제 출력과 함께 나누기의 효과를 정확히 말해요.'}, cases=XY_CASES,
              reject=[([['test_size=2, shuffle=False)', 'test_size=2, random_state=1)']], 'Shuffled'),
                      ([['X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=2, shuffle=False)', 'X_train, X_test, y_train, y_test = X[:2], X[-2:], y[:2], y[-2:]']], 'Wrong training slice')],
              accept=[([['X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=2, shuffle=False)', 'X_train, X_test, y_train, y_test = X[:-2], X[-2:], y[:-2], y[-2:]']], 'Slicing the last two')]),
    code_step('stp_27e5b09a-d74d-4f79-8a2a-bccb60f48a53', 'math.ceil로 비율 테스트 개수를 계산하세요', '비율 test_size가 만드는 테스트 개수를 직접 계산해 맞춰요.',
              '일곱 행의 25%는 1.75이고 실제 테스트는 2개다. int는 1로 버린다. math.ceil로 고쳐 2를 확인한다. 채점은 길이가 다른 자료로 실행한다.',
              '일곱 행의 25%를 테스트로 남겨요. 실수 test_size는 비율이고, 테스트 개수는 전체 × 비율을 올린 값이에요. `math.ceil`은 소수를 올리고, `int`는 버려요.',
              'expected 줄을 고쳐 테스트 개수를 비율로 직접 계산하세요. 소수는 올려요. 채점은 길이가 다른 자료로도 실행해요.',
              ['코드 실행을 눌러 실제 개수와 expected를 비교하세요.', '`int(len(X) * 0.25)`를 `math.ceil(len(X) * 0.25)`로 고치세요.', '코드 실행을 눌러 두 값이 같은지 확인하세요.', SUBMIT],
              s3, s3_sol, n3, {n3.actions[-1]['text']: W}, cases=[{'X': list(range(10))}, {'X': list(range(8))}, {'X': list(range(5))}],
              reject=[([['expected = math.ceil(len(X) * 0.25)\n', 'expected = int(len(X) * 0.25)\n']], 'Rounding down'), ([['expected = math.ceil(len(X) * 0.25)\n', 'expected = 2\n']], 'Typing the count')],
              accept=[([['expected = math.ceil(len(X) * 0.25)\n', 'expected = len(b)\n']], 'Reading the real split')]),
    code_step('stp_8fcb0a62-f16c-4f70-b5a3-5bcd25ecf93e', 'random_state를 맞춰 같은 분할을 재현하세요', '같은 자료·시드·조건으로 분할을 재현해요.',
              '시드 42와 7은 다른 테스트를 만들어 False다. 둘째 시드를 42로 고쳐 True와 같은 테스트를 확인한다. 채점은 다른 자료로 실행한다.',
              '같은 자료·같은 random_state·같은 조건으로 나누면 같은 분할이 다시 나와요. 시드가 다르면 다르게 섞어요.',
              '두 줄의 시드를 맞춰 같은 조건으로 두 번 나누세요. 채점은 다른 자료로도 실행해요.',
              ['코드 실행을 눌러 False가 나오는지 확인하세요.', '둘째 줄의 `random_state=7`을 `random_state=42`로 고치세요.', '코드 실행을 눌러 True가 나오는지 확인하세요.', SUBMIT],
              s4, s4_sol, n4, {n4.actions[-1]['text']: W}, cases=XY_CASES,
              reject=[([['b_train, b_test = train_test_split(X, test_size=2, random_state=42)', 'b_train, b_test = train_test_split(X, test_size=3, random_state=42)']], 'Another test size'),
                      ([['b_train, b_test = train_test_split(X, test_size=2, random_state=42)', 'b_train, b_test = train_test_split(X, test_size=2, random_state=7)'], ['print(a_test == b_test)', 'print(True)']], 'Different seeds, typing True')],
              accept=[([['b_train, b_test = train_test_split(X, test_size=2, random_state=42)', 'seed = 42\nb_train, b_test = train_test_split(X, test_size=2, random_state=seed)']], 'Seed in a name')]),
    code_step('stp_da58a8f7-2c3a-4c2f-9fc0-084f4633e584', 'train_test_split(X, y)로 함께 나누세요', '입력과 정답을 한 호출로 함께 나눠 짝을 지켜요.',
              '서로 다른 시드로 따로 나누면 테스트 쌍의 짝이 어긋나 False다. 한 호출 train_test_split(X, y, ...)로 고쳐 True를 확인한다. 채점은 다른 자료로 실행한다.',
              'X와 y를 서로 다른 시드로 나눴어요. 길이가 같아도 섞기가 다르면 다른 배송끼리 짝지어져요. 한 호출에 X와 y를 함께 넣으면 같은 섞기로 나눠요.',
              '두 줄을 고쳐 X와 y를 한 번에 함께 나누세요. 반환값은 X_train, X_test, y_train, y_test 순서예요. 채점은 다른 자료로도 실행해요.',
              ['코드 실행을 눌러 False가 나오는지 확인하세요.', '두 줄을 `X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=2, random_state=42)` 한 줄로 고치세요.', '코드 실행을 눌러 True가 나오는지 확인하세요.', SUBMIT],
              s5, s5_sol, n5, {n5.actions[-1]['text']: W}, cases=XY_CASES,
              reject=[([['X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=2, random_state=42)\n', 'X_train, X_test = train_test_split(X, test_size=2, random_state=42)\ny_train, y_test = train_test_split(y, test_size=2, random_state=7)\n']], 'Separate shuffles'),
                      ([['X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=2, random_state=42)\n', 'X_train, y_train, X_test, y_test = train_test_split(X, y, test_size=2, random_state=42)\n']], 'Return values in the wrong places')],
              accept=[([['X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=2, random_state=42)\n', 'X_train, X_test = train_test_split(X, test_size=2, random_state=42)\ny_train, y_test = train_test_split(y, test_size=2, random_state=42)\n']], 'Same seed and size on equal lengths')]),
    code_step('stp_b6d77818-18de-447a-9b5b-583827b59bbe', 'stratify=y로 분류 비율을 유지하세요', '분류 정답의 비율을 훈련과 테스트에 비슷하게 나눠요.',
              '층화 없이 나누면 분류 1이 모두 훈련으로 가서 테스트가 4 0이다. stratify=y를 더해 양쪽 3 1을 확인한다. 채점은 다른 정답 목록으로 실행한다.',
              '두 분류의 개수는 여섯 개와 두 개예요. `stratify=y`는 분류 정답 y의 비율을 훈련과 테스트에 비슷하게 나눠요.',
              'train_test_split 줄에 옵션을 더해 양쪽의 분류 비율을 원래 비율에 가깝게 나누세요. 채점은 다른 정답 목록으로도 실행해요.',
              ['코드 실행을 눌러 양쪽의 분류 개수를 확인하세요.', '끝에 `stratify=y`를 더하세요.', '코드 실행을 눌러 양쪽이 3 1인지 확인하세요.', SUBMIT],
              s6, s6_sol, n6, {n6.actions[-1]['text']: W}, cases=[{'y': [1, 1, 1, 1, 0, 0, 0, 0, 0, 0]}, {'y': [0, 1, 0, 1, 0, 1, 0, 0]}],
              reject=[([['random_state=25, stratify=y)', 'random_state=25)']], 'No stratify'),
                      ([['print(ya.count(0), ya.count(1))', 'print(3, 1)']], 'Typing the counts')],
              accept=[([['random_state=25, stratify=y)', 'random_state=25, stratify=list(y))']], 'A copy of y')]),
    code_step('stp_fa54de92-25c4-46aa-b5a1-bcd7f4de3964', '층화할 수 있는지 확인하는 조건을 쓰세요', '한 분류의 관측이 하나뿐이면 층화할 수 없음을 확인해 처리해요.',
              'use = y로 층화하면 관측 하나뿐인 분류 때문에 ValueError다. 가장 적은 분류가 둘 이상일 때만 y, 아니면 None을 쓰도록 고친다. 채점은 층화할 수 있는 자료와 없는 자료로 실행한다.',
              '한 분류의 관측이 하나뿐이에요. 층화는 각 분류를 훈련과 테스트 양쪽에 나눠야 해서 분류마다 관측이 둘 이상 필요해요. `stratify=None`은 층화하지 않아요.',
              'use 줄을 고쳐 모든 분류에 관측이 둘 이상일 때만 y로 층화하고, 아니면 None으로 두세요. 채점은 층화할 수 있는 자료로도 실행해요.',
              ['코드 실행을 눌러 ValueError가 나오는지 확인하세요.', '`use = y`를 `use = y if min(y.count(label) for label in set(y)) >= 2 else None`으로 고치세요.', '코드 실행을 눌러 층화 여부와 테스트 개수를 확인하세요.', SUBMIT],
              s7, s7_sol, n7, {n7.actions[-1]['text']: W, n7.actions[2]['text']: '실제 scikit-learn 오류의 이유(최소 표본)를 정확히 말해요.'},
              cases=[{'y': [0, 0, 0, 1, 1, 1]}, {'y': [2, 0, 0, 1, 1, 0, 0]}],
              reject=[([['use = y if min(y.count(label) for label in set(y)) >= 2 else None\n', 'use = None\n']], 'Never stratifying'),
                      ([['use = y if min(y.count(label) for label in set(y)) >= 2 else None\n', 'use = y\n']], 'Always stratifying')],
              accept=[([['use = y if min(y.count(label) for label in set(y)) >= 2 else None\n', 'from collections import Counter\nuse = None if min(Counter(y).values()) < 2 else y\n']], 'Counter')]),
    code_step('stp_de190aec-5129-4fea-a670-f441d780e9f3', 'sorted로 날짜를 정렬한 뒤 나누세요', 'shuffle=False와 시간순서 정렬을 구별해요.',
              'shuffle=False는 입력 순서 [3, 1] [4, 2]를 지켜 False다. ordered = sorted(dates)로 고쳐 [1, 2] [3, 4]와 True를 확인한다. 채점은 다른 날짜로 실행한다.',
              '섞지 않으면 날짜가 정렬될까요? `shuffle=False`는 받은 순서를 지킬 뿐이에요. 앞 날짜로 훈련하고 뒤 날짜로 평가하려면 `sorted`로 먼저 정렬해요.',
              'ordered 줄을 고쳐 날짜를 작은 순서로 정렬한 뒤 나누세요. 채점은 다른 날짜로도 실행해요.',
              ['코드 실행을 눌러 False가 나오는지 확인하세요.', '`ordered = dates`를 `ordered = sorted(dates)`로 고치세요.', '코드 실행을 눌러 True가 나오는지 확인하세요.', SUBMIT],
              s8, s8_sol, n8, {n8.actions[-1]['text']: W, n8.actions[0]['text']: '실제 shuffle=False 의미를 정확히 말해요.'}, cases=[{'dates': [9, 2, 7, 5, 1, 8]}, {'dates': [20, 11, 30, 4]}],
              reject=[([['ordered = sorted(dates)\n', 'ordered = dates\n']], 'Input order'), ([['ordered = sorted(dates)\n', 'ordered = sorted(dates, reverse=True)\n']], 'Newest first')],
              accept=[([['ordered = sorted(dates)\n', 'ordered = list(dates)\nordered.sort()\n']], 'Sorting a copy')]),
    code_step('stp_3b5d9768-c2d2-45cd-b705-f2cb81ba6688', '검증 점수로 설정을 고르세요', '조정용 검증과 마지막 평가 테스트의 역할을 나눠요.',
              '테스트 점수로 고르면 large를 고르고 테스트가 조정에 쓰인다. max(valid_scores, key=valid_scores.get)로 고쳐 small과 그 테스트 점수 0.7을 확인한다. 채점은 다른 점수로 실행한다.',
              '검증과 마지막 테스트를 따로 남겼어요. 설정은 검증 점수로 고르고, 고른 설정의 테스트 점수는 마지막에 한 번만 보고해요. `max(사전, key=사전.get)`은 값이 가장 큰 키를 돌려줘요.',
              'best 줄을 고쳐 마지막 테스트가 아니라 검증 점수로 설정을 고르세요. 채점은 다른 점수로도 실행해요.',
              ['코드 실행을 눌러 고른 설정을 확인하세요.', '`max(test_scores, key=test_scores.get)`을 `max(valid_scores, key=valid_scores.get)`으로 고치세요.', '코드 실행을 눌러 검증으로 고른 설정과 테스트 점수를 확인하세요.', SUBMIT],
              s9, s9_sol, n9, {n9.actions[-1]['text']: '실제 평가 원칙을 정확히 말해요.'},
              cases=[{'valid_scores': {'a': 0.5, 'b': 0.9, 'c': 0.6}, 'test_scores': {'a': 0.95, 'b': 0.8, 'c': 0.7}}, {'valid_scores': {'x': 0.7, 'y': 0.6}, 'test_scores': {'x': 0.6, 'y': 0.9}}],
              reject=[([['best = max(valid_scores, key=valid_scores.get)', 'best = max(test_scores, key=test_scores.get)']], 'Tuning on the test'),
                      ([['best = max(valid_scores, key=valid_scores.get)', 'best = "small"']], 'Typing the name')],
              accept=[([['best = max(valid_scores, key=valid_scores.get)', 'best = sorted(valid_scores, key=lambda name: valid_scores[name])[-1]']], 'Sorting by validation score')]),
]
