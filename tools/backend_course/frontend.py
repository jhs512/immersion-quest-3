from .common import *

lesson('html-css','HTML·CSS와 접근 가능한 화면','의미 있는 태그와 배치 규칙으로 화면을 만들어요.',[14149],[
('태그의 의미와 입력의 이름','''
    HTML은 화면 내용의 구조를 표현해요.
    제목은 h1, 목록은 ul과 li를 사용해요.
    동작은 button, 이동은 a로 표현하세요.
    입력에는 연결된 label을 붙여요.
    label의 for와 input의 id가 같아야 해요.
    조심하세요. placeholder는 label을 대신하지 못해요.
    키보드 Tab으로도 입력과 버튼에 갈 수 있어야 해요.
    개발자 도구에서 요소와 접근성 이름을 확인해요.
'''),
('크기와 배치를 분리하기','''
    CSS는 선택한 요소의 모양을 정해요.
    padding은 안쪽, margin은 바깥 여백이에요.
    box-sizing: border-box로 크기를 예측해요.
    flex는 한 방향, grid는 행과 열 배치에 유용해요.
    먼저 한 카드를 만든 뒤 두 개를 배치하세요.
    화면 폭을 줄여서 줄바꿈도 확인해요.
    고정 폭만 사용하면 작은 화면에서 넘칠 수 있어요.
''')],[
task('semantic-form','이름이 있는 입력 화면','h1에 `명언 등록`을 표시하세요.\nlabel `명언`을 id=content 입력에 연결하세요.\nlabel `작가`를 id=author 입력에 연결하세요.\n`등록` submit 버튼과 목록 ul#quotes를 만드세요.',html('''
<!-- 문서의 목적을 제목으로 알려줘요. -->
<main><h1>명언 등록</h1>
<form>
  <!-- label과 id를 연결하면 클릭과 키보드 사용을 도와줘요. -->
  <label for="content">명언</label><input id="content" required>
  <label for="author">작가</label><input id="author" required>
  <button type="submit">등록</button>
</form><ul id="quotes"></ul></main>
'''),language='web',entry='index.html',starter=html('<main><!-- 제목과 폼을 작성하세요. --></main>'),checks=[
check('text','h1',pattern='^명언 등록$'),check('attribute','label[for="content"]',name='for',value='content'),check('text','label[for="author"]',pattern='작가'),check('count','input#content',value=1),check('count','input#author',value=1),check('attribute','button',name='type',value='submit'),check('count','ul#quotes',value=1)]),
task('responsive-grid','폭에 따라 달라지는 카드 배치','main.cards 안에 article.card 세 개를 만드세요.\n800px 이상에서는 grid 3열이에요.\n그보다 작으면 1열이에요. gap은 16px이에요.',html('''
<!-- 반복되는 항목은 같은 카드 클래스를 사용해요. -->
<main class="cards"><article class="card">Git</article>
<article class="card">Java</article><article class="card">React</article></main>
''','''
/* 작은 화면을 기본값으로 둬요. */
* { box-sizing:border-box; }
.cards { display:grid; grid-template-columns:1fr; gap:16px; }
/* 넓은 화면에서만 세 열로 바꿔요. */
@media(min-width:800px) { .cards { grid-template-columns:repeat(3,1fr); } }
.card { padding:16px; border:1px solid #777; }
'''),language='web',entry='index.html',starter=html('<main class="cards"></main>'),checks=[check('count','article.card',value=3),check('css','.cards',property='display',value='grid'),check('css','.cards',property='gap',value='16px'),check('viewport',width=600,height=800),check('css','.cards',property='gridTemplateColumns',value='584px'),check('viewport',width=1200,height=800),check('css','.cards',property='gridTemplateColumns',value='384px 384px 384px')])
],['calculator-parser'])

