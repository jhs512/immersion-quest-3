"""Show what 코드 흐름 보기 records at a narration point of a Python step, to author a code_flow action.

Replays the step's narration (patch_code / set_code / try-undo as written in content.json) up to the spoken
sentence `after`, traces that code with the app's tracer (assets/python-trace/mq_pytrace.py, the same runner
and arguments as src/python_trace.rs) and prints every recorded step on lines containing `needle`, with the
event, its index among same-line steps (nth) and the locals. Authoring aid only: the lesson validator replays
the final action on the real trace.

  python tools/course_audit/flow_probe.py <lesson-key> <step-number> "<after sentence>" "<line needle>"
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import narration_review  # noqa: E402

PYTHON = os.environ.get('MOLIP_PYTHON') or str(Path(os.environ['LOCALAPPDATA']) / 'MolipQuest/MolipQuest/data/ml-env/python.exe')


def source_at(task, after):
    source = task.get('example_code') or task['starter_code']
    for action in task['narration']:
        if action['action'] == 'patch_code':
            source = source.replace(action['before'], action['after'], 1)
        elif action['action'] == 'set_code':
            source = action['code']
        if narration_review.spoken(action) == after:
            return source
    raise SystemExit(f'sentence not found: {after}')


def main():
    key, number, after, needle = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
    _, _, authored, _ = narration_review.load(key)
    task = authored['tasks'][number - 1]
    source = source_at(task, after)
    work = Path(tempfile.mkdtemp(prefix='mq-flow-probe-'))
    try:
        (work / 'main.py').write_text(source, encoding='utf-8')
        for name, text in (task.get('files') or {}).items():
            (work / name).write_text(text, encoding='utf-8')
        shutil.copy(ROOT / 'assets/python/rich_runner.py', work / 'rich_runner.py')
        shutil.copy(ROOT / 'assets/python-trace/mq_pytrace.py', work / 'mq_pytrace.py')
        (work / 'stdin.txt').write_text((task.get('tests') or [{}])[0].get('input', ''), encoding='utf-8')
        subprocess.run([PYTHON, '-I', '-X', 'utf8', '-u', 'mq_pytrace.py', 'rich_runner.py', 'stdin.txt', 'trace.json', '1000'],
                       cwd=work, capture_output=True, timeout=60)
        doc = json.loads((work / 'trace.json').read_text(encoding='utf-8'))
    finally:
        shutil.rmtree(work, ignore_errors=True)
    lines = source.splitlines()
    wanted = [i for i, text in enumerate(lines, 1) if needle in text]
    print(f"status {doc['status']}, {len(doc['trace'])} steps, lines {wanted}")
    seen = {}
    for index, step in enumerate(doc['trace'], 1):
        key_ = (step['line'], step['event'])
        seen[key_] = seen.get(key_, 0) + 1
        if step['line'] in wanted:
            frame = step['stack_to_render'][-1] if step['stack_to_render'] else {}
            shown = {k: (step['heap'].get(str(v[1]), v) if isinstance(v, list) and v and v[0] == 'REF' else v)
                     for k, v in frame.get('encoded_locals', {}).items()}
            print(f"#{index} line {step['line']} {step['event']} nth={seen[key_]} {frame.get('func_name')} {json.dumps(shown, ensure_ascii=False)[:300]}")


if __name__ == '__main__':
    main()
