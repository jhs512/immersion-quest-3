"""aice-data-split: split into training, validation and test parts and check overlap and class shares.

Most tasks read a small original subscription table whose churn target (1) is a minority. The churn
rows sit where a plain random_state=42 split puts half of them in the test part, so stratify=y makes
a visible difference; the changed tables have other row counts and churn shares (one puts no churn
row at all in the plain test part). The time tasks read an original daily sales log with a rising
trend; the changed logs cover other dates and lengths, and the challenge reads the same logs stored
out of date order. Splits without random_state differ on every run, so they never match the reference.
"""
from certification_course.kit import py_task
from principles_course.common import code, lesson

SOURCES = ['https://aice.study/info/aice/asso',
           'https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html',
           'https://scikit-learn.org/stable/modules/cross_validation.html']

MEMBERS = 'data/members.csv'
DAILY = 'data/daily.csv'

# Base: 36 members, 9 churn (25%). A plain random_state=42 split with test_size=0.2 tests rows
# 12, 13, 16, 21, 26, 30, 31, 35; four churn rows (13, 21, 30, 35) sit there, so the plain test
# part is 50% churn while stratify=y keeps 25% on both sides. In the three-way challenge the plain
# second split gives the validation part 3 churn of 7 against 2 with stratify.
BASE = code('''
    months,visits,spend,churn
    19,3,31000,0
    25,3,39000,0
    6,4,13000,1
    15,14,31000,0
    24,10,42000,0
    20,20,16000,0
    4,4,11000,1
    16,3,37000,0
    15,19,33000,0
    3,2,23000,1
    5,7,31000,0
    12,5,28000,0
    12,5,40000,0
    7,2,12000,1
    33,4,41000,0
    30,3,20000,0
    19,8,49000,0
    26,4,51000,0
    6,2,20000,1
    19,5,36000,0
    17,18,46000,0
    7,1,18000,1
    19,6,37000,0
    31,17,43000,0
    17,4,15000,0
    4,1,23000,1
    32,19,15000,0
    22,14,19000,0
    23,7,34000,0
    35,8,37000,0
    6,1,15000,1
    29,12,29000,0
    11,4,45000,0
    16,11,29000,0
    31,12,16000,0
    3,4,15000,1
''')

# Fewer rows (24) and more churn (7, 29%); the plain test part (rows 0, 8, 11, 16, 18) has no churn.
SHORTER = code('''
    months,visits,spend,churn
    25,18,42000,0
    21,15,20000,0
    4,4,12000,1
    15,13,32000,0
    17,12,20000,0
    7,1,24000,1
    18,11,20000,0
    6,3,12000,1
    26,18,20000,0
    9,3,29000,0
    8,19,15000,0
    18,3,19000,0
    20,4,17000,0
    5,5,19000,1
    4,6,50000,0
    7,5,12000,1
    35,12,14000,0
    7,4,39000,0
    19,16,21000,0
    27,3,22000,0
    7,0,17000,1
    27,4,24000,0
    3,1,25000,1
    20,12,26000,0
''')

# 33 rows and less churn (7, 21%); three churn rows land in the 7-row plain test part.
LONGER = code('''
    months,visits,spend,churn
    12,4,22000,0
    2,2,13000,1
    12,3,29000,0
    29,9,27000,0
    35,10,41000,0
    7,4,22000,1
    10,11,37000,0
    12,5,43000,0
    4,8,44000,0
    7,3,16000,1
    24,6,38000,0
    7,5,48000,0
    6,0,12000,1
    34,11,18000,0
    19,17,45000,0
    12,18,23000,0
    8,12,41000,0
    2,0,16000,1
    20,18,31000,0
    9,12,17000,0
    8,17,14000,0
    15,15,35000,0
    24,10,46000,0
    34,17,50000,0
    4,4,32000,0
    11,20,23000,0
    4,4,14000,1
    13,6,51000,0
    23,20,27000,0
    7,0,15000,1
    23,18,31000,0
    31,6,44000,0
    26,11,23000,0
''')

