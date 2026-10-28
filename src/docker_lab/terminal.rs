//! Docker CLI lessons in the learner's real terminal.
//!
//! The lesson session owns one Docker project for the learner and a separate one for the
//! narration. Both stay for the whole lesson: moving between steps or running a command again
//! never recreates a container. A step's start state is prepared once (only what is missing is
//! made), the 초기화 button restores it exactly, and leaving the lesson removes only resources
//! carrying the project's ownership label. The learner's Bash gets the real `docker` CLI plus a
//! small guard function (TERMINAL_GUARD) that adds that label to containers it creates and
//! refuses changes to containers, images, volumes and networks this lesson does not own.
use super::*;
use crate::git_practice::{DockerExercise,DockerStart};

/// What a practice terminal needs to reach this lesson's Docker resources.
#[derive(Clone,Debug)]
pub struct TerminalLab {
    pub project:String,
    /// The real name behind `$BOX`.
    pub container:String,
    pub environment:Vec<(String,String)>,
    /// What the app prepared for this step's start, shown to the learner.
    pub prepared:Option<String>,
}

/// Sourced by the practice Bash before its first prompt (Bash 3.2 compatible). Every allowed
/// command is the real Docker CLI with its own output; nothing is simulated here.
pub const TERMINAL_GUARD:&str=r#"# MQ 실습 터미널의 docker: 입력한 명령은 실제 Docker CLI가 실행하고 출력도 그대로 보여요.
# 이 수업이 만드는 컨테이너에 소유 라벨을 붙여요. 이 컴퓨터의 다른 Docker 자원을 바꾸거나 지우는 명령은 막아요.
__mq3_refuse() { printf 'MQ 실습 터미널: %s\n' "$1" >&2; return 2; }
__mq3_owned() {
  [ "$(command docker inspect -f '{{index .Config.Labels "io.mq3.project"}}' "$1" 2>/dev/null)" = "$MQ3_PROJECT" ]
}
__mq3_publish() {
  case "$1" in 127.0.0.1::*|127.0.0.1:0:*) return 0 ;; esac
  __mq3_refuse "포트는 127.0.0.1::80처럼 쓰세요. 이 컴퓨터 안에서만, Docker가 고른 빈 포트로 열어야 다른 프로그램의 포트와 부딪히지 않아요."
}
__mq3_files_hash() {
  local h
  if command -v sha256sum >/dev/null 2>&1; then h=$(cat "$MQ3_WORK/compose.yaml" "$MQ3_WORK/Dockerfile" "$MQ3_WORK/.env" 2>/dev/null | sha256sum)
  else h=$(cat "$MQ3_WORK/compose.yaml" "$MQ3_WORK/Dockerfile" "$MQ3_WORK/.env" 2>/dev/null | shasum -a 256); fi
  printf '%s' "${h%% *}"
}
# The app checks compose.yaml and Dockerfile right before each Enter and writes its verdict with the
# files' hash. Compose runs only files the app checked, exactly as they are now.
__mq3_compose_checked() {
  local want='' verdict=''
  if [ -z "${MQ3_COMPOSE_VERDICT-}" ] || [ ! -f "$MQ3_COMPOSE_VERDICT" ]; then __mq3_refuse "이 문제의 compose 파일 확인 기록이 없어요. 문제를 다시 열어 주세요."; return 2; fi
  { IFS= read -r want; IFS= read -r verdict; } < "$MQ3_COMPOSE_VERDICT"
  if [ "$want" != "$(__mq3_files_hash)" ]; then __mq3_refuse "compose.yaml이나 Dockerfile이 방금 바뀌었어요. 같은 명령을 한 번 더 입력하면 바뀐 파일을 확인한 뒤 실행해요."; return 2; fi
  [ "$verdict" = ok ] && return 0
  __mq3_refuse "$verdict"; return 2
}
__mq3_compose() {
  local sub="${1-}" arg next=''
  if [ -z "${MQ3_WORK-}" ]; then __mq3_refuse "이 문제에서는 docker compose를 쓰지 않아요."; return 2; fi
  case "$sub" in
    -*) __mq3_refuse "docker compose 바로 뒤에는 up·ps 같은 명령을 쓰세요. 이 터미널은 -f·-p 없이 이 폴더의 compose.yaml을 이 문제의 이름으로 실행해요."; return 2 ;;
    ''|version|ls) command docker compose "$@"; return ;;
  esac
  shift
  case "$sub" in
    ps|logs|config|images|port|top|events) ;;
    up|down|run|exec|build|restart|start|stop|create|rm|kill|pause|unpause|pull|wait)
      for arg in "$@"; do
        if [ -n "$next" ]; then next=''; continue; fi
        case "$arg" in
          --rmi|--rmi=*|--push)
            __mq3_refuse "이 실습 터미널에서는 docker compose $sub ${arg%%=*}를 쓰지 않아요. 함께 쓰는 이미지를 지키려고 막았어요."; return 2 ;;
          -v|--volume|--volume=*|-p|--publish|--publish=*|--service-ports|--privileged|--cap-add|--cap-add=*|--cap-drop|--cap-drop=*)
            case "$sub:$arg" in down:-v|rm:-v) continue ;; esac
            __mq3_refuse "이 실습 터미널에서는 docker compose $sub에 ${arg%%=*}를 쓰지 않아요. 포트·폴더 연결과 권한은 compose.yaml에만 쓰고 앱이 확인해요."; return 2 ;;
          -e|--env|-w|--workdir|-u|--user|--name|--entrypoint|-l|--label|--index|--pull|-t|--timeout|--scale|--wait-timeout|-s|--signal) next=value ;;
          -*) ;;
          *) case "$sub" in run|exec) break ;; esac ;;
        esac
      done
      __mq3_compose_checked || return 2 ;;
    *) __mq3_refuse "이 실습 터미널에서는 docker compose $sub 명령을 쓰지 않아요."; return 2 ;;
  esac
  COMPOSE_PROFILES= COMPOSE_ENV_FILES= command docker compose -p "$MQ3_PROJECT" -f "$MQ3_WORK/compose.yaml" "$sub" "$@"
}
docker() {
  local sub="${1-}" arg next='' value target
  if [ "$sub" = compose ]; then shift; __mq3_compose "$@"; return; fi
  if [ "$sub" = volume ] || [ "$sub" = network ]; then
    case "${2-}" in ls|list|inspect) command docker "$@"; return ;; esac
    __mq3_refuse "이 실습 터미널에서는 docker $sub ${2-} 명령을 쓰지 않아요. 볼륨·네트워크는 compose.yaml로 만들고 down으로 정리해요."; return 2
  fi
  if [ "$sub" = container ] || [ "$sub" = image ]; then
    case "$sub:${2-}" in
      container:ls|container:list|container:ps) shift 2; set -- ps "$@" ;;
      image:ls|image:list) shift 2; set -- images "$@" ;;
      image:pull|image:inspect|image:history|container:*) shift ;;
      *) __mq3_refuse "이 실습 터미널에서는 docker image ${2-} 명령을 쓰지 않아요. 함께 쓰는 이미지를 지키려고 막았어요."; return 2 ;;
    esac
    sub="${1-}"
  fi
  case "$sub" in
    ''|-h|--help|help|-v|--version|version|info|pull|images|ps|logs|inspect|port|top|stats|diff|history|search|events)
      command docker "$@" ;;
    run|create)
      shift
      for arg in "$@"; do
        if [ -n "$next" ]; then
          if [ "$next" = publish ]; then __mq3_publish "$arg" || return 2; fi
          next=''; continue
        fi
        case "$arg" in
          --) break ;;
          -p|--publish) next=publish ;;
          --publish=*) __mq3_publish "${arg#--publish=}" || return 2 ;;
          -P|--publish-all|--privileged|--privileged=*|--network|--network=*|--net|--net=*|--pid|--pid=*|--ipc|--ipc=*|--uts|--uts=*|--userns|--userns=*|--cap-add|--cap-add=*|--device|--device=*|-v|--volume|--volume=*|--mount|--mount=*|--volumes-from|--volumes-from=*|--security-opt|--security-opt=*|--cgroup-parent|--cgroup-parent=*|--cgroupns|--cgroupns=*)
            __mq3_refuse "이 실습 터미널에서는 ${arg%%=*}를 쓰지 않아요. 이 컴퓨터의 파일·네트워크·권한을 바꾸지 않으려고 막았어요."; return 2 ;;
          --name|-e|--env|--env-file|-w|--workdir|-u|--user|-h|--hostname|--entrypoint|--restart|-l|--label|-m|--memory|--cpus|--platform|--pull|--add-host|--dns|--expose|--stop-signal|--stop-timeout|--log-driver|--log-opt|--health-cmd|--health-interval|--tmpfs|-a|--attach|--cidfile)
            next=value ;;
          --*) ;;
          -?*)
            # A cluster such as -dp: a trailing p takes the next word as its value.
            value="${arg#-}"
            case "$value" in
              *[vP]*) __mq3_refuse "이 실습 터미널에서는 ${arg}를 쓰지 않아요. 볼륨 연결과 모든 포트 공개는 막았어요."; return 2 ;;
              *p) next=publish ;;
              *p*) __mq3_publish "${value#*p}" || return 2 ;;
              *[ewuhlma]) next=value ;;
            esac ;;
          *) break ;;
        esac
      done
      command docker "$sub" --label "$MQ3_OWNER_LABEL" "$@" ;;
    stop|start|restart|kill|rm|pause|unpause|rename|update|wait|attach|exec|cp|commit|export)
      shift
      for arg in "$@"; do
        if [ -n "$next" ]; then next=''; continue; fi
        case "$arg" in
          -t|--time|-s|--signal|-e|--env|--env-file|-w|--workdir|-u|--user|--detach-keys|-a|--author|-c|--change|-m|--message|-o|--output) next=value; continue ;;
          -*) continue ;;
        esac
        target="$arg"
        if [ "$sub" = cp ]; then case "$target" in *:*) target="${target%%:*}" ;; *) continue ;; esac; fi
        __mq3_owned "$target" || { __mq3_refuse "이 실습이 만든 컨테이너만 바꿀 수 있어요: $target"; return 2; }
        case "$sub" in exec|rename|attach|commit|export|update) break ;; esac
      done
      command docker "$sub" "$@" ;;
    *) __mq3_refuse "이 실습 터미널에서는 docker $sub 명령을 쓰지 않아요. 이 컴퓨터의 다른 Docker 자원(이미지·볼륨·네트워크)을 지키려고 막았어요." ;;
  esac
}
readonly MQ3_PROJECT MQ3_OWNER_LABEL MQ3_WORK MQ3_COMPOSE_VERDICT 2>/dev/null
"#;

