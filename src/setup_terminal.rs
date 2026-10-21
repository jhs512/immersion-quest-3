//! A local, short-lived interactive shell for installing and signing into gh.
use portable_pty::{native_pty_system, CommandBuilder, MasterPty, PtySize};
use std::{io::{Read, Write}, path::PathBuf};
use tokio::sync::mpsc;

/// Finder starts GUI apps with a minimal PATH. Resolve the same tools as a terminal.
/// Call once, before the desktop runtime creates threads.
pub fn prepare_desktop_path() {
    #[cfg(target_os = "macos")]
    {
        let mut paths = gh_directories();
        if let Some(home) = std::env::var_os("HOME") {
            paths.push(PathBuf::from(home).join(".local/bin"));
        }
        paths.extend(std::env::split_paths(&std::env::var_os("PATH").unwrap_or_default()));
        if let Ok(path) = std::env::join_paths(paths) { std::env::set_var("PATH", path); }
    }
}

pub struct SetupTerminal {
    master: Box<dyn MasterPty + Send>,
    writer: Box<dyn Write + Send>,
    child: Option<Box<dyn portable_pty::Child + Send + Sync>>,
    scope:Option<PracticeScope>,
    draining:std::sync::Arc<std::sync::atomic::AtomicBool>,
}

// Weak entries do not keep a shell or a practice folder alive.
struct PracticeProcess {
    process: Option<crate::process_scope::ProcessScope>,
    draining: std::sync::Arc<std::sync::atomic::AtomicBool>,
}
type SharedScope = std::sync::Arc<std::sync::Mutex<PracticeProcess>>;
type WeakScope = std::sync::Weak<std::sync::Mutex<PracticeProcess>>;
#[derive(Default)]
struct PracticeRegistry { scopes: Vec<WeakScope>, exiting: bool }
fn practice_scopes() -> &'static std::sync::Mutex<PracticeRegistry> {
    static SCOPES: std::sync::OnceLock<std::sync::Mutex<PracticeRegistry>> = std::sync::OnceLock::new();
    SCOPES.get_or_init(Default::default)
}
struct PracticeScope(SharedScope);
impl PracticeScope {
    fn spawn(start: impl FnOnce() -> Result<Box<dyn portable_pty::Child + Send + Sync>, String>, draining:std::sync::Arc<std::sync::atomic::AtomicBool>)
        -> Result<(Box<dyn portable_pty::Child + Send + Sync>, Self), String> {
        // The admission lock covers spawn itself, not just registration. Exit
        // cannot pass a worker that has created a child but not registered it.
        let mut registry = practice_scopes().lock().unwrap_or_else(|e| e.into_inner());
        if registry.exiting { return Err("업데이트를 준비하고 있어요. 잠시 뒤 다시 여세요.".into()); }
        let mut child = start()?;
        let process = match crate::process_scope::ProcessScope::attach(child.as_ref()) {
            Ok(process) => process,
            Err(error) => { let _ = child.kill(); let _ = child.wait(); return Err(error); }
        };
        let scope = std::sync::Arc::new(std::sync::Mutex::new(PracticeProcess {process:Some(process),draining}));
        registry.scopes.retain(|entry| entry.strong_count() > 0);
        registry.scopes.push(std::sync::Arc::downgrade(&scope));
        Ok((child, Self(scope)))
    }
    fn terminate(&self) -> Result<(), String> { terminate_scope(&self.0) }
}
fn terminate_scope(scope: &SharedScope) -> Result<(), String> {
    let mut scope = scope.lock().unwrap_or_else(|e| e.into_inner());
    scope.draining.store(true,std::sync::atomic::Ordering::Relaxed);
    if let Some(process) = scope.process.as_ref() { process.terminate()?; }
    // A completed session ID must never be signalled again after PID reuse.
    scope.process.take();
    Ok(())
}
/// While held, in-flight initialization cannot admit a shell after exit cleanup.
/// Dropping the guard on a handoff error permits students to reopen their terminal.
pub struct PracticeExit { _private: () }
impl Drop for PracticeExit {
    fn drop(&mut self) { practice_scopes().lock().unwrap_or_else(|e| e.into_inner()).exiting = false; }
}
pub fn prepare_practice_exit() -> Result<PracticeExit, String> {
    {
        let mut registry = practice_scopes().lock().unwrap_or_else(|e| e.into_inner());
        if registry.exiting { return Err("실습을 종료하고 있어요.".into()); }
        registry.exiting = true;
    }
    let guard = PracticeExit { _private: () };
    shutdown_practices()?;
    Ok(guard)
}
/// Stop real practice shells before an updater calls process::exit (which skips Drop).
/// Repository files stay intact; this is not a reset or a state backup.
pub fn shutdown_practices() -> Result<(), String> {
    let scopes = practice_scopes().lock().unwrap_or_else(|e| e.into_inner()).scopes.iter().filter_map(std::sync::Weak::upgrade).collect::<Vec<_>>();
    let mut failures = Vec::new();
    for scope in scopes { if let Err(error) = terminate_scope(&scope) { failures.push(error); } }
    if failures.is_empty() { Ok(()) } else { Err(failures.join("\n")) }
}