# Daily logs in date order with a rising sales trend: 20, 15 and 25 days in different months.
DAYS = code('''
    date,temp,rain,sales
    2026-04-01,14,0,329000
    2026-04-02,17,2,352000
    2026-04-03,17,0,373000
    2026-04-04,14,0,366000
    2026-04-05,15,0,380000
    2026-04-06,15,0,361000
    2026-04-07,18,22,346000
    2026-04-08,17,0,379000
    2026-04-09,19,0,395000
    2026-04-10,14,27,353000
    2026-04-11,21,0,410000
    2026-04-12,18,0,423000
    2026-04-13,20,22,373000
    2026-04-14,19,0,429000
    2026-04-15,19,0,454000
    2026-04-16,21,2,443000
    2026-04-17,22,0,456000
    2026-04-18,21,6,440000
    2026-04-19,21,0,480000
    2026-04-20,23,29,415000
''')

FEWER_DAYS = code('''
    date,temp,rain,sales
    2026-05-11,11,0,360000
    2026-05-12,12,0,370000
    2026-05-13,13,29,323000
    2026-05-14,14,0,385000
    2026-05-15,19,0,423000
    2026-05-16,14,0,415000
    2026-05-17,19,9,420000
    2026-05-18,21,21,409000
    2026-05-19,18,0,427000
    2026-05-20,18,0,446000
    2026-05-21,21,0,477000
    2026-05-22,23,0,477000
    2026-05-23,25,0,494000
    2026-05-24,23,0,478000
    2026-05-25,25,0,506000
''')

MORE_DAYS = code('''
    date,temp,rain,sales
    2026-06-01,15,0,327000
    2026-06-02,13,10,318000
    2026-06-03,16,0,355000
    2026-06-04,15,5,345000
    2026-06-05,12,0,347000
    2026-06-06,18,0,349000
    2026-06-07,16,0,362000
    2026-06-08,18,0,384000
    2026-06-09,20,0,385000
    2026-06-10,18,0,393000
    2026-06-11,15,0,396000
    2026-06-12,16,0,393000
    2026-06-13,20,0,416000
    2026-06-14,15,0,407000
    2026-06-15,19,0,427000
    2026-06-16,20,0,423000
    2026-06-17,17,0,416000
    2026-06-18,20,13,409000
    2026-06-19,21,0,449000
    2026-06-20,19,0,465000
    2026-06-21,20,0,445000
    2026-06-22,22,0,479000
    2026-06-23,19,0,470000
    2026-06-24,20,15,455000
    2026-06-25,24,16,449000
''')


def scramble(text, order):
    """The same log stored out of date order: data rows in the given fixed order."""
    header, *rows = text.splitlines()
    assert sorted(order) == list(range(len(rows)))
    return '\n'.join([header] + [rows[i] for i in order]) + '\n'


# Fixed orders, so the challenge's starter never happens to be in date order.
DAYS_MIXED = scramble(DAYS, [3, 5, 10, 6, 14, 19, 15, 9, 18, 4, 11, 0, 8, 2, 7, 1, 12, 13, 17, 16])
FEWER_DAYS_MIXED = scramble(FEWER_DAYS, [7, 14, 2, 1, 8, 11, 10, 3, 9, 6, 13, 0, 12, 4, 5])
MORE_DAYS_MIXED = scramble(MORE_DAYS, [24, 15, 17, 5, 4, 11, 22, 8, 0, 21, 23, 16, 12, 1, 19, 13, 10, 14, 6,
                                       3, 9, 18, 2, 7, 20])

MEMBER_HEADER = '''import pandas as pd
# scikit-learn에서 나누는 함수만 불러와요.
from sklearn.model_selection import train_test_split

# 직접 만든 구독 고객 자료예요. churn이 1이면 떠난 고객이에요.
df = pd.read_csv('data/members.csv')
'''

XY = '''# 입력 X와 정답 y를 나눠요.
X = df.drop(columns=['churn'])
y = df['churn']
'''

DAILY_HEADER = '''import pandas as pd
# scikit-learn에서 나누는 함수만 불러와요.
from sklearn.model_selection import train_test_split

# 직접 만든 하루 매출 기록이에요. 날짜순으로 저장돼 있어요.
df = pd.read_csv('data/daily.csv')
# 입력 X와 정답 y(매출)를 나눠요.
X = df.drop(columns=['sales'])
y = df['sales']
'''


def member_task(id, title, principle, goal, body, before, after, *, xy=True, compare=(), caution, hints,
                wrong=None, challenge=False, volatile=False):
    """One split experiment on the member table plus the two changed tables."""
    starter = MEMBER_HEADER + (XY if xy else '') + code(body)
    scenarios = [{'files': {MEMBERS: SHORTER}}, {'files': {MEMBERS: LONGER}}]
    return py_task(id, title, principle, goal, starter, before, after, caution=caution, hints=hints,
                   scenarios=scenarios, files={MEMBERS: BASE}, compare=compare, wrong=wrong,
                   challenge=challenge, volatile=volatile)


