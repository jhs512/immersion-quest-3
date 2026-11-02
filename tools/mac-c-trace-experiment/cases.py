import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
tool = ROOT / 'assets/c-trace/mac_c_flow.py'
root = Path(sys.argv[1]).resolve()
root.mkdir(parents=True, exist_ok=True)
checked = []


def run_case(name, source, stdin, status, expected_stdout=None):
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
        assert doc['verification']['grader_output_and_exit_match'], (name, doc)
        assert doc['trace'], (name, doc)
    checked.append({'case': name, 'status': doc['status'], 'steps': len(doc['trace'])})


run_case('scanf', '#include <stdio.h>\nint main(void) {\n int value;\n scanf("%d", &value);\n printf("%d\\n", value + 1);\n return 0;\n}\n', '8\n', 'ok', '9\n')
run_case('compile-error', 'int main(void) {\n int bad = ;\n}\n', '', 'compile_error')
run_case('crash', 'int main(void) {\n int *p = (int *)0;\n *p = 3;\n return 0;\n}\n', '', 'uncaught_exception')
run_case('infinite-loop', 'int main(void) {\n int n = 0;\n while (1) {\n n++;\n }\n}\n', '', 'step_limit')
run_case('file-name', '#include <stdio.h>\nint main(void) {\n puts(__FILE__);\n return 0;\n}\n', '', 'ok', 'main.c\n')
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
run_case('globals-static', '#include <stdio.h>\nint stock = 2;\nvoid bump(void) {\n static int calls = 0;\n calls++;\n stock++;\n}\nint main(void) {\n bump();\n bump();\n printf("%d\\n", stock);\n return 0;\n}\n', '', 'ok', '4\n')
global_doc = json.loads((root / 'globals-static/c_flow.json').read_text(encoding='utf-8'))
assert any(step['globals'].get('stock') == 4 for step in global_doc['trace']), global_doc
assert any(frame['encoded_locals'].get('calls') == 2 and 'calls' in frame['static_names'] for step in global_doc['trace'] for frame in step['stack_to_render']), global_doc

for lesson_path in sorted((ROOT / 'courses/redesigned').glob('engineer-c-*.json')):
    lesson_name = lesson_path.stem
    lesson = json.loads(lesson_path.read_text(encoding='utf-8'))
    tasks = [task for task in lesson['tasks'] if task.get('language') == 'c']
    for index, task in enumerate(tasks):
        for field in ['starter_code', 'solution']:
            source = task.get(field)
            if not source:
                continue
            inputs = list(dict.fromkeys(case.get('input', '') for case in task.get('tests', []))) or ['']
            for input_index, stdin in enumerate(inputs):
                case_name = f'{lesson_name}-{index}-{field}-{input_index}'
                case = root / case_name
                case.mkdir(exist_ok=True)
                (case / 'src.c').write_text(source, encoding='utf-8')
                (case / 'stdin.txt').write_text(stdin, encoding='utf-8')
                subprocess.run([sys.executable, str(tool), str(case)], check=True, timeout=110)
                doc = json.loads((case / 'c_flow.json').read_text(encoding='utf-8'))
                if field == 'solution':
                    assert doc['status'] == 'ok', (case_name, doc)
                    assert doc['verification']['grader_output_and_exit_match'], (case_name, doc)
                    assert doc['trace'], (case_name, doc)
                else:
                    assert doc['status'] in ('ok', 'compile_error', 'uncaught_exception', 'step_limit'), (case_name, doc)
                checked.append({'case': case_name, 'status': doc['status'], 'steps': len(doc['trace'])})

(root / 'summary.json').write_text(json.dumps(checked, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'checked': len(checked), 'all_expected': True, 'cases': checked}, ensure_ascii=False))
