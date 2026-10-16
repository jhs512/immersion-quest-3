"""정답 주석 달기: write rich `#` comments on every coding solution whose code changed since its
comments were written, with the Claude CLI installed on this computer.

    python tools/annotate.py             # missing or stale only
    python tools/annotate.py --all       # every coding problem
    python tools/annotate.py --ids hello variable-print
    python tools/annotate.py --check     # list what is stale, write nothing

The bare solutions stay in the unit files; the commented ones live in
tools/kpc_course/solution_comments/<problem id>.json with the hash of the bare code
(kpc_course/comments.py). The build uses the commented code wherever a student sees the
solution, and refuses to build while any cache is missing or stale. A generated version must
strip back to the bare code line for line, keep the starter's lines untouched, compile, and
still pass the problem's tests.
"""
import argparse
import concurrent.futures
import json
import os
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from kpc_course import chapters as outline, comments, dsl, narration  # noqa: E402

VOICE = (ROOT / "docs" / "voice.md").read_text(encoding="utf-8")
RULES = (ROOT / "docs" / "content-rules.md").read_text(encoding="utf-8")


def prompt_for(activity, bare, prefix):
    problem = activity["problem"]
    return f"""{RULES}

{VOICE}

아래 정답 코드에 `#` 주석을 풍부하게 달아 주세요. 코드만 답하세요(설명 없이, ```python 펜스 안에).
- 코드 줄은 글자 하나도 바꾸지 않는다. 줄을 더하거나 빼지 않는다(주석 줄만 더한다). 주석을 지우면 원래 코드와 똑같아야 한다.
- 주석은 그 줄이 무엇을 왜 하는지, 수강생이 헷갈리는 지점(따옴표, 자료형, 인덱스, 열 이름 등)을 짚는다. 줄 위에 한 줄 주석이나 줄 끝 인라인 주석.
- 주석도 수업의 말투(해요체, 짧게). 코드 2~3줄마다 하나 이상.
- '그대로 두는 준비 코드' 부분은 글자 그대로 두고, 그 아래부터 주석을 단다.

## 미션: {activity['title']}

### 문제
{problem['content']}

### 그대로 두는 준비 코드
```python
{prefix if prefix else '(없음)'}
```

### 정답 코드 (여기에 주석을 단다)
```python
{bare}
```
"""


def ask_claude(prompt):
    command = os.environ.get("MOLIP_CLAUDE", "claude")
    args = [command, "-p", "--output-format", "text"]
    if os.name == "nt":
        args = ["cmd", "/C", *args]
    result = subprocess.run(args, input=prompt, capture_output=True, text=True, encoding="utf-8", timeout=600)
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout).strip()[:300])
    return result.stdout


def parse_code(text):
    match = re.search(r"```(?:python)?\n(.*?)```", text, re.S)
    code = match.group(1) if match else text
    return code.rstrip("\n") + "\n"


def run_check(problem, commented):
    """The commented solution still produces the expected output (first test) and no traceback."""
    sys.path.insert(0, str(ROOT / "tools"))
    import importlib.util
    spec = importlib.util.spec_from_file_location("narrate", ROOT / "tools" / "narrate.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    out = module.run_solution(problem, commented)
    if "Traceback" in out:
        return f"주석을 단 코드를 실행하니 오류가 납니다: {out.strip().splitlines()[-1][:120]}"
    tests = problem.get("tests") or []
    if tests and tests[0].get("expected") and out.strip() != tests[0]["expected"].strip():
        return "주석을 단 코드의 출력이 예상 출력과 다릅니다"
    return None


def generate(activity, bare, attempts=3):
    problem = activity["problem"]
    prefix = narration._starter_prefix(problem, bare)
    prompt = prompt_for(activity, bare, prefix)
    feedback = ""
    last_error = None
    for _ in range(attempts):
        try:
            commented = parse_code(ask_claude(prompt + feedback))
        except RuntimeError as error:
            last_error = f"응답 실패: {error}"
            continue
        error = comments.check(bare, commented, prefix) or run_check(problem, commented)
        if error is None:
            return commented
        last_error = error
        feedback = f"\n\n이전 답이 검사에 걸렸습니다: {error}\n고쳐서 코드만 다시 답하세요."
    raise RuntimeError(last_error or "실패")


def main():
    parser = argparse.ArgumentParser(description="정답 주석 달기")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--ids", nargs="*", default=[])
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--jobs", type=int, default=4)
    args = parser.parse_args()
    problems = {}
    for chapter in outline.build():
        for unit in chapter["units"]:
            for activity in unit["activities"]:
                if activity["kind"] == "coding":
                    problems[activity["problem"]["id"]] = (unit, activity)
    todo = []
    for problem_id, bare in dsl.SOLUTIONS.items():
        state = comments.status(problem_id, bare)
        if args.check:
            if state != "fresh":
                print(f"  {state:6} {problem_id}")
            continue
        wanted = args.all or problem_id in args.ids or state != "fresh"
        if args.ids and problem_id not in args.ids:
            wanted = False
        if wanted:
            todo.append((problem_id, bare, state))
    if args.check:
        return
    print(f"{len(todo)}개 정답에 주석을 답니다 (Claude CLI, 동시 {args.jobs})")

    def work(item):
        problem_id, bare, state = item
        unit, activity = problems[problem_id]
        try:
            commented = generate(activity, bare)
        except Exception as error:  # noqa: BLE001
            return f"  ! {unit['id']}/{problem_id}: {error}"
        comments.write(problem_id, bare, commented, "claude")
        added = commented.count("\n") - bare.count("\n")
        return f"  ✓ {unit['id']}/{problem_id} ({state} → 주석 줄 +{added})"

    failed = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        for line in pool.map(work, todo):
            print(line, flush=True)
            failed += line.strip().startswith("!")
    if failed:
        sys.exit(f"{failed}개 실패. 다시 실행하면 실패한 것만 다시 답니다.")
    print("끝. 해설은 python tools/narrate.py, 빌드는 python tools/build-kpc-course.py.")


if __name__ == "__main__":
    main()
