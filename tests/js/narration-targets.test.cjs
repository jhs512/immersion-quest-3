// Precise narration targets: the exact problem sentence (text:구절#n) and the exact code token
// (code:토큰#n) are highlighted while the matching sentence is spoken, and nothing is left behind
// when the explanation ends, is stopped, or the task changes. Audio timing on a real device is a
// separate manual check; here a fake clip holds each sentence until the test ends it.
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {chromium}=require('../../target/ui-tests/node_modules/playwright-core');

const TASK=`<article class="repository-task" data-explanation-session="s1">
 <section class="problem-pane"><div class="problem-heading"><h2>무료배송 경계를 고치세요</h2></div>
  <div class="markdown"><p>주문 금액은 20000원이에요. 2만 원 이상이면 배송비가 0원이에요.</p>
   <p>지금 코드는 <code>&gt;</code>로 비교해요. 2만 원 이상이면 무료라는 규칙과 맞는지 보세요.</p>
   <ol><li>코드 실행을 누르세요.</li><li>비교 기호 하나를 고친 뒤 제출하세요.</li></ol></div></section>
 <textarea data-code-editor="java">int fee = amount &gt; 20000 ? 0 : 3000;
System.out.println(fee);
System.out.println(amount &gt; 20000);</textarea>
 <section class="result-pane"><pre class="output">3000</pre></section>
 <input type="hidden" class="answer-state-bridge" value="student-choice">
</article>`;

async function open(html=TASK) {
  const browser=await chromium.launch({...(process.platform==='win32'?{channel:'msedge'}:{}),headless:true});
  // Any failure while opening must still close the browser, or the test process never exits.
  try {
    // Reduced motion turns off the spotlight's .3s transition, so a measured frame is the final one.
    const page=await browser.newPage({viewport:{width:1100,height:800},reducedMotion:'reduce'});
    await page.setContent(html);
    await page.addScriptTag({content:fs.readFileSync('assets/editor/editor.bundle.js','utf8')});
    await page.addStyleTag({content:fs.readFileSync('assets/app.css','utf8')});
    await page.evaluate(()=>{
      window.clips=[];
      window.molipVoice={name:'ko-KR-SunHiNeural',enabled:()=>true,rate:1.5,synthesize:async text=>'clip:'+text};
      window.Audio=class{constructor(url){this.url=url;clips.push(this)}play(){return Promise.resolve()}pause(){}};
    });
    await page.addScriptTag({content:fs.readFileSync('assets/layout/agent.js','utf8')});
    // The editor is mounted once CodeMirror replaced the textarea; an empty editor (a theory step)
    // is mounted too, so wait for the mount, not for non-empty text.
    await page.waitForFunction(()=>typeof window.molipCodeEditors?.getValue==='function'&&document.querySelector('.cm-editor'),null,{timeout:10000});
    return {browser,page};
  } catch (error) {await browser.close();throw error;}
}
// The highlighted text range (CSS Custom Highlight API) and the editor's marked characters.
const state=page=>page.evaluate(()=>{
  const h=CSS.highlights.get('narration-text');
  const text=h?[...h].map(range=>range.toString()):[];
  const code=[...document.querySelectorAll('.cm-narration-span')].map(e=>e.textContent).join('');
  const lines=[...document.querySelectorAll('.cm-narration-line')].map(e=>e.textContent);
  const spot=document.querySelector('.agent-spotlight');
  return {text,code,lines,spotHidden:!spot||spot.hidden,clips:clips.length,caption:document.querySelector('.agent-caption')?.textContent};
});
const next=page=>page.evaluate(()=>clips.at(-1).onended());
// A bounded wait: a missing clip fails with a clear message well inside the per-test timeout.
const waitClips=(page,n)=>page.waitForFunction(n=>clips.length===n,n,{timeout:10000});

