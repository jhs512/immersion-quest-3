"""Publish lessons fixed in the 2026-10-28 narration audit (all lessons except java-values).

Every changed lesson is compared with its currently published pin, path by path. Allowed:
  - revision
  - narration[*].text / narration[*].say (spoken copy)
  - goal and narration[*].target only for steps listed in docs/narration-audit-20261028/allowed-changes.json
    (each listed with the user request that allowed it).
  - code_constant (listed steps only): starter_code, solution and narration[*].before/after may differ only by
    the listed exact replacement (e.g. 「int coupon = 1;」 → 「int coupon = 1000;」); tests and variations stay.
Anything else (code, solution, tests, variations, actions, ids, number of actions) refuses publishing.
Current Java/Python/... execution evidence (target/narration-audit/<key>-validation.json from
validate_redesigned_lesson) must match the lesson hash. The course manifest keeps fresh remote metadata.

  python tools/publish-narration-audit.py --lessons java-conditions            # verify only
  python tools/publish-narration-audit.py --lessons java-conditions --publish
"""
import argparse
import base64
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('publisher', ROOT / 'tools/publish-coding-conversions.py')
publisher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)
gh = publisher.gh
ALLOWED = ROOT / 'docs/narration-audit-20261028/allowed-changes.json'
EXCLUDED = {'java-values'}
SLUG = {'java': 'java-backend', 'aice': 'aice-associate', 'engineer': 'engineer-practical'}


def spoken_of(action):
    return (action.get('text') or action.get('say') or '').strip()


def changed_paths(a, b, path=()):
    if type(a) is not type(b):
        return [path]
    if isinstance(a, dict):
        return [p for k in sorted(set(a) | set(b)) for p in changed_paths(a.get(k), b.get(k), path + (k,))]
    if isinstance(a, list):
        found = [path + ('len',)] if len(a) != len(b) else []
        return found + [p for i, (x, y) in enumerate(zip(a, b)) for p in changed_paths(x, y, path + (i,))]
    return [] if a == b else [path]


def check_allowed(key, before, after, allowed):
    steps = allowed.get(key, {})
    if [t['id'] for t in before['tasks']] != [t['id'] for t in after['tasks']]:
        raise ValueError(f'{key}: step ids or order changed')
    report = []
    before = copy.deepcopy(before)
    for index, (old_task, new_task) in enumerate(zip(before['tasks'], after['tasks'])):
        if 'remove_say' not in steps.get(new_task['id'], {}).get('fields', []):
            continue
        # A removed sentence must be a plain say. Every executable action stays, in order, unchanged
        # apart from its spoken text; the remaining says are then compared path by path below.
        actions = lambda task: [{k: v for k, v in a.items() if k not in ('say', 'text', 'target')}
                                for a in task['narration'] if a['action'] != 'say']
        if actions(old_task) != actions(new_task):
            raise ValueError(f"{key}: executable narration changed in {new_task['id']}")
        # Align old to new: an old say with no counterpart at this position is a removed sentence.
        # A counterpart keeps its action and every non-spoken field (target is checked below).
        shape = lambda a: {k: v for k, v in a.items() if k not in ('say', 'text', 'target')}
        old_list, new_list, i, j, removed = old_task['narration'], new_task['narration'], 0, 0, []
        surplus = len(old_list) - len(new_list)
        while i < len(old_list):
            same = j < len(new_list) and shape(old_list[i]) == shape(new_list[j])
            if same and (len(removed) == surplus or spoken_of(old_list[i]) == spoken_of(new_list[j])
                         or old_list[i]['action'] != 'say'):
                i, j = i + 1, j + 1
            elif old_list[i]['action'] == 'say' and len(removed) < surplus:
                removed.append(old_list[i]); i += 1
            else:
                raise ValueError(f"{key}: only whole say actions may be removed in {new_task['id']}")
        if j != len(new_list) or len(removed) != surplus:
            raise ValueError(f"{key}: only whole say actions may be removed in {new_task['id']}")
        for action in removed:
            old_list.remove(action)
            report.append((new_task['id'], 'narration.removed_say: ' + spoken_of(action)[:40]))
    for path in changed_paths(before, after):
        if path == ('revision',):
            continue
        ok = False
        if len(path) >= 3 and path[0] == 'tasks':
            step = after['tasks'][path[1]]['id']
            extra = set(steps.get(step, {}).get('fields', []))
            if path[2:3] == ('goal',) and len(path) == 3 and 'goal' in extra:
                ok = True
            elif len(path) == 5 and path[2] == 'narration' and path[4] in ('text', 'say'):
                ok = True
            elif len(path) == 5 and path[2] == 'narration' and path[4] == 'target' and 'target' in extra:
                ok = True
            elif 'code_constant' in extra and (path[2:] in (('starter_code',), ('solution',)) or (
                    len(path) == 5 and path[2] == 'narration' and path[4] in ('before', 'after'))):
                constant = steps[step]['constant']
                old_value, new_value = before, after
                for part in path:
                    old_value, new_value = old_value[part], new_value[part]
                ok = (isinstance(old_value, str) and constant['from'] in old_value
                      and old_value.replace(constant['from'], constant['to']) == new_value)
            report.append((step, '.'.join(map(str, path[2:]))))
        if not ok:
            raise ValueError(f'{key}: change outside the allowed fields: {path}')
    return report


