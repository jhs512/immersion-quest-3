// Draw comic-gen code fences from course Markdown as inline comic strips.
//
// The Markdown renderer leaves ```comic-gen fences as `pre > code.language-comic-gen`.
// This loader imports the vendored Comic Gen SDK (an ES module, so it is loaded
// from a Blob URL built from `window.__molipComicGenSource`), renders each fence
// to an SVG, and replaces the fence with a <figure>. Slides select one resolved
// panel via a molip-panel marker, sharing the rendered script across slides. Missions
// re-render on navigation, so a MutationObserver draws fences as they appear.
(function () {
  'use strict';
  if (globalThis.molipComics) return;
  const source = globalThis.__molipComicGenSource;
  delete globalThis.__molipComicGenSource;
  if (typeof document === 'undefined' || !source) return;
  // Mermaid diagrams inside panels: the SDK would fetch its loader and Mermaid from a CDN,
  // so the vendored Mermaid build is served from a Blob URL through a tiny loader of our own
  // that fulfils the same ready/error events. Comics then render fully offline.
  const mermaidSource = globalThis.__molipMermaidSource;
  delete globalThis.__molipMermaidSource;
  let sdkSource = source;
  if (mermaidSource) {
    const mermaidUrl = URL.createObjectURL(new Blob([mermaidSource], { type: 'text/javascript' }));
    const loader = "const s=document.createElement('script');s.src=" + JSON.stringify(mermaidUrl)
      + ";s.onload=()=>{const e=globalThis.mermaid;if(e&&typeof e.initialize==='function'&&typeof e.render==='function'){Object.defineProperty(window,'__comicGenMermaid',{value:e});window.dispatchEvent(new Event('comic-gen-mermaid-ready'));}else{window.dispatchEvent(new Event('comic-gen-mermaid-error'));}};"
      + "s.onerror=()=>window.dispatchEvent(new Event('comic-gen-mermaid-error'));document.head.append(s);";
    const loaderUrl = URL.createObjectURL(new Blob([loader], { type: 'text/javascript' }));
    sdkSource = sdkSource.replace('"https://cdn.jsdelivr.net/gh/jhs512/comic-gen@v0.6.0/cdn/comic-gen.mermaid.js"', JSON.stringify(loaderUrl));
  }
  const url = URL.createObjectURL(new Blob([sdkSource], { type: 'text/javascript' }));
  const sdk = import(url).catch(error => { console.error('comic-gen SDK failed to load', error); return null; });
  const seen = new WeakSet();
  let count = 0;
  const slideRenders = new Map();

  async function render(root) {
    if (!(root instanceof Element) && root !== document) return;
    const codes = [...root.querySelectorAll('pre > code.language-comic-gen')];
    if (root instanceof Element && root.matches('pre > code.language-comic-gen')) codes.push(root);
    if (!codes.length) return;
    const api = await sdk;
    for (const code of codes) {
      const pre = code.parentElement;
      if (!pre || !pre.isConnected || seen.has(pre)) continue;
      seen.add(pre);
      const figure = document.createElement('figure');
      figure.className = 'comic-strip';
      figure.setAttribute('aria-label', '설명 만화');
      try {
        if (!api) throw new Error('SDK unavailable');
        const panelMarker = code.textContent.match(/^# molip-panel:(\d+)\n/);
        const script = code.textContent.replace(/^# molip-panel:\d+\n/, '');
        const result = await (panelMarker ? cachedRender(api, script, 720) : api.renderComicAsync(script, { 너비: 720 }));
        if (result.diagnostics.length) throw new Error(result.diagnostics.join(' / '));
        const panel = panelMarker && result.panels[Number(panelMarker[1])];
        if (panel) await placeSlidePanel(api, script, Number(panelMarker[1]), panel, figure, !!pre.nextElementSibling);
        else figure.innerHTML = result.svg;
        const svg = figure.querySelector('svg');
        if (svg) { svg.setAttribute('role', 'img'); svg.setAttribute('aria-label', panel ? `설명 만화 ${Number(panelMarker[1]) + 1} / ${result.panels.length}컷` : '설명 만화 ' + ((result.panels && result.panels.length) || 1) + '컷'); }
        count += 1;
      } catch (error) {
        figure.classList.add('comic-error');
        figure.textContent = '만화를 그리지 못했습니다: ' + (error && error.message ? error.message : error);
      }
      pre.replaceWith(figure);
    }
  }
  // Slide comics. The SDK keeps a panel's height fixed and only widens it, so a 720-wide panel
  // 820 tall lands at 334 x 380 on a 1280 x 720 slide with the sides empty. Two fixes:
  //  - a panel with a diagram is split: the diagram SVG the SDK drew on its board is lifted out
  //    to the left, and the panel is drawn again without the diagram for the right, at the SDK's
  //    narrowest width (480) so the narrow column shrinks it less and the bubbles stay readable;
  //  - any other panel is rendered again at the width that makes it fill the slide box
  //    (content width 1120; height ~400 under a caption, ~500 without one; SDK cap 2400).
  const SLIDE_BOX_WIDTH = 1120, SLIDE_BOX_CAPTIONED = 400, SLIDE_BOX_PLAIN = 500, SPLIT_PANEL_WIDTH = 480;
  function cachedRender(api, script, width) {
    const key = width + '\n' + script;
    let pending = slideRenders.get(key);
    if (!pending) { pending = api.renderComicAsync(script, { 너비: width }); slideRenders.set(key, pending); }
    return pending;
  }
  // Drops every `다이어그램:` block (its lines are indented deeper than the key).
  function withoutDiagrams(script) {
    const out = []; let skipDeeperThan = -1;
    for (const line of script.split('\n')) {
      const indent = line.match(/^ */)[0].length;
      if (skipDeeperThan >= 0) { if (!line.trim() || indent > skipDeeperThan) continue; skipDeeperThan = -1; }
      if (/^\s*다이어그램\s*:/.test(line)) { skipDeeperThan = indent; continue; }
      out.push(line);
    }
    return out.join('\n');
  }
  function diagramOf(panelSvg) {
    const holder = document.createElement('div'); holder.innerHTML = panelSvg;
    const nested = holder.querySelectorAll('svg svg');
    const board = nested.length ? nested[nested.length - 1] : null;
    // The SDK inlines Mermaid's output as a nested <svg role="graphics-document"> with its
    // classes stripped, so the role is what identifies it.
    if (!board || !/graphics-document/.test(board.getAttribute('role') || '')) return null;
    const svg = board.cloneNode(true);
    svg.removeAttribute('x'); svg.removeAttribute('y');
    for (const property of ['width', 'height', 'max-width', 'max-height']) svg.style.removeProperty(property);
    if (!svg.getAttribute('viewBox') && svg.getAttribute('width') && svg.getAttribute('height')) svg.setAttribute('viewBox', `0 0 ${parseFloat(svg.getAttribute('width'))} ${parseFloat(svg.getAttribute('height'))}`);
    return svg;
  }
  async function placeSlidePanel(api, script, index, panel, figure, captioned) {
    const diagram = /^\s*다이어그램\s*:/m.test(script) ? diagramOf(panel.svg) : null;
    if (diagram) {
      try {
        const rest = await cachedRender(api, withoutDiagrams(script), SPLIT_PANEL_WIDTH);
        const own = !rest.diagnostics.length && rest.panels[index];
        if (own) {
          figure.classList.add('comic-split');
          const left = document.createElement('div'); left.className = 'comic-split-diagram'; left.append(diagram);
          const right = document.createElement('div'); right.className = 'comic-split-panel'; right.innerHTML = own.svg;
          figure.replaceChildren(left, right);
          return;
        }
      } catch (error) { console.warn('comic split failed, showing the whole panel', error); }
    }
    const boxHeight = captioned ? SLIDE_BOX_CAPTIONED : SLIDE_BOX_PLAIN;
    const width = Math.min(2400, Math.max(720, Math.round(SLIDE_BOX_WIDTH * (panel.height || 0) / boxHeight)));
    let shown = panel;
    if (width > 720) {
      const wide = await cachedRender(api, script, width);
      if (!wide.diagnostics.length && wide.panels[index]) shown = wide.panels[index];
    }
    figure.innerHTML = shown.svg;
  }
  const observer = new MutationObserver(records => {
    for (const record of records) for (const node of record.addedNodes) if (node instanceof Element) render(node);
  });
  const start = () => { observer.observe(document.body, { childList: true, subtree: true }); render(document); };
  if (document.body) start(); else document.addEventListener('DOMContentLoaded', start);
  globalThis.molipComics = { render, get count() { return count; }, ready: sdk.then(api => !!api) };
})();
