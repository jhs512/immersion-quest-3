"""Measure 코드 흐름 보기 on data lessons at several data sizes (course audit experiment).

For each workload and row count it runs the grader's runner (assets/python/rich_runner.py) plainly and under
the app's tracer (assets/python-trace/mq_pytrace.py, same arguments as src/python_trace.rs), in a fresh temp
workspace, and records wall time, peak working set, trace size, step count, status, what the viewer can show
of the data object (elements vs an OPAQUE type name) and how many line events the step budget dropped.
With --ui it also renders the heaviest step with the app's TraceView (assets/java-trace/core/render.js) in
headless Chrome/Edge and records the render time and DOM node count.

  python tools/course_audit/trace_scale.py --python <course python> [--ui] [--out <json>]

Peak memory uses GetProcessMemoryInfo, so it runs on Windows only. The app kills a trace after 20 s; this
harness waits up to --timeout seconds so the cost past that limit is measured, and marks app_timeout.
"""
import argparse
import ctypes
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from ctypes import wintypes
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / 'assets/python/rich_runner.py'
TRACER = ROOT / 'assets/python-trace/mq_pytrace.py'
APP_SECONDS = 20
STEP_BUDGET = 1000


def csv_rows(n):
    lines = ['id,group,price,quantity,target']
    for i in range(n):
        lines.append(f'{i},{"ABCD"[i % 4]},{(i * 370) % 1000 / 10},{i % 7},{int((i * 370) % 1000 > 500)}')
    return '\n'.join(lines) + '\n'


# Each workload mirrors a step shape found in the lessons (see the audit report for the matching steps).
WORKLOADS = {
    'python_list_loop': ('values = list(range({n}))\ntotal = 0\nfor value in values[:5]:\n    total = total + value\nprint(len(values), total)\n', False),
    'pandas_groupby': ("import pandas as pd\ndf = pd.read_csv('data.csv')\nsummary = df.groupby('group')['price'].mean()\nprint(len(df))\nprint(summary.round(2))\n", True),
    'pandas_iterrows': ("import pandas as pd\ndf = pd.read_csv('data.csv')\ncount = 0\nfor _, row in df.iterrows():\n    if row['price'] > 50:\n        count = count + 1\nprint(count)\n", True),
    'numpy_vector': ('import numpy as np\nvalues = np.arange({n})\ndoubled = values * 2\nprint(doubled.sum())\n', False),
    'sklearn_fit': ("import pandas as pd\nfrom sklearn.model_selection import train_test_split\nfrom sklearn.linear_model import LogisticRegression\n"
                    "df = pd.read_csv('data.csv')\nX = df[['price', 'quantity']]\ny = df['target']\n"
                    "X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)\n"
                    "model = LogisticRegression(max_iter=200)\nmodel.fit(X_train, y_train)\nprint(round(model.score(X_test, y_test), 3))\n", True),
}


class Counters(ctypes.Structure):
    _fields_ = [('cb', wintypes.DWORD), ('PageFaultCount', wintypes.DWORD), ('PeakWorkingSetSize', ctypes.c_size_t),
                ('WorkingSetSize', ctypes.c_size_t), ('QuotaPeakPagedPoolUsage', ctypes.c_size_t),
                ('QuotaPagedPoolUsage', ctypes.c_size_t), ('QuotaPeakNonPagedPoolUsage', ctypes.c_size_t),
                ('QuotaNonPagedPoolUsage', ctypes.c_size_t), ('PagefileUsage', ctypes.c_size_t),
                ('PeakPagefileUsage', ctypes.c_size_t)]


def run(args, cwd, timeout):
    started = time.perf_counter()
    process = subprocess.Popen(args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               env={**os.environ, 'TF_CPP_MIN_LOG_LEVEL': '3', 'PYTHONIOENCODING': 'utf-8'})
    try:
        out, err = process.communicate(timeout=timeout)
        state = 'exit' if process.returncode == 0 else f'exit {process.returncode}'
    except subprocess.TimeoutExpired:
        process.kill()
        out, err = process.communicate()
        state = 'timeout'
    seconds = time.perf_counter() - started
    counters = Counters()
    counters.cb = ctypes.sizeof(counters)
    ctypes.windll.psapi.GetProcessMemoryInfo(int(process._handle), ctypes.byref(counters), counters.cb)
    return {'state': state, 'seconds': round(seconds, 3), 'peak_mb': round(counters.PeakWorkingSetSize / 1e6, 1),
            'stderr_tail': err.decode('utf-8', 'replace').strip()[-300:]}


