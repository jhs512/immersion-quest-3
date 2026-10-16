"""Authoring vocabulary for the KPC course. Each unit file builds one `UNIT` with these helpers.

Text is written as Markdown by hand; nothing is auto-formatted. Multiple-choice options are
shuffled deterministically so the correct answer does not always sit in the first slot.
"""
import random
import re
import textwrap

# Reference answers collected while units are built; written to courses/kpc-solutions.json.
SOLUTIONS = {}

REVISION = 4

# Shared preparation code. Every problem is independent, so these are repeated per problem.
PD = "import pandas as pd\n"
TI = PD + "titanic = pd.read_csv('data/titanic.csv')\n"
CR = PD + "credit = pd.read_csv('data/credit.csv')\ntarget = '다음달 부도'\n"
ST = PD + "prices = pd.read_csv('data/stock.csv', parse_dates=['날짜']).set_index('날짜').sort_index()\n"
ORDERS = PD + "orders = pd.DataFrame({'product': ['A', 'B', 'A', 'C'], 'price': [10000, 20000, 12000, None], 'quantity': [3, 2, 4, 1]})\n"
PLOT = "import matplotlib.pyplot as plt\nimport seaborn as sns\n"
FEATURES = "features = ['객실등급', '성별', '나이', '형제배우자', '부모자녀', '요금', '탑승항구']\nX = titanic[features].copy()\ny = titanic['생존'].astype(int)\n"
SPLIT = "from sklearn.model_selection import train_test_split\n\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)\n"
PREP = "from sklearn.compose import ColumnTransformer\nfrom sklearn.impute import SimpleImputer\nfrom sklearn.pipeline import Pipeline\nfrom sklearn.preprocessing import OneHotEncoder, StandardScaler\n\n\ndef make_preprocessor():\n    return ColumnTransformer([('numeric', Pipeline([('fill', SimpleImputer(strategy='median')), ('scale', StandardScaler())]), ['객실등급', '나이', '형제배우자', '부모자녀', '요금']), ('category', Pipeline([('fill', SimpleImputer(strategy='most_frequent')), ('encode', OneHotEncoder(handle_unknown='ignore'))]), ['성별', '탑승항구'])])\n"
ST_FRAME = ST + "frame = pd.DataFrame(index=prices.index)\nframe['close'] = prices['종가']\nframe['return_1'] = prices['종가'].pct_change()\nframe['ma5'] = prices['종가'].rolling(5).mean()\nframe['lag_close_1'] = prices['종가'].shift(1)\nframe['target_next_close'] = prices['종가'].shift(-1)\nframe['target_date'] = pd.Series(prices.index, index=prices.index).shift(-1)\nframe = frame.dropna().copy()\n"
TIME_SPLIT = "feature_columns = ['close', 'return_1', 'ma5', 'lag_close_1']\nX = frame[feature_columns]\ny = frame['target_next_close']\ntest_start = frame.index[-80]\ntrain_mask = (frame.index < test_start) & (frame['target_date'] < test_start)\ntest_mask = frame.index >= test_start\nX_train, X_test = X.loc[train_mask], X.loc[test_mask]\ny_train, y_test = y.loc[train_mask], y.loc[test_mask]\n"
REG = "from sklearn.pipeline import Pipeline\nfrom sklearn.preprocessing import StandardScaler\nfrom sklearn.linear_model import LinearRegression, Ridge, Lasso\nfrom sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score\n"

