// 코드 흐름 보기 dialog. The Rust side traces the editor's current code (src/java_trace.rs) and hands
// the core trace document to show(); the core TraceView (window.MqTraceView) draws every step.
// Closing only destroys the view: the editor, output and progress are never touched here.
// A narration (agent.js `code_flow`) opens the same dialog without a modal backdrop, so its caption,
// spotlight and 멈춤 stay usable, and moves the view to the trace step it explains.
(() => {
  if (window.mqCodeFlow) return;
  let dialog = null, view = null, opener = null, current = 0, narrated = false, pendingNarration = false, ownClose = false, state = 'closed';
  const STATUS = {
    compile_error: '컴파일 오류가 있어 실행 흐름을 기록하지 못했어요. 아래 줄을 고친 뒤 다시 열어 보세요.',
    no_main: '실행을 시작할 main 메서드를 찾지 못했어요.',
    internal_error: '코드 흐름 도구에서 문제가 생겼어요.',
    uncaught_exception: '처리되지 않은 예외로 실행이 멈췄어요. 멈춘 단계까지 따라가 볼 수 있어요.',
    step_limit: '실행 단계가 많아 앞부분만 기록했어요.',
  };
  const build = () => {
    if (dialog) return dialog;
    dialog = document.createElement('dialog');
    dialog.id = 'code-flow-dialog';
    dialog.className = 'code-flow-dialog';
    dialog.setAttribute('aria-labelledby', 'code-flow-title');
    dialog.innerHTML = `<header><div><h2 id="code-flow-title">코드 흐름 보기</h2>
      <p class="code-flow-note">지금 편집기의 코드를 수업 채점과 같은 실행 환경으로 실행하며 한 단계씩 기록했어요. 채점과 진도에는 영향이 없어요. ←·→ 키로도 움직여요.</p></div>
      <button type="button" class="code-flow-close">닫기</button></header>
      <div class="code-flow-status" role="status" aria-live="polite"></div>
      <div class="code-flow-view"></div>`;
    dialog.querySelector('.code-flow-close').addEventListener('click', () => dialog.close());
    // Without a modal, Escape does not close a dialog by itself.
    dialog.addEventListener('keydown', (event) => { if (event.key === 'Escape' && narrated) { event.preventDefault(); dialog.close(); } });
    dialog.addEventListener('close', () => {
      // The learner closing a narrated view ends that narration, as its 멈춤 would.
      if (narrated && !ownClose) document.querySelector('.repository-task [data-explanation-stop]:not(:disabled)')?.click();
      narrated = false; ownClose = false; state = 'closed';
      dialog.classList.remove('is-narrated');
      current += 1;
      view?.destroy?.(); view = null;
      dialog.querySelector('.code-flow-view').replaceChildren();
      if (opener?.isConnected) opener.focus();
      opener = null;
    });
    document.body.append(dialog);
    return dialog;
  };
  const status = (text, error = false, problems = []) => {
    const box = build().querySelector('.code-flow-status');
    box.className = 'code-flow-status' + (error ? ' is-error' : '');
    box.replaceChildren();
    if (text) box.append(document.createTextNode(text));
    if (problems.length) {
      const list = document.createElement('ul');
      list.className = 'code-flow-problems';
      for (const p of problems) {
        const item = document.createElement('li');
        item.textContent = (p.line > 0 ? `${p.line}행: ` : '') + p.message;
        list.append(item);
      }
      box.append(list);
    }
  };
  window.mqCodeFlow = {
    /** Opens the dialog for a new request and returns its token; older results are ignored. */
    loading() {
      const d = build();
      const forNarration = pendingNarration;
      pendingNarration = false;
      if (d.open && narrated !== forNarration) { ownClose = true; d.close(); }
      if (!d.open) {
        opener = document.activeElement;
        narrated = forNarration;
        d.classList.toggle('is-narrated', narrated);
        d.querySelector('.code-flow-note').textContent = narrated
          ? '해설이 지금 편집기의 코드를 수업 채점과 같은 실행 환경으로 실행해 기록한 단계를 차례로 보여 줘요. 채점과 진도에는 영향이 없어요. 닫으면 해설도 멈춰요.'
          : '지금 편집기의 코드를 수업 채점과 같은 실행 환경으로 실행하며 한 단계씩 기록했어요. 채점과 진도에는 영향이 없어요. ←·→ 키로도 움직여요.';
        if (narrated) d.show(); else d.showModal();
      }
      state = 'loading';
      current += 1;
      view?.destroy?.(); view = null;
      d.querySelector('.code-flow-view').replaceChildren();
      status('코드를 실행하며 흐름을 기록하고 있어요. 처음에는 도구를 준비하느라 조금 더 걸려요.');
      return current;
    },
    show(token, doc) {
      if (token !== current || !dialog?.open) return false;
      const problems = (doc.problems || []).filter((p) => p.error);
      if (doc.status === 'compile_error' || !doc.trace?.length) {
        const text = STATUS[doc.status] || '기록한 실행 단계가 없어요.';
        status(doc.message && doc.status !== 'compile_error' ? `${text} ${doc.message}` : text, true, problems);
        state = 'error';
        return true;
      }
      status(STATUS[doc.status] || '', doc.status === 'internal_error');
      // Which real runtime recorded it (JDK 25 for Java, the course Python for Python).
      const runtime = doc.language === 'python' ? `수업과 같은 Python ${doc.runtime || ''}`.trim() : '수업과 같은 JDK 25';
      const note = dialog.querySelector('.code-flow-note');
      if (note) note.textContent = note.textContent.replace('수업 채점과 같은 실행 환경', runtime);
      const root = dialog.querySelector('.code-flow-view');
      view = new window.MqTraceView(root, doc);
      state = 'shown';
      return true;
    },
    fail(token, message) {
      if (token !== current || !dialog?.open) return false;
      status(message, true);
      state = 'error';
      return true;
    },
    close() { if (dialog?.open) dialog.close(); },
    isOpen() { return !!dialog?.open; },
    /** Test and narration hook: the step on screen (1-based) and its source line. */
    position() { return view ? { step: view.index + 1, steps: view.trace.length, line: view.trace[view.index]?.line } : null; },
    /** Narration: the next loading() opens without a modal backdrop. */
    narrate() { pendingNarration = true; },
    /** 'closed' | 'loading' | 'shown' | 'error', with the status text that explains an error. */
    state() { return { state, narrated, message: dialog?.querySelector('.code-flow-status')?.textContent.trim() || '' }; },
    /** Narration: shows the nth (1-based) recorded step on `line`, of `event` if given. Same rule as
     *  the lesson validator's replay (examples/validate_redesigned_lesson.rs), so a step that the
     *  validator found on the real trace is the step the learner sees. */
    seek({ line, event = null, nth = 1 }) {
      if (!view) return null;
      let seen = 0;
      const index = view.trace.findIndex((step) => step.line === line && (!event || step.event === event) && ++seen === nth);
      if (index < 0) return null;
      view.goTo(index);
      return this.position();
    },
    /** Narration end or the narration's next edit: closes only a view that a narration opened. */
    closeNarrated() { if (dialog?.open && narrated) { ownClose = true; dialog.close(); } },
  };
})();
