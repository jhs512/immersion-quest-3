"""Compile small, independent Python input variants into a lesson-owned checker."""
import json


def _output_checker(cases):
    if not isinstance(cases,list) or not 1 <= len(cases) <= 50:
        raise ValueError('준비 값 검사 사례를 확인하세요.')
    for case in cases:
        if set(case) != {'values','expected'} or not isinstance(case['expected'],str):
            raise ValueError('준비 값과 예상 출력을 확인하세요.')
        values = case['values']
        if not isinstance(values,dict) or not 1 <= len(values) <= 20 or any(not name.isascii() or not name.isidentifier() for name in values):
            raise ValueError('준비 자료 이름을 확인하세요.')
    payload = json.dumps(cases, ensure_ascii=False)
    return """import ast
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
                            encoding='utf-8', timeout=10)
    if result.returncode != 0 or result.stdout.strip() != case['expected'].strip():
        raise AssertionError('다른 준비 값에서도 같은 원리가 맞는지 확인하세요.')
print('준비 값을 바꾼 검사도 통과했어요.')
""".replace('PAYLOAD', repr(payload))


def checker(cases, probe=None):
    script = _output_checker(cases)
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
