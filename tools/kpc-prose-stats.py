"""Readability numbers for the student-facing prose in courses/kpc-finance.json.

Counts sentences, sentences over 45 characters, formal endings (~니다) and plain-form endings
(~다.) per chapter and per mission kind, so passes can be compared.
"""
import json
import re
import sys
from collections import Counter

FENCE = re.compile(r"```.*?```", re.S)
COMMENT = re.compile(r"<!--.*?-->", re.S)
TABLE_ROW = re.compile(r"^\s*\|.*$", re.M)


def prose(markdown):
    text = FENCE.sub("", markdown or "")
    text = COMMENT.sub("", text)
    text = TABLE_ROW.sub("", text)
    text = re.sub(r"`[^`\n]+`", "C", text)
    text = re.sub(r"\*\*", "", text)
    text = re.sub(r"^#+\s*", "", text, flags=re.M)
    return text


def sentences(text):
    out = []
    for line in text.splitlines():
        line = line.strip().lstrip("->* 0123456789.").strip()
        if not line:
            continue
        for s in re.split(r"(?<=[.!?。])\s+", line):
            s = s.strip()
            if len(s) >= 4:
                out.append(s)
    return out


def texts(activity):
    kind = activity["kind"]
    if kind == "concept":
        yield activity["body"]
        yield activity["check"]["prompt"] + "\n" + activity["check"]["explanation"]
    elif kind == "coding":
        yield activity["problem"]["content"]
    elif kind == "slides":
        yield activity["markdown"]
    else:
        for q in activity["questions"]:
            yield q["prompt"] + "\n" + q["explanation"] + "\n" + "\n".join(q.get("options", []))


def main(path):
    course = json.load(open(path, encoding="utf-8"))
    rows = []
    total = Counter()
    for chapter in course["chapters"]:
        per = Counter()
        for unit in chapter["units"]:
            for activity in unit["activities"]:
                for t in texts(activity):
                    for s in sentences(prose(t)):
                        per["sentences"] += 1
                        per[activity["kind"]] += 1
                        if len(s) > 45:
                            per["long"] += 1
                        if re.search(r"니다[.?!]?$", s):
                            per["formal"] += 1
                        elif re.search(r"(?<![요죠])다[.?!]?$", s) and not re.search(r"(겠|었|았|니)다[.?!]?$", s):
                            per["plain"] += 1
        rows.append((chapter["id"], per))
        total.update(per)
    print(f"{'chapter':14} {'sent':>6} {'>45자':>6} {'니다':>6} {'~다':>6}")
    for cid, per in rows + [("total", total)]:
        print(f"{cid:14} {per['sentences']:6} {per['long']:6} {per['formal']:6} {per['plain']:6}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "courses/kpc-finance.json")
