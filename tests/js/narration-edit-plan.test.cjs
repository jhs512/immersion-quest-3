// Narration code edits are typed keystroke by keystroke (assets/layout/agent.js editPlan).
// Every intermediate document must keep the lines the edit does not change whole, and the last
// one must be exactly the authored target. Replays every narrated edit of every course file.
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');

const root=path.join(__dirname,'../..');
const context={Intl,console};context.globalThis=context;
vm.runInNewContext(fs.readFileSync(path.join(root,'assets/layout/agent.js'),'utf8'),context);
const plan=context.molipEditPlan;

const splitLines=text=>text.split(/\r\n|\r|\n/);
// Whole lines of a text; the empty piece after a final line break is the end, not a line.
const wholeLines=text=>{const lines=splitLines(text);if(lines[lines.length-1]==='')lines.pop();return lines;};
// Lines both documents share at the start and at the end, outside [from, to).
function keptLines(source,from,to,target){
 const head=splitLines(source.slice(0,from)).slice(0,-1);
 // When the edit ends at a line start, the line after it is a whole line too.
 const tail=wholeLines(source.slice(to)).slice(to===0||/[\r\n]$/.test(source.slice(0,to))?0:1);
 const t=wholeLines(target);
 let p=0;while(p<head.length&&head[p]===t[p])p++;
 let s=0;while(s<tail.length&&tail[tail.length-1-s]===t[t.length-1-s])s++;
 return [head.slice(0,p),tail.slice(tail.length-s)];
}
function play(source,from,to,insert){
 const target=source.slice(0,from)+insert+source.slice(to);
 const [head,tail]=keptLines(source,from,to,target);
 let doc=source,steps=0;
 for(const step of plan.steps(source,from,to,insert)){
  assert.ok(step.from>=0&&step.to<=doc.length&&step.from<=step.to,'step stays inside the document');
  doc=doc.slice(0,step.from)+step.insert+doc.slice(step.to);steps++;
  assert.ok(!/[\uD800-\uDBFF](?![\uDC00-\uDFFF])|(?<![\uD800-\uDBFF])[\uDC00-\uDFFF]/.test(doc),'never splits a character');
  const lines=wholeLines(doc);
  assert.deepEqual(lines.slice(0,head.length),head,'unchanged lines above the edit stay whole');
  assert.deepEqual(lines.slice(lines.length-tail.length),tail,'unchanged lines below the edit stay whole');
 }
 assert.equal(doc,target,'the final document is exactly the authored target');
 return {steps,doc};
}

test('the pictured Java fix types only " + 1000" and keeps the closing brace on its own line',()=>{
 const source='class Main {\n    static int next_fee(int fee) {\n        return fee;\n    }\n\n    public static void main(String[] args) {\n    }\n}\n';
 const before='        return fee;\n',from=source.indexOf(before);
 const frames=[];let doc=source;
 for(const s of plan.steps(source,from,from+before.length,'        return fee + 1000;\n')){doc=doc.slice(0,s.from)+s.insert+doc.slice(s.to);frames.push(doc);}
 assert.equal(frames.length,' + 1000'.length,'nothing shared is deleted and retyped');
 for(const f of frames)assert.match(f,/\n    \}\n\n    public static/,'`}` keeps its own line in every frame');
 assert.ok(frames.some(f=>f.includes('        return fee + 1;\n    }\n')),'the half-typed frame of the screenshot now keeps `}` below');
 play(source,from,from+before.length,'        return fee + 1000;\n');
});

test('line insertions, deletions and nested blocks never pull the next line up',()=>{
 const py='def f(x):\n    if x:\n        y = 1\n    return y\n';
 // Insert a new indented line after `if x:` (Python indentation exactly as authored).
 let at=py.indexOf('        y = 1\n');
 let r=play(py,at,at,'        z = 2\n');
 assert.equal(r.doc,'def f(x):\n    if x:\n        z = 2\n        y = 1\n    return y\n');
 // Delete a whole line.
 const java='for (int p : prices) {\n    result = result + p;\n    return result;\n}\n';
 at=java.indexOf('    result = result + p;\n');
 play(java,at,java.indexOf('}'),'    result = result + p;\n');
 // A one-line statement becomes a nested block; and back again.
 const one='int f() {\n    return 2500; // 고치세요.\n}\n',b='    return 2500; // 고치세요.';
 at=one.indexOf(b);
 r=play(one,at,at+b.length,'    // 무료 이상이면 0이에요.\n    if (amount >= freeFrom) {\n        return 0;\n    }\n    return 2500;');
 play(r.doc,0,r.doc.length,one);
 // One-line constructs stay one line: no brace is moved.
 const inline='int[] a = {2000, 3000};\n';
 r=play(inline,inline.indexOf('{'),inline.indexOf('}')+1,'{}');
 assert.equal(r.doc,'int[] a = {};\n');
});