test('two sentences of one paragraph are highlighted one after the other, exactly',async()=>{
  const {browser,page}=await open();
  try {
    await page.evaluate(()=>{window.done=molipAgent.runExplanation([
      {action:'say',target:'text:주문 금액은 20000원이에요.',text:'주어진 금액은 이만 원이에요.'},
      {action:'say',target:'text:2만 원 이상이면 배송비가 0원이에요.',text:'이만 원 이상이면 무료라는 조건이에요.'},
    ])});
    await waitClips(page,1);
    let s=await state(page);
    assert.deepEqual(s.text,['주문 금액은 20000원이에요.']);
    assert.equal(s.spotHidden,false);
    const frame=await page.evaluate(()=>{const r=document.querySelector('.agent-spotlight').getBoundingClientRect();const p=document.querySelector('.markdown p').getBoundingClientRect();return {spot:r.width,paragraph:p.width}});
    assert.ok(frame.spot<frame.paragraph,'the frame covers the sentence, not the whole paragraph');
    await next(page);await waitClips(page,2);
    s=await state(page);
    assert.deepEqual(s.text,['2만 원 이상이면 배송비가 0원이에요.']);
    await next(page);await page.evaluate(()=>done);
    s=await state(page);
    assert.deepEqual(s.text,[],'no highlight remains after the explanation');
    assert.equal(s.spotHidden,true);
  } finally {await browser.close();}
});

test('a repeated phrase is chosen by #n and a phrase across inline code still matches',async()=>{
  const {browser,page}=await open();
  try {
    await page.evaluate(()=>{window.done=molipAgent.runExplanation([
      {action:'say',target:'text:2만 원 이상이면#2',text:'두 번째 문장의 규칙이에요.'},
      {action:'say',target:'text:지금 코드는 >로 비교해요.',text:'지금 비교 기호예요.'},
      {action:'say',target:'text:없는 구절이에요',text:'없는 구절이면 강조하지 않아요.'},
    ])});
    await waitClips(page,1);
    const second=await page.evaluate(()=>{const [r]=[...CSS.highlights.get('narration-text')];return {text:r.toString(),inSecondParagraph:document.querySelectorAll('.markdown p')[1].contains(r.startContainer)}});
    assert.deepEqual(second,{text:'2만 원 이상이면',inSecondParagraph:true});
    await next(page);await waitClips(page,2);
    assert.deepEqual((await state(page)).text,['지금 코드는 >로 비교해요.']);
    await next(page);await waitClips(page,3);
    const missing=await state(page);
    assert.deepEqual(missing.text,[],'a missing phrase leaves no stale highlight');
    await next(page);await page.evaluate(()=>done);
  } finally {await browser.close();}
});

test('code:token highlights the exact characters and line, and #n picks a later occurrence',async()=>{
  const {browser,page}=await open();
  try {
    await page.evaluate(()=>{window.done=molipAgent.runExplanation([
      {action:'say',target:'code:amount > 20000',text:'이 비교가 경계를 정해요.'},
      {action:'say',target:'code:amount > 20000#2',text:'아래 줄은 비교 결과를 그대로 보여 줘요.'},
      {action:'say',target:'text:주문 금액은 20000원이에요.',text:'다시 문제로 돌아와요.'},
    ])});
    await waitClips(page,1);
    let s=await state(page);
    assert.equal(s.code,'amount > 20000');
    assert.deepEqual(s.lines,['int fee = amount > 20000 ? 0 : 3000;']);
    await next(page);await waitClips(page,2);
    s=await state(page);
    assert.equal(s.code,'amount > 20000');
    assert.deepEqual(s.lines,['System.out.println(amount > 20000);']);
    await next(page);await waitClips(page,3);
    s=await state(page);
    assert.equal(s.code,'','moving to a text target clears the code span');
    assert.deepEqual(s.text,['주문 금액은 20000원이에요.']);
    await next(page);await page.evaluate(()=>done);
  } finally {await browser.close();}
});

