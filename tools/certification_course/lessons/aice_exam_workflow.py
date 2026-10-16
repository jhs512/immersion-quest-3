"""aice-exam-workflow: notebook cells, files and the limited open book (AICE Associate 23rd lesson).

The exam runs in a Jupyter notebook, cell by cell, with a kernel that remembers what ran. This player
runs main.py from the top as a fresh process every time, so `# [셀]` comments stand in for cells and
every run is like a kernel restart followed by running every cell once. Lesson text says so and never
claims to match the exam screen.

Every task reads a small original delivery table (order id, district, km, items, fee, minutes with
blanks). Two changed tables make memorized output fail: a shorter one whose slowest district differs,
and a longer one with a fifth district. Official facts used in the text come from the examinee guide
(answer in one cell, delete work cells, keep file names and extensions, saved CSV survives a kernel
restart, a failed first import or data load affects later items), notice 16322 (seven libraries and
their official documents only) and the official samples (answer variables such as 답안04, a pre-run
TensorFlow import cell and a Korean font cell). See .scratch/certification-research/aice-libraries.md.
"""
from certification_course.kit import py_task
from principles_course.common import code, lesson

SOURCES = ['https://aice.study/certi/examGuide', 'https://aice.study/info/aice/asso',
           'https://aice.study/board/notice/detail/16322', 'https://www.aice.team/guidebook',
           'https://scikit-learn.org/stable/install.html']

PATH = 'data/deliveries.csv'

# Base: 12 orders, two blank minutes. Slowest district by mean minutes is 북구.
BASE = code('''
    order_id,region,distance,items,fee,minutes
    D01,동구,1.2,2,3000,18
    D02,서구,3.5,1,3500,34
    D03,남구,2.1,3,3000,
    D04,북구,4.8,2,4000,41
    D05,동구,0.8,1,2500,15
    D06,서구,2.9,4,3500,30
    D07,남구,3.3,2,3500,29
    D08,북구,5.6,3,4500,
    D09,동구,1.9,2,3000,22
    D10,서구,4.1,1,4000,37
    D11,남구,2.6,5,3000,27
    D12,북구,3.9,2,4000,33
''')

# Shorter: 9 orders, two blanks. Slowest district is 서구.
SHORTER = code('''
    order_id,region,distance,items,fee,minutes
    E01,서구,2.4,1,3000,26
    E02,동구,1.1,3,2500,
    E03,북구,4.2,2,4000,38
    E04,남구,3.0,2,3500,31
    E05,서구,5.1,4,4500,44
    E06,동구,0.9,1,2500,14
    E07,남구,2.2,1,3000,
    E08,북구,3.6,3,4000,30
    E09,서구,1.7,2,3000,41
''')

# Longer: 14 orders, a fifth district (중구), two blanks. Slowest district is 남구.
LONGER = code('''
    order_id,region,distance,items,fee,minutes
    F01,중구,1.5,2,3000,24
    F02,남구,3.8,1,4000,39
    F03,동구,2.7,3,3500,
    F04,중구,4.9,2,4500,47
    F05,서구,1.2,1,2500,17
    F06,남구,2.5,4,3000,30
    F07,북구,3.1,2,3500,28
    F08,동구,4.4,2,4000,36
    F09,중구,0.7,1,2500,12
    F10,서구,3.4,3,3500,
    F11,북구,2.0,2,3000,23
    F12,남구,5.3,5,4500,49
    F13,동구,1.6,1,3000,20
    F14,서구,2.8,2,3500,29
''')

# The challenge's wrong file: last month's table, never changed by scenarios.
MAY = code('''
    order_id,region,distance,items,fee,minutes
    M01,동구,2.2,1,3000,21
    M02,서구,1.4,2,2500,19
    M03,남구,3.7,3,3500,35
    M04,북구,2.9,1,3500,
    M05,동구,4.5,2,4000,40
    M06,서구,0.6,4,2500,13
    M07,남구,1.8,2,3000,24
    M08,북구,3.2,1,3500,31
''')


