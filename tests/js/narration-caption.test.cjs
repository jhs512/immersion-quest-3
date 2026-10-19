const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {chromium}=require('../../target/ui-tests/node_modules/playwright-core');
test('caption shows numerical values while speech retains its pronunciation',async()=>{
 const browser=await chromium.launch({...(process.platform==='win32'?{channel:'msedge'}:{}),headless:true});
 try{
  const page=await browser.newPage();
  await page.setContent('<article class="repository-task"><div class="cm-content">minutes = [12, 18, 24, 40, 100]</div><pre class="output">12</pre></article>');
  await page.evaluate(()=>{window.spoken=[];window.clips=[];window.molipVoice={name:'ko-KR-SunHiNeural',enabled:()=>true,rate:1.5,synthesize:async text=>{spoken.push(text);return 'clip'}};window.Audio=class{constructor(){clips.push(this)}play(){return Promise.resolve()}pause(){}}});
  await page.addScriptTag({content:fs.readFileSync('assets/layout/agent.js','utf8')});
  const phrase='배송 시간은 십이, 십팔, 이십사예요. 평균은 사십이에요. 백업 파일은 그대로예요.';
  await page.evaluate(text=>{window.finished=molipAgent.run([{action:'say',text}])},phrase);
  await page.waitForFunction(()=>clips.length===1);
  assert.equal(await page.locator('.agent-caption').textContent(),'배송 시간은 12, 18, 24예요. 평균은 40이에요. 백업 파일은 그대로예요.');
  assert.ok((await page.evaluate(()=>spoken)).every(text=>text===phrase),'audio keeps the authored pronunciation');
  await page.evaluate(()=>molipAgent.stop());await page.evaluate(()=>finished);
 }finally{await browser.close()}
});


test('price captions keep thousands separators while speech keeps Korean pronunciation',async()=>{
 const browser=await chromium.launch({...(process.platform==='win32'?{channel:'msedge'}:{}),headless:true});
 try{
  const page=await browser.newPage();
  await page.setContent('<article class="repository-task"><p>주문 금액은 19,999원이에요.</p></article>');
  await page.addScriptTag({content:fs.readFileSync('assets/speech/pronunciation.js','utf8')});
  await page.addScriptTag({content:fs.readFileSync('assets/speech/speech.js','utf8')});
  await page.evaluate(()=>{window.spoken=[];window.clips=[];window.molipVoice={name:'ko-KR-SunHiNeural',enabled:()=>true,rate:1.5,synthesize:async text=>{spoken.push(molipSpeech.pronunciationText(text));return 'clip'}};window.Audio=class{constructor(){clips.push(this)}play(){return Promise.resolve()}pause(){}}});
  await page.addScriptTag({content:fs.readFileSync('assets/layout/agent.js','utf8')});
  await page.evaluate(()=>{window.finished=molipAgent.run([{action:'say',text:'주문 금액은 만구천구백구십구 원이에요.'}])});
  await page.waitForFunction(()=>clips.length===1);
  assert.equal(await page.locator('.agent-caption').textContent(),'주문 금액은 19,999 원이에요.');
  assert.ok((await page.evaluate(()=>spoken)).every(text=>text==='주문 금액은 만구천구백구십구 원이에요.'));
  await page.evaluate(()=>molipAgent.stop());await page.evaluate(()=>finished);
 }finally{await browser.close()}
});
