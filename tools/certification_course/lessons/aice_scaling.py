"""aice-scaling: measure the scaling rule on the training part only, then only apply it (AICE Associate 13th lesson).

Every task reads a small original store table (seats, rent in thousand won, daily visitors, store
type) and splits it with train_test_split(test_size=0.25, random_state=42). Rent is about a hundred
times larger than seats, and one training store has a huge visitor count, so StandardScaler and
RobustScaler disagree. Base test stores lie outside the training range, so MinMaxScaler gives
values below 0 and above 1. Three changed tables make memorized output fail: a shorter one and a
longer one (another outlier, a fourth store type), and one that keeps every training row and makes
only the test rows huge, so any answer that fits on test or whole data changes its rule.
"""
from certification_course.kit import py_task
from principles_course.common import code, lesson

SOURCES = ['https://aice.study/info/aice/asso',
           'https://scikit-learn.org/stable/modules/preprocessing.html',
           'https://scikit-learn.org/stable/common_pitfalls.html']

PATH = 'data/stores.csv'

# Base: 12 stores. With random_state=42 rows 0, 9 and 10 become the test part.
# Row 4's 2400 visitors is the training outlier. Test rows 0 and 10 sit outside the training range.
BASE = code('''
    type,seats,rent,visitors
    street,14,1200,120
    mall,48,4200,260
    station,30,3100,320
    street,18,1500,110
    mall,56,4800,2400
    station,36,3500,290
    street,20,1300,95
    mall,42,3900,230
    station,28,2700,350
    street,26,2000,170
    mall,60,5300,310
    station,34,3300,300
''')

# Fewer rows: rows 1, 5 and 8 are the test part, the visitor outlier (1900) is in training.
SHORTER = code('''
    type,seats,rent,visitors
    station,32,2900,280
    street,12,1100,90
    mall,50,4600,330
    street,22,1600,1900
    station,38,3400,260
    mall,64,5600,410
    street,16,1400,150
    mall,46,4100,300
    station,30,2500,240
    street,24,1800,180
''')

# More rows and a fourth type (drive): rows 0, 9, 11 and 13 are the test part.
# One outlier (3100) is in training and another (1500) is in the test part.
LONGER = code('''
    type,seats,rent,visitors
    mall,58,5000,340
    street,20,1500,130
    station,32,3000,310
    mall,44,4000,270
    street,16,1200,100
    station,38,3600,3100
    mall,52,4700,350
    street,24,1900,160
    station,28,2600,290
    street,10,900,80
    mall,48,4300,320
    station,36,3300,1500
    street,22,1700,150
    mall,66,6000,380
    drive,30,2800,250
''')

# The base training rows unchanged; only the three test rows (0, 9, 10) become extreme.
# A correct rule stays exactly the same; a rule measured on test or whole data moves a lot.
TEST_SHIFT = code('''
    type,seats,rent,visitors
    street,8,600,40
    mall,48,4200,260
    station,30,3100,320
    street,18,1500,110
    mall,56,4800,2400
    station,36,3500,290
    street,20,1300,95
    mall,42,3900,230
    station,28,2700,350
    street,90,9800,1600
    mall,120,12000,900
    station,34,3300,300
''')

NUMERIC_X = '''# 입력 X는 좌석 수, 월세(천 원), 하루 방문자 수예요.
X = df[['seats', 'rent', 'visitors']]
'''

ENCODED_X = '''# 매장 유형(type)을 원핫 인코딩해요. 0과 1로 된 열이 생겨요.
X = pd.get_dummies(df, columns=['type'], dtype=int)
'''

SPLIT = '''# 훈련 75%, 테스트 25%로 나눠요. X만 넣으면 두 몫이 나와요.
X_train, X_test = train_test_split(X, test_size=0.25, random_state=42)'''


