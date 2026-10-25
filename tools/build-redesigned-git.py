"""Compile approved practice lessons; retain unchanged narration caches."""
import argparse
import copy
import hashlib
import json
import re
from pathlib import Path

from lesson_prd import content_hash, validate
from lesson_registry import load_registry
from narration_review import check_lesson as check_narration_review
from redesigned_lessons.python_prepared_checks import checker as python_prepared_checker
from redesigned_lessons.pandas_head_checks import checker as pandas_head_checker

ROOT = Path(__file__).resolve().parents[1]
LESSONS = {row["key"]: (row["folder"], row["revision"], row["pilot"]) for row in load_registry()}


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


# Generic lines that replaced a real explanation of the step (2026-10-24 user criteria).
BOILERPLATE = ('이번 스텝에 제공된 코드로 설명할게요', '직접 작성한 답은 해설 뒤에도 유지돼요',
    '한 곳만 바꿔 실행 결과를 비교해요', '이 조건 한 곳만 바꿔', '연결 또는 비교 한 곳만 바꿔',
    '입력과 결과를 연결해 보세요', '화면의 명령을 한 번 실행해 볼게요', '화면의 명령을 실행하고 결과를 볼게요',
    '처음 조건의 결과를 기준으로 답을 골라요', '처음 코드의 결과를 기준으로', '처음 코드의 결과를 확인하고 답안에 적어요',
    '읽을 값과 출력할 줄을 먼저 살펴봐요', '먼저 실행할 코드와 출력 위치를 살펴봐요', '문제의 처음 코드로 돌아와 비교를 마무리해요',
    '앞 문제의 파일과 기록을 그대로 이어서 써요', '한 명령의 결과를 확인한 뒤 다음 명령으로 넘어가세요')


# Region keys that frame the whole problem panel (assets/layout/agent.js TARGETS).
COARSE_TARGETS = ('problem', 'examples', 'hint', 'prompt')
# Sentences that are spoken without any spotlight, each with the reviewed reason (no on-screen words,
# option or code to point at). Every target-less say must be listed and every entry must still exist.
EXCEPTIONS = ROOT / 'tools/redesigned_lessons/narration-target-exceptions.json'


def caption_only_record():
    entries = json.loads(EXCEPTIONS.read_text(encoding='utf-8')) if EXCEPTIONS.exists() else []
    for entry in entries:
        if not entry.get('reason', '').strip():
            raise ValueError(f"강조 없는 해설에 이유가 없어요: {entry.get('text', '')[:40]}")
    return {(entry['lesson'], entry['step_id'], entry['text']) for entry in entries}


def check_caption_only(name, tasks, record):
    spoken = set()
    for task in tasks:
        for action in task['narration']:
            if action['action'] == 'say' and not action.get('target'):
                key = (name, task['id'], action.get('text', ''))
                if key not in record:
                    raise ValueError(f"{task['id']}: 강조 대상이 없는 해설이에요. 정확히 가리키거나 예외 기록에 이유를 남기세요: {key[2][:40]}")
                spoken.add(key)
    stale = {key for key in record if key[0] == name} - spoken
    if stale:
        raise ValueError(f'{name}: 예외 기록에 없는 해설이 남아 있어요: ' + ' | '.join(key[2][:40] for key in sorted(stale)[:3]))


def plain(markdown):
    """The text a learner sees for a markdown goal: markers removed and whitespace collapsed."""
    lines = []
    for line in markdown.splitlines():
        line = re.sub(r'^\s*(?:\d+\.|[-*+]|#+)\s+', '', line)
        line = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', line)
        lines.append(line)
    return re.sub(r'\s+', ' ', re.sub(r'[`*]', '', '\n'.join(lines))).strip()


def occurrence(spec):
    match = re.fullmatch(r'(.*?)(?:#(\d+))?', spec, re.S)
    return match[1], int(match[2]) if match[2] else None


def count(text, wanted):
    return sum(1 for index in range(len(text)) if text.startswith(wanted, index)) if wanted else 0


