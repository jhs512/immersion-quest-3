"""Publish the GitLab MR / remote / CI lessons of the backend course (2026-10-29).

Scope: exactly three lesson repositories change.
  - jhs512/mq3-lesson-redesigned-github-pr: revision github-pr-5 -> gitlab-mr-1 (key kept for progress
    compatibility; visible title GitLab MR), and its designated final `challenge_task`.
  - jhs512/mq3-lesson-redesigned-git-remote: git-remote-12 -> git-remote-13 (two GitHub links replaced).
  - jhs512/mq3-lesson-redesigned-gitlab-ci: new repository, gitlab-ci-1, inserted after docker-image-container.
The backend course.json keeps every other pin, field, prerequisite, preview, challenge designation and the
order of existing lessons from the remote; it gains the three previews and one change-history entry. Lesson
tags are immutable: an existing tag with other bytes stops the run. The course write is a compare-and-swap
on the course.json blob sha, then every byte is read back.

These lessons use lesson schema 3 (GitLab exercises). Older apps reject schema 3 instead of silently passing
an empty goal, so the course is written only after a public release with both desktop installers contains
the runtime commit.

Default: verify and print the plan. --publish performs the writes.
    python tools/publish-gitlab-courses.py --runtime-release v0.1.0-build.N --runtime-commit <sha> [--publish]
"""
import argparse
import base64
import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'tools' / file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


content = load('content_publisher', 'publish-redesigned-courses.py')
coding = load('coding_publisher', 'publish-coding-conversions.py')
gh = content.gh
APP = 'jhs512/immersion-quest-3'
COURSE = 'jhs512/mq3-course-redesigned-java-backend'
PREFIX = 'jhs512/mq3-lesson-redesigned-'
# key -> revision expected on the remote now (None: the lesson is new).
CHANGES = {'github-pr': 'github-pr-5', 'git-remote': 'git-remote-12', 'gitlab-ci': None}
SUMMARY = 'GitHub 원격·PR 실습을 로컬 GitLab과 MR로 바꾸고, GitLab CI/CD 수업을 더했어요.'
# Fields of a lesson row this release may change; all others must stay as the remote has them.
UPDATED = ('title', 'revision', 'sha256', 'challenge_task')
# Real local GitLab runs (tests/gitlab_platform.rs --ignored): log -> (lesson it exercised, passing lines).
LIVE_LOGS = {'target/gitlab-work/run2/live-mr.log': ('github-pr', ('actual_gitlab_mr_lifecycle_passes_each_stage_and_rejects_unmerged_final ... ok',
                                                                   'Verified authored MR step: 새 프로젝트에서 변경 제안부터 병합까지 마치세요',
                                                                   'test result: ok. 2 passed')),
             'target/gitlab-work/run2/live-ci.log': ('gitlab-ci', ('Verified: 실패한 검사를 고치고 결과 파일까지 남기세요',
                                                                   'test result: ok. 1 passed'))}


def key_of(row):
    return row['repository'].removeprefix(PREFIX)


def read_course():
    file = gh(f'repos/{COURSE}/contents/course.json?ref=main')
    return file, json.loads(base64.b64decode(file['content']))


