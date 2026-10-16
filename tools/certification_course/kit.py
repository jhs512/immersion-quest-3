"""Shared builders for certificate lessons: real execution, changed inputs, rejected mistakes.

Every exercise is graded against its reference solution. Python checkers rerun the reference and
the learner's code with changed prepared values or data files. Java checkers are JDK contracts that
rewrite the prepared variable values, run the program, and compare with reference outputs that the
build computed. Representative mistakes are kept out of the lesson file and proven to fail.
"""
import base64
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

from principles_course.common import JAVA, PYTHON, ROOT, code, execute, task

CHECK_RUNNER = ("import runpy,sys,traceback\ntry:\n    runpy.run_path('checker.py',run_name='__main__')\n"
    "except AssertionError:\n    traceback.print_exc()\n    sys.exit(1)\nexcept SystemExit as e:\n"
    "    sys.exit(0 if e.code is None else e.code)\nexcept BaseException:\n    traceback.print_exc()\n    sys.exit(2)\n")

PY_CHECKER = '''
import ast
import builtins
import contextlib
import io
import math
import os
from pathlib import Path
import shutil
import sys
import tempfile
import traceback
import warnings

os.environ['MPLBACKEND'] = 'Agg'
# Grading output is for the verdict only; font and library warnings would bury the reason.
warnings.filterwarnings('ignore')
builtins.display = lambda *args, **kwargs: None
reference = REFERENCE
cases = CASES
names = NAMES
base_files = BASE_FILES
source = open(sys.argv[1], encoding='utf8').read()


class Inputs(ast.NodeTransformer):
    # Replace only the first prepared assignment to each changed name.
    def __init__(self, values):
        self.values = values
        self.seen = set()

    def visit_Assign(self, node):
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name in self.values and name not in self.seen:
                self.seen.add(name)
                node.value = ast.parse(repr(self.values[name]), mode='eval').body
        return node


def execute(text, values):
    tree = ast.fix_missing_locations(Inputs(values).visit(ast.parse(text)))
    scope = {'__name__': '__main__'}
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        exec(compile(tree, 'main.py', 'exec'), scope)
    plt = sys.modules.get('matplotlib.pyplot')
    if plt is not None:
        plt.close('all')
    return output.getvalue().rstrip('\\n'), scope


def same(actual, expected):
    pd = sys.modules.get('pandas')
    if pd is not None and isinstance(expected, (pd.DataFrame, pd.Series, pd.Index)):
        if type(actual) is not type(expected):
            return False
        try:
            if isinstance(expected, pd.DataFrame):
                pd.testing.assert_frame_equal(actual, expected)
            elif isinstance(expected, pd.Series):
                pd.testing.assert_series_equal(actual, expected)
            else:
                pd.testing.assert_index_equal(actual, expected)
            return True
        except AssertionError:
            return False
    np = sys.modules.get('numpy')
    if np is not None and isinstance(expected, np.ndarray):
        # Model and scaler outputs: same shape, and values equal up to float rounding.
        if not isinstance(actual, np.ndarray) or actual.shape != expected.shape:
            return False
        if expected.dtype.kind in 'fc':
            return bool(np.allclose(actual, expected, rtol=1e-7, atol=1e-9, equal_nan=True))
        return bool(np.array_equal(actual, expected))
    if isinstance(expected, float) and isinstance(actual, (int, float)):
        return math.isclose(actual, expected, rel_tol=1e-9, abs_tol=1e-12)
    try:
        return bool(actual == expected)
    except Exception:
        return False


def fail(message):
    # The learner reads only this message, never the checker's own traceback.
    print(message, file=sys.stderr)
    sys.exit(1)


def snapshot(inputs):
    # Files the run created or changed, such as a saved result CSV.
    produced = {}
    for path in Path('.').rglob('*'):
        if path.is_file() and inputs.get(path.as_posix()) != path.read_bytes():
            produced[path.as_posix()] = path.read_bytes()
    return produced


def run_in_fresh_folder(files, text, values):
    # Each run gets its own copy of the data, so files one run writes never help another.
    home = os.getcwd()
    folder = tempfile.mkdtemp(dir=home)
    try:
        os.chdir(folder)
        inputs = {}
        for path, content in files.items():
            target = Path(path)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding='utf8')
            inputs[target.as_posix()] = target.read_bytes()
        output, scope = execute(text, values)
        return output, scope, snapshot(inputs)
    finally:
        os.chdir(home)
        shutil.rmtree(folder, ignore_errors=True)


def describe(case):
    parts = [name + ' = ' + repr(value) for name, value in case.items() if name != 'files']
    parts += [path + ' 내용' for path in case.get('files', {})]
    return ', '.join(parts)


MESSAGES = {'__figures__': '그래프의 종류·축 이름·값이 기준 그래프와 달라요. 바뀐 자료로도 같은 그래프를 그리세요.'}
for index, case in enumerate(cases):
    values = {k: v for k, v in case.items() if k != 'files'}
    files = {**base_files, **case.get('files', {})}
    expected, wanted, made = run_in_fresh_folder(files, reference, values)
    changed = '준비 값을 ' + describe(case) + '(으)로 바꾸면 '
    try:
        actual, scope, produced = run_in_fresh_folder(files, source, values)
    except SystemExit:
        fail('코드가 exit로 중간에 끝났어요. 끝까지 실행되게 하세요.')
    except BaseException as error:
        reason = ''.join(traceback.format_exception_only(type(error), error)).strip()
        fail(('코드를 실행하면' if index == 0 else changed.rstrip()) + ' 오류가 나요.\\n' + reason)
    if index == 0:
        problem = '실행 결과가 기대와 달라요.'
    else:
        problem = changed + '결과가 달라요.\\n값이나 자료가 바뀌어도 맞는 방법인지 확인하세요.'
    if actual != expected:
        fail(problem + '\\n기대 출력:\\n' + expected[-600:] + '\\n실제 출력:\\n' + actual[-600:])
    for name in names:
        if name not in scope:
            fail(name + '에 결과를 담아 주세요.')
        if not same(scope[name], wanted[name]):
            fail(problem + '\\n' + MESSAGES.get(name, name + '의 값이 기대와 달라요.'))
    for path in sorted(made):
        if path not in produced:
            fail(problem + '\\n' + path + ' 파일을 저장하지 않았어요.')
        if produced[path] != made[path]:
            fail(problem + '\\n저장한 ' + path + ' 파일의 내용이 기대와 달라요.')
print('준비 값과 자료를 바꿔도 같은 원리로 계산했어요.')
'''

