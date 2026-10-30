// 라이트 모드 전체 버튼·팝업 인벤토리 검사 (2026-10-30 사용자 요청: "라이트 모드 전체 버튼이랑 팝업 다 점검").
// 실제 앱(검증 모드, 격리된 데이터)에서 각 화면과 떠 있는 UI를 실제로 열고, 밝게·어둡게 × 넓은 창·820px 창에서
// 보이는 모든 버튼(기본·hover·포커스·비활성·선택·위험·아이콘 전용)과 팝업 텍스트를 검사한다.
//   - 활성 버튼 글자 대비 >= 4.5:1, 아이콘 전용 버튼의 아이콘(currentColor) >= 3:1, 비활성은 기록만(1.8 미만이면 실패)
//   - 팝업·메뉴 안 텍스트가 팝업 밖으로 넘치거나 잘리면 실패, `{a.b}` 형태의 보간 누락이 보이면 실패
//   - 팝업마다 Tab으로 이동한 포커스의 윤곽선이 보이는지(스타일 none 아님, 대비 >= 3:1)
//   - hover 상태의 대비
// 초기화 확인 같은 위험 단계는 시드한 격리 진도에서 열기만 하고 확인을 누르지 않는다.
//   MQ3_CAPTURE_DATA_DIR=<seed-lesson-clear.py 폴더> node tools/design-capture.cjs tools/design-scenarios/ui-inventory.cjs <out>
// MOLIP_GH_SETUP_PREVIEW로 띄우면 GitHub 준비 화면만 검사하고 끝낸다.
const fs = require('node:fs');
const path = require('node:path');

