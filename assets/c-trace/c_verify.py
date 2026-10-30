"""Hybrid check v2: every value the instrumented twin knows, read from the UNMODIFIED tcc 0.9.27 program.

Fixes over hybrid_check.py (whose numbers were: 792 targeted, 751 matched, 41 heap and 18 static skipped):
  - the twin is built like the original (`tcc -g -o`), with the runtime as a SECOND translation unit after the
    learner's, so the learner's globals and statics keep the original's section offsets; a static/global is
    read in the original at the same section + offset (globals are registered at main's start);
  - heap blocks of the original are followed by the debugger itself: breakpoints on msvcrt!malloc/calloc/
    realloc/free called from the learner's code, the result read at the return address. A pointer into a block
    is compared as (allocation number, offset) with the twin's runtime record of the same allocation;
  - stack pointers are compared relative to main's frame (the two programs' stacks start at different places).
Nothing is skipped silently: every targeted value ends as exact / stack-relative / heap / static match,
or a mismatch, or "unmapped" with a reason.
usage: <ml-env python> -I -X utf8 hybrid2.py <case_dir>    (case_dir holds src.c and stdin.txt)  -> hybrid2.json
"""
import json, os, re, struct, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from c_instrument import Instrumenter, TCC, Unsupported          # noqa: E402
from dbgeng import Debugger, DEBUG_STATUS_NO_DEBUGGEE   # noqa: E402
from stabs import stab_table             # noqa: E402

RT = open(os.path.join(HERE, 'mq_rt.c'), encoding='utf-8').read()
MACROS = [l for l in RT.split('\n') if l.startswith('#define ') and '__mq_' in l]
RT_IMPL = '\n'.join(l for l in RT.split('\n') if l not in MACROS)
HEADER = '\n'.join([
    '#include <stdio.h>', '#include <stdlib.h>', '#include <string.h>', '#include <stddef.h>',
    'void __mq_enter(int, int, char *);', 'void __mq_called(int);', 'void __mq_var(int, void *, int, char *);',
    'void __mq_line(int, char *);', 'long long __mq_ret(int, char *, long long);', 'void *__mq_malloc(size_t);',
    'void __mq_free(void *);', 'void *__mq_calloc(size_t, size_t);', 'void *__mq_realloc(void *, size_t);'] + MACROS) + '\n'
NEAR = 1 << 20


def pe_sections(path):
    b = open(path, 'rb').read(); pe = struct.unpack_from('<I', b, 0x3c)[0]; n = struct.unpack_from('<H', b, pe + 6)[0]
    base = struct.unpack_from('<Q', b, pe + 24 + 24)[0]
    o = pe + 24 + struct.unpack_from('<H', b, pe + 20)[0]; out = []
    for i in range(n):
        name = b[o + 40 * i:o + 40 * i + 8].rstrip(b'\0').decode(); vs, va = struct.unpack_from('<II', b, o + 40 * i + 8)
        out.append((name, base + va, vs))
    return out


def section_of(secs, addr):
    for name, start, size in secs:
        if start <= addr < start + max(size, 1):
            return name, addr - start
    return None


def read_bytes(dbg, addr, size):
    out = ''
    for line in dbg.run(f'db 0x{addr:x} L0x{size:x}').splitlines():
        parts = line.split('  ')
        if len(parts) > 1:
            out += ''.join(re.findall(r'[0-9a-f]{2}', parts[1].replace('-', ' ')))
    return out


def reg(dbg, name):
    return int(re.search(name + r'=([0-9a-f]+)', dbg.run(f'r {name}')).group(1), 16)


