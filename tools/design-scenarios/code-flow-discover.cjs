// 코드 흐름 보기의 발견 가능성과 동작(2026-10-30 사용자: 「코드 실행 후 비주얼라이저 보는 단축키나 버튼 있나? … 알 수 있어야 해」).
// 실제 지원 수업(engineer-python-calls, 검증 버전 '노')에서: 버튼의 키 표시·aria, 실행 뒤 결과 영역 안내, 편집기 포커스에서
// 단축키로 열기 → 다음·이전 → 닫기 → 편집기 코드 그대로, 안내 버튼으로 열기, 실행 중·미지원 단계에서 단축키 무시, 단축키 안내 창.
module.exports = async ({page, shot}) => {
  const notes = [];
  const fail = (m) => notes.push('FAIL ' + m);
  const button = (name) => page.getByRole('button', {name, exact: true});
  const mac = await page.evaluate(() => /mac/i.test(navigator.platform));
  const MOD = mac ? 'Meta' : 'Control';
  const KEY = mac ? '⌘+Shift+F' : 'Ctrl+Shift+F';
  await page.setViewportSize({width: 1440, height: 900});
  await page.waitForSelector('.pilot-toolbox', {timeout: 60000});
  await page.evaluate(() => { document.querySelector('.pilot-toolbox').open = true; });
  await button('버전 노').click();
  await page.evaluate(() => { document.querySelector('.pilot-toolbox').open = false; });
  await page.waitForSelector('.lesson-card', {timeout: 60000});
  if (await page.locator('#course-display-name').count()) {
    await page.locator('#course-display-name').fill('흐름검증');
    await page.locator('.course-identity button[type=submit]').click();
  }
  await page.waitForFunction(() => [...document.querySelectorAll('.lesson-card button')].some(b => /학습 시작|이어서/.test(b.textContent) && !b.disabled), null, {timeout: 90000});
  await page.locator('.lesson-card').first().locator('button', {hasText: /학습 시작|이어서/}).first().click();
  await page.waitForSelector('.study-navigation', {timeout: 60000});
  const openTask = async (n) => { await page.locator('.study-navigation button', {hasText: `문제 ${n} ·`}).first().click(); await page.waitForSelector('.cm-editor', {timeout: 30000}); await page.waitForTimeout(300); };

  // 미지원 단계(1번): 버튼 없음, 단축키 무시.
  await openTask(1);
  if (await page.locator('.code-flow-open').count()) fail('1번(코드 흐름 없음)에 버튼이 있음');
  await page.locator('.cm-content').click();
  await page.keyboard.press(`${MOD}+Shift+KeyF`); await page.waitForTimeout(500);
  if (await page.locator('.code-flow-dialog[open]').count()) fail('미지원 단계에서 단축키가 대화상자를 엶');
  else notes.push('미지원 단계: 버튼 없음, 단축키 무시');

  for (const theme of ['light', 'dark']) {
    for (const width of [1440, 820]) {
      const T = `${theme}-${width}`;
      await page.setViewportSize({width, height: 900});
      await page.evaluate((t) => window.mqTheme.set(t), theme);
      await openTask(2);
      const attrs = await page.evaluate(() => { const b = document.querySelector('.code-flow-open'); return b && {label: b.dataset.shortcutLabel, aria: b.getAttribute('aria-keyshortcuts'), title: b.title, visible: !!b.getClientRects().length}; });
      notes.push(`${T} 버튼: ${JSON.stringify(attrs)}`);
      if (!attrs || !attrs.visible) { fail(`${T}: 코드 흐름 버튼이 보이지 않음`); continue; }
      if (attrs.label !== KEY || !/Shift\+F/.test(attrs.aria || '') || !/코드 흐름 보기/.test(attrs.title)) fail(`${T}: 키 표시·aria·설명 불일치`);
      // 처음 열었을 때만 실행 전 상태다(같은 문제를 다시 열면 앞의 실행 결과와 안내가 그대로 남는 것이 정상).
      if (T === 'light-1440' && await page.locator('.code-flow-hint').count()) fail(`${T}: 실행 전인데 결과 안내가 보임`);
      await shot(`F1-before-run-${T}`);
      // 실행 → 결과 영역 안내
      await page.locator('.repository-task [data-shortcut-action="run"]').click();
      // 실행 중에는 단축키가 열지 않는다.
      await page.locator('.cm-content').click({position: {x: 300, y: 20}});
      await page.keyboard.press(`${MOD}+Shift+KeyF`); await page.waitForTimeout(150);
      const openedWhileBusy = await page.evaluate(() => !!document.querySelector('.code-flow-dialog[open]') && document.querySelector('.repository-task')?.dataset.busy === 'true');
      if (openedWhileBusy) fail(`${T}: 실행 중에 단축키로 열림`);
      if (await page.locator('.code-flow-dialog[open]').count()) { await page.keyboard.press('Escape'); await page.waitForTimeout(300); }
      await page.waitForFunction(() => ['finished', 'failed'].includes(document.querySelector('.result-pane')?.dataset.executionState) && document.querySelector('.repository-task')?.dataset.busy !== 'true', null, {timeout: 90000});
      const hint = await page.evaluate(() => { const h = document.querySelector('.code-flow-hint'); return h && {text: h.innerText.replace(/\s+/g, ' ').trim(), visible: !!h.getClientRects().length}; });
      notes.push(`${T} 실행 뒤 안내: ${JSON.stringify(hint)}`);
      if (!hint || !hint.visible || !hint.text.includes(KEY)) fail(`${T}: 실행 뒤 결과 영역 안내가 없음/키 없음`);
      await shot(`F2-after-run-${T}`);
      // 편집기 포커스에서 단축키로 열기 → 다음 → 이전 → 닫기 → 코드 그대로
      const before = await page.evaluate(() => window.molipCodeEditors.getValue());
      await page.locator('.cm-content').click({position: {x: 300, y: 20}});
      await page.keyboard.press(`${MOD}+Shift+KeyF`);
      const opened = await page.waitForSelector('.code-flow-dialog[open] .code-flow-view:not(:empty)', {timeout: 60000}).then(() => true, () => false);
      if (!opened) { fail(`${T}: 단축키로 코드 흐름이 열리지 않음`); continue; }
      const step0 = await page.locator('.code-flow-dialog .tv-position').innerText().catch(() => '');
      await page.locator('.code-flow-dialog button', {hasText: '다음'}).first().click(); await page.waitForTimeout(200);
      const step1 = await page.locator('.code-flow-dialog .tv-position').innerText().catch(() => '');
      await page.locator('.code-flow-dialog button', {hasText: '이전'}).first().click(); await page.waitForTimeout(200);
      const step2 = await page.locator('.code-flow-dialog .tv-position').innerText().catch(() => '');
      notes.push(`${T} 단계 표시: ${step0.replace(/\s+/g, ' ')} → ${step1.replace(/\s+/g, ' ')} → ${step2.replace(/\s+/g, ' ')}`);
      if (step0 === step1 || step0 !== step2) fail(`${T}: 다음·이전 이동 이상`);
      await shot(`F3-open-${T}`);
      await page.keyboard.press('Escape'); await page.waitForTimeout(400);
      if (await page.locator('.code-flow-dialog[open]').count()) fail(`${T}: Esc로 닫히지 않음`);
      const after = await page.evaluate(() => window.molipCodeEditors.getValue());
      if (after !== before) fail(`${T}: 닫은 뒤 편집기 코드가 바뀜`);
      const focus = await page.evaluate(() => document.activeElement?.closest('.cm-editor') ? 'editor' : (document.activeElement?.className || document.activeElement?.tagName));
      notes.push(`${T} 닫은 뒤 포커스: ${focus}`);
      // 결과 영역 안내 버튼으로 열기
      await page.locator('.code-flow-hint-open').click();
      const viaHint = await page.waitForSelector('.code-flow-dialog[open] .code-flow-view:not(:empty)', {timeout: 60000}).then(() => true, () => false);
      if (!viaHint) fail(`${T}: 안내 버튼으로 열리지 않음`);
      await page.keyboard.press('Escape'); await page.waitForTimeout(300);
    }
  }
  // 단축키 안내 창
  await page.evaluate(() => window.mqTheme.set('light'));
  await page.setViewportSize({width: 1440, height: 900});
  await page.locator('.repository-study .shortcut-sheet-open').click();
  await page.waitForSelector('.shortcut-sheet[open]');
  const sheetRow = await page.evaluate(() => [...document.querySelectorAll('.shortcut-sheet tr')].map((r) => r.innerText.replace(/\s+/g, ' ')).find((t) => t.includes('코드 흐름')));
  notes.push(`단축키 안내: ${sheetRow}`);
  if (!sheetRow || !sheetRow.includes('Shift+F')) fail('단축키 안내 창에 코드 흐름 항목이 없음');
  await shot('F4-shortcut-sheet');
  await page.keyboard.press('Escape');
  notes.push(`TOTAL FAIL ${notes.filter((n) => n.startsWith('FAIL')).length}`);
  return notes;
};
