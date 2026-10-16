// Marp slide decks inside the app.
//
// A slides mission renders its Markdown through Marp Core (bundled here, offline) into
// scaled SVG slides and shows one at a time with ←/→, a counter and a fullscreen
// button, so the instructor can project a deck from the same screen students use.
// comic-gen, mapping and interactive fences inside slides are picked up by the other
// loaders because the rendered DOM contains ordinary <pre><code> blocks.
import { Marp } from '@marp-team/marp-core';
import { load } from 'js-yaml';

const marp = new Marp({ html: false, inlineSVG: false, minifyCSS: false });
// Course prose also uses spaced markers and Korean words next to emphasis.
// Handle those as inline tokens; fenced and inline code never enter this rule.
marp.markdown.inline.ruler.before('emphasis', 'course_strong', (state, silent) => {
  if (state.src.slice(state.pos, state.pos + 2) !== '**') return false;
  const end = state.src.indexOf('**', state.pos + 2);
  if (end < 0) return false;
  const content = state.src.slice(state.pos + 2, end).trim();
  if (!content || content.includes('\n')) return false;
  if (!silent) {
    state.push('strong_open', 'strong', 1);
    const children = [];
    state.md.inline.parse(content, state.md, state.env, children);
    for (const token of children) { token.level += state.level; state.tokens.push(token); }
    state.push('strong_close', 'strong', -1);
  }
  state.pos = end + 2;
  return true;
});
// A friendly default theme: Pretendard, dark text on a warm paper, accent for headings.
marp.themeSet.add(`/* @theme molip */
section::after { content: attr(data-marpit-pagination) ' / ' attr(data-marpit-pagination-total); font-size: 20px; color: #6b7c8c; }
section { width: 1280px; height: 720px; padding: 64px 80px; font-family: 'Pretendard', 'Malgun Gothic', sans-serif; font-size: 30px; line-height: 1.6; color: #1d2b3a; background: #fbf8f1; }
section h1 { font-size: 60px; line-height: 1.25; margin: 0 0 24px; color: #0f3d5e; letter-spacing: -1px; }
section h2 { font-size: 44px; margin: 0 0 20px; color: #0f3d5e; letter-spacing: -0.5px; }
section h3 { font-size: 34px; margin: 0 0 12px; color: #236b55; }
section p, section li { margin: 0 0 10px; }
section ul, section ol { padding-left: 1.2em; }
section strong { color: #b2461d; }
section code { font-family: 'JetBrains Mono', 'Pretendard', monospace; font-size: 0.85em; background: #eee8da; padding: 2px 8px; border-radius: 6px; }
section pre { background: #16283a; color: #e4eef7; padding: 20px 24px; border-radius: 12px; font-size: 24px; line-height: 1.5; }
section pre code { background: none; color: inherit; padding: 0; font-size: inherit; }
section blockquote { border-left: 6px solid #e0a63a; margin: 12px 0; padding: 6px 24px; color: #4a5a6a; font-size: 28px; }
section table { font-size: 24px; border-collapse: collapse; } section th, section td { border: 1px solid #cfc7b5; padding: 8px 14px; } section th { background: #eee8da; }
section footer, section header { color: #8a93a0; font-size: 18px; }
section.lead { display: flex; flex-direction: column; justify-content: center; text-align: center; background: #0f3d5e; color: #f4f8fb; }
section.lead h1, section.lead h2 { color: #ffffff; } section.lead strong { color: #ffd37a; }
section.lead p { font-size: 34px; color: #d6e4f0; }
section .comic-strip { height: 380px; display: flex; align-items: center; justify-content: center; }
section .comic-strip + p { font-size: 26px; margin-top: 4px; }
section .comic-strip svg { max-height: 100%; max-width: 100%; width: auto; height: auto; margin: 0 auto; }
/* A slide that holds a comic panel stacks as a column so the strip takes every pixel the
   heading and caption leave over, instead of a fixed 380px with the rest of the slide empty. */
section.comic { display: flex; flex-direction: column; }
section.comic > * { flex: none; }
section.comic > .comic-strip { flex: 1 1 0; min-height: 0; height: auto; }
/* A panel with a diagram is split by comics.js: the diagram alone on the left, the characters
   and their speech on the right, so neither is squeezed under the other. */
section .comic-split { gap: 28px; }
section .comic-split > div { max-height: 100%; min-width: 0; display: flex; align-items: center; justify-content: center; }
section .comic-split > .comic-split-diagram { flex: 13 1 0; padding: 16px; box-sizing: border-box; background: #ffffff; border: 1px solid #cfd8e3; border-radius: 14px; }
section .comic-split > .comic-split-panel { flex: 7 1 0; height: 100%; }
section figure { margin: 8px 0; }
section .columns { display: grid; grid-template-columns: 1fr 1fr; gap: 32px; }
`);

