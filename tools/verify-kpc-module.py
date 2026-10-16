"""Check a few kpc_course modules on their own, without building the whole course.

    python tools/verify-kpc-module.py d1_p1_environment decks_stock table_quizzes

For every mission the named modules define (a unit's UNIT, a deck module's slides, CHALLENGES,
table-quiz PLACEMENTS) this runs the same narration compile and editorial checks the full build
runs, but imports only those modules and the narration files that load. Use it while editing one
chapter so a half-edited file elsewhere does not get in the way; the full build is still the
final word.
"""
import importlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from kpc_course import checks, dsl, narration  # noqa: E402
from kpc_course import comments  # noqa: E402
import os
os.environ.setdefault("KPC_LENIENT", "1")
def solutions():
    """The commented solutions, once the unit modules have registered theirs."""
    return comments.apply(dsl.SOLUTIONS)




def activities_of(name):
    module = importlib.import_module(f"kpc_course.{name}")
    found = []
    if hasattr(module, "UNIT"):
        found += module.UNIT["activities"]
    if hasattr(module, "CHALLENGES"):
        found += list(module.CHALLENGES.values())
    if name == "table_quizzes":
        found += [placement[2] for placement in module.PLACEMENTS]
    for value in vars(module).values():
        if isinstance(value, dict) and value.get("kind") == "slides":
            found.append(value)
    unique, seen = [], set()
    for activity in found:
        if activity["id"] not in seen:
            seen.add(activity["id"])
            unique.append(activity)
    return unique


def narration_table():
    table = {}
    for path in sorted((ROOT / "tools/kpc_course").glob("narration_*.py")):
        try:
            module = importlib.import_module(f"kpc_course.{path.stem}")
        except Exception as error:  # another editor may be mid-change there
            print(f"(skip {path.name}: {error})")
            continue
        table.update(module.NARRATION)
    return table


def main(names):
    if not names:
        sys.exit(__doc__)
    activities = [a for name in names for a in activities_of(name)]
    table = narration_table()
    failures = []
    for activity in activities:
        where = activity["id"]
        try:
            kind = activity["kind"]
            if kind == "slides":
                narration.compile_slides(activity)
            elif kind == "quiz":
                narration.compile_quiz(activity)
            elif activity["id"] not in table:
                failures.append(f"{where}: 해설 스크립트가 없습니다 (narration_*.py)")
            elif kind == "concept":
                narration.compile_concept(activity, table[where], where)
            else:
                narration.compile_coding(activity, table[where], solutions()[activity["problem"]["id"]], where)
        except SystemExit as error:
            failures.append(str(error))
    failures += checks.run([dict(units=[dict(id="verify", activities=activities)])])
    for line in failures:
        print(line)
    print(f"{len(activities)} missions checked, {len(failures)} problems")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
