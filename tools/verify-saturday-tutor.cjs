// Exhaustive renderer replay. Audio duration and native runs are isolated here;
// build-saturday-specials separately compiles/runs every actual C/Java program.
const {chromium}=require('../target/ui-tests/node_modules/playwright-core');
const fs=require('node:fs');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 try {
  const page=await browser.newPage({viewport:{width:1470,height:923}});
  const report=[];
  for(const folder of fs.readdirSync('target/saturday-specials').filter(x=>x.startsWith('sat-engineer-'))){
   const lesson=JSON.parse(fs.readFileSync(`target/saturday-specials/${folder}/lesson.json`,'utf8'));
   for(const task of lesson.tasks){
    await page.goto('about:blank');
    await page.setContent(`<main style="display:flex;gap:20px"><section class="problem-pane" style="width:40%"></section><section style="width:60%"><div class="pane-actions"><button>코드 실행</button></div><textarea data-code-editor="${task.language}"></textarea><div class="result-pane" data-execution-id="0" data-execution-state="finished"><textarea aria-label="실행 입력"></textarea><pre class="output">실행 전</pre></div></section></main>`);
    await page.addStyleTag({content:fs.readFileSync('assets/repository-player.css','utf8')});
    await page.addScriptTag({content:fs.readFileSync('assets/editor/editor.bundle.js','utf8')});
    await page.evaluate(starter=>{
     molipCodeEditors.setValue(starter);
     window.observations=[];window.runs=[];
     const timer=window.setTimeout.bind(window);window.setTimeout=(fn,ms,...args)=>timer(fn,Math.min(ms,5),...args);
     window.molipVoice={enabled:()=>true,rate:2,synthesize:async()=> 'fixture'};
     window.Audio=class {play(){observations.push({caption:document.querySelector('.agent-caption')?.textContent,marked:[...document.querySelectorAll('.cm-narration-line')].map(e=>e.textContent),memory:document.querySelector('.narration-memory')?.innerText,spot:document.querySelector('.agent-spotlight')?.getBoundingClientRect().toJSON()});timer(()=>this.onended(),10);return Promise.resolve()}pause(){}};
     document.querySelector('button').onclick=()=>{
      runs.push(molipCodeEditors.getValue());
      const pane=document.querySelector('.result-pane');pane.dataset.executionId=String(Number(pane.dataset.executionId)+1);pane.dataset.executionState='finished';pane.querySelector('.output').textContent='실행 완료';
     };
    },task.starter_code);
    await page.addScriptTag({content:fs.readFileSync('assets/layout/agent.js','utf8')});
    const actions=task.narration.filter(a=>a.action!=='submit');
    const result=await page.evaluate(actions=>molipAgent.run(actions),actions);
    assert.doesNotMatch(result,/오류 -|모르는 동작/,`${folder}/${task.id}: ${result}`);
    const state=await page.evaluate(()=>({observations,runs,source:molipCodeEditors.getValue(),memory:!!document.querySelector('.narration-memory')}));
    assert.equal(state.runs.length,2);
    assert.equal(state.runs[0],task.starter_code);
    assert.equal(state.runs[1],task.solution);
    let code=task.starter_code;
    for(const action of actions){
     if(action.action==='patch_code') code=code.replace(action.before,action.after);
     if(action.lines && (action.text||action.say)){
      const observed=state.observations.find(o=>o.caption===(action.text||action.say));
      assert.ok(observed,task.id+': missing spoken step');
      const wanted=code.split('\n').slice(action.lines[0]-1,action.lines[1]).map(x=>x.trim());
      assert.deepEqual(observed.marked.map(x=>x.trim()),wanted,task.id+': wrong highlighted lines');
     }
     if(action.diagram){
      assert.ok(state.observations.some(o=>o.memory?.includes(action.diagram.title)),task.id+': missing memory view');
     }
    }
    assert.equal(state.memory,false,'clear diagram when playback ends');
    report.push({lesson:folder,task:task.id,spokenSteps:state.observations.length,runs:2,passed:true});
    console.log('PASS '+folder+'/'+task.id);
   }
  }
  fs.mkdirSync('target/saturday-specials/audit',{recursive:true});
  fs.writeFileSync('target/saturday-specials/audit/replay.json',JSON.stringify(report,null,2));
  assert.equal(report.length,32);
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
