// Run only in design-capture's isolated validation account/store. No real GitHub progress is written.
const fs = require('node:fs');
const path = require('node:path');
module.exports = async ({page, shot}) => {
  const courseKey = process.env.MQ3_CAPTURE_COURSE || 'aice';
  const root = path.resolve(__dirname, '../..');
  const slug = courseKey === 'aice' ? 'aice-associate' : 'engineer-practical';
  const key = courseKey === 'aice' ? 'aice-python-start' : 'engineer-c-start';
  const manifest = JSON.parse(fs.readFileSync(path.join(root, `courses/redesigned-courses/${slug}.json`), 'utf8'));
  const lesson = JSON.parse(fs.readFileSync(path.join(root, `courses/redesigned/${key}.json`), 'utf8'));
  const final = lesson.tasks.at(-1);
  const notes = [];
  await page.setViewportSize({width: 1440, height: 900});
  await page.emulateMedia({colorScheme: 'light'});
  await page.waitForSelector('.pilot-toolbox', {timeout: 60000});
  await page.evaluate(() => {document.querySelector('.pilot-toolbox').open = true;});
  await page.getByRole('button', {name: courseKey === 'aice' ? '버전 에' : '버전 정', exact: true}).click();
  await page.evaluate(() => {document.querySelector('.pilot-toolbox').open = false;});
  await page.waitForFunction(n => document.querySelectorAll('.lesson-card').length === n, manifest.lessons.length, {timeout: 60000});
  if (await page.locator('#course-display-name').isVisible().catch(() => false) && !(await page.locator('.course-identity[data-saved="true"]').count())) {
    await page.locator('#course-display-name').fill('과정검증');
    await page.locator('.course-identity button[type=submit]').click();
  }
  const grouped = page.getByRole('button', {name: '분류별', exact: true});
  if (!(await grouped.isEnabled())) throw Error('Category view unavailable');
  if (await grouped.getAttribute('aria-pressed') !== 'true') throw Error('Grouped view is not the default');
  if (await page.locator('.lesson-group-title').count() !== manifest.categories.length) throw Error('Category count differs');
  if (process.env.MQ3_CAPTURE_PHASE === 'restart') {
    const first = page.locator('.lesson-card', {has: page.locator('h3', {hasText: lesson.title})});
    const state = await first.evaluate(el => ({state: el.dataset.state, challenge: el.dataset.challenge, progress: el.querySelector('.lesson-progress')?.textContent}));
    if (state.state !== 'todo' || state.challenge !== 'none' || !state.progress.includes(`0 / ${lesson.tasks.filter(t => t.required !== false).length}`)) throw Error('Reset did not survive restart: ' + JSON.stringify(state));
    await first.scrollIntoViewIfNeeded();
    await shot(`${courseKey}-restart-reset-kept`);
    return ['fresh app process retained the lesson reset: ' + JSON.stringify(state)];
  }
  await shot(`${courseKey}-01-grouped`);
  await page.getByRole('button', {name: '전체 순서', exact: true}).click();
  if (await page.locator('.lesson-card').count() !== manifest.lessons.length) throw Error('Ungrouped view dropped lessons');
  const card = () => page.locator('.lesson-card', {has: page.locator('h3', {hasText: lesson.title})});
  await card().locator('button.primary').click();
  await page.waitForSelector('.lesson-preview', {timeout: 60000});
  notes.push('entry preview ' + (await page.locator('.lesson-preview').innerText()).slice(0,800));
  await shot(`${courseKey}-02-preview`);
  // The lesson orientation is a screen of its own. Select the new final step directly.
  const last = page.locator('.study-navigation button').last();
  await last.click();
  await page.waitForSelector('[data-code-editor]', {state: 'attached', timeout: 60000});
  await page.waitForSelector('.cm-editor', {timeout: 60000});
  await page.waitForFunction(() => window.molipCodeEditors?.setValue);
  await page.evaluate(source => window.molipCodeEditors.setValue(source), final.solution);
  await page.waitForFunction(source => document.querySelector('[data-code-editor]')?.dataset.editorValue === source, final.solution);
  await page.getByRole('button', {name: '제출', exact: true}).click();
  await page.waitForFunction(() => document.querySelector('.result-pane')?.dataset.feedback === 'passed', null, {timeout: 60000});
  await shot(`${courseKey}-03-final-passed`);
  await page.getByRole('button', {name: '수업 목록으로', exact: true}).click();
  await page.waitForFunction(title => [...document.querySelectorAll('.lesson-card')].some(el => el.querySelector('h3')?.textContent.includes(title) && el.dataset.challenge === 'passed'), lesson.title, {timeout: 30000});
  const state = await card().evaluate(el => ({state: el.dataset.state, challenge: el.dataset.challenge, progress: el.querySelector('.lesson-progress')?.textContent, color: getComputedStyle(el.querySelector('.lesson-number')).backgroundColor}));
  if (state.state !== 'challenge' || !state.progress.includes(`1 / ${lesson.tasks.filter(t => t.required !== false).length}`)) throw Error('Challenge clear inflated the practice gauge: ' + JSON.stringify(state));
  notes.push('challenge clear ' + JSON.stringify(state));
  await card().scrollIntoViewIfNeeded();
  await page.emulateMedia({colorScheme: 'dark'});
  await shot(`${courseKey}-04-purple-partial-dark`);
  await card().locator('button.primary').click();
  await page.waitForSelector('.lesson-info-trigger');
  await page.locator('.lesson-info-trigger').click();
  await page.locator('#lesson-info-dialog .lesson-reset-open').click();
  await page.locator('#lesson-info-dialog .lesson-reset-confirm').click();
  await page.waitForFunction(() => document.querySelector('#lesson-info-dialog .study-progress')?.textContent.includes('필수 문제 0 /'), null, {timeout: 10000});
  await shot(`${courseKey}-05-reset`);
  notes.push('reset ' + await page.locator('#lesson-info-dialog .study-progress').innerText());
  return notes;
};
