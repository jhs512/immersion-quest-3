const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {chromium,webkit}=require('../../target/ui-tests/node_modules/playwright-core');
for(const [engineName,engine] of Object.entries({chromium,webkit}))for(const platform of ['MacIntel','Win32'])test(`${engineName} ${platform}: one action per chord, guarded editing, modal help and visible platform hints`,async()=>{
 const browser=await engine.launch({headless:true});
 try{
  const page=await browser.newPage();
  await page.setContent(`<article class="repository-task" data-busy="false" data-narrating="false"><div class="pane-actions">
   <button data-shortcut-action="run" onclick="runs++">코드 실행</button><button data-shortcut-action="submit" data-enter-submit onclick="submits++">제출</button></div>
   <textarea id="editor"></textarea><div class="xterm"><textarea id="terminal"></textarea></div><p id="reading" tabindex="0">문제</p></article>
   <button data-shortcut-action="previous" onclick="moves--">이전 문제</button><button data-shortcut-action="next" onclick="moves++">다음 문제</button>
   <button id="help" data-shortcut-action="help" onclick="molipShortcuts.toggleSheet()">단축키</button>`);
  await page.evaluate(platform=>{Object.defineProperty(navigator,'platform',{value:platform,configurable:true});window.runs=0;window.submits=0;window.moves=0},platform);
  await page.addScriptTag({content:fs.readFileSync('assets/layout/shortcuts.js','utf8')});
  const mod=platform==='MacIntel'?'Meta':'Control';
  await page.locator('#editor').focus();await page.keyboard.press(`${mod}+Enter`);await page.keyboard.press(`${mod}+Enter`);
  assert.equal(await page.evaluate(()=>runs),2);assert.equal(await page.evaluate(()=>submits),0,'double run cannot submit');
  await page.keyboard.press(`${mod}+Shift+Enter`);assert.equal(await page.evaluate(()=>submits),1);
  await page.evaluate(()=>document.querySelector('[data-shortcut-action=run]').disabled=true);
  await page.keyboard.press(`${mod}+Enter`);assert.equal(await page.evaluate(()=>runs),2);
  await page.evaluate(()=>document.querySelector('[data-shortcut-action=submit]').disabled=true);
  await page.keyboard.press(`${mod}+Shift+Enter`);
  await page.evaluate(()=>document.querySelector('[data-shortcut-action=submit]').disabled=false);
  await page.waitForTimeout(160);assert.equal(await page.evaluate(()=>submits),1,'disabled submission is never queued');
  await page.keyboard.press(`${mod}+ArrowRight`);assert.equal(await page.evaluate(()=>moves),0,'editor navigation keeps editing meaning');
  await page.locator('#terminal').focus();await page.keyboard.press('Enter');assert.equal(await page.locator('#terminal').inputValue(),'\n');
  await page.keyboard.press(`${mod}+ArrowRight`);assert.equal(await page.evaluate(()=>moves),0,'terminal navigation keeps shell meaning');
  await page.locator('#reading').focus();await page.keyboard.press(`${mod}+ArrowRight`);assert.equal(await page.evaluate(()=>moves),1);
  await page.keyboard.press(`${mod}+ArrowLeft`);assert.equal(await page.evaluate(()=>moves),0);
  await page.evaluate(()=>document.querySelector('.repository-task').dataset.busy='true');
  await page.keyboard.press(`${mod}+ArrowRight`);assert.equal(await page.evaluate(()=>moves),0,'grading cannot be navigated away with a shortcut');
  await page.evaluate(()=>document.querySelector('.repository-task').dataset.busy='false');
  await page.locator('#reading').evaluate((el,mac)=>{
   for(const extra of [{isComposing:true},{keyCode:229},{repeat:true}])el.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',bubbles:true,cancelable:true,shiftKey:true,...(mac?{metaKey:true}:{ctrlKey:true}),...extra}));
  },platform==='MacIntel');assert.equal(await page.evaluate(()=>submits),1,'IME and held keys cannot submit');
  assert.equal(await page.locator('[data-shortcut-action=run]').getAttribute('data-shortcut-label'),`${platform==='MacIntel'?'⌘':'Ctrl'}+Enter`);
  assert.equal(await page.locator('[data-shortcut-action=submit]').getAttribute('aria-keyshortcuts'),`${platform==='MacIntel'?'Meta':'Control'}+Shift+Enter`);
  await page.locator('#help').click();assert.equal(await page.locator('dialog[open]').count(),1);
  assert.ok((await page.locator('.shortcut-note').textContent()).includes(platform==='MacIntel'?'Command':'Windows'));
  await page.keyboard.press(`${mod}+Shift+Enter`);await page.keyboard.press(`${mod}+ArrowRight`);
  assert.equal(await page.evaluate(()=>submits),1);assert.equal(await page.evaluate(()=>moves),0,'help blocks background actions');
  await page.keyboard.press('Escape');assert.equal(await page.locator('dialog[open]').count(),0);
  assert.equal(await page.evaluate(()=>document.activeElement.id),'help','closing restores focus');
 }finally{await browser.close();}
});
