"""Compile small, independent Python input variants into a lesson-owned checker."""
import json


def _output_checker(cases, timeout_seconds=10, headless_figures=False):
    if type(timeout_seconds) is not int or not 1 <= timeout_seconds <= 45:
        raise ValueError("독립 검사 시간은 1~45초로 정하세요.")
    if not isinstance(cases,list) or not 1 <= len(cases) <= 50:
        raise ValueError('준비 값 검사 사례를 확인하세요.')
    for case in cases:
        if set(case) != {'values','expected'} or not isinstance(case['expected'],str):
            raise ValueError('준비 값과 예상 출력을 확인하세요.')
        values = case['values']
        if not isinstance(values,dict) or not 1 <= len(values) <= 20 or any(not name.isascii() or not name.isidentifier() for name in values):
            raise ValueError('준비 자료 이름을 확인하세요.')
    payload = json.dumps(cases, ensure_ascii=False)
    script = """import ast
import copy
import json
import subprocess
import sys
from pathlib import Path

source = Path('main.py').read_text(encoding='utf-8')
original = ast.parse(source, filename='main.py')
cases = json.loads(PAYLOAD)
for case in cases:
    tree = copy.deepcopy(original)
    remaining = set(case['values'])
    for statement in tree.body:
        if isinstance(statement, ast.Assign):
            names = [target.id for target in statement.targets if isinstance(target, ast.Name)]
            for name in names:
                if name in remaining:
                    statement.value = ast.parse(repr(case['values'][name]), mode='eval').body
                    remaining.remove(name)
    if remaining:
        raise AssertionError('준비된 자료의 이름은 그대로 두세요.')
    ast.fix_missing_locations(tree)
    result = subprocess.run([sys.executable, '-I', '-X', 'utf8', '-c', ast.unparse(tree)],
                            stdin=subprocess.DEVNULL, capture_output=True, text=True,
                            encoding='utf-8', timeout=CASE_TIMEOUT)
    if result.returncode != 0 or result.stdout.strip() != case['expected'].strip():
        raise AssertionError('다른 준비 값에서도 같은 원리가 맞는지 확인하세요.')
print('준비 값을 바꾼 검사도 통과했어요.')
""".replace('CASE_TIMEOUT', str(timeout_seconds)).replace('PAYLOAD', repr(payload))
    if headless_figures:
        # The app hands MPLBACKEND=Agg only to the learner's own run, not to this checker, so a case
        # calling plt.show() would wait for a window. Render its figures off-screen like that run does.
        script = script.replace('import json\n', 'import json\nimport os\n', 1)
        script = script.replace('    result = subprocess.run(',
                                "    # Figures render off-screen as in the player's own run, so plt.show() never waits for a window.\n"
                                '    result = subprocess.run(', 1)
        script = script.replace(f"encoding='utf-8', timeout={timeout_seconds})\n",
                                f"encoding='utf-8', timeout={timeout_seconds}, env=dict(os.environ, MPLBACKEND='Agg'))\n", 1)
    return script


def uses_figures(*sources):
    """Whether task code draws with matplotlib/seaborn, so its prepared cases need a headless backend."""
    return any(word in (source or '') for source in sources for word in ('matplotlib', 'seaborn'))


def checker(cases, probe=None, *, timeout_seconds=10, headless_figures=False):
    script = _output_checker(cases, timeout_seconds, headless_figures)
    if probe is None:
        return script
    if not isinstance(probe, str) or not probe.strip():
        raise ValueError('실제 상태를 확인할 검사문을 확인하세요.')
    script = script.replace('import sys\n', 'import sys\nimport uuid\n', 1)
    script = script.replace('for case in cases:\n', 'probe = ' + repr(probe) + '\nfor case in cases:\n', 1)
    script = script.replace('    ast.fix_missing_locations(tree)\n',
                            "    witness = uuid.uuid4().hex\n"
                            "    tree.body.extend(ast.parse(probe).body)\n"
                            "    tree.body.extend(ast.parse('print(' + repr(witness) + ')').body)\n"
                            "    ast.fix_missing_locations(tree)\n", 1)
    script = script.replace("    if result.returncode != 0 or result.stdout.strip() != case['expected'].strip():\n",
                            "    lines = result.stdout.strip().splitlines()\n"
                            "    if not lines or lines[-1] != witness:\n"
                            "        raise AssertionError('실제 실행 상태의 검사까지 끝나야 해요.')\n"
                            "    output = '\\n'.join(lines[:-1]).strip()\n"
                            "    if result.returncode != 0 or output != case['expected'].strip():\n", 1)
    return script
