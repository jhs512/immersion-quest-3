// Lets the tutor chat act on the screen, and explain while it does.
//
// The assistant may end an answer with a ```molip-actions fence holding a JSON array such as
// [{"action":"set_code","code":"..."},{"action":"submit"}]. The Rust side hands that array to
// window.molipAgent.run, which drives the same buttons and inputs the student uses, waits for
// each run or submission to finish, and returns a text report that goes back to the assistant.
//
// 해설 모드: any action may carry "say". The agent then puts a purple spotlight on the part of the
// screen it is about to touch, shows the sentence in a caption there and reads it aloud (Web
// Speech, Korean voice, the reading speed the 읽어주기 panel saved), and only then acts.
// `say` {target, text} is narration alone; `type_code` {code, say, replace} types code into the
// editor a few characters at a time while the explanation is spoken. A target of the form
// "text:<구절>" is the block of the mission text that contains that phrase (a paragraph, a
// code block, a comic): the page glides there slowly before the sentence is read, so an
// explanation of something below the fold is seen, not just heard. The voice comes from
// assets/layout/voice.js (neural clips), or Web Speech when explicitly selected. molipAgent.stop() ends a
// narration (the sidebar's 멈춤 button), molipAgent.setVoice(false) keeps the captions but mutes.
(function () {
  'use strict';
  // ---- Narration code edits as keystrokes (pure; tests/js/narration-edit-plan.test.cjs). ----
  // steps(source, from, to, insert) yields {from, to, insert} replacements of one character each
  // that turn source into source[0,from) + insert + source[to,…) exactly. Only the parts that
  // differ are deleted and typed: the edit is diffed by words, spaces and line breaks, so text
  // both sides share (a line's own newline, the `}` below it) is never deleted and retyped.
  // A pure insertion or deletion that could equally sit one line higher is moved there when that
  // keeps the following line whole: inserting `    return 0;\n` above `    }` is typed as
  // `\n    return 0;` at the end of the line before, so `}` never trails the half-typed code.
  // Sliding only picks between equivalent positions, so the final text, the indentation of
  // Python and the contents of strings and comments are exactly what the lesson authored.
  const editPlan = (() => {
    const segmenter = globalThis.Intl?.Segmenter ? new Intl.Segmenter(undefined, {granularity: 'grapheme'}) : null;
    const graphemes = text => segmenter ? Array.from(segmenter.segment(text), part => part.segment) : Array.from(text);
    const isBreak = g => g === '\n' || g === '\r\n' || g === '\r';
    const wordLike = g => /^[\p{L}\p{N}_$]/u.test(g);
    const blankLike = g => g === ' ' || g === '\t';
    // Words, runs of spaces/tabs, line breaks and single other characters; joined they are `text`.
    function tokens(text) {
      const out = [];
      for (const g of graphemes(text)) {
        const last = out.length ? out[out.length - 1] : '';
        if (last && ((wordLike(g) && wordLike(last)) || (blankLike(g) && blankLike(last[0])))) out[out.length - 1] = last + g;
        else out.push(g);
      }
      return out;
    }
    // Myers' diff of two token lists: [{a0, a1, b0, b1}] in token indices, or null when too large.
    function changes(a, b) {
      const n = a.length, m = b.length, max = n + m, offset = max + 1;
      const v = new Int32Array(2 * max + 3), trace = [];
      let budget = 4e6;
      for (let d = 0; d <= max; d++) {
        if ((budget -= v.length) < 0) return null;
        trace.push(v.slice());
        for (let k = -d; k <= d; k += 2) {
          let x = (k === -d || (k !== d && v[offset + k - 1] < v[offset + k + 1])) ? v[offset + k + 1] : v[offset + k - 1] + 1;
          let y = x - k;
          while (x < n && y < m && a[x] === b[y]) { x++; y++; }
          v[offset + k] = x;
          if (x >= n && y >= m) {
            const ops = [];
            for (let e = d; e > 0; e--) {
              const w = trace[e], kk = x - y;
              // down: b[py] was inserted before a[px]; otherwise a[px] was deleted.
              const down = kk === -e || (kk !== e && w[offset + kk - 1] < w[offset + kk + 1]);
              const pk = down ? kk + 1 : kk - 1, px = w[offset + pk], py = px - pk;
              const mx = down ? px : px + 1, my = down ? py + 1 : py;
              while (x > mx && y > my) { x--; y--; }
              ops.push({a: px, b: py, insert: down});
              x = px; y = py;
            }
            ops.reverse();
            const hunks = [];
            for (const op of ops) {
              const last = hunks[hunks.length - 1];
              const a0 = op.a, b0 = op.b, a1 = op.insert ? op.a : op.a + 1, b1 = op.insert ? op.b + 1 : op.b;
              if (last && last.a1 === a0 && last.b1 === b0) { last.a1 = a1; last.b1 = b1; }
              else hunks.push({a0, a1, b0, b1});
            }
            return hunks;
          }
        }
      }
      return null;
    }
    // Changed regions of old → next as character offsets, in order.
    function hunks(old, next) {
      if (old === next) return [];
      const a = tokens(old), b = tokens(next);
      const at = list => { const sums = [0]; for (const t of list) sums.push(sums[sums.length - 1] + t.length); return sums; };
      const sa = at(a), sb = at(b);
      let found = changes(a, b);
      if (!found) {
        let p = 0, s = 0;
        while (p < a.length && p < b.length && a[p] === b[p]) p++;
        while (s < a.length - p && s < b.length - p && a[a.length - 1 - s] === b[b.length - 1 - s]) s++;
        found = [{a0: p, a1: a.length - s, b0: p, b1: b.length - s}];
      }
      // A single shared space or symbol between two changes reads better replaced with them.
      const merged = [];
      for (const h of found) {
        const last = merged[merged.length - 1];
        if (last && h.a0 - last.a1 === 1 && h.b0 - last.b1 === 1 && a[last.a1].length === 1 && !isBreak(a[last.a1])) { last.a1 = h.a1; last.b1 = h.b1; }
        else merged.push({...h});
      }
      return merged.map(h => ({oldFrom: sa[h.a0], oldTo: sa[h.a1], text: next.slice(sb[h.b0], sb[h.b1]), removed: old.slice(sa[h.a0], sa[h.a1])}));
    }
    const before = (doc, p) => { if (p <= 0) return ''; const g = graphemes(doc.slice(Math.max(0, p - 32), p)); return g[g.length - 1] || ''; };
    const after = (doc, p) => (p >= doc.length ? '' : graphemes(doc.slice(p, p + 32))[0] || '');
    // Among the positions where inserting (or deleting) `span` gives the same text, prefer one
    // that ends right before a line break without itself ending in one.
    function slide(doc, p, span, deleting) {
      const good = (q, text) => { const next = after(doc, deleting ? q + text.length : q), parts = graphemes(text); return (!next || isBreak(next)) && !isBreak(parts[parts.length - 1]); };
      if (!span || good(p, span)) return [p, span];
      const candidates = [];
      for (const direction of [-1, 1]) {
        let q = p, text = span;
        for (let i = 0; i < 4000; i++) {
          const parts = graphemes(text);
          if (direction < 0) {
            const g = before(doc, q), last = deleting ? before(doc, q + text.length) : parts[parts.length - 1];
            if (!g || g !== last) break;
            q -= g.length; text = deleting ? doc.slice(q, q + text.length) : g + parts.slice(0, -1).join('');
          } else {
            const first = deleting ? after(doc, q) : parts[0], g = after(doc, deleting ? q + text.length : q);
            if (!g || g !== first) break;
            q += g.length; text = deleting ? doc.slice(q, q + text.length) : parts.slice(1).join('') + g;
          }
          if (good(q, text)) { candidates.push([Math.abs(q - p), direction, q, text]); break; }
        }
      }
      candidates.sort((x, y) => x[0] - y[0] || x[1] - y[1]);
      return candidates.length ? [candidates[0][2], candidates[0][3]] : [p, span];
    }
    function* steps(source, from, to, insert) {
      let doc = source, shift = 0;
      for (const h of hunks(source.slice(from, to), insert)) {
        const at = from + h.oldFrom + shift;
        if (h.removed) {
          const [p, text] = slide(doc, at, h.removed, true);
          const parts = graphemes(text);
          if (isBreak(parts[parts.length - 1])) {
            // Still ends with a line break (a whole first line of the file): delete it from the
            // front, so the line below never joins the half-deleted one.
            for (const g of parts) {
              const step = {from: p, to: p + g.length, insert: ''};
              doc = doc.slice(0, step.from) + doc.slice(step.to);
              yield step;
            }
          } else {
            let end = p + text.length;
            for (const g of parts.reverse()) {
              const step = {from: end - g.length, to: end, insert: ''};
              doc = doc.slice(0, step.from) + doc.slice(step.to); end = step.from;
              yield step;
            }
          }
        }
        if (h.text) {
          const [p, text] = slide(doc, at, h.text, false);
          const parts = graphemes(text);
          let q = p;
          // Ending with a line break: press it first, then type the line above it, as a person
          // opening a new line does.
          if (isBreak(parts[parts.length - 1])) {
            const g = parts.pop();
            doc = doc.slice(0, q) + g + doc.slice(q);
            yield {from: q, to: q, insert: g};
          }
          for (const g of parts) {
            const step = {from: q, to: q, insert: g};
            doc = doc.slice(0, q) + g + doc.slice(q); q += g.length;
            yield step;
          }
        }
        shift += h.text.length - h.removed.length;
      }
    }
    return {steps, hunks, tokens};
  })();
  globalThis.molipEditPlan = editPlan;
  if (globalThis.molipAgent || typeof document === 'undefined') return;
  const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
  const byText = (selector, text) => [...document.querySelectorAll(selector)].find(b => b.textContent.trim() === text);
  // Wait for a run or a grading to finish: the button comes back, or the reward card is up (a
  // passed quiz keeps its 제출 button disabled, so the card is the signal there).
  async function waitIdle(button, limit = 180000, previousExecution = null, active = () => !cancelled) {
    const started = Date.now();
    const pane = document.querySelector('.result-pane');
    if (previousExecution === null) await sleep(40);
    // Execution and history synchronization are separate operations. A run id also
    // catches quick programs that finish between two render frames.
    while (active() && button.isConnected && Date.now() - started < limit) {
      if (previousExecution !== null && pane?.dataset.executionId !== previousExecution
          && ['finished','failed'].includes(pane?.dataset.executionState)) return;
      if (previousExecution === null && (!button.disabled || cleared())) return;
      await sleep(40);
    }
    if (active() && button.isConnected && Date.now() - started >= limit)
      throw new Error('실행이 끝나지 않았어요. 실행 상태를 확인하세요.');
  }

  const text = (selector, max = 3000) => [...document.querySelectorAll(selector)].map(e => e.textContent.trim()).filter(Boolean).join('\n').slice(0, max);
  function workspaceReport() {
    return [text('.result-pane .execution-status'), text('.result-pane .output')].filter(Boolean).join('\n');
  }
  // The reward card (다음 미션 / 여기 머물기) is left to the student or to /auto-all; its presence
  // is how a pass is recognised. A `next` action takes its 다음 미션 button.
  const popupButton = text => [...document.querySelectorAll('.doctor-panel button')].find(b => b.textContent.trim() === text) || null;
  const cleared = () => !!document.querySelector('.victory-panel');

  // ---- Spotlight: a purple frame over the element being talked about, with the sentence. ----
  const TARGETS = {
    problem: ['.problem-pane h3', '.problem-pane', '.reading-mission'],
    examples: ['.problem-pane details', '.problem-pane .examples', '.problem-pane table', '.problem-pane'],
    editor: ['.cm-editor', '.editor-pane', 'textarea.code-editor'],
    blanks: ['.code-blanks', 'input.code-blank', '.editor-pane'],
    input: ['.result-pane textarea', '.result-pane details', '.result-pane'],
    output: ['.result-pane .output', '.result-pane'],
    memory: ['.narration-memory'],
    run: [() => byText('.pane-actions button', '코드 실행'), '.pane-actions'],
    submit: [() => byText('.pane-actions button', '제출'), '.pane-actions'],
    hint: ['.problem-pane details', '.hint', '.problem-pane'],
    prompt: ['.prompt-buttons', '.problem-pane'],
    quiz: ['.quiz-question', '.reading-mission'],
    quiz_submit: ['.quiz-actions .primary', '.quiz-actions'],
    nav: ['.header-navigation'],
    missions: ['.mission-cell.current', '.mission-cell'],
    slides: ['.slides-stage', '.slides-host'],
    xp: ['.learning-xp'],
    title: ['.reading-mission h2', '.problem-pane h2', '.slides-mission h2'],
  };
  const normalize = value => String(value || '').replace(/[`*]/g, '').replace(/\s+/g, ' ').trim();
  // The question numbered N (data-question, set by the Rust side), or the N-th on screen.
  function question(n) {
    return document.querySelector(`.quiz-question[data-question="${n}"]`)
      || document.querySelectorAll('.quiz-question')[Number(n) - 1] || null;
  }
  // The smallest block of the mission text that contains the phrase: a paragraph, list item,
  // heading, table, code block or rendered figure (comics keep their title as SVG text).
  function textBlock(phrase) {
    const wanted = normalize(phrase);
    if (!wanted) return null;
    const roots = [...document.querySelectorAll('.reading-mission .markdown, .problem-pane .markdown, .quiz-question')];
    for (const root of roots) {
      for (const block of root.children) {
        if (!normalize(block.textContent).includes(wanted)) continue;
        // A list or table: narrow to the item/row when one holds the whole phrase.
        const inner = [...block.querySelectorAll('li, tr, p')].find(e => normalize(e.textContent).includes(wanted));
        return inner && inner.getBoundingClientRect().height > 0 ? inner : block;
      }
    }
    // A practice problem never falls back to framing its whole panel: an unmatched phrase gets no
    // frame (the caption still shows). Only a KPC reading mission keeps its block-level fallback.
    const fallback = [...document.querySelectorAll('.reading-mission')].find(e => normalize(e.textContent).includes(wanted));
    return fallback || null;
  }
  // "구절#2" names the second occurrence of the phrase; without a suffix the first one.
  function occurrence(spec) {
    const match = String(spec).match(/^(.*?)(?:#(\d+))?$/s);
    return [match[1], Math.max(1, Number(match[2] || 1))];
  }
  // A rectangle-only stand-in for a Range or a set of elements, so the spotlight can frame the
  // exact words without inserting anything into the DOM that Dioxus owns.
  function rectTarget(rects, anchor) {
    return {
      get isConnected() { return anchor.isConnected; },
      parentElement: anchor.parentElement || anchor,
      closest: selector => anchor.closest?.(selector) ?? null,
      getBoundingClientRect() {
        const boxes = rects().filter(r => r.width || r.height);
        if (!boxes.length) return anchor.getBoundingClientRect();
        const left = Math.min(...boxes.map(r => r.left)), top = Math.min(...boxes.map(r => r.top));
        const right = Math.max(...boxes.map(r => r.right)), bottom = Math.max(...boxes.map(r => r.bottom));
        return {left, top, right, bottom, width: right - left, height: bottom - top};
      },
    };
  }
  // The exact phrase inside the mission text: whitespace is collapsed and markdown markers
  // ignored on both sides, and a DOM Range covers precisely the matched characters.
  function textRange(spec) {
    const [phrase, nth] = occurrence(spec);
    const wanted = normalize(phrase);
    if (!wanted) return null;
    const roots = [...document.querySelectorAll('.reading-mission .markdown, .problem-pane .problem-heading h2, .problem-pane .task-question, .problem-pane .markdown, .quiz-question')];
    let seen = 0;
    for (const root of roots) {
      const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
      const map = [];
      let flat = '', block = null;
      const blockOf = node => node.parentElement?.closest('p, li, h1, h2, h3, h4, h5, h6, td, th, pre, blockquote, figcaption, label, div') || root;
      for (let node = walker.nextNode(); node; node = walker.nextNode()) {
        if (node.parentElement?.closest('script, style')) continue;
        // Separate blocks (two list items) with a space; inline code inside a sentence joins.
        const here = blockOf(node);
        if (block && here !== block && flat && !flat.endsWith(' ')) { flat += ' '; map.push(map.at(-1)); }
        block = here;
        for (let i = 0; i < node.data.length; i++) {
          let ch = node.data[i];
          if (/[`*]/.test(ch)) continue;
          if (/\s/.test(ch)) { if (!flat || flat.endsWith(' ')) continue; ch = ' '; }
          flat += ch; map.push([node, i]);
        }
      }
      for (let at = flat.indexOf(wanted); at >= 0; at = flat.indexOf(wanted, at + 1)) {
        if (++seen < nth) continue;
        const [startNode, startOffset] = map[at];
        const [endNode, endIndex] = map[at + wanted.length - 1];
        const range = document.createRange();
        range.setStart(startNode, startOffset);
        range.setEnd(endNode, Math.min(endNode.data.length, endIndex + 1));
        return range;
      }
    }
    return null;
  }
  let textHighlight = null;
  function showTextRange(range) {
    clearTextRange();
    if (globalThis.CSS?.highlights && globalThis.Highlight) {
      textHighlight = new Highlight(range);
      CSS.highlights.set('narration-text', textHighlight);
    }
    const anchor = range.startContainer.parentElement;
    return rectTarget(() => [...range.getClientRects()], anchor);
  }
  function clearTextRange() {
    if (textHighlight) { globalThis.CSS?.highlights?.delete('narration-text'); textHighlight = null; }
  }
  // "code:<토큰>#n": the exact characters in the visible editor, with their line highlighted too.
  function codeRange(spec) {
    const api = globalThis.molipCodeEditors;
    if (!api?.highlightRange) return null;
    const [snippet, nth] = occurrence(spec);
    const source = api.getValue() || '';
    let from = -1;
    for (let k = 0, at = source.indexOf(snippet); at >= 0; at = source.indexOf(snippet, at + 1)) if (++k === nth) { from = at; break; }
    if (from < 0 || !snippet) return null;
    const to = from + snippet.length;
    api.highlightLines(lineAt(source, from), lineAt(source, Math.max(from, to - 1)));
    api.highlightRange(from, to);
    const marked = () => [...document.querySelectorAll('.cm-narration-span')];
    const first = marked()[0];
    if (!first) return null;
    return rectTarget(() => marked().flatMap(e => [...e.getClientRects()]), first);
  }
  // A rendered element has a box. A selector can match a hidden copy first: during a Vim
  // demonstration the learner's live panel (.vim-live-panel) is still in the page but hidden, and
  // the demo's visible panel comes after it. Pick the first rendered match, else the first match.
  const rendered = element => { if (!element?.isConnected) return false; const r = element.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
  function pick(selector) {
    const all = [...document.querySelectorAll(selector)];
    return all.find(rendered) || all[0] || null;
  }
  function resolveTarget(target) {
    if (!target) return null;
    const key = String(target).trim();
    if (!key.startsWith('code:')) globalThis.molipCodeEditors?.highlightRange?.(null);
    if (!key.startsWith('text:')) clearTextRange();
    if (key.startsWith('code:')) return codeRange(key.slice(5));
    if (key.startsWith('answer:')) return document.querySelector(`[data-option-id="${CSS.escape(key.slice(7))}"]`);
    const lines = key.match(/^(?:lines|editor):(\d+)(?::(\d+))?$/);
    if (lines) globalThis.molipCodeEditors?.highlightLines(Number(lines[1]), Number(lines[2] || lines[1]));
    if (key === 'editor' || lines) {
      const marked = [...document.querySelectorAll('.cm-narration-line')];
      if (marked.length) return {
        get isConnected() { return marked[0].isConnected; },
        parentElement: marked[0].parentElement,
        getBoundingClientRect() {
          const first = marked[0].getBoundingClientRect(), last = marked.at(-1).getBoundingClientRect();
          return {left: first.left, right: first.right, top: first.top, bottom: last.bottom,
            width: first.width, height: last.bottom - first.top};
        },
      };
    }
    // "quiz:2" is the second question; "option:2:3" its third choice.
    if (key.startsWith('text:')) {
      const range = textRange(key.slice(5));
      if (range) return showTextRange(range);
      clearTextRange();
      return textBlock(occurrence(key.slice(5))[0]);
    }
    let m = key.match(/^quiz[:\s]+(\d+)$/);
    if (m) return question(m[1]);
    m = key.match(/^option[:\s]+(\d+)[:\s]+(\d+)$/);
    if (m) {
      const section = question(m[1]);
      return (section && section.querySelectorAll('.quiz-option')[Number(m[2]) - 1]) || section || null;
    }
    const candidates = TARGETS[key];
    if (candidates) {
      for (const candidate of candidates) {
        const element = typeof candidate === 'function' ? candidate() : pick(candidate);
        if (element) return element;
      }
      return null;
    }
    try { return pick(key); } catch { return null; }
  }
  let spot, caption, spotTarget = null, spotKey = null, raf = 0;
  // Options the narration has talked about keep a mark until the run ends.
  function mark(element) {
    const option = element && element.closest && element.closest('.quiz-option');
    if (option) option.classList.add('agent-said');
  }
  function clearMarks() { for (const e of document.querySelectorAll('.agent-said')) e.classList.remove('agent-said'); }
  function ensureSpot() {
    if (spot) return;
    spot = document.createElement('div'); spot.className = 'agent-spotlight'; spot.hidden = true; spot.setAttribute('aria-hidden', 'true');
    caption = document.createElement('div'); caption.className = 'agent-caption'; caption.hidden = true; caption.setAttribute('role', 'status'); caption.setAttribute('aria-live', 'polite');
    document.body.append(spot, caption);
  }
  function place() {
    const margin = 8;
    // The UI re-renders after a tick or a grade: find the same target again by its key.
    if (spotTarget && !spotTarget.isConnected && spotKey) { spotTarget = resolveTarget(spotKey); mark(spotTarget); }
    // A plain selector whose element became hidden (a demo ended, a panel swapped): find the
    // rendered one again. Text and code targets keep their range.
    else if (spotTarget && spotKey && !rendered(spotTarget) && !/^(?:text|code|lines|editor|answer|quiz|option):|^editor$/.test(spotKey)) { const again = resolveTarget(spotKey); if (again) { spotTarget = again; mark(again); } }
    // A target without a box (hidden) is no place for the frame or the caption: the caption then sits
    // where it does without a target, never at the window's top corner over the header and steps.
    const r = spotTarget && spotTarget.isConnected ? spotTarget.getBoundingClientRect() : null;
    if (r && r.width > 0 && r.height > 0) {
      const pad = 6;
      spot.style.left = `${r.left - pad}px`; spot.style.top = `${r.top - pad}px`;
      spot.style.width = `${r.width + pad * 2}px`; spot.style.height = `${r.height + pad * 2}px`;
      spot.hidden = spot.dataset.webTarget === 'true';
      if (!caption.hidden) {
        const w = caption.offsetWidth, h = caption.offsetHeight;
        let left = r.left + r.width / 2 - w / 2;
        left = Math.max(margin, Math.min(left, innerWidth - margin - w));
        let top = r.bottom + pad + 12;
        if (top + h > innerHeight - margin) top = r.top - pad - 12 - h;
        if (top < margin) top = Math.min(innerHeight - margin - h, r.top + 12);
        caption.style.left = `${left}px`; caption.style.top = `${top}px`;
      }
    } else {
      spot.hidden = true;
      if (!caption.hidden) {
        caption.style.left = `${Math.max(margin, innerWidth / 2 - caption.offsetWidth / 2)}px`;
        caption.style.top = `${innerHeight - margin - caption.offsetHeight - 24}px`;
      }
    }
    raf = requestAnimationFrame(place);
  }
  // ---- Glide: bring the element into view slowly, the way a presenter scrolls while talking. ----
  const scrollParent = element => {
    for (let node = element.parentElement; node; node = node.parentElement) {
      const style = getComputedStyle(node);
      if (/(auto|scroll)/.test(style.overflowY) && node.scrollHeight > node.clientHeight + 1) return node;
    }
    return document.scrollingElement || document.documentElement;
  };
  const ease = t => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
  let glideFrame = 0;
  function glideTo(element) {
    cancelAnimationFrame(glideFrame);
    const container = scrollParent(element);
    const viewport = container === document.scrollingElement || container === document.documentElement;
    const box = viewport ? { top: 0, height: innerHeight } : container.getBoundingClientRect();
    const r = element.getBoundingClientRect();
    const margin = 24;
    // Already fully on screen: leave the page where it is.
    if (r.top >= box.top + margin && r.bottom <= box.top + box.height - margin) return 0;
    // Centre the block; a block taller than the view lands with its top near the top.
    const offset = r.height > box.height * 0.6 ? margin + 12 : (box.height - r.height) / 2;
    const target = Math.max(0, Math.min(container.scrollTop + (r.top - box.top) - offset, container.scrollHeight - container.clientHeight));
    const start = container.scrollTop, distance = target - start;
    if (Math.abs(distance) < 2) return 0;
    const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
    const duration = reduced ? 0 : Math.min(1600, Math.max(600, 450 + Math.abs(distance) * 0.7));
    const began = performance.now();
    const step = now => {
      const t = duration ? Math.min(1, (now - began) / duration) : 1;
      container.scrollTop = start + distance * ease(t);
      if (t < 1) glideFrame = requestAnimationFrame(step);
    };
    glideFrame = requestAnimationFrame(step);
    return duration;
  }
  // Authored speech uses pronunciations such as 십이. Captions use the numerical
  // values in this task and demonstration, without changing what the voice reads.
  let captionSource = '';
  function captionText(sentence) {
    const display = value => globalThis.molipSpeech?.formatPrices(value) ?? String(value);
    const source = (document.querySelector('.repository-task')?.textContent || '') + '\n' + captionSource;
    const digits = ['', '일', '이', '삼', '사', '오', '육', '칠', '팔', '구'];
    const group = value => {
      let result = '';
      for (const [unit, word] of [[1000,'천'],[100,'백'],[10,'십'],[1,'']]) {
        const digit = Math.floor(value / unit); value %= unit;
        if (digit) result += (digit === 1 && unit > 1 ? '' : digits[digit]) + word;
      }
      return result;
    };
    const numbers = new Map();
    for (const match of source.matchAll(/\b\d{1,3}(?:,\d{3})+\b|\b\d{2,8}\b/g)) {
      const value = Number(match[0].replaceAll(',', ''));
      if (value < 10) continue;
      const high = Math.floor(value / 10000), low = value % 10000;
      const word = (high ? (high === 1 ? '' : group(high)) + '만' : '') + group(low);
      numbers.set(word, String(value));
    }
    if (!numbers.size) return display(sentence || '');
    const words = [...numbers.keys()].sort((a,b)=>b.length-a.length).join('|');
    // A suffix check keeps ordinary words such as 백업 and 만약 intact.
    const pattern = new RegExp('(^|[^가-힣])(' + words + ')(?=$|[\\s,.!?…]|은|는|이|가|을|를|의|에|예|와|과|로|도|만|번|개|명|건|점|초|분|시|줄|배|원|퍼센트|%)', 'g');
    return display(String(sentence || '').replace(pattern, (whole, prefix, word, index, text) => {
      const base = word.slice(0,-1);
      if (word.endsWith('이') && text.slice(index + whole.length).startsWith('에요') && numbers.has(base)) return prefix + numbers.get(base) + '이';
      return prefix + numbers.get(word);
    }));
  }
  function spotlight(target, sentence) {
    ensureSpot();
    // The sandbox draws per-element frames, not a frame around a text dump.
    // Existing lessons' output targets resolve to their tested screen elements.
    const frame = pick('iframe[title="해설 웹 미리보기"]');
    const webTarget = frame && (target === 'output' || String(target).startsWith('web:') || String(target).includes('iframe[title="해설 웹 미리보기"]'));
    for(const preview of document.querySelectorAll('.result-pane iframe'))preview.contentWindow?.postMessage({type:'mq3-web-highlight',selector:''},'*');
    spot.dataset.webTarget = webTarget ? 'true' : 'false';
    if(webTarget) {
      const selector=String(target).startsWith('web:')?String(target).slice(4):webFocus || document.querySelector('.result-pane')?.dataset.webSelectors || 'body';
      frame.contentWindow.postMessage({type:'mq3-web-highlight',selector},'*');
      target='iframe[title="해설 웹 미리보기"]';
    }
    const element = resolveTarget(target);
    spotTarget = element || null;
    spotKey = element ? String(target) : null;
    if (element) {
      mark(element);
      try { glideTo(element); } catch {}
    }
    document.querySelectorAll('.overview-speaking').forEach(node=>node.classList.remove('overview-speaking'));
    if(spotTarget?.closest?.('#lesson-info-dialog, #course-guide-dialog')) {
      spotTarget.classList.add('overview-speaking');
      spot.hidden=true;caption.hidden=true;cancelAnimationFrame(raf);raf=0;
      const dialog=spotTarget.closest('dialog');
      const status=dialog?.querySelector('[data-overview-status], #lesson-overview-status');if(status)status.textContent=sentence||'';
      return;
    }
    caption.textContent = captionText(sentence);
    caption.hidden = !sentence;
    cancelAnimationFrame(raf);
    place();
  }
  function clearSpot() {
    for(const preview of document.querySelectorAll('.result-pane iframe'))preview.contentWindow?.postMessage({type:'mq3-web-highlight',selector:''},'*');
    cancelAnimationFrame(raf); raf = 0;
    document.querySelectorAll('.overview-speaking').forEach(node=>node.classList.remove('overview-speaking'));
    spotTarget = null; spotKey = null;
    clearMarks();
    globalThis.molipCodeEditors?.highlightLines(null);
    globalThis.molipCodeEditors?.highlightRange?.(null);
    clearTextRange();
    if (spot) { spot.hidden = true; caption.hidden = true; }
    document.querySelector('.narration-memory')?.remove();
  }

  function showMemory(diagram) {
    if (!diagram || !Array.isArray(diagram.rows)) return;
    const host = document.querySelector('.problem-pane');
    if (!host) throw new Error('메모리 그림을 표시할 문제 패널이 없어요.');
    let panel = host.querySelector('.narration-memory');
    if (!panel) {
      panel = document.createElement('figure');
      panel.className = 'narration-memory';
      panel.setAttribute('aria-label', '해설 메모리 그림');
      host.prepend(panel);
    }
    panel.replaceChildren();
    const title = document.createElement('figcaption');
    title.textContent = String(diagram.title || '변수와 연결');
    panel.append(title);
    for (const row of diagram.rows) {
      const line = document.createElement('div');
      line.className = 'narration-memory-row';
      for (const [i, cell] of String(row).split('→').entries()) {
        if (i) { const arrow = document.createElement('span'); arrow.textContent = '→'; arrow.className = 'narration-memory-arrow'; line.append(arrow); }
        const box = document.createElement('span'); box.className = 'narration-memory-cell'; box.textContent = cell.trim(); line.append(box);
      }
      panel.append(line);
    }
  }

  // ---- Voice: one sentence at a time, resolved when it has been read (or would have been). ----
  let voice = true, cancelled = false;
  let forcedVoiceRun = 0;
  const voiceOn = () => voice || (forcedVoiceRun !== 0 && forcedVoiceRun === narrationRun);
  // Pause (the panel's ⏸, the Space key): the clip or utterance playing is held, typing stops,
  // and the next action waits; resume picks up exactly there. The spotlight stays where it is.
  let paused = false, running = false;
  async function waitWhilePaused() { while (paused && !cancelled) await sleep(100); }
  function pause() {
    if (!running || paused) return paused;
    paused = true;
    if (currentAudio) { try { currentAudio.pause(); } catch {} }
    if ('speechSynthesis' in window) { try { window.speechSynthesis.pause(); } catch {} }
    return paused;
  }
  function resume() {
    if (!paused) return paused;
    paused = false;
    if (currentAudio) { currentAudio.play().catch(() => {}); }
    if ('speechSynthesis' in window) { try { window.speechSynthesis.resume(); } catch {} }
    return paused;
  }
  // ---- Neural voice: clips come from assets/layout/voice.js (the app's /tts endpoint). ----
  let currentAudio = null, finishClip = null;
  const neural = () => (globalThis.molipVoice && globalThis.molipVoice.enabled()) ? globalThis.molipVoice : null;
  // 멈춤 while a clip is being fetched: the fetch keeps going (it fills the cache), but the
  // narration stops waiting for it. Each waiter is released by stop().
  let cancelWaiters = [];
  const untilCancelled = () => new Promise(resolve => cancelWaiters.push(resolve));
  function releaseCancelWaiters() { const waiters = cancelWaiters; cancelWaiters = []; for (const resolve of waiters) resolve(null); }
  function synthesize(sentence) {
    const v = neural();
    if (!v) return Promise.resolve(null);
    if (cancelled) return Promise.resolve(null);
    return Promise.race([v.synthesize(sentence), untilCancelled()]);
  }
  function playClip(url) {
    return new Promise(resolve => {
      const audio = new Audio(url);
      audio.playbackRate = globalThis.molipVoice ? globalThis.molipVoice.rate : 1;
      let done = false;
      const finish = ok => { if (done) return; done = true; if (currentAudio === audio) { currentAudio = null; finishClip = null; } resolve(ok); };
      audio.onended = () => finish(true);
      audio.onerror = () => finish(false);
      currentAudio = audio; finishClip = finish;
      audio.play().then(() => { if (cancelled) { audio.pause(); finish(true); } }).catch(() => finish(false));
    });
  }
  // A paused clip never fires `ended`: stopping must settle its promise, or the narration that
  // awaits it (and the panel's 진행 중 state behind it) would hang after 멈춤.
  function stopClip() {
    const finish = finishClip;
    if (currentAudio) { try { currentAudio.pause(); } catch {} currentAudio = null; }
    finishClip = null;
    if (finish) finish(false);
  }
  window.addEventListener('molip:tts-rate', event => { if (currentAudio) currentAudio.playbackRate = event.detail; });
  async function prefetch(actions, active) {
    if (!voiceOn() || !neural()) return;
    const sentences = [...new Set(actions.map(a => a && (a.action === 'say' ? a.text : a.say)).filter(Boolean).map(String))];
    if (!sentences.length) return;
    let next = 0, ready = 0;
    const progress = () => { if (active()) spotlight(null, `해설 음성을 준비해요. ${ready} / ${sentences.length}`); };
    progress();
    // Cache the entire problem before moving the screen. Limit simultaneous TTS requests.
    await Promise.all(Array.from({length: Math.min(3, sentences.length)}, async () => {
      while (active() && neural() && next < sentences.length) {
        await synthesize(sentences[next++]);
        ready++;
        progress();
      }
    }));
  }
  // Chromium drops onend for an utterance that gets garbage-collected, and ignores speak() in the
  // same tick as cancel(): keep the utterance referenced, and only cancel when something plays.
  let current = null;
  async function speak(sentence) {
    if (!sentence) return;
    if (voiceOn() && globalThis.molipVoice && molipVoice.name !== 'system' && !cancelled) {
      const url = await synthesize(String(sentence));
      if (cancelled) return;
      if (url && await playClip(url)) { lastSpeech = 'neural'; return; }
      lastSpeech = 'unavailable';
      throw new Error('Edge 음성을 재생하지 못했어요. 연결을 확인한 뒤 다시 재생해 주세요.');
    }
    lastSpeech = 'system';
    return speakWithSystemVoice(sentence);
  }
  let lastSpeech = '';
  // Told once per session: the neural voice gave up, or this device has no Korean voice.
  let toldFallback = false, toldNoKorean = false;
  window.addEventListener('molip:voice-fallback', event => {
    if (toldFallback) return;
    toldFallback = true;
    const reason = String(event.detail || '').slice(0, 80);
    if (globalThis.molipToast) molipToast('Edge 음성을 준비하지 못했어요. 연결을 확인한 뒤 다시 재생해 주세요. (' + reason + ')', 'warn');
  });
  function speakWithSystemVoice(sentence) {
    const length = String(sentence).length;
    if (!voiceOn() || !('speechSynthesis' in window) || !('SpeechSynthesisUtterance' in window)) {
      return sleep(Math.min(5000, 700 + length * 55)); // reading time, so the caption can be read
    }
    return new Promise(resolve => {
      const helpers = globalThis.molipSpeech;
      const synth = window.speechSynthesis;
      let done = false, timer = 0;
      const finish = () => { if (done) return; done = true; clearTimeout(timer); current = null; resolve(); };
      const start = () => {
        if (cancelled || !voiceOn()) { finish(); return; }
        const utterance = new SpeechSynthesisUtterance(globalThis.molipPronunciation.pronunciationText(sentence));
        utterance.lang = 'ko-KR';
        const korean = helpers && helpers.koreanVoice ? helpers.koreanVoice(synth.getVoices()) : null;
        if (korean) utterance.voice = korean;
        else if (!toldNoKorean && synth.getVoices().length) {
          toldNoKorean = true;
          if (globalThis.molipToast) molipToast('이 컴퓨터에 한국어 음성이 없어 자막으로만 보여 줘요. Windows 설정 → 시간 및 언어 → 언어 및 지역에서 한국어 음성 팩을 추가하면 소리가 나요.', 'warn');
        }
        // The same validated speed as the neural voice (assets/layout/voice.js), up to its fastest.
        const rate = globalThis.molipVoice ? globalThis.molipVoice.rate : 1.5;
        utterance.rate = rate;
        timer = setTimeout(finish, 3000 + length * 170 / rate);
        utterance.onend = finish; utterance.onerror = finish;
        current = utterance;
        try { synth.resume(); synth.speak(utterance); } catch { finish(); }
      };
      if (synth.speaking || synth.pending) { synth.cancel(); setTimeout(start, 150); } else start();
    });
  }
  function stopSpeech() { current = null; stopClip(); if ('speechSynthesis' in window) try { window.speechSynthesis.cancel(); } catch {} }

  async function typeCode(code, replace, active = () => !cancelled) {
    const api = window.molipCodeEditors;
    if (!api || !api.appendValue || !api.getValue) throw new Error('코드 편집기를 찾지 못했습니다');
    const current = api.getValue();
    if (current === null) throw new Error('이 미션에는 코드 편집기가 없습니다 (코딩 미션에서만 됩니다)');
    let body = String(code ?? '');
    if (!body.endsWith('\n')) body += '\n';
    if (!replace && current && !current.endsWith('\n')) body = '\n' + body;
    await animateEdit(replace ? 0 : current.length, current.length, body, active);
    return body.split('\n').filter(line => line.trim()).length;
  }

  const lineAt = (code, offset) => code.slice(0, offset).split('\n').length;
  const lastCodeLine = source => Math.max(1, source.trimEnd().split('\n').length);
  function focusCode(action, next) {
    const api = globalThis.molipCodeEditors;
    if (!api?.highlightLines) return;
    if (Array.isArray(action.lines)) { api.highlightLines(...action.lines); return; }
    const source = api.getValue() || '';
    if (action.action === 'run') { const line=lastCodeLine(source); api.highlightLines(line,line,true); return; }
    if (action.target === 'output') return;
    const edit = action.action === 'patch_code' ? action : next?.action === 'patch_code' ? next : null;
    if (edit && edit.before) {
      const from = source.indexOf(edit.before);
      if (from >= 0) { api.highlightLines(lineAt(source, from), lineAt(source, from + edit.before.length - 1)); return; }
    }
    if (action.action === 'set_code') {
      const desired = String(action.code ?? '');
      let from = 0;
      while (from < source.length && from < desired.length && source[from] === desired[from]) from++;
      api.highlightLines(source === desired ? lastCodeLine(source) : lineAt(source, from));
    } else if (action.action === 'type_code') api.highlightLines(source.split('\n').length);
    else if (action.target === 'editor') {
      if (!document.querySelector('.cm-narration-line')) api.highlightLines(1);
    } else if (!/^(?:lines|editor|code):/.test(String(action.target || ''))) api.highlightLines(null);
  }
  // Retain unchanged code and type only the changed fragments, including replacements in place.
  // The keystrokes come from molipEditPlan.steps (below), which never removes a line break that
  // the edit keeps: `return fee;\n    }` → `return fee + 1000;\n    }` types " + 1000" only, so
  // the `}` line stays on its own line throughout the animation.
  async function animateEdit(from, to, insert, active = () => !cancelled) {
    const api = globalThis.molipCodeEditors;
    const source = api.getValue();
    const element = document.querySelector('textarea[data-code-editor]');
    let expected = source;
    const ensureUnchanged = () => {
      if (api.getValue() !== expected || (element && !element.isConnected)) {
        const message = '코드가 바뀌었어요. 해설을 다시 재생해 주세요.';
        globalThis.molipToast?.(message, 'warn');
        throw new Error(message);
      }
    };
    const replace = (from,to,text) => {
      ensureUnchanged();
      expected = expected.slice(0,from) + text + expected.slice(to);
      return api.replaceRange ? api.replaceRange(from,to,text) : api.setValue(expected);
    };
    const delay = ms => sleep(ms * 1.5 / (globalThis.molipVoice?.rate || 1.5));
    const target = source.slice(0, from) + insert + source.slice(to);
    let startLine = lineAt(source, from);
    api.highlightLines?.(startLine, lineAt(source, Math.max(from, to - 1)));
    for (const step of editPlan.steps(source, from, to, insert)) {
      await waitWhilePaused(); if (!active()) return;
      replace(step.from, step.to, step.insert);
      const offset = step.from + step.insert.length, current = api.getValue();
      startLine = Math.min(startLine, lineAt(current, step.from));
      api.highlightLines?.(startLine, Math.max(startLine, lineAt(current, Math.max(step.from, offset - 1))));
      spotlight('editor',caption?.textContent || '');
      await delay(step.insert ? 45 : 35);
    }
    if (active()) {
      ensureUnchanged();
      if (expected !== target) throw new Error('해설 편집 결과가 준비한 코드와 달라요.');
    }
  }

  async function demonstrateAnswer(value) {
    const bridge = document.querySelector('.answer-state-bridge');
    if (!bridge) throw new Error('이 문제의 답안 입력을 찾지 못했어요.');
    bridge.value = value;
    bridge.dispatchEvent(new Event('input', {bubbles:true}));
    await sleep(60);
    return '답안을 비교해 봐요.';
  }
  // A command such as docker pull may legitimately take minutes: the action may allow up to 15 minutes.
  const terminalWait = a => Math.min(900, Math.max(15, Number(a?.wait_seconds) || 15)) * 1000;
  async function readTerminal(command, active, expected, wait = 15000) {
    const tutor = explanationSession ? explanationSession.gitTutor() : window.molipGitTutor;
    const terminal = window.mq3GitDemoTerminal;
    if (!tutor || !terminal) throw new Error('Git 해설 터미널이 없어요.');
    const owner = tutor.owner;
    const before = terminal.text(owner).trimEnd();
    const count = () => terminal.text(owner).split('\n').filter(line => line.trim() === expected).length;
    const previous = count();
    if (!await terminal.typeCommand(command, owner)) return '해설을 멈췄어요.';
    const deadline = Date.now() + wait;
    while (active()) {
      const output = terminal.text(owner).trimEnd();
      if (output !== before && /(?:\$|>)\s*$/.test(output) && (expected == null || count() > previous)) return '출력을 확인했어요.';
      if (Date.now() > deadline) throw new Error('명령의 출력을 확인하지 못했어요.');
      await sleep(30);
    }
    return '해설을 멈췄어요.';
  }
  const handlers = {
    // Click or type in the tutor's own web preview (assets/layout/web-bridge.js answers inside it).
    async web_action(a, active) {
      const frame = document.querySelector('iframe[title="해설 웹 미리보기"]');
      if (!frame?.contentWindow) throw new Error('해설 웹 미리보기가 없어요. 먼저 실행하세요.');
      if (!['click', 'fill', 'read', 'width'].includes(a.do) || typeof a.selector !== 'string') throw new Error('웹 동작을 확인하세요.');
      // A width change resizes the tutor's own preview so media queries such as md: apply, then reads.
      if (a.do === 'width') {
        const width = Number(a.value);
        if (!(width >= 200 && width <= 1600)) throw new Error('미리보기 폭을 확인하세요.');
        frame.style.width = `${width}px`; frame.style.maxWidth = 'none';
        await sleep(250);
      }
      const id = Math.random().toString(36).slice(2);
      const reply = new Promise((resolve, reject) => {
        const timer = setTimeout(() => { removeEventListener('message', receive); reject(new Error('웹 미리보기가 응답하지 않아요.')); }, 3000);
        function receive(event) {
          if (event.source !== frame.contentWindow || event.data?.type !== 'mq3-web-result' || event.data.id !== id) return;
          clearTimeout(timer); removeEventListener('message', receive); resolve(event.data);
        }
        addEventListener('message', receive);
      });
      frame.contentWindow.postMessage({type: 'mq3-web-action', id, do: a.do === 'width' ? 'read' : a.do, selector: a.selector, value: a.value, read: a.read, style: a.style}, '*');
      const result = await reply;
      if (!active()) return '해설을 멈췄어요.';
      if (!result.ok) throw new Error(`웹 미리보기에서 ${a.selector}를 찾지 못했어요.`);
      return `웹 화면: ${result.text}`;
    },
    async bash_command(a, active) {
      if(typeof a.command!=='string'||!a.command||a.command.length>4000||/[\r\n\0]/.test(a.command))throw new Error('Bash 명령을 확인하세요.');
      return readTerminal(a.command,active,a.expected,terminalWait(a));
    },
    async vim_wait(a,active) {
      const terminal=window.mq3GitDemoTerminal;const tutor=explanationSession ? explanationSession.gitTutor() : window.molipGitTutor;
      const deadline=Date.now()+15000;
      while(active()){
        const progress=terminal?.vimState(tutor?.owner);
        if(progress && (a.passed ? progress.passed : progress.state))return 'Vim의 실제 상태를 확인했어요.';
        if(Date.now()>deadline)throw new Error('Vim 상태를 확인하지 못했어요.');
        await sleep(30);
      }
    },
    async vim_open(a, active) {
      const tutor=explanationSession ? explanationSession.gitTutor() : window.molipGitTutor;
      const terminal=window.mq3GitDemoTerminal;
      if(!tutor||!terminal)throw new Error('해설 터미널이 없어요.');
      if(!await terminal.typeCommand('vim memo.txt',tutor.owner))return '해설을 멈췄어요.';
      const deadline=Date.now()+15000;
      while(active()){
        const text=terminal.text(tutor.owner);
        if(/"memo.txt"/.test(text)&&/\d+L/.test(text))return 'Vim에서 메모를 열었어요.';
        if(Date.now()>deadline)throw new Error('Vim 화면을 확인하지 못했어요.');
        await sleep(30);
      }
    },
    async vim_keys(a, active) {
      const tutor=explanationSession ? explanationSession.gitTutor() : window.molipGitTutor;
      const terminal=window.mq3GitDemoTerminal;
      if(!tutor||!terminal||typeof a.keys!=='string'||a.keys.length>1000)throw new Error('Vim 키 입력을 확인하세요.');
      if(!await terminal.typeKeys(a.keys,tutor.owner))return '해설을 멈췄어요.';
      if(a.wait_prompt){
        const direct=document.querySelector('#git-demo-terminal')?.dataset.vim==='true';
        const deadline=Date.now()+15000;
        while(active()){
          if((direct && terminal.vimState(tutor.owner)?.state?.exited)||(!direct && /\$\s*$/.test(terminal.text(tutor.owner).trimEnd())))return '편집을 마치고 터미널로 돌아왔어요.';
          if(Date.now()>deadline)throw new Error('Vim 종료를 확인하지 못했어요.');
          await sleep(30);
        }
      }else{await sleep(100);return 'Vim 키를 입력했어요.';}
    },
    async inspect_folder(a, active) {
      // Fixed read-only commands only; each action runs exactly one command.
      if (!['pwd', 'ls'].includes(a.command)) throw new Error('폴더 확인 명령을 확인하세요.');
      return readTerminal(a.command, active);
    },
    async write_memo(a, active) {
      if (!['첫 메모', '둘째 메모', '셋째 메모'].includes(a.content)) throw new Error('메모 내용을 확인하세요.');
      return readTerminal('echo "' + a.content + '" > memo.txt', active);
    },
    async read_memo(a, active) {
      return readTerminal('cat memo.txt', active, String(a.expected || '').trim());
    },
    async git_command(a, active) {
      const tutor=explanationSession ? explanationSession.gitTutor() : window.molipGitTutor;
      if (!tutor || !Array.isArray(a.args)) throw new Error('Git 해설 터미널이 없어요.');
      const completed=await Promise.race([tutor.command(a.args),untilCancelled()]);
      if (!active()) return '해설을 멈췄어요.';
      if (!completed) throw new Error('Git 명령의 완료를 확인하지 못했어요.');
      return '실제 Git 명령이 끝났어요.';
    },
    async git_graph(a, active) {
      const tutor=explanationSession ? explanationSession.gitTutor() : window.molipGitTutor;
      if (!tutor?.graph) throw new Error('커밋 그래프를 찾지 못했어요.');
      const ready=await Promise.race([tutor.graph(),untilCancelled()]);
      if(active()&&!ready)throw new Error('커밋 그래프를 확인하지 못했어요.');
      return '실제 저장소의 그래프를 확인했어요.';
    },
    choose_answer: a => demonstrateAnswer(String(a.id ?? '')),
    order_answer: a => demonstrateAnswer(JSON.stringify(a.ids ?? [])),
    fill_answer: a => demonstrateAnswer(String(a.value ?? '')),
    async set_input(a) {
      const input = document.querySelector('.result-pane textarea[aria-label="실행 입력"]');
      if (!input) throw new Error('실행 입력 칸을 찾지 못했어요.');
      input.value = String(a.value ?? '');
      input.dispatchEvent(new Event('input', {bubbles:true}));
      await sleep(40);
      return '해설의 첫 예제 입력을 준비했어요.';
    },
    async say(a) {
      // The spotlight and speech were started by run(); nothing else to do.
      return '설명: ' + String(a.text || '').slice(0, 80);
    },
    async type_code(a, active) {
      spotlight('editor', a.say);
      const spoken = speak(a.say);
      const lines = await typeCode(a.code, !!a.replace, active);
      await spoken;
      await sleep(250);
      return `코드 ${lines}줄을 입력했습니다.`;
    },
    async set_code(a, active) {
      const api = window.molipCodeEditors;
      if (!api || !api.setValue) throw new Error('코드 편집기를 찾지 못했습니다');
      const source = api.getValue();
      if (source == null) throw new Error('이 미션에는 코드 편집기가 없습니다 (코딩 미션에서만 됩니다)');
      const desired = String(a.code ?? '');
      let from = 0, tail = 0;
      while (from < source.length && from < desired.length && source[from] === desired[from]) from++;
      while (tail < source.length - from && tail < desired.length - from && source[source.length - tail - 1] === desired[desired.length - tail - 1]) tail++;
      const spoken = speak(a.say);
      if (source !== desired) await animateEdit(from, source.length - tail, desired.slice(from, desired.length - tail), active);
      await spoken;
      await sleep(300);
      return '코드를 편집기에 넣었습니다.';
    },
    async patch_code(a, active) {
      if (a.file) {
        // A Compose step's narration edits one of several files: show that file's tab first.
        const tab = [...document.querySelectorAll('[data-editor-tab]')].find(t => t.dataset.editorTab === a.file && t.getClientRects().length);
        if (!tab) throw new Error(`${a.file} 편집기 탭을 찾지 못했어요`);
        if (tab.getAttribute('aria-selected') !== 'true') {
          tab.click();
          const deadline = Date.now() + 5000;
          while (!(window.molipCodeEditors?.getValue() ?? '').includes(String(a.before ?? ''))) {
            if (Date.now() > deadline) throw new Error(`${a.file}을 편집기에 열지 못했어요`);
            await sleep(30);
          }
        }
      }
      const api = window.molipCodeEditors;
      if (!api?.setValue || !api?.getValue) throw new Error('코드 편집기를 찾지 못했습니다');
      const current = api.getValue();
      if (current == null) throw new Error('코딩 미션에서 실행하세요');
      const before = String(a.before ?? '');
      const index = current.indexOf(before);
      if (!before || index < 0 || current.indexOf(before, index + 1) >= 0)
        throw new Error('바꿀 코드 조각이 정확히 한 곳에 있어야 해요');
      const spoken = speak(a.say);
      await animateEdit(index, index + before.length, String(a.after ?? ''), active);
      await spoken;
      await sleep(300);
      return '코드 조각을 바꿨어요.';
    },
    async fill_blanks(a) {
      const inputs = [...document.querySelectorAll('input.code-blank')];
      if (!inputs.length) throw new Error('채울 빈칸이 없습니다');
      const values = Array.isArray(a.values) ? a.values : [];
      values.forEach((value, i) => {
        if (!inputs[i]) return;
        inputs[i].value = String(value);
        inputs[i].dispatchEvent(new Event('input', { bubbles: true }));
      });
      await sleep(300);
      return `빈칸 ${Math.min(inputs.length, values.length)}개를 채웠습니다.`;
    },
    async run(a, active) {
      const button = byText('.pane-actions button', '코드 실행');
      if (!button) throw new Error('코드 실행 버튼이 없습니다 (코딩 미션에서만 됩니다)');
      const previous=document.querySelector('.result-pane')?.dataset.executionId ?? null;
      button.click();
      await sleep(40);
      await waitIdle(button,180000,previous,active);
      return '실행 결과:\n' + (workspaceReport() || '(출력 없음)');
    },
    async submit(a, active) {
      const button = byText('.pane-actions button', '제출');
      if (!button) throw new Error('제출 버튼이 없습니다 (코딩 미션에서만 됩니다)');
      button.click();
      await waitIdle(button,180000,null,active);
      await sleep(400);
      const passed = cleared();
      return (passed ? '제출 결과: 통과. 미션 클리어로 기록됐습니다 (정답 카드가 떠 있습니다).\n' : '제출 결과:\n') + (workspaceReport() || '(출력 없음)');
    },
    async answer_quiz(a) {
      const sections = [...document.querySelectorAll('.quiz-question')];
      if (!sections.length) throw new Error('이 미션에는 퀴즈나 확인 문항이 없습니다');
      const answers = a.answers && typeof a.answers === 'object' ? a.answers : {};
      const notes = [];
      for (const [key, value] of Object.entries(answers)) {
        const section = question(key);
        if (!section) { notes.push(`${key}번 문항이 없습니다 (이미 맞힌 문항이거나 번호가 다릅니다)`); continue; }
        const want = String(value).trim();
        const radios = [...section.querySelectorAll('input[type=radio]')];
        if (radios.length) {
          // Exact text, then 1-based number (what the compiled 해설 sends), then containment:
          // assets/layout/quiz-pick.js, shared with tests/js/quiz-pick.test.mjs.
          const label = r => normalize((r.closest('.quiz-option') || r.parentElement || r).textContent);
          const pick = radios[globalThis.molipQuizPick.pickOption(radios.map(label), want)];
          if (!pick) { notes.push(`${key}번: 보기 "${want}"를 찾지 못했습니다. 보기: ${radios.map(r => label(r)).join(' | ')}`); continue; }
          if (a.say) { spotlight(pick.closest('.quiz-option') ? `option:${key}:${radios.indexOf(pick) + 1}` : `quiz:${key}`, a.say); }
          pick.click();
        } else if (section.querySelector('.table-select')) {
          // A table: the answer is 1-based row/column numbers ("1,3,5"); tick exactly those.
          const wanted = new Set(want.split(',').map(s => Number(s.trim()) - 1).filter(n => Number.isInteger(n) && n >= 0));
          const boxes = [...section.querySelectorAll('.table-select input[type=checkbox]')];
          if (!boxes.length) { notes.push(`${key}번: 고를 표가 없습니다`); continue; }
          if (a.say) spotlight(`quiz:${key}`, a.say);
          for (const box of boxes) {
            const index = Number(box.dataset.index);
            if (box.checked !== wanted.has(index)) { box.click(); await sleep(120); }
          }
        } else {
          const input = section.querySelector('input:not([type=radio]):not([type=checkbox])');
          if (!input) { notes.push(`${key}번: 입력칸이 없습니다`); continue; }
          if (a.say) spotlight(`quiz:${key}`, a.say);
          input.value = want;
          input.dispatchEvent(new Event('input', { bubbles: true }));
        }
        if (a.say) await sleep(500);
      }
      await sleep(300);
      // submit:false ticks the answers and stops; a later call with no answers grades.
      if (a.submit === false) return `답을 넣었습니다: ${Object.keys(answers).join(', ')}번` + (notes.length ? '\n' + notes.join('\n') : '');
      const button = document.querySelector('.quiz-actions .primary');
      if (button && !button.disabled) { if (a.say && !Object.keys(answers).length) spotlight('quiz_submit', a.say); button.click(); await waitIdle(button); }
      await sleep(300);
      const status = text('.quiz-actions ~ .execution-status, .concept-flow .execution-status, .execution-status', 600) + (cleared() ? ' · 미션 클리어 (정답 카드가 떠 있습니다)' : '');
      const banner = text('.clear-banner', 200);
      return ['채점 결과: ' + (status || '(상태 없음)'), banner, ...notes].filter(Boolean).join('\n');
    },
    async next() { const popup = popupButton('다음 미션 ›'); const b = popup || byText('.header-navigation button', '다음 →'); if (!b || b.disabled) throw new Error('다음 미션으로 갈 수 없습니다'); b.click(); await sleep(600); return '다음 미션으로 이동했습니다: ' + text('.reading-mission h2, .problem-pane h2, .slides-mission h2', 120); },
    async prev() { const b = byText('.header-navigation button', '← 이전'); if (!b || b.disabled) throw new Error('이전 미션으로 갈 수 없습니다'); b.click(); await sleep(600); return '이전 미션으로 이동했습니다: ' + text('.reading-mission h2, .problem-pane h2, .slides-mission h2', 120); },
    async goto(a) { const cells = document.querySelectorAll('.mission-cell'); const cell = cells[Number(a.mission) - 1]; if (!cell) throw new Error(`이 단원에는 ${a.mission}번 미션이 없습니다 (미션 ${cells.length}개)`); cell.click(); await sleep(600); return `${a.mission}번 미션으로 이동했습니다: ` + text('.reading-mission h2, .problem-pane h2, .slides-mission h2', 120); },
    async next_slide() {
      // Steps by source slide (the Markdown's `---` count the model sees): a comic's extra panels
      // are shown briefly on the way, so the narration and the deck stay in step.
      const host = document.querySelector('.slides-host');
      if (host && host.molipSlides) {
        if (!(await host.molipSlides.nextSource(1500))) throw new Error('넘길 장이 없습니다');
        await sleep(300);
        return '다음 장으로 넘겼습니다 (' + host.molipSlides.sourceIndex(host.molipSlides.index) + '번째 장): ' + text('.slides-counter', 20);
      }
      const b = byText('.slides-bar button', '다음 장 →'); if (!b || b.disabled) throw new Error('넘길 장이 없습니다'); b.click(); await sleep(300); return '다음 장으로 넘겼습니다: ' + text('.slides-counter', 20);
    },
    async finish_slides(a) {
      // {quiet: true} (/tour-all) marks the deck watched where it stands, no presentation.
      const b = byText('button', '다 봤어요 · 미션 완료'); if (!b) throw new Error('슬라이드 미션이 아닙니다');
      if (a && a.quiet) { if (!b.disabled) b.click(); await sleep(400); return '슬라이드 미션을 완료로 표시했습니다.'; }
      // Presenting: the next mission, if it is a deck, opens in presentation mode too (slides.js mount).
      const host = document.querySelector('.slides-host');
      if (host && host.classList.contains('slides-presenting') && globalThis.molipSlides) globalThis.molipSlides.carryPresenting = Date.now();
      if (!b.disabled) b.click(); await sleep(400); return '슬라이드 미션을 완료로 표시했습니다.';
    },
  };
  // Where each action's spotlight goes when it carries "say" (type_code places its own).
  const DEFAULT_TARGET = {
    git_command: () => '#git-demo-terminal',
    git_graph: () => '#git-demo-terminal + .git-graph-panel',
    choose_answer: a => `answer:${a.id}`, order_answer: () => '.answer-order', fill_answer: () => '[aria-label="빈칸 답안"]',
    web_action: a => `web:${a.read || a.selector}`,
    say: a => a.target || null, set_code: () => 'editor', patch_code: () => 'editor', fill_blanks: () => 'blanks', run: () => 'run', submit: () => 'submit',
    answer_quiz: () => 'quiz', next: () => 'nav', prev: () => 'nav', goto: () => 'missions', next_slide: () => 'slides', finish_slides: () => 'slides',
  };
  let narrationRun = 0;
  let webFocus = '';
  // A session owns both its restoration snapshot and its DOM/Git targets.
  class ExplanationSession {
    constructor(root, owner) {
      this.root = root;
      this.owner = owner ?? root.dataset.explanationSession ?? null;
      // A separate Java demo owns its own editor and disk state. A late JS restore
      // must not apply that teacher source to the student editor after Rust switches back.
      this.code = root.querySelector('.java-build-workspace') ? null : globalThis.molipCodeEditors?.getValue() ?? null;
      this.fields = [...root.querySelectorAll('.answer-interaction input, .answer-state-bridge, .run-input textarea')].map(field => [field, field.value, field.checked]);
      this.tutor = globalThis.molipGitTutor;
      this.terminal = root.querySelector('#git-demo-terminal');
      this.blockInput = event => {
        if (!event.isTrusted || event.target.closest?.('[data-explanation-stop], .narration-speed')) return;
        if (event.type === 'keydown' && (['Tab','Escape','Home','End','PageUp','PageDown'].includes(event.key) || event.key.startsWith('Arrow'))) return;
        if (event.type === 'keydown' && (event.ctrlKey || event.metaKey) && ['a','c'].includes(event.key.toLowerCase())) return;
        event.preventDefault();event.stopImmediatePropagation();
      };
      for (const name of ['click','keydown','beforeinput','paste','drop']) root.addEventListener(name, this.blockInput, true);
    }
    current() { return this.root.isConnected && (this.owner === null || this.root.dataset.explanationSession === this.owner); }
    gitTutor() {
      if (!this.current() || this.tutor !== globalThis.molipGitTutor) return null;
      const terminalOwner = this.terminal?.dataset.terminalSession;
      return !terminalOwner || this.tutor?.owner === terminalOwner ? this.tutor : null;
    }
    restore() {
      for (const name of ['click','keydown','beforeinput','paste','drop']) this.root.removeEventListener(name, this.blockInput, true);
      if (!this.current()) return;
      if (this.code !== null) globalThis.molipCodeEditors?.setValue(this.code);
      for (const [field, value, checked] of this.fields) {
        if (!field.isConnected) continue;
        field.value = value;
        if (checked !== undefined) field.checked = checked;
        if (field.matches('.answer-state-bridge, .run-input textarea')) field.dispatchEvent(new Event('input', {bubbles:true}));
      }
    }
    static retireGitTutor(owner) {
      const tutor=globalThis.molipGitTutor;
      if (tutor?.owner !== owner) return false;
      tutor.dispose();
      delete globalThis.molipGitTutor;
      return true;
    }
  }
  let explanationSession = null;
  function restoreExplanation() {
    const session=explanationSession;
    explanationSession=null;
    session?.restore();
  }
  async function runExplanation(actions, options = {}) {
    stop();
    const root=options.root || document.querySelector('.repository-task') || document.body;
    if (!root.isConnected || (options.owner != null && root.dataset.explanationSession !== options.owner)) return '해설이 이미 끝났어요.';
    const session=new ExplanationSession(root,options.owner);
    explanationSession=session;
    // A demonstration can execute examples, but never submit, advance or grant completion.
    const allowed = new Set(['vim_wait', 'bash_command', 'vim_open', 'vim_keys', 'write_memo', 'inspect_folder', 'read_memo', 'git_command', 'git_graph', 'say', 'set_code', 'patch_code', 'type_code', 'set_input', 'run', 'web_action', 'choose_answer', 'order_answer', 'fill_answer']);
    try { return await run(Array.isArray(actions) ? actions.filter(action => allowed.has(action?.action)) : [], true); }
    finally { if (explanationSession === session) restoreExplanation(); }
  }
  async function run(actions, explanation = false, options = {}) {
    if (!explanation && explanationSession) stop();
    if (!Array.isArray(actions)) return '동작 목록이 배열이 아닙니다.';
    captionSource = actions.flatMap(action => ['code','before','after','input','value'].map(key=>action?.[key] ?? '')).join('\n');
    const runId = ++narrationRun;
    webFocus = '';
    if (options.forceVoice) forcedVoiceRun = runId;
    const session = explanation ? explanationSession : null;
    const active = () => !cancelled && runId === narrationRun && (!session || session.current());
    replyRun++; stopSpeech(); releaseCancelWaiters(); clearSpot();
    cancelled = false; paused = false; running = true;
    globalThis.molipVoice?.resetFailure?.();
    const lines = [];
    try {
    const initialAudio = Number.isInteger(options.prefetchLimit) ? actions.slice(0, Math.max(0, options.prefetchLimit)) : actions;
    await Promise.race([prefetch(initialAudio, active), untilCancelled()]);
    if (!active()) return '해설 준비를 멈췄어요.';
    clearSpot();
    // A deck script (it ends with finish_slides) is presented full screen, like a class, and
    // starts from the first slide: its lines and next_slide steps count from the top, so a deck
    // left on slide 5 would otherwise have the voice a few slides behind the picture.
    if (actions.some(a => a && a.action === 'finish_slides' && !a.quiet)) {
      const host = document.querySelector('.slides-host');
      if (host && host.molipSlides && host.molipSlides.first) host.molipSlides.first();
      if (host && host.molipPresent && !host.classList.contains('slides-presenting')) { host.molipPresent(true); await sleep(300); }
    }
      for (const [i, action] of actions.entries()) {
        await waitWhilePaused();
        if (!active()) { lines.push(`${i + 1}. 학생이 멈춤을 눌러 여기서 중단했습니다.`); break; }
        const name = action && action.action;
        const handler = handlers[name];
        if (!handler) { lines.push(`${i + 1}. ${name}: 모르는 동작입니다 (가능: ${Object.keys(handlers).join(', ')})`); continue; }
        try {
          if(name==='web_action')webFocus=action.read || action.selector || '';
          // CSS explanations often name the selector in the highlighted code.
          // Follow that exact selector when the next sentence describes its result.
          const css = name==='patch_code'?action.after: String(action.target||'').startsWith('code:')?String(action.target).slice(5):'';
          const selector=String(css||'').match(/^([.#]?[a-zA-Z][\w.#:[\]="' >+~(),-]*)\s*\{/);
          if(selector)webFocus=selector[1].trim();
          const sentence = name === 'say' ? action.text : action.say;
          showMemory(action.diagram);
          focusCode(action, actions[i + 1]);
          if (name !== 'type_code' && name !== 'answer_quiz') {
            spotlight(action.target || (DEFAULT_TARGET[name] ? DEFAULT_TARGET[name](action) : null), sentence);
          }
          if (sentence && !['type_code', 'answer_quiz', 'patch_code', 'set_code'].includes(name)) {
            await speak(sentence);
            await waitWhilePaused();
            if (!active()) { lines.push(`${i + 1}. 학생이 멈춤을 눌러 여기서 중단했습니다.`); break; }
          } else if (sentence && name === 'answer_quiz') {
            spotlight('quiz', sentence);
            await speak(sentence);
          }
          if (!active()) break;
          lines.push(`${i + 1}. ${name}: ${await handler(action, active)}`);
          if (sentence) await sleep(350);
        } catch (error) {
          lines.push(`${i + 1}. ${name}: 오류 - ${error && error.message ? error.message : error}`);
          break;
        }
      }
    } finally {
      if (runId === narrationRun) {
      running = false; paused = false;
      if(forcedVoiceRun===runId)forcedVoiceRun=0;
      stopSpeech();
      clearSpot();
      releaseCancelWaiters();
      }
    }
    return lines.join('\n');
  }
  // Read a chat answer aloud (the 소리 switch is on): prose only, code blocks skipped, one
  // sentence at a time so 멈춤 and a new question cut it off cleanly. No spotlight, no caption.
  let replyRun = 0;
  async function speakReply(text, force) {
    if ((!voice && !force) || running) return false;
    const run = ++replyRun;
    stopSpeech();
    cancelled = false;
    // 🔊 읽기 on a message reads it even while the switch is off.
    const restore = voice;
    if (force) voice = true;
    try {
    const prose = String(text || '')
      .replace(/```[\s\S]*?```/g, ' ')
      .replace(/^#{1,6}\s*/gm, '').replace(/^\s*[-*]\s+/gm, '').replace(/^\s*\d+\.\s+/gm, '')
      .replace(/\*\*(.+?)\*\*/g, '$1').replace(/`([^`\n]+)`/g, '$1').replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
      .replace(/\s+/g, ' ').trim();
    if (!prose) return false;
    const helpers = globalThis.molipSpeech;
    const sentences = helpers && helpers.speechSentences ? helpers.speechSentences(prose).map(s => s.text) : [prose];
    if (neural()) for (const sentence of sentences) synthesize(sentence);
    for (const sentence of sentences) {
      if (cancelled || run !== replyRun || running) break;
      await speak(sentence);
    }
    return run === replyRun;
    } finally { voice = restore; }
  }
  // Stop reading a reply without touching a narration that may be running.
  function stopReply() { replyRun++; if (!running) stopSpeech(); }
  function stop() { cancelled = true; paused = false; replyRun++; cancelAnimationFrame(glideFrame); stopSpeech(); releaseCancelWaiters(); clearSpot(); restoreExplanation(); }
  function setVoice(on) { voice = !!on; if (!voice) stopSpeech(); return voice; }
  function setVoiceName(name) { return globalThis.molipVoice ? globalThis.molipVoice.setName(name) : String(name || 'system'); }
  async function runOverview(actions, dialog) {
    if(!dialog?.open)return '학습 정보 창을 먼저 여세요.';
    stop();
    const abort=()=>stop();
    dialog.addEventListener('close',abort);
    dialog.dataset.overviewRunning='true';
    // A course can contain many lessons: start after the first few sentences.
    // Remaining clips use the same cache on demand instead of preloading the whole course.
    try{return await run(actions.filter(a=>a.action==='say'),false,{forceVoice:true,prefetchLimit:3});}
    finally{dialog.removeEventListener('close',abort);dialog.dataset.overviewRunning='false';}
  }
  globalThis.molipAgent = { runOverview, retireGitTutor: ExplanationSession.retireGitTutor, run, runExplanation, stop, pause, resume, speakReply, stopReply, get paused() { return paused; }, get running() { return running; }, setVoice, setVoiceName, resolveTarget, glideTo, get voice() { return voice; }, get voiceName() { return globalThis.molipVoice ? globalThis.molipVoice.name : 'system'; }, get lastSpeech() { return lastSpeech; }, get playbackRate() { return currentAudio ? currentAudio.playbackRate : null; }, actions: Object.keys(handlers) };
})();
