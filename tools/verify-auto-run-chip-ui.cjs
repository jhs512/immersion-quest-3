// Render the lesson header's 관리자 자동 풀이 chip with the app's real stylesheets and measure
// that its state mark keeps clear of the chip edge in every state, theme and width.
// Usage: node tools/verify-auto-run-chip-ui.cjs  (needs target/ui-tests/node_modules/playwright-core and Edge or Chrome)
const {chromium}=require('../target/ui-tests/node_modules/playwright-core');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const root=path.resolve(__dirname,'..');
const sheets=['assets/app.css','assets/repository-player.css','assets/content-updates.css','assets/player-workspace.css','assets/git-graph.css','assets/window-controls.css','assets/diagnostics.css','assets/compact-toolbar.css','assets/product-ui.css','assets/station.css']
  .map(file=>fs.readFileSync(path.join(root,file),'utf8').replace(/@import[^;]+;/g,'')).join('\n');
// The same markup src/player_ui.rs renders for each state of the run.
const icon='<svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true"><path d="M4.5 3.5h2.5v9H4.5zM9 3.5h2.5v9H9z" fill="currentColor"></path></svg>';
const control=(state,mark,label)=>state==='running'||state==='paused'
  ? `<div class="auto-run-control" role="group" data-state="${state}"><span class="auto-run-chip" role="status"><span class="${state==='paused'?'auto-run-state paused':'auto-run-state'}" aria-hidden="true"></span>${label}</span><button id="auto-run-pause" class="auto-run-icon" type="button">${icon}</button><button id="auto-run-stop" class="auto-run-icon danger" type="button">${icon}</button></div>`
  : `<div class="auto-run-control" role="group" data-state="${state}"><details class="auto-run-details"><summary class="auto-run-chip"><span class="auto-run-end" aria-hidden="true"></span>${label}</summary></details></div>`;
const page=(theme,state,label)=>`<!doctype html><html data-theme-choice="${theme}"><head><meta charset="utf-8"><style>${sheets}</style></head><body>
<div class="repository-study is-task"><header class="repository-header"><button class="course-back">← 코스 수업 목록</button><h1>이미지와 컨테이너 · 지워도 남는 것과 사라지는 것</h1>
<span class="auto-run-slot" data-auto="${state}"><button class="lesson-share" type="button">수업 링크 복사</button>${control(state,null,label)}</span></header></div></body></html>`;
(async()=>{
  const executablePath=['C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe','C:/Program Files/Google/Chrome/Application/chrome.exe','/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'].find(p=>fs.existsSync(p));
  const browser=await chromium.launch({executablePath,headless:true});
  const tab=await browser.newPage();
  const out=path.join(root,'target/auto-run-chip-ui');fs.mkdirSync(out,{recursive:true});
  const rows=[];
  for (const theme of ['light','dark']) for (const width of [1280,720,420]) for (const [state,label] of [['running','3'],['running','개념'],['paused','12'],['stopped','멈춤'],['finished','완료']]) {
    await tab.setViewportSize({width,height:200});
    await tab.setContent(page(theme,state,label));
    const m=await tab.evaluate(()=>{
      const chip=document.querySelector('.auto-run-chip'),mark=chip.querySelector('span'),c=chip.getBoundingClientRect(),d=mark.getBoundingClientRect(),slot=document.querySelector('.auto-run-slot').getBoundingClientRect(),ctl=document.querySelector('.auto-run-control').getBoundingClientRect();
      const range=document.createRange();range.selectNodeContents(chip);const content=range.getBoundingClientRect();
      return {left:d.left-c.left,right:c.right-content.right,markWidth:d.width,clipped:content.left<c.left-0.5||content.right>c.right+0.5,inside:ctl.left>=slot.left-0.5&&ctl.right<=slot.right+0.5,chip:c.width};
    });
    rows.push({theme,width,state,label,...m});
    await tab.screenshot({path:path.join(out,`${theme}-${width}-${state}-${label}.png`),clip:await tab.locator('.auto-run-slot').boundingBox().then(b=>({x:b.x-6,y:b.y-6,width:b.width+12,height:b.height+12}))});
  }
  await browser.close();
  console.table(rows.map(r=>({...r,left:r.left.toFixed(1),right:r.right.toFixed(1),chip:r.chip.toFixed(1)})));
  for (const r of rows) {
    assert.ok(r.markWidth>=7,`${r.theme} ${r.width} ${r.state}: state mark is visible`);
    assert.ok(r.left>=4,`${r.theme} ${r.width} ${r.state}: mark keeps ${r.left.toFixed(1)}px from the chip edge`);
    assert.ok(r.right>=3,`${r.theme} ${r.width} ${r.state}: label keeps ${r.right.toFixed(1)}px from the chip edge`);
    assert.ok(!r.clipped,`${r.theme} ${r.width} ${r.state} ${r.label}: content fits the chip`);
    assert.ok(r.inside,`${r.theme} ${r.width} ${r.state}: control stays inside the share button's box`);
  }
  console.log(`PASS ${rows.length} chip renderings keep the state mark off the edge; screenshots in target/auto-run-chip-ui`);
})().catch(error=>{console.error(error.message||error);process.exit(1)});
