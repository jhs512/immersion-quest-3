"""Editorial checks that run at build time. A failing check stops the build."""
import collections
import re

NL = chr(10)

# Tooling and trivia that students never touch in this course (the tools the official outline
# names — Anaconda, Jupyter, Selenium, yfinance, FinanceDataReader — are explained in concepts).
FORBIDDEN = ["uv", "폰트", "891행", "번째 보기", "교시", "일차"]
FENCED = re.compile(r"```.*?```", re.S)
INLINE_CODE = re.compile(r"`[^`\n]+`")


def broken_backtick(value):
    """Code split across backticks, e.g. `groupby`('`gender`') or `index`=`False` or ['`price`']."""
    prose = FENCED.sub("", value)
    for match in INLINE_CODE.finditer(prose):
        before = prose[match.start() - 1] if match.start() > 0 else ""
        after = prose[match.end()] if match.end() < len(prose) else ""
        # `name`(그리고 …) is a Korean parenthetical; `name`() or `name`('x') is split code.
        parenthetical = prose[match.end() + 1 : prose.find(")", match.end()) if prose.find(")", match.end()) != -1 else len(prose)]
        split_call = after == "(" and not re.search(r"[가-힣]", parenthetical) and not parenthetical.startswith("`")
        quoted = bool(before) and before in "'\"" and bool(after) and after in "'\""
        if split_call or (after and after in "[=") or quoted:
            return match.group(0) + after
    return None


def _texts(activity):
    if activity["kind"] == "concept":
        yield "body", activity["body"]
        yield "check", activity["check"]["prompt"] + "\n" + activity["check"]["explanation"]
    elif activity["kind"] == "coding":
        yield "content", activity["problem"]["content"]
    elif activity["kind"] == "slides":
        yield "markdown", activity["markdown"]
    else:
        for q in activity["questions"]:
            yield q["id"], q["prompt"] + "\n" + q["explanation"] + "\n" + "\n".join(q.get("options", []))


def run(chapters):
    problems = []
    positions = collections.Counter()
    choices = 0
    for chapter in chapters:
        for unit in chapter["units"]:
            for activity in unit["activities"]:
                where = f"{unit['id']}/{activity['id']}"
                for label, value in _texts(activity):
                    broken = broken_backtick(value)
                    if broken:
                        problems.append(f"{where} {label}: 코드가 백틱으로 쪼개져 있습니다 → {broken!r}")
                    for word in FORBIDDEN:
                        if re.search(rf"(?<![A-Za-z]){re.escape(word)}(?![A-Za-z])", value):
                            problems.append(f"{where} {label}: 수업 밖 용어 {word!r}")
                    # A fence that still carries the source file's indentation means dedent failed
                    # (a literal newline inside the Python string, for one): the whole text would
                    # render as one code block.
                    if re.search(r"^[ 	]+```", value, re.M):
                        problems.append(f"{where} {label}: 코드 펜스 앞에 들여쓰기가 남아 있습니다 (본문이 통째로 코드 블록으로 보입니다)")
                    if value.count("```") % 2:
                        problems.append(f"{where} {label}: 코드 펜스가 닫히지 않았습니다")
                if activity["kind"] == "slides" and activity["markdown"].count(NL + "---" + NL) < 2:
                    problems.append(f"{where}: 슬라이드는 3장 이상이어야 합니다")
                if activity["kind"] == "concept":
                    # Prose paragraphs only: a blank line inside a code fence is not a paragraph.
                    paragraphs = [p for p in FENCED.sub("", activity["body"]).split("\n\n") if p.strip()]
                    if not 2 <= len(paragraphs) <= 10:
                        problems.append(f"{where}: 개념 본문은 2~10문단이어야 합니다 (현재 {len(paragraphs)})")
                    if "```" not in activity["body"]:
                        problems.append(f"{where}: 개념에 코드 예시 블록이 없습니다")
                if activity["kind"] == "coding":
                    from kpc_course import dsl as _dsl
                    dead = _dsl.unused_imports(_dsl.SOLUTIONS[activity["problem"]["id"]])
                    if dead:
                        problems.append(f"{where}: 정답이 쓰지 않는 import가 있습니다 → {dead}")
                if activity["kind"] == "quiz":
                    for q in activity["questions"]:
                        if q["type"] == "choice":
                            positions[q["correct"]] += 1
                            choices += 1
    if choices >= 10 and max(positions.values()) / choices > 0.6:
        problems.append(f"객관식 정답 위치가 한쪽에 쏠려 있습니다: {dict(positions)}")
    return problems
