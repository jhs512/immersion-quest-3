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
