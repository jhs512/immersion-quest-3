"""Small original experiments, explicit transfer challenges, and real execution narration."""
import difflib
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import textwrap

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'target/principles-expansion'
def _managed_python():
    # Same order as the player: explicit override, then the managed venv (Windows layout first).
    if os.environ.get('MOLIP_PYTHON'):return Path(os.environ['MOLIP_PYTHON'])
    env=Path(os.environ.get('LOCALAPPDATA',''))/'MolipQuest/MolipQuest/data/ml-env'
    for candidate in [env/'Scripts/python.exe',env/'python.exe',env/'bin/python']:
        if candidate.is_file():return candidate
    return env/'Scripts/python.exe'
PYTHON=_managed_python()
JAVA=str(Path(os.environ['JAVA_HOME'])/'bin/java.exe') if os.environ.get('JAVA_HOME') else 'java'
LESSONS=[]
# The same TinyCC the player prepares (src/lesson_runner.rs), in the same app data folder.
TCC_URL='https://download.savannah.gnu.org/releases/tinycc/tcc-0.9.27-win64-bin.zip'
TCC_SHA256='34a721949a2583fdff725312da092fa0f5f1f284b702e6f811c6954714faabb2'

def c_compiler():
    """Windows: tcc.exe (downloaded once, hash checked). Elsewhere: cc. MOLIP_TCC overrides."""
    if os.environ.get('MOLIP_TCC'):return os.environ['MOLIP_TCC']
    if os.name!='nt':return os.environ.get('MOLIP_CC','cc')
    root=Path(os.environ['LOCALAPPDATA'])/'MolipQuest/MolipQuest/data/course-tools'
    exe=root/'tcc-0.9.27/tcc/tcc.exe'
    if exe.is_file():return str(exe)
    import urllib.request,zipfile,io,shutil
    raw=urllib.request.urlopen(TCC_URL,timeout=60).read()
    assert hashlib.sha256(raw).hexdigest()==TCC_SHA256,'TinyCC download hash mismatch'
    pending=root/f'tcc-0.9.27.{os.getpid()}.tmp'
    zipfile.ZipFile(io.BytesIO(raw)).extractall(pending)
    try:pending.rename(root/'tcc-0.9.27')
    except OSError:shutil.rmtree(pending,ignore_errors=True)
    assert exe.is_file(),'TinyCC was not prepared'
    return str(exe)

def code(value):
    return textwrap.dedent(value).strip()+'\n'

def task(id,title,principle,goal,starter,before,after,*,language='java_project',files=None,tests=None,checks=None,git=None,challenge=False,hints=None,caution='실행 성공과 모든 검사 통과는 달라요.'):
    starter=code(starter)
    assert starter.count(before)==1,(id,before)
    solution=starter.replace(before,after,1)
    changed=sum(len([line for line in group if line.strip()]) for tag,a,b,c,d in difflib.SequenceMatcher(None,starter.splitlines(),solution.splitlines()).get_opcodes() if tag!='equal' for group in [solution.splitlines()[c:d]])
    assert changed<=5,(id,'too much typing',changed)
    entry={'java_project':'Exercise.java','java':'Main.java','git':'practice.sh','web':'index.html','python':'main.py','junit':'ExerciseTest.java','c':'main.c'}.get(language,'main.js')
    return dict(id=id,title=title,goal=principle+'\n\n'+goal,language=language,entry_file=entry,
        starter_code=starter,solution=solution,files=files or {},tests=[dict(input=i,expected=str(e)) for i,e in (tests or [])],
        web_checks=checks or [],git_checks=git,required=not challenge,hints=hints or [],narration=[],
        _edit=dict(before=before,after=after),_caution=caution)

def java(id,title,principle,goal,signature,body,before,after,call,tests,**kw):
    source='class Exercise {\n    // 값이 바뀌는 줄을 실행 결과와 비교해요.\n    '+signature+' {\n'+textwrap.indent(code(body),'        ')+'    }\n}\n'
    main='import java.util.*;\nclass Main {\n    public static void main(String[] args) throws Exception {\n        Scanner in=new Scanner(System.in);\n        System.out.println('+call+');\n    }\n}\n'
    return task(id,title,principle,goal,source,before,after,files={'Main.java':main},tests=tests,**kw)

def python(id,title,principle,goal,starter,before,after,tests,**kw):
    return task(id,title,principle,goal,starter,before,after,language='python',tests=tests,**kw)

def lesson(id,title,description,sources,tasks):
    result=dict(schema_version=1,id=id,revision='v1.0.0',title=title,description=description,
        sources=sources,sections=[],review_enabled=False,tasks=tasks)
    LESSONS.append(result)
    return result