def header(tools, x, split):
    """Imports only what the solution uses, the store table, X and (usually) the split."""
    text = 'import pandas as pd\nfrom sklearn.model_selection import train_test_split\n'
    if tools:
        text += 'from sklearn.preprocessing import ' + tools + '\n'
    text += "\n# 직접 만든 매장 자료예요. 실제 매장 자료가 아니에요.\ndf = pd.read_csv('data/stores.csv')\n" + x
    return text + (SPLIT + '\n' if split else '')


def stores(id, title, principle, goal, body, before, after, *, tools='StandardScaler', x=NUMERIC_X, split=True,
           values=({}, {}, {}), compare, caution, hints, wrong=None, challenge=False):
    """One scaling experiment on the base table plus the shorter, longer and test-shifted tables."""
    scenarios = [dict(v, files={PATH: data}) for v, data in zip(values, (SHORTER, LONGER, TEST_SHIFT))]
    return py_task(id, title, principle, goal, header(tools, x, split) + code(body), before, after,
                   caution=caution, hints=hints, scenarios=scenarios, files={PATH: BASE}, compare=compare,
                   wrong=wrong, challenge=challenge)


# fit-after-split: the fit line moves below the split and measures the training part only.
FIT_FIRST = '# 전체 X로 기준을 재요. 아직 나누기 전이에요.\nscaler.fit(X)\n' + SPLIT
FIT_AFTER = SPLIT + '\n# 나눈 뒤 훈련 자료로만 기준을 재요.\nscaler.fit(X_train)'

# scale-numbers-only: the starter scales the one-hot columns too and refits on the test part.
WRAP_ALL = '''# 지금은 표 전체를 바꿔 새 표로 감싸요. 행 번호가 0부터 새로 붙어요.
X_train = pd.DataFrame(scaler.fit_transform(X_train), columns=X_train.columns)
X_test = pd.DataFrame(scaler.fit_transform(X_test), columns=X_test.columns)'''

NUMBERS_ONLY = '''# 숫자 열만 바꿔 같은 자리에 다시 담아요.
X_train[num_cols] = scaler.fit_transform(X_train[num_cols])
X_test[num_cols] = scaler.transform(X_test[num_cols])'''

# new-store: wrong column order and a fresh fit on the single new row.
NEW_START = '''new_store = pd.DataFrame({'rent': [rent], 'seats': [seats], 'visitors': [visitors]})
# 새 매장 값을 바꿔요.
new_s = RobustScaler().fit_transform(new_store)'''

NEW_DONE = '''new_store = pd.DataFrame({'seats': [seats], 'rent': [rent], 'visitors': [visitors]})
# 새 매장 값을 바꿔요.
new_s = scaler.transform(new_store)'''


