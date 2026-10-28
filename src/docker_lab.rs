//! Real Docker labs for lessons. Directory isolation is not an OS sandbox.
//!
//! A lesson session owns reusable Compose projects named `mq3lab-…`. The authored script (`lab.sh`)
//! runs in Bash with that project name. Before the script starts, the learner's compose file is
//! checked: published ports must stay on 127.0.0.1 with an engine-chosen host port, and nothing may
//! use a fixed container name, host networking, privileges or a bind mount outside the run folder.
//! Interactive runs retain their resources until the lesson closes. Standalone validation runs
//! remain isolated and short-lived. On lesson exit only its labelled containers, networks,
//! volumes and built images are removed. A project left behind by a
//! killed desktop app is cleaned by a detached lock watcher; startup also sweeps the same labels
//! after a machine/engine interruption, unless a live run still holds its lock. Dropping an async
//! caller does not abort an already running blocking lab; it stays bounded by LAB_SECONDS.
//! Declared official images are digest-pinned and stay cached like any `docker pull`.
//! CLI lessons run in the learner's real terminal (terminal.rs): the real `docker ps` table shows
//! other containers too; destructive operations and cleanup are limited to the lesson's ownership labels.
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
static WATCH_EXECUTABLE:std::sync::OnceLock<PathBuf>=std::sync::OnceLock::new();

/// The desktop binary handles the private watchdog CLI before opening its UI.
/// Examples and test runners do not opt in: they are not desktop helper binaries.
pub fn enable_watchdog(executable:PathBuf) {let _=WATCH_EXECUTABLE.set(executable);}

pub fn watchdog_cli(args:&[String])->Option<Result<(),String>> {
    if args.get(1).map(String::as_str)!=Some("--mq3-docker-watch"){return None}
    Some(match args.get(2) {
        Some(project) if args.len()==3&&valid_project(project)=>watch_project(project),
        _=>Err("Invalid Docker lab watchdog project".into()),
    })
}

fn watch_project(project:&str)->Result<(),String> {
    if !owns_project(project){return Err("Unregistered Docker lab watchdog project".into())}
    let path=locks()?.join(format!("{project}.lock"));
    loop {
        // A normal run removes this file after cleanup. An abruptly terminated
        // owner leaves the file but the OS releases its exclusive lock.
        let file=match std::fs::OpenOptions::new().read(true).write(true).open(&path) {
            Ok(file)=>file,
            Err(e) if e.kind()==std::io::ErrorKind::NotFound=>return Ok(()),
            Err(e)=>return Err(e.to_string()),
        };
        if file.try_lock().is_ok() {
            if let Some(cli)=cli(){remove_project(&cli,project);}
            drop(file);
            let _=std::fs::remove_file(&path);
            return Ok(())
        }
        drop(file);
        std::thread::sleep(Duration::from_millis(500));
    }
}

fn spawn_watchdog(project:&str)->Result<(),String> {
    let Some(executable)=WATCH_EXECUTABLE.get() else{return Ok(())};
    let mut command=Command::new(executable);
    command.args(["--mq3-docker-watch",project]).stdin(Stdio::null()).stdout(Stdio::null()).stderr(Stdio::null());
    #[cfg(windows)] {
        use std::os::windows::process::CommandExt;
        command.creation_flags(0x08000000|0x00000008); // hidden, detached from the owner's console
    }
    #[cfg(unix)] {use std::os::unix::process::CommandExt;command.process_group(0);}
    command.spawn().map(|_|()).map_err(|e|format!("실습 정리 감시자를 시작하지 못했어요: {e}"))
}

/// Official images pinned by a multi-platform index digest, e.g. `busybox:1.36@sha256:…`.
pub fn valid_image(reference:&str)->bool {
    let Some((name,digest))=reference.split_once("@sha256:") else{return false};
    let Some((repo,tag))=name.split_once(':') else{return false};
    matches!(repo,"busybox"|"postgres"|"mysql"|"nginx")&&!tag.is_empty()&&tag.len()<64
        &&tag.bytes().all(|c|c.is_ascii_alphanumeric()||b"._-".contains(&c))
        &&digest.len()==64&&digest.bytes().all(|c|c.is_ascii_digit()||(b'a'..=b'f').contains(&c))
}

pub fn validate_task(task:&Task)->Result<(),String> {
    if let Some(exercise)=&task.git_terminal {
        // A Docker CLI step: the learner types commands in a real terminal; no lab script runs.
        let Some(docker)=&exercise.docker else{return Err("Docker 실습 터미널의 구성을 확인하세요.".into())};
        if task.interaction.is_some()||task.checker.is_some()||!task.mutations.is_empty()||!task.files.is_empty()||!task.tests.is_empty()||!task.variations.is_empty()||!task.libraries.is_empty()
            ||task.docker_images!=docker.compose.as_ref().map(|c|c.images.clone()).unwrap_or_else(||vec![docker.image.clone()]) {
            return Err("Docker 터미널 실습은 실제 명령과 엔진 상태로만 판정해요.".into())
        }
        return Ok(())
    }
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
    #[cfg(windows)] if let Ok(shell) = crate::setup_terminal::git_bash_executable() {
        // Desktop launches need not inherit Git's POSIX tools. Bash itself can
        // start without them, but lab scripts and the Docker plugin launcher
        // also need sh, sed, cat and the rest of Git for Windows' tools.
        if let Some(bin) = shell.parent() {
            paths.push(bin.to_path_buf());
            if let Some(root) = bin.parent() {
                paths.push(root.join("usr/bin"));
                paths.push(root.join("mingw64/bin"));
            }
        }
    }
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
fn execute(command:Command,input:&str,seconds:u64)->Result<Output,String> {
    execute_cancellable(command,input,seconds,None)
}

