"""Publish the engineer-practical and AICE coding conversions of 2026-10-29 (Codex-relayed user request).

Scope: exactly the lessons listed in LESSONS change, in two course repositories.
  - Each lesson row changes only `revision` and `sha256`; ids, order, prerequisites, categories, tracks,
    previews, challenge designations and every other lesson stay as the remote has them now.
  - The remote pin of every listed lesson must still be the revision that origin/main's catalog names
    (the one this work started from), or the run stops instead of rolling someone else's update back.
  - Every lesson needs passing validator evidence for its exact bytes (target/mcq/<key>.json, written by
    tools/coding_conversion.py verify), and every converted step must be a coding step (no
    `interaction`), with the old choice step id gone.
Lesson tags are immutable: an existing tag with other bytes stops the run. The course write is a
compare-and-swap on the course.json blob sha, then every byte is read back.

Java lessons now carry `code_flow` steps and narrations with `code_flow` actions; an app without them
would not open 코드 흐름 보기. So the courses are written only after a public release with both desktop
installers contains the runtime commit.

Default: verify and print the plan. --publish performs the writes.
    python tools/publish-coding-trace-reset.py --runtime-release v0.1.0-build.N --runtime-commit <sha> [--publish]
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
conversion = load('coding_conversion', 'coding_conversion.py')
gh = content.gh
APP = 'jhs512/immersion-quest-3'
PREFIX = 'jhs512/mq3-lesson-redesigned-'
# The catalog this work started from (public build 154); origin/main now carries the new pins.
BASELINE = 'c593fb7604150c2b607d403fedc49e312b7dbb61'
LESSONS = {
    'engineer-practical': ['engineer-c-start', 'engineer-c-conditions', 'engineer-c-arrays', 'engineer-c-functions',
                           'engineer-c-pointers', 'engineer-c-double-pointers', 'engineer-c-structures',
                           'engineer-java-flow', 'engineer-java-references', 'engineer-java-static',
                           'engineer-java-polymorphism', 'engineer-python-values', 'engineer-python-calls',
                           'engineer-db-model', 'engineer-sql-select', 'engineer-sql-group', 'engineer-sql-change'],
    'aice-associate': ['aice-python-start', 'aice-python-conditions', 'aice-python-api', 'aice-table-csv',
                       'aice-selection', 'aice-quality', 'aice-join', 'aice-plots', 'aice-features', 'aice-scale',
                       'aice-regression', 'aice-regression-metrics'],
}
UPDATED = ('revision', 'sha256')
SUMMARY = {
    'engineer-practical': '코드를 고르던 문제를 직접 코드를 고쳐 실행하는 문제로 바꾸고, Java 코드 흐름 보기를 더했어요.',
    'aice-associate': '코드를 고르던 문제를 직접 pandas·scikit-learn 코드를 고쳐 실행하는 문제로 바꿨어요.',
}
DETAILS = {
    'engineer-practical': ['C·Java·Python·SQL 17수업에서 값·식·문장을 고르던 112문제를 직접 코드나 SQL을 고쳐 실행하고 제출하는 문제로 바꿨어요. 채점은 실제 실행 결과와 바꾼 준비 값으로 해요.',
                           '설계·테스트·보안 같은 개념 문제는 그대로예요.',
                           'Java 참조·static·다형성·실행 흐름 수업의 16문제에 「코드 흐름 보기」를 붙였어요. 지금 편집기의 코드를 수업과 같은 JDK 25로 실행하며 호출 스택·변수·객체를 한 단계씩 보여 줘요.',
                           '참조 1·3번, static 3번, 다형성 5번 문제의 해설은 이 화면을 직접 열어 설명하는 단계까지 보여 줘요.',
                           '본질이 바뀐 문제는 새 문제로 열려요. 이전 선택 문제의 완료 기록은 이전 버전에 남아요.'],
    'aice-associate': ['파이썬 기초·표·선택·품질·결합·그래프·특성·스케일·회귀·회귀 평가 12수업에서 고르던 76문제를 직접 코드를 고쳐 실행하는 문제로 바꿨어요. 학습 점수처럼 흔들리는 값이 아니라 선택한 열·모양·설정·누수 여부를 바꾼 준비 자료로 채점해요.',
                       '모델 해석 같은 개념 문제와 나머지 12수업의 문제는 그대로예요. 남은 수업의 전환은 이어서 진행해요.',
                       '본질이 바뀐 문제는 새 문제로 열려요. 이전 선택 문제의 완료 기록은 이전 버전에 남아요.'],
}
REASON = '사용자 요청: 「정처기에서도 코딩 문제에서는 객관식을 순수 코딩 문제로 바꾸자, 에이쓰에서도」 그리고 Java 메모리 시각화의 핵심을 수업에서 활용해요.'


def baseline_revisions():
    catalog = json.loads(subprocess.check_output(['git', 'show', f'{BASELINE}:tools/redesigned_courses/catalog.json'], cwd=ROOT))
    return {item['key']: item['revision'] for course in catalog['courses'] for item in course['lessons']}


def read_course(name):
    repository = 'jhs512/mq3-course-redesigned-' + name
    file = gh(f'repos/{repository}/contents/course.json?ref=main')
    return repository, file, json.loads(base64.b64decode(file['content']))


def converted_steps(key, lesson):
    """The converted steps of one lesson; each must now be a coding step under its new id."""
    specs = conversion.specs_for(key).SPECS
    tasks = {task['id']: task for task in lesson['tasks']}
    for spec in specs:
        new = conversion.new_step_id(spec['old'])
        if spec['old'] in tasks or new not in tasks or tasks[new].get('interaction'):
            raise ValueError(f'{key}: step {spec["old"]} is not a coding step under {new}')
    return len(specs)


def prepare():
    subprocess.run([sys.executable, str(ROOT / 'tools/build-redesigned-course-bundle.py'), '--check'], cwd=ROOT / 'tools', check=True)
    base = baseline_revisions()
    plans = []
    for name, keys in LESSONS.items():
        prepared = json.loads((ROOT / 'courses/redesigned-courses' / f'{name}.json').read_text(encoding='utf-8'))
        repository, file, remote = read_course(name)
        if remote['id'] != prepared['id'] or remote['repository'] != repository:
            raise ValueError(f'Unexpected course identity: {name}')
        mine = {row['repository']: row for row in prepared['lessons']}
        theirs = {row['repository']: row for row in remote['lessons']}
        if set(mine) != set(theirs):
            raise ValueError(f'Course membership differs from the remote: {name}')
        pin = lambda r: (r['id'], r['revision'], r['sha256'], r.get('challenge_task'))
        for repo, row in theirs.items():
            if repo.removeprefix(PREFIX) not in keys and pin(row) != pin(mine[repo]):
                raise ValueError(f'Unrelated lesson differs from the remote; refusing to roll it: {repo}')
        rows = []
        for key in keys:
            old, new = theirs[PREFIX + key], mine[PREFIX + key]
            raw = (ROOT / 'courses/redesigned' / f'{key}.json').read_bytes()
            digest = hashlib.sha256(raw).hexdigest()
            lesson = json.loads(raw)
            proof = json.loads((ROOT / 'target/mcq' / f'{key}.json').read_text(encoding='utf-8'))
            if not proof.get('passed') or proof.get('recorded_only') or proof.get('lesson_sha256') != digest:
                raise ValueError(f'Missing passing validator evidence for the current bytes: {key}')
            if digest != new['sha256'] or lesson['revision'] != new['revision'] or lesson['id'] != old['id']:
                raise ValueError(f'Prepared pin does not match the lesson file: {key}')
            if old['revision'] not in (base[key], new['revision']):
                raise ValueError(f'Remote {key} is at {old["revision"]}, not the baseline {base[key]}')
            if old['revision'] == new['revision'] and old['sha256'] != digest:
                raise ValueError(f'Published immutable revision has different bytes: {key}')
            coding.check_transition(key, {'id': old['id'], 'revision': base[key]}, new)
            if pin(old)[3] != pin(new)[3]:
                raise ValueError(f'Challenge designation would change: {key}')
            tag = gh(f'repos/{new["repository"]}/git/ref/tags/{new["revision"]}', optional=True)
            if tag is not None:
                tagged = base64.b64decode(gh(f'repos/{new["repository"]}/contents/lesson.json?ref={new["revision"]}')['content'])
                if tagged != raw:
                    raise ValueError(f'Tag {new["revision"]} already exists with other bytes: {key}')
            steps = converted_steps(key, lesson)
            flows = sum(1 for task in lesson['tasks'] if any(a.get('action') == 'code_flow' for a in task.get('narration', [])))
            print(f'Prepared {key}: {old["revision"]} -> {new["revision"]} {digest[:12]}, {steps} coding steps'
                  f' ({proof["rejected_answers"]} rejected / {proof["accepted_answers"]} accepted answers)'
                  + (f', {flows} narrated code-flow steps' if flows else ''), flush=True)
            rows.append((old, new, raw, steps))
        plans.append((name, repository, prepared, file, remote, rows))
    return plans


def check_release(tag, commit):
    release = gh(f'repos/{APP}/releases/tags/{tag}')
    names = [asset['name'].lower() for asset in release.get('assets', [])]
    if release.get('draft') or release.get('prerelease') or not all(any(n.endswith(ext) for n in names) for ext in ('.exe', '.dmg')):
        raise ValueError('Both public desktop installers must exist first')
    comparison = gh(f'repos/{APP}/compare/{commit}...{tag}')
    if comparison['status'] not in ('identical', 'ahead'):
        raise ValueError(f'{tag} does not contain the code-flow runtime {commit}')
    print(f'Release {tag} contains {commit[:12]}; assets: {", ".join(sorted(names))}', flush=True)


def merge(name, remote, rows, release, at=None):
    merged = copy.deepcopy(remote)
    changed = {new['repository']: new for _, new, _, _ in rows}
    for row in merged['lessons']:
        if row['repository'] in changed:
            for field in UPDATED:
                row[field] = changed[row['repository']][field]
    if not any(change.get('summary') == SUMMARY[name] for change in merged.get('change_history', [])):
        merged.setdefault('change_history', []).insert(0, dict(
            at=at or datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z'),
            summary=SUMMARY[name], reason=REASON,
            details=DETAILS[name] + ([f'{release} 이상 앱에서 코드 흐름 보기를 지원해요.'] if name == 'engineer-practical' else [])))
    # Guards: same lessons in the same order; outside the listed rows, nothing but the history entry changes.
    if [row['repository'] for row in merged['lessons']] != [row['repository'] for row in remote['lessons']]:
        raise ValueError('Lessons would be reordered')
    strip = lambda row: {k: v for k, v in row.items() if k not in UPDATED}
    for row, before in zip(merged['lessons'], remote['lessons']):
        if strip(row) != strip(before) or (row['repository'] not in changed and row != before):
            raise ValueError(f'A lesson field outside the scope would change: {row["repository"]}')
    for field in set(remote) | set(merged):
        if field not in ('lessons', 'change_history') and merged.get(field) != remote.get(field):
            raise ValueError(f'Course field would change: {field}')
    return merged


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--runtime-release', required=True)
    parser.add_argument('--runtime-commit', required=True)
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    plans = prepare()
    check_release(args.runtime_release, args.runtime_commit)
    for name, _, _, _, remote, rows in plans:
        merge(name, remote, rows, args.runtime_release)
        print(f'Plan {name}: {len(rows)} lessons, {sum(r[3] for r in rows)} coding steps; '
              f'{len(remote["lessons"])} lessons kept in order', flush=True)
    if not args.publish:
        return
    user = gh('user')
    if (user['login'], user['id']) != ('jhs512', 4741844):
        raise ValueError('Unexpected GitHub account')
    for name, repository, _, _, remote, rows in plans:
        for old, new, raw, _ in rows:
            coding.publish_lesson(old, new, raw, 'Replace answer picking with real coding exercises')
        current, latest = read_course(name)[1:]
        if latest != remote:
            raise ValueError(f'The remote course changed during publication; rerun to merge the newer course: {name}')
        body = (json.dumps(merge(name, latest, rows, args.runtime_release), ensure_ascii=False, indent=2) + '\n').encode()
        result = gh(f'repos/{repository}/contents/course.json', 'PUT', dict(
            message=f'Publish {len(rows)} verified coding-conversion lesson revisions', branch='main',
            sha=current['sha'], content=base64.b64encode(body).decode('ascii')))
        readback = base64.b64decode(gh(f'repos/{repository}/contents/course.json?ref={result["commit"]["sha"]}')['content'])
        if readback != body:
            raise ValueError(f'Published course readback differs: {name}')
        print(f'Course {name} commit {result["commit"]["sha"]} sha256 {hashlib.sha256(body).hexdigest()}', flush=True)
        for _, new, raw, _ in rows:
            tagged = base64.b64decode(gh(f'repos/{new["repository"]}/contents/lesson.json?ref={new["revision"]}')['content'])
            if tagged != raw:
                raise ValueError('Lesson tag readback differs: ' + new['repository'])
            print(f'VERIFIED {new["repository"]}@{new["revision"]} {hashlib.sha256(tagged).hexdigest()}', flush=True)


if __name__ == '__main__':
    main()
