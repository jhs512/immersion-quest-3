"""Course → lesson → step inventory for the course audit (.scratch/course-visualizer-audit/).

Reads the bundled course manifests (src/bundled_courses.rs) and every lesson file, and checks that each
manifest reference resolves to a lesson whose sha256 and revision match. Per step it records the facts
the audit judges from: language, interaction, the effective 코드 흐름 보기 state per OS (mirrors
Task::code_flow_availability in src/repository_course.rs), the narration's code_flow actions and whether
the narration has a try/caution moment.

  python tools/course_audit/inventory.py            # write inventory.json and inventory.md
  python tools/course_audit/inventory.py --check    # fail when a manifest reference does not resolve
"""
import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COURSES = ['java-backend', 'engineer-practical', 'aice-associate']
OUT = ROOT / '.scratch/course-visualizer-audit'
TRACED_EVERYWHERE = {'java', 'python'}
TRACED_ON = {'c': {'windows', 'macos'}}
RUNNABLE_EXAMPLE = {'java', 'python', 'c', 'javascript', 'sql'}


def has_runnable_example(task):
    source = task.get('example_code') or ''
    return bool(task.get('interaction')) and not task.get('git_terminal') and task.get('language') in RUNNABLE_EXAMPLE \
        and bool(source.strip()) and len(source) <= 65536


def availability(task, os_name):
    """The button the player shows: hidden, ready, or unsupported (shown with a reason)."""
    if task.get('code_flow') is False or task.get('git_terminal') or (task.get('interaction') and not has_runnable_example(task)):
        return 'hidden'
    language = task.get('language')
    if language in TRACED_EVERYWHERE or os_name in TRACED_ON.get(language, ()):
        return 'ready'
    return 'unsupported'


def narration_facts(task):
    actions = task.get('narration', [])
    says = ' '.join(str(a.get('say') or a.get('text') or '') for a in actions)
    return {
        'actions': len(actions),
        'runs': sum(a.get('action') == 'run' for a in actions),
        'code_flow': sum(a.get('action') == 'code_flow' and not a.get('close') for a in actions),
        'caution': '조심하세요' in says,
        'expect_error': any(a.get('expect_error') for a in actions),
    }


def lesson_inventory(path):
    raw = path.read_bytes()
    lesson = json.loads(raw)
    tasks = {task['id']: task for task in lesson['tasks']}
    key = path.stem
    folder = ROOT / 'tools/redesigned_lessons' / key.replace('-', '_')
    steps = []
    for c, chapter in enumerate(lesson.get('chapters', []), 1):
        for u, unit in enumerate(chapter.get('units', []), 1):
            for s, step in enumerate(unit.get('steps', []), 1):
                task = tasks.get(step['id'], {})
                interaction = task.get('interaction') or {}
                steps.append({
                    'position': f'{c}.{u}.{s}', 'id': step['id'], 'title': task.get('title', ''),
                    'chapter': chapter.get('title', ''), 'unit': unit.get('title', ''),
                    'objectives': step.get('objectives', []), 'language': task.get('language'),
                    'interaction': interaction.get('kind'), 'git_terminal': bool(task.get('git_terminal')),
                    'required': task.get('required', True), 'explicit_code_flow': task.get('code_flow'),
                    'code_flow': {os_name: availability(task, os_name) for os_name in ('windows', 'macos', 'linux')},
                    'narration': narration_facts(task), 'has_task': bool(task),
                })
    return {
        'key': key, 'id': lesson['id'], 'revision': lesson.get('revision'), 'title': lesson.get('title'),
        'sha256': hashlib.sha256(raw).hexdigest(), 'objectives': lesson.get('objectives', []),
        'chapters': len(lesson.get('chapters', [])), 'tasks': len(tasks), 'steps': steps,
        'prd': (folder / 'approved-prd.json').is_file(), 'content': (folder / 'content.json').is_file(),
        'cases': (ROOT / 'tests/lesson-cases' / f'{key}.json').is_file(),
        'orphan_tasks': sorted(set(tasks) - {step['id'] for step in steps}),
    }


