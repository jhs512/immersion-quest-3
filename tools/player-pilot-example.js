// Exercise prepared code and a separate answer through the actual native player.
(async()=>{
 const checked=[],inputTrace=[];
 const wait=async(predicate,label)=>{const until=Date.now()+45000;while(Date.now()<until){if(predicate())return;await new Promise(r=>setTimeout(r,40));}throw Error(`Timed out: ${label}`);};
 const button=text=>[...document.querySelectorAll('button')].find(b=>b.textContent.trim()===text);
 const click=async text=>{await wait(()=>button(text)&&!button(text).disabled,text);button(text).click();await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));};
 const output=()=>document.querySelector('.output')?.textContent.trim();
 const status=text=>document.querySelector('.execution-status')?.textContent.includes(text);
 const choiceState=()=>({answer:document.querySelector('.answer-state-bridge')?.value,narrating:document.querySelector('.repository-task')?.dataset.narrating,options:[...document.querySelectorAll('input[type=radio]')].map(radio=>({id:radio.value,checked:radio.checked,disabled:radio.matches(':disabled')}))});
 const choose=async id=>{
  await wait(()=>{const state=choiceState();return state.narrating==='false'&&state.options.length>0&&state.options.every(option=>!option.disabled&&option.checked===(option.id===state.answer));},'controlled choices ready');
  inputTrace.push({before:choiceState(),click:id});
  document.querySelector(`input[type=radio][value="${id}"]`).click();
  await wait(()=>document.querySelector('.answer-state-bridge')?.value===id,'answer acknowledged');
  inputTrace.push({after:choiceState()});
 };
 try{
  // Let the initial installation finish before the debug control replaces its store.
  await wait(()=>document.querySelector('.lesson-card')?.textContent.includes('pilot-a'),'initial fixture installed');
  await click('버전 m');await wait(()=>document.querySelector('.lesson-card')?.textContent.includes('pilot-m'),'example fixture');
  await click('학습 시작');await wait(()=>window.molipCodeEditors?.getValue()==='console.log(3);','prepared editor');
  if(document.querySelector('.cm-content').getAttribute('contenteditable')!=='false')throw Error('Prepared example is learner editable');
  if(!button('코드 실행').disabled)throw Error('Prediction must precede execution');
  molipAgent.setVoice(false);await click('해설 재생');await wait(()=>molipAgent.running,'teacher before prediction starts');
  await wait(()=>!molipAgent.running&&!button('해설 재생').disabled,'teacher before prediction ends');
  await wait(()=>document.querySelector('.answer-state-bridge')?.value===''&&molipCodeEditors.getValue()==='console.log(3);','unanswered prediction restored');
  if(!button('코드 실행').disabled)throw Error('Teacher must not satisfy learner prediction gate');
  await choose('five');await click('코드 실행');await wait(()=>output()==='3','execute prepared code');
  if(!document.querySelector('input[type=radio][value="five"]').checked)throw Error('Running replaced the answer');
  await click('제출');await wait(()=>status('다시 풀어보세요'),'wrong answer remains wrong');
  checked.push('read-only prepared code executes independently of selected answer');
  molipAgent.setVoice(false);await click('해설 재생');await wait(()=>molipAgent.running,'teacher starts');
  await wait(()=>!molipAgent.running&&!button('해설 재생').disabled,'teacher ends');
  await wait(()=>molipCodeEditors.getValue()==='console.log(3);'&&document.querySelector('input[type=radio][value="five"]')?.checked,'student example and choice restored');
  await click('제출');await wait(()=>status('다시 풀어보세요'),'teacher did not pass student');
  checked.push('teacher can edit and run the example, then restores learner answer without granting success');
  await click('초기화');await wait(()=>document.querySelector('.answer-state-bridge')?.value===''&&molipCodeEditors.getValue()==='console.log(3);','reset example and answer');
  await choose('three');await click('제출');await wait(()=>status('통과했어요'),'correct answer');
  checked.push('reset restores both inputs and only a correct submission grants success');
  await click('다음 문제 →');await wait(()=>document.querySelectorAll('[data-answer-field]').length===2,'separate state cells');
  const fill=async(id,value)=>{const field=document.querySelector(`[data-answer-field="${id}"]`);field.value=value;field.dispatchEvent(new Event('input',{bubbles:true}));await wait(()=>JSON.parse(document.querySelector('.answer-state-bridge').value||'{}')[id]===value,'state cell acknowledged');};
  await fill('before','3');await fill('after','2');await click('제출');await wait(()=>status('다시 풀어보세요'),'reversed states rejected');
  await click('해설 재생');await wait(()=>molipAgent.running,'state cell teacher');await wait(()=>!molipAgent.running&&!button('해설 재생').disabled,'state cell teacher ends');
  await wait(()=>document.querySelector('[data-answer-field="before"]').value==='3'&&document.querySelector('[data-answer-field="after"]').value==='2','state cells restored');
  await fill('before','2');await fill('after','3');await click('제출');await wait(()=>status('통과했어요'),'correct state cells');
  checked.push('two independent state cells are graded by identity and restored after teacher playback');
  await click('다음 문제 →');await wait(()=>molipCodeEditors.getValue()?.includes('console.log(quantity);\nquantity=3;'),'ordered prepared code');
  await click('코드 실행');await wait(()=>output()==='2','print before assign');
  document.querySelector('.answer-order li:last-child button[aria-label="조각 위로"]').click();
  await wait(()=>molipCodeEditors.getValue()?.includes('quantity=3;\nconsole.log(quantity);'),'moving line updates prepared code');
  await click('코드 실행');await wait(()=>output()==='3','assign before print');
  await click('초기화');await wait(()=>molipCodeEditors.getValue()?.includes('console.log(quantity);\nquantity=3;'),'ordered reset');
  await click('제출');await wait(()=>status('다시 풀어보세요'),'reset order remains wrong');
  checked.push('reordering authored statements updates the visible program and real output without executing answer IDs');
  dioxus.send({passed:true,checked,userAgent:navigator.userAgent});
 }catch(error){dioxus.send({passed:false,checked,error:String(error),inputTrace,choiceState:choiceState(),screen:document.body.innerText.slice(0,5000)});}
})();
