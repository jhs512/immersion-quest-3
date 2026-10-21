// `autofocus` only works while a page loads; a popup rendered later (the instructor login, the
// reward card, a confirm dialog) gets no focus from it. This watches the page and focuses the
// first [autofocus] element of anything newly added, so Enter and typing go where the eye is.
// <dialog> elements opened with showModal() already do this themselves and are left alone.
(function () {
  'use strict';
  if (globalThis.molipAutofocus || typeof document === 'undefined') return;
  const focusWithin = node => {
    if (!(node instanceof Element)) return;
    const target = node.matches('[autofocus]') ? node : node.querySelector('[autofocus]');
    if (!target || target.closest('dialog')) return;
    setTimeout(() => { if (target.isConnected && document.activeElement !== target) target.focus(); }, 0);
  };
  const observer = new MutationObserver(records => {
    for (const record of records) for (const node of record.addedNodes) focusWithin(node);
  });
  observer.observe(document.body, { childList: true, subtree: true });
  // Toolbar popovers behave alike: one open at a time, outside click and Escape close.
  // Restrict this to toolbar details so lesson hints and provided files stay open.
  const menuSelector='.app-update-settings, .repository-tools .content-update-controls>details';
  const menus=()=>[...document.querySelectorAll(menuSelector)].filter(menu=>menu.open);
  document.addEventListener('toggle',event=>{
    if(!(event.target instanceof Element)||!event.target.matches(menuSelector)||!event.target.open)return;
    for(const menu of menus())if(menu!==event.target)menu.open=false;
  },true);
  document.addEventListener('click',event=>{
    for(const menu of menus())if(!menu.contains(event.target))menu.open=false;
  });
  window.addEventListener('keydown',event=>{
    if(event.key!=='Escape'||event.isComposing)return;
    if([...document.querySelectorAll('dialog[open],[role="dialog"]')].some(dialog=>dialog.getClientRects().length>0))return;
    const open=menus();if(!open.length)return;
    event.preventDefault();event.stopImmediatePropagation();
    for(const menu of open)menu.open=false;
    open[open.length-1].querySelector('summary')?.focus();
  },true);
  globalThis.molipAutofocus = { focusWithin };
})();
