"""Capture native SQL tables and compare every data row with approved plain-output evidence.

Only the five SQL-client lessons are covered. This is a test fixture recorder, not
a player output parser. Each demo gets a fresh schema in a disposable test project.
"""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import uuid

ROOT = Path(__file__).resolve().parents[1]
KEYS = ['sql-first', 'sql-tables-constraints', 'sql-join-group', 'sql-index-plan', 'sql-transactions']


def data_rows(text, engine):
    rows, borders = [], 0
    for line in text.splitlines():
        if re.fullmatch(r'\+[+\-]+', line.strip()):
            borders += 1
            if borders == 3:
                borders = 0
        elif borders == 2 and line.startswith('|') and line.endswith('|'):
            cells = [cell.strip() for cell in line[1:-1].split('|')]
            if engine == 'postgres':
                cells = ['' if cell == 'NULL' else cell for cell in cells]
            rows.append(('\t' if engine == 'mysql' else '|').join(cells))
    return '\n'.join(rows).rstrip()


def main():
    shell = 'C:/Program Files/Git/bin/bash.exe' if os.name == 'nt' else shutil.which('bash')
    pending = {}
    for engine, keys in [('mysql', KEYS[:2]), ('postgres', KEYS[2:])]:
        with tempfile.TemporaryDirectory(prefix='mq3-table-record-') as directory:
            cwd = Path(directory)
            env = dict(os.environ, COMPOSE_PROJECT_NAME='mq3-table-record-' + uuid.uuid4().hex,
                       MQ3_OUTPUT='raw', MSYS_NO_PATHCONV='1')
            def docker(*args):
                return subprocess.run(['docker', 'compose', *args], cwd=cwd, env=env,
                                      capture_output=True, text=True, encoding='utf-8', timeout=120, check=True)
            try:
                for key in keys:
                    lesson = json.loads((ROOT / f'courses/redesigned/{key}.json').read_text(encoding='utf-8'))
                    previous = json.loads((ROOT / f'tools/principles_lessons/recorded/{key}.json').read_text(encoding='utf-8'))
                    outputs = []
                    for index, task in enumerate(lesson['tasks']):
                        for name, value in task['files'].items():
                            (cwd / name).write_text(value, encoding='utf-8', newline='\n')
                        docker('up', '-d', '--wait', 'db')
                        source = task.get('example_code', task['starter_code'])
                        step_outputs = []
                        for action in task['narration']:
                            if action['action'] == 'patch_code':
                                assert source.count(action['before']) == 1
                                source = source.replace(action['before'], action['after'], 1)
                            elif action['action'] == 'set_code':
                                source = action['code']
                            elif action['action'] == 'run':
                                if engine == 'mysql':
                                    docker('exec', '-T', '-e', 'MYSQL_PWD=lab', 'db', 'mysql', '-uroot', '-e',
                                           'DROP DATABASE IF EXISTS lab; CREATE DATABASE lab CHARACTER SET utf8mb4;')
                                else:
                                    docker('exec', '-T', 'db', 'psql', '-U', 'postgres', '-d', 'lab', '-X', '-q',
                                           '-v', 'ON_ERROR_STOP=1', '-c', 'DROP SCHEMA public CASCADE; CREATE SCHEMA public;')
                                (cwd / 'lesson.sql').write_text(source, encoding='utf-8', newline='\n')
                                result = subprocess.run([shell, 'lab.sh'], cwd=cwd, env=env, capture_output=True,
                                                        text=True, encoding='utf-8', timeout=120, check=True)
                                text = result.stdout.rstrip()
                                expected = previous[index][len(step_outputs)]
                                expected_rows = data_rows(expected, engine) if expected.lstrip().startswith('+') else expected.rstrip()
                                assert data_rows(text, engine) == expected_rows, (
                                    key, index + 1, expected, text, data_rows(text, engine))
                                step_outputs.append(text)
                        assert len(step_outputs) == len(previous[index])
                        outputs.append(step_outputs)
                    pending[key] = outputs
                    print(f'{key}: {len(outputs)} steps; every displayed row matches approved data', flush=True)
            finally:
                if (cwd / 'compose.yaml').exists():
                    docker('down', '--volumes', '--remove-orphans')
    # Never bless partially checked recordings.
    for key, outputs in pending.items():
        (ROOT / f'tools/principles_lessons/recorded/{key}.json').write_text(
            json.dumps(outputs, ensure_ascii=False, indent=1) + '\n', encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
