(async()=>{
 const checked=[];
 const wait=async(predicate,label)=>{const end=Date.now()+45000;while(Date.now()<end){if(predicate())return;await new Promise(r=>setTimeout(r,40));}throw Error(`Timed out: ${label}`)};
 const button=text=>[...document.querySelectorAll('button')].find(b=>b.textContent.trim()===text);
 const click=async text=>{await wait(()=>button(text)&&!button(text).disabled,text);button(text).click()};
 try{
  await wait(()=>document.querySelector('.lesson-card')?.textContent.includes('pilot-a'),'initial installation');
  await click('버전 2');
  await wait(()=>document.querySelector('.lesson-card')?.textContent.includes('aice-plots-1'),'plots installed');
  await wait(()=>document.querySelector('.lesson-progress')?.textContent.includes('0% 완료'),'catalog progress');
  if(button('복습모드 시작')||button('풀모드 시작'))throw Error('Old mode entry remains');
  checked.push('one learning entry and visible percentage');
  await click('학습 시작');
  await wait(()=>document.querySelector('.cm-content')&&document.querySelectorAll('.study-navigation button').length===10,'plots lesson opened');
  await new Promise(r=>setTimeout(r,200));
  for(const selector of ['.repository-header','.cm-editor','.answer-interaction']){
   const r=document.querySelector(selector).getBoundingClientRect();
   if(r.width<=0||r.height<=0||r.right>innerWidth+1||r.left<0)throw Error(`${selector}: ${JSON.stringify(r.toJSON())}`);
  }
  checked.push('aice-plots-1 renders header, code and choices within viewport');
  if(!document.querySelector('.repository-header .app-window-controls')||!document.querySelector('.repository-header .content-update-controls'))throw Error('Settings are outside the shared row');
  await wait(()=>document.getElementById('lesson-info-dialog'),'information dialog mounted');
  document.querySelector('.lesson-info-trigger').click();
  await wait(()=>document.getElementById('lesson-info-dialog').open,'learning information opens');
  if(!document.querySelector('.lesson-info-dialog .lesson-outline')?.textContent.includes('수업 목표'))throw Error('Learning goals missing');
  document.getElementById('lesson-info-dialog').dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}));
  await wait(()=>!document.getElementById('lesson-info-dialog').open,'Escape closes information');
  document.querySelector('.lesson-info-trigger').click();
  await wait(()=>document.getElementById('lesson-info-dialog').open,'information reopens');
  document.querySelector('.lesson-info-dialog>header>button').click();
  await wait(()=>!document.getElementById('lesson-info-dialog').open,'close button');
  checked.push('single toolbar and learning information popup with Escape and close button');
  await click('정답과 풀이 보기');
  await wait(()=>document.querySelector('.explanation-info summary'),'explanation record');
  document.querySelector('.explanation-info summary').click();
  if(!document.querySelector('.explanation-info').textContent.includes('풀이 전에 해설을 확인했어요.'))throw Error('Explanation information contains only an icon');
  for(const control of document.querySelectorAll('.explanation-controls>button,.explanation-controls select'))if(control.getBoundingClientRect().height>34)throw Error('Explanation controls are too tall');
  checked.push('explanation information displays readable record text');
  for(const nav of [...document.querySelectorAll('.study-navigation button')]){
   nav.click();await new Promise(r=>setTimeout(r,120));
   if(!document.querySelector('.problem-pane h2')?.textContent.trim())throw Error('Empty task');
  }
  checked.push('all ten tasks open');
  await click('← 코스 수업 목록');await click('버전 a');
  await wait(()=>document.querySelector('.lesson-card')?.textContent.includes('pilot-a'),'progress fixture');
  await click('학습 시작');
  await wait(()=>window.molipCodeEditors?.getValue()?.includes('console.log'),'first editor');
  const solve=async value=>{
   molipCodeEditors.setValue(`console.log(${value});`);
   await new Promise(r=>setTimeout(r,100));await click('제출');
   await wait(()=>document.querySelector('[role=dialog]'),'passed dialog');
  };
  await solve(3);await click('여기 머물기');await click('← 코스 수업 목록');
  await wait(()=>document.querySelector('.lesson-progress')?.textContent.includes('50% 완료'),'half complete in catalog');
  await click('학습 시작');
  await wait(()=>document.querySelector('.study-navigation .selected')?.textContent.includes('문제 2'),'resume first unfinished task');
  await solve(5);await click('수업 목록으로');
  await wait(()=>document.querySelector('.lesson-progress')?.textContent.includes('100% 완료'),'fully complete in catalog');
  checked.push('catalog 0 to 50 to 100 percent, passed dialog and resume unfinished task');
  // Exercise the actual custom protocol and real audio on the platform's native WebView.
  const started=Date.now();
  const clip=await molipVoice.synthesize(`맥 음성 연결을 확인해요. ${Date.now()}`);
  const voice={clip:!!clip,stats:{...molipVoice.stats},elapsed:Date.now()-started};
  if(!clip)throw Error(`Edge voice failed: ${JSON.stringify(voice)}`);
  checked.push('native WebView downloads Edge audio');
  dioxus.send({passed:true,checked,voice,userAgent:navigator.userAgent});
 }catch(error){dioxus.send({passed:false,checked,error:String(error),screen:document.body.innerText.slice(0,3000),voice:window.molipVoice?.stats,userAgent:navigator.userAgent})}
})();
