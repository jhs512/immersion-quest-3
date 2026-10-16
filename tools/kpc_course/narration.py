"""해설 모드 scripts, compiled at build time so /auto and /auto-all play at once, without a CLI.

Every mission carries `narration`: the list of agent actions (assets/layout/agent.js) that the
tutor would otherwise have to improvise. The app runs them straight away and shows the lines.

- Slides: compiled from the deck's presenter script (one line per slide, then finish).
- Quizzes: compiled from each question's explanation, then the answers are filled and graded.
- Concepts and coding problems: one file per mission in narration_cache/<id>.json, written by
  tools/narrate.py (the Claude CLI) or by hand. The file records a hash of the content it was
  written for; when the content changes the build refuses until `python tools/narrate.py`
  rewrites the stale entries (only those). The entry formats:
  * A concept entry is a list of (anchor, line). `anchor` is a fragment of the body text (as
    the student reads it: no backticks or bold); the app scrolls that block into view and
    speaks `line`. `"title"` points at the heading, `"check"` at the check question. The check
    is then answered with its explanation as the spoken 풀이.
  * A coding entry is a list of steps: ("problem", line), ("examples", line), ("hint", line),
    ("starter", line), ("code", chunk, line), ("run", line), ("output", line), ("submit", line).
    The code chunks, after the starter's own code lines, must join into the reference solution
    exactly. problem/run/output/submit get default lines when left out.

The rule this module enforces: when a body or a solution changes, its narration changes too.
A stale hash, a stale anchor or a chunk set that no longer matches the solution fails the build.
"""
import hashlib
import importlib
import json
import os
import pathlib
import re

# Bump when the narration format or voice rules change, so every entry counts as stale.
RULES_VERSION = "2"
CACHE_DIR = pathlib.Path(__file__).parent / "narration_cache"


def source_hash(activity, solution=None):
    """What a narration was written for: the words the student sees and, for a problem, the
    reference solution. Same hash → the narration still fits."""
    if activity["kind"] == "concept":
        parts = [activity["title"], activity["body"], activity["check"]["prompt"], activity["check"]["explanation"]]
    elif activity["kind"] == "coding":
        problem = activity["problem"]
        parts = [activity["title"], problem["content"], problem["starter_code"], solution or ""]
    else:
        parts = [activity["title"], json.dumps(activity.get("questions", activity.get("markdown", "")), ensure_ascii=False, sort_keys=True)]
    return hashlib.sha256(("\n--\n".join([RULES_VERSION, *parts])).encode("utf-8")).hexdigest()[:16]


def cache_path(activity_id):
    return CACHE_DIR / f"{activity_id}.json"


def read_cache(activity_id):
    """{"hash", "entry", "by", "sources"} or None. `sources` (cache format 2) records, line by
    line, the source block each line was written for: [{"block": "p3", "hash": "…"}, …]."""
    path = cache_path(activity_id)
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    data["entry"] = [tuple(item) for item in data["entry"]]
    data.setdefault("sources", None)
    return data


def write_cache(activity_id, hash_, entry, by, sources, blocks=None):
    """`sources`: the block each line is written for; `blocks`: every block of the mission at
    that time ({key: hash}), so a block that appears or vanishes later is reported as such."""
    CACHE_DIR.mkdir(exist_ok=True)
    data = {"format": 2, "hash": hash_, "by": by, "blocks": blocks or {}, "sources": sources, "entry": [list(item) for item in entry]}
    cache_path(activity_id).write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


# Which source block each kind of coding step is written for (sources.py keys).
CODING_STEP_BLOCK = {"problem": "problem", "examples": "example", "hint": "problem", "starter": "starter",
                     "code": "solution", "try": "solution", "undo": "solution", "caution": "solution",
                     "run": "solution", "input": "example", "output": "solution", "submit": "solution"}