JAVA_CONTRACT = r'''
import com.sun.source.tree.VariableTree;
import com.sun.source.util.JavacTask;
import com.sun.source.util.TreeScanner;
import com.sun.source.util.Trees;
import java.io.ByteArrayOutputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Base64;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;

class QuestContract {
    // The prepared values' output, then each scenario: output, then name/value pairs. Base64 keeps any text intact.
    static final String BASE = "{BASE}";
    static final String[] SCENARIOS = {SCENARIOS};

    // A learner sees only this message, never a stack trace.
    static void fail(String message) {
        System.err.println(message);
        System.exit(1);
    }

    static String describe(Map<String, String> values) {
        List<String> parts = new ArrayList<>();
        values.forEach((name, value) -> parts.add(name + " = " + value));
        return String.join(", ", parts);
    }

    public static void main(String[] args) throws Exception {
        String source = Files.readString(Path.of("Main.java"));
        List<Map<String, String>> scenarios = new ArrayList<>();
        List<String> expected = new ArrayList<>();
        List<String> programs = new ArrayList<>();
        programs.add(source);
        for (String encoded : SCENARIOS) {
            String[] parts = new String(Base64.getDecoder().decode(encoded), StandardCharsets.UTF_8).split("\u0000", -1);
            Map<String, String> values = new LinkedHashMap<>();
            for (int i = 1; i + 1 < parts.length; i += 2) values.put(parts[i], parts[i + 1]);
            scenarios.add(values);
            expected.add(parts[0]);
            programs.add(mutate(values));
        }
        // Run the learner's program and every changed copy at once; report in order.
        List<java.util.concurrent.Future<String[]>> runs = new ArrayList<>();
        var pool = java.util.concurrent.Executors.newFixedThreadPool(programs.size());
        for (String program : programs) runs.add(pool.submit(() -> run(program)));
        pool.shutdown();
        String base = new String(Base64.getDecoder().decode(BASE), StandardCharsets.UTF_8);
        String[] own = runs.get(0).get();
        if (own[1] != null) fail("코드를 실행하면 오류가 나요. 코드 실행으로 오류 줄을 먼저 확인하세요.\n" + own[1]);
        if (!own[0].equals(base)) fail("실행 결과가 기대와 달라요.\n기대 출력:\n" + tail(base) + "\n실제 출력:\n" + tail(own[0]));
        for (int i = 0; i < scenarios.size(); i++) {
            String[] result = runs.get(i + 1).get();
            String changed = "준비 값을 " + describe(scenarios.get(i)) + "(으)로 바꾸면 ";
            if (result[1] != null) fail(changed + "오류가 나요.\n" + result[1]);
            if (!result[0].equals(expected.get(i))) {
                fail(changed + "결과가 달라요.\n값이 바뀌어도 맞는 식인지 확인하세요.\n기대 출력:\n" + tail(expected.get(i))
                    + "\n실제 출력:\n" + tail(result[0]));
            }
        }
        System.out.print(programs.get(programs.size() - 1));
    }

    static String tail(String text) {
        return text.length() > 600 ? text.substring(text.length() - 600) : text;
    }

    // Replace the first initializer of each prepared name, found by the compiler's own parser.
    static String mutate(Map<String, String> values) throws Exception {
        String source = Files.readString(Path.of("Main.java"));
        var compiler = javax.tools.ToolProvider.getSystemJavaCompiler();
        try (var files = compiler.getStandardFileManager(null, null, StandardCharsets.UTF_8)) {
            var task = (JavacTask) compiler.getTask(null, files, diagnostic -> {}, List.of("-proc:none"), null,
                files.getJavaFileObjects("Main.java"));
            var tree = task.parse().iterator().next();
            var positions = Trees.instance(task).getSourcePositions();
            Map<String, long[]> found = new LinkedHashMap<>();
            new TreeScanner<Void, Void>() {
                public Void visitVariable(VariableTree node, Void unused) {
                    String name = node.getName().toString();
                    if (values.containsKey(name) && !found.containsKey(name) && node.getInitializer() != null) {
                        found.put(name, new long[] {positions.getStartPosition(tree, node.getInitializer()),
                            positions.getEndPosition(tree, node.getInitializer())});
                    }
                    return super.visitVariable(node, unused);
                }
            }.scan(tree, null);
            for (String name : values.keySet()) {
                long[] bounds = found.get(name);
                if (bounds == null || bounds[0] < 0 || bounds[1] < bounds[0]) {
                    fail("준비 코드의 " + name + " 선언과 처음 값은 그대로 두세요.");
                }
            }
            List<Map.Entry<String, long[]>> edits = new ArrayList<>(found.entrySet());
            edits.sort(Comparator.comparingLong((Map.Entry<String, long[]> e) -> e.getValue()[0]).reversed());
            StringBuilder changed = new StringBuilder(source);
            for (var edit : edits) changed.replace((int) edit.getValue()[0], (int) edit.getValue()[1], values.get(edit.getKey()));
            return changed.toString();
        }
    }

    // Returns {output, null} or {null, problem}; problems are worded for the learner.
    static String[] run(String program) throws Exception {
        Path folder = Files.createTempDirectory("quest-contract");
        try {
            Files.writeString(folder.resolve("Main.java"), program);
            String java = Path.of(System.getProperty("java.home"), "bin", "java").toString();
            Process process = new ProcessBuilder(java, "-Xmx128m", "-Dfile.encoding=UTF-8", "-Dstdout.encoding=UTF-8",
                "-Dstderr.encoding=UTF-8", "--source", "25", "Main.java").directory(folder.toFile()).start();
            process.getOutputStream().close();
            ByteArrayOutputStream out = new ByteArrayOutputStream();
            ByteArrayOutputStream err = new ByteArrayOutputStream();
            Thread readOut = new Thread(() -> { try { process.getInputStream().transferTo(out); } catch (Exception ignored) {} });
            Thread readErr = new Thread(() -> { try { process.getErrorStream().transferTo(err); } catch (Exception ignored) {} });
            readOut.start();
            readErr.start();
            if (!process.waitFor(8, TimeUnit.SECONDS)) {
                process.destroyForcibly();
                return new String[] {null, "실행이 8초 안에 끝나지 않아요. 반복 조건을 확인하세요."};
            }
            readOut.join();
            readErr.join();
            if (process.exitValue() != 0) return new String[] {null, tail(err.toString(StandardCharsets.UTF_8))};
            String text = out.toString(StandardCharsets.UTF_8).replace("\r\n", "\n");
            while (text.endsWith("\n")) text = text.substring(0, text.length() - 1);
            return new String[] {text, null};
        } finally {
            try (var paths = Files.walk(folder)) {
                paths.sorted(Comparator.reverseOrder()).forEach(path -> path.toFile().delete());
            }
        }
    }
}
'''

