const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {chromium,webkit}=require('../../target/ui-tests/node_modules/playwright-core');
for(const engine of ['chromium','webkit'])for(const form of ['NFC','NFD'])test(`${engine}/${form}: Korean composition reaches the terminal input bridge once`,async()=>{
 const browser=await({chromium,webkit}[engine]).launch(engine==='chromium'?{channel:'msedge',headless:true}:{headless:true,...(process.env.MQ3_WEBKIT_EXECUTABLE?{executablePath:process.env.MQ3_WEBKIT_EXECUTABLE}:{})});
 try{
  const page=await browser.newPage();await page.setContent('<div id="git-student-terminal" style="width:800px;height:400px"></div>');
  await page.addScriptTag({content:fs.readFileSync('assets/layout/ime.js','utf8')});
  assert.equal(await page.evaluate(()=>{
   const field=document.createElement('textarea');document.body.append(field);field.value='initial';
   field.dispatchEvent(new CompositionEvent('compositionstart',{bubbles:true}));field.value='stale render';
   const protectedValue=field.value;field.dispatchEvent(new CompositionEvent('compositionend',{bubbles:true}));
   field.value='committed';const restored=field.value;field.remove();return protectedValue==='initial'&&restored==='committed';
  }),true,'ordinary controlled inputs retain their composition protection');
  await page.addStyleTag({content:fs.readFileSync('assets/terminal/terminal.bundle.css','utf8')});
  await page.addScriptTag({content:fs.readFileSync('assets/terminal/terminal.bundle.js','utf8')});
  await page.evaluate(()=>{window.inputs=[];mq3GitTerminal.mount(e=>{if(e.kind==='input')inputs.push(e.data)},()=>{},'ime')});
  await page.keyboard.type('git commit -m "');
  for(const word of ['첫','기','록']){
   await page.evaluate(async word=>{
    const input=document.querySelector('.xterm-helper-textarea');
    input.dispatchEvent(new CompositionEvent('compositionstart',{bubbles:true,data:''}));
    input.value+=word;
    input.dispatchEvent(new CompositionEvent('compositionupdate',{bubbles:true,data:word}));
    input.dispatchEvent(new InputEvent('input',{bubbles:true,inputType:'insertCompositionText',data:word,isComposing:true}));
    await new Promise(r=>setTimeout(r,10));
    input.dispatchEvent(new CompositionEvent('compositionend',{bubbles:true,data:word}));
    await new Promise(r=>setTimeout(r,10));
   },word.normalize(form));
   if(word==='첫')await page.keyboard.press('Space');
  }
  await page.keyboard.type('"');await page.keyboard.press('Enter');
  assert.equal(await page.evaluate(()=>inputs.join('')),'git commit -m "첫 기록"\r');
 }finally{await browser.close()}
});
