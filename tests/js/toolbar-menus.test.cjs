const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {chromium,webkit}=require('../../target/ui-tests/node_modules/playwright-core');

for(const [name,engine] of Object.entries({chromium,webkit}))test(`${name}: toolbar menus close without disturbing hints, narration or dialogs`,async()=>{
 const browser=await engine.launch({headless:true});
 try{
  const page=await browser.newPage();
  await page.setContent(`<div class="repository-tools">
   <div class="content-update-controls"><details id="content"><summary>수업 설정</summary><div>수업 업데이트</div></details></div>
   <details class="app-update-settings"><summary>앱 설정</summary><div>환경 진단</div></details>
   </div><details id="hint" open><summary>힌트</summary><p>문제의 단서</p></details><p id="outside">문제</p>`);
  await page.evaluate(()=>{window.stopped=0;window.molipAgent={running:true,stop(){stopped++}};});
  for(const file of ['shortcuts','focus'])await page.addScriptTag({content:fs.readFileSync(`assets/layout/${file}.js`,'utf8')});
  await page.locator('#content>summary').click();
  await page.locator('.app-update-settings>summary').click();
  assert.equal(await page.locator('#content').evaluate(e=>e.open),false);
  assert.equal(await page.locator('.app-update-settings').evaluate(e=>e.open),true);
  await page.keyboard.press('Escape');
  assert.equal(await page.locator('.app-update-settings').evaluate(e=>e.open),false);
  assert.equal(await page.evaluate(()=>document.activeElement.matches('.app-update-settings>summary')),true);
  assert.equal(await page.evaluate(()=>stopped),0,'closing a toolbar menu must not stop the teacher');
  assert.equal(await page.locator('#hint').evaluate(e=>e.open),true,'lesson details stay open');
  await page.locator('#content>summary').click();await page.locator('#outside').click();
  assert.equal(await page.locator('#content').evaluate(e=>e.open),false);
  await page.locator('.app-update-settings>summary').click();
  await page.evaluate(()=>{
   const modal=document.createElement('div');modal.setAttribute('role','dialog');modal.tabIndex=-1;
   modal.textContent='설치 확인';modal.id='modal';modal.addEventListener('keydown',event=>{if(event.key==='Escape')modal.dataset.escaped='true'});
   document.querySelector('.app-update-settings').append(modal);modal.focus();
  });
  await page.keyboard.press('Escape');
  assert.equal(await page.locator('#modal').getAttribute('data-escaped'),'true','modal owns its Escape');
  assert.equal(await page.locator('.app-update-settings').evaluate(e=>e.open),true,'modal parent remains visible');
 }finally{await browser.close();}
});
