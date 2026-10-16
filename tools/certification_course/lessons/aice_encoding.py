"""aice-encoding: turn categories into model input with one-hot, label and ordinal codes (AICE Associate 12th lesson).

Single-table tasks read a small original member table; train/test tasks read a separate pair of
files. Every changed pair is built so that the test file misses a train category, brings a new one,
or both. The base test regions are fewer than the train regions, while the LONGER pair has the same
count with another meaning, so refitting an encoder on test data changes shapes or column meaning.
Two changed tables (other rows, channels, regions and yes ratios) make memorized output fail.
"""
from certification_course.kit import py_task
from principles_course.common import code, lesson

SOURCES = ['https://aice.study/info/aice/asso',
           'https://pandas.pydata.org/docs/reference/api/pandas.get_dummies.html',
           'https://scikit-learn.org/stable/modules/preprocessing.html#encoding-categorical-features']

MEMBERS = 'data/members.csv'
TRAIN = 'data/train.csv'
TEST = 'data/test.csv'

# Base: 8 members, three channels, all three grades, 3 of 8 renewed.
BASE = code('''
    region,channel,grade,visits,renew
    north,app,mid,12,yes
    south,web,low,3,no
    east,store,high,25,yes
    north,web,low,5,no
    west,app,high,18,yes
    south,app,mid,9,no
    east,web,mid,14,no
    north,store,low,2,no
''')

# Fewer rows, only two channels and two regions, 3 of 5 renewed.
SHORTER = code('''
    region,channel,grade,visits,renew
    south,web,high,21,yes
    south,app,low,4,no
    west,app,mid,11,yes
    west,web,mid,16,yes
    south,app,high,7,no
''')

# More rows, a fourth channel (call) and another region (jeju), 5 of 10 renewed.
LONGER = code('''
    region,channel,grade,visits,renew
    east,call,low,1,no
    north,app,high,30,yes
    jeju,web,mid,8,no
    east,app,mid,13,yes
    north,call,high,19,yes
    jeju,store,low,6,no
    south,web,low,4,no
    east,store,mid,15,yes
    north,app,low,3,no
    south,call,high,22,yes
''')

# Base pair: test has no store channel but a new kiosk; test regions are north and a new west.
BASE_TRAIN = code('''
    region,channel,grade,visits,renew
    north,app,mid,12,yes
    south,web,low,3,no
    east,store,high,25,yes
    north,web,low,5,no
    south,app,high,18,yes
    east,app,mid,9,no
    north,store,mid,14,yes
    south,web,low,2,no
''')

BASE_TEST = code('''
    region,channel,grade,visits,renew
    north,app,high,16,yes
    west,kiosk,low,4,no
    north,web,mid,10,no
    west,app,low,7,yes
''')

# Shorter pair: test has no app channel but a new store; three test regions against two in train.
SHORT_TRAIN = code('''
    region,channel,grade,visits,renew
    west,call,low,6,no
    north,app,high,22,yes
    west,web,mid,11,yes
    north,call,mid,8,no
    west,app,low,3,no
    north,web,high,17,yes
''')

SHORT_TEST = code('''
    region,channel,grade,visits,renew
    south,web,mid,13,yes
    north,store,low,5,no
    west,call,high,20,yes
''')

# Longer pair: test keeps every train channel and adds store; three regions on each side, but
# test has north instead of south, so a refit keeps the column count and changes the meaning.
LONG_TRAIN = code('''
    region,channel,grade,visits,renew
    east,app,low,4,no
    jeju,web,high,27,yes
    south,app,mid,12,yes
    east,kiosk,mid,15,yes
    jeju,app,low,2,no
    south,web,high,19,yes
    east,web,low,6,no
    jeju,kiosk,mid,10,no
    south,app,high,23,yes
''')

LONG_TEST = code('''
    region,channel,grade,visits,renew
    north,web,mid,9,no
    east,app,high,21,yes
    jeju,store,low,3,no
    north,kiosk,mid,14,yes
    east,web,low,5,no
''')

MEMBERS_HEADER = '''import pandas as pd

# 직접 만든 회원 자료예요. 실제 회원 자료가 아니에요.
df = pd.read_csv('data/members.csv')
'''

PAIR_HEADER = '''import pandas as pd

# 직접 만든 회원 자료를 훈련용과 테스트용으로 따로 받았어요.
train = pd.read_csv('data/train.csv')
test = pd.read_csv('data/test.csv')
'''

