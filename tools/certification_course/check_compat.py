"""Run built AICE lessons under another Python environment (e.g. the exam-era versions).

MOLIP_PYTHON=target/aice-exam-env/Scripts/python.exe python tools/certification_course/check_compat.py [lesson ids]
COMPAT_DRAFTS=1 ... check_compat.py <lesson id> checks a draft from target/certification-drafts instead.
The exam-era environment follows KT notice 16322 (2026-08-18): uv venv target/aice-exam-env --python 3.10,
then pandas 1.5.3, numpy 1.23.5, matplotlib 3.7.0, seaborn 0.12.1, scikit-learn 1.3.2, tensorflow 2.13.1,
xgboost 0.90. See .scratch/certification-research/aice-libraries.md.

For every Python exercise: the solution must run there, pass its own checker there, and the starter must
still fail. Printed output that differs from the course's recorded output is listed separately: the
checker compares reference and learner in the same environment, so a different display is not a
failure, but lesson text that quotes such output may need care.
"""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from certification_course import kit
from principles_course.common import PYTHON, ROOT, execute


def lessons(ids):
    if os.environ.get('COMPAT_DRAFTS'):
        # Drafts written by check_lesson.py, named on the command line.
        for id in ids:
            yield json.loads((ROOT / 'target/certification-drafts' / id / 'lesson.json').read_text(encoding='utf8'))
        return
    course = json.loads((ROOT / 'target/certification-foundations/aice-associate/course.json').read_text(encoding='utf8'))
    for ref in course['lessons']:
        if ids and ref['id'] not in ids:
            continue
        own = ROOT / 'target/certification-foundations' / ref['id'] / 'lesson.json'
        path = own if own.exists() else ROOT / 'target/certification-pilots/aice-associate/lesson.json'
        yield json.loads(path.read_text(encoding='utf8'))


def probe(lesson, t):
    result = execute(t, t['solution'])
    row = dict(lesson=lesson['id'], task=t['id'], runs=result.returncode == 0, error=result.stderr[-600:] if result.returncode else '')
    row['same_output'] = result.stdout.replace('\r\n', '\n').rstrip('\n') == t['tests'][0]['expected'].rstrip('\n')
    row['output'] = '' if row['same_output'] else result.stdout[-400:]
    noise = [line for line in result.stderr.splitlines() if line.strip()]
    row['warnings'] = '' if result.returncode else '\n'.join(noise)[-400:]
    if t.get('checker'):
        row['passes'], detail = kit.grade(t, t['solution'])
        row['grade_detail'] = '' if row['passes'] else detail[-600:]
        row['starter_fails'] = not kit.grade(t, t['starter_code'])[0]
    return row


if __name__ == '__main__':
    print('python:', PYTHON, flush=True)
    jobs = [(lesson, t) for lesson in lessons(set(sys.argv[1:])) for t in lesson['tasks'] if t['language'] == 'python']
    with ThreadPoolExecutor(max_workers=int(os.environ.get('COMPAT_WORKERS', '8'))) as pool:
        rows = list(pool.map(lambda job: probe(*job), jobs))
    # One report per draft set, so several authors can check at the same time.
    suffix = '-' + '-'.join(sorted(sys.argv[1:])) if os.environ.get('COMPAT_DRAFTS') else ''
    out = ROOT / f'target/aice-compat-report{suffix}.json'
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    broken = [r for r in rows if not r['runs'] or not r.get('passes', True) or not r.get('starter_fails', True)]
    shown = [r for r in rows if r['runs'] and not r['same_output']]
    warned = [r for r in rows if r['warnings']]
    print(f'{len(rows)} exercises: {len(broken)} broken, {len(shown)} print differently, {len(warned)} print warnings')
    for r in broken:
        print('BROKEN', r['lesson'], r['task'], (r['error'] or r.get('grade_detail', '')).strip().splitlines()[-1:] or '')
    print('report:', out)
