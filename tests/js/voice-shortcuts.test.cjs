const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {chromium,webkit}=require('../../target/ui-tests/node_modules/playwright-core');

for(const [name,engine] of Object.entries({chromium,webkit}))for(const platform of ['Win32','MacIntel'])test(`${name} ${platform}: global voice speed persists and changes playing narration from editor, terminal and dialogs`,async()=>{
 const browser=await engine.launch({headless:true});
 try{
  const page=await browser.newPage();
  await page.route('http://voice.test/**',route=>route.fulfill({contentType:'text/html',body:'<section class="problem-pane"><textarea id="editor"></textarea><div class="xterm"><textarea id="terminal"></textarea></div><select class="assistant-rate"><option>0.75</option><option>1</option><option>1.25</option><option>1.5</option><option>1.75</option><option>2</option></select></section><dialog id="overview"><button>해설</button></dialog>'}));
  await page.goto('http://voice.test/');
  await page.evaluate(platform=>{
   Object.defineProperty(navigator,'platform',{value:platform,configurable:true});
   window.fetch=async()=>new Response(new Blob(['mp3']));
   window.clips=[];
   window.Audio=class{constructor(){clips.push(this)}play(){this.onplay?.();return Promise.resolve()}pause(){}};
  },platform);
  for(const file of ['assets/speech/pronunciation.js','assets/layout/voice.js','assets/layout/agent.js','assets/layout/shortcuts.js'])await page.addScriptTag({content:fs.readFileSync(file,'utf8')});
  const mod=platform==='MacIntel'?'Meta':'Control';
  await page.evaluate(()=>{molipVoice.setRate(1);window.playing=molipAgent.run([{action:'say',text:'재생 속도를 바꿔 보세요.'}]);});
  await page.waitForFunction(()=>clips.length===1);
  for(const id of ['editor','terminal']){
   await page.locator(`#${id}`).focus();
   await page.keyboard.press(`${mod}+Alt+ArrowUp`);
  }
  assert.deepEqual(await page.evaluate(()=>[molipVoice.rate,clips[0].playbackRate,document.querySelector('select').value]),[1.5,1.5,'1.5']);
  await page.evaluate(()=>document.querySelector('#overview').showModal());
  await page.keyboard.press(`${mod}+Alt+ArrowDown`);
  assert.equal(await page.locator('[data-voice-rate-status]').textContent(),'AI 음성 속도 1.25배');
  await page.evaluate(()=>molipShortcuts.toggleSheet(true));
  await page.keyboard.press(`${mod}+Alt+ArrowUp`);
  assert.equal(await page.locator('.shortcut-sheet [data-voice-rate-status]').textContent(),'AI 음성 속도 1.5배');
  assert.ok((await page.locator('.shortcut-sheet').textContent()).includes('AI 음성 느리게'));
  await page.evaluate(()=>{
   molipVoice.setRate(1);
   const chord={key:'ArrowUp',altKey:true,...(/mac/i.test(navigator.platform)?{metaKey:true}:{ctrlKey:true}),bubbles:true,cancelable:true};
   for(const extra of [{isComposing:true},{keyCode:229},{repeat:true}])document.activeElement.dispatchEvent(new KeyboardEvent('keydown',{...chord,...extra}));
  });
  assert.equal(await page.evaluate(()=>molipVoice.rate),1,'IME and held keys must not change speed');
  for(let i=0;i<10;i++)await page.keyboard.press(`${mod}+Alt+ArrowUp`);
  assert.equal(await page.evaluate(()=>molipVoice.rate),2);
  for(let i=0;i<10;i++)await page.keyboard.press(`${mod}+Alt+ArrowDown`);
  assert.equal(await page.evaluate(()=>molipVoice.rate),0.75);
  await page.evaluate(()=>molipAgent.stop());
  await page.reload();
  await page.addScriptTag({content:fs.readFileSync('assets/layout/voice.js','utf8')});
  assert.equal(await page.evaluate(()=>molipVoice.rate),0.75,'speed survives reloading the app document');
 }finally{await browser.close();}
});