module.exports = async ({page, shot, dataDir, output}) => {
  const notes = [];
  const fails = [];
  const step = async (label, run) => {
    try { await run(); notes.push(`ok: ${label}`); }
    catch (error) { notes.push(`STEP FAIL: ${label}: ${String(error.message || error).split('\n')[0]}`); fails.push(`step ${label}`); }
    // 실패해도 다음 단계가 깨끗한 화면에서 시작하게: 열린 메뉴·팝업을 닫는다.
    await page.keyboard.press('Escape').catch(() => {});
    await page.evaluate(() => {
      for (const d of document.querySelectorAll('details[open]')) if (!d.matches('.git-graph-panel, .pilot-toolbox, .course-identity-details')) d.open = false;
      for (const d of document.querySelectorAll('dialog[open]')) d.close();
    }).catch(() => {});
  };
  const button = (name) => page.getByRole('button', {name, exact: true});

  // 화면 하나를 검사한다: scope 안(기본 문서 전체)의 보이는 버튼과, popup 선택자들의 넘침·보간.
  const audit = (label, popups = []) => page.evaluate(({label, popups}) => {
    const out = [], info = [], local = new Set();
    const parse = (v) => { const m = v && v.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(/[ ,/]+/).filter(Boolean).map(Number); return {r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1}; };
    const lum = ({r, g, b}) => { const f = (c) => { c /= 255; return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4; }; return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b); };
    const ratio = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return (x + 0.05) / (y + 0.05); };
    const backdrop = (el) => {
      const chain = [];
      for (let n = el; n && n.nodeType === 1; n = n.parentElement) { const c = parse(getComputedStyle(n).backgroundColor); if (c && c.a > 0) { chain.push(c); if (c.a >= 0.99) break; } }
      let o = {r: 255, g: 255, b: 255, a: 1};
      const root = parse(getComputedStyle(document.body).backgroundColor); if (root && root.a > 0.99) o = root;
      for (const c of chain.reverse()) o = {r: c.r * c.a + o.r * (1 - c.a), g: c.g * c.a + o.g * (1 - c.a), b: c.b * c.a + o.b * (1 - c.a), a: 1};
      return o;
    };
    const visible = (el) => { const r = el.getBoundingClientRect(); if (r.width < 3 || r.height < 3 || r.bottom < 0 || r.top > innerHeight || r.right < 0 || r.left > innerWidth) return false;
      for (let n = el; n && n.nodeType === 1; n = n.parentElement) { const s = getComputedStyle(n); if (s.display === 'none' || s.visibility === 'hidden' || Number(s.opacity) < 0.05) return false; } return true; };
    const name = (el) => (el.getAttribute('aria-label') || el.textContent || el.title || '').trim().replace(/\s+/g, ' ').slice(0, 28);
    // 모달이 열려 있으면 그 밖은 비활성(inert)이므로 모달 안만 검사한다.
    const modal = [...document.querySelectorAll('dialog[open]')].find((d) => d.matches(':modal'));
    const scope = modal || document;
    for (const el of scope.querySelectorAll('button, summary, [role=button], a.button, select, .theme-option, input[type=submit]')) {
      if (!visible(el) || el.closest('.pilot-toolbox,.pilot-toolbar')) continue;
      // 반투명 가림막(제출 진행·통과 대화상자) 아래 컨트롤은 사용자가 조작할 수 없으므로 건너뛴다.
      const r0 = el.getBoundingClientRect(); const top = document.elementFromPoint(r0.left + r0.width / 2, r0.top + r0.height / 2);
      if (top && top !== el && !el.contains(top) && top.closest('.submission-progress-backdrop,.task-passed-backdrop')) continue;
      const s = getComputedStyle(el);
      const fg = parse(s.color), bg = backdrop(el);
      const disabled = el.disabled || el.getAttribute('aria-disabled') === 'true';
      const text = (el.innerText || '').trim();
      const r = ratio(fg, bg);
      const key = `${name(el)}|${el.className}`;
      if (local.has(key)) continue; local.add(key);
      const kind = disabled ? 'disabled' : (text ? 'text' : 'icon');
      const min = kind === 'text' ? 4.5 : kind === 'icon' ? 3 : 1.8;
      info.push(`${kind} ${r.toFixed(2)} ${name(el)}`);
      if (r < min) out.push(`${label}: ${kind} button "${name(el)}" ${r.toFixed(2)}:1 (${s.color} on rgb(${Math.round(bg.r)},${Math.round(bg.g)},${Math.round(bg.b)})) .${String(el.className).split(' ').slice(0, 2).join('.')}`);
    }
    for (const sel of popups) {
      for (const box of document.querySelectorAll(sel)) {
        if (!visible(box)) continue;
        const rb = box.getBoundingClientRect();
        const text = box.innerText || '';
        const literal = text.match(/@?\{[a-z_]+(\.[a-z_]+)+\}/i);
        if (literal) out.push(`${label}: ${sel} 보간 누락 "${literal[0]}"`);
        for (const el of box.querySelectorAll('p, li, h2, h3, strong, span, label, button, summary, pre, code, td')) {
          if (!visible(el) || el.closest('pre, .cm-editor, .xterm, .code-flow-view')) continue;
          const r = el.getBoundingClientRect();
          const s = getComputedStyle(el);
          const clipped = el.scrollWidth > el.clientWidth + 1 && ['hidden', 'clip'].includes(s.overflowX) && s.textOverflow !== 'ellipsis';
          if (r.right > rb.right + 1 || r.left < rb.left - 1 || clipped) { out.push(`${label}: ${sel} 넘침 "${(el.innerText || '').trim().slice(0, 30)}" (${Math.round(r.left)}..${Math.round(r.right)} vs ${Math.round(rb.left)}..${Math.round(rb.right)})`); break; }
        }
        // 팝업의 본문 글자 대비
        for (const el of box.querySelectorAll('h2, h3, p, li, label')) {
          if (!visible(el) || !el.innerText.trim()) continue;
          const r = ratio(parse(getComputedStyle(el).color), backdrop(el));
          if (r < 4.5) { out.push(`${label}: ${sel} 글자 대비 ${r.toFixed(2)} "${el.innerText.trim().slice(0, 24)}"`); break; }
        }
      }
    }
    return {out, info, theme: document.documentElement.dataset.theme};
  }, {label, popups});

  const focusCheck = async (label, container) => {
    // 열렸을 때 처음 포커스가 팝업 안이어야 한다. Tab 이동은 팝업 안 조작 요소가 둘 이상일 때만 검사한다
    // (하나뿐이면 브라우저가 포커스를 창 밖으로 보내는 것이 표준 동작).
    if (container) {
      const start = await page.evaluate((c) => ({inside: !!document.activeElement?.closest(c), count: document.querySelector(c)?.querySelectorAll('button:not(:disabled), a[href], input, select, textarea, summary, [tabindex]:not([tabindex="-1"])').length || 0}), container);
      notes.push(`${label}: 처음 포커스 안=${start.inside} 조작 요소 ${start.count}`);
      if (!start.inside) { fails.push(`${label}: 처음 포커스가 팝업 밖`); notes.push(`FAIL ${label}: 처음 포커스가 팝업 밖`); }
      if (start.count < 2) return;
    }
    await page.keyboard.press('Tab');
    const f = await page.evaluate((container) => {
      const el = document.activeElement; if (!el || el === document.body) return null;
      const s = getComputedStyle(el);
      return {inside: container ? !!el.closest(container) : true, style: s.outlineStyle, width: s.outlineWidth, color: s.outlineColor, shadow: s.boxShadow, tag: el.tagName, text: (el.innerText || el.getAttribute('aria-label') || '').trim().slice(0, 20)};
    }, container);
    // 마지막 조작 요소에서 Tab을 누르면 브라우저가 포커스를 창 밖으로 보낸다(모달 dialog의 표준 동작): 기록만 한다.
    if (!f) { notes.push(`${label}: Tab 뒤 포커스가 문서 밖(마지막 조작 요소에서 이동, 표준 동작)`); return; }
    const visibleRing = (f.style !== 'none' && parseFloat(f.width) >= 1) || (f.shadow && f.shadow !== 'none');
    notes.push(`${label}: focus ${f.tag} "${f.text}" outline ${f.style} ${f.width} ${f.color}${container ? ' inside=' + f.inside : ''}`);
    if (!visibleRing) { fails.push(`${label}: 포커스 윤곽선 없음`); notes.push(`FAIL ${label}: 포커스 윤곽선 없음`); }
    if (container && !f.inside) notes.push(`${label}: Tab 뒤 포커스가 팝업 밖(마지막 조작 요소에서 이동)`);
  };

  const look = async (label, popups = [], options = {}) => {
    await page.waitForTimeout(options.settle ?? 350);
    const r = await audit(label, popups);
    for (const o of r.out) { fails.push(o); notes.push('FAIL ' + o); }
    notes.push(`${label}: theme=${r.theme} buttons=${r.info.length} problems=${r.out.length}`);
    fs.appendFileSync(path.join(output, 'buttons.txt'), `## ${label}\n${r.info.join('\n')}\n`);
    await shot(label);
  };
  const setTheme = async (theme) => { await page.evaluate((t) => window.mqTheme.set(t), theme); await page.waitForTimeout(250); };
  const sizes = [['1440', 1440], ['820', 820]];

  await page.setViewportSize({width: 1440, height: 900});
  // GitHub 준비 화면(실제 화면, MOLIP_GH_SETUP_PREVIEW)
  if (await page.locator('.repository-player.needs-gh').count().then((n) => n > 0, () => false) || process.env.MOLIP_GH_SETUP_PREVIEW) {
    await page.waitForSelector('.repository-player.needs-gh', {timeout: 30000});
    for (const theme of ['light', 'dark']) for (const [tag, w] of sizes) {
      await page.setViewportSize({width: w, height: 900}); await setTheme(theme);
      await step(`gh ${theme}-${tag}`, async () => {
        const top = await page.evaluate(() => document.querySelector('.repository-player.needs-gh>.repository-header').getBoundingClientRect().top);
        if (top > 2) { fails.push(`gh ${theme}-${tag}: 헤더가 맨 위가 아님 ${top}`); notes.push(`FAIL gh ${theme}-${tag}: header top ${top}`); }
        await look(`G-${theme}-${tag}`, ['.gh-setup-card', '.gh-checking']);
      });
    }
    notes.push(`TOTAL FAIL ${fails.length}`);
    fs.writeFileSync(path.join(output, 'fails.txt'), fails.join('\n') + '\n');
    return notes;
  }

  await page.waitForSelector('.pilot-toolbox', {timeout: 60000});
  fs.writeFileSync(path.join(dataDir, 'pilot-course-reviewer'), '');
  await page.evaluate(() => { document.querySelector('.pilot-toolbox').open = true; });
  await button('버전 본').click();
  await page.evaluate(() => { document.querySelector('.pilot-toolbox').open = false; });
  await page.waitForFunction(() => document.querySelectorAll('.lesson-card').length > 30, null, {timeout: 60000});
  // 이름 저장 전 화면(비활성 수업 버튼)을 한 번 검사하고, 이름을 저장해 수업 버튼을 연다.
  await step('catalog before name', async () => { await look('C00-catalog-name-required-light-1440'); });
  await page.locator('#course-display-name').fill('인벤토리검증');
  await page.locator('.course-identity button[type=submit]').click();
  await page.waitForFunction(() => [...document.querySelectorAll('.lesson-card button')].some(b => /학습 시작|이어서|복습|다시/.test(b.textContent) && !b.disabled), null, {timeout: 30000});
  const toCatalog = async () => {
    for (const n of ['← 코스 수업 목록', '← 도전 과제']) if (await button(n).count()) { await button(n).click(); break; }
    await page.waitForSelector('.course-catalog');
  };
  const closeDetails = (sel) => page.evaluate((sel) => { for (const d of document.querySelectorAll(sel)) d.open = false; }, sel);

  for (const theme of ['light', 'dark']) {
    for (const [tag, w] of sizes) {
      const T = `${theme}-${tag}`;
      await page.setViewportSize({width: w, height: 900}); await setTheme(theme);
      await step(`catalog ${T}`, async () => { await toCatalog(); await page.evaluate(() => scrollTo(0, 0)); await look(`C01-catalog-${T}`); });
      await step(`catalog hover ${T}`, async () => {
        for (const sel of ['.next-station-start', '.course-guide-open', '.lesson-card .lesson-actions button.primary', '.repository-header .shortcut-sheet-open']) {
          const el = page.locator(sel).first(); if (!await el.count()) continue;
          await el.hover(); await page.waitForTimeout(220);
          const r = await audit(`hover ${sel} ${T}`, []); for (const o of r.out.filter((o) => o.includes(sel.split(' ').pop().replace(/^\./, '').split('.')[0]) || true)) { if (o.startsWith(`hover ${sel}`)) { fails.push(o); notes.push('FAIL ' + o); } }
        }
        await page.mouse.move(5, 300);
      });
      await step(`lesson settings menu ${T}`, async () => {
        await page.locator('.content-update-controls > details > summary').first().click();
        await page.evaluate(() => { for (const d of document.querySelectorAll('.content-update-menu details')) d.open = true; });
        await look(`C02-lesson-settings-${T}`, ['.content-update-menu']);
        await closeDetails('.content-update-controls > details');
      });
      await step(`app settings menu ${T}`, async () => {
        await page.locator('.app-update-settings > summary').first().click();
        await look(`C03-app-settings-${T}`, ['.app-update-menu']);
        await focusCheck(`C03-focus-${T}`, null);
      });
      await step(`doctor popup ${T}`, async () => {
        if (!await page.evaluate(() => !!document.querySelector('.app-update-settings')?.open)) await page.locator('.app-update-settings > summary').first().click();
        const open = page.locator('.app-update-menu button', {hasText: '환경 진단'}).first();
        if (!await open.count()) throw Error('환경 진단 버튼 없음');
        await open.click();
        await page.waitForSelector('.doctor-backdrop .doctor-panel', {timeout: 10000});
        await page.waitForTimeout(1500);
        await look(`C04-doctor-${T}`, ['.doctor-panel']);
        const close = page.locator('.doctor-panel button', {hasText: /닫기/}).first();
        if (await close.count()) await close.click(); else await page.keyboard.press('Escape');
        await closeDetails('.app-update-settings');
      });
      await step(`account reset ${T}`, async () => {
        await page.locator('.account-reset-open').click();
        await page.waitForFunction(() => document.getElementById('account-reset-dialog')?.open, null, {timeout: 10000});
        await page.waitForFunction(() => !/확인하고 있어요/.test(document.getElementById('account-reset-dialog')?.textContent || ''), null, {timeout: 30000}).catch(() => {});
        await look(`C05-account-reset-${T}`, ['#account-reset-dialog']);
        await focusCheck(`C05-focus-${T}`, '#account-reset-dialog');
        await page.keyboard.press('Escape');
        await page.waitForFunction(() => !document.getElementById('account-reset-dialog')?.open, null, {timeout: 5000}).catch(() => {});
      });
      await step(`course guide ${T}`, async () => {
        await page.locator('.course-guide-open').first().click();
        await page.waitForFunction(() => document.getElementById('course-guide-dialog')?.open, null, {timeout: 10000});
        await look(`C06-course-guide-${T}`, ['#course-guide-dialog']);
        await focusCheck(`C06-focus-${T}`, '#course-guide-dialog');
        await page.keyboard.press('Escape');
      });
      await step(`challenges ${T}`, async () => { await button('도전 과제').click(); await page.waitForTimeout(1000); await look(`C07-challenges-${T}`); await button('수업 목록').click(); });
      await step(`shortcut sheet ${T}`, async () => {
        await page.locator('.repository-header .shortcut-sheet-open').first().click();
        await page.waitForSelector('.shortcut-sheet[open]', {timeout: 5000});
        await look(`C08-shortcuts-${T}`, ['.shortcut-sheet']);
        await focusCheck(`C08-focus-${T}`, '.shortcut-sheet');
        await page.keyboard.press('Escape');
      });
    }
  }

  // 수업 화면 (넓은 창·820px, 밝게·어둡게)
  const openLesson = async (index) => {
    await toCatalog(); if (await button('수업 목록').count()) await button('수업 목록').click();
    const card = page.locator('.lesson-card').nth(index); await card.scrollIntoViewIfNeeded();
    await card.locator('button', {hasText: /학습 시작|이어서|다시 보기|복습/}).first().click();
    await page.waitForSelector('.study-navigation', {timeout: 60000});
  };
  const openTask = async (n) => { await page.locator('.study-navigation button', {hasText: `문제 ${n} ·`}).first().click(); await page.waitForSelector('.repository-task'); };
  for (const theme of ['light', 'dark']) {
    for (const [tag, w] of sizes) {
      const T = `${theme}-${tag}`;
      await page.setViewportSize({width: w, height: 900}); await setTheme(theme);
      await step(`lesson problem ${T}`, async () => { await openLesson(4); await openTask(1); await page.waitForSelector('.cm-editor', {timeout: 30000}); await look(`L01-problem-${T}`); });
      await step(`run and submit ${T}`, async () => {
        await page.locator('.repository-task [data-shortcut-action="run"]').click();
        await page.waitForFunction(() => ['finished', 'failed'].includes(document.querySelector('.result-pane')?.dataset.executionState), null, {timeout: 90000});
        await page.locator('.repository-task [data-shortcut-action="submit"]').click();
        await page.waitForSelector('.submission-progress-dialog', {timeout: 5000}).then(() => look(`L02-submitting-${T}`, ['.submission-progress-dialog'], {settle: 0})).catch(() => notes.push(`${T}: 제출 진행 팝업이 너무 빨리 끝나 캡처 못 함`));
        await page.waitForFunction(() => ['passed', 'incorrect', 'error'].includes(document.querySelector('.result-pane')?.dataset.feedback), null, {timeout: 90000});
        await look(`L03-feedback-${T}`, ['.result-pane']);
      });
      await step(`lesson info and reset confirm ${T}`, async () => {
        await page.locator('.lesson-info-trigger').click();
        await page.waitForFunction(() => document.getElementById('lesson-info-dialog')?.open);
        await look(`L04-lesson-info-${T}`, ['#lesson-info-dialog']);
        const reset = page.locator('#lesson-info-dialog .lesson-reset-open');
        if (await reset.count() && await reset.isEnabled()) { await reset.click(); await page.waitForTimeout(300); await look(`L05-lesson-reset-confirm-${T}`, ['#lesson-info-dialog']); const cancel = page.locator('#lesson-info-dialog .lesson-reset button', {hasText: '취소'}); if (await cancel.count()) await cancel.click(); }
        await focusCheck(`L04-focus-${T}`, '#lesson-info-dialog');
        await page.keyboard.press('Escape');
      });
      await step(`lesson menus ${T}`, async () => {
        await page.locator('.repository-study .content-update-controls > details > summary').first().click();
        await look(`L06-lesson-menu-${T}`, ['.content-update-menu']);
        await closeDetails('.content-update-controls > details');
      });
      await step(`code flow dialog ${T}`, async () => {
        const doc = JSON.parse(fs.readFileSync(path.join(__dirname, '../../target/ui-fixtures/trace.json'), 'utf8'));
        await page.evaluate((doc) => { const t = window.mqCodeFlow.loading(); window.mqCodeFlow.show(t, doc); }, doc);
        await page.waitForSelector('.code-flow-dialog[open]', {timeout: 5000});
        await look(`L07-code-flow-${T}`, ['.code-flow-dialog']);
        await focusCheck(`L07-focus-${T}`, '.code-flow-dialog');
        await page.keyboard.press('Escape');
      });
      await step(`auto run ${T}`, async () => {
        await page.waitForSelector('#auto-run-start:not([disabled])', {timeout: 30000});
        await page.locator('#auto-run-start').click();
        await page.waitForSelector('.auto-run-control[data-state="running"]', {timeout: 30000});
        await page.waitForTimeout(1500);
        await look(`L08-auto-running-${T}`, ['.agent-caption']);
        await page.keyboard.press('Escape');
        await page.waitForSelector('.auto-run-control:not([data-state="running"])', {timeout: 30000});
        await page.locator('.auto-run-details > summary').click();
        await look(`L09-auto-stopped-${T}`, ['.auto-run-menu']);
        await page.locator('.auto-run-dismiss').click();
      });
      await step(`git graph ${T}`, async () => {
        // The Git lesson by title (the seeded catalog can be grouped by category, so indexes move).
        await toCatalog(); if (await button('수업 목록').count()) await button('수업 목록').click();
        if (await button('전체 순서').count()) await button('전체 순서').click();
        const card = page.locator('.lesson-card').filter({hasText: 'Git · 브랜치 기본'}).first(); await card.waitFor({timeout: 10000}); await card.scrollIntoViewIfNeeded();
        await card.locator('button', {hasText: /학습 시작|이어서|다시 보기|복습/}).first().click();
        await page.waitForSelector('.study-navigation', {timeout: 60000}); await openTask(3);
        await page.waitForFunction(() => document.querySelector('.repository-task')?.dataset.gitReady === 'true', null, {timeout: 120000});
        await look(`L10-git-${T}`, ['.git-graph-panel']);
        const big = page.locator('.git-graph-panel button', {hasText: '크게 보기'}).first();
        if (await big.count()) { await big.click(); await page.waitForTimeout(400); await look(`L11-git-graph-expanded-${T}`, ['.git-graph-panel.is-expanded']); await page.keyboard.press('Escape'); const small = page.locator('.git-graph-panel button', {hasText: /작게|닫기/}).first(); if (await small.count()) await small.click(); }
      });
    }
  }
  notes.push(`TOTAL FAIL ${fails.length}`);
  fs.writeFileSync(path.join(output, 'fails.txt'), fails.join('\n') + '\n');
  return notes;
};
