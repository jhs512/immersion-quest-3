const test=require('node:test');const assert=require('node:assert/strict');const fs=require('node:fs');
const {chromium}=require('../target/ui-tests/node_modules/playwright-core');
test('an editor replacement during narration must stop the old edit without corrupting the new problem',async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 try {
  const page=await browser.newPage();
  await page.setContent('<textarea data-code-editor="java">int count = 12345;</textarea>');
  await page.addScriptTag({content:fs.readFileSync('assets/editor/editor.bundle.js','utf8')});
  await page.addScriptTag({content:fs.readFileSync('assets/layout/agent.js','utf8')});
  const result=await page.evaluate(async()=>{
   molipAgent.setVoice(false);let edits=0;
   const changed='class AnotherProblem {}';
   document.querySelector('textarea').addEventListener('input',()=>{if(++edits===2)queueMicrotask(()=>molipCodeEditors.setValue(changed));});
   const report=await molipAgent.run([{action:'patch_code',before:'12345',after:'67890'}]);
   return {report,code:molipCodeEditors.getValue(),changed};
  });
  assert.equal(result.code,result.changed);
  assert.match(result.report,/코드가 바뀌었어요/);
 } finally {await browser.close();}
});
