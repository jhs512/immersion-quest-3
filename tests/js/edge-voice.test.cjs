const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {chromium}=require('../../target/ui-tests/node_modules/playwright-core');
test('an Edge failure keeps the selected voice and a new playback retries it',async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 try{
  const page=await browser.newPage();await page.setContent('<section class="problem-pane">설명</section>');
  await page.evaluate(()=>{
   window.attempts=0;window.systemCalls=0;window.clips=[];
   window.fetch=async()=>++attempts===1?new Response('offline',{status:503}):new Response(new Blob(['mp3']),{headers:{'X-Molip-Engine':'edge-tts'}});
   speechSynthesis.speak=()=>systemCalls++;
   window.Audio=class{constructor(){clips.push(this)}play(){setTimeout(()=>this.onended(),10);return Promise.resolve()}pause(){}};
  });
  await page.addScriptTag({content:fs.readFileSync('assets/speech/pronunciation.js','utf8')});
  for(const file of ['voice.js','agent.js'])await page.addScriptTag({content:fs.readFileSync(`assets/layout/${file}`,'utf8')});
  await page.evaluate(()=>molipAgent.run([{action:'say',text:'음성을 확인해요.'}]));
  assert.equal(await page.evaluate(()=>systemCalls),0,'do not change the chosen voice to the system voice');
  await page.evaluate(()=>molipAgent.run([{action:'say',text:'음성을 확인해요.'}]));
  assert.equal(await page.evaluate(()=>clips.length),1,'retry the Edge service on the next playback');
  assert.equal(await page.evaluate(()=>molipAgent.lastSpeech),'neural');
 }finally{await browser.close()}
});
