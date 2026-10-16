"""저장 HTML에서 자료 수집"""
from kpc_course.dsl import *

SOUP = PD + "from pathlib import Path\nfrom bs4 import BeautifulSoup\n\nhtml = Path('data/prices.html').read_text(encoding='utf-8')\nsoup = BeautifulSoup(html, 'html.parser')\n"

UNIT = unit('html', '저장 HTML에서 자료 수집', [
    concept('html-selectors', '웹 페이지는 글자 덩어리, 우리가 원하는 건 그중 두 칸',
        body="""
        지금까지의 표는 파일로 받았죠? 그런데 어떤 숫자는 파일이 아니라 **웹 페이지에만** 있어요. 포털의 시세 화면이 그래요. 브라우저가 보여 주는 화면의 정체는 HTML이라는 글자 파일이에요. 그 안에 가격이 적혀 있고요. 문제는 가격 말고도 광고, 메뉴, 제목 같은 글자가 수천 줄 섞여 있다는 거예요. 거기서 원하는 칸만 집어내요. 그게 이 단원의 일이에요.

        ```comic-gen
        제목: 수집은 네 단계
        등장인물:
          강사:
            그림: 사람
            이름표: 강사
            외형: {옷: 재킷, 옷색: "#5379a7", 안경: true}
        컷:
          - 인물: [{식별자: 강사, 손모양: 가리키는손}]
            대사: [{화자: 강사, 내용: "선택자로 찾고, 글자를 꺼내고, 숫자로 바꾸고, 표에 모읍니다."}]
            다이어그램:
              종류: 머메이드
              제목: HTML에서 표까지
              높이: 600
              원문: |
                flowchart TB
                  A["1. 읽기: BeautifulSoup"] --> B["2. 선택: select(#prices li)"]
                  B --> C["3. 추출: 글자와 속성"]
                  C --> D["4. 변환: 쉼표 지우고 int()"]
                  D --> E["표: rows → DataFrame"]
        ```

        HTML은 `<li>`, `<span>`처럼 꺾쇠로 감싼 **태그**로 내용을 묶어요. 앱이 준비한 `data/prices.html`은 아래처럼 생겼어요. 종목 하나가 `li` 하나예요. 그 안에 이름을 담은 `span`과 가격을 담은 `b`가 있고요.

        ```html
        <ul id="prices">
          <li data-code="A"><span class="name">가상A</span><b>10,000</b></li>
          <li data-code="B"><span class="name">가상B</span><b>20,000</b></li>
        </ul>
        ```

        원하는 태그를 집어내는 주소 표기법이 **선택자**(selector)예요. `#prices`는 `id`가 prices인 요소예요. `.name`은 `class`가 name인 요소고요. `#prices li`는 "prices 안에 있는 모든 `li`"예요. `BeautifulSoup`이라는 도구로 HTML을 읽어 둬요. 그러면 `select(선택자)`로 맞는 요소를 전부 꺼낼 수 있어요. `select_one(선택자)`은 첫 하나만 꺼내고요. 꺼낸 요소에서 글자만 뽑을 때는 `get_text(strip=True)`를 써요.

        ```python
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, 'html.parser')
        items = soup.select('#prices li')  # li 두 개
        name = items[0].select_one('.name').get_text(strip=True)  # '가상A'
        price = int(items[0].select_one('b').get_text(strip=True).replace(',', ''))
        ```

        마지막 줄에 함정이 하나 있어요. 뽑아낸 가격은 `'10,000'`이라는 **글자**예요. 쉼표까지 들어 있어서 `int()`로 바로 바꾸면 오류가 나요. `replace(',', '')`로 쉼표를 먼저 지우세요. 그다음 `int()`를 거쳐야 계산할 수 있는 숫자가 돼요. 수집은 늘 이렇게 "찾기 → 글자 뽑기 → 숫자로 고치기 → 표로 모으기" 네 단계예요.

        실제 포털 사이트에 접속하는 대신 저장해 둔 문서로 연습하는 이유는 하나예요. 사이트는 구조가 자주 바뀌어요. 그러면 어제 되던 선택자가 오늘 빈 결과를 내죠. 원리는 같아요. 저장된 문서로 네 단계를 먼저 몸에 익혀요.
        """,
        check=short('HTML에서 태그를 집어내는 `#prices li` 같은 주소 표기법을 뭐라고 하나요?', ['선택자', 'selector', 'CSS 선택자', 'css selector', 'CSS selector'],
                    '선택자(selector)는 "어떤 요소를 고를지"를 적는 표기법이에요. `#`은 id, `.`은 class, 공백은 "그 안의"를 뜻해요.')),
    coding('string-to-int', '쉼표 있는 가격 글자를 숫자로',
        goal="""
        수집의 네 단계 중 세 번째, 글자를 숫자로 고치는 단계만 따로 연습해요. `price_text`에 `'10,000'`이 들어 있어요. 쉼표를 지우고 `int()`로 바꿔 `price`에 담으세요. 그다음 `price * 3`을 출력하세요.

        30000이 나오면 숫자로 바뀐 거예요.
        """,
        hint="""
        `price_text.replace(',', '')`가 쉼표를 빈 글자로 바꿔요. 그러면 `'10000'`이 돼요. 그다음 `int()`로 감싸세요. 순서를 바꿔 `int('10,000')`을 먼저 하면 `ValueError`가 나요.
        """,
        starter="price_text = '10,000'\n# price를 만들고 price * 3을 출력하세요\n",
        solution="price_text = '10,000'\nprice = int(price_text.replace(',', ''))\nprint(price * 3)\n",
        check="assert s['price'] == 10000 and isinstance(s['price'], int)"),
    coding('select-one', '선택자로 요소 찾기',
        goal="""
        준비 코드가 HTML을 읽어 `soup`를 만들어 뒀어요. `#prices li`에 맞는 요소가 몇 개인지 `n_items`에 담으세요. 첫 종목의 이름(`.name` 요소의 글자)은 `first_name`에 담고요. 둘 다 출력하세요.

        2와 `가상A`가 나오면 맞게 찾은 거예요.
        """,
        hint="""
        `soup.select('#prices li')`는 맞는 요소를 리스트로 돌려줘요. 그러니 `len()`으로 세면 돼요. 첫 요소 `[0]`에서 `.select_one('.name')`으로 이름 요소를 찾으세요. `.get_text(strip=True)`로 글자만 꺼내고요.
        """,
        starter=SOUP + "# n_items, first_name을 만들고 출력하세요\n",
        solution=SOUP + "items = soup.select('#prices li')\nn_items = len(items)\nfirst_name = items[0].select_one('.name').get_text(strip=True)\nprint(n_items, first_name)\n",
        check="assert s['n_items'] == 2 and s['first_name'] == '가상A'"),
    coding('select-prices', '가격만 모두 뽑아 숫자 리스트로',
        goal="""
        이번에는 두 종목의 가격을 전부 뽑아 숫자 리스트로 만들어요. `#prices li b`로 가격 요소를 모두 찾으세요. 하나씩 글자를 꺼내 쉼표를 지우고 `int()`로 바꿔요. 그 값을 `prices` 리스트에 모으면 돼요.

        `prices`가 `[10000, 20000]`이면 맞게 한 거예요. 앞 단원의 `for`와 `append`가 그대로 쓰여요.
        """,
        hint="""
        `prices = []`로 빈 리스트를 만드세요. `for tag in soup.select('#prices li b'):`로 돌아요. 안에서 `prices.append(int(tag.get_text(strip=True).replace(',', '')))`를 하면 돼요.
        """,
        starter=SOUP + "# prices 리스트를 만들고 출력하세요\n",
        solution=SOUP + "prices = []\nfor tag in soup.select('#prices li b'):\n    prices.append(int(tag.get_text(strip=True).replace(',', '')))\nprint(prices)\n",
        check="assert s['prices'] == [10000, 20000]"),
    coding('parse-html', '종목 코드·이름·가격을 표로 모으기',
        goal="""
        네 단계를 한 번에 해요. 준비 코드가 `data/prices.html`을 `html`로 읽어 뒀어요. 그걸로 `soup`를 만드세요. `#prices li`를 하나씩 돌면서 딕셔너리를 만들어요. 종목 코드(`data-code` 속성)와 이름(`.name`)을 담아요. 가격(`b`)은 쉼표 없는 정수로 담고요. 그 딕셔너리를 `rows` 리스트에 모으세요. 마지막으로 `rows`로 `df`를 만드세요.

        `df`가 2행이고 `price` 열이 10000, 20000이면 맞게 한 거예요. 딕셔너리 리스트가 표가 되는 건 앞 단원에서 본 그대로예요.
        """,
        hint="""
        `soup = BeautifulSoup(html, 'html.parser')`로 시작해요. `for item in soup.select('#prices li'):` 안에서 세 값을 꺼내요. 코드는 `item['data-code']`예요. 이름은 `item.select_one('.name').get_text(strip=True)`고요. 가격은 `int(item.select_one('b').get_text(strip=True).replace(',', ''))`예요. 셋을 `{'code': ..., 'name': ..., 'price': ...}` 딕셔너리로 묶으세요. 그걸 `rows`에 `append`하고요. 마지막에 `df = pd.DataFrame(rows)`로 표를 만들어요.
        """,
        starter=PD + "from pathlib import Path\nfrom bs4 import BeautifulSoup\n\nhtml = Path('data/prices.html').read_text(encoding='utf-8')\n# soup, rows, df를 만드세요\n",
        solution=PD + "from pathlib import Path\nfrom bs4 import BeautifulSoup\n\nhtml = Path('data/prices.html').read_text(encoding='utf-8')\nsoup = BeautifulSoup(html, 'html.parser')\nrows = []\nfor item in soup.select('#prices li'):\n    rows.append({'code': item['data-code'], 'name': item.select_one('.name').get_text(strip=True), 'price': int(item.select_one('b').get_text(strip=True).replace(',', ''))})\ndf = pd.DataFrame(rows)\ndf\n",
        check="assert s['df']['code'].tolist() == ['A', 'B']\nassert s['df']['price'].tolist() == [10000, 20000]\nassert s['df']['name'].tolist() == ['가상A', '가상B']"),
    concept('live-web', '진짜 웹에서 받으려면: requests, 그리고 Selenium',
        body="""
        지금까지는 앱이 저장해 둔 `data/prices.html`을 읽었죠? 인터넷이 되는 컴퓨터에서는 그 파일을 코드가 직접 받아 와요. 받는 도구가 `requests`예요. 받은 뒤는 저장 파일 때와 **한 글자도 다르지 않아요**.

        ```python
        import requests
        from bs4 import BeautifulSoup

        response = requests.get('https://example.com/prices', headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        for tag in soup.select('#prices li b'):
            print(tag.get_text(strip=True))
        ```

        `requests.get`이 주소를 요청하면 `response.text`에 글자 덩어리가 와요. 그 글자가 바로 우리가 읽던 HTML이에요. `headers`의 `User-Agent`는 "저 브라우저예요"라고 밝히는 명함이에요. 없으면 거절하는 사이트가 있거든요. `timeout`은 응답이 없을 때 무한정 기다리지 않게 해요.

        받은 글자를 파일로 저장해 두세요. `Path('prices.html').write_text(response.text)`로요. 그러면 이 수업과 같은 방식이 돼요. 수업이 저장 파일을 쓰는 이유도 여기 있어요. 모두가 같은 숫자로 연습하고, 사이트가 바뀌어도 미션이 안 깨지거든요.

        그런데 어떤 페이지는 `requests`로 받으면 비어 있어요. 화면이 자바스크립트(브라우저 안에서 도는 코드)로 **나중에** 그려지는 경우예요. 아니면 검색창에 글자를 넣고 버튼을 눌러야 결과가 나오는 경우고요. 포털 검색이 그래요. 이럴 때는 **Selenium**(셀레니움)으로 진짜 브라우저를 코드로 조종해요. 주소를 열어요. 검색창을 찾아 글자를 넣고 엔터를 쳐요. 그려진 화면의 HTML을 가져오고요.

        ```python
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        browser = webdriver.Chrome()
        browser.get('https://www.naver.com')
        browser.find_element(By.ID, 'query').send_keys('삼성전자 주가\\n')
        soup = BeautifulSoup(browser.page_source, 'html.parser')   # 여기부터는 다시 같은 네 단계
        browser.quit()
        ```

        고르는 기준은 하나예요. **주소만으로 내용이 다 오면 `requests`, 클릭·입력·스크롤이 있어야 나오면 Selenium.** Selenium은 브라우저를 띄우니 느려요. 크롬과 드라이버 설치도 필요하고요.

        어느 쪽이든 수집 전에 사이트의 이용 약관과 `robots.txt`를 확인하세요. `robots.txt`는 수집 허용 범위를 적어 둔 파일이에요. 요청 사이에 간격도 두세요. 같은 서버에 초당 수십 번 요청하면 수집이 아니라 공격이에요.

        이 앱 안에서는 둘 다 실행하지 않아요. 네트워크와 브라우저가 필요하니까요. 받은 결과를 저장한 파일로 네 단계를 연습해요. 받는 두 줄은 회사 컴퓨터에서 붙이세요. `import requests`와 `requests.get(...)`이요.
        """,
        check=short('검색창에 글자를 넣고 엔터를 치는 것까지 브라우저를 조종하는 도구는 뭘까요?', ['Selenium', '셀레니움', 'selenium'],
                    'Selenium이에요. 주소만으로 내용이 다 오는 페이지는 `requests`로 충분해요. 자바스크립트로 그려지거나 입력이 필요한 페이지만 Selenium을 써요.')),
    coding('live-crawl', '진짜 웹에서: 코스피 연도별 종가 긁어 오기',
        intro="""
        인터넷이 필요한 미션이에요. 위키백과의 KOSPI 문서에는 1981년부터 해마다 코스피 종가와 그해 등락률이 적힌 표가 있어요. 준비 코드가 그 페이지를 `requests`로 받아 `soup`까지 만들어 둬요. 포털 시세 화면은 자바스크립트로 그려져서 `requests`로는 비어 오니, 정적인 위키 표를 써요.
        """,
        goal="""
        `soup.select('table.wikitable')` 중 글자에 `Closing level`이 든 표를 골라 `table`에 두세요. 그 표의 `tr`마다 `td` 글자를 리스트로 꺼내요. 칸이 네 개 미만이거나 넷째 칸(등락률)이 비어 있으면 건너뛰어요. 나머지 행에서 연도(`int`), 종가(쉼표를 지우고 `float`), 변화율(`−` 기호를 `-`로 바꾸고 `float`)을 뽑아 `kospi` 표를 만드세요. 열 이름은 `연도`, `종가`, `변화율`이에요.

        그 표로 두 가지를 구하세요. 가장 많이 오른 해를 `best_year`에, 오른 해의 수를 `up_years`에 담고, 표 끝부분과 두 값, 평균 변화율을 출력하세요.
        """,
        hint="""
        표 고르기는 `[t for t in soup.select('table.wikitable') if 'Closing level' in t.get_text()][0]`이에요. 행 반복은 `for tr in table.select('tr'):` 안에서 `cells = [td.get_text(strip=True) for td in tr.select('td')]`. 위키의 음수 기호는 `-`가 아니라 `−`(유니코드)라서 `.replace('−', '-')`가 필요해요. 가장 많이 오른 해는 `kospi.loc[kospi['변화율'].idxmax(), '연도']`.
        """,
        starter="import requests\nimport pandas as pd\nfrom bs4 import BeautifulSoup\n\nurl = 'https://en.wikipedia.org/wiki/KOSPI'\nresponse = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)\nsoup = BeautifulSoup(response.text, 'html.parser')\n# table, kospi, best_year, up_years를 만드세요\n",
        solution="import requests\nimport pandas as pd\nfrom bs4 import BeautifulSoup\n\nurl = 'https://en.wikipedia.org/wiki/KOSPI'\nresponse = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)\nsoup = BeautifulSoup(response.text, 'html.parser')\ntable = [t for t in soup.select('table.wikitable') if 'Closing level' in t.get_text()][0]\nrows = []\nfor tr in table.select('tr'):\n    cells = [td.get_text(strip=True) for td in tr.select('td')]\n    if len(cells) < 4 or not cells[3]:\n        continue\n    rows.append({'연도': int(cells[0]), '종가': float(cells[1].replace(',', '')), '변화율': float(cells[3].replace('−', '-'))})\nkospi = pd.DataFrame(rows)\nbest_year = int(kospi.loc[kospi['변화율'].idxmax(), '연도'])\nup_years = int((kospi['변화율'] > 0).sum())\nprint(kospi.tail())\nprint(best_year, up_years, round(kospi['변화율'].mean(), 1))\n",
        check="assert len(s['kospi']) >= 30\nassert list(s['kospi'].columns) == ['연도', '종가', '변화율']\nassert (s['kospi']['종가'] > 0).all() and s['kospi']['연도'].is_monotonic_increasing\nassert 2020 in set(s['kospi']['연도'])\nassert s['best_year'] == int(s['kospi'].loc[s['kospi']['변화율'].idxmax(), '연도'])\nassert s['up_years'] == int((s['kospi']['변화율'] > 0).sum())"),
    quiz('html-check', '단원 점검',
        choice('포털 검색 결과처럼 검색어를 입력해야 나오는 페이지를 모으려고 해요. 맞는 도구는 무엇인가요?',
               ['Selenium으로 브라우저를 조종해 검색어를 넣고 그려진 화면을 받는다',
                'requests.get으로 주소만 요청한다',
                'read_csv로 주소를 읽는다',
                'BeautifulSoup이 알아서 검색해 준다'], 0,
               'Selenium이 맞아요. 입력과 클릭이 있어야 나오는 화면은 브라우저를 직접 움직여야 하거든요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「requests.get」: 주소만으로 내용이 다 오는 정적 페이지용이에요. 검색 결과는 비어 와요.\n- 「read_csv」: 표 파일을 읽는 함수예요. 웹 페이지를 받는 도구가 아니에요.\n- 「BeautifulSoup이 알아서」: BeautifulSoup은 받아 온 HTML을 읽을 뿐이에요. 받아 오지는 않아요."),
        short('`id`가 `prices`인 요소를 고르는 선택자를 기호까지 포함해 쓰면 무엇인가요?', ['#prices'],
              '`#`은 id를 뜻해요. class를 고를 때는 `.name`처럼 점을 써요.'),
        choice("`int('10,000')`을 실행하면 어떻게 되나요?",
               ['`ValueError`. 쉼표 때문에 숫자로 바꿀 수 없다', '`10000`이 된다', '`10`이 된다'], 0,
               "`int()`는 숫자 글자만 받아요. 쉼표를 먼저 `replace(',', '')`로 지워야 해요." "\n\n**다른 보기는 왜 아닌가**\n\n- 「10이 된다」: 쉼표 앞에서 끊어 읽지 않아요.\n- 「10000이 된다」: int()는 쉼표를 알아서 지워 주지 않아요."),
        choice('`soup.select(...)`와 `soup.select_one(...)`의 차이는 무엇인가요?',
               ['앞은 맞는 요소를 전부 리스트로, 뒤는 첫 하나만 돌려준다', '앞은 id로, 뒤는 class로 찾는다', '둘은 같다'], 0,
               '`select`는 리스트예요. `for`로 돌거나 `[0]`으로 꺼내야 해요. `select_one`은 요소 하나를 바로 돌려주고요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「id로, class로」: 둘 다 같은 CSS 선택자를 받아요.\n- 「둘은 같다」: 돌려주는 게 리스트냐 요소 하나냐가 달라요."),
        choice('수집 코드가 어제는 됐는데 오늘은 빈 결과를 내요. 가장 가능성이 높은 원인은 무엇인가요?',
               ['사이트 구조가 바뀌어 선택자가 더 이상 맞지 않는다', 'Python 문법이 바뀌었다', '`int()`가 고장 났다'], 0,
               '사이트 구조가 바뀐 거예요. 선택자는 문서 구조에 기대어 있거든요. 태그나 class 이름이 바뀌면 같은 선택자가 아무것도 못 찾아요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「Python 문법이 바뀌었다」: 하루 사이에 바뀌지 않아요.\n- 「int()가 고장」: 내장 함수는 고장 나지 않아요. 입력이 비었을 뿐이에요."),
        choice("`item['data-code']`는 무엇을 꺼내나요?",
               ['`<li data-code="A">`처럼 태그에 붙은 속성 값', '`li` 안의 글자', '종목 가격'], 0,
               '태그에 붙은 속성 값이에요. 꺾쇠 안에 `이름="값"` 꼴로 붙은 게 속성이거든요. 태그 사이의 글자는 `get_text()`로 꺼내요.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「종목 가격」: 가격은 b 태그 안의 글자예요.\n- 「li 안의 글자」: 글자는 get_text()로 꺼내요. 속성과 달라요."),
        short('수집한 딕셔너리 리스트 `rows`를 표로 만드는 코드는 `pd.________(rows)`예요. 빈칸은?', ['DataFrame'],
              '앞 단원과 같아요. 딕셔너리 하나가 한 행이 되어 `DataFrame`이 만들어져요.'),
        choice("""**프롬프트 고르기** · 저장된 HTML에서 `#prices li` 안의 가격을 숫자 리스트로 모아야 해요. 어떤 프롬프트가 한 번에 맞는 코드를 줄까요?""",
               ["""파이썬 BeautifulSoup. soup 객체가 있어. "#prices li b" 요소들의 텍스트를 쉼표 제거 후 int로 바꿔 prices 리스트에 모아 출력. 결과 [10000, 20000]. 코드만""", """웹에서 가격 긁어 줘""", """HTML 파싱하는 법 알려 줘""", """가격 뽑아서 리스트로 만들어 줘"""], 0,
               """정답에는 선택자와 네 단계가 다 있어요. 찾기 → 글자 뽑기 → 숫자로 고치기 → 리스트에 모으기요. 결과 변수와 기대값도 있고요. 수집 프롬프트는 선택자를 주는 게 절반이에요.

**다른 보기는 왜 아닌가**

- 「웹에서 가격 긁어 줘」: 어느 페이지, 어느 요소인지 없어요. 인터넷 접근 코드가 오고요.
- 「파싱하는 법」: 설명만 와요.
- 「가격 뽑아서 리스트로」: 선택자가 없어 AI가 구조를 추측해요."""),
        choice("""**프롬프트 고르기** · 어제 되던 수집 코드가 오늘 빈 결과를 내요. AI에게 원인을 찾아 달라고 할 때 가장 좋은 질문은 무엇인가요?""",
               ["""BeautifulSoup으로 soup.select('#prices li')가 어제는 2개였는데 오늘은 빈 리스트야. HTML 구조가 바뀌었는지 확인하는 코드와, 선택자를 점검하는 순서를 알려 줘""", """코드가 안 돼""", """빈 리스트 나오는데 고쳐 줘""", """파이썬 버전 문제야?"""], 0,
               """정답은 어제와 오늘의 결과 차이와 쓴 선택자를 적었어요. 원하는 답의 종류(확인 코드 + 점검 순서)도 있고요. 증상의 변화를 적으면 원인이 좁혀져요.

**다른 보기는 왜 아닌가**

- 「코드가 안 돼」: 아무 정보가 없어요.
- 「고쳐 줘」: 코드를 보여 주지 않아 고칠 수 없어요.
- 「파이썬 버전 문제야?」: 하루 사이 버전은 안 바뀌어요. 잘못된 가설로 유도하고요."""),
    ),
])
