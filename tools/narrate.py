"""AI 나레이션 재작업: write the 해설 script of every concept and coding mission whose content
changed since its script was written, with the Claude CLI installed on this computer.

    python tools/narrate.py              # stale or missing entries only
    python tools/narrate.py --all        # every concept and coding mission
    python tools/narrate.py --ids hello numbers-text
    python tools/narrate.py --import     # move the hand-written narration_*.py entries into the cache
    python tools/narrate.py --check      # list what is stale, block by block, write nothing
    python tools/narrate.py --stamp hello   # keep a hand-edited entry, re-record its hash and sources
    python tools/narrate.py --migrate    # record block sources for fresh entries saved without them

Each mission's script lives in tools/kpc_course/narration_cache/<id>.json with the hash of the
content it was written for (narration.source_hash) and, line by line, the source block each
line was written for (kpc_course/sources.py: 1-4-1/p3, 1-4-2/solution …). The build
(tools/build-kpc-course.py) refuses a stale entry, so "content changed → narration rewritten"
is enforced, and nothing is recomputed when nothing changed. When one block changed, only the
lines written for it are rewritten: the other lines are handed to the model to keep verbatim
and are restored afterwards whatever it answered. A generated entry must pass the same compile checks the
build runs (anchors present in the body, code chunks joining into the solution); the model
gets the error and tries again, up to three times. Coding missions include the solution's real
output so the 결과 line states what the student will actually see. No network of its own:
the CLI's login is used, like the app's tutor.
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

from kpc_course import chapters as outline, comments, dsl, narration, sources  # noqa: E402

RULES = ((ROOT / "docs" / "content-rules.md").read_text(encoding="utf-8") + "\n\n"
         + (ROOT / "docs" / "agents" / "narration.md").read_text(encoding="utf-8"))

# The one voice guide every LLM call in this project shares (the app's tutor embeds the same
# file): change docs/voice.md, not this script, to change how narrations sound.
VOICE = (ROOT / "docs" / "voice.md").read_text(encoding="utf-8")


def python_executable():
    candidates = [ROOT / "target" / "ml-env" / "Scripts" / "python.exe", ROOT / "target" / "ml-env" / "bin" / "python"]
    for c in candidates:
        if c.exists():
            return str(c)
    return os.environ.get("MOLIP_PYTHON", sys.executable)


def run_solution(problem, solution):
    """The reference solution's real output (first test input when there is one), for the 결과 line."""
    stdin = problem["tests"][0]["input"] if problem.get("tests") else ""
    try:
        # As in the app's runner (assets/python/rich_runner.py): no windows, Korean fonts.
        env = dict(os.environ, MPLBACKEND="Agg")
        prelude = ("import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as _plt; "
                   "import logging as _lg; _lg.getLogger('matplotlib.font_manager').setLevel(_lg.ERROR); from matplotlib import font_manager as _fm; _installed = {f.name for f in _fm.fontManager.ttflist}; _plt.rcParams['font.family'] = [n for n in ['Malgun Gothic', 'Apple SD Gothic Neo', 'AppleGothic', 'NanumGothic', 'Noto Sans KR', 'Noto Sans CJK KR'] if n in _installed] or ['DejaVu Sans']; "
                   "_plt.rcParams['axes.unicode_minus'] = False\n")
        result = subprocess.run([python_executable(), "-X", "utf8", "-c", prelude + solution], input=stdin, capture_output=True,
                                text=True, encoding="utf-8", timeout=120, cwd=os.environ.get("MOLIP_RUN_CWD", str(ROOT / "courses")), env=env)
        out = (result.stdout + ("\n" + result.stderr if result.returncode else "")).strip()
    except Exception as error:  # noqa: BLE001
        out = f"(실행 실패: {error})"
    return out[:1500]


def keep_section(entry, kept):
    """The existing script with the lines to keep marked, for a rewrite after a partial change."""
    if not kept:
        return ""
    rows = []
    for i, item in enumerate(entry):
        mark = "유지" if i in kept else "다시 씀"
        rows.append(f"- [{mark}] {json.dumps(list(item), ensure_ascii=False)}")
    return ("\n\n### 기존 대본\n원본이 바뀌지 않은 줄은 [유지]: 글자 그대로 다시 답한다. [다시 씀] 줄만 지금 본문에 맞게 새로 쓴다. "
            "본문 블록이 늘거나 줄었으면 줄을 더하거나 빼도 된다.\n" + "\n".join(rows))


