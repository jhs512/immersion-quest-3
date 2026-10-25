//! Real Docker labs for lessons. Directory isolation is not an OS sandbox.
//!
//! One run owns one Compose project named `mq3lab-…`. The lesson's authored lab script (`lab.sh`)
//! runs in Bash with that project name. Before the script starts, the learner's compose file is
//! checked: published ports must stay on 127.0.0.1 with an engine-chosen host port, and nothing may
//! use a fixed container name, host networking, privileges or a bind mount outside the run folder.
//! When the run ends — success, failure, timeout or a dropped caller — only containers, networks,
//! volumes and built images labelled with that project are removed. A project left behind by a
//! killed app is found by the same labels and removed at the next start or the next run, unless
//! its run lock is still held by a live process. Images the lesson pulls (digest-pinned official
//! images) stay cached like any `docker pull`; the user's own resources are never listed by name
//! or touched.
use crate::{repository_course::Task, runner::Execution};
use std::{collections::BTreeSet, io::Read, path::{Path,PathBuf}, process::{Command,Stdio}, time::{Duration,Instant}};

pub const PREFIX:&str="mq3lab-";
/// Label the lab script adds to anything it creates outside Compose (`docker build`, `docker run`).
pub const OWNER_LABEL:&str="io.mq3.project";
const COMPOSE_LABEL:&str="com.docker.compose.project";
const LAB_SECONDS:u64=300;
const PULL_SECONDS:u64=1200;
const OUTPUT:usize=65536;
pub const INSTALL_GUIDE:&str="https://docs.docker.com/get-started/get-docker/";

/// Official images pinned by a multi-platform index digest, e.g. `busybox:1.36@sha256:…`.
pub fn valid_image(reference:&str)->bool {
    let Some((name,digest))=reference.split_once("@sha256:") else{return false};
    let Some((repo,tag))=name.split_once(':') else{return false};
    matches!(repo,"busybox"|"postgres"|"mysql")&&!tag.is_empty()&&tag.len()<64
        &&tag.bytes().all(|c|c.is_ascii_alphanumeric()||b"._-".contains(&c))
        &&digest.len()==64&&digest.bytes().all(|c|c.is_ascii_digit()||(b'a'..=b'f').contains(&c))
}

pub fn validate_task(task:&Task)->Result<(),String> {
    if task.interaction.is_some()||task.git_terminal.is_some()||task.checker.is_some()||!task.mutations.is_empty() {
        return Err("Docker 실습은 실행 결과로만 판정해요.".into())
    }
    if !task.files.contains_key("lab.sh")||task.entry_file.is_empty()||task.entry_file=="lab.sh"||task.files.contains_key(&task.entry_file) {
        return Err("Docker 실습 스크립트와 학습자 파일을 확인하세요.".into())
    }
    if task.docker_images.is_empty()||task.docker_images.len()>4||!task.docker_images.iter().all(|image|valid_image(image)) {
        return Err("Docker 실습 이미지는 digest로 고정한 공식 이미지만 써요.".into())
    }
    if task.variations.iter().any(|v|!v.values.is_empty()||!v.expected_files.is_empty()) {
        return Err("Docker 실습의 변형 검사는 준비 파일만 바꿔요.".into())
    }
    crate::library_sets::validate(&task.libraries)
}

pub fn cli()->Option<PathBuf> {
    if let Some(path)=std::env::var_os("MOLIP_DOCKER") {return Some(path.into())}
    let file=if cfg!(windows){"docker.exe"}else{"docker"};
    #[allow(unused_mut)]
    let mut directories:Vec<PathBuf>=std::env::split_paths(&std::env::var_os("PATH").unwrap_or_default()).collect();
    #[cfg(windows)] for key in ["ProgramFiles","ProgramW6432"] {
        if let Some(root)=std::env::var_os(key){directories.push(PathBuf::from(root).join("Docker/Docker/resources/bin"));}
    }
    #[cfg(target_os="macos")] {
        // A Finder launch has a minimal PATH; Docker Desktop links its CLI into these places.
        directories.extend(["/usr/local/bin","/opt/homebrew/bin","/Applications/Docker.app/Contents/Resources/bin"].map(PathBuf::from));
        if let Some(home)=std::env::var_os("HOME"){directories.push(PathBuf::from(home).join(".docker/bin"));}
    }
    #[cfg(target_os="linux")] directories.extend(["/usr/bin","/usr/local/bin"].map(PathBuf::from));
    directories.into_iter().map(|directory|directory.join(file)).find(|path|path.is_file())
}

