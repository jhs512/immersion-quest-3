const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {chromium,webkit}=require('../../target/ui-tests/node_modules/playwright-core');
for(const [name,engine] of Object.entries({chromium,webkit}))test(`${name}: direct course dashboard includes enrolled students and problem times`,async()=>{
 const browser=await engine.launch(name==='chromium'&&process.platform==='win32'?{channel:'msedge',headless:true}:{headless:true});
 try{
  const page=await browser.newPage({viewport:{width:1100,height:900}});
  const key={user_id:7,course_id:'course',lesson_id:'lesson'};
  const course={id:'course',title:'테스트 코스',lessons:[{id:'lesson',repository:'owner/lesson',revision:'v1',title:'첫 수업'}]};
  const marker=(kind,value)=>`<!-- mq3-${kind}:${JSON.stringify(value)} -->`;
  const issues=[{number:1,user:{id:7,login:'learner'},body:marker('progress',key),comments:1,html_url:'https://github.com/owner/course/issues/1'},
    {number:2,user:{id:8,login:'newcomer'},body:marker('enrollment',{user_id:8,course_id:'course',name:'참여만한학생'}),comments:0,html_url:'https://github.com/owner/course/issues/2'}];
  await page.route('https://raw.githubusercontent.com/**',route=>route.fulfill({json:route.request().url().endsWith('course.json')?course:{id:'lesson',revision:'v1',tasks:[{id:'task',title:'지금 수량은 얼마인가요?',required:true}]}}));
  await page.route('https://api.github.com/**',route=>route.fulfill({json:route.request().url().includes('/comments')?[{user:{id:7},body:[{id:'start',kind:'started',at:100},{id:'pass',kind:'attempt',passed:true,at:160}].map(e=>marker('event',{...e,key,revision:'v1',task_id:'task'})).join('\n')}]:issues}));
  await page.route('https://mq.test/**',route=>{
   const url=new URL(route.request().url()),last=url.pathname.split('/').pop();
   const file=['app.mjs','model.mjs','style.css'].includes(last)?last:'index.html';
   return route.fulfill({body:fs.readFileSync('site/dashboard/'+file),contentType:file.endsWith('.mjs')?'text/javascript':file.endsWith('.css')?'text/css':'text/html'});
  });
  await page.goto('https://mq.test/immersion-quest-3/dashboard/owner/course/');
  await page.locator('#results:not([hidden])').waitFor();
  assert.equal(await page.locator('.student').count(),2);
  await page.locator('.student').filter({hasText:'@learner'}).locator(':scope > summary').click();
  await page.locator('.lesson-detail > summary').first().click();
  const cells=await page.locator('.task-times').first().locator('tr').nth(1).locator('td').allTextContents();
  assert.equal(cells[0],'지금 수량은 얼마인가요?');assert.equal(cells[1],'완료');
  assert.ok(!cells[2].includes('없음')&&!cells[3].includes('없음'));assert.equal(cells[4],'1회');
  assert.match(page.url(),/\/dashboard\/owner\/course\/$/);
  await page.setViewportSize({width:400,height:800});
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'narrow dashboard overflows');
 }finally{await browser.close();}
});
