const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {chromium,webkit}=require('../../target/ui-tests/node_modules/playwright-core');
for(const engine of ['chromium','webkit'])test(`${engine}: both workspace dividers resize independently and stay within the pane`,async()=>{
 const browser=await ({chromium,webkit}[engine]).launch(engine==='chromium'?{channel:'msedge',headless:true}:{headless:true,...(process.env.MQ3_WEBKIT_EXECUTABLE?{executablePath:process.env.MQ3_WEBKIT_EXECUTABLE}:{})});
 try{
  const page=await browser.newPage({viewport:{width:1280,height:850}});
  await page.route('http://split.test/',r=>r.fulfill({body:'<html></html>',contentType:'text/html'}));await page.goto('http://split.test/');
  const styles=['assets/app.css','assets/repository-player.css','assets/player-workspace.css'].map(f=>fs.readFileSync(f,'utf8')).join('\n');
  await page.setContent(`<style>${styles}</style><div class="repository-session"><div class="lesson repository-task" style="height:650px;min-height:0"><div class="problem-pane">문제</div><div class="split-col split-handle"></div><section class="coding-pane"><div class="pane-heading">main.py</div><div class="editor-pane interaction-example-editor" style="display:grid;grid-template-rows: minmax(48px,1fr) 10px var(--example-answer-height,fit-content(60%))"><textarea data-code-editor="python">print(31 &gt;= 30)</textarea><div class="split-handle split-row split-example" role="separator" tabindex="0"></div><div class="interaction-example-answer"><fieldset class="answer-interaction"><legend>답을 골라요</legend><label class="answer-option"><input type="radio">31</label><label class="answer-option"><input type="radio">True · 참</label></fieldset></div></div><div class="split-handle split-row split-result" role="separator" tabindex="0"></div><section class="result-pane">실행 결과</section></section></div></div>`);
  for(const file of ['assets/editor/editor.bundle.js','assets/layout/split.js'])await page.addScriptTag({content:fs.readFileSync(file,'utf8')});
  const height=s=>page.locator(s).evaluate(e=>e.getBoundingClientRect().height);
  assert.ok(await height('.interaction-example-answer')<160,'two choices must not reserve most of the workspace');
  fs.mkdirSync('target/workspace-split',{recursive:true});await page.screenshot({path:`target/workspace-split/${engine}.png`});
  const before=await height('.python-editor-host'),outer=await height('.editor-pane');
  await page.locator('.split-example').focus();await page.keyboard.press('Shift+ArrowUp');
  assert.ok(await height('.python-editor-host')<before-25,'upper handle must resize code, not the entire editor');
  assert.ok(Math.abs(await height('.editor-pane')-outer)<2,'upper handle must preserve result height');
  await page.locator('.split-result').focus();await page.keyboard.press('Shift+ArrowDown');
  assert.ok(await height('.editor-pane')>outer+25,'lower handle resizes code + choices');
  for(const selector of ['.split-result','.split-example']){
   const r=await page.locator(selector).boundingBox();await page.mouse.move(r.x+r.width/2,r.y+r.height/2);await page.mouse.down();await page.mouse.move(r.x+r.width/2,r.y+1500,{steps:5});await page.mouse.up();
  }
  assert.ok(await height('.result-pane')>=70,'results remain accessible at maximum drag');
  assert.ok(await height('.interaction-example-answer')>=62,'choices remain accessible at maximum drag');
  await page.locator('.lesson').evaluate(e=>e.style.height='420px');await page.setViewportSize({width:1100,height:620});await page.waitForTimeout(150);
  const boxes=await page.evaluate(()=>{const rect=s=>{const r=document.querySelector(s).getBoundingClientRect();return {top:r.top,bottom:r.bottom}};return {pane:rect('.coding-pane'),result:rect('.result-pane'),answer:rect('.interaction-example-answer'),editor:rect('.editor-pane')}});
  assert.ok(boxes.result.bottom<=boxes.pane.bottom+1,JSON.stringify(boxes));
  assert.ok(boxes.answer.bottom<=boxes.editor.bottom+1,JSON.stringify(boxes));
  await page.locator('.split-example').dblclick();
  assert.equal(await page.locator('.interaction-example-editor').evaluate(e=>e.style.getPropertyValue('--example-answer-height')),'');
  await page.evaluate(()=>{const field=document.querySelector('fieldset');for(let i=0;i<20;i++)field.appendChild(field.querySelector('label').cloneNode(true))});
  const overflow=await page.evaluate(()=>document.querySelector('.interaction-example-answer').getBoundingClientRect().bottom-document.querySelector('.editor-pane').getBoundingClientRect().bottom);
  assert.ok(overflow<=1,'many choices scroll inside the panel');
 }finally{await browser.close()}
});
