// Drag handles for the coding mission layout.
//
// `.split-col` sits between the problem pane and the code pane and sets
// `--problem-width` on `.lesson`; `.split-row` sits between the editor and the
// run results and sets `--editor-height` on `.coding-pane`. Sizes persist in
// localStorage and are re-applied whenever a mission mounts. Arrow keys move a
// focused handle; double-click restores the default split.
(function () {
  'use strict';
  if (globalThis.molipSplit || typeof document === 'undefined') return;
  const KEY = 'molip:split';
  let saved = {};
  try { saved = JSON.parse(localStorage.getItem(KEY) || '{}') || {}; } catch {}
  const persist = () => { try { localStorage.setItem(KEY, JSON.stringify(saved)); } catch {} };

  // `.assistant-handle` sits left of the AI dock and sets `--assistant-width` on their parent;
  // dragging it left makes the dock wider, so its delta is inverted.
  const axis = handle => handle.classList.contains('assistant-handle')
    ? { key: 'assistant', prop: '--assistant-width', container: handle.parentElement, pane: '.assistant-dock', horizontal: true, min: 280, reserve: 420, invert: true }
    : handle.classList.contains('split-col')
    ? { key: 'problem', prop: '--problem-width', container: handle.closest('.lesson'), pane: '.problem-pane', horizontal: true, min: 260, reserve: 360 }
    : handle.classList.contains('split-example')
    ? { key: 'exampleAnswer', prop: '--example-answer-height', container: handle.closest('.interaction-example-editor'), pane: '.interaction-example-answer', horizontal: false, min: 64, reserve: 58, invert: true }
    : { key: 'editor', prop: '--editor-height', container: handle.closest('.coding-pane'), pane: '.editor-pane', horizontal: false, min: 120, reserve: 54 + 8 + 140 };

  function set(a, size, gesture) {
    // The answer pane yields first. Continue the same drag into the result pane
    // once answers reach their minimum, without accumulating repeated pointer deltas.
    if (a.key === 'exampleAnswer') {
      const coding = a.container.closest('.coding-pane');
      const lower = coding?.querySelector(':scope > .split-row');
      if (lower && (size < a.min || gesture?.cascaded)) {
        const outer = axis(lower);
        const baseline = gesture?.outerSize ?? a.container.getBoundingClientRect().height;
        if (gesture) gesture.cascaded = true;
        set(outer, baseline + Math.max(0, a.min - size));
      }
    }
    const bounds = a.container.getBoundingClientRect();
    let min=a.min, reserve=a.reserve;
    if(a.key==='editor' && a.container.closest('.repository-task')) {
      min=a.container.querySelector('.interaction-example-editor')?142:96;
      reserve=(a.container.querySelector('.pane-heading')?.getBoundingClientRect().height||0)+
        (a.container.querySelector(':scope > .split-row')?.getBoundingClientRect().height||10)+74;
    }
    if(a.key==='exampleAnswer') {
      const style=getComputedStyle(a.container);
      reserve+=parseFloat(style.paddingTop)+parseFloat(style.paddingBottom);
    }
    const max=Math.max(min,(a.horizontal ? bounds.width : bounds.height)-reserve);
    size = Math.round(Math.max(min, Math.min(max, size)));
    a.container.style.setProperty(a.prop, size + 'px');
    saved[a.key] = size;
  }
  function applyAll() {
    for(const handle of document.querySelectorAll('.split-handle')) {
      const a=axis(handle);
      if(a.container && saved[a.key]) set(a,saved[a.key]);
    }
  }
  const paneFor=a=>[...a.container.querySelectorAll(a.pane)].find(p=>p.getBoundingClientRect().height>0);

  document.addEventListener('pointerdown', event => {
    const handle = event.target.closest('.split-handle');
    if (!handle || event.button !== 0) return;
    const a = axis(handle);
    if (!a.container) return;
    const pane = paneFor(a);
    if(!pane)return;
    const start = a.horizontal ? event.clientX : event.clientY;
    const rect = pane.getBoundingClientRect();
    const startSize = a.horizontal ? rect.width : rect.height;
    const gesture = {outerSize:a.container.getBoundingClientRect().height, cascaded:false};
    try { handle.setPointerCapture(event.pointerId); } catch {}
    handle.classList.add('dragging'); document.body.classList.add('splitting');
    const move = ev => set(a, startSize + (a.invert ? -1 : 1) * ((a.horizontal ? ev.clientX : ev.clientY) - start), gesture);
    const stop = () => {
      handle.removeEventListener('pointermove', move); handle.removeEventListener('pointerup', stop); handle.removeEventListener('pointercancel', stop);
      handle.classList.remove('dragging'); document.body.classList.remove('splitting');
      try { handle.releasePointerCapture(event.pointerId); } catch {}
      persist();
    };
    handle.addEventListener('pointermove', move); handle.addEventListener('pointerup', stop); handle.addEventListener('pointercancel', stop);
    event.preventDefault();
  });
  document.addEventListener('keydown', event => {
    const handle = event.target instanceof Element && event.target.closest('.split-handle');
    if (!handle) return;
    const a = axis(handle);
    const step = event.shiftKey ? 40 : 10;
    const delta = { ArrowLeft: -step, ArrowRight: step }[event.key] ?? { ArrowUp: -step, ArrowDown: step }[event.key];
    const matches = a.horizontal ? /^Arrow(Left|Right)$/ : /^Arrow(Up|Down)$/;
    if (!matches.test(event.key) || !a.container) return;
    event.preventDefault();
    const pane=paneFor(a);if(!pane)return;
    const rect = pane.getBoundingClientRect();
    set(a, (a.horizontal ? rect.width : rect.height) + (a.invert ? -delta : delta)); persist();
  });
  document.addEventListener('dblclick', event => {
    const handle = event.target.closest('.split-handle');
    if (!handle) return;
    const a = axis(handle);
    if (!a.container) return;
    a.container.style.removeProperty(a.prop); delete saved[a.key]; persist();
  });
  new MutationObserver(records => {
    if (records.some(r => [...r.addedNodes].some(n => n instanceof Element && (n.matches('.lesson, .assistant-dock') || n.querySelector('.lesson, .assistant-dock'))))) applyAll();
  }).observe(document.body, { childList: true, subtree: true });
  window.addEventListener('resize',()=>requestAnimationFrame(applyAll));
  const sizes=new ResizeObserver(()=>applyAll());
  const observed=new Set();
  const watch=()=>{
    for(const pane of observed)if(!pane.isConnected){sizes.unobserve(pane);observed.delete(pane)}
    for(const pane of document.querySelectorAll('.coding-pane,.interaction-example-editor'))if(!observed.has(pane)){observed.add(pane);sizes.observe(pane)}
  };
  new MutationObserver(watch).observe(document.body,{childList:true,subtree:true});watch();
  applyAll();
  globalThis.molipSplit = { applyAll };
})();
