// The reviewed pronunciation inventory of the published lessons (docs/speech-pronunciation-review.json).
// Run: node --test assets/speech/
// These tests check the text sent to a voice, not how it sounds. When a lesson adds a command, file name,
// class name, acronym … the coverage test fails until the item is reviewed:
//   node tools/speech-audit.mjs --write   (adds it as "unreviewed"), then set decision/note by hand.
// When a rule or LEXICON change alters a reviewed sentence, the pin test prints the difference; review it,
// then `node tools/speech-audit.mjs --accept`.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { audit, loadPronunciation, lessonFiles, speechTexts, referencedLessons } from '../../tools/speech-audit.mjs';

const p = loadPronunciation();
const review = JSON.parse(readFileSync(new URL('../../docs/speech-pronunciation-review.json', import.meta.url), 'utf8'));
const result = audit(p);
const DECISIONS = new Set(['lexicon', 'as-written', 'unresolved']);

test('every command, file name, class name and acronym in the published lessons has a reviewed decision', () => {
  const missing = result.items.filter(item => !review.items[item.key]).map(item => item.key);
  assert.deepEqual(missing, [], 'run node tools/speech-audit.mjs --write and review the new items');
  const unreviewed = Object.entries(review.items).filter(([, entry]) => !DECISIONS.has(entry.decision)).map(([key]) => key);
  assert.deepEqual(unreviewed, [], 'set decision to lexicon, as-written or unresolved');
  const stale = Object.keys(review.items).filter(key => !result.items.some(item => item.key === key));
  assert.deepEqual(stale, [], 'items no longer in a lesson: run node tools/speech-audit.mjs --write');
  for (const [key, entry] of Object.entries(review.items)) {
    if (entry.decision !== 'lexicon') assert.ok(entry.note, `${key}: say why it is ${entry.decision}`);
  }
});

test('each reviewed sentence is still spoken as reviewed', () => {
  const changed = [];
  for (const [key, entry] of Object.entries(review.items)) {
    const spoken = p.pronunciationText(entry.example);
    if (spoken !== entry.spoken) changed.push(`${key}\n  source  ${entry.example}\n  review  ${entry.spoken}\n  now     ${spoken}`);
  }
  assert.equal(changed.length, 0, 'review these, then node tools/speech-audit.mjs --accept\n' + changed.join('\n'));
});

test('lexicon items are not sent to the voice as written; as-written items are', () => {
  const escape = value => value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  for (const [key, entry] of Object.entries(review.items)) {
    const token = key.slice(key.indexOf(':') + 1);
    if (key.startsWith('subcommand:') || key.startsWith('member:') || key.startsWith('extension:')) continue;
    const raw = new RegExp('(?<![A-Za-z0-9_])' + escape(token) + '(?![A-Za-z0-9_])').test(entry.spoken);
    if (entry.decision === 'lexicon' && key !== 'class:Main') assert.ok(!raw, `${key} is still sent as written: ${entry.spoken}`);
    if (entry.decision === 'as-written') assert.ok(raw, `${key} is reviewed as written but was converted: ${entry.spoken}`);
  }
});

test('the spoken text of every published lesson line is unchanged by speaking it again', () => {
  const referenced = referencedLessons();
  const lines = new Set();
  for (const file of lessonFiles()) {
    const lesson = JSON.parse(readFileSync(file, 'utf8'));
    if (file.includes('redesigned') && !referenced.has(lesson.id)) continue;
    for (const [, text] of speechTexts(lesson)) for (const line of text.split(/\n+/)) if (line.trim()) lines.add(line);
  }
  assert.ok(lines.size > 15000, `corpus ${lines.size}`);
  const unstable = [];
  for (const line of lines) {
    const once = p.pronunciationText(line);
    if (p.pronunciationText(once) !== once && !review.idempotency_exceptions[line.trim()]) unstable.push(line);
  }
  assert.deepEqual(unstable, []);
  for (const line of Object.keys(review.idempotency_exceptions)) assert.ok([...lines].some(l => l.trim() === line), 'stale exception: ' + line);
});
