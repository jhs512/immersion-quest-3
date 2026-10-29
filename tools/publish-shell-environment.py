"""Publish the three shell variable / environment / argument lessons and the final-challenge designations.

Scope (2026-10-29): creates jhs512/mq3-lesson-redesigned-{bash-variables,bash-environment,bash-command-env-args}
with immutable revision tags, then updates only the backend course.json: inserts the three lesson refs in the
prepared order (after java-arguments), adds `challenge_task` to the designated lessons, adds the three previews
and one change-history entry. Every other pin, field and the published order of existing lessons is kept from
the remote. The course is written only after a public release with both desktop installers contains the app
commit that understands lesson resets and challenge clears (older apps ignore `challenge_task`).

Default: verify and print the plan. --publish performs the writes and reads every byte back.
    python tools/publish-shell-environment.py --runtime-release v0.1.0-build.N --runtime-commit <sha> [--publish]
"""
import argparse
import base64
import copy
import hashlib
import importlib.util
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('content_publisher', ROOT / 'tools/publish-redesigned-courses.py')
publisher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)
gh = publisher.gh
APP = 'jhs512/immersion-quest-3'
COURSE = 'jhs512/mq3-course-redesigned-java-backend'
KEYS = ('bash-variables', 'bash-environment', 'bash-command-env-args')
SUMMARY = '셸 변수·환경 변수·실행 인자 수업 3개를 더하고, 수업별 진도 초기화와 마지막 도전 클리어를 지원해요.'
PIN = ('id', 'title', 'repository', 'revision', 'sha256', 'prerequisites', 'required', 'review_enabled', 'category', 'track')


def read_course():
    file = gh(f'repos/{COURSE}/contents/course.json?ref=main')
    return file, json.loads(base64.b64decode(file['content']))


def key_of(row):
    return row['repository'].removeprefix('jhs512/mq3-lesson-redesigned-')


def prepare():
    subprocess.run(['python', str(ROOT / 'tools/build-redesigned-course-bundle.py'), '--check'], cwd=ROOT / 'tools', check=True)
    prepared = json.loads((ROOT / 'courses/redesigned-courses/java-backend.json').read_text(encoding='utf-8'))
    _, remote = read_course()
    if remote['id'] != prepared['id'] or remote['repository'] != COURSE:
        raise ValueError('Unexpected course identity')
    by_repo = {row['repository']: row for row in prepared['lessons']}
    # Every remote lesson must already be the prepared pin: this release never rolls a lesson back.
    for row in remote['lessons']:
        mine = by_repo.get(row['repository'])
        if mine is None or (mine['revision'], mine['sha256']) != (row['revision'], row['sha256']):
            raise ValueError(f'Remote pin differs from the prepared course: {key_of(row)} {row["revision"]}')
    values = next(row for row in remote['lessons'] if key_of(row) == 'java-values')
    if values['revision'] != 'java-values-7':
        raise ValueError('First Java lesson must stay java-values-7')
    rows = []
    for key in KEYS:
        new = next(row for row in prepared['lessons'] if key_of(row) == key)
        raw = (ROOT / 'courses/redesigned' / f'{key}.json').read_bytes()
        if hashlib.sha256(raw).hexdigest() != new['sha256'] or json.loads(raw)['revision'] != new['revision']:
            raise ValueError(f'Prepared pin does not match the lesson file: {key}')
        if any(row['repository'] == new['repository'] for row in remote['lessons']):
            raise ValueError(f'Lesson already in the course: {key}')
        tag = gh(f'repos/{new["repository"]}/git/ref/tags/{new["revision"]}', optional=True)
        if tag is not None:
            tagged = base64.b64decode(gh(f'repos/{new["repository"]}/contents/lesson.json?ref={new["revision"]}')['content'])
            if tagged != raw:
                raise ValueError(f'Tag {new["revision"]} already exists with other bytes: {key}')
        print(f'Prepared {key}: {new["revision"]} {new["sha256"][:12]} ({len(json.loads(raw)["tasks"])} steps)', flush=True)
        rows.append((new, raw))
    return prepared, remote, rows


