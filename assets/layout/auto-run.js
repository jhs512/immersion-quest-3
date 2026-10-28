// 관리자 자동 풀이 (administrator auto-run), browser side. The run itself lives in Rust
// (src/player_ui.rs): it plays each step's narration, solves the step with the ordinary input,
// run and submit buttons, and records through the ordinary progress path. This file only
//  - maps the start chord, Space and Esc to the run's own buttons, which exist only for an
//    account GitHub reports as able to edit the course,
//  - keeps stray input out of the task while the run is working,
//  - types the step's terminal actions into the learner's real terminal at the current
//    narration speed (the same 1.5/rate scaling the narration's code typing uses).
(function () {
  'use strict';
  if (globalThis.molipAutoRun || typeof document === 'undefined') return;
  const mac = /mac/i.test(navigator.platform);
  const CHORD = mac ? 'Control+Option+Shift+A' : 'Ctrl+Alt+Shift+A';
  let state = {active: false, paused: false, generation: 0};
  const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
  const rate = () => { const value = Number(globalThis.molipVoice?.rate); return value > 0 ? value : 1.5; };
  const current = generation => state.active && state.generation === generation;

  // Wait `ms` (a delay authored for 1.5×) at the current narration speed. The speed and the pause
  // are read again every slice, so a change during the wait applies to the rest of it.
  async function pace(ms, generation) {
    let done = 0;
    while (done < 1) {
      if (!current(generation)) return false;
      if (state.paused) { await sleep(40); continue; }
      const full = ms * 1.5 / rate();
      const slice = Math.min(20, (1 - done) * full);
      await sleep(slice);
      done += full > 0 ? slice / full : 1;
    }
    return current(generation);
  }
  // Wait for a real signal. Paused time does not count toward the deadline, and the deadline is
  // never scaled by the speed: a slow process gets the same real time at any speed.
  async function until(predicate, generation, seconds, what) {
    let waited = 0;
    while (true) {
      if (!current(generation)) return false;
      if (predicate()) return true;
      if (!state.paused) waited += 30;
      if (waited > seconds * 1000) throw new Error(`${what}을(를) 확인하지 못했어요.`);
      await sleep(30);
    }
  }
  function shellArgument(value) {
    const text = String(value);
    if (text && [...text].every(c => /[\p{L}\p{N}_./:=+@%^-]/u.test(c))) return text;
    return `"${text.replace(/\\/g, '\\\\').replace(/\$/g, '\\$').replace(/`/g, '\\`').replace(/"/g, '\\"')}"`;
  }
  const terminal = () => globalThis.mq3GitTerminal;
  const owner = () => document.querySelector('#git-student-terminal')?.dataset.terminalSession;

  async function command(text, generation, seconds = 120) {
    const bridge = terminal(), session = owner();
    if (!bridge || !session) throw new Error('실습 터미널이 없어요.');
    const before = bridge.text(session).trimEnd();
    const typed = await bridge.typeCommand(text, session, ms => pace(ms, generation));
    if (!typed) { if (!current(generation)) return false; throw new Error('터미널이 바뀌어 명령을 입력하지 못했어요.'); }
    return until(() => { const after = bridge.text(session).trimEnd(); return after !== before && /(?:\$|>)\s*$/.test(after); },
      generation, seconds, `「${text}」 명령의 완료`);
  }

  async function act(action, generation) {
    const bridge = terminal();
    switch (action.action) {
      case 'bash_command':
        if (typeof action.command !== 'string' || !action.command || /[\r\n\0]/.test(action.command)) throw new Error('Bash 명령을 확인하세요.');
        return command(action.command, generation, Math.min(900, Math.max(120, Number(action.wait_seconds) || 120)));
      case 'inspect_folder':
        if (!['pwd', 'ls'].includes(action.command)) throw new Error('폴더 확인 명령을 확인하세요.');
        return command(action.command, generation);
      case 'write_memo': return command(`echo "${action.content}" > memo.txt`, generation);
      case 'read_memo': return command('cat memo.txt', generation);
      case 'git_command':
        if (!Array.isArray(action.args) || !action.args.length) throw new Error('Git 명령을 확인하세요.');
        return command(`git ${action.args.map(shellArgument).join(' ')}`, generation);
      case 'vim_open': return command('vim memo.txt', generation);
      case 'vim_wait':
        return until(() => { const p = bridge?.vimState(owner()); return !!p && (action.passed ? p.passed : !!p.state); }, generation, 60, 'Vim 상태');
      case 'vim_keys': {
        if (typeof action.keys !== 'string') throw new Error('Vim 키 입력을 확인하세요.');
        const typed = await bridge?.typeKeys(action.keys, owner(), ms => pace(ms, generation));
        if (!typed) { if (!current(generation)) return false; throw new Error('Vim 편집기가 바뀌어 키를 입력하지 못했어요.'); }
        if (!action.wait_prompt) return pace(100, generation);
        const direct = document.querySelector('#git-student-terminal')?.dataset.vim === 'true';
        return until(() => direct ? !!bridge.vimState(owner())?.state?.exited : /\$\s*$/.test(bridge.text(owner()).trimEnd()), generation, 60, 'Vim 종료');
      }
      case 'patch_code': {
        // Main.java of a Java terminal step, or a file of a Compose step: the same edit the
        // narration shows, made in the learner's own editor, which saves the file into the
        // terminal's folder through its ordinary input handler.
        const name = action.file || 'Main.java';
        if (action.file) {
          const tab = [...document.querySelectorAll('[data-editor-tab]')].find(t => t.dataset.editorTab === action.file && t.getClientRects().length);
          if (!tab) throw new Error(`${name} 편집기 탭을 찾지 못했어요.`);
          if (tab.getAttribute('aria-selected') !== 'true') tab.click();
          if (!await until(() => document.querySelector(`textarea[data-editor-file="${CSS.escape(action.file)}"]`) && globalThis.molipCodeEditors?.getValue()?.includes(action.before), generation, 10, `${name} 편집기`)) return false;
        }
        const editors = globalThis.molipCodeEditors;
        const source = editors?.getValue();
        if (source == null) throw new Error(`${name} 편집기를 찾지 못했어요.`);
        if (source.split(action.before).length !== 2) throw new Error(`${name}에서 고칠 부분을 하나로 찾지 못했어요.`);
        editors.setValue(source.replace(action.before, action.after));
        return pace(250, generation);
      }
      default: throw new Error(`자동 풀이가 모르는 동작이에요: ${action.action}`);
    }
  }

  // Replay a step's terminal actions in order. Resolves {ok}, {cancelled} or {error, index}.
  async function solveTerminal(actions, generation) {
    for (const [index, action] of (Array.isArray(actions) ? actions : []).entries()) {
      try {
        const done = await act(action, generation);
        if (done === false || !current(generation)) return {cancelled: true, index};
      } catch (error) { return {error: String(error?.message || error), index}; }
    }
    return current(generation) ? {ok: true} : {cancelled: true};
  }

  function sync(next) {
    state = {active: !!next?.active, paused: !!next?.paused, generation: Number(next?.generation) || 0};
    document.documentElement.dataset.autoRun = state.active ? (state.paused ? 'paused' : 'running') : 'off';
  }
  // Esc acts here first: every browser-side wait of the run ends now, before Rust hears of it.
  function cancelNow() {
    if (!state.active) return false;
    state = {...state, active: false, paused: false};
    const explanation = document.querySelector('.repository-task')?.dataset.explanationSession;
    if (explanation) (globalThis.mq3CancelledExplanations ??= new Set()).add(explanation);
    globalThis.molipAgent?.stop();
    document.getElementById('auto-run-stop')?.click();
    return true;
  }

  const inEditable = target => target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement || target instanceof HTMLSelectElement
    || (target instanceof Element && (target.isContentEditable || !!target.closest('.cm-editor, .xterm')));
  const isChord = event => event.ctrlKey && event.altKey && event.shiftKey && !event.metaKey && event.code === 'KeyA';
  window.addEventListener('keydown', event => {
    if (event.isComposing || event.keyCode === 229) return;
    if (isChord(event)) {
      event.preventDefault(); event.stopImmediatePropagation();
      if (event.repeat || state.active) return;
      const start = document.getElementById('auto-run-start');
      if (start && !start.disabled) start.click();
      else if (!start && document.querySelector('.repository-study')) globalThis.molipToast?.('자동 풀이는 코스 저장소를 편집할 수 있는 관리자 계정에서만 쓸 수 있어요.');
      return;
    }
    if (!state.active) return;
    if (event.key === 'Escape') { event.preventDefault(); event.stopImmediatePropagation(); if (!event.repeat) cancelNow(); return; }
    // Inside the task the learner's typing is held off during the run, so Space there pauses too
    // (focus often sits in the terminal). Buttons, links and selects keep their own Space.
    const inTask = event.target instanceof Element && !!event.target.closest('.repository-task');
    if (event.key === ' ' && !event.ctrlKey && !event.metaKey && !event.altKey && (inTask || !inEditable(event.target))
      && !(event.target instanceof Element && event.target.closest('button:not(:disabled),a,select,summary'))) {
      event.preventDefault(); event.stopImmediatePropagation();
      if (!event.repeat) document.getElementById('auto-run-pause')?.click();
    }
  }, {capture: true});

  // While the run works, the learner's own clicks and typing inside the task would race it.
  // Speed, the run control, narration voice keys and text selection stay available.
  const guard = event => {
    if (!state.active || !event.isTrusted || !(event.target instanceof Element)) return;
    if (!event.target.closest('.repository-task') || event.target.closest('.narration-speed, .auto-run-control')) return;
    if (event.type === 'keydown') {
      if (['Tab', 'Escape', 'Home', 'End', 'PageUp', 'PageDown'].includes(event.key)) return;
      if ((event.ctrlKey || event.metaKey) && (event.key.startsWith('Arrow') || ['a', 'c'].includes(event.key.toLowerCase()))) return;
      if (event.key.startsWith('Arrow') && !inEditable(event.target)) return;
    }
    event.preventDefault(); event.stopImmediatePropagation();
  };
  for (const name of ['click', 'keydown', 'beforeinput', 'paste', 'drop']) window.addEventListener(name, guard, {capture: true});

  globalThis.molipAutoRun = {sync, solveTerminal, pace, cancelNow, shellArgument, chord: CHORD, get state() { return {...state}; }};
})();
