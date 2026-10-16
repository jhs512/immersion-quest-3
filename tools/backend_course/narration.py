"""Compile small edits into executable walkthroughs, cached by complete task content."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
from .common import ROOT
CACHE=ROOT/'tools/backend_course/narration_cache'

def patch(before,after,say=None):
    return dict(action='patch_code',before=before,after=after,**(dict(say=say) if say else {}))

def reading():
    return dict(action='say',target='output',text='실행 결과를 읽어보세요. 아직 남은 검사와 통과한 검사를 비교해요.')

def java_stages(task):
    source=task['solution']
    with tempfile.TemporaryDirectory() as temp:
        file=Path(temp)/task['entry_file'];file.write_text(source,encoding='utf8',newline='\n')
        executable=str(Path(os.environ['JAVA_HOME'])/'bin/java.exe') if os.environ.get('JAVA_HOME') else 'java'
        result=subprocess.run([executable,str(ROOT/'tools/backend_course/MethodBodies.java'),str(file)],capture_output=True,text=True,encoding='utf8',check=True)
    bounds=[tuple(map(int,line.split(':'))) for line in result.stdout.splitlines()]
    assert bounds,task['id']
    current=source
    for index,(start,end) in reversed(list(enumerate(bounds))):
        current=current[:start]+'{'+f'/*mq3-step-{index}*/throw new UnsupportedOperationException("아직 구현 전이에요");'+'}'+current[end:]
    actions=[dict(action='set_code',code=current,say='선언과 생성자를 먼저 준비했어요. 메서드는 하나씩 채울게요.'),dict(action='run',expected_failure=True),dict(action='say',target='output',text='아직 구현하지 않은 메서드가 있어요. 지금 실패하는 위치를 확인하세요.')]
    for index,(start,end) in enumerate(bounds):
        marker=f'/*mq3-step-{index}*/throw new UnsupportedOperationException("아직 구현 전이에요");'
        lines=source[start+1:end-1].splitlines(keepends=True)
        for offset in range(0,len(lines),3):
            actions.append(patch(marker,''.join(lines[offset:offset+3])+marker,'작은 조각을 채워요. 앞뒤의 변수와 조건을 함께 확인하세요.' if offset==0 else None))
        actions.append(patch(marker,''))
        actions.extend([dict(action='run',expected_failure=index<len(bounds)-1),reading()])
    return actions

def browser_stages(task):
    source=task['solution']
    if task['entry_file'].endswith('.jsx'):
        last=source.splitlines(keepends=True)[-1];scaffold=source[:-len(last)]
        actions=[dict(action='set_code',code=scaffold,say='컴포넌트 함수를 먼저 준비해요. 아직 화면에 연결하지 않았어요.'),dict(action='run'),dict(action='say',target='output',text='화면은 아직 비어 있어요. 이제 루트에 컴포넌트를 연결해요.'),patch(scaffold,source)]
    else:
        start=source.index('<body>')+len('<body>');end=source.rindex('</body>');marker='<!-- mq3-build-here -->'
        scaffold=source[:start]+marker+source[end:]
        actions=[dict(action='set_code',code=scaffold,say='문서와 스타일을 먼저 준비해요. 본문은 작은 조각으로 채워요.'),dict(action='run'),dict(action='say',target='output',text='본문이 비어 있는 화면이에요. 요소와 이벤트를 차례로 넣어요.')]
        lines=source[start:end].splitlines(keepends=True)
        for offset in range(0,len(lines),3):actions.append(patch(marker,''.join(lines[offset:offset+3])+marker))
        actions.append(patch(marker,''))
    return actions+[dict(action='run'),dict(action='say',target='output',text='완성한 화면을 확인하세요. 입력과 버튼도 직접 사용해보세요.')]

def compile_task(task):
    if task['narration']:return
    if task['language'] in ('junit','java_project'):actions=java_stages(task)
    elif task['language']=='web':actions=browser_stages(task)
    elif task['language']=='git':
        stage="set -e\ngit init -b main work\ngit -C work status --short\n"
        actions=[dict(action='set_code',code=stage,say='먼저 빈 저장소를 만들고 상태를 확인해요.'),dict(action='run'),dict(action='say',target='output',text='저장소 초기화 결과를 확인하세요. 아직 커밋한 파일은 없어요.'),dict(action='set_code',code=task['solution'],say='이제 파일을 저장하고 커밋을 남겨요.'),dict(action='run'),reading()]
    else:
        stage="const fs=require('node:fs');\nconst rows=JSON.parse(fs.readFileSync(0,'utf8'));\nconsole.log(JSON.stringify(rows));\n"
        actions=[dict(action='set_code',code=stage,say='먼저 입력이 배열로 읽히는지 확인해요.'),dict(action='run'),dict(action='say',target='output',text='변환 전의 배열이 보여요. 이제 필요한 값만 골라요.'),dict(action='set_code',code=task['solution']),dict(action='run'),reading()]
    task['narration']=[dict(action='say',target='problem',text=task['goal']),dict(action='say',target='editor',text='조심하세요. 실행 성공과 모든 검사 통과는 달라요. 단계마다 결과를 확인해요.')]+actions

def cache_task(lesson_id,task):
    CACHE.mkdir(exist_ok=True)
    digest=hashlib.sha256(('compiler-2\n'+json.dumps({k:v for k,v in task.items() if k not in ('narration','source_hash')},ensure_ascii=False,sort_keys=True)).encode()).hexdigest()
    path=CACHE/f"{lesson_id}--{task['id']}.json"
    if path.is_file():
        saved=json.loads(path.read_text(encoding='utf8'))
        if saved['hash']==digest:
            task['narration']=saved['actions'];return digest
    compile_task(task)
    path.write_text(json.dumps(dict(hash=digest,by='hand-compiled',actions=task['narration']),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return digest
