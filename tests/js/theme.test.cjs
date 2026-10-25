// Theme choice (시스템 / 밝게 / 어둡게) against an emulated OS scheme, in both engines the app ships on.
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const {chromium, webkit} = require('../../target/ui-tests/node_modules/playwright-core');
const styles = ['app', 'repository-player', 'content-updates', 'player-workspace', 'window-controls', 'compact-toolbar', 'product-ui', 'station']
  .map(name => fs.readFileSync(`assets/${name}.css`, 'utf8')).join('\n');
const script = fs.readFileSync('assets/layout/theme.js', 'utf8');
const page = (choice) => `<!doctype html><html${choice === undefined ? '' : ` data-theme-choice="${choice}"`}><head><style>${styles}</style></head><body>
<div class="repository-player" style="--line:#009b4c;--line-ink:#00703a;--line-soft:#e3f4ea;--line-bright:#3ccf7e"><main class="course-main"><section class="course-catalog">
<section class="next-station" data-state="next"><div class="next-station-text"><h3>수업 1</h3><p class="next-station-detail"><strong class="next-station-label">다음 수업</strong> · 필수 문제 23개</p></div></section>
<ol class="repository-lessons"><li class="card lesson-card" data-state="todo" data-next="false" data-required="true"><span class="lesson-number">1</span><div class="lesson-card-heading"><h3>Bash</h3><div class="lesson-meta"><span class="lesson-track basic">기본</span><span class="lesson-revision">버전 bash-basics-4</span></div></div></li></ol>
</section></main></div></body></html>`;

const luminance = c => { const a = c.match(/[\d.]+/g).slice(0, 3).map(Number).map(x => x / 255).map(x => x <= .04045 ? x / 12.92 : ((x + .055) / 1.055) ** 2.4); return a[0] * .2126 + a[1] * .7152 + a[2] * .0722; };
const ratio = (a, b) => { const [x, y] = [luminance(a), luminance(b)].sort((p, q) => p - q); return (y + .05) / (x + .05); };

for (const [name, engine] of Object.entries({chromium, webkit})) test(`${name}: stored choice and OS scheme give one effective theme`, async () => {
  const browser = await engine.launch(name === 'chromium' && process.platform === 'win32' ? {channel: 'msedge', headless: true} : {headless: true, ...(name === 'webkit' && process.env.MQ3_WEBKIT_EXECUTABLE ? {executablePath: process.env.MQ3_WEBKIT_EXECUTABLE} : {})});
  try {
    let tab = await browser.newPage();
    const look = () => tab.evaluate(() => ({
      effective: document.documentElement.dataset.theme,
      wall: getComputedStyle(document.documentElement).getPropertyValue('--wall').trim(),
      ink: getComputedStyle(document.querySelector('.lesson-card h3')).color,
      panel: getComputedStyle(document.querySelector('.next-station')).backgroundColor,
      label: getComputedStyle(document.querySelector('.next-station-label')).color,
      meta: getComputedStyle(document.querySelector('.lesson-revision')).color,
      wallColor: getComputedStyle(document.body).backgroundColor,
    }));
    for (const os of ['light', 'dark']) for (const choice of ['system', 'light', 'dark', undefined, 'sepia']) {
      tab = await browser.newPage();
      await tab.emulateMedia({colorScheme: os});
      await tab.setContent(page(choice));
      await tab.addScriptTag({content: script});
      const expected = (choice === 'light' || choice === 'dark') ? choice : os;
      const seen = await look();
      assert.equal(seen.effective, expected, `${os}/${choice}`);
      assert.equal(seen.wall, expected === 'dark' ? '#161f2e' : '#eef1f5', `${os}/${choice}: tokens follow the effective theme before any script`);
      for (const [fg, bg, label] of [[seen.ink, seen.panel, 'title'], [seen.label, seen.panel, 'line label'], [seen.meta, seen.wallColor, 'meta']])
        assert.ok(ratio(fg, bg) >= 4.5, `${os}/${choice}: ${label} contrast ${ratio(fg, bg).toFixed(2)}`);
    }
    // 시스템 follows a runtime OS change; explicit choices do not.
    tab = await browser.newPage();
    await tab.emulateMedia({colorScheme: 'light'});
    await tab.setContent(page('system'));
    await tab.addScriptTag({content: script});
    const events = await tab.evaluate(() => { window.__themeEvents = []; document.addEventListener('mq-theme', e => window.__themeEvents.push(e.detail.effective)); return true; });
    assert.ok(events);
    await tab.emulateMedia({colorScheme: 'dark'});
    await tab.waitForFunction(() => document.documentElement.dataset.theme === 'dark');
    assert.deepEqual(await tab.evaluate(() => window.__themeEvents), ['dark']);
    assert.equal(await tab.evaluate(() => mqTheme.set('light')), 'light');
    await tab.emulateMedia({colorScheme: 'light'}); await tab.emulateMedia({colorScheme: 'dark'});
    assert.equal(await tab.evaluate(() => document.documentElement.dataset.theme), 'light', 'explicit 밝게 stays light');
    assert.equal(await tab.evaluate(() => mqTheme.set('nonsense')), 'dark', 'an unknown choice is 시스템');
    assert.equal(await tab.evaluate(() => document.documentElement.dataset.themeChoice), 'system');
  } finally { await browser.close(); }
});
