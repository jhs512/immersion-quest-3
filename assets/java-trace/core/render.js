// Renders a trace document (docs/trace-format.md) as a stepper: code, call stack, objects, arrows.
// No dependencies. All DOM queries are scoped to the view root so several views can coexist.

import { highlightLines } from './highlight.js';

const EVENT_LABELS = {
  call: '메서드 호출',
  step_line: '줄 실행',
  return: '반환',
  exception: '예외 전파',
  uncaught_exception: '처리되지 않은 예외',
  instruction_limit_reached: '단계 제한 도달',
};
// MQ: a Python trace (src/python_trace.rs) has functions, not methods, and a module-level frame.
const PYTHON_EVENT_LABELS = { ...EVENT_LABELS, call: '함수 호출', exception: '예외 발생' };

const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const h = (tag, cls, html) => { const el = document.createElement(tag); if (cls) el.className = cls; if (html != null) el.innerHTML = html; return el; };

export function isRef(v) { return Array.isArray(v) && v[0] === 'REF'; }

/** Inline rendering of a primitive/string value, or a reference stub that the arrow layer links. */
export function valueHtml(v) {
  if (v === null || v === undefined) return '<span class="v-null">null</span>';
  if (isRef(v)) return `<span class="v-ref" data-ref="${v[1]}"></span>`;
  if (Array.isArray(v)) {
    if (v[0] === 'CHAR') return `<span class="v-char">'${esc(v[1])}'</span>`;
    if (v[0] === 'LONG') return `<span class="v-num">${esc(v[1])}L</span>`;
    if (v[0] === 'SPECIAL_FLOAT') return `<span class="v-num">${esc(v[1])}</span>`;
    // MQ (C traces, src/c_trace.rs): a pointer to a named stack/global cell, and a value the tracer could
    // not observe or will not follow (freed memory, unknown address, unsupported type) — shown as text.
    if (v[0] === 'C_PTR') return `<span class="v-ptr">→ ${esc(v[1])}</span>`;
    if (v[0] === 'C_NOTE') return `<span class="v-note">${esc(v[1])}</span>`;
    if (v[0] === 'PRESENT') return '<span class="v-null" title="HashSet이 모든 값 자리에 넣는 공용 표식 객체">PRESENT</span>';
    return `<span class="v-num">${esc(JSON.stringify(v))}</span>`;
  }
  if (typeof v === 'string') return `<span class="v-str">"${esc(v)}"</span>`;
  if (typeof v === 'boolean') return `<span class="v-bool">${v}</span>`;
  return `<span class="v-num">${esc(v)}</span>`;
}

const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);

export class TraceView {
  constructor(root, doc, options = {}) {
    this.root = root;
    this.doc = doc;
    this.trace = doc.trace || [];
    this.lines = (doc.code || '').replace(/\r\n?/g, '\n').split('\n');
    this.options = { hideMainArgs: true, ...options };
    this.index = 0;
    this.build();
    this.goTo(0);
    this.onResize = () => this.drawArrows();
    window.addEventListener('resize', this.onResize);
    // Layout can settle after the first draw (fonts, pane resize without a window resize event,
    // scrollbars appearing): redraw whenever the memory panel or its columns change size.
    this.resizeObserver = new ResizeObserver(() => this.drawArrows());
    for (const el of [this.memory, this.framesCol, this.heapCol]) this.resizeObserver.observe(el);
    document.fonts?.ready?.then(() => this.drawArrows());
    this.onKey = (e) => {
      if (e.target?.closest?.('textarea, input, select')) return;
      if (e.key === 'ArrowRight') { this.goTo(this.index + 1); e.preventDefault(); }
      if (e.key === 'ArrowLeft') { this.goTo(this.index - 1); e.preventDefault(); }
    };
    document.addEventListener('keydown', this.onKey);
  }

  destroy() {
    window.removeEventListener('resize', this.onResize);
    this.resizeObserver?.disconnect();
    document.removeEventListener('keydown', this.onKey);
    this.root.replaceChildren();
  }

