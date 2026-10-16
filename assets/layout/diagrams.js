// Draw ```mapping fences from course Markdown as "one input → one output" pictures.
//
//   ```mapping
//   제목: map(int, ['10000', '3'])
//   함수: int
//   '10000' → 10000
//   '3' → 3
//   ```
//
// Each line with an arrow becomes a row: the left box is the value going in, the arrow
// carries the function name, the right box is the value coming out. The footer states
// that N inputs give N outputs, which is the point of map.
//
// `종류: 비교` draws the same rows side by side with no arrow and no footer: two things
// compared line by line (리스트 vs 딕셔너리), not one turning into the other.
(function () {
  'use strict';
  if (globalThis.molipDiagrams || typeof document === 'undefined') return;
  const esc = s => s.replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  function parse(text) {
    const spec = { title: '', fn: '', left: '들어가는 값', right: '나오는 값', rows: [], compare: false };
    for (const raw of text.split('\n')) {
      const line = raw.trim();
      if (!line) continue;
      if (line.startsWith('제목:')) spec.title = line.slice(3).trim();
      else if (line.startsWith('종류:')) spec.compare = line.slice(3).trim() === '비교';
      else if (line.startsWith('함수:')) spec.fn = line.slice(3).trim();
      else if (line.startsWith('왼쪽:')) spec.left = line.slice(3).trim();
      else if (line.startsWith('오른쪽:')) spec.right = line.slice(4).trim();
      else {
        const parts = line.split(/\s*(?:→|->)\s*/);
        if (parts.length === 2) spec.rows.push(parts);
      }
    }
    return spec;
  }

  // Rough text width: Hangul and CJK are about one em, Latin and digits about 0.6 em.
  function textWidth(text, size) {
    let w = 0;
    for (const ch of text) w += (/[ᄀ-ᇿ　-〿가-힯㄰-㆏＀-￯]/.test(ch) ? 1 : 0.6) * size;
    return w;
  }

  // Fit a label into a box: shrink the font a little, then fold into two lines at a space
  // near the middle (after a comma when there is one), never inside quotes or brackets.
  // Text with no place to fold (a code call) just keeps shrinking.
  function fit(text, width) {
    const inner = width - 20;
    for (const size of [16, 15, 14, 13, 12]) if (textWidth(text, size) <= inner) return { lines: [text], size };
    const cut = pick(text);
    if (!cut) {
      for (const size of [11, 10, 9]) if (textWidth(text, size) <= inner) return { lines: [text], size };
      return { lines: [text], size: 9 };
    }
    const lines = [text.slice(0, cut).trim(), text.slice(cut).trim()];
    for (const size of [13, 12, 11, 10]) if (lines.every(l => textWidth(l, size) <= inner)) return { lines, size };
    return { lines, size: 10 };
  }

  function pick(text) {
    // A label that is one quoted sentence ("이 파일로 … 맞혀 줘") folds like plain text.
    const wrapped = text.length > 2 && (text[0] === '"' || text[0] === "'") && text[text.length - 1] === text[0];
    const mid = text.length / 2;
    let best = 0, score = Infinity, depth = 0, quote = '';
    for (let i = wrapped ? 1 : 0; i < text.length - (wrapped ? 1 : 0); i++) {
      const ch = text[i];
      if (quote) { if (ch === quote) quote = ''; continue; }
      if (ch === "'" || ch === '"') { quote = ch; continue; }
      if (ch === '(' || ch === '[' || ch === '{') depth++;
      else if (ch === ')' || ch === ']' || ch === '}') depth--;
      else if (ch === ' ' && depth === 0 && i > 0 && i < text.length - 1) {
        const after = text[i - 1] === ',' || text[i - 1] === '·';
        const d = Math.abs(i - mid) - (after ? 3 : 0);
        if (d < score) { best = i; score = d; }
      }
    }
    return best;
  }

  function label(x, cx, lines, size, mid, mono, fill) {
    if (lines.length === 1) return `<text x="${cx}" y="${mid + size * 0.36}" text-anchor="middle" font-family="${mono}" font-size="${size}" fill="${fill}">${esc(lines[0])}</text>`;
    const gap = size + 3;
    return `<text x="${cx}" y="${mid - gap / 2 + size * 0.36}" text-anchor="middle" font-family="${mono}" font-size="${size}" fill="${fill}">${esc(lines[0])}</text>`
      + `<text x="${cx}" y="${mid + gap / 2 + size * 0.36}" text-anchor="middle" font-family="${mono}" font-size="${size}" fill="${fill}">${esc(lines[1])}</text>`;
  }

  function svg(spec) {
    const compare = spec.compare;
    const W = 720;
    const lx = compare ? 40 : 60, lw = compare ? 300 : 210, rx = compare ? 380 : 450, rw = compare ? 300 : 210;
    const top = (spec.title ? 46 : 12) + 28;
    const mono = 'Consolas, "Malgun Gothic", monospace';
    // Each row is as tall as its longer label needs: one line (34) or two (50).
    const rows = spec.rows.map(([a, b]) => {
      const fa = fit(a, lw), fb = fit(b, rw);
      const two = fa.lines.length > 1 || fb.lines.length > 1;
      return { fa, fb, boxH: two ? 50 : 34 };
    });
    const H = top + rows.reduce((h, r) => h + r.boxH + 14, 0) + (compare ? 8 : 44);
    let s = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(spec.title || '대응 그림')}">`;
    s += '<defs><marker id="mapping-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10z" fill="#9fe3c6"/></marker></defs>';
    if (spec.title) s += `<text x="${W / 2}" y="28" text-anchor="middle" font-family="${mono}" font-size="17" font-weight="700" fill="#a9d9ff">${esc(spec.title)}</text>`;
    const headY = top - 10;
    s += `<text x="${lx + lw / 2}" y="${headY}" text-anchor="middle" font-size="13" fill="#9ab0c2">${esc(spec.left)}</text>`;
    s += `<text x="${rx + rw / 2}" y="${headY}" text-anchor="middle" font-size="13" fill="#9ab0c2">${esc(spec.right)}</text>`;
    let y = top;
    rows.forEach(({ fa, fb, boxH }) => {
      const mid = y + boxH / 2;
      s += `<rect x="${lx}" y="${y}" width="${lw}" height="${boxH}" rx="8" fill="#12212f" stroke="#405970"/>`;
      s += label(lx, lx + lw / 2, fa.lines, fa.size, mid, mono, compare ? '#a9d9ff' : '#f7cc91');
      if (compare) {
        s += `<text x="${(lx + lw + rx) / 2}" y="${mid + 5}" text-anchor="middle" font-size="13" fill="#6f8799">vs</text>`;
      } else {
        s += `<line x1="${lx + lw + 14}" y1="${mid}" x2="${rx - 14}" y2="${mid}" stroke="#9fe3c6" stroke-width="2" marker-end="url(#mapping-arrow)"/>`;
        if (spec.fn) s += `<text x="${(lx + lw + rx) / 2}" y="${mid - 7}" text-anchor="middle" font-family="${mono}" font-size="13" fill="#9fe3c6">${esc(spec.fn)}</text>`;
      }
      s += `<rect x="${rx}" y="${y}" width="${rw}" height="${boxH}" rx="8" fill="#12212f" stroke="#405970"/>`;
      s += label(rx, rx + rw / 2, fb.lines, fb.size, mid, mono, compare ? '#f7cc91' : '#a6efd1');
      y += boxH + 14;
    });
    const n = spec.rows.length;
    if (!compare) s += `<text x="${W / 2}" y="${H - 14}" text-anchor="middle" font-size="14" fill="#dce7f1">값 ${n}개가 들어가면 결과도 ${n}개 · 한 줄씩 짝지어 바뀝니다</text>`;
    return s + '</svg>';
  }

  const seen = new WeakSet();
  function render(root) {
    if (!(root instanceof Element) && root !== document) return;
    const codes = [...root.querySelectorAll('pre > code.language-mapping')];
    if (root instanceof Element && root.matches('pre > code.language-mapping')) codes.push(root);
    for (const code of codes) {
      const pre = code.parentElement;
      if (!pre || !pre.isConnected || seen.has(pre)) continue;
      seen.add(pre);
      const spec = parse(code.textContent);
      if (!spec.rows.length) continue;
      const figure = document.createElement('figure');
      figure.className = 'diagram-strip';
      figure.innerHTML = svg(spec);
      pre.replaceWith(figure);
    }
  }
  new MutationObserver(records => {
    for (const record of records) for (const node of record.addedNodes) if (node instanceof Element) render(node);
  }).observe(document.body, { childList: true, subtree: true });
  render(document);
  globalThis.molipDiagrams = { render, parse, svg };
})();
