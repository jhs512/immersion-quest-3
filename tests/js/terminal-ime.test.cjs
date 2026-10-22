const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {chromium,webkit}=require('../../target/ui-tests/node_modules/playwright-core');
for(const [name,engine] of Object.entries({chromium,webkit}))test(`${name}: native Korean finalization with a space does not duplicate a handled Space key`,async()=>{
 const browser=await engine.launch({headless:true});
 try{
  const page=await browser.newPage();await page.setContent('<div id="git-student-terminal" style="width:800px;height:400px"></div>');
  await page.addScriptTag({content:fs.readFileSync('assets/terminal/terminal.bundle.js','utf8')});
  await page.evaluate(()=>{window.inputs=[];mq3GitTerminal.mount(e=>{if(e.kind==='input')inputs.push(e.data)},()=>{},'space-finalize')});
  await page.keyboard.type('echo "');
  await page.evaluate(async()=>{
   const input=document.querySelector('.xterm-helper-textarea');
   const edit=async(type,value)=>{
    input.dispatchEvent(new InputEvent('beforeinput',{bubbles:true,inputType:type,data:value}));
    input.value=value;
    input.dispatchEvent(new InputEvent('input',{bubbles:true,inputType:type,data:value}));
    await new Promise(r=>setTimeout(r,10));
   };
   await edit('insertText','ㅊ');await edit('insertReplacementText','첫');
   // Some unmarked native IMEs commit their previous syllable plus the separator
   // after xterm has already handled the ordinary Space keydown.
   input.dispatchEvent(new KeyboardEvent('keydown',{bubbles:true,key:' ',code:'Space',keyCode:32}));
   await edit('insertReplacementText','첫 ');
   input.dispatchEvent(new KeyboardEvent('keyup',{bubbles:true,key:' ',code:'Space',keyCode:32}));
  });
  await page.keyboard.type('memo"');await page.keyboard.press('Enter');
  const line=await page.evaluate(()=>{const out=[];for(const c of inputs.join('')){if(c==='\x7f')out.pop();else out.push(c)}return out.join('')});
  assert.equal(line,'echo "첫 memo"\r');
 }finally{await browser.close();}
});
for(const engine of ['chromium','webkit'])for(const form of ['NFC','NFD'])for(const nativeKeys of [false,true])test(`${engine}/${form}/${nativeKeys?'native-keycodes':'composition-only'}: Korean composition reaches the terminal input bridge once`,async()=>{
 const browser=await({chromium,webkit}[engine]).launch(engine==='chromium'?{...(process.platform==='win32'?{channel:'msedge'}:{}),headless:true}:{headless:true,...(process.env.MQ3_WEBKIT_EXECUTABLE?{executablePath:process.env.MQ3_WEBKIT_EXECUTABLE}:{})});
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
   await page.evaluate(async ({word,nativeKeys})=>{
    const input=document.querySelector('.xterm-helper-textarea');
    const prefix=input.value;
    input.dispatchEvent(new CompositionEvent('compositionstart',{bubbles:true,data:''}));
    if(nativeKeys){
     input.value=prefix+'ㅎ';
     input.dispatchEvent(new CompositionEvent('compositionupdate',{bubbles:true,data:'ㅎ'}));
     await new Promise(r=>setTimeout(r,10));
     input.dispatchEvent(new KeyboardEvent('keydown',{bubbles:true,key:'k',keyCode:75,isComposing:true}));
    }
    input.value=prefix+word;
    input.dispatchEvent(new CompositionEvent('compositionupdate',{bubbles:true,data:word}));
    input.dispatchEvent(new InputEvent('input',{bubbles:true,inputType:'insertCompositionText',data:word,isComposing:true}));
    await new Promise(r=>setTimeout(r,10));
    input.dispatchEvent(new CompositionEvent('compositionend',{bubbles:true,data:word}));
    await new Promise(r=>setTimeout(r,10));
   },{word:word.normalize(form),nativeKeys});
   if(word==='첫')await page.keyboard.press('Space');
  }
  await page.keyboard.type('"');await page.keyboard.press('Enter');
  assert.equal(await page.evaluate(()=>inputs.join('')),'git commit -m "첫 기록"\r');
 }finally{await browser.close()}
});