def build():
    return lesson('aice-scaling', '훈련 자료로만 변환 기준 익히기',
        '단위가 다른 숫자 열의 크기를 맞춰요. 기준은 훈련 자료로만 재고, 테스트 자료는 바꾸기만 해요. '
        '필수 문제 7개와 선택 도전 2개예요.',
        SOURCES, [
        stores('unit-gap', '열마다 숫자 크기가 달라요',
            '좌석 수는 수십, 월세(천 원)는 수천이에요. 숫자가 큰 열은 모델 계산에서 더 크게 보일 수 있어요.\n'
            '그래서 크기를 맞춰요(스케일링). 표준편차(std)는 값이 평균에서 퍼진 폭이에요.\n'
            '평균을 빼고 표준편차로 나누면 단위가 사라져요. 이걸 표준화라고 해요.',
            '자, 먼저 실행해 보세요. 요약 표가 두 개 나와요.\n'
            '위 표는 X_train이에요. mean과 std 줄을 열끼리 견줘 보세요.\n'
            '아래 표는 평균을 뺀 result예요. mean은 0(-0.00도 0)인데 std는 그대로죠?\n'
            'result 줄을 `(X_train - X_train.mean()) / X_train.std()`로 바꾸세요.\n'
            '다시 실행해서 아래 표의 std를 세 열끼리 비교해요.',
            '''
            # 훈련 자료의 행 수예요.
            print(len(X_train))
            # 열마다 평균(mean)과 표준편차(std)를 봐요.
            print(X_train.describe().round(1))
            # 열마다 자기 평균을 빼요. 가운데가 0으로 와요.
            # 퍼진 폭까지 맞추려면 표준편차로도 나눠요.
            result = X_train - X_train.mean()
            # 바꾼 뒤의 요약을 소수 둘째 자리까지 봐요.
            print(result.describe().round(2))
            ''',
            'result = X_train - X_train.mean()', 'result = (X_train - X_train.mean()) / X_train.std()',
            tools='', compare=['result'],
            caution='괄호를 빼면 나눗셈을 먼저 해서 엉뚱한 값이 나와요.',
            hints=['줄 전체를 `result = (X_train - X_train.mean()) / X_train.std()`로 바꿔요. '
                   '괄호가 있어야 뺄셈을 먼저 해요.'],
            wrong=[('result = X_train - X_train.mean()', 'result = X_train - X_train.mean() / X_train.std()'),
                   # Whole X instead of the training part.
                   ('result = X_train - X_train.mean()', 'result = (X - X.mean()) / X.std()')]),
        stores('standard-scaler', 'StandardScaler로 표준화해요',
            '`StandardScaler`는 표준화 도구예요. 열마다 평균을 빼고 표준편차로 나눠요.\n'
            '`fit`은 기준(평균·표준편차)을 재고, `transform`은 그 기준으로 값을 바꿔요.\n'
            '`fit_transform`은 둘을 한 번에 해요. 결과는 열 이름이 없는 배열이에요.',
            '`mean(axis=0)`은 행 방향으로 모아 열마다 평균을 내요. 먼저 실행해서 원래 단위의 평균과 표준편차를 보세요.\n'
            'X_train_s 줄을 `X_train_s = scaler.fit_transform(X_train)`으로 바꾸세요.\n'
            '다시 실행하면 [ ] 안에 값만 나와요. 순서는 seats, rent, visitors예요.\n'
            '평균이 0, 표준편차가 1인지 봐요. -0.은 0과 같아요.',
            '''
            # 표준화 도구(StandardScaler)를 만들어요.
            scaler = StandardScaler()
            # 지금은 원래 값을 그대로 담았어요.
            X_train_s = X_train
            # 열마다 평균과 표준편차예요. 소수 둘째 자리까지 봐요.
            print(X_train_s.mean(axis=0).round(2))
            print(X_train_s.std(axis=0).round(2))
            ''',
            '# 지금은 원래 값을 그대로 담았어요.\nX_train_s = X_train\n',
            '# 훈련 자료로 기준을 재고(fit) 바로 바꿔요(transform).\nX_train_s = scaler.fit_transform(X_train)\n',
            compare=['X_train_s'],
            caution='`fit`만 쓰면 바뀐 값이 아니라 도구 자신이 돌아와요.',
            hints=['`X_train_s = scaler.fit_transform(X_train)`으로 바꿔요.'],
            wrong=[('X_train_s = X_train\n', 'X_train_s = scaler.fit(X_train)\n'),
                   ('X_train_s = X_train\n', 'X_train_s = scaler.fit_transform(X)\n')]),
        stores('transform-test', '테스트 자료는 transform만 해요',
            '테스트 자료는 학습에 안 쓰고 남겨 둔 모의고사예요.\n'
            '그래서 기준은 훈련 자료로만 재요(fit). 테스트는 그 기준으로 바꾸기만 해요(transform).\n'
            '잰 평균은 `mean_`, 표준편차는 `scale_`에 남아요.',
            '먼저 실행해서 두 mean_과 X_test_s를 봐 두세요. 두 mean_이 다르죠?\n'
            'X_test_s 줄의 `fit_transform`을 `transform`으로 바꾸세요.\n'
            '다시 실행해서 두 mean_이 같은지 봐요. 열 순서는 seats, rent, visitors예요.\n'
            'X_test_s도 봐 둔 값과 견줘요. 이제 훈련 평균에서 떨어진 정도로 바뀌었어요.',
            '''
            # 표준화 도구를 만들어요.
            scaler = StandardScaler()
            # 훈련 자료로 기준을 재고 바로 바꿔요.
            X_train_s = scaler.fit_transform(X_train)
            # 훈련 자료로 잰 평균이에요. 소수 둘째 자리까지 봐요.
            print(scaler.mean_.round(2))
            # 테스트 자료를 바꿔요.
            X_test_s = scaler.fit_transform(X_test)
            # 지금 scaler에 남은 기준 평균이에요.
            mean = scaler.mean_
            print(mean.round(2))
            # 바꾼 테스트 자료예요.
            print(X_test_s.round(2))
            ''',
            'X_test_s = scaler.fit_transform(X_test)', 'X_test_s = scaler.transform(X_test)',
            compare=['mean', 'X_test_s'],
            caution='테스트 자료로 다시 fit하면 기준이 테스트 평균으로 바뀌어요.',
            hints=['`X_test_s = scaler.transform(X_test)`로 바꿔요.'],
            wrong=[('X_test_s = scaler.fit_transform(X_test)', 'X_test_s = StandardScaler().fit_transform(X_test)')]),
        stores('fit-after-split', '나누기 전에 fit하면 새요',
            '나누기 전에 전체 X로 fit하면 테스트 값이 기준에 섞여요.\n'
            '테스트 정보가 학습 쪽으로 새는 거죠. 이걸 누수라고 해요.\n'
            '훈련 자료로만 fit하면 바꾼 훈련 자료의 열 평균은 딱 0이에요.',
            '먼저 실행해서 mean_과 열 평균을 보세요. 작아도 0이 아니죠? 기준에 테스트 값이 섞여서예요.\n'
            '`scaler.fit(X)` 줄과 바로 위 주석 줄을 지우세요.\n'
            'train_test_split 줄 아래에 `scaler.fit(X_train)`을 쓰세요.\n'
            '다시 실행해서 mean_과 열 평균을 비교해요.',
            '''
            # 표준화 도구를 만들어요.
            scaler = StandardScaler()
            ''' + FIT_FIRST.replace('\n', '\n            ') + '''
            # 두 자료를 같은 기준으로 바꿔요.
            X_train_s = scaler.transform(X_train)
            X_test_s = scaler.transform(X_test)
            # 기준으로 쓴 평균이에요.
            mean = scaler.mean_
            print(mean)
            # 바꾼 훈련 자료의 열 평균이에요.
            print(X_train_s.mean(axis=0).round(2))
            ''',
            FIT_FIRST, FIT_AFTER, split=False, compare=['mean', 'X_test_s'],
            caution='fit 줄만 옮기고 X를 그대로 두면 여전히 전체 기준이에요.',
            hints=['train_test_split 줄 바로 아래에 `scaler.fit(X_train)`을 두고, 위의 `scaler.fit(X)`는 지워요.'],
            wrong=[(FIT_FIRST, FIT_AFTER.replace('scaler.fit(X_train)', 'scaler.fit(X)')),
                   (FIT_FIRST, FIT_AFTER.replace('scaler.fit(X_train)', 'scaler.fit(X_test)'))]),
        stores('robust-scaler', '이상치에 덜 흔들리는 RobustScaler',
            '평균과 표준편차는 아주 큰 값 하나에 크게 끌려가요.\n'
            '`RobustScaler`는 중앙값을 빼고 IQR로 나눠요. IQR은 Q3(75% 값) - Q1(25% 값)이에요.\n'
            '이상치를 없애진 않아요. 대신 보통 값들의 기준이 덜 흔들려요.',
            '먼저 실행해서 두 결과를 보세요. 지금은 둘 다 StandardScaler라 같아요. 보통 값들이 좁은 폭에 몰렸죠?\n'
            'scale_은 describe의 std보다 조금 작아요. describe는 (개수 - 1)로 나누거든요.\n'
            '`scaler = StandardScaler()`를 `scaler = RobustScaler()`로 바꾸세요.\n'
            '다시 실행해서 scale_을 describe의 75% - 25%와 견줘요.\n'
            '아래 결과에서 보통 값들은 넓게 펴지고, 이상치는 더 멀어졌죠?',
            '''
            # 방문자 수 열만 표로 골라요. 아주 큰 값이 하나 있어요.
            v_train = X_train[['visitors']]
            # 한 열짜리 표예요. (행 수, 열 수)로 나와요.
            print(v_train.shape)
            # 50%가 중앙값이에요. 75%에서 25%를 빼면 IQR이에요.
            print(v_train.describe().round(1))
            # 평균과 표준편차로 바꾼 결과예요.
            standard = StandardScaler().fit_transform(v_train)
            print(standard.round(2))
            # 견줄 도구예요. 지금은 위와 같은 StandardScaler예요.
            scaler = StandardScaler()
            other = scaler.fit_transform(v_train)
            # 이 도구가 나눈 값(scale_)과 바꾼 결과예요.
            scale = scaler.scale_
            print(scale)
            print(other.round(2))
            ''',
            '# 견줄 도구예요. 지금은 위와 같은 StandardScaler예요.\nscaler = StandardScaler()',
            '# 견줄 도구예요. 중앙값과 IQR을 기준으로 써요.\nscaler = RobustScaler()',
            tools='RobustScaler, StandardScaler', compare=['other', 'scale'],
            caution='`RobustScaler` 뒤 괄호를 빼면 도구를 만들지 않은 채라 TypeError가 나요.',
            hints=['`scaler = RobustScaler()`로 바꿔요.'],
            wrong=[('scaler = StandardScaler()', 'scaler = RobustScaler'),
                   # Measured on every store, test stores included.
                   ('scaler = RobustScaler()\nother = scaler.fit_transform(v_train)',
                    "scaler = RobustScaler()\nother = scaler.fit_transform(X[['visitors']])")]),
        stores('minmax-range', 'MinMaxScaler와 범위 밖 테스트 값',
            '`MinMaxScaler`는 열마다 최솟값을 0, 최댓값을 1로 맞춰요.\n'
            '이 최솟값과 최댓값도 훈련 자료로 재요.\n'
            '그래서 훈련 범위 밖의 테스트 값은 0보다 작거나 1보다 커요. 틀린 게 아니에요.',
            '먼저 실행해서 low와 high를 보세요. 훈련 자료는 딱 0과 1이죠?\n'
            'low와 high 줄의 `X_train_s`를 `X_test_s`로 바꾸세요. 두 줄이에요.\n'
            '다시 실행해서 0보다 작거나 1보다 큰 값을 찾아보세요. 훈련 범위 밖의 테스트 값이에요.',
            '''
            # 최솟값을 0, 최댓값을 1로 맞추는 도구예요.
            scaler = MinMaxScaler()
            # 훈련 자료로 기준을 재고 바로 바꿔요.
            X_train_s = scaler.fit_transform(X_train)
            # 훈련 자료에서 잰 최솟값(data_min_)과 최댓값(data_max_)이에요.
            print(scaler.data_min_)
            print(scaler.data_max_)
            # 테스트 자료는 훈련 기준으로 바꾸기만 해요.
            X_test_s = scaler.transform(X_test)
            print(X_test_s.round(2))
            # 열마다 가장 작은 값과 가장 큰 값이에요.
            low = X_train_s.min(axis=0)
            high = X_train_s.max(axis=0)
            print(low.round(2))
            print(high.round(2))
            ''',
            'low = X_train_s.min(axis=0)\nhigh = X_train_s.max(axis=0)',
            'low = X_test_s.min(axis=0)\nhigh = X_test_s.max(axis=0)',
            tools='MinMaxScaler', compare=['low', 'high', 'X_test_s'],
            caution='범위를 벗어났다고 테스트로 다시 fit하면 기준이 바뀌어요.',
            hints=['`low = X_test_s.min(axis=0)`처럼 두 줄 모두 X_test_s로 바꿔요.'],
            wrong=[('X_test_s = scaler.transform(X_test)\nprint(X_test_s.round(2))\n'
                    '# 열마다 가장 작은 값과 가장 큰 값이에요.\nlow = X_test_s',
                    'X_test_s = scaler.fit_transform(X_test)\nprint(X_test_s.round(2))\n'
                    '# 열마다 가장 작은 값과 가장 큰 값이에요.\nlow = X_test_s'),
                   # The raw test table instead of the scaled one.
                   ('low = X_test_s.min(axis=0)\nhigh = X_test_s.max(axis=0)',
                    'low = X_test.min(axis=0)\nhigh = X_test.max(axis=0)')]),
        stores('wrap-columns', '배열을 표로 다시 감싸요',
            '스케일러의 결과는 넘파이 배열(ndarray)이에요. 넘파이(numpy)는 숫자 계산 라이브러리예요.\n'
            '배열에는 열 이름과 행 이름이 없어요. `pd.DataFrame(배열, columns=열 이름)`으로 감싸요.\n'
            '그러면 열 이름이 돌아와요. 열 이름은 원래 표의 `columns`에서 가져와요.',
            '`type(값)`은 값의 자료형을 알려 줘요. 먼저 실행해서 자료형과 X_test, 열 이름을 보세요.\n'
            '열 이름이 0, 1, 2뿐이죠? test_df 줄의 `X_test_s` 뒤에 `, columns=X_test.columns`를 넣으세요.\n'
            '다시 실행해서 열 이름을 비교해요. 행 이름은 X_test의 행 번호가 아니라 0부터 새로 붙어요.',
            '''
            # 표준화 도구로 훈련 기준을 재고 바꿔요.
            scaler = StandardScaler()
            X_train_s = scaler.fit_transform(X_train)
            # 테스트 자료는 바꾸기만 해요.
            X_test_s = scaler.transform(X_test)
            # 결과의 자료형이에요. 표(DataFrame)가 아니에요.
            print(type(X_test_s))
            # 바꾸기 전 테스트 자료예요. 맨 왼쪽이 원래 행 번호예요.
            print(X_test)
            # 바꾼 테스트 자료를 표로 감싸요.
            test_df = pd.DataFrame(X_test_s)
            print(test_df.round(2))
            ''',
            'pd.DataFrame(X_test_s)', 'pd.DataFrame(X_test_s, columns=X_test.columns)', compare=['test_df'],
            caution='`columns=`를 빼고 열 이름만 넣으면 행 이름(index)으로 들어가요.',
            hints=['`test_df = pd.DataFrame(X_test_s, columns=X_test.columns)`로 바꿔요.'],
            wrong=[('pd.DataFrame(X_test_s)', 'pd.DataFrame(X_test_s, X_test.columns)')]),
        stores('scale-numbers-only', '도전 · 원핫 열은 두고 숫자 열만',
            '원핫 열은 이미 0과 1이라 그대로 두고, 숫자 열만 크기를 맞춰요.\n'
            '`X_train[num_cols] = 배열`은 그 열만 바꿔요. 행 번호와 다른 열은 그대로예요.\n'
            '오른쪽 배열도 숫자 열 3개여야 해요. 테스트 자료는 훈련 기준으로 바꾸기만 해요.',
            '준비 코드는 원핫 열까지 바꿨고, 테스트 기준도 잘못 쟀어요.\n'
            '숫자 열만 훈련 기준으로 바꾸세요. 원핫 열은 0과 1 그대로예요.\n'
            'X_train과 X_test는 열 이름과 행 번호가 그대로인 표로 남겨요.\n'
            '고칠 곳은 직접 찾아보세요. 바꾼 줄 위 주석도 맞게 고쳐요.',
            '''
            # 크기를 맞출 숫자 열 이름이에요.
            num_cols = ['seats', 'rent', 'visitors']
            # 표준화 도구를 만들어요.
            scaler = StandardScaler()
            ''' + WRAP_ALL.replace('\n', '\n            ') + '''
            # 두 표의 (행 수, 열 수)예요.
            print(X_train.shape, X_test.shape)
            # 소수 둘째 자리까지 봐요. 원핫 열의 값도 보세요.
            print(X_train.round(2))
            print(X_test.round(2))
            ''',
            WRAP_ALL, NUMBERS_ONLY, x=ENCODED_X, compare=['X_train', 'X_test'], challenge=True,
            caution='`transform`에 X_test 전체를 넣으면 열 이름이 달라 ValueError가 나요.',
            hints=['원핫 열까지 바꾼 것과 테스트로 다시 fit한 것, 두 가지를 고쳐요. '
                   '스케일러에 표 전체를 넣으면 열 수가 안 맞아 ValueError가 나요.',
                   '`X_train[num_cols] = scaler.fit_transform(X_train[num_cols])` 모양이에요. '
                   '테스트 줄은 `transform`이에요.'],
            wrong=[(WRAP_ALL, NUMBERS_ONLY.replace('scaler.transform(X_test', 'scaler.fit_transform(X_test')),
                   ('X_test = pd.DataFrame(scaler.fit_transform(X_test)', 'X_test = pd.DataFrame(scaler.transform(X_test)'),
                   ('X_test[num_cols] = scaler.transform(X_test[num_cols])', 'X_test[num_cols] = scaler.transform(X_test)')]),
        stores('new-store', '도전 · 새 매장 하나를 바꿔요',
            '모델을 쓸 때 들어오는 새 자료도 테스트 자료처럼 다뤄요.\n'
            '훈련 기준으로 `transform`만 해요. 한 행으로 fit하면 기준이 그 행 자신이 돼요.\n'
            "`pd.DataFrame({'열': [값]})`은 한 행짜리 표를 만들어요. 열 이름과 순서는 fit 때와 같아야 해요.",
            '`center_`는 RobustScaler가 훈련 자료로 잰 열마다의 중앙값이에요.\n'
            '먼저 실행해서 결과를 보세요. 새 매장 값을 바꿔도 늘 0이 나와요.\n'
            '준비 코드에는 실수가 두 가지 있어요. 고칠 곳은 직접 찾아보세요.\n'
            '고친 뒤에는 새 매장의 세 값을 center_와 열마다 견줘요. '
            '중앙값보다 작은 열은 결과가 음수죠?',
            '''
            # 이상치에 덜 흔들리는 도구로 훈련 기준을 재요.
            scaler = RobustScaler()
            scaler.fit(X_train)
            # 훈련 자료로 잰 열마다의 중앙값이에요.
            print(scaler.center_)
            # 새로 열 매장 하나의 값이에요.
            seats = 32
            rent = 2900
            visitors = 240
            # 새 매장을 한 행짜리 표로 만들어요.
            ''' + NEW_START.replace('\n', '\n            ') + '''
            print(new_s.round(2))
            ''',
            NEW_START, NEW_DONE, tools='RobustScaler', compare=['new_s'], challenge=True,
            values=(dict(seats=50, rent=4500, visitors=520), dict(seats=12, rent=1000, visitors=90),
                    dict(seats=70, rent=6100, visitors=3000)),
            caution='`scaler.fit_transform(new_store)`로 쓰면 훈련 기준이 새 매장 기준으로 바뀌어요.',
            hints=['새로 fit한 것과 표의 열 순서, 두 가지를 고쳐요.',
                   '`new_s = scaler.transform(new_store)`로 바꿔요. 열 순서는 seats, rent, visitors예요.'],
            wrong=[('new_s = RobustScaler().fit_transform(new_store)', 'new_s = scaler.transform(new_store)'),
                   ("{'rent': [rent], 'seats': [seats], 'visitors': [visitors]}",
                    "{'seats': [seats], 'rent': [rent], 'visitors': [visitors]}"),
                   ('new_s = scaler.transform(new_store)', 'new_s = scaler.fit_transform(new_store)')]),
    ])