fn search_path(cli:&Path)->std::ffi::OsString {
    let mut paths:Vec<PathBuf>=cli.parent().map(Path::to_path_buf).into_iter().collect();
    #[cfg(target_os="macos")] {
        // Credential helpers (docker-credential-desktop) must be found for a pull to succeed.
        paths.extend(["/usr/local/bin","/opt/homebrew/bin","/Applications/Docker.app/Contents/Resources/bin"].map(PathBuf::from));
        if let Some(home)=std::env::var_os("HOME"){paths.push(PathBuf::from(home).join(".docker/bin"));}
    }
    paths.extend(std::env::split_paths(&std::env::var_os("PATH").unwrap_or_default()));
    std::env::join_paths(paths).unwrap_or_default()
}

fn prepare(command:&mut Command,cli:&Path) {
    command.env("PATH",search_path(cli)).env("DOCKER_CLI_HINTS","false").env("COMPOSE_ANSI","never")
        .env("COMPOSE_MENU","false").env("BUILDKIT_PROGRESS","plain")
        // Git Bash would rewrite /data or /var/lib/... into Windows paths before docker sees them.
        .env("MSYS_NO_PATHCONV","1").env("MSYS2_ARG_CONV_EXCL","*")
        .env_remove("COMPOSE_FILE").env_remove("COMPOSE_PROFILES").env_remove("COMPOSE_ENV_FILES")
        .env_remove("COMPOSE_PROJECT_NAME").env_remove("COMPOSE_PATH_SEPARATOR")
        .env_remove("JAVA_TOOL_OPTIONS").env_remove("JDK_JAVA_OPTIONS").env_remove("_JAVA_OPTIONS").env_remove("CLASSPATH");
    #[cfg(windows)] {use std::os::windows::process::CommandExt;command.creation_flags(0x08000000);}
    #[cfg(unix)] {use std::os::unix::process::CommandExt;command.process_group(0);}
}

struct Output { success:bool, timed_out:bool, limited:bool, stdout:String, stderr:String }

/// Run one owned process tree with a time limit; the whole tree is ended on timeout.
fn execute(mut command:Command,input:&str,seconds:u64)->Result<Output,String> {
    command.stdin(Stdio::piped()).stdout(Stdio::piped()).stderr(Stdio::piped());
    let mut child=command.spawn().map_err(|e|format!("실행 도구를 시작하지 못했어요: {e}"))?;
    let scope=match crate::process_scope::CommandScope::attach(&child){Ok(scope)=>scope,Err(e)=>{let _=child.kill();let _=child.wait();return Err(format!("실습 프로세스 소유: {e}"))}};
    let overflow=std::sync::Arc::new(std::sync::atomic::AtomicBool::new(false));
    fn collect(mut pipe:impl Read+Send+'static,overflow:std::sync::Arc<std::sync::atomic::AtomicBool>)->std::thread::JoinHandle<Vec<u8>> {
        std::thread::spawn(move||{let mut result=vec![];let mut block=[0;8192];while let Ok(n)=pipe.read(&mut block){if n==0{break}let keep=n.min(OUTPUT.saturating_sub(result.len()));result.extend_from_slice(&block[..keep]);if keep<n{overflow.store(true,std::sync::atomic::Ordering::Relaxed);}}result})
    }
    let out=collect(child.stdout.take().unwrap(),overflow.clone());let err=collect(child.stderr.take().unwrap(),overflow.clone());
    if let Some(mut stdin)=child.stdin.take() {use std::io::Write;let _=stdin.write_all(input.as_bytes());}
    let started=Instant::now();let mut timed_out=false;
    let status=loop {
        if let Some(status)=child.try_wait().map_err(|e|e.to_string())?{break status}
        if started.elapsed()>Duration::from_secs(seconds){timed_out=true;let _=scope.terminate();let _=child.kill();break child.wait().map_err(|e|e.to_string())?}
        std::thread::sleep(Duration::from_millis(20));
    };
    let _=scope.terminate();
    let text=|bytes:Vec<u8>|String::from_utf8_lossy(&bytes).replace("\r\n","\n");
    let stdout=text(out.join().map_err(|_|"출력 수집 오류")?);let stderr=text(err.join().map_err(|_|"오류 수집 오류")?);
    let limited=overflow.load(std::sync::atomic::Ordering::Relaxed);
    Ok(Output{success:status.success()&&!timed_out&&!limited,timed_out,limited,stdout,stderr})
}

