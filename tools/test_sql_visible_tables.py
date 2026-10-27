"""Real DB clients: visible tables and unchanged grading, without replaying writes."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid

sys.path.insert(0, str(Path(__file__).parent / 'principles_lessons'))
from sql_lab import compose, lab


class SqlVisibleTables(unittest.TestCase):
    def test_mysql_and_postgres(self):
        for engine in ('mysql', 'postgres'):
            with self.subTest(engine=engine), tempfile.TemporaryDirectory(prefix='mq3-sql-table-') as directory:
                cwd = Path(directory)
                env = dict(os.environ, COMPOSE_PROJECT_NAME='mq3-sql-table-' + uuid.uuid4().hex,
                           MSYS_NO_PATHCONV='1')
                shell = 'C:/Program Files/Git/bin/bash.exe' if os.name == 'nt' else shutil.which('bash')
                (cwd / 'compose.yaml').write_text(compose(engine), encoding='utf-8')
                (cwd / 'lab.sh').write_text(lab(engine), encoding='utf-8', newline='\n')
                for name in ('before.sql', 'after.sql'):
                    (cwd / name).write_text('', encoding='utf-8')

                def run(sql, mode):
                    (cwd / 'lesson.sql').write_text(sql, encoding='utf-8', newline='\n')
                    return subprocess.run([shell, 'lab.sh'], cwd=cwd, env=dict(env, MQ3_OUTPUT=mode),
                                          capture_output=True, text=True, encoding='utf-8', timeout=120)

                try:
                    result = run("CREATE TABLE counter(n INT); INSERT INTO counter VALUES(0);\n"
                                 "UPDATE counter SET n=n+1; SELECT n AS changed_once FROM counter;\n"
                                 "SELECT '한글' AS name, NULL AS missing, '' AS empty_text;\n"
                                 "SELECT not_a_column FROM counter; SELECT n AS after_error FROM counter;\n", 'raw')
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn('+---', result.stdout)
                    for value in ('changed_once', 'name', 'missing', 'empty_text', '한글', 'NULL', 'after_error'):
                        self.assertIn(value, result.stdout)
                    self.assertIn('ERROR', result.stderr)
                    plain = run('SELECT n FROM counter;\n', 'grading')
                    self.assertEqual(plain.returncode, 0, plain.stderr)
                    self.assertEqual(plain.stdout.strip(), '1', 'Display must never execute UPDATE twice')
                    empty = run('SELECT n AS empty_result FROM counter WHERE n=999;\n', 'raw')
                    self.assertEqual(empty.returncode, 0, empty.stderr)
                    self.assertNotIn('| 1 ', empty.stdout)
                    if engine == 'postgres':
                        self.assertIn('empty_result', empty.stdout)
                        self.assertIn('(0 rows)', empty.stdout)
                    # Keep two real connections in the persistence exercise.
                    (cwd / 'lab.sh').write_text(lab(engine, separate_observer=True), encoding='utf-8', newline='\n')
                    (cwd / 'after.sql').write_text('SELECT n AS new_connection FROM counter;\n', encoding='utf-8')
                    observed = run('UPDATE counter SET n=n+1;\n', 'raw')
                    self.assertIn('new_connection', observed.stdout)
                    self.assertRegex(observed.stdout, r'\|\s*2\s*\|')
                    print(engine + ': native table, NULL, Unicode, SQL error, empty result, single write, separate connection verified')
                finally:
                    subprocess.run(['docker', 'compose', 'down', '--volumes', '--remove-orphans'],
                                   cwd=cwd, env=env, capture_output=True, timeout=60, check=True)


if __name__ == '__main__':
    unittest.main()