  build() {
    this.root.replaceChildren();
    const left = h('div', 'tv-left');
    this.codeEl = h('div', 'tv-code');
    const highlighted = highlightLines(this.lines.join('\n'));
    this.lines.forEach((text, i) => {
      const row = h('div', 'tv-line');
      row.dataset.line = i + 1;
      row.innerHTML = `<span class="tv-gutter"><span class="tv-arrow"></span></span><span class="tv-ln">${i + 1}</span><span class="tv-src">${highlighted[i] || ' '}</span>`;
      this.codeEl.append(row);
    });
    left.append(this.codeEl);

    const nav = h('div', 'tv-nav');
    nav.innerHTML = `
      <div class="tv-legend"><span class="tv-arrow prev"></span> 방금 실행한 줄 <span class="tv-arrow next"></span> 다음에 실행할 줄</div>
      <input type="range" class="tv-slider" min="0" max="${Math.max(0, this.trace.length - 1)}" value="0" aria-label="단계">
      <div class="tv-buttons">
        <button data-go="first">« 처음</button><button data-go="prev">‹ 이전</button>
        <button data-go="next">다음 ›</button><button data-go="last">마지막 »</button>
      </div>
      <div class="tv-position"></div>`;
    nav.querySelector('.tv-slider').addEventListener('input', (e) => this.goTo(Number(e.target.value)));
    nav.querySelectorAll('button').forEach((b) => b.addEventListener('click', () => {
      const go = b.dataset.go;
      this.goTo(go === 'first' ? 0 : go === 'last' ? this.trace.length - 1 : this.index + (go === 'next' ? 1 : -1));
    }));
    left.append(nav);
    this.nav = nav;

    const right = h('div', 'tv-right');
    this.banner = h('div', 'tv-banner');
    this.banner.hidden = true;
    this.stdoutEl = h('pre', 'tv-stdout');
    const stdoutWrap = h('div', 'tv-stdout-wrap', '<div class="tv-title">출력</div>');
    stdoutWrap.append(this.stdoutEl);
    this.memory = h('div', 'tv-memory');
    this.framesCol = h('div', 'tv-frames', '<div class="tv-title">호출 스택</div>');
    this.heapCol = h('div', 'tv-heap', '<div class="tv-title">객체</div>');
    this.svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    this.svg.classList.add('tv-arrows');
    this.svg.innerHTML = `<defs>
      <marker id="tv-head" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z"/></marker>
      <marker id="tv-head-dim" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z"/></marker>
    </defs>`;
    this.memory.append(this.framesCol, this.heapCol, this.svg);
    right.append(this.banner, stdoutWrap, this.memory);

    this.root.append(left, right);
  }

  goTo(i) {
    if (!this.trace.length) return;
    this.index = Math.max(0, Math.min(this.trace.length - 1, i));
    const step = this.trace[this.index];
    const prev = this.index > 0 ? this.trace[this.index - 1] : null;
    this.renderCode(step, prev);
    this.renderNav(step);
    this.renderStdout(step);
    this.renderFrames(step, prev);
    this.renderHeap(step, prev);
    this.drawArrows();
    setTimeout(() => this.drawArrows(), 50); // once more after layout settles
  }

  renderCode(step, prev) {
    const nextLine = step.line;
    const prevLine = prev ? prev.line : 0;
    this.codeEl.querySelectorAll('.tv-line').forEach((row) => {
      const n = Number(row.dataset.line);
      row.classList.toggle('is-next', n === nextLine);
      row.classList.toggle('is-prev', n === prevLine && n !== nextLine);
      row.classList.toggle('is-error', n === nextLine && step.event.endsWith('exception'));
    });
    const target = this.codeEl.querySelector(`.tv-line[data-line="${nextLine}"]`);
    if (target) {
      const box = this.codeEl.getBoundingClientRect(), r = target.getBoundingClientRect();
      if (r.top < box.top + 40 || r.bottom > box.bottom - 40) target.scrollIntoView({ block: 'center' });
    }
  }

