// Native speech check: the app's own pronunciation, Edge neural request (molip://tts → src/tts.rs) and
// device voice (speechSynthesis) for the reported Java examples. Checks the text each voice receives and
// that each voice produced audio or speech events; it does not judge how the audio sounds.
(async()=>{
 const checked=[],samples=[
  ['`javac Main.java`로 컴파일해요.','자바 씨 메인 점 자바로 컴파일해요.'],
  ['방금 만든 Main.class를 java Main으로 실행해요.','방금 만든 메인 점 클래스를 자바 메인으로 실행해요.'],
  ['오류가 없으면 javac는 조용히 끝나요.','오류가 없으면 자바 씨는 조용히 끝나요.'],
  ['**결정 트리**(`DecisionTreeClassifier`)는 스무고개예요.','결정 트리(디시전 트리 클래시파이어)는 스무고개예요.'],
 ];
 const wait=async(fn,label,ms=30000)=>{const end=Date.now()+ms;while(Date.now()<end){if(fn())return;await new Promise(r=>setTimeout(r,50));}throw Error('Timed out: '+label);};
 const neural=[],device=[];
 try{
  await wait(()=>window.molipPronunciation&&window.molipVoice,'speech modules');
  for(const [source,expected] of samples){
   const spoken=molipPronunciation.pronunciationText(source);
   if(spoken!==expected)throw Error(`spoken text: ${source} → ${spoken}`);
  }
  checked.push('app pronunciation module gives the expected speech text');
  molipVoice.setName('ko-KR-SunHiNeural');
  for(const [source,expected] of samples){
   const url=await molipVoice.synthesize(source);
   if(!url)throw Error('neural voice returned no clip for '+source);
   const bytes=(await (await fetch(url)).arrayBuffer()).byteLength;
   neural.push({source,expected,bytes,engine:molipVoice.stats.lastEngine});
   if(bytes<2000)throw Error('clip too small: '+bytes);
  }
  checked.push('Edge neural clips downloaded through the app protocol');
  const voices=await new Promise(resolve=>{const list=speechSynthesis.getVoices();if(list.length)return resolve(list);speechSynthesis.onvoiceschanged=()=>resolve(speechSynthesis.getVoices());setTimeout(()=>resolve(speechSynthesis.getVoices()),3000);});
  const korean=voices.find(v=>/^ko/i.test(v.lang));
  if(!korean){checked.push('device voice: no Korean voice installed (skipped)');}
  else{
   for(const [source,expected] of samples.slice(0,2)){
    const text=molipPronunciation.pronunciationText(source);
    const events=await new Promise(resolve=>{
     const u=new SpeechSynthesisUtterance(text);u.voice=korean;u.lang=korean.lang;u.rate=2;u.volume=0;
     const seen={text,start:false,end:false,error:null,boundaries:0};
     u.onstart=()=>seen.start=true;u.onboundary=()=>seen.boundaries++;u.onend=()=>{seen.end=true;resolve(seen)};u.onerror=e=>{seen.error=e.error;resolve(seen)};
     speechSynthesis.speak(u);setTimeout(()=>resolve(seen),20000);
    });
    device.push({voice:korean.name,...events});
    if(!events.start||!events.end||events.error)throw Error('device voice did not speak: '+JSON.stringify(events));
   }
   checked.push('device Korean voice spoke the converted text (muted)');
  }
  dioxus.send({passed:true,checked,neural,device});
 }catch(error){dioxus.send({passed:false,checked,neural,device,error:String(error),stats:window.molipVoice?.stats});}
})();