/// One read-only or owned-resource Docker CLI call from the app: (success, stdout, stderr).
pub fn query(args:&[&str])->Result<(bool,String,String),String> {
    let cli=cli().ok_or_else(||format!("Docker를 찾지 못했어요. Docker Desktop을 설치하고 실행하세요. 설치 안내: {INSTALL_GUIDE}"))?;
    let output=docker(&cli,args,60)?;
    Ok((output.success,output.stdout,output.stderr))
}

fn status(cli:&Path,name:&str,project:&str)->Result<Option<String>,String> {
    let output=docker(cli,&["inspect","-f","{{.State.Status}}|{{index .Config.Labels \"io.mq3.project\"}}",name],60)?;
    if !output.success{return Ok(None)}
    let text=output.stdout.trim().to_owned();
    let (state,owner)=text.split_once('|').unwrap_or((&text,""));
    // A same-named container this lesson does not own is never touched.
    if owner!=project{return Err(format!("{name} 이름의 컨테이너가 이미 있어요. 이 실습이 만든 것이 아니라서 그대로 두었어요."))}
    Ok(Some(state.to_owned()))
}

fn checked(output:Output,what:&str)->Result<(),String> {
    if output.success{Ok(())}else{Err(format!("{what}하지 못했어요.\n{}",output.stderr.trim()))}
}