  renderNav(step) {
    this.nav.querySelector('.tv-slider').value = this.index;
    const label = (this.doc.language === 'python' || this.doc.language === 'c' ? PYTHON_EVENT_LABELS : EVENT_LABELS)[step.event] || step.event;
    this.nav.querySelector('.tv-position').innerHTML =
      `<strong>${this.index + 1} / ${this.trace.length}</strong> 단계 · ${esc(label)}` +
      (step.func_name ? ` · <code>${esc(this.frameTitle(step.stack_to_render.at(-1)))}</code>` : '') +
      // C: declarations have no stop of their own in the compiler's line table; say they ran before this one.
      (step.also_ran_lines?.length ? ` · <span class="tv-also">선언 ${step.also_ran_lines.join(', ')}행도 이 단계 전에 실행됨</span>` : '');
    this.nav.querySelector('[data-go="first"]').disabled = this.nav.querySelector('[data-go="prev"]').disabled = this.index === 0;
    this.nav.querySelector('[data-go="last"]').disabled = this.nav.querySelector('[data-go="next"]').disabled = this.index === this.trace.length - 1;
    if (step.exception_msg) {
      this.banner.hidden = false;
      this.banner.className = 'tv-banner ' + (step.event === 'uncaught_exception' ? 'is-fatal' : 'is-warn');
      this.banner.textContent = (step.event === 'uncaught_exception' ? '처리되지 않은 예외: ' : '예외 발생: ') + step.exception_msg;
    } else if (step.event === 'instruction_limit_reached') {
      this.banner.hidden = false;
      this.banner.className = 'tv-banner is-warn';
      this.banner.textContent = `단계 제한(${this.doc.stepBudget ?? ''}단계)에 도달해 실행을 멈췄습니다.`;
    } else this.banner.hidden = true;
  }

  renderStdout(step) {
    const text = (step.stdout || '').replace(/\r\n?/g, '\n');
    this.stdoutEl.textContent = text;
    this.stdoutEl.classList.toggle('is-empty', !text);
    this.stdoutEl.scrollTop = this.stdoutEl.scrollHeight;
  }

  frameTitle(frame) {
    if (!frame) return '';
    let name = frame.func_name;
    if (name === '<module>' && this.doc.language === 'python') return '전역 코드';
    if (name === '<init>') name = `${frame.class}()`;
    else if (name === '<clinit>') name = `${frame.class} static 초기화`;
    else if (name.startsWith('lambda$')) name = `${frame.class} 람다`;
    else if (frame.class && frame.func_name !== 'main') name = `${frame.class}.${name}`;
    return name;
  }

  renderFrames(step, prev) {
    const col = this.framesCol;
    col.replaceChildren(h('div', 'tv-title', '호출 스택'));
    const prevFrames = new Map((prev?.stack_to_render || []).map((f) => [f.frame_id, f]));

    if (step.ordered_globals?.length) {
      const box = h('div', 'tv-frame tv-globals');
      box.innerHTML = `<div class="tv-frame-title">${this.doc.language === 'c' ? '전역 변수' : 'static 변수'}</div>`;
      const table = h('table');
      for (const key of step.ordered_globals) {
        const changed = prev && !same(prev.globals?.[key], step.globals[key]);
        table.append(this.row(key, step.globals[key], changed));
      }
      box.append(table);
      col.append(box);
    }

    const frames = step.stack_to_render || [];
    frames.forEach((frame, i) => {
      const box = h('div', 'tv-frame' + (i === frames.length - 1 ? ' is-current' : ''));
      box.dataset.frame = frame.frame_id;
      box.innerHTML = `<div class="tv-frame-title">${esc(this.frameTitle(frame))}<span class="tv-frame-line">${frame.line}행</span></div>`;
      const table = h('table');
      const before = prevFrames.get(frame.frame_id);
      for (const name of frame.ordered_varnames) {
        if (this.options.hideMainArgs && i === 0 && name === 'args' && frame.func_name === 'main') continue;
        const value = frame.encoded_locals[name];
        const changed = before ? !same(before.encoded_locals[name], value) : !!prev;
        const badges = [frame.static_names?.includes(name) ? 'static' : '', frame.declared_without_initializer?.includes(name) ? '선언 때 초기값 없음' : ''].filter(Boolean);
        table.append(this.row(name === '__return__' ? '반환값' : name, value, changed, name === '__return__', badges));
      }
      if (!table.children.length) table.append(h('tr', 'tv-empty', '<td colspan="2">지역 변수 없음</td>'));
      box.append(table);
      col.append(box);
    });
    if (!frames.length) col.append(h('div', 'tv-note', '실행이 끝났습니다.'));
  }

  row(name, value, changed, isReturn = false, badges = []) {
    const tr = h('tr', (changed ? 'is-changed' : '') + (isReturn ? ' is-return' : ''));
    tr.innerHTML = `<td class="tv-name">${esc(name)}${badges.map((b) => ` <span class="tv-badge">${esc(b)}</span>`).join('')}</td><td class="tv-value">${valueHtml(value)}</td>`;
    return tr;
  }

