"""Publish only the packaged browser preview to its dedicated public repository."""
import base64
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('publisher',ROOT/'tools/publish-principles-course.py')
publisher=importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)
gh=publisher.gh
REPO='jhs512/mq3-web-player'
MARKER='Molip Quest 3: browser-only course preview'
FIXED=['index.html','style.css','app.js','python-worker.js','editor.bundle.js','split.js','rich_runner.py','.nojekyll',
       'catalog.json','plan-aice-associate.html','plan-engineer-practical.html']
# Lesson files follow the packaged catalog, so a new lesson needs no edit here.
CATALOG=json.loads((ROOT/'target/web-course-preview/catalog.json').read_text(encoding='utf8'))
FILES=FIXED+[entry['path'] for entry in CATALOG]


if __name__=='__main__':
    user=gh('user')
    assert user['login']=='jhs512' and user['id']==4741844
    metadata=gh('repos/'+REPO,optional=True)
    if metadata is None:
        metadata=gh('user/repos','POST',dict(name=REPO.split('/')[1],private=False,description=MARKER,auto_init=True))
    assert metadata['description']==MARKER and metadata['owner']['login']=='jhs512' and not metadata['private']
    branch=metadata['default_branch']
    head=gh(f'repos/{REPO}/git/ref/heads/{branch}')['object']['sha']
    parent=gh(f'repos/{REPO}/git/commits/{head}')
    tree=[]
    for name in FILES:
        raw=(ROOT/'target/web-course-preview'/name).read_bytes()
        blob=gh(f'repos/{REPO}/git/blobs','POST',dict(content=base64.b64encode(raw).decode(),encoding='base64'))
        tree.append(dict(path=name,mode='100644',type='blob',sha=blob['sha']))
    updated=gh(f'repos/{REPO}/git/trees','POST',dict(base_tree=parent['tree']['sha'],tree=tree))
    commit=gh(f'repos/{REPO}/git/commits','POST',dict(message='Publish browser Python course preview',tree=updated['sha'],parents=[head]))
    gh(f'repos/{REPO}/git/refs/heads/{branch}','PATCH',dict(sha=commit['sha'],force=False))
    pages=gh(f'repos/{REPO}/pages',optional=True)
    if pages is None:
        pages=gh(f'repos/{REPO}/pages','POST',dict(source=dict(branch=branch,path='/'),build_type='legacy'))
    print(json.dumps(dict(repository=REPO,url=pages['html_url'],commit=commit['sha']),ensure_ascii=False),flush=True)