lesson('tailwind-layout','Tailwind로 반응형 레이아웃 만들기','유틸리티를 조합하고 실제 계산된 스타일을 확인해요.',[14149],[
('유틸리티가 바꾸는 CSS 읽기','''
    Tailwind는 작은 CSS 클래스를 조합해요.
    flex는 display, gap은 항목 간격을 정해요.
    먼저 flex 하나를 적용하고 배치를 확인하세요.
    다음에 gap-4를 추가해 간격을 비교해요.
    md: 접두사는 해당 화면 폭부터 적용돼요.
    이 수업은 Tailwind 4의 브라우저 빌드를 사용해요.
    앱은 고정한 패키지를 로컬에서 불러와요.
    `<!-- tailwind -->` 위치는 그대로 두세요.
    조심하세요. 비슷한 클래스가 늘 같은 CSS는 아니에요.
    개발자 도구의 계산된 스타일을 확인하세요.
    제품 배포에서는 빌드 단계의 CSS 생성을 검토해요.
''')],[
task('tailwind-card','상태 배지와 카드 만들기','article#lesson에 p-4, rounded-lg를 적용하세요.\n제목은 h2 `자바 기초`예요.\nspan.badge에 `필수`와 font-bold를 적용하세요.\n버튼 `시작`에는 px-4 py-2를 적용하세요.',html('''
<!-- 여백과 모서리를 유틸리티로 지정해요. -->
<article id="lesson" class="p-4 rounded-lg border">
  <h2>자바 기초</h2><span class="badge font-bold">필수</span>
  <!-- 버튼은 실제 버튼 태그로 남겨요. -->
  <button class="px-4 py-2">시작</button>
</article>
''',tailwind=True),language='web',entry='index.html',starter=html('<article id="lesson"></article>',tailwind=True),checks=[check('text','h2',pattern='^자바 기초$'),check('css','#lesson',property='paddingTop',value='16px'),check('css','#lesson',property='borderRadius',value='8px'),check('css','.badge',property='fontWeight',value='700'),check('css','button',property='paddingLeft',value='16px'),check('css','button',property='paddingTop',value='8px')]),
task('tailwind-responsive','작으면 세로, 넓으면 가로','nav#menu에 flex flex-col md:flex-row gap-4를 적용하세요.\n버튼 세 개를 넣으세요.',html('''
<!-- 기본 방향은 세로이고 md부터 가로로 바꿔요. -->
<nav id="menu" class="flex flex-col md:flex-row gap-4">
<button>학습</button><button>복습</button><button>진도</button>
</nav>
''',tailwind=True),language='web',entry='index.html',starter=html('<nav id="menu"></nav>',tailwind=True),checks=[check('count','button',value=3),check('viewport',width=600,height=800),check('css','#menu',property='flexDirection',value='column'),check('css','#menu',property='gap',value='16px'),check('viewport',width=1000,height=800),check('css','#menu',property='flexDirection',value='row')])
],['html-css'])