def course_of(key):
    catalog = json.loads((ROOT / 'tools/redesigned_courses/catalog.json').read_text(encoding='utf-8'))
    for course in catalog['courses']:
        if any(lesson['key'] == key for lesson in course['lessons']):
            return SLUG[course['key']]
    raise ValueError(f'{key}: not in the catalog')


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--lessons', nargs='+', required=True)
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    if EXCLUDED & set(args.lessons):
        raise ValueError('java-values is outside this audit')
    allowed = json.loads(ALLOWED.read_text(encoding='utf-8'))
    groups = {}
    for key in args.lessons:
        slug = course_of(key)
        repo = 'jhs512/mq3-lesson-redesigned-' + key
        endpoint = f'repos/jhs512/mq3-course-redesigned-{slug}/contents/course.json'
        remote = json.loads(base64.b64decode(gh(endpoint)['content']))
        old = next(row for row in remote['lessons'] if row['repository'] == repo)
        prepared = json.loads((ROOT / f'courses/redesigned-courses/{slug}.json').read_text(encoding='utf-8'))
        new = next(row for row in prepared['lessons'] if row['repository'] == repo)
        raw = (ROOT / f'courses/redesigned/{key}.json').read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if digest != new['sha256'] or old['id'] != new['id']:
            raise ValueError(f'{key}: unexpected lesson identity or hash')
        publisher.check_transition(key, old, new)
        before_raw = base64.b64decode(gh(f'repos/{repo}/contents/lesson.json?ref={old["revision"]}')['content'])
        if hashlib.sha256(before_raw).hexdigest() != old['sha256']:
            raise ValueError(f'{key}: the published lesson pin does not match')
        report = check_allowed(key, json.loads(before_raw), json.loads(raw), allowed)
        evidence = json.loads((ROOT / f'target/narration-audit/{key}-validation.json').read_text(encoding='utf-8'))
        if not evidence.get('passed') or evidence.get('lesson_sha256') != digest:
            raise ValueError(f'{key}: current execution evidence is required')
        goals = sorted({step for step, field in report if field == 'goal'})
        targets = sorted({(step, field) for step, field in report if field.endswith('.target')})
        constants = sorted({(step, field) for step, field in report
                            if field in ('starter_code', 'solution') or field.endswith(('.before', '.after'))})
        print(f'VERIFIED {key} {old["revision"]} -> {new["revision"]}: {len(report)} changed fields; '
              f'goal {len(goals)} {goals}; targets {targets}; approved constant {constants}; '
              f'others are spoken text only; execution passed', flush=True)
        groups.setdefault(endpoint, []).append((key, old, new, raw))
    if not args.publish:
        return
    user = gh('user')
    if (user['login'], user['id']) != ('jhs512', 4741844):
        raise ValueError('Unexpected publishing account')
    for endpoint, rows in groups.items():
        for key, old, new, raw in rows:
            publisher.publish_lesson(old, new, raw, 'Clarify narration and step order found in the lesson narration audit')
        fresh = gh(endpoint)
        course = json.loads(base64.b64decode(fresh['content']))
        pin = lambda row: (row['id'], row['revision'], row['sha256'])
        for key, old, new, raw in rows:
            current = next(row for row in course['lessons'] if row['repository'] == new['repository'])
            if pin(current) not in (pin(old), pin(new)):
                raise ValueError(f'{key}: another lesson revision was published concurrently')
            current.update({field: new[field] for field in ('revision', 'sha256')})
        body = (json.dumps(course, ensure_ascii=False, indent=2) + '\n').encode()
        result = gh(endpoint, 'PUT', dict(message='Publish narration audit fixes: ' + ', '.join(r[0] for r in rows),
                                          branch='main', sha=fresh['sha'], content=base64.b64encode(body).decode()))
        readback = gh(endpoint + '?ref=' + result['commit']['sha'])
        if base64.b64decode(readback['content']) != body:
            raise ValueError('Published course readback differs')
        print('VERIFIED public course ' + endpoint.split('/')[2] + ': ' + ', '.join(f'{r[0]}@{r[2]["revision"]}' for r in rows)
              + '; other course metadata preserved', flush=True)


if __name__ == '__main__':
    main()
