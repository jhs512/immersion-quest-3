"""The head exercise checks table meaning, independent of printed alignment."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from redesigned_lessons.pandas_head_checks import checker


class HeadCheckerTests(unittest.TestCase):
    def accepts(self, source):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, 'main.py').write_text(source, encoding='utf-8')
            result = subprocess.run([sys.executable, '-I', '-X', 'utf8', '-c', checker()],
                                    cwd=directory, capture_output=True, text=True, timeout=30)
            return result.returncode == 0

    def test_selects_three_rows_without_changing_original_table(self):
        prefix = 'import pandas as pd\ndelivery = {}\ndf = pd.DataFrame(delivery)\n'
        self.assertTrue(self.accepts(prefix + 'print(df.head(3))\n'))
        self.assertFalse(self.accepts(prefix + 'print(df.head(2))\n'))
        self.assertFalse(self.accepts(prefix + 'df = df.head(3)\nprint(df)\n'))
        self.assertFalse(self.accepts(prefix + 'print("a memorized table")\n'))
        self.assertFalse(self.accepts(prefix + 'raise SystemExit(0)\n'))
        self.assertFalse(self.accepts(prefix + "with open('hidden.txt','w') as output:\n    print(df.head(3),file=output)\n"))
        self.assertFalse(self.accepts(prefix + "from contextlib import redirect_stdout\nwith open('hidden.txt','w') as output, redirect_stdout(output):\n    print(df.head(3))\n"))


if __name__ == '__main__':
    unittest.main()
