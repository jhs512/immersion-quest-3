"""Verify the draft PRD's representative state transition in a real disposable Git repo."""
import json
import os
from pathlib import Path
import subprocess
import tempfile


def verify():
    environment = dict(os.environ, GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull)
    for name in list(environment):
        if name.startswith(('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_CONFIG_COUNT', 'GIT_CONFIG_KEY_', 'GIT_CONFIG_VALUE_')):
            environment.pop(name)
    with tempfile.TemporaryDirectory(prefix='mq3-prd-git-') as directory:
        root = Path(directory)
        def git(*arguments, check=True):
            return subprocess.run(['git', *arguments], cwd=root, env=environment, capture_output=True, text=True, encoding='utf-8', check=check)
        git('init', '--quiet', '--initial-branch=main')
        (root / 'memo.txt').write_bytes('첫 메모\n'.encode())
        assert git('status', '--porcelain=v1').stdout.strip() == '?? memo.txt'
        git('add', '--', 'memo.txt')
        assert git('diff', '--cached', '--name-only').stdout.strip() == 'memo.txt'
        assert git('show', ':memo.txt').stdout == '첫 메모\n'
        assert git('rev-parse', '--verify', 'HEAD', check=False).returncode != 0
        assert (root / 'memo.txt').read_text(encoding='utf-8') == '첫 메모\n'
        return {'passed': True, 'checked': ['real untracked file', 'real staging', 'index content', 'no commit yet', 'working file preserved'], 'scope': 'representative PRD draft only; not a completed lesson'}


if __name__ == '__main__':
    result = verify()
    output = Path(__file__).resolve().parent.parent / 'target/lesson-prd-audit'
    output.mkdir(parents=True, exist_ok=True)
    (output / 'git-representative.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result))
