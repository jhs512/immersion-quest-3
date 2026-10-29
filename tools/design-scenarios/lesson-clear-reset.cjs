// Lesson clear by the final challenge and lesson-level reset, on the real course (validation version 본)
// with progress seeded by tools/design-scenarios/seed-lesson-clear.py:
//   MQ3_CAPTURE_DATA_DIR=<seeded folder> node tools/design-capture.cjs tools/design-scenarios/lesson-clear-reset.cjs <out>
// Phase "reset" (default) checks the catalog states, opens the challenge-cleared lesson, resets it and
// checks the catalog again. Run once more with MQ3_CAPTURE_PHASE=restart on the same folder to check
// that the reset survives an app restart and the neighbouring lessons keep their progress.
module.exports = async ({page, shot}) => {
  const notes = [];
  const phase = process.env.MQ3_CAPTURE_PHASE || 'reset';
  const os = async (scheme) => { await page.emulateMedia({colorScheme: scheme}); await page.waitForTimeout(150); };
  const card = (title) => page.locator('.lesson-card', {has: page.locator('h3', {hasText: title})});
  const cardState = (title) => card(title).evaluate(el => ({state: el.dataset.state, challenge: el.dataset.challenge,
    badge: el.querySelector('.lesson-challenge-badge')?.textContent.trim() ?? null,
    headline: el.querySelector('.lesson-progress strong')?.textContent.trim() ?? null,
    count: el.querySelector('.lesson-progress span')?.textContent.trim() ?? null,
    ring: getComputedStyle(el.querySelector('.lesson-number')).backgroundColor,
    hidden: el.querySelector('.lesson-number .visually-hidden:last-child')?.textContent ?? ''}));
  const expectState = async (title, wanted) => {
    await page.waitForFunction(([t, s]) => [...document.querySelectorAll('.lesson-card')].some(el => el.querySelector('h3')?.textContent.includes(t) && el.dataset.state === s), [title, wanted.state], {timeout: 30000});
    const s = await cardState(title);
    for (const [k, v] of Object.entries(wanted)) if (s[k] !== v) throw Error(`${title}: ${k}=${s[k]} expected ${v} ${JSON.stringify(s)}`);
    notes.push(`ok ${phase} ${title}: ${JSON.stringify(s)}`);
  };

  await page.setViewportSize({width: 1440, height: 900});
  await os('light');
  await page.waitForSelector('.pilot-toolbox', {timeout: 60000});
  if (phase === 'reset') {
    await page.evaluate(() => { document.querySelector('.pilot-toolbox').open = true; });
    await page.getByRole('button', {name: '버전 본', exact: true}).click();
    await page.evaluate(() => { document.querySelector('.pilot-toolbox').open = false; });
  }
  await page.waitForFunction(() => document.querySelectorAll('.lesson-card').length > 40, null, {timeout: 60000});
  if (await page.locator('#course-display-name').isVisible().catch(() => false) && !(await page.locator('.course-identity[data-saved="true"]').count())) {
    await page.locator('#course-display-name').fill('디자인검증');
    await page.locator('.course-identity button[type=submit]').click();
  }
  await page.waitForFunction(() => [...document.querySelectorAll('.lesson-card button.primary')].some(b => !b.disabled), null, {timeout: 30000});

  if (phase === 'restart') {
    await expectState('변수에 값을 담고 꺼내요', {state: 'todo', challenge: 'none', badge: null});
    await expectState('값이 계산되고 표시되는 과정', {state: 'done'});
    await expectState('export로 자식 프로세스에 값을 전해요', {state: 'progress', count: '필수 문제 5 / 6'});
    await card('변수에 값을 담고 꺼내요').scrollIntoViewIfNeeded();
    await shot('r01-after-restart-reset-kept');
    return notes;
  }

  // 1. Catalog: challenge clear (purple, words, true gauge), full completion and partial progress.
  await expectState('변수에 값을 담고 꺼내요', {state: 'challenge', challenge: 'passed', badge: '도전 통과', headline: '수업 클리어', count: '필수 문제 3 / 7', hidden: ', 도전 과제 통과로 클리어'});
  await expectState('값이 계산되고 표시되는 과정', {state: 'done', challenge: 'none'});
  await expectState('export로 자식 프로세스에 값을 전해요', {state: 'progress', challenge: 'none', headline: '83% 완료', count: '필수 문제 5 / 6'});
  notes.push('course facts: ' + await page.locator('.course-facts .study-progress').textContent());
  await card('변수에 값을 담고 꺼내요').scrollIntoViewIfNeeded();
  await page.evaluate(() => scrollBy(0, -160));
  await shot('c01-catalog-wide-light');
  await os('dark');
  await shot('c02-catalog-wide-dark');
  notes.push('dark ring ' + JSON.stringify(await cardState('변수에 값을 담고 꺼내요')));
  await page.setViewportSize({width: 820, height: 900});
  await card('변수에 값을 담고 꺼내요').scrollIntoViewIfNeeded();
  await shot('c03-catalog-narrow-dark');
  await os('light');
  await shot('c04-catalog-narrow-light');
  // Grouped view keeps the same state and placement.
  const grouped = page.getByRole('button', {name: '분류별', exact: true});
  if (await grouped.isEnabled()) {
    await grouped.click();
    await card('변수에 값을 담고 꺼내요').scrollIntoViewIfNeeded();
    await expectState('변수에 값을 담고 꺼내요', {state: 'challenge', badge: '도전 통과'});
    await shot('c05-grouped-narrow-light');
    await page.getByRole('button', {name: '전체 순서', exact: true}).click();
  } else notes.push('grouped view unavailable');
  // Challenge board marks designated challenges.
  await page.setViewportSize({width: 1440, height: 900});
  await page.getByRole('button', {name: '도전 과제', exact: true}).click();
  await page.waitForSelector('.challenge-card[data-designated="true"]', {timeout: 60000});
  const board = await page.evaluate(() => ({designated: document.querySelectorAll('.challenge-card[data-designated="true"]').length,
    cleared: document.querySelectorAll('.challenge-card .challenge-cleared').length}));
  notes.push('challenge board ' + JSON.stringify(board));
  await page.locator('.challenge-card .challenge-cleared').first().scrollIntoViewIfNeeded();
  await shot('c06-challenge-board-light');
  await page.getByRole('button', {name: '수업 목록', exact: true}).click();

  // 2. Lesson: 학습 정보 shows the challenge clear with the true gauge, then the reset asks once.
  await card('변수에 값을 담고 꺼내요').locator('button.primary').click();
  await page.waitForSelector('.lesson-info-trigger', {timeout: 60000});
  notes.push('header gauge ' + await page.locator('.lesson-info-trigger').textContent());
  await page.locator('.lesson-info-trigger').click();
  await page.waitForSelector('#lesson-info-dialog[open] .lesson-reset', {timeout: 10000});
  notes.push('dialog progress ' + await page.locator('#lesson-info-dialog .study-progress').textContent());
  await shot('l01-lesson-info-light');
  await page.locator('#lesson-info-dialog .lesson-reset-open').click();
  await page.waitForSelector('#lesson-info-dialog .lesson-reset[data-confirming="true"]');
  notes.push('confirm text ' + await page.locator('#lesson-info-dialog .lesson-reset-question').textContent());
  await page.locator('#lesson-info-dialog .lesson-reset').scrollIntoViewIfNeeded();
  await shot('l02-reset-confirm-light');
  await os('dark');
  await shot('l03-reset-confirm-dark');
  await page.setViewportSize({width: 820, height: 900});
  await page.locator('#lesson-info-dialog .lesson-reset').scrollIntoViewIfNeeded();
  await shot('l04-reset-confirm-narrow-dark');
  await os('light');
  await page.setViewportSize({width: 1440, height: 900});
  // Cancel keeps everything; confirm resets this lesson only.
  await page.locator('#lesson-info-dialog .lesson-reset').getByRole('button', {name: '취소', exact: true}).click();
  await page.waitForSelector('#lesson-info-dialog .lesson-reset[data-confirming="false"]');
  if (!(await page.locator('#lesson-info-dialog .study-progress').textContent()).includes('3 / 7')) throw Error('cancel changed progress');
  await page.locator('#lesson-info-dialog .lesson-reset-open').click();
  await page.locator('#lesson-info-dialog .lesson-reset-confirm').click();
  await page.waitForFunction(() => document.querySelector('#lesson-info-dialog .study-progress')?.textContent.includes('필수 문제 0 / 7'), null, {timeout: 10000});
  const after = await page.locator('#lesson-info-dialog .study-progress').textContent();
  if (after.includes('도전 통과')) throw Error('challenge still shown after reset: ' + after);
  notes.push('after reset ' + after + ' | status ' + await page.locator('#lesson-info-dialog .lesson-reset-status').textContent());
  await shot('l05-after-reset-light');
  await page.locator('#lesson-info-dialog header button').click();
  notes.push('header after reset ' + await page.locator('.lesson-info-trigger').textContent());
  await page.locator('button.course-back').click();
  await page.waitForFunction(() => document.querySelectorAll('.lesson-card').length > 40, null, {timeout: 60000});
  await expectState('변수에 값을 담고 꺼내요', {state: 'todo', challenge: 'none', badge: null, count: '필수 문제 0 / 7'});
  await expectState('값이 계산되고 표시되는 과정', {state: 'done'});
  await expectState('export로 자식 프로세스에 값을 전해요', {state: 'progress', count: '필수 문제 5 / 6'});
  await card('변수에 값을 담고 꺼내요').scrollIntoViewIfNeeded();
  await shot('c07-catalog-after-reset-light');
  return notes;
};
