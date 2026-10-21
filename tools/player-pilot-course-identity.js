(async()=>{
 const checked=[],wait=async(fn,label)=>{const end=Date.now()+45000;while(Date.now()<end){if(fn())return;await new Promise(r=>setTimeout(r,50));}throw Error(label);};
 const input=()=>document.getElementById('course-display-name');
 const set=value=>{const e=input();Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(e,value);e.dispatchEvent(new Event('input',{bubbles:true}));};
 try{
  await wait(()=>input()&&!input().disabled,'name input did not load');
  const starts=()=>[...document.querySelectorAll('.repository-lessons button')].filter(b=>b.textContent==='학습 시작');
  if(!starts().length||starts().some(b=>!b.disabled))throw Error('unregistered learner can start');
  checked.push('first course entry requires a name');
  set(' [BE16]홍 길동 ');await new Promise(r=>setTimeout(r,100));input().form.requestSubmit();
  await wait(()=>input().value==='[BE16]홍길동'&&!input().disabled&&document.querySelector('.course-identity').textContent.includes('이름을 저장했어요'),'name did not sync');
  if(starts().some(b=>b.disabled))throw Error('registration did not unlock lessons');
  checked.push('spaces removed and successful enrollment unlocks learning');
  set('[BE16]바꾼이름');await new Promise(r=>setTimeout(r,100));input().form.requestSubmit();
  await wait(()=>!input().disabled&&document.querySelector('.course-identity').textContent.includes('이름을 저장했어요'),'rename did not sync');
  checked.push('course display name can be changed');
  dioxus.send({passed:true,checked});
 }catch(e){dioxus.send({passed:false,error:String(e),checked,body:document.body.innerText.slice(-4000)});}
})();
