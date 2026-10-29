"""Small builders for conversion specs. Line numbers are computed from the code, never typed."""


def line_of(code, needle, nth=1):
    found = 0
    for number, text in enumerate(code.splitlines(), 1):
        if needle in text:
            found += 1
            if found == nth:
                return number
    raise ValueError(f'line not found: {needle!r}')


def say(text, target):
    return {'action': 'say', 'text': text, 'target': target}


def patch(before, after, spoken):
    return {'action': 'patch_code', 'before': before, 'after': after, 'say': spoken}


def run(code, first, last=None):
    """Run while highlighting the print lines that the next sentence reads (in `code` as it is then)."""
    a = line_of(code, first)
    b = line_of(code, last) if last else a
    return {'action': 'run', 'lines': [a, b]}


def run_error(code, first, error, last=None):
    action = run(code, first, last)
    action['expect_error'] = error
    return action


def set_input(value):
    return {'action': 'set_input', 'value': value}


def apply_patches(code, actions):
    """The code after the narration's patches, to compute later line numbers."""
    for action in actions:
        if action['action'] == 'patch_code':
            if code.count(action['before']) != 1:
                raise ValueError(f"patch not unique: {action['before']!r}")
            code = code.replace(action['before'], action['after'], 1)
    return code


def todo(*items):
    return '**할 일**\n\n' + '\n'.join(f'{i}. {item}' for i, item in enumerate(items, 1))


class Script:
    """A narration written in order: patches update the code that later highlights are computed on."""

    def __init__(self, code):
        self.code = code
        self.actions = []

    def say(self, text, target):
        self.actions.append(say(text, target))
        return self

    def patch(self, before, after, spoken):
        if self.code.count(before) != 1:
            raise ValueError(f'patch not unique: {before!r}')
        self.code = self.code.replace(before, after, 1)
        self.actions.append(patch(before, after, spoken))
        return self

    def run(self, first, last=None, error=None):
        action = run(self.code, first, last)
        if error:
            action['expect_error'] = error
        self.actions.append(action)
        return self

    def input(self, value):
        self.actions.append(set_input(value))
        return self


def _sql_statements(sql):
    import sqlite3
    pending = ''
    for char in sql:
        pending += char
        if char == ';' and sqlite3.complete_statement(pending):
            yield pending
            pending = ''
    if pending.strip() and not all(l.strip().startswith('--') or not l.strip() for l in pending.splitlines()):
        yield pending


def sql_output(files, source):
    """What the player's SQL runner prints for `source` on these files (setup.sql, after.sql), computed by
    running SQLite. Authoring aid only: the lesson validator still runs the real grader on every case."""
    import sqlite3

    def value(v):
        if v is None:
            return 'NULL'
        if isinstance(v, float):
            return f'{v:.1f}' if v == int(v) and abs(v) < 1e15 else repr(v)
        return str(v)

    db = sqlite3.connect(':memory:', isolation_level=None)
    db.execute('PRAGMA foreign_keys=ON')
    out = []
    for name, show in (('setup.sql', False), (None, True), ('after.sql', True)):
        sql = source if name is None else files.get(name, '')
        for statement in _sql_statements(sql):
            cursor = db.execute(statement)
            if not (show and cursor.description):
                cursor.fetchall()
                continue
            text = ' | '.join(c[0] for c in cursor.description) + '\n'
            rows = cursor.fetchall()
            text += ''.join(' | '.join(value(v) for v in row) + '\n' for row in rows) if rows else '(행 없음)\n'
            out.append(text)
    return '\n'.join(out).rstrip('\n')


def lesson_python():
    """The interpreter the debug player grades with (src/runner.rs python_executable): MOLIP_PYTHON, then
    the repository's target/ml-env with the course packages."""
    import os
    import sys
    from pathlib import Path
    if os.environ.get('MOLIP_PYTHON'):
        return os.environ['MOLIP_PYTHON']
    root = Path(__file__).resolve().parents[2]
    for local in (root / 'target/ml-env/Scripts/python.exe', root / 'target/ml-env/bin/python'):
        if local.is_file():
            return str(local)
    return sys.executable