def concept_prompt(activity, keep=""):
    check = activity["check"]
    return keep + f"""{RULES}

{VOICE}

아래 개념 미션의 해설 대본을 JSON으로만 답하세요. 형식: [["구절", "말"], ...]
- "구절"은 본문에 글자 그대로 있는 문단 앞부분 10~30자(백틱·굵게 표시는 뺀 글자). 만화·그림·코드 블록은 펜스 안의 글자(예: "제목: ...", 코드 한 줄)로 가리킨다.
- 첫 항목은 ["title", "..."]로 시작해도 되고, 마지막 항목은 ["check", "..."]로 확인 문항을 짚어도 된다. 본문의 위에서 아래 순서로 4~8줄.
- 각 "말"은 그 문단이 하는 말을 강사가 설명하듯 1~2문장으로. 본문 밖의 내용을 지어내지 않는다.

## 미션: {activity['title']}

### 본문
{activity['body']}

### 확인 문항
{check['prompt']}
(인정 답안: {', '.join(check['accepted'])}) 풀이: {check['explanation']}
"""


def coding_prompt(activity, solution, prefix, keep=""):
    problem = activity["problem"]
    rest = solution[len(prefix):] if prefix and solution.startswith(prefix) else solution
    return keep + f"""{RULES}

{VOICE}

아래 코딩 미션의 해설 대본을 JSON으로만 답하세요. 형식: 단계 목록
[["problem", "말"], ["starter", "말"], ["code", "코드 조각", "말"], ["run", "말"], ["output", "말"], ["caution", "말"], ["try", "코드 조각", "말"], ["run", "말"], ["output", "말"], ["undo", "말"], ["code", "코드 조각", "말"], ["run", "말"], ["output", "말"], ..., ["submit", "말"]]
- 살짝 코딩 → 실행 → 출력 읽기를 반복한다: 한 번에 다 쓰고 끝에 한 번 실행하지 않는다. 조각은 1~3줄, 조각마다(또는 두 조각마다) run과 output을 넣는다. 실행했을 때 오류 없이 무언가 보이는 자리에서 run 한다(예: 변수를 만든 뒤 print로 확인).
- "이렇게 해볼까요? 이렇게 하기 쉬운데, 그러면 이런 문제가 생기니 조심하세요"를 1~2번 넣는다. 방법은 둘 중 하나: ["try", 틀리기 쉬운 코드, "이렇게 해 볼까요?"] → ["run", ...] → ["output", 무엇이 잘못됐는지] → ["undo", "그래서 이렇게 고쳐요"]로 실제로 보여 주거나, 코드를 치지 않고 ["caution", "…하기 쉬운데 …하니 조심하세요"]로 말만 한다. try는 반드시 undo로 되돌린다.
- "code" 조각들을 순서대로 이어 붙이면(try는 undo로 되돌린 뒤) 아래 '타이핑할 코드'와 글자 하나까지 같아야 한다(띄어쓰기·줄 바꿈 포함). 조각을 더 잘게 나눌 수는 있지만 글자를 바꾸면 안 된다.
- "starter"는 준비 코드가 있을 때만 넣고, 무엇이 준비되어 있는지 말한다. "examples", "hint", "input"은 필요할 때만.
- "output"은 그 시점에 실제로 나오는 값을 말한다. 지금은 모르면 "결과를 보세요"처럼 두면 되고, 제가 실제 출력을 알려 주면 그때 고쳐 쓴다.
- 마지막은 run → output → submit.

## 미션: {activity['title']}

### 문제
{problem['content']}

### 그대로 두는 준비 코드
```python
{prefix if prefix else '(없음: 첫 조각이 편집기를 비우고 시작)'}
```

### 타이핑할 코드 (조각을 이으면 이것과 같아야 함)
```python
{rest}
```
"""


