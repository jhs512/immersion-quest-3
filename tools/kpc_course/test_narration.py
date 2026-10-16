"""The coding 해설 compiler enforces the content rules (docs/content-rules.md) without the AI.

    python -m pytest tools/kpc_course/test_narration.py -q
"""
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from kpc_course import comments, narration  # noqa: E402

SOLUTION = "price = 10000\nquantity = 3\namount = price * quantity\nprint(amount)\n"
ACTIVITY = {
    "id": "variable-print",
    "kind": "coding",
    "title": "1-1-8 변수에 저장하고 출력하기",
    "problem": {"id": "variable-print", "content": "### 목표\n\n곱해서 출력하세요.", "starter_code": "price = 10000\nquantity = 3\n# amount를 만들고 출력하세요\n", "tests": [{"input": "", "expected": "30000\n"}]},
}
GOOD = [
    ("problem", "같은 계산을 이름표로 해요."),
    ("starter", "준비 코드 두 줄은 그대로 둘게요."),
    ("code", "amount = price * quantity\n", "오른쪽을 먼저 계산해서 amount에 넣어요."),
    ("run", "일단 실행해 볼게요."),
    ("output", "아무것도 안 나오죠? 넣기만 했거든요."),
    ("try", "print(amount\n", "이렇게 해 볼까요?"),
    ("run", "실행하면요."),
    ("output", "SyntaxError가 나요. 괄호를 안 닫았거든요."),
    ("undo", "그래서 괄호를 꼭 닫아요."),
    ("code", "print(amount)\n", "그다음 줄에서 꺼내 써요."),
    ("run", "다시 실행해요."),
    ("output", "30000이 나왔죠?"),
    ("caution", "숫자 30000을 직접 적기 쉬운데, 가격이 바뀌면 틀리니 조심하세요."),
    ("submit", "제출할게요."),
]


def compile_(entry):
    return narration.compile_coding(ACTIVITY, entry, SOLUTION, "test")


def test_incremental_entry_compiles_to_typed_runs_and_an_undo_that_restores_the_code():
    actions = compile_(GOOD)
    kinds = [a["action"] for a in actions]
    assert kinds.count("run") == 3 and kinds[-1] == "submit"
    assert actions[0]["target"] == "problem"
    typed = [a for a in actions if a["action"] == "type_code"]
    assert [t["code"] for t in typed] == ["amount = price * quantity\n", "print(amount\n", "print(amount)\n"]
    undo = next(a for a in actions if a["action"] == "set_code" and a["say"].startswith("그래서"))
    assert undo["code"] == "price = 10000\nquantity = 3\namount = price * quantity\n"
    caution = next(a for a in actions if a["action"] == "say" and a["target"] == "editor")
    assert "조심하세요" in caution["text"]
    # Replayed like the agent, the editor ends as the solution.
    states = narration.coding_states([s for s in GOOD if s[0] in ("code", "try", "undo")], "price = 10000\nquantity = 3\n")
    assert states[-1][1] == SOLUTION


def test_one_run_at_the_end_is_refused():
    entry = [s for s in GOOD if s[0] not in ("run", "output", "try", "undo")]
    entry.insert(-1, ("run", "실행해요."))
    entry.insert(-1, ("output", "30000이에요."))
    with pytest.raises(SystemExit, match="반복"):
        compile_(entry)


def test_a_try_must_be_undone_and_an_undo_needs_a_try():
    entry = [s for s in GOOD if s[0] != "undo"]
    with pytest.raises(SystemExit, match="undo"):
        compile_(entry)
    entry = [s for s in GOOD if s[0] != "try"]
    with pytest.raises(SystemExit, match="try"):
        compile_(entry)


def test_a_caution_or_a_try_is_required_and_output_follows_run():
    entry = [
        ("problem", "말"), ("starter", "말"),
        ("code", "amount = price * quantity\n", "말"), ("run", "말"), ("output", "말"),
        ("code", "print(amount)\n", "말"), ("run", "말"), ("output", "말"), ("submit", "말"),
    ]
    with pytest.raises(SystemExit, match="조심하세요"):
        compile_(entry)
    entry = list(GOOD)
    entry.insert(4, ("output", "run 없이 나온 output"))
    with pytest.raises(SystemExit, match="output은 run 바로 뒤"):
        compile_(entry)


def test_chunks_must_join_into_the_solution_with_comments_intact():
    commented = "price = 10000\nquantity = 3\n# 가격 × 수량\namount = price * quantity  # 금액\nprint(amount)  # 출력\n"
    entry = [
        ("problem", "말"), ("starter", "말"),
        ("code", "# 가격 × 수량\namount = price * quantity  # 금액\n", "말"), ("run", "말"), ("output", "말"),
        ("caution", "조심하세요."),
        ("code", "print(amount)  # 출력\n", "말"), ("run", "말"), ("output", "말"), ("submit", "말"),
    ]
    actions = narration.compile_coding(ACTIVITY, entry, commented, "test")
    typed = "".join(a["code"] for a in actions if a["action"] == "type_code")
    assert "price = 10000\nquantity = 3\n" + typed == commented
    with pytest.raises(SystemExit, match="정답 코드가 되어야"):
        narration.compile_coding(ACTIVITY, entry, SOLUTION, "test")
    assert comments.strip_comments(commented) == comments.strip_comments(SOLUTION)


def test_unused_imports_are_dropped_from_starter_and_solution_alike():
    from kpc_course import dsl
    starter = "import matplotlib.pyplot as plt\nimport seaborn as sns\n# fig, ax를 만드세요\n"
    solution = "import matplotlib.pyplot as plt\nimport seaborn as sns\nfig, ax = plt.subplots()\n"
    new_starter, new_solution = dsl.drop_unused_imports(starter, solution)
    assert "seaborn" not in new_starter and "seaborn" not in new_solution
    assert new_starter == "import matplotlib.pyplot as plt\n# fig, ax를 만드세요\n"
    assert new_solution.startswith("import matplotlib.pyplot as plt\nfig, ax")
    kept = "import pandas as pd\nfrom bs4 import BeautifulSoup\n"
    used = kept + "soup = BeautifulSoup(html)\ndf = pd.DataFrame()\n"
    assert dsl.drop_unused_imports(kept, used) == (kept, used)
    assert dsl.unused_imports("import time\nfrom sklearn.metrics import accuracy_score, f1_score\nprint(f1_score)\n") == ["import time"]
