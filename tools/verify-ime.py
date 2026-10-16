"""WebView2 composition regression probe; requires Python websockets.

Launch a fresh KPC fixture with a unique course id, using MOLIP_COURSE_PATH
and WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS=--remote-debugging-port=9227.
This probe writes and clears the first concept: never use student progress.
It simulates composition input events, not the Windows hardware IME.
"""
import asyncio, json, urllib.request
import websockets

async def main():
    targets=json.load(urllib.request.urlopen('http://localhost:9227/json/list'))
    async with websockets.connect(targets[0]['webSocketDebuggerUrl']) as ws:
        seq=0
        async def call(method,params={}):
            nonlocal seq
            seq+=1; current=seq
            await ws.send(json.dumps({'id':current,'method':method,'params':params}))
            while True:
                r=json.loads(await ws.recv())
                if r.get('id')==current:
                    if 'error' in r: raise RuntimeError(r['error'])
                    return r.get('result',{})
        async def js(expression):
            r=await call('Runtime.evaluate',{'expression':expression,'returnByValue':True})
            if 'exceptionDetails' in r: raise RuntimeError(r['exceptionDetails'])
            return r['result'].get('value')
        await js("Array.from(document.querySelectorAll('button')).find(b=>b.textContent.includes('학습 시작'))?.click()")
        await asyncio.sleep(.3)

        await call('Page.bringToFront')
        await call('Emulation.setFocusEmulationEnabled',{'enabled':True})
        await js("window.testInput=document.querySelector('input[placeholder=\"답을 입력하세요\"]'); testInput.focus(); testInput.select()")
        await call('Input.insertText',{'text':''})
        await js("(()=>{window.valueWrites=[]; const valueDescriptor=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value'); Object.defineProperty(HTMLInputElement.prototype,'value',{get(){return valueDescriptor.get.call(this)},set(v){if(this===testInput)valueWrites.push(v);valueDescriptor.set.call(this,v)}});const setAttribute=Element.prototype.setAttribute;Element.prototype.setAttribute=function(k,v){if(this===testInput&&k==='value')valueWrites.push(v);return setAttribute.call(this,k,v)}})()")
        for text in ['ㅍ','파','파ㅇ','파이','파이ㅆ','파이써','파이썬']:
            await js("testInput.value="+json.dumps(text)+";valueWrites.length=0;testInput.dispatchEvent(new InputEvent('input',{bubbles:true,inputType:'insertCompositionText',isComposing:true,data:"+json.dumps(text)+"}))")
            await asyncio.sleep(.08)
            actual=await js('testInput.value')
            print(ascii(text),'->',ascii(actual))
            assert await js('valueWrites.length')==0, 'Framework value rewrite during composition'
            assert actual==text, f'IME corruption: expected {text!r}, got {actual!r}'
        await js("testInput.value='파이썬';valueWrites.length=0;testInput.dispatchEvent(new InputEvent('input',{bubbles:true,inputType:'insertText',isComposing:false,data:'파이썬'}))")
        await asyncio.sleep(.15)
        actual=await js('testInput.value')
        print('committed',ascii(actual)); print('framework value writes',await js('valueWrites'))
        assert await js('valueWrites.length')==0, 'Framework rewrote DOM value during Korean composition'
        assert actual=='파이썬', f'Commit corruption: {actual!r}'
        await js("Array.from(document.querySelectorAll('button')).find(b=>b.textContent.includes('← 클래스룸')).click()")
        await asyncio.sleep(.2)
        await js("Array.from(document.querySelectorAll('button')).find(b=>b.textContent.includes('학습 시작')).click()")
        await asyncio.sleep(.2)
        assert await js("document.querySelector('input[placeholder=\"답을 입력하세요\"]').value")=='파이썬', 'Answer was not restored from drafts'
        await js("Array.from(document.querySelectorAll('button')).find(b=>b.textContent.trim()==='제출').click()")
        await asyncio.sleep(.3)
        assert await js("!!document.querySelector('[aria-label=\"정답 확인\"]')"), 'Correct-answer popup missing'
        await js("Array.from(document.querySelectorAll('button')).find(b=>b.textContent.trim()==='확인').click()")
        await asyncio.sleep(.2)
        assert await js("!!document.querySelector('textarea[data-code-editor]')"), 'Saved answer did not unlock next mission'
        print('PASS: composition preserved, draft restored, Korean answer graded')

asyncio.run(main())
