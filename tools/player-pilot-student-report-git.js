(async()=>{
 const checked=[];
 const wait=async(fn,label)=>{const end=Date.now()+30000;while(!fn()){if(Date.now()>end)throw Error(label);await new Promise(r=>setTimeout(r,40));}};
 const button=text=>[...document.querySelectorAll('button')].find(b=>b.textContent.trim()===text&&!b.disabled);
 const click=async text=>{await wait(()=>button(text),text);button(text).click();};
 const ready=async()=>wait(()=>document.querySelector('.repository-task')?.dataset.gitReady==='true'&&window.mq3GitTerminal?.text().includes('$ '),'terminal ready');
 let sequence=0;
 const command=async value=>{const mark=`REPORT_GIT_${++sequence}`;mq3GitTerminal.command(`${value}; printf '\n${mark}\n'`);await wait(()=>mq3GitTerminal.text().split('\n').some(l=>l.trim()===mark),value);};
 try{
  await wait(()=>document.querySelector('.lesson-card'),'catalog');
  await click('버전 k');await wait(()=>document.querySelector('.lesson-card')?.textContent.includes('git-first-3'),'current content');
  await click('학습 시작');await ready();
  const nav=[...document.querySelectorAll('.study-navigation button')];
  if(!nav[0].classList.contains('completed')||!nav[1].classList.contains('completed')||nav[2].classList.contains('completed'))throw Error('old progress not preserved precisely');
  nav[2].click();await wait(()=>document.querySelector('.problem-pane h2')?.textContent.includes('첫 커밋'),'third step');await ready();
  if(!document.querySelector('.practice-start-notice')?.textContent.includes('앞 단계'))throw Error('missing preparation notice');
  await command('cat memo.txt; git show :memo.txt; git status --short');
  if(!mq3GitTerminal.text().includes('첫 메모')||!mq3GitTerminal.text().includes('A  memo.txt'))throw Error('missing memo or staging');
  checked.push('old completion survives current content and step three restores memo/index with a visible notice');
  await click('제출');await wait(()=>document.querySelector('.execution-status')?.textContent.includes('다시 풀어보세요'),'commit is not fabricated');
  await command('git commit -m "직접 커밋"');
  await click('제출');await wait(()=>document.querySelector('.task-passed-dialog'),'actual commit passes');
  await click('여기 머물기');await command("printf 'learner-preserved\\n' > keep.txt");
  checked.push('student commits directly and grading passes without pre-completing the step');
  dioxus.send({passed:true,checked});
 }catch(error){dioxus.send({passed:false,checked,error:String(error),screen:document.body.innerText,terminal:window.mq3GitTerminal?.text()});}
})();