def execute(t,source,input='',checking=False):
    with tempfile.TemporaryDirectory() as temp:
        folder=Path(temp)
        for name,body in t['files'].items():
            file=folder/name;file.parent.mkdir(parents=True,exist_ok=True);file.write_text(body,encoding='utf8',newline='\n')
        (folder/t['entry_file']).write_text(source,encoding='utf8',newline='\n')
        env=os.environ.copy()
        env.update(PYTHONUTF8='1',MPLBACKEND='Agg',TF_CPP_MIN_LOG_LEVEL='3',TF_ENABLE_ONEDNN_OPTS='0')
        if t['language'] in ('java','java_project'):
            cmd=[JAVA,'-Dfile.encoding=UTF-8','-Dstdout.encoding=UTF-8','-Dstderr.encoding=UTF-8','--source','25','Main.java']
        elif t['language']=='python': cmd=[str(PYTHON),'-X','utf8','main.py']
        elif t['language']=='c':
            if os.name=='nt':cmd=[c_compiler(),'-run','main.c']
            else:
                compiled=subprocess.run([c_compiler(),'-std=c11','-o','main','main.c'],cwd=temp,capture_output=True,text=True,encoding='utf8',errors='replace')
                if compiled.returncode:return compiled
                cmd=['./main']
        elif t['language']=='git':
            subprocess.run(['git','init','--bare','-q','remote.git'],cwd=temp,check=True,capture_output=True)
            env.update(GIT_CONFIG_GLOBAL='NUL' if os.name=='nt' else '/dev/null',GIT_AUTHOR_NAME='Learner',GIT_AUTHOR_EMAIL='learner@example.invalid',GIT_COMMITTER_NAME='Learner',GIT_COMMITTER_EMAIL='learner@example.invalid')
            cmd=['C:/Program Files/Git/bin/bash.exe' if os.name=='nt' else 'bash','practice.sh']
        elif t['language']=='junit':
            jars=Path(os.environ['LOCALAPPDATA'])/'MolipQuest/MolipQuest/data/course-tools'
            cp=os.pathsep.join(str(p) for p in jars.glob('*.jar'))
            compiled=subprocess.run(['javac','-encoding','UTF-8','-cp',cp,*[p.name for p in folder.glob('*.java')]],cwd=temp,capture_output=True,text=True,encoding='utf8',errors='replace')
            if compiled.returncode:return compiled
            cmd=[JAVA,'-jar',str(jars/'junit-platform-console-standalone-1.13.4.jar'),'execute','--disable-banner','--class-path',temp+os.pathsep+cp,'--scan-class-path','--details','summary']
        elif t['language']=='web':
            (folder/'web-runner.cjs').write_bytes((ROOT/'assets/web-runner.cjs').read_bytes())
            (folder/'request.json').write_text(json.dumps(dict(entry=t['entry_file'],checks=t['web_checks'] if checking else [])),encoding='utf8')
            env['MQ3_PLAYWRIGHT']=str(ROOT/'target/ui-tests/node_modules/playwright-core')
            cmd=['node','web-runner.cjs']
        else:cmd=['node','main.js']
        return subprocess.run(cmd,cwd=temp,input=input,capture_output=True,text=True,encoding='utf8',errors='replace',timeout=65,env=env)

def compile_narration(lesson,t):
    cache=ROOT/'tools/principles_course/narration_cache'/f"{lesson['id']}--{t['id']}.json"
    fingerprint=hashlib.sha256(('experiment-1\n'+json.dumps(t,ensure_ascii=False,sort_keys=True)).encode()).hexdigest()
    if cache.exists() and json.loads(cache.read_text(encoding='utf8'))['hash']==fingerprint:
        t['narration']=json.loads(cache.read_text(encoding='utf8'))['actions']
    else:
        sample=t['tests'][0]['input'] if t['tests'] else ''
        initial=execute(t,t['starter_code'],sample)
        final=execute(t,t['solution'],sample)
        assert final.returncode==0,(lesson['id'],t['id'],final.stderr[-1200:])
        if t['language']=='web':
            graded=execute(t,t['solution'],sample,checking=True)
            assert graded.returncode==0,(lesson['id'],t['id'],graded.stderr[-1200:])
        if t['language'] not in ('web','junit','git'):
            assert final.stdout.strip()==t['tests'][0]['expected'],(t['id'],final.stdout,t['tests'][0])
        def reading(result):
            if result.returncode:return '지금 코드는 검사를 통과하지 못해요.'
            if t['language']=='web':return '화면에서 바뀐 동작을 직접 확인해요.'
            if t['language']=='junit':return '테스트가 통과했어요. 확인한 조건을 읽어봐요.'
            line=result.stdout.strip().splitlines()
            visible=' / '.join(line)[-32:] if line else '출력이 없어요'
            return '실행 결과를 비교해요. '+visible
        t['narration']=[dict(action='set_code',code=t['starter_code'],say='준비 코드를 먼저 실행해 볼게요.'),
            dict(action='run',expected_failure=initial.returncode!=0),dict(action='say',target='output',text=reading(initial)),
            dict(action='say',target='editor',text='조심하세요. '+t['_caution']),
            dict(action='patch_code',**t['_edit'],say='작은 부분을 바꿔 원리를 확인해요.'),
            dict(action='run'),dict(action='say',target='output',text=reading(final)),dict(action='submit')]
        cache.write_text(json.dumps(dict(hash=fingerprint,actions=t['narration']),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    t.pop('_edit');t.pop('_caution')

def emit():
    OUT.mkdir(exist_ok=True,parents=True)
    for l in LESSONS:
        for t in l['tasks']:compile_narration(l,t)
        folder=OUT/l['id'];folder.mkdir(exist_ok=True)
        (folder/'lesson.json').write_text(json.dumps(l,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
        print(f"BUILT {l['id']}: {len(l['tasks'])} exercises",flush=True)