def main(case):
    case = os.path.abspath(case)
    src = open(os.path.join(case, 'src.c'), encoding='utf-8').read()
    stdin_path = os.path.join(case, 'stdin.txt')
    try:
        ins = Instrumenter(src).run()
    except Unsupported as e:
        result = {'case': os.path.basename(case), 'error': f'{e} 코드는 아직 코드 흐름 보기를 지원하지 않아요', 'unsupported': str(e)}
        json.dump(result, open(os.path.join(case, 'hybrid2.json'), 'w', encoding='utf-8'), ensure_ascii=False); return result
    except Exception as e:      # pycparser could not read it (e.g. inline assembly, unusual macros)
        result = {'case': os.path.basename(case), 'error': 'C 코드 구조를 해석하지 못해 코드 흐름을 확인할 수 없어요', 'unsupported': type(e).__name__}
        json.dump(result, open(os.path.join(case, 'hybrid2.json'), 'w', encoding='utf-8'), ensure_ascii=False); return result
    full = ins.output()
    assert full.startswith(RT)
    open(os.path.join(case, 'twin_user.c'), 'w', encoding='utf-8', newline='').write(HEADER + full[len(RT):])
    open(os.path.join(case, 'twin_rt.c'), 'w', encoding='utf-8', newline='').write(RT_IMPL)
    built = subprocess.run([TCC, '-g', '-o', 'twin.exe', 'twin_user.c', 'twin_rt.c'], cwd=case, capture_output=True)
    if built.returncode:
        result = {'case': os.path.basename(case), 'error': '추적용 사본을 컴파일하지 못했어요: ' + built.stderr.decode('utf-8', 'replace')[-300:]}
        json.dump(result, open(os.path.join(case, 'hybrid2.json'), 'w', encoding='utf-8'), ensure_ascii=False); return result
    if os.path.exists(os.path.join(case, 'mq_trace.txt')): os.remove(os.path.join(case, 'mq_trace.txt'))
    with open(stdin_path, 'rb') as si, open(os.path.join(case, 'twin_stdout.txt'), 'wb') as so:
        twin_run = subprocess.run([os.path.join(case, 'twin.exe')], cwd=case, stdin=si, stdout=so, timeout=20)
    graded = subprocess.run([TCC, '-run', 'src.c'], cwd=case, stdin=open(stdin_path, 'rb'), capture_output=True, timeout=20)
    twin_secs = pe_sections(os.path.join(case, 'twin.exe'))
    twin_funcs, _ = stab_table(os.path.join(case, 'twin.exe'))

    # ---- twin records
    steps, cur, twin_limit = [], None, False
    for line in open(os.path.join(case, 'mq_trace.txt'), encoding='utf-8').read().split('\n'):
        p = line.split(' ')
        if p[0] == 'S': cur = {'event': p[1], 'line': int(p[2]), 'frames': [], 'vars': [], 'blocks': {}}; steps.append(cur)
        elif p[0] == 'F': cur['frames'].append((int(p[1]), int(p[2], 16)))
        elif p[0] == 'V': cur['vars'].append((int(p[1], 16), int(p[2]), int(p[3], 16), int(p[4]), p[5] if len(p) > 5 else ''))
        elif p[0] == 'H': cur['blocks'][int(p[1], 16)] = (int(p[2]), int(p[3]))
        elif p[0] == 'LIMIT': twin_limit = True
    layout, inconsistent = {}, []
    for st in steps:
        for fa, vid, addr, size, _ in st['vars']:
            fid = next((f for f, a in st['frames'] if a == fa), None)
            if fid is None:
                continue                         # frame record cut off (step limit or crash); counted below
            if abs(addr - fa) < NEAR:
                where = ('frame', addr - fa, size)
            else:
                sec = section_of(twin_secs, addr)
                where = ('data', sec[0], sec[1], size) if sec else ('unmapped', 'outside the image', size)
            prev = layout.get((fid, vid))
            if prev and prev != where: inconsistent.append(((fid, vid), prev, where))
            layout[(fid, vid)] = where
    expected, history = {}, {}
    for st in steps:
        history.update(st['blocks'])            # every block the twin ever had, freed ones included
        if st['event'] != 'step_line' or not st['frames']: continue
        fid, fa = st['frames'][-1]
        vals = {vid: hx for vfa, vid, a, s, hx in st['vars'] if vfa == fa or layout.get((fid, vid), ('',))[0] == 'data'}
        # globals belong to main's frame record; at a step in another function they are still readable
        gl = {vid: hx for vfa, vid, a, s, hx in st['vars'] if ins.vars[vid].get('global')}
        vals.update(gl)
        expected.setdefault((ins.funcs[fid]['name'], st['line']), []).append((fid, vals, st['frames'][0][1], dict(st['blocks']), dict(history)))

    # ---- original program under the debugger
    exe = os.path.join(case, 'orig_g.exe')
    subprocess.run([TCC, '-g', '-o', exe, os.path.join(case, 'src.c')], check=True, capture_output=True)
    orig_secs = pe_sections(exe)
    funcs, lines = stab_table(exe)
    starts = {f['start'] for f in funcs}
    in_user = lambda a: any(f['start'] <= a < f.get('end', 0) for f in funcs)
    dbg = Debugger(f'"{exe}"', stdin_path, os.path.join(case, 'orig_stdout.txt'))
    for a in sorted(lines):
        if a not in starts: dbg.run(f'bp 0x{a:x}')
    alloc_fn = {}
    for name in ('malloc', 'calloc', 'realloc', 'free'):
        m = re.search(r'([0-9a-f`]{17})\s', dbg.run(f'x msvcrt!{name}'))
        if m:
            a = int(m.group(1).replace('`', ''), 16); alloc_fn[a] = name; dbg.run(f'bp 0x{a:x}')
    blocks, ohistory, serial, pending, visits, orig_main, last, hits = {}, {}, 0, {}, [], None, None, 0
    while True:
        dbg.go()
        if dbg.status() == DEBUG_STATUS_NO_DEBUGGEE: break
        hits += 1
        if hits > 5000: break
        rip = reg(dbg, 'rip')
        if rip in pending:                      # return address of an allocation from the learner's code
            kind, size, old = pending.pop(rip)
            ptr = reg(dbg, 'rax')
            if kind == 'realloc' and old in blocks and (ptr or size == 0): blocks.pop(old)
            if ptr: serial += 1; blocks[ptr] = (size, serial); ohistory[ptr] = (size, serial)
            if rip not in lines: continue
        if rip in alloc_fn:
            ret = int.from_bytes(bytes.fromhex(read_bytes(dbg, reg(dbg, 'rsp'), 8)), 'little')   # return address
            if not in_user(ret): continue       # the C runtime's own allocations are not the learner's
            kind = alloc_fn[rip]; rcx, rdx = reg(dbg, 'rcx'), reg(dbg, 'rdx')
            if kind == 'free': blocks.pop(rcx, None); continue
            size = rcx if kind == 'malloc' else rcx * rdx if kind == 'calloc' else rdx
            pending[ret] = (kind, size, rcx if kind == 'realloc' else None)
            if ret not in lines: dbg.run(f'bp /1 0x{ret:x}')
            continue
        rbp = reg(dbg, 'rbp')
        f = next((f for f in funcs if f['start'] <= rip < f.get('end', 0)), None)
        key = (f['name'] if f else None, lines.get(rip))
        if orig_main is None and key[0] == 'main': orig_main = rbp
        if last == (key, rbp): continue
        last = (key, rbp)
        fid = next((x['id'] for x in ins.funcs if x['name'] == key[0]), None)
        mem = {}
        for (lfid, vid), where in layout.items():
            if where[0] == 'frame' and lfid == fid: mem[vid] = read_bytes(dbg, rbp + where[1], min(where[2], 256))
            elif where[0] == 'data':
                base = next((s for n, s, z in orig_secs if n == where[1]), None)
                if base is not None: mem[vid] = read_bytes(dbg, base + where[2], min(where[3], 256))
        visits.append((key, mem, dict(blocks), dict(ohistory)))
    dbg.close()

    def fn_at(table, a):
        return next((f['name'] for f in table if f['start'] == a), None)

    def heap_pos(p, table):          # (allocation number, offset) of a pointer into a known block
        for a, (size, ser) in table.items():
            if a <= p < a + max(size, 1): return (ser, p - a)
        return None

    counts = {}
    for key, *_ in visits: counts[key] = counts.get(key, 0) + 1
    aligned = {k for k in counts if k in expected and counts[k] == len(expected[k])}
    unaligned = sorted(str(k) for k in counts if k in expected and k not in aligned)
    tally = {'exact': 0, 'stack_relative': 0, 'heap': 0, 'freed_block': 0, 'function_pointer': 0, 'static_or_global': 0}
    mismatch, unmapped, seen, targeted, uninit_diff = [], [], {}, 0, []
    for key, mem, oblocks, ohist in visits:
        k = seen.get(key, 0); seen[key] = k + 1
        if key not in aligned: continue
        fid, vals, twin_main, tblocks, thist = expected[key][k]
        for vid, hx in vals.items():
            targeted += 1
            where = layout.get((fid, vid)) or layout.get(next(((f, v) for (f, v) in layout if v == vid), None))
            if where is None or where[0] == 'unmapped' or vid not in mem:
                unmapped.append({'var': ins.vars[vid]['name'], 'why': where[1] if where else 'no layout'}); continue
            got, n = mem[vid], 2 * min(where[-1], 256)
            if got[:n] == hx[:n]:
                tally['static_or_global' if where[0] == 'data' else 'exact'] += 1; continue
            verdict = 'same'
            if where[-1] % 8 == 0 and orig_main is not None and len(got) >= n:
                for i in range(0, n, 16):
                    if got[i:i + 16] == hx[i:i + 16]: continue
                    a = int.from_bytes(bytes.fromhex(hx[i:i + 16]), 'little'); b = int.from_bytes(bytes.fromhex(got[i:i + 16]), 'little')
                    if abs(a - twin_main) < NEAR and abs(b - orig_main) < NEAR and a - twin_main == b - orig_main: continue
                    # a function pointer: the two binaries place code differently, so compare WHICH function
                    tfn, ofn = fn_at(twin_funcs, a), fn_at(funcs, b)
                    if tfn and tfn == ofn: verdict = 'function' if verdict != 'heap' else verdict; continue
                    ta, ob = heap_pos(a, tblocks), heap_pos(b, oblocks)
                    if ta and ta == ob: verdict = 'heap'; continue
                    # a dangling pointer: both point into the same allocation that has been freed
                    tf, of = heap_pos(a, thist), heap_pos(b, ohist)
                    if not ta and not ob and tf and tf == of: verdict = 'freed'; continue
                    verdict = 'diff'; break
            else:
                verdict = 'diff'
            if verdict == 'diff' and not ins.vars[vid]['has_init'] and not ins.vars[vid].get('static'):
                # declared without an initializer: memory it never wrote differs between two runs by nature.
                # The original's value is the one shown; it is NOT counted as a match.
                uninit_diff.append({'func': key[0], 'line': key[1], 'var': ins.vars[vid]['name'], 'twin': hx[:64], 'orig': got[:64]})
            elif verdict == 'diff':
                mismatch.append({'func': key[0], 'line': key[1], 'visit': k, 'var': ins.vars[vid]['name'], 'twin': hx[:32], 'orig': got[:32]})
            else:
                tally[{'heap': 'heap', 'freed': 'freed_block', 'function': 'function_pointer'}.get(verdict, 'stack_relative')] += 1
    norm = lambda b: b.replace(b'\r\n', b'\n')
    result = {'case': os.path.basename(case), 'targeted': targeted, **tally, 'mismatch_count': len(mismatch), 'uninitialized_differs_count': len(uninit_diff), 'uninitialized_differs': uninit_diff[:10],
              'mismatches': mismatch[:10], 'unmapped_count': len(unmapped), 'unmapped': unmapped[:10],
              'unaligned_lines': unaligned, 'layout_inconsistent': len(inconsistent), 'breakpoint_hits': hits, 'twin_step_limit': twin_limit,
              'orig_stdout_equals_grader': norm(open(os.path.join(case, 'orig_stdout.txt'), 'rb').read()) == norm(graded.stdout),
              'twin_stdout_equals_grader': norm(open(os.path.join(case, 'twin_stdout.txt'), 'rb').read()) == norm(graded.stdout),
              'twin_exit_equals_grader': (twin_run.returncode == 0) == (graded.returncode == 0)}
    json.dump(result, open(os.path.join(case, 'hybrid2.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for f in ('orig_g.exe', 'twin.exe'):
        try: os.remove(os.path.join(case, f))
        except OSError: pass
    print(f"{result['case']}: targeted={targeted} exact={tally['exact']} stack_rel={tally['stack_relative']} heap={tally['heap']} "
          f"freed={tally['freed_block']} fnptr={tally['function_pointer']} static/global={tally['static_or_global']} mismatch={len(mismatch)} uninit_diff={len(uninit_diff)} unmapped={len(unmapped)} unaligned={len(unaligned)} "
          f"layout_inconsistent={len(inconsistent)} orig_out==grader={result['orig_stdout_equals_grader']} twin_out==grader={result['twin_stdout_equals_grader']}")
    return result


if __name__ == '__main__':
    main(sys.argv[1])
