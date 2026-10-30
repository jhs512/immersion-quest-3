"""Experimental C code-flow by SOURCE INSTRUMENTATION, compiled and run by the grader's own TinyCC
0.9.27 in the grader's own mode (`tcc -run`). NOT integrated into the app.

1. pycparser (already in MQ's managed Python, as a cffi dependency) parses main.c. Only the structure
   is needed: #-lines are blanked for the parser, the original text is what gets compiled.
2. Calls are inserted at the START OF SOURCE LINES only (never inside an expression):
     function body:   __mq_enter(fid, line, fa); __mq_var(param...); __mq_called(line);
     each statement:  __mq_var(variables declared by the previous item...); __mq_line(line, fa);
     `return E;` in an integer function: return (T)__mq_ret(line, fa, (long long)(E));
   fa = __builtin_frame_address(0). Each __mq_var passes &name and sizeof(name): the compiler, not this
   script, decides addresses, sizes and struct layouts (offsetof table emitted at the end of the file).
3. The runtime (mq_rt.c) copies the bytes of live variables and of malloc blocks at every step. It never
   follows a learner pointer. This script decodes the bytes with the parsed types: raw values are kept
   as they are (an uninitialized int shows whatever was in memory; nothing is normalized).

usage: <ml-env python> -I -X utf8 mq_cinstr.py main.c stdin.txt out_dir
       -> out_dir/main_mq.c, mq_trace.txt, stdout.txt, trace.json, grader_stdout.txt
"""
import json, os, re, struct, subprocess, sys, time
from pycparser import c_parser, c_ast

HERE = os.path.dirname(os.path.abspath(__file__))
TCC = os.environ['MQ_TCC']   # the grader's TinyCC (src/lesson_runner.rs)
PRELUDE = ('typedef int FILE; typedef unsigned long long size_t; typedef int bool; typedef long long int64_t;'
           ' typedef int int32_t; typedef unsigned int uint32_t; typedef unsigned char uint8_t; typedef long long ptrdiff_t;\n')
FA = '__builtin_frame_address(0)'
BASE = {  # Windows x64 (LLP64), as TinyCC lays them out
    'char': (1, True), 'signed char': (1, True), 'unsigned char': (1, False), 'short': (2, True), 'short int': (2, True),
    'unsigned short': (2, False), 'int': (4, True), 'signed': (4, True), 'signed int': (4, True), 'unsigned': (4, False),
    'unsigned int': (4, False), 'long': (4, True), 'long int': (4, True), 'unsigned long': (4, False), 'long long': (8, True),
    'long long int': (8, True), 'unsigned long long': (8, False), 'size_t': (8, False), 'int64_t': (8, True), 'int32_t': (4, True),
    'uint32_t': (4, False), 'uint8_t': (1, False), 'bool': (4, True), '_Bool': (1, False), 'ptrdiff_t': (8, True)}
FLOATS = {'float': 4, 'double': 8, 'long double': 8}


def blank_comments(text):
    """Comments become spaces (newlines kept), so every line and column stays where it was."""
    out, i, n = list(text), 0, len(text)
    while i < n:
        c = text[i]
        if c in '"\'':
            j = i + 1
            while j < n and text[j] != c and text[j] != '\n':
                j += 2 if text[j] == '\\' else 1
            i = j + 1
        elif text.startswith('//', i):
            while i < n and text[i] != '\n': out[i] = ' '; i += 1
        elif text.startswith('/*', i):
            j = text.find('*/', i + 2); j = n if j < 0 else j + 2
            for k in range(i, j):
                if text[k] != '\n': out[k] = ' '
            i = j
        else:
            i += 1
    return ''.join(out)


class Unsupported(Exception):
    """Code this tracer cannot show correctly. The learner gets the reason instead of a trace."""


# Calls that change control flow or memory in ways the trace cannot follow.
UNSUPPORTED_CALLS = {'setjmp': 'setjmp/longjmp', 'longjmp': 'setjmp/longjmp', '_setjmp': 'setjmp/longjmp',
                     'alloca': 'alloca', '_alloca': 'alloca', 'signal': 'signal', 'raise': 'signal',
                     '_beginthread': '스레드', '_beginthreadex': '스레드', 'CreateThread': '스레드', 'thrd_create': '스레드',
                     'va_start': '가변 인자(va_list)', 'atexit': 'atexit'}


