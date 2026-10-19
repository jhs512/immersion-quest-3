"""Grade actual bar heights after running lesson-owned input variants."""
import json


def checker(cases):
    payload = json.dumps(cases, ensure_ascii=False)
    return '''import ast
import copy
import json
import secrets
import subprocess
import sys
from pathlib import Path

original = ast.parse(Path('main.py').read_text(encoding='utf-8'))
cases = json.loads(PAYLOAD)
for case in cases:
    tree = copy.deepcopy(original)
    assignments = [node for node in tree.body if isinstance(node, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == 'data' for t in node.targets)]
    if len(assignments) != 1:
        raise AssertionError('준비된 data 이름은 그대로 두세요.')
    assignments[0].value = ast.parse(repr(case['data']), mode='eval').body
    ast.fix_missing_locations(tree)
    setup = "import matplotlib; matplotlib.use('Agg')\\nimport matplotlib.pyplot as plt\\nplt.show = lambda *args, **kwargs: None\\n"
    probe = "\\nassert len(plt.get_fignums()) == 1, '그림 하나를 그리세요.'\\nax = plt.gcf().axes[0]\\nactual = [float(p.get_height()) for p in ax.patches]\\nexpected = " + repr(case['heights']) + "\\nassert len(actual) == len(expected) and all(abs(a-b) < 1e-8 for a,b in zip(actual,expected)), '막대가 나타내는 값을 확인하세요.'\\nassert [t.get_text() for t in ax.get_xticklabels()] == " + repr(case['labels']) + "\\n"
    witness = secrets.token_hex(24)
    completed = "\\nprint(" + repr(witness) + ")\\n"
    result = subprocess.run([sys.executable, '-I', '-X', 'utf8', '-c', setup + ast.unparse(tree) + probe + completed],
                            stdin=subprocess.DEVNULL, capture_output=True, text=True,
                            encoding='utf-8', timeout=20)
    if result.returncode or result.stdout.splitlines()[-1:] != [witness]:
        raise AssertionError('다른 준비 자료의 실제 막대 높이도 확인하세요.\\n' + result.stderr[-1500:])
print('실제 막대와 다른 준비 자료도 확인했어요.')
'''.replace('PAYLOAD', repr(payload))
