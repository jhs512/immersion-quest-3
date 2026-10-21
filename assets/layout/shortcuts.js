// Shared shortcut policy. Mod = Command on macOS, Control on Windows/Linux.
// One chord has one action: running never arms a later submission.
(function () {
  'use strict';
  if (globalThis.molipShortcuts || typeof document === 'undefined') return;
  const mac = /mac/i.test(navigator.platform);
  const MOD = mac ? '⌘' : 'Ctrl';
  const bindings = {
    run: {label: `${MOD}+Enter`, aria: `${mac ? 'Meta' : 'Control'}+Enter`, title: '코드 실행'},
    submit: {label: `${MOD}+Shift+Enter`, aria: `${mac ? 'Meta' : 'Control'}+Shift+Enter`, title: '답안 제출'},
    previous: {label: `${MOD}+←`, aria: `${mac ? 'Meta' : 'Control'}+ArrowLeft`, title: '이전 스텝'},
    next: {label: `${MOD}+→`, aria: `${mac ? 'Meta' : 'Control'}+ArrowRight`, title: '다음 스텝'},
    help: {label: `${MOD}+/`, aria: `${mac ? 'Meta' : 'Control'}+/`, title: '단축키 안내'},
  };
  const inEditable = target => target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement
    || (target instanceof Element && (target.isContentEditable || !!target.closest('.cm-editor, .xterm')));
  const paneButton = text => [...document.querySelectorAll('.pane-actions button')].find(b => b.textContent.trim() === text && !b.disabled) || null;
  const clickId = id => { const b = document.getElementById(id); if (!b || b.disabled) return false; b.click(); return true; };
  const toggleButton = () => document.getElementById('app-fullscreen-toggle');
  const toggleFullscreen = () => { const b = toggleButton(); if (!b) return false; b.click(); return true; };
  const isFullscreen = () => toggleButton()?.dataset.fullscreen === 'true';
  const taskBusy = () => {
    const task = document.querySelector('.repository-task');
    return task?.dataset.busy === 'true' || task?.dataset.narrating === 'true';
  };
  function move(direction) {
    if (taskBusy()) return false;
    const b = document.querySelector(`[data-shortcut-action="${direction}"]`);
    if (b) { if (b.disabled) return false; b.click(); return true; }
    const steps = [...document.querySelectorAll('.study-navigation [data-step-id]')];
    const task = document.querySelector('.repository-task');
    const current = steps.findIndex(step => step.dataset.stepId === task?.dataset.taskId);
    if (task && current >= 0) {
      const target = steps[current + (direction === 'next' ? 1 : -1)];
      if (!target || target.disabled) return false;
      target.click(); return true;
    }
    return clickId(direction === 'next' ? 'shortcut-next-mission' : 'shortcut-prev-mission');
  }
  function toggleCurriculum() {
    const dialog = document.querySelector('.curriculum-menu');
    if (!dialog) return false;
    if (dialog.open) dialog.close(); else document.querySelector('.curriculum-toggle')?.click();
    return true;
  }
  const SHEET = [
    ['실행과 제출', [[bindings.run.label, '코드를 실행해 결과 확인'], [bindings.submit.label, '현재 답안 제출'], ['Enter', '문제 영역에서 제출 · 통과 창에서 다음으로 이동'], ['터미널의 Enter', '현재 명령 실행 · Vim 명령 입력']]],
    ['스텝 이동', [[`${bindings.previous.label}  ${bindings.next.label}`, '이전 · 다음 스텝'], [`${MOD}+↑  ${MOD}+↓`, '이전 · 다음 단원 (단원 이동 화면)'], [`${MOD}+K`, '수업 목차 (목차가 있는 화면)'], [`${MOD}+I`, 'AI 패널 (조교가 있는 화면)']]],
    ['해설과 화면', [['Space', '해설 일시정지 · 재개'], ['Esc', '해설 정지 · 열린 안내 닫기'], [mac ? '⌃⌘F' : 'F11', '전체 화면'], [bindings.help.label, '이 안내 열기 · 닫기']]],
    ['신고', [['Ctrl+Alt+Shift+B', '앱 오류 신고 · 별도 네이티브 창'], ['Ctrl+Alt+Shift+P', '현재 수업의 문제 신고 (Mac: Alt는 Option)']]],
    ['슬라이드와 읽기', [['←  →  Space', '슬라이드 이전 · 다음 장'], ['N', '슬라이드 강사 스크립트'], [`${MOD}+더블 클릭`, '선택한 문단부터 읽기']]],
  ];
  let sheet = null, previousFocus = null;
  const restoreFocus = () => { if (previousFocus?.isConnected) previousFocus.focus(); previousFocus = null; };
  function toggleSheet(on) {
    if (!sheet) {
      sheet = document.createElement('dialog'); sheet.className = 'shortcut-sheet'; sheet.setAttribute('aria-labelledby', 'shortcut-title');
      const panel = document.createElement('div'); panel.className = 'shortcut-panel';
      const head = document.createElement('div'); head.className = 'shortcut-head';
      const title = document.createElement('h2'); title.id = 'shortcut-title'; title.textContent = '단축키';
      const close = document.createElement('button'); close.type = 'button'; close.textContent = '닫기'; close.autofocus = true; close.onclick = () => toggleSheet(false);
      head.append(title, close); panel.append(head);
      const note = document.createElement('p'); note.className = 'shortcut-note';
      note.textContent = `${mac ? 'Mac은 Command(⌘)' : 'Windows는 Ctrl'}를 사용해요. 스텝 이동·목차·안내 키는 코드나 터미널 입력 중에는 편집 기능을 유지해요. 실행·제출 키는 입력 중에도 사용할 수 있어요. 한글 조합 중에는 동작하지 않아요.`;
      panel.append(note);
      for (const [group, rows] of SHEET) {
        const section = document.createElement('section');
        const h = document.createElement('h3'); h.textContent = group; section.append(h);
        const table = document.createElement('table'); table.setAttribute('aria-label', group);
        for (const [keys, what] of rows) {
          const tr = document.createElement('tr'); const k = document.createElement('td'); k.className = 'shortcut-keys';
          for (const [i, key] of keys.split('  ').entries()) { if (i) k.append(' '); const kbd = document.createElement('kbd'); kbd.textContent = key; k.append(kbd); }
          const w = document.createElement('td'); w.textContent = what; tr.append(k, w); table.append(tr);
        }
        section.append(table); panel.append(section);
      }
      sheet.append(panel); sheet.addEventListener('click', event => { if (event.target === sheet) toggleSheet(false); });
      sheet.addEventListener('close', restoreFocus);
      document.body.append(sheet);
    }
    const show = on === undefined ? !sheet.open : !!on;
    if (show && !sheet.open) { previousFocus = document.activeElement === document.body ? document.querySelector('[data-shortcut-action="help"]') : document.activeElement; sheet.showModal(); }
    else if (!show && sheet.open) { sheet.close(); restoreFocus(); }
    return true;
  }
  function decorate() {
    for (const button of document.querySelectorAll('[data-shortcut-action]')) {
      const binding = bindings[button.dataset.shortcutAction]; if (!binding) continue;
      if (button.dataset.shortcutLabel !== binding.label) {
        button.dataset.shortcutLabel = binding.label;
        button.setAttribute('aria-keyshortcuts', binding.aria);
        if (!button.hasAttribute('aria-label')) button.setAttribute('aria-label', button.textContent.trim());
        button.title = `${binding.title} · ${binding.label}${['previous','next','help'].includes(button.dataset.shortcutAction) ? ' (코드·터미널 입력 중 제외)' : ''}`;
      }
    }
  }
  // Hints use CSS-generated text so accessible button names and automation stay stable.
  if (typeof MutationObserver !== 'undefined') {
    const observer = new MutationObserver(decorate);
    observer.observe(document.documentElement, {subtree: true, childList: true}); decorate();
  }
  document.addEventListener('keydown', event => {
    if (event.isComposing || event.keyCode === 229 || globalThis.molipIme?.isComposing(event.target)) return;
    if (!event.repeat && (event.ctrlKey || (mac && event.metaKey)) && !event.altKey && !event.shiftKey && event.key.toLowerCase() === 'q' && clickId('app-quit')) {event.preventDefault();event.stopPropagation();return;}
    if (event.repeat) { if (event.key === 'F11' || ((event.ctrlKey || event.metaKey) && ['Enter','ArrowLeft','ArrowRight'].includes(event.key)) || (event.key === 'Enter' && !inEditable(event.target))) event.preventDefault(); return; }
    if (sheet?.open) {
      if (event.key === 'Escape' || ((mac ? event.metaKey : event.ctrlKey) && event.key === '/')) {
        event.preventDefault(); event.stopPropagation(); toggleSheet(false);
      }
      return;
    }
    const card = document.querySelector('.task-passed-dialog, .doctor-panel');
    if (card && event.key === 'Enter' && !event.ctrlKey && !event.metaKey && !event.altKey && !event.shiftKey) {
      // A focused action keeps native keyboard activation (for example, "여기 머물기").
      // Only use the default action when Enter came from non-interactive content.
      if (event.target instanceof Element && card.contains(event.target)
        && (inEditable(event.target) || event.target.closest('button,a,select,summary'))) return;
      const primary = card.querySelector('button.primary');
      if (primary && !primary.disabled) { event.preventDefault(); event.stopPropagation(); primary.click(); }
      return;
    }
    // Keep all background learning shortcuts out of an open modal.
    const modal = [...(document.querySelectorAll?.('[role="dialog"], dialog[open]') || [])].some(p => !p.hidden && p.getClientRects().length > 0);
    if (modal) return;
    if (event.key === 'F11' || (mac && event.metaKey && event.ctrlKey && event.key.toLowerCase() === 'f')) {
      event.preventDefault(); toggleFullscreen(); return;
    }
    const mod = mac ? event.metaKey : event.ctrlKey;
    if (event.key === 'Enter' && mod && !event.altKey) {
      // No retries, waiting queue or run-then-submit shortcut: disabled means no action.
      const label = event.shiftKey ? '제출' : '코드 실행';
      const button = paneButton(label);
      const control = button || [...document.querySelectorAll('.pane-actions button')].find(b => b.textContent.trim() === label);
      if (control) { event.preventDefault(); event.stopPropagation(); if (button) button.click(); }
      return;
    }
    if (mod && !event.altKey && !event.shiftKey && !inEditable(event.target)) {
      let handled = false;
      switch (event.key) {
        case 'ArrowLeft': handled = move('previous'); break;
        case 'ArrowRight': handled = move('next'); break;
        case 'ArrowUp': handled = !taskBusy() && clickId('shortcut-prev-unit'); break;
        case 'ArrowDown': handled = !taskBusy() && clickId('shortcut-next-unit'); break;
        case 'k': case 'K': handled = toggleCurriculum(); break;
        case 'i': case 'I': handled = clickId('shortcut-assistant'); break;
        case '/': handled = toggleSheet(); break;
      }
      if (handled) { event.preventDefault(); event.stopPropagation(); return; }
    }
    const agent = globalThis.molipAgent;
    if (event.key === ' ' && agent?.running && !event.ctrlKey && !event.metaKey && !event.altKey && !inEditable(event.target)
      && !(event.target instanceof Element && event.target.closest('button:not(:disabled),a,select:not(:disabled),summary'))) {
      event.preventDefault(); event.stopPropagation();
      const b = document.getElementById('narration-pause'); if (b) b.click(); else if (agent.paused) agent.resume(); else agent.pause(); return;
    }
    if (event.key === 'Escape') {
      if (agent?.running) agent.stop();
      const stop = document.getElementById('autopilot-stop'); if (stop) stop.click(); return;
    }
    if (event.key !== 'Enter' || event.ctrlKey || event.metaKey || event.altKey || event.shiftKey) return;
    const target = event.target;
    const inQuestion = target instanceof HTMLInputElement && target.closest('.quiz-question, .answer-interaction');
    if (!inQuestion && (inEditable(target) || (target instanceof Element && target.closest('button, a, select, summary, .slides-mission, .xterm')))) return;
    const submit = document.querySelector('[data-enter-submit]');
    if (submit) { if (!submit.disabled) { event.preventDefault(); event.stopPropagation(); submit.click(); } return; }
    const grade = document.querySelector('.quiz-actions button.primary');
    if (grade && !grade.disabled) { event.preventDefault(); event.stopPropagation(); grade.click(); }
    else {
      const next = document.querySelector('[data-enter-next]');
      if (next && !next.disabled) { event.preventDefault(); event.stopPropagation(); next.click(); }
      else if (move('next')) { event.preventDefault(); event.stopPropagation(); }
    }
  }, {capture: true});
  globalThis.molipShortcuts = {move, bindings, toggleFullscreen, isFullscreen, toggleSheet, toggleCurriculum, runKey: bindings.run.label, submitKey: bindings.submit.label, mod: MOD};
})();
