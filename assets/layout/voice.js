// The app's neural voice, shared by 읽어주기 (speech.js) and 해설 모드 (agent.js).
//
// A sentence becomes an MP3 through the app's own `molip` protocol (POST /tts, see src/tts.rs:
// the Edge Read Aloud voices 선히/인준/현수, fetched by the app itself and cached on disk). This
// module keeps an in-page cache of object URLs per (voice, sentence) so the same line is never
// fetched twice, and lets callers prefetch the next sentence while one plays. `name` is the
// voice id from the assistant settings; "system" means the device's own Web Speech voice.
(function () {
  'use strict';
  if (globalThis.molipVoice || typeof document === 'undefined') return;
  let name = 'ko-KR-SunHiNeural';
  const clips = new Map();
  const stats = { fetched: 0, cached: 0, failed: 0, lastEngine: '' };
  function url() {
    // wry serves custom protocols as http://<name>.localhost on Windows (the page itself is on
    // http://dioxus.index.html there), and as <name>://localhost on macOS and Linux.
    return location.protocol === 'http:' || location.protocol === 'https:'
      ? `${location.protocol}//molip.localhost/tts` : 'molip://localhost/tts';
  }
  // Stop repeated requests during a failed playback; retry when playback starts again.
  let unreachable = false;
  const enabled = () => name !== 'system' && typeof fetch === 'function' && !unreachable;
  function giveUp(reason) {
    if (unreachable) return;
    unreachable = true;
    stats.lastEngine = 'unavailable';
    window.dispatchEvent(new CustomEvent('molip:voice-fallback', { detail: reason }));
  }
  // Resolves to an object URL for the clip, or null when the voice is off or unreachable.
  // The sentence is sent as it should be pronounced (assets/speech/pronunciation.js: course terms in
  // Korean, "main.py" as 메인 점 파이, operators as words); the caption keeps the written form.
  const spoken = text => globalThis.molipPronunciation.pronunciationText(text);
  function synthesize(sentence) {
    const text = String(sentence || '').trim();
    if (!enabled() || !text) return Promise.resolve(null);
    const pronounced = spoken(text);
    const key = name + '\n' + pronounced;
    let pending = clips.get(key);
    if (pending) { stats.cached += 1; return pending; }
    // End a stalled request after the native process deadline; the narration shows an error.
    const abort = typeof AbortController === 'function' ? new AbortController() : null;
    const timer = abort ? setTimeout(() => abort.abort(), 25000) : 0;
    pending = fetch(url(), { method: 'POST', headers: { 'Content-Type': 'text/plain' }, body: JSON.stringify({ text: pronounced, voice: name }), signal: abort ? abort.signal : undefined })
      .finally(() => clearTimeout(timer))
      .then(async response => {
        if (!response.ok) { stats.failed += 1; const why = await response.text().catch(() => ''); console.warn('tts', response.status, why); clips.delete(key); giveUp(why || String(response.status)); return null; }
        stats.fetched += 1; stats.lastEngine = response.headers.get('X-Molip-Engine') || '';
        return URL.createObjectURL(await response.blob());
      })
      .catch(error => { stats.failed += 1; clips.delete(key); console.warn('tts', error); giveUp(error && error.name === 'AbortError' ? '응답이 25초 안에 오지 않았어요' : String(error)); return null; });
    clips.set(key, pending);
    return pending;
  }
  function resetFailure() { unreachable = false; }
  function setName(value) { name = String(value || 'system'); unreachable = false; return name; }
  // Reading speed, shared with the 읽어주기 panel (same localStorage key) and announced to every
  // player so a clip already playing changes pace too.
  const RATE_KEY = 'molip:tts-rate';
  const RATES = Object.freeze([0.75, 1, 1.25, 1.5, 1.75, 2]);
  function getRate() {
    try { const value = Number(localStorage.getItem(RATE_KEY)); if (RATES.includes(value)) return value; } catch {}
    return 1.5;
  }
  function setRate(value) {
    const rate = Number(value);
    if (!RATES.includes(rate)) return getRate();
    try { localStorage.setItem(RATE_KEY, String(rate)); } catch {}
    window.dispatchEvent(new CustomEvent('molip:tts-rate', { detail: rate }));
    return rate;
  }
  window.addEventListener('molip:tts-rate', event => {
    for (const select of document.querySelectorAll('select.assistant-rate')) select.value = String(event.detail);
  });
  globalThis.molipVoice = { synthesize, setName, resetFailure, enabled, get name() { return name; }, stats, get rate() { return getRate(); }, setRate, RATES };
})();
