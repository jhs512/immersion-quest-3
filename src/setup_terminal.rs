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
}

// Weak entries do not keep a shell or a practice folder alive.
type SharedScope = std::sync::Arc<std::sync::Mutex<Option<crate::process_scope::ProcessScope>>>;
type WeakScope = std::sync::Weak<std::sync::Mutex<Option<crate::process_scope::ProcessScope>>>;
#[derive(Default)]
struct PracticeRegistry { scopes: Vec<WeakScope>, exiting: bool }
fn practice_scopes() -> &'static std::sync::Mutex<PracticeRegistry> {
    static SCOPES: std::sync::OnceLock<std::sync::Mutex<PracticeRegistry>> = std::sync::OnceLock::new();
    SCOPES.get_or_init(Default::default)
}
struct PracticeScope(SharedScope);
impl PracticeScope {
    fn spawn(start: impl FnOnce() -> Result<Box<dyn portable_pty::Child + Send + Sync>, String>)
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
        let scope = std::sync::Arc::new(std::sync::Mutex::new(Some(process)));
        registry.scopes.retain(|entry| entry.strong_count() > 0);
        registry.scopes.push(std::sync::Arc::downgrade(&scope));
        Ok((child, Self(scope)))
    }
    fn terminate(&self) -> Result<(), String> { terminate_scope(&self.0) }
}
fn terminate_scope(scope: &SharedScope) -> Result<(), String> {
    let mut scope = scope.lock().unwrap_or_else(|e| e.into_inner());
    if let Some(process) = scope.as_ref() { process.terminate()?; }
    // A completed session ID must never be signalled again after PID reuse.
    scope.take();
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

impl SetupTerminal {
    pub fn open() -> Result<(Self, mpsc::Receiver<Vec<u8>>), String> {Self::open_with(None)}
    pub fn open_practice(path:&std::path::Path,environment:&[(String,String)])->Result<(Self,mpsc::Receiver<Vec<u8>>),String> {Self::open_with(Some((path,environment)))}
    fn open_with(practice:Option<(&std::path::Path,&[(String,String)])>) -> Result<(Self, mpsc::Receiver<Vec<u8>>), String> {
        let pair=native_pty_system().openpty(PtySize {rows:20,cols:100,pixel_width:0,pixel_height:0}).map_err(|e|e.to_string())?;
        #[cfg(windows)]
        let mut command={let mut c=CommandBuilder::new("powershell.exe");c.args(["-NoLogo","-NoProfile"]);c};
        #[cfg(not(windows))]
        let mut command=if practice.is_some(){let mut c=CommandBuilder::new("/bin/bash");c.args(["--noprofile","--norc","-i","+m"]);c}else{CommandBuilder::new(std::env::var_os("SHELL").unwrap_or_else(||"/bin/sh".into()))};
        let paths=gh_directories().into_iter().chain(std::env::split_paths(&std::env::var_os("PATH").unwrap_or_default()).collect::<Vec<_>>());
        if let Ok(path)=std::env::join_paths(paths) {command.env("PATH",path);}
        command.env("TERM","xterm-256color");
        if let Some(home)=std::env::var_os(if cfg!(windows){"USERPROFILE"}else{"HOME"}) {command.cwd(home);}
        if let Some((path,environment))=practice {
            command.cwd(path);
            for (key,_) in std::env::vars_os(){if key.to_string_lossy().starts_with("GIT_"){command.env_remove(key);}}
            for (key,value) in environment {command.env(key,value);}
        }
        let mut reader=pair.master.try_clone_reader().map_err(|e|e.to_string())?;
        let writer=pair.master.take_writer().map_err(|e|e.to_string())?;
        let start = || pair.slave.spawn_command(command).map_err(|error| error.to_string());
        let (child, scope) = if practice.is_some() {
            let (child, scope) = PracticeScope::spawn(start)?;
            (child, Some(scope))
        } else { (start()?, None) };
        drop(pair.slave);
        let (tx,rx)=mpsc::channel(32);
        // Bytes stay in memory; TextDecoder in the terminal handles split UTF-8 sequences.
        std::thread::spawn(move || {
            let mut bytes=[0u8;8192];
            loop {match reader.read(&mut bytes) {
                Ok(0)|Err(_)=>break,
                Ok(n)=>if tx.blocking_send(bytes[..n].to_vec()).is_err(){break;},
            }}
        });
        Ok((Self{master:pair.master,writer,child:Some(child),scope},rx))
    }
    pub fn input(&mut self,data:&str)->Result<(),String> {
        self.writer.write_all(data.as_bytes()).and_then(|_|self.writer.flush()).map_err(|e|e.to_string())
    }
    /// Call on a worker thread before replacing a practice directory.
    pub fn shutdown(&mut self)->Result<(),String> {
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
        let command=if cfg!(windows){"Write-Output ('MQ3_' + 'PTY_READY')\r"}else{"printf 'MQ3_%s\\n' PTY_READY\n"};
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
            if seen.contains("MQ3_PTY_READY"){break;}
            std::thread::sleep(std::time::Duration::from_millis(20));
        }
        drop(shell);
        assert!(seen.contains("MQ3_PTY_READY"),"interactive shell did not execute the input: {seen:?}");
    }
}
