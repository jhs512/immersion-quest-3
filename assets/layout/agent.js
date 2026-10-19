// Lets the tutor chat act on the screen, and explain while it does.
//
// The assistant may end an answer with a ```molip-actions fence holding a JSON array such as
// [{"action":"set_code","code":"..."},{"action":"submit"}]. The Rust side hands that array to
// window.molipAgent.run, which drives the same buttons and inputs the student uses, waits for
// each run or submission to finish, and returns a text report that goes back to the assistant.
//
// 해설 모드: any action may carry "say". The agent then puts a purple spotlight on the part of the
// screen it is about to touch, shows the sentence in a caption there and reads it aloud (Web
// Speech, Korean voice, the reading speed the 읽어주기 panel saved), and only then acts.
// `say` {target, text} is narration alone; `type_code` {code, say, replace} types code into the
// editor a few characters at a time while the explanation is spoken. A target of the form
// "text:<구절>" is the block of the mission text that contains that phrase (a paragraph, a
// code block, a comic): the page glides there slowly before the sentence is read, so an
// explanation of something below the fold is seen, not just heard. The voice comes from
// assets/layout/voice.js (neural clips), or Web Speech when explicitly selected. molipAgent.stop() ends a
// narration (the sidebar's 멈춤 button), molipAgent.setVoice(false) keeps the captions but mutes.
(function () {
  'use strict';
  if (globalThis.molipAgent || typeof document === 'undefined') return;
  const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
  const byText = (selector, text) => [...document.querySelectorAll(selector)].find(b => b.textContent.trim() === text);
  // Wait for a run or a grading to finish: the button comes back, or the reward card is up (a
  // passed quiz keeps its 제출 button disabled, so the card is the signal there).
  async function waitIdle(button, limit = 180000, previousExecution = null, active = () => !cancelled) {
    const started = Date.now();
    const pane = document.querySelector('.result-pane');
    if (previousExecution === null) await sleep(40);
    // Execution and history synchronization are separate operations. A run id also
    // catches quick programs that finish between two render frames.
    while (active() && button.isConnected && Date.now() - started < limit) {
      if (previousExecution !== null && pane?.dataset.executionId !== previousExecution
          && ['finished','failed'].includes(pane?.dataset.executionState)) return;
      if (previousExecution === null && (!button.disabled || cleared())) return;
      await sleep(40);
    }
    if (active() && button.isConnected && Date.now() - started >= limit)
      throw new Error('실행이 끝나지 않았어요. 실행 상태를 확인하세요.');
  }

  const text = (selector, max = 3000) => [...document.querySelectorAll(selector)].map(e => e.textContent.trim()).filter(Boolean).join('\n').slice(0, max);
  function workspaceReport() {
    return [text('.result-pane .execution-status'), text('.result-pane .output')].filter(Boolean).join('\n');
  }
  // The reward card (다음 미션 / 여기 머물기) is left to the student or to /auto-all; its presence
  // is how a pass is recognised. A `next` action takes its 다음 미션 button.
  const popupButton = text => [...document.querySelectorAll('.doctor-panel button')].find(b => b.textContent.trim() === text) || null;
  const cleared = () => !!document.querySelector('.victory-panel');

  // ---- Spotlight: a purple frame over the element being talked about, with the sentence. ----
  const TARGETS = {
    problem: ['.problem-pane h3', '.problem-pane', '.reading-mission'],
    examples: ['.problem-pane details', '.problem-pane .examples', '.problem-pane table', '.problem-pane'],
    editor: ['.cm-editor', '.editor-pane', 'textarea.code-editor'],
    blanks: ['.code-blanks', 'input.code-blank', '.editor-pane'],
    input: ['.result-pane textarea', '.result-pane details', '.result-pane'],
    output: ['.result-pane .output', '.result-pane'],
    memory: ['.narration-memory'],
    run: [() => byText('.pane-actions button', '코드 실행'), '.pane-actions'],
    submit: [() => byText('.pane-actions button', '제출'), '.pane-actions'],
    hint: ['.problem-pane details', '.hint', '.problem-pane'],
    prompt: ['.prompt-buttons', '.problem-pane'],
    quiz: ['.quiz-question', '.reading-mission'],
    quiz_submit: ['.quiz-actions .primary', '.quiz-actions'],
    nav: ['.header-navigation'],
    missions: ['.mission-cell.current', '.mission-cell'],
    slides: ['.slides-stage', '.slides-host'],
    xp: ['.learning-xp'],
    title: ['.reading-mission h2', '.problem-pane h2', '.slides-mission h2'],
  };
  const normalize = value => String(value || '').replace(/[`*]/g, '').replace(/\s+/g, ' ').trim();
  // The question numbered N (data-question, set by the Rust side), or the N-th on screen.
  function question(n) {
    return document.querySelector(`.quiz-question[data-question="${n}"]`)
      || document.querySelectorAll('.quiz-question')[Number(n) - 1] || null;
  }
  // The smallest block of the mission text that contains the phrase: a paragraph, list item,
  // heading, table, code block or rendered figure (comics keep their title as SVG text).
  function textBlock(phrase) {
    const wanted = normalize(phrase);
    if (!wanted) return null;
    const roots = [...document.querySelectorAll('.reading-mission .markdown, .problem-pane .markdown, .quiz-question')];
    for (const root of roots) {
      for (const block of root.children) {
        if (!normalize(block.textContent).includes(wanted)) continue;
        // A list or table: narrow to the item/row when one holds the whole phrase.
        const inner = [...block.querySelectorAll('li, tr, p')].find(e => normalize(e.textContent).includes(wanted));
        return inner && inner.getBoundingClientRect().height > 0 ? inner : block;
      }
    }
    const fallback = [...document.querySelectorAll('.reading-mission, .problem-pane')].find(e => normalize(e.textContent).includes(wanted));
    return fallback || null;
  }
  function resolveTarget(target) {
    if (!target) return null;
    const key = String(target).trim();
    if (key.startsWith('answer:')) return document.querySelector(`[data-option-id="${CSS.escape(key.slice(7))}"]`);
    const lines = key.match(/^(?:lines|editor):(\d+)(?::(\d+))?$/);
    if (lines) globalThis.molipCodeEditors?.highlightLines(Number(lines[1]), Number(lines[2] || lines[1]));
    if (key === 'editor' || lines) {
      const marked = [...document.querySelectorAll('.cm-narration-line')];
      if (marked.length) return {
        get isConnected() { return marked[0].isConnected; },
        parentElement: marked[0].parentElement,
        getBoundingClientRect() {
          const first = marked[0].getBoundingClientRect(), last = marked.at(-1).getBoundingClientRect();
          return {left: first.left, right: first.right, top: first.top, bottom: last.bottom,
            width: first.width, height: last.bottom - first.top};
        },
      };
    }
    // "quiz:2" is the second question; "option:2:3" its third choice.
    if (key.startsWith('text:')) return textBlock(key.slice(5));
    let m = key.match(/^quiz[:\s]+(\d+)$/);
    if (m) return question(m[1]);
    m = key.match(/^option[:\s]+(\d+)[:\s]+(\d+)$/);
    if (m) {
      const section = question(m[1]);
      return (section && section.querySelectorAll('.quiz-option')[Number(m[2]) - 1]) || section || null;
    }
    const candidates = TARGETS[key];
    if (candidates) {
      for (const candidate of candidates) {
        const element = typeof candidate === 'function' ? candidate() : document.querySelector(candidate);
        if (element) return element;
      }
      return null;
    }
    try { return document.querySelector(key); } catch { return null; }
  }
  let spot, caption, spotTarget = null, spotKey = null, raf = 0;
  // Options the narration has talked about keep a mark until the run ends.
  function mark(element) {
    const option = element && element.closest && element.closest('.quiz-option');
    if (option) option.classList.add('agent-said');
  }
  function clearMarks() { for (const e of document.querySelectorAll('.agent-said')) e.classList.remove('agent-said'); }
  function ensureSpot() {
    if (spot) return;
    spot = document.createElement('div'); spot.className = 'agent-spotlight'; spot.hidden = true; spot.setAttribute('aria-hidden', 'true');
    caption = document.createElement('div'); caption.className = 'agent-caption'; caption.hidden = true; caption.setAttribute('role', 'status'); caption.setAttribute('aria-live', 'polite');
    document.body.append(spot, caption);
  }
  function place() {
    const margin = 8;
    // The UI re-renders after a tick or a grade: find the same target again by its key.
    if (spotTarget && !spotTarget.isConnected && spotKey) { spotTarget = resolveTarget(spotKey); mark(spotTarget); }
    if (spotTarget && spotTarget.isConnected) {
      const r = spotTarget.getBoundingClientRect();
      const pad = 6;
      spot.style.left = `${r.left - pad}px`; spot.style.top = `${r.top - pad}px`;
      spot.style.width = `${r.width + pad * 2}px`; spot.style.height = `${r.height + pad * 2}px`;
      spot.hidden = false;
      if (!caption.hidden) {
        const w = caption.offsetWidth, h = caption.offsetHeight;
        let left = r.left + r.width / 2 - w / 2;
        left = Math.max(margin, Math.min(left, innerWidth - margin - w));
        let top = r.bottom + pad + 12;
        if (top + h > innerHeight - margin) top = r.top - pad - 12 - h;
        if (top < margin) top = Math.min(innerHeight - margin - h, r.top + 12);
        caption.style.left = `${left}px`; caption.style.top = `${top}px`;
      }
    } else {
      spot.hidden = true;
      if (!caption.hidden) {
        caption.style.left = `${Math.max(margin, innerWidth / 2 - caption.offsetWidth / 2)}px`;
        caption.style.top = `${innerHeight - margin - caption.offsetHeight - 24}px`;
      }
    }
    raf = requestAnimationFrame(place);
  }
  // ---- Glide: bring the element into view slowly, the way a presenter scrolls while talking. ----
  const scrollParent = element => {
    for (let node = element.parentElement; node; node = node.parentElement) {
      const style = getComputedStyle(node);
      if (/(auto|scroll)/.test(style.overflowY) && node.scrollHeight > node.clientHeight + 1) return node;
    }
    return document.scrollingElement || document.documentElement;
  };
  const ease = t => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
  let glideFrame = 0;
  function glideTo(element) {
    cancelAnimationFrame(glideFrame);
    const container = scrollParent(element);
    const viewport = container === document.scrollingElement || container === document.documentElement;
    const box = viewport ? { top: 0, height: innerHeight } : container.getBoundingClientRect();
    const r = element.getBoundingClientRect();
    const margin = 24;
    // Already fully on screen: leave the page where it is.
    if (r.top >= box.top + margin && r.bottom <= box.top + box.height - margin) return 0;
    // Centre the block; a block taller than the view lands with its top near the top.
    const offset = r.height > box.height * 0.6 ? margin + 12 : (box.height - r.height) / 2;
    const target = Math.max(0, Math.min(container.scrollTop + (r.top - box.top) - offset, container.scrollHeight - container.clientHeight));
    const start = container.scrollTop, distance = target - start;
    if (Math.abs(distance) < 2) return 0;
    const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
    const duration = reduced ? 0 : Math.min(1600, Math.max(600, 450 + Math.abs(distance) * 0.7));
    const began = performance.now();
    const step = now => {
      const t = duration ? Math.min(1, (now - began) / duration) : 1;
      container.scrollTop = start + distance * ease(t);
      if (t < 1) glideFrame = requestAnimationFrame(step);
    };
    glideFrame = requestAnimationFrame(step);
    return duration;
  }
  // Authored speech uses pronunciations such as 십이. Captions use the numerical
  // values in this task and demonstration, without changing what the voice reads.
  let captionSource = '';
  function captionText(sentence) {
    const display = value => globalThis.molipSpeech?.formatPrices(value) ?? String(value);
    const source = (document.querySelector('.repository-task')?.textContent || '') + '\n' + captionSource;
    const digits = ['', '일', '이', '삼', '사', '오', '육', '칠', '팔', '구'];
    const group = value => {
      let result = '';
      for (const [unit, word] of [[1000,'천'],[100,'백'],[10,'십'],[1,'']]) {
        const digit = Math.floor(value / unit); value %= unit;
        if (digit) result += (digit === 1 && unit > 1 ? '' : digits[digit]) + word;
      }
      return result;
    };
    const numbers = new Map();
    for (const match of source.matchAll(/\b\d{1,3}(?:,\d{3})+\b|\b\d{2,8}\b/g)) {
      const value = Number(match[0].replaceAll(',', ''));
      if (value < 10) continue;
      const high = Math.floor(value / 10000), low = value % 10000;
      const word = (high ? (high === 1 ? '' : group(high)) + '만' : '') + group(low);
      numbers.set(word, String(value));
    }
    if (!numbers.size) return display(sentence || '');
    const words = [...numbers.keys()].sort((a,b)=>b.length-a.length).join('|');
    // A suffix check keeps ordinary words such as 백업 and 만약 intact.
    const pattern = new RegExp('(^|[^가-힣])(' + words + ')(?=$|[\\s,.!?…]|은|는|이|가|을|를|의|에|예|와|과|로|도|만|번|개|명|건|점|초|분|시|줄|배|원|퍼센트|%)', 'g');
    return display(String(sentence || '').replace(pattern, (whole, prefix, word, index, text) => {
      const base = word.slice(0,-1);
      if (word.endsWith('이') && text.slice(index + whole.length).startsWith('에요') && numbers.has(base)) return prefix + numbers.get(base) + '이';
      return prefix + numbers.get(word);
    }));
  }
  function spotlight(target, sentence) {
    ensureSpot();
    const element = resolveTarget(target);
    spotTarget = element || null;
    spotKey = element ? String(target) : null;
    if (element) {
      mark(element);
      try { glideTo(element); } catch {}
    }
    document.querySelectorAll('.overview-speaking').forEach(node=>node.classList.remove('overview-speaking'));
    if(spotTarget?.closest?.('#lesson-info-dialog')) {
      spotTarget.classList.add('overview-speaking');
      spot.hidden=true;caption.hidden=true;cancelAnimationFrame(raf);raf=0;
      const status=document.querySelector('#lesson-overview-status');if(status)status.textContent=sentence||'';
      return;
    }
    caption.textContent = captionText(sentence);
    caption.hidden = !sentence;
    cancelAnimationFrame(raf);
    place();
  }
  function clearSpot() {
    cancelAnimationFrame(raf); raf = 0;
    document.querySelectorAll('.overview-speaking').forEach(node=>node.classList.remove('overview-speaking'));
    spotTarget = null; spotKey = null;
    clearMarks();
    globalThis.molipCodeEditors?.highlightLines(null);
    if (spot) { spot.hidden = true; caption.hidden = true; }
    document.querySelector('.narration-memory')?.remove();
  }

  function showMemory(diagram) {
    if (!diagram || !Array.isArray(diagram.rows)) return;
    const host = document.querySelector('.problem-pane');
    if (!host) throw new Error('메모리 그림을 표시할 문제 패널이 없어요.');
    let panel = host.querySelector('.narration-memory');
    if (!panel) {
      panel = document.createElement('figure');
      panel.className = 'narration-memory';
      panel.setAttribute('aria-label', '해설 메모리 그림');
      host.prepend(panel);
    }
    panel.replaceChildren();
    const title = document.createElement('figcaption');
    title.textContent = String(diagram.title || '변수와 연결');
    panel.append(title);
    for (const row of diagram.rows) {
      const line = document.createElement('div');
      line.className = 'narration-memory-row';
      for (const [i, cell] of String(row).split('→').entries()) {
        if (i) { const arrow = document.createElement('span'); arrow.textContent = '→'; arrow.className = 'narration-memory-arrow'; line.append(arrow); }
        const box = document.createElement('span'); box.className = 'narration-memory-cell'; box.textContent = cell.trim(); line.append(box);
      }
      panel.append(line);
    }
  }

  // ---- Voice: one sentence at a time, resolved when it has been read (or would have been). ----
  let voice = true, cancelled = false;
  let forcedVoiceRun = 0;
  const voiceOn = () => voice || (forcedVoiceRun !== 0 && forcedVoiceRun === narrationRun);
  // Pause (the panel's ⏸, the Space key): the clip or utterance playing is held, typing stops,
  // and the next action waits; resume picks up exactly there. The spotlight stays where it is.
  let paused = false, running = false;
  async function waitWhilePaused() { while (paused && !cancelled) await sleep(100); }
  function pause() {
    if (!running || paused) return paused;
    paused = true;
    if (currentAudio) { try { currentAudio.pause(); } catch {} }
    if ('speechSynthesis' in window) { try { window.speechSynthesis.pause(); } catch {} }
    return paused;
  }
  function resume() {
    if (!paused) return paused;
    paused = false;
    if (currentAudio) { currentAudio.play().catch(() => {}); }
    if ('speechSynthesis' in window) { try { window.speechSynthesis.resume(); } catch {} }
    return paused;
  }
  // ---- Neural voice: clips come from assets/layout/voice.js (the app's /tts endpoint). ----
  let currentAudio = null, finishClip = null;
  const neural = () => (globalThis.molipVoice && globalThis.molipVoice.enabled()) ? globalThis.molipVoice : null;
  // 멈춤 while a clip is being fetched: the fetch keeps going (it fills the cache), but the
  // narration stops waiting for it. Each waiter is released by stop().
  let cancelWaiters = [];
  const untilCancelled = () => new Promise(resolve => cancelWaiters.push(resolve));
  function releaseCancelWaiters() { const waiters = cancelWaiters; cancelWaiters = []; for (const resolve of waiters) resolve(null); }
  function synthesize(sentence) {
    const v = neural();
    if (!v) return Promise.resolve(null);
    if (cancelled) return Promise.resolve(null);
    return Promise.race([v.synthesize(sentence), untilCancelled()]);
  }
  function playClip(url) {
    return new Promise(resolve => {
      const audio = new Audio(url);
      audio.playbackRate = globalThis.molipVoice ? globalThis.molipVoice.rate : 1;
      let done = false;
      const finish = ok => { if (done) return; done = true; if (currentAudio === audio) { currentAudio = null; finishClip = null; } resolve(ok); };
      audio.onended = () => finish(true);
      audio.onerror = () => finish(false);
      currentAudio = audio; finishClip = finish;
      audio.play().then(() => { if (cancelled) { audio.pause(); finish(true); } }).catch(() => finish(false));
    });
  }
  // A paused clip never fires `ended`: stopping must settle its promise, or the narration that
  // awaits it (and the panel's 진행 중 state behind it) would hang after 멈춤.
  function stopClip() {
    const finish = finishClip;
    if (currentAudio) { try { currentAudio.pause(); } catch {} currentAudio = null; }
    finishClip = null;
    if (finish) finish(false);
  }
  window.addEventListener('molip:tts-rate', event => { if (currentAudio) currentAudio.playbackRate = event.detail; });
  async function prefetch(actions, active) {
    if (!voiceOn() || !neural()) return;
    const sentences = [...new Set(actions.map(a => a && (a.action === 'say' ? a.text : a.say)).filter(Boolean).map(String))];
    if (!sentences.length) return;
    let next = 0, ready = 0;
    const progress = () => { if (active()) spotlight(null, `해설 음성을 준비해요. ${ready} / ${sentences.length}`); };
    progress();
    // Cache the entire problem before moving the screen. Limit simultaneous TTS requests.
    await Promise.all(Array.from({length: Math.min(3, sentences.length)}, async () => {
      while (active() && neural() && next < sentences.length) {
        await synthesize(sentences[next++]);
        ready++;
        progress();
      }
    }));
  }
  // Chromium drops onend for an utterance that gets garbage-collected, and ignores speak() in the
  // same tick as cancel(): keep the utterance referenced, and only cancel when something plays.
  let current = null;
  async function speak(sentence) {
    if (!sentence) return;
    if (voiceOn() && globalThis.molipVoice && molipVoice.name !== 'system' && !cancelled) {
      const url = await synthesize(String(sentence));
      if (cancelled) return;
      if (url && await playClip(url)) { lastSpeech = 'neural'; return; }
      lastSpeech = 'unavailable';
      throw new Error('Edge 음성을 재생하지 못했어요. 연결을 확인한 뒤 다시 재생해 주세요.');
    }
    lastSpeech = 'system';
    return speakWithSystemVoice(sentence);
  }
  let lastSpeech = '';
  // Told once per session: the neural voice gave up, or this device has no Korean voice.
  let toldFallback = false, toldNoKorean = false;
  window.addEventListener('molip:voice-fallback', event => {
    if (toldFallback) return;
    toldFallback = true;
    const reason = String(event.detail || '').slice(0, 80);
    if (globalThis.molipToast) molipToast('Edge 음성을 준비하지 못했어요. 연결을 확인한 뒤 다시 재생해 주세요. (' + reason + ')', 'warn');
  });
  function speakWithSystemVoice(sentence) {
    const length = String(sentence).length;
    if (!voiceOn() || !('speechSynthesis' in window) || !('SpeechSynthesisUtterance' in window)) {
      return sleep(Math.min(5000, 700 + length * 55)); // reading time, so the caption can be read
    }
    return new Promise(resolve => {
      const helpers = globalThis.molipSpeech;
      const synth = window.speechSynthesis;
      let done = false, timer = 0;
      const finish = () => { if (done) return; done = true; clearTimeout(timer); current = null; resolve(); };
      const start = () => {
        if (cancelled || !voice) { finish(); return; }
        const utterance = new SpeechSynthesisUtterance(globalThis.molipPronunciation.pronunciationText(sentence));
        utterance.lang = 'ko-KR';
        const korean = helpers && helpers.koreanVoice ? helpers.koreanVoice(synth.getVoices()) : null;
        if (korean) utterance.voice = korean;
        else if (!toldNoKorean && synth.getVoices().length) {
          toldNoKorean = true;
          if (globalThis.molipToast) molipToast('이 컴퓨터에 한국어 음성이 없어 자막으로만 보여 줘요. Windows 설정 → 시간 및 언어 → 언어 및 지역에서 한국어 음성 팩을 추가하면 소리가 나요.', 'warn');
        }
        let rate = globalThis.molipVoice ? globalThis.molipVoice.rate : 1.5;
        try { const saved = Number(localStorage.getItem('molip:tts-rate')); if (saved >= 0.5 && saved <= 2) rate = saved; } catch {}
        utterance.rate = rate;
        timer = setTimeout(finish, 3000 + length * 170 / rate);
        utterance.onend = finish; utterance.onerror = finish;
        current = utterance;
        try { synth.resume(); synth.speak(utterance); } catch { finish(); }
      };
      if (synth.speaking || synth.pending) { synth.cancel(); setTimeout(start, 150); } else start();
    });
  }
  function stopSpeech() { current = null; stopClip(); if ('speechSynthesis' in window) try { window.speechSynthesis.cancel(); } catch {} }

  async function typeCode(code, replace, active = () => !cancelled) {
    const api = window.molipCodeEditors;
    if (!api || !api.appendValue || !api.getValue) throw new Error('코드 편집기를 찾지 못했습니다');
    const current = api.getValue();
    if (current === null) throw new Error('이 미션에는 코드 편집기가 없습니다 (코딩 미션에서만 됩니다)');
    let body = String(code ?? '');
    if (!body.endsWith('\n')) body += '\n';
    if (!replace && current && !current.endsWith('\n')) body = '\n' + body;
    await animateEdit(replace ? 0 : current.length, current.length, body, active);
    return body.split('\n').filter(line => line.trim()).length;
  }

  const lineAt = (code, offset) => code.slice(0, offset).split('\n').length;
  const lastCodeLine = source => Math.max(1, source.trimEnd().split('\n').length);
  function focusCode(action, next) {
    const api = globalThis.molipCodeEditors;
    if (!api?.highlightLines) return;
    if (Array.isArray(action.lines)) { api.highlightLines(...action.lines); return; }
    const source = api.getValue() || '';
    if (action.action === 'run') { const line=lastCodeLine(source); api.highlightLines(line,line,true); return; }
    if (action.target === 'output') return;
    const edit = action.action === 'patch_code' ? action : next?.action === 'patch_code' ? next : null;
    if (edit && edit.before) {
      const from = source.indexOf(edit.before);
      if (from >= 0) { api.highlightLines(lineAt(source, from), lineAt(source, from + edit.before.length - 1)); return; }
    }
    if (action.action === 'set_code') {
      const desired = String(action.code ?? '');
      let from = 0;
      while (from < source.length && from < desired.length && source[from] === desired[from]) from++;
      api.highlightLines(source === desired ? lastCodeLine(source) : lineAt(source, from));
    } else if (action.action === 'type_code') api.highlightLines(source.split('\n').length);
    else if (action.target === 'editor') {
      if (!document.querySelector('.cm-narration-line')) api.highlightLines(1);
    } else if (!String(action.target || '').startsWith('lines:') && !String(action.target || '').startsWith('editor:')) api.highlightLines(null);
  }
  // Retain unchanged code and type only the changed fragment, including replacements in place.
  async function animateEdit(from, to, insert, active = () => !cancelled) {
    const api = globalThis.molipCodeEditors;
    const source = api.getValue();
    const element = document.querySelector('textarea[data-code-editor]');
    let expected = source;
    const ensureUnchanged = () => {
      if (api.getValue() !== expected || (element && !element.isConnected)) {
        const message = '코드가 바뀌었어요. 해설을 다시 재생해 주세요.';
        globalThis.molipToast?.(message, 'warn');
        throw new Error(message);
      }
    };
    const startLine = lineAt(source, from);
    const replace = (from,to,text) => {
      ensureUnchanged();
      expected = expected.slice(0,from) + text + expected.slice(to);
      return api.replaceRange ? api.replaceRange(from,to,text) : api.setValue(expected);
    };
    const characters = text => globalThis.Intl?.Segmenter
      ? [...new Intl.Segmenter(undefined,{granularity:'grapheme'}).segment(text)].map(part=>part.segment)
      : Array.from(text);
    const delay = ms => sleep(ms * 1.5 / (globalThis.molipVoice?.rate || 1.5));
    let offset = to;
    api.highlightLines?.(startLine, lineAt(source, Math.max(from, to - 1)));
    for (const point of characters(source.slice(from,to)).reverse()) {
      await waitWhilePaused(); if (!active()) return;
      replace(offset-point.length,offset,''); offset-=point.length;
      const end=lineAt(api.getValue(),Math.max(from,offset-1));
      api.highlightLines?.(startLine,Math.max(startLine,end));
      spotlight('editor',caption?.textContent || '');
      await delay(35);
    }
    for (const point of characters(insert)) {
      await waitWhilePaused(); if (!active()) return;
      replace(offset,offset,point); offset+=point.length;
      api.highlightLines?.(startLine,lineAt(api.getValue(),Math.max(from,offset-1)));
      spotlight('editor',caption?.textContent || '');
      await delay(45);
    }
    if (active()) ensureUnchanged();
  }

  async function demonstrateAnswer(value) {
    const bridge = document.querySelector('.answer-state-bridge');
    if (!bridge) throw new Error('이 문제의 답안 입력을 찾지 못했어요.');
    bridge.value = value;
    bridge.dispatchEvent(new Event('input', {bubbles:true}));
    await sleep(60);
    return '답안을 비교해 봐요.';
  }
  async function readTerminal(command, active, expected) {
    const tutor = explanationSession ? explanationSession.gitTutor() : window.molipGitTutor;
    const terminal = window.mq3GitDemoTerminal;
    if (!tutor || !terminal) throw new Error('Git 해설 터미널이 없어요.');
    const owner = tutor.owner;
    const before = terminal.text(owner).trimEnd();
    const count = () => terminal.text(owner).split('\n').filter(line => line.trim() === expected).length;
    const previous = count();
    if (!await terminal.typeCommand(command, owner)) return '해설을 멈췄어요.';
    const deadline = Date.now() + 15000;
    while (active()) {
      const output = terminal.text(owner).trimEnd();
      if (output !== before && /(?:\$|>)\s*$/.test(output) && (expected == null || count() > previous)) return '출력을 확인했어요.';
      if (Date.now() > deadline) throw new Error('명령의 출력을 확인하지 못했어요.');
      await sleep(30);
    }
    return '해설을 멈췄어요.';
  }
  const handlers = {
    async bash_command(a, active) {
      if(typeof a.command!=='string'||!a.command||a.command.length>4000||/[\r\n\0]/.test(a.command))throw new Error('Bash 명령을 확인하세요.');
      return readTerminal(a.command,active,a.expected);
    },
    async vim_wait(a,active) {
      const terminal=window.mq3GitDemoTerminal;const tutor=explanationSession ? explanationSession.gitTutor() : window.molipGitTutor;
      const deadline=Date.now()+15000;
      while(active()){
        const progress=terminal?.vimState(tutor?.owner);
        if(progress && (a.passed ? progress.passed : progress.state))return 'Vim의 실제 상태를 확인했어요.';
        if(Date.now()>deadline)throw new Error('Vim 상태를 확인하지 못했어요.');
        await sleep(30);
      }
    },
    async vim_open(a, active) {
      const tutor=explanationSession ? explanationSession.gitTutor() : window.molipGitTutor;
      const terminal=window.mq3GitDemoTerminal;
      if(!tutor||!terminal)throw new Error('해설 터미널이 없어요.');
      if(!await terminal.typeCommand('vim memo.txt',tutor.owner))return '해설을 멈췄어요.';
      const deadline=Date.now()+15000;
      while(active()){
        const text=terminal.text(tutor.owner);
        if(/"memo.txt"/.test(text)&&/\d+L/.test(text))return 'Vim에서 메모를 열었어요.';
        if(Date.now()>deadline)throw new Error('Vim 화면을 확인하지 못했어요.');
        await sleep(30);
      }
    },
    async vim_keys(a, active) {
      const tutor=explanationSession ? explanationSession.gitTutor() : window.molipGitTutor;
      const terminal=window.mq3GitDemoTerminal;
      if(!tutor||!terminal||typeof a.keys!=='string'||a.keys.length>1000)throw new Error('Vim 키 입력을 확인하세요.');
      if(!await terminal.typeKeys(a.keys,tutor.owner))return '해설을 멈췄어요.';
      if(a.wait_prompt){
        const direct=document.querySelector('#git-demo-terminal')?.dataset.vim==='true';
        const deadline=Date.now()+15000;
        while(active()){
          if((direct && terminal.vimState(tutor.owner)?.state?.exited)||(!direct && /\$\s*$/.test(terminal.text(tutor.owner).trimEnd())))return '편집을 마치고 터미널로 돌아왔어요.';
          if(Date.now()>deadline)throw new Error('Vim 종료를 확인하지 못했어요.');
          await sleep(30);
        }
      }else{await sleep(100);return 'Vim 키를 입력했어요.';}
    },
    async inspect_folder(a, active) {
      // Fixed read-only commands only; each action runs exactly one command.
      if (!['pwd', 'ls'].includes(a.command)) throw new Error('폴더 확인 명령을 확인하세요.');
      return readTerminal(a.command, active);
    },
    async write_memo(a, active) {
      if (!['첫 메모', '둘째 메모', '셋째 메모'].includes(a.content)) throw new Error('메모 내용을 확인하세요.');
      return readTerminal('echo "' + a.content + '" > memo.txt', active);
    },
    async read_memo(a, active) {
      return readTerminal('cat memo.txt', active, String(a.expected || '').trim());
    },
    async git_command(a, active) {
      const tutor=explanationSession ? explanationSession.gitTutor() : window.molipGitTutor;
      if (!tutor || !Array.isArray(a.args)) throw new Error('Git 해설 터미널이 없어요.');
      const completed=await Promise.race([tutor.command(a.args),untilCancelled()]);
      if (!active()) return '해설을 멈췄어요.';
      if (!completed) throw new Error('Git 명령의 완료를 확인하지 못했어요.');
      return '실제 Git 명령이 끝났어요.';
    },
    choose_answer: a => demonstrateAnswer(String(a.id ?? '')),
    order_answer: a => demonstrateAnswer(JSON.stringify(a.ids ?? [])),
    fill_answer: a => demonstrateAnswer(String(a.value ?? '')),
    async set_input(a) {
      const input = document.querySelector('.result-pane textarea[aria-label="실행 입력"]');
      if (!input) throw new Error('실행 입력 칸을 찾지 못했어요.');
      input.value = String(a.value ?? '');
      input.dispatchEvent(new Event('input', {bubbles:true}));
      await sleep(40);
      return '해설의 첫 예제 입력을 준비했어요.';
    },
    async say(a) {
      // The spotlight and speech were started by run(); nothing else to do.
      return '설명: ' + String(a.text || '').slice(0, 80);
    },
    async type_code(a, active) {
      spotlight('editor', a.say);
      const spoken = speak(a.say);
      const lines = await typeCode(a.code, !!a.replace, active);
      await spoken;
      await sleep(250);
      return `코드 ${lines}줄을 입력했습니다.`;
    },
    async set_code(a, active) {
      const api = window.molipCodeEditors;
      if (!api || !api.setValue) throw new Error('코드 편집기를 찾지 못했습니다');
      const source = api.getValue();
      if (source == null) throw new Error('이 미션에는 코드 편집기가 없습니다 (코딩 미션에서만 됩니다)');
      const desired = String(a.code ?? '');
      let from = 0, tail = 0;
      while (from < source.length && from < desired.length && source[from] === desired[from]) from++;
      while (tail < source.length - from && tail < desired.length - from && source[source.length - tail - 1] === desired[desired.length - tail - 1]) tail++;
      const spoken = speak(a.say);
      if (source !== desired) await animateEdit(from, source.length - tail, desired.slice(from, desired.length - tail), active);
      await spoken;
      await sleep(300);
      return '코드를 편집기에 넣었습니다.';
    },
    async patch_code(a, active) {
      const api = window.molipCodeEditors;
      if (!api?.setValue || !api?.getValue) throw new Error('코드 편집기를 찾지 못했습니다');
      const current = api.getValue();
      if (current == null) throw new Error('코딩 미션에서 실행하세요');
      const before = String(a.before ?? '');
      const index = current.indexOf(before);
      if (!before || index < 0 || current.indexOf(before, index + 1) >= 0)
        throw new Error('바꿀 코드 조각이 정확히 한 곳에 있어야 해요');
      const spoken = speak(a.say);
      await animateEdit(index, index + before.length, String(a.after ?? ''), active);
      await spoken;
      await sleep(300);
      return '코드 조각을 바꿨어요.';
    },
    async fill_blanks(a) {
      const inputs = [...document.querySelectorAll('input.code-blank')];
      if (!inputs.length) throw new Error('채울 빈칸이 없습니다');
      const values = Array.isArray(a.values) ? a.values : [];
      values.forEach((value, i) => {
        if (!inputs[i]) return;
        inputs[i].value = String(value);
        inputs[i].dispatchEvent(new Event('input', { bubbles: true }));
      });
      await sleep(300);
      return `빈칸 ${Math.min(inputs.length, values.length)}개를 채웠습니다.`;
    },
    async run(a, active) {
      const button = byText('.pane-actions button', '코드 실행');
      if (!button) throw new Error('코드 실행 버튼이 없습니다 (코딩 미션에서만 됩니다)');
      const previous=document.querySelector('.result-pane')?.dataset.executionId ?? null;
      button.click();
      await sleep(40);
      await waitIdle(button,180000,previous,active);
      return '실행 결과:\n' + (workspaceReport() || '(출력 없음)');
    },
    async submit(a, active) {
      const button = byText('.pane-actions button', '제출');
      if (!button) throw new Error('제출 버튼이 없습니다 (코딩 미션에서만 됩니다)');
      button.click();
      await waitIdle(button,180000,null,active);
      await sleep(400);
      const passed = cleared();
      return (passed ? '제출 결과: 통과. 미션 클리어로 기록됐습니다 (정답 카드가 떠 있습니다).\n' : '제출 결과:\n') + (workspaceReport() || '(출력 없음)');
    },
    async answer_quiz(a) {
      const sections = [...document.querySelectorAll('.quiz-question')];
      if (!sections.length) throw new Error('이 미션에는 퀴즈나 확인 문항이 없습니다');
      const answers = a.answers && typeof a.answers === 'object' ? a.answers : {};
      const notes = [];
      for (const [key, value] of Object.entries(answers)) {
        const section = question(key);
        if (!section) { notes.push(`${key}번 문항이 없습니다 (이미 맞힌 문항이거나 번호가 다릅니다)`); continue; }
        const want = String(value).trim();
        const radios = [...section.querySelectorAll('input[type=radio]')];
        if (radios.length) {
          // Exact text, then 1-based number (what the compiled 해설 sends), then containment:
          // assets/layout/quiz-pick.js, shared with tests/js/quiz-pick.test.mjs.
          const label = r => normalize((r.closest('.quiz-option') || r.parentElement || r).textContent);
          const pick = radios[globalThis.molipQuizPick.pickOption(radios.map(label), want)];
          if (!pick) { notes.push(`${key}번: 보기 "${want}"를 찾지 못했습니다. 보기: ${radios.map(r => label(r)).join(' | ')}`); continue; }
          if (a.say) { spotlight(pick.closest('.quiz-option') ? `option:${key}:${radios.indexOf(pick) + 1}` : `quiz:${key}`, a.say); }
          pick.click();
        } else if (section.querySelector('.table-select')) {
          // A table: the answer is 1-based row/column numbers ("1,3,5"); tick exactly those.
          const wanted = new Set(want.split(',').map(s => Number(s.trim()) - 1).filter(n => Number.isInteger(n) && n >= 0));
          const boxes = [...section.querySelectorAll('.table-select input[type=checkbox]')];
          if (!boxes.length) { notes.push(`${key}번: 고를 표가 없습니다`); continue; }
          if (a.say) spotlight(`quiz:${key}`, a.say);
          for (const box of boxes) {
            const index = Number(box.dataset.index);
            if (box.checked !== wanted.has(index)) { box.click(); await sleep(120); }
          }
        } else {
          const input = section.querySelector('input:not([type=radio]):not([type=checkbox])');
          if (!input) { notes.push(`${key}번: 입력칸이 없습니다`); continue; }
          if (a.say) spotlight(`quiz:${key}`, a.say);
          input.value = want;
          input.dispatchEvent(new Event('input', { bubbles: true }));
        }
        if (a.say) await sleep(500);
      }
      await sleep(300);
      // submit:false ticks the answers and stops; a later call with no answers grades.
      if (a.submit === false) return `답을 넣었습니다: ${Object.keys(answers).join(', ')}번` + (notes.length ? '\n' + notes.join('\n') : '');
      const button = document.querySelector('.quiz-actions .primary');
      if (button && !button.disabled) { if (a.say && !Object.keys(answers).length) spotlight('quiz_submit', a.say); button.click(); await waitIdle(button); }
      await sleep(300);
      const status = text('.quiz-actions ~ .execution-status, .concept-flow .execution-status, .execution-status', 600) + (cleared() ? ' · 미션 클리어 (정답 카드가 떠 있습니다)' : '');
      const banner = text('.clear-banner', 200);
      return ['채점 결과: ' + (status || '(상태 없음)'), banner, ...notes].filter(Boolean).join('\n');
    },
    async next() { const popup = popupButton('다음 미션 ›'); const b = popup || byText('.header-navigation button', '다음 →'); if (!b || b.disabled) throw new Error('다음 미션으로 갈 수 없습니다'); b.click(); await sleep(600); return '다음 미션으로 이동했습니다: ' + text('.reading-mission h2, .problem-pane h2, .slides-mission h2', 120); },
    async prev() { const b = byText('.header-navigation button', '← 이전'); if (!b || b.disabled) throw new Error('이전 미션으로 갈 수 없습니다'); b.click(); await sleep(600); return '이전 미션으로 이동했습니다: ' + text('.reading-mission h2, .problem-pane h2, .slides-mission h2', 120); },
    async goto(a) { const cells = document.querySelectorAll('.mission-cell'); const cell = cells[Number(a.mission) - 1]; if (!cell) throw new Error(`이 단원에는 ${a.mission}번 미션이 없습니다 (미션 ${cells.length}개)`); cell.click(); await sleep(600); return `${a.mission}번 미션으로 이동했습니다: ` + text('.reading-mission h2, .problem-pane h2, .slides-mission h2', 120); },
    async next_slide() {
      // Steps by source slide (the Markdown's `---` count the model sees): a comic's extra panels
      // are shown briefly on the way, so the narration and the deck stay in step.
      const host = document.querySelector('.slides-host');
      if (host && host.molipSlides) {
        if (!(await host.molipSlides.nextSource(1500))) throw new Error('넘길 장이 없습니다');
        await sleep(300);
        return '다음 장으로 넘겼습니다 (' + host.molipSlides.sourceIndex(host.molipSlides.index) + '번째 장): ' + text('.slides-counter', 20);
      }
      const b = byText('.slides-bar button', '다음 장 →'); if (!b || b.disabled) throw new Error('넘길 장이 없습니다'); b.click(); await sleep(300); return '다음 장으로 넘겼습니다: ' + text('.slides-counter', 20);
    },
    async finish_slides(a) {
      // {quiet: true} (/tour-all) marks the deck watched where it stands, no presentation.
      const b = byText('button', '다 봤어요 · 미션 완료'); if (!b) throw new Error('슬라이드 미션이 아닙니다');
      if (a && a.quiet) { if (!b.disabled) b.click(); await sleep(400); return '슬라이드 미션을 완료로 표시했습니다.'; }
      // Presenting: the next mission, if it is a deck, opens in presentation mode too (slides.js mount).
      const host = document.querySelector('.slides-host');
      if (host && host.classList.contains('slides-presenting') && globalThis.molipSlides) globalThis.molipSlides.carryPresenting = Date.now();
      if (!b.disabled) b.click(); await sleep(400); return '슬라이드 미션을 완료로 표시했습니다.';
    },
  };
  // Where each action's spotlight goes when it carries "say" (type_code places its own).
  const DEFAULT_TARGET = {
    git_command: () => '#git-demo-terminal',
    choose_answer: a => `answer:${a.id}`, order_answer: () => '.answer-order', fill_answer: () => '[aria-label="빈칸 답안"]',
    say: a => a.target || null, set_code: () => 'editor', patch_code: () => 'editor', fill_blanks: () => 'blanks', run: () => 'run', submit: () => 'submit',
    answer_quiz: () => 'quiz', next: () => 'nav', prev: () => 'nav', goto: () => 'missions', next_slide: () => 'slides', finish_slides: () => 'slides',
  };
  let narrationRun = 0;
  // A session owns both its restoration snapshot and its DOM/Git targets.
  class ExplanationSession {
    constructor(root, owner) {
      this.root = root;
      this.owner = owner ?? root.dataset.explanationSession ?? null;
      this.code = globalThis.molipCodeEditors?.getValue() ?? null;
      this.fields = [...root.querySelectorAll('.answer-interaction input, .answer-state-bridge, .run-input textarea')].map(field => [field, field.value, field.checked]);
      this.tutor = globalThis.molipGitTutor;
      this.terminal = root.querySelector('#git-demo-terminal');
      this.blockInput = event => {
        if (!event.isTrusted || event.target.closest?.('[data-explanation-stop], .narration-speed')) return;
        if (event.type === 'keydown' && (['Tab','Escape','Home','End','PageUp','PageDown'].includes(event.key) || event.key.startsWith('Arrow'))) return;
        if (event.type === 'keydown' && (event.ctrlKey || event.metaKey) && ['a','c'].includes(event.key.toLowerCase())) return;
        event.preventDefault();event.stopImmediatePropagation();
      };
      for (const name of ['click','keydown','beforeinput','paste','drop']) root.addEventListener(name, this.blockInput, true);
    }
    current() { return this.root.isConnected && (this.owner === null || this.root.dataset.explanationSession === this.owner); }
    gitTutor() {
      if (!this.current() || this.tutor !== globalThis.molipGitTutor) return null;
      const terminalOwner = this.terminal?.dataset.terminalSession;
      return !terminalOwner || this.tutor?.owner === terminalOwner ? this.tutor : null;
    }
    restore() {
      for (const name of ['click','keydown','beforeinput','paste','drop']) this.root.removeEventListener(name, this.blockInput, true);
      if (!this.current()) return;
      if (this.code !== null) globalThis.molipCodeEditors?.setValue(this.code);
      for (const [field, value, checked] of this.fields) {
        if (!field.isConnected) continue;
        field.value = value;
        if (checked !== undefined) field.checked = checked;
        if (field.matches('.answer-state-bridge, .run-input textarea')) field.dispatchEvent(new Event('input', {bubbles:true}));
      }
    }
    static retireGitTutor(owner) {
      const tutor=globalThis.molipGitTutor;
      if (tutor?.owner !== owner) return false;
      tutor.dispose();
      delete globalThis.molipGitTutor;
      return true;
    }
  }
  let explanationSession = null;
  function restoreExplanation() {
    const session=explanationSession;
    explanationSession=null;
    session?.restore();
  }
  async function runExplanation(actions, options = {}) {
    stop();
    const root=options.root || document.querySelector('.repository-task') || document.body;
    if (!root.isConnected || (options.owner != null && root.dataset.explanationSession !== options.owner)) return '해설이 이미 끝났어요.';
    const session=new ExplanationSession(root,options.owner);
    explanationSession=session;
    // A demonstration can execute examples, but never submit, advance or grant completion.
    const allowed = new Set(['vim_wait', 'bash_command', 'vim_open', 'vim_keys', 'write_memo', 'inspect_folder', 'read_memo', 'git_command', 'say', 'set_code', 'patch_code', 'type_code', 'set_input', 'run', 'choose_answer', 'order_answer', 'fill_answer']);
    try { return await run(Array.isArray(actions) ? actions.filter(action => allowed.has(action?.action)) : [], true); }
    finally { if (explanationSession === session) restoreExplanation(); }
  }
  async function run(actions, explanation = false, options = {}) {
    if (!explanation && explanationSession) stop();
    if (!Array.isArray(actions)) return '동작 목록이 배열이 아닙니다.';
    captionSource = actions.flatMap(action => ['code','before','after','input','value'].map(key=>action?.[key] ?? '')).join('\n');
    const runId = ++narrationRun;
    if (options.forceVoice) forcedVoiceRun = runId;
    const session = explanation ? explanationSession : null;
    const active = () => !cancelled && runId === narrationRun && (!session || session.current());
    replyRun++; stopSpeech(); releaseCancelWaiters(); clearSpot();
    cancelled = false; paused = false; running = true;
    globalThis.molipVoice?.resetFailure?.();
    const lines = [];
    try {
    await Promise.race([prefetch(actions, active), untilCancelled()]);
    if (!active()) return '해설 준비를 멈췄어요.';
    clearSpot();
    // A deck script (it ends with finish_slides) is presented full screen, like a class, and
    // starts from the first slide: its lines and next_slide steps count from the top, so a deck
    // left on slide 5 would otherwise have the voice a few slides behind the picture.
    if (actions.some(a => a && a.action === 'finish_slides' && !a.quiet)) {
      const host = document.querySelector('.slides-host');
      if (host && host.molipSlides && host.molipSlides.first) host.molipSlides.first();
      if (host && host.molipPresent && !host.classList.contains('slides-presenting')) { host.molipPresent(true); await sleep(300); }
    }
      for (const [i, action] of actions.entries()) {
        await waitWhilePaused();
        if (!active()) { lines.push(`${i + 1}. 학생이 멈춤을 눌러 여기서 중단했습니다.`); break; }
        const name = action && action.action;
        const handler = handlers[name];
        if (!handler) { lines.push(`${i + 1}. ${name}: 모르는 동작입니다 (가능: ${Object.keys(handlers).join(', ')})`); continue; }
        try {
          const sentence = name === 'say' ? action.text : action.say;
          showMemory(action.diagram);
          focusCode(action, actions[i + 1]);
          if (name !== 'type_code' && name !== 'answer_quiz') {
            spotlight(action.target || (DEFAULT_TARGET[name] ? DEFAULT_TARGET[name](action) : null), sentence);
          }
          if (sentence && !['type_code', 'answer_quiz', 'patch_code', 'set_code'].includes(name)) {
            await speak(sentence);
            await waitWhilePaused();
            if (!active()) { lines.push(`${i + 1}. 학생이 멈춤을 눌러 여기서 중단했습니다.`); break; }
          } else if (sentence && name === 'answer_quiz') {
            spotlight('quiz', sentence);
            await speak(sentence);
          }
          if (!active()) break;
          lines.push(`${i + 1}. ${name}: ${await handler(action, active)}`);
          if (sentence) await sleep(350);
        } catch (error) {
          lines.push(`${i + 1}. ${name}: 오류 - ${error && error.message ? error.message : error}`);
          break;
        }
      }
    } finally {
      if (runId === narrationRun) {
      running = false; paused = false;
      if(forcedVoiceRun===runId)forcedVoiceRun=0;
      stopSpeech();
      clearSpot();
      releaseCancelWaiters();
      }
    }
    return lines.join('\n');
  }
  // Read a chat answer aloud (the 소리 switch is on): prose only, code blocks skipped, one
  // sentence at a time so 멈춤 and a new question cut it off cleanly. No spotlight, no caption.
  let replyRun = 0;
  async function speakReply(text, force) {
    if ((!voice && !force) || running) return false;
    const run = ++replyRun;
    stopSpeech();
    cancelled = false;
    // 🔊 읽기 on a message reads it even while the switch is off.
    const restore = voice;
    if (force) voice = true;
    try {
    const prose = String(text || '')
      .replace(/```[\s\S]*?```/g, ' ')
      .replace(/^#{1,6}\s*/gm, '').replace(/^\s*[-*]\s+/gm, '').replace(/^\s*\d+\.\s+/gm, '')
      .replace(/\*\*(.+?)\*\*/g, '$1').replace(/`([^`\n]+)`/g, '$1').replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
      .replace(/\s+/g, ' ').trim();
    if (!prose) return false;
    const helpers = globalThis.molipSpeech;
    const sentences = helpers && helpers.speechSentences ? helpers.speechSentences(prose).map(s => s.text) : [prose];
    if (neural()) for (const sentence of sentences) synthesize(sentence);
    for (const sentence of sentences) {
      if (cancelled || run !== replyRun || running) break;
      await speak(sentence);
    }
    return run === replyRun;
    } finally { voice = restore; }
  }
  // Stop reading a reply without touching a narration that may be running.
  function stopReply() { replyRun++; if (!running) stopSpeech(); }
  function stop() { cancelled = true; paused = false; replyRun++; cancelAnimationFrame(glideFrame); stopSpeech(); releaseCancelWaiters(); clearSpot(); restoreExplanation(); }
  function setVoice(on) { voice = !!on; if (!voice) stopSpeech(); return voice; }
  function setVoiceName(name) { return globalThis.molipVoice ? globalThis.molipVoice.setName(name) : String(name || 'system'); }
  async function runOverview(actions, dialog) {
    if(!dialog?.open)return '학습 정보 창을 먼저 여세요.';
    stop();
    const abort=()=>stop();
    dialog.addEventListener('close',abort);
    dialog.dataset.overviewRunning='true';
    try{return await run(actions.filter(a=>a.action==='say'),false,{forceVoice:true});}
    finally{dialog.removeEventListener('close',abort);dialog.dataset.overviewRunning='false';}
  }
  globalThis.molipAgent = { runOverview, retireGitTutor: ExplanationSession.retireGitTutor, run, runExplanation, stop, pause, resume, speakReply, stopReply, get paused() { return paused; }, get running() { return running; }, setVoice, setVoiceName, resolveTarget, glideTo, get voice() { return voice; }, get voiceName() { return globalThis.molipVoice ? globalThis.molipVoice.name : 'system'; }, get lastSpeech() { return lastSpeech; }, get playbackRate() { return currentAudio ? currentAudio.playbackRate : null; }, actions: Object.keys(handlers) };
})();