def outputs_prompt(activity, entry, outputs):
    """Second pass: the real output at every run, so each output line says what is on screen."""
    rows = []
    run_index = 0
    for i, step in enumerate(entry):
        mark = ""
        if step[0] == "run":
            mark = f"   ← 실제 출력:\n```\n{outputs[run_index]}\n```"
            run_index += 1
        rows.append(f"{i + 1}. {json.dumps(list(step), ensure_ascii=False)}{mark}")
    return f"""{VOICE}

아래는 코딩 미션 「{activity['title']}」의 해설 대본과, 각 run 시점에 실제로 나온 출력입니다.
"output" 줄만 실제 출력에 맞게 다시 쓰세요(값을 말하고, 길면 무엇을 볼지를 말한다). try 뒤의 output은 무엇이 잘못됐는지 실제 출력으로 설명한다.
다른 줄은 글자 그대로 두고, 전체 목록을 같은 형식의 JSON으로만 답하세요.

{chr(10).join(rows)}
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


def parse_entry(text):
    match = re.search(r"\[\s*\[.*\]\s*\]", text, re.S)
    if not match:
        raise ValueError("JSON 목록을 찾지 못했습니다")
    entry = json.loads(match.group(0))
    return [tuple(item) for item in entry]


def validate(activity, entry, solution):
    """The build's own compile; returns the error text or None."""
    try:
        if activity["kind"] == "concept":
            narration.compile_concept(activity, entry, activity["id"])
        else:
            narration.compile_coding(activity, entry, solution, activity["id"])
    except SystemExit as error:
        return str(error)
    return None


def run_states(activity, entry, solution):
    """The real output at every run of a coding entry, in order."""
    problem = activity["problem"]
    prefix = narration._starter_prefix(problem, solution)
    outputs = []
    text = prefix
    tried = []
    for step in entry:
        kind = step[0]
        if kind in ("code", "try"):
            if kind == "try":
                tried.append(text)
            text = text + step[1].rstrip("\n") + "\n"
        elif kind == "undo":
            text = tried.pop()
        elif kind == "run":
            outputs.append(run_solution(problem, text))
    return outputs


def run_errors(entry, outputs):
    """Runs that crashed where the script did not mean to show a mistake: a run right after a
    plain code chunk must not end in a traceback."""
    problems = []
    run_index = 0
    last_typed = None
    for step in entry:
        if step[0] in ("code", "try", "undo"):
            last_typed = step[0]
        elif step[0] == "run":
            out = outputs[run_index]
            run_index += 1
            if "Traceback" in out and last_typed != "try":
                problems.append(f"{run_index}번째 run이 오류로 끝납니다 (try가 아닌 조각 뒤): {out.strip().splitlines()[-1][:120]}")
    return problems


def restore_except_outputs(fixed, entry):
    """The second pass may only change output lines: everything else comes back from `entry`."""
    if len(fixed) != len(entry):
        return entry
    out = []
    for new, old in zip(fixed, entry):
        out.append(tuple(new) if old[0] == "output" and new[0] == "output" else old)
    return out


def restore_kept(entry, previous, kept):
    """Put the kept lines back exactly as they were: a concept line by its anchor, a coding
    step by its name (code chunks by their code)."""
    kept_items = [previous[i] for i in kept]
    out = []
    for item in entry:
        match = next((k for k in kept_items if k[0] == item[0] and (k[0] != "code" or k[1] == item[1])), None)
        out.append(match if match is not None else item)
    return out


def generate(activity, solution, attempts=3, previous=None, kept=()):
    """A new entry; with `previous` and `kept` (line indexes whose source did not change), a
    rewrite of the other lines only."""
    keep = keep_section(previous, kept) if previous else ""
    if activity["kind"] == "coding":
        problem = activity["problem"]
        solution = solution.rstrip("\n") + "\n"
        prefix = narration._starter_prefix(problem, solution)
        prompt = coding_prompt(activity, solution, prefix, keep)
    else:
        prompt = concept_prompt(activity, keep)
    feedback = ""
    last_error = None
    for _ in range(attempts):
        try:
            entry = parse_entry(ask_claude(prompt + feedback))
        except (ValueError, json.JSONDecodeError, RuntimeError) as error:
            last_error = f"응답 해석 실패: {error}"
            feedback = f"\n\n이전 답은 JSON으로 읽히지 않았습니다 ({error}). JSON 목록만 다시 답하세요."
            continue
        if previous and kept:
            entry = restore_kept(entry, previous, kept)
        error = validate(activity, entry, solution)
        if error is None and activity["kind"] == "coding":
            # Every run really runs; then the output lines are rewritten from what came out.
            outputs = run_states(activity, entry, solution)
            crashed = run_errors(entry, outputs)
            if crashed:
                error = "\n".join(crashed)
            else:
                try:
                    fixed = parse_entry(ask_claude(outputs_prompt(activity, entry, outputs)))
                    candidate = restore_except_outputs(fixed, entry)
                    if validate(activity, candidate, solution) is None:
                        entry = candidate
                except (ValueError, json.JSONDecodeError, RuntimeError):
                    pass  # the first-pass output lines stay
        if error is None:
            return entry
        last_error = error
        feedback = f"\n\n이전 답이 검사에 걸렸습니다:\n{error}\n고쳐서 JSON 목록만 다시 답하세요."
    raise RuntimeError(last_error or "실패")


