"""Publish only the verified network series after its compatible player release.

Plan by default. Existing immutable tags are never moved. The live course is
read/merged with a contents SHA so unrelated newer lessons and metadata survive.
"""
import argparse
import base64
import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
SOURCE_REPO='jhs512/immersion-quest-3'
COURSE='jhs512/mq3-course-redesigned-java-backend'
PREFIX='jhs512/mq3-lesson-redesigned-'
KEYS=('network-bytes','network-endpoints','network-ip','network-routing',
      'network-dns','network-tcp','network-udp','network-http')
SUMMARY='네트워크 기초와 실제 Docker 상태 실습을 추가했어요.'
spec=importlib.util.spec_from_file_location('network_content_publisher',ROOT/'tools/publish-redesigned-courses.py')
publisher=importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)
gh=publisher.gh


def prepared():
    course=json.loads((ROOT/'courses/redesigned-courses/java-backend.json').read_text(encoding='utf-8'))
    rows=[]
    for key in KEYS:
        ref=next(r for r in course['lessons'] if r['repository']==PREFIX+key)
        raw=(ROOT/'courses/redesigned'/f'{key}.json').read_bytes()
        lesson=json.loads(raw)
        if hashlib.sha256(raw).hexdigest()!=ref['sha256'] or lesson['id']!=ref['id'] or lesson['revision']!=ref['revision']:
            raise ValueError('Prepared lesson identity/hash differs: '+key)
        if any(t.get('interaction') for t in lesson['tasks']):
            raise ValueError('Network lessons must use executable tasks: '+key)
        rows.append((ref,raw))
    if len({r['id'] for r,_ in rows})!=len(KEYS):raise ValueError('Duplicate network identities')
    return course,rows


def merge_course(remote,local):
    if remote.get('repository')!=COURSE or remote.get('id')!=local['id']:
        raise ValueError('Unexpected course identity')
    value=copy.deepcopy(remote)
    new=[next(r for r in local['lessons'] if r['repository']==PREFIX+k) for k in KEYS]
    by_repo={r['repository']:r for r in new}
    existing=copy.deepcopy([r for r in remote['lessons'] if r['repository'] not in by_repo])
    if len({r['repository'] for r in remote['lessons']})!=len(remote['lessons']):raise ValueError('Duplicate live repositories')
    for ref in remote['lessons']:
        if ref['repository'] in by_repo and ref!=by_repo[ref['repository']]:
            raise ValueError('Concurrent network reference differs: '+ref['repository'])
    if {r['id'] for r in existing}&{r['id'] for r in new}:raise ValueError('Network IDs collide with live lessons')
    anchor=PREFIX+'docker-image-container'
    at=next(i for i,r in enumerate(existing) if r['repository']==anchor)+1
    value['lessons']=existing[:at]+copy.deepcopy(new)+existing[at:]
    ids={r['id'] for r in value['lessons']}
    if any(p not in ids for r in new for p in r.get('prerequisites',[])):
        raise ValueError('Live course lacks a required network prerequisite')
    # Keep older/live additional prerequisites while adding the new foundation.
    for ref in value['lessons']:
        if ref['repository']==PREFIX+'docker-network-ports':
            required=by_repo[PREFIX+'network-http']['id']
            ref['prerequisites']=list(dict.fromkeys(ref.get('prerequisites',[])+[required]))
    categories=value.setdefault('categories',[])
    if not any(c['id']=='network' for c in categories):
        categories.append(copy.deepcopy(next(c for c in local['categories'] if c['id']=='network')))
    previews=value.setdefault('lesson_previews',{})
    for ref in new:
        preview=local['lesson_previews'][ref['id']]
        if ref['id'] in previews and previews[ref['id']]!=preview:raise ValueError('Concurrent network preview differs')
        previews[ref['id']]=copy.deepcopy(preview)
    history=value.setdefault('change_history',[])
    if not any(h.get('summary')==SUMMARY for h in history):
        history.insert(0,dict(at=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z'),summary=SUMMARY,
            reason='사용자 지시: 기초 네트워크 원리를 실제 실험하고 수업 본편·채점기까지 적용해 배포해요.',
            details=['바이트·끝점·IP·라우팅·DNS·TCP·UDP·HTTP 여덟 수업이에요.',
                     'Java 실행 문제 32개와 실제 Docker 상태를 검사하는 실습 8개로 구성해요.',
                     'IP·마스크·사용 가능한 주소·인터페이스·루프백·다음 홉·NAT·권한 DNS와 캐시를 연결해요.',
                     'Docker Desktop Linux 엔진과 이 실습을 지원하는 최신 MQ3 플레이어가 필요해요.',
                     '기존 수업의 완료 기록과 운영 과정의 다른 수업은 유지해요.']))
    return value


