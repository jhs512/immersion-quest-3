"""Execute the draft's learner actions in disposable directories; never publish it."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from lesson_prd import validate, content_hash
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'tools/redesigned_lessons/java_launch'
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None

def verify():
    prd=validate(json.loads((SOURCE/'draft-prd.json').read_text()))
    draft=json.loads((SOURCE/'prototype.json').read_text())
    assert prd['approval']['status']=='draft' and draft['status']=='draft_not_runtime_content'
    steps=[s for c in prd['chapters'] for u in c['units'] for s in u['steps']]
    assert [s['id'] for s in steps]==[s['id'] for s in draft['steps']]
    java=shutil.which('java');assert java,'JDK java is required'
    javac=Path(java).resolve().with_name('javac.exe' if os.name=='nt' else 'javac')
    assert javac.exists(),'Use javac from the same JDK'
    cat=shutil.which('cat');ls=shutil.which('ls');assert cat and ls,'Bash tools cat/ls are required'
    environment=os.environ.copy()
    for name in ['JDK_JAVA_OPTIONS','JDK_JAVAC_OPTIONS','JAVA_TOOL_OPTIONS','_JAVA_OPTIONS','CLASSPATH']:
        environment.pop(name,None)
    version=subprocess.run([java,'-version'],env=environment,text=True,capture_output=True,check=True).stderr.strip()
    scenarios=[]
    for messages in [('첫 메모','둘째 메모','셋째 메모'),('메모 A','다른 메모 B','마지막 메모 C')]:
        def variant(value):
            for original,replacement in zip(('첫 메모','둘째 메모','셋째 메모'),messages):value=value.replace(original,replacement)
            return value
        with tempfile.TemporaryDirectory(prefix='mq-java-launch-') as folder:
            work=Path(folder)
            for name,body in draft['source_files'].items():
                assert name=='Main.java';(work/name).write_text(variant(body),encoding='utf-8')
            evidence=[]
            for planned,task in zip(steps,draft['steps']):
                complexity=planned['complexity']
                assert len(complexity['new_concepts'])==1 and complexity['new_external_services']==0
                assert complexity['learner_edited_lines']<=1
                todo=task['goal'].split('**할 일**')[1]
                numbers=[int(x) for x in re.findall(r'^(\d+)\. ',todo,re.M)]
                assert numbers==list(range(1,len(numbers)+1))
                assert '제출' in todo.splitlines()[-1]
                checks=[]
                for action in task['actions']:
                    path=work/'Main.java'
                    if action['kind']=='learner_edit':
                        before=variant(action['before']);after=variant(action['after']);source=path.read_text()
                        assert source.count(before)==1
                        path.write_text(source.replace(before,after,1),encoding='utf-8')
                        checks.append({'action':'learner_edit','changed_lines':1});continue
                    assert action['kind']=='command'
                    argv=list(action['argv']);executable={'java':java,'javac':str(javac),'cat':cat,'ls':ls}[argv[0]]
                    before=digest(work/'Main.class')
                    run=subprocess.run([executable,*argv[1:]],cwd=work,env=environment,text=True,encoding='utf-8',capture_output=True,timeout=20)
                    assert run.returncode==0,(task['title'],run.stderr)
                    output=run.stdout.replace('\r\n','\n')
                    if 'stdout' in action:assert output==variant(action['stdout']),(task['title'],output)
                    for name in action.get('contains',[]):assert name in output.splitlines()
                    artifact=work/'Main.class';after=digest(artifact)
                    assert artifact.exists()==action['class_exists']
                    if artifact.exists():assert artifact.read_bytes()[:4]==bytes.fromhex('cafebabe')
                    if action.get('class_relation')=='same':assert before==after and after is not None
                    if action.get('class_relation')=='changed':assert before!=after and before and after
                    checks.append({'argv':argv,'stdout':output,'class_sha256':after})
                if task['predict_before_run']:
                    assert task['interaction']['answer']=='second'
                    assert checks[-1]['stdout']!=messages[2]+'\n','A stale class must reject the changed-source prediction'
                evidence.append({'step_id':task['id'],'new_concept':complexity['new_concepts'][0],'checks':checks})
            scenarios.append({'messages':messages,'steps':evidence})
    return {'passed':True,'status':'draft_prototype_only','platform':platform.platform(),'jdk':version,'lesson_id':prd['id'],'steps':len(steps),'scenarios':scenarios,'app_course_modified':False,'external_services':0,'prd_sha256':content_hash(prd),'prototype_sha256':hashlib.sha256((SOURCE/'prototype.json').read_bytes()).hexdigest()}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'target/java-launch-prototype/evidence.json')
    args=parser.parse_args()
    try:result=verify()
    except Exception as error:
        result={'passed':False,'error':str(error)}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    if not result['passed']:print(result['error'],file=sys.stderr);return 1
    print(f"Draft verified: {result['steps']} steps × {len(result['scenarios'])} scenarios; zero external services. Not published.")
    return 0
if __name__=='__main__':raise SystemExit(main())