def unsupported(ast):
    """The first construct outside the supported C subset, as a reason, or None."""
    found = []

    class V(c_ast.NodeVisitor):
        def visit_Union(self, n): found.append('union')
        def visit_Goto(self, n): found.append('goto')
        def visit_Label(self, n): found.append('goto 라벨')
        def visit_Decl(self, n):
            if n.bitsize is not None: found.append('비트필드')
            self.generic_visit(n)
        def visit_ArrayDecl(self, n):
            if n.dim is not None and not isinstance(n.dim, c_ast.Constant) and not (
                    isinstance(n.dim, c_ast.ID) and n.dim.name.isupper()):
                found.append('가변 길이 배열(VLA)')
            self.generic_visit(n)
        def visit_FuncCall(self, n):
            name = n.name.name if isinstance(n.name, c_ast.ID) else None
            if name in UNSUPPORTED_CALLS: found.append(UNSUPPORTED_CALLS[name])
            self.generic_visit(n)
        def visit_Pragma(self, n): found.append('#pragma')
    V().visit(ast)
    return found[0] if found else None


class Instrumenter:
    def __init__(self, source):
        self.src = source
        self.lines = source.split('\n')
        code = blank_comments(source)
        # Constructs found by name before parsing: the parser may not know their types (va_list, jmp_buf)
        # or may read them as ordinary calls (__asm__("nop")).
        for pattern, reason in ((r'\b(va_start|va_arg|va_list)\b', '가변 인자(va_list)'), (r'\b(setjmp|longjmp|jmp_buf)\b', 'setjmp/longjmp'),
                                (r'\b(__asm__|__asm|asm)\b', '인라인 어셈블리'), (r'#\s*pragma\b', '#pragma')):
            if re.search(pattern, code):
                raise Unsupported(reason)
        blanked = code.split('\n')
        parse_text = PRELUDE + '# 1 "main.c"\n' + '\n'.join('' if l.lstrip().startswith('#') else l for l in blanked)
        self.code_lines = blanked     # comment-free text, same columns
        self.ast = c_parser.CParser().parse(parse_text, 'main.c')
        self.typedefs, self.structs = {}, {}   # name -> type node ; "struct X"/typedef name -> [(field, type)]
        self.vars, self.funcs, self.global_decls = [], [], []
        self.prefix = {}       # line -> text inserted at the first non-space column
        self.after_brace = {}  # line -> (column just after an opening brace, text)
        self.replace = {}      # line -> new full text
        self.skipped = []      # statements that got no line step (and why)

    # ---------- types ----------
    def type_info(self, t):
        if isinstance(t, c_ast.Decl):
            t = t.type
        if isinstance(t, c_ast.FuncDecl):
            return {'k': 'func', 'c': '함수'}
        if isinstance(t, c_ast.PtrDecl):
            return {'k': 'ptr', 'to': self.type_info(t.type)}
        if isinstance(t, c_ast.ArrayDecl):
            return {'k': 'array', 'of': self.type_info(t.type)}
        if isinstance(t, c_ast.TypeDecl):
            inner = t.type
            if isinstance(inner, c_ast.IdentifierType):
                name = ' '.join(inner.names)
                if name in BASE:
                    return {'k': 'int', 'size': BASE[name][0], 'signed': BASE[name][1], 'c': name}
                if name in FLOATS:
                    return {'k': 'float', 'size': FLOATS[name], 'c': name}
                if name in self.typedefs:
                    info = self.type_info(self.typedefs[name]); info.setdefault('alias', name); return info
                return {'k': 'opaque', 'c': name}
            if isinstance(inner, c_ast.Struct):
                key = f'struct {inner.name}' if inner.name else None
                if inner.decls is not None and key:
                    self.structs[key] = inner.decls
                return {'k': 'struct', 'name': key, 'c': key}
            if isinstance(inner, c_ast.Enum):
                return {'k': 'int', 'size': 4, 'signed': True, 'c': 'enum'}
        return {'k': 'opaque', 'c': type(t).__name__}

    def c_type(self, info):
        if info['k'] == 'ptr': return self.c_type(info['to']) + ' *'
        if info['k'] == 'array': return self.c_type(info['of']) + '[]'
        return info.get('alias') or info.get('c') or info['k']

    # ---------- insertion helpers ----------
    def line_start_ok(self, item):
        """True when `item` is the first thing on its source line, so text can go in front of the line."""
        line = self.code_lines[item.coord.line - 1]
        first = len(line) - len(line.lstrip())
        before = line[first:item.coord.column - 1]
        return not re.search(r'[;{}:]', before) and not line.lstrip().startswith(('}', 'case', 'default', 'else'))

    def add(self, line, text):
        self.prefix[line] = self.prefix.get(line, '') + text

    def register(self, decls, fid):
        out = ''
        for d in decls:
            if d.name and 'register' not in (d.storage or []) and 'extern' not in (d.storage or []) and not isinstance(d.type, c_ast.FuncDecl):
                vid = len(self.vars)
                self.vars.append({'id': vid, 'name': d.name, 'type': self.type_info(d), 'line': d.coord.line,
                                  'has_init': d.init is not None, 'fid': fid, 'static': 'static' in (d.storage or [])})
                out += f'__mq_var({vid}, &{d.name}, sizeof({d.name}), {FA}); '
        return out

    # ---------- walk ----------
    def run(self):
        reason = unsupported(self.ast)
        if reason:
            raise Unsupported(reason)
        for ext in self.ast.ext:
            if isinstance(ext, c_ast.Typedef):
                self.typedefs[ext.name] = ext.type
                if isinstance(ext.type, c_ast.TypeDecl) and isinstance(ext.type.type, c_ast.Struct) and ext.type.type.decls:
                    self.structs[ext.name] = ext.type.type.decls
                    if ext.type.type.name: self.structs[f'struct {ext.type.type.name}'] = ext.type.type.decls
            elif isinstance(ext, c_ast.Decl) and isinstance(ext.type, (c_ast.TypeDecl, c_ast.ArrayDecl, c_ast.PtrDecl)):
                self.type_info(ext)      # file-scope struct definitions
                if ext.name and 'extern' not in (ext.storage or []) and 'typedef' not in (ext.storage or []):
                    self.global_decls.append(ext)   # registered when main starts (their address never changes)
            elif isinstance(ext, c_ast.Decl) and isinstance(getattr(ext.type, 'type', None), c_ast.Struct):
                self.type_info(ext.type)
            elif isinstance(ext, c_ast.FuncDef):
                self.func(ext)
        return self

    def func(self, fd):
        fid = len(self.funcs)
        rtype = self.type_info(fd.decl.type.type)
        self.funcs.append({'id': fid, 'name': fd.decl.name, 'line': fd.decl.coord.line, 'ret': rtype})
        items = fd.body.block_items or []
        params = [p for p in (fd.decl.type.args.params if fd.decl.type.args else []) if isinstance(p, c_ast.Decl)]
        if not items:
            self.skipped.append((fd.decl.coord.line, 'empty function body')); return
        globals_ = ''
        if fd.decl.name == 'main' and self.global_decls:
            first = len(self.vars)
            globals_ = self.register(self.global_decls, fid)
            for v in self.vars[first:]: v['global'] = True; v['static'] = True
        head = f'__mq_enter({fid}, {fd.decl.coord.line}, {FA}); ' + globals_ + self.register(params, fid) + f'__mq_called({fd.decl.coord.line}); '
        self.block(items, fid, head, rtype, fd.body.coord)

    def block(self, items, fid, head, rtype, brace=None):
        pending = head
        prev = None
        for item in items:
            if isinstance(item, (c_ast.Case, c_ast.Default)):
                self.block(item.stmts or [], fid, '', rtype); pending = ''; continue
            if isinstance(item, c_ast.Label):
                item = item.stmt
            if isinstance(item, c_ast.Decl) and isinstance(prev, c_ast.Decl) and prev.coord.line == item.coord.line:
                # `int a = 1, b = 2;` is several Decl items of one declaration: one step, then both names.
                pending += self.register([item], fid); prev = item; self.stmt(item, fid, rtype); continue
            prev = item
            code = self.code_lines[item.coord.line - 1]
            if self.line_start_ok(item):
                self.add(item.coord.line, pending + f'__mq_line({item.coord.line}, {FA}); ')
            elif brace is not None and brace.line == item.coord.line and code[brace.column - 1] == '{'                     and not code[brace.column:item.coord.column - 1].strip(' 	').rstrip() and item.coord.line not in self.after_brace:
                # `int f(int x) { return x; }`: the step goes right after the opening brace.
                self.after_brace[item.coord.line] = (brace.column, pending + f'__mq_line({item.coord.line}, {FA}); ')
            else:
                self.skipped.append((item.coord.line, type(item).__name__ + ' not first on its line'))
            pending = ''
            if isinstance(item, c_ast.Decl):
                pending = self.register([item], fid)
            elif isinstance(item, c_ast.DeclList):
                pending = self.register(item.decls, fid)
            self.stmt(item, fid, rtype)

    def body(self, node, fid, rtype, extra=''):
        if node is None: return
        if isinstance(node, c_ast.Compound):
            self.block(node.block_items or [], fid, extra, rtype, node.coord)
            return
        # A brace-less body on its own line gets braces only when its line ends with ';'.
        code = self.code_lines[node.coord.line - 1].rstrip()
        if self.line_start_ok(node) and code.endswith(';') and not isinstance(node, (c_ast.If, c_ast.For, c_ast.While, c_ast.DoWhile, c_ast.Switch)):
            self.add(node.coord.line, '{ ' + extra + f'__mq_line({node.coord.line}, {FA}); ')
            self.suffix_brace(node.coord.line)
        else:
            self.skipped.append((node.coord.line, 'brace-less body not wrapped'))
        self.stmt(node, fid, rtype)

    def suffix_brace(self, line_no):
        line = self.replace.get(line_no, self.lines[line_no - 1])
        end = self.code_lines[line_no - 1].rstrip().rfind(';') + 1     # comments are blank in code_lines
        self.replace[line_no] = line[:end] + ' }' + line[end:]

    def stmt(self, s, fid, rtype):
        if isinstance(s, c_ast.If):
            self.body(s.iftrue, fid, rtype); self.body(s.iffalse, fid, rtype)
        elif isinstance(s, c_ast.For):
            init = self.register(s.init.decls, fid) if isinstance(s.init, c_ast.DeclList) else ''
            self.body(s.stmt, fid, rtype, init)
        elif isinstance(s, (c_ast.While, c_ast.DoWhile)):
            self.body(s.stmt, fid, rtype)
        elif isinstance(s, c_ast.Switch):
            self.body(s.stmt, fid, rtype)
        elif isinstance(s, c_ast.Compound):
            self.block(s.block_items or [], fid, '', rtype, s.coord)
        elif isinstance(s, c_ast.Return) and s.expr is not None and rtype['k'] == 'int':
            ln = s.coord.line
            line = self.replace.get(ln, self.lines[ln - 1])
            code = self.code_lines[ln - 1]
            m = re.search(r'\breturn\b([^;]*);', code)
            if m and len(re.findall(r'\breturn\b', code)) == 1 and code.count(';') == 1 and '"' not in m.group(1) and "'" not in m.group(1):
                ctype = rtype.get('alias') or rtype['c']
                # same columns in `line` (code_lines only blanks comments; earlier edits add text after the `;`)
                self.replace[ln] = line[:m.start()] + f'return ({ctype})__mq_ret({ln}, {FA}, (long long)({m.group(1).strip()}));' + line[m.end():]
            else:
                self.skipped.append((ln, 'return value not captured'))

    def output(self):
        out = []
        for i, line in enumerate(self.lines, 1):
            text = self.replace.get(i, line)
            if i in self.after_brace:
                col, extra = self.after_brace[i]
                text = text[:col] + ' ' + extra + text[col:]
            if i in self.prefix:
                first = len(text) - len(text.lstrip())
                text = text[:first] + self.prefix[i] + text[first:]
            out.append(text)
        layout = ['void __mq_layout(FILE *o) {']
        for key, decls in self.structs.items():
            for f in decls:
                layout.append(f'    fprintf(o, "L {key}|{f.name}|%d|%d\\n", (int)offsetof({key}, {f.name}), (int)sizeof((({key} *)0)->{f.name}));')
        layout.append('}')
        rt = open(os.path.join(HERE, 'mq_rt.c'), encoding='utf-8').read()
        return rt + '#include <stddef.h>\n' + '\n'.join(out) + '\n' + '\n'.join(layout) + '\n'