def line_sources(activity, entry, solution=None):
    """For each line of a narration entry, the block it is written for and that block's hash
    now: [{"block": key, "hash": hash}]. A concept line points at the block its anchor phrase
    sits in; a coding step at the problem, example, starter or solution."""
    index = sources.index(activity, solution)
    out = []
    for item in entry:
        if activity["kind"] == "concept":
            anchor = spoken(item[0])
            key = "title" if anchor == "title" else "check" if anchor == "check" else sources.find_block(activity, anchor, spoken)
        else:
            key = CODING_STEP_BLOCK.get(item[0])
        if key is None or key not in index:
            raise SystemExit(f"{activity['id']}: 해설 줄 {item[0]!r}가 가리키는 원본 블록을 찾지 못했습니다.")
        out.append({"block": key, "hash": index[key]})
    return out


def stale_report(activity, cached, solution=None):
    """Why a cached entry is stale, block by block: which blocks changed, appeared or vanished,
    and which lines of the entry are written for a changed block. Lines whose block is unchanged
    can be kept as they are. Returns (changed_keys, kept_line_indexes, text)."""
    number = sources.mission_number(activity)
    now = dict(sources.blocks(activity, solution))
    index = {key: sources.content_hash(text) for key, text in now.items()}
    recorded = cached.get("sources")
    if not recorded:
        return list(index), [], f"{number}: 해설이 원본 블록 기록 없이 저장돼 있습니다 (python tools/narrate.py --migrate)."
    before = dict(cached.get("blocks") or {})
    for line in recorded:
        before.setdefault(line["block"], line["hash"])
    changed = [key for key in index if key in before and before[key] != index[key]]
    added = [key for key in index if key not in before]
    gone = [key for key in before if key not in index]
    kept = [i for i, line in enumerate(recorded) if line["block"] in index and index[line["block"]] == line["hash"]]
    affected = [i for i in range(len(recorded)) if i not in kept]
    parts = []
    for key in changed:
        parts.append(f"{number}/{key} 바뀜 「{sources.excerpt(now[key])}」")
    for key in added:
        parts.append(f"{number}/{key} 새 블록 「{sources.excerpt(now[key])}」")
    for key in gone:
        parts.append(f"{number}/{key} 없어짐")
    lines = ", ".join(str(i + 1) for i in affected) or "없음"
    text = "; ".join(parts) + f" → 다시 쓸 해설 줄: {lines} (전체 {len(recorded)}줄 중 {len(kept)}줄은 그대로)"
    return changed + added + gone, kept, text


from kpc_course import sources
from kpc_course.dsl import split_slides

def load():
    """Hand-written entries in tools/kpc_course/narration_*.py, merged by activity id (the
    pre-cache form; tools/narrate.py --import moves them into the cache)."""
    table = {}
    here = pathlib.Path(__file__).parent
    for path in sorted(here.glob("narration_*.py")):
        module = importlib.import_module(f"kpc_course.{path.stem}")
        for key, value in module.NARRATION.items():
            if key in table:
                raise SystemExit(f"narration: '{key}'가 두 모듈에 있습니다.")
            table[key] = value
    return table


def entry_for(activity, solution):
    """The narration entry for a concept or coding mission: the cache file when it is fresh,
    a module entry otherwise. Returns (entry, status) with status fresh / stale / module / none.
    A cache file without block sources (format 1) counts as stale until --migrate records them."""
    cached = read_cache(activity["id"])
    if cached is not None:
        fresh = cached["hash"] == source_hash(activity, solution) and bool(cached.get("sources"))
        return cached["entry"], ("fresh" if fresh else "stale")
    entry = load().get(activity["id"])
    return entry, ("module" if entry is not None else "none")


FENCE = re.compile(r"```.*?```", re.S)
COMMENT = re.compile(r"<!--.*?-->", re.S)


def spoken(text):
    """Markdown prose as it is read aloud and shown in the caption: no bold, code marks or links."""
    text = COMMENT.sub("", str(text))
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"`([^`\n]+)`", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"^#+\s*", "", text, flags=re.M)
    return re.sub(r"[ \t]+", " ", text).strip()


def body_text(markdown):
    """The concept body as the browser shows it: fences become their own text, prose loses marks."""
    parts = []
    for block in FENCE.split(markdown):
        parts.append(spoken(block))
    for fence in FENCE.findall(markdown):
        parts.append(fence.strip("`").strip())
    return "\n".join(parts)


