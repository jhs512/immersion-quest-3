(async()=>{
 const checked=[];const wait=async(test,label)=>{const end=Date.now()+60000;while(!test()){if(Date.now()>end)throw new Error(label);await new Promise(r=>setTimeout(r,30));}};
 const button=text=>[...document.querySelectorAll('button')].find(b=>b.textContent.trim()===text);
 const click=async text=>wait(()=>{const control=button(text);if(!control||control.disabled)return false;control.click();return true;},text);
 try{
  // The native harness selects Bash before launching the app. Do not remount
  // the player through the version toolbar while lesson opening is in flight.
  await wait(()=>document.querySelector('.lesson-card .lesson-revision')?.textContent.includes('bash-basics-'),'Bash lesson card');
  await click('학습 시작');
  await wait(()=>document.querySelectorAll('.study-navigation button').length===24,'Bash lesson opened');
  await click('문제 2 · 파일 목록을 확인하세요');await wait(()=>document.querySelector('.problem-pane h2')?.textContent==='파일 목록을 확인하세요','ls task mounted');await wait(()=>document.querySelector('.repository-task')?.dataset.gitReady==='true','Bash terminal ready');
  if(!document.body.textContent.includes('Bash 터미널')||!document.querySelector('.problem-pane ol'))throw new Error('Bash label or ordered tasks missing');
  molipAgent.setVoice(false);await click('해설 재생');
  await wait(()=>window.mq3GitDemoTerminal?.text().includes('$ ls'),'first Bash ls is demonstrated');
  await wait(()=>document.querySelector('.repository-task')?.dataset.narrating==='false','ls explanation finishes');
  checked.push('Bash ls and ordered task list render in the native WebView');
  const ready=async()=>wait(()=>document.querySelector('.repository-task')?.dataset.gitReady==='true'&&/\$\s*$/.test(mq3GitTerminal.text()),'student terminal ready');
  const run=async command=>{const before=mq3GitTerminal.text();mq3GitTerminal.command(command);await wait(()=>mq3GitTerminal.text()!==before&&/\$\s*$/.test(mq3GitTerminal.text()),command);};
  await click('문제 9 · 같은 이름의 파일을 만드세요');await wait(()=>document.querySelector('.problem-pane h2')?.textContent==='같은 이름의 파일을 만드세요','step nine mounted');await ready();
  const previous=document.querySelector('#git-student-terminal').dataset.terminalSession;
  await click('초기화');await wait(()=>document.querySelector('#git-student-terminal')?.dataset.terminalSession!==previous,'step nine resets without visiting step one');await ready();
  await run('pwd');if(!/\/notes\s*\n\$/.test(mq3GitTerminal.text().trim()))throw Error('step nine cwd was not restored');
  await run('cat ../memo.txt');if(!mq3GitTerminal.text().includes('둘째 줄'))throw Error('previous step memo was lost');
  await run('echo "폴더 안 메모" >\u00a0memo.txt');await run('cat memo.txt');
  await click('제출');await wait(()=>document.querySelector('.result-pane')?.dataset.feedback==='passed','NBSP input creates the correct file and passes step nine');
  await click('여기 머물기');
  const solvedOwner=document.querySelector('#git-student-terminal').dataset.terminalSession;
  await click('초기화');await wait(()=>document.querySelector('#git-student-terminal')?.dataset.terminalSession!==solvedOwner,'reset clears current feedback');await ready();
  if(![...document.querySelectorAll('.study-navigation button')].find(b=>b.textContent.includes('문제 9'))?.textContent.includes('✓'))throw Error('reset cleared completion history');
  checked.push('Bash step nine resets independently, converts NBSP, and preserves completion history');
  document.querySelector('[aria-label="학습 정보"]').click();await wait(()=>document.querySelector('#lesson-info-dialog')?.open,'learning info dialog opens');
  window.overviewHeld=null;molipVoice.synthesize=async text=>text;
  window.Audio=class{constructor(text){this.text=text;}play(){overviewHeld=this;return Promise.resolve();}pause(){}};
  await click('목표와 학습 방법 해설');
  await wait(()=>overviewHeld&&document.querySelector('#lesson-goal-0.overview-speaking'),'overview speaks and highlights first goal');
  const highlighted=document.querySelector('#lesson-goal-0');if(getComputedStyle(highlighted).outlineStyle==='none')throw new Error('overview highlight is not visible');
  await click('닫기');await wait(()=>!molipAgent.running&&!document.querySelector('.overview-speaking'),'closing info stops speech');
  checked.push('Learning info overview highlights the spoken objective and closing cancels speech');
  dioxus.send({passed:true,checked});
 }catch(error){dioxus.send({passed:false,checked,error:String(error),screen:document.body.innerText.slice(-5000),demo:window.mq3GitDemoTerminal?.text(),student:window.mq3GitTerminal?.text()});}
})();
