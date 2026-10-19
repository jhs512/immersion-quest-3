(async()=>{
 const checked=[];const wait=async(test,label)=>{const until=Date.now()+20000;while(!test()){if(Date.now()>until)throw Error(label);await new Promise(r=>setTimeout(r,40));}};
 const button=text=>[...document.querySelectorAll('button')].find(b=>b.textContent.trim()===text&&b.getClientRects().length>0);
 const click=async text=>{await wait(()=>button(text)&&!button(text).disabled,text);button(text).click();};
 try{
  await wait(()=>document.querySelector('.lesson-card')?.textContent.includes('pilot-a'),'initial fixture');
  await click('버전 브');await wait(()=>document.querySelector('.lesson-card')?.textContent.includes('vim-basics-1'),'Vim fixture');
  // Reproduce a filename notification that is not present after a screen redraw.
  const originalText=mq3GitTerminal.text.bind(mq3GitTerminal);mq3GitTerminal.text=()=>'';
  await click('학습 시작');
  await wait(()=>document.querySelector('.repository-task')?.dataset.gitReady==='true','Vim is ready without any filename text');
  await wait(()=>button('제출')&&!button('제출').disabled,'submission enabled');
  if(!mq3GitTerminal.vimState()?.state)throw Error('No actual editor state');
  checked.push('Actual Vim state makes the terminal ready even when its screen exposes no memo.txt text');
  await mq3GitTerminal.typeKeys('i');
  await wait(()=>mq3GitTerminal.vimState()?.passed&&document.querySelector('.vim-live-panel')?.dataset.vimPassed==='true','live insert-mode goal');
  if(button('제출').disabled)throw Error('i reached its goal but submission remains disabled');
  if(mq3GitTerminal.vimState().state.mode!=='i')throw Error('Real Vim is not in insert mode');
  checked.push('Real i input updates live confirmation and leaves submission available');
  const root=document.querySelector('.problem-pane h2');root.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',shiftKey:true,...(/mac/i.test(navigator.platform)?{metaKey:true}:{ctrlKey:true}),bubbles:true,cancelable:true}));
  await wait(()=>document.querySelector('.task-passed-dialog'),'real Vim grading passes');
  checked.push('Submit shortcut grades the actual Vim goal successfully');
  mq3GitTerminal.text=originalText;dioxus.send({passed:true,checked});
 }catch(error){dioxus.send({passed:false,checked,error:String(error),screen:document.body.innerText.slice(-5500)});}
})();
