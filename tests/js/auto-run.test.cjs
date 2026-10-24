// 관리자 자동 풀이, browser side (assets/layout/auto-run.js) with the real terminal bundle and
// the real narration agent. Speeds are measured on wall time: the run's typing and the narration
// clips follow the saved narration speed, including a change in the middle; Esc ends every wait
// at once; the start chord only reaches an existing (administrator) button.
const test=require('node:test');
const assert=require('node:assert/strict');
const path=require('node:path');
const {chromium}=require(path.resolve('target/ui-tests/node_modules/playwright-core'));

const PAGE=`<main class="repository-study"><div class="auto-run-control"></div>
<article class="repository-task" data-explanation-session="">
 <button id="task-submit" onclick="window.submits=(window.submits||0)+1">제출</button>
 <label class="narration-speed"><select id="speed"><option>1.5</option><option>2</option></select></label>
 <input id="answer">
 <div id="git-student-terminal" data-terminal-session="o1" style="width:700px;height:300px"></div>
</article></main>`;

async function open(t,{buttons=true}={}){
  const browser=await chromium.launch({channel:'msedge',headless:true});
  t.after(()=>browser.close());
  const page=await browser.newPage();
  await page.setContent(PAGE);
  await page.addStyleTag({path:path.resolve('assets/terminal/terminal.bundle.css')});
  await page.addScriptTag({path:path.resolve('assets/terminal/terminal.bundle.js')});
  await page.evaluate(buttons=>{
    window.clicks={start:0,stop:0,pause:0};window.toasts=[];window.agentStops=0;
    window.molipToast=text=>toasts.push(text);
    // The saved speed, as assets/layout/voice.js keeps it: a change is announced with molip:tts-rate.
    let rate=1.5;
    window.molipVoice={name:'ko-KR-SunHiNeural',enabled:()=>true,synthesize:async text=>'clip:'+text,
      get rate(){return rate},setRate(value){rate=value;window.dispatchEvent(new CustomEvent('molip:tts-rate',{detail:value}));return rate}};
    if(buttons){for(const id of ['start','stop','pause']){const b=document.createElement('button');b.id='auto-run-'+id;b.onclick=()=>clicks[id]++;document.querySelector(".auto-run-control").append(b);}}
    // A terminal whose shell answers every Enter with a prompt, like the practice Bash.
    window.inputs='';
    mq3GitTerminal.mount(event=>{if(event.kind!=='input')return;inputs+=event.data;if(event.data.includes('\r'))setTimeout(()=>mq3GitTerminal.write(btoa('\r\n$ '),'o1'),5);},()=>{},'o1');
    mq3GitTerminal.write(btoa('$ '),'o1');
  },buttons);
  await page.addScriptTag({path:path.resolve('assets/layout/agent.js')});
  await page.addScriptTag({path:path.resolve('assets/layout/auto-run.js')});
  await page.evaluate(()=>{const stop=molipAgent.stop;molipAgent.stop=()=>{agentStops++;return stop();};});
  return page;
}

test('pacing follows the narration speed, a change mid-wait, and the pause',async t=>{
  const page=await open(t);
  const r=await page.evaluate(async()=>{
    molipAutoRun.sync({active:true,paused:false,generation:1});
    const time=async run=>{const start=performance.now();const value=await run();return [Math.round(performance.now()-start),value];};
    const out={};
    for(const rate of [0.75,1.5,2]){molipVoice.setRate(rate);out[rate]=(await time(()=>molipAutoRun.pace(400,1)))[0];}
    molipVoice.setRate(0.75);
    setTimeout(()=>molipVoice.setRate(2),500);
    out.changed=(await time(()=>molipAutoRun.pace(1000,1)))[0];
    molipVoice.setRate(1.5);
    setTimeout(()=>molipAutoRun.sync({active:true,paused:true,generation:1}),100);
    setTimeout(()=>molipAutoRun.sync({active:true,paused:false,generation:1}),700);
    out.paused=(await time(()=>molipAutoRun.pace(400,1)))[0];
    out.stale=await time(()=>molipAutoRun.pace(5000,99));
    return out;
  });
  // 400ms authored for 1.5×: 800ms at 0.75×, 400ms at 1.5×, 300ms at 2×.
  assert.ok(Math.abs(r[0.75]-800)<120,`0.75x ${r[0.75]}`);
  assert.ok(Math.abs(r[1.5]-400)<100,`1.5x ${r[1.5]}`);
  assert.ok(Math.abs(r[2]-300)<100,`2x ${r[2]}`);
  // 2000ms at 0.75×; after 500ms (a quarter) the rest takes 3/4 of 750ms.
  assert.ok(r.changed>900&&r.changed<1300,`speed change mid-wait ${r.changed}`);
  assert.ok(r.paused>=950,`a 600ms pause is added ${r.paused}`);
  assert.deepEqual(r.stale[1],false);assert.ok(r.stale[0]<100,'another run never waits');
});

test('terminal actions are typed into the learner terminal at the current speed',async t=>{
  const page=await open(t);
  const r=await page.evaluate(async()=>{
    molipAutoRun.sync({active:true,paused:false,generation:3});
    const time=async rate=>{molipVoice.setRate(rate);inputs='';const start=performance.now();
      const result=await molipAutoRun.solveTerminal([{action:'bash_command',command:'echo "첫 메모" > memo.txt'},{action:'git_command',args:['commit','-m','첫 기록']},{action:'inspect_folder',command:'ls'}],3);
      return {result,ms:performance.now()-start,typed:inputs};};
    return {slow:await time(0.75),fast:await time(2)};
  });
  assert.deepEqual(r.slow.result,{ok:true});assert.deepEqual(r.fast.result,{ok:true});
  assert.equal(r.fast.typed,'echo "첫 메모" > memo.txt\rgit commit -m "첫 기록"\rls\r');
  assert.equal(r.slow.typed,r.fast.typed);
  // 39 characters at 25ms per character (1.5×): 2.67 times as long at 0.75× as at 2×.
  assert.ok(r.slow.ms/r.fast.ms>1.9,`slow ${r.slow.ms} fast ${r.fast.ms}`);
});

