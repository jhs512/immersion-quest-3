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
    pub image:String,
    /// The name suffix of the lesson's container: `$BOX` is `<owned project>-<container>`.
    pub container:String,
    /// The container port the app publishes on 127.0.0.1 with an engine-chosen host port when it
    /// prepares a start state itself.
    pub port:u16,
    #[serde(default)] pub start:DockerStart,
    pub goal:DockerGoal,
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
const VALUED:&[&str]=&["--name","-p","-e","--env","-w","--workdir","-u","--user","-t","--time","-s","--signal","-n","--tail","--since","--until","--format","-f","--filter","--label","-l"];
/// `docker <sub> …` as (subcommand, sorted options, ordered operands).
fn docker_parts(words:&[String])->Option<(String,Vec<(String,String)>,Vec<String>)> {
    let mut rest=words.strip_prefix(&["docker".to_string()])?.to_vec();
    if rest.first().is_some_and(|w|w=="container"||w=="image") {
        let group=rest.remove(0);
        let sub=rest.first()?.clone();
        let mapped=match (group.as_str(),sub.as_str()) {("container","ls"|"list"|"ps")=>"ps",("image","ls"|"list")=>"images",(_,other)=>other};
        rest[0]=mapped.into();
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
        if VALUED.contains(&flag.as_str())&&!(sub=="logs"&&flag=="-f")&&!(sub=="exec"&&flag=="-t")&&!(sub=="run"&&flag=="-t") {
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
    pub fn docker_session(&self)->Result<DockerSession,String> {
        let raw=std::fs::read(self.root().join("docker-session.json")).map_err(|_|"Docker 실습 터미널이 아직 준비되지 않았어요. 터미널이 열린 뒤 제출하세요.".to_string())?;
        serde_json::from_slice(&raw).map_err(|e|e.to_string())
    }
    /// Open the learner's (or the narration's) real Bash with Docker reachable. The lesson session
    /// prepared the step's start state; this terminal only records what the learner does next.
    #[cfg(not(target_os="android"))]
    pub fn open_docker_terminal(&self,lab:&crate::docker_lab::TerminalLab)->Result<(crate::setup_terminal::SetupTerminal,tokio::sync::mpsc::Receiver<Vec<u8>>),String> {
        self.docker_exercise()?;
        let session=DockerSession{project:lab.project.clone(),container:lab.container.clone()};
        std::fs::write(self.root().join("docker-session.json"),serde_json::to_vec(&session).unwrap()).map_err(|e|e.to_string())?;
        let guard=self.root().join("docker-guard.sh");
        std::fs::write(&guard,crate::docker_lab::TERMINAL_GUARD).map_err(|e|e.to_string())?;
        self.prepare_shell_checkpoint()?;
        // Commands typed before this step (or for an earlier lesson session) do not count here.
        let path=self.docker_checkpoint_path()?;
        let current=std::fs::read(&path).ok().and_then(|raw|serde_json::from_slice::<DockerCheckpoint>(&raw).ok());
        if current.as_ref().is_none_or(|c|c.project!=lab.project) {
            let container_id=crate::docker_lab::query(&["inspect","-f","{{.Id}}",&lab.container]).ok().filter(|o|o.0).map(|o|o.1.trim().to_owned()).unwrap_or_default();
            let image_id=crate::docker_lab::query(&["image","inspect","-f","{{.Id}}",self.docker_exercise()?.tag()]).ok().filter(|o|o.0).map(|o|o.1.trim().to_owned()).unwrap_or_default();
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
    fn the_command_inside_exec_stays_one_exact_word() {
        let expected="docker exec \"$BOX\" sh -c 'echo hello > /memo.txt; cat /memo.txt'";
        assert!(same(expected,"docker exec $BOX sh -c \"echo hello > /memo.txt; cat /memo.txt\"",BOX));
        assert!(!same(expected,"docker exec \"$BOX\" sh -c 'echo bye > /memo.txt; cat /memo.txt'",BOX));
        assert!(!same(expected,"docker exec \"$BOX\" sh -c 'echo hello > /memo.txt'",BOX));
        assert!(!same(expected,"docker exec \"$BOX\" sh -c \"$(echo x)\"",BOX));
    }
}