fn docker(cli:&Path,args:&[&str],seconds:u64)->Result<Output,String> {
    let mut command=Command::new(cli);prepare(&mut command,cli);command.args(args);
    execute(command,"",seconds)
}

fn first_line(text:&str)->&str {text.lines().find(|line|!line.trim().is_empty()).unwrap_or("").trim()}

/// The engine must already be running; the player never installs or starts Docker Desktop.
pub fn engine(cli:&Path)->Result<String,String> {
    let info=docker(cli,&["info","--format","{{.OSType}} {{.ServerVersion}}"],30)?;
    if !info.success {
        return Err(format!("Docker 엔진에 연결하지 못했어요. Docker Desktop을 설치하고 실행한 뒤 다시 실행하세요. 설치 안내: {INSTALL_GUIDE}\n{}",first_line(&info.stderr)))
    }
    let text=info.stdout.trim().to_owned();
    if !text.starts_with("linux ") {return Err("Docker가 Windows 컨테이너 모드예요. Docker Desktop에서 Linux 컨테이너로 바꾼 뒤 다시 실행하세요.".into())}
    let compose=docker(cli,&["compose","version","--short"],30)?;
    if !compose.success {return Err(format!("Docker Compose v2를 찾지 못했어요. Docker Desktop을 최신으로 설치하세요. 설치 안내: {INSTALL_GUIDE}"))}
    Ok(format!("Docker {} · Compose {}",text.trim_start_matches("linux "),compose.stdout.trim()))
}

/// The environment check: reports whether Docker lessons can run here. Never starts the engine.
pub async fn inspect()->Result<String,String> {
    tokio::task::spawn_blocking(||{
        let cli=cli().ok_or_else(||format!("Docker가 설치되지 않았어요. Docker·DB 실습을 하려면 Docker Desktop을 설치하고 실행하세요. 설치 안내: {INSTALL_GUIDE}"))?;
        engine(&cli)
    }).await.map_err(|e|e.to_string())?
}

static PULLING:std::sync::Mutex<()>=std::sync::Mutex::new(());
fn ensure_images(cli:&Path,images:&[String])->Result<(),String> {
    for image in images {
        let present=||docker(cli,&["image","inspect","--format","{{.Id}}",image],60).map(|o|o.success);
        if present()? {continue}
        let _pulling=PULLING.lock().unwrap_or_else(|poisoned|poisoned.into_inner());
        if present()? {continue}
        let pulled=docker(cli,&["pull","--quiet",image],PULL_SECONDS)?;
        if !pulled.success {
            return Err(format!("이미지 {image}를 받지 못했어요. 인터넷 연결과 Docker Desktop 상태를 확인하세요.\n{}",first_line(&pulled.stderr)))
        }
    }
    Ok(())
}

fn ids(cli:&Path,args:&[&str])->Vec<String> {
    docker(cli,args,60).ok().filter(|o|o.success).map(|o|o.stdout.lines().map(str::trim).filter(|l|!l.is_empty()).map(str::to_owned).collect::<BTreeSet<_>>().into_iter().collect()).unwrap_or_default()
}

