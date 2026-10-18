"""Compile approved practice lessons; retain unchanged narration caches."""
import argparse
import copy
import hashlib
import json
from pathlib import Path

from lesson_prd import content_hash, validate
from redesigned_lessons.python_prepared_checks import checker as python_prepared_checker
from redesigned_lessons.pandas_head_checks import checker as pandas_head_checker

ROOT = Path(__file__).resolve().parents[1]
LESSONS = {'git-first': ('git_first', 'git-first-1', 'k'), 'git-branch': ('git_branch', 'git-branch-1', 'l'), 'java-values': ('java_values', 'java-values-1', 'n'), 'aice-python-start': ('aice_python_start', 'aice-python-start-1', 'o'), 'aice-python-conditions': ('aice_python_conditions', 'aice-python-conditions-1', 'p'), 'aice-table-csv': ('aice_table_csv', 'aice-table-csv-1', 'q'), 'engineer-c-start': ('engineer_c_start', 'engineer-c-start-1', 'r')}


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':')).encode()).hexdigest()


def write_changed(path, value):
    text = json.dumps(value, ensure_ascii=False, indent=2) + '\n'
    if not path.exists() or path.read_bytes() != text.encode('utf-8'):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8', newline='\n')
        return True
    return False


def build(name, check=False):
    folder, revision, pilot = LESSONS[name]
    SOURCE = ROOT / 'tools/redesigned_lessons' / folder
    OUTPUT = ROOT / 'courses/redesigned' / f'{name}.json'
    prd = json.loads((SOURCE / 'approved-prd.json').read_text(encoding='utf-8'))
    validate(prd, require_approval=True)
    authored = json.loads((SOURCE / 'content.json').read_text(encoding='utf-8'))
    steps = [step for chapter in prd['chapters'] for unit in chapter['units'] for step in unit['steps']]
    tasks = copy.deepcopy(authored['tasks'])
    for task in tasks:
        if task['id'] == authored.get('head_three_step'):
            task['checker'] = pandas_head_checker()
        cases = authored.get('prepared_cases', {}).get(task['id'])
        if cases is not None:
            if task['language'] != 'python' or task.get('interaction'):
                raise ValueError('준비 자료 검사는 파이썬 코드 문제에만 넣어요.')
            task['checker'] = python_prepared_checker(cases)
    if [task['id'] for task in tasks] != [step['id'] for step in steps]:
        raise ValueError('제작한 스텝이 승인된 PRD 구성과 달라요.')
    stale = []
    for step, task in zip(steps, tasks):
        actions = task['narration']
        if not actions or not any('조심하세요' in action.get('text', '') for action in actions):
            raise ValueError(f"{step['id']}: 주의할 지점이 없는 해설이에요.")
        for index, action in enumerate(actions):
            if action['action'] in ('git_command', 'run'):
                if index + 1 == len(actions):
                    raise ValueError('명령 실행 뒤 결과 설명이 필요해요.')
                following = actions[index + 1]
                if following['action'] != 'say' and not following.get('say'):
                    raise ValueError('명령 실행 뒤 결과를 짚어 주세요.')
        source_hash = digest({'step': step, 'task': task, 'policy': prd['policy_snapshot']})
        cache = SOURCE / 'narration_cache' / f"{step['id']}.json"
        expected = {'by': 'hand', 'source_sha256': source_hash, 'entry': actions}
        existing = json.loads(cache.read_text(encoding='utf-8')) if cache.exists() else None
        if existing != expected:
            stale.append(step['id'])
            if not check:
                write_changed(cache, expected)
    # Only learner-facing hierarchy is published. Core flows and approval evidence stay in authoring.
    chapters = copy.deepcopy(prd['chapters'])
    presentation = authored['presentation']
    for chapter in chapters:
        chapter['objectives'] = presentation['chapters'][chapter['id']]
        for unit in chapter['units']:
            display = presentation['units'][unit['id']]
            unit['objectives'] = display['objectives']
            unit['premise'] = display['premise']
            unit['steps'] = [{'id': step['id'], 'objectives': step['objectives']} for step in unit['steps']]
    lesson = {'schema_version': 2, 'id': prd['id'], 'revision': revision,
              'title': prd['title'], 'description': authored['description'],
              'objectives': presentation['objectives'], 'sources': [source['url'] for source in prd['sources']],
              'review_enabled': False, 'sections': [], 'chapters': chapters, 'tasks': tasks}
    if check:
        if stale or not OUTPUT.exists() or json.loads(OUTPUT.read_text(encoding='utf-8')) != lesson:
            raise ValueError('해설 또는 수업 파생물이 낡았어요. --redesigned-git로 다시 만드세요.')
    else:
        write_changed(OUTPUT, lesson)
    course_path = ROOT / 'tests/fixtures/player-pilot' / pilot / 'course.json'
    course = json.loads(course_path.read_text(encoding='utf-8'))
    course['lessons'][0]['sha256'] = hashlib.sha256(OUTPUT.read_bytes()).hexdigest()
    if check:
        if json.loads(course_path.read_text(encoding='utf-8')) != course:
            raise ValueError('검증 코스가 이전 수업 해시를 가리켜요.')
    else:
        write_changed(course_path, course)
    print(f"{name}: {len(tasks)}스텝, 해설 {len(stale)}개 갱신, PRD {content_hash(prd)[:12]}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--lesson', choices=[*LESSONS, 'all'], default='all')
    args = parser.parse_args()
    for name in LESSONS if args.lesson == 'all' else [args.lesson]:
        build(name, args.check)
