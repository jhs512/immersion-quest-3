// 실제 해설 재생 중(자막·스포트라이트·행/단어 강조가 함께 있을 때) 강조된 코드가 읽히고 자막이 강조 대상을 덮지 않는지.
module.exports = async ({page, shot}) => {
  const notes = [];
  const button = (name) => page.getByRole('button', {name, exact: true});
  await page.setViewportSize({width: 1440, height: 900});
  await page.waitForSelector('.pilot-toolbox', {timeout: 60000});
  await page.evaluate(() => { document.querySelector('.pilot-toolbox').open = true; });
  await button('버전 본').click();
  await page.evaluate(() => { document.querySelector('.pilot-toolbox').open = false; });
  await page.waitForFunction(() => document.querySelectorAll('.lesson-card').length > 30, null, {timeout: 60000});
  await page.locator('#course-display-name').fill('해설검증');
  await page.locator('.course-identity button[type=submit]').click();
  await page.waitForFunction(() => [...document.querySelectorAll('.lesson-card button')].some(b => b.textContent.includes('학습 시작') && !b.disabled), null, {timeout: 30000});
  for (const theme of ['light', 'dark']) {
    await page.evaluate((t) => window.mqTheme.set(t), theme);
    if (await button('← 코스 수업 목록').count()) await button('← 코스 수업 목록').click();
    await page.locator('.lesson-card').nth(4).locator('button', {hasText: '학습 시작'}).click();
    await page.waitForSelector('.study-navigation', {timeout: 60000});
    await page.locator('.study-navigation button', {hasText: '문제 1 ·'}).first().click();
    await page.waitForSelector('.cm-editor', {timeout: 30000});
    await page.locator('.repository-task .narration-play').click();
    const seen = await page.waitForSelector('.cm-narration-span', {timeout: 90000}).then(() => true, () => false);
    await page.waitForTimeout(300);
    const r = await page.evaluate(() => {
      const span = document.querySelector('.cm-narration-span'); const cap = document.querySelector('.agent-caption');
      if (!span) return null; const a = span.getBoundingClientRect(); const b = cap?.getBoundingClientRect();
      const overlap = b ? !(b.right < a.left || b.left > a.right || b.bottom < a.top || b.top > a.bottom) : false;
      return {text: span.innerText, overlap, caption: !!cap};
    });
    notes.push(`${theme}: 강조 ${seen} ${JSON.stringify(r)}`);
    if (!seen || !r) notes.push(`FAIL ${theme}: 해설 중 단어 강조를 못 봄`); else if (r.overlap) notes.push(`FAIL ${theme}: 자막이 강조 대상을 덮음`);
    await shot(`live-${theme}`);
    await page.locator('.repository-task .narration-stop').click().catch(() => {});
  }
  return notes;
};
