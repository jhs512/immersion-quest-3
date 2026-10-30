// 라이트 감사에서 준비 시간 초과로 확인하지 못한 수업 카드(24번)를 밝게에서 직접 연다.
// 준비 상태와 상관없이 일정 간격으로 화면과 상태(gitReady, 터미널 유무, 오류 문구)를 남기고,
// 같은 화면 검사(어두운 배경·낮은 대비)를 적용한다.
const fs = require('node:fs');
const path = require('node:path');

module.exports = async ({page, shot, dataDir, output}) => {
  const notes = [];
  const button = (name) => page.getByRole('button', {name, exact: true});
  await page.setViewportSize({width: 1440, height: 900});
  await page.emulateMedia({colorScheme: 'dark'});
  await page.waitForSelector('.pilot-toolbox', {timeout: 60000});
  await page.evaluate(() => { document.querySelector('.pilot-toolbox').open = true; });
  await button('버전 본').click();
  await page.evaluate(() => { document.querySelector('.pilot-toolbox').open = false; });
  await page.waitForFunction(() => document.querySelectorAll('.lesson-card').length > 30, null, {timeout: 60000});
  await page.locator('.app-update-settings > summary').click();
  await page.locator('input[name="mq-theme-choice"][value="light"]').check({force: true});
  await page.waitForFunction(() => document.documentElement.dataset.theme === 'light');
  await page.locator('.app-update-settings > summary').click();
  await page.locator('#course-display-name').fill('라이트검증');
  await page.locator('.course-identity button[type=submit]').click();
  await page.waitForFunction(() => [...document.querySelectorAll('.lesson-card button')].some(b => b.textContent.includes('학습 시작') && !b.disabled), null, {timeout: 30000});
  const card = page.locator('.lesson-card').nth(24);
  notes.push('card 24: ' + (await card.locator('h3').innerText()).trim());
  await card.scrollIntoViewIfNeeded();
  await card.locator('button', {hasText: '학습 시작'}).click();
  await page.waitForSelector('.study-navigation', {timeout: 60000});
  await page.locator('.study-navigation button', {hasText: '문제 1 ·'}).first().click();
  for (const seconds of [5, 30, 90, 180]) {
    await page.waitForTimeout(seconds === 5 ? 5000 : (seconds === 30 ? 25000 : (seconds === 90 ? 60000 : 90000)));
    const state = await page.evaluate(() => {
      const t = document.querySelector('.repository-task');
      return {gitReady: t?.dataset.gitReady ?? null, terminal: !!document.querySelector('.xterm'),
        status: [...document.querySelectorAll('.repository-task .execution-status,.repository-task [role=status],.git-terminal-shell>p')].map(e => e.textContent.trim()).filter(Boolean).slice(0, 4)};
    });
    notes.push(`after ${seconds}s: ${JSON.stringify(state)}`);
    await shot(`C24-${seconds}s`);
  }
  return notes;
};