def missions(chapters):
    for chapter in chapters:
        for unit in chapter["units"]:
            for activity in unit["activities"]:
                if activity["kind"] in ("concept", "coding"):
                    yield unit, activity


def main():
    parser = argparse.ArgumentParser(description="AI 나레이션 재작업")
    parser.add_argument("--all", action="store_true", help="모든 개념·코딩 미션을 다시 쓴다")
    parser.add_argument("--kind", choices=["concept", "coding"], help="이 종류의 미션만 (--all과 함께)")
    parser.add_argument("--ids", nargs="*", default=[], help="이 미션들만")
    parser.add_argument("--import", dest="import_modules", action="store_true", help="narration_*.py의 손글 항목을 캐시로 옮긴다")
    parser.add_argument("--check", action="store_true", help="낡은 항목만 나열한다")
    parser.add_argument("--stamp", nargs="*", help="손으로 고친 해설을 그대로 두고 해시만 지금 내용으로 다시 찍는다 (미션 id들)")
    parser.add_argument("--migrate", action="store_true", help="원본 블록 기록이 없는 해설에 지금 블록을 기록한다 (내용이 바뀌지 않은 것만)")
    parser.add_argument("--jobs", type=int, default=4)
    args = parser.parse_args()

    chapters = outline.build()
    # The commented solutions: the 해설 types code with its comments (docs/content-rules.md 3).
    solutions = comments.apply(dsl.SOLUTIONS)
    todo = []
    for unit, activity in missions(chapters):
        solution = solutions[activity["problem"]["id"]] if activity["kind"] == "coding" else None
        hash_ = narration.source_hash(activity, solution)
        entry, status = narration.entry_for(activity, solution)
        cached = narration.read_cache(activity["id"])
        if args.migrate:
            incomplete = cached is not None and (not cached.get("sources") or not cached.get("blocks"))
            if incomplete and cached["hash"] == hash_:
                narration.write_cache(activity["id"], hash_, entry, cached.get("by", "claude"), narration.line_sources(activity, entry, solution), sources.index(activity, solution))
                print(f"  → {activity['id']} (원본 블록 기록)")
            elif incomplete:
                print(f"  ! {activity['id']}: 내용이 바뀌어 기록할 수 없습니다. python tools/narrate.py 로 다시 쓰세요.")
            continue
        if args.stamp is not None:
            if activity["id"] in args.stamp:
                if entry is None:
                    print(f"  ! {activity['id']}: 해설이 없습니다")
                    continue
                error = validate(activity, entry, solution)
                if error:
                    print(f"  ! {activity['id']}: {error}")
                    continue
                narration.write_cache(activity["id"], hash_, entry, "hand", narration.line_sources(activity, entry, solution), sources.index(activity, solution))
                print(f"  → {activity['id']} (해시·원본 블록 갱신)")
            continue
        if args.import_modules:
            if status == "module":
                error = validate(activity, entry, solution)
                if error:
                    print(f"  ! {activity['id']}: {error}")
                    continue
                narration.write_cache(activity["id"], hash_, entry, "hand", narration.line_sources(activity, entry, solution), sources.index(activity, solution))
                print(f"  → {activity['id']} (캐시로 옮김)")
            continue
        wanted = args.all or activity["id"] in args.ids or status in ("stale", "none", "module")
        if args.ids and activity["id"] not in args.ids:
            wanted = False
        if args.kind and activity["kind"] != args.kind:
            wanted = False
        # A stale entry keeps the lines whose source block did not change.
        kept = []
        changed_keys = []
        if status == "stale" and cached is not None and cached.get("sources") and not args.all:
            changed_keys, kept, why = narration.stale_report(activity, cached, solution)
        else:
            why = ""
        if args.check:
            if status != "fresh":
                print(f"  {status:6} {unit['id']}/{activity['id']}" + (f"\n         {why}" if why else ""))
            continue
        # Every line's block is unchanged and no block vanished (a block no line mentions was
        # edited, or one was added): nothing to rewrite, so only the hashes are re-recorded.
        now_keys = sources.index(activity, solution)
        vanished = any(key in (cached.get("blocks") or {}) and key not in now_keys for key in changed_keys) if cached else False
        if status == "stale" and kept and len(kept) == len(entry) and not vanished and not args.ids:
            narration.write_cache(activity["id"], hash_, entry, cached.get("by", "claude"), narration.line_sources(activity, entry, solution), now_keys)
            print(f"  = {unit['id']}/{activity['id']} (해설 줄이 가리키는 블록은 그대로: 해시만 갱신)")
            continue
        if wanted:
            todo.append((unit, activity, solution, hash_, status, entry if kept else None, kept))
    if args.import_modules or args.check or args.stamp is not None or args.migrate:
        return
    print(f"{len(todo)}개 미션의 해설을 다시 씁니다 (Claude CLI, 동시 {args.jobs})")

    def work(item):
        unit, activity, solution, hash_, status, previous, kept = item
        try:
            entry = generate(activity, solution, previous=previous, kept=kept)
        except Exception as error:  # noqa: BLE001
            return f"  ! {unit['id']}/{activity['id']}: {error}"
        narration.write_cache(activity["id"], hash_, entry, "claude", narration.line_sources(activity, entry, solution), sources.index(activity, solution))
        how = f"{len(kept)}줄 유지, 나머지 새로" if kept else f"새 해설 {len(entry)}줄"
        return f"  ✓ {unit['id']}/{activity['id']} ({status} → {how})"

    failed = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        for line in pool.map(work, todo):
            print(line, flush=True)
            failed += line.strip().startswith("!")
    if failed:
        sys.exit(f"{failed}개 실패. 다시 실행하면 실패한 것만 다시 씁니다.")
    print("끝. python tools/build-kpc-course.py 로 빌드하세요.")


