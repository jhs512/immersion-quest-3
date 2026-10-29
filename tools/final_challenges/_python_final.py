"""Build a single, explicitly authored Python challenge with an observed before/after demo."""
import ast
import json
from pathlib import Path
from _common import Script, ids, todo

ROOT = Path(__file__).resolve().parents[2]


def make(key, title, goal, objective, starter, patches, expected, variants, wrong, equivalent,
         before, partial, after, caution, probe=None, first_error=None, timeout=30, baseline_values=None):
    unit, step = ids(key)
    folder = ROOT / 'tools/redesigned_lessons' / key.replace('-', '_')
    # The original revision is pinned when the new spec is authored, not inferred from a regenerated file.
    base = json.loads((ROOT / 'tools/redesigned_courses/catalog.json').read_text(encoding='utf-8'))
    item = next(l for c in base['courses'] for l in c['lessons'] if l['key'] == key)
    content = json.loads((folder / 'content.json').read_text(encoding='utf-8'))
    has_step = any(t['id'] == step for t in content['tasks'])
    revision = item['revision'] if has_step else key + '-' + str(int(item['revision'].rsplit('-', 1)[1]) + 1)
    solution = starter
    for old, new, _ in patches:
        assert solution.count(old) == 1, (key, old)
        solution = solution.replace(old, new, 1)
    instructions = [text for _, _, text in patches]
    text = goal + '\n\n' + todo('코드 실행을 눌러 현재 결과를 확인하세요.', *instructions,
                               '다시 실행해 요구한 결과를 확인한 뒤 작성한 코드를 제출하세요.')
    s = Script(starter)
    s.say('마지막 도전이에요. ' + objective, 'text:' + objective)
    s.run(expect_error=first_error)
    s.say(before, 'output')
    old, new, instruction = patches[0]
    s.patch(old, new, instruction)
    s.run()
    s.say(partial, 'output')
    for old, new, instruction in patches[1:]:
        s.patch(old, new, instruction)
    s.run()
    s.say(after, 'output')
    s.say(caution, 'code:' + patches[-1][1].splitlines()[-1])
    # A custom checker replaces ordinary stdout tests. Keep the visible preparation in its own
    # explicit case as well, so variants whose MSE happens to be 0 or 1 cannot hide a missing root.
    baseline = baseline_values or {}
    for node in ast.parse(starter).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            try:
                if not baseline:
                    baseline[node.targets[0].id] = ast.literal_eval(node.value)
                break
            except (ValueError, TypeError):
                pass
    if not baseline:
        raise ValueError(f'{key}: give the checker at least one explicit prepared input')
    return dict(
        key=key, course='aice', revision=revision,
        reason=objective + ' 기존 단일 수정에서 새 자료의 여러 조건을 함께 판단하는 문제로 넓혀요.',
        grading='실제 Python 실행과 다른 준비 자료의 결과를 검사해요. 시작 코드는 실패하고 동등한 풀이도 통과해야 해요.',
        unit=dict(id=unit, title='마지막 도전', objectives=[objective], premise=goal.split('\n')[0]),
        step=dict(id=step, title=title, objectives=[objective], core_flow=goal + '\n' + before + '\n' + partial + '\n' + after),
        task=dict(id=step, title=title, language='python', goal=objective + '\n\n' + text,
                  starter_code=starter, solution=solution, required=True,
                  tests=[dict(input='', expected=expected)], narration=s.actions),
        prepared_cases=[dict(values=baseline, expected=expected), *variants], prepared_probe=probe, prepared_timeout_seconds=timeout,
        _snapshots=s.snapshots,
        cases=dict(expected_outputs=[None, None, None], reject=wrong, accept=equivalent),
        review={caution: '이 문제의 잘못된 코드와 준비 자료 교체 검사로 확인하는 구체적 오류예요.'})
