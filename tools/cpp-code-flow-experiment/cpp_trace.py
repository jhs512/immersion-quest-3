"""Experimental C++ tracer (a C++ adaptation of ../../c/c_trace.py; MQ has no C++ grader): real execution under the Windows debugger engine (dbgeng.dll), recorded in
the java-memory-visualizer trace format. NOT integrated into the app.

The executable must carry a PDB (MSVC `cl /Zi`). The course's Windows grader uses TinyCC 0.9.27
(`tcc -run`), whose STABS debug info dbgeng cannot read -- see report.md. So this traces the same
source compiled by a DIFFERENT compiler than the grader.

Every source line of main.c gets a breakpoint; each hit becomes one full snapshot:
  - the line and the call stack come from `kn` (only frames whose source is main.c);
  - each frame's locals come from `.frame N` + `dv /t /v` (arrays/structs expanded one level by `dx -r1`);
  - a hit at a function's first byte (before its prolog) is not a step: its locals are not set up yet.
    It marks a call; the next hit (first body line) is recorded as `call`, then `step_line`.
  - the hit on a function's closing-brace line is recorded as `return`, with __return__ = eax for int-like
    return types.

usage: python -I c_trace.py main_cl.exe main.c stdin.txt trace.json [stepBudget]
"""
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'assets', 'c-trace'))   # shared dbgeng driver
from dbgeng import Debugger, DEBUG_STATUS_NO_DEBUGGEE  # noqa: E402

SIZES = {'char': 1, 'signed char': 1, 'unsigned char': 1, 'short': 2, 'unsigned short': 2, 'int': 4,
         'unsigned int': 4, 'long': 4, 'unsigned long': 4, 'float': 4, 'double': 8, 'long long': 8,
         'unsigned long long': 8, '__int64': 8}
INTLIKE = {'int', 'unsigned int', 'long', 'unsigned long', 'short', 'unsigned short', 'char', 'unsigned char', 'long long', '__int64'}
FRAME_RE = re.compile(r'^([0-9a-f]+) ([0-9a-f`]+) [0-9a-f`]+\s+(\w+)!([^\s\[+]+)(\+0x[0-9a-f]+)? \[(.+) @ (\d+)\]')
DV_RE = re.compile(r'^([0-9a-f`]+)\s+(.+?)\s+(\w+) = (.*)$')
DX_RE = re.compile(r'^\s+(\[\+0x[0-9a-f]+\]\s+)?(\[[^\]]+\]|\w+)\s+: (.*?) \[Type: (.+)\]\s*$')
DX_HEAD = re.compile(r'^\S+\s+: (.*?) \[Type: (.+)\]\s*$')
STL_NATVIS = os.path.join(r"C:/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/Common7/Packages/Debugger/Visualizers", "stl.natvis")


def addr(text):
    return int(text.replace('`', ''), 16)


