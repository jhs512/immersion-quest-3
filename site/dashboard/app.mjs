import {repository,repositoryFromUrl,dashboardPath,progressKey,verifiedEvents,summarize} from './model.mjs';
const $ = id => document.getElementById(id);
let students=[], busy=false;
const cache = new Map();
function node(tag, text, cls) {const n=document.createElement(tag); if(text!=null)n.textContent=text;if(cls)n.className=cls;return n;}
const date = value => value === undefined ? '기록 없음' : new Date(value*1000).toLocaleString('ko-KR');
const savedKey = repo => `mq-dashboard:v1:${repo}`;
const validSnapshot = (data,repo) => data?.version===1 && data.repository===repo && typeof data.title==='string' && Array.isArray(data.students) && Number.isFinite(data.generatedAt) && Number.isFinite(data.lessonCount);
function showSnapshot(data,stored=false){
  students=data.students;$('title').textContent=data.title;
  $('stats').replaceChildren(node('span',`학생 ${students.length}명`),node('span',`수업 ${data.lessonCount}개`));
  $('status').textContent=`${stored?'새 자료를 받지 못해 이전 저장 자료를 보여요. ':'공용 현황 · '}집계 시각: ${new Date(data.generatedAt).toLocaleString('ko-KR')}`;
  $('results').hidden=false;history.replaceState(null,'',dashboardPath(data.repository,location.pathname));render();
}
async function sharedSnapshot(repo){
  let saved;try{saved=JSON.parse(localStorage.getItem(savedKey(repo)));}catch{}
  try{
    const response=await fetch(new URL(`data/${repo}.json`,document.baseURI),{cache:'no-store'});
    if(response.status===404){if(validSnapshot(saved,repo)){showSnapshot(saved,true);return true;}return false;}
    if(!response.ok)throw Error('공용 현황을 불러오지 못했어요. 잠시 뒤 조회하세요.');
    let data;try{data=await response.json();}catch{return false;}
    if(!validSnapshot(data,repo))throw Error('공용 현황 형식을 확인하지 못했어요.');
    try{localStorage.setItem(savedKey(repo),JSON.stringify(data));}catch{/* Storage may be disabled or full. */}
    showSnapshot(data);return true;
  }catch(error){if(validSnapshot(saved,repo)){showSnapshot(saved,true);return true;}throw error;}
}
async function json(url) {
  const headers = {Accept:'application/vnd.github+json'};
  if(cache.get(url)?.etag) headers['If-None-Match']=cache.get(url).etag;
  const res=await fetch(url,{headers});
  if(res.status===304 && cache.has(url))return cache.get(url).data;
  if(!res.ok)throw new Error(res.status===403 || res.status===429 ? 'GitHub 조회 한도에 도달했어요. 잠시 뒤 다시 조회하세요.' : `자료를 불러오지 못했어요 (${res.status}). 공개 저장소와 게시된 수업을 확인하세요.`);
  const data=await res.json();cache.set(url,{etag:res.headers.get('etag'),data});return data;
}
async function pages(path) {const all=[];for(let p=1;p<=100;p++){const page=await json(`https://api.github.com${path}${path.includes('?')?'&':'?'}per_page=100&page=${p}`);if(!Array.isArray(page))throw new Error('GitHub 응답을 확인하지 못했어요.');all.push(...page);if(page.length<100)return all;}throw new Error('기록이 너무 많아 전체 조회를 마치지 못했어요.');}
async function content(repo, ref, path){return json(`https://raw.githubusercontent.com/${repository(repo)}/${encodeURIComponent(ref)}/${path}`);}
async function pool(items, work){let i=0;const results=await Promise.allSettled(Array.from({length:Math.min(3,items.length)},async()=>{while(i<items.length)await work(items[i++]);}));const failed=results.find(r=>r.status==='rejected');if(failed)throw failed.reason;}
function render(){
  const query=$('search').value.trim().toLowerCase();$('students').replaceChildren();
  const shown=students.filter(s=>s.login.toLowerCase().includes(query)||s.name.toLowerCase().includes(query));
  if(!shown.length)$('students').append(node('p',students.length?'검색 결과가 없어요.':'아직 전송된 학습 기록이 없어요.','empty'));
  for(const s of shown){
    const detail=node('details',null,'student'), summary=node('summary');
    const identity=node('span',s.name,'identity');identity.append(node('small',`@${s.login}`));summary.append(identity);
    const prog=node('span',null,'progress');
    if(s.percent!==null){const bar=node('progress');bar.max=100;bar.value=s.percent;bar.setAttribute('aria-label',`진도 ${s.percent}%`);prog.append(bar,node('span',`${s.percent}%`));}else prog.append(node('span','진도 확인 필요'));
    summary.append(prog,node('span',s.last,'last'),node('span',s.latest?new Date(s.latest*1000).toLocaleString('ko-KR'):'기록 대기','time'),node('span','자세히 보기','detail-hint'));detail.append(summary);
    const table=node('table');const head=node('tr');head.append(node('th','수업'),node('th','필수 문제'));table.append(head);
    for(const l of s.details){
      const row=node('tr'), cell=node('td');
      if(l.unavailable)cell.textContent=l.title;
      else {
        const lesson=node('details',null,'lesson-detail');lesson.append(node('summary',`${l.title} · 문제별 자세히 보기`));
        const taskTable=node('table',null,'task-times'), headings=node('tr');
        for(const title of ['문제','상태','시작','완료','제출'])headings.append(node('th',title));taskTable.append(headings);
        for(const task of l.tasks){const tr=node('tr');
          for(const text of [task.title,task.status,date(task.started),date(task.finished),`${task.attempts}회`])tr.append(node('td',text));
          taskTable.append(tr);
        }
        const scroll=node('div',null,'table-scroll');scroll.append(taskTable);lesson.append(scroll);cell.append(lesson);
      }
      row.append(cell,node('td',l.unavailable?'수업 자료 확인 필요':`${l.complete?'✓ 완료 · ':l.challenge?'◆ 도전 통과 · ':''}${l.solved} / ${l.total}`));table.append(row);
    }detail.append(table);
    const link=node('a','GitHub 원본 기록 보기 ↗');link.href=s.issues[0];link.target='_blank';link.rel='noopener noreferrer';detail.append(link);$('students').append(detail);
  }
}
async function load(){
  if(busy)return;busy=true;$('load').disabled=true;for(const b of $('presets').querySelectorAll('button'))b.disabled=true;$('results').hidden=true;$('status').textContent='코스와 학습 기록을 불러오고 있어요…';
  try{
    const repo=repository($('repo').value);
    if(await sharedSnapshot(repo))return;
    const course=await content(repo,'main','course.json');
    if(!course.id || !Array.isArray(course.lessons))throw new Error('MQ 코스 형식이 아니에요.');
    const lessons=new Map(),issues=await pages(`/repos/${repo}/issues?state=all`),records=[];
    const relevant=issues.filter(i=>progressKey(i,course));let done=0;
    await pool(course.lessons,async ref=>{try{const lesson=await content(ref.repository,ref.revision,'lesson.json');if(lesson.id===ref.id && lesson.revision===ref.revision && Array.isArray(lesson.tasks))lessons.set(ref.id,lesson);}catch{/* A missing lesson must not become 0% or 100%. */}});
    await pool(relevant,async issue=>{const key=progressKey(issue,course);const comments=issue.comments===0?[]:await pages(`/repos/${repo}/issues/${issue.number}/comments`);records.push({issue,events:verifiedEvents(comments,key)});$('status').textContent=`진도 이슈 ${++done} / ${relevant.length}개를 확인했어요.`;});
    students=summarize(course,lessons,records,issues);$('title').textContent=course.title;$('stats').replaceChildren(node('span',`학생 ${students.length}명`),node('span',`수업 ${course.lessons.length}개`));
    if(lessons.size===course.lessons.length)try{localStorage.setItem(savedKey(repo),JSON.stringify({version:1,repository:repo,generatedAt:Date.now(),title:course.title,lessonCount:course.lessons.length,students}));}catch{}
    const missing=course.lessons.length-lessons.size;$('status').textContent=`조회 완료 · ${new Date().toLocaleTimeString('ko-KR')}${missing?` · 수업 자료 ${missing}개를 확인하지 못했어요. 전체 완료율은 표시하지 않아요.`:''}`;
    $('results').hidden=false;history.replaceState(null,'',dashboardPath(repo,location.pathname));render();
  }catch(error){$('status').textContent=error.message;}finally{busy=false;$('load').disabled=false;for(const b of $('presets').querySelectorAll('button'))b.disabled=false;}
}
$('lookup').addEventListener('submit',e=>{e.preventDefault();load();});
$('presets').addEventListener('click',e=>{if(e.target.dataset.repo){$('repo').value=e.target.dataset.repo;load();}});
$('search').addEventListener('input',render);
try {const initial=repositoryFromUrl(location.href);if(initial){$('repo').value=initial;load();}}
catch(error){$('status').textContent=error.message;}
