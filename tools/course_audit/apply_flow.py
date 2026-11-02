"""Insert reviewed 코드 흐름 보기 moments into lesson narrations (course audit, 2026-11-02).

Spec: a JSON list of {lesson, step, after, action, note}. `after` is the spoken sentence (or patch `say`) the
code_flow action follows; `action` is the code_flow action itself; `note` is the reviewer's meaning check of
the new sentence (docs/agents/narration.md 「상세 해설의 의미 검토」). Re-running is a no-op once inserted.

For each changed lesson: the catalog revision moves to the next number once (only while it still equals the
revision the course bundle references), and the step's review entry is re-recorded on the new text. Earlier
checked notes and findings of sentences that are still spoken are carried; the new sentence gets `note`.

  python tools/course_audit/apply_flow.py <spec.json>
Then: build-redesigned-git.py --lesson <key>, build-redesigned-course-bundle.py, and the lesson validator.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import narration_review  # noqa: E402

CATALOG = ROOT / 'tools/redesigned_courses/catalog.json'
MANIFESTS = ROOT / 'courses/redesigned-courses'


def published_revisions(base=os.environ.get('MQ_AUDIT_BASE', '0090f482')):
    """Lesson revisions the course manifests reference at `base`, the commit this audit branch started from (its
    revisions may already be tagged). The working manifests are rebuilt after every lesson build, so comparing
    against them would bump an unpublished revision twice; `main` can be older than the branch start."""
    revisions = {}
    for path in MANIFESTS.glob('*.json'):
        raw = subprocess.check_output(['git', 'show', f'{base}:{path.relative_to(ROOT).as_posix()}'], cwd=ROOT)
        for ref in json.loads(raw)['lessons']:
            revisions[ref['id']] = ref['revision']
    return revisions


def write_json(path, value):
    newline = '\r\n' if b'\r\n' in path.read_bytes() else '\n'
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline=newline)


def insert(task, after, action):
    if action in task['narration']:
        return False
    anchors = [i for i, item in enumerate(task['narration']) if narration_review.spoken(item) == after]
    if len(anchors) != 1:
        raise ValueError(f"{task['id']}: 앞 문장을 정확히 하나 찾지 못했어요: {after[:40]}")
    task['narration'].insert(anchors[0] + 1, action)
    return True


def bump(key):
    catalog = json.loads(CATALOG.read_text(encoding='utf-8'))
    published = published_revisions()
    for course in catalog['courses']:
        for item in course.get('lessons', []):
            if item['key'] == key and item['revision'] == published.get(item['id']):
                prefix, number = item['revision'].rsplit('-', 1)
                item['revision'] = f'{prefix}-{int(number) + 1}'
    write_json(CATALOG, catalog)


def main():
    spec = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    ledger = narration_review.load_ledger()
    decisions = []
    for lesson in sorted({item['lesson'] for item in spec}):
        folder, _, authored, steps = narration_review.load(lesson)
        tasks = {task['id']: task for task in authored['tasks']}
        changed = False
        for item in (i for i in spec if i['lesson'] == lesson):
            changed |= insert(tasks[item['step']], item['after'], item['action'])
        if not changed:
            print(f'{lesson}: already applied')
            continue
        write_json(folder / 'content.json', authored)
        bump(lesson)
        for step in dict.fromkeys(i['step'] for i in spec if i['lesson'] == lesson):
            task = tasks[step]
            current = {narration_review.spoken(action) for action in task['narration']}
            earlier = ledger['steps'].get(step, {})
            checked = {text: note for text, note in earlier.get('checked', {}).items() if text in current}
            for item in (i for i in spec if i['step'] == step):
                checked[narration_review.spoken(item['action'])] = item['note']
            decisions.append({'lesson': lesson, 'step': step, 'checked': checked, 'findings': earlier.get('findings', [])})
        print(f'{lesson}: inserted, revision bumped')
    if decisions:
        narration_review.record(decisions, ledger)
        narration_review.save_ledger(ledger)


if __name__ == '__main__':
    main()