SKLEARN_HEADER = '''import pandas as pd
from sklearn.preprocessing import OneHotEncoder

# 직접 만든 회원 자료를 훈련용과 테스트용으로 따로 받았어요.
train = pd.read_csv('data/train.csv')
test = pd.read_csv('data/test.csv')
'''


def members(id, title, principle, goal, body, before, after, *, header=MEMBERS_HEADER, compare, caution,
            hints, wrong=None, challenge=False):
    """One experiment on the member table plus the two changed tables."""
    scenarios = [{'files': {MEMBERS: SHORTER}}, {'files': {MEMBERS: LONGER}}]
    return py_task(id, title, principle, goal, header + code(body), before, after, caution=caution,
                   hints=hints, scenarios=scenarios, files={MEMBERS: BASE}, compare=compare, wrong=wrong,
                   challenge=challenge)


def pair(id, title, principle, goal, body, before, after, *, header=PAIR_HEADER, compare, caution, hints,
         wrong=None, challenge=False):
    """One experiment on a train/test pair plus the two changed pairs."""
    scenarios = [{'files': {TRAIN: SHORT_TRAIN, TEST: SHORT_TEST}},
                 {'files': {TRAIN: LONG_TRAIN, TEST: LONG_TEST}}]
    return py_task(id, title, principle, goal, header + code(body), before, after, caution=caution,
                   hints=hints, scenarios=scenarios, files={TRAIN: BASE_TRAIN, TEST: BASE_TEST},
                   compare=compare, wrong=wrong, challenge=challenge)


LABEL_HEADER = MEMBERS_HEADER.replace('import pandas as pd\n',
                                      'import pandas as pd\nfrom sklearn.preprocessing import LabelEncoder\n')

ALIGN = 'X_test = X_test.reindex(columns=X_train.columns, fill_value=0)'

# Challenge 1: the test side misses both the grade map and the column alignment.
GRADE_START = '''train['grade'] = train['grade'].map(order)
# 입력 열만 골라 channel을 원핫해요.
cols = ['grade', 'visits', 'channel']
X_train = pd.get_dummies(train[cols], columns=['channel'], dtype=int)
X_test = pd.get_dummies(test[cols], columns=['channel'], dtype=int)'''

GRADE_DONE = '''train['grade'] = train['grade'].map(order)
# 테스트 등급도 같은 딕셔너리로 바꿔요.
test['grade'] = test['grade'].map(order)
# 입력 열만 골라 channel을 원핫해요.
cols = ['grade', 'visits', 'channel']
X_train = pd.get_dummies(train[cols], columns=['channel'], dtype=int)
X_test = pd.get_dummies(test[cols], columns=['channel'], dtype=int)
# 테스트 열을 훈련 열에 맞춰요.
''' + ALIGN

# Challenge 2: the encoder neither ignores unknown categories nor keeps what it learned from train.
TWO_START = '''enc = OneHotEncoder(sparse_output=False)
# 훈련 자료로 두 열을 한 번에 배우고 바꿔요.
X_train = enc.fit_transform(train[['region', 'channel']])
# 테스트 자료의 두 열도 바꿔요.
X_test = enc.fit_transform(test[['region', 'channel']])'''

TWO_DONE = TWO_START.replace("OneHotEncoder(sparse_output=False)",
                             "OneHotEncoder(handle_unknown='ignore', sparse_output=False)") \
    .replace("X_test = enc.fit_transform(", "X_test = enc.transform(")


