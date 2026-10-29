// The narration's code typing in the real CodeMirror editor (assets/editor/editor.bundle.js):
// the lesson 「자바 · 계산을 메서드로 나눠요」 step 1 used to show `return fee + 1    }` while typing.
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {chromium}=require('../../target/ui-tests/node_modules/playwright-core');

const root=path.join(__dirname,'../..');
const lesson=JSON.parse(fs.readFileSync(path.join(root,'courses/redesigned/java-methods.json'),'utf8'));
const task=lesson.tasks[0];
const edit=task.narration.find(a=>a.action==='patch_code');

async function open(browser,student){
 const page=await browser.newPage();
 await page.setContent('<article class="repository-task"><textarea data-code-editor="java"></textarea><div class="pane-actions"><button>코드 실행</button></div><section class="result-pane"><pre class="output"></pre></section></article>');
 await page.locator('textarea').evaluate((e,v)=>{e.value=v;},student);
 await page.addScriptTag({content:fs.readFileSync(path.join(root,'assets/editor/editor.bundle.js'),'utf8')});
 await page.evaluate(()=>{
  window.frames=[];
  document.querySelector('textarea').addEventListener('input',e=>frames.push(e.target.value));
  window.molipVoice={enabled:()=>false,rate:1.5};
 });
 await page.addScriptTag({content:fs.readFileSync(path.join(root,'assets/layout/agent.js'),'utf8')});
 await page.evaluate(()=>molipAgent.setVoice(false));
 return page;
}
const target=task.starter_code.replace(edit.before,edit.after);
function assertFrames(frames){
 assert.ok(frames.length>=' + 1000'.length,'typed in visible keystrokes');
 for(const frame of frames){
  assert.match(frame,/\n {4}\}\n\n {4}public static void main/,'`}` keeps its own line in every frame');
  assert.ok(frame.startsWith(task.starter_code.slice(0,task.starter_code.indexOf(edit.before))),'lines above untouched');
 }
}

test('the real editor keeps `}` on its own line while typing and ends with the authored code',async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 try{
  const page=await open(browser,task.starter_code);
  await page.evaluate(a=>molipAgent.run([a]),{...edit,say:undefined});
  const frames=await page.evaluate(()=>frames);
  assertFrames(frames);
  assert.equal(frames[frames.length-1],target,'exact final bytes');
  assert.equal(await page.evaluate(()=>molipCodeEditors.getValue()),target);
  // Rendered lines, as the learner sees them.
  const lines=await page.locator('.cm-line').allTextContents();
  assert.equal(lines[3],'        return fee + 1000;');
  assert.equal(lines[4],'    }');
 }finally{await browser.close();}
});

test('pause/resume, stop and repeated 해설 keep lines whole and restore the student code',async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 try{
  const student=task.starter_code.replace('return fee;','return fee; // 학생 메모 ✅');
  // Used last: a learner's own edit that the narration did not author.
  const page=await open(browser,task.starter_code);
  await page.evaluate(()=>{window.pending=molipAgent.runExplanation([{action:'patch_code',before:'        return fee;\n',after:'        return fee + 1000;\n'}]);});
  await page.waitForFunction(()=>frames.length>=2);
  await page.evaluate(()=>molipAgent.pause());
  const paused=await page.evaluate(()=>frames.length);
  await page.waitForTimeout(250);
  assert.equal(await page.evaluate(()=>frames.length),paused,'no keystroke while paused');
  await page.evaluate(()=>molipAgent.resume());
  await page.waitForFunction(n=>frames.length>n+1,paused);
  await page.evaluate(()=>molipAgent.stop());
  await page.evaluate(()=>pending);
  assert.equal(await page.evaluate(()=>molipCodeEditors.getValue()),task.starter_code,'stop restores the code from before the 해설');
  // Replay twice from the restored code; both runs type the same frames and end exactly.
  const runs=[];
  for(let i=0;i<2;i++){
   await page.evaluate(()=>{frames.length=0;});
   await page.evaluate(a=>molipAgent.run([a]),edit);
   const frames=await page.evaluate(()=>frames.slice());
   assertFrames(frames);
   assert.equal(frames[frames.length-1],target);
   runs.push(frames);
   await page.evaluate(s=>molipCodeEditors.setValue(s),task.starter_code);
  }
  assert.deepEqual(runs[0],runs[1],'repeated playback is identical');
  // A learner edit that the 해설 did not author survives: explanation restores it untouched.
  await page.evaluate(s=>molipCodeEditors.setValue(s),student);
  await page.evaluate(()=>molipAgent.runExplanation([{action:'patch_code',before:'// 학생 메모 ✅',after:'// 고친 메모 ✅'}]));
  assert.equal(await page.evaluate(()=>molipCodeEditors.getValue()),student,'student code restored after the 해설');
 }finally{await browser.close();}
});
