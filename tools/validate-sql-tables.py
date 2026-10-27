"""Run the existing actual-engine grader for all changed SQL lessons sequentially."""
from pathlib import Path
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
KEYS = ['sql-first', 'sql-tables-constraints', 'sql-join-group', 'sql-index-plan', 'sql-transactions']
RUNNER = ROOT / 'target/debug/examples/validate_redesigned_lesson'
if sys.platform == 'win32':
    RUNNER = RUNNER.with_suffix('.exe')


def validate(key):
    run = subprocess.Popen([str(RUNNER), f'tests/lesson-cases/{key}.json', f'target/mcq/{key}.json'],
                           cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           text=True, encoding='utf-8', env={**os.environ, 'MQ3_VALIDATE_SQL_SESSION': '1'})
    output = []
    for line in run.stdout:
        output.append(line)
        print(line.rstrip(), flush=True)
    return key, run.wait(), ''.join(output), ''


if __name__ == '__main__':
    failed = False
    for key in KEYS:
        print('Validating ' + key, flush=True)
        key, code, stdout, stderr = validate(key)
        print(key + ': ' + stdout.strip(), flush=True)
        if code:
            failed = True
            print(stderr[-3000:], flush=True)
    raise SystemExit(1 if failed else 0)
