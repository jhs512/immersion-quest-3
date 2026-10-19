// Executes current authored pages with the exact browser runner bundled in the app.
const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),out=path.join(root,'target/backend-web-checks');
const course=JSON.parse(fs.readFileSync(path.join(root,'target/backend-course/mq3-course-java-backend/course.json'),'utf8'));
for(const reference of course.lessons) {
 const lesson=JSON.parse(fs.readFileSync(path.join(root,'target/backend-course/mq3-lesson-'+reference.id+'/lesson.json'),'utf8'));
 for(const task of lesson.tasks.filter(t=>t.language==='web')) {
  const folder=path.join(out,lesson.id,task.id);fs.mkdirSync(folder,{recursive:true});
  for(const [name,body] of Object.entries(task.files))fs.writeFileSync(path.join(folder,name),body);
  fs.writeFileSync(path.join(folder,task.entry_file),task.solution);
  fs.writeFileSync(path.join(folder,'web-runner.cjs'),fs.readFileSync(path.join(root,'assets/web-runner.cjs')));
  fs.writeFileSync(path.join(folder,'web-browser.cjs'),fs.readFileSync(path.join(root,'assets/web-browser.cjs')));
  fs.writeFileSync(path.join(folder,'request.json'),JSON.stringify({entry:task.entry_file,checks:task.web_checks}));
  const result=spawnSync(process.execPath,['web-runner.cjs'],{cwd:folder,env:{...process.env,MQ3_PLAYWRIGHT:path.join(root,'target/ui-tests/node_modules/playwright-core')},encoding:'utf8',timeout:40000,windowsHide:true});
  assert.equal(result.status,0,`${lesson.id}/${task.id}: ${result.stderr}`);
  let code='';for(const action of task.narration) {if(action.action==='set_code')code=action.code;if(action.action==='patch_code'){assert.equal(code.split(action.before).length-1,1);code=code.replace(action.before,()=>action.after);}}
  assert.equal(code,task.solution);console.log('PASS '+lesson.id+'/'+task.id);
 }
}