def prepare():
    subprocess.run([sys.executable, str(ROOT / 'tools/build-redesigned-course-bundle.py'), '--check'], cwd=ROOT / 'tools', check=True)
    prepared = json.loads((ROOT / 'courses/redesigned-courses/java-backend.json').read_text(encoding='utf-8'))
    _, remote = read_course()
    if remote['id'] != prepared['id'] or remote['repository'] != COURSE:
        raise ValueError('Unexpected course identity')
    mine = {row['repository']: row for row in prepared['lessons']}
    theirs = {row['repository']: row for row in remote['lessons']}
    for repository, row in theirs.items():
        if repository not in mine:
            raise ValueError(f'Remote lesson missing from the prepared course: {key_of(row)}')
        if key_of(row) in CHANGES:
            continue
        pin = lambda r: (r['id'], r['revision'], r['sha256'], r.get('challenge_task'))
        if pin(row) != pin(mine[repository]):
            raise ValueError(f'Unrelated lesson differs from the remote; refusing to roll it: {key_of(row)}')
    rows = []
    for key, expected in CHANGES.items():
        new = mine[PREFIX + key]
        old = theirs.get(PREFIX + key)
        raw = (ROOT / 'courses/redesigned' / f'{key}.json').read_bytes()
        lesson = json.loads(raw)
        if hashlib.sha256(raw).hexdigest() != new['sha256'] or lesson['revision'] != new['revision']:
            raise ValueError(f'Prepared pin does not match the lesson file: {key}')
        if expected is None:
            if old is not None:
                raise ValueError(f'Lesson unexpectedly exists in the course already: {key}')
        elif old is None or old['id'] != new['id'] or old['revision'] not in (expected, new['revision']):
            raise ValueError(f'Unexpected published revision of {key}: {old and old["revision"]}')
        elif old['revision'] == new['revision'] and old['sha256'] != new['sha256']:
            raise ValueError(f'Published immutable revision has different bytes: {key}')
        tag = gh(f'repos/{new["repository"]}/git/ref/tags/{new["revision"]}', optional=True)
        if tag is not None:
            tagged = base64.b64decode(gh(f'repos/{new["repository"]}/contents/lesson.json?ref={new["revision"]}')['content'])
            if tagged != raw:
                raise ValueError(f'Tag {new["revision"]} already exists with other bytes: {key}')
        print(f'Prepared {key}: {old["revision"] if old else "(new)"} -> {new["revision"]} '
              f'{new["sha256"][:12]} schema {lesson["schema_version"]}, {len(lesson["tasks"])} steps', flush=True)
        rows.append((old, new, raw))
    return prepared, remote, rows


