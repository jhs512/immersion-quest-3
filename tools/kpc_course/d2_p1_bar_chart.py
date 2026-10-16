"""Figure·Axes와 막대그래프"""
from kpc_course.dsl import *

UNIT = unit('bar-chart', 'Figure·Axes와 막대그래프', [
    concept('axes', '종이 한 장과 그 위의 그래프',
        body="""
        자, 앞 단원에서 성별 생존율 표를 만들었죠. 숫자 둘을 비교할 땐 표로 충분해요. 그런데 그룹이 넷, 여섯이 되면 눈이 숫자를 못 따라가거든요. 그래서 이제 표를 그래프로 바꿔요. 이 챕터는 그래프로 시작해요. 다음 챕터에선 "누가 살아남았나"를 맞히는 모델로 이어지고요.

        ```comic-gen
        제목: 종이와 그래프 영역
        등장인물:
          민지:
            그림: 사람
            이름표: 민지
            외형: {머리모양: 단발, 머리색: "#573d36", 옷: 후드, 옷색: "#609b87"}
          강사:
            그림: 사람
            이름표: 강사
            외형: {옷: 재킷, 옷색: "#5379a7", 안경: true}
        컷:
          - 인물: [{식별자: 민지, 표정: 어리둥절}, 강사]
            대사:
              - {화자: 민지, 상대: 강사, 내용: "fig랑 ax, 둘 다 그림 아니에요?"}
              - 화자: 강사
                상대: 민지
                내용: |-
                  fig는 종이, ax는 그 위의
                  그래프 영역이에요.
          - 구성: 이전
            인물: [{식별자: 민지, 표정: 기쁨}, {식별자: 강사, 손모양: 가리키는손}]
            대사:
              - {화자: 민지, 상대: 강사, 내용: "그래서 막대는 ax.bar로 그리는구나."}
              - {화자: 강사, 상대: 민지, 내용: "축 이름도 ax에 붙여요. 종이에는 안 그려요."}
        ```

        파이썬에서 그래프를 그리는 도구는 `matplotlib`이에요. 처음 보면 낯선 단어가 둘 나와요. 비유 하나면 돼요. `Figure`는 **종이 한 장**이에요. `Axes`는 그 종이 위에 그리는 **그래프 영역 하나**고요. 종이 한 장에 그래프를 하나만 그릴 수도, 여럿 그릴 수도 있죠. 우리는 거의 항상 하나만 그려요. 그래서 시작은 늘 같은 한 줄이에요.

        ```python
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()  # 종이(fig) 한 장, 그래프 영역(ax) 하나
        ax.bar(['A', 'B', 'C'], [30000, 40000, 60000])  # 막대 그리기
        ax.set(title='종목별 금액', ylabel='금액')  # 제목과 축 이름
        plt.show()  # 앱 화면에 표시
        ```

        그리는 명령은 종이가 아니라 **그래프 영역 `ax`**에 붙여요. `ax.bar(이름들, 값들)`가 막대그래프예요. `ax.set(...)`은 제목·축 이름·축 범위를 정하고요. 마지막 `plt.show()`가 "다 그렸으니 보여 줘"예요. 이 네 줄이 이 챕터 모든 그래프의 뼈대예요.

        그래프를 그리기 전에 두 가지를 정해 두세요. 그러면 그래프가 흔들리지 않아요. 첫째, **y축이 무엇인가.** 인원인지 비율인지 퍼센트인지에 따라 같은 그래프가 다른 말을 해요. 생존율처럼 0~1 사이 비율은 100을 곱해 퍼센트로 그려요. y축 범위도 `ylim = (0, 100)`으로 고정하면 읽기 쉽고요.

        둘째, **축을 어디서 시작하는가.** y축을 0이 아니라 60부터 자르면요? 62%와 70%가 몇 배 차이처럼 보여요. 과장하려는 뜻이 없어도 그렇게 읽히거든요. 비율 막대는 0부터 그리세요.

        축 이름과 제목은 한글로 적어도 돼요. 이 앱의 실행 환경이 한글 글꼴을 미리 골라 두거든요.
        """,
        check=short('`matplotlib`에서 종이 한 장, 그러니까 전체 그림을 뭐라고 부르죠? (`fig, ax = plt.subplots()`의 `fig`)', ['Figure', 'figure', '피겨'],
                    '`Figure`가 종이 한 장, `Axes`가 그 위의 그래프 영역이에요. 막대나 선은 `ax`에 그려요.')),
    coding('simple-bar', '리스트로 첫 막대그래프',
        goal="""
        앞서 만든 종목 세 개의 금액으로 첫 막대그래프를 그려요. `fig, ax = plt.subplots()`로 종이와 그래프 영역을 만드세요. `ax.bar(names, amounts)`로 막대를 그려요. `ax.set(title='종목별 금액', ylabel='금액')`로 제목과 y축 이름을 붙이고요. 마지막에 `plt.show()`로 띄우세요.

        막대 세 개가 30000, 40000, 60000 높이로 서면 맞게 한 거예요.
        """,
        hint="""
        개념의 네 줄 그대로예요. 순서는 `subplots` → `bar` → `set` → `show`. `ax.set()`의 괄호 안에 `title=`, `ylabel=`을 쉼표로 나란히 적어요.
        """,
        starter="import matplotlib.pyplot as plt\n\nnames = ['A', 'B', 'C']\namounts = [30000, 40000, 60000]\n# fig, ax를 만들고 막대그래프를 그리세요\n",
        solution="import matplotlib.pyplot as plt\n\nnames = ['A', 'B', 'C']\namounts = [30000, 40000, 60000]\nfig, ax = plt.subplots()\nax.bar(names, amounts)\nax.set(title='종목별 금액', ylabel='금액')\nplt.show()\n",
        check="assert len(s['ax'].patches) == 3\nassert [p.get_height() for p in s['ax'].patches] == [30000, 40000, 60000]\nassert s['ax'].get_ylabel() == '금액'"),
    coding('sex-bar', '성별 생존율을 퍼센트로 그리기',
        goal="""
        앞 단원의 성별 생존율 표를 그래프로 바꿔요. `rates`에 성별 `생존` 평균을 담으세요. `rates * 100`을 막대로 그리세요. y축 범위는 `ylim = (0, 100)`이에요. x축 이름은 `성별`, y축 이름은 `생존율 (%)`로 하세요. 그리고 `plt.show()`로 띄우세요.

        막대 둘이 여성·남성 생존율 퍼센트 높이로 서면 맞게 한 거예요.
        """,
        hint="""
        `rates = titanic.groupby('성별')['생존'].mean()`은 앞 단원과 같아요. `ax.bar(rates.index, rates * 100)`로 그려요. 그다음 `ax.set(xlabel='성별', ylabel='생존율 (%)', ylim=(0, 100), title='성별 생존율')`로 꾸미세요.
        """,
        starter=TI + PLOT + "# rates, fig, ax를 만들고 막대그래프를 그리세요\n",
        solution=TI + PLOT + "rates = titanic.groupby('성별')['생존'].mean()\nfig, ax = plt.subplots()\nax.bar(rates.index, rates * 100)\nax.set(xlabel='성별', ylabel='생존율 (%)', ylim=(0, 100), title='성별 생존율')\nplt.show()\n",
        check="assert len(s['ax'].patches) == 2\nassert s['ax'].get_ylim() == (0.0, 100.0)\nassert s['ax'].get_ylabel() == '생존율 (%)'\nassert s['ax'].get_xlabel() == '성별'\nheights = {label.get_text(): bar.get_height() for label, bar in zip(s['ax'].get_xticklabels(), s['ax'].patches)}\nassert set(heights) == {'여성', '남성'}\nassert abs(heights['여성'] - 339 / 466 * 100) < 1e-8\nassert abs(heights['남성'] - 161 / 843 * 100) < 1e-8"),
    coding('pclass-bar', '등급별 생존율 막대그래프',
        goal="""
        같은 그래프를 객실 등급으로 그려요. `rates`에 등급별 `생존` 평균을 담으세요. `rates * 100`을 막대로 그리세요. y축 범위는 0~100, x축 이름은 `객실등급`, y축 이름은 `생존율 (%)`예요.

        막대 세 개가 1등급에서 3등급으로 갈수록 낮아지는지 보세요.
        """,
        hint="""
        성별 그래프에서 `groupby('성별')`를 `groupby('객실등급')`로 바꾸면 돼요. 등급 1·2·3은 숫자라 x축 간격이 어색할 수 있어요. `ax.bar(rates.index.astype(str), rates * 100)`처럼 글자로 바꿔 넘기세요.
        """,
        starter=TI + PLOT + "# rates, fig, ax를 만들고 막대그래프를 그리세요\n",
        solution=TI + PLOT + "rates = titanic.groupby('객실등급')['생존'].mean()\nfig, ax = plt.subplots()\nax.bar(rates.index.astype(str), rates * 100)\nax.set(xlabel='객실등급', ylabel='생존율 (%)', ylim=(0, 100), title='Survival by class')\nplt.show()\n",
        check="assert len(s['ax'].patches) == 3\nassert s['ax'].get_ylim() == (0.0, 100.0) and s['ax'].get_xlabel() == '객실등급'\nheights = sorted(p.get_height() for p in s['ax'].patches)\nassert abs(heights[0] - 181 / 709 * 100) < 1e-8 and abs(heights[2] - 200 / 323 * 100) < 1e-8"),
    quiz('bar-check', '단원 점검',
        short('종이 위에서 실제로 그래프가 그려지는 영역이 있죠. `fig, ax = plt.subplots()`의 `ax`예요. 이걸 뭐라고 부르나요?', ['Axes', 'axes', '축 영역'],
              '`Axes`가 그래프 영역이에요. 막대·선·축 이름은 전부 `ax`에 붙여요.'),
        choice('`fig, ax = plt.subplots()` 다음에 막대를 그리는 명령은 어느 것인가요?',
               ['`ax.bar(...)`', '`fig.bar(...)`', '`plt.subplots.bar(...)`'], 0,
               '그리는 명령은 그래프 영역 `ax`에 붙여요. `fig`는 종이라서 거기엔 막대를 안 그려요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「plt.subplots.bar」: subplots는 함수라 그런 메서드가 없어요.\n- 「fig.bar」: Figure는 종이예요. 그리는 메서드는 Axes에 있어요."),
        choice('생존율 0.4를 퍼센트 막대로 그리려면 어떤 값을 넘기나요?',
               ['`0.4 * 100`, 즉 40', '`0.4` 그대로', '`0.4 / 100`'], 0,
               '비율에 100을 곱하면 퍼센트예요. y축 범위도 0~100으로 맞춰야 막대 높이가 퍼센트로 읽혀요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「0.4 그대로」: 축이 0~100이면 막대가 거의 안 보여요.\n- 「0.4 / 100」: 0.004가 돼서 뜻이 없어요."),
        choice('y축을 0이 아니라 60부터 시작하도록 자르면 어떤 일이 생기나요?',
               ['작은 차이가 크게 보여 과장된다', '그림이 더 정확해진다', '막대가 사라진다'], 0,
               '62%와 70% 막대의 높이 차이가 몇 배로 보여요. 비율 막대는 0부터 그려야 안전해요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「더 정확해진다」: 값은 같은데 보이는 차이만 커져요.\n- 「막대가 사라진다」: 60 아래 막대만 잘릴 뿐 사라지진 않아요."),
        short('다 그린 그래프를 앱 화면에 띄우는 마지막 명령은 무엇인가요?', ['plt.show()', 'plt.show', 'show()'],
              '`plt.show()`가 "보여 줘"예요. 이 줄이 없으면 그래프가 화면에 안 나와요.'),
        choice('막대그래프를 보고 "여성 생존율이 두 배 높다"고 말하려 해요. 그 전에 먼저 확인할 것은 무엇인가요?',
               ['y축이 퍼센트인지 인원인지, 그리고 각 그룹이 몇 명인지', '막대 색이 예쁜지', '제목이 영어인지'], 0,
               '같은 높이 차이도 y축 단위에 따라 뜻이 달라요. 분모가 작은 그룹은 비율이 흔들리고요. 앞서 배운 "몇 명 중"이 그래프에서도 그대로 통해요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「제목이 영어인지」: 언어는 해석과 무관해요.\n- 「막대 색」: 색은 비율을 안 바꿔요."),
        choice("""**프롬프트 고르기** · 성별 생존율을 퍼센트 막대그래프로 그려야 해요. 검사기는 `ax` 객체를 읽고요. 어떤 프롬프트가 맞을까요?""",
               ["""pandas + matplotlib. titanic DataFrame. groupby('성별')['생존'].mean()을 rates에 담고 rates*100을 ax.bar로 그려. ylim=(0,100), xlabel '성별', ylabel '생존율 (%)'. fig, ax = plt.subplots() 방식, plt.show(). 코드만""", """성별 생존율 그래프 그려 줘""", """plt.bar로 막대그래프 하나 그려 줘""", """seaborn으로 예쁜 그래프 만들어 줘"""], 0,
               """정답엔 집계, 퍼센트 변환, 축 범위, 축 이름이 다 있어요. "fig, ax 방식"도 적었고요. 검사기가 ax를 읽으니까 방식이 중요해요.

**다른 보기는 왜 아닌가**

- 「그래프 그려 줘」: 종류·단위·축 모두 AI 마음대로예요.
- 「plt.bar로」: ax 객체가 없어서 검사기가 그래프를 못 찾아요.
- 「예쁜 그래프」: 예쁨은 검사 조건이 아니에요."""),
        choice("""**프롬프트 고르기** · 막대그래프 y축이 60부터 시작해서 차이가 과장돼 보여요. AI에게 어떻게 고쳐 달라고 해야 할까요?""",
               ["""y축이 60부터 시작해 비율 차이가 과장돼 보여. ax.set_ylim(0, 100)으로 0부터 그리게 고쳐 줘""", """그래프가 이상해""", """더 극적으로 보이게 해 줘""", """축 좀 손봐 줘"""], 0,
               """정답은 문제(과장), 원인(60부터), 원하는 수정(0~100)을 함께 적었어요. 비율 막대는 0부터 그리는 게 안전하니까요.

**다른 보기는 왜 아닌가**

- 「그래프가 이상해」: 무엇이 이상한지 없어요.
- 「더 극적으로」: 과장을 키우는 요청이에요.
- 「축 좀 손봐 줘」: 어느 축을 어떻게 바꿀지 없어요."""),
    ),
])
