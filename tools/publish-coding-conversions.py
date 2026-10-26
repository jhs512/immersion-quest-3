"""Publish selected verified coding conversions, preserving newer remote work.

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
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
BASE='02800d257db109f63b6a484293e22ab555fb6907'
REVIEW_BASE='0717b40f29bd26a1b5de05218631f83145334ba5'
COURSE='jhs512/mq3-course-redesigned-java-backend'
KEYS=['java-values','java-conditions','java-launch','java-arrays','java-arguments','java-methods',
      'java-references','java-static','java-roles','java-collections','java-streams','java-files']
SECOND_BATCH=['java-crud','java-testing','java-regex','java-rq','java-calculator',
              'git-first','git-branch','git-remote','git-branch-advanced']
QUALITY_BATCH=['docker-image-container']
module=importlib.util.spec_from_file_location('content_publisher',ROOT/'tools/publish-redesigned-courses.py')
publisher=importlib.util.module_from_spec(module)
module.loader.exec_module(publisher)
gh=publisher.gh


def check_transition(key,old,new):
    prefix=key+'-'
    old_number=old['revision'].removeprefix(prefix)
    new_number=new['revision'].removeprefix(prefix)
    if new['id']!=old['id'] or new['revision']==old['revision']:
        raise ValueError(f'Invalid revision transition: {key}')
    if old_number.isdigit() and new_number.isdigit() and int(new_number)<=int(old_number):
        raise ValueError(f'Revision must increase: {key}')


def preflight(keys=None):
    base=json.loads(subprocess.check_output(['git','show',f'{BASE}:courses/redesigned-courses/java-backend.json'],cwd=ROOT))
    prepared=json.loads((ROOT/'courses/redesigned-courses/java-backend.json').read_text(encoding='utf-8'))
    review_base=json.loads(subprocess.check_output(['git','show',f'{REVIEW_BASE}:courses/redesigned-courses/java-backend.json'],cwd=ROOT))
    rows=[]
    for key in (KEYS if keys is None else keys):
        repo='jhs512/mq3-lesson-redesigned-'+key
        old=next(row for row in (review_base if key in QUALITY_BATCH else base)['lessons'] if row['repository']==repo)
        new=next(row for row in prepared['lessons'] if row['repository']==repo)
        raw=(ROOT/'courses/redesigned'/f'{key}.json').read_bytes()
        digest=hashlib.sha256(raw).hexdigest()
        proof=json.loads((ROOT/'target/mcq'/f'{key}.json').read_text(encoding='utf-8'))
        if not proof.get('passed') or proof.get('lesson_sha256')!=digest or digest!=new['sha256']:
            raise ValueError(f'Missing current execution evidence: {key}')
        lesson=json.loads(raw)
        if any(task.get('interaction') for task in lesson['tasks']):raise ValueError(f'Answer picking remains: {key}')
        check_transition(key,old,new)
        rows.append((old,new,raw))
    return prepared,rows


def publish_lesson(old,new,raw,message='Replace answer picking with real coding exercises'):
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
            result=gh(endpoint,'PUT',dict(message=message,branch='main',
                sha=current['sha'],content=base64.b64encode(raw).decode('ascii')))
            commit=result['commit']['sha']
        else:
            commit=gh(f'repos/{repo}/git/ref/heads/main')['object']['sha']
        gh(f'repos/{repo}/git/refs','POST',dict(ref='refs/tags/'+new['revision'],sha=commit))
    actual=base64.b64decode(gh(endpoint+'?ref='+new['revision'])['content'])
    if actual!=raw:raise ValueError('Immutable revision differs: '+repo)
    print('VERIFIED '+repo+' @ '+new['revision'],flush=True)


def merge(remote,prepared,rows,apply_sequence=False):
    value=copy.deepcopy(remote)
    for old,new,_ in rows:
        position=next(i for i,row in enumerate(value['lessons']) if row['repository']==new['repository'])
        current=value['lessons'][position]
        pin=lambda row: tuple(row.get(field) for field in ('id','repository','revision','sha256'))
        if pin(current) not in (pin(old),pin(new)):raise ValueError('Concurrent course revision changed: '+new['repository'])
        # A prerequisite/order/category edit is not a conflicting lesson revision.
        # Preserve fresh remote metadata on the converted lesson itself too.
        updated=copy.deepcopy(current)
        updated.update({field:new[field] for field in ('id','title','repository','revision','sha256') if field in new})
        value['lessons'][position]=updated
        if new['id'] in prepared.get('lesson_previews',{}):
            value.setdefault('lesson_previews',{})[new['id']]=prepared['lesson_previews'][new['id']]
    selected={new['repository'].removeprefix('jhs512/mq3-lesson-redesigned-') for _,new,_ in rows}
    first_batch=selected==set(KEYS)
    if first_batch:
        summary='Java 12수업의 선택 문제를 직접 구현하는 문제로 바꿨어요.'
    elif selected==set(SECOND_BATCH):
        summary='Java 5수업과 Git 4수업의 남은 선택 문제를 직접 구현·실행하는 문제로 바꿨어요.'
    elif selected.intersection(QUALITY_BATCH):
        summary='코딩 문제 전환과 전수 점검에서 발견한 해설을 함께 반영했어요.'
    else:
        summary=f'{len(rows)}수업의 선택 문제를 직접 구현·실행하는 문제로 바꿨어요.'
    if not any(item.get('summary')==summary for item in value.get('change_history',[])):
        value.setdefault('change_history',[]).insert(0,dict(at='2026-10-25T22:25:00Z' if first_batch else datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z'),summary=summary,
            reason='사용자 지시: 보기를 고르는 대신 직접 코딩하거나 명령을 실행해 문제를 풀어요.',
            details=['값·조건·컴파일·배열·실행 인자·메서드·참조·static·역할·컬렉션·스트림·파일 입출력 수업이에요.' if first_batch else '바뀐 수업: '+', '.join(new.get('title',new['repository']) for _,new,_ in rows),
                     '기존 기록은 이전 문제에 남고, 본질이 바뀐 문제는 새 단계로 직접 풀어요.',
                     '다른 과정의 선택 문제 전환은 별도로 진행해요. 이 기록이 전체 과정 전환 완료를 뜻하지 않아요.']))
    if apply_sequence:
        actual={row['id']:row for row in value['lessons']}
        expected={row['id']:row for row in prepared['lessons']}
        if len(actual)!=len(value['lessons']) or set(actual)!=set(expected):
            raise ValueError('Concurrent course membership changed; do not overwrite the new list')
        # Only ordering/prerequisites are in scope here. Keep any newer revision,
        # classification, track and previews from the freshly fetched manifest.
        ordered=[]
        for row in prepared['lessons']:
            current=actual[row['id']]
            current['prerequisites']=row['prerequisites']
            ordered.append(current)
        value['lessons']=ordered
        summary='선수 지식과 난이도에 맞춰 전체 추천 순서를 다시 정했어요.'
        if not any(change.get('summary')==summary for change in value.get('change_history',[])):
            value.setdefault('change_history',[]).insert(0,dict(at=datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z'),
                summary=summary,reason='사용자 요청: 분류별 보기와 독립적인 전체 학습 순서를 제공해요.',
                details=['수업 ID와 기존 학습 기록은 유지해요.','참조·컬렉션 다음에 클래스 심화, 트랜잭션·JDBC 다음에 격리·락을 배워요.']))
    return value


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publish',action='store_true')
    parser.add_argument('--lessons',nargs='+',choices=KEYS+SECOND_BATCH+QUALITY_BATCH,help='Default: the original twelve Java lessons')
    parser.add_argument('--apply-sequence',action='store_true',help='Apply the reviewed order and prerequisites, preserving fresh remote metadata')
    args=parser.parse_args()
    subprocess.run([sys.executable,str(ROOT/'tools/build-redesigned-course-bundle.py'),'--check'],cwd=ROOT,check=True)
    keys=KEYS if args.lessons is None else args.lessons
    if len(keys)!=len(set(keys)):raise ValueError('Duplicate selected lesson')
    prepared,rows=preflight(keys)
    print(f'Verified current local evidence for {len(rows)} coding lessons',flush=True)
    if not args.publish:return
    user=gh('user')
    if (user['login'],user['id'])!=('jhs512',4741844):raise ValueError('Unexpected GitHub account')
    endpoint=f'repos/{COURSE}/contents/course.json'
    # Check conflicts before creating any new immutable tags.
    initial=gh(endpoint+'?ref=main')
    remote=json.loads(base64.b64decode(initial['content']))
    if remote.get('repository')!=COURSE or remote['id']!=prepared['id']:raise ValueError('Unexpected course identity')
    merge(remote,prepared,rows,args.apply_sequence)
    for old,new,raw in rows:publish_lesson(old,new,raw)
    current=gh(endpoint+'?ref=main')
    remote=json.loads(base64.b64decode(current['content']))
    merged=merge(remote,prepared,rows,args.apply_sequence)
    if merged!=remote:
        raw=(json.dumps(merged,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
        gh(endpoint,'PUT',dict(message=f'Publish {len(rows)} verified coding-conversion lesson revisions',branch='main',
            sha=current['sha'],content=base64.b64encode(raw).decode('ascii')))
    actual=json.loads(base64.b64decode(gh(endpoint+'?ref=main')['content']))
    if actual!=merged:raise ValueError('Published course differs')
    print('VERIFIED public coding-conversion batch',flush=True)


if __name__=='__main__':main()
