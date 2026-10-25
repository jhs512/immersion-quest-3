const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {chromium,webkit}=require('../../target/ui-tests/node_modules/playwright-core');
const css=['app','repository-player','content-updates','player-workspace','window-controls','compact-toolbar','product-ui','station'].map(name=>fs.readFileSync(`assets/${name}.css`,'utf8')).join('\n');
const lum=color=>{const a=color.match(/[\d.]+/g).slice(0,3).map(Number).map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4);return a[0]*.2126+a[1]*.7152+a[2]*.0722};
const contrast=(a,b)=>(Math.max(lum(a),lum(b))+.05)/(Math.min(lum(a),lum(b))+.05);
for(const [name,engine] of Object.entries({chromium,webkit}))test(`${name}: route survives hover, titles are keyboard controls and pass check is legible across themes`,async()=>{
 const browser=await engine.launch({headless:true});
 try{
  const page=await browser.newPage();
  await page.setContent(`<style>${css}</style><div class="repository-player"><main class="course-main"><ol class="repository-lessons">${[1,2,3].map(n=>`<li class="card lesson-card" data-next="false" data-state="todo"><span class="lesson-number">${n}</span><div class="lesson-card-heading"><h3><button type="button" class="lesson-title" onclick="window.opened=(window.opened||0)+1">수업 ${n} · 배열과 반복으로 합계를 구해요</button></h3></div><div class="lesson-actions"><button>수업 링크 복사</button><button class="primary">학습 시작</button></div></li>`).join('')}</ol></main></div><div class="task-passed-dialog"><div class="task-passed-icon" aria-hidden="true"><svg viewBox="0 0 24 24" width="30" height="30" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12 4 4L19 6"/></svg></div><h2>통과했어요!</h2></div>`);
  fs.mkdirSync('target/catalog-affordances',{recursive:true});
  for(const theme of ['light','dark'])for(const width of [1280,640]){
   await page.setViewportSize({width,height:760});
   await page.evaluate(theme=>document.documentElement.dataset.themeChoice=theme,theme);
   await page.mouse.move(width-2,2);
   const row=page.locator('.lesson-card').nth(1),box=await row.boundingBox(),ring=await row.locator('.lesson-number').boundingBox();
   const clip={x:Math.floor(ring.x+ring.width/2),y:Math.round(box.y+3),width:1,height:3};
   const before=await page.screenshot({clip});
   await row.hover();
   const after=await page.screenshot({clip});
   assert.deepEqual(after,before,`${theme}/${width}: hover erases the route above the station`);
   const icon=await page.locator('.task-passed-icon').evaluate(e=>{const s=getComputedStyle(e),svg=e.querySelector('svg'),b=svg.getBoundingClientRect();return {fg:s.color,bg:s.backgroundColor,stroke:getComputedStyle(svg).stroke,width:b.width,height:b.height}});
   assert.equal(icon.bg,theme==='dark'?'rgb(23, 54, 39)':'rgb(228, 243, 234)','actual theme must be applied');
   assert.ok(contrast(icon.fg,icon.bg)>=4.5,`${theme}: check contrast ${contrast(icon.fg,icon.bg)}`);
   assert.equal(icon.stroke,icon.fg);assert.ok(icon.width>=28&&icon.height>=28);
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,'catalog cannot overflow');
   await page.screenshot({path:`target/catalog-affordances/${name}-${theme}-${width}.png`,fullPage:true});
  }
  const title=page.locator('.lesson-title').first();
  await title.focus();await page.keyboard.press('Enter');await page.keyboard.press('Space');
  assert.equal(await page.evaluate(()=>window.opened),2,'native button activates with Enter and Space');
  await title.evaluate(e=>e.disabled=true);await title.click({force:true});
  assert.equal(await page.evaluate(()=>window.opened),2,'disabled title cannot start a lesson');
 }finally{await browser.close();}
});
