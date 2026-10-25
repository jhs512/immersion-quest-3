// Real app, isolated validation store, current backend manifest and real grading.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');

module.exports = async ({page, shot, dataDir}) => {
  const from = Number(process.env.MQ3_JOURNEY_FROM || 26);
  const root = path.resolve(__dirname, '../..');
  const course = JSON.parse(fs.readFileSync(path.join(root, 'courses/redesigned-courses/java-backend.json')));
  const button = name => page.getByRole('button', {name, exact:true});
  const back = async () => { await button('← 코스 수업 목록').click(); await page.waitForSelector('.course-catalog'); };
  const open = async index => {
    const card = page.locator('.lesson-card').nth(index);
    await card.locator('button', {hasText:'학습 시작'}).click();
    await page.waitForSelector('.lesson-preview', {timeout:60000});
  };
  const expectPreview = async () => {
    for (const text of ['배우는 것','마지막 도전','이렇게 진행해요','가정과 제약','생각해 볼 질문'])
      assert.equal(await page.locator('.lesson-preview h3', {hasText:text}).count(), 1, text);
    assert.equal(await page.locator('.repository-task').count(), 0, 'no grading/workspace mounted on preview');
    assert.equal(await page.locator('.study-navigation [aria-current=step]').count(), 1, 'one current item');
  };
  await page.setViewportSize({width:1440,height:900});
  await page.waitForSelector('.pilot-toolbox', {timeout:60000});
  await page.waitForFunction(() => document.querySelector('.lesson-card')?.textContent.includes('pilot-a'), null, {timeout:60000});
  await page.evaluate(() => document.querySelector('.pilot-toolbox').open = true);
  await button('버전 본').click();
  await page.evaluate(() => document.querySelector('.pilot-toolbox').open = false);
  await page.waitForFunction(() => document.querySelectorAll('.lesson-card').length === 34, null, {timeout:60000});
  console.log('real backend course: 34 lessons loaded');
  await page.locator('#course-display-name').fill('수업여정검증');
  await page.locator('.course-identity button[type=submit]').click();
  await page.waitForFunction(() => [...document.querySelectorAll('.lesson-card button')].some(b => b.textContent.includes('학습 시작') && !b.disabled));
  await button('분류별').click();
  assert.equal(await page.locator('.lesson-card').count(), 34);
  await shot('01-grouped-course');
  await page.emulateMedia({colorScheme:'dark'});
  await shot('01b-grouped-course-dark');
  await page.emulateMedia({colorScheme:'light'});
  await button('전체 순서').click();
  for (let i=from===26?0:from;i<34;i++) {
    await open(i); await expectPreview();
    if (i===0) await shot('02-preview-terminal');
    if (i===26) {
      await page.setViewportSize({width:640,height:760});
      await shot('03-preview-narrow');
      assert(await page.locator('.lesson-preview').evaluate(e => e.scrollWidth <= e.clientWidth+1));
      assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth+1), 'narrow page has no sideways scroll');
      await page.emulateMedia({colorScheme:'dark'});
      await shot('04-preview-dark');
      await page.emulateMedia({colorScheme:'light'});
      await page.setViewportSize({width:390,height:844});
      await shot('05-preview-mobile-light');
      assert(await page.locator('.lesson-preview').evaluate(e => e.scrollWidth <= e.clientWidth+1), 'mobile preview fits');
      assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth+1), 'mobile page has no sideways scroll');
      await page.setViewportSize({width:1440,height:900});
    }
    await back();
    console.log(`preview ${i+1}/34 verified`);
  }
  // Showing previews records nothing: the next-station panel still offers lesson 1 as not started.
  const nextStation = async () => page.locator('.next-station').evaluate(e => ({
    state:e.dataset.state, ring:e.querySelector('.next-station-ring')?.textContent, action:e.querySelector('.next-station-start')?.textContent}));
  const afterPreviews = await nextStation();
  if (from===26) assert.deepEqual([afterPreviews.ring, afterPreviews.action], ['1','이 수업 시작'], 'preview-only visits created a learning record');
  console.log('after previews: '+JSON.stringify(afterPreviews));
  const solved=[];
  let resumedAfterRecord=null;
  let expected=0;
  for (let i=from;i<34;i++) {
    const ref=course.lessons[i];
    const key=ref.repository.replace('jhs512/mq3-lesson-redesigned-', '');
    const lesson=JSON.parse(fs.readFileSync(path.join(root,'courses/redesigned',key+'.json')));
    expected += lesson.tasks.length;
    await open(i);
    await page.locator('.lesson-preview').getByRole('button',{name:'학습 시작',exact:true}).click();
    await page.waitForSelector('.repository-task');
    await page.evaluate(() => {molipAgent.setVoice(false); molipAgent.setRate?.(3);});
    for (let n=0;n<lesson.tasks.length;n++) {
      const task=lesson.tasks[n];
      await page.locator(`.study-navigation button[data-step-id="${task.id}"]`).click();
      await page.waitForFunction(id=>document.querySelector('.repository-task')?.dataset.taskId===id,task.id);
      await page.waitForFunction(()=>!!window.molipCodeEditors?.getValue());
      if (n===0 && !process.env.MQ3_JOURNEY_FAST) {
        const initial=await page.evaluate(()=>molipCodeEditors.getValue());
        await button('해설 재생').click();
        await page.waitForFunction(()=>molipAgent.running);
        await page.waitForFunction(()=>!molipAgent.running && document.querySelector('.repository-task')?.dataset.narrating==='false',null,{timeout:120000});
        assert.equal(await page.evaluate(()=>molipCodeEditors.getValue()),initial,'narration restores draft');
      }
      await page.evaluate(source=>molipCodeEditors.setValue(source),task.solution);
      await page.waitForFunction(source=>document.querySelector('[data-code-editor]')?.dataset.editorValue===source,task.solution);
      await button('제출').click();
      await page.waitForFunction(()=>document.querySelector('.result-pane')?.dataset.feedback==='passed',null,{timeout:90000});
      solved.push(task.id);
      console.log(`lesson ${i+1}, step ${n+1}: normal submit passed`);
      // Close the ordinary success dialog before selecting the next step.
      if (await page.locator('.task-passed-dialog').count()) await page.locator('.task-passed-dialog').getByRole('button',{name:'여기 머물기'}).click();
      if (i===from && n===0) {
        // Positive control: a real submit is a learning record, so the same panel now resumes this lesson.
        await back();
        resumedAfterRecord = await nextStation();
        assert.deepEqual([resumedAfterRecord.ring, resumedAfterRecord.action], [String(from+1),'이어서 학습'], 'a real submit must be recorded');
        await open(i);
        await page.locator('.lesson-preview').getByRole('button',{name:'학습 시작',exact:true}).click();
        await page.waitForSelector('.repository-task');
        await page.evaluate(() => {molipAgent.setVoice(false); molipAgent.setRate?.(3);});
        const reopened=Date.now();
        await page.waitForFunction(id=>document.querySelector(`.study-navigation button[data-step-id="${id}"]`)?.dataset.completed==='true',task.id,{timeout:30000})
          .catch(()=>assert.fail('passed step kept after reopening'));
        console.log(`passed step shown as completed ${Date.now()-reopened}ms after reopening`);
      }
    }
    await shot(`lesson-${i+1}-graded`);
    await back();
  }
  assert.equal(solved.length,expected);
  return {afterPreviews,resumedAfterRecord,previewed:from===26?34:34-from,firstLesson:from+1,graded:solved.length,solved,dataDir};
};
