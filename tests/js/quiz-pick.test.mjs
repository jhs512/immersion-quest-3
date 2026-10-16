// The option matcher behind 정답 보기 and the compiled 해설, run against the real course data
// without the app: every choice question's narrated answer must name its correct option.
//   node --test tests/js/quiz-pick.test.mjs   (cargo test runs it too: tests/js_quiz_pick.rs)
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import vm from 'node:vm';

const root = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
vm.runInThisContext(readFileSync(join(root, 'assets/layout/quiz-pick.js'), 'utf8'));
const { pickOption } = globalThis.molipQuizPick;

test('a bare number is the N-th option even when another option contains that digit', () => {
  const options = ['10000 곱하기 3이 얼마야?', '`30000`', '파이썬. 10000 * 3 계산해서 출력'];
  assert.equal(pickOption(options, '3'), 2);
  assert.equal(pickOption(options, '1'), 0);
  assert.equal(pickOption(options, '4'), -1);
});

test('exact text wins over the number, then containment', () => {
  assert.equal(pickOption(['`2`', '3', '4'], '3'), 1);
  assert.equal(pickOption(['오류가 난다', '`30000`이 나온다'], '30000이 나온다'), 1);
  assert.equal(pickOption(['오류가 난다', '`30000`이 나온다'], '오류'), 0);
  assert.equal(pickOption(['a', 'b'], ''), -1);
});

test('every narrated quiz and concept answer in the KPC course names the correct option', () => {
  const course = JSON.parse(readFileSync(join(root, 'courses/kpc-finance.json'), 'utf8'));
  let checked = 0;
  for (const chapter of course.chapters) for (const unit of chapter.units) for (const activity of unit.activities) {
    const questions = activity.kind === 'quiz' ? activity.questions : activity.kind === 'concept' ? [activity.check] : [];
    const answers = {};
    for (const step of activity.narration) if (step.action === 'answer_quiz') Object.assign(answers, step.answers || {});
    questions.forEach((question, i) => {
      if (question.type !== 'choice') return;
      const want = answers[String(i + 1)];
      assert.ok(want !== undefined, `${activity.id} q${i + 1}: no narrated answer`);
      assert.equal(pickOption(question.options, want), question.correct, `${activity.id} q${i + 1}: "${want}"`);
      checked += 1;
    });
  }
  assert.ok(checked > 100, `only ${checked} choice questions checked`);
});
