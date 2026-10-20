const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {chromium,webkit}=require('../../target/ui-tests/node_modules/playwright-core');
for(const engine of ['chromium','webkit'])test(`${engine}: instruction literals select the clicked item including internal spaces`,async()=>{
 const browser=await({chromium,webkit}[engine]).launch(engine==='chromium'?{...(process.platform==='win32'?{channel:'msedge'}:{}),headless:true}:{headless:true,...(process.env.MQ3_WEBKIT_EXECUTABLE?{executablePath:process.env.MQ3_WEBKIT_EXECUTABLE}:{})});
 try{
  const goal=JSON.parse(fs.readFileSync('courses/redesigned/vim-basics.json','utf8')).tasks[1].goal;
  assert.ok(goal.includes('"`첫 메모`"를 입력하세요.'));
  const escape=text=>text.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
  const items=goal.split('\n').filter(line=>/^\d+\. /.test(line)).map(line=>`<li>${escape(line.replace(/^\d+\. /,'')).replace(/`([^`]+)`/g,'<code>$1</code>')}</li>`).join('');
  const css=['app.css','repository-player.css','content-updates.css','player-workspace.css','window-controls.css','compact-toolbar.css','product-ui.css'].map(f=>fs.readFileSync('assets/'+f,'utf8')).join('\n');
  for(const scale of [1,2]){
   const context=await browser.newContext({deviceScaleFactor:scale});const page=await context.newPage();
   for(const width of [1470,735]){
    await page.setViewportSize({width,height:900});
    await page.setContent(`<style>${css}</style><div class="repository-study"><div class="repository-task"><section class="problem-pane"><h2>첫 메모를 입력하고 일반 모드로 돌아오세요</h2><div class="markdown"><p>아직 저장하지 않아요.</p><p><strong>할 일</strong></p><ol>${items}</ol></div></section></div></div>`);
    const point=await page.evaluate(()=>{const code=document.querySelector('li code');const r=document.createRange();r.setStart(code.firstChild,0);r.setEnd(code.firstChild,1);const b=r.getBoundingClientRect();return{x:b.x+b.width/2,y:b.y+b.height/2}});
    await page.mouse.dblclick(point.x,point.y);
    const selected=await page.evaluate(()=>{const selection=getSelection();return{text:selection.toString(),item:selection.anchorNode.parentElement.closest('li')===document.querySelector('li'),focus:selection.focusNode.parentElement.closest('li')===document.querySelector('li')}});
    assert.deepEqual(selected,{text:'첫 메모',item:true,focus:true},`${width}px/${scale}x`);
    await page.evaluate(()=>getSelection().removeAllRanges());
    const second=page.locator('li').nth(1);await second.dblclick({position:{x:15,y:10}});
    assert.equal(await page.evaluate(()=>getSelection().anchorNode.parentElement.closest('li')===document.querySelectorAll('li')[1]),true,'ordinary selection must stay in its own list item');
   }
   await context.close();
  }
 }finally{await browser.close()}
});
