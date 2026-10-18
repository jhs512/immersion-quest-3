(async()=>{
 const checked=[];
 const wait=async(predicate,label)=>{const until=Date.now()+60000;while(Date.now()<until){if(predicate())return;await new Promise(r=>setTimeout(r,40));}throw Error(`Timed out: ${label}`);};
 const button=text=>[...document.querySelectorAll('button')].find(b=>b.textContent.trim()===text);
 const click=async text=>{await wait(()=>button(text)&&!button(text).disabled,text);button(text).click();};
 const bridge=()=>document.querySelector('.answer-state-bridge');
 const status=text=>document.querySelector('.execution-status')?.textContent.includes(text);
 const answer=async task=>{
  if(task.interaction?.kind==='choice')document.querySelector(`input[type=radio][value="${task.solution}"]`).click();
  else if(task.interaction?.kind==='order')document.querySelector('.answer-order li:last-child button[aria-label="조각 위로"]').click();
  else if(task.interaction?.kind==='fill_fields'){
   for(const [id,value] of Object.entries(JSON.parse(task.solution))){const field=document.querySelector(`[data-answer-field="${id}"]`);field.value=value;field.dispatchEvent(new Event('input',{bubbles:true}));await wait(()=>JSON.parse(bridge()?.value||'{}')[id]===value,'state cell echo');}
  }else molipCodeEditors.setValue(task.solution);
  await wait(()=>task.interaction?.kind==='fill_fields'?Object.entries(JSON.parse(task.solution)).every(([id,value])=>JSON.parse(bridge()?.value||'{}')[id]===value):task.interaction?bridge()?.value===task.solution:document.querySelector('[data-code-editor]')?.dataset.editorValue===task.solution,'answer echo');
 };
 try{
  await click('검증 높이 720');await click('버전 n');await wait(()=>document.querySelector('.lesson-card')?.textContent.includes('java-values-1'),'approved Java lesson');
  await click('풀모드 시작');molipAgent.setVoice(false);
  for(const [index,task] of mq3JavaTasks.entries()){
   await wait(()=>document.querySelector('.repository-task')?.dataset.taskId===task.id&&window.molipCodeEditors?.getValue()!=null,`step ${index+1}`);
   const initialCode=molipCodeEditors.getValue(),initialAnswer=bridge()?.value;
   await click('해설 재생 · 정답 실행');await wait(()=>molipAgent.running,'teacher starts');
   await wait(()=>!molipAgent.running&&document.querySelector('.repository-task').dataset.narrating==='false','teacher ends');
   await wait(()=>molipCodeEditors.getValue()===initialCode&&bridge()?.value===initialAnswer,'student state restored');
   await click('제출');await wait(()=>status('다시 풀어보세요'),'teacher did not solve learner task');
   await answer(task);await click('제출');await wait(()=>status(index===8?'수업 완료':'통과했어요'),'authored solution accepted');
   await click('초기화');await wait(()=>molipCodeEditors.getValue()===initialCode&&bridge()?.value===initialAnswer,'independent reset');
   await click('제출');await wait(()=>status('다시 풀어보세요'),'reset task is unsolved');
   checked.push(`Java step ${index+1}: teacher restoration, wrong answer, correct submission, independent reset`);
   if(index<8)await click('다음 문제 →');
  }
  dioxus.send({passed:true,checked,userAgent:navigator.userAgent,viewport:{width:innerWidth,height:innerHeight}});
 }catch(error){dioxus.send({passed:false,checked,error:String(error),screen:document.body.innerText.slice(0,6000)});}
})();
