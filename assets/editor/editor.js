import { EditorView, lineNumbers, highlightActiveLineGutter, highlightSpecialChars, drawSelection,
  dropCursor, rectangularSelection, crosshairCursor, highlightActiveLine, keymap, Decoration } from '@codemirror/view';
import { EditorState, StateEffect, StateField, Compartment } from '@codemirror/state';
import { python } from '@codemirror/lang-python';
import { java } from '@codemirror/lang-java';
import { javascript } from '@codemirror/lang-javascript';
import { html } from '@codemirror/lang-html';
import { history, defaultKeymap, historyKeymap, indentWithTab } from '@codemirror/commands';
import { syntaxHighlighting, HighlightStyle, indentUnit, defaultHighlightStyle, indentOnInput, bracketMatching, foldGutter, foldKeymap } from '@codemirror/language';
import { searchKeymap, highlightSelectionMatches } from '@codemirror/search';
import { tags, highlightCode, classHighlighter } from '@lezer/highlight';

// The textarea stays as the Dioxus event bridge and accessible fallback.
// Indentation is four spaces, as the course text and every example teach.
if (!window.molipCodeEditors) {
  const editors = new Map();
  const resetVersions = new Map();
  const narrationFocus = StateEffect.define();
  const narrationLines = StateField.define({
    create: () => Decoration.none,
    update(value, transaction) {
      value = value.map(transaction.changes);
      for (const effect of transaction.effects) if (effect.is(narrationFocus)) {
        if (!effect.value) { value = Decoration.none; continue; }
        const [start, end] = effect.value;
        const doc = transaction.state.doc;
        const ranges = [];
        for (let n = Math.max(1, start); n <= Math.min(doc.lines, end); n++)
          ranges.push(Decoration.line({class: 'cm-narration-line'}).range(doc.line(n).from));
        value = Decoration.set(ranges);
      }
      return value;
    },
    provide: field => EditorView.decorations.from(field),
  });
  // The exact characters a narration sentence is about (a token or expression), beside the
  // line highlight. Cleared with highlightRange(null) when the sentence or explanation ends.
  const narrationSpanEffect = StateEffect.define();
  const narrationSpan = StateField.define({
    create: () => Decoration.none,
    update(value, transaction) {
      value = value.map(transaction.changes);
      for (const effect of transaction.effects) if (effect.is(narrationSpanEffect)) {
        if (!effect.value) { value = Decoration.none; continue; }
        const [from, to] = effect.value;
        value = from < to ? Decoration.set([Decoration.mark({class: 'cm-narration-span'}).range(from, to)]) : Decoration.none;
      }
      return value;
    },
    provide: field => EditorView.decorations.from(field),
  });
  // Colours come from the theme tokens in station.css (--editor-*, --syn-*), so 밝게 and 어둡게
  // repaint the editor through CSS alone; only CodeMirror's own light/dark base flag is
  // reconfigured when the effective look changes (mq-theme event from layout/theme.js).
  const colors = syntaxHighlighting(HighlightStyle.define([
    { tag: tags.keyword, color: 'var(--syn-keyword, #c792ea)' },
    { tag: tags.string, color: 'var(--syn-string, #a8d99c)' },
    { tag: tags.comment, color: 'var(--syn-comment, #92abc0)' },
    { tag: tags.number, color: 'var(--syn-number, #f6c177)' },
    { tag: tags.function(tags.variableName), color: 'var(--syn-function, #82cfff)' },
    { tag: tags.operator, color: 'var(--syn-operator, #89dceb)' },
  ]));
  const isDark = () => (window.mqTheme ? window.mqTheme.effective() : document.documentElement.dataset.theme) === 'dark';
  const darkness = new Compartment();
  // codemirror's basicSetup minus autocompletion and auto-closing brackets: learners type
  // every character themselves, and a popup over "pr" only distracts beginners.
  const setup = [
    lineNumbers(), highlightActiveLineGutter(), highlightSpecialChars(), history(), foldGutter(),
    drawSelection(), dropCursor(), EditorState.allowMultipleSelections.of(true), indentOnInput(),
    syntaxHighlighting(defaultHighlightStyle, { fallback: true }), bracketMatching(),
    rectangularSelection(), crosshairCursor(), highlightActiveLine(), highlightSelectionMatches(),
    keymap.of([...defaultKeymap, ...searchKeymap, ...historyKeymap, ...foldKeymap]),
  ];
  const theme = EditorView.theme({
    '&': { height: '100%', backgroundColor: 'var(--editor-bg, #202d3e)', color: 'var(--editor-ink, #e3edf6)' },
    '.cm-scroller': { overflow: 'auto', fontFamily: 'Consolas, monospace', fontSize: '15px' },
    '.cm-content': { padding: '16px 0', caretColor: 'var(--editor-cursor, #fff)' },
    '.cm-gutters': { backgroundColor: 'var(--editor-bg, #202d3e)', color: 'var(--editor-gutter-ink, #8299ae)', border: 'none' },
    // Selection is drawn behind the text; keep the active line translucent.
    '.cm-activeLine': { backgroundColor: 'var(--editor-active-line, #2b405555)' },
    '.cm-activeLineGutter': { backgroundColor: 'var(--editor-active-gutter, #2b4055)' },
    '.cm-cursor': { borderLeftColor: 'var(--editor-cursor, #fff)' },
    '.cm-selectionBackground': { backgroundColor: 'var(--editor-selection, #426385) !important' },
    '.cm-panels, .cm-tooltip': { backgroundColor: 'var(--editor-panel, #192b3c)', color: 'var(--editor-ink, #e3edf6)' },
  });

  function sync() {
    document.querySelectorAll('.markdown pre code.language-python, .markdown pre code.language-java').forEach(code => {
      const source = code.textContent;
      if (code.dataset.highlighted === source) return;
      code.dataset.highlighted = source;
      const fragment = document.createDocumentFragment();
      highlightCode(source, (code.classList.contains('language-java') ? java() : python()).language.parser.parse(source), classHighlighter, (text, classes) => {
        const span = document.createElement('span');
        span.textContent = text;
        span.className = classes;
        fragment.append(span);
      }, () => fragment.append(document.createTextNode('\n')));
      code.replaceChildren(fragment);
    });
    for (const [element, view] of editors) {
      if (!element.isConnected) { view.destroy(); editors.delete(element); resetVersions.delete(element); }
    }
    document.querySelectorAll('textarea[data-code-editor]').forEach(element => {
      const source = element.getAttribute('data-editor-value') ?? element.value;
      const resetVersion = element.getAttribute('data-editor-reset');
      let view = editors.get(element);
      if (!view) {
        const host = document.createElement('div');
        host.className = 'python-editor-host';
        element.after(host);
        view = new EditorView({
          doc: source,
          parent: host,
          extensions: [setup, narrationLines, narrationSpan, element.dataset.codeEditor === 'java' ? java() : element.dataset.codeEditor === 'javascript' ? javascript({jsx:true}) : element.dataset.codeEditor === 'html' ? html() : python(), indentUnit.of('    '), keymap.of([indentWithTab]), theme, darkness.of(EditorView.darkTheme.of(isDark())), colors,
            EditorState.readOnly.of(element.readOnly),
            EditorView.editable.of(!element.readOnly),
            EditorView.contentAttributes.of({ 'aria-label': ({java:'Java',javascript:'JavaScript',html:'HTML',shell:'Shell',python:'Python'}[element.dataset.codeEditor] || '코드') + ' 코드 편집기' }),
            EditorView.updateListener.of(update => {
              if (!update.docChanged || element.value === update.state.doc.toString()) return;
              element.value = update.state.doc.toString();
              element.dispatchEvent(new Event('input', { bubbles: true }));
            })],
        });
        editors.set(element, view);
        resetVersions.set(element, resetVersion);
        element.hidden = true;
      } else if (resetVersions.get(element) !== resetVersion) {
        // Only explicit resets may replace the editor document. Typing is owned
        // by CodeMirror: delayed backend echoes must not interrupt IME input.
        resetVersions.set(element, resetVersion);
        element.value = source;
        if (view.state.doc.toString() !== source) {
          view.dispatch({ changes: { from: 0, to: view.state.doc.length, insert: source } });
        }
      }
    });
  }
  // Replace the document of the editor on screen (used by the tutor agent). The update
  // listener above then syncs the hidden textarea and tells the Rust side.
  function setValue(source) {
    let done = false;
    for (const [element, view] of editors) {
      if (!element.isConnected || !view.dom.getClientRects().length) continue;
      view.dispatch({ changes: { from: 0, to: view.state.doc.length, insert: source } });
      done = true;
    }
    return done;
  }
  // The editor's text, or null when no editor is on screen (narration mode reads it first).
  function getValue() {
    for (const [element, view] of editors) if (element.isConnected && view.dom.getClientRects().length) return view.state.doc.toString();
    return null;
  }
  // Insert at the end without touching what is there: narration types code a few characters at a time.
  function appendValue(piece) {
    for (const [element, view] of editors) {
      if (!element.isConnected || !view.dom.getClientRects().length) continue;
      const end = view.state.doc.length;
      view.dispatch({ changes: { from: end, to: end, insert: piece }, selection: { anchor: end + piece.length }, scrollIntoView: true });
      return true;
    }
    return false;
  }
  function highlightLines(start, end = start, moveCursor = false) {
    for (const [element, view] of editors) if (element.isConnected && view.dom.getClientRects().length) {
      const first = Math.max(1, Math.min(view.state.doc.lines, Number(start) || 1));
      const last = Math.max(first, Math.min(view.state.doc.lines, Number(end) || first));
      view.dispatch({...(moveCursor && start != null ? {selection:{anchor:view.state.doc.line(last).to}} : {}),effects: [narrationFocus.of(start == null ? null : [first, last]),
        ...(start == null ? [] : [EditorView.scrollIntoView(view.state.doc.line(last).from, {y: 'nearest'})])]});
      return true;
    }
    return false;
  }
  // Highlight characters [from, to) of the visible editor; null clears it.
  function highlightRange(from, to = from) {
    for (const [element, view] of editors) if (element.isConnected && view.dom.getClientRects().length) {
      if (from == null) { view.dispatch({effects: narrationSpanEffect.of(null)}); return true; }
      const length = view.state.doc.length;
      const start = Math.max(0, Math.min(length, Number(from) || 0));
      const end = Math.max(start, Math.min(length, Number(to) || start));
      view.dispatch({effects: [narrationSpanEffect.of([start, end]), EditorView.scrollIntoView(start, {y: 'nearest'})]});
      return true;
    }
    return false;
  }
  function replaceRange(from, to, insert) {
    for (const [element, view] of editors) if (element.isConnected && view.dom.getClientRects().length) {
      view.dispatch({changes: {from, to, insert}, selection: {anchor: from + insert.length}, scrollIntoView: true});
      return true;
    }
    return false;
  }
  window.molipCodeEditors = { sync, setValue, getValue, appendValue, highlightLines, highlightRange, replaceRange };
  // The look changed (choice in 앱 설정 or the OS while 시스템): CodeMirror's base styles follow.
  document.addEventListener('mq-theme', () => {
    const dark = isDark();
    for (const view of editors.values()) view.dispatch({ effects: darkness.reconfigure(EditorView.darkTheme.of(dark)) });
  });
  new MutationObserver(sync).observe(document.body, {
    subtree: true, childList: true, attributes: true,
    attributeFilter: ['data-editor-value', 'data-editor-reset'],
  });
  sync();
}
