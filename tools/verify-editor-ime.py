"""Editor/WebView2 regression probe (Python websockets required).

Launch a fresh KPC fixture with just one coding activity and a unique course
id via MOLIP_COURSE_PATH, with remote-debugging-port=9227. The probe writes,
runs and resets the fixture code. Do not run against student progress.
Reproduces stale backend echoes through actual CodeMirror transactions and
checks Korean text, execution, draft restoration and explicit reset.
This is a synchronization test, not Windows hardware IME keyboard automation.
"""
import asyncio,json,urllib.request,websockets
async def main():
 target=json.load(urllib.request.urlopen('http://localhost:9227/json/list'))[0]
 async with websockets.connect(target['webSocketDebuggerUrl']) as ws:
  seq=0
  async def js(expression):
   nonlocal seq
   seq+=1;await ws.send(json.dumps({'id':seq,'method':'Runtime.evaluate','params':{'expression':expression,'returnByValue':True}}))
   while True:
    r=json.loads(await ws.recv())
    if r.get('id')==seq:
     if 'exceptionDetails' in r['result']:raise RuntimeError(r['result']['exceptionDetails'])
     return r['result']['result'].get('value')
  await js("Array.from(document.querySelectorAll('button')).find(b=>b.textContent.includes('학습 시작'))?.click()")
  await asyncio.sleep(.3)
  for source in ['print("안', 'print("안녕', 'print("안녕하', 'print("안녕하세', 'print("안녕하세요.")\n']:
   encoded=json.dumps(source)
   result=await js("(()=>{const view=document.querySelector('.cm-content').cmTile.root.view;const bridge=document.querySelector('textarea[data-code-editor]');const old=bridge.getAttribute('data-editor-value');view.dispatch({changes:{from:0,to:view.state.doc.length,insert:"+encoded+"}});bridge.setAttribute('data-editor-value',old);window.molipCodeEditors.sync();return view.state.doc.toString()})()")
   assert result==source, 'A delayed backend echo overwrote the Korean editor update'
   await asyncio.sleep(.08)
  expected='print("안녕하세요.")\n'
  await asyncio.sleep(.25)
  assert await js("document.querySelector('.cm-content').cmTile.root.view.state.doc.toString()")==expected
  print('PASS: staged Korean edits survive stale backend echoes')
  await js("Array.from(document.querySelectorAll('button')).find(b=>b.textContent.trim()==='코드 실행').click()")
  for _ in range(100):
   output=await js("document.querySelector('.output').textContent")
   if '안녕하세요.' in output:break
   await asyncio.sleep(.1)
  assert '안녕하세요.' in output and '실행 완료' in output
  print('PASS: exact Korean source runs through Python')
  await js("Array.from(document.querySelectorAll('button')).find(b=>b.textContent.includes('← 클래스룸')).click()")
  await asyncio.sleep(.2)
  await js("Array.from(document.querySelectorAll('button')).find(b=>b.textContent.includes('학습 시작')).click()")
  await asyncio.sleep(.2)
  assert await js("document.querySelector('.cm-content').cmTile.root.view.state.doc.toString()")==expected
  print('PASS: editor draft survives remount')
  await js("Array.from(document.querySelectorAll('button')).find(b=>b.textContent.trim()==='초기화').click()")
  await asyncio.sleep(.2)
  assert '안녕하세요' not in await js("document.querySelector('.cm-content').cmTile.root.view.state.doc.toString()")
  print('PASS: explicit code reset still works')

asyncio.run(main())

