(async()=>{
 const checked=[],pilot=window.mq3LessonPilot;
 const frameLoads=new WeakMap(),observedFrames=new WeakSet();
 const watchFrames=()=>{for(const frame of document.querySelectorAll('iframe'))if(!observedFrames.has(frame)){observedFrames.add(frame);frameLoads.set(frame,0);frame.addEventListener('load',()=>frameLoads.set(frame,(frameLoads.get(frame)||0)+1));}};
 const frameObserver=new MutationObserver(watchFrames);frameObserver.observe(document.body,{childList:true,subtree:true});watchFrames();
 const wait=async(predicate,label,ms=60000)=>{const until=Date.now()+ms;while(Date.now()<until){if(predicate())return;await new Promise(r=>setTimeout(r,40));}throw Error(`Timed out: ${label}`);};
 const button=text=>[...document.querySelectorAll('button')].find(b=>b.textContent.trim()===text);
 // Hidden native WebViews can suspend animation frames; later assertions check readiness.
 const click=async text=>{await wait(()=>button(text)&&!button(text).disabled,text);button(text).click();await new Promise(r=>setTimeout(r,80));};
 const bridge=()=>document.querySelector('.answer-state-bridge');
 const status=text=>document.querySelector('.execution-status')?.textContent.includes(text);
 const prepared=(task,answer)=>{
  if(task.interaction&&!task.example_code)return null;
  const source=task.example_code??answer,marker=task.example_order_marker;if(!marker)return source;
  const offset=source.indexOf(marker),prefix=source.slice(0,offset).split('\n').at(-1);
  const wholeLine=/^[\t ]*$/.test(prefix)&&!source.slice(offset+marker.length).split('\n')[0].trim();
  // Match the authored placeholder indentation; each inserted statement stays in its block.
  const lines=JSON.parse(answer).map(id=>task.interaction.options.find(option=>option.id===id).text).join('\n');
  return source.replace(marker,()=>wholeLine?lines.replaceAll('\n','\n'+prefix):lines);
 };
 const answer=async task=>{
  if(task.interaction?.kind==='choice')await wait(()=>{const radios=[...document.querySelectorAll('input[type=radio][name=step-choice]')];return radios.length===task.interaction.options.length&&radios.every(radio=>!radio.matches(':disabled')&&radio.checked===(radio.value===bridge()?.value));},'controlled choices ready');
  if(task.interaction?.kind==='choice')document.querySelector(`input[type=radio][name=step-choice][value="${task.solution}"]`).click();
  else if(task.interaction?.kind==='fill'){const field=document.querySelector('[aria-label="빈칸 답안"]');field.value=task.solution;field.dispatchEvent(new Event('input',{bubbles:true}));}
  else if(task.interaction?.kind==='order')document.querySelector('.answer-order li:last-child button[aria-label="조각 위로"]').click();
  else if(task.interaction?.kind==='fill_fields'){
   for(const [id,value] of Object.entries(JSON.parse(task.solution))){const field=document.querySelector(`[data-answer-field="${id}"]`);field.value=value;field.dispatchEvent(new Event('input',{bubbles:true}));await wait(()=>JSON.parse(bridge()?.value||'{}')[id]===value,'state cell echo');}
  }else molipCodeEditors.setValue(task.solution);
  await wait(()=>task.interaction?.kind==='fill_fields'?Object.entries(JSON.parse(task.solution)).every(([id,value])=>JSON.parse(bridge()?.value||'{}')[id]===value):task.interaction?bridge()?.value===task.solution:document.querySelector('[data-code-editor]')?.dataset.editorValue===task.solution,'answer echo');
  if(task.example_order_marker)await wait(()=>molipCodeEditors.getValue()===prepared(task,task.solution),'reordered program echo');
 };
 try{
  // Let the initial installation finish before the debug control replaces its store.
  await wait(()=>document.querySelector('.lesson-card')?.textContent.includes('pilot-a'),'initial fixture installed');
  await click('검증 높이 720');await click(`버전 ${pilot.version}`);await wait(()=>document.querySelector('.lesson-card')?.textContent.includes(pilot.revision),'approved code lesson');
  // New course installations require a course-scoped display name before learning.
  if(document.getElementById('course-display-name')){
   const field=document.getElementById('course-display-name');field.value='네트워크검증';field.dispatchEvent(new Event('input',{bubbles:true}));
   await click('이름 저장 후 시작');
  }
  await click('학습 시작');molipAgent.setVoice(false);
  let teacherResult='',teacherStatus='',requestedRanges=[],shownDiagrams=[],shownPlots=[],shownWeb=false;const originalExplanation=molipAgent.runExplanation.bind(molipAgent);
  const originalHighlight=molipCodeEditors.highlightLines.bind(molipCodeEditors);
  molipCodeEditors.highlightLines=(from,to,...rest)=>{if(Number.isInteger(from))requestedRanges.push([from,to??from]);return originalHighlight(from,to,...rest);};
  // A narration's code_flow actions: what the trace view really showed when the narration moved it.
  let flowSeeks=[];
  const flowLines=text=>String(text).split('\n').map(line=>line.replace(/\s+$/,'')).join('\n').replace(/\n+$/,'');
  if(window.mqCodeFlow){const seek=window.mqCodeFlow.seek.bind(window.mqCodeFlow);window.mqCodeFlow.seek=target=>{
   const at=seek(target),dialog=document.getElementById('code-flow-dialog');
   flowSeeks.push({target,at,narrated:window.mqCodeFlow.state().narrated,modal:!!dialog?.matches(':modal'),domLine:Number(dialog?.querySelector('.tv-line.is-next')?.dataset.line),
    shown:flowLines([...(dialog?.querySelectorAll('.tv-line .tv-src')??[])].map(node=>node.textContent).join('\n')),editor:flowLines(molipCodeEditors.getValue()),
    stack:[...(dialog?.querySelectorAll('.tv-frames .tv-frame-title')??[])].map(node=>node.textContent.trim())});
   return at;};}
  molipAgent.runExplanation=async (actions,options)=>{
   teacherResult='';teacherStatus='';requestedRanges=[];shownDiagrams=[];shownPlots=[];shownWeb=false;flowSeeks=[];
   const observer=new MutationObserver(()=>{const panel=document.querySelector('.narration-memory');if(panel)shownDiagrams.push({title:panel.querySelector('figcaption')?.textContent,rows:[...panel.querySelectorAll('.narration-memory-row')].map(row=>row.textContent.replace(/\s/g,''))});for(const image of document.querySelectorAll('.plot-result img'))if(image.src.startsWith('data:image/png;base64,'))shownPlots.push(image.src);});
   const webObserver=new MutationObserver(()=>{if(document.querySelector('iframe[title="해설 웹 미리보기"]')?.getAttribute('srcdoc'))shownWeb=true;if(document.querySelector('.repository-task')?.dataset.narrating==='true')teacherStatus=document.querySelector('.execution-status')?.textContent+': '+document.querySelector('.output')?.textContent;});
   webObserver.observe(document.body,{subtree:true,childList:true,attributes:true,attributeFilter:['srcdoc']});
   observer.observe(document.body,{subtree:true,childList:true,characterData:true});
   try{const result=await originalExplanation(actions,options);teacherResult=result;return result;}finally{observer.disconnect();webObserver.disconnect();}
  };
  const verifyTeacher=task=>{
   if(pilot.requirePlot&&!shownPlots.length)throw Error(`Teacher plot was not rendered in the output panel: ${teacherResult}; ${teacherStatus}`);
   if(pilot.requireHtml&&!shownWeb)throw Error(`Teacher webpage was not rendered in the output panel: ${teacherResult}; ${teacherStatus}`);
   if(teacherResult.includes('오류 -')||teacherResult.split('run:').length-1!==task.narration.filter(action=>action.action==='run').length)throw Error(`Teacher did not finish all authored runs: ${teacherResult}`);
   for(const action of task.narration){
    const range=String(action.target??'').match(/^(?:lines|editor):(\d+)(?::(\d+))?$/);
    const wanted=range?[Number(range[1]),Number(range[2]??range[1])]:action.lines;
    if(wanted&&!requestedRanges.some(actual=>actual[0]===wanted[0]&&actual[1]===wanted[1]))throw Error(`Teacher line highlight was not applied: ${wanted}`);
    if(action.diagram&&!shownDiagrams.some(actual=>actual.title===action.diagram.title&&action.diagram.rows.every((row,index)=>actual.rows[index]===row.replace(/\s/g,''))))throw Error(`Teacher memory diagram was not shown: ${action.diagram.title}`);
   }
   // Narrated 코드 흐름 보기: each step opened on the teacher's own code, without a modal, on the authored line.
   const flows=task.narration.filter(action=>action.action==='code_flow'&&!action.close);
   if(flowSeeks.length!==flows.length)throw Error(`Narration moved the code flow ${flowSeeks.length} times, authored ${flows.length}: ${teacherResult}`);
   flows.forEach((action,i)=>{
    const seen=flowSeeks[i];
    if(!seen.at||seen.at.line!==action.line||seen.domLine!==action.line)throw Error(`Narrated code flow is not on line ${action.line}: ${JSON.stringify(seen)}`);
    if(!seen.narrated||seen.modal)throw Error('Narrated code flow opened as the modal learner view');
    if(seen.shown!==seen.editor)throw Error('Narrated code flow shows a different program than the teacher editor');
    if(!seen.stack.length)throw Error('Narrated code flow shows no call stack');
   });
   if(document.getElementById('code-flow-dialog')?.open)throw Error('The narrated code flow stayed open after the narration');
   return flows.length?`${flows.length} traced steps on lines ${flowSeeks.map(seen=>`${seen.at.line} (${seen.at.step}/${seen.at.steps}, ${seen.stack.join(' > ')})`).join(', ')}`:'';
  };
  for(const [index,task] of pilot.tasks.entries()){
   if(index<(window.mq3PilotFrom||0)){molipShortcuts.move('next');await new Promise(r=>setTimeout(r,300));continue;}
   if(task.git_terminal?.cloud){
    // A cloud step grades the owned local EC2 API state. The learner's answer is the narration's own
    // edits and commands, made in the learner's editor and terminal; the teacher uses its own runtime.
    const minutes=m=>m*60000;
    const feedback=()=>document.querySelector('.result-pane')?.dataset.feedback;
    const terminalReady=()=>document.querySelector('.repository-task')?.dataset.taskId===task.id&&document.querySelector('.repository-task')?.dataset.gitReady==='true'&&/\$\s*$/.test(window.mq3GitTerminal?.text()??'');
    const editable=task.git_terminal.cloud.editable??[],start=task.git_terminal.shell.start.files;
    const tab=name=>[...document.querySelectorAll('[data-editor-tab]')].find(t=>t.dataset.editorTab===name&&t.getClientRects().length);
    const show=async name=>{if(tab(name).getAttribute('aria-selected')!=='true')tab(name).click();await wait(()=>document.querySelector(`textarea[data-editor-file="${CSS.escape(name)}"]`)&&molipCodeEditors.getValue()!=null,`${name} editor`);};
    const files=async()=>{const seen={};for(const name of editable){await show(name);seen[name]=molipCodeEditors.getValue();}return seen;};
    // A repeated verdict looks the same, so first see the grading start (button busy or verdict cleared).
    const submit=async(expected,label)=>{
     await click('제출');
     await wait(()=>button('제출')?.disabled||feedback()!==expected,`${label}: grading starts`,10000).catch(()=>{});
     await wait(()=>feedback()===expected&&!button('제출')?.disabled,label,minutes(5));
     if(button('여기 머물기'))await click('여기 머물기');
    };
    await wait(terminalReady,`cloud step ${index+1} ready`,minutes(15));
    // The grid must put the code in the editor row: code visible, the height handle below it, a usable terminal.
    const gridOk=(terminal,label)=>{
     // Measure inside the workspace that holds this terminal: the learner's stays in the page during an explanation.
     const root=document.querySelector(terminal)?.closest('.git-terminal-shell');
     // A step with only read-only helpers shows the selected helper as a plain block instead of an editor.
     const editorBox=root?.querySelector('.compose-source .cm-editor')??root?.querySelector('.compose-source textarea')??root?.querySelector('.compose-source pre.readonly-file');
     const code=editorBox?.getBoundingClientRect(),handle=root?.querySelector('.split-java-source')?.getBoundingClientRect(),term=document.querySelector(terminal)?.getBoundingClientRect();
     // Structure, not only size: the notes row must come first so the editor sits in the sized editor row
     // (a min-content row collapses a not-yet-measured editor to nothing).
     const kids=[...(root?.children??[])],notesFirst=kids[0]?.classList.contains('docker-notes')&&kids.indexOf(root.querySelector(':scope > .compose-source'))===1;
     const seen={notesFirst,editor:editorBox?.className||'none',code:Math.round(code?.height||0),handleBelowCode:!!(code&&handle&&handle.top>=code.bottom-2),terminal:Math.round(term?.height||0)};
     if(!(seen.notesFirst&&seen.code>=80&&seen.handleBelowCode&&seen.terminal>=110))throw Error(`Cloud step ${index+1} ${label} layout: ${JSON.stringify(seen)}`);
    };
    // Layout as the learner sees it: how much of each prepared file the editor shows without scrolling.
    await new Promise(r=>setTimeout(r,500));
    const layout=[];
    for(const name of editable){
     await show(name);await new Promise(r=>setTimeout(r,200));
     const scroller=document.querySelector('.compose-source .cm-scroller'),line=document.querySelector('.compose-source .cm-line');
     const lineHeight=line?.getBoundingClientRect().height||0,lines=start[name].replace(/\n$/,'').split('\n').length;
     const shown=lineHeight?Math.floor((scroller?.clientHeight||0)/lineHeight):0;
     const rect=[...document.querySelectorAll('.compose-source .cm-line')].map(l=>l.getBoundingClientRect());
     layout.push({name,lines,shown,scrolls:(scroller?.scrollHeight||0)>(scroller?.clientHeight||0)+2,lastLineVisible:rect.length===lines&&rect.at(-1).bottom<=(scroller?.getBoundingClientRect().bottom||0)+1});
    }
    checked.push(`layout step ${index+1} window ${innerWidth}x${innerHeight} terminal ${Math.round(document.querySelector('#git-student-terminal')?.getBoundingClientRect().height||0)}px ${JSON.stringify(layout)}`);
    // Every code block of the problem (copyable options, starting commands) has a working 「복사」 button.
    const fences=(task.goal.match(/```/g)||[]).length/2,blocks=[...document.querySelectorAll('.problem-pane .markdown pre')];
    if(blocks.length!==fences||blocks.some(b=>!b.querySelector(':scope > .code-copy')))throw Error(`Cloud step ${index+1}: ${blocks.length}/${fences} code blocks with a copy button`);
    if(blocks.length){blocks[0].querySelector('.code-copy').click();await wait(()=>blocks[0].querySelector('.code-copy').textContent==='복사했어요','copy button copies',5000);}
    // Tabs: the editable files, then the read-only prepared helpers. A step with neither has no editor.
    const readonly=task.git_terminal.readonly_files??[],shownTabs=[...editable,...readonly];
    if(shownTabs.length)gridOk('#git-student-terminal','learner');
    else if(document.querySelector('.compose-source'))throw Error(`Cloud step ${index+1} shows an editor without files`);
    const tabs=[...document.querySelectorAll('[data-editor-tab]')].filter(t=>t.getClientRects().length).map(t=>t.dataset.editorTab);
    if(JSON.stringify(tabs)!==JSON.stringify(shownTabs))throw Error(`Cloud editor tabs ${tabs} differ from ${shownTabs}`);
    for(const [name,text] of Object.entries(await files()))if(text!==start[name])throw Error(`${name} does not show the prepared file`);
    for(const name of readonly){
     // A read-only helper is plain text in the editor area: its content, and no editor that could change it.
     tab(name).click();
     const block=()=>document.querySelector(`pre[data-readonly-file="${CSS.escape(name)}"]`);
     await wait(()=>block()?.textContent===start[name],`${name} shows the prepared helper`,10000);
     if(document.querySelector(`textarea[data-editor-file="${CSS.escape(name)}"]`))throw Error(`${name} is editable`);
    }
    if(readonly.length)tab(editable[0]??readonly[0]).click();
    await submit('incorrect','cloud start state rejected');
    for(const action of task.narration){
     if(action.action==='patch_code'){
      await show(action.file);const source=molipCodeEditors.getValue();
      if(source.split(action.before).length!==2)throw Error(`${action.file}: ${action.before}`);
      const edited=source.split(action.before).join(action.after);molipCodeEditors.setValue(edited);
      await wait(()=>document.querySelector(`textarea[data-editor-file="${CSS.escape(action.file)}"]`)?.dataset.editorValue===edited,'learner cloud edit saved');
      await new Promise(r=>setTimeout(r,400));
     }else if(action.action==='bash_command'){
      const previous=window.mq3GitTerminal.text();window.mq3GitTerminal.command(action.command);
      await wait(()=>window.mq3GitTerminal.text()!==previous&&/\$\s*$/.test(window.mq3GitTerminal.text()),`learner runs ${action.command.slice(0,40)}`,(action.wait_seconds??60)*1000+minutes(1));
     }
    }
    const solved=await files();
    await submit('passed','learner cloud state accepted');
    // The teacher prepares its own cloud first; server steps take minutes before narration starts.
    await click('해설 재생');await wait(()=>molipAgent.running,'cloud teacher begins',minutes(15));
    await wait(()=>document.querySelector('#git-demo-terminal')&&window.molipGitTutor?.owner===document.querySelector('#git-demo-terminal')?.dataset.terminalSession,'teacher terminal shown',minutes(15));
    await new Promise(r=>setTimeout(r,600));if(shownTabs.length)gridOk('#git-demo-terminal','teacher');
    await wait(()=>!molipAgent.running&&document.querySelector('.repository-task')?.dataset.narrating==='false','cloud teacher ends',minutes(30));
    verifyTeacher(task);
    if(teacherResult.includes('중단했습니다')||teacherResult.includes('해설을 멈췄어요')||teacherResult.split('bash_command:').length-1!==task.narration.filter(a=>a.action==='bash_command').length)throw Error(`Cloud teacher did not finish: ${teacherResult}`);
    if(JSON.stringify(await files())!==JSON.stringify(solved))throw Error('The teacher changed the learner files');
    await submit('passed','teacher preserved the learner cloud state');
    const owner=document.querySelector('#git-student-terminal')?.dataset.terminalSession;
    await click('초기화');await wait(()=>document.querySelector('#git-student-terminal')?.dataset.terminalSession!==owner&&terminalReady(),'cloud reset creates a fresh environment',minutes(15));
    for(const [name,text] of Object.entries(await files()))if(text!==start[name])throw Error(`${name} was not restored by 초기화`);
    await submit('incorrect','reset cloud task is unsolved');
    checked.push(`${pilot.label} step ${index+1}: editor tabs, learner edits and commands graded by the local cloud API, teacher isolation and owned reset`);
    if(index<pilot.tasks.length-1)molipShortcuts.move('next');
    continue;
   }
   if(task.git_terminal?.network){
    const terminalReady=()=>document.querySelector('.repository-task')?.dataset.taskId===task.id&&document.querySelector('.repository-task')?.dataset.gitReady==='true'&&/\$\s*$/.test(window.mq3GitTerminal?.text()??'');
    await wait(terminalReady,`network step ${index+1} ready`);
    await click('제출');await wait(()=>document.querySelector('.result-pane')?.dataset.feedback==='incorrect','incomplete network state rejected');
    const previous=window.mq3GitTerminal.text();
    window.mq3GitTerminal.command(task.solution.replaceAll('\n','; '));
    await wait(()=>window.mq3GitTerminal.text()!==previous&&/\$\s*$/.test(window.mq3GitTerminal.text()),'authored Docker solution returns');
    await click('제출');await wait(()=>document.querySelector('.result-pane')?.dataset.feedback==='passed','actual network state accepted');
    if(button('여기 머물기'))await click('여기 머물기');
    await click('해설 재생');await wait(()=>molipAgent.running,'Docker teacher begins');
    await wait(()=>!molipAgent.running&&document.querySelector('.repository-task')?.dataset.narrating==='false','Docker teacher ends');
    verifyTeacher(task);
    if(teacherResult.includes('중단했습니다')||teacherResult.includes('해설을 멈췄어요')||teacherResult.split('bash_command:').length-1!==task.narration.filter(a=>a.action==='bash_command').length)throw Error(`Docker teacher did not finish: ${teacherResult}`);
    await click('제출');await wait(()=>document.querySelector('.result-pane')?.dataset.feedback==='passed','teacher preserved solved student Docker state');
    if(button('여기 머물기'))await click('여기 머물기');
    const owner=document.querySelector('#git-student-terminal')?.dataset.terminalSession;
    await click('초기화');await wait(()=>document.querySelector('#git-student-terminal')?.dataset.terminalSession!==owner&&terminalReady(),'Docker reset creates fresh environment');
    await click('제출');await wait(()=>document.querySelector('.result-pane')?.dataset.feedback==='incorrect','reset Docker task is unsolved');
    checked.push(`${pilot.label} step ${index+1}: actual Docker grading, teacher isolation and owned reset`);
    if(index<pilot.tasks.length-1)molipShortcuts.move('next');
    continue;
   }
   await wait(()=>document.querySelector('.repository-task')?.dataset.taskId===task.id&&window.molipCodeEditors?.getValue()===prepared(task,task.starter_code)&&(!task.interaction||bridge()?.value===task.starter_code),`step ${index+1}`);
   if(task.question){
    if(document.querySelector('.task-question')?.textContent.trim()!==task.question)throw Error('The explicit learner question is missing');
    // Choices are a fieldset whose legend is the question; a fill step shows the question above its one answer field.
    if(task.interaction?.kind==='fill'){if(!document.querySelector('.answer-interaction input[aria-label="빈칸 답안"]'))throw Error('The fill question has no answer field');}
    // A code step with a question shows it above the editor (checked above); only choice steps have a legend.
    else if(task.interaction&&document.querySelector('.answer-interaction legend')?.textContent.trim()!==task.question)throw Error('The answer choices do not show the actual question');
   }
   if(task.predict_before_run&&!bridge()?.value){
    if(!document.querySelector('.prediction-run-note')?.textContent.includes('예상 보기를 먼저'))throw Error('The locked run button has no explanation');
   }
   const files=Object.entries(task.files??{});
   if(files.length){
    await wait(()=>document.querySelectorAll('.provided-file').length===files.length,'provided file list');
    const container=document.querySelector('.provided-files');container.querySelector(':scope > summary').click();
    for(const [name,body] of files){
     const item=[...container.querySelectorAll('.provided-file')].find(item=>item.querySelector('summary').textContent.startsWith(name));
     if(!item)throw Error(`Provided file missing: ${name}`);
     item.querySelector('summary').click();
     if(!item.open||!item.textContent.includes(body.trim()))throw Error(`Provided file preview differs: ${name}`);
     if((task.example_code??task.starter_code).includes(name)&&!item.querySelector('summary').textContent.includes('이 문제에서 사용'))throw Error(`Used file is not marked: ${name}`);
     item.querySelector('summary').click();
    }
    container.querySelector(':scope > summary').click();
   }
   const initialCode=molipCodeEditors.getValue(),initialAnswer=bridge()?.value;
   if(pilot.webPreviewOnly){
    await answer(task);await click('제출');
    await wait(()=>document.querySelector('.result-pane')?.dataset.feedback==='passed','correct answer passes without running a preview first');
    if(document.querySelector('.web-console'))throw Error('Successful grading was displayed as a console log');
    await click('여기 머물기');await click('초기화');
    await wait(()=>molipCodeEditors.getValue()===initialCode,'restore starter after grading-only check');
   }
   await click('해설 재생');await wait(()=>molipAgent.running,'teacher starts');
   await wait(()=>!molipAgent.running&&document.querySelector('.repository-task').dataset.narrating==='false','teacher ends',180000);
   await wait(()=>molipCodeEditors.getValue()===initialCode&&bridge()?.value===initialAnswer,'student state restored');
   const narratedFlow=verifyTeacher(task);
   if(narratedFlow)checked.push(`${pilot.label} step ${index+1}: narration opened 코드 흐름 보기 on the teacher code and showed ${narratedFlow}, then closed it and restored the learner code`);
   await click('제출');await wait(()=>status('다시 풀어보세요'),'teacher did not solve learner task');
   const modification=pilot.modifications?.[index];
   if(modification){
    if(modification.source){molipCodeEditors.setValue(modification.source);await wait(()=>document.querySelector('[data-code-editor]').dataset.editorValue===modification.source,'learner edit');}
    else await answer(task);
    const editedCode=molipCodeEditors.getValue(),editedAnswer=bridge()?.value;
    await click('해설 재생');await wait(()=>molipAgent.running,'teacher after edit starts');
    await wait(()=>!molipAgent.running&&document.querySelector('.repository-task').dataset.narrating==='false','teacher after edit ends',180000);
    await wait(()=>molipCodeEditors.getValue()===editedCode&&bridge()?.value===editedAnswer,'modified learner state restored');verifyTeacher(task);
    checked.push(`${pilot.label} step ${index+1}: canonical teacher baseline restores an edited or reordered learner answer`);
   }
   if(!modification?.correct)await answer(task);
   // 코드 흐름 보기: only on the steps that offer it; traces the code now in the editor and leaves it as it was.
   if(task.code_flow_state==='hidden'&&button('코드 흐름 보기'))throw Error('Code flow is offered on a step without code or with an explicit opt-out');
   if(task.code_flow_state==='unsupported'){
    const unavailable=button('코드 흐름 보기');
    if(!unavailable?.disabled||!document.querySelector('.code-flow-unavailable')?.textContent.trim())throw Error('Unsupported code flow has no disabled control and explanation');
   }
   if(task.code_flow_state==='ready'&&!button('코드 흐름 보기'))throw Error('Code flow is missing from an enabled code step');
   if(task.code_flow_state==='ready'&&task.code_flow===true){
    const before=molipCodeEditors.getValue(),dialog=()=>document.getElementById('code-flow-dialog');
    await click('코드 흐름 보기');
    await wait(()=>dialog()?.open,'code flow dialog opens');
    const until=Date.now()+180000;while(Date.now()<until&&!window.mqCodeFlow.position()&&!dialog().querySelector('.code-flow-status.is-error'))await new Promise(r=>setTimeout(r,100));
    if(!window.mqCodeFlow.position())throw Error('Code flow did not trace: '+dialog().querySelector('.code-flow-status')?.textContent);
    // The core view draws an empty line as one space; compare the lines without trailing blanks.
    const lines=text=>text.split('\n').map(line=>line.replace(/\s+$/,'')).join('\n').replace(/\n+$/,'');
    const shown=lines([...dialog().querySelectorAll('.tv-line .tv-src')].map(node=>node.textContent).join('\n'));
    if(shown!==lines(before))throw Error('Code flow shows a different program than the editor');
    const at=()=>window.mqCodeFlow.position(),active=()=>Number(dialog().querySelector('.tv-line.is-next')?.dataset.line);
    const step=async(go,expected)=>{dialog().querySelector(`[data-go="${go}"]`).click();await wait(()=>at().step===expected&&active()===at().line,`code flow ${go}`);};
    if(at().step!==1||active()!==at().line)throw Error('Code flow does not start at its first step on the traced line');
    await step('next',2);await step('prev',1);await step('last',at().steps);
    const printed=dialog().querySelector('.tv-stdout').textContent.replace(/\r\n?/g,'\n').trim();
    if(printed!==task.tests[0].expected.trim())throw Error(`Code flow output ${JSON.stringify(printed)} differs from the graded output`);
    if(!dialog().querySelector('.tv-frames .tv-frame-title')&&at().steps>1)throw Error('Code flow shows no call stack');
    if(/\bnew\b/.test(before)&&!dialog().querySelector('.tv-heap .tv-object, .tv-heap .tv-note'))throw Error('Code flow shows no object panel');
    dialog().querySelector('.code-flow-close').click();await wait(()=>!dialog().open,'code flow closes');
    if(molipCodeEditors.getValue()!==before)throw Error('Code flow changed the learner code');
    checked.push(`${pilot.label} step ${index+1}: code flow traces the editor code, steps forward/back in line sync, ends with the graded output and closes without changes`);
   }
   if(pilot.requirePlot&&index===0){
    await click('코드 실행');
    await wait(()=>status('실행을 마쳤어요')&&[...document.querySelectorAll('.plot-result img')].some(image=>image.complete&&image.naturalWidth>0),'student plot is visible');
    const studentPlot=document.querySelector('.plot-result img').src;
    await click('해설 재생');await wait(()=>molipAgent.running,'teacher with student plot starts');
    await wait(()=>!molipAgent.running&&document.querySelector('.repository-task').dataset.narrating==='false','teacher with student plot ends');
    await wait(()=>document.querySelector('.plot-result img')?.src===studentPlot,'student plot restored after teacher');verifyTeacher(task);
   }
   if(pilot.requireHtml&&index===0){
    await click('코드 실행');
    await wait(()=>status('실행을 마쳤어요')&&document.querySelector('iframe[title="수업 웹 미리보기"]')?.getAttribute('srcdoc'),'student webpage is visible');
    const studentFrame=document.querySelector('iframe[title="수업 웹 미리보기"]');
    await wait(()=>frameLoads.get(studentFrame)>0,'student page load');
    if(document.querySelector('.result-pane > pre.output'))throw Error('Web lesson still shows the duplicate text output');
    // Exercise the actual Rust message subscription, not only the bridge in isolation.
    studentFrame.srcdoc += '<button id="mq3-log-test" onclick="console.log(\'later log\');throw Error(\'preview failure\')">log</button><script>console.log("initial preview log")<\/script>';
    await wait(()=>document.querySelector('.web-console')?.textContent.includes('initial preview log'),'real preview log opens console');
    studentFrame.contentWindow.postMessage({type:'mq3-web-action',id:'console-test',do:'click',selector:'#mq3-log-test'},'*');
    await wait(()=>document.querySelector('.web-console')?.textContent.includes('later log')&&document.querySelector('.web-console')?.textContent.includes('preview failure'),'later click and runtime error reach console');
    const studentPreview=studentFrame.getAttribute('srcdoc'),studentWindow=studentFrame.contentWindow,studentLoads=frameLoads.get(studentFrame);
    await click('해설 재생');await wait(()=>molipAgent.running,'teacher with student webpage starts');
    await wait(()=>!molipAgent.running&&document.querySelector('.repository-task').dataset.narrating==='false','teacher with student webpage ends');
    await wait(()=>document.querySelector('iframe[title="수업 웹 미리보기"]')?.getAttribute('srcdoc')===studentPreview,'student webpage restored');
    if(document.querySelector('iframe[title="수업 웹 미리보기"]')!==studentFrame||studentFrame.contentWindow!==studentWindow||frameLoads.get(studentFrame)!==studentLoads)throw Error('Teacher replaced or reloaded the live student webpage');
    verifyTeacher(task);
    if(pilot.webPreviewOnly){
     molipCodeEditors.setValue(initialCode);
     await wait(()=>document.querySelector('[data-code-editor]')?.dataset.editorValue===initialCode,'wrong code echo');
     await click('제출');await wait(()=>document.querySelector('.result-pane')?.dataset.feedback==='incorrect','wrong web answer rejected');
     await wait(()=>[...document.querySelectorAll('.web-console')].some(node=>node.textContent.includes('검사 결과')&&node.querySelector('.output')?.textContent.trim()),'failed checks stay visible beside the live preview');
     dioxus.send({passed:true,checked:['No duplicate page text','Successful grading without a preview does not create a console','Live preview console: initial log, later click, runtime error','Narration preserves the student iframe and logs','Failed grading keeps its diagnostic beside the existing preview']});
     return;
    }
   }
   await click('제출');await wait(()=>status(index===pilot.tasks.length-1?'수업 완료':'통과했어요'),'authored solution accepted');
   await click('초기화');await wait(()=>molipCodeEditors.getValue()===initialCode&&bridge()?.value===initialAnswer,'independent reset');
   if(pilot.requirePlot&&document.querySelector('.plot-result img'))throw Error('Reset retained the previous plot');
   if(pilot.requireHtml)await wait(()=>!document.querySelector('iframe[title="수업 웹 미리보기"]'),'reset clears student webpage');
   await click('제출');await wait(()=>status('다시 풀어보세요'),'reset task is unsolved');
   checked.push(`${pilot.label} step ${index+1}: teacher restoration, wrong answer, correct submission, independent reset`);
   if(index<pilot.tasks.length-1)molipShortcuts.move('next');
  }
  dioxus.send({passed:true,checked,userAgent:navigator.userAgent,viewport:{width:innerWidth,height:innerHeight}});
 }catch(error){dioxus.send({passed:false,checked,error:String(error),screen:document.body.innerText.slice(0,6000)});}
})();