def build():
    return lesson('aice-encoding', '범주를 모델 입력으로 바꾸기',
        '글자로 된 범주를 모델이 계산하는 숫자 열로 바꿔요. '
        '훈련과 테스트의 열 구성도 똑같이 맞춰요. '
        '필수 문제 7개와 선택 도전 2개예요.',
        SOURCES, [
        members('onehot-first', '글자 열을 0과 1 열로 나눠요',
            'channel의 app, web 같은 종류를 범주(category)라고 해요. 모델은 이런 글자를 계산하지 못해요.\n'
            '원핫 인코딩(one-hot)은 범주마다 열을 하나씩 만들어요. 그 행의 범주 열만 1, 나머지는 0이에요.\n'
            '`pd.get_dummies(표, columns=[열])`가 그 일을 해요.',
            '자, 먼저 실행해서 원핫 전후의 열 수를 비교하세요.\n'
            'channel 대신 channel_app 같은 열이 생겼죠? 값은 True(1)/False(0)로 보여요.\n'
            'pandas 버전마다 0과 1로 보이기도 해요. 그래서 형식을 정해 줘요.\n'
            "`columns=['channel']` 뒤에 `, dtype=int`를 넣고 다시 실행해 값을 봐요.",
            '''
            # 정답 renew를 빼고 입력 표 X를 만들어요.
            X = df.drop(columns=['renew'])
            # 원핫 전의 크기와 열 이름이에요.
            print(X.shape)
            print(X.columns)
            # channel 열만 원핫해서 다시 담아요. region과 grade는 다음 문제에서 다뤄요.
            # dtype=int를 주면 값이 0과 1로 나와요.
            X = pd.get_dummies(X, columns=['channel'])
            # 원핫 뒤의 크기와 표예요. 열이 늘었는지 봐요.
            print(X.shape)
            print(X)
            ''',
            "pd.get_dummies(X, columns=['channel'])", "pd.get_dummies(X, columns=['channel'], dtype=int)",
            compare=['X'],
            caution='표 전체에 `.astype(int)`를 붙이면 글자 열 때문에 ValueError가 나요.',
            hints=["`pd.get_dummies(X, columns=['channel'], dtype=int)`로 바꿔요."],
            wrong=[("pd.get_dummies(X, columns=['channel'])", "pd.get_dummies(X, columns=['channel']).astype(int)"),
                   ("pd.get_dummies(X, columns=['channel'])", "pd.get_dummies(X['channel'], dtype=int)")]),
        members('onehot-columns', '원핫할 열만 골라요',
            '`columns=`를 비우면 글자 열을 모두 원핫해요.\n'
            '순서가 있는 grade도 0/1 열 세 개로 쪼개져요. 세 열은 서로 대등해서 low < mid < high 순서가 사라져요.\n'
            '그래서 원핫할 열만 `columns=`에 적어요.',
            '먼저 실행해서 grade_로 시작하는 열을 찾아보세요. low, mid, high 순서로 놓였나요?\n'
            "`dtype=int` 앞에 `columns=['region', 'channel'], `를 넣으세요.\n"
            '다시 실행해서 열 목록에 grade가 그대로 남았는지 봐요.\n'
            'grade는 뒤 문제에서 순서대로 번호를 줘요.',
            '''
            # 정답 renew를 빼고 입력 표 X를 만들어요.
            X = df.drop(columns=['renew'])
            # columns=에 적은 열만 원핫해요. 비우면 글자 열을 모두 해요.
            X = pd.get_dummies(X, dtype=int)
            # 원핫 뒤의 열 이름과 크기예요.
            print(X.columns)
            print(X.shape)
            ''',
            'pd.get_dummies(X, dtype=int)', "pd.get_dummies(X, columns=['region', 'channel'], dtype=int)",
            compare=['X'],
            caution="`X[['region', 'channel']]`로 고르면 원핫하지 않을 열이 빠져요.",
            hints=["`pd.get_dummies(X, columns=['region', 'channel'], dtype=int)`로 바꿔요."],
            wrong=[('pd.get_dummies(X, dtype=int)', "pd.get_dummies(X, columns=['region'], dtype=int)"),
                   ('pd.get_dummies(X, dtype=int)', "pd.get_dummies(X[['region', 'channel']], dtype=int)")]),
        members('label-target', '글자 정답을 0과 1로 바꿔요',
            '라벨 인코딩(label encoding)은 종류마다 번호를 하나씩 줘요.\n'
            '`LabelEncoder`의 `fit_transform`은 종류를 배우고(fit) 번호로 바꿔요(transform).\n'
            '번호는 abc 순서로 붙고, 배운 순서는 `classes_`에 있어요.',
            '먼저 실행해서 y와 오류를 보세요. 글자로는 평균을 못 내요.\n'
            "`y = df['renew']`를 `y = le.fit_transform(df['renew'])`로 바꾸세요.\n"
            '다시 실행하면 y가 행 번호 없이 값만 늘어선 배열(array)로 나와요. 0과 1을 `classes_` 순서와 견줘 보세요.\n'
            'LabelEncoder는 이렇게 정답 y에 쓰는 도구예요.',
            '''
            # 라벨 인코더(LabelEncoder)를 하나 만들어 le에 담아요.
            le = LabelEncoder()
            # renew 열(yes/no)로 정답 y를 만들어요.
            y = df['renew']
            print(y)
            # y의 평균이에요. 0과 1이면 1의 비율이 돼요.
            print(y.mean())
            # 인코더가 배운 종류예요. 이 순서대로 0, 1 번호예요.
            print(le.classes_)
            ''',
            "y = df['renew']", "y = le.fit_transform(df['renew'])", header=LABEL_HEADER, compare=['y'],
            caution='`fit`만 쓰면 번호가 아니라 인코더 자체가 y에 담겨요.',
            hints=["`y = le.fit_transform(df['renew'])`로 바꿔요."],
            wrong=[("y = df['renew']", "y = le.fit(df['renew'])"),
                   ("y = df['renew']", "y = pd.get_dummies(df['renew'], dtype=int)")]),
        members('ordinal-map', '순서가 있는 등급은 직접 번호를 줘요',
            '순서가 있는 범주는 번호도 그 순서를 따라야 해요.\n'
            "앞에서 배운 딕셔너리에 '값: 번호' 짝을 적어요.\n"
            '`map(딕셔너리)`는 열의 값을 딕셔너리의 번호로 바꿔요.',
            '먼저 실행해서 grade와 abc_code를 나란히 보세요. 순서가 맞나요?\n'
            "grade_code 줄의 `df['abc_code']`를 아래 코드로 바꾸세요.\n"
            "`df['grade'].map({'low': 0, 'mid': 1, 'high': 2})`\n"
            '다시 실행해서 grade_code가 등급 순서대로 커지는지 봐요.',
            '''
            # 등급은 low < mid < high 순서가 있어요.
            le = LabelEncoder()
            # 라벨 인코더는 abc 순서로 번호를 줘요.
            df['abc_code'] = le.fit_transform(df['grade'])
            print(le.classes_)
            # 모델에 넣을 등급 번호예요.
            df['grade_code'] = df['abc_code']
            # 등급과 두 번호를 나란히 봐요.
            print(df[['grade', 'abc_code', 'grade_code']])
            ''',
            "df['grade_code'] = df['abc_code']",
            "df['grade_code'] = df['grade'].map({'low': 0, 'mid': 1, 'high': 2})",
            header=LABEL_HEADER, compare=['df'],
            caution='딕셔너리에 없는 값은 대소문자만 달라도 NaN이 돼요.',
            hints=["`df['grade_code'] = df['grade'].map({'low': 0, 'mid': 1, 'high': 2})`로 바꿔요."],
            wrong=[("df['grade_code'] = df['abc_code']", "df['grade_code'] = df['grade'].map({'low': 0, 'mid': 1})"),
                   ("df['grade_code'] = df['abc_code']",
                    "df['grade_code'] = df['grade'].map({'Low': 0, 'Mid': 1, 'High': 2})")]),
        pair('align-columns', '테스트 열을 훈련 열에 맞춰요',
            '훈련과 테스트에 나온 범주가 다르면, 따로 원핫한 열 구성도 달라져요.\n'
            '`reindex(columns=훈련 열, fill_value=0)`은 열을 훈련과 똑같이 맞춰요.\n'
            '없던 열은 0으로 채우고, 훈련에 없는 열은 버려요.',
            '먼저 실행해서 두 열 이름 목록을 견줘 보세요.\n'
            '맞추는 주석 아래에 다음 줄을 넣으세요.\n'
            f'`{ALIGN}`\n'
            '다시 실행해서 테스트에 없던 열과 테스트에만 있던 열을 봐요. '
            '테스트에만 있던 범주의 행은 channel 칸이 모두 0이 돼요.',
            '''
            # 입력은 visits와 channel이에요. 두 자료를 따로 원핫해요.
            X_train = pd.get_dummies(train[['visits', 'channel']], columns=['channel'], dtype=int)
            X_test = pd.get_dummies(test[['visits', 'channel']], columns=['channel'], dtype=int)
            # 두 표의 열 이름을 견줘 봐요.
            print(X_train.columns)
            print(X_test.columns)
            # 이 아래에서 테스트 열을 훈련 열에 맞춰요.
            # 테스트 표와 열 이름을 다시 확인해요.
            print(X_test)
            print(X_test.columns)
            ''',
            '# 이 아래에서 테스트 열을 훈련 열에 맞춰요.',
            '# 이 아래에서 테스트 열을 훈련 열에 맞춰요.\n' + ALIGN,
            compare=['X_train', 'X_test'],
            caution='`fill_value=0`을 빼면 테스트에 없던 열이 NaN으로 채워져요.',
            hints=[f'주석 아래에 `{ALIGN}`을 넣어요.'],
            wrong=[('# 이 아래에서 테스트 열을 훈련 열에 맞춰요.',
                    '# 이 아래에서 테스트 열을 훈련 열에 맞춰요.\nX_test = X_test.reindex(columns=X_train.columns)'),
                   ('# 이 아래에서 테스트 열을 훈련 열에 맞춰요.',
                    '# 이 아래에서 테스트 열을 훈련 열에 맞춰요.\nX_test = X_test.reindex(X_train.columns, fill_value=0)'),
                   ('# 이 아래에서 테스트 열을 훈련 열에 맞춰요.',
                    '# 이 아래에서 테스트 열을 훈련 열에 맞춰요.\n'
                    'X_train = X_train.reindex(columns=X_test.columns, fill_value=0)')]),
        pair('unknown-category', '처음 보는 범주가 나왔어요',
            '`OneHotEncoder`도 원핫을 해요. fit으로 범주를 배우고 transform으로 바꿔요.\n'
            '배우지 않은 범주가 테스트에 오면 지금 설정으로는 오류가 나요.\n'
            "`handle_unknown='ignore'`를 주면 그 행은 원핫 칸이 모두 0이 돼요.",
            '먼저 실행해서 오류의 마지막 줄을 읽어 보세요.\n'
            "`OneHotEncoder(` 괄호 안 맨 앞에 `handle_unknown='ignore', `를 넣으세요.\n"
            '다시 실행해서 처음 보는 channel 행의 값을 보세요.\n'
            '배운 열 이름과 견주면 어느 칸이 어느 범주인지 보여요.',
            '''
            # 원핫 인코더예요. 기본 결과는 0을 빼고 줄여 담은 희소(sparse) 형태예요.
            # sparse_output=False면 0까지 모두 담은 배열로 줘요.
            enc = OneHotEncoder(sparse_output=False)
            # 훈련 자료의 channel 종류를 배워요. 대괄호 두 겹은 표 모양이에요.
            enc.fit(train[['channel']])
            # 배운 열 이름이에요.
            print(enc.get_feature_names_out())
            # 테스트 자료의 channel이에요. 행 순서를 봐 둬요.
            print(test[['channel']])
            # 테스트 자료는 배운 대로 바꾸기만 해요.
            X_test = enc.transform(test[['channel']])
            # 1.과 0.은 소수점이 붙은 1과 0이에요.
            print(X_test)
            ''',
            'OneHotEncoder(sparse_output=False)', "OneHotEncoder(handle_unknown='ignore', sparse_output=False)",
            header=SKLEARN_HEADER, compare=['X_test'],
            caution="`test['channel']`처럼 대괄호를 한 겹만 쓰면 ValueError가 나요.",
            hints=["`OneHotEncoder(handle_unknown='ignore', sparse_output=False)`로 바꿔요."],
            wrong=[("X_test = enc.transform(test[['channel']])",
                    "X_test = enc.transform(test[['channel']], handle_unknown='ignore')"),
                   # Silencing the error by learning from the test file instead.
                   ("enc.fit(train[['channel']])", "enc.fit(test[['channel']])")]),
        pair('fit-train-only', '인코더는 훈련 자료로만 배워요',
            'fit은 범주를 배우는 단계예요. 다시 fit하면 앞에서 배운 것을 잊어요.\n'
            '테스트로 다시 배우면 열의 수나 뜻이 훈련과 달라져요.\n'
            '그래서 fit은 훈련 자료로만 하고, 테스트는 transform만 해요.',
            '먼저 실행해서 두 번 나온 열 이름과 크기를 견줘 보세요.\n'
            'X_test 줄의 `fit_transform`을 `transform`으로 바꾸세요.\n'
            '다시 실행해서 열 이름과 열 수가 훈련과 같은지 봐요.\n'
            '처음 보는 지역 행은 모든 칸이 0이에요.',
            '''
            # 처음 보는 범주는 0으로 두는 원핫 인코더예요.
            enc = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
            # 훈련 자료의 region을 배우고 바로 바꿔요.
            X_train = enc.fit_transform(train[['region']])
            print(enc.get_feature_names_out())
            print(X_train.shape)
            # 테스트 자료의 region을 바꿔요.
            X_test = enc.fit_transform(test[['region']])
            # 인코더가 마지막으로 배운 열 이름과 테스트 결과예요.
            print(enc.get_feature_names_out())
            print(X_test.shape)
            print(X_test)
            ''',
            "X_test = enc.fit_transform(test[['region']])", "X_test = enc.transform(test[['region']])",
            header=SKLEARN_HEADER, compare=['X_train', 'X_test'],
            caution='열 수가 같아도 테스트로 다시 fit하면 열의 뜻이 바뀔 수 있어요.',
            hints=["`X_test = enc.transform(test[['region']])`로 바꿔요."],
            wrong=[("X_test = enc.fit_transform(test[['region']])", "X_test = enc.transform(train[['region']])"),
                   ("X_test = enc.fit_transform(test[['region']])",
                    "enc = OneHotEncoder(handle_unknown='ignore', sparse_output=False)\n"
                    "X_test = enc.fit_transform(test[['region']])")]),
        pair('grade-and-channel', '도전 · 등급 번호와 원핫을 함께',
            '등급은 딕셔너리로 순서 번호를 주고, channel은 원핫해요.\n'
            '테스트 자료도 훈련 자료와 똑같은 처리를 거쳐야 해요.\n'
            '마지막에는 테스트 열을 훈련 열에 맞춰요.',
            '테스트 표 X_test가 훈련 표와 같은 열을 갖게 하세요. grade도 훈련처럼 번호여야 해요.\n'
            '준비 코드는 테스트 쪽 처리 두 가지를 빠뜨렸어요.\n'
            '고칠 곳은 직접 찾아보세요. 열 이름과 grade 값을 비교해요.',
            code('''
            # 등급 순서대로 번호를 주는 딕셔너리예요.
            order = {'low': 0, 'mid': 1, 'high': 2}
            # 훈련 등급을 딕셔너리의 번호로 바꿔요.
            ''') + GRADE_START + '\n' + code('''
            # 두 표의 열 이름과 테스트 표를 확인해요.
            print(X_train.columns)
            print(X_test.columns)
            print(X_test)
            '''),
            GRADE_START, GRADE_DONE, compare=['X_train', 'X_test'], challenge=True,
            caution='테스트 등급을 바꾸지 않으면 X_test의 grade가 글자로 남아요.',
            hints=['테스트 등급도 같은 딕셔너리로 바꾸고, 열은 훈련 열에 맞춰요.',
                   "훈련 등급 줄 아래에 `test['grade'] = test['grade'].map(order)`를 넣어요. "
                   f'X_test 줄 아래에는 `{ALIGN}`을 넣어요.'],
            wrong=[(GRADE_START, GRADE_START + '\n' + ALIGN),
                   (GRADE_START, GRADE_DONE.replace('\n# 테스트 열을 훈련 열에 맞춰요.\n' + ALIGN, '')),
                   (GRADE_START, GRADE_DONE.replace(ALIGN, 'X_test = X_test.reindex(columns=X_train.columns)'))]),
        pair('two-columns-encoder', '도전 · 두 열을 한 번에 원핫해요',
            '`OneHotEncoder`는 여러 열을 한 번에 원핫할 수 있어요.\n'
            '테스트에 처음 보는 범주가 있어도 오류 없이 모두 0이 되게 해요.\n'
            '배우기는 훈련 자료로만 해요. 그래야 두 배열의 열이 같아요.',
            '테스트 배열 X_test가 훈련 배열과 같은 열을 갖게 하세요.\n'
            '준비 코드는 두 군데가 틀렸어요. 고칠 곳은 직접 찾아보세요.\n'
            '두 배열의 크기와 마지막으로 배운 열 이름을 비교해요.',
            '# 결과를 0까지 모두 담은 배열로 받는 원핫 인코더예요.\n' + TWO_START + '\n' + code('''
            # 인코더가 마지막으로 배운 열 이름이에요.
            print(enc.get_feature_names_out())
            # 두 배열의 크기를 견줘요.
            print(X_train.shape)
            print(X_test.shape)
            '''),
            TWO_START, TWO_DONE, header=SKLEARN_HEADER, compare=['X_train', 'X_test'], challenge=True,
            caution='transform만 고치면 처음 보는 범주에서 ValueError가 나요.',
            hints=['인코더 설정 하나와 테스트를 바꾸는 줄 하나를 고쳐요.',
                   "`handle_unknown='ignore'`를 넣고, X_test 줄은 `enc.transform`으로 바꿔요."],
            wrong=[(TWO_START, TWO_START.replace('X_test = enc.fit_transform(', 'X_test = enc.transform(')),
                   (TWO_START, TWO_START.replace('OneHotEncoder(sparse_output=False)',
                                                 "OneHotEncoder(handle_unknown='ignore', sparse_output=False)")),
                   (TWO_START, TWO_START.replace('X_test = enc.fit_transform(test', 'X_test = enc.transform(train'))]),
    ])
