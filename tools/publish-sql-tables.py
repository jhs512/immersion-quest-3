"""Publish only the five verified SQL table-display revisions, preserving other lessons."""
import argparse
import base64
import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]
module = importlib.util.spec_from_file_location('coding_publisher', ROOT / 'tools/publish-coding-conversions.py')
publisher = importlib.util.module_from_spec(module)
module.loader.exec_module(publisher)
gh = publisher.gh
KEYS = ['sql-first', 'sql-tables-constraints', 'sql-join-group', 'sql-index-plan', 'sql-transactions']


def course():
    file = gh(f'repos/{publisher.COURSE}/contents/course.json?ref=main')
    return file, json.loads(base64.b64decode(file['content']))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    prepared = json.loads((ROOT / 'courses/redesigned-courses/java-backend.json').read_text(encoding='utf-8'))
    _, remote = course()
    if (remote['id'], remote['repository']) != (prepared['id'], publisher.COURSE):
        raise ValueError('Unexpected course identity')
    rows = []
    for key in KEYS:
        repository = 'jhs512/mq3-lesson-redesigned-' + key
        old = next(row for row in remote['lessons'] if row['repository'] == repository)
        new = next(row for row in prepared['lessons'] if row['repository'] == repository)
        raw = (ROOT / f'courses/redesigned/{key}.json').read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        proof = json.loads((ROOT / f'target/mcq/{key}.json').read_text(encoding='utf-8'))
        if not proof.get('passed') or proof.get('lesson_sha256') != digest or new['sha256'] != digest:
            raise ValueError('Current execution evidence required: ' + key)
        if old['id'] != new['id'] or old['revision'] not in (key + '-2', new['revision']):
            raise ValueError('Concurrent revision changed: ' + key)
        if old['revision'] == new['revision'] and old['sha256'] != digest:
            raise ValueError('Immutable revision differs: ' + key)
        rows.append((old, new, raw))
        print(f'Verified {key}: {len(proof["steps"])} steps', flush=True)
    if not args.publish:
        return
    user = gh('user')
    if (user['login'], user['id']) != ('jhs512', 4741844):
        raise ValueError('Unexpected publishing account')
    release = gh('repos/jhs512/immersion-quest-3/releases/tags/v0.1.0-build.143')
    if release.get('draft') or release.get('prerelease'):
        raise ValueError('The raw/grading runtime must already be public')
    for old, new, raw in rows:
        publisher.publish_lesson(old, new, raw, 'Show native SQL tables while preserving grading')
    file, current = course()
    merged = copy.deepcopy(current)
    pin = lambda row: (row['id'], row['revision'], row['sha256'])
    for old, new, _ in rows:
        row = next(row for row in merged['lessons'] if row['repository'] == new['repository'])
        if pin(row) not in (pin(old), pin(new)):
            raise ValueError('Course changed during publication')
        row.update({key: new[key] for key in ('title', 'revision', 'sha256')})
    summary = 'SQL 조회 결과를 열 이름과 행이 있는 표로 보여 줘요.'
    if not any(item.get('summary') == summary for item in merged.get('change_history', [])):
        merged.setdefault('change_history', []).insert(0, dict(
            at=datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z'),
            summary=summary, reason='실제 MySQL·PostgreSQL 조회 결과를 읽을 수 있게 해요.',
            details=['SQL 기초·제약·JOIN·인덱스·트랜잭션의 39개 문제에 적용했어요.',
                     '채점 데이터와 기존 문제 ID·학습 기록은 유지해요.',
                     '빌드 143 이상에서 표를 표시해요. 앱 재배포 없이 수업만 갱신해요.']))
    if merged != current:
        body = (json.dumps(merged, ensure_ascii=False, indent=2) + '\n').encode()
        result = gh(f'repos/{publisher.COURSE}/contents/course.json', 'PUT', dict(
            message='Publish SQL query table display', branch='main', sha=file['sha'],
            content=base64.b64encode(body).decode('ascii')))
        # Verify the exact commit returned by the write, avoiding a stale main cache.
        verified = gh(f'repos/{publisher.COURSE}/contents/course.json?ref={result["commit"]["sha"]}')
        if json.loads(base64.b64decode(verified['content'])) != merged:
            raise ValueError('Published course bytes differ')
    for attempt in range(5):
        _, visible = course()
        if all(pin(next(row for row in visible['lessons'] if row['repository'] == new['repository'])) == pin(new)
               for _, new, _ in rows):
            print('VERIFIED all five public SQL table revisions', flush=True)
            return
        time.sleep(2)
    raise ValueError('Published commit verified, but main is not visible yet')


if __name__ == '__main__':
    main()
