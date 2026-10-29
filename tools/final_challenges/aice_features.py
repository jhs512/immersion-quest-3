"""aice-features final challenge: convert planned dates keeping failures visible, then build inputs known at order time with region indicators."""
from _common import Script, todo, ids, next_revision

KEY = 'aice-features'
UNIT, STEP = ids(KEY)
DAY_TODO = 'df["weekday"] = 0  # 1) 계획일을 날짜로 바꿔 요일 번호를 넣으세요. 바꿀 수 없는 날짜는 -1이에요.'
X_TODO = 'X = df[["id", "distance", "weekday", "region", "minutes"]]  # 2) 접수할 때 아는 열만 남기세요.'
STARTER = f'''import pandas as pd

# 접수한 배송이에요. 계획일 하나는 날짜가 아닌 글자로 들어왔어요.
data = {{"id": [101, 102, 103, 104], "distance": [3, 1, 4, 2],
        "planned": ["2024-01-01", "2024-01-06", "soon", "2024-01-03"],
        "region": ["north", "south", "north", "west"], "minutes": [30, 12, 41, 25]}}
df = pd.DataFrame(data)
# 정답 y는 맞힐 배송 시간이에요.
y = df["minutes"]
{DAY_TODO}
{X_TODO}
# 문자 범주는 범주마다 표시 열로 바꿔요.
X = pd.get_dummies(X, dtype=int)
print(X.columns.tolist())
print(X.values.tolist())
# 날짜로 바꾸지 못한 배송 수예요.
print(int((df["weekday"] == -1).sum()))
'''
DAY_WRONG = '''parsed = pd.to_datetime(df["planned"], format="%Y-%m-%d", errors="coerce")
df["weekday"] = parsed.dt.dayofweek'''
DAY = '''# 형식에 맞지 않는 글자는 오류 대신 빈 날짜(NaT)로 남겨요.
parsed = pd.to_datetime(df["planned"], format="%Y-%m-%d", errors="coerce")
# 월요일이 0이에요. 빈 날짜는 -1로 표시해 정수 열로 만들어요.
df["weekday"] = parsed.dt.dayofweek.fillna(-1).astype("int64")'''
X = '''# 식별자 id와 정답 minutes는 입력에서 빼요.
X = df[["distance", "weekday", "region"]]'''
SOLUTION = STARTER.replace(DAY_TODO, DAY).replace(X_TODO, X)

s = Script(STARTER)
s.say('마지막 도전이에요. 계획일을 요일 번호로 바꾸되 실패를 숨기지 않고, 접수할 때 아는 열만 입력으로 만들어요.',
      'text:바꾸지 못한 날짜는 -1로 표시해요.')
s.run()
s.say('입력에 id와 정답 minutes가 들어 있어요. 요일은 모두 0이라 바꾸지 못한 날짜도 보이지 않아요.', 'output')
s.patch(DAY_TODO, DAY_WRONG, '먼저 errors="coerce"로 날짜를 바꾸고 요일을 꺼내 볼게요.')
s.run()
s.say('요일이 0.0, 5.0, nan, 2.0처럼 소수와 nan으로 나왔어요. 실패 건수도 0이라고 잘못 세요.', 'output')
s.patch(DAY_WRONG, DAY, '빈 날짜를 -1로 채우고 정수로 바꿔요.')
s.patch(X_TODO, X, '입력에서 id와 정답을 빼요.')
s.run()
s.say('입력은 거리, 요일, 지역 표시 열 셋이에요. soon인 103은 요일 -1로 남고 실패 건수는 1이에요.', 'output')
s.say('조심하세요. 정답 minutes를 입력에 남기면 모델이 답을 보고 맞히는 셈이라 평가 점수가 거짓으로 좋아져요.', 'code:X = df[["distance", "weekday", "region"]]')

GOAL = ('자, 마지막 도전이에요. 접수한 배송 표 df로 배송 시간을 예측할 입력 X를 만들어요.\n\n'
        '계획일 planned를 날짜로 바꿔 요일 번호(월요일 0) 열 weekday에 넣어요. 바꾸지 못한 날짜는 -1로 표시해요. '
        '입력에는 접수할 때 아는 거리, 요일, 지역만 남기고 식별자 id와 정답 minutes는 빼요. '
        '그러면 입력 열 이름, 입력 값, 날짜로 바꾸지 못한 건수가 출력돼요. 지금 자료이면 첫 줄이 '
        '`[\'distance\', \'weekday\', \'region_north\', \'region_south\', \'region_west\']`이고 마지막 줄이 `1`이에요. '
        '채점은 다른 배송 자료로도 실행해요.\n\n'
        + todo('코드 실행을 눌러 지금 입력 열을 확인하세요.',
               '계획일을 날짜로 바꿔 요일 번호를 넣고, 바꾸지 못한 날짜는 -1로 두세요.',
               '입력에 거리, 요일, 지역만 남기세요.',
               '다시 실행해 실패 건수와 입력 열을 확인한 뒤 제출하세요.'))

