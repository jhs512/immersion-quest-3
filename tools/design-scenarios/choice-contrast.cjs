// 객관식 선택 상태의 글자 대비를 밝게·어둡게에서 잰다. 검증 모드 정보처리기사 과정(버전 정)의
// 저장소 수업 첫 객관식 문제에서
// 선택 전, 선택(오답), 오답 제출 뒤, 키보드 초점, 잠김(해설·채점 중), 정답 선택을 찍고
// 선택된 줄의 배경·글자·테두리 색과 WCAG 대비를 notes에 남긴다.
const path = require('node:path');

const channel = (c) => { c /= 255; return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4; };
const luminance = (rgb) => { const [r, g, b] = rgb.match(/[\d.]+/g).map(Number); return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b); };
const contrast = (a, b) => { const [x, y] = [luminance(a), luminance(b)].sort((p, q) => q - p); return ((x + 0.05) / (y + 0.05)).toFixed(2); };

module.exports = async ({page, shot, output}) => {
  const notes = [];
  const failures = [];
  const button = (name) => page.getByRole('button', {name, exact: true});
  const setTheme = async (key) => {
    await page.locator('.app-update-settings > summary').click();
    await page.locator(`input[name="mq-theme-choice"][value="${key}"]`).check({force: true});
    await page.waitForFunction((k) => document.documentElement.dataset.theme === k, key);
    await page.locator('.app-update-settings > summary').click();
  };
  const measure = async (label, selector) => {
    const s = await page.evaluate((sel) => {
      const option = document.querySelector(sel);
      const style = getComputedStyle(option);
      const text = getComputedStyle(option.querySelector('span'));
      const radio = getComputedStyle(option.querySelector('input'));
      return {theme: document.documentElement.dataset.theme, bg: style.backgroundColor, rule: style.borderTopColor, ink: text.color,
        opacity: text.opacity, accent: radio.accentColor, well: getComputedStyle(option.closest('.coding-pane') ?? document.body).backgroundColor};
    }, selector);
    // A transparent option sits on the well, so the well is the background the text is read on.
    const bg = /rgba\(.*, 0\)$/.test(s.bg) || s.bg === 'transparent' ? s.well : s.bg;
    const result = {label, ...s, text_contrast: contrast(s.ink, bg), rule_vs_well: contrast(s.rule, s.well)};
    notes.push(JSON.stringify(result));
    if (Number(result.text_contrast) < 4.5) failures.push(`${label} 글자 대비 ${result.text_contrast} < 4.5`);
    return result;
  };
  const option = (index) => page.locator('.answer-option').nth(index);
  const capture = async (name) => {
    await shot(name);
    await page.locator('.answer-interaction').first().screenshot({path: path.join(output, `${name}-choices.png`)});
  };

  await page.setViewportSize({width: 1440, height: 900});
  await page.emulateMedia({colorScheme: 'light'});
  await page.waitForSelector('.pilot-toolbox', {timeout: 60000});
  await page.evaluate(() => { document.querySelector('.pilot-toolbox').open = true; });
  await button('버전 정').click();
  await page.evaluate(() => { document.querySelector('.pilot-toolbox').open = false; });
  await page.waitForFunction(() => document.querySelectorAll('.lesson-card').length > 20, null, {timeout: 60000});
  await setTheme('light');
  await page.locator('#course-display-name').fill('대비검증');
  await page.locator('.course-identity button[type=submit]').click();
  await page.waitForFunction(() => [...document.querySelectorAll('.lesson-card button.primary')].some(b => !b.disabled), null, {timeout: 30000});
  const lesson = page.locator('.lesson-card').nth(17);
  notes.push('lesson: ' + (await lesson.locator('h3').innerText()).trim());
  await lesson.scrollIntoViewIfNeeded();
  await lesson.locator('button.primary').click();
  await page.waitForSelector('.study-navigation', {timeout: 60000});
  const tasks = page.locator('.study-navigation button', {hasText: /문제 \d+ ·/});
  for (let i = 0; i < await tasks.count() && !await page.locator('.answer-option').count(); i++) {
    await tasks.nth(i).click();
    await page.waitForTimeout(1500);
  }
  await page.waitForSelector('.answer-option', {timeout: 10000});
  notes.push('task: ' + await page.locator('.study-navigation [aria-current], .study-navigation .current').first().innerText().catch(() => '?'));
  const texts = await page.locator('.answer-option').allInnerTexts();
  notes.push('options: ' + JSON.stringify(texts.map(t => t.trim())));

  await measure('light unselected', '.answer-option');
  await capture('light-1-unselected');
  await option(0).click();
  await measure('light selected', '.answer-option:has(input:checked)');
  await option(1).hover();
  await capture('light-2-selected');
  await page.locator('.repository-task [data-shortcut-action="submit"]').click();
  await page.waitForFunction(() => ['passed', 'incorrect', 'error'].includes(document.querySelector('.result-pane')?.dataset.feedback), null, {timeout: 90000});
  const feedback = await page.evaluate(() => document.querySelector('.result-pane')?.dataset.feedback);
  notes.push('feedback after submit: ' + feedback);
  if (await button('여기 머물기').count()) await button('여기 머물기').click();
  await measure(`light selected after ${feedback}`, '.answer-option:has(input:checked)');
  await capture('light-3-after-submit');
  await page.locator('.answer-option:has(input:checked) input').focus();
  await page.keyboard.press('ArrowDown');
  await measure('light keyboard-moved selection', '.answer-option:has(input:checked)');
  notes.push('focus-visible on radio: ' + await page.evaluate(() => !!document.querySelector('.answer-option input:focus-visible')));
  await capture('light-4-keyboard-focus');
  await option(1).click();
  // 해설·채점 중에는 fieldset이 잠긴다. 그 상태의 선택 줄도 읽혀야 한다.
  await page.evaluate(() => { document.querySelector('.answer-interaction').disabled = true; });
  await measure('light selected while locked', '.answer-option:has(input:checked)');
  await capture('light-5-locked');
  await page.evaluate(() => { document.querySelector('.answer-interaction').disabled = false; });

  await setTheme('dark');
  await measure('dark unselected', '.answer-option:not(:has(input:checked))');
  await measure('dark selected', '.answer-option:has(input:checked)');
  await capture('dark-1-selected');
  if (failures.length) notes.push('FAIL ' + failures.join('; '));
  return notes;
};
