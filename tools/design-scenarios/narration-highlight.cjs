// 재현 루프(2026-10-30 사용자 스크린샷: 「recall_score 함수가 잘 안 보여」).
// AICE 「지연 경보의 성능을 판단해요」 1번 문제의 실제 코드를 편집기에 넣고, 해설이 쓰는 것과 같은 API로
// 행 강조(highlightLines)와 토큰 구간 강조(highlightRange)를 겹친다. 강조 안의 모든 구문 토큰이 그 바탕에서
// 읽히는지(>= 4.5:1), 강조 테두리가 보이는지(바탕과 >= 3:1)를 밝게·어둡게 × 포커스 없음/있음 × 선택 겹침에서 잰다.
const fs = require('node:fs');
const path = require('node:path');

const CODE = `from sklearn.metrics import accuracy_score, recall_score

# 정상 아홉 건과 지연 한 건을 모두 정상으로 예측했어요.
y_true = [0] * 9 + [1]
y_pred = [0] * 10
print(float(accuracy_score(y_true, y_pred)))
# 이 줄을 고쳐 정확도 대신 실제 지연 중 찾아낸 비율(지연 재현율)을 report에 담으세요.
report = recall_score(y_true, y_pred, pos_label=1)
print(float(report))
`;

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
  await page.locator('#course-display-name').fill('강조검증');
  await page.locator('.course-identity button[type=submit]').click();
  await page.waitForFunction(() => [...document.querySelectorAll('.lesson-card button')].some(b => b.textContent.includes('학습 시작') && !b.disabled), null, {timeout: 30000});
  await page.locator('.lesson-card').nth(4).locator('button', {hasText: '학습 시작'}).click();
  await page.waitForSelector('.study-navigation', {timeout: 60000});
  await page.locator('.study-navigation button', {hasText: '문제 1 ·'}).first().click();
  await page.waitForSelector('.cm-editor', {timeout: 30000});
  await page.evaluate((code) => window.molipCodeEditors.setValue(code), CODE);
  await page.waitForTimeout(300);
  // "report = recall_score" on line 8, as the narration targets it.
  const range = await page.evaluate(() => {
    const view = document.querySelector('.cm-content'); const text = window.molipCodeEditors.getValue();
    const from = text.indexOf('report = recall_score'); return [from, from + 'report = recall_score'.length];
  });

  const measure = (label) => page.evaluate((label) => {
    const parse = (v) => { const m = v.match(/[\d.]+/g).map(Number); return {r: m[0], g: m[1], b: m[2], a: m.length > 3 ? m[3] : 1}; };
    const lum = ({r, g, b}) => { const f = (c) => { c /= 255; return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4; }; return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b); };
    const ratio = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return (x + 0.05) / (y + 0.05); };
    // The colour actually under a token: every translucent layer from the editor up to it, composited.
    const under = (el) => { const chain = []; for (let n = el; n && !n.classList?.contains('cm-editor'); n = n.parentElement) { const c = parse(getComputedStyle(n).backgroundColor); if (c.a > 0) chain.push(c); }
      let o = parse(getComputedStyle(document.querySelector('.cm-editor')).backgroundColor);
      // CodeMirror draws selection in a layer behind the text: include it where it covers the token.
      const rect = el.getBoundingClientRect(); for (const s of document.querySelectorAll('.cm-selectionBackground')) { const r = s.getBoundingClientRect(); if (r.left < rect.right && r.right > rect.left && r.top < rect.bottom && r.bottom > rect.top) chain.push(parse(getComputedStyle(s).backgroundColor)); }
      for (const c of chain.reverse()) o = {r: c.r * c.a + o.r * (1 - c.a), g: c.g * c.a + o.g * (1 - c.a), b: c.b * c.a + o.b * (1 - c.a), a: 1};
      return o; };
    const mark = document.querySelector('.cm-narration-span');
    if (!mark) return {label, error: 'no span'};
    const tokens = [mark, ...mark.querySelectorAll('span')].filter((el) => [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim()));
    const rows = tokens.map((el) => ({text: [...el.childNodes].filter((n) => n.nodeType === 3).map((n) => n.textContent).join('').trim(), ratio: ratio(parse(getComputedStyle(el).color), under(el))}));
    const line = document.querySelector('.cm-narration-line');
    const outside = line ? [...line.querySelectorAll(':scope > span')].filter((el) => !el.closest('.cm-narration-span') && el.textContent.trim()).map((el) => ({text: el.textContent.trim(), ratio: ratio(parse(getComputedStyle(el).color), under(el))})) : [];
    const s = getComputedStyle(mark);
    const ringColor = s.outlineStyle !== 'none' ? s.outlineColor : s.boxShadow.match(/rgba?\([^)]+\)/)?.[0];
    const ring = ringColor ? ratio(parse(ringColor), under(mark.parentElement)) : 0;
    return {label, rows, outside, ring, bg: s.backgroundColor};
  }, label);

  const check = async (label) => {
    const r = await measure(label);
    if (r.error) { fail(`${label}: ${r.error}`); return; }
    const low = [...r.rows, ...r.outside].filter((x) => x.ratio < 4.5);
    notes.push(`${label}: 강조 안 ${r.rows.map((x) => `${x.text}=${x.ratio.toFixed(1)}`).join(' ')} | 같은 행 ${r.outside.map((x) => `${x.text}=${x.ratio.toFixed(1)}`).join(' ')} | 테두리 ${r.ring.toFixed(1)} bg ${r.bg}`);
    if (low.length) fail(`${label}: 낮은 대비 ${low.map((x) => `${x.text} ${x.ratio.toFixed(2)}`).join(', ')}`);
    if (r.ring < 3) fail(`${label}: 강조 테두리가 바탕과 구분되지 않음 ${r.ring.toFixed(2)}`);
    await shot(label);
  };

  for (const theme of ['light', 'dark']) {
    await page.evaluate((t) => window.mqTheme.set(t), theme); await page.waitForTimeout(250);
    await page.evaluate(([a, b]) => { window.molipCodeEditors.highlightLines(8, 8); window.molipCodeEditors.highlightRange(a, b); document.activeElement?.blur(); }, range);
    await page.waitForTimeout(250);
    await check(`${theme}-line+span`);
    // Focus in the editor (active line + cursor) on the same line.
    await page.locator('.cm-line').nth(7).click({position: {x: 400, y: 6}});
    await page.evaluate(([a, b]) => { window.molipCodeEditors.highlightLines(8, 8); window.molipCodeEditors.highlightRange(a, b); }, range);
    await page.waitForTimeout(200);
    await check(`${theme}-focused`);
    // A learner selection over the highlighted tokens.
    await page.locator('.cm-line').nth(7).click({position: {x: 5, y: 6}});
    await page.keyboard.press('Shift+End');
    await page.waitForTimeout(200);
    const selected = await page.evaluate(() => document.querySelectorAll('.cm-selectionBackground').length);
    notes.push(`${theme} 선택 레이어 ${selected}개`); if (!selected) fail(`${theme}: 선택이 만들어지지 않음`);
    await check(`${theme}-selection`);
    await page.keyboard.press('ArrowRight');
  }
  notes.push(`TOTAL FAIL ${notes.filter((n) => n.startsWith('FAIL')).length}`);
  return notes;
};
