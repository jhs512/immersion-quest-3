// 작은 재현 루프(2026-10-30 인벤토리에서 발견):
//  1) 모달을 연 뒤 포커스가 팝업 밖에 있을 때 Esc로 닫으면 앱 상태가 '열림'으로 남아 다시 열 수 없던 문제
//     (진도 초기화·코스 가이드·학습 정보). 닫힌 뒤 같은 버튼으로 다시 열리고, 처음 포커스가 팝업 안에 있어야 한다.
//  2) 비활성 primary 버튼의 글자가 보이지 않던 문제(밝게·어둡게에서 글자 대비 >= 3:1).
// 격리된 검증 데이터만 쓰고 초기화 확인은 누르지 않는다.
module.exports = async ({page, shot}) => {
  const notes = [];
  const fail = (m) => notes.push('FAIL ' + m);
  const button = (name) => page.getByRole('button', {name, exact: true});
  await page.setViewportSize({width: 1440, height: 900});
  await page.waitForSelector('.pilot-toolbox', {timeout: 60000});
  await page.evaluate(() => { document.querySelector('.pilot-toolbox').open = true; });
  await button('버전 본').click();
  await page.evaluate(() => { document.querySelector('.pilot-toolbox').open = false; });
  await page.waitForFunction(() => document.querySelectorAll('.lesson-card').length > 30, null, {timeout: 60000});

  // 2) 코스 이름 저장 전: 수업 버튼이 비활성이다.
  for (const theme of ['light', 'dark']) {
    await page.evaluate((t) => window.mqTheme.set(t), theme);
    await page.waitForTimeout(200);
    const r = await page.evaluate(() => {
      const lum = (c) => { const m = c.match(/[\d.]+/g).map(Number); const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; }; return 0.2126 * f(m[0]) + 0.7152 * f(m[1]) + 0.0722 * f(m[2]); };
      return [...document.querySelectorAll('button.primary:disabled')].slice(0, 4).map((b) => {
        let bg = 'rgb(255,255,255)'; for (let n = b; n; n = n.parentElement) { const c = getComputedStyle(n).backgroundColor; const a = c.match(/[\d.]+/g); if (a && (a.length < 4 || +a[3] > 0.9)) { bg = c; break; } }
        const x = [lum(getComputedStyle(b).color), lum(bg)].sort((p, q) => q - p); return {text: b.innerText.trim(), ratio: (x[0] + 0.05) / (x[1] + 0.05)};
      });
    });
    for (const b of r) { notes.push(`disabled ${theme} "${b.text}" ${b.ratio.toFixed(2)}:1`); if (b.ratio < 3) fail(`disabled ${theme} "${b.text}" ${b.ratio.toFixed(2)}`); }
    if (!r.length) fail(`disabled ${theme}: 비활성 primary 없음`);
    await shot(`disabled-${theme}`);
  }
  await page.evaluate(() => window.mqTheme.set('light'));

  const cycle = async (label, open, dialogSel) => {
    for (let round = 1; round <= 2; round++) {
      await open();
      await page.waitForFunction((s) => document.querySelector(s)?.open, dialogSel, {timeout: 10000});
      await page.waitForTimeout(300);
      const inside = await page.evaluate((s) => !!document.activeElement?.closest(s), dialogSel);
      notes.push(`${label} round ${round}: 처음 포커스 팝업 안=${inside}`);
      if (!inside) fail(`${label}: 처음 포커스가 팝업 밖`);
      // 포커스를 팝업 밖(문서)으로 옮긴 뒤 Esc: 브라우저가 닫아도 앱이 상태를 따라가야 한다.
      await page.evaluate(() => document.activeElement?.blur());
      await page.keyboard.press('Escape');
      await page.waitForTimeout(400);
      const closed = await page.evaluate((s) => !document.querySelector(s)?.open, dialogSel);
      if (!closed) fail(`${label} round ${round}: Esc로 닫히지 않음`);
    }
    notes.push(`ok ${label}: 두 번 열고 닫음`);
  };
  try { await cycle('진도 초기화', () => page.locator('.account-reset-open').click({timeout: 5000}), '#account-reset-dialog'); } catch (e) { fail('진도 초기화: ' + String(e.message).split('\n')[0]); }
  try { await cycle('코스 가이드', () => page.locator('.course-guide-open').first().click({timeout: 5000}), '#course-guide-dialog'); } catch (e) { fail('코스 가이드: ' + String(e.message).split('\n')[0]); }
  // 코스 이름을 저장해 수업을 연 뒤 학습 정보 팝업
  try {
    await page.locator('#course-display-name').fill('모달검증');
    await page.locator('.course-identity button[type=submit]').click();
    await page.waitForFunction(() => [...document.querySelectorAll('.lesson-card button')].some(b => b.textContent.includes('학습 시작') && !b.disabled), null, {timeout: 30000});
    await page.locator('.lesson-card').nth(1).locator('button', {hasText: '학습 시작'}).click();
    await page.waitForSelector('.study-navigation', {timeout: 60000});
    await cycle('학습 정보', () => page.locator('.lesson-info-trigger').click({timeout: 5000}), '#lesson-info-dialog');
  } catch (e) { fail('학습 정보: ' + String(e.message).split('\n')[0]); }
  notes.push(`TOTAL FAIL ${notes.filter((n) => n.startsWith('FAIL')).length}`);
  return notes;
};