def deliveries(id, title, principle, goal, starter, before, after, *, values=({}, {}), compare=(), caution, hints,
               wrong=None, challenge=False):
    """One notebook-habit experiment on the base table, then the shorter and the longer table."""
    scenarios = [dict(v, files={PATH: data}) for v, data in zip(values, (SHORTER, LONGER))]
    return py_task(id, title, principle, goal, starter, before, after, caution=caution, hints=hints,
                   scenarios=scenarios, files={PATH: BASE}, compare=compare, wrong=wrong, challenge=challenge)


# import-cell: the import written in the last cell moves up into the first cell.
IMPORT_LATE = '''# [셀] 불러오기 셀이에요. 쓸 도구는 여기 모아요.
import pandas as pd

# [셀] 자료를 읽고 훈련 75%, 테스트 25%로 나눠요.
df = pd.read_csv('data/deliveries.csv')
train, test = train_test_split(df, test_size=0.25, random_state=42)
# 두 몫의 행 수를 봐요.
print(len(train), len(test))

# [셀] 테스트 몫의 주문 번호를 봐요. 이 셀을 먼저 만들었어요.
from sklearn.model_selection import train_test_split
'''
IMPORT_TOP = '''# [셀] 불러오기 셀이에요. 쓸 도구는 여기 모아요.
import pandas as pd
from sklearn.model_selection import train_test_split

# [셀] 자료를 읽고 훈련 75%, 테스트 25%로 나눠요.
df = pd.read_csv('data/deliveries.csv')
train, test = train_test_split(df, test_size=0.25, random_state=42)
# 두 몫의 행 수를 봐요.
print(len(train), len(test))

# [셀] 테스트 몫의 주문 번호를 봐요. 이 셀을 먼저 만들었어요.
'''

# cell-order: the cell that makes clean moves above the cell that uses it.
USE_FIRST = '''# [셀] 지역별 평균 배달 시간을 봐요.
print(clean.groupby('region')['minutes'].mean().round(1).to_dict())

# [셀] 배달 시간이 빈 행을 지운 표 clean을 만들어요.
clean = df.dropna(subset=['minutes'])
# 지우기 전과 뒤의 행 수를 봐요.
print(len(df), len(clean))
'''
MAKE_FIRST = '''# [셀] 배달 시간이 빈 행을 지운 표 clean을 만들어요.
clean = df.dropna(subset=['minutes'])
# 지우기 전과 뒤의 행 수를 봐요.
print(len(df), len(clean))

# [셀] 지역별 평균 배달 시간을 봐요.
print(clean.groupby('region')['minutes'].mean().round(1).to_dict())
'''

# run-twice: the repeated run of the fee cell disappears.
TWICE = "# 같은 셀을 한 번 더 실행한 셈이에요.\ndf['fee'] = df['fee'] + extra\n"

# scaled-name and the first challenge share the scaling cell.
SCALE_OVER = 'X_train = scaler.fit_transform(X_train)'
SCALE_NEW = 'x_train = scaler.fit_transform(X_train)'

# restart-run-all: wrong file, scaling before the split, and the scaled values over X_train.
RUN_ALL_START = '''df = pd.read_csv('data/deliveries_may.csv')
X = df[['distance', 'items']]

# [셀] 훈련 자료로 기준을 재고 두 몫을 바꿔요.
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
x_test = scaler.transform(X_test)

# [셀] 훈련 75%, 테스트 25%로 나눠요.
X_train, X_test = train_test_split(X, test_size=0.25, random_state=42)
'''
RUN_ALL_DONE = '''df = pd.read_csv('data/deliveries_june.csv')
X = df[['distance', 'items']]

# [셀] 훈련 75%, 테스트 25%로 나눠요.
X_train, X_test = train_test_split(X, test_size=0.25, random_state=42)

# [셀] 훈련 자료로 기준을 재고 두 몫을 바꿔요.
scaler = StandardScaler()
x_train = scaler.fit_transform(X_train)
x_test = scaler.transform(X_test)
'''