fn gh_directories() -> Vec<PathBuf> {
    #[cfg(windows)]
    { ["ProgramFiles", "ProgramFiles(x86)", "LOCALAPPDATA"].iter().filter_map(std::env::var_os)
        .flat_map(|root|[PathBuf::from(&root).join("GitHub CLI"),PathBuf::from(root).join("Programs/GitHub CLI")]).collect() }
    #[cfg(not(windows))]
    { vec![PathBuf::from("/opt/homebrew/bin"), PathBuf::from("/usr/local/bin"), PathBuf::from("/usr/bin")] }
}

/// A newly installed gh is usable even when the app inherited the pre-install PATH.
pub fn gh_executable() -> PathBuf {
    let file = if cfg!(windows) { "gh.exe" } else { "gh" };
    for dir in gh_directories() {
        let candidate=dir.join(file);
        if candidate.is_file() {return candidate;}
    }
    PathBuf::from(file)
}

/// Git practice uses the same Bash syntax on every desktop platform.
#[cfg(windows)]
pub fn git_bash_executable()->Result<PathBuf,String> {
    let mut roots=Vec::new();
    for key in ["ProgramFiles","ProgramFiles(x86)"] {if let Some(root)=std::env::var_os(key){roots.push(PathBuf::from(root).join("Git"));}}
    if let Some(root)=std::env::var_os("LOCALAPPDATA"){roots.push(PathBuf::from(root).join("Programs/Git"));}
    for path in std::env::split_paths(&std::env::var_os("PATH").unwrap_or_default()) {
        roots.extend(path.ancestors().take(3).map(std::path::Path::to_path_buf));
    }
    for root in roots {
        if !root.join("cmd/git.exe").is_file() && !root.join("bin/git.exe").is_file(){continue;}
        for relative in ["usr/bin/bash.exe","bin/bash.exe"] {let file=root.join(relative);if file.is_file(){return Ok(file)}}
    }
    Err("Git Bash를 찾지 못했어요. Git for Windows를 설치한 뒤 다시 열어 주세요.".into())
}

