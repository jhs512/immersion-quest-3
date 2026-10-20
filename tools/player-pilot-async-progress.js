(async()=>{
 const checked=[];
 const wait=async(fn,label)=>{const end=Date.now()+20000;while(!fn()){if(Date.now()>end)throw Error(label);await new Promise(r=>setTimeout(r,30));}};
 const button=text=>[...document.querySelectorAll('button')].find(b=>b.textContent.trim()===text&&!b.disabled);
 const click=async text=>{await wait(()=>button(text),text);button(text).click();};
 let token=0;
 const stats=async(control='stats')=>{const next=++token;dioxus.send({control,token:next});await wait(()=>window.mq3ProgressStats?.token===next,'progress stats');return mq3ProgressStats;};
 try{
  await click('학습 시작');await wait(()=>window.molipCodeEditors?.getValue()!=null,'editor');
  molipCodeEditors.setValue('console.log(3);');await wait(()=>document.querySelector('[data-code-editor]')?.dataset.editorValue==='console.log(3);','first source saved');
  await stats('pause-record');
  await click('제출');await wait(()=>document.querySelector('.task-passed-dialog'),'clear does not wait for local or remote storage');
  if(document.querySelector('.submission-progress-dialog')||document.querySelector('.execution-status')?.textContent.includes('저장'))throw Error('UI still checks saving');
  let state;
  if(!document.querySelector('.study-navigation button.completed'))throw Error('local completion missing');
  await click('다음으로 이동');await wait(()=>document.querySelector('.problem-pane h2')?.textContent==='값 5 확인','can navigate while offline');
  if(document.querySelector('.task-paging'))throw Error('Bottom paging bar remains');
  document.body.dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowLeft',ctrlKey:true,metaKey:true,bubbles:true,cancelable:true}));
  await wait(()=>document.querySelector('.problem-pane h2')?.textContent==='값 3 확인','previous shortcut without footer');
  document.body.dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowRight',ctrlKey:true,metaKey:true,bubbles:true,cancelable:true}));
  await wait(()=>document.querySelector('.problem-pane h2')?.textContent==='값 5 확인','next shortcut without footer');
  await stats('resume-record');
  const recordUntil=Date.now()+20000;
  while((state=await stats()).pending<1){if(Date.now()>recordUntil)throw Error('offline event not retained');await new Promise(r=>setTimeout(r,30));}
  checked.push('clear and next problem are available while local storage is locked and GitHub writes fail');
  await stats('advance-hour');
  const retriesUntil=Date.now()+20000;
  while((state=await stats()).attempts<1||state.running){if(Date.now()>retriesUntil)throw Error("retry deadline");await new Promise(r=>setTimeout(r,100));}
  const attempts=state.attempts;await new Promise(r=>setTimeout(r,500));state=await stats();
  if(state.attempts!==attempts||state.pending<1)throw Error('retries did not stop with retained history');
  checked.push('one hourly upload attempt stops after failure and pending history remains');
  await stats('resume');
  molipCodeEditors.setValue('console.log(5);');await wait(()=>document.querySelector('[data-code-editor]')?.dataset.editorValue==='console.log(5);','second source saved');
  await click('제출');await wait(()=>document.querySelector('.task-passed-dialog'),'second clear');
  const recordDeadline=Date.now()+20000;
  while((state=await stats()).pending<4){if(Date.now()>recordDeadline)throw Error('second clear not durable');await new Promise(r=>setTimeout(r,50));}
  await stats('advance-hour');
  const uploadUntil=Date.now()+20000;
  while((state=await stats()).pending>0){if(Date.now()>uploadUntil)throw Error("upload deadline");await new Promise(r=>setTimeout(r,100));}
  checked.push('next clear uploads earlier history and lesson completion');
  dioxus.send({passed:true,checked});
 }catch(error){dioxus.send({passed:false,checked,error:String(error),screen:document.body.innerText});}
})();