def evidence(rows):
    """Structural suites now, plus the real local GitLab runs recorded after these lesson bytes."""
    run = subprocess.run(['cargo', 'test', '--locked', '--test', 'gitlab_platform', '--test', 'backend_journeys',
                          '--test', 'bundled_courses', '--test', 'challenges', '--test', 'github_pr'],
                         cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if run.returncode != 0 or ' failed;' in run.stdout.replace(' 0 failed;', ''):
        raise ValueError('Structural lesson tests must pass first:\n' + run.stdout[-3000:] + run.stderr[-3000:])
    print('Structural lesson tests passed', flush=True)
    for name, (key, lines) in LIVE_LOGS.items():
        path = ROOT / name
        text = path.read_text(encoding='utf-8', errors='replace') if path.exists() else ''
        lesson = ROOT / 'courses/redesigned' / f'{key}.json'
        # The run must postdate the lesson bytes it exercised.
        if not all(line in text for line in lines) or path.stat().st_mtime < lesson.stat().st_mtime:
            raise ValueError(f'Real local GitLab evidence for the current {key} bytes is missing: {name}')
        print(f'Real local GitLab evidence for {key}: {name}', flush=True)


def check_release(tag, commit):
    release = gh(f'repos/{APP}/releases/tags/{tag}')
    names = [asset['name'].lower() for asset in release.get('assets', [])]
    if release.get('draft') or release.get('prerelease') or not all(any(n.endswith(ext) for n in names) for ext in ('.exe', '.dmg')):
        raise ValueError('Both public desktop installers must exist first')
    comparison = gh(f'repos/{APP}/compare/{commit}...{tag}')
    if comparison['status'] not in ('identical', 'ahead'):
        raise ValueError(f'{tag} does not contain the schema 3 GitLab runtime {commit}')
    print(f'Release {tag} contains {commit[:12]}; assets: {", ".join(sorted(names))}', flush=True)


def merge(prepared, remote, rows, release):
    merged = copy.deepcopy(remote)
    theirs = {row['repository']: row for row in remote['lessons']}
    changed = {new['repository']: new for _, new, _ in rows}
    lessons = []
    for row in prepared['lessons']:
        current = theirs.get(row['repository'])
        if row['repository'] in changed:
            if current is None:
                lessons.append(copy.deepcopy(row))
            else:
                updated = copy.deepcopy(current)
                for field in UPDATED:
                    updated.pop(field, None)
                    if field in row:
                        updated[field] = row[field]
                lessons.append(updated)
        else:
            lessons.append(copy.deepcopy(current))
    merged['lessons'] = lessons
    for _, new, _ in rows:
        merged.setdefault('lesson_previews', {})[new['id']] = prepared['lesson_previews'][new['id']]
    if not any(change.get('summary') == SUMMARY for change in merged.get('change_history', [])):
        merged.setdefault('change_history', []).insert(0, dict(
            at=datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z'), summary=SUMMARY,
            reason='사용자 요청: 학생 원격 저장소·PR 실습을 GitLab 기반(MR)으로 바꾸고, .gitlab-ci.yml 워크플로(CI/CD) 수업을 더해요.',
            details=['원격 저장소 수업의 GitHub 링크 두 곳을 로컬 GitLab으로 바꿨어요.',
                     'PR 수업을 로컬 GitLab과 공식 glab CLI로 Merge Request를 만들고 병합하는 수업으로 바꾸고, 마지막 종합 문제를 더해 클리어 도전으로 지정했어요.',
                     'Docker 이미지·컨테이너 수업 뒤에 GitLab CI/CD 선택 수업(10문제)을 더했어요. 실제 러너가 실행한 파이프라인·작업 로그·산출물로 채점해요.',
                     '회원가입이나 로그인 없이 이 컴퓨터의 전용 로컬 계정을 쓰고, 수업을 떠나면 실습 서버를 멈춰요.',
                     '기존 문제 ID와 학습 기록은 유지해요.', f'{release} 이상 앱에서 GitLab 실습을 지원해요.']))
    # Guards: existing lessons keep their relative order and every field outside UPDATED.
    old_order = [row['repository'] for row in remote['lessons']]
    if [row['repository'] for row in merged['lessons'] if row['repository'] in theirs] != old_order:
        raise ValueError('Existing lessons would be reordered')
    strip = lambda row: {k: v for k, v in row.items() if k not in UPDATED}
    for row in merged['lessons']:
        if row['repository'] in theirs and (row['repository'] not in changed and row != theirs[row['repository']]
                                            or strip(row) != strip(theirs[row['repository']])):
            raise ValueError(f'An existing lesson pin would change: {key_of(row)}')
    if [row['id'] for row in merged['lessons']] != [row['id'] for row in prepared['lessons']]:
        raise ValueError('Course order differs from the prepared sequence')
    for field in set(remote) - {'lessons', 'lesson_previews', 'change_history'}:
        if merged[field] != remote[field]:
            raise ValueError(f'Course field would change: {field}')
    for lesson_id, preview in remote.get('lesson_previews', {}).items():
        if lesson_id not in changed_ids(rows) and merged['lesson_previews'][lesson_id] != preview:
            raise ValueError('An unrelated preview would change')
    return merged


def changed_ids(rows):
    return {new['id'] for _, new, _ in rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--runtime-release', required=True)
    parser.add_argument('--runtime-commit', required=True)
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    prepared, remote, rows = prepare()
    evidence(rows)
    check_release(args.runtime_release, args.runtime_commit)
    plan = merge(prepared, remote, rows, args.runtime_release)
    print(f'Plan: {len(remote["lessons"])} -> {len(plan["lessons"])} lessons; challenge designations '
          f'{sum(1 for row in plan["lessons"] if row.get("challenge_task"))}', flush=True)
    if not args.publish:
        return
    user = gh('user')
    if (user['login'], user['id']) != ('jhs512', 4741844):
        raise ValueError('Unexpected GitHub account')
    for old, new, raw in rows:
        if old is None:
            content.publish_file(new['repository'], 'lesson.json', raw, new['revision'])
        else:
            coding.publish_lesson(old, new, raw, 'Teach remote hosting with local GitLab, MRs and CI')
    current, latest = read_course()
    if latest != remote:
        raise ValueError('The remote course changed during publication; rerun to merge the newer course')
    body = (json.dumps(plan, ensure_ascii=False, indent=2) + '\n').encode()
    result = gh(f'repos/{COURSE}/contents/course.json', 'PUT', dict(
        message='Teach remote hosting with local GitLab MRs and add GitLab CI/CD', branch='main',
        sha=current['sha'], content=base64.b64encode(body).decode('ascii')))
    readback = base64.b64decode(gh(f'repos/{COURSE}/contents/course.json?ref={result["commit"]["sha"]}')['content'])
    if readback != body:
        raise ValueError('Published course readback differs')
    print('Course commit ' + result['commit']['sha'], flush=True)
    print('course.json sha256 ' + hashlib.sha256(body).hexdigest(), flush=True)
    for _, new, raw in rows:
        tagged = base64.b64decode(gh(f'repos/{new["repository"]}/contents/lesson.json?ref={new["revision"]}')['content'])
        if tagged != raw:
            raise ValueError('Lesson tag readback differs: ' + new['repository'])
        print(f'VERIFIED {new["repository"]}@{new["revision"]} {hashlib.sha256(tagged).hexdigest()}', flush=True)


if __name__ == '__main__':
    main()
