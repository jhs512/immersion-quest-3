//! Real Bash practice state and completed commands, kept outside the learner's files.
use super::*;
#[derive(Clone,Debug,Default,Serialize,Deserialize,PartialEq)]
#[serde(deny_unknown_fields)]
pub struct ShellSnapshot {
    #[serde(default)] pub files:BTreeMap<String,String>,
    #[serde(default)] pub directories:Vec<String>,
    #[serde(default)] pub cwd:String,
}
#[derive(Clone,Debug,Default,Serialize,Deserialize,PartialEq)]
#[serde(deny_unknown_fields)]
pub struct ShellExercise {
    pub step_id:String,
    pub goal:ShellSnapshot,
    pub demo:ShellSnapshot,
    #[serde(default,skip_serializing_if="Option::is_none")] pub start:Option<ShellSnapshot>,
    #[serde(default)] pub commands:Vec<String>,
    #[serde(default)] pub requires_vim:bool,
}
#[derive(Clone,Debug)]
pub struct ShellCompletion {pub command:String,pub cwd:PathBuf,pub success:bool}
impl ShellExercise {
    pub fn validate(&self)->Result<(),String> {
        if self.step_id.is_empty()||self.step_id.len()>80||!self.step_id.bytes().all(|b|b.is_ascii_alphanumeric()||b"_-".contains(&b)) {return Err("Bash 스텝 이름을 확인하세요.".into())}
        if self.commands.is_empty()||self.commands.len()>30||self.commands.iter().any(|s|s.is_empty()||s.len()>4000||s.contains(['\n','\r','\0'])){return Err("Bash 실습 명령을 확인하세요.".into())}
        for state in [&self.goal,&self.demo].into_iter().chain(self.start.iter()) {
            if state.files.len()>80||state.directories.len()>80{return Err("Bash 실습 파일 수를 확인하세요.".into())}
            for (path,body) in &state.files {validate_file(path,body)?;}
            for path in &state.directories {validate_file(path,"")?;}
            if !state.cwd.is_empty(){validate_file(&state.cwd,"")?;}
        }
        Ok(())
    }
}
#[cfg(windows)]
fn native_path(value:&str)->PathBuf {
    let bytes=value.as_bytes();
    if bytes.len()>3&&bytes[0]==b'/'&&bytes[1].is_ascii_alphabetic()&&bytes[2]==b'/' {return PathBuf::from(format!("{}:/{}",(bytes[1] as char).to_ascii_uppercase(),&value[3..]))}
    PathBuf::from(value)
}
#[cfg(not(windows))]
fn native_path(value:&str)->PathBuf {PathBuf::from(value)}
// Accept literal directory spelling differences without evaluating shell text.
// Keep operators, substitutions and additional arguments out of normalization.
fn command_matches(expected:&str,actual:&str)->bool {
    if expected.trim()==actual.trim(){return true;}
    fn cd_target(command:&str)->Option<&str> {
        let command=command.trim();
        let (name,target)=command.split_once(char::is_whitespace)?;
        if name!="cd"{return None;}
        let target=target.trim();
        let quoted=(target.starts_with('\"')&&target.ends_with('\"'))||(target.starts_with('\'')&&target.ends_with('\''));
        let target=if quoted&&target.len()>=2{&target[1..target.len()-1]}else{target};
        if target.is_empty()||target.chars().any(|c|!c.is_alphanumeric()&&!"./_-".contains(c)&&!(quoted&&c==' ')){return None;}
        let target=target.trim_end_matches('/');
        if target.is_empty(){return Some("/");}
        let mut target=target;
        while let Some(rest)=target.strip_prefix("./"){target=rest;}
        Some(if target.is_empty(){"."}else{target})
    }
    matches!((cd_target(expected),cd_target(actual)),(Some(a),Some(b)) if a==b)
}
impl GitPractice {
    pub(super) fn prepare_shell_start(&self)->Result<(),String> {
        if let Some(start)=self.exercise.shell.as_ref().and_then(|s|s.start.as_ref()) {
            for directory in &start.directories {std::fs::create_dir_all(self.work().join(directory)).map_err(|e|e.to_string())?;}
            for (path,body) in &start.files {self.write(path,body)?;}
        }
        Ok(())
    }
    pub fn shell_completions(&self)->Result<Vec<ShellCompletion>,String> {
        let raw=match std::fs::read(self.root().join("shell-commands.log")) {Ok(raw)=>raw,Err(e) if e.kind()==std::io::ErrorKind::NotFound=>return Ok(vec![]),Err(e)=>return Err(e.to_string())};
        if raw.len()>4_000_000{return Err("실습 명령 기록이 너무 커요. 실습을 다시 시작하세요.".into())}
        let parts:Vec<_>=raw.split(|b|*b==0).collect();
        Ok(parts.chunks_exact(3).filter_map(|chunk|{
            let command=std::str::from_utf8(chunk[0]).ok()?.to_owned();
            let cwd=native_path(std::str::from_utf8(chunk[1]).ok()?);
            let success=chunk[2]==b"0";
            Some(ShellCompletion{command,cwd,success})
        }).collect())
    }
    pub fn shell_directory(&self)->Result<PathBuf,String> {
        let shell=self.exercise.shell.as_ref().ok_or("Bash 실습이 아니에요.")?;
        let directory=self.shell_completions()?.last().map(|item|item.cwd.clone()).unwrap_or_else(||self.work().join(shell.start.as_ref().map(|s|s.cwd.as_str()).unwrap_or("")));
        if directory.is_dir(){Ok(directory)}else{Ok(self.work())}
    }
    pub(super) fn shell_environment(&self)->Vec<(String,String)> {
        // Commands are observed only when the interactive shell returns to a prompt.
        // History keeps the actual command line; no student command is eval'd here.
        let prompt=r#"__mq3_status=$?; __mq3_line="$(HISTTIMEFORMAT= builtin history 1)"; if [[ "$__mq3_line" =~ ^[[:space:]]*([0-9]+)[[:space:]]+(.*)$ ]]; then __mq3_number="${BASH_REMATCH[1]}"; __mq3_command="${BASH_REMATCH[2]}"; if [[ "$__mq3_number" != "${__mq3_last:-}" ]]; then printf '%s\0%s\0%s\0' "$__mq3_command" "$([[ $OSTYPE == msys* || $OSTYPE == cygwin* ]] && builtin pwd -W || printf '%s' "$PWD")" "$__mq3_status" >> "$MQ3_SHELL_LOG"; __mq3_last="$__mq3_number"; fi; fi"#;
        vec![("MQ3_SHELL_LOG".into(),self.root().join("shell-commands.log").to_string_lossy().replace('\\',"/")),("PROMPT_COMMAND".into(),prompt.into()),("PS1".into(),"$ ".into()),("PS2".into(),"> ".into()),("HISTFILE".into(),"/dev/null".into()),("HISTCONTROL".into(),String::new()),("HISTIGNORE".into(),String::new()),("HISTSIZE".into(),"10000".into()),("VIMINIT".into(),"set nocompatible noswapfile showmode encoding=utf-8 fileencoding=utf-8 noautoindent nobackup nowritebackup viminfo=".into())]
    }
    pub(super) fn prepare_shell_checkpoint(&self)->Result<(),String> {
        let shell=self.exercise.shell.as_ref().ok_or("Bash 실습이 아니에요.")?;
        if shell.requires_vim&&!crate::setup_terminal::vim_executable().is_ok_and(|path|Command::new(path).arg("--version").output().is_ok_and(|result|result.status.success())) {return Err("Vim이 설치되어 있지 않아요. macOS에서는 Vim 설치를, Windows에서는 Git for Windows의 Vim 포함 여부를 확인한 뒤 다시 여세요.".into())}
        let directory=self.root().join("shell-checkpoints");std::fs::create_dir_all(&directory).map_err(|e|e.to_string())?;
        let path=directory.join(&shell.step_id);
        if !path.exists(){std::fs::write(path,self.shell_completions()?.len().to_string()).map_err(|e|e.to_string())?;}
        Ok(())
    }
    pub fn check_shell(&self)->Result<crate::runner::TestReport,String> {
        use crate::runner::{TestReport,TestCaseResult};
        let shell=self.exercise.shell.as_ref().ok_or("Bash 실습이 아니에요.")?;
        let records=self.shell_completions()?;
        let offset=std::fs::read_to_string(self.root().join("shell-checkpoints").join(&shell.step_id)).ok().and_then(|s|s.parse::<usize>().ok()).unwrap_or(records.len());
        let mut cursor=0;
        for item in records.iter().skip(offset) {if item.success&&shell.commands.get(cursor).is_some_and(|expected|command_matches(expected,&item.command)){cursor+=1;}}
        let mut cases=vec![];
        let mut record=|name:&str,expected:String,actual:String,passed:bool|cases.push(TestCaseResult{input:name.into(),expected,stdout:actual,stderr:String::new(),passed,state:"shell_artifact".into()});
        record("명령 실행",shell.commands.join("\n"),records.iter().skip(offset).map(|r|r.command.as_str()).collect::<Vec<_>>().join("\n"),cursor==shell.commands.len());
        let actual=self.shell_directory()?;
        let expected=self.work().join(&shell.goal.cwd);
        record("현재 폴더",shell.goal.cwd.clone(),actual.to_string_lossy().into_owned(),actual.canonicalize().ok()==expected.canonicalize().ok());
        let mut files=BTreeMap::new();let mut directories=vec![];
        fn walk(root:&Path,path:&Path,files:&mut BTreeMap<String,String>,directories:&mut Vec<String>,java:bool)->Result<(),String> {
            for entry in std::fs::read_dir(path).map_err(|e|e.to_string())? {
                let entry=entry.map_err(|e|e.to_string())?;let p=entry.path();let kind=entry.file_type().map_err(|e|e.to_string())?;
                if kind.is_symlink(){return Err("실습 폴더에 바로가기 대신 실제 파일을 사용하세요.".into())}
                let name=p.strip_prefix(root).map_err(|e|e.to_string())?.to_string_lossy().replace('\\',"/");
                if java&&name=="Main.class"&&kind.is_file(){continue;}
                if kind.is_dir(){directories.push(name);if directories.len()>80{return Err("실습 폴더가 너무 많아요.".into())}walk(root,&p,files,directories,java)?;}
                else if kind.is_file(){if entry.metadata().map_err(|e|e.to_string())?.len()>200_000{return Err("실습 파일이 너무 커요.".into())}files.insert(name,std::fs::read_to_string(&p).map_err(|e|e.to_string())?);if files.len()>80{return Err("실습 파일이 너무 많아요.".into())}}
            }
            Ok(())
        }
        walk(&self.work(),&self.work(),&mut files,&mut directories,self.exercise.java_build.is_some())?;
        directories.sort();let mut expected_directories=shell.goal.directories.clone();expected_directories.sort();
        record("파일 내용",serde_json::to_string(&shell.goal.files).unwrap(),serde_json::to_string(&files).unwrap(),files==shell.goal.files);
        record("폴더 목록",expected_directories.join("\n"),directories.join("\n"),directories==expected_directories);
        Ok(TestReport{passed:cases.iter().all(|c|c.passed),cases})
    }
}
