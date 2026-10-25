"""Build the three independent course manifests from approved lesson sources.

This prepares files locally; publication and default registration are separate.
Existing course repositories and their progress issues are never rewritten here.
"""
import argparse
import hashlib
import json
from pathlib import Path

from lesson_prd import content_hash, validate
from lesson_registry import load_registry

ROOT = Path(__file__).resolve().parents[1]
NAMES = {'java': 'java-backend', 'aice': 'aice-associate', 'engineer': 'engineer-practical'}


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def write(path, raw, check):
    if check:
        if not path.exists() or path.read_bytes() != raw:
            raise ValueError(f'Stale course bundle: {path.relative_to(ROOT)}')
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists() or path.read_bytes() != raw:
            path.write_bytes(raw)


CLASSIFICATION = ROOT / 'tools/redesigned_courses/lesson-classification.json'
TRACKS = ('basic', 'essential', 'advanced')


def classification(catalog, path=CLASSIFICATION):
    """Approved category/track per lesson key, plus each course's categories in order.

    The source keeps reviewable proposals (status "proposed", with evidence). Only "approved" entries reach
    a manifest; a lesson without one stays 미분류 in the app. Classification is manifest metadata: it never
    changes lesson bytes or revisions, so progress is untouched."""
    if not path.exists():
        return {}
    source = json.loads(path.read_text(encoding='utf-8'))
    courses = {course['key']: [lesson['key'] for lesson in course['lessons']] for course in catalog['courses']}
    result = {}
    for key, entry in source.get('courses', {}).items():
        if key not in courses:
            raise ValueError(f'Classification for an unknown course: {key}')
        ids = [c['id'] for c in entry.get('categories', [])]
        if len(ids) != len(set(ids)) or any(not c.get('id') or not str(c.get('title', '')).strip() for c in entry.get('categories', [])):
            raise ValueError(f'{key}: category ids must be unique and every category needs a title')
        approved = {}
        for lesson_key, item in entry.get('lessons', {}).items():
            if lesson_key not in courses[key]:
                raise ValueError(f'{key}: classification for an unregistered lesson: {lesson_key}')
            if item.get('status') not in ('proposed', 'approved'):
                raise ValueError(f'{key}/{lesson_key}: status must be proposed or approved')
            if item.get('category') is not None and item['category'] not in ids:
                raise ValueError(f'{key}/{lesson_key}: unknown category {item["category"]}')
            if item.get('track') is not None and item['track'] not in TRACKS:
                raise ValueError(f'{key}/{lesson_key}: track must be one of {TRACKS} or null')
            if item['status'] == 'approved':
                if not item.get('decided_by') or not item.get('decided_on'):
                    raise ValueError(f'{key}/{lesson_key}: an approved classification records who decided and when')
                if item.get('category') is None and item.get('track') is None:
                    raise ValueError(f'{key}/{lesson_key}: nothing to approve')
                approved[lesson_key] = {k: item[k] for k in ('category', 'track') if item.get(k) is not None}
        # A user decision can approve a track for many lessons at once without approving any proposed category.
        for decision in source.get('track_decisions', []):
            if decision.get('track') not in TRACKS or decision.get('status') not in ('proposed', 'approved'):
                raise ValueError('track decision: unknown track or status')
            if decision['status'] != 'approved':
                continue
            for field in ('decided_by', 'decided_on', 'quote'):
                if not str(decision.get(field, '')).strip():
                    raise ValueError(f'track decision: an approved decision records {field}')
            for lesson_key in decision.get('lessons', {}).get(key, []):
                if lesson_key not in courses[key]:
                    raise ValueError(f'{key}: track decision for an unregistered lesson: {lesson_key}')
                approved.setdefault(lesson_key, {})['track'] = decision['track']
        used = {a['category'] for a in approved.values() if 'category' in a}
        result[key] = {'categories': [dict(id=c['id'], title=c['title']) for c in entry.get('categories', []) if c['id'] in used],
                       'lessons': approved}
    return result