def _say(target, text):
    return {"action": "say", "target": target, "text": spoken(text)}


def compile_slides(deck):
    front, parts = split_slides(deck["markdown"])
    actions = []
    for n, part in enumerate(parts):
        inner = [c[4:-3].strip() for c in COMMENT.findall(part)]
        line = " ".join(spoken(c) for c in inner if c and not c.startswith("_"))
        if not line:
            raise SystemExit(f"{deck['id']}: {n + 1}번째 장에 스크립트가 없어 해설을 만들 수 없습니다.")
        actions.append(_say("slides", line))
        if n + 1 < len(parts):
            actions.append({"action": "next_slide"})
    actions.append({"action": "finish_slides"})
    return actions


def _answer(question):
    """What answer_quiz fills in: the 1-based option number (options are shuffled at build
    time, so the number is final), or the first accepted short answer."""
    if question["type"] == "choice":
        return str(question["correct"] + 1)
    if question["type"] == "table_select":
        return ",".join(str(i + 1) for i in _selection(question))
    return question["accepted"][0]


def _selection(question):
    """One selection that satisfies a 표 고르기 rule: the required ones, then rows that fill
    each quota, then more allowed ones up to the minimum size. Fails the build if none works."""
    table, pick, rule = question["table"], question["pick"], question["rule"]
    count = len(table["rows"]) if pick == "rows" else len(table["columns"])
    allowed = set(rule.get("allowed", range(count)) if rule.get("allowed") is not None else range(count))
    allowed -= set(rule.get("forbidden", []))
    picked = list(rule.get("required", []))
    for quota in rule.get("quota", []):
        column = table["columns"].index(quota["column"])
        have = sum(1 for r in picked if table["rows"][r][column].strip() == quota["value"].strip())
        for r in range(count):
            if have >= quota["count"]:
                break
            if r in picked or r not in allowed:
                continue
            if table["rows"][r][column].strip() == quota["value"].strip():
                picked.append(r)
                have += 1
    low = rule.get("size", [0, count])[0]
    for r in range(count):
        if len(picked) >= low:
            break
        if r not in picked and r in allowed:
            picked.append(r)
    picked.sort()
    if rule.get("size") and not rule["size"][0] <= len(picked) <= rule["size"][1]:
        raise SystemExit(f"표 고르기 문항의 규칙을 만족하는 답을 찾지 못했습니다: {question['prompt'][:40]}")
    return picked


def _pick_line(question, answer):
    """What the tutor says while ticking: the option (short ones in full), the typed answer,
    or the model selection of a table."""
    if question["type"] == "choice":
        option = spoken(question["options"][int(answer) - 1])
        return f"{answer}번, {option}. 이걸 고를게요." if len(option) <= 40 else f"{answer}번 보기를 고를게요."
    if question["type"] == "short_answer":
        return f"답은 {spoken(answer)}. 이렇게 적을게요."
    return f"{spoken(question['expected'])}. 이렇게 고를게요."


WRONG_HEADING = re.compile(r"\*\*다른 보기는 왜 아닌가\*\*|다른 보기는 왜 아닌가")
WRONG_BULLET = re.compile(r"^\s*[-*]\s*「(.+?)」\s*[:：]\s*(.+?)\s*$")


def _option_index(question, label):
    """1-based index of the option a 「label」 bullet names, by its text without marks."""
    wanted = spoken(label)
    options = [spoken(o) for o in question.get("options", [])]
    for i, option in enumerate(options, start=1):
        if option == wanted or option.startswith(wanted):
            return i
    for i, option in enumerate(options, start=1):
        if wanted in option or option in wanted:
            return i
    return None


