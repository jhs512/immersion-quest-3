"""C++ code-flow experiment check (NOT part of the app; MQ has no C++ course or grader).

For each case: build with the installed MSVC (build_cpp.cmd), run the program normally to get its real
output, trace it under the Windows debugger (cpp_trace.py), and check the trace against facts of that real
run and of the source -- not against a stored copy of an earlier trace:
  - the trace's final output equals the normal run's output, and the status matches how the run ended;
  - a local is never drawn before its declaration line (no garbage shown as an object, e.g. an empty vector);
  - object lifetime and dispatch facts named per case below.
usage: python -I -X utf8 check.py      (Windows, VS 2022 BuildTools with MSVC; about 15 s)
"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def run_case(name, normal_run=True):
    case = os.path.join(HERE, 'cases', name)
    subprocess.run(['cmd', '/c', os.path.join(HERE, 'build_cpp.cmd'), case], check=True, capture_output=True, timeout=180)
    # The uncaught case is not run normally: the debug CRT would stop at its abort() dialog.
    normal = subprocess.run([os.path.join(case, 'main_cpp.exe')], capture_output=True, timeout=20, creationflags=0x08000000) if normal_run else None
    subprocess.run([sys.executable, '-I', '-X', 'utf8', os.path.join(HERE, 'cpp_trace.py'), 'main_cpp.exe', 'main.cpp', 'stdin.txt', 'trace.json'],
                   cwd=case, check=True, capture_output=True, timeout=120)
    doc = json.load(open(os.path.join(case, 'trace.json'), encoding='utf-8'))
    for f in ('main_cpp.exe', 'main_cpp.pdb', 'main.obj', 'mq_unbuffered.obj'):
        try: os.remove(os.path.join(case, f))
        except OSError: pass
    return doc, normal


def frames(step): return step['stack_to_render']
def names(step): return [f['func_name'] for f in frames(step)]


def main():
    failures = []
    def expect(ok, what):
        print(('PASS ' if ok else 'FAIL ') + what)
        if not ok: failures.append(what)

    for name in ('counter-vector', 'inherit-virtual-catch'):
        doc, normal = run_case(name)
        out = normal.stdout.decode('utf-8', 'replace').replace('\r\n', '\n')
        expect(doc['status'] == 'ok' and normal.returncode == 0, f'{name}: finished normally')
        expect(doc['stdout'].replace('\r\n', '\n') == out, f'{name}: trace output equals the normal run ({out!r})')
        src = open(os.path.join(HERE, 'cases', name, 'main.cpp'), encoding='utf-8').read().split('\n')
        drawn_early = []
        for s in doc['trace']:
            for f in frames(s):
                for var, val in f['encoded_locals'].items():
                    decl = next((i + 1 for i, l in enumerate(src) if f' {var}' in l and ('=' in l or '(' in l or '{' in l) and l.strip().startswith(('int ', 'Counter ', 'Square ', 'Shape ', 'std::', 'Counter *', 'const '))), None)
                    if decl and f['line'] <= decl and isinstance(val, list) and val[:1] == ['REF']:
                        drawn_early.append((var, f['line']))
        expect(not drawn_early, f'{name}: no local drawn as an object before its declaration {drawn_early[:3]}')

    doc, _ = run_case('counter-vector')
    vec = [o for s in doc['trace'] for o in s['heap'].values() if o[0] == 'COLLECTION' and o[1].startswith('std::vector')]
    expect(any(o[2] == [1, 2] for o in vec) and any(o[2] == [1, 2, 14] for o in vec), 'counter-vector: vector [1, 2] then [1, 2, 14] after push_back')
    expect(not any(o[2] == [] for o in vec), 'counter-vector: never shown as an empty vector (before construction it is not drawn)')
    add = [s for s in doc['trace'] if names(s)[-1:] == ['Counter::add'] and s['event'] == 'return']
    expect(bool(add) and frames(add[0])[-1]['encoded_locals'].get('__return__') == 7, 'counter-vector: Counter::add returns 7')

    doc, _ = run_case('inherit-virtual-catch')
    calls = [names(s)[-1] for s in doc['trace'] if s['event'] == 'call']
    expect('Square::area' in calls and 'Shape::area' in calls, 'inherit-virtual-catch: virtual call reaches Square::area and Shape::area')
    expect(['Square::Square', 'Shape::Shape'] == [c for c in calls if c in ('Square::Square', 'Shape::Shape')][:2], 'inherit-virtual-catch: Square() runs, then its Shape base')
    expect(any(s['event'] == 'exception' for s in doc['trace']) and any(n.endswith('· catch') for s in doc['trace'] for n in names(s)), 'inherit-virtual-catch: throw then the catch handler')
    expect(calls.count('Shape::~Shape') == 2, 'inherit-virtual-catch: two Shape destructors at the end of main')

    doc, _ = run_case('uncaught', normal_run=False)
    expect(doc['status'] == 'uncaught_exception', 'uncaught: the trace ends in an uncaught exception')
    expect(doc['stdout'].replace('\r\n', '\n') == 'before\n', 'uncaught: only the printf before the throw ran (source line 12)')
    expect(names(doc['trace'][-1]) == ['main', 'fail'], 'uncaught: stopped inside fail()')
    print('FAILED' if failures else 'ALL PASSED', len(failures))
    sys.exit(1 if failures else 0)


if __name__ == '__main__':
    main()
