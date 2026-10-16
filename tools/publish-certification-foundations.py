"""Publish certificate lessons and course order; preserve every published tag and learner history.

The ledger tools/certification_course/published.json records the sha256 of the bytes this tool last
confirmed on GitHub. Before anything is written, every remote file must equal either that record or
the new build; any other remote change stops the run so it can be reconciled by hand. Tags are
never moved, course entries are never dropped, and progress issues in course repositories are not
touched. A rerun after a partial failure continues where it stopped.
"""
import base64
import hashlib
import json
from pathlib import Path
import importlib.util

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('pilots',ROOT/'tools/publish-certification-pilots.py')
pilots=importlib.util.module_from_spec(spec);spec.loader.exec_module(pilots)
gh=pilots.gh
MARKER=pilots.MARKER
LEDGER=ROOT/'tools/certification_course/published.json'
OUT=ROOT/'target/certification-foundations'
COURSES=['aice-associate','engineer-practical']


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def save(ledger):
    LEDGER.write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')


def lesson_bytes(course_id,ref):
    own=OUT/ref['id']/'lesson.json'
    path=own if own.exists() else ROOT/'target/certification-pilots'/course_id/'lesson.json'
    raw=path.read_bytes()
    assert sha(raw)==ref['sha256'],(ref['id'],'built lesson differs from the course pin')
    return raw


def remote_file(repo,path,ref=None):
    found=gh(f'repos/{repo}/contents/{path}'+(f'?ref={ref}' if ref else ''),optional=True)
    return (base64.b64decode(found['content']),found['sha']) if found else (None,None)


def check_lesson(ledger,repo,revision,raw):
    """Return the work needed for one pinned lesson, or stop on an unknown remote state."""
    known=ledger['lessons'].get(repo,{})
    metadata=gh('repos/'+repo,optional=True)
    if metadata is None:
        assert not known,(repo,'published repository disappeared')
        return 'create'
    assert metadata['owner']['login']=='jhs512' and metadata['description']==MARKER and not metadata['private'],repo
    tagged,_=remote_file(repo,'lesson.json',revision) if gh(f'repos/{repo}/git/ref/tags/{revision}',optional=True) else (None,None)
    if tagged is not None:
        assert tagged==raw,(repo,revision,'a published tag never changes; bump the revision instead')
        assert known.get(revision) in (None,sha(raw)),(repo,revision,'ledger and tag disagree')
        return 'done'
    assert revision not in known,(repo,revision,'tag recorded in the ledger is missing on GitHub')
    head,_=remote_file(repo,'lesson.json')
    allowed={sha(raw)}|set(known.values())
    assert head is None or sha(head) in allowed,(repo,'main branch has an unknown lesson.json; reconcile first')
    return 'tag'


def publish_lesson(ledger,repo,revision,raw):
    metadata=gh('repos/'+repo,optional=True)
    if metadata is None:
        metadata=gh('user/repos','POST',dict(name=repo.split('/')[1],private=False,description=MARKER,auto_init=True,has_issues=True))
    branch=metadata['default_branch']
    head,blob=remote_file(repo,'lesson.json')
    if head!=raw:
        body=dict(message=f'Publish lesson {revision}',branch=branch,content=base64.b64encode(raw).decode())
        if blob:body['sha']=blob
        gh(f'repos/{repo}/contents/lesson.json','PUT',body)
    if gh(f'repos/{repo}/git/ref/tags/{revision}',optional=True) is None:
        commit=gh(f'repos/{repo}/git/ref/heads/{branch}')['object']['sha']
        gh(f'repos/{repo}/git/refs','POST',dict(ref='refs/tags/'+revision,sha=commit))
    tagged,_=remote_file(repo,'lesson.json',revision)
    assert tagged==raw,(repo,revision,'published bytes differ')
    ledger['lessons'].setdefault(repo,{})[revision]=sha(raw)
    ledger['lessons'][repo]=dict(sorted(ledger['lessons'][repo].items()))
    save(ledger)
    print(f'LESSON https://github.com/{repo}/tree/{revision}',flush=True)


def main(dry_run=False):
    user=gh('user');assert user['login']=='jhs512' and user['id']==4741844,'Unexpected gh account'
    ledger=json.loads(LEDGER.read_text(encoding='utf8'))
    courses={c:(OUT/c/'course.json').read_bytes() for c in COURSES}
    parsed={c:json.loads(raw) for c,raw in courses.items()}
    repos=[{l['repository'] for l in parsed[c]['lessons']} for c in COURSES]
    assert repos[0].isdisjoint(repos[1]),'the two certificate courses never share lessons'
    plan=[]
    # Preflight everything before the first write.
    for c in COURSES:
        course=parsed[c];repo=course['repository']
        remote,_=remote_file(repo,'course.json')
        assert remote is not None and sha(remote) in (ledger['courses'].get(repo),sha(courses[c])),(repo,'course.json changed on GitHub since the last confirmed publish; reconcile first')
        previous=json.loads(remote)
        kept={l['id']:l for l in course['lessons']}
        for old in previous['lessons']:
            assert old['id'] in kept,(repo,old['id'],'never drop a published lesson from a course')
            assert old['revision']==kept[old['id']]['revision'] or old['revision'] in ledger['lessons'].get(old['repository'],{}),(repo,old['id'])
        for ref in course['lessons']:
            raw=lesson_bytes(c,ref)
            state=check_lesson(ledger,ref['repository'],ref['revision'],raw)
            if state!='done':plan.append((ref['repository'],ref['revision'],raw))
    for c in COURSES:
        print(f"PLAN {c}: {len(parsed[c]['lessons'])} lessons",flush=True)
    for repo,revision,raw in plan:
        print(f'PLAN publish {repo} {revision} {sha(raw)[:12]}',flush=True)
    if dry_run:
        print('DRY RUN: preflight passed, nothing written',flush=True)
        return
    for repo,revision,raw in plan:
        publish_lesson(ledger,repo,revision,raw)
    for c in COURSES:
        repo=parsed[c]['repository'];new=courses[c]
        remote,blob=remote_file(repo,'course.json')
        if remote!=new:
            assert sha(remote)==ledger['courses'][repo],(repo,'course.json changed during this run')
            branch=gh('repos/'+repo)['default_branch']
            # The blob sha makes GitHub refuse the write if anyone changed the file meanwhile.
            gh(f'repos/{repo}/contents/course.json','PUT',dict(branch=branch,sha=blob,message='Add the next prerequisite lessons in order',content=base64.b64encode(new).decode()))
        remote,_=remote_file(repo,'course.json')
        assert remote==new,(repo,'course.json was not published as built')
        ledger['courses'][repo]=sha(new);save(ledger)
        for ref in parsed[c]['lessons']:
            tagged,_=remote_file(ref['repository'],'lesson.json',ref['revision'])
            assert tagged is not None and sha(tagged)==ref['sha256'],(ref['id'],'course pin does not match the tag')
        print(f'COURSE https://github.com/{repo}',flush=True)


if __name__=='__main__':
    import sys
    main(dry_run='--dry-run' in sys.argv)
