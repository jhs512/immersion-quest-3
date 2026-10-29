"""Append each lesson's reviewed final challenge (a new step with a new stable code) to its sources.

Plan and approval record: docs/plans/2026-10-29-final-challenges-all-courses.md. A challenge is never an
existing step renamed or strengthened: an existing step code keeps its learners' passes, so reusing it would
grant the new challenge silently. Each spec lives in tools/final_challenges/<folder>.py and defines SPEC:

    key, revision (the new lesson version), course ('java'|'aice'|'engineer'), reason (why it is a final challenge)
    unit: {id, title, objectives, premise}        a new unit appended to the last chapter
    step: {id, title, objectives, core_flow[, complexity]}   PRD step
    task: the lesson task (same schema as content.json tasks, narration by hand)
    cases: optional {expected_outputs, reject, accept} for tests/lesson-cases/<key>.json (code lessons)
    review: {sentence: note} for every caution/concession sentence the reviewer kept

Idempotent: re-running replaces the same unit/step/task. Existing steps, ids and objectives are untouched.
    python tools/apply-final-challenges.py --lesson java-values [--lesson ...] | --all
"""
import argparse
import copy
import datetime
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'tools/final_challenges'))
from lesson_prd import approve, render, validate  # noqa: E402
import narration_review  # noqa: E402

SPECS = ROOT / 'tools/final_challenges'
PLAN = 'docs/plans/2026-10-29-final-challenges-all-courses.md'
BY = 'user · Codex 경유 MQ3 후속 지시 2026-10-29'
EVIDENCE = ('2026-10-29 사용자(Codex 경유): 「나머지 24개 수업도 제대로 된 도전과제 만들어서, 모든 수업에서 도전과제만 '
            '풀어도 클리어되게 해. 클로드가 계획 세우고 배포까지 마무리해.」 그리고 다른 두 과정에도 백엔드의 개선을 '
            f'적용하라고 했어요. 계획: {PLAN}. 이 수업에는 새 고유 코드의 마지막 도전 스텝 하나만 더했고 기존 스텝·목표는 '
            '그대로예요. 사용자가 이 PRD 파일 자체를 열람했다고 주장하지 않아요.')
CHALLENGES = {course: ROOT / f'tools/redesigned_courses/{course}/lesson-challenges.json' for course in ('java', 'aice', 'engineer')}
GRADING_PREFIX = '마지막 도전('


def dump(path, value):
    # Keep each file's existing indentation so a diff shows only the real change.
    indent = 2
    if path.exists():
        lines = path.read_text(encoding='utf-8').splitlines()
        if len(lines) > 1 and lines[1].startswith(' ') and not lines[1].startswith('  '):
            indent = 1
    path.write_text(json.dumps(value, ensure_ascii=False, indent=indent) + '\n', encoding='utf-8', newline='\n')


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def spec_for(key):
    path = SPECS / (key.replace('-', '_') + '.py')
    module_spec = importlib.util.spec_from_file_location('final_' + key.replace('-', '_'), path)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    spec = dict(module.SPEC)
    # Terminal challenges (Bash, Vim, Java launcher, Git) carry real-runtime cases for
    # examples/validate_final_terminal_challenges.rs instead of lesson-cases.
    if getattr(module, 'CASES', None) is not None:
        spec['terminal_cases'] = dict(step=spec['step']['id'], sources=getattr(module, 'SOURCES', {}),
                                      accept=[dict(steps=s, reason=r) for s, r in module.CASES['accept']],
                                      reject=[dict(steps=s, reason=r) for s, r in module.CASES['reject']])
    if spec['key'] != key:
        raise ValueError(f'{path}: key mismatch')
    return spec


def registration(key):
    catalog = load(ROOT / 'tools/redesigned_courses/catalog.json')
    for course in catalog['courses']:
        for item in course['lessons']:
            if item['key'] == key:
                return catalog, course, item
    raise ValueError(f'unregistered lesson {key}')


