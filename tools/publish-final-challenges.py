"""Publish lesson revisions that only append a final challenge, and designate the challenges in the course.

Plan: docs/plans/2026-10-29-final-challenges-all-courses.md. For every requested lesson:
  - the currently pinned public revision is read back and must hash to its pin;
  - the new lesson must equal the published one except `revision`, one task appended at the end with a new
    step id, and one unit holding only that step appended to the last chapter (no existing step, unit,
    chapter, objective or narration changes);
  - real-runtime evidence for these exact bytes must exist (target/final-challenges/<key>.json);
  - the new immutable tag is created once (never moved) and read back.
The course is then re-read: only the requested lessons' revision, sha256 and challenge_task change, every
other pin and field keeps the remote value, and one change-history entry is added. If the remote course
changed between planning and writing, publication stops.

  python tools/publish-final-challenges.py --course java --lessons java-values ...           # verify only
  python tools/publish-final-challenges.py --course java --lessons java-values ... --publish
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
spec = importlib.util.spec_from_file_location('publisher', ROOT / 'tools/publish-coding-conversions.py')
publisher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)
gh = publisher.gh
SLUG = {'java': 'java-backend', 'aice': 'aice-associate', 'engineer': 'engineer-practical'}
TEXT = {
    'java': dict(summary='모든 수업에 마지막 도전을 더했어요. 도전만 통과해도 수업을 클리어해요.',
                 reason='사용자 요청: 「나머지 24개 수업도 제대로 된 도전과제 만들어서, 모든 수업에서 도전과제만 풀어도 클리어되게 해.」',
                 details=['도전이 없던 수업 {n}개에 배운 원리를 새 조건에 옮기는 마지막 도전 문제를 새 고유 코드로 하나씩 더했어요.',
                          '도전은 앞 문제를 풀지 않아도 자기 시작 상태에서 바로 풀 수 있어요. 통과하면 수업을 클리어하고, 문제 진도는 실제로 푼 만큼만 세요.',
                          '기존 문제의 ID·내용·학습 기록은 바꾸지 않았어요. 이전 버전을 모두 푼 경우 새 도전 한 문제가 추가로 표시돼요.']),
}
for _course, _title in [('aice', 'AICE Associate'), ('engineer', '정보처리기사 실기')]:
    TEXT[_course] = dict(
        summary=f'{_title} 모든 수업에 마지막 도전을 더했어요.',
        reason='사용자 요청으로 백엔드 과정의 도전 클리어 방식을 다른 두 과정에도 적용했어요.',
        details=['수업 {n}개에 앞에서 배운 조건을 함께 적용하는 독립적인 마지막 도전을 새 고유 코드로 더했어요.',
                 '도전만 통과해도 수업을 클리어해요. 문제 진행률은 실제로 통과한 문제만 세요.',
                 '기존 문제와 진도 ID, 예전 버전은 그대로 보존해요.'])


def course_endpoint(course):
    return f'repos/jhs512/mq3-course-redesigned-{SLUG[course]}/contents/course.json'


def read_course(course):
    file = gh(course_endpoint(course))
    return file, json.loads(base64.b64decode(file['content']))


def only_appended(key, before, after):
    """The new lesson is the published one plus exactly one final step in one new unit of the last chapter."""
    old, new = copy.deepcopy(before), copy.deepcopy(after)
    if old['id'] != new['id']:
        raise ValueError(f'{key}: lesson id changed')
    old.pop('revision'); new.pop('revision')
    if len(new['tasks']) != len(old['tasks']) + 1 or new['tasks'][:-1] != old['tasks']:
        raise ValueError(f'{key}: existing steps changed or more than one step was added')
    task = new['tasks'].pop()
    if any(t['id'] == task['id'] for t in old['tasks']) or not task.get('required', True):
        raise ValueError(f'{key}: the challenge must be a new required step')
    last = new['chapters'][-1]['units']
    unit = last.pop()
    if [s['id'] for s in unit['steps']] != [task['id']] or any(u['id'] == unit['id'] for c in old['chapters'] for u in c['units']):
        raise ValueError(f'{key}: the challenge must sit alone in a new unit of the last chapter')
    if new != old:
        raise ValueError(f'{key}: lesson fields outside the appended challenge changed')
    return task


def plan_lessons(course, keys):
    _, remote = read_course(course)
    prepared = json.loads((ROOT / f'courses/redesigned-courses/{SLUG[course]}.json').read_text(encoding='utf-8'))
    rows = []
    for key in keys:
        repo = 'jhs512/mq3-lesson-redesigned-' + key
        old = next(row for row in remote['lessons'] if row['repository'] == repo)
        new = next(row for row in prepared['lessons'] if row['repository'] == repo)
        raw = (ROOT / f'courses/redesigned/{key}.json').read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if digest != new['sha256'] or json.loads(raw)['revision'] != new['revision']:
            raise ValueError(f'{key}: prepared pin does not match the lesson file')
        if (old['revision'], old['sha256'], old.get('challenge_task')) == (new['revision'], new['sha256'], new.get('challenge_task')):
            # Already published: only the entry brief may still follow (see merge).
            print(f'ALREADY {key}@{new["revision"]} pinned and designated', flush=True)
            rows.append((key, None, new, raw))
            continue
        publisher.check_transition(key, old, new)
        before = base64.b64decode(gh(f'repos/{repo}/contents/lesson.json?ref={old["revision"]}')['content'])
        if hashlib.sha256(before).hexdigest() != old['sha256']:
            raise ValueError(f'{key}: the published pin does not match its tag')
        task = only_appended(key, json.loads(before), json.loads(raw))
        if new.get('challenge_task') != task['id']:
            raise ValueError(f'{key}: the prepared designation is not the appended step')
        evidence = json.loads((ROOT / f'target/final-challenges/{key}.json').read_text(encoding='utf-8'))
        if evidence.get('passed') is not True or evidence.get('lesson_sha256') != digest:
            raise ValueError(f'{key}: current real-runtime evidence is required')
        tag = gh(f'repos/{repo}/git/ref/tags/{new["revision"]}', optional=True)
        if tag is not None and base64.b64decode(gh(f'repos/{repo}/contents/lesson.json?ref={new["revision"]}')['content']) != raw:
            raise ValueError(f'{key}: tag {new["revision"]} already exists with other bytes')
        print(f'VERIFIED {key} {old["revision"]} -> {new["revision"]}: +{task["id"]} 「{task["title"]}」, evidence {digest[:12]}', flush=True)
        rows.append((key, old, new, raw))
    return remote, prepared, rows


def merge(remote, prepared, rows, course):
    merged = copy.deepcopy(remote)
    changed = {new['repository']: new for _, _, new, _ in rows}
    prepared_rows = {row['repository']: row for row in prepared['lessons']}
    for row in merged['lessons']:
        new = changed.get(row['repository'])
        if new is None:
            mine = prepared_rows.get(row['repository'])
            if mine is None:
                raise ValueError(f'Remote lesson missing from the prepared course: {row["repository"]}')
            if (mine['revision'], mine['sha256'], mine.get('challenge_task', '')) != (row['revision'], row['sha256'], row.get('challenge_task', '')):
                # A prepared but unrequested revision stays unpublished: the remote pin is kept as it is.
                print(f'KEPT remote pin {row["repository"]}@{row["revision"]} (prepared {mine["revision"]} not requested)', flush=True)
            continue
        row.update(revision=new['revision'], sha256=new['sha256'], challenge_task=new['challenge_task'])
        # The entry brief names the final challenge: only its `challenge` sentence follows the new step.
        brief = prepared.get('lesson_previews', {}).get(row['id'])
        if brief and row['id'] in merged.get('lesson_previews', {}):
            merged['lesson_previews'][row['id']]['challenge'] = brief['challenge']
    text = TEXT[course]
    if not any(entry.get('summary') == text['summary'] for entry in merged.get('change_history', [])):
        merged.setdefault('change_history', []).insert(0, dict(
            at=datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z'), summary=text['summary'],
            reason=text['reason'], details=[d.format(n=len(rows)) for d in text['details']]))
    strip = lambda row: {k: v for k, v in row.items() if k not in ('revision', 'sha256', 'challenge_task')}
    if [strip(r) for r in merged['lessons']] != [strip(r) for r in remote['lessons']]:
        raise ValueError('Lesson order or other pinned fields would change')
    ids = {new['id'] for _, _, new, _ in rows}
    for lesson_id, brief in remote.get('lesson_previews', {}).items():
        after = merged['lesson_previews'][lesson_id]
        if {k: v for k, v in after.items() if k != 'challenge'} != {k: v for k, v in brief.items() if k != 'challenge'} or (lesson_id not in ids and after != brief):
            raise ValueError(f'Entry brief would change beyond the challenge sentence: {lesson_id}')
    for field in set(remote) - {'lessons', 'change_history', 'lesson_previews'}:
        if merged[field] != remote[field]:
            raise ValueError(f'Course field would change: {field}')
    return merged


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--course', choices=sorted(SLUG), required=True)
    parser.add_argument('--lessons', nargs='+', required=True)
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    remote, prepared, rows = plan_lessons(args.course, args.lessons)
    plan = merge(remote, prepared, rows, args.course)
    designated = sum(1 for row in plan['lessons'] if row.get('challenge_task'))
    print(f'Plan: {len(rows)} lesson revisions; designations {sum(1 for r in remote["lessons"] if r.get("challenge_task"))} -> {designated} of {len(plan["lessons"])}', flush=True)
    if not args.publish:
        return
    user = gh('user')
    if (user['login'], user['id']) != ('jhs512', 4741844):
        raise ValueError('Unexpected publishing account')
    for key, old, new, raw in rows:
        if old is not None:
            publisher.publish_lesson(old, new, raw, 'Add the final challenge step')
    if plan == remote:
        print('Course already up to date', flush=True)
        return
    current, latest = read_course(args.course)
    if latest != remote:
        raise ValueError('The remote course changed during publication; rerun to merge the newer course')
    body = (json.dumps(plan, ensure_ascii=False, indent=2) + '\n').encode()
    result = gh(course_endpoint(args.course), 'PUT', dict(message='Designate final challenges: ' + ', '.join(r[0] for r in rows),
                                                           branch='main', sha=current['sha'], content=base64.b64encode(body).decode('ascii')))
    readback = base64.b64decode(gh(course_endpoint(args.course) + '?ref=' + result['commit']['sha'])['content'])
    if readback != body:
        raise ValueError('Published course readback differs')
    print(f'Course commit {result["commit"]["sha"]} sha256 {hashlib.sha256(body).hexdigest()}', flush=True)
    for key, old, new, raw in rows:
        tagged = base64.b64decode(gh(f'repos/{new["repository"]}/contents/lesson.json?ref={new["revision"]}')['content'])
        main = base64.b64decode(gh(f'repos/{new["repository"]}/contents/lesson.json?ref=main')['content'])
        if tagged != raw or main != raw:
            raise ValueError('Lesson readback differs: ' + key)
        print(f'READBACK {key}@{new["revision"]} tag=main=local {hashlib.sha256(tagged).hexdigest()}', flush=True)


if __name__ == '__main__':
    main()
