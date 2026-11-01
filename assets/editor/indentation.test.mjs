import test from 'node:test';
import assert from 'node:assert/strict';
import { Compartment, EditorState } from '@codemirror/state';
import { indentMore, indentLess, insertNewlineAndIndent } from '@codemirror/commands';
import { indentUnit } from '@codemirror/language';
import { html } from '@codemirror/lang-html';
import { documentIndentation, documentIndentationExtensions } from './indentation.mjs';

function editor(doc, language = 'html', compartment = new Compartment()) {
  let state = EditorState.create({ doc, extensions: [html(), compartment.of(documentIndentationExtensions(doc, language))] });
  return {
    get state() { return state; },
    dispatch(transaction) { state = transaction.state || state.update(transaction).state; },
    replace(doc) { this.dispatch({ changes: { from: 0, to: state.doc.length, insert: doc }, effects: compartment.reconfigure(documentIndentationExtensions(doc, language)) }); },
  };
}

for (const unit of ['  ', '    ', '\t']) {
  test(`Tab, Shift-Tab and Enter follow ${JSON.stringify(unit)} indentation`, () => {
    const source = `<ul>\n${unit}<li>항목</li>\n</ul>`;
    const view = editor(source);
    assert.equal(view.state.facet(indentUnit), unit);
    assert.equal(view.state.tabSize, unit === '\t' ? 4 : unit.length);
    const line = view.state.doc.line(2);
    view.dispatch({ selection: { anchor: line.from } });
    assert.equal(indentMore(view), true);
    assert.equal(view.state.doc.line(2).text, unit.repeat(2) + '<li>항목</li>');
    assert.equal(indentLess(view), true);
    assert.equal(view.state.doc.toString(), source);
    view.dispatch({ selection: { anchor: 4 } });
    assert.equal(insertNewlineAndIndent(view), true);
    assert.equal(view.state.doc.line(2).text, unit);
  });
}

test('replacing a document resets indentation without formatting its source', () => {
  const view = editor('<ul>\n  <li>둘</li>\n</ul>');
  const four = '<ul>\n    <li>넷</li>\n</ul>';
  view.replace(four);
  assert.equal(view.state.doc.toString(), four);
  assert.equal(view.state.facet(indentUnit), '    ');
  assert.equal(view.state.tabSize, 4);
  const tabs = '<ul>\n\t<li>탭</li>\n</ul>';
  view.replace(tabs);
  assert.equal(view.state.doc.toString(), tabs);
  assert.equal(view.state.facet(indentUnit), '\t');
});

test('ordinary typing keeps the document indentation fixed', () => {
  const view = editor('<ul>\n  <li>둘</li>\n</ul>');
  view.dispatch({ changes: { from: 0, insert: ' <p>작성 중</p>\n' } });
  assert.equal(view.state.facet(indentUnit), '  ');
});

test('blank documents use language defaults, existing indentation wins over them', () => {
  assert.equal(documentIndentation('', 'html'), '  ');
  assert.equal(documentIndentation('', 'javascript'), '  ');
  assert.equal(documentIndentation('', 'python'), '    ');
  assert.equal(documentIndentation('class Main {\n  void run() {}\n}', 'java'), '  ');
  assert.equal(documentIndentation('<ul>\n    <li>a</li>\n    \n        <b>b</b>\n</ul>', 'html'), '    ');
});

test('nested excerpts and aligned comments do not disguise the indentation unit', () => {
  assert.equal(documentIndentation('    <ul>\n      <li>항목</li>\n    </ul>', 'html'), '  ');
  assert.equal(documentIndentation('class Main {\n    /** 설명\n     * 정렬된 주석\n     */\n    void run() {\n        call(\n         value);\n    }\n}', 'java'), '    ');
});