def main():
    exe, source_path, stdin_path, out_path = [os.path.abspath(p) for p in sys.argv[1:5]]
    budget = int(sys.argv[5]) if len(sys.argv) > 5 else 1000
    module = os.path.splitext(os.path.basename(exe))[0]
    source = open(source_path, encoding='utf-8').read()
    src_name = os.path.normcase(source_path)
    stdout_path = out_path + '.stdout.txt'
    started = time.perf_counter()
    d = Debugger(f'"{exe}"', stdin_path, stdout_path)
    d.run('.sympath ' + os.path.dirname(exe))
    d.run('.lines -e')
    d.run(f'.reload /f {os.path.basename(exe)}')
    # STL display rules from the already installed VS BuildTools (vector elements, string text)
    natvis = d.run(f'.nvload {STL_NATVIS}').strip() if os.path.exists(STL_NATVIS) else 'stl.natvis not found'
    version = next((l for l in d.run('version').splitlines() if 'Debugger Version' in l), '').strip()
    d.run('sxe eh')                     # stop when a C++ exception is thrown (first chance)
    for n in range(1, source.count('\n') + 2):
        d.run(f'bp `{module}!{os.path.basename(source_path)}:{n}`')
    breakpoints = d.run('bl')

    doc = {'code': source, 'stdin': open(stdin_path, encoding='utf-8').read(), 'problems': [], 'status': 'ok',
           'language': 'cpp', 'compiler': 'MSVC cl /EHsc /std:c++17 /Zi /Od (MQ has no C++ grader)', 'debugger': version,
           'natvis': natvis, 'stepBudget': budget, 'options': {'objects': False}, 'heapTruncated': False, 'trace': []}
    trace = doc['trace']
    frame_ids, return_types, closing, opening = {}, {}, {}, {}
    pending_call = None

    def source_closing(open_line):
        """Line of the `}` that closes the function whose body starts at or after `open_line`."""
        text = source.splitlines()
        depth, started = 0, False
        for n in range(max(open_line, 1), len(text) + 1):
            for ch in re.sub(r'//.*$', '', text[n - 1]):
                if ch == '{': depth += 1; started = True
                elif ch == '}':
                    depth -= 1
                    if started and depth == 0: return n
        return 0

    def function_lines():
        """Closing-brace line of each function = its highest breakpoint line."""
        for line in breakpoints.splitlines():
            m = re.search(r'\d+:\*\*\*\* (\w+)!([^\s+]+)', line)
            if m:
                closing.setdefault(m.group(2), None)
        for fn in closing:
            # The return type is read from the definition in the source (`x /t` prints only parameters).
            m = re.search(r'^\s*((?:\w+\s+)*\w+[\s\*&]*?)\s*\b' + re.escape(fn.split('::')[-1]) + r'\s*\(', source, re.M)
            return_types[fn] = ' '.join(m.group(1).replace('static', '').split()) if m else '?'
            nums = [int(x) for x in re.findall(r'^\s*(\d+) [0-9a-f]{8}`', d.run(f'uf {module}!{fn}'), re.M)] or [0]
            closing[fn] = source_closing(min([n for n in nums if n] or [0])) or max(nums)
            opening[fn] = min([n for n in nums if n] or [0])

    function_lines()

    def declaration_line(func, name):
        """The source line declaring local `name` inside `func` (first match between its first and last line)."""
        base = func.split(' · ')[0]           # a catch funclet looks up its function's locals
        lo, hi = opening.get(base, 0), closing.get(base, 0)
        pat = re.compile(r'(\w+|[>*&\]])(?:\s+|\s*[*&]+\s*)' + re.escape(name) + r'\s*(=|\(|\{|;|\[|,|:(?!:))')
        not_types = {'return', 'delete', 'throw', 'case', 'goto', 'else', 'new', 'sizeof', 'co_return'}
        catch_pat = re.compile(r'catch\s*\(.*[\s*&]' + re.escape(name) + r'\s*\)')
        for n, text in enumerate(source.split('\n'), 1):
            if lo <= n <= hi:
                if catch_pat.search(text):
                    return n - 1        # a catch parameter exists from the moment its handler is entered
                for m in pat.finditer(re.sub(r'//.*$', '', text)):
                    if m.group(1) not in not_types and text[max(0, m.start() - 1):m.start()] not in ('.',):
                        return n
        return None

    def frames():
        out = []
        for line in d.run('kn').splitlines():
            m = FRAME_RE.match(line.strip())
            if m and os.path.normcase(m.group(6)) == src_name:
                line_no = int(m.group(7))
                if out and m.group(5):
                    # A caller's call site is a return address, which already belongs to the next line;
                    # the line of the call is the line of the byte before it.
                    lm = re.search(re.escape(os.path.basename(source_path)) + r' @ (\d+)\]', d.run(f'u {m.group(3)}!{m.group(4)}{m.group(5)}-1 L1'))
                    line_no = int(lm.group(1)) if lm else line_no
                func = re.sub(r'^(.*)\$catch\$\d+$', r'\1 · catch', m.group(4))   # MSVC catch funclet
                out.append({'n': int(m.group(1), 16), 'sp': addr(m.group(2)), 'func': func,
                            'offset': m.group(5), 'line': line_no})
        return out

    def snapshot(event, user, override_line=None):
        heap = {}
        kinds = {}     # (function, name) -> 'param' | 'local'
        cells = []     # (start, size, label) of every local, to name what a pointer points to
        raw = []
        for f in user:
            d.run(f'.frame {f["n"]:x}')
            locals_ = []
            for line in d.run('dv /i /t /v').splitlines():
                km = re.match(r'^\S+ (param|local)\s+(.*)$', line.strip())
                m = DV_RE.match(km.group(2) if km else line.strip())
                if m:
                    a, typ, name, value = addr(m.group(1)), m.group(2).strip(), m.group(3), m.group(4).strip()
                    kinds[(f['func'], name)] = km.group(1) if km else '?'
                    locals_.append((a, typ, name, value))
                    am = re.match(r'(.+?) \[(\d+)\]$', typ)
                    size = SIZES.get(am.group(1), 8) * int(am.group(2)) if am else SIZES.get(typ, 8)
                    cells.append((a, size, f'{name}' + ('' if f is user[-1] else f' ({f["func"]})'),
                                  SIZES.get(am.group(1), 8) if am else None))
            raw.append((f, locals_))
        d.run('.frame 0')

        def pointee(p):
            for start, size, label, elem in cells:
                if start <= p < start + size:
                    return label if elem is None else f'{label}[{(p - start) // elem}]'
            return None

        def scalar(typ, value):
            cm = re.match(r"^(-?\d+) '(.)'$", value)
            if cm:
                return ['CHAR', cm.group(2)]
            if value.startswith('0n'):
                m = re.match(r"0n(-?\d+)(?: '(.*)')?$", value)
                if m and m.group(2) is not None:
                    return ['CHAR', m.group(2)]
                return int(m.group(1)) if m else value
            if typ.endswith('*'):
                m = re.match(r'0x([0-9a-f`]+)', value)
                if not m:
                    return value
                p = int(m.group(1).replace('`', ''), 16)
                if p == 0:
                    return None
                target = pointee(p)
                # The viewer draws arrows only to heap boxes; a pointer to a stack cell is shown as text.
                return ['SPECIAL_FLOAT', f'→ {target}' if target else m.group(0)]
            try:
                return int(value)
            except ValueError:
                pass
            try:
                return float(value)
            except ValueError:
                return value

        stack = []
        destructing_frames = {id(user[k]) for k in range(len(user) - 1) if '~' in user[k + 1]['func']}
        parent_names = set()
        for f, locals_ in raw:
            key = (f['func'], f['sp'])
            fid = frame_ids.setdefault(key, len(frame_ids) + 1)
            if ' · catch' in f['func']:
                # MSVC's catch funclet also lists the enclosing function's locals; they are already drawn
                # in that function's frame, so only the handler's own names (the caught exception) stay.
                locals_ = [l for l in locals_ if l[2] not in parent_names]
            parent_names = {l[2] for l in locals_}
            names, values = [], {}
            not_yet, unknown, ending = [], [], []
            destructing = id(f) in destructing_frames
            for a, typ, name, value in locals_:
                if kinds.get((f['func'], name)) != 'param' and name != 'this':
                    decl = declaration_line(f['func'], name)
                    # A local the line has not reached yet holds whatever was in that memory. An object not yet
                    # constructed is not drawn (natvis would read the garbage as, e.g., an empty vector).
                    if decl is None:
                        values[name] = ['SPECIAL_FLOAT', '(볼 수 없음: 선언 줄을 찾지 못함)']; unknown.append(name); names.append(name); continue
                    if f['line'] <= decl:
                        values[name] = ['SPECIAL_FLOAT', '(아직 선언·생성 전)']; not_yet.append(name); names.append(name); continue
                    if (f['line'] == closing.get(f['func']) or destructing) and typ.startswith(('struct ', 'class ')) and not typ.endswith('*'):
                        # The closing brace runs the destructors: the object's lifetime is ending, so its
                        # memory may already be torn down (an emptied vector is not an empty vector).
                        values[name] = ['SPECIAL_FLOAT', '(수명이 끝나는 중: 소멸자 실행)']; ending.append(name); names.append(name); continue
                if not typ.endswith('*') and (re.search(r'\[\d+\]$', typ) or typ.startswith(('struct ', 'class '))):
                    d.run(f'.frame {f["n"]:x}')
                    lines_ = d.run(f'dx -r1 {name}').splitlines()
                    d.run('.frame 0')
                    head = DX_HEAD.match(lines_[0]) if lines_ else None
                    items = [m for m in (DX_RE.match(l) for l in lines_[1:]) if m]
                    if 'std::basic_string<char' in typ and head and head.group(1).startswith('"'):
                        values[name] = head.group(1)[1:-1]          # natvis text, shown inline like Java/Python strings
                        names.append(name); continue
                    hid = str(len(heap) + 1)
                    if 'std::vector<' in typ:
                        elem = [scalar(m.group(4), m.group(3)) for m in items if re.match(r'\[\d+\]$', m.group(2))]
                        cap = next((m.group(3) for m in items if m.group(2) == '[capacity]'), '?')
                        heap[hid] = ['COLLECTION', f'std::vector (capacity {int(cap, 0) if cap != "?" else "?"})', elem]
                    elif typ.startswith(('struct ', 'class ')):
                        # instance fields only: natvis/static members have no [+0x..] offset
                        heap[hid] = ['INSTANCE', f'{typ} (스택)', *[[m.group(2), scalar(m.group(4), m.group(3))] for m in items if m.group(1)]]
                    else:
                        heap[hid] = ['ARRAY', typ.replace(' [', '[') + ' (스택)', *[scalar(m.group(4), m.group(3)) for m in items]]
                    values[name] = ['REF', int(hid)]
                else:
                    values[name] = scalar(typ, value)
                names.append(name)
            stack.append({'func_name': f['func'], 'frame_id': fid, 'line': f['line'], 'is_highlighted': f is raw[-1][0],
                          'encoded_locals': values, 'ordered_varnames': names,
                          'not_yet_declared': not_yet, 'declaration_not_found': unknown, 'lifetime_ending': ending})
        top = user[-1]
        if event == 'return':
            rtype = return_types.get(top['func'], '?')
            if rtype in INTLIKE:
                m = re.search(r'Evaluate expression: (-?\d+)', d.run('? @eax'))
                if m:
                    value = int(m.group(1)) & 0xFFFFFFFF
                    stack[-1]['ordered_varnames'].append('__return__')
                    stack[-1]['encoded_locals']['__return__'] = value - (1 << 32) if value >= 1 << 31 else value
        out = open(stdout_path, encoding='utf-8', errors='replace').read() if os.path.exists(stdout_path) else ''
        return {'event': event, 'line': override_line or top['line'], 'func_name': top['func'], 'stdout': out,
                'globals': {}, 'ordered_globals': [], 'stack_to_render': stack, 'heap': heap}

    def refs(value, out):
        if isinstance(value, list):
            if len(value) == 2 and value[0] == 'REF': out.add(str(value[1]))
            else:
                for v in value: refs(v, out)
        return out

    def stack_mask(step):
        top = step['stack_to_render'][-1]
        for name in top['ordered_varnames']:
            top['encoded_locals'][name] = ['SPECIAL_FLOAT', '(함수 시작 직후: 아직 준비 전)']
        top['frame_not_ready'] = True
        # drop boxes nothing points to any more (they belonged to the masked frame)
        keep, todo = set(), set()
        for f in step['stack_to_render']:
            refs(list(f['encoded_locals'].values()), todo)
        while todo:
            k = todo.pop()
            if k in keep or k not in step['heap']: continue
            keep.add(k); refs(step['heap'][k], todo)
        step['heap'] = {k: v for k, v in step['heap'].items() if k in keep}
        return step

    while True:
        if time.perf_counter() - started > 20:
            doc['status'] = 'internal_error'; doc['message'] = 'timeout'; break
        hr, event_text = d.go()
        if d.status() == DEBUG_STATUS_NO_DEBUGGEE:
            break
        if 'C++ EH exception' in event_text and 'first chance' in event_text:
            user = frames()
            if user:
                step = snapshot('exception', list(reversed(user)))
                step['exception_msg'] = 'C++ 예외를 던졌어요 (throw)'
                trace.append(step)
            continue                            # `g` passes it on: the program's own catch decides
        if 'Breakpoint' not in event_text:
            # An access violation or other stop the experiment does not handle.
            doc['status'] = 'uncaught_exception'
            if trace:
                last = dict(trace[-1]); last.update(event='uncaught_exception', exception_msg=event_text.strip()[:200])
                trace.append(last)
            break
        user = frames()
        if not user:
            continue
        top = user[0]                          # kn lists the innermost frame first
        user = list(reversed(user))            # stack_to_render is outermost first
        if len(trace) >= budget:
            last = dict(trace[-1]); last['event'] = 'instruction_limit_reached'; trace.append(last)
            doc['status'] = 'step_limit'; break
        if top['offset'] is None:
            # First byte of a function, before its prolog: the call is real (this is the function the
            # program actually entered, e.g. the overriding area()), but its frame is not set up, so its
            # values are not shown. A one-line function is only ever seen here.
            step = snapshot('call', user)
            masked = stack_mask(step)
            trace.append(masked)
            continue
        event = 'return' if closing.get(top['func']) == top['line'] else 'step_line'
        trace.append(snapshot(event, user))
    d.close()
    doc['stdout'] = open(stdout_path, encoding='utf-8', errors='replace').read() if os.path.exists(stdout_path) else ''
    doc['timing'] = {'seconds': round(time.perf_counter() - started, 3)}
    json.dump(doc, open(out_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{os.path.basename(out_path)}: status={doc["status"]} steps={len(trace)} seconds={doc["timing"]["seconds"]}')


if __name__ == '__main__':
    main()