CHECKER_HEAD = (
    "import matplotlib\n\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as _plt\n\n_plt.show = lambda *a, **k: None  # a check opens no window and leaves no 'non-interactive' warning in the result\nimport logging as _lg, warnings as _wn\n_lg.getLogger('matplotlib.font_manager').setLevel(_lg.ERROR)  # no 'findfont' lines in the result\n_wn.filterwarnings('ignore', message='Glyph .* missing from font')\nfrom matplotlib import font_manager as _fm\n_installed = {f.name for f in _fm.fontManager.ttflist}\n_plt.rcParams['font.family'] = [n for n in ['Malgun Gothic', 'Apple SD Gothic Neo', 'AppleGothic', 'NanumGothic', 'Noto Sans KR', 'Noto Sans CJK KR'] if n in _installed] or ['DejaVu Sans']\n_plt.rcParams['axes.unicode_minus'] = False\nimport runpy, sys\n\ntry:\n    s = runpy.run_path(sys.argv[1])\nexcept Exception as error:\n    raise AssertionError('작성한 코드가 실행되지 않았습니다. 실행 결과를 확인하세요.') from error\n"
)
CHECKER_TAIL = (
    "\nexcept (KeyError,TypeError,AttributeError,ValueError,IndexError) as error:\n"
    "    raise AssertionError('결과 변수의 값과 자료형을 확인하세요.') from error\nprint('미션 검사 통과')\n"
)


def text(value):
    """Triple-quoted prose: drop common indentation and surrounding blank lines."""
    return textwrap.dedent(value).strip()


def short(prompt, accepted, explanation):
    return dict(prompt=text(prompt), type="short_answer", accepted=list(accepted), explanation=text(explanation))


def choice(prompt, options, correct, explanation):
    """`correct` is the index in the author's order; quiz() shuffles the options later."""
    return dict(prompt=text(prompt), type="choice", options=[text(o) for o in options], correct=correct, explanation=text(explanation))


def io(input, expected):
    return dict(input=input, expected=expected)


# ---- 표에서 고르기: a real table on screen, the student ticks rows or columns. ----

def table(csv, rows=None, columns=None, where=None, limit=None):
    """A small table taken from courses/data/<csv> as the student would see it. `rows` picks
    row numbers (0-based, in the file's order), `where(row_dict)` filters, `columns` keeps and
    orders columns, `limit` caps the count. Cells stay the file's text (blank stays blank)."""
    import csv as _csv
    import pathlib
    path = pathlib.Path(__file__).resolve().parents[2] / "courses" / "data" / csv
    with path.open(encoding="utf-8", newline="") as handle:
        reader = _csv.DictReader(handle)
        records = list(reader)
        names = list(reader.fieldnames)
    if rows is not None:
        records = [records[i] for i in rows]
    if where is not None:
        records = [r for r in records if where(r)]
    if limit is not None:
        records = records[:limit]
    keep = list(columns) if columns else names
    return dict(columns=keep, rows=[[r[c] for c in keep] for r in records])


def pick_rows(prompt, table, explanation, expected, size=None, required=(), forbidden=(), allowed=None, quota=()):
    """Rows to tick. `quota` is a list of (column, value, count): exactly that many picked rows
    must have column == value. `expected` is the model answer in words (shown after a miss)."""
    return _pick("rows", prompt, table, explanation, expected, size, required, forbidden, allowed, quota)


def pick_columns(prompt, table, explanation, expected, size=None, required=(), forbidden=(), allowed=None):
    """Columns to tick; `required`/`forbidden`/`allowed` take column names or indices."""
    names = table["columns"]
    index = lambda c: names.index(c) if isinstance(c, str) else int(c)
    return _pick("columns", prompt, table, explanation, expected, size,
                 [index(c) for c in required], [index(c) for c in forbidden],
                 None if allowed is None else [index(c) for c in allowed], ())


def _pick(pick, prompt, table, explanation, expected, size, required, forbidden, allowed, quota):
    rule = dict(required=list(required), forbidden=list(forbidden), quota=[dict(column=c, value=str(v), count=n) for c, v, n in quota])
    if size is not None:
        rule["size"] = list(size) if isinstance(size, (list, tuple)) else [size, size]
    if allowed is not None:
        rule["allowed"] = list(allowed)
    return dict(prompt=text(prompt), type="table_select", table=table, pick=pick, rule=rule,
                expected=text(expected), explanation=text(explanation))


