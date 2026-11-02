import json
from pathlib import Path
import subprocess
import sys
import tempfile
from decimal import Decimal
import platform
from concurrent.futures import ThreadPoolExecutor, as_completed


ROOT = Path(__file__).resolve().parents[2]
tool = ROOT / 'assets/c-trace/mac_c_flow.py'
root = Path(sys.argv[1]).resolve()
root.mkdir(parents=True, exist_ok=True)
checked = []


def record(name, doc):
    item = {'case': name, 'status': doc['status'], 'steps': len(doc['trace'])}
    checked.append(item)
    (root / 'summary.json').write_text(json.dumps(checked, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(item, ensure_ascii=False), flush=True)


def verify_grader(source, stdin, doc):
    with tempfile.TemporaryDirectory(prefix='mq-c-grader-') as temporary:
        path = Path(temporary)
        (path / 'main.c').write_text(source, encoding='utf-8')
        subprocess.run(['cc', '-std=c11', '-o', 'main', 'main.c'], cwd=path, check=True, capture_output=True, timeout=30)
        graded = subprocess.run([str(path / 'main')], cwd=path, input=stdin.encode(), capture_output=True, timeout=15)
        assert graded.returncode == doc['exit_code'], doc
        assert graded.stdout.decode('utf-8', 'replace').replace('\r\n', '\n') == doc['stdout'], doc


def run_case(name, source, stdin, status, expected_stdout=None, compare_grader=True):
    case = root / name
    case.mkdir(exist_ok=True)
    (case / 'src.c').write_text(source, encoding='utf-8')
    (case / 'stdin.txt').write_text(stdin, encoding='utf-8')
    subprocess.run([sys.executable, str(tool), str(case)], check=True, timeout=110)
    doc = json.loads((case / 'c_flow.json').read_text(encoding='utf-8'))
    assert doc['status'] == status, (name, doc)
    if expected_stdout is not None:
        assert doc['stdout'] == expected_stdout, (name, doc)
    if status == 'ok':
        assert doc['verification']['program_runs'] == 1, (name, doc)
        if compare_grader:
            verify_grader(source, stdin, doc)
        assert doc['trace'], (name, doc)
    record(name, doc)


run_case('scanf', '#include <stdio.h>\nint main(void) {\n int value;\n scanf("%d", &value);\n printf("%d\\n", value + 1);\n return 0;\n}\n', '8\n', 'ok', '9\n')
run_case('compile-error', 'int main(void) {\n int bad = ;\n}\n', '', 'compile_error')
run_case('crash', 'int main(void) {\n int *p = (int *)0;\n *p = 3;\n return 0;\n}\n', '', 'uncaught_exception')
run_case('infinite-loop', 'int main(void) {\n int n = 0;\n while (1) {\n n++;\n }\n}\n', '', 'step_limit')
run_case('file-name', '#include <stdio.h>\nint main(void) {\n puts(__FILE__);\n return 0;\n}\n', '', 'ok', 'main.c\n')
run_case('native-address', '#include <stdio.h>\n#include <unistd.h>\n#include <time.h>\nint main(void) {\n int value = 7;\n printf("%p %ld %ld\\n", (void *)&value, (long)getpid(), (long)time(NULL));\n return 0;\n}\n', '', 'ok', compare_grader=False)
address_doc = json.loads((root / 'native-address/c_flow.json').read_text(encoding='utf-8'))
assert address_doc['stdout'].startswith('0x'), address_doc
assert len(address_doc['stdout'].split()) == 3, address_doc
(root / 'single-side-effect').mkdir(exist_ok=True)
(root / 'single-side-effect/side-effect.txt').unlink(missing_ok=True)
run_case('single-side-effect', '#include <stdio.h>\nint main(void) {\n FILE *file = fopen("side-effect.txt", "a");\n fputs("once\\n", file);\n fclose(file);\n return 0;\n}\n', '', 'ok', '')
assert (root / 'single-side-effect/side-effect.txt').read_text(encoding='utf-8') == 'once\n'
run_case('nested-struct', 'struct Inner { int value; };\nstruct Outer { struct Inner inner; };\nint main(void) {\n struct Outer outer = {{7}};\n struct Outer *whole = &outer;\n int *field = &outer.inner.value;\n *field += 1;\n return 0;\n}\n', '', 'ok', '')
nested_doc = json.loads((root / 'nested-struct/c_flow.json').read_text(encoding='utf-8'))
found_nested = False
for step in nested_doc['trace']:
    for frame in step['stack_to_render']:
        local = frame['encoded_locals']
        if 'field' in local:
            assert local['whole'] == ['C_PTR', 'outer'], step
            assert local['field'] == ['C_PTR', 'outer.inner.value'], step
            outer = step['heap'][str(local['outer'][1])]
            inner_ref = next(value for name, value in outer[2:] if name == 'inner')
            assert inner_ref != local['outer'], step
            inner = step['heap'][str(inner_ref[1])]
            assert any(name == 'value' and value in (7, 8) for name, value in inner[2:]), step
            found_nested = True
assert found_nested, nested_doc
run_case('same-line-calls', '#include <stdio.h>\nint bump(void) {\n static int calls = 0;\n calls++;\n return calls;\n}\nint main(void) {\n int value = bump() + bump();\n printf("%d\\n", value);\n return 0;\n}\n', '', 'ok', '3\n')
calls_doc = json.loads((root / 'same-line-calls/c_flow.json').read_text(encoding='utf-8'))
call_ids = {frame['frame_id'] for step in calls_doc['trace'] if step['event'] == 'call' for frame in step['stack_to_render'] if frame['func_name'] == 'bump'}
assert len(call_ids) == 2, calls_doc
run_case('unreferenced-allocation', '#include <stdlib.h>\nint main(void) {\n void *value = malloc(5);\n value = 0;\n return 0;\n}\n', '', 'ok', '')
lost_doc = json.loads((root / 'unreferenced-allocation/c_flow.json').read_text(encoding='utf-8'))
assert any(any(obj[0] == 'INSTANCE' and ['바이트 수', 5] in obj for obj in step['heap'].values()) for step in lost_doc['trace']), lost_doc
run_case('long-double', '#include <stdio.h>\nint main(void) {\n long double value = 1.25L;\n printf("%.2Lf\\n", value);\n return 0;\n}\n', '', 'ok', '1.25\n')
long_double_doc = json.loads((root / 'long-double/c_flow.json').read_text(encoding='utf-8'))
assert any(frame['encoded_locals'].get('value', [None])[0] == 'SPECIAL_FLOAT' and Decimal(frame['encoded_locals']['value'][1]) == Decimal('1.25') for step in long_double_doc['trace'] for frame in step['stack_to_render']), long_double_doc
if platform.machine() == 'x86_64':
    run_case('long-double-range', '#include <stdio.h>\n#include <math.h>\nint main(void) {\n long double value = 1e400L;\n printf("%d\\n", isfinite(value));\n return 0;\n}\n', '', 'ok', '1\n')
    extended_doc = json.loads((root / 'long-double-range/c_flow.json').read_text(encoding='utf-8'))
    assert any(frame['encoded_locals'].get('value', [None])[0] == 'SPECIAL_FLOAT' and Decimal(frame['encoded_locals']['value'][1]).is_finite() and Decimal(frame['encoded_locals']['value'][1]) > Decimal('1e399') for step in extended_doc['trace'] for frame in step['stack_to_render']), extended_doc
run_case('int128', '#include <stdio.h>\nint main(void) {\n __int128 value = ((__int128)1) << 100;\n printf("%d\\n", value > 0);\n return 0;\n}\n', '', 'ok', '1\n')
wide_doc = json.loads((root / 'int128/c_flow.json').read_text(encoding='utf-8'))
wide_values = [frame['encoded_locals']['value'] for step in wide_doc['trace'] for frame in step['stack_to_render'] if 'value' in frame['encoded_locals']]
assert wide_values, wide_doc
for value in wide_values:
    assert isinstance(value, list) and value[0] in ('LONG', 'C_NOTE'), value
    if value[0] == 'LONG':
        assert int(value[1], 0) == 1 << 100, value
run_case('globals-static', '#include <stdio.h>\nextern int stock;\nvoid bump(void) {\n static int calls = 0;\n calls++;\n stock++;\n}\nint stock = 2;\nint main(void) {\n bump();\n bump();\n printf("%d\\n", stock);\n return 0;\n}\n', '', 'ok', '4\n')
global_doc = json.loads((root / 'globals-static/c_flow.json').read_text(encoding='utf-8'))
assert any(step['globals'].get('stock') == 4 for step in global_doc['trace']), global_doc
assert any(frame['encoded_locals'].get('calls') == 2 and 'calls' in frame['static_names'] for step in global_doc['trace'] for frame in step['stack_to_render']), global_doc

jobs = []
for lesson_path in sorted((ROOT / 'courses/redesigned').glob('*.json')):
    lesson_name = lesson_path.stem
    lesson = json.loads(lesson_path.read_text(encoding='utf-8'))
    tasks = [task for task in lesson.get('tasks', []) if task.get('language') == 'c']
    for index, task in enumerate(tasks):
        for field in ['starter_code', 'solution']:
            source = task.get(field)
            if not source:
                continue
            inputs = list(dict.fromkeys(case.get('input', '') for case in task.get('tests', []))) or ['']
            for input_index, stdin in enumerate(inputs):
                jobs.append((f'{lesson_name}-{index}-{field}-{input_index}', source, stdin, field))


def run_course(job):
    case_name, source, stdin, field = job
    case = root / case_name
    case.mkdir(exist_ok=True)
    (case / 'src.c').write_text(source, encoding='utf-8')
    (case / 'stdin.txt').write_text(stdin, encoding='utf-8')
    subprocess.run([sys.executable, str(tool), str(case)], check=True, timeout=110)
    doc = json.loads((case / 'c_flow.json').read_text(encoding='utf-8'))
    if field == 'solution':
        assert doc['status'] == 'ok', (case_name, doc)
        assert doc['verification']['program_runs'] == 1, (case_name, doc)
        verify_grader(source, stdin, doc)
        assert doc['trace'], (case_name, doc)
    else:
        assert doc['status'] in ('ok', 'compile_error', 'uncaught_exception', 'step_limit'), (case_name, doc)
    return case_name, doc


failures = []
with ThreadPoolExecutor(max_workers=2) as executor:
    pending = {executor.submit(run_course, job): job[0] for job in jobs}
    for future in as_completed(pending):
        try:
            name, doc = future.result()
            record(name, doc)
        except Exception as error:
            failures.append({'case': pending[future], 'error': str(error)[:2000]})
            (root / 'failures.json').write_text(json.dumps(failures, ensure_ascii=False, indent=2), encoding='utf-8')
            print(json.dumps({'failed': pending[future], 'error': str(error)[:200]}, ensure_ascii=False), flush=True)

(root / 'summary.json').write_text(json.dumps(checked, ensure_ascii=False, indent=2), encoding='utf-8')
assert not failures, failures
print(json.dumps({'checked': len(checked), 'all_expected': True, 'cases': checked}, ensure_ascii=False))