export function renderDeck(markdown) {
  const { html, css, comments } = marp.render(paginateComics(markdown));
  // Presenter notes: every non-directive HTML comment of a slide, joined. Slides generated for
  // comic panels carry a copy of their source slide's comments (paginateComics).
  const notes = (comments || []).map(list => list.map(c => c.trim()).filter(Boolean).join('\n\n'));
  return { html, css, notes };
}

function paginateComics(markdown) {
  const lines = markdown.split('\n');
  const tokens = marp.markdown.parse(markdown, {});
  const replacements = [];
  for (const token of tokens) {
    if (token.type !== 'fence' || token.info.trim() !== 'comic-gen') continue;
    let comic;
    try { comic = load(token.content); } catch { continue; } // Loader shows authoring errors.
    const panels = comic?.['컷'];
    if (!Array.isArray(panels)) continue;
    const [start, end] = token.map;
    let heading = '';
    let slideStart = 0, slideEnd = lines.length;
    for (let i = start - 1; i >= 0; i--) {
      if (lines[i].trim() === '---') { slideStart = i + 1; break; }
      if (!heading && /^#{1,3}\s/.test(lines[i])) heading = lines[i];
    }
    for (let i = end; i < lines.length; i++) if (lines[i].trim() === '---') { slideEnd = i; break; }
    // The slide's presenter notes (non-directive comments) travel with every generated panel slide.
    const notes = (lines.slice(slideStart, slideEnd).join('\n').match(/<!--[\s\S]*?-->/g) || [])
      .filter(c => !/^<!--\s*_?[a-zA-Z]+\s*:/.test(c));
    const fence = lines[start].trim();
    // Keep the complete script so "구성: 이전" and character inheritance resolve.
    // The comic loader selects one resolved SVG panel per generated slide.
    // Every generated slide gets the `comic` class so the theme lets the strip fill the slide;
    // the panels after the first are `continued`: the same source slide, shown one panel at a
    // time, so anything that counts slides the way the Markdown does can step over them.
    replacements.push({ start, end, content: panels.map((_, i) =>
      `${i ? `\n---\n\n${heading}\n\n${notes.join('\n')}\n\n` : ''}<!-- _class: ${i ? 'comic continued' : 'comic'} -->\n${fence}\n# molip-panel:${i}\n${token.content}\`\`\``
    ).join('\n') });
  }
  for (const item of replacements.reverse()) lines.splice(item.start, item.end - item.start, item.content);
  return lines.join('\n');
}

// Hosts can be reused with a different deck (the PPT gallery's previous/next), so a host is
// re-rendered whenever its source changes rather than only on first sight.
const mountedSource = new WeakMap();
function mount(host) {
  const source = host.dataset.marpSource || '';
  if (mountedSource.get(host) === source) return;
  mountedSource.set(host, source);
  let rendered;
  try { rendered = renderDeck(source); } catch (error) { host.textContent = '슬라이드를 그리지 못했습니다: ' + error.message; return; }
  const style = document.createElement('style'); style.textContent = rendered.css;
  const stage = document.createElement('div'); stage.className = 'slides-stage'; stage.innerHTML = rendered.html;
  // Presentation mode: a thin gauge along the top shows how far into the deck we are.
  const progress = document.createElement('div'); progress.className = 'slides-progress'; progress.setAttribute('aria-hidden', 'true');
  const progressFill = document.createElement('div'); progressFill.className = 'slides-progress-fill'; progress.append(progressFill);
  const slides = [...stage.querySelectorAll(':scope > .marpit > svg, :scope > .marpit > section')];
  // Fit: the deck is laid out at 1280×720 and scaled with a transform to the stage's width (and,
  // outside presentation, to 70% of the window height), so every engine shows the same thing.
  const deck = stage.querySelector(':scope > .marpit');
  const scaler = document.createElement('div'); scaler.className = 'slides-scaler';
  if (deck) { deck.replaceWith(scaler); scaler.append(deck); }
  const fit = () => {
    if (!deck) return;
    const style = getComputedStyle(stage);
    const inner = stage.clientWidth - parseFloat(style.paddingLeft || '0') - parseFloat(style.paddingRight || '0');
    const presenting = host.classList.contains('slides-presenting');
    const byHeight = (presenting ? innerHeight : innerHeight * 0.7) / 720;
    const k = Math.max(0.05, Math.min(inner / 1280, byHeight));
    deck.style.transform = `scale(${k})`;
    scaler.style.width = `${Math.round(1280 * k)}px`;
    scaler.style.height = `${Math.round(720 * k)}px`;
  };
  if (typeof ResizeObserver !== 'undefined') new ResizeObserver(fit).observe(stage);
  window.addEventListener('resize', fit);
  const bar = document.createElement('div'); bar.className = 'slides-bar';
  const prev = document.createElement('button'); prev.type = 'button'; prev.textContent = '← 이전 장';
  const counter = document.createElement('span'); counter.className = 'slides-counter';
  const next = document.createElement('button'); next.type = 'button'; next.textContent = '다음 장 →';
  const full = document.createElement('button'); full.type = 'button'; full.textContent = '전체 화면'; full.className = 'slides-full';
  // Presenter script: the slide's notes (what the instructor says, one message per slide) and a
  // glimpse of the next slide's line, so the flow is visible. Right-click on the slide or the
  // 스크립트 button toggles it; it follows the current slide and works in presentation mode.
  const notesButton = document.createElement('button'); notesButton.type = 'button'; notesButton.textContent = '스크립트'; notesButton.className = 'slides-notes-toggle';
  const notes = document.createElement('aside'); notes.className = 'slides-notes'; notes.hidden = true; notes.setAttribute('aria-label', '강사 스크립트');
  const notesText = document.createElement('p'); notesText.className = 'slides-notes-text';
  const notesNext = document.createElement('p'); notesNext.className = 'slides-notes-next';
  notes.append(notesText, notesNext);
  let notesOpen = false;
  const updateNotes = () => {
    const line = rendered.notes[index] || '';
    notesText.textContent = line || '(이 장에는 스크립트가 없습니다)';
    const coming = rendered.notes[index + 1];
    notesNext.textContent = coming ? '다음 → ' + coming.split(/(?<=[.!?。])\s/)[0].slice(0, 70) : (index === slides.length - 1 ? '마지막 장' : '');
    notes.hidden = !notesOpen;
    notesButton.classList.toggle('active', notesOpen);
  };
  const toggleNotes = on => { notesOpen = on === undefined ? !notesOpen : !!on; updateNotes(); };
  stage.addEventListener('contextmenu', event => { event.preventDefault(); toggleNotes(); });
  notesButton.onclick = () => toggleNotes();
  // Presentation mode: the host covers the whole screen (and asks the window to go
  // fullscreen); the control bar only shows while the mouse moves. Esc leaves it.
  let uiTimer = 0;
  const showUi = () => {
    host.classList.add('slides-ui-visible');
    clearTimeout(uiTimer);
    uiTimer = setTimeout(() => host.classList.remove('slides-ui-visible'), 2500);
  };
  const present = on => {
    host.classList.toggle('slides-presenting', on);
    requestAnimationFrame(fit);
    full.textContent = on ? '발표 종료 (Esc)' : '전체 화면';
    if (on) {
      const shortcuts = globalThis.molipShortcuts;
      if (shortcuts && !shortcuts.isFullscreen()) shortcuts.toggleFullscreen();
      showUi();
      host.focus();
    } else {
      host.classList.remove('slides-ui-visible');
    }
  };
  // Chromium also fires a mousemove when the element under a still cursor changes (the bar
  // hiding does that), so only a cursor that actually moved reveals the bar.
  let lastX = -1, lastY = -1;
  host.addEventListener('mousemove', event => {
    const moved = event.clientX !== lastX || event.clientY !== lastY;
    lastX = event.clientX; lastY = event.clientY;
    if (moved && host.classList.contains('slides-presenting')) showUi();
  });
  bar.append(prev, counter, next, notesButton, full);
  host.replaceChildren(style, progress, stage, notes, bar);
  fit(); requestAnimationFrame(fit);
  let index = 0;
  const update = () => {
    slides.forEach((s, i) => { s.style.display = i === index ? '' : 'none'; });
    counter.textContent = `${index + 1} / ${slides.length}`;
    progressFill.style.width = `${(index + 1) * 100 / slides.length}%`;
    prev.disabled = index === 0; next.disabled = index === slides.length - 1;
    host.dataset.slideIndex = String(index);
    updateNotes();
    // Reaching the last slide completes the mission: the Rust side listens on a hidden button.
    if (index === slides.length - 1) host.closest('.slides-mission')?.querySelector('.slides-finish')?.click();
  };
  prev.onclick = () => { if (index > 0) { index--; update(); } };
  next.onclick = () => { if (index < slides.length - 1) { index++; update(); } };
  full.onclick = () => present(!host.classList.contains('slides-presenting'));
  host.tabIndex = 0;
  // Past the last slide, → moves on to the next mission (and ← before the first slide goes
  // back one), through the mission's own 이전/다음 buttons so the learning flow stays in charge.
  const missionNav = text => [...(host.closest('.slides-mission, .gallery') || document).querySelectorAll('.mission-nav button, .header-navigation button, .gallery-nav button')]
    .find(b => b.textContent.trim() === text && !b.disabled) || null;
  const leaveTo = text => {
    const b = missionNav(text); if (!b) return false;
    // Presenting: the next mission, if it is a deck, opens straight in presentation mode
    // (mount() reads this within a few seconds); otherwise the flag just lapses.
    if (host.classList.contains('slides-presenting')) globalThis.molipSlides.carryPresenting = Date.now();
    b.click(); return true;
  };
  host.addEventListener('keydown', event => {
    if (event.key === 'ArrowRight' || event.key === 'PageDown' || event.key === ' ') {
      event.preventDefault();
      if (index === slides.length - 1) leaveTo('다음 →'); else next.click();
    }
    if (event.key === 'ArrowLeft' || event.key === 'PageUp') {
      event.preventDefault();
      if (index === 0) leaveTo('← 이전'); else prev.click();
    }
    if (event.key === 'Escape' && notesOpen) { event.preventDefault(); toggleNotes(false); return; }
    if (event.key === 'Escape' && host.classList.contains('slides-presenting')) { event.preventDefault(); present(false); }
    if ((event.key === 'n' || event.key === 'N') && !event.ctrlKey && !event.metaKey && !event.altKey) { event.preventDefault(); toggleNotes(); }
  });
  host.molipPresent = present;
  const carried = globalThis.molipSlides.carryPresenting;
  if (carried && Date.now() - carried < 5000) { delete globalThis.molipSlides.carryPresenting; setTimeout(() => present(true), 50); }
  host.molipNotes = { toggle: toggleNotes, get open() { return notesOpen; }, get text() { return notesText.textContent; } };
  // For the tutor agent, which counts slides as the Markdown does: a comic's extra panels are
  // `continued` slides. nextSource() shows any remaining panels of the current source slide for
  // `dwell` ms each, then lands on the next source slide; it resolves false at the end of the deck.
  const isContinued = i => !!slides[i]?.querySelector('section.continued');
  host.molipSlides = {
    get index() { return index; }, get count() { return slides.length; }, isContinued,
    // Back to the first slide (a narration script always starts from the top of the deck).
    first() { if (index !== 0) { index = 0; update(); } },
    sourceIndex(i) { let n = 0; for (let k = 0; k <= i; k++) if (!isContinued(k)) n++; return n; },
    async nextSource(dwell = 1500) {
      if (index >= slides.length - 1) return false;
      while (index < slides.length - 1 && isContinued(index + 1)) {
        index++; update();
        await new Promise(resolve => setTimeout(resolve, dwell));
      }
      if (index >= slides.length - 1) return false;
      index++; update();
      return true;
    },
  };
  update();
  globalThis.molipSlides.count += 1;
}
function render(root) {
  if (!(root instanceof Element) && root !== document) return;
  const hosts = [...root.querySelectorAll('[data-marp-source]')];
  if (root instanceof Element && root.matches('[data-marp-source]')) hosts.push(root);
  hosts.forEach(mount);
}
globalThis.molipSlides = { render, renderDeck, count: 0 };
new MutationObserver(records => {
  for (const r of records) {
    if (r.type === 'attributes') { render(r.target); continue; }
    for (const n of r.addedNodes) if (n instanceof Element) render(n);
  }
}).observe(document.body, { childList: true, subtree: true, attributes: true, attributeFilter: ['data-marp-source'] });
render(document);
