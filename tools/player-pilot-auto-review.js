// Native check of 관리자 자동 풀이 in the two-lesson validation course (Bash basics, then Java).
// Phase "student": no push permission. Phase "admin": the pilot reports push permission.
// Run states are read from the control's data attributes and kept in a history written by
// MutationObservers, so a state shown only briefly is never missed even if timers are slowed.
(async()=>{
 const checked=[];const phase=window.mq3AutoReviewPhase;
 const sleep=ms=>new Promise(r=>setTimeout(r,ms));
 const wait=async(test,label,ms=120000)=>{const end=Date.now()+ms;while(!test()){if(Date.now()>end)throw new Error(label);await sleep(30);}};
 const q=s=>document.querySelector(s);
 const ctl=()=>q('.auto-run-control');const data=()=>({...(ctl()?.dataset||{})});
 const state=()=>data().state||'none';const active=()=>['running','paused'].includes(state());
 const button=text=>[...document.querySelectorAll('button')].find(b=>b.textContent.trim()===text);
 const click=async text=>wait(()=>{const c=button(text);if(!c||c.disabled)return false;c.click();return true;},text);
 const navs=()=>[...document.querySelectorAll('.study-navigation [data-step-id]')];
 const nav=number=>navs().find(b=>b.textContent.includes(`문제 ${number} · `));
 const solved=number=>nav(number)?.dataset.completed==='true';
 const title=()=>q('.problem-pane h2')?.textContent||'';
 const lesson=()=>q('.repository-study .repository-header h1')?.textContent||'';
 const ready=async label=>wait(()=>q('.repository-task')?.dataset.gitReady==='true'&&/\$\s*$/.test(mq3GitTerminal.text()),label);
 const open=async number=>{nav(number).click();await wait(()=>nav(number)?.getAttribute('aria-current')==='step','step '+number+' selected');await ready('step '+number+' terminal');};
 const key=init=>window.dispatchEvent(new KeyboardEvent('keydown',{bubbles:true,cancelable:true,...init}));
 const chord=()=>key({key:'A',code:'KeyA',ctrlKey:true,altKey:true,shiftKey:true});
 const toasts=[];const toast=window.molipToast;window.molipToast=(text,...rest)=>{toasts.push(String(text));return toast?.(text,...rest);};
 let token=0;
 const control=async(message,ack)=>{const id=++token;dioxus.send({...message,token:id});await wait(()=>window[ack]===id,message.control);};
 const reviewer=value=>control({control:'reviewer',value},'mq3ReviewerToken');
 const capture=async name=>{await control({control:'capture',name},'mq3CaptureToken');if(!window.mq3CaptureOk)throw new Error('capture '+name);};
 const resize=async(width,height)=>{const fits=()=>Math.abs(innerWidth-width)<40&&Math.abs(innerHeight-height)<120;let asked=0;
   await wait(()=>{if(fits())return true;if(Date.now()-asked>1500){asked=Date.now();dioxus.send({control:'resize',width,height});}return false;},`${width}x${height}`);await sleep(400);};
 // History of every run state and every ✓, with time, from DOM mutations (not polling).
 const t0=performance.now();const seen=[];const passedIds=new Set();let lastRow='';
 const note=()=>{const d=data();const row=JSON.stringify([d.state,d.stage,d.step,d.lesson,d.passed,d.reason]);if(row!==lastRow){lastRow=row;seen.push({t:Math.round(performance.now()-t0),...d,title:lesson().slice(0,8)});if(seen.length>600)seen.shift();}
   for(const b of navs())if(b.dataset.completed==='true')passedIds.add(b.dataset.stepId);};
 new MutationObserver(note).observe(document.body,{subtree:true,childList:true,attributes:true,attributeFilter:['data-state','data-stage','data-step','data-lesson','data-passed','data-completed']});
 // Only what happened since the current phase began counts.
 let since=0;const saw=test=>seen.slice(since).some(test);
 // Geometry that must not change when a run starts or stops.
 const layout=()=>{const r=e=>{const b=e?.getBoundingClientRect();return b?[Math.round(b.top),Math.round(b.height),Math.round(b.left),Math.round(b.width)]:null;};
   return JSON.stringify({header:r(q('.repository-study>.repository-header')),slot:r(q('.auto-run-slot')),nav:r(q('.study-navigation')),task:r(q('.repository-task')),problem:r(q('.problem-pane')),controls:r(q('.explanation-controls')),start:r(q('#auto-run-start')),coding:r(q('.coding-pane'))});};
 const visible=e=>{const b=e.getBoundingClientRect();return b.width>0&&e.checkVisibility({visibilityProperty:true,opacityProperty:true});};
 // The header's controls that are cut off or overlap, as a comparable list.
 const toolbarProblems=()=>{const header=q('.repository-study>.repository-header');const items=[...header.querySelectorAll('button,summary,a')].filter(visible);const out=[];
   if(header.scrollWidth>header.clientWidth+1)out.push('overflow');
   for(const e of items){const b=e.getBoundingClientRect();if(b.right>innerWidth+1||b.left<-1)out.push('cut:'+(e.getAttribute('aria-label')||e.textContent.trim()));
     for(const o of items){if(o===e||o.contains(e)||e.contains(o))continue;const c=o.getBoundingClientRect();if(b.left<c.right-1&&b.right>c.left+1&&b.top<c.bottom-1&&b.bottom>c.top+1)out.push('overlap:'+e.textContent.trim()+'/'+o.textContent.trim());}}
   return [...new Set(out)].sort().join('|');};
 // Every header item's width and the space left for the title: reported with any failure.
 const headerWidths=()=>{const header=q('.repository-study>.repository-header');const items=[...header.children].flatMap(e=>e.classList.contains('repository-tools')?[...e.children]:[e]);
   return {width:header.clientWidth,scroll:header.scrollWidth,title:Math.round(header.querySelector('h1').getBoundingClientRect().width),items:items.map(e=>[(e.className||e.tagName).toString().slice(0,24),Math.round(e.getBoundingClientRect().width)])};};
 const widths={};
 const toolbarFits=label=>{const header=q('.repository-study>.repository-header');widths[label]=headerWidths();if(header.scrollWidth>header.clientWidth+1)throw new Error(label+': header overflows '+JSON.stringify(widths[label]));
   for(const e of header.querySelectorAll('button,summary,.auto-run-control')){const b=e.getBoundingClientRect();if(b.width&&(b.right>innerWidth+1||b.left<-1))throw new Error(label+': control cut off: '+(e.getAttribute('aria-label')||e.textContent.trim())+' '+JSON.stringify(widths[label]));}
   const c=ctl()?.getBoundingClientRect();for(const e of header.querySelectorAll('button,summary')){if(ctl()?.contains(e))continue;const b=e.getBoundingClientRect();if(c&&b.width&&b.left<c.right-1&&b.right>c.left+1&&b.top<c.bottom-1&&b.bottom>c.top+1)throw new Error(label+': overlaps '+e.textContent.trim());}};
 try{
  await wait(()=>document.querySelectorAll('.lesson-card').length===2,'two-lesson validation course');
  const cards=[...document.querySelectorAll('.lesson-card')];
  if(!cards[0].textContent.includes('Bash')||!cards[1].textContent.includes('자바'))throw new Error('course order is Bash, then Java');
  await wait(()=>{const b=cards[0].querySelector('button.primary');if(!b||b.disabled)return false;b.click();return true;},'open Bash');
  await wait(()=>navs().length===23,'Bash lesson opened');
  const bashIds=navs().map(b=>b.dataset.stepId);
  if(phase==='student'){
   await sleep(1500);
   if(ctl())throw new Error('a learner without push permission sees the run control');
   chord();await sleep(300);
   if(!toasts.some(t=>t.includes('관리자 계정에서만')))throw new Error('the chord explains it is for administrators');
   if(molipAutoRun.state.active||q('#auto-run-start'))throw new Error('a learner started a run');
   checked.push('without push permission: no run controls, the chord only explains, nothing runs');
   await open(1);
   const before=mq3GitTerminal.text();mq3GitTerminal.command('pwd');await wait(()=>mq3GitTerminal.text()!==before&&/\$\s*$/.test(mq3GitTerminal.text()),'pwd');
   await click('제출');await wait(()=>q('.result-pane')?.dataset.feedback==='passed','manual pwd passes');
   await click('여기 머물기');
   checked.push('the learner solves step 1 by hand as before');
   dioxus.send({passed:true,checked});return;
  }
  // A clip of the neural voice that advances by playbackRate like <audio>: narration length
  // follows the speed setting, including a change while a sentence plays.
  molipVoice.setName('ko-KR-SunHiNeural');molipVoice.synthesize=async text=>'clip:'+text;
  window.clips=[];
  window.Audio=class{constructor(url){this.url=url;this.playbackRate=1;this.position=0;this.length=Math.min(1400,String(url).length*14);this.rates=[];clips.push(this);}
   play(){clearInterval(this.timer);this.started??=performance.now();this.timer=setInterval(()=>{this.rates.push(this.playbackRate);this.position+=20*this.playbackRate;if(this.position>=this.length){clearInterval(this.timer);this.ended=performance.now();this.onended?.();}},20);return Promise.resolve();}
   pause(){clearInterval(this.timer);}};
  molipVoice.setRate(2);
  await wait(()=>q('#auto-run-start')&&!q('#auto-run-start').disabled,'administrator sees the start button');
  if(!q('#auto-run-start').title.includes('Ctrl+Alt+Shift+A')||!q('.explanation-controls #auto-run-start'))throw new Error('the start button sits in the narration controls and names the chord');
  if(ctl())throw new Error('no run control in the header before a run');
  if(!solved(1))throw new Error('the learner record of step 1 is shown');
  // The control sits in the existing tool row at every width; no row is added.
  // Idle adds nothing to the header; its state at each width is recorded as the baseline.
  const baseline={};
  for(const [w,h] of [[1280,800],[900,800],[640,800],[480,800]]){await resize(w,h);widths[`${w}px idle`]=headerWidths();baseline[w]=toolbarProblems();await capture(`idle-${w}`);}
  await resize(1280,800);
  checked.push('idle: no run control in the header; header problems by width (pre-existing): '+JSON.stringify(baseline));

  // 1. Permission is read again before the next lesson opens.
  await open(23);
  const idle=layout();
  chord();await wait(active,'run starts at step 23');
  await wait(()=>data().stage==='해설 재생','step 23 narrates');
  if(layout()!==idle)throw new Error('starting a run moved the lesson: '+idle+' -> '+layout());
  if(toolbarProblems()!==baseline[1280])throw new Error('running at 1280px: '+toolbarProblems()+' vs '+baseline[1280]);
  if(!q('.auto-run-slot .auto-run-control #auto-run-stop')||!visible(q('#auto-run-stop')))throw new Error('the stop button is visible in the header');
  await capture('running-1280');
  await reviewer(false);
  await wait(()=>state()==='stopped','run stops at the lesson change',240000);
  const stopReason=data().reason;
  if(!stopReason.includes('편집 권한'))throw new Error('stop reason names the permission: '+stopReason);
  if(!lesson().includes('Bash')||!solved(23))throw new Error('step 23 was really solved and the Java lesson did not open');
  if(layout()!==idle)throw new Error('stopping moved the lesson');
  q('.auto-run-details summary').click();await wait(()=>q('.auto-run-details[open] .auto-run-menu'),'stop details open on request');
  if(layout()!==idle)throw new Error('opening the stop details moved the lesson');
  await capture('stopped-details-1280');
  q('.auto-run-dismiss').click();await wait(()=>!ctl()&&visible(q('.lesson-share')),'closing the details returns the share button');
  if(layout()!==idle)throw new Error('dismissing moved the lesson');
  checked.push('starting, stopping, the stop details and closing them keep header, steps and task exactly in place; reason: '+stopReason);
  await reviewer(true);

  // 2. From step 22 (unsolved) through 23 (solved before) into Java, until Esc. The run prepares the
  // Bash workspace once, at its first step (22); solved step 23 is not reset but solved again on the
  // state step 22 really left.
  await open(22);
  if(solved(22))throw new Error('step 22 starts unsolved');
  const step22=bashIds[21],step23=bashIds[22];
  since=seen.length;chord();await wait(active,'run starts at step 22');
  await wait(()=>data().stage==='해설 재생'&&data().step===step22&&clips.some(c=>c.started&&!c.ended),'narration plays');
  const playing=clips.filter(c=>c.started&&!c.ended).sort((a,b)=>b.started-a.started)[0];
  key({key:' ',code:'Space'});
  await wait(()=>state()==='paused'&&molipAgent.paused,'Space pauses');
  const held=playing.position;const heldData=JSON.stringify(data());const heldClips=clips.length;await sleep(900);
  if(playing.position!==held||JSON.stringify(data())!==heldData||clips.length!==heldClips)throw new Error('pause holds the voice and the run: '+JSON.stringify({held,now:playing.position,ended:!!playing.ended,heldClips,clips:clips.length,heldData,now:data(),paused:molipAgent.paused}));
  key({key:' ',code:'Space'});await wait(()=>state()==='running','Space resumes');
  molipVoice.setRate(1.75);
  checked.push('Space pauses the voice and the run for 0.9s, Space resumes');
  await wait(()=>saw(r=>r.step===step23),'run moves from step 22 to step 23',240000);
  if(!passedIds.has(step22))throw new Error('step 22 was marked solved before the run moved on');
  await wait(()=>saw(r=>r.step===step23&&r.stage==='채점')||['stopped','failed'].includes(state()),'solved step 23 is graded again on the state step 22 left',240000);
  if(!saw(r=>r.step===step22&&r.stage==='이 문제의 시작 상태로 초기화'))throw new Error('the run prepares the Bash workspace at its first step (22)');
  if(saw(r=>r.step===step23&&r.stage==='이 문제의 시작 상태로 초기화'))throw new Error('solved step 23 was reset; the run keeps the state step 22 left');
  await wait(()=>lesson().includes('자바')&&saw(r=>r.lesson&&r.lesson!==seen.find(x=>x.step===step22)?.lesson),'run opens the Java lesson',300000);
  const javaIds=navs().map(b=>b.dataset.stepId);
  if(Number(seen.filter(r=>r.lesson===seen.find(x=>x.step===step23)?.lesson).pop()?.passed)<2)throw new Error('steps 22 and 23 both passed in this run before the Java lesson: '+JSON.stringify(seen.slice(-8)));
  if(saw(r=>r.step===step23&&r.stage==='이 문제의 시작 상태로 초기화'))throw new Error('solved step 23 was reset later in the run');
  checked.push('the run prepared the Bash workspace once at step 22, solved it, solved the already solved step 23 again on that state without a reset, then opened the next lesson itself');
  await wait(()=>passedIds.has(javaIds[0])&&data().step===javaIds[1]&&data().stage==='해설 재생','Java step 1 passes and step 2 narrates',300000);
  const rates=[...new Set(clips.flatMap(c=>c.rates))];
  if(!rates.includes(2)||!rates.includes(1.75))throw new Error('voice rates seen: '+rates);
  const beforeEsc=clips.length;
  const escAt=performance.now();key({key:'Escape',code:'Escape'});
  await wait(()=>!active(),'Esc stops',1500);
  const stoppedIn=performance.now()-escAt;
  await sleep(4000);
  if(passedIds.has(javaIds[1])||molipAgent.running||clips.slice(beforeEsc).some(c=>c.started>escAt+300))throw new Error('something ran after Esc');
  if(!data().reason.includes('Esc'))throw new Error('Esc reason: '+data().reason);
  checked.push(`Esc stopped the run in ${Math.round(stoppedIn)}ms; nothing ran or passed afterwards`);

  // 3. Narrow window: a run at 640px keeps the layout; picking a step by hand ends it.
  await resize(640,800);
  const narrow=layout();
  chord();await wait(active,'run starts at Java step 2');
  await wait(()=>data().stage==='해설 재생','Java step 2 narrates');
  if(layout()!==narrow)throw new Error('starting a run at 640px moved the lesson: '+narrow+' -> '+layout());
  if(toolbarProblems()!==baseline[640])throw new Error('running at 640px: '+toolbarProblems()+' vs '+baseline[640]);
  await capture('running-640');
  nav(4).click();
  await wait(()=>state()==='stopped'&&data().reason.includes('직접 선택'),'manual step choice stops the run');
  await wait(()=>nav(4).getAttribute('aria-current')==='step','step 4 is on screen');
  await sleep(2000);if(passedIds.has(javaIds[1])||passedIds.has(javaIds[3]))throw new Error('nothing passes after a manual move');
  checked.push('at 640px the run kept the layout and fit the tool row; choosing a step by hand stopped it');
  await resize(1280,800);

  // 4. The last step of the course ends the run.
  await open(8);
  chord();await wait(active,'run starts at the last Java step');
  await wait(()=>state()==='finished',"course end",300000);
  if(!data().reason.includes('마지막 수업')||!solved(8))throw new Error('course end: '+data().reason);
  checked.push('the last step passed and the run finished at the end of the course');
  dioxus.send({passed:true,checked,widths,rates,clips:clips.length,seen:seen.slice(-80)});
 }catch(error){dioxus.send({passed:false,checked,seen:seen.slice(-200),error:String(error),data:data(),lesson:lesson(),title:title(),screen:document.body.innerText.slice(-3000),student:window.mq3GitTerminal?.text?.().slice(-1200)});}
})();
