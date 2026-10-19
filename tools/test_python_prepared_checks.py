"""A printed request must not substitute for the fitted object's state."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from redesigned_lessons.python_prepared_checks import checker


class PreparedProbeTests(unittest.TestCase):
    def check_source(self, source, probe=True):
        script = checker([{'values': {'tree_count': 1}, 'expected': '1'},
                          {'values': {'tree_count': 3}, 'expected': '3'}],
                         'assert len(model.estimators_) == tree_count' if probe else None)
        with tempfile.TemporaryDirectory() as folder:
            Path(folder, 'main.py').write_text(source, encoding='utf-8')
            return subprocess.run([sys.executable, '-I', '-X', 'utf8', '-c', script],
                                  cwd=folder, capture_output=True, text=True, encoding='utf-8')

    def test_requested_count_is_checked_on_actual_model(self):
        wrong = '''from types import SimpleNamespace
tree_count = 3
model = SimpleNamespace(estimators_=[object()])
print(tree_count)
'''
        self.assertNotEqual(self.check_source(wrong).returncode, 0)
        correct = wrong.replace('estimators_=[object()]',
                                'estimators_=[object() for _ in range(tree_count)]')
        result = self.check_source(correct)
        self.assertEqual(result.returncode, 0, result.stderr)
        skipped = self.check_source(wrong + '\nraise SystemExit(0)\n')
        self.assertNotEqual(skipped.returncode, 0)
        self.assertIn('실제 실행 상태', skipped.stderr)

    def test_explicit_budget_allows_slow_cases_but_still_stops_them(self):
        cases = [{'values': {'tree_count': 1}, 'expected': '1'}]
        with tempfile.TemporaryDirectory() as folder:
            Path(folder, 'main.py').write_text(
                'import time\ntime.sleep(1.5)\ntree_count = 1\nprint(tree_count)\n', encoding='utf-8')
            results = []
            for seconds in [1, 3]:
                results.append(subprocess.run(
                    [sys.executable, '-I', '-X', 'utf8', '-c', checker(cases, timeout_seconds=seconds)],
                    cwd=folder, capture_output=True, text=True, encoding='utf-8', timeout=10))
        self.assertNotEqual(results[0].returncode, 0)
        self.assertIn('TimeoutExpired', results[0].stderr)
        self.assertEqual(results[1].returncode, 0, results[1].stderr)
        for invalid in [0, 46, True, '45']:
            with self.assertRaises(ValueError):
                checker(cases, timeout_seconds=invalid)

    def test_timeout_template_does_not_rewrite_literal_prepared_values(self):
        with tempfile.TemporaryDirectory() as folder:
            Path(folder, 'main.py').write_text('tree_count = 1\nprint(tree_count)\n', encoding='utf-8')
            script = checker([{'values': {'tree_count': 'CASE_TIMEOUT'}, 'expected': 'CASE_TIMEOUT'}])
            result = subprocess.run([sys.executable, '-I', '-X', 'utf8', '-c', script],
                                    cwd=folder, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_existing_output_only_cases_remain_compatible(self):
        result = self.check_source('tree_count = 3\nprint(tree_count)\n', probe=False)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