# The challenge's last block: the two splits of a mixed-up log and what each part covers.
MIXED_BEFORE = '''df = pd.read_csv('data/daily.csv')
# 입력 X와 정답 y(매출)를 나눠요.
X = df.drop(columns=['sales'])
y = df['sales']
# 뒤쪽 20%를 테스트 몫으로 떼요.
X_rest, X_test, y_rest, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
# 남은 몫의 뒤쪽 25%를 검증 몫으로 떼요.
X_train, X_val, y_train, y_val = train_test_split(X_rest, y_rest, test_size=0.25, random_state=42)'''

MIXED_AFTER = '''df = pd.read_csv('data/daily.csv')
# 날짜순으로 정렬해 다시 담아요.
df = df.sort_values('date')
# 입력 X와 정답 y(매출)를 나눠요.
X = df.drop(columns=['sales'])
y = df['sales']
# 뒤쪽 20%를 테스트 몫으로 떼요.
X_rest, X_test, y_rest, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
# 남은 몫의 뒤쪽 25%를 검증 몫으로 떼요.
X_train, X_val, y_train, y_val = train_test_split(X_rest, y_rest, test_size=0.25, shuffle=False)'''

MIXED_STARTER = '''import pandas as pd
# scikit-learn에서 나누는 함수만 불러와요.
from sklearn.model_selection import train_test_split

# 직접 만든 하루 매출 기록이에요. 날짜가 뒤섞여 저장돼 있어요.
''' + MIXED_BEFORE + '''
# 세 몫의 첫 날짜, 마지막 날짜, 평균 매출이에요.
print(X_train['date'].min(), X_train['date'].max(), round(y_train.mean()))
print(X_val['date'].min(), X_val['date'].max(), round(y_val.mean()))
print(X_test['date'].min(), X_test['date'].max(), round(y_test.mean()))
'''


