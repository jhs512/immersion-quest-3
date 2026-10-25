(async()=>{
 const checked=[];
 const wait=async(test,label)=>{const end=Date.now()+60000;while(!test()){if(Date.now()>end)throw Error(label);await new Promise(r=>setTimeout(r,40));}};
 const button=text=>[...document.querySelectorAll('button')].find(b=>b.textContent.trim()===text);
 const click=async text=>{await wait(()=>button(text)&&!button(text).disabled,text);button(text).click();};
 const ready=async()=>{await wait(()=>document.querySelector('.repository-task')?.dataset.gitReady==='true'&&document.querySelector('.java-build-source .cm-editor'),'source and PTY ready');await new Promise(r=>setTimeout(r,300));};
 const run=async command=>{const before=mq3GitTerminal.text();mq3GitTerminal.command(command);await wait(()=>mq3GitTerminal.text()!==before&&/\$\s*$/.test(mq3GitTerminal.text()),command);};
 const submit=async passed=>{await click('제출');await wait(()=>document.querySelector('.repository-task')?.dataset.busy==='false'&&document.querySelector('.result-pane')?.dataset.feedback===(passed?'passed':'incorrect'),'submission result');};
 try{
  await wait(()=>button('학습 시작')&&!button('학습 시작').disabled,'initial catalog');await click('버전 '+mq3JavaPilot.pilot);
  await wait(()=>document.querySelector('.lesson-card')?.textContent.includes(mq3JavaLaunch.revision),'Java workspace catalog');await click('학습 시작');await ready();await wait(()=>typeof window.molipAgent?.setVoice==='function','narration module ready');molipAgent.setVoice(false);
  for(let i=0;i<mq3JavaLaunch.tasks.length;i++){
   const task=mq3JavaLaunch.tasks[i];await wait(()=>document.querySelector('.repository-task')?.dataset.taskId===task.id,'task mounted');await ready();
   if(task.interaction||document.querySelector('.answer-interaction input[type=radio]'))throw Error('Java coding lesson still requires an answer choice');
   if(i===0){const pane=document.querySelector('.editor-pane').getBoundingClientRect();for(const selector of ['.java-build-source','#git-student-terminal']){const box=document.querySelector(selector).getBoundingClientRect();if(box.height<48||box.bottom>pane.bottom+1||box.right>pane.right+1)throw Error('Source/terminal layout: '+selector);}
    await wait(()=>window.molipSplit,'workspace dividers ready');
    const divider=document.querySelector('.split-java-source');if(!divider)throw Error('Missing Java editor/terminal divider');
    const sourceHeight=()=>document.querySelector('.java-build-source').getBoundingClientRect().height;
    const before=sourceHeight();divider.dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowDown',bubbles:true,cancelable:true}));
    if(sourceHeight()<before+6)throw Error('Java divider dimensions: '+JSON.stringify({before,after:sourceHeight(),workspace:document.querySelector('.java-build-workspace').getBoundingClientRect().height,outer:pane.height,rows:getComputedStyle(document.querySelector('.java-build-workspace')).gridTemplateRows,style:document.querySelector('.java-build-workspace').getAttribute('style')}));
    divider.dispatchEvent(new MouseEvent('dblclick',{bubbles:true}));
    await submit(false);checked.push('source alone cannot pass without a real terminal command');}
   const source=task.git_terminal.shell.goal.files['Main.java'];
   if(molipCodeEditors.getValue()!==source)molipCodeEditors.setValue(source);
   if(i===2||i===5){
    const student=molipCodeEditors.getValue();let demoText='';const sample=setInterval(()=>{const text=mq3GitDemoTerminal.text();if(text)demoText=text;},60);await click('해설 재생');
    await wait(()=>document.querySelector('.repository-task')?.dataset.narrating==='true','demonstration started');
    if(i===2){molipAgent.pause();button('멈춤').click();}
    await wait(()=>document.querySelector('.repository-task')?.dataset.narrating==='false','demonstration returned');
    clearInterval(sample);if(i===5&&(!demoText.includes(task.git_terminal.shell.commands[0])||!demoText.includes(task.git_terminal.java_build.stdout.trim())))throw Error('Demonstration did not show real JDK output');
    await ready();if(molipCodeEditors.getValue()!==student)throw Error('Demo overwrote learner source');checked.push(i===2?'stopping demonstration preserves editor and terminal':'full demonstration preserves editor and terminal');
   }
   for(const command of task.git_terminal.shell.commands)await run(command);
   if(i===4){
    const wrong=source.replace(/System\.out\.println\([^\n]*\);/,'System.out.println("wrong learner output");');
    if(wrong===source)throw Error('Wrong-source probe did not change Main.java');
    molipCodeEditors.setValue(wrong);await submit(false);
    molipCodeEditors.setValue(source);for(const command of task.git_terminal.shell.commands)await run(command);
    checked.push('valid prior JDK output cannot pass with incorrect learner source');
   }
   await submit(true);checked.push(`step ${i+1} passes with source, artifact and real execution without answer choices`);
   if(i<mq3JavaLaunch.tasks.length-1)await click('다음으로 이동');else await click('수업 목록으로');
  }
  await wait(()=>document.querySelector('.lesson-progress')?.textContent.includes('100% 완료'),'catalog completed');
  dioxus.send({passed:true,checked});
 }catch(error){dioxus.send({passed:false,checked,error:String(error),screen:document.body.innerText.slice(-7000),student:window.mq3GitTerminal?.text(),demo:window.mq3GitDemoTerminal?.text()});}
})();
