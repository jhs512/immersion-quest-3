(async()=>{
 const checked=[];
 const wait=async(check,label)=>{const deadline=Date.now()+90000;while(!check()){if(Date.now()>deadline)throw new Error(label);await new Promise(r=>setTimeout(r,30));}};
 const button=text=>[...document.querySelectorAll('button')].find(b=>b.textContent.trim()===text);
 const click=async text=>{await wait(()=>button(text)&&!button(text).disabled,text);button(text).click();};
 const text=()=>window.mq3GitTerminal?.text()||'';
 const visible=()=>{const host=document.querySelector('#git-student-terminal .xterm');return host?.isConnected&&host.getBoundingClientRect().height>0&&!!host.querySelector('canvas,.xterm-rows');};
 try{
  await click('버전 k');await wait(()=>document.querySelector('.lesson-card')?.textContent.includes('git-first-'),'Git lesson');await click('학습 시작');
  await click('문제 1 · 메모 파일의 상태를 확인해 보세요');
  await wait(()=>document.querySelector('.repository-task')?.dataset.gitReady==='true','first terminal ready');
  molipAgent.setVoice(false);
  await click('해설 재생');
  await wait(()=>window.mq3GitDemoTerminal?.text().includes('Untracked files'),'first explanation reaches Git status');
  const survey=window.mq3GitDemoTerminal.text();
  const commands=['pwd','ls','git init','echo "첫 메모" > memo.txt','cat memo.txt','git status'].map(command=>survey.indexOf('$ '+command));
  if(commands.some(index=>index<0)||commands.some((index,i)=>i>0&&index<=commands[i-1]))throw new Error('first explanation command order: '+survey);
  await wait(()=>document.querySelector('.repository-task')?.dataset.narrating==='false','first explanation finishes');
  await click('문제 3 · 준비한 메모를 첫 커밋으로 남기세요');await wait(()=>document.querySelector('.problem-pane h2')?.textContent==='준비한 메모를 첫 커밋으로 남기세요','commit task');
  await wait(()=>document.querySelector('.repository-task')?.dataset.gitReady==='true','student ready');
  const owner=document.querySelector('#git-student-terminal').dataset.terminalSession;
  mq3GitTerminal.command('git init');await wait(()=>text().includes('Initialized empty Git repository'),'student creates Git repository');
  mq3GitTerminal.command('git switch -c student-restore');await wait(()=>text().includes('student-restore'),'student branch');
  molipAgent.setVoice(false);
  for(const cancel of [false,true]){
   await click('해설 재생');await wait(()=>document.querySelector('#git-demo-terminal .xterm'),'demo mounted');
   if(cancel)await click('멈춤');
   else {
    await wait(()=>window.mq3GitDemoTerminal?.text().split('\n').some(line=>line.trim()==='첫 메모'),'cat shows actual memo contents');
    if(window.mq3GitDemoTerminal.text().includes('$ git init'))throw new Error('later explanation must not repeat git init');
    if(window.mq3GitDemoTerminal.text().includes('$ echo'))throw new Error('later explanation must not recreate earlier files');
    if(!window.mq3GitDemoTerminal.text().includes('git commit -m'))throw new Error('current step must demonstrate commit');
   }
   await wait(()=>document.querySelector('.repository-task')?.dataset.narrating==='false','explanation finished');
   await wait(()=>visible(),'student terminal visible');
   if(document.querySelector('#git-student-terminal').dataset.terminalSession!==owner)throw new Error('student shell replaced');
   const marker=cancel?'RESTORED_CANCEL':'RESTORED_COMPLETE';
   mq3GitTerminal.command(`git branch --show-current; echo ${marker}`);
   await wait(()=>text().split('\n').some(line=>line.trim()===marker),'student shell accepts input');
   if(!text().split('\n').some(line=>line.trim()==='student-restore'))throw new Error('student work lost');
   checked.push(cancel?'cancel restores visible live student terminal':'completion restores visible live student terminal');
  }
  dioxus.send({passed:true,checked});
 }catch(error){dioxus.send({passed:false,checked,error:String(error),studentText:text(),screen:document.body.innerText.slice(-3000),html:document.querySelector('.editor-pane')?.innerHTML.slice(0,3000)});}
})();
