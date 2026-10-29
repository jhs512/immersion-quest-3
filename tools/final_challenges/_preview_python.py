"""Author aid for Python final challenges: run a spec's narration snapshots, tests and prepared cases locally.

Uses the same interpreter the debug player uses (target/ml-env). The real evidence is still
examples/validate_redesigned_lesson.rs; this only shows actual outputs while writing a spec.
    python tools/final_challenges/_preview_python.py aice-join
"""
import ast
import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PYTHON = ROOT / ('target/ml-env/Scripts/python.exe' if sys.platform == 'win32' else 'target/ml-env/bin/python')
sys.path.insert(0, str(Path(__file__).parent))


FILES = {}


def run(source, stdin=''):
    import os
    import tempfile
    with tempfile.TemporaryDirectory() as folder:
        for name, body in FILES.items():
            Path(folder, name).write_text(body, encoding='utf-8')
        Path(folder, 'main.py').write_text(source, encoding='utf-8')
        environment = dict(os.environ, MPLBACKEND='Agg', TF_CPP_MIN_LOG_LEVEL='3')
        result = subprocess.run([str(PYTHON), '-X', 'utf8', 'main.py'], input=stdin, capture_output=True, text=True,
                                cwd=folder, encoding='utf-8', timeout=300, env=environment)
    return result.returncode, result.stdout.rstrip(), result.stderr.strip()[-600:]


def replaced(source, values):
    tree = ast.parse(source)
    left = set(values)
    for statement in tree.body:
        if isinstance(statement, ast.Assign):
            for target in statement.targets:
                if isinstance(target, ast.Name) and target.id in left:
                    statement.value = ast.parse(repr(values[target.id]), mode='eval').body
                    left.discard(target.id)
    assert not left, left
    return ast.unparse(ast.fix_missing_locations(tree))


def main(key):
    spec_path = Path(__file__).parent / (key.replace('-', '_') + '.py')
    module_spec = importlib.util.spec_from_file_location('spec', spec_path)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    spec, script = module.SPEC, getattr(module, 's', None)
    task = spec['task']
    FILES.update(task.get('files') or {})
    stdin = task['tests'][0]['input'] if task.get('tests') else ''
    if script is not None:
        source, snapshot = task['starter_code'], 0
        for action in task['narration']:
            if action['action'] == 'set_input':
                stdin = action['value']
            if action['action'] == 'run':
                code, out, err = run(script.snapshots[snapshot], stdin)
                print(f'--- run {snapshot + 1} (exit {code})\n{out}' + (f'\n!! {err}' if code else ''))
                snapshot += 1
    for name, source in (('starter', task['starter_code']), ('solution', task['solution'])):
        for case in task.get('tests', []):
            code, out, err = run(source, case['input'])
            print(f'=== {name} test: {"PASS" if code == 0 and out == case["expected"].strip() else "fail"}' + ('' if out == case['expected'].strip() else f'\n{out}\n!! {err}'))
        for case in spec.get('prepared_cases', []):
            code, out, err = run(replaced(source, case['values']))
            ok = code == 0 and out == case['expected'].strip()
            print(f'=== {name} prepared {list(case["values"])}: {"PASS" if ok else "fail"}' + ('' if ok else f'\n{out}\n!! {err}'))
    for kind, rows in (('reject', spec.get('cases', {}).get('reject', [])), ('accept', spec.get('cases', {}).get('accept', []))):
        for replacements, reason in rows:
            source = task['solution']
            for before, after in replacements:
                assert source.count(before) == 1, (kind, reason, before)
                source = source.replace(before, after, 1)
            results = [run(source, c['input']) for c in task.get('tests', [])] + [run(replaced(source, c['values'])) for c in spec.get('prepared_cases', [])]
            expected = [c['expected'].strip() for c in task.get('tests', [])] + [c['expected'].strip() for c in spec.get('prepared_cases', [])]
            passed = all(r[0] == 0 and r[1] == e for r, e in zip(results, expected))
            print(f'{kind} {"OK" if passed == (kind == "accept") else "WRONG"}: {reason}')


if __name__ == '__main__':
    main(sys.argv[1])
