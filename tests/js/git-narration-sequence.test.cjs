const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {chromium}=require('../../target/ui-tests/node_modules/playwright-core');

test('the next shell command waits until the current output explanation finishes',async()=>{
 const browser=await chromium.launch({headless:true});
 try {
  const page=await browser.newPage();
  await page.setContent('<article class="repository-task"><div id="git-demo-terminal"></div></article>');
  const actions=JSON.parse(fs.readFileSync('courses/redesigned/git-first.json','utf8')).tasks[0].narration;
  await page.evaluate(()=>{
   window.commands=[];window.held=null;let output='$ ';
   window.molipGitTutor={owner:'demo',command:async args=>{commands.push('git '+args.join(' '));return true}};
   window.mq3GitDemoTerminal={text:()=>output,typeCommand:async command=>{commands.push(command);output+=' '+command+'\n'+({pwd:'/tmp/work',ls:'','cat memo.txt':'첫 메모'}[command])+'\n$ ';return true}};
   window.molipVoice={name:'ko-KR-SunHiNeural',enabled:()=>true,rate:1.5,synthesize:async text=>text};
   window.Audio=class {
    constructor(text){this.text=text}
    play(){if(/^(경로가 나왔어요|목록을 확인했어요|첫 메모가 나와요)/.test(this.text))window.held=this;else setTimeout(()=>this.onended?.(),0);return Promise.resolve()}
    pause(){}
   };
  });
  await page.addScriptTag({content:fs.readFileSync('assets/layout/agent.js','utf8')});
  await page.evaluate(actions=>{window.finished=molipAgent.run(actions)},actions);
  for(const [prefix,commands] of [
   ['경로가 나왔어요',['pwd']],
   ['목록을 확인했어요',['pwd','ls']],
   ['첫 메모가 나와요',['pwd','ls','git init','echo "첫 메모" > memo.txt','cat memo.txt']],
  ]){
   await page.waitForFunction(prefix=>window.held?.text.startsWith(prefix),prefix);
   assert.deepEqual(await page.evaluate(()=>window.commands),commands);
   await page.evaluate(()=>{const clip=held;held=null;clip.onended()});
  }
  await page.evaluate(()=>finished);
  assert.deepEqual(await page.evaluate(()=>commands),['pwd','ls','git init','echo "첫 메모" > memo.txt','cat memo.txt','git status']);
 }finally{await browser.close()}
});
