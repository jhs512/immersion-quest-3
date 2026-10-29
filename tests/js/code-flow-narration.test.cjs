// A narration's `code_flow` action (assets/layout/agent.js) on the real 코드 흐름 보기 viewer
// (assets/java-trace, built as src/java_trace.rs::viewer_script does) with a trace document that the
// app's tracer recorded for engineer-java-static step 3 (tests/js/fixtures/code-flow-ticket.json).
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {chromium}=require('../../target/ui-tests/node_modules/playwright-core');

const fixture=JSON.parse(fs.readFileSync('tests/js/fixtures/code-flow-ticket.json','utf8'));
const viewer=()=>{
 const highlight=fs.readFileSync('assets/java-trace/core/highlight.js','utf8').replaceAll('export function','function');
 const render=fs.readFileSync('assets/java-trace/core/render.js','utf8').replace("import { highlightLines } from './highlight.js';",'')
  .replaceAll('export function','function').replaceAll('export class','class');
 return `(()=>{if(window.MqTraceView)return;\nconst highlightLines=(()=>{\n${highlight}\nreturn highlightLines;})();\n(()=>{\n${render}\nwindow.MqTraceView=TraceView;})();\n})();\n`+fs.readFileSync('assets/java-trace/code-flow.js','utf8');
};
const escape=text=>text.replace(/&/g,'&amp;').replace(/</g,'&lt;');

async function lessonPage(browser){
 const page=await browser.newPage({viewport:{width:1400,height:950}});
 await page.setContent(`<article class="repository-task"><textarea data-code-editor="java">${escape(fixture.starter.source)}</textarea>
  <div class="pane-actions"><button>코드 실행</button><button class="code-flow-open">코드 흐름 보기</button><button>제출</button></div>
  <button class="narration-stop" data-explanation-stop="true">멈춤</button><section class="result-pane"><pre class="output"></pre></section></article>`);
 await page.addStyleTag({content:fs.readFileSync('assets/java-trace/code-flow.css','utf8')+fs.readFileSync('assets/app.css','utf8')});
 await page.addScriptTag({content:fs.readFileSync('assets/editor/editor.bundle.js','utf8')});
 await page.addScriptTag({content:viewer()});
 await page.evaluate(documents=>{
  // As player_ui.rs: trace the editor's code now, then hand the document to the dialog.
  window.traced=[];window.seeks=[];window.stops=0;
  document.querySelector('.code-flow-open').onclick=()=>{
   const source=molipCodeEditors.getValue();traced.push(source);
   const token=mqCodeFlow.loading();
   setTimeout(()=>documents[source]?mqCodeFlow.show(token,documents[source]):mqCodeFlow.fail(token,'이 테스트에 없는 코드예요.'),30);
  };
  document.querySelector('.narration-stop').onclick=()=>{stops++;molipAgent.stop();};
  const seek=mqCodeFlow.seek.bind(mqCodeFlow);
  mqCodeFlow.seek=target=>{
   const at=seek(target),dialog=document.getElementById('code-flow-dialog');
   seeks.push({at,modal:dialog.matches(':modal'),zIndex:getComputedStyle(dialog).zIndex,
    line:Number(dialog.querySelector('.tv-line.is-next')?.dataset.line),
    stack:[...dialog.querySelectorAll('.tv-frames .tv-frame-title')].map(node=>node.textContent.trim()),
    statics:dialog.querySelector('.tv-globals')?.textContent.replace(/\s+/g,' ').trim(),
    objects:dialog.querySelectorAll('.tv-heap .tv-object').length});
   if(window.closeOnSeek)dialog.querySelector('.code-flow-close').click();
   return at;
  };
 },{[fixture.starter.source]:fixture.starter.document,[fixture.patched.source]:fixture.patched.document});
 await page.addScriptTag({content:fs.readFileSync('assets/layout/agent.js','utf8')});
 return page;
}

test('a narration opens the traced teacher code at the explained steps, then closes it and restores the learner code',async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 try {
  const page=await lessonPage(browser);
  const result=await page.evaluate(async narration=>{
   molipAgent.setVoice(false);
   const log=await molipAgent.runExplanation(narration);
   return {log,traced,seeks,code:molipCodeEditors.getValue(),open:mqCodeFlow.isOpen(),stops};
  },fixture.narration);
  assert.doesNotMatch(result.log,/오류 -/,result.log);
  // Both trace steps of the narration come from one trace of the teacher's patched code.
  assert.deepEqual(result.traced,[fixture.patched.source]);
  assert.deepEqual(result.seeks.map(seen=>[seen.at.line,seen.at.step,seen.line]),[[4,4,4],[4,8,4]]);
  assert.ok(result.seeks.every(seen=>!seen.modal&&seen.zIndex==='1400'),'narrated view stays under the caption without a modal backdrop');
  assert.match(result.seeks[0].statics,/Ticket\.total\s*0/);
  assert.match(result.seeks[1].statics,/Ticket\.total\s*2/);
  assert.equal(result.seeks[1].objects,2);
  assert.ok(result.seeks[0].stack.length>=2,'the constructor frame is on the stack');
  assert.equal(result.open,false);
  assert.equal(result.code,fixture.starter.source);
  assert.equal(result.stops,0);
 } finally {await browser.close();}
});

test('closing the narrated view stops the narration and the learner then opens the ordinary modal view',async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 try {
  const page=await lessonPage(browser);
  const result=await page.evaluate(async()=>{
   molipAgent.setVoice(false);window.closeOnSeek=true;
   const log=await molipAgent.runExplanation([
    {action:'code_flow',line:4,event:'call',target:'flow_statics',say:'첫 생성자 호출이에요.'},
    {action:'code_flow',line:4,event:'return',nth:1,say:'생성자가 끝나요.'}]);
   const after={log,seeks:seeks.length,stops,open:mqCodeFlow.isOpen(),code:molipCodeEditors.getValue()};
   window.closeOnSeek=false;
   document.querySelector('.code-flow-open').click();
   await new Promise(resolve=>setTimeout(resolve,200));
   const dialog=document.getElementById('code-flow-dialog');
   return {...after,learnerModal:dialog.open&&dialog.matches(':modal'),learnerState:mqCodeFlow.state()};
  });
  assert.equal(result.seeks,1,result.log);
  assert.equal(result.stops,1);
  assert.equal(result.open,false);
  assert.equal(result.code,fixture.starter.source);
  assert.equal(result.learnerModal,true);
  assert.equal(result.learnerState.narrated,false);
 } finally {await browser.close();}
});

test('a step the trace does not have is reported instead of showing another step',async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 try {
  const page=await lessonPage(browser);
  const log=await page.evaluate(async()=>{molipAgent.setVoice(false);return molipAgent.runExplanation([{action:'code_flow',line:4,event:'call',nth:3,say:'세 번째 호출이에요.'}]);});
  assert.match(log,/code_flow: 오류 - 코드 흐름에 4행 call 3번째 단계가 없습니다/);
  assert.equal(await page.evaluate(()=>mqCodeFlow.isOpen()),false);
 } finally {await browser.close();}
});
