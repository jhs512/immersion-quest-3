"""Build and run, or build and trace, one C++ or Rust program with the same compiler command.

    native_flow.py run   <case> <cpp|rust>   compile, then become the program (stdin/stdout pass through)
    native_flow.py trace <case> <cpp|rust>   compile, then record the program once under LLDB

<case>/src holds the learner's source and is never changed; the build reads a byte-identical copy.
`run` writes <case>/compile.json; `trace` writes <case>/native_flow.json.
"""
import json
import os
from pathlib import Path
import re
import shlex
import signal
import subprocess
import sys

HERE = Path(__file__).resolve().parent
SOURCE = {'cpp': 'main.cpp', 'rust': 'main.rs'}
RUST_EDITION = '2024'


def tool(name, default):
    return shlex.split(os.environ.get(name, default))


def compile_command(language):
    if language == 'cpp':
        return [*tool('MQ_CXX', 'clang++'), '-std=c++17', '-g', '-O0', '-fstandalone-debug', '-o', 'main', 'main.cpp']
    return [*tool('MQ_RUSTC', 'rustc'), '--edition', RUST_EDITION, '-g', '-C', 'opt-level=0',
            '--error-format=json', '--emit=link,mir', '-o', 'main', 'main.rs']


def problems(language, text):
    if language == 'rust':
        found, rendered = [], []
        for line in text.splitlines():
            try:
                item = json.loads(line)
            except ValueError:
                continue
            if item.get('$message_type') != 'diagnostic' or item.get('level') not in ('error', 'error: internal compiler error'):
                continue
            if item.get('message', '').startswith('aborting due to'):
                continue
            spans = [s for s in item.get('spans', []) if s.get('is_primary') and s.get('file_name') == 'main.rs']
            found.append({'line': spans[0]['line_start'] if spans else 0, 'error': True, 'message': item.get('message', '')})
            rendered.append(item.get('rendered') or item.get('message', ''))
        return found, '\n'.join(rendered)
    found = [{'line': int(m.group(1)), 'error': True, 'message': m.group(2)}
             for m in re.finditer(r'main\.cpp:(\d+):\d+: (?:fatal )?error: ([^\n]+)', text)]
    return found, text


def build(case, language):
    original = (case / 'src').read_bytes()
    (case / SOURCE[language]).write_bytes(original)
    built = subprocess.run(compile_command(language), cwd=case, capture_output=True, timeout=60)
    text = (built.stderr + built.stdout).decode('utf-8', 'replace')
    found, rendered = problems(language, text)
    result = {'success': built.returncode == 0 and (case / 'main').is_file(), 'problems': found, 'stderr': rendered,
              'command': compile_command(language)}
    if result['success'] and language == 'rust':
        result['stderr'] = ''
    (case / 'compile.json').write_text(json.dumps(result, ensure_ascii=False), encoding='utf-8')
    return original.decode('utf-8', 'replace'), result


def rust_moves(case):
    """Ownership events from the spans MIR, only when it is the MIR of the build that made ./main."""
    sys.path.insert(0, str(HERE))
    import rust_mir
    spans = case / 'spans'
    spans.mkdir(exist_ok=True)
    (spans / 'main.rs').write_bytes((case / 'main.rs').read_bytes())
    env = dict(os.environ, RUSTC_BOOTSTRAP='1')
    run = subprocess.run([*tool('MQ_RUSTC', 'rustc'), '--edition', RUST_EDITION, '-g', '-C', 'opt-level=0',
                          '-Zmir-include-spans=yes', '-Zdump-mir=built', '-Zdump-mir-dir=dump',
                          '--emit=mir', '-o', 'main.mir', 'main.rs'],
                         cwd=spans, capture_output=True, timeout=60, env=env)
    if run.returncode:
        return None, 'MIR 위치 정보를 만들지 못했어요'
    stable = (case / 'main.mir').read_text(encoding='utf-8')
    if not rust_mir.same_mir(stable, (spans / 'main.mir').read_text(encoding='utf-8')):
        return None, '위치 정보가 붙은 MIR이 실행 파일의 MIR과 달라요'
    built = sorted((spans / 'dump').glob('*.built.after.mir'))
    if not built:
        return None, '빌드 단계 MIR이 없어요'
    text = '\n'.join(p.read_text(encoding='utf-8') for p in built)
    return rust_mir.events(text, 'main.rs', (case / 'main.rs').read_text(encoding='utf-8')), None


