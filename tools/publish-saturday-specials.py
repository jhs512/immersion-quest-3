"""Publish only the two independent workshops; immutable content and tags, repeatable retries."""
import base64
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('sat_publisher', ROOT / 'tools/publish-principles-course.py')
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
def gh(*args, **kwargs):
    for attempt in range(3):
        try:
            return helper.gh(*args, **kwargs)
        except RuntimeError as error:
            # Retrying the same contents/ref request preserves the preflight checks.
            transient = any(word in str(error).lower() for word in ('wsarecv', 'timeout', 'connection', 'tls handshake'))
            if not transient or attempt == 2:
                raise
OUT = ROOT / 'target/saturday-specials'
MARKER = 'Molip Quest 3: independent Saturday workshop'
COURSES = ['aice-saturday-practice', 'engineer-saturday-final']
LEDGER = ROOT / '.scratch/saturday-specials/published.json'


def safe_course_update(repo, current, raw):
    if current is None or current == raw:
        return
    known = json.loads(LEDGER.read_text(encoding='utf8'))
    id = repo.removeprefix('jhs512/mq3-course-')
    assert hashlib.sha256(current).hexdigest() == known.get(id), (repo, 'unknown existing course version')
    old, new = json.loads(current), json.loads(raw)
    kept = {l['id']: l for l in new['lessons']}
    for ref in old['lessons']:
        assert ref['id'] in kept, (repo, 'published lessons remain available')
        replacement = kept[ref['id']]
        assert ref['repository'] == replacement['repository'], (repo, ref['id'], 'preserve lesson repository')
        if (ref['revision'], ref['sha256']) != (replacement['revision'], replacement['sha256']):
            previous = read(ref['repository'], 'lesson.json', ref['revision'])
            assert previous and hashlib.sha256(previous).hexdigest() == ref['sha256']
            upcoming = (OUT / ref['id'] / 'lesson.json').read_bytes()
            assert hashlib.sha256(upcoming).hexdigest() == replacement['sha256']
            safe_lesson_update(ref['repository'], previous, upcoming)


def safe_lesson_update(repo, current, raw):
    if current is None or current == raw:
        return
    old, new = json.loads(current), json.loads(raw)
    assert (old['revision'], new['revision']) in {('v1.0.0', 'v1.0.1'), ('v1.0.1', 'v1.0.2'), ('v1.0.2', 'v1.0.3')}, (repo, 'only authored narration revision')
    assert read(repo, 'lesson.json', old['revision']) == current, (repo, 'previous version must remain immutable')
    for item in (old, new):
        item.pop('revision')
        for task in item['tasks']:
            task.pop('narration')
    assert old == new, (repo, 'only narration and revision may change')


def read(repo, file, revision=None):
    result = gh(f'repos/{repo}/contents/{file}' + (f'?ref={revision}' if revision else ''), optional=True)
    return base64.b64decode(result['content']) if result else None


def publish(repo, file, raw, revision=None):
    metadata = gh('repos/' + repo, optional=True)
    if metadata is None:
        metadata = gh('user/repos', 'POST', dict(name=repo.split('/')[1], private=False,
            description=MARKER, auto_init=True, has_issues=True))
    assert metadata['owner']['login'] == 'jhs512' and metadata['description'] == MARKER and not metadata['private'], repo
    existing = read(repo, file)
    if file == 'course.json':
        safe_course_update(repo, existing, raw)
    else:
        safe_lesson_update(repo, existing, raw)
    if existing is None:
        gh(f'repos/{repo}/contents/{file}', 'PUT', dict(branch=metadata['default_branch'],
            message='Publish original Saturday workshop', content=base64.b64encode(raw).decode()))
    elif existing != raw:
        blob = gh(f'repos/{repo}/contents/{file}')
        assert base64.b64decode(blob['content']) == existing, 'course changed during this run'
        gh(f'repos/{repo}/contents/{file}', 'PUT', dict(branch=metadata['default_branch'], sha=blob['sha'],
            message='Replace truncated narration with authored problem explanations', content=base64.b64encode(raw).decode()))
    if revision:
        ref = gh(f'repos/{repo}/git/ref/tags/{revision}', optional=True)
        if ref is None:
            head = gh(f'repos/{repo}/git/ref/heads/' + metadata['default_branch'])['object']['sha']
            gh(f'repos/{repo}/git/refs', 'POST', dict(ref='refs/tags/' + revision, sha=head))
    assert read(repo, file, revision) == raw, (repo, 'remote bytes differ')
    if file == 'course.json':
        known = json.loads(LEDGER.read_text(encoding='utf8')) if LEDGER.exists() else {}
        known[repo.removeprefix('jhs512/mq3-course-')] = hashlib.sha256(raw).hexdigest()
        LEDGER.write_text(json.dumps(known, indent=2), encoding='utf8')
    print('PUBLISHED https://github.com/' + repo, flush=True)


def main():
    user = gh('user')
    assert user['login'] == 'jhs512' and user['id'] == 4741844
    manifests = [json.loads((OUT / c / 'course.json').read_text(encoding='utf8')) for c in COURSES]
    assert set(l['repository'] for l in manifests[0]['lessons']).isdisjoint(l['repository'] for l in manifests[1]['lessons'])
    # Check every existing file before making the first write.
    entries = []
    for course in manifests:
        for reference in course['lessons']:
            raw = (OUT / reference['id'] / 'lesson.json').read_bytes()
            assert hashlib.sha256(raw).hexdigest() == reference['sha256']
            entries.append((reference['repository'], 'lesson.json', raw, reference['revision']))
        entries.append((course['repository'], 'course.json', (OUT / course['id'] / 'course.json').read_bytes(), None))
    for repo, file, raw, revision in entries:
        metadata = gh('repos/' + repo, optional=True)
        if metadata:
            assert metadata['description'] == MARKER and metadata['owner']['login'] == 'jhs512' and not metadata['private'], repo
            current = read(repo, file)
            if file == 'course.json':
                safe_course_update(repo, current, raw)
            else:
                safe_lesson_update(repo, current, raw)
            if revision and gh(f'repos/{repo}/git/ref/tags/{revision}', optional=True):
                assert read(repo, file, revision) == raw, (repo, 'immutable tag differs')
    for entry in entries:
        publish(*entry)
    # Register only fully published courses in this installation's ordinary catalog.
    import os
    catalog = Path(os.environ['LOCALAPPDATA']) / 'MolipQuest/MolipQuest/data/repository-courses.json'
    saved = json.loads(catalog.read_text(encoding='utf8')) if catalog.exists() else []
    for course in manifests:
        if course['repository'] not in saved:
            saved.append(course['repository'])
    catalog.write_text(json.dumps(saved, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print('VERIFIED independent workshop pins and local course catalog', flush=True)


if __name__ == '__main__':
    main()
