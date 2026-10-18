from contextlib import ExitStack
import json
import tempfile
import unittest
from pathlib import Path

from content_review import Artifact, ReviewLedger, ContentTree


class AdjacentReviewTest(unittest.TestCase):
    def test_wording_only_goal_change_reuses_core_flow_with_recorded_evidence(self):
        before = Artifact('step-a/goal', 'goal', '출력 결과를 확인해요.')
        after = Artifact('step-a/goal', 'goal', '출력한 결과를 확인해요.')
        flow = Artifact('step-a/core', 'core_flow', '값을 바꿔 실행하고 출력과 비교한다.')
        with tempfile.TemporaryDirectory() as directory, ExitStack() as resources:
            ledger = resources.enter_context(ReviewLedger(Path(directory) / 'reviews.sqlite3'))
            def assess(request):
                self.assertEqual(request['source_before']['text'], before.text)
                self.assertEqual(request['source_after']['text'], after.text)
                self.assertEqual(request['target']['text'], flow.text)
                return {'change_required': False, 'reason': '표현만 다르고 확인할 행동은 같아요.'}
            decision = ledger.assess(before, after, flow, assess, assessor_key='synthetic-review-v1')
            self.assertFalse(decision.change_required)
            row = ledger.history(flow.key)[0]
            self.assertEqual(row['source_before']['revision'], before.revision)
            self.assertEqual(row['source_after']['revision'], after.revision)
            self.assertEqual(row['target']['revision'], flow.revision)
            self.assertEqual(row['status'], 'reviewed')
            self.assertEqual(flow.text, '값을 바꿔 실행하고 출력과 비교한다.')
            ledger.close()
            reopened = resources.enter_context(ReviewLedger(Path(directory) / 'reviews.sqlite3'))
            def must_not_run(_):
                raise AssertionError('The same reviewed inputs must reuse the decision')
            cached = reopened.assess(before, after, flow, must_not_run, assessor_key='synthetic-review-v1')
            self.assertEqual(cached.review_id, decision.review_id)
            self.assertEqual(len(reopened.history(flow.key)), 1)
            reopened.close()

    def test_unchanged_adjacent_flow_stops_review_and_generation_of_descendants(self):
        goal = Artifact('goal-a', 'goal', '출력을 확인해요.')
        flow = Artifact('flow-a', 'core_flow', '값을 바꾸고 실행해 출력과 비교한다.')
        content = Artifact('content-a', 'content', 'console.log(3);')
        tree = ContentTree([goal, flow, content], {'flow-a': 'goal-a', 'content-a': 'flow-a'})
        with tempfile.TemporaryDirectory() as directory, ExitStack() as resources:
            ledger = resources.enter_context(ReviewLedger(Path(directory) / 'reviews.sqlite3'))
            def assess(request):
                self.assertEqual(request['target']['key'], 'flow-a')
                return {'change_required': False, 'reason': '학습 행동은 그대로예요.'}
            def generate(_):
                raise AssertionError('Unchanged flow must not regenerate any descendants')
            tree.apply(Artifact('goal-a', 'goal', '출력한 값을 확인해요.'), ledger, assess,
                       generate, assessor_key='synthetic-v1', generator_key='synthetic-generator-v1')
            self.assertEqual(tree.artifact('flow-a'), flow)
            self.assertEqual(tree.artifact('content-a'), content)
            self.assertIsNone(tree.generated_from('flow-a'))
            self.assertEqual(tree.reviewed_from('flow-a'), tree.artifact('goal-a').revision)
            self.assertEqual(ledger.history('content-a'), [])
            ledger.close()

    def test_changed_flow_passes_its_own_diff_to_content_then_stops(self):
        goal = Artifact('g', 'goal', '출력을 확인해요.')
        flow = Artifact('f', 'core_flow', '숫자 하나를 출력한다.')
        content = Artifact('c', 'content', 'console.log(3);')
        picture = Artifact('s', 'support_spec', '숫자 3이 나오는 그림')
        tree = ContentTree([goal, flow, content, picture], {'f': 'g', 'c': 'f', 's': 'c'})
        with tempfile.TemporaryDirectory() as directory, ExitStack() as resources:
            ledger = resources.enter_context(ReviewLedger(Path(directory) / 'reviews.sqlite3'))
            def assess(request):
                if request['target']['key'] == 'f':
                    return {'change_required': True, 'reason': '값을 비교하는 행동을 넣어요.'}
                self.assertEqual(request['target']['key'], 'c')
                self.assertEqual(request['source_before']['text'], '숫자 하나를 출력한다.')
                self.assertEqual(request['source_after']['text'], '숫자를 바꿔 출력 차이를 비교한다.')
                return {'change_required': False, 'reason': '현재 코드로도 비교할 수 있어요.'}
            def generate(request):
                self.assertEqual(request['target']['key'], 'f')
                return '숫자를 바꿔 출력 차이를 비교한다.'
            tree.apply(Artifact('g', 'goal', '두 값을 바꿔 출력 차이를 비교해요.'),
                       ledger, assess, generate, assessor_key='synthetic-v1', generator_key='synthetic-generator-v1')
            self.assertEqual(tree.artifact('f').text, '숫자를 바꿔 출력 차이를 비교한다.')
            self.assertEqual(ledger.generation_history('f')[0]['output']['revision'], tree.artifact('f').revision)
            self.assertEqual(tree.artifact('c'), content)
            self.assertEqual(tree.artifact('s'), picture)
            self.assertEqual(ledger.history('s'), [])
            ledger.close()

    def test_failed_or_ambiguous_review_remains_pending_and_can_retry(self):
        goal = Artifact('g', 'goal', '출력을 확인해요.')
        flow = Artifact('f', 'core_flow', '값을 바꾸고 실행한다.')
        tree = ContentTree([goal, flow], {'f': 'g'})
        after = Artifact('g', 'goal', '출력한 값을 확인해요.')
        with tempfile.TemporaryDirectory() as directory, ExitStack() as resources:
            ledger = resources.enter_context(ReviewLedger(Path(directory) / 'reviews.sqlite3'))
            def failed(_):
                raise RuntimeError('Synthetic model unavailable')
            def no_generation(_):
                raise AssertionError('An unreviewed artifact cannot regenerate')
            with self.assertRaisesRegex(RuntimeError, 'unavailable'):
                tree.apply(after, ledger, failed, no_generation, assessor_key='synthetic-v1', generator_key='synthetic-generator-v1')
            self.assertIsNone(tree.reviewed_from('f'))
            self.assertEqual(ledger.history('f')[0]['status'], 'failed')
            with self.assertRaisesRegex(ValueError, '변경 여부'):
                tree.resume(ledger, lambda _: {'change_required': 'false', 'reason': 'ambiguous'},
                            no_generation, assessor_key='synthetic-v1', generator_key='synthetic-generator-v1')
            self.assertEqual(tree.artifact('f'), flow)
            tree.resume(ledger, lambda _: {'change_required': False, 'reason': '영향이 없어요.'},
                        no_generation, assessor_key='synthetic-v1', generator_key='synthetic-generator-v1')
            self.assertEqual(tree.reviewed_from('f'), after.revision)
            self.assertEqual([row['status'] for row in ledger.history('f')], ['reviewed', 'failed', 'failed'])
            ledger.close()

    def test_fixed_player_pilot_keeps_solution_and_other_step_when_goal_wording_changes(self):
        fixture = Path(__file__).parent.parent / 'tests/fixtures/player-pilot/a/lesson.json'
        lesson = json.loads(fixture.read_text(encoding='utf-8'))
        step = lesson['chapters'][0]['units'][0]['steps'][0]
        task = next(task for task in lesson['tasks'] if task['id'] == step['id'])
        goal = Artifact(step['id'] + '/goal', 'goal', step['objectives'][0])
        flow = Artifact(step['id'] + '/core', 'core_flow', '코드 값을 바꾸고 출력된 숫자와 비교한다.')
        content = Artifact(step['id'] + '/content', 'content', task['solution'])
        other = Artifact(lesson['tasks'][1]['id'] + '/content', 'content', lesson['tasks'][1]['solution'])
        tree = ContentTree([goal, flow, content, other], {flow.key: goal.key, content.key: flow.key})
        with tempfile.TemporaryDirectory() as directory, ExitStack() as resources:
            ledger = resources.enter_context(ReviewLedger(Path(directory) / 'reviews.sqlite3'))
            def generate(_):
                raise AssertionError('No artifact should regenerate for this wording-only edit')
            tree.apply(Artifact(goal.key, 'goal', '출력된 값을 확인해요: 3'), ledger,
                       lambda _: {'change_required': False, 'reason': '숫자 3을 출력해 확인하는 목표는 같아요.'},
                       generate, assessor_key='synthetic-pilot-v1')
            self.assertEqual(tree.artifact(content.key), content)
            self.assertEqual(tree.artifact(other.key), other)
            self.assertEqual(ledger.history(other.key), [])
            self.assertEqual(ledger.history(flow.key)[0]['target']['revision'], flow.revision)
            ledger.close()

    def test_direct_edit_cannot_inherit_provenance_of_the_previous_generated_text(self):
        goal = Artifact('g', 'goal', '출력을 확인해요.')
        flow = Artifact('f', 'core_flow', '숫자 하나를 출력한다.')
        tree = ContentTree([goal, flow], {'f': 'g'})
        with tempfile.TemporaryDirectory() as directory, ExitStack() as resources:
            ledger = resources.enter_context(ReviewLedger(Path(directory) / 'reviews.sqlite3'))
            changed_goal = Artifact('g', 'goal', '출력 차이를 비교해요.')
            reviewer = lambda _: {'change_required': True, 'reason': '비교 행동을 넣어요.'}
            tree.apply(changed_goal, ledger, reviewer, lambda _: '두 번 실행해 비교한다.', assessor_key='synthetic-v1', generator_key='synthetic-generator-v1')
            self.assertEqual(tree.generated_from('f'), changed_goal.revision)
            tree.apply(Artifact('f', 'core_flow', '직접 편집한 다른 흐름'), ledger,
                       reviewer, lambda _: self.fail('No descendants exist'), assessor_key='synthetic-v1', generator_key='synthetic-generator-v1')
            self.assertIsNone(tree.generated_from('f'))
            self.assertIsNone(tree.reviewed_from('f'))
            self.assertEqual(len(ledger.history('f')), 1)
            ledger.close()

    def test_generation_history_binds_output_and_reuses_only_successful_results(self):
        before = Artifact('g', 'goal', '출력을 확인해요.')
        after = Artifact('g', 'goal', '출력 차이를 비교해요.')
        flow = Artifact('f', 'core_flow', '한 번 실행한다.')
        with tempfile.TemporaryDirectory() as directory, ExitStack() as resources:
            path = Path(directory) / 'reviews.sqlite3'
            ledger = resources.enter_context(ReviewLedger(path))
            decision = ledger.assess(before, after, flow,
                lambda _: {'change_required': True, 'reason': '두 번 비교해야 해요.'}, assessor_key='review-v1')
            def failed(_):
                raise RuntimeError('Synthetic generation unavailable')
            with self.assertRaisesRegex(RuntimeError, 'unavailable'):
                ledger.generate(before, after, flow, decision, failed, generator_key='generate-v1')
            generated = ledger.generate(before, after, flow, decision,
                                        lambda _: '두 번 실행해 차이를 비교한다.', generator_key='generate-v1')
            history = ledger.generation_history('f')
            self.assertEqual([row['status'] for row in history], ['succeeded', 'failed'])
            self.assertEqual(history[0]['output'], generated.snapshot())
            self.assertEqual(history[0]['target'], flow.snapshot())
            self.assertEqual(history[0]['review_id'], decision.review_id)
            ledger.close()
            reopened = resources.enter_context(ReviewLedger(path))
            def no_duplicate(_):
                raise AssertionError('An unchanged successful generation must be reused')
            cached = reopened.generate(before, after, flow, decision, no_duplicate, generator_key='generate-v1')
            self.assertEqual(cached, generated)
            self.assertEqual(len(reopened.generation_history('f')), 2)


if __name__ == '__main__':
    unittest.main()
