const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {chromium,webkit}=require('../../target/ui-tests/node_modules/playwright-core');
for(const engine of ['chromium','webkit'])test(`${engine}: lesson controls share one row with bounded menus`,async()=>{
 const browser=await ({chromium,webkit}[engine]).launch(engine==='chromium'?{channel:'msedge',headless:true}:{headless:true,...(process.env.MQ3_WEBKIT_EXECUTABLE?{executablePath:process.env.MQ3_WEBKIT_EXECUTABLE}:{})});
 try{
  const page=await browser.newPage();
  const styles=['assets/app.css','assets/repository-player.css','assets/content-updates.css','assets/player-workspace.css','assets/window-controls.css','assets/compact-toolbar.css','assets/product-ui.css'].map(f=>fs.readFileSync(f,'utf8')).join('\n');
  for(const width of [1470,980,735,640,400]){
   await page.setViewportSize({width,height:720});
   await page.setContent(`<style>${styles}</style><div class="repository-session"><div class="repository-study is-task"><header class="repository-header"><button class="course-back">← 코스 수업 목록</button><h1>학습 기록을 보고 개선 방법을 판단해요</h1><button class="lesson-info-trigger">0% · 0/8 ⓘ</button><div class="repository-tools"><span class="lesson-account">@jhs512</span><div class="content-update-controls"><details><summary>수업 설정</summary><div class="content-update-menu"><button>수업 업데이트 확인</button><p>이전 답안과 변경 이력을 확인해요.</p></div></details></div><div class="app-window-controls"><button class="window-fullscreen-control">창 모드 · F11</button><details class="app-update-settings"><summary>설정</summary><div class="app-update-menu"><p>최신 버전입니다</p><button>업데이트 확인</button></div></details><button class="app-update-icon">↻</button></div></div></header></div></div>`);
   const boxes=await page.evaluate(()=>{const r=e=>{const b=e.getBoundingClientRect();return{left:b.left,right:b.right,top:b.top,bottom:b.bottom,height:b.height}};return{header:r(document.querySelector('.repository-header')),controls:[...document.querySelectorAll('.course-back,.lesson-info-trigger,.content-update-controls>details>summary,.app-window-controls>button,.app-update-settings>summary')].map(r)}});
   assert.ok(boxes.header.height<=42,`${width}: header must remain one row`);
   for(const b of boxes.controls)assert.ok(b.left>=0&&b.right<=width&&b.top>=boxes.header.top&&b.bottom<=boxes.header.bottom,`${width}: ${JSON.stringify(boxes)}`);
   for(const selector of ['.content-update-controls>details>summary','.app-update-settings>summary']){
    await page.locator(selector).click();
    const b=await page.locator(selector.startsWith('.content')?'.content-update-menu':'.app-update-menu').boundingBox();
    assert.ok(b.x>=0&&b.x+b.width<=width&&b.y+b.height<=720,`${width}: popup overflows`);
    await page.locator(selector).click();
   }
   if(width===1470){fs.mkdirSync('target/compact-toolbar',{recursive:true});await page.screenshot({path:`target/compact-toolbar/${engine}.png`})}
  }
 }finally{await browser.close()}
});
