// Major learner and teacher flows on the real course, for before/after design captures.
// Every step is attempted; a failing step is recorded in notes instead of stopping the run.
const fs = require('node:fs');
const path = require('node:path');

module.exports = async ({page, shot, dataDir}) => {
  const notes = [];
  const step = async (label, run) => {
    try { await run(); notes.push(`ok: ${label}`); }
    catch (error) { notes.push(`FAIL: ${label}: ${String(error.message || error).split('\n')[0]}`); }
  };
  const button = (name) => page.getByRole('button', {name, exact: true});
  const desktop = async () => page.setViewportSize({width: 1440, height: 900});
  const narrow = async () => page.setViewportSize({width: 820, height: 760});
  const toolbox = async (open) => page.evaluate((open) => { const t = document.querySelector('.pilot-toolbox'); if (t) t.open = open; }, open);
  const toCatalog = async () => {
    for (const name of ['← 코스 수업 목록', '← 도전 과제']) if (await button(name).count()) { await button(name).click(); break; }
    await page.waitForSelector('.course-catalog');
  };
  const openLesson = async (index) => {
    await toCatalog();
    if (await button('수업 목록').count()) await button('수업 목록').click();
    const card = page.locator('.lesson-card').nth(index);
    await card.scrollIntoViewIfNeeded();
    await card.locator('button', {hasText: '학습 시작'}).click();
    await page.waitForSelector('.study-navigation', {timeout: 60000});
  };
  const openTask = async (number) => {
    await page.locator('.study-navigation button', {hasText: `문제 ${number} ·`}).first().click();
    await page.waitForSelector('.repository-task');
  };

  await desktop();
  await page.waitForSelector('.pilot-toolbox', {timeout: 60000});
  // 관리자 자동 풀이 needs edit permission; in validation it is a file in this run's own folder.
  fs.writeFileSync(path.join(dataDir, 'pilot-course-reviewer'), '');
  await toolbox(true);
  await button('버전 본').click();
  await toolbox(false);
  await page.waitForFunction(() => document.querySelectorAll('.lesson-card').length > 30, null, {timeout: 60000});

  await step('catalog before name', async () => { await shot('01-catalog-name-required'); });
  await step('save course name', async () => {
    await page.locator('#course-display-name').fill('디자인검증');
    await page.locator('.course-identity button[type=submit]').click();
    await page.waitForFunction(() => [...document.querySelectorAll('.lesson-card button')].some(b => b.textContent.includes('학습 시작') && !b.disabled), null, {timeout: 30000});
    await shot('02-catalog-ready');
  });
  await step('catalog scrolled list', async () => {
    await page.locator('.lesson-card').nth(26).scrollIntoViewIfNeeded();
    await shot('03-catalog-list-end');
  });
  await step('catalog keyboard focus', async () => {
    await page.locator('.lesson-card').nth(1).locator('button', {hasText: '학습 시작'}).focus();
    await page.keyboard.press('Shift+Tab');
    await page.keyboard.press('Tab');
    await shot('04-catalog-focus');
  });
  await step('challenges view', async () => {
    await page.evaluate(() => scrollTo(0, 0));
    await button('도전 과제').click();
    await page.waitForTimeout(1500);
    await shot('05-challenges');
    await button('수업 목록').click();
  });
  await step('search empty', async () => {
    await page.locator('.course-search input').fill('없는과정');
    await shot('06-course-search-empty');
    await page.locator('.course-search input').fill('');
  });
  await step('narrow catalog', async () => { await narrow(); await page.evaluate(() => scrollTo(0, 0)); await shot('07-catalog-narrow'); await desktop(); });

  await step('open java values lesson with loading stages', async () => {
    await toCatalog();
    const card = page.locator('.lesson-card').nth(1);
    await card.scrollIntoViewIfNeeded();
    await card.locator('button', {hasText: '학습 시작'}).click();
    await page.waitForSelector('.lesson-launch-status', {timeout: 5000}).then(() => shot('09-lesson-launching', {settle: 0})).catch(() => {});
    await page.waitForSelector('.study-navigation', {timeout: 60000});
    await shot('10-lesson-open');
  });
  await step('code problem', async () => {
    await openTask(1);
    await page.waitForSelector('.cm-editor', {timeout: 30000});
    await shot('11-problem-editor');
  });
  await step('run code', async () => {
    await page.locator('.repository-task [data-shortcut-action="run"]').click();
    await page.waitForFunction(() => ['finished', 'failed'].includes(document.querySelector('.result-pane')?.dataset.executionState), null, {timeout: 90000});
    await shot('12-run-result');
  });
  await step('submit incorrect', async () => {
    await page.locator('.repository-task [data-shortcut-action="submit"]').click();
    await page.waitForFunction(() => ['passed', 'incorrect', 'error'].includes(document.querySelector('.result-pane')?.dataset.feedback), null, {timeout: 90000});
    await shot('13-submit-feedback');
    if (await button('여기 머물기').count()) await button('여기 머물기').click();
  });
  await step('passed dialog', async () => {
    await page.locator('.answer-option', {hasText: /^\s*2\s*$/}).first().click();
    await page.locator('.repository-task [data-shortcut-action="submit"]').click();
    await page.waitForSelector('.task-passed-dialog', {timeout: 60000});
    await shot('13b-passed-dialog');
    await button('여기 머물기').click();
  });
  await step('lesson info dialog', async () => {
    await page.locator('.lesson-info-trigger').click();
    await page.waitForFunction(() => document.getElementById('lesson-info-dialog')?.open);
    await shot('14-lesson-info');
    await page.keyboard.press('Escape');
  });
  await step('lesson settings menu', async () => {
    await page.locator('.content-update-controls > details > summary').click();
    await shot('15-lesson-settings');
    await page.locator('.content-update-controls > details > summary').click();
  });
  await step('app settings menu', async () => {
    await page.locator('.app-update-settings > summary').click();
    await shot('16-app-settings');
    await page.locator('.app-update-settings > summary').click();
  });
  await step('shortcut sheet', async () => {
    await page.locator('.repository-study .shortcut-sheet-open').click();
    await shot('17-shortcuts');
    await page.keyboard.press('Escape');
  });
  await step('narration playing', async () => {
    const play = page.locator('.repository-task .narration-play');
    if (!await play.count()) throw Error('no narration on this step');
    await play.click();
    await page.waitForFunction(() => document.querySelector('.repository-task')?.dataset.narrating === 'true', null, {timeout: 30000});
    await page.waitForTimeout(2500);
    await shot('18-narration');
    await page.locator('.repository-task .narration-stop').click();
    await page.waitForFunction(() => document.querySelector('.repository-task')?.dataset.narrating === 'false', null, {timeout: 30000});
  });
  await step('auto run running', async () => {
    await page.waitForSelector('#auto-run-start:not([disabled])', {timeout: 30000});
    await page.locator('#auto-run-start').click();
    await page.waitForSelector('.auto-run-control[data-state="running"]', {timeout: 30000});
    await page.waitForTimeout(1500);
    await shot('19-auto-running');
    await page.keyboard.press('Escape');
    await page.waitForSelector('.auto-run-control:not([data-state="running"])', {timeout: 30000});
    await page.waitForTimeout(400);
    await page.locator('.auto-run-details > summary').click();
    await shot('20-auto-stopped');
    await page.locator('.auto-run-dismiss').click();
  });
  await step('narrow problem', async () => { await narrow(); await shot('21-problem-narrow'); await desktop(); });
  await step('reduced motion problem', async () => {
    await page.emulateMedia({reducedMotion: 'reduce'});
    await shot('22-problem-reduced-motion');
    await page.emulateMedia({reducedMotion: 'no-preference'});
  });

  await step('terminal lesson', async () => {
    await openLesson(0);
    await openTask(1);
    await page.waitForFunction(() => document.querySelector('.repository-task')?.dataset.gitReady === 'true', null, {timeout: 90000});
    await page.waitForTimeout(800);
    await shot('30-terminal');
  });
  for (const [index, name] of [[2, '32-git-graph'], [4, '33-vim'], [5, '34-java-build'], [24, '35-web-preview'], [26, '36-single-code']]) {
    await step(`lesson ${index} workspace`, async () => {
      await openLesson(index);
      await openTask(index === 2 ? 2 : 1);
      await page.waitForFunction(() => { const t = document.querySelector('.repository-task'); return t && (!t.querySelector('.git-terminal,#git-student-terminal') || t.dataset.gitReady === 'true'); }, null, {timeout: 120000});
      await page.waitForTimeout(1500);
      await shot(name);
    });
  }
  await step('back to catalog with progress', async () => { await toCatalog(); await page.waitForTimeout(800); await shot('40-catalog-after-study'); });
  await step('category preview catalog', async () => {
    await toolbox(true);
    await button('버전 분').click();
    await toolbox(false);
    await page.waitForFunction(() => document.querySelectorAll('.lesson-card').length > 30, null, {timeout: 60000});
    await page.waitForTimeout(800);
    await shot('41-catalog-category-preview');
    const grouped = button('분류별');
    if (await grouped.count() && await grouped.isEnabled()) {
      await grouped.click();
      await page.waitForSelector('.lesson-group-title');
      await page.locator('.lesson-group-title').first().scrollIntoViewIfNeeded();
      await shot('42-catalog-grouped');
    }
  });
  return notes;
};
