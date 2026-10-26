"""Real-engine checks: native output, isolated names/ports, and learner-state reuse."""
import os
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid

sys.path.insert(0, str(Path(__file__).parent / 'principles_lessons'))
from d1_image_container import LESSON


class DockerCliIntro(unittest.TestCase):
    def setUp(self):
        self.project = 'mq3-cli-test-' + uuid.uuid4().hex
        self.owner = 'io.mq3.project=' + self.project
        self.directory = tempfile.TemporaryDirectory(prefix='mq3-cli-test-')
        self.cwd = Path(self.directory.name)
        self.env = dict(os.environ, MQ3_PROJECT=self.project,
                        MQ3_OWNER_LABEL=self.owner, MQ3_ENTRY='commands.sh',
                        MQ3_OUTPUT='raw', MSYS_NO_PATHCONV='1')
        self.shell = shutil.which('bash')
        if os.name == 'nt':
            self.shell = 'C:/Program Files/Git/bin/bash.exe'
        self.steps = LESSON['chapters'][0]['units'][0]['steps']

    def tearDown(self):
        ids = self.docker('ps', '-aq', '--filter', 'label=' + self.owner).split()
        if ids:
            self.docker('rm', '-f', *ids)
        self.directory.cleanup()

    def docker(self, *args):
        return subprocess.check_output(['docker', *args], text=True, encoding='utf-8').strip()

    def run_step(self, mode, source=None, grading=False):
        step = next(s for s in self.steps if s['slug'] == 'cli-' + mode)
        for name, contents in step['files'].items():
            (self.cwd / name).write_text(contents, encoding='utf-8', newline='\n')
        (self.cwd / 'commands.sh').write_text(step['solution'] if source is None else source,
                                             encoding='utf-8', newline='\n')
        env = dict(self.env, MQ3_OUTPUT='grading' if grading else 'raw')
        return subprocess.run([self.shell, 'lab.sh'], cwd=self.cwd, env=env,
                              capture_output=True, text=True, encoding='utf-8', timeout=120)

    def test_ps_shows_docker_table_and_preserves_existing_container(self):
        result = self.run_step('ps')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('CONTAINER ID', result.stdout)
        self.assertIn('IMAGE', result.stdout)
        self.assertIn('NAMES', result.stdout)
        self.assertIn(self.project, result.stdout)
        before = self.docker('ps', '-q', '--filter', 'label=' + self.owner)
        again = self.run_step('ps')
        self.assertEqual(again.returncode, 0, again.stderr)
        self.assertEqual(before, self.docker('ps', '-q', '--filter', 'label=' + self.owner))

    def test_run_uses_nginx_loopback_random_port_and_reports_real_errors(self):
        result = self.run_step('run')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertRegex(result.stdout.strip(), r'^[a-f0-9]{64}$')
        box = self.project + '-nginx'
        info = json.loads(self.docker('inspect', box))[0]
        self.assertEqual(info['Config']['Image'], 'nginx:1.28-alpine')
        bindings = info['NetworkSettings']['Ports']['80/tcp']
        self.assertEqual(bindings[0]['HostIp'], '127.0.0.1')
        self.assertNotIn(bindings[0]['HostPort'], ['80', '8080', '3306', '5432'])
        duplicate = self.run_step('run')
        self.assertNotEqual(duplicate.returncode, 0)
        self.assertIn('already in use', duplicate.stderr)
        self.assertEqual(self.docker('inspect', '-f', '{{.Id}}', box), info['Id'])

    def test_other_container_is_visible_but_cannot_be_stopped(self):
        other = self.project + '-unrelated'
        self.docker('run', '-d', '--name', other, 'nginx:1.28-alpine')
        try:
            result = self.run_step('ps')
            self.assertIn(other, result.stdout)
            blocked = self.run_step('ps', f'docker stop "{other}"\n')
            self.assertNotEqual(blocked.returncode, 0)
            # Also reject extra targets appended to an otherwise owned target.
            blocked = self.run_step('ps', f'docker stop "$BOX" "{other}"\n')
            self.assertNotEqual(blocked.returncode, 0)
            self.assertEqual(self.docker('inspect', '-f', '{{.State.Running}}', other), 'true')
        finally:
            self.docker('rm', '-f', other)

    def test_fixed_or_extra_ports_are_rejected_without_starting_container(self):
        for binding in ('8080:80', '0.0.0.0::80', '127.0.0.1:3306:80'):
            result = self.run_step('run', f'docker run -d --name "$BOX" -p {binding} nginx:1.28-alpine\n')
            self.assertNotEqual(result.returncode, 0)
        result = self.run_step('run', 'docker run -d --name "$BOX" -p 8080:80 -p 127.0.0.1::80 nginx:1.28-alpine\n')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.docker('ps', '-aq', '--filter', 'label=' + self.owner), '')
        result = self.run_step('run', 'docker run --publish=127.0.0.1::80 --name="$BOX" --detach nginx:1.28-alpine\n')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_grading_checks_all_commands_and_rejects_noops(self):
        parent = self.cwd
        base = self.project
        for step in self.steps:
            mode = step['slug'].removeprefix('cli-')
            for valid in (False, True):
                with self.subTest(mode=mode, valid=valid):
                    self.project = base + '-' + mode + ('-ok' if valid else '-bad')
                    self.owner = 'io.mq3.project=' + self.project
                    self.env.update(MQ3_PROJECT=self.project, MQ3_OWNER_LABEL=self.owner)
                    self.cwd = parent / (mode + str(valid))
                    self.cwd.mkdir()
                    try:
                        result = self.run_step(mode, None if valid else 'true\n', grading=True)
                        passed = result.returncode == 0 and result.stdout.strip() == step['tests'][0][1]
                        self.assertEqual(passed, valid, result.stdout + result.stderr)
                    finally:
                        ids = self.docker('ps', '-aq', '--filter', 'label=' + self.owner).split()
                        if ids:
                            self.docker('rm', '-f', *ids)

    def test_raw_logs_and_exec_outputs(self):
        result = self.run_step('logs')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('GET / HTTP', result.stdout)
        result = self.run_step('exec')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), 'hello')


if __name__ == '__main__':
    unittest.main()
