"""Execute every source stage and every grading case in the split Java lessons."""
import json,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
count=0
for key in ['java-regex','java-rq','java-calculator']:
 lesson=json.loads((ROOT/f'courses/redesigned/{key}.json').read_text(encoding='utf8'))
 cases=json.loads((ROOT/f'tests/lesson-cases/{key}.json').read_text(encoding='utf8'))
 for n,task in enumerate(lesson['tasks']):
  code=task.get('example_code') or task['starter_code'];runs=[]
  with tempfile.TemporaryDirectory(prefix='mq-split-java-') as d:
   folder=Path(d)
   def compile(source):
    (folder/'Main.java').write_text(source,encoding='utf8')
    r=subprocess.run(['javac','-encoding','UTF-8','-d',d,str(folder/'Main.java')],capture_output=True,text=True,encoding='utf8')
    assert r.returncode==0,(key,n+1,r.stderr)
   def execute(input=''):
    r=subprocess.run(['java','-cp',d,'Main'],input=input,capture_output=True,text=True,encoding='utf8',timeout=10)
    assert r.returncode==0,(key,n+1,r.stderr)
    return r.stdout.rstrip('\r\n')
   for action in task['narration']:
    if action['action']=='patch_code':
     assert code.count(action['before'])==1;code=code.replace(action['before'],action['after'],1)
    elif action['action']=='run':
     compile(code);runs.append(execute(task['tests'][0]['input'] if task['tests'] else ''));count+=1
   assert runs==cases['expected_outputs'][n],(key,n+1,runs,cases['expected_outputs'][n])
   if task.get('interaction') is None:
    assert code==task['solution'],(key,n+1,'teacher final code differs')
    compile(task['solution'])
    for case in task['tests']:
     actual=execute(case['input']);assert actual==case['expected'].rstrip('\r\n'),(key,n+1,case,actual);count+=1
  print(f'{key} {n+1}: source stages and grading passed',flush=True)
print(f'PASS: {count} real Java executions')
