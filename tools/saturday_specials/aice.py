"""Original split experiments and two independent preprocessing practice sets."""
import csv
import io
from certification_course.kit import py_task
from certification_course.kit_plots import plot_task
from principles_course.common import code, lesson

SOURCES = [
    'https://www.hancoding.kr/theory/12?note=136',
    'https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html',
    'https://pandas.pydata.org/docs/user_guide/missing_data.html',
]


def customers(n, offset=0):
    out = io.StringIO()
    w = csv.writer(out, lineterminator='\n')
    w.writerow(['member_id', 'age', 'fee', 'region', 'plan', 'churn'])
    for i in range(n):
        w.writerow([100 + i, '' if i % 11 == 0 else 19 + (i * 7 + offset) % 44,
                    18000 + (i * 3000 + offset * 1000) % 42000,
                    ['East', 'West', 'South'][i % 3], ['Basic', 'Silver', 'Gold'][i % 3],
                    int(i % 4 == 0)])
    return out.getvalue()


def deliveries(n, offset=0):
    out = io.StringIO()
    w = csv.writer(out, lineterminator='\n')
    w.writerow(['order_id', 'distance', 'minutes', 'weather'])
    for i in range(n):
        w.writerow([200 + i, 45 if i == 3 else 1 + (i * 3 + offset) % 20,
                    '' if i % 13 == 0 else 12 + (i * 5 + offset) % 50,
                    ['Clear', 'Rain'][i % 2]])
    return out.getvalue()


FILES = {'data/members.csv': customers(32), 'data/delivery.csv': deliveries(30)}
CASES = [
    {'files': {'data/members.csv': customers(24, 5), 'data/delivery.csv': deliveries(24, 3)}},
    {'files': {'data/members.csv': customers(40, 9), 'data/delivery.csv': deliveries(40, 7)}},
]
HEADER = """\
import pandas as pd
from sklearn.model_selection import train_test_split
# 각 문제는 자기 자료를 처음부터 읽어요.
"""
MEMBERS = HEADER + "df = pd.read_csv('data/members.csv')\n"
DELIVERY = HEADER + "df = pd.read_csv('data/delivery.csv')\n"
SPLIT = MEMBERS + """\
# 타깃을 입력에서 빼고 같은 행의 정답을 남겨요.
X = df[['age', 'fee']]
y = df['churn']
"""


def make(id, title, principle, goal, source, before, after, *, compare=(), caution=None,
         challenge=False, plot=False, wrong=None):
    factory = plot_task if plot else py_task
    source = code(source)
    # Split is imported only by exercises that actually use it.
    if 'train_test_split(' not in source.replace(before, after, 1):
        source = source.replace('from sklearn.model_selection import train_test_split\n', '')
    return factory(id, title, principle, goal, source, before, after,
        files=FILES, scenarios=CASES, compare=compare, wrong=wrong or [],
        caution=caution or '정답 숫자를 외워 쓰면 자료가 바뀔 때 틀려요.',
        hints=['문제의 조건과 바꿀 줄을 하나씩 대조해 보세요.', chr(96) + after.strip() + chr(96)],
        challenge=challenge)


