(async()=>{
 const checked=[];
 const wait=async(check,label)=>{const deadline=Date.now()+45000;while(!check()){if(Date.now()>deadline)throw new Error(label);await new Promise(r=>setTimeout(r,30));}};
 const button=text=>[...document.querySelectorAll('button')].find(b=>b.textContent.trim()===text);
 const click=async text=>{await wait(()=>button(text)&&!button(text).disabled,text);button(text).click();};
 const text=()=>window.mq3GitTerminal?.text()||'';
 const visible=()=>{const host=document.querySelector('#git-student-terminal .xterm');return host?.isConnected&&host.getBoundingClientRect().height>0&&!!host.querySelector('canvas,.xterm-rows');};
 try{
  await click('버전 k');await wait(()=>document.querySelector('.lesson-card')?.textContent.includes('git-first-1'),'Git lesson');await click('학습 시작');await click('문제 3 · 준비한 내용을 기록');await wait(()=>document.querySelector('.problem-pane h2')?.textContent==='준비한 내용을 기록','commit task');
  await wait(()=>document.querySelector('.repository-task')?.dataset.gitReady==='true','student ready');
  const owner=document.querySelector('#git-student-terminal').dataset.terminalSession;
  mq3GitTerminal.command('git switch -c student-restore');await wait(()=>text().includes('student-restore'),'student branch');
  molipAgent.setVoice(false);
  for(const cancel of [false,true]){
   await click('해설 재생');await wait(()=>document.querySelector('#git-demo-terminal .xterm'),'demo mounted');
   if(cancel)await click('멈춤');
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
