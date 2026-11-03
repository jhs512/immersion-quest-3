// node tools/design-capture.cjs .scratch/mq-logout/logout-scenario.cjs <out>
// MQ_LOGOUT_STEP=logout | restart. Validation transport only; gh never runs (pilot_source::gh_logout).
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

const digest = dir => Object.fromEntries(fs.readdirSync(dir).filter(name => !name.startsWith('github-signed-out'))
  .filter(name => fs.statSync(path.join(dir, name)).isFile())
  .map(name => {
    const file = path.join(dir, name);
    // An open SQLite file can be locked against reads on Windows; size and mtime still show a write.
    try { return [name, crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex').slice(0, 12)]; }
    catch { const st = fs.statSync(file); return [name, `${st.size}@${st.mtimeMs}`]; }
  }));
const assert = (ok, message) => { if (!ok) throw Error(message); };

module.exports = async ({page, shot, dataDir}) => {
  const notes = {};
  const step = process.env.MQ_LOGOUT_STEP || 'logout';
  if (step === 'logout') {
    await page.locator('button.account-logout-open').waitFor();
    await shot('01-catalog-with-logout');
    await page.click('button.account-logout-open');
    await page.locator('#github-logout-dialog').waitFor();
    await shot('02-confirm-dialog');
    await page.click('#github-logout-dialog button:has-text("취소")');
    await page.locator('#github-logout-dialog').waitFor({state: 'detached'});
    assert(await page.locator('button.account-logout-open').isVisible(), 'cancel keeps the account signed in');
    assert(!fs.existsSync(path.join(dataDir, 'github-signed-out')), 'cancel writes no marker');
    notes.cancel = 'dialog closed, still signed in, no marker';
    const before = digest(dataDir);
    await page.click('button.account-logout-open');
    await page.click('#github-logout-dialog button.account-reset-confirm');
    await page.locator('.gh-signed-out').waitFor();
    await shot('03-signed-out', {fullPage: true});
    assert(await page.locator('button.account-logout-open').count() === 0, 'no account controls after logout');
    assert(fs.readFileSync(path.join(dataDir, 'github-signed-out'), 'utf8') === 'mq3-validation', 'marker names the account');
    const after = digest(dataDir);
    notes.changed_files = Object.keys({...before, ...after}).filter(name => before[name] !== after[name]);
    notes.signed_out_text = await page.locator('.gh-signed-out').innerText();
    notes.setup_heading = await page.locator('.gh-setup-card:not(.gh-signed-out) h2').innerText();
  } else {
    await page.locator('.gh-signed-out').waitFor();
    await page.waitForTimeout(3000);
    assert(await page.locator('button.account-logout-open').count() === 0, 'restart stays signed out');
    await shot('04-after-restart', {fullPage: true});
    notes.restart_text = await page.locator('.gh-signed-out').innerText();
    if (process.env.MQ_LOGOUT_RECONNECT) {
      await page.click('.gh-setup-footer button.primary');
      await page.locator('button.account-logout-open').waitFor();
      assert(!fs.existsSync(path.join(dataDir, 'github-signed-out')), 'reconnect clears the marker');
      await shot('05-reconnected');
      notes.reconnect = 'catalog back, marker removed';
    }
  }
  return notes;
};