test('stopping mid-sentence clears every highlight and restores the learner state',async()=>{
  const {browser,page}=await open();
  try {
    await page.evaluate(()=>{window.done=molipAgent.runExplanation([
      {action:'set_code',code:'int fee = amount >= 20000 ? 0 : 3000;\nSystem.out.println(fee);\nSystem.out.println(amount > 20000);'},
      {action:'say',target:'code:>=',text:'이상이면 같음도 포함해요.'},
      {action:'say',target:'text:주문 금액은 20000원이에요.',text:'끝까지 가지 않아요.'},
    ])});
    await waitClips(page,1);
    assert.equal((await state(page)).code,'>=');
    await page.evaluate(()=>molipAgent.stop());await page.evaluate(()=>done);
    const s=await state(page);
    assert.equal(s.code,'');assert.deepEqual(s.lines,[]);assert.deepEqual(s.text,[]);assert.equal(s.spotHidden,true);
    assert.equal(await page.evaluate(()=>molipCodeEditors.getValue()),'int fee = amount > 20000 ? 0 : 3000;\nSystem.out.println(fee);\nSystem.out.println(amount > 20000);');
    assert.equal(await page.evaluate(()=>document.querySelector('.answer-state-bridge').value),'student-choice');
  } finally {await browser.close();}
});

test('replacing the task while a sentence is highlighted leaves no stale range on the next task',async()=>{
  const {browser,page}=await open();
  try {
    await page.evaluate(()=>{window.done=molipAgent.runExplanation([
      {action:'say',target:'text:2만 원 이상이면 배송비가 0원이에요.',text:'조건이에요.'},
      {action:'say',target:'text:2만 원 이상이면 배송비가 0원이에요.',text:'다음 문장은 오지 않아요.'},
    ])});
    await waitClips(page,1);
    // Navigation: the session root changes owner, then the old explanation is stopped.
    await page.evaluate(()=>{document.querySelector('.repository-task').dataset.explanationSession='s2';molipAgent.stop();});
    await page.evaluate(()=>done);
    await page.evaluate(()=>{document.querySelector('.problem-pane .markdown').innerHTML='<p>다음 문제예요. 2만 원 이상이면 배송비가 0원이에요.</p>';});
    const s=await state(page);
    assert.deepEqual(s.text,[]);assert.equal(s.spotHidden,true);
  } finally {await browser.close();}
});

test('web_action clicks and types inside the sandboxed tutor preview and reads the changed screen',async()=>{
  const browser=await chromium.launch({...(process.platform==='win32'?{channel:'msedge'}:{}),headless:true});
  try {
    const page=await browser.newPage();
    const bridge=fs.readFileSync('assets/layout/web-bridge.js','utf8');
    const app=`<script>${bridge}<\/script><button>좋아요 0</button><input aria-label="글"><p id="echo"></p><script>
      let count=0;const b=document.querySelector('button');b.onclick=()=>{count++;b.textContent='좋아요 '+count};
      document.querySelector('input').addEventListener('input',e=>{document.querySelector('#echo').textContent=e.target.value});<\/script>`;
    await page.setContent('<article class="repository-task" data-explanation-session="w"><section class="result-pane"></section></article>');
    await page.evaluate(srcdoc=>{const f=document.createElement('iframe');f.title='해설 웹 미리보기';f.setAttribute('sandbox','allow-scripts allow-forms');f.srcdoc=srcdoc;document.querySelector('.result-pane').append(f);},app);
    await page.waitForFunction(()=>document.querySelector('iframe').contentWindow && document.readyState==='complete');
    await new Promise(r=>setTimeout(r,300));
    await page.addScriptTag({content:fs.readFileSync('assets/layout/agent.js','utf8')});
    const report=await page.evaluate(async()=>{molipAgent.setVoice(false);return molipAgent.runExplanation([
      {action:'web_action',do:'click',selector:'button'},
      {action:'web_action',do:'click',selector:'button'},
      {action:'web_action',do:'fill',selector:'input',value:'첫 글',read:'#echo'},
    ])});
    assert.match(report,/웹 화면: 좋아요 1/);
    assert.match(report,/웹 화면: 좋아요 2/);
    assert.match(report,/웹 화면: 첫 글/);
  } finally {await browser.close();}
});

