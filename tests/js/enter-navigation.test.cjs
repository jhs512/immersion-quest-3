const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {chromium}=require('../../target/ui-tests/node_modules/playwright-core');

test('Enter submits answers and advances once while preserving editing and composition',async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 try{
  const page=await browser.newPage();
  await page.setContent(`<main><section class="quiz-question"><input type="radio" name="answer"><input id="answer"></section>
   <div class="quiz-actions"><button class="primary" onclick="grades++">제출</button></div>
   <button id="shortcut-next-mission" onclick="moves++">다음</button>
   <textarea id="code"></textarea><div class="xterm"><textarea id="terminal"></textarea></div>
   <div id="reading" tabindex="0">문제</div></main>`);
  await page.evaluate(()=>{window.grades=0;window.moves=0});
  await page.addScriptTag({content:fs.readFileSync('assets/layout/shortcuts.js','utf8')});
  await page.locator('input[type=radio]').focus();await page.keyboard.press('Enter');
  assert.equal(await page.evaluate(()=>grades),1,'choice answers submit on Enter');
  assert.equal(await page.evaluate(()=>moves),0,'submission must not also skip to the next problem');
  await page.evaluate(()=>document.querySelector('.quiz-actions button').disabled=true);
  await page.locator('#answer').focus();await page.keyboard.press('Enter');
  assert.equal(await page.evaluate(()=>moves),1,'a graded answer advances on Enter');
  await page.locator('#reading').focus();await page.keyboard.press('Enter');
  assert.equal(await page.evaluate(()=>moves),2,'reading area advances on Enter');
  for(const id of ['code','terminal']){
   await page.locator('#'+id).focus();await page.keyboard.press('Enter');
   assert.equal(await page.locator('#'+id).inputValue(),'\n');
  }
  assert.equal(await page.evaluate(()=>moves),2,'editor and terminal keep Enter');
  await page.evaluate(()=>document.body.insertAdjacentHTML('beforeend','<section role="dialog" hidden></section>'));
  await page.locator('#reading').focus();await page.keyboard.press('Enter');
  assert.equal(await page.evaluate(()=>moves),3,'a closed shortcut sheet cannot block navigation');
  // This checks shortcut filtering, not actual OS IME compatibility.
  await page.locator('#reading').evaluate(el=>{
   for(const extra of [{isComposing:true},{keyCode:229},{repeat:true}])
    el.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',bubbles:true,cancelable:true,...extra}));
  });
  assert.equal(await page.evaluate(()=>moves),3,'composition and held Enter cannot skip steps');
  await page.evaluate(()=>document.body.insertAdjacentHTML('beforeend','<section class="doctor-panel" role="dialog"><button>닫기</button></section>'));
  await page.locator('#reading').focus();await page.keyboard.press('Enter');
  assert.equal(await page.evaluate(()=>moves),3,'an open dialog blocks background navigation');
  await page.evaluate(()=>document.querySelector('.doctor-panel').innerHTML='<button class="primary" onclick="cards++">다음 미션</button>');
  await page.evaluate(()=>window.cards=0);await page.keyboard.press('Enter');
  assert.equal(await page.evaluate(()=>cards),1,'success card still accepts Enter');
  await page.evaluate(()=>{
   document.querySelector('.doctor-panel').remove();
   document.querySelector('.quiz-actions').remove();
   document.querySelector('.quiz-question').className='answer-interaction';
   document.querySelector('#shortcut-next-mission').removeAttribute('id');
   document.querySelector('main > button').dataset.enterNext='true';
   document.querySelector('main').insertAdjacentHTML('beforeend','<button data-enter-submit onclick="grades++">제출</button>');
  });
  await page.locator('#answer').focus();await page.keyboard.press('Enter');
  assert.equal(await page.evaluate(()=>grades),2,'repository answer submits through the production hook');
  await page.evaluate(()=>document.querySelector('[data-enter-submit]').disabled=true);
  await page.keyboard.press('Enter');
  assert.equal(await page.evaluate(()=>moves),3,'a busy repository submission must not skip the problem');
  await page.evaluate(()=>{
   document.querySelector('[data-enter-submit]').remove();
   document.body.insertAdjacentHTML('beforeend','<section class="task-passed-dialog" role="dialog"><button class="primary" onclick="cards++">다음으로 이동</button></section>');
  });
  await page.keyboard.press('Enter');
  assert.equal(await page.evaluate(()=>cards),2,'repository success dialog advances even if editor retained focus');
  await page.evaluate(()=>document.querySelector('.task-passed-dialog').remove());
  await page.locator('#reading').focus();await page.keyboard.press('Enter');
  assert.equal(await page.evaluate(()=>moves),4,'repository reading hook advances');
 }finally{await browser.close()}
});
