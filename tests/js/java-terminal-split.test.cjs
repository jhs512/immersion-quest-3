const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {chromium,webkit}=require('../../target/ui-tests/node_modules/playwright-core');
const markup='<div class="git-terminal-shell java-build-workspace"><div class="java-build-source"><strong>Main.java · 같은 폴더에 자동 저장</strong><div class="python-editor-host"><div class="cm-editor">Java editor</div></div></div><div class="split-handle split-row split-java-source" role="separator" tabindex="0" aria-orientation="horizontal" aria-label="에디터와 터미널 높이 조절"></div><div class="git-terminal-row"><div class="git-terminal">Terminal</div></div></div>';
for(const [name,engine] of Object.entries({chromium,webkit}))test(`${name}: Java editor and terminal have an independent persistent height divider`,async()=>{
 const browser=await engine.launch(name==='chromium'&&process.platform==='win32'?{channel:'msedge',headless:true}:{headless:true});
 try{
  const page=await browser.newPage({viewport:{width:1200,height:900}});
  await page.route('https://mq.test/',route=>route.fulfill({body:'<!doctype html><html><body></body></html>',contentType:'text/html'}));await page.goto('https://mq.test/');
  const styles=['app','repository-player','player-workspace','product-ui','git-graph','station'].map(key=>fs.readFileSync(`assets/${key}.css`,'utf8')).join('\n');
  await page.setContent(`<style>${styles}</style><section class="repository-task" style="display:block;min-height:0"><p class="prediction-run-note">예상 보기를 먼저 하나 고르면 실행할 수 있어요.</p><div class="editor-pane" style="height:500px;padding:0">${markup}</div></section>`);
  await page.addScriptTag({path:path.resolve('assets/layout/split.js')});
  const padding=await page.locator('.prediction-run-note').evaluate(node=>{const s=getComputedStyle(node);return {left:parseFloat(s.paddingLeft),right:parseFloat(s.paddingRight),top:parseFloat(s.paddingTop),bottom:parseFloat(s.paddingBottom)}});
  assert.ok(padding.left>=16&&padding.right>=16&&padding.top>=8&&padding.bottom>=8,'prediction instructions touch the panel border');
  const source=page.locator('.java-build-source'),handle=page.locator('.split-java-source');
  const height=async()=>Math.round((await source.boundingBox()).height);
  const before=await height();const bar=await handle.boundingBox();
  await page.mouse.move(bar.x+bar.width/2,bar.y+bar.height/2);await page.mouse.down();await page.mouse.move(bar.x+bar.width/2,bar.y+bar.height/2+75);await page.mouse.up();
  assert.ok((await height())>=before+65,'the actual Java source pane did not grow');
  await handle.focus();const dragged=await height();await page.keyboard.press('ArrowUp');assert.ok((await height())<dragged,'arrow key did not adjust the source pane');
  const keyed=await height();await page.locator('.editor-pane').evaluate((node,html)=>node.innerHTML=html,markup);await page.waitForTimeout(80);assert.ok(Math.abs((await height())-keyed)<=1,'remount lost the stored Java split');
  await page.locator('.editor-pane').evaluate(node=>node.style.height='280px');await page.waitForTimeout(80);
  assert.ok((await page.locator('.git-terminal-row').boundingBox()).height>=110,'terminal lost its minimum usable height');
  await handle.dblclick();assert.equal(await page.locator('.java-build-workspace').evaluate(node=>node.style.getPropertyValue('--java-source-height')),'');
  assert.ok(!await page.evaluate(()=>Object.hasOwn(JSON.parse(localStorage.getItem('molip:split')),'editor')),'inner divider changed the outer editor/result split');
  assert.match(fs.readFileSync('src/git_terminal_ui.rs','utf8'),/class:"split-handle split-row split-java-source"/,'native Java workspace is missing the divider');
 }finally{await browser.close()}
});
