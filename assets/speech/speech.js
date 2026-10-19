// Double-click text-to-speech for the learning screen.
//
// Double-clicking a paragraph (or list item, heading, table cell, quiz option)
// reads aloud from that block to the end of the mission with the device's
// Korean voice. The engine is ported from jhs512/kpc-lec `site/shared/speech-*.mjs`:
// sentence-level chunks so pause/resume is reliable, a Korean pronunciation
// dictionary applied only to the spoken text, and a highlight of the sentence
// being read. Pure helpers are exposed on `window.molipSpeech` for tests.
(function () {
  'use strict';
  if (globalThis.molipSpeech) return;

  // Speech-only rules live in one place, shared with the neural narration voice.
  const { pronunciations, pronunciationText, formatPrices, fileSpeechText, mathSpeechText } = globalThis.molipPronunciation;

  // ---- Sentences and bounded utterances; offsets stay valid for highlighting. ----
  function speechSentences(text) {
    const result = [], push = (start, end) => {
      while (start < end && /\s/.test(text[start])) start++;
      while (end > start && /\s/.test(text[end - 1])) end--;
      if (start < end) result.push({ text: text.slice(start, end), start, end });
    };
    // ICU keeps "다. print는" in one sentence (lowercase continuation), so each
    // segment is split again at a terminator followed by whitespace.
    const terminators = /[.!?。]+["'”’)]*\s+/g;
    const splitAt = (from, to) => {
      let start = from;
      for (const match of text.slice(from, to).matchAll(terminators)) { const end = from + match.index + match[0].length; push(start, end); start = end; }
      push(start, to);
    };
    if (typeof Intl !== 'undefined' && Intl.Segmenter) {
      for (const segment of new Intl.Segmenter('ko', { granularity: 'sentence' }).segment(text)) splitAt(segment.index, segment.index + segment.segment.length);
    } else splitAt(0, text.length);
    return result;
  }
  function splitSpeechRanges(text, limit = 180) {
    const result = [];
    for (const [sentenceIndex, sentence] of speechSentences(text).entries()) {
      let start = sentence.start; const end = sentence.end;
      while (start < end) {
        let stop = Math.min(start + limit, end);
        if (stop < end) { const space = text.lastIndexOf(' ', stop); if (space > start + limit / 2) stop = space; }
        result.push({ text: text.slice(start, stop), start, end: stop, sentenceIndex, sentenceStart: sentence.start, sentenceEnd: end });
        start = stop; while (start < end && /\s/.test(text[start])) start++;
      }
    }
    return result;
  }
  const speechRates = Object.freeze([0.75, 1, 1.25, 1.5, 1.75, 2]);
  function koreanVoice(voices) {
    return voices.filter(v => /^ko(?:[-_]|$)/i.test(v.lang))
      .sort((a, b) => Number(b.localService) - Number(a.localService) || Number(b.default) - Number(a.default))[0];
  }

  class StorySpeech {
    constructor(synth, Utterance, update, timers = globalThis) {
      Object.assign(this, { synth, Utterance, update, timers });
      this.chunks = []; this.state = 'idle'; this.index = 0; this.rate = 1; this.generation = 0;
    }
    emit(message) { this.update({ state: this.state, index: this.index, total: this.chunks.length, message }); }
    cancel() {
      this.generation++; this.timers.clearTimeout(this.timer); this.utterance = null; this.synth.cancel();
      if (this.audio) { try { this.audio.pause(); } catch {} this.audio = null; }
    }
    // The neural voice (assets/layout/voice.js) when it is on; null means Web Speech.
    neural() { const voice = globalThis.molipVoice; return voice && voice.enabled() && typeof Audio === 'function' ? voice : null; }
    start() {
      if (['starting', 'speaking'].includes(this.state)) return;
      this.voice = koreanVoice(this.synth.getVoices());
      if (!this.voice && !this.neural()) { this.state = 'error'; this.emit('한국어 음성을 찾지 못했습니다. 기기 설정에서 한국어 음성을 설치한 뒤 다시 Ctrl+더블 클릭해 주세요.'); return; }
      if (this.state !== 'paused') this.index = 0;
      this.cancel(); this.synth.resume(); this.next();
    }
    next() {
      if (this.index >= this.chunks.length) { this.state = 'ended'; this.emit('모두 읽었습니다.'); return; }
      const token = ++this.generation;
      const neural = this.neural();
      if (neural) { this.playClip(neural, token); return; }
      this.speakNative(token);
    }
    // One sentence as an MP3 clip; the next sentence is fetched meanwhile. Any failure on the
    // way falls back to Web Speech for that sentence, so reading never stalls.
    playClip(neural, token) {
      const valid = () => token === this.generation;
      const fail = () => { if (!valid()) return; this.cancel(); this.state = 'error'; this.emit('음성 재생이 멈췄습니다. 본문을 다시 Ctrl+더블 클릭해 주세요.'); };
      this.state = 'starting'; this.emit('재생 준비 중 · ' + (this.index + 1) + '/' + this.chunks.length);
      this.timer = this.timers.setTimeout(fail, 15000);
      neural.synthesize(this.chunks[this.index]).then(url => {
        if (!valid()) return;
        if (!url) { this.timers.clearTimeout(this.timer); if (this.voice) this.speakNative(token); else fail(); return; }
        const audio = new Audio(url);
        audio.playbackRate = this.rate;
        this.audio = audio;
        audio.onplay = () => {
          if (!valid()) return;
          this.timers.clearTimeout(this.timer);
          this.state = 'speaking'; this.emit('읽는 중 · ' + (this.index + 1) + '/' + this.chunks.length);
          this.timer = this.timers.setTimeout(fail, 90000);
        };
        audio.onended = () => { if (!valid()) return; this.timers.clearTimeout(this.timer); this.audio = null; this.index++; this.next(); };
        audio.onerror = () => { if (!valid()) return; this.timers.clearTimeout(this.timer); if (this.voice) this.speakNative(token); else fail(); };
        audio.play().catch(() => { if (!valid()) return; this.timers.clearTimeout(this.timer); if (this.voice) this.speakNative(token); else fail(); });
        if (this.chunks[this.index + 1]) neural.synthesize(this.chunks[this.index + 1]);
      });
    }
    speakNative(token) {
      const utterance = new this.Utterance(pronunciationText(this.chunks[this.index]));
      this.utterance = utterance; // Keep a strong reference until the utterance finishes.
      utterance.lang = 'ko-KR'; utterance.voice = this.voice; utterance.rate = this.rate;
      const valid = () => token === this.generation;
      const fail = () => { if (!valid()) return; this.cancel(); this.state = 'error'; this.emit('음성 재생이 멈췄습니다. 본문을 다시 Ctrl+더블 클릭해 주세요.'); };
      utterance.onstart = () => {
        if (!valid()) return;
        this.timers.clearTimeout(this.timer);
        this.state = 'speaking'; this.emit('읽는 중 · ' + (this.index + 1) + '/' + this.chunks.length);
        this.timer = this.timers.setTimeout(fail, 60000);
      };
      utterance.onend = () => { if (!valid()) return; this.timers.clearTimeout(this.timer); this.utterance = null; this.index++; this.next(); };
      utterance.onerror = event => { if (event && event.error === 'interrupted' || event && event.error === 'canceled') return; fail(); };
      this.state = 'starting'; this.emit('재생 준비 중 · ' + (this.index + 1) + '/' + this.chunks.length);
      if (!valid()) return;
      this.timer = this.timers.setTimeout(fail, 12000);
      try { this.synth.speak(utterance); } catch { fail(); }
    }
    pause() {
      if (!['starting', 'speaking'].includes(this.state)) return;
      // Sentence-level pause: resuming native speech is unreliable across engines.
      this.cancel(); this.state = 'paused'; this.emit('일시정지 · 이어읽기는 멈춘 문장부터 시작합니다.');
    }
    setRateLive(rate) { if (this.audio) this.audio.playbackRate = rate; }
    stop() { this.cancel(); this.index = 0; this.state = 'idle'; this.emit('정지했습니다.'); }
    setRate(rate) {
      if (!speechRates.includes(rate)) return;
      this.rate = rate;
      this.setRateLive(rate);
      this.emit(['starting', 'speaking'].includes(this.state) ? (this.audio ? '읽기 속도 ' + rate + '배' : '속도는 다음 문장부터 적용됩니다.') : '읽기 속도 ' + rate + '배');
    }
  }

  // ---- DOM text with per-character node offsets, so highlights match exactly. ----
  const BLOCKS = 'p,li,h1,h2,h3,h4,h5,h6,th,td,blockquote,dt,dd,.question-heading';
  const EXCLUDED = 'button,input,select,textarea,svg,script,style,pre,figure,.comic-strip,.cm-editor,.output,.speech-controls,[data-speech-controls],dialog';
  function visible(element) {
    if (!element.isConnected || element.closest('[hidden],[aria-hidden="true"]')) return false;
    for (let node = element; node instanceof Element; node = node.parentElement) {
      const style = getComputedStyle(node);
      if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') return false;
    }
    return element.getClientRects().length > 0;
  }
  function mapSpeechText(element) {
    const raw = [], allowed = new Map();
    if (!visible(element)) return { text: '', points: [] };
    const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT);
    for (let node; (node = walker.nextNode());) {
      const parent = node.parentElement;
      if (!allowed.has(parent)) {
        let blocked = false;
        for (let ancestor = parent; ancestor && ancestor !== element; ancestor = ancestor.parentElement) {
          if (ancestor.matches(EXCLUDED)) { blocked = true; break; }
        }
        allowed.set(parent, !blocked && visible(parent));
      }
      if (!allowed.get(parent)) continue;
      for (let offset = 0; offset < node.data.length; offset++) raw.push({ node, offset, char: node.data[offset] });
    }
    const points = [];
    for (const point of raw) {
      const char = /\s/.test(point.char) ? ' ' : point.char;
      if (char === ' ' && (!points.length || points[points.length - 1].char === ' ')) continue;
      points.push({ node: point.node, offset: point.offset, char });
    }
    while (points.length && /[ ·]/.test(points[points.length - 1].char)) points.pop();
    return { text: points.map(p => p.char).join(''), points };
  }
  // Spoken text differs from display text only inside <code>: wrap it so the
  // pronunciation pass reads identifiers verbatim.
  function speechChunkText(mapping, start, end) {
    let result = '';
    for (let i = start; i < end;) {
      const code = mapping.points[i].node.parentElement.closest('code');
      if (!code) { result += mapping.text[i++]; continue; }
      let stop = i + 1;
      while (stop < end && code.contains(mapping.points[stop].node)) stop++;
      result += '`' + mapping.text.slice(i, stop) + '`'; i = stop;
    }
    return result;
  }
  function speechRanges(mapping, start, end) {
    const ranges = []; let range, previous;
    for (const point of mapping.points.slice(start, end)) {
      if (!range || point.node !== previous.node || point.offset !== previous.offset + 1) {
        range = document.createRange(); range.setStart(point.node, point.offset); ranges.push(range);
      }
      range.setEnd(point.node, point.offset + 1); previous = point;
    }
    return ranges;
  }
  function createHighlight() {
    const native = !!(globalThis.CSS && CSS.highlights && globalThis.Highlight);
    let ranges = [], overlay;
    function clear() { ranges = []; if (native) CSS.highlights.delete('speech-sentence'); if (overlay) overlay.remove(); overlay = undefined; }
    function paint() {
      if (native) return;
      if (overlay) overlay.remove();
      if (!ranges.length) return;
      overlay = document.createElement('div'); overlay.className = 'speech-range-overlay'; overlay.setAttribute('aria-hidden', 'true');
      for (const range of ranges) for (const rect of range.getClientRects()) {
        if (!rect.width || !rect.height) continue;
        const mark = document.createElement('span');
        Object.assign(mark.style, { left: rect.left + 'px', top: rect.top + 'px', width: rect.width + 'px', height: rect.height + 'px' });
        overlay.append(mark);
      }
      document.body.append(overlay);
    }
    addEventListener('scroll', paint, { capture: true, passive: true });
    addEventListener('resize', paint);
    return { show(next) { clear(); ranges = next; if (native) CSS.highlights.set('speech-sentence', new Highlight(...ranges)); else paint(); }, clear };
  }

  // ---- Blocks: innermost readable elements, in document order, within one mission. ----
  function readableBlocks(scope) {
    return [...scope.querySelectorAll(BLOCKS)].filter(node => !node.closest(EXCLUDED) && !node.querySelector(BLOCKS) && visible(node));
  }
  function blockAt(target) {
    if (!(target instanceof Element)) target = target && target.parentElement;
    if (!target || target.closest(EXCLUDED)) return null;
    const block = target.closest(BLOCKS);
    return block && !block.querySelector(BLOCKS) ? block : null;
  }
  function scopeOf(block) { return block.closest('.reading-mission,.lesson,main') || document.body; }

  globalThis.molipSpeech = { pronunciations, pronunciationText, formatPrices, fileSpeechText, mathSpeechText, speechSentences, splitSpeechRanges, koreanVoice, StorySpeech, speechRates };
  if (typeof document === 'undefined') return;

  // ---- Mount: a floating panel, and the double-click that starts reading. ----
  function mount() {
    const rateKey = 'molip:tts-rate';
    let savedRate = globalThis.molipVoice ? globalThis.molipVoice.rate : 1.5;
    try { const value = Number(localStorage.getItem(rateKey)); if (speechRates.includes(value)) savedRate = value; } catch {}
    const panel = document.createElement('section');
    panel.className = 'speech-controls'; panel.dataset.speechControls = ''; panel.hidden = true; panel.setAttribute('aria-label', '텍스트 읽어주기');
    panel.innerHTML = '<div class="speech-buttons"><button type="button" data-action="play" disabled>이어읽기</button><button type="button" data-action="pause" disabled>일시정지</button><button type="button" data-action="stop" disabled>정지</button><label>속도 <select aria-label="읽기 속도">'
      + speechRates.map(rate => '<option value="' + rate + '"' + (rate === savedRate ? ' selected' : '') + '>' + rate + '배</option>').join('')
      + '</select></label><button type="button" class="speech-close" aria-label="읽어주기 닫기 및 정지">닫기 ×</button></div><p class="speech-status" role="status"></p><p class="speech-help">Ctrl(맥은 ⌘)을 누른 채 문단을 더블 클릭하면 거기부터 미션 끝까지 읽습니다. Esc로 정지, 한 번 더 누르면 닫힙니다.</p>';
    document.body.append(panel);
    const status = panel.querySelector('.speech-status');
    const play = panel.querySelector('[data-action="play"]'), pause = panel.querySelector('[data-action="pause"]'), stop = panel.querySelector('[data-action="stop"]');
    const supported = 'speechSynthesis' in window && 'SpeechSynthesisUtterance' in window;
    let hideTimer;
    const flash = message => { panel.hidden = false; panel.dataset.state = 'error'; status.textContent = message; play.disabled = pause.disabled = stop.disabled = true; clearTimeout(hideTimer); hideTimer = setTimeout(() => { panel.hidden = true; }, 6000); };
    if (!supported) {
      document.addEventListener('dblclick', event => { if ((event.ctrlKey || event.metaKey) && blockAt(event.target)) flash('이 기기는 읽어주기를 지원하지 않습니다. 데스크톱 앱에서 해 보세요.'); });
      return;
    }
    const synth = window.speechSynthesis, highlight = createHighlight();
    let chunks = [], active;
    const controller = new StorySpeech(synth, window.SpeechSynthesisUtterance, ({ state, message, index }) => {
      const chunk = chunks[index];
      if (['starting', 'speaking'].includes(state) && chunk) {
        // The mission can re-render or change while reading; never read stale text.
        if (!chunk.node.isConnected || !visible(chunk.node) || mapSpeechText(chunk.node).text !== chunk.mapping.text) { controller.stop(); return; }
        if (active !== chunk.node) { if (active) active.classList.remove('speech-active'); active = chunk.node; }
      }
      if (state === 'speaking' && chunk) highlight.show(speechRanges(chunk.mapping, chunk.sentenceStart, chunk.sentenceEnd));
      else if (state !== 'paused') highlight.clear();
      clearTimeout(hideTimer);
      // A stop asked for with Esc leaves the panel up (a second Esc closes it).
      panel.hidden = !['starting', 'speaking', 'paused', 'error', 'ended'].includes(state) && !(state === 'idle' && stoppedByKey);
      panel.dataset.state = state;
      play.disabled = state !== 'paused'; pause.disabled = !['starting', 'speaking'].includes(state); stop.disabled = !['starting', 'speaking', 'paused'].includes(state);
      status.textContent = message;
      if (active) active.classList.toggle('speech-active', ['starting', 'speaking', 'paused'].includes(state));
      if (state === 'ended') hideTimer = setTimeout(() => { panel.hidden = true; }, 4000);
    });
    controller.rate = savedRate;
    let stoppedByKey = false;
    const dismiss = () => { stoppedByKey = false; controller.stop(); if (active) active.classList.remove('speech-active'); active = null; panel.hidden = true; };
    play.onclick = () => { if (active && active.isConnected && visible(active)) controller.start(); else dismiss(); };
    pause.onclick = () => controller.pause(); stop.onclick = dismiss;
    panel.querySelector('.speech-close').onclick = dismiss;
    panel.querySelector('select').onchange = event => {
      const rate = Number(event.target.value);
      if (!speechRates.includes(rate)) return;
      controller.setRate(rate);
      try { localStorage.setItem(rateKey, String(rate)); } catch {}
      if (globalThis.molipVoice) globalThis.molipVoice.setRate(rate); // the AI panel's speed follows
    };
    // The AI panel's speed control (assets/layout/voice.js) changes this reader too.
    addEventListener('molip:tts-rate', event => {
      const rate = Number(event.detail);
      if (!speechRates.includes(rate) || rate === controller.rate) return;
      controller.setRate(rate);
      panel.querySelector('select').value = String(rate);
    });
    // Esc, anywhere: a first press stops the reading and keeps the panel (it says so), a second
    // press closes the panel. Captured before the slide host sees it, so a presentation stays.
    document.addEventListener('keydown', event => {
      if (event.key !== 'Escape') return;
      if (['starting', 'speaking', 'paused'].includes(controller.state)) {
        event.preventDefault(); event.stopPropagation();
        stoppedByKey = true;
        controller.stop();
        status.textContent = '정지했습니다 · Esc를 한 번 더 누르면 닫힙니다';
      } else if (!panel.hidden) {
        event.preventDefault(); event.stopPropagation();
        dismiss();
      }
    }, true);
    // Ctrl (⌘ on macOS) + double click on a paragraph starts reading there. A plain double click
    // is left to the browser, so selecting a word never starts a voice.
    document.addEventListener('dblclick', event => {
      if (!(event.ctrlKey || event.metaKey)) return;
      const block = blockAt(event.target);
      if (!block) return;
      event.preventDefault();
      stoppedByKey = false;
      startReading(block);
    });
    function startReading(block) {
      const nodes = readableBlocks(scopeOf(block));
      const startIndex = nodes.indexOf(block);
      if (startIndex < 0) return;
      // The browser selected a word on the double click; the sentence highlight replaces it.
      const selection = getSelection(); if (selection) selection.removeAllRanges();
      controller.cancel(); controller.state = 'idle';
      if (active) active.classList.remove('speech-active'); active = null;
      chunks = [];
      for (const node of nodes.slice(startIndex)) {
        const mapping = mapSpeechText(node);
        if (!mapping.text) continue;
        for (const range of splitSpeechRanges(mapping.text)) chunks.push({ ...range, node, mapping, utterance: speechChunkText(mapping, range.start, range.end) });
      }
      if (!chunks.length) return;
      controller.chunks = chunks.map(chunk => chunk.utterance);
      controller.start();
    }
    document.addEventListener('visibilitychange', () => { if (document.hidden) dismiss(); });
    addEventListener('pagehide', dismiss);
    synth.getVoices(); // Warm the voice list; some engines fill it asynchronously.
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount); else mount();
})();
