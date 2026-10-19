// Real RepositoryPlayer with the isolated pilot transport; never writes GitHub progress.
const {chromium}=require('../target/ui-tests/node_modules/playwright-core');
const assert=require('node:assert/strict');
const fs=require('node:fs');
(async()=>{
 const browser=await chromium.connectOverCDP(process.env.MQ3_PILOT_CDP||'http://127.0.0.1:9269');
 try{
  const page=browser.contexts()[0].pages()[0];page.setDefaultTimeout(12000);
  const button=name=>page.getByRole('button',{name,exact:true});
  const back=button('← 코스 수업 목록');
  if(await page.getByRole('dialog',{name:'문제 통과'}).count())await button('여기 머물기').click();
  if(await back.count())await back.click();
  await page.getByRole('heading',{name:'플레이어 검증 코스',exact:true}).waitFor();
  await page.evaluate(()=>document.getElementById('__dx-toast')?.remove());
  await button('버전 a').click();await button('풀모드 시작').click();
  await page.locator('.cm-editor').waitFor();
  await button('초기화').click();await button('제출').click();
  await page.waitForFunction(()=>document.querySelector('.output')?.textContent.includes('다시 풀기')&&![...document.querySelectorAll('.pane-actions button')].find(button=>button.textContent==='제출')?.disabled);
  assert.equal(await page.getByRole('dialog',{name:'문제 통과'}).count(),0,'wrong answer must not open completion');
  const solve=async value=>{
   await page.evaluate(value=>molipCodeEditors.setValue(`console.log(${value});`),value);
   await button('제출').click();await page.getByRole('dialog',{name:'문제 통과'}).waitFor();
  };
  await solve(3);
  assert.match(await page.locator('.study-navigation .selected').innerText(),/문제 1/,'no automatic navigation');
  await page.getByRole('dialog',{name:'문제 통과'}).dispatchEvent('keydown',{key:'Enter',repeat:true,bubbles:true});
  assert.equal(await page.getByRole('dialog',{name:'문제 통과'}).count(),1,'held Enter must not skip a problem');
  await page.keyboard.press('Tab');
  assert.equal(await page.evaluate(()=>document.activeElement.textContent),'여기 머물기');
  await page.keyboard.press('Shift+Tab');
  assert.equal(await page.evaluate(()=>document.activeElement.textContent),'다음으로 이동');
  fs.mkdirSync('target/completion-audit',{recursive:true});
  await page.screenshot({path:'target/completion-audit/passed.png'});
  await button('여기 머물기').click();
  assert.match(await page.locator('.study-navigation .selected').innerText(),/문제 1/);
  await solve(3);await page.keyboard.press('Escape');
  await page.getByRole('dialog',{name:'문제 통과'}).waitFor({state:'hidden'});
  await solve(3);await page.keyboard.press('Enter');
  await page.waitForFunction(()=>document.querySelector('.study-navigation .selected')?.textContent.includes('문제 2'));
  assert.equal(await page.getByRole('dialog',{name:'문제 통과'}).count(),0);
  await solve(5);await button('수업 목록으로').click();
  await button('풀모드 시작').waitFor();await button('풀모드 시작').click();
  await page.locator('.cm-editor').waitFor();await solve(3);await button('다음으로 이동').click();
  await page.waitForFunction(()=>document.querySelector('.study-navigation .selected')?.textContent.includes('문제 2'));
  await solve(5);await page.keyboard.press('Enter');await button('풀모드 시작').waitFor();
  fs.writeFileSync('target/completion-audit/result.json',JSON.stringify({passed:true,checked:['wrong answer has no dialog','success stays on current task','stay button','Enter advances once','next button','last-task button and Enter return to lesson list','isolated progress only']},null,2));
  console.log('PASS native completion dialog, next button, Enter, stay, final task and failure paths');
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exit(1)});
