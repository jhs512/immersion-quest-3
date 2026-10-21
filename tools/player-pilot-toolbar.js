// Geometry and interaction checks run against the production UI in the native WebView.
(async () => {
  const checked=[];
  const wait=async(fn,label)=>{const end=Date.now()+20000;while(Date.now()<end){if(fn())return;await new Promise(r=>setTimeout(r,50));}throw Error(`Timed out: ${label}`);};
  const settle=()=>new Promise(r=>setTimeout(r,250));
  const click=async(text)=>{let b;await wait(()=>b=[...document.querySelectorAll('button')].find(b=>b.textContent.trim()===text&&!b.disabled),text);b.click();await settle();};
  const inside=(el,label)=>{const r=el.getBoundingClientRect();if(r.left<0||r.right>document.documentElement.clientWidth+1||r.top<0||r.bottom>innerHeight+1)throw Error(`${label} escapes viewport: ${JSON.stringify(r)}`);};
  const audit=async(label)=>{
    await settle();
    const header=document.querySelector('.repository-header');
    inside(header,`${label} header`);
    if(header.getBoundingClientRect().height>(innerWidth<700?86:50))throw Error(`${label}: toolbar takes excessive vertical space`);
    const report=document.querySelector('.app-window-controls>button:not(.window-fullscreen-control)');
    const box=report.getBoundingClientRect();
    if(box.height>34||box.width>42)throw Error(`${label}: oversized report button ${box.width}x${box.height}`);
    const controls=[...header.querySelectorAll('button,summary')].filter(e=>!e.closest('details')||e.parentElement.tagName==='DETAILS');
    const visible=controls.filter(e=>e.getClientRects().length&&getComputedStyle(e).visibility!=='hidden'&&![...header.querySelectorAll('details:not([open])')].some(d=>d.contains(e)&&!d.querySelector(':scope>summary')?.contains(e)));
    for(const e of visible)inside(e,`${label} ${e.textContent.trim()}`);
    for(let i=0;i<visible.length;i++)for(let j=i+1;j<visible.length;j++){
      const a=visible[i].getBoundingClientRect(),b=visible[j].getBoundingClientRect();
      if(Math.min(a.right,b.right)-Math.max(a.left,b.left)>1&&Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>1)throw Error(`${label}: controls overlap: ${visible[i].textContent}/${visible[j].textContent}`);
    }
    const settings=document.querySelector('.app-update-settings');
    settings.querySelector('summary').click();await settle();
    inside(settings.querySelector('.app-update-menu'),`${label} settings menu`);
    document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true,cancelable:true}));await settle();
    if(settings.open)throw Error(`${label}: Escape did not close settings`);
    settings.querySelector('summary').click();await settle();
    document.querySelector('h1').dispatchEvent(new MouseEvent('click',{bubbles:true}));await settle();
    if(settings.open)throw Error(`${label}: outside click did not close settings`);
    const content=document.querySelector('.content-update-controls>details');
    content.querySelector('summary').click();await settle();
    inside(content.querySelector('.content-update-menu'),`${label} lesson settings`);
    settings.querySelector('summary').click();await settle();
    if(content.open||!settings.open)throw Error(`${label}: toolbar menus compete`);
    document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true,cancelable:true}));await settle();
    if(document.activeElement!==settings.querySelector('summary'))throw Error(`${label}: Escape lost keyboard focus`);
    checked.push(`${label}: compact controls, no overlap, reachable menus and dismissal`);
  };
  const resize=async(width,height)=>{
    dioxus.send({control:'resize',width,height});
    await wait(()=>Math.abs(innerWidth-width)<40&&innerHeight>=height-100&&innerHeight<=height+40,`${width}x${height}`);await settle();
  };
  try{
    await wait(()=>document.querySelector('.lesson-card')&&document.querySelector('.update-banner'),'catalog and update offer');
    await resize(400,720);inside(document.querySelector('.update-banner'),'narrow update offer');await click('나중에');
    for(const width of [1280,1024,800,640,400]){await resize(width,720);await audit(`catalog ${width}`);}
    await resize(1280,720);await click('학습 시작');
    await wait(()=>document.querySelector('.repository-task'),'learning workspace');
    for(const [width,height] of [[1280,720],[1024,720],[800,720],[640,720],[400,720],[1280,480]]){await resize(width,height);await audit(`lesson ${width}x${height}`);}
    dioxus.send({passed:true,checked});
  }catch(error){dioxus.send({passed:false,checked,error:String(error),viewport:[innerWidth,innerHeight]});}
})();
