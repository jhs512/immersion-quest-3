"""Publish reviewed orientation for all three public courses, independently of app builds.

Default is read-only preflight. --publish writes immutable lesson revisions and
then updates course pins. Concurrent course metadata is preserved. Re-runs resume.
"""
import argparse
import base64
import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time

from test_narration_openings import baseline, behavior

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('coding_publisher', ROOT / 'tools/publish-coding-conversions.py')
publisher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)
gh = publisher.gh
SUMMARY = '모든 수업의 첫 해설에 교육목표와 흐름을, 각 문제 해설 앞에 해결할 목표를 안내해요.'


def read_course(repository, ref='main'):
    file = gh(f'repos/{repository}/contents/course.json?ref={ref}')
    return file, json.loads(base64.b64decode(file['content']))


def pin(row):
    return tuple(row[k] for k in ('id', 'repository', 'revision', 'sha256'))


def prepare():
    courses = []
    for path in sorted((ROOT / 'courses/redesigned-courses').glob('*.json')):
        local = json.loads(path.read_text(encoding='utf-8'))
        original = baseline(path.relative_to(ROOT).as_posix())
        repository = local['repository']
        _, remote = read_course(repository)
        if remote['id'] != local['id'] or remote['repository'] != repository:
            raise ValueError('Course identity changed')
        if {r['id'] for r in remote['lessons']} != {r['id'] for r in local['lessons']}:
            raise ValueError('Course membership changed; inspect before publication')
        rows = []
        for new in local['lessons']:
            old = next(r for r in original['lessons'] if r['id'] == new['id'])
            live = next(r for r in remote['lessons'] if r['id'] == new['id'])
            key = new['repository'].removeprefix('jhs512/mq3-lesson-redesigned-')
            lesson_path = f'courses/redesigned/{key}.json'
            raw = (ROOT / lesson_path).read_bytes()
            lesson = json.loads(raw)
            if pin(live) not in (pin(old), pin(new)):
                raise ValueError('Concurrent lesson revision: ' + key)
            if behavior(lesson) != behavior(baseline(lesson_path)):
                raise ValueError('Unexpected executable/content change: ' + key)
            if hashlib.sha256(raw).hexdigest() != new['sha256'] or lesson['revision'] != new['revision']:
                raise ValueError('Stale lesson pin: ' + key)
            publisher.check_transition(key, old, new)
            rows.append((old, new, raw))
        courses.append((repository, rows))
        print(f'PREFLIGHT {repository}: {len(rows)} lessons, behavior unchanged', flush=True)
    if len(courses) != 3 or sum(len(rows) for _, rows in courses) != 94:
        raise ValueError('Expected all 94 lessons in three courses')
    return courses


def publish_course(repository, rows):
    file, current = read_course(repository)
    merged = copy.deepcopy(current)
    for old, new, _ in rows:
        row = next(r for r in merged['lessons'] if r['id'] == new['id'])
        if pin(row) not in (pin(old), pin(new)):
            raise ValueError('Concurrent course pin changed')
        row.update({key: new[key] for key in ('revision', 'sha256')})
    if not any(item.get('summary') == SUMMARY for item in merged.get('change_history', [])):
        merged.setdefault('change_history', []).insert(0, dict(
            at=datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z'),
            summary=SUMMARY, reason='코드나 특정 구절을 설명하기 전에 수업과 문제의 맥락을 알려 줘요.',
            details=['첫 단계: 교육목표 → 진행 흐름 → 이번 문제 → 상세 해설 순서예요.',
                     '이후 단계: 이번 문제 → 상세 해설 순서예요.',
                     '문제 ID·채점·실행 코드·학습 기록을 유지해요. 앱 설치 없이 수업을 갱신해요.']))
    if merged != current:
        raw = (json.dumps(merged, ensure_ascii=False, indent=2) + '\n').encode()
        result = gh(f'repos/{repository}/contents/course.json', 'PUT', dict(
            message='Publish lesson and problem narration orientation', branch='main',
            sha=file['sha'], content=base64.b64encode(raw).decode('ascii')))
        _, verified = read_course(repository, result['commit']['sha'])
        if verified != merged:
            raise ValueError('Published course bytes differ')
    for attempt in range(5):
        _, visible = read_course(repository)
        if all(pin(next(r for r in visible['lessons'] if r['id'] == new['id'])) == pin(new) for _, new, _ in rows):
            print(f'PUBLIC {repository}: {len(rows)} lesson pins verified', flush=True)
            return
        time.sleep(2)
    raise ValueError('Course commit published; main cache not visible yet')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    for command in ([sys.executable, 'tools/test_narration_openings.py'],
                    [sys.executable, 'tools/build-redesigned-git.py', '--check'],
                    [sys.executable, 'tools/build-redesigned-course-bundle.py', '--check']):
        result = subprocess.run(command, cwd=ROOT, capture_output=True)
        if result.returncode:
            sys.stderr.buffer.write(result.stdout + result.stderr)
            raise RuntimeError('Content validation failed')
    courses = prepare()
    if not args.publish:
        return
    user = gh('user')
    if (user['login'], user['id']) != ('jhs512', 4741844):
        raise ValueError('Unexpected publishing account')
    for repository, rows in courses:
        for old, new, raw in rows:
            publisher.publish_lesson(old, new, raw, 'Explain lesson goals and problem before detailed narration')
        publish_course(repository, rows)
    print('COMPLETE: 94 lessons / 925 steps published and verified; no app release', flush=True)


if __name__ == '__main__':
    main()
