// Runs against the real native player with an isolated GitHub transport.
(async () => {
  const checked = [], frames = [];
  const wait = async (predicate, label) => {
    const until = Date.now() + 25000;
    while (!predicate()) {
      if (Date.now() > until) throw Error(label);
      await new Promise(resolve => setTimeout(resolve, 30));
    }
  };
  const button = text => [...document.querySelectorAll('button')].find(b => b.textContent.trim() === text);
  const click = async text => {await wait(() => button(text) && !button(text).disabled, text);button(text).click();};
  const status = text => document.querySelector('.execution-status')?.textContent.includes(text);
  const observer = new MutationObserver(() => {
    const dialog = document.querySelector('.submission-progress-dialog');
    if (!dialog) return;
    const rect = dialog.getBoundingClientRect();
    frames.push({text:dialog.textContent,centered:Math.abs(rect.x+rect.width/2-innerWidth/2)<3 && Math.abs(rect.y+rect.height/2-innerHeight/2)<3});
    // Keyboard shortcuts must not navigate behind the submitting dialog.
    document.activeElement.dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowRight',ctrlKey:true,metaKey:true,bubbles:true,cancelable:true}));
  });
  try {
    await wait(() => document.querySelector('.lesson-card'), 'catalog');
    if (button('나중에')) await click('나중에');
    observer.observe(document.body,{subtree:true,childList:true,characterData:true});
    await click('학습 시작');
    await wait(() => window.molipCodeEditors?.getValue()!=null, 'editor');
    await click('제출');
    await wait(() => status('다시 풀어보세요') && !document.querySelector('.submission-progress-dialog') && !button('제출').disabled, 'incorrect closes progress');
    if (document.querySelector('.study-navigation button.completed')) throw Error('Incorrect answer marked complete');
    molipCodeEditors.setValue('console.log(3);');
    await wait(() => document.querySelector('[data-code-editor]')?.dataset.editorValue==='console.log(3);', 'answer reached Rust');
    await click('제출');
    await wait(() => document.querySelector('.task-passed-dialog'), 'saved success');
    if (!frames.length || !frames.every(f=>f.centered) || !frames.some(f=>f.text.includes('진도를 저장'))) throw Error('Missing centered progress');
    await wait(() => document.querySelector('.study-navigation button.selected.completed .step-completed-badge')?.textContent==='완료', 'selected completed badge');
    checked.push('centered submission progress closes on incorrect and success; shortcuts cannot navigate behind modal');
    await click('여기 머물기');
    await click('문제 2 · 값 5 확인');
    await wait(() => document.querySelector('.repository-task .problem-pane h2')?.textContent==='값 5 확인' && document.querySelector('[data-code-editor]')?.dataset.editorValue===molipCodeEditors.getValue(), 'second step mounted');
    if (!document.querySelector('.study-navigation button.completed:not(.selected) .step-completed-badge')) throw Error('Completion disappears off selection');
    checked.push('completed badge and selected state remain distinct');
    molipCodeEditors.setValue('console.log(99);');
    await wait(() => document.querySelector('[data-code-editor]')?.dataset.editorValue==='console.log(99);', 'draft saved');
    document.querySelector('.content-update-controls>details').open=true;
    await click('손상 업데이트 공개');
    await click('수업 업데이트 확인');
    await wait(() => document.querySelector('.content-update-controls').textContent.includes('고정한 버전과 달라'), 'bad hash rejected');
    if (document.querySelector('[aria-label="수업 업데이트 적용"]')) throw Error('Invalid update installable');
    await click('새 업데이트 공개');
    await click('수업 업데이트 확인');
    await wait(() => document.querySelector('[aria-label="수업 업데이트 적용"]'), 'update queued');
    if (molipCodeEditors.getValue()!=='console.log(99);') throw Error('Pending update changed answer');
    await click('← 코스 수업 목록');
    await wait(() => document.querySelector('.lesson-card')?.textContent.includes('pilot-g'), 'automatic apply in catalog');
    checked.push('bad hash rejected and valid update automatically applied after leaving active lesson');
    await click('학습 시작');
    await wait(() => document.querySelector('.study-progress')?.textContent.includes('1 / 4'), 'progress preserved without passing added steps');
    await click('문제 2 · 값 5 확인');
    await wait(() => molipCodeEditors.getValue()==='console.log(99);', 'draft survives content update');
    checked.push('content update preserves draft and completion by stable resource code');
    observer.disconnect();
    dioxus.send({passed:true,checked});
  } catch (error) {
    observer.disconnect();
    dioxus.send({passed:false,checked,error:String(error),screen:document.body.innerText});
  }
})();