  renderHeap(step, prev) {
    const col = this.heapCol;
    col.replaceChildren(h('div', 'tv-title', '객체'));
    this.expanded ??= new Set();
    const internal = new Set(step.internal || []);
    const ids = Object.keys(step.heap || {}).map(Number).filter((id) => !internal.has(id)).sort((a, b) => a - b);
    for (const id of ids) col.append(this.objectBox(id, step, prev));
    if (!ids.length) col.append(h('div', 'tv-note', '아직 객체가 없습니다.'));
    if (this.doc.heapTruncated) col.append(h('div', 'tv-note', '객체 수가 많아 일부만 표시합니다.'));
  }

  /** One heap object as a box; collections get a type-specific shape and an internals toggle. */
  objectBox(id, step, prev) {
    const obj = step.heap[id];
    const was = prev?.heap?.[id];
    const box = h('div', 'tv-object' + (prev && !was ? ' is-new' : ''));
    box.dataset.id = id;
    const kind = obj[0], type = obj[1];
    let title = kind === 'INSTANCE' ? (type.includes('.') ? type : `${type} 인스턴스`) : kind === 'ARRAY' ? `배열 ${type}` : kind === 'STRING' ? 'String' : type;
    if (kind === 'COLLECTION') {
      const items = obj[2] || [], internals = obj[3];
      title = `${type} · size ${items.length}`;
      if (internals?.elementData && isRef(internals.elementData)) {
        const backing = step.heap[internals.elementData[1]];
        if (backing) title += ` / 용량 ${backing.length - 2}`;
      }
    } else if (kind === 'MAP') {
      const entries = obj[2] || [], internals = obj[3];
      title = `${type} · size ${entries.length}`;
      if (internals?.table && isRef(internals.table)) {
        const table = step.heap[internals.table[1]];
        if (table) title += ` / 버킷 ${table.length - 2}`;
      }
    }
    box.innerHTML = `<div class="tv-object-title"><span class="tv-id">#${id}</span>${esc(title)}</div>`;
    if (kind === 'INSTANCE') {
      const table = h('table', 'tv-fields');
      const wasFields = new Map(was && was[0] === 'INSTANCE' ? was.slice(2) : []);
      for (const [name, value] of obj.slice(2)) table.append(this.row(name, value, was && !same(wasFields.get(name), value)));
      if (!table.children.length) table.append(h('tr', 'tv-empty', '<td colspan="2">필드 없음</td>'));
      box.append(table);
    } else if (kind === 'ARRAY') {
      box.append(this.cells(obj.slice(2), was ? was.slice(2) : null, 0));
    } else if (kind === 'COLLECTION') {
      this.collectionBody(box, id, obj, was, step, prev);
    } else if (kind === 'MAP') {
      this.mapBody(box, id, obj, was, step, prev);
    } else if (kind === 'STRING') {
      box.classList.add('tv-scalar');
      box.append(h('div', 'tv-scalar-value', valueHtml(obj[1])));
    } else if (kind === 'BOXED') {
      box.classList.add('tv-scalar');
      box.append(h('div', 'tv-scalar-value', valueHtml(obj[2])));
    } else {
      box.append(h('div', 'tv-opaque', '내부 상태는 관측하지 않음'));
    }
    return box;
  }

  /** Index-labelled cells; `spare` adds dashed unused-capacity cells after the items. */
  cells(items, wasItems, spare) {
    const table = h('table', 'tv-array');
    const head = h('tr'), body = h('tr');
    items.forEach((v, i) => {
      head.append(h('th', null, String(i)));
      body.append(h('td', wasItems && !same(wasItems[i], v) ? 'is-changed' : '', valueHtml(v)));
    });
    const shown = Math.min(spare, 12);
    for (let i = 0; i < shown; i++) { head.append(h('th', null, String(items.length + i))); body.append(h('td', 'tv-spare', '')); }
    if (spare > shown) { head.append(h('th', null, '…')); body.append(h('td', 'tv-spare', `+${spare - shown}`)); }
    if (!items.length && !spare) { head.append(h('th', null, '')); body.append(h('td', 'tv-empty', '비어 있음')); }
    table.append(head, body);
    return table;
  }

