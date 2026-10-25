// Theme checks on the real course, with the OS colour scheme emulated through DevTools (the
// person's OS setting is never touched). Fails loudly on any wrong effective theme.
const fs = require('node:fs');
const path = require('node:path');

module.exports = async ({page, shot, dataDir}) => {
  const notes = [];
  const button = (name) => page.getByRole('button', {name, exact: true});
  const os = async (scheme) => { await page.emulateMedia({colorScheme: scheme}); await page.waitForTimeout(120); };
  const state = () => page.evaluate(() => ({
    choice: document.documentElement.dataset.themeChoice, effective: document.documentElement.dataset.theme,
    wall: getComputedStyle(document.documentElement).getPropertyValue('--wall').trim(),
    bg: getComputedStyle(document.body).backgroundColor, scheme: getComputedStyle(document.documentElement).colorScheme,
    checked: document.querySelector('input[name="mq-theme-choice"]:checked')?.value ?? null,
  }));
  const expect = async (label, choice, effective) => {
    const s = await state();
    const wallDark = s.wall === '#161f2e';
    if (s.choice !== choice || s.effective !== effective || wallDark !== (effective === 'dark') || (s.checked && s.checked !== choice)) throw Error(`${label}: ${JSON.stringify(s)}`);
    notes.push(`ok ${label}: choice=${s.choice} effective=${s.effective} body=${s.bg} scheme=${s.scheme}`);
  };
  const settings = async (open) => {
    const isOpen = await page.evaluate(() => !!document.querySelector('.app-update-settings')?.open);
    if (isOpen !== open) await page.locator('.app-update-settings > summary').click();
    await page.waitForFunction((open) => !!document.querySelector('.app-update-settings')?.open === open, open);
  };
  const choose = async (key) => {
    await settings(true);
    await page.locator(`input[name="mq-theme-choice"][value="${key}"]`).check({force: true});
    try { await page.waitForFunction((key) => document.documentElement.dataset.themeChoice === key, key, {timeout: 5000}); }
    catch (error) { throw Error('choose ' + key + ': ' + JSON.stringify(await page.evaluate(() => ({html: document.documentElement.dataset.themeChoice, menus: document.querySelectorAll('.app-update-settings').length, open: [...document.querySelectorAll('.app-update-settings')].map(d => d.open), radios: [...document.querySelectorAll('input[name="mq-theme-choice"]')].map(r => r.value + ':' + r.checked)})))); }
  };
  const stored = () => { try { return JSON.parse(fs.readFileSync(path.join(dataDir, 'prefs.json'), 'utf8')).theme ?? '(none)'; } catch { return '(no file)'; } };

  await page.setViewportSize({width: 1440, height: 900});
  await os('light');
  await page.waitForSelector('.pilot-toolbox', {timeout: 60000});
  await expect('first start, OS light', 'system', 'light');
  notes.push(`stored before any choice: ${stored()}`);
  await page.evaluate(() => { document.querySelector('.pilot-toolbox').open = true; });
  await button('버전 본').click();
  await page.evaluate(() => { document.querySelector('.pilot-toolbox').open = false; });
  await page.waitForFunction(() => document.querySelectorAll('.lesson-card').length > 30, null, {timeout: 60000});
  await shot('t01-catalog-name-light', {});
  await os('dark');
  await expect('OS switches to dark at runtime (시스템)', 'system', 'dark');
  await shot('t02-catalog-name-system-dark');
  await page.locator('#course-display-name').fill('디자인검증');
  await page.locator('.course-identity button[type=submit]').click();
  await page.waitForFunction(() => [...document.querySelectorAll('.lesson-card button.primary')].some(b => !b.disabled), null, {timeout: 30000});
  await shot('t03-catalog-system-dark');
  await settings(true);
  await shot('t04-settings-system-dark');
  // keyboard: arrow keys move the radio choice natively
  await page.locator('input[name="mq-theme-choice"]:checked').focus();
  await page.keyboard.press('ArrowRight');
  await page.waitForFunction(() => document.documentElement.dataset.themeChoice === 'light');
  await expect('keyboard arrow picks 밝게 while OS is dark', 'light', 'light');
  notes.push(`stored after keyboard choice: ${stored()}`);
  await shot('t05-settings-light-over-os-dark');
  await settings(false);
  await os('light'); await os('dark');
  await expect('explicit 밝게 ignores OS changes', 'light', 'light');
  await choose('dark');
  await settings(false);
  await os('light');
  await expect('explicit 어둡게 ignores OS light', 'dark', 'dark');
  notes.push(`stored after 어둡게: ${stored()}`);
  await page.locator('.lesson-card').nth(26).scrollIntoViewIfNeeded();
  await shot('t06-catalog-route-dark');
  await page.evaluate(() => scrollTo(0, 0));
  await button('분류별').isDisabled().then(d => notes.push(`분류별 disabled without categories: ${d}`));
  await button('도전 과제').click(); await page.waitForTimeout(1200); await shot('t07-challenges-dark'); await button('수업 목록').click();
  await page.locator('.course-search input').fill('없는과정'); await shot('t08-search-empty-dark'); await page.locator('.course-search input').fill('');
  // lesson in dark
  await page.locator('.lesson-card').nth(1).locator('button.primary').click();
  await page.waitForSelector('.cm-editor', {timeout: 60000});
  await expect('lesson keeps 어둡게', 'dark', 'dark');
  await shot('t10-problem-dark');
  await page.locator('.repository-task [data-shortcut-action="submit"]').click();
  await page.waitForFunction(() => ['passed', 'incorrect', 'error'].includes(document.querySelector('.result-pane')?.dataset.feedback), null, {timeout: 60000});
  await shot('t11-feedback-dark');
  if (await button('여기 머물기').count()) await button('여기 머물기').click();
  await page.locator('.lesson-info-trigger').click();
  await page.waitForFunction(() => document.getElementById('lesson-info-dialog')?.open);
  await shot('t12-info-dialog-dark'); await page.keyboard.press('Escape');
  await page.locator('.content-update-controls > details > summary').click(); await shot('t13-lesson-settings-dark'); await page.locator('.content-update-controls > details > summary').click();
  await page.locator('.repository-study .shortcut-sheet-open').click(); await shot('t14-shortcuts-dark'); await page.keyboard.press('Escape');
  // narration highlight in dark, then stop restores the plain brief
  const play = page.locator('.repository-task .narration-play');
  await play.click();
  await page.waitForFunction(() => document.querySelector('.repository-task')?.dataset.narrating === 'true', null, {timeout: 30000});
  await page.waitForSelector('.agent-caption', {timeout: 30000}).catch(() => {});
  await page.waitForTimeout(1800);
  const during = await page.evaluate(() => ({spot: !!document.querySelector('.agent-spotlight'), caption: !!document.querySelector('.agent-caption'), border: document.querySelector('.agent-spotlight') && getComputedStyle(document.querySelector('.agent-spotlight')).borderTopColor}));
  notes.push(`narration in dark: ${JSON.stringify(during)}`);
  await shot('t15-narration-dark');
  await page.locator('.repository-task .narration-stop').click();
  await page.waitForFunction(() => document.querySelector('.repository-task')?.dataset.narrating === 'false', null, {timeout: 30000});
  await page.waitForTimeout(600);
  const after = await page.evaluate(() => ({spotVisible: [...document.querySelectorAll('.agent-spotlight')].some(e => e.getBoundingClientRect().width > 0 && getComputedStyle(e).opacity !== '0' && getComputedStyle(e).display !== 'none'), said: document.querySelectorAll('.agent-said').length}));
  notes.push(`after stop: ${JSON.stringify(after)}`);
  await expect('after narration stop', 'dark', 'dark');
  await shot('t16-after-stop-dark');
  await page.setViewportSize({width: 820, height: 760}); await shot('t17-problem-narrow-dark'); await page.setViewportSize({width: 1440, height: 900});
  // terminal lesson in dark
  await button('← 코스 수업 목록').click();
  await page.waitForSelector('.course-catalog');
  await expect('back on the course list', 'dark', 'dark');
  await shot('t18-catalog-after-study-dark');
  await page.locator('.lesson-card').nth(2).locator('button.primary').click();
  await page.locator('.study-navigation button', {hasText: '문제 2 ·'}).first().click();
  await page.waitForFunction(() => document.querySelector('.repository-task')?.dataset.gitReady === 'true', null, {timeout: 120000});
  await page.waitForTimeout(1200);
  await shot('t19-git-terminal-dark');
  await button('← 코스 수업 목록').click();
  await page.setViewportSize({width: 820, height: 760}); await page.evaluate(() => scrollTo(0, 0)); await shot('t20-catalog-narrow-dark');
  await page.setViewportSize({width: 1440, height: 900});
  // light screens of the same states for the pair
  await choose('light'); await settings(false);
  await expect('back to 밝게', 'light', 'light');
  await shot('t21-catalog-light');
  await page.locator('.lesson-card').nth(1).locator('button.primary').click();
  await page.waitForSelector('.cm-editor', {timeout: 60000});
  await shot('t22-problem-light');
  await button('← 코스 수업 목록').click();
  // leave 어둡게 stored for the restart check
  await choose('dark'); await settings(false);
  notes.push(`stored at end: ${stored()}`);
  return notes;
};
