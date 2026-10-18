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
        let mut command=if practice.is_some(){let mut c=CommandBuilder::new("/bin/bash");c.args(["--noprofile","--norc"]);c}else{CommandBuilder::new(std::env::var_os("SHELL").unwrap_or_else(||"/bin/sh".into()))};
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
        let child=pair.slave.spawn_command(command).map_err(|e|e.to_string())?;
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
        Ok((Self{master:pair.master,writer,child:Some(child)},rx))
    }
    pub fn input(&mut self,data:&str)->Result<(),String> {
        self.writer.write_all(data.as_bytes()).and_then(|_|self.writer.flush()).map_err(|e|e.to_string())
    }
    /// Call on a worker thread before replacing a practice directory.
    pub fn shutdown(&mut self)->Result<(),String> {
        if let Some(child)=self.child.as_mut() {
            child.kill().map_err(|e|e.to_string())?;
            for _ in 0..50 {
                if child.try_wait().map_err(|e|e.to_string())?.is_some(){self.child.take();return Ok(())}
                std::thread::sleep(std::time::Duration::from_millis(100));
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
