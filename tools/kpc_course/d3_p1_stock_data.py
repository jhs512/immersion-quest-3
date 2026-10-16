"""주가 파일과 시점"""
from kpc_course.dsl import *

UNIT = unit('stock-data', '주가 파일과 시점', [
    concept('saved-prices', '오늘 저녁에 아는 것으로 내일을 맞힌다',
        body="""
        마지막 챕터예요. 지금까지 익힌 흐름을 주가에 그대로 써요. 자료 읽기, 입력과 정답 나누기, 훈련·테스트 나누기, 기준 모델과 비교하기, 이 넷이에요. 다른 점은 하나뿐이에요. 타이타닉의 정답은 "생존/사망" 중 하나를 **고르는** 분류였죠. 이번 정답은 "다음 거래일 종가"라는 **숫자**예요. 숫자를 맞히는 걸 회귀라고 해요. 점수를 재는 방법이 달라져요.

        자료는 `data/stock.csv`, 삼성전자의 하루치 주가 기록 401일분이에요. 열은 `날짜`, `시가`, `고가`, `저가`, `종가`, `거래량`, 그리고 수익률(어제 대비 변화율)인 `변화율`이에요. 날짜가 있는 표는 날짜를 행 이름(인덱스)으로 올려 두면 다루기 편해요. 그래서 준비 코드가 늘 이렇게 읽어요.

        ```python
        prices = pd.read_csv('data/stock.csv', parse_dates=['날짜']).set_index('날짜').sort_index()
        ```

        `parse_dates`는 글자를 날짜로 바꿔요. `set_index`는 날짜를 행 이름으로 올려요. `sort_index`는 날짜순으로 줄 세워요. 정렬이 왜 중요한지는 곧 나와요.

        예측하는 상황을 정확히 정해 둘게요. **오늘 장이 끝난 저녁**이에요. 오늘까지 가격은 전부 알아요. 그 상태에서 **다음 거래일의 종가**를 맞혀요. 왜 "다음 날"이 아니라 "다음 거래일"일까요? 주말과 휴장일에는 가격이 없거든요. 금요일 저녁의 정답은 토요일이 아니라 월요일 종가예요. 이 시점을 흐리면 앞서 배운 누수가 바로 생겨요. 내일 가격이 입력에 섞이는 순간, 모델은 답을 보고 답을 맞히게 돼요.

        빵 공장에 옮겨 보면 같은 그림이에요. 파리바게뜨 공장은 **새벽 3시**에 오늘 크루아상을 몇 개 구울지 정해야 해요. 그때 아는 건 요일, 어제와 지난주 같은 요일의 판매량이에요. 날씨 예보와 근처 학교 개학 여부도요. 모르는 건 **오늘 실제로 팔릴 개수**예요. 그 개수가 정답이고, 정답은 저녁에야 적혀요. "오늘 판매량"을 입력에 넣고 오늘 판매량을 맞히면 점수는 완벽해요. 그런데 새벽 3시에는 못 쓰는 모델이에요. 주가에서 내일 종가를 입력에 넣는 것과 똑같은 누수예요.

        ```comic-gen
        제목: 결정하는 시각에 아는 것만
        등장인물:
          공장장:
            그림: 사람
            이름표: 빵 공장장
            외형: {피부색: "#d6a279", 머리모양: 민머리, 옷색: "#8a6d4b"}
          민지:
            그림: 사람
            이름표: 민지 · 수강생
            외형: {머리모양: 단발, 옷: 후드, 옷색: "#4f8a8b"}
        컷:
          - 인물: [{식별자: 공장장, 표정: 보통}, 민지]
            대사:
              - {화자: 공장장, 상대: 민지, 내용: "새벽 3시에 오늘 몇 개 구울지 정해요."}
              - {화자: 민지, 상대: 공장장, 내용: "그 시각에 아는 건 요일, 어제 판매량, 날씨 예보 정도죠?"}
          - 구성: 이전
            인물: [{식별자: 공장장, 표정: 기쁨}, {식별자: 민지, 손모양: 가리키는손}]
            대사:
              - {화자: 민지, 상대: 공장장, 내용: "오늘 판매량은 저녁에나 아니까 입력에 못 넣어요."}
              - {화자: 공장장, 상대: 민지, 내용: "주가도 똑같네요. 오늘 저녁에 아는 걸로 내일을 맞히는 거."}
        ```

        ```comic-gen
        제목: 새벽 3시의 결정
        등장인물:
          공장장:
            그림: 사람
            이름표: 빵 공장장
            외형: {피부색: "#d6a279", 머리모양: 민머리, 옷색: "#8a6d4b"}
          민지:
            그림: 사람
            이름표: 민지
            외형: {머리모양: 단발, 머리색: "#573d36", 옷: 후드, 옷색: "#609b87"}
        컷:
          - 인물: [{식별자: 공장장, 표정: 어리둥절}, 민지]
            대사:
              - 화자: 공장장
                상대: 민지
                내용: |-
                  새벽 3시에 오늘 몇 개 구울지
                  정해야 해요.
              - {화자: 민지, 상대: 공장장, 내용: "그때 아는 건 뭐예요?"}
          - 구성: 이전
            인물: [{식별자: 공장장, 표정: 보통}, {식별자: 민지, 손모양: 가리키는손}]
            대사:
              - {화자: 공장장, 상대: 민지, 내용: "요일, 어제 판매량, 날씨 예보 정도죠."}
              - 화자: 민지
                상대: 공장장
                내용: |-
                  그게 입력이고,
                  오늘 실제 판매량이 정답이에요.
          - 구성: 이전
            인물: [{식별자: 공장장, 표정: 기쁨}, {식별자: 민지, 손모양: null}]
            대사:
              - {화자: 공장장, 상대: 민지, 내용: "오늘 판매량을 넣으면 백발백중일 텐데?"}
              - 화자: 민지
                상대: 공장장
                내용: |-
                  저녁에야 아는 값이라 새벽엔 못 쓰죠.
                  그게 누수예요.
        ```

        한 가지 더. 이 수업은 **예측이 얼마나 빗나가는지를 재는 연습**이에요. 돈을 버는 방법이 아니에요. 모델이 기준보다 조금 낫게 나와도 그게 수익을 뜻하진 않아요. 결과를 투자 판단에 쓰지 마세요.
        """,
        check=short('오늘 저녁에 아는 가격으로 맞히려는 정답은 다음 거래일의 종가예요. 그 열 이름은 뭘까요?', ['종가', 'close'],
                    '`종가` 열의 다음 거래일 값이 정답이에요. 다음 날이 아니라 다음 거래일이에요. 그리고 그 값은 입력에 넣으면 안 돼요.')),
    concept('fetch-prices', '주가 파일은 어디서 오나: yfinance와 FinanceDataReader',
        body="""
        `data/stock.csv`는 하늘에서 떨어진 파일이 아니에요. 인터넷이 되는 컴퓨터에서는 두 줄이면 같은 표를 받아요. 도구는 둘 중 하나예요.

        ```python
        import yfinance as yf

        prices = yf.download('005930.KS', start='2025-01-01', end='2026-09-05')  # Open, High, Low, Close, Volume

        import FinanceDataReader as fdr

        prices = fdr.DataReader('005930', '2025-01-01', '2026-09-04')  # Open, High, Low, Close, Volume, Change
        ```

        **yfinance**는 야후 파이낸스에서 받아요. 종목 코드 뒤의 `.KS`는 코스피, `.KQ`는 코스닥이라는 뜻이에요. **FinanceDataReader**는 국내 종목 코드를 그대로 써요. 거래소 자료를 받고요. 둘 다 날짜가 인덱스인 표가 와요. 열은 시가·고가·저가·종가·거래량이에요. 우리 파일은 이렇게 받은 표의 열 이름을 한글로 바꿔 저장한 거예요. `변화율`은 FinanceDataReader의 `Change`, 그러니까 어제 대비 수익률이에요.

        받은 표를 바로 쓰지 않고 **저장해서 쓰는** 이유가 있어요. 수업 중엔 모두가 같은 숫자를 봐야 해요. 네트워크가 끊겨도 미션이 돌아야 하고요. 한 달 뒤 다시 돌려도 같은 결과가 나와야 해요(재현). 회사에서도 순서는 같아요. 받는 코드는 하루 한 번 돌려 파일로 저장해요. 분석 코드는 그 파일을 읽고요. 받기와 분석을 섞어 두면요? 어느 날 사이트가 바뀌면 분석까지 같이 멈춰요.

        ```python
        prices.to_csv('stock.csv')  # 받은 날 한 번
        prices = pd.read_csv('stock.csv', parse_dates=['Date']).set_index('Date')  # 분석할 때마다
        ```

        그래서 이 단원의 모든 미션은 `data/stock.csv`에서 시작해요. 받는 두 줄은 회사 컴퓨터에서 붙이면 돼요.
        """,
        check=short('야후 파이낸스에서 주가 표를 받아 오는 yfinance의 함수 이름은 뭘까요?', ['download', 'yf.download', 'yfinance.download', 'download()'],
                    '`yf.download(종목, start=, end=)`예요. FinanceDataReader는 `fdr.DataReader`고요. 받은 표는 저장해 두고, 분석은 저장 파일로 해요.')),
    coding('live-prices', '진짜 웹에서: 지금 이 순간의 삼성전자 주가',
        intro="""
        인터넷이 필요한 미션이에요. 저장 파일이 아니라 **지금** 시세를 받아 봐요. `FinanceDataReader`로 삼성전자(`005930`)를 올해 1월 1일부터 받으면 날짜가 인덱스인 표가 와요. 열은 `Open`, `High`, `Low`, `Close`, `Volume`, `Change`예요.
        """,
        goal="""
        `fdr.DataReader('005930', '2026-01-01')`로 받은 표를 날짜순으로 정렬해 `live`에 두세요. 마지막 종가를 정수로 `latest_close`에, 최근 5거래일 종가 평균을 `ma5`에 담으세요. 표 끝부분과 마지막 날짜, 두 값을 출력하세요.

        받는 날에 따라 숫자가 달라요. 그래서 검사는 값이 아니라 모양을 봐요. 날짜 인덱스, 20행 이상, 마지막 날짜가 2주 안, 그리고 두 값이 표와 맞는지요.
        """,
        hint="""
        `live = fdr.DataReader('005930', '2026-01-01').sort_index()`. 마지막 종가는 `live['Close'].iloc[-1]`, 5일 평균은 `live['Close'].rolling(5).mean().iloc[-1]`이에요. yfinance를 쓰고 싶으면 `yf.download('005930.KS', start='2026-01-01', auto_adjust=True, multi_level_index=False)`로 받으면 열 이름이 같은 모양이 돼요.
        """,
        starter="import pandas as pd\nimport FinanceDataReader as fdr\n# live, latest_close, ma5를 만드세요\n",
        solution="import pandas as pd\nimport FinanceDataReader as fdr\n\nlive = fdr.DataReader('005930', '2026-01-01').sort_index()\nlatest_close = int(live['Close'].iloc[-1])\nma5 = float(live['Close'].rolling(5).mean().iloc[-1])\nprint(live.tail())\nprint(live.index.max().date(), latest_close, round(ma5))\n",
        check="import pandas as pd\n\nassert isinstance(s['live'].index, pd.DatetimeIndex) and len(s['live']) >= 20\nassert 'Close' in s['live'].columns and (s['live']['Close'] > 0).all()\nassert s['live'].index.is_monotonic_increasing\nassert (pd.Timestamp.today() - s['live'].index.max()).days <= 14\nassert s['latest_close'] == int(s['live']['Close'].iloc[-1])\nassert abs(s['ma5'] - float(s['live']['Close'].rolling(5).mean().iloc[-1])) < 1e-6"),
    coding('stock-load', '날짜 순서와 크기 확인',
        goal="""
        주가 파일을 읽어 `prices`에 저장하세요. `날짜` 열은 글자가 아니라 날짜로 읽어 인덱스로 올리세요. 그리고 `sort_index()`로 정렬하세요. 행 수는 `n_rows`에 담으세요. 열 수는 `n_columns`에 담고요. 첫 날짜와 마지막 날짜도 출력하세요.

        401행 6열이고 날짜가 오름차순이면 맞게 읽은 거예요.
        """,
        hint="""
        개념의 한 줄을 그대로 쓰면 돼요. `pd.read_csv('data/stock.csv', parse_dates=['날짜']).set_index('날짜').sort_index()`예요. 날짜 범위는 `prices.index.min()`과 `prices.index.max()`로 구해요.
        """,
        starter='import pandas as pd\n# prices, n_rows, n_columns를 만드세요\n',
        solution=ST + "n_rows, n_columns = prices.shape\nprint(n_rows, n_columns)\nprint(prices.index.min(), prices.index.max())\nprices.head()\n",
        check="assert s['prices'].shape == (401, 6) and s['n_rows'] == 401 and s['n_columns'] == 6\nassert s['prices'].index.is_monotonic_increasing and not s['prices'].index.has_duplicates\nassert s['prices']['종가'].iloc[0] == 54100"),
    coding('close-plot', '종가를 선으로 그리기',
        goal="""
        날짜순 자료는 선그래프가 어울려요. `fig, ax`를 만드세요. `ax.plot(prices.index, prices['종가'])`로 종가를 선으로 그리세요. x축 이름 `날짜`, y축 이름 `종가`를 붙여 띄우세요.

        401개 점을 이은 선 하나가 보이면 맞게 그린 거예요. 1년 8개월 동안 가격이 어떻게 움직였는지 보세요.
        """,
        hint="""
        막대그래프의 뼈대에서 `ax.bar`를 `ax.plot`으로 바꾸면 돼요. x에는 날짜 인덱스 `prices.index`를 넣어요. y에는 `prices['종가']`를 넣고요.
        """,
        starter=ST + "import matplotlib.pyplot as plt\n# fig, ax를 만들고 종가를 그리세요\n",
        solution=ST + "import matplotlib.pyplot as plt\n\nfig, ax = plt.subplots()\nax.plot(prices.index, prices['종가'])\nax.set(xlabel='날짜', ylabel='종가', title='Close price')\nplt.show()\n",
        check="assert len(s['ax'].lines) == 1 and len(s['ax'].lines[0].get_ydata()) == 401\nassert s['ax'].get_ylabel() == '종가'"),
    coding('price-range', '기간과 최고 종가',
        goal="""
        자료의 첫 날짜와 마지막 날짜를 `first_date`, `last_date`에 담으세요. 가장 높았던 종가는 `max_close`에, 그 날짜는 `max_date`에 담으세요. 넷 다 출력하세요.

        최고 종가가 언제였는지 그래프와 맞춰 보세요.
        """,
        hint="""
        날짜 인덱스의 `.min()`과 `.max()`가 양 끝 날짜예요. 종가 열의 `.max()`는 값이에요. `.idxmax()`는 그 값이 있는 행 이름, 그러니까 날짜예요.
        """,
        starter=ST + "# first_date, last_date, max_close, max_date를 만들고 출력하세요\n",
        solution=ST + "first_date = prices.index.min()\nlast_date = prices.index.max()\nmax_close = prices['종가'].max()\nmax_date = prices['종가'].idxmax()\nprint(first_date, last_date)\nprint(max_close, max_date)\n",
        check="import pandas as pd\n\nassert s['first_date'] == pd.Timestamp('2025-01-13') and s['last_date'] == pd.Timestamp('2026-09-04')\nassert s['max_close'] == 362500 and s['max_date'] == pd.Timestamp('2026-06-18')"),
    quiz('stock-data-check', '단원 점검',
        choice('주가는 yfinance로 받을 수 있어요. 그런데 이 수업은 저장 파일 `data/stock.csv`로 시작해요. 그 이유로 맞지 **않는** 건 뭘까요?',
               ['저장 파일이 인터넷에서 받은 표보다 항상 더 정확하다',
                '모두가 같은 숫자로 연습한다',
                '네트워크가 끊겨도 미션이 돌아간다',
                '한 달 뒤 다시 돌려도 같은 결과가 나온다'], 0,
               '저장 파일이 더 정확하다는 건 틀린 말이에요. 받은 표를 그대로 둔 거거든요. 같은 숫자, 네트워크 독립, 재현이 저장해 쓰는 이유예요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「같은 숫자」·「네트워크」·「재현」: 셋 다 저장해 쓰는 진짜 이유예요. 그래서 이 문제의 답이 아니에요."),
        choice('금요일 저녁에 예측하는 "다음 거래일 종가"는 언제의 종가인가요?',
               ['월요일(다음 거래일)', '토요일(다음 날)', '금요일 당일'], 0,
               '월요일 종가예요. 주말과 휴장일에는 가격이 없거든요. 정답은 다음 달력 날짜가 아니라 다음 거래일의 종가예요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「금요일 당일」: 이미 아는 값이에요.\n- 「토요일」: 장이 안 열려 가격이 없어요."),
        choice('타이타닉 생존 예측과 이 챕터의 주가 예측은 무엇이 다른가요?',
               ['둘 중 하나를 고르는 분류와 숫자를 맞히는 회귀', '둘 다 분류', '주가는 머신러닝이 아니다'], 0,
               '정답이 "생존/사망" 중 하나면 분류, 종가 같은 숫자면 회귀예요. 흐름은 같고 점수 재는 법이 달라요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「주가는 머신러닝이 아니다」: 흐름은 같아요. 정답의 종류만 달라요.\n- 「둘 다 분류」: 종가는 숫자라 회귀예요."),
        short('날짜를 행 이름으로 올린 뒤 날짜순으로 정렬하는 메서드는 무엇인가요? (`.set_index(\'날짜\').________()`)', ['sort_index', 'sort_index()'],
              '`sort_index()`가 행 이름(날짜) 순으로 정렬해요. 날짜가 뒤섞여 있으면 "이전 날", "다음 날"이 전부 틀어져요.'),
        short('가장 높은 종가가 있는 날짜를 돌려주는 메서드는 무엇인가요? (`prices[\'종가\'].________()`)', ['idxmax', 'idxmax()'],
              '`idxmax()`예요. `max()`는 값이고, `idxmax()`는 그 값의 행 이름이에요. 날짜 인덱스에서는 날짜가 나와요.'),
        choice('모델이 기준 예측보다 오차가 작게 나왔어요. 이건 무엇을 뜻할까요?',
               ['이 기간에서 예측 오차가 더 작았다는 것뿐, 수익과는 별개다', '이 모델로 투자하면 돈을 번다', '예측이 항상 맞는다'], 0,
               '이 기간에 오차가 더 작았다는 뜻일 뿐이에요. 이 수업은 예측이 얼마나 빗나가는지를 재는 연습이에요. 오차가 작다는 것과 수익은 다른 이야기예요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「항상 맞는다」: 오차가 작아졌을 뿐 0이 아니에요.\n- 「돈을 번다」: 오차와 수익은 다른 문제예요."),
        choice("""**프롬프트 고르기** · 주가 CSV를 읽어 날짜 인덱스로 정렬해야 해요. 어떤 프롬프트가 다음 단원의 밀기(shift)와 이동평균(rolling)에 안전한 코드를 줄까요?""",
               ["""pandas. data/stock.csv를 parse_dates=['날짜']로 읽고 set_index('날짜').sort_index()해서 prices에. 행·열 수와 첫·마지막 날짜 출력. 코드만""", """주가 파일 읽어 줘""", """stock.csv 열어서 보여 줘""", """주가 데이터 불러와서 분석 준비해 줘"""], 0,
               """정답은 날짜로 읽기, 날짜 인덱스, 정렬 셋을 메서드 이름으로 적었어요. 하나라도 빠지면 뒤의 shift/rolling이 엉뚱한 순서로 계산돼요.

**다른 보기는 왜 아닌가**

- 「읽어 줘」: 날짜가 글자로 남고 정렬도 안 돼요.
- 「열어서 보여 줘」: 경로도 처리도 없어요.
- 「분석 준비해 줘」: 무엇을 준비할지 AI 마음대로예요."""),
        choice("""**프롬프트 고르기** · AI가 "이 모델로 투자하면 수익이 난다"고 적었어요. 바로잡는 프롬프트는 뭘까요?""",
               ["""이 수업은 예측 오차를 재는 연습이고 수익과는 별개야. 수익 언급을 빼고, 테스트 기간과 기준 대비 MAE만 적은 결론으로 다시 써 줘""", """얼마나 벌 수 있는지 계산해 줘""", """수익률도 그래프로 그려 줘""", """좋아, 그대로 둬"""], 0,
               """정답은 결론을 오차 비교로 좁히고, 수익 주장은 빼라고 했어요. 모델이 기준보다 조금 낫다는 것과 수익은 다른 이야기예요.

**다른 보기는 왜 아닌가**

- 「얼마나 벌 수 있는지」: 근거 없는 수익 계산을 불러요.
- 「수익률 그래프」: 같은 문제를 그래프로 키워요.
- 「그대로 둬」: 잘못된 주장이 보고서에 남아요."""),
    ),
])