/// Remove only what carries this project's label. Names are never used to select resources.
pub fn remove_project(cli:&Path,project:&str) {
    if !project.starts_with(PREFIX) {return}
    for label in [COMPOSE_LABEL,OWNER_LABEL] {
        let filter=format!("label={label}={project}");
        let containers=ids(cli,&["ps","-aq","--filter",&filter]);
        if !containers.is_empty(){let mut args=vec!["rm","-f","-v"];args.extend(containers.iter().map(String::as_str));let _=docker(cli,&args,120);}
    }
    for label in [COMPOSE_LABEL,OWNER_LABEL] {
        let filter=format!("label={label}={project}");
        let networks=ids(cli,&["network","ls","-q","--filter",&filter]);
        if !networks.is_empty(){let mut args=vec!["network","rm"];args.extend(networks.iter().map(String::as_str));let _=docker(cli,&args,60);}
        let volumes=ids(cli,&["volume","ls","-q","--filter",&filter]);
        if !volumes.is_empty(){let mut args=vec!["volume","rm","-f"];args.extend(volumes.iter().map(String::as_str));let _=docker(cli,&args,60);}
        let images=ids(cli,&["image","ls","-q","--no-trunc","--filter",&filter]);
        if !images.is_empty(){let mut args=vec!["image","rm","-f"];args.extend(images.iter().map(String::as_str));let _=docker(cli,&args,120);}
    }
}

/// Run locks live in the per-user temp folder, not the app data folder, so a pilot session with its
/// own data folder still sees the locks of the installed app's running labs (and vice versa).
fn locks()->Result<PathBuf,String> {
    let directory=std::env::temp_dir().join("mq3-docker-labs");
    std::fs::create_dir_all(&directory).map_err(|e|e.to_string())?;
    Ok(directory)
}

fn valid_project(name:&str)->bool {
    name.starts_with(PREFIX)&&name.len()<64&&name.bytes().all(|c|c.is_ascii_lowercase()||c.is_ascii_digit()||c==b'-')
}

/// Projects of earlier runs whose lock is no longer held (the app was closed or killed mid-run).
pub fn stale_projects(cli:&Path)->Vec<String> {
    let mut found=BTreeSet::new();
    for label in [COMPOSE_LABEL,OWNER_LABEL] {
        let format=format!("{{{{.Label \"{label}\"}}}}");
        for kind in [["ps","-a"],["volume","ls"],["network","ls"]] {
            let mut args=kind.to_vec();let filter=format!("label={label}");
            args.extend(["--filter",&filter,"--format",&format]);
            found.extend(ids(cli,&args));
        }
        let filter=format!("label={label}");
        let images=ids(cli,&["image","ls","-q","--no-trunc","--filter",&filter]);
        if !images.is_empty() {
            let format=format!("{{{{index .Config.Labels \"{label}\"}}}}");
            let mut args=vec!["image","inspect","--format",&format];args.extend(images.iter().map(String::as_str));
            found.extend(ids(cli,&args));
        }
    }
    let Ok(directory)=locks() else{return vec![]};
    found.into_iter().filter(|name|valid_project(name)).filter(|name|{
        let path=directory.join(format!("{name}.lock"));
        match std::fs::OpenOptions::new().read(true).write(true).open(&path) {
            Ok(file)=>match file.try_lock() {Ok(())=>{let _=file.unlock();true},Err(_)=>false},
            Err(_)=>true,
        }
    }).collect()
}

/// Best effort at startup: only acts when an engine already answers; never starts one.
pub fn sweep_stale()->usize {
    let Some(cli)=cli() else{return 0};
    if !docker(&cli,&["info","--format","{{.OSType}}"],15).is_ok_and(|o|o.success) {return 0}
    let stale=stale_projects(&cli);
    for project in &stale {remove_project(&cli,project);}
    if let Ok(directory)=locks() {
        for project in &stale {let _=std::fs::remove_file(directory.join(format!("{project}.lock")));}
    }
    stale.len()
}

