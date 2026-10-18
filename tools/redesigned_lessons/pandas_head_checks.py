"""Lesson-owned head(3) checker: compare tables, never pandas repr spacing."""


def checker():
    worker = '''import ast
import copy
import json
import sys
import pandas as pd

payload = json.loads(sys.stdin.read())
tree = ast.parse(payload['source'], filename='main.py')
found = False
for statement in tree.body:
    if isinstance(statement, ast.Assign) and any(isinstance(target, ast.Name) and target.id == 'delivery' for target in statement.targets):
        if not found:
            statement.value = ast.parse(repr(payload['delivery']), mode='eval').body
            found = True
if not found:
    raise AssertionError('준비 자료의 이름을 그대로 두세요.')
ast.fix_missing_locations(tree)
shown = []
def capture(*args, **kwargs):
    shown.append([value.copy(deep=True) if isinstance(value, pd.DataFrame) else value for value in args])
namespace = {'__name__': '__main__', 'print': capture}
exec(compile(tree, 'main.py', 'exec'), namespace)
original = pd.DataFrame(payload['delivery'])
if len(shown) != 1 or len(shown[0]) != 1 or not isinstance(shown[0][0], pd.DataFrame):
    raise AssertionError('앞부분의 표 하나를 출력해 보세요.')
if not shown[0][0].equals(original.head(3)):
    raise AssertionError('앞의 세 건을 확인하는지 살펴보세요.')
if not isinstance(namespace.get('df'), pd.DataFrame) or not namespace['df'].equals(original):
    raise AssertionError('원래 표는 그대로 두고 앞부분만 살펴보세요.')
print('HEAD_CHECK_COMPLETE')
'''
    return '''import json
import subprocess
import sys
from pathlib import Path

source = Path('main.py').read_text(encoding='utf-8')
for count in [4, 7, 1]:
    delivery = {'order_id': list(range(101, 101 + count)),
                'minutes': [12 + offset * 6 for offset in range(count)],
                'region': ['서울' if offset % 2 == 0 else '부산' for offset in range(count)]}
    result = subprocess.run([sys.executable, '-I', '-X', 'utf8', '-c', WORKER],
                            input=json.dumps({'source': source, 'delivery': delivery}),
                            capture_output=True, text=True, encoding='utf-8', timeout=10)
    if result.returncode != 0 or result.stdout.strip() != 'HEAD_CHECK_COMPLETE':
        raise AssertionError('앞의 세 건과 원래 표를 다른 자료에서도 확인해 보세요.')
print('표의 행과 값이 맞아요. 원래 자료도 유지했어요.')
'''.replace('WORKER', repr(worker))
