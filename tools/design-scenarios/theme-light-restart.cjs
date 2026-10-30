// 다시 연 앱: 저장한 밝게가 첫 화면부터(OS 어둡게여도) 적용되고, 편집기·터미널 토큰도 밝은지 확인한다.
module.exports = async ({page, shot}) => {
  const notes = [];
  await page.emulateMedia({colorScheme: 'dark'});
  await page.waitForFunction(() => document.documentElement.dataset.themeChoice !== undefined, null, {timeout: 60000});
  const s = await page.evaluate(() => ({choice: document.documentElement.dataset.themeChoice, effective: document.documentElement.dataset.theme,
    bg: getComputedStyle(document.documentElement).backgroundColor, editor: getComputedStyle(document.documentElement).getPropertyValue('--editor-bg').trim(),
    term: getComputedStyle(document.documentElement).getPropertyValue('--term-bg').trim()}));
  notes.push('after restart: ' + JSON.stringify(s));
  if (s.choice !== 'light' || s.effective !== 'light' || s.editor !== '#ffffff' || s.term !== '#ffffff') notes.push('FAIL 밝게가 재시작 뒤 유지되지 않음');
  await page.waitForTimeout(1500); await shot('restart-light');
  return notes;
};