struct Lab { cli:PathBuf, project:String, lock:Option<std::fs::File>, lock_path:PathBuf }
impl Lab {
    fn open(cli:&Path,task:&Task)->Result<Self,String> {
        use sha2::{Digest,Sha256};
        let step=format!("{:x}",Sha256::digest(task.id.as_bytes()));
        let run=crate::issue_progress::new_id().to_ascii_lowercase().chars().filter(char::is_ascii_alphanumeric).take(10).collect::<String>();
        let project=format!("{PREFIX}{}-{run}",&step[..8]);
        if !valid_project(&project) {return Err("실습 프로젝트 이름을 만들지 못했어요.".into())}
        let lock_path=locks()?.join(format!("{project}.lock"));
        let file=std::fs::OpenOptions::new().read(true).write(true).create(true).truncate(true).open(&lock_path).map_err(|e|e.to_string())?;
        file.lock().map_err(|e|format!("실습 잠금: {e}"))?;
        Ok(Self{cli:cli.to_path_buf(),project,lock:Some(file),lock_path})
    }
}
impl Drop for Lab {
    fn drop(&mut self) {
        remove_project(&self.cli,&self.project);
        drop(self.lock.take());
        let _=std::fs::remove_file(&self.lock_path);
    }
}

fn reject(message:String)->Execution {
    Execution{stdout:String::new(),stderr:message,success:false,state:"runtime_error".into(),artifacts:vec![]}
}

fn lower(path:&str)->String {
    let text=path.replace('\\',"/");
    let text=text.trim_end_matches('/');
    if cfg!(windows)||cfg!(target_os="macos"){text.to_lowercase()}else{text.to_owned()}
}
fn inside(root:&str,path:&str)->bool {
    let (root,path)=(lower(root),lower(path));
    path==root||path.starts_with(&format!("{root}/"))
}

/// Problems in the learner's compose file that would reach outside this run. `None` means it may run.
fn compose_problem(cli:&Path,dir:&Path,project:&str,task:&Task)->Result<Option<String>,String> {
    if !dir.join("compose.yaml").is_file() {return Ok(None)}
    let mut command=Command::new(cli);prepare(&mut command,cli);
    command.current_dir(dir).env("COMPOSE_PROJECT_NAME",project).args(["compose","-f","compose.yaml","config","--format","json"]);
    let output=execute(command,"",60)?;
    if !output.success {return Ok(Some(format!("compose.yaml을 읽지 못했어요.\n{}",output.stderr.trim())))}
    let config:serde_json::Value=serde_json::from_str(&output.stdout).map_err(|e|e.to_string())?;
    let root=dunce::simplified(&dir.canonicalize().map_err(|e|e.to_string())?).to_string_lossy().into_owned();
    let empty=serde_json::Map::new();
    for (name,service) in config["services"].as_object().unwrap_or(&empty) {
        for key in ["container_name","network_mode","pid","ipc","userns_mode","cgroup_parent","devices","cap_add","security_opt","sysctls"] {
            if !service[key].is_null() {
                return Ok(Some(format!("서비스 {name}: 이 실습에서는 {key}를 쓰지 않아요. 앱이 실행마다 이름과 네트워크를 따로 만들어요.")))
            }
        }
        if service["privileged"].as_bool()==Some(true) {return Ok(Some(format!("서비스 {name}: privileged 권한은 쓰지 않아요.")))}
        for port in service["ports"].as_array().unwrap_or(&vec![]) {
            let published=port["published"].as_str().unwrap_or("");
            if port["host_ip"].as_str()!=Some("127.0.0.1")||!(published.is_empty()||published=="0") {
                return Ok(Some(format!("서비스 {name}: 포트는 \"127.0.0.1::{}\"처럼 써요. 이 컴퓨터 안(127.0.0.1)에서만, Docker가 고른 빈 포트로 열어야 다른 프로그램의 포트와 부딪히지 않아요.",port["target"])))
            }
        }
        for volume in service["volumes"].as_array().unwrap_or(&vec![]) {
            let kind=volume["type"].as_str().unwrap_or("");
            let source=volume["source"].as_str().unwrap_or("");
            if kind=="bind"&&!inside(&root,source) || !matches!(kind,"bind"|"volume"|"tmpfs") {
                return Ok(Some(format!("서비스 {name}: 실습 폴더 밖의 경로는 연결하지 않아요: {source}")))
            }
        }
        let image=service["image"].as_str();
        if service["build"].is_object() {
            if image.is_some() {return Ok(Some(format!("서비스 {name}: build를 쓰는 서비스에는 image 이름을 붙이지 않아요. Compose가 실행마다 이름을 붙여요.")))}
            let context=service["build"]["context"].as_str().unwrap_or("");
            if !inside(&root,context) {return Ok(Some(format!("서비스 {name}: 빌드 폴더는 실습 폴더 안이어야 해요.")))}
        } else if !image.is_some_and(|image|task.docker_images.iter().any(|allowed|allowed==image)) {
            return Ok(Some(format!("서비스 {name}: 준비된 이미지만 써요. image 줄은 바꾸지 마세요.")))
        }
    }
    for section in ["volumes","networks"] {
        for (name,item) in config[section].as_object().unwrap_or(&empty) {
            if item["external"].as_bool()==Some(true)||!item["driver_opts"].is_null()||!item["name"].as_str().is_none_or(|n|n.starts_with(project)) {
                return Ok(Some(format!("{name}: 이 실습 밖의 볼륨·네트워크는 쓰지 않아요.")))
            }
        }
    }
    Ok(None)
}

