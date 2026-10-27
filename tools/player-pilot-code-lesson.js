(async()=>{
 const checked=[],pilot=window.mq3LessonPilot;
 const frameLoads=new WeakMap(),observedFrames=new WeakSet();
 const watchFrames=()=>{for(const frame of document.querySelectorAll('iframe'))if(!observedFrames.has(frame)){observedFrames.add(frame);frameLoads.set(frame,0);frame.addEventListener('load',()=>frameLoads.set(frame,(frameLoads.get(frame)||0)+1));}};
 const frameObserver=new MutationObserver(watchFrames);frameObserver.observe(document.body,{childList:true,subtree:true});watchFrames();
 const wait=async(predicate,label)=>{const until=Date.now()+60000;while(Date.now()<until){if(predicate())return;await new Promise(r=>setTimeout(r,40));}throw Error(`Timed out: ${label}`);};
 const button=text=>[...document.querySelectorAll('button')].find(b=>b.textContent.trim()===text);
 const click=async text=>{await wait(()=>button(text)&&!button(text).disabled,text);button(text).click();await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));};
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
  if(task.interaction?.kind==='choice')await wait(()=>{const radios=[...document.querySelectorAll('input[type=radio]')];return radios.length===task.interaction.options.length&&radios.every(radio=>!radio.matches(':disabled')&&radio.checked===(radio.value===bridge()?.value));},'controlled choices ready');
  if(task.interaction?.kind==='choice')document.querySelector(`input[type=radio][value="${task.solution}"]`).click();
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
  await click('학습 시작');molipAgent.setVoice(false);
  let teacherResult='',teacherStatus='',requestedRanges=[],shownDiagrams=[],shownPlots=[],shownWeb=false;const originalExplanation=molipAgent.runExplanation.bind(molipAgent);
  const originalHighlight=molipCodeEditors.highlightLines.bind(molipCodeEditors);
  molipCodeEditors.highlightLines=(from,to,...rest)=>{if(Number.isInteger(from))requestedRanges.push([from,to??from]);return originalHighlight(from,to,...rest);};
  molipAgent.runExplanation=async (actions,options)=>{
   teacherResult='';teacherStatus='';requestedRanges=[];shownDiagrams=[];shownPlots=[];shownWeb=false;
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
  };
  for(const [index,task] of pilot.tasks.entries()){
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
   await click('해설 재생');await wait(()=>molipAgent.running,'teacher starts');
   await wait(()=>!molipAgent.running&&document.querySelector('.repository-task').dataset.narrating==='false','teacher ends');
   await wait(()=>molipCodeEditors.getValue()===initialCode&&bridge()?.value===initialAnswer,'student state restored');verifyTeacher(task);
   await click('제출');await wait(()=>status('다시 풀어보세요'),'teacher did not solve learner task');
   const modification=pilot.modifications[index];
   if(modification){
    if(modification.source){molipCodeEditors.setValue(modification.source);await wait(()=>document.querySelector('[data-code-editor]').dataset.editorValue===modification.source,'learner edit');}
    else await answer(task);
    const editedCode=molipCodeEditors.getValue(),editedAnswer=bridge()?.value;
    await click('해설 재생');await wait(()=>molipAgent.running,'teacher after edit starts');
    await wait(()=>!molipAgent.running&&document.querySelector('.repository-task').dataset.narrating==='false','teacher after edit ends');
    await wait(()=>molipCodeEditors.getValue()===editedCode&&bridge()?.value===editedAnswer,'modified learner state restored');verifyTeacher(task);
    checked.push(`${pilot.label} step ${index+1}: canonical teacher baseline restores an edited or reordered learner answer`);
   }
   if(!modification?.correct)await answer(task);
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
