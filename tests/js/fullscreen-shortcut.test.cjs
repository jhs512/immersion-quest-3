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
 const key={key:'F11',repeat:false,preventDefault(){},stopPropagation(){}};
 listener(key);
 assert.equal(fullscreen,true);
 for(let i=0;i<6;i++)listener({...key,repeat:true});
 assert.equal(fullscreen,true,'auto repeat must not undo the mode change');
 listener(key);
 assert.equal(fullscreen,false);
});

test('Mac Control+Command+F toggles from editable surfaces without handling Command+F',()=>{
 let listener, clicks=0;
 class Element { closest(){return true;} }
 const document={
  getElementById:id=>id==='app-fullscreen-toggle'?{click:()=>clicks++}:null,
  addEventListener:(type,fn)=>{if(type==='keydown')listener=fn},
  querySelector:()=>null,
 };
 vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../../assets/layout/shortcuts.js'),'utf8'),{
  document,navigator:{platform:'MacIntel'},performance:{now:()=>0},
  HTMLInputElement:class{},HTMLTextAreaElement:class{},Element,
 });
 let prevented=0, stopped=0;
 const key={key:'f',metaKey:true,ctrlKey:true,repeat:false,target:new Element(),
  preventDefault(){prevented++},stopPropagation(){stopped++}};
 listener({...key,ctrlKey:false});
 assert.equal(clicks,0,'Command+F remains available for search');
 listener(key);
 assert.equal(clicks,1);
 assert.equal(stopped,1,'the editor or terminal must not receive the handled chord');
 listener({...key,repeat:true});
 assert.equal(clicks,1);
 assert.equal(prevented,2,'held Mac shortcut must suppress native repeat as well');
 listener({...key,key:'F'});
 assert.equal(clicks,2);
 listener({...key,altKey:true});
 assert.equal(clicks,2);
});
