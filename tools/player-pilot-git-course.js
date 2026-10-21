(async()=>{
 const checked=[];
 const wait=async(fn,label)=>{const end=Date.now()+45000;while(Date.now()<end){if(fn())return;await new Promise(r=>setTimeout(r,40));}throw Error(`Timed out: ${label}`)};
 const button=text=>[...document.querySelectorAll('button')].find(b=>b.textContent.trim()===text);
 const click=async text=>{await wait(()=>button(text)&&!button(text).disabled,text);button(text).click()};
 const ready=async()=>wait(()=>{const root=document.querySelector('.repository-task'),host=document.getElementById('git-student-terminal');return root?.dataset.gitReady==='true'&&host&&window.mq3GitTerminal?.text(host.dataset.terminalSession).split('\n').some(line=>line.trimEnd().endsWith('$'));},'current student terminal owner and prompt');
 try{
  await wait(()=>document.querySelector('.lesson-card')?.textContent.includes('pilot-a'),'catalog');
  for(const [version,revision,count] of [['l','git-branch-',13],['굳','git-branch-advanced-',5],['풀','github-pr-',8]]){
   await click(`버전 ${version}`);
   await wait(()=>document.querySelector('.lesson-card')?.textContent.includes(revision),revision);
   await click('학습 시작');await ready();
   if(version==='l'){
    const startOwner=document.getElementById('git-student-terminal').dataset.terminalSession;
    document.querySelectorAll('.study-navigation button')[2].click();
    await wait(()=>document.getElementById('git-student-terminal')?.dataset.terminalSession!==startOwner,'branch creation step');await ready();
    const beforeReset=document.getElementById('git-student-terminal').dataset.terminalSession;
    await click('초기화');await wait(()=>document.getElementById('git-student-terminal')?.dataset.terminalSession!==beforeReset,'prepare branch baseline');await ready();
    const owner=()=>document.getElementById('git-student-terminal').dataset.terminalSession;
    const snapshot=()=>window.mq3GitGraphs?.snapshot(owner());
    await wait(()=>snapshot()?.commits.length===1,'actual initial commit graph');
    const graph=document.querySelector(`[data-git-graph-owner="${owner()}"]`);
    const terminalBox=document.getElementById('git-student-terminal').getBoundingClientRect(),graphBox=graph.getBoundingClientRect();
    if(Math.abs(terminalBox.top-graphBox.top)>1||Math.abs(terminalBox.bottom-graphBox.bottom)>1)throw Error('terminal and graph heights differ');
    const divider=graph.parentElement.querySelector('.split-git');
    if(!divider||divider.getBoundingClientRect().width<8||divider.getBoundingClientRect().height<terminalBox.height-1)throw Error('terminal/graph divider is missing');
    const canvas=()=>graph.querySelector('.git-graph-canvas');
    if(graph.dataset.graphCount!=='1'||canvas().getBoundingClientRect().height<80)throw Error('graph is not visible');
    const cy=canvas()._cyreg.cy;
    if(cy.nodes()[0].numericStyle('font-size')*cy.zoom()<11)throw Error('graph labels are too small');
    const small=canvas().getBoundingClientRect();
    graph.querySelector('[data-graph-action="expand"]').click();
    await wait(()=>canvas().getBoundingClientRect().width>small.width*1.5&&canvas().getBoundingClientRect().height>innerHeight*.5,'large readable graph');
    window.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true,cancelable:true}));
    await wait(()=>!graph.classList.contains('is-expanded'),'graph returns to the terminal');
    mq3GitTerminal.command('git branch feature');
    await wait(()=>snapshot()?.references.some(ref=>ref.name==='feature'),'created branch appears on graph');
    mq3GitTerminal.command('git switch feature');
    await wait(()=>snapshot()?.branch==='feature','graph follows branch switch');
    await wait(()=>cy.nodes()[0]?.data('label').includes('HEAD → feature'),'visible HEAD points to feature at the shared commit');
    mq3GitTerminal.command('git switch main');
    await wait(()=>snapshot()?.branch==='main'&&cy.nodes()[0]?.data('label').includes('HEAD → main'),'visible HEAD switches back to main at the same commit');
    mq3GitTerminal.command('git switch feature');
    await wait(()=>snapshot()?.branch==='feature'&&cy.nodes()[0]?.data('label').includes('HEAD → feature'),'visible HEAD switches again');
    cy.pan({x:-900,y:-900});cy.zoom(2);
    graph.querySelector('[data-graph-action="focus"]').click();
    const located=cy.nodes()[0].renderedPosition();
    if(cy.zoom()!==1||Math.abs(located.y-canvas().clientHeight/2)>2||!graph.querySelector('.git-graph-detail').textContent.includes('HEAD → feature'))throw Error('HEAD navigation did not recenter and identify the current branch');
    mq3GitTerminal.command('echo graph > graph.txt && git add graph.txt && git commit -m graph');
    await wait(()=>snapshot()?.commits.length===2,'real commit appears on graph');
    const featureHead=snapshot().head;
    mq3GitTerminal.command('git switch main');await wait(()=>snapshot()?.branch==='main','back to main');
    mq3GitTerminal.command('git merge --ff-only feature');
    await wait(()=>snapshot()?.head===featureHead&&snapshot()?.references.filter(ref=>['main','feature'].includes(ref.name)).every(ref=>ref.id===featureHead),'graph follows fast-forward');
    const oldOwner=owner();await click('초기화');await wait(()=>owner()!==oldOwner,'graph owner reset');await ready();
    await wait(()=>snapshot()?.commits.length===1&&!snapshot()?.references.some(ref=>ref.name==='feature'),'reset restores initial graph');
    const resetGraph=document.querySelector(`[data-git-graph-owner="${owner()}"]`);
    const resetCy=resetGraph.querySelector('.git-graph-canvas')._cyreg.cy;
    if(resetCy.nodes().length!==1||resetGraph.innerText.includes('feature'))throw Error('the visible canvas retained the old graph');
    if(window.mq3GitGraphs.snapshot(oldOwner)!==undefined)throw Error('retired graph survived reset');
    // Reset again after panning and enlarging, including the visual renderer.
    resetGraph.querySelector('[data-graph-action="expand"]').click();
    resetCy.pan({x:-900,y:-900});
    const secondOwner=owner();await click('초기화');await wait(()=>owner()!==secondOwner,'second graph reset');await ready();
    await wait(()=>snapshot()?.commits.length===1,'second reset snapshot');
    const freshGraph=document.querySelector(`[data-git-graph-owner="${owner()}"]`);
    if(freshGraph.classList.contains('is-expanded')||freshGraph.querySelector('.git-graph-canvas')._cyreg.cy.pan().x < -100)throw Error('graph viewport survived reset');
    checked.push('Cytoscape graph follows actual branch, commit, fast-forward and reset');
   }
   if(document.querySelectorAll('.study-navigation button').length!==count)throw Error(`${revision} task count`);
   const firstId=document.querySelector('.repository-task').dataset.taskId;
   for(let i=0;i<count;i++){
    const nav=document.querySelectorAll('.study-navigation button')[i];nav.click();await wait(()=>document.querySelectorAll('.study-navigation button')[i]?.classList.contains('selected'),'selected task');await ready();
    if(version==='l'&&i===1){
     const owner=document.querySelector('#git-student-terminal').dataset.terminalSession;
     await click('초기화');await wait(()=>document.querySelector('#git-student-terminal')?.dataset.terminalSession!==owner,'middle Git step reset');await ready();
     checked.push('shared Git step resets without returning to the first step');
    }
    await new Promise(r=>setTimeout(r,120));
    if(!document.querySelector('.problem-pane h2')?.textContent.trim())throw Error(`${revision} empty task ${i}`);
    if(version==='풀'&&button('새 회차 시작')?.disabled!==(i!==0))throw Error('Hosted reset is not limited to the first stage');
    const choices=document.querySelector('.answer-interaction input[type="radio"]');
    if(choices&&document.querySelector('.answer-interaction legend')?.textContent.trim()!==document.querySelector('.problem-pane h2').textContent.trim())throw Error('the question is missing above the answer choices');
    const pane=document.querySelector('.git-terminal').getBoundingClientRect();
    if(pane.width<=0||pane.height<=0||pane.left<0||pane.right>innerWidth+1)throw Error(`${revision} terminal layout ${JSON.stringify(pane.toJSON())}`);
   }
   checked.push(`${revision}: all ${count} tasks render with the real terminal`);
   if(version==='풀'){
    document.querySelector('.study-navigation button').click();await wait(()=>document.querySelector('.repository-task')?.dataset.taskId===firstId,'first PR task mounted');await ready();
    mq3GitTerminal.command("printf 'keep\\n' > keep.txt; printf 'PR_KEEP_BEFORE\\n'");
    await wait(()=>mq3GitTerminal.text().split('\n').some(line=>line.trim()==='PR_KEEP_BEFORE'),'student file');
    await wait(()=>window.molipAgent,'explanation agent');molipAgent.setVoice(false);
    await click('해설 재생');await wait(()=>document.getElementById('git-demo-terminal'),'separate teacher terminal');
    // With voice off these read-only explanations can finish before a stop click.
    molipAgent.stop();if(button('멈춤')&&!button('멈춤').disabled)button('멈춤').click();await ready();
    mq3GitTerminal.command("cat keep.txt; printf 'PR_KEEP_AFTER\\n'");
    await wait(()=>mq3GitTerminal.text().split('\n').some(line=>line.trim()==='PR_KEEP_AFTER'),'student survives explanation');
    if(!mq3GitTerminal.text().split('\n').some(line=>line.trim()==='keep'))throw Error('student file lost');
    const originalConfirm=window.confirm,oldOwner=document.querySelector('#git-student-terminal').dataset.terminalSession;
    let warning='';window.confirm=message=>{warning=message;return false;};
    await click('새 회차 시작');await new Promise(r=>setTimeout(r,150));
    if(!warning.includes('실제 새 비공개 저장소')||document.querySelector('#git-student-terminal').dataset.terminalSession!==oldOwner)throw Error('Cancelled hosted reset changed the learner workspace or omitted its warning');
    window.confirm=()=>true;await click('새 회차 시작');
    await wait(()=>document.querySelector('#git-student-terminal')?.dataset.terminalSession!==oldOwner,'new hosted practice round');await ready();window.confirm=originalConfirm;
    checked.push('PR explanation preserves learner work; hosted restart requires consent and is limited to the first stage');
   }
   await click('← 코스 수업 목록');
  }
  dioxus.send({passed:true,checked,userAgent:navigator.userAgent});
 }catch(error){dioxus.send({passed:false,checked,error:String(error),screen:document.body.innerText.slice(-5000),terminal:window.mq3GitTerminal?.text()});}
})();
