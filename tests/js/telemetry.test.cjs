const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
test('WebView error bridge forwards locations only, bounds traffic and replaces old listeners',()=>{
 let time=0; const sent=[]; const listeners=new Map();
 const window={addEventListener:(type,fn)=>{if(!listeners.has(type))listeners.set(type,new Set());listeners.get(type).add(fn)},removeEventListener:(type,fn)=>listeners.get(type)?.delete(fn)};
 const context=vm.createContext({window,Date:{now:()=>time},document:{querySelector:()=>({dataset:{courseId:'course_1',lessonId:'lesson_1',taskId:'task_1'}})},dioxus:{send:value=>sent.push(JSON.parse(JSON.stringify(value)))}});
 const source=fs.readFileSync('assets/layout/telemetry.js','utf8');
 vm.runInContext(source,context);vm.runInContext(source,context);
 assert.equal(listeners.get('error').size,1);
 const fire=(type,event)=>{for(const listener of listeners.get(type))listener(event)};
 fire('error',{error:{name:'TypeError',message:'SECRET'},message:'SECRET',filename:'https://private.example/user/editor.js?token=SECRET',lineno:8,colno:4});
 fire('unhandledrejection',{reason:{name:'ReferenceError',message:'SECRET'}});
 assert.equal(sent[0].name,'TypeError');assert.equal(sent[0].file,'');assert.equal(sent[0].line,8);assert.equal(sent[0].task,'task_1');
 assert.equal(sent[1].kind,'unhandledrejection');assert.ok(!JSON.stringify(sent).includes('SECRET'));assert.ok(!JSON.stringify(sent).includes('private.example'));
 for(let i=0;i<100;i++)fire('error',{error:{name:'Error'}});
 assert.equal(sent.length,20);time=60001;fire('error',{error:{name:'Error'}});assert.equal(sent.length,21);
});
