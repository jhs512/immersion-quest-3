"""Teacher line references must resolve against the code at that exact action."""
import importlib.util
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


if __name__ == '__main__':
    unittest.main()