def evidence():
    """Real PTY Bash (+ JDK) run of every step and challenge variant for these exact bytes."""
    run = subprocess.run(['cargo', 'test', '--locked', '--test', 'shell_environment_lessons', '--', '--test-threads=2'],
                         cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if run.returncode != 0 or 'test result: ok. 7 passed' not in run.stdout:
        raise ValueError('Real PTY lesson tests must pass first:\n' + run.stdout[-3000:] + run.stderr[-3000:])
    print('Real PTY lesson tests passed (7)', flush=True)


def check_release(tag, commit):
    release = gh(f'repos/{APP}/releases/tags/{tag}')
    names = [asset['name'].lower() for asset in release.get('assets', [])]
    if release.get('draft') or release.get('prerelease') or not all(any(n.endswith(ext) for n in names) for ext in ('.exe', '.dmg')):
        raise ValueError('Both public desktop installers must exist first')
    comparison = gh(f'repos/{APP}/compare/{commit}...{tag}')
    if comparison['status'] not in ('identical', 'ahead'):
        raise ValueError(f'{tag} does not contain the reset/challenge runtime {commit}')
    print(f'Release {tag} contains {commit[:12]}; assets: {", ".join(sorted(names))}', flush=True)


def merge(prepared, remote, rows, release):
    merged = copy.deepcopy(remote)
    remote_rows = {row['repository']: row for row in remote['lessons']}
    lessons = []
    for row in prepared['lessons']:
        if row['repository'] in remote_rows:
            current = copy.deepcopy(remote_rows[row['repository']])
            current.pop('challenge_task', None)
            if row.get('challenge_task'):
                current['challenge_task'] = row['challenge_task']
            lessons.append(current)
        elif key_of(row) in KEYS:
            lessons.append(copy.deepcopy(row))
        else:
            raise ValueError(f'Prepared lesson missing remotely and not in this release: {key_of(row)}')
    merged['lessons'] = lessons
    for new, _ in rows:
        merged.setdefault('lesson_previews', {})[new['id']] = prepared['lesson_previews'][new['id']]
    if not any(change.get('summary') == SUMMARY for change in merged.get('change_history', [])):
        merged.setdefault('change_history', []).insert(0, dict(
            at=datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z'), summary=SUMMARY,
            reason='사용자 요청: 셸 변수와 환경 변수, 명령 한 번의 환경과 실행 인자를 실제 Bash로 익히고, 수업을 직접 다시 시작하거나 마지막 도전으로 클리어해요.',
            details=['자바 실행 인자 수업 뒤에 선택 수업 3개(셸 변수, export와 자식 프로세스, 명령 한 번의 환경 값과 실행 인자)를 넣었어요.',
                     '수업 19개의 마지막 종합 문제를 「수업 클리어 도전」으로 지정했어요. 통과하면 건너뛴 문제가 있어도 수업을 클리어하고, 문제 진도는 그대로 세요.',
                     '학습 정보에서 수업 하나의 진도를 초기화할 수 있어요. 작성한 코드와 다른 수업은 그대로예요.',
                     '기존 수업의 버전·문제 ID·학습 기록은 바꾸지 않았어요.', f'{release} 이상 앱에서 초기화와 도전 클리어를 지원해요.']))
    # Guards: existing lessons keep every pinned field and their relative order; only challenge_task may be added.
    strip = lambda row: {k: v for k, v in row.items() if k != 'challenge_task'}
    old_order = [row['repository'] for row in remote['lessons']]
    kept = [row for row in merged['lessons'] if row['repository'] in remote_rows]
    if [row['repository'] for row in kept] != old_order:
        raise ValueError('Existing lessons would be reordered')
    if any(strip(row) != strip(remote_rows[row['repository']]) for row in kept):
        raise ValueError('An existing lesson pin would change')
    if [row['id'] for row in merged['lessons']] != [row['id'] for row in prepared['lessons']]:
        raise ValueError('Course order differs from the prepared sequence')
    for field in set(remote) - {'lessons', 'lesson_previews', 'change_history'}:
        if merged[field] != remote[field]:
            raise ValueError(f'Course field would change: {field}')
    return merged


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--runtime-release', required=True)
    parser.add_argument('--runtime-commit', required=True)
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    prepared, remote, rows = prepare()
    evidence()
    check_release(args.runtime_release, args.runtime_commit)
    plan = merge(prepared, remote, rows, args.runtime_release)
    print(f'Plan: {len(remote["lessons"])} -> {len(plan["lessons"])} lessons; challenge designations '
          f'{sum(1 for row in plan["lessons"] if row.get("challenge_task"))}', flush=True)
    if not args.publish:
        return
    user = gh('user')
    if (user['login'], user['id']) != ('jhs512', 4741844):
        raise ValueError('Unexpected GitHub account')
    for new, raw in rows:
        publisher.publish_file(new['repository'], 'lesson.json', raw, new['revision'])
    current, latest = read_course()
    if latest != remote:
        raise ValueError('The remote course changed during publication; rerun to merge the newer course')
    body = (json.dumps(plan, ensure_ascii=False, indent=2) + '\n').encode()
    result = gh(f'repos/{COURSE}/contents/course.json', 'PUT', dict(
        message='Add shell environment lessons and final-challenge designations', branch='main',
        sha=current['sha'], content=base64.b64encode(body).decode('ascii')))
    readback = base64.b64decode(gh(f'repos/{COURSE}/contents/course.json?ref={result["commit"]["sha"]}')['content'])
    if readback != body:
        raise ValueError('Published course readback differs')
    print('Course commit ' + result['commit']['sha'], flush=True)
    print('course.json sha256 ' + hashlib.sha256(body).hexdigest(), flush=True)
    for new, raw in rows:
        tagged = base64.b64decode(gh(f'repos/{new["repository"]}/contents/lesson.json?ref={new["revision"]}')['content'])
        if tagged != raw:
            raise ValueError('Lesson tag readback differs: ' + new['repository'])
        print(f'VERIFIED {new["repository"]}@{new["revision"]} {hashlib.sha256(tagged).hexdigest()}', flush=True)


if __name__ == '__main__':
    main()