/// Every FROM must be one of the task's pinned images (or an earlier build stage).
fn dockerfile_problem(dir:&Path,task:&Task)->Option<String> {
    let entries=std::fs::read_dir(dir).ok()?;
    for entry in entries.flatten() {
        let name=entry.file_name().to_string_lossy().into_owned();
        if name!="Dockerfile"&&!name.ends_with(".Dockerfile") {continue}
        let text=std::fs::read_to_string(entry.path()).unwrap_or_default();
        let mut stages=BTreeSet::new();
        for line in text.lines() {
            let words:Vec<&str>=line.split_whitespace().collect();
            if words.first().is_none_or(|w|!w.eq_ignore_ascii_case("FROM")) {continue}
            let rest:Vec<&str>=words[1..].iter().copied().filter(|w|!w.starts_with("--")).collect();
            let Some(base)=rest.first() else{return Some(format!("{name}: FROM 줄을 확인하세요."))};
            if !task.docker_images.iter().any(|image|image==base)&&!stages.contains(&base.to_ascii_lowercase())&&*base!="scratch" {
                return Some(format!("{name}: FROM은 준비된 이미지만 써요. FROM 줄의 이미지 이름은 바꾸지 마세요."))
            }
            if rest.len()>=3&&rest[1].eq_ignore_ascii_case("AS") {stages.insert(rest[2].to_ascii_lowercase());}
        }
    }
    None
}

fn bash()->Result<PathBuf,String> {
    #[cfg(windows)] {crate::setup_terminal::git_bash_executable()}
    #[cfg(not(windows))] {Ok(PathBuf::from("/bin/bash"))}
}

struct Prepared { java:Option<String>, classpath:String }

