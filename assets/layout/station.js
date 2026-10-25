// Step strip marker: one ink bar under the current station that slides to the next one
// (160ms in CSS; instant under reduced motion). It follows window resizes.
(() => {
  if (window.mqStationMarker) return;
  const place = (nav) => {
    nav = nav || document.querySelector('.study-navigation');
    const current = nav && nav.querySelector('.selected');
    if (!current) return;
    const label = current.getBoundingClientRect(), strip = nav.getBoundingClientRect();
    const dot = current.querySelector('.step-dot');
    const start = (dot ? dot.getBoundingClientRect().right + 6 : label.left) - strip.left + nav.scrollLeft;
    const end = label.right - strip.left + nav.scrollLeft - (current.nextElementSibling ? 30 : 10);
    nav.style.setProperty('--marker-x', `${Math.round(start)}px`);
    nav.style.setProperty('--marker-w', `${Math.max(0, Math.round(end - start))}px`);
    nav.dataset.marker = 'on';
  };
  window.mqStationMarker = place;
  window.addEventListener('resize', () => place());
})();
