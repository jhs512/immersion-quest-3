const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {chromium}=require('../../target/ui-tests/node_modules/playwright-core');

test('narration speaks faster and follows the run button and its output',async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 try {
  const page=await browser.newPage();
  await page.route('http://narration.test/',route=>route.fulfill({body:'<!doctype html><html></html>',contentType:'text/html'}));
  await page.goto('http://narration.test/');
  await page.evaluate(()=>localStorage.clear());
  await page.setContent('<div class="pane-actions"><button>코드 실행</button></div><section class="result-pane"><pre class="output">결과</pre></section>');
  await page.addScriptTag({content:fs.readFileSync(path.join(__dirname,'../../assets/speech/pronunciation.js'),'utf8')});
  await page.evaluate(()=>{
   // Keep a clip open so assertions observe the actual speaking/highlighting phase.
   window.clips=[];window.clicked=0;
   window.Audio=class {constructor(){window.clips.push(this)}play(){return Promise.resolve()}pause(){}};
   document.querySelector('button').onclick=()=>window.clicked++;
  });
  // Use a real origin for the saved-rate path; isolate network synthesis only.
  await page.addScriptTag({content:fs.readFileSync(path.join(__dirname,'../../assets/layout/voice.js'),'utf8')});
  await page.evaluate(()=>{molipVoice.synthesize=async()=> 'test-clip';});
  await page.addScriptTag({content:fs.readFileSync(path.join(__dirname,'../../assets/layout/agent.js'),'utf8')});
  await page.evaluate(()=>{window.finished=molipAgent.run([{action:'run',say:'실행해요.'},{action:'say',target:'output',text:'결과를 보세요.'}]);});
  await page.waitForFunction(()=>window.clips.length===1);
  assert.equal(await page.evaluate(()=>clips[0].playbackRate),1.5,'default spoken pace');
  assert.equal(await page.evaluate(()=>parseFloat(document.querySelector('.agent-spotlight').style.left)),await page.locator('button').evaluate(e=>e.getBoundingClientRect().left-6));
  await page.evaluate(()=>molipVoice.setRate(1.75));
  assert.equal(await page.evaluate(()=>clips[0].playbackRate),1.75,'change current audio immediately');
  await page.evaluate(()=>clips[0].onended());
  await page.waitForFunction(()=>window.clips.length===2);
  assert.equal(await page.evaluate(()=>window.clicked),1);
  assert.equal(await page.evaluate(()=>parseFloat(document.querySelector('.agent-spotlight').style.top)),await page.locator('.output').evaluate(e=>e.getBoundingClientRect().top-6));
  assert.equal(await page.evaluate(()=>clips[1].playbackRate),1.75);
  await page.evaluate(()=>clips[1].onended());
  await page.evaluate(()=>window.finished);
  assert.equal(await page.locator('.agent-spotlight').evaluate(e=>e.hidden),true);
  await page.evaluate(()=>{delete window.molipVoice;});
  await page.addScriptTag({content:fs.readFileSync(path.join(__dirname,'../../assets/layout/voice.js'),'utf8')});
  assert.equal(await page.evaluate(()=>molipVoice.rate),1.75,'keep the learner speed after reloading');
  await page.evaluate(()=>{window.finished=molipAgent.run([{action:'run'}]);});
  await page.waitForFunction(()=>window.clicked===2);
  assert.equal(await page.evaluate(()=>parseFloat(document.querySelector('.agent-spotlight').style.left)),await page.locator('button').evaluate(e=>e.getBoundingClientRect().left-6),'silent run must not keep the previous output spotlight');
  await page.evaluate(()=>window.finished);
 } finally {await browser.close();}
});

