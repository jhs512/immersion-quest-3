"""Build the first independent components after validating whole-course coverage."""
from concurrent.futures import ThreadPoolExecutor
import copy
import hashlib
import json
from pathlib import Path
import importlib
from certification_course import blueprint, foundations, kit
from certification_course.lessons import MODULES, REVISIONS
from principles_course.common import ROOT, compile_narration, execute


def build():
    items=foundations.build()
    # Later lessons live one per module and are proven against representative mistakes.
    proven=set()
    for name in MODULES:
        item=importlib.import_module('certification_course.lessons.'+name).build()
        item['revision']=REVISIONS.get(item['id'],item['revision'])
        proven.add(item['id'])
        items.append(item)
    # A published revision is fixed: different bytes need a new revision, never a moved tag.
    published=json.loads((ROOT/'tools/certification_course/published.json').read_text(encoding='utf8'))['lessons']
    output=ROOT/'target/certification-foundations'
    output.mkdir(parents=True,exist_ok=True)
    def make(item):
        for t in item['tasks']:
            initial=execute(t,t['starter_code'])
            final=execute(t,t['solution'])
            assert final.returncode==0,(t['id'],final.stderr)
            assert initial.returncode!=0 or initial.stdout!=final.stdout,(t['id'],'starter equals solution')
            t['tests'][0]['expected']=final.stdout.rstrip('\n')
        mistakes=None
        pinned=published.get('jhs512/mq3-lesson-'+item['id'],{}).get(item['revision'])
        if item['id'] in proven:
            # A lesson identical to its published bytes was proven when it was published.
            draft=copy.deepcopy(item);kit.finish(draft)
            for t in draft['tasks']:compile_narration(draft,t)
            kit.settle_narration(draft)
            same=pinned==hashlib.sha256((json.dumps(draft,ensure_ascii=False,indent=2)+'\n').encode()).hexdigest()
            if not same:kit.verify(item)
            mistakes=kit.finish(item)
        for t in item['tasks']:
            compile_narration(item,t)
        kit.settle_narration(item)
        folder=output/item['id'];folder.mkdir(exist_ok=True)
        raw=json.dumps(item,ensure_ascii=False,indent=2)+'\n'
        assert pinned in (None,hashlib.sha256(raw.encode()).hexdigest()),(item['id'],item['revision'],
            'published with other bytes; set a new revision in certification_course/lessons/__init__.py REVISIONS')
        (folder/'lesson.json').write_text(raw,encoding='utf8',newline='\n')
        if mistakes is not None:
            (folder/'mistakes.json').write_text(json.dumps(mistakes,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
        print(f"BUILT {item['id']}: {len(item['tasks'])} exercises",flush=True)
    # Lessons are independent and their work is mostly waiting on subprocesses (TensorFlow
    # checks take ~15 s each), so several lessons build at once. Each writes only its own files.
    with ThreadPoolExecutor(max_workers=8) as pool:
        for done in [pool.submit(make,item) for item in items]:done.result()
    plan=blueprint.write()
    for course in plan['courses']:
        references=[]
        for planned in course['lessons']:
            if planned['status']!='implemented':continue
            path=output/planned['id']/'lesson.json'
            pilot={'aice-data-first':'aice-associate','engineer-java-state':'engineer-practical'}.get(planned['id'])
            if not path.exists():path=ROOT/'target/certification-pilots'/pilot/'lesson.json'
            raw=path.read_bytes();item=json.loads(raw)
            # A recommendation only points to an actually available earlier lesson.
            prior=[r['id'] for r in references]
            references.append(dict(id=item['id'],title=item['title'],repository='jhs512/mq3-lesson-'+item['id'],
                revision=item['revision'],sha256=hashlib.sha256(raw).hexdigest(),prerequisites=prior[-1:],required=True,review_enabled=item['review_enabled']))
        manifest=dict(schema_version=1,id=course['id'],title=course['title']+' · 기초부터 시험까지',
            description='전체 학습 순서를 먼저 잡았어요. 완성된 기초 수업부터 차례로 제공해요.',
            repository='jhs512/mq3-course-'+course['id'],lessons=references)
        folder=output/course['id'];folder.mkdir(exist_ok=True)
        (folder/'course.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')


if __name__=='__main__':build()