def build():
    result = []
    result.append(lesson('sat-aice-split', '데이터를 나누는 이유부터 확인해요',
        '훈련과 검증을 나누고 행의 짝을 확인해요. 필수 5문제와 선택 도전 1문제예요.',
        SOURCES, [
        make('target-out', '입력에 정답이 들어가면 어떨까요',
             '입력 X에는 예측할 정답이 없어야 해요.',
             'churn만 입력에서 빼세요. 원본 df는 남겨요.',
             MEMBERS + "# 입력과 정답을 따로 보관해요.\nX = df.copy()\ny = df['churn']\nprint(list(X.columns))\nprint(y.head(3).tolist())",
             'X = df.copy()', "X = df.drop(columns=['churn'])", compare=['X', 'y'],
             caution='정답을 입력에 넣으면 정답을 보고 맞히는 누수예요.'),
        make('holdout', '같은 자료로 연습하고 채점하지 않아요',
             '검증용 행은 훈련용 행과 겹치지 않게 남겨요.',
             '두 줄의 대입을 한 번의 분리 호출로 바꾸세요.\n검증 비율은 25%, 난수 설정값은 7이에요.',
             SPLIT + "# 지금은 같은 행을 훈련과 검증에 넣었어요.\nX_train, X_valid = X, X\ny_train, y_valid = y, y\n# 개수와 겹친 행 수를 비교해요.\nprint(len(X_train), len(X_valid))\nprint(len(X_train.index.intersection(X_valid.index)))",
             'X_train, X_valid = X, X\ny_train, y_valid = y, y',
             'X_train, X_valid, y_train, y_valid = train_test_split(X, y, test_size=0.25, random_state=7)',
             compare=['X_train', 'X_valid', 'y_train', 'y_valid'],
             caution='같은 행을 복사해 나누면 검증 역할을 못 해요.'),
        make('return-order', '네 반환값의 자리를 맞춰요',
             '반환 순서는 입력 두 묶음 다음 정답 두 묶음이에요.',
             '받는 변수 순서만 고치세요.\nX_train에는 표, y_train에는 정답이 담겨야 해요.',
             SPLIT + "# 함수의 반환 순서대로 이름을 붙여요.\nX_train, y_train, X_valid, y_valid = train_test_split(X, y, test_size=0.25, random_state=7)\nprint(type(X_train).__name__, type(y_train).__name__)\nprint(len(X_train), len(y_train))",
             'X_train, y_train, X_valid, y_valid =',
             'X_train, X_valid, y_train, y_valid =',
             compare=['X_train', 'X_valid', 'y_train', 'y_valid']),
        make('same-rows', '입력과 정답은 함께 섞어요',
             '입력과 정답을 한 번에 나누면 행의 짝이 유지돼요.',
             '정답만 원래 순서에서 자르는 줄을 고치세요.\nX_train의 행 번호로 y를 골라 담으세요.',
             SPLIT + "# 함께 나눈 결과에서 훈련 행 번호를 얻어요.\nX_train, X_valid, _, y_valid = train_test_split(X, y, test_size=0.25, random_state=7)\n# 정답도 같은 행 번호로 골라요.\ny_train = y.iloc[:len(X_train)]\nprint(y_train.index.tolist())\nprint(y_train.tolist())",
             'y.iloc[:len(X_train)]', 'y.loc[X_train.index]', compare=['y_train'],
             caution='두 자료의 개수가 같아도 행의 짝은 다를 수 있어요.'),
        make('ratio', '25는 비율일까요 개수일까요',
             'test_size의 실수는 비율, 정수는 개수예요.',
             '검증 자료를 전체의 25%로 바꾸세요.\n행이 늘면 검증 행 수도 함께 늘어야 해요.',
             SPLIT + "# 정수 5는 다섯 행을 뜻해요.\nX_train, X_valid, y_train, y_valid = train_test_split(X, y, test_size=5, random_state=7)\nprint(len(X_valid), len(X))",
             'test_size=5', 'test_size=0.25', compare=['X_valid']),
        make('partition-proof', '도전 · 겹침과 누락을 확인해요',
             '서로 겹치지 않고 전체를 덮어야 올바른 분리예요.',
             '공통 행이 아니라 두 묶음의 모든 행을 구하세요.\ncovered에는 중복 없는 전체 행 번호를 담아요.',
             SPLIT + "X_train, X_valid, y_train, y_valid = train_test_split(X, y, test_size=0.25, random_state=7)\n# 합친 행 번호가 원본 전체와 같은지 확인해요.\ncovered = X_train.index.intersection(X_valid.index)\nprint(sorted(covered.tolist()))",
             '.intersection(', '.union(', compare=['covered'], challenge=True),
    ]))
    result.append(lesson('sat-aice-options', '분리 옵션을 바꾸며 원리를 확인해요',
        '재현성과 클래스 비율을 실험해요. 필수 5문제와 선택 도전 1문제예요.',
        SOURCES, [
        make('seed', '같은 조건으로 분리를 재현해요',
             '같은 자료와 난수 설정값이면 분리를 재현할 수 있어요.',
             'random_state만 42에서 7로 바꾸세요.\n지정된 행 번호를 다시 얻는 실험이에요.',
             SPLIT + "X_train, X_valid, y_train, y_valid = train_test_split(X, y, test_size=0.25, random_state=42)\n# 실제로 뽑힌 행 번호를 비교해요.\nprint(X_valid.index.tolist())",
             'random_state=42', 'random_state=7', compare=['X_valid'],
             caution='7이 더 좋은 모델을 보장하는 숫자는 아니에요.'),
        make('stratify', '소수 클래스도 나눠 담아요',
             '층화 분리는 정답 종류의 비율을 비슷하게 유지해요.',
             'stratify를 y로 바꾸세요.\n나눈 정답의 종류별 개수를 비교해요.',
             SPLIT + "# 분류 정답으로 층을 나눠요.\nX_train, X_valid, y_train, y_valid = train_test_split(X, y, test_size=0.25, random_state=7, stratify=None)\nprint(y_train.value_counts().sort_index().tolist())\nprint(y_valid.value_counts().sort_index().tolist())",
             'stratify=None', 'stratify=y', compare=['X_valid', 'y_valid'],
             caution='작은 자료에서는 반올림 때문에 비율이 완전히 같진 않아요.'),
        make('regression', '연속 숫자는 종류별로 묶지 않아요',
             '배달 시간처럼 연속적인 정답은 보통 층화하지 않아요.',
             '회귀 자료를 나눌 수 있게 stratify를 고치세요.\n기존 오류와 바뀐 실행 결과를 비교해요.',
             DELIVERY + "# 결측 행을 빼고 입력과 연속 정답을 나눠요.\ndf = df.dropna()\nX = df[['distance']]\ny = df['minutes']\n# 각 숫자를 별도 클래스로 층화하면 문제가 생겨요.\nX_train, X_valid, y_train, y_valid = train_test_split(X, y, test_size=0.25, random_state=7, stratify=y)\nprint(X_valid.index.tolist())",
             'stratify=y', 'stratify=None', compare=['X_valid', 'y_valid'],
             caution='연속 숫자를 그대로 층화하면 한 종류가 한 행일 수 있어요.'),
        make('fit-training', '스케일의 기준은 훈련에서 구해요',
             '검증 자료로 기준을 배우면 누수가 생겨요.',
             '평균을 구하는 대상을 X에서 X_train으로 바꾸세요.\n검증에는 훈련에서 구한 평균을 그대로 써요.',
             SPLIT + "X_train, X_valid, y_train, y_valid = train_test_split(X, y, test_size=0.25, random_state=7)\n# 평균도 훈련으로만 구해요.\nmean_fee = X['fee'].mean()\nvalid_centered = X_valid['fee'] - mean_fee\nprint(round(mean_fee, 2))\nprint(valid_centered.round(2).tolist())",
             "mean_fee = X['fee'].mean()", "mean_fee = X_train['fee'].mean()",
             compare=['mean_fee', 'valid_centered']),
        make('time-order', '시간 자료는 미래를 남겨요',
             '시간순 예측에서는 뒤쪽을 검증으로 남길 수 있어요.',
             '행이 날짜순으로 정렬돼 있다고 가정해요.\nshuffle을 False로 바꾸고 뒤쪽 행을 확인해요.',
             DELIVERY + "# 주문 번호가 증가하는 시간순 자료예요.\nX = df[['order_id', 'distance']]\ny = df['minutes']\n# 시간순 분리에서는 앞뒤를 섞지 않아요.\nX_train, X_valid, y_train, y_valid = train_test_split(X, y, test_size=0.25, shuffle=True, random_state=7)\nprint(X_valid['order_id'].tolist())",
             'shuffle=True', 'shuffle=False', compare=['X_valid'],
             caution='시간순 자료를 섞으면 미래 정보가 훈련에 섞일 수 있어요.'),
        make('transfer', '도전 · 조건 세 개를 함께 적용해요',
             '새 조건에도 분리 원리는 같아요.',
             '검증 25%, 난수 19, 클래스 비율 유지예요.\n함수 호출 한 줄을 조건에 맞게 완성하세요.',
             SPLIT + "# 세 조건을 동시에 만족시켜요.\nX_train, X_valid, y_train, y_valid = train_test_split(X, y, test_size=0.5, random_state=3)\nprint(X_valid.index.tolist())\nprint(y_valid.tolist())",
             'test_size=0.5, random_state=3', 'test_size=0.25, random_state=19, stratify=y',
             compare=['X_valid', 'y_valid'], challenge=True),
    ]))
    result.append(lesson('sat-aice-mock-inspect', '모의문제 · 표와 그래프를 읽어요',
        '분석·전처리 범위의 자체 모의문제예요. 필수 5문제와 선택 도전 1문제예요.',
        SOURCES, [
        make('csv', '다른 CSV를 읽는 실수를 고쳐요',
             '파일 이름은 분석 대상과 같아야 해요.',
             '회원 자료를 읽어 마지막 세 행을 확인하세요.\ndf의 파일 경로만 고치세요.',
             "import pandas as pd\n# 회원 자료를 읽을 자리예요.\ndf = pd.read_csv('data/delivery.csv')\nprint(df.tail(3).to_string(index=False))",
             "'data/delivery.csv'", "'data/members.csv'", compare=['df']),
        make('missing-count', '빈칸의 개수를 구해요',
             'isna는 빈칸 위치를 참거짓으로 표시해요.',
             '전체 빈칸 수를 total에 담으세요.\n두 번 합쳐야 표 전체의 개수가 나와요.',
             MEMBERS + "# 표 전체의 결측 개수를 세어요.\ntotal = df.isna().sum().mean()\nprint(total)",
             '.sum().mean()', '.sum().sum()', compare=['total']),
        make('region-bars', '지역별 인원수를 그려요',
             '막대의 높이는 지역마다 센 인원수예요.',
             '지역별 fee 합계 대신 행의 개수를 세세요.\n축 이름은 준비된 코드를 그대로 써요.',
             MEMBERS + "import matplotlib.pyplot as plt\n# 지역별 행 수를 막대로 보여 줘요.\ncounts = df.groupby('region')['fee'].sum()\ncounts.plot.bar()\nplt.xlabel('region')\nplt.ylabel('members')\nplt.tight_layout()\nplt.show()",
             "df.groupby('region')['fee'].sum()", "df.groupby('region').size()",
             plot=True, compare=['counts']),
        make('scatter', '거리와 시간의 관계를 그려요',
             '산점도의 한 점은 같은 행의 두 값이에요.',
             'Y축 자료를 minutes로 고치세요.\n거리와 소요 시간의 관계를 확인해요.',
             DELIVERY + "import matplotlib.pyplot as plt\n# 그래프에 쓸 두 값이 모두 있는 행을 남겨요.\ndf = df.dropna(subset=['distance', 'minutes'])\n# 가로는 거리, 세로는 배달 시간이에요.\nplt.scatter(df['distance'], df['distance'])\nplt.xlabel('distance')\nplt.ylabel('minutes')\nplt.tight_layout()\nplt.show()",
             "plt.scatter(df['distance'], df['distance'])", "plt.scatter(df['distance'], df['minutes'])",
             plot=True),
        make('iqr', 'IQR의 방향을 고쳐요',
             '사분위 범위는 Q3에서 Q1을 뺀 값이에요.',
             'iqr 계산의 뺄셈 순서를 고치세요.\n하한과 상한을 함께 확인해요.',
             MEMBERS + "# 요금의 가운데 절반 범위를 구해요.\nq1 = df['fee'].quantile(0.25)\nq3 = df['fee'].quantile(0.75)\n# Q3가 큰 쪽이에요.\niqr = q1 - q3\nbounds = (q1 - 1.5 * iqr, q3 + 1.5 * iqr)\nprint(bounds)",
             'iqr = q1 - q3', 'iqr = q3 - q1', compare=['bounds']),
        make('audit', '도전 · 결측 비율을 요약해요',
             '비율은 빈칸 수를 전체 행 수로 나눠 구해요.',
             '열별 결측 비율을 0~1로 구하세요.\n건수 대신 비율을 rate에 담아요.',
             MEMBERS + "# 열마다 빠진 값의 비율을 비교해요.\nrate = df.isna().sum()\nprint(rate.round(3).to_dict())",
             'df.isna().sum()', 'df.isna().mean()', compare=['rate'], challenge=True),
    ]))
    result.append(lesson('sat-aice-mock-clean', '모의문제 · 전처리부터 분리까지 풀어요',
        '조건을 읽고 자료를 바꿔도 풀어봐요. 필수 6문제와 선택 도전 1문제예요.',
        SOURCES, [
        make('outlier', '경계값을 읽고 행을 남겨요',
             '30 미만을 남기면 30 이상은 제거돼요.',
             'distance가 30 미만인 행만 남기세요.\n결과는 원본과 분리된 clean에 담아요.',
             DELIVERY + "# 경계의 어느 쪽을 남기는지 확인해요.\nclean = df.loc[df['distance'] >= 30].copy()\nprint(clean['order_id'].tolist())",
             "df['distance'] >= 30", "df['distance'] < 30", compare=['clean']),
        make('dropna', '빈칸 위치와 삭제 결과를 구분해요',
             'dropna는 빈칸이 있는 행을 지운 표를 돌려줘요.',
             '빈칸이 있는 행을 모두 지우세요.\n남은 표를 clean에 담아요.',
             DELIVERY + "# 참거짓 표가 아니라 남은 자료가 필요해요.\nclean = df.isna()\nprint(clean.to_string(index=False))",
             'clean = df.isna()', 'clean = df.dropna()', compare=['clean']),
        make('category', '두 요금제를 하나로 묶어요',
             'isin은 목록 중 하나인지 검사해요.',
             'Basic과 Silver를 모두 Standard로 바꾸세요.\nGold는 그대로 남겨요.',
             MEMBERS + "# 두 종류를 같은 이름으로 바꿔요.\ndf.loc[df['plan'].isin(['Basic']), 'plan'] = 'Standard'\nprint(df['plan'].value_counts().sort_index().to_dict())",
             "isin(['Basic'])", "isin(['Basic', 'Silver'])", compare=['df']),
        make('onehot', '입력 범주만 원핫 인코딩해요',
             '범주를 종류별 열로 바꾸면 숫자 입력이 돼요.',
             'region과 plan을 모두 변환하세요.\n타깃 churn은 변환하지 않아요.',
             MEMBERS + "# 입력용 문자 열만 변환해요.\nencoded = pd.get_dummies(df, columns=['region'], dtype=int)\nprint(encoded.columns.tolist())",
             "columns=['region']", "columns=['region', 'plan']", compare=['encoded']),
        make('reset', '지운 행 번호를 다시 붙여요',
             'drop=True면 예전 행 번호를 열로 남기지 않아요.',
             '결측 행을 지운 뒤 행 번호를 다시 붙여요.\n예전 번호 열이 생기지 않게 고치세요.',
             MEMBERS + "# 원본 번호를 새 입력 열로 남기지 않아요.\nclean = df.dropna().reset_index(drop=False)\nprint(clean.columns.tolist())\nprint(clean.index.tolist())",
             'drop=False', 'drop=True', compare=['clean']),
        make('target', '새 타깃 이름으로 입력을 나눠요',
             '입력에서는 식별자와 정답을 함께 빼요.',
             '입력에서 member_id와 churn을 빼세요.\ny에는 churn을 그대로 남겨요.',
             MEMBERS + "# 식별 번호를 예측 입력으로 쓰지 않아요.\nX = df.drop(columns=['member_id'])\ny = df['churn']\nprint(X.columns.tolist())\nprint(y.head(4).tolist())",
             "columns=['member_id']", "columns=['member_id', 'churn']", compare=['X', 'y']),
        make('pipeline', '도전 · 전처리와 분리를 연결해요',
             '자료를 정리한 뒤 입력과 정답을 함께 나눠요.',
             '누수 열을 입력에서 빼세요.\n검증 25%, 난수 7, 비율 유지 조건은 준비돼요.',
             MEMBERS + "# 결측 제거와 문자 변환은 준비돼 있어요.\nclean = df.dropna()\nencoded = pd.get_dummies(clean, columns=['region', 'plan'], dtype=int)\n# 정답 열을 입력에서 빼는 줄을 고쳐요.\nX = encoded.drop(columns=['member_id'])\ny = encoded['churn']\nX_train, X_valid, y_train, y_valid = train_test_split(X, y, test_size=0.25, random_state=7, stratify=y)\nprint(X_valid.columns.tolist())\nprint(X_valid.index.tolist())",
             "columns=['member_id']", "columns=['member_id', 'churn']",
             compare=['X_train', 'X_valid', 'y_train', 'y_valid'], challenge=True),
    ]))
    return result
