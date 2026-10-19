const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {chromium,webkit}=require('../../target/ui-tests/node_modules/playwright-core');
for(const [name,engine] of Object.entries({chromium,webkit}))test(name+': dialog overview speaks and highlights without editing work, and closing cancels it',async()=>{
 const browser=await engine.launch({headless:true});
 try{
  const page=await browser.newPage();
  await page.setContent('<textarea id="work">내 작업</textarea><dialog id="lesson-info-dialog"><ul><li id="lesson-goal-0">목표 하나예요.</li><li id="lesson-goal-1">목표 둘이에요.</li></ul><p id="lesson-learning-strategy">직접 비교해요.</p><p id="lesson-overview-status"></p></dialog>');
  await page.evaluate(()=>{
   window.played=[];window.held=null;
   window.molipVoice={name:'ko-KR-SunHiNeural',enabled:()=>true,rate:1,synthesize:async text=>text};
   window.Audio=class{constructor(text){this.text=text;}play(){played.push(this.text);held=this;return Promise.resolve();}pause(){}};
   document.querySelector('dialog').showModal();
  });
  await page.addScriptTag({content:fs.readFileSync('assets/layout/agent.js','utf8')});
  await page.evaluate(()=>{molipAgent.setVoice(false);window.done=molipAgent.runOverview([{action:'say',text:'목표 하나예요.',target:'#lesson-goal-0'},{action:'say',text:'목표 둘이에요.',target:'#lesson-goal-1'},{action:'say',text:'직접 비교해요.',target:'#lesson-learning-strategy'}],document.querySelector('dialog'));});
  await page.waitForFunction(()=>played.length===1);
  assert.equal(await page.locator('.overview-speaking').getAttribute('id'),'lesson-goal-0');
  await page.evaluate(()=>held.onended());
  await page.waitForFunction(()=>played.length===2);
  assert.equal(await page.locator('.overview-speaking').getAttribute('id'),'lesson-goal-1');
  await page.evaluate(()=>document.querySelector('dialog').close());
  await page.evaluate(()=>done);
  assert.equal(await page.locator('.overview-speaking').count(),0);
  assert.equal(await page.locator('#work').inputValue(),'내 작업');
  assert.equal(await page.evaluate(()=>molipAgent.voice),false);
  assert.equal(await page.evaluate(()=>molipAgent.running),false);
  assert.equal(await page.evaluate(()=>played.length),2);
 }finally{await browser.close();}
});