test('narration types only changed lines, highlights them, then runs each completed step',async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 try {
  const page=await browser.newPage();
  await page.setContent('<div class="pane-actions"><button>코드 실행</button></div><textarea data-code-editor="python"># 준비 코드\nx = 1\ny = 2\nprint(x + y)</textarea><section class="result-pane"><pre class="output"></pre></section>');
  await page.addScriptTag({content:fs.readFileSync(path.join(__dirname,'../../assets/speech/pronunciation.js'),'utf8')});
  await page.addScriptTag({content:fs.readFileSync(path.join(__dirname,'../../assets/editor/editor.bundle.js'),'utf8')});
  await page.evaluate(()=>{
   window.edits=[];window.runs=[];window.spoken=[];
   document.querySelector('textarea').addEventListener('input',e=>edits.push(e.target.value));
   document.querySelector('button').onclick=()=>runs.push(molipCodeEditors.getValue());
   window.molipVoice={enabled:()=>true,rate:1.5,synthesize:async()=> 'clip'};
   window.Audio=class {play(){spoken.push([...document.querySelectorAll('.cm-narration-line')].map(e=>e.textContent));setTimeout(()=>this.onended(),60);return Promise.resolve()}pause(){}};
   window.initial=molipCodeEditors.getValue();
  });
  await page.addScriptTag({content:fs.readFileSync(path.join(__dirname,'../../assets/layout/agent.js'),'utf8')});
  await page.evaluate(()=>{window.finished=molipAgent.run([
   {action:'run'},{action:'say',target:'editor',text:'이 두 줄을 보세요.'},
   {action:'patch_code',before:'x = 1\ny = 2',after:'x = 10\ny = 20',say:'이 두 줄을 바꿔요.'},
   {action:'run'},{action:'say',target:'output',text:'결과를 비교해요.'},
  ]);});
  await page.evaluate(()=>finished);
  const result=await page.evaluate(()=>({edits,runs,spoken,initial,final:molipCodeEditors.getValue(),marked:document.querySelectorAll('.cm-narration-line').length}));
  assert.ok(result.edits.length>4,'the edit must be visible in multiple keystrokes');
  for(const value of result.edits){assert.ok(value.startsWith('# 준비 코드\n'));assert.ok(value.endsWith('\nprint(x + y)'));}
  assert.deepEqual(result.runs,[result.initial,result.initial.replace('x = 1\ny = 2','x = 10\ny = 20')]);
  assert.deepEqual(result.spoken[0],['x = 1','y = 2'],'speech focuses the two changed lines');
  assert.equal(result.marked,0,'stop/end clears line marks');
 }finally{await browser.close();}
});

test('all narration clips finish caching before playback; stop cancels preparation',async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 try {
  const page=await browser.newPage();
  await page.route('http://narration.test/',route=>route.fulfill({body:'<!doctype html><html></html>',contentType:'text/html'}));
  await page.goto('http://narration.test/');
  await page.setContent('<section class="problem-pane">문제</section><section class="result-pane"><pre class="output">결과</pre></section>');
  await page.addScriptTag({content:fs.readFileSync(path.join(__dirname,'../../assets/speech/pronunciation.js'),'utf8')});
  await page.evaluate(()=>{
   window.downloads=[];window.clips=[];
   window.fetch=()=>new Promise(resolve=>downloads.push(()=>resolve(new Response(new Blob(['audio'])))));
   window.Audio=class {constructor(){clips.push(this)}play(){return Promise.resolve()}pause(){}};
  });
  for(const file of ['voice.js','agent.js'])await page.addScriptTag({content:fs.readFileSync(path.join(__dirname,'../../assets/layout',file),'utf8')});
  await page.evaluate(()=>{window.finished=molipAgent.run([{action:'say',target:'problem',text:'첫 설명'},{action:'say',target:'output',text:'결과 설명'}]);});
  await page.waitForFunction(()=>downloads.length===2);
  await page.evaluate(()=>downloads[0]());
  await page.waitForTimeout(80);
  assert.equal(await page.evaluate(()=>clips.length),0,'do not play the first sentence while the rest is downloading');
  assert.equal(await page.locator('.agent-spotlight').evaluate(e=>e.hidden),true,'preparation must not highlight the next action early');
  await page.evaluate(()=>downloads[1]());
  await page.waitForFunction(()=>clips.length===1);
  await page.evaluate(()=>clips[0].onended());
  await page.waitForFunction(()=>clips.length===2);
  await page.evaluate(()=>clips[1].onended());
  await page.evaluate(()=>finished);
  await page.evaluate(()=>{window.finished=molipAgent.run([{action:'say',target:'problem',text:'첫 설명'}]);});
  await page.waitForFunction(()=>clips.length===3);
  assert.equal(await page.evaluate(()=>downloads.length),2,'replay uses cached audio');
  await page.evaluate(()=>molipAgent.stop());await page.evaluate(()=>finished);
  await page.evaluate(()=>{window.finished=molipAgent.run([{action:'say',text:'새 설명'}]);});
  await page.waitForFunction(()=>downloads.length===3);
  await page.evaluate(()=>molipAgent.stop());
  await page.evaluate(()=>finished);
  assert.equal(await page.evaluate(()=>clips.length),3,'stop during download must never start playback');
 }finally{await browser.close();}
});