fn execute_cancellable(mut command:Command,input:&str,seconds:u64,cancel:Option<&std::sync::atomic::AtomicBool>)->Result<Output,String> {
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
        if cancel.is_some_and(|flag|flag.load(std::sync::atomic::Ordering::Acquire))||started.elapsed()>Duration::from_secs(seconds){timed_out=true;let _=scope.terminate();let _=child.kill();break child.wait().map_err(|e|e.to_string())?}
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

fn start_when_needed<T>(mut probe:impl FnMut()->Result<T,String>,start:impl FnOnce()->Result<(),String>,mut pause:impl FnMut(),timeout:Duration)->Result<T,String> {
    if let Ok(ready)=probe(){return Ok(ready)}
    start()?;
    let deadline=Instant::now()+timeout;
    while Instant::now()<deadline {
        pause();
        if let Ok(ready)=probe(){return Ok(ready)}
    }
    Err("Docker Desktop을 실행했지만 엔진 준비가 끝나지 않았어요. Docker 창에 초기 설정이나 권한 확인이 뜨면 완료한 뒤 다시 실행하세요.".into())
}

fn local_desktop_endpoint(endpoint:&str)->bool {
    let endpoint=endpoint.trim().to_ascii_lowercase();
    (endpoint.starts_with("unix://")&&(endpoint.contains("/.docker/")||endpoint=="unix:///var/run/docker.sock"))
        ||(endpoint.starts_with("npipe://")&&(endpoint.contains("/docker_engine")||endpoint.contains("/dockerdesktoplinuxengine")))
}

/// This short-lived launcher deliberately has no CommandScope: the desktop app
/// must survive the CLI that launched it and the lesson that requested it.
fn launch_desktop_command(mut command:Command)->Result<(),String> {
    command.stdin(Stdio::null()).stdout(Stdio::null()).stderr(Stdio::null());
    #[cfg(windows)] {use std::os::windows::process::CommandExt;command.creation_flags(0x08000000);}
    let mut child=command.spawn().map_err(|e|e.to_string())?;
    let deadline=Instant::now()+Duration::from_secs(15);
    loop {
        match child.try_wait().map_err(|e|e.to_string())? {
            Some(status) if status.success()=>return Ok(()),
            Some(_)=>return Err("Docker Desktop 실행 요청을 완료하지 못했어요.".into()),
            None if Instant::now()>=deadline=>{let _=child.kill();let _=child.wait();return Err("Docker Desktop 실행 요청이 지연되고 있어요.".into())},
            None=>std::thread::sleep(Duration::from_millis(100)),
        }
    }
}

fn start_desktop(cli:&Path)->Result<(),String> {
    let context=std::env::var("DOCKER_CONTEXT").ok().filter(|v|!v.is_empty());
    let endpoint=if context.is_none() {
        std::env::var("DOCKER_HOST").ok().filter(|v|!v.is_empty())
    }else{None};
    let endpoint=match endpoint {
        Some(value)=>value,
        None=>{
            let mut args=vec!["context","inspect","--format","{{.Endpoints.docker.Host}}"];
            if let Some(name)=context.as_deref(){args.push(name);}
            let output=docker(cli,&args,10)?;
            if !output.success{return Err("Docker 연결 대상을 확인하지 못했어요. 환경 진단에서 현재 연결 설정을 확인하세요.".into())}
            output.stdout
        },
    };
    if !local_desktop_endpoint(&endpoint) {
        return Err("현재 Docker 연결 대상에 접속하지 못했어요. 해당 엔진을 실행한 뒤 다시 시도하세요. 선택한 연결 대상은 그대로 유지해요.".into())
    }
    let mut command=Command::new(cli);prepare(&mut command,cli);
    command.args(["desktop","start","--detach"]);
    if launch_desktop_command(command).is_ok(){return Ok(())}
    // Older Desktop versions may not include the desktop CLI plugin.
    #[cfg(target_os="macos")] {
        let mut command=Command::new("/usr/bin/open");command.args(["-g","-a","Docker"]);
        if launch_desktop_command(command).is_ok(){return Ok(())}
    }
    #[cfg(windows)] {
        let mut candidates=vec![];
        if let Some(root)=cli.parent().and_then(Path::parent).and_then(Path::parent){candidates.push(root.join("Docker Desktop.exe"));}
        for key in ["ProgramFiles","ProgramW6432"] {
            if let Some(root)=std::env::var_os(key){candidates.push(PathBuf::from(root).join("Docker/Docker/Docker Desktop.exe"));}
        }
        if let Some(executable)=candidates.into_iter().find(|p|p.is_file()) {
            use std::os::windows::process::CommandExt;
            Command::new(executable).stdin(Stdio::null()).stdout(Stdio::null()).stderr(Stdio::null())
                .creation_flags(0x08000000).spawn().map_err(|e|e.to_string())?;
            return Ok(())
        }
    }
    Err(format!("Docker Desktop을 자동으로 실행하지 못했어요. 설치되어 있으면 직접 실행하세요. 설치하지 않았다면 먼저 설치하세요. 설치 안내: {INSTALL_GUIDE}"))
}

#[cfg(test)]
mod startup_tests {
    use super::*;
    use std::cell::Cell;

    #[test]
    fn stopped_engine_starts_once_and_waits_until_ready() {
        let probes=Cell::new(0);let launches=Cell::new(0);let waits=Cell::new(0);
        let result=start_when_needed(||{probes.set(probes.get()+1);if probes.get()<3{Err("socket missing".into())}else{Ok("linux ready")}},
            ||{launches.set(launches.get()+1);Ok(())},||waits.set(waits.get()+1),Duration::from_secs(1));
        assert_eq!(result.unwrap(),"linux ready");assert_eq!(launches.get(),1);assert_eq!(waits.get(),2);
    }

    #[test]
    fn already_running_engine_is_not_started_again() {
        assert_eq!(start_when_needed(||Ok("ready"),||panic!("must not launch"),||panic!("must not wait"),Duration::ZERO).unwrap(),"ready");
    }

    #[test]
    fn launch_failure_does_not_claim_docker_is_ready() {
        let result=start_when_needed::<()>(||Err("socket missing".into()),||Err("launch failed".into()),||panic!("must not wait"),Duration::from_secs(1));
        assert_eq!(result.unwrap_err(),"launch failed");
    }

    #[test]
    fn startup_wait_has_a_deadline() {
        let launched=Cell::new(false);
        assert!(start_when_needed::<()>(||Err("not ready".into()),||{launched.set(true);Ok(())},||{},Duration::ZERO).is_err());
        assert!(launched.get());
    }

    #[test]
    fn only_local_desktop_connections_are_started() {
        for endpoint in ["unix:///Users/test/.docker/run/docker.sock","unix:///var/run/docker.sock","npipe:////./pipe/dockerDesktopLinuxEngine","npipe:////./pipe/docker_engine"] {
            assert!(local_desktop_endpoint(endpoint),"{endpoint}");
        }
        for endpoint in ["ssh://server","tcp://127.0.0.1:2376","tcp://remote:2376","unix:///Users/test/.colima/default/docker.sock",""] {
            assert!(!local_desktop_endpoint(endpoint),"{endpoint}");
        }
    }
}

fn engine_info(cli:&Path,seconds:u64)->Result<Output,String> {
    let info=docker(cli,&["info","--format","{{.OSType}} {{.ServerVersion}}"],seconds)?;
    if !info.success {
        return Err(format!("Docker 엔진에 연결하지 못했어요. Docker Desktop이 꺼져 있으면 실행하세요.\n{}",first_line(&info.stderr)))
    }
    Ok(info)
}