JAVA_TYPES = r'(?:int|long|double|float|boolean|char|String|var|byte|short)(?:\[\])*'


def main_class(body, methods=''):
    """A fixed Main class. Prepared statements go inside main; optional static methods go above it."""
    inner = ''.join('    ' + line + '\n' if line else '\n' for line in code(methods).splitlines()) + '\n' if methods.strip() else ''
    return ('class Main {\n' + inner + '    public static void main(String[] args) {\n'
        + ''.join('        ' + line + '\n' if line else '\n' for line in code(body).splitlines()) + '    }\n}\n')


def _mistakes(t, wrong):
    sources = []
    for item in wrong or []:
        before, after = item
        base = t['starter_code'] if t['starter_code'].count(before) == 1 else t['solution']
        assert base.count(before) == 1, (t['id'], 'mistake edit must match once', before)
        changed = base.replace(before, after, 1)
        assert changed not in (t['solution'], t['starter_code']), (t['id'], 'mistake equals starter or solution')
        sources.append(changed)
    t['_wrong'] = sources
    return t


def py_task(id, title, principle, goal, starter, before, after, *, caution, hints, scenarios=None, files=None,
            compare=(), wrong=None, challenge=False, volatile=False):
    """Python exercise compared with its reference on the prepared values and every changed scenario.

    scenarios: dicts; 'files' replaces data files, any other key replaces the first assignment to that name.
    compare: variable names whose values must equal the reference too (pandas-aware).
    wrong: (before, after) edits of the starter (or solution) that represent common mistakes.
    """
    t = task(id, title, principle, goal, starter, before, after, language='python', files=files or {},
             tests=[('', '')], caution=caution, hints=hints, challenge=challenge)
    cases = [{}] + list(scenarios or [])
    assert len(cases) >= 3, (id, 'at least two changed scenarios are required')
    t['checker'] = code(PY_CHECKER).replace('REFERENCE', repr(t['solution'])).replace('CASES', repr(cases)) \
        .replace('NAMES', repr(list(compare))).replace('BASE_FILES', repr(files or {})) \
        .replace('MISSING', repr('에 결과를 담아 주세요.')).replace('CHANGED', repr('준비 값이나 자료가 바뀌었을 때도 같은 원리로 계산하세요.'))
    t['_scenarios'] = cases
    # volatile: the starter's output changes every run (no random_state yet), so narration must not quote it.
    if volatile:
        t['_volatile'] = True
    return _mistakes(t, wrong)


