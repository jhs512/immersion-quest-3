// Finish-review captures: catalog and lesson at desktop (1440) and phone width (390).
module.exports = async ({page, shot}) => {
  const notes = [];
  const button = (name) => page.getByRole('button', {name, exact: true});
  await page.setViewportSize({width: 1440, height: 900});
  await page.waitForSelector('.pilot-toolbox', {timeout: 60000});
  await page.evaluate(() => { document.querySelector('.pilot-toolbox').open = true; });
  await button('버전 본').click();
  await page.evaluate(() => { document.querySelector('.pilot-toolbox').open = false; });
  await page.waitForFunction(() => document.querySelectorAll('.lesson-card').length > 30, null, {timeout: 60000});
  await page.locator('#course-display-name').fill('디자인검증');
  await page.locator('.course-identity button[type=submit]').click();
  await page.waitForFunction(() => [...document.querySelectorAll('.lesson-card button.primary')].some(b => !b.disabled), null, {timeout: 30000});
  // One real pass so the route shows started, in-progress and next states.
  await page.locator('.lesson-card').nth(1).locator('button.primary').click();
  await page.waitForSelector('.answer-option', {timeout: 60000});
  await page.locator('.answer-option', {hasText: /^\s*2\s*$/}).first().click();
  await page.locator('.repository-task [data-shortcut-action="submit"]').click();
  await page.waitForSelector('.task-passed-dialog', {timeout: 60000});
  await button('여기 머물기').click();
  await page.evaluate(() => scrollTo(0, 0));
  await shot('lesson-desktop');
  await page.setViewportSize({width: 390, height: 844});
  await shot('lesson-mobile');
  await page.setViewportSize({width: 1440, height: 900});
  await button('← 코스 수업 목록').click();
  await page.waitForSelector('.next-station[data-state="started"]', {timeout: 30000});
  await page.evaluate(() => scrollTo(0, 0));
  await shot('desktop', {fullPage: true});
  await page.setViewportSize({width: 390, height: 844});
  await page.evaluate(() => scrollTo(0, 0));
  await shot('mobile', {fullPage: true});
  notes.push('catalog and lesson captured after one recorded pass in lesson 2');
  return notes;
};
