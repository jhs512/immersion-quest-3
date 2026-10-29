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

    def test_a_code_flow_step_names_a_line_of_the_code_at_that_moment(self):
        code = 'public class Main {\n    public static void main(String[] args) {\n        int a = 1;\n    }\n}\n'
        flow = {'action': 'code_flow', 'line': 3, 'event': 'step_line', 'target': 'flow_memory', 'say': 'a가 생겨요.'}
        task = {'language': 'java', 'code_flow': True, 'starter_code': code,
                'narration': [flow, {'action': 'code_flow', 'close': True}]}
        compiler.validate_highlights(task)
        for broken, message in [({'line': 4}, '없는 줄'), ({'line': 9}, '없는 줄'), ({'event': 'jump'}, '단계 종류'),
                                ({'nth': 0}, '1 이상'), ({'say': ' '}, '문장'), ({'target': 'output'}, '화면의 한 곳'),
                                ({'lines': [3, 3]}, '항목')]:
            task['narration'][0] = flow | broken
            with self.assertRaisesRegex(ValueError, message):
                compiler.validate_highlights(task)
        task['narration'][0] = flow
        for step in ({'code_flow': False}, {'language': 'python'}):
            with self.assertRaisesRegex(ValueError, '코드 흐름 보기가 없는'):
                compiler.validate_highlights(task | step)
        task['narration'][1] = {'action': 'code_flow', 'close': True, 'line': 3}
        with self.assertRaisesRegex(ValueError, '닫기'):
            compiler.validate_highlights(task)

    def test_a_code_flow_step_follows_the_teacher_patch(self):
        code = 'public class Main {\n    public static void main(String[] args) {\n        int a = 1;\n    }\n}\n'
        task = {'language': 'java', 'code_flow': True, 'starter_code': code, 'narration': [
            {'action': 'patch_code', 'before': '        int a = 1;\n', 'after': '        int a = 1;\n        int b = a;\n'},
            {'action': 'code_flow', 'line': 4, 'say': 'b가 생기기 직전이에요.'}]}
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