def topic_particle(text):
    """은 or 는 after `text`, by the final sound: Hangul batchim, a digit's Korean reading, or a
    Latin letter that ends in a consonant sound (l, m, n). Trailing marks are skipped."""
    stripped = text.rstrip(" .,!?)]}'\"」』")
    if not stripped:
        return "은"
    last = stripped[-1]
    if "가" <= last <= "힣":
        return "은" if (ord(last) - 0xAC00) % 28 else "는"
    if last.isdigit():
        return "은" if last in "013678" else "는"
    if last.lower() in "lmn":
        return "은"
    if last.lower() == "t" and len(stripped) > 1 and stripped[-2].lower() in "aeiou":
        return "은"  # fit → 핏, get → 겟 (but test → 테스트)
    return "는"


def explanation_lines(n, question):
    """The spoken lines of a question's explanation: the reasoning at the question, then one
    line per wrong option at that option (the 「…」 bullets under 다른 보기는 왜 아닌가)."""
    explanation = question["explanation"]
    parts = WRONG_HEADING.split(explanation, maxsplit=1)
    main = parts[0].strip()
    lines = [_say(f"quiz:{n}", f"{n}번. " + main)] if main else []
    if len(parts) > 1:
        for raw in parts[1].splitlines():
            match = WRONG_BULLET.match(raw)
            if not match:
                continue
            label, reason = match.groups()
            index = _option_index(question, label) if question["type"] == "choice" else None
            name = spoken(label)
            text = f"{name}{topic_particle(name)} 아니에요. {spoken(reason)}"
            lines.append(_say(f"option:{n}:{index}" if index else f"quiz:{n}", text))
    return lines


def compile_quiz(activity):
    """Each question: the reasoning, each wrong option named at its place, then the tick (choice,
    typed answer or table picks) on screen; grading once at the end."""
    actions = []
    for n, question in enumerate(activity["questions"], start=1):
        answer = _answer(question)
        actions.extend(explanation_lines(n, question))
        actions.append({"action": "answer_quiz", "answers": {str(n): answer}, "submit": False, "say": _pick_line(question, answer)})
    actions.append({"action": "answer_quiz", "answers": {}, "say": "자, 다 넣었으니 채점할게요."})
    return actions


def compile_concept(activity, entry, where):
    if not isinstance(entry, (list, tuple)) or not entry:
        raise SystemExit(f"{where}: 개념 해설은 (구절, 말) 목록이어야 합니다.")
    text = body_text(activity["body"])
    actions = []
    for item in entry:
        if not (isinstance(item, (list, tuple)) and len(item) == 2):
            raise SystemExit(f"{where}: 개념 해설 항목은 (구절, 말) 둘이어야 합니다 → {item!r}")
        anchor, line = item
        anchor = spoken(anchor)
        if anchor == "title":
            actions.append(_say("title", line))
        elif anchor == "check":
            actions.append(_say("quiz:1", line))
        else:
            if anchor not in text:
                raise SystemExit(f"{where}: 해설이 가리키는 구절이 본문에 없습니다 → {anchor!r}. 본문을 바꿨다면 해설도 고치세요.")
            actions.append(_say("text:" + anchor, line))
    check = activity["check"]
    actions.append({"action": "answer_quiz", "answers": {"1": _answer(check)}, "say": spoken(check["explanation"])})
    return actions


def _starter_prefix(problem, solution):
    """The starter's own code (its trailing '# ...하세요' comment lines dropped) when the solution
    begins with it; the narration keeps that part and types only what follows."""
    lines = problem["starter_code"].rstrip("\n").split("\n")
    while lines and (not lines[-1].strip() or lines[-1].lstrip().startswith("#")):
        lines.pop()
    prefix = "\n".join(lines) + "\n" if lines else ""
    return prefix if prefix and solution.startswith(prefix) else ""


def _default_problem_line(problem):
    goal = problem["content"].split("### 목표", 1)[-1].split("### 힌트", 1)[0]
    paragraph = next((p for p in FENCE.sub("", goal).split("\n\n") if p.strip()), "")
    return "자, 문제부터 볼게요. " + spoken(paragraph)


CODING_STEPS = {"problem", "examples", "hint", "starter", "code", "try", "undo", "run", "input", "output", "caution", "submit"}


