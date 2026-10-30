// 작은 확인 루프: Git 그래프 패널(기본·크게 보기)을 밝게·어둡게에서 연다. 패널 버튼과 글자 대비(>= 4.5:1)를 잰다.
module.exports = async ({page, shot}) => {
  const notes = [];
  const button = (name) => page.getByRole('button', {name, exact: true});
  await page.setViewportSize({width: 1440, height: 900});
  await page.waitForSelector('.pilot-toolbox', {timeout: 60000});
  await page.evaluate(() => { document.querySelector('.pilot-toolbox').open = true; });
  await button('버전 본').click();
  await page.evaluate(() => { document.querySelector('.pilot-toolbox').open = false; });
  await page.waitForFunction(() => document.querySelectorAll('.lesson-card').length > 30, null, {timeout: 60000});
  await page.locator('#course-display-name').fill('그래프검증');
  await page.locator('.course-identity button[type=submit]').click();
  await page.waitForFunction(() => [...document.querySelectorAll('.lesson-card button')].some(b => b.textContent.includes('학습 시작') && !b.disabled), null, {timeout: 30000});
  const card = page.locator('.lesson-card').filter({hasText: 'Git · 브랜치 기본'}).first(); await card.scrollIntoViewIfNeeded();
  notes.push('card: ' + (await card.locator('h3').innerText()).trim());
  await card.locator('button', {hasText: '학습 시작'}).click();
  await page.waitForSelector('.study-navigation', {timeout: 60000});
  await page.locator('.study-navigation button', {hasText: '문제 3 ·'}).first().click();
  await page.waitForFunction(() => document.querySelector('.repository-task')?.dataset.gitReady === 'true', null, {timeout: 120000});
  const scan = () => page.evaluate(() => {
    const lum = (c) => { const m = c.match(/[\d.]+/g).map(Number); const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; }; return 0.2126 * f(m[0]) + 0.7152 * f(m[1]) + 0.0722 * f(m[2]); };
    const bgOf = (el) => { for (let n = el; n; n = n.parentElement) { const c = getComputedStyle(n).backgroundColor; const a = c.match(/[\d.]+/g); if (a && (a.length < 4 || +a[3] > 0.9)) return c; } return 'rgb(255,255,255)'; };
    const low = [];
    for (const el of document.querySelectorAll('.git-graph-panel summary, .git-graph-panel button, .git-graph-status, .git-graph-detail')) {
      if (!el.getClientRects().length || !el.innerText.trim()) continue;
      const x = [lum(getComputedStyle(el).color), lum(bgOf(el))].sort((p, q) => q - p); const r = (x[0] + 0.05) / (x[1] + 0.05);
      if (r < 4.5) low.push(`${r.toFixed(2)} ${el.innerText.trim().slice(0, 16)}`);
    }
    return {low, panelBg: getComputedStyle(document.querySelector('.git-graph-panel')).backgroundColor};
  });
  for (const theme of ['light', 'dark']) {
    await page.evaluate((t) => window.mqTheme.set(t), theme); await page.waitForTimeout(400);
    let r = await scan(); notes.push(`${theme}: panel ${r.panelBg} 낮은 대비 ${r.low.length} ${r.low.join(' | ')}`); if (r.low.length) notes.push(`FAIL ${theme}`);
    await shot(`git-graph-${theme}`);
    const big = page.locator('.git-graph-panel button', {hasText: '크게 보기'}).first();
    if (await big.count()) { await big.click(); await page.waitForTimeout(500); r = await scan(); notes.push(`${theme} 크게: 낮은 대비 ${r.low.length} ${r.low.join(' | ')}`); if (r.low.length) notes.push(`FAIL ${theme} 크게`); await shot(`git-graph-${theme}-expanded`); await page.keyboard.press('Escape'); await page.waitForTimeout(300); const small = page.locator('.git-graph-panel button', {hasText: /작게|원래 크기|닫기/}).first(); if (await small.count() && await small.isVisible()) await small.click(); }
  }
  return notes;
};
