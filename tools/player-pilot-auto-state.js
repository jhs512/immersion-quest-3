// Native check (administrator, validation course Bash → Java) of two things a person reported:
//  A. The narration speed chosen in the select stays chosen: after the next step, a new render,
//     a new clip and the next lesson the select, molipVoice.rate, localStorage and the clip's
//     playbackRate agree; the speeds go up to 3x and change while a clip plays.
//  B. 관리자 자동 풀이 initializes a practice workspace once per run, then keeps the real
//     cumulative state (files, folder, current directory) from step to step, also when the
//     steps were solved before; every step still passes the real grader and is recorded.
// Everything is measured and returned as `report`; `problems` lists what disagrees.
// window.mq3AutoStatePart ('rate', 'runs' or unset = both) runs one half, for a quick red/green loop.
// Every phase is logged to auto-state.log (control "log"), so a stuck run shows where it stopped.
(async()=>{
 const checked=[],problems=[],report={rates:[],runs:[]};
 const part=window.mq3AutoStatePart||'all';
 const log=line=>dioxus.send({control:'log',t:performance.now(),line:String(line)});
 const sleep=ms=>new Promise(r=>setTimeout(r,ms));
 const wait=async(test,label,ms=90000)=>{const begin=Date.now(),end=begin+ms;while(!test()){if(Date.now()>end){log('TIMEOUT '+label+' after '+ms+' ms; state '+JSON.stringify(data()));throw new Error('timed out: '+label);}await sleep(30);}if(Date.now()-begin>3000)log('waited '+(Date.now()-begin)+' ms: '+label);};
 const q=s=>document.querySelector(s);
 const ctl=()=>q('.auto-run-control');const data=()=>({...(ctl()?.dataset||{})});
 const state=()=>data().state||'none';const active=()=>['running','paused'].includes(state());
 const navs=()=>[...document.querySelectorAll('.study-navigation [data-step-id]')];
 const nav=number=>navs().find(b=>b.textContent.includes(`문제 ${number} · `));
 const lesson=()=>q('.repository-study .repository-header h1')?.textContent||'';
 const ready=async label=>wait(()=>q('.repository-task')?.dataset.gitReady==='true'&&/\$\s*$/.test(mq3GitTerminal.text()),label);
 const open=async number=>{nav(number).click();await wait(()=>nav(number)?.getAttribute('aria-current')==='step','step '+number+' selected');await ready('step '+number+' terminal');};
 const key=init=>window.dispatchEvent(new KeyboardEvent('keydown',{bubbles:true,cancelable:true,...init}));
 const chord=()=>key({key:'A',code:'KeyA',ctrlKey:true,altKey:true,shiftKey:true});
 let token=0;
 const capture=async name=>{const id=++token;dioxus.send({control:'capture',name,token:id});await wait(()=>window.mq3CaptureToken===id,'capture '+name,30000);};
 // Stage history from DOM mutations, so a stage shown briefly is never missed.
 // A pass is the run's pass counter (data-passed) going up: it counts real grader passes the run
 // saved, and belongs to the step that was current just before (the short "통과 기록 저장" stage is
 // often replaced within one render, so the stage name alone misses passes).
 const seen=[];let lastRow='';let lastPassed=0,lastStep=null;
 const note=()=>{const d=data();const row=JSON.stringify([d.state,d.stage,d.step,d.lesson,d.passed,d.initialized]);if(row===lastRow)return;lastRow=row;
  const count=Number(d.passed||0);let pass=null;
  if(count>lastPassed&&lastStep)pass=lastStep;
  lastPassed=count;lastStep=d.step||lastStep;
  seen.push({t:Math.round(performance.now()),state:d.state,stage:d.stage,step:d.step,lesson:lesson().slice(0,12),passed:d.passed,initialized:d.initialized,pass});};
 new MutationObserver(note).observe(document.body,{subtree:true,childList:true,attributes:true,attributeFilter:['data-state','data-stage','data-step','data-lesson','data-passed','data-initialized','data-completed']});
 // The neural voice is replaced by a clip that advances by playbackRate like <audio>, so clip
 // length follows the speed (the request path itself is covered by player_speech_voices_native).
 // Installed after the page scripts load (startStage below): this eval can run before them.
 window.clips=[];
 const FakeAudio=class{constructor(url){this.url=url;this.playbackRate=1;this.position=0;this.length=Math.min(900,String(url).length*10);this.rates=[];clips.push(this);}
  play(){clearInterval(this.timer);this.started??=performance.now();this.timer=setInterval(()=>{this.rates.push(this.playbackRate);this.position+=20*this.playbackRate;if(this.position>=this.length){clearInterval(this.timer);this.ended=performance.now();this.onended?.();}},20);return Promise.resolve();}
  pause(){clearInterval(this.timer);}};
 const startStage=async()=>{
  log('script started; molipVoice '+typeof window.molipVoice+', molipAgent '+typeof window.molipAgent);
  await wait(()=>window.molipVoice&&window.molipAgent&&window.molipAutoRun,'page scripts (molipVoice, molipAgent, molipAutoRun)');
  molipVoice.setName('ko-KR-SunHiNeural');molipVoice.synthesize=async text=>'clip:'+text;window.Audio=FakeAudio;
  log('page scripts ready; saved rate '+localStorage.getItem('molip:tts-rate')+', molipVoice.rate '+molipVoice.rate);};
 const select=()=>q('select.repository-narration-rate');
 const rateState=label=>{const s=select();const playing=clips.filter(c=>c.started&&!c.ended).pop();
  const row={label,dom:s?.value??null,shown:s?.selectedOptions?.[0]?.textContent??null,options:s?[...s.options].map(o=>o.value).join(','):null,voice:molipVoice.rate,storage:localStorage.getItem('molip:tts-rate'),selects:document.querySelectorAll('select.repository-narration-rate').length,clip:playing?playing.playbackRate:null};
  report.rates.push(row);return row;};
 const expectRate=(label,rate)=>{const row=rateState(label);const want=String(rate);
  if(row.dom!==want||String(row.voice)!==want||row.storage!==want||(row.clip!==null&&String(row.clip)!==want))problems.push(`${label}: want ${want} got ${JSON.stringify(row)}`);return row;};
 // Choose a speed the way a person does: pick the option in the select.
 const choose=async rate=>{const s=select();if(![...s.options].some(o=>o.value===String(rate))){problems.push(`no ${rate}x option: ${[...s.options].map(o=>o.value)}`);return false;}
  s.value=String(rate);s.dispatchEvent(new Event('input',{bubbles:true}));s.dispatchEvent(new Event('change',{bubbles:true}));await sleep(400);return true;};
 const resetsIn=from=>seen.slice(from).filter((r,i,a)=>r.stage==='이 문제의 시작 상태로 초기화'&&!(i&&a[i-1].stage===r.stage&&a[i-1].step===r.step)).map(r=>r.step);
 const passesIn=from=>[...new Set(seen.slice(from).filter(r=>r.pass).map(r=>r.pass))];
 // Output of one command in the real shell, read between printed markers (the terminal text is a
 // screen buffer that rewraps, so slicing it at the old length is not reliable). The typed line shows
 // "@@""S", only the output shows @@S.
 let mark=0;
 const shell=async command=>{const id=++mark,start=`@@S${id}@@`,end=`@@E${id}@@`;
  mq3GitTerminal.command(`echo "@@""S${id}@@"; ${command}; echo "@@""E${id}@@"`);
  await wait(()=>{const t=mq3GitTerminal.text();return t.includes(end)&&/\$\s*$/.test(t);},command,45000);
  const t=mq3GitTerminal.text();return t.slice(t.lastIndexOf(start)+start.length,t.lastIndexOf(end)).trim();};
 const workspace=async()=>({ready:await ready('terminal after Esc').then(()=>true),pwd:await shell('pwd'),ls:await shell('ls -A'),notes:await shell('cat notes/memo.txt'),memo:await shell('cat memo.txt'),git:await shell('git status --short 2>&1 | head -5')});
 // Run from step `from` until steps `until` have passed (by the run), then Esc.
 const runUntil=async(label,from,until)=>{
  await open(from);const start=seen.length;lastPassed=0;lastStep=null;chord();await wait(active,label+' starts');
  const ids=until.map(n=>nav(n)?.dataset.stepId).filter(Boolean);
  await wait(()=>until.every((n,i)=>passesIn(start).includes(ids[i]??'?'))||['stopped','failed','finished'].includes(state()),'run '+label,300000);
  key({key:'Escape',code:'Escape'});await wait(()=>!active(),label+' stops on Esc',3000);
  const run={label,resets:resetsIn(start),passed:passesIn(start),stopped:data().reason,initialized:data().initialized??null,steps:[...new Set(seen.slice(start).map(r=>r.step).filter(Boolean))]};
  report.runs.push(run);log('run '+JSON.stringify(run));return run;};
 try{
  await startStage();
  await wait(()=>document.querySelectorAll('.lesson-card').length===2,'two-lesson validation course');
  const cards=[...document.querySelectorAll('.lesson-card')];
  await wait(()=>{const b=cards[0].querySelector('button.primary');if(!b||b.disabled)return false;b.click();return true;},'open Bash');
  await wait(()=>navs().length===23,'Bash lesson opened');
  log('Bash lesson open, part '+part);
  await open(7);
  if(part!=='runs'){
  // A. The chosen speed after the next step, a new render and a new clip.
  // First use (this run's own WebView profile): the default shows, and nothing is saved yet.
  {const row=rateState('first use (no choice yet)');if(row.dom!=='1.5'||row.voice!==1.5||row.storage!==null)problems.push('first use: want 1.5 shown, 1.5 used, nothing saved; got '+JSON.stringify(row));}
  await choose(2);expectRate('chose 2x',2);
  await open(8);await sleep(500);expectRate('next step after 2x',2);
  await capture('rate-next-step');
  await open(7);await sleep(300);expectRate('back to step 7 (new render)',2);
  if(await choose(3)){expectRate('chose 3x',3);await open(8);await sleep(500);expectRate('next step after 3x',3);}
  await capture('rate-3x-next-step');
  checked.push('speed choice across steps measured');
  log('rates '+JSON.stringify(report.rates));
  }
  if(part!=='rate'){
  // B1. A fresh run over four cumulative steps: 7 mkdir notes, 8 cd notes, 9 write notes/memo.txt, 10 cd ..
  const first=await runUntil('fresh 7-10',7,[7,8,9,10]);
  const after1=await workspace();
  report.workspaceAfterFirst=after1;
  // data-initialized (the run's own count of prepared workspaces) is absent on builds before it existed.
  if(first.initialized!==null&&first.initialized!=='1')problems.push('fresh run prepared '+first.initialized+' workspaces, want 1');
  if(first.resets.length>1)problems.push('fresh run reset more than once: '+JSON.stringify(first));
  if(first.passed.length<4)problems.push('fresh run did not pass 4 steps: '+JSON.stringify(first));
  if(!after1.notes.includes('폴더 안 메모')||!after1.memo.includes('둘째 줄'))problems.push('cumulative files after fresh run: '+JSON.stringify(after1));
  // B2. The same steps again, now all solved before: still one initialization at most.
  const second=await runUntil('repeat solved 7-10',7,[7,8,9,10]);
  const after2=await workspace();report.workspaceAfterRepeat=after2;
  if(!after2.notes.includes('폴더 안 메모')||!after2.memo.includes('둘째 줄')||/notes\/?$/.test(after2.pwd))problems.push('cumulative files after repeat run: '+JSON.stringify(after2));
  if(second.initialized!==null&&second.initialized!=='1')problems.push('repeat run prepared '+second.initialized+' workspaces, want 1');
  if(second.resets.length>1)problems.push('repeat run reset more than once: '+JSON.stringify(second));
  if(second.passed.length<4)problems.push('repeat run did not pass 4 steps: '+JSON.stringify(second));
  rateState('after runs');
  // B3. From step 22 across the lesson change into Java; speed 2x chosen during the run.
  await open(22);await choose(2);
  const startCross=seen.length;lastPassed=0;lastStep=null;chord();await wait(active,'cross-lesson run starts');
  await wait(()=>lesson().includes('자바'),'run opens the Java lesson',300000);
  await wait(()=>select()&&data().stage==='해설 재생'&&clips.some(c=>c.started&&!c.ended),'Java narration plays',120000);
  expectRate('Java lesson during the run',2);
  await capture('rate-java-lesson');
  await choose(3);expectRate('changed to 3x while Java narrates',3);
  const javaFirst=navs()[0]?.dataset.stepId;
  await wait(()=>passesIn(startCross).includes(javaFirst),'Java step 1 passes',300000);
  key({key:'Escape',code:'Escape'});await wait(()=>!active(),'cross-lesson run stops',3000);
  const cross={label:'22 → 23 → Java 1',resets:resetsIn(startCross),passed:passesIn(startCross),initialized:data().initialized??null};report.runs.push(cross);
  if(cross.initialized!==null&&cross.initialized!=='2')problems.push('cross-lesson run prepared '+cross.initialized+' workspaces, want 2 (Bash, Java)');
  if(cross.resets.length>2)problems.push('cross-lesson run reset more than once per workspace: '+JSON.stringify(cross));
  if(cross.passed.length<3)problems.push('cross-lesson run passes: '+JSON.stringify(cross));
  expectRate('after Esc',3);
  const rates=[...new Set(clips.flatMap(c=>c.rates))];report.clipRates=rates;
  if(!rates.includes(3))problems.push('no clip ever played at 3x: '+rates);
  checked.push('runs measured');
  }
  log('done; problems '+JSON.stringify(problems));
  dioxus.send({passed:problems.length===0,problems,checked,report,seen:seen.slice(-120)});
 }catch(error){log('ERROR '+error);dioxus.send({passed:false,problems,checked,report,error:String(error),data:data(),lesson:lesson(),seen:seen.slice(-120),screen:document.body.innerText.slice(-2000)});}
})();
