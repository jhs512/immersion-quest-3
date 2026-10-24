import {test} from 'node:test';
import assert from 'node:assert/strict';
import {lessonTarget} from '../site/open/link.mjs';
test('web entry preserves the exact course and lesson identity',()=>{
 const value=lessonTarget('?course=jhs512%2Fcourse-one&lesson=lsn_example');
 assert.equal(value.course,'jhs512/course-one');assert.equal(new URL(value.app).searchParams.get('lesson'),'lsn_example');
 assert.equal(new URL(value.app).protocol,'molipquest:');
});
test('reject missing, duplicated, executable and extra parameters',()=>{
 for(const search of ['', '?lesson=x', '?course=a/b&lesson=', '?course=a/b&course=c/d','?course=a/b&lesson=x&lesson=y','?course=a/b&lesson=x&exec=git','?course=../b&lesson=x','?course=a/b&lesson=%22%3E%3Cscript%3E','?course=a/b&lesson=x%0A']) assert.throws(()=>lessonTarget(search),search);
});

// A general course link must never silently select its first lesson.
test('course-only links stop at the course and omit lesson in the app URL',()=>{
 const value=lessonTarget('?course=jhs512%2Fcourse-one');
 assert.equal(value.course,'jhs512/course-one');assert.equal(value.lesson,null);
 assert.equal(new URL(value.app).searchParams.has('lesson'),false);
});

// Docker Desktop is optional preparation: official links only, no detection, install or start actions.
test('landing page explains optional Docker Desktop setup with official links',async()=>{
 const {readFile}=await import('node:fs/promises');
 const html=await readFile(new URL('../site/open/index.html',import.meta.url),'utf8');
 const section=html.match(/<section id="docker-prep"[\s\S]*?<\/section>/)?.[0];
 assert.ok(section,'Docker section');
 for(const href of ['https://docs.docker.com/desktop/setup/install/windows-install/','https://docs.docker.com/desktop/setup/install/mac-install/'])
  assert.ok(section.includes(`href="${href}"`),href);
 for(const words of ['Docker가 필요한 실습','모든 수업에 필요한 건 아니에요','Apple Silicon과 Intel','한 번 실행']) assert.ok(section.includes(words),words);
 assert.doesNotMatch(section,/<button|<script|molipquest:|docker run|자동|감지|확인했어요/);
 // The existing entry points stay intact.
 assert.ok(html.includes('releases/latest/download/molip-quest-3-windows-x64-setup.exe'));
 assert.ok(html.includes('packaging/macos/install.sh | bash'));
 assert.ok(html.includes('id="open"'));
});
