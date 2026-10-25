const {test}=require('node:test');const assert=require('node:assert/strict');const fs=require('node:fs');
const {chromium,webkit}=require('../../target/ui-tests/node_modules/playwright-core');
const markup=`<div class="repository-session"><main class="repository-study is-task"><header class="repository-header"><h1>MQ · 자바 학습</h1><button data-shortcut-action="help" onclick="molipShortcuts.toggleSheet()">단축키</button></header>
<article class="lesson repository-task"><section class="problem-pane"><h2>기준 금액도 무료 배송일까요?</h2><p>배송비 조건을 고치고 결과를 비교하세요.</p><strong>할 일</strong><ol><li>수정 전 결과를 확인하세요.</li><li>비교 연산자를 고치세요.</li><li>실행한 뒤 제출하세요.</li></ol></section><div class="split-handle split-col"></div><section class="coding-pane"><div class="pane-heading"><strong>Main.java</strong><span class="submission-indicator">제출 실패</span><div class="pane-actions"><button>초기화</button><button data-shortcut-action="run">코드 실행</button><button class="primary" data-shortcut-action="submit">제출</button></div></div><div class="editor-pane"><pre>int amount = 10000;\nboolean free = amount > 10000;\nSystem.out.println(free);</pre></div><div class="split-handle split-row"></div><section class="result-pane" data-feedback="incorrect"><h3>실행·채점 결과</h3><div class="submission-feedback" role="alert"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="m9 9 6 6m0-6-6 6"/></svg><div><strong>제출 실패 · 다시 풀어보세요</strong><p>아래 검사에서 예상값과 실제 결과를 비교한 뒤 코드를 수정하세요.</p></div></div><p class="execution-status" role="status">다시 풀어보세요.</p><pre class="output">검사 1 · 다시 풀기\n예상: true\n결과: false</pre></section></section></article><div class="task-paging"><button data-shortcut-action="previous">← 이전 문제</button><span>문제 8 / 8</span><button data-shortcut-action="next" disabled>다음 문제 →</button></div></main></div>`;
for(const [name,engine] of Object.entries({chromium,webkit}))test(`${name}: red feedback stays readable and visible at desktop and narrow widths`,async()=>{
 const browser=await engine.launch({headless:true});try{
  const page=await browser.newPage();
  await page.setContent(`<style>${['app','repository-player','player-workspace','product-ui','station'].map(f=>fs.readFileSync(`assets/${f}.css`,'utf8')).join('\n')}</style>${markup}`);
  await page.addScriptTag({content:fs.readFileSync('assets/layout/shortcuts.js','utf8')});
  fs.mkdirSync('target/shortcut-feedback',{recursive:true});
  for(const width of [1280,720]){
   await page.setViewportSize({width,height:850});
   const values=await page.locator('.submission-feedback').evaluate(e=>{const s=getComputedStyle(e),r=e.getBoundingClientRect();return {fg:s.color,bg:s.backgroundColor,width:r.width,height:r.height,scroll:e.scrollWidth,client:e.clientWidth}});
   assert.equal(values.fg,'rgb(255, 182, 186)');assert.ok(values.width>150&&values.height>50);assert.ok(values.scroll<=values.client+1,'error text must wrap');
   assert.equal(await page.locator('.execution-status').evaluate(e=>getComputedStyle(e).color),values.fg,'status cannot stay green on failure');
   const luminance=c=>{const a=c.match(/\d+/g).slice(0,3).map(Number).map(x=>x/255).map(x=>x<=.04045?x/12.92:((x+.055)/1.055)**2.4);return a[0]*.2126+a[1]*.7152+a[2]*.0722};
   assert.ok((luminance(values.fg)+.05)/(luminance(values.bg)+.05)>=4.5,'failure text contrast');
   assert.ok(await page.locator('[data-shortcut-action=submit]').isVisible());
   await page.screenshot({path:`target/shortcut-feedback/${name}-${width}.png`,fullPage:true});
  }
  await page.locator('[data-shortcut-action=help]').click();await page.screenshot({path:`target/shortcut-feedback/${name}-help.png`,fullPage:true});
  await page.keyboard.press('Escape');await page.locator('.result-pane').evaluate(e=>e.dataset.feedback='passed');
  assert.notEqual(await page.locator('.execution-status').evaluate(e=>getComputedStyle(e).color),'rgb(255, 182, 186)');
 }finally{await browser.close();}
});