fn run_blocking(task:&Task,source:&str,input:&str,prepared:Prepared)->Result<Execution,String> {
    let cli=cli().ok_or_else(||format!("Docker를 찾지 못했어요. Docker Desktop을 설치하고 실행한 뒤 다시 실행하세요. 설치 안내: {INSTALL_GUIDE}"))?;
    engine(&cli)?;
    for project in stale_projects(&cli) {remove_project(&cli,&project);if let Ok(d)=locks(){let _=std::fs::remove_file(d.join(format!("{project}.lock")));}}
    ensure_images(&cli,&task.docker_images)?;
    let directory=tempfile::Builder::new().prefix("mq3-docker-lab-").tempdir().map_err(|e|e.to_string())?;
    for (name,content) in &task.files {write(directory.path(),name,content)?;}
    write(directory.path(),&task.entry_file,source)?;
    let lab=Lab::open(&cli,task)?;
    if let Some(problem)=compose_problem(&cli,directory.path(),&lab.project,task)? {return Ok(reject(problem))}
    if let Some(problem)=dockerfile_problem(directory.path(),task) {return Ok(reject(problem))}
    let mut command=Command::new(bash()?);prepare(&mut command,&cli);
    command.current_dir(directory.path()).arg("lab.sh")
        .env("COMPOSE_PROJECT_NAME",&lab.project).env("MQ3_PROJECT",&lab.project)
        .env("MQ3_OWNER_LABEL",format!("{OWNER_LABEL}={}",lab.project)).env("MQ3_ENTRY",&task.entry_file)
        .env("MQ3_OS",if cfg!(windows){"windows"}else if cfg!(target_os="macos"){"macos"}else{"linux"})
        .env("LC_ALL","C.UTF-8").env("PGCLIENTENCODING","UTF8");
    if let Some(java)=&prepared.java {command.env("MQ3_JAVA",java).env("MQ3_CLASSPATH",&prepared.classpath);}
    let output=execute(command,input,LAB_SECONDS)?;
    drop(lab);
    let state=if output.timed_out{"timeout"}else if output.limited{"output_limit"}else if output.success{"finished"}else{"runtime_error"};
    let mut stderr=output.stderr;
    if output.timed_out {stderr.push_str(&format!("\n실행 시간 제한 {LAB_SECONDS}초를 넘었어요. 실습 컨테이너는 정리했어요."));}
    if output.limited {stderr.push_str("\n출력 제한 64KB를 넘었어요.");}
    Ok(Execution{stdout:output.stdout,stderr,success:output.success,state:state.into(),artifacts:vec![]})
}

fn write(root:&Path,name:&str,content:&str)->Result<(),String> {
    if !crate::repository_course::safe_file(name) {return Err("실습 파일 경로를 확인하세요.".into())}
    let path=root.join(name);
    std::fs::create_dir_all(path.parent().ok_or("파일 경로 오류")?).map_err(|e|e.to_string())?;
    // Shell scripts and compose files keep LF line endings on every platform.
    std::fs::write(path,content.replace("\r\n","\n")).map_err(|e|e.to_string())
}

pub async fn run(task:&Task,source:&str,input:&str)->Result<Execution,String> {
    if source.len()>65536||input.len()>65536 {return Err("작성 코드와 입력은 각각 64KB 이하여야 해요.".into())}
    let prepared=if task.libraries.is_empty(){Prepared{java:None,classpath:String::new()}}else{
        crate::java::version().await?;
        let classpath=crate::library_sets::classpath(&task.libraries).await?;
        Prepared{java:Some(crate::java::executable().replace('\\',"/")),classpath:crate::library_sets::joined(&classpath)}
    };
    let (task,source,input)=(task.clone(),source.to_owned(),input.to_owned());
    tokio::task::spawn_blocking(move||run_blocking(&task,&source,&input,prepared)).await.map_err(|e|e.to_string())?
}

