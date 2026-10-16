"""WebView2 UI regression probe; requires Python websockets.

Create target/navigation-course.json from the current KPC course, with a
unique course id and the first two units. Launch the debug app with that
MOLIP_COURSE_PATH and remote-debugging-port=9227. This clears the first unit;
do not run against student progress. Tests Markdown colors, correct-answer
popups, CodeMirror, mission navigation and navigation between units.
"""
import asyncio,json,urllib.request
from pathlib import Path
import websockets

async def main():
 course=json.loads(Path('target/navigation-course.json').read_text(encoding='utf-8'))
 solutions=json.loads(Path('courses/kpc-solutions.json').read_text(encoding='utf-8'))
 target=json.load(urllib.request.urlopen('http://localhost:9227/json/list'))[0]
 async with websockets.connect(target['webSocketDebuggerUrl']) as ws:
  sequence=0
  async def js(expression):
   nonlocal sequence
   sequence+=1
   await ws.send(json.dumps({'id':sequence,'method':'Runtime.evaluate','params':{'expression':expression,'returnByValue':True}}))
   while True:
    response=json.loads(await ws.recv())
    if response.get('id')==sequence:
     result=response['result']
     if 'exceptionDetails' in result:raise RuntimeError(result['exceptionDetails'])
     return result['result'].get('value')
  async def browser_input(method,params):
   nonlocal sequence
   sequence+=1
   await ws.send(json.dumps({'id':sequence,'method':method,'params':params}))
   while True:
    response=json.loads(await ws.recv())
    if response.get('id')==sequence:return response
  async def click(text):
   await js('Array.from(document.querySelectorAll("button")).find(b=>b.textContent.trim()=='+json.dumps(text)+')?.click()')
   await asyncio.sleep(.2)
  async def expect(expression,label):
   assert await js(expression),label
   print('PASS',label)
  async def wait_popup():
   for _ in range(100):
    if await js("!!document.querySelector('[aria-label=\"정답 확인\"]')"):return
    await asyncio.sleep(.1)
   raise AssertionError('correct-answer popup missing')
  await click('학습 시작 · 이어하기')
  await expect("Array.from(document.querySelectorAll('button')).find(b=>b.textContent.trim()==='다음 →').disabled",'next locked before correct answer')
  await expect("!!document.querySelector('.markdown code.language-python .tok-string')",'Markdown Python syntax colors')
  await expect("!!document.querySelector('.markdown blockquote strong')",'Markdown emphasis and callout')
  await expect("document.querySelector('.curriculum-menu .unit.selected').getAttribute('aria-current')==='step'",'current unit marked on initial open')
  await js("document.querySelector('.curriculum-toggle').click()")
  await asyncio.sleep(.2)
  await expect("document.querySelector('.curriculum-menu').open",'curriculum opens')
  await expect("(()=>{const r=document.querySelector('.curriculum-menu').getBoundingClientRect();return r.width>700 && Math.abs(r.x+r.width/2-document.documentElement.clientWidth/2)<3 && Math.abs(r.y+r.height/2-innerHeight/2)<3})()",'curriculum is a large centered dialog')
  await expect("document.querySelector('.curriculum-overall').textContent.includes('0%') && document.querySelector('.unit-progress').textContent.includes('0%')",'overall and unit percentages start at zero')
  await js("document.querySelector('.curriculum-modal-header h2').click()")
  await expect("document.querySelector('.curriculum-menu').open",'click inside keeps curriculum open')
  await browser_input('Input.dispatchMouseEvent',{'type':'mousePressed','x':5,'y':5,'button':'left','clickCount':1})
  await browser_input('Input.dispatchMouseEvent',{'type':'mouseReleased','x':5,'y':5,'button':'left','clickCount':1})
  await asyncio.sleep(.15)
  await expect("!document.querySelector('.curriculum-menu').open",'outside click dismisses curriculum')
  await js("document.querySelector('.curriculum-toggle').click()")
  await browser_input('Input.dispatchKeyEvent',{'type':'keyDown','key':'Escape','code':'Escape','windowsVirtualKeyCode':27})
  await browser_input('Input.dispatchKeyEvent',{'type':'keyUp','key':'Escape','code':'Escape','windowsVirtualKeyCode':27})
  await asyncio.sleep(.15)
  await expect("!document.querySelector('.curriculum-menu').open",'Escape dismisses curriculum')
  await js("document.querySelector('.curriculum-toggle').click()")
  await expect("document.querySelector('.curriculum-menu .unit.selected .unit-current').textContent==='학습 중'",'current unit has visible badge')
  await js("document.querySelector('.curriculum-menu .unit.selected').click()")
  await asyncio.sleep(.2)
  await expect("!document.querySelector('.curriculum-menu').open",'selecting current unit closes curriculum')
  await expect("!document.querySelector('.mission-tabs') && !document.querySelector('.mission-controls')",'old inline mission navigation removed')
  await expect("document.querySelector('.header-navigation').closest('header')!==null",'previous and next live in the top header')
  await expect("document.querySelectorAll('.curriculum-missions button').length==="+str(len(course['chapters'][0]['units'][0]['activities'])),'unit missions integrated into curriculum')
  await expect("document.querySelectorAll('.curriculum-missions button')[1].disabled",'future curriculum mission remains locked')
  activities=course['chapters'][0]['units'][0]['activities']
  for index,activity in enumerate(activities):
   kind=activity['kind']
   if kind in ['concept','quiz']:
    questions=[activity['check']] if kind=='concept' else activity['questions']
    for q in questions:
     if q['type']=='short_answer':
      answer=q['accepted'][0]
      await js('(()=>{const input=Array.from(document.querySelectorAll("input")).find(e=>e.getAttribute("aria-label")=='+json.dumps(q['prompt'])+');input.value='+json.dumps(answer)+';input.dispatchEvent(new InputEvent("input",{bubbles:true,data:'+json.dumps(answer)+'}));})()')
     else:
      await js('document.querySelector("input[name=\\"'+q['id']+'\\"][value=\\"'+str(q['correct'])+'\\"]").click()')
     await asyncio.sleep(.1)
    await click('제출')
   else:
    await expect("!!document.querySelector('.cm-editor .cm-content')",'CodeMirror content mounted')
    source=solutions[activity['problem']['id']]
    if index==1:
     await js('(()=>{const view=document.querySelector(".cm-content").cmTile.root.view;view.dispatch({changes:{from:0,to:view.state.doc.length,insert:'+json.dumps("print('wrong')\n")+'}});})()')
     await asyncio.sleep(.2)
     await click('제출')
     for _ in range(100):
      if not await js("Array.from(document.querySelectorAll('button')).find(b=>b.textContent.trim()==='제출').disabled"):break
      await asyncio.sleep(.1)
     await expect("!document.querySelector('[aria-label=\"정답 확인\"]')",'wrong submission has no success popup')
     await expect('document.querySelectorAll(".curriculum-missions button")['+str(index)+'].classList.contains("selected")','wrong submission stays on mission')
    await js('(()=>{const view=document.querySelector(".cm-content").cmTile.root.view;view.dispatch({changes:{from:0,to:view.state.doc.length,insert:'+json.dumps(source)+'}});})()')
    await asyncio.sleep(.2)
    await expect('document.querySelector(".cm-content").textContent.includes('+json.dumps(source.splitlines()[0])+')','CodeMirror synchronized with code')
    if activity['problem'].get('tests') and activity['problem']['tests'][0]['input']:
     sample=activity['problem']['tests'][0]
     await expect('Array.from(document.querySelectorAll("textarea")).find(e=>e.getAttribute("aria-label")==="실행 입력").value==='+json.dumps(sample['input']),'sample input prefilled')
     await expect('Array.from(document.querySelectorAll("textarea")).find(e=>e.getAttribute("aria-label")==="실행 입력").closest("details").open','run input visible')
     await click('코드 실행')
     for _ in range(100):
      if not await js("Array.from(document.querySelectorAll('button')).find(b=>b.textContent.trim()==='코드 실행').disabled"):break
      await asyncio.sleep(.1)
     await expect('document.querySelector(".output").textContent.includes('+json.dumps(sample['expected'].strip())+')','run succeeds with sample input')
     await expect('document.querySelectorAll(".curriculum-missions button")['+str(index)+'].classList.contains("selected")','run does not submit')
    await click('제출')
   await wait_popup()
   await expect("document.querySelector('[aria-label=\"정답 확인\"]').textContent.includes('정답입니다!')",'correct-answer popup')
   await click('확인')
   if index+1<len(activities):
    await expect('document.querySelectorAll(".curriculum-missions button")['+str(index+1)+'].classList.contains("selected")','correct submission automatically advances')
   if index==0:
    await expect("document.querySelector('.unit-progress').textContent.includes('20%')",'unit percentage reflects partial mission completion')
    await expect("!!document.querySelector('.cm-editor .cm-content')",'submission opens coding editor')
    await click('← 이전')
    await expect("!!document.querySelector('.concept-flow')",'previous returns to concept')
    await click('다음 →')
  await expect('document.querySelector(".mission-heading strong").textContent.includes('+json.dumps(course['chapters'][0]['units'][1]['title'])+')','next crosses unit boundary')
  await js("document.querySelector('.curriculum-toggle').click()")
  await asyncio.sleep(.2)
  await js("document.querySelector('.curriculum-menu .unit').click()")
  await asyncio.sleep(.2)
  await expect("!document.querySelector('.curriculum-menu').open",'selecting completed unit closes curriculum')
  await expect('document.querySelector(".curriculum-menu .unit.selected").textContent.includes('+json.dumps(course['chapters'][0]['units'][0]['title'])+')','selected unit highlight follows navigation')

  await js("document.querySelector('.curriculum-toggle').click()")
  await asyncio.sleep(.1)
  await js("document.querySelectorAll('.curriculum-missions button')[1].click()")
  await asyncio.sleep(.2)
  await expect("!document.querySelector('.curriculum-menu').open",'mission selection closes curriculum')
  await expect("document.querySelectorAll('.curriculum-missions button')[1].getAttribute('aria-current')==='step' && !!document.querySelector('.cm-editor')",'curriculum mission selection updates current highlight and content')
  await expect("document.querySelector('.unit-progress').textContent.includes('100%')",'completed unit shows 100 percent')
  print('ALL UI FLOW CHECKS PASSED')

asyncio.run(main())
