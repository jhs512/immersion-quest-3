"""Publish the new principle lessons after a desktop release containing this commit.

The remote course is re-read immediately before a SHA-guarded update. Existing
lesson pins, progress identities and unrelated course metadata remain authoritative.
Default is a local plan; --publish also requires --runtime-release TAG.
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
sys.path.insert(0,str(ROOT/'tools/principles_lessons'))
from make import NEW_ORDER

module=importlib.util.spec_from_file_location('redesigned_publisher',ROOT/'tools/publish-redesigned-courses.py')
publisher=importlib.util.module_from_spec(module)
module.loader.exec_module(publisher)
gh=publisher.gh
COURSE='jhs512/mq3-course-redesigned-java-backend'
APP='jhs512/immersion-quest-3'


def encode(value):
    return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')


def additions():
    prepared=json.loads((ROOT/'courses/redesigned-courses/java-backend.json').read_text(encoding='utf-8'))
    rows=[]
    for key in NEW_ORDER:
        repo='jhs512/mq3-lesson-redesigned-'+key
        reference=next(item for item in prepared['lessons'] if item['repository']==repo)
        raw=(ROOT/'courses/redesigned'/f'{key}.json').read_bytes()
        if hashlib.sha256(raw).hexdigest()!=reference['sha256']:
            raise ValueError(f'Prepared lesson hash is stale: {key}')
        lesson=json.loads(raw)
        if any(task.get('interaction') for task in lesson['tasks']):
            raise ValueError(f'A new principle lesson still contains answer picking: {key}')
        rows.append((reference,raw))
    return prepared,rows


def merge_course(remote,prepared,rows):
    value=copy.deepcopy(remote)
    current={row['repository']:row for row in value['lessons']}
    desired={row['repository']:row for row,_ in rows}
    for repo,row in desired.items():
        if repo in current and current[repo]['id']!=row['id']:
            raise ValueError(f'Unexpected published identity: {repo}')
        if repo in current and current[repo]['revision']!=row['revision']:
            raise ValueError(f'A different revision is already public: {repo}')
    # Keep every existing pin byte-for-byte, including another worker's coding
    # conversions. Only these new lesson entries get added or refreshed.
    value['lessons']=[row for row in value['lessons'] if row['repository'] not in desired]+[
        desired['jhs512/mq3-lesson-redesigned-'+key] for key in NEW_ORDER]
    if len({row['id'] for row in value['lessons']})!=len(value['lessons']):
        raise ValueError('Duplicate course lesson identity')
    categories={row['id']:row for row in value.get('categories',[])}
    needed={row['category'] for row,_ in rows}
    for row in prepared.get('categories',[]):
        if row['id'] in needed:
            if row['id'] in categories and categories[row['id']]!=row:
                raise ValueError(f'Conflicting category: {row["id"]}')
            categories[row['id']]=row
    value['categories']=list(categories.values())
    value.setdefault('lesson_previews',{}).update({
        row['id']:prepared['lesson_previews'][row['id']] for row,_ in rows})
    changes=[row for row in prepared['change_history'] if row['summary']=='Docker·DB·객체지향 원리를 직접 구현하는 수업 14개를 더했어요.']
    if len(changes)!=1:raise ValueError('Missing expansion change record')
    history=value.setdefault('change_history',[])
    if not any(row.get('summary')==changes[0]['summary'] for row in history):
        value['change_history']=changes+history
    return value


def require_runtime_release(tag):
    release=gh(f'repos/{APP}/releases/tags/{tag}')
    if release.get('draft') or release.get('prerelease'):
        raise ValueError('The runtime release is not public and stable')
    names=[asset['name'].lower() for asset in release.get('assets',[])]
    if not any(name.endswith('.exe') for name in names) or not any(name.endswith('.dmg') for name in names):
        raise ValueError('Windows and macOS runtime installers must both be public first')
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    comparison=gh(f'repos/{APP}/compare/{commit}...{tag}')
    if comparison['status'] not in ('identical','ahead'):
        raise ValueError('The runtime release does not contain the current implementation commit')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publish',action='store_true')
    parser.add_argument('--runtime-release')
    args=parser.parse_args()
    subprocess.run([sys.executable,str(ROOT/'tools/build-redesigned-course-bundle.py'),'--check'],cwd=ROOT,check=True)
    prepared,rows=additions()
    print(f'Prepared {len(rows)} new lessons; existing course entries will be preserved',flush=True)
    if not args.publish:return
    if not args.runtime_release:raise ValueError('--runtime-release is required before course publication')
    user=gh('user')
    if (user['login'],user['id'])!=('jhs512',4741844):raise ValueError('Unexpected GitHub account')
    require_runtime_release(args.runtime_release)
    for reference,raw in rows:
        publisher.publish_file(reference['repository'],'lesson.json',raw,reference['revision'])
    endpoint=f'repos/{COURSE}/contents/course.json'
    remote_file=gh(endpoint+'?ref=main')
    old_raw=base64.b64decode(remote_file['content'])
    remote=json.loads(old_raw)
    if remote['repository']!=COURSE or remote['id']!=prepared['id']:
        raise ValueError('Unexpected public course identity')
    merged=merge_course(remote,prepared,rows)
    raw=encode(merged)
    if merged!=remote:
        gh(endpoint,'PUT',dict(message='Add 14 principle lessons with verified runtime support',
            branch='main',sha=remote_file['sha'],content=base64.b64encode(raw).decode('ascii')))
    actual=base64.b64decode(gh(endpoint+'?ref=main')['content'])
    if json.loads(actual)!=merged:raise ValueError('Public course does not match the merged course')
    print(f'VERIFIED course: {len(merged["lessons"])} lessons, {args.runtime_release}',flush=True)


if __name__=='__main__':main()
