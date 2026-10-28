//! Docker CLI practice in the learner's real terminal.
//!
//! The learner types `docker …` at a real Bash prompt (the same PTY as the Bash lessons). Its
//! stdout/stderr go straight to the terminal. Grading reads two kinds of evidence only: the
//! commands the learner's shell actually completed (the Bash history hook in shell_practice) and
//! the real Docker engine state of this lesson's own container. Nothing here runs the answer.
use super::*;

#[derive(Clone,Debug,Default,Serialize,Deserialize,PartialEq)]
#[serde(deny_unknown_fields)]
pub struct DockerExercise {
    /// A digest-pinned official image (crate::docker_lab::valid_image). The learner types its tag.
    #[serde(default,skip_serializing_if="String::is_empty")] pub image:String,
    /// The name suffix of the lesson's container: `$BOX` is `<owned project>-<container>`.
    #[serde(default,skip_serializing_if="String::is_empty")] pub container:String,
    /// The container port the app publishes on 127.0.0.1 with an engine-chosen host port when it
    /// prepares a start state itself.
    #[serde(default)] pub port:u16,
    #[serde(default)] pub start:DockerStart,
    #[serde(default)] pub goal:DockerGoal,
    /// A Compose/Dockerfile step: the learner edits files in an editor above the same terminal and
    /// types `docker compose …` there. Without it the step is a plain Docker CLI step.
    #[serde(default,skip_serializing_if="Option::is_none")] pub compose:Option<ComposeWork>,
}
/// Files edited in the editor are saved into the terminal's own folder, which is the Compose
/// project directory Docker reads. Start files come from the shell exercise (`shell.start`).
#[derive(Clone,Debug,Default,Serialize,Deserialize,PartialEq)]
#[serde(deny_unknown_fields)]
pub struct ComposeWork {
    /// Digest-pinned official images the compose file and Dockerfile may use.
    pub images:Vec<String>,
    /// The files shown in the editor, first one selected.
    pub editable:Vec<String>,
    /// The graded commands must have been entered while these files had their current content.
    #[serde(default)] pub same_files:Vec<String>,
    /// Read-only checks of the real result.
    pub checks:Vec<ComposeCheck>,
}
#[derive(Clone,Debug,Serialize,Deserialize,PartialEq)]
#[serde(tag="kind",rename_all="snake_case")]
pub enum ComposeCheck {
    /// `docker compose config` (the files as Compose reads them) contains this JSON. Objects match by
    /// their listed keys, arrays by containing each listed element, `null` by the key existing.
    Config{what:String,expect:serde_json::Value},
    /// The service's container runs and was created from the current files (Compose config hash).
    Running{service:String},
    /// A named volume of this step's project is mounted at `target` (`volume`: its name in compose.yaml).
    Mount{service:String,target:String,#[serde(default,skip_serializing_if="Option::is_none")] volume:Option<String>},
    /// The service container's own log has these lines.
    Logs{service:String,has:Vec<String>},
    /// A read-only command (`cat`, or psql with one SELECT) in the running service container.
    Exec{what:String,service:String,command:Vec<String>,#[serde(default)] has:Vec<String>,#[serde(default)] lacks:Vec<String>},
    /// A file of the terminal folder (case-insensitive text).
    File{path:String,#[serde(default)] has:Vec<String>,#[serde(default)] lacks:Vec<String>},
    /// The image Compose built for the service has layers created by these instructions, in order.
    History{service:String,order:Vec<String>},
    /// The service publishes `port` on 127.0.0.1 and an HTTP GET there answers with `has`.
    Http{service:String,port:u16,has:String},
}
#[derive(Clone,Copy,Debug,Default,Serialize,Deserialize,PartialEq)]
#[serde(rename_all="snake_case")]
pub enum DockerStart { #[default] Absent, Running, Stopped }
#[derive(Clone,Copy,Debug,Serialize,Deserialize,PartialEq)]
#[serde(rename_all="snake_case")]
pub enum DockerState { Absent, Running, Exited }
#[derive(Clone,Debug,Default,Serialize,Deserialize,PartialEq)]
#[serde(deny_unknown_fields)]
pub struct DockerGoal {
    /// The image tag is present on this machine.
    #[serde(default)] pub image_present:bool,
    #[serde(default,skip_serializing_if="Option::is_none")] pub container:Option<DockerState>,
    /// The container is the very object that existed when the step started (not a new one).
    #[serde(default)] pub same_container:bool,
    /// The container was created from the tag the learner typed.
    #[serde(default)] pub created_from_image:bool,
    /// `docker logs` of the container has output.
    #[serde(default)] pub logs:bool,
    #[serde(default,skip_serializing_if="Option::is_none")] pub file:Option<DockerFile>,
}
#[derive(Clone,Debug,Default,Serialize,Deserialize,PartialEq)]
#[serde(deny_unknown_fields)]
pub struct DockerFile { pub path:String, pub content:String }

impl DockerExercise {
    pub fn tag(&self)->&str {self.image.split_once('@').map(|(tag,_)|tag).unwrap_or(&self.image)}
    pub fn validate(&self)->Result<(),String> {
        if let Some(compose)=&self.compose {
            if !self.image.is_empty()||!self.container.is_empty()||self.port!=0||self.start!=DockerStart::Absent||self.goal!=DockerGoal::default() {return Err("Compose 실습에는 CLI 컨테이너 목표를 함께 쓰지 않아요.".into())}
            return compose.validate()
        }
        if !crate::docker_lab::valid_image(&self.image){return Err("Docker 터미널 실습 이미지는 digest로 고정한 공식 이미지만 써요.".into())}
        if self.container.is_empty()||self.container.len()>20||!self.container.bytes().all(|c|c.is_ascii_lowercase()||c.is_ascii_digit()||c==b'-'){return Err("Docker 실습 컨테이너 이름을 확인하세요.".into())}
        if self.port==0{return Err("Docker 실습 포트를 확인하세요.".into())}
        let goal=&self.goal;
        if !goal.image_present&&goal.container.is_none()&&!goal.logs&&goal.file.is_none(){return Err("Docker 실습의 목표 상태가 필요해요.".into())}
        if (goal.same_container||goal.created_from_image||goal.logs||goal.file.is_some())&&!matches!(goal.container,Some(DockerState::Running|DockerState::Exited)){return Err("컨테이너가 남아 있어야 확인할 수 있는 목표예요.".into())}
        if goal.same_container&&self.start==DockerStart::Absent{return Err("시작할 때 없던 컨테이너는 같은 객체인지 비교할 수 없어요.".into())}
        if let Some(file)=&goal.file {
            if !file.path.starts_with('/')||file.path.len()>200||file.content.len()>4000||file.path.contains(['\0','\n','\'']){return Err("컨테이너 안 파일 목표를 확인하세요.".into())}
        }
        Ok(())
    }
}

impl ComposeWork {
    pub fn validate(&self)->Result<(),String> {
        if self.images.is_empty()||self.images.len()>4||!self.images.iter().all(|image|crate::docker_lab::valid_image(image)) {return Err("Compose 실습 이미지는 digest로 고정한 공식 이미지만 써요.".into())}
        if self.editable.is_empty()||self.editable.len()>4||self.editable.iter().any(|f|!crate::repository_course::safe_file(f)) {return Err("Compose 실습에서 고칠 파일을 확인하세요.".into())}
        if self.same_files.iter().any(|f|!crate::repository_course::safe_file(f)) {return Err("Compose 실습의 고정 파일을 확인하세요.".into())}
        if self.checks.is_empty()||self.checks.len()>20 {return Err("Compose 실습의 확인 항목을 확인하세요.".into())}
        let service=|name:&str|!name.is_empty()&&name.len()<64&&name.bytes().all(|c|c.is_ascii_alphanumeric()||b"_-".contains(&c));
        for check in &self.checks {
            let ok=match check {
                ComposeCheck::Config{what,expect}=>!what.is_empty()&&expect.is_object(),
                ComposeCheck::Running{service:s}|ComposeCheck::Logs{service:s,..}|ComposeCheck::History{service:s,..}|ComposeCheck::Http{service:s,..}=>service(s),
                ComposeCheck::Mount{service:s,target,..}=>service(s)&&target.starts_with('/'),
                ComposeCheck::Exec{what,service:s,command,..}=>!what.is_empty()&&service(s)&&read_only(command),
                ComposeCheck::File{path,..}=>crate::repository_course::safe_file(path),
            };
            if !ok {return Err("Compose 실습의 확인 항목을 확인하세요.".into())}
        }
        Ok(())
    }
}
/// Grading may read inside a container, never change it: `cat` files, or psql with one SELECT.
fn read_only(command:&[String])->bool {
    match command.first().map(String::as_str) {
        Some("cat")=>command.len()>1&&command[1..].iter().all(|p|p.starts_with('/')&&!p.contains("..")),
        Some("psql")=>command.iter().any(|a|a=="-c")&&command.last().is_some_and(|sql|{let sql=sql.trim().to_ascii_uppercase();sql.starts_with("SELECT ")&&!sql.contains(';')}),
        _=>false,
    }
}
/// `expect` is part of `actual`: objects by listed keys, arrays by containing each listed element,
/// `null` by the key existing.
fn contains_json(actual:&serde_json::Value,expect:&serde_json::Value)->bool {
    use serde_json::Value;
    match (actual,expect) {
        (_,Value::Null)=>true,
        (Value::Object(a),Value::Object(e))=>e.iter().all(|(k,v)|a.get(k).is_some_and(|x|contains_json(x,v))),
        (Value::Array(a),Value::Array(e))=>e.iter().all(|v|a.iter().any(|x|contains_json(x,v))),
        (a,e)=>a==e,
    }
}

/// One shell word list, or None for anything beyond plain words (operators, substitutions,
/// globs and redirections are not compared word by word).
fn words(command:&str,container:&str)->Option<Vec<String>> {
    let (mut out,mut word,mut quote,mut started)=(Vec::new(),String::new(),None::<char>,false);
    let mut chars=command.trim().chars().peekable();
    let variable=|chars:&mut std::iter::Peekable<std::str::Chars>|->Option<String>{
        let braced=chars.peek()==Some(&'{');if braced{chars.next();}
        let mut name=String::new();
        while let Some(&c)=chars.peek(){if c.is_ascii_alphanumeric()||c=='_'{name.push(c);chars.next();}else{break}}
        if braced&&chars.next()!=Some('}'){return None}
        (name=="BOX").then(||container.to_owned())
    };
    while let Some(c)=chars.next() {
        match quote {
            Some('\'') if c=='\''=>quote=None,
            Some('\'')=>word.push(c),
            Some(_) if c=='"'=>quote=None,
            Some(_) if c=='$'=>word.push_str(&variable(&mut chars)?),
            Some(_) if c=='\\'=>{let next=chars.next()?;if !"\"\\$`".contains(next){word.push('\\');}word.push(next);},
            Some(_) if c=='`'=>return None,
            Some(_)=>word.push(c),
            None if c=='\''||c=='"'=>{quote=Some(c);started=true;},
            None if c==' '||c=='\t'=>{if started{out.push(std::mem::take(&mut word));started=false;}},
            None if c=='$'=>{word.push_str(&variable(&mut chars)?);started=true;},
            None if c=='\\'=>{word.push(chars.next()?);started=true;},
            None if c.is_alphanumeric()||"./_-:=,+@%^".contains(c)=>{word.push(c);started=true;},
            None=>return None,
        }
    }
    if quote.is_some(){return None}
    if started{out.push(word);}
    Some(out)
}
/// Docker options that take a value in the commands these lessons teach.
const VALUED:&[&str]=&["--name","-p","-e","--env","-w","--workdir","-u","--user","-t","--time","-s","--signal","-n","--tail","--since","--until","--format","-f","--filter","--label","-l","--timeout","--entrypoint","--scale","--index","--wait-timeout","--pull"];
/// `docker <sub> …` as (subcommand, sorted options, ordered operands).
fn docker_parts(words:&[String])->Option<(String,Vec<(String,String)>,Vec<String>)> {
    let mut rest=words.strip_prefix(&["docker".to_string()])?.to_vec();
    if rest.first().is_some_and(|w|w=="container"||w=="image") {
        let group=rest.remove(0);
        let sub=rest.first()?.clone();
        let mapped=match (group.as_str(),sub.as_str()) {("container","ls"|"list"|"ps")=>"ps",("image","ls"|"list")=>"images",(_,other)=>other};
        rest[0]=mapped.into();
    }
    // `docker compose up -d`: the Compose subcommand is part of the command name.
    if rest.first().is_some_and(|w|w=="compose") {
        if rest.get(1)?.starts_with('-'){return None}
        rest.remove(0);rest[0]=format!("compose {}",rest[0]);
    }
    let sub=rest.first()?.clone();
    let mut options=vec![];let mut operands=vec![];let mut index=1;
    while index<rest.len() {
        let word=&rest[index];
        if !operands.is_empty()||!word.starts_with('-')||word=="-" {operands.push(word.clone());index+=1;continue}
        if word=="--" {operands.extend(rest[index+1..].iter().cloned());break}
        let (flag,value)=match word.split_once('=') {Some((f,v)) if f.starts_with("--")=>(f.to_string(),Some(v.to_string())),_=>(word.clone(),None)};
        let flag=match flag.as_str() {"--detach"=>"-d".into(),"--publish"=>"-p".into(),"--interactive"=>"-i".into(),"--tty"=>"-t".into(),"--all"=>"-a".into(),"--follow"=>"-f".into(),_=>flag};
        if let Some(value)=value {options.push((flag,value));index+=1;continue}
        let compose=sub.starts_with("compose ");
        if VALUED.contains(&flag.as_str())&&!((sub=="logs"||sub=="compose logs")&&flag=="-f")&&!(sub=="exec"&&flag=="-t")&&!(sub=="run"&&flag=="-t")&&!(compose&&(flag=="-p"||flag=="-f"||flag=="-l")) {
            options.push((flag,rest.get(index+1)?.clone()));index+=2;continue
        }
        if flag.len()>2&&!flag.starts_with("--") {
            // -dit is -d -i -t.
            for c in flag[1..].chars(){options.push((format!("-{c}"),String::new()));}
        }else{options.push((flag,String::new()));}
        index+=1;
    }
    options.sort();options.dedup();
    Some((sub,options,operands))
}
/// Whether the learner's completed command line is the expected Docker command. `$BOX` and the
/// container's real name are the same word; option order and `--long=value` spelling may differ.
pub fn docker_command_matches(expected:&str,actual:&str,container:&str)->bool {
    if expected.trim()==actual.trim(){return true}
    // A plain shell command of a Compose step (echo 빵 >> menu.txt): the Bash lessons' comparison.
    if !expected.trim_start().starts_with("docker "){return super::shell_practice::command_matches(expected,actual)}
    let (Some(a),Some(b))=(words(expected,container),words(actual,container)) else{return false};
    if a==b {return true}
    matches!((docker_parts(&a),docker_parts(&b)),(Some(x),Some(y)) if x==y)
}

#[derive(Clone,Debug,Serialize,Deserialize,PartialEq)]
pub struct DockerSession { pub project:String, pub container:String }
#[derive(Clone,Debug,Default,Serialize,Deserialize,PartialEq)]
struct DockerCheckpoint { project:String, offset:usize, container_id:String, image_id:String }

impl GitPractice {
    fn docker_exercise(&self)->Result<&DockerExercise,String> {self.exercise.docker.as_ref().ok_or_else(||"Docker 실습이 아니에요.".to_string())}
    fn docker_checkpoint_path(&self)->Result<PathBuf,String> {
        let shell=self.exercise.shell.as_ref().ok_or("Bash 실습이 아니에요.")?;
        Ok(self.root().join("docker-checkpoints").join(format!("{}.json",shell.step_id)))
    }
    /// The files a Compose step shows in its editor (empty for other steps).
    pub fn editable_files(&self)->Vec<String> {self.exercise.docker.as_ref().and_then(|d|d.compose.as_ref()).map(|c|c.editable.clone()).unwrap_or_default()}
    fn editable(&self,name:&str)->Result<PathBuf,String> {
        if !self.editable_files().iter().any(|f|f==name){return Err("이 문제에서 고칠 파일이 아니에요.".into())}
        Ok(self.work().join(name))
    }
    /// The real file in the terminal's folder, as Docker reads it.
    pub fn read_editable(&self,name:&str)->Result<String,String> {
        let bytes=std::fs::read(self.editable(name)?).map_err(|e|e.to_string())?;
        Ok(String::from_utf8_lossy(&bytes).replace("\r\n","\n"))
    }
    /// Save the editor's text into the terminal's folder (LF line endings, like the lab files).
    pub fn save_editable(&self,name:&str,text:&str)->Result<(),String> {
        use std::io::Write;
        let path=self.editable(name)?;
        validate_file(name,text)?;
        let text=text.replace("\r\n","\n");
        if self.read_editable(name).ok().as_deref()==Some(text.as_str()){return Ok(())}
        let mut file=tempfile::NamedTempFile::new_in(path.parent().ok_or("실습 파일 경로를 확인하세요.")?).map_err(|e|e.to_string())?;
        file.write_all(text.as_bytes()).and_then(|_|file.as_file().sync_all()).map_err(|e|e.to_string())?;
        // Docker may be reading the old file; then replace it in place instead.
        if let Err(error)=file.persist(&path) {std::fs::write(&path,text.as_bytes()).map_err(|e|format!("{e} ({error})"))?;}
        Ok(())
    }
    fn docker_enters(&self)->Vec<(usize,String)> {
        std::fs::read_to_string(self.root().join("docker-enters.log")).unwrap_or_default().lines()
            .filter_map(|line|{let (n,h)=line.split_once('\t')?;Some((n.parse().ok()?,h.to_owned()))}).collect()
    }
    /// Called right before Enter reaches the shell of a Compose step. Records the content of the
    /// step's fixed files for the command about to run, and when compose.yaml, Dockerfile or .env
    /// changed, checks them again and writes the verdict the terminal guard requires.
    pub fn refresh_docker_files(&self)->Result<(),String> {
        let Some(compose)=self.exercise.docker.as_ref().and_then(|d|d.compose.as_ref()) else{return Ok(())};
        use std::io::Write;
        let work=self.work();
        let fixed=crate::docker_lab::files_hash(&work,&compose.same_files.iter().map(String::as_str).collect::<Vec<_>>());
        if self.docker_enters().last().is_none_or(|(_,h)|*h!=fixed) {
            let mut log=std::fs::OpenOptions::new().create(true).append(true).open(self.root().join("docker-enters.log")).map_err(|e|e.to_string())?;
            writeln!(log,"{}\t{fixed}",self.shell_completions()?.len()).map_err(|e|e.to_string())?;
        }
        let hash=crate::docker_lab::files_hash(&work,&crate::docker_lab::COMPOSE_FILES);
        let path=self.root().join("docker-verdict");
        if std::fs::read_to_string(&path).is_ok_and(|text|text.lines().next()==Some(hash.as_str())){return Ok(())}
        let session=self.docker_session()?;
        let verdict=crate::docker_lab::compose_folder_problem(&work,&session.project,&compose.images)?
            .map(|problem|problem.replace(['\r','\n']," ")).unwrap_or_else(||"ok".into());
        std::fs::write(&path,format!("{hash}\n{verdict}\n")).map_err(|e|e.to_string())
    }
    pub fn docker_session(&self)->Result<DockerSession,String> {
        let raw=std::fs::read(self.root().join("docker-session.json")).map_err(|_|"Docker 실습 터미널이 아직 준비되지 않았어요. 터미널이 열린 뒤 제출하세요.".to_string())?;
        serde_json::from_slice(&raw).map_err(|e|e.to_string())
    }
    /// Open the learner's (or the narration's) real Bash with Docker reachable. The lesson session
    /// prepared the step's start state; this terminal only records what the learner does next.
    #[cfg(not(target_os="android"))]
    pub fn open_docker_terminal(&self,lab:&crate::docker_lab::TerminalLab)->Result<(crate::setup_terminal::SetupTerminal,tokio::sync::mpsc::Receiver<Vec<u8>>),String> {
        let compose=self.docker_exercise()?.compose.is_some();
        let session=DockerSession{project:lab.project.clone(),container:lab.container.clone()};
        std::fs::write(self.root().join("docker-session.json"),serde_json::to_vec(&session).unwrap()).map_err(|e|e.to_string())?;
        let guard=self.root().join("docker-guard.sh");
        std::fs::write(&guard,crate::docker_lab::TERMINAL_GUARD).map_err(|e|e.to_string())?;
        self.prepare_shell_checkpoint()?;
        // Commands typed before this step (or for an earlier lesson session) do not count here.
        let path=self.docker_checkpoint_path()?;
        let current=std::fs::read(&path).ok().and_then(|raw|serde_json::from_slice::<DockerCheckpoint>(&raw).ok());
        if current.as_ref().is_none_or(|c|c.project!=lab.project) {
            let container_id=if compose{String::new()}else{crate::docker_lab::query(&["inspect","-f","{{.Id}}",&lab.container]).ok().filter(|o|o.0).map(|o|o.1.trim().to_owned()).unwrap_or_default()};
            let image_id=if compose{String::new()}else{crate::docker_lab::query(&["image","inspect","-f","{{.Id}}",self.docker_exercise()?.tag()]).ok().filter(|o|o.0).map(|o|o.1.trim().to_owned()).unwrap_or_default()};
            std::fs::create_dir_all(path.parent().unwrap()).map_err(|e|e.to_string())?;
            let checkpoint=DockerCheckpoint{project:lab.project.clone(),offset:self.shell_completions()?.len(),container_id,image_id};
            std::fs::write(&path,serde_json::to_vec(&checkpoint).unwrap()).map_err(|e|e.to_string())?;
        }
        let mut environment=self.environment();
        let guard_path=guard.to_string_lossy().replace('\\',"/");
        for (key,value) in self.shell_environment() {
            // Load the docker guard function once, before the first prompt is drawn. It comes after
            // the history hook, which must read the exit status of the learner's own command.
            let value=if key=="PROMPT_COMMAND" {format!("{value}; [[ -n ${{__mq3_docker_guard-}} ]] || {{ . \"$MQ3_DOCKER_GUARD\"; __mq3_docker_guard=1; }}")}else{value};
            environment.push((key,value));
        }
        environment.push(("MQ3_DOCKER_GUARD".into(),guard_path));
        environment.extend(lab.environment.iter().cloned());
        if compose {
            // The guard runs `docker compose -f "$MQ3_WORK/compose.yaml"` only after the app's verdict.
            let slash=|path:PathBuf|path.to_string_lossy().replace('\\',"/");
            environment.push(("MQ3_WORK".into(),slash(self.work())));
            environment.push(("MQ3_COMPOSE_VERDICT".into(),slash(self.root().join("docker-verdict"))));
            self.refresh_docker_files()?;
        }
        crate::setup_terminal::SetupTerminal::open_practice(&self.shell_directory()?,&environment)
    }
    pub fn check_docker(&self)->Result<crate::runner::TestReport,String> {
        use crate::runner::{TestReport,TestCaseResult};
        let exercise=self.docker_exercise()?;
        let shell=self.exercise.shell.as_ref().ok_or("Bash 실습이 아니에요.")?;
        let session=self.docker_session()?;
        let checkpoint:DockerCheckpoint=std::fs::read(self.docker_checkpoint_path()?).ok().and_then(|raw|serde_json::from_slice(&raw).ok()).ok_or("이 문제의 시작 기록이 없어요. 터미널을 다시 여세요.")?;
        if checkpoint.project!=session.project{return Err("이 문제의 시작 기록이 현재 실습과 달라요. 터미널을 다시 여세요.".into())}
        let records=self.shell_completions()?;
        if let Some(compose)=&exercise.compose {return self.check_compose(compose,&shell.commands,&session,checkpoint.offset,&records)}
        let mut cases=vec![];
        let mut record=|name:&str,expected:String,actual:String,passed:bool|cases.push(TestCaseResult{input:name.into(),expected,stdout:actual,stderr:String::new(),passed,state:"docker_state".into()});
        let mut cursor=0;
        for item in records.iter().skip(checkpoint.offset) {
            if item.success&&shell.commands.get(cursor).is_some_and(|expected|docker_command_matches(expected,&item.command,&session.container)){cursor+=1;}
        }
        let typed=records.iter().skip(checkpoint.offset).map(|r|format!("{}{}",r.command,if r.success{""}else{"  (실패)"})).collect::<Vec<_>>().join("\n");
        record("터미널에서 실행한 명령",shell.commands.join("\n"),if typed.is_empty(){"아직 실행한 명령이 없어요.".into()}else{typed},cursor==shell.commands.len());
        let query=|args:&[&str]|crate::docker_lab::query(args);
        let goal=&exercise.goal;
        if goal.image_present {
            let present=query(&["image","inspect","-f","{{.Id}}",exercise.tag()])?.0;
            let kept=!checkpoint.image_id.is_empty()&&query(&["image","inspect","-f","{{.Id}}",&checkpoint.image_id])?.0;
            record("이 컴퓨터의 이미지",format!("{} 있음",exercise.tag()),if present||kept{format!("{} 있음",exercise.tag())}else{"없음".into()},present||kept);
        }
        if let Some(expected)=goal.container {
            let (found,status,_)=query(&["inspect","-f","{{.State.Status}}|{{index .Config.Labels \"io.mq3.project\"}}|{{.Id}}|{{.Config.Image}}",&session.container])?;
            let fields:Vec<&str>=status.trim().splitn(4,'|').collect();
            let owned=found&&fields.get(1)==Some(&session.project.as_str());
            let actual=if !found{"없음".to_string()}else if !owned{"이 실습이 만들지 않은 같은 이름의 컨테이너".into()}else{fields[0].to_owned()};
            let wanted=match expected {DockerState::Absent=>"없음",DockerState::Running=>"running",DockerState::Exited=>"exited"};
            record("실습 컨테이너 상태",wanted.into(),actual.clone(),actual==wanted);
            if goal.same_container {
                let id=fields.get(2).copied().unwrap_or_default();
                record("컨테이너 식별자",format!("시작할 때와 같은 {}",short(&checkpoint.container_id)),if id.is_empty(){"없음".into()}else{short(id).into()},owned&&!id.is_empty()&&id==checkpoint.container_id);
            }
            if goal.created_from_image {
                let image=fields.get(3).copied().unwrap_or_default();
                record("컨테이너를 만든 이미지",exercise.tag().into(),image.into(),owned&&image==exercise.tag());
            }
            if goal.logs {
                let (ok,out,err)=if owned{query(&["logs",&session.container])?}else{(false,String::new(),String::new())};
                let lines=out.lines().chain(err.lines()).filter(|l|!l.trim().is_empty()).count();
                record("컨테이너 로그",format!("주 프로세스의 출력"),format!("{lines}줄"),ok&&lines>0);
            }
            if let Some(file)=&goal.file {
                let (ok,out,_)=if owned{query(&["exec",&session.container,"cat",&file.path])?}else{(false,String::new(),String::new())};
                let text=out.trim_end_matches(['\r','\n']).to_owned();
                record(&format!("컨테이너 안 {}",file.path),file.content.clone(),if ok{text.clone()}else{"파일 없음".into()},ok&&text==file.content);
            }
        }
        Ok(TestReport{passed:cases.iter().all(|c|c.passed),cases})
    }
    /// Grade a Compose step by reading only: the commands the learner's shell completed (entered
    /// while the step's fixed files had their current content), the files, and the real engine
    /// state of this step's own project. Nothing is started, built or changed here.
    fn check_compose(&self,compose:&ComposeWork,commands:&[String],session:&DockerSession,offset:usize,records:&[ShellCompletion])->Result<crate::runner::TestReport,String> {
        use crate::runner::{TestReport,TestCaseResult};
        let work=self.work();
        let project=session.project.as_str();
        let mut cases=vec![];
        let mut record=|name:&str,expected:String,actual:String,passed:bool|cases.push(TestCaseResult{input:name.into(),expected,stdout:actual,stderr:String::new(),passed,state:"docker_state".into()});
        let fixed=crate::docker_lab::files_hash(&work,&compose.same_files.iter().map(String::as_str).collect::<Vec<_>>());
        let enters=self.docker_enters();
        let current=|index:usize|compose.same_files.is_empty()||enters.iter().rev().find(|(n,_)|*n<=index).is_some_and(|(_,h)|*h==fixed);
        let mut cursor=0;let mut typed=vec![];
        for (index,item) in records.iter().enumerate().skip(offset) {
            let now=current(index);
            if item.success&&now&&commands.get(cursor).is_some_and(|expected|docker_command_matches(expected,&item.command,"")){cursor+=1;}
            typed.push(format!("{}{}",item.command,if !item.success{"  (실패)"}else if !now{"  (지금 파일로 바꾸기 전)"}else{""}));
        }
        let fixed_names=compose.same_files.join("·");
        record(&if fixed_names.is_empty(){"터미널에서 실행한 명령".to_string()}else{format!("지금의 {fixed_names}로 터미널에서 실행한 명령")},commands.join("\n"),
            if typed.is_empty(){"아직 실행한 명령이 없어요.".into()}else{typed.join("\n")},cursor==commands.len());
        let problem=crate::docker_lab::compose_folder_problem(&work,project,&compose.images)?;
        record("이 폴더의 compose 파일",format!("이 실습에서 실행할 수 있는 파일"),problem.clone().unwrap_or_else(||"실행할 수 있어요".into()),problem.is_none());
        let query=|args:&[&str]|crate::docker_lab::query(args);
        let container=|service:&str|->Result<Option<String>,String>{
            let (ok,out,_)=query(&["ps","-a","--filter",&format!("label=com.docker.compose.project={project}"),"--filter",&format!("label=com.docker.compose.service={service}"),"--filter","label=com.docker.compose.oneoff=False","--format","{{.ID}}"])?;
            Ok(if ok{out.lines().map(str::trim).find(|l|!l.is_empty()).map(str::to_owned)}else{None})
        };
        let running=|id:&Option<String>|->Result<bool,String>{Ok(match id {Some(id)=>{let (ok,out,_)=query(&["inspect","-f","{{.State.Status}}",id])?;ok&&out.trim()=="running"},None=>false})};
        let contains=|text:&str,has:&[String],lacks:&[String]|has.iter().all(|h|text.contains(h.as_str()))&&!lacks.iter().any(|l|text.contains(l.as_str()));
        for check in &compose.checks {
            match check {
                ComposeCheck::Config{what,expect}=>{
                    let (ok,out,err)=crate::docker_lab::compose_query(&work,project,&["config","--format","json"])?;
                    let config:Option<serde_json::Value>=ok.then(||serde_json::from_str(&out).ok()).flatten();
                    let passed=config.as_ref().is_some_and(|c|contains_json(c,expect));
                    record(&format!("compose 설정: {what}"),what.clone(),if config.is_none(){err.trim().to_owned()}else if passed{what.clone()}else{"설정이 달라요".into()},passed);
                }
                ComposeCheck::Running{service}=>{
                    let id=container(service)?;
                    let (state,label)=match &id {Some(id)=>{let (_,out,_)=query(&["inspect","-f","{{.State.Status}}|{{index .Config.Labels \"com.docker.compose.config-hash\"}}",id])?;let mut p=out.trim().splitn(2,'|');(p.next().unwrap_or("").to_owned(),p.next().unwrap_or("").to_owned())},None=>("없음".into(),String::new())};
                    let (_,hash,_)=crate::docker_lab::compose_query(&work,project,&["config","--hash",service])?;
                    let expected=hash.split_whitespace().nth(1).unwrap_or("").to_owned();
                    let current=!label.is_empty()&&label==expected;
                    record(&format!("{service} 컨테이너"),"running · 지금 파일로 만든 컨테이너".into(),
                        format!("{state}{}",if id.is_none(){""}else if current{" · 지금 파일로 만든 컨테이너"}else{" · 파일을 바꾸기 전에 만든 컨테이너"}),state=="running"&&current);
                }
                ComposeCheck::Mount{service,target,volume}=>{
                    let id=container(service)?;
                    let mounts:Vec<serde_json::Value>=match &id {Some(id)=>{let (_,out,_)=query(&["inspect","-f","{{json .Mounts}}",id])?;serde_json::from_str(out.trim()).unwrap_or_default()},None=>vec![]};
                    let found=mounts.iter().find(|m|m["Destination"]==target.as_str());
                    let name=found.and_then(|m|m["Name"].as_str()).unwrap_or("");
                    let kind=found.and_then(|m|m["Type"].as_str()).unwrap_or("");
                    let wanted=volume.as_ref().map(|v|format!("{project}_{v}"));
                    let passed=kind=="volume"&&match &wanted {Some(w)=>name==w,None=>name.starts_with(&format!("{project}_"))};
                    let shown=|n:&str|n.strip_prefix(&format!("{project}_")).unwrap_or(n).to_owned();
                    record(&format!("{service}의 {target}"),format!("이름 있는 볼륨{}",volume.as_ref().map(|v|format!(" {v}")).unwrap_or_default()),
                        if id.is_none(){"컨테이너 없음".into()}else if found.is_none(){"컨테이너 자기 쓰기 레이어(볼륨 없음)".into()}else if kind=="volume"{if name.len()==64&&name.bytes().all(|c|c.is_ascii_hexdigit()){"이름 없는 익명 볼륨".into()}else{format!("볼륨 {}",shown(name))}}else{format!("{kind} 연결")},passed);
                }
                ComposeCheck::Logs{service,has}=>{
                    let id=container(service)?;
                    let text=match &id {Some(id)=>{let (_,out,err)=query(&["logs",id])?;format!("{out}{err}")},None=>String::new()};
                    let passed=contains(&text,has,&[]);
                    record(&format!("{service} 로그"),has.join("\n"),if passed{has.join("\n")}else{text.lines().take(5).collect::<Vec<_>>().join("\n")},passed);
                }
                ComposeCheck::Exec{what,service,command,has,lacks}=>{
                    let id=container(service)?;
                    let (ok,text)=if running(&id)? {let mut args=vec!["exec",id.as_deref().unwrap()];args.extend(command.iter().map(String::as_str));let (ok,out,err)=query(&args)?;(ok,if ok{out}else{err})}else{(false,"실행 중인 컨테이너 없음".into())};
                    let text=text.trim().to_owned();
                    let mut expected=has.join("\n");if !lacks.is_empty(){expected.push_str(&format!(" ({} 없음)",lacks.join("·")));}
                    record(what,expected,if text.is_empty(){"(없음)".into()}else{text.clone()},ok&&contains(&text,has,lacks));
                }
                ComposeCheck::File{path,has,lacks}=>{
                    let text=std::fs::read_to_string(work.join(path)).unwrap_or_default().to_lowercase();
                    let has=has.iter().map(|s|s.to_lowercase()).collect::<Vec<_>>();let lacks=lacks.iter().map(|s|s.to_lowercase()).collect::<Vec<_>>();
                    let passed=contains(&text,&has,&lacks);
                    record(&format!("{path} 내용"),has.join(" · "),if passed{has.join(" · ")}else{"요구한 내용과 달라요".into()},passed);
                }
                ComposeCheck::History{service,order}=>{
                    let image=format!("{project}-{service}");
                    let (ok,out,_)=query(&["history","--no-trunc","--format","{{.CreatedBy}}",&image])?;
                    let layers:Vec<&str>=out.lines().rev().collect();
                    let mut at=0;let mut found=0;
                    for wanted in order {match layers[at..].iter().position(|l|l.contains(wanted.as_str())) {Some(p)=>{at+=p+1;found+=1;},None=>break}}
                    record(&format!("{service} 이미지의 레이어 순서"),order.join(" → "),if !ok{"빌드한 이미지 없음".into()}else if found==order.len(){order.join(" → ")}else{"순서가 달라요".into()},ok&&found==order.len());
                }
                ComposeCheck::Http{service,port,has}=>{
                    let id=container(service)?;
                    let address=match &id {Some(id)=>{let (_,out,_)=query(&["inspect","-f","{{json .NetworkSettings.Ports}}",id])?;
                        let ports:serde_json::Value=serde_json::from_str(out.trim()).unwrap_or_default();
                        ports[format!("{port}/tcp")].as_array().into_iter().flatten().find(|b|b["HostIp"]=="127.0.0.1").and_then(|b|b["HostPort"].as_str()).and_then(|p|p.parse::<u16>().ok())},None=>None};
                    let body=address.map(|p|http_get(p).unwrap_or_else(|e|e));
                    let passed=body.as_deref().is_some_and(|b|b.contains(has.as_str()));
                    record(&format!("PC에서 127.0.0.1로 {service}에 요청"),has.clone(),match (address,&body) {(Some(p),Some(b))=>format!("127.0.0.1:{p} 응답: {}",b.trim()),_=>"127.0.0.1에 공개된 포트 없음".into()},passed);
                }
            }
        }
        Ok(TestReport{passed:cases.iter().all(|c|c.passed),cases})
    }
}
/// One GET to the engine-assigned loopback port: the body of the response.
fn http_get(port:u16)->Result<String,String> {
    use std::io::{Read,Write};
    let address=std::net::SocketAddr::from(([127,0,0,1],port));
    let mut stream=std::net::TcpStream::connect_timeout(&address,std::time::Duration::from_secs(3)).map_err(|e|format!("연결 실패: {e}"))?;
    stream.set_read_timeout(Some(std::time::Duration::from_secs(5))).map_err(|e|e.to_string())?;
    stream.write_all(b"GET / HTTP/1.0\r\nHost: 127.0.0.1\r\nConnection: close\r\n\r\n").map_err(|e|e.to_string())?;
    let mut raw=vec![];stream.take(65536).read_to_end(&mut raw).map_err(|e|format!("응답 실패: {e}"))?;
    let text=String::from_utf8_lossy(&raw).replace("\r\n","\n");
    Ok(text.split_once("\n\n").map(|(_,body)|body.to_owned()).unwrap_or(text))
}
fn short(id:&str)->&str {let id=id.strip_prefix("sha256:").unwrap_or(id);&id[..id.len().min(12)]}

#[cfg(test)]
mod tests {
    use super::docker_command_matches as same;
    const BOX:&str="mq3lab-1a2b3c4d-learn-nginx";
    #[test]
    fn the_container_variable_and_its_real_name_are_the_same_target() {
        for actual in ["docker logs \"$BOX\"","docker logs $BOX","docker logs ${BOX}","docker logs \"${BOX}\"",&format!("docker logs {BOX}"),&format!("docker container logs '{BOX}'")] {
            assert!(same("docker logs \"$BOX\"",actual,BOX),"{actual}");
        }
        assert!(!same("docker logs \"$BOX\"","docker logs other",BOX));
        assert!(!same("docker logs \"$BOX\"","docker logs \"$OTHER\"",BOX));
    }
    #[test]
    fn option_order_and_long_spellings_are_equivalent() {
        let expected="docker run -d --name \"$BOX\" -p 127.0.0.1::80 nginx:1.28-alpine";
        for actual in ["docker run --name \"$BOX\" -d -p 127.0.0.1::80 nginx:1.28-alpine","docker run --detach --name=\"$BOX\" --publish=127.0.0.1::80 nginx:1.28-alpine","docker container run -p 127.0.0.1::80 --name $BOX -d nginx:1.28-alpine"] {
            assert!(same(expected,actual,BOX),"{actual}");
        }
        for actual in ["docker run -d --name \"$BOX\" -p 8080:80 nginx:1.28-alpine","docker run --name \"$BOX\" -p 127.0.0.1::80 nginx:1.28-alpine","docker run -d --name \"$BOX\" -p 127.0.0.1::80 nginx:latest","docker run -d --name \"$BOX\" -p 127.0.0.1::80 nginx:1.28-alpine; docker ps"] {
            assert!(!same(expected,actual,BOX),"{actual}");
        }
        assert!(same("docker ps","docker container ls",BOX));
        assert!(!same("docker ps","docker ps -a",BOX));
        assert!(!same("docker ps","docker images",BOX));
    }
    #[test]
    fn compose_commands_compare_by_subcommand_options_and_service() {
        for actual in ["docker compose up --detach","docker compose up -d ","docker  compose up -d"] {assert!(same("docker compose up -d",actual,""),"{actual}");}
        assert!(same("docker compose run --rm -T client","docker compose run -T --rm client",""));
        assert!(same("docker compose up -d --build --force-recreate","docker compose up --force-recreate --build -d",""));
        for actual in ["docker compose up","docker compose down","docker compose up -d web","docker compose -f x.yaml up -d","docker compose up -d; docker compose down"] {
            assert!(!same("docker compose up -d",actual,""),"{actual}");
        }
        // Words after the service are the command run inside it, compared in order.
        assert!(!same("docker compose exec memo cat /memo/list.txt","docker compose exec memo cat /memo/other.txt",""));
        // A plain shell command of a Compose step uses the Bash lessons' comparison.
        assert!(same("echo 빵 >> menu.txt","echo 빵>>menu.txt",""));
        assert!(!same("echo 빵 >> menu.txt","echo 빵 > menu.txt",""));
    }
    #[test]
    fn compose_checks_read_only_and_match_configuration_parts() {
        use super::{contains_json,read_only};
        let config=serde_json::json!({"services":{"client":{"command":["wget","http://web:8080"],"networks":{"front":null}}}});
        assert!(contains_json(&config,&serde_json::json!({"services":{"client":{"command":["http://web:8080"],"networks":{"front":null}}}})));
        assert!(!contains_json(&config,&serde_json::json!({"services":{"client":{"networks":{"back":null}}}})));
        assert!(!contains_json(&config,&serde_json::json!({"services":{"client":{"command":["http://localhost:8080"]}}})));
        let strings=|v:&[&str]|v.iter().map(|s|s.to_string()).collect::<Vec<_>>();
        assert!(read_only(&strings(&["cat","/memo/list.txt"])));
        assert!(read_only(&strings(&["psql","-U","postgres","-c","SELECT title FROM memo"])));
        for command in [&["rm","/memo/list.txt"][..],&["cat","../etc/passwd"],&["psql","-c","SELECT 1; DROP TABLE memo"],&["psql","-c","DELETE FROM memo"],&["sh","-c","cat /x"]] {
            assert!(!read_only(&strings(command)),"{command:?}");
        }
    }
    #[test]
    fn the_command_inside_exec_stays_one_exact_word() {
        let expected="docker exec \"$BOX\" sh -c 'echo hello > /memo.txt; cat /memo.txt'";
        assert!(same(expected,"docker exec $BOX sh -c \"echo hello > /memo.txt; cat /memo.txt\"",BOX));
        assert!(!same(expected,"docker exec \"$BOX\" sh -c 'echo bye > /memo.txt; cat /memo.txt'",BOX));
        assert!(!same(expected,"docker exec \"$BOX\" sh -c 'echo hello > /memo.txt'",BOX));
        assert!(!same(expected,"docker exec \"$BOX\" sh -c \"$(echo x)\"",BOX));
    }
}