/// The image the app uses to prepare a container: the tag when it is the pinned image, so
/// `docker ps` shows the name the learner typed; otherwise the pinned reference itself.
fn image_for(cli:&Path,exercise:&DockerExercise)->Result<String,String> {
    ensure_images(cli,std::slice::from_ref(&exercise.image))?;
    let id=|reference:&str|docker(cli,&["image","inspect","-f","{{.Id}}",reference],60).ok().filter(|o|o.success).map(|o|o.stdout.trim().to_owned());
    Ok(if id(exercise.tag()).is_some()&&id(exercise.tag())==id(&exercise.image){exercise.tag().to_owned()}else{exercise.image.clone()})
}

fn create(cli:&Path,lab:&Lab,name:&str,exercise:&DockerExercise)->Result<(),String> {
    let image=image_for(cli,exercise)?;
    let label=format!("{OWNER_LABEL}={}",lab.project);let publish=format!("127.0.0.1::{}",exercise.port);
    checked(docker(cli,&["run","-d","--name",name,"--label",&label,"-p",&publish,&image],120)?,"실습 컨테이너를 준비")?;
    // Wait until the server answers inside the container, so the step starts from a real server.
    let deadline=Instant::now()+Duration::from_secs(20);
    while Instant::now()<deadline {
        if docker(cli,&["exec",name,"wget","-q","-O","/dev/null",&format!("http://127.0.0.1:{}",exercise.port)],10).is_ok_and(|o|o.success){return Ok(())}
        std::thread::sleep(Duration::from_millis(150));
    }
    Err("실습 서버가 시작했는지 확인하지 못했어요. 초기화해 다시 여세요.".into())
}

