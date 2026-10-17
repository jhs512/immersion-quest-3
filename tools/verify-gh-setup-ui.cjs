// Exercise our app's embedded terminal without changing the user's gh login.
const {chromium}=require('../target/ui-tests/node_modules/playwright-core');
const assert=require('node:assert/strict');
const fs=require('node:fs');
(async()=>{
 const browser=await chromium.connectOverCDP('http://127.0.0.1:9229');
 const page=browser.contexts()[0].pages()[0];page.setDefaultTimeout(30000);
 const output=()=>page.locator('.xterm-screen').innerText();
 await page.getByRole('button',{name:'2 · GitHub 로그인',exact:true}).waitFor();
 await page.waitForFunction(()=>document.querySelector('.xterm-screen')?.innerText.includes('PS '));
 const viewport=await page.evaluate(()=>({width:innerWidth,height:innerHeight}));
 const box=await page.locator('.gh-setup-card').boundingBox();
 assert.ok(Math.abs(box.x+box.width/2-viewport.width/2)<3,'center the whole setup horizontally');
 assert.ok(box.y>0&&box.y+box.height<viewport.height,'desktop setup should fit inside viewport');
 const input=page.getByRole('textbox',{name:'설정 터미널 입력',exact:true});
 await input.pressSequentially("Write-Output ('MQ3-' + 'TERMINAL-OK')");await input.press('Enter');
 await page.waitForFunction(()=>document.querySelector('.xterm-screen').innerText.includes('MQ3-TERMINAL-OK'));
 await input.pressSequentially('gh --version');await input.press('Enter');
 await page.waitForFunction(()=>document.querySelector('.xterm-screen').innerText.includes('gh version'));
 fs.mkdirSync('target/gh-setup-ui',{recursive:true});
 await page.screenshot({path:'target/gh-setup-ui/desktop.png'});
 await page.setViewportSize({width:640,height:800});
 await page.waitForFunction(()=>document.documentElement.scrollWidth<=innerWidth);
 assert.ok((await output()).includes('gh version'));
 await page.screenshot({path:'target/gh-setup-ui/compact.png'});
 await page.setViewportSize(viewport);
 // Verify that reconnect succeeds with the existing login and unmounts the terminal.
 await page.getByRole('button',{name:'준비 완료 · 연결 확인',exact:true}).click();
 await page.locator('.course-sidebar').waitFor({timeout:60000});
 assert.equal(await page.locator('#gh-setup-terminal').count(),0);
 console.log('PASS centered setup, actual shell input/output, gh execution, resize, and reconnect cleanup; login unchanged');
 await browser.close();
})().catch(error=>{console.error(error);process.exit(1)});