def _java_mutate(source, values):
    for name, value in values.items():
        pattern = re.compile(r'(\b' + JAVA_TYPES + r'\s+' + re.escape(name) + r'\s*=\s*)([^;]+)(;)')
        match = pattern.search(source)
        assert match, ('reference has no simple declaration for', name)
        source = source[:match.start(2)] + value + source[match.end(2):]
    return source


def _run_java(source, folder=None, entry='Main.java', extra=None, input=''):
    with tempfile.TemporaryDirectory() as temp:
        (Path(temp) / 'Main.java').write_text(source, encoding='utf8', newline='\n')
        for name, body in (extra or {}).items():
            (Path(temp) / name).write_text(body, encoding='utf8', newline='\n')
        env = os.environ.copy()
        for key in ['JAVA_TOOL_OPTIONS', 'JDK_JAVA_OPTIONS', '_JAVA_OPTIONS']:
            env.pop(key, None)
        return subprocess.run([JAVA, '-Xmx128m', '-Dfile.encoding=UTF-8', '-Dstdout.encoding=UTF-8',
            '-Dstderr.encoding=UTF-8', '--source', '25', entry], cwd=temp, input=input, capture_output=True,
            text=True, encoding='utf8', errors='replace', timeout=60, env=env)


def _out(result):
    return result.stdout.replace('\r\n', '\n').rstrip('\n')


