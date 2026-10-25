// Native check of the reported Vim narration (vim-basics step 1, 입력 모드로 들어가세요): for every caption
// the narration shows, where the caption and the spotlight are, which text is highlighted (CSS.highlights
// 'narration-text'), and every element the target selector matches. Measured on the real page.
(async()=>{
 const checked=[],problems=[],rows=[];
 const log=line=>dioxus.send({control:'log',t:performance.now(),line:String(line)});
 const sleep=ms=>new Promise(r=>setTimeout(r,ms));
 const wait=async(test,label,ms=60000)=>{const end=Date.now()+ms;while(!test()){if(Date.now()>end){log('TIMEOUT '+label);throw Error('timed out: '+label);}await sleep(30);}};
 const q=s=>document.querySelector(s);
 const button=text=>[...document.querySelectorAll('button')].find(b=>b.textContent.trim()===text&&b.getClientRects().length>0);
 const click=async text=>{await wait(()=>button(text)&&!button(text).disabled,text);button(text).click();};
 const box=e=>{if(!e)return null;const r=e.getBoundingClientRect();return [Math.round(r.left),Math.round(r.top),Math.round(r.width),Math.round(r.height)];};
 const overlap=(a,b)=>a&&b&&a[0]<b[0]+b[2]&&b[0]<a[0]+a[2]&&a[1]<b[1]+b[3]&&b[1]<a[1]+a[3];
 const highlighted=()=>{const h=globalThis.CSS?.highlights?.get('narration-text');if(!h)return null;return [...h].map(r=>r.toString()).join(' | ');};
 const sample=()=>{const cap=q('.agent-caption'),spot=q('.agent-spotlight');
  const header=box(q('.repository-study>.repository-header')),tabs=box(q('.study-navigation'));
  const panels=[...document.querySelectorAll('.vim-live-panel')].map(p=>({box:box(p),visible:p.checkVisibility?.()??null,inDemo:!!p.closest('#git-demo-terminal, .git-demo, [data-demo="true"]'),passed:p.dataset.vimPassed}));
  return {t:Math.round(performance.now()),caption:cap&&!cap.hidden?cap.textContent:null,captionBox:cap&&!cap.hidden?box(cap):null,spot:spot&&!spot.hidden?box(spot):null,
   highlight:highlighted(),demo:box(q('#git-demo-terminal')),demoVisible:q('#git-demo-terminal')?.checkVisibility?.()??null,panels,
   overHeader:cap&&!cap.hidden&&(overlap(box(cap),header)||overlap(box(cap),tabs))};};
 let last='';const watch=()=>{const s=sample();const key=JSON.stringify([s.caption,s.captionBox,s.spot,s.highlight,s.panels.length]);if(key!==last){last=key;rows.push(s);}};
 try{
  await wait(()=>window.molipVoice&&window.molipAgent,'page scripts');
  // Clips that advance like <audio> at the chosen speed, so the run takes seconds, not minutes.
  molipVoice.setName('ko-KR-SunHiNeural');molipVoice.synthesize=async text=>'clip:'+text;
  window.Audio=class{constructor(url){this.url=url;this.playbackRate=1;this.position=0;this.length=Math.min(900,String(url).length*10);}
   play(){clearInterval(this.timer);this.timer=setInterval(()=>{this.position+=20*this.playbackRate;if(this.position>=this.length){clearInterval(this.timer);this.onended?.();}},20);return Promise.resolve();}
   pause(){clearInterval(this.timer);}};
  await wait(()=>q('.lesson-card')?.textContent.includes('pilot-a'),'initial fixture');
  await click('버전 브');await wait(()=>q('.lesson-card')?.textContent.includes('vim-basics'),'Vim fixture');
  await click('학습 시작');
  await wait(()=>q('.repository-task')?.dataset.gitReady==='true','learner Vim ready');
  log('Vim step open: '+q('.repository-task h2, .problem-pane h2')?.textContent);
  const timer=setInterval(watch,16);
  await click('해설 재생');
  await wait(()=>molipAgent.running,'narration starts',20000);
  await wait(()=>!molipAgent.running,'narration ends',120000);
  await sleep(500);watch();clearInterval(timer);
  log('rows '+rows.length);
  // What a person should see per sentence (the published targets of this step).
  const final=rows.filter(r=>r.caption&&r.caption.startsWith('입력 모드 항목이 완료됐어요'));
  const terminal=rows.filter(r=>r.caption&&/해설 편집기|i를 눌러요|INSERT/.test(r.caption));
  for(const r of terminal.concat(final))if(r.highlight)problems.push('old text still highlighted at «'+r.caption.slice(0,24)+'»: '+r.highlight);
  for(const r of rows)if(r.overHeader)problems.push('caption covers the header/step tabs at «'+(r.caption||'').slice(0,24)+'» '+JSON.stringify(r.captionBox));
  if(!final.length)problems.push('final sentence never shown');
  for(const r of final){const shown=r.panels.filter(p=>p.visible);if(!r.spot||!shown.some(p=>overlap(p.box,r.spot)))problems.push('final sentence spotlight is not on a visible live panel: '+JSON.stringify({spot:r.spot,panels:r.panels}));}
  const after=sample();if(after.highlight||after.spot||after.caption)problems.push('after the end something stays: '+JSON.stringify(after));
  checked.push('narration measured');
  dioxus.send({passed:problems.length===0,problems,checked,rows,after});
 }catch(error){dioxus.send({passed:false,problems,checked,rows,error:String(error),screen:document.body.innerText.slice(-3000)});}
})();
