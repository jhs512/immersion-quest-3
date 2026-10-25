"""Publish only the verified first coding-conversion batch, preserving newer remote work.

This content uses the existing Java/terminal runtime. It is independent of the
new Docker/JDBC app release. Tags are immutable; every update uses the file SHA.
"""
import argparse
import base64
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
BASE='02800d257db109f63b6a484293e22ab555fb6907'
COURSE='jhs512/mq3-course-redesigned-java-backend'
KEYS=['java-values','java-conditions','java-launch','java-arrays','java-arguments','java-methods',
      'java-references','java-static','java-roles','java-collections','java-streams','java-files']
module=importlib.util.spec_from_file_location('content_publisher',ROOT/'tools/publish-redesigned-courses.py')
publisher=importlib.util.module_from_spec(module)
module.loader.exec_module(publisher)
gh=publisher.gh


def preflight():
    base=json.loads(subprocess.check_output(['git','show',f'{BASE}:courses/redesigned-courses/java-backend.json'],cwd=ROOT))
    prepared=json.loads((ROOT/'courses/redesigned-courses/java-backend.json').read_text(encoding='utf-8'))
    rows=[]
    for key in KEYS:
        repo='jhs512/mq3-lesson-redesigned-'+key
        old=next(row for row in base['lessons'] if row['repository']==repo)
        new=next(row for row in prepared['lessons'] if row['repository']==repo)
        raw=(ROOT/'courses/redesigned'/f'{key}.json').read_bytes()
        digest=hashlib.sha256(raw).hexdigest()
        proof=json.loads((ROOT/'target/mcq'/f'{key}.json').read_text(encoding='utf-8'))
        if not proof.get('passed') or proof.get('lesson_sha256')!=digest or digest!=new['sha256']:
            raise ValueError(f'Missing current execution evidence: {key}')
        lesson=json.loads(raw)
        if any(task.get('interaction') for task in lesson['tasks']):raise ValueError(f'Answer picking remains: {key}')
        if new['id']!=old['id'] or new['revision']==old['revision']:raise ValueError(f'Invalid revision transition: {key}')
        rows.append((old,new,raw))
    return prepared,rows


def publish_lesson(old,new,raw):
    repo=new['repository']
    info=gh('repos/'+repo)
    if info['owner']['login']!='jhs512' or info['description']!=publisher.MARKER or info['private']:
        raise ValueError('Unexpected repository provenance: '+repo)
    endpoint=f'repos/{repo}/contents/lesson.json'
    tag=gh(f'repos/{repo}/git/ref/tags/{new["revision"]}',optional=True)
    if tag is None:
        current=gh(endpoint+'?ref=main')
        existing=base64.b64decode(current['content'])
        if existing!=raw:
            # Do not overwrite an unpublished update made by someone else.
            if hashlib.sha256(existing).hexdigest()!=old['sha256']:
                raise ValueError('Unrecognized newer lesson main: '+repo)
            result=gh(endpoint,'PUT',dict(message='Replace answer picking with real coding exercises',branch='main',
                sha=current['sha'],content=base64.b64encode(raw).decode('ascii')))
            commit=result['commit']['sha']
        else:
            commit=gh(f'repos/{repo}/git/ref/heads/main')['object']['sha']
        gh(f'repos/{repo}/git/refs','POST',dict(ref='refs/tags/'+new['revision'],sha=commit))
    actual=base64.b64decode(gh(endpoint+'?ref='+new['revision'])['content'])
    if actual!=raw:raise ValueError('Immutable revision differs: '+repo)
    print('VERIFIED '+repo+' @ '+new['revision'],flush=True)


def merge(remote,prepared,rows):
    value=copy.deepcopy(remote)
    for old,new,_ in rows:
        position=next(i for i,row in enumerate(value['lessons']) if row['repository']==new['repository'])
        current=value['lessons'][position]
        if current not in (old,new):raise ValueError('Concurrent course revision changed: '+new['repository'])
        value['lessons'][position]=new
        if new['id'] in prepared.get('lesson_previews',{}):
            value.setdefault('lesson_previews',{})[new['id']]=prepared['lesson_previews'][new['id']]
    summary='Java 12수업의 선택 문제를 직접 구현하는 문제로 바꿨어요.'
    if not any(item.get('summary')==summary for item in value.get('change_history',[])):
        value.setdefault('change_history',[]).insert(0,dict(at='2026-10-25T22:25:00Z',summary=summary,
            reason='사용자 지시: 보기를 고르는 대신 직접 코딩하거나 명령을 실행해 문제를 풀어요.',
            details=['값·조건·컴파일·배열·실행 인자·메서드·참조·static·역할·컬렉션·스트림·파일 입출력 수업이에요.',
                     '기존 기록은 이전 문제에 남고, 본질이 바뀐 문제는 새 단계로 직접 풀어요.',
                     'Java의 나머지 수업과 다른 과정의 객관식은 아직 전환 중이에요. 전체 전환 완료를 뜻하지 않아요.']))
    return value


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publish',action='store_true')
    args=parser.parse_args()
    subprocess.run([sys.executable,str(ROOT/'tools/build-redesigned-course-bundle.py'),'--check'],cwd=ROOT,check=True)
    prepared,rows=preflight()
    print(f'Verified current local evidence for {len(rows)} coding lessons',flush=True)
    if not args.publish:return
    user=gh('user')
    if (user['login'],user['id'])!=('jhs512',4741844):raise ValueError('Unexpected GitHub account')
    endpoint=f'repos/{COURSE}/contents/course.json'
    # Check conflicts before creating any new immutable tags.
    initial=gh(endpoint+'?ref=main')
    remote=json.loads(base64.b64decode(initial['content']))
    if remote.get('repository')!=COURSE or remote['id']!=prepared['id']:raise ValueError('Unexpected course identity')
    merge(remote,prepared,rows)
    for old,new,raw in rows:publish_lesson(old,new,raw)
    current=gh(endpoint+'?ref=main')
    remote=json.loads(base64.b64decode(current['content']))
    merged=merge(remote,prepared,rows)
    if merged!=remote:
        raw=(json.dumps(merged,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
        gh(endpoint,'PUT',dict(message='Publish 12 verified coding-conversion lesson revisions',branch='main',
            sha=current['sha'],content=base64.b64encode(raw).decode('ascii')))
    actual=json.loads(base64.b64decode(gh(endpoint+'?ref=main')['content']))
    if actual!=merged:raise ValueError('Published course differs')
    print('VERIFIED public coding-conversion batch',flush=True)


if __name__=='__main__':main()
