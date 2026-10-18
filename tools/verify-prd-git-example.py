"""Verify the draft PRD's representative state transition in a real disposable Git repo."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import lesson_prd


def verify(document=None):
    if document is None:
        source = Path(__file__).resolve().parent.parent / 'tests/fixtures/lesson-prd/git-first.json'
        document = json.loads(source.read_text(encoding='utf-8'))
    lesson_prd.validate(document)
    specification = document['representative']['execution_spec']
    environment = dict(os.environ, GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull)
    for name in list(environment):
        if name.startswith(('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_CONFIG_COUNT', 'GIT_CONFIG_KEY_', 'GIT_CONFIG_VALUE_')):
            environment.pop(name)
    with tempfile.TemporaryDirectory(prefix='mq3-prd-git-') as directory:
        root = Path(directory)
        def git(*arguments, check=True):
            return subprocess.run(['git', *arguments], cwd=root, env=environment, capture_output=True, text=True, encoding='utf-8', check=check)
        git('init', '--quiet', '--initial-branch=main')
        for name, content in specification['files'].items():
            destination = (root / name).resolve()
            if not destination.is_relative_to(root.resolve()) or '.git' in Path(name).parts:
                raise ValueError('실습 파일 경로를 확인하세요.')
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(content.encode('utf-8'))
        assert not git('ls-files').stdout.strip()
        for action in specification['actions']:
            if action[:2] != ['add', '--'] or not action[2:] or any(name not in specification['files'] for name in action[2:]):
                raise ValueError('대표 문제는 지정된 파일의 add만 실행해요.')
            git(*action)
        assert sorted(git('diff', '--cached', '--name-only').stdout.splitlines()) == sorted(specification['expected_index_files'])
        for name in specification['expected_index_files']:
            assert git('show', ':' + name).stdout == specification['files'][name]
        assert (git('rev-parse', '--verify', 'HEAD', check=False).returncode == 0) == specification['expected_head']
        for name, content in specification['files'].items():
            assert (root / name).read_bytes() == content.encode('utf-8')
        return {'passed': True, 'prd_sha256': lesson_prd.content_hash(document), 'checked': ['real untracked file', 'real staging', 'index content', 'HEAD expectation', 'working files preserved'], 'scope': 'representative PRD draft only; not a completed lesson'}


if __name__ == '__main__':
    result = verify()
    output = Path(__file__).resolve().parent.parent / 'target/lesson-prd-audit'
    output.mkdir(parents=True, exist_ok=True)
    (output / 'git-representative.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result))