def apply(spec):
    key = spec['key']
    catalog, course, item = registration(key)
    if course['key'] != spec['course']:
        raise ValueError(f'{key}: course mismatch')
    folder = ROOT / item['authoring_prd'].rsplit('/', 1)[0]
    prd_path, content_path = folder / 'approved-prd.json', folder / 'content.json'
    prd, content = load(prd_path), load(content_path)
    step_id, unit_id = spec['step']['id'], spec['unit']['id']
    task = copy.deepcopy(spec['task'])
    if task['id'] != step_id:
        raise ValueError(f'{key}: task and PRD step ids differ')
    # PRD: one new unit in the last chapter holding only the challenge step.
    chapter = prd['chapters'][-1]
    for other in prd['chapters']:
        if other is not chapter and any(u['id'] == unit_id for u in other['units']):
            raise ValueError(f'{key}: challenge unit is in an earlier chapter')
    chapter['units'] = [u for u in chapter['units'] if u['id'] != unit_id]
    step = {k: v for k, v in spec['step'].items()}
    ledger = any('complexity' in s for ch in prd['chapters'] for u in ch['units'] for s in u['steps'])
    if ledger and 'complexity' not in step:
        raise ValueError(f'{key}: this PRD records a complexity ledger for every step')
    if not ledger:
        step.pop('complexity', None)
    chapter['units'].append(dict(id=unit_id, title=spec['unit']['title'], objectives=spec['unit']['objectives'],
                                 premise=spec['unit']['premise'], steps=[step]))
    prd['grading'] = [line for line in prd['grading'] if not line.startswith(GRADING_PREFIX)]
    prd['grading'].append(f"{GRADING_PREFIX}{step_id}): {spec['grading']}")
    previous = prd.get('approval', {})
    prd['approval'] = dict(status='draft')
    evidence = previous.get('evidence', '')
    if EVIDENCE not in evidence:
        evidence = (evidence + ' ' + EVIDENCE).strip()
    by = previous.get('by', '')
    prd = approve(prd, by if BY in by else (f'{by} / {BY}' if by else BY), evidence)
    # Content: the task appended last; presentation for the new unit.
    content['tasks'] = [t for t in content['tasks'] if t['id'] != step_id] + [task]
    content['presentation']['units'][unit_id] = dict(objectives=spec['unit']['objectives'], premise=spec['unit']['premise'])
    order = [s['id'] for ch in prd['chapters'] for u in ch['units'] for s in u['steps']]
    if order != [t['id'] for t in content['tasks']]:
        raise ValueError(f'{key}: content order differs from the PRD after appending')
    dump(prd_path, prd)
    dump(content_path, content)
    if (folder / 'approved-prd.md').exists():
        (folder / 'approved-prd.md').write_text(render(prd) + '\n', encoding='utf-8', newline='\n')
    # Registration: the new immutable lesson version.
    item['revision'] = spec['revision']
    dump(ROOT / 'tools/redesigned_courses/catalog.json', catalog)
    # Designation source of the course.
    path = CHALLENGES[course['key']]
    source = load(path) if path.exists() else dict(schema_version=1, purpose='', decided_by='', decided_on='', rule='', lessons={}, not_designated={})
    source['lessons'][key] = dict(task_id=step_id, title=task['title'], reason=spec['reason'])
    source.get('not_designated', {}).pop(key, None)
    dump(path, source)
    # Real-execution cases for code lessons.
    if spec.get('cases'):
        cases_path = ROOT / 'tests/lesson-cases' / f'{key}.json'
        cases = load(cases_path)
        number = len(content['tasks'])
        outputs = cases['expected_outputs'][:number - 1]
        if len(outputs) != number - 1:
            raise ValueError(f'{key}: lesson cases do not cover the earlier steps')
        cases['expected_outputs'] = outputs + [spec['cases']['expected_outputs']]
        for field in ('reject', 'accept'):
            kept = [row for row in cases.get(field, []) if row['step'] != number]
            added = [dict(step=number, replacements=row[0], reason=row[1]) for row in spec['cases'].get(field, [])]
            if kept or added:
                cases[field] = kept + added
        dump(cases_path, cases)
    if spec.get('terminal_cases'):
        path = ROOT / 'tests/final-challenge-cases' / f'{key}.json'
        path.parent.mkdir(parents=True, exist_ok=True)
        dump(path, spec['terminal_cases'])
    return folder, prd, content


def record_review(spec, prd, content):
    """The reviewer's keep notes for this new step, tied to its exact context hash."""
    steps = {s['id']: s for ch in prd['chapters'] for u in ch['units'] for s in u['steps']}
    task = next(t for t in content['tasks'] if t['id'] == spec['step']['id'])
    prompts = {p['text'] for p in narration_review.prompts(task)}
    checked = spec.get('review', {})
    missing = prompts - set(checked)
    if missing:
        raise ValueError(f"{spec['key']}: 검토 메모가 없는 문장: " + ' | '.join(sorted(missing)))
    ledger = narration_review.load_ledger()
    ledger['steps'][task['id']] = dict(lesson=spec['key'], state='reviewed',
        context_sha256=narration_review.context_sha256(steps[task['id']], task),
        reviewed=datetime.date(2026, 10, 29).isoformat(), checked={k: v for k, v in checked.items() if k in prompts}, findings=[])
    narration_review.save_ledger(ledger)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--lesson', action='append', default=[])
    parser.add_argument('--all', action='store_true')
    args = parser.parse_args()
    keys = sorted(p.stem.replace('_', '-') for p in SPECS.glob('*.py') if not p.stem.startswith('_')) if args.all else args.lesson
    for key in keys:
        spec = spec_for(key)
        _, prd, content = apply(spec)
        record_review(spec, prd, content)
        print(f"{key}: {spec['revision']} + {spec['step']['id']} ({len(content['tasks'])} steps)")


if __name__ == '__main__':
    main()