test('web_action width resizes only the tutor preview so a min-width rule applies, and reads a computed style',async()=>{
  const browser=await chromium.launch({...(process.platform==='win32'?{channel:'msedge'}:{}),headless:true});
  try {
    const page=await browser.newPage({viewport:{width:1400,height:800}});
    const bridge=fs.readFileSync('assets/layout/web-bridge.js','utf8');
    const app=`<style>#cards{display:grid;grid-template-columns:1fr;width:320px}@media (min-width:768px){#cards{grid-template-columns:1fr 1fr}}</style><script>${bridge}<\/script><div id="cards"><article>시작</article><article>다음</article></div>`;
    await page.setContent('<article class="repository-task"><section class="result-pane"></section></article>');
    await page.evaluate(srcdoc=>{const f=document.createElement('iframe');f.title='해설 웹 미리보기';f.setAttribute('sandbox','allow-scripts allow-forms');f.srcdoc=srcdoc;f.style.width='100%';document.querySelector('.result-pane').append(f);},app);
    await new Promise(r=>setTimeout(r,400));
    await page.addScriptTag({content:fs.readFileSync('assets/layout/agent.js','utf8')});
    const report=await page.evaluate(async()=>{molipAgent.setVoice(false);return molipAgent.runExplanation([
      {action:'web_action',do:'width',value:360,selector:'#cards',style:'gridTemplateColumns'},
      {action:'web_action',do:'width',value:900,selector:'#cards',style:'gridTemplateColumns'},
    ])});
    assert.match(report,/웹 화면: 320px\n/);
    assert.match(report,/웹 화면: 160px 160px/);
  } finally {await browser.close();}
});

// A theory step: the given sentence (with authored line breaks), a duplicated phrase and two
// options inside the problem pane. Nothing here may be explained by framing the whole pane.
const CHOICE=`<article class="repository-task" data-explanation-session="s2">
 <section class="problem-pane"><div class="problem-heading"><h2>복합 키 일부에만 의존하는 값을 찾아요</h2></div>
  <div class="markdown"><p>상품명은
     상품만으로   정해져요. 상품명은 주문상품에 반복돼요.</p></div>
  <fieldset class="answer-interaction"><legend>어디로 옮길까요?</legend>
   <label class="answer-option" data-option-id="qty"><input type="radio" name="c" value="qty"><span>주문 표로 옮겨요</span></label>
   <label class="answer-option" data-option-id="item"><input type="radio" name="c" value="item"><span>상품 표로 분리해요</span></label>
  </fieldset></section>
 <textarea data-code-editor="python"></textarea>
 <section class="result-pane"><pre class="output"></pre></section>
 <input type="hidden" class="answer-state-bridge" value="qty">
</article>`;
const frame=page=>page.evaluate(()=>{const spot=document.querySelector('.agent-spotlight');if(!spot||spot.hidden)return null;
  const r=spot.getBoundingClientRect(),p=document.querySelector('.problem-pane').getBoundingClientRect();
  const item=document.querySelector('[data-option-id="item"]').getBoundingClientRect();
  return {width:r.width,height:r.height,pane:{width:p.width,height:p.height},item:{width:item.width,height:item.height}};});

test('theory narration frames the exact given, the exact option, or nothing - never the whole problem',async()=>{
  const {browser,page}=await open(CHOICE);
  try {
    await page.evaluate(()=>{window.done=molipAgent.runExplanation([
      {action:'say',target:'text:상품명은 상품만으로 정해져요.',text:'상품명은 상품에만 결정돼요.'},
      {action:'say',target:'text:상품명은#2',text:'두 번째 문장의 상품명이에요.'},
      {action:'say',target:'answer:item',text:'그래서 상품 표로 분리해요.'},
      {action:'say',text:'조심하세요. 선택한 주키 하나만 확인하지 않아요.'},
      {action:'say',target:'text:상품 표로 분리해요',text:'보기 글자는 문제 문장이 아니에요.'},
    ])});
    await waitClips(page,1);
    let s=await state(page);
    assert.deepEqual(s.text.map(t=>t.replace(/\s+/g,' ')),['상품명은 상품만으로 정해져요.'],'line breaks and runs of spaces in the DOM still match one sentence');
    let f=await frame(page);
    assert.ok(f&&f.width<f.pane.width&&f.height<f.pane.height,'the frame is the sentence, not the problem pane');
    await next(page);await waitClips(page,2);
    s=await state(page);
    assert.deepEqual(s.text,['상품명은']);
    assert.equal(await page.evaluate(()=>[...CSS.highlights.get('narration-text')][0].startContainer.data.includes('주문상품에')),true,'#2 picks the later occurrence');
    await next(page);await waitClips(page,3);
    s=await state(page);f=await frame(page);
    assert.deepEqual(s.text,[],'moving to an option clears the sentence range');
    assert.ok(f&&Math.abs(f.width-f.item.width)<=16&&Math.abs(f.height-f.item.height)<=16,'the frame is that one option: '+JSON.stringify(f));
    await next(page);await waitClips(page,4);
    s=await state(page);
    assert.equal(s.spotHidden,true,'a caption-only sentence frames nothing');
    assert.match(s.caption,/선택한 주키/);
    await next(page);await waitClips(page,5);
    s=await state(page);
    assert.deepEqual(s.text,[]);
    assert.equal(s.spotHidden,true,'an unmatched phrase does not fall back to the whole problem pane');
    await next(page);await page.evaluate(()=>done);
    s=await state(page);
    assert.equal(s.spotHidden,true);assert.deepEqual(s.text,[]);
    assert.equal(await page.evaluate(()=>document.querySelector('.answer-state-bridge').value),'qty','the learner choice is restored');
  } finally {await browser.close();}
});