# submit-ready: the work cell goes, the answer gets the set name, the file gets its extension.
SUBMIT_START = '''# [작업용 셀] 앞 다섯 행만 남겨 빠르게 시험해 봤어요.
df = df.head(5)
print(df)

# [답안 셀]
late = df[df['minutes'] >= 30]
answer = len(late)
late[['order_id', 'minutes']].to_csv('submission', index=False)
print(answer)
'''
SUBMIT_DONE = '''# [답안 셀]
late = df[df['minutes'] >= 30]
답안10 = len(late)
late[['order_id', 'minutes']].to_csv('submission.csv', index=False)
print(답안10)
'''


def build():
    return lesson('aice-exam-workflow', '노트북·파일·제한적 참고자료 사용',
        '시험 노트북에서 셀 순서와 이름 때문에 틀리는 일을 막아요. '
        '이 앱은 노트북이 아니라서 셀을 주석으로 흉내 내요. 필수 문제 8개와 선택 도전 2개예요.',
        SOURCES, [
        deliveries('import-cell', '불러오기는 맨 위 셀에 모아요',
            '시험은 노트북에서 코드를 셀로 나눠 하나씩 실행해요.\n'
            '이 앱은 노트북이 아니에요. `# [셀]` 주석으로 셀을 흉내 내요.\n'
            '불러오기(import)는 맨 위 셀에 모아요. 공식 샘플엔 TensorFlow 불러오기 셀과 '
            '한글 글꼴 설정 셀이 이미 있어요.',
            '자, 먼저 실행해서 NameError가 말하는 이름을 읽어 보세요.\n'
            '그 이름은 맨 아래 셀에서 불러와요. 위 셀이 먼저 돌아서 아직 모르죠.\n'
            '`from sklearn` 줄을 맨 위 pandas 줄 바로 아래로 옮기세요.\n'
            '다시 실행해서 행 수와 테스트 주문 번호를 확인해요.',
            IMPORT_LATE + "print(test['order_id'].tolist())\n",
            IMPORT_LATE, IMPORT_TOP, compare=['test'],
            wrong=[('import pandas as pd\n', 'import pandas as pd\nimport sklearn\n'),
                   ('import pandas as pd\n', 'import pandas as pd\nfrom sklearn import train_test_split\n')],
            caution='`import sklearn`만 위에 적으면 train_test_split 이름은 여전히 몰라요.',
            hints=['`from sklearn.model_selection import train_test_split` 줄을 잘라 맨 위로 옮겨요.']),
        deliveries('module-name', '불러올 때 이름은 sklearn이에요',
            'scikit-learn은 설치할 때 쓰는 이름이에요. 불러올 땐 `import sklearn`이라고 써요.\n'
            '`모듈.__version__`은 설치된 버전을 보여 줘요. 밑줄은 앞뒤 두 개씩이에요.\n'
            '공식 안내는 첫 불러오기가 실패하면 뒤 문항도 영향을 받는다고 해요.',
            '먼저 실행해서 마지막 줄의 ModuleNotFoundError를 읽어 보세요.\n'
            '그런 이름의 모듈이 없다는 뜻이에요. 이 앱엔 이미 깔려 있어 설치 명령은 안 써요.\n'
            '`import scikit_learn`을 `import sklearn`으로 바꾸세요.\n'
            '다시 실행해서 두 버전과 표 크기를 확인해요. 버전 숫자는 환경마다 달라요.',
            '''
            # [셀] 불러오기 셀이에요. 시험 공지에 나온 라이브러리를 불러와요.
            import pandas as pd
            import scikit_learn

            # 불러온 라이브러리의 버전을 봐요.
            print('pandas', pd.__version__)
            print('scikit-learn', sklearn.__version__)

            # [셀] 자료를 읽고 행과 열의 수를 봐요.
            df = pd.read_csv('data/deliveries.csv')
            print(df.shape)
            ''',
            'import scikit_learn', 'import sklearn',
            wrong=[('import scikit_learn', 'import sklearn as sk'), ('import scikit_learn', 'import scikit-learn')],
            caution='`import sklearn as sk`로 별명을 붙이면 sklearn 이름이 없어 NameError가 나요.',
            hints=['불러오기 줄을 `import sklearn`으로 바꿔요. 버전 줄은 그대로 둬요.']),
        deliveries('cell-order', '만드는 셀이 쓰는 셀보다 위에',
            '커널(kernel)은 셀을 실행하고 변수를 기억하는 곳이에요. 실행한 순서대로 기억해요.\n'
            '아래 셀을 먼저 돌렸다면 노트북에선 돌아가요. 커널을 다시 시작하면 그 기억이 지워져요.\n'
            '이 앱은 실행마다 처음부터 새로 돌려요. 다시 시작하고 위부터 다 실행한 셈이에요.',
            '먼저 실행해서 NameError가 말하는 이름을 보세요.\n'
            'clean은 맨 아래 셀에서 만들어요. 쓰는 셀이 그보다 위에 있죠?\n'
            'clean을 만드는 셀 네 줄(주석 포함)을 평균을 보는 셀 위로 옮기세요.\n'
            '다시 실행해서 행 수와 지역별 평균을 확인해요.',
            '''
            import pandas as pd

            # [셀] 자료를 읽어요.
            df = pd.read_csv('data/deliveries.csv')

            ''' + USE_FIRST.replace('\n', '\n            '),
            USE_FIRST, MAKE_FIRST, compare=['clean'],
            wrong=[("print(clean.groupby('region')", "print(df.groupby('region')"),
                   ("clean = df.dropna(subset=['minutes'])", "clean = df")],
            caution='오류 난 줄의 clean을 df로 바꾸면 빈칸을 지우기 전 표를 써요.',
            hints=['`# [셀] 배달 시간이 빈 행을` 주석부터 print 줄까지를 평균 셀 위로 옮겨요.']),
        deliveries('run-twice', '같은 셀을 두 번 실행하면',
            '자기 열을 고쳐 다시 담는 셀은 실행할 때마다 값이 또 바뀌어요.\n'
            '노트북에서 이런 셀을 두 번 돌리면 요금이 두 번 더해지죠.\n'
            '그럴 땐 커널을 다시 시작하고 위에서부터 한 번씩 실행해요.',
            '준비 코드는 배달비 셀을 두 번 실행한 상황을 흉내 내요.\n'
            '먼저 실행해서 두 목록의 차이가 extra의 몇 배인지 보세요.\n'
            '「한 번 더 실행한 셈」 주석과 그 아래 줄을 지우세요.\n'
            '다시 실행해서 차이가 extra 한 번만큼인지 확인해요.',
            '''
            import pandas as pd

            # 밤 배달에 더하는 요금(원)이에요.
            extra = 500

            # [셀] 자료를 읽고 원래 배달비를 봐 둬요.
            df = pd.read_csv('data/deliveries.csv')
            print(df['fee'].head(3).tolist())

            # [셀] 배달비에 밤 요금을 더해 같은 열에 다시 담아요.
            df['fee'] = df['fee'] + extra
            ''' + TWICE.replace('\n', '\n            ') + '''
            # [셀] 요금을 더한 배달비를 봐요.
            print(df['fee'].head(3).tolist())
            ''',
            TWICE, '', values=({'extra': 700}, {'extra': 300}), compare=['df'],
            wrong=[(TWICE, TWICE.replace('+ extra', '- extra')), ('extra = 500', 'extra = 250')],
            caution='extra를 반으로 줄여 맞추면 extra가 바뀔 때 틀려요.',
            hints=["`# 같은 셀을 한 번 더` 주석과 바로 아래 `df['fee'] = ...` 줄을 지워요."]),
        deliveries('scaled-name', '바꾼 값은 새 이름에 담아요',
            '`fit_transform`은 열 이름 없는 배열을 돌려줘요.\n'
            '이걸 같은 이름 X_train에 담으면 원래 표가 사라져요. 열 이름으로도 못 고르죠.\n'
            '문제가 x_train처럼 새 이름을 정하면 그 이름에 담아요. 파이썬은 대소문자를 구별해요.',
            '먼저 실행해서 마지막 줄의 IndexError를 보세요.\n'
            '배열은 자리 번호로만 고를 수 있다는 뜻이에요. X_train이 배열로 덮어써졌거든요.\n'
            'fit_transform 줄의 왼쪽 X_train만 `x_train`으로 바꾸세요.\n'
            '다시 실행해서 원래 단위의 평균과 두 몫의 크기를 확인해요.',
            '''
            import pandas as pd
            from sklearn.model_selection import train_test_split
            from sklearn.preprocessing import StandardScaler

            # [셀] 자료를 읽고 나눠요. 입력 X는 거리(km)와 물건 수예요.
            df = pd.read_csv('data/deliveries.csv')
            X = df[['distance', 'items']]
            X_train, X_test = train_test_split(X, test_size=0.25, random_state=42)

            # [셀] 문제: 표준화한 값은 x_train, x_test에 담으세요.
            scaler = StandardScaler()
            # 훈련 자료로 기준을 재고 바로 바꿔요.
            X_train = scaler.fit_transform(X_train)
            # 테스트 자료는 같은 기준으로 바꾸기만 해요.
            x_test = scaler.transform(X_test)

            # [셀] 원래 단위로 훈련 자료의 평균 거리를 봐요.
            print(round(X_train['distance'].mean(), 2))
            # 표준화한 두 몫의 크기를 봐요.
            print(x_train.shape, x_test.shape)
            ''',
            SCALE_OVER, SCALE_NEW, compare=['X_train', 'x_train', 'x_test'],
            wrong=[(SCALE_OVER, 'x_train = scaler.fit_transform(x_train)'),
                   ("print(round(X_train['distance'].mean(), 2))", 'print(round(X_train[:, 0].mean(), 2))')],
            caution='괄호 안까지 `x_train`으로 바꾸면 없는 이름이라 NameError가 나요.',
            hints=['`x_train = scaler.fit_transform(X_train)`으로 바꿔요. 괄호 안은 그대로예요.']),
        deliveries('submit-csv', '결과 파일은 정한 이름 그대로',
            '공식 안내는 결과 파일의 이름과 확장자를 문항대로 지키라고 해요.\n'
            '확장자는 파일 이름 끝의 `.csv` 같은 부분이에요. 빼면 다른 이름의 파일이 생겨요.\n'
            '저장한 CSV는 커널을 다시 시작해도 남아요. 변수와 다르죠.',
            '먼저 실행해서 FileNotFoundError가 찾지 못한 이름을 보세요.\n'
            "저장은 `'submission'`으로 했는데 읽기는 `'submission.csv'`로 했어요.\n"
            "to_csv의 이름을 `'submission.csv'`로 고치세요. 읽는 줄은 그대로 둬요.\n"
            '다시 실행해서 행·열 수와 열 이름을 확인해요.',
            '''
            import pandas as pd

            # [셀] 자료를 읽고 30분 이상 걸린 주문만 골라요.
            df = pd.read_csv('data/deliveries.csv')
            late = df[df['minutes'] >= 30]

            # [답안 셀] 문제: late의 order_id와 minutes를 submission.csv로 저장하세요.
            late[['order_id', 'minutes']].to_csv('submission', index=False)
            # 저장한 파일을 다시 읽어 확인해요.
            check = pd.read_csv('submission.csv')
            # 행·열 수와 열 이름을 봐요.
            print(check.shape)
            print(check.columns.tolist())
            ''',
            "'submission', index=False", "'submission.csv', index=False", compare=['check'],
            wrong=[("check = pd.read_csv('submission.csv')", "check = pd.read_csv('submission')"),
                   ("'submission', index=False", "'Submission.csv', index=False"),
                   ("'submission', index=False", "'submission.csv'")],
            caution="읽는 줄을 `'submission'`으로 맞추면 오류는 없어도 정한 파일이 없어요.",
            hints=["`to_csv('submission.csv', index=False)`로 고쳐요."]),
        deliveries('answer-name', '답은 정한 변수 이름에 담아요',
            '공식 샘플은 `답안04`처럼 답을 담을 변수 이름을 정해 줘요.\n'
            '이름이 한 글자만 달라도 파이썬에겐 다른 변수예요.\n'
            '글자를 직접 적는 답은 따옴표로 감싸요. 없으면 변수 이름으로 읽거든요.',
            '먼저 실행해서 NameError와 그 뒤의 물음을 읽어 보세요.\n'
            '문제는 `답안07`에 담으라고 했어요. 준비 코드는 `답안7`에 담았죠?\n'
            '답안 셀의 `답안7`을 `답안07`로 고치세요. 확인 셀은 그대로 둬요.\n'
            '다시 실행해서 지역 이름이 나오는지 확인해요.',
            '''
            import pandas as pd

            # [셀] 자료를 읽어요.
            df = pd.read_csv('data/deliveries.csv')

            # [답안 셀] 문제: 평균 배달 시간이 가장 긴 지역을 답안07에 담으세요.
            # 지역별 평균 배달 시간이에요. 빈칸은 빼고 계산해요.
            means = df.groupby('region')['minutes'].mean()
            # 평균이 가장 큰 지역의 이름을 골라요.
            답안7 = means.idxmax()

            # [셀] 문제가 정한 이름으로 답을 확인해요.
            print(답안07)
            ''',
            '답안7 = means.idxmax()', '답안07 = means.idxmax()', compare=['답안07'],
            wrong=[('답안7 = means.idxmax()', "답안07 = '북구'"),
                   ('print(답안07)', 'print(답안7)'),
                   ('답안7 = means.idxmax()', '답안_07 = means.idxmax()')],
            caution='print 줄을 `답안7`로 바꾸면 오류는 사라져도 답안07은 없어요.',
            hints=['`답안07 = means.idxmax()`로 고쳐요. 숫자 0을 빼먹지 마세요.']),
        deliveries('work-cell', '작업용 셀은 지우고 처음부터',
            '공식 안내는 답안을 한 셀에 쓰라고 해요. 여러 셀에 나누면 오답이에요.\n'
            '작업용 셀은 제출 전에 지워요. 그런데 지워도 그 셀이 바꾼 값은 커널에 남아요.\n'
            '그래서 지운 뒤 커널을 다시 시작하고 처음부터 실행해요.',
            '먼저 실행해서 작업용 셀이 무엇을 바꿨는지 보세요.\n'
            '작업용 셀의 세 줄(주석 포함)을 지우세요. 답안 셀은 그대로 둬요.\n'
            '다시 실행해서 답안08이 어떻게 달라졌는지 비교해요.',
            '''
            import pandas as pd

            # [셀] 자료를 읽어요.
            df = pd.read_csv('data/deliveries.csv')

            # [작업용 셀] 빈칸을 0으로 채워 보며 살펴봤어요.
            df['minutes'] = df['minutes'].fillna(0)
            print(df['minutes'].isna().sum())

            # [답안 셀] 문제: 빈칸을 뺀 평균 배달 시간을 답안08에 담으세요.
            답안08 = round(df['minutes'].mean(), 1)
            print(답안08)
            ''',
            "# [작업용 셀] 빈칸을 0으로 채워 보며 살펴봤어요.\ndf['minutes'] = df['minutes'].fillna(0)\n"
            "print(df['minutes'].isna().sum())\n\n", '', compare=['답안08'],
            wrong=[("print(df['minutes'].isna().sum())\n", ''),
                   ("df['minutes'] = df['minutes'].fillna(0)\n", '')],
            caution='print 줄만 지우고 fillna 줄을 남기면 빈칸이 0으로 계산돼요.',
            hints=['`# [작업용 셀]` 주석부터 그 아래 print 줄까지 세 줄을 지워요.']),
        py_task('restart-run-all', '도전 · 처음부터 한 번에 돌게',
            '셀 순서, 읽는 파일 이름, 덮어쓰기를 함께 점검해요.\n'
            '커널을 다시 시작하고 위에서부터 실행해도 돌아야 해요.',
            '문제 주석이 정한 대로 고치세요.\n'
            '오류를 하나 고치면 다음 오류가 보일 수 있어요.\n'
            '오류 없이 돌아도 문제가 정한 파일을 읽는지 확인하세요.',
            '''
            import pandas as pd
            from sklearn.model_selection import train_test_split
            from sklearn.preprocessing import StandardScaler

            # 문제: data/deliveries_june.csv의 거리와 물건 수를 표준화하세요.
            # 표준화한 값은 x_train, x_test에 담고 X_train은 원래 값으로 두세요.

            # [셀] 자료를 읽고 입력 X를 골라요.
            ''' + RUN_ALL_START.replace('\n', '\n            ') + '''
            # [셀] 원래 단위로 훈련 자료의 평균 물건 수를 봐요.
            print(round(X_train['items'].mean(), 2))
            # 표준화한 두 몫의 크기를 봐요.
            print(x_train.shape, x_test.shape)
            ''',
            RUN_ALL_START, RUN_ALL_DONE, challenge=True,
            files={'data/deliveries_june.csv': BASE, 'data/deliveries_may.csv': MAY},
            scenarios=[{'files': {'data/deliveries_june.csv': SHORTER}},
                       {'files': {'data/deliveries_june.csv': LONGER}}],
            compare=['X_train', 'x_train', 'x_test'],
            wrong=[(RUN_ALL_START, RUN_ALL_DONE.replace('june', 'may')),
                   (RUN_ALL_START, RUN_ALL_DONE.replace(SCALE_NEW, SCALE_OVER)),
                   (RUN_ALL_START, RUN_ALL_START.replace('may', 'june').replace(SCALE_OVER, SCALE_NEW))],
            caution='나누는 셀만 옮기면 X_train이 배열로 덮어써져 IndexError가 나요.',
            hints=['고칠 곳은 세 군데예요. 셀 순서, 읽는 파일, fit_transform 줄의 왼쪽 이름이에요.',
                   '나누는 셀을 표준화 셀 위로 옮겨요. june 파일을 읽고, 왼쪽은 x_train에 담아요.']),
        deliveries('submit-ready', '도전 · 제출 전에 답안 셀 점검',
            '작업용 셀 지우기, 답안 변수 이름, 결과 파일 이름을 함께 봐요.\n'
            '오류 없이 돌아도 정한 이름이 아니면 채점이 답을 못 찾아요.',
            '문제 주석이 시킨 대로 답안과 파일을 만드세요.\n'
            '지금도 오류 없이 돌지만 채점은 통과하지 못해요.\n'
            '고칠 곳은 직접 찾아보세요.',
            '''
            import pandas as pd

            # 문제: 30분 이상 걸린 주문 수를 답안10에 담으세요.
            # 그 주문들의 order_id와 minutes를 submission.csv로 저장하세요.

            # [셀] 자료를 읽어요.
            df = pd.read_csv('data/deliveries.csv')

            ''' + SUBMIT_START.replace('\n', '\n            '),
            SUBMIT_START, SUBMIT_DONE, compare=['답안10'], challenge=True,
            wrong=[(SUBMIT_START, SUBMIT_DONE.replace("'submission.csv'", "'submission'")),
                   (SUBMIT_START, SUBMIT_START.replace('answer', '답안10').replace("'submission'", "'submission.csv'")),
                   (SUBMIT_START, SUBMIT_DONE.replace('답안10', 'answer'))],
            caution='작업용 셀을 남기면 앞 다섯 행으로만 답을 구해요.',
            hints=['문제가 정한 이름은 답안10과 submission.csv예요. 작업용 셀도 봐요.',
                   '작업용 셀 세 줄을 지워요. answer는 답안10으로 바꾸고, 파일 이름엔 .csv를 붙여요.']),
    ])
