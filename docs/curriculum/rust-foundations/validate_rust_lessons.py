"""Validate authored Rust lessons with the real rustc until the app runner speaks `rust`.

Mirrors examples/validate_redesigned_lesson.rs for one language: the starter must fail the
grader, the solution must pass, the narration replay must produce the recorded outputs, rejected
answers must fail and accepted ones must pass. The grading contract it implements is the one the
runtime must adopt (handoff.md, "Rust 콘텐츠 계약").

    python docs/curriculum/rust-foundations/validate_rust_lessons.py [rust-values ...] [--evidence]
"""
import argparse
import json
import platform
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = Path(__file__).resolve().parent / 'evidence'
LESSONS = {
    'rust-values': 'rust_values',
    'rust-flow-functions': 'rust_flow_functions',
    'rust-ownership-borrowing': 'rust_ownership_borrowing',
    'rust-data-results': 'rust_data_results',
}
REPLAYED = {'patch_code', 'set_code', 'run', 'say', 'submit'}


def run(source, stdin=''):
    """Compile main.rs with the 2024 edition and run it, as the runner contract requires."""
    with tempfile.TemporaryDirectory(prefix='mq-rust-') as temp:
        folder = Path(temp)
        (folder / 'main.rs').write_text(source, encoding='utf-8', newline='\n')
        binary = folder / ('main.exe' if platform.system() == 'Windows' else 'main')
        built = subprocess.run(['rustc', '--edition=2024', '-o', str(binary), 'main.rs'], cwd=folder,
                               capture_output=True, text=True, encoding='utf-8', timeout=60)
        if built.returncode != 0:
            return {'success': False, 'stdout': '', 'stderr': built.stderr, 'state': 'compile_error'}
        try:
            done = subprocess.run([str(binary)], cwd=folder, input=stdin, capture_output=True, text=True,
                                  encoding='utf-8', timeout=15)
        except subprocess.TimeoutExpired:
            return {'success': False, 'stdout': '', 'stderr': 'timeout', 'state': 'timeout'}
        return {'success': done.returncode == 0, 'stdout': done.stdout.replace('\r\n', '\n'),
                'stderr': built.stderr + done.stderr, 'state': 'finished' if done.returncode == 0 else 'runtime_error'}


def skip_literal(text, i):
    """Index just past a comment or string starting at i, or None when none starts there."""
    if text.startswith('//', i):
        end = text.find('\n', i)
        return len(text) if end < 0 else end
    if text.startswith('/*', i):
        end = text.find('*/', i + 2)
        return len(text) if end < 0 else end + 2
    if text[i] == '"':
        j = i + 1
        while j < len(text) and text[j] != '"':
            j += 2 if text[j] == '\\' else 1
        return j + 1
    return None


LET = re.compile(r'\blet\s+(?:mut\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*(?::[^=;]+)?=(?!=)')


def mutate_rust(source, name, value):
    """Replace the initializer of the first `let [mut] name[: T] = ...;` outside comments and strings."""
    i = 0
    while i < len(source):
        skipped = skip_literal(source, i)
        if skipped is not None:
            i = skipped
            continue
        match = LET.match(source, i)
        if match and (i == 0 or not (source[i - 1].isalnum() or source[i - 1] == '_')) and match[1] == name:
            begin = end = match.end()
            depth = 0
            while end < len(source):
                skipped = skip_literal(source, end)
                if skipped is not None:
                    end = skipped
                    continue
                char = source[end]
                if char in '([{':
                    depth += 1
                elif char in ')]}':
                    depth -= 1
                elif char == ';' and depth == 0:
                    return source[:begin] + ' ' + value.strip() + source[end:]
                end += 1
            return None
        i += 1
    return None


def check(task, source):
    """The grader: every test's trimmed stdout, then each prepared-value variation."""
    cases = []
    for test in task['tests']:
        result = run(source, test.get('input', ''))
        passed = result['success'] and result['stdout'].rstrip('\n') == test['expected'].rstrip('\n')
        cases.append({'case': 'test', 'expected': test['expected'], 'stdout': result['stdout'],
                      'state': result['state'], 'passed': passed})
    if all(case['passed'] for case in cases):
        for variation in task.get('variations', []):
            changed = source
            for name, value in variation['values'].items():
                changed = mutate_rust(changed, name, value) if changed is not None else None
            if changed is None:
                cases.append({'case': f"variation {variation['values']}", 'state': 'concept_error', 'passed': False})
                continue
            result = run(changed)
            passed = result['success'] and result['stdout'].rstrip('\n') == variation['expected'].rstrip('\n')
            cases.append({'case': f"variation {variation['values']}", 'expected': variation['expected'],
                          'stdout': result['stdout'], 'state': result['state'], 'passed': passed})
    return {'passed': bool(cases) and all(case['passed'] for case in cases), 'cases': cases}


def code_lines(source):
    return [line.rstrip() for line in source.splitlines() if line.strip() and not line.strip().startswith('//')]


def replace_once(source, before, after, label):
    if source.count(before) != 1:
        raise AssertionError(f'{label}: replacement must match exactly once: {before!r}')
    return source.replace(before, after, 1)


