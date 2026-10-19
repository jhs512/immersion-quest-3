"""Real matplotlib output must be graded, not a printed answer."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from redesigned_lessons.plot_bar_checks import checker


class BarCheckerTests(unittest.TestCase):
    def test_printing_expected_heights_cannot_substitute_for_plotting_means(self):
        script = checker([{'data': {'region': ['n', 'n', 's'], 'minutes': [10, 20, 90]},
                           'heights': [15, 90], 'labels': ['n', 's']}])
        source = '''import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
data = {'region': ['n','n','s','s'], 'minutes': [10,20,30,50]}
df = pd.DataFrame(data)
sns.countplot(data=df, x='region', order=['n','s'])
print([15.0, 40.0])
plt.show()
'''
        python = os.environ.get('MOLIP_PYTHON', sys.executable)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'main.py'
            path.write_text(source, encoding='utf-8')
            result = subprocess.run([python, '-I', '-X', 'utf8', '-c', script], cwd=directory,
                                    capture_output=True, text=True, encoding='utf-8')
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn('실제 막대 높이', result.stderr)
            path.write_text(source + '\nraise SystemExit(0)\n', encoding='utf-8')
            result = subprocess.run([python, '-I', '-X', 'utf8', '-c', script], cwd=directory,
                                    capture_output=True, text=True, encoding='utf-8')
            self.assertNotEqual(result.returncode, 0, 'Early exit skipped every graph assertion')
            path.write_text(source.replace("sns.countplot(data=df, x='region', order=['n','s'])",
                                           "sns.barplot(data=df, x='region', y='minutes', order=['n','s'], errorbar=None)"), encoding='utf-8')
            result = subprocess.run([python, '-I', '-X', 'utf8', '-c', script], cwd=directory,
                                    capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