DOM=html('''
<form id="form"><label for="name">이름</label><input id="name">
<button>추가</button></form><p id="error" role="status"></p><ul id="names"></ul>
<script>
// 배열을 실제 자료로 두고 화면은 그 자료에서 만들어요.
const names = [];
const form = document.querySelector('#form');
const input = document.querySelector('#name');
// 화면 목록도 같은 이벤트 처리에서 갱신해요.
const list = document.querySelector('#names');
form.addEventListener('submit', event => {
  event.preventDefault();
  const name = input.value.trim();
  // 잘못된 입력은 목록을 바꾸기 전에 막아요.
  if (!name) { document.querySelector('#error').textContent='이름을 입력하세요'; return; }
  document.querySelector('#error').textContent='';
  names.push(name);
  // 기존 항목을 새 DOM 목록으로 바꿔 자료와 화면을 맞춰요.
  list.replaceChildren(...names.map(value => {
    // HTML 문자열 대신 textContent로 입력을 표시해요.
    const item=document.createElement('li'); item.textContent=value; return item;
  }));
  input.value='';
});
</script>
''')
lesson('javascript-browser','JavaScript와 브라우저 이벤트','자료와 DOM을 연결하고 입력 오류를 처리해요.',[14149],[
('자바와 다른 값의 규칙','''
    JavaScript는 자바와 다른 언어예요.
    const는 변수의 재할당을 막아요.
    배열 내부의 변경까지 막는 것은 아니에요.
    let은 재할당할 값에 사용해요.
    자료형까지 비교할 때는 ===를 사용하세요.
    배열의 map과 filter는 새 배열을 반환해요.
    객체 복사는 펼침 문법 {...value}로 표현해요.
    조심하세요. 얕은 복사는 중첩 객체를 공유해요.
'''),
('이벤트에서 화면 갱신하기','''
    DOM은 브라우저가 다루는 문서 구조예요.
    querySelector로 요소를 찾을 수 있어요.
    addEventListener로 입력과 클릭을 처리해요.
    폼 기본 제출은 페이지 이동을 일으킬 수 있어요.
    preventDefault로 멈추고 자료를 갱신하세요.
    먼저 한 이름을 추가하고 화면을 확인해요.
    다음에는 빈 값과 공백만 입력해보세요.
    사용자 입력은 textContent로 표시해요.
    innerHTML에 그대로 넣으면 코드로 해석될 수 있어요.
''')],[
task('pure-array','원본을 바꾸지 않는 목록 처리','표준 입력의 JSON 배열에서 done=false만 골라요.\ntitle을 trim하고 JSON 배열로 출력하세요.\n입력 예: `[{"title":" A ","done":false}]`', '''
// Node 표준 입력 전체를 JSON으로 읽어요.
const fs = require('node:fs');
const rows = JSON.parse(fs.readFileSync(0,'utf8'));
// filter 뒤 map으로 남은 값의 모양을 바꿔요.
const titles = rows.filter(row => !row.done).map(row => row.title.trim());
console.log(JSON.stringify(titles));
''',language='javascript',entry='main.js',starter="const fs=require('node:fs');\nconst rows=JSON.parse(fs.readFileSync(0,'utf8'));\n// 결과를 출력하세요.",tests=[{'input':'[{"title":" A ","done":false},{"title":"B","done":true},{"title":" C","done":false}]','expected':'["A","C"]'},{'input':'[]','expected':'[]'}]),
task('dom-form','폼 입력으로 목록 갱신하기','form#form, input#name, ul#names, p#error를 만드세요.\n폼 제출로 이름을 목록에 추가해요.\n공백을 제거하고 빈 이름은 거부하세요.\n실패 문구는 `이름을 입력하세요`예요.\n성공하면 오류와 입력을 비우세요.',DOM,language='web',entry='index.html',starter=html('<main><!-- 폼과 이벤트를 작성하세요. --></main>'),checks=[check('click','button'),check('text','#error',pattern='이름을 입력하세요'),check('fill','#name',value=' 민수 '),check('click','button'),check('text','#names li',pattern='^민수$'),check('attribute','#name',name='id',value='name'),check('fill','#name',value='<b>텍스트</b>'),check('click','button'),check('count','#names b',value=0),check('count','#names li',value=2)])
],['tailwind-layout'])

COMPONENTS='''
import React from 'react';
import {createRoot} from 'react-dom/client';
function LessonCard({title, required}) {
  // props는 부모가 전달한 값이에요. 직접 바꾸지 않아요.
  return <article className="lesson"><h2>{title}</h2>
    <span>{required ? '필수' : '선택'}</span></article>;
}
function App() {
  const lessons=[{id:'git',title:'Git',required:true},{id:'java',title:'Java',required:true},{id:'react',title:'React',required:false}];
  // 안정된 ID를 key로 사용해요.
  return <main><h1>수업 목록</h1>{lessons.map(lesson=><LessonCard key={lesson.id} {...lesson}/>)}</main>;
}
createRoot(document.getElementById('root')).render(<App/>);
'''
lesson('react-components','React 컴포넌트·props·목록','JSX로 화면을 나누고 값을 전달해요.',[14149],[
('함수로 화면 만들기','''
    React 컴포넌트는 JSX를 반환하는 함수예요.
    이름은 대문자로 시작해요.
    JSX는 HTML과 닮았지만 JavaScript 문법이에요.
    class 대신 className을 사용하세요.
    중괄호 안에는 JavaScript 표현식을 넣어요.
    부모는 props로 자식에게 값을 전달해요.
    조심하세요. 자식이 props를 직접 바꾸면 안 돼요.
    먼저 카드 한 개를 화면에 표시하세요.
    다음에는 props로 제목을 바꾸고 다시 실행해요.
'''),
('목록과 안정된 key','''
    자료 목록을 map으로 컴포넌트 목록으로 바꿔요.
    key는 같은 항목을 다음 화면에서도 찾게 해줘요.
    삭제와 순서 변경이 있으면 배열 위치를 피하세요.
    자료의 ID를 key로 사용하는 것이 적절해요.
    이 앱은 JSX를 실제 React 코드로 빌드해요.
    App.jsx만 편집하고 root 연결은 유지하세요.
''')],[react('lesson-cards','props로 수업 카드 재사용하기','h1 `수업 목록`과 article.lesson 세 개를 표시하세요.\n각 카드의 h2는 Git, Java, React 순서예요.\nGit·Java에는 `필수`, React에는 `선택`을 표시해요.\nLessonCard 컴포넌트에 props를 전달해보세요.',COMPONENTS,[check('text','h1',pattern='^수업 목록$'),check('count','article.lesson',value=3),check('text','article.lesson:nth-of-type(1)',pattern='Git.*필수'),check('text','article.lesson:nth-of-type(2)',pattern='Java.*필수'),check('text','article.lesson:nth-of-type(3)',pattern='React.*선택')])],['javascript-browser'])

