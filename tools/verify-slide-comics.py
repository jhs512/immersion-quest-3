"""Check comic pagination and emphasis in the running WebView2 (CDP port 9227)."""
import asyncio
import base64
import json
import sys
import urllib.request
from pathlib import Path
import websockets

SOURCE = '''---
theme: molip
---
## 만화와 ** 강조 **
가격이 **높으면** 선택합니다.
```comic-gen
제목: 두 컷
등장인물:
  강사: {그림: 사람, 이름표: 강사}
컷:
  - 인물: [강사]
    대사: [{화자: 강사, 내용: 첫 번째 컷입니다}]
  - 구성: 이전
    대사: [{화자: 강사, 내용: 두 번째 컷입니다}]
```
---
## 끝
'''


async def main():
    pages = json.load(urllib.request.urlopen('http://localhost:9227/json/list'))
    page = next(p for p in pages if p['type'] == 'page')
    async with websockets.connect(page['webSocketDebuggerUrl'], max_size=20_000_000) as ws:
        serial = 0

        async def call(method, params):
            nonlocal serial
            serial += 1
            await ws.send(json.dumps(dict(id=serial, method=method, params=params)))
            while True:
                response = json.loads(await ws.recv())
                if response.get('id') == serial:
                    assert 'error' not in response, response
                    return response['result']

        async def js(source):
            result = await call('Runtime.evaluate', dict(expression=source, returnByValue=True, awaitPromise=True))
            assert 'exceptionDetails' not in result, result
            return result['result'].get('value')

        await call('Emulation.setDeviceMetricsOverride', dict(width=1200, height=900, deviceScaleFactor=1, mobile=False))
        await js("(()=>{document.querySelector('#slide-probe')?.remove(); document.querySelector('#actual-deck')?.remove(); for(const el of document.body.children) { if(el.tagName!=='STYLE'&&el.tagName!=='SCRIPT') el.style.display='none'; } const host=document.createElement('div'); host.id='slide-probe'; host.className='slides-host'; host.style.maxWidth='1100px'; host.dataset.marpSource=" + json.dumps(SOURCE) + "; document.body.append(host); molipSlides.render(host);})()")
        for _ in range(100):
            if await js("document.querySelectorAll('#slide-probe .comic-strip svg').length===2"):
                break
            await asyncio.sleep(.1)
        assert await js("document.querySelectorAll('#slide-probe .marpit > svg').length===3"), 'wrong slide count'
        assert await js("document.querySelectorAll('#slide-probe .comic-strip svg').length===2"), 'comics failed to render'
        assert await js("[...document.querySelectorAll('#slide-probe section')].every(s=>s.querySelectorAll('.comic-strip').length<=1)"), 'multiple panels in a slide'
        assert await js("document.querySelector('#slide-probe strong').textContent==='강조'"), 'literal bold markers'
        for index, text in enumerate(['첫 번째', '두 번째']):
            assert await js("(()=>{const s=[...document.querySelectorAll('#slide-probe section')][" + str(index) + "]; const svg=s.querySelector('.comic-strip svg');return svg.textContent.includes(" + json.dumps(text) + ")})()"), 'wrong panel selected'
            assert await js("(()=>{const s=[...document.querySelectorAll('#slide-probe section')][" + str(index) + "];const r=s.getBoundingClientRect(), c=s.querySelector('.comic-strip svg').getBoundingClientRect();return c.height>20&&c.bottom<=r.bottom&&c.top>=r.top})()"), 'comic clipped'
            shot = await call('Page.captureScreenshot', dict(format='png'))
            Path(f'target/slide-comic-{index + 1}.png').write_bytes(base64.b64decode(shot['data']))
            await js("document.querySelector('#slide-probe .slides-bar button:nth-child(3)').click()")
        assert await js("document.querySelector('#slide-probe .slides-counter').textContent==='3 / 3'"), 'navigation broken'
        sys.path.insert(0, str(Path('tools').resolve()))
        from kpc_course.decks import INTRO
        await js("(()=>{const actual=document.createElement('div'); actual.id='actual-deck'; actual.className='slides-host'; actual.style.maxWidth='1100px'; actual.dataset.marpSource=" + json.dumps(INTRO['markdown']) + "; document.querySelector('#slide-probe').remove(); document.body.append(actual); molipSlides.render(actual);})()")
        for _ in range(200):
            if await js("document.querySelector('#actual-deck .comic-error') || !document.querySelector('#actual-deck code.language-comic-gen')"):
                break
            await asyncio.sleep(.1)
        assert await js("!document.querySelector('#actual-deck .comic-error') && document.querySelectorAll('#actual-deck .comic-strip > svg').length===3"), 'actual course comics missing'
        slides = await js("document.querySelectorAll('#actual-deck .marpit > svg').length")
        for _ in range(slides):
            assert await js("(()=>{const s=[...document.querySelectorAll('#actual-deck .marpit > svg')].find(s=>s.style.display!=='none');const r=s.querySelector('section').getBoundingClientRect();return [...s.querySelectorAll('.comic-strip svg')].every(c=>{const b=c.getBoundingClientRect();return b.bottom<=r.bottom&&b.top>=r.top})})()"), 'actual course comic clipped'
            await js("document.querySelector('#actual-deck .slides-bar button:nth-child(3)').click()")
        print('PASS: both resolved panels fit, emphasis renders, navigation preserves all slides')


asyncio.run(main())
