(async()=>{
 const checked=[];const wait=async(test,label)=>{const end=Date.now()+60000;while(!test()){if(Date.now()>end)throw new Error(label);await new Promise(r=>setTimeout(r,30));}};
 const button=text=>[...document.querySelectorAll('button')].find(b=>b.textContent.trim()===text);
 const click=async text=>{await wait(()=>button(text)&&!button(text).disabled,text);button(text).click();};
 try{
  await wait(()=>button('학습 시작')&&!button('학습 시작').disabled,'initial course ready');
  let lastSwitch=0;
  await wait(()=>{
   if(document.querySelector('.lesson-card')?.textContent.includes('bash-basics-1'))return true;
   if(Date.now()-lastSwitch>1000){button('버전 부')?.click();lastSwitch=Date.now();}
   return false;
  },'Bash lesson card');await click('학습 시작');
  await click('문제 2 · 파일 목록을 확인하세요');await wait(()=>document.querySelector('.problem-pane h2')?.textContent==='파일 목록을 확인하세요','ls task mounted');await wait(()=>document.querySelector('.repository-task')?.dataset.gitReady==='true','Bash terminal ready');
  if(!document.body.textContent.includes('Bash 터미널')||!document.querySelector('.problem-pane ol'))throw new Error('Bash label or ordered tasks missing');
  molipAgent.setVoice(false);await click('해설 재생');
  await wait(()=>window.mq3GitDemoTerminal?.text().includes('$ ls'),'first Bash ls is demonstrated');
  await wait(()=>document.querySelector('.repository-task')?.dataset.narrating==='false','ls explanation finishes');
  checked.push('Bash ls and ordered task list render in the native WebView');
  document.querySelector('[aria-label="학습 정보"]').click();await wait(()=>document.querySelector('#lesson-info-dialog')?.open,'learning info dialog opens');
  window.overviewHeld=null;molipVoice.synthesize=async text=>text;
  window.Audio=class{constructor(text){this.text=text;}play(){overviewHeld=this;return Promise.resolve();}pause(){}};
  await click('목표와 학습 방법 해설');
  await wait(()=>overviewHeld&&document.querySelector('#lesson-goal-0.overview-speaking'),'overview speaks and highlights first goal');
  const highlighted=document.querySelector('#lesson-goal-0');if(getComputedStyle(highlighted).outlineStyle==='none')throw new Error('overview highlight is not visible');
  await click('닫기');await wait(()=>!molipAgent.running&&!document.querySelector('.overview-speaking'),'closing info stops speech');
  checked.push('Learning info overview highlights the spoken objective and closing cancels speech');
  dioxus.send({passed:true,checked});
 }catch(error){dioxus.send({passed:false,checked,error:String(error),screen:document.body.innerText.slice(-5000),demo:window.mq3GitDemoTerminal?.text(),student:window.mq3GitTerminal?.text()});}
})();