def java_task(id, title, principle, goal, source, before, after, *, caution, hints, scenarios, wrong=None,
              challenge=False):
    """Single-file Java exercise (class Main). scenarios: dicts of prepared name -> Java literal text."""
    t = task(id, title, principle, goal, source, before, after, language='java', tests=[('', '')],
             caution=caution, hints=hints, challenge=challenge)
    assert len(scenarios) >= 2, (id, 'at least two changed scenarios are required')
    base = _out(_run_java(t['solution']))
    encoded = []
    for values in scenarios:
        result = _run_java(_java_mutate(t['solution'], values))
        assert result.returncode == 0, (id, values, result.stderr[-800:])
        expected = _out(result)
        assert expected != base, (id, values, 'a changed scenario must change the reference output')
        payload = '\u0000'.join([expected] + [x for pair in values.items() for x in pair])
        encoded.append('"' + base64.b64encode(payload.encode('utf8')).decode('ascii') + '"')
    t['checker'] = code(JAVA_CONTRACT).replace('{SCENARIOS}', '{' + ', '.join(encoded) + '}') \
        .replace('{BASE}', base64.b64encode(base.encode('utf8')).decode('ascii'))
    t['_scenarios'] = [{}] + list(scenarios)
    return _mistakes(t, wrong)


def mutate_c(source, name, value):
    """Same rule as src/lesson_runner.rs mutate_c: replace the first declaration's initializer of name."""
    i, previous, n = 0, ';', len(source)

    def ident(c):
        return c.isascii() and (c.isalnum() or c == '_')

    while i < n:
        c = source[i]
        if source.startswith('//', i):
            while i < n and source[i] != '\n':
                i += 1
            continue
        if source.startswith('/*', i):
            end = source.find('*/', i + 2)
            i = n if end < 0 else end + 2
            continue
        if c in '"\'':
            i += 1
            while i < n and source[i] != c:
                i += 2 if source[i] == '\\' else 1
            i += 1
            previous = c
            continue
        if ident(c):
            start = i
            while i < n and ident(source[i]):
                i += 1
            declared = ident(previous) or previous in '*,'
            if source[start:i] == name and declared:
                j = i
                while True:
                    while j < n and source[j].isspace():
                        j += 1
                    if j < n and source[j] == '[':
                        j = source.find(']', j) + 1
                        continue
                    break
                if j < n and source[j] == '=' and source[j + 1:j + 2] != '=':
                    begin, end, depth = j + 1, j + 1, 0
                    while end < n:
                        ch = source[end]
                        if ch in '({[':
                            depth += 1
                        elif ch in ')}]':
                            depth -= 1
                        elif ch in '"\'':
                            end += 1
                            while end < n and source[end] != ch:
                                end += 2 if source[end] == '\\' else 1
                        elif ch in ';,' and depth == 0:
                            break
                        end += 1
                    if end >= n:
                        return None
                    return source[:begin] + ' ' + value.strip() + source[end:]
            previous = source[i - 1]
            continue
        if not c.isspace():
            previous = c
        i += 1
    return None