test('run narration points at code rather than its trailing blank line',async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 try{
  const page=await browser.newPage();
  await page.setContent('<div class="pane-actions"><button>코드 실행</button></div><textarea data-code-editor="python"># 설명\nprint("분석 시작")\n</textarea><section class="result-pane"><pre class="output"></pre></section>');
  await page.addScriptTag({content:fs.readFileSync(path.join(__dirname,'../../assets/speech/pronunciation.js'),'utf8')});
  await page.addScriptTag({content:fs.readFileSync(path.join(__dirname,'../../assets/editor/editor.bundle.js'),'utf8')});
  await page.evaluate(()=>{molipCodeEditors.setValue('# 설명\nprint("분석 시작")\n');window.clips=[];window.molipVoice={enabled:()=>true,rate:1.5,synthesize:async()=> 'clip'};window.Audio=class{constructor(){clips.push(this)}play(){return Promise.resolve()}pause(){}};document.querySelector('button').onclick=()=>{document.querySelector('.output').textContent='분석 시작'};});
  await page.addScriptTag({content:fs.readFileSync(path.join(__dirname,'../../assets/layout/agent.js'),'utf8')});
  await page.evaluate(()=>{window.finished=molipAgent.run([{action:'run'},{action:'say',target:'output',text:'실행 결과를 확인해요.'}])});
  await page.waitForFunction(()=>clips.length===1);
  assert.deepEqual(await page.locator('.cm-narration-line').allTextContents(),['print("분석 시작")']);
  assert.equal(await page.locator('.cm-activeLine').textContent(),'print("분석 시작")');
  await page.evaluate(()=>{clips[0].onended()});await page.evaluate(()=>finished);
 }finally{await browser.close()}
});

test('replacement visibly backspaces and types one Unicode character per edit',async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 try{
  const page=await browser.newPage();await page.setContent('<textarea data-code-editor="python"># 유지\nprint("자료 준비")\n</textarea>');
  await page.addScriptTag({content:fs.readFileSync(path.join(__dirname,'../../assets/speech/pronunciation.js'),'utf8')});
  await page.addScriptTag({content:fs.readFileSync(path.join(__dirname,'../../assets/editor/editor.bundle.js'),'utf8')});
  await page.evaluate(()=>{window.edits=[molipCodeEditors.getValue()];document.querySelector('textarea').addEventListener('input',e=>edits.push(e.target.value));});
  await page.addScriptTag({content:fs.readFileSync(path.join(__dirname,'../../assets/layout/agent.js'),'utf8')});
  await page.evaluate(async()=>{await molipAgent.run([{action:'patch_code',before:'자료 준비',after:'분석 🚀'}])});
  const edits=await page.evaluate(()=>edits);
  assert.equal(edits.at(-1),'# 유지\nprint("분석 🚀")\n');
  for(let i=1;i<edits.length;i++)assert.equal(Math.abs(Array.from(edits[i]).length-Array.from(edits[i-1]).length),1,'each deletion/insertion is one character');
  assert.ok(edits.length>=10);
 }finally{await browser.close()}
});

test('narration follows execution completion without waiting for history storage',async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 try{
  const page=await browser.newPage();await page.setContent('<div class="pane-actions"><button>코드 실행</button></div><section class="result-pane" data-execution-id="0" data-execution-state="idle"><pre class="output"></pre></section>');
  await page.addScriptTag({content:fs.readFileSync(path.join(__dirname,'../../assets/speech/pronunciation.js'),'utf8')});
  await page.evaluate(()=>{document.querySelector('button').onclick=()=>{const button=document.querySelector('button'),pane=document.querySelector('.result-pane');button.disabled=true;pane.dataset.executionId='1';pane.dataset.executionState='running';setTimeout(()=>{pane.dataset.executionState='finished';pane.querySelector('.output').textContent='분석 시작'},40);setTimeout(()=>{button.disabled=false},2000)}});
  await page.addScriptTag({content:fs.readFileSync(path.join(__dirname,'../../assets/layout/agent.js'),'utf8')});
  const result=await page.evaluate(async()=>Promise.race([molipAgent.run([{action:'run'}]),new Promise(resolve=>setTimeout(()=>resolve('WAITED_FOR_STORAGE'),900))]));
  assert.notEqual(result,'WAITED_FOR_STORAGE');assert.match(result,/분석 시작/);
 }finally{await browser.close()}
});