def require_player_release(tag,commit):
    release=gh(f'repos/{SOURCE_REPO}/releases/tags/{tag}')
    if release.get('draft') or release.get('prerelease'):raise ValueError('Player release is not public/stable')
    required={'molip-quest-3-windows-x64-setup.exe','molip-quest-3-macos-arm64.dmg','SHA256SUMS'}
    if not required.issubset({a['name'] for a in release['assets'] if a['size']>0}):raise ValueError('Player release lacks verified installer assets')
    obj=gh(f'repos/{SOURCE_REPO}/git/ref/tags/{tag}')['object']
    while obj['type']=='tag':obj=gh(f'repos/{SOURCE_REPO}/git/tags/{obj["sha"]}')['object']
    if obj['type']!='commit' or obj['sha']!=commit:raise ValueError('Player tag does not match deployment source commit')
    code=gh(f'repos/{SOURCE_REPO}/contents/src/network_practice.rs?ref={commit}')
    if base64.b64decode(code['content'])!=(ROOT/'src/network_practice.rs').read_bytes():
        raise ValueError('Released player network grader differs from the verified source')
    return release['html_url']


def verify_lessons(rows):
    for ref,raw in rows:
        data=gh(f'repos/{ref["repository"]}/contents/lesson.json?ref={ref["revision"]}')
        if base64.b64decode(data['content'])!=raw:raise ValueError('Immutable network lesson differs: '+ref['repository'])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    actions=parser.add_mutually_exclusive_group()
    actions.add_argument('--publish',action='store_true')
    actions.add_argument('--verify-only',action='store_true')
    actions.add_argument('--stage-lessons',action='store_true',help='Publish immutable lessons only; leave the live course unchanged until its player release exists')
    parser.add_argument('--player-release')
    parser.add_argument('--source-commit')
    args=parser.parse_args()
    subprocess.run([sys.executable,str(ROOT/'tools/build-redesigned-course-bundle.py'),'--check'],cwd=ROOT,check=True)
    local,rows=prepared()
    endpoint=f'repos/{COURSE}/contents/course.json'
    current=gh(endpoint+'?ref=main');remote=json.loads(base64.b64decode(current['content']))
    plan=merge_course(remote,local)
    print(f'Prepared network lessons: {len(rows)}; live course {len(remote["lessons"])} -> {len(plan["lessons"])}; other live references preserved',flush=True)
    if not args.publish and not args.verify_only and not args.stage_lessons:return
    user=gh('user')
    if (user['login'],user['id'])!=('jhs512',4741844):raise ValueError('Unexpected publication account')
    if args.stage_lessons:
        for ref,raw in rows:publisher.publish_file(ref['repository'],'lesson.json',raw,ref['revision'])
        verify_lessons(rows)
        print('STAGED eight immutable network lessons; live course unchanged',flush=True)
        return
    if not args.player_release or not args.source_commit:raise ValueError('Publishing/verification requires a compatible player release and source commit')
    release_url=require_player_release(args.player_release,args.source_commit)
    if args.publish:
        for ref,raw in rows:publisher.publish_file(ref['repository'],'lesson.json',raw,ref['revision'])
        for _ in range(3):
            current=gh(endpoint+'?ref=main');remote=json.loads(base64.b64decode(current['content']));merged=merge_course(remote,local)
            if merged==remote:break
            payload=dict(message='Publish verified network foundations and Docker state-graded labs',branch='main',sha=current['sha'],
                content=base64.b64encode((json.dumps(merged,ensure_ascii=False,indent=2)+'\n').encode()).decode())
            try:
                result=gh(endpoint,'PUT',payload)
            except RuntimeError as error:
                if '409' in str(error):continue
                raise
            committed=gh(endpoint+'?ref='+result['commit']['sha'])
            if json.loads(base64.b64decode(committed['content']))!=merged:raise ValueError('Course commit differs from scoped merge')
            break
        else:raise ValueError('Concurrent course changes prevented publication')
    verify_lessons(rows)
    actual=json.loads(base64.b64decode(gh(endpoint+'?ref=main')['content']))
    expected={ref['repository']:ref for ref,_ in rows}
    if {r['repository']:r for r in actual['lessons'] if r['repository'] in expected}!=expected:raise ValueError('Live course network references differ')
    for ref,_ in rows:
        if actual['lesson_previews'].get(ref['id'])!=local['lesson_previews'][ref['id']]:raise ValueError('Live network preview differs')
    print('VERIFIED '+COURSE+f' ({len(actual["lessons"])} live lessons)',flush=True)
    print('VERIFIED player '+release_url,flush=True)


if __name__=='__main__':main()
