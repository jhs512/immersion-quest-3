const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {chromium}=require('../../target/ui-tests/node_modules/playwright-core');

test('explanation demonstrates code without submitting and restores the student answer',async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 try {
  const page=await browser.newPage();
  await page.setContent('<article class="repository-task"><textarea data-code-editor="javascript">console.log(99);</textarea><div class="pane-actions"><button>코드 실행</button><button>제출</button></div><section class="result-pane"><details class="run-input"><textarea aria-label="실행 입력">student input</textarea></details><pre class="output">학생 실행 결과</pre></section></article>');
  await page.addScriptTag({content:fs.readFileSync('assets/editor/editor.bundle.js','utf8')});
  await page.evaluate(()=>{
   window.runs=[];window.submissions=0;
   document.querySelectorAll('button')[0].onclick=()=>runs.push(molipCodeEditors.getValue());
   document.querySelectorAll('button')[1].onclick=()=>submissions++;
  });
  await page.addScriptTag({content:fs.readFileSync('assets/layout/agent.js','utf8')});
  const result=await page.evaluate(async()=>{
   molipAgent.setVoice(false);
   await molipAgent.runExplanation([{action:'set_input',value:'demo input'},{action:'set_code',code:'console.log(3);'},{action:'run'},{action:'submit'}]);
   return {code:molipCodeEditors.getValue(),runs,submissions,input:document.querySelector('.run-input textarea').value};
  });
  assert.equal(result.code,'console.log(99);');
  assert.deepEqual(result.runs,['console.log(3);']);
  assert.equal(result.submissions,0);
  assert.equal(result.input,'student input');
 } finally {await browser.close();}
});

test('stopping pending audio preparation restores state and late audio cannot edit the next task',async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 try {
  const page=await browser.newPage();
  await page.setContent('<article class="repository-task"><textarea data-code-editor="javascript">console.log(99);</textarea></article>');
  await page.addScriptTag({content:fs.readFileSync('assets/editor/editor.bundle.js','utf8')});
  await page.evaluate(()=>{window.molipVoice={enabled:()=>true,synthesize:()=>new Promise(resolve=>{window.releaseAudio=resolve;})};});
  await page.addScriptTag({content:fs.readFileSync('assets/layout/agent.js','utf8')});
  await page.evaluate(()=>{window.pending=molipAgent.runExplanation([{action:'set_code',code:'console.log(3);',say:'준비 중이에요.'}]);});
  await page.waitForFunction(()=>window.releaseAudio);
  await page.evaluate(()=>{molipAgent.stop();molipCodeEditors.setValue('console.log(88);');releaseAudio('late-clip');});
  await page.evaluate(()=>pending);
  assert.equal(await page.evaluate(()=>molipCodeEditors.getValue()),'console.log(88);');
 } finally {await browser.close();}
});

test('choice explanation changes the visible answer then restores it without submission',async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 try {
  const page=await browser.newPage();
  await page.setContent('<article class="repository-task"><input type="hidden" class="answer-state-bridge" value="student"><label data-option-id="correct">정답 보기</label><div class="pane-actions"><button>제출</button></div></article>');
  await page.evaluate(()=>{
   window.answers=[];window.submissions=0;
   document.querySelector('input').oninput=e=>answers.push(e.target.value);
   document.querySelector('button').onclick=()=>submissions++;
  });
  await page.addScriptTag({content:fs.readFileSync('assets/layout/agent.js','utf8')});
  const result=await page.evaluate(async()=>{
   molipAgent.setVoice(false);
   await molipAgent.runExplanation([{action:'choose_answer',id:'correct'},{action:'submit'}]);
   return {answers,submissions,value:document.querySelector('input').value};
  });
  assert.deepEqual(result.answers,['correct','student']);
  assert.equal(result.value,'student');assert.equal(result.submissions,0);
 } finally {await browser.close();}
});

test('Git explanation invokes the real command bridge and waits for its completion',async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 try {
  const page=await browser.newPage();
  await page.setContent('<article class="repository-task"><div id="git-demo-terminal"></div></article>');
  await page.evaluate(()=>{window.calls=[];window.molipGitTutor={command(args){calls.push(args);return new Promise(resolve=>window.finishCommand=resolve);}};});
  await page.addScriptTag({content:fs.readFileSync('assets/layout/agent.js','utf8')});
  await page.evaluate(()=>{molipAgent.setVoice(false);window.finished=false;window.demo=molipAgent.runExplanation([{action:'git_command',args:['branch','--show-current']}]).then(()=>finished=true);});
  await page.waitForFunction(()=>window.calls.length===1,{},{timeout:1500});
  assert.equal(await page.evaluate(()=>finished),false);
  assert.deepEqual(await page.evaluate(()=>calls),[['branch','--show-current']]);
  await page.evaluate(()=>finishCommand(true));await page.evaluate(()=>demo);
  assert.equal(await page.evaluate(()=>finished),true);
 }finally{await browser.close();}
});

test('a retired explanation cannot edit or restore over a new owner on the same task root',async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 try {
  const page=await browser.newPage();
  await page.setContent('<article class="repository-task" data-explanation-session="one"><textarea data-code-editor="javascript">console.log(99);</textarea></article>');
  await page.addScriptTag({content:fs.readFileSync('assets/editor/editor.bundle.js','utf8')});
  await page.evaluate(()=>{window.molipVoice={enabled:()=>true,synthesize:()=>new Promise(resolve=>{window.releaseAudio=resolve;})};});
  await page.addScriptTag({content:fs.readFileSync('assets/layout/agent.js','utf8')});
  await page.evaluate(()=>{window.pending=molipAgent.runExplanation([{action:'set_code',code:'console.log(3);',say:'준비 중이에요.'}],{owner:'one'});});
  await page.waitForFunction(()=>window.releaseAudio);
  await page.evaluate(()=>{document.querySelector('article').dataset.explanationSession='two';molipCodeEditors.setValue('console.log(88);');molipAgent.setVoice(false);releaseAudio(null);});
  await page.evaluate(()=>pending);
  assert.equal(await page.evaluate(()=>molipCodeEditors.getValue()),'console.log(88);');
 }finally{await browser.close();}
});


test('retiring a Git demonstration disposes only its own bridge',async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 try {
  const page=await browser.newPage();
  await page.setContent('<article class="repository-task"></article>');
  await page.addScriptTag({content:fs.readFileSync('assets/layout/agent.js','utf8')});
  const result=await page.evaluate(()=>{
   let disposed=0;window.molipGitTutor={owner:'current',dispose(){disposed++;}};
   const retired=molipAgent.retireGitTutor('retired');
   const kept=window.molipGitTutor?.owner;
   const current=molipAgent.retireGitTutor('current');
   return {retired,kept,current,disposed,removed:!window.molipGitTutor};
  });
  assert.deepEqual(result,{retired:false,kept:'current',current:true,disposed:1,removed:true});
 }finally{await browser.close();}
});