def build():
    item = lesson('aice-data-split', '훈련·검증·테스트를 구분하기',
        '자료를 훈련·검증·테스트 몫으로 나눠요. 몫끼리 겹침과 비율을 직접 확인해요. '
        '필수 문제 8개와 선택 도전 2개예요.',
        SOURCES, [
        member_task('first-split', '훈련 자료와 테스트 자료로 나눠요',
            'scikit-learn(코드에선 sklearn)은 머신러닝 도구 모음이에요. `from 모듈 import 이름`은 그 이름만 불러와요.\n'
            '`train_test_split`은 행을 섞어 훈련 자료와 테스트 자료로 나눠요. 나뉜 한쪽을 몫이라고 해요.\n'
            '학습에 쓴 자료로 채점하면 외운 건지 몰라요. 그래서 테스트 자료는 남겨 둬요. '
            '훈련 자료는 문제집, 테스트 자료는 모의고사인 셈이죠.',
            '자, 먼저 실행해서 전체와 두 몫의 크기(행 수, 열 수)를 보세요.\n'
            '지금은 절반을 테스트로 떼요. 공부할 문제집이 너무 얇죠?\n'
            '`test_size=0.5`의 0.5를 0.2로 바꾸세요.\n'
            '다시 실행해서 행 수를 비교해요. 나눠떨어지지 않으면 테스트 행 수를 올림해요.',
            '''
            # 전체 표의 크기예요. (행 수, 열 수)로 나와요.
            print(df.shape)
            # 행을 섞어 두 몫으로 나눠요. test_size는 테스트 몫의 비율이에요.
            # 돌려준 두 몫을 차례로 train, test에 받아요.
            train, test = train_test_split(df, test_size=0.5)
            # 두 몫의 크기를 견줘요.
            print(train.shape)
            print(test.shape)
            ''',
            'test_size=0.5', 'test_size=0.2', xy=False,
            caution='`test_size=20`처럼 정수를 쓰면 비율이 아니라 20행을 떼요.',
            hints=['`train_test_split(df, test_size=0.2)`로 바꿔요.'],
            wrong=[('test_size=0.5', 'test_size=20'), ('test_size=0.5', 'train_size=0.2')]),
        member_task('return-order', '몫 네 개는 정해진 순서로 받아요',
            '입력 X와 정답 y를 함께 넣으면 몫 네 개를 돌려줘요.\n'
            '순서는 `X_train, X_test, y_train, y_test`예요. 넣은 것마다 훈련, 테스트 순이죠.\n'
            '값은 받는 이름이 아니라 자리 순서대로 담겨요. 순서가 틀려도 오류가 안 나요.',
            '먼저 실행해서 크기 네 개를 보세요. 입력은 (행 수, 열 수)로 나와요.\n'
            '정답은 열이 하나라서 (행 수,)로 나오고요.\n'
            'X_test에 열 수가 없죠? 정답이 담긴 거예요.\n'
            '받는 이름을 `X_train, X_test, y_train, y_test` 순서로 고치고 다시 실행하세요.',
            '''
            # 몫 네 개를 받아요. 받는 순서를 잘 보세요.
            X_train, y_train, X_test, y_test = train_test_split(X, y, test_size=0.2)
            # 입력의 크기예요. (행 수, 열 수)로 나와야 해요.
            print(X_train.shape)
            print(X_test.shape)
            # 정답의 크기예요. 열이 하나라서 (행 수,)로 나와야 해요.
            print(y_train.shape)
            print(y_test.shape)
            ''',
            'X_train, y_train, X_test, y_test =', 'X_train, X_test, y_train, y_test =',
            caution='받는 순서를 바꿔 적어도 오류 없이 엉뚱한 값이 담겨요.',
            hints=['`X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)`예요.'],
            wrong=[('X_train, y_train, X_test, y_test =', 'X_train, X_test, y_test, y_train ='),
                   ('X_train, y_train, X_test, y_test =', 'X_test, X_train, y_test, y_train =')]),
        member_task('random-state', '섞는 방법을 번호로 고정해요',
            'train_test_split은 실행할 때마다 행을 새로 섞어요. 뽑히는 행이 매번 달라요.\n'
            '`random_state=42`처럼 번호를 주면 섞는 방법이 고정돼요. 늘 같은 행이 뽑히죠.\n'
            '번호가 다르면 뽑히는 행도 달라요. 시험에선 문제에 적힌 번호를 그대로 써요.',
            '먼저 실행해서 두 줄의 행 번호를 비교하세요. 한 번 더 실행해서도 봐요.\n'
            '`train_test_split` 두 줄 모두 `test_size=0.2` 뒤에 `, random_state=42`를 넣으세요.\n'
            '여러 번 실행해서 행 번호가 늘 같은지 봐요.',
            '''
            # 같은 코드로 두 번 나눠요.
            first_train, first_test = train_test_split(df, test_size=0.2)
            second_train, second_test = train_test_split(df, test_size=0.2)
            # 테스트 몫에 뽑힌 행 번호(인덱스)예요.
            print(first_test.index)
            print(second_test.index)
            ''',
            'first_train, first_test = train_test_split(df, test_size=0.2)\n'
            'second_train, second_test = train_test_split(df, test_size=0.2)',
            'first_train, first_test = train_test_split(df, test_size=0.2, random_state=42)\n'
            'second_train, second_test = train_test_split(df, test_size=0.2, random_state=42)',
            xy=False, compare=['first_test', 'second_test'],
            caution='한 줄에만 넣으면 다른 줄은 여전히 매번 다르게 섞여요.',
            hints=['두 줄 모두 `train_test_split(df, test_size=0.2, random_state=42)` 모양이에요.'],
            wrong=[('first_test = train_test_split(df, test_size=0.2)',
                    'first_test = train_test_split(df, test_size=0.2, random_state=42)'),
                   ('first_train, first_test = train_test_split(df, test_size=0.2)\n'
                    'second_train, second_test = train_test_split(df, test_size=0.2)',
                    'first_train, first_test = train_test_split(df, test_size=0.2, random_state=0)\n'
                    'second_train, second_test = train_test_split(df, test_size=0.2, random_state=0)')]),
        member_task('test-count', '테스트 몫을 행 수로 정해요',
            '`test_size`는 테스트 몫, `train_size`는 훈련 몫의 크기예요.\n'
            '하나만 주면 남은 행이 다른 몫이 돼요.\n'
            '0.2처럼 1보다 작은 수는 비율, 5처럼 1 이상의 정수는 행 수예요.',
            '이번 문제는 테스트 자료를 5행으로 정했어요.\n'
            '먼저 실행해서 두 몫의 행 수를 보세요. 훈련 쪽이 5행이죠?\n'
            '`train_size=5`를 `test_size=5`로 바꾸세요.\n'
            '다시 실행해서 테스트 쪽이 5행인지 봐요.',
            '''
            # 이번에 정한 테스트 몫은 5행이에요.
            X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=5, random_state=42)
            # 두 몫의 행 수를 확인해요.
            print(len(X_train))
            print(len(X_test))
            ''',
            'train_size=5', 'test_size=5', compare=['X_train', 'X_test'],
            caution='`test_size=0.5`로 쓰면 5행이 아니라 절반을 떼요.',
            hints=['`train_test_split(X, y, test_size=5, random_state=42)`로 바꿔요.'],
            # train_size=31 only works because the base table has 36 rows.
            wrong=[('train_size=5', 'test_size=0.5'), ('train_size=5', 'train_size=31')]),
        member_task('stratify', '떠난 고객 비율을 두 몫에 고루 나눠요',
            '떠난 고객(1)처럼 드문 값은 섞기만 하면 한쪽 몫에 몰릴 수 있어요.\n'
            '`stratify=y`를 넣으면 y의 값 비율대로 두 몫에 나눠 담아요. 층화 추출이라고 해요.\n'
            '비율은 `value_counts(normalize=True)`로 견줘요.',
            '먼저 실행해서 전체, 훈련, 테스트의 1 비율을 견줘 보세요.\n'
            '`random_state=42` 뒤에 `, stratify=y`를 넣으세요.\n'
            '다시 실행해서 세 비율이 비슷해졌는지 봐요.',
            '''
            # 전체 자료의 0과 1 비율이에요. 1이 떠난 고객이에요.
            print(y.value_counts(normalize=True))
            # 섞어서 나눠요. 1의 비율은 따로 챙기지 않았어요.
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            # 훈련 몫과 테스트 몫의 비율을 견줘요.
            print(y_train.value_counts(normalize=True))
            print(y_test.value_counts(normalize=True))
            ''',
            'random_state=42)', 'random_state=42, stratify=y)', compare=['y_train', 'y_test'],
            caution='`stratify=X`처럼 입력 표를 넣으면 이 자료에선 ValueError가 나요.',
            hints=['`train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)`예요.'],
            wrong=[('random_state=42)', 'random_state=42, stratify=X)'),
                   ('random_state=42)', 'stratify=y)')]),
        member_task('overlap-check', '문제집과 모의고사가 겹치나요?',
            'train_test_split은 원래 행 번호(인덱스)를 그대로 가져가요. `X_test.index`로 꺼내요.\n'
            '`set(값들)`은 값 모음(집합)이에요. `&`는 양쪽에 다 있는 값만 남겨요.\n'
            '겹친 게 없으면 `set()`으로 보여요. 학습 자료와 테스트 자료는 겹치면 안 돼요.',
            '먼저 실행해서 겹친 행 번호와 그 수를 보세요.\n'
            '훈련 자료는 문제집, 테스트 자료는 모의고사예요. 지금은 모의고사 문제를 문제집에 넣은 셈이죠. '
            '외운 건지 이해한 건지 몰라요.\n'
            'study 줄의 X를 X_train으로 바꾸세요.\n'
            '다시 실행해서 `set()`과 0이 나오는지 봐요.',
            '''
            # 훈련 80%, 테스트 20%로 나눠요.
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            # 모델이 공부할 문제집이에요.
            study = X
            # 문제집과 테스트 몫에 함께 있는 행 번호예요.
            common = set(study.index) & set(X_test.index)
            print(common)
            # 겹친 행의 수예요.
            print(len(common))
            ''',
            'study = X', 'study = X_train', compare=['study', 'common'],
            caution='테스트 행이 학습 자료에 섞여도 오류 없이 그냥 실행돼요.',
            hints=['`study = X_train`으로 바꿔요.'],
            wrong=[('study = X', 'study = X_test'), ('study = X', 'study = y_train')]),
        member_task('validation-split', '검증 자료는 남은 몫에서 떼요',
            '검증 자료는 모델을 고르고 고칠 때 보는 몫이에요. 테스트 자료는 마지막에 한 번만 써요.\n'
            '그래서 테스트를 먼저 떼고, 남은 몫을 다시 나눠 검증 자료를 만들어요.\n'
            '남은 80%의 25%는 전체의 20%예요. 훈련, 검증, 테스트가 60:20:20이 되죠. '
            '나눠떨어지지 않으면 떼는 쪽을 올림해서 조금 어긋나요.',
            '먼저 실행해서 세 몫과 전체의 행 수, 겹친 행 번호를 보세요.\n'
            '세 몫을 더하면 전체보다 많죠? 검증 몫을 떼는 줄이 전체 X, y를 다시 나눴어요.\n'
            '그 줄의 `X, y`를 `X_rest, y_rest`로 바꾸세요. 첫 나누기 줄은 그대로 둬요.\n'
            '다시 실행해서 행 수의 합과 겹침을 비교해요.',
            '''
            # 테스트 몫 20%를 먼저 떼요. 남은 몫은 X_rest, y_rest예요.
            X_rest, X_test, y_rest, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            # 남은 몫에서 검증 몫 25%를 떼요.
            X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.25, random_state=42)
            # 훈련, 검증, 테스트, 전체의 행 수예요.
            print(len(X_train), len(X_val), len(X_test), len(X))
            # 검증 몫과 테스트 몫에 함께 있는 행 번호예요.
            print(set(X_val.index) & set(X_test.index))
            ''',
            '(X, y, test_size=0.25', '(X_rest, y_rest, test_size=0.25', compare=['X_train', 'X_val', 'y_val'],
            caution='`X_rest`에 `y`를 짝지으면 행 수가 달라 ValueError가 나요.',
            hints=['`train_test_split(X_rest, y_rest, test_size=0.25, random_state=42)`예요.'],
            wrong=[('(X, y, test_size=0.25', '(X_rest, y, test_size=0.25'),
                   ('(X, y, test_size=0.25', '(X_test, y_test, test_size=0.25')]),
        py_task('time-order', '날짜가 있으면 섞지 않고 나눠요',
            '날짜가 있는 자료를 섞어 나누면 테스트보다 늦은 날로 배우게 돼요. '
            '미래를 미리 보고 과거를 맞히는 셈이죠.\n'
            '`shuffle=False`를 넣으면 섞지 않고 앞쪽을 훈련, 뒤쪽을 테스트로 떼요.\n'
            '섞지 않으니 random_state는 필요 없어요.',
            '먼저 실행해서 두 몫의 첫 날짜와 마지막 날짜를 보세요.\n'
            "'2025-12-31'처럼 적은 날짜는 글자 순서가 곧 날짜 순서예요. "
            '그래서 `min()`이 첫 날짜, `max()`가 마지막 날짜예요.\n'
            '훈련 몫에 테스트보다 늦은 날이 있죠? `random_state=42`를 `shuffle=False`로 바꾸세요.\n'
            '다시 실행해서 훈련 마지막 날이 테스트 첫날보다 앞인지 봐요.',
            DAILY_HEADER + code('''
            # 뒤쪽 20%를 테스트 몫으로 떼려고 해요.
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            # 두 몫의 첫 날짜와 마지막 날짜예요.
            print(X_train['date'].min(), X_train['date'].max())
            print(X_test['date'].min(), X_test['date'].max())
            '''),
            'random_state=42', 'shuffle=False', files={DAILY: DAYS},
            scenarios=[{'files': {DAILY: FEWER_DAYS}}, {'files': {DAILY: MORE_DAYS}}],
            compare=['X_train', 'X_test', 'y_test'],
            caution='random_state 번호만 바꾸면 날짜는 여전히 섞여요.',
            hints=['`train_test_split(X, y, test_size=0.2, shuffle=False)`로 바꿔요.'],
            wrong=[('random_state=42', 'random_state=0'), ('random_state=42', "shuffle='False'")]),
        member_task('three-way-stratified', '도전 · 세 몫 모두 비율을 지켜요',
            '세 몫으로 나눌 때는 두 번의 나누기 모두 같은 규칙을 지켜요.\n'
            'stratify에는 그 줄에서 나누는 정답을 넣어요. 행 수가 같아야 하거든요. '
            '다르면 `inconsistent numbers of samples` 오류가 나요.\n'
            '0과 1만 있는 열의 평균은 1의 비율과 같아요.',
            '검증 몫도 1의 비율을 지키고, 몇 번을 실행해도 같게 나눠야 해요.\n'
            '섞는 번호는 42예요. 고칠 곳은 직접 찾아보세요.\n'
            '여러 번 실행해서 검증 몫의 행 번호와 세 비율을 보세요.\n'
            '행은 쪼갤 수 없어서 세 비율이 딱 같진 않아요. 비슷하면 돼요.',
            '''
            # 테스트 몫 20%를 먼저 떼요. 1의 비율을 지켜요.
            X_rest, X_test, y_rest, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
            # 남은 몫에서 검증 몫 25%를 떼요.
            X_train, X_val, y_train, y_val = train_test_split(X_rest, y_rest, test_size=0.25)
            # 검증 몫에 뽑힌 행 번호예요.
            print(X_val.index)
            # 훈련, 검증, 테스트의 행 수예요.
            print(len(y_train), len(y_val), len(y_test))
            # 세 몫의 1 비율이에요. 0과 1의 평균이 곧 1의 비율이에요.
            print(y_train.mean(), y_val.mean(), y_test.mean())
            ''',
            'test_size=0.25)', 'test_size=0.25, random_state=42, stratify=y_rest)',
            compare=['X_val', 'y_train', 'y_val', 'y_test'], challenge=True,
            caution='두 번째 줄에 `stratify=y`를 넣으면 행 수가 달라 ValueError가 나요.',
            hints=['두 번째 나누기 줄에 빠진 것이 두 가지예요. 첫 줄과 견줘 보세요. '
                   'stratify에는 그 줄이 나누는 정답을 넣어요.',
                   '`test_size=0.25` 뒤에 `, random_state=42, stratify=y_rest`를 넣어요.'],
            wrong=[('test_size=0.25)', 'test_size=0.25, random_state=42, stratify=y)'),
                   ('test_size=0.25)', 'test_size=0.25, random_state=42)'),
                   ('test_size=0.25)', 'test_size=0.25, stratify=y_rest)')]),
        py_task('time-three-way', '도전 · 뒤섞인 기록을 세 몫으로',
            '기록 파일이 늘 날짜순이지는 않아요. `shuffle=False`는 놓인 순서대로 잘라요.\n'
            "그래서 X, y를 나누기 전에 df를 `sort_values('date')`로 날짜순 정렬해요. "
            '`sort_values`는 정렬한 새 표를 돌려줘요. df 자체는 그대로라서 다시 담아야 하죠.\n'
            '검증 몫도 시간 순서를 지켜요. 훈련, 검증, 테스트 순으로 날짜가 이어져야 해요.',
            '이번 기록은 날짜가 뒤섞여 저장돼 있어요. 날이 갈수록 매출이 느는 자료예요.\n'
            '세 몫이 날짜순으로 이어지게 고치세요. 줄 하나를 더하고, 줄 하나를 고쳐요.\n'
            '날짜 범위와 평균 매출을 고치기 전과 비교해요.',
            MIXED_STARTER, MIXED_BEFORE, MIXED_AFTER, files={DAILY: DAYS_MIXED},
            scenarios=[{'files': {DAILY: FEWER_DAYS_MIXED}}, {'files': {DAILY: MORE_DAYS_MIXED}}],
            challenge=True,
            caution='X만 정렬하고 y를 그대로 두면 날짜와 매출의 짝이 어긋나요.',
            hints=["`df.sort_values('date')`만 쓰면 df는 그대로예요. 앞에 `df = `를 붙여요. "
                   '검증 몫을 떼는 줄도 섞지 않아야 해요.',
                   "read_csv 줄 아래에 `df = df.sort_values('date')`를 넣어요. "
                   '두 번째 나누기의 `random_state=42`는 `shuffle=False`로 바꿔요.'],
            wrong=[(MIXED_BEFORE, MIXED_AFTER.replace('test_size=0.25, shuffle=False', 'test_size=0.25, random_state=42')),
                   (MIXED_BEFORE, MIXED_BEFORE.replace('test_size=0.25, random_state=42', 'test_size=0.25, shuffle=False')),
                   # Only X sorted: y keeps the file order, so dates and sales no longer pair up.
                   ("# 날짜순으로 정렬해 다시 담아요.\ndf = df.sort_values('date')\n"
                    "# 입력 X와 정답 y(매출)를 나눠요.\nX = df.drop(columns=['sales'])",
                    "# 입력 X와 정답 y(매출)를 나눠요.\nX = df.drop(columns=['sales']).sort_values('date')")]),
    ])
    # These starters split without random_state, so their first run differs every time.
    for t in item['tasks']:
        if t['id'] in ('random-state', 'three-way-stratified'):
            t['_volatile'] = True
    return item