STATE='''
import React, {useState} from 'react';
import {createRoot} from 'react-dom/client';
function App() {
  const [value,setValue]=useState('');
  const [items,setItems]=useState([]);
  // 화면에서 항목을 찾을 때 사용할 안정된 ID예요.
  const [nextId,setNextId]=useState(1);
  function add(event) {
    // 폼의 기본 페이지 이동을 막고 입력을 검사해요.
    event.preventDefault();
    if (!value.trim()) return;
    // 현재 배열을 수정하지 않고 새 항목을 붙여요.
    setItems(rows=>[...rows,{id:nextId,title:value.trim(),done:false}]);
    setNextId(id=>id+1); setValue('');
  }
  return <main><form onSubmit={add}>
    <label htmlFor="title">할 일</label><input id="title" value={value} onChange={e=>setValue(e.target.value)}/>
    <button>추가</button></form><ul>{items.map(item=><li key={item.id}>
      {/* 현재 항목의 ID와 같은 객체만 새 값으로 바꿔요. */}
      <span>{item.title}</span><input aria-label={'완료 '+item.title} type="checkbox" checked={item.done}
        onChange={()=>setItems(rows=>rows.map(row=>row.id===item.id?{...row,done:!row.done}:row))}/>
      {/* ID를 비교해 선택한 항목만 삭제해요. */}
      <button onClick={()=>setItems(rows=>rows.filter(row=>row.id!==item.id))}>삭제 {item.title}</button>
    </li>)}</ul><p id="count">남은 일 {items.filter(item=>!item.done).length}</p></main>;
}
createRoot(document.getElementById('root')).render(<App/>);
'''
lesson('react-state','React 상태·폼·불변 갱신','사용자 입력으로 목록을 추가·완료·삭제해요.',[14149],[
('렌더링과 상태의 관계','''
    일반 변수를 바꿔도 화면이 다시 그려지지 않아요.
    useState가 상태와 변경 함수를 제공해요.
    변경 함수를 호출하면 새 화면을 계산해요.
    이전 값을 쓸 때는 함수형 갱신을 사용하세요.
    `setCount(n => n + 1)`처럼 표현해요.
    조심하세요. 같은 이벤트의 옛 값을 반복 사용하지 마세요.
    여러 번 갱신할 때 결과가 기대와 다를 수 있어요.
'''),
('목록을 불변 방식으로 갱신하기','''
    추가는 펼침, 수정은 map, 삭제는 filter예요.
    바뀌는 객체도 새로 만들어야 해요.
    input의 value와 onChange를 상태에 연결해요.
    먼저 추가 하나를 만들고 화면을 확인하세요.
    다음은 완료 토글과 남은 수를 연결해요.
    마지막에 삭제하고 다른 항목이 남는지 확인해요.
    새로고침하면 사라지는 문제는 다음에 해결해요.
''')],[react('state-todos','추가·완료·삭제와 남은 수','input#title과 `추가` 버튼을 만드세요.\n빈 값은 무시하고 앞뒤 공백을 제거해요.\n각 li에는 제목, checkbox, `삭제 제목` 버튼이 있어요.\np#count에는 `남은 일 N`을 표시해요.',STATE,[check('text','#count',pattern='남은 일 0'),check('fill','#title',value=' Java '),check('click','form button'),check('fill','#title',value='React'),check('click','form button'),check('count','li',value=2),check('text','#count',pattern='남은 일 2'),check('click','input[aria-label="완료 Java"]'),check('text','#count',pattern='남은 일 1'),check('click','button:text-is("삭제 React")'),check('count','li',value=1),check('text','#count',pattern='남은 일 0')])],['react-components'])