def _c_output(result):
    return result.stdout.replace('\r\n', '\n').rstrip('\n')


def c_task(id, title, principle, goal, source, before, after, *, caution, hints, scenarios, wrong=None,
           challenge=False):
    """C exercise (main.c). scenarios: dicts of prepared name -> C literal text, rerun by the player."""
    t = task(id, title, principle, goal, source, before, after, language='c', tests=[('', '')],
             caution=caution, hints=hints, challenge=challenge)
    assert len(scenarios) >= 2, (id, 'at least two changed scenarios are required')
    base = execute(t, t['solution'])
    assert base.returncode == 0, (id, base.stderr[-800:])
    variations = []
    for values in scenarios:
        changed = t['solution']
        for name, value in values.items():
            changed = mutate_c(changed, name, value)
            assert changed is not None, (id, 'no simple declaration with an initial value for', name)
        result = execute(t, changed)
        assert result.returncode == 0, (id, values, result.stderr[-800:])
        assert _c_output(result) != _c_output(base), (id, values, 'a changed scenario must change the reference output')
        variations.append(dict(values=dict(values), expected=_c_output(result)))
    t['variations'] = variations
    t['_scenarios'] = [{}] + list(scenarios)
    return _mistakes(t, wrong)


def grade(t, source):
    """Emulate the player's grading path closely enough for authoring; cargo tests use the real one."""
    if t['language'] == 'c':
        result = execute(t, source)
        if result.returncode or _c_output(result) != t['tests'][0]['expected'].rstrip('\n'):
            return False, (result.stdout + result.stderr)[-1500:]
        for variation in t.get('variations', []):
            changed = source
            for name, value in variation['values'].items():
                changed = mutate_c(changed, name, value) if changed is not None else None
            if changed is None:
                return False, 'prepared declaration removed'
            result = execute(t, changed)
            if result.returncode or _c_output(result) != variation['expected'].rstrip('\n'):
                return False, 'changed values: ' + str(variation['values'])
        return True, ''
    if t['language'] == 'python':
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            for name, body in t['files'].items():
                path = folder / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(body, encoding='utf8', newline='\n')
            (folder / 'main.py').write_text(source, encoding='utf8', newline='\n')
            (folder / 'checker.py').write_text(t['checker'], encoding='utf8', newline='\n')
            (folder / 'check_runner.py').write_text(CHECK_RUNNER, encoding='utf8', newline='\n')
            result = subprocess.run([str(PYTHON), '-I', '-X', 'utf8', '-u', 'check_runner.py', str(folder / 'main.py')],
                cwd=temp, capture_output=True, text=True, encoding='utf8', errors='replace', timeout=120)
            return result.returncode == 0, (result.stdout + result.stderr)[-1500:]
    if t['language'] == 'java':
        expected = t['tests'][0]['expected']
        if t.get('checker'):
            contract = _run_java(source, entry='QuestContract.java', extra={'QuestContract.java': t['checker']})
            if contract.returncode:
                return False, contract.stderr[-1500:]
            mutated = _run_java(contract.stdout)
            if mutated.returncode or _out(mutated) == expected.rstrip('\n'):
                return False, 'changed values did not change the output'
        result = _run_java(source)
        return result.returncode == 0 and _out(result) == expected.rstrip('\n'), (result.stdout + result.stderr)[-1500:]
    results = [execute(t, source, case['input']) for case in t['tests']]
    passed = all(r.returncode == 0 and r.stdout.replace('\r\n', '\n').rstrip('\n') == c['expected'].rstrip('\n')
                 for r, c in zip(results, t['tests']))
    return passed, ''


