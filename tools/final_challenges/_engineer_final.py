"""Authored practical-exam challenges: runnable code or independently graded written fields."""
import json
from pathlib import Path
from _common import Script, ids, todo

ROOT = Path(__file__).resolve().parents[2]


def base(key, title, objective, goal, task, outputs, reject, accept, review=None):
    unit, step = ids(key)
    catalog = json.loads((ROOT / 'tools/redesigned_courses/catalog.json').read_text(encoding='utf-8'))
    item = next(x for c in catalog['courses'] for x in c['lessons'] if x['key'] == key)
    content = json.loads((ROOT / 'tools/redesigned_lessons' / key.replace('-', '_') / 'content.json').read_text(encoding='utf-8'))
    revision = item['revision'] if any(t['id'] == step for t in content['tasks']) else key + '-' + str(int(item['revision'].rsplit('-', 1)[1]) + 1)
    task.update(id=step, title=title, required=True)
    return dict(key=key, course='engineer', revision=revision,
        reason=objective + ' 앞에서 나눠 익힌 조건을 한 자료에 함께 적용하는 마지막 도전이에요.',
        grading='시작 답안은 실패해야 해요. 실제 실행 결과 또는 각 서술형 답안 칸을 검사하고 오답과 동등한 정답도 대조해요.',
        unit=dict(id=unit, title='마지막 도전', objectives=[objective], premise=goal),
        step=dict(id=step, title=title, objectives=[objective], core_flow=goal + '\n' + objective),
        task=task, cases=dict(expected_outputs=outputs, reject=reject, accept=accept), review=review or {})


def code(key, title, objective, goal, language, starter, patches, expected, outputs,
         variants, reject, accept, before, after, caution, files=None):
    solution = starter
    for old, new, _ in patches:
        assert solution.count(old) == 1, (key, old)
        solution = solution.replace(old, new, 1)
    s = Script(starter)
    s.say('마지막 도전이에요. ' + objective, 'text:' + objective)
    s.run()
    s.say(before, 'output')
    for old, new, instruction in patches:
        s.patch(old, new, instruction)
    s.run()
    s.say(after, 'output')
    s.say(caution, 'code:' + patches[-1][1].splitlines()[-1])
    task = dict(language=language, starter_code=starter, solution=solution,
        goal=objective + '\n\n' + goal + '\n\n' + todo('코드 실행을 눌러 수정 전 결과를 확인하세요.',
        *[p[2] for p in patches], '다시 실행해 결과를 확인하고 작성한 코드를 제출하세요.'),
        tests=[dict(input='', expected=expected)], narration=s.actions)
    if variants:
        task['variations'] = variants
    if files:
        task['files'] = files
    spec = base(key, title, objective, goal, task, outputs, reject, accept,
                {caution: '이 도전의 잘못된 코드와 다른 준비 자료 검사로 확인하는 실수예요.'})
    spec['_snapshots'] = s.snapshots
    return spec


def fields(key, title, objective, scenario, questions, explanations, example=None, output=None):
    """Questions are applications of an explicit scenario, not multiple choice or copied labels."""
    answers = {q[0]: q[2][0] for q in questions}
    solution = json.dumps(answers, ensure_ascii=False)
    actions = [dict(action='say', text='마지막 도전이에요. ' + objective, target='text:' + objective)]
    if example:
        actions.append(dict(action='run', lines=[1, len(example.splitlines())]))
    for q, explanation in zip(questions, explanations):
        actions.append(dict(action='say', text=explanation, target='text:' + q[1]))
    actions.append(dict(action='fill_answer', value=solution))
    task = dict(language='python', goal=objective + '\n\n' + scenario + '\n\n' +
        '\n'.join(f'**{q[1]}**' for q in questions) + '\n\n' +
        todo('주어진 자료와 조건을 먼저 읽으세요.', '각 답안 칸의 질문에 맞춰 값이나 용어를 적으세요.', '세 답안을 모두 확인하고 제출하세요.'),
        starter_code='', solution=solution, tests=[], interaction=dict(kind='fill_fields',
        fields=[dict(id=q[0], label=q[1], accepted=q[2]) for q in questions]), narration=actions)
    if example:
        task['example_code'] = example
    # A single wrong component must invalidate the whole challenge.
    reject = [([[json.dumps(q[2][0], ensure_ascii=False), json.dumps('__오답__', ensure_ascii=False)]],
               q[1] + '도 독립적으로 맞아야 해요.') for q in questions
               if solution.count(json.dumps(q[2][0], ensure_ascii=False)) == 1]
    accept = []
    for q in questions:
        if len(q[2]) > 1 and solution.count(json.dumps(q[2][0], ensure_ascii=False)) == 1:
            accept.append(([[json.dumps(q[2][0], ensure_ascii=False), json.dumps(q[2][1], ensure_ascii=False)]], '허용한 동의어도 정답이에요.'))
    return base(key, title, objective, scenario, task, [output] if example else [], reject, accept)
