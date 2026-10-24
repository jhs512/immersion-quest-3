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
  // The final clear: local storage is locked again (the recorder cannot commit) and every
  // GitHub progress read takes four seconds. Returning to the list must show 100% at once.
  const catalogPercent=()=>document.querySelector('.lesson-progress strong')?.textContent.trim();
  molipCodeEditors.setValue('console.log(5);');await wait(()=>document.querySelector('[data-code-editor]')?.dataset.editorValue==='console.log(5);','second source saved');
  await stats('slow-remote');state=await stats('pause-record');const pausedAt=Date.now();
  const readsBefore=state.reads;
  await click('제출');await wait(()=>document.querySelector('.task-passed-dialog'),'second clear');
  await click('수업 목록으로');
  const returned=Date.now();
  while(catalogPercent()!=='100% 완료'){if(Date.now()-returned>1500)throw Error(`catalog did not show 100% at once: ${catalogPercent()} after ${Date.now()-returned}ms`);await new Promise(r=>setTimeout(r,20));}
  const shownAfter=Date.now()-returned;
  state=await stats();
  if(!state.locked)throw Error('local storage was released before 100% was checked');
  if(!document.querySelector('.study-progress')?.textContent.includes('필수 수업 1 / 1'))throw Error('course summary is not complete: '+document.querySelector('.study-progress')?.textContent);
  checked.push(`final clear reads 100% in the catalog ${shownAfter}ms after return while the local save is locked and GitHub reads are slow (reads ${readsBefore}->${state.reads}, none can finish within 4s)`);
  // GitHub goes offline as well; the local save then completes. A failed or late remote read
  // must leave the fresh completion on screen.
  // Keep SQLite locked past its 5s busy_timeout: the recorder's first save attempt fails and
  // must be retried from its journal, not logged and dropped.
  while(Date.now()-pausedAt<7000){if(catalogPercent()!=='100% 완료')throw Error('catalog rolled back while the save was locked: '+catalogPercent());await new Promise(r=>setTimeout(r,100));}
  state=await stats();if(!state.locked)throw Error('local storage was released early');
  await stats('offline-remote');await stats('resume-record');
  const recordDeadline=Date.now()+20000;
  while((state=await stats()).pending<4){if(Date.now()>recordDeadline)throw Error('second clear not durable');await new Promise(r=>setTimeout(r,50));}
  const settle=Date.now()+9000;
  while(Date.now()<settle){if(catalogPercent()!=='100% 완료')throw Error('catalog rolled back while GitHub was slow/offline: '+catalogPercent());await new Promise(r=>setTimeout(r,100));}
  checked.push('slow then offline GitHub reads and a local save locked for 7s (past the 5s busy timeout) never roll the catalog back, and the retried save still lands');
  await stats('online-remote');
  await stats('advance-hour');
  const uploadUntil=Date.now()+20000;
  while((state=await stats()).pending>0){if(Date.now()>uploadUntil)throw Error("upload deadline");await new Promise(r=>setTimeout(r,100));}
  checked.push('next clear uploads earlier history and lesson completion');
  // After the retried upload, reopening and returning reads the same completion from GitHub.
  await click('학습 시작');await wait(()=>document.querySelector('.course-back'),'lesson reopened');
  await click('← 코스 수업 목록');
  await wait(()=>catalogPercent()==='100% 완료','catalog after upload');
  await new Promise(r=>setTimeout(r,1500));
  if(catalogPercent()!=='100% 완료')throw Error('catalog changed after the remote refresh: '+catalogPercent());
  checked.push('after the upload a fresh remote refresh keeps 100%');
  dioxus.send({passed:true,checked});
 }catch(error){dioxus.send({passed:false,checked,error:String(error),screen:document.body.innerText});}
})();