def py_run(source, values=None, timeout=120, files=None, error_ok=False):
    """Run Python `source` with top-level assignments replaced as the prepared checker does (ast).
    Authoring aid: the expected output of the solution for each prepared case. `files` are written to a
    fresh working folder first, as the player does with a step's prepared files."""
    import ast
    import subprocess
    import tempfile
    tree = ast.parse(source)
    remaining = set(values or {})
    for statement in tree.body:
        if isinstance(statement, ast.Assign):
            for target in statement.targets:
                if isinstance(target, ast.Name) and target.id in remaining:
                    statement.value = ast.parse(repr(values[target.id]), mode='eval').body
                    remaining.remove(target.id)
    if remaining:
        raise ValueError(f'prepared names not assigned at top level: {remaining}')
    ast.fix_missing_locations(tree)
    from pathlib import Path
    with tempfile.TemporaryDirectory() as folder:
        for name, text in (files or {}).items():
            Path(folder, name).write_text(text, encoding='utf-8')
        run = subprocess.run([lesson_python(), '-I', '-X', 'utf8', '-c', ast.unparse(tree)], capture_output=True, text=True,
                             encoding='utf-8', timeout=timeout, cwd=folder,
                             env={**__import__('os').environ, 'TF_CPP_MIN_LOG_LEVEL': '3', 'MPLBACKEND': 'Agg'})
    if error_ok:
        return run.stdout.strip() + ('\n' + run.stderr.strip().splitlines()[-1] if run.returncode and run.stderr.strip() else '')
    if run.returncode != 0:
        raise ValueError(f'solution failed for {values}: {run.stderr[-800:]}')
    return run.stdout.strip()


def py_cases(solution, *value_sets):
    """Prepared cases whose expected output is the solution's real output for each set of values."""
    return [{'values': v, 'expected': py_run(solution, v)} for v in value_sets]


def file_variants_checker(reference, variants, message):
    """A lesson checker that rewrites the prepared data files and runs both the learner's main.py and the
    reference solution on each variant, comparing their real output. `variants` is a list of
    {file name: text}; the original files are restored afterwards."""
    import json as _json
    return ('import json\nimport os\nimport subprocess\nimport sys\nfrom pathlib import Path\n\n'
            f'REFERENCE = {reference!r}\nVARIANTS = json.loads({_json.dumps(variants, ensure_ascii=False)!r})\n'
            'names = sorted({name for variant in VARIANTS for name in variant})\n'
            'original = {name: Path(name).read_text(encoding="utf-8") if Path(name).exists() else None for name in names}\n'
            'Path("_reference.py").write_text(REFERENCE, encoding="utf-8")\n'
            'def run(script):\n'
            '    return subprocess.run([sys.executable, "-I", "-X", "utf8", script], stdin=subprocess.DEVNULL, capture_output=True,\n'
            '                          text=True, encoding="utf-8", timeout=60, env=dict(os.environ, MPLBACKEND="Agg"))\n'
            'try:\n'
            '    for variant in VARIANTS:\n'
            '        for name, text in variant.items():\n'
            '            Path(name).write_text(text, encoding="utf-8")\n'
            '        expected = run("_reference.py")\n'
            '        if expected.returncode != 0:\n'
            '            raise RuntimeError("준비한 검사 자료를 읽지 못했어요: " + expected.stderr[-300:])\n'
            '        actual = run("main.py")\n'
            '        if actual.returncode != 0 or actual.stdout.strip() != expected.stdout.strip():\n'
            f'            raise AssertionError({message!r})\n'
            'finally:\n'
            '    for name, text in original.items():\n'
            '        if text is None:\n'
            '            Path(name).unlink(missing_ok=True)\n'
            '        else:\n'
            '            Path(name).write_text(text, encoding="utf-8")\n'
            '    Path("_reference.py").unlink(missing_ok=True)\n'
            'print(f"바꾼 자료 {len(VARIANTS)}개에서도 통과했어요.")\n')


def code_step(old, title, objective, core_flow, intro, instruction, todos, starter, solution, script, warning_review,
              reject=(), accept=(), cases=None, files=None, checker=None, probe=None, timeout=None):
    """One converted Python step. `tests` is the reference solution's real output (never typed)."""
    spec = dict(old=old, title=title, objectives=[objective], core_flow=core_flow,
                goal=intro + '\n\n' + instruction + '\n\n' + todo(*todos), starter_code=starter, solution=solution,
                tests=[{'input': '', 'expected': py_run(solution, files=files)}], narration=script.actions,
                review=warning_review, reject=list(reject), accept=list(accept))
    if files:
        spec['files'] = files
    if cases:
        spec['prepared_cases'] = py_cases(solution, *cases) if not files else [
            {'values': v, 'expected': py_run(solution, v, files=files)} for v in cases]
    if probe:
        spec['prepared_probes'] = probe
    if timeout:
        spec['prepared_task_timeout_seconds'] = timeout
    if checker:
        spec['checker'] = checker
    return spec
