(async()=>{
 const checked=[];
 const wait=async(predicate,label)=>{const end=Date.now()+45000;while(Date.now()<end){if(predicate())return;await new Promise(r=>setTimeout(r,40));}throw Error(`Timed out: ${label}`)};
 const button=text=>[...document.querySelectorAll('button')].find(b=>b.textContent.trim()===text);
 const click=async text=>{await wait(()=>button(text)&&!button(text).disabled,text);button(text).click()};
 try{
  await wait(()=>document.querySelector('.lesson-card')?.textContent.includes('pilot-a'),'initial installation');
  await click(`버전 ${mq3LoadingLesson.version}`);
  await wait(()=>document.querySelector('.lesson-card')?.textContent.includes(mq3LoadingLesson.revision),'plots installed');
  await wait(()=>document.querySelector('.lesson-progress')?.textContent.includes('0% 완료'),'catalog progress');
  if(button('복습모드 시작')||button('풀모드 시작'))throw Error('Old mode entry remains');
  checked.push('one learning entry and visible percentage');
  await click('학습 시작');
  await wait(()=>document.querySelector('.cm-content')&&document.querySelectorAll('.study-navigation button').length===11,'plots lesson opened');
  await new Promise(r=>setTimeout(r,200));
  // The plots lesson is now all coding steps: header, task, code editor and its run/grading pane.
  if(document.querySelector('.answer-interaction'))throw Error('The converted coding step still shows answer choices');
  for(const selector of ['.repository-header','.problem-pane','.cm-editor','.result-pane']){
   const r=document.querySelector(selector).getBoundingClientRect();
   if(r.width<=0||r.height<=0||r.right>innerWidth+1||r.left<0)throw Error(`${selector}: ${JSON.stringify(r.toJSON())}`);
  }
  checked.push(`${mq3LoadingLesson.revision} renders header, task, code and result pane within viewport`);
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
  const settings=document.querySelector('.app-update-settings');settings.open=true;
  for(const label of ['환경 진단','환경 설치']){
   const control=button(label);if(!control||control.getBoundingClientRect().height<=0)throw Error(`Environment control missing in app settings: ${label}`);
  }
  settings.open=false;
  checked.push('single toolbar and learning information popup with Escape and close button');
  if(document.querySelector('.solution-toggle')||button('정답과 풀이 보기'))throw Error('Standalone answer reveal remains');
  for(const control of document.querySelectorAll('.explanation-controls>button,.explanation-controls select'))if(control.getBoundingClientRect().height>34)throw Error('Explanation controls are too tall');
  checked.push('narration controls remain without standalone answer reveal');
  for(const nav of [...document.querySelectorAll('.study-navigation button')]){
   nav.click();await new Promise(r=>setTimeout(r,120));
   if(!document.querySelector('.problem-pane h2')?.textContent.trim())throw Error('Empty task');
  }
  checked.push('all eleven tasks open');
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
  await click('버전 k');
  await wait(()=>document.querySelector('.lesson-card')?.textContent.includes('git-first-'),'Git lesson installed');
  await click('학습 시작');
  await wait(()=>document.querySelectorAll('.study-navigation button').length===7,'Git navigation');
  // This lesson shares one real workspace: complete initialization and staging
  // through the same PTY before navigating to the commit step.
  await wait(()=>document.querySelector('.repository-task')?.dataset.gitReady==='true'&&window.mq3GitTerminal,'Git initialization ready');
  const gitRun=async command=>{
   const before=mq3GitTerminal.text();mq3GitTerminal.command(command);
   await wait(()=>mq3GitTerminal.text()!==before&&/\$\s*$/.test(mq3GitTerminal.text()),command);
  };
  await gitRun('git init');await gitRun('echo "첫 메모" > memo.txt');
  document.querySelectorAll('.study-navigation button')[1].click();
  await wait(()=>document.querySelector('.study-navigation .selected')?.textContent.includes('문제 2')&&document.querySelector('.repository-task')?.dataset.gitReady==='true','Git staging ready');
  await gitRun('git add memo.txt');
  document.querySelectorAll('.study-navigation button')[2].click();
  await wait(()=>document.querySelector('.study-navigation .selected')?.textContent.includes('문제 3')&&document.querySelector('.repository-task')?.dataset.gitReady==='true'&&document.querySelector('[aria-label="Git 실습 터미널 입력"]'),'Git commit exercise ready');
  await new Promise(r=>setTimeout(r,500));
  // Feed the same DOM composition path used by the OS IME, including NFD syllables.
  const input=document.querySelector('[aria-label="Git 실습 터미널 입력"]');
  const insert=text=>{input.value+=text;input.dispatchEvent(new InputEvent('input',{bubbles:true,inputType:'insertText',data:text}));};
  insert('git commit -m "');
  await new Promise(r=>setTimeout(r,150));
  for(const syllable of ['첫','기','록']){
   input.dispatchEvent(new CompositionEvent('compositionstart',{bubbles:true,data:''}));
   const text=syllable.normalize('NFD');input.value+=text;
   input.dispatchEvent(new CompositionEvent('compositionupdate',{bubbles:true,data:text}));
   input.dispatchEvent(new InputEvent('input',{bubbles:true,inputType:'insertCompositionText',data:text,isComposing:true}));
   await new Promise(r=>setTimeout(r,20));
   input.dispatchEvent(new CompositionEvent('compositionend',{bubbles:true,data:text}));
   await new Promise(r=>setTimeout(r,150));
   if(syllable==='첫')insert(' ');
  }
  insert('"');mq3GitTerminal.command('');
  await wait(()=>mq3GitTerminal.text().includes('첫 기록'),'Korean commit echoed');
  mq3GitTerminal.command('git log -1 --format=%s');
  await wait(()=>mq3GitTerminal.text().split('\n').some(line=>line.trim()==='첫 기록'),'Git persists composed Korean subject');
  if(mq3GitTerminal.text().includes('The default interactive shell is now zsh'))throw Error('Obsolete shell banner remains');
  checked.push('native WebView NFD composition reaches real Git as NFC Korean');
  dioxus.send({passed:true,checked,voice,userAgent:navigator.userAgent});
 }catch(error){dioxus.send({passed:false,checked,error:String(error),screen:document.body.innerText.slice(0,3000),terminal:window.mq3GitTerminal?.text(),voice:window.molipVoice?.stats,userAgent:navigator.userAgent})}
})();