def validate_task(label, task, expected_outputs):
    if task.get('language') != 'rust':
        raise AssertionError(f'{label}: language must be rust')
    if task.get('code_flow'):
        raise AssertionError(f'{label}: 코드 흐름 보기 is not proven for Rust')
    starter = check(task, task['starter_code'])
    if starter['passed']:
        raise AssertionError(f'{label}: starter already passes')
    solved = check(task, task['solution'])
    if not solved['passed']:
        raise AssertionError(f'{label}: solution failed: {json.dumps(solved, ensure_ascii=False)}')
    warning = run(task['solution'])['stderr']
    if 'warning' in warning:
        raise AssertionError(f'{label}: solution compiles with a warning: {warning[:300]}')
    lines = code_lines(task['solution'])
    comments = sum(1 for line in task['solution'].splitlines() if line.strip().startswith('//'))
    if comments * 3 < len([line for line in lines if line.strip() not in ('{', '}', '};')]):
        raise AssertionError(f'{label}: solution needs a comment every two or three code lines')
    source, outputs = task['starter_code'], []
    for action in task['narration']:
        kind = action['action']
        if kind not in REPLAYED:
            raise AssertionError(f'{label}: narration action {kind} is not replayable for Rust')
        if kind == 'patch_code':
            source = replace_once(source, action['before'], action['after'], label)
        elif kind == 'set_code':
            source = action['code']
        elif kind == 'run':
            first, last = action['lines']
            marked = source.splitlines()[first - 1:last]
            if 'expect_error' not in action and not any('print' in line for line in marked):
                raise AssertionError(f'{label}: run highlight {action["lines"]} does not show an output line')
            result = run(source, task['tests'][0].get('input', '') if task['tests'] else '')
            if 'expect_error' in action:
                if result['success'] or action['expect_error'] not in result['stderr']:
                    raise AssertionError(f"{label}: expected {action['expect_error']}, got {result['stderr'][:300]}")
            elif not result['success']:
                raise AssertionError(f"{label}: teacher run failed: {result['stderr'][:400]}")
            outputs.append(result['stdout'].rstrip())
    if outputs != expected_outputs:
        raise AssertionError(f'{label}: narration outputs {outputs!r} != recorded {expected_outputs!r}')
    if code_lines(source) != code_lines(task['solution']):
        raise AssertionError(f'{label}: the narration does not end on the solution code')
    return {'id': task['id'], 'teacher_outputs': outputs, 'starter_cases': len(starter['cases']),
            'grading_cases': len(solved['cases'])}


def validate(key, record=False):
    folder = ROOT / 'tools/redesigned_lessons' / LESSONS[key]
    tasks = json.loads((folder / 'content.json').read_text(encoding='utf-8'))['tasks']
    spec_path = ROOT / 'tests/lesson-cases' / f'{key}.json'
    spec = json.loads(spec_path.read_text(encoding='utf-8'))
    if len(spec['expected_outputs']) != len(tasks):
        raise AssertionError(f'{key}: expected_outputs has {len(spec["expected_outputs"])} steps for {len(tasks)} tasks')
    steps = []
    for index, task in enumerate(tasks):
        steps.append(validate_task(f'{key} step {index + 1}', task, spec['expected_outputs'][index]))
    counter = []
    for kind, wanted in (('reject', False), ('accept', True)):
        for answer in spec.get(kind, []):
            task = tasks[answer['step'] - 1]
            source = task['solution']
            for before, after in answer['replacements']:
                source = replace_once(source, before, after, f"{key} {kind} {answer['reason']}")
            report = check(task, source)
            if report['passed'] != wanted:
                raise AssertionError(f"{key} step {answer['step']}: {kind} '{answer['reason']}' passed={report['passed']}")
            counter.append({'step': answer['step'], kind: answer['reason']})
    missing = [index + 1 for index in range(len(tasks)) if not any(r['step'] == index + 1 for r in spec.get('reject', []))]
    if missing:
        raise AssertionError(f'{key}: steps without a rejected shortcut answer: {missing}')
    return {'lesson': key, 'steps': steps, 'counterexamples': counter}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('lessons', nargs='*', help=', '.join(LESSONS))
    parser.add_argument('--evidence', action='store_true', help='write evidence/<key>-<os>.json')
    args = parser.parse_args()
    unknown = set(args.lessons) - set(LESSONS)
    if unknown:
        parser.error(f'unknown lessons: {sorted(unknown)}')
    version = subprocess.check_output(['rustc', '--version'], text=True).strip()
    failed = False
    for key in args.lessons or LESSONS:
        try:
            result = validate(key)
        except AssertionError as error:
            failed = True
            print(f'FAIL {error}')
            continue
        result.update(platform=platform.platform(), rustc=version)
        print(f"PASS {key}: {len(result['steps'])} steps, {len(result['counterexamples'])} counterexamples")
        if args.evidence:
            EVIDENCE.mkdir(exist_ok=True)
            name = f"{key}-{platform.system().lower()}.json"
            (EVIDENCE / name).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
