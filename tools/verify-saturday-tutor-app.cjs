// Replay all 32 narrations through the installed app and its real native runners.
// Keep voice on for the first full lesson; captions-only for the exhaustive run.
const {chromium}=require('../target/ui-tests/node_modules/playwright-core');
const fs=require('node:fs');const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.connectOverCDP('http://127.0.0.1:9229');
 try {
  const page=browser.contexts()[0].pages()[0];page.setDefaultTimeout(90000);
  const dir='target/saturday-specials/audit';fs.mkdirSync(dir,{recursive:true});
  if(await page.getByRole('button',{name:'← 코스 수업 목록',exact:true}).count()) await page.getByRole('button',{name:'← 코스 수업 목록',exact:true}).click();
  await page.locator('.course-switcher').getByRole('button',{name:/mq3-course-engineer-saturday-final/}).click();
  const course=JSON.parse(fs.readFileSync('target/saturday-specials/engineer-saturday-final/course.json','utf8'));
  const reports=process.env.TUTOR_RESUME==='1' && fs.existsSync(`${dir}/app-replay.json`)
   ? JSON.parse(fs.readFileSync(`${dir}/app-replay.json`,'utf8')) : [];
  for(const ref of course.lessons){
   const lesson=JSON.parse(fs.readFileSync(`target/saturday-specials/${ref.id}/lesson.json`,'utf8'));
   if(lesson.tasks.every(task=>reports.some(r=>r.lesson===ref.id && r.task===task.id))) continue;
   await page.locator('.lesson-card').filter({has:page.getByRole('heading',{name:ref.title,exact:true})}).getByRole('button',{name:'풀모드 시작',exact:true}).click();
   for(const [index,task] of lesson.tasks.entries()){
    if(reports.some(r=>r.lesson===ref.id && r.task===task.id)) continue;
    await page.locator('.study-navigation').getByRole('button',{name:new RegExp(`문제 ${index+1} ·`)}).click();
    await page.locator('.repository-task .cm-editor').waitFor();
    await page.locator('.problem-pane h2').filter({hasText:task.title}).waitFor();
    await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
    const previous=await page.evaluate(()=>molipCodeEditors.getValue());
    // Start each review from the published prepared code; preserve the saved draft.
    await page.evaluate(source=>molipCodeEditors.setValue(source),task.starter_code);
    const spoken=process.env.TUTOR_AUDIO==='1' && reports.length===0;
    await page.evaluate(({actions,spoken})=>{
     // The first replay uses actual Edge audio. Exhaustive native execution uses
     // short audio fixtures so the checks wait for runs, not sentence duration.
     if(!spoken && !window.__tutorAudioOriginal){
      window.__tutorAudioOriginal=window.Audio;
      window.__tutorSynthesizeOriginal=molipVoice.synthesize;
      window.__tutorEnabledOriginal=molipVoice.enabled;
      window.Audio=class {play(){setTimeout(()=>this.onended?.(),30);return Promise.resolve()}pause(){}};
      molipVoice.synthesize=async()=> 'fixture';molipVoice.enabled=()=>true;
     }
     molipAgent.setVoice(true);
     window.__tutorReport=null;
     molipAgent.run(actions).then(result=>window.__tutorReport=result);
    },{actions:task.narration.filter(a=>a.action!=='submit'),spoken});
    await page.waitForFunction(()=>document.querySelector('.narration-memory figcaption')?.textContent.includes('바꾼 뒤'),null,{timeout:180000});
    await page.screenshot({path:`${dir}/${ref.id}--${task.id}.png`});
    await page.waitForFunction(()=>window.__tutorReport!==null,null,{timeout:180000});
    const result=await page.evaluate(()=>({report:__tutorReport,code:molipCodeEditors.getValue(),output:document.querySelector('.result-pane .output')?.innerText}));
    assert.doesNotMatch(result.report,/오류 -|모르는 동작/,task.id+': '+result.report);
    assert.equal(result.code,task.solution);
    assert.equal(result.output.trim(),task.tests[0].expected.trim());
    reports.push({lesson:ref.id,task:task.id,output:result.output,report:result.report});
    fs.writeFileSync(`${dir}/app-replay.json`,JSON.stringify(reports,null,2));
    await page.evaluate(code=>molipCodeEditors.setValue(code),previous);
    console.log('PASS native app '+ref.id+'/'+task.id);
   }
   await page.getByRole('button',{name:'← 코스 수업 목록',exact:true}).click();
  }
  assert.equal(reports.length,32);
  await page.evaluate(()=>molipAgent.setVoice(true));
 } finally {
  const page=browser.contexts()[0]?.pages()[0];
  if(page) await page.evaluate(()=>{
   if(window.__tutorAudioOriginal){window.Audio=__tutorAudioOriginal;molipVoice.synthesize=__tutorSynthesizeOriginal;molipVoice.enabled=__tutorEnabledOriginal;delete window.__tutorAudioOriginal;}
  }).catch(()=>{});
  await browser.close();
 }
})().catch(e=>{console.error(e);process.exitCode=1});
