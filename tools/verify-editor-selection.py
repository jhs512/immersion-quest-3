"""WebView2 pixel regression for CodeMirror selected text.

Requires Python websockets/Pillow and an isolated coding-only course fixture
launched with remote-debugging-port=9227. Writes fixture code; never run
against student progress. Screenshot artifacts are saved under target/.
"""
import asyncio,json,urllib.request,base64,io
from pathlib import Path
import websockets
from PIL import Image,ImageChops
async def main():
 target=json.load(urllib.request.urlopen('http://localhost:9227/json/list'))[0]
 async with websockets.connect(target['webSocketDebuggerUrl']) as ws:
  seq=0
  async def call(method,params):
   nonlocal seq
   seq+=1;await ws.send(json.dumps(dict(id=seq,method=method,params=params)))
   while True:
    r=json.loads(await ws.recv())
    if r.get('id')==seq:return r['result']
  async def js(expr):
   r=await call('Runtime.evaluate',dict(expression=expr,returnByValue=True))
   if 'exceptionDetails' in r:raise RuntimeError(r['exceptionDetails'])
   return r['result'].get('value')
  await js("Array.from(document.querySelectorAll('button')).find(b=>b.textContent.includes('학습 시작'))?.click()")
  await asyncio.sleep(.4)
  await js("window.probeView=document.querySelector('.cm-content').cmTile.root.view;probeView.dispatch({changes:{from:0,to:probeView.state.doc.length,insert:'price = 10000\\nquantity = 3\\namount = price * quantity'},selection:{anchor:28}});probeView.focus()")
  await asyncio.sleep(.2)
  async def shot():
   r=await call('Page.captureScreenshot',dict(format='png'))
   return Image.open(io.BytesIO(base64.b64decode(r['data']))).convert('RGB')
  before=await shot()
  await js("(()=>{const start=probeView.state.doc.line(3).from;probeView.dispatch({selection:{anchor:start,head:start+10}})})()")
  await asyncio.sleep(.2)
  details=await js("(()=>{const e=document.querySelector('.cm-selectionBackground');const r=e.getBoundingClientRect();return {range:probeView.state.selection.main.toJSON(),color:getComputedStyle(e).backgroundColor,rect:{x:r.x,y:r.y,width:r.width,height:r.height},lineColor:getComputedStyle(document.querySelector('.cm-activeLine')).backgroundColor}})()")
  after=await shot();r=details['rect']
  box=(int(r['x'])+2,int(r['y'])+2,int(r['x']+r['width'])-2,int(r['y']+r['height'])-2)
  delta=ImageChops.difference(before.crop(box),after.crop(box))
  changed=sum(1 for p in delta.get_flattened_data() if max(p)>20)
  print(json.dumps(details));print('Selection pixels visibly changed:',changed)
  after.save('target/selection-probe.png')
  assert changed>100,'Selected text has no visible background highlight'
  print('PASS: third-line first ten characters visibly highlighted')
asyncio.run(main())
