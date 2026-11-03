"""Apply the reviewed topic/sequence plan to the live MQ practical course.

Read-only by default. Publication changes course metadata, never lesson pins.
"""
import argparse
import base64
import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = 'jhs512/mq3-course-redesigned-engineer-practical'
PREFIX = 'jhs512/mq3-lesson-redesigned-'


def lesson_key(reference):
    repository = reference['repository']
    if not repository.startswith(PREFIX):
        raise ValueError(f'Unexpected lesson repository: {repository}')
    return repository[len(PREFIX):]


def organize(course, plan):
    if course.get('repository') != REPOSITORY:
        raise ValueError('Unexpected course repository')
    order = plan['order']
    if not order or len(order) != len(set(order)):
        raise ValueError('Order must contain every lesson exactly once')
    current = {lesson_key(reference): reference for reference in course['lessons']}
    if len(current) != len(course['lessons']) or set(order) != set(current):
        raise ValueError('Public lesson set changed; review the plan before publishing')
    ids = [reference['id'] for reference in current.values()]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate lesson identity')
    categories = []
    assignments = {}
    category_ids = set()
    for category in plan['categories']:
        identifier, title = category['id'], category['title']
        if not re.fullmatch(r'[a-z][a-z0-9-]{0,63}', identifier) or identifier in category_ids or not title.strip():
            raise ValueError('Invalid or duplicate category')
        category_ids.add(identifier)
        categories.append({'id': identifier, 'title': title})
        if not category['keys']:
            raise ValueError(f'Empty category: {identifier}')
        for key in category['keys']:
            if key not in current or key in assignments:
                raise ValueError(f'Unknown or multiply classified lesson: {key}')
            assignments[key] = identifier
    if set(assignments) != set(current):
        raise ValueError('Every lesson needs a topic category')
    prerequisites = plan['prerequisites']
    if set(prerequisites) != set(current):
        raise ValueError('Prerequisites must explicitly cover every lesson')
    rank = {key: index for index, key in enumerate(order)}
    result = copy.deepcopy(course)
    result['categories'] = categories
    result['lessons'] = []
    for key in order:
        before = prerequisites[key]
        if len(before) != len(set(before)) or any(item not in rank or rank[item] >= rank[key] for item in before):
            raise ValueError(f'Prerequisites must be unique and precede their lesson: {key}')
        reference = copy.deepcopy(current[key])
        reference['category'] = assignments[key]
        reference['prerequisites'] = [current[item]['id'] for item in before]
        result['lessons'].append(reference)
    return result


def publication(course, plan, at):
    result = organize(course, plan)
    if result == course:
        return result
    entry = {
        'at': at,
        'summary': '출제범위와 선수 개념에 맞춰 분류와 추천 순서를 정리했어요.',
        'reason': '찾아볼 주제와 처음부터 배울 순서를 구분해요.',
        'details': [
            f"수업 {len(result['lessons'])}개를 빠짐없이 주제별로 나눠요.",
            '선수 수업은 추천 안내예요. 다른 수업을 먼저 골라도 돼요.',
            '수업과 문제의 고유 코드·버전·정답·학습 기록은 유지해요.',
        ],
    }
    result['change_history'] = [entry, *copy.deepcopy(course.get('change_history', []))]
    return result


def gh(*args, body=None):
    command = ['gh', 'api', '--hostname', 'github.com', *args]
    if body is not None:
        command += ['--input', '-']
    completed = subprocess.run(command, input=json.dumps(body) if body is not None else None,
                               capture_output=True, text=True, encoding='utf-8', timeout=60, check=True)
    return json.loads(completed.stdout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, default=ROOT / 'tools/redesigned_courses/engineer-organization.json')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--publish', action='store_true')
    mode.add_argument('--proposal-patch', action='store_true', help='Print a patch for the reviewable candidate JSON')
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text(encoding='utf-8'))
    endpoint = f'repos/{REPOSITORY}/contents/course.json'
    current = gh(endpoint)
    course = json.loads(base64.b64decode(current['content']))
    result = publication(course, plan, datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'))
    changed = result != course
    if changed and current['sha'] != plan['baseline_blob_sha']:
        raise ValueError('Course metadata changed since review; inspect the new blob before publishing')
    if args.proposal_patch:
        path = ROOT / '.scratch/engineer-course-organization/proposal.json'
        raw = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
        print(f'*** Begin Patch\n*** Add File: {path.as_posix()}')
        print(''.join('+' + line + '\n' for line in raw.splitlines()), end='')
        print('*** End Patch')
        return
    print(json.dumps({'repository': REPOSITORY, 'blob': current['sha'],
                      'lessons': len(result['lessons']), 'categories': len(result['categories']),
                      'changed': changed, 'publish': args.publish}, ensure_ascii=False))
    if not changed or not args.publish:
        return
    raw = (json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    gh(endpoint, '--method', 'PUT', body={
        'message': 'Organize practical course by reviewed topics and learning prerequisites',
        'branch': 'main', 'sha': current['sha'], 'content': base64.b64encode(raw).decode('ascii')})
    actual = json.loads(base64.b64decode(gh(endpoint)['content']))
    if actual != result:
        raise RuntimeError('Published course changed or readback differs; inspect before any retry')
    print('VERIFIED: course organization readback matches; immutable lesson references preserved')


if __name__ == '__main__':
    main()
