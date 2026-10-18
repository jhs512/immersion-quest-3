// Exercise prepared code and a separate answer through the actual native player.
(async()=>{
 const checked=[];
 const wait=async(predicate,label)=>{const until=Date.now()+45000;while(Date.now()<until){if(predicate())return;await new Promise(r=>setTimeout(r,40));}throw Error(`Timed out: ${label}`);};
 const button=text=>[...document.querySelectorAll('button')].find(b=>b.textContent.trim()===text);
 const click=async text=>{await wait(()=>button(text)&&!button(text).disabled,text);button(text).click();};
 const output=()=>document.querySelector('.output')?.textContent.trim();
 const status=text=>document.querySelector('.execution-status')?.textContent.includes(text);
 const choose=async id=>{document.querySelector(`input[type=radio][value="${id}"]`).click();await wait(()=>document.querySelector('.answer-state-bridge')?.value===id,'answer acknowledged');};
 try{
  await click('버전 m');await wait(()=>document.querySelector('.lesson-card')?.textContent.includes('pilot-m'),'example fixture');
  await click('풀모드 시작');await wait(()=>window.molipCodeEditors?.getValue()==='console.log(3);','prepared editor');
  if(document.querySelector('.cm-content').getAttribute('contenteditable')!=='false')throw Error('Prepared example is learner editable');
  await choose('five');await click('코드 실행');await wait(()=>output()==='3','execute prepared code');
  if(!document.querySelector('input[type=radio][value="five"]').checked)throw Error('Running replaced the answer');
  await click('제출');await wait(()=>status('다시 풀어보세요'),'wrong answer remains wrong');
  checked.push('read-only prepared code executes independently of selected answer');
  molipAgent.setVoice(false);await click('해설 재생 · 정답 실행');await wait(()=>molipAgent.running,'teacher starts');
  await wait(()=>!molipAgent.running&&!button('해설 재생 · 정답 실행').disabled,'teacher ends');
  await wait(()=>molipCodeEditors.getValue()==='console.log(3);'&&document.querySelector('input[type=radio][value="five"]')?.checked,'student example and choice restored');
  await click('제출');await wait(()=>status('다시 풀어보세요'),'teacher did not pass student');
  checked.push('teacher can edit and run the example, then restores learner answer without granting success');
  await click('초기화');await wait(()=>document.querySelector('.answer-state-bridge')?.value===''&&molipCodeEditors.getValue()==='console.log(3);','reset example and answer');
  await choose('three');await click('제출');await wait(()=>status('통과했어요'),'correct answer');
  checked.push('reset restores both inputs and only a correct submission grants success');
  dioxus.send({passed:true,checked,userAgent:navigator.userAgent});
 }catch(error){dioxus.send({passed:false,checked,error:String(error),screen:document.body.innerText.slice(0,5000)});}
})();
