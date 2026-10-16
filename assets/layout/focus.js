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
  globalThis.molipAutofocus = { focusWithin };
})();
