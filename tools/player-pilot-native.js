// Executed inside the actual platform WebView; no browser automation protocol required.
(async () => {
  const checked = [];
  const wait = async (predicate, label) => {
    const deadline = Date.now() + 20000;
    while (Date.now() < deadline) {
      if (predicate()) return;
      await new Promise(resolve => setTimeout(resolve, 40));
    }
    throw new Error(`Timed out: ${label}`);
  };
  const buttons = () => [...document.querySelectorAll('button')];
  const button = text => buttons().find(item => item.textContent.trim() === text);
  const click = async text => {
    await wait(() => button(text) && !button(text).disabled, text);
    button(text).click();
    await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
  };
  const status = text => document.querySelector('.execution-status')?.textContent.includes(text);
  try {
    await wait(() => document.querySelector('.lesson-card'), 'production course catalog');
    await click('풀모드 시작');
    await wait(() => document.querySelector('.lesson-outline'), 'four-level objectives');
    if (document.querySelectorAll('.learning-objective').length !== 4) throw new Error('Missing goals');
    checked.push('production course opening and four-level goals');
    await wait(() => window.molipCodeEditors?.getValue() != null, 'editor mounted');
    await click('초기화');
    await click('제출');
    await wait(() => status('다시 풀어보세요'), 'wrong answer rejected');
    molipCodeEditors.setValue('// 결과를 확인해요.\nconsole.log(3);\n');
    await click('코드 실행');
    await wait(() => document.querySelector('.output')?.textContent.trim() === '3', 'real Node execution');
    await click('제출');
    await wait(() => status('통과했어요'), 'correct answer accepted');
    checked.push('real execution, grading and isolated progress');
    await click('초기화');
    await wait(() => molipCodeEditors.getValue()?.includes('console.log(0)'), 'reset');
    await click('문제 2 · 값 5 확인');
    await wait(() => document.querySelector('.lesson-outline')?.textContent.includes('출력 결과를 확인해요: 5'), 'step goals');
    checked.push('reset and step context');
    await click('버전 b');
    await wait(() => document.querySelector('.lesson-card')?.textContent.includes('pilot-b'), 'snapshot B');
    await click('풀모드 시작');
    await wait(() => document.querySelectorAll('.study-navigation button').length === 3, 'added step');
    await click('손상 후보 검사');
    await wait(() => document.querySelector('.pilot-toolbar')?.textContent.includes('손상 후보를 거절'), 'invalid candidate');
    await click('버전 c');
    await wait(() => document.querySelector('.lesson-card')?.textContent.includes('pilot-c'), 'snapshot C');
    await click('풀모드 시작');
    await wait(() => buttons().some(item => item.textContent.includes('두 값을 합쳐요')), 'replacement step');
    if (buttons().some(item => item.textContent.includes('값 5 확인'))) throw new Error('Retired step is active');
    checked.push('A/B/C snapshots, invalid candidate and replacement identity');
    dioxus.send({passed: true, checked, userAgent: navigator.userAgent, viewport: {width: innerWidth, height: innerHeight}});
  } catch (error) {
    dioxus.send({passed: false, checked, error: String(error), screen: document.body.innerText.slice(0, 4000)});
  }
})();
