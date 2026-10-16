// Which quiz option an answer names. Shared by the tutor agent (assets/layout/agent.js) and the
// tests (tests/js/quiz-pick.test.mjs), so the rule lives in one place:
//   1. the option whose text is exactly the answer;
//   2. else, an answer that is a bare number N (what the compiled 해설 and 정답 보기 send) is the
//      N-th option, counted from 1;
//   3. else, the first option whose text contains the answer (or, for a long answer, that the
//      answer contains).
// Order matters: "3" must mean the third option, never the first option whose wording happens
// to contain a 3 ("10000 곱하기 3이 얼마야?").
(function () {
  'use strict';
  if (globalThis.molipQuizPick) return;
  // Text as the student reads it: no backticks or bold marks, single spaces.
  const normalize = value => String(value == null ? '' : value).replace(/[`*]/g, '').replace(/\s+/g, ' ').trim();
  // The 0-based index of the option `want` names among `labels`, or -1 when none does.
  function pickOption(labels, want) {
    const texts = Array.from(labels, normalize);
    const wantText = normalize(want);
    let index = texts.indexOf(wantText);
    if (index >= 0) return index;
    if (/^\d+$/.test(wantText)) {
      const n = Number(wantText);
      if (n >= 1 && n <= texts.length) return n - 1;
    }
    if (!wantText) return -1;
    return texts.findIndex(text => text.includes(wantText) || (wantText.length > 6 && wantText.includes(text)));
  }
  globalThis.molipQuizPick = { pickOption, normalize };
})();
