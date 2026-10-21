import {execFileSync} from 'node:child_process';
import {readFile,mkdir,writeFile,readdir} from 'node:fs/promises';
import {pathToFileURL} from 'node:url';
import {repository,progressKey,verifiedEvents,summarize} from '../site/dashboard/model.mjs';

export async function snapshot(repo, api, raw) {
  repo=repository(repo);
  const meta=await api(`/repos/${repo}`);
  if(meta.private!==false)throw Error('Only public course repositories can be published');
  const course=await raw(repo,'main','course.json');
  if(!course.id||!Array.isArray(course.lessons))throw Error('Invalid course');
  async function pages(path){const all=[];for(let p=1;p<=1000;p++){
    const rows=await api(`${path}${path.includes('?')?'&':'?'}per_page=100&page=${p}`);
    if(!Array.isArray(rows))throw Error('Invalid GitHub list');
    all.push(...rows);if(rows.length<100)return all;
  }throw Error('Pagination limit exceeded');}
  const issues=await pages(`/repos/${repo}/issues?state=all`);
  const relevant=issues.filter(i=>progressKey(i,course));
  const grouped=new Map(relevant.map(i=>[`https://api.github.com/repos/${repo}/issues/${i.number}`,[]]));
  // One paginated repository-wide list instead of one API request per student/lesson.
  if(relevant.some(i=>i.comments>0))for(const comment of await pages(`/repos/${repo}/issues/comments`))grouped.get(comment.issue_url)?.push(comment);
  const lessons=new Map();
  for(const ref of course.lessons){
    const lesson=await raw(repository(ref.repository),ref.revision,'lesson.json');
    if(lesson.id!==ref.id||lesson.revision!==ref.revision||!Array.isArray(lesson.tasks))throw Error('Pinned lesson mismatch');
    lessons.set(ref.id,lesson);
  }
  const records=relevant.map(issue=>({issue,events:verifiedEvents(grouped.get(`https://api.github.com/repos/${repo}/issues/${issue.number}`)||[],progressKey(issue,course))}));
  const students=summarize(course,lessons,records,issues).map(({events,...student})=>student);
  return {version:1,repository:repo,generatedAt:Date.now(),title:course.title,lessonCount:course.lessons.length,students};
}
async function main(){
  const api=async path=>JSON.parse(execFileSync('gh',['api',path],{encoding:'utf8',stdio:['ignore','pipe','pipe']}));
  const raw=async(repo,ref,path)=>{const r=await fetch(`https://raw.githubusercontent.com/${repo}/${encodeURIComponent(ref)}/${path}`);if(!r.ok)throw Error(`Public content HTTP ${r.status}`);return r.json();};
  const output=process.argv[2]||'public/dashboard/data';
  for(const name of await readdir('courses/redesigned-courses'))if(name.endsWith('.json')){
    const {repository:repo}=JSON.parse(await readFile(`courses/redesigned-courses/${name}`,'utf8'));
    const data=await snapshot(repo,api,raw),path=`${output}/${repo}.json`;
    await mkdir(`${output}/${repo.split('/')[0]}`,{recursive:true});
    await writeFile(path,JSON.stringify(data));console.log(`${repo}: ${data.students.length} students`);
  }
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href)main().catch(()=>{console.error('Dashboard snapshot failed; existing published data is preserved. Check GitHub API access and pinned public lessons.');process.exitCode=1;});