#[cfg(test)]
mod tests {
    use super::*;
    fn task(compose:&str)->Task {
        serde_json::from_value(serde_json::json!({"id":"stp_docker_probe","title":"Docker","goal":"x","language":"docker",
            "starter_code":compose,"solution":compose,"entry_file":"compose.yaml",
            "files":{"lab.sh":"set -e\ndocker compose run --rm --no-deps box\n"},
            "docker_images":["busybox:1.36@sha256:73aaf090f3d85aa34ee199857f03fa3a95c8ede2ffd4cc2cdb5b94e566b11662"],
            "tests":[{"input":"","expected":"hello"}]})).unwrap()
    }
    #[test]
    fn only_digest_pinned_official_images() {
        assert!(valid_image("busybox:1.36@sha256:73aaf090f3d85aa34ee199857f03fa3a95c8ede2ffd4cc2cdb5b94e566b11662"));
        assert!(!valid_image("busybox:1.36"));
        assert!(!valid_image("evil/busybox:1.36@sha256:73aaf090f3d85aa34ee199857f03fa3a95c8ede2ffd4cc2cdb5b94e566b11662"));
        assert!(!valid_image("busybox:1.36@sha256:73AAF090F3D85AA34EE199857F03FA3A95C8EDE2FFD4CC2CDB5B94E566B11662"));
        assert!(validate_task(&task("services: {}\n")).is_ok());
        let mut t=task("x");t.files.remove("lab.sh");assert!(validate_task(&t).is_err());
    }
    #[test]
    fn bind_mounts_must_stay_in_the_run_folder() {
        assert!(inside("C:/Temp/run","C:\\Temp\\run\\data"));
        assert!(inside("C:/Temp/run","c:/temp/run"));
        assert!(!inside("C:/Temp/run","C:/Temp/run2"));
        assert!(!inside("C:/Temp/run","C:/Users"));
    }
    #[test]
    fn dockerfile_from_lines_use_pinned_images() {
        let dir=tempfile::tempdir().unwrap();let t=task("x");
        std::fs::write(dir.path().join("Dockerfile"),format!("FROM {} AS base\nFROM base\nRUN echo hi\n",t.docker_images[0])).unwrap();
        assert_eq!(dockerfile_problem(dir.path(),&t),None);
        std::fs::write(dir.path().join("Dockerfile"),"FROM ubuntu:latest\n").unwrap();
        assert!(dockerfile_problem(dir.path(),&t).is_some());
    }
    /// Real engine checks. Run with `cargo test --lib docker_lab -- --ignored --test-threads=1`.
    #[tokio::test]
    #[ignore="Needs a running Docker engine"]
    async fn a_run_owns_its_project_rejects_fixed_ports_and_leaves_nothing() {
        let compose="services:\n  box:\n    image: busybox:1.36@sha256:73aaf090f3d85aa34ee199857f03fa3a95c8ede2ffd4cc2cdb5b94e566b11662\n    command: [\"echo\", \"hello\"]\n";
        let t=task(compose);
        let result=run(&t,compose,"").await.unwrap();
        assert!(result.success,"{}",result.stderr);
        assert_eq!(result.stdout.trim(),"hello");
        assert!(crate::lesson_runner::check(&t,compose).await.unwrap().passed);
        let fixed=format!("{compose}    ports:\n      - \"8080:80\"\n");
        let rejected=run(&t,&fixed,"").await.unwrap();
        assert!(!rejected.success&&rejected.stderr.contains("127.0.0.1::"),"{}",rejected.stderr);
        let open=format!("{compose}    ports:\n      - \"80\"\n");
        assert!(!run(&t,&open,"").await.unwrap().success);
        let named=compose.replace("    command:","    container_name: web\n    command:");
        assert!(run(&t,&named,"").await.unwrap().stderr.contains("container_name"));
        let cli=cli().unwrap();
        let left=ids(&cli,&["ps","-aq","--filter","label=com.docker.compose.project"]).into_iter()
            .filter(|id|ids(&cli,&["inspect","--format","{{index .Config.Labels \"com.docker.compose.project\"}}",id]).iter().any(|p|p.starts_with(PREFIX))).count();
        assert_eq!(left,0,"lab containers remain");
    }
    #[tokio::test]
    #[ignore="Needs a running Docker engine"]
    async fn a_killed_run_is_swept_by_its_labels_only() {
        let cli=cli().unwrap();
        let project=format!("{PREFIX}sweeptest-{}",crate::issue_progress::new_id().to_ascii_lowercase().chars().filter(char::is_ascii_alphanumeric).take(8).collect::<String>());
        let label=format!("{OWNER_LABEL}={project}");
        let image="busybox:1.36@sha256:73aaf090f3d85aa34ee199857f03fa3a95c8ede2ffd4cc2cdb5b94e566b11662";
        ensure_images(&cli,&[image.to_owned()]).unwrap();
        assert!(docker(&cli,&["volume","create","--label",&label],30).unwrap().success);
        assert!(docker(&cli,&["run","-d","--label",&label,image,"sleep","60"],60).unwrap().success);
        assert!(stale_projects(&cli).contains(&project));
        remove_project(&cli,&project);
        assert!(ids(&cli,&["ps","-aq","--filter",&format!("label={label}")]).is_empty());
        assert!(ids(&cli,&["volume","ls","-q","--filter",&format!("label={label}")]).is_empty());
    }
}
