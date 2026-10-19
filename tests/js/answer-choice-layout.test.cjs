const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {chromium}=require('../../target/ui-tests/node_modules/playwright-core');

test('choice labels remain visible beside radios and usable with prepared code',async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 try{
  const lesson=JSON.parse(fs.readFileSync('courses/redesigned/aice-python-start.json','utf8'));
  const find=value=>value&&typeof value==='object'?(value.title==='값에 이름을 붙여요'?value:Object.values(value).map(find).find(Boolean)):null;
  const task=find(lesson);assert.ok(task);
  const css=['assets/app.css',process.env.MOLIP_TEST_PLAYER_CSS||'assets/repository-player.css','assets/player-workspace.css'].map(file=>fs.readFileSync(file,'utf8')).join('\n');
  const page=await browser.newPage();
  for(const width of [1470,900,640]){
   await page.setViewportSize({width,height:900});
   await page.setContent(`<style>${css}</style><div class="repository-study"><div class="repository-task"><section class="problem-pane">값에 이름을 붙여요</section><div class="split-handle split-col"></div><section class="coding-pane"><div class="pane-heading">main.py</div><pre>${task.example_code}</pre><fieldset class="answer-interaction"><legend>답을 골라요</legend>${task.interaction.options.map(option=>`<label class="answer-option"><input type="radio" name="step-choice" value="${option.id}"><span>${option.text}</span></label>`).join('')}</fieldset></section></div></div>`);
   const layout=await page.locator('.answer-option').evaluateAll(options=>options.map(option=>{
    const row=option.getBoundingClientRect(),input=option.querySelector('input').getBoundingClientRect(),text=option.querySelector('span').getBoundingClientRect();
    return {row:{left:row.left,right:row.right},inputWidth:input.width,text:{left:text.left,right:text.right,width:text.width},scroll:option.scrollWidth,client:option.clientWidth};
   }));
   for(const row of layout){
    assert.ok(row.inputWidth<=24,`radio consumes the answer row at ${width}px: ${JSON.stringify(row)}`);
    assert.ok(row.text.width>0&&row.text.left>=row.row.left&&row.text.right<=row.row.right,`answer text outside option at ${width}px: ${JSON.stringify(row)}`);
    assert.ok(row.scroll<=row.client+1,`answer option scrolls horizontally at ${width}px`);
   }
   await page.getByText('18',{exact:true}).click();
   await page.locator('input[value=eighteen]').check();
   assert.equal(await page.locator('input[value=eighteen]').isChecked(),true);
   await page.locator('input[value=eighteen]').focus();await page.keyboard.press('ArrowUp');
   assert.equal(await page.locator('input[value=name]').isChecked(),true);
  }
 }finally{await browser.close();}
});
