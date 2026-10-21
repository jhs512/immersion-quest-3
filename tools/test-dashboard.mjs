import test from 'node:test';
import assert from 'node:assert/strict';
import {markers,repository,progressKey,verifiedEvents,summarize} from '../site/dashboard/model.mjs';
const course={id:'course-a',lessons:[{id:'lesson-a',title:'값',revision:'v2'}]};
const key={user_id:7,course_id:course.id,lesson_id:'lesson-a'};
const issue={user:{id:7,login:'student'},body:`<!-- mq3-progress:${JSON.stringify(key)} -->`,html_url:'https://github.com/o/r/issues/1'};
const stable='stp_1fdc2de8-0712-4723-8cc5-5db33a8a0418';
const event=(id,extra={})=>({id,key,at:100,kind:'attempt',passed:true,revision:'v1',task_id:stable,...extra});
const comment=(events,author=7)=>({user:{id:author},body:events.map(e=>`<!-- mq3-event:${JSON.stringify(e)} -->`).join('\n')});
test('only the real issue author can own a course-scoped progress marker',()=>{
  assert.deepEqual(progressKey(issue,course),key);
  assert.equal(progressKey({...issue,user:{id:8}},course),null);
  assert.equal(progressKey(issue,{...course,id:'course-b'}),null);
  assert.equal(progressKey({...issue,pull_request:{}},course),null);
  assert.deepEqual(markers('<!-- mq3-event:bad -->','event'),[]);
  assert.equal(repository('https://github.com/owner/repo/'),'owner/repo');
  for(const bad of ['https://evil.test/o/r','o/../r','o/r?x','o/..'])assert.throws(()=>repository(bad));
});
test('batch and legacy events are deduplicated; spoofed authors and other courses are ignored',()=>{
  const valid=event('a');
  const result=verifiedEvents([comment([valid,valid]),comment([event('b')],8),comment([event('c',{key:{...key,course_id:'course-b'}})]),comment([event('d',{at:101})])],key);
  assert.deepEqual(result.map(e=>e.id),['a','d']);
});
test('current required tasks determine progress; stable IDs survive revisions, legacy IDs do not',()=>{
  const lessons=new Map([['lesson-a',{tasks:[{id:stable,title:'첫 값',required:true},{id:'old-task',required:true},{id:'optional',required:false}]}]]);
  const events=[event('a'),event('b',{task_id:'old-task'}),event('c',{kind:'explanation_viewed',task_id:'old-task',revision:'v2'})];
  let s=summarize(course,lessons,[{issue,events}])[0];
  assert.equal(s.solved,1);assert.equal(s.total,2);assert.equal(s.percent,50);assert.match(s.last,/old-task/);
  s=summarize(course,lessons,[{issue,events:[...events,event('d',{task_id:'old-task',revision:'v2',at:102})]}])[0];
  assert.equal(s.percent,100);assert.equal(s.details[0].complete,true);
});
test('missing pinned lessons stay unknown; duplicate issues cannot double-count successes',()=>{
  const records=[{issue,events:[event('a')]},{issue,events:[event('a')]}];
  assert.equal(summarize(course,new Map(),records)[0].percent,null);
  const lesson=new Map([['lesson-a',{tasks:[{id:stable,required:true}]}]]);
  const rows=summarize(course,lesson,records);assert.equal(rows.length,1);assert.equal(rows[0].solved,1);
});

test('editable names stay course-scoped; registration alone also appears in the dashboard',()=>{
  const reg=(id,course_id,name,number=10)=>({number,user:{id,login:'student'},html_url:'https://github.com/o/r/issues/'+number,body:'<!-- mq3-enrollment:'+JSON.stringify({user_id:id,course_id,name,revision:'v1',updated_at:1})+' -->'});
  let rows=summarize(course,new Map(),[],[reg(7,course.id,'[BE16]홍길동'),reg(8,'other-course','다른코스')]);
  assert.equal(rows.length,1);assert.equal(rows[0].name,'[BE16]홍길동');assert.equal(rows[0].latest,undefined);
  rows=summarize(course,new Map(),[{issue,events:[event('a')]}],[reg(7,course.id,'바꾼이름')]);assert.equal(rows.length,1);assert.equal(rows[0].name,'바꾼이름');
  const spoof=reg(8,course.id,'사칭');spoof.user.id=7;
  assert.equal(summarize(course,new Map(),[],[spoof]).length,0);
});
