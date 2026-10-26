"""Publish only the verified native-output Docker lesson after its runtime release."""
import argparse
import base64
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('coding_publisher', ROOT / 'tools/publish-coding-conversions.py')
publisher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)
gh = publisher.gh
APP = 'jhs512/immersion-quest-3'
COURSE = publisher.COURSE
KEY = 'docker-image-container'
REPO = 'jhs512/mq3-lesson-redesigned-' + KEY
RUNTIME_COMMIT = 'd35ea47'


def read_course():
    file = gh(f'repos/{COURSE}/contents/course.json?ref=main')
    return file, json.loads(base64.b64decode(file['content']))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime-release', required=True)
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    raw = (ROOT / f'courses/redesigned/{KEY}.json').read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    proof = json.loads((ROOT / f'target/mcq/{KEY}.json').read_text(encoding='utf-8'))
    prepared = json.loads((ROOT / 'courses/redesigned-courses/java-backend.json').read_text(encoding='utf-8'))
    new = next(row for row in prepared['lessons'] if row['repository'] == REPO)
    if not proof.get('passed') or proof['lesson_sha256'] != digest or new['sha256'] != digest:
        raise ValueError('Current lesson execution evidence is required')
    _, initial = read_course()
    if initial['id'] != prepared['id'] or initial['repository'] != COURSE:
        raise ValueError('Unexpected course identity')
    old = next(row for row in initial['lessons'] if row['repository'] == REPO)
    if old['id'] != new['id'] or old['revision'] not in ('docker-image-container-3', new['revision']):
        raise ValueError('Unexpected published revision')
    if old['revision'] == new['revision'] and old['sha256'] != digest:
        raise ValueError('Published immutable revision has different bytes')
    print(f'Verified {len(proof["steps"])} steps; {old["revision"]} -> {new["revision"]}', flush=True)
    if not args.publish:
        return
    user = gh('user')
    if (user['login'], user['id']) != ('jhs512', 4741844):
        raise ValueError('Unexpected GitHub account')
    release = gh(f'repos/{APP}/releases/tags/{args.runtime_release}')
    names = [asset['name'].lower() for asset in release.get('assets', [])]
    if release.get('draft') or release.get('prerelease') or not all(any(n.endswith(ext) for n in names) for ext in ('.exe', '.dmg')):
        raise ValueError('Both public desktop installers must exist first')
    comparison = gh(f'repos/{APP}/compare/{RUNTIME_COMMIT}...{args.runtime_release}')
    if comparison['status'] not in ('identical', 'ahead'):
        raise ValueError('Release lacks native output and Nginx support')
    publisher.publish_lesson(old, new, raw, 'Use real Nginx commands and native Docker output')
    current, remote = read_course()
    actual_old = next(row for row in remote['lessons'] if row['repository'] == REPO)
    pin = lambda row: (row['id'], row['revision'], row['sha256'])
    if pin(actual_old) not in (pin(old), pin(new)):
        raise ValueError('Concurrent lesson revision changed')
    merged = copy.deepcopy(remote)
    row = next(row for row in merged['lessons'] if row['repository'] == REPO)
    row.update({key: new[key] for key in ('title', 'revision', 'sha256')})
    merged.setdefault('lesson_previews', {})[new['id']] = prepared['lesson_previews'][new['id']]
    summary = 'Docker 입문을 Nginx 직접 실행과 실제 명령 출력으로 바꿨어요.'
    if not any(change.get('summary') == summary for change in merged.get('change_history', [])):
        merged.setdefault('change_history', []).insert(0, dict(
            at=datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z'),
            summary=summary, reason='사용자 요청: 실습 이름과 포트를 구분하고 실제 Docker 결과를 읽어요.',
            details=['고유 이름과 빈 루프백 포트를 사용해요.', '같은 문제의 재실행은 컨테이너 상태를 유지해요.',
                     '기존 문제 ID와 학습 기록은 유지해요.', f'{args.runtime_release} 이상 앱에서 Nginx 실습을 지원해요.']))
    if merged != remote:
        body = (json.dumps(merged, ensure_ascii=False, indent=2) + '\n').encode()
        gh(f'repos/{COURSE}/contents/course.json', 'PUT', dict(
            message='Publish Nginx CLI lesson with native Docker output', branch='main',
            sha=current['sha'], content=base64.b64encode(body).decode('ascii')))
    _, actual = read_course()
    if actual != merged:
        raise ValueError('Published course differs')
    print('VERIFIED public Nginx CLI lesson revision', flush=True)


if __name__ == '__main__':
    main()