/// Make the step's start state. `exact` (narration, or after 초기화) also undoes later work;
/// otherwise only what is missing is made and the learner's containers stay as they are.
fn prepare_start(cli:&Path,lab:&Lab,name:&str,exercise:&DockerExercise,exact:bool)->Result<Option<String>,String> {
    let current=status(cli,name,&lab.project)?;
    let running=current.as_deref()==Some("running");
    Ok(match exercise.start {
        DockerStart::Absent=>{
            if exact&&current.is_some() {checked(docker(cli,&["rm","-f",name],60)?,"이전 실습 컨테이너를 정리")?;Some("이 문제의 시작 상태로 실습 컨테이너를 지웠어요.".into())}else{None}
        }
        DockerStart::Running=>match current {
            None=>{create(cli,lab,name,exercise)?;Some("이 문제를 위해 실습 컨테이너를 만들어 실행해 두었어요.".into())}
            Some(_) if running=>None,
            Some(_)=>{checked(docker(cli,&["start",name],60)?,"실습 컨테이너를 시작")?;Some("이 문제를 위해 멈춰 있던 실습 컨테이너를 실행해 두었어요.".into())}
        },
        DockerStart::Stopped=>match current {
            None=>{create(cli,lab,name,exercise)?;checked(docker(cli,&["stop",name],60)?,"실습 컨테이너를 멈추")?;Some("이 문제를 위해 실습 컨테이너를 만든 뒤 멈춰 두었어요.".into())}
            Some(_) if running=>{checked(docker(cli,&["stop",name],60)?,"실습 컨테이너를 멈추")?;Some("이 문제의 시작 상태로 실습 컨테이너를 멈춰 두었어요.".into())}
            Some(_)=>None,
        },
    })
}

fn environment(cli:&Path,lab:&Lab,name:&str)->Vec<(String,String)> {
    let mut environment=vec![
        ("PATH".into(),search_path(cli).to_string_lossy().into_owned()),
        ("DOCKER_CLI_HINTS".into(),"false".into()),
        // Git Bash would rewrite /memo.txt or /usr/share/... into Windows paths before docker sees them.
        ("MSYS_NO_PATHCONV".into(),"1".into()),("MSYS2_ARG_CONV_EXCL".into(),"*".into()),
        ("BOX".into(),name.into()),("MQ3_PROJECT".into(),lab.project.clone()),
        ("MQ3_OWNER_LABEL".into(),format!("{OWNER_LABEL}={}",lab.project)),
    ];
    // The practice shell has a private HOME. Docker's own settings (the selected engine context
    // and credential helpers) stay the user's, so the terminal reaches the same engine as the app.
    if std::env::var_os("DOCKER_CONFIG").is_none() {
        let home=std::env::var_os(if cfg!(windows){"USERPROFILE"}else{"HOME"});
        if let Some(config)=home.map(|home|PathBuf::from(home).join(".docker")).filter(|path|path.is_dir()) {
            environment.push(("DOCKER_CONFIG".into(),config.to_string_lossy().into_owned()));
        }
    }
    environment
}

