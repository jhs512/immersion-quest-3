"""Compile with the grader's cc, then ask the native LLDB to record original memory."""
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys


def declarations(compiler, path, source):
    run = subprocess.run([compiler, '-std=c11', '-Xclang', '-ast-dump=json', '-fsyntax-only', path.name], cwd=path.parent, capture_output=True, timeout=15)
    if run.returncode:
        return {}
    data = source.encode('utf-8')
    found = {}
    def visit(node):
        if node.get('kind') == 'VarDecl':
            loc = node.get('loc', {})
            offset, name = loc.get('offset'), node.get('name', '')
            if isinstance(offset, int) and not loc.get('includedFrom') and data[offset:offset + len(name)] == name.encode():
                line = data[:offset].count(b'\n') + 1
                key = f'{line}:{name}'
                found.setdefault(key, []).append('init' in node)
        for child in node.get('inner', []):
            visit(child)
    try:
        visit(json.loads(run.stdout))
    except (ValueError, RecursionError):
        return {}
    return {key: values[0] for key, values in found.items() if len(values) == 1}


def main(case):
    case = Path(case).resolve()
    original = (case / 'src.c').read_bytes()
    source = original.decode('utf-8')
    (case / 'main.c').write_bytes(original)
    compiler = os.environ.get('MQ_CC', 'cc')
    built = subprocess.run([compiler, '-std=c11', '-g', '-O0', '-o', 'main', 'main.c'], cwd=case, capture_output=True, timeout=30)
    path = case / 'c_flow.json'
    if built.returncode:
        text = built.stderr.decode('utf-8', 'replace')
        problems = [{'line': int(m.group(1)), 'error': True, 'message': m.group(2)}
                    for m in re.finditer(r'main\.c:(\d+):\d+: (?:fatal )?error: ([^\n]+)', text)]
        doc = {'code': source, 'language': 'c', 'status': 'compile_error', 'trace': [],
               'problems': problems or [{'line': 0, 'error': True, 'message': text[-500:]}]}
        path.write_text(json.dumps(doc, ensure_ascii=False), encoding='utf-8')
        return
    (case / 'declarations.json').write_text(json.dumps(declarations(compiler, case / 'main.c', source)), encoding='utf-8')
    run = subprocess.run(['xcrun', 'lldb', '-b', '-Q',
                          '-o', 'command script import ' + shlex.quote(str(Path(__file__).with_name('mac_lldb.py'))),
                          '-o', 'mq-c-trace ' + shlex.quote(str(case))], capture_output=True, timeout=75)
    if run.returncode or not path.is_file():
        raise RuntimeError('LLDB 추적 실패: ' + (run.stdout + run.stderr).decode('utf-8', 'replace')[-1500:])
    doc = json.loads(path.read_text(encoding='utf-8'))
    doc['verification'] = {'original_source': True, 'same_compiler': compiler,
                           'native_debugger': 'LLDB', 'debug_flags': ['-g', '-O0'],
                           'program_runs': doc.pop('program_runs', 0)}
    path.write_text(json.dumps(doc, ensure_ascii=False), encoding='utf-8')


if __name__ == '__main__':
    main(sys.argv[1])
