import copy
import json
from pathlib import Path
import unittest

import lesson_prd
import importlib.util


class LessonPrdTest(unittest.TestCase):
    def setUp(self):
        self.document = json.loads((Path(__file__).parent.parent / 'tests/fixtures/lesson-prd/git-first.json').read_text(encoding='utf-8'))

    def test_representative_prd_is_readable_but_does_not_authorize_production(self):
        document = self.document
        text = lesson_prd.render(document)
        self.assertIn(document['title'], text)
        self.assertIn(document['representative']['prompt'], text)
        with self.assertRaisesRegex(ValueError, '승인'):
            lesson_prd.validate(document, require_approval=True)

    def test_approval_binds_the_reviewed_content_and_does_not_modify_the_draft(self):
        approved = lesson_prd.approve(self.document, 'test-reviewer', 'synthetic test approval only')
        lesson_prd.validate(approved, require_approval=True)
        self.assertEqual(self.document['approval']['status'], 'draft')
        approved['objectives'][0] = 'Changed goal after approval'
        with self.assertRaisesRegex(ValueError, '승인 후'):
            lesson_prd.validate(approved, require_approval=True)

    def test_missing_goals_or_duplicate_step_identity_is_rejected(self):
        missing = copy.deepcopy(self.document)
        missing['chapters'][0]['units'][0]['steps'][0]['objectives'] = []
        with self.assertRaisesRegex(ValueError, '교육 목표'):
            lesson_prd.render(missing)
        repeated = copy.deepcopy(self.document)
        steps = repeated['chapters'][0]['units'][0]['steps']
        steps[1]['id'] = steps[0]['id']
        with self.assertRaisesRegex(ValueError, '중복'):
            lesson_prd.validate(repeated)

    def test_strategy_is_optional_and_representative_must_reference_a_step(self):
        document = copy.deepcopy(self.document)
        document.pop('strategy')
        self.assertNotIn('## 선택 교육 전략', lesson_prd.render(document))
        document['representative']['step_id'] = 'missing'
        with self.assertRaisesRegex(ValueError, '연결'):
            lesson_prd.validate(document)

    def test_non_document_or_invalid_approval_has_clear_feedback(self):
        for value in [[], None, 'not a PRD']:
            with self.assertRaisesRegex(ValueError, '객체'):
                lesson_prd.validate(value)
        document = copy.deepcopy(self.document)
        document['approval'] = None
        with self.assertRaisesRegex(ValueError, '승인'):
            lesson_prd.validate(document)

    def test_policy_snapshot_is_reproducible_and_detects_tampering(self):
        lesson_prd.validate(self.document)
        self.document['policy_snapshot']['artifacts'][0]['text'] += 'changed'
        with self.assertRaisesRegex(ValueError, '정책'):
            lesson_prd.validate(self.document)

    def test_git_verification_uses_prd_inputs_and_binds_its_report(self):
        path = Path(__file__).parent / 'verify-prd-git-example.py'
        spec = importlib.util.spec_from_file_location('verify_git_prd', path)
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        self.document['representative']['execution_spec']['files'] = {'memo.txt': 'a different memo\n'}
        result = verifier.verify(self.document)
        self.assertEqual(result['prd_sha256'], lesson_prd.content_hash(self.document))
        self.document['representative']['execution_spec']['expected_index_files'] = ['wrong.txt']
        with self.assertRaises(AssertionError):
            verifier.verify(self.document)


class UnderstandingFirstPrdTest(unittest.TestCase):
    def setUp(self):
        self.document = json.loads((Path(__file__).parent / 'redesigned_lessons/java_launch/draft-prd.json').read_text(encoding='utf-8'))

    def test_first_draft_keeps_the_small_steps(self):
        lesson_prd.validate(self.document)

    def test_cannot_sneak_docker_and_compile_into_one_step(self):
        self.document['chapters'][0]['units'][0]['steps'][0]['complexity']['new_concepts'].append('Docker')
        with self.assertRaisesRegex(ValueError, '새 개념'):
            lesson_prd.validate(self.document)

    def test_cannot_drop_the_ledger_or_require_many_edited_lines(self):
        missing = copy.deepcopy(self.document)
        del missing['chapters'][0]['units'][0]['steps'][0]['complexity']
        with self.assertRaisesRegex(ValueError, '난도'):
            lesson_prd.validate(missing)
        self.document['chapters'][0]['units'][0]['steps'][0]['complexity']['learner_edited_lines'] = 4
        with self.assertRaisesRegex(ValueError, '0~3줄'):
            lesson_prd.validate(self.document)

    def test_cannot_introduce_multiple_services_in_one_unit(self):
        steps = self.document['chapters'][0]['units'][0]['steps']
        steps[0]['complexity']['new_external_services'] = 1
        steps[1]['complexity']['new_external_services'] = 1
        with self.assertRaisesRegex(ValueError, '한 단원'):
            lesson_prd.validate(self.document)


if __name__ == '__main__':
    unittest.main()
