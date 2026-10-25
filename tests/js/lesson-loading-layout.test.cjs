const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {chromium,webkit}=require('../../target/ui-tests/node_modules/playwright-core');
const escape=text=>text.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');

for(const engine of ['chromium','webkit'])test(`${engine}: long plot examples stay within the lesson workspace on load`,async()=>{
 const options=engine==='chromium'?{channel:'msedge',headless:true}:{headless:true,...(process.env.MQ3_WEBKIT_EXECUTABLE?{executablePath:process.env.MQ3_WEBKIT_EXECUTABLE}:{})};
 const browser=await({chromium,webkit}[engine]).launch(options);
 try{
  const lesson=JSON.parse(fs.readFileSync('courses/redesigned/aice-plots.json','utf8'));
  const styles=['assets/app.css','assets/repository-player.css','assets/player-workspace.css','assets/product-ui.css','assets/window-controls.css','assets/station.css'].map(file=>fs.readFileSync(file,'utf8')).join('\n');
  for(const width of [1470,980,735]){
   const page=await browser.newPage();
   await page.setViewportSize({width,height:747});
   const task=lesson.tasks[0];
   await page.setContent(`<style>${styles}</style><div class="app-window-controls">설정</div><div class="repository-session"><div class="content-update-controls">수업 설정</div><div class="repository-study is-task"><header class="repository-header"><h1>${lesson.title}</h1></header><div class="study-progress">학습 진행</div><nav class="study-navigation">${lesson.tasks.map(t=>`<button>${t.title}</button>`).join('')}</nav><article class="lesson repository-task"><section class="problem-pane"><h2>${task.title}</h2></section><div class="split-col"></div><section class="coding-pane"><div class="pane-heading">main.py</div><div class="editor-pane interaction-example-editor" style="display:grid;grid-template-rows:minmax(0,2fr) minmax(0,3fr);gap:6px"><textarea class="code-editor" data-code-editor="python" readonly>${escape(task.example_code)}</textarea><div class="interaction-example-answer" style="min-height:0;overflow:hidden"><fieldset class="answer-interaction"><legend>답을 골라요</legend>${task.interaction.options.map(o=>`<label class="answer-option"><input type="radio" name="answer"><span>${o.text}</span></label>`).join('')}</fieldset></div></div><div class="split-row"></div><div class="result-pane">실행 결과</div></section></article></div></div>`);
   await page.addScriptTag({content:fs.readFileSync('assets/editor/editor.bundle.js','utf8')});
   await page.locator('.cm-content').waitFor();
   const boxes=await page.evaluate(()=>{
    const rect=s=>{const r=document.querySelector(s).getBoundingClientRect();return{left:r.left,right:r.right,top:r.top,bottom:r.bottom,width:r.width,height:r.height}};
    return{pane:rect('.coding-pane'),editor:rect('.cm-editor'),answer:rect('.answer-interaction'),header:rect('.repository-header')};
   });
   assert.ok(boxes.header.top>=0&&boxes.header.bottom<747,JSON.stringify(boxes));
   for(const key of ['editor','answer'])assert.ok(boxes[key].width>0&&boxes[key].left>=boxes.pane.left&&boxes[key].right<=boxes.pane.right,`${engine}/${width}: ${key} overflows: ${JSON.stringify(boxes)}`);
   await page.close();
  }
 }finally{await browser.close();}
});