EFFECTS='''
import React,{useState,useEffect,createContext,useContext} from 'react';
import {createRoot} from 'react-dom/client';
const ThemeContext=createContext(null);
function ThemeButton() {
  // 중간 컴포넌트의 props 전달 없이 공통 값을 읽어요.
  const {theme,setTheme}=useContext(ThemeContext);
  return <button id="theme" onClick={()=>setTheme(t=>t==='light'?'dark':'light')}>{theme}</button>;
}
function App() {
  const [theme,setTheme]=useState(()=>localStorage.getItem('mq3-theme') || 'light');
  // 초기 읽기는 한 번, 이후 저장은 테마가 바뀔 때마다 해요.
  useEffect(()=>{
    // 외부 저장소와 화면의 상태를 동기화해요.
    localStorage.setItem('mq3-theme',theme);
    document.title='테마: '+theme;
  },[theme]);
  return <ThemeContext.Provider value={{theme,setTheme}}><main data-theme={theme}><ThemeButton/></main></ThemeContext.Provider>;
}
createRoot(document.getElementById('root')).render(<App/>);
'''
lesson('react-effects-context','React Effect·Context·저장','외부 시스템과 동기화하고 공통 상태를 전달해요.',[14149],[
('Effect를 쓰는 자리','''
    Effect는 렌더링 바깥의 시스템과 동기화해요.
    localStorage나 문서 제목이 그 예예요.
    계산 가능한 값은 렌더링 중 계산하면 돼요.
    남은 할 일 수에 별도 Effect는 필요 없어요.
    의존성 배열에는 사용하는 반응형 값을 넣어요.
    이벤트 리스너나 타이머는 정리 함수를 반환해요.
    조심하세요. Effect에서 무조건 상태를 바꾸지 마세요.
    렌더링과 Effect가 반복될 수 있어요.
'''),
('초기 읽기와 공통 상태','''
    useState 초기화 함수에서 저장 값을 읽어요.
    이후 변경은 Effect에서 저장하세요.
    저장한 JSON이 손상된 경우도 처리해야 해요.
    Context는 여러 단계 아래로 값을 전달해요.
    Provider 범위 안에서 useContext로 읽어요.
    가까운 부모의 props만으로 충분하면 props를 써요.
    먼저 테마 버튼을 누르고 화면을 확인하세요.
    다음에는 새로고침 후 같은 테마인지 확인해요.
''')],[react('theme-context','테마를 공유하고 저장하기','ThemeContext로 테마와 변경 함수를 전달하세요.\nmain의 data-theme은 light 또는 dark예요.\nbutton#theme은 현재 테마를 표시하고 클릭하면 바꿔요.\nlocalStorage 키는 mq3-theme이에요.\n새로고침 뒤에도 선택한 테마가 유지돼요.',EFFECTS,[check('text','#theme',pattern='^light$'),check('click','#theme'),check('attribute','main',name='data-theme',value='dark'),check('reload'),check('text','#theme',pattern='^dark$'),check('click','#theme'),check('attribute','main',name='data-theme',value='light')])],['react-state'])

