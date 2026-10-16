"""Publish the approved 24 public lesson repositories, then the composition-only course.

Never moves an existing version tag. Re-running resumes missing files and repositories.
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'target/backend-course'

def api(endpoint,method='GET',payload=None,optional=False):
    args=['gh','api','--hostname','github.com','--method',method,endpoint]
    if payload is not None: args+=['--input','-']
    result=subprocess.run(args,input=None if payload is None else json.dumps(payload,ensure_ascii=True).encode(),capture_output=True)
    if result.returncode:
        if optional and b'HTTP 404' in result.stderr:return None
        raise RuntimeError(result.stderr.decode('utf-8','replace'))
    return json.loads(result.stdout) if result.stdout.strip() else None

def read(repo,path,ref='main'):
    data=api(f'repos/{repo}/contents/{path}?ref={ref}',optional=True)
    return None if data is None else base64.b64decode(data['content'])

def put(repo,path,raw):
    old=api(f'repos/{repo}/contents/{path}',optional=True)
    if old and base64.b64decode(old['content'])==raw:return
    body=dict(message='Publish reusable course material',content=base64.b64encode(raw).decode(),branch='main')
    if old:body['sha']=old['sha']
    api(f'repos/{repo}/contents/{path}','PUT',body)

def ensure(repo,course=False):
    current=api(f'repos/{repo}',optional=True)
    if not current:
        current=api('user/repos','POST',dict(name=repo.split('/')[1],private=False,auto_init=True,
            description='Molip Quest 3 · '+('course composition' if course else 'reusable lesson'),has_issues=course))
    if current['private']:raise RuntimeError(f'{repo} must be public')
    if current['default_branch']!='main':raise RuntimeError(f'{repo}: expected main branch')
    return current

def finalize_prepared(course):
    # Read all immutable content in one GraphQL query. Top-level createRef mutations
    # then run serially on GitHub; no existing reference is updated or forced.
    def snapshot():
        fields=[]
        for index,ref in enumerate(course['lessons']):
            owner,name=ref['repository'].split('/')
            fields.append(f'l{index}:repository(owner:{json.dumps(owner)},name:{json.dumps(name)})'+'{id isPrivate head:ref(qualifiedName:"refs/heads/main"){target{oid}} tag:ref(qualifiedName:'+json.dumps('refs/tags/'+ref['revision'])+')'+'{target{oid}} source:object(expression:"main:lesson.json"){...on Blob{text}} published:object(expression:'+json.dumps(ref['revision']+':lesson.json')+'){...on Blob{text}}}')
        result=api('graphql','POST',dict(query='query {'+' '.join(fields)+'}'))
        if result.get('errors'):raise RuntimeError(result['errors'])
        return result['data']
    data=snapshot();mutations=[];changed=False
    for index,ref in enumerate(course['lessons']):
        repo=data[f'l{index}'];assert repo and not repo['isPrivate']
        if not repo['tag'] and hashlib.sha256(repo['source']['text'].encode()).hexdigest()!=ref['sha256']:
            raw=(OUT/ref['repository'].split('/')[1]/'lesson.json').read_bytes()
            assert hashlib.sha256(raw).hexdigest()==ref['sha256']
            put(ref['repository'],'lesson.json',raw);changed=True
    if changed:data=snapshot()
    for index,ref in enumerate(course['lessons']):
        repo=data[f'l{index}'];assert repo and not repo['isPrivate']
        text=repo['published']['text'] if repo['tag'] else repo['source']['text']
        assert hashlib.sha256(text.encode()).hexdigest()==ref['sha256'],ref['repository']
        if not repo['tag']:
            mutations.append(f'l{index}:createRef(input:{{repositoryId:{json.dumps(repo["id"])},name:{json.dumps("refs/tags/"+ref["revision"])},oid:{json.dumps(repo["head"]["target"]["oid"])}}})'+'{ref{name}}')
    if mutations:
        result=api('graphql','POST',dict(query='mutation {'+' '.join(mutations)+'}'))
        if result.get('errors'):raise RuntimeError(result['errors'])
    data=snapshot()
    for index,ref in enumerate(course['lessons']):
        assert hashlib.sha256(data[f'l{index}']['published']['text'].encode()).hexdigest()==ref['sha256']
        print(f"verified {ref['repository']} @ {ref['revision']}",flush=True)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--publish',action='store_true');parser.add_argument('--prepare',action='store_true');parser.add_argument('--finalize-prepared',action='store_true');args=parser.parse_args()
    course=json.loads((OUT/'mq3-course-java-backend/course.json').read_text(encoding='utf-8'))
    assert api('user')['login']=='jhs512','Wrong gh account'
    if args.finalize_prepared:
        finalize_prepared(course)
        args.publish=True
    for ref in course['lessons']:
        if args.finalize_prepared:continue
        folder=OUT/ref['repository'].split('/')[1]
        raw=(folder/'lesson.json').read_bytes()
        assert hashlib.sha256(raw).hexdigest()==ref['sha256']
        if not args.publish and not args.prepare:
            print(f"ready {ref['repository']} @ {ref['revision']}")
            continue
        repo=ref['repository'];ensure(repo)
        tag=api(f"repos/{repo}/git/ref/tags/{ref['revision']}",optional=True)
        if args.prepare and not tag:
            put(repo,'README.md',(folder/'README.md').read_bytes());put(repo,'lesson.json',raw)
            print(f"prepared {repo}",flush=True)
            continue
        if tag:
            if read(repo,'lesson.json',ref['revision'])!=raw:raise RuntimeError(f'{repo}: immutable tag differs')
        else:
            put(repo,'README.md',(folder/'README.md').read_bytes());put(repo,'lesson.json',raw)
            commit=api(f'repos/{repo}/git/ref/heads/main')['object']['sha']
            api(f'repos/{repo}/git/refs','POST',dict(ref='refs/tags/'+ref['revision'],sha=commit))
        assert read(repo,'lesson.json',ref['revision'])==raw
        print(f"verified {repo} @ {ref['revision']}",flush=True)
    if args.publish:
        repo=course['repository'];ensure(repo,course=True)
        put(repo,'course.json',(OUT/'mq3-course-java-backend/course.json').read_bytes())
        put(repo,'README.md',('# 자바 백엔드 과정\n\n몰입 퀘스트 3의 공개 코스예요.\n\n이 리포는 `course.json`에 수업 구성과 순서만 보관해요.\n24개 수업의 본문과 문제는 각 수업 리포에 있어요.\n수업은 버전 태그와 SHA-256으로 고정해요.\n\n플레이어에서 기존 gh 계정으로 학습해요.\n풀모드와 복습모드 중 자유롭게 선택하세요.\n어느 모드든 필수 문제를 통과하면 수업을 완료해요.\n\n진도는 이 리포의 공개 이슈에 남아요.\n학습자×수업마다 하나의 이슈를 사용해요.\n풀모드 학습과 복습 기록은 따로 보존해요.\n수업이 개정돼도 이전 완료 기록은 유지해요.\n').encode())
        print('Published https://github.com/'+repo,flush=True)

if __name__=='__main__':main()
