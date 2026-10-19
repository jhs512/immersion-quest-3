const test=require('node:test');
const assert=require('node:assert/strict');
const path=require('node:path');
const fs=require('node:fs');
const os=require('node:os');
const cache=fs.mkdtempSync(path.join(os.tmpdir(),'mq3-browser-cache-'));
process.env.PLAYWRIGHT_BROWSERS_PATH=cache;
process.env.MQ3_PLAYWRIGHT=path.resolve('target/ui-tests/node_modules/playwright-core');
// Exercise the managed browser path even when Windows already has Edge.
process.env.MQ3_WEB_BROWSER_CHANNEL='chromium';
test('managed browser installs into an empty cache and runs an isolated page without Edge', {timeout:240000}, async(t)=>{
 t.after(()=>{
  const resolved=path.resolve(cache),temporary=path.resolve(os.tmpdir());
  assert.equal(path.dirname(resolved),temporary);
  assert.ok(path.basename(resolved).startsWith('mq3-browser-cache-'));
  fs.rmSync(resolved,{recursive:true,force:true,maxRetries:5,retryDelay:100});
 });
 assert.deepEqual(fs.readdirSync(cache),[]);
 const {prepareBrowser,launchBrowser}=require('../../assets/web-browser.cjs');
 const options=await prepareBrowser();
 assert.equal(options.headless,true);
 assert.equal(options.channel,undefined);
 const browser=await launchBrowser(options);
 try{
  const first=await browser.newContext();const page=await first.newPage();
  await page.setContent('<button onclick="this.textContent=Number(this.textContent)+1">0</button>');
  await page.locator('button').click();assert.equal(await page.locator('button').innerText(),'1');
  const second=await browser.newContext();const other=await second.newPage();
  await other.setContent('<button>0</button>');assert.equal(await other.locator('button').innerText(),'0');
  await first.close();await second.close();
 }finally{await browser.close();}
});