// Recorded from the macOS two-set input source in the native WKWebView:
// insertText(ㅎ), insertReplacementText(하), insertReplacementText(한), ...
// No compositionstart/end and isComposing is false throughout.
for(const engine of ['chromium','webkit'])for(const form of ['NFC','NFD'])test(`${engine}/${form}: native Korean replacement edits reach Readline`,async()=>{
 const browser=await({chromium,webkit}[engine]).launch(engine==='chromium'?{...(process.platform==='win32'?{channel:'msedge'}:{}),headless:true}:{headless:true,...(process.env.MQ3_WEBKIT_EXECUTABLE?{executablePath:process.env.MQ3_WEBKIT_EXECUTABLE}:{})});
 try{
  const page=await browser.newPage();
  await page.setContent('<div id="git-student-terminal" style="width:800px;height:400px"></div>');
  for(const file of ['assets/layout/ime.js','assets/terminal/terminal.bundle.js'])await page.addScriptTag({content:fs.readFileSync(file,'utf8')});
  await page.evaluate(()=>{window.inputs=[];mq3GitTerminal.mount(e=>{if(e.kind==='input')inputs.push(e.data)},()=>{},'native-ime')});
  await page.keyboard.type('git commit -m "');
  await page.evaluate(async form=>{
   const input=document.querySelector('.xterm-helper-textarea');
   const prefix=input.value;
   let previous='';
   for(const [type,word] of [['insertText','ㅎ'],['insertReplacementText','하'],['insertReplacementText','한'],['insertReplacementText','한'],['insertText','한ㄱ'],['insertReplacementText','한그'],['insertReplacementText','한글'],['insertReplacementText','한그'],['insertReplacementText','한글'],['insertReplacementText','한글']]){
    // Include an IME backspace (한글 → 한그 → 한글) and repeated finalization.
    const value=word.normalize(form),data=(type==='insertText'?value.slice(previous.length):value).normalize(form);
    input.dispatchEvent(new InputEvent('beforeinput',{bubbles:true,composed:true,inputType:type,data,isComposing:false}));
    input.value=prefix+value;
    input.dispatchEvent(new InputEvent('input',{bubbles:true,composed:true,inputType:type,data,isComposing:false}));
    input.dispatchEvent(new KeyboardEvent('keydown',{bubbles:true,key:data,keyCode:229,isComposing:false}));
    previous=value;
    await new Promise(r=>setTimeout(r,10));
   }
  },form);
  await page.keyboard.press('Space');await page.keyboard.type('ok"');await page.keyboard.press('Enter');
  const stream=await page.evaluate(()=>inputs.join(''));
  // Interpret Readline's erase-character bytes, including edits of decomposed Hangul.
  const line=[];for(const character of stream){if(character==='\x7f')line.pop();else line.push(character);}
  assert.equal(line.join(''),'git commit -m "한글 ok"\r');
 }finally{await browser.close()}
});