def build():
    lessons = {}
    for path in sorted((ROOT / 'courses/redesigned').glob('*.json')):
        item = lesson_inventory(path)
        lessons[item['id']] = item
    courses, problems = [], []
    for name in COURSES:
        manifest = json.loads((ROOT / 'courses/redesigned-courses' / f'{name}.json').read_text(encoding='utf-8'))
        refs = []
        for order, ref in enumerate(manifest['lessons'], 1):
            lesson = lessons.get(ref['id'])
            state = 'ok'
            if lesson is None:
                state = 'missing lesson file'
            elif lesson['sha256'] != ref.get('sha256'):
                state = 'sha256 differs'
            elif lesson['revision'] != ref.get('revision'):
                state = 'revision differs'
            if state != 'ok':
                problems.append(f"{name} #{order} {ref.get('repository')}: {state}")
            known = [p for p in ref.get('prerequisites', []) if p in {r['id'] for r in manifest['lessons'][:order - 1]}]
            refs.append({'order': order, 'id': ref['id'], 'key': lesson['key'] if lesson else None,
                         'revision': ref.get('revision'), 'required': ref.get('required', True),
                         'category': ref.get('category'), 'track': ref.get('track'),
                         'prerequisites': [lessons[p]['key'] if p in lessons else p for p in ref.get('prerequisites', [])],
                         'prerequisites_after_lesson': [lessons[p]['key'] if p in lessons else p
                                                        for p in ref.get('prerequisites', []) if p not in known],
                         'state': state})
        courses.append({'key': name, 'id': manifest['id'], 'title': manifest['title'], 'lessons': refs})
    used = {ref['id'] for course in courses for ref in course['lessons']}
    unreferenced = sorted(item['key'] for item in lessons.values() if item['id'] not in used)
    return {'courses': courses, 'lessons': sorted(lessons.values(), key=lambda l: l['key']),
            'unreferenced_lessons': unreferenced, 'problems': problems}


def markdown(data):
    lessons = {item['key']: item for item in data['lessons']}
    steps = [step for item in data['lessons'] for step in item['steps']]
    lines = ['# 코스·수업·스텝 inventory', '',
             '`python tools/course_audit/inventory.py`가 만든다. 손으로 고치지 않는다.', '',
             f"- 고유 수업 파일 {len(data['lessons'])}개, 스텝 {len(steps)}개.",
             f"- 코스 참조 {sum(len(c['lessons']) for c in data['courses'])}개. 어느 코스에도 없는 수업: "
             + (', '.join(data['unreferenced_lessons']) or '없음') + '.',
             f"- manifest 대조 문제: {len(data['problems'])}건." + ''.join(f'\n  - {p}' for p in data['problems']), '']
    lines += ['## 코드 흐름 보기 상태(스텝 수)', '', '| 언어 | 스텝 | Windows ready | macOS ready | Linux ready | 숨김 | 해설 code_flow |',
              '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    by_language = {}
    for step in steps:
        by_language.setdefault(step['language'], []).append(step)
    for language, group in sorted(by_language.items(), key=lambda kv: -len(kv[1])):
        ready = Counter(os_name for step in group for os_name, state in step['code_flow'].items() if state == 'ready')
        hidden = sum(step['code_flow']['windows'] == 'hidden' for step in group)
        flows = sum(step['narration']['code_flow'] > 0 for step in group)
        lines.append(f"| {language} | {len(group)} | {ready['windows']} | {ready['macos']} | {ready['linux']} | {hidden} | {flows} |")
    for course in data['courses']:
        lines += ['', f"## {course['title']} (`{course['key']}`)", '',
                  '| # | 수업 | revision | 스텝 | 언어 | ready(Win/Mac) | 해설 code_flow | caution 스텝 | PRD | cases | 선수 |',
                  '| ---: | --- | --- | ---: | --- | --- | ---: | ---: | --- | --- | --- |']
        for ref in course['lessons']:
            item = lessons.get(ref['key'])
            if not item:
                lines.append(f"| {ref['order']} | (없음) | {ref['revision']} | | | | | | | | {ref['state']} |")
                continue
            group = item['steps']
            languages = '/'.join(f'{k}:{v}' for k, v in Counter(s['language'] for s in group).most_common())
            win = sum(s['code_flow']['windows'] == 'ready' for s in group)
            mac = sum(s['code_flow']['macos'] == 'ready' for s in group)
            prereq = ', '.join(ref['prerequisites']) or '없음'
            if ref['prerequisites_after_lesson']:
                prereq += ' (뒤에 오는 선수: ' + ', '.join(ref['prerequisites_after_lesson']) + ')'
            lines.append(f"| {ref['order']} | `{item['key']}` {item['title']} | {item['revision']} | {len(group)} | {languages} | "
                         f"{win}/{mac} | {sum(s['narration']['code_flow'] > 0 for s in group)} | "
                         f"{sum(s['narration']['caution'] for s in group)} | {'O' if item['prd'] else 'X'} | "
                         f"{'O' if item['cases'] else 'X'} | {prereq} |")
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    data = build()
    if args.check:
        for problem in data['problems']:
            print(problem)
        sys.exit(1 if data['problems'] else 0)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'inventory.json').write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    (OUT / 'inventory.md').write_text(markdown(data), encoding='utf-8')
    print(f"{len(data['lessons'])} lessons, {sum(len(l['steps']) for l in data['lessons'])} steps, "
          f"{len(data['problems'])} manifest problems, unreferenced: {data['unreferenced_lessons']}")


if __name__ == '__main__':
    main()
