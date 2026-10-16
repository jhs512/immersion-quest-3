"""Build courses/kpc-finance.json and kpc-solutions.json from tools/kpc_course/*. No network."""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from kpc_course import chapters as outline, checks, comments, dsl, narration, sources  # noqa: E402

chapters = outline.build()  # fills dsl.SOLUTIONS as the unit modules load
# Solutions with their comments (tools/annotate.py): what 정답 보기 shows and the 해설 types.
SOLUTIONS = comments.apply(dsl.SOLUTIONS)
chapters = narration.attach(chapters, SOLUTIONS)

problems = checks.run(chapters)
if problems and not os.environ.get("KPC_LENIENT"):
    print("\n".join(problems))
    sys.exit(f"{len(problems)}개 편집 검사 실패. 고친 뒤 다시 빌드하세요.")

course = dict(
    id="kpc-finance-2026",
    title="KPC · 머신러닝을 활용한 금융데이터 분석",
    description="7챕터 · 20단원. 개념을 확인하고 독립된 main.py 미션과 퀴즈를 클리어하세요.",
    chapters=chapters,
)
(ROOT / "courses/kpc-finance.json").write_text(json.dumps(course, ensure_ascii=False, indent=2), encoding="utf-8")
(ROOT / "courses/kpc-solutions.json").write_text(json.dumps(SOLUTIONS, ensure_ascii=False, indent=2), encoding="utf-8")
# Every source block's key, hash and opening words: its diff shows what a commit changed.
(ROOT / "courses/kpc-finance.sources.json").write_text(
    json.dumps(sources.course_index(chapters, SOLUTIONS), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

units = [u for c in chapters for u in c["units"]]


# Keep the unit table in docs/kpc-course.md in step with the generated course.
def table_rows():
    for c in chapters:
        for u in c["units"]:
            kinds = [a["kind"] for a in u["activities"]]
            questions = sum(len(a["questions"]) for a in u["activities"] if a["kind"] == "quiz")
            yield f"| {c['title']} | {u['title']} | {kinds.count('concept')} | {kinds.count('coding')} | {questions} |"


doc = ROOT / "docs/kpc-course.md"
lines = doc.read_text(encoding="utf-8").splitlines()
start = next(i for i, l in enumerate(lines) if l.startswith("| 챕터 |"))
end = start
while end < len(lines) and lines[end].startswith("|"):
    end += 1
lines[start:end] = [lines[start], lines[start + 1], *table_rows()]
doc.write_text("\n".join(lines) + "\n", encoding="utf-8")

print(
    f"{len(chapters)} chapters, {len(units)} units, {sum(len(u['activities']) for u in units)} missions, "
    f"{len(dsl.SOLUTIONS)} coding problems, "
    f"{sum(len(a['questions']) for u in units for a in u['activities'] if a['kind'] == 'quiz')} quiz questions"
    + (f", {len(problems)} editorial warnings (lenient)" if problems else "")
)
