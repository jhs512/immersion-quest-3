"""Run every fixture through native_flow.py (run and trace) and assert what the trace must show.

    python check_fixtures.py <work dir> [--docker IMAGE]

Without --docker the host compilers run (MQ_CXX, MQ_RUSTC, MQ_LLDB as native_flow.py reads them).
Writes <work dir>/report.json and exits non-zero when any check fails.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import uuid

HERE = Path(__file__).resolve().parent
TOOL = HERE.parent.parent / 'assets' / 'native-trace'
MOVED = '옮겨진 값(move)'


def invoke(mode, case, language, image):
    if image:
        name = f'mq-native-check-{uuid.uuid4().hex[:12]}'
        command = ['docker', 'run', '--rm', '-i', '--name', name, '--label', 'mq.owner=mq-native-trace',
                   '--network', 'none', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges',
                   '--memory', '512m', '--pids-limit', '128', '--cpus', '2',
                   '-v', f'{TOOL}:/tool:ro', '-v', f'{case}:/case', image,
                   'python3', '/tool/native_flow.py', mode, '/case', language]
    else:
        name, command = None, [sys.executable, str(TOOL / 'native_flow.py'), mode, str(case), language]
    try:
        with open(case / 'stdin.txt', 'rb') as stdin:
            return subprocess.run(command, stdin=stdin, capture_output=True, timeout=150, env=dict(os.environ, MSYS_NO_PATHCONV='1'))
    except subprocess.TimeoutExpired:
        if name:
            subprocess.run(['docker', 'rm', '-f', name], capture_output=True)
        raise


def frames(doc):
    return [(step, frame) for step in doc['trace'] for frame in step['stack_to_render']]


def resolve(step, value):
    if isinstance(value, list) and value and value[0] == 'REF':
        return step['heap'][str(value[1])]
    return value


def local(doc, name, line=None):
    return [(step, frame['encoded_locals'][name]) for step, frame in frames(doc)
            if name in frame['encoded_locals'] and (line is None or step['line'] == line)]


def moved(value):
    return isinstance(value, list) and value[:1] == ['C_NOTE'] and MOVED in value[1]


def checks_ownership(doc):
    yield 'first is moved once line 17 ran', all(moved(v) for s, v in local(doc, 'first') if s['line'] >= 18 and s['func_name'] == 'main')
    yield 'first is a live String before the move', any(resolve(s, v) == ['STRING', 'pen'] for s, v in local(doc, 'first', 17))
    yield 'owned is moved while take runs', all(moved(v) for s, v in local(doc, 'owned') if s['func_name'] == 'take')
    yield 'take receives the Item', any(resolve(s, v)[0] == 'INSTANCE' for s, v in local(doc, 'item') if s['func_name'] == 'take')
    yield 'copy is moved into the Vec', any(moved(v) for s, v in local(doc, 'copy', 21))


def checks_edge_rs(doc):
    yield 'char is a CHAR', any(v == ['CHAR', 'R'] for _, v in local(doc, 'letter'))
    yield 'i128 is exact', any(v == ['LONG', '-170141183460469231731687303715884105728'] for _, v in local(doc, 'huge'))
    yield 'reference to a field names it', any(v == ['C_PTR', 'order.counts'] for _, v in local(doc, 'counts'))
    yield 'moved in loop body, then reassigned', (any(moved(v) for _, v in local(doc, 'name', 32))
                                                 and any(resolve(s, v) == ['STRING', 'a0'] for s, v in local(doc, 'name', 30)))
    yield 'partial move marks only the field', any(
        resolve(s, v)[0] == 'INSTANCE' and moved(dict(resolve(s, v)[2:])['label']) for s, v in local(doc, 'order', 25))
    yield 'compiler-made iter is hidden', not local(doc, 'iter')
    yield 'derived Debug code is not a frame', not any('fmt' in f['func_name'] for _, f in frames(doc))
    yield 'shadowed binding is labelled', any(any(k.startswith('x · 가려짐') for k in f['encoded_locals']) for _, f in frames(doc))
    yield 'recursion has three depth frames', any(sum(f['func_name'] == 'depth' for f in s['stack_to_render']) == 3 for s in doc['trace'])
    yield 'same-line calls get distinct frames', len({f['frame_id'] for _, f in frames(doc) if f['func_name'] == 'add'}) == 3
    yield 'closure captured by move', any(moved(v) for s, v in local(doc, 'note', 47))


def checks_lifetime(doc):
    yield 'reference names its target', any(v == ['C_PTR', 'stock'] for _, v in local(doc, 'alias'))
    yield 'deleted pointer is freed memory', any(isinstance(v, list) and v[0] == 'C_NOTE' and '해제된' in v[1] for _, v in local(doc, 'raw', 30))
    yield 'constructor sees this', any('this' in f['encoded_locals'] for _, f in frames(doc) if f['func_name'] == 'Box::Box')
    yield 'destructors run as calls', sum(1 for s in doc['trace'] if s['func_name'] == 'Box::~Box' and s['event'] == 'call') == 3
    yield 'vector shows its elements', any(resolve(s, v)[2:] == [1, 2, 3, 4] for s, v in local(doc, 'values', 22))
    yield 'unique_ptr points at the heap Box', any(resolve(s, v)[0] == 'INSTANCE' for s, v in local(doc, 'owned', 24))
    yield 'long double is SPECIAL_FLOAT', any(v == ['SPECIAL_FLOAT', '1.5'] for _, v in local(doc, 'wide', 32))


def checks_edge_cpp(doc):
    nodes = [(s, resolve(s, v)) for s, v in local(doc, 'a', 31)]
    yield 'cycle a.next -> b', any(dict(n[2:]).get('next') == ['C_PTR', 'b'] for _, n in nodes)
    yield 'nested first field keeps its own name', any(v == ['C_PTR', 'pair.first'] for _, v in local(doc, 'inner'))
    yield 'same-line calls', any(v == 10 for _, v in local(doc, 'level', 35))
    yield 'NaN is SPECIAL_FLOAT', any(isinstance(v, list) and v[0] == 'SPECIAL_FLOAT' and 'nan' in v[1].lower() for _, v in local(doc, 'nan', 38))
    yield 'moved-from unique_ptr is null', any(v is None for _, v in local(doc, 'first', 39))
    yield 'moved-from vector is empty', any(resolve(s, v)[2:] == [] for s, v in local(doc, 'source', 41))
    yield 'dangling pointer is freed memory', any(isinstance(v, list) and '해제된' in str(v) for _, v in local(doc, 'dangling', 43))
    yield 'uninitialized local is badged', any('unset' in f.get('declared_without_initializer', []) for _, f in frames(doc))


CASES = [
    ('ownership.rs', 'rust', 'ok', checks_ownership),
    ('edge.rs', 'rust', 'ok', checks_edge_rs),
    ('moved_error.rs', 'rust', 'compile_error', lambda d: [('E0382 at line 4', any(p['line'] == 4 for p in d['problems']))]),
    ('panic.rs', 'rust', 'uncaught_exception', lambda d: [('output before the panic', d['stdout'] == 'before\n')]),
    ('forever.rs', 'rust', 'step_limit', lambda d: [('stopped by the budget', len(d['trace']) > 0)]),
    ('lifetime.cpp', 'cpp', 'ok', checks_lifetime),
    ('edge.cpp', 'cpp', 'ok', checks_edge_cpp),
    ('throw.cpp', 'cpp', 'uncaught_exception', lambda d: [('stopped at the throw', any(s['line'] == 4 for s in d['trace']))]),
    ('broken.cpp', 'cpp', 'compile_error', lambda d: [('error at line 2', any(p['line'] == 2 for p in d['problems']))]),
]


def main():
    work = Path(sys.argv[1]).resolve()
    image = sys.argv[sys.argv.index('--docker') + 1] if '--docker' in sys.argv else None
    report, failed = [], 0
    for fixture, language, status, checks in CASES:
        case = work / fixture
        shutil.rmtree(case, ignore_errors=True)
        case.mkdir(parents=True)
        shutil.copy(HERE / 'fixtures' / fixture, case / 'src')
        (case / 'stdin.txt').write_bytes(b'')
        traced = invoke('trace', case, language, image)
        entry = {'fixture': fixture, 'trace_exit': traced.returncode, 'trace_stderr': traced.stderr.decode('utf-8', 'replace')[-800:]}
        if not (case / 'native_flow.json').is_file():
            entry['checks'] = {'trace document written': False}
        else:
            doc = json.loads((case / 'native_flow.json').read_text(encoding='utf-8'))
            results = {'status ' + status: doc['status'] == status}
            if status != 'compile_error':
                results['one program run'] = doc.get('verification', {}).get('program_runs') == 1
                results['original source unchanged'] = doc.get('verification', {}).get('original_source') is True
            if status == 'ok':
                ran = invoke('run', case, language, image)
                results['run output equals trace output'] = ran.returncode == 0 and ran.stdout.decode('utf-8').replace('\r\n', '\n') == doc['stdout']
            for name, passed in checks(doc):
                results[name] = bool(passed)
            entry.update(status=doc['status'], steps=len(doc['trace']), checks=results)
        failed += sum(not v for v in entry['checks'].values())
        report.append(entry)
        print(fixture, entry.get('status'), entry.get('steps'), ' '.join(('PASS ' if v else 'FAIL ') + k for k, v in entry['checks'].items() if not v) or 'all pass', flush=True)
    (work / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'{failed} failed checks')
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
