"""Repair mutable course metadata for existing MQ clients; never touch lesson pins.

Default is read-only. --publish uses each fresh GitHub blob SHA to reject races.
"""
import argparse
import base64
import copy
from datetime import datetime, timezone
import json
import re
import subprocess

REPOSITORIES = [f'jhs512/mq3-course-redesigned-{name}' for name in
                ('java-backend', 'aice-associate', 'engineer-practical')]
CANONICAL = re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z')


def repair(course):
    result = copy.deepcopy(course)
    changes = []
    for entry in result.get('change_history', []):
        before = entry['at']
        if CANONICAL.fullmatch(before):
            datetime.strptime(before, '%Y-%m-%dT%H:%M:%SZ')
            continue
        stamp = datetime.fromisoformat(before)
        if stamp.tzinfo is None or stamp.utcoffset() != timezone.utc.utcoffset(stamp):
            raise ValueError(f'Refusing ambiguous or non-UTC history time: {before}')
        entry['at'] = stamp.strftime('%Y-%m-%dT%H:%M:%SZ')
        changes.append({'before': before, 'after': entry['at']})
    restored = copy.deepcopy(result)
    for old, new in zip(course.get('change_history', []), restored.get('change_history', [])):
        new['at'] = old['at']
    if restored != course:
        raise AssertionError('Repair changed content beyond history timestamps')
    return result, changes


def gh(*args, body=None):
    command = ['gh', 'api', '--hostname', 'github.com', *args]
    if body is not None:
        command += ['--input', '-']
    output = subprocess.run(command, input=json.dumps(body) if body is not None else None,
                            text=True, encoding='utf-8', capture_output=True,
                            timeout=60, check=True)
    return json.loads(output.stdout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    for repository in REPOSITORIES:
        endpoint = f'repos/{repository}/contents/course.json'
        current = gh(endpoint)
        course = json.loads(base64.b64decode(current['content']))
        if course['repository'] != repository:
            raise ValueError('Unexpected repository identity')
        fixed, changes = repair(course)
        print(json.dumps({'repository': repository, 'sha': current['sha'],
                          'lessons': len(course['lessons']), 'changes': changes,
                          'mode': 'publish' if args.publish else 'read-only'}, ensure_ascii=False))
        if not changes or not args.publish:
            continue
        raw = (json.dumps(fixed, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
        gh(endpoint, '--method', 'PUT', body={
            'message': 'Normalize course history UTC timestamps for installed MQ clients',
            'branch': 'main', 'sha': current['sha'],
            'content': base64.b64encode(raw).decode('ascii')})
        verified = json.loads(base64.b64decode(gh(endpoint)['content']))
        if verified != fixed:
            raise RuntimeError(f'Concurrent change or readback mismatch: {repository}')
        print(f'VERIFIED {repository}: all lesson pins and non-time metadata preserved')


if __name__ == '__main__':
    main()