  collectionBody(box, id, obj, was, step, prev) {
    const type = obj[1], items = obj[2] || [], internals = obj[3];
    const wasItems = was && was[0] === 'COLLECTION' ? was[2] : null;
    const backing = internals?.elementData && isRef(internals.elementData) ? step.heap[internals.elementData[1]] : null;
    if (type === 'LinkedList') {
      const chain = h('div', 'tv-chain');
      items.forEach((v, i) => {
        if (i > 0) chain.append(h('span', 'tv-link', '\u21c4'));
        chain.append(h('span', 'tv-chip' + (wasItems && !same(wasItems[i], v) ? ' is-changed' : ''), valueHtml(v)));
      });
      if (!items.length) chain.append(h('span', 'tv-empty', '비어 있음'));
      box.append(chain);
    } else if (type.endsWith('Set')) {
      const bag = h('div', 'tv-chain tv-bag');
      const wasSet = new Set((wasItems || []).map((v) => JSON.stringify(v)));
      items.forEach((v) => bag.append(h('span', 'tv-chip' + (wasItems && !wasSet.has(JSON.stringify(v)) ? ' is-changed' : ''), valueHtml(v))));
      if (!items.length) bag.append(h('span', 'tv-empty', '비어 있음'));
      box.append(bag);
    } else {
      box.append(this.cells(items, wasItems, backing ? Math.max(0, backing.length - 2 - items.length) : 0));
    }
    if (!internals) return;
    const open = this.expanded.has(id);
    const toggle = h('button', 'tv-toggle', open ? '\u25be 내부 구조 접기' : '\u25b8 내부 구조 보기');
    toggle.addEventListener('click', () => {
      if (open) this.expanded.delete(id);
      else {
        this.expanded.add(id);
        if (isRef(internals.map)) this.expanded.add(internals.map[1]); // a set opens its backing map too
      }
      this.goTo(this.index);
    });
    box.append(toggle);
    if (!open) return;
    const table = h('table', 'tv-fields');
    const wasInternals = was && was[0] === 'COLLECTION' ? was[3] : null;
    for (const [name, value] of Object.entries(internals)) table.append(this.row(name, value, wasInternals && !same(wasInternals[name], value)));
    box.append(table);
    const inner = h('div', 'tv-internals');
    const order = [];
    if (backing) order.push(internals.elementData[1]);
    if (isRef(internals.map) && step.heap[internals.map[1]]) order.push(internals.map[1]);
    if (type === 'LinkedList') {
      let cursor = internals.first, guard = 0;
      while (isRef(cursor) && step.heap[cursor[1]] && guard++ < 64) {
        order.push(cursor[1]);
        const node = step.heap[cursor[1]];
        cursor = (node.slice(2).find(([n]) => n === 'next') || [])[1];
      }
    }
    for (const innerId of order) inner.append(this.objectBox(innerId, step, prev));
    if (order.length) box.append(inner);
  }

  mapBody(box, id, obj, was, step, prev) {
    const entries = obj[2] || [], internals = obj[3];
    const wasByKey = was && was[0] === 'MAP' ? new Map(was[2].map(([k, v]) => [JSON.stringify(k), v])) : null;
    const table = h('table', 'tv-fields');
    entries.forEach(([k, v]) => {
      const key = JSON.stringify(k);
      const tr = h('tr', wasByKey && (!wasByKey.has(key) || !same(wasByKey.get(key), v)) ? 'is-changed' : '');
      tr.innerHTML = `<td class="tv-name">${valueHtml(k)}</td><td class="tv-value">${valueHtml(v)}</td>`;
      table.append(tr);
    });
    if (!entries.length) table.append(h('tr', 'tv-empty', '<td colspan="2">비어 있음</td>'));
    box.append(table);
    if (!internals) return;
    const open = this.expanded.has(id);
    const toggle = h('button', 'tv-toggle', open ? '\u25be 내부 구조 접기' : '\u25b8 내부 구조 보기');
    toggle.addEventListener('click', () => {
      if (open) this.expanded.delete(id); else this.expanded.add(id);
      this.goTo(this.index);
    });
    box.append(toggle);
    if (!open) return;
    const fields = h('table', 'tv-fields');
    const wasInternals = was && was[0] === 'MAP' ? was[3] : null;
    for (const [name, value] of Object.entries(internals)) fields.append(this.row(name, value, wasInternals && !same(wasInternals[name], value)));
    box.append(fields);
    const bucketArray = internals.table && isRef(internals.table) ? step.heap[internals.table[1]] : null;
    if (!bucketArray) return;
    const inner = h('div', 'tv-internals');
    inner.append(this.bucketBox(internals.table[1], bucketArray, prev?.heap?.[internals.table[1]]));
    const chains = h('div', 'tv-chains');
    bucketArray.slice(2).forEach((slot) => {
      if (!isRef(slot)) return;
      const chain = h('div', 'tv-chain-row');
      let cursor = slot, guard = 0;
      while (isRef(cursor) && step.heap[cursor[1]] && guard++ < 64) {
        chain.append(this.objectBox(cursor[1], step, prev));
        const node = step.heap[cursor[1]];
        cursor = (node.slice(2).find(([n]) => n === 'next') || [])[1];
      }
      chains.append(chain);
    });
    inner.append(chains);
    box.append(inner);
  }