impl LessonSession {
    /// Prepare this lesson's Docker resources for a step's terminal (blocking: Docker Desktop may
    /// be started and an image pulled). `demo` is the narration's own project; it always starts
    /// from the exact start state, so it never needs or touches the learner's containers.
    pub fn terminal(&self,demo:bool,step:&str,exercise:&DockerExercise)->Result<TerminalLab,String> {
        self.ensure_open()?;
        let cli=cli().ok_or_else(||format!("Docker가 설치되지 않았어요. Docker Desktop을 설치하고 실행한 뒤 이 문제를 다시 여세요. 설치 안내: {INSTALL_GUIDE}"))?;
        ensure_engine(&cli)?;
        if let Some(compose)=&exercise.compose {return self.compose_terminal(&cli,demo,step,&compose.images)}
        let mut terminals=self.0.terminals.lock().unwrap_or_else(|e|e.into_inner());
        self.ensure_open()?;
        let key=if demo{"demo"}else{"learn"};
        if !terminals.contains_key(key) {
            let lab=Lab::open_for(&cli,&format!("docker-terminal:{key}:{}",crate::issue_progress::new_id()))?;
            terminals.insert(key.to_owned(),TerminalState{lab,prepared:BTreeSet::new(),restore:BTreeSet::new()});
        }
        let state=terminals.get_mut(key).unwrap();
        let name=format!("{}-{}",state.lab.project,exercise.container);
        let exact=demo||state.restore.remove(step);
        let prepared=if exact||!state.prepared.contains(step) {prepare_start(&cli,&state.lab,&name,exercise,exact)?}else{None};
        state.prepared.insert(step.to_owned());
        self.ensure_open()?;
        Ok(TerminalLab{project:state.lab.project.clone(),container:name.clone(),environment:environment(&cli,&state.lab,&name),prepared})
    }
    /// A Compose step: its own owned project (one per step, so services, volumes and built images
    /// of different steps never meet), kept for the whole lesson. The learner's `docker compose`
    /// creates everything; the app only pulls the pinned images first. The narration gets a new
    /// project every time (its exact start: nothing yet); 초기화 replaces the learner's project,
    /// which removes only resources carrying its labels.
    fn compose_terminal(&self,cli:&Path,demo:bool,step:&str,images:&[String])->Result<TerminalLab,String> {
        ensure_images(cli,images)?;
        let mut terminals=self.0.terminals.lock().unwrap_or_else(|e|e.into_inner());
        self.ensure_open()?;
        let key=format!("{}:{step}",if demo{"demo"}else{"learn"});
        let mut prepared=None;
        let fresh=demo||terminals.get(&key).is_some_and(|state|state.restore.contains(step));
        if fresh&&terminals.remove(&key).is_some()&&!demo {
            prepared=Some("이 문제의 시작 상태로 이 문제가 만든 컨테이너·네트워크·볼륨·빌드 이미지를 지웠어요.".to_owned());
        }
        if !terminals.contains_key(&key) {
            let lab=Lab::open_for(cli,&format!("docker-compose:{key}:{}",crate::issue_progress::new_id()))?;
            terminals.insert(key.clone(),TerminalState{lab,prepared:BTreeSet::new(),restore:BTreeSet::new()});
        }
        let state=&terminals[&key];
        self.ensure_open()?;
        let mut environment=environment(cli,&state.lab,"");
        environment.retain(|(name,_)|name!="BOX");
        environment.extend([("COMPOSE_PROJECT_NAME".to_owned(),state.lab.project.clone()),("BUILDKIT_PROGRESS".into(),"plain".into()),
            ("COMPOSE_PROGRESS".into(),"plain".into()),("COMPOSE_MENU".into(),"false".into())]);
        Ok(TerminalLab{project:state.lab.project.clone(),container:String::new(),environment,prepared})
    }
    /// 초기화: the next learner terminal of this step restores its exact start state. Other steps'
    /// state and the narration's project are untouched.
    pub fn reset_terminal(&self,step:&str)->Result<(),String> {
        self.ensure_open()?;
        let mut terminals=self.0.terminals.lock().unwrap_or_else(|e|e.into_inner());
        // No terminal yet in this session: the first one prepares the start state anyway.
        for key in ["learn".to_owned(),format!("learn:{step}")] {
            if let Some(state)=terminals.get_mut(&key){state.restore.insert(step.to_owned());}
        }
        Ok(())
    }
    #[cfg(test)]
    pub(crate) fn terminal_projects(&self)->Vec<String> {self.0.terminals.lock().unwrap().values().map(|s|s.lab.project.clone()).collect()}
}