SPEC = dict(
    key=KEY, course='aice', revision=next_revision(KEY, 'aice-features-5'),
    reason='날짜 변환 실패를 숨기지 않고 표시하기, 자료형 맞추기, 범주 표시 열, 예측 시점에 아는 입력과 정답·식별자의 구별을 새 배송 표에서 함께 쓰는 마지막 도전이에요.',
    grading='실제 파이썬 출력과 다른 배송 자료 세 가지로 채점해요. 정답·식별자 포함, 실패를 nan으로 둔 소수 열, 실패 행 삭제는 실패해요.',
    unit=dict(id=UNIT, title='마지막 도전', objectives=['변환 실패를 표시하고 예측 시점의 입력 열만 만들어요.'],
              premise='계획일 하나가 날짜가 아닌 배송 표예요. 앞 스텝과 상관없이 바로 풀 수 있어요.'),
    step=dict(id=STEP, title='접수할 때 아는 입력 표를 만드세요',
              objectives=['날짜 실패를 -1로 표시하고 정답·식별자를 뺀 입력을 만들어요.'],
              core_flow='준비 코드는 요일을 0으로 두고 모든 열을 입력에 넣는다. 학생은 to_datetime(errors="coerce"), dayofweek.fillna(-1).astype("int64"), 입력 열 선택을 쓴다. '
                        '해설은 fillna 없는 nan 소수 열과 실패 건수 0의 실제 결과를 보여 준다. 채점: 실패 없는 자료, 실패 두 건, 다른 지역 이름.'),
    task=dict(id=STEP, title='접수할 때 아는 입력 표를 만드세요', language='python', goal=GOAL,
              starter_code=STARTER, solution=SOLUTION, required=True,
              tests=[dict(input='', expected="['distance', 'weekday', 'region_north', 'region_south', 'region_west']\n"
                                             "[[3, 0, 1, 0, 0], [1, 5, 0, 1, 0], [4, -1, 1, 0, 0], [2, 2, 0, 0, 1]]\n1")],
              narration=s.actions),
    prepared_cases=[dict(values=dict(data={'id': [1, 2], 'distance': [5, 6], 'planned': ['2024-01-02', '2024-01-07'],
                                           'region': ['east', 'east'], 'minutes': [9, 9]}),
                         expected="['distance', 'weekday', 'region_east']\n[[5, 1, 1], [6, 6, 1]]\n0"),
                    dict(values=dict(data={'id': [7, 8, 9], 'distance': [2, 2, 8], 'planned': ['later', '2024-01-04', '01/05/2024'],
                                           'region': ['south', 'north', 'south'], 'minutes': [20, 15, 70]}),
                         expected="['distance', 'weekday', 'region_north', 'region_south']\n[[2, -1, 0, 1], [2, 3, 1, 0], [8, -1, 0, 1]]\n2"),
                    dict(values=dict(data={'id': [3], 'distance': [7], 'planned': ['2024-01-05'], 'region': ['west'], 'minutes': [50]}),
                         expected="['distance', 'weekday', 'region_west']\n[[7, 4, 1]]\n0")],
    cases=dict(expected_outputs=[None, None, None],
               reject=[([['X = df[["distance", "weekday", "region"]]', 'X = df[["id", "distance", "weekday", "region"]]']], 'The identifier is not an input'),
                       ([['X = df[["distance", "weekday", "region"]]', 'X = df[["distance", "weekday", "region", "minutes"]]']], 'The answer is not an input'),
                       ([['.fillna(-1).astype("int64")', '']], 'Failed dates are marked -1'),
                       ([['df["weekday"] = parsed.dt.dayofweek.fillna(-1).astype("int64")',
                          'df["weekday"] = parsed.dt.dayofweek.fillna(-1).astype("int64")\ndf = df[df["weekday"] != -1]']], 'Failed rows stay in the table')],
               accept=[([['parsed.dt.dayofweek', 'parsed.dt.weekday']], 'weekday is the same Monday-zero number')]),
    review={'조심하세요. 정답 minutes를 입력에 남기면 모델이 답을 보고 맞히는 셈이라 평가 점수가 거짓으로 좋아져요.':
            '이 수업 8번의 입력 열 고르기를 이 도전에서 말해요. 채점의 정답 포함 오답 사례가 잡아요.'},
)
