(async()=>{
 const checked=[];
 const wait=async(fn,label)=>{const end=Date.now()+45000;while(Date.now()<end){if(fn())return;await new Promise(r=>setTimeout(r,40));}throw Error(`Timed out: ${label}`)};
 const button=text=>[...document.querySelectorAll('button')].find(b=>b.textContent.trim()===text);
 const click=async text=>{await wait(()=>button(text)&&!button(text).disabled,text);button(text).click()};
 const ready=async()=>wait(()=>{const root=document.querySelector('.repository-task'),host=document.getElementById('git-student-terminal');return root?.dataset.gitReady==='true'&&host&&window.mq3GitTerminal?.text(host.dataset.terminalSession).split('\n').some(line=>line.trimEnd().endsWith('$'));},'current student terminal owner and prompt');
 try{
  await wait(()=>document.querySelector('.lesson-card'),'catalog');
  for(const [version,revision,count] of [['l','git-branch-1',4],['굳','git-branch-advanced-1',5],['풀','github-pr-1',8]]){
   await click(`버전 ${version}`);
   await wait(()=>document.querySelector('.lesson-card')?.textContent.includes(revision),revision);
   await click('학습 시작');await ready();
   if(document.querySelectorAll('.study-navigation button').length!==count)throw Error(`${revision} task count`);
   const firstId=document.querySelector('.repository-task').dataset.taskId;
   for(let i=0;i<count;i++){
    const nav=document.querySelectorAll('.study-navigation button')[i];nav.click();await wait(()=>document.querySelectorAll('.study-navigation button')[i]?.classList.contains('selected'),'selected task');await ready();
    if(version==='l'&&i===1){
     const owner=document.querySelector('#git-student-terminal').dataset.terminalSession;
     await click('초기화');await wait(()=>document.querySelector('#git-student-terminal')?.dataset.terminalSession!==owner,'middle Git step reset');await ready();
     checked.push('shared Git step resets without returning to the first step');
    }
    await new Promise(r=>setTimeout(r,120));
    if(!document.querySelector('.problem-pane h2')?.textContent.trim())throw Error(`${revision} empty task ${i}`);
    const pane=document.querySelector('.git-terminal').getBoundingClientRect();
    if(pane.width<=0||pane.height<=0||pane.left<0||pane.right>innerWidth+1)throw Error(`${revision} terminal layout ${JSON.stringify(pane.toJSON())}`);
   }
   checked.push(`${revision}: all ${count} tasks render with the real terminal`);
   if(version==='풀'){
    document.querySelector('.study-navigation button').click();await wait(()=>document.querySelector('.repository-task')?.dataset.taskId===firstId,'first PR task mounted');await ready();
    mq3GitTerminal.command("printf 'keep\\n' > keep.txt; printf 'PR_KEEP_BEFORE\\n'");
    await wait(()=>mq3GitTerminal.text().split('\n').some(line=>line.trim()==='PR_KEEP_BEFORE'),'student file');
    await wait(()=>window.molipAgent,'explanation agent');molipAgent.setVoice(false);
    await click('해설 재생');await wait(()=>document.getElementById('git-demo-terminal'),'separate teacher terminal');
    // With voice off these read-only explanations can finish before a stop click.
    molipAgent.stop();if(button('멈춤')&&!button('멈춤').disabled)button('멈춤').click();await ready();
    mq3GitTerminal.command("cat keep.txt; printf 'PR_KEEP_AFTER\\n'");
    await wait(()=>mq3GitTerminal.text().split('\n').some(line=>line.trim()==='PR_KEEP_AFTER'),'student survives explanation');
    if(!mq3GitTerminal.text().split('\n').some(line=>line.trim()==='keep'))throw Error('student file lost');
    checked.push('PR explanation uses an independent local terminal and preserves learner work');
   }
   await click('← 코스 수업 목록');
  }
  dioxus.send({passed:true,checked,userAgent:navigator.userAgent});
 }catch(error){dioxus.send({passed:false,checked,error:String(error),screen:document.body.innerText.slice(-5000),terminal:window.mq3GitTerminal?.text()});}
})();