def coding_states(entry, prefix):
    """The editor's text after each step of a coding entry, following the agent: `code` and
    `try` append a chunk, `undo` puts the text back to what it was before the last `try`.
    Returns [(step, text_after)] and raises on a stray undo or an unfinished try."""
    text = prefix
    tried = []
    states = []
    for step in entry:
        kind = step[0]
        if kind in ("code", "try"):
            if kind == "try":
                tried.append(text)
            text = text + step[1].rstrip("\n") + "\n"
        elif kind == "undo":
            if not tried:
                raise SystemExit("되돌릴 try가 없습니다")
            text = tried.pop()
        states.append((step, text))
    if tried:
        raise SystemExit("try를 undo로 되돌리지 않았습니다")
    return states


def compile_coding(activity, entry, solution, where):
    """A coding 해설 builds the program a little at a time: code → run → read the output, again
    and again, with a tempting mistake tried and taken back (try/undo) or a spoken caution on
    the way. The build refuses a script that types everything and runs once at the end."""
    if not isinstance(entry, (list, tuple)) or not entry:
        raise SystemExit(f"{where}: 코딩 해설은 단계 목록이어야 합니다.")
    problem = activity["problem"]
    solution = solution.rstrip("\n") + "\n"
    prefix = _starter_prefix(problem, solution)
    for step in entry:
        if not step or step[0] not in CODING_STEPS:
            raise SystemExit(f"{where}: 모르는 해설 단계 {step!r} (가능: {', '.join(sorted(CODING_STEPS))})")
        if step[0] in ("code", "try") and len(step) != 3:
            raise SystemExit(f"{where}: {step[0]} 단계는 ('{step[0]}', 코드, 말) 셋이어야 합니다.")
        if step[0] not in ("code", "try") and len(step) != 2:
            raise SystemExit(f"{where}: {step[0]} 단계는 ('{step[0]}', 말) 둘이어야 합니다.")
    steps = {step[0]: step for step in entry if step[0] in ("problem", "examples", "hint", "starter", "input", "submit")}
    chunks = [step for step in entry if step[0] == "code"]
    if not chunks:
        raise SystemExit(f"{where}: 코딩 해설에 code 단계가 없습니다.")
    try:
        states = coding_states([step for step in entry if step[0] in ("code", "try", "undo")], prefix)
    except SystemExit as error:
        raise SystemExit(f"{where}: {error}") from None
    final = states[-1][1] if states else prefix
    if final != solution:
        raise SystemExit(f"{where}: 해설의 코드 조각을 이으면(try는 undo로 되돌린 뒤) 정답 코드가 되어야 합니다. 정답을 바꿨다면 해설도 고치세요.\n--- 조각을 이은 것\n{final}\n--- 정답\n{solution}")
    if prefix and "starter" not in steps:
        pass
    elif not prefix and "starter" in steps:
        raise SystemExit(f"{where}: 정답이 준비 코드로 시작하지 않아 starter 단계를 쓸 수 없습니다.")
    # The rule: a run (with its output read) after the chunks, not one run at the very end.
    kinds = [step[0] for step in entry]
    runs = kinds.count("run")
    if len(chunks) >= 2 and runs < 2:
        raise SystemExit(f"{where}: 코드를 조금 쓰고 실행해 보는 걸 반복해야 합니다 (조각 {len(chunks)}개에 실행 {runs}번). 조각 사이에 run과 output을 넣으세요.")
    typed_since_run = False
    for kind in kinds:
        if kind in ("code", "try", "undo"):
            typed_since_run = True
        elif kind == "run":
            if not typed_since_run:
                raise SystemExit(f"{where}: 코드를 더 쓰지 않고 run을 반복했습니다.")
            typed_since_run = False
    if typed_since_run:
        raise SystemExit(f"{where}: 마지막 조각 뒤에 run과 output이 있어야 제출할 수 있습니다.")
    for i, kind in enumerate(kinds):
        if kind == "output" and (i == 0 or kinds[i - 1] != "run"):
            raise SystemExit(f"{where}: output은 run 바로 뒤에 옵니다.")
        if kind == "run" and (i + 1 >= len(kinds) or kinds[i + 1] != "output"):
            raise SystemExit(f"{where}: run 뒤에는 output(결과 읽기)이 와야 합니다.")
    if "try" not in kinds and "caution" not in kinds:
        raise SystemExit(f"{where}: 「이렇게 하기 쉬운데 … 조심하세요」가 하나는 있어야 합니다 (try/undo 또는 caution).")
    if kinds[-1] != "submit":
        raise SystemExit(f"{where}: 마지막 단계는 submit이어야 합니다.")
    actions = [_say("problem", steps["problem"][1] if "problem" in steps else _default_problem_line(problem))]
    if "examples" in steps:
        actions.append(_say("examples", steps["examples"][1]))
    elif problem.get("tests"):
        first = problem["tests"][0]
        shown_input = first["input"].strip().replace("\n", ", ") or "없음"
        actions.append(_say("examples", f"예제를 보면 입력이 {shown_input}일 때 {first['expected'].strip()}이 나와야 해요."))
    if "hint" in steps:
        actions.append(_say("hint", steps["hint"][1]))
    if prefix:
        actions.append({"action": "set_code", "code": prefix,
                        "say": steps["starter"][1] if "starter" in steps else "준비 코드는 그대로 두고, 그 아래에 이어서 써요."})
    typed_any = False
    text = prefix
    tried = []
    for step in entry:
        kind = step[0]
        if kind in ("code", "try"):
            if kind == "try":
                tried.append(text)
            action = {"action": "type_code", "code": step[1].rstrip("\n") + "\n", "say": spoken(step[2])}
            if not typed_any and not prefix:
                action["replace"] = True
            typed_any = True
            text = text + step[1].rstrip("\n") + "\n"
            actions.append(action)
        elif kind == "undo":
            text = tried.pop()
            actions.append({"action": "set_code", "code": text, "say": spoken(step[1])})
        elif kind == "run":
            actions.append({"action": "run", "say": spoken(step[1])})
        elif kind == "output":
            actions.append(_say("output", step[1]))
        elif kind == "caution":
            actions.append(_say("editor", step[1]))
        elif kind == "input":
            actions.append(_say("input", step[1]))
        elif kind == "submit":
            actions.append({"action": "submit", "say": spoken(step[1])})
    return actions


