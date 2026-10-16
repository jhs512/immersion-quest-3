"""Publish the two reviewed pilots, preserving every existing different file/tag."""
import base64
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('publisher',ROOT/'tools/publish-principles-course.py')
publisher=importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)
gh=publisher.gh
MARKER='Molip Quest 3: original certification pilot'


def publish(repo,filename,raw,revision=None):
    metadata=gh('repos/'+repo,optional=True)
    if metadata is None:
        metadata=gh('user/repos','POST',dict(name=repo.split('/')[1],private=False,
            description=MARKER,auto_init=True,has_issues=True))
    assert metadata['owner']['login']=='jhs512' and metadata['description']==MARKER and not metadata['private'],repo
    branch=metadata['default_branch']
    endpoint=f'repos/{repo}/contents/{filename}'
    if revision:
        reference=gh(f'repos/{repo}/git/ref/tags/{revision}',optional=True)
        if reference:
            pinned=gh(endpoint+'?ref='+revision)
            assert base64.b64decode(pinned['content'])==raw,'Refusing to change a published tag'
    existing=gh(endpoint,optional=True)
    if existing:
        previous=base64.b64decode(existing['content'])
        if previous!=raw:
            old=json.loads(previous)
            new=json.loads(raw)
            # Only the explicitly reviewed beginner revision may replace this pilot.
            assert repo in ['jhs512/mq3-lesson-aice-data-first','jhs512/mq3-course-aice-associate']
            if filename=='lesson.json':
                assert old['id']==new['id']=='aice-data-first' and old['revision']=='v1.0.0' and new['revision']=='v1.1.0'
            else:
                assert old['id']==new['id']=='aice-associate' and len(old['lessons'])==len(new['lessons'])==1
                assert old['lessons'][0]['revision']=='v1.0.0' and new['lessons'][0]['revision']=='v1.1.0'
            gh(endpoint,'PUT',dict(message='Introduce data and code before manipulating them',branch=branch,sha=existing['sha'],content=base64.b64encode(raw).decode()))
    else:
        gh(endpoint,'PUT',dict(message='Publish original practice pilot',branch=branch,
            content=base64.b64encode(raw).decode()))
    if revision:
        reference=gh(f'repos/{repo}/git/ref/tags/{revision}',optional=True)
        if reference is None:
            head=gh(f'repos/{repo}/git/ref/heads/{branch}')
            gh(f'repos/{repo}/git/refs','POST',dict(ref='refs/tags/'+revision,sha=head['object']['sha']))
        remote=gh(endpoint+'?ref='+revision)
    else:
        remote=gh(endpoint)
    assert base64.b64decode(remote['content'])==raw,'Published bytes differ'
    print('PUBLISHED https://github.com/'+repo,flush=True)


if __name__=='__main__':
    user=gh('user')
    assert user['login']=='jhs512' and user['id']==4741844,'Unexpected account'
    for id in ['aice-associate','engineer-practical']:
        folder=ROOT/'target/certification-pilots'/id
        course=json.loads((folder/'course.json').read_text(encoding='utf8'))
        publish(course['lessons'][0]['repository'],'lesson.json',(folder/'lesson.json').read_bytes(),course['lessons'][0]['revision'])
        publish(course['repository'],'course.json',(folder/'course.json').read_bytes())
