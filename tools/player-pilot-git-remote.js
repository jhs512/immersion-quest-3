(async()=>{
 const checked=[],pilot=window.mq3LessonPilot;
 const wait=async(predicate,label,ms=60000)=>{const until=Date.now()+ms;while(Date.now()<until){if(predicate())return;await new Promise(r=>setTimeout(r,40));}throw Error(`Timed out: ${label}`);};
 const button=text=>[...document.querySelectorAll('button')].find(b=>b.textContent.trim()===text);
 const click=async text=>{await wait(()=>button(text)&&!button(text).disabled,text);button(text).click();await new Promise(requestAnimationFrame);};
 const status=text=>document.querySelector('.execution-status')?.textContent.includes(text);
 const ready=async()=>wait(()=>document.querySelector('.repository-task')?.dataset.gitReady==='true'&&window.mq3GitTerminal&&!button('제출')?.disabled,'real student Git terminal');
 let sequence=0,teacherResult='',staleTutorUsed=false;
 const runGit=async command=>{
  const marker=`MQ3_REMOTE_DONE_${++sequence}`;
  const echo=navigator.platform.toLowerCase().includes('win')?`Write-Output '${marker}'`:`printf '${marker}\\n'`;
  mq3GitTerminal.command(`${command}; ${echo}`);
  await wait(()=>mq3GitTerminal.text().split('\n').some(line=>line.trim()===marker),command);
 };
 try{
  await wait(()=>document.querySelector('.lesson-card')?.textContent.includes('pilot-a'),'initial fixture');
  await click('검증 높이 720');await click(`버전 ${pilot.version}`);
  await wait(()=>document.querySelector('.lesson-card')?.textContent.includes(pilot.revision),'remote lesson installed');
  await click('학습 시작');await ready();molipAgent.setVoice(false);
  const original=molipAgent.runExplanation.bind(molipAgent);
  molipAgent.runExplanation=async (actions,options)=>{teacherResult='';return teacherResult=await original(actions,options);};
  for(const [index,task] of pilot.tasks.entries()){
   await wait(()=>document.querySelector('.repository-task')?.dataset.taskId===task.id,'remote step');await ready();
   const marker=[0,2,7].includes(index)?`student-marker-${index}`:null;
   if(marker)await runGit(`git branch ${marker}`);
   // A retired bridge can remain while the next real Git terminal starts.
   if(index===3)window.molipGitTutor={owner:'retired-verification-session',command(){staleTutorUsed=true;return Promise.resolve(false);},dispose(){}};
   await click('해설 재생');await wait(()=>molipAgent.running,'teacher starts');
   await wait(()=>!molipAgent.running&&!button('해설 재생')?.disabled,'teacher finishes');
   if(staleTutorUsed)throw Error('Narration used a retired Git tutor session');
   if(teacherResult.includes('오류 -')||teacherResult.split('git_command:').length-1!==task.narration.filter(a=>a.action==='git_command').length)throw Error(`Remote teacher did not finish: ${teacherResult}`);
   if(marker){
    await runGit(`git branch --list ${marker}`);
    if(!mq3GitTerminal.text().split('\n').some(line=>line.trim()===marker))throw Error('Teacher replaced student repository');
    checked.push(`remote step ${index+1}: teacher preserves student branch and repository`);
   }
   await click('제출');await wait(()=>status('다시 풀어보세요'),'teacher does not pass learner');
   if(task.interaction){
    document.querySelector(`input[type=radio][value="${task.solution}"]`).click();
    await wait(()=>document.querySelector('.answer-state-bridge')?.value===task.solution,'choice echo');
   }else for(const args of pilot.studentCommands[index])await runGit(`git ${args.join(' ')}`);
   await click('제출');await wait(()=>status(index===pilot.tasks.length-1?'수업 완료':'통과했어요'),'real remote goal');
   if([2,6].includes(index)){
    const previous=document.querySelector('#git-student-terminal')?.dataset.terminalSession;
    await click('초기화');await wait(()=>document.querySelector('#git-student-terminal')?.dataset.terminalSession!==previous,'fresh repository');await ready();
    await click('제출');await wait(()=>status('다시 풀어보세요'),'reset removes prior result');
    for(const args of pilot.studentCommands[index])await runGit(`git ${args.join(' ')}`);
    await click('제출');await wait(()=>status(index===pilot.tasks.length-1?'수업 완료':'통과했어요'),'goal after full reset');
   }
   checked.push(`remote step ${index+1}: actual Git state, independent explanation and progress`);
   if(index<pilot.tasks.length-1)await click('다음 문제 →');
  }
  dioxus.send({passed:true,checked,userAgent:navigator.userAgent,voiceListened:false});
 }catch(error){dioxus.send({passed:false,checked,error:String(error),terminalFailure:window.mq3GitDemoFailure,body:document.body.innerText.slice(-4000)});}
})();
