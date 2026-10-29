"""Prepare a validation data folder for the lesson-clear / lesson-reset design capture.

Creates a fresh `mq3-player-pilot-installed-*` folder (owner marker included) whose local progress
store already holds recorded events for the bundled 자바 백엔드 과정 served as validation version 본:
- java-values: every required problem passed and completed (full completion),
- bash-variables: two practice problems and the designated final challenge passed (challenge clear),
- bash-environment: five of six problems passed (in progress, challenge not passed).
Nothing here touches real accounts, GitHub or the person's data. Prints the folder path.
"""
import json
import secrets
import sqlite3
import sys
import tempfile
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
USER = 987654321
COURSE = 'crs_3f59e7bd-70c1-4e81-9cb0-000000000001'
REPOSITORY = 'mq3-validation/course'


def lesson(key):
    return json.loads((ROOT / 'courses/redesigned' / f'{key}.json').read_text(encoding='utf-8'))


def event(data, kind, task=None, passed=False, at=None, required=None, round_='seed-round'):
    value = {'id': uuid.uuid4().hex, 'key': {'user_id': USER, 'course_id': COURSE, 'lesson_id': data['id']},
             'revision': data['revision'], 'mode': 'full', 'round': round_, 'at': at or int(time.time()) - 3600,
             'kind': kind, 'task_id': task, 'passed': passed, 'required': required or [], 'success_before_view': False}
    return value


def main():
    folder = Path(tempfile.mkdtemp(prefix='mq3-player-pilot-installed-')).resolve()
    (folder / '.mq3-pilot-owner').write_text(secrets.token_hex(16), encoding='utf-8')
    events = []
    values = lesson('java-values')
    required = [t['id'] for t in values['tasks'] if t.get('required', True)]
    events += [event(values, 'attempt', task, True) for task in required]
    events.append(event(values, 'completed', required=required))
    variables = lesson('bash-variables')
    ids = [t['id'] for t in variables['tasks']]
    events += [event(variables, 'attempt', ids[0], True), event(variables, 'attempt', ids[1], True), event(variables, 'attempt', ids[-1], True)]
    environment = lesson('bash-environment')
    events += [event(environment, 'attempt', task['id'], True) for task in environment['tasks'][:5]]
    db = sqlite3.connect(folder / 'progress-events.sqlite3')
    db.executescript("""CREATE TABLE IF NOT EXISTS progress_events (
          sequence INTEGER PRIMARY KEY AUTOINCREMENT, repository TEXT NOT NULL,
          event_id TEXT NOT NULL, user_id TEXT NOT NULL, course_id TEXT NOT NULL,
          lesson_id TEXT NOT NULL, title TEXT NOT NULL, document TEXT NOT NULL,
          pending INTEGER NOT NULL, UNIQUE(repository,user_id,event_id));""")
    for item in events:
        db.execute('INSERT INTO progress_events(repository,event_id,user_id,course_id,lesson_id,title,document,pending) VALUES(?,?,?,?,?,?,?,0)',
                   (REPOSITORY, item['id'], str(USER), COURSE, item['key']['lesson_id'], '', json.dumps(item, ensure_ascii=False)))
    db.commit()
    db.close()
    print(folder)


if __name__ == '__main__':
    sys.exit(main())
