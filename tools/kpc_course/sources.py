"""Source identity for derived text.

Every piece of student-facing text is a *block* with a stable key and a content hash:

    1-4-1/p3      third block of concept 1-4-1 (a paragraph, a fence or a figure, in order)
    1-4-1/check   its check question (prompt, accepted answers, explanation)
    1-4-2/solution  the reference solution of coding mission 1-4-2
    1-4-5/s7      the seventh slide of deck 1-4-5 (its text and instructor script)
    1-4-9/q3      the third question of quiz 1-4-9

Derived text (a mission's AI-written 해설 in tools/kpc_course/narration_cache, and through it
the /tour-all gist) records the key and hash of the block each line was written for. The build
compares those with the blocks as they are now, so "this paragraph changed → these lines must
be rewritten" is known exactly, and nothing is rewritten for a block that did not change.
courses/kpc-finance.sources.json lists every block's key, hash and opening words; its git
diff shows which blocks a commit touched.

Decks, quizzes and the tour are compiled from their sources on every build, so they can never
be stale; only the AI-written 해설 is cached and needs this bookkeeping.
"""
import hashlib
import json
import re

from kpc_course.dsl import split_slides

FENCE = re.compile(r"```.*?```", re.S)
FIGURE = re.compile(r"<!--.*?-->", re.S)


def mission_number(activity):
    """The 1-4-1 style number a mission's title starts with."""
    return activity["title"].split()[0]


def content_hash(text):
    """A short hash of the text with whitespace runs collapsed, so reflowing a paragraph does
    not count as changing it."""
    normalized = re.sub(r"\s+", " ", str(text)).strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:12]


def body_blocks(markdown):
    """The blocks of a concept body in document order: each paragraph (text between blank lines)
    and each code fence is one block."""
    blocks = []
    position = 0
    for match in FENCE.finditer(markdown):
        blocks += _paragraphs(markdown[position:match.start()])
        blocks.append(match.group(0).strip())
        position = match.end()
    blocks += _paragraphs(markdown[position:])
    return blocks


def _paragraphs(text):
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def blocks(activity, solution=None):
    """[(key, text)] for a mission: what a derived line can be written for."""
    items = [("title", activity["title"])]
    kind = activity["kind"]
    if kind == "concept":
        items += [(f"p{n}", block) for n, block in enumerate(body_blocks(activity["body"]), start=1)]
        check = activity["check"]
        items.append(("check", "\n".join([check["prompt"], " / ".join(check.get("accepted", [])), check["explanation"]])))
    elif kind == "coding":
        problem = activity["problem"]
        items.append(("problem", problem["content"]))
        items.append(("starter", problem.get("starter_code", "")))
        tests = problem.get("tests") or []
        # Always present: an "examples" or "input" line may describe a problem without tests.
        items.append(("example", json.dumps(tests[0], ensure_ascii=False, sort_keys=True) if tests else ""))
        items.append(("solution", solution or ""))
    elif kind == "slides":
        _, parts = split_slides(activity["markdown"])
        items += [(f"s{n}", part) for n, part in enumerate(parts, start=1)]
    else:
        items += [(f"q{n}", json.dumps(q, ensure_ascii=False, sort_keys=True)) for n, q in enumerate(activity["questions"], start=1)]
    return items


def index(activity, solution=None):
    """{key: hash} for a mission."""
    return {key: content_hash(text) for key, text in blocks(activity, solution)}


def find_block(activity, anchor, normalize):
    """The key of the first body block whose normalized text contains the anchor phrase; a
    figure's title or a code line counts through the fence it sits in."""
    for key, text in blocks(activity):
        if key in ("title", "check"):
            continue
        shown = normalize(text.strip("`").strip()) if text.startswith("```") else normalize(text)
        if anchor in shown:
            return key
    return None


def excerpt(text, width=40):
    """The opening words of a block, one line, for messages and the index."""
    flat = re.sub(r"\s+", " ", FIGURE.sub("", str(text))).strip().strip("`").strip()
    return flat if len(flat) <= width else flat[: width - 1] + "…"


def course_index(chapters, solutions):
    """The sources index for courses/kpc-finance.sources.json, mission by mission."""
    out = {}
    for chapter in chapters:
        for unit in chapter["units"]:
            for activity in unit["activities"]:
                solution = solutions[activity["problem"]["id"]] if activity["kind"] == "coding" else None
                out[mission_number(activity)] = {
                    "id": activity["id"],
                    "kind": activity["kind"],
                    "blocks": [
                        {"key": key, "hash": content_hash(text), "text": excerpt(text)}
                        for key, text in blocks(activity, solution)
                    ],
                }
    return out
