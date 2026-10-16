// Keyboard shortcuts for the whole app. The scheme (Ctrl on Windows, ⌘ on macOS = "mod"):
//
//   mod+← / mod+→      previous / next mission        mod+↑ / mod+↓   previous / next unit
//   mod+K              curriculum menu                mod+I           AI panel open / fold
//   mod+/              this cheat sheet               F11 (⌃⌘F)       fullscreen
//   mod+Enter          run code; twice = submit       mod+Shift+Enter submit at once
//   Enter              grade a short answer; take a modal card's primary button
//   Space              pause / resume a running 해설 (in a deck: next slide)
//   Esc                stop autopilot or reading, close sheets and menus, leave presentation
//   ← → N              inside a deck: slides and the presenter script (assets/slides/slides.js)
//   mod+double-click   read aloud from that paragraph (assets/speech/speech.js)
//
// mod+letter/arrow shortcuts stay out of text fields and the code editor, where those keys
// keep their editing meaning. The learning view renders hidden #shortcut-* buttons that the
// moves click, so the Rust side keeps the navigation rules.
//
// F11 (macOS: control+command+F) toggles the OS window fullscreen by clicking the hidden
// button the Rust side renders (#app-fullscreen-toggle), whose data-fullscreen attribute
// mirrors the window state. Slides use the same button when they enter presentation mode.
//
// Coding missions: Ctrl+Enter (macOS: ⌘Enter) runs the code. Enter pressed right after that
// chord (within RESUBMIT_WINDOW_MS, before any other key) submits, so "run, looks right,
// Enter" is one motion. Ctrl+Shift+Enter (⌘⇧Enter) submits straight away. The listener runs in
// the capture phase so CodeMirror's own Mod-Enter binding never sees the chord.
(function () {
  'use strict';
  if (globalThis.molipShortcuts || typeof document === 'undefined') return;
  const mac = navigator.platform.toLowerCase().includes('mac');
  const toggleButton = () => document.getElementById('app-fullscreen-toggle');
  const toggleFullscreen = () => { const b = toggleButton(); if (b) b.click(); return !!b; };
  const isFullscreen = () => toggleButton()?.dataset.fullscreen === 'true';
  const paneButton = text => [...document.querySelectorAll('.pane-actions button')].find(b => b.textContent.trim() === text && !b.disabled) || null;
  const RESUBMIT_WINDOW_MS = 2000;
  let armedUntil = 0;
  const MOD = mac ? '⌘' : 'Ctrl';
  const inEditable = target => target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement
    || (target instanceof Element && (target.isContentEditable || !!target.closest('.cm-editor')));
  const clickId = id => { const b = document.getElementById(id); if (!b || b.disabled) return false; b.click(); return true; };
  function toggleCurriculum() {
    const dialog = document.querySelector('.curriculum-menu');
    if (!dialog) return false;
    if (dialog.open) dialog.close(); else document.querySelector('.curriculum-toggle')?.click();
    return true;
  }
  // ---- Cheat sheet (mod+/): every shortcut, with this platform's keys. ----
  const SHEET = [
    ['이동', [[`${MOD}+←  ${MOD}+→`, '이전 · 다음 단계'], [`${MOD}+↑  ${MOD}+↓`, '이전 · 다음 단원'], [`${MOD}+K`, '수업 목차 열기 · 닫기'], [`${MOD}+I`, 'AI에게 물어보기 열기 · 접기']]],
    ['코딩 미션', [[`${MOD}+Enter`, '코드 실행'], [`${MOD}+Enter 두 번`, '실행하고 바로 제출'], [`${MOD}+Shift+Enter`, '바로 제출'], ['Enter', '주관식 답 칸에서 채점 · 정답 카드에서 다음 미션']]],
    ['슬라이드', [['←  →  Space', '이전 · 다음 장 (마지막 장에서 →는 다음 단계, 첫 장에서 ←는 이전 단계)'], ['N', '강사 스크립트'], ['전체 화면 버튼', '발표 모드 · Esc로 해제']]],
    ['소리', [[`${MOD}+더블 클릭`, '그 문단부터 읽어 주기 · Esc로 정지'], ['Space', '해설 일시정지 · 재개'], ['Esc', '자동 진행 해제']]],
    ['화면', [[mac ? '⌃⌘F' : 'F11', '전체 화면'], [`${MOD}+/`, '이 안내 열기 · 닫기']]],
  ];
  let sheet = null;
  function toggleSheet(on) {
    if (!sheet) {
      sheet = document.createElement('div'); sheet.className = 'shortcut-sheet'; sheet.setAttribute('role', 'dialog'); sheet.setAttribute('aria-label', '단축키');
      const panel = document.createElement('div'); panel.className = 'shortcut-panel';
      const head = document.createElement('div'); head.className = 'shortcut-head';
      const title = document.createElement('h2'); title.textContent = '단축키';
      const close = document.createElement('button'); close.type = 'button'; close.textContent = '닫기 ×'; close.onclick = () => toggleSheet(false);
      head.append(title, close); panel.append(head);
      for (const [group, rows] of SHEET) {
        const section = document.createElement('section');
        const h = document.createElement('h3'); h.textContent = group; section.append(h);
        const table = document.createElement('table');
        for (const [keys, what] of rows) {
          const tr = document.createElement('tr');
          const k = document.createElement('td'); k.className = 'shortcut-keys';
          for (const [i, key] of keys.split('  ').entries()) { if (i) k.append(' '); const kbd = document.createElement('kbd'); kbd.textContent = key; k.append(kbd); }
          const w = document.createElement('td'); w.textContent = what;
          tr.append(k, w); table.append(tr);
        }
        section.append(table); panel.append(section);
      }
      sheet.append(panel);
      sheet.addEventListener('click', event => { if (event.target === sheet) toggleSheet(false); });
      document.body.append(sheet);
    }
    const show = on === undefined ? sheet.hidden !== false || !sheet.isConnected : !!on;
    sheet.hidden = !show;
    return true;
  }
  document.addEventListener('keydown', event => {
    // Navigation and panels: mod + key, outside text fields and the code editor so editing
    // keys (word jumps, line start/end) keep their meaning there.
    const mod = mac ? event.metaKey : event.ctrlKey;
    if (mod && !event.altKey && !event.shiftKey && !inEditable(event.target)) {
      let handled = false;
      switch (event.key) {
        case 'ArrowLeft': handled = clickId('shortcut-prev-mission'); break;
        case 'ArrowRight': handled = clickId('shortcut-next-mission'); break;
        case 'ArrowUp': handled = clickId('shortcut-prev-unit'); break;
        case 'ArrowDown': handled = clickId('shortcut-next-unit'); break;
        case 'k': case 'K': handled = toggleCurriculum(); break;
        case 'i': case 'I': handled = clickId('shortcut-assistant'); break;
        case '/': handled = toggleSheet(); break;
      }
      if (handled) { event.preventDefault(); event.stopPropagation(); return; }
    }
    if (event.key === 'Escape' && sheet && !sheet.hidden) { event.preventDefault(); toggleSheet(false); return; }
    // A modal card on screen (정답 카드, 확인 대화상자): Enter takes its primary button. Only
    // primary buttons, so a destructive confirmation never fires from a stray Enter.
    const card = document.querySelector('.doctor-panel');
    if (card && event.key === 'Enter' && !event.ctrlKey && !event.metaKey && !event.altKey && !event.shiftKey) {
      const primary = card.querySelector('button.primary');
      if (primary && !primary.disabled) {
        event.preventDefault(); event.stopPropagation();
        armedUntil = 0;
        primary.click();
        return;
      }
    }
    // Space pauses or resumes a running 해설 (the panel's button keeps the Rust side in step).
    const agent = globalThis.molipAgent;
    if (event.key === ' ' && agent && agent.running && !event.ctrlKey && !event.metaKey && !event.altKey
        && !(event.target instanceof HTMLInputElement || event.target instanceof HTMLTextAreaElement || event.target.isContentEditable)) {
      event.preventDefault(); event.stopPropagation();
      const button = document.getElementById('narration-pause');
      if (button) button.click(); else if (agent.paused) agent.resume(); else agent.pause();
      return;
    }
    if (event.key === 'Escape') {
      // /auto-all: the learning view renders a hidden stop button while it runs.
      const stop = document.getElementById('autopilot-stop');
      if (stop) { stop.click(); globalThis.molipToast?.('자동 진행을 해제했습니다', 'info'); }
      return;
    }
    if (event.key === 'F11' || (mac && event.metaKey && event.ctrlKey && event.key.toLowerCase() === 'f')) {
      event.preventDefault();
      if (event.repeat) return;
      toggleFullscreen();
      return;
    }
    if (event.key !== 'Enter') { armedUntil = 0; return; }
    const chord = mac ? event.metaKey : event.ctrlKey;
    if (chord && !event.altKey) {
      // Ctrl+Enter runs. Ctrl+Enter again right away (Ctrl held, Enter twice) submits; the
      // submit waits for the run to finish if it is still going. Ctrl+Shift+Enter submits at once.
      event.preventDefault(); event.stopPropagation();
      if (event.shiftKey || performance.now() < armedUntil) {
        armedUntil = 0;
        submitWhenIdle();
        return;
      }
      const button = paneButton('코드 실행');
      if (!button) return;
      button.click();
      armedUntil = performance.now() + RESUBMIT_WINDOW_MS;
      globalThis.molipToast?.('실행 중 · Ctrl+Enter를 한 번 더 누르면 제출합니다', 'info');
      return;
    }
    // Enter in a short-answer box grades the question.
    if (!event.ctrlKey && !event.metaKey && !event.altKey && !event.shiftKey && event.target instanceof HTMLInputElement
        && event.target.closest('.quiz-question')) {
      const grade = document.querySelector('.quiz-actions button.primary');
      if (grade && !grade.disabled) { event.preventDefault(); event.stopPropagation(); grade.click(); }
      return;
    }
    armedUntil = 0;
  }, { capture: true });
  async function submitWhenIdle() {
    const started = performance.now();
    while (performance.now() - started < 8000) {
      const button = paneButton('제출');
      if (button) { button.click(); globalThis.molipToast?.('제출했습니다', 'info'); return; }
      if (![...document.querySelectorAll('.pane-actions button')].some(b => b.textContent.trim() === '제출')) return;
      await new Promise(resolve => setTimeout(resolve, 120));
    }
  }
  globalThis.molipShortcuts = { toggleFullscreen, isFullscreen, toggleSheet, toggleCurriculum, runKey: mac ? '⌘Enter' : 'Ctrl+Enter', submitKey: mac ? '⌘⇧Enter' : 'Ctrl+Shift+Enter', mod: MOD };
})();