FORMAL = re.compile(r'(습니다|입니다|합니다|됩니다|십시오|한다|된다|이다|있다|없다)[.!]?$')


def voice_problems(lesson):
    """Lines a learner reads: polite spoken endings and short sentences (docs/voice.md)."""
    problems = []
    texts = [('description', lesson['description'])]
    for t in lesson['tasks']:
        texts += [(t['id'] + '/goal', t['goal'])] + [(t['id'] + '/hint', h) for h in t['hints']]
        texts += [(t['id'] + '/caution', t.get('_caution', ''))]
    for where, text in texts:
        for line in text.splitlines():
            if not line.strip() or line.lstrip().startswith('|'):
                continue
            plain = re.sub(r'`[^`]*`', 'X', line)
            for sentence in re.split(r'(?<=[.?!])\s+', plain.strip()):
                if len(sentence) > 45:
                    problems.append(f'{where}: 문장이 45자를 넘어요: {sentence}')
                if FORMAL.search(sentence.strip()):
                    problems.append(f'{where}: 해요체가 아니에요: {sentence}')
    return problems


def verify(lesson, *, strict_voice=True):
    """Prove each new exercise: starter fails, solution passes, every listed mistake fails."""
    report = []
    for t in lesson['tasks']:
        ok, detail = grade(t, t['solution'])
        assert ok, (lesson['id'], t['id'], 'solution must pass', detail)
        if t['language'] == 'python':
            # Warnings would reach learners as noise next to the real output.
            # The player replaces plt.show with figure capture; a plain run only warns about Agg.
            # TensorFlow's Windows GPU notice is hidden by the player's runner and by tf_task checkers.
            noise = '\n'.join(line for line in execute(t, t['solution']).stderr.strip().splitlines()
                              if 'FigureCanvasAgg is non-interactive' not in line and line.strip() != 'plt.show()'
                              and 'GPU support is not available on native Windows' not in line)
            assert not noise, (lesson['id'], t['id'], 'solution prints warnings', noise[-800:])
        ok, detail = grade(t, t['starter_code'])
        assert not ok, (lesson['id'], t['id'], 'starter must fail')
        for index, source in enumerate(t.get('_wrong', [])):
            ok, detail = grade(t, source)
            assert not ok, (lesson['id'], t['id'], f'mistake {index + 1} must fail', source)
        report.append(f"OK {t['id']}: solution passes, starter and {len(t.get('_wrong', []))} mistakes fail")
    problems = voice_problems(lesson)
    if strict_voice:
        assert not problems, '\n'.join(problems)
    return report


def settle_narration(lesson):
    """After compile_narration: a volatile starter's reading says what to watch, not one run's numbers."""
    for t in lesson['tasks']:
        if t.pop('_volatile', False):
            reading = next(step for step in t['narration'] if step.get('action') == 'say' and step.get('target') == 'output')
            reading['text'] = '실행할 때마다 결과가 달라져요. 한 번 더 실행해서 비교해 보세요.'


def finish(lesson):
    """Move author-only data out of the lesson. Returns {task id: [mistake sources]}."""
    mistakes = {}
    for t in lesson['tasks']:
        mistakes[t['id']] = t.pop('_wrong', [])
        t.pop('_scenarios', None)
    return mistakes
