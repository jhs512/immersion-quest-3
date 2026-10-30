// Whole-app light theme audit on the real course (validation mode, private data folder).
// Picks 밝게, walks the learner and teacher screens (catalog, challenges, lesson, editor, run and
// submit results, dialogs, menus, narration, auto run, terminal, Git graph, Vim, Java build, web
// preview) and on each one scans every visible element: a dark background or light text on light
// ground is a finding unless it is a deliberate role of the station world (the navy signage band and
// its menus' triggers, filled line-colour actions, status chips, toasts). Then it repeats the
// key screens in 어둡게 to show dark still works, and returns to 밝게 for the restart check.
// Any finding fails the run (exit 1) after every screen was captured.
const fs = require('node:fs');
const path = require('node:path');

module.exports = async ({page, shot, dataDir, output}) => {
  const notes = [];
  const findings = [];
  const step = async (label, run) => {
    try { await run(); notes.push(`ok: ${label}`); }
    catch (error) { notes.push(`FAIL: ${label}: ${String(error.message || error).split('\n')[0]}`); }
  };
  const button = (name) => page.getByRole('button', {name, exact: true});
  const desktop = async () => page.setViewportSize({width: 1440, height: 900});
  const toolbox = async (open) => page.evaluate((open) => { const t = document.querySelector('.pilot-toolbox'); if (t) t.open = open; }, open);
  const settings = async (open) => {
    const isOpen = await page.evaluate(() => !!document.querySelector('.app-update-settings')?.open);
    if (isOpen !== open) await page.locator('.app-update-settings > summary').click();
  };
  const choose = async (key) => {
    await settings(true);
    await page.locator(`input[name="mq-theme-choice"][value="${key}"]`).check({force: true});
    await page.waitForFunction((key) => document.documentElement.dataset.themeChoice === key && document.documentElement.dataset.theme === key, key, {timeout: 5000});
    await settings(false);
  };
  const toCatalog = async () => {
    for (const name of ['← 코스 수업 목록', '← 도전 과제']) if (await button(name).count()) { await button(name).click(); break; }
    await page.waitForSelector('.course-catalog');
  };
  const openLesson = async (index) => {
    await toCatalog();
    if (await button('수업 목록').count()) await button('수업 목록').click();
    const card = page.locator('.lesson-card').nth(index);
    await card.scrollIntoViewIfNeeded();
    await card.locator('button', {hasText: '학습 시작'}).click();
    await page.waitForSelector('.study-navigation', {timeout: 60000});
  };
  const openTask = async (number) => {
    await page.locator('.study-navigation button', {hasText: `문제 ${number} ·`}).first().click();
    await page.waitForSelector('.repository-task');
  };

  // The scan runs in the page. Luminance is WCAG relative luminance of the composited colour.
  const scan = (label) => page.evaluate((label) => {
    const parse = (value) => {
      const m = value && value.match(/rgba?\(([^)]+)\)/);
      if (!m) return null;
      const parts = m[1].split(/[ ,/]+/).filter(Boolean).map(Number);
      return {r: parts[0], g: parts[1], b: parts[2], a: parts.length > 3 ? parts[3] : 1};
    };
    const lum = ({r, g, b}) => {
      const f = (c) => { c /= 255; return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4; };
      return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
    };
    const contrast = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return (x + 0.05) / (y + 0.05); };
    // Composite the background chain up to the page so translucent fills are judged as seen.
    const backdrop = (element) => {
      const chain = [];
      for (let node = element; node && node.nodeType === 1; node = node.parentElement) {
        const c = parse(getComputedStyle(node).backgroundColor);
        if (c && c.a > 0) { chain.push(c); if (c.a >= 0.99) break; }
      }
      let out = parse(getComputedStyle(document.documentElement).backgroundColor) || {r: 255, g: 255, b: 255, a: 1};
      if (out.a < 1) out = {r: 255, g: 255, b: 255, a: 1};
      for (const c of chain.reverse()) out = {r: c.r * c.a + out.r * (1 - c.a), g: c.g * c.a + out.g * (1 - c.a), b: c.b * c.a + out.b * (1 - c.a), a: 1};
      return out;
    };
    // Deliberate dark roles of the station world in 밝게 (DESIGN.md): the navy signage band and what
    // sits on it, filled line-colour/primary actions, the selected segment, status chips and toasts,
    // the narrator's caption, danger confirmations, modal scrims.
    const allowed = (element) => element.closest([
      '.repository-header', '.molip-toast', '.update-banner', '.agent-caption', '.repository-status',
      'button.primary', '.lesson-next-label', '.next-station-start', '.theme-option.selected', '.catalog-toolbar button.selected',
      '.narration-play', '.lesson-card[data-state="done"]>.lesson-number', '.lesson-card[data-state="challenge"]>.lesson-number',
      '.study-navigation .step-dot', '.lesson-reset-confirm', '.account-reset-confirm', '.auto-run-chip', '.auto-run-icon',
      '.content-update-menu>button:first-child', '.course-identity button[type=submit]', '.task-passed-backdrop', '.submission-progress-backdrop',
      '.cm-narration-span', '.git-graph-panel.is-expanded', '.pilot-toolbox',
    ].join(','));
    const visible = (element) => {
      const rect = element.getBoundingClientRect();
      if (rect.width < 4 || rect.height < 4 || rect.bottom < 0 || rect.right < 0 || rect.top > innerHeight || rect.left > innerWidth) return false;
      for (let node = element; node && node.nodeType === 1; node = node.parentElement) {
        const style = getComputedStyle(node);
        if (style.display === 'none' || style.visibility === 'hidden' || Number(style.opacity) === 0) return false;
      }
      return true;
    };
    const name = (element) => {
      const cls = typeof element.className === 'string' ? element.className.trim().split(/\s+/).slice(0, 3).join('.') : '';
      const parent = element.parentElement;
      const pcls = parent && typeof parent.className === 'string' ? parent.className.trim().split(/\s+/).slice(0, 2).join('.') : '';
      return `${parent ? parent.tagName.toLowerCase() + (pcls ? '.' + pcls : '') + ' > ' : ''}${element.tagName.toLowerCase()}${element.id ? '#' + element.id : ''}${cls ? '.' + cls : ''}`;
    };
    const out = [];
    const seen = new Set();
    for (const element of document.body.querySelectorAll('*')) {
      if (['SCRIPT', 'STYLE', 'svg', 'path', 'BR', 'OPTION'].includes(element.tagName) || element.closest('svg')) continue;
      if (!visible(element) || allowed(element)) continue;
      const style = getComputedStyle(element);
      const own = parse(style.backgroundColor);
      if (own && own.a >= 0.5) {
        const bg = backdrop(element);
        if (lum(bg) < 0.2) {
          const key = 'bg ' + name(element);
          if (!seen.has(key)) { seen.add(key); out.push(`${label}: dark background ${style.backgroundColor} on ${name(element)}`); }
        }
      }
      // Text drawn by this element itself (a direct non-empty text node).
      const hasText = [...element.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
      if (hasText) {
        const fg = parse(style.color);
        const bg = backdrop(element);
        if (fg && fg.a > 0.3 && lum(bg) > 0.5 && contrast(fg, bg) < 3) {
          const key = 'fg ' + name(element);
          if (!seen.has(key)) { seen.add(key); out.push(`${label}: low-contrast text ${style.color} on ${name(element)} (${contrast(fg, bg).toFixed(2)}:1) "${element.textContent.trim().slice(0, 30)}"`); }
        }
      }
    }
    const root = getComputedStyle(document.documentElement);
    return {findings: out, theme: document.documentElement.dataset.theme, editor: [...document.querySelectorAll('.cm-editor')].map(e => getComputedStyle(e).backgroundColor),
      terminal: [...document.querySelectorAll('.xterm-viewport,.xterm-screen')].map(e => getComputedStyle(e).backgroundColor), scheme: root.colorScheme};
  }, label);
  const look = async (label, options) => {
    await page.waitForTimeout(300);
    const result = await scan(label);
    findings.push(...result.findings);
    notes.push(`${label}: theme=${result.theme} findings=${result.findings.length} editor=${JSON.stringify(result.editor)} terminal=${JSON.stringify(result.terminal)}`);
    await shot(label, options);
  };

  await desktop();
  await page.emulateMedia({colorScheme: 'dark'});
  await page.waitForSelector('.pilot-toolbox', {timeout: 60000});
  fs.writeFileSync(path.join(dataDir, 'pilot-course-reviewer'), '');
  await toolbox(true);
  await button('버전 본').click();
  await toolbox(false);
  await page.waitForFunction(() => document.querySelectorAll('.lesson-card').length > 30, null, {timeout: 60000});
  // The OS is dark here on purpose: an explicit 밝게 must win everywhere.
  await choose('light');
  await step('catalog name form', () => look('L01-catalog-name'));
  await step('save course name', async () => {
    await page.locator('#course-display-name').fill('라이트검증');
    await page.locator('.course-identity button[type=submit]').click();
    await page.waitForFunction(() => [...document.querySelectorAll('.lesson-card button')].some(b => b.textContent.includes('학습 시작') && !b.disabled), null, {timeout: 30000});
    await look('L02-catalog');
  });
  await step('app settings', async () => { await settings(true); await look('L03-app-settings'); await settings(false); });
  await step('challenges', async () => { await button('도전 과제').click(); await page.waitForTimeout(1500); await look('L04-challenges'); await button('수업 목록').click(); });
  await step('course guide', async () => {
    const guide = page.locator('.course-guide-open');
    if (!await guide.count()) throw Error('no course guide');
    await guide.first().click(); await page.waitForTimeout(800); await look('L05-course-guide'); await page.keyboard.press('Escape');
  });
  await step('code problem', async () => {
    await openLesson(1); await look('L10-lesson-open');
    await openTask(1);
    await page.waitForSelector('.cm-editor', {timeout: 30000});
    await look('L11-editor');
  });
  await step('run result', async () => {
    await page.locator('.repository-task [data-shortcut-action="run"]').click();
    await page.waitForFunction(() => ['finished', 'failed'].includes(document.querySelector('.result-pane')?.dataset.executionState), null, {timeout: 90000});
    await look('L12-run-result');
  });
  await step('submit feedback', async () => {
    await page.locator('.repository-task [data-shortcut-action="submit"]').click();
    await page.waitForFunction(() => ['passed', 'incorrect', 'error'].includes(document.querySelector('.result-pane')?.dataset.feedback), null, {timeout: 90000});
    await look('L13-submit-feedback');
    if (await button('여기 머물기').count()) { await look('L13b-dialog'); await button('여기 머물기').click(); }
  });
  await step('lesson info', async () => {
    await page.locator('.lesson-info-trigger').click();
    await page.waitForFunction(() => document.getElementById('lesson-info-dialog')?.open);
    await look('L14-lesson-info'); await page.keyboard.press('Escape');
  });
  await step('lesson settings', async () => {
    await page.locator('.content-update-controls > details > summary').click();
    await look('L15-lesson-settings');
    await page.locator('.content-update-controls > details > summary').click();
  });
  await step('shortcut sheet', async () => {
    await page.locator('.repository-study .shortcut-sheet-open').click();
    await look('L16-shortcuts'); await page.keyboard.press('Escape');
  });
  await step('narration', async () => {
    const play = page.locator('.repository-task .narration-play');
    if (!await play.count()) throw Error('no narration on this step');
    await play.click();
    await page.waitForFunction(() => document.querySelector('.repository-task')?.dataset.narrating === 'true', null, {timeout: 30000});
    await page.waitForTimeout(2500);
    await look('L17-narration');
    await page.locator('.repository-task .narration-stop').click();
    await page.waitForFunction(() => document.querySelector('.repository-task')?.dataset.narrating === 'false', null, {timeout: 30000});
  });
  await step('auto run', async () => {
    await page.waitForSelector('#auto-run-start:not([disabled])', {timeout: 30000});
    await page.locator('#auto-run-start').click();
    await page.waitForSelector('.auto-run-control[data-state="running"]', {timeout: 30000});
    await page.waitForTimeout(1500);
    await look('L18-auto-running');
    await page.keyboard.press('Escape');
    await page.waitForSelector('.auto-run-control:not([data-state="running"])', {timeout: 30000});
    await page.locator('.auto-run-details > summary').click();
    await look('L19-auto-stopped');
    await page.locator('.auto-run-dismiss').click();
  });
  await step('terminal lesson', async () => {
    await openLesson(0); await openTask(1);
    await page.waitForFunction(() => document.querySelector('.repository-task')?.dataset.gitReady === 'true', null, {timeout: 90000});
    await page.waitForTimeout(1200);
    await page.locator('.xterm-helper-textarea').first().focus();
    await page.keyboard.type('ls --color=always -la; printf "\\033[31mred \\033[32mgreen \\033[33myellow \\033[34mblue \\033[35mmagenta \\033[36mcyan \\033[37mwhite \\033[97mbright\\033[0m\\n"\r');
    await page.waitForTimeout(1500);
    await look('L20-terminal');
  });
  for (const [index, task, name] of [[2, 2, 'L21-git-graph'], [4, 1, 'L22-vim'], [5, 1, 'L23-java-build'], [24, 1, 'L24-web-preview'], [26, 1, 'L25-single-code']]) {
    await step(`lesson ${index} workspace`, async () => {
      await openLesson(index); await openTask(task);
      await page.waitForFunction(() => { const t = document.querySelector('.repository-task'); return t && (!t.querySelector('.git-terminal,#git-student-terminal') || t.dataset.gitReady === 'true'); }, null, {timeout: 120000});
      await page.waitForTimeout(1500);
      await look(name);
    });
  }
  await step('catalog after study', async () => { await toCatalog(); await page.waitForTimeout(800); await look('L30-catalog-after-study'); });

  // 어둡게 keeps working: the same key screens, captured for the pair (findings not applied).
  await step('dark pair', async () => {
    await choose('dark');
    await shot('D02-catalog');
    await openLesson(1); await openTask(1); await page.waitForSelector('.cm-editor', {timeout: 30000});
    const dark = await scan('dark-editor');
    notes.push(`dark editor=${JSON.stringify(dark.editor)} theme=${dark.theme}`);
    if (!dark.editor.length || dark.editor.some(c => !/rgb\(32, 45, 62\)/.test(c))) throw Error('editor is not the night well in 어둡게: ' + JSON.stringify(dark.editor));
    await shot('D11-editor');
    await openLesson(0); await openTask(1);
    await page.waitForFunction(() => document.querySelector('.repository-task')?.dataset.gitReady === 'true', null, {timeout: 90000});
    await page.waitForTimeout(1200);
    const term = await scan('dark-terminal');
    notes.push(`dark terminal=${JSON.stringify(term.terminal)}`);
    await shot('D20-terminal');
    // Live switch while the terminal is open: it repaints without a remount.
    await choose('light');
    await page.waitForTimeout(400);
    const live = await scan('live-switch-terminal');
    notes.push(`live switch terminal=${JSON.stringify(live.terminal)}`);
    findings.push(...live.findings);
    await shot('L26-terminal-after-live-switch');
  });
  fs.writeFileSync(path.join(output, 'findings.txt'), findings.join('\n') + '\n');
  notes.push(`TOTAL light findings: ${findings.length}`);
  return notes;
};