if __name__ == "__main__":
    if sys.argv[1:2] == ["--redesigned-aice-first"]:
        subprocess.run([sys.executable, str(ROOT / "tools/build-redesigned-git.py"), "--lesson", "aice-python-start", *sys.argv[2:]], check=True)
    elif sys.argv[1:2] == ["--redesigned-java"]:
        subprocess.run([sys.executable, str(ROOT / "tools/build-redesigned-git.py"), "--lesson", "java-values", *sys.argv[2:]], check=True)
    elif sys.argv[1:2] == ["--redesigned-git"]:
        subprocess.run([sys.executable, str(ROOT / "tools/build-redesigned-git.py"), *sys.argv[2:]], check=True)
    elif sys.argv[1:2] == ["--redesigned-git-first"]:
        subprocess.run([sys.executable, str(ROOT / "tools/build-redesigned-git-first.py"), *sys.argv[2:]], check=True)
    elif sys.argv[1:2] == ["--saturday-specials"]:
        subprocess.run([sys.executable, str(ROOT / "tools/build-saturday-specials.py"), *sys.argv[2:]], check=True)
    elif sys.argv[1:] == ["--certification-foundations"]:
        subprocess.run([sys.executable, str(ROOT / "tools/build-certification-foundations.py")], check=True)
    elif sys.argv[1:] == ["--certification-pilots"]:
        subprocess.run([sys.executable, str(ROOT / "tools/build-certification-pilots.py")], check=True)
    elif sys.argv[1:] == ["--principles"]:
        subprocess.run([sys.executable, str(ROOT / "tools/build-principles-course.py")], check=True)
    elif sys.argv[1:] == ["--backend"]:
        subprocess.run([sys.executable, str(ROOT / "tools/build-backend-course.py")], check=True)
    elif sys.argv[1:] == ["--java"]:
        # Java narration is authored with runnable stages; cache hashes retain
        # unchanged missions, and each new stage is executed on JDK 25.
        subprocess.run([sys.executable, str(ROOT / "tools/build-java-course.py")], check=True)
    else:
        main()
