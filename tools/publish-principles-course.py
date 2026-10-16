"""Publish only the new independent course; never updates an existing different file/tag."""
import base64
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
MARKER = 'Molip Quest 3: small Java experiments'


def gh(path, method='GET', body=None, optional=False):
    args = ['gh', 'api', '--hostname', 'github.com', path, '--method', method]
    if body is not None:
        args += ['--input', '-']
    result = subprocess.run(args, input=json.dumps(body, ensure_ascii=True).encode() if body is not None else None,
                            capture_output=True)
    if result.returncode:
        if optional and b'HTTP 404' in result.stderr:
            return None
        raise RuntimeError(result.stderr.decode('utf8', errors='replace'))
    return json.loads(result.stdout)


def publish(repo, filename, tagged=False):
    existing = gh('repos/'+repo, optional=True)
    if existing is None:
        existing = gh('user/repos', 'POST', dict(name=repo.split('/')[1], private=False,
                      description=MARKER, auto_init=True, has_issues=True))
    assert existing['owner']['login'] == 'jhs512' and existing['description'] == MARKER and not existing['private'], repo
    branch = existing['default_branch']
    raw = (ROOT/'target/principles-course'/filename).read_bytes()
    file = gh(f'repos/{repo}/contents/{filename}', optional=True)
    if file:
        assert base64.b64decode(file['content']) == raw, f'Refusing to overwrite {repo}/{filename}'
    else:
        gh(f'repos/{repo}/contents/{filename}', 'PUT', dict(message='Publish independent practice lesson',
           branch=branch, content=base64.b64encode(raw).decode()))
    if tagged:
        ref = gh(f'repos/{repo}/git/ref/tags/v1.0.0', optional=True)
        if ref is None:
            head = gh(f'repos/{repo}/git/ref/heads/{branch}')
            gh(f'repos/{repo}/git/refs', 'POST', dict(ref='refs/tags/v1.0.0', sha=head['object']['sha']))
        tagged_file = gh(f'repos/{repo}/contents/{filename}?ref=v1.0.0')
        assert base64.b64decode(tagged_file['content']) == raw
    print('https://github.com/'+repo)


if __name__ == '__main__':
    user=gh('user')
    assert user['login']=='jhs512' and user['id']==4741844, 'Unexpected gh account'
    publish('jhs512/mq3-lesson-java-principles-output', 'lesson.json', tagged=True)
    publish('jhs512/mq3-course-java-principles', 'course.json')
