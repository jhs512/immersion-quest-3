// Screen theme in the page. The stored choice (시스템 / 밝게 / 어둡게) lives in prefs.json and is
// written onto <html data-theme-choice> by the page head before the first paint; styles derive
// the look from it, and 시스템 follows prefers-color-scheme through CSS alone. This script only
// mirrors the effective look onto <html data-theme> (for scripts and checks) and keeps it current
// when the OS setting changes or the learner picks another choice.
(() => {
  const valid = value => (value === 'light' || value === 'dark' || value === 'system') ? value : 'system';
  if (window.mqTheme) { window.mqTheme.adopt(); return; }
  const media = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null;
  let choice = 'system';
  const effective = () => choice === 'system' ? (media && media.matches ? 'dark' : 'light') : choice;
  const apply = () => {
    const root = document.documentElement;
    root.dataset.themeChoice = choice;
    const look = effective();
    if (root.dataset.theme !== look) {
      root.dataset.theme = look;
      document.dispatchEvent(new CustomEvent('mq-theme', {detail: {choice, effective: look}}));
    }
  };
  const follow = () => { if (choice === 'system') apply(); };
  if (media) {
    if (media.addEventListener) media.addEventListener('change', follow);
    else if (media.addListener) media.addListener(follow);
  }
  window.mqTheme = {
    set(next) { choice = valid(next); apply(); return effective(); },
    // Take the choice the page head wrote (or 시스템 when there is none or it is unknown).
    adopt() { choice = valid(document.documentElement.dataset.themeChoice); apply(); return effective(); },
    choice: () => choice,
    effective,
  };
  window.mqTheme.adopt();
})();
