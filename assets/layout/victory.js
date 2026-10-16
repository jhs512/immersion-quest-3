// Celebration is driven by persisted mission counts, never by animation state.
//
// The reward card carries data-xp-before/after. The XP bar counts up from one to the other;
// when the count crosses a level boundary the card gets the `evolving` class, which swaps the
// current avatar for the next one (CSS keyframes), shows LEVEL UP with the new title, and fires
// a second, golden burst. The header's XP counter is watched too: whenever it grows, "+N XP"
// floats up from it and the small avatar bumps.
(() => {
  if (globalThis.molipVictory) return;
  const seen = new WeakSet();
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const XP_PER_LEVEL = 500;
  // ---- Effect switches (home screen toggles, persisted by src/prefs.rs) and sounds. ----
  // Animations off: no particles, no floating XP, and CSS keyframes are stopped through the
  // fx-still class on <html>. Sounds are synthesized with Web Audio, so nothing is downloaded.
  const fx = { animations: true, sounds: true, lastSound: '' };
  let audio = null;
  function tone(at, freq, duration, type, gain) {
    const osc = audio.createOscillator(), vol = audio.createGain();
    osc.type = type; osc.frequency.setValueAtTime(freq, at);
    vol.gain.setValueAtTime(0.0001, at);
    vol.gain.exponentialRampToValueAtTime(gain, at + 0.012);
    vol.gain.exponentialRampToValueAtTime(0.0001, at + duration);
    osc.connect(vol).connect(audio.destination);
    osc.start(at); osc.stop(at + duration + 0.05);
  }
  function play(kind) {
    fx.lastSound = kind;
    if (!fx.sounds || !('AudioContext' in window)) return;
    try {
      audio = audio || new AudioContext();
      if (audio.state === 'suspended') audio.resume();
      const t = audio.currentTime + 0.01;
      if (kind === 'xp') {            // a two-note coin
        tone(t, 1318.5, 0.09, 'square', 0.06);
        tone(t + 0.09, 1760, 0.22, 'square', 0.06);
      } else if (kind === 'clear') {  // the card opens: a soft rising triad
        [523.25, 659.25, 783.99].forEach((f, i) => tone(t + i * 0.07, f, 0.25, 'triangle', 0.08));
      } else if (kind === 'levelup') { // fanfare: arpeggio up and a held chord
        [523.25, 659.25, 783.99, 1046.5].forEach((f, i) => tone(t + i * 0.11, f, 0.3, 'triangle', 0.1));
        [783.99, 1046.5, 1318.5].forEach(f => tone(t + 0.5, f, 0.9, 'sine', 0.07));
      }
    } catch (error) { console.warn('sound', error); }
  }
  function set(values) {
    if (values && typeof values.animations === 'boolean') fx.animations = values.animations;
    if (values && typeof values.sounds === 'boolean') fx.sounds = values.sounds;
    document.documentElement.classList.toggle('fx-still', !fx.animations);
    return { animations: fx.animations, sounds: fx.sounds };
  }
  // The home toggle decides, not the OS hint: a student who turns animations on wants them
  // even on a machine whose system setting asks for reduced motion.
  const still = () => !fx.animations;
  globalThis.molipFx = { set, play, get animations() { return fx.animations; }, get sounds() { return fx.sounds; }, get lastSound() { return fx.lastSound; } };
  function burst(particles, x, y, colors, count, delay, speedMin, speedMax) {
    for (let i = 0; i < count; i++) {
      const angle = Math.PI * 2 * i / count + Math.random() * .2;
      const speed = speedMin + Math.random() * (speedMax - speedMin);
      particles.push({ x, y, vx: Math.cos(angle) * speed, vy: Math.sin(angle) * speed,
        delay, color: colors[i % colors.length], size: 1.5 + Math.random() * 2.5 });
    }
  }
  function celebrate(card) {
    if (seen.has(card)) return;
    seen.add(card);
    const before = Number(card.dataset.xpBefore), after = Number(card.dataset.xpAfter);
    const fill = card.querySelector('.victory-fill');
    const total = card.querySelector('.victory-total');
    const level = card.querySelector('.victory-level');
    const stage = card.querySelector('.victory-avatar-stage');
    const levelsUp = after > before && Math.floor(after / XP_PER_LEVEL) > Math.floor(before / XP_PER_LEVEL);
    // The moment (0..1 of the count-up) at which the bar reaches the next level.
    const boundary = levelsUp ? ((Math.floor(before / XP_PER_LEVEL) + 1) * XP_PER_LEVEL - before) / (after - before) : 2;
    const start = performance.now();
    let frame, canvas, ctx, evolved = false;
    const particles = [];
    play(after > before ? 'clear' : 'xp');
    if (!still()) {
      canvas = document.createElement('canvas');
      canvas.className = 'victory-fireworks';
      canvas.setAttribute('aria-hidden', 'true');
      (document.fullscreenElement || document.body).append(canvas);
      const dpr = Math.min(devicePixelRatio || 1, 2);
      canvas.width = innerWidth * dpr; canvas.height = innerHeight * dpr;
      ctx = canvas.getContext('2d'); ctx.scale(dpr, dpr);
      const colors = ['#ffdc84', '#67e8e0', '#c7a5ff', '#ffffff', '#ffa8ba'];
      for (let b = 0; b < 5; b++) {
        burst(particles, innerWidth * [.2, .8, .5, .12, .88][b], innerHeight * [.35, .35, .18, .65, .65][b], colors, 48, b * 170, 70, 240);
      }
    }
    function evolve(now) {
      evolved = true;
      card.classList.add('evolving');
      play('levelup');
      const nextLevel = Number(stage?.dataset.levelAfter || Math.floor(after / XP_PER_LEVEL) + 1);
      const banner = card.querySelector('.victory-levelup');
      if (banner) banner.textContent = `LEVEL UP · Lv. ${nextLevel}`;
      const title = card.querySelector('.victory-title');
      if (title && stage?.dataset.titleAfter) title.textContent = `새 칭호 · ${stage.dataset.titleAfter}`;
      const note = card.querySelector('.victory-level-note');
      if (note) note.textContent = `LEVEL UP! ${stage?.dataset.titleAfter ? stage.dataset.titleAfter + '로 자랐어요.' : '새로운 레벨에 도달했어요.'}`;
      card.classList.add('leveled-up');
      if (ctx && stage) {
        const r = stage.getBoundingClientRect();
        const x = r.left + r.width / 2, y = r.top + r.height / 2;
        const gold = ['#ffe0a0', '#f2c94c', '#ffffff', '#ffd27a'];
        burst(particles, x, y, gold, 72, now - start + 450, 120, 420);
        burst(particles, x, y, gold, 36, now - start + 700, 60, 200);
      }
    }
    function update(now) {
      if (!card.isConnected) { canvas?.remove(); cancelAnimationFrame(frame); return; }
      const elapsed = now - start;
      const t = still() ? 1 : Math.min(1, elapsed / 1500);
      const ease = 1 - Math.pow(1 - t, 3);
      const xp = Math.round(before + (after - before) * ease);
      total.textContent = `${xp.toLocaleString()} XP`;
      level.textContent = `Lv. ${Math.floor(xp / XP_PER_LEVEL) + 1}`;
      fill.style.width = `${(xp % XP_PER_LEVEL) / 5}%`;
      if (!evolved && ease >= boundary) evolve(now);
      if (ctx) {
        ctx.clearRect(0, 0, innerWidth, innerHeight);
        for (const p of particles) {
          const age = (elapsed - p.delay) / 1000;
          if (age < 0 || age > 1.65) continue;
          ctx.globalAlpha = Math.pow(1 - age / 1.65, 1.4);
          ctx.strokeStyle = p.color; ctx.fillStyle = p.color;
          ctx.shadowBlur = 12; ctx.shadowColor = p.color;
          const x = p.x + p.vx * age, y = p.y + p.vy * age + 80 * age * age;
          ctx.lineWidth = p.size;
          ctx.beginPath(); ctx.moveTo(x - p.vx * .025, y - p.vy * .025); ctx.lineTo(x, y); ctx.stroke();
        }
        ctx.globalAlpha = 1;
      }
      const span = levelsUp ? 4200 : 2600;
      if (elapsed < span && !still()) frame = requestAnimationFrame(update);
      else { canvas?.remove(); card.dataset.celebrated = 'true'; }
    }
    frame = requestAnimationFrame(update);
  }
  // Header XP: float the gain and bump the avatar whenever the persisted total grows.
  let knownXp = null;
  function watchHeader() {
    const counter = document.querySelector('.learning-xp');
    if (!counter) { knownXp = null; return; }
    const xp = Number((counter.textContent.match(/([\d,]+)\s*XP/) || [])[1]?.replace(/,/g, ''));
    if (!Number.isFinite(xp)) return;
    if (knownXp !== null && xp > knownXp) {
      // Every kind of mission lands here when its completion is stored: a cleared problem, a
      // passed quiz or check question, a deck read to the end. The card (coding, quiz) plays
      // its own sound; the quiet completions (decks) get the chime from here.
      const gain = xp - knownXp;
      if (!document.querySelector('.victory-panel')) play('xp');
      if (!still()) {
        const r = counter.getBoundingClientRect();
        const chip = document.createElement('div');
        chip.className = 'xp-float';
        chip.textContent = `+${gain} XP`;
        chip.style.left = `${r.left}px`; chip.style.top = `${r.top - 6}px`;
        document.body.append(chip);
        setTimeout(() => chip.remove(), 1500);
        const avatar = document.querySelector('.learning-avatar');
        if (avatar) { avatar.classList.remove('xp-bump'); void avatar.offsetWidth; avatar.classList.add('xp-bump'); }
      }
      // A quiet completion can also cross a level: say so, with the fanfare.
      if (!document.querySelector('.victory-panel') && Math.floor(xp / XP_PER_LEVEL) > Math.floor(knownXp / XP_PER_LEVEL)) {
        play('levelup');
        const title = document.querySelector('.learning-avatar')?.getAttribute('title');
        globalThis.molipToast?.(`LEVEL UP! Lv. ${Math.floor(xp / XP_PER_LEVEL) + 1}${title ? ' · ' + title : ''}`, 'success');
      } else {
        globalThis.molipToast?.(`+${gain} XP`, 'success');
      }
    }
    knownXp = xp;
  }
  function scan() { document.querySelectorAll('.victory-panel').forEach(celebrate); watchHeader(); }
  new MutationObserver(scan).observe(document.body, { childList: true, subtree: true, characterData: true });
  globalThis.molipVictory = { scan }; scan();
})();
