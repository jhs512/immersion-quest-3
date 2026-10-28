"""Publish the three Docker lessons that run in the real practice terminal, after their app release.

The lessons use git_terminal.docker.compose, which older apps cannot validate. So this refuses to publish
until a public release with both desktop installers contains the runtime commit. Each lesson needs current
real PTY/Docker evidence for its exact bytes (target/docker-terminal-integration/<key>.json from
validate_redesigned_lesson). Tags are immutable: an existing tag must already hold the same bytes. Only the
three Docker pins and their previews change in the course; every other pin and field is kept from the remote.
"""
import argparse
import base64
import copy
import hashlib
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('coding_publisher', ROOT / 'tools/publish-coding-conversions.py')
publisher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)
gh = publisher.gh
APP = 'jhs512/immersion-quest-3'
COURSE = publisher.COURSE
KEYS = ('docker-image-container', 'docker-network-ports', 'docker-compose-db')
PUBLISHED = {'docker-image-container': 'docker-image-container-6', 'docker-network-ports': 'docker-network-ports-3',
             'docker-compose-db': 'docker-compose-db-4'}
EVIDENCE = ROOT / 'target/docker-terminal-integration'
SUMMARY = 'Docker 수업의 Compose·Dockerfile 문제도 실제 터미널에서 직접 명령을 입력해요.'


def read_course():
    file = gh(f'repos/{COURSE}/contents/course.json?ref=main')
    return file, json.loads(base64.b64decode(file['content']))


def pin(row):
    return row['id'], row['revision'], row['sha256']


def prepare():
    prepared = json.loads((ROOT / 'courses/redesigned-courses/java-backend.json').read_text(encoding='utf-8'))
    _, remote = read_course()
    if remote['id'] != prepared['id'] or remote['repository'] != COURSE:
        raise ValueError('Unexpected course identity')
    rows = []
    for key in KEYS:
        repo = 'jhs512/mq3-lesson-redesigned-' + key
        raw = (ROOT / f'courses/redesigned/{key}.json').read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        new = next(row for row in prepared['lessons'] if row['repository'] == repo)
        old = next(row for row in remote['lessons'] if row['repository'] == repo)
        proof = json.loads((EVIDENCE / f'{key}.json').read_text(encoding='utf-8'))
        if not proof.get('passed') or proof.get('lesson_sha256') != digest or proof.get('revision') != new['revision']:
            raise ValueError(f'Current real PTY/Docker evidence is required: {key}')
        if new['sha256'] != digest or json.loads(raw).get('revision') != new['revision']:
            raise ValueError(f'Prepared pin does not match the lesson file: {key}')
        if old['revision'] == new['revision']:
            if old['sha256'] != digest:
                raise ValueError(f'Published immutable revision has different bytes: {key}')
        elif old['revision'] != PUBLISHED[key]:
            raise ValueError(f'Unexpected published revision {old["revision"]}: {key}')
        else:
            publisher.check_transition(key, old, new)
        tag = gh(f'repos/{repo}/git/ref/tags/{new["revision"]}', optional=True)
        if tag is not None:
            tagged = base64.b64decode(gh(f'repos/{repo}/contents/lesson.json?ref={new["revision"]}')['content'])
            if tagged != raw:
                raise ValueError(f'Tag {new["revision"]} already exists with other bytes; choose the next revision: {key}')
        print(f'Verified {key}: {len(proof["steps"])} steps in {proof["seconds"]:.0f}s, '
              f'{old["revision"]} -> {new["revision"]} ({digest[:12]})', flush=True)
        rows.append((old, new, raw))
    return prepared, rows


def check_release(tag, commit):
    release = gh(f'repos/{APP}/releases/tags/{tag}')
    names = [asset['name'].lower() for asset in release.get('assets', [])]
    if release.get('draft') or release.get('prerelease') or not all(any(n.endswith(ext) for n in names) for ext in ('.exe', '.dmg')):
        raise ValueError('Both public desktop installers must exist first')
    comparison = gh(f'repos/{APP}/compare/{commit}...{tag}')
    if comparison['status'] not in ('identical', 'ahead'):
        raise ValueError(f'{tag} does not contain the Docker terminal runtime {commit}')
    print(f'Release {tag} contains {commit[:12]}; assets: {", ".join(sorted(names))}', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--runtime-release', required=True)
    parser.add_argument('--runtime-commit', required=True)
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    prepared, rows = prepare()
    check_release(args.runtime_release, args.runtime_commit)
    if not args.publish:
        return
    user = gh('user')
    if (user['login'], user['id']) != ('jhs512', 4741844):
        raise ValueError('Unexpected GitHub account')
    for old, new, raw in rows:
        publisher.publish_lesson(old, new, raw, 'Type Docker CLI and Compose commands in the real practice terminal')
    current, remote = read_course()
    merged = copy.deepcopy(remote)
    for old, new, _ in rows:
        row = next(row for row in merged['lessons'] if row['repository'] == new['repository'])
        if pin(row) not in (pin(old), pin(new)):
            raise ValueError('Concurrent lesson revision changed: ' + new['repository'])
        row.update({key: new[key] for key in ('title', 'revision', 'sha256')})
        merged.setdefault('lesson_previews', {})[new['id']] = prepared['lesson_previews'][new['id']]
    if not any(change.get('summary') == SUMMARY for change in merged.get('change_history', [])):
        merged.setdefault('change_history', []).insert(0, dict(
            at=datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z'), summary=SUMMARY,
            reason='사용자 요청: Docker 문제를 commands.sh 대신 실제 터미널에서 풀어요.',
            details=['편집기는 compose.yaml·Dockerfile 같은 실습 파일만 고치고, 명령은 터미널에 직접 입력해요.',
                     '채점은 정답을 다시 실행하지 않고 지금의 실제 Docker 상태와 입력한 명령을 읽어요.',
                     '문제마다 고유한 프로젝트 이름과 127.0.0.1의 빈 포트를 써요. 수업을 나가면 이 수업이 만든 것만 정리해요.',
                     '기존 문제 ID와 학습 기록은 유지해요.', f'{args.runtime_release} 이상 앱에서 지원해요.']))
    others = lambda course: [pin(row) for row in course['lessons'] if row['repository'] not in {new['repository'] for _, new, _ in rows}]
    if others(merged) != others(remote):
        raise ValueError('Another lesson pin would change')
    if merged != remote:
        body = (json.dumps(merged, ensure_ascii=False, indent=2) + '\n').encode()
        result = gh(f'repos/{COURSE}/contents/course.json', 'PUT', dict(
            message='Publish Docker lessons that run in the real practice terminal', branch='main',
            sha=current['sha'], content=base64.b64encode(body).decode('ascii')))
        readback = base64.b64decode(gh(f'repos/{COURSE}/contents/course.json?ref={result["commit"]["sha"]}')['content'])
        if readback != body:
            raise ValueError('Published course readback differs')
        print('Course commit ' + result['commit']['sha'], flush=True)
    _, actual = read_course()
    if actual != merged:
        raise ValueError('Published course differs')
    print('VERIFIED public Docker terminal lesson revisions: ' + ', '.join(new['revision'] for _, new, _ in rows), flush=True)


if __name__ == '__main__':
    main()
