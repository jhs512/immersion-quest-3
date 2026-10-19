(async()=>{
 const checked=[];
 const wait=async(test,label)=>{const end=Date.now()+10000;while(Date.now()<end){if(test())return;await new Promise(resolve=>setTimeout(resolve,30));}throw Error(label);};
 const button=text=>[...document.querySelectorAll('button')].find(item=>item.textContent.trim()===text);
 const click=async text=>{await wait(()=>button(text)&&!button(text).disabled,text);button(text).click();await new Promise(requestAnimationFrame);};
 const bad=()=>document.querySelector('.answer-state-bridge')?.value==='not-json';
 const responsive=async()=>{for(let n=0;n<5;n++)await new Promise(requestAnimationFrame);};
 try {
  await wait(()=>document.querySelector('.lesson-card')?.textContent.includes('pilot-a'),'initial course');
  await click('버전 n');await wait(()=>document.querySelector('.lesson-card')?.textContent.includes('java-values-1'),'Java course');
  await click('풀모드 시작');
  const step=()=>[...document.querySelectorAll('.study-navigation button')].find(item=>item.textContent.startsWith('문제 5 ·'));
  await wait(step,'ordered step');step().click();await wait(()=>document.querySelector('.answer-order'),'ordered answer');
  const bridge=document.querySelector('.answer-state-bridge');bridge.value='not-json';bridge.dispatchEvent(new Event('input',{bubbles:true}));
  await wait(()=>bad()&&document.querySelector('.execution-status')?.textContent.includes('실행할 조각을 먼저 골라요.'),'invalid answer diagnosis');
  await responsive();checked.push('invalid answer leaves the app responsive');
  await click('← 이전 문제');await click('다음 문제 →');
  await wait(bad,'persisted invalid answer');await responsive();checked.push('reopened invalid saved answer remains responsive');
  await click('초기화');await wait(()=>!bad()&&document.querySelector('.answer-order'),'reset recovered');
  await responsive();checked.push('reset returns to the authored order');
  dioxus.send({passed:true,checked,userAgent:navigator.userAgent});
 }catch(error){dioxus.send({passed:false,checked,error:String(error),screen:document.body.innerText.slice(0,2500)});}
})();
