// Inspect actual published course composition in our own desktop app. Never submit.
const {chromium}=require('../target/ui-tests/node_modules/playwright-core');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.connectOverCDP('http://127.0.0.1:9229');
 const page=browser.contexts()[0].pages()[0];page.setDefaultTimeout(60000);
 if(await page.getByRole('button',{name:'← 코스 수업 목록',exact:true}).count())await page.getByRole('button',{name:'← 코스 수업 목록',exact:true}).click();
 await page.getByRole('button',{name:'코스 추가·만들기',exact:true}).waitFor();
 await page.evaluate(()=>document.getElementById('__dx-toast')?.remove());
 const fs=require('node:fs');
 const built=id=>JSON.parse(fs.readFileSync(`target/certification-foundations/${id}/course.json`,'utf8'));
 for(const id of ['engineer-practical','aice-associate']){
  const course=built(id),count=course.lessons.length,title=course.lessons[0].title;
  await page.getByRole('button',{name:'코스 추가·만들기',exact:true}).click();
  await page.getByLabel('코스 저장소 · owner/repository',{exact:true}).fill('jhs512/mq3-course-'+id);
  await page.getByRole('button',{name:'코스 불러오기',exact:true}).click();
  await page.locator('.lesson-card').first().getByRole('heading',{name:title,exact:true}).waitFor();
  assert.equal(await page.locator('.lesson-card').count(),count);
  assert.match(await page.locator('.lesson-card').first().innerText(),new RegExp(title));
 }
 await page.getByRole('button',{name:'풀모드 시작',exact:true}).first().click();
 await page.locator('.repository-task .cm-editor').waitFor();
 assert.equal(await page.locator('.study-navigation button').count(),9);
 assert.match(await page.locator('.problem-pane').innerText(),/코드를 그대로 실행해 봐요/);
 assert.equal(await page.getByRole('button',{name:'복습모드 시작',exact:true}).count(),0);
 console.log('PASS separate course composition, correct first lessons, preserved later lessons, optional review, no answer submitted');
 await browser.close();
})().catch(error=>{console.error(error);process.exit(1)});
