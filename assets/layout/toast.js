// A single floating notice anchored to the last click: it opens at the upper right of the
// point that was clicked, is kept inside the window, and is replaced on each call.
(function () {
  'use strict';
  if (globalThis.molipToast || typeof document === 'undefined') return;
  let host, timer;
  let anchor = null;
  document.addEventListener('pointerdown', event => { anchor = { x: event.clientX, y: event.clientY }; }, { capture: true, passive: true });
  document.addEventListener('keydown', event => {
    // Keyboard activation: anchor at the focused element's top-right corner.
    if ((event.key === 'Enter' || event.key === ' ') && document.activeElement instanceof Element) {
      const r = document.activeElement.getBoundingClientRect();
      anchor = { x: r.right, y: r.top };
    }
  }, { capture: true, passive: true });
  globalThis.molipToast = function (text, kind) {
    if (!host) {
      host = document.createElement('div');
      host.className = 'molip-toast';
      host.setAttribute('role', 'status');
      host.setAttribute('aria-live', 'polite');
      document.body.append(host);
    }
    host.textContent = text;
    host.dataset.kind = kind || 'info';
    host.classList.remove('show');
    // Measure first, then place: bottom-left corner of the toast just above and to the right of the click.
    const margin = 8, gap = 10;
    const point = anchor || { x: innerWidth / 2, y: innerHeight - 40 };
    const w = host.offsetWidth, h = host.offsetHeight;
    let left = point.x + gap, top = point.y - gap - h;
    if (left + w > innerWidth - margin) left = Math.max(margin, point.x - gap - w);
    if (top < margin) top = Math.min(innerHeight - margin - h, point.y + gap);
    left = Math.max(margin, Math.min(left, innerWidth - margin - w));
    top = Math.max(margin, Math.min(top, innerHeight - margin - h));
    host.style.left = left + 'px';
    host.style.top = top + 'px';
    void host.offsetWidth; // restart the transition
    host.classList.add('show');
    clearTimeout(timer);
    timer = setTimeout(() => host.classList.remove('show'), 2600);
  };
})();
