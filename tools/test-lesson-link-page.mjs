import {test} from 'node:test';
import assert from 'node:assert/strict';
import {lessonTarget} from '../site/open/link.mjs';
test('web entry preserves the exact course and lesson identity',()=>{
 const value=lessonTarget('?course=jhs512%2Fcourse-one&lesson=lsn_example');
 assert.equal(value.course,'jhs512/course-one');assert.equal(new URL(value.app).searchParams.get('lesson'),'lsn_example');
 assert.equal(new URL(value.app).protocol,'molipquest:');
});
test('reject missing, duplicated, executable and extra parameters',()=>{
 for(const search of ['', '?course=a/b','?course=a/b&lesson=x&lesson=y','?course=a/b&lesson=x&exec=git','?course=../b&lesson=x','?course=a/b&lesson=%22%3E%3Cscript%3E','?course=a/b&lesson=x%0A']) assert.throws(()=>lessonTarget(search),search);
});