// Readability of the exact highlights, measured on rendered pixels (Bash 파일과 폴더 · 문제 1 and the
// rmdir problem, dark theme). The sentence highlight used `color: inherit`, which kept the pale
// lesson text on the pale lilac and the sentence vanished. Both engines the app ships on are checked:
// WebKit (macOS WKWebView) and Chromium (Windows WebView2).
const BASH=`<article class="repository-task practice-shell" data-explanation-session="bash-1" style="background:#1d2a3a">
 <section class="problem-pane"><div class="problem-heading"><h2>현재 폴더를 확인하세요</h2></div>
  <div class="markdown"><p>파일이 없는 새 연습 폴더에서 시작해요. 이 수업에서는 파일과 현재 위치를 다음 단계에도 그대로 이어 써요.</p>
   <ol><li><code>pwd</code>: 현재 폴더의 경로를 확인하세요.</li></ol></div></section>
 <div style="height:160px"><textarea data-code-editor="shell">mkdir empty
rmdir empty</textarea></div>
 <div id="git-demo-terminal" style="height:120px;background:#171a33;color:#e6e6f0">$ pwd</div>
</article>`;
// Relative luminance and contrast ratio (WCAG 2).
const lum=([r,g,b])=>{const c=v=>{v/=255;return v<=.03928?v/12.92:((v+.055)/1.055)**2.4};return .2126*c(r)+.7152*c(g)+.0722*c(b)};
const contrast=(a,b)=>{const [x,y]=[lum(a),lum(b)].sort((p,q)=>q-p);return (x+.05)/(y+.05)};
// The pixels inside a rectangle of the rendered page: the most common color (the background) and
// the color that differs most from it (the glyph core).
async function swatch(page,rect){
  const png=await page.screenshot({clip:rect});
  const px=await page.evaluate(async b64=>{const img=new Image();img.src='data:image/png;base64,'+b64;await img.decode();
    const c=document.createElement('canvas');c.width=img.width;c.height=img.height;const g=c.getContext('2d');g.drawImage(img,0,0);
    return [...g.getImageData(0,0,c.width,c.height).data];},png.toString('base64'));
  const counts=new Map(),colors=[];
  for(let i=0;i<px.length;i+=4){const k=px[i]<<16|px[i+1]<<8|px[i+2];colors.push([px[i],px[i+1],px[i+2]]);counts.set(k,(counts.get(k)||0)+1);}
  const top=[...counts].sort((a,b)=>b[1]-a[1])[0][0],bg=[top>>16&255,top>>8&255,top&255];
  const fg=colors.reduce((best,c)=>contrast(c,bg)>contrast(best,bg)?c:best,bg);
  return {bg,fg,ratio:contrast(fg,bg),png};
}
// The rectangle of the current sentence range or of the marked code characters, shrunk off the frame.
const box=(page,kind)=>page.evaluate(kind=>{
  const r=kind==='text'?[...CSS.highlights.get('narration-text')][0].getClientRects()[0]:document.querySelector('.cm-narration-span').getBoundingClientRect();
  return {x:Math.round(r.left)+1,y:Math.round(r.top)+1,width:Math.floor(r.width)-2,height:Math.floor(r.height)-2};},kind);

