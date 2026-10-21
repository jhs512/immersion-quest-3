const test=require('node:test');
const assert=require('node:assert/strict');
const path=require('node:path');
const {chromium,webkit}=require(path.resolve('target/ui-tests/node_modules/playwright-core'));
for(const [name,engine] of Object.entries({chromium,webkit})){
 test(`${name}: Git graph stays readable and retires a reused reset canvas`,async()=>{
  const browser=await engine.launch({headless:true});
  try{
   const page=await browser.newPage();
   await page.setContent('<details open data-git-graph-owner="old" class="git-graph-panel" style="width:300px;height:220px"><summary>커밋 그래프</summary><div class="git-graph-body"><p class="git-graph-status"></p><div class="git-graph-canvas"></div><p class="git-graph-detail"></p></div></details>');
   await page.addStyleTag({path:path.resolve('assets/git-graph.css')});
   await page.addScriptTag({path:path.resolve('assets/terminal/terminal.bundle.js')});
   const result=await page.evaluate(async()=>{
    const commits=Array.from({length:35},(_,i)=>({id:`commit${i}`,parents:i<34?[`commit${i+1}`]:[],subject:`기록 ${i}`}));
    const state={initialized:true,head:'commit0',branch:'main',commits,references:[{id:'commit0',name:'main',remote:false}],changes:[],merging:false,truncated:false};
    const root=document.querySelector('details'),canvas=root.querySelector('.git-graph-canvas');
    mq3GitGraphs.update('old',state);
    await new Promise(r=>setTimeout(r,100));
    const before=canvas._cyreg.cy;
    const font=before.nodes()[0].numericStyle('font-size')*before.zoom();
    // Dioxus can retain the DOM while a keyed terminal changes owner. A late
    // cleanup for the old session must never destroy the new session's canvas.
    root.dataset.gitGraphOwner='new';
    mq3GitGraphs.update('new',{...state,commits:[],head:null,references:[]});
    const current=canvas._cyreg.cy;
    mq3GitGraphs.dispose('old');
    await new Promise(r=>setTimeout(r,50));
    return {font,oldDestroyed:before.destroyed(),currentDestroyed:current.destroyed(),canvasCount:canvas.querySelectorAll('canvas').length,retired:mq3GitGraphs.snapshot('old')===undefined,count:root.dataset.graphCount};
   });
    assert.ok(result.font>=11,`Graph labels shrank to ${result.font}px`);
   assert.equal(result.oldDestroyed,true,'reset must retire the previous renderer before reusing its canvas');
   assert.equal(result.currentDestroyed,false);
   assert.ok(result.canvasCount>0,'new renderer disappeared after old-session cleanup');
   assert.equal(result.retired,true);assert.equal(result.count,'0');
  }finally{await browser.close();}
 });
 test(`${name}: reset clears the visible graph immediately and rejects a late old snapshot`,async()=>{
  const browser=await engine.launch({headless:true});
  try{
   const page=await browser.newPage();
   await page.setContent('<details open data-git-graph-owner="old" class="git-graph-panel" style="width:300px;height:220px"><summary>커밋 그래프</summary><div class="git-graph-body"><p class="git-graph-status"></p><div class="git-graph-canvas"></div><p class="git-graph-detail"></p></div></details>');
   await page.addScriptTag({path:path.resolve('assets/terminal/terminal.bundle.js')});
   const result=await page.evaluate(()=>{
    const state={initialized:true,head:'old-commit',branch:'old-branch',commits:[{id:'old-commit',parents:[],subject:'old'}],references:[],changes:[]};
    const root=document.querySelector('details');
    mq3GitGraphs.update('old',state);
    mq3GitGraphs.reset?.('old');
    mq3GitGraphs.update('old',state);
    return {count:root.dataset.graphCount,text:root.innerText,retired:mq3GitGraphs.snapshot('old')===undefined};
   });
   assert.equal(result.count,'0','reset must clear the previous drawing before the next terminal starts');
   assert.equal(result.retired,true);assert.ok(!result.text.includes('old-branch'));
  }finally{await browser.close();}
 });
 test(`${name}: graph uses the panel height and expands into a readable workspace`,async()=>{
  const browser=await engine.launch({headless:true});
  try{
   const page=await browser.newPage({viewport:{width:1280,height:720}});
   await page.setContent('<details open data-git-graph-owner="large" class="git-graph-panel" style="height:500px"><summary>커밋 그래프</summary><div class="git-graph-body"><div class="git-graph-tools"><button data-graph-action="expand">크게 보기</button><button data-graph-action="focus">현재 위치</button></div><p class="git-graph-status"></p><div class="git-graph-canvas"></div><p class="git-graph-detail"></p></div></details>');
   await page.addStyleTag({path:path.resolve('assets/git-graph.css')});
   await page.addScriptTag({path:path.resolve('assets/terminal/terminal.bundle.js')});
   await page.evaluate(()=>mq3GitGraphs.update('large',{initialized:true,head:'abc',branch:'main',commits:[{id:'abc',parents:[],subject:'메모를 저장해요'}],references:[{id:'abc',name:'main'}],changes:[]}));
   assert.ok((await page.locator('.git-graph-canvas').boundingBox()).height>=300,'canvas wasted the panel height');
   // Production panels have their height assigned by the terminal row.
   await page.locator('details').evaluate(root=>root.style.height='');
   await page.click('[data-graph-action="expand"]');
   const large=await page.locator('.git-graph-canvas').boundingBox();
   assert.ok(large.width>1000&&large.height>400,JSON.stringify(large));
   if(process.env.MQ3_GRAPH_SCREENSHOTS)await page.screenshot({path:`target/git-graph-${name}.png`});
   await page.keyboard.press('Escape');
   assert.equal(await page.locator('details').evaluate(root=>root.classList.contains('is-expanded')),false);
   assert.equal(await page.locator('[data-graph-action="expand"]').getAttribute('aria-pressed'),'false');
   await page.locator('summary').click();
   assert.equal(await page.locator('.git-graph-canvas').isVisible(),false,'collapsed graph still occupies space');
  }finally{await browser.close();}
 });
}
