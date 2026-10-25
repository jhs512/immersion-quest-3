const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {chromium,webkit}=require('../../target/ui-tests/node_modules/playwright-core');
const styles=['app','repository-player','content-updates','player-workspace','window-controls','compact-toolbar','product-ui'].map(name=>fs.readFileSync(`assets/${name}.css`,'utf8')).join('\n');
// Same markup as src/player_ui.rs renders for a course with categories and tracks.
const card=(index,title,track)=>`<article class="card lesson-card"><div class="lesson-card-heading"><span class="lesson-number">수업 ${index}</span>${track?`<span class="lesson-track ${track==='필수'?'essential':'advanced'}" aria-label="학습 분류: ${track}">${track}</span>`:''}<h3>${title}</h3></div><p class="lesson-revision">버전 long-revision-name-2026-10-25</p><div class="lesson-progress"><strong>25% 완료</strong><span>필수 문제 2 / 8</span><progress max="100" value="25"></progress></div><button class="primary">학습 시작</button></article>`;
const group=(title,cards)=>`<section class="lesson-group"><h3 class="lesson-group-title">${title}</h3><div class="repository-lessons">${cards.join('')}</div></section>`;
const markup=`<style>${styles}</style><div class="repository-player"><div class="course-shell"><aside class="course-sidebar"><h2>내 과정</h2></aside><main class="course-main"><section class="course-catalog"><h2>자바 백엔드 기초</h2>
<div class="track-filter" role="group" aria-label="학습 분류로 보기"><button class="selected" aria-pressed="true">전체</button><button aria-pressed="false">필수</button><button aria-pressed="false">고급</button></div>
${group('터미널 기초',[card(1,'Bash · 파일과 폴더를 다루는 기본 명령','필수'),card(5,'Vim · 직접 편집하며 익히는 기본 조작','고급')])}
${group('아주 긴 분류 이름도 좁은 화면에서 줄바꿈되어 카드와 겹치지 않아야 해요',[card(3,'Git · 내 파일이 기록이 되는 과정',null)])}
${group('미분류',[card(9,'자바 · 계산을 메서드로 나눠요',null)])}</section></main></div></div>`;
for(const engine of ['chromium','webkit'])test(`${engine}: grouped lessons keep headings, text track labels and actions usable at every width`,async()=>{
 const browser=await({chromium,webkit}[engine]).launch(engine==='chromium'?{...(process.platform==='win32'?{channel:'msedge'}:{}),headless:true}:{headless:true,...(process.env.MQ3_WEBKIT_EXECUTABLE?{executablePath:process.env.MQ3_WEBKIT_EXECUTABLE}:{})});
 try{
  const page=await browser.newPage();
  for(const width of [1470,980,735,400]){
   await page.setViewportSize({width,height:900});
   await page.setContent(markup);
   const report=await page.evaluate(()=>{
    const rect=element=>{const b=element.getBoundingClientRect();return{left:b.left,right:b.right,top:b.top,bottom:b.bottom,width:b.width,height:b.height}};
    return{overflow:document.documentElement.scrollWidth>innerWidth,
     filters:[...document.querySelectorAll('.track-filter button')].map(rect),
     groups:[...document.querySelectorAll('.lesson-group')].map(g=>({title:rect(g.querySelector('.lesson-group-title')),cards:[...g.querySelectorAll('.lesson-card')].map(rect)})),
     badges:[...document.querySelectorAll('.lesson-track')].map(b=>({box:rect(b),card:rect(b.closest('.lesson-card')),title:rect(b.closest('.lesson-card').querySelector('h3')),text:b.textContent,label:b.getAttribute('aria-label')}))};
   });
   assert.equal(report.overflow,false,`${width}: page overflows`);
   for(const box of report.filters)assert.ok(box.height>=32&&box.width>0,`${width}: filter button too small`);
   for(const {title,cards} of report.groups){
    assert.ok(title.height>0,`${width}: group heading hidden`);
    for(const c of cards)assert.ok(title.bottom<=c.top,`${width}: group heading overlaps its lessons`);
   }
   assert.equal(report.badges.length,2);
   for(const b of report.badges){
    assert.ok(['필수','고급'].includes(b.text)&&b.label===`학습 분류: ${b.text}`,'track is text with a label, not colour only');
    assert.ok(b.box.left>=b.card.left&&b.box.right<=b.card.right&&b.box.width>0,`${width}: label escapes card`);
    assert.ok(b.box.bottom<=b.title.top+1,`${width}: label overlaps lesson title`);
   }
  }
 }finally{await browser.close()}
});
