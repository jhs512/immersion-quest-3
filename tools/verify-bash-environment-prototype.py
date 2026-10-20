"""Verify environment scope in one real Bash, and expose the fresh-shell counterexample."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'tools/redesigned_lessons/bash_environment/prototype.json'

def verify():
    draft=json.loads(SOURCE.read_text(encoding='utf-8'))
    assert draft['status']=='prototype_only_not_registered'
    bash=shutil.which('bash')
    if os.name=='nt':
        installed=Path(os.environ.get('ProgramFiles','C:/Program Files'))/'Git/bin/bash.exe'
        if installed.exists():bash=str(installed)
    assert bash,'Bash is required'
    env=os.environ.copy()
    for key in ['MQ_LABEL','BASH_ENV','ENV']:env.pop(key,None)
    env['PATH']=str(Path(bash).parent)+os.pathsep+env.get('PATH','')
    results=[]
    for words in [('Blue','Green'),('Amber','Purple')]:
        def variant(s):return s.replace('Blue',words[0]).replace('Green',words[1])
        with tempfile.TemporaryDirectory(prefix='mq-environment-prototype-') as directory:
            work=Path(directory)
            for name,source in draft['source_files'].items():
                (work/name).write_text(variant(source),encoding='utf-8',newline='\n')
            script='set -e\n';expected='';checks=[]
            for i,step in enumerate(draft['steps']):
                for j,action in enumerate(step['commands']):
                    marker=f'__MQ_PROBE_{i}_{j}__'
                    script+=f"printf '%s\\n' {marker}\n"+variant(action['command'])+'\n'
                    expected+=marker+'\n'+variant(action['stdout'])
                    checks.append({'title':step['title'],'command':variant(action['command']),'stdout':variant(action['stdout'])})
            run=subprocess.run([bash,'--noprofile','--norc','-c',script],cwd=work,env=env,text=True,encoding='utf-8',capture_output=True,timeout=15)
            assert run.returncode==0,run.stderr
            assert run.stdout==expected,(run.stdout,expected)
            # The current UI destroys the PTY at a step change. Reopening a shell
            # cannot silently recreate the non-exported variable from step one.
            fresh=subprocess.run([bash,'--noprofile','--norc','-c','export MQ_LABEL\nbash show-env.sh'],cwd=work,env=env,text=True,encoding='utf-8',capture_output=True,timeout=10,check=True)
            assert fresh.stdout=='<unset>\n'
            results.append({'words':words,'checks':checks,'fresh_shell_stdout':fresh.stdout})
    return {'passed':True,'steps':len(draft['steps']),'scenarios':results,'registered':False,'requires_continuous_shell':True}

if __name__=='__main__':
    result=verify();output=ROOT/'target/bash-environment-prototype/evidence.json'
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Verified 8 steps × 2 scenarios in a real persistent Bash; fresh-shell counterexample confirmed. Not registered.')
