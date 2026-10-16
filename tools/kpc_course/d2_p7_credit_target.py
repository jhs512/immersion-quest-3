"""부도 정의와 연체 이력"""
from kpc_course.dsl import *

UNIT = unit('credit-target', '부도 정의와 연체 이력', [
    concept('credit-definition', '지난달 연체와 다음 달 부도는 다른 칸이다',
        body="""
        자, 타이타닉으로 분류의 흐름을 익혔죠? 이번엔 금융 자료에 옮겨 봐요. `data/credit.csv`는 신용카드 고객 3만 명의 기록이에요. 한 사람이 한 행이고요. 맞힐 칸은 `다음달 부도`, **다음 달에 카드 대금을 못 갚는지**예요. 1이면 부도, 0이면 정상 상환이에요. 열 이름에 공백이 있어서 점으로는 못 불러요. 그래서 준비 코드가 `target` 변수에 이름을 담아 뒀어요. `credit[target]`으로 꺼내면 돼요.

        ```comic-gen
        제목: 아는 것과 맞힐 것
        등장인물:
          준호:
            그림: 사람
            이름표: 준호 · 은행 직원
            외형: {머리색: "#303746", 옷색: "#b88646"}
          강사:
            그림: 사람
            이름표: 강사
            외형: {옷: 재킷, 옷색: "#5379a7", 안경: true}
        컷:
          - 인물: [준호, 강사]
            대사:
              - {화자: 준호, 상대: 강사, 내용: "지난달 연체 기록을 입력에 넣어도 돼요?"}
              - {화자: 강사, 상대: 준호, 내용: "네. 지금 알고 있는 과거니까요."}
          - 구성: 이전
            인물: [{식별자: 준호, 표정: 기쁨}, {식별자: 강사, 손모양: 가리키는손}]
            대사:
              - {화자: 준호, 상대: 강사, 내용: "맞힐 건 다음 달 부도고요."}
              - {화자: 강사, 상대: 준호, 내용: "그 칸만 타깃이에요. 다음 달 값은 아직 몰라요."}
        ```

        입력 열은 타이타닉보다 많아요. `신용한도`와 `나이`는 이름 그대로예요. `성별`·`학력`·`결혼`은 **숫자 코드**로 적혀 있고요. 숫자라고 크기가 있는 건 아니에요. 성별 2가 1보다 "큰" 게 아니죠? 이런 열은 숫자처럼 보이는 글자 열이에요. `고객번호`는 사람을 구별하는 번호일 뿐이에요. 규칙을 찾을 재료가 못 되니 입력에서 빼요.

        가장 중요한 열은 상환 상태 `상환_9월`, `상환_8월` … `상환_4월`이에요. `상환_9월`이 가장 최근 달이죠. 월 번호가 작아질수록 더 전의 달이고요. 값의 뜻은 이 표예요.

        | 값 | 뜻 |
        | ---: | --- |
        | -2 | 쓴 돈이 없음 |
        | -1 | 제때 전액 상환 |
        | 0 | 최소 금액만 상환 |
        | 1 | 1개월 연체 |
        | 2 | 2개월 연체 |
        | 3~8 | 그만큼 연체 |

        여기서 선을 하나 그어요. `상환_9월`은 **지난달까지의 기록**이에요. `target`은 **다음 달의 결과**고요. 둘은 비슷해 보여도 시점이 달라요. 과거 연체 기록으로 미래 부도를 맞히는 게 이 문제예요. 그래서 `상환_9월`은 입력에 넣어도 누수가 아니에요. 다음 달 결과를 적은 열은 `target` 하나뿐이에요.

        ```comic-gen
        제목: 지난달과 다음 달
        등장인물:
          준호:
            그림: 사람
            이름표: 준호 · 은행 직원
            외형: {머리색: "#303746", 옷색: "#b88646"}
          강사:
            그림: 사람
            이름표: 강사
            외형: {옷: 재킷, 옷색: "#5379a7", 안경: true}
        컷:
          - 인물: [{식별자: 준호, 표정: 어리둥절}, 강사]
            대사:
              - {화자: 준호, 상대: 강사, 내용: "지난달에 연체했으면 그게 부도 아니에요?"}
              - {화자: 강사, 상대: 준호, 내용: "지난달 연체는 이미 아는 기록이고, 맞히려는 건 다음 달 결과예요."}
          - 구성: 이전
            인물: [{식별자: 준호, 표정: 기쁨}, {식별자: 강사, 손모양: 가리키는손}]
            대사:
              - {화자: 강사, 상대: 준호, 내용: "상환_9월은 입력, 다음달 부도는 정답. 시점이 다른 두 칸이에요."}
              - {화자: 준호, 상대: 강사, 내용: "과거 기록으로 미래를 맞히는 거네요."}
        ```

        ```python
        credit[target].value_counts()  # 부도·정상 인원
        credit.groupby('상환_9월')[target].agg(['count', 'mean'])  # 상환 상태별 인원과 부도율
        ```

        이 단원은 타이타닉에서 한 탐색 그대로예요. 몇 명인지, 부도가 몇 명인지, 어떤 그룹에서 부도율이 높은지 봐요. 도구는 전부 이미 배운 거예요. 자료만 바뀌죠. 그룹 인원이 몇 명인지 함께 보는 습관도 그대로 가져와요.
        """,
        check=short('이 자료의 타깃 `다음달 부도`에서 다음 달 부도를 나타내는 값은 무엇인가요?', ['1'],
                    '1이 부도, 0이 정상 상환이에요. 0과 1뿐이라 타깃의 평균이 곧 부도율이죠.')),
    coding('credit-shape', '신용카드 자료 살펴보기',
        goal="""
        자, 새 자료는 뼈대부터 봐요. `credit`의 행 수와 열 수를 `n_rows, n_columns`에 나눠 담으세요. `credit[target].value_counts()`로 `target_counts`도 만들어 두세요. 둘 다 출력하세요.

        3만 명, 25열이에요. 부도(1)보다 정상(0)이 훨씬 많아요. 확인해 보세요.
        """,
        hint="""
        크기는 `n_rows, n_columns = credit.shape`예요. 인원은 `credit[target].value_counts()`고요. 열 이름에 공백이 있어서 `credit[target]`처럼 변수로 꺼내야 해요.
        """,
        starter=CR + "# n_rows, n_columns, target_counts를 만들고 출력하세요\n",
        solution=CR + "n_rows, n_columns = credit.shape\ntarget_counts = credit[target].value_counts()\nprint(n_rows, n_columns)\nprint(target_counts)\n",
        check="assert s['n_rows'] == 30000 and s['n_columns'] == 25\nassert s['target_counts'][1] == 6636 and s['target_counts'][0] == 23364"),
    coding('default-summary', '부도 인원과 부도율, 그리고 입력 표',
        goal="""
        부도 인원은 `default_count`에 담으세요. 부도율은 `default_rate`에 담고요. 그리고 `고객번호`와 타깃 열을 뺀 입력 표를 `X`에 만드세요. 세 값을 출력하세요.

        부도율은 0과 1의 평균이라 20% 근처가 나와요. `X`는 23열이고요.
        """,
        hint="""
        타깃이 0과 1이라 `credit[target].sum()`이 부도 인원이에요. `credit[target].mean()`은 부도율이고요. `X = credit.drop(columns=['고객번호', target])`로 두 열을 빼요.
        """,
        starter=CR + "# default_count, default_rate, X를 만드세요\n",
        solution=CR + "default_count = int(credit[target].sum())\ndefault_rate = credit[target].mean()\nX = credit.drop(columns=['고객번호', target])\nprint(default_count, f'{default_rate:.2%}', X.shape)\n",
        check="assert s['default_count'] == 6636 and abs(s['default_rate'] - 0.2212) < 1e-10\nassert s['X'].shape == (30000, 23) and '고객번호' not in s['X'] and s['target'] not in s['X']"),
    coding('limit-by-default', '부도 여부별 평균 신용 한도',
        goal="""
        타이타닉에서 쓴 `groupby`를 금융 자료에 그대로 써요. 타깃으로 묶어 `신용한도`의 평균을 구하세요. `limit_by_default`에 담고 출력하세요.

        부도 그룹과 정상 그룹의 평균 한도가 어느 쪽이 높은지 보세요.
        """,
        hint="""
        `credit.groupby(target)['신용한도'].mean()`이에요. 타이타닉에서 `groupby('성별')['생존'].mean()`을 한 것과 같은 모양이죠. 묶는 열과 평균 낼 열만 달라요.
        """,
        starter=CR + "# limit_by_default를 만들고 출력하세요\n",
        solution=CR + "limit_by_default = credit.groupby(target)['신용한도'].mean()\nprint(limit_by_default)\n",
        check="assert set(s['limit_by_default'].index) == {0, 1}\nassert s['limit_by_default'][0] > s['limit_by_default'][1]\nassert abs(s['limit_by_default'][1] - 130109.65642) < 0.01"),
    coding('rate-by-attribute', '성별·학력·나이대별 부도율',
        goal="""
        고객 속성마다 부도율이 얼마나 다른지 봐요. `성별`과 `학력`은 코드 그대로 묶으세요. 타깃의 평균을 `rate_by_sex`, `rate_by_education`에 담으면 돼요. `나이`는 `pd.cut`으로 새 열 `나이대`를 만드세요. 다섯 구간은 20대, 30대, 40대, 50대, 60대 이상이에요. 그걸로 묶어 `rate_by_age`에 담으세요. 셋을 출력하세요.

        구간은 `bins = [20, 30, 40, 50, 60, 80]`, `right=False`, `labels = ['20대', '30대', '40대', '50대', '60대 이상']`이에요. 속성 사이의 차이를 기억해 두세요. 다음 미션에서 연체 이력 차이와 견줘요.
        """,
        hint="""
        `credit.groupby('성별')[target].mean()`을 세 번, 묶는 열만 바꿔요. 나이는 먼저 `credit['나이대'] = pd.cut(credit['나이'], bins=..., right=False, labels=...)`로 구간 열을 만들어요. 그다음 `groupby('나이대', observed=True)`로 묶어요. `observed=True`는 빈 구간을 빼라는 뜻이에요.
        """,
        starter=CR + "# rate_by_sex, rate_by_education, rate_by_age를 만들고 출력하세요\n",
        solution=CR + "rate_by_sex = credit.groupby('성별')[target].mean()\nrate_by_education = credit.groupby('학력')[target].mean()\ncredit['나이대'] = pd.cut(credit['나이'], bins=[20, 30, 40, 50, 60, 80], right=False, labels=['20대', '30대', '40대', '50대', '60대 이상'])\nrate_by_age = credit.groupby('나이대', observed=True)[target].mean()\nprint(rate_by_sex)\nprint(rate_by_education)\nprint(rate_by_age)\n",
        check="assert set(s['rate_by_sex'].index) == {1, 2}\nassert abs(s['rate_by_sex'].loc[1] - 0.2417) < 0.001\nassert len(s['rate_by_education']) == 7\nassert list(s['rate_by_age'].index) == ['20대', '30대', '40대', '50대', '60대 이상']\nassert abs(s['rate_by_age'].loc['60대 이상'] - 0.2832) < 0.001"),
    coding('delay-groups', '한 번이라도 연체한 적이 있는가',
        goal="""
        여섯 달 중 한 번이라도 연체한 적이 있는지를 새 열 `has_delay`로 만들어요. 연체는 값 1 이상이에요. `pay_columns` 여섯 열에 `>= 1` 조건을 거세요. 그다음 `.any(axis=1)`로 행마다 "하나라도 참인가"를 구해요. 그 결과를 `credit['has_delay']`에 넣으면 돼요. 이어서 `has_delay`로 묶으세요. 타깃의 `count`, `sum`, `mean`을 `summary`에 담고요.

        연체 경험이 있는 그룹과 없는 그룹의 부도율 차이를 보세요.
        """,
        hint="""
        `(credit[pay_columns] >= 1)`은 여섯 열 전부에 참·거짓을 매긴 표예요. `.any(axis=1)`은 행마다 그중 하나라도 참이면 참이고요. `credit.groupby('has_delay')[target].agg(['count', 'sum', 'mean'])`으로 마무리하세요.
        """,
        starter=CR + "pay_columns = ['상환_9월', '상환_8월', '상환_7월', '상환_6월', '상환_5월', '상환_4월']\n# has_delay와 summary를 만드세요\n",
        solution=CR + "pay_columns = ['상환_9월', '상환_8월', '상환_7월', '상환_6월', '상환_5월', '상환_4월']\ncredit['has_delay'] = (credit[pay_columns] >= 1).any(axis=1)\nsummary = credit.groupby('has_delay')[target].agg(['count', 'sum', 'mean'])\nsummary\n",
        check="assert s['summary']['count'].sum() == 30000 and s['summary']['sum'].sum() == 6636\nassert set(s['summary'].index) == {False, True}\nassert s['credit']['has_delay'].equals((s['credit'][['상환_9월', '상환_8월', '상환_7월', '상환_6월', '상환_5월', '상환_4월']] >= 1).any(axis=1))"),
    coding('pay0-rate', '최근 상환 상태별 부도율',
        goal="""
        가장 최근 달의 상환 상태 `상환_9월`로 묶으세요. 타깃의 `count`와 `mean`을 `pay0_summary`에 담으면 돼요. 그중 두 칸을 꺼내요. 상태 0(최소 금액 상환)의 부도율은 `rate_0`, 상태 2(2개월 연체)의 부도율은 `rate_2`예요. 둘 다 출력하세요.

        연체 상태의 부도율이 몇 배나 높은지 보세요. 인원이 몇 명 안 되는 상태의 비율은 믿을 만할까요? `count`와 함께 읽어 보세요.
        """,
        hint="""
        `pay0_summary = credit.groupby('상환_9월')[target].agg(['count', 'mean'])`이에요. 표에서 한 칸은 `pay0_summary.loc[0, 'mean']`처럼 꺼내요.
        """,
        starter=CR + "# pay0_summary, rate_0, rate_2를 만들고 출력하세요\n",
        solution=CR + "pay0_summary = credit.groupby('상환_9월')[target].agg(['count', 'mean'])\nrate_0 = pay0_summary.loc[0, 'mean']\nrate_2 = pay0_summary.loc[2, 'mean']\nprint(pay0_summary)\nprint(rate_0, rate_2)\n",
        check="assert s['pay0_summary']['count'].sum() == 30000\nassert s['rate_2'] > s['rate_0']\nassert abs(s['rate_0'] - 0.128113) < 1e-5 and abs(s['rate_2'] - 0.691414) < 1e-5"),
    quiz('credit-check', '단원 점검',
        choice('`상환_9월`을 입력에 넣어도 누수가 아닌 이유는 무엇인가요?',
               ['지난달까지의 기록이라 다음 달 부도를 맞히는 시점에 알 수 있다', '숫자라서', '값이 작아서'], 0,
               '누수는 맞히는 시점에 알 수 없는 정보예요. 지난달 연체 기록은 이미 아는 과거고요. 다음 달 결과만 타깃이에요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「숫자라서」: 자료형은 누수와 상관없어요.\n- 「값이 작아서」: 크기도 상관없어요. 시점이 기준이에요."),
        choice('`성별`이 1과 2로 적혀 있다고 해서 숫자 크기로 다루면 어떤 문제가 생기나요?',
               ['2가 1보다 "크다"는 없는 의미를 모델이 배울 수 있다', '아무 문제 없다', '오류가 나서 실행이 안 된다'], 0,
               '성별 코드는 이름표예요. 크기가 아니에요. 이런 열은 글자 열처럼 One-hot으로 다루는 게 안전해요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「오류가 난다」: 실행은 되지만 잘못 배워요.\n- 「아무 문제 없다」: 2가 1보다 크다는 없는 규칙을 배워요."),
        short('가장 최근 달의 상환 상태를 담은 열 이름은 무엇인가요?', ['상환_9월'],
              '`상환_9월`이 최근 달이에요. `상환_8월`부터 `상환_4월`이 그 전 달들이고요.'),
        choice('`상환_9월`이 7인 그룹의 부도율이 78%로 나왔어요. 이 숫자를 조심해서 읽어야 하는 이유는 무엇인가요?',
               ['그 그룹이 9명뿐이라 한두 명으로 비율이 크게 흔들린다', '7은 큰 숫자라서', '78%는 100%가 아니라서'], 0,
               '분모가 작은 비율은 우연에 흔들려요. 앞서 배운 "몇 명 중"이 여기서도 그대로예요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「7은 큰 숫자라서」: 코드 값의 크기는 뜻이 없어요.\n- 「100%가 아니라서」: 비율의 크기가 아니라 분모가 문제예요."),
        choice("`(credit[pay_columns] >= 1).any(axis=1)`은 무엇을 돌려주나요?",
               ['행마다 여섯 달 중 하나라도 연체면 참, 아니면 거짓', '열마다 연체 인원', '여섯 달의 평균'], 0,
               '`axis=1`은 "행 방향으로"예요. 한 행의 여섯 값 중 하나라도 참이면 그 행은 참이에요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「열마다 연체 인원」: 그건 axis=0 방향의 sum()이에요.\n- 「여섯 달의 평균」: any()는 참·거짓만 돌려줘요."),
        short('타깃의 열 이름에는 공백이 있어요. 그래서 준비 코드가 이름을 변수에 담아 뒀죠. 그 변수는 무엇인가요? (`credit[______]`)', ['target'],
              "`target = '다음달 부도'`예요. 그래서 `credit[target]`으로 꺼내요."),
        choice("""**프롬프트 고르기** · 신용카드 자료에서 입력 표 `X`를 만들어야 해요. 고객 번호는 어떻게 할지까지 적은 프롬프트는 무엇인가요?""",
               ["""pandas. credit DataFrame, target = '다음달 부도'. 부도 인원 default_count, 부도율(타깃 평균) default_rate, 고객번호와 target 열을 drop한 입력 표 X를 만들어 출력. 코드만""", """신용카드 자료로 X 만들어 줘""", """타깃만 빼고 전부 입력으로 써 줘""", """부도 예측 준비해 줘"""], 0,
               """정답은 타깃 열 이름을 변수로 넘겼어요. 고객번호를 빼는 판단도 적었고요. 식별자는 재료가 아니니까요. 결과 변수 세 개도 적었어요.

**다른 보기는 왜 아닌가**

- 「X 만들어 줘」: 고객번호가 들어가요.
- 「타깃만 빼고 전부」: 역시 고객번호가 들어가 번호를 외워요.
- 「준비해 줘」: 무엇을 준비할지 없어요."""),
        choice("""**프롬프트 고르기** · 여섯 달 중 한 번이라도 연체한 고객을 표시하는 열을 만들려고 해요. 그걸로 부도율을 비교하고요. 어떤 프롬프트가 한 줄짜리 벡터 연산을 줄까요?""",
               ["""pandas. pay_columns 여섯 열에 대해 (credit[pay_columns] >= 1).any(axis=1)을 credit['has_delay']에 넣고, has_delay로 groupby한 target의 count·sum·mean을 summary에. 코드만""", """연체한 사람 찾아 줘""", """for로 한 명씩 돌면서 연체 여부 확인해 줘""", """연체 경험이랑 부도율 관계 알려 줘"""], 0,
               """정답은 조건을 코드 한 줄로 적었어요(any(axis=1)). 말로만 풀면 AI는 느린 반복문을 짜요.

**다른 보기는 왜 아닌가**

- 「연체한 사람 찾아 줘」: 어느 열, 어떤 조건인지 없어요.
- 「for로 한 명씩」: 3만 행을 반복문으로 돌리는 틀린 지시예요.
- 「관계 알려 줘」: 설명만 오고 열과 표는 안 생겨요."""),
    ),
])
