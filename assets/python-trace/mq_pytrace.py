"""Experimental Python tracer for MQ's 코드 흐름 보기 (NOT integrated into the app).

Runs the grader's own runner (assets/python/rich_runner.py, which execs `main.py`) under
sys.settrace and records every event of frames whose code comes from `main.py`. Each step is a
full snapshot in the java-memory-visualizer trace format (Python Tutor OPT style: trace[],
stack_to_render, encoded_locals, heap, ["REF", id]) so the vendored TraceView can replay it.

usage (cwd = a directory holding main.py and rich_runner.py, exactly like the grader):
    python -I -X utf8 -u mq_pytrace.py rich_runner.py stdin.txt trace.json [stepBudget]
"""
import builtins
import io
import json
import math
import os
import runpy
import sys
import time
import types

USER_FILE = 'main.py'          # rich_runner compiles the learner's code under this name
MAX_OBJECTS = 300
RAW_EVENT_CAP = 2_000_000      # same back-edge style cap as the Java core


class StopTrace(BaseException):
    pass


class Tee(io.TextIOBase):
    """Stands in for sys.stdout / sys.stderr: keeps per-stream text and the combined console."""
    def __init__(self, own, combined, encoding='utf-8'):
        self.own, self.combined, self._encoding = own, combined, encoding
    @property
    def encoding(self):
        return self._encoding
    def writable(self):
        return True
    def write(self, text):
        self.own.append(text)
        self.combined.append(text)
        return len(text)
    def flush(self):
        pass


