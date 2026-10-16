// Keep Korean (and any other IME) composition intact in controlled inputs.
//
// Dioxus writes an input's value back into the DOM on every render. While an IME is still
// composing a syllable, that write cancels the composition, so typing 안녕 ends up as 안ㄴ녕.
// Rather than fixing every input separately, the value setter of inputs and textareas is
// wrapped once: while an element has an open composition, programmatic writes are skipped.
// The composition's own input event already carried the text to the Rust side, and the next
// render after compositionend writes the final value as usual.
(function () {
  'use strict';
  if (globalThis.molipIme || typeof document === 'undefined') return;
  const composing = new WeakSet();
  document.addEventListener('compositionstart', event => { if (event.target) composing.add(event.target); }, true);
  document.addEventListener('compositionend', event => { if (event.target) composing.delete(event.target); }, true);
  let patched = 0;
  for (const proto of [HTMLInputElement.prototype, HTMLTextAreaElement.prototype]) {
    const original = Object.getOwnPropertyDescriptor(proto, 'value');
    if (!original || !original.set) continue;
    Object.defineProperty(proto, 'value', {
      configurable: true,
      enumerable: original.enumerable,
      get() { return original.get.call(this); },
      set(value) { if (!composing.has(this)) original.set.call(this, value); },
    });
    patched += 1;
  }
  globalThis.molipIme = { isComposing: element => composing.has(element), patched };
})();
