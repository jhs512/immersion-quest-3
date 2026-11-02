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

for lesson_name in ['functions', 'pointers', 'structures', 'double-pointers']:
    lesson = json.loads((ROOT / 'courses/redesigned' / f'engineer-c-{lesson_name}.json').read_text(encoding='utf-8'))
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
