"""Build the three independent course manifests from approved lesson sources.

This prepares files locally; publication and default registration are separate.
Existing course repositories and their progress issues are never rewritten here.
"""
import argparse
import hashlib
import json
from pathlib import Path

from lesson_prd import content_hash, validate

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


def build(check=False):
    catalog = json.loads((ROOT / 'tools/redesigned_courses/catalog.json').read_text(encoding='utf-8'))
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
            if lesson['id'] != item['id'] or lesson['id'] != prd['id']:
                raise ValueError(f'Lesson identity differs: {lesson_key}')
            if lesson['id'] in all_lessons:
                raise ValueError('These three independent courses must not share lessons')
            all_lessons.add(lesson['id'])
            digest = hashlib.sha256(raw).hexdigest()
            references.append(dict(id=lesson['id'], title=lesson['title'],
                repository=f'jhs512/mq3-lesson-redesigned-{lesson_key}',
                revision=lesson['revision'], sha256=digest, prerequisites=[],
                required=True, review_enabled=lesson['review_enabled']))
            lesson_specs.append(dict(key=lesson_key, id=lesson['id'], title=lesson['title'],
                objectives=lesson['objectives'], approved_prd_sha256=content_hash(prd),
                lesson_sha256=digest, chapters=len(lesson['chapters']),
                units=sum(len(c['units']) for c in lesson['chapters']), steps=len(lesson['tasks'])))
        manifest = dict(schema_version=2, id=course['id'], title=course['title'],
            description=' '.join(course['objectives']),
            repository=f'jhs512/mq3-course-redesigned-{slug}', lessons=references,
            change_history=[dict(at='2026-10-19T00:00:00Z',
                summary='새 지침에 맞춘 독립 과정을 구성했어요.',
                reason='작은 문제를 풀며 원리를 이해하도록 다시 구성했어요.',
                details=[f'{len(references)}수업을 챕터·단원·스텝으로 구성했어요.',
                    '이전 과정과 학습 기록은 별도 저장소에 그대로 남아요.',
                    '모든 수업은 추천 순서와 관계없이 자유롭게 열 수 있어요.'])])
        write(ROOT / 'courses/redesigned-courses' / f'{slug}.json', encoded(manifest), check)
        spec = dict(schema_version=1, id=course['id'], title=course['title'],
            objectives=course['objectives'], policy_snapshot=course['policy_snapshot'],
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