pub fn vim_executable()->Result<PathBuf,String>{
    #[cfg(not(windows))] {Ok(PathBuf::from("/usr/bin/vim"))}
    #[cfg(windows)] {let bash=git_bash_executable()?;bash.ancestors().take(4).map(|p|p.join("usr/bin/vim.exe")).chain(bash.parent().map(|p|p.join("vim.exe"))).find(|p|p.is_file()).ok_or("Git for Windows의 Vim을 찾지 못했어요.".into())}
}
impl SetupTerminal {
    pub fn open() -> Result<(Self, mpsc::Receiver<Vec<u8>>), String> {Self::open_with(None,None)}
    pub fn open_practice(path:&std::path::Path,environment:&[(String,String)])->Result<(Self,mpsc::Receiver<Vec<u8>>),String> {Self::open_with(Some((path,environment)),None)}
    pub fn open_vim(path:&std::path::Path,environment:&[(String,String)],script:&std::path::Path,file:&str)->Result<(Self,mpsc::Receiver<Vec<u8>>),String>{Self::open_with(Some((path,environment)),Some((script,file)))}
    fn open_with(practice:Option<(&std::path::Path,&[(String,String)])>,editor:Option<(&std::path::Path,&str)>) -> Result<(Self, mpsc::Receiver<Vec<u8>>), String> {
        let pair=native_pty_system().openpty(PtySize {rows:20,cols:100,pixel_width:0,pixel_height:0}).map_err(|e|e.to_string())?;
        let vim_command=||->Result<CommandBuilder,String>{
            let executable=vim_executable()?;
            let (script,file)=editor.ok_or("Vim 실행 설정 오류")?;
            let mut c=CommandBuilder::new(executable);c.arg("-N");c.arg("-u");c.arg(script);c.args(["-i","NONE","-n","--",file]);Ok(c)
        };
        #[cfg(windows)]
        let mut command=if editor.is_some(){vim_command()?}else if practice.is_some(){let mut c=CommandBuilder::new(git_bash_executable()?);c.args(["--noprofile","--norc","-i","+m"]);c}else{let mut c=CommandBuilder::new("powershell.exe");c.args(["-NoLogo","-NoProfile","-NoExit","-Command",
            "$utf8=[System.Text.UTF8Encoding]::new($false);[Console]::InputEncoding=$utf8;[Console]::OutputEncoding=$utf8;$OutputEncoding=$utf8"]);c};
        #[cfg(not(windows))]
        let mut command=if editor.is_some(){vim_command()?}else if practice.is_some(){let mut c=CommandBuilder::new("/bin/bash");c.args(["--noprofile","--norc","-i","+m"]);c}else{CommandBuilder::new(std::env::var_os("SHELL").unwrap_or_else(||"/bin/sh".into()))};
        let paths=gh_directories().into_iter().chain(std::env::split_paths(&std::env::var_os("PATH").unwrap_or_default()).collect::<Vec<_>>());
        if let Ok(path)=std::env::join_paths(paths) {command.env("PATH",path);}
        command.env("TERM","xterm-256color");
        if let Some(home)=std::env::var_os(if cfg!(windows){"USERPROFILE"}else{"HOME"}) {command.cwd(home);}
        if let Some((path,environment))=practice {
            command.cwd(path);
            for (key,_) in std::env::vars_os(){if key.to_string_lossy().starts_with("GIT_"){command.env_remove(key);}}
            for (key,value) in environment {command.env(key,value);}
        }
        #[cfg(windows)]
        if let Some((_,environment))=practice {
            // --noprofile/--norc does not add Git Bash's coreutils to a GUI app's PATH.
            let bash=git_bash_executable()?;
            let inherited=environment.iter().find(|(key,_)|key=="PATH").map(|(_,value)|std::ffi::OsString::from(value)).unwrap_or_else(||std::env::var_os("PATH").unwrap_or_default());
            let paths=bash.parent().map(std::path::Path::to_path_buf).into_iter().chain(gh_directories()).chain(std::env::split_paths(&inherited));
            command.env("PATH",std::env::join_paths(paths).map_err(|e|e.to_string())?);
        }
        #[cfg(windows)]
        if practice.is_some() {
            // Git Bash launched from a Korean Windows GUI must not inherit a
            // legacy ANSI locale. This changes only the practice child process.
            command.env_remove("LC_ALL");
            command.env("LC_CTYPE","C.UTF-8");
        }
        #[cfg(target_os="macos")]
        {
            // Finder need not provide a login-shell locale. In the C locale,
            // macOS Bash 3.2 Readline treats UTF-8 input bytes as Meta commands.
            // Keep LANG (and translated messages), but guarantee UTF-8 characters
            // even when the parent supplied LC_ALL=C. Only this PTY is changed.
            command.env_remove("LC_ALL");
            command.env("LC_CTYPE","en_US.UTF-8");
            command.env("BASH_SILENCE_DEPRECATION_WARNING","1");
        }
        let mut reader=pair.master.try_clone_reader().map_err(|e|e.to_string())?;
        let writer=pair.master.take_writer().map_err(|e|e.to_string())?;
        let draining=std::sync::Arc::new(std::sync::atomic::AtomicBool::new(false));
        let start = || pair.slave.spawn_command(command).map_err(|error| error.to_string());
        let (child, scope) = if practice.is_some() {
            let (child, scope) = PracticeScope::spawn(start,draining.clone())?;
            (child, Some(scope))
        } else { (start()?, None) };
        drop(pair.slave);
        let (tx,rx)=mpsc::channel(32);
        // Keep draining the PTY after a UI receiver disconnects. A macOS child
        // can otherwise block during startup/exit with unread master output.
        let reader_draining=draining.clone();
        std::thread::spawn(move || {
            use std::sync::atomic::Ordering::Relaxed;
            let mut bytes=[0u8;8192];
            loop {match reader.read(&mut bytes) {
                Ok(0)|Err(_)=>break,
                Ok(n)=>{
                    let mut chunk=bytes[..n].to_vec();
                    while !reader_draining.load(Relaxed) {
                        match tx.try_send(chunk) {
                            Ok(())=>break,
                            Err(mpsc::error::TrySendError::Full(returned))=>{
                                chunk=returned;std::thread::sleep(std::time::Duration::from_millis(10));
                            },
                            Err(mpsc::error::TrySendError::Closed(_))=>{reader_draining.store(true,Relaxed);break;}
                        }
                    }
                }
            }}
        });
        Ok((Self{master:pair.master,writer,child:Some(child),scope,draining},rx))
    }
    pub fn input(&mut self,data:&str)->Result<(),String> {
        self.writer.write_all(data.as_bytes()).and_then(|_|self.writer.flush()).map_err(|e|e.to_string())
    }
    /// Call on a worker thread before replacing a practice directory.
    pub fn shutdown(&mut self)->Result<(),String> {
        self.draining.store(true,std::sync::atomic::Ordering::Relaxed);
        if let Some(scope)=&self.scope {scope.terminate()?;}
        if let Some(child)=self.child.as_mut() {
            child.kill().map_err(|e|e.to_string())?;
            for _ in 0..50 {
                if child.try_wait().map_err(|e|e.to_string())?.is_some(){self.child.take();return Ok(())}
                std::thread::sleep(std::time::Duration::from_millis(100));
            }
            #[cfg(unix)]
            if let Some(pid) = child.process_id() {
                let state = std::process::Command::new("/bin/ps").args(["-p", &pid.to_string(), "-o", "pid=,ppid=,stat=,command="]).output().map(|output|String::from_utf8_lossy(&output.stdout).into_owned()).unwrap_or_default();
                return Err(format!("터미널이 아직 종료되지 않았어요. PID {pid}: {state}"));
            }
            return Err("터미널이 아직 종료되지 않았어요.".into());
        }
        Ok(())
    }
    pub fn resize(&self,rows:u16,cols:u16)->Result<(),String> {
        self.master.resize(PtySize{rows:rows.clamp(2,150),cols:cols.clamp(10,300),pixel_width:0,pixel_height:0}).map_err(|e|e.to_string())
    }
}
impl Drop for SetupTerminal {
    fn drop(&mut self) {
        self.draining.store(true,std::sync::atomic::Ordering::Relaxed);
        if let Some(scope)=&self.scope {let _=scope.terminate();}
        if let Some(mut child)=self.child.take() {
            let _=child.kill();
            std::thread::spawn(move ||{let _=child.wait();});
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn interactive_shell_accepts_input_resizes_and_closes_on_drop() {
        let (mut shell,mut rx)=SetupTerminal::open().unwrap();
        shell.resize(24,90).unwrap();
        // Build the sentinel inside the shell, so terminal echo cannot satisfy the test.
        let expected=if cfg!(windows){"MQ3_PTY_READY 한글 65001"}else{"MQ3_PTY_READY 한글"};
        let command=if cfg!(windows){"[Console]::WriteLine('MQ3_' + 'PTY_READY 한글 ' + [Console]::OutputEncoding.CodePage)\r"}else{"printf 'MQ3_%s\\n' 'PTY_READY 한글'\n"};
        let mut seen=String::new();
        let mut sent=false;
        let deadline=std::time::Instant::now()+std::time::Duration::from_secs(12);
        while std::time::Instant::now()<deadline {
            while let Ok(bytes)=rx.try_recv(){
                let chunk=String::from_utf8_lossy(&bytes);
                // ConPTY inherits the cursor from its emulator before starting the shell.
                if chunk.contains("\x1b[6n") {shell.input("\x1b[1;1R").unwrap();}
                seen.push_str(&chunk);
            }
            if !sent && (seen.contains("PS ")||!cfg!(windows)) {shell.input(command).unwrap();sent=true;}
            if seen.contains(expected){break;}
            std::thread::sleep(std::time::Duration::from_millis(20));
        }
        drop(shell);
        assert!(seen.contains(expected),"interactive shell did not preserve UTF-8: {seen:?}");
    }
}