  /** Hash table array drawn vertically: one row per bucket, runs of empty buckets collapsed. */
  bucketBox(id, arr, was) {
    const box = h('div', 'tv-object tv-buckets' + (was ? '' : ' is-new'));
    box.dataset.id = id;
    const slots = arr.slice(2);
    box.innerHTML = `<div class="tv-object-title"><span class="tv-id">#${id}</span>배열 ${esc(arr[1].replace('[]', ''))}[${slots.length}]</div>`;
    const table = h('table', 'tv-fields');
    for (let i = 0; i < slots.length; i++) {
      if (slots[i] === null) {
        let j = i;
        while (j + 1 < slots.length && slots[j + 1] === null) j++;
        const tr = h('tr', 'tv-empty');
        tr.innerHTML = `<td class="tv-name">${j > i ? `${i}–${j}` : i}</td><td class="tv-value"><span class="v-null">null</span></td>`;
        table.append(tr);
        i = j;
        continue;
      }
      const changed = was && !same(was[i + 2], slots[i]);
      table.append(this.row(String(i), slots[i], changed));
    }
    box.append(table);
    return box;
  }

  drawArrows() {
    const svg = this.svg;
    const defs = svg.querySelector('defs');
    svg.replaceChildren(defs);
    const box = this.memory.getBoundingClientRect();
    svg.setAttribute('width', this.memory.clientWidth);
    svg.setAttribute('height', this.memory.clientHeight);
    // client rects are post-transform/zoom; SVG units are layout px, so undo any ancestor scaling
    const k = (box.width / this.memory.offsetWidth) || 1;
    const sx = this.memory.scrollLeft, sy = this.memory.scrollTop;
    const current = this.framesCol.querySelector('.tv-frame.is-current');
    for (const src of this.memory.querySelectorAll('[data-ref]')) {
      const target = this.heapCol.querySelector(`.tv-object[data-id="${src.dataset.ref}"]`);
      if (!target) continue;
      const a = src.getBoundingClientRect(), b = target.getBoundingClientRect();
      const x1 = (a.left - box.left) / k + sx + 6, y1 = (a.top - box.top + a.height / 2) / k + sy;
      const x2 = (b.left - box.left) / k + sx, y2 = (b.top - box.top) / k + sy + 12;
      const fromHeap = !!src.closest('.tv-object');
      const dim = fromHeap ? false : !(current && current.contains(src)) && !src.closest('.tv-globals');
      const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      let d;
      if (fromHeap && src.closest('.tv-object') === target) {
        // self reference: loop out to the right and back to the top-left corner
        const r = src.closest('.tv-object').getBoundingClientRect();
        const rx = (r.right - box.left) / k + sx;
        d = `M${x1},${y1} C${rx + 30},${y1} ${rx + 30},${y2 - 24} ${x2 + 20},${y2 - 10}`;
      } else {
        const dx = Math.max(40, Math.abs(x2 - x1) / 2);
        d = `M${x1},${y1} C${x1 + dx},${y1} ${x2 - dx},${y2} ${x2},${y2}`;
      }
      path.setAttribute('d', d);
      path.setAttribute('class', 'tv-edge' + (dim ? ' is-dim' : '') + (fromHeap ? ' is-heap' : ''));
      path.setAttribute('marker-end', dim ? 'url(#tv-head-dim)' : 'url(#tv-head)');
      svg.append(path);
      src.classList.toggle('is-dim', dim);
    }
  }
}
