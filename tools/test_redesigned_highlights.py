"""Teacher line references must resolve against the code at that exact action."""
import importlib.util
import json
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('redesigned_build', Path(__file__).with_name('build-redesigned-git.py'))
compiler = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compiler)


class TeacherHighlightTest(unittest.TestCase):
    def test_rejects_a_silently_unresolved_range(self):
        task = {'starter_code': 'a\nb\nc\n', 'narration': [
            {'action': 'say', 'target': 'lines:1-3', 'text': 'Compare these lines.'}]}
        with self.assertRaisesRegex(ValueError, '강조'):
            compiler.validate_highlights(task)

    def test_checks_the_code_after_each_small_edit(self):
        task = {'example_code': 'a\nb\n', 'starter_code': '', 'narration': [
            {'action': 'patch_code', 'before': 'b', 'after': 'b\nc'},
            {'action': 'say', 'target': 'lines:2:3', 'text': 'The inserted line.'},
            {'action': 'run', 'lines': [3, 3]}]}
        compiler.validate_highlights(task)
        task['narration'].append({'action': 'say', 'target': 'lines:4', 'text': 'No such line.'})
        with self.assertRaisesRegex(ValueError, '강조'):
            compiler.validate_highlights(task)

    def test_rejects_a_whole_problem_spotlight_for_a_spoken_sentence(self):
        for coarse in compiler.COARSE_TARGETS:
            task = {'goal': '재고는 3이에요.', 'starter_code': '', 'narration': [
                {'action': 'say', 'target': coarse, 'text': '재고가 3이라는 조건을 읽어요.'}]}
            with self.assertRaisesRegex(ValueError, '문제 전체'):
                compiler.validate_highlights(task)
        task['narration'][0]['target'] = 'text:재고는 3이에요.'
        compiler.validate_highlights(task)

    def test_an_option_target_must_name_a_shown_option(self):
        task = {'goal': '어느 쪽일까요?', 'starter_code': '', 'interaction': {'kind': 'choice', 'options': [
            {'id': 'keep', 'text': '그대로 둬요'}, {'id': 'move', 'text': '옮겨요'}]},
            'narration': [{'action': 'say', 'target': 'answer:move', 'text': '옮기는 보기가 맞아요.'}]}
        compiler.validate_highlights(task)
        task['narration'][0]['target'] = 'answer:missing'
        with self.assertRaisesRegex(ValueError, '없는 보기'):
            compiler.validate_highlights(task)

    def test_a_caption_only_sentence_needs_a_reviewed_record_that_is_not_stale(self):
        tasks = [{'id': 'stp_a', 'narration': [{'action': 'say', 'text': '일반 주의예요.'}]}]
        with self.assertRaisesRegex(ValueError, '강조 대상이 없는'):
            compiler.check_caption_only('lesson', tasks, set())
        compiler.check_caption_only('lesson', tasks, {('lesson', 'stp_a', '일반 주의예요.')})
        with self.assertRaisesRegex(ValueError, '예외 기록'):
            compiler.check_caption_only('lesson', tasks, {('lesson', 'stp_a', '일반 주의예요.'), ('lesson', 'stp_a', '사라진 문장')})

    def test_shipped_lessons_never_frame_the_whole_problem_for_a_sentence(self):
        root = Path(__file__).resolve().parents[1]
        record = compiler.caption_only_record()
        for name in compiler.LESSONS:
            lesson = json.loads((root / 'courses/redesigned' / f'{name}.json').read_text(encoding='utf-8'))
            for task in lesson['tasks']:
                for action in task['narration']:
                    if action['action'] != 'say':
                        continue
                    self.assertNotIn(action.get('target'), compiler.COARSE_TARGETS, (name, action.get('text')))
                    if not action.get('target'):
                        self.assertIn((name, task['id'], action.get('text', '')), record, name)


if __name__ == '__main__':
    unittest.main()
