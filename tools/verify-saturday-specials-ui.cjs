// Inspect our own application and run prepared code. Never submit learner answers.
const {chromium}=require('../target/ui-tests/node_modules/playwright-core');
const assert=require('node:assert/strict');
const fs=require('node:fs');
(async()=>{
 const browser=await chromium.connectOverCDP('http://127.0.0.1:9229');
 const page=browser.contexts()[0].pages()[0];page.setDefaultTimeout(90000);
 const images='target/saturday-specials/screenshots';fs.mkdirSync(images,{recursive:true});
 for(const id of ['engineer-saturday-final','aice-saturday-practice'].filter(id=>!process.env.SATURDAY_ONLY||process.env.SATURDAY_ONLY===id)){
  if(await page.getByRole('button',{name:'← 코스 수업 목록',exact:true}).count())
   await page.getByRole('button',{name:'← 코스 수업 목록',exact:true}).click();
  await page.getByRole('button',{name:'코스 추가·만들기',exact:true}).waitFor();
  const catalog=page.locator('.course-switcher');
  assert.equal(await catalog.getByRole('button',{name:new RegExp('mq3-course-'+id)}).count(),1);
  await catalog.getByRole('button',{name:new RegExp('mq3-course-'+id)}).click();
  await page.locator('.lesson-card').first().waitFor();
  const manifest=JSON.parse(fs.readFileSync('target/saturday-specials/'+id+'/course.json','utf8'));
  await page.getByRole('heading',{name:manifest.title,exact:true}).waitFor();
  assert.equal(await page.locator('.lesson-card').count(),manifest.lessons.length);
  await page.screenshot({path:images+'/'+id+'-catalog.png',fullPage:true});
  await page.locator('.lesson-card').first().getByRole('button',{name:'학습 시작',exact:true}).click();
  await page.locator('.study-navigation').getByRole('button',{name:/^문제 1 ·/}).click();
  await page.locator('.repository-task .cm-editor').waitFor();
  await page.getByRole('button',{name:'코드 실행',exact:true}).click();
  await page.waitForFunction(()=>document.querySelector('.execution-status')?.textContent.includes('실행 완료'),null,{timeout:90000});
  assert.match(await page.locator('.study-progress').innerText(),/필수 문제 0/);
  await page.screenshot({path:images+'/'+id+'-first.png',fullPage:true});
  console.log('PASS published '+id+': '+manifest.lessons.length+' lessons, actual first '+(id.startsWith('engineer')?'C':'Python')+' execution; no submission');
  if(id==='engineer-saturday-final' && manifest.lessons.some(l=>l.id==='sat-engineer-c-memory-strings')){
   await page.getByRole('button',{name:'← 코스 수업 목록',exact:true}).click();
   const extra=manifest.lessons.find(l=>l.id==='sat-engineer-c-memory-strings');
   await page.locator('.lesson-card').filter({has:page.getByRole('heading',{name:extra.title,exact:true})}).getByRole('button',{name:'학습 시작',exact:true}).click();
   await page.locator('.study-navigation').getByRole('button',{name:/^문제 1 ·/}).click();
   await page.getByRole('button',{name:'코드 실행',exact:true}).click();
   await page.waitForFunction(()=>document.querySelector('.execution-status')?.textContent.includes('실행 완료'));
   await page.screenshot({path:images+'/c-memory-first.png',fullPage:true});
   console.log('PASS corrected Notion supplement: new pinned lesson loads and C allocation exercise executes; no submission');
  }
 }
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
