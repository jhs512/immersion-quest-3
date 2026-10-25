// 관리자 자동 풀이 running and stopped, in both looks (OS scheme emulated, never changed).
const fs = require('node:fs');
const path = require('node:path');
module.exports = async ({page, shot, dataDir}) => {
  const notes = [];
  const button = (name) => page.getByRole('button', {name, exact: true});
  fs.writeFileSync(path.join(dataDir, 'pilot-course-reviewer'), '');
  await page.setViewportSize({width: 1440, height: 900});
  await page.emulateMedia({colorScheme: 'light'});
  await page.waitForSelector('.pilot-toolbox', {timeout: 60000});
  await page.evaluate(() => { document.querySelector('.pilot-toolbox').open = true; });
  await button('버전 본').click();
  await page.evaluate(() => { document.querySelector('.pilot-toolbox').open = false; });
  await page.waitForFunction(() => document.querySelectorAll('.lesson-card').length > 30, null, {timeout: 60000});
  await page.locator('#course-display-name').fill('디자인검증');
  await page.locator('.course-identity button[type=submit]').click();
  await page.waitForFunction(() => [...document.querySelectorAll('.lesson-card button.primary')].some(b => !b.disabled), null, {timeout: 30000});
  await page.locator('.lesson-card').nth(1).locator('button.primary').click();
  await page.waitForSelector('#auto-run-start:not([disabled])', {timeout: 60000});
  for (const scheme of ['light', 'dark']) {
    await page.emulateMedia({colorScheme: scheme});
    await page.locator('#auto-run-start').click();
    await page.waitForSelector('.auto-run-control[data-state="running"]', {timeout: 30000});
    await page.waitForTimeout(1500);
    await shot(`a-${scheme}-running`);
    await page.keyboard.press('Escape');
    await page.waitForSelector('.auto-run-control:not([data-state="running"])', {timeout: 30000});
    await page.locator('.auto-run-details > summary').click();
    await shot(`a-${scheme}-stopped`);
    notes.push(`${scheme}: ${await page.evaluate(() => document.documentElement.dataset.theme)}`);
    await page.locator('.auto-run-dismiss').click();
  }
  return notes;
};
