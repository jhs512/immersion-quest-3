const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {chromium,webkit}=require('../../target/ui-tests/node_modules/playwright-core');
const styles=['app','repository-player','content-updates','player-workspace','window-controls','compact-toolbar','product-ui','station'].map(name=>fs.readFileSync(`assets/${name}.css`,'utf8')).join('\n');
for(const engine of ['chromium','webkit'])test(`${engine}: course catalog keeps titles, progress and actions usable at every width`,async()=>{
 const browser=await({chromium,webkit}[engine]).launch(engine==='chromium'?{...(process.platform==='win32'?{channel:'msedge'}:{}),headless:true}:{headless:true,...(process.env.MQ3_WEBKIT_EXECUTABLE?{executablePath:process.env.MQ3_WEBKIT_EXECUTABLE}:{})});
 try{
  const page=await browser.newPage();
  for(const width of [1470,980,735,400]){
   await page.setViewportSize({width,height:800});
   await page.setContent(`<style>${styles}</style><div class="repository-player"><header class="repository-header"><h1>몰입 퀘스트 3</h1></header><div class="course-shell"><aside class="course-sidebar"><h2>내 과정</h2><label class="course-search">과정 검색<input type="search" placeholder="이름으로 찾기"></label><nav class="course-switcher"><button class="course-selected" aria-current="page"><strong>코딩의 원리를 직접 확인하는 과정</strong><small>learning/long-course-repository-name</small></button><button>Git과 협업</button></nav><button class="course-create">코스 추가·만들기</button></aside><main class="course-main"><section class="course-catalog"><h2>코딩의 원리를 직접 확인하는 과정</h2><p>예제를 실행하고 결과를 확인하며 학습해요.</p><p class="study-progress">최신 버전 완료: 필수 수업 2 / 12</p><ol class="repository-lessons">${[1,2,3].map(index=>`<li class="card lesson-card" data-state="progress" data-next="${index===1}" data-required="${index!==3}"><span class="lesson-number"><span class="visually-hidden">수업 </span>${index}</span><div class="lesson-card-heading"><h3>자바 · 비교 결과를 저장하고 무료배송 기준이 바뀌었을 때의 동작을 판단하는 과정</h3><div class="lesson-meta"><span class="lesson-track basic" aria-label="학습 분류: 기본">기본</span>${index===3?'<span class="lesson-optional">선택</span>':''}<span class="lesson-revision">버전 java-conditions-long-revision-2026-10-20</span></div><p class="prerequisite">선수 학습: 변수와 자료형</p></div><div class="lesson-progress"><strong>25% 완료</strong><span>필수 문제 2 / 8</span><progress max="100" value="25" aria-label="수업 진도 25%"></progress></div><div class="lesson-actions"><button class="lesson-share" type="button">수업 링크 복사</button><button class="primary">학습 시작</button></div></li>`).join('')}</ol></section></main></div></div>`);
   const report=await page.evaluate(()=>{
    const rect=element=>{const b=element.getBoundingClientRect();return{left:b.left,right:b.right,top:b.top,bottom:b.bottom,width:b.width,height:b.height}};
    return{overflow:document.documentElement.scrollWidth>innerWidth,cards:[...document.querySelectorAll('.lesson-card')].map(card=>({card:rect(card),heading:rect(card.querySelector('h3')),button:rect(card.querySelector('button.primary')),progress:rect(card.querySelector('progress'))}))};
   });
   assert.equal(report.overflow,false,`${width}: page overflows`);
   for(const {card,heading,button,progress} of report.cards){
    for(const box of [heading,button,progress])assert.ok(box.left>=card.left&&box.right<=card.right&&box.width>0,`${width}: content escapes card`);
    assert.ok(button.height>=32,`${width}: action too small`);
    assert.ok(heading.right<=button.left||heading.bottom<=button.top,`${width}: heading overlaps action`);
   }
   fs.mkdirSync('target/product-ui',{recursive:true});
   await page.screenshot({path:`target/product-ui/${engine}-${width}.png`,fullPage:true});
  }
 }finally{await browser.close()}
});