fn engine_details(cli:&Path,info:Output)->Result<String,String> {
    let text=info.stdout.trim().to_owned();
    if !text.starts_with("linux ") {return Err("Docker가 Windows 컨테이너 모드예요. Docker Desktop에서 Linux 컨테이너로 바꾼 뒤 다시 실행하세요.".into())}
    let compose=docker(cli,&["compose","version","--short"],30)?;
    if !compose.success {return Err(format!("Docker Compose v2를 찾지 못했어요. Docker Desktop을 최신으로 설치하세요. 설치 안내: {INSTALL_GUIDE}"))}
    Ok(format!("Docker {} · Compose {}",text.trim_start_matches("linux "),compose.stdout.trim()))
}

/// Read-only diagnostics do not launch an app.
pub fn engine(cli:&Path)->Result<String,String> {engine_details(cli,engine_info(cli,30)?)}

/// A requested lesson starts installed Docker Desktop once and waits for its
/// engine, then continues the same run without changing the learner's code.
fn ensure_engine(cli:&Path)->Result<String,String> {
    static STARTING:std::sync::Mutex<()>=std::sync::Mutex::new(());
    if let Ok(info)=engine_info(cli,5){return engine_details(cli,info)}
    let _starting=STARTING.lock().unwrap_or_else(|p|p.into_inner());
    let info=start_when_needed(||engine_info(cli,5),||start_desktop(cli),
        ||std::thread::sleep(Duration::from_secs(2)),Duration::from_secs(120))?;
    engine_details(cli,info)
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

/// The owned project whose Compose build produced this image repository. Compose names a built service image
/// `<project>-<service>` (`compose_problem` forbids `image:` on build services). Compose's bake builder (the
/// default of Compose v2.38 on Linux) does not add the project label to that image, so the label alone misses it.
/// Only a project with this app's ownership receipt counts, and the longest owned name wins, so a nested name
/// never reaches another project's image.
fn built_image_owner(repository:&str)->Option<String> {
    let repository=repository.split(':').next().unwrap_or(repository);
    repository.match_indices('-').map(|(at,_)|&repository[..at]).filter(|name|owns_project(name)).last().map(str::to_owned)
}

/// Tags of images Compose built for this owned project. Removed by tag, so a tag someone else added stays.
fn built_images(cli:&Path,project:&str)->Vec<String> {
    ids(cli,&["image","ls","--filter",&format!("reference={project}-*"),"--format","{{.Repository}}:{{.Tag}}"]).into_iter()
        .filter(|reference|built_image_owner(reference).as_deref()==Some(project)).collect()
}

/// Remove only what carries this project's label, plus the images Compose built under this owned project's name.
pub fn remove_project(cli:&Path,project:&str) {
    if !owns_project(project) {return}
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
    // After the containers that used them are gone.
    let built=built_images(cli,project);
    if !built.is_empty(){let mut args=vec!["image","rm"];args.extend(built.iter().map(String::as_str));let _=docker(cli,&args,120);}
}

/// Run locks live in the per-user temp folder, not the app data folder, so a pilot session with its
/// own data folder still sees the locks of the installed app's running labs (and vice versa).
fn locks()->Result<PathBuf,String> {
    let directory=std::env::temp_dir().join("mq3-docker-labs");
    std::fs::create_dir_all(&directory).map_err(|e|e.to_string())?;
    Ok(directory)
}

/// A Compose label or an app-looking name alone is never ownership evidence.
/// Retain this tiny local receipt for crash/engine recovery even after a run
/// releases its lock; an unrelated user project can have the same prefix.
fn register_owner(project:&str)->Result<(),String> {
    if !valid_project(project){return Err("Invalid owned Docker project".into())}
    use std::io::Write;
    let mut file=std::fs::OpenOptions::new().write(true).create_new(true)
        .open(locks()?.join(format!("{project}.owned"))).map_err(|e|e.to_string())?;
    file.write_all(format!("MQ3 owned Docker project v1\n{project}\n").as_bytes()).map_err(|e|e.to_string())
}

fn owns_project(project:&str)->bool {
    if !valid_project(project){return false}
    let Ok(directory)=locks() else{return false};
    std::fs::read_to_string(directory.join(format!("{project}.owned"))).is_ok_and(|text|
        text==format!("MQ3 owned Docker project v1\n{project}\n"))
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
    let built=ids(cli,&["image","ls","--filter",&format!("reference={PREFIX}*"),"--format","{{.Repository}}"]);
    found.extend(built.iter().filter_map(|repository|built_image_owner(repository)));
    let Ok(directory)=locks() else{return vec![]};
    found.into_iter().filter(|name|owns_project(name)).filter(|name|{
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
    fn open(cli:&Path,task:&Task)->Result<Self,String> {Self::open_for(cli,&task.id)}
    fn open_for(cli:&Path,seed:&str)->Result<Self,String> {
        use sha2::{Digest,Sha256};
        let step=format!("{:x}",Sha256::digest(seed.as_bytes()));
        let run=crate::issue_progress::new_id().to_ascii_lowercase().chars().filter(char::is_ascii_alphanumeric).take(10).collect::<String>();
        let project=format!("{PREFIX}{}-{run}",&step[..8]);
        if !valid_project(&project) {return Err("실습 프로젝트 이름을 만들지 못했어요.".into())}
        let lock_path=locks()?.join(format!("{project}.lock"));
        let file=std::fs::OpenOptions::new().read(true).write(true).create(true).truncate(true).open(&lock_path).map_err(|e|e.to_string())?;
        file.lock().map_err(|e|format!("실습 잠금: {e}"))?;
        register_owner(&project)?;
        let lab=Self{cli:cli.to_path_buf(),project,lock:Some(file),lock_path};
        spawn_watchdog(&lab.project)?;
        Ok(lab)
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
fn compose_problem(cli:&Path,dir:&Path,project:&str,images:&[String])->Result<Option<String>,String> {
    if !dir.join("compose.yaml").is_file() {return Ok(None)}
    let mut command=Command::new(cli);prepare(&mut command,cli);
    command.current_dir(dir).env("COMPOSE_PROJECT_NAME",project).env("MQ3_PROJECT",project).args(["compose","-f","compose.yaml","config","--format","json"]);
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
        } else if !image.is_some_and(|image|images.iter().any(|allowed|allowed==image)) {
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
fn dockerfile_problem(dir:&Path,images:&[String])->Option<String> {
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
            if !images.iter().any(|image|image==base)&&!stages.contains(&base.to_ascii_lowercase())&&*base!="scratch" {
                return Some(format!("{name}: FROM은 준비된 이미지만 써요. FROM 줄의 이미지 이름은 바꾸지 마세요."))
            }
            if rest.len()>=3&&rest[1].eq_ignore_ascii_case("AS") {stages.insert(rest[2].to_ascii_lowercase());}
        }
    }
    None
}

/// Files whose content decides what `docker compose` may run in a Compose terminal step, in the
/// order the terminal guard (TERMINAL_GUARD) concatenates them for its hash.
pub const COMPOSE_FILES:[&str;3]=["compose.yaml","Dockerfile",".env"];

/// SHA-256 (hex) of the concatenated bytes of these files in `dir`; a missing file adds nothing.
/// The terminal guard computes the same value with sha256sum or `shasum -a 256`.
pub fn files_hash(dir:&Path,names:&[&str])->String {
    use sha2::{Digest,Sha256};
    let mut hash=Sha256::new();
    for name in names {if let Ok(bytes)=std::fs::read(dir.join(name)){hash.update(&bytes);}}
    format!("{:x}",hash.finalize())
}

/// Whether `docker compose` may run this folder's files as `project`: the same checks the lab
/// scripts had (127.0.0.1 engine-chosen host ports, no bind mount outside the folder, no fixed
/// names, host networking or privileges, only the step's pinned images, Dockerfile FROM lines),
/// and, because the learner's shell environment differs from the app's: no .env file and no `$`
/// interpolation other than the provided `${MQ3_PROJECT}`. `None` means it may run.
pub fn compose_folder_problem(dir:&Path,project:&str,images:&[String])->Result<Option<String>,String> {
    if dir.join(".env").exists() {return Ok(Some(".env 파일은 이 실습에서 쓰지 않아요. 터미널 환경에 따라 설정이 바뀌지 않게 막았어요. .env를 지운 뒤 다시 실행하세요.".into()))}
    let Ok(text)=std::fs::read_to_string(dir.join("compose.yaml")) else{return Ok(Some("이 폴더에 compose.yaml이 없어요. 편집기의 compose.yaml을 확인하세요.".into()))};
    if text.replace("${MQ3_PROJECT}","").contains('$') {return Ok(Some("compose.yaml에는 $ 변수를 쓰지 않아요. 터미널 환경에 따라 설정이 바뀌지 않게 막았어요.".into()))}
    let cli=cli().ok_or_else(||format!("Docker를 찾지 못했어요. Docker Desktop을 설치하고 실행하세요. 설치 안내: {INSTALL_GUIDE}"))?;
    if let Some(problem)=compose_problem(&cli,dir,project,images)? {return Ok(Some(problem))}
    Ok(dockerfile_problem(dir,images))
}

/// One read-only `docker compose` query on this folder as `project` (config, ps, images…).
/// Grading uses it to read state; it never starts, builds or changes services.
pub fn compose_query(dir:&Path,project:&str,args:&[&str])->Result<(bool,String,String),String> {
    let cli=cli().ok_or_else(||format!("Docker를 찾지 못했어요. Docker Desktop을 설치하고 실행하세요. 설치 안내: {INSTALL_GUIDE}"))?;
    let mut command=Command::new(&cli);prepare(&mut command,&cli);
    command.current_dir(dir).env("MQ3_PROJECT",project).args(["compose","-p",project,"-f","compose.yaml"]).args(args);
    let output=execute(command,"",60)?;
    Ok((output.success,output.stdout,output.stderr))
}

fn bash()->Result<PathBuf,String> {
    #[cfg(windows)] {crate::setup_terminal::git_bash_executable()}
    #[cfg(not(windows))] {Ok(PathBuf::from("/bin/bash"))}
}

struct Prepared { java:Option<String>, classpath:String }

/// Owned by the lesson screen, not by an individual step or execution future.
#[derive(Clone)]
pub struct LessonSession(std::sync::Arc<LessonState>);
mod sql_browser;
pub use sql_browser::{SqlColumn,SqlTable,SqlTables};
mod terminal;
pub use terminal::{TerminalLab,TERMINAL_GUARD,query};
pub fn has_sql_tables(task:&Task)->bool {sql_fixture(task).is_some()}
struct LessonState {
    closed:std::sync::atomic::AtomicBool,
    cleaned:std::sync::atomic::AtomicBool,
    environments:std::sync::Mutex<std::collections::BTreeMap<String,Environment>>,
    /// Docker CLI terminals: one owned project for the learner, a separate one for narration.
    terminals:std::sync::Mutex<std::collections::BTreeMap<String,TerminalState>>,
}
struct TerminalState {
    lab:Lab,
    /// Steps whose start state this session already prepared. Revisiting a step keeps the
    /// learner's real containers as they are.
    prepared:BTreeSet<String>,
    /// Steps the learner reset: the next terminal for them restores the exact start state.
    restore:BTreeSet<String>,
}
struct Environment {
    lab:Lab,
    directory:tempfile::TempDir,
    fixture:Option<String>,
}
impl LessonSession {
    pub fn new()->Self {Self(std::sync::Arc::new(LessonState {
        closed:std::sync::atomic::AtomicBool::new(false),
        cleaned:std::sync::atomic::AtomicBool::new(false),
        environments:std::sync::Mutex::new(std::collections::BTreeMap::new()),
        terminals:std::sync::Mutex::new(std::collections::BTreeMap::new()),
    }))}
    fn ensure_open(&self)->Result<(),String> {
        if self.0.closed.load(std::sync::atomic::Ordering::Acquire){Err("수업을 나가서 실습을 종료했어요.".into())}else{Ok(())}
    }
    pub async fn run(&self,task:&Task,source:&str,input:&str)->Result<Execution,String> {
        self.execute(task,source,input,false,false).await
    }
    /// Narration may execute destructive SQL too. Its examples must never alter learner data.
    pub async fn demonstrate(&self,task:&Task,source:&str,input:&str)->Result<Execution,String> {
        self.execute(task,source,input,true,false).await
    }
    pub(crate) async fn check_case(&self,task:&Task,source:&str,input:&str)->Result<Execution,String> {
        // SQL fixtures can be reset without restarting the DB. Other labs intentionally teach
        // volume/build/restart behavior and require a clean, independent grading project.
        self.execute(task,source,input,true,true).await
    }
    async fn execute(&self,task:&Task,source:&str,input:&str,grading:bool,check_output:bool)->Result<Execution,String> {
        self.ensure_open()?;
        if source.len()>65536||input.len()>65536{return Err("작성 코드와 입력은 각각 64KB 이하여야 해요.".into())}
        let prepared=prepare_runtime(task).await?;
        let (session,task,source,input)=(self.clone(),task.clone(),source.to_owned(),input.to_owned());
        tokio::task::spawn_blocking(move||{
            let mut environments=session.0.environments.lock().unwrap_or_else(|e|e.into_inner());
            session.ensure_open()?;
            let key=environment_key(&task,grading);
            let isolated_check=grading&&sql_fixture(&task).is_none();
            if isolated_check {environments.remove(&key);}
            if !environments.contains_key(&key) {
                let cli=cli().ok_or("Docker를 찾지 못했어요.")?;
                ensure_engine(&cli)?;
                ensure_images(&cli,&task.docker_images)?;
                session.ensure_open()?;
                let directory=tempfile::Builder::new().prefix("mq3-docker-lesson-").tempdir().map_err(|e|e.to_string())?;
                let lab=Lab::open(&cli,&task)?;
                environments.insert(key.clone(),Environment{lab,directory,fixture:None});
            }
            let environment=environments.get_mut(&key).unwrap();
            for(name,content)in &task.files {write(environment.directory.path(),name,content)?;}
            write(environment.directory.path(),&task.entry_file,&source)?;
            if let Some(problem)=compose_problem(&environment.lab.cli,environment.directory.path(),&environment.lab.project,&task.docker_images)? {return Ok(reject(problem))}
            if let Some(problem)=dockerfile_problem(environment.directory.path(),&task.docker_images) {return Ok(reject(problem))}
            if let Some(database)=sql_fixture(&task) {
                let fixture=serde_json::to_string(&(&task.id,&task.files)).map_err(|e|e.to_string())?;
                if grading||environment.fixture.as_ref()!=Some(&fixture) {
                    reset_sql_fixture(environment,database,&session.0.closed)?;
                    environment.fixture=Some(fixture);
                }else{
                    // The prepared seed runs once on entry to a problem. Running the learner's
                    // SQL again keeps its actual state; checking uses a separate database container.
                    write(environment.directory.path(),"before.sql","")?;
                }
            }
            let result=execute_lab(&task,&input,&prepared,&environment.lab,environment.directory.path(),Some(&session.0.closed),check_output)?;
            if isolated_check {environments.remove(&key);}
            session.ensure_open()?;
            Ok(result)
        }).await.map_err(|e|e.to_string())?
    }
    /// Closing is synchronous as a state change; cancellation and Docker cleanup run off the UI.
    /// Queued work checks the closed flag again after obtaining the execution lock.
    pub fn close(&self) {
        if self.0.closed.swap(true,std::sync::atomic::Ordering::AcqRel){return}
        let state=self.0.clone();
        std::thread::spawn(move||{
            state.environments.lock().unwrap_or_else(|e|e.into_inner()).clear();
            state.terminals.lock().unwrap_or_else(|e|e.into_inner()).clear();
            state.cleaned.store(true,std::sync::atomic::Ordering::Release);
        });
    }
    pub async fn wait_closed(&self) {
        while !self.0.cleaned.load(std::sync::atomic::Ordering::Acquire){tokio::time::sleep(Duration::from_millis(30)).await;}
    }
    pub async fn reset(&self,task:&Task)->Result<(),String> {
        self.ensure_open()?;
        let session=self.clone();let key=environment_key(task,false);
        tokio::task::spawn_blocking(move||{
            let mut environments=session.0.environments.lock().unwrap_or_else(|e|e.into_inner());
            session.ensure_open()?;
            environments.remove(&key);
            Ok(())
        }).await.map_err(|e|e.to_string())?
    }
    #[cfg(test)]
    fn projects(&self)->Vec<String> {self.0.environments.lock().unwrap().values().map(|e|e.lab.project.clone()).collect()}
}
impl Default for LessonSession {fn default()->Self{Self::new()}}

fn sql_fixture(task:&Task)->Option<&'static str> {
    if !task.entry_file.ends_with(".sql")||!task.files.contains_key("before.sql"){return None}
    let compose=task.files.get("compose.yaml")?;
    if compose.contains("image: mysql:"){Some("mysql")}else if compose.contains("image: postgres:"){Some("postgres")}else{None}
}
fn environment_key(task:&Task,grading:bool)->String {
    // SQL steps with the same engine share one live DB. Two lanes keep the learner's changes
    // away from fixtures/hidden variations. Other labs retain their own authored workspace.
    let identity=if sql_fixture(task).is_some(){task.files.get("compose.yaml").cloned().unwrap_or_default()}else{task.id.clone()};
    format!("{}:{identity}",if grading{"check"}else{"learn"})
}
fn reset_sql_fixture(environment:&Environment,database:&str,cancel:&std::sync::atomic::AtomicBool)->Result<(),String> {
    let reset=if database=="mysql" {
        "docker compose exec -T db sh -c 'MYSQL_PWD=\"$MYSQL_ROOT_PASSWORD\" mysql -uroot --batch -e \"DROP DATABASE IF EXISTS lab; CREATE DATABASE lab CHARACTER SET utf8mb4;\"'"
    }else{
        "docker compose exec -T db psql -U postgres -d lab -X -q -v ON_ERROR_STOP=1 -c 'DROP SCHEMA IF EXISTS public CASCADE; CREATE SCHEMA public;'"
    };
    let mut command=Command::new(bash()?);prepare(&mut command,&environment.lab.cli);
    command.current_dir(environment.directory.path()).env("COMPOSE_PROJECT_NAME",&environment.lab.project)
        .args(["-c",&format!("set -e\ndocker compose up -d --wait db >/dev/null 2>&1\n{reset}")]);
    let output=execute_cancellable(command,"",LAB_SECONDS,Some(cancel))?;
    if output.success{Ok(())}else{Err(format!("실습 자료를 준비하지 못했어요.\n{}",output.stderr.trim()))}
}

fn run_blocking(task:&Task,source:&str,input:&str,prepared:Prepared,check_output:bool)->Result<Execution,String> {
    let cli=cli().ok_or_else(||format!("Docker를 찾지 못했어요. Docker Desktop을 설치하고 실행한 뒤 다시 실행하세요. 설치 안내: {INSTALL_GUIDE}"))?;
    ensure_engine(&cli)?;
    for project in stale_projects(&cli) {remove_project(&cli,&project);if let Ok(d)=locks(){let _=std::fs::remove_file(d.join(format!("{project}.lock")));}}
    ensure_images(&cli,&task.docker_images)?;
    let directory=tempfile::Builder::new().prefix("mq3-docker-lab-").tempdir().map_err(|e|e.to_string())?;
    for (name,content) in &task.files {write(directory.path(),name,content)?;}
    write(directory.path(),&task.entry_file,source)?;
    let lab=Lab::open(&cli,task)?;
    if let Some(problem)=compose_problem(&cli,directory.path(),&lab.project,&task.docker_images)? {return Ok(reject(problem))}
    if let Some(problem)=dockerfile_problem(directory.path(),&task.docker_images) {return Ok(reject(problem))}
    execute_lab(task,input,&prepared,&lab,directory.path(),None,check_output)
}

fn execute_lab(task:&Task,input:&str,prepared:&Prepared,lab:&Lab,directory:&Path,cancel:Option<&std::sync::atomic::AtomicBool>,check_output:bool)->Result<Execution,String> {
    let mut command=Command::new(bash()?);prepare(&mut command,&lab.cli);
    command.current_dir(directory).arg("lab.sh")
        .env("COMPOSE_PROJECT_NAME",&lab.project).env("MQ3_PROJECT",&lab.project)
        .env("MQ3_OWNER_LABEL",format!("{OWNER_LABEL}={}",lab.project)).env("MQ3_ENTRY",&task.entry_file)
        .env("MQ3_OUTPUT",if check_output{"grading"}else{"raw"})
        .env("MQ3_OS",if cfg!(windows){"windows"}else if cfg!(target_os="macos"){"macos"}else{"linux"})
        .env("LC_ALL","C.UTF-8").env("PGCLIENTENCODING","UTF8");
    if let Some(java)=&prepared.java {command.env("MQ3_JAVA",java).env("MQ3_CLASSPATH",&prepared.classpath);}
    let output=execute_cancellable(command,input,LAB_SECONDS,cancel)?;
    let state=if output.timed_out{"timeout"}else if output.limited{"output_limit"}else if output.success{"finished"}else{"runtime_error"};
    let mut stderr=output.stderr;
    if output.timed_out {stderr.push_str(&format!("\n실행을 중단했거나 시간 제한 {LAB_SECONDS}초를 넘었어요."));}
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
    run_with_output(task,source,input,false).await
}

pub(crate) async fn check_case(task:&Task,source:&str,input:&str)->Result<Execution,String> {
    run_with_output(task,source,input,true).await
}

async fn run_with_output(task:&Task,source:&str,input:&str,check_output:bool)->Result<Execution,String> {
    if source.len()>65536||input.len()>65536 {return Err("작성 코드와 입력은 각각 64KB 이하여야 해요.".into())}
    let prepared=prepare_runtime(task).await?;
    let (task,source,input)=(task.clone(),source.to_owned(),input.to_owned());
    tokio::task::spawn_blocking(move||run_blocking(&task,&source,&input,prepared,check_output)).await.map_err(|e|e.to_string())?
}

async fn prepare_runtime(task:&Task)->Result<Prepared,String> {
    Ok(if task.libraries.is_empty(){Prepared{java:None,classpath:String::new()}}else{
        crate::java::version().await?;
        let classpath=crate::library_sets::classpath(&task.libraries).await?;
        Prepared{java:Some(crate::java::executable().replace('\\',"/")),classpath:crate::library_sets::joined(&classpath)}
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    #[tokio::test]
    #[ignore="Needs a running Docker engine"]
    async fn lesson_reuses_a_container_until_leave_and_rejects_late_runs() {
        let image="busybox:1.36@sha256:73aaf090f3d85aa34ee199857f03fa3a95c8ede2ffd4cc2cdb5b94e566b11662";
        let compose=format!("services:\n  box:\n    image: {image}\n    command: [sleep, '600']\n");
        let mut t=task(&compose);
        t.files.insert("lab.sh".into(),"set -e\ndocker compose up -d >/dev/null 2>&1\ndocker compose exec -T box sh -c 'n=$(cat /tmp/count 2>/dev/null || echo 0); n=$((n+1)); echo $n > /tmp/count; echo $n'\n".into());
        let session=LessonSession::new();
        let first=session.run(&t,&compose,"").await.unwrap();
        assert!(first.success,"{}",first.stderr);
        assert_eq!(first.stdout.trim(),"1");
        let projects=session.projects();
        assert_eq!(projects.len(),1);
        let cli=cli().unwrap();
        let filter=format!("label={COMPOSE_LABEL}={}",projects[0]);
        let before=ids(&cli,&["ps","-q","--filter",&filter]);
        assert_eq!(before.len(),1);
        let second=session.run(&t,&compose,"").await.unwrap();
        assert!(second.success,"{}",second.stderr);
        assert_eq!(second.stdout.trim(),"2");
        assert_eq!(before,ids(&cli,&["ps","-q","--filter",&filter]));
        session.close();
        session.wait_closed().await;
        assert!(ids(&cli,&["ps","-aq","--filter",&filter]).is_empty());
        assert!(session.run(&t,&compose,"").await.is_err());
    }
    #[tokio::test]
    #[ignore="Needs a running Docker engine and the course's MySQL image"]
    async fn sql_reuses_db_across_steps_but_grading_cannot_change_learner_data() {
        // Learner runs now show the native table; grading still compares flat values.
        let cells=|result:&Execution|result.stdout.lines().filter(|line|line.starts_with('|')).map(|line|line.trim_matches('|').trim().to_owned()).collect::<Vec<_>>();
        let lesson:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/sql-first.json")).unwrap();
        let mut t:Task=serde_json::from_value(lesson["tasks"][0].clone()).unwrap();
        let session=LessonSession::new();
        let source="UPDATE item SET qty=qty+1 WHERE id=1; SELECT qty FROM item WHERE id=1;";
        let first=session.run(&t,source,"").await.unwrap();
        assert!(first.success,"{}",first.stderr);
        assert_eq!(cells(&first),["qty","4"]);
        let cli=cli().unwrap();
        let project=session.projects()[0].clone();
        let filter=format!("label={COMPOSE_LABEL}={project}");
        let container=ids(&cli,&["ps","-q","--filter",&filter]);
        let second=session.run(&t,source,"").await.unwrap();
        assert!(second.success,"{}",second.stderr);
        assert_eq!(cells(&second),["qty","5"]);
        t.tests[0].expected="3".into();
        // This lifecycle probe runs a custom qty query, not the lesson's SELECT exercise.
        // Its recently added name/price variation expects different columns entirely.
        // Lesson variation grading is covered by validate_redesigned_lesson separately.
        t.variations.clear();
        let correct="SELECT qty FROM item WHERE id=1;";
        let report=crate::lesson_runner::check_in_lesson(&t,correct,&session).await.unwrap();
        assert!(report.passed,"{}",serde_json::to_string(&report).unwrap());
        assert!(!crate::lesson_runner::check_in_lesson(&t,"SELECT 4;",&session).await.unwrap().passed);
        assert!(crate::lesson_runner::check_in_lesson(&t,correct,&session).await.unwrap().passed);
        let after_check=session.run(&t,correct,"").await.unwrap();
        assert_eq!(cells(&after_check),["qty","5"],"checking must not mutate the learner's DB");
        assert_eq!(container,ids(&cli,&["ps","-q","--filter",&filter]));
        t.id.push_str("_next_step");
        let next=session.run(&t,correct,"").await.unwrap();
        assert!(next.success,"{}",next.stderr);
        assert_eq!(cells(&next),["qty","3"],"a new independent problem gets its own fixture");
        assert_eq!(container,ids(&cli,&["ps","-q","--filter",&filter]));
        session.reset(&t).await.unwrap();
        assert!(ids(&cli,&["ps","-aq","--filter",&filter]).is_empty());
        let reset=session.run(&t,source,"").await.unwrap();
        assert_eq!(cells(&reset),["qty","4"]);
        let remaining=session.projects();
        session.close();session.wait_closed().await;
        for project in remaining {
            let filter=format!("label={COMPOSE_LABEL}={project}");
            assert!(ids(&cli,&["ps","-aq","--filter",&filter]).is_empty());
            assert!(ids(&cli,&["network","ls","-q","--filter",&filter]).is_empty());
            assert!(ids(&cli,&["volume","ls","-q","--filter",&filter]).is_empty());
        }
    }

    #[tokio::test]
    #[ignore="Needs a running Docker engine"]
    async fn leaving_a_lesson_cancels_an_in_flight_run_and_cleans_its_resources() {
        use sha2::{Digest,Sha256};
        let image="busybox:1.36@sha256:73aaf090f3d85aa34ee199857f03fa3a95c8ede2ffd4cc2cdb5b94e566b11662";
        let compose=format!("services:\n  box:\n    image: {image}\n    command: [sleep, '600']\n");
        let mut t=task(&compose);t.id=format!("stp_cancel_{}",crate::issue_progress::new_id());
        let prefix=format!("{PREFIX}{}-",&format!("{:x}",Sha256::digest(t.id.as_bytes()))[..8]);
        t.files.insert("lab.sh".into(),"set -e\ndocker compose up -d >/dev/null 2>&1\nsleep 60\n".into());
        let session=LessonSession::new();let active=session.clone();
        let execution=tokio::spawn(async move{active.run(&t,&compose,"").await});
        let cli=cli().unwrap();let mut project=None;
        for _ in 0..100 {
            project=ids(&cli,&["ps","--format","{{.Label \"com.docker.compose.project\"}}"]).into_iter().find(|p|p.starts_with(&prefix));
            if project.is_some(){break}
            tokio::time::sleep(Duration::from_millis(100)).await;
        }
        let project=project.expect("the actual lab must be running before testing exit");
        let started=Instant::now();session.close();
        assert!(tokio::time::timeout(Duration::from_secs(10),execution).await.unwrap().unwrap().is_err());
        tokio::time::timeout(Duration::from_secs(10),session.wait_closed()).await.unwrap();
        assert!(started.elapsed()<Duration::from_secs(10));
        assert!(ids(&cli,&["ps","-aq","--filter",&format!("label={COMPOSE_LABEL}={project}")]).is_empty());
    }
    #[test]
    fn watchdog_only_accepts_an_owned_project_argument() {
        assert!(watchdog_cli(&["app".into()]).is_none());
        for project in ["../outside", "user-database", "mq3lab-../../outside"] {
            assert!(watchdog_cli(&["app".into(),"--mq3-docker-watch".into(),project.into()]).unwrap().is_err());
        }
    }
    #[test]
    #[ignore="Needs a running Docker engine"]
    fn an_unowned_project_with_an_app_like_name_is_preserved() {
        let cli=cli().unwrap();
        let project=format!("{PREFIX}user-{}",crate::issue_progress::new_id().to_ascii_lowercase().chars().filter(char::is_ascii_alphanumeric).take(8).collect::<String>());
        let volume=format!("{project}-keep");
        let label=format!("{COMPOSE_LABEL}={project}");
        assert!(docker(&cli,&["volume","create","--label",&label,&volume],30).unwrap().success);
        assert!(!owns_project(&project));
        assert!(!stale_projects(&cli).contains(&project));
        remove_project(&cli,&project);
        assert!(docker(&cli,&["volume","inspect",&volume],30).unwrap().success);
        // Remove only the exact volume this test created, after proving the
        // application's cleanup left it untouched.
        assert!(docker(&cli,&["volume","rm",&volume],30).unwrap().success);
    }
    #[test]
    #[ignore="Private subprocess fixture used by the hard-kill watchdog test"]
    fn watchdog_owner_probe() {
        let Ok(project)=std::env::var("MQ3_DOCKER_OWNER_PROBE") else{return};
        assert!(valid_project(&project));
        let file=std::fs::OpenOptions::new().read(true).write(true).create(true).truncate(true)
            .open(locks().unwrap().join(format!("{project}.lock"))).unwrap();
        file.lock().unwrap();
        println!("owner-ready");
        std::io::Write::flush(&mut std::io::stdout()).unwrap();
        std::thread::sleep(Duration::from_secs(10));
        drop(file);
    }
    #[test]
    #[ignore="Needs a running Docker engine"]
    fn a_hard_killed_owner_is_cleaned_by_its_watchdog() {
        use std::io::BufRead;
        let cli=cli().unwrap();
        let project=format!("{PREFIX}watch-{}",crate::issue_progress::new_id().to_ascii_lowercase().chars().filter(char::is_ascii_alphanumeric).take(8).collect::<String>());
        let label=format!("{OWNER_LABEL}={project}");
        register_owner(&project).unwrap();
        let image="busybox:1.36@sha256:73aaf090f3d85aa34ee199857f03fa3a95c8ede2ffd4cc2cdb5b94e566b11662";
        ensure_images(&cli,&[image.into()]).unwrap();
        assert!(docker(&cli,&["volume","create","--label",&label],30).unwrap().success);
        assert!(docker(&cli,&["run","-d","--label",&label,image,"sleep","60"],60).unwrap().success);
        let mut command=Command::new(std::env::current_exe().unwrap());
        command.args(["--exact","docker_lab::tests::watchdog_owner_probe","--ignored","--nocapture"])
            .env("MQ3_DOCKER_OWNER_PROBE",&project).stdout(Stdio::piped()).stderr(Stdio::null());
        #[cfg(windows)] {use std::os::windows::process::CommandExt;command.creation_flags(0x08000000);}
        let mut child=command.spawn().unwrap();
        let mut ready=false;
        for line in std::io::BufReader::new(child.stdout.take().unwrap()).lines() {
            if line.unwrap().contains("owner-ready"){ready=true;break}
        }
        assert!(ready);
        let watched=project.clone();
        let guard=std::thread::spawn(move||watch_project(&watched));
        std::thread::sleep(Duration::from_millis(100));
        assert!(!ids(&cli,&["ps","-aq","--filter",&format!("label={label}")]).is_empty(),"a live owner must be preserved");
        child.kill().unwrap();child.wait().unwrap();
        guard.join().unwrap().unwrap();
        assert!(ids(&cli,&["ps","-aq","--filter",&format!("label={label}")]).is_empty());
        assert!(ids(&cli,&["volume","ls","-q","--filter",&format!("label={label}")]).is_empty());
    }
    /// Compose v2.38's bake builder tags `<project>-<service>` without the project label. Cleanup and the
    /// startup sweep still find it through the ownership receipt; other tags and the shared image stay.
    #[test]
    #[ignore="Needs a running Docker engine"]
    fn an_unlabelled_compose_built_image_of_an_owned_project_is_removed_by_its_name_only() {
        let cli=cli().unwrap();
        let id=||crate::issue_progress::new_id().to_ascii_lowercase().chars().filter(char::is_ascii_alphanumeric).take(8).collect::<String>();
        let project=format!("{PREFIX}built-{}",id());
        let stranger=format!("{PREFIX}built-{}-app",id());
        register_owner(&project).unwrap();
        let image="busybox:1.36@sha256:73aaf090f3d85aa34ee199857f03fa3a95c8ede2ffd4cc2cdb5b94e566b11662";
        ensure_images(&cli,&[image.into()]).unwrap();
        let built=format!("{project}-app");
        for tag in [&built,&stranger] {assert!(docker(&cli,&["tag",image,tag],30).unwrap().success);}
        let filter=format!("label={COMPOSE_LABEL}={project}");
        assert!(ids(&cli,&["image","ls","-q","--filter",&filter]).is_empty(),"the image carries no project label");
        assert!(docker(&cli,&["run","-d","--label",&format!("{COMPOSE_LABEL}={project}"),&built,"sleep","60"],60).unwrap().success);
        assert_eq!(built_image_owner(&format!("{built}:latest")),Some(project.clone()));
        assert_eq!(built_image_owner(&stranger),None,"a look-alike name without a receipt is not owned");
        remove_project(&cli,&project);
        let present=|reference:&str|docker(&cli,&["image","inspect","--format","{{.Id}}",reference],30).unwrap().success;
        assert!(!present(&built),"the image Compose built for the owned project is removed");
        assert!(ids(&cli,&["ps","-aq","--filter",&filter]).is_empty());
        assert!(present(&stranger),"an unowned look-alike tag stays");
        assert!(present(image),"the shared pinned image stays");
        // A crash can leave only the built image; the startup sweep finds its project by the same rule.
        assert!(docker(&cli,&["tag",image,&built],30).unwrap().success);
        assert!(stale_projects(&cli).contains(&project));
        remove_project(&cli,&project);
        assert!(!present(&built));
        let _=docker(&cli,&["image","rm",&stranger],30);
        let _=std::fs::remove_file(locks().unwrap().join(format!("{project}.owned")));
    }
    #[cfg(windows)]
    #[test]
    fn desktop_shell_finds_posix_tools_without_an_inherited_git_path() {
        let shell = bash().expect("Git Bash is installed for Windows terminal labs");
        let fake_cli = PathBuf::from(r"C:\mq3-desktop-path-probe\docker.exe");
        let mut command = Command::new(shell);
        prepare(&mut command, &fake_cli);
        command.args(["-c", "printf '%s' hello | /usr/bin/env sh -c 'cat'"]);
        let result = execute(command, "", 15).unwrap();
        assert!(result.success, "{}", result.stderr);
        assert_eq!(result.stdout, "hello");
    }
    fn task(compose:&str)->Task {
        serde_json::from_value(serde_json::json!({"id":"stp_docker_probe","title":"Docker","goal":"x","language":"docker",
            "starter_code":compose,"solution":compose,"entry_file":"compose.yaml",
            "files":{"lab.sh":"set -e\ndocker compose run --rm --no-deps box\n"},
            "docker_images":["busybox:1.36@sha256:73aaf090f3d85aa34ee199857f03fa3a95c8ede2ffd4cc2cdb5b94e566b11662"],
            "tests":[{"input":"","expected":"hello"}]})).unwrap()
    }
    #[test]
    fn only_digest_pinned_official_images() {
        assert!(valid_image("nginx:1.28-alpine@sha256:a8b39bd9cf0f83869a2162827a0caf6137ddf759d50a171451b335cecc87d236"));
        assert!(!valid_image("nginx:1.28-alpine"));
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
        assert_eq!(inside("C:/Temp/run","c:/temp/run"),cfg!(windows)||cfg!(target_os="macos"));
        assert!(!inside("C:/Temp/run","C:/Temp/run2"));
        assert!(!inside("C:/Temp/run","C:/Users"));
    }
    #[test]
    fn dockerfile_from_lines_use_pinned_images() {
        let dir=tempfile::tempdir().unwrap();let t=task("x");
        std::fs::write(dir.path().join("Dockerfile"),format!("FROM {} AS base\nFROM base\nRUN echo hi\n",t.docker_images[0])).unwrap();
        assert_eq!(dockerfile_problem(dir.path(),&t.docker_images),None);
        std::fs::write(dir.path().join("Dockerfile"),"FROM ubuntu:latest\n").unwrap();
        assert!(dockerfile_problem(dir.path(),&t.docker_images).is_some());
    }
    /// Real engine checks. Run with `cargo test --lib docker_lab -- --ignored --test-threads=1`.
    #[tokio::test]
    #[ignore="Needs a running Docker engine"]
    async fn learner_and_narration_keep_raw_output_while_checks_use_grading_output() {
        let mut t=task("services: {}\n");
        t.files.insert("lab.sh".into(),"printf '%s' \"$MQ3_OUTPUT\"\n".into());
        assert_eq!(run(&t,"services: {}\n","").await.unwrap().stdout,"raw");
        assert_eq!(check_case(&t,"services: {}\n","").await.unwrap().stdout,"grading");
        let session=LessonSession::new();
        assert_eq!(session.run(&t,"services: {}\n","").await.unwrap().stdout,"raw");
        assert_eq!(session.check_case(&t,"services: {}\n","").await.unwrap().stdout,"grading");
        assert_eq!(session.demonstrate(&t,"services: {}\n","").await.unwrap().stdout,"raw");
        session.close();session.wait_closed().await;
    }

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
        register_owner(&project).unwrap();
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
