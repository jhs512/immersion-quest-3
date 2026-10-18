const test=require('node:test');
const assert=require('node:assert/strict');
const path=require('node:path');
const {chromium}=require(path.resolve('target/ui-tests/node_modules/playwright-core'));
test('late writes, disposal and typing cannot cross a replaced real terminal session',async()=>{
  const browser=await chromium.launch({channel:'msedge',headless:true});
  try {
    const page=await browser.newPage();
    await page.setContent('<div id="git-student-terminal" style="width:800px;height:400px"></div>');
    await page.addStyleTag({path:path.resolve('assets/terminal/terminal.bundle.css')});
    await page.addScriptTag({path:path.resolve('assets/terminal/terminal.bundle.js')});
    const result=await page.evaluate(async()=>{
      const events=[];
      mq3GitTerminal.mount(event=>events.push(event),()=>{},'old');
      mq3GitTerminal.mount(event=>events.push(event),()=>{},'new');
      mq3GitTerminal.write(btoa('stale-output'),'old');
      mq3GitTerminal.dispose('old');
      const staleTyped=await mq3GitTerminal.typeCommand('stale-command','old');
      mq3GitTerminal.write(btoa('current-output'),'new');
      await new Promise(resolve=>setTimeout(resolve,50));
      const text=mq3GitTerminal.text('new');
      const currentTyped=await mq3GitTerminal.typeCommand('ok','new');
      return {text,staleTyped,currentTyped,inputs:events.filter(event=>event.kind==='input').map(event=>event.data).join('')};
    });
    assert.equal(result.staleTyped,false);assert.equal(result.currentTyped,true);
    assert.equal(result.text.trim(),'current-output');
    assert.equal(result.inputs,'ok'+String.fromCharCode(13));
  }finally{await browser.close();}
});
