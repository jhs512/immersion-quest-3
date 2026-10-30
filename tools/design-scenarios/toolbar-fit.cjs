// 코드 영역 상단 버튼 줄(초기화·코드 실행·코드 흐름 보기·제출)이 여러 창 폭과 분할 비율에서 패널 안에 다 들어오는지 잰다.
// 지원 문제(engineer-python-calls 2번, 코드 흐름 있음)와 미지원 문제(같은 수업 1번), 밝게·어둡게.
// 버튼의 오른쪽 끝이 코드 패널 오른쪽 안쪽 경계를 넘거나, 버튼 글자가 잘리거나(scrollWidth > clientWidth), 클릭 대상이
// 다른 요소에 가려지면 실패.
module.exports = async ({page, shot}) => {
  const notes = [];
  const fail = (m) => notes.push('FAIL ' + m);
  const button = (name) => page.getByRole('button', {name, exact: true});
  await page.setViewportSize({width: 1440, height: 900});
  await page.waitForSelector('.pilot-toolbox', {timeout: 60000});
  await page.evaluate(() => { document.querySelector('.pilot-toolbox').open = true; });
  await button('버전 노').click();
  await page.evaluate(() => { document.querySelector('.pilot-toolbox').open = false; });
  await page.waitForSelector('.lesson-card', {timeout: 60000});
  if (await page.waitForSelector('#course-display-name', {timeout: 15000}).then(() => true, () => false)) {
    await page.locator('#course-display-name').fill('버튼검증');
    await page.locator('.course-identity button[type=submit]').click();
  }
  const ready = await page.waitForFunction(() => [...document.querySelectorAll('.lesson-card button')].some(b => /학습 시작|이어서/.test(b.textContent) && !b.disabled), null, {timeout: 90000}).then(() => true, () => false);
  if (!ready) {
    const state = await page.evaluate(() => ({cards: document.querySelectorAll('.lesson-card').length, buttons: [...document.querySelectorAll('.lesson-card button')].map((b) => b.textContent.trim() + (b.disabled ? '(비활성)' : '')).slice(0, 4), identity: document.querySelector('.course-identity')?.innerText.slice(0, 80), status: document.querySelector('.repository-status')?.innerText}));
    await shot('T-not-ready'); throw Error('수업 버튼이 활성화되지 않음 ' + JSON.stringify(state));
  }
  await page.locator('.lesson-card').first().locator('button', {hasText: /학습 시작|이어서/}).first().click();
  await page.waitForSelector('.study-navigation', {timeout: 60000});
  const openTask = async (n) => { await page.locator('.study-navigation button', {hasText: `문제 ${n} ·`}).first().click(); await page.waitForSelector('.cm-editor', {timeout: 30000}); await page.waitForTimeout(400); };
  const measure = () => page.evaluate(() => {
    const pane = document.querySelector('.repository-task .coding-pane'); const pr = pane.getBoundingClientRect();
    const pad = parseFloat(getComputedStyle(pane).paddingRight) || 0;
    const rows = [...document.querySelectorAll('.repository-task .pane-actions button')].filter((b) => b.getClientRects().length).map((b) => {
      const r = b.getBoundingClientRect(); const cx = r.left + r.width / 2, cy = r.top + r.height / 2;
      const top = document.elementFromPoint(Math.min(cx, innerWidth - 1), cy);
      return {text: b.innerText.replace(/\s+/g, ' ').trim(), right: Math.round(r.right), left: Math.round(r.left), top: Math.round(r.top),
        clipped: b.scrollWidth > b.clientWidth + 1, reachable: !!top && (top === b || b.contains(top))};
    });
    return {paneRight: Math.round(pr.right - pad), paneLeft: Math.round(pr.left), rows, vw: innerWidth};
  });
  const check = async (tag) => {
    const m = await measure();
    const bad = m.rows.filter((r) => r.right > m.paneRight + 1 || r.left < m.paneLeft || r.clipped || !r.reachable || r.right > m.vw);
    notes.push(`${tag}: 패널 ${m.paneLeft}..${m.paneRight} | ${m.rows.map((r) => `${r.text.split(' ')[0]}@${r.left}-${r.right}/${r.top}${r.clipped ? '잘림' : ''}${r.reachable ? '' : '가림'}`).join(' ')}`);
    if (bad.length) fail(`${tag}: ${bad.map((r) => r.text.split(' ')[0]).join(', ')} 패널 밖·잘림·가림`);
    return m;
  };
  // Drag the real handle between the brief and the code side, as a learner does with the mouse.
  const split = async (ratio) => {
    const h = await page.evaluate(() => { const hs = [...document.querySelectorAll('.repository-task .split-handle')].map((el) => el.getBoundingClientRect()).filter((r) => r.height > r.width * 3);
      const r = hs.sort((a, b) => b.height - a.height)[0]; return r && {x: r.left + r.width / 2, y: r.top + r.height / 2}; });
    if (!h) return false;
    const vw = await page.evaluate(() => innerWidth);
    await page.mouse.move(h.x, h.y); await page.mouse.down(); await page.mouse.move(vw * ratio, h.y, {steps: 8}); await page.mouse.up();
    return true;
  };
  for (const theme of ['light', 'dark']) {
    await page.evaluate((t) => window.mqTheme.set(t), theme);
    for (const [task, kind] of [[2, '지원'], [1, '미지원']]) {
      await openTask(task);
      if (task === 2 && theme === 'light') { await page.locator('.repository-task [data-shortcut-action="run"]').click(); await page.waitForFunction(() => ['finished', 'failed'].includes(document.querySelector('.result-pane')?.dataset.executionState), null, {timeout: 90000}); }
      for (const width of [820, 1024, 1280, 1440, 1920]) {
        await page.setViewportSize({width, height: 900}); await page.waitForTimeout(250);
        await check(`${theme}-${kind}-${width}`);
        if (width === 1440 || width === 1024) await shot(`T-${theme}-${kind}-${width}`);
      }
      // A narrow code side at a wide window (the learner dragged the split to the right).
      await page.setViewportSize({width: 1440, height: 900});
      if (await split(0.9)) { await page.waitForTimeout(250); await check(`${theme}-${kind}-1440-좁은코드영역`); await shot(`T-${theme}-${kind}-1440-narrow-pane`); await split(0.38); }
    }
  }
  notes.push(`TOTAL FAIL ${notes.filter((n) => n.startsWith('FAIL')).length}`);
  return notes;
};
