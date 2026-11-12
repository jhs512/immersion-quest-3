// A 「복사」 button on each code block of a problem, so prepared options such as
// --endpoint-url "$LAB_ENDPOINT" can be pasted into the terminal at any time.
// The text goes to the app's native clipboard (src/main.rs), like 「수업 링크 복사」: the macOS
// WebView neither copies a selected range nor settles navigator.clipboard for this button.
(() => {
  if (window.molipCodeCopy) return;
  const pending = new Map();
  let next = 0;
  const nativeCopy = text => new Promise(resolve => {
    const token = ++next;
    pending.set(token, resolve);
    dioxus.send({ token, text });
    // No answer means no native bridge (e.g. a page without the app): try the WebView copy.
    setTimeout(() => { if (pending.delete(token)) resolve(null); }, 3000);
  });
  const webCopy = async text => {
    const area = document.createElement('textarea');
    area.value = text;
    area.setAttribute('readonly', '');
    area.style.cssText = 'position:fixed;left:-9999px;top:0;opacity:0';
    document.body.appendChild(area);
    area.select();
    let copied = false;
    try { copied = document.execCommand('copy'); } catch (_) { copied = false; }
    area.remove();
    return copied;
  };
  const copyText = async text => {
    const native = typeof dioxus === 'object' ? await nativeCopy(text) : null;
    return native ?? webCopy(text);
  };
  // Called by the app with the native clipboard's result for one request.
  const resolve = (token, copied) => {
    pending.get(token)?.(copied);
    pending.delete(token);
  };
  const decorate = root => {
    for (const block of root.querySelectorAll('.problem-pane .markdown pre')) {
      if (block.querySelector(':scope > .code-copy')) continue;
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'code-copy';
      button.textContent = '복사';
      button.setAttribute('aria-label', '코드 복사');
      button.addEventListener('click', async event => {
        event.stopPropagation();
        const code = block.querySelector('code')?.textContent ?? block.textContent.replace(/복사$/, '');
        const copied = await copyText(code.replace(/\n$/, ''));
        button.textContent = copied ? '복사했어요' : '복사하지 못했어요';
        setTimeout(() => { button.textContent = '복사'; }, 1600);
      });
      block.appendChild(button);
    }
  };
  decorate(document);
  new MutationObserver(() => decorate(document)).observe(document.body, { childList: true, subtree: true });
  window.molipCodeCopy = { copyText, decorate, resolve };
})();