for(const engine of ['chromium','webkit'])test(`${engine}: starting native Korean cannot erase the opening quote`,async()=>{
 const browser=await({chromium,webkit}[engine]).launch(engine==='chromium'?{...(process.platform==='win32'?{channel:'msedge'}:{}),headless:true}:{headless:true,...(process.env.MQ3_WEBKIT_EXECUTABLE?{executablePath:process.env.MQ3_WEBKIT_EXECUTABLE}:{})});
 try{
  const page=await browser.newPage();
  await page.setContent('<div id="git-student-terminal" style="width:800px;height:400px"></div>');
  for(const file of ['assets/layout/ime.js','assets/terminal/terminal.bundle.js'])await page.addScriptTag({content:fs.readFileSync(file,'utf8')});
  await page.evaluate(()=>{window.inputs=[];mq3GitTerminal.mount(e=>{if(e.kind==='input')inputs.push(e.data)},()=>{},'quote-ime')});
  await page.keyboard.type('echo "');
  await page.evaluate(async()=>{
   const input=document.querySelector('.xterm-helper-textarea');
   // xterm keeps the last ASCII key in its helper textarea. A native IME can
   // replace that helper value at the start of an unmarked Korean composition.
   for(const [type,text] of [['insertText','ㅊ'],['insertReplacementText','처'],['insertReplacementText','첫']]){
    input.dispatchEvent(new InputEvent('beforeinput',{bubbles:true,composed:true,inputType:type,data:text}));
    input.value=text;
    input.dispatchEvent(new InputEvent('input',{bubbles:true,composed:true,inputType:type,data:text}));
    input.dispatchEvent(new KeyboardEvent('keydown',{bubbles:true,key:text,keyCode:229}));
    await new Promise(r=>setTimeout(r,10));
   }
  });
  await page.keyboard.press('Space');
  await page.evaluate(async()=>{
   const input=document.querySelector('.xterm-helper-textarea');
   for(const [type,text,data] of [['insertText','ㅁ','ㅁ'],['insertReplacementText','메','메'],['insertText','메ㅁ','ㅁ'],['insertReplacementText','메모','메모']]){
    input.dispatchEvent(new InputEvent('beforeinput',{bubbles:true,composed:true,inputType:type,data}));
    input.value=text;
    input.dispatchEvent(new InputEvent('input',{bubbles:true,composed:true,inputType:type,data}));
    input.dispatchEvent(new KeyboardEvent('keydown',{bubbles:true,key:data,keyCode:229}));
    await new Promise(r=>setTimeout(r,10));
   }
  });
  await page.keyboard.type('"');await page.keyboard.press('Enter');
  const stream=await page.evaluate(()=>inputs.join(''));
  const line=[];for(const character of stream){if(character==='\x7f')line.pop();else line.push(character);}
  assert.equal(line.join(''),'echo "첫 메모"\r');
 }finally{await browser.close()}
});

for(const engine of ['chromium','webkit'])test(`${engine}: keyboard nonbreaking spaces cannot become hidden filename prefixes`,async()=>{
 const browser=await({chromium,webkit}[engine]).launch(engine==='chromium'?{...(process.platform==='win32'?{channel:'msedge'}:{}),headless:true}:{headless:true,...(process.env.MQ3_WEBKIT_EXECUTABLE?{executablePath:process.env.MQ3_WEBKIT_EXECUTABLE}:{})});
 try{
  const page=await browser.newPage();await page.setContent('<div id="git-student-terminal" style="width:800px;height:400px"></div>');
  await page.addScriptTag({content:fs.readFileSync('assets/terminal/terminal.bundle.js','utf8')});
  await page.evaluate(()=>{window.inputs=[];mq3GitTerminal.mount(e=>{if(e.kind==='input')inputs.push(e.data)},()=>{},'space-ime')});
  await page.keyboard.type('echo "memo" >');
  await page.evaluate(()=>{
   const input=document.querySelector('.xterm-helper-textarea');
   input.dispatchEvent(new InputEvent('beforeinput',{bubbles:true,inputType:'insertText',data:'\u00a0'}));
   input.value+='\u00a0';
   input.dispatchEvent(new InputEvent('input',{bubbles:true,inputType:'insertText',data:'\u00a0'}));
  });
  await page.keyboard.type('memo.txt');await page.keyboard.press('Enter');
  assert.equal(await page.evaluate(()=>inputs.join('')),'echo "memo" > memo.txt\r');
  const paste=await page.evaluate(()=>{
   inputs=[];
   const input=document.querySelector('.xterm-helper-textarea');
   const clipboardData=new DataTransfer();clipboardData.setData('text/plain','echo "a\u00a0b" >\u00a0memo.txt');
   input.dispatchEvent(new ClipboardEvent('paste',{bubbles:true,clipboardData}));
   return inputs.join('');
  });
  assert.ok(paste.includes('a b'),'pasted nonbreaking spaces become ordinary spaces');
  assert.ok(paste.includes('> memo.txt'),'pasted filename separators cannot become filename prefixes');
  assert.ok(!paste.includes('\u00a0'));
 }finally{await browser.close()}
});
