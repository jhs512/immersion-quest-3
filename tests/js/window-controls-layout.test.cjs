const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {chromium}=require('../../target/ui-tests/node_modules/playwright-core');

test('window controls stay in their own row and settings open inside the viewport',async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 try{
  for(const scale of [1,2]){
   const context=await browser.newContext({deviceScaleFactor:scale});
   const page=await context.newPage();
   for(const width of [1470,980,735,640,360]){
    await page.setViewportSize({width,height:720});
    const styles=['assets/app.css','assets/repository-player.css','assets/content-updates.css','assets/player-workspace.css','assets/window-controls.css'].filter(file=>fs.existsSync(file)).map(file=>fs.readFileSync(file,'utf8')).join('\n');
    await page.setContent(`<style>${styles}</style><div class="app-window-controls"><button class="window-fullscreen-control">창 모드 · F11</button><details class="app-update-settings"><summary>설정</summary><div class="app-update-menu"><p>최신 버전입니다 · 빌드 12</p><button>업데이트 확인</button><button disabled>새 버전 설치</button></div></details><button class="app-update-icon" aria-label="앱 업데이트 확인">↻</button></div><div class="repository-session"><div class="content-update-controls"><details><summary>수업 설정</summary></details></div><div class="repository-study is-task"><header class="repository-header"><h1>수업</h1></header></div></div>`);
    const layout=await page.evaluate(()=>{
     const rect=selector=>{const r=document.querySelector(selector).getBoundingClientRect();return {left:r.left,right:r.right,top:r.top,bottom:r.bottom,height:r.height}};
     return {bar:rect('.app-window-controls'),settings:rect('.app-update-settings'),update:rect('.app-update-icon'),fullscreen:rect('.window-fullscreen-control'),lesson:rect('.content-update-controls'),session:rect('.repository-session')};
    });
    for(const control of ['settings','update','fullscreen']){
     const r=layout[control];
     assert.ok(r.top>=layout.bar.top&&r.bottom<=layout.bar.bottom,`${control} overflows toolbar at ${width}px/${scale}x: ${JSON.stringify(layout)}`);
     assert.ok(r.left>=0&&r.right<=width,`${control} outside window`);
    }
    assert.ok(layout.settings.right<=layout.update.left&&layout.update.right<=layout.fullscreen.left,'controls overlap or change order');
    assert.ok(layout.lesson.top>=layout.bar.bottom,'toolbar covers lesson settings');
    if(width>=700)assert.ok(layout.session.bottom<=720,'toolbar must share the lesson viewport budget');
    await page.locator('.app-update-settings>summary').click();
    const menu=await page.locator('.app-update-menu').boundingBox();
    assert.ok(menu.x>=0&&menu.x+menu.width<=width&&menu.y+menu.height<=720,`settings menu outside viewport at ${width}px: ${JSON.stringify(menu)}`);
   }
   await context.close();
  }
 }finally{await browser.close()}
});
