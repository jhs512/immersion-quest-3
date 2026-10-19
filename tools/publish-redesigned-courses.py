"""Publish the prepared independent repositories, without overwriting old courses.

Default is a local plan. --publish creates public repositories in the authorized
account, verifies every immutable lesson tag, then publishes course composition.
Re-running accepts identical files only. A conflicting file or tag stops the run.
"""
import argparse
import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MARKER = 'Molip Quest 3: redesigned independent learning content'
module = importlib.util.spec_from_file_location('mq3_publisher', ROOT / 'tools/publish-principles-course.py')
publisher = importlib.util.module_from_spec(module)
module.loader.exec_module(publisher)
gh = publisher.gh


def publish_file(repository, filename, raw, revision=None):
    if not repository.startswith(('jhs512/mq3-lesson-redesigned-', 'jhs512/mq3-course-redesigned-')):
        raise ValueError('Publication is restricted to the new independent repositories')
    metadata = gh('repos/' + repository, optional=True)
    if metadata is None:
        metadata = gh('user/repos', 'POST', dict(name=repository.split('/')[1],
            private=False, description=MARKER, auto_init=True, has_issues=True))
    if metadata['owner']['login'] != 'jhs512' or metadata['description'] != MARKER or metadata['private']:
        raise ValueError(f'Unexpected repository ownership or provenance: {repository}')
    branch = metadata['default_branch']
    if branch != 'main':
        raise ValueError(f'Expected main branch, found {branch}: {repository}')
    endpoint = f'repos/{repository}/contents/{filename}'
    existing = gh(endpoint, optional=True)
    if existing is not None:
        if base64.b64decode(existing['content']) != raw:
            raise ValueError(f'Refusing to overwrite different published content: {repository}/{filename}')
    else:
        gh(endpoint, 'PUT', dict(message='Publish redesigned learning content', branch=branch,
            content=base64.b64encode(raw).decode('ascii')))
    if revision is not None:
        tag = gh(f'repos/{repository}/git/ref/tags/{revision}', optional=True)
        if tag is None:
            head = gh(f'repos/{repository}/git/ref/heads/main')
            gh(f'repos/{repository}/git/refs', 'POST', dict(ref='refs/tags/' + revision, sha=head['object']['sha']))
        published = gh(endpoint + '?ref=' + revision)
    else:
        published = gh(endpoint + '?ref=main')
    if base64.b64decode(published['content']) != raw:
        raise ValueError(f'Published bytes differ: {repository}')
    print(f'VERIFIED {repository}' + (f' @ {revision}' if revision else ''), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    subprocess.run([sys.executable, str(ROOT / 'tools/build-redesigned-course-bundle.py'), '--check'], cwd=ROOT, check=True)
    manifests = [json.loads(p.read_text(encoding='utf-8')) for p in sorted((ROOT / 'courses/redesigned-courses').glob('*.json'))]
    if len(manifests) != 3:
        raise ValueError('Exactly three course manifests are required')
    catalog = json.loads((ROOT / 'tools/redesigned_courses/catalog.json').read_text(encoding='utf-8'))
    paths = {lesson['id']: ROOT / 'courses/redesigned' / (lesson['key'] + '.json')
        for course in catalog['courses'] for lesson in course['lessons']}
    files = []
    for course in manifests:
        for lesson in course['lessons']:
            raw = paths[lesson['id']].read_bytes()
            if hashlib.sha256(raw).hexdigest() != lesson['sha256']:
                raise ValueError('Lesson bytes do not match the prepared course')
            files.append((lesson['repository'], 'lesson.json', raw, lesson['revision']))
    if not args.publish:
        print(f'Prepared {len(files)} independent lessons and {len(manifests)} courses; no remote changes')
        return
    user = gh('user')
    if user['login'] != 'jhs512' or user['id'] != 4741844:
        raise ValueError('Unexpected gh account')
    for item in files:
        publish_file(*item)
    # A course is visible only after every referenced immutable lesson was verified.
    for course in manifests:
        name = course['repository'].removeprefix('jhs512/mq3-course-redesigned-')
        raw = (ROOT / 'courses/redesigned-courses' / (name + '.json')).read_bytes()
        publish_file(course['repository'], 'course.json', raw)


if __name__ == '__main__':
    main()