def line_events(python, workspace, timeout):
    """Total main.py line events without the step budget: what a complete trace would have to record."""
    probe = workspace / 'count_lines.py'
    probe.write_text(
        'import runpy, sys\ncount = [0]\n'
        'def local(frame, event, arg):\n    if event == "line": count[0] += 1\n    return local\n'
        'def glob(frame, event, arg):\n    return local if frame.f_code.co_filename == "main.py" else None\n'
        'sys.settrace(glob)\ntry:\n    runpy.run_path("rich_runner.py", run_name="__main__")\nexcept SystemExit:\n    pass\n'
        'sys.settrace(None)\nopen("line_count.txt", "w").write(str(count[0]))\n', encoding='utf-8')
    result = run([python, '-I', '-X', 'utf8', '-u', 'count_lines.py'], workspace, timeout)
    count = workspace / 'line_count.txt'
    return int(count.read_text()) if count.exists() else None, result['state']


def shown_data(doc):
    """What the viewer can show of the data: the largest collection's element count, or OPAQUE type names."""
    largest, opaque = 0, set()
    for step in doc.get('trace', []):
        for obj in (step.get('heap') or {}).values():
            if obj and obj[0] == 'COLLECTION':
                largest = max(largest, len(obj[2]))
            elif obj and obj[0] == 'OPAQUE':
                opaque.add(obj[1])
    return largest, sorted(opaque)


def heaviest_step(doc):
    trace = doc.get('trace', [])
    if not trace:
        return None
    return max(range(len(trace)), key=lambda i: len(json.dumps(trace[i].get('heap', {}))))


