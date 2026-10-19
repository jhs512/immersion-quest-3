// Runs inside the actual installed-player WebView for a sequential restart test.
(async()=>{
  const phase=window.mq3RestartPhase;
  const wait=async(predicate,label)=>{const deadline=Date.now()+18000;while(Date.now()<deadline){if(predicate())return;await new Promise(resolve=>setTimeout(resolve,40));}throw new Error(label);};
  const button=text=>[...document.querySelectorAll('button')].find(item=>item.textContent.trim()===text&&!item.disabled);
  try {
    await wait(()=>button('학습 시작'),'Course catalog did not open');
    button('학습 시작').click();
    await wait(()=>window.molipCodeEditors?.getValue()!=null,'Editor did not mount');
    if(phase==='seed') {
      molipCodeEditors.setValue('console.log(3);');
      button('제출').click();
      await wait(()=>document.querySelector('.execution-status')?.textContent.includes('통과했어요'),'Initial problem did not pass');
      molipCodeEditors.setValue('console.log(99);');
      await wait(()=>document.querySelector('[data-code-editor]')?.dataset.editorValue==='console.log(99);','Draft did not reach player state');
    } else {
      if(molipCodeEditors.getValue()!=='console.log(99);')throw new Error('Restart lost the student draft');
      await wait(()=>document.querySelector('.study-progress')?.textContent.includes('1 / 2'),'Restart lost prior success');
      if(document.querySelector('.study-progress').textContent.includes('최신 버전 완료'))throw new Error('Restart passed the unfinished problem');
    }
    const draft=molipCodeEditors.getValue(),progress=document.querySelector('.study-progress').textContent;
    button('버전 h').click();
    await wait(()=>button('학습 시작'),'Git catalog did not open');button('학습 시작').click();
    await wait(()=>document.querySelector('.repository-task')?.dataset.gitReady==='true','Git practice did not mount');
    if(phase==='seed') {
      mq3GitTerminal.command(navigator.platform.toLowerCase().includes('win')
        ? "git switch -c restart-check; Set-Content -NoNewline -LiteralPath tracked.txt -Value 'staged'; git add tracked.txt; Set-Content -NoNewline -LiteralPath tracked.txt -Value 'working'; git status --short"
        : "git switch -c restart-check; printf staged > tracked.txt; git add tracked.txt; printf working > tracked.txt; git status --short");
      await wait(()=>mq3GitTerminal.text().includes('MM tracked.txt'),'Git staged and working changes were not prepared');
    } else {
      mq3GitTerminal.command('git branch --show-current; git show :tracked.txt; git diff --numstat; git status --short');
      await wait(()=>mq3GitTerminal.text().split('\n').some(line=>line.trim()==='restart-check')&&mq3GitTerminal.text().includes('MM tracked.txt'),'Restart lost the Git branch or index/worktree changes');
      if(!mq3GitTerminal.text().includes('staged'))throw new Error('Restart lost staged file contents');
    }
    button('버전 a').click();
    await wait(()=>button('학습 시작'),'Restored code catalog did not open');button('학습 시작').click();
    await wait(()=>window.molipCodeEditors?.getValue()==='console.log(99);','Code draft changed after Git practice');
    dioxus.send({passed:true,phase,draft,progress,git:{branch:'restart-check',index:'staged',worktree:'modified'}});
  } catch(error) {dioxus.send({passed:false,phase,error:String(error),screen:document.body.innerText.slice(0,2500)});}
})();
