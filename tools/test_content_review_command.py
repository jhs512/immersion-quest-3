"""Exercise the authoring command through real files and subprocesses."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from content_review import Artifact, ContentTree
from lesson_prd import approve

COMMAND = Path(__file__).with_name('content_review_command.py')


class CommandTests(unittest.TestCase):
    def run_command(self, *arguments):
        return subprocess.run([sys.executable, '-X', 'utf8', str(COMMAND), *map(str, arguments)],
                              capture_output=True, text=True, encoding='utf-8', timeout=20)

    def test_author_can_apply_no_impact_change_and_read_persisted_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state, database = root / 'tree.json', root / 'ledger.db'
            ContentTree([Artifact('g', 'goal', '출력을 확인해요.'),
                         Artifact('f', 'core_flow', '두 번 실행해 비교한다.')], {'f': 'g'}).save(state)
            worker = root / 'model.py'
            worker.write_text('''import json, sys
request = json.load(sys.stdin)
assert request['operation'] == 'assess'
print(json.dumps({'change_required': False, 'reason': '기존 흐름이 새 목표를 충족해요.'}))
''', encoding='utf-8')
            config = root / 'model.json'
            config.write_text(json.dumps({'command': [sys.executable, '-X', 'utf8', str(worker)],
                                          'model_revision': 'isolated-fixture-v1'}), encoding='utf-8')
            replacement = root / 'replacement.json'
            replacement.write_text(json.dumps({'key': 'g', 'layer': 'goal',
                'text': '출력 차이를 비교해요.'}, ensure_ascii=False), encoding='utf-8')
            result = self.run_command('apply', '--state', state, '--ledger', database,
                                      '--model-config', config, '--replacement', replacement)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(ContentTree.load(state).artifact('f').text, '두 번 실행해 비교한다.')
            history = self.run_command('history', '--ledger', database, '--target', 'f')
            self.assertEqual(history.returncode, 0, history.stderr)
            records = json.loads(history.stdout)
            self.assertFalse(records['reviews'][0]['change_required'])
            self.assertEqual(records['generations'], [])

    def test_unapproved_generation_stays_pending_and_can_resume_after_real_approval_record(self):
        document = json.loads((Path(__file__).resolve().parents[1] /
            'tests/fixtures/lesson-prd/git-first.json').read_text(encoding='utf-8'))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state, database = root / 'tree.json', root / 'ledger.db'
            ContentTree([Artifact('g', 'goal', '기존 목표'), Artifact('f', 'core_flow', '기존 흐름')],
                        {'f': 'g'}).save(state)
            worker = root / 'model.py'
            worker.write_text('''import json, sys
request = json.load(sys.stdin)
if request['operation'] == 'assess':
    result = {'change_required': True, 'reason': '목표에 맞게 흐름을 고쳐요.'}
else:
    assert request['lesson_prd']['approval']['status'] == 'approved'
    result = {'text': '검토 후 수정한 흐름'}
print(json.dumps(result))
''', encoding='utf-8')
            config = root / 'model.json'
            settings = {'command': [sys.executable, '-X', 'utf8', str(worker)],
                        'model_revision': 'isolated-fixture-v1', 'prd': 'prd.json',
                        'target_steps': {'f': document['representative']['step_id'],
                                         'g': document['representative']['step_id']}}
            config.write_text(json.dumps(settings), encoding='utf-8')
            prd = root / 'prd.json'
            prd.write_text(json.dumps(document, ensure_ascii=False), encoding='utf-8')
            replacement = root / 'replacement.json'
            selected_step = next(step for chapter in document['chapters'] for unit in chapter['units']
                                 for step in unit['steps'] if step['id'] == document['representative']['step_id'])
            replacement.write_text(json.dumps({'key': 'g', 'layer': 'goal',
                'text': '\n'.join(selected_step['objectives'])}), encoding='utf-8')
            failed = self.run_command('apply', '--state', state, '--ledger', database,
                '--model-config', config, '--replacement', replacement)
            self.assertEqual(failed.returncode, 1)
            self.assertEqual(ContentTree.load(state).artifact('f').text, '기존 흐름')
            # Trusted approval is synthetic and exists only inside this disposable fixture.
            prd.write_text(json.dumps(approve(document, 'fixture-human', 'Isolated test approval only'),
                                      ensure_ascii=False), encoding='utf-8')
            resumed = self.run_command('resume', '--state', state, '--ledger', database,
                                      '--model-config', config)
            self.assertEqual(resumed.returncode, 0, resumed.stderr)
            self.assertEqual(ContentTree.load(state).artifact('f').text, '검토 후 수정한 흐름')
            history = json.loads(self.run_command('history', '--ledger', database, '--target', 'f').stdout)
            self.assertEqual([item['status'] for item in history['generations']], ['succeeded', 'failed'])

    def test_downstream_generation_cannot_skip_an_unapproved_ancestor_goal(self):
        document = json.loads((Path(__file__).resolve().parents[1] /
            'tests/fixtures/lesson-prd/git-first.json').read_text(encoding='utf-8'))
        approved = approve(document, 'fixture-human', 'Isolated test approval only')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state, database = root / 'tree.json', root / 'ledger.db'
            ContentTree([Artifact('g', 'goal', '승인되지 않은 다른 목표'),
                         Artifact('f', 'core_flow', '기존 흐름'), Artifact('c', 'content', '기존 문제')],
                        {'f': 'g', 'c': 'f'}).save(state)
            worker = root / 'model.py'
            worker.write_text('''import json, sys
request = json.load(sys.stdin)
print(json.dumps({'change_required': True, 'reason': '흐름이 달라요.'} if
    request['operation'] == 'assess' else {'text': '생성되면 안 되는 문제'}))
''', encoding='utf-8')
            (root / 'prd.json').write_text(json.dumps(approved), encoding='utf-8')
            config = root / 'model.json'
            config.write_text(json.dumps({'command': [sys.executable, '-X', 'utf8', str(worker)],
                'model_revision': 'isolated-fixture-v1', 'prd': 'prd.json',
                'target_steps': {key: document['representative']['step_id'] for key in ['g', 'f', 'c']}}), encoding='utf-8')
            replacement = root / 'replacement.json'
            replacement.write_text(json.dumps({'key': 'f', 'layer': 'core_flow', 'text': '바꾼 흐름'}), encoding='utf-8')
            result = self.run_command('apply', '--state', state, '--ledger', database,
                                      '--model-config', config, '--replacement', replacement)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(ContentTree.load(state).artifact('c').text, '기존 문제')


if __name__ == '__main__':
    unittest.main()
