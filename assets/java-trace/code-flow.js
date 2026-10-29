// 코드 흐름 보기 dialog. The Rust side traces the editor's current code (src/java_trace.rs) and hands
// the core trace document to show(); the core TraceView (window.MqTraceView) draws every step.
// Closing only destroys the view: the editor, output and progress are never touched here.
(() => {
  if (window.mqCodeFlow) return;
  let dialog = null, view = null, opener = null, current = 0;
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
      <p class="code-flow-note">지금 편집기의 코드를 수업과 같은 JDK 25로 실행하며 한 단계씩 기록했어요. 채점과 진도에는 영향이 없어요. ←·→ 키로도 움직여요.</p></div>
      <button type="button" class="code-flow-close">닫기</button></header>
      <div class="code-flow-status" role="status" aria-live="polite"></div>
      <div class="code-flow-view"></div>`;
    dialog.querySelector('.code-flow-close').addEventListener('click', () => dialog.close());
    dialog.addEventListener('close', () => {
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
      if (!d.open) { opener = document.activeElement; d.showModal(); }
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
        return true;
      }
      status(STATUS[doc.status] || '', doc.status === 'internal_error');
      const root = dialog.querySelector('.code-flow-view');
      view = new window.MqTraceView(root, doc);
      return true;
    },
    fail(token, message) {
      if (token !== current || !dialog?.open) return false;
      status(message, true);
      return true;
    },
    close() { if (dialog?.open) dialog.close(); },
    isOpen() { return !!dialog?.open; },
    /** Test and narration hook: the step on screen (1-based) and its source line. */
    position() { return view ? { step: view.index + 1, steps: view.trace.length, line: view.trace[view.index]?.line } : null; },
  };
})();