for (const engine of ['webkit','chromium']) test(`${engine}: Bash sentence and code highlights are readable and stop restores the original colors`,async()=>{
  const pw=require('../../target/ui-tests/node_modules/playwright-core');
  const browser=await pw[engine].launch({...(engine==='chromium'&&process.platform==='win32'?{channel:'msedge'}:{}),headless:true});
  try {
    const page=await browser.newPage({viewport:{width:900,height:600},reducedMotion:'reduce'});
    await page.setContent(BASH);
    await page.addScriptTag({content:fs.readFileSync('assets/editor/editor.bundle.js','utf8')});
    await page.addStyleTag({content:fs.readFileSync('assets/app.css','utf8')});
    await page.evaluate(()=>{window.clips=[];window.molipVoice={name:'v',enabled:()=>true,rate:1.5,synthesize:async t=>'clip:'+t};
      window.Audio=class{constructor(u){this.url=u;clips.push(this)}play(){return Promise.resolve()}pause(){}};});
    await page.addScriptTag({content:fs.readFileSync('assets/layout/agent.js','utf8')});
    await page.waitForFunction(()=>document.querySelector('.cm-editor'),null,{timeout:10000});
    await page.evaluate(()=>{window.done=molipAgent.runExplanation([
      {action:'say',target:'text:파일이 없는 새 연습 폴더에서 시작해요.',text:'파일이 없는 새 연습 폴더에서 시작해요.'},
      {action:'say',target:'code:rmdir empty',text:'이 줄이 빈 폴더를 지워요.'},
      {action:'say',target:'#git-demo-terminal',text:'터미널 전체를 봐요.'},
      {action:'say',target:'text:파일이 없는 새 연습 폴더에서 시작해요.',text:'멈추면 원래 색으로 돌아와요.'},
    ])});
    await waitClips(page,1);
    const textRect=await box(page,'text');
    const sentence=await swatch(page,textRect);
    assert.ok(lum(sentence.bg)>.6,'the sentence sits on the pale lilac: '+sentence.bg);
    assert.ok(sentence.ratio>=7,`the highlighted sentence is readable: ${sentence.fg} on ${sentence.bg} = ${sentence.ratio.toFixed(2)}`);
    assert.ok(lum(sentence.fg)<.05,'the sentence glyphs are dark, not the inherited pale text: '+sentence.fg);
    await next(page);await waitClips(page,2);
    const codeRect=await box(page,'code');
    const code=await swatch(page,codeRect);
    assert.equal((await state(page)).code,'rmdir empty','only the exact code characters are marked');
    assert.ok(code.ratio>=7,`the highlighted code is readable: ${code.fg} on ${code.bg} = ${code.ratio.toFixed(2)}`);
    await next(page);await waitClips(page,3);
    const term=await page.evaluate(()=>{const s=document.querySelector('.agent-spotlight').getBoundingClientRect(),t=document.querySelector('#git-demo-terminal').getBoundingClientRect();return {s:[s.width,s.height],t:[t.width,t.height]}});
    assert.ok(term.s[0]>=term.t[0]&&term.s[1]>=term.t[1],'the terminal keeps its whole-border frame: '+JSON.stringify(term));
    assert.deepEqual((await state(page)).text,[],'the terminal frame does not paint any sentence');
    await next(page);await waitClips(page,4);
    await page.evaluate(()=>molipAgent.stop());await page.evaluate(()=>done);
    const s=await state(page);
    assert.deepEqual(s.text,[]);assert.equal(s.code,'');assert.equal(s.spotHidden,true);
    // After stop the same rectangles show the lesson's own colors again: light text on the dark pane.
    const after=await swatch(page,textRect),afterCode=await swatch(page,codeRect);
    assert.ok(lum(after.bg)<.05&&lum(after.fg)>.5,`the sentence is back to its own colors: ${after.fg} on ${after.bg}`);
    assert.ok(lum(afterCode.bg)<.05,'the code background is back to the editor color: '+afterCode.bg);
  } finally {await browser.close();}
});
