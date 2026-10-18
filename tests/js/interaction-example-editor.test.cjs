const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {chromium}=require('../../target/ui-tests/node_modules/playwright-core');

test('prepared example is read-only for the learner while tutor edits and ordinary editors still work',async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 try{
  const page=await browser.newPage();
  await page.setContent('<textarea data-code-editor="javascript" readonly>console.log(2);</textarea>');
  await page.addScriptTag({content:fs.readFileSync(process.env.MOLIP_TEST_EDITOR_BUNDLE||'assets/editor/editor.bundle.js','utf8')});
  await page.waitForSelector('.cm-content');
  assert.equal(await page.locator('.cm-content').getAttribute('contenteditable'),'false');
  await page.locator('.cm-content').click();await page.keyboard.type('student typing');
  assert.equal(await page.evaluate(()=>molipCodeEditors.getValue()),'console.log(2);');
  assert.equal(await page.evaluate(()=>molipCodeEditors.setValue('console.log(3);')),true);
  assert.equal(await page.evaluate(()=>molipCodeEditors.getValue()),'console.log(3);');
  await page.setContent('<textarea data-code-editor="javascript">console.log(2);</textarea>');
  await page.evaluate(()=>molipCodeEditors.sync());
  await page.locator('.cm-content').click();await page.keyboard.type('x');
  assert.match(await page.evaluate(()=>molipCodeEditors.getValue()),/x/);
 }finally{await browser.close();}
});
