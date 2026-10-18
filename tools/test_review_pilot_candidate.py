"""A reviewed local result becomes only an isolated validation-course candidate."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import subprocess
import sys

from content_review import Artifact, ContentTree, ReviewLedger
from review_pilot_candidate import materialize

FIXTURE = Path(__file__).resolve().parents[1] / 'tests/fixtures/player-pilot/a'


class CandidateTests(unittest.TestCase):
    def test_cli_workflow_exports_only_successful_isolated_results(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'audit'
            process = subprocess.run([sys.executable, '-X', 'utf8',
                str(Path(__file__).with_name('build-review-pilot.py')), '--output', str(output)],
                capture_output=True, text=True, encoding='utf-8', timeout=30)
            self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
            report = json.loads((output / 'result.json').read_text(encoding='utf-8'))
            self.assertTrue(report['failure_export_blocked'])
            self.assertEqual(report['successful_generations'], 1)
            baseline = json.loads((FIXTURE / 'lesson.json').read_text(encoding='utf-8'))
            no_impact = json.loads((output / 'no-impact/lesson.json').read_text(encoding='utf-8'))
            changed = json.loads((output / 'candidate/lesson.json').read_text(encoding='utf-8'))
            self.assertEqual(no_impact['tasks'], baseline['tasks'])
            self.assertEqual(changed['tasks'][0]['goal'], '숫자 3을 출력한 뒤 제출하세요.')
            self.assertEqual(changed['tasks'][1], baseline['tasks'][1])
            for filename in ['course.json', 'lesson.json']:
                self.assertEqual((output / 'candidate' / filename).read_bytes(),
                                 (FIXTURE.parent / 'i' / filename).read_bytes())

    def test_only_reviewed_task_instruction_changes_and_pending_work_cannot_export(self):
        lesson = json.loads((FIXTURE / 'lesson.json').read_text(encoding='utf-8'))
        course = json.loads((FIXTURE / 'course.json').read_text(encoding='utf-8'))
        task = lesson['tasks'][0]
        flow = Artifact(task['id'] + '/core_flow', 'core_flow', '출력할 값을 확인한다.')
        content = Artifact(task['id'] + '/content', 'content', task['goal'])
        tree = ContentTree([flow, content], {content.key: flow.key})
        mapping = {content.key: task['id']}
        with self.assertRaisesRegex(ValueError, '검토 근거'):
            materialize(tree, lesson, course, mapping, revision='pilot-i')
        with tempfile.TemporaryDirectory() as directory, ReviewLedger(Path(directory) / 'review.db') as ledger:
            tree.apply(Artifact(flow.key, flow.layer, '출력 뒤 제출 순서를 명확히 한다.'), ledger,
                lambda _: {'change_required': True, 'reason': '제출 안내를 명확히 해요.'},
                lambda _: '숫자 3을 출력한 뒤 제출하세요.', assessor_key='fixture-v1', generator_key='fixture-v1')
            with self.assertRaisesRegex(ValueError, '스텝'):
                materialize(tree, lesson, course, {content.key: lesson['tasks'][1]['id']}, revision='pilot-i')
            candidate, raw = materialize(tree, lesson, course, mapping, revision='pilot-i')
            output = json.loads(raw)
            self.assertEqual(output['tasks'][0]['goal'], '숫자 3을 출력한 뒤 제출하세요.')
            self.assertEqual(output['tasks'][1], lesson['tasks'][1])
            self.assertEqual(output['tasks'][0]['solution'], task['solution'])
            self.assertEqual(output['chapters'], lesson['chapters'])
            self.assertNotIn('core_flow', raw)
            self.assertEqual(candidate['lessons'][0]['sha256'], hashlib.sha256(raw.encode('utf-8')).hexdigest())
            self.assertEqual(lesson['tasks'][0]['goal'], task['goal'])
            def unavailable(_):
                raise RuntimeError('Synthetic unavailable model')
            with self.assertRaises(RuntimeError):
                tree.apply(Artifact(flow.key, flow.layer, '미완료 변경'), ledger, unavailable,
                           lambda _: self.fail('No generation after failed review'), assessor_key='fixture-v1')
            with self.assertRaisesRegex(ValueError, '미완료'):
                materialize(tree, lesson, course, mapping, revision='pilot-i')


if __name__ == '__main__':
    unittest.main()