# ---------- decode ----------
def decode(ins, trace_text, stdout_bytes, source):
    layout = {}
    steps, cur = [], None
    for line in trace_text.split('\n'):
        p = line.split(' ')
        if p[0] == 'L':
            key, field, off, size = line[2:].split('|'); layout.setdefault(key, {})[field] = (int(off), int(size))
        elif p[0] == 'S':
            cur = {'event': p[1], 'line': int(p[2]), 'out': int(p[3]), 'ret': int(p[4]), 'frames': [], 'vars': [], 'blocks': [], 'freed': []}; steps.append(cur)
        elif p[0] == 'F':
            cur['frames'].append((int(p[1]), int(p[2], 16), int(p[3])))
        elif p[0] == 'V':
            cur['vars'].append((int(p[1], 16), int(p[2]), int(p[3], 16), int(p[4]), bytes.fromhex(p[5]) if len(p) > 5 else b''))
        elif p[0] == 'H':
            cur['blocks'].append((int(p[1], 16), int(p[2]), bytes.fromhex(p[4]) if len(p) > 4 else b''))   # p[3]: allocation serial
        elif p[0] == 'X':
            cur['freed'].append((int(p[1], 16), int(p[2])))         # a block the program already freed
        elif p[0] == 'LIMIT':
            steps.append({'limit': True})
    meta = {v['id']: v for v in ins.vars}

    def size_of(t):
        if t['k'] in ('int', 'float'): return t['size']
        if t['k'] == 'ptr': return 8
        if t['k'] == 'struct':
            fields = layout.get(t['name'], {})
            return max((o + s for o, s in fields.values()), default=0)
        return None

    out = []
    for st in steps:
        if st.get('limit'):
            last = dict(out[-1]); last['event'] = 'instruction_limit_reached'; out.append(last); continue
        cells = [(addr, size, meta[vid]['name'], meta[vid]['type'], fa) for fa, vid, addr, size, _ in st['vars']]
        blocks = {addr: (size, data) for addr, size, data in st['blocks']}
        heap, block_ids = {}, {}

        def where(p):
            for addr, size, name, t, fa in cells:
                if addr <= p < addr + max(size, 1):
                    if t['k'] == 'array' and size_of(t['of']):
                        return f'{name}[{(p - addr) // size_of(t["of"])}]'
                    if t['k'] == 'struct':
                        for f, (o, s) in layout.get(t['name'], {}).items():
                            if o <= p - addr < o + s: return f'{name}.{f}'
                    return name
            return None

        def value(t, data):
            if t['k'] == 'int':
                if len(data) < t['size']: return None
                v = int.from_bytes(data[:t['size']], 'little', signed=t['signed'])
                if t['size'] == 1 and t.get('c', '').endswith('char') and 32 <= (v & 0xff) < 127: return ['CHAR', chr(v & 0xff)]
                return v
            if t['k'] == 'float':
                v = struct.unpack('<f' if t['size'] == 4 else '<d', data[:t['size']])[0]
                return v if v == v and abs(v) != float('inf') else ['SPECIAL_FLOAT', repr(v)]
            if t['k'] == 'ptr' and t['to']['k'] == 'func':
                # the original program's function table (STABS starts), set by c_flow.py
                p = int.from_bytes(data[:8], 'little')
                if p == 0: return None
                name = getattr(ins, 'code_names', {}).get(p)
                return ['C_PTR', f'함수 {name}'] if name else ['C_NOTE', f'0x{p:x} · 함수 포인터(대상 이름 모름)']
            if t['k'] == 'ptr':
                p = int.from_bytes(data[:8], 'little')
                if p == 0: return None
                for addr, (size, bdata) in blocks.items():
                    if addr <= p < addr + max(size, 1):
                        return ['REF', heap_block(addr, size, bdata, t['to'])]
                target = where(p)
                if target:
                    return ['C_PTR', target]                         # a stack or global cell, by name
                if any(a <= p < a + max(s, 1) for a, s in st['freed']):
                    return ['C_NOTE', f'0x{p:x} · 해제된 동적 메모리 (따라가지 않음)']
                return ['C_NOTE', f'0x{p:x} · 어디인지 모름 (따라가지 않음)']
            if t['k'] == 'array':
                es = size_of(t['of'])
                if not es: return ['C_NOTE', '볼 수 없음: 원소 크기를 모름']
                hid = str(len(heap) + 1000)
                heap[hid] = None
                heap[hid] = ['ARRAY', f'{ins.c_type(t["of"])}[{len(data) // es}] (스택)'] + [value(t['of'], data[i * es:(i + 1) * es]) for i in range(len(data) // es)]
                return ['REF', int(hid)]
            if t['k'] == 'struct':
                hid = str(len(heap) + 1000)
                heap[hid] = None
                fields = []
                for d in ins.structs.get(t['name'], []):
                    o, s = layout.get(t['name'], {}).get(d.name, (None, None))
                    if o is not None: fields.append([d.name, value(ins.type_info(d), data[o:o + s])])
                heap[hid] = ['INSTANCE', f'{t["name"]} (스택)', *fields]
                return ['REF', int(hid)]
            return ['C_NOTE', f'볼 수 없음: {t.get("c", t["k"])} 형식은 아직 그리지 않아요']

        def heap_block(addr, size, data, to):
            if addr in block_ids: return block_ids[addr]
            hid = len(block_ids) + 1; block_ids[addr] = hid
            heap[str(hid)] = None
            es = size_of(to) or 1
            n = size // es
            if to['k'] == 'struct' and n == 1:
                inner = value(to, data)          # a stack-style box; re-label it as the malloc block
                heap[str(hid)] = heap.pop(str(inner[1])); heap[str(hid)][1] = f'{to["name"]} (동적 할당 {size}B)'
            else:
                heap[str(hid)] = ['ARRAY', f'{ins.c_type(to)}[{n}] (동적 할당 {size}B)'] + [value(to, data[i * es:(i + 1) * es]) for i in range(n)]
            return hid

        frames, gvals, gnames = [], {}, []
        for vfa, vid, addr, size, data in st['vars']:
            if meta[vid].get('global'):
                gnames.append(meta[vid]['name']); gvals[meta[vid]['name']] = value(meta[vid]['type'], data)
        for fid, fa, line in st['frames']:
            names, vals, uninit, statics = [], {}, [], []
            for vfa, vid, addr, size, data in st['vars']:
                if vfa != fa or meta[vid].get('global'): continue
                m = meta[vid]
                names.append(m['name']); vals[m['name']] = value(m['type'], data)
                if m['static']: statics.append(m['name'])
                if not m['has_init'] and not m['static'] and m['fid'] == fid and m['line'] > ins.funcs[fid]['line']:
                    uninit.append(m['name'])
            frames.append({'func_name': ins.funcs[fid]['name'], 'frame_id': fa, 'line': line, 'is_highlighted': False,
                           'encoded_locals': vals, 'ordered_varnames': names, 'declared_without_initializer': uninit,
                           'static_names': statics})
        if frames:
            frames[-1]['is_highlighted'] = True
            rtype = ins.funcs[st['frames'][-1][0]]['ret'] if st['frames'] else {'k': 'void'}
            if st['event'] == 'return' and rtype['k'] == 'int':
                # rax at the function's `leave`: the value the function returns, cut to its return type
                v = st['ret'] & ((1 << (8 * rtype['size'])) - 1)
                if rtype['signed'] and v >= 1 << (8 * rtype['size'] - 1): v -= 1 << (8 * rtype['size'])
                frames[-1]['ordered_varnames'].append('__return__'); frames[-1]['encoded_locals']['__return__'] = v
        so = stdout_bytes[:st['out']].decode('utf-8', 'replace').replace('\r\n', '\n') if st['out'] >= 0 else ''
        out.append({'event': st['event'], 'line': st['line'], 'func_name': frames[-1]['func_name'] if frames else '',
                    'stdout': so, 'globals': gvals, 'ordered_globals': gnames, 'stack_to_render': frames, 'heap': heap})
    return out


def main():
    src_path, stdin_path, out_dir = sys.argv[1:4]
    os.makedirs(out_dir, exist_ok=True)
    source = open(src_path, encoding='utf-8').read()
    stdin = open(stdin_path, 'rb').read()
    t0 = time.perf_counter()
    ins = Instrumenter(source).run()
    open(os.path.join(out_dir, 'main.c'), 'w', encoding='utf-8', newline='').write(source)
    open(os.path.join(out_dir, 'main_mq.c'), 'w', encoding='utf-8', newline='').write(ins.output())
    t1 = time.perf_counter()
    graded = subprocess.run([TCC, '-run', 'main.c'], cwd=out_dir, input=stdin, capture_output=True, timeout=15)
    open(os.path.join(out_dir, 'grader_stdout.txt'), 'wb').write(graded.stdout)
    t2 = time.perf_counter()
    with open(os.path.join(out_dir, 'stdout.txt'), 'wb') as so, open(stdin_path, 'rb') as si:
        traced = subprocess.run([TCC, '-run', 'main_mq.c'], cwd=out_dir, stdin=si, stdout=so, stderr=subprocess.PIPE, timeout=20)
    t3 = time.perf_counter()
    stdout_bytes = open(os.path.join(out_dir, 'stdout.txt'), 'rb').read()
    trace_text = open(os.path.join(out_dir, 'mq_trace.txt'), encoding='utf-8').read() if os.path.exists(os.path.join(out_dir, 'mq_trace.txt')) else ''
    steps = decode(ins, trace_text, stdout_bytes, source)
    # Small stable frame ids: one per (function, frame address) run between a call and the frame leaving.
    next_id, live = 1, {}
    for st in steps:
        frames = st['stack_to_render']
        for i, f in enumerate(frames):
            key = (f['func_name'], f['frame_id'])
            if key not in live or (st['event'] == 'call' and i == len(frames) - 1 and not st.get('_seen')):
                live[key] = next_id; next_id += 1
            f['frame_id'] = live[key]
        st['_seen'] = True
    for st in steps: st.pop('_seen', None)
    status = 'ok' if traced.returncode == 0 else 'uncaught_exception'
    if steps and steps[-1]['event'] == 'instruction_limit_reached': status = 'step_limit'
    if traced.returncode != 0 and steps:
        last = dict(steps[-1]); last['event'] = 'uncaught_exception'; last['exception_msg'] = f'프로그램이 종료 코드 {traced.returncode & 0xffffffff:#x}로 끝났어요'
        steps.append(last)
    norm = lambda b: b.decode('utf-8', 'replace').replace('\r\n', '\n')
    doc = {'code': source, 'stdin': stdin.decode('utf-8', 'replace'), 'problems': [], 'status': status, 'language': 'c',
           'compiler': 'TinyCC 0.9.27 tcc -run (grader compiler and mode) on an instrumented copy', 'stepBudget': 1000,
           'options': {'objects': False}, 'heapTruncated': False, 'stdout': norm(stdout_bytes), 'trace': steps,
           'instrumentation': {'skipped': ins.skipped, 'variables': len(ins.vars), 'functions': len(ins.funcs)},
           'grader': {'exit': graded.returncode, 'stdout': norm(graded.stdout)}, 'traced_exit': traced.returncode,
           'traced_stderr': traced.stderr.decode('utf-8', 'replace')[-400:],
           'timing': {'instrument_s': round(t1 - t0, 3), 'grader_s': round(t2 - t1, 3), 'traced_run_s': round(t3 - t2, 3)}}
    json.dump(doc, open(os.path.join(out_dir, 'trace.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    same = norm(stdout_bytes) == norm(graded.stdout) and (traced.returncode == 0) == (graded.returncode == 0)
    print(f'{os.path.basename(out_dir)}: status={status} steps={len(steps)} same_stdout_and_exit_as_grader={same} '
          f'skipped={len(ins.skipped)} timing={doc["timing"]}')


if __name__ == '__main__':
    main()