def measure(python, workload, n, timeout):
    template, uses_csv = WORKLOADS[workload]
    workspace = Path(tempfile.mkdtemp(prefix='mq-trace-scale-'))
    try:
        (workspace / 'main.py').write_text(template.format(n=n), encoding='utf-8')
        if uses_csv:
            (workspace / 'data.csv').write_text(csv_rows(n), encoding='utf-8')
        shutil.copy(RUNNER, workspace / 'rich_runner.py')
        shutil.copy(TRACER, workspace / 'mq_pytrace.py')
        (workspace / 'stdin.txt').write_text('', encoding='utf-8')
        plain = run([python, '-I', '-X', 'utf8', '-u', 'rich_runner.py'], workspace, timeout)
        traced = run([python, '-I', '-X', 'utf8', '-u', 'mq_pytrace.py', 'rich_runner.py', 'stdin.txt', 'trace.json',
                      str(STEP_BUDGET)], workspace, timeout)
        row = {'workload': workload, 'rows': n, 'plain': plain, 'traced': traced,
               'app_timeout': traced['state'] == 'timeout' or traced['seconds'] > APP_SECONDS}
        trace_path = workspace / 'trace.json'
        if trace_path.exists():
            raw = trace_path.read_bytes()
            doc = json.loads(raw)
            largest, opaque = shown_data(doc)
            total, count_state = line_events(python, workspace, timeout)
            recorded = sum(step.get('event') == 'step_line' for step in doc.get('trace', []))
            row.update({'trace_mb': round(len(raw) / 1e6, 3), 'status': doc.get('status'), 'steps': len(doc.get('trace', [])),
                        'heap_truncated': doc.get('heapTruncated'), 'largest_collection_shown': largest, 'opaque': opaque,
                        'line_events_total': total, 'line_events_recorded': recorded,
                        'line_events_dropped': (total - recorded) if total is not None else None,
                        'line_count_state': count_state, 'stdout_tail': (doc.get('stdout') or '').strip()[-120:]})
            index = heaviest_step(doc)
            if index is not None:
                row['_ui_doc'] = {**doc, 'trace': [doc['trace'][index]]}
                row['ui_step'] = index
        else:
            row.update({'trace_mb': None, 'status': 'no trace written'})
        return row
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def browser():
    for path in (r'C:\Program Files\Google\Chrome\Application\chrome.exe', r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'):
        if Path(path).exists():
            return path
    return None


def strip_module(text):
    return '\n'.join(line.replace('export ', '', 1) if line.startswith('export ') else line
                     for line in text.splitlines() if not line.startswith('import '))


def render_ui(doc, timeout):
    """Render one step with TraceView in headless Chrome; the page writes its measurement into the DOM."""
    exe = browser()
    if exe is None:
        return {'ui': 'no browser'}
    core = ROOT / 'assets/java-trace/core'
    script = ('const { highlightLines } = (() => {\n' + strip_module((core / 'highlight.js').read_text(encoding='utf-8'))
              + '\nreturn { highlightLines };\n})();\nconst { TraceView } = (() => {\n'
              + strip_module((core / 'render.js').read_text(encoding='utf-8')) + '\nreturn { TraceView };\n})();\n')
    css = (ROOT / 'assets/java-trace/code-flow.css').read_text(encoding='utf-8')
    payload = json.dumps(doc, ensure_ascii=False).replace('</', '<\\/')
    page = (f'<!doctype html><meta charset="utf-8"><style>{css}</style><div id="root" style="width:1200px;height:800px"></div>'
            f'<pre id="result"></pre><script>{script}\n'
            f'try {{ const t0 = performance.now(); const doc = JSON.parse(document.getElementById("doc").textContent);'
            f'const t1 = performance.now(); const view = new TraceView(document.getElementById("root"), doc);'
            f'view.goTo(0); document.body.offsetHeight; const t2 = performance.now();'
            f'document.getElementById("result").textContent = JSON.stringify({{parse_ms: t1 - t0, render_ms: t2 - t1,'
            f' nodes: document.getElementById("root").getElementsByTagName("*").length}});'
            f' }} catch (e) {{ document.getElementById("result").textContent = JSON.stringify({{error: String(e)}}); }}</script>')
    page = page.replace('<script>', f'<script type="application/json" id="doc">{payload}</script><script>', 1)
    folder = Path(tempfile.mkdtemp(prefix='mq-trace-ui-'))
    try:
        html = folder / 'page.html'
        html.write_text(page, encoding='utf-8')
        try:
            done = subprocess.run([exe, '--headless=new', '--disable-gpu', f'--user-data-dir={folder / "profile"}',
                                   '--virtual-time-budget=60000', '--dump-dom', html.as_uri()],
                                  capture_output=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return {'ui': 'browser timeout'}
        dom = done.stdout.decode('utf-8', 'replace')
        start = dom.find('<pre id="result">')
        text = dom[start + len('<pre id="result">'):dom.find('</pre>', start)] if start >= 0 else ''
        try:
            return {'ui': 'ok', **{k: round(v, 1) if isinstance(v, float) else v for k, v in json.loads(text).items()},
                    'page_mb': round(html.stat().st_size / 1e6, 2)}
        except ValueError:
            return {'ui': 'no result', 'page_mb': round(html.stat().st_size / 1e6, 2)}
    finally:
        shutil.rmtree(folder, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--python', required=True)
    parser.add_argument('--sizes', default='10,1000,100000,1000000')
    parser.add_argument('--workloads', default=','.join(WORKLOADS))
    parser.add_argument('--timeout', type=int, default=180)
    parser.add_argument('--ui', action='store_true')
    parser.add_argument('--out', default=str(ROOT / '.scratch/course-visualizer-audit/trace-scale.json'))
    args = parser.parse_args()
    version = subprocess.run([args.python, '-c', 'import sys, pandas, numpy, sklearn; print(sys.version.split()[0], pandas.__version__, numpy.__version__, sklearn.__version__)'],
                             capture_output=True, text=True).stdout.strip()
    rows = []
    for workload in args.workloads.split(','):
        for n in map(int, args.sizes.split(',')):
            row = measure(args.python, workload, n, args.timeout)
            doc = row.pop('_ui_doc', None)
            if args.ui and doc is not None:
                row['render'] = render_ui(doc, args.timeout)
            rows.append(row)
            print(json.dumps({k: v for k, v in row.items() if k not in ('stdout_tail',)}, ensure_ascii=False), flush=True)
    Path(args.out).write_text(json.dumps({'python': args.python, 'versions': version, 'app_seconds': APP_SECONDS,
                                          'step_budget': STEP_BUDGET, 'rows': rows}, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
