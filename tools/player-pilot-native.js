// Executed inside the actual platform WebView; no browser automation protocol required.
(async () => {
  const checked = [];
  const wait = async (predicate, label, timeout=20000) => {
    const deadline = Date.now() + timeout;
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
  // WebKit can report root clientWidth before subtracting the body's classic scrollbar.
  const viewportWidth = () => Math.min(document.documentElement.clientWidth, document.body.clientWidth);
  const status = text => document.querySelector('.execution-status')?.textContent.includes(text);
  const editorState = () => ({
    task: document.querySelector('.repository-task')?.dataset.taskId,
    title: document.querySelector('.repository-task .problem-pane h2')?.textContent,
    editor: window.molipCodeEditors?.getValue(),
    model: document.querySelector('.repository-task [data-code-editor]')?.dataset.editorValue,
    execution: document.querySelector('.result-pane')?.dataset.executionState,
    status: document.querySelector('.execution-status')?.textContent,
  });
  const writeCode = async (source, title) => {
    // Different tasks can have identical starter text. Do not use that text as
    // evidence that the newly selected task and its editor have both mounted.
    await wait(() => editorState().title === title && editorState().editor != null, `${title}: editor mounted`);
    if (!molipCodeEditors.setValue(source)) throw new Error(`${title}: editor rejected input`);
    // setValue dispatches input through the native bridge. Submit only after the
    // task's Rust state has echoed it, rather than after an arbitrary frame delay.
    await wait(() => {
      const state = editorState();
      return state.title === title && state.editor === source && state.model === source;
    }, `${title}: student input reached task state`);
  };
  try {
    if (!window.mq3FirstGitOnly) {
    const updateBanner = () => document.querySelector('.update-banner');
    await wait(() => updateBanner(), 'startup update offer');
    if (document.querySelector('.update-panel')) throw new Error('Startup must not install automatically');
    await click('나중에');
    await wait(() => document.querySelector('[aria-label="앱 업데이트 설치"]'), 'persistent update icon');
    document.querySelector('.app-update-settings').open = true;
    await click('업데이트 확인');
    await new Promise(resolve => setTimeout(resolve, 1200));
    if (updateBanner()) throw new Error('Manual check repeated the same update notice');
    document.querySelector('.app-update-settings').open = false;
    checked.push('update offer requires click and leaves icon after dismiss');
    await wait(() => document.querySelector('.lesson-card'), 'production course catalog');
    await click('풀모드 시작');
    await wait(() => document.querySelector('.lesson-outline'), 'four-level objectives');
    if (document.querySelectorAll('.learning-objective').length !== 4) throw new Error('Missing goals');
    checked.push('production course opening and four-level goals');
    document.querySelector('#app-fullscreen-toggle').click();
    // Native fullscreen transitions can finish after the first resize event (notably on macOS).
    // Re-request the window size, then require a settled viewport before measuring layout.
    const resizeWindow = async height => {
      const deadline = Date.now() + 20000;
      while (Date.now() < deadline) {
        await click(`검증 높이 ${height}`);
        await new Promise(resolve => setTimeout(resolve, 1000));
        const measured = innerHeight;
        await new Promise(resolve => setTimeout(resolve, 500));
        // The OS may reserve menu/title-bar space or clamp the requested frame.
        // Still require the CSS normal-height range, or the separate short-height range.
        if (measured >= (height >= 640 ? 640 : 360) && measured <= height+40 && innerHeight === measured) return;
      }
      throw new Error(`Native window did not settle at ${height}: ${innerWidth}x${innerHeight}`);
    };
    await resizeWindow(720);
    const workspace = document.querySelector('.repository-study');
    const workspaceBounds=workspace.getBoundingClientRect();
    if(workspaceBounds.left < -1 || workspaceBounds.right > viewportWidth()+1 || workspaceBounds.width < viewportWidth()-2)throw new Error(`Practice width escapes viewport: ${JSON.stringify({left:workspaceBounds.left,right:workspaceBounds.right,width:workspaceBounds.width,viewport:innerWidth,root:document.documentElement.clientWidth,body:document.body.clientWidth})}`);
    const paging = document.querySelector('.task-paging').getBoundingClientRect();
    if (paging.bottom > innerHeight + 1) throw new Error(`Practice controls overflow: ${paging.bottom} > ${innerHeight}`);
    if (document.querySelector('.repository-task').getBoundingClientRect().height < 180) throw new Error('Workspace squeezed out by headers');

    for(const pane of document.querySelectorAll('.problem-pane,.result-pane')) {
      const scrollbar=getComputedStyle(pane,'::-webkit-scrollbar');
      if(scrollbar.width!==scrollbar.height)throw new Error('Scrollbar axes have different thickness');
    }
    checked.push('normal window keeps task and previous/next controls inside viewport');
    const previousSplit = localStorage.getItem('molip:split');
    try {
      for (const [selector,key,pane,dimension] of [['.split-col','ArrowRight','.problem-pane','width'],['.split-row','ArrowUp','.editor-pane','height']]) {
        const handle=document.querySelector(selector);
        handle.dispatchEvent(new MouseEvent('dblclick',{bubbles:true}));
        await new Promise(requestAnimationFrame);
        const before=document.querySelector(pane).getBoundingClientRect()[dimension];
        handle.focus();handle.dispatchEvent(new KeyboardEvent('keydown',{key,bubbles:true,cancelable:true}));
        await new Promise(requestAnimationFrame);
        const after=document.querySelector(pane).getBoundingClientRect()[dimension];
        if(Math.abs(after-before)<5)throw new Error(`Panel handle did not resize: ${selector}: ${before} -> ${after}`);
        handle.dispatchEvent(new MouseEvent('dblclick',{bubbles:true}));
      }
    } finally {if(previousSplit===null)localStorage.removeItem('molip:split');else localStorage.setItem('molip:split',previousSplit);}
    const codeFocus = document.querySelector('.cm-content') || document.querySelector('[data-code-editor]');
    const fullscreenKey = () => new KeyboardEvent('keydown', navigator.platform.toLowerCase().includes('mac')
      ? {key:'f',ctrlKey:true,metaKey:true,bubbles:true,cancelable:true}
      : {key:'F11',bubbles:true,cancelable:true});
    codeFocus.focus();codeFocus.dispatchEvent(fullscreenKey());
    await wait(() => document.querySelector('#app-fullscreen-toggle').dataset.fullscreen === 'true','editor fullscreen shortcut');
    codeFocus.dispatchEvent(fullscreenKey());
    await wait(() => document.querySelector('#app-fullscreen-toggle').dataset.fullscreen === 'false','editor fullscreen return');
    await resizeWindow(480);
    const shortPaging = document.querySelector('.task-paging');
    shortPaging.scrollIntoView({block:'end'});
    if (shortPaging.getBoundingClientRect().bottom > innerHeight + 1) throw new Error('Small window cannot scroll to previous/next');
    window.scrollTo(0,0);
    checked.push('native editor shortcut toggles window and short window controls remain scrollable');

    document.querySelector('#app-fullscreen-toggle').click();

    await wait(() => window.molipCodeEditors?.getValue() != null, 'editor mounted');
    for (let round=0; round<3; round++) {
      await click('문제 2 · 값 5 확인');
      await writeCode(`console.log(${51+round});`, '값 5 확인');
      await click('문제 1 · 값 3 확인');
      await writeCode(`console.log(${31+round});`, '값 3 확인');
    }
    checked.push('repeated task transitions keep editor input bound to the selected task');
    await click('초기화');
    await click('제출');
    await wait(() => status('다시 풀어보세요'), 'wrong answer rejected');
    await writeCode('// 결과를 확인해요.\nconsole.log(3);\n', '값 3 확인');
    await click('코드 실행');
    await wait(() => document.querySelector('.output')?.textContent.trim() === '3', 'real Node execution');
    await click('제출');
    await wait(() => status('통과했어요'), 'correct answer accepted');
    checked.push('real execution, grading and isolated progress');
    await click('초기화');
    await wait(() => molipCodeEditors.getValue()?.includes('console.log(0)'), 'reset');
    await click('문제 2 · 값 5 확인');
    await wait(() => document.querySelector('.lesson-outline')?.textContent.includes('출력 결과를 확인해요: 5'), 'step goals');
    await writeCode('console.log(5);\n', '값 5 확인');
    await click('제출');
    await wait(() => status('수업 완료'), 'original completion');
    checked.push('reset and step context');
    await click('버전 e');
    await wait(() => document.querySelector('.lesson-card')?.textContent.includes('pilot-e'), 'wording-only snapshot');
    await wait(() => document.querySelector('.lesson-status')?.textContent.includes('최신 버전 완료'), 'catalog stable completion');
    if (!document.querySelector('.study-progress')?.textContent.includes('1 / 1')) throw new Error('Catalog lost current completion');
    checked.push('catalog retains completion after wording-only revision');
    await click('버전 b');
    await wait(() => document.querySelector('.lesson-card')?.textContent.includes('pilot-b'), 'snapshot B');
    await click('풀모드 시작');
    await wait(() => document.querySelectorAll('.study-navigation button').length === 3, 'added step');
    await wait(() => document.querySelector('.study-progress')?.textContent.includes('추가 학습 있음'), 'old completion retained');
    if (!document.querySelector('.study-progress')?.textContent.includes('2 / 3')) throw new Error('Stable achievements lost');
    await click('문제 3 · 값 8 확인');
    await writeCode('console.log(8);\n', '값 8 확인');
    await click('제출');
    await wait(() => status('수업 완료'), 'additional learning completion');
    await click('손상 후보 검사');
    await wait(() => document.querySelector('.pilot-toolbar')?.textContent.includes('손상 후보를 거절'), 'invalid candidate');
    await click('버전 c');
    await wait(() => document.querySelector('.lesson-card')?.textContent.includes('pilot-c'), 'snapshot C');
    await click('풀모드 시작');
    await wait(() => buttons().some(item => item.textContent.includes('두 값을 합쳐요')), 'replacement step');
    if (buttons().some(item => item.textContent.includes('값 5 확인'))) throw new Error('Retired step is active');
    if (!document.querySelector('.study-progress')?.textContent.includes('1 / 2')) throw new Error('Replacement inherited success');
    checked.push('A/B/C snapshots, invalid candidate and replacement identity');
    checked.push('stable achievements, past completion and new required learning');
    await click('버전 d');
    await wait(() => document.querySelector('.lesson-card')?.textContent.includes('pilot-d'), 'interaction snapshot D');
    await click('풀모드 시작');
    await wait(() => document.querySelector('input[type=radio]'), 'choice editor');
    if (button('코드 실행')) throw new Error('Interaction should not offer code execution');
    document.querySelector('input[type=radio][value=five]').click();
    await click('제출');
    await wait(() => status('다시 풀어보세요'), 'wrong choice');
    document.querySelector('input[type=radio][value=three]').click();
    await click('제출');
    await wait(() => status('통과했어요'), 'immediate retry');
    await click('초기화');
    await wait(() => !document.querySelector('input[type=radio]:checked'), 'choice reset');
    await click('문제 2 · 출력 순서 배열');
    await wait(() => document.querySelector('.answer-pool'), 'order editor');
    await click('console.log(5);');
    await click('console.log(3);');
    await click('제출');
    await wait(() => status('다시 풀어보세요'), 'wrong order');
    document.querySelectorAll('[aria-label="조각 위로"]')[1].click();
    await click('제출');
    await wait(() => status('통과했어요'), 'reordered answer');
    await click('문제 3 · 출력값 빈칸');
    await wait(() => document.querySelector('[aria-label="빈칸 답안"]'), 'fill editor');
    const field = document.querySelector('[aria-label="빈칸 답안"]');
    const set = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
    set.call(field, '8');
    field.dispatchEvent(new Event('input', {bubbles: true}));
    await click('제출');
    await wait(() => status('수업 완료'), 'fill answer and whole lesson completion');
    checked.push('choice wrong/retry/reset, order move/grade, fill grade, shared progress');
    await click('← 코스 수업 목록');
    await click('풀모드 시작');
    await wait(() => document.querySelector('input[type=radio][value=five]'), 'reopened lesson');
    document.querySelector('input[type=radio][value=five]').click();
    await click('← 코스 수업 목록');
    await click('풀모드 시작');
    await wait(() => document.querySelector('input[type=radio][value=five]:checked'), 'answer retained across new round');
    document.querySelector('[aria-label="앱 업데이트 설치"]').click();
    await wait(() => document.querySelector('.update-panel')?.textContent.includes('검증 모드'), 'safe installer boundary failure');
    await click('이대로 계속');
    if (!document.querySelector('input[type=radio][value=five]:checked')) throw new Error('Update failure lost answer');
    checked.push('answer survives reopening and rejected installation; real installation not exercised');
    await click('버전 f');
    await wait(() => document.querySelector('.lesson-card')?.textContent.includes('pilot-f'), 'explanation snapshot');
    await click('풀모드 시작');
    await click('문제 4 · 해설 답안 보존');
    await wait(() => molipCodeEditors.getValue()?.includes('console.log(0)'), 'explanation editor');
    molipAgent.setVoice(false);
    molipCodeEditors.setValue('console.log(99);');
    const runInput = document.querySelector('.run-input textarea');
    runInput.value = 'student input';
    runInput.dispatchEvent(new Event('input', {bubbles:true}));
    await click('해설 재생 · 정답 실행');
    await wait(() => molipAgent.running, 'cancellable explanation');
    if (!button('초기화').disabled) throw new Error('Reset can overwrite the student draft during explanation');
    button('초기화').click();
    await wait(() => document.querySelector('.result-pane')?.dataset.executionState === 'running', 'delayed real example');
    await click('해설 멈춤');
    await wait(() => !molipAgent.running && !button('해설 재생 · 정답 실행').disabled, 'cancelled example restored');
    await new Promise(resolve => setTimeout(resolve, 1000));
    if (document.querySelector('.result-pane').dataset.executionState === 'running') throw new Error('Cancelled example left a spinner');
    if (runInput.value !== 'student input') throw new Error('Execution input display was not restored');
    molipCodeEditors.setValue("process.stdin.on('data', data => process.stdout.write(data));");
    await click('코드 실행');
    await wait(() => document.querySelector('.output')?.textContent.trim() === 'student input', 'actual input after cancellation');
    molipCodeEditors.setValue('console.log(99);');
    await click('← 코스 수업 목록');
    await click('풀모드 시작');
    await click('문제 4 · 해설 답안 보존');
    await wait(() => molipCodeEditors.getValue() === 'console.log(99);', 'saved draft after attempted reset');
    await click('해설 재생 · 정답 실행');
    await wait(() => molipAgent.running, 'explanation started');
    await wait(() => !molipAgent.running && !button('해설 재생 · 정답 실행').disabled, 'explanation restored');
    if (molipCodeEditors.getValue() !== 'console.log(99);') throw new Error('Explanation replaced student answer');
    if (!document.querySelector('.study-progress').textContent.includes('3 / 4')) throw new Error('Explanation granted success');
    await wait(() => document.querySelector('[aria-label="풀이 전 해설 확인"]'), 'before-success explanation history');
    molipCodeEditors.setValue('console.log(7);');
    await click('제출');
    await wait(() => status('수업 완료'), 'normal success after explanation');
    await click('해설 재생 · 정답 실행');
    await wait(() => molipAgent.running, 'post-success explanation');
    await wait(() => !molipAgent.running && !button('해설 재생 · 정답 실행').disabled, 'post-success restore');
    await wait(() => document.querySelector('[aria-label="성공 후 해설 확인"]'), 'after-success explanation history');
    checked.push('explanation restores answer, cannot submit, and records before/after successful solving');
    checked.push('reset is blocked during explanation, cancellation restores input/state, and late execution cannot overwrite it');
    await click('버전 a');
    await wait(() => document.querySelector('.lesson-card')?.textContent.includes('pilot-a'), 'installed A');
    await click('풀모드 시작');
    await wait(() => molipCodeEditors.getValue()?.includes('console.log'), 'update student editor');
    molipCodeEditors.setValue('console.log(99);');
    const beforeReviewedProgress = document.querySelector('.study-progress')?.textContent;
    await click('버전 j');
    await wait(() => document.querySelector('.lesson-card')?.textContent.includes('pilot-j'), 'optional support candidate');
    await click('풀모드 시작');
    await wait(() => document.querySelectorAll('.supporting-material').length === 4, 'four optional aids');
    if (document.querySelector('.supporting-material iframe,.supporting-material img,.interactive-visualization')) throw new Error('Optional aids opened automatically');
    let diagramResult;
    const onDiagram = event => {
      const frame = document.querySelector('.supporting-material iframe');
      if (frame && event.source === frame.contentWindow && event.data?.type === 'molip-support-render') diagramResult = event.data.status;
    };
    window.addEventListener('message', onDiagram);
    await click('값과 출력 그림 · 펼쳐 보기');
    await wait(() => diagramResult, 'vendored Mermaid rendered in sandbox');
    window.removeEventListener('message', onDiagram);
    if (diagramResult !== 'ready') throw new Error('Mermaid drawing failed');
    if (document.querySelector('.supporting-material iframe').getAttribute('sandbox') !== 'allow-scripts') throw new Error('Diagram can access player origin');
    await click('값과 출력 그림 · 접기');
    await click('값 변화 · 펼쳐 보기');
    const facts = () => document.querySelector('.interactive-visualization td')?.textContent;
    await wait(() => facts() === '1', 'first visual state');
    await click('다음 상태');
    await wait(() => facts() === '2', 'next visual state');
    await click('이전 상태');
    await wait(() => facts() === '1', 'previous visual state');
    const condition = document.querySelector('[aria-label="시각화 조건"]');
    condition.value = '1';condition.dispatchEvent(new Event('change', {bubbles:true}));
    await wait(() => facts() === '3', 'condition change resets frame');
    await click('다음 상태');
    await wait(() => facts() === '4', 'alternate next state');
    button('이전 상태').focus();
    if (document.activeElement !== button('이전 상태')) throw new Error('Visualization button is not focusable');
    await click('값 변화 · 접기');
    await click('그림 보기 · 펼쳐 보기');
    await click('만화 보기 · 펼쳐 보기');
    await wait(() => [...document.querySelectorAll('.supporting-material img')].length===2 && [...document.querySelectorAll('.supporting-material img')].every(image => image.complete && image.naturalWidth===1 && image.alt), 'local image and comic load with alt');
    if (molipCodeEditors.getValue() !== 'console.log(99);' || document.querySelector('.study-progress')?.textContent !== beforeReviewedProgress) throw new Error('Optional aids changed answer or progress');
    checked.push('optional aids start collapsed, Mermaid renders isolated, state navigation and conditions work, local image/comic load without changing answer or progress');
    await click('버전 i');
    await wait(() => document.querySelector('.lesson-card')?.textContent.includes('pilot-i'), 'reviewed authoring candidate');
    await click('풀모드 시작');
    await wait(() => document.querySelector('.problem-pane')?.textContent.includes('숫자 3을 출력한 뒤 제출하세요.'), 'reviewed task instruction visible');
    await wait(() => molipCodeEditors.getValue() === 'console.log(99);', 'draft survives reviewed authoring change');
    if (document.querySelector('.study-progress')?.textContent !== beforeReviewedProgress) throw new Error('Reviewed instruction changed student progress');
    if (document.body.textContent.includes('core_flow') || document.body.textContent.includes('synthetic-fixture-only')) throw new Error('Private authoring data leaked into lesson');
    await click('다음 문제 →');
    await wait(() => document.querySelector('.problem-pane')?.textContent.includes('다음 값을 출력해 보세요: 5'), 'unrelated step unchanged after review');
    checked.push('CLI-reviewed candidate renders changed instruction while preserving draft, progress and unrelated step');
    await click('버전 a');
    await wait(() => document.querySelector('.lesson-card')?.textContent.includes('pilot-a'), 'baseline restored after review candidate');
    await click('풀모드 시작');
    await wait(() => molipCodeEditors.getValue() === 'console.log(99);', 'review candidate returns to baseline draft');
    await click('손상 업데이트 공개');
    const contentSettings=document.querySelector('.content-update-controls>details');
    contentSettings.open=true;
    await click('수업 업데이트 확인');
    await wait(() => document.querySelector('.content-update-controls').textContent.includes('고정한 버전과 달라'), 'corrupted content rejected');
    if (molipCodeEditors.getValue() !== 'console.log(99);') throw new Error('Failed content candidate lost answer');
    if (document.querySelector('[aria-label="수업 업데이트 적용"]')) throw new Error('Invalid content became installable');
    await click('새 업데이트 공개');
    await click('수업 업데이트 확인');
    await wait(() => document.querySelector('[aria-label="수업 업데이트 적용"]'), 'valid complete content candidate');
    if (buttons().some(item => item.textContent.includes('값 8 확인'))) throw new Error('Candidate applied without consent');
    document.querySelector('.content-update-controls aside button').click();
    await wait(() => !document.querySelector('.content-update-controls aside'), 'content notice dismissed');
    document.querySelector('[aria-label="수업 업데이트 적용"]').click();
    await wait(() => document.querySelector('.lesson-card')?.textContent.includes('pilot-g'), 'atomic G installation');
    document.querySelector('.content-update-controls>details').open=true;
    await click('변경 이력');
    await wait(() => document.querySelectorAll('.change-entry').length===2, 'creator change history inside player');
    const changeRows=[...document.querySelectorAll('.change-entry')];
    if(changeRows[0].querySelector('time').dateTime !== '2026-10-19T02:00:00Z')throw new Error('History is not newest first');
    if(!changeRows[0].textContent.includes('출력 안내를 읽기 쉽게'))throw new Error('Creator change reason missing');
    if(changeRows[0].querySelector('details').open)throw new Error('Change details are not collapsed');
    changeRows[0].querySelector('summary').click();
    if(!changeRows[0].querySelector('details').open)throw new Error('Change details do not expand');
    document.querySelector('[aria-label="변경 이력 닫기"]').click();
    await wait(() => !document.querySelector('.change-history-panel'), 'history closed inside player');
    checked.push('creator history includes typo reason and time, newest first, with expandable details; update click adds no entry');
    document.querySelector('.content-update-controls>details').open=true;
    document.querySelector('.draft-backups').open=true;
    await wait(() => document.querySelector('.draft-backups')?.textContent.includes('console.log(99)'), 'previous answer recoverable');
    await click('풀모드 시작');
    await wait(() => molipCodeEditors.getValue() === 'console.log(99);', 'draft survives content update');
    if (!document.querySelector('.study-progress').textContent.includes('3 / 4')) throw new Error('Content update lost old achievement or passed new step');
    checked.push('atomic content update, rejected hash, explicit apply, additional learning and recoverable student backup');
    await click('← 코스 수업 목록');
    await click('검증 캐시 지우기');
    await click('코스 추가·만들기');
    await wait(() => document.querySelector('.course-builder input'), 'course import form');
    const repositoryInput=document.querySelector('.course-builder input');
    set.call(repositoryInput,'mq3-validation/course');
    repositoryInput.dispatchEvent(new Event('input',{bubbles:true}));
    await click('코스 불러오기');
    await wait(() => document.querySelector('.lesson-card')?.textContent.includes('pilot-g'), 'uncached course imported');
    await click('풀모드 시작');
    await wait(() => document.querySelector('.study-progress')?.textContent.includes('3 / 4'), 'imported course has installed lessons');
    checked.push('uncached course imported through CourseBuilder and its lesson opens');
    await click('버전 h');
    await wait(() => document.querySelector('.lesson-card')?.textContent.includes('pilot-h'), 'real Git lesson');
    await click('풀모드 시작');
    await wait(() => document.querySelector('[aria-label="Git 실습 터미널 입력"]') && document.querySelector('.repository-task')?.dataset.gitReady === 'true', 'real platform terminal',45000);
    if (document.querySelector('.code-editor')) throw new Error('Git exercise still uses code editor');
    await click('제출');
    await wait(() => status('다시 풀어보세요'), 'unexecuted Git command rejected');
    mq3GitTerminal.command('git switch -c student-work');
    await wait(() => mq3GitTerminal.text().includes("Switched to a new branch 'student-work'"), 'student branch before demonstration');
    await click('해설 재생 · 정답 실행');
    await wait(() => molipAgent.running, 'Git explanation starts');
    await wait(() => mq3GitDemoTerminal.text().split('\n').some(line=>line.trim()==='main'), 'teacher real Git output from independent main branch',45000);
    await wait(() => !molipAgent.running && !button('해설 재생 · 정답 실행').disabled, 'real Git demonstration completes');
    await click('제출');
    await wait(() => status('다시 풀어보세요') && !button('제출').disabled && document.querySelector('.output')?.textContent.includes('student-work'), 'teacher command leaves student branch intact and does not pass student');
    mq3GitTerminal.command('git switch main');
    await wait(() => mq3GitTerminal.text().includes("Switched to branch 'main'"), 'student returns to main');
    mq3GitTerminal.command('git status --porcelain');
    await new Promise(resolve=>setTimeout(resolve,1000));
    await click('제출');
    await wait(() => status('수업 완료'), 'student actual Git command succeeds');
    mq3GitTerminal.command('git switch -c dirty');
    await new Promise(resolve=>setTimeout(resolve,600));
    await click('초기화');
    await wait(() => document.querySelector('.repository-task')?.dataset.gitReady === 'true' && document.querySelector('[aria-label="Git 실습 터미널 입력"]'), 'fresh Git terminal after reset');
    await click('제출');
    await wait(() => status('다시 풀어보세요'), 'reset removed previous actual command evidence');
    mq3GitTerminal.command('git status --porcelain');
    await new Promise(resolve=>setTimeout(resolve,1000));
    await click('제출');
    await wait(() => status('통과했어요'), 'reset recreated clean baseline and local remote');
    checked.push('real platform Git terminal, separate teacher repo, command evidence, and clean reset');
    const terminalInput=document.querySelector('[aria-label="Git 실습 터미널 입력"]');
    terminalInput.focus();terminalInput.dispatchEvent(fullscreenKey());
    await wait(() => document.querySelector('#app-fullscreen-toggle').dataset.fullscreen==='false','terminal fullscreen return');
    terminalInput.dispatchEvent(fullscreenKey());
    await wait(() => document.querySelector('#app-fullscreen-toggle').dataset.fullscreen==='true','terminal fullscreen toggle');
    mq3GitTerminal.command(navigator.platform.toLowerCase().includes('win')?"[Console]::WriteLine('한글 연결 확인')":"printf '한글 연결 확인\\n'");
    await wait(() => mq3GitTerminal.text().split('\n').some(line=>line.trim()==='한글 연결 확인'),'terminal UTF-8 round trip');
    await click('gh 준비 검증');
    await wait(() => document.querySelector('[aria-label="설정 터미널 입력"]')&&!button('로그인 상태 확인').disabled,'existing gh setup terminal');
    await wait(() => /PS |[$%#] /m.test(mq3SetupTerminal.text()),'setup shell prompt',45000);
    const card=document.querySelector('.gh-setup-card').getBoundingClientRect();
    if(Math.abs(card.left+card.width/2-viewportWidth()/2)>4)throw new Error('gh setup is not horizontally centered');
    mq3SetupTerminal.command(navigator.platform.toLowerCase().includes('win')?"[Console]::WriteLine('설정 터미널 확인')":"printf '설정 터미널 확인\\n'");
    await wait(() => mq3SetupTerminal.text().split('\n').some(line=>line.trim()==='설정 터미널 확인'),'gh real terminal output');
    await click('준비 완료 · 연결 확인');
    checked.push('panel handles resize, terminal shortcut/UTF-8 work, and centered existing gh setup runs a real shell');

    }
    await click('검증 높이 720');
    await wait(()=>innerHeight>=640&&innerHeight<=760,'first Git normal-height window');
    await new Promise(resolve=>setTimeout(resolve,500));
    await click('버전 k');
    await wait(() => document.querySelector('.lesson-card')?.textContent.includes('git-first-1'), 'approved first Git lesson');
    await click('풀모드 시작');
    let commandSequence=0;
    const gitReady=async()=>wait(()=>document.querySelector('.repository-task')?.dataset.gitReady==='true' && !button('초기화')?.disabled && !button('제출')?.disabled && window.mq3GitTerminal && document.querySelector('[aria-label="Git 실습 터미널 입력"]'),'first Git terminal ready',45000);
    const resetGit=async()=>{
      const previous=document.querySelector('#git-student-terminal')?.dataset.terminalSession;
      await click('초기화');
      await wait(()=>{const current=document.querySelector('#git-student-terminal')?.dataset.terminalSession;return current&&current!==previous;},'new terminal instance after reset',45000);
      await gitReady();
    };
    const runGit=async command=>{
      const marker=`MQ3_GIT_DONE_${++commandSequence}`;
      const echo=navigator.platform.toLowerCase().includes('win')?`Write-Output '${marker}'`:`printf '${marker}\\n'`;
      mq3GitTerminal.command(`${command}; ${echo}`);
      await wait(()=>mq3GitTerminal.text().split('\n').some(line=>line.trim()===marker),command,30000);
    };
    const nextGit=async()=>{
      const previous=document.querySelector('.repository-task').dataset.taskId;
      await click('다음 문제 →');
      await wait(()=>document.querySelector('.repository-task')?.dataset.taskId!==previous,'next first Git step');
      await gitReady();
    };
    await gitReady();
    molipAgent.setVoice(false);
    await click('제출');await wait(()=>status('다시 풀어보세요'),'first status initially unsolved');
    await runGit('git status');await click('제출');await wait(()=>status('통과했어요'),'first real status');
    await nextGit();
    await click('제출');await wait(()=>status('다시 풀어보세요'),'staging initially unsolved');
    await runGit('git add memo.txt');await click('제출');await wait(()=>status('통과했어요'),'equivalent add command');
    await resetGit();
    await click('제출');await wait(()=>status('다시 풀어보세요'),'reset removed index');
    await runGit('git add -- memo.txt');await click('제출');await wait(()=>status('통과했어요'),'staging after reset');
    await nextGit();
    await runGit('git commit -m "my first record"');await click('제출');await wait(()=>status('통과했어요'),'first commit');
    await nextGit();
    await wait(()=>document.querySelectorAll('input[type=radio]').length===3,'Git and choice shown together');
    await click('검증 높이 720');
    await wait(()=>innerHeight>=640&&innerHeight<=760,'hybrid normal-height window');
    await new Promise(resolve=>setTimeout(resolve,500));
    window.mq3GitLayoutViewport={width:innerWidth,height:innerHeight};
    const hybridPane=document.querySelector('.editor-pane').getBoundingClientRect();
    const choiceBounds=document.querySelector('.answer-interaction').getBoundingClientRect();
    if(choiceBounds.bottom>hybridPane.bottom+1||choiceBounds.top<hybridPane.top)throw new Error(`Git choices escape editor pane: ${JSON.stringify({pane:hybridPane.toJSON(),choices:choiceBounds.toJSON(),viewport:{width:innerWidth,height:innerHeight}})}`);
    document.querySelector('input[type=radio][value="record-changed"]').click();
    await click('제출');await wait(()=>status('다시 풀어보세요'),'wrong Git interpretation');
    document.querySelector('input[type=radio][value="working-only"]').click();
    await click('제출');await wait(()=>status('통과했어요'),'correct Git interpretation');
    await resetGit();
    await wait(()=>!document.querySelector('input[type=radio]:checked'),'Git reset clears saved choice too');
    await nextGit();
    document.querySelector('input[type=radio][value="working-third"]').click();
    await wait(()=>document.querySelector('.answer-state-bridge')?.value==='working-third','student choice reached task state');
    await click('해설 재생 · 정답 실행');
    await wait(()=>molipAgent.running,'staged snapshot demonstration starts');
    await wait(()=>!molipAgent.running&&!button('해설 재생 · 정답 실행').disabled,'staged snapshot demonstration completes',60000);
    await wait(()=>document.querySelector('input[type=radio][value="working-third"]')?.checked,'student Git choice restored');
    await runGit('git show :memo.txt');
    if(!mq3GitTerminal.text().split('\n').some(line=>line.trim()==='둘째 메모'))throw new Error('Git teacher changed student index');
    await click('제출');await wait(()=>status('다시 풀어보세요'),'teacher did not answer for student');
    document.querySelector('input[type=radio][value="staged-second"]').click();
    await click('제출');await wait(()=>status('통과했어요'),'staged snapshot choice');
    await nextGit();
    await runGit('git commit -m "too soon"');await click('제출');await wait(()=>status('다시 풀어보세요'),'commit of wrong snapshot rejected');
    await resetGit();
    await runGit('git add -- memo.txt');await runGit('git commit -m "current memo"');
    await click('제출');await wait(()=>status('수업 완료'),'all six first Git steps solved');
    checked.push('approved six-step Git lesson at normal height: real commands, equivalent add, wrong snapshot rejection, choice reset and isolated teacher playback');

    if (window.mq3IncludeGitBranch) {
      await click('버전 l');
      await wait(()=>document.querySelector('.lesson-card')?.textContent.includes('git-branch-1'),'approved branch lesson');
      await click('풀모드 시작');await gitReady();molipAgent.setVoice(false);
      await click('제출');await wait(()=>status('다시 풀어보세요'),'branch initially absent');
      await runGit('git branch feature');await click('제출');await wait(()=>status('통과했어요'),'branch creation without switching');
      await nextGit();await runGit('git switch feature');await click('제출');await wait(()=>status('통과했어요'),'branch switch');
      await nextGit();await runGit('git add -- guide.txt');await runGit('git commit -m "feature record"');await click('제출');await wait(()=>status('통과했어요'),'feature record preserves main');
      await nextGit();await runGit('git merge feature');await click('제출');await wait(()=>status('통과했어요'),'fast forward merge');
      await nextGit();await runGit('git merge --no-edit feature');await click('제출');await wait(()=>status('통과했어요'),'two parent merge');
      await nextGit();
      document.querySelector('input[type=radio][value="always-conflict"]').click();
      await wait(()=>document.querySelector('.answer-state-bridge')?.value==='always-conflict','same-file choice acknowledged');
      await click('해설 재생 · 정답 실행');await wait(()=>molipAgent.running,'same-file merge teacher');
      await wait(()=>!molipAgent.running&&!button('해설 재생 · 정답 실행').disabled,'same-file merge teacher ends',60000);
      await wait(()=>document.querySelector('input[type=radio][value="always-conflict"]')?.checked,'branch choice restored');
      await runGit('git rev-list --count HEAD');
      if(!mq3GitTerminal.text().split('\n').some(line=>line.trim()==='2'))throw new Error('Teacher merged student history');
      await click('제출');await wait(()=>status('다시 풀어보세요'),'teacher choice does not pass student');
      document.querySelector('input[type=radio][value="auto-merge"]').click();await click('제출');await wait(()=>status('통과했어요'),'same-file changes can merge');
      await nextGit();document.querySelector('input[type=radio][value="choose-content"]').click();await click('제출');await wait(()=>status('통과했어요'),'real conflict needs content decision');
      await nextGit();await runGit('git restore --source=feature --worktree -- guide.txt');
      await click('제출');await wait(()=>status('다시 풀어보세요'),'file-only resolution rejected');
      await runGit('git add -- guide.txt');await click('제출');await wait(()=>status('통과했어요'),'index resolution accepted');
      await resetGit();await click('제출');await wait(()=>status('다시 풀어보세요'),'reset recreated conflict');
      await runGit('git restore --source=feature --worktree -- guide.txt');await runGit('git add -- guide.txt');await click('제출');await wait(()=>status('통과했어요'),'resolve again after reset');
      await nextGit();await click('제출');await wait(()=>status('다시 풀어보세요'),'prepared resolution is not a merge commit');
      await runGit('git commit --no-edit');await click('제출');await wait(()=>status('수업 완료'),'all nine branch and merge steps');
      checked.push('approved nine-step branch lesson: branch pointers, fast forward and two-parent merge, independent demonstration, conflict decision, staged resolution, reset and final merge');
    }

    dioxus.send({passed: true, checked, gitLayoutViewport:window.mq3GitLayoutViewport, userAgent: navigator.userAgent, viewport: {width: innerWidth, height: innerHeight}});
  } catch (error) {
    dioxus.send({passed: false, checked, error: String(error), editorState: editorState(), terminalState:{git:window.mq3GitTerminal?.text(),setup:window.mq3SetupTerminal?.text()}, screen: document.body.innerText.slice(0, 4000)});
  }
})();
