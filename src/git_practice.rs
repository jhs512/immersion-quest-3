//! Real Git in a disposable owned directory. Directory isolation is not an OS sandbox.
use serde::{Deserialize,Serialize};
#[cfg(windows)]
use std::os::windows::process::CommandExt;
use std::{collections::BTreeMap,path::{Path,PathBuf},process::{Command,Output}};
#[derive(Clone,Debug,Default,Serialize,Deserialize,PartialEq)]
pub struct GitExercise {
    #[serde(default,skip_serializing_if="GitInitialHistory::is_recorded")] pub initial_history:GitInitialHistory,
    #[serde(default,skip_serializing_if="Option::is_none")] pub state_goal:Option<GitStateGoal>,
    #[serde(default)] pub files:BTreeMap<String,String>,
    #[serde(default)] pub setup:Vec<GitSetup>,
    #[serde(default)] pub commands:Vec<Vec<String>>,
}
#[derive(Clone,Copy,Debug,Default,Serialize,Deserialize,PartialEq)]
#[serde(rename_all="snake_case")]
pub enum GitInitialHistory { #[default] Recorded, Empty }
impl GitInitialHistory {fn is_recorded(&self)->bool{*self==Self::Recorded}}
#[derive(Clone,Debug,Default,Serialize,Deserialize,PartialEq)]
#[serde(deny_unknown_fields)]
pub struct GitStateGoal {
    #[serde(default,skip_serializing_if="Option::is_none")] pub parent_count:Option<usize>,
    #[serde(default,skip_serializing_if="Option::is_none")] pub merge_in_progress:Option<bool>,
    #[serde(default,skip_serializing_if="Option::is_none")] pub unmerged_paths:Option<Vec<String>>,
    #[serde(default,skip_serializing_if="Option::is_none")] pub current_branch:Option<String>,
    #[serde(default,skip_serializing_if="Option::is_none")] pub references:Option<BTreeMap<String,String>>,
    #[serde(default,skip_serializing_if="Option::is_none")] pub head_exists:Option<bool>,
    #[serde(default,skip_serializing_if="Option::is_none")] pub commit_count:Option<usize>,
    #[serde(default,skip_serializing_if="Option::is_none")] pub clean:Option<bool>,
    #[serde(default,skip_serializing_if="Option::is_none")] pub index:Option<BTreeMap<String,String>>,
    #[serde(default,skip_serializing_if="Option::is_none")] pub working_files:Option<BTreeMap<String,String>>,
    #[serde(default,skip_serializing_if="Option::is_none")] pub head_files:Option<BTreeMap<String,String>>,
    #[serde(default,skip_serializing_if="Option::is_none")] pub parent_files:Option<BTreeMap<String,String>>,
}
#[derive(Clone,Debug,Serialize,Deserialize,PartialEq)]
#[serde(tag="kind",rename_all="snake_case")]
pub enum GitSetup { File{path:String,content:String}, Git{args:Vec<String>}, MergeConflict{branch:String} }
enum PracticeDirectory { Temporary(tempfile::TempDir), Saved{path:PathBuf,scope:String} }
impl PracticeDirectory {fn path(&self)->&Path {match self {Self::Temporary(directory)=>directory.path(),Self::Saved{path,..}=>path}}}
pub struct GitPractice { directory:PracticeDirectory, exercise:GitExercise }

/// Student repositories stay at their original paths across player restarts.
/// Each reset publishes a new owned directory; the previous state remains a recovery copy.
pub struct GitPracticeStore { root:PathBuf }
fn canonical_directory(path:&Path)->Result<PathBuf,String> {
    let canonical=path.canonicalize().map_err(|error|error.to_string())?;
    // Git for Windows cannot read GIT_CONFIG_GLOBAL using the Win32 verbatim prefix.
    #[cfg(windows)] if let Some(text)=canonical.to_str() {
        if let Some(unc)=text.strip_prefix(r"\\?\UNC\"){return Ok(PathBuf::from(format!(r"\\{unc}")))}
        if let Some(disk)=text.strip_prefix(r"\\?\"){return Ok(PathBuf::from(disk))}
    }
    Ok(canonical)
}

impl GitPracticeStore {
    pub fn new(root:&Path)->Result<Self,String> {
        std::fs::create_dir_all(root).map_err(|error|error.to_string())?;
        if std::fs::symlink_metadata(root).map_err(|error|error.to_string())?.file_type().is_symlink(){return Err("Git 실습 보관 경로를 확인하세요.".into())}
        Ok(Self{root:canonical_directory(root)?})
    }
    pub fn installed()->Result<Self,String> {Self::new(&crate::data_dir()?.join("git-practices"))}
    fn key(scope:&str)->String {use sha2::{Digest,Sha256};format!("{:x}",Sha256::digest(scope.as_bytes()))}
    fn lock(&self,scope:&str)->Result<std::fs::File,String> {
        let path=self.root.join(format!("{}.lock",Self::key(scope)));
        match std::fs::symlink_metadata(&path) {
            Ok(metadata) if !metadata.is_file()||metadata.file_type().is_symlink()=>return Err("Git 실습 잠금 경로를 확인하세요.".into()),
            Err(error) if error.kind()!=std::io::ErrorKind::NotFound=>return Err(error.to_string()),
            _=>{}
        }
        let file=std::fs::OpenOptions::new().read(true).write(true).create(true).truncate(false).open(path).map_err(|error|error.to_string())?;
        file.lock().map_err(|error|error.to_string())?;
        Ok(file)
    }
    pub fn open(&self,scope:&str,exercise:GitExercise)->Result<GitPractice,String> {
        let _lock=self.lock(scope)?;
        exercise.validate()?;
        let key=Self::key(scope);let pointer=self.root.join(format!("{key}.json"));
        let metadata=match std::fs::symlink_metadata(&pointer){Ok(metadata)=>metadata,Err(error) if error.kind()==std::io::ErrorKind::NotFound=>return self.reset_locked(scope,exercise),Err(error)=>return Err(error.to_string())};
        if !metadata.is_file()||metadata.file_type().is_symlink()||metadata.len()>1024{return Err("Git 실습 보관 정보를 확인하세요.".into())}
        let folder:String=serde_json::from_slice(&std::fs::read(pointer).map_err(|error|error.to_string())?).map_err(|error|error.to_string())?;
        if !folder.strip_prefix("practice-").is_some_and(|suffix|!suffix.is_empty()&&suffix.len()<100&&suffix.bytes().all(|c|c.is_ascii_alphanumeric())){return Err("Git 실습 폴더 정보를 확인하세요.".into())}
        let directory=self.root.join(folder);
        if std::fs::symlink_metadata(&directory).map_err(|error|error.to_string())?.file_type().is_symlink()||canonical_directory(&directory)?.parent()!=Some(self.root.as_path()){return Err("Git 실습 폴더의 경계를 확인하세요.".into())}
        let owner=directory.join(".mq3-owner");let metadata=std::fs::symlink_metadata(&owner).map_err(|error|error.to_string())?;
        if !metadata.is_file()||metadata.file_type().is_symlink()||metadata.len()!=64||std::fs::read_to_string(owner).map_err(|error|error.to_string())?!=key{return Err("Git 실습의 소유 정보를 확인하세요.".into())}
        Ok(GitPractice{directory:PracticeDirectory::Saved{path:directory,scope:scope.into()},exercise})
    }
    pub fn reset(&self,scope:&str,exercise:GitExercise)->Result<GitPractice,String> {
        let _lock=self.lock(scope)?;
        self.reset_locked(scope,exercise)
    }
    fn reset_locked(&self,scope:&str,exercise:GitExercise)->Result<GitPractice,String> {
        use std::io::Write;
        let directory=tempfile::Builder::new().prefix("practice-").tempdir_in(&self.root).map_err(|error|error.to_string())?;
        let mut practice=GitPractice::initialize(exercise,directory)?;
        let key=Self::key(scope);
        std::fs::write(practice.root().join(".mq3-owner"),&key).map_err(|error|error.to_string())?;
        let folder=practice.root().file_name().and_then(|name|name.to_str()).ok_or("Git 실습 폴더 이름 오류")?;
        let mut pointer=tempfile::NamedTempFile::new_in(&self.root).map_err(|error|error.to_string())?;
        pointer.write_all(serde_json::to_string(folder).unwrap().as_bytes()).map_err(|error|error.to_string())?;
        pointer.as_file().sync_all().map_err(|error|error.to_string())?;
        pointer.persist(self.root.join(format!("{key}.json"))).map_err(|error|error.to_string())?;
        // Keep the exact absolute path: Git's local origin and private HOME refer to it.
        let PracticeDirectory::Temporary(directory)=practice.directory else {unreachable!()};
        practice.directory=PracticeDirectory::Saved{path:directory.keep(),scope:scope.into()};
        Ok(practice)
    }
}
impl GitExercise {
    pub fn has_goal(&self)->bool {self.state_goal.is_some()||!self.commands.is_empty()}
    pub fn validate(&self)->Result<(),String> {
        if self.files.len()>80||self.setup.len()>100||self.commands.len()>20{return Err("Git 실습의 준비 내용을 확인하세요.".into())}
        if let Some(goal)=&self.state_goal {
            if goal.parent_count.is_none()&&goal.merge_in_progress.is_none()&&goal.unmerged_paths.is_none()&&goal.current_branch.is_none()&&goal.references.is_none()&&goal.head_exists.is_none()&&goal.commit_count.is_none()&&goal.clean.is_none()&&goal.index.is_none()&&goal.working_files.is_none()&&goal.head_files.is_none()&&goal.parent_files.is_none(){return Err("Git 목표 상태가 필요해요.".into())}
            if let Some(paths)=&goal.unmerged_paths {
                if paths.len()>80||paths.iter().collect::<std::collections::BTreeSet<_>>().len()!=paths.len(){return Err("미병합 경로 목록을 확인하세요.".into())}
                for path in paths {validate_file(path,"")?;}
            }
            if goal.current_branch.as_deref().is_some_and(|name|!valid_branch_name(name)){return Err("목표 브랜치 이름을 확인하세요.".into())}
            if let Some(references)=&goal.references {
                if references.is_empty()||references.len()>20||references.iter().any(|(name,target)|!name.strip_prefix("refs/heads/").is_some_and(valid_branch_name)||!["HEAD","HEAD^","HEAD^1","HEAD^2"].contains(&target.as_str())) {
                    return Err("목표 브랜치 참조를 확인하세요.".into());
                }
            }
            for files in [goal.index.as_ref(),goal.working_files.as_ref(),goal.head_files.as_ref(),goal.parent_files.as_ref()].into_iter().flatten() {
                if files.len()>80{return Err("Git 목표 파일이 너무 많아요.".into())}
                for (path,content) in files {validate_file(path,content)?;}
            }
        }
        for (path,content) in &self.files {validate_file(path,content)?;}
        for action in &self.setup {match action {
            GitSetup::File{path,content}=>validate_file(path,content)?,
            GitSetup::MergeConflict{branch}=>{if !valid_branch_name(branch){return Err("충돌을 준비할 브랜치를 확인하세요.".into())}}
            GitSetup::Git{args}=>{
                if args.len()>50 || !args.first().is_some_and(|arg|["add","commit","branch","checkout","switch","merge","rebase","cherry-pick","tag","reset"].contains(&arg.as_str())) || args.iter().any(|arg|arg.len()>4000||arg=="-C"||(arg=="-c"&&args.first().is_none_or(|command|command!="switch"))||arg.starts_with("--git-dir")||arg.starts_with("--work-tree")||arg.starts_with("--config-env")) {return Err("Git 시작 명령을 확인하세요.".into())}
            }
        }}
        if self.commands.iter().any(|args|args.is_empty()||args.len()>50||args.iter().any(|arg|arg.len()>4000)){return Err("검사할 Git 명령을 확인하세요.".into())}
        Ok(())
    }
}
fn valid_branch_name(name:&str)->bool {
    !name.is_empty()&&name.len()<=200&&!name.starts_with('-')&&!name.starts_with('.')&&!name.ends_with('.')&&!name.ends_with('/')&&!name.ends_with(".lock")&&!name.contains("..")&&!name.contains("//")&&name.bytes().all(|c|c.is_ascii_alphanumeric()||b"/_-.".contains(&c))
}
fn validate_file(path:&str,content:&str)->Result<(),String> {
    if !crate::repository_course::safe_file(path)||path.split('/').any(|part|part.eq_ignore_ascii_case(".git"))||content.len()>200_000 {return Err("Git 준비 파일 경로를 확인하세요.".into())}Ok(())
}
impl GitPractice {
    pub fn new(exercise:GitExercise)->Result<Self,String> {
        let directory=tempfile::Builder::new().prefix("mq3-git-practice-").tempdir().map_err(|e|e.to_string())?;
        Self::initialize(exercise,directory)
    }
    fn initialize(exercise:GitExercise,directory:tempfile::TempDir)->Result<Self,String> {
        exercise.validate()?;
        let practice=Self{directory:PracticeDirectory::Temporary(directory),exercise};
        for folder in ["work","home"] {std::fs::create_dir(practice.root().join(folder)).map_err(|e|e.to_string())?;}
        std::fs::write(practice.root().join("global.config"),"").map_err(|e|e.to_string())?;
        practice.checked_at(practice.root(),&["init","--bare","--initial-branch=main","remote.git"])?;
        practice.checked_at(practice.work().as_path(),&["init","--initial-branch=main"])?;
        let remote=practice.root().join("remote.git");
        practice.checked_at(practice.work().as_path(),&["remote","add","origin",remote.to_str().ok_or("Git 경로 오류")?])?;
        if practice.exercise.initial_history==GitInitialHistory::Recorded {practice.write("tracked.txt","initial\n")?;}
        for (path,content) in &practice.exercise.files {practice.write(path,content)?;}
        if practice.exercise.initial_history==GitInitialHistory::Recorded {
            practice.checked_at(practice.work().as_path(),&["add","."])?;
            practice.checked_at(practice.work().as_path(),&["commit","-m","Start"])?;
            practice.checked_at(practice.work().as_path(),&["push","-u","origin","main"])?;
        }
        for action in &practice.exercise.setup {match action {
            GitSetup::File{path,content}=>practice.write(path,content)?,
            GitSetup::MergeConflict{branch}=>{
                let merge=practice.execute(&practice.work(),&["merge","--no-edit","--",branch],false)?;
                let head=practice.merge_in_progress()?;
                let index=practice.execute(&practice.work(),&["ls-files","--unmerged","-z"],false)?;
                if merge.status.code()!=Some(1)||!head||!index.status.success()||index.stdout.is_empty(){return Err("시작 상태에서 예상한 병합 충돌이 나지 않았어요.".into())}
            }
            GitSetup::Git{args}=>{practice.checked_at(practice.work().as_path(),&args.iter().map(String::as_str).collect::<Vec<_>>())?;}
        }}
        Ok(practice)
    }
    fn merge_in_progress(&self)->Result<bool,String> {
        use std::io::Read;
        let path=self.work().join(".git/MERGE_HEAD");
        let metadata=match std::fs::symlink_metadata(&path) {
            Ok(metadata)=>metadata,
            Err(error) if error.kind()==std::io::ErrorKind::NotFound=>return Ok(false),
            Err(error)=>return Err(error.to_string()),
        };
        if !metadata.is_file()||metadata.file_type().is_symlink()||metadata.len()>4096{return Err("병합 상태 파일을 확인하세요. 초기화해 다시 열 수 있어요.".into())}
        let mut raw=String::new();
        std::fs::File::open(path).map_err(|error|error.to_string())?.take(4097).read_to_string(&mut raw).map_err(|error|error.to_string())?;
        if raw.is_empty()||raw.len()>4096{return Err("병합 상태 파일의 내용을 확인하세요.".into())}
        for hash in raw.lines() {
            if !matches!(hash.len(),40|64)||!hash.bytes().all(|byte|byte.is_ascii_hexdigit()){return Err("병합 대상 기록을 확인하세요.".into())}
            let kind=self.execute(&self.work(),&["cat-file","-t",hash],false)?;
            if !kind.status.success()||kind.stdout!=b"commit\n"{return Err("병합 대상 커밋을 확인하세요.".into())}
        }
        Ok(true)
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
        if checks.pushed {
            let head=self.execute(&self.work(),&["rev-parse","HEAD"],false)?;
            query("원격 main 커밋",vec!["rev-parse","refs/remotes/origin/main"],String::from_utf8_lossy(&head.stdout).trim().into(),false)?;
            // Read the actual local remote too; a stale tracking ref is not evidence of a push.
            let remote=self.execute(&self.root().join("remote.git"),&["rev-parse","refs/heads/main"],false)?;
            let remote_ok=head.status.success()&&remote.status.success()&&head.stdout==remote.stdout;
            cases.push(TestCaseResult{input:"로컬 원격의 실제 커밋".into(),expected:String::from_utf8_lossy(&head.stdout).into_owned(),stdout:String::from_utf8_lossy(&remote.stdout).into_owned(),stderr:String::from_utf8_lossy(&remote.stderr).into_owned(),passed:remote_ok,state:"git_artifact".into()});
        }
        for (file,content) in &checks.tracked_files {
            validate_file(file,content)?;
            let result=self.execute(&self.work(),&["show",&format!("HEAD:{file}")],false)?;
            let stdout=String::from_utf8_lossy(&result.stdout).into_owned();
            cases.push(TestCaseResult{input:format!("추적 파일 {file}"),expected:content.clone(),passed:result.status.success()&&stdout==*content,stdout,stderr:String::from_utf8_lossy(&result.stderr).into_owned(),state:"git_artifact".into()});
        }
        if !self.exercise.commands.is_empty()||self.exercise.state_goal.is_some() {cases.extend(self.check_exercise()?.cases);}
        Ok(TestReport{passed:cases.iter().all(|case|case.passed),cases})
    }
    /// Grade the actual repository state, successful command goals, or both.
    pub fn check_exercise(&self)->Result<crate::runner::TestReport,String> {
        use crate::runner::{TestReport,TestCaseResult};
        use std::collections::BTreeSet;
        let Some(goal)=&self.exercise.state_goal else{return self.check_commands()};
        let mut cases=vec![];
        let mut record=|name:String,passed:bool,expected:String,stdout:String|cases.push(TestCaseResult{input:name,expected,stdout,stderr:String::new(),passed,state:"git_artifact".into()});
        // A damaged or redirected repository must not count as an unborn HEAD.
        for directory in [self.work(),self.work().join(".git")] {
            let valid=std::fs::symlink_metadata(&directory).is_ok_and(|m|m.is_dir()&&!m.file_type().is_symlink());
            if !valid {return Err("실습 저장소의 경로를 확인하세요. 초기화해 다시 열 수 있어요.".into())}
        }
        let repository=self.execute(&self.work(),&["rev-parse","--is-inside-work-tree"],false)?;
        record("실습 저장소".into(),repository.status.success()&&repository.stdout==b"true\n","true".into(),String::from_utf8_lossy(&repository.stdout).into());
        if let Some(expected)=goal.parent_count {
            let result=self.execute(&self.work(),&["rev-list","--parents","-n","1","HEAD"],false)?;
            let actual=String::from_utf8_lossy(&result.stdout).split_whitespace().count().checked_sub(1);
            record("현재 기록의 부모 수".into(),result.status.success()&&actual==Some(expected),expected.to_string(),actual.map(|count|count.to_string()).unwrap_or_default());
        }
        if let Some(expected)=goal.merge_in_progress {
            let actual=self.merge_in_progress()?;
            record("병합 진행 상태".into(),actual==expected,expected.to_string(),actual.to_string());
        }
        if let Some(paths)=&goal.unmerged_paths {
            let result=self.execute(&self.work(),&["diff","--name-only","--diff-filter=U","-z"],false)?;
            let output=String::from_utf8_lossy(&result.stdout);
            let actual=output.split('\0').filter(|path|!path.is_empty()).collect::<BTreeSet<_>>();
            let expected=paths.iter().map(String::as_str).collect::<BTreeSet<_>>();
            record("미병합 경로".into(),result.status.success()&&actual==expected,expected.into_iter().collect::<Vec<_>>().join(", "),actual.into_iter().collect::<Vec<_>>().join(", "));
        }
        if let Some(expected)=&goal.current_branch {
            let result=self.execute(&self.work(),&["symbolic-ref","--quiet","HEAD"],false)?;
            let actual=String::from_utf8_lossy(&result.stdout).trim().to_owned();
            let expected=format!("refs/heads/{expected}");
            record("현재 브랜치".into(),result.status.success()&&actual==expected,expected,actual);
        }
        if let Some(references)=&goal.references {
            for (reference,expected) in references {
                let head=self.execute(&self.work(),&["rev-parse","--verify",&format!("{expected}^{{commit}}")],false)?;
                let actual=self.execute(&self.work(),&["rev-parse","--verify",&format!("{reference}^{{commit}}")],false)?;
                record(reference.clone(),head.status.success()&&actual.status.success()&&head.stdout==actual.stdout,expected.clone(),String::from_utf8_lossy(&actual.stdout).trim().into());
            }
        }
        if let Some(expected)=goal.head_exists {
            let actual=self.execute(&self.work(),&["rev-parse","--verify","HEAD^{commit}"],false)?.status.success();
            record("커밋 존재".into(),actual==expected,expected.to_string(),actual.to_string());
        }
        if let Some(expected)=goal.commit_count {
            let result=self.execute(&self.work(),&["rev-list","--count","HEAD"],false)?;
            let actual=if result.status.success(){String::from_utf8_lossy(&result.stdout).trim().parse::<usize>().ok()}else if !self.execute(&self.work(),&["rev-parse","--verify","HEAD^{commit}"],false)?.status.success(){Some(0)}else{None};
            record("기록 개수".into(),actual==Some(expected),expected.to_string(),actual.map(|n|n.to_string()).unwrap_or_default());
        }
        if let Some(expected)=goal.clean {
            let result=self.execute(&self.work(),&["status","--porcelain"],false)?;
            let actual=result.stdout.is_empty();
            record("작업 상태".into(),result.status.success()&&actual==expected,if expected{"변경 없음"}else{"변경 있음"}.into(),String::from_utf8_lossy(&result.stdout).into());
        }
        for (reference,label,files) in [(Some(":"),"준비 영역",goal.index.as_ref()),(None,"작업 파일",goal.working_files.as_ref()),(Some("HEAD:"),"현재 기록",goal.head_files.as_ref()),(Some("HEAD^:"),"직전 기록",goal.parent_files.as_ref())] {
            let Some(files)=files else{continue};
            let args=match reference {Some(":")=>vec!["ls-files","-z"],Some("HEAD:")=>vec!["ls-tree","-r","--name-only","-z","HEAD"],Some("HEAD^:")=>vec!["ls-tree","-r","--name-only","-z","HEAD^"],_=>vec!["ls-files","--cached","--others","-z"]};
            let listed=self.execute(&self.work(),&args,false)?;
            let actual=String::from_utf8_lossy(&listed.stdout).split('\0').filter(|s|!s.is_empty())
                .filter(|path|reference.is_some()||std::fs::symlink_metadata(self.work().join(path)).is_ok())
                .map(str::to_owned).collect::<BTreeSet<_>>();
            let expected=files.keys().cloned().collect::<BTreeSet<_>>();
            record(format!("{label} 목록"),listed.status.success()&&actual==expected,expected.into_iter().collect::<Vec<_>>().join(", "),actual.into_iter().collect::<Vec<_>>().join(", "));
            for (path,expected) in files {
                let actual=if let Some(reference)=reference {
                    let object=format!("{reference}{path}");
                    let size=self.execute(&self.work(),&["cat-file","-s",&object],false)?;
                    if size.status.success()&&String::from_utf8_lossy(&size.stdout).trim().parse::<usize>()==Ok(expected.len()) {
                        let result=self.execute(&self.work(),&["show",&object],false)?;
                        result.status.success().then_some(result.stdout)
                    }else{None}
                }else{
                    use std::io::Read;
                    let mut file=self.work();let mut safe=true;
                    for part in path.split('/') {file.push(part);if !std::fs::symlink_metadata(&file).is_ok_and(|m|!m.file_type().is_symlink()){safe=false;break;}}
                    if safe&&std::fs::symlink_metadata(&file).is_ok_and(|m|m.is_file()) {std::fs::File::open(&file).ok().and_then(|file|{let mut bytes=vec![];file.take(expected.len() as u64+1).read_to_end(&mut bytes).ok()?;Some(bytes)})}else{None}
                };
                let passed=actual.as_deref()==Some(expected.as_bytes());
                record(format!("{label} {path}"),passed,expected.clone(),actual.map(|bytes|String::from_utf8_lossy(&bytes).into_owned()).unwrap_or_else(||"파일 내용이 없거나 크기가 달라요.".into()));
            }
        }
        if !self.exercise.commands.is_empty(){cases.extend(self.check_commands()?.cases);}
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
        let replacement=match &self.directory {
            PracticeDirectory::Temporary(_)=>Self::new(self.exercise.clone())?,
            PracticeDirectory::Saved{path,scope}=>GitPracticeStore::new(path.parent().ok_or("Git 실습 보관 경로 오류")?)?.reset(scope,self.exercise.clone())?,
        };
        let previous=std::mem::replace(self,replacement);
        match previous.directory {PracticeDirectory::Temporary(directory)=>directory.close().map_err(|e|e.to_string()),PracticeDirectory::Saved{..}=>Ok(())}
    }
}
