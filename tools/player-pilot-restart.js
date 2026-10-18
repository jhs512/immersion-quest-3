// Runs inside the actual installed-player WebView for a sequential restart test.
(async()=>{
  const phase=window.mq3RestartPhase;
  const wait=async(predicate,label)=>{const deadline=Date.now()+18000;while(Date.now()<deadline){if(predicate())return;await new Promise(resolve=>setTimeout(resolve,40));}throw new Error(label);};
  const button=text=>[...document.querySelectorAll('button')].find(item=>item.textContent.trim()===text&&!item.disabled);
  try {
    await wait(()=>button('풀모드 시작'),'Course catalog did not open');
    button('풀모드 시작').click();
    await wait(()=>window.molipCodeEditors?.getValue()!=null,'Editor did not mount');
    if(phase==='seed') {
      molipCodeEditors.setValue('console.log(3);');
      button('제출').click();
      await wait(()=>document.querySelector('.execution-status')?.textContent.includes('통과했어요'),'Initial problem did not pass');
      molipCodeEditors.setValue('console.log(99);');
      await wait(()=>document.querySelector('[data-code-editor]')?.dataset.editorValue==='console.log(99);','Draft did not reach player state');
    } else {
      if(molipCodeEditors.getValue()!=='console.log(99);')throw new Error('Restart lost the student draft');
      await wait(()=>document.querySelector('.study-progress')?.textContent.includes('1 / 2'),'Restart lost prior success');
      if(document.querySelector('.study-progress').textContent.includes('최신 버전 완료'))throw new Error('Restart passed the unfinished problem');
    }
    dioxus.send({passed:true,phase,draft:molipCodeEditors.getValue(),progress:document.querySelector('.study-progress').textContent});
  } catch(error) {dioxus.send({passed:false,phase,error:String(error),screen:document.body.innerText.slice(0,2500)});}
})();