SENTENCE_END = re.compile(r"(?<=[.?!])\s+")
# A sentence that only leads into the next one ("자, 실행해 볼게요.", "정리하면 이거예요.") says
# nothing on its own and is skipped when the gist is picked.
LEAD_IN = re.compile(r"(할게요|볼게요|갈게요|볼까요|할까요|이거예요|다음 장이에요|거든요|잖아요|되죠|보세요|볼 거예요)[.?!]?$")


def _sentences(text, limit, substantive=True):
    """The first `limit` sentences of a spoken line, lead-ins dropped and a leading 자, trimmed."""
    out = []
    for sentence in SENTENCE_END.split(spoken(text).strip()):
        sentence = re.sub(r"^자,\s*", "", sentence.strip())
        if not sentence or (substantive and LEAD_IN.search(sentence)):
            continue
        out.append(sentence)
        if len(out) == limit:
            break
    return out


def compile_tour(activity):
    """The 1~3 sentences `/tour-all` says before it fills the mission in and moves on: the gist
    of the compiled 해설, not a new text. A concept gives its first and last explained passage
    and the check's answer; a coding problem its task, how the code does it and what comes out;
    a quiz its size and the first answers; a deck its opening point and its closing summary."""
    actions = activity["narration"]
    says = [a for a in actions if a["action"] == "say"]
    kind = activity["kind"]
    picks = []
    if kind == "concept":
        text_lines = [a["text"] for a in says if str(a.get("target", "")).startswith("text:")]
        if text_lines:
            picks += _sentences(text_lines[0], 1)
            if len(text_lines) > 1:
                picks += _sentences(text_lines[-1], 1)
        picks += _sentences(activity["check"]["explanation"], 1)
    elif kind == "coding":
        problem = [a for a in says if a.get("target") == "problem"]
        if problem:
            picks += _sentences(problem[0]["text"], 1)
        for a in actions:
            if a["action"] == "type_code" and a.get("say"):
                picks += _sentences(a["say"], 1)
        output = [a for a in says if a.get("target") == "output"]
        if output:
            picks += _sentences(output[-1]["text"], 1)
    elif kind == "quiz":
        questions = activity["questions"]
        picks.append(f"단원 점검 {len(questions)}문항이에요.")
        # The first answers that read as a statement on their own ("0이에요." does not).
        for question in questions:
            main = WRONG_HEADING.split(question["explanation"], maxsplit=1)[0]
            picks += [line for line in _sentences(main, 1) if len(line) >= 12]
            if len(picks) >= 3:
                break
    else:
        if says:
            picks += _sentences(says[0]["text"], 1)
            if len(says) > 1:
                picks += _sentences(says[-1]["text"], 2)
    lines = []
    for line in picks:
        if line and line not in lines:
            lines.append(line)
    lines = lines[:3]
    if not lines:
        # Every line was a lead-in: keep the first sentences as they are rather than say nothing.
        source = says[0]["text"] if says else activity.get("title", "")
        lines = _sentences(source, 2, substantive=False)
    if not lines:
        raise SystemExit(f"{activity['id']}: 핵심 요약(tour)을 만들 문장이 없습니다.")
    return lines