def main():
    runner, stdin_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    budget = int(sys.argv[4]) if len(sys.argv) > 4 else 1000
    source = open(USER_FILE, encoding='utf-8').read()
    doc = {'code': source, 'stdin': open(stdin_path, encoding='utf-8').read(), 'problems': [],
           'status': 'ok', 'language': 'python', 'runtime': sys.version.split()[0],
           'stepBudget': budget, 'options': {'objects': False}, 'heapTruncated': False, 'trace': []}
    try:
        compile(source, USER_FILE, 'exec')
    except SyntaxError as e:
        doc['status'] = 'compile_error'
        doc['problems'].append({'line': e.lineno or 0, 'error': True, 'message': f'{type(e).__name__}: {e.msg}'})
        json.dump(doc, open(out_path, 'w', encoding='utf-8'), ensure_ascii=False)
        return

    out, err, console = [], [], []
    real = (sys.stdin, sys.stdout, sys.stderr)
    sys.stdin = open(stdin_path, encoding='utf-8')
    sys.stdout, sys.stderr = Tee(out, console), Tee(err, console)

    trace = doc['trace']
    frame_ids = {}       # id(frame) -> (frame_id, frame)  (frame kept alive while it is on the stack)
    next_frame = [1]
    obj_ids = {}         # id(obj) -> (heap id, obj)  objects are retained so ids are never reused
    raw = [0]
    state = {'module_exception': None, 'last_line': 0}

    def heap_id(obj):
        key = id(obj)
        if key not in obj_ids:
            obj_ids[key] = (len(obj_ids) + 1, obj)
        return obj_ids[key][0]

    def is_user_function(v):
        return isinstance(v, types.FunctionType) and v.__code__.co_filename == USER_FILE

    def snapshot(event, frame, arg=None):
        heap = {}

        def enc(v):
            if v is None or isinstance(v, bool):
                return v
            if isinstance(v, int):
                return v if abs(v) <= 2**53 else ['SPECIAL_FLOAT', str(v)]
            if isinstance(v, float):
                return v if math.isfinite(v) else ['SPECIAL_FLOAT', repr(v)]
            if isinstance(v, str):
                return v
            ref = heap_id(v)
            if str(ref) in heap:
                return ['REF', ref]
            if len(heap) >= MAX_OBJECTS:
                doc['heapTruncated'] = True
                return ['REF', ref]
            heap[str(ref)] = None          # reserve before recursing (cycles)
            heap[str(ref)] = obj(v)
            return ['REF', ref]

        def obj(v):
            if isinstance(v, (list, tuple)):
                return ['COLLECTION', type(v).__name__, [enc(x) for x in v]]
            if isinstance(v, (set, frozenset)):
                return ['COLLECTION', type(v).__name__, [enc(x) for x in v]]
            if isinstance(v, dict):
                return ['MAP', type(v).__name__, [[enc(k), enc(x)] for k, x in v.items()]]
            if isinstance(v, type):
                fields = [[k, enc(x)] for k, x in vars(v).items()
                          if not k.startswith('__') and not callable(x)]
                return ['INSTANCE', f'class {v.__name__}', *fields]
            if isinstance(v, types.FunctionType):
                return ['OPAQUE', f'function {v.__name__}']
            if isinstance(v, types.ModuleType):
                return ['OPAQUE', f'module {v.__name__}']
            if getattr(type(v), '__module__', None) == '__main__' and hasattr(v, '__dict__'):
                return ['INSTANCE', type(v).__name__, *[[k, enc(x)] for k, x in vars(v).items()]]
            return ['OPAQUE', type(v).__name__]

        chain = []
        f = frame
        while f is not None:
            if f.f_code.co_filename == USER_FILE:
                chain.append(f)
            f = f.f_back
        chain.reverse()
        stack = []
        for f in chain:
            fid = frame_ids.setdefault(id(f), (next_frame[0], f))[0]
            if fid == next_frame[0]:
                next_frame[0] += 1
            is_module = f.f_code.co_name == '<module>'
            names, values = [], {}
            for k, v in list(f.f_locals.items()):
                if is_module and (k.startswith('__') or k in ('print', 'display')
                                  or (isinstance(v, types.FunctionType) and not is_user_function(v))):
                    continue      # names the grader's runner injected, not the learner's
                names.append(k)
                values[k] = enc(v)
            if f is frame and event == 'return' and not is_module:
                names.append('__return__')
                values['__return__'] = enc(arg)
            stack.append({'func_name': f.f_code.co_name, 'frame_id': fid, 'line': f.f_lineno,
                          'is_highlighted': f is frame, 'encoded_locals': values, 'ordered_varnames': names})
        step = {'event': event, 'line': frame.f_lineno, 'func_name': frame.f_code.co_name,
                'stdout': ''.join(console), 'globals': {}, 'ordered_globals': [],
                'stack_to_render': stack, 'heap': heap}
        return step

    def record(event, frame, arg=None):
        if len(trace) >= budget:
            last = dict(trace[-1])
            last['event'] = 'instruction_limit_reached'
            trace.append(last)
            doc['status'] = 'step_limit'
            raise StopTrace
        step = snapshot(event, frame, arg)
        if event in ('exception',):
            exc_type, exc, _ = arg
            step['exception_msg'] = f'{exc_type.__name__}: {exc}'
        trace.append(step)
        state['last_line'] = frame.f_lineno

    def local(frame, event, arg):
        raw[0] += 1
        if raw[0] > RAW_EVENT_CAP:
            doc['status'] = 'step_limit'
            raise StopTrace
        if event == 'line':
            prev = trace[-1] if trace else None
            # Like the Java core (JDI line step): returning to the same line in the same frame is one step.
            if prev and prev['event'] == 'step_line' and prev['line'] == frame.f_lineno and \
                    prev['stack_to_render'] and prev['stack_to_render'][-1]['frame_id'] == frame_ids.get(id(frame), (None,))[0]:
                return local
            record('step_line', frame)
        elif event == 'return':
            # After an 'exception' that leaves this frame, CPython still sends 'return' with None while
            # unwinding. Like the Java core, the frame just leaves: no 'return' step, no __return__.
            prev = trace[-1] if trace else None
            unwinding = prev and prev['event'] == 'exception' and prev['stack_to_render'] and                 prev['stack_to_render'][-1]['frame_id'] == frame_ids.get(id(frame), (None,))[0]
            if not unwinding:
                record('return', frame, arg)
            frame_ids.pop(id(frame), None)
        elif event == 'exception':
            record('exception', frame, arg)
            if frame.f_code.co_name == '<module>':
                state['module_exception'] = arg
        return local

    def glob(frame, event, arg):
        if frame.f_code.co_filename != USER_FILE:
            return None
        if event == 'call' and frame.f_code.co_name != '<module>':
            record('call', frame)
        return local

    started = time.perf_counter_ns()
    exit_code = 0
    sys.settrace(glob)
    try:
        runpy.run_path(runner, run_name='__main__')
    except StopTrace:
        pass
    except SystemExit as e:
        exit_code = 0 if e.code is None else e.code
    finally:
        sys.settrace(None)
        sys.stdin.close()
        sys.stdin, sys.stdout, sys.stderr = real
    if state['module_exception'] is not None and exit_code and trace:
        exc_type, exc, _ = state['module_exception']
        last = dict(trace[-1])
        last.update(event='uncaught_exception', exception_msg=f'{exc_type.__name__}: {exc}',
                    stdout=''.join(console))
        trace.append(last)
        doc['status'] = 'uncaught_exception'
    doc['stdout'] = ''.join(out)
    doc['stderr'] = ''.join(err)
    doc['exitCode'] = exit_code
    doc['retainedObjects'] = len(obj_ids)
    doc['timing'] = {'runNs': time.perf_counter_ns() - started}
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(doc, f, ensure_ascii=False)


if __name__ == '__main__':
    main()
