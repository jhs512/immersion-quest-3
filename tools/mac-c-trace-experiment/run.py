import json
from pathlib import Path
import shlex
import subprocess
import sys


HERE = Path(__file__).resolve().parent
case = Path(sys.argv[1]).resolve()
case.mkdir(parents=True, exist_ok=True)
source = '''#include <stdio.h>
#include <stdlib.h>
int twice(int value) {
    return value * 2;
}
int main(void) {
    long wide = 4294967297L;
    int stock = 2;
    int *alias = &stock;
    int values[3] = {1, 2, 3};
    int *box = malloc(sizeof *box);
    stock = twice(*alias);
    *box = stock + values[1];
    printf("%ld %d %d\\n", wide, stock, *box);
    free(box);
    return 0;
}
'''
(case / 'main.c').write_text(source, encoding='utf-8')
(case / 'stdin.txt').write_text('', encoding='utf-8')
for name, flags in [('grader-main', []), ('trace-main', ['-g', '-O0'])]:
    subprocess.run(['cc', '-std=c11', *flags, '-o', str(case / name), str(case / 'main.c')], check=True)
graded = subprocess.run([str(case / 'grader-main')], capture_output=True, check=True, timeout=10).stdout
command = ['xcrun', 'lldb', '-b', '-Q',
           '-o', 'command script import ' + shlex.quote(str(HERE / 'probe.py')),
           '-o', 'mq-probe ' + shlex.quote(str(case))]
run = subprocess.run(command, capture_output=True, text=True, timeout=90)
(case / 'lldb.log').write_text(run.stdout + '\n' + run.stderr, encoding='utf-8')
assert run.returncode == 0, run.stdout + run.stderr
if not (case / 'probe.json').is_file():
    raise RuntimeError(run.stdout + '\n' + run.stderr)
doc = json.loads((case / 'probe.json').read_text(encoding='utf-8'))
assert doc['exit'] == 0, doc
assert (case / 'trace-stdout.txt').read_bytes() == graded == b'4294967297 4 6\n'
values = [value for stop in doc['stops'] for frame in stop for value in frame['values']]
assert any(v['name'] == 'wide' and v['size'] == 8 and v['value'] == '4294967297' for v in values), values
assert any(v['name'] == 'stock' and v['value'] == '4' for v in values), values
assert any(v['name'] == 'values' and [c['value'] for c in v['children']] == ['1', '2', '3'] for v in values), values
assert any(frame['function'] == 'twice' for stop in doc['stops'] for frame in stop), doc
print(json.dumps({'target': doc['target'], 'stops': len(doc['stops']), 'stdout': graded.decode(),
                  'long_bytes': 8, 'scalar_array_call_stack': 'passed'}, ensure_ascii=False))

(case / 'src.c').write_text(source, encoding='utf-8')
subprocess.run([sys.executable, str(HERE.parent.parent / 'assets/c-trace/mac_c_flow.py'), str(case)], check=True, timeout=110)
flow = json.loads((case / 'c_flow.json').read_text(encoding='utf-8'))
assert flow['status'] == 'ok', flow
assert flow['verification']['original_source'] and flow['verification']['program_runs'] == 1, flow
assert flow['stdout'].encode() == graded, flow
frames = [frame for step in flow['trace'] for frame in step['stack_to_render']]
assert any(frame['encoded_locals'].get('stock') == 4 for frame in frames), flow
assert any(frame['encoded_locals'].get('alias') == ['C_PTR', 'stock'] for frame in frames), flow
assert any(any(isinstance(v, list) and v[0] == 'REF' for name, v in frame['encoded_locals'].items() if name == 'box') for frame in frames), flow
assert any(any(isinstance(v, list) and v[0] == 'C_NOTE' and '해제된' in v[1] for name, v in frame['encoded_locals'].items() if name == 'box') for frame in frames), flow
assert any(any(isinstance(obj, list) and obj[0] == 'INSTANCE' and ['[0]', 6] in obj for obj in step['heap'].values()) for step in flow['trace']), flow
print(json.dumps({'native_flow_steps': len(flow['trace']), 'aliases_heap_free': 'passed'}, ensure_ascii=False))

offset_case = case / 'offset'
offset_case.mkdir(exist_ok=True)
(offset_case / 'src.c').write_text('''#include <stdlib.h>
struct Box { int count; };
int main(void) {
    struct Box item = {7};
    int *field = &item.count;
    int *base = malloc(3 * sizeof *base);
    base[0] = 10;
    base[1] = 20;
    base[2] = 30;
    int *next = base + 1;
    *field += 1;
    free(base);
    return 0;
}
''', encoding='utf-8')
(offset_case / 'stdin.txt').write_text('', encoding='utf-8')
subprocess.run([sys.executable, str(HERE.parent.parent / 'assets/c-trace/mac_c_flow.py'), str(offset_case)], check=True, timeout=110)
offset_doc = json.loads((offset_case / 'c_flow.json').read_text(encoding='utf-8'))
assert offset_doc['status'] == 'ok', offset_doc
observed = False
for step in offset_doc['trace']:
    for frame in step['stack_to_render']:
        local = frame['encoded_locals']
        base, nxt = local.get('base'), local.get('next')
        if isinstance(base, list) and base[0] == 'REF' and isinstance(nxt, list) and nxt[0] == 'REF':
            assert base != nxt, step
            assert ['[0]', 10] in step['heap'][str(base[1])], step
            assert ['[0]', 20] in step['heap'][str(nxt[1])], step
            assert local['field'] == ['C_PTR', 'item.count'], step
            observed = True
assert observed, offset_doc
print('allocation offset views and struct field pointers passed')
