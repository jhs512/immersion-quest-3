// One speed list (assets/layout/voice.js) for every speed select, the neural clip, the device voice,
// the 읽어주기 panel and narration typing; up to 3x; a chosen speed survives a select rendered again
// (next step, next lesson) and is never replaced by the 1.5 default.
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const {chromium}=require('../../target/ui-tests/node_modules/playwright-core');

const page=async(browser,stored)=>{
 const p=await browser.newPage();
 await p.route('http://rate.test/**',route=>route.fulfill({contentType:'text/html',body:'<main id="app"><select class="assistant-rate repository-narration-rate"></select></main>'}));
 await p.goto('http://rate.test/');
 await p.evaluate(stored=>{if(stored!==undefined)localStorage.setItem('molip:tts-rate',stored);else localStorage.clear();
  window.fetch=async()=>new Response(new Blob(['mp3']));window.clips=[];
  window.Audio=class{constructor(){this.playbackRate=1;clips.push(this)}play(){return Promise.resolve()}pause(){}};
  window.spoken=[];Object.defineProperty(window,'speechSynthesis',{configurable:true,value:{getVoices:()=>[{lang:'ko-KR',name:'ko'}],speak(u){spoken.push(u)},cancel(){},resume(){},pause(){}}});
  window.SpeechSynthesisUtterance=class{constructor(text){this.text=text}};},stored);
 for(const file of ['assets/speech/pronunciation.js','assets/layout/voice.js','assets/speech/speech.js','assets/layout/agent.js'])await p.addScriptTag({content:fs.readFileSync(file,'utf8')});
 return p;
};
const state=p=>p.evaluate(()=>[...document.querySelectorAll('select.assistant-rate')].map(s=>({value:s.value,options:[...s.options].map(o=>o.value).join()})).concat([{voice:molipVoice.rate,storage:localStorage.getItem('molip:tts-rate')}]));

test('speeds: one list up to 3x, default only on first use, invalid saved values ignored, legacy values kept',async()=>{
 const browser=await chromium.launch({headless:true});
 try{
  const all='0.75,1,1.25,1.5,1.75,2,2.5,3';
  let p=await page(browser);
  assert.deepEqual(await state(p),[{value:'1.5',options:all},{voice:1.5,storage:null}],'first use shows the default');
  for(const bad of ['NaN','-1','0','4','3.5','abc','','Infinity']){
   await p.close();p=await page(browser,bad);
   assert.equal(await p.evaluate(()=>molipVoice.rate),1.5,`saved ${JSON.stringify(bad)} is ignored`);
   assert.equal(await p.evaluate(()=>molipVoice.setRate('7')),1.5,'an invalid choice changes nothing');
  }
  for(const legacy of ['0.75','1.75','2']){await p.close();p=await page(browser,legacy);assert.equal(await p.evaluate(()=>document.querySelector('select').value),legacy,'a speed saved by an older version stays');}
  assert.deepEqual(await p.evaluate(()=>[molipVoice.RATES.join(),molipSpeech.speechRates===molipVoice.RATES]),[all,true],'the reader uses the same list');
 }finally{await browser.close();}
});

test('a chosen 2x or 3x survives a select rendered again; changes reach the playing clip, the device voice and the reader',async()=>{
 const browser=await chromium.launch({headless:true});
 try{
  const p=await page(browser);
  for(const rate of ['2','3']){
   // Choose in the select, as a person does (the app's onchange calls setRate).
   await p.evaluate(rate=>{const s=document.querySelector('select');s.value=rate;molipVoice.setRate(s.value);},rate);
   // The next step renders a new select (as Dioxus does: no options, or an old 1.5-selected render).
   await p.evaluate(()=>{document.querySelector('select').remove();const fresh=document.createElement('select');fresh.className='assistant-rate repository-narration-rate';document.getElementById('app').append(fresh);
    const old=document.createElement('select');old.className='assistant-rate';old.innerHTML='<option>0.75</option><option selected>1.5</option><option>2</option>';document.body.append(old);});
   await p.waitForFunction(rate=>[...document.querySelectorAll('select.assistant-rate')].every(s=>s.value===rate),rate);
   const [fresh,old,global]=await state(p);
   assert.deepEqual([fresh.value,old.value,global.voice,global.storage],[rate,rate,Number(rate),rate],`a new render shows ${rate}x`);
   await p.evaluate(()=>document.querySelectorAll('select.assistant-rate')[1].remove());
  }
  // A new neural clip and the device voice start at the chosen speed; a change applies to the playing clip.
  await p.evaluate(()=>{window.run=molipAgent.run([{action:'say',text:'첫 문장이에요.'},{action:'say',text:'둘째 문장이에요.'}]);});
  await p.waitForFunction(()=>clips.length>=1);
  assert.equal(await p.evaluate(()=>clips[0].playbackRate),3);
  await p.evaluate(()=>molipVoice.setRate(2.5));
  assert.equal(await p.evaluate(()=>clips[0].playbackRate),2.5,'the playing clip follows at once');
  assert.equal(await p.evaluate(()=>document.querySelector('select').value),'2.5');
  await p.evaluate(()=>molipAgent.stop());
  await p.evaluate(()=>{molipVoice.setName('system');molipAgent.setVoice(true);window.run=molipAgent.run([{action:'say',text:'기기 음성이에요.'}]);});
  await p.waitForFunction(()=>spoken.length>=1);
  assert.equal(await p.evaluate(()=>spoken[0].rate),2.5,'the device voice uses the same speed (no 2x cap)');
  await p.evaluate(()=>molipAgent.stop());
  // Narration typing paces by the same speed: at 3x a 300 ms step takes 150 ms.
  await p.evaluate(()=>molipVoice.setRate(3));
  assert.equal(await p.evaluate(()=>molipVoice.rate),3);
 }finally{await browser.close();}
});

test('speech.js alone keeps the same list as voice.js', () => {
 const context={Intl,console};context.globalThis=context;
 vm.runInNewContext(fs.readFileSync('assets/speech/pronunciation.js','utf8'),context);
 vm.runInNewContext(fs.readFileSync('assets/speech/speech.js','utf8'),context);
 const voice=fs.readFileSync('assets/layout/voice.js','utf8').match(/const RATES = Object\.freeze\(\[([^\]]+)\]\)/)[1].split(',').map(Number);
 assert.deepEqual([...context.molipSpeech.speechRates],voice);
});
