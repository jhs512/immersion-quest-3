"""Exercise the model process boundary without network calls or real lesson changes."""
import json
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from content_review import Artifact, ReviewLedger
from content_review_model import JsonReviewModel
from lesson_prd import approve, validate


class ModelTests(unittest.TestCase):
    def test_policy_change_can_produce_only_an_unapproved_prd_draft(self):
        document = json.loads((Path(__file__).resolve().parents[1] /
            'tests/fixtures/lesson-prd/git-first.json').read_text(encoding='utf-8'))
        approved = approve(document, 'fixture-human', 'Isolated test approval only')
        with tempfile.TemporaryDirectory() as directory:
            worker = Path(directory) / 'model.py'
            worker.write_text('''import json, sys
request = json.load(sys.stdin)
assert request['operation'] == 'draft_prd'
document = json.loads(request['input']['target']['text'])
document['title'] = document['title'] + ' 수정 초안'
print(json.dumps({'prd': document}))
''', encoding='utf-8')
            model = JsonReviewModel([sys.executable, '-X', 'utf8', str(worker)], model_revision='fixture-v1')
            with self.assertRaisesRegex(ValueError, '정책 원본'):
                model.authorize_lineage([Artifact('prd', 'prd', json.dumps(approved)),
                    Artifact('policy', 'policy', 'different policy revision')])
            before = Artifact('policy', 'policy', 'older policy revision')
            after = Artifact('policy', 'policy', 'different policy revision')
            target = Artifact('prd', 'prd', json.dumps(approved))
            database = Path(directory) / 'old-results.db'
            with ReviewLedger(database) as ledger:
                decision = ledger.assess(before, after, target,
                    lambda _: {'change_required': True, 'reason': 'Synthetic pre-fix review'}, assessor_key=model.identity)
                ledger.generate(before, after, target, decision,
                    lambda _: json.dumps(dict(approved, title='Cached pre-fix draft')),
                    generator_key=model.identity)
            with ReviewLedger(database) as reopened:
                with self.assertRaisesRegex(ValueError, '정책 원본'):
                    reopened.generate(before, after, target, decision,
                        lambda _: self.fail('Cached result must not trigger generation'),
                        generator_key=model.identity,
                        authorize=lambda: model.authorize_lineage([target, after]))
                self.assertEqual(reopened.generation_history('prd')[0]['status'], 'failed')
            with self.assertRaisesRegex(ValueError, '정책 원본'):
                model.generate({'target': {'key': 'prd', 'layer': 'prd', 'text': json.dumps(approved)},
                    'source_after': {'key': 'policy', 'layer': 'policy', 'text': 'different policy revision'}})
            value = json.loads(model.generate({'target': {'key': 'prd', 'layer': 'prd',
                'text': json.dumps(approved)}, 'source_after': {'key': 'policy', 'layer': 'policy',
                'text': model.policy_source}}))
            validate(value)
            self.assertEqual(value['approval'], {'status': 'draft'})
            self.assertEqual(value['id'], document['id'])
            with self.assertRaisesRegex(ValueError, '승인'):
                validate(value, require_approval=True)

    def test_generation_requires_approved_prd_and_target_step_binding(self):
        document = json.loads((Path(__file__).resolve().parents[1] /
            'tests/fixtures/lesson-prd/git-first.json').read_text(encoding='utf-8'))
        step_id = document['representative']['step_id']
        step = next(step for chapter in document['chapters'] for unit in chapter['units']
                    for step in unit['steps'] if step['id'] == step_id)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            worker = root / 'model.py'
            worker.write_text('''import json, sys
request = json.load(sys.stdin)
assert request['operation'] == 'generate'
assert request['lesson_prd']['approval']['status'] == 'approved'
assert request['step_id'] == request['lesson_prd']['representative']['step_id']
snapshot = {item['path']: item['text'] for item in request['lesson_prd']['policy_snapshot']['artifacts']}
assert request['voice'] == snapshot['docs/voice.md']
assert request['content_rules'] == snapshot['docs/content-rules.md']
print(json.dumps({'text': '새로 검토한 핵심 흐름'}))
''', encoding='utf-8')
            command = [sys.executable, '-X', 'utf8', str(worker)]
            request = {'target': {'key': 'flow', 'layer': 'core_flow'},
                       'source_after': {'key': 'goal', 'layer': 'goal', 'text': '\n'.join(step['objectives'])}}
            unconfigured = JsonReviewModel(command, model_revision='fixture-v1')
            with self.assertRaisesRegex(ValueError, '승인'):
                unconfigured.generate(request)
            draft = JsonReviewModel(command, model_revision='fixture-v1',
                prd=document, target_steps={'flow': step_id})
            with self.assertRaisesRegex(ValueError, '승인'):
                draft.generate(request)
            approved = approve(document, 'synthetic-test', 'Synthetic approval for isolated test only')
            configured = JsonReviewModel(command, model_revision='fixture-v1',
                prd=approved, target_steps={'flow': step_id, 'goal': step_id})
            self.assertEqual(configured.generate(request), '새로 검토한 핵심 흐름')
            # The external policy files may advance before this lesson's impact review.
            with patch.object(Path, 'read_text', return_value='new unreviewed global policy'):
                later_policy = JsonReviewModel(command, model_revision='fixture-v1',
                    prd=approved, target_steps={'flow': step_id, 'goal': step_id})
            self.assertEqual(later_policy.generate(request), '새로 검토한 핵심 흐름')
            self.assertNotEqual(configured.identity, draft.identity)
            with self.assertRaisesRegex(ValueError, '스텝'):
                configured.generate({'target': {'key': 'other-lesson-flow', 'layer': 'core_flow'}})
            with self.assertRaisesRegex(ValueError, '레이어'):
                configured.generate({'target': {'key': 'flow', 'layer': 'goal'}})
            with self.assertRaisesRegex(ValueError, '교육 목표'):
                configured.generate(dict(request, source_after={'layer': 'goal', 'text': '승인되지 않은 새 교육 목표'}))
            with self.assertRaisesRegex(ValueError, '같은 스텝'):
                configured.generate(dict(request, source_after={'key': 'unrelated-flow',
                    'layer': 'core_flow', 'text': '다른 수업의 흐름'}))
            approved['objectives'][0] = 'caller changed original after construction'
            self.assertEqual(configured.generate(request), '새로 검토한 핵심 흐름')

    def test_invalid_or_failed_process_is_recorded_as_failed_review(self):
        cases = [
            ("print('```json\\n{}\\n```')", ValueError),
            ("print('{\"change_required\": true, \"change_required\": false, \"reason\": \"ambiguous\"}')", ValueError),
            ("print('{\"change_required\": \"false\", \"reason\": \"unknown\"}')", ValueError),
            ("import sys; print('private token', file=sys.stderr); sys.exit(7)", RuntimeError),
            ("import time; time.sleep(2)", subprocess.TimeoutExpired),
        ]
        for program, error in cases:
            with self.subTest(program=program), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                worker = root / 'model.py'
                worker.write_text(program, encoding='utf-8')
                model = JsonReviewModel([sys.executable, str(worker)],
                    model_revision='invalid-fixture-v1',
                    timeout=0.2 if error is subprocess.TimeoutExpired else 10)
                with ReviewLedger(root / 'review.db') as ledger:
                    with self.assertRaises(error) as failure:
                        ledger.assess(Artifact('g', 'goal', 'before'), Artifact('g', 'goal', 'after'),
                            Artifact('f', 'core_flow', 'existing'), model.assess, assessor_key=model.identity)
                    record = ledger.history('f')[0]
                    self.assertEqual(record['status'], 'failed')
                    self.assertNotIn('change_required', record)
                    self.assertNotIn('private token', str(failure.exception))

    def test_process_receives_full_policy_and_strict_review_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            worker = root / 'model.py'
            worker.write_text('''import json, sys
request = json.load(sys.stdin)
assert request['operation'] == 'assess'
assert '한 문장 45자 이내' in request['voice']
assert '인접한 레이어' in request['content_rules']
assert request['input']['source_before']['text'] == '출력을 확인해요.'
assert request['input']['source_after']['text'] == '출력 차이를 비교해요.'
print(json.dumps({'change_required': False, 'reason': '기존 흐름으로 비교할 수 있어요.'}))
''', encoding='utf-8')
            model = JsonReviewModel([sys.executable, '-X', 'utf8', str(worker)],
                                    model_revision='synthetic-model-v1')
            with ReviewLedger(root / 'review.db') as ledger:
                decision = ledger.assess(Artifact('g', 'goal', '출력을 확인해요.'),
                    Artifact('g', 'goal', '출력 차이를 비교해요.'),
                    Artifact('f', 'core_flow', '두 번 실행해 비교한다.'),
                    model.assess, assessor_key=model.identity)
                self.assertFalse(decision.change_required)
                self.assertEqual(ledger.history('f')[0]['status'], 'reviewed')


if __name__ == '__main__':
    unittest.main()
