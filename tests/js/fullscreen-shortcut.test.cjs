const {test}=require('node:test');
const assert=require('node:assert/strict');
const vm=require('node:vm');
const fs=require('node:fs');
const path=require('node:path');

test('holding F11 changes mode once; releasing and pressing again changes it back',()=>{
 let listener, fullscreen=false;
 const document={
  getElementById:()=>({click:()=>{fullscreen=!fullscreen}}),
  addEventListener:(type,fn)=>{if(type==='keydown')listener=fn},
  querySelector:()=>null,
 };
 vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../../assets/layout/shortcuts.js'),'utf8'),{
  document,navigator:{platform:'Win32'},performance:{now:()=>0},
  HTMLInputElement:class{},HTMLTextAreaElement:class{},Element:class{},
 });
 const key={key:'F11',repeat:false,preventDefault(){}};
 listener(key);
 assert.equal(fullscreen,true);
 for(let i=0;i<6;i++)listener({...key,repeat:true});
 assert.equal(fullscreen,true,'auto repeat must not undo the mode change');
 listener(key);
 assert.equal(fullscreen,false);
});
