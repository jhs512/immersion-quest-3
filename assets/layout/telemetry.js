// Forward error locations only. No exception messages, source, URLs or input values.
(() => {
  window.mqTelemetryCleanup?.();
  let count = 0;
  let period = Date.now();
  const names = new Set(['TypeError', 'RangeError', 'SyntaxError', 'ReferenceError', 'URIError', 'EvalError', 'AggregateError']);
  const send = (event, kind) => {
    if (Date.now() - period >= 60000) { period = Date.now(); count = 0; }
    if (count >= 20) return;
    count++;
    try {
      const candidate = kind === 'error' ? event.error : event.reason;
      const name = names.has(candidate?.name) ? candidate.name : 'Error';
      const basename = typeof event.filename === 'string' ? event.filename.split(/[\\/]/).pop() : '';
      const file = /^[a-zA-Z0-9_.-]{1,80}\.js$/.test(basename) ? basename : '';
      const root = document.querySelector('.repository-task');
      const id = key => { const value = root?.dataset[key] || ''; return /^[a-zA-Z0-9_-]{1,100}$/.test(value) ? value : ''; };
      dioxus.send({kind, name, file, course:id('courseId'), lesson:id('lessonId'), task:id('taskId'), line: Number.isSafeInteger(event.lineno) && event.lineno > 0 ? Math.min(event.lineno, 1000000) : 0,
        column: Number.isSafeInteger(event.colno) && event.colno > 0 ? Math.min(event.colno, 1000000) : 0});
    } catch (_) { /* Diagnostics must never cause another application error. */ }
  };
  const onError = event => send(event, 'error');
  const onRejection = event => send(event, 'unhandledrejection');
  window.addEventListener('error', onError);
  window.addEventListener('unhandledrejection', onRejection);
  window.mqTelemetryCleanup = () => {
    window.removeEventListener('error', onError);
    window.removeEventListener('unhandledrejection', onRejection);
  };
})();
