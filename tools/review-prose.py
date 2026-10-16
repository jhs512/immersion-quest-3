"""문구 검토: read every student-facing text of the course with the Claude CLI and list what is
clearly wrong or awkward, as exact before → after replacements.

    python tools/review-prose.py                 # review all missions → .scratch/prose-review/findings.json
    python tools/review-prose.py --ids live-web  # some missions
    python tools/review-prose.py --apply         # apply the findings whose `before` occurs exactly once in a unit file

Only findings a reader would call a mistake are wanted (typos, broken words, grammar that does not
parse, a claim the code next to it contradicts, a sentence that cannot be understood). Taste is
not a finding. Each finding carries the exact text to replace, so `--apply` is a plain string
replacement in tools/kpc_course/*.py; the build's provenance then points at the changed blocks
and `python tools/narrate.py` refreshes only the narration lines written for them.
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

from kpc_course import chapters as outline  # noqa: E402

OUT = ROOT / ".scratch" / "prose-review" / "findings.json"
VOICE = (ROOT / "docs" / "voice.md").read_text(encoding="utf-8")


def texts(activity):
    kind = activity["kind"]
    if kind == "concept":
        yield "body", activity["body"]
        check = activity["check"]
        yield "check", check["prompt"] + "\n\n" + check["explanation"]
    elif kind == "coding":
        yield "problem", activity["problem"]["content"]
    elif kind == "slides":
        yield "markdown", activity["markdown"]
    else:
        for n, q in enumerate(activity["questions"], start=1):
            yield f"q{n}", q["prompt"] + "\n" + "\n".join(f"- {o}" for o in q.get("options", [])) + "\n\n" + q["explanation"]


def prompt_for(activity, label, text):
    return f"""{VOICE}

아래는 수업 미션 「{activity['title']}」의 {label} 글입니다. 수강생이 읽다가 "이상하다"고 할 곳만 찾으세요:
오타, 깨진 단어, 문법이 안 맞아 읽히지 않는 문장, 옆의 코드와 모순되는 설명, 뜻을 알 수 없는 문장, 잘못 끊긴 마크다운.
취향이나 더 나은 표현은 고치지 않습니다. 말투(해요체)는 이미 맞으면 그대로 둡니다. 코드·백틱 안·만화 YAML·표는 건드리지 않습니다.

JSON 배열로만 답하세요. 없으면 []. 각 항목: {{"before": "글자 그대로 있는 짧은 구절(한 문장 이내, 고유하게)", "after": "고친 구절", "why": "한 줄 이유"}}

### 글
{text}
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


def parse(text):
    match = re.search(r"\[.*\]", text, re.S)
    if not match:
        return []
    try:
        items = json.loads(match.group(0))
    except json.JSONDecodeError:
        return []
    return [i for i in items if isinstance(i, dict) and i.get("before") and i.get("after") and i["before"] != i["after"]]


def review(unit, activity):
    findings = []
    for label, text in texts(activity):
        try:
            items = parse(ask_claude(prompt_for(activity, label, text)))
        except RuntimeError as error:
            findings.append({"mission": activity["id"], "label": label, "error": str(error)})
            continue
        for item in items:
            if item["before"] in text:
                findings.append({"mission": activity["id"], "unit": unit["id"], "label": label, **item})
    return findings


def unit_file(unit_id):
    for path in sorted((ROOT / "tools" / "kpc_course").glob("*.py")):
        source = path.read_text(encoding="utf-8")
        if re.search(rf"UNIT\s*=\s*unit\(\s*['\"]{re.escape(unit_id)}['\"]", source) or f'"{unit_id}"' in source[:400] or f"'{unit_id}'" in source[:400]:
            return path
    return None


def apply(findings):
    applied, skipped = [], []
    sources = {}
    for f in findings:
        if "error" in f:
            continue
        hits = [p for p in sorted((ROOT / "tools" / "kpc_course").glob("*.py")) if f["before"] in (sources.setdefault(p, p.read_text(encoding="utf-8")))]
        if len(hits) != 1 or sources[hits[0]].count(f["before"]) != 1:
            skipped.append(f)
            continue
        path = hits[0]
        sources[path] = sources[path].replace(f["before"], f["after"], 1)
        applied.append((path.name, f))
    for path, source in sources.items():
        if source != path.read_text(encoding="utf-8"):
            path.write_text(source, encoding="utf-8", newline="\n")
    return applied, skipped


def main():
    parser = argparse.ArgumentParser(description="문구 검토")
    parser.add_argument("--ids", nargs="*", default=[])
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--jobs", type=int, default=4)
    args = parser.parse_args()
    if args.apply:
        findings = json.loads(OUT.read_text(encoding="utf-8"))
        applied, skipped = apply(findings)
        for name, f in applied:
            print(f"  ✓ {name} {f['mission']}/{f['label']}: {f['before'][:40]!r} → {f['after'][:40]!r}")
        for f in skipped:
            print(f"  - 건너뜀 {f['mission']}/{f['label']}: {f.get('before', '')[:50]!r} (한 곳에 딱 한 번 있지 않음)")
        print(f"{len(applied)}개 적용, {len(skipped)}개 건너뜀. 빌드: python tools/build-kpc-course.py (낡은 해설은 python tools/narrate.py)")
        return
    missions = [(u, a) for c in outline.build() for u in c["units"] for a in u["activities"] if not args.ids or a["id"] in args.ids]
    print(f"{len(missions)}개 미션의 글을 검토합니다 (Claude CLI, 동시 {args.jobs})")
    findings = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        for items in pool.map(lambda m: review(*m), missions):
            findings.extend(items)
            for item in items:
                if "error" in item:
                    print(f"  ! {item['mission']}/{item['label']}: {item['error']}", flush=True)
                else:
                    print(f"  · {item['mission']}/{item['label']}: {item['before'][:40]!r} → {item['after'][:40]!r} ({item['why'][:40]})", flush=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(findings, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len([f for f in findings if 'error' not in f])}개 발견 → {OUT.relative_to(ROOT)}. 적용: python tools/review-prose.py --apply")


if __name__ == "__main__":
    main()
