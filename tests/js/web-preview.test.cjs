const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const cp=require('node:child_process');
const {chromium}=require('../../target/ui-tests/node_modules/playwright-core');
const asset=file=>process.env.MQ3_TEST_BASELINE ? cp.execFileSync('git',['show',`HEAD:${file}`],{encoding:'utf8'}) : fs.readFileSync(file,'utf8');

test('web runner emits console messages, not rendered body text',async()=>{
  // Drive the real runner in an isolated directory, with the installed browser.
  const os=require('node:os'),path=require('node:path');
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'mq3-web-output-'));
  try {
    fs.writeFileSync(path.join(dir,'request.json'),JSON.stringify({entry:'index.html',checks:[]}));
    fs.writeFileSync(path.join(dir,'index.html'),'<p>NOT A CONSOLE MESSAGE</p><script>console.log("learner log", {count:2})</script>');
    fs.writeFileSync(path.join(dir,'web-runner.cjs'),asset('assets/web-runner.cjs'));
    fs.copyFileSync('assets/web-browser.cjs',path.join(dir,'web-browser.cjs'));
    const out=cp.execFileSync(process.execPath,['web-runner.cjs'],{cwd:dir,encoding:'utf8',env:{...process.env,MQ3_PLAYWRIGHT:path.resolve('target/ui-tests/node_modules/playwright-core')}});
    assert.doesNotMatch(out,/NOT A CONSOLE MESSAGE/);
    assert.match(out,/learner log/);
    fs.writeFileSync(path.join(dir,'index.html'),'<p>Only the preview should show this page</p>');
    const silent=cp.execFileSync(process.execPath,['web-runner.cjs'],{cwd:dir,encoding:'utf8',env:{...process.env,MQ3_PLAYWRIGHT:path.resolve('target/ui-tests/node_modules/playwright-core')}});
    assert.equal(silent,'','a page without logs has no console output');
  } finally {fs.rmSync(dir,{recursive:true,force:true});}
});

test('opaque web preview exposes real logs and highlights matching elements through narration and stop',async()=>{
  const browser=await chromium.launch({...(process.platform==='win32'?{channel:'msedge'}:{}),headless:true});
  try {
    const page=await browser.newPage({viewport:{width:1100,height:800},reducedMotion:'reduce'});
    await page.setContent('<article class="repository-task"><section class="result-pane" data-web-selectors=".card,#guide"></section></article>');
    await page.evaluate(()=>{
      window.messages=[];addEventListener('message',e=>{if(e.source===document.querySelector('iframe')?.contentWindow)messages.push(e.data)});
      window.clips=[];window.molipVoice={enabled:()=>true,rate:1.5,synthesize:async text=>'clip:'+text};
      window.Audio=class{constructor(){clips.push(this)}play(){return Promise.resolve()}pause(){}};
    });
    const html=`<script>${asset('assets/layout/web-bridge.js')}<\/script><style>.card{font-weight:700}</style><article class="card">첫 카드</article><article class="card">둘째 카드</article><p id="guide">안내</p><button onclick="console.log('clicked');console.warn('warning')">기록</button><script>console.log('initial');<\/script>`;
    await page.evaluate(src=>{let f=document.createElement('iframe');f.title='해설 웹 미리보기';f.sandbox='allow-scripts allow-forms';f.srcdoc=src;document.querySelector('.result-pane').append(f)},html);
    const frame=page.frameLocator('iframe');await frame.locator('button').waitFor();
    const request=()=>page.evaluate(()=>document.querySelector('iframe').contentWindow.postMessage({type:'mq3-web-console-request'},'*'));
    await request();
    await page.waitForFunction(()=>messages.some(m=>m.type==='mq3-web-console'&&m.lines.includes('[log] initial')));
    await frame.locator('button').click();
    await page.waitForFunction(()=>messages.some(m=>m.lines?.includes('[warn] warning')));
    assert.equal(await page.evaluate(()=>messages.at(-1).lines.some(s=>s.includes('첫 카드'))),false);
    await page.addScriptTag({content:asset('assets/layout/agent.js')});
    await page.evaluate(()=>{window.done=molipAgent.runExplanation([{action:'say',target:'web:.card',text:'카드 두 개가 굵어요.'},{action:'say',target:'web:#guide',text:'안내는 그대로예요.'}])});
    await page.waitForFunction(()=>clips.length===1);
    await frame.locator('[data-mq3-web-highlight]').first().waitFor();
    assert.equal(await frame.locator('[data-mq3-web-highlight]').count(),2);
    assert.equal(await page.locator('.agent-spotlight').isVisible(),false,'no frame around the whole iframe');
    const box=await frame.locator('[data-mq3-web-highlight]').first().boundingBox(),card=await frame.locator('.card').first().boundingBox();
    assert.ok(Math.abs(box.y-(card.y-3))<1);
    await page.evaluate(()=>clips.at(-1).onended());await page.waitForFunction(()=>clips.length===2);
    await page.waitForTimeout(100);
    assert.equal(await frame.locator('[data-mq3-web-highlight]').count(),1);
    await page.evaluate(()=>molipAgent.stop());await page.evaluate(()=>done);
    await page.waitForTimeout(100);
    assert.equal(await frame.locator('[data-mq3-web-highlight]').count(),0);
    assert.equal(await frame.locator('.card').first().evaluate(e=>getComputedStyle(e).fontWeight),'700');
  }finally{await browser.close();}
});
