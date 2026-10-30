// 작은 재현 루프: 앱 설정 → 환경 진단 팝업을 밝게·어둡게에서 열어 제목·결과 카드 글자 대비를 잰다(>= 4.5:1).
module.exports = async ({page, shot}) => {
  const notes = [];
  const button = (name) => page.getByRole('button', {name, exact: true});
  await page.setViewportSize({width: 1440, height: 900});
  await page.waitForSelector('.pilot-toolbox', {timeout: 60000});
  await page.evaluate(() => { document.querySelector('.pilot-toolbox').open = true; });
  await button('버전 본').click();
  await page.evaluate(() => { document.querySelector('.pilot-toolbox').open = false; });
  await page.waitForFunction(() => document.querySelectorAll('.lesson-card').length > 30, null, {timeout: 60000});
  for (const theme of ['light', 'dark']) {
    await page.evaluate((t) => window.mqTheme.set(t), theme);
    if (!await page.evaluate(() => !!document.querySelector('.app-update-settings')?.open)) await page.locator('.app-update-settings > summary').first().click();
    await page.locator('.app-update-menu button', {hasText: '환경 진단'}).first().click();
    await page.waitForSelector('.doctor-backdrop .doctor-check', {timeout: 30000});
    await page.waitForTimeout(800);
    const worst = await page.evaluate(() => {
      const lum = (c) => { const m = c.match(/[\d.]+/g).map(Number); const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; }; return 0.2126 * f(m[0]) + 0.7152 * f(m[1]) + 0.0722 * f(m[2]); };
      const bgOf = (el) => { for (let n = el; n; n = n.parentElement) { const c = getComputedStyle(n).backgroundColor; const a = c.match(/[\d.]+/g); if (a && (a.length < 4 || +a[3] > 0.9)) return c; } return 'rgb(255,255,255)'; };
      let low = []; for (const el of document.querySelectorAll('.doctor-panel h2, .doctor-panel h3, .doctor-panel p, .doctor-panel strong, .doctor-check')) {
        if (!el.innerText.trim()) continue; const x = [lum(getComputedStyle(el).color), lum(bgOf(el))].sort((p, q) => q - p); const r = (x[0] + 0.05) / (x[1] + 0.05);
        if (r < 4.5) low.push(`${r.toFixed(2)} ${el.innerText.trim().slice(0, 20)}`); }
      return low;
    });
    notes.push(`${theme}: 낮은 대비 ${worst.length}건 ${worst.slice(0, 3).join(' | ')}`);
    if (worst.length) notes.push(`FAIL ${theme}`);
    await shot(`doctor-${theme}`);
    const close = page.locator('.doctor-panel button', {hasText: /닫기/}).first(); if (await close.count()) await close.click(); else await page.keyboard.press('Escape');
    await page.evaluate(() => { const d = document.querySelector('.app-update-settings'); if (d) d.open = false; });
  }
  return notes;
};
