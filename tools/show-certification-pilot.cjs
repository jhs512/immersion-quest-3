// Load the published pilot in our own desktop WebView. Do not submit answers.
const {chromium}=require('../target/ui-tests/node_modules/playwright-core');
const fs=require('node:fs');
(async()=>{
 const browser=await chromium.connectOverCDP('http://127.0.0.1:9229');
 const page=browser.contexts()[0].pages()[0];page.setDefaultTimeout(60000);
 await page.getByRole('button',{name:'코스 추가·만들기',exact:true}).waitFor();
 // A stale development-server toast can survive the independent debug launch.
 await page.evaluate(()=>document.getElementById('__dx-toast')?.remove());
 if(await page.getByRole('button',{name:'← 코스 수업 목록',exact:true}).count())
   await page.getByRole('button',{name:'← 코스 수업 목록',exact:true}).click();
 for(const course of ['engineer-practical','aice-associate']){
   await page.getByRole('button',{name:'코스 추가·만들기',exact:true}).click();
   await page.getByLabel('코스 저장소 · owner/repository',{exact:true}).fill('jhs512/mq3-course-'+course);
   await page.getByRole('button',{name:'코스 불러오기',exact:true}).click();
   await page.locator('.lesson-card').waitFor();
 }
 await page.getByRole('button',{name:'학습 시작',exact:true}).click();
 await page.locator('.repository-task .cm-editor').waitFor();
 await page.getByRole('button',{name:'코드 실행',exact:true}).click();
 await page.waitForFunction(()=>document.querySelector('.execution-status')?.textContent.includes('실행 완료'));
 const assert=require('node:assert/strict');
 assert.equal(await page.locator('.study-navigation button').count(),10);
 assert.equal(await page.getByRole('button',{name:'복습모드 시작',exact:true}).count(),0);
 assert.match(await page.locator('body').innerText(),/그대로 실행하고 표를 만나봐요/);
 fs.mkdirSync('target/certification-pilots/screenshots',{recursive:true});
 await page.screenshot({path:'target/certification-pilots/screenshots/aice-first.png',fullPage:true});
 console.log('PASS both course manifests loaded; AICE first exercise open and real Python run complete; no submission');
 await browser.close();
})().catch(error=>{console.error(error);process.exit(1)});