def build(check=False):
    catalog = json.loads((ROOT / 'tools/redesigned_courses/catalog.json').read_text(encoding='utf-8'))
    load_registry(catalog)
    classes = classification(catalog)
    release = json.loads((ROOT / 'tools/redesigned_courses/release.json').read_text(encoding='utf-8'))
    all_lessons = set()
    for course in catalog['courses']:
        key = course['key']
        slug = NAMES[key]
        references, lesson_specs = [], []
        for item in course['lessons']:
            lesson_key = item['key']
            source = ROOT / item['authoring_prd']
            prd = json.loads(source.read_text(encoding='utf-8'))
            validate(prd, require_approval=True)
            raw = (ROOT / 'courses/redesigned' / f'{lesson_key}.json').read_bytes()
            lesson = json.loads(raw)
            if lesson['revision'] != item['revision']:
                raise ValueError(f'Lesson revision differs from registration: {lesson_key}')
            if lesson['id'] != item['id'] or lesson['id'] != prd['id']:
                raise ValueError(f'Lesson identity differs: {lesson_key}')
            if lesson['id'] in all_lessons:
                raise ValueError('These three independent courses must not share lessons')
            all_lessons.add(lesson['id'])
            digest = hashlib.sha256(raw).hexdigest()
            references.append(dict(id=lesson['id'], title=lesson['title'],
                repository=f'jhs512/mq3-lesson-redesigned-{lesson_key}',
                revision=lesson['revision'], sha256=digest, prerequisites=[],
                required=item.get('required', True), review_enabled=lesson['review_enabled'],
                **classes.get(key, {}).get('lessons', {}).get(lesson_key, {})))
            lesson_specs.append(dict(key=lesson_key, id=lesson['id'], title=lesson['title'],
                objectives=lesson['objectives'], approved_prd_sha256=content_hash(prd),
                lesson_sha256=digest, chapters=len(lesson['chapters']),
                units=sum(len(c['units']) for c in lesson['chapters']), steps=len(lesson['tasks'])))
        manifest = dict(schema_version=2, id=course['id'], title=course['title'],
            description=course['presentation']['description'],
            objectives=course['presentation']['objectives'], scope_note=course['presentation']['scope_note'],
            repository=f'jhs512/mq3-course-redesigned-{slug}', lessons=references,
            change_history=release.get('course_changes', {}).get(key, []) + [dict(at=release['prepared_at'],
                summary='새 지침에 맞춘 독립 과정을 구성했어요.',
                reason='작은 문제를 풀며 원리를 이해하도록 다시 구성했어요.',
                details=[f'{sum(1 for item in course["lessons"] if not item.get("added_on"))}수업을 챕터·단원·스텝으로 구성했어요.',
                    '이전 과정과 학습 기록은 별도 저장소에 그대로 남아요.',
                    '모든 수업은 추천 순서와 관계없이 자유롭게 열 수 있어요.'])])
        if classes.get(key, {}).get('categories'):
            manifest['categories'] = classes[key]['categories']
        if key == 'java':
            from redesigned_courses.backend_previews import for_course
            manifest['lesson_previews'] = for_course(course['lessons'])
        write(ROOT / 'courses/redesigned-courses' / f'{slug}.json', encoded(manifest), check)
        spec = dict(schema_version=1, id=course['id'], title=course['title'],
            objectives=course['objectives'], presentation=course['presentation'], policy_snapshot=course['policy_snapshot'],
            scope_boundary=course['scope_boundary'], research_snapshot=course['research_snapshot'],
            lessons=lesson_specs, completion_gate=course['completion_gate'],
            transition=dict(previous_repository=f'jhs512/mq3-course-{slug}',
                new_repository=manifest['repository'],
                progress='이전 기록을 지우거나 새 문제의 완료로 복사하지 않아요.',
                access='이전 저장소는 코스 추가에서 다시 열 수 있어요.'),
            approval=dict(mode='delegated_scope',
                authority='2026-10-19 사용자의 세 과정 전체 재설계·구현 지시',
                evidence='.scratch/player-content-redesign/authorization-2026-10-19.md'))
        spec['approval']['content_sha256'] = hashlib.sha256(encoded(spec)).hexdigest()
        write(ROOT / 'tools/redesigned_courses' / key / 'course-prd.json', encoded(spec), check)
        print(f'{slug}: {len(references)} lessons / {sum(x["steps"] for x in lesson_specs)} steps')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    build(parser.parse_args().check)
