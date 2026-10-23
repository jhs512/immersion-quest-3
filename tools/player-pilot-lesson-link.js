(async()=>{
 const checked=[], wait=async(fn,label)=>{const end=Date.now()+45000;while(Date.now()<end){if(fn())return;await new Promise(r=>setTimeout(r,40));}throw Error(label);};
 try{
  const targets=window.mq3LinkTargets;
  await wait(()=>document.querySelector('.repository-task')?.dataset.taskId===targets.first,'cold link did not open its lesson');
  const link=document.querySelector('.repository-header [data-lesson-link]')?.dataset.lessonLink;
  if(new URL(link).searchParams.get('course')!==targets.course)throw Error('share link lost course identity');
  checked.push('cold web link opens the exact course lesson after login');
  document.querySelector('.course-back').click();
  await wait(()=>!document.querySelector('.repository-task'),'return to catalog before reopening link');
  dioxus.send({control:'lesson-link-stage',stage:'first'});
  await wait(()=>document.querySelector('.repository-task')?.dataset.taskId===targets.second,'existing instance did not receive link');
  checked.push('second process forwards its link to the existing player');
  dioxus.send({control:'lesson-link-stage',stage:'second'});
  await wait(()=>document.body.innerText.includes('코스에 이 수업이 없거나 현재 계정에서 열 수 없어요.'),'wrong-course link was not rejected');
  if(document.querySelector('.repository-task')?.dataset.taskId!==targets.second)throw Error('invalid link replaced current lesson');
  checked.push('invalid course membership preserves the active lesson');
  dioxus.send({control:'lesson-link-stage',stage:'course'});
  await wait(()=>!document.querySelector('.repository-task')&&document.querySelector('.course-catalog .lesson-card'),'course-only link did not stop at the lesson list');
  if(!document.querySelector('.course-selected')?.innerText.includes(targets.course))throw Error('course-only link selected the wrong course');
  checked.push('course-only link returns to its course list without opening a lesson');
  dioxus.send({passed:true,checked});
 }catch(error){dioxus.send({passed:false,checked,error:String(error),screen:document.body.innerText.slice(-4000)});}
})();
