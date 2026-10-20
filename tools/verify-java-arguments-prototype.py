"""Verify the independent argument lesson with the real Bash parser and JDK."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from lesson_prd import validate,content_hash

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'tools/redesigned_lessons/java_arguments'

def verify():
    prd=validate(json.loads((SOURCE/'approved-prd.json').read_text(encoding='utf-8')),True)
    prototype=json.loads((SOURCE/'prototype.json').read_text(encoding='utf-8'))
    steps=[s for c in prd['chapters'] for u in c['units'] for s in u['steps']]
    assert [s['id'] for s in steps]==[s['id'] for s in prototype['steps']]
    java=shutil.which('java')
    bash=shutil.which('bash')
    if os.name=='nt':
        installed=Path(os.environ.get('ProgramFiles','C:/Program Files'))/'Git/bin/bash.exe'
        if installed.exists():bash=str(installed)
    assert java and bash,'JDK 25 and Bash are required'
    env=os.environ.copy()
    for key in ['JDK_JAVA_OPTIONS','JAVA_TOOL_OPTIONS','_JAVA_OPTIONS','CLASSPATH','BASH_ENV']:
        env.pop(key,None)
    env['MQ3_PROTOTYPE_JAVA']=java.replace('\\','/')
    version=subprocess.run([java,'--version'],capture_output=True,text=True,encoding='utf-8',env=env,timeout=10,check=True).stdout
    assert '25.' in version or '25 ' in version,version
    scenarios=[]
    for words in [('Hello','World'),('Red','Green')]:
        def variant(text):return text.replace('Hello',words[0]).replace('World',words[1])
        with tempfile.TemporaryDirectory(prefix='mq-java-arguments-prototype-') as directory:
            work=Path(directory);source=variant(prototype['source_files']['Main.java'])
            (work/'Main.java').write_text(source,encoding='utf-8',newline='\n')
            checks=[]
            for step,task in zip(steps,prototype['steps']):
                assert variant(task['source_before'])==source
                after=variant(task['source_after'])
                assert sum(a!=b for a,b in zip(source.splitlines(),after.splitlines()))<=1
                assert len(step['complexity']['new_concepts'])<=1
                (work/'Main.java').write_text(after,encoding='utf-8',newline='\n');source=after
                # Bash must split/strip quotes, rather than Python shlex pretending
                # to be the platform's shell. No user or course directories are used.
                function='java() { "$MQ3_PROTOTYPE_JAVA" -Xmx128m -Dfile.encoding=UTF-8 -Dstdout.encoding=UTF-8 -Dstderr.encoding=UTF-8 "$@"; }\n'
                result=subprocess.run([bash,'--noprofile','--norc','-c',function+variant(task['command'])],cwd=work,env=env,text=True,encoding='utf-8',capture_output=True,timeout=20)
                assert result.returncode==0,(task['title'],result.stderr)
                assert result.stdout==variant(task['stdout']),(task['title'],result.stdout)
                assert not (work/'Main.class').exists(),'source execution must not leave a class artifact'
                assert (work/'Main.java').read_text(encoding='utf-8')==source
                checks.append({'step_id':task['id'],'command':variant(task['command']),'stdout':result.stdout})
            scenarios.append({'words':words,'checks':checks})
    return {'passed':True,'lesson_id':prd['id'],'steps':len(steps),'scenarios':scenarios,'jdk':version,'prd_sha256':content_hash(prd),'external_services':0}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'target/java-arguments-prototype/evidence.json')
    args=parser.parse_args()
    try:result=verify()
    except Exception as error:result={'passed':False,'error':str(error)}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if not result['passed']:raise SystemExit(result['error'])
    print(f"Verified {result['steps']} independent steps × {len(result['scenarios'])} word scenarios; real Bash/JDK, no external services.")
if __name__=='__main__':main()
