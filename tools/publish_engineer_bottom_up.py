"""Publish verified reinforcement lessons, then merge them into the live course.

Existing lesson references, metadata and progress remain untouched. New lesson
tags are immutable. A changed existing addition or an unrelated repository stops
publication. The default is a preflight; --publish performs the authorized update.
"""
import argparse
import base64
import copy
import hashlib
import importlib.util
import json

from verify_engineer_bottom_up import MAP, ROOT, read, verify

spec = importlib.util.spec_from_file_location('redesigned_publisher', ROOT / 'tools/publish-redesigned-courses.py')
publisher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)
gh = publisher.gh
COURSE = 'jhs512/mq3-course-redesigned-engineer-practical'


def merge(remote, prepared, additions):
    if remote.get('repository') != COURSE or remote['id'] != prepared['id']:
        raise ValueError('Unexpected course identity')
    result = copy.deepcopy(remote)
    by_repo = {row['repository']: row for row in prepared['lessons']}
    prefix = 'jhs512/mq3-lesson-redesigned-'
    original = {row['id']: row for row in remote['lessons']}
    if len(original) != len(remote['lessons']):
        raise ValueError('Duplicate remote lesson identity')
    added_ids = set()
    for item in additions:
        new = by_repo[prefix + item['key']]
        added_ids.add(new['id'])
        existing = [row for row in result['lessons'] if row['id'] == new['id'] or row['repository'] == new['repository']]
        if existing:
            if existing != [new]:
                raise ValueError('Conflicting reinforcement revision: ' + item['key'])
            continue
        position = next(i for i, row in enumerate(result['lessons']) if row['repository'] == prefix + item['after'])
        result['lessons'].insert(position + 1, copy.deepcopy(new))
    # Never replace another author's current old-lesson revision with a stale local one.
    assert all(next(row for row in result['lessons'] if row['id'] == identity) == before
               for identity, before in original.items() if identity not in added_ids)
    change = next(row for row in prepared['change_history'] if '보강 수업 32개' in row['summary'])
    if not any(row.get('summary') == change['summary'] for row in result.get('change_history', [])):
        result.setdefault('change_history', []).insert(0, change)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    verify()
    prepared = read(ROOT / 'courses/redesigned-courses/engineer-practical.json')
    additions = read(MAP)['lesson_order']
    user = gh('user')
    if (user['login'], user['id']) != ('jhs512', 4741844):
        raise ValueError('Unexpected GitHub account')
    endpoint = f'repos/{COURSE}/contents/course.json'
    initial = gh(endpoint + '?ref=main')
    remote = json.loads(base64.b64decode(initial['content']))
    merge(remote, prepared, additions)
    print('Preflight: all 32 current grader reports match; live old lessons are preserved.', flush=True)
    if not args.publish:
        return
    by_repo = {row['repository']: row for row in prepared['lessons']}
    for item in additions:
        reference = by_repo['jhs512/mq3-lesson-redesigned-' + item['key']]
        raw = (ROOT / 'courses/redesigned' / f"{item['key']}.json").read_bytes()
        publisher.publish_file(reference['repository'], 'lesson.json', raw, reference['revision'])
    # Refresh immediately before the SHA-guarded write; retain newer unrelated changes.
    current = gh(endpoint + '?ref=main')
    before = json.loads(base64.b64decode(current['content']))
    merged = merge(before, prepared, additions)
    if merged != before:
        raw = (json.dumps(merged, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
        gh(endpoint, 'PUT', dict(message='Integrate 32 verified bottom-up engineer lessons', branch='main',
                                sha=current['sha'], content=base64.b64encode(raw).decode('ascii')))
    actual = json.loads(base64.b64decode(gh(endpoint + '?ref=main')['content']))
    if actual != merged:
        raise ValueError('Published course readback differs')
    proof = dict(passed=True, course=COURSE, lessons=len(actual['lessons']),
                 additions=32, preserved_existing_lessons=len(before['lessons']),
                 course_sha256=hashlib.sha256(json.dumps(actual, sort_keys=True).encode()).hexdigest())
    destination = ROOT / 'target/ebu/publication.json'
    destination.write_text(json.dumps(proof, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(proof), flush=True)


if __name__ == '__main__':
    main()
