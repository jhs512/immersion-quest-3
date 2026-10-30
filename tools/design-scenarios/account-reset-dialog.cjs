// 사용자 스크린샷(2026-10-30) 재현: GitHub 확인 화면의 헤더 위치·버튼 대비, 「진도 초기화」 팝업의
// 제목·닫기 버튼 대비, 계정 이름 보간, 안내 문장 잘림. 밝게·어둡게, 넓은 창·820px 창에서 검사한다.
// 검증 모드의 격리된 데이터 폴더만 쓰고, 팝업은 열어 계획을 읽기만 한다(초기화 확인은 누르지 않음).
// 하나라도 어긋나면 notes에 FAIL을 남기고 마지막에 실패한다.
module.exports = async ({page, shot}) => {
  const notes = [];
  const fail = (m) => notes.push('FAIL ' + m);
  const button = (name) => page.getByRole('button', {name, exact: true});
  const lum = (c) => { const m = c.match(/[\d.]+/g).map(Number); const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; }; return 0.2126 * f(m[0]) + 0.7152 * f(m[1]) + 0.0722 * f(m[2]); };
  const ratio = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return (x + 0.05) / (y + 0.05); };
  // The composited background behind an element (first opaque ancestor).
  const probe = (selector) => page.evaluate((selector) => {
    const el = document.querySelector(selector); if (!el) return null;
    let bg = 'rgb(255,255,255)';
    for (let n = el; n; n = n.parentElement) { const c = getComputedStyle(n).backgroundColor; const a = c.match(/[\d.]+/g); if (a && (a.length < 4 || Number(a[3]) > 0.9)) { bg = c; break; } }
    const r = el.getBoundingClientRect();
    return {fg: getComputedStyle(el).color, bg, text: el.textContent.trim(), top: r.top, right: r.right, width: r.width,
      overflow: el.scrollWidth > el.clientWidth + 1, ws: getComputedStyle(el).whiteSpace};
  }, selector);
  const check = async (label, selector, min) => {
    const p = await probe(selector);
    if (!p) { fail(`${label}: ${selector} 없음`); return null; }
    const r = ratio(p.fg, p.bg);
    notes.push(`${label}: ${selector} ${r.toFixed(2)}:1 (${p.fg} on ${p.bg})`);
    if (r < min) fail(`${label}: ${selector} 대비 ${r.toFixed(2)} < ${min}`);
    return p;
  };

  await page.setViewportSize({width: 1440, height: 900});
  // 1) 시작 직후의 GitHub 확인 화면 (needs-gh)
  try {
    // 검증 모드는 GitHub 확인 단계를 건너뛰므로, 같은 DOM 구조(헤더 + .gh-checking)를 수업 목록 위에 재현한다.
    await page.waitForSelector('.pilot-toolbox', {timeout: 60000});
    await page.evaluate(() => {
      const root = document.querySelector('.repository-player'); root.classList.add('needs-gh');
      for (const child of [...root.children]) if (!child.classList.contains('repository-header') && !child.classList.contains('pilot-toolbar')) child.style.display = 'none';
      const s = document.createElement('section'); s.className = 'gh-checking'; s.setAttribute('role', 'status');
      s.innerHTML = '<h2>GitHub 연결을 확인하고 있어요</h2><p>설치된 gh의 로그인 상태를 확인해요.</p>'; root.append(s);
    });
    for (const look of ['light', 'dark']) {
      await page.evaluate((look) => window.mqTheme.set(look), look);
      await page.waitForTimeout(200);
      const head = await probe('.repository-player.needs-gh>.repository-header');
      notes.push(`gh-check ${look}: header top ${head && head.top}`);
      if (!head || head.top > 8) fail(`gh-check ${look}: 헤더가 맨 위가 아님 (top ${head && head.top})`);
      await check(`gh-check ${look}`, '.repository-player.needs-gh .shortcut-sheet-open', 4.5);
      await check(`gh-check ${look}`, '.repository-player.needs-gh .app-update-settings>summary', 4.5);
      await shot(`gh-check-${look}`);
    }
    await page.setViewportSize({width: 820, height: 900}); await shot('gh-check-light-820'); await page.setViewportSize({width: 1440, height: 900});
    await page.evaluate(() => { const root = document.querySelector('.repository-player'); root.classList.remove('needs-gh'); root.querySelector(':scope>.gh-checking')?.remove(); for (const child of root.children) child.style.display = ''; });
  } catch (error) { notes.push('gh-check 화면을 잡지 못함: ' + String(error.message).split('\n')[0]); }

  await page.waitForSelector('.pilot-toolbox', {timeout: 60000});
  await page.evaluate(() => { document.querySelector('.pilot-toolbox').open = true; });
  await button('버전 본').click();
  await page.evaluate(() => { document.querySelector('.pilot-toolbox').open = false; });
  await page.waitForFunction(() => document.querySelectorAll('.lesson-card').length > 30, null, {timeout: 60000});
  for (const [look, width] of [['light', 1440], ['light', 820], ['dark', 1440], ['dark', 820]]) {
    await page.setViewportSize({width, height: 900});
    await page.evaluate((look) => window.mqTheme.set(look), look);
    const tag = `${look}-${width}`;
    await check(`header ${tag}`, '.repository-account .account-recheck', 4.5);
    await page.locator('.account-reset-open').click();
    await page.waitForFunction(() => document.getElementById('account-reset-dialog')?.open, null, {timeout: 10000});
    await page.waitForFunction(() => !/확인하고 있어요/.test(document.getElementById('account-reset-dialog')?.textContent || ''), null, {timeout: 30000}).catch(() => {});
    await page.waitForTimeout(400);
    await check(`dialog ${tag}`, '#account-reset-title', 4.5);
    await check(`dialog ${tag}`, '#account-reset-dialog header button', 4.5);
    const intro = await probe('#account-reset-dialog .account-reset-intro');
    if (intro) {
      notes.push(`dialog ${tag}: intro "${intro.text.slice(0, 40)}" ws=${intro.ws}`);
      if (/\{|@\{/.test(intro.text) || !/@mq3-validation/.test(intro.text)) fail(`dialog ${tag}: 계정 이름이 보간되지 않음`);
      const box = await page.evaluate(() => document.getElementById('account-reset-dialog').getBoundingClientRect().right);
      if (intro.overflow || intro.right > box + 1) fail(`dialog ${tag}: 안내 문장이 팝업 밖으로 넘침`);
    } else fail(`dialog ${tag}: 안내 문장 없음`);
    const confirm = await probe('#account-reset-dialog .account-reset-confirm');
    if (confirm) await check(`dialog ${tag}`, '#account-reset-dialog .account-reset-confirm', 4.5);
    await shot(`dialog-${tag}`);
    await page.locator('#account-reset-dialog header button').click();
    await page.waitForFunction(() => !document.getElementById('account-reset-dialog')?.open, null, {timeout: 10000}).catch(() => {});
  }
  const failed = notes.filter((n) => n.startsWith('FAIL'));
  notes.push(`TOTAL FAIL ${failed.length}`);
  return notes;
};
