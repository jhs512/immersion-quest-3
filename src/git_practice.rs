//! Real Git in a disposable owned directory. Directory isolation is not an OS sandbox.
use serde::{Deserialize,Serialize};
#[cfg(windows)]
use std::os::windows::process::CommandExt;
use std::{collections::BTreeMap,path::{Path,PathBuf},process::{Command,Output}};
#[derive(Clone,Debug,Default,Serialize,Deserialize,PartialEq)]
pub struct GitExercise {
    #[serde(default)] pub files:BTreeMap<String,String>,
    #[serde(default)] pub setup:Vec<GitSetup>,
    #[serde(default)] pub commands:Vec<Vec<String>>,
}
#[derive(Clone,Debug,Serialize,Deserialize,PartialEq)]
#[serde(tag="kind",rename_all="snake_case")]
pub enum GitSetup { File{path:String,content:String}, Git{args:Vec<String>} }
pub struct GitPractice { directory:tempfile::TempDir, exercise:GitExercise }
impl GitExercise {
    pub fn validate(&self)->Result<(),String> {
        if self.files.len()>80||self.setup.len()>100||self.commands.len()>20{return Err("Git 실습의 준비 내용을 확인하세요.".into())}
        for (path,content) in &self.files {validate_file(path,content)?;}
        for action in &self.setup {match action {
            GitSetup::File{path,content}=>validate_file(path,content)?,
            GitSetup::Git{args}=>{
                if args.len()>50 || !args.first().is_some_and(|arg|["add","commit","branch","checkout","switch","merge","rebase","cherry-pick","tag","reset"].contains(&arg.as_str())) || args.iter().any(|arg|arg.len()>4000||arg=="-C"||arg=="-c"||arg.starts_with("--git-dir")||arg.starts_with("--work-tree")||arg.starts_with("--config-env")) {return Err("Git 시작 명령을 확인하세요.".into())}
            }
        }}
        if self.commands.iter().any(|args|args.is_empty()||args.len()>50||args.iter().any(|arg|arg.len()>4000)){return Err("검사할 Git 명령을 확인하세요.".into())}
        Ok(())
    }
}
fn validate_file(path:&str,content:&str)->Result<(),String> {
    if !crate::repository_course::safe_file(path)||path.split('/').any(|part|part.eq_ignore_ascii_case(".git"))||content.len()>200_000 {return Err("Git 준비 파일 경로를 확인하세요.".into())}Ok(())
}
impl GitPractice {
    pub fn new(exercise:GitExercise)->Result<Self,String> {
        exercise.validate()?;
        let directory=tempfile::Builder::new().prefix("mq3-git-practice-").tempdir().map_err(|e|e.to_string())?;
        let practice=Self{directory,exercise};
        for folder in ["work","home"] {std::fs::create_dir(practice.root().join(folder)).map_err(|e|e.to_string())?;}
        std::fs::write(practice.root().join("global.config"),"").map_err(|e|e.to_string())?;
        practice.checked_at(practice.root(),&["init","--bare","--initial-branch=main","remote.git"])?;
        practice.checked_at(practice.work().as_path(),&["init","--initial-branch=main"])?;
        let remote=practice.root().join("remote.git");
        practice.checked_at(practice.work().as_path(),&["remote","add","origin",remote.to_str().ok_or("Git 경로 오류")?])?;
        practice.write("tracked.txt","initial\n")?;
        for (path,content) in &practice.exercise.files {practice.write(path,content)?;}
        practice.checked_at(practice.work().as_path(),&["add","."])?;
        practice.checked_at(practice.work().as_path(),&["commit","-m","Start"])?;
        practice.checked_at(practice.work().as_path(),&["push","-u","origin","main"])?;
        for action in &practice.exercise.setup {match action {
            GitSetup::File{path,content}=>practice.write(path,content)?,
            GitSetup::Git{args}=>{practice.checked_at(practice.work().as_path(),&args.iter().map(String::as_str).collect::<Vec<_>>())?;}
        }}
        Ok(practice)
    }
    pub fn root(&self)->&Path {self.directory.path()}
    pub fn work(&self)->PathBuf {self.root().join("work")}
    pub fn environment(&self)->Vec<(String,String)> {
        let home=self.root().join("home").to_string_lossy().into_owned();
        vec![("HOME".into(),home.clone()),("USERPROFILE".into(),home.clone()),("APPDATA".into(),home.clone()),("LOCALAPPDATA".into(),home.clone()),("XDG_CONFIG_HOME".into(),home),
            ("GIT_CONFIG_GLOBAL".into(),self.root().join("global.config").to_string_lossy().into_owned()),("GIT_CONFIG_NOSYSTEM".into(),"1".into()),
            ("GIT_AUTHOR_NAME".into(),"Learner".into()),("GIT_AUTHOR_EMAIL".into(),"learner@example.invalid".into()),("GIT_COMMITTER_NAME".into(),"Learner".into()),("GIT_COMMITTER_EMAIL".into(),"learner@example.invalid".into()),
            ("GIT_AUTHOR_DATE".into(),"2026-01-01T00:00:00+0000".into()),("GIT_COMMITTER_DATE".into(),"2026-01-01T00:00:00+0000".into()),("GIT_ALLOW_PROTOCOL".into(),"file".into()),("GIT_TERMINAL_PROMPT".into(),"0".into()),("GIT_PAGER".into(),"cat".into()),("GIT_EDITOR".into(),"true".into()),("GIT_SEQUENCE_EDITOR".into(),"true".into())]
    }
    fn execute(&self,dir:&Path,args:&[&str],trace:bool)->Result<Output,String> {
        let mut command=Command::new("git");command.args(args).current_dir(dir);
        for (key,_) in std::env::vars_os(){if key.to_string_lossy().starts_with("GIT_"){command.env_remove(key);}}
        command.envs(self.environment());
        if trace {command.env("GIT_TRACE2_EVENT",self.root().join("commands.jsonl"));}
        #[cfg(windows)] command.creation_flags(0x08000000);
        command.output().map_err(|e|format!("Git을 실행하지 못했어요. {e}"))
    }
    fn checked_at(&self,dir:&Path,args:&[&str])->Result<(),String> {
        let output=self.execute(dir,args,false)?;
        if output.status.success(){Ok(())}else{Err(String::from_utf8_lossy(&output.stderr).into_owned())}
    }
    pub fn git(&self,args:&[&str])->Result<crate::runner::Execution,String> {
        let result=self.execute(self.work().as_path(),args,true)?;
        Ok(crate::runner::Execution{success:result.status.success(),stdout:String::from_utf8_lossy(&result.stdout).replace("\r\n","\n"),stderr:String::from_utf8_lossy(&result.stderr).into_owned(),state:"finished".into(),artifacts:vec![]})
    }
    fn write(&self,path:&str,content:&str)->Result<(),String> {
        validate_file(path,content)?;let file=self.work().join(path);
        std::fs::create_dir_all(file.parent().ok_or("Git 파일 경로 오류")?).map_err(|e|e.to_string())?;
        std::fs::write(file,content).map_err(|e|e.to_string())
    }
    #[cfg(not(target_os="android"))]
    pub fn open_terminal(&self)->Result<(crate::setup_terminal::SetupTerminal,tokio::sync::mpsc::Receiver<Vec<u8>>),String> {
        let mut environment=self.environment();
        environment.push(("GIT_TRACE2_EVENT".into(),self.root().join("commands.jsonl").to_string_lossy().into_owned()));
        crate::setup_terminal::SetupTerminal::open_practice(&self.work(),&environment)
    }
    pub fn check(&self,checks:&crate::repository_course::GitChecks)->Result<crate::runner::TestReport,String> {
        use crate::runner::{TestReport,TestCaseResult};
        let mut cases=vec![];
        let mut query=|name:&str,args:Vec<&str>,expected:String,minimum:bool|->Result<(),String>{
            let result=self.execute(&self.work(),&args,false)?;
            let stdout=String::from_utf8_lossy(&result.stdout).replace("\r\n","\n");
            let matched=if minimum {stdout.trim().parse::<usize>().is_ok_and(|n|n>=checks.minimum_commits)}else{stdout.trim_end()==expected.trim_end()};
            cases.push(TestCaseResult{input:name.into(),expected,stdout,stderr:String::from_utf8_lossy(&result.stderr).into_owned(),passed:result.status.success()&&matched,state:"git_artifact".into()});Ok(())
        };
        query("커밋 개수",vec!["rev-list","--count","HEAD"],checks.minimum_commits.to_string(),true)?;
        query("마지막 커밋",vec!["log","-1","--format=%s"],checks.head_message.clone(),false)?;
        query("작업 폴더",vec!["status","--porcelain"],String::new(),false)?;
        if let Some(branch)=&checks.branch {query("현재 브랜치",vec!["branch","--show-current"],branch.clone(),false)?;}
        for (file,content) in &checks.tracked_files {validate_file(file,content)?;query("추적 파일",vec!["show",&format!("HEAD:{file}")],content.clone(),false)?;}
        if checks.pushed {
            let head=self.execute(&self.work(),&["rev-parse","HEAD"],false)?;
            query("원격 main 커밋",vec!["rev-parse","refs/remotes/origin/main"],String::from_utf8_lossy(&head.stdout).trim().into(),false)?;
            // Read the actual local remote too; a stale tracking ref is not evidence of a push.
            let remote=self.execute(&self.root().join("remote.git"),&["rev-parse","refs/heads/main"],false)?;
            let remote_ok=head.status.success()&&remote.status.success()&&head.stdout==remote.stdout;
            cases.push(TestCaseResult{input:"로컬 원격의 실제 커밋".into(),expected:String::from_utf8_lossy(&head.stdout).into_owned(),stdout:String::from_utf8_lossy(&remote.stdout).into_owned(),stderr:String::from_utf8_lossy(&remote.stderr).into_owned(),passed:remote_ok,state:"git_artifact".into()});
        }
        if !self.exercise.commands.is_empty() {cases.extend(self.check_commands()?.cases);}
        Ok(TestReport{passed:cases.iter().all(|case|case.passed),cases})
    }
    pub fn check_commands(&self)->Result<crate::runner::TestReport,String> {
        if self.exercise.commands.is_empty(){return Err("검사할 Git 명령이 없어요.".into())}
        let passed=self.commands_satisfied()?;
        Ok(crate::runner::TestReport{passed,cases:vec![crate::runner::TestCaseResult{input:"실제 Git 명령 실행".into(),expected:"목표 명령이 성공적으로 실행돼요.".into(),stdout:String::new(),stderr:String::new(),passed,state:"git_command".into()}]})
    }
    pub fn completed_commands(&self)->Result<Vec<Vec<String>>,String> {
        let path=self.root().join("commands.jsonl");
        let raw=match std::fs::read_to_string(&path){Ok(raw)=>raw,Err(e) if e.kind()==std::io::ErrorKind::NotFound=>return Ok(vec![]),Err(e)=>return Err(e.to_string())};
        if raw.len()>4_000_000{return Err("명령 기록이 너무 길어요. 실습을 초기화하세요.".into())}
        let mut started=BTreeMap::<String,Vec<String>>::new();let mut completed=vec![];
        for line in raw.lines() {
            let Ok(value)=serde_json::from_str::<serde_json::Value>(line) else{continue};
            let Some(sid)=value["sid"].as_str() else{continue};
            if value["event"]=="start" {
                if let Some(args)=value["argv"].as_array() {started.insert(sid.into(),args.iter().skip(1).filter_map(|arg|arg.as_str().map(str::to_owned)).collect());}
            } else if value["event"]=="exit" && value["code"]==0 {
                if let Some(args)=started.remove(sid){completed.push(args);}
            }
        }
        Ok(completed)
    }
    pub fn commands_satisfied(&self)->Result<bool,String> {
        let completed=self.completed_commands()?;
        Ok(self.exercise.commands.iter().all(|expected|completed.contains(expected)))
    }
    pub fn reset(&mut self)->Result<(),String> {
        // Build the complete next state first. TempDir only removes its owned root,
        // including local remote/index/in-progress operations, without following links.
        let replacement=Self::new(self.exercise.clone())?;
        let previous=std::mem::replace(self,replacement);
        previous.directory.close().map_err(|e|e.to_string())
    }
}