PROJECT='''
import React,{useState,useEffect} from 'react';
import {createRoot} from 'react-dom/client';
function load() {
  // 저장된 값도 외부 입력이므로 자료형을 확인해요.
  try {
    const rows=JSON.parse(localStorage.getItem('mq3-quotes') || '[]');
    return Array.isArray(rows)?rows.filter(q=>q && Number.isInteger(q.id) && typeof q.content==='string' && typeof q.author==='string'):[];
  } catch { return []; }
}
function App() {
  // 화면 목록은 저장 자료를 검증한 결과로 초기화해요.
  const [rows,setRows]=useState(load);
  // 두 입력은 제어 컴포넌트로 상태와 연결해요.
  const [content,setContent]=useState(''),[author,setAuthor]=useState('');
  const [editing,setEditing]=useState(null),[keyword,setKeyword]=useState('');
  // 오류 안내는 자료 목록과 독립된 화면 상태예요.
  const [error,setError]=useState('');
  useEffect(()=>{localStorage.setItem('mq3-quotes',JSON.stringify(rows));},[rows]);
  function submit(event) {
    // 빈 값은 저장 전에 거부하고 폼 이동도 막아요.
    event.preventDefault();
    if (!content.trim() || !author.trim()) {setError('내용과 작가를 입력하세요');return;}
    // 수정은 기존 ID를 유지하고 등록은 새 ID를 만들어요.
    setRows(old=>editing===null?[...old,{id:Math.max(0,...old.map(q=>q.id))+1,content:content.trim(),author:author.trim()}]
      :old.map(q=>q.id===editing?{...q,content:content.trim(),author:author.trim()}:q));
    setContent('');setAuthor('');setEditing(null);setError('');
  }
  return <main><h1>명언 게시판</h1><form onSubmit={submit}>
    <label htmlFor="content">명언</label><input id="content" value={content} onChange={e=>setContent(e.target.value)}/>
    <label htmlFor="author">작가</label><input id="author" value={author} onChange={e=>setAuthor(e.target.value)}/>
    {/* 수정 중인 ID의 유무로 버튼의 동작 이름을 구분해요. */}
    <button id="save">{editing===null?'등록':'저장'}</button></form><p role="status" id="error">{error}</p>
    <label htmlFor="search">검색</label><input id="search" value={keyword} onChange={e=>setKeyword(e.target.value)}/>
    {/* 검색은 원본을 지우지 않고 화면에 보일 항목만 골라요. */}
    <ul>{rows.filter(q=>q.content.includes(keyword)||q.author.includes(keyword)).map(q=><li key={q.id}>
      <span>{q.content} · {q.author}</span><button onClick={()=>{setEditing(q.id);setContent(q.content);setAuthor(q.author);}}>수정</button>
      {/* 원본 배열을 직접 지우지 않고 새 배열을 만들어요. */}
      <button onClick={()=>setRows(old=>old.filter(row=>row.id!==q.id))}>삭제</button>
    </li>)}</ul></main>;
}
createRoot(document.getElementById('root')).render(<App/>);
'''
lesson('frontend-project','프론트 통합 프로젝트 · 명언 CRUD','입력·수정·삭제·검색·저장을 하나로 연결해요.',[14149,14145],[
('요구사항을 시나리오로 확인하기','''
    콘솔에서 만든 명언 앱을 웹 화면으로 옮겨요.
    화면만 닮게 만들면 CRUD가 완성되지는 않아요.
    등록한 항목을 수정하고 다시 검색해보세요.
    새로고침 후에도 수정한 값이 남아야 해요.
    삭제한 뒤에도 다른 항목은 유지돼야 해요.
    빈 입력은 자료를 바꾸기 전에 거부하세요.
    조심하세요. 저장한 JSON도 손상될 수 있어요.
    읽기 실패 시 빈 목록으로 복구해요.
    이 저장소는 브라우저의 localStorage예요.
    서버 저장이나 사용자 간 공유는 후속 주제예요.
'''),
('작게 완성하고 다시 검사하기','''
    먼저 등록과 목록만 만들고 실행하세요.
    다음에는 수정과 삭제를 하나씩 연결해요.
    검색은 원본 목록을 지우지 않고 걸러 보여줘요.
    마지막에 저장 Effect와 초기 읽기를 붙여요.
    동작이 되면 컴포넌트를 역할로 나눠보세요.
    기존 시나리오 검사가 계속 통과해야 해요.
    이 프로젝트까지가 이번 기초 코스의 범위예요.
    Spring·DB·웹 API는 다음 코스로 이어갈 수 있어요.
''')],[react('quote-project','웹 명언 게시판 완성하기','h1 `명언 게시판`과 input#content, #author를 만드세요.\nbutton#save로 등록·저장해요. 빈 값은 p#error에 안내해요.\n각 li에 내용·작가와 `수정`, `삭제` 버튼을 둬요.\ninput#search는 내용 또는 작가를 검색해요.\nlocalStorage의 mq3-quotes에 저장해요.\n새로고침 후 복원하고 손상된 JSON은 빈 목록으로 처리해요.',PROJECT,[check('click','#save'),check('text','#error',pattern='내용과 작가를 입력하세요'),check('fill','#content',value=' 시작 '),check('fill','#author',value=' 민수 '),check('click','#save'),check('text','li span',pattern='시작 · 민수'),check('click','li button:text-is("수정")'),check('fill','#content',value='계속'),check('click','#save'),check('reload'),check('text','li span',pattern='계속 · 민수'),check('fill','#search',value='없는값'),check('count','li',value=0),check('fill','#search',value='민수'),check('count','li',value=1),check('click','li button:text-is("삭제")'),check('count','li',value=0),check('reload'),check('count','li',value=0)])],['react-effects-context'])
