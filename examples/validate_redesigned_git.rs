//! Replay current Git lessons using real isolated repositories and Bash commands.
use molip_quest::{git_practice::{GitPractice,GitPracticeStore},repository_course::{CourseManifest,Lesson,Task}};
use sha2::{Digest,Sha256};
use std::time::Instant;

fn quote(value:&str)->String {format!("'{}'",value.replace('\'',"'\\''"))}
fn play(p:&GitPractice,t:&Task,alternative:bool)->Result<(),String>{
    let mut lines=vec!["set -e".to_string()];
    for a in &t.narration {
        let kind=a["action"].as_str().unwrap_or_default();
        let mut command=match kind {
            "git_command"=>{
                let mut args=a["args"].as_array().ok_or("missing args")?.iter().map(|v|v.as_str().unwrap().to_string()).collect::<Vec<_>>();
                if alternative&&args==["merge","main"] {args=vec!["merge".into(),"--ff-only".into(),"main".into()];}
                if alternative&&args==["merge","feature"] {args=vec!["merge".into(),"--no-ff".into(),"feature".into()];}
                if alternative&&args==["add","memo.txt"] {args.insert(1,"--".into());}
                format!("git {}",args.iter().map(|s|quote(s)).collect::<Vec<_>>().join(" "))
            },
            "bash_command"=>a["command"].as_str().ok_or("missing shell command")?.to_string(),
            "write_memo"=>format!("printf '%s\\n' {} > memo.txt",quote(a["content"].as_str().ok_or("memo contents")?)),
            "read_memo"=>"cat memo.txt".to_string(),
            _=>continue,
        };
        if alternative&&command=="echo \"문의: 임시 창구\" >> guide.txt" {command="printf '%s\\n' '문의: 임시 창구' >> guide.txt".into();}
        if a["expected_exit"]==1 {command=format!("{command} && exit 99; test $? -eq 1");}
        lines.push(command);
        if kind=="read_memo" {if let Some(expected)=a["expected"].as_str(){lines.push(format!("test \"$(cat memo.txt)\" = {}",quote(expected.trim_end_matches('\n'))));}}
    }
    #[cfg(windows)] let shell=molip_quest::setup_terminal::git_bash_executable()?;
    #[cfg(not(windows))] let shell=std::path::PathBuf::from("/bin/bash");
    let environment=p.environment();
    let inherited=environment.iter().find(|(key,_)|key=="PATH").map(|(_,value)|std::ffi::OsString::from(value)).unwrap_or_else(||std::env::var_os("PATH").unwrap_or_default());
    let paths=shell.parent().map(std::path::Path::to_path_buf).into_iter().chain(std::env::split_paths(&inherited));
    let path=std::env::join_paths(paths).map_err(|e|e.to_string())?;
    let mut command=std::process::Command::new(shell);
    command.args(["--noprofile","--norc","-c",&lines.join("\n")]).current_dir(p.work()).envs(environment).env("PATH",path)
        .env("GIT_TRACE2_EVENT",p.root().join("commands.jsonl"));
    #[cfg(target_os="macos")] command.env("LC_CTYPE","en_US.UTF-8");
    #[cfg(windows)] {use std::os::windows::process::CommandExt; command.creation_flags(0x08000000);command.env("LC_CTYPE","C.UTF-8");}
    let output=command.output().map_err(|e|e.to_string())?;
    if !output.status.success(){return Err(format!("{}: {}\n{}",t.title,String::from_utf8_lossy(&output.stdout),String::from_utf8_lossy(&output.stderr)));}
    Ok(())
}
fn require_pass(p:&GitPractice,t:&Task,label:&str)->Result<(),String>{
    let r=if let Some(checks)=&t.git_checks{p.check(checks)?}else{p.check_exercise()?};
    if r.passed{Ok(())}else{Err(format!("{label}: {}: {}",t.title,serde_json::to_string(&r).unwrap()))}
}
fn passed(p:&GitPractice,t:&Task)->bool{require_pass(p,t,"probe").is_ok()}
fn snapshot(p:&GitPractice)->(bool,String,Vec<Option<Vec<u8>>>){
    let head=p.git(&["rev-parse","HEAD"]).unwrap();
    (head.success,head.stdout,["memo.txt","guide.txt"].iter().map(|f|std::fs::read(p.work().join(f)).ok()).collect())
}
fn changed_step(key:&str,n:usize)->bool{match key{"git-first"=>matches!(n,4|5),"git-branch"=>n==14,"git-remote"=>matches!(n,5|8|17|22),"git-branch-advanced"=>matches!(n,2|3),_=>false}}
fn wrong(p:&GitPractice,key:&str,n:usize)->Result<(),String>{
    let args:Vec<&str>=match(key,n){
        ("git-first",4|5)=>vec!["add","memo.txt"],
        ("git-branch",14)=>vec!["switch","main"],
        ("git-remote",5)=>vec!["remote","set-url","origin","../wrong.git"],
        ("git-remote",8)=>vec!["merge","origin/main"],
        ("git-remote",17)=>vec!["add","guide.txt"],
        ("git-remote",22)=>vec!["revert","--no-edit","HEAD"],
        ("git-branch-advanced",2)=>vec!["switch","feature"],
        ("git-branch-advanced",3)=>vec!["add","guide.txt"],
        _=>return Err("no wrong-state probe".into()),
    };
    let r=p.git(&args)?;if !r.success{return Err(r.stderr);}Ok(())
}
fn main()->Result<(),Box<dyn std::error::Error>>{
    let root=std::path::Path::new(env!("CARGO_MANIFEST_DIR"));
    let mut keys=std::env::args().skip(1).collect::<Vec<_>>();if keys.is_empty(){keys.push("git-remote".into());}
    for key in keys {
        let pilot=match key.as_str(){"git-first"=>"k","git-branch"=>"l","git-remote"=>"어","git-branch-advanced"=>"굳",_=>return Err("unsupported Git lesson".into())};
        let raw=std::fs::read(root.join(format!("courses/redesigned/{key}.json")))?;
        let course=CourseManifest::parse(&std::fs::read_to_string(root.join(format!("tests/fixtures/player-pilot/{pilot}/course.json")))?)?;
        let digest=format!("{:x}",Sha256::digest(&raw));if digest!=course.lessons[0].sha256{return Err("fixture hash mismatch".into());}
        let lesson=Lesson::parse(std::str::from_utf8(&raw)?,&course.lessons[0])?;
        let owned=tempfile::tempdir()?;let store=GitPracticeStore::new(owned.path())?;
        let started=Instant::now();let mut results=vec![];let mut rejects=0;let mut accepts=0;
        for (index,t) in lesson.tasks.iter().enumerate(){
            if t.interaction.is_some(){return Err(format!("choice remains: {}",t.title).into());}
            let e=t.git_terminal.clone().ok_or("missing exercise")?;
            let scope=if e.workspace_group.is_empty(){format!("task-{}",t.id)}else{e.workspace_scope("student")};
            let student=store.open(&scope,e.clone())?;
            if passed(&student,t){return Err(format!("already solved: {key} {}",index+1).into());}
            let before=snapshot(&student);
            let teacher=GitPractice::new(e.demonstration())?;play(&teacher,t,false)?;require_pass(&teacher,t,"teacher")?;
            if snapshot(&student)!=before{return Err("teacher changed student state".into());}
            play(&student,t,false)?;require_pass(&student,t,"student")?;
            let reset=store.reset_step(&format!("reset-{}",t.id),e.clone(),&t.id)?;
            if passed(&reset,t){return Err(format!("reset already solved: {}",t.title).into());}
            play(&reset,t,false)?;require_pass(&reset,t,"reset")?;
            if changed_step(&key,index+1){
                let bad=GitPractice::new(e.demonstration())?;play(&bad,t,false)?;wrong(&bad,&key,index+1)?;
                if passed(&bad,t){return Err(format!("wrong state passed: {}",t.title).into());}rejects+=1;
                let alternative=GitPractice::new(e.demonstration())?;play(&alternative,t,true)?;require_pass(&alternative,t,"alternative")?;accepts+=1;
            }
            results.push(serde_json::json!({"id":t.id,"passed":true,"independent_teacher":true,"continuous_student":true,"reset_replay":true}));
        }
        let report=serde_json::json!({"passed":true,"lesson":lesson.title,"lesson_sha256":digest,"seconds":started.elapsed().as_secs_f64(),"steps":results,"rejected_answers":rejects,"accepted_answers":accepts,"native_ui_verified":false,"voice_listened":false});
        for path in [root.join(format!("target/mcq/{key}.json")),root.join(format!("target/player-pilot-audit/{key}/public-cases.json"))]{std::fs::create_dir_all(path.parent().unwrap())?;std::fs::write(path,serde_json::to_vec_pretty(&report)?)?;}
        println!("{key}: {} actual Git steps passed, {rejects} wrong states rejected, {accepts} alternative replays in {:.2}s",results.len(),started.elapsed().as_secs_f64());
    }
    Ok(())
}
