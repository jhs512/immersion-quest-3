"""C code flow from the UNMODIFIED tcc 0.9.27 program (experiment; not wired into the app).

1. Verify first (hybrid2.main): the twin and the original agree on every value the twin knows, the original's
   output equals the grader's, and every variable has a location. Otherwise the document is
   `status: unsupported` with the reason and NO steps (a wrong trace is never shown).
2. Run the original under the debugger. Steps are only the original's real line stops (no invented steps:
   a declaration line has no stop of its own in tcc 0.9.27's line table; its effect shows at the next stop).
   Frames come from the rbp chain mapped through the STABS functions. A frame shows exactly the variables in
   lexical scope at its line (the twin's record for that function and line), read from the original's memory.
   Heap blocks are the original's own malloc/calloc/realloc results. Values are decoded with the parsed types
   (mq_cinstr.decode); nothing is normalized: an uninitialized variable shows its real bytes and is flagged.
3. Not observable here, and therefore not shown: the output printed so far at each step (the original's
   stdout is buffered until exit; the last step shows the full output), return values.
usage: <ml-env python> -I -X utf8 c_flow.py <case_dir>  -> <case_dir>/c_flow.json
"""
import json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import c_verify as hybrid2                                            # noqa: E402
from c_verify import Instrumenter, TCC, Debugger, DEBUG_STATUS_NO_DEBUGGEE, stab_table, pe_sections, section_of, read_bytes, reg  # noqa: E402
from c_instrument import decode                             # noqa: E402


