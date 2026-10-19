// Measures actual app layout, including small windows and previously saved pane sizes.
const {chromium}=require('../target/ui-tests/node_modules/playwright-core');
const assert=require('node:assert/strict');const path=require('node:path');
(async()=>{
 const browser=await chromium.connectOverCDP('http://127.0.0.1:9229');
 const page=browser.contexts()[0].pages()[0];page.setDefaultTimeout(60000);
 if(!await page.locator('.repository-task').count()){
  await page.locator('.course-switcher button').filter({hasText:'작은 실험'}).click();
  await page.locator('.lesson-card').filter({hasText:'직접 바꾸며 이해하는 출력과 계산'}).waitFor();
  await page.getByRole('button',{name:'학습 시작',exact:true}).click();
 }
 await page.locator('.repository-task .cm-editor').waitFor();
 const cdp=await page.context().newCDPSession(page);
 const measure=()=>page.evaluate(()=>{
  const box=selector=>{let n=document.querySelector(selector),r=n.getBoundingClientRect();return {x:r.x,y:r.y,right:r.right,bottom:r.bottom,width:r.width,height:r.height,clientHeight:n.clientHeight,scrollHeight:n.scrollHeight}};
  return {width:innerWidth,height:innerHeight,documentHeight:document.scrollingElement.scrollHeight,documentWidth:document.scrollingElement.scrollWidth,
   task:box('.repository-task'),problem:box('.problem-pane'),coding:box('.coding-pane'),editor:box('.editor-pane'),result:box('.result-pane'),paging:box('.task-paging'),actions:box('.pane-actions')};
 });
 try{
  for(const [width,height] of [[1920,1080],[1366,768],[1280,720],[1100,720],[1024,600],[800,600],[720,600],[768,1024],[390,844]]){
   await cdp.send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:false});
   await page.evaluate(()=>new Promise(requestAnimationFrame));
   const m=await measure();
   assert.ok(m.documentHeight<=height+1,JSON.stringify(m));
   assert.ok(m.documentWidth<=width+1,JSON.stringify(m));
   for(const name of ['task','problem','coding','editor','result','paging','actions']){
    assert.ok(m[name].bottom<=height+1&&m[name].right<=width+1,`${name} is off screen: ${JSON.stringify(m)}`);
    assert.ok(m[name].height>0,`${name} collapsed`);
   }
   assert.ok(m.result.height>=99&&m.editor.height>=99,JSON.stringify(m));
   assert.ok((await page.locator('.split-row').boundingBox())?.height>0,'editor resize handle must remain available');
   const oldHeight=await page.evaluate(()=>{const pane=document.querySelector('.coding-pane');const old=pane.style.getPropertyValue('--editor-height');pane.style.setProperty('--editor-height','1600px');return old});
   const resized=await measure();
   assert.ok(resized.result.height>=99,`saved editor size hid output: ${JSON.stringify(resized)}`);
   assert.ok(resized.paging.bottom<=height+1);
   await page.evaluate(old=>{const pane=document.querySelector('.coding-pane');if(old)pane.style.setProperty('--editor-height',old);else pane.style.removeProperty('--editor-height')},oldHeight);
   const previousOutput=await page.locator('.result-pane .output').textContent();
   await page.locator('.result-pane .output').evaluate(node=>{node.textContent=('긴 실행 결과를 확인해요. '.repeat(15)+'\n').repeat(80)});
   const long=await measure();assert.ok(long.documentHeight<=height+1,'long output must scroll inside the panel');
   assert.ok(long.result.scrollHeight>long.result.clientHeight);
   await page.locator('.result-pane .output').evaluate((node,value)=>{node.textContent=value},previousOutput);
   console.log(`PASS ${width}x${height}: page=${m.documentHeight}, editor=${Math.round(m.editor.height)}, results=${Math.round(m.result.height)}`);
   if(width===1366)await page.screenshot({path:path.resolve(__dirname,'../target/principles-ui/study-1366x768.png')});
   if(width===390)await page.screenshot({path:path.resolve(__dirname,'../target/principles-ui/study-390x844.png')});
  }
  for(const [width,height] of [[1280,480],[390,600]]){
   await cdp.send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:false});
   const m=await measure();assert.ok(m.documentHeight>height,'tiny screens should scroll');
   assert.ok(m.result.height>=99&&m.editor.height>=99);
   console.log(`PASS ${width}x${height}: readable panels, page scroll allowed`);
  }
 }finally{
  await cdp.send('Emulation.clearDeviceMetricsOverride');await browser.close();
 }
})().catch(error=>{console.error(error);process.exit(1)});
