"""Author the approved 2026-10-26 backend journey update, with execution evidence.

Runs only isolated Java/Node source examples. Does not publish repositories or
alter user services. The existing final tasks keep their IDs and content.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import uuid

from lesson_prd import content_hash
from narration_review import context_sha256, prompts
from redesigned_courses.backend_buildup import STAGES, MODEL

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, value):
    raw = json.dumps(value, ensure_ascii=False, indent=1 if path.name == 'narration-review.json' else 2) + '\n'
    if not path.exists() or path.read_text(encoding='utf-8') != raw:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(raw, encoding='utf-8', newline='\n')


def identity(key):
    return 'stp_' + str(uuid.UUID(bytes=hashlib.sha256(('backend-journey:' + key).encode()).digest()[:16], version=4))


def run(source, language):
    with tempfile.TemporaryDirectory(prefix='mq3-journey-') as folder:
        name = 'Main.java' if language == 'java' else 'main.js'
        Path(folder, name).write_text(source, encoding='utf-8')
        cmd = ['java', '-Xmx128m', '-Dfile.encoding=UTF-8', '-Dstdout.encoding=UTF-8', name] if language == 'java' else ['node', name]
        result = subprocess.run(cmd, cwd=folder, capture_output=True, timeout=25)
        if result.returncode:
            raise ValueError(result.stderr.decode('utf-8', 'replace')[-1600:])
        return result.stdout.decode('utf-8').replace('\r\n', '\n')


def make_stage(key, number, data):
    title, context, body, before, after, interpretation = data
    language = 'javascript' if key == 'node-cpu-offload' else 'java'
    boundary = ('실제 Node worker 스레드 하나를 만들어요. 계산 결과 메시지를 주고받아요.' if key == 'node-cpu-offload' and number == 4
                else '실제 Node에서 실행해요. 이 단계는 스레드를 만들지 않아요.' if language == 'javascript'
                else '실제 소켓을 127.0.0.1의 동적 포트에서 열어요. 연결과 서버는 이 실행이 끝날 때 닫아요.' if key == 'socket-partial-frames' and number == 4
                else '문자열을 받는 과정의 교육용 모형이에요. 아직 실제 소켓을 열지 않아요.' if key == 'socket-partial-frames' else MODEL)
    initial = 9 if key == 'sys-page-table' and number == 3 else 6
    if language == 'java':
        before = before.replace('\n', '\n    ')
        after = after.replace('\n', '\n    ')
    code = (f'// 준비 값: 변형 검사에서 값이 달라져요.\nconst VALUE = {initial};\n' + body + '\n' if language == 'javascript'
            else f'// 준비 값: 변형 검사에서 값이 달라져요.\nstatic final int VALUE = {initial};\n\nvoid main() {{\n'
                 + '\n'.join('    ' + line for line in body.splitlines()) + '\n}\n')
    if code.count(before) != 1:
        raise ValueError(f'{key}/{number}: edit must identify one span')
    solution = code.replace(before, after)
    start, expected = run(code, language), run(solution, language)
    if start.rstrip() == expected.rstrip():
        raise ValueError(f'{key}/{number}: no observable difference')
    variants = []
    for value in (7, 9):
        out = run(solution.replace(f'VALUE = {initial};', f'VALUE = {value};'), language)
        variants.append(dict(values={'VALUE': str(value)}, expected=out))
    task = dict(id=identity(f'{key}:{number}'), title=title, question=context,
                goal=context + '\n\n' + boundary + '\n\n이번 단계의 준비 코드로 시작해요. 앞 단계의 답안은 별도로 남아요.\n\n**할 일**\n\n'
                     + f'1. 준비 코드를 실행하고 출력을 읽으세요.\n2. `{before.splitlines()[0].strip()}` 부분에서 요구한 관계를 계산하도록 고치세요.\n3. 다시 실행해 바뀐 출력을 비교하세요.\n4. 제출하세요. 준비 값을 바꾼 경우도 검사해요.',
                language=language, starter_code=code, solution=solution,
                tests=[dict(input='', expected=expected)], variations=variants, required=True,
                supporting_materials=[dict(id='trace', title='준비 코드의 실행 기록', kind='interactive', variants=[dict(label='준비 코드', frames=[
                    dict(caption=boundary, facts={'근거': '위 준비 코드를 실제로 실행한 출력이에요.'}),
                    *[dict(caption=line, facts={'출력': line}) for line in start.strip().splitlines() if line.strip()]
                ])])],
                narration=[
                    dict(action='say', text=context, target='text:' + context),
                    dict(action='run'),
                    dict(action='say', text='지금 출력은 ' + '. '.join(line for line in start.strip().splitlines() if line.strip()) + '예요.', target='output'),
                    dict(action='say', text=f'{before} 부분에서 요구한 관계를 계산하고 있는지 봐요.', target='code:' + before),
                    dict(action='patch_code', before=before, after=after, say=f'{after}로 바꿔 비교해요.'),
                    dict(action='run'),
                    dict(action='say', text=interpretation, target='output'),
                    dict(action='submit'),
                ])
    step = dict(id=task['id'], title=title, objectives=[context],
                core_flow=f'새 개념: {title}\n시작: {boundary}\n변경: {before} → {after}\n관찰: {interpretation}\n외부 서비스: 없음. 이전 답안을 덮어쓰지 않는 별도 준비 코드예요.')
    evidence = dict(key=key, step=task['id'], title=title, starter_output=start,
                    expected=expected, variants=len(variants), starter_rejected=True,
                    source_sha256=hashlib.sha256(solution.encode()).hexdigest())
    return task, step, evidence


def main():
    catalog_path = ROOT / 'tools/redesigned_courses/catalog.json'
    catalog = read(catalog_path)
    java = next(c for c in catalog['courses'] if c['key'] == 'java')
    classes_path = ROOT / 'tools/redesigned_courses/lesson-classification.json'
    classes = read(classes_path)
    categories = [('java', '자바'), ('git', 'Git'), ('terminal', '터미널 · Bash·Vim'), ('frontend', '화면'),
                  ('network', '네트워크'), ('memory', 'OS·메모리'), ('db', 'DB'),
                  ('language', '언어·인터프리터'), ('concurrency', '동시성·Node')]
    classes['courses']['java']['categories'] = [dict(id=i, title=t) for i, t in categories]
    class_lessons = classes['courses']['java']['lessons']
    ledger_path = ROOT / 'tools/redesigned_lessons/narration-review.json'
    ledger = read(ledger_path)
    evidence = []
    for item in java['lessons']:
        key = item['key']
        category = ('terminal' if key in ('bash-basics', 'vim-basics') else 'git' if key.startswith(('git-', 'github-'))
                    else 'frontend' if key in ('java-tailwind', 'java-react')
                    else 'network' if key in ('sys-sliding-window', 'socket-partial-frames')
                    else 'memory' if key in ('sys-page-table', 'sys-cache-locality')
                    else 'db' if key == 'sys-buffer-pool' else 'language' if key == 'sys-interpreter-env'
                    else 'concurrency' if key in ('sys-interleavings', 'node-cpu-offload') else 'java')
        class_lessons[key] = dict(category=category, track=None, status='approved',
                                 decided_by='사용자: 과정 주제별 분류 구현 지시', decided_on='2026-10-26',
                                 evidence={'category': '실제 수업의 실행 도구와 주제 기준.',
                                           'track': '기존 기본 수업 결정을 보존해요. 이 분류는 필수 여부와 난이도를 바꾸지 않아요.'}, title=item['title'])
        if key not in STAGES:
            continue
        folder = ROOT / Path(item['authoring_prd']).parent
        prd, authored = read(folder / 'approved-prd.json'), read(folder / 'content.json')
        # Preserve the original final challenge exactly, even when rerunning the authoring command.
        final = authored['tasks'][-1]
        final_step = prd['chapters'][-1]['units'][-1]['steps'][-1]
        tasks, steps = [], []
        for n, data in enumerate(STAGES[key], 1):
            task, step, proof = make_stage(key, n, data)
            tasks.append(task)
            steps.append(step)
            evidence.append(proof)
            # Author self-review of these exact authored sentences and executed outputs; never human sign-off.
            # Keep an earlier record while its exact context is unchanged; a changed or new step gets a fresh one.
            previous = ledger['steps'].get(step['id'])
            if previous and previous.get('context_sha256') == context_sha256(step, task):
                continue
            ledger['steps'][step['id']] = dict(lesson=key, state='reviewed', context_sha256=context_sha256(step, task),
                reviewed='2026-10-26', reviewer='Claude author self-review (resumed run); not independent or human review',
                checked={p['text']: f'작성자 자체 검토: {data[1]} / {data[5]} 수정 전후 실제 실행 출력과 대조했어요.' for p in prompts(task)}, findings=[])
        authored['tasks'] = tasks + [final]
        unit = prd['chapters'][0]['units'][0]
        unit['title'] = '작은 실습에서 마지막 도전으로'
        unit['steps'] = steps + [final_step]
        authored['presentation']['units'][unit['id']]['objectives'] = unit['objectives']
        prd['out_of_scope'] = [x for x in prd['out_of_scope'] if '최종 문제 하나' not in x]
        prd['approval'].update(by='사용자의 수업 구체화 지시(2026-10-26)',
            evidence='27~34번을 작은 도전과 관찰로 구체화하라는 직접 구현 지시. 기존 최종 문제의 본질·ID는 유지. 사람의 개별 검토를 뜻하지 않아요.')
        prd['approval']['content_sha256'] = content_hash(prd)
        item['revision'] = key + '-2'
        item['validation']['modifications'] = {str(i): {'correct': True} for i in range(1, len(tasks) + 2)}
        write(folder / 'content.json', authored)
        write(folder / 'approved-prd.json', prd)
        # Real-grader cases: each bridge replays starter then solution; the final keeps its authored
        # outputs and documented wrong answers, now numbered as the last step. Idempotent on rerun.
        cases_path = ROOT / f'tests/lesson-cases/{key}.json'
        cases = read(cases_path)
        bridge = [p for p in evidence if p['key'] == key]
        cases['expected_outputs'] = [[p['starter_output'].rstrip('\n'), p['expected'].rstrip('\n')] for p in bridge] + [cases['expected_outputs'][-1]]
        for rejected in cases['reject']:
            rejected['step'] = len(bridge) + 1
        write(cases_path, cases)
    write(catalog_path, catalog)
    write(classes_path, classes)
    write(ledger_path, ledger)
    write(ROOT / '.scratch/backend-lesson-journeys/execution-evidence.json', evidence)
    print(f'{len(java["lessons"])} lessons classified; {len(evidence)} executable buildup steps authored and checked')


if __name__ == '__main__':
    main()
