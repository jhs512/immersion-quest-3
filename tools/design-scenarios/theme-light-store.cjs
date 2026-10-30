// 밝게를 앱 설정에서 골라 저장한다(OS는 어둡게로 흉내). 다음 실행(theme-light-restart.cjs)이 같은 폴더로 다시 연다.
module.exports = async ({page, shot}) => {
  await page.emulateMedia({colorScheme: 'dark'});
  await page.waitForSelector('.app-update-settings > summary', {timeout: 60000});
  await page.locator('.app-update-settings > summary').first().click();
  await page.locator('input[name="mq-theme-choice"][value="light"]').check({force: true});
  await page.waitForFunction(() => document.documentElement.dataset.themeChoice === 'light' && document.documentElement.dataset.theme === 'light');
  await shot('store-light');
  return ['stored 밝게 over OS dark'];
};