LOCATION = re.compile(r'<invalid sloc>|<built-in>|<scratch space>|line:(\d+):\d+|col:\d+|([^\s<>,:]+):(\d+):\d+')
VAR_DECL = re.compile(r'-VarDecl 0x[0-9a-f]+ <[^>]*> (?:\S+ )?(?:used |referenced )?(\w+) \'')


def cpp_declarations(case):
    """{'line:name': has initializer} for main.cpp's variables, streamed from clang's text AST.

    The JSON AST of a file that includes <iostream> is hundreds of megabytes; the text dump is read line by line.
    Each location in it is relative to the one printed before it.
    """
    process = subprocess.Popen([*tool('MQ_CXX', 'clang++'), '-std=c++17', '-fno-color-diagnostics', '-Xclang', '-ast-dump',
                                '-fsyntax-only', 'main.cpp'], cwd=case, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    found, file, line = {}, None, 0
    for raw in process.stdout:
        text = raw.decode('utf-8', 'replace')
        for match in LOCATION.finditer(text):
            if match.group(1):
                line = int(match.group(1))
            elif match.group(2):
                file, line = match.group(2), int(match.group(3))
        declared = VAR_DECL.search(text)
        if declared and file == 'main.cpp':
            initialized = re.search(r' (?:c|call|list|parenlist)init(?: destroyed)?$', text.rstrip()) is not None
            found.setdefault(f'{line}:{declared.group(1)}', []).append(initialized)
    if process.wait(timeout=60):
        return {}
    return {key: values[0] for key, values in found.items() if len(values) == 1}


def trace(case, language):
    source, built = build(case, language)
    path = case / 'native_flow.json'
    if not built['success']:
        doc = {'code': source, 'language': language, 'status': 'compile_error', 'trace': [],
               'problems': built['problems'] or [{'line': 0, 'error': True, 'message': built['stderr'][-500:]}]}
        path.write_text(json.dumps(doc, ensure_ascii=False), encoding='utf-8')
        return
    if language == 'rust':
        moves, reason = rust_moves(case)
        if moves is None:
            doc = {'code': source, 'language': language, 'status': 'unsupported', 'trace': [], 'problems': [],
                   'message': f'Rust의 move 상태를 확인할 근거가 없어 코드 흐름을 그리지 않아요. {reason}'}
            path.write_text(json.dumps(doc, ensure_ascii=False), encoding='utf-8')
            return
        (case / 'moves.json').write_text(json.dumps(moves), encoding='utf-8')
    else:
        (case / 'declarations.json').write_text(json.dumps(cpp_declarations(case)), encoding='utf-8')
    lldb = tool('MQ_LLDB', 'lldb')
    commands = ['-o', 'command script import ' + shlex.quote(str(HERE / 'native_lldb.py'))]
    if language == 'rust':
        sysroot = subprocess.run([*tool('MQ_RUSTC', 'rustc'), '--print', 'sysroot'], capture_output=True, text=True,
                                 timeout=30).stdout.strip()
        etc = Path(sysroot) / 'lib' / 'rustlib' / 'etc'
        commands = ['-o', 'command script import ' + shlex.quote(str(etc / 'lldb_lookup.py')),
                    '-o', 'command source -s 1 ' + shlex.quote(str(etc / 'lldb_commands')), *commands]
    commands += ['-o', f'mq-native-trace {shlex.quote(str(case))} {language} {SOURCE[language]}']
    process = subprocess.Popen([*lldb, '-b', '-Q', *commands], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               start_new_session=True)
    try:
        out, err = process.communicate(timeout=int(os.environ.get('MQ_TRACE_SECONDS', '75')))
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.communicate()
        raise RuntimeError('LLDB 추적이 제한 시간을 넘었어요')
    if process.returncode or not path.is_file():
        raise RuntimeError('LLDB 추적 실패: ' + (out + err).decode('utf-8', 'replace')[-1500:])
    doc = json.loads(path.read_text(encoding='utf-8'))
    doc['verification'] = {'original_source': (case / 'src').read_bytes() == (case / SOURCE[language]).read_bytes(),
                           'compile_command': built['command'], 'native_debugger': 'LLDB',
                           'program_runs': doc.pop('program_runs', 0),
                           'ownership': 'rustc MIR (same compiler, same source)' if language == 'rust' else None}
    path.write_text(json.dumps(doc, ensure_ascii=False), encoding='utf-8')


def run(case, language):
    _, built = build(case, language)
    if not built['success']:
        sys.stderr.write(built['stderr'])
        sys.exit(1)
    os.execv(str(case / 'main'), [str(case / 'main')])


if __name__ == '__main__':
    mode, folder, lang = sys.argv[1:4]
    {'run': run, 'trace': trace}[mode](Path(folder).resolve(), lang)
