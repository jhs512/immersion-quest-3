"""Publish exact reviewed copy edits without changing executable lesson fields."""
import argparse
import base64
import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / '.audit'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'tools' / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def reviewed_payload(original, edits):
    result = copy.deepcopy(original)
    for edit in edits:
        path = edit['path']
        if not path or path[0] not in ('title', 'description', 'objectives', 'chapters', 'tasks', 'learning_strategy'):
            raise ValueError('Unexpected copy field')
        if any(part in path for part in ('solution', 'starter_code', 'example_code', 'tests', 'checker',
                                        'answer', 'accepted', 'value', 'files', 'git_terminal', 'code', 'command', 'expected')):
            raise ValueError('Executable or grading data cannot be edited')
        if path[-1] == 'target' and not (edit['old'].startswith('text:') and edit['new'].startswith('text:')):
            raise ValueError('Only prose highlights can change')
        parent = result
        for part in path[:-1]:
            parent = parent[part]
        if parent[path[-1]] != edit['old']:
            raise ValueError('Reviewed baseline differs')
        parent[path[-1]] = edit['new']
    result['revision'] = original['revision'] + '-spacing-20261103'
    return result


def prepare():
    records = read(ROOT / 'tools/course-copy-edits/spacing-20261103.json')
    groups = {}
    for edit in records['edits']:
        key = Path(edit['file']).name.removesuffix('.lesson.json')
        groups.setdefault(key, []).append(edit)
    builder = load('copy_validation_builder', 'build-redesigned-git.py')
    plans = {}
    for key, edits in sorted(groups.items()):
        old = read(AUDIT / 'live' / (key + '.lesson.json'))
        expected = reviewed_payload(old, edits)
        raw = (ROOT / 'courses/redesigned' / (key + '.json')).read_bytes()
        if json.loads(raw) != expected:
            raise ValueError('Compiled lesson contains changes outside reviewed copy: ' + key)
        for task in expected['tasks']:
            builder.validate_highlights(task)
        plans[key] = {'old': old, 'new': expected, 'raw': raw, 'sha256': hashlib.sha256(raw).hexdigest()}
    return plans, records


def pin(reference):
    return tuple(reference.get(field) for field in ('id', 'revision', 'sha256'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    plans, records = prepare()
    if not args.publish:
        print(json.dumps({'lessons': len(plans), 'reviewed_fields': len(records['edits']),
                          'protected_fields_unchanged': True, 'highlights_valid': True}))
        return
    publisher = load('copy_revision_publisher', 'publish-coding-conversions.py')
    gh = publisher.gh
    account = gh('user')
    if (account['login'], account['id']) != ('jhs512', 4741844):
        raise ValueError('Unexpected publication account')
    coverage = []
    updated = set()
    for slug in ('java-backend', 'engineer-practical', 'aice-associate'):
        baseline = read(AUDIT / 'live' / (slug + '.course.json'))
        endpoint = f'repos/{baseline["repository"]}/contents/course.json'
        initial = gh(endpoint + '?ref=main')
        remote = json.loads(base64.b64decode(initial['content']))
        changes = []
        for reference in remote['lessons']:
            key = reference['repository'].removeprefix('jhs512/mq3-lesson-redesigned-')
            if key not in plans:
                continue
            plan = plans[key]
            before = next(row for row in baseline['lessons'] if row['id'] == reference['id'])
            after = dict(reference, revision=plan['new']['revision'], sha256=plan['sha256'])
            if pin(reference) not in (pin(before), pin(after)):
                raise ValueError('Lesson changed concurrently: ' + key)
            if key not in updated:
                publisher.publish_lesson(before, after, plan['raw'], message='Correct reviewed Korean spacing and exact prose highlights')
                updated.add(key)
            changes.append((reference['id'], before, after))
        latest = gh(endpoint + '?ref=main')
        current = json.loads(base64.b64decode(latest['content']))
        merged = copy.deepcopy(current)
        for identity, before, after in changes:
            row = next(row for row in merged['lessons'] if row['id'] == identity)
            if pin(row) not in (pin(before), pin(after)):
                raise ValueError('Course changed concurrently')
            row.update({field: after[field] for field in ('revision', 'sha256')})
        if merged != current:
            merged.setdefault('change_history', []).insert(0, {
                'at': datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z'),
                'summary': '수업 문장의 띄어쓰기와 해설 강조 구절을 다듬었어요.',
                'reason': '모든 과정의 모든 수업을 점검해 달라는 요청을 반영했어요.',
                'details': ['문제와 해설의 숫자·단어 사이 공백을 보완했어요.',
                            '수업 순서와 문제 고유 코드, 정답·채점·학습 기록은 유지해요.']})
            raw = encode(merged)
            result = gh(endpoint, 'PUT', {'message': 'Publish reviewed all-course Korean spacing corrections',
                        'branch': 'main', 'sha': latest['sha'], 'content': base64.b64encode(raw).decode('ascii')})
            published = base64.b64decode(gh(endpoint + '?ref=' + result['commit']['sha'])['content'])
            if published != raw:
                raise ValueError('Course readback differs')
        else:
            if current != remote:
                raise ValueError('Unchanged course changed during verification')
        assert len(merged['lessons']) == len(current['lessons'])
        coverage.append({'course': slug, 'lessons': len(merged['lessons']), 'updated': len(changes)})
        print(json.dumps(coverage[-1]), flush=True)
    (AUDIT / 'spacing-publication.json').write_bytes(encode({'courses': coverage, 'updated_lessons': len(updated),
        'fields': len(records['edits']), 'tag_readbacks_verified': True, 'course_readbacks_verified': True}))


if __name__ == '__main__':
    main()
