// Lets a narration act on a lesson web preview: the preview is a sandboxed srcdoc iframe with an
// opaque origin, so the parent cannot reach its DOM. The tutor posts {type:'mq3-web-action'} with
// a selector and a click or fill; the page performs it like a user (a fill uses the native value
// setter and an input event, which React's controlled inputs listen to) and replies with the text
// of the element to read (or one computed style). Only messages from the embedding page are accepted.
(() => {
  window.addEventListener('message', event => {
    const message = event.data;
    if (event.source !== window.parent || !message || message.type !== 'mq3-web-action') return;
    const element = typeof message.selector === 'string' ? document.querySelector(message.selector) : null;
    if (element && message.do === 'click') element.click();
    if (element && message.do === 'fill') {
      const setter = Object.getOwnPropertyDescriptor(Object.getPrototypeOf(element), 'value')?.set;
      if (setter) setter.call(element, String(message.value ?? '')); else element.value = String(message.value ?? '');
      element.dispatchEvent(new Event('input', {bubbles: true}));
    }
    // Let React re-render before the result is read.
    setTimeout(() => {
      const read = document.querySelector(typeof message.read === 'string' ? message.read : message.selector);
      const text = !read ? null
        : typeof message.style === 'string' ? getComputedStyle(read)[message.style]
        : ('value' in read && /^(INPUT|TEXTAREA)$/.test(read.tagName)) ? read.value : read.textContent;
      window.parent.postMessage({type: 'mq3-web-result', id: message.id, ok: !!element, text}, '*');
    }, 80);
  });
})();
