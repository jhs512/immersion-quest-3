(async()=>{
 const checked=[],pilot=window.mqSqlPilot;
 const wait=async(predicate,label,seconds=60)=>{const until=Date.now()+seconds*1000;while(Date.now()<until){if(predicate())return;await new Promise(r=>setTimeout(r,50));}throw Error(label);};
 const button=text=>[...document.querySelectorAll('button')].find(b=>b.textContent.trim()===text);
 const click=async text=>{await wait(()=>button(text)&&!button(text).disabled,text);button(text).click();};
 try{
  await wait(()=>document.querySelector('.lesson-card')?.textContent.includes('pilot-a'),'initial fixture');
  await click(`버전 ${pilot.version}`);
  await wait(()=>document.querySelector('.lesson-card')?.textContent.includes(pilot.lesson.revision),'SQL lesson installed');
  await click('학습 시작');
  await wait(()=>document.querySelector('.repository-task'),'first SQL task');
  await wait(()=>document.querySelector('.sql-browser'),'SQL table browser is missing before any code execution',5);
  await wait(()=>document.querySelector('.sql-browser [data-table="item"]'),'prepared item table',120);
  const pane=document.querySelector('.sql-browser');
  for(const text of ['id','name','price','qty','milk','100'])if(!pane.textContent.includes(text))throw Error(`Initial table is missing ${text}`);
  if(molipCodeEditors.getValue().trim()!=='SELECT 1;')throw Error('Opening the table changed learner code');
  checked.push('Prepared table and column names are visible before running SQL');
  const capture=async(name,token)=>{dioxus.send({control:'capture',name,token});await wait(()=>window.mq3CaptureToken===token,'screenshot',30);if(!window.mq3CaptureOk)throw Error('Screenshot failed');};
  document.documentElement.dataset.themeChoice='dark';
  await capture('sql-browser-before-query',1);
  molipCodeEditors.setValue("UPDATE item SET price=777 WHERE id=1; SELECT * FROM item;");
  await click('코드 실행');
  await wait(()=>!button('코드 실행').disabled&&pane.querySelector('.sql-table-data')?.textContent.includes('777'),'updated row visible',60);
  await click('새로고침');
  await wait(()=>!pane.querySelector('button').disabled,'refresh finished',30);
  if(!pane.querySelector('.sql-table-data').textContent.includes('777'))throw Error('Refresh reset learner data');
  checked.push('SQL changes appear in current data; refresh preserves changes');
  document.documentElement.dataset.themeChoice='light';
  await capture('sql-browser-light',2);
  await click('초기화');
  await wait(()=>!pane.querySelector('button').disabled&&pane.querySelector('.sql-table-data')?.textContent.includes('100')&&!pane.querySelector('.sql-table-data')?.textContent.includes('777'),'reset seed restored',60);
  checked.push('Explicit reset restores the seed table');
  dioxus.send({control:'resize',width:900,height:720});
  await wait(()=>innerWidth<1000,'narrow window');
  await capture('sql-browser-narrow',3);
  dioxus.send({passed:true,checked});
 }catch(error){dioxus.send({passed:false,checked,error:String(error),screen:document.body.innerText.slice(-3000)});}
})();
