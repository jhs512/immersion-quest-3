"""Publish task wording only, proving the executable lesson is unchanged."""
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
KEY = 'sql-first'
REPO = 'jhs512/mq3-lesson-redesigned-' + KEY


def without_goals(value):
    result = copy.deepcopy(value)
    result.pop('revision', None)
    for task in result['tasks']:
        del task['goal']
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    endpoint = f'repos/{publisher.COURSE}/contents/course.json'
    file = gh(endpoint)
    remote = json.loads(base64.b64decode(file['content']))
    old = next(row for row in remote['lessons'] if row['repository'] == REPO)
    prepared = json.loads((ROOT / 'courses/redesigned-courses/java-backend.json').read_text(encoding='utf8'))
    new = next(row for row in prepared['lessons'] if row['repository'] == REPO)
    raw = (ROOT / f'courses/redesigned/{KEY}.json').read_bytes()
    if hashlib.sha256(raw).hexdigest() != new['sha256'] or old['id'] != new['id']:
        raise ValueError('Unexpected lesson identity or hash')
    before_raw = base64.b64decode(gh(f'repos/{REPO}/contents/lesson.json?ref={old["revision"]}')['content'])
    if hashlib.sha256(before_raw).hexdigest() != old['sha256']:
        raise ValueError('The published lesson pin does not match')
    before, after = json.loads(before_raw), json.loads(raw)
    if without_goals(before) != without_goals(after):
        raise ValueError('This publisher only permits task goal wording changes')
    if len(after['tasks']) != 18:
        raise ValueError('Expected the same 18 SQL exercises')
    for task in after['tasks']:
        goal = task['goal']
        if goal.index('**할 일**') > goal.index('**알아두세요**'):
            raise ValueError('The task must precede the explanation')
        if '오류가 난 문장과 그 뒤 조회 결과' in goal:
            raise ValueError('An unconditional SQL error instruction remains')
    print('Verified 18 task descriptions; all executable fields and IDs are unchanged', flush=True)
    if not args.publish:
        return
    user = gh('user')
    if (user['login'], user['id']) != ('jhs512', 4741844):
        raise ValueError('Unexpected publishing account')
    if old['revision'] != new['revision']:
        publisher.check_transition(KEY, old, new)
    publisher.publish_lesson(old, new, raw, 'Put each SQL task and its result criteria first')
    fresh = gh(endpoint)
    course = json.loads(base64.b64decode(fresh['content']))
    pin = lambda row: (row['id'], row['revision'], row['sha256'])
    current = next(row for row in course['lessons'] if row['repository'] == REPO)
    if pin(current) not in (pin(old), pin(new)):
        raise ValueError('Another lesson revision was published concurrently')
    current.update({key: new[key] for key in ('title', 'revision', 'sha256')})
    body = (json.dumps(course, ensure_ascii=False, indent=2) + '\n').encode()
    result = gh(endpoint, 'PUT', dict(message='Clarify the task in all 18 SQL foundation exercises',
        branch='main', sha=fresh['sha'], content=base64.b64encode(body).decode()))
    readback = gh(endpoint + '?ref=' + result['commit']['sha'])
    if base64.b64decode(readback['content']) != body:
        raise ValueError('Published course readback differs')
    print('VERIFIED public ' + new['revision'] + '; unrelated metadata preserved', flush=True)


if __name__ == '__main__':
    main()
