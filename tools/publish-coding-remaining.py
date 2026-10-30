"""Publish the remaining coding conversions of 2026-10-30 (Codex-relayed user request), one course at a time.

Same guarantees as tools/publish-coding-trace-reset.py, against the courses that build 156 published:
  - Only the listed lesson rows change: `revision`, `sha256`, and `challenge_task` when that lesson's final
    challenge was itself converted (it may only move from the old step code to its new step code).
    Order, prerequisites, categories, tracks, previews and every other lesson stay as the remote has them.
  - The remote pin of every listed lesson must still be the revision origin/main's catalog names (the
    build 156 publication), or already the new one; otherwise the run stops instead of rolling back.
  - Every lesson needs passing validator evidence for its exact bytes (target/mcq/<key>.json), and every
    converted step must be a coding step under its new code with the old code gone.
  - A moved challenge also renames that lesson's `lesson_previews[...].challenge` to the new step title
    (the only preview field allowed to change).
  - Lesson tags are immutable; the course write is a compare-and-swap on the course.json blob sha, then
    every written byte is read back.
Lesson content only: these lessons use features build 156 already runs (prepared Python checks with
probes, SQL and C/Java value variations), so no desktop build is needed. The run still checks that the
public build 156 release with both installers contains its runtime commit.

    python tools/publish-coding-remaining.py engineer-practical [--publish]
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


trace = load('trace_publisher', 'publish-coding-trace-reset.py')
coding, conversion, gh = trace.coding, trace.conversion, trace.gh
PREFIX = trace.PREFIX
RELEASE, RUNTIME = 'v0.1.0-build.156', '846504afb5d1f52e1231bf5d3df89cb366cd4f3d'
# The catalog whose pins build 156's course publication wrote.
BASELINE = RUNTIME
LESSONS = {
    'engineer-practical': ['engineer-c-start', 'engineer-c-structures', 'engineer-java-flow', 'engineer-java-references',
                           'engineer-java-static', 'engineer-java-polymorphism', 'engineer-python-values',
                           'engineer-python-calls', 'engineer-mixed', 'engineer-os', 'engineer-network'],
    'aice-associate': ['aice-python-start', 'aice-python-conditions', 'aice-split', 'aice-leakage', 'aice-classification',
                       'aice-classification-metrics', 'aice-models', 'aice-tuning', 'aice-boosting', 'aice-tensorflow',
                       'aice-neural-regression', 'aice-neural-classification', 'aice-training', 'aice-integration'],
}
SUMMARY = {
    'engineer-practical': '코드를 읽고 출력값만 적던 문제도 직접 코드를 고쳐 실행하는 문제로 바꿨어요.',
    'aice-associate': '남은 AICE 수업의 고르던 문제를 직접 코드를 고쳐 실행하는 문제로 바꿨어요.',
}
DETAILS = {
    'engineer-practical': ['C·Java·Python 수업과 복합 문제·운영체제·네트워크 도전에서 코드를 읽고 출력값을 적던 46문제를 직접 코드를 고쳐 실행하고 제출하는 문제로 바꿨어요. 채점은 실제 실행 결과와 바꾼 준비 값·표로 해요.',
                           '코드 없이 손으로 계산하거나 용어를 적는 문제와 설계·테스트·보안 같은 개념 문제는 그대로예요.',
                           '운영체제·네트워크·복합·다형성 수업의 마지막 도전은 바뀐 문제로 지정했어요.',
                           '본질이 바뀐 문제는 새 문제로 열려요. 이전 문제의 완료 기록은 이전 버전에 남아요.'],
    'aice-associate': ['파이썬 기초·데이터 나누기·누수·분류·평가 지표·모델·튜닝·부스팅·신경망·학습·종합 수업에서 보기를 고르던 89문제를 직접 코드를 고쳐 실행하고 제출하는 문제로 바꿨어요.',
                       '채점은 실제 파이썬·scikit-learn·TensorFlow 실행 결과로 해요. 다른 준비 자료로도 다시 실행해 결과를 글자로 적은 답은 통과하지 못해요.',
                       '결과를 해석하거나 판단하는 문제는 그대로예요.',
                       '본질이 바뀐 문제는 새 문제로 열려요. 이전 문제의 완료 기록은 이전 버전에 남아요.'],
}
REASON = ('사용자 요청: 「객관식에서 순수 코딩 문제로」 바꾸고, 2026-10-30 확인에 따라 코드를 읽고 출력값만 적는 빈칸도 '
          '직접 코드를 작성·수정·실행하는 문제로 바꿔요. 실제 개념·이론 문제는 그대로 둬요.')
UPDATED = ('revision', 'sha256', 'challenge_task')


def baseline_revisions():
    catalog = json.loads(subprocess.check_output(['git', 'show', f'{BASELINE}:tools/redesigned_courses/catalog.json'], cwd=ROOT))
    return {item['key']: item['revision'] for course in catalog['courses'] for item in course['lessons']}


def prepare(name):
    keys = LESSONS[name]
    if not keys:
        raise ValueError(f'No verified lessons listed for {name}')
    subprocess.run([sys.executable, str(ROOT / 'tools/build-redesigned-course-bundle.py'), '--check'], cwd=ROOT / 'tools', check=True)
    base = baseline_revisions()
    prepared = json.loads((ROOT / 'courses/redesigned-courses' / f'{name}.json').read_text(encoding='utf-8'))
    repository, file, remote = trace.read_course(name)
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
        moved = {spec['old']: conversion.new_step_id(spec['old']) for spec in conversion.specs_for(key).SPECS}
        if old.get('challenge_task') != new.get('challenge_task') and moved.get(old.get('challenge_task')) != new.get('challenge_task'):
            raise ValueError(f'Challenge designation would change beyond the converted step: {key}')
        if new.get('challenge_task') and new['challenge_task'] not in {task['id'] for task in lesson['tasks']}:
            raise ValueError(f'Challenge step is missing from the lesson: {key}')
        if old.get('challenge_task') != new.get('challenge_task'):
            # The course preview names the final challenge by title; it follows the moved designation.
            title = next(task['title'] for task in lesson['tasks'] if task['id'] == new['challenge_task'])
            if prepared['lesson_previews'][old['id']]['challenge'] != title:
                raise ValueError(f'Prepared preview does not name the new challenge: {key}')
            CHALLENGE_TITLES[old['id']] = title
        tag = gh(f'repos/{new["repository"]}/git/ref/tags/{new["revision"]}', optional=True)
        if tag is not None:
            tagged = base64.b64decode(gh(f'repos/{new["repository"]}/contents/lesson.json?ref={new["revision"]}')['content'])
            if tagged != raw:
                raise ValueError(f'Tag {new["revision"]} already exists with other bytes: {key}')
        steps = trace.converted_steps(key, lesson)
        before = sum(1 for s in conversion.specs_for(key).SPECS if s['old'] not in old_ids(old))
        print(f'Prepared {key}: {old["revision"]} -> {new["revision"]} {digest[:12]}, {steps - before} newly converted '
              f'({steps} converted in total; {proof["rejected_answers"]} rejected / {proof["accepted_answers"]} accepted answers)'
              + (f', challenge {old.get("challenge_task")} -> {new.get("challenge_task")}' if old.get('challenge_task') != new.get('challenge_task') else ''),
              flush=True)
        rows.append((old, new, raw, steps - before))
    return repository, remote, rows


_published = {}
# Lesson id -> new challenge title, for lessons whose final challenge was itself converted.
CHALLENGE_TITLES = {}


def old_ids(old):
    """Step codes of the currently published revision of a lesson (to count only this round's conversions)."""
    if old['repository'] not in _published:
        lesson = json.loads(base64.b64decode(gh(f'repos/{old["repository"]}/contents/lesson.json?ref={old["revision"]}')['content']))
        if not lesson.get('tasks'):
            raise ValueError('Published lesson without tasks: ' + old['repository'])
        _published[old['repository']] = {task['id'] for task in lesson['tasks']}
    # A spec already converted in an earlier round no longer has its old code in the published lesson.
    return _published[old['repository']]


def merge(name, remote, rows, at=None):
    merged = copy.deepcopy(remote)
    changed = {new['repository']: new for _, new, _, _ in rows}
    for row in merged['lessons']:
        if row['repository'] in changed:
            for field in UPDATED:
                if field in changed[row['repository']]:
                    row[field] = changed[row['repository']][field]
    if not any(change.get('summary') == SUMMARY[name] for change in merged.get('change_history', [])):
        merged.setdefault('change_history', []).insert(0, dict(
            at=at or datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z'),
            summary=SUMMARY[name], reason=REASON, details=DETAILS[name]))
    for lesson_id, title in CHALLENGE_TITLES.items():
        merged['lesson_previews'][lesson_id]['challenge'] = title
    if [row['repository'] for row in merged['lessons']] != [row['repository'] for row in remote['lessons']]:
        raise ValueError('Lessons would be reordered')
    strip = lambda row: {k: v for k, v in row.items() if k not in UPDATED}
    for row, before in zip(merged['lessons'], remote['lessons']):
        if strip(row) != strip(before) or (row['repository'] not in changed and row != before):
            raise ValueError(f'A lesson field outside the scope would change: {row["repository"]}')
    for lesson_id, preview in remote.get('lesson_previews', {}).items():
        allowed = {'challenge'} if lesson_id in CHALLENGE_TITLES else set()
        after = merged['lesson_previews'][lesson_id]
        if set(after) != set(preview) or any(after[k] != v for k, v in preview.items() if k not in allowed):
            raise ValueError(f'A lesson preview outside the moved challenge would change: {lesson_id}')
    if set(merged.get('lesson_previews', {})) != set(remote.get('lesson_previews', {})):
        raise ValueError('Lesson previews would be added or removed')
    for field in set(remote) | set(merged):
        if field not in ('lessons', 'change_history', 'lesson_previews') and merged.get(field) != remote.get(field):
            raise ValueError(f'Course field would change: {field}')
    return merged


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('course', choices=sorted(LESSONS))
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    repository, remote, rows = prepare(args.course)
    trace.check_release(RELEASE, RUNTIME)
    merge(args.course, remote, rows)
    print(f'Plan {args.course}: {len(rows)} lessons, {sum(r[3] for r in rows)} newly converted steps; '
          f'{len(remote["lessons"])} lessons kept in order', flush=True)
    if not args.publish:
        return
    user = gh('user')
    if (user['login'], user['id']) != ('jhs512', 4741844):
        raise ValueError('Unexpected GitHub account')
    for old, new, raw, _ in rows:
        coding.publish_lesson(old, new, raw, 'Turn code-reading answers into real coding exercises')
    current, latest = trace.read_course(args.course)[1:]
    if latest != remote:
        raise ValueError(f'The remote course changed during publication; rerun to merge the newer course: {args.course}')
    body = (json.dumps(merge(args.course, latest, rows), ensure_ascii=False, indent=2) + '\n').encode()
    result = gh(f'repos/{repository}/contents/course.json', 'PUT', dict(
        message=f'Publish {len(rows)} verified coding-conversion lesson revisions', branch='main',
        sha=current['sha'], content=base64.b64encode(body).decode('ascii')))
    readback = base64.b64decode(gh(f'repos/{repository}/contents/course.json?ref={result["commit"]["sha"]}')['content'])
    if readback != body:
        raise ValueError(f'Published course readback differs: {args.course}')
    print(f'Course {args.course} commit {result["commit"]["sha"]} sha256 {hashlib.sha256(body).hexdigest()}', flush=True)
    for _, new, raw, _ in rows:
        tagged = base64.b64decode(gh(f'repos/{new["repository"]}/contents/lesson.json?ref={new["revision"]}')['content'])
        if tagged != raw:
            raise ValueError('Lesson tag readback differs: ' + new['repository'])
        print(f'VERIFIED {new["repository"]}@{new["revision"]} {hashlib.sha256(tagged).hexdigest()}', flush=True)


if __name__ == '__main__':
    main()