def exact_rows(prompt, table, explanation, expected, rows):
    """Tick exactly these rows (0-based indices)."""
    rows = list(rows)
    return pick_rows(prompt, table, explanation, expected, size=len(rows), required=rows, allowed=rows)


def exact_columns(prompt, table, explanation, expected, columns):
    """Tick exactly these columns (names)."""
    columns = list(columns)
    return pick_columns(prompt, table, explanation, expected, size=len(columns), required=columns, allowed=columns)


CODE_TOKEN = re.compile(r"`([A-Za-z_][A-Za-z0-9_.]*(?:\(\))?)`")


def first_code_term(*texts):
    """The first inline-code identifier (e.g. `print`, `df.groupby()`) mentioned in the texts."""
    for value in texts:
        match = CODE_TOKEN.search(value or "")
        if match:
            return match.group(1)
    return None


def default_ask(kind, title, *texts, count=0):
    """Three quick questions for the tutor panel that name this activity's own content."""
    term = first_code_term(*texts)
    if kind == "concept":
        first = f"`{term}` 빵 공장 예로 설명해 줘" if term else f"'{title}' 빵 공장 예로 설명해 줘"
        return [first, "확인 문항 힌트만 줘, 답은 말고", f"'{title}' 핵심 용어 세 개만 정리해 줘"]
    if kind == "coding":
        first = f"`{term}` 쓰는 법 힌트만 줘" if term else "힌트만 줘, 답은 말고"
        return [first, "지금 쓴 코드 어디가 틀렸어?", f"'{title}' 풀어서 제출까지 해 줘"]
    if kind == "quiz":
        return ["1번 문제 힌트만 줘", f"'{title}' {count}문제에서 헷갈리기 쉬운 함정 알려 줘", "퀴즈 전부 풀어서 채점해 줘"]
    return ["이 덱을 세 줄로 요약해 줘", f"'{title}'에서 꼭 기억할 한 가지는?", "다음 장으로 넘겨 줘"]


def concept(id, title, body, check, ask=None):
    body = text(body)
    return dict(id=id, title=title, kind="concept", body=body, check=dict(check, id="check"),
                ask=list(ask) if ask else default_ask("concept", title, body))


IMPORT_LINE = re.compile(r"^(?:import\s+([\w.]+)(?:\s+as\s+(\w+))?|from\s+[\w.]+\s+import\s+([\w, ]+))\s*$")


def unused_imports(code, used_in=None):
    """The import lines of `code` whose names never appear in `used_in` (default: the code itself)
    outside import lines. `from x import a, b` counts as used when either name is."""
    reference = used_in if used_in is not None else code
    body = "\n".join(line for line in reference.split("\n") if not IMPORT_LINE.match(line.strip()))
    out = []
    for line in code.split("\n"):
        match = IMPORT_LINE.match(line.strip())
        if not match:
            continue
        module, alias, names = match.groups()
        targets = [n.strip().split(" as ")[-1] for n in names.split(",")] if names else [alias or module.split(".")[0]]
        if not any(re.search(r"\b" + re.escape(t) + r"\b", body) for t in targets if t):
            out.append(line)
    return out


def drop_unused_imports(starter, solution):
    """Content rule: no import that the solution never uses, in the starter or the solution.
    The shared PLOT/PD prefixes bring seaborn or pandas to missions that only use matplotlib or
    BeautifulSoup; those lines are removed from both texts so the student sees no dead import."""
    for line in unused_imports(starter, used_in=solution):
        starter = starter.replace(line + "\n", "", 1)
        solution = solution.replace(line + "\n", "", 1)
    return starter, solution


