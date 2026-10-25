const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {chromium,webkit}=require(path.resolve('target/ui-tests/node_modules/playwright-core'));
const markup='<div class="git-terminal-row" style="height:400px;flex:none"><div class="git-terminal">터미널</div><details open class="git-graph-panel"><summary>커밋 그래프</summary><div class="git-graph-body"><div class="git-graph-canvas"></div></div></details><div class="split-handle split-col split-git" role="separator" tabindex="0" aria-orientation="vertical" aria-label="터미널과 그래프 너비 조절"></div></div>';
for(const [name,engine] of Object.entries({chromium,webkit}))test(`${name}: Git terminal and graph align and share a persistent draggable divider`,async()=>{
 const browser=await engine.launch({headless:true});
 try{
  const page=await browser.newPage({viewport:{width:1200,height:800}});
  await page.route('https://mq.test/',route=>route.fulfill({body:'<!doctype html><html><body></body></html>',contentType:'text/html'}));
  await page.goto('https://mq.test/');
  const css=['app','repository-player','player-workspace','product-ui','git-graph','station'].map(name=>fs.readFileSync(`assets/${name}.css`,'utf8')).join('\n');
  await page.setContent(`<style>${css}</style><section class="repository-task" style="display:block;min-height:0"><div class="coding-pane">${markup}</div></section>`);
  await page.addScriptTag({path:path.resolve('assets/layout/split.js')});
  const boxes=()=>page.evaluate(()=>Object.fromEntries(['git-terminal','git-graph-panel','split-git'].map(key=>{const r=document.querySelector('.'+key).getBoundingClientRect();return [key,{top:r.top,bottom:r.bottom,width:r.width,left:r.left,right:r.right}]})));
  const before=await boxes();
  assert.equal(before['git-terminal'].top,before['git-graph-panel'].top,'top edges differ');
  assert.equal(before['git-terminal'].bottom,before['git-graph-panel'].bottom,'bottom edges differ');
  const h=await page.locator('.split-git').boundingBox();
  await page.mouse.move(h.x+h.width/2,h.y+h.height/2);await page.mouse.down();await page.mouse.move(h.x+h.width/2-100,h.y+h.height/2);await page.mouse.up();
  const dragged=await boxes();assert.ok(dragged['git-graph-panel'].width>before['git-graph-panel'].width+80,'drag did not resize the graph');
  await page.locator('.split-git').focus();await page.keyboard.press('ArrowRight');
  const keyed=await boxes();assert.ok(keyed['git-graph-panel'].width<dragged['git-graph-panel'].width,'keyboard divider failed');
  await page.locator('.coding-pane').evaluate((node,html)=>node.innerHTML=html,markup);
  await page.waitForTimeout(100);
  assert.ok(Math.abs((await boxes())['git-graph-panel'].width-keyed['git-graph-panel'].width)<2,'new terminal lost the saved split');
  await page.setViewportSize({width:700,height:800});await page.waitForTimeout(100);
  const narrow=await boxes();assert.ok(narrow['git-terminal'].width>=180&&narrow['git-graph-panel'].width>=160,'a pane became unusably narrow');
  assert.equal(narrow['git-terminal'].top,narrow['git-graph-panel'].top);assert.equal(narrow['git-terminal'].bottom,narrow['git-graph-panel'].bottom);
  await page.locator('.split-git').dblclick();
  assert.equal(await page.locator('.git-terminal-row').evaluate(node=>node.style.getPropertyValue('--git-graph-width')),'');
 }finally{await browser.close();}
});