def main(case):
    case = os.path.abspath(case)
    out_path = os.path.join(case, 'c_flow.json')
    src = open(os.path.join(case, 'src.c'), encoding='utf-8').read()
    stdin_path = os.path.join(case, 'stdin.txt')
    built = subprocess.run([TCC, '-g', '-o', os.path.join(case, 'orig_g.exe'), os.path.join(case, 'src.c')], capture_output=True)
    if built.returncode:
        text = built.stderr.decode('utf-8', 'replace')
        problems = [{'line': int(m.group(1)), 'error': True, 'message': m.group(2).strip()}
                    for m in re.finditer(r'src\.c:(\d+): (?:error|warning): (.*)', text)] or [{'line': 0, 'error': True, 'message': text.strip()[-300:]}]
        doc = {'code': src, 'language': 'c', 'status': 'compile_error', 'problems': problems, 'trace': []}
        json.dump(doc, open(out_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(f'{os.path.basename(case)}: compile_error'); return doc
    # a second dbgeng session in one process crashed earlier: the check runs in its own process
    subprocess.run([sys.executable, '-I', '-X', 'utf8', os.path.join(HERE, 'c_verify.py'), case], capture_output=True, timeout=180)
    path = os.path.join(case, 'hybrid2.json')
    check = json.load(open(path, encoding='utf-8')) if os.path.exists(path) else {'error': '검증을 실행하지 못했어요'}
    doc = {'code': src, 'stdin': open(stdin_path, encoding='utf-8').read(), 'language': 'c', 'problems': [],
           'compiler': 'TinyCC 0.9.27 (the grader) - the unmodified program under the Windows debugger',
           'stepBudget': 1000, 'options': {'objects': False}, 'heapTruncated': False, 'trace': [], 'verification': check}
    reasons = []
    if 'error' in check: reasons.append(check['error'])
    else:
        if check['mismatch_count']: reasons.append(f"원본과 계측본의 값이 {check['mismatch_count']}개 달라요")
        if check['unmapped_count']: reasons.append(f"위치를 모르는 변수가 {check['unmapped_count']}개 있어요")
        if check['layout_inconsistent']: reasons.append('변수 위치가 단계마다 달라요')
        if not check['orig_stdout_equals_grader']: reasons.append('원본 실행의 출력이 채점과 달라요')
        if not check['twin_stdout_equals_grader']: reasons.append('계측 실행의 출력이 채점과 달라 위치를 검증할 수 없어요')
        if check.get('twin_step_limit'): reasons.append('1000단계 안에 끝나지 않아 위치를 끝까지 검증하지 못했어요')
    if reasons:
        doc.update(status='unsupported', message=' / '.join(reasons))
        json.dump(doc, open(out_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(f'{os.path.basename(case)}: unsupported ({doc["message"]})'); return doc

    ins = Instrumenter(src).run()
    # lexical scope: which variables the twin had registered in a frame of (function, line)
    scope, layout = {}, {}
    cur = None
    for line in open(os.path.join(case, 'mq_trace.txt'), encoding='utf-8').read().split('\n'):
        p = line.split(' ')
        if p[0] == 'S': cur = {'frames': [], 'vars': []}
        elif p[0] == 'F': cur['frames'].append((int(p[1]), int(p[2], 16), int(p[3])))
        elif p[0] == 'V':
            fa, vid, addr = int(p[1], 16), int(p[2]), int(p[3], 16)
            fr = next((f for f in cur['frames'] if f[1] == fa), None)
            if fr is None: continue
            scope.setdefault((fr[0], fr[2]), set()).add(vid)
            layout[vid] = ('frame', addr - fa, int(p[4])) if abs(addr - fa) < hybrid2.NEAR else ('data', addr, int(p[4]))
    twin_secs = pe_sections(os.path.join(case, 'twin.exe')) if os.path.exists(os.path.join(case, 'twin.exe')) else None
    if twin_secs is None:   # hybrid2 removed it; rebuild the twin the same way (same bytes)
        subprocess.run([TCC, '-g', '-o', 'twin.exe', 'twin_user.c', 'twin_rt.c'], cwd=case, check=True, capture_output=True)
        twin_secs = pe_sections(os.path.join(case, 'twin.exe'))
    for vid, where in list(layout.items()):
        if where[0] == 'data':
            sec = section_of(twin_secs, where[1]); layout[vid] = ('data', sec[0], sec[1], where[2])

    code_lines = __import__('c_instrument').blank_comments(src).split(chr(10))

    def scope_end(vid):
        """Last line of the block a variable lives in (a `for (int i...)` variable: the loop's body)."""
        v = ins.vars[vid]
        if v.get('global') or v.get('static') and False: return 10 ** 9
        start = v['line'] - 1
        is_for = 'for' in code_lines[start].split(v['name'])[0]
        depth, opened = 0, False
        for n in range(start, len(code_lines)):
            text = code_lines[n] if n > start else code_lines[n][code_lines[n].find(v['name']):] if not is_for else code_lines[n]
            for ch in text:
                if ch == '{': depth += 1; opened = True
                elif ch == '}':
                    depth -= 1
                    if depth < 0 or (is_for and opened and depth == 0): return n + 1
            if is_for and not opened and n > start and ';' in text: return n + 1   # brace-less loop body
        return 10 ** 9

    exe = os.path.join(case, 'orig_g.exe')
    subprocess.run([TCC, '-g', '-o', exe, os.path.join(case, 'src.c')], check=True, capture_output=True)
    orig_secs = pe_sections(exe)
    funcs, lines = stab_table(exe)
    starts = {f['start'] for f in funcs}
    fn_at = lambda a: next((f for f in funcs if f['start'] <= a < f.get('end', 0)), None)
    fid_of = {f['name']: f['id'] for f in ins.funcs}
    line_addrs = sorted(lines)
    line_at = lambda a: next((lines[x] for x in reversed(line_addrs) if x <= a and fn_at(x) is fn_at(a)), None)
    stdout_file = os.path.join(case, 'c_flow_stdout.txt')
    dbg = Debugger(f'"{exe}"', stdin_path, stdout_file)
    for a in line_addrs:
        if a not in starts: dbg.run(f'bp 0x{a:x}')
    leave_at = {}
    for f in funcs:
        end = f.get('end', 0)
        # `leave; ret` is how tcc 0.9.27 ends every function; the STABS end can include alignment padding
        tail = read_bytes(dbg, end - 16, 16) if end else ''
        k = max((i for i in range(0, len(tail) - 3, 2) if tail[i:i + 4] == 'c9c3'), default=None)
        if k is not None:
            at = end - 16 + k // 2
            leave_at[at] = f; dbg.run(f'bp 0x{at:x}')
    # the C runtime's stdout FILE (msvcrt _iob[1]): bytes already printed but still in its buffer
    m = re.search(r'([0-9a-f`]{17})\s', dbg.run('x msvcrt!_iob'))
    stdout_file_struct = int(m.group(1).replace('`', ''), 16) + 48 if m else None
    alloc_fn = {}
    for name in ('malloc', 'calloc', 'realloc', 'free'):
        m = re.search(r'([0-9a-f`]{17})\s', dbg.run(f'x msvcrt!{name}'))
        if m: a = int(m.group(1).replace('`', ''), 16); alloc_fn[a] = name; dbg.run(f'bp 0x{a:x}')
    records, blocks, serial, pending, last, seen_frames, hits = [], {}, 0, {}, None, set(), 0
    freed, outputs, also, prev_line = {}, [], [], {}
    status, crash = 'ok', None
    while True:
        dbg.go()
        if dbg.status() == DEBUG_STATUS_NO_DEBUGGEE: break
        hits += 1
        if hits > 20000 or len(records) >= 1000: status = 'step_limit'; break
        ev = dbg.run('.lastevent')
        if 'Breakpoint' not in ev and 'Hit breakpoint' not in ev and 'break instruction' not in ev.lower():
            if 'Exit process' not in ev:
                m = re.search(r'(Access violation|Stack overflow|Integer divide-by-zero|[A-Za-z ]+exception) - code ([0-9a-f]+)', ev)
                names = {'c0000005': '잘못된 메모리 접근', 'c00000fd': '스택 넘침', 'c0000094': '0으로 나누기'}
                status, crash = 'uncaught_exception', (f"{names.get(m.group(2), m.group(1))} (0x{m.group(2).upper()})" if m else ev.strip().split(chr(10))[0][-120:])
            break
        rip = reg(dbg, 'rip')
        if rip in pending:
            kind, size, old = pending.pop(rip); ptr = reg(dbg, 'rax')
            if kind == 'realloc' and old in blocks and (ptr or size == 0): freed[old] = blocks.pop(old)
            if ptr: serial += 1; blocks[ptr] = (size, serial)
            if rip not in lines: continue
        if rip in alloc_fn:
            ret = int.from_bytes(bytes.fromhex(read_bytes(dbg, reg(dbg, 'rsp'), 8)), 'little')
            if not fn_at(ret): continue
            kind = alloc_fn[rip]; rcx, rdx = reg(dbg, 'rcx'), reg(dbg, 'rdx')
            if kind == 'free':
                if rcx in blocks: freed[rcx] = blocks.pop(rcx)
                continue
            pending[ret] = (kind, rcx if kind == 'malloc' else rcx * rdx if kind == 'calloc' else rdx, rcx if kind == 'realloc' else None)
            if ret not in lines: dbg.run(f'bp /1 0x{ret:x}')
            continue
        rbp = reg(dbg, 'rbp')
        returning = rip in leave_at
        if returning: last = None
        elif last == (rip, rbp) or last == (lines.get(rip), fn_at(rip)['name'] if fn_at(rip) else None, rbp): continue
        last = (lines.get(rip), fn_at(rip)['name'] if fn_at(rip) else None, rbp)
        chain, b, a = [], rbp, rip     # innermost first: (fid, frame address, line)
        while True:
            f = fn_at(a)
            if not f or f['name'] not in fid_of: break
            chain.append((fid_of[f['name']], b, (lines.get(a) or line_at(a)) if not chain else line_at(a)))
            if f['name'] == 'main': break
            a = int.from_bytes(bytes.fromhex(read_bytes(dbg, b + 8, 8)), 'little') - 1
            b = int.from_bytes(bytes.fromhex(read_bytes(dbg, b, 8)), 'little')
        chain.reverse()
        top = chain[-1]
        event = 'return' if returning else 'call' if (top[0], top[1]) not in seen_frames else 'step_line'
        seen_frames = {(c[0], c[1]) for c in chain}
        rec = [f'S {event} {top[2]} -1 {reg(dbg, "rax") if returning else 0}']
        # declarations the line table has no stop for, run since this frame's previous stop
        before = prev_line.get((top[0], top[1]))
        decls = sorted({v['line'] for v in ins.vars if v['fid'] == top[0] and not v.get('global') and before is not None and before < v['line'] < top[2]})
        also.append(decls)
        prev_line[(top[0], top[1])] = top[2]
        # output so far: what reached the file + what the C runtime still holds in stdout's buffer
        done = open(stdout_file, 'rb').read() if os.path.exists(stdout_file) else b''
        held = b''
        if stdout_file_struct:
            ptr = int.from_bytes(bytes.fromhex(read_bytes(dbg, stdout_file_struct, 8)), 'little')
            base = int.from_bytes(bytes.fromhex(read_bytes(dbg, stdout_file_struct + 16, 8)), 'little')
            if base and 0 < ptr - base <= 65536: held = bytes.fromhex(read_bytes(dbg, base, ptr - base))
        outputs.append((done + held).decode('utf-8', 'replace').replace('\r\n', '\n'))
        for fid, fa, ln in chain:
            rec.append(f'F {fid} {fa:x} {ln}')
        main_fa = chain[0][1]
        for fid, fa, ln in chain:
            for vid in sorted(v for v in scope.get((fid, ln), ()) if ln <= scope_end(v)):
                where = layout.get(vid)
                if not where: continue
                if where[0] == 'frame':
                    addr = fa + where[1]
                else:
                    base = next(s for n, s, z in orig_secs if n == where[1]); addr = base + where[2]
                    if ins.vars[vid].get('global') and fa != main_fa: continue   # a global is drawn once, in main's frame
                rec.append(f'V {fa:x} {vid} {addr:x} {where[-1]} ' + read_bytes(dbg, addr, min(where[-1], 256)))
        for a2, (size, ser) in blocks.items():
            rec.append(f'H {a2:x} {size} {ser} ' + read_bytes(dbg, a2, min(size, 256)))
        for a2, (size, ser) in freed.items():
            rec.append(f'X {a2:x} {size}')
        records.append('\n'.join(rec))
    dbg.close()
    for f in (exe, os.path.join(case, 'twin.exe')):
        try: os.remove(f)
        except OSError: pass
    text = '\n'.join(records)
    layout_lines = [l for l in open(os.path.join(case, 'mq_trace.txt'), encoding='utf-8').read().split('\n') if l.startswith('L ')]
    steps = decode(ins, '\n'.join(layout_lines) + '\n' + text, b'', src)
    final = open(stdout_file, 'rb').read().decode('utf-8', 'replace').replace('\r\n', '\n')
    # each step's output must be a prefix of the program's final output; otherwise no step shows any
    # (the last step still shows the whole output)
    per_step = len(outputs) <= len(steps) and all(final.startswith(o) for o in outputs)
    for i, st in enumerate(steps[:len(outputs)]):
        st['stdout'] = outputs[i] if per_step else ''
        if also[i]: st['also_ran_lines'] = also[i]
    if steps:
        steps[-1]['stdout'] = final
        if status == 'uncaught_exception':
            last_step = dict(steps[-1]); last_step.update(event='uncaught_exception', exception_msg=f'프로그램이 멈췄어요: {crash}'); steps.append(last_step)
        if status == 'step_limit':
            last_step = dict(steps[-1]); last_step['event'] = 'instruction_limit_reached'; steps.append(last_step)
    # small stable frame ids per (function, frame address) run
    ids, nxt = {}, 1
    for st in steps:
        for fr in st['stack_to_render']:
            k = (fr['func_name'], fr['frame_id'])
            if st['event'] == 'call' and fr is st['stack_to_render'][-1] or k not in ids: ids[k] = nxt; nxt += 1
            fr['frame_id'] = ids[k]
    doc.update(status=status, trace=steps, stdout=final, stdout_per_step=per_step)
    json.dump(doc, open(out_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{os.path.basename(case)}: {status} steps={len(steps)}')
    return doc


if __name__ == '__main__':
    main(sys.argv[1])