def coding(id, title, goal, hint, starter, solution, check=None, tests=None, intro=None, ask=None):
    starter, solution = drop_unused_imports(starter, solution)
    """A standalone main.py problem. `check` is assertion source over `s` (the student's globals)."""
    content = ""
    if intro:
        content += "### 문제에서 필요한 설명\n\n" + text(intro) + "\n\n"
    content += "### 목표\n\n" + text(goal) + "\n\n### 힌트\n\n" + text(hint)
    problem = dict(id=id, title=title, content=content, starter_code=starter)
    if check:
        assertions = text(check)
        required = sorted(set(re.findall(r"\bs\[['\"]([A-Za-z_][A-Za-z_0-9]*)['\"]\]", assertions)))
        body = "\n".join("    " + line for line in assertions.splitlines())
        problem["checker"] = (
            CHECKER_HEAD
            + f"assert set({required!r}).issubset(s), '문제에서 요청한 결과 변수를 준비하세요.'\n"
            + "try:\n" + body + CHECKER_TAIL
        )
    else:
        problem["tests"] = list(tests)
    SOLUTIONS[id] = solution
    return dict(id=id, title=title, kind="coding", problem=problem,
                ask=list(ask) if ask else default_ask("coding", title, text(goal), text(hint)))


# Front matter every deck starts with (Marp, the app's theme, page numbers).
MARP_FRONT = "---\nmarp: true\ntheme: molip\npaginate: true\n---\n\n"


def split_slides(markdown):
    """(front matter or None, [slide bodies]) for Marp Markdown: slides break at a line that is
    exactly `---`, except the front matter fence at the very top."""
    front = None
    body = markdown
    if body.startswith("---\n"):
        end = body.find("\n---\n", 4)
        if end >= 0:
            front = body[:end + 5]
            body = body[end + 5:]
    # A `---` inside a code fence (a prompt's "---\n코드만 줘", for one) is text, not a break.
    parts, current, fenced = [], [], False
    for line in body.split("\n"):
        if line.startswith("```"):
            fenced = not fenced
        if line == "---" and not fenced:
            parts.append("\n".join(current))
            current = []
        else:
            current.append(line)
    parts.append("\n".join(current))
    return front, parts


def slides(id, title, markdown, ask=None, script=None):
    """A Marp deck (Markdown with `---` slide breaks) the instructor presents in class.

    `script` is the presenter script: one spoken paragraph per slide, in order, in the
    instructor's own voice. It is stored as an HTML comment at the end of each slide (Marp keeps
    comments as presenter notes) and the app shows it on right-click. The count must match the
    slide count, so a slide can never be presented without its line."""
    markdown = text(markdown)
    if script is not None:
        front, parts = split_slides(markdown)
        script = [text(s) for s in script]
        if len(script) != len(parts):
            raise SystemExit(f"{id}: 슬라이드 {len(parts)}장인데 스크립트가 {len(script)}개입니다.")
        for n, line in enumerate(script):
            if not line or "-->" in line:
                raise SystemExit(f"{id}: {n + 1}번째 스크립트가 비었거나 '-->'를 담고 있습니다.")
        parts = [f"{part.rstrip()}\n\n<!-- {line} -->\n" for part, line in zip(parts, script)]
        markdown = (front or "") + "\n---\n".join(parts)
    return dict(id=id, title=title, kind="slides", markdown=markdown,
                ask=list(ask) if ask else default_ask("slides", title), ask_is_default=not ask)


def challenge(id, title, **kwargs):
    """A chapter capstone: a coding problem that needs everything the chapter taught."""
    activity = coding(id, '★ 도전 과제 · ' + title, **kwargs)
    activity["challenge"] = True
    return activity


def quiz(id, title, *questions, ask=None):
    shuffled = []
    for index, question in enumerate(questions):
        question = dict(question, id=f"q{index + 1}")
        if question["type"] == "choice":
            order = list(range(len(question["options"])))
            random.Random(f"{id}:{index}").shuffle(order)
            question["options"] = [question["options"][i] for i in order]
            question["correct"] = order.index(question["correct"])
        shuffled.append(question)
    return dict(id=id, title=title, kind="quiz", questions=shuffled,
                ask=list(ask) if ask else default_ask("quiz", title, count=len(shuffled)), ask_is_default=not ask)


def unit(id, title, activities):
    return dict(id=id, title=title, content="", revision=REVISION, activities=list(activities))
