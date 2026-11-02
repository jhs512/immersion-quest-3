"""Run the real lesson builder for one Rust lesson against its own review decisions.

tools/build-redesigned-git.py reads the shared review ledger. While several authors work at once,
each lesson keeps its decisions in review-decisions.json; this applies them to a copy of the ledger
(nothing shared is written) and then builds. The coordinator records the decisions for real with
`python tools/narration_review.py record <file>` before the final build.

    python docs/curriculum/rust-foundations/check_lesson.py rust-values
"""
import copy
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
import narration_review  # noqa: E402

spec = importlib.util.spec_from_file_location('build_redesigned_git', ROOT / 'tools/build-redesigned-git.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


def main(key):
    folder = builder.LESSONS[key][0]
    decisions = json.loads((ROOT / 'tools/redesigned_lessons' / folder / 'review-decisions.json').read_text(encoding='utf-8'))
    ledger = copy.deepcopy(narration_review.load_ledger())
    narration_review.record(decisions, ledger, dry_run=True)
    builder.check_narration_review = lambda lesson, steps, tasks: narration_review.check_lesson(lesson, steps, tasks, ledger=ledger)
    builder.build(key)


if __name__ == '__main__':
    main(sys.argv[1])