test('CRLF, Korean, emoji and strings/comments keep exact bytes and offsets',()=>{
 const crlf='class A {\r\n    int f() {\r\n        return 1;\r\n    }\r\n}\r\n';
 let at=crlf.indexOf('        return 1;\r\n');
 play(crlf,at,at+'        return 1;\r\n'.length,'        int x = 1;\r\n        return x + 1;\r\n');
 const ko='print("배송비 👩‍💻 2,000원")  # 주석 ✅\nprint("끝")\n';
 at=ko.indexOf('2,000원');
 let r=play(ko,at,at+'2,000원'.length,'3,000원 🚚');
 assert.equal(r.doc,'print("배송비 👩‍💻 3,000원 🚚")  # 주석 ✅\nprint("끝")\n');
 play(ko,0,ko.length,'print("배송비 👩‍💻 2,000원")  # 주석 ✅\nprint("새 줄 $& $1 ${x}")\nprint("끝")\n');
 // Template literal with a closing brace on the same line stays as authored.
 const js='const out = `<output>${state.count}</output>`;\n';
 r=play(js,js.indexOf('${'),js.indexOf('}')+1,'${state.count + 1}');
 assert.equal(r.doc,'const out = `<output>${state.count + 1}</output>`;\n');
});

test('repeating the same edit yields the same keystrokes (replay is deterministic)',()=>{
 const s='a {\n    b;\n}\n',x=[...plan.steps(s,4,11,'    b + 1;\n')],y=[...plan.steps(s,4,11,'    b + 1;\n')];
 assert.deepEqual(JSON.parse(JSON.stringify(x)),JSON.parse(JSON.stringify(y)));
});

// Every narrated edit of every course, replayed from the task's real starter code in order.
test('every narrated code edit of every course keeps unchanged lines whole and ends exact',()=>{
 const counts={patch_code:0,set_code:0,type_code:0,synthetic:0};
 const files=[];
 (function walk(dir){for(const n of fs.readdirSync(dir,{withFileTypes:true})){const p=path.join(dir,n.name);if(n.isDirectory())walk(p);else if(n.name.endsWith('.json'))files.push(p);}})(path.join(root,'courses'));
 const visit=(node,fn)=>{if(Array.isArray(node))node.forEach(x=>visit(x,fn));else if(node&&typeof node==='object'){fn(node);Object.values(node).forEach(x=>visit(x,fn));}};
 for(const file of files){
  let data;try{data=JSON.parse(fs.readFileSync(file,'utf8'));}catch{continue;}
  visit(data,item=>{
   if(!Array.isArray(item.narration))return;
   const starter=typeof item.starter_code==='string'?item.starter_code:typeof item.problem?.starter_code==='string'?item.problem.starter_code:null;
   let doc=starter??'';
   for(const a of item.narration){
    if(!a||!['patch_code','set_code','type_code'].includes(a.action))continue;
    const where=`${path.relative(root,file)} ${item.id||''} ${a.action}`;
    try{
     if(a.action==='patch_code'){
      const before=String(a.before??''),after=String(a.after??'');
      const i=doc.indexOf(before);
      if(a.file||!before||i<0||doc.indexOf(before,i+1)>=0){
       // Another file's tab, or code the replay cannot reconstruct: check it in two contexts.
       counts.synthetic++;
       play('head();\n'+before+'\n    }\n}\n',8,8+before.length,after);
       play(before+'tail',0,before.length,after);
       continue;
      }
      doc=play(doc,i,i+before.length,after).doc;counts.patch_code++;
     }else if(a.action==='set_code'){
      const desired=String(a.code??'');let from=0,tail=0;
      while(from<doc.length&&from<desired.length&&doc[from]===desired[from])from++;
      while(tail<doc.length-from&&tail<desired.length-from&&doc[doc.length-tail-1]===desired[desired.length-tail-1])tail++;
      doc=play(doc,from,doc.length-tail,desired.slice(from,desired.length-tail)).doc;counts.set_code++;
     }else{
      let body=String(a.code??'');if(!body.endsWith('\n'))body+='\n';
      if(!a.replace&&doc&&!doc.endsWith('\n'))body='\n'+body;
      doc=play(doc,a.replace?0:doc.length,doc.length,body).doc;counts.type_code++;
     }
    }catch(error){console.error("FAILED AT",where,JSON.stringify(a).slice(0,300),JSON.stringify(doc).slice(0,400));throw error;}
   }
  });
 }
 // 2026-10-29: answer-picking steps became coding steps. Their old example patches could only be
 // checked out of context (synthetic, 465 -> 150); the new ones replay exactly on the real starter
 // code (650 -> 850). The floor follows that: more exact replays, fewer synthetic ones.
 assert.ok(counts.patch_code>800&&counts.patch_code+counts.synthetic>950&&counts.set_code>200&&counts.type_code>400,JSON.stringify(counts));
 console.log('replayed narrated edits',JSON.stringify(counts));
});
