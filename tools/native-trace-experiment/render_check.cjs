// C++ and Rust trace documents on the real 코드 흐름 보기 viewer (assets/java-trace, assembled as
// src/java_trace.rs::viewer_script does), in Edge: the seeked step's stack, objects, arrows and notes.
// Usage: node tools/native-trace-experiment/render_check.cjs <check dir from check_fixtures.py> <screenshot dir>
const fs=require('node:fs');
const path=require('node:path');
const assert=require('node:assert/strict');
const {chromium}=require('../../target/ui-tests/node_modules/playwright-core');

const [checkDir,shots]=process.argv.slice(2);
fs.mkdirSync(shots,{recursive:true});
const viewer=()=>{
 const highlight=fs.readFileSync('assets/java-trace/core/highlight.js','utf8').replaceAll('export function','function');
 const render=fs.readFileSync('assets/java-trace/core/render.js','utf8').replace("import { highlightLines } from './highlight.js';",'')
  .replaceAll('export function','function').replaceAll('export class','class');
 return `(()=>{if(window.MqTraceView)return;\nconst highlightLines=(()=>{\n${highlight}\nreturn highlightLines;})();\n(()=>{\n${render}\nwindow.MqTraceView=TraceView;})();\n})();\n`+fs.readFileSync('assets/java-trace/code-flow.js','utf8');
};

const CASES=[
 {fixture:'ownership.rs',line:12,nth:1,expect:s=>{
  assert.ok(s.text.includes('옮겨진 값(move)'),'moved binding shown as a note');
  assert.deepEqual(s.stack,['main26행','take12행'],'caller and callee frames');
  assert.ok(s.objects>=2&&s.arrows>=2,`objects ${s.objects} arrows ${s.arrows}`);}},
 {fixture:'edge.rs',line:32,nth:1,expect:s=>{
  assert.ok(s.text.includes('옮겨진 값(move)'),'name moved inside the loop');
  assert.ok(s.text.includes('가려짐'),'shadowed x labelled');}},
 {fixture:'lifetime.cpp',line:30,nth:1,expect:s=>{
  assert.ok(s.text.includes('해제된 동적 메모리'),'deleted pointer is freed memory');
  assert.ok(s.text.includes('→ stock'),'reference drawn as a pointer to stock');}},
 {fixture:'edge.cpp',line:42,nth:1,expect:s=>{
  assert.ok(s.text.includes('→ b')&&s.text.includes('→ a'),'cycle a.next/b.next');
  assert.ok(s.text.includes('→ pair.first'),'nested first field keeps its name');
  assert.ok(s.text.includes('선언 때 초기값 없음'),'uninitialized badge');}},
];

(async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 const results=[];
 try {
  for(const c of CASES){
   const doc=JSON.parse(fs.readFileSync(path.join(checkDir,c.fixture,'native_flow.json'),'utf8'));
   const page=await browser.newPage({viewport:{width:1500,height:1000}});
   const errors=[];page.on('pageerror',e=>errors.push(String(e)));
   await page.setContent('<main></main>');
   await page.addStyleTag({content:fs.readFileSync('assets/java-trace/code-flow.css','utf8')+fs.readFileSync('assets/app.css','utf8')});
   await page.addScriptTag({content:viewer()});
   const seen=await page.evaluate(({doc,line,nth})=>{
    const token=mqCodeFlow.loading();
    mqCodeFlow.show(token,doc);
    const at=mqCodeFlow.seek({line,nth});
    const dialog=document.getElementById('code-flow-dialog');
    return {at,state:mqCodeFlow.state(),
     stack:[...dialog.querySelectorAll('.tv-frames .tv-frame-title')].map(n=>n.textContent.trim()).filter(t=>t!=='전역 변수'&&t!=='static 변수'),
     objects:dialog.querySelectorAll('.tv-heap .tv-object').length,
     arrows:dialog.querySelectorAll('svg.tv-arrows path').length,
     text:dialog.querySelector('.code-flow-view').innerText};
   },{doc,line:c.line,nth:c.nth});
   await page.waitForTimeout(150);
   await page.screenshot({path:path.join(shots,c.fixture+'.png'),fullPage:false});
   assert.deepEqual(errors,[],c.fixture+' page errors');
   assert.equal(seen.state.state,'shown',c.fixture+' '+seen.state.message);
   assert.ok(seen.at,c.fixture+' seek found the step');
   c.expect(seen);
   results.push({fixture:c.fixture,step:seen.at,stack:seen.stack,objects:seen.objects,arrows:seen.arrows});
   await page.close();
  }
 } finally { await browser.close(); }
 console.log(JSON.stringify(results,null,1));
})().catch(e=>{console.error(e);process.exit(1);});