def validate_highlights(task):
    source = task.get('example_code') or task.get('starter_code', '')
    if task.get('git_terminal', {}).get('java_build') is not None:
        source = task['git_terminal']['shell']['demo']['files']['Main.java']
    goal = plain(task.get('goal', ''))
    screen = ' '.join([plain(task.get('title', '')), plain(task.get('question', '')), goal, *map(plain, task.get('hints', []))])
    options = {option['id'] for option in (task.get('interaction') or {}).get('options', [])}
    for action in task['narration']:
        target = action.get('target', '')
        # A spoken sentence is anchored to the exact words, option or code it explains; a frame
        # around the whole problem panel is not an explanation of any one sentence.
        if action['action'] == 'say' and target in COARSE_TARGETS:
            raise ValueError(f'문제 전체를 강조해요. 설명하는 문장(text:)·보기(answer:)·코드(code:)를 정확히 가리키세요: {action.get("text", "")[:40]}')
        if target.startswith('answer:') and target[7:] not in options:
            raise ValueError(f'없는 보기를 강조해요: {target}')
        if target.startswith('text:'):
            phrase, nth = occurrence(target[5:])
            wanted = plain(phrase)
            if not wanted or count(screen, wanted) == 0:
                raise ValueError(f'문제에 없는 구절을 강조해요: {phrase}')
            if nth is None and count(goal, wanted) > 1:
                raise ValueError(f'같은 구절이 여러 번 있어요. #n으로 고르세요: {phrase}')
            if nth is not None and nth > count(screen, wanted):
                raise ValueError(f'구절의 {nth}번째가 없어요: {phrase}')
        if target.startswith('code:'):
            snippet, nth = occurrence(target[5:])
            found = count(source, snippet)
            if not snippet or not found or (nth or 1) > found:
                raise ValueError(f'현재 코드에 없는 부분을 강조해요: {snippet}')
            if nth is None and found > 1:
                raise ValueError(f'코드에 같은 부분이 여러 번 있어요. #n으로 고르세요: {snippet}')
        lines = action.get('lines')
        if target.startswith(('lines:', 'editor:')):
            match = re.fullmatch(r'(?:lines|editor):(\d+)(?::(\d+))?', target)
            if not match:
                raise ValueError(f'코드 강조 형식을 확인하세요: {target}')
            lines = [int(match[1]), int(match[2] or match[1])]
        if lines is not None:
            if (not isinstance(lines, list) or len(lines) != 2
                    or any(type(line) is not int for line in lines)
                    or not 1 <= lines[0] <= lines[1] <= len(source.splitlines())):
                raise ValueError(f'현재 코드에 없는 줄을 강조해요: {lines}')
            marked = source.splitlines()[lines[0] - 1:lines[1]]
            if all(line.strip() in ('', '{', '}', '};') for line in marked):
                raise ValueError(f'빈 줄이나 괄호만 강조해요: {lines}')
            # A run highlights the statement whose output the next sentence reads.
            if (action['action'] == 'run' and not action.get('expect_error') and task.get('language') in ('java', 'python', 'c')
                    and 'print' in source and not any('print' in line for line in marked)):
                raise ValueError(f'실행 강조가 출력문을 가리키지 않아요: {lines} {marked}')
        if action['action'] == 'patch_code':
            before = action['before']
            if source.count(before) != 1:
                raise ValueError('해설이 수정할 코드 영역은 정확히 하나여야 해요.')
            source = source.replace(before, action['after'], 1)
        elif action['action'] == 'set_code':
            source = action['code']
        elif action['action'] == 'order_answer' and task.get('example_order_marker'):
            options = {option['id']: option['text'] for option in task['interaction']['options']}
            source = task['example_code']
            marker = task['example_order_marker']
            offset = source.index(marker)
            indent = source[source.rfind('\n', 0, offset) + 1:offset]
            replacement = '\n'.join(options[key] for key in action['ids'])
            if not indent.strip(' \t') and not source[offset + len(marker):].split('\n', 1)[0].strip():
                replacement = replacement.replace('\n', '\n' + indent)
            source = source.replace(marker, replacement)


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
            task['checker'] = python_prepared_checker(cases, authored.get('prepared_probes', {}).get(task['id']),
                timeout_seconds=authored.get('prepared_timeout_seconds', 10))
    if [task['id'] for task in tasks] != [step['id'] for step in steps]:
        raise ValueError('제작한 스텝이 승인된 PRD 구성과 달라요.')
    stale = []
    for step, task in zip(steps, tasks):
        if True:
            goal = task['goal']
            if goal.count('**할 일**') != 1:
                raise ValueError(f"{step['id']}: 할 일을 한곳에 표시하세요.")
            todo = goal.split('**할 일**', 1)[1].strip()
            items = re.findall(r'^(\d+)\. (.+)$', todo, re.MULTILINE)
            if not items or [int(number) for number, _ in items] != list(range(1, len(items) + 1)):
                raise ValueError(f"{step['id']}: 할 일을 순서 있는 번호 목록으로 쓰세요.")
            if len(items) != len([line for line in todo.splitlines() if line.strip()]) or '제출' not in items[-1][1]:
                raise ValueError(f"{step['id']}: 할 일 목록은 제출까지 빠짐없이 이어 쓰세요.")
        if name.startswith("java-") and task.get("interaction",{}).get("kind")=="choice":
            if not task.get("question","").strip().endswith("?"):
                raise ValueError(f"{step['id']}: 활동 이름과 별도로 정확한 질문을 쓰세요.")
            if not task.get("title", "").strip().endswith("?"):
                raise ValueError(f"{step['id']}: 선택형 제목에서도 무엇을 답할지 질문하세요.")
        validate_highlights(task)
        actions = task['narration']
        if not actions:
            raise ValueError(f"{step['id']}: 해설이 없어요.")
        # The narration explains this problem: at least one exact sentence of the problem, and the
        # exact code it talks about when the step shows code.
        if not any(action.get('target', '').startswith('text:') for action in actions):
            raise ValueError(f"{step['id']}: 해설이 문제의 어느 문장을 설명하는지 text: 강조가 없어요.")
        has_code = bool(task.get('example_code') or task.get('starter_code')) or task.get('git_terminal', {}).get('java_build') is not None
        if has_code and not any(action.get('target', '').startswith(('code:', 'lines:', 'editor:')) or action.get('lines') for action in actions):
            raise ValueError(f"{step['id']}: 설명하는 코드 줄이나 토큰을 강조하지 않았어요.")
        for action in actions:
            spoken = (action.get('text') or action.get('say') or '')
            for phrase in BOILERPLATE:
                if phrase in spoken:
                    raise ValueError(f"{step['id']}: 문제를 설명하지 않는 상투 문장이에요: {phrase}")
            if '조심하세요' in spoken and any(objective.rstrip('.') in spoken for objective in step['objectives']):
                raise ValueError(f"{step['id']}: 경고가 교육 목표를 되풀이해요.")
        for index, action in enumerate(actions):
            if action['action'] in ('git_command', 'bash_command', 'vim_open', 'vim_keys', 'vim_wait', 'write_memo', 'inspect_folder', 'read_memo', 'run', 'web_action'):
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
    check_caption_only(name, tasks, caption_only_record())
    # Meaning review (tools/narration_review.py): the form checks above cannot tell whether a sentence is
    # true and clear for this step. A changed step needs a fresh review; open findings block the build.
    check_narration_review(name, steps, authored['tasks'])
    # A sentence reused across many steps is a template, not an explanation of each problem.
    usage = {}
    for task in tasks:
        for spoken in {(action.get('text') or action.get('say') or '').strip() for action in task['narration']}:
            if len(spoken) >= 12:
                usage.setdefault(spoken, set()).add(task['id'])
    repeated = [(spoken, len(ids)) for spoken, ids in usage.items() if len(ids) >= 3 or ('조심하세요' in spoken and len(ids) >= 2)]
    if repeated:
        raise ValueError(f"{name}: 여러 스텝에 같은 해설 문장을 반복해요: " + ' | '.join(f'{text[:40]}×{n}' for text, n in repeated[:5]))
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
    if presentation.get('learning_strategy'):
        lesson['learning_strategy'] = presentation['learning_strategy']
    if check:
        if stale or not OUTPUT.exists() or json.loads(OUTPUT.read_text(encoding='utf-8')) != lesson:
            raise ValueError('해설 또는 수업 파생물이 낡았어요. --redesigned-git로 다시 만드세요.')
    else:
        write_changed(OUTPUT, lesson)
    course_path = ROOT / 'tests/fixtures/player-pilot' / pilot / 'course.json'
    course = json.loads(course_path.read_text(encoding='utf-8'))
    course['lessons'][0]['revision'] = revision
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
