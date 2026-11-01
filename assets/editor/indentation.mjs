import { EditorState } from '@codemirror/state';
import { indentUnit } from '@codemirror/language';

export function documentIndentation(source, language) {
  const prefixes = String(source).split(/\r?\n/).filter(line => /\S/.test(line) && !/^\s*\*/.test(line))
    .map(line => /^[ \t]*/.exec(line)[0]).filter(Boolean);
  const tabs = prefixes.filter(prefix => prefix.startsWith('\t')).length;
  const spaces = prefixes.filter(prefix => /^ +$/.test(prefix)).map(prefix => prefix.length);
  if (tabs && tabs >= spaces.length) return '\t';
  if (spaces.length) {
    const candidates = [2, 3, 4, 5, 6, 7, 8];
    if (spaces.filter(width => width === 1).length > spaces.length / 2) candidates.push(1);
    candidates.sort((a, b) => spaces.filter(width => width % b === 0).length - spaces.filter(width => width % a === 0).length
      || spaces.filter(width => width === b).length - spaces.filter(width => width === a).length || a - b);
    return ' '.repeat(candidates[0]);
  }
  return ' '.repeat(['html', 'javascript'].includes(language) ? 2 : 4);
}

export function documentIndentationExtensions(source, language) {
  const unit = documentIndentation(source, language);
  return [indentUnit.of(unit), EditorState.tabSize.of(unit === '\t' ? 4 : unit.length)];
}