test('Esc stops at once: typing, waits and the narration end, and the stop button is pressed',async t=>{
  const page=await open(t);
  await page.evaluate(()=>{molipAutoRun.sync({active:true,paused:false,generation:7});molipVoice.setRate(0.75);inputs='';
    window.solving=molipAutoRun.solveTerminal([{action:'bash_command',command:'echo "아주 긴 명령을 천천히 입력하는 중이에요" > long.txt'},{action:'bash_command',command:'ls'}],7).then(r=>{window.solved={r,at:performance.now()};});});
  await page.waitForFunction(()=>inputs.length>=5);
  const pressed=await page.evaluate(()=>performance.now());
  await page.keyboard.press('Escape');
  await page.waitForFunction(()=>window.solved);
  const r=await page.evaluate(()=>({solved,clicks,agentStops,inputs,state:molipAutoRun.state}));
  assert.equal(r.solved.r.cancelled,true);
  assert.ok(r.solved.at-pressed<150,`typing stopped ${r.solved.at-pressed}ms after Esc`);
  assert.ok(!r.inputs.includes('\r'),'the half-typed command is never entered');
  assert.equal(r.clicks.stop,1);assert.ok(r.agentStops>=1);assert.equal(r.state.active,false);
  // A late Enter of the old run cannot start a new wait.
  assert.deepEqual(await page.evaluate(()=>molipAutoRun.pace(10,7)),false);
});

test('the start chord reaches only an administrator button; Space pauses; learner input is held off',async t=>{
  const student=await open(t,{buttons:false});
  await student.keyboard.press('Control+Alt+Shift+KeyA');
  assert.equal((await student.evaluate(()=>toasts))[0],'자동 풀이는 코스 저장소를 편집할 수 있는 관리자 계정에서만 쓸 수 있어요.');
  assert.equal(await student.evaluate(()=>molipAutoRun.state.active),false);

  const page=await open(t);
  await page.keyboard.press('Control+Alt+Shift+KeyA');
  assert.equal(await page.evaluate(()=>clicks.start),1);
  await page.evaluate(()=>molipAutoRun.sync({active:true,paused:false,generation:9}));
  await page.keyboard.press('Control+Alt+Shift+KeyA');
  assert.equal(await page.evaluate(()=>clicks.start),1,'no second start while running');
  // Focus is in the learner terminal (it focuses itself when mounted): Space still pauses.
  assert.ok(await page.evaluate(()=>!!document.activeElement.closest('.xterm')));
  await page.keyboard.press('Space');
  assert.equal(await page.evaluate(()=>clicks.pause),1);
  await page.focus('#answer');await page.keyboard.press('Space');await page.keyboard.type('x');
  assert.equal(await page.evaluate(()=>clicks.pause),2,'Space in a task field pauses during the run');
  assert.equal(await page.inputValue('#answer'),'','typing into the task is held off during the run');
  await page.focus('#speed');await page.keyboard.press('Space');
  assert.equal(await page.evaluate(()=>clicks.pause),2,'the speed select keeps its own Space');
  await page.click('#task-submit');
  assert.equal(await page.evaluate(()=>window.submits||0),0,'a learner click cannot submit beside the run');
  await page.selectOption('#speed','2');
  assert.equal(await page.inputValue('#speed'),'2','the speed control stays usable');
  await page.evaluate(()=>molipAutoRun.sync({active:false,paused:false,generation:0}));
  await page.click('#task-submit');
  assert.equal(await page.evaluate(()=>window.submits),1,'after the run the learner controls return');
});

test('the narration voice follows the speed, also when it changes while a sentence plays',async t=>{
  const page=await open(t);
  const r=await page.evaluate(async()=>{
    // A clip of 1200ms media time. Like an <audio>, it advances by playbackRate, pauses and resumes.
    window.Audio=class{constructor(url){this.url=url;this.playbackRate=1;this.position=0;}
      play(){clearInterval(this.timer);this.timer=setInterval(()=>{this.position+=20*this.playbackRate;if(this.position>=1200){clearInterval(this.timer);this.onended?.();}},20);return Promise.resolve();}
      pause(){clearInterval(this.timer);}};
    const time=async(rate,change)=>{molipVoice.setRate(rate);const start=performance.now();
      if(change)setTimeout(()=>molipVoice.setRate(change),300);
      await molipAgent.run([{action:'say',text:'첫 문장이에요'}]);return performance.now()-start;};
    return {one:await time(1),two:await time(2),changed:await time(0.75,2)};
  });
  // The agent adds the same fixed pause after every sentence; the clip itself is what scales.
  // 1x: 1200ms of clip, 2x: 600ms. Mid-change: 300ms at 0.75x covers 225ms, the remaining
  // 975ms at 2x takes about 490ms, so about 190ms more than the whole sentence at 2x.
  assert.ok(r.one-r.two>450&&r.one-r.two<750,`1x ${r.one} vs 2x ${r.two}`);
  assert.ok(r.changed-r.two>80&&r.changed-r.two<400,`speed changed mid-sentence ${r.changed} vs 2x ${r.two}`);
  assert.ok(r.one-r.changed>200,`the change shortened the sentence ${r.changed} vs 1x ${r.one}`);
});
