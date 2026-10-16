"""WebView2 reward lifecycle probe (launch app with CDP port 9227)."""
import asyncio
import base64
import json
import urllib.request
from pathlib import Path
import websockets


async def main():
    page = next(p for p in json.load(urllib.request.urlopen('http://localhost:9227/json/list')) if p['type'] == 'page')
    async with websockets.connect(page['webSocketDebuggerUrl'], max_size=20_000_000) as ws:
        seq = 0

        async def call(method, params):
            nonlocal seq
            seq += 1
            await ws.send(json.dumps(dict(id=seq, method=method, params=params)))
            while True:
                response = json.loads(await ws.recv())
                if response.get('id') == seq:
                    assert 'error' not in response, response
                    return response['result']

        async def js(source):
            result = await call('Runtime.evaluate', dict(expression=source, returnByValue=True))
            assert 'exceptionDetails' not in result, result
            return result['result'].get('value')

        async def show(before, after):
            await js("document.querySelector('#reward-probe')?.remove();")
            markup = f'''<div id="reward-probe" class="doctor-backdrop victory-backdrop"><section class="doctor-panel victory-panel" data-xp-before="{before}" data-xp-after="{after}" role="dialog" aria-label="정답 확인">
<div class="victory-emblem">✦</div><p class="victory-eyebrow">MISSION COMPLETE</p><h2>정답입니다!</h2><p>한 걸음 더 성장했어요.</p><div class="victory-reward">+{after-before} XP</div>
<div class="victory-xp"><div class="victory-xp-label"><strong class="victory-level">Lv. 1</strong><span class="victory-total">{before} XP</span></div><div class="victory-track"><div class="victory-fill"></div></div><p class="victory-level-note">미션마다 100 XP · 500 XP마다 레벨 업</p></div>
<div class="popup-actions"><button class="primary">다음 미션 ›</button><button>여기 머물기</button></div></section></div>'''
            await js('document.body.insertAdjacentHTML("beforeend",' + json.dumps(markup) + '); molipVictory.scan();')
            await asyncio.sleep(.1)

        await call('Emulation.setDeviceMetricsOverride', dict(width=1200, height=900, deviceScaleFactor=1, mobile=False))
        await call('Emulation.setEmulatedMedia', dict(features=[dict(name='prefers-reduced-motion', value='no-preference')]))
        await show(400, 500)
        assert await js("!!document.querySelector('.victory-fireworks')"), 'fireworks missing'
        await asyncio.sleep(.7)
        xp = await js("Number(document.querySelector('.victory-total').textContent.split(' ')[0])")
        assert 400 < xp < 500, 'XP counter does not animate'
        screenshot = await call('Page.captureScreenshot', dict(format='png'))
        Path('target/victory-animation.png').write_bytes(base64.b64decode(screenshot['data']))
        await asyncio.sleep(2)
        assert await js("document.querySelector('.victory-total').textContent==='500 XP' && document.querySelector('.victory-level').textContent==='Lv. 2' && document.querySelector('.victory-panel').classList.contains('leveled-up')"), 'level boundary incorrect'
        assert await js("!document.querySelector('.victory-fireworks')"), 'canvas leaked'
        await show(500, 500)
        await js("document.querySelector('#reward-probe').remove()")
        await asyncio.sleep(.1)
        assert await js("!document.querySelector('.victory-fireworks')"), 'early dismissal leaks canvas'
        await call('Emulation.setEmulatedMedia', dict(features=[dict(name='prefers-reduced-motion', value='reduce')]))
        await show(500, 600)
        assert await js("!document.querySelector('.victory-fireworks') && document.querySelector('.victory-total').textContent==='600 XP'"), 'reduced motion not respected'
        await js("document.querySelector('#reward-probe').remove()")
        print('PASS: fireworks, animated XP, level up, early-dismiss cleanup, reduced motion')


asyncio.run(main())
