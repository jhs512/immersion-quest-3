const {chromium}=require('../target/ui-tests/node_modules/playwright-core');
const assert=require('node:assert/strict');
const fs=require('node:fs');
(async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 const page=await browser.newPage({viewport:{width:1366,height:768}});page.setDefaultTimeout(180000);
 const errors=[];page.on('pageerror',e=>errors.push(String(e)));
 page.on('requestfailed',r=>console.log('REQUEST FAILED',r.url(),r.failure()?.errorText));
 await page.exposeFunction('reportPreviewStatus',message=>console.log('STATUS',message));
 await page.goto((process.env.PREVIEW_URL||'http://127.0.0.1:8188')+'?lesson=aice-data-first');
 await page.locator('.cm-editor').waitFor();
 await page.waitForFunction(()=>document.querySelectorAll('#tasks option').length===10);
 await page.evaluate(()=>new MutationObserver(()=>window.reportPreviewStatus(document.querySelector('#status').textContent)).observe(document.querySelector('#status'),{childList:true,subtree:true,characterData:true}));
 assert.equal(await page.locator('#tasks option').count(),10);
 await page.getByRole('button',{name:'코드 실행',exact:true}).click();
 await page.waitForFunction(()=>document.querySelector('#run').disabled===false,{},{timeout:180000});
 assert.match(await page.locator('#status').innerText(),/^실행했어요\./,await page.locator('#output').innerText());
 assert.match(await page.locator('#output').innerText(),/방문 자료/);
 assert.equal(await page.locator('#output table').count(),0,'starter must not display the answer table');
 const lesson=JSON.parse(fs.readFileSync('target/web-course-preview/lesson.json','utf8'));
 await page.evaluate(s=>window.molipCodeEditors.setValue(s),lesson.tasks[0].solution);
 await page.getByRole('button',{name:'코드 실행',exact:true}).click();
 await page.waitForFunction(()=>document.querySelector('#status').textContent.startsWith('실행했어요.'));
 assert.equal(await page.locator('#output table tr').count(),7);
 assert.match(await page.locator('#output table').innerText(),/visits/);
 console.log('PASS real browser Python runtime, CSV, starter text, six-row result table');
 await page.getByRole('button',{name:'다음 →',exact:true}).click();
 await page.getByRole('button',{name:'← 이전',exact:true}).click();
 assert.equal(await page.evaluate(()=>window.molipCodeEditors.getValue()),lesson.tasks[0].solution,'draft preserved');
 await page.reload();await page.locator('.cm-editor').waitFor();
 assert.equal(await page.evaluate(()=>window.molipCodeEditors.getValue()),lesson.tasks[0].solution,'reload preserves draft');
 await page.evaluate(()=>window.molipCodeEditors.setValue('while True:\n    pass\n'));
 await page.getByRole('button',{name:'코드 실행',exact:true}).click();
 await page.waitForFunction(()=>document.querySelector('#status').textContent.includes('코드를 실행하고'));
 await page.getByRole('button',{name:'정지',exact:true}).click();
 assert.ok(await page.getByRole('button',{name:'코드 실행',exact:true}).isEnabled());
 await page.evaluate(()=>window.molipCodeEditors.setValue('print(1 / 0)\n'));
 await page.getByRole('button',{name:'코드 실행',exact:true}).click();
 await page.waitForFunction(()=>document.querySelector('#status').textContent.startsWith('오류가 났어요.'));
 assert.match(await page.locator('#output').innerText(),/ZeroDivisionError/);
 await page.getByRole('button',{name:'처음 코드',exact:true}).click();
 await page.getByRole('button',{name:'코드 실행',exact:true}).click();
 await page.waitForFunction(()=>document.querySelector('#status').textContent.startsWith('실행했어요.'));
 console.log('PASS stop infinite execution, restart runtime, error recovery, navigation and drafts');
 for(const [i,task] of lesson.tasks.entries()){
  await page.locator('#tasks').selectOption(String(i));
  await page.evaluate(s=>window.molipCodeEditors.setValue(s),task.solution);
  await page.getByRole('button',{name:'코드 실행',exact:true}).click();
  await page.waitForFunction(()=>document.querySelector('#run').disabled===false);
  assert.match(await page.locator('#status').innerText(),/^실행했어요\./,`${task.id}: ${await page.locator('#output').innerText()}`);
 }
 console.log('PASS all ten lesson solutions execute in the browser runtime');
 const catalog=JSON.parse(fs.readFileSync('target/web-course-preview/catalog.json','utf8'));
 const course=JSON.parse(fs.readFileSync('target/certification-foundations/aice-associate/course.json','utf8'));
 assert.deepEqual(catalog.map(c=>c.id),course.lessons.map(l=>l.id),'preview follows the course order');
 let solved=0,desktopOnly=0;
 for(const entry of catalog.filter(c=>c.id!=='aice-data-first')){
  await page.locator('#lessons').selectOption(entry.id);
  await page.waitForFunction(()=>!document.querySelector('#lessons').disabled);
  assert.equal(await page.locator('#lesson-title').innerText(),entry.title);
  const foundation=JSON.parse(fs.readFileSync('target/web-course-preview/'+entry.path,'utf8'));
  for(const [i,task] of foundation.tasks.entries()){
   await page.locator('#tasks').selectOption(String(i));
   if(task.desktop_only){
    // Desktop-only (TensorFlow) tasks must say so and must not offer a browser run.
    assert.ok(await page.locator('#run').isDisabled(),`${entry.id}/${task.id} run should be disabled`);
    assert.match(await page.locator('#status').innerText(),/데스크톱 앱에서만/);
    desktopOnly++;continue;
   }
   await page.evaluate(s=>window.molipCodeEditors.setValue(s),task.solution);
   await page.getByRole('button',{name:'코드 실행',exact:true}).click();
   await page.waitForFunction(()=>document.querySelector('#run').disabled===false);
   assert.match(await page.locator('#status').innerText(),/^실행했어요\./,`${entry.id}/${task.id}`);
   // Graph lessons must show the drawn figure, not just finish without errors.
   if(task.solution.includes('plt.show()'))assert.ok(await page.locator('#output img').count()>=1,`${entry.id}/${task.id} shows no figure`);
   solved++;
  }
 }
 console.log(`PASS ${solved} solutions of ${catalog.length-1} more AICE lessons; ${desktopOnly} TensorFlow tasks marked desktop-only; independent lesson navigation`);
 await page.goto((process.env.PREVIEW_URL||'http://127.0.0.1:8188'));
 await page.waitForFunction(()=>document.querySelector('#tasks option')&&!document.querySelector('#lessons').disabled);
 assert.equal(await page.locator('#lessons').inputValue(),'aice-python-first');
 assert.equal(await page.locator('#tasks option').count(),9);
 for(const [file,count] of [['plan-aice-associate.html',24],['plan-engineer-practical.html',30]]){
  const plan=await browser.newPage();await plan.goto(new URL(file,page.url()).href);
  assert.equal(await plan.locator('ol>li').count(),count);
  await plan.close();
 }
 await page.locator('#tasks').selectOption('0');
 await page.getByRole('button',{name:'처음 코드',exact:true}).click();
 for(const size of [{width:1366,height:768},{width:390,height:844}]){
  await page.setViewportSize(size);
  const bounds=await page.evaluate(()=>({h:document.documentElement.scrollHeight,w:document.documentElement.scrollWidth,ih:innerHeight,iw:innerWidth}));
  assert.ok(bounds.h<=bounds.ih+1&&bounds.w<=bounds.iw+1,JSON.stringify(bounds));
  await page.screenshot({path:`target/web-course-preview/preview-${size.width}.png`,fullPage:true});
 }
 assert.deepEqual(errors,[]);
 console.log('PASS desktop and narrow viewport; no document overflow or page errors');
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
