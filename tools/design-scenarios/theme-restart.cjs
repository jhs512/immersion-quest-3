// Relaunch on the folder theme.cjs used: the stored choice must be on <html> at the first script
// that can observe the page, with the dark ground already painted, while the OS is emulated light.
module.exports = async ({page, shot}) => {
  const notes = [];
  await page.waitForFunction(() => document.documentElement.dataset.themeChoice !== undefined && document.head, null, {timeout: 60000});
  const first = await page.evaluate(() => {
    const head = document.head.innerHTML;
    return {choice: document.documentElement.dataset.themeChoice, bg: getComputedStyle(document.documentElement).backgroundColor,
      bootScriptAt: head.indexOf('themeChoice='), firstAppStyleAt: head.search(/<style[^>]*>(?!html\{background)/), mounted: !!document.querySelector('.repository-player,.repository-study')};
  });
  notes.push(`first observation after launch: ${JSON.stringify(first)}`);
  await page.emulateMedia({colorScheme: 'light'});
  await page.waitForSelector('.course-catalog,.pilot-toolbox', {timeout: 60000});
  const later = await page.evaluate(() => ({choice: document.documentElement.dataset.themeChoice, effective: document.documentElement.dataset.theme, checked: null}));
  if (later.choice !== process.env.MQ3_EXPECT_CHOICE || later.effective !== process.env.MQ3_EXPECT_EFFECTIVE) throw Error('restart: ' + JSON.stringify(later));
  await page.evaluate(() => { const d = document.querySelector('.app-update-settings'); if (d) d.open = true; });
  const checked = await page.evaluate(() => document.querySelector('input[name="mq-theme-choice"]:checked')?.value);
  if (checked !== process.env.MQ3_EXPECT_CHOICE) throw Error('settings show ' + checked);
  notes.push(`after restart: choice=${later.choice} effective=${later.effective} settings=${checked}`);
  await shot('r01-restart');
  return notes;
};