def attach(chapters, solutions):
    """Give every activity its `narration`; refuse to build when a concept or coding problem
    has none, or when a hand-written one no longer matches its content."""
    table = load()
    used = set()
    missing = []
    stale_entries = []
    for chapter in chapters:
        for unit in chapter["units"]:
            for activity in unit["activities"]:
                where = f"{unit['id']}/{activity['id']}"
                kind = activity["kind"]
                if kind == "slides":
                    activity["narration"] = compile_slides(activity)
                elif kind == "quiz":
                    activity["narration"] = compile_quiz(activity)
                else:
                    solution = solutions[activity["problem"]["id"]] if kind == "coding" else None
                    entry, status = entry_for(activity, solution)
                    if status == "none":
                        if os.environ.get("KPC_LENIENT"):
                            missing.append(where)
                            activity["narration"] = []
                            continue
                        raise SystemExit(f"{where}: 해설이 없습니다. python tools/narrate.py 를 실행하세요.")
                    if status == "stale":
                        stale_entries.append(where)
                        if not os.environ.get("KPC_LENIENT"):
                            _, _, why = stale_report(activity, read_cache(activity["id"]), solution)
                            raise SystemExit(f"{where}: 원본이 바뀌어 해설이 낡았습니다. {why}\npython tools/narrate.py 를 실행하세요 (바뀐 줄만 다시 씁니다).")
                    used.add(activity["id"])
                    if kind == "concept":
                        activity["narration"] = compile_concept(activity, entry, where)
                    else:
                        activity["narration"] = compile_coding(activity, entry, solutions[activity["problem"]["id"]], where)
    for chapter in chapters:
        for unit in chapter["units"]:
            for activity in unit["activities"]:
                activity["tour"] = compile_tour(activity) if activity["narration"] else []
    orphan = sorted(set(table) - used)
    if orphan:
        raise SystemExit(f"narration: 미션에 없는 해설 항목 {orphan}")
    # A cache file whose mission is gone (renamed or removed) would silently rot: refuse it.
    if CACHE_DIR.exists():
        orphan_files = sorted(p.stem for p in CACHE_DIR.glob("*.json") if p.stem not in used)
        if orphan_files:
            raise SystemExit(f"narration: 미션에 없는 해설 캐시 파일 {orphan_files} (tools/kpc_course/narration_cache에서 지우세요)")
    if missing:
        print(f"narration: 해설 없는 미션 {len(missing)}개 (lenient): {', '.join(missing[:8])}{' …' if len(missing) > 8 else ''}")
    if stale_entries:
        print(f"narration: 낡은 해설 {len(stale_entries)}개 (lenient): {', '.join(stale_entries[:8])}{' …' if len(stale_entries) > 8 else ''}")
    return chapters
