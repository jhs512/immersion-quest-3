// Lets a narration act on a lesson web preview: the preview is a sandboxed srcdoc iframe with an
// opaque origin, so the parent cannot reach its DOM. The tutor posts {type:'mq3-web-action'} with
// a selector and a click or fill; the page performs it like a user (a fill uses the native value
// setter and an input event, which React's controlled inputs listen to) and replies with the text
// of the element to read (or one computed style). Only messages from the embedding page are accepted.
(() => {
  // Keep the preview's own console, including logs from later clicks. Never turn
  // rendered page text into a log. Buffer until the parent has mounted its listener.
  const lines = [];
  const publish = () => window.parent.postMessage({type:'mq3-web-console', lines:[...lines]}, '*');
  const format = value => {try {return typeof value === 'string' ? value : JSON.stringify(value) ?? String(value);} catch {return String(value);}};
  const log = (kind, values) => {lines.push(`[${kind}] ${values.map(format).join(' ')}`);if(lines.length>200)lines.shift();publish();};
  for (const kind of ['log','info','warn','error','debug']) {
    const original = console[kind].bind(console);
    console[kind] = (...values) => {original(...values);log(kind, values);};
  }
  addEventListener('error', event=>log('error',[event.message]));
  addEventListener('unhandledrejection', event=>log('error',[event.reason?.message ?? event.reason]));
  let selector = '', overlays = [], animation = 0;
  function clearHighlight() {
    cancelAnimationFrame(animation);animation=0;
    overlays.forEach(node=>node.remove());overlays=[];
  }
  function drawHighlight() {
    overlays.forEach(node=>node.remove());overlays=[];
    let elements=[];
    try {elements=[...document.querySelectorAll(selector)];} catch {}
    for(const element of elements) {
      const r=element.getBoundingClientRect();if(!r.width||!r.height)continue;
      const box=document.createElement('div');box.dataset.mq3WebHighlight='';
      box.style.cssText=`all:initial;position:fixed;pointer-events:none;z-index:2147483647;box-sizing:border-box;left:${r.left-3}px;top:${r.top-3}px;width:${r.width+6}px;height:${r.height+6}px;border:3px solid #a78bfa;border-radius:4px;box-shadow:0 0 0 2px #5b21b6;`;
      document.documentElement.append(box);overlays.push(box);
    }
    animation=requestAnimationFrame(drawHighlight);
  }
  window.addEventListener('message', event => {
    const message = event.data;
    if (event.source !== window.parent || !message) return;
    if(message.type==='mq3-web-console-request'){publish();return;}
    if(message.type==='mq3-web-highlight') {
      clearHighlight();selector=typeof message.selector==='string'?message.selector:'';
      if(selector){try {document.querySelector(selector)?.scrollIntoView({block:'nearest',inline:'nearest'});}catch{}drawHighlight();}
      return;
    }
    if(message.type !== 'mq3-web-action') return;
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
