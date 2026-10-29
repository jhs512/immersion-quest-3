// Minimal Java syntax highlighter: returns HTML with <span class="hl-*"> tokens. No dependencies.
// Handles block comments spanning lines when called on the whole source (highlightJava) or
// line by line with carried state (highlightLines).

const KEYWORDS = new Set(('abstract assert break case catch class const continue default do else enum extends final ' +
  'finally for goto if implements import instanceof interface native new package private protected public return ' +
  'static strictfp super switch synchronized this throw throws transient try volatile while var record sealed permits yield').split(' '));
const TYPES = new Set('boolean byte char double float int long short void'.split(' '));
const LITERALS = new Set(['true', 'false', 'null']);

const esc = (s) => s.replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const span = (cls, text) => `<span class="hl-${cls}">${esc(text)}</span>`;

const TOKEN = /(\/\*[\s\S]*?\*\/|\/\*[\s\S]*$)|(\/\/.*$)|("(?:[^"\\\n]|\\.)*"?)|('(?:[^'\\\n]|\\.)*'?)|(@[A-Za-z_]\w*)|(\b\d[\d_]*(?:\.\d[\d_]*)?(?:[eE][+-]?\d+)?[lLfFdD]?\b|\b0[xX][\da-fA-F_]+[lL]?\b)|([A-Za-z_$][\w$]*)/gm;

/** Highlights one line. `state.inComment` carries an open block comment across lines. */
export function highlightLine(line, state = { inComment: false }) {
  let out = '';
  let rest = line;
  if (state.inComment) {
    const end = rest.indexOf('*/');
    if (end < 0) return span('comment', rest);
    out += span('comment', rest.slice(0, end + 2));
    rest = rest.slice(end + 2);
    state.inComment = false;
  }
  let last = 0;
  TOKEN.lastIndex = 0;
  let m;
  while ((m = TOKEN.exec(rest))) {
    out += esc(rest.slice(last, m.index));
    const [text, block, lineComment, str, chr, annotation, num, word] = m;
    if (block) { out += span('comment', text); if (!text.endsWith('*/')) state.inComment = true; }
    else if (lineComment) out += span('comment', text);
    else if (str) out += span('string', text);
    else if (chr) out += span('char', text);
    else if (annotation) out += span('annotation', text);
    else if (num) out += span('number', text);
    else if (word) {
      if (KEYWORDS.has(word)) out += span('keyword', word);
      else if (TYPES.has(word)) out += span('type', word);
      else if (LITERALS.has(word)) out += span('literal', word);
      else if (/^[A-Z]/.test(word)) out += span('class', word);
      else out += esc(word);
    } else out += esc(text);
    last = m.index + text.length;
  }
  out += esc(rest.slice(last));
  return out;
}

/** Highlights every line of a source string; returns an array of HTML strings, one per line. */
export function highlightLines(source) {
  const state = { inComment: false };
  return source.replace(/\r\n?/g, '\n').split('\n').map((line) => highlightLine(line, state));
}

export function highlightJava(source) {
  return highlightLines(source).join('\n');
}
